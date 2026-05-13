
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

**Servidor**: Werner — 4× NVIDIA TITAN RTX, Python 3.11.15, PyTorch 2.10.0+cu128
sobre CUDA driver 13.0.

- Hostname real del equipo: `jenny2-System-Product-Name`.
- Alias SSH desde mi laptop: `environbio` (configurado en `~/.ssh/config`).
- IP: `200.1.17.169`.
- Usuario en Werner: `onco` (compartido entre el equipo, no personal).
- `$HOME` allá: `/home/onco/` (compartido), pero **mi workspace de trabajo
  vive bajo `/mnt/disco_duro/onco/oncologiaEnviron/ernestogamero/`**.
- **Env conda activo: `memoriaSebaDonoso`** (no `base` — `base` no tiene
  torch). Profile en `/home/onco/miniconda3/etc/profile.d/conda.sh`. Activar
  con `source <profile> && conda activate memoriaSebaDonoso`.

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

## Sprint actual: B4 / Sprint 4 (abierto el 12 mayo 2026)

**Estado**: scaffolding inicial post-presentación a Benjamín. Dataset
compartido, splits canónicos y división de trabajo Ernesto/Eduardo
**pendientes** de reunión con Sebastián + Eduardo (esta semana, fecha
sin confirmar).

**Dirección del sprint** (de Benjamín, 12 mayo 2026): pasar de
propuestas teóricas a **implementación con argumento clínico /
arquitectónico explícito**. No probar por probar. Una ablation cuenta
como argumento solo si la hipótesis está enunciada de antemano y la
métrica de éxito está predefinida (regla operativa nueva — ver más
abajo).

**4 hilos del sprint** (detalle en `sprints/B4_sprint4/`):

1. **Baseline CLAM reproducible** sobre dataset compartido — con args
   bendecidos por Sebastián. Punto de partida para los otros 3 hilos.
2. **Ablation cuantitativa `B=8` vs `B=16`** sobre tareas prioritarias.
3. **Implementar DSMIL** (Li et al., CVPR 2021) como módulo MIL
   alternativo — wrapper-only que reemplaza el `attention_net` de CLAM.
4. **Heatmaps cualitativos lado-a-lado** (baseline + B=16 + DSMIL);
   upgrade a cuantitativo (IoU/Dice) si Sebastián confirma anotaciones
   de patólogo.

**Tareas prioritarias candidatas** (AUC test < 0.65 en
`Environ_OncoMets_Metricas_V4.pdf`, pendiente confirmación en reunión):

| Tarea | AUC test | AUC val | Gap | n |
|---|---|---|---|---|
| MicroCalcificaciones | 0.55 | 0.82 | 0.27 | 548 |
| C.D.I. Grado Nuclear | 0.60 | — | — | 508 |
| C.D.I. Necrosis | 0.61 | — | — | 508 |
| G.H. Diferenciación Tubular | 0.65 | 0.81 | 0.16 | 934 |

Detalle exhaustivo cuando se confirme: `Excel_Objetivo_Especifico_B4_Sprint4__EG.xlsx`
(a generar tras la reunión).

## Sprints completados

- **B1 — Sprint 1**: configuración de entorno y auditoría de datos en Werner;
  estudio teórico CLAM + CONCH; mapeo del código fuente.
- **B2 — Sprint 2**: estudio inicial de pseudo-etiquetas (§2.2 paper CLAM);
  diagrama `attention → pseudo-labels`; primera propuesta de mejoras.
  Reunión cierre 22 abril 2026. Entregado en `CLAM_Sprint_B2_Presentacion_1.pdf`.
- **B3 — Sprint 3** (cerrado técnicamente el 5 mayo 2026; presentado al
  equipo el 12 mayo 2026): estudio profundo `L_instance` con diagrama
  completo; 2 runs CLAM end-to-end exitosos en Werner (`tipo_histologico`,
  `grado_histologico_grado_general`); documentación del pipeline + CSVs;
  ≥ 2 propuestas de mejora teóricas. Resumen final + métricas en
  `sprints/B3_sprint3/README.md`. Hallazgos metodológicos consolidados
  acá abajo y en `docs/codebase_map.md`. PDF final
  (`CLAM_Sprint_B3.pdf`) en project files de claude.ai.

**Estado vivo**: ver `progress/current.md`.

## Hallazgos del Sprint 3 (relevantes para sprints futuros)

1. **`splits_0_descriptor.csv` puede estar desincronizado con `splits_0.csv`.**
   Caso confirmado: `grado_histologico_grado_general_100`. Causa probable:
   re-etiquetado del CSV de labels sin regenerar el descriptor. Verdad de
   campo = join programático `splits_0.csv ⨯ dataset_<task>_label.csv`.
   **NO confiar en el descriptor sin verificación.**
