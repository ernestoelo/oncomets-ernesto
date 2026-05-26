---
name: slurm-submission
description: Lanza trabajos GPU vía sbatch en el servidor Environ (nunca python directo). Plantilla .slurm, recursos típicos, cortesía single-GPU. Triggers — lanzar entrenamiento, train CLAM, sbatch, correr eval, extraer features, run on GPU.
---

# slurm-submission — Lanzar trabajos GPU vía SLURM en el servidor Environ

Toda carga GPU en el servidor Environ se lanza con **`sbatch <archivo>.slurm`**.
**Nunca** `python` directo en GPU (ni `python -c "import torch; torch.cuda..."`,
ni `srun`, ni `nvidia-smi --persistence-mode`). Esta skill fija la plantilla,
los recursos típicos y el protocolo de monitoreo/cancelación.

## Contexto del servidor (validado 19 may 2026)

- Host `administrador-PowerEdge-R740xd`, usuario compartido `sdonoso`.
- **1× RTX A6000 (49 GB)**, driver 570.211.01, CUDA 12.8.
- SLURM slurm-wlm 21.08.5, **partición única `debug` (default), 1 nodo**.
- Conda env de CLAM: **`clam_latest`** (`which python` base está ROTO).
- Codebase read-only: `/media/administrador/Storage1/sdonoso/clam_environ/`.
- Mi workspace: `/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/`.

## Regla de cortesía (GPU única)

No hay GPU de respaldo. **Antes de cada `sbatch`**:

```bash
squeue                  # ¿hay jobs ajenos pendientes? (ej. conch_fe de Sebastián)
squeue -u $USER         # ¿tengo algo ya en cola?
sinfo                   # estado del nodo
```

Si hay jobs ajenos esperando por `Resources`, **no monopolizar**: esperar o
coordinar con el equipo. No enviar jobs grandes a ciegas.

## Plantilla `.slurm` (espejo de `clam_environ/run_training.slurm`, con MIS paths)

Logs van a `logs/` del repo; `--chdir` apunta al codebase de Sebastián para
que los paths relativos (`environ/...`) resuelvan.

```bash
#!/bin/bash
#SBATCH --job-name=eg_train
#SBATCH --output=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/logs/%x_%j.out
#SBATCH --error=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/logs/%x_%j.err
#SBATCH --chdir=/media/administrador/Storage1/sdonoso/clam_environ
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=16
#SBATCH --mem=32G
#SBATCH --time=48:00:00
# sin --partition  → usa la default 'debug'

source $(conda info --base)/etc/profile.d/conda.sh
conda activate clam_latest

CUDA_VISIBLE_DEVICES=0 python main.py \
    --task <task> --exp_code <exp> \
    --split_dir environ/splits/<task>_100 \
    --data_root_dir environ/ --results_dir environ/results_modelo \
    --drop_out 0.25 --lr 2e-4 --bag_loss ce --inst_loss svm \
    --model_type clam_mb --embed_dim 512 --k 1 \
    --early_stopping --weighted_sample --auto-label-dict --log_data
```

> El repo trae `scripts/train_clam.slurm` ya armado con esto — editar task /
> exp_code / split_dir y `sbatch`.

## Preflight checks (obligatorio en `.slurm` de entrenamiento)

**Cuándo agregarlos**: siempre que el entrenamiento dependa de invariantes
del split o del dataset que, si se violan, hacen crashear el job *tarde*
(tras horas) en vez de fallar rápido. Caso de referencia: el bug `topk` del
run 4096 — slides de train con menos parches que `--B` reventaban
`torch.topk` en `inst_eval`, y con `--weighted_sample` el crash aparecía
recién en una época avanzada.

**Patrón**: un script de validación corre **antes** de `python main.py`; si
falla, el job termina en segundos. Bloque a insertar en el `.slurm`:

