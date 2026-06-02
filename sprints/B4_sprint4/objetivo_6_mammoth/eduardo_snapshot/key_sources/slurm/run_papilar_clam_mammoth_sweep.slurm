#!/bin/bash
#SBATCH --job-name=papilar_clam_mam
#SBATCH --output=logs/papilar_clam_mammoth_sweep/%x_%j.out
#SBATCH --error=logs/papilar_clam_mammoth_sweep/%x_%j.err
#SBATCH --time=48:00:00
#SBATCH --cpus-per-task=16
#SBATCH --mem=32G
#SBATCH --gres=gpu:1

# ==============================================================================
# Campaña papilar — CLAM-MB + Mammoth (sweep controlado alrededor de e8s16h16d256)
# Tarea: cdis_patron_papilar_pth_balance
# SOLO CLAM-MB + Mammoth. Sin DTFD-MIL ni DTFD+Mammoth.
# ==============================================================================

# ── VARIABLES EDITABLES ───────────────────────────────────────────────────────
# Ajusta SOLO estas rutas si tu entorno cambia.
ENV_NAME="clam_latest"
CONDA_BASE="/home/sdonoso/miniconda3"

PROJECT_DIR="/media/administrador/Storage1/sdonoso/clam_testing"
DATA_ROOT="/media/administrador/Storage1/sdonoso/clam_environ/environ"   # --data_root_dir (contiene 'features/')
FEATURES_DIR="${DATA_ROOT}/features"                                     # derivado; informativo
SPLIT_DIR="${DATA_ROOT}/splits/cdis_patron_papilar_pth_balance_100"      # contiene splits_0.csv (...splits_4 si K=5)

TASK="cdis_patron_papilar_pth_balance"

# Raíces de salida (todas con "papilar" en el nombre)
EXP_ROOT="${PROJECT_DIR}/results/papilar_clam_mammoth_sweep"
REPORT_ROOT="${PROJECT_DIR}/reports/papilar_clam_mammoth_sweep"
LOG_ROOT="${PROJECT_DIR}/logs/papilar_clam_mammoth_sweep"
CKPT_ROOT="${PROJECT_DIR}/checkpoints/papilar_clam_mammoth_sweep"   # informativo: los ckpt los guarda main.py dentro de EXP_ROOT/<exp>_s1/

# K-fold:
#   K=1 → 1 fold (estado actual: solo existe splits_0 en SPLIT_DIR).
#   K=5 → requiere splits_0..splits_4 en SPLIT_DIR (ver nota K-FOLD al final del archivo).
K=1
# K=5   # <-- descomenta para 5-fold DESPUÉS de generar los splits (ver nota K-FOLD)

SEED=1                 # main.py guarda resultados en EXP_ROOT/<exp_code>_s${SEED}
MAX_EPOCHS=200
MODEL_TYPE="clam_mb"
EMBED_DIM=512
GPU=0
# ──────────────────────────────────────────────────────────────────────────────

# Activación de conda (SLURM arranca sin conda en PATH)
source "${CONDA_BASE}/etc/profile.d/conda.sh"
conda activate "${ENV_NAME}"
PY="${CONDA_BASE}/envs/${ENV_NAME}/bin/python3"

cd "${PROJECT_DIR}" || exit 1
mkdir -p "${EXP_ROOT}" "${REPORT_ROOT}" "${LOG_ROOT}" "${CKPT_ROOT}"

if [ ! -d "${SPLIT_DIR}" ]; then
    echo "ERROR: SPLIT_DIR no existe: ${SPLIT_DIR}"
    exit 1
fi

echo "========================================"
echo "Campaña papilar — CLAM-MB + Mammoth"
echo "  TASK       = ${TASK}"
echo "  DATA_ROOT  = ${DATA_ROOT}"
echo "  SPLIT_DIR  = ${SPLIT_DIR}"
echo "  EXP_ROOT   = ${EXP_ROOT}"
echo "  K          = ${K}   SEED=${SEED}   MAX_EPOCHS=${MAX_EPOCHS}"
echo "========================================"

# ── Definición del sweep controlado ───────────────────────────────────────────
# Formato por línea: "LR DROP REG MAM_E MAM_S MAM_H MAM_DIM SCHED WPOS  # etiqueta"
# SCHED ∈ {plateau, cosine, none}.  WPOS = class_weight_pos (clase positiva).
SWEEP=(
  "5e-4 0.5 3e-5 8 16 16 256 plateau 3.0"   # 1) baseline mejorado
  "5e-4 0.4 3e-5 8 16 16 256 plateau 3.0"   # 2) menor dropout
  "5e-4 0.6 5e-5 8 16 16 256 plateau 3.0"   # 3) más regularización
  "3e-4 0.5 3e-5 8 16 16 256 plateau 3.0"   # 4) lr más bajo
  "7e-4 0.5 3e-5 8 16 16 256 plateau 3.0"   # 5) lr más alto
  "5e-4 0.5 3e-5 4  8  8 128 plateau 3.0"   # 6) mammoth intermedio
  "5e-4 0.5 3e-5 2  4  8 128 plateau 3.0"   # 7) mammoth compacto
  "5e-4 0.5 5e-5 8 16 16 256 cosine  3.0"   # 8) mayor capacidad + cosine
)

