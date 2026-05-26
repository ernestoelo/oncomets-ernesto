#!/bin/bash
# run_dsmil_smoke_carcinoma.slurm
#
# §6.3 mini-train (GPU, 1 epoch) — smoke test pre-experimento del wrapper
# DSMIL_CLAM_MB sobre la task binaria `microcalcificaciones_en_carcinoma_invasivo_pth`.
# La más chica en positivos (68) y la que tiene baseline más fuerte
# (job 4109 balanced_acc 0.78) → mejor para observar señal en 1 epoch.
#
# Objetivo: validar antes del experimento completo (3 tareas × 30 epochs) que
#   (i) train_loss decrece,
#  (ii) no NaN/Inf,
# (iii) gradientes a W_0 y q son sanos (W_0 distinto de cero = L_max
#      activa y c entrena; q distinto de cero = atención relacional
#      entrena).
#
# NO es el experimento. Es la valla antes del experimento.
#
# Lanzamiento (con OK explícito de Ernesto, NO autónomo):
#     cd /media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto
#     squeue ; sinfo                # cortesía: GPU única, no monopolizar
#     sbatch scripts/run_dsmil_smoke_carcinoma.slurm
#
# Monitor:  tail -f logs/eg_dsmil_smoke_*.out
# Cancel:   scancel <jobid>
#
# Workspace containment (CLAUDE.md): logs/ y results/ bajo
# clam_testing2/oncomets-ernesto/. CLAM_environ permanece READ-ONLY.

#SBATCH --job-name=eg_dsmil_smoke
#SBATCH --output=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/logs/%x_%j.out
#SBATCH --error=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/logs/%x_%j.err
#SBATCH --chdir=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --time=00:30:00
# (no --partition → usa la default 'debug')

set -euo pipefail

# Workaround B: `which python` apunta a ADFRsuite python2.7 roto.
# Siempre usar el binario absoluto del env clam_latest.
PYBIN=/home/sdonoso/miniconda3/envs/clam_latest/bin/python

REPO=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto
CLAM=/media/administrador/Storage1/sdonoso/clam_environ

TASK=microcalcificaciones_en_carcinoma_invasivo_pth
CSV=$CLAM/environ/csv/dataset_microcalcificaciones_en_carcinoma_invasivo_label.csv
SPLIT=$CLAM/environ/splits/${TASK}_100

echo "===== Job started at $(date) on $(hostname) ====="
echo "PYBIN  = $PYBIN"
echo "REPO   = $REPO"
echo "CLAM   = $CLAM (READ-ONLY)"
echo "TASK   = $TASK"
nvidia-smi -L || true   # cortesía: log de la GPU asignada

# ── PREFLIGHT (workaround G obligatorio) ─────────────────────────────────
# Reutiliza scripts/preflight_minpatch.py: falla rápido si alguna slide
# de train tiene N parches < B (= 8). Sin esto, el job crashearía tarde
# en torch.topk dentro de inst_eval (bug del run 4096, Sprint 4).
echo "===== PREFLIGHT min_patches >= 8 ====="
$PYBIN $REPO/scripts/preflight_minpatch.py \
    --split_dir    $SPLIT \
    --features_dir $CLAM/environ/features/pt_files \
    --min_patches  8 \
    --fold         0

# ── TRAINING (1 epoch, smoke §6.3) ───────────────────────────────────────
echo "===== TRAIN DSMIL (1 epoch, smoke) ====="
CUDA_VISIBLE_DEVICES=0 $PYBIN $REPO/scripts/train_dsmil.py \
    --task          $TASK \
    --exp_code      smoke_dsmil_carcinoma \
    --csv_path      $CSV \
    --data_root_dir $CLAM/environ \
    --split_dir     $SPLIT \
    --results_dir   $REPO/results/sprint4_obj3_dsmil_smoke \
    --max_epochs    1 \
    --B             8 \
    --bag_weight    0.7 \
    --w_max         0.1 \
    --lr            2e-4 \
    --reg           1e-5 \
    --drop_out      0.25 \
    --embed_dim     512 \
    --seed          1 \
    --fold          0 \
    --label_dict    '{"no": 0, "si": 1}'

echo "===== Job done at $(date) ====="
