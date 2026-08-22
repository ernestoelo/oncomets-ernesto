#!/bin/bash
#SBATCH --job-name=eg_hn_11laminas
#SBATCH --output=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/logs/%x_%j.out
#SBATCH --error=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/logs/%x_%j.err
#SBATCH --chdir=/media/administrador/Storage1/sdonoso/clam_testing2/hover_next_reference
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=16
#SBATCH --mem=96G
#SBATCH --time=5:00:00
# (sin --partition -> usa la default 'debug')
#
# ==============================================================================
# B1 — encargo 4 de Sebastian: HoVer-NeXt sobre las 11 laminas anotadas que
# faltan. Generaliza run_hovernext_129741.slurm a un BUCLE dentro de UN SOLO job,
# para tomar el token de GPU una vez (hay uno solo y con cola de terceros).
#
# POR QUE IMPORTA: lleva el denominador de 26 marcas a 94. No es "cubrir mas
# superficie": es lo que convierte un numero de UNA lamina en un numero medible.
# A3 ya dejo todo lo que necesita (offsets, CSVs por lamina, y el techo 94/94).
#
# SIN --keep_raw, a proposito: ~142 MB por lamina en vez de ~10,5 GB (1,6 GB
# total contra 121 GB). El raw solo hacia falta para la pregunta de
# segmentado-pero-mal-clasificado (A0), y el de la 129741 ya esta en disco.
#
# PRESUPUESTO (medido, no estimado a ojo): la 129741 tardo 18 min y tiene 3199 Mpx.
# Las 11 suman 17.3 Gpx = 5.4x => ~103 min = 1,7 h. Las 12 laminas comparten que NO
# exponen 'thumbnail', asi que las 12 teselan el LIENZO ENTERO y los 18 min ya incluyen
# eso: la extrapolacion es apples-to-apples. --time=5:00:00 = ~3x, que cubre el caso de
# compartir GPU con jobs de terceros (documentado: puede duplicar el reloj, no la metrica).
#
# Reanudable: salta la lamina que ya tenga su marca .done, que se escribe DESPUES
# de que main.py salga 0 (workaround J: marcar con el artefacto FINAL, nunca con
# uno intermedio, que daria por completa una corrida cortada a mitad).
#
# Workarounds aplicados: B (binario absoluto), D (set -uo sin -e), G (preflight
# por lamina antes de gastar GPU), K (libopenslide parchada), M (whitelist de
# extension -> symlink .tif), L (--time real), L.a (CP con '+' en vez de coma).
#
#   sbatch scripts/run_hovernext_slides.slurm
#   sbatch --export=ALL,CP=lizard_convnextv2_tiny,TAG=lizard_mitosis scripts/run_hovernext_slides.slurm
# ==============================================================================

set -uo pipefail   # SIN -e: workaround D

REPO=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto
HN=/media/administrador/Storage1/sdonoso/clam_testing2/hover_next_reference
ENVP=/media/administrador/Storage1/sdonoso/clam_testing2/envs/hovernext
PY=$ENVP/bin/python
WSI_ROOT=/media/administrador/Storage1/sdonoso/wsi
SHIM=/media/administrador/Storage1/sdonoso/clam_testing2/wsi_shim

# workaround K: openslide-python busca libopenslide por ctypes y no la encuentra sin
# "activar" el env. Se invoca por binario absoluto (workaround B) => se expone a mano.
export LD_LIBRARY_PATH=$ENVP/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}

