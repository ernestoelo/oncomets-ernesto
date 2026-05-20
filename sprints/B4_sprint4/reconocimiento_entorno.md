# Reconocimiento del entorno — Servidor Environ (migración desde Werner)

> Sesión read-only de reconocimiento. **Fecha: 19 may 2026.** Cero `sbatch`,
> cero `srun`, cero GPU. Todo el contenido se obtuvo leyendo el entorno fuera
> del workspace (read-only) y cargando `.pt` en CPU (`map_location='cpu'`).
>
> **Objetivo**: migrar el contexto del repo desde el servidor antiguo
> (Werner / jenny2) al servidor actual donde ahora vive el codebase, los
> datasets y el workflow SLURM.

---

## 0. Stack registrado (Fase 0)

Salidas exactas de los comandos de verificación:

| Campo | Valor |
|---|---|
| `pwd` | `/media/administrador/Storage1/sdonoso/clam_testing2` |
| `hostname` | `administrador-PowerEdge-R740xd` |
| `whoami` | `sdonoso` (uid 1008, gid 1008; grupos: `sdonoso`, `docker`) |
| `uname -a` | `Linux administrador-PowerEdge-R740xd 6.8.0-101-generic #101~22.04.1-Ubuntu ... x86_64` |
| `$SHELL` | `/bin/bash` |
| `$CONDA_DEFAULT_ENV` | `base` (¡no `memoriaSebaDonoso`!) |
| `which python` | `/usr/local/ADFRsuite-.../bin/python` → **ROTO** (`libpython2.7.so.1.0` faltante) |
| `sbatch` | `/usr/bin/sbatch` — slurm-wlm **21.08.5** |
| `df -h .` | `/dev/sdb` 15T, usados 13T, disp **1.7T (88%)** en `/media/administrador/Storage1` |

### Conda envs disponibles (no se activó ninguno fuera de `base`)

```
base *  clam_latest  conch  dataset-env  extractor_caracteristicas
memoriaSebaDonoso  pruebas  report-env  trident  xtuner-env
```

- **El env de CLAM en este server es `clam_latest`** (lo confirman TODOS los
  `.slurm` del codebase: `conda activate clam_latest`). NO es
  `memoriaSebaDonoso` como en Werner.
- Para inspección CPU de `.pt` usé el python de `clam_latest`:
  `/home/sdonoso/miniconda3/envs/clam_latest/bin/python`.

### SLURM

```
$ sinfo
PARTITION AVAIL  TIMELIMIT  NODES  STATE NODELIST
debug*       up   infinite      1    mix administrador-PowerEdge-R740xd
```

- **Una sola partición**, `debug` (default), **un solo nodo** que es este
  mismo host. No hay cluster multi-nodo.

```
$ squeue -u sdonoso
  JOBID PARTITION     NAME     USER ST  TIME  NODES NODELIST(REASON)
   4072     debug conch_fe  sdonoso PD  0:00      1 (Resources)
```

- **squeue NO está vacío**: hay un job PENDING (`4072`, `conch_fe`) del
  usuario compartido `sdonoso` — casi seguro la extracción de features CONCH
  de Sebastián (ver `run_extract_features.slurm`). **No se tocó.**

### GPU

```
NVIDIA-SMI 570.211.01   Driver 570.211.01   CUDA 12.8
GPU 0: NVIDIA RTX A6000   49140 MiB   (en uso ~1 GB, util 12%)
Procesos: Xorg + varios python sueltos (oncoMETS-scRNA venv, etc.)
```

- **1× RTX A6000 (49 GB)**, no 4× TITAN RTX como Werner.

---

## 1. Diagrama del directorio padre (Fase 1)

`/media/administrador/Storage1/sdonoso/` — todo propiedad de `sdonoso`.
No se ejecutó `du` sobre los datasets grandes (cientos/miles de entradas
sobre 13 TB; sería lento). No se entró a `clam_testing/`.

