#!/usr/bin/env bash
# verify_clam_access.sh
# Smoke test del codebase de Sebastián. Confirma:
# 1. Read access a los archivos clave (paths actualizados a la realidad).
# 2. Si import directo de CLAM_MB funciona, o si hace falta importlib workaround.
# 3. Validez básica del entorno PyTorch.

set -euo pipefail

CLAM_PATH="${CLAM_PATH:-/mnt/disco_duro/onco/sebastianDonoso/testMIL/CLAM}"

log() { printf '\033[1;34m[verify]\033[0m %s\n' "$*"; }
err() { printf '\033[1;31m[verify ERROR]\033[0m %s\n' "$*" >&2; }

# ---------------------------------------------------------------------------
# 1. Read access
# ---------------------------------------------------------------------------
log "1. checking CLAM path is readable..."
[[ -d "${CLAM_PATH}" ]] || { err "directory not found: ${CLAM_PATH}"; exit 1; }
log "   ok: ${CLAM_PATH}"

log "2. checking expected files (real paths)..."
EXPECTED=(
    "main.py"
    "eval.py"
    "create_splits_seq.py"
    "models/model_clam.py"
    "models/__init__.py"
    "utils/core_utils.py"
    "run_all_splits.sh"
    "run_all_training.sh"
)
MISSING=0
for f in "${EXPECTED[@]}"; do
    if [[ -r "${CLAM_PATH}/${f}" ]]; then
        log "   ${f} ok"
    else
        err "missing or unreadable: ${CLAM_PATH}/${f}"
        MISSING=$((MISSING+1))
    fi
done
[[ "${MISSING}" -eq 0 ]] || { err "${MISSING} expected files missing"; exit 1; }

# ---------------------------------------------------------------------------
# 3. PyTorch + CUDA sanity
# ---------------------------------------------------------------------------
log "3. checking PyTorch + CUDA..."
python - <<'EOF' || { exit 2; }
import torch
print(f"   torch={torch.__version__}  cuda_runtime={torch.version.cuda}  available={torch.cuda.is_available()}  devices={torch.cuda.device_count()}")
assert torch.cuda.is_available(), "CUDA not available — wrong conda env?"
EOF

# ---------------------------------------------------------------------------
# 4. Direct import — paso 1 del workarounds.md
# ---------------------------------------------------------------------------
log "4. trying direct import of CLAM_MB (no workaround)..."
DIRECT_OK=0
python - <<EOF && DIRECT_OK=1 || true
import sys
sys.path.insert(0, "${CLAM_PATH}")
try:
    from models.model_clam import CLAM_MB
    print("   direct import: OK")
except Exception as e:
    print(f"   direct import failed: {type(e).__name__}: {e}")
    raise
EOF

if [[ "${DIRECT_OK}" -eq 1 ]]; then
    log "   ✓ direct import works — no workaround needed"
else
    log "   direct import failed, trying importlib.util workaround..."

    # ---------------------------------------------------------------------------
    # 5. Importlib workaround — paso 2 del workarounds.md
    # ---------------------------------------------------------------------------
    python - <<EOF || { err "BOTH import methods failed — check timm install and __init__.py"; exit 3; }
import importlib.util
import sys
from pathlib import Path

clam_path = Path("${CLAM_PATH}") / "models" / "model_clam.py"
spec = importlib.util.spec_from_file_location("model_clam", clam_path)
module = importlib.util.module_from_spec(spec)
sys.modules["model_clam"] = module
spec.loader.exec_module(module)

assert hasattr(module, "CLAM_MB"), "CLAM_MB not found in model_clam.py"
print(f"   importlib workaround: OK  ({module.CLAM_MB})")
EOF
    log "   ⚠ direct import failed but importlib workaround works"
    log "   action: keep importlib workaround in any custom script"
fi

log "all checks passed"