n_total=${#SWEEP[@]}
n_ok=0
n_fail=0
idx=0

for cfg in "${SWEEP[@]}"; do
    idx=$((idx + 1))
    read -r LR DROP REG E S H D SCHED WPOS <<< "$cfg"

    EXP_CODE="papilar_clam_mam_lr${LR}_do${DROP}_reg${REG}_e${E}s${S}h${H}d${D}_sched_${SCHED}_wpos${WPOS}"
    RUN_LOG="${LOG_ROOT}/${EXP_CODE}.log"

    echo ""
    echo "────────────────────────────────────────"
    echo "[${idx}/${n_total}] ${EXP_CODE}"
    echo "  lr=${LR} drop=${DROP} reg=${REG} mammoth=e${E}s${S}h${H}d${D} sched=${SCHED} wpos=${WPOS}"
    echo "────────────────────────────────────────"

    # Skip si ya existe summary.csv para esta config
    if [ -f "${EXP_ROOT}/${EXP_CODE}_s${SEED}/summary.csv" ]; then
        echo "  Skipping (ya existe summary.csv)."
        n_ok=$((n_ok + 1))
        continue
    fi

    CUDA_VISIBLE_DEVICES=$GPU "$PY" main.py \
        --task "$TASK" \
        --exp_code "$EXP_CODE" \
        --split_dir "$SPLIT_DIR" \
        --results_dir "$EXP_ROOT" \
        --data_root_dir "$DATA_ROOT" \
        --drop_out "$DROP" \
        --lr "$LR" \
        --reg "$REG" \
        --seed "$SEED" \
        --k "$K" \
        --max_epochs "$MAX_EPOCHS" \
        --model_type "$MODEL_TYPE" \
        --embed_dim "$EMBED_DIM" \
        --bag_loss ce \
        --inst_loss svm \
        --early_stopping \
        --weighted_sample \
        --log_gradients \
        --use_mammoth \
        --mammoth_num_experts "$E" \
        --mammoth_num_slots "$S" \
        --mammoth_num_heads "$H" \
        --mammoth_slot_dim "$D" \
        --scheduler "$SCHED" \
        --class_weight_pos "$WPOS" \
        --confidence_penalty 0.2 \
        --auto-label-dict 2>&1 | tee "$RUN_LOG"

    # ${PIPESTATUS[0]} = exit code de python (no de tee)
    if [ "${PIPESTATUS[0]}" -ne 0 ]; then
        echo "  ERROR en ${EXP_CODE}"
        n_fail=$((n_fail + 1))
    else
        n_ok=$((n_ok + 1))
    fi
done

echo ""
echo "========================================"
echo "Sweep terminado: OK=${n_ok}  FAIL=${n_fail}  TOTAL=${n_total}"
echo "========================================"

# ── PASO FINAL: reporte consolidado ───────────────────────────────────────────
echo ""
echo "Generando reporte consolidado..."
"$PY" generate_papilar_report.py \
    --results_dir "$EXP_ROOT" \
    --output_dir  "$REPORT_ROOT"

echo ""
echo "========================================"
echo "LISTO. Resultados en:"
echo "  CSV consolidado : ${REPORT_ROOT}/papilar_clam_mammoth_summary.csv"
echo "  PDF reporte     : ${REPORT_ROOT}/reporte_papilar_clam_mammoth_sweep.pdf"
echo "  PNGs            : ${REPORT_ROOT}/*.png"
echo "  Runs/ckpt       : ${EXP_ROOT}/<exp_code>_s${SEED}/"
echo "  Logs por corrida: ${LOG_ROOT}/"
echo "========================================"

# ==============================================================================
# NOTA K-FOLD (cómo activar K=5)
# ------------------------------------------------------------------------------
# Estado actual: SPLIT_DIR solo contiene splits_0.csv  → solo K=1 es posible.
# main.py YA soporta --k 5 (itera folds 0..k-1 leyendo splits_<i>.csv del SPLIT_DIR),
# pero NO existen splits_1..splits_4. Para habilitar K=5:
#
#   1) Necesitas generar splits_0..splits_4 en:
#        ${SPLIT_DIR}
#      ATENCIÓN: el create_splits_seq.py actual SOLO soporta las tasks demo
#      ('task_1_tumor_vs_normal' / 'task_2_tumor_subtyping'), NO las tasks 'environ'.
#      Para esta task hay que añadir un bloque en create_splits_seq.py que cargue
#      el CSV de la task (environ/csv_balance/dataset_cdis_patron_papilar_label.csv)
#      con Generic_WSI_Classification_Dataset y k=5, o reutilizar tu pipeline de splits.
#
#   2) Una vez existan ${SPLIT_DIR}/splits_0..4.csv :
#        - comenta la línea  K=1
#        - descomenta        K=5
#      y vuelve a lanzar este SLURM.
#
#   Recomendado para papilar (≈3 positivos en test): usar 5-fold para promediar la
#   inestabilidad. generate_papilar_report.py ya promedia automáticamente sobre los
#   folds presentes en cada summary.csv.
# ==============================================================================