```
sdonoso/
├── clam_environ/            CODEBASE CLAM compartido (Sebastián) — READ-ONLY. Contiene environ/ (datos)
├── clam_testing/            workspace de OTRA persona — NO TOCAR
├── clam_testing2/           MI workspace (Ernesto) — contiene oncomets-ernesto/
├── camelyon16_dataset/      dataset público Camelyon16 (WSI)
├── cosine/                  (módulo/experimento)
├── dataset_mama_tcga/       WSI TCGA de mama (~883 entradas)
├── features_statistics_output/  outputs de estadísticas de features
├── HISTAI/                  dataset HistAI
├── histoqc_custom/          HistoQC (control de calidad de WSI)
├── ICIAR2018/               dataset público ICIAR 2018
├── imgs/                    imágenes sueltas
├── LongNetEmbeddings/       embeddings LongNet
├── oncoMets_Spatial/        proyecto espacial OncoMets (scRNA, etc.)
├── PdftoTextReportFormatAndDataset/  pipeline PDF→texto de informes
├── ReportGenModel/          modelo de generación de informes
├── SlideChat / SlideChat_original/   SlideChat (VLM de patología)
├── TCGA_dataset_curated/    TCGA curado (~883 entradas)
├── tcga_files/              metadatos TCGA
├── utils_data_stats/        utilidades de estadísticas
├── wsi / wsi-2/             WSIs del proyecto Environ (privado) (~591 entradas)
├── wsi_biomarker/           WSIs por biomarcador
└── wsi_histai/              WSIs HistAI (~1694 entradas)
```

---

## 2. Tabla de scripts de `clam_environ/` (Fase 2)

Path raíz: `/media/administrador/Storage1/sdonoso/clam_environ/`

| Archivo | Rol | Inputs | Outputs | Invocado desde |
|---|---|---|---|---|
| `main.py` | Entrypoint de training CLAM. Contiene `TASK_CONFIGS` (38 tasks) y `--auto-label-dict` (genera label_dict desde el CSV). | `--task`, `--split_dir`, `--data_root_dir`, features `.pt` | `results_dir/<exp>_s1/`: `summary.csv`, `split_N_results.pkl`, `s_0_checkpoint.pt`, `experiment_*.txt` | `run_all_training.sh`, `run.slurm`, `train_task.slurm`, `run_main.slurm` |
| `eval.py` | Evaluación de checkpoints CLAM. | `--models_dir`, `--splits_dir`, `--split test`, `--task` | `EVAL_*/summary.csv` | `run_eval_comparative.slurm` |
| `create_splits_seq.py` | Genera splits train/val/test por task. | `--task`, `--seed`, `--k`, `--val_frac`, `--test_frac`, `--split_dir`, `--auto-label-dict` | `environ/splits/<task>_100/{splits_0.csv, splits_0_bool.csv, splits_0_descriptor.csv}` | `create_splits_new_tasks.slurm`, `run_all_splits*.sh`, `run_splits_*.slurm` |
| `extract_features_fp.py` | Extracción de features (CONCH v1) por slide. | `--data_h5_dir`, `--data_slide_dir`, `--csv_path`, `--model_name conch_v1`, `--target_patch_size 224` | `environ/features/{pt_files,h5_files}/<slide>.pt/.h5` | `run_extract_features.slurm` (job `conch_fe` 4072 PENDING) |
| `extract_features.py` | Variante de extracción de features. | similar | features `.pt` | (legacy) |
| `extract_supervised_features.py` | Features de parches anotados (supervisado). | `--patches_dir`, `--output_dir`, `--model_name conch_v1` | `environ/parches_anotados_features/` | `run.slurm` (comentado) |
| `create_patches_fp.py` / `create_patches.py` | Tessellation de WSI → parches. | WSI dir, presets | `environ/patches/{patches,...}` | `run_create_patches*.slurm`, `run_patch_*.slurm` |
| `create_heatmaps.py` | Heatmaps de attention. | config YAML, `--task` | `environ/heatmap_production*/` | `run_heatmaps.sh`, `run.slurm` (comentado) |
| `obtener_parches_relevantes.py` | Selección de parches relevantes por attention. | `--task`, `--wsi_path`, `--auto-label-dict` | `resultados_parches_relevantes/` | `run.slurm`, `run_main.slurm` (comentado) |
| `environ_utils.py` | Genera CSVs de labels desde JSON de WSIs. | `--path_wsi`, `--output_path` | `environ/csv/` | `run_environ_utils*.slurm` |
| `run_all_training.sh` | Loop de training sobre lista de tasks. `EMBED_DIM=512`, `--split_dir environ/splits/<task>_100`, K=1, clam_mb. | tasks array | invoca `python main.py` por task | `run_training.slurm`, `run.slurm` (comentado) |
| `models/model_clam.py` | `CLAM_SB` y `CLAM_MB`. | — | — | importado por `main.py` |
| `utils/core_utils.py` | `train`, `train_loop_clam`, `validate`, `summary`. | — | — | importado por `main.py` |
| `data_augmentation_environ.py`, `build_preset.py`, `search_json.py`, `check_patch_size.py` | utilidades varias | — | — | scripts/manual |

