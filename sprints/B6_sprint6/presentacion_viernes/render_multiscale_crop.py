#!/usr/bin/env python
"""render_multiscale_crop.py — crop REAL de un WSI de mama a dos escalas (fino 112µm +
contexto 512µm, mismo centro) para la slide didáctica de magnificación del deck B6.

Read-only sobre el WSI (openslide, CPU). Reusa una coord de tejido de un .h5 de parches
existente para garantizar que el centro cae en tejido (no fondo). Sin GPU.

Uso:
  /home/sdonoso/miniconda3/envs/clam_latest/bin/python \
    sprints/B6_sprint6/presentacion_viernes/render_multiscale_crop.py --mode montage
  ... --mode final --coord-idx <i>   # renderiza el par limpio de la coord elegida
"""
import argparse
import os

import h5py
import numpy as np
import openslide
from PIL import Image, ImageDraw
from scipy.spatial import cKDTree

REPO = "/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto"
OUT = os.path.join(REPO, "sprints/B6_sprint6/presentacion_viernes")
ASSETS = os.path.join(REPO, "papers/presentations/assets_branding/multiscale_crop")
QA = os.path.join(OUT, "_qa_crop")

WSI = ("/media/administrador/Storage1/sdonoso/TCGA_dataset_curated/"
       "TCGA-3C-AALI-01Z-00-DX1/"
       "TCGA-3C-AALI-01Z-00-DX1.F6E9A5DF-D8FB-45CF-B4BD-C6B76294C291.svs")
H5 = ("/media/administrador/Storage1/sdonoso/clam_environ/environ/features/h5_files/"
      "TCGA-3C-AALI-01Z-00-DX1.F6E9A5DF-D8FB-45CF-B4BD-C6B76294C291.h5")

MPP = 0.2325                 # TCGA level0 (verificado openslide, [[cohortes-magnificacion-fisica]])
FINE_UM = 112.0
CTX_UM = 512.0
DISP = 460                   # px de display de cada panel


def load_coords():
    with h5py.File(H5, "r") as f:
        coords = f["coords"][:]                      # top-left de cada parche a level0
        ps = int(f["coords"].attrs.get("patch_size", 256))
    centers = coords + ps // 2
    return centers


def pick_dense(centers, n=6, ctx_px=None, min_sep=None):
    """Elige n centros en tejido DENSO (muchos vecinos a escala contexto) y separados."""
    tree = cKDTree(centers)
    dens = tree.query_ball_point(centers, r=ctx_px, return_length=True)
    order = np.argsort(-dens)                         # más denso primero
    picked = []
    for i in order:
        c = centers[i]
        if all(np.hypot(*(c - centers[j])) > min_sep for j in picked):
            picked.append(i)
        if len(picked) == n:
            break
    return picked


def crop(slide, cx, cy, field_px):
    """read_region centrado en (cx,cy) cubriendo field_px a level0 → PIL RGB DISP×DISP."""
    x0 = int(cx - field_px // 2)
    y0 = int(cy - field_px // 2)
    W, H = slide.level_dimensions[0]
    x0 = max(0, min(x0, W - field_px))               # clamp a bordes (no black-fill)
    y0 = max(0, min(y0, H - field_px))
    img = slide.read_region((x0, y0), 0, (field_px, field_px)).convert("RGB")
    return img.resize((DISP, DISP), Image.LANCZOS)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["montage", "final"], default="montage")
    ap.add_argument("--coord-idx", type=int, default=None,
                    help="índice (0-based) de la lista de candidatos densos a renderizar en final")
    args = ap.parse_args()

    fine_px = round(FINE_UM / MPP)                    # 482
    ctx_px = round(CTX_UM / MPP)                       # 2202
    centers = load_coords()
    picks = pick_dense(centers, n=6, ctx_px=ctx_px, min_sep=ctx_px * 2)
    slide = openslide.OpenSlide(WSI)
    print(f"[info] mpp={MPP} fine_px={fine_px} ctx_px={ctx_px} · {len(centers)} coords · picks={picks}")

    if args.mode == "montage":
        os.makedirs(QA, exist_ok=True)
        pad = 10
        cols = 2                                       # fino | contexto
        rows = len(picks)
        cell = DISP + pad
        sheet = Image.new("RGB", (cols * cell + pad, rows * cell + pad + 22 * rows), "white")
        draw = ImageDraw.Draw(sheet)
        for r, idx in enumerate(picks):
            cx, cy = centers[idx]
            fine = crop(slide, cx, cy, fine_px)
            ctx = crop(slide, cx, cy, ctx_px)
            # caja del campo fino dentro del contexto (112/512 del ancho)
            box = int(DISP * FINE_UM / CTX_UM)
            off = (DISP - box) // 2
            d2 = ImageDraw.Draw(ctx)
            d2.rectangle([off, off, off + box, off + box], outline=(226, 114, 59), width=3)
            y = pad + r * (cell + 22)
            sheet.paste(fine, (pad, y))
            sheet.paste(ctx, (pad + cell, y))
            draw.text((pad, y + DISP + 4), f"idx={r}  center=({cx},{cy})  |  fino 112um | contexto 512um",
                      fill=(0, 0, 0))
        p = os.path.join(QA, "candidates_montage.png")
        sheet.save(p)
        print("[montage]", p)
    else:
        assert args.coord_idx is not None, "pasa --coord-idx"
        os.makedirs(ASSETS, exist_ok=True)
        idx = picks[args.coord_idx]
        cx, cy = centers[idx]
        fine = crop(slide, cx, cy, fine_px)
        ctx = crop(slide, cx, cy, ctx_px)
        box = int(DISP * FINE_UM / CTX_UM)
        off = (DISP - box) // 2
        ImageDraw.Draw(ctx).rectangle([off, off, off + box, off + box],
                                      outline=(226, 114, 59), width=4)
        fine.save(os.path.join(ASSETS, "fine_112um.png"))
        ctx.save(os.path.join(ASSETS, "context_512um.png"))
        print("[final] center=", (cx, cy), "->", ASSETS)


if __name__ == "__main__":
    main()
