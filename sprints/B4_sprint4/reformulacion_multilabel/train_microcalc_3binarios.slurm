#!/bin/bash
#SBATCH --job-name=onc_b4_mc_3bin
#SBATCH --partition=debug
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=16
#SBATCH --mem=32G
#SBATCH --time=06:00:00
#SBATCH --output=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/logs/mc_3binarios_%j.out
#SBATCH --error=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/logs/mc_3binarios_%j.err
#SBATCH --chdir=/media/administrador/Storage1/sdonoso/clam_environ

# ============================================================
#  PLANTILLA — NO LANZAR TODAVÍA.  Scaffolding del Sprint B4.
# ============================================================
# Reformulación multi-label de microcalcificaciones: 3 tareas binarias,
# una por tejido {carcinoma_invasivo, cdis, tejido_no_neoplasico}.
# Resuelve el hallazgo de fondo del baseline 8-clases (job 4098): las 8
# clases son un multi-etiqueta aplastado -> régimen de evaluación roto.
#
# Argumento, hipótesis y métrica de éxito: plan_entrenamiento.md
# (regla 9 de CLAUDE.md — argumento antes de código).
#
# PRECONDICIONES (NINGUNA se asume cumplida — ver plan_entrenamiento.md §5):
#   A. La reunión confirma la reformulación en 3 binarios.
#   B. Se ratifica qué es `no_identificado` (el equipo eligió `excluir`;
#      los CSVs existentes tienen 333 slides). Si la reunión decide
#      "negativo limpio", regenerar CSVs + splits antes de usar esto.
#   C. Preflight `topk` OK (este script lo corre; si falla, filtrar el
#      split con scripts/filter_split_by_minpatch.py -> splits_local/).
#   D. Cortesía de GPU: `squeue` antes de `sbatch` (GPU/partición únicas).
#
# CONTAINMENT: --chdir va al codebase de Sebastián (read-only) porque
# main.py lee csv_path relativo. TODO output (logs, results) va a
# clam_testing2/ con paths ABSOLUTOS. No se escribe nada en clam_environ.
# ============================================================

set -euo pipefail

REPO=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto
ENVIRON=/media/administrador/Storage1/sdonoso/clam_environ/environ
FEATURES_DIR="$ENVIRON/features/pt_files"
B=8

source /home/sdonoso/miniconda3/etc/profile.d/conda.sh
conda activate clam_latest
PYBIN="$CONDA_PREFIX/bin/python"   # 'python' a secas está ROTO (ADFRsuite py2.7)

echo "Job $SLURM_JOB_ID started at $(date) on $(hostname)"
"$PYBIN" -c "import torch; assert torch.cuda.is_available(), 'no CUDA'; print('torch', torch.__version__, 'cuda', torch.version.cuda)"
nvidia-smi | head -20 || true   # '|| true': head cierra el pipe -> SIGPIPE (workaround D)

# 3 tareas binarias. Cada una: preflight topk + entrenamiento CLAM_MB.
for TEJIDO in carcinoma_invasivo cdis tejido_no_neoplasico; do
  TASK="microcalcificaciones_en_${TEJIDO}_pth"
  SPLIT_DIR="$ENVIRON/splits/${TASK}_100"
  # Si el preflight (abajo) falla, reemplazar SPLIT_DIR por la copia filtrada:
  #   SPLIT_DIR="$REPO/splits_local/${TASK}_100_minpatch${B}"
  # generada con scripts/filter_split_by_minpatch.py.

  echo ""
  echo "===== TASK: $TASK ====="

  # Preflight obligatorio (CLAUDE.md workaround G): ninguna slide de train
  # con n_patches < B, o torch.topk revienta inst_eval (bug run 4096).
  # Idiom 'if !' exento de set -e.
  if ! "$PYBIN" "$REPO/scripts/preflight_minpatch.py" \
      --split_dir    "$SPLIT_DIR" \
      --features_dir "$FEATURES_DIR" \
      --min_patches  "$B" ; then
    echo "PREFLIGHT FAILED en $TASK: filtrar el split con filter_split_by_minpatch.py"
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
    --B "$B" \
    --task "$TASK" \
    --split_dir "$SPLIT_DIR" \
    --data_root_dir "$ENVIRON" \
    --results_dir "$REPO/results/reformulacion_multilabel/${TEJIDO}" \
    --exp_code "mc_bin_${TEJIDO}_B${B}_$(date +%Y%m%d_%H%M)"

  echo "===== $TASK done ====="
done

echo ""
echo "Job $SLURM_JOB_ID done at $(date)"
echo "Results under $REPO/results/reformulacion_multilabel/"
