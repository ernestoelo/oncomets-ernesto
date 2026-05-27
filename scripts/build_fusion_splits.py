#!/usr/bin/env python
"""build_fusion_splits.py — k-fold splits del binario fusionado (Objetivo 5, Fase 1).

Reusa las clases EXACTAS de `clam_environ/dataset_modules/dataset_generic.py`
(`Generic_WSI_Classification_Dataset` + `save_splits`) replicando el loop de
`clam_environ/create_splits_seq.py` (L611-632), SIN forkear el archivo entero
ni tocar el `TASK_CONFIGS` read-only de Sebastián. Misma lógica (Monte-Carlo CV,
patient_strat, estratificado) y mismos parámetros que los splits de Fase 0
(--k 5 --val_frac 0.1 --test_frac 0.1 --seed 1) → consistencia entre fases.

Lee READ-ONLY el CSV fusionado propio (data/csv_fusion/), escribe SOLO bajo
clam_testing2/ (data/splits_kfold/microcalcificaciones_presencia_100/).

Uso:
    PY=/home/sdonoso/miniconda3/envs/clam_latest/bin/python
    $PY scripts/build_fusion_splits.py
"""
import os
import sys

import numpy as np

_CLAM = "/media/administrador/Storage1/sdonoso/clam_environ"
_REPO = "/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto"
if _CLAM not in sys.path:
    sys.path.insert(0, _CLAM)

from dataset_modules.dataset_generic import (  # noqa: E402
    Generic_WSI_Classification_Dataset,
    save_splits,
)

CSV = os.path.join(_REPO, "data", "csv_fusion",
                   "dataset_microcalcificaciones_presencia_label.csv")
OUT = os.path.join(_REPO, "data", "splits_kfold",
                   "microcalcificaciones_presencia_100")
# k=3 (no 5): la fusionada tiene ~33 positivos en test (vs 7 en las binarias)
# → varianza de partición baja → 3 draws bastan para barras de error estables.
# Decisión "k por régimen de datos" (hipotesis.md Fase 1/2). Las binarias (Fase 0)
# sí van a k=5 porque con 7 positivos la AUC por fold oscila fuerte.
K = 3
VAL_FRAC = 0.1
TEST_FRAC = 0.1
SEED = 1
LABEL_DICT = {"no": 0, "si": 1}


def main():
    np.random.seed(SEED)
    dataset = Generic_WSI_Classification_Dataset(
        csv_path=CSV,
        shuffle=False,
        seed=SEED,
        print_info=True,
        label_dict=LABEL_DICT,
        patient_strat=True,
        ignore=[],
    )

    num_slides_cls = np.array([len(ids) for ids in dataset.patient_cls_ids])
    val_num = np.round(num_slides_cls * VAL_FRAC).astype(int)
    test_num = np.round(num_slides_cls * TEST_FRAC).astype(int)
    print(f"\nslides por clase (patient-level): {num_slides_cls.tolist()}")
    print(f"val_num por clase:  {val_num.tolist()}")
    print(f"test_num por clase: {test_num.tolist()}")

    os.makedirs(OUT, exist_ok=True)
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

    print(f"\nSplits escritos en: {OUT}  (splits_0..{K-1}.csv)")
    sys.exit(0)


if __name__ == "__main__":
    main()
