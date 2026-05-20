#!/bin/bash
# train_clam.slurm
# SLURM wrapper around Sebastián's main.py. Does NOT modify the original code.
# GPU launches on the Environ server go through `sbatch`, never `python` direct.
#
# Edit TASK / EXP_CODE / SPLIT_DIR below, then:
#     cd /media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto
#     mkdir -p logs
#     squeue ; sinfo            # courtesy check — single GPU, don't monopolize
#     sbatch scripts/train_clam.slurm
#
# Monitor:  squeue -u $USER ;  tail -f logs/eg_train_<jobid>.out
# Cancel:   scancel <jobid>
#
# Blessed args (from clam_environ/run_all_training.sh): embed_dim 512 = CONCH.

#SBATCH --job-name=eg_train
#SBATCH --output=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/logs/%x_%j.out
#SBATCH --error=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/logs/%x_%j.err
#SBATCH --chdir=/media/administrador/Storage1/sdonoso/clam_environ
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=16
#SBATCH --mem=32G
#SBATCH --time=48:00:00
# (no --partition → uses default 'debug')

set -euo pipefail

# ── Edit these per run ────────────────────────────────────────────────────
TASK="${TASK:-microcalcificaciones}"
EXP_CODE="${EXP_CODE:-B4_${TASK}}"
SPLIT_DIR="${SPLIT_DIR:-environ/splits/${TASK}_100}"
RESULTS_DIR="${RESULTS_DIR:-environ/results_modelo}"
MAX_EPOCHS="${MAX_EPOCHS:-30}"
# ──────────────────────────────────────────────────────────────────────────

source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate clam_latest

echo "Job started at $(date)  on $(hostname)"
echo "Task: ${TASK}   exp_code: ${EXP_CODE}   split_dir: ${SPLIT_DIR}"
nvidia-smi -L

CUDA_VISIBLE_DEVICES=0 python main.py \
    --task          "${TASK}" \
    --exp_code      "${EXP_CODE}" \
    --split_dir     "${SPLIT_DIR}" \
    --data_root_dir environ/ \
    --results_dir   "${RESULTS_DIR}" \
    --drop_out      0.25 \
    --lr            2e-4 \
    --bag_loss      ce \
    --inst_loss     svm \
    --model_type    clam_mb \
    --embed_dim     512 \
    --k             1 \
    --max_epochs    "${MAX_EPOCHS}" \
    --early_stopping \
    --weighted_sample \
    --log_data \
    --auto-label-dict

echo "Done at $(date). Results in ${RESULTS_DIR}/${EXP_CODE}_s1/"
