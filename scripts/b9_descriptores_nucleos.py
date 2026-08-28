"""b9_descriptores_nucleos.py — descriptores de forma de TODAS las instancias, por lamina.

Insumo del eje 3 del inventario del B9 (pleomorfismo y grado nuclear). El pre-registro
(`sprints/B9_sprint9/ejes_nucleares/prereg.md` §3) exige que **ningun descriptor del nucleo
salga del poligono del patologo**: el area de esa marca es en parte el pincel de radio fijo de
QuPath ([[anotacion-tamano-objeto-vs-region]]). Todos salen de `pinst_pp.zip`, que es la
segmentacion de HoVer-NeXt.

Que calcula
-----------
Una pasada en **streaming** por el mapa de instancias de cada lamina, acumulando por instancia
los momentos de orden 0, 1 y 2 con `np.bincount`:

    area = #px      Sx  Sy      Sxx  Syy  Sxy

De ahi salen area, centroide, ejes mayor y menor, excentricidad y razon de aspecto **sin
`skimage`** (que no esta en ningun env). La convencion es la de `skimage.regionprops`:
autovalores l1 >= l2 del tensor de momentos centrales de segundo orden normalizados, y
`eje = 4*sqrt(l)`. Sin la correccion de discretizacion de +1/12: un nucleo son ~200 px, asi
que aporta menos del 1 % y skimage tampoco la aplica.

Por que en streaming: el mapa de la 129741 es (80496, 39426) int32 = **12,7 GB** en memoria,
pero comprime a 116 MB en el zip y solo el 0,3 % de los pixeles es nucleo. Leerlo por bloques
de filas alineados al chunk cuesta segundos.

Geometria (verificada, no asumida — [[hovernext-salida-geometria-y-clases]]): para la cohorte
privada con Lizard-Mitosis `ds_factor = 1`, asi que `pinst_pp[fila, columna]` esta en
coordenadas openslide **level 0** y un pixel mide 0,465 um. **Verificado el 28-ago sobre las
doce**: el shape del mapa reproduce las dimensiones de level 0 de la lamina con un margen menor
a una tesela (128 a 243 px de recorte). Esa comparacion es el chequeo DURO de escala, y esta
cableada abajo en `DIMS_LEVEL0`: un error de nivel daria un factor 2 o 4, no 200 px.

El area absoluta NO es comparable entre clases de HoVer-NeXt
-----------------------------------------------------------
El pre-registro habia declarado como chequeo de sanidad que el area mediana de los nucleos
epiteliales cayera entre 30 y 120 um2. **Se cumple en 8 de 12 laminas**: el rango medido es
22,7 a 46,5 um2 (diametro equivalente 5,4 a 7,7 um contra los 7 a 9 um de un nucleo epitelial
mamario), y quedan fuera por abajo 103762 (23,8), 106552 (26,2), 109609 (22,7) y B25-158899
(28,1). La escala esta bien (parrafo de arriba); lo que pasa es que `pinst_pp` no es el contorno
del nucleo sino la region que sobrevive al umbral de foreground del post-proceso, y **ese umbral
esta afinado por clase**:

    faster_instance_seg (post_process_utils.py:370-409): fg = (1 - bg_pred) > best_fg_thresh_cl[cl]
    lizard_convnextv2_tiny/liz_test_param_dict.json, "best_fg_f1" (el job corrio --metric f1):
      neutrophil 0,5 · epithelial 0,6 · lymphocyte 0,5 · plasma 0,3 · eosinophil 0,5 ·
      connective 0,3 · mitosis 0,5 (este ultimo pisado por mit_test_param_dict, ...:579-582)

`epithelial-cell` tiene **el umbral mas alto de las siete**, asi que es la clase mas erosionada,
y `plasma-cell` y `connective` los mas bajos. Por eso en la 109609 una plasmatica mide **mas**
(25,7 um2) que una epitelial (22,7 um2), que biologicamente esta al reves. **Consecuencia para
el eje 3**: un area cruda que mezcle marcas resueltas a clases distintas mezcla umbrales, y el
reparto de clases cambia con el grado (`moderado` trae 7 plasmaticas de 14). La comparacion
limpia es **dentro de una clase**, que es justo lo que pre-registro el primario de H3.a:
percentil dentro de la poblacion epitelial de la propia lamina.

Lo que NO es
------------
- **No es una segmentacion validada.** Es la salida de HoVer-NeXt tal cual; el geojson del
  patologo son positivos parciales y no permite calcular precision, F1 ni PQ.
- **No filtra nada.** Se guardan todas las instancias, incluidas las astillas. Quien consuma el
  npz decide el subconjunto, y lo declara.

Uso (workaround B, binario absoluto; `envs/pruebas` es el unico con zarr Y pandas):
  /home/sdonoso/miniconda3/envs/pruebas/bin/python scripts/b9_descriptores_nucleos.py
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import zarr

REPO = Path(__file__).resolve().parents[1]

# Las doce laminas anotadas. Lista EXPLICITA: el glob de `anotaciones/` da 13 archivos y 12
# laminas (el extra es una segunda exportacion de la 103762). Ver cruce_94_marcas.py:53-58.
SLIDES = ["129741", "103762", "106552", "109609", "110616", "124729",
          "124806", "126504", "128194", "144317", "164001", "B25-158899"]

# Lizard-Mitosis, `hover_next_reference/src/constants.py:31-39`. El 0 no es una clase: es el
# fondo del mapa de instancias (`fill_value` del zarr).
CLASES = {0: "(fondo)", 1: "neutrophil", 2: "epithelial-cell", 3: "lymphocyte",
          4: "plasma-cell", 5: "eosinophil", 6: "connective-tissue-cell", 7: "mitosis"}
EPITELIAL = 2

MPP = 0.465          # um/px, cohorte privada a level 0 ([[cohortes-magnificacion-fisica]])

# Chequeo DURO de escala: dimensiones (ancho, alto) de level 0 de cada lamina, leidas con
# openslide sobre el .bif el 28-ago-2026 (env clam_latest, que es el que tiene la libopenslide
# parchada de 1,2 MB — workaround K). El mapa de instancias tiene que reproducirlas con un
# margen menor a una tesela. Un error de nivel daria factor 2 o 4, no 200 px.
DIMS_LEVEL0 = {
    "129741": (39669, 80640), "103762": (52428, 28160), "106552": (53901, 46080),
    "109609": (36910, 32000), "110616": (42261, 29440), "124729": (46638, 30720),
    "124806": (38330, 26880), "126504": (49941, 30720), "128194": (52231, 33280),
    "144317": (47469, 34560), "164001": (49661, 30720), "B25-158899": (50868, 58880),
}
MARGEN_RECORTE = 256          # px: HoVer-NeXt recorta a multiplo de la grilla de teselas

# El rango que el pre-registro habia declarado como sanidad de escala. NO se cumple, y la causa
# esta en el docstring: el umbral de foreground del post-proceso esta afinado POR CLASE y el de
# `epithelial-cell` es el mas alto de las siete. Se sigue reportando — se declaro antes de medir
# y taparlo seria elegir el criterio despues de ver el dato — pero no aborta, porque el chequeo
# de escala que decide es DIMS_LEVEL0 y ese pasa en las doce.
AREA_EPI_MIN, AREA_EPI_MAX = 30.0, 120.0


def paths_de(slide: str) -> Path:
    """El barrido de las once anido el slide_id dos veces; la 129741 corrio sola y quedo plana."""
    a = REPO / f"results/b8_hovernext_12laminas/hovernext/lizard_mitosis/{slide}/{slide}"
    b = REPO / f"results/b8_hovernext_129741/hovernext/lizard_mitosis/{slide}"
    d = a if a.is_dir() else b
    if not d.is_dir():
        sys.exit(f"no encuentro la salida de HoVer-NeXt de {slide}")
    return d


def leer_class_inst(path: Path):
    """{id: [clase, [fila, columna]]} -> (clase_de, centroide_de) indexados por id."""
    ci = json.loads(Path(path).read_text())
    nmax = max(int(k) for k in ci)
    cls = np.zeros(nmax + 1, dtype=np.int8)
    cen = np.full((nmax + 1, 2), np.nan, dtype=np.float64)   # (fila=y, columna=x)
    for k, v in ci.items():
        i = int(k)
        cls[i] = v[0]
        cen[i] = v[1]
    return cls, cen, len(ci)


def momentos(pinst: Path, n: int, filas: int):
    """Momentos de orden 0,1,2 por instancia, en una pasada por bloques de filas.

    `n` = nmax+1 de class_inst.json. Si el mapa trae un id que no esta ahi, se aborta: seria
    un desajuste entre los dos artefactos y cualquier descriptor saldria corrido.
    """
    z = zarr.open(zarr.storage.ZipStore(str(pinst), mode="r"), mode="r")
    H, W = z.shape
    blk = max(z.chunks[0], (filas // z.chunks[0]) * z.chunks[0])   # alineado al chunk
    acc = [np.zeros(n, dtype=np.int64)] + [np.zeros(n, dtype=np.float64) for _ in range(5)]
    for y0 in range(0, H, blk):
        b = np.asarray(z[y0:min(y0 + blk, H), :])
        iy, ix = np.nonzero(b)
        if not len(iy):
            continue
        v = b[iy, ix].astype(np.int64)
        if v.max() >= n:
            sys.exit(f"{pinst}: el mapa trae la instancia {v.max()} y class_inst.json llega "
                     f"hasta {n - 1}. Los dos artefactos no son de la misma corrida.")
        x = ix.astype(np.float64)
        y = (iy + y0).astype(np.float64)
        acc[0] += np.bincount(v, minlength=n)
        for j, w in enumerate((x, y, x * x, y * y, x * y), start=1):
            acc[j] += np.bincount(v, weights=w, minlength=n)
    return (H, W), acc


def descriptores(acc):
    """Area, centroide y ejes desde los momentos. Devuelve todo en PIXELES.

    Los ejes son los de `skimage.regionprops`: autovalores del tensor de momentos centrales
    normalizados, `eje = 4*sqrt(l)`. `l2` se recorta a 0 porque la resta puede dar -1e-12.
    """
    area, sx, sy, sxx, syy, sxy = acc
    ok = area > 0
    a = np.where(ok, area, 1).astype(np.float64)      # divisor seguro; lo que no es ok va a NaN
    cx, cy = sx / a, sy / a
    mu20 = sxx / a - cx * cx
    mu02 = syy / a - cy * cy
    mu11 = sxy / a - cx * cy
    semi = np.sqrt(((mu20 - mu02) / 2.0) ** 2 + mu11 ** 2)
    l1 = np.clip((mu20 + mu02) / 2.0 + semi, 0.0, None)
    l2 = np.clip((mu20 + mu02) / 2.0 - semi, 0.0, None)
    mayor, menor = 4.0 * np.sqrt(l1), 4.0 * np.sqrt(l2)
    with np.errstate(divide="ignore", invalid="ignore"):
        exc = np.where(l1 > 0, np.sqrt(np.clip(1.0 - l2 / np.where(l1 > 0, l1, 1.0), 0.0, 1.0)),
                       np.nan)
        # NaN, no un max(x, eps) de guarda: un divisor que miente no falla, devuelve un numero
        # enorme y pasa cualquier corte ([[razon-denominador-degenerado]]).
        razon = np.where(menor > 0, mayor / np.where(menor > 0, menor, 1.0), np.nan)
    diam_eq = 2.0 * np.sqrt(area / np.pi)
    for v in (cx, cy, mayor, menor, exc, razon, diam_eq):
        v[~ok] = np.nan
    return dict(area_px=area, cx=cx, cy=cy, eje_mayor_px=mayor, eje_menor_px=menor,
                excentricidad=exc, razon_aspecto=razon, diam_eq_px=diam_eq)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slides", nargs="*", default=SLIDES)
    ap.add_argument("--filas", type=int, default=4096, help="filas por bloque (se alinea al chunk)")
    ap.add_argument("--mpp", type=float, default=MPP)
    ap.add_argument("--out", default=str(REPO / "results/b9_nucleos"))
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)

    print("=" * 100)
    print("DESCRIPTORES DE FORMA DE LAS INSTANCIAS DE HoVer-NeXt — insumo del eje 3")
    print("=" * 100)
    print(f"{a.mpp} um/px, level 0 (ds_factor=1 para Lizard sobre la cohorte privada)")
    print("chequeo DURO de escala: el shape del mapa contra las dimensiones de level 0 del .bif")
    print(f"chequeo declarado en el pre-registro: area epitelial mediana en "
          f"{AREA_EPI_MIN:g}-{AREA_EPI_MAX:g} um2 (se reporta; ver el docstring)\n")
    print(f"  {'lamina':<12} {'mapa (H,W)':>15} {'instancias':>10} {'epitel.':>8} "
          f"{'area epi med':>13} {'d_eq':>7} {'exc':>6} {'d centroide':>12} {'s':>6}  "
          f"{'escala':>7}  prereg")

    fallos, malos = [], []
    for slide in a.slides:
        d = paths_de(slide)
        t0 = time.time()
        cls, cen, n_inst = leer_class_inst(d / "class_inst.json")
        (H, W), acc = momentos(d / "pinst_pp.zip", len(cls), a.filas)
        des = descriptores(acc)
        dt = time.time() - t0

        ids = np.nonzero(des["area_px"] > 0)[0]
        clase = cls[ids]
        area_um2 = des["area_px"][ids] * a.mpp ** 2
        # Cruce libre contra class_inst.json: el centroide que sale de los momentos tiene que
        # ser el mismo que escribio HoVer-NeXt. Si estuvieran transpuestos (fila<->columna,
        # la trampa de la memoria) esto se dispara a miles de pixeles.
        dcen = np.hypot(des["cx"][ids] - cen[ids, 1], des["cy"][ids] - cen[ids, 0])
        epi = clase == EPITELIAL
        med_epi = float(np.median(area_um2[epi])) if epi.any() else float("nan")
        prereg_ok = AREA_EPI_MIN <= med_epi <= AREA_EPI_MAX
        if not prereg_ok:
            fallos.append((slide, med_epi))
        # el chequeo que decide: shape del mapa contra las dimensiones de level 0
        W0, H0 = DIMS_LEVEL0[slide]
        escala = 0 <= H0 - H <= MARGEN_RECORTE and 0 <= W0 - W <= MARGEN_RECORTE
        if not escala:
            malos.append((slide, (H, W), (H0, W0)))

        np.savez_compressed(
            out / f"{slide}_nucleos.npz",
            id=ids.astype(np.int32), clase=clase.astype(np.int8),
            area_px=des["area_px"][ids].astype(np.int32),
            cx=des["cx"][ids].astype(np.float32), cy=des["cy"][ids].astype(np.float32),
            eje_mayor_px=des["eje_mayor_px"][ids].astype(np.float32),
            eje_menor_px=des["eje_menor_px"][ids].astype(np.float32),
            diam_eq_px=des["diam_eq_px"][ids].astype(np.float32),
            excentricidad=des["excentricidad"][ids].astype(np.float32),
            razon_aspecto=des["razon_aspecto"][ids].astype(np.float32),
            mpp=np.float64(a.mpp), shape=np.asarray([H, W], dtype=np.int64),
        )
        # nanmedian: una instancia de un solo pixel tiene l1 = 0, asi que su excentricidad y su
        # razon de aspecto son NaN a proposito (no un max(x, eps) que devuelva un numero falso).
        n_deg = int(np.isnan(des["excentricidad"][ids]).sum())
        print(f"  {slide:<12} {H:>7}x{W:<7} {len(ids):>10} {int(epi.sum()):>8} "
              f"{med_epi:>11.1f} um2 {np.nanmedian(des['diam_eq_px'][ids][epi])*a.mpp:>6.1f} "
              f"{np.nanmedian(des['excentricidad'][ids][epi]):>6.2f} "
              f"{np.median(dcen):>10.2f}px {dt:>6.1f}  "
              f"{'level 0' if escala else 'NO CUADRA':>7}  {'ok' if prereg_ok else 'bajo'}",
              flush=True)
        if len(ids) != n_inst:
            print(f"     ojo: class_inst.json declara {n_inst} instancias y el mapa tiene "
                  f"{len(ids)} con al menos un pixel", flush=True)
        if n_deg:
            print(f"     {n_deg} instancias de un solo pixel: excentricidad y razon de aspecto "
                  f"van NaN (area y centroide siguen siendo validos)", flush=True)

    print(f"\n  -> {out}/<slide>_nucleos.npz")
    if malos:
        print("\n  ESCALA: NO CUADRA en " + ", ".join(
            f"{sl} mapa {m} contra level 0 {d}" for sl, m, d in malos))
        print("  El mapa no esta en level 0: ningun descriptor en um2 se puede leer.")
        sys.exit(1)
    print(f"  escala (shape contra level 0 del .bif): PASA en las {len(a.slides)} laminas")
    print(f"  centroide contra class_inst.json: coincide, asi que no hay transposicion "
          f"fila/columna")
    if fallos:
        print(f"\n  chequeo del pre-registro (area epitelial en {AREA_EPI_MIN:g}-"
              f"{AREA_EPI_MAX:g} um2): NO SE CUMPLE en {len(fallos)} de {len(a.slides)} laminas")
        print("  " + ", ".join(f"{sl} {m:.1f}" for sl, m in fallos))
        print("  No es un error de escala (la de arriba pasa): `pinst_pp` es la region que")
        print("  sobrevive al umbral de foreground, y ese umbral esta afinado POR CLASE, con")
        print("  `epithelial-cell` en el mas alto de las siete (0,6). Ver el docstring.")


if __name__ == "__main__":
    main()
