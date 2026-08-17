"""overlay_anotaciones_atencion.py — atencion de CLAM y Mammoth CONTRA las marcas del patologo.

Fase 1, paso 5 del plan de la semana del 17-ago (`plan_semana_17ago.md`). Responde, sobre la
129741, la pregunta que Sebastian quiere ver dibujada: **¿los dos brazos miran donde el patologo
marco?** No es un AUC (eso lo mide `atencion_vs_anotaciones.py` con su nulo por traslacion): es
la figura, mas la tabla de percentil medio de atencion por grupo de anotacion.

QUE CABEZA SE DIBUJA. CLAM_MB tiene UNA cabeza de atencion por clase. Se dibuja la de la clase
VERDADERA (`--head true`, default), que es la que puntua evidencia a favor del diagnostico real
— es la pregunta correcta cuando se contrasta contra marcas de patologo. `--head pred` dibuja la
de la clase predicha, que es lo que usa `clam_vs_mammoth_attention.py`. En la 129741 NO son la
misma: los dos brazos predicen `no` y la verdad es `si`.

DOS TRAMPAS DE ESTA LAMINA, las dos anticipadas en el codigo:
  - la atencion de `attention_only` viene PRE-softmax -> se normaliza sobre los N parches;
  - el `.bif` tiene DOS regiones de escaneo (`region[1].y = 49920`) y el tejido sale DOS VECES en
    todo mapa. Las 163 marcas caen todas en la de abajo, asi que ademas de la lamina entera se
    emite una figura CONFINADA a esa region ([[anotaciones-patologo-qupath]] ADDENDUM 1-ago: si
    una region recibiera mas atencion que la otra se estaria midiendo la region, no las marcas).

Los positivos son PARCIALES: un parche sin marca NO es un negativo. Por eso esto se lee como
"donde mira" y no como precision. El sesgo tiene direccion y es conservador.

CPU, post-hoc, read-only. NO toca modelo ni training (regla 9 no aplica).

Uso (workaround B, binario absoluto):
  CUDA_VISIBLE_DEVICES="" /home/sdonoso/miniconda3/envs/clam_latest/bin/python \
      scripts/overlay_anotaciones_atencion.py \
      --selection sprints/B8_sprint8/hovernext_129741/interp_slides_129741.json \
      --anotaciones sprints/B8_sprint8/anotaciones_patologo/parches_anotados_129741.csv \
      --out-dir results/b8_hovernext_129741/interp/anotaciones
"""
from __future__ import annotations

import argparse
import json
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
for p in (str(REPO), CLAM_ENVIRON):
    if p not in sys.path:
        sys.path.insert(0, p)

from scripts.mammoth_interpretability import (  # noqa: E402
    load_feats_and_coords, get_wsi_thumbnail, build_overlay_rgba, blend, percentile_scores,
)
from scripts.clam_vs_mammoth_attention import build_arm, get_attention, infer_patch_size_level0  # noqa: E402

# colores por grupo de anotacion (los mismos rotulos que trae el CSV alineado)
COLOR_GRUPO = {
    "Mitosis": "#ff00ff",
    "Nucleos alto grado": "#00e5ff",
    "Tumor": "#ff2d2d",
    "necrosis": "#ffd400",
    "Immune cells": "#00ff66",
    "Stroma": "#ff9a3c",
    "Tejido Adiposo": "#b28dff",
    "Negative": "#bbbbbb",
}
GRUPOS_INTERES = ["Mitosis", "Nucleos alto grado"]


def parse_args():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--selection", required=True)
    ap.add_argument("--anotaciones", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--head", choices=["true", "pred"], default="true",
                    help="cabeza de clase a dibujar: 'true' (default) o 'pred'")
    ap.add_argument("--y-cut", type=int, default=49920,
                    help="frontera y entre las dos regiones de escaneo; 0 desactiva la figura confinada")
    ap.add_argument("--device", default="cpu")
    return ap.parse_args()


