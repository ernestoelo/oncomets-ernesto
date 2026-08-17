"""build_slot_softmax_tables.py — tabla de la softmax de ruteo por slot, por TAREA (B7).

Para mostrarle a Sebastian, LITERALMENTE, la 2a softmax de Mammoth (`combine_weights`)
sobre los E*S=300 slots: cuanto se parece cada parche a cada slot, promediado sobre los
parches de la lamina y sobre las laminas de la tarea. Deja ver que la mayoria de los 300
slots pesan ~0 (basura numerica de la softmax) y cuales concentran el ruteo.

Lee los `slot_usage.csv` que ya produjo `scripts/mammoth_interpretability.py` (post-hoc,
CPU). NO toca modelo ni training (regla 9 no aplica). Cada slot_usage.csv trae los 300
slots con `mean_combine_weight` (promedio del peso softmax sobre los parches de esa
lamina), y suma 1 por lamina (verificado).

Agregacion por TAREA: promedio simple del peso entre las laminas de la tarea, re-normalizado
a 100%. Simple y no ponderado por nº de parches para que una lamina grande no domine el
"slot tipico de la tarea"; se incluyen las columnas por-lamina para ver que la historia no
cambia. El slot ES el mismo objeto dentro de una tarea (mismo checkpoint Mammoth, fold 0);
entre tareas NO (checkpoints distintos) -> por eso una tabla POR TAREA, nunca una global.

Salida (sprints/B7_sprint7/slot_softmax/):
  - slot_softmax_<tarea>.csv : 300 slots ordenados por peso de la tarea
  - slot_softmax_resumen.csv : una fila por tarea (N_eff, cuantos ~0, masa del top, etc.)

Uso (B7, defaults — reproduce la corrida original):
  /home/sdonoso/miniconda3/envs/clam_latest/bin/python scripts/build_slot_softmax_tables.py

Uso (un slot_usage.csv suelto, fuera del layout B7 — p.ej. la 129741 del B8):
  ... scripts/build_slot_softmax_tables.py \
      --slot-usage results/b8_hovernext_129741/interp/expertos/slot_usage.csv \
      --label 129741 --out sprints/B8_sprint8/hovernext_129741/slot_softmax

PARAMETRIZADO el 17-ago-2026 (B8): antes clavaba `INTERP`/`OUT`/`TASK_LABEL` a las 3 tareas
del B7 y exigia el layout `<task>/<slide>/expertos/slot_usage.csv`. Ademas `UNIFORM` estaba
fijo en 1/300: ahora sale del nº real de slots del CSV, porque un checkpoint del grid E×S
(fase 6) tiene otro total y la cota uniforme mentiria. Los defaults preservan el B7.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path("/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto")

TASK_LABEL_B7 = {
    "tipo_histologico_3clases_ci": "tipo_histologico",
    "carcinoma_ductal_insitu_presente_ci_reform": "cdis",
    "invasion_linfatica_vascular_ci_reform": "lvi",
}


def parse_args():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--interp-root", default=str(REPO / "results/b7_mammoth_interp/interpretabilidad"),
                    help="raiz con <task>/<slide>/expertos/slot_usage.csv")
    ap.add_argument("--out", default=str(REPO / "sprints/B7_sprint7/slot_softmax"),
                    help="directorio de salida")
    ap.add_argument("--slot-usage", nargs="+", default=None,
                    help="rutas EXPLICITAS a slot_usage.csv; puentea --interp-root y su layout")
    ap.add_argument("--label", default=None,
                    help="etiqueta del grupo cuando se usa --slot-usage (default: 'slides')")
    ap.add_argument("--only-task", default=None, help="procesar solo esta tarea")
    return ap.parse_args()


def rel(p: Path):
    """Path relativo al repo si esta adentro; absoluto si no (el --out puede caer afuera)."""
    try:
        return p.relative_to(REPO)
    except ValueError:
        return p


def n_eff(p):
    """Numero efectivo de slots = exp(entropia). 300 si uniforme, 1 si colapsa en uno."""
    p = np.clip(np.asarray(p, float), 1e-15, 1.0)
    p = p / p.sum()
    return float(np.exp(-(p * np.log(p)).sum()))


def load_csvs(csvs):
    """Devuelve {slide_short: serie de pesos indexada por 'e{e}s{s}'}.

    El nombre de lamina sale del dir <slide>/expertos/; el `split("-01Z")` solo acorta los
    UUID largos de TCGA y es no-op en un ID privado como `129741`.
    """
    out = {}
    for csv in sorted(csvs):
        csv = Path(csv)
        slide = csv.parent.parent.name.split("-01Z")[0]
        df = pd.read_csv(csv)
        idx = [f"e{int(e)}s{int(s)}" for e, s in zip(df["expert"], df["slot"])]
        out[slide] = pd.Series(df["mean_combine_weight"].to_numpy(float), index=idx)
    return out


def load_task(task_dir: Path):
    return load_csvs(task_dir.glob("*/expertos/slot_usage.csv"))


def main():
    args = parse_args()
    OUT = Path(args.out)
    OUT.mkdir(parents=True, exist_ok=True)
    resumen = []

    if args.slot_usage:
        grupos = [(args.label or "slides", load_csvs(args.slot_usage))]
    else:
        grupos = [(lab, load_task(Path(args.interp_root) / tk))
                  for tk, lab in TASK_LABEL_B7.items()
                  if not args.only_task or tk == args.only_task]

    for label, slides in grupos:
        if not slides:
            print(f"  [skip] sin slot_usage.csv para {label}")
            continue

        mat = pd.DataFrame(slides)                     # n_slots x n_slides
        # cota del reparto uniforme derivada del nº REAL de slots, no clavada en 1/300
        UNIFORM = 1.0 / len(mat)
        avg = mat.mean(axis=1)                         # promedio simple entre laminas
        avg = avg / avg.sum()                          # re-normaliza a 100%

        order = avg.sort_values(ascending=False).index
        avg = avg[order]
        mat = mat.loc[order]

        pct = avg * 100.0
        cum = pct.cumsum()
        exp, slot = zip(*[(int(i[1:].split("s")[0]), int(i.split("s")[1])) for i in order])

        tab = pd.DataFrame({
            "rank": np.arange(1, len(order) + 1),
            "experto": exp,
            "slot": slot,
            "id": [f"e{e}·s{s}" for e, s in zip(exp, slot)],
            "peso_pct": pct.round(4).values,
            "vs_uniforme": (avg / UNIFORM).round(3).values,   # >1 = por encima del reparto igual
            "masa_acum_pct": cum.round(2).values,
            "sobre_uniforme": np.where(avg.values >= UNIFORM, "si", "no (≈0)"),
            "en_top_90pct": np.where(cum.values <= 90.0, "si", "no"),
        })
        # peso por lamina (transparencia: mismo slot, distinta lamina de la tarea)
        for sl in mat.columns:
            tab[f"pct_{sl}"] = (mat[sl] / mat[sl].sum() * 100).round(4).values

        out_csv = OUT / f"slot_softmax_{label}.csv"
        tab.to_csv(out_csv, index=False)
        print(f"[ok] {rel(out_csv)}  ({len(tab)} slots, {len(mat.columns)} laminas)")
        # NOTA: la tabla MINIMALISTA (top-12 + resto) se emite POR LAMINA en
        # scripts/slot_heatmaps_contraste.py (slot_mini_<tarea>.csv), para que calce 1:1
        # con los heatmaps. El promedio por tarea aplana la distribucion (sube la entropia)
        # y transmite peor el "slots casi cero" -> no se emite mini a nivel tarea.

        # ---- resumen de la tarea ----
        p = avg.values
        cumv = np.cumsum(np.sort(p)[::-1])
        neff_slides = [n_eff(mat[sl].values) for sl in mat.columns]
        resumen.append({
            "tarea": label,
            "laminas": len(mat.columns),
            "N_eff_slots": round(n_eff(p), 1),
            "N_eff_por_lamina": " / ".join(f"{v:.0f}" for v in neff_slides),
            "slots_sobre_uniforme": int((p >= UNIFORM).sum()),
            "slots_bajo_uniforme_≈0": int((p < UNIFORM).sum()),
            "slots_para_50pct": int(np.searchsorted(cumv, 0.50) + 1),
            "slots_para_90pct": int(np.searchsorted(cumv, 0.90) + 1),
            "masa_top10_pct": round(100 * cumv[9], 1),
            "top1_id": tab.loc[0, "id"],
            "top1_pct": tab.loc[0, "peso_pct"],
            "top1_vs_uniforme": tab.loc[0, "vs_uniforme"],
            "peso_min_pct": round(100 * p.min(), 5),
        })

    if resumen:
        res = pd.DataFrame(resumen)
        res_csv = OUT / "slot_softmax_resumen.csv"
        res.to_csv(res_csv, index=False)
        print(f"\n[ok] {rel(res_csv)}")
        with pd.option_context("display.width", 160, "display.max_columns", 20):
            print("\n" + res.to_string(index=False))


if __name__ == "__main__":
    main()
