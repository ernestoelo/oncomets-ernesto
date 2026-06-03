#!/bin/bash
#SBATCH --job-name=eg_mammoth_patinv
#SBATCH --partition=debug
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=16
#SBATCH --mem=32G
#SBATCH --time=48:00:00
#SBATCH --output=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/logs/%x_%j.out
#SBATCH --error=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/logs/%x_%j.err
#SBATCH --chdir=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto
# ============================================================
# Obj 2 B5 — Mammoth en CLAM: patrón arquitectónico (4 binarias) +
# invasión linfática (3 clases), k=5 PAIRED (CLAM vs CLAM+mammoth).
#
#   - Ambos brazos por el MISMO harness (scripts/train_dsmil.py), único delta
#     = --model_type {clam, clam_mammoth}. Misma config fija que microcalc (job
#     4229) → comparación real. Hipótesis pre-registrada:
#     sprints/B5_sprint5/objetivo_2_mammoth_patron_invasion/README.md
#   - Splits MC-CV propios bajo data/splits_kfold/<task>_100 (build_new_tasks_splits.py).
#   - Métricas: balanced_acc + AUC (binario; invasión = macro-OVR) + confusión + n.
#
# ESCALA: invasión (2814 slides) es ~8× más pesada por run que patrón (513).
# Para no monopolizar la GPU única, lanzar en OLAS separadas con GROUP:
#     GROUP=patron   sbatch scripts/run_obj2_mammoth_patron_invasion_kfold.slurm   # ~13h, 40 runs
#     GROUP=invasion sbatch scripts/run_obj2_mammoth_patron_invasion_kfold.slurm   # ~20-25h, 10 runs
#   (GROUP=all = default; corre las 5 tareas seguidas, ~38h — cabe en 48h pero
#    acapara la GPU; preferir las olas si hay jobs ajenos.)
# Brazo liviano (compara contra baseline ya computado): MODEL_TYPES="clam_mammoth".
#
# Lanzamiento SOLO con OK explícito de Ernesto (NO autónomo). Cortesía: squeue/sinfo.
# ============================================================

set -euo pipefail

REPO=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto
CLAM=/media/administrador/Storage1/sdonoso/clam_environ
ENVIRON="$CLAM/environ"
FEATURES_DIR="$ENVIRON/features/pt_files"
SPLITS_BASE="$REPO/data/splits_kfold"
CSV_NT="$REPO/data/csv_new_tasks"          # snapshots filtrados (slides con .pt)
B=8
K=5
RUN_TS=$(date +%Y%m%d_%H%M)                 # workaround C: re-run no pisa el previo
MODEL_TYPES="${MODEL_TYPES:-clam clam_mammoth}"
GROUP="${GROUP:-all}"                       # patron | invasion | all

source /home/sdonoso/miniconda3/etc/profile.d/conda.sh
conda activate clam_latest
PYBIN="$CONDA_PREFIX/bin/python"            # 'python' a secas ROTO (workaround B)

echo "Job ${SLURM_JOB_ID:-local} started at $(date) on $(hostname)  GROUP=$GROUP  brazos=$MODEL_TYPES"
"$PYBIN" -c "import torch; assert torch.cuda.is_available(), 'no CUDA'; print('torch', torch.__version__, 'cuda', torch.version.cuda)"
"$PYBIN" -c "import mammoth; print('mammoth OK:', mammoth.__file__)"
nvidia-smi | head -20 || true              # workaround D (head cierra el pipe -> SIGPIPE)

# Gate 1: verificador determinístico de splits (incluye las 5 tareas nuevas).
if ! "$PYBIN" "$REPO/scripts/verify_kfold_splits.py" ; then
  echo "VERIFY KFOLD FAILED — splits inconsistentes, abortar"; exit 1
fi
# Gate 2: tests CPU del modelo Mammoth (preflight de código, segundos).
if ! CUDA_VISIBLE_DEVICES="" "$PYBIN" "$REPO/tests/test_mammoth_cpu.py" ; then
  echo "TEST CPU MAMMOTH FAILED — port roto, abortar antes de gastar GPU"; exit 1
fi

run_task() {
  local TASK="$1" CSV="$2" NCLS="$3" LABELDICT="$4"
  local SPLIT_DIR="$SPLITS_BASE/${TASK}_100"
  local RESULTS_DIR="$REPO/results/obj2_mammoth/${TASK}"
  echo ""
  echo "===== TASK: $TASK  (n_classes=$NCLS, brazos: $MODEL_TYPES, k=$K) ====="

  # Preflight obligatorio (workaround G) por fold: ninguna slide de train con
  # n_patches < B (si no, torch.topk revienta inst_eval, bug 4096).
  for ((f=0; f<K; f++)); do
    if ! "$PYBIN" "$REPO/scripts/preflight_minpatch.py" \
        --split_dir "$SPLIT_DIR" --features_dir "$FEATURES_DIR" \
        --min_patches "$B" --fold "$f" ; then
      echo "PREFLIGHT FAILED en $TASK fold $f"; exit 1
    fi
  done

  for MT in $MODEL_TYPES; do
    echo ""
    echo "----- modelo: $MT -----"
    for ((f=0; f<K; f++)); do
      echo "  $TASK | $MT | fold $f / $((K-1))"
      CUDA_VISIBLE_DEVICES=0 "$PYBIN" "$REPO/scripts/train_dsmil.py" \
        --model_type    "$MT" \
        --task          "$TASK" \
        --exp_code      "${MT}_${TASK}_f${f}_${RUN_TS}" \
        --csv_path      "$CSV" \
        --data_root_dir "$ENVIRON" \
        --split_dir     "$SPLIT_DIR" \
        --results_dir   "$RESULTS_DIR" \
        --fold          "$f" \
        --n_classes     "$NCLS" \
        --max_epochs    30 \
        --early_stopping \
        --patience      20 \
        --stop_epoch    50 \
        --B             "$B" \
        --bag_weight    0.7 \
        --lr            2e-4 \
        --reg           1e-5 \
        --drop_out      0.25 \
        --embed_dim     512 \
        --seed          1 \
        --label_dict    "$LABELDICT"
    done
  done
  echo "===== $TASK done ====="
}

PA="dataset_carcinoma_ductal_in_situ_patrones_arquitectonicos"

if [ "$GROUP" = "patron" ] || [ "$GROUP" = "all" ]; then
  run_task cdis_patron_cribiforme_pth   "$CSV_NT/${PA}_cribiforme_label.csv"   2 '{"no": 0, "si": 1}'
  run_task cdis_patron_solido_pth       "$CSV_NT/${PA}_solido_label.csv"       2 '{"no": 0, "si": 1}'
  run_task cdis_patron_micropapilar_pth "$CSV_NT/${PA}_micropapilar_label.csv" 2 '{"no": 0, "si": 1}'
  run_task cdis_patron_papilar_pth      "$CSV_NT/${PA}_papilar_label.csv"      2 '{"no": 0, "si": 1}'
fi

if [ "$GROUP" = "invasion" ] || [ "$GROUP" = "all" ]; then
  run_task invasion_linfatica_vascular_pth \
           "$CSV_NT/dataset_invasion_linfovascular_label.csv" \
           3 '{"ausente": 0, "no_identificado": 1, "presente": 2}'
fi

echo ""
echo "Job ${SLURM_JOB_ID:-local} done at $(date)"
echo "Results under $REPO/results/obj2_mammoth/<task>/<modelo>_<task>_f<0..$((K-1))>_*_s1/"
echo "  (test_metrics.json: balanced_acc + AUC + confusión + n_test; test_predictions.csv: y_prob_<c>)"
