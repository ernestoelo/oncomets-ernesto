#!/usr/bin/env python
"""Verificador determinístico de los k-fold splits del Objetivo 5 (Fase 0).

Smoke test #1 de `sprints/B4_sprint4/objetivo_5_fusion_binaria/hipotesis.md`.
Read-only sobre `clam_environ/`; no escribe nada.

Para cada tarea binaria y cada fold valida:
  1. train / val / test son disjuntos dentro del fold.
  2. el total (train+val+test) es constante entre folds (= identificadas).
  3. los conteos por clase (join con el label CSV) son coherentes.
  4. cada slide_id de cada fold tiene su `.pt` en features/pt_files/.

Uso:
  PY=/home/sdonoso/miniconda3/envs/clam_latest/bin/python
  $PY scripts/verify_kfold_splits.py
Sale con código != 0 si alguna invariante falla (apto para preflight).
"""
import glob
import os
import sys
import pandas as pd

REPO = "/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto"
ENVIRON = "/media/administrador/Storage1/sdonoso/clam_environ/environ"
SPLITS_BASE = os.path.join(REPO, "data", "splits_kfold")
FEATS = os.path.join(ENVIRON, "features", "pt_files")

# split_dir_name (bajo data/splits_kfold/) -> CSV de labels (path completo).
# Las 3 binarias leen los CSV read-only de Sebastián; la fusionada lee el CSV
# propio bajo clam_testing2/.
_C = os.path.join(ENVIRON, "csv")
_F = os.path.join(REPO, "data", "csv_fusion")
TASKS = {
    "microcalcificaciones_en_carcinoma_invasivo_pth_100":
        os.path.join(_C, "dataset_microcalcificaciones_en_carcinoma_invasivo_label.csv"),
    "microcalcificaciones_en_cdis_pth_100":
        os.path.join(_C, "dataset_microcalcificaciones_en_cdis_label.csv"),
    "microcalcificaciones_en_tejido_no_neoplasico_pth_100":
        os.path.join(_C, "dataset_microcalcificaciones_en_tejido_no_neoplasico_label.csv"),
    "microcalcificaciones_presencia_100":
        os.path.join(_F, "dataset_microcalcificaciones_presencia_label.csv"),
}


def load_fold(split_dir, i):
    df = pd.read_csv(os.path.join(split_dir, f"splits_{i}.csv"), index_col=0)
    return {col: df[col].dropna().astype(str).tolist() for col in ("train", "val", "test")}


def main():
    pt_ids = {f[:-3] for f in os.listdir(FEATS) if f.endswith(".pt")}
    ok = True
    for split_name, csv_path in TASKS.items():
        split_dir = os.path.join(SPLITS_BASE, split_name)
        labels = pd.read_csv(csv_path)
        lab = dict(zip(labels["slide_id"].astype(str), labels["label"].astype(str)))
        n_total_expected = len(labels)
        # nº de folds = auto-detectado (binarias k=5, fusionada k=3).
        fold_files = glob.glob(os.path.join(split_dir, "splits_*.csv"))
        n_folds = len([p for p in fold_files
                       if not p.endswith(("_bool.csv", "_descriptor.csv"))])
        print(f"\n=== {split_name}  (label CSV: {len(labels)} filas, {n_folds} folds) ===")
        for i in range(n_folds):
            f = load_fold(split_dir, i)
            tr, va, te = set(f["train"]), set(f["val"]), set(f["test"])
            allids = f["train"] + f["val"] + f["test"]
            # 1. disjuntos
            if (tr & va) or (tr & te) or (va & te):
                print(f"  fold {i}: ✗ solapamiento train/val/test"); ok = False
            # 2. total constante
            if len(allids) != n_total_expected:
                print(f"  fold {i}: ✗ total {len(allids)} != {n_total_expected}"); ok = False
            if len(set(allids)) != len(allids):
                print(f"  fold {i}: ✗ slide_id duplicado en el fold"); ok = False
            # 3. conteos por clase en test
            te_lab = [lab.get(s, "??") for s in f["test"]]
            n_pos = sum(1 for x in te_lab if x == "si")
            n_neg = sum(1 for x in te_lab if x == "no")
            n_unk = sum(1 for x in te_lab if x not in ("si", "no"))
            # 4. .pt existe
            missing = [s for s in allids if s not in pt_ids]
            flag = "✓" if (not missing and n_unk == 0) else "✗"
            if missing or n_unk:
                ok = False
            print(f"  fold {i}: {flag} train={len(tr)} val={len(va)} test={len(te)} "
                  f"| test pos(si)={n_pos} neg(no)={n_neg}"
                  + (f" | SIN .pt: {len(missing)}" if missing else "")
                  + (f" | label desconocido: {n_unk}" if n_unk else ""))
    print("\n" + ("RESULTADO: ✓ TODAS LAS INVARIANTES OK" if ok else "RESULTADO: ✗ FALLA — revisar arriba"))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
