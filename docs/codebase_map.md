# Codebase map — código de Sebastián Donoso

Mapa de archivos y líneas clave del CLAM fork de Sebastián. Validado contra
el código real en el **servidor Environ el 19 de mayo de 2026** (re-validado
tras la migración desde Werner; los números de línea se desplazaron, la
lógica es idéntica).

**Path raíz**: `/media/administrador/Storage1/sdonoso/clam_environ/`

**Reglas**: ningún archivo bajo este path se modifica. Si algo necesita
cambiar, se hace en este repo (vía wrapper o copia local).

## CLAM oficial (Mahmood Lab) — REFERENCE ONLY

**Path**: `/media/administrador/Storage1/sdonoso/clam_testing2/CLAM_official_reference/`
**Origen**: `https://github.com/mahmoodlab/CLAM.git`
**HEAD**: `53e2409d4a8189c682c173382964a85f114f923c` ("Update README.md") — clonado
19 may 2026. Incluye soporte CONCH v1.5.

**Uso**: referencia y fuente de `create_heatmaps.py`. **NO se agrega al
PYTHONPATH, NO se importa cruzado con el codebase de Sebastián, NO es
submódulo.** Solo lectura/consulta.

**Hallazgos relevantes (heatmaps, para el Objetivo 4)**:
- `create_heatmaps.py` (raíz) + `vis_utils/heatmap_utils.py` + config en
  `heatmaps/configs/config_template.yaml`.
- Demo: `heatmaps/demo/{ckpts/s_0_checkpoint.pt, slides/*.svs}` +
  `heatmaps/process_lists/heatmap_demo_dataset.csv`.
- **Necesita los WSI originales** (`.svs`/etc.): usa `initialize_wsi` y
  `compute_from_patches` (no basta con los `.pt` de features). Los WSI del
  proyecto están en `/media/administrador/Storage1/sdonoso/{wsi,wsi_histai,...}`
  (read-only) — confirmar disponibilidad/coords h5 antes de la Fase 7.
- Importa `from models import get_encoder` (API más nueva); el codebase de
  Sebastián puede diferir — verificar compatibilidad del checkpoint antes de
  generar heatmaps.

## Estructura general

```
CLAM/
├── main.py                  # entrypoint training
├── eval.py                  # entrypoint evaluación
├── create_splits_seq.py     # generación de splits — usar este, no a mano
├── create_patches.py / create_patches_fp.py   # tessellation
├── extract_features.py / extract_features_fp.py
├── obtener_parches_relevantes.py
├── data_augmentation_environ.py
├── environ_utils.py         # utilidades específicas Environ
├── build_preset.py
├── run_all_splits.sh        # ← workflow de Sebastián para splits
├── run_all_training.sh      # ← workflow de Sebastián para training
├── env.yml / environment.yml
├── readme_environ.md
├── index_CAP_environ.md
├── openslide_solution.md    # ← Sebastián tuvo problemas con openslide
├── models/
├── utils/
├── dataset_modules/
├── wsi_core/
├── vis_utils/
├── extractor_caracteristicas/
├── openslide/               # build local (workaround del solution.md)
├── presets/
├── dataset_csv/             # ← splits que Sebastián ya generó
├── environ/                 # data del proyecto Environ
├── heatmaps/
└── temp_processing/
```

## models/model_clam.py

**Dos clases**: `CLAM_SB` (single-branch) y `CLAM_MB` (multi-branch).
**OncoMets usa `CLAM_MB`**.

> **Líneas validadas 19 may 2026 (server Environ).** Entre paréntesis la
> línea antigua de Werner (5 may 2026) cuando difiere — desplazamiento ≈+2.

### CLAM_SB