def match_patches(coords, ann, ps0):
    """Indice de parche del h5 -> lista de grupos anotados. Match EXACTO por (x,y).

    El CSV de anotaciones ya viene alineado al sistema de openslide con el offset validado
    (dx = 3829), y sus (x,y) son las coords del h5, asi que el match es exacto por par.
    Se verifica que efectivamente calcen: si el CSV viniera de otra corrida sin alinear,
    caerian 0 y la figura seria ruido con apariencia de senal.
    """
    idx = {(int(x), int(y)): i for i, (x, y) in enumerate(coords[:, :2])}
    out = {}
    perdidos = 0
    for r in ann.itertuples():
        key = (int(r.x), int(r.y))
        if key in idx:
            out.setdefault(idx[key], []).extend(str(r.clases).split("|"))
        else:
            perdidos += 1
    return out, perdidos


def draw_marks(ax, coords, por_parche, scale, ps0, lw=0.6):
    """Rectangulos de las marcas, coloreados por su PRIMER grupo."""
    side = max(1.0, ps0 * scale)
    vistos = set()
    for i, grupos in por_parche.items():
        g = grupos[0]
        c = COLOR_GRUPO.get(g, "#ffffff")
        ax.add_patch(Rectangle((coords[i, 0] * scale, coords[i, 1] * scale), side, side,
                               fill=False, edgecolor=c, linewidth=lw))
        vistos.add(g)
    handles = [plt.Line2D([], [], color=COLOR_GRUPO.get(g, "#fff"), lw=2, label=g)
               for g in sorted(vistos)]
    return handles


def panel(ax, thumb, coords, vals, scale, ps0, titulo, por_parche=None):
    ov = build_overlay_rgba(coords, percentile_scores(vals), scale, thumb.shape[1], thumb.shape[0], ps0)
    ax.imshow(blend(thumb, ov))
    h = draw_marks(ax, coords, por_parche, scale, ps0) if por_parche else []
    ax.set_title(titulo, fontsize=10)
    ax.set_axis_off()
    return h


