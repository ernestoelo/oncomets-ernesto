#!/bin/bash
# Los dos brazos de control del eje de atención (plan del 07/09, paso 1). CPU, en serie.
# Va DESATADO (workaround J): setsid nohup ... < /dev/null &, y se verifica ppid = 1.
set -uo pipefail
REPO=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto
PY=/home/sdonoso/miniconda3/envs/clam_latest/bin/python
cd "$REPO"

echo "=== gate de regresión, antes de leer un número nuevo ==="
CUDA_VISIBLE_DEVICES="" "$PY" scripts/b9_atencion_12_laminas.py --gate || {
  echo "GATE FALLA — no se corre nada"; exit 1; }

for V in limpios todos; do
  echo; echo "=== brazo ckpt_limpio --folds $V  ($(date +%H:%M:%S)) ==="
  CUDA_VISIBLE_DEVICES="" "$PY" scripts/b9_atencion_12_laminas.py \
      --fuente ckpt_limpio --folds "$V" || echo "FALLO el brazo $V"
done
echo; echo "=== fin $(date +%H:%M:%S) ==="
