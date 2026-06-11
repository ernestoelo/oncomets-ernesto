#!/bin/bash
#SBATCH --job-name=eg_pathpt_necrosis
#SBATCH --partition=debug
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=16
#SBATCH --mem=48G
#SBATCH --time=12:00:00
#SBATCH --output=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/logs/%x_%j.out
#SBATCH --error=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/logs/%x_%j.err
#SBATCH --chdir=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto
# ============================================================
# Etapa 1 B5 — PathPT-CONCH vs CLAM en NECROSIS binaria, k=5 PAIRED.
#
#   - 2 brazos con DRIVERS DISTINTOS sobre los MISMOS splits (paired por construcción):
#       CLAM   = scripts/train_dsmil.py --model_type clam   (baseline)
#       PathPT = scripts/train_pathpt.py                    (θ_v + θ_t, harness propio)
#     Ambos producen el MISMO schema (summary.csv, test_metrics.json,
#     split_<f>_results.pkl, test_predictions.csv) → Δ pareado 1:1 por fold.
#   - Pre-registración (regla 9, reviewer GO): sprints/B5_sprint5/pathpt/etapa1_prereg_necrosis.md
#   - Splits MC-CV propios: data/splits_kfold/cdis_necrosis_2clases_pth_100 (build_necrosis_splits.py)
#   - Métricas: balanced_acc + AUC + confusión + n (política B5). Δ pareado por fold + confusión pooled.
#
# Control de brazos (para correr uno solo si el otro baseline ya existe):
#     ARMS="clam pathpt" sbatch ...   (default; corre ambos)
#     ARMS="pathpt"      sbatch ...   (solo PathPT)
#
# Lanzamiento SOLO con OK explícito de Ernesto (NO autónomo). Cortesía: squeue/sinfo
# antes (GPU única). PathPT necesita nystrom_attention (clam_testing2/.pylibs; el driver
# lo agrega a sys.path solo, y torch viene de clam_latest).
# ============================================================

set -euo pipefail

REPO=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto
CLAM=/media/administrador/Storage1/sdonoso/clam_environ
ENVIRON="$CLAM/environ"
FEATURES_DIR="$ENVIRON/features/pt_files"

TASK=cdis_necrosis_2clases_pth
SPLIT_DIR="$REPO/data/splits_kfold/${TASK}_100"
CSV="$REPO/data/csv_new_tasks/dataset_cdis_necrosis_2clases_label.csv"
RESULTS_DIR="$REPO/results/pathpt_etapa1/necrosis"
LABELDICT='{"no": 0, "si": 1}'
NCLS=2
K=5
B=8
RUN_TS=$(date +%Y%m%d_%H%M)                  # workaround C: re-run no pisa el previo
ARMS="${ARMS:-clam pathpt}"

source /home/sdonoso/miniconda3/etc/profile.d/conda.sh
conda activate clam_latest
PYBIN="$CONDA_PREFIX/bin/python"             # 'python' a secas ROTO (workaround B)

echo "Job ${SLURM_JOB_ID:-local} started at $(date) on $(hostname)  brazos=$ARMS  task=$TASK"
"$PYBIN" -c "import torch; assert torch.cuda.is_available(), 'no CUDA'; print('torch', torch.__version__, 'cuda', torch.version.cuda)"
nvidia-smi | head -20 || true               # workaround D (head cierra el pipe -> SIGPIPE)

# ---- Preflight (workaround G): falla en segundos, no tras horas ----
# Gate 1: verificador determinístico de splits (incluye cdis_necrosis_2clases_pth_100).
if ! "$PYBIN" "$REPO/scripts/verify_kfold_splits.py" ; then
  echo "VERIFY KFOLD FAILED — splits inconsistentes, abortar"; exit 1
fi
# Gate 2: test CPU del port PathPT (wiring θ_v/θ_t, loss, modelo+gradiente).
if ! CUDA_VISIBLE_DEVICES="" "$PYBIN" "$REPO/tests/test_pathpt_cpu.py" ; then
  echo "TEST CPU PATHPT FAILED — port roto, abortar antes de gastar GPU"; exit 1
fi
# Gate 3: minpatch por fold para el brazo CLAM (inst_eval topk revienta si n_patches<B).
for ((f=0; f<K; f++)); do
  if ! "$PYBIN" "$REPO/scripts/preflight_minpatch.py" \
      --split_dir "$SPLIT_DIR" --features_dir "$FEATURES_DIR" \
      --min_patches "$B" --fold "$f" ; then
    echo "PREFLIGHT MINPATCH FAILED en fold $f"; exit 1
  fi
done

# ---- Brazo CLAM (baseline) ----
if [[ " $ARMS " == *" clam "* ]]; then
  echo ""; echo "===== BRAZO CLAM (train_dsmil.py --model_type clam) ====="
  for ((f=0; f<K; f++)); do
    echo "  CLAM | fold $f / $((K-1))"
    CUDA_VISIBLE_DEVICES=0 "$PYBIN" "$REPO/scripts/train_dsmil.py" \
      --model_type    clam \
      --task          "$TASK" \
      --exp_code      "clam_${TASK}_f${f}_${RUN_TS}" \
      --csv_path      "$CSV" \
      --data_root_dir "$ENVIRON" \
      --split_dir     "$SPLIT_DIR" \
      --results_dir   "$RESULTS_DIR" \
      --fold          "$f" \
      --n_classes     "$NCLS" \
      --max_epochs    30 --early_stopping --patience 20 --stop_epoch 50 \
      --B "$B" --bag_weight 0.7 --lr 2e-4 --reg 1e-5 --drop_out 0.25 \
      --embed_dim 512 --seed 1 --label_dict "$LABELDICT"
  done
fi

# ---- Brazo PathPT (θ_v + θ_t) ----
if [[ " $ARMS " == *" pathpt "* ]]; then
  echo ""; echo "===== BRAZO PathPT (train_pathpt.py) ====="
  for ((f=0; f<K; f++)); do
    echo "  PathPT | fold $f / $((K-1))"
    CUDA_VISIBLE_DEVICES=0 "$PYBIN" "$REPO/scripts/train_pathpt.py" \
      --task          necrosis \
      --exp_code      "pathpt_${TASK}_f${f}_${RUN_TS}" \
      --csv_path      "$CSV" \
      --data_root_dir "$ENVIRON" \
      --split_dir     "$SPLIT_DIR" \
      --results_dir   "$RESULTS_DIR" \
      --fold          "$f" \
      --n_classes     "$NCLS" \
      --epochs 20 --lr 1e-4 --n_ctx 32 \
      --prompt_num 200 --select_num 100 \
      --seed 1 --label_dict "$LABELDICT"
  done
fi

echo ""
echo "Job ${SLURM_JOB_ID:-local} done at $(date)"
echo "Results under $RESULTS_DIR/{clam,pathpt}_${TASK}_f<0..$((K-1))>_${RUN_TS}_s1/"
echo "  (test_metrics.json: balanced_acc + AUC + confusión + n; analizar Δ pareado por fold + confusión pooled)"
