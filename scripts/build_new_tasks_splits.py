#!/usr/bin/env python
"""build_new_tasks_splits.py — k=5 MC-CV splits para las tareas del Obj 2 B5.

Tareas (mammoth en CLAM, patrón arquitectónico + invasión linfática):
  - cdis_patron_{cribiforme,micropapilar,papilar,solido}_pth  (4 binarias si/no)
  - invasion_linfatica_vascular_pth                           (3 clases)

Replica EXACTAMENTE la receta de `scripts/build_fusion_splits.py` (que a su vez
replica el loop de `clam_environ/create_splits_seq.py`): reusa
`Generic_WSI_Classification_Dataset` + `save_splits` del codebase read-only de
Sebastián, SIN forkearlo ni tocar su `TASK_CONFIGS`. Mismos parámetros que Fase 0
(k=5, val_frac=test_frac=0.1, seed=1, patient_strat, estratificado) → comparación
paired consistente con microcalc.

Lee los CSV de labels READ-ONLY desde `clam_environ/environ/csv/`, **snapshotea**
cada uno (filtrando slides sin `.pt`) a `data/csv_new_tasks/` y genera los splits
desde el snapshot. Escribe SOLO bajo `clam_testing2/`.

NUNCA correr con `python` a secas (workaround B). Usar el binario absoluto del env:
  PY=/home/sdonoso/miniconda3/envs/clam_latest/bin/python ; $PY scripts/build_new_tasks_splits.py
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

CSV_SRC = os.path.join(_CLAM, "environ", "csv")
FEATS = os.path.join(_CLAM, "environ", "features", "pt_files")
CSV_SNAP = os.path.join(_REPO, "data", "csv_new_tasks")
SPLITS_BASE = os.path.join(_REPO, "data", "splits_kfold")

K = 5
VAL_FRAC = 0.1
TEST_FRAC = 0.1
SEED = 1
BIN = {"no": 0, "si": 1}
INV = {"ausente": 0, "no_identificado": 1, "presente": 2}

# (task_dir_name, csv_basename_en_clam_environ, label_dict)
TASKS = [
    ("cdis_patron_cribiforme_pth",
     "dataset_carcinoma_ductal_in_situ_patrones_arquitectonicos_cribiforme_label.csv", BIN),
    ("cdis_patron_solido_pth",
     "dataset_carcinoma_ductal_in_situ_patrones_arquitectonicos_solido_label.csv", BIN),
    ("cdis_patron_micropapilar_pth",
     "dataset_carcinoma_ductal_in_situ_patrones_arquitectonicos_micropapilar_label.csv", BIN),
    ("cdis_patron_papilar_pth",
     "dataset_carcinoma_ductal_in_situ_patrones_arquitectonicos_papilar_label.csv", BIN),
    ("invasion_linfatica_vascular_pth",
     "dataset_invasion_linfovascular_label.csv", INV),
]


def have_pt():
    return set(os.path.splitext(f)[0] for f in os.listdir(FEATS) if f.endswith(".pt"))


def main():
    os.makedirs(CSV_SNAP, exist_ok=True)
    pt = have_pt()
    print(f"features .pt disponibles: {len(pt)}\n")

    for task, csv_base, label_dict in TASKS:
        src = os.path.join(CSV_SRC, csv_base)
        df = pd.read_csv(src)
        n0 = len(df)
        # filtrar slides sin features (evita crash tardío de training)
        keep = df["slide_id"].astype(str).isin(pt)
        dropped = df.loc[~keep, "slide_id"].tolist()
        df = df.loc[keep].reset_index(drop=True)
        snap = os.path.join(CSV_SNAP, csv_base)
        df.to_csv(snap, index=False)

        print("=" * 70)
        print(f"TASK {task}")
        print(f"  CSV: {csv_base}  n={n0} -> {len(df)} (drop sin .pt: {len(dropped)} {dropped[:3]})")
        print(f"  dist: {df['label'].value_counts().to_dict()}")

        np.random.seed(SEED)
        dataset = Generic_WSI_Classification_Dataset(
            csv_path=snap, shuffle=False, seed=SEED, print_info=True,
            label_dict=label_dict, patient_strat=True, ignore=[],
        )
        num_slides_cls = np.array([len(ids) for ids in dataset.patient_cls_ids])
        val_num = np.round(num_slides_cls * VAL_FRAC).astype(int)
        test_num = np.round(num_slides_cls * TEST_FRAC).astype(int)
        print(f"  pacientes por clase: {num_slides_cls.tolist()}  "
              f"val_num={val_num.tolist()}  test_num={test_num.tolist()}")

        out = os.path.join(SPLITS_BASE, f"{task}_100")
        os.makedirs(out, exist_ok=True)
        dataset.create_splits(k=K, val_num=val_num, test_num=test_num, label_frac=1.0)
        for i in range(K):
            dataset.set_splits()
            descriptor_df = dataset.test_split_gen(return_descriptor=True)
            splits = dataset.return_splits(from_id=True)
            save_splits(splits, ["train", "val", "test"],
                        os.path.join(out, f"splits_{i}.csv"))
            save_splits(splits, ["train", "val", "test"],
                        os.path.join(out, f"splits_{i}_bool.csv"), boolean_style=True)
            descriptor_df.to_csv(os.path.join(out, f"splits_{i}_descriptor.csv"))
        print(f"  -> splits en {out}  (splits_0..{K-1}.csv)")

    print("\nOK: splits generados para las 5 tareas.")
    sys.exit(0)


if __name__ == "__main__":
    main()
