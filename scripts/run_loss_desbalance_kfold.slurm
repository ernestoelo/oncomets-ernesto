#!/bin/bash
#SBATCH --job-name=eg_loss_desbalance
#SBATCH --partition=debug
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=16
#SBATCH --mem=32G
#SBATCH --time=48:00:00
#SBATCH --output=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/logs/%x_%j.out
#SBATCH --error=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/logs/%x_%j.err
#SBATCH --chdir=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto
# ============================================================
# Loss de desbalance B5 — CLAM_MB + {focal, class_balanced} vs CLAM_MB + CE.
# Eje C1 (desbalance). NO es swap de arquitectura: el modelo es CLAM_MB intacto,
# el único delta es la bag loss (--bag_loss). Paired vs el baseline CLAM+CE YA en
# disco (mismos splits/seed/hiperparámetros → Δ pareado por fold).
#
#   Pre-registración (regla 9 + reviewer GO-con-obs):
#     sprints/B5_sprint5/loss_desbalance/prereg.md
#
#   BRAZOS (solo CLAM; el baseline CLAM+CE NO se re-corre):
#     - focal : --bag_loss focal           (γ=2.0, sin α; focusing ortogonal al sampler)
#     - cb    : --bag_loss class_balanced  (pesos número efectivo Cui 2019, β=0.9999)
#   Δ pareado: C_focal = focal − CE ; C_cb = cb − CE (mismo baseline en disco).
#
#   Baselines CLAM+CE (brazo clam_*), paired por construcción:
#     invasion  : results/obj2_mammoth/invasion_linfatica_vascular_pth/
#     carcinoma : results/obj6_mammoth_binarias_carcinoma_invasivo/
#     cdis      : results/obj6_mammoth_binarias_cdis/
#     tejido    : results/obj6_mammoth_binarias_tejido_no_neoplasico/
#
#   TAREAS (mismos splits y CSVs que los baselines):
#     binarias : microcalc en carcinoma / cdis / tejido (n=328 c/u). LIGERAS.
#     invasion : invasión linfática vascular, 3 clases (n=2814). PESADA (~8×/run).
#
# ESCALA: 4 tareas × 2 brazos × 5 folds = 40 runs. Lanzar en OLAS — la PRUDENTE primero:
#     GROUP=binarias sbatch scripts/run_loss_desbalance_kfold.slurm   # ligero, valida pipeline
#     GROUP=invasion sbatch scripts/run_loss_desbalance_kfold.slurm   # pesado, con GPU libre
#   (GROUP=all = default; corre las dos olas seguidas.)
#
# Lanzamiento SOLO con OK explícito de Ernesto (NO autónomo). Antes: squeue/sinfo
# (cortesía single-GPU; si hay jobs ajenos pendientes por Resources, esperar).
# ============================================================

set -euo pipefail

REPO=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto
CLAM=/media/administrador/Storage1/sdonoso/clam_environ
ENVIRON="$CLAM/environ"
FEATURES_DIR="$ENVIRON/features/pt_files"
SPLITS_BASE="$REPO/data/splits_kfold"
CSV_NT="$REPO/data/csv_new_tasks"          # snapshot de invasión (slides con .pt)
CSV_RO="$ENVIRON/csv"                       # CSVs binarios read-only de Sebastián
B=8
K=5
RUN_TS=$(date +%Y%m%d_%H%M)                 # workaround C: re-run no pisa el previo
ARMS="${ARMS:-focal cb}"                    # focal | cb | "focal cb"
GROUP="${GROUP:-all}"                       # binarias | invasion | all

source /home/sdonoso/miniconda3/etc/profile.d/conda.sh
conda activate clam_latest
PYBIN="$CONDA_PREFIX/bin/python"            # 'python' a secas ROTO (workaround B)

echo "Job ${SLURM_JOB_ID:-local} started at $(date) on $(hostname)  GROUP=$GROUP  brazos=$ARMS"
"$PYBIN" -c "import torch; assert torch.cuda.is_available(), 'no CUDA'; print('torch', torch.__version__, 'cuda', torch.version.cuda)"
nvidia-smi | head -20 || true              # workaround D (head cierra el pipe -> SIGPIPE)

