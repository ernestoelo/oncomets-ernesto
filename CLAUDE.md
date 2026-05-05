# CLAUDE.md — Control center OncoMets / Ernesto

> Este archivo es lo primero que Claude Code lee al lanzarse en este repo.
> Contiene contexto persistente del proyecto y reglas operativas.
> Estado en evolución (sprint actual, hallazgos): ver `progress/current.md`.

---

## Quién soy y dónde estoy

Soy Ernesto Gamero, estudiante de último año de Ingeniería Civil Electrónica
(esp. Computadores) en la UTFSM. Práctica en EnvironBio en el proyecto
**OncoMets** (IA para diagnóstico oncológico), 20 hrs/sem. Supervisor:
Sebastián Gaete. Senior: Benjamín. Colaborador: Eduardo.

Este repo (`oncomets-ernesto`) es mi **control center** sobre Werner. NO
contiene el código de CLAM — ese es de Sebastián Donoso y es read-only.

## Stack y paths críticos

**Servidor**: Werner — 4× NVIDIA TITAN RTX, Python 3.11, PyTorch 2.11+cu130.
- Hostname real del equipo: `jenny2-System-Product-Name`.
- Alias SSH desde mi laptop: `environbio` (configurado en `~/.ssh/config`).
- IP: `200.1.17.169`.
- Usuario en Werner: `onco` (compartido entre el equipo, no personal).
- `$HOME` allá: `/home/onco/` (compartido), pero **mi workspace de trabajo
  vive bajo `/mnt/disco_duro/onco/oncologiaEnviron/ernestogamero/`**.
- Conda activo por default: `(base)`. El env con PyTorch 2.11+cu130 puede ser
  `base` u otro — confirmar con `conda env list` la primera vez y documentarlo
  en `docs/werner_environment.md`.

**Codebase de Sebastián Donoso (READ-ONLY, no tocar)**:

```
/mnt/disco_duro/onco/sebastianDonoso/testMIL/CLAM/
├── main.py                      # entrypoint del training
├── eval.py                      # evaluación
├── create_splits_seq.py         # ← genera splits (no los crees a mano)
├── run_all_splits.sh            # ← script que Sebastián usa para splits
├── run_all_training.sh          # ← script que Sebastián usa para training
├── extract_features.py          # extracción de features (CONCH-style)
├── extract_features_fp.py       # variante feature pyramid
├── create_patches.py            # tessellation de WSI
├── create_patches_fp.py         # variante feature pyramid
├── create_heatmaps.py           # visualizaciones de attention
├── obtener_parches_relevantes.py  # selección de patches
├── data_augmentation_environ.py
├── environ_utils.py             # utilidades específicas Environ
├── build_preset.py
├── env.yml / environment.yml    # specs del conda env
├── readme_environ.md / index_CAP_environ.md / openslide_solution.md
├── models/
│   ├── model_clam.py            # ← CLAM_SB y CLAM_MB
│   ├── model_mil.py
│   ├── builder.py
│   ├── resnet_custom_dep.py
│   ├── timm_wrapper.py          # ← contiene timm
│   └── __init__.py
├── utils/
│   ├── core_utils.py            # ← train loop con instance loss
│   ├── eval_utils.py
│   ├── transform_utils.py
│   ├── file_utils.py
│   ├── constants.py
│   └── utils.py
├── dataset_modules/
│   ├── dataset_generic.py
│   ├── dataset_h5.py
│   └── wsi_dataset.py
├── wsi_core/
│   ├── WholeSlideImage.py
│   ├── batch_process_utils.py
│   └── ...
├── vis_utils/
├── extractor_caracteristicas/
├── openslide/                   # build local de openslide (Sebastián tuvo problemas — ver openslide_solution.md)
├── presets/                     # presets de tessellation
├── dataset_csv/                 # CSVs de splits (los que Sebastián ya usó)
├── environ/                     # datos del proyecto Environ (probablemente WSI o features)
├── heatmaps/
└── temp_processing/
```

**Mi workspace en Werner**:

```
/mnt/disco_duro/onco/oncologiaEnviron/ernestogamero/
└── oncomets-ernesto/      # ← este repo, clonado acá
```

> El home `/home/onco/` es **compartido** con el equipo. No instalar deps
> personales con `pip install --user` ni dejar archivos personales ahí.
> Todo lo mío vive bajo `oncologiaEnviron/ernestogamero/`.

