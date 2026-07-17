#!/bin/bash
#SBATCH --job-name=eg_b7_mammoth_interp
#SBATCH --partition=debug
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=16
#SBATCH --mem=32G
#SBATCH --time=48:00:00
#SBATCH --output=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/logs/%x_%j.out
#SBATCH --error=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/logs/%x_%j.err
#SBATCH --chdir=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto
# ============================================================
# B7 — Mammoth (paired vs CLAM) en las 3 tareas del sprint 7 para la comparación
# de interpretabilidad CLAM vs Mammoth: tipo_histologico, CDIS presente e invasión
# linfovascular (LVI). Se re-entrenan las 3 sobre FEATURES ACTUALES (drift 26-27 jun,
# [[features-tcga-drift-reextraccion]]) con la formulación decidida por Sebastián
# (17-jul, cascada gate invasivo + reformulación CDIS/LVI).
#
# PROPÓSITO (para el reviewer): este entrenamiento es un INSTRUMENTO de
# interpretabilidad, NO un experimento de rendimiento. El objetivo del sprint 7 es
# comparar los mapas de atención de CLAM vs los mapas de ruteo por experto/slot de
# Mammoth (pedido de Sebastián). Para cada tarea se entrena un checkpoint CLAM y uno
# Mammoth PAIRED (mismo split por fold, [[patron-paired-comparison-reuso-splits]]) y
# luego se corre scripts/mammoth_interpretability.py sobre el checkpoint clam_mammoth.
# NO se reclama que Mammoth mejore la métrica: eso está CERRADO (Hallazgo 12, 0 palancas).
# El brazo CLAM paired da el mapa de atención de referencia para la comparación visual.
#
# Régimen de training = args bendecidos + early stopping (idéntico a B6 multiescala y a
# los baselines): max_epochs 200, early_stopping patience 20 stop_epoch 50, B 8,
# bag_weight 0.7, lr 2e-4, reg 1e-5, drop_out 0.25, embed_dim 512, seed 1. Harness
# scripts/train_dsmil.py, único delta entre brazos = --model_type {clam, clam_mammoth}.
#
# FORMULACIÓN (fijada; snapshots CSV filtrados en data/csv_new_tasks/):
#   - tipo_histologico: 3 clases (no_identificado excluido por el gate). Reusa el split
#     _ci de Sebastián (READ-ONLY, environ/splits_5fold_balance_ci/...4clases_ci_100).
#   - CDIS presente: binaria {no,si}, invasivas ∩ explícitos. Split _ci_reform (nuestro).
#   - LVI (invasión linfovascular): binaria {ausente,presente}, invasivas ∩ explícitos.
#     Split _ci_reform (nuestro). n=836 balanceado.
#
# GATES antes del sbatch: reviewer (regla 9, hipótesis pre-registrada) + OK de Ernesto +
# GPU libre (cortesía single-GPU). Preflight obligatorio por fold (workaround G).
# ============================================================

set -euo pipefail

REPO=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto
CLAM=/media/administrador/Storage1/sdonoso/clam_environ
ENVIRON="$CLAM/environ"
FEATURES_DIR="$ENVIRON/features/pt_files"
SPLITS_BASE="$REPO/data/splits_kfold"
CSV_NT="$REPO/data/csv_new_tasks"
CI_BASE="$ENVIRON/splits_5fold_balance_ci"   # splits _ci de Sebastián (READ-ONLY)
B=8
K=5
RUN_TS=$(date +%Y%m%d_%H%M)
MODEL_TYPES="${MODEL_TYPES:-clam clam_mammoth}"   # brazo liviano: MODEL_TYPES="clam_mammoth"
GROUP="${GROUP:-all}"                             # tipo | cdis | lvi | all

source /home/sdonoso/miniconda3/etc/profile.d/conda.sh
conda activate clam_latest
PYBIN="$CONDA_PREFIX/bin/python"                  # workaround B: 'python' a secas ROTO

echo "Job ${SLURM_JOB_ID:-local} started at $(date) on $(hostname)  GROUP=$GROUP  brazos=$MODEL_TYPES"
"$PYBIN" -c "import torch; assert torch.cuda.is_available(), 'no CUDA'; print('torch', torch.__version__)"
"$PYBIN" -c "import mammoth; print('mammoth OK:', mammoth.__file__)"
nvidia-smi | head -20 || true                     # workaround D