```bash
# Preflight: validar invariantes del split antes de entrenar.
# Idiom 'if ! cmd; then' (NO 'cmd; if [ $? ]'): bajo 'set -e' un comando
# suelto que falla aborta el script antes del 'if'.
if ! "$PYBIN" "$REPO/scripts/preflight_minpatch.py" \
  --split_dir    "$SPLIT_DIR" \
  --features_dir "$FEATURES_DIR" \
  --min_patches  <= --B del run> ; then
  echo "PREFLIGHT FAILED: invariante del split no se cumple"
  exit 1
fi
```

**Ejemplo de referencia**: `scripts/preflight_minpatch.py` — valida que
ninguna slide de train tenga `< min_patches` parches. El `.out` del job
imprime `PREFLIGHT OK: ...` antes de empezar a entrenar (señal a buscar en
los primeros logs).

**El patrón es general**: aplica a cualquier task futura, no es específico de
microcalcificaciones ni de `minpatch`. Si una task nueva tiene otra
invariante crítica (ej. nº de clases, balance mínimo), escribir su propio
script de preflight siguiendo el mismo molde y referenciarlo en el `.slurm`.

## Recursos típicos (observados en `clam_environ/`)

| Tipo de job | gres | cpus | mem | time | env |
|---|---|---|---|---|---|
| training CLAM | gpu:1 | 16 | 32G | 48:00:00 | clam_latest |
| eval | gpu:1 | 8 | 32G | 48:00:00 | clam_latest |
| feature extraction (CONCH) | gpu:1 | 8 | 32G | 48:00:00 | clam_latest |
| generar splits | — (CPU) | 4 | 8G | 00:30:00 | clam_latest |

## Nombrar `--output` para que los logs vayan al repo

Usar `%x` (job-name) y `%j` (jobid):

```
#SBATCH --output=.../oncomets-ernesto/logs/%x_%j.out
```

Crear `logs/` si no existe (`mkdir -p logs`). Los logs versionables del sprint
van bajo `sprints/<sprint>/<objetivo>/logs/`.

## `--max_epochs` con `--early_stopping` (runs cortos / tareas chicas)

`EarlyStopping` en `utils/core_utils.py` tiene `stop_epoch=50` **hardcoded**:
solo empieza a contar paciencia DESPUÉS de la época 50. Por eso, si pasás
`--max_epochs N` con **N < 50**, el run **para exacto en la época N** (early
stopping nunca recorta) y el mejor checkpoint por `val_loss` igual se guarda.
Útil para tareas chicas que sobreajustan temprano — ej. los 3 binarios de
microcalcificaciones (333 slides, `--max_epochs 30`, job 4109, ~14 min c/u).

Recordatorio de args: **CONCH = `--embed_dim 512`** (1024 es ResNet legacy —
error fácil de cometer al redactar). Plantilla multi-tarea (loop sobre tareas
con preflight por tarea):
`sprints/B4_sprint4/reformulacion_multilabel/train_microcalc_3binarios.slurm`.

## Monitorear y cancelar

```bash
squeue -j <jobid>                 # estado (PD pending / R running)
tail -f logs/<job>_<jobid>.out    # seguir el log
sacct -j <jobid> --format=JobID,State,Elapsed,MaxRSS   # post-mortem
scancel <jobid>                   # cancelar MIS jobs (no los de otros)
```

## Prohibiciones explícitas

- ❌ `python main.py` (o cualquier python en GPU) fuera de un `.slurm`.
- ❌ `srun` interactivo para entrenar.
- ❌ `nvidia-smi --persistence-mode` / `-pm` y similares.
- ❌ Activar un env conda distinto de `clam_latest` para CLAM sin razón.
- ❌ Escribir resultados fuera de mi workspace o de `environ/results_*`
  cuando corresponda (coordinar — `environ/` es de Sebastián).

## Cuándo NO usar esta skill

- Inspección read-only de `.pt`/`.csv` en CPU (`map_location='cpu'`) — eso no
  toca GPU ni SLURM.
- Lectura de logs, `squeue`, `sinfo` (no lanzan nada).
