#!/usr/bin/env bash
# bootstrap_werner.sh
# Validates env on Werner (jenny2) and launches Claude Code with sprint context.
#
# Used for SSH-direct sessions ("camino B" en README). Para VS Code Remote SSH
# este script no es necesario — Claude Code se lanza desde la terminal
# integrada y lee CLAUDE.md automáticamente.
#
# Triggered by: `ssh environbio` (RemoteCommand in ~/.ssh/config) OR manual.
# Exit codes:
#   0  ok, claude launched
#   1  CLAM codebase unreadable
#   2  workspace path not writable
#   3  conda profile not found
#   4  conda env activation failed
#   5  no GPUs visible
#   6  claude binary not found

set -euo pipefail

# ---------------------------------------------------------------------------
# Configuration — adjust if paths or env name change
# ---------------------------------------------------------------------------
CLAM_PATH="/mnt/disco_duro/onco/sebastianDonoso/testMIL/CLAM"
WORKSPACE="/mnt/disco_duro/onco/oncologiaEnviron/ernestogamero"
REPO_DIR="${WORKSPACE}/oncomets-ernesto"

# Default conda env. Validated 2026-05-05: the env with torch 2.10.0+cu128
# and all CLAM deps is `memoriaSebaDonoso`. `base` does NOT have torch.
# Override via ONCOMETS_CONDA_ENV when launching:
#     ONCOMETS_CONDA_ENV=other-env ssh environbio
CONDA_ENV="${ONCOMETS_CONDA_ENV:-memoriaSebaDonoso}"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
log() { printf '\033[1;34m[bootstrap]\033[0m %s\n' "$*"; }
err() { printf '\033[1;31m[bootstrap ERROR]\033[0m %s\n' "$*" >&2; }

# ---------------------------------------------------------------------------
# 1. Validate read access to Sebastián's codebase
# ---------------------------------------------------------------------------
log "checking CLAM codebase read access..."
if [[ ! -r "${CLAM_PATH}/model_clam.py" ]]; then
    err "cannot read ${CLAM_PATH}/model_clam.py"
    err "is the path mounted? are permissions correct?"
    exit 1
fi

# ---------------------------------------------------------------------------
# 2. Validate workspace
# ---------------------------------------------------------------------------
log "checking workspace..."
if [[ ! -w "${WORKSPACE}" ]]; then
    err "workspace not writable: ${WORKSPACE}"
    err "are you logged in as 'onco' (shared user)?"
    exit 2
fi
cd "${REPO_DIR}"

# ---------------------------------------------------------------------------
# 3. Locate and source conda profile
# ---------------------------------------------------------------------------
log "locating conda profile..."
CONDA_SH=""
for candidate in \
    "${HOME}/miniconda3/etc/profile.d/conda.sh" \
    "/opt/miniconda3/etc/profile.d/conda.sh" \
    "${HOME}/anaconda3/etc/profile.d/conda.sh" \
    "/opt/anaconda3/etc/profile.d/conda.sh" \
    "/home/onco/miniconda3/etc/profile.d/conda.sh" \
    "/home/onco/anaconda3/etc/profile.d/conda.sh"
do
    if [[ -f "${candidate}" ]]; then
        CONDA_SH="${candidate}"
        break
    fi
done

if [[ -z "${CONDA_SH}" ]]; then
    err "conda profile not found in standard locations"
    err "tried HOME and /opt for {miniconda3,anaconda3}"
    err "fix: set CONDA_SH manually in this script or run 'which conda' to locate"
    exit 3
fi
log "   found ${CONDA_SH}"
# shellcheck disable=SC1090
source "${CONDA_SH}"

# ---------------------------------------------------------------------------
# 4. Activate conda env
# ---------------------------------------------------------------------------
log "activating conda env: ${CONDA_ENV}"
if ! conda activate "${CONDA_ENV}" 2>/dev/null; then
    err "could not activate conda env '${CONDA_ENV}'"
    err "available envs:"
    conda env list >&2
    err "override with: ONCOMETS_CONDA_ENV=<name> ssh environbio"
    exit 4
fi

# ---------------------------------------------------------------------------
# 5. Validate GPUs
# ---------------------------------------------------------------------------
log "checking GPUs..."
if ! command -v nvidia-smi >/dev/null 2>&1; then
    err "nvidia-smi not found"
    exit 5
fi

GPU_COUNT=$(nvidia-smi -L | wc -l)
if [[ "${GPU_COUNT}" -eq 0 ]]; then
    err "no GPUs visible to driver"
    exit 5
fi
log "found ${GPU_COUNT} GPU(s):"
nvidia-smi -L | sed 's/^/         /'

# ---------------------------------------------------------------------------
# 6. Quick sanity: PyTorch sees CUDA?
# ---------------------------------------------------------------------------
log "checking PyTorch CUDA..."
python -c "import torch; assert torch.cuda.is_available(), 'torch sees no CUDA'; \
print(f'         torch={torch.__version__}  cuda={torch.version.cuda}  devices={torch.cuda.device_count()}')" \
    || { err "PyTorch CUDA check failed — wrong conda env?"; exit 4; }

# ---------------------------------------------------------------------------
# 7. Launch Claude Code
# ---------------------------------------------------------------------------
if ! command -v claude >/dev/null 2>&1; then
    err "'claude' binary not found in PATH"
    err "install Claude Code or fix PATH"
    exit 6
fi

log "launching Claude Code with sprint context..."
echo

INITIAL_PROMPT="Acabo de entrar a Werner (jenny2) como user onco.
Lee CLAUDE.md y progress/current.md.
Estamos en Sprint 3 (B3), deadline mañana 6 de mayo de 2026.
Reporta status de los 4 entregables y propón el próximo paso concreto.
Si hay un entrenamiento en curso, revisa los últimos logs antes de responder."

exec claude "${INITIAL_PROMPT}"