| Línea | Símbolo | Notas |
|---|---|---|
| L96 | `self.subtyping = subtyping` | flag almacenado |
| L107 | `def inst_eval(self, A, h, classifier)` | **rama in-class del instance classifier**. Comentario: "h corresponde a la lista con todos los features." |
| L128 (Werner L126) | `def inst_eval_out(self, A, h, classifier)` | **rama out-of-class** del instance classifier |
| L172 (Werner L170) | `M = torch.mm(A, h)` | **attention pooling**. Comentario: "M representa el feature que representa a la slide completa por clase (K_classes x feature_dim)" |

### CLAM_MB

| Línea | Símbolo | Notas |
|---|---|---|
| L185 | `__init__` signature | con `subtyping=False, embed_dim=1024` |
| L205 (Werner L203) | `self.subtyping = subtyping` | |
| L239 (Werner L237) | `M = torch.mm(A, h)` | **attention pooling de CLAM_MB**. |

### Hechos clave

- `inst_eval` y `inst_eval_out` son métodos de la clase. Operan sobre el
  **subset top-B/bottom-B** de patches según attention scores — NO sobre
  los N totales.
- `torch.mm(A, h)` (attention pooling) usa **TODOS los N patches**, no la
  selección top-B/bottom-B. Son mecanismos disjuntos.
- `self.subtyping=True` activa mutual exclusivity. Bajo este flag, la rama
  `inst_eval_out` corre para cada clase ≠ la verdadera, multiplicando su
  contribución al gradiente. Asimetría 9:1 documentada en sprints anteriores.

## utils/core_utils.py

| Línea | Función / símbolo | Qué hace |
|---|---|---|
| L16 | `class Accuracy_Logger` | tracker de accuracy por clase |
| L120 | `loss_fn = SmoothTop1SVM(n_classes=args.n_classes)` | bag-level loss cuando se usa SVM |
| L142–146 | bloque `if args.inst_loss == 'svm':` | **construye `instance_loss_fn = SmoothTop1SVM(n_classes=2)`**. El `n_classes=2` es porque la instance loss es binaria por clase (in vs out). |
| L148 | `instance_loss_fn = nn.CrossEntropyLoss()` | fallback si `inst_loss != 'svm'` |
| L151–153 | construcción del modelo | CLAM_SB o CLAM_MB con `instance_loss_fn` inyectada |
| L187–188 | llamada a `train_loop_clam` y `validate_clam` | entry point del entrenamiento con instance loss |
| L241 (Werner L226) | `def train_loop_clam(epoch, model, loader, optimizer, n_classes, bag_weight, ...)` | **train loop completo** |
| L266 (Werner L246) | `instance_loss = instance_dict['instance_loss']` | extracción de la instance loss del dict que devuelve el modelo |
| L271 (Werner L251) | `total_loss = bag_weight * loss + (1-bag_weight) * instance_loss` | **combinación final** — esto es lo que se backpropaga |

> El resto del loop (logging por batch, normalización, print de fin de epoch)
> mantiene la misma estructura; offsets análogos respecto a Werner.

### Hechos clave

- `bag_weight=0.7` (default) significa que el slide-level loss pesa 70% y
  la instance loss 30%. Es el principal hiperparámetro de balance.
- "clustering loss" en los prints es lo mismo que "instance loss" — Sebastián
  o el upstream usa los nombres intercambiables.
- La división por `n_classes` que mencionaba la memoria del proyecto es
  parte del cómputo dentro de `instance_dict['instance_loss']`, que viene
  del forward del modelo. No está en `core_utils.py` directamente — está
  en `model_clam.py` (probablemente en `forward()`).

## main.py — argumentos relevantes

Parser desde **L446** (server Environ; Werner ~L299). **Default entre
paréntesis.** `TASK_CONFIGS` ahora tiene **38 tasks** (incluye variantes
`_combined`, `_pth` y tasks nuevas de microcalcificaciones/patrones CDIS).
Nuevo arg `--pretrain_path` (warm-start desde checkpoint).

