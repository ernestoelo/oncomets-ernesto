#!/bin/bash
#SBATCH --job-name=onc_b4_baseB8_mcalc_pth
#SBATCH --partition=debug
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=16
#SBATCH --mem=32G
#SBATCH --time=08:00:00
#SBATCH --output=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/logs/baseline_microcalc_B8_%j.out
#SBATCH --error=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/logs/baseline_microcalc_B8_%j.err
#SBATCH --chdir=/media/administrador/Storage1/sdonoso/clam_environ

# ============================================================
# Objetivo 1 (Sprint 4): baseline CLAM reproducible — MicroCalcificaciones (B=8).
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
# Rol de ESTE job: anclar el baseline B=8 (default del paper) antes de cualquier
# ablation. Métrica de éxito del baseline: reproducir (±0.02) el AUC test
# reportado en Environ_OncoMets_Metricas_V4.pdf para microcalcificaciones (~0.55).
#
# Args: bendecidos por Sebastián (run_all_training.sh) + embed_dim 512 (CONCH).
#
# SPLIT (decisión 20 may 2026): se usa la variante **_pth** (microcalcificaciones_pth,
# priv+TCGA+HistAI, 3072 slides, csv environ/csv/), NO el privado de 533. Razón:
# es el "dataset compartido unificado" del sprint; más datos diluyen el desbalance
# (minorías pasan de ~11 a ~30-90 slides, val/test de 1 a 3-17 por clase) → AUC
# multiclase más estable. El n=548 del PDF V4 (que se parecía al privado) es
# referencia histórica, no el blanco de reproducción del Sprint 4.
#
# CONTAINMENT: --chdir va al codebase de Sebastián (read-only) porque main.py lee
# csv_path relativo (environ/csv/...). TODO output nuestro (logs, results) va con
# paths ABSOLUTOS dentro de clam_testing2/. No se escribe nada en clam_environ.
# DATA: 128 slides del split (todas histai_*) aún sin .pt al momento de preparar
# este script — el job conch_fe (4072) las está extrayendo. El loader las salta
# (warning + None). Como este job queda detrás de conch_fe en la cola, lo más
# probable es que ya existan al arrancar. Train efectivo ~2355, val ~291, test ~298
# si corriera ahora; ~completo si conch_fe terminó. Se reporta el N efectivo real.
# ============================================================

set -euo pipefail

REPO=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto
source /home/sdonoso/miniconda3/etc/profile.d/conda.sh
conda activate clam_latest
# 'python' a secas resuelve a un binario ROTO (ADFRsuite py2.7) por el PATH
# interactivo; usar el binario absoluto del env.
PYBIN="$CONDA_PREFIX/bin/python"

echo "Job $SLURM_JOB_ID started at $(date) on $(hostname)"
"$PYBIN" -c "import torch; assert torch.cuda.is_available(), 'no CUDA'; print('torch', torch.__version__, 'cuda', torch.version.cuda)"
# '|| true': head cierra el pipe -> nvidia-smi recibe SIGPIPE (141); sin esto,
# 'set -o pipefail' + 'set -e' abortarían el job antes de entrenar (bug del run 4083).
nvidia-smi | head -20 || true

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
  --split_dir /media/administrador/Storage1/sdonoso/clam_environ/environ/splits/microcalcificaciones_pth_100 \
  --data_root_dir /media/administrador/Storage1/sdonoso/clam_environ/environ \
  --results_dir "$REPO/results/baseline_microcalc_pth_B8" \
  --exp_code "baseline_microcalc_pth_B8_$(date +%Y%m%d_%H%M)"

echo "Job $SLURM_JOB_ID done at $(date)"
echo "Results under $REPO/results/baseline_microcalc_B8/"