2. **Bug en `invasion_linfatica_vascular_100`**: el descriptor lista
   `'no identificada'` (femenino) y `'no identificado'` (masculino) como
   clases distintas. Bug de etiquetado en el CSV fuente que `--auto-label-dict`
   propaga. **No usar esta task hasta que Sebastián resuelva el typo.**
3. **Clases minoritarias quedan enteras en train.** En todas las tasks de
   Environ con `seed=1`, `val_frac=test_frac=0.1`, al menos una clase con
   <10 slides queda 100% en train. Para AUC computable, evaluar sólo el
   subset binario efectivo, o regenerar splits con stratification.
4. **Bag loss puede no converger en datasets pequeños** cuando
   `--auto-label-dict` registra clases que el modelo nunca ve en val/test
   (caso `grado_general`). El instance loss SmoothTop1SVM sí converge en
   esos casos. Síntoma de fragilidad del slide-level classifier, no del
   mecanismo de pseudo-etiquetado.
5. **Identidad git en Werner**: el `git config --global` del user `onco`
   apunta a Sebastián Donoso. Para commits desde Werner, **siempre setear
   `git config --local user.name/user.email`** dentro del repo, no global.

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
6. **Antes de confiar en `splits_0_descriptor.csv`**, hacer cross-check con
   join `splits_0.csv ⨯ dataset_<task>_label.csv`. Ver Hallazgo 1 arriba.
7. **Argumento antes de código** (regla nueva, Sprint 4, derivada del
   feedback de Benjamín 12 mayo 2026). Toda propuesta de implementación
   o módulo nuevo viene con justificación **clínica o arquitectónica
   explícita** ANTES de tocar código. Una ablation cuantitativa cuenta
   como argumento sólido **solo si**:

   - La **hipótesis** está enunciada de antemano (qué se espera observar
     y por qué, en términos del mecanismo del modelo o del fenómeno
     clínico).
   - La **métrica de éxito** está predefinida (qué número, sobre qué
     subset, con qué dirección de cambio).

   Si un cambio toca `model_*.py`, `core_utils.py` o el training
   wrapper sin cumplir esto, el agente `reviewer` bloquea el commit.

## Pedagogía de CSVs

Cualquier CSV / artefacto tabular que entra o sale del pipeline se
documenta con este formato fijo. Aplica para introducción de un CSV
nuevo (especialmente con el dataset compartido del Sprint 4) y para
auditar uno existente. Skill asociada: `@csv-audit` (en
`.claude/skills/csv-audit/`).

```
CSV: <nombre exacto del archivo>
Path en Werner: <absoluto>
Schema (columnas y tipos):
  - col_1: tipo, ejemplo, qué representa
  - col_2: ...
Filas: <cuántas hay o se esperan>
Producido por: <script o paso>
Consumido por: <script o paso>
Ejemplo (head -3): ...
Trampas conocidas: <ej. descriptor stale, label_dict bugs>
```

**Práctica complementaria**: descargar snapshot del CSV al workspace
local del sprint para cross-checkear contra el archivo físico — la
copia versionada en `sprints/<sprint>/<objetivo>/` es la verdad de
referencia durante el sprint, el archivo en Werner puede mutar.

### CSVs canónicos del pipeline OncoMets

| CSV | Productor | Consumidor | Sirve para |
|---|---|---|---|
| `dataset_<task>_label.csv` | manual (equipo) | `main.py` vía `Generic_MIL_Dataset` | mapear `slide_id` → label por task |
| `splits_0.csv` | `create_splits_seq.py` | `main.py` | partición train/val/test por fold (**verdad de campo**) |
| `splits_0_bool.csv` | `create_splits_seq.py` | exploración manual | versión booleana del split |
| `splits_0_descriptor.csv` | `create_splits_seq.py` | nadie de confianza (puede estar **stale**) | conteo por clase del split |
| `summary.csv` | `core_utils.py` (fin del entrenamiento) | análisis post-hoc | métricas finales (test_auc/acc, val_auc/acc) por fold |
| `split_0_results.pkl` | `core_utils.py` | análisis post-hoc | predicciones por slide en val/test |

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

| Argumento             | Default       | Notas                                                |
| --------------------- | ------------- | ---------------------------------------------------- |
| `--data_root_dir`   | `None`      | path a features `.pt`                              |
| `--embed_dim`       | `1024`      | CONCH 512 (TCGA) o 1024 (Environ)                    |
| `--max_epochs`      | `200`       |                                                      |
| `--lr`              | `1e-4`      |                                                      |
| `--results_dir`     | `./results` |                                                      |
| `--split_dir`       | `None`      | **NO `--csv_path`** — usa `--split_dir`   |
| `--early_stopping`  | `False`     | flag                                                 |
| `--opt`             | `adam`      | `adam` o `sgd`                                   |
| `--drop_out`        | `0.25`      |                                                      |
| `--bag_loss`        | `ce`        | `svm` o `ce`                                     |
| `--model_type`      | `clam_sb`   | usar `clam_mb` para OncoMets                       |
| `--model_size`      | `small`     | `small` o `big`                                  |
| `--task`            | requerido     | task name from TASK_CONFIGS                          |
| `--inst_loss`       | `None`      | `svm`, `ce` o `None`                           |
| `--subtyping`       | `False`     | flag — activar para mutual exclusivity              |
| `--bag_weight`      | `0.7`       |                                                      |
| `--B`               | `8`         | top-B/bottom-B sample count                          |
| `--exp_code`        | requerido     | nombre del experimento                               |
| `--auto-label-dict` | `False`     | flag                                                 |
| `--weighted_sample` | `False`     | flag — siempre activar para datasets desbalanceados |