| Argumento | Default | Uso para OncoMets |
|---|---|---|
| `--data_root_dir` | `None` (req) | path a features `.pt` |
| `--embed_dim` | `1024` | **usar 512 (CONCH); 1024 = ResNet legacy** |
| `--max_epochs` | `200` | |
| `--lr` | `1e-4` | |
| `--label_frac` | `1.0` | |
| `--reg` | `1e-5` | weight decay |
| `--seed` | `1` | |
| `--k` | `10` | k-fold cross-validation |
| `--k_start` | `-1` | |
| `--k_end` | `-1` | |
| `--results_dir` | `./results` | |
| `--split_dir` | `None` (req) | **NO es `--csv_path`** — apunta a `environ/splits/<task>_100/` |
| `--log_data` | flag | tensorboard |
| `--testing` | flag | debug |
| `--early_stopping` | flag | |
| `--opt` | `adam` | `adam` \| `sgd` |
| `--drop_out` | `0.25` | |
| `--bag_loss` | `ce` | `svm` \| `ce` |
| `--model_type` | `clam_sb` | **usar `clam_mb`** |
| `--exp_code` | req | nombre experimento |
| `--weighted_sample` | flag | |
| `--model_size` | `small` | `small` \| `big` |
| `--task` | req | task name from TASK_CONFIGS |
| `--no_inst_cluster` | flag | desactiva instance clustering |
| `--inst_loss` | `None` | `svm` \| `ce` \| `None` — **`svm` para paper-faithful** |
| `--subtyping` | flag | **activar para mutual exclusivity en multi-clase** |
| `--bag_weight` | `0.7` | |
| `--B` | `8` | **top-B/bottom-B count** |
| `--auto-label-dict` | flag | |

## Scripts de Sebastián (usar como referencia)

- `run_all_splits.sh` — leer ANTES de generar splits propios. Probablemente
  llama a `create_splits_seq.py` con args específicos.
- `run_all_training.sh` — leer ANTES de armar nuestro `train_clam.sh`.
  Probablemente llama a `main.py` con un set de args concretos.

**Acción para el agente trainer**: leer estos dos `.sh` antes de hacer nada.

## Workaround `importlib.util` — re-validar

En sprints anteriores el workaround era necesario porque `__init__.py` del
`models/` cargaba timm. **Re-validar primero con import directo**, y si
falla, aplicar el workaround. Ver `docs/workarounds.md`.

## Notas de Sebastián que vale la pena leer

- `readme_environ.md`
- `index_CAP_environ.md`
- `openslide_solution.md` — explica el build local de openslide en
  `openslide/`. Si hay problemas con WSI loading, leer este.

## Hallazgos al 5 mayo 2026

Acumulados durante el bring-up del entrenamiento end-to-end (Sprint 3 B3,
Entregable 2). Validar contra el código real si pasa tiempo.

### `splits_0_descriptor.csv` puede estar desactualizado vs `splits_0.csv`

- **Caso confirmado**: bajo
  `environ/splits/grado_histologico_grado_general_100/`, el descriptor
  reporta para val/test counts que **NO matchean** el join
  `splits_0.csv ⨯ dataset_grado_histologico_score_total_label.csv`. Train
  counts sí matchean.
- **Caso opuesto**: bajo `environ/splits/tipo_histologico_100/`, el
  descriptor SÍ está en sync.
- **Causa probable**: re-etiquetado de slides en el CSV de labels después
  de generar el descriptor — `splits_0.csv` (que guarda solo `slide_id`)
  sobrevive, descriptor (que guarda labels) queda stale.
- **Verdad de campo**: hacer el join programático
  `splits_0.csv ⨯ dataset_*_label.csv`. **No confiar en el descriptor**
  para reportes/decisiones de splits.

### Bug en `invasion_linfatica_vascular_100`

- El descriptor lista tres clases: `'no identificada'` (femenino),
  `'no identificado'` (masculino), `'presente'`.
- `--auto-label-dict` las trata como **clases distintas** porque difieren
  en un carácter.
- Probable bug de etiquetado en el CSV fuente (typo de género).
- **Acción**: hablar con Sebastián, NO incluir en entregables del sprint.
