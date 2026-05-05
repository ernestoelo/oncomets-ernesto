# Codebase map — código de Sebastián Donoso

Mapa de archivos y líneas clave del CLAM fork de Sebastián. Validado contra
el código real en Werner el **5 de mayo de 2026**.

**Path raíz**: `/mnt/disco_duro/onco/sebastianDonoso/testMIL/CLAM/`

**Reglas**: ningún archivo bajo este path se modifica. Si algo necesita
cambiar, se hace en este repo (vía wrapper o copia local).

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

### CLAM_SB (líneas aproximadas 60–180)

| Línea | Símbolo | Notas |
|---|---|---|
| L75 | docstring `subtyping` | "whether it's a subtyping problem" |
| L79 | `__init__` signature | con `subtyping=False, embed_dim=1024` |
| L96 | `self.subtyping = subtyping` | flag almacenado |
| L107 | `def inst_eval(self, A, h, classifier)` | **rama in-class del instance classifier**. Comentario en código: "h corresponde a la lista con todos los features." |
| L126 | `def inst_eval_out(self, A, h, classifier)` | **rama out-of-class** del instance classifier |
| L159 | `if self.subtyping:` | activa exclusividad mutua dentro de inst_eval (probablemente) |
| L167 | `if self.subtyping:` | otro check de subtyping |
| L170 | `M = torch.mm(A, h)` | **attention pooling**. Comentario: "M representa el feature que representa a la slide completa por clase (K_classes x feature_dim)" |

### CLAM_MB (líneas aproximadas 180–250+)

| Línea | Símbolo | Notas |
|---|---|---|
| L185 | `__init__` signature | con `subtyping=False, embed_dim=1024` |
| L203 | `self.subtyping = subtyping` | |
| L226 | `if self.subtyping:` | |
| L234 | `if self.subtyping:` | |
| L237 | `M = torch.mm(A, h)` | **attention pooling de CLAM_MB**. Sin comentario explícito. |

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
| L226 | `def train_loop_clam(epoch, model, loader, optimizer, n_classes, bag_weight, ...)` | **train loop completo** |
| L229–230 | `Accuracy_Logger` para acc y instance acc | |
| L246 | `instance_loss = instance_dict['instance_loss']` | extracción de la instance loss del dict que devuelve el modelo |
| L248–249 | `instance_loss_value`, `train_inst_loss +=` | logging |
| L251 | `total_loss = bag_weight * loss + (1-bag_weight) * instance_loss` | **combinación final** — esto es lo que se backpropaga |
| L259 | print formateado por batch | "loss, instance_loss, weighted_loss" |
| L276 | `train_inst_loss /= inst_count` | normalización al final del epoch |
| L282 | print fin de epoch | "train_loss, train_clustering_loss, train_error" |

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

Línea 299 en adelante. **Default values entre paréntesis**.

| Argumento | Default | Uso para OncoMets |
|---|---|---|
| `--data_root_dir` | `None` (req) | path a features `.pt` |
| `--embed_dim` | `1024` | **CONCH 512 (TCGA) o 1024 (Environ)** |
| `--max_epochs` | `200` | |
| `--lr` | `1e-4` | |
| `--label_frac` | `1.0` | |
| `--reg` | `1e-5` | weight decay |
| `--seed` | `1` | |
| `--k` | `10` | k-fold cross-validation |
| `--k_start` | `-1` | |
| `--k_end` | `-1` | |
| `--results_dir` | `./results` | |
| `--split_dir` | `None` (req) | **NO es `--csv_path`** — apunta a `dataset_csv/<task>/` |
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