### Wrappers `.slurm` — recursos observados

| `.slurm` | partición | gres | cpus | mem | time | conda env | comando |
|---|---|---|---|---|---|---|---|
| `run_training.slurm` | (default `debug`) | gpu:1 | 16 | 32G | 48:00:00 | `clam_latest` | `./run_all_training.sh` |
| `train_task.slurm` | (default) | gpu:1 | 16 | 32G | 48:00:00 | `clam_latest` | `python main.py` (1 task) |
| `run_main.slurm` | `debug` | gpu:1 | 16 | 24G | 24:00:00 | `extractor_caracteristicas` | varios (config) |
| `run.slurm` | `debug` | gpu:1 | 8 | 32G | 10:00:00 | `clam_latest` | `python main.py` / eval / utils |
| `run_extract_features.slurm` | `debug` | gpu:1 | 8 | 32G | 48:00:00 | `clam_latest` | `extract_features_fp.py` (CONCH) |
| `run_eval_comparative.slurm` | (default) | gpu:1 | 8 | 32G | 48:00:00 | `clam_latest` | `eval.py` (priv vs combined) |
| `create_splits_new_tasks.slurm` | (default) | — (CPU) | 4 | 8G | 00:30:00 | `clam_latest` | `create_splits_seq.py` |

> `module load cuda/12.8` aparece en algunos `.slurm` antiguos, pero
> `run_extract_features.slurm` lo comenta con "**not available on this
> machine**". El patrón vigente es `source $(conda info --base)/etc/profile.d/conda.sh && conda activate clam_latest`.

---

## 3. Datasets / features (Fase 3)

### NO existen archivos `.pth`

`find clam_environ -name "*.pth"` → **0 resultados.** La premisa de la
misión (inventario de `.pth` con reglas `_100`→privado / `combined`→pub+priv)
**no aplica a la realidad**:

- El sufijo **`_pth`** en los nombres de tasks/splits **NO se refiere a
  archivos `.pth`**. Según el comentario en `main.py`, las tasks `*_pth` son
  la variante **"privado + TCGA + HistAI"** (la unión grande). Es solo
  nomenclatura de tarea.
- Los "datasets" reales son: **features `.pt` por slide** + **CSVs de labels**
  + **directorios de splits**.

### Features extraídas con CONCH — ubicación confirmada (Fase 3, punto 7)

| Dir | Slides (`.pt`) | Dim feature | Extractor |
|---|---|---|---|
| **`environ/features/pt_files/`** | **2935** | **512** | **CONCH v1** ← features principales del proyecto |
| `environ/features/h5_files/` | 2935 | — | coords/patches (h5) |
| `environ/features_resnet/pt_files/` | 344 | 1024 | ResNet50 (legacy) |
| `environ/features_256/pt_files/` | 344 | 512 | CONCH @ patch 256 |
| `environ/parches_anotados_features/pt_files/` | 10 | — | CONCH supervisado (parches anotados) |