def main():
    args = parse_args()
    out = Path(args.out_dir); out.mkdir(parents=True, exist_ok=True)
    sel = json.loads(Path(args.selection).read_text())
    ann_all = pd.read_csv(args.anotaciones)

    resumen = []
    for task, cfg in sel.items():
        n_classes = len(cfg["classes"])
        clam, _ = build_arm("clam", n_classes, cfg["ckpt_clam"], args.device)
        mam, _ = build_arm("clam_mammoth", n_classes, cfg["ckpt_mammoth"], args.device)

        for sl in cfg["slides"]:
            sid = sl["slide_id"]
            ann = ann_all[ann_all["slide_id"].astype(str) == str(sid)]
            if ann.empty:
                print(f"[skip] {sid}: sin filas en el CSV de anotaciones")
                continue

            feats, coords = load_feats_and_coords(sl["h5"])
            A_c, _, prob_c, yhat_c = get_attention(clam, feats, args.device)
            A_m, _, prob_m, yhat_m = get_attention(mam, feats, args.device)
            y_true = int(sl["y_true"])
            head_c = y_true if args.head == "true" else yhat_c
            head_m = y_true if args.head == "true" else yhat_m
            a_c, a_m = A_c[head_c], A_m[head_m]

            thumb, scale, _, _, _ = get_wsi_thumbnail(sl["wsi"])
            ps0 = infer_patch_size_level0(coords)
            por_parche, perdidos = match_patches(coords, ann, ps0)
            print(f"\n[{sid}] N={len(coords)} parches | marcas casadas={len(por_parche)} "
                  f"de {len(ann)} (perdidas={perdidos}) | ps0={ps0:.0f}px")
            print(f"   y_true={y_true}({cfg['classes'][y_true]}) "
                  f"CLAM pred={yhat_c} p={prob_c[yhat_c]:.3f} | Mammoth pred={yhat_m} p={prob_m[yhat_m]:.3f}"
                  f" | cabeza dibujada: {args.head} -> clam {head_c}, mammoth {head_m}")
            if perdidos:
                print(f"   AVISO: {perdidos} marcas no casaron con ningun parche del h5 "
                      f"(¿CSV sin alinear?)")

            # ---- figuras: lamina entera y, si corresponde, confinada a la region anotada ----
            vistas = [("lamina_entera", np.ones(len(coords), bool))]
            if args.y_cut:
                sel_reg = coords[:, 1] >= args.y_cut
                vistas.append(("region_anotada", sel_reg))

            for nombre, m in vistas:
                cc = coords[m]
                # reindexar el diccionario de marcas al subconjunto
                remap = {viejo: nuevo for nuevo, viejo in enumerate(np.flatnonzero(m))}
                pp = {remap[i]: g for i, g in por_parche.items() if i in remap}
                if nombre == "region_anotada":
                    y0 = cc[:, 1].min()
                    thumb_v = thumb[int(y0 * scale):, :]
                    cc_v = cc.copy(); cc_v[:, 1] -= y0
                else:
                    thumb_v, cc_v = thumb, cc

                th, tw = thumb_v.shape[:2]
                fig, axes = plt.subplots(1, 3, figsize=(3 * 5.0, 5.0 * th / tw + 0.9))
                axes[0].imshow(thumb_v); axes[0].set_axis_off()
                hs = draw_marks(axes[0], cc_v, pp, scale, ps0, lw=0.8)
                axes[0].set_title(f"marcas del patologo ({len(pp)} parches)", fontsize=10)
                panel(axes[1], thumb_v, cc_v, a_c[m], scale, ps0,
                      f"CLAM — atencion (cabeza '{cfg['classes'][head_c]}')", pp)
                panel(axes[2], thumb_v, cc_v, a_m[m], scale, ps0,
                      f"Mammoth — atencion (cabeza '{cfg['classes'][head_m]}')", pp)
                if hs:
                    axes[0].legend(handles=hs, loc="lower left", fontsize=6, framealpha=0.5)
                fig.suptitle(f"{sid} · {nombre.replace('_', ' ')} · "
                             f"y_true={cfg['classes'][y_true]}, ambos brazos predicen "
                             f"{cfg['classes'][yhat_c]}", fontsize=11)
                plt.tight_layout(rect=[0, 0, 1, 0.94])
                p = out / f"anotaciones_{sid}_{nombre}.png"
                plt.savefig(p, bbox_inches="tight", dpi=125); plt.close()
                print(f"   -> {p.relative_to(REPO) if str(p).startswith(str(REPO)) else p}")

            # ---- tabla: percentil medio de atencion por grupo, dentro de la region anotada ----
            reg = coords[:, 1] >= args.y_cut if args.y_cut else np.ones(len(coords), bool)
            for arm, a in (("CLAM", a_c), ("Mammoth", a_m)):
                pct = percentile_scores(a[reg])          # percentil DENTRO de la region anotada
                sub_idx = np.flatnonzero(reg)
                pos = {viejo: nuevo for nuevo, viejo in enumerate(sub_idx)}
                grupos = sorted({g for gs in por_parche.values() for g in gs})
                for g in grupos:
                    ii = [pos[i] for i, gs in por_parche.items() if g in gs and i in pos]
                    if not ii:
                        continue
                    resto = np.setdiff1d(np.arange(reg.sum()), np.array(ii))
                    resumen.append(dict(
                        slide=sid, brazo=arm, grupo=g, n_parches=len(ii),
                        percentil_medio=round(float(pct[ii].mean()), 4),
                        percentil_mediano=round(float(np.median(pct[ii])), 4),
                        percentil_medio_resto=round(float(pct[resto].mean()), 4),
                        interes=g in GRUPOS_INTERES))

    if resumen:
        df = pd.DataFrame(resumen).sort_values(["brazo", "percentil_medio"], ascending=[True, False])
        csv = out / "percentil_atencion_por_grupo.csv"
        df.to_csv(csv, index=False)
        print(f"\n[ok] {csv}")
        with pd.option_context("display.width", 170, "display.max_columns", 20):
            print("\n" + df.to_string(index=False))


if __name__ == "__main__":
    main()