## Pipeline OncoMets (referencia rápida)

```
WSI → patches → CONCH features (512/1024-dim) → CLAM_MB → 10 clases clínicas
```

## Sprint actual: B3 / Sprint 3

**Deadline: miércoles 6 de mayo de 2026.**

Detalle exhaustivo en `Objetivo_Especifico_B3_Sprint3__EG.xlsx` (hoja
"Ernesto Gamero"). Resumen de los 4 entregables:

| # | Foco | Entregable |
|---|---|---|
| 1 | Estudio profundo de `L_instance` y su acoplamiento con pseudo-etiquetas | Diagrama `attention → top-B/bottom-B → pseudo-labels → SmoothTop1SVM → L_instance` + tabla de hiperparámetros |
| 2 | Entrenamiento end-to-end de CLAM en Werner con dataset público | Reporte con config, dataset, curvas loss/acc, observaciones |
| 3 | Pipeline de entrenamiento + formato de los `.csv` | Diagrama del pipeline + esquemas de CSVs input/output |
| 4 | ≥2 propuestas de mejora algorítmica (estudio teórico, sin implementar) | Una de ellas es aumentar top-B/bottom-B; la otra abierta |

**Estado vivo**: ver `progress/current.md`.

## Reglas operativas no negociables

1. **NO modificar** ningún archivo bajo `/mnt/disco_duro/onco/sebastianDonoso/`.
   Si necesito cambiar comportamiento, lo hago via wrapper o copia local en
   mi workspace.
2. **Validación factual**: toda afirmación técnica se valida contra
   (a) paper original (`CLAM_Data_Efficient_and_Weakly_Supervised__Paper.pdf`)
   y/o (b) código real en Werner. Si no está en ninguno: decir "no encontrado",
   no inventar.
3. **Referenciar líneas exactas** del código: formato
   `models/model_clam.py:107–125`. Si la línea cambió desde un sprint anterior,
   actualizar `docs/codebase_map.md`.
4. **No inventar resultados experimentales**. Si una métrica no está en los
   logs, decirlo.
5. **No instalar paquetes con `pip --user`** ni dejar archivos en `/home/onco/`
   — es home compartido. Todo bajo `oncologiaEnviron/ernestogamero/`.

## Hechos validados contra el código real (5 mayo 2026)

Todos los números de línea referencian la versión actual del codebase de
Sebastián en Werner. Si Sebastián edita los archivos, hay que re-validar.

### `models/model_clam.py`

- **Existen DOS clases en este archivo**: `CLAM_SB` (single-branch) y
  `CLAM_MB` (multi-branch). El proyecto OncoMets usa `CLAM_MB`.
- `inst_eval` y `inst_eval_out`: **definidos en L107 y L126** respectivamente.
  Son métodos compartidos por ambas clases (probablemente vía herencia o
  duplicación; verificar al primer uso).
- `self.subtyping = subtyping`: **L96** (CLAM_SB) y **L203** (CLAM_MB).
- Bloques `if self.subtyping:` que activan mutual exclusivity:
  - CLAM_SB: L159, L167
  - CLAM_MB: L226, L234
- **Attention pooling** `M = torch.mm(A, h)`: **L170 (CLAM_SB)** y **L237
  (CLAM_MB)**. Opera sobre todos los N parches. La selección top-B/bottom-B
  NO interviene acá — es solo del instance classifier path.

### `utils/core_utils.py`

- `train_loop_clam`: **L226** — entry point del training loop con instance
  loss.
- Cómputo de instance loss en el loop: **L246–251**.
  - L246: `instance_loss = instance_dict['instance_loss']`
  - L251: `total_loss = bag_weight * loss + (1-bag_weight) * instance_loss`
- `bag_weight` es el hiperparámetro que combina bag-level (slide) loss e
  instance loss. **Default: 0.7** (en `main.py` L340).
- `inst_loss` es la elección de loss function: `svm` (SmoothTop1SVM) o `ce`
  (CrossEntropyLoss). Default: `None`. **Para experimentos del paper original:
  `svm`**.
