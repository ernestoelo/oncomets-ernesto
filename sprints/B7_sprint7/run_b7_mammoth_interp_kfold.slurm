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
# B7 — Mammoth (paired vs CLAM) en las 2 tareas del sprint 7 que HOY no tienen
# checkpoint mammoth: tipo_histologico y carcinoma_ductal_insitu_presente.
#
# DRAFT — NO LANZAR. Requiere 3 cosas ANTES del sbatch (ver "PREREQUISITOS"):
#   (1) decidir la FORMULACIÓN de cada tarea (n_classes, label_dict, cohorte) — Ernesto/Sebastián;
#   (2) generar splits_kfold + csv_new_tasks para esas 2 tareas (hoy NO existen);
#   (3) pase del reviewer (regla 9: hipótesis pre-registrada) + OK explícito de Ernesto (gate d/b).
#
# PROPÓSITO (importante, para el reviewer): este entrenamiento es un INSTRUMENTO de
# interpretabilidad, NO un experimento de rendimiento. El objetivo del sprint 7 es
# comparar los mapas de atención de CLAM vs los mapas de ruteo por experto de Mammoth
# (pedido de Sebastián). Para las tareas sin checkpoint mammoth hace falta entrenar uno
# y así poder correr scripts/mammoth_interpretability.py sobre él. NO se reclama que
# Mammoth mejore la métrica: eso está cerrado (Hallazgo 12, 0 palancas). El brazo CLAM
# paired da el mapa de atención de referencia para la comparación visual.
#
# Mismo harness que obj2 (scripts/train_dsmil.py), único delta = --model_type
# {clam, clam_mammoth}. Splits reusados/paired (patrón [[patron-paired-comparison-reuso-splits]]).
# ============================================================
#
# PREREQUISITOS (resolver antes de habilitar el sbatch) — hoy bloquean:
#
#  A. FORMULACIÓN (decisión de Ernesto/Sebastián, pre-registrar regla 9):
#     - carcinoma_ductal_insitu_presente: labels {no:636, no_identificado:1369, si:810}.
#       ¿binaria {no,si} excluyendo no_identificado (como los binarios de microcalc), o
#       3-clase? → fija n_classes y label_dict.
#     - tipo_histologico: la versión cruda tiene ~17 clases (muchas n=1..14). La entrenable
#       es dataset_tipo_histologico_4clases_label.csv {carcinoma_invasivo_tipo_no_especifico:766,
#       carcinoma_lobulillar_invasivo:183, no_identificado:366, otros:81}. ¿Se usa la de 4
#       clases? ¿se excluye no_identificado?
#     - Cohorte: ¿_pth (priv+TCGA+HistAI) para tener TCGA con WSI para los heatmaps, como
#       invasión? (recomendado: los heatmaps se hacen sobre WSIs TCGA con .svs disponible).
#
#  B. SPLITS + CSV (hoy NO existen para estas 2 tareas):
#     - data/splits_kfold/<task>_100/  → generar con el generador de splits k-fold del repo
#       (mismo que produjo los otros splits_kfold; ver scripts/verify_kfold_splits.py).
#     - data/csv_new_tasks/<...>_label.csv → snapshot filtrado (solo slides con .pt).
#     Ambos con la formulación de (A). Es un paso CPU (no GPU), pero es data-pipeline →
#     pre-registrar + reviewer antes de generarlos.
#
#  C. GOBERNANZA: reviewer (regla 9) + OK explícito de Ernesto + cortesía single-GPU.
#
# ============================================================

set -euo pipefail

REPO=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto
CLAM=/media/administrador/Storage1/sdonoso/clam_environ
ENVIRON="$CLAM/environ"
FEATURES_DIR="$ENVIRON/features/pt_files"
SPLITS_BASE="$REPO/data/splits_kfold"
CSV_NT="$REPO/data/csv_new_tasks"
B=8
K=5
RUN_TS=$(date +%Y%m%d_%H%M)
MODEL_TYPES="${MODEL_TYPES:-clam clam_mammoth}"   # brazo liviano: MODEL_TYPES="clam_mammoth"
GROUP="${GROUP:-all}"                             # tipo | cdis | all

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
  local TASK="$1" CSV="$2" NCLS="$3" LABELDICT="$4"
  local SPLIT_DIR="$SPLITS_BASE/${TASK}_100"
  local RESULTS_DIR="$REPO/results/b7_mammoth_interp/${TASK}"

  # PREREQUISITO B: sin splits generados, abortar limpio (no correr a ciegas).
  if [ ! -d "$SPLIT_DIR" ]; then
    echo "SPLITS AUSENTES: $SPLIT_DIR no existe → generar splits_kfold + csv antes (prereq B). ABORTA."
    exit 1
  fi
  if [ ! -f "$CSV" ]; then
    echo "CSV AUSENTE: $CSV no existe (prereq B). ABORTA."; exit 1
  fi

  echo ""
  echo "===== TASK: $TASK  (n_classes=$NCLS, brazos: $MODEL_TYPES, k=$K) ====="

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
        --max_epochs    30 \
        --early_stopping --patience 20 --stop_epoch 50 \
        --B "$B" --bag_weight 0.7 --lr 2e-4 --reg 1e-5 --drop_out 0.25 \
        --embed_dim 512 --seed 1 \
        --label_dict "$LABELDICT"
    done
  done
  echo "===== $TASK done ====="
}

# ---- Parametrización DRAFT (n_classes/label_dict/CSV = PENDIENTE de decisión, prereq A) ----
# Los valores de abajo son PLACEHOLDERS con la formulación recomendada; confirmar antes de usar.

if [ "$GROUP" = "tipo" ] || [ "$GROUP" = "all" ]; then
  # recomendado: 4 clases (versión _4clases limpia). Confirmar si se excluye no_identificado.
  run_task tipo_histologico_4clases_pth \
           "$CSV_NT/dataset_tipo_histologico_4clases_label.csv" \
           4 '{"carcinoma_invasivo_tipo_no_especifico": 0, "carcinoma_lobulillar_invasivo": 1, "no_identificado": 2, "otros": 3}'
fi

if [ "$GROUP" = "cdis" ] || [ "$GROUP" = "all" ]; then
  # recomendado: binaria {no,si} excluyendo no_identificado (como los binarios de microcalc).
  # Si se decide 3-clase, cambiar NCLS=3 y el label_dict + el CSV (sin excluir).
  run_task carcinoma_ductal_insitu_presente_bin_pth \
           "$CSV_NT/dataset_carcinoma_ductal_in_situ_presente_bin_label.csv" \
           2 '{"no": 0, "si": 1}'
fi

echo ""
echo "Job ${SLURM_JOB_ID:-local} done at $(date)"
echo "Checkpoints bajo $REPO/results/b7_mammoth_interp/<task>/<modelo>_<task>_f<0..$((K-1))>_*_s1/"
echo "Siguiente paso: correr scripts/mammoth_interpretability.py sobre el checkpoint clam_mammoth de cada task."
