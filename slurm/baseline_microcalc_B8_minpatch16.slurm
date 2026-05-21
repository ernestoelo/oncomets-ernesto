#!/bin/bash
#SBATCH --job-name=onc_b4_baseB8_mc_mp16
#SBATCH --partition=debug
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=16
#SBATCH --mem=32G
#SBATCH --time=08:00:00
#SBATCH --output=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/logs/baseline_microcalc_B8_minpatch16_%j.out
#SBATCH --error=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/logs/baseline_microcalc_B8_minpatch16_%j.err
#SBATCH --chdir=/media/administrador/Storage1/sdonoso/clam_environ

# ============================================================
# Objetivo 1 (Sprint 4): baseline CLAM reproducible — MicroCalcificaciones (B=8).
# v2: split FILTRADO minpatch16 (tras el fallo del run 4096 por bug topk).
#
# Justificación de la elección (tarea microcalcificaciones):
# - AUC test = 0.55, AUC val = 0.82, gap = 0.27 (peor caso en el reporte V4).
# - MicroCalcificaciones es biológicamente focal y dispersa.
# - Hipótesis: el attention pooling lineal de CLAM diluye la señal cuando el
#   patrón diagnóstico está concentrado en pocos parches sobre miles. Aumentar B
#   (top-B/bottom-B sampling en inst_eval) debería enriquecer la señal supervisada
#   al SmoothTop1SVM y mejorar la calidad de las pseudo-etiquetas en este régimen.
# - Métrica de éxito predefinida (para la ablation B=16): ΔAUC test >= +0.03 entre
#   B=16 y B=8 sobre microcalcificaciones, manteniendo o reduciendo el gap Val-Test.
#   Cualquier resultado fuera de esa banda (incluida degradación) es información
#   válida y se reporta sin reinterpretar la hipótesis.
#
# Rol de ESTE job: anclar el baseline B=8 (default del paper).
#
# SPLIT: microcalcificaciones_pth_100_minpatch16 (split filtrado en el repo).
# El canónico tenía 2 slides de train con <16 parches (histai_1536: 6,
# histai_1196: 8) que crasheaban torch.topk en inst_eval (bug del run 4096).
# Se removieron del train; val/test intactos. Ver splits_local/.../README.md.
# Mismo split para B=8 y B=16 -> ablation controlada.
#
# CONTAINMENT: --chdir va al codebase de Sebastián (read-only) porque main.py lee
# csv_path relativo (environ/csv/...). TODO output nuestro (logs, results, split)
# está en clam_testing2/ con paths ABSOLUTOS. No se escribe nada en clam_environ.
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
  --min_patches  8 ; then
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
  --B 8 \
  --task microcalcificaciones_pth \
  --split_dir "$SPLIT_DIR" \
  --data_root_dir /media/administrador/Storage1/sdonoso/clam_environ/environ \
  --results_dir "$REPO/results/baseline_microcalc_pth_B8_minpatch16" \
  --exp_code "baseline_microcalc_pth_B8_minpatch16_$(date +%Y%m%d_%H%M)"

echo "Job $SLURM_JOB_ID done at $(date)"
echo "Results under $REPO/results/baseline_microcalc_pth_B8_minpatch16/"
