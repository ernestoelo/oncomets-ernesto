---
name: slurm-submission
description: Use when the user asks to train, evaluate, generate splits, extract features, or launch ANYTHING that uses the GPU on the Environ server. Triggers include "lanzar entrenamiento", "train CLAM", "sbatch", "correr eval", "generar splits", "extraer features", "run on GPU". Enforces SLURM submission (never python directly on GPU) and the single-GPU courtesy rule.
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