- **Formato `.pt`**: tensor `torch.float32` de shape `[N_parches, 512]`
  (ej. `101907.pt` → `[4308, 512]`). Un tensor por slide; el `.pth` no
  empaqueta nada — CLAM lee los `.pt` individuales vía `data_root_dir/features`.
- **CONCH = 512-dim** para TODAS las slides (Environ + TCGA + HistAI). El
  **1024-dim** corresponde a las features ResNet legacy, NO a CONCH.
  → **Corrige el args bendecido `--embed_dim 1024`: para el workflow CONCH
  actual es `--embed_dim 512`** (así lo usan `run_all_training.sh`,
  `train_task.slurm`, `run.slurm`, `run_eval_comparative.slurm`).
- **No hay que re-extraer**: Sebastián ya tiene 2935 slides con features
  CONCH. (El job `conch_fe` PENDING está completando/actualizando esto.)

### Esquema de datos (CSVs y splits)

| Dir CSV | Contenido |
|---|---|
| `environ/csv_privado/` | labels solo **Environ** (privado). ~533 slides |
| `environ/csv_tcga/` | labels solo **TCGA** |
| `environ/csv_histai/` | labels solo **HistAI** |
| `environ/csv/` | labels **combinado** (unión, ~3072 slides) — lo usan tasks `_combined` y `_pth` |

| Sufijo de split | Composición |
|---|---|
| `<task>_100` | privado (Environ); el `_100` = `label_frac×100` = 100% labels, **no** marcador de privacidad |
| `<task>_combined_100` | privado + TCGA |
| `<task>_pth_100` | privado + TCGA + HistAI (el conjunto grande) |

> La regla de nomenclatura de la misión (`_100`→privado, `combined`→pub+priv)
> es **parcialmente correcta por accidente** (`_100` a secas sí es el set
> privado), pero la semántica real es la de arriba.

### Dataset grande para pruebas finales del Sprint 4

Los splits `_pth_100` (priv+TCGA+HistAI) son los más grandes, sobre las 2935
slides con features CONCH. Tamaños (slides en `splits_0.csv`):

| split `_pth_100` | slides |
|---|---|
| `invasion_linfatica_vascular_pth_100` | **2471** ← el mayor |
| `tipo_histologico_pth_100` | 2462 |
| `grado_histologico_aplica_pth_100` | 2446 |
| `carcinoma_ductal_insitu_presente_pth_100` | 2446 |
| `microcalcificaciones_pth_100` | 2438 |

---

## 4. CSVs relevantes

| CSV | Schema | Filas | Productor | Consumidor | Trampas |
|---|---|---|---|---|---|
| `csv_privado/dataset_<task>_label.csv` | `case_id`, `slide_id`, `label` (str) | ~533 | `environ_utils.py` / equipo | `main.py` (split `_100`) | labels con `_` (ej. `en_tejido_no_neoplasico`); el `label_dict` hardcoded en `main.py` está **stale** vs CSV (auto-label-dict lo sobre-escribe) |
| `csv/dataset_<task>_label.csv` | igual | ~3072 | igual | `main.py` (`_combined`, `_pth`) | mismo |
| `splits/<task>_100/splits_0.csv` | `,train,val,test` (slide_ids) | varía | `create_splits_seq.py` | `main.py` | **verdad de campo** del split |
| `splits/<task>_100/splits_0_descriptor.csv` | `,train,val,test` (counts por clase) | n_clases | `create_splits_seq.py` | reporte | puede estar stale (ver §6) |
| `splits/<task>_100/splits_0_bool.csv` | matriz booleana slide×partición | n_slides | `create_splits_seq.py` | exploración | — |
| `results_*/<exp>_s1/summary.csv` | `folds,test_auc,val_auc,test_acc,val_acc` | =k | `main.py` (fin) | post-hoc | `test_auc` vacío/`nan` si clase con <2 ej. en val/test |

