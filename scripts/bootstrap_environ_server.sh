#!/usr/bin/env bash
# bootstrap_environ_server.sh
# Validates env on the Environ server and launches Claude Code with sprint context.
#
# Used for SSH-direct sessions. For VS Code Remote SSH this script is NOT
# needed — Claude Code launches from the integrated terminal and reads
# CLAUDE.md automatically.
#
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
CLAM_PATH="/media/administrador/Storage1/sdonoso/clam_environ"
WORKSPACE="/media/administrador/Storage1/sdonoso/clam_testing2"
REPO_DIR="${WORKSPACE}/oncomets-ernesto"

# Default conda env. Validated 2026-05-19: the CLAM env on this server is
# `clam_latest` (all .slurm in clam_environ activate it). `base` has a BROKEN
# `python` on PATH (ADFRsuite py2.7). Override via ONCOMETS_CONDA_ENV.
CONDA_ENV="${ONCOMETS_CONDA_ENV:-clam_latest}"

log() { printf '\033[1;34m[bootstrap]\033[0m %s\n' "$*"; }
err() { printf '\033[1;31m[bootstrap ERROR]\033[0m %s\n' "$*" >&2; }

# ---------------------------------------------------------------------------
# 1. Validate read access to Sebastián's codebase
# ---------------------------------------------------------------------------
log "checking CLAM codebase read access..."
if [[ ! -r "${CLAM_PATH}/models/model_clam.py" ]]; then
    err "cannot read ${CLAM_PATH}/models/model_clam.py"
    err "is the VPN up and the path mounted? are permissions correct?"
    exit 1
fi

# ---------------------------------------------------------------------------
# 2. Validate workspace
# ---------------------------------------------------------------------------
log "checking workspace..."
if [[ ! -w "${REPO_DIR}" ]]; then
    err "repo dir not writable: ${REPO_DIR}"
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
    "/home/sdonoso/miniconda3/etc/profile.d/conda.sh" \
    "${HOME}/anaconda3/etc/profile.d/conda.sh" \
    "/opt/miniconda3/etc/profile.d/conda.sh"
do
    if [[ -f "${candidate}" ]]; then
        CONDA_SH="${candidate}"
        break
    fi
done

if [[ -z "${CONDA_SH}" ]]; then
    err "conda profile not found in standard locations"
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
    conda env list >&2
    err "override with: ONCOMETS_CONDA_ENV=<name> ssh <host>"
    exit 4
fi

# ---------------------------------------------------------------------------
# 5. Validate GPUs (read-only — no -pm / persistence mode)
# ---------------------------------------------------------------------------
log "checking GPUs..."
if ! command -v nvidia-smi >/dev/null 2>&1; then
    err "nvidia-smi not found"
    exit 5
fi
GPU_COUNT=$(nvidia-smi -L | wc -l)
[[ "${GPU_COUNT}" -ge 1 ]] || { err "no GPUs visible to driver"; exit 5; }
log "found ${GPU_COUNT} GPU(s):"
nvidia-smi -L | sed 's/^/         /'

# ---------------------------------------------------------------------------
# 6. SLURM sanity + courtesy snapshot (single GPU → don't monopolize)
# ---------------------------------------------------------------------------
log "SLURM queue snapshot (single-GPU courtesy):"
sinfo 2>/dev/null | sed 's/^/         /' || err "sinfo not available"
squeue 2>/dev/null | sed 's/^/         /' || true

# ---------------------------------------------------------------------------
# 7. Launch Claude Code
# ---------------------------------------------------------------------------
if ! command -v claude >/dev/null 2>&1; then
    err "'claude' binary not found in PATH"
    exit 6
fi

log "launching Claude Code with sprint context..."
echo

INITIAL_PROMPT="Acabo de entrar al servidor Environ como user compartido sdonoso.
Lee CLAUDE.md y progress/current.md.
Estamos en Sprint 4 (B4). Recuerda: codebase en clam_environ/ es READ-ONLY,
toda carga GPU va por sbatch (nunca python directo), git config es LOCAL.
Reporta status y propón el próximo paso concreto. Revisa squeue antes de
sugerir cualquier sbatch (GPU única)."

exec claude "${INITIAL_PROMPT}"
