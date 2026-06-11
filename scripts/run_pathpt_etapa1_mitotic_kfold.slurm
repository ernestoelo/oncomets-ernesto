#!/bin/bash
#SBATCH --job-name=eg_pathpt_mitotic
#SBATCH --partition=debug
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=16
#SBATCH --mem=48G
#SBATCH --time=18:00:00
#SBATCH --output=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/logs/%x_%j.out
#SBATCH --error=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/logs/%x_%j.err
#SBATCH --chdir=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto
# ============================================================
# Etapa 1 B5 — PathPT-CONCH vs CLAM en TASA MITÓTICA 3-clase ordinal, k=5 PAIRED.
#
#   - 2 brazos con DRIVERS DISTINTOS sobre los MISMOS splits (paired por construcción):
#       CLAM   = scripts/train_dsmil.py --model_type clam --n_classes 3   (baseline)
#       PathPT = scripts/train_pathpt.py --task mitotic --n_classes 3      (θ_v + θ_t)
#     Ambos producen el MISMO schema → Δ pareado 1:1 por fold (bal_acc + macro-OVR AUC).
#   - Pre-registración (regla 9, reviewer): sprints/B5_sprint5/pathpt/etapa1_prereg_mitotic.md
#   - Splits MC-CV propios: data/splits_kfold/grado_mitotic_3clases_pth_100 (build_mitotic_splits.py)
#   - 3 clases ordinales: score_1(0)/score_2(1)/score_3(2). Clase 0 = basal ordinal (prereg §3.1).
#   - Métrica (política B5): balanced_acc + macro-OVR AUC + confusión 3×3 + n. Δ pareado por fold.
#   - Tamaño ~3× necrosis (1177 vs 396) → estimado ~6–8 h; --time 18h con margen.
#
# Control de brazos:  ARMS="clam pathpt" (default) | ARMS="pathpt" (solo PathPT).
# Lanzamiento SOLO con OK de Ernesto. Cortesía single-GPU: squeue/sinfo antes.
# ============================================================

set -euo pipefail

REPO=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto
CLAM=/media/administrador/Storage1/sdonoso/clam_environ
ENVIRON="$CLAM/environ"
FEATURES_DIR="$ENVIRON/features/pt_files"

TASK=grado_mitotic_3clases_pth
SPLIT_DIR="$REPO/data/splits_kfold/${TASK}_100"
CSV="$REPO/data/csv_new_tasks/dataset_grado_mitotic_3clases_label.csv"
RESULTS_DIR="$REPO/results/pathpt_etapa1/mitotic"
LABELDICT='{"score_1": 0, "score_2": 1, "score_3": 2}'
NCLS=3
K=5
B=8
RUN_TS=$(date +%Y%m%d_%H%M)
ARMS="${ARMS:-clam pathpt}"

source /home/sdonoso/miniconda3/etc/profile.d/conda.sh
conda activate clam_latest
PYBIN="$CONDA_PREFIX/bin/python"             # 'python' a secas ROTO (workaround B)

echo "Job ${SLURM_JOB_ID:-local} started at $(date) on $(hostname)  brazos=$ARMS  task=$TASK"
"$PYBIN" -c "import torch; assert torch.cuda.is_available(), 'no CUDA'; print('torch', torch.__version__, 'cuda', torch.version.cuda)"
nvidia-smi | head -20 || true               # workaround D (head cierra el pipe -> SIGPIPE)

# ---- Preflight (workaround G): falla en segundos, no tras horas ----
# Gate 1: verificador determinístico de splits (incluye grado_mitotic_3clases_pth_100).
if ! "$PYBIN" "$REPO/scripts/verify_kfold_splits.py" ; then
  echo "VERIFY KFOLD FAILED — splits inconsistentes, abortar"; exit 1
fi
# Gate 2: test CPU del port PathPT (incluye los casos multiclase 3-clase).
if ! CUDA_VISIBLE_DEVICES="" PYTHONPATH=/media/administrador/Storage1/sdonoso/clam_testing2/.pylibs \
     "$PYBIN" "$REPO/tests/test_pathpt_cpu.py" ; then
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
  echo ""; echo "===== BRAZO CLAM (train_dsmil.py --model_type clam, 3 clases) ====="
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

# ---- Brazo PathPT (θ_v + θ_t, multiclase) ----
if [[ " $ARMS " == *" pathpt "* ]]; then
  echo ""; echo "===== BRAZO PathPT (train_pathpt.py --task mitotic, 3 clases) ====="
  for ((f=0; f<K; f++)); do
    echo "  PathPT | fold $f / $((K-1))"
    CUDA_VISIBLE_DEVICES=0 "$PYBIN" "$REPO/scripts/train_pathpt.py" \
      --task          mitotic \
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
echo "  (test_metrics.json: balanced_acc + macro-OVR AUC + confusión 3×3 + n; Δ pareado por fold + confusión pooled)"
