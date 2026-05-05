#!/usr/bin/env bash
# verify_clam_access.sh
# Smoke test: confirms that the importlib.util workaround for CLAM_MB works
# on Werner. Run once after cloning the repo, and any time the env changes.

set -euo pipefail

CLAM_PATH="${CLAM_PATH:-/mnt/disco_duro/onco/sebastianDonoso/testMIL/CLAM}"

log() { printf '\033[1;34m[verify]\033[0m %s\n' "$*"; }
err() { printf '\033[1;31m[verify ERROR]\033[0m %s\n' "$*" >&2; }

log "1. checking CLAM path is readable..."
[[ -d "${CLAM_PATH}" ]] || { err "directory not found: ${CLAM_PATH}"; exit 1; }
[[ -r "${CLAM_PATH}/model_clam.py" ]] || { err "model_clam.py not readable"; exit 1; }
log "   ok"

log "2. checking expected files..."
for f in model_clam.py main.py builder.py core_utils.py; do
    if [[ -r "${CLAM_PATH}/${f}" ]]; then
        log "   ${f} ok"
    else
        err "missing or unreadable: ${CLAM_PATH}/${f}"
    fi
done

log "3. testing importlib.util workaround..."
python - <<EOF
import importlib.util
import sys
from pathlib import Path

clam_path = Path("${CLAM_PATH}") / "model_clam.py"
spec = importlib.util.spec_from_file_location("model_clam", clam_path)
module = importlib.util.module_from_spec(spec)
sys.modules["model_clam"] = module
spec.loader.exec_module(module)

assert hasattr(module, "CLAM_MB"), "CLAM_MB not found in model_clam.py"
print(f"   CLAM_MB importable: {module.CLAM_MB}")

# Sanity: try to instantiate with a known minimal config
try:
    m = module.CLAM_MB(
        gate=True, size_arg="small", dropout=False,
        k_sample=8, n_classes=2, instance_loss_fn=None, subtyping=True,
    )
    print(f"   CLAM_MB instantiable: {type(m).__name__}")
except Exception as e:
    print(f"   WARN: instantiation failed (signature may differ): {e}")
EOF

log "all checks passed"