**Important**: el modelo NO toma un `--csv_path`. Toma `--split_dir`.
Los splits se generan con `create_splits_seq.py` y van a `dataset_csv/`.

### Workflow de Sebastián (inferido de `run_all_splits.sh` y `run_all_training.sh`)

1. Genera splits con `create_splits_seq.py` → CSVs en `dataset_csv/`.
2. Lanza training con `main.py --split_dir <dataset_csv/...>` etc.

Ver esos scripts antes de armar nuestro propio wrapper para entender
exactamente qué args usa Sebastián.

### Sobre el "workaround importlib" (validado innecesario en `memoriaSebaDonoso`)

En sprints anteriores se documentó un workaround `importlib.util` para
importar `CLAM_MB` evitando el `__init__.py` que cargaba `timm`. **Validado
el 5 mayo 2026: NO es necesario en el env `memoriaSebaDonoso`**. El import
directo funciona:

```python
import sys
sys.path.insert(0, "/mnt/disco_duro/onco/sebastianDonoso/testMIL/CLAM")
from models.model_clam import CLAM_MB
```

Si en una sesión futura aparece error de timm, aplicar `importlib.util`
como fallback y documentar la causa en `docs/workarounds.md`.

## Dependencias instaladas en `memoriaSebaDonoso` durante Sprint 3 B3

Las siguientes deps se instalaron al ejecutar el primer training end-to-end
(5 mayo 2026). Si la sesión de Claude Code se ejecuta en un env que NO
tiene estas, hay que instalarlas:

| Acción             | Paquete                | Versión final | Motivo                                                                     |
| ------------------- | ---------------------- | -------------- | -------------------------------------------------------------------------- |
| install             | `h5py`               | 3.16.0         | bloqueaba `utils/file_utils.py:2`                                        |
| install             | `tensorboardX`       | 2.6.5          | dep declarada en `env.yml`                                               |
| install             | `topk` (smooth-topk) | 1.0            | requerido por `--inst_loss svm` (SmoothTop1SVM)                          |
| install             | `future`             | 1.0.0          | dep transitiva de `topk`                                                 |
| **downgrade** | `pandas`             | 3.0.1 → 2.3.3 | pandas 3.x rechaza `int` en columna `str` (`dataset_generic.py:120`) |

Comando de install (con conda env activo):

```bash
pip install h5py tensorboardX 'pandas>=2.0,<3.0' future
pip install 'git+https://github.com/oval-group/smooth-topk.git'
```

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

| Agente      | Foco                                            | Cuándo invocarlo                                                                           |
| ----------- | ----------------------------------------------- | ------------------------------------------------------------------------------------------- |
| `trainer`  | Ejecutar entrenamiento end-to-end de CLAM (y wrappers, ej. DSMIL) | Cualquier tarea que toque `main.py`, `create_splits_seq.py`, splits, lanzamiento en GPU |
| `reviewer` | Validar propuestas de cambio a modelo / training contra "Argumento antes de código" | **Antes** de cualquier commit que toque `model_*.py`, `core_utils.py`, scripts de training o config. Bloquea si no hay hipótesis + métrica de éxito predefinidas |

Setup minimal por ahora. Post-Sprint 4 se evaluará escalar a
leader/implementer/reviewer formal con `@harness`.

## Skills cargadas en este repo

- `@dev-workflow` — estructura del repo, Gitflow, validación.
- `@harness` — referencia para escalado post-sprint.
- `@csv-audit` — formato pedagógico de CSVs y práctica de cross-check
  contra el archivo físico. Triggers: discusión de un paso del pipeline
  que produce/consume CSV, introducción de un CSV nuevo, sospecha de
  metadata stale.

(`@architect` y `@sys-env` no aplican a este repo — la primera es para
crear skills, la segunda es de mi laptop personal Arch+Hyprland.)

## Contexto del usuario para sesiones rápidas

Idioma: **español**. Tono: técnico + explicativo. No simplificar conceptos
generales de ML/DL/CV. SÍ explicar pedagógicamente al introducir notación
específica del subcampo (MIL, weakly-supervised, computational pathology).