- Si `inst_loss == 'svm'`: `instance_loss_fn = SmoothTop1SVM(n_classes=2)`
  (L142–144). El `n_classes=2` es porque la instance loss es binaria por
  clase (in vs out), independientemente del número de clases del slide-level
  classifier.

### `main.py` — argumentos relevantes (L299–345)

| Argumento | Default | Notas |
|---|---|---|
| `--data_root_dir` | `None` | path a features `.pt` |
| `--embed_dim` | `1024` | CONCH 512 (TCGA) o 1024 (Environ) |
| `--max_epochs` | `200` | |
| `--lr` | `1e-4` | |
| `--results_dir` | `./results` | |
| `--split_dir` | `None` | **NO `--csv_path`** — usa `--split_dir` |
| `--early_stopping` | `False` | flag |
| `--opt` | `adam` | `adam` o `sgd` |
| `--drop_out` | `0.25` | |
| `--bag_loss` | `ce` | `svm` o `ce` |
| `--model_type` | `clam_sb` | usar `clam_mb` para OncoMets |
| `--model_size` | `small` | `small` o `big` |
| `--task` | requerido | task name from TASK_CONFIGS |
| `--inst_loss` | `None` | `svm`, `ce` o `None` |
| `--subtyping` | `False` | flag — activar para mutual exclusivity |
| `--bag_weight` | `0.7` | |
| `--B` | `8` | top-B/bottom-B sample count |
| `--exp_code` | requerido | nombre del experimento |
| `--auto-label-dict` | `False` | flag |

**Important**: el modelo NO toma un `--csv_path`. Toma `--split_dir`.
Los splits se generan con `create_splits_seq.py` y van a `dataset_csv/`.

### Workflow de Sebastián (inferido de `run_all_splits.sh` y `run_all_training.sh`)

1. Genera splits con `create_splits_seq.py` → CSVs en `dataset_csv/`.
2. Lanza training con `main.py --split_dir <dataset_csv/...>` etc.

Ver esos scripts antes de armar nuestro propio wrapper para entender
exactamente qué args usa Sebastián.

### Sobre el "workaround importlib"

En sprints anteriores había un workaround para importar CLAM_MB porque
`__init__.py` cargaba `timm` y rompía. **NO está confirmado que siga siendo
necesario** — el `models/__init__.py` real puede haber cambiado. Validar
intentando primero un import directo simple:

```python
import sys
sys.path.insert(0, "/mnt/disco_duro/onco/sebastianDonoso/testMIL/CLAM")
from models.model_clam import CLAM_MB
```

Si falla con error de timm, aplicar `importlib.util` como fallback.
Documentar el resultado en `docs/workarounds.md`.

## Formato de entregables (regla de oro)

**Diagramas > texto plano. Siempre.** Sebastián rechaza informes de texto
plano. Estilo visual: ver `Modelo_OncoMets_Spatial_V1.pdf` en project files.
Estructura de presentación: ver `Plantilla.pdf`.

**Speaker notes (formato fijado en B2)**:
- Bloques `BLOQUE N — Título`
- Sub-items con `-> `
- Fórmulas inline sin LaTeX render (ej. `h_k = ReLU(W₁·z_k)`)
- Sin emojis ni corchetes de gesto
- Destacados en línea propia: `Punto clave:` / `Detalle crítico:`
- Ultra-minimalista, listo para copy-paste a OnlyOffice

## Subagentes disponibles

| Agente | Foco | Cuándo invocarlo |
|---|---|---|
| `trainer` | Entregable 2: ejecutar entrenamiento end-to-end | Cualquier tarea que toque `main.py`, `create_splits_seq.py`, splits, lanzamiento en GPU |

(Sólo `trainer` por ahora. Setup minimal pre-deadline. Post-cierre se
escalará a leader/implementer/reviewer con `@harness`.)

## Skills cargadas en este repo

- `@dev-workflow` — estructura del repo, Gitflow, validación.
- `@harness` — referencia para escalado post-sprint.

(`@architect` y `@sys-env` no aplican a este repo — la primera es para
crear skills, la segunda es de mi laptop personal Arch+Hyprland.)

## Contexto del usuario para sesiones rápidas

Idioma: **español**. Tono: técnico + explicativo. No simplificar conceptos
generales de ML/DL/CV. SÍ explicar pedagógicamente al introducir notación
específica del subcampo (MIL, weakly-supervised, computational pathology).
