"""q1_slots_analisis.py — B8: ¿la dispersión de slots sigue al tamaño de lámina o a la tarea?

Segunda pregunta del encargo 1. Con n=7 la correlación con el número de parches daba
Spearman rho=0.750 (p=0.052), que **describe y no establece**, y encima se apoyaba en una
sola lámina chica. Con el barrido grande la pregunta pasa a ser testeable.

Lee `results/b8_q1_slots_escalado/q1_escalado_laminas.csv` (lo produce
`q1_slots_escalado.py`) y separa las dos explicaciones candidatas:

  * **tamaño**: Spearman de `n_eff_slots` contra `n_parches`, global y DENTRO de cada
    tarea. Dentro de tarea importa porque las tareas tienen mezclas distintas de cohorte
    y por lo tanto de tamaño: una correlación global podría ser efecto de tarea disfrazado.
  * **tarea**: fracción de varianza de `n_eff_slots` explicada por la tarea (eta cuadrado)
    y por la cohorte, contra la que explica el tamaño (rho al cuadrado de Spearman).

Sólo lectura de un CSV ya generado. CPU, segundos.
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np
from scipy.stats import kruskal, spearmanr

REPO = Path("/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto")


def eta2(grupos):
    """Fracción de la varianza total explicada por la partición en grupos."""
    todos = np.concatenate(grupos)
    media = todos.mean()
    entre = sum(len(g) * (g.mean() - media) ** 2 for g in grupos)
    total = ((todos - media) ** 2).sum()
    return float(entre / total) if total > 0 else float("nan")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=str(REPO / "results/b8_q1_slots_escalado/q1_escalado_laminas.csv"))
    args = ap.parse_args()

    filas = list(csv.DictReader(open(args.csv)))
    y = np.array([float(r["n_eff_slots"]) for r in filas])
    n = np.array([float(r["n_parches"]) for r in filas])
    task = np.array([r["task"] for r in filas])
    coh = np.array([r["cohorte"] for r in filas])

    print(f"n = {len(filas)} láminas-fold\n")

    print("== ¿sigue al TAMAÑO de la lámina? ==")
    rho, p = spearmanr(n, y)
    print(f"  global                       rho={rho:+.3f}  p={p:.2e}  rho²={rho**2:.3f}")
    for t in sorted(set(task)):
        m = task == t
        r_t, p_t = spearmanr(n[m], y[m])
        print(f"  dentro de {t[:38]:<40} rho={r_t:+.3f}  p={p_t:.2e}  (n={m.sum()})")
    for c in sorted(set(coh)):
        m = coh == c
        r_c, p_c = spearmanr(n[m], y[m])
        print(f"  dentro de cohorte {c:<32} rho={r_c:+.3f}  p={p_c:.2e}  (n={m.sum()})")

    print("\n== ¿sigue a la TAREA? ==")
    g_task = [y[task == t] for t in sorted(set(task))]
    h, p_k = kruskal(*g_task)
    print(f"  eta² tarea   = {eta2(g_task):.3f}   Kruskal-Wallis H={h:.1f}  p={p_k:.2e}")
    for t in sorted(set(task)):
        v = y[task == t]
        print(f"    {t[:44]:<46} {v.mean():6.1f} ± {v.std(ddof=1):4.1f}  (n={len(v)})")

    g_coh = [y[coh == c] for c in sorted(set(coh))]
    h_c, p_c = kruskal(*g_coh)
    print(f"  eta² cohorte = {eta2(g_coh):.3f}   Kruskal-Wallis H={h_c:.1f}  p={p_c:.2e}")
    for c in sorted(set(coh)):
        v = y[coh == c]
        print(f"    {c:<46} {v.mean():6.1f} ± {v.std(ddof=1):4.1f}  (n={len(v)})")

    print("\n== lectura ==")
    print(f"  varianza explicada: tamaño (rho²) {rho**2:.3f} · tarea {eta2(g_task):.3f} · "
          f"cohorte {eta2(g_coh):.3f}")
    print(f"  desviación estándar total: {y.std(ddof=1):.1f} slots sobre una media de {y.mean():.1f}")


if __name__ == "__main__":
    main()
