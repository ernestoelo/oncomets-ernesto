#!/bin/bash
#SBATCH --job-name=onc_b4_mc_3bin
#SBATCH --partition=debug
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=16
#SBATCH --mem=32G
#SBATCH --time=03:00:00
#SBATCH --output=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/logs/mc_3binarios_%j.out
#SBATCH --error=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/logs/mc_3binarios_%j.err
#SBATCH --chdir=/media/administrador/Storage1/sdonoso/clam_environ

# ============================================================
#  RUN PRELIMINAR — reformulación multi-label de microcalcificaciones.
# ============================================================
# Entrena las 3 tareas binarias, una por tejido {carcinoma_invasivo,
# cdis, tejido_no_neoplasico}, SECUENCIALES en este único job.
# Resuelve el hallazgo de fondo del baseline 8-clases (job 4098) y de la
# ablación B=16 (job 4099): las 8 clases son un multi-etiqueta aplastado;
# B es un hiperparámetro que no mueve la aguja. La palanca correcta es
# reformular la tarea -> esto es esa reformulación.
#
# Argumento, hipótesis y métrica de éxito: plan_entrenamiento.md
# (regla 9 de CLAUDE.md — argumento antes de código).
#
# PRELIMINAR: el resultado de estos runs es insumo para la reunión. Su
# interpretación es contingente a que la reunión (a) confirme la
# reformulación en 3 binarios y (b) ratifique qué es `no_identificado`.
# El equipo eligió `excluir` -> los CSVs binarios existentes tienen ~333
# slides (sin las no_identificado). Este job usa esos CSVs tal cual.
#
# Preflight verificado el 21 may 2026 (CPU, antes de lanzar):
#   - topk/minpatch: los 3 splits de train tienen todas las slides con
#     >= B parches (B=8) -> OK, no hace falta filtrar.
#   - mínimo de positivos por split: los 3 splits están estratificados,
#     ambas clases (si/no) presentes en train/val/test (peor caso:
#     carcinoma, 7 positivos en val y 7 en test) -> OK, AUC computable.
# El bloque preflight de abajo lo re-verifica en el job (workaround G).
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

  # --max_epochs 30: el baseline sobreajustó en la época 6; 30 da margen y
  # con ~333 slides cada run termina en minutos. EarlyStopping tiene
  # stop_epoch=50 hardcoded > 30 -> el run para exacto en la época 30.
  "$PYBIN" main.py \
    --drop_out 0.25 \
    --lr 2e-4 \
    --bag_loss ce \
    --inst_loss svm \
    --model_type clam_mb \
    --embed_dim 512 \
    --k 1 \
    --max_epochs 30 \
    --early_stopping \
    --weighted_sample \
    --auto-label-dict \
    --log_data \
    --B "$B" \
    --task "$TASK" \
    --split_dir "$SPLIT_DIR" \
    --data_root_dir "$ENVIRON" \
    --results_dir "$REPO/results/reformulacion_3binarios_${TEJIDO}" \
    --exp_code "mc_bin_${TEJIDO}_B${B}_$(date +%Y%m%d_%H%M)"

  echo "===== $TASK done ====="
done

echo ""
echo "Job $SLURM_JOB_ID done at $(date)"
echo "Results under $REPO/results/reformulacion_3binarios_<tejido>/"
