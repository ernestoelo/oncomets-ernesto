#!/usr/bin/env python
"""build_fusion_csv.py — construye el CSV del binario fusionado "tiene/no tiene
microcalcificaciones" (Objetivo 5, Fase 1).

Regla determinística (hipotesis.md §1.2), leyendo READ-ONLY el CSV 8-clases de
Sebastián y escribiendo SOLO bajo clam_testing2/:

    label_fused = "no"  si  label == "no_identificado"
    label_fused = "si"  en cualquier otro caso (cualquier tejido / combinación)

Uso:
    PY=/home/sdonoso/miniconda3/envs/clam_latest/bin/python
    $PY scripts/build_fusion_csv.py
"""
import os
import sys
import pandas as pd

SRC = "/media/administrador/Storage1/sdonoso/clam_environ/environ/csv/dataset_microcalcificaciones_label.csv"
FEATS = "/media/administrador/Storage1/sdonoso/clam_environ/environ/features/pt_files"
OUT_DIR = "/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/data/csv_fusion"
OUT = os.path.join(OUT_DIR, "dataset_microcalcificaciones_presencia_label.csv")

NEG_LABEL = "no_identificado"


def main():
    df = pd.read_csv(SRC)
    assert {"case_id", "slide_id", "label"}.issubset(df.columns), f"cols inesperadas: {list(df.columns)}"
    n_raw = len(df)

    # Filtrar slides sin features CONCH (.pt): el dataloader las saltaría
    # (return None) → test-n no determinístico. Mejor excluirlas explícito.
    # Consistente con Fase 0 (las 328 identificadas todas tienen .pt).
    pt_ids = {f[:-3] for f in os.listdir(FEATS) if f.endswith(".pt")}
    has_pt = df["slide_id"].astype(str).isin(pt_ids)
    dropped = df.loc[~has_pt, ["slide_id", "label"]]
    if len(dropped):
        print(f"[FILTRO] {len(dropped)} slide(s) sin .pt excluida(s):")
        for _, r in dropped.iterrows():
            print(f"    {r['slide_id']}  (label original: {r['label']})")
    df = df.loc[has_pt].reset_index(drop=True)
    n_in = len(df)

    orig = df["label"].astype(str)
    df["label"] = orig.apply(lambda x: "no" if x == NEG_LABEL else "si")

    n_neg = int((df["label"] == "no").sum())
    n_pos = int((df["label"] == "si").sum())
    assert n_neg + n_pos == n_in, "conteo inconsistente"
    assert n_neg == int((orig == NEG_LABEL).sum()), "negativos != no_identificado"

    os.makedirs(OUT_DIR, exist_ok=True)
    df[["case_id", "slide_id", "label"]].to_csv(OUT, index=False)

    ratio = n_neg / n_pos if n_pos else float("inf")
    print(f"Fuente (READ-ONLY): {SRC}")
    print(f"  filas crudas: {n_raw}  ->  con .pt: {n_in}  (excluidas {n_raw - n_in})")
    print(f"Salida: {OUT}")
    print(f"  positivos (si, cualquier tejido): {n_pos}")
    print(f"  negativos (no, == no_identificado): {n_neg}")
    print(f"  ratio neg:pos = {ratio:.2f}:1  ({'CUMPLE' if ratio <= 10 else 'EXCEDE'} cap 10x de Sebastián)")
    # breakdown de positivos por etiqueta original (trazabilidad)
    print("  breakdown positivos (label original):")
    for lab, n in orig[orig != NEG_LABEL].value_counts().items():
        print(f"    {lab}: {n}")
    sys.exit(0)


if __name__ == "__main__":
    main()
