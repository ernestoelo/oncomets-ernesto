#!/bin/bash
#SBATCH --job-name=eg_mc_var_kfold
#SBATCH --partition=debug
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=16
#SBATCH --mem=32G
#SBATCH --time=06:00:00
#SBATCH --output=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/logs/%x_%j.out
#SBATCH --error=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/logs/%x_%j.err
#SBATCH --chdir=/media/administrador/Storage1/sdonoso/clam_environ

# ============================================================
#  OBJETIVO 5 — FASE 0: caracterización de varianza (k-fold CLAM_MB).
# ============================================================
# Corre las 3 binarias de microcalcificaciones con --k 5 (Monte-Carlo CV,
# test_frac=0.1) para medir mean ± std del test_auc / balanced_acc y
# calibrar si los Δ a n≈33 son reales o ruido (hipotesis.md §FASE 0).
#
# DIFERENCIA vs job 4109 (apples-to-apples salvo lo siguiente):
#   - --k 5 (no --k 1): 5 particiones de test distintas por tarea.
#   - --split_dir apunta a splits PROPIOS bajo clam_testing2/ (k-fold
#     generados con create_splits_seq.py --k 5 --val_frac 0.1
#     --test_frac 0.1 --seed 1), NO a los splits de Sebastián.
#   - universo 328 identificadas (drift del CSV; era 333 en 4109).
# Todo lo demás (modelo, features, args bendecidos) es idéntico al 4109.
#
# Argumento + métrica: sprints/B4_sprint4/objetivo_5_fusion_binaria/hipotesis.md
# (regla 9). Reviewer OK 2026-05-27.
#
# NO es pass/fail de modelo — caracteriza la varianza del régimen de
# evaluación. std(test_auc) > 0.05 → toda comparación downstream (fusión,
# DSMIL) va con k-fold.
#
# CONTAINMENT: --chdir al codebase de Sebastián (read-only) porque main.py
# lee csv_path relativo. TODO output (logs, results, splits) va a
# clam_testing2/ con paths ABSOLUTOS. Splits leídos del workspace propio.
#
# Lanzamiento (solo con OK explícito de Ernesto, NO autónomo):
#     cd /media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto
#     squeue ; sinfo                # cortesía: GPU única compartida
#     sbatch scripts/run_obj5_varianza_kfold.slurm
# Monitor:  tail -f logs/eg_mc_var_kfold_*.out
# Cancel:   scancel <jobid>
# Tiempo estimado: ~42 min (4109, 3 tareas × 1 fold) × 5 ≈ 3.5h. --time 6h.
# ============================================================

set -euo pipefail

REPO=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto
ENVIRON=/media/administrador/Storage1/sdonoso/clam_environ/environ
FEATURES_DIR="$ENVIRON/features/pt_files"
SPLITS_BASE="$REPO/data/splits_kfold"
B=8
K=5
RUN_TS=$(date +%Y%m%d_%H%M)   # timestamp en exp_code: un re-run NO pisa el run previo (workaround C: nada se borra)

source /home/sdonoso/miniconda3/etc/profile.d/conda.sh
conda activate clam_latest
PYBIN="$CONDA_PREFIX/bin/python"   # 'python' a secas está ROTO (ADFRsuite py2.7)

echo "Job $SLURM_JOB_ID started at $(date) on $(hostname)"
"$PYBIN" -c "import torch; assert torch.cuda.is_available(), 'no CUDA'; print('torch', torch.__version__, 'cuda', torch.version.cuda)"
nvidia-smi | head -20 || true   # '|| true': head cierra el pipe -> SIGPIPE (workaround D)

# Verificador determinístico de los k-fold splits (smoke #1, idiom 'if !' exento de set -e).
if ! "$PYBIN" "$REPO/scripts/verify_kfold_splits.py" ; then
  echo "VERIFY KFOLD FAILED — splits inconsistentes, abortar"
  exit 1
fi

for TEJIDO in carcinoma_invasivo cdis tejido_no_neoplasico; do
  TASK="microcalcificaciones_en_${TEJIDO}_pth"
  SPLIT_DIR="$SPLITS_BASE/${TASK}_100"

  echo ""
  echo "===== TASK: $TASK  (k=$K folds) ====="

  # Preflight obligatorio (workaround G) en CADA fold: ninguna slide de
  # train con n_patches < B, o torch.topk revienta inst_eval (bug 4096).
  for ((f=0; f<K; f++)); do
    if ! "$PYBIN" "$REPO/scripts/preflight_minpatch.py" \
        --split_dir    "$SPLIT_DIR" \
        --features_dir "$FEATURES_DIR" \
        --min_patches  "$B" \
        --fold         "$f" ; then
      echo "PREFLIGHT FAILED en $TASK fold $f"
      exit 1
    fi
  done

  # Entrenamiento CLAM_MB, k=5 folds (main.py itera splits_0..4.csv).
  # Args bendecidos idénticos al 4109; solo cambian --k y --split_dir.
  "$PYBIN" main.py \
    --drop_out 0.25 \
    --lr 2e-4 \
    --bag_loss ce \
    --inst_loss svm \
    --model_type clam_mb \
    --embed_dim 512 \
    --k "$K" \
    --max_epochs 30 \
    --early_stopping \
    --weighted_sample \
    --auto-label-dict \
    --log_data \
    --B "$B" \
    --task "$TASK" \
    --split_dir "$SPLIT_DIR" \
    --data_root_dir "$ENVIRON" \
    --results_dir "$REPO/results/obj5_varianza_${TEJIDO}" \
    --exp_code "mc_var_${TEJIDO}_B${B}_k${K}_${RUN_TS}"

  echo "===== $TASK done ====="
done

echo ""
echo "Job $SLURM_JOB_ID done at $(date)"
echo "Results under $REPO/results/obj5_varianza_<tejido>/  (summary.csv con $K filas + mean/std)"
