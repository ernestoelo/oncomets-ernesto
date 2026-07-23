"""slot_cota_softmax.py — cota sobre la softmax por slot: cuantos slots aportan (B7).

Encargo de Sebastian (reunion 23-jul, §4 de `reunion_23jul_acuerdos.md`): definir una cota
conveniente sobre la 2a softmax para decidir que slots ya no aportan practicamente nada, y
con eso dar una idea de cuantos slots requiere aproximadamente cada tarea.

POR QUE POR LAMINA Y NO POR TAREA: promediar los pesos de laminas distintas SUBE la entropia
y aplana la cola (N_eff de tarea 199 vs ~161 por lamina en tipo). El objeto medible es la
lamina; la tarea se reporta como RANGO entre sus laminas, nunca como una distribucion
promediada. Mismo criterio que se uso para citar N_eff ([[mammoth-slot-routing-weight]]).

LA COTA ELEGIDA es el reparto uniforme, 1/300 = 0.333 %. Es el unico corte sin parametro
libre (igual que `N_eff = exp(H)`): un slot que recibe MENOS que el uniforme no concentra
nada, recibe menos de lo que le tocaria si el ruteo fuera ciego. Cortes a ojo dan de 25 a
300 slots segun donde se pongan (§5.2 de `resultados_interpretabilidad.md`), por eso hay
que justificar la cota y no elegirla a mano.

CPU, post-hoc, read-only sobre los `slot_usage.csv` + `attention_stats.json` ya existentes.
NO toca modelo ni training (regla 9 no aplica).

Salida: sprints/B7_sprint7/slot_softmax/slot_cota_por_lamina.csv

Uso:
  /home/sdonoso/miniconda3/envs/clam_latest/bin/python scripts/slot_cota_softmax.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path("/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto")
INTERP = REPO / "results/b7_mammoth_interp/interpretabilidad"
OUT = REPO / "sprints/B7_sprint7/slot_softmax"
UNIFORM = 1.0 / 300.0  # 0.3333 % — la cota

TASK_LABEL = {
    "tipo_histologico_3clases_ci": "tipo_histologico",
    "carcinoma_ductal_insitu_presente_ci_reform": "cdis",
    "invasion_linfatica_vascular_ci_reform": "lvi",
}


def n_eff(p):
    """Numero efectivo de slots = exp(entropia). n si uniforme, 1 si colapsa en uno."""
    p = np.clip(np.asarray(p, float), 1e-15, 1.0)
    p = p / p.sum()
    return float(np.exp(-(p * np.log(p)).sum()))


def main():
    filas = []
    for task_key, label in TASK_LABEL.items():
        for csv in sorted((INTERP / task_key).glob("*/expertos/slot_usage.csv")):
            slide_dir = csv.parent.parent
            # meta.json = marcador FINAL del driver reanudable: sin el, la lamina puede
            # estar a medio escribir (mismo filtro que answer_q1, fix f0d043e)
            if not (slide_dir / "expertos" / "meta.json").exists():
                print(f"  [skip] sin meta.json: {slide_dir.name}")
                continue
            stats = json.loads((slide_dir / "attention_stats.json").read_text())
            w = pd.read_csv(csv)["mean_combine_weight"].to_numpy(float)
            p = np.sort(w / w.sum())[::-1]
            cum = np.cumsum(p)

            sobre = int((p >= UNIFORM).sum())
            filas.append({
                "tarea": label,
                "lamina": slide_dir.name.split("-01Z")[0],
                "parches": stats["n_patches"],
                "N_eff": round(n_eff(p), 1),
                "slots_sobre_uniforme": sobre,
                "masa_de_esos_pct": round(100 * cum[sobre - 1], 1),
                "slots_50pct": int(np.searchsorted(cum, 0.50) + 1),
                "slots_90pct": int(np.searchsorted(cum, 0.90) + 1),
                "top1_pct": round(100 * p[0], 2),
                "min_vs_uniforme": round(p[-1] / UNIFORM, 4),
            })

    df = pd.DataFrame(filas).sort_values(["tarea", "parches"]).reset_index(drop=True)
    out_csv = OUT / "slot_cota_por_lamina.csv"
    df.to_csv(out_csv, index=False)

    with pd.option_context("display.width", 200, "display.max_columns", 20):
        print(df.to_string(index=False))

    print("\n=== rango por tarea (cota = uniforme 1/300 = 0.333 %) ===")
    for t, g in df.groupby("tarea", sort=False):
        s = g["slots_sobre_uniforme"]
        print(f"{t:>17}: {s.min()}–{s.max()} slots sobre la cota "
              f"(media {s.mean():.0f}), concentran {g['masa_de_esos_pct'].min():.0f}–"
              f"{g['masa_de_esos_pct'].max():.0f} % del peso · N_eff "
              f"{g['N_eff'].min():.0f}–{g['N_eff'].max():.0f}")

    s = df["slots_sobre_uniforme"]
    print(f"\nGLOBAL (7 laminas): {s.min()}–{s.max()} slots sobre la cota, media {s.mean():.0f} "
          f"(= {100 * s.mean() / 300:.0f} % de los 300); concentran "
          f"{df['masa_de_esos_pct'].mean():.0f} % del peso de media.")
    print(f"El slot mas chico recibe {df['min_vs_uniforme'].min():.4f}× a "
          f"{df['min_vs_uniforme'].max():.4f}× el uniforme (o sea, entre "
          f"{1 / df['min_vs_uniforme'].max():.0f}× y {1 / df['min_vs_uniforme'].min():.0f}× MENOS).")
    print(f"\n[ok] {out_csv.relative_to(REPO)}")


if __name__ == "__main__":
    main()
