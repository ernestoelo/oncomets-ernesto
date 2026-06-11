#!/usr/bin/env python
"""build_necrosis_splits.py — k=5 MC-CV splits del binario NECROSIS (Etapa 1 PathPT).

Pre-registración (regla 9): sprints/B5_sprint5/pathpt/etapa1_prereg_necrosis.md §3.1.

Mismo molde que `scripts/build_new_tasks_splits.py` (reusa
`Generic_WSI_Classification_Dataset` + `save_splits` del codebase READ-ONLY de
Sebastián, sin forkearlo), con el ÚNICO delta de la **binarización**:

    CSV origen (4 clases):  ausente · no_identificado · presente_central · presente_focal
    binario:                ausente -> "no"   |   presente_central ∪ presente_focal -> "si"
                            no_identificado -> EXCLUIDO (mal definido a nivel tile)

Parámetros idénticos a Fase 0 / mammoth (k=5, val_frac=test_frac=0.1, seed=1,
patient_strat, estratificado) → comparación PAIRED consistente.

Lee el CSV de labels READ-ONLY desde clam_environ, snapshotea el binario (filtrando
slides sin .pt) a data/csv_new_tasks/ y genera los splits desde el snapshot. Escribe
SOLO bajo clam_testing2/.

NUNCA correr con `python` a secas (workaround B). Usar el binario absoluto del env:
  PY=/home/sdonoso/miniconda3/envs/clam_latest/bin/python ; $PY scripts/build_necrosis_splits.py
"""
import os
import sys

import numpy as np
import pandas as pd

_CLAM = "/media/administrador/Storage1/sdonoso/clam_environ"
_REPO = "/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto"
if _CLAM not in sys.path:
    sys.path.insert(0, _CLAM)

from dataset_modules.dataset_generic import (  # noqa: E402
    Generic_WSI_Classification_Dataset,
    save_splits,
)

SRC_CSV = os.path.join(
    _CLAM, "environ", "csv",
    "dataset_carcinoma_ductal_in_situ_necrosis_label.csv",
)
FEATS = os.path.join(_CLAM, "environ", "features", "pt_files")
CSV_SNAP = os.path.join(_REPO, "data", "csv_new_tasks",
                        "dataset_cdis_necrosis_2clases_label.csv")
OUT = os.path.join(_REPO, "data", "splits_kfold", "cdis_necrosis_2clases_pth_100")

K = 5
VAL_FRAC = 0.1
TEST_FRAC = 0.1
SEED = 1
LABEL_DICT = {"no": 0, "si": 1}

# binarización (verdad de campo necrosis, handoff §10)
NEG = {"ausente"}                              # -> "no"
POS = {"presente_central", "presente_focal"}  # -> "si"
DROP = {"no_identificado"}                     # excluido


def have_pt():
    return set(os.path.splitext(f)[0] for f in os.listdir(FEATS) if f.endswith(".pt"))


def main():
    os.makedirs(os.path.dirname(CSV_SNAP), exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    pt = have_pt()
    print(f"features .pt disponibles: {len(pt)}\n")

    df = pd.read_csv(SRC_CSV)
    n0 = len(df)
    print(f"CSV origen: {n0} slides | dist: {df['label'].value_counts().to_dict()}")

    # binarizar
    df = df[df["label"].isin(NEG | POS)].copy()
    n_dropped_noid = n0 - len(df)
    df["label"] = np.where(df["label"].isin(POS), "si", "no")

    # filtrar slides sin features (evita crash tardío en training)
    keep = df["slide_id"].astype(str).isin(pt)
    dropped = df.loc[~keep, "slide_id"].tolist()
    df = df.loc[keep].reset_index(drop=True)
    df.to_csv(CSV_SNAP, index=False)

    print(f"binario: {len(df)} slides (excluido no_identificado: {n_dropped_noid})")
    print(f"  dist binaria: {df['label'].value_counts().to_dict()}")
    print(f"  drop sin .pt: {len(dropped)} {dropped[:5]}")
    print(f"  case_id únicos: {df['case_id'].nunique()}  | snapshot -> {CSV_SNAP}")

    np.random.seed(SEED)
    dataset = Generic_WSI_Classification_Dataset(
        csv_path=CSV_SNAP, shuffle=False, seed=SEED, print_info=True,
        label_dict=LABEL_DICT, patient_strat=True, ignore=[],
    )
    num_slides_cls = np.array([len(ids) for ids in dataset.patient_cls_ids])
    val_num = np.round(num_slides_cls * VAL_FRAC).astype(int)
    test_num = np.round(num_slides_cls * TEST_FRAC).astype(int)
    print(f"\npacientes por clase [no, si]: {num_slides_cls.tolist()}  "
          f"val_num={val_num.tolist()}  test_num={test_num.tolist()}")

    dataset.create_splits(k=K, val_num=val_num, test_num=test_num, label_frac=1.0)
    for i in range(K):
        dataset.set_splits()
        descriptor_df = dataset.test_split_gen(return_descriptor=True)
        splits = dataset.return_splits(from_id=True)
        save_splits(splits, ["train", "val", "test"],
                    os.path.join(OUT, f"splits_{i}.csv"))
        save_splits(splits, ["train", "val", "test"],
                    os.path.join(OUT, f"splits_{i}_bool.csv"), boolean_style=True)
        descriptor_df.to_csv(os.path.join(OUT, f"splits_{i}_descriptor.csv"))
    print(f"\nOK: splits_0..{K-1}.csv en {OUT}")
    sys.exit(0)


if __name__ == "__main__":
    main()
