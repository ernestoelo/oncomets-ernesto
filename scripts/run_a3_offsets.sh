#!/bin/bash
# run_a3_offsets.sh — A3 del B8: deriva el offset QuPath->openslide de las 11 laminas
# anotadas que faltan, para que el cruce de la fase B1 pueda correr sobre ellas.
#
# Sin esto B1 da cero: el geojson NO esta en coordenadas de openslide y en la 129741,
# sin corregir, caian 0 de 26 marcas sobre un parche.
#
# CPU puro, post-hoc, sin GPU y sin sbatch. Binario absoluto del env (workaround B).
# Va DESATADO con setsid y es reanudable por el artefacto FINAL (workaround J): una
# lamina con su `offset_<id>.json` ya escrito se salta. FORCE=1 rehace todo.
#
# La 129741 NO esta en la lista: ya tiene su offset (dx=3829, dy=0) y su CSV desde el
# 31-jul. Se la deja intacta a proposito.
set -uo pipefail

REPO=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto
PYBIN=/home/sdonoso/miniconda3/envs/clam_latest/bin/python
ANOT=/media/administrador/Storage1/sdonoso/anotaciones          # ajeno, SOLO LECTURA
WSI=/media/administrador/Storage1/sdonoso/wsi                   # ajeno, SOLO LECTURA
OUT="$REPO/sprints/B8_sprint8/anotaciones_patologo"

cd "$REPO" || exit 1

SLIDES=(126504 128194 124729 124806 B25-158899 144317 164001 106552 103762 109609 110616)
FORCE="${FORCE:-0}"
n=${#SLIDES[@]}
i=0

echo "== A3: offsets de $n laminas anotadas =="
date

for sid in "${SLIDES[@]}"; do
  i=$((i+1))
  if [ "$FORCE" != "1" ] && [ -s "$OUT/offset_${sid}.json" ]; then
    echo ""
    echo "[$i/$n] $sid  (offset ya derivado, se salta)"
    continue
  fi
  gj="$ANOT/${sid}.bif - GDT.geojson"
  wsi="$WSI/$sid/${sid}.bif"
  echo ""
  echo "================================================================"
  echo "[$i/$n] $sid"
  echo "================================================================"
  if [ ! -f "$gj" ];  then echo "   !! falta el geojson: $gj"; continue; fi
  if [ ! -f "$wsi" ]; then echo "   !! falta la WSI: $wsi";    continue; fi
  "$PYBIN" "$REPO/scripts/alinear_anotaciones_qupath.py" \
      --geojson "$gj" --slide_id "$sid" --wsi "$wsi" --out "$OUT" 2>&1
done

echo ""
echo "== listo =="
date
