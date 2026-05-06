# Entregable 2 — Entrenamiento end-to-end de CLAM en Werner

> **NOTA**: borrador estructurado. Tablas + bullets factuales. La prosa
> final la escribe Ernesto sobre esta base.

## Objetivo

- Correr el pipeline CLAM completo (`main.py`) sobre Werner con el codebase
  read-only de Sebastián (`/mnt/disco_duro/onco/sebastianDonoso/testMIL/CLAM/`).
- Producir métricas reales (no inventadas) en `summary.csv` para al menos
  una task.
- Documentar el flujo de invocación, los CSVs que entran/salen y las
  observaciones técnicas (curvas, comportamiento de instance loss,
  early stopping).

## Configuración del entorno

### Stack confirmado en Werner (5 mayo 2026)

- Hostname: `jenny2-System-Product-Name` · alias SSH `environbio`.
- Usuario: `onco` (compartido).
- GPUs: 4× NVIDIA TITAN RTX (24 GB).
- Driver: 580.126.09 · CUDA driver 13.0.
- Python: 3.11.15 (env `memoriaSebaDonoso`).
- PyTorch: 2.10.0+cu128 · CUDA runtime 12.8 · 4 devices visibles.
- Conda profile: `/home/onco/miniconda3/etc/profile.d/conda.sh`.
- Env activo para CLAM: `memoriaSebaDonoso` (`base` no tiene torch).

### Modificaciones aplicadas al env durante esta sesión

| Acción | Paquete | Versión | Motivo |
|---|---|---|---|
| install | `h5py` | 3.16.0 | bloqueaba `utils/file_utils.py:2` |
| install | `tensorboardX` | 2.6.5 | dep declarada en `env.yml` |
| install | `topk` (smooth-topk) | 1.0 | requerido por `--inst_loss svm` (SmoothTop1SVM) |
| install | `future` | 1.0.0 | dep transitiva de `topk` |
| **downgrade** | `pandas` | 3.0.1 → 2.3.3 | pandas 3.x rechaza `int` en columna `str` (`dataset_generic.py:120`) |

### Verificación pre-run de imports relevantes

```python
import h5py                         # 3.16.0
import tensorboardX                 # 2.6.5
from topk.svm import SmoothTop1SVM  # OK — instanciable con n_classes=2
import torch                        # 2.10.0+cu128, cuda=True, devices=4
import pandas                       # 2.3.3
```

## Setup de datos

### Dataset

- **Privado — Environ** (decisión justificada por disponibilidad inmediata
  de splits, features y `TASK_CONFIGS`; alternativa pública TCGA-BRCA tenía
  features `.pt` pero sin CSV de labels y requería extra setup que no entró
  en la ventana del sprint).
- 41 WSIs totales con `case_id`, `slide_id`, `label` ya generados por
  `environ_utils.py` y curados por Sebastián.
- Features extraídas previamente por Sebastián, dim 1024, en
  `/mnt/disco_duro/onco/sebastianDonoso/testMIL/CLAM/environ/features/pt_files/`.

### Splits

- Generados por `create_splits_seq.py` con seed=1, k=1, val_frac=0.1,
  test_frac=0.1 (defaults).
- Path: `/mnt/disco_duro/onco/sebastianDonoso/testMIL/CLAM/environ/splits/<task>_100/`.
- 3 archivos por task: `splits_0.csv`, `splits_0_bool.csv`,
  `splits_0_descriptor.csv` (este último puede estar **stale** — ver
  Hallazgos).

### Comando de invocación (idéntico para ambos runs salvo task/exp_code)

```bash
CUDA_VISIBLE_DEVICES=1 python main.py \
  --split_dir   <env>/splits/<task>_100 \
  --data_root_dir <env> \
  --task        <task> \
  --exp_code    <exp_code> \
  --results_dir <run_dir> \
  --drop_out 0.25 --lr 2e-4 --bag_loss ce --inst_loss svm \
  --model_type clam_mb --embed_dim 1024 --k 1 --max_epochs 30 \
  --early_stopping --weighted_sample --auto-label-dict
```

- Wrapper local: `scripts/train_clam.sh` (no modifica `main.py`).
- Lanzamiento con `nohup` para sobrevivir caída de SSH.
- GPU 1 (GPU 0 con Xorg minoritario, GPUs 2/3 ocupadas por `jenny2`).

## Resultados Run 1 — `tipo_histologico`

- Run dir: `sprints/B3_sprint3/objetivo_2_entrenamiento/logs/20260505_160216_B3_sprint3_20260505_1602/`
- exp_code: `B3_sprint3_20260505_1602`
- Duración: ~3 minutos (16:02 → 16:05 UTC-4).

### Composición real del split (cross-check `splits_0.csv ⨯ labels.csv`)

| Clase | train | val | test |
|---|---|---|---|
| `carcinoma invasivo de tipo no específico (ductal)` | 30 | 3 | 4 |
| `carcinoma lobulillar invasivo` | 4 | 0 | 0 |
| **Total** | **34** | **3** | **4** |

