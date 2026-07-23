"""slot_heatmaps_contraste.py — heatmap espacial POR SLOT de los top slots (B7).

Para el contraste tabla ↔ imagen que pidio Ernesto. La tabla (slot_usage.csv) rankea los
300 slots por peso de ruteo; esta figura MUESTRA que tejido enciende cada uno de los slots
top, sobre la lamina real. Es el analogo de la Fig.3 del paper Mammoth (mapa de
«patch-slot similarity», rotulado por par experto+slot).

POR QUE POR SLOT Y NO POR EXPERTO ([[slot-unidad-de-morfologia]], [[heatmap-atencion-no-es-per-experto]]):
  - Los heatmaps que YA existian (`heatmaps/expert_N.png`) son por EXPERTO y usan la 1a
    softmax (`dispatch`). A nivel experto el ruteo es ~uniforme (30.0/30), asi que la tabla
    (que rankea slots) NO se contrasta con ellos: mezclaria dos softmax (dispatch vs
    combine) y dos niveles (experto vs slot).
  - Este script usa la MISMA softmax que la tabla — `combine` (2a softmax, sobre los 300
    slots) — SIN colapsar el eje espacial N, y selecciona la columna del slot (e,s). Asi el
    heatmap y el ranking hablan del mismo objeto.

CPU, post-hoc, read-only. NO toca modelo ni training (regla 9 no aplica).

Uso:
  CUDA_VISIBLE_DEVICES="" /home/sdonoso/miniconda3/envs/clam_latest/bin/python \
      scripts/slot_heatmaps_contraste.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = Path("/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto")
sys.path.insert(0, str(REPO))
sys.path.insert(0, "/media/administrador/Storage1/sdonoso/clam_environ")

from scripts.mammoth_interpretability import (  # noqa: E402
    build_mammoth, load_feats_and_coords, get_wsi_thumbnail, percentile_scores,
    build_overlay_rgba, blend,
)
from scripts.clam_vs_mammoth_attention import infer_patch_size_level0  # noqa: E402

INTERP = REPO / "results/b7_mammoth_interp/interpretabilidad"
OUT = REPO / "sprints/B7_sprint7/slot_softmax/heatmaps"
TOPK = 4  # slots a mostrar

# lamina representativa por tarea (task_key -> slide_id que empieza asi)
REPR = {
    "tipo_histologico_3clases_ci": "TCGA-AC-A8OS",
    "carcinoma_ductal_insitu_presente_ci_reform": "TCGA-D8-A1XB",
    "invasion_linfatica_vascular_ci_reform": "TCGA-D8-A1X5",
}
TASK_LABEL = {
    "tipo_histologico_3clases_ci": "tipo_histologico",
    "carcinoma_ductal_insitu_presente_ci_reform": "cdis",
    "invasion_linfatica_vascular_ci_reform": "lvi",
}


def slot_combine_spatial(mammoth, feats, device="cpu"):
    """combine (2a softmax) SIN colapsar N -> (N, E*S). Mismo tensor que la tabla."""
    x = torch.from_numpy(feats).float().unsqueeze(0).to(device)
    H = mammoth.num_heads
    with torch.no_grad():
        q = mammoth.norm(mammoth.wq(x))
        b, n, _ = q.shape
        q = q.reshape(b, n, H, -1)
        logits = mammoth.get_logits(q)                 # (1,N,E,H,S)
        combine, _ = mammoth.get_weights(logits)       # (1,N,H,E*S)
    return combine[0].mean(dim=1).cpu().numpy().astype(np.float64)  # (N, E*S)


def pick_diverse_slots(comb, su, S, k, pool=20):
    """Del top-`pool` por peso, elige greedy k slots ESPACIALMENTE diversos.

    Los slots mas pesados no son redundantes (corr media ~0) pero algunos si se
    parecen entre si (p.ej. dos que rutean el mismo tejido, corr ~0.9). Mostrar dos
    casi identicos desperdicia un panel. Greedy: parte del top-1 y agrega el slot del
    pool que MINIMIZA su maxima correlacion con los ya elegidos -> paneles que encienden
    tejidos distintos, todos altos en la tabla (se rotula su rank real).
    """
    cand = su.head(pool)
    ranks = np.vstack([np.argsort(np.argsort(comb[:, int(r.expert) * S + int(r.slot)]))
                       for r in cand.itertuples()])
    R = np.corrcoef(ranks)
    chosen = [0]
    while len(chosen) < k:
        best, best_score = None, 2.0
        for j in range(len(cand)):
            if j in chosen:
                continue
            score = max(R[j, c] for c in chosen)   # cuanto se parece al mas parecido ya elegido
            if score < best_score:
                best, best_score = j, score
        chosen.append(best)
    return cand.iloc[chosen]


def footprint(thumb, coords, col, scale, ps0, q=0.85):
    """Huella del slot: pinta SOLO el top-(1-q) de parches, resto = tejido visible.

    percentile_scores + turbo pintaba TODOS los parches y aplastaba el contraste entre
    slots. Aca cada panel muestra donde se CONCENTRA el slot -> el contraste morfologico
    entre slots distintos salta a la vista."""
    th, tw = thumb.shape[:2]
    p = percentile_scores(col)                     # [0,1] por percentil
    keep = p >= q
    ov = build_overlay_rgba(coords[keep], p[keep], scale, tw, th, ps0)
    return blend(thumb, ov)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    sel = json.loads((REPO / "sprints/B7_sprint7/interp_slides.json").read_text())

    for task_key, short in REPR.items():
        label = TASK_LABEL[task_key]
        cfg = sel[task_key]
        sl = [s for s in cfg["slides"] if s["slide_id"].startswith(short)][0]
        slide_dir = INTERP / task_key / sl["slide_id"].split(".")[0]
        # el slot_usage.csv de ESTA lamina fija el ranking (no el promedio de tarea)
        su = pd.read_csv(slide_dir / "expertos" / "slot_usage.csv")

        # tabla mini de ESTA lamina (calza 1:1 con los heatmaps): top-12 + fila resto
        TOPN = 12
        w = su["mean_combine_weight"].to_numpy(float)
        mini = pd.DataFrame({
            "rank": np.arange(1, TOPN + 1),
            "slot": [f"e{int(e)}·s{int(s)}" for e, s in
                     zip(su["expert"].head(TOPN), su["slot"].head(TOPN))],
            "peso_pct": (w[:TOPN] * 100).round(3),
            "masa_acum_pct": (np.cumsum(w[:TOPN]) * 100).round(1),
        })
        mini.loc[len(mini)] = [f"{TOPN + 1}–300", f"otros {300 - TOPN} slots",
                               round(w[TOPN:].sum() * 100, 2), 100.0]
        mini.to_csv(OUT / f"slot_mini_{label}.csv", index=False)

        print(f"\n[{label}] {short}  (clase real: {sl['label']})")
        mammoth, _ = build_mammoth(cfg["ckpt_mammoth"], keep_slots=False, device="cpu")
        feats, coords = load_feats_and_coords(sl["h5"])
        comb = slot_combine_spatial(mammoth, feats)          # (N, E*S)
        S = mammoth.num_slots

        # slots DIVERSOS del top por peso (no dos que rutean el mismo tejido)
        top = pick_diverse_slots(comb, su, S, TOPK, pool=20)
        print("   slots elegidos (rank en la tabla): " +
              ", ".join(f"e{int(r.expert)}·s{int(r.slot)}(#{int(r.rank)+1})"
                        for r in top.itertuples()))

        thumb, scale, mag, _, _ = get_wsi_thumbnail(sl["wsi"])
        ps0 = infer_patch_size_level0(coords)                # geometria real del h5

        th, tw = thumb.shape[:2]
        fig, axes = plt.subplots(1, TOPK + 1, figsize=((TOPK + 1) * 4.4, 4.4 * th / tw + 0.7))
        axes[0].imshow(thumb); axes[0].set_axis_off()
        axes[0].set_title(f"{short}\n{sl['label']}", fontsize=11)

        for ax, r in zip(axes[1:], top.itertuples()):
            e, s = int(r.expert), int(r.slot)
            col = comb[:, e * S + s]                          # peso del slot por parche
            ax.imshow(footprint(thumb, coords, col, scale, ps0, q=0.85)); ax.set_axis_off()
            ax.set_title(f"e{e}·s{s}   {100 * r.mean_combine_weight:.1f}%\n"
                         f"(#{int(r.rank) + 1} de 300)", fontsize=11)

        fig.suptitle(f"Donde se concentra cada slot (top 15% de parches) — {label}  ·  "
                     f"combine, softmax sobre 300 slots", fontsize=12)
        plt.tight_layout()
        out_png = OUT / f"slot_heatmaps_{label}.png"
        plt.savefig(out_png, bbox_inches="tight", dpi=120)
        plt.close()
        print(f"   -> {out_png.relative_to(REPO)}")


if __name__ == "__main__":
    main()
