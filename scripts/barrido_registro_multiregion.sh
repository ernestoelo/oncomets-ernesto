#!/bin/bash
# Barrido del test de REGISTRO sobre las laminas multi-region de la cohorte privada.
#
# Que hace: corre `auditar_regiones_escaneo.py registro` lamina por lamina, en CPU,
# y deja el veredicto por lamina en un JSON. El test decide si las DOS regiones de
# escaneo de un .bif son los MISMOS PIXELES (re-escaneo de la misma lamina) o dos
# secciones seriadas del mismo bloque. Ver el criterio pre-fijado en el docstring de
# `registro()` (auditar_regiones_escaneo.py:591-601).
#
# Por que un driver y no un for a mano:
#   - workaround J: se lanza DESATADO (setsid) o muere al cerrar la sesion.
#   - REANUDABLE por el artefacto FINAL (registro_<sid>.json, que el script escribe
#     en su ultima linea). Un `<sid>.stop` marca las que el script rechaza, para no
#     re-pagarlas en cada reanudacion.
#
# NO toca el script auditado: lo invoca por CLI y MUEVE su salida al subdirectorio
# del barrido. Asi `auditar_regiones_escaneo.py` queda byte-identico al que produjo
# el resultado de la 129741 y ese resultado sigue siendo reproducible.
#
# Uso:
#   setsid nohup bash scripts/barrido_registro_multiregion.sh > logs/barrido_registro_desatado.log 2>&1 < /dev/null &
#   ps -eo pid,ppid,sid,cmd | grep barrido_registro   # ppid debe ser 1
#
# Variables (todas opcionales):
#   ROT_MAX   barrido de rotacion de la etapa B, en grados (default 8.0)
#   ROT_A_MAX barrido de rotacion de la ETAPA A, en grados (default 0 = apagado,
#             comportamiento original). Ver el docstring de _buscar_local: medido
#             el 17-ago, el |theta| necesario tuvo mediana 7.8 grados y 6 de 12
#             laminas "no medibles" pasan a medibles al barrerlo.
#   OUT_DIR   subdirectorio de salida (default barrido_138). Una corrida con
#             ROT_A_MAX distinto NO debe pisar barrido_138, que es la verdad de
#             campo versionada del barrido sin rotacion.
#   SALTAR_129741  1 = excluir la 129741 (default 1, como el barrido original)
#   LIMITE    procesar solo las primeras N pendientes (default 0 = todas)

set -uo pipefail   # SIN -e: una lamina que falla no puede matar el barrido

REPO=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto
PY=/home/sdonoso/miniconda3/envs/clam_latest/bin/python
SCRIPT=$REPO/scripts/auditar_regiones_escaneo.py
BASE=$REPO/sprints/B8_sprint8/anotaciones_patologo/regiones_escaneo
CSV=$BASE/laminas_multiregion.csv
OUT=$BASE/${OUT_DIR:-barrido_138}
LOGS=$OUT/logs

ROT_MAX=${ROT_MAX:-8.0}
ROT_A_MAX=${ROT_A_MAX:-0.0}
SALTAR_129741=${SALTAR_129741:-1}
LIMITE=${LIMITE:-0}

mkdir -p "$OUT" "$LOGS"

echo "================================================================"
echo "barrido de registro multi-region  |  $(date)"
echo "  ROT_MAX=$ROT_MAX  ROT_A_MAX=$ROT_A_MAX  LIMITE=$LIMITE"
echo "  salida: $OUT"
echo "  pid=$$  ppid=$PPID  (ppid debe ser 1 si se lanzo con setsid)"
echo "================================================================"

# --- lista de laminas: solo las de EXACTAMENTE 2 regiones ---
# El subcomando `registro` aborta con "[stop] tiene N regiones, no 2"
# (auditar_regiones_escaneo.py:615-617). Las de 3 y 4 regiones quedan fuera por
# construccion del test, no por descarte nuestro: el test compara UN par.
SLIDES=$("$PY" - "$CSV" "$SALTAR_129741" <<'EOF'
import csv, sys
saltar = sys.argv[2] == "1"
for r in csv.DictReader(open(sys.argv[1])):
    if r["n_regiones"] == "2" and not (saltar and r["slide_id"] == "129741"):
        print(r["slide_id"])
EOF
)

