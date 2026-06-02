#!/bin/bash
#SBATCH --job-name=papilar_clam_mam_v2
#SBATCH --output=logs/papilar_clam_mammoth_sweep_v2/%x_%j.out
#SBATCH --error=logs/papilar_clam_mammoth_sweep_v2/%x_%j.err
#SBATCH --time=48:00:00
#SBATCH --cpus-per-task=16
#SBATCH --mem=32G
#SBATCH --gres=gpu:1

# ==============================================================================
# Campaña papilar V2 — CLAM-MB + Mammoth
# Tarea: cdis_patron_papilar_pth_balance   (SOLO CLAM-MB + Mammoth)
#
# QUÉ CAMBIA RESPECTO AL V1 (y por qué)
# -----------------------------------------------------------------------------
# Diagnóstico del v1 (ver ESTUDIO_papilar_v2.md):
#   - test = 28 slides con SOLO 3 positivos  -> test_auc cuantizado a 1/75.
#     Mover 1 slide cambia el AUC ~0.013-0.04: el ranking del v1 es, en gran
#     parte, RUIDO. No se puede confiar en "config #1 > #3" con 1 fold y 1 seed.
#   - val_auc>>test_auc en TODAS las configs (esperable con tan pocos positivos).
#   - lr 3e-4 (test 0.48) y lr 7e-4 (bacc 0.50) -> descartados.
#   - scheduler cosine peor que plateau -> descartado.
#   - 2 regímenes "ganadores":
#       A) alta capacidad + reg fuerte : do0.6 reg5e-5 e8s16h16d256 (mejor AUC)
#       B) mammoth compacto            : do0.5 reg3e-5 e2s4h8d128   (mejor bacc/gap)
#
# Decisiones del v2:
#   1) MULTI-SEED (1,2,3) sobre el MISMO fold-0  -> ejecutable HOY sin generar
#      splits nuevos. Estima variabilidad de inicialización; el reporte promedia.
#      (El arreglo definitivo de los 3 positivos es K=5 CV: ver NOTA K-FOLD.)
#   2) lr=5e-4 y scheduler=plateau BLOQUEADOS (perdedores eliminados).
#   3) Grid fino alrededor de los 2 regímenes A y B.
#   4) NUEVA palanca: confidence_penalty {0.1, 0.2, 0.3} (v1 fija en 0.2).
#   5) Selección por AUC PROMEDIO entre seeds (lo hace generate_papilar_report_v2.py).
# ==============================================================================

# ── VARIABLES EDITABLES ───────────────────────────────────────────────────────
ENV_NAME="clam_latest"
CONDA_BASE="/home/sdonoso/miniconda3"

PROJECT_DIR="/media/administrador/Storage1/sdonoso/clam_testing"
DATA_ROOT="/media/administrador/Storage1/sdonoso/clam_environ/environ"   # contiene 'features/'
SPLIT_DIR="${DATA_ROOT}/splits/cdis_patron_papilar_pth_balance_100"      # contiene splits_0.csv

TASK="cdis_patron_papilar_pth_balance"

# Raíces de salida V2 (todas con "papilar..._v2" en el nombre)
EXP_ROOT="${PROJECT_DIR}/results/papilar_clam_mammoth_sweep_v2"
REPORT_ROOT="${PROJECT_DIR}/reports/papilar_clam_mammoth_sweep_v2"
LOG_ROOT="${PROJECT_DIR}/logs/papilar_clam_mammoth_sweep_v2"
CKPT_ROOT="${PROJECT_DIR}/checkpoints/papilar_clam_mammoth_sweep_v2"

# K-fold:
#   K=1 -> 1 fold (estado actual: solo existe splits_0 en SPLIT_DIR).
#   K=5 -> requiere splits_0..splits_4 (ver NOTA K-FOLD al final).
K=1

# ── PARÁMETROS BLOQUEADOS (ganadores del v1) ──────────────────────────────────
LR="5e-4"              # 3e-4 y 7e-4 descartados
SCHED="plateau"        # cosine descartado
WPOS="3.0"             # peso clase positiva (fijo; sensibilidad se explora vía CV en v3)

# Multi-seed: cada config se entrena con cada seed; el reporte promedia.
SEEDS=(1 2 3)

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
echo "Campaña papilar V2 — CLAM-MB + Mammoth"
echo "  TASK       = ${TASK}"
echo "  DATA_ROOT  = ${DATA_ROOT}"
echo "  SPLIT_DIR  = ${SPLIT_DIR}"
echo "  EXP_ROOT   = ${EXP_ROOT}"
echo "  LR=${LR}(fijo)  SCHED=${SCHED}(fijo)  WPOS=${WPOS}(fijo)"
echo "  SEEDS      = ${SEEDS[*]}"
echo "  K          = ${K}   MAX_EPOCHS=${MAX_EPOCHS}"
echo "========================================"