---

## 5. Cross-check de descriptors — 4 tareas prioritarias (Fase 3, punto 6)

Join programático `splits_0.csv ⨯ csv_privado/dataset_<task>_label.csv`
vs `splits_0_descriptor.csv` (split `_100`, fold 0):

| Tarea (split `_100`) | Clases | ¿Descriptor == join? |
|---|---|---|
| `microcalcificaciones` | en_carcinoma_invasivo, en_carcinoma_invasivo-en_cdis, en_cdis, en_cdis-en_tejido_no_neoplasico, en_tejido_no_neoplasico, no_identificado | **MATCH** (sin diffs) |
| `carcinoma_ductal_insitu_grado_nuclear` | grado_1_bajo, grado_2_intermedio, grado_3_alto, no_identificado | **MATCH** |
| `carcinoma_ductal_insitu_necrosis` | ausente, no_identificado, presente_central, presente_focal | **MATCH** |
| `grado_histologico_diferenciacion_tubular` | no_identificado, score_1, score_2, score_3 | **MATCH** |

**Conclusión**: en estas 4 tareas el descriptor está **en sync**. El
hallazgo del Sprint 3 (descriptor stale en `grado_histologico_grado_general`)
no se reproduce aquí — probablemente los splits se regeneraron. La regla de
cross-check sigue vigente como precaución, pero no hay descriptor stale en
las prioritarias.

**Bonus — bug de case-sensitivity RESUELTO**: `invasion_linfovascular` ahora
tiene labels limpias `{ausente, no_identificado, presente}` tanto en privado
(533) como combinado (3072). El typo `'no identificada'` vs `'no identificado'`
del Sprint 3 **ya no está presente** — Sebastián lo corrigió. La task vuelve
a ser usable.

> Severo desbalance de clases en las prioritarias (probable causa del AUC bajo):
> p.ej. `gh_dif_tubular` tiene `score_1`=4 en train; `cdi_necrosis` tiene
> `presente_focal`=1 en train; clase `no_identificado` domina en varias.

---

## 6. Diff: codebase actual vs copias de referencia (Fase 5, punto 8)

No tengo las "copias del project knowledge" como archivos; la referencia
disponible es `docs/codebase_map.md` (validado contra Werner el 5 may 2026).
Comparación contra el código actual en `clam_environ/`:

| Archivo | Símbolo | Línea (codebase_map / Werner) | Línea (server actual) | ¿Lógica? |
|---|---|---|---|---|
| `models/model_clam.py` | `self.subtyping` (CLAM_SB) | 96 | **96** | idéntica |
| | `inst_eval` | 107 | **107** | idéntica |
| | `inst_eval_out` | 126 | **128** | idéntica |
| | `M = torch.mm(A,h)` (SB) | 170 | **172** | idéntica |
| | `self.subtyping` (CLAM_MB) | 203 | **205** | idéntica |
| | `M = torch.mm(A,h)` (MB) | 237 | **239** | idéntica |
| `utils/core_utils.py` | `train_loop_clam` | 226 | **241** | idéntica |
| | `instance_loss = instance_dict[...]` | 246 | **266** | idéntica |
| | `total_loss = bag_weight*loss + (1-bag_weight)*instance_loss` | 251 | **271** | idéntica |
| `main.py` | parser args | ~299 | **446** | crecido |

**Veredicto**: la **lógica del modelo y del train loop es idéntica** a lo
documentado; solo hay **desplazamiento de líneas** (≈+2 en `model_clam.py`,
≈+15–20 en `core_utils.py`). `main.py` **creció mucho**: `TASK_CONFIGS` ahora
tiene **38 tasks** (incluye variantes `_combined`, `_pth`, y tasks nuevas:
`microcalcificaciones_en_{cdis,carcinoma_invasivo,tejido_no_neoplasico}`,
`cdis_patron_{cribiforme,micropapilar,papilar,solido}`,
`tipo_histologico_4clases`). El parser de args es el mismo (defaults
`embed_dim=1024`, `bag_weight=0.7`, `B=8`, `lr=1e-4`, `max_epochs=200`).
`main.py` añadió `--pretrain_path` (warm-start desde checkpoint CLAM).

