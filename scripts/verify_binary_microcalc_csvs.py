#!/usr/bin/env python3
"""verify_binary_microcalc_csvs.py — deriva y verifica los CSVs binarios de
microcalcificaciones (reformulación multi-label → 3 tareas binarias).

CONTEXTO
--------
La task `microcalcificaciones_pth` tiene 8 clases que NO son independientes:
son las 7 combinaciones no vacías de 3 tejidos {carcinoma_invasivo, cdis,
tejido_no_neoplasico} + `no_identificado`. Es un problema multi-etiqueta
aplastado en clases-combinación (ver
`sprints/B4_sprint4/objetivo_1_baseline/resultados.md`).

La reformulación correcta: 3 tareas binarias, una por tejido. El equipo de
Sebastián ya las implementó — los CSVs viven en `clam_environ/environ/csv/`
y las task configs están registradas en `main.py`. Este script NO los
re-crea: los **verifica**.

QUÉ HACE
--------
1. Re-deriva, de forma determinística, las etiquetas binarias desde el CSV
   de 8 clases (`dataset_microcalcificaciones_label.csv`).
2. Según `--no-identificado`:
   - `excluir`  : descarta las slides `no_identificado` (queda solo el
                  subconjunto con localización). Es la política con la que
                  el equipo construyó los CSVs existentes (333 slides).
   - `negativo` : trata `no_identificado` como negativo (`no`) en las 3
                  tareas (queda el dataset completo, ~3072 slides).
3. Si se pasa `--verify-against <dir>`, cross-chequea la derivación contra
   los CSVs ya existentes y reporta MATCH / MISMATCH por tarea.
4. Si se pasa `--out-dir <dir>`, escribe los 3 CSVs derivados (útil para la
   política `negativo`, que no tiene CSVs existentes en `clam_environ/`).

La derivación es 100 % determinística (parseo del nombre de la clase). El
script es CPU-only: no usa GPU, no usa red, no toca `clam_environ/`.

POLÍTICA `no_identificado` — PRECONDICIÓN SIN CERRAR
---------------------------------------------------
Qué significa `no_identificado` (¿"no hay microcalcificación" o "hay pero
sin ubicar"?) es una pregunta abierta para la reunión con Sebastián. Por eso
`--no-identificado` es **obligatorio**: obliga a elegir conscientemente. Los
CSVs existentes usan `excluir`.

USO
---
    # Verificar los CSVs existentes (política excluir):
    python scripts/verify_binary_microcalc_csvs.py \\
        --eight-class-csv /.../clam_environ/environ/csv/dataset_microcalcificaciones_label.csv \\
        --no-identificado excluir \\
        --verify-against  /.../clam_environ/environ/csv

    # Generar la variante `negativo` (no existe en clam_environ):
    python scripts/verify_binary_microcalc_csvs.py \\
        --eight-class-csv /.../dataset_microcalcificaciones_label.csv \\
        --no-identificado negativo \\
        --out-dir         sprints/B4_sprint4/reformulacion_multilabel/csv_negativo
"""
from __future__ import annotations

import argparse
import csv
import os
import sys

# Los 3 tejidos. Ninguno es substring de otro -> el parseo por token es seguro.
TISSUES = ["carcinoma_invasivo", "cdis", "tejido_no_neoplasico"]
NO_ID = "no_identificado"
POS, NEG = "si", "no"  # codificación de los CSVs existentes del equipo


def parse_label(label: str) -> set[str]:
    """Parsea el nombre de una clase de 8-clases al conjunto de tejidos
    presentes. Determinístico. Lanza ValueError si el formato no calza
    (defensa contra drift del CSV).

    Ejemplos:
      'no_identificado'                                  -> set()
      'en_cdis'                                          -> {'cdis'}
      'en_carcinoma_invasivo-en_cdis'                    -> {'carcinoma_invasivo','cdis'}
      'en_carcinoma_invasivo-en_cdis-en_tejido_no_neoplasico'
                                  -> {'carcinoma_invasivo','cdis','tejido_no_neoplasico'}
    """
    label = label.strip()
    if label == NO_ID:
        return set()
    tissues: set[str] = set()
    for token in label.split("-"):
        if not token.startswith("en_"):
            raise ValueError(f"token inesperado '{token}' en label '{label}'")
        tissue = token[len("en_"):]
        if tissue not in TISSUES:
            raise ValueError(f"tejido desconocido '{tissue}' en label '{label}'")
        tissues.add(tissue)
    return tissues