- `--auto-label-dict` registra **2 clases** (las únicas con label en el CSV
  filtrado por slides presentes), aunque `TASK_CONFIGS` declara 18 clases.
- Mapeo: `'carcinoma invasivo ... (ductal)' → 0`, `'carcinoma lobulillar invasivo' → 1`.

### Métricas finales (`summary.csv`)

| folds | test_auc | val_auc | test_acc | val_acc |
|---|---|---|---|---|
| 0 | (vacío) | (vacío) | 1.0 | 1.0 |

### Lectura técnica

- AUC vacío en val y test → `Only one class is present in y_true` (sklearn
  warning repetido en log) porque `clase 1` (lobulillar) tiene 0 ejemplos en
  val/test.
- `acc=1.0` engañosamente perfecto: 3/3 y 4/4 sobre la única clase presente.
- Las **métricas de train sí son significativas**:
  - `train_clustering_loss` (instance loss SmoothTop1SVM) baja de ~0.7 a 0.075.
  - `train_error` llega a 0.0 antes del epoch 29.
  - `class 0/1 clustering acc = 1.0` perfecto en train (los pseudo-labels top-B/bottom-B se separan correctamente).
- `EarlyStopping counter` osciló (max ~3/20), nunca cortó; el run llegó al
  límite `max_epochs=30`.
- Epoch típico ~5 s en GPU 1 (34 slides, batch_size=1 dentro de cada slide,
  ~10k–80k patches por slide).

### Caso edge — desbalance extremo

- Confirmado por descriptor + cross-check: 4 vs 30 = 1:7.5 en train, 0 vs 3
  en val, 0 vs 4 en test.
- `--weighted_sample` mitiga durante train (resamplea para balancear) pero
  no puede inventar ejemplos de la clase minoritaria en val/test.
- Resultado: AUC indefinido. Métrica útil para defender = comportamiento
  del instance loss (sí converge), no el slide-level classifier (no
  evaluable).

## Resultados Run 2 — `grado_histologico_grado_general`

- Run dir: `sprints/B3_sprint3/objetivo_2_entrenamiento/logs/20260505_230052_B3_sprint3_20260505_2300_grado_general/`
- exp_code: `B3_sprint3_20260505_2300_grado_general`
- Duración: ~3 minutos (23:00 → 23:03 UTC-4).

### Composición real del split (cross-check `splits_0.csv ⨯ labels.csv`)

| Clase | train | val | test |
|---|---|---|---|
| `grado 1` | 5 | 0 | 0 |
| `grado 2` | 9 | 3 | 1 |
| `grado 3` | 10 | 1 | 3 |
| `no identificado` | 6 | 0 | 0 |
| **Total** | **30** | **4** | **4** |

- `--auto-label-dict` registra **4 clases**.
- Mapeo: `'grado 1':0, 'grado 2':1, 'grado 3':2, 'no identificado':3`.
- Eval **efectivamente binaria sobre `grado 2` vs `grado 3`** (clases 1 y 2),
  ambas presentes en val y test → AUC computable.

### Métricas finales (`summary.csv`)

| folds | test_auc | val_auc | test_acc | val_acc |
|---|---|---|---|---|
| 0 | 1.0 | 0.0 | 0.25 | 0.75 |

### Lectura técnica

- **`test_auc=1.0` con `test_acc=0.25`**: ranking de scores correcto, decisión
  argmax desplazada — clásico síntoma de threshold mal calibrado en multi-clase
  con classes minoritarias.
- **`val_auc=0.0` con `val_acc=0.75`**: ranking inverso pero con argmax la
  mayoría cae correcta; es **ruido de N pequeño** (4 muestras), no señal
  consistente.
- **Bag loss NO converge**:
  - `train_loss` final = 1.2449 (epoch 29).
  - `train_error` final = 0.6667 (epoch 29).
  - El slide-level classifier no aprende a discriminar las 4 clases (probable
    causa: 2 de 4 clases — `grado 1`, `no identificado` — nunca se ven en
    val/test, generando gradientes que el modelo no puede calibrar contra
    señal externa).
- **Instance loss SÍ converge**:
  - `train_clustering_loss` final = 0.0889.
  - `class 0/1 clustering acc = 1.0` (perfect) en train.
  - El SmoothTop1SVM separa top-B/bottom-B parches dentro de cada slide aunque
    el slide-level classifier no aprenda.
- `EarlyStopping counter` llegó a 14/20, nunca disparó; modelo guardado =
  best `val_loss` registrado (~0.013 en epoch 26).
- Las métricas en `summary.csv` se computan sobre el **best checkpoint**
  (early-stopping model), no sobre el último epoch — por eso `val_acc=0.75`
  difiere del `val_error=1.0` del último print de training en `train.log`.

## Hallazgos metodológicos

### 1. `splits_0_descriptor.csv` puede estar desactualizado

