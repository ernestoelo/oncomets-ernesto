---
name: environ-server
description: Inventario READ-ONLY del codebase y datos compartidos del servidor Environ (CLAM + CONCH features + CSVs + splits). Triggers — dónde están las features, qué tasks hay, ruta del dataset, inventario del servidor, qué hay en clam_environ.
---

# environ-server — Inventario del servidor Environ (codebase + datos)

Referencia del entorno compartido. **Todo bajo `clam_environ/` es READ-ONLY**
(codebase y datos de Sebastián Donoso). Mi workspace es
`clam_testing2/oncomets-ernesto/`. Validado 19 may 2026
(`sprints/B4_sprint4/reconocimiento_entorno.md`).

## Paths raíz

```
/media/administrador/Storage1/sdonoso/
├── clam_environ/        codebase CLAM (READ-ONLY)
│   └── environ/         datos del proyecto (READ-ONLY)
├── clam_testing/        workspace de OTRA persona (NO entrar a escribir)
└── clam_testing2/oncomets-ernesto/   MI workspace
```

## Stack

- Host `administrador-PowerEdge-R740xd`, usuario compartido `sdonoso`.
- Conda env de CLAM: **`clam_latest`** (`which python` base está ROTO →
  activar el env o usar su binario). Para inspección CPU:
  `/home/sdonoso/miniconda3/envs/clam_latest/bin/python`.
- 1× RTX A6000 (49 GB), CUDA 12.8. SLURM: partición única `debug`, 1 nodo.

## Scripts clave de `clam_environ/`

| Script | Rol |
|---|---|
| `main.py` | training; `TASK_CONFIGS` (38 tasks); `--auto-label-dict`; toma `--split_dir` (no `--csv_path`) |
| `eval.py` | evaluación de checkpoints (`--models_dir`, `--splits_dir`, `--split test`) |
| `create_splits_seq.py` | genera splits por task |
| `extract_features_fp.py` | extracción de features CONCH v1 (job `conch_fe`) |
| `run_all_training.sh` | loop de training (embed_dim 512, clam_mb, k=1) |
| `train_task.slurm` / `run_training.slurm` | wrappers SLURM de training (env `clam_latest`) |
| `run_eval_comparative.slurm` | eval privado vs combined |
| `models/model_clam.py` | `CLAM_SB`, `CLAM_MB` |
| `utils/core_utils.py` | train loop + instance loss |

## Features extraídas (NO re-extraer)

| Dir | Slides | Dim | Extractor |
|---|---|---|---|
| `environ/features/pt_files/` | **~3013** | **512** | **CONCH v1** (principal) |
| `environ/features/h5_files/` | ~3013 | — | coords/patches |
| `environ/features_resnet/pt_files/` | 344 | 1024 | ResNet50 (legacy) |
| `environ/features_256/pt_files/` | 344 | 512 | CONCH @ patch 256 |

- Formato `.pt`: `torch.float32`, shape `[N_parches, dim]` (un tensor por slide).
- **CONCH = 512-dim** → usar `--embed_dim 512`. El 1024 es ResNet legacy.
- **No hay archivos `.pth`**: el sufijo `_pth` en tasks/splits = "privado +
  TCGA + HistAI".

## CSVs de labels

| Dir | Conjunto | ~Filas |
|---|---|---|
| `environ/csv_privado/` | Environ (privado) | 533 |
| `environ/csv_tcga/` | TCGA | — |
| `environ/csv_histai/` | HistAI | — |
| `environ/csv/` | combinado (priv+TCGA+HistAI) | 3072 |

Schema: `case_id`, `slide_id`, `label` (str). Labels con `_` (ej.
`en_tejido_no_neoplasico`). Los `label_dict` hardcoded en `main.py` están
stale → `--auto-label-dict` los sobre-escribe desde el CSV.

## Splits (`environ/splits/`)

| Sufijo | Composición |
|---|---|
| `<task>_100` | privado (`_100` = label_frac 100%) |
| `<task>_combined_100` | privado + TCGA |
| `<task>_pth_100` | privado + TCGA + HistAI (**conjunto grande**, ~3013 slides) |

Cada dir: `splits_0.csv` (verdad de campo), `splits_0_bool.csv`,
`splits_0_descriptor.csv` (puede estar stale → cross-check con `@csv-audit`).

El `_pth_100` más grande: `invasion_linfatica_vascular_pth_100` (2471 slides).

## Tareas prioritarias del Sprint 4 (AUC < 0.65)

`microcalcificaciones`, `carcinoma_ductal_insitu_grado_nuclear`,
`carcinoma_ductal_insitu_necrosis`, `grado_histologico_diferenciacion_tubular`.
Descriptors de las 4 verificados **en sync** (19 may 2026). Fuerte desbalance
de clases (probable causa del AUC bajo).

## Reformulación de microcalcificaciones en 3 binarios (infra YA existente)

El equipo (Sebastián) **ya implementó** la reformulación multi-label de
`microcalcificaciones` en 3 tareas binarias — **NO recrearla**:

- **Tasks** (en `main.py`): `microcalcificaciones_en_carcinoma_invasivo_pth`,
  `..._en_cdis_pth`, `..._en_tejido_no_neoplasico_pth` (+ variantes
  `_pth_balance`). `label_dict={}` → requieren `--auto-label-dict`.
- **CSVs**: `environ/csv/dataset_microcalcificaciones_en_<tejido>_label.csv`
  — **333 filas** (subconjunto con localización; `no_identificado` EXCLUIDO),
  label `si`/`no`. Positivos: carcinoma 68, CDIS 121, tejido 195.
- **`csv_balance/`** es **byte-idéntico** a `csv/` para estas 3 tasks (si
  `_balance` aporta algo, está en los splits `_pth_balance_100`).
- **Splits**: `environ/splits/microcalcificaciones_en_<tejido>_pth_100/`,
  estratificados sobre la etiqueta binaria (≥7 positivos en val/test).
- **Verificar** la derivación (CPU): `scripts/verify_binary_microcalc_csvs.py`
  re-deriva del CSV de 8 clases y cross-chequea (MATCH confirmado 21 may 2026).
- Resultados PRELIMINARES (job 4109): carcinoma balanced acc 0,78; CDIS 0,59;
  tejido 0,58. Ver `sprints/B4_sprint4/reformulacion_multilabel/`.

## Reglas

- **READ-ONLY** sobre todo `clam_environ/` (codebase y datos). Cambios →
  wrapper/copia local en mi workspace.
- **NO entrar a escribir** en `clam_testing/`.
- Carga GPU **solo vía SLURM** (`@slurm-submission`). Inspección de `.pt`/`.csv`
  en CPU (`map_location='cpu'`) está OK.
- Cortesía: `squeue`/`sinfo` antes de `sbatch` (GPU única; respetar `conch_fe`).
