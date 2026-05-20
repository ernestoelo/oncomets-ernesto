#!/bin/bash
#SBATCH --job-name=onc_b4_ablB16_mcalc_pth
#SBATCH --partition=debug
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=16
#SBATCH --mem=32G
#SBATCH --time=08:00:00
#SBATCH --output=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/logs/ablation_microcalc_B16_%j.out
#SBATCH --error=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/logs/ablation_microcalc_B16_%j.err
#SBATCH --chdir=/media/administrador/Storage1/sdonoso/clam_environ

# ============================================================
# Objetivo 2 (Sprint 4): ablation B=8 vs B=16 — MicroCalcificaciones (_pth).
# ESTE job es el brazo B=16. Idéntico al baseline EXCEPTO --B 16 y exp_code/results.
#
# Justificación de la elección (tarea microcalcificaciones):
# - AUC test = 0.55, AUC val = 0.82, gap = 0.27 (peor caso en el reporte V4).
# - MicroCalcificaciones es biológicamente focal y dispersa.
# - Hipótesis: el attention pooling lineal de CLAM diluye la señal cuando el
#   patrón diagnóstico está concentrado en pocos parches sobre miles. Aumentar B
#   (top-B/bottom-B sampling en inst_eval) debería enriquecer la señal supervisada
#   al SmoothTop1SVM y mejorar la calidad de las pseudo-etiquetas en este régimen.
# - Métrica de éxito predefinida: ΔAUC test >= +0.03 entre B=16 y B=8 sobre
#   microcalcificaciones, manteniendo o reduciendo el gap Val-Test. Cualquier
#   resultado fuera de esa banda (incluida degradación) es información válida y se
#   reporta sin reinterpretar la hipótesis. Si |Δ| < 0.02 o nan en alguna clase:
#   "no concluyente bajo single seed" (múltiples seeds → próximo sprint).
#
# SECUENCIAL: NO encolar hasta que el baseline (B=8) termine COMPLETED y se haya
# revisado su resultado. GPU única → jobs estrictamente secuenciales.
# CONTAINMENT y DATA: idénticos al baseline (ver baseline_microcalc_B8.slurm).
# ============================================================

set -euo pipefail

REPO=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto
source /home/sdonoso/miniconda3/etc/profile.d/conda.sh
conda activate clam_latest
PYBIN="$CONDA_PREFIX/bin/python"   # 'python' a secas está ROTO (ADFRsuite py2.7)

echo "Job $SLURM_JOB_ID started at $(date) on $(hostname)"
"$PYBIN" -c "import torch; assert torch.cuda.is_available(), 'no CUDA'; print('torch', torch.__version__, 'cuda', torch.version.cuda)"
nvidia-smi | head -20

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
  --split_dir /media/administrador/Storage1/sdonoso/clam_environ/environ/splits/microcalcificaciones_pth_100 \
  --data_root_dir /media/administrador/Storage1/sdonoso/clam_environ/environ \
  --results_dir "$REPO/results/ablation_microcalc_pth_B16" \
  --exp_code "ablation_microcalc_pth_B16_$(date +%Y%m%d_%H%M)"

echo "Job $SLURM_JOB_ID done at $(date)"
echo "Results under $REPO/results/ablation_microcalc_pth_B16/"
