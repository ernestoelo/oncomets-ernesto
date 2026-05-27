#!/usr/bin/env python
"""gate_no_colapso.py — guardrail pre-registrado de Fase 2 (Objetivo 5).

Lee los test_metrics.json de los folds de Fase 1 (CLAM sobre el fusionado),
computa el balanced_acc medio y decide si vale la pena correr Fase 2 (DSMIL):

- mean(balanced_acc) >= THRESHOLD  → exit 0  (proceder con Fase 2).
- mean(balanced_acc) <  THRESHOLD  → exit 1  (COLAPSO: no correr Fase 2;
  comparar arquitecturas sobre una task degenerada es quemar GPU).
- no hay resultados de Fase 1        → exit 2  (Fase 1 falló/no corrió).

Umbral = 0.55 (hipotesis.md §1.3: "colapso a mayoritaria = balanced_acc < 0.55").

Uso (desde el .slurm de Fase 2, idiom `if ! ... ; then exit 0; fi`):
    PY=/home/sdonoso/miniconda3/envs/clam_latest/bin/python
    $PY scripts/gate_no_colapso.py \
        --results_glob 'results/obj5_fase1_clam_fusionado/clam_presencia_f*_s1' \
        --threshold 0.55
"""
import argparse
import glob
import json
import os
import sys


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--results_glob", required=True,
                    help="glob de los dirs de fold de Fase 1 (cada uno con test_metrics.json)")
    ap.add_argument("--threshold", type=float, default=0.55,
                    help="umbral de colapso de balanced_acc (default 0.55)")
    ap.add_argument("--metric", default="balanced_acc")
    ap.add_argument("--expected_folds", type=int, default=0,
                    help="si >0, exige exactamente N folds con test_metrics.json; "
                         "si faltan (Fase 1 parcial/crasheada) → exit 2 (skip Fase 2)")
    args = ap.parse_args()

    dirs = sorted(glob.glob(args.results_glob))
    vals = []
    for d in dirs:
        f = os.path.join(d, "test_metrics.json")
        if not os.path.isfile(f):
            continue
        with open(f) as fh:
            m = json.load(fh)
        v = m.get(args.metric)
        if v is not None and v == v:  # no None, no NaN
            vals.append(float(v))
            print(f"  {os.path.basename(d)}: {args.metric}={v:.4f}")

    if not vals:
        print(f"GATE: ✗ sin resultados de Fase 1 en '{args.results_glob}' "
              f"(Fase 1 falló o no corrió). NO se corre Fase 2.", file=sys.stderr)
        sys.exit(2)

    if args.expected_folds > 0 and len(vals) != args.expected_folds:
        print(f"GATE: ✗ Fase 1 incompleta: {len(vals)} folds con {args.metric} "
              f"de {args.expected_folds} esperados (crash parcial). NO se corre "
              f"Fase 2 — promediar sobre folds parciales sesga el guardrail.",
              file=sys.stderr)
        sys.exit(2)

    mean = sum(vals) / len(vals)
    print(f"GATE: mean({args.metric}) sobre {len(vals)} folds = {mean:.4f}  "
          f"(umbral colapso {args.threshold})")
    if mean < args.threshold:
        print(f"GATE: ✗ COLAPSO (mean {mean:.4f} < {args.threshold}). "
              f"El fusionado no es aprendible ni con CLAM → NO se corre Fase 2 "
              f"(guardrail hipotesis.md §1.3).", file=sys.stderr)
        sys.exit(1)
    print(f"GATE: ✓ Fase 1 no colapsó (mean {mean:.4f} >= {args.threshold}). "
          f"Proceder con Fase 2 (DSMIL).")
    sys.exit(0)


if __name__ == "__main__":
    main()
