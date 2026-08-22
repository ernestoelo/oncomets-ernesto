#!/bin/bash
#SBATCH --job-name=eg_b3_gate_clam
#SBATCH --output=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/logs/%x_%j.out
#SBATCH --error=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/logs/%x_%j.err
#SBATCH --chdir=/media/administrador/Storage1/sdonoso/clam_testing
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=16
#SBATCH --mem=32G
#SBATCH --time=4:00:00
# (sin --partition -> usa la default 'debug')
#
# ==============================================================================
# B3 — CLAM PLANO del gate de carcinoma invasivo, SOLO fold 0
#
# Pre-registro (regla 9, leer ANTES de tocar esto):
#   sprints/B8_sprint8/hovernext_129741/prereg_gate_invasivo.md
# Plan: sprints/B8_sprint8/encargos_sebastian/plan.md §B3 + ADDENDUM 21-ago
#
# QUE ES: el brazo que falta del encargo 1 de Sebastian. El unico checkpoint del
# gate que hay en disco es MAMMOTH (su experiment.txt dice clam_mb y es falso).
# Esto entrena el CLAM plano sobre el MISMO split para que la comparacion del
# encargo quede CLAM contra CLAM.
#
# POR QUE clam_testing Y NO clam_environ (no es plomeria, es el pareado):
#   los dos arboles divergieron (main.py 885 lineas vs 750; core_utils ~1000 de
#   diff; model_clam ~312). El brazo Mammoth salio de clam_testing/main.py
#   --use_mammoth (run_mammoth_5fold_balanced.slurm). Correrlo desde clam_environ
#   cambiaria el modelo Y el bucle a la vez, que es lo que P1 existe para evitar.
#   La corrida pareada es ESE MISMO archivo SIN el flag: unico delta la 1a capa
#   (models/model_clam.py:303 nn.Linear vs :284-300 MammothPatchEmbed).
#
# --chdir a clam_testing porque el csv_path de TASK_CONFIGS se resuelve relativo
# al CWD. Su environ/ es un SYMLINK a clam_environ/environ (el CSV canonico).
# NO se escribe nada ahi: main.py y core_utils.py escriben solo bajo results_dir.
#
# Workarounds aplicados: B (binario absoluto), D (set -uo sin -e, head||true),
# G (preflight antes de la GPU), H-al-reves (md5 del arbol ajeno), L (--time real).
# ==============================================================================

set -uo pipefail   # SIN -e: workaround D (un `cmd | head` daria exit 141)

# ── Rutas ─────────────────────────────────────────────────────────────────────
PY="/home/sdonoso/miniconda3/envs/clam_latest/bin/python"      # workaround B
REPO="/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto"
PROJECT_DIR="/media/administrador/Storage1/sdonoso/clam_testing"
DATA_ROOT="/media/administrador/Storage1/sdonoso/clam_environ/environ"

TASK="invasion_carcinoma_gate_pth_balance"
SPLIT_DIR="${DATA_ROOT}/splits_5fold_balanced/${TASK}_100"
EXP_CODE="${TASK}_clam_fold0"
RESULTS_DIR="${REPO}/results/b8_gate_invasivo"
PROV="${RESULTS_DIR}/procedencia_${SLURM_JOB_ID:-NA}.txt"

# Config IDENTICA al brazo Mammoth de sgaete, salvo --use_mammoth (ausente).
K=5; K_START=0; K_END=1        # -> folds = [0]; el resumen sale summary_partial_0_1.csv
MODEL_TYPE="clam_mb"; EMBED_DIM=512
LR="2e-4"; DROP="0.25"; REG="1e-5"; MAX_EPOCHS=30; SEED=1
B_INST=8                       # default de main.py; el preflight usa este mismo valor

echo "========================================"
echo "B3 — CLAM plano, gate de invasivo, fold 0"
echo "  job        = ${SLURM_JOB_ID:-NA} en $(hostname)"
echo "  inicio     = $(date -Is)"
echo "  PY         = ${PY}"
echo "  CWD        = $(pwd)"
echo "  SPLIT_DIR  = ${SPLIT_DIR}"
echo "  RESULTS    = ${RESULTS_DIR}"
echo "========================================"

# main.py usa os.mkdir (no makedirs) => el padre tiene que existir.
mkdir -p "${RESULTS_DIR}" "${REPO}/logs" || exit 1

