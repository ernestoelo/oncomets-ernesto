"""cruce_94_marcas.py — el cruce de HoVer-NeXt contra las 94 marcas de las 12 laminas.

Generaliza a las doce laminas anotadas lo que `cruce_hovernext_marcas.py` hizo sobre la
129741 sola (26 marcas). No lo reemplaza: aquel script sostiene la regresion del caso de
referencia y ademas cruza el segundo factor con la mascara de atencion, que aqui no
aplica porque las otras once no tienen `atencion_por_parche.npz`.

Lo que se reusa por import y NO se re-implementa: `marcas_mitosis()` (centroides de los
poligonos de Mitosis mas el offset), `emparejar_pares()` (hungaro con corte, uno a uno),
`TOLS_UM` y `TOL_ADOPTADA_UM`.

Reglas que gobiernan la lectura (no son adorno):

- La unidad es **marcas** (94). No parches (28 en la 129741), no detecciones (732 = 177 +
  555), no poligonos (472 anotaciones en total).
- Las marcas son **positivos parciales**: lo no marcado NO es negativo. Por eso se reporta
  **recall y nada mas**. No se calcula precision ni se llama falso positivo a ninguna
  deteccion sin marca.
- Un recall agregado **no es el recall de HoVer-NeXt**: el denominador son las marcadas.
- **Seis laminas tienen <=3 marcas** y tres concentran 63 de las 94. El numero que se lee
  es el agregado; el per-lamina va con su `n` y no es una medicion independiente.
- El geojson **no esta en coordenadas de openslide**: se le suma el offset por lamina que
  derivo `alinear_anotaciones_qupath.py` (A3, 21-ago). Los doce tienen dy=0.
- **Dos laminas tienen dos regiones de escaneo** (129741 y B25-158899). El confinamiento
  se reporta, y no altera el emparejamiento: la region contraria esta a decenas de miles
  de pixeles, muy lejos de la mayor tolerancia barrida (300 um = 645 px).

Uso:
  PYTHONPATH=/media/administrador/Storage1/sdonoso/clam_testing2/.pylibs \
  /home/sdonoso/miniconda3/envs/clam_latest/bin/python scripts/cruce_94_marcas.py
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
from cruce_hovernext_marcas import (                                       # noqa: E402
    TOL_ADOPTADA_UM,
    TOLS_UM,
    emparejar_pares,
    marcas_mitosis,
)

ANOTACIONES = Path("/media/administrador/Storage1/sdonoso/anotaciones")

# Las doce laminas anotadas por el patologo, ordenadas por numero de marcas (descendente),
# que es como se leen: las tres primeras concentran 63 de las 94.
#
# OJO con el glob sobre `anotaciones/`: hay TRECE geojson. El extra es
# `103762.bif - Series 0-full.geojson`, y contarlo daria 95 marcas en vez de 94. Por eso la
# lista es explicita y el sufijo es siempre " - GDT".
SLIDES = ["129741", "126504", "128194", "124729", "124806", "B25-158899",
          "144317", "164001", "106552", "103762", "109609", "110616"]

# La region de escaneo que contiene las anotaciones, como intervalo [y_min, y_max) en px de
# level 0. Solo dos de las doce tienen mas de una region (`regiones_por_slide.csv`); las
# otras diez van sin confinamiento. Es el pendiente que `techo_atencion_topk.py:45` dejo
# como constante de modulo, y aqui queda por lamina.
#
# OJO con la DIRECCION, que no es la misma en las dos: en la 129741 el patologo anoto la
# region de ABAJO (region[1], y>=49920) y en la B25-158899 la de ARRIBA (region[0],
# y<25600). Un corte escalar tipo `y >= Y_CORTE` sirve para una y da vuelta la otra, asi
# que se guarda el intervalo entero y se VERIFICA que las marcas caigan dentro.
REGION_ANOTADA = {"129741": (49920, 80640), "B25-158899": (0, 25600)}

# Las doce son de la cohorte privada: Ventana a 20x, 0,465 um/px verificado en las doce
# ([[cohortes-magnificacion-fisica]]).
MPP = 0.465

# La 129741 se corrio sola (job 5008) y las once restantes en un barrido (job 5070), que
# escribio el slide_id ANIDADO DOS VECES. No es un error de este script.
JOB_129741, JOB_11 = 5008, 5070


def paths_de(slide: str) -> dict:
    if slide == "129741":
        tsv = REPO / "results/b8_hovernext_129741/hovernext/lizard_mitosis/129741/pred_mitosis.tsv"
    else:
        tsv = (REPO / "results/b8_hovernext_12laminas/hovernext/lizard_mitosis"
               / slide / slide / "pred_mitosis.tsv")
    return dict(
        geojson=ANOTACIONES / f"{slide}.bif - GDT.geojson",
        tsv=tsv,
        offset=REPO / "sprints/B8_sprint8/anotaciones_patologo" / f"offset_{slide}.json",
    )


def leer_detecciones(tsv: Path) -> np.ndarray:
    with open(tsv) as fh:
        return np.asarray([[float(r["x"]), float(r["y"])]
                           for r in csv.DictReader(fh, delimiter="\t")], dtype=float)


def regresion_129741(escalera: dict, ref_csv: Path) -> list[str]:
    """La 129741 tiene que reproducir su escalera del B8, o hay un bug de generalizacion.

    No es un chequeo cosmetico: si el offset, el sufijo del geojson o el path del tsv se
    generalizaron mal, aqui se cae antes de que nadie lea un numero.
    """
    fallos = []
    with open(ref_csv) as fh:
        for r in csv.DictReader(fh):
            t, esperado = float(r["tolerancia_um"]), int(r["tp"])
            obtenido = escalera.get(t)
            if obtenido != esperado:
                fallos.append(f"    tol {t:g} um: esperado tp={esperado}, obtenido {obtenido}")
    return fallos


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(REPO / "results/b9_cruce_94"))
    ap.add_argument("--mpp", type=float, default=MPP)
    a = ap.parse_args()

    import pandas as pd                                                    # noqa: E402

    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    mpp = a.mpp

    print("=" * 78)
    print("CRUCE HoVer-NeXt x LAS 94 MARCAS DEL PATOLOGO — las 12 laminas anotadas")
    print("=" * 78)
    print("unidad = MARCAS. No parches, no detecciones, no poligonos.")
    print("positivos parciales: se reporta recall y nada mas; no hay precision ni FP.\n")

    filas, tp_agregado = [], {t: 0 for t in TOLS_UM}
    escaleras = []          # forma larga: permite recomputar cualquier subconjunto
    escalera_129741 = {}
    n_marcas_total = n_det_total = 0

    print(f"  {'lamina':<12} {'marcas':>6} {'detec.':>7} {'en reg.':>8} {'TP@30':>6} "
          f"{'recall':>8} {'dmin p50':>9}")
    for slide in SLIDES:
        p = paths_de(slide)
        for k, v in p.items():
            if not Path(v).exists():
                raise SystemExit(f"falta {k} de {slide}: {v}")

        off = json.loads(Path(p["offset"]).read_text())
        marcas, lados = marcas_mitosis(str(p["geojson"]), off["dx"], off["dy"])
        det = leer_detecciones(p["tsv"])

        if len(marcas) == 0:
            raise SystemExit(f"{slide}: 0 marcas de Mitosis leidas — offset o geojson mal")
        if len(det) == 0:
            raise SystemExit(f"{slide}: 0 detecciones — el tsv esta vacio")

        region = REGION_ANOTADA.get(slide)
        if region is None:
            en_reg_marcas = np.ones(len(marcas), bool)
            en_reg_det = np.ones(len(det), bool)
        else:
            y0, y1 = region
            en_reg_marcas = (marcas[:, 1] >= y0) & (marcas[:, 1] < y1)
            en_reg_det = (det[:, 1] >= y0) & (det[:, 1] < y1)
            if not en_reg_marcas.all():
                raise SystemExit(
                    f"{slide}: {(~en_reg_marcas).sum()}/{len(marcas)} marcas caen FUERA de "
                    f"la region declarada [{y0}, {y1}) — el intervalo esta mal")
        marcas_en_region, det_en_region = int(en_reg_marcas.sum()), int(en_reg_det.sum())

        dist = np.linalg.norm(marcas[:, None, :] - det[None, :, :], axis=2)
        dmin = dist.min(axis=1)

        escalera = {}
        for t_um in TOLS_UM:
            ok, _ = emparejar_pares(dist, t_um / mpp)
            escalera[t_um] = int(ok.sum())
            tp_agregado[t_um] += int(ok.sum())
            escaleras.append(dict(slide_id=slide, tolerancia_um=t_um, tp=int(ok.sum()),
                                  n=len(marcas),
                                  recall=round(float(ok.sum()) / len(marcas), 4)))
        if slide == "129741":
            escalera_129741 = escalera

        ok, pares = emparejar_pares(dist, TOL_ADOPTADA_UM / mpp)
        pd.DataFrame([
            dict(marca=i,
                 x=round(float(marcas[i, 0]), 1), y=round(float(marcas[i, 1]), 1),
                 lado_px=round(float(lados[i]), 1),
                 en_region_anotada=bool(en_reg_marcas[i]),
                 dmin_px=round(float(dmin[i]), 1), dmin_um=round(float(dmin[i]) * mpp, 1),
                 acreditada=bool(ok[i]),
                 deteccion=int(pares[i]),
                 det_x=round(float(det[pares[i], 0]), 1) if pares[i] >= 0 else "",
                 det_y=round(float(det[pares[i], 1]), 1) if pares[i] >= 0 else "")
            for i in range(len(marcas))
        ]).to_csv(out / f"pares_{slide}.csv", index=False)

        filas.append(dict(
            slide_id=slide, marcas=len(marcas), detecciones=len(det),
            marcas_en_region_anotada=marcas_en_region,
            detecciones_en_region_anotada=det_en_region,
            region_anotada=f"[{region[0]}, {region[1]})" if region else "",
            tp_30um=int(ok.sum()), recall_30um=round(float(ok.sum()) / len(marcas), 4),
            dmin_mediana_um=round(float(np.median(dmin)) * mpp, 1),
            lado_mediano_um=round(float(np.median(lados)) * mpp, 1),
            dx=off["dx"], dy=off["dy"],
        ))
        n_marcas_total += len(marcas)
        n_det_total += len(det)
        print(f"  {slide:<12} {len(marcas):>6} {len(det):>7} {det_en_region:>8} "
              f"{ok.sum():>6} {ok.sum()/len(marcas):>8.1%} "
              f"{np.median(dmin)*mpp:>8.1f}u")

    pd.DataFrame(filas).to_csv(out / "por_lamina.csv", index=False)
    pd.DataFrame(escaleras).to_csv(out / "recall_por_tolerancia_por_lamina.csv", index=False)

    # ---------------- el agregado, que es el numero que se lee ----------------
    print(f"\nrecall AGREGADO sobre las {n_marcas_total} marcas, emparejamiento UNO A UNO:")
    print(f"  {'tol um':>7} {'tol px':>7} {'TP':>4} {'recall':>8}")
    agg = []
    for t_um in TOLS_UM:
        tp = tp_agregado[t_um]
        agg.append(dict(tolerancia_um=t_um, tolerancia_px=round(t_um / mpp, 1),
                        tp=tp, n=n_marcas_total, recall=round(tp / n_marcas_total, 4)))
        print(f"  {t_um:7.1f} {t_um/mpp:7.1f} {tp:4d} {tp/n_marcas_total:8.1%}")
    pd.DataFrame(agg).to_csv(out / "recall_por_tolerancia_agregado.csv", index=False)

    tp30 = tp_agregado[TOL_ADOPTADA_UM]
    print(f"\nSe adopta {TOL_ADOPTADA_UM:g} um: {tp30}/{n_marcas_total} = "
          f"{tp30/n_marcas_total:.1%}")

    # ---------------- chequeos que decidn si esto se puede leer ----------------
    print("\n" + "=" * 78)
    print("CHEQUEOS")
    print("=" * 78)
    errores = []
    for nombre, obtenido, esperado in (("marcas", n_marcas_total, 94),
                                       ("detecciones", n_det_total, 732)):
        ok_chk = obtenido == esperado
        print(f"  suma de {nombre:<12} {obtenido:>5}  esperado {esperado:>5}  "
              f"{'OK' if ok_chk else 'FALLA'}")
        if not ok_chk:
            errores.append(f"suma de {nombre}: {obtenido} != {esperado}")

    ref = REPO / "results/b8_hovernext_129741/cruce_marcas/recall_por_tolerancia.csv"
    fallos = regresion_129741(escalera_129741, ref)
    print(f"  regresion 129741 contra {ref.name}: "
          f"{'OK (escalera identica)' if not fallos else 'FALLA'}")
    for f in fallos:
        print(f)
    errores += fallos

    meta = dict(
        que_es="recall de deteccion de HoVer-NeXt contra las 94 marcas de Mitosis del "
               "patologo, sobre las 12 laminas anotadas",
        unidad="marcas de Mitosis",
        no_es=["precision de HoVer-NeXt",
               "el recall de HoVer-NeXt: el denominador son LAS MARCADAS, no las mitosis "
               "que hay en la lamina",
               "una medida por lamina: seis laminas tienen <=3 marcas",
               "parches (28 en la 129741), detecciones (732) ni poligonos (472)"],
        n_laminas=len(SLIDES), n_marcas=n_marcas_total, n_detecciones=n_det_total,
        tolerancia_adoptada_um=TOL_ADOPTADA_UM, tolerancias_barridas_um=TOLS_UM,
        tp_adoptada=tp30, recall_adoptada=round(tp30 / n_marcas_total, 4),
        mpp=mpp, emparejamiento="hungaro uno a uno con corte por tolerancia",
        procedencia=dict(
            job_129741=JOB_129741, job_11_laminas=JOB_11,
            pesos="lizard_mitosis (la unica de los dos juegos con clase de mitosis)",
            geojson=str(ANOTACIONES) + "/<slide>.bif - GDT.geojson",
            offsets="sprints/B8_sprint8/anotaciones_patologo/offset_<slide>.json (A3, 21-ago)",
            offsets_dx={f["slide_id"]: f["dx"] for f in filas},
            region_anotada=REGION_ANOTADA,
        ),
        regresion_129741="OK" if not fallos else "FALLA",
        chequeos_fallidos=errores,
    )
    (out / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    print(f"\nSalida: {out}")

    if errores:
        raise SystemExit("\nHAY CHEQUEOS FALLIDOS: es un bug de la generalizacion, "
                         "no un resultado.")


if __name__ == "__main__":
    main()
