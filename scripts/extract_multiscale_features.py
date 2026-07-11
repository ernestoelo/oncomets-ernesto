#!/usr/bin/env python
"""extract_multiscale_features.py — extracción CONCH multi-escala parametrizada en µm/px.

Réplica del baseline MIL multi-escala de CPathAgent (Ap. C.1.2), portada a CONCH:
por cada región del grid, extrae un tile FINO (campo ~112 µm ≈ 20×, CONCH-nativo) y un
tile de CONTEXTO (campo ~512 µm ≈ 5×), cada uno → CONCH 512-d, y los FUSIONA por
**promedio** → un token [512] por región → `.pt [N,512]`. CLAM_MB queda intacto.

Clave (hallazgo 10-jul, [[cohortes-magnificacion-fisica]]): las cohortes están a distinta
magnificación FÍSICA a level0 (TCGA ~0.2325 µm/px ≈40×, privado ~0.465 ≈20×). Por eso el
campo objetivo se define en **µm** y el tamaño de crop en px se calcula **por slide** desde
su µm/px real → CONCH ve el MISMO campo físico a la misma escala en todas las cohortes
(y de paso se normaliza el confound single-scale). NO se copian px crudos del paper.

Modos (`--mode`):
  - multiscale : fusión promedio (fino + contexto)  → arm B (experimento)
  - fine_only  : solo el tile fino @ grid común       → arm B0 (aísla el re-grid del contexto)

NO modifica clam_environ (regla 2): reusa `get_encoder('conch_v1')` y `save_hdf5` por import.
GPU vía sbatch (workaround B: binario absoluto del env). Grid de entrada = coords .h5 de
create_patches_fp.py corrido por-cohorte con `--patch_size = round(112/mpp)` (grid 112 µm común).
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

import h5py
import numpy as np
import openslide
import torch
from PIL import Image
from torch.utils.data import DataLoader, Dataset

_CLAM_ENVIRON = "/media/administrador/Storage1/sdonoso/clam_environ"
if _CLAM_ENVIRON not in sys.path:
    sys.path.insert(0, _CLAM_ENVIRON)
from models import get_encoder  # noqa: E402
from utils.file_utils import save_hdf5  # noqa: E402

# --- campos físicos de la pirámide (µm) — ver investigacion_magnificacion.md §5.1/§5.5 ---
FINE_UM = 112.0    # ≈20× · 0.5 µm/px @ 224 px = CONCH-nativo (objeto + morfología)
CONTEXT_UM = 512.0  # ≈5×  · 2.3 µm/px @ 224 px (conducto/lobulillo anfitrión = Tarea B)

# MPP fallback por cohorte cuando el metadata no es confiable (HistAI = generic-tiff bogus).
COHORT_MPP_FALLBACK = {"histai": None}  # None ⇒ sin MPP fiable → se salta / se trata aparte
MPP_MIN, MPP_MAX = 0.10, 1.00  # banda sana para aceptar el mpp leído del WSI


def resolve_mpp(wsi: openslide.OpenSlide, cohort: str | None) -> float | None:
    """µm/px físico del WSI. Lee PROPERTY_NAME_MPP_X; si está fuera de banda (bogus,
    p.ej. HistAI=1000) usa el fallback de cohorte. Devuelve None si no se puede fijar."""
    try:
        mpp = float(wsi.properties.get(openslide.PROPERTY_NAME_MPP_X, "nan"))
    except (TypeError, ValueError):
        mpp = float("nan")
    if MPP_MIN <= mpp <= MPP_MAX:
        return mpp
    return COHORT_MPP_FALLBACK.get(cohort, None)


class MultiScaleTiles(Dataset):
    """Por cada coord (top-left level0) devuelve (fine_img, ctx_img) ya listos para CONCH.
    fine se lee a level0; contexto se lee del mejor nivel de la pirámide para el campo pedido
    (barato). img_transforms hace el resize final a 224 + normalización."""

    def __init__(self, wsi, coords, mpp, patch_size_l0, img_transforms, mode):
        self.wsi = wsi
        self.coords = coords
        self.img_t = img_transforms
        self.mode = mode
        self.fine_px = max(1, round(FINE_UM / mpp))
        self.ctx_px = max(1, round(CONTEXT_UM / mpp))
        # el grid se generó con patch_size = round(112/mpp); center = coord + patch_size/2
        self.half_grid = patch_size_l0 // 2
        self.W, self.H = wsi.level_dimensions[0]

    def __len__(self):
        return len(self.coords)

    def _read(self, cx, cy, size_l0):
        """Lee un crop de lado size_l0 (px level0) centrado en (cx,cy), del mejor nivel
        de la pirámide, clampeado a bordes. Devuelve PIL RGB."""
        best = self.wsi.get_best_level_for_downsample(max(1.0, size_l0 / 224.0))
        ds = self.wsi.level_downsamples[best]
        size_lvl = max(1, round(size_l0 / ds))
        x0 = int(np.clip(cx - size_l0 // 2, 0, max(0, self.W - size_l0)))
        y0 = int(np.clip(cy - size_l0 // 2, 0, max(0, self.H - size_l0)))
        img = self.wsi.read_region((x0, y0), best, (size_lvl, size_lvl)).convert("RGB")
        return img

    def __getitem__(self, idx):
        coord = self.coords[idx]
        cx = int(coord[0]) + self.half_grid
        cy = int(coord[1]) + self.half_grid
        fine = self.img_t(self._read(cx, cy, self.fine_px))
        if self.mode == "fine_only":
            return fine, torch.zeros(0), coord
        ctx = self.img_t(self._read(cx, cy, self.ctx_px))
        return fine, ctx, coord


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--h5_dir", required=True, help="dir con <slide_id>.h5 de coords (grid 112µm común)")
    p.add_argument("--wsi_dirs", nargs="+", required=True,
                   help="dirs raíz de WSI (TCGA, privado, histai) — se busca el slide en todos")
    p.add_argument("--out_dir", required=True, help="dir de salida (bajo clam_testing2/ — containment)")
    p.add_argument("--mode", choices=["multiscale", "fine_only"], default="multiscale")
    p.add_argument("--model_name", default="conch_v1")
    p.add_argument("--target_patch_size", type=int, default=224)
    p.add_argument("--batch_size", type=int, default=64)
    p.add_argument("--slide_ext", nargs="+", default=[".svs", ".bif", ".tiff", ".tif"])
    return p.parse_args()


def find_wsi(slide_id: str, wsi_dirs, exts):
    """Busca el archivo WSI del slide en los dirs (recursivo) y devuelve (path, cohort)."""
    for root in wsi_dirs:
        cohort = ("tcga" if "TCGA" in root else "histai" if "histai" in root else "privado")
        for ext in exts:
            hits = list(Path(root).rglob(f"{slide_id}{ext}"))
            if hits:
                return str(hits[0]), cohort
    return None, None


def main() -> int:
    args = parse_args()
    out_root = Path(args.out_dir).resolve()
    if not str(out_root).startswith("/media/administrador/Storage1/sdonoso/clam_testing2/"):
        raise ValueError(f"--out_dir debe estar bajo clam_testing2/ (containment). Recibido: {out_root}")
    # layout `features/pt_files` para que train_dsmil.py --data_root_dir <out_dir> lo consuma directo.
    feat_root = out_root / "features"
    (feat_root / "pt_files").mkdir(parents=True, exist_ok=True)
    (feat_root / "h5_files").mkdir(parents=True, exist_ok=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model, img_transforms = get_encoder(args.model_name, target_img_size=args.target_patch_size)
    model = model.eval().to(device)
    print(f"[INFO] device={device} mode={args.mode} model={args.model_name}")

    h5_files = sorted(Path(args.h5_dir).glob("*.h5"))
    print(f"[INFO] {len(h5_files)} slides con coords en {args.h5_dir}")
    skipped = []
    for k, h5p in enumerate(h5_files):
        slide_id = h5p.stem
        out_pt = feat_root / "pt_files" / f"{slide_id}.pt"
        if out_pt.exists():
            continue
        wsi_path, cohort = find_wsi(slide_id, args.wsi_dirs, args.slide_ext)
        if wsi_path is None:
            skipped.append((slide_id, "WSI no encontrado")); continue
        wsi = openslide.OpenSlide(wsi_path)
        mpp = resolve_mpp(wsi, cohort)
        if mpp is None:
            skipped.append((slide_id, f"mpp no fiable (cohort={cohort})")); continue
        with h5py.File(h5p, "r") as f:
            coords = f["coords"][:]
            patch_size_l0 = int(f["coords"].attrs.get("patch_size", round(FINE_UM / mpp)))

        ds = MultiScaleTiles(wsi, coords, mpp, patch_size_l0, img_transforms, args.mode)
        # num_workers=0 obligatorio: el handle openslide (self.wsi) NO es fork-safe/picklable
        # → con workers>0 el DataLoader crashea. La extracción es GPU-bound (CONCH), el I/O
        # single-thread es aceptable. Paralelizar requeriría reabrir el WSI por worker.
        loader = DataLoader(ds, batch_size=args.batch_size, num_workers=0,
                            collate_fn=lambda b: b)  # lista de tuplas (tensor ya transformado)
        feats = []
        t0 = time.time()
        with torch.inference_mode():
            for batch in loader:
                fine = torch.stack([x[0] for x in batch]).to(device, non_blocking=True)
                vf = model(fine)
                if args.mode == "multiscale":
                    ctx = torch.stack([x[1] for x in batch]).to(device, non_blocking=True)
                    vc = model(ctx)
                    v = 0.5 * (vf + vc)
                else:
                    v = vf
                feats.append(v.cpu())
        feats = torch.cat(feats, dim=0).float()  # [N,512]
        torch.save(feats, out_pt)
        save_hdf5(str(feat_root / "h5_files" / f"{slide_id}.h5"),
                  {"features": feats.numpy(), "coords": coords.astype(np.int32)},
                  attr_dict=None, mode="w")
        print(f"[{k+1}/{len(h5_files)}] {slide_id} cohort={cohort} mpp={mpp:.4f} "
              f"fine_px={ds.fine_px} ctx_px={ds.ctx_px} N={feats.shape[0]} "
              f"({time.time()-t0:.1f}s)")

    if skipped:
        print(f"\n[WARN] {len(skipped)} slides saltados:")
        for s, r in skipped[:50]:
            print(f"   {s}: {r}")
    print("[OK] extracción multi-escala terminada")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