# Gate 1: verificador determinístico de splits.
if ! "$PYBIN" "$REPO/scripts/verify_kfold_splits.py" ; then
  echo "VERIFY KFOLD FAILED — splits inconsistentes, abortar"; exit 1
fi
# Gate 2: tests CPU de las bag losses (ce==CE, focal(γ=0)==CE, pesos CB correctos).
if ! CUDA_VISIBLE_DEVICES="" "$PYBIN" "$REPO/tests/test_loss_cpu.py" ; then
  echo "TEST CPU LOSS FAILED — abortar antes de gastar GPU"; exit 1
fi

# Flags extra por brazo (el delta vs el baseline CLAM+CE).
arm_flags() {
  case "$1" in
    focal) echo "--bag_loss focal --focal_gamma 2.0" ;;
    cb)    echo "--bag_loss class_balanced --cb_beta 0.9999" ;;
    *)     echo "ARM desconocido: $1" >&2; exit 1 ;;
  esac
}

run_task() {
  local TASK="$1" CSV="$2" NCLS="$3" LABELDICT="$4"
  local SPLIT_DIR="$SPLITS_BASE/${TASK}_100"
  local RESULTS_DIR="$REPO/results/loss_desbalance/${TASK}"
  echo ""
  echo "===== TASK: $TASK  (n_classes=$NCLS, brazos: $ARMS, k=$K) ====="

  # Preflight obligatorio (workaround G) por fold: ninguna slide de train con
  # n_patches < B (bug topk en inst_eval de CLAM con --weighted_sample).
  for ((f=0; f<K; f++)); do
    if ! "$PYBIN" "$REPO/scripts/preflight_minpatch.py" \
        --split_dir "$SPLIT_DIR" --features_dir "$FEATURES_DIR" \
        --min_patches "$B" --fold "$f" ; then
      echo "PREFLIGHT FAILED en $TASK fold $f"; exit 1
    fi
  done

  for ARM in $ARMS; do
    local EXTRA; EXTRA="$(arm_flags "$ARM")"
    echo ""
    echo "----- brazo: $ARM  ($EXTRA) -----"
    for ((f=0; f<K; f++)); do
      echo "  $TASK | $ARM | fold $f / $((K-1))"
      CUDA_VISIBLE_DEVICES=0 "$PYBIN" "$REPO/scripts/train_dsmil.py" \
        --model_type    clam \
        --task          "$TASK" \
        --exp_code      "${ARM}_${TASK}_f${f}_${RUN_TS}" \
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
        --label_dict    "$LABELDICT" \
        $EXTRA
    done
  done
  echo "===== $TASK done ====="
}

if [ "$GROUP" = "binarias" ] || [ "$GROUP" = "all" ]; then
  run_task microcalcificaciones_en_carcinoma_invasivo_pth \
           "$CSV_RO/dataset_microcalcificaciones_en_carcinoma_invasivo_label.csv" \
           2 '{"no": 0, "si": 1}'
  run_task microcalcificaciones_en_cdis_pth \
           "$CSV_RO/dataset_microcalcificaciones_en_cdis_label.csv" \
           2 '{"no": 0, "si": 1}'
  run_task microcalcificaciones_en_tejido_no_neoplasico_pth \
           "$CSV_RO/dataset_microcalcificaciones_en_tejido_no_neoplasico_label.csv" \
           2 '{"no": 0, "si": 1}'
fi

if [ "$GROUP" = "invasion" ] || [ "$GROUP" = "all" ]; then
  run_task invasion_linfatica_vascular_pth \
           "$CSV_NT/dataset_invasion_linfovascular_label.csv" \
           3 '{"ausente": 0, "no_identificado": 1, "presente": 2}'
fi

echo ""
echo "Job ${SLURM_JOB_ID:-local} done at $(date)"
echo "Results under $REPO/results/loss_desbalance/<task>/<arm>_<task>_f<0..$((K-1))>_*_s1/"
echo "  (test_metrics.json: balanced_acc + AUC + confusión + n_test; test_predictions.csv: y_prob_<c>)"
echo "  Paired: C_focal = focal − CE, C_cb = cb − CE (baselines clam_* en results/obj2_mammoth, results/obj6_*)"
