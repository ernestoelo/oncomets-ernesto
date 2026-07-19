#!/bin/bash
# run_b7_expert_interp.sh — corre mammoth_interpretability.py sobre las slides
# seleccionadas del Sprint 7 (ruteo por experto/slot + Q1 combine_weights).
#
# Etapa 0: CPU puro, post-hoc, SIN GPU y SIN sbatch (inferencia sobre checkpoints
# congelados; no toca modelo ni training). Binario absoluto del env (workaround B).
#
# patch_size_level0=448 = geometría REAL de las coords del h5 (parche de magnificación
# de Sebastián 448@×40→224), verificada en las 7 slides el 18-jul. Sin este override
# el script infiere 512 desde la magnificación y sobredimensiona cada parche.
set -uo pipefail

REPO=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto
PYBIN=/home/sdonoso/miniconda3/envs/clam_latest/bin/python
SEL="$REPO/sprints/B7_sprint7/interp_slides.json"
OUT_ROOT="$REPO/results/b7_mammoth_interp/interpretabilidad"
PATCH_SIZE_LEVEL0=448

cd "$REPO" || exit 1

# task<TAB>slide_id<TAB>h5<TAB>wsi<TAB>ckpt_mammoth<TAB>label
"$PYBIN" - "$SEL" <<'PY' > /tmp/b7_interp_rows.tsv
import json, sys
sel = json.load(open(sys.argv[1]))
for task, cfg in sel.items():
    for s in cfg["slides"]:
        print("\t".join([task, s["slide_id"], s["h5"], s["wsi"],
                         cfg["ckpt_mammoth"], s["label"]]))
PY

n=$(wc -l < /tmp/b7_interp_rows.tsv)
echo "== $n slides a procesar (expertos/slots) =="

# Reanudable: una lámina con slot_usage.csv Y meta.json ya está completa y se salta.
# Corre ~10 min por lámina (más en las de 20k+ parches), así que una corrida que se
# interrumpe (cierre de sesión, caída de la VPN) no debe repetir lo ya hecho.
# FORCE=1 rehace todo.
FORCE="${FORCE:-0}"

i=0
while IFS=$'\t' read -r task sid h5 wsi ckpt label; do
  i=$((i+1))
  short="${sid%%.*}"
  out="$OUT_ROOT/$task/$short/expertos"
  echo ""
  if [ "$FORCE" != "1" ] && [ -s "$out/slot_usage.csv" ] && [ -s "$out/meta.json" ]; then
    echo "[$i/$n] $task / $short  (ya completa, se salta)"
    continue
  fi
  echo "[$i/$n] $task / $short  (clase: $label)"
  CUDA_VISIBLE_DEVICES="" "$PYBIN" "$REPO/scripts/mammoth_interpretability.py" \
      --ckpt "$ckpt" --h5 "$h5" --wsi "$wsi" --out-dir "$out" \
      --patch-size-level0 "$PATCH_SIZE_LEVEL0" \
      --topk 6 --label "clase_real=$label" 2>&1 \
    | grep -viE "futurewarning|nn.init|^ *$"
done < /tmp/b7_interp_rows.tsv

echo ""
echo "== listo: salida bajo $OUT_ROOT/<task>/<slide>/expertos =="