# Gate CPU del modelo (segundos) — preflight de código antes de gastar GPU.
if ! CUDA_VISIBLE_DEVICES="" "$PYBIN" "$REPO/tests/test_mammoth_cpu.py" ; then
  echo "TEST CPU MAMMOTH FAILED — abortar"; exit 1
fi

run_task() {
  local TASK="$1" CSV="$2" NCLS="$3" LABELDICT="$4" SPLIT_DIR="$5"
  local RESULTS_DIR="$REPO/results/b7_mammoth_interp/${TASK}"

  if [ ! -d "$SPLIT_DIR" ]; then
    echo "SPLITS AUSENTES: $SPLIT_DIR no existe. ABORTA."; exit 1
  fi
  if [ ! -f "$CSV" ]; then
    echo "CSV AUSENTE: $CSV no existe. ABORTA."; exit 1
  fi

  echo ""
  echo "===== TASK: $TASK  (n_classes=$NCLS, brazos: $MODEL_TYPES, k=$K) ====="
  echo "       split_dir=$SPLIT_DIR"
  echo "       csv=$CSV"

  # Preflight obligatorio (workaround G) por fold.
  for ((f=0; f<K; f++)); do
    if ! "$PYBIN" "$REPO/scripts/preflight_minpatch.py" \
        --split_dir "$SPLIT_DIR" --features_dir "$FEATURES_DIR" \
        --min_patches "$B" --fold "$f" ; then
      echo "PREFLIGHT FAILED en $TASK fold $f"; exit 1
    fi
  done

  for MT in $MODEL_TYPES; do
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
        --max_epochs    200 \
        --early_stopping --patience 20 --stop_epoch 50 \
        --B "$B" --bag_weight 0.7 --lr 2e-4 --reg 1e-5 --drop_out 0.25 \
        --embed_dim 512 --seed 1 \
        --label_dict "$LABELDICT"
    done
  done
  echo "===== $TASK done ====="
}

# ---- Parametrización FIJADA (formulación de Sebastián + snapshots verificados) ----

if [ "$GROUP" = "tipo" ] || [ "$GROUP" = "all" ]; then
  # 3 clases (no_identificado excluido por el gate). Split _ci de Sebastián (read-only).
  run_task tipo_histologico_3clases_ci \
           "$CSV_NT/dataset_tipo_histologico_3clases_ci_label.csv" \
           3 '{"carcinoma_invasivo_tipo_no_especifico": 0, "carcinoma_lobulillar_invasivo": 1, "otros": 2}' \
           "$CI_BASE/tipo_histologico_4clases_ci_100"
fi

if [ "$GROUP" = "cdis" ] || [ "$GROUP" = "all" ]; then
  # binaria {no,si}, invasivas ∩ explícitos (85% positivo, aceptado por Sebastián).
  run_task carcinoma_ductal_insitu_presente_ci_reform \
           "$CSV_NT/dataset_carcinoma_ductal_insitu_presente_ci_reform_label.csv" \
           2 '{"no": 0, "si": 1}' \
           "$SPLITS_BASE/carcinoma_ductal_insitu_presente_ci_reform_100"
fi

if [ "$GROUP" = "lvi" ] || [ "$GROUP" = "all" ]; then
  # binaria {ausente,presente}, invasivas ∩ explícitos (balanceado, n=836).
  run_task invasion_linfatica_vascular_ci_reform \
           "$CSV_NT/dataset_invasion_linfatica_vascular_ci_reform_label.csv" \
           2 '{"ausente": 0, "presente": 1}' \
           "$SPLITS_BASE/invasion_linfatica_vascular_ci_reform_100"
fi

echo ""
echo "Job ${SLURM_JOB_ID:-local} done at $(date)"
echo "Checkpoints bajo $REPO/results/b7_mammoth_interp/<task>/<modelo>_<task>_f<0..$((K-1))>_*_s1/"
echo "Siguiente paso: correr scripts/mammoth_interpretability.py sobre el checkpoint clam_mammoth de cada task."
