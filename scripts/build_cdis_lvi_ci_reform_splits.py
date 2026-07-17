#!/usr/bin/env python
"""build_cdis_lvi_ci_reform_splits.py — k=5 MC-CV splits para CDIS y LVI con la
FORMULACIÓN NUEVA de Sebastián (17-jul-2026): restringir a WSI invasivas ∩ casos
explícitos, descartando `no_identificado`.

CONTEXTO / ARGUMENTO (regla 9 — para el reviewer)
-------------------------------------------------
Sprint 7 = comparar heatmaps CLAM vs Mammoth en 3 tareas. Estas 2 (CDIS, LVI) se
re-entrenan sobre features ACTUALES con la formulación que decidió Sebastián por
WhatsApp (17-jul, doc `sprints/B7_sprint7/auditoria_coherencia/
hallazgos_sesion_reformulacion_sebastian_17jul.md`, R1-R5):

  "De las WSI invasivas, entrenar LVI y CDIS solo con los casos explícitamente
   ausentes/presentes. No vaya a ser que el modelo termine clasificando
   invasión/no-invasión para la tarea de LVI o CDIS."

  → argumento de FUGA DE TAREA: si `no_identificado` se pliega a la clase negativa
    (como en los `_ci` de Sebastián, ahora SUPERSEDED para estas 2 tareas), la clase
    negativa se llena de WSIs donde el hallazgo NO se evaluó → el modelo puede
    aprender a separar invasivo/no-invasivo (la tarea del clasificador de entrada)
    en vez de LVI/CDIS. Restringir a invasivas ∩ explícitos elimina esa fuga.

Sebastián ACEPTÓ (16:04) los números tal cual, incluido el 85% positivo de CDIS
(la restricción da vuelta el desbalance: los negativos caen de 636 a 132 porque la
mayoría de los "no CDIS" estaban en WSIs no invasivas — clínicamente coherente:
el invasivo suele traer CDIS asociado) y nos delegó la generación ("dale no más").

Comparación CLAM vs Mammoth = PAIRED por reuso del MISMO split_dir
([[patron-paired-comparison-reuso-splits]]). Estratificación a NIVEL PACIENTE
(`patient_strat`) → sin fuga de paciente entre train/val/test. Preflight de
presencia de `.pt` embebido (aborta si algún slide del set no tiene features).

RECETA (idéntica a build_new_tasks_splits.py / build_fusion_splits.py, que replican
el loop de clam_environ/create_splits_seq.py): reusa
`Generic_WSI_Classification_Dataset` + `save_splits` del codebase READ-ONLY de
Sebastián, SIN forkearlo. k=5, val_frac=test_frac=0.1, seed=1, patient_strat.

INSUMOS (READ-ONLY, clam_environ/environ/):
  - Gate invasión (define las WSI invasivas):
      csv_balance/dataset_invasion_carcinoma_gate_label.csv  {invasivo:2013, no_invasivo:802}
  - CDIS 3-cat: csv_balance/dataset_carcinoma_ductal_insitu_presente_label.csv
      {no_identificado:1369, si:810, no:636}
  - LVI  3-cat: csv/dataset_invasion_linfovascular_label.csv   (⚠ CRLF Windows)
      {no_identificado:1968, ausente:479, presente:368}

SALIDA (SOLO bajo clam_testing2/):
  - Snapshots filtrados → data/csv_new_tasks/dataset_<task>_ci_reform_label.csv
  - Splits              → data/splits_kfold/<task>_ci_reform_100/ (splits_i.csv + _bool + _descriptor)

Naming `_ci_reform` para NO pisar los `_ci` de Sebastián (superseded) ni los
snapshots viejos (el LVI 3-clase ya vive como dataset_invasion_linfovascular_label.csv).
`tipo_histologico` NO se regenera (reusa el `_ci` de Sebastián, sigue válido).

NUNCA correr con `python` a secas (workaround B). Usar el binario absoluto del env:
  PY=/home/sdonoso/miniconda3/envs/clam_latest/bin/python ; $PY scripts/build_cdis_lvi_ci_reform_splits.py
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

FEATS = os.path.join(_CLAM, "environ", "features", "pt_files")
CSV_SNAP = os.path.join(_REPO, "data", "csv_new_tasks")
SPLITS_BASE = os.path.join(_REPO, "data", "splits_kfold")

GATE_CSV = os.path.join(_CLAM, "environ", "csv_balance",
                        "dataset_invasion_carcinoma_gate_label.csv")
GATE_POS = "invasivo"   # label del gate que marca WSI invasiva

K = 5
VAL_FRAC = 0.1
TEST_FRAC = 0.1
SEED = 1

# (task_dir_name, csv_insumo_abs, labels_explicitos_a_conservar, label_dict, snap_basename)
TASKS = [
    ("carcinoma_ductal_insitu_presente_ci_reform",
     os.path.join(_CLAM, "environ", "csv_balance",
                  "dataset_carcinoma_ductal_insitu_presente_label.csv"),
     ["no", "si"],
     {"no": 0, "si": 1},
     "dataset_carcinoma_ductal_insitu_presente_ci_reform_label.csv"),
    ("invasion_linfatica_vascular_ci_reform",
     os.path.join(_CLAM, "environ", "csv",
                  "dataset_invasion_linfovascular_label.csv"),
     ["ausente", "presente"],
     {"ausente": 0, "presente": 1},
     "dataset_invasion_linfatica_vascular_ci_reform_label.csv"),
]


def have_pt():
    return set(os.path.splitext(f)[0] for f in os.listdir(FEATS) if f.endswith(".pt"))


def load_clean(path):
    """Lee un CSV de labels y limpia whitespace/CRLF en las columnas de texto."""
    df = pd.read_csv(path, dtype=str)
    for c in ("case_id", "slide_id", "label"):
        df[c] = df[c].str.strip()
    return df


def main():
    os.makedirs(CSV_SNAP, exist_ok=True)
    pt = have_pt()
    print(f"features .pt disponibles: {len(pt)}")

    # WSI invasivas segun el gate (read-only)
    gate = load_clean(GATE_CSV)
    inv_slides = set(gate.loc[gate["label"] == GATE_POS, "slide_id"])
    print(f"WSI invasivas (gate == '{GATE_POS}'): {len(inv_slides)}\n")

    for task, csv_src, keep_labels, label_dict, snap_base in TASKS:
        df = load_clean(csv_src)
        n0 = len(df)

        # FILTRO CENTRAL: invasivas ∩ casos explícitos (descarta no_identificado)
        mask = df["slide_id"].isin(inv_slides) & df["label"].isin(keep_labels)
        df = df.loc[mask].reset_index(drop=True)

        # PREFLIGHT de features: ningun slide del set puede quedar sin .pt
        no_pt = df.loc[~df["slide_id"].isin(pt), "slide_id"].tolist()
        if no_pt:
            print(f"ABORT {task}: {len(no_pt)} slides sin .pt -> {no_pt[:5]}")
            sys.exit(1)

        # Invariantes: sin duplicados, sin fuga de paciente (case con >1 label)
        assert df["slide_id"].duplicated().sum() == 0, f"{task}: slide_id duplicado"
        multi = df.groupby("case_id")["label"].nunique()
        assert (multi > 1).sum() == 0, f"{task}: case_id con >1 label (fuga)"

        snap = os.path.join(CSV_SNAP, snap_base)
        df.to_csv(snap, index=False)

        print("=" * 70)
        print(f"TASK {task}")
        print(f"  insumo: {os.path.basename(csv_src)}  n={n0} -> {len(df)} "
              f"(invasivas ∩ {keep_labels})")
        print(f"  dist slides:    {df['label'].value_counts().to_dict()}")
        print(f"  dist pacientes: {df.groupby('label')['case_id'].nunique().to_dict()}")
        print(f"  snapshot -> {snap}")

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
        print(f"  -> splits en {out}  (splits_0..{K-1}.csv)\n")

    print("OK: splits generados para CDIS y LVI (formulacion _ci_reform).")
    sys.exit(0)


if __name__ == "__main__":
    main()
