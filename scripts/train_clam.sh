#!/usr/bin/env bash
# train_clam.sh
# Wrapper around Sebastián's main.py. Does NOT modify the original code.
# Logs everything to sprints/B3_sprint3/objetivo_2_entrenamiento/logs/<run_id>/
#
# IMPORTANT — args reales de main.py (validados 5 mayo 2026):
#   --split_dir (NO --csv_path)
#   --data_root_dir, --task, --exp_code, --model_type, --model_size,
#   --bag_loss, --inst_loss, --B, --bag_weight, --subtyping (flag),
#   --max_epochs, --lr, --early_stopping (flag), --opt, --drop_out,
#   --embed_dim, --results_dir, --k, --k_start, --k_end
#
# Usage:
#   ./scripts/train_clam.sh \
#       --split-dir /mnt/disco_duro/onco/sebastianDonoso/testMIL/CLAM/dataset_csv/<task>_100/ \
#       --data-root /mnt/disco_duro/.../features_conch \
#       --task <task_from_TASK_CONFIGS> \
#       --exp-code <my_exp_name> \
#       --extra "--model_type clam_mb --inst_loss svm --B 8 --bag_weight 0.7 --subtyping --embed_dim 1024 --max_epochs 50 --early_stopping"

set -euo pipefail

CLAM_PATH="${CLAM_PATH:-/mnt/disco_duro/onco/sebastianDonoso/testMIL/CLAM}"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOG_BASE="${REPO_ROOT}/sprints/B3_sprint3/objetivo_2_entrenamiento/logs"

# ---------------------------------------------------------------------------
# Parse args
# ---------------------------------------------------------------------------
SPLIT_DIR=""
DATA_ROOT=""
TASK=""
EXP_CODE=""
EXTRA=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --split-dir)  SPLIT_DIR="$2"; shift 2 ;;
        --data-root)  DATA_ROOT="$2"; shift 2 ;;
        --task)       TASK="$2"; shift 2 ;;
        --exp-code)   EXP_CODE="$2"; shift 2 ;;
        --extra)      EXTRA="$2"; shift 2 ;;
        -h|--help)
            grep '^#' "$0" | sed 's/^# \?//'; exit 0 ;;
        *) echo "unknown arg: $1" >&2; exit 1 ;;
    esac
done

[[ -n "${SPLIT_DIR}" ]] || { echo "missing --split-dir" >&2; exit 1; }
[[ -n "${DATA_ROOT}" ]] || { echo "missing --data-root" >&2; exit 1; }
[[ -n "${TASK}" ]] || { echo "missing --task" >&2; exit 1; }
[[ -n "${EXP_CODE}" ]] || { echo "missing --exp-code" >&2; exit 1; }

[[ -d "${SPLIT_DIR}" ]] || { echo "split-dir not a directory: ${SPLIT_DIR}" >&2; exit 1; }
[[ -d "${DATA_ROOT}" ]] || { echo "data root not a directory: ${DATA_ROOT}" >&2; exit 1; }

# ---------------------------------------------------------------------------
# Setup run directory
# ---------------------------------------------------------------------------
RUN_ID="$(date +%Y%m%d_%H%M%S)_${EXP_CODE}"
RUN_DIR="${LOG_BASE}/${RUN_ID}"
mkdir -p "${RUN_DIR}"

echo "[train] run_id=${RUN_ID}"
echo "[train] log_dir=${RUN_DIR}"

# ---------------------------------------------------------------------------
# Snapshot config — exact reproducibility info
# ---------------------------------------------------------------------------
cat > "${RUN_DIR}/config_snapshot.txt" <<EOF
run_id:        ${RUN_ID}
timestamp:     $(date -Iseconds)
split_dir:     ${SPLIT_DIR}
data_root:     ${DATA_ROOT}
task:          ${TASK}
exp_code:      ${EXP_CODE}
clam_path:     ${CLAM_PATH}
clam_commit:   $(git -C "${CLAM_PATH}" rev-parse HEAD 2>/dev/null || echo "<not a git repo>")
extra_args:    ${EXTRA}
python:        $(python --version 2>&1)
torch:         $(python -c "import torch; print(torch.__version__)" 2>&1)
cuda:          $(python -c "import torch; print(torch.version.cuda)" 2>&1)
gpus:          $(nvidia-smi -L | wc -l)
hostname:      $(hostname)
EOF

# ---------------------------------------------------------------------------
# Launch — tee output to log file
# ---------------------------------------------------------------------------
cd "${CLAM_PATH}"

# shellcheck disable=SC2086
python main.py \
    --split_dir "${SPLIT_DIR}" \
    --data_root_dir "${DATA_ROOT}" \
    --task "${TASK}" \
    --exp_code "${EXP_CODE}" \
    --results_dir "${RUN_DIR}" \
    ${EXTRA} \
    2>&1 | tee "${RUN_DIR}/train.log"

echo "[train] done. logs at ${RUN_DIR}"