# GUARD contra re-corrida sobre un directorio ya usado. NO es paranoia:
#   - main.py:854-859 reusa el dir existente sin chistar (os.mkdir con guarda if-not-isdir)
#   - los checkpoints y el summary se SOBREESCRIBEN, pero
#   - save_probability_records (core_utils.py:157-168) hace pd.read_csv del archivo viejo y
#     CONCATENA => val_slide_probabilities_fold_0.csv quedaria con las filas de las dos
#     corridas mezcladas, y nada lo señalaria.
# Un run abortado y relanzado dejaria el dir mitad viejo mitad nuevo. Mejor fallar acá.
if [ -d "${RESULTS_DIR}/${EXP_CODE}_s${SEED}" ]; then
    echo "ABORTA: ${RESULTS_DIR}/${EXP_CODE}_s${SEED} ya existe."
    echo "  Una re-corrida CONCATENA los probability_logs sobre los viejos sin avisar."
    echo "  Mové o borrá el directorio a mano, o cambiá EXP_CODE, y volvé a lanzar."
    exit 1
fi

# ── Procedencia: workaround H AL REVES ────────────────────────────────────────
# clam_testing/ es arbol COMPARTIDO y vivo. Si alguien edita estos tres archivos
# mientras el job corre, le cambia el piso. Se registra md5+mtime al lanzar y al
# terminar; si cambiaron, el run queda marcado SOSPECHOSO en vez de pasar por bueno.
TRACKED=("main.py" "utils/core_utils.py" "models/model_clam.py")
{
  echo "# Procedencia del job ${SLURM_JOB_ID:-NA} — B3 CLAM plano gate fold 0"
  echo "# Arbol ajeno y compartido: ${PROJECT_DIR}"
  echo "## AL LANZAR  $(date -Is)"
  for f in "${TRACKED[@]}"; do
    printf '%s  %s  %s\n' "$(md5sum "${PROJECT_DIR}/${f}" | cut -d' ' -f1)" \
           "$(date -Is -r "${PROJECT_DIR}/${f}")" "${f}"
  done
} > "${PROV}"
cat "${PROV}"

# ── Preflight (workaround G): que un bug de datos mate el job en segundos ──────
echo ""
echo "── PREFLIGHT: minimo de parches por slide de train (>= B=${B_INST}) ──"
"$PY" "${REPO}/scripts/preflight_minpatch.py" \
    --split_dir    "${SPLIT_DIR}" \
    --features_dir "${DATA_ROOT}/features/pt_files" \
    --min_patches  "${B_INST}" \
    --fold         "${K_START}"
if [ $? -ne 0 ]; then
    echo "PREFLIGHT FAIL -> no se entrena. Exit."
    exit 1
fi
echo "── PREFLIGHT OK ──"
echo ""

nvidia-smi --query-gpu=name,memory.used,memory.total --format=csv | head -5 || true
echo ""

# ── Entrenamiento ─────────────────────────────────────────────────────────────
# SIN --use_mammoth: ese es el UNICO delta contra el brazo de sgaete.
# B y bag_weight quedan en sus defaults (8 y 0.7), igual que en la corrida Mammoth.
CUDA_VISIBLE_DEVICES=0 "$PY" main.py \
    --task           "$TASK" \
    --exp_code       "$EXP_CODE" \
    --split_dir      "$SPLIT_DIR" \
    --results_dir    "$RESULTS_DIR" \
    --data_root_dir  "$DATA_ROOT" \
    --k              "$K" \
    --k_start        "$K_START" \
    --k_end          "$K_END" \
    --model_type     "$MODEL_TYPE" \
    --embed_dim      "$EMBED_DIM" \
    --drop_out       "$DROP" \
    --lr             "$LR" \
    --reg            "$REG" \
    --seed           "$SEED" \
    --max_epochs     "$MAX_EPOCHS" \
    --bag_loss       ce \
    --inst_loss      svm \
    --early_stopping \
    --weighted_sample \
    --auto-label-dict
RC=$?

# ── Procedencia al terminar ───────────────────────────────────────────────────
{
  echo "## AL TERMINAR  $(date -Is)   rc=${RC}"
  for f in "${TRACKED[@]}"; do
    printf '%s  %s  %s\n' "$(md5sum "${PROJECT_DIR}/${f}" | cut -d' ' -f1)" \
           "$(date -Is -r "${PROJECT_DIR}/${f}")" "${f}"
  done
} >> "${PROV}"

echo ""
echo "========================================"
if [ "$RC" -ne 0 ]; then
    echo "FALLO: main.py devolvio rc=${RC}"
else
    echo "OK. Resultados en ${RESULTS_DIR}/${EXP_CODE}_s${SEED}/"
    echo "  resumen esperado: summary_partial_${K_START}_${K_END}.csv (NO summary.csv)"
fi
echo "Procedencia: ${PROV}"
echo "  -> si los md5 de las dos secciones difieren, el run es SOSPECHOSO"
echo "     (alguien edito el arbol compartido mientras corria)"
echo "fin = $(date -Is)"
echo "========================================"
exit $RC