TOTAL=$(echo "$SLIDES" | grep -c .)
echo "[lista] $TOTAL laminas de 2 regiones (la 129741 ya esta hecha y no se re-mide)"
echo

HECHAS=0; NUEVAS=0; SALTADAS=0; FALLIDAS=0; PARADAS=0; INTENTOS=0
T0=$(date +%s)

for SID in $SLIDES; do
    # --- reanudable: el JSON es el artefacto FINAL, el .stop marca las rechazadas ---
    if [ -f "$OUT/registro_$SID.json" ]; then
        HECHAS=$((HECHAS+1)); SALTADAS=$((SALTADAS+1)); continue
    fi
    if [ -f "$OUT/$SID.stop" ]; then
        SALTADAS=$((SALTADAS+1)); continue
    fi
    # LIMITE cuenta laminas INTENTADAS, no exitosas: una lamina que el test
    # rechaza igual consumio tiempo, y si contaramos exitos un lote de prueba
    # podria recorrer la cohorte entera buscando la N-esima que pase.
    if [ "$LIMITE" -gt 0 ] && [ "$INTENTOS" -ge "$LIMITE" ]; then
        echo "[limite] alcanzado LIMITE=$LIMITE laminas intentadas, se corta"; break
    fi
    INTENTOS=$((INTENTOS+1))

    TS=$(date +%s)
    echo "[$(date +%H:%M:%S)] $SID  ..."
    "$PY" "$SCRIPT" registro --slide "$SID" --rot-max "$ROT_MAX" \
        --rot-a-max "$ROT_A_MAX" \
        > "$LOGS/$SID.log" 2>&1
    RC=$?
    DT=$(( $(date +%s) - TS ))

    # el script escribe en su OUT_DIR plano; lo mudamos al subdir del barrido
    for F in "$BASE/registro_$SID.json" "$BASE/${SID}_registro_level0.png"; do
        [ -f "$F" ] && mv "$F" "$OUT/"
    done

    if [ -f "$OUT/registro_$SID.json" ]; then
        NUEVAS=$((NUEVAS+1)); HECHAS=$((HECHAS+1))
        RES=$(grep -E "^\[resumen\]" "$LOGS/$SID.log" | tr '\n' ' ')
        echo "    ok en ${DT}s  $RES"
    elif grep -q "^\[stop\]" "$LOGS/$SID.log"; then
        PARADAS=$((PARADAS+1))
        grep -m1 "^\[stop\]" "$LOGS/$SID.log" > "$OUT/$SID.stop"
        echo "    STOP en ${DT}s: $(cat "$OUT/$SID.stop")"
    else
        FALLIDAS=$((FALLIDAS+1))
        echo "    FALLO en ${DT}s (rc=$RC), ultimas lineas:"
        tail -4 "$LOGS/$SID.log" | sed 's/^/      /'
    fi

    PEND=$((TOTAL - HECHAS - PARADAS - FALLIDAS))
    if [ "$NUEVAS" -gt 0 ]; then
        MEDIA=$(( ($(date +%s) - T0) / NUEVAS ))
        echo "    progreso: $HECHAS ok / $PARADAS stop / $FALLIDAS fallo / $PEND pendientes"
        echo "    media ${MEDIA}s por lamina -> ETA $(( PEND * MEDIA / 60 )) min"
    fi
done

echo
echo "================================================================"
echo "FIN  |  $(date)  |  $(( ($(date +%s) - T0) / 60 )) min de pared"
echo "  con JSON: $HECHAS   nuevas esta corrida: $NUEVAS   saltadas: $SALTADAS"
echo "  stop (rechazadas por el test): $PARADAS   fallidas: $FALLIDAS"
echo "  salida en: $OUT"
echo "================================================================"