CP=${CP:-lizard_convnextv2_tiny}
CP=${CP//+/,}          # workaround L.a: --export parte por comas
TAG=${TAG:-lizard_mitosis}
METRIC=${METRIC:-f1}
TTA=${TTA:-4}
BATCH=${BATCH:-32}

OUTBASE=$REPO/results/b8_hovernext_12laminas/hovernext/$TAG

# Las 11 que faltan. La 129741 NO esta: ya corrio (job 5008) y su salida vive en
# results/b8_hovernext_129741/. El agregado de las 12 se arma en CPU despues.
# Ordenadas por nº de marcas de Mitosis, de mayor a menor: si el job se corta por
# tiempo, lo que quede afuera es lo que menos mueve el denominador.
SLIDES=(126504 128194 124729 124806 B25-158899 144317 164001 106552 103762 109609 110616)
MARCAS=(20     17     8      6      6          3      3      2      1      1      1)

mkdir -p "$SHIM" "$OUTBASE" "$REPO/logs" || exit 1

echo "================================================================"
echo "B1 — HoVer-NeXt sobre las 11 laminas anotadas restantes"
echo "  job $SLURM_JOB_ID  |  $(date -Is)  |  $(hostname)"
echo "  CP=$CP  TAG=$TAG  METRIC=$METRIC  TTA=$TTA  BATCH=$BATCH"
echo "  laminas: ${#SLIDES[@]}   marcas que aportan: 68  (+26 de la 129741 = 94)"
echo "  salida: $OUTBASE"
echo "  SIN --keep_raw"
echo "================================================================"
nvidia-smi --query-gpu=name,memory.used,memory.total --format=csv | head -5 || true
echo "--- quien mas esta en el nodo (afecta el reloj, no la metrica) ---"
squeue || true
echo "================================================================"

N_OK=0; N_SKIP=0; N_FAIL=0
FALLIDAS=()
T0=$(date +%s)

for i in "${!SLIDES[@]}"; do
    SID="${SLIDES[$i]}"
    OUT="$OUTBASE/$SID"
    DONE="$OUT/.done"
    echo ""
    echo "────────────────────────────────────────────────────────────────"
    echo "[$((i+1))/${#SLIDES[@]}] $SID   (${MARCAS[$i]} marcas de Mitosis)   $(date -Is)"
    echo "────────────────────────────────────────────────────────────────"

    if [ -f "$DONE" ]; then
        echo "  ya esta hecha (.done presente) -> se salta"
        N_SKIP=$((N_SKIP+1)); continue
    fi

    WSI_REAL="$WSI_ROOT/$SID/$SID.bif"
    if [ ! -f "$WSI_REAL" ]; then
        echo "  ERROR: no existe $WSI_REAL"
        N_FAIL=$((N_FAIL+1)); FALLIDAS+=("$SID (sin WSI)"); continue
    fi

    # workaround M: la whitelist de extension de data_utils.py:234-242 rechaza el .bif
    # aunque openslide lo abra bien. Symlink .tif bajo containment, sin tocar el repo
    # de referencia (REFERENCE ONLY).
    ln -sfn "$WSI_REAL" "$SHIM/$SID.tif"
    WSI="$SHIM/$SID.tif"

    # workaround G: preflight ANTES de gastar GPU. Chequea que openslide elija el driver
    # ventana (y no caiga a generic-tiff, que perderia el mpp) y que los pesos existan.
    "$PY" "$REPO/scripts/preflight_hovernext.py" \
        --cp "$CP" --input "$WSI" --output-root "$OUT" \
        --metric "$METRIC" --keep-raw 0 --sin-raw-a-proposito
    if [ $? -ne 0 ]; then
        echo "  PREFLIGHT FALLIDO -> se salta la lamina sin gastar GPU"
        N_FAIL=$((N_FAIL+1)); FALLIDAS+=("$SID (preflight)"); continue
    fi

    cd "$HN" || exit 1
    S0=$(date +%s)
    "$PY" main.py \
        --input "$WSI" \
        --output_root "$OUT" \
        --cp "$CP" \
        --metric "$METRIC" \
        --tta "$TTA" \
        --batch_size "$BATCH" \
        --inf_workers 12 \
        --inf_writers 2 \
        --pp_workers 14 \
        --pp_tiling 8
    RC=$?
    S1=$(date +%s)

    if [ "$RC" -eq 0 ]; then
        # La marca se escribe SOLO si main.py salio 0, y va con la procedencia adentro
        # para que una corrida cortada no pase por completa (workaround J).
        {
          echo "slide_id=$SID"
          echo "cp=$CP  tag=$TAG  metric=$METRIC  tta=$TTA  batch=$BATCH"
          echo "keep_raw=0"
          echo "job=${SLURM_JOB_ID:-NA}"
          echo "fin=$(date -Is)"
          echo "segundos=$((S1-S0))"
        } > "$DONE"
        echo "  OK en $(( (S1-S0)/60 )) min $(( (S1-S0)%60 )) s"
        if [ -f "$OUT/pred_mitosis.tsv" ]; then
            echo "  detecciones de mitosis: $(( $(wc -l < "$OUT/pred_mitosis.tsv") - 1 ))"
        else
            echo "  !! no hay pred_mitosis.tsv (revisar: el --metric puede estar mal)"
        fi
        du -sh "$OUT" 2>/dev/null
        N_OK=$((N_OK+1))
    else
        echo "  FALLO: main.py devolvio rc=$RC tras $(( (S1-S0)/60 )) min"
        N_FAIL=$((N_FAIL+1)); FALLIDAS+=("$SID (rc=$RC)")
    fi
done

T1=$(date +%s)
echo ""
echo "================================================================"
echo "TERMINADO  OK=$N_OK  SKIP=$N_SKIP  FALLO=$N_FAIL  de ${#SLIDES[@]}"
echo "TIEMPO DE PARED TOTAL: $(( (T1-T0)/60 )) min"
if [ ${#FALLIDAS[@]} -gt 0 ]; then
    echo "Fallidas:"
    for f in "${FALLIDAS[@]}"; do echo "   $f"; done
    echo "  -> relanzar el mismo .slurm: las OK se saltan por su .done"
fi
echo "--- inventario ---"
du -sh "$OUTBASE" 2>/dev/null
for s in "${SLIDES[@]}"; do
    if [ -f "$OUTBASE/$s/pred_mitosis.tsv" ]; then
        printf "  %-12s %6d detecciones\n" "$s" "$(( $(wc -l < "$OUTBASE/$s/pred_mitosis.tsv") - 1 ))"
    else
        printf "  %-12s %s\n" "$s" "SIN SALIDA"
    fi
done
echo "--- GPU al cierre ---"
nvidia-smi --query-gpu=memory.used --format=csv | head -3 || true
date -Is
echo "================================================================"
[ "$N_FAIL" -eq 0 ]
