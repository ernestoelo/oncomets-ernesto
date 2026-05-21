#!/bin/bash
#SBATCH --job-name=onc_b4_ablB16_mc_mp16
#SBATCH --partition=debug
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=16
#SBATCH --mem=32G
#SBATCH --time=08:00:00
#SBATCH --output=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/logs/ablation_microcalc_B16_minpatch16_%j.out
#SBATCH --error=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/logs/ablation_microcalc_B16_minpatch16_%j.err
#SBATCH --chdir=/media/administrador/Storage1/sdonoso/clam_environ

# ============================================================
# Objetivo 2 (Sprint 4): ablation B=8 vs B=16 — MicroCalcificaciones.
# v2: split FILTRADO minpatch16. ESTE job es el brazo B=16.
# Idéntico al baseline EXCEPTO --B 16 y exp_code/results.
#
# Justificación / hipótesis / métrica de éxito:
# - AUC test = 0.55, AUC val = 0.82, gap = 0.27 (peor caso en V4).
# - Hipótesis: aumentar B (top-B/bottom-B sampling en inst_eval) enriquece la
#   señal supervisada al SmoothTop1SVM en régimen focal (microcalcificaciones).
# - Métrica de éxito predefinida: ΔAUC test >= +0.03 entre B=16 y B=8,
#   manteniendo o reduciendo el gap Val-Test. Si |Δ| < 0.02 o nan en alguna
#   clase: "no concluyente bajo single seed" (múltiples seeds -> próximo sprint).
#   NO forzar interpretación.
#
# SECUENCIAL: se encola con --dependency=afterok:<jobid_baseline>. GPU única.
# SPLIT: microcalcificaciones_pth_100_minpatch16 — el MISMO que el baseline B=8,
# para que la ablation sea controlada (única variable: --B). El umbral 16 del
# split filtrado garantiza >=16 parches por slide de train (necesario para B=16).
# Ver splits_local/.../README.md.
# CONTAINMENT: idéntico al baseline (--chdir read-only, outputs absolutos a clam_testing2/).
# ============================================================

set -euo pipefail

REPO=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto
SPLIT_DIR="$REPO/splits_local/microcalcificaciones_pth_100_minpatch16"
FEATURES_DIR=/media/administrador/Storage1/sdonoso/clam_environ/environ/features/pt_files

source /home/sdonoso/miniconda3/etc/profile.d/conda.sh
conda activate clam_latest
PYBIN="$CONDA_PREFIX/bin/python"   # 'python' a secas está ROTO (ADFRsuite py2.7)

echo "Job $SLURM_JOB_ID started at $(date) on $(hostname)"
"$PYBIN" -c "import torch; assert torch.cuda.is_available(), 'no CUDA'; print('torch', torch.__version__, 'cuda', torch.version.cuda)"
# '|| true': head cierra el pipe -> nvidia-smi recibe SIGPIPE (141); sin esto,
# 'set -o pipefail' + 'set -e' abortarían el job antes de entrenar (bug del run 4083).
nvidia-smi | head -20 || true

# Preflight: verificar que ninguna slide del train tenga n_patches < k_sample (=--B).
# Idiom 'if ! cmd' (no 'cmd; if [ $? ]'): bajo 'set -e' un comando suelto que
# falla aborta el script antes del 'if'; el idiom 'if !' está exento de set -e.
if ! "$PYBIN" "$REPO/scripts/preflight_minpatch.py" \
  --split_dir    "$SPLIT_DIR" \
  --features_dir "$FEATURES_DIR" \
  --min_patches  16 ; then
  echo "PREFLIGHT FAILED: slides with insufficient patches in train split"
  exit 1
fi

"$PYBIN" main.py \
  --drop_out 0.25 \
  --lr 2e-4 \
  --bag_loss ce \
  --inst_loss svm \
  --model_type clam_mb \
  --embed_dim 512 \
  --k 1 \
  --early_stopping \
  --weighted_sample \
  --auto-label-dict \
  --log_data \
  --B 16 \
  --task microcalcificaciones_pth \
  --split_dir "$SPLIT_DIR" \
  --data_root_dir /media/administrador/Storage1/sdonoso/clam_environ/environ \
  --results_dir "$REPO/results/ablation_microcalc_pth_B16_minpatch16" \
  --exp_code "ablation_microcalc_pth_B16_minpatch16_$(date +%Y%m%d_%H%M)"

echo "Job $SLURM_JOB_ID done at $(date)"
echo "Results under $REPO/results/ablation_microcalc_pth_B16_minpatch16/"
