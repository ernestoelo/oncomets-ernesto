#!/bin/bash
#SBATCH --job-name=eg_hn129741
#SBATCH --output=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/logs/%x_%j.out
#SBATCH --error=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/logs/%x_%j.err
#SBATCH --chdir=/media/administrador/Storage1/sdonoso/clam_testing2/hover_next_reference
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=16
#SBATCH --mem=96G
#SBATCH --time=12:00:00
# (sin --partition -> usa la default 'debug')
#
# Fase 2 del plan del 17-ago: HoVer-NeXt sobre la 129741 COMPLETA, un juego de pesos por
# submission. Los brazos restringidos NO se corren aca: salen de enmascarar esta salida
# post-hoc (fase 3). Ver plan_semana_17ago.md y auditoria_codigo.md.
#
# Se lanza una vez por juego de pesos. OJO: `--export` de SLURM separa variables por COMA,
# asi que el ensemble de PanNuke (que main.py:76 espera como lista con comas) NO puede
# viajar con comas. Se pasa con '+' y este script lo traduce (ver CP mas abajo).
#   sbatch --export=ALL,CP=lizard_convnextv2_tiny,TAG=lizard_mitosis  scripts/run_hovernext_129741.slurm
#   sbatch --export=ALL,CP=pannuke_convnextv2_tiny_1+pannuke_convnextv2_tiny_2+pannuke_convnextv2_tiny_3,TAG=pannuke \
#          scripts/run_hovernext_129741.slurm
#
# --chdir va al repo de HoVer-NeXt porque main.py resuelve los pesos como
# dirname(__file__)/<cp> (main.py:74-77). TODA la salida va por --output_root ABSOLUTO a
# clam_testing2/, asi que el containment se respeta igual.

set -uo pipefail   # SIN -e: ver workaround D (SIGPIPE 141 en diagnosticos pipelined)

REPO=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto
HN=/media/administrador/Storage1/sdonoso/clam_testing2/hover_next_reference
ENVP=/media/administrador/Storage1/sdonoso/clam_testing2/envs/hovernext
PY=$ENVP/bin/python
# openslide-python busca libopenslide por ctypes y NO la encuentra si el env no esta
# "activado". Se invoca por binario absoluto (workaround B), asi que la biblioteca se
# expone a mano en vez de con `conda activate` (que ademas no arregla el PATH, ver
# workaround B). Verificado 17-ago: sin esto, `import openslide` tira
# OSError: libopenslide.so.0: cannot open shared object file.
export LD_LIBRARY_PATH=$ENVP/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}
WSI=/media/administrador/Storage1/sdonoso/wsi/129741/129741.bif

CP=${CP:-lizard_convnextv2_tiny}
# `--export` de SLURM parte por comas, asi que un CP multi-checkpoint llega partido en
# variables basura. Se pasa con '+' y se traduce a la coma que espera main.py:76
# (`--cp` es una lista que promedia como ensemble; asi reporta PanNuke el paper).
# Idempotente: un CP de un solo checkpoint pasa intacto.
CP=${CP//+/,}
TAG=${TAG:-lizard_mitosis}
METRIC=${METRIC:-f1}
TTA=${TTA:-4}
BATCH=${BATCH:-32}

OUTROOT=$REPO/results/b8_hovernext_129741/hovernext/$TAG

echo "================================================================"
echo "job $SLURM_JOB_ID  |  $(date)"
echo "  CP=$CP  TAG=$TAG  METRIC=$METRIC  TTA=$TTA  BATCH=$BATCH"
echo "  salida: $OUTROOT"
echo "================================================================"
nvidia-smi --query-gpu=name,memory.used,memory.total --format=csv || true
echo "--- quien mas esta en el nodo (afecta el reloj, no la metrica) ---"
squeue || true
echo "================================================================"

# ---------- PREFLIGHT OBLIGATORIO (workaround G) ----------
"$PY" "$REPO/scripts/preflight_hovernext.py" \
    --cp "$CP" --input "$WSI" --output-root "$OUTROOT" \
    --metric "$METRIC" --keep-raw 1
if [ $? -ne 0 ]; then
    echo "PREFLIGHT FALLIDO -> se aborta sin gastar GPU"
    exit 1
fi

# ---------- LA CORRIDA ----------
# --keep_raw es OBLIGATORIO: sin el, main.py:121-126 borra los zarr _inst (BCB-map) y
# _cls (raw class), que son el insumo de la fase 2.b. Ver auditoria_codigo.md §5.
cd "$HN" || exit 1
START=$(date +%s)

"$PY" main.py \
    --input "$WSI" \
    --output_root "$OUTROOT" \
    --cp "$CP" \
    --metric "$METRIC" \
    --tta "$TTA" \
    --batch_size "$BATCH" \
    --inf_workers 12 \
    --inf_writers 2 \
    --pp_workers 14 \
    --pp_tiling 8 \
    --keep_raw
RC=$?

END=$(date +%s)
echo "================================================================"
echo "exit code de main.py: $RC   (2 = salio por --only_inference; 0 = completo)"
echo "TIEMPO DE PARED: $((END-START)) s = $(( (END-START)/60 )) min"
echo "  ^ dato pedido por el plan: contrasta con las 3 h 36 medidas de HoVer-Net (job 4714)"
echo "--- salida producida ---"
ls -lhR "$OUTROOT" 2>/dev/null | head -40
du -sh "$OUTROOT" 2>/dev/null
echo "--- GPU al cierre ---"
nvidia-smi --query-gpu=memory.used --format=csv || true
date