# ── Sweep V2 alrededor de los 2 regímenes ─────────────────────────────────────
# Formato por línea: "DROP REG E S H D CP  # etiqueta"
#   CP = confidence_penalty (NUEVA palanca explorada en v2).
# Régimen A = e8s16h16d256 (alta capacidad).  Régimen B = e{2,4}... (compacto).
SWEEP=(
  # ── Régimen A: alta capacidad + reg fuerte (champion v1) ──
  "0.6 5e-5 8 16 16 256 0.2"   # A1) champion v1 (cp baseline)
  "0.6 5e-5 8 16 16 256 0.1"   # A2) menos confidence_penalty
  "0.6 5e-5 8 16 16 256 0.3"   # A3) más  confidence_penalty
  "0.5 5e-5 8 16 16 256 0.2"   # A4) dropout cruzado (0.5)
  # ── Régimen B: mammoth compacto (mejor bacc/gap v1) ──
  "0.5 3e-5 2  4  8 128 0.2"   # B1) best bacc v1 (cp baseline)
  "0.5 3e-5 2  4  8 128 0.1"   # B2) menos confidence_penalty
  "0.5 3e-5 2  4  8 128 0.3"   # B3) más  confidence_penalty
  "0.5 3e-5 4  8  8 128 0.2"   # B4) gap mínimo v1 (e4s8h8d128)
)

n_total=$(( ${#SWEEP[@]} * ${#SEEDS[@]} ))
n_ok=0
n_fail=0
idx=0

for cfg in "${SWEEP[@]}"; do
    read -r DROP REG E S H D CP <<< "$cfg"

    # exp_code incluye cp para distinguir configs y para el parseo del reporte.
    EXP_CODE="papilar_clam_mam_lr${LR}_do${DROP}_reg${REG}_e${E}s${S}h${H}d${D}_sched_${SCHED}_wpos${WPOS}_cp${CP}"

    for SEED in "${SEEDS[@]}"; do
        idx=$((idx + 1))
        RUN_LOG="${LOG_ROOT}/${EXP_CODE}_s${SEED}.log"

        echo ""
        echo "────────────────────────────────────────"
        echo "[${idx}/${n_total}] ${EXP_CODE}  (seed ${SEED})"
        echo "  lr=${LR} drop=${DROP} reg=${REG} mammoth=e${E}s${S}h${H}d${D} sched=${SCHED} wpos=${WPOS} cp=${CP}"
        echo "────────────────────────────────────────"

        # Skip si ya existe summary.csv para esta config+seed
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
echo "Sweep V2 terminado: OK=${n_ok}  FAIL=${n_fail}  TOTAL=${n_total}"
echo "========================================"

# ── PASO FINAL: reporte consolidado V2 (promedia sobre seeds) ─────────────────
echo ""
echo "Generando reporte consolidado V2 (media±desv sobre seeds)..."
"$PY" generate_papilar_report_v2.py \
    --results_dir "$EXP_ROOT" \
    --output_dir  "$REPORT_ROOT"

echo ""
echo "========================================"
echo "LISTO (V2). Resultados en:"
echo "  CSV consolidado : ${REPORT_ROOT}/papilar_clam_mammoth_v2_summary.csv"
echo "  PDF reporte     : ${REPORT_ROOT}/reporte_papilar_clam_mammoth_sweep_v2.pdf"
echo "  PNGs            : ${REPORT_ROOT}/*.png"
echo "  Runs/ckpt       : ${EXP_ROOT}/<exp_code>_s{1,2,3}/"
echo "  Logs por corrida: ${LOG_ROOT}/"
echo "========================================"

# ==============================================================================
# NOTA K-FOLD (arreglo definitivo del problema de los 3 positivos en test)
# ------------------------------------------------------------------------------
# El multi-seed de este v2 NO cambia el split: siguen siendo los MISMOS 3
# positivos en test. Para que cada caso rote por test (≈15 positivos agregados)
# hay que pasar a K=5 CV:
#   1) Generar splits_0..splits_4 (5-fold ESTRATIFICADO por label) en SPLIT_DIR.
#      OJO: create_splits_seq.py actual NO soporta las tasks 'environ'. Hay que
#      añadir un bloque que cargue environ/csv_balance/dataset_cdis_patron_papilar_label.csv
#      con Generic_WSI_Classification_Dataset y k=5.
#   2) Con splits_0..4 presentes: poner K=5 arriba y relanzar.
#   generate_papilar_report_v2.py ya promedia sobre folds Y sobre seeds.
# ==============================================================================