- **Caso confirmado**: `grado_histologico_grado_general_100/splits_0_descriptor.csv`
  reporta `grado 1: 5/3/1` y `grado 2: 9/1/3`, pero el cross-check de
  `splits_0.csv ⨯ dataset_grado_histologico_score_total_label.csv` da
  `grado 1: 5/0/0` y `grado 2: 9/3/1`.
- **Tabla de divergencia** (val/test):

  | Partición | Clase | Descriptor | Cross-check (verdad) |
  |---|---|---|---|
  | val | grado 1 | 3 | 0 |
  | val | grado 2 | 1 | 3 |
  | val | grado 3 | 0 | 1 |
  | test | grado 1 | 1 | 0 |
  | test | grado 2 | 3 | 1 |
  | test | grado 3 | 0 | 3 |

- **Train counts del descriptor SÍ matchean** (5/9/10/6) → la divergencia
  está localizada en val/test.
- **Caso opuesto**: `tipo_histologico_100/splits_0_descriptor.csv` SÍ está
  sincronizado (30/3/4 ductal · 4/0/0 lobulillar = match con el cross-check).
- **Causa probable**: re-etiquetado posterior de algunos slides del CSV
  de labels sin regenerar el descriptor (el `splits_0.csv` solo guarda
  `slide_id`, sobrevive al re-labeling; el descriptor no).
- **Verdad de campo**: derivar particiones programáticamente del join
  `splits_0.csv ⨯ dataset_*_label.csv`. **No confiar en el descriptor** sin
  verificación.
- **NO es** problema de `--auto-label-dict`: el orden alfabético de las
  clases en el log coincide con el descriptor (`'grado 1':0`, etc.).

### 2. Clases minoritarias quedan enteras en train

- En todas las tasks de Environ con seed=1, val_frac=0.1, test_frac=0.1:
  al menos una clase con <10 slides queda 100% en train (counts 0 en
  val y test).
- Confirmado por inspección de `splits_0_descriptor.csv` de las 5 tasks
  multi-clase candidatas (todas con la misma patología).
- Implicación directa: `--auto-label-dict` registra clases que el modelo
  ve en train pero **no se evalúan**, contaminando el espacio de output.
- Causa: `create_splits_seq.py` particiona uniformemente, no estratificado.

### 3. Bug colateral en `invasion_linfatica_vascular_100`

> Para conversación con Sebastián, **NO entra en el reporte para Sebastián
> ni en los entregables del sprint**.

- El descriptor lista 3 clases: `'no identificada'` (femenino),
  `'no identificado'` (masculino), `'presente'`.
- `--auto-label-dict` las trata como tres clases distintas porque difieren
  en un caracter.
- Probablemente bug de etiquetado en el CSV fuente (typo de género gramatical).

## Conexión con entregable 4 (propuestas)

- **Aumentar `--B` (top-B/bottom-B count)**: ya planteada en reunión inicial.
  Motivada por el éxito del instance loss en ambos runs (clustering acc
  perfecta) — más muestras top/bottom darían señal más rica al SmoothTop1SVM,
  especialmente con datasets pequeños como Environ.
- **K-fold estratificado por clase**: motivada por el hallazgo 2 (clases
  minoritarias enteras en train). Reemplazar `create_splits_seq.py` por una
  versión que use `sklearn.model_selection.StratifiedKFold` o similar.
  Permitiría `val_auc/test_auc` computables aún para tasks con clases muy
  minoritarias.
- **Derivación programática de particiones**: motivada por el hallazgo 1.
  Convertir `splits_0.csv ⨯ labels.csv` en parte del data loader para
  que el descriptor sea siempre fresco. Pequeño helper en mi workspace.
- (Opcional, candidata adicional): re-pesado de instance loss vs bag loss
  cuando bag loss no converge (caso `grado_general`) — exponer el
  `bag_weight` como adaptativo en función del val_loss del slide-level
  classifier.

## Anexos

### Artifacts producidos

| Run | exp_code | Path relativo | Tamaño |
|---|---|---|---|
| 1 | `B3_sprint3_20260505_1602` | `logs/20260505_160216_*/B3_sprint3_20260505_1602_s1/` | checkpoint 3.2 MB · log 28 KB |
| 2 | `B3_sprint3_20260505_2300_grado_general` | `logs/20260505_230052_*/B3_sprint3_20260505_2300_grado_general_s1/` | checkpoint 3.2 MB · log ~30 KB |

Ambos contienen: `s_0_checkpoint.pt`, `summary.csv`, `split_0_results.pkl`,
`splits_0.csv`, `experiment_*.txt`. Logs en `train.log` del run dir padre,
config en `config_snapshot.txt`.

### Otros runs descartados durante la sesión

- Run `20260505_155355_B3_sprint3_20260505_1553`: falló por `h5py` faltante.
- Run `20260505_155936_B3_sprint3_20260505_1559`: falló por pandas 3.0
  rechazando int en columna str.
- Ambos quedan como evidencia del bring-up del entorno; no se borran.
