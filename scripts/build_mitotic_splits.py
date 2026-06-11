#!/usr/bin/env python
"""build_mitotic_splits.py — k=5 MC-CV splits de TASA MITÓTICA 3-clase (Etapa 1 PathPT).

Pre-registración (regla 9): sprints/B5_sprint5/pathpt/etapa1_prereg_mitotic.md §3.3.

Mismo molde que `scripts/build_necrosis_splits.py` (reusa
`Generic_WSI_Classification_Dataset` + `save_splits` del codebase READ-ONLY de Sebastián),
pero SIN binarizar — la tarea es 3-clase ordinal:

    CSV origen (4 clases): no_identificado · score_1 · score_2 · score_3
    3-clase:               score_1 / score_2 / score_3  (mapeo directo)
                           no_identificado -> EXCLUIDO (mal definido a nivel tile)

Parámetros idénticos a necrosis/Fase 0 (k=5, val_frac=test_frac=0.1, seed=1, patient_strat,
estratificado por las 3 clases) → comparación PAIRED consistente.

Lee el CSV READ-ONLY desde clam_environ, snapshotea el 3-clase (filtrando slides sin .pt)
a data/csv_new_tasks/ y genera splits desde el snapshot. Escribe SOLO bajo clam_testing2/.

NUNCA correr con `python` a secas (workaround B):
  PY=/home/sdonoso/miniconda3/envs/clam_latest/bin/python ; $PY scripts/build_mitotic_splits.py
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
    "dataset_grado_histologico_tasa_mitotica_label.csv",
)
FEATS = os.path.join(_CLAM, "environ", "features", "pt_files")
CSV_SNAP = os.path.join(_REPO, "data", "csv_new_tasks",
                        "dataset_grado_mitotic_3clases_label.csv")
OUT = os.path.join(_REPO, "data", "splits_kfold", "grado_mitotic_3clases_pth_100")

K = 5
VAL_FRAC = 0.1
TEST_FRAC = 0.1
SEED = 1
LABEL_DICT = {"score_1": 0, "score_2": 1, "score_3": 2}   # clase 0 = score_1 = basal ordinal

KEEP = {"score_1", "score_2", "score_3"}
DROP = {"no_identificado"}                                 # excluido


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

    # 3-clase (mapeo directo, sin re-etiquetar) — excluir no_identificado
    df = df[df["label"].isin(KEEP)].copy()
    n_dropped_noid = n0 - len(df)

    # filtrar slides sin features (evita crash tardío en training)
    keep = df["slide_id"].astype(str).isin(pt)
    dropped = df.loc[~keep, "slide_id"].tolist()
    df = df.loc[keep].reset_index(drop=True)
    df.to_csv(CSV_SNAP, index=False)

    print(f"3-clase: {len(df)} slides (excluido no_identificado: {n_dropped_noid})")
    print(f"  dist: {df['label'].value_counts().to_dict()}")
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
    print(f"\npacientes por clase [s1, s2, s3]: {num_slides_cls.tolist()}  "
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
