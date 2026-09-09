#!/bin/bash
# run_b10_offsets.sh — B10: deriva el offset QuPath->openslide de las 9 laminas anotadas
# NUEVAS (geojson con fecha 27-ago-2026) que ninguna sesion habia visto hasta el 8-sep.
#
# Clon de scripts/run_a3_offsets.sh (B8, las 11 primeras) con UN solo cambio de fondo:
# el nombre del geojson. Cinco de los nueve se llaman `<id>.bif GDT.geojson`, SIN el ` - `
# que el driver del B8 tiene cableado (128250, 131461-1, 133677, 142541-1, 154144). Los
# otros cuatro si lo traen. En vez de cablear dos patrones se prueban los dos y se aborta
# la lamina si ninguno existe, que es lo que falla ruidosamente si el patologo cambia otra
# vez la convencion.
#
# El alineador NO se toca: recibe --geojson por argumento.
#
# La salida va al MISMO directorio que la del B8 (`sprints/B8_sprint8/anotaciones_patologo/`)
# a proposito: los offsets son un artefacto por lamina, no por sprint, y TODOS los consumidores
# (b9_pleomorfismo.py, b9_epitelio_estroma.py, cruce_94_marcas.py, ...) leen de ahi. Partirlos
# en dos directorios obligaria a parchear cada consumidor.
#
# CPU puro, post-hoc, sin GPU y sin sbatch. Binario absoluto del env (workaround B).
# Va DESATADO con setsid y es reanudable por el artefacto FINAL (workaround J): una lamina
# con su `offset_<id>.json` ya escrito se salta. FORCE=1 rehace todo.
#
# Costo medido en el B8: ~22 min de CPU por 11 laminas => ~18 min esperados por 9.
#
#   setsid nohup bash scripts/run_b10_offsets.sh > logs/b10_offsets_desatado.log 2>&1 < /dev/null &
set -uo pipefail

REPO=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto
PYBIN=/home/sdonoso/miniconda3/envs/clam_latest/bin/python
ANOT=/media/administrador/Storage1/sdonoso/anotaciones          # ajeno, SOLO LECTURA
WSI=/media/administrador/Storage1/sdonoso/wsi                   # ajeno, SOLO LECTURA
OUT="$REPO/sprints/B8_sprint8/anotaciones_patologo"

cd "$REPO" || exit 1

# Las 9 nuevas NUMERICAS. La decima del 27-ago es `Br0244 ... MxBr_02 HE`, que es `.svs`
# y no tiene `.bif` en wsi/: queda fuera y se declara, no se deja caer en silencio.
SLIDES=(110962 128250 131461-1 132208 132844 133677 141426-1 142541-1 154144)
FORCE="${FORCE:-0}"
n=${#SLIDES[@]}
i=0
OK=0; SKIP=0; FAIL=0
FALLIDAS=()

echo "== B10: offsets de $n laminas anotadas nuevas =="
date -Is

for sid in "${SLIDES[@]}"; do
  i=$((i+1))
  if [ "$FORCE" != "1" ] && [ -s "$OUT/offset_${sid}.json" ]; then
    echo ""
    echo "[$i/$n] $sid  (offset ya derivado, se salta)"
    SKIP=$((SKIP+1)); continue
  fi

  # El fix: los dos patrones de nombre que usa el patologo, en orden.
  gj="$ANOT/${sid}.bif - GDT.geojson"
  [ -f "$gj" ] || gj="$ANOT/${sid}.bif GDT.geojson"

  wsi="$WSI/$sid/${sid}.bif"
  echo ""
  echo "================================================================"
  echo "[$i/$n] $sid"
  echo "   geojson: $(basename "$gj")"
  echo "================================================================"
  if [ ! -f "$gj" ];  then echo "   !! falta el geojson con los dos patrones probados"; FAIL=$((FAIL+1)); FALLIDAS+=("$sid (sin geojson)"); continue; fi
  if [ ! -f "$wsi" ]; then echo "   !! falta la WSI: $wsi"; FAIL=$((FAIL+1)); FALLIDAS+=("$sid (sin WSI)"); continue; fi
  "$PYBIN" "$REPO/scripts/alinear_anotaciones_qupath.py" \
      --geojson "$gj" --slide_id "$sid" --wsi "$wsi" --out "$OUT" 2>&1
  if [ -s "$OUT/offset_${sid}.json" ]; then OK=$((OK+1)); else FAIL=$((FAIL+1)); FALLIDAS+=("$sid (sin offset al salir)"); fi
done

echo ""
echo "== listo   OK=$OK  SKIP=$SKIP  FALLO=$FAIL  de $n =="
if [ ${#FALLIDAS[@]} -gt 0 ]; then
  echo "Fallidas:"
  for f in "${FALLIDAS[@]}"; do echo "   $f"; done
fi
echo "--- offsets y su flag de alineacion ---"
for sid in "${SLIDES[@]}"; do
  f="$OUT/offset_${sid}.json"
  if [ -s "$f" ]; then
    printf "  %-12s %s\n" "$sid" "$("$PYBIN" -c "import json,sys; d=json.load(open(sys.argv[1])); print(f\"dx={d.get('dx')} dy={d.get('dy')} alineada={d.get('alineada')}\")" "$f")"
  else
    printf "  %-12s SIN OFFSET\n" "$sid"
  fi
done
date -Is