def derive(rows: list[dict], policy: str) -> dict[str, list[tuple[str, str, str]]]:
    """Deriva las 3 tablas binarias. Devuelve {tissue: [(case_id, slide_id,
    label), ...]}. `policy` ∈ {'excluir','negativo'}."""
    out: dict[str, list[tuple[str, str, str]]] = {t: [] for t in TISSUES}
    for r in rows:
        present = parse_label(r["label"])
        if not present and policy == "excluir":
            continue  # slide no_identificado -> se descarta
        for t in TISSUES:
            out[t].append((r["case_id"], r["slide_id"], POS if t in present else NEG))
    return out


def load_label_csv(path: str) -> dict[str, str]:
    """Carga un CSV `case_id,slide_id,label` como dict slide_id -> label."""
    d: dict[str, str] = {}
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            d[r["slide_id"]] = r["label"].strip()
    return d


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--eight-class-csv", required=True,
                    help="path al dataset_microcalcificaciones_label.csv (8 clases)")
    ap.add_argument("--no-identificado", required=True, choices=["excluir", "negativo"],
                    help="política para las slides no_identificado (PRECONDICIÓN: ver docstring)")
    ap.add_argument("--verify-against", default=None,
                    help="directorio con los CSVs binarios existentes a cross-chequear")
    ap.add_argument("--out-dir", default=None,
                    help="si se da, escribe los 3 CSVs derivados ahí")
    args = ap.parse_args()

    if not os.path.isfile(args.eight_class_csv):
        print(f"ERROR: no existe {args.eight_class_csv}", file=sys.stderr)
        return 1

    with open(args.eight_class_csv, newline="") as f:
        rows = list(csv.DictReader(f))
    for col in ("case_id", "slide_id", "label"):
        if col not in rows[0]:
            print(f"ERROR: el CSV de 8 clases no tiene columna '{col}'", file=sys.stderr)
            return 1

    print(f"CSV de 8 clases: {args.eight_class_csv}")
    print(f"  filas: {len(rows)}")
    print(f"política no_identificado: {args.no_identificado}\n")

    try:
        derived = derive(rows, args.no_identificado)
    except ValueError as e:
        print(f"ERROR de parseo (¿drift del CSV?): {e}", file=sys.stderr)
        return 1

    # Resumen de la derivación.
    print("derivación binaria:")
    for t in TISSUES:
        labs = [lab for _, _, lab in derived[t]]
        n, npos = len(labs), labs.count(POS)
        print(f"  {t:24s}  filas {n:5d}  | si {npos:4d}  no {n - npos:4d}  "
              f"| positivos {100 * npos / n:.1f}%")
    print()

    rc = 0

    # Cross-check contra los CSVs existentes.
    if args.verify_against:
        print(f"cross-check contra: {args.verify_against}")
        for t in TISSUES:
            existing_path = os.path.join(
                args.verify_against, f"dataset_microcalcificaciones_en_{t}_label.csv")
            if not os.path.isfile(existing_path):
                print(f"  {t:24s}  AVISO: no existe {existing_path}")
                rc = 1
                continue
            existing = load_label_csv(existing_path)
            mine = {sid: lab for _, sid, lab in derived[t]}
            only_mine = set(mine) - set(existing)
            only_exist = set(existing) - set(mine)
            disagree = [s for s in (set(mine) & set(existing)) if mine[s] != existing[s]]
            if not only_mine and not only_exist and not disagree:
                print(f"  {t:24s}  MATCH  ({len(mine)} slides, etiquetas idénticas)")
            else:
                rc = 1
                print(f"  {t:24s}  MISMATCH")
                print(f"      solo en mi derivación: {len(only_mine)}")
                print(f"      solo en el CSV existente: {len(only_exist)}")
                print(f"      etiqueta distinta: {len(disagree)}")
                for s in disagree[:5]:
                    print(f"        {s}: derivado={mine[s]} existente={existing[s]}")
        print()

    # Escritura opcional.
    if args.out_dir:
        os.makedirs(args.out_dir, exist_ok=True)
        for t in TISSUES:
            out_path = os.path.join(
                args.out_dir, f"dataset_microcalcificaciones_en_{t}_label.csv")
            with open(out_path, "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(["case_id", "slide_id", "label"])
                w.writerows(derived[t])
            print(f"escrito: {out_path}")

    if args.verify_against and rc == 0:
        print("RESULTADO: los CSVs existentes coinciden con la derivación determinística.")
    elif args.verify_against:
        print("RESULTADO: hay discrepancias — revisar arriba.")
    return rc


if __name__ == "__main__":
    sys.exit(main())
