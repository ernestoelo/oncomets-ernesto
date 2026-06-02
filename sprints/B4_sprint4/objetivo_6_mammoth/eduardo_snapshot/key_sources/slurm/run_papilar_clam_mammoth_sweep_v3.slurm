#!/bin/bash
#SBATCH --job-name=papilar_clam_mam_v3
#SBATCH --output=logs/papilar_clam_mammoth_sweep_v3/%x_%j.out
#SBATCH --error=logs/papilar_clam_mammoth_sweep_v3/%x_%j.err
#SBATCH --time=6:00:00
#SBATCH --cpus-per-task=16
#SBATCH --mem=32G
#SBATCH --gres=gpu:1

# ==============================================================================
# Campaña papilar V3 — CLAM-MB + Mammoth
# Tarea: cdis_patron_papilar_pth_balance   (SOLO CLAM-MB + Mammoth)
#
# QUÉ CAMBIA RESPECTO AL V2 (y por qué)
# -----------------------------------------------------------------------------
# Diagnóstico del v2 (ver ESTUDIO_papilar_v2.md):
#   - Config #8 (do=0.5 reg=3e-5 e4s8h8d128 cp=0.2) fue la mejor en media de
#     test AUC (0.662) y la más estable del régimen B (std=0.044).
#   - Régimen A (e8s16h16d256) tiene mejor val_auc pero seed3 colapsa en B4.
#   - Explorar dropout y regularización sobre e4s8h8d128 (arquitectura fija).
#
# Decisiones del v3:
#   1) Arquitectura fija: e4s8h8d128, cp=0.2 (ganadores de la palanca cp).
#   2) Multi-seed (1,2,3): misma metodología que v2, estimado ~2h 50min.
#   3) 3 configs: varían dropout {0.5, 0.6} y reg {3e-5, 5e-5}.
#   4) lr=5e-4, scheduler=plateau, wpos=3.0 bloqueados (como v2).
#   5) Reporte via generate_papilar_report_v2.py (promedia sobre seeds).
# ==============================================================================

# ── VARIABLES EDITABLES ───────────────────────────────────────────────────────
ENV_NAME="clam_latest"
CONDA_BASE="/home/sdonoso/miniconda3"

PROJECT_DIR="/media/administrador/Storage1/sdonoso/clam_testing"
DATA_ROOT="/media/administrador/Storage1/sdonoso/clam_environ/environ"
SPLIT_DIR="${DATA_ROOT}/splits/cdis_patron_papilar_pth_balance_100"

TASK="cdis_patron_papilar_pth_balance"

EXP_ROOT="${PROJECT_DIR}/results/papilar_clam_mammoth_sweep_v3"
REPORT_ROOT="${PROJECT_DIR}/reports/papilar_clam_mammoth_sweep_v3"
LOG_ROOT="${PROJECT_DIR}/logs/papilar_clam_mammoth_sweep_v3"
CKPT_ROOT="${PROJECT_DIR}/checkpoints/papilar_clam_mammoth_sweep_v3"

K=1

# ── PARÁMETROS BLOQUEADOS ─────────────────────────────────────────────────────
LR="5e-4"
SCHED="plateau"
WPOS="3.0"

SEEDS=(1 2 3)

MAX_EPOCHS=200
MODEL_TYPE="clam_mb"
EMBED_DIM=512
GPU=0
# ──────────────────────────────────────────────────────────────────────────────

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
echo "Campaña papilar V3 — CLAM-MB + Mammoth"
echo "  TASK       = ${TASK}"
echo "  DATA_ROOT  = ${DATA_ROOT}"
echo "  SPLIT_DIR  = ${SPLIT_DIR}"
echo "  EXP_ROOT   = ${EXP_ROOT}"
echo "  LR=${LR}(fijo)  SCHED=${SCHED}(fijo)  WPOS=${WPOS}(fijo)"
echo "  SEEDS      = ${SEEDS[*]}"
echo "  K          = ${K}   MAX_EPOCHS=${MAX_EPOCHS}"
echo "========================================"

# ── Sweep V3: do × reg sobre e4s8h8d128 fijo ─────────────────────────────────
# Formato por línea: "DROP REG E S H D CP  # etiqueta"
# Arquitectura e4s8h8d128 y cp=0.2 fijos (ganadores de v2).
SWEEP=(
  "0.6 3e-5 4  8  8 128 0.2"   # V3-1) do alto + reg suave  (cruce A×B)
  "0.5 5e-5 4  8  8 128 0.2"   # V3-2) do base  + reg fuerte (cruce B×A)
  "0.6 5e-5 4  8  8 128 0.2"   # V3-3) do alto  + reg fuerte (régimen A sobre arq B4)
)

n_total=$(( ${#SWEEP[@]} * ${#SEEDS[@]} ))
n_ok=0
n_fail=0
idx=0

for cfg in "${SWEEP[@]}"; do
    read -r DROP REG E S H D CP <<< "$cfg"

    EXP_CODE="papilar_clam_mam_lr${LR}_do${DROP}_reg${REG}_e${E}s${S}h${H}d${D}_sched_${SCHED}_wpos${WPOS}_cp${CP}"

    for SEED in "${SEEDS[@]}"; do
        idx=$((idx + 1))
        RUN_LOG="${LOG_ROOT}/${EXP_CODE}_s${SEED}.log"

        echo ""
        echo "────────────────────────────────────────"
        echo "[${idx}/${n_total}] ${EXP_CODE}  (seed ${SEED})"
        echo "  lr=${LR} drop=${DROP} reg=${REG} mammoth=e${E}s${S}h${H}d${D} sched=${SCHED} wpos=${WPOS} cp=${CP}"
        echo "────────────────────────────────────────"

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
            --confidence_penalty "$CP" \
            --auto-label-dict 2>&1 | tee "$RUN_LOG"

        if [ "${PIPESTATUS[0]}" -ne 0 ]; then
            echo "  ERROR en ${EXP_CODE} (seed ${SEED})"
            n_fail=$((n_fail + 1))
        else
            n_ok=$((n_ok + 1))
        fi
    done
done

echo ""
echo "========================================"
echo "Sweep V3 terminado: OK=${n_ok}  FAIL=${n_fail}  TOTAL=${n_total}"
echo "========================================"

echo ""
echo "Generando reporte consolidado V3..."
"$PY" generate_papilar_report_v2.py \
    --results_dir "$EXP_ROOT" \
    --output_dir  "$REPORT_ROOT"

echo ""
echo "========================================"
echo "LISTO (V3). Resultados en:"
echo "  CSV consolidado : ${REPORT_ROOT}/papilar_clam_mammoth_v2_summary.csv"
echo "  PDF reporte     : ${REPORT_ROOT}/reporte_papilar_clam_mammoth_sweep_v2.pdf"
echo "  PNGs            : ${REPORT_ROOT}/*.png"
echo "  Runs/ckpt       : ${EXP_ROOT}/<exp_code>_s1/"
echo "  Logs por corrida: ${LOG_ROOT}/"
echo "========================================"
