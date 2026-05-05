#!/usr/bin/env bash
# train_clam.sh
# Wrapper around Sebastián's main.py. Does NOT modify the original code.
# Logs everything to sprints/B3_sprint3/objetivo_2_entrenamiento/logs/<run_id>/
#
# Usage:
#   ./scripts/train_clam.sh \
#       --csv sprints/B3_sprint3/objetivo_2_entrenamiento/splits/camelyon_train.csv \
#       --data-root /mnt/disco_duro/datasets/camelyon16/features_conch \
#       --extra "--task task_1_tumor_vs_normal --model_type clam_mb --B 8"

set -euo pipefail

CLAM_PATH="${CLAM_PATH:-/mnt/disco_duro/onco/sebastianDonoso/testMIL/CLAM}"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOG_BASE="${REPO_ROOT}/sprints/B3_sprint3/objetivo_2_entrenamiento/logs"

# ---------------------------------------------------------------------------
# Parse args
# ---------------------------------------------------------------------------
CSV=""
DATA_ROOT=""
EXTRA=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --csv)        CSV="$2"; shift 2 ;;
        --data-root)  DATA_ROOT="$2"; shift 2 ;;
        --extra)      EXTRA="$2"; shift 2 ;;
        -h|--help)
            grep '^#' "$0" | sed 's/^# \?//'; exit 0 ;;
        *) echo "unknown arg: $1" >&2; exit 1 ;;
    esac
done

[[ -n "${CSV}" ]] || { echo "missing --csv" >&2; exit 1; }
[[ -n "${DATA_ROOT}" ]] || { echo "missing --data-root" >&2; exit 1; }
[[ -r "${CSV}" ]] || { echo "csv not readable: ${CSV}" >&2; exit 1; }
[[ -d "${DATA_ROOT}" ]] || { echo "data root not a directory: ${DATA_ROOT}" >&2; exit 1; }

# ---------------------------------------------------------------------------
# Setup run directory
# ---------------------------------------------------------------------------
RUN_ID="$(date +%Y%m%d_%H%M%S)_$(basename "${CSV}" .csv)"
RUN_DIR="${LOG_BASE}/${RUN_ID}"
mkdir -p "${RUN_DIR}"

echo "[train] run_id=${RUN_ID}"
echo "[train] log_dir=${RUN_DIR}"

# ---------------------------------------------------------------------------
# Snapshot config — exactly which CSV, data root, code version
# ---------------------------------------------------------------------------
cat > "${RUN_DIR}/config_snapshot.txt" <<EOF
run_id:      ${RUN_ID}
timestamp:   $(date -Iseconds)
csv:         ${CSV}
csv_md5:     $(md5sum "${CSV}" | awk '{print $1}')
data_root:   ${DATA_ROOT}
clam_path:   ${CLAM_PATH}
clam_commit: $(git -C "${CLAM_PATH}" rev-parse HEAD 2>/dev/null || echo "<not a git repo>")
extra_args:  ${EXTRA}
python:      $(python --version 2>&1)
torch:       $(python -c "import torch; print(torch.__version__)" 2>&1)
cuda:        $(python -c "import torch; print(torch.version.cuda)" 2>&1)
gpus:        $(nvidia-smi -L | wc -l)
EOF

# ---------------------------------------------------------------------------
# Launch — tee output to log file
# ---------------------------------------------------------------------------
cd "${CLAM_PATH}"

# shellcheck disable=SC2086
python main.py \
    --csv_path "${CSV}" \
    --data_root_dir "${DATA_ROOT}" \
    --results_dir "${RUN_DIR}" \
    ${EXTRA} \
    2>&1 | tee "${RUN_DIR}/train.log"

echo "[train] done. logs at ${RUN_DIR}"
