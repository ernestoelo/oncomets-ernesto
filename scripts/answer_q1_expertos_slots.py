"""answer_q1_expertos_slots.py — Q1 del Sprint 7: "cuantos expertos/slots usa Mammoth?".

Agrega los `slot_usage.csv` y `expert_usage.csv` que produce mammoth_interpretability.py
sobre las slides del sprint y responde con numeros, no con impresiones.

Que se mide (y por que):
  - "peso por slot" = `combine_weights`, la 2a softmax sobre los E*S=300 slots
    (mammoth.py:411) — NO el top-k de parches por experto, que es otra cosa
    ([[mammoth-slot-routing-weight]]). No reportarlo como "top-k".
  - **Numero efectivo** = exp(entropia de la distribucion de pesos). Si el ruteo fuera
    uniforme sobre los 300 slots daria 300; si colapsara en uno, daria 1. Es la lectura
    honesta de "cuantos se usan de verdad", porque *todos* los slots reciben peso > 0
    (es una softmax): contar "los que tienen peso no nulo" siempre daria 300.
  - **Masa acumulada**: cuantos slots hacen falta para juntar el 50% y el 90% del peso.
  - **Sobre-uniforme**: cuantos superan el peso uniforme 1/300 (o 1/30 para expertos).

Etapa 0: CPU, solo lectura de artefactos ya generados.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np

REPO = Path("/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto")


def numero_efectivo(w):
    """exp(H) con H la entropia de Shannon de w normalizado. Unidades = 'nº de items'."""
    p = np.clip(np.asarray(w, dtype=np.float64), 1e-300, None)
    p = p / p.sum()
    return float(np.exp(-(p * np.log(p)).sum()))


def masa_acumulada(w, frac):
    p = np.sort(np.asarray(w, dtype=np.float64))[::-1]
    p = p / p.sum()
    return int(np.searchsorted(np.cumsum(p), frac) + 1)


def leer_slots(path):
    e, s, w = [], [], []
    with open(path) as fh:
        for row in csv.DictReader(fh):
            e.append(int(row["expert"])); s.append(int(row["slot"]))
            w.append(float(row["mean_combine_weight"]))
    return np.array(e), np.array(s), np.array(w)


def leer_expertos(path):
    idx, w = [], []
    with open(path) as fh:
        for row in csv.DictReader(fh):
            idx.append(int(row["expert"])); w.append(float(row["mean_score"]))
    return np.array(idx), np.array(w)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(REPO / "results/b7_mammoth_interp/interpretabilidad"))
    ap.add_argument("--out", default=str(REPO / "sprints/B7_sprint7/respuesta_q1_expertos_slots.md"))
    args = ap.parse_args()

    root = Path(args.root)
    # `meta.json` se escribe AL FINAL de cada lamina; `slot_usage.csv` es intermedio.
    # Filtrar por el marcador final evita promediar una lamina en vuelo (CSV a medio
    # escribir) o de una corrida que crasheo, que entrarian sin aviso (workaround J).
    todos = sorted(root.glob("*/*/expertos/slot_usage.csv"))
    slot_files = [sf for sf in todos if (sf.parent / "meta.json").exists()]
    if not slot_files:
        raise SystemExit(f"Sin laminas completas bajo {root} — corre antes run_b7_expert_interp.sh")
    if len(todos) > len(slot_files):
        parciales = [sf.parent.parent.name for sf in todos if sf not in slot_files]
        print(f"[aviso] {len(todos) - len(slot_files)} lamina(s) sin meta.json (en vuelo o "
              f"incompletas), EXCLUIDAS: {', '.join(parciales)}\n")

    filas, por_tarea = [], {}
    for sf in slot_files:
        slide = sf.parent.parent.name
        task = sf.parent.parent.parent.name
        e, s, w = leer_slots(sf)
        ef = sf.parent / "expert_usage.csv"
        ei, ew = leer_expertos(ef) if ef.exists() else (np.array([]), np.array([]))
        E, S = (int(e.max()) + 1, int(s.max()) + 1)
        rec = dict(
            task=task, slide=slide, n_slots=len(w), n_expertos=len(ew) or E,
            slots_efectivos=numero_efectivo(w),
            slots_50=masa_acumulada(w, 0.50), slots_90=masa_acumulada(w, 0.90),
            slots_sobre_uniforme=int((w > 1.0 / len(w)).sum()),
            expertos_efectivos=numero_efectivo(ew) if len(ew) else None,
            expertos_50=masa_acumulada(ew, 0.50) if len(ew) else None,
            expertos_90=masa_acumulada(ew, 0.90) if len(ew) else None,
            expertos_sobre_uniforme=int((ew > 1.0 / len(ew)).sum()) if len(ew) else None,
            top5_slots=[f"e{int(e[i])}·s{int(s[i])}" for i in np.argsort(w)[::-1][:5]],
            top5_expertos=[int(ei[i]) for i in np.argsort(ew)[::-1][:5]] if len(ew) else [],
        )
        filas.append(rec)
        por_tarea.setdefault(task, []).append(rec)

    print(f"{'tarea':<44}{'slide':<26}{'slots ef.':>10}{'s50':>5}{'s90':>5}"
          f"{'exp ef.':>9}{'e50':>5}{'e90':>5}")
    print("-" * 110)
    for r in filas:
        print(f"{r['task'][:42]:<44}{r['slide'][:24]:<26}{r['slots_efectivos']:>10.1f}"
              f"{r['slots_50']:>5}{r['slots_90']:>5}"
              f"{(r['expertos_efectivos'] or 0):>9.1f}{r['expertos_50'] or 0:>5}"
              f"{r['expertos_90'] or 0:>5}")

    tot_s = np.mean([r["slots_efectivos"] for r in filas])
    tot_e = np.mean([r["expertos_efectivos"] for r in filas if r["expertos_efectivos"]])
    n_slots = filas[0]["n_slots"]; n_exp = filas[0]["n_expertos"]
    print(f"\nMEDIA sobre {len(filas)} slides: slots efectivos {tot_s:.1f} de {n_slots} · "
          f"expertos efectivos {tot_e:.1f} de {n_exp}")

    L = ["# Q1 — ¿cuántos expertos/slots usa Mammoth? (Sprint 7)", "",
         "«Peso por slot» = `combine_weights`, la segunda softmax sobre los "
         f"E·S={n_slots} slots (`mammoth.py:411`). No es el top-k de parches por experto.",
         "",
         "**Número efectivo** = exp(entropía de la distribución de pesos): sería "
         f"{n_slots} si el ruteo fuera perfectamente uniforme y 1 si colapsara en un "
         "solo slot. Se usa esta medida porque la softmax da peso positivo a todos los "
         "slots, así que contar «los que reciben algo» siempre daría el total.", "",
         f"## Respuesta corta", "",
         f"- Slots efectivos: **{tot_s:.1f} de {n_slots}**",
         f"- Expertos efectivos: **{tot_e:.1f} de {n_exp}**", "",
         "## Por slide", "",
         "| Tarea | Slide | Slots efect. | Slots p/50% | Slots p/90% | Expertos efect. | "
         "Expertos p/50% | Expertos p/90% | Top-5 slots |", "|---|---|---|---|---|---|---|---|---|"]
    for r in filas:
        L.append(f"| {r['task']} | `{r['slide']}` | {r['slots_efectivos']:.1f} | "
                 f"{r['slots_50']} | {r['slots_90']} | "
                 f"{(r['expertos_efectivos'] or 0):.1f} | {r['expertos_50']} | "
                 f"{r['expertos_90']} | {', '.join(r['top5_slots'])} |")
    L.append("")
    Path(args.out).write_text("\n".join(L))
    Path(args.out).with_suffix(".json").write_text(json.dumps(filas, indent=2))
    print(f"\nEscrito: {args.out}")


if __name__ == "__main__":
    main()
