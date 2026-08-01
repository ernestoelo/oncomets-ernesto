"""figura_atencion_vs_anotaciones.py — figura espacial del experimento del B8.

Muestra, sobre la lámina 129741, dónde cae la atención de CLAM y dónde marcó el patólogo.
Es la figura de lámina del experimento `sprints/B8_sprint8/atencion_vs_patologo/`.

Es una FIGURA (imagen sobre tejido real), no una tabla ni un gráfico: por eso va como PNG
y no como objeto nativo del deck. La regla "tablas y gráficos NATIVOS, no PNG de matplotlib"
([[deck-completo-pptx-buildable]]) aplica a la tabla de AUC, que se arma nativa en el deck
desde `auc_por_checkpoint.csv`.

Panel A: thumbnail + heatmap de atención (cabeza de la clase verdadera, score_3).
Panel B: el mismo thumbnail con los parches anotados por clase.

Etapa 0: CPU, post-hoc. Uso (workaround B):
  CUDA_VISIBLE_DEVICES="" /home/sdonoso/miniconda3/envs/clam_latest/bin/python \
      scripts/figura_atencion_vs_anotaciones.py
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

REPO = Path("/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto")
CLAM_ENVIRON = "/media/administrador/Storage1/sdonoso/clam_environ"
ENVIRON = Path(CLAM_ENVIRON) / "environ"
for p in (str(REPO), CLAM_ENVIRON):
    if p not in sys.path:
        sys.path.insert(0, p)

from scripts.atencion_vs_anotaciones import build_clam, get_attention, CLASSES_4  # noqa: E402

SLIDE = "129741"
WSI = "/media/administrador/Storage1/sdonoso/wsi/129741/129741.bif"
# Checkpoint PRIMARIO (129741 en val) de la cohorte a la que pertenece la lámina.
CKPT = f"{ENVIRON}/results_modelo/grado_histologico_mitotic_rate_s1/s_0_checkpoint.pt"
MAX_SIDE = 1600

COLORES = {
    "Mitosis": "#e6194b", "Nucleos alto grado": "#f58231", "Tumor": "#3cb44b",
    "necrosis": "#911eb4", "Immune cells": "#4363d8", "Stroma": "#00c2c7",
    "Tejido Adiposo": "#9a6324",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(REPO / "sprints/B8_sprint8/atencion_vs_patologo"))
    ap.add_argument("--wsi", default=WSI)
    args = ap.parse_args()
    out = Path(args.out_dir); out.mkdir(parents=True, exist_ok=True)

    import h5py
    import openslide
    with h5py.File(f"{ENVIRON}/features/h5_files/{SLIDE}.h5", "r") as f:
        feats, coords = np.array(f["features"]), np.array(f["coords"])

    sl = openslide.OpenSlide(args.wsi)
    W, H = sl.level_dimensions[0]
    scale = MAX_SIDE / max(W, H)
    thumb = np.array(sl.get_thumbnail((int(W * scale), int(H * scale))).convert("RGB"))
    th, tw = thumb.shape[:2]
    scale_x, scale_y = tw / W, th / H
    ps = 256  # verificado como la moda del paso entre coords (geometría real del h5)

    model, _ = build_clam(len(CLASSES_4), CKPT)
    A, y_prob, y_hat = get_attention(model, feats)
    i_true = CLASSES_4.index("score_3")
    scores = A[i_true]
    pct = (np.argsort(np.argsort(scores)) / (len(scores) - 1))

    ann = pd.read_csv(out.parent / "anotaciones_patologo" / f"parches_anotados_{SLIDE}.csv")

    fig, axes = plt.subplots(1, 2, figsize=(15, 8.2), dpi=220)
    for ax in axes:
        ax.imshow(thumb)
        ax.set_xticks([]); ax.set_yticks([])
        for s in ax.spines.values():
            s.set_visible(False)

    # --- Panel A: atención ---
    cmap = matplotlib.colormaps["turbo"]
    ov = np.zeros((th, tw, 4), dtype=np.float32)
    for (x, y), v in zip(coords, pct):
        x0, y0 = int(x * scale_x), int(y * scale_y)
        x1, y1 = int((x + ps) * scale_x), int((y + ps) * scale_y)
        r, g, b, _ = cmap(float(v))
        ov[y0:y1, x0:x1] = (r, g, b, 0.55)
    a = ov[:, :, 3][:, :, None]
    axes[0].imshow(np.clip(a * ov[:, :, :3] + (1 - a) * (thumb / 255.0), 0, 1))
    axes[0].set_title(f"Atención de CLAM (cabeza score_3)\n"
                      f"predicción: {CLASSES_4[y_hat]}  ·  p={y_prob[y_hat]:.2f}",
                      fontsize=13)

    # --- Panel B: anotaciones ---
    vistos = set()
    for r in ann.itertuples():
        for c in str(r.clases).split("|"):
            c = c.strip()
            col = COLORES.get(c, "#808080")
            axes[1].add_patch(Rectangle(
                (r.x * scale_x, r.y * scale_y), ps * scale_x, ps * scale_y,
                linewidth=1.1, edgecolor=col,
                facecolor=(*matplotlib.colors.to_rgb(col), 0.35),
                label=c if c not in vistos else None))
            vistos.add(c)
    axes[1].legend(loc="lower right", fontsize=9, framealpha=0.92)
    axes[1].set_title("Anotaciones del patólogo (QuPath, realineadas)\n"
                      "163 de 4799 parches quedan bajo alguna marca", fontsize=13)

    fig.tight_layout()
    p = out / "figura_atencion_vs_anotaciones.png"
    fig.savefig(p, bbox_inches="tight", facecolor="white")
    print(f"[out] {p}")

    # --- Figura 2: zoom a los parches de mitosis sobre el mapa de atención ---
    fig2, ax = plt.subplots(figsize=(8.6, 8.6), dpi=220)
    ax.imshow(np.clip(a * ov[:, :, :3] + (1 - a) * (thumb / 255.0), 0, 1))
    mit = ann[ann.clases.str.contains("Mitosis")]
    for r in mit.itertuples():
        ax.add_patch(Rectangle((r.x * scale_x, r.y * scale_y), ps * scale_x, ps * scale_y,
                               linewidth=1.6, edgecolor="white", facecolor="none"))
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_title(f"Los {len(mit)} parches de mitosis (blanco) sobre el mapa de atención",
                 fontsize=13)
    fig2.tight_layout()
    p2 = out / "figura_mitosis_sobre_atencion.png"
    fig2.savefig(p2, bbox_inches="tight", facecolor="white")
    print(f"[out] {p2}")


if __name__ == "__main__":
    main()