---

## 7. Args bendecidos (corregidos para el server actual)

De `run_all_training.sh` / `train_task.slurm` / `run.slurm` (reales):

```
--drop_out 0.25 --lr 2e-4 --bag_loss ce --inst_loss svm
--model_type clam_mb --embed_dim 512   # 512 = CONCH (1024 era ResNet legacy)
--k 1 --early_stopping --weighted_sample --auto-label-dict --log_data
```

---

## 8. Dudas / decisiones pendientes para la reunión (Sebastián + Eduardo)

1. **¿El conjunto "grande" de pruebas finales = splits `_pth_100`**
   (priv+TCGA+HistAI, ~2935 slides, features CONCH 512-dim)? Confirmar que
   es el que Ernesto debe usar en el Sprint 4.
2. **`embed_dim` definitivo = 512** (CONCH). Toda la doc del repo decía 1024
   (era ResNet). Confirmar que no se usará ResNet en B4.
3. **conda env de trabajo = `clam_latest`** (no `memoriaSebaDonoso`).
   Confirmar deps (h5py, topk/smooth-topk, tensorboardX, pandas<3) ya
   presentes — no se verificó `pip list` para no activar el env.
4. **Job `conch_fe` (4072) PENDING de `sdonoso`**: ¿es de Sebastián? ¿Conviene
   esperar a que termine antes de lanzar cualquier cosa? GPU única → cortesía.
5. **Una sola GPU (RTX A6000) y partición única `debug`**: no hay GPU "libre
   de respaldo" como en Werner. La regla de cortesía (revisar `squeue`/`sinfo`
   antes de `sbatch`) es ahora crítica.
6. **4 tareas prioritarias**: confirmar la lista (Microcalcificaciones, CDI
   Grado Nuclear, CDI Necrosis, GH Dif. Tubular) y sobre qué split
   (`_100` privado vs `_pth_100` grande) se evalúan.
7. **Módulo MIL alternativo (Objetivo 3)**: la propuesta es DSMIL pero queda
   **sujeta a confirmación** en reunión (ver `objetivo_3_dsmil/README.md`).
8. **`which python` roto** (ADFRsuite py2.7 en PATH): cualquier `python`
   directo fuera de un env conda falla. Siempre `conda activate clam_latest`
   (o el env que aplique) antes de correr nada.

---

## 9. Qué se encontró vs qué se esperaba (resumen de sorpresas)

| Esperado (misión / doc Werner) | Realidad (server actual) |
|---|---|
| Servidor "Environ" con VPN, hostname propio | `administrador-PowerEdge-R740xd` (Dell físico) |
| Usuario personal de Ernesto | usuario **compartido `sdonoso`** (git global = Seba) |
| env `memoriaSebaDonoso` | env de CLAM = **`clam_latest`** |
| 4× TITAN RTX 24GB | **1× RTX A6000 49GB** |
| SLURM multi-partición | **1 partición `debug`, 1 nodo** (este host) |
| squeue vacío | job `conch_fe` (4072) **PENDING** de sdonoso |
| inventario de `.pth` | **no hay `.pth`**; features = `.pt` por slide |
| CONCH 512(TCGA)/1024(Environ) | **CONCH = 512 para todo**; 1024 = ResNet legacy |
| codebase en `/mnt/disco_duro/onco/sebastianDonoso/testMIL/CLAM` | **`/media/administrador/Storage1/sdonoso/clam_environ`** |
| descriptors potencialmente stale | en las 4 prioritarias **están en sync** |
| bug `invasion_linfatica_vascular` | **ya corregido** por Sebastián |
| git user.name | era `ernestoelo` → corregido a `Ernesto Gamero` (local) |
