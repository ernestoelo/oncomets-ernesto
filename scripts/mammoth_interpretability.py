"""mammoth_interpretability.py — OBJ-A (B5): qué mira cada experto/slot de MAMMOTH en mama.

Adaptación propia del tutorial de la librería
(`clam_testing2/MAMMOTH/examples/tutorial_mammoth_visualization.py`) a NUESTROS
checkpoints (CLAM_MB_Mammoth) y a la estructura de datos del servidor Environ.
Es **Etapa 0: CPU, post-hoc, sin GPU, sin sbatch** — inferencia sobre un checkpoint
congelado, NO toca modelo/training (regla 9 no aplica).

Produce, para una WSI de mama:
  1. dispatch_weights (1, N, E=30, H=16, S=10) vía mammoth(x, return_weights=True).
  2. score por experto = mean sobre (H, S) → (N, E).
  3. heatmap de ruteo por experto sobre el thumbnail + un MONTAGE de los 30 expertos.
  4. top-k parches por experto, recortados a ALTA RESOLUCIÓN del .svs (read_region),
     + un contact sheet (expertos × top-k).
  5. expert_usage.csv (ranking de expertos por uso medio) + meta.json (provenance).

Diferencias clave vs el tutorial lung (verificadas 30-jun, handoff §6 + checkpoint real):
  - Prefijo del state_dict: `attention_net.0.mammoth.`  (NO `mlp.router.mammoth.`).
  - Config Mammoth = la NUESTRA (CONCH 512): input_dim=512, dim=512, num_experts=30,
    num_slots=10, num_heads=16, slot_dim=256, auto_rank=True (→ rank 8). `keep_slots`
    se infiere del checkpoint o se pasa por flag.
  - Features + coords viven en el MISMO h5 (`features` + `coords`); el handoff decía
    archivos separados (.pt/.h5) — falso, ambos están en el h5 (verificado).

NUNCA correr con `python` a secas (workaround B). Usar el binario absoluto del env:
  CUDA_VISIBLE_DEVICES="" /home/sdonoso/miniconda3/envs/clam_latest/bin/python \
      scripts/mammoth_interpretability.py --ckpt ... --h5 ... --wsi ... --out-dir ...
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

try:
    import h5py
except ImportError:  # pragma: no cover
    h5py = None
try:
    import openslide
except ImportError:  # pragma: no cover
    openslide = None
try:
    from PIL import Image
except ImportError:  # pragma: no cover
    Image = None

# Import Mammoth desde la librería vendorizada (editable en clam_latest). Mismo
# patrón que models_mammoth/clam_mammoth.py + fallback a src.mammoth del repo.
_MAMMOTH_REPO = "/media/administrador/Storage1/sdonoso/clam_testing2/MAMMOTH"
try:
    from mammoth import Mammoth
except ImportError:  # pragma: no cover
    if _MAMMOTH_REPO not in sys.path:
        sys.path.insert(0, _MAMMOTH_REPO)
    from src.mammoth import Mammoth

# ---- Constantes de extracción (CLAM/CONCH estándar: parche 256 @ 20x) --------
H5_FEAT_KEY = "features"
COORDS_KEY = "coords"
PATCH_SIZE_AT_EXTRACTION = 256
FEATURE_EXTRACTION_MAG = 20
LEVEL0_MAG_FALLBACK = 40
MAX_THUMBNAIL_SIDE = 4000
HEATMAP_ALPHA = 0.45
STATE_DICT_PREFIX = "attention_net.0.mammoth."

# ---- Config Mammoth NUESTRA (CONCH 512) --------------------------------------
MAMMOTH_CONFIG = dict(
    input_dim=512,
    dim=512,
    num_experts=30,
    num_slots=10,
    num_heads=16,
    slot_dim=256,
    auto_rank=True,
    share_lora_weights=True,
    dropout=0.0,
    slot_dropout=0.0,
)


# =============================================================================
# 1. Cargar Mammoth desde nuestro checkpoint
# =============================================================================
def load_mammoth_state_dict(ckpt_path, device="cpu"):
    """Extrae el sub-state_dict de Mammoth de un checkpoint CLAM_MB_Mammoth."""
    ckpt = torch.load(ckpt_path, map_location=device)
    model_sd = ckpt.get("model", ckpt) if isinstance(ckpt, dict) else ckpt
    stripped = {
        k[len(STATE_DICT_PREFIX):]: v
        for k, v in model_sd.items()
        if k.startswith(STATE_DICT_PREFIX)
    }
    if not stripped:
        raise ValueError(
            f"No hay keys con prefijo {STATE_DICT_PREFIX!r} en el checkpoint. "
            f"Keys: {list(model_sd.keys())[:10]}..."
        )
    return stripped


def infer_keep_slots(state_dict):
    """keep_slots no cambia el state_dict; se pasa por flag. Default = False (drop-in)."""
    return None  # señal: usar el flag/CLI


def build_mammoth(ckpt_path, keep_slots, device="cpu"):
    """Construye Mammoth con NUESTRA config, carga pesos, eval()."""
    mammoth = Mammoth(keep_slots=keep_slots, **MAMMOTH_CONFIG)
    sd = load_mammoth_state_dict(ckpt_path, device)
    mammoth.load_state_dict(sd, strict=True)
    mammoth.to(device).eval()
    return mammoth, sd


# =============================================================================
# 2. Features/coords (mismo h5) + forward → scores por experto
# =============================================================================
def load_feats_and_coords(h5_path):
    """Lee features (N, 512) y coords (N, 2) del MISMO h5. Coords = px nivel-0."""
    if h5py is None:
        raise ImportError("h5py requerido")
    with h5py.File(h5_path, "r") as f:
        fkey = H5_FEAT_KEY if H5_FEAT_KEY in f else "feats"
        if fkey not in f:
            raise KeyError(f"Sin key de features en {list(f.keys())}")
        feats = np.asarray(f[fkey], dtype=np.float32)
        if COORDS_KEY not in f:
            raise KeyError(f"Sin key {COORDS_KEY!r} en {list(f.keys())}")
        coords = np.asarray(f[COORDS_KEY], dtype=np.float64)
    if feats.ndim == 3 and feats.shape[0] == 1:
        feats = feats.squeeze(0)
    if coords.ndim == 3 and coords.shape[0] == 1:
        coords = coords.squeeze(0)
    return feats, coords[:, :2]


def compute_expert_scores(mammoth, feats, device="cpu"):
    """Forward → dispatch_weights (1,N,E,H,S); normaliza por parche; score=(N,E)."""
    x = torch.from_numpy(feats).float().unsqueeze(0).to(device)
    with torch.no_grad():
        _, dispatch = mammoth(x, return_weights=True)  # (1, N, E, H, S)
    # normalizar por parche sobre (E,H,S): fracción del ruteo del parche a cada (e,h,s)
    dispatch = dispatch / dispatch.sum(dim=(2, 3, 4), keepdim=True)
    scores = dispatch[0].mean(dim=(2, 3))  # (N, E)
    return scores.cpu().numpy().astype(np.float64), tuple(dispatch.shape)


def compute_slot_weights(mammoth, feats, device="cpu"):
    """Peso de RUTEO por SLOT (B7 Q1 — distinto del top-k de parches por experto).

    Replica los primeros pasos del forward de Mammoth (proyección + split multi-cabeza)
    y llama a `get_weights` para obtener `combine_weights` — la 2ª softmax, sobre los
    E·S=300 slots (`mammoth.py:411`), que es el "peso de cada slot durante el ruteo hacia
    los expertos". Agrega sobre parches (N) y cabezas (H) → importancia por slot (E,S).
    También devuelve el logit crudo medio por slot (similitud query↔prototipo = "los más
    parecidos"). NO reentrena ni modifica nada: sólo lee el forward (Etapa 0, post-hoc).

    Devuelve: slot_combine (E,S), slot_logit (E,S), sumas de chequeo.
    """
    x = torch.from_numpy(feats).float().unsqueeze(0).to(device)
    H = mammoth.num_heads
    with torch.no_grad():
        # pasos 1-2 del forward (mammoth.py:341-342): proyección + norm + split multi-cabeza
        q = mammoth.norm(mammoth.wq(x))               # (1, N, slot_dim)
        b, n, _ = q.shape
        q = q.reshape(b, n, H, -1)                    # (1, N, H, P)  ≡ rearrange "b n (h d)->b n h d"
        logits = mammoth.get_logits(q)                # (1, N, E, H, S)
        combine, dispatch = mammoth.get_weights(logits)  # combine: (1, N, H, E*S)
    E, S = mammoth.num_experts, mammoth.num_slots
    # combine: softmax sobre los E*S slots (dim=-1). Importancia media por slot sobre (b,N,H).
    slot_combine = combine.mean(dim=(0, 1, 2)).reshape(E, S).cpu().numpy().astype(np.float64)
    # logit crudo medio por slot (similitud) sobre (b,N,H): "los más parecidos"
    slot_logit = logits.mean(dim=(0, 1, 3)).reshape(E, S).cpu().numpy().astype(np.float64)
    return slot_combine, slot_logit


def save_slot_usage(slot_combine, slot_logit, out_dir, topn=20):
    """Escribe slot_usage.csv (300 filas, orden desc por peso de combine) + bar chart top-N."""
    E, S = slot_combine.shape
    rows = []
    for e in range(E):
        for s in range(S):
            rows.append((e, s, slot_combine[e, s], slot_logit[e, s]))
    rows.sort(key=lambda r: r[2], reverse=True)
    header = "rank,expert,slot,mean_combine_weight,mean_routing_logit\n"
    lines = [header]
    for rank, (e, s, cw, lg) in enumerate(rows):
        lines.append(f"{rank},{e},{s},{cw:.6e},{lg:.6e}\n")
    (Path(out_dir) / "slot_usage.csv").write_text("".join(lines))
    # bar chart top-N slots
    top = rows[:topn]
    labels = [f"e{e}·s{s}" for e, s, _, _ in top]
    vals = [cw for _, _, cw, _ in top]
    fig, ax = plt.subplots(figsize=(max(6, topn * 0.5), 3.2))
    ax.bar(range(len(top)), vals, color="#31859C")
    ax.set_xticks(range(len(top))); ax.set_xticklabels(labels, rotation=60, ha="right", fontsize=7)
    ax.set_ylabel("peso de ruteo medio\n(combine, softmax sobre 300 slots)", fontsize=8)
    ax.set_title(f"Top-{topn} slots por peso de ruteo (de E·S={E*S})", fontsize=10)
    ax.axhline(1.0 / (E * S), color="#B4521E", ls="--", lw=0.8, label="uniforme 1/300")
    ax.legend(fontsize=7)
    plt.tight_layout()
    plt.savefig(Path(out_dir) / "slot_usage_top.png", dpi=120)
    plt.close()
    return rows[:topn]


def percentile_scores(scores_e):
    """Mapea scores de un experto a [0,1] por percentil (robusto a escala)."""
    n = scores_e.size
    if n <= 1:
        return np.zeros_like(scores_e, dtype=np.float64)
    ranks = np.argsort(np.argsort(scores_e)).astype(np.float64)
    return ranks / (n - 1)


# =============================================================================
# 3. Thumbnail + heatmaps de ruteo
# =============================================================================
def get_wsi_thumbnail(svs_path, max_side=MAX_THUMBNAIL_SIDE):
    if openslide is None:
        raise ImportError("openslide requerido")
    slide = openslide.OpenSlide(str(svs_path))
    level0_w, level0_h = slide.dimensions
    level0_mag = None
    for key in ("openslide.objective-power", "aperio.AppMag"):
        try:
            mag = float(slide.properties.get(key, 0) or 0)
            if mag > 0:
                level0_mag = mag
                break
        except (TypeError, ValueError):
            continue
    if level0_mag is None:
        level0_mag = float(LEVEL0_MAG_FALLBACK)
    scale = min(1.0, max_side / max(level0_w, level0_h))
    new_w, new_h = int(round(level0_w * scale)), int(round(level0_h * scale))
    thumb = np.array(slide.get_thumbnail((new_w, new_h)).convert("RGB"))
    slide.close()
    actual_w = thumb.shape[1]
    scale = actual_w / level0_w
    return thumb, scale, level0_mag, level0_w, level0_h


def patch_size_at_level0(level0_mag):
    if level0_mag is None or level0_mag <= FEATURE_EXTRACTION_MAG:
        level0_mag = LEVEL0_MAG_FALLBACK
    return PATCH_SIZE_AT_EXTRACTION * (level0_mag / FEATURE_EXTRACTION_MAG)


def build_overlay_rgba(coords0, pct_e, scale, thumb_w, thumb_h, patch_size0):
    try:
        cmap = matplotlib.colormaps["turbo"]
    except (AttributeError, KeyError):
        cmap = plt.cm.get_cmap("turbo")
    patch_thumb = max(1, int(round(patch_size0 * scale)))
    px = np.round(coords0[:, 0] * scale).astype(np.int32)
    py = np.round(coords0[:, 1] * scale).astype(np.int32)
    pct = np.clip(pct_e.astype(np.float64), 0.0, 1.0)
    if px.size == 0:
        return np.zeros((thumb_h, thumb_w, 4), dtype=np.float32)
    grid = np.arange(patch_thumb, dtype=np.int32)
    rr = py[:, None, None] + grid[None, :, None] + np.zeros((1, 1, patch_thumb), np.int32)
    cc = px[:, None, None] + grid[None, None, :] + np.zeros((1, patch_thumb, 1), np.int32)
    valid = (rr >= 0) & (rr < thumb_h) & (cc >= 0) & (cc < thumb_w)
    vflat = valid.ravel()
    row = rr.ravel()[vflat]
    col = cc.ravel()[vflat]
    pflat = np.repeat(pct, patch_thumb * patch_thumb)[vflat]
    n_pix = thumb_h * thumb_w
    s = np.zeros(n_pix); c = np.zeros(n_pix)
    idx = row * thumb_w + col
    np.add.at(s, idx, pflat)
    np.add.at(c, idx, 1.0)
    c = np.maximum(c, 1.0)
    avg = (s / c).reshape(thumb_h, thumb_w)
    hit = (c.reshape(thumb_h, thumb_w) > 0)
    overlay = np.zeros((thumb_h, thumb_w, 4), dtype=np.float32)
    overlay[hit] = np.array(cmap(avg[hit]), dtype=np.float32)
    overlay[hit, 3] = HEATMAP_ALPHA
    return overlay


def blend(thumb, overlay):
    a = overlay[:, :, 3][:, :, None]
    return np.clip(a * overlay[:, :, :3] + (1 - a) * (thumb.astype(np.float32) / 255.0), 0, 1)


def save_expert_heatmap(thumb, coords0, scores_e, scale, patch_size0, out_path, label):
    th, tw = thumb.shape[:2]
    overlay = build_overlay_rgba(coords0, percentile_scores(scores_e), scale, tw, th, patch_size0)
    blended = blend(thumb, overlay)
    fig, ax = plt.subplots(figsize=(tw / 150, th / 150))
    ax.imshow(blended); ax.set_axis_off()
    ax.text(tw * 0.02, th * 0.98, label, ha="left", va="top",
            fontsize=12, color="white", weight="bold",
            bbox=dict(facecolor="black", alpha=0.4, pad=2, edgecolor="none"))
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    plt.savefig(out_path, bbox_inches="tight", pad_inches=0, dpi=120)
    plt.close()


def save_heatmap_montage(thumb, coords0, scores, scale, patch_size0, out_path, order):
    """Grid de los E expertos (ordenados por uso) sobre el thumbnail."""
    th, tw = thumb.shape[:2]
    E = scores.shape[1]
    ncol = 6
    nrow = int(np.ceil(E / ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(ncol * 2.6, nrow * 2.6 * th / tw))
    axes = np.atleast_1d(axes).ravel()
    for ax in axes:
        ax.set_axis_off()
    for cell, e in enumerate(order):
        overlay = build_overlay_rgba(coords0, percentile_scores(scores[:, e]),
                                     scale, tw, th, patch_size0)
        axes[cell].imshow(blend(thumb, overlay))
        axes[cell].set_title(f"experto {e}", fontsize=8)
    plt.tight_layout()
    plt.savefig(out_path, bbox_inches="tight", dpi=110)
    plt.close()


# =============================================================================
# 4. Top-k parches a ALTA RESOLUCIÓN (read_region del .svs)
# =============================================================================
def read_hires_patch(slide, x0, y0, patch_size0, out_px=256):
    """Lee un parche a nivel-0 del .svs y lo baja a out_px×out_px (RGB)."""
    size = int(round(patch_size0))
    region = slide.read_region((int(x0), int(y0)), 0, (size, size)).convert("RGB")
    if Image is not None and size != out_px:
        region = region.resize((out_px, out_px), Image.BILINEAR)
    return np.asarray(region)


def save_topk_hires(svs_path, coords0, scores, patch_size0, k, out_dir, order):
    """Para cada experto, guarda sus top-k parches a alta resolución + contact sheet."""
    out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    slide = openslide.OpenSlide(str(svs_path))
    E = scores.shape[1]
    k = min(k, scores.shape[0])
    sheet = np.full(((E * 256), (k * 256), 3), 255, dtype=np.uint8)
    for row, e in enumerate(order):
        top = np.argsort(scores[:, e])[::-1][:k]
        for col, idx in enumerate(top):
            patch = read_hires_patch(slide, coords0[idx, 0], coords0[idx, 1], patch_size0)
            plt.imsave(out_dir / f"expert_{e:02d}_rank_{col:02d}.png", patch)
            sheet[row * 256:(row + 1) * 256, col * 256:(col + 1) * 256] = patch
    slide.close()
    # contact sheet con etiquetas de experto
    fig, ax = plt.subplots(figsize=(k * 1.1, E * 1.1))
    ax.imshow(sheet); ax.set_axis_off()
    for row, e in enumerate(order):
        ax.text(-10, row * 256 + 128, f"e{e}", ha="right", va="center", fontsize=8)
    ax.set_title(f"top-{k} parches por experto (orden = uso medio desc.)", fontsize=10)
    plt.savefig(out_dir.parent / "topk_contact_sheet.png", bbox_inches="tight", dpi=110)
    plt.close()


# =============================================================================
# Main
# =============================================================================
def main():
    ap = argparse.ArgumentParser(description="OBJ-A: interpretabilidad de expertos MAMMOTH")
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--h5", required=True)
    ap.add_argument("--wsi", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--keep-slots", action="store_true",
                    help="usar keep_slots=True (checkpoints obj3). Default False (drop-in).")
    ap.add_argument("--topk", type=int, default=8)
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--label", default="", help="texto opcional (y_true/y_pred) para meta.json")
    args = ap.parse_args()

    out_dir = Path(args.out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    for p in (args.ckpt, args.h5, args.wsi):
        if not Path(p).exists():
            raise SystemExit(f"No existe: {p}")

    print("[1/5] Cargando Mammoth desde checkpoint...")
    mammoth, sd = build_mammoth(args.ckpt, keep_slots=args.keep_slots, device=args.device)
    print(f"      keep_slots={args.keep_slots} | rank={mammoth.lora_rank} | "
          f"slot_embeds={tuple(sd['slot_embeds'].shape)}")

    print("[2/5] Features + coords + forward...")
    feats, coords = load_feats_and_coords(args.h5)
    scores, dshape = compute_expert_scores(mammoth, feats, args.device)
    print(f"      feats={feats.shape} coords={coords.shape} dispatch={dshape} scores={scores.shape}")

    # ranking de expertos por uso medio (para ordenar montage / contact sheet)
    usage = scores.mean(axis=0)  # (E,)
    order = list(np.argsort(usage)[::-1])
    np.savetxt(out_dir / "expert_usage.csv",
               np.column_stack([np.arange(len(usage)), usage]),
               fmt=["%d", "%.6e"], delimiter=",", header="expert,mean_score", comments="")
    print(f"      top-5 expertos por uso: {[int(e) for e in order[:5]]}")

    # peso de ruteo por SLOT (B7 Q1): combine_weights sobre los 300 slots
    print("[2b/6] Peso de ruteo por slot (combine_weights sobre E·S=300)...")
    slot_combine, slot_logit = compute_slot_weights(mammoth, feats, args.device)
    top_slots = save_slot_usage(slot_combine, slot_logit, out_dir)
    print(f"      top-5 slots (e·s) por peso de ruteo: "
          f"{[(int(e), int(s)) for e, s, _, _ in top_slots[:5]]}")

    print("[3/6] Thumbnail...")
    thumb, scale, mag, w0, h0 = get_wsi_thumbnail(args.wsi)
    if np.nanmax(coords) <= 1.1:  # coords normalizadas → reescalar a px nivel-0
        coords = coords * np.array([w0, h0])
    ps0 = patch_size_at_level0(mag)
    print(f"      thumb={thumb.shape[:2]} mag={mag} patch_size_level0={ps0:.0f}px")

    print("[4/6] Heatmaps por experto + montage...")
    hm_dir = out_dir / "heatmaps"; hm_dir.mkdir(exist_ok=True)
    for e in range(scores.shape[1]):
        save_expert_heatmap(thumb, coords, scores[:, e], scale, ps0,
                            hm_dir / f"expert_{e:02d}.png", f"experto {e}")
    save_heatmap_montage(thumb, coords, scores, scale, ps0,
                         out_dir / "heatmap_montage.png", order)

    print("[5/6] Top-k parches a alta resolución + contact sheet...")
    save_topk_hires(args.wsi, coords, scores, ps0, args.topk,
                    out_dir / "topk_patches", order)

    meta = dict(
        ckpt=args.ckpt, h5=args.h5, wsi=args.wsi, label=args.label,
        keep_slots=args.keep_slots, lora_rank=mammoth.lora_rank,
        config=MAMMOTH_CONFIG, n_patches=int(feats.shape[0]),
        dispatch_shape=list(dshape), level0_mag=mag, patch_size_level0=float(ps0),
        expert_order_by_usage=[int(e) for e in order],
        top_slots_by_routing=[(int(e), int(s), float(cw)) for e, s, cw, _ in top_slots],
    )
    (out_dir / "meta.json").write_text(json.dumps(meta, indent=2))
    print(f"\nListo. Salida en: {out_dir}")


if __name__ == "__main__":
    main()
