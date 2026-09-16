#!/usr/bin/env python
"""b10_deck_seleccion.py — elige los recortes de las láminas de imagen del deck del 15-sep.

Plan: `sprints/B10_sprint10/presentacion_b10/plan_deck_visual.md`, paso 1.a. NO MIDE NADA: vuelve
a correr el orden por tamaño de O1 sobre los mismos artefactos, verifica que reproduce lo
publicado y, recién entonces, elige qué dibujar. El render va aparte, en
`scripts/b10_deck_imagenes.py`, porque este env (`pruebas`) tiene zarr y no abre los `.bif`, y
`clam_latest` abre los `.bif` y no tiene zarr (workaround K.a).

Reglas de selección, deterministas. Ninguna se elige a ojo, y si una regla elige un ejemplo poco
lucido se declara, no se cambia la regla.

  Orden y estado de cada marca. El de O1 sin tocar: percentil de área dentro de los núcleos
  epiteliales vivos de la lámina (`argsort` estable), orden descendente estable, marca resuelta
  con `resolver_por_centroide` a `TOL_VECINDAD_UM`. Estado en N = 500: `recuperada` si el puesto
  de su núcleo es <= 500, `no_recuperada` si resolvió a un núcleo epitelial de puesto mayor, y
  `no_alcanzable` si no resolvió.

  s03 · qué detecta HoVer-NeXt. Entre las marcas de alto grado de láminas con `alineada: true`,
  la que tiene más núcleos epiteliales en su parche de 256 px, con el parche de la grilla de
  `carga_mm2` (`floor(x / 256)`, `floor(y / 256)`). Empate: orden de `SLIDES + SLIDES_B10` y
  orden de la marca en el geojson. Dos ventanas centradas en la marca: `LADO_CONTEXTO` px
  (500 µm) y 256 px (un parche de CLAM, 119 µm); se guarda sólo la grande, porque la chica es
  su centro.

  s05 · O1 sobre una lámina. La lámina de alto grado con más marcas alcanzables y la de bajo
  grado con más marcas alcanzables, las dos alineadas; empate por el mismo orden. Por lámina,
  los parches de la unión de N = 500 (la misma grilla), cada marca con su estado y la carga.

  s06 · O1 núcleo a núcleo. Por grado, entre las marcas alcanzables de láminas alineadas,
  ordenadas por puesto (empate: lámina y marca): las recuperadas en los puestos mínimo, mediano
  y máximo, y las no recuperadas en el primer cuartil y la mediana. Índices sobre la lista
  ordenada de largo n: mínimo 0, primer cuartil (n-1)//4, mediana (n-1)//2, máximo n-1. Una
  lámina distinta por panel cuando alcance: se toman los paneles en ese orden (mínimo, mediano,
  máximo, primer cuartil, mediano) y cada uno se queda con el candidato más cercano a su índice
  cuya lámina no esté ya en la fila; a igual distancia, el de índice menor; si todas las
  láminas ya están, se repite. Bajo no tiene recuperadas: su fila son sólo las no recuperadas.
  Ventana de `LADO_GALERIA` px centrada en el centroide del núcleo.

Gates que abortan antes de escribir:
  1. Por lámina, `escalera()` de O1 con este orden reproduce `escalera.csv` en N = 500 (recall,
     `n_resueltas`, `n_candidatos` y carga), y los estados por marca suman lo mismo. Sumado sobre
     las 21: recuperadas 41 · 12 · 0 y alcanzables 76 · 53 · 16 (alto · moderado · bajo).
  2. En cada ventana, `pinst_pp[fila, columna]` en el centroide de `class_inst.json` de cada
     núcleo dibujado devuelve su id, y su clase coincide con la del npz
     ([[hovernext-salida-geometria-y-clases]]).

Escribe en `results/b10_deck_imagenes/`: `seleccion.json` y una `ventana_<nombre>.npz` por
recorte, con el trozo de `pinst_pp` y los ids con su clase (y su puesto, en la galería).

  /home/sdonoso/miniconda3/envs/pruebas/bin/python scripts/b10_deck_seleccion.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import zarr

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from b9_descriptores_nucleos import (CLASES, EPITELIAL, MPP, SLIDES,   # noqa: E402
                                     SLIDES_B10, leer_class_inst, paths_de)
from b9_pleomorfismo import TOL_VECINDAD_UM, marcas_de_grado               # noqa: E402
from b10_grado_sin_marca import (AREA_PARCHE_MM2, LADO_PARCHE_PX,          # noqa: E402
                                 cargar_offset, carga_mm2, escalera,
                                 resolver_por_centroide)

OUT = REPO / "results" / "b10_deck_imagenes"
ESCALERA_CSV = REPO / "results" / "b10_grado_sin_marca" / "escalera.csv"
N_CARGA = 500
GRADOS = ["alto", "moderado", "bajo"]
PUB_RECUPERADAS = {"alto": 41, "moderado": 12, "bajo": 0}
PUB_ALCANZABLES = {"alto": 76, "moderado": 53, "bajo": 16}

LADO_CONTEXTO = 1076          # px de level 0 = 500,3 µm
LADO_GALERIA = 160            # px = 74,4 µm: el núcleo y sus vecinos del top 500
PANELES_GALERIA = [("recuperada", "mínimo"), ("recuperada", "mediano"),
                   ("recuperada", "máximo"), ("no_recuperada", "primer cuartil"),
                   ("no_recuperada", "mediano")]


# --------------------------------------------------------------------------------------
# el orden de O1, por lámina

def lamina(slide):
    """Arrays del npz, el orden por tamaño y el estado de cada marca en N = 500."""
    z = dict(np.load(REPO / "results" / "b9_nucleos" / f"{slide}_nucleos.npz"))
    cls, area_px = z["clase"], z["area_px"].astype(float)
    cx, cy = z["cx"].astype(float), z["cy"].astype(float)
    mpp = float(z["mpp"])
    area_um2 = area_px * mpp * mpp
    epi = (cls == EPITELIAL) & (area_px > 0)

    # Las mismas líneas que `b10_grado_sin_marca.main()`: el percentil sale de un `argsort`
    # estable sobre el área de los epiteliales vivos. El gate 1 compara el resultado entero.
    pct = np.full(len(cls), np.nan)
    ae = area_um2[epi]
    o = np.argsort(ae, kind="stable")
    r = np.empty(len(ae)); r[o] = np.arange(len(ae))
    pct[np.nonzero(epi)[0]] = 100.0 * r / max(len(ae) - 1, 1)

    idx = np.nonzero(epi)[0]
    orden = idx[np.argsort(-pct[idx], kind="stable")]           # el de `escalera()`
    puesto = np.zeros(len(cls), dtype=np.int64)
    puesto[orden] = np.arange(1, len(orden) + 1)

    dx, dy, alineada = cargar_offset(slide)
    tol_px = TOL_VECINDAD_UM / MPP
    marcas = []
    for k, (grado, _ord, p) in enumerate(marcas_de_grado(slide, dx, dy)):
        i = resolver_por_centroide(cx, cy, epi, p[0], p[1], tol_px)
        if i < 0:
            estado, pu = "no_alcanzable", None
        else:
            pu = int(puesto[i])
            estado = "recuperada" if pu <= N_CARGA else "no_recuperada"
        marcas.append(dict(slide=slide, marca=k, grado=grado, x=float(p[0]), y=float(p[1]),
                           alineada=alineada, estado=estado, inst_pos=int(i),
                           inst_id=int(z["id"][i]) if i >= 0 else None, puesto=pu,
                           percentil=float(pct[i]) if i >= 0 else None,
                           area_um2=float(area_um2[i]) if i >= 0 else None))
    return dict(slide=slide, z=z, cls=cls, cx=cx, cy=cy, epi=epi, pct=pct, orden=orden,
                puesto=puesto, marcas=marcas, alineada=alineada, tol_px=tol_px,
                shape=tuple(int(v) for v in z["shape"]))


def gate_escalera(L, ref):
    """Gate 1, por lámina: `escalera()` de O1 con este orden contra la fila publicada."""
    mxy = np.asarray([[m["x"], m["y"]] for m in L["marcas"]], float)
    filas, n_res, n_cand = escalera(L["cx"], L["cy"], L["pct"], L["epi"], mxy, L["tol_px"],
                                    [N_CARGA])
    f = ref[ref.slide == L["slide"]]
    if len(f) != 1:
        sys.exit(f"gate 1: {L['slide']} tiene {len(f)} filas en escalera.csv para N = 500")
    f = f.iloc[0]
    rec = sum(m["estado"] == "recuperada" for m in L["marcas"])
    alc = sum(m["estado"] != "no_alcanzable" for m in L["marcas"])
    carga = carga_mm2(L["cx"], L["cy"], L["orden"], N_CARGA)
    malos = []
    for nombre, mio, pub in (("recall de escalera()", filas[0]["recall"], f.recall),
                             ("recuperadas por marca", rec, f.recall),
                             ("n_resueltas", n_res, f.n_resueltas),
                             ("alcanzables por marca", alc, f.n_resueltas),
                             ("n_candidatos", n_cand, f.n_candidatos),
                             ("n_marcas", len(L["marcas"]), f.n_marcas)):
        if int(mio) != int(pub):
            malos.append(f"{nombre} {mio} contra {pub}")
    if abs(carga - f.carga_mm2) > 1e-9 or abs(filas[0]["carga_mm2"] - f.carga_mm2) > 1e-9:
        malos.append(f"carga {carga} contra {f.carga_mm2}")
    if bool(f.alineada) != L["alineada"]:
        malos.append(f"alineada {L['alineada']} contra {f.alineada}")
    if malos:
        sys.exit(f"gate 1: {L['slide']} no reproduce escalera.csv: " + "; ".join(malos))
    return f.grados, carga


# --------------------------------------------------------------------------------------
# ventanas

def origen(c, lado, limite):
    """Origen de una ventana centrada en `c`, clampado para que entre en el mapa."""
    return int(max(0, min(int(round(c - lado / 2.0)), limite - lado)))


def leer_ventana(slide, x0, y0, lado):
    d = paths_de(slide)
    zz = zarr.open(zarr.storage.ZipStore(str(d / "pinst_pp.zip"), mode="r"), mode="r")
    return np.asarray(zz[y0:y0 + lado, x0:x0 + lado])


def gate_ids(nombre, win, x0, y0, ids, cls_de, cen_de, clase_npz):
    """Gate 2: el pixel del centroide devuelve el id, y la clase coincide con la del npz."""
    lado_y, lado_x = win.shape
    malos, n = [], 0
    for i in ids:
        fila, col = cen_de[i]
        u, v = int(round(col)) - x0, int(round(fila)) - y0
        if not (0 <= u < lado_x and 0 <= v < lado_y):
            continue                                   # centroide fuera: no se chequea
        n += 1
        if int(win[v, u]) != int(i):
            malos.append(f"id {i}: el pixel del centroide da {int(win[v, u])}")
        if int(cls_de[i]) != int(clase_npz[i]):
            malos.append(f"id {i}: clase {cls_de[i]} en class_inst.json, {clase_npz[i]} en npz")
    if malos:
        sys.exit(f"gate 2 ({nombre}): {len(malos)} de {n} núcleos no cuadran: "
                 + "; ".join(malos[:6]))
    return n


# --------------------------------------------------------------------------------------
# reglas

def elegir_s03(laminas):
    mejor = None
    for L in laminas:
        if not L["alineada"]:
            continue
        ex = L["cx"][L["epi"]]; ey = L["cy"][L["epi"]]
        celda = (ex // LADO_PARCHE_PX).astype(np.int64) * (1 << 32) + \
            (ey // LADO_PARCHE_PX).astype(np.int64)
        u, c = np.unique(celda, return_counts=True)
        cuenta = dict(zip(u.tolist(), c.tolist()))
        for m in L["marcas"]:
            if m["grado"] != "alto":
                continue
            k = int(m["x"] // LADO_PARCHE_PX) * (1 << 32) + int(m["y"] // LADO_PARCHE_PX)
            n = int(cuenta.get(k, 0))
            if mejor is None or n > mejor[0]:           # estricto: el empate queda con el primero
                mejor = (n, L, m)
    return mejor


def elegir_s05(laminas, grado):
    mejor = None
    for L in laminas:
        if not L["alineada"] or not any(m["grado"] == grado for m in L["marcas"]):
            continue
        alc = sum(m["estado"] != "no_alcanzable" for m in L["marcas"])
        if mejor is None or alc > mejor[0]:
            mejor = (alc, L)
    return mejor


def elegir_s06(laminas, grado):
    cand = [m for L in laminas if L["alineada"] for m in L["marcas"]
            if m["grado"] == grado and m["estado"] != "no_alcanzable"]
    orden_slide = {s: i for i, s in enumerate(SLIDES + SLIDES_B10)}
    listas = {e: sorted([m for m in cand if m["estado"] == e],
                        key=lambda m: (m["puesto"], orden_slide[m["slide"]], m["marca"]))
              for e in ("recuperada", "no_recuperada")}
    usadas, paneles = set(), []
    for estado, cual in PANELES_GALERIA:
        lst = listas[estado]
        if not lst:
            continue
        n = len(lst)
        objetivo = {"mínimo": 0, "primer cuartil": (n - 1) // 4, "mediano": (n - 1) // 2,
                    "máximo": n - 1}[cual]
        libres = [j for j in range(n) if lst[j]["slide"] not in usadas] or list(range(n))
        j = min(libres, key=lambda j: (abs(j - objetivo), j))
        usadas.add(lst[j]["slide"])
        paneles.append(dict(lst[j], columna=f"{estado}:{cual}", indice_objetivo=objetivo,
                            indice_elegido=j, n_candidatos=n))
    return paneles


# --------------------------------------------------------------------------------------

def main():
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    ref = pd.read_csv(ESCALERA_CSV, dtype={"slide": str})
    ref = ref[(ref.brazo == "A_lamina_entera") & (ref.desc == "percentil") & (ref.N == N_CARGA)]

    print("=" * 100)
    print("Selección de recortes para el deck del 15-sep · el orden de O1, re-corrido y verificado")
    print("=" * 100)
    laminas, tot_rec, tot_alc = [], dict.fromkeys(GRADOS, 0), dict.fromkeys(GRADOS, 0)
    for slide in SLIDES + SLIDES_B10:
        L = lamina(slide)
        grados, carga = gate_escalera(L, ref)
        rec = sum(m["estado"] == "recuperada" for m in L["marcas"])
        alc = sum(m["estado"] != "no_alcanzable" for m in L["marcas"])
        tot_rec[grados] += rec
        tot_alc[grados] += alc
        L["grado"], L["carga_mm2"] = grados, carga
        laminas.append(L)
        print(f"  {slide:<11} {grados:<9} {'alineada' if L['alineada'] else 'SIN VERIFICAR':<13} "
              f"marcas {len(L['marcas']):>3}  alcanzables {alc:>3}  recuperadas {rec:>3}  "
              f"carga {carga:5.2f} mm²")
    for g in GRADOS:
        if tot_rec[g] != PUB_RECUPERADAS[g] or tot_alc[g] != PUB_ALCANZABLES[g]:
            sys.exit(f"gate 1: {g} da {tot_rec[g]} de {tot_alc[g]}, publicado "
                     f"{PUB_RECUPERADAS[g]} de {PUB_ALCANZABLES[g]}")
    print("  gate 1 OK: recuperadas " + " · ".join(str(tot_rec[g]) for g in GRADOS)
          + ", alcanzables " + " · ".join(str(tot_alc[g]) for g in GRADOS)
          + " (alto · moderado · bajo), y cada lámina reproduce su fila de escalera.csv")

    sel = dict(plan="sprints/B10_sprint10/presentacion_b10/plan_deck_visual.md",
               mpp=MPP, n_carga=N_CARGA, lado_parche_px=LADO_PARCHE_PX,
               area_parche_mm2=AREA_PARCHE_MM2, tol_vecindad_um=TOL_VECINDAD_UM,
               clases=CLASES)
    ventanas = []

    # --- s03
    n03, L, m = elegir_s03(laminas)
    H, W = L["shape"]
    x0, y0 = origen(m["x"], LADO_CONTEXTO, W), origen(m["y"], LADO_CONTEXTO, H)
    sel["s03"] = dict(regla="marca de alto grado, lámina alineada, con más núcleos epiteliales "
                            "en su parche de 256 px", slide=L["slide"], marca=m,
                      n_epi_parche=n03, ventana="ventana_s03.npz", x0=x0, y0=y0,
                      lado_px=LADO_CONTEXTO, lado_centro_px=LADO_PARCHE_PX)
    ventanas.append(("s03", L, x0, y0, LADO_CONTEXTO, None))
    print(f"\n  s03: {L['slide']} marca {m['marca']} en ({m['x']:.0f}, {m['y']:.0f}), "
          f"{n03} núcleos epiteliales en su parche, estado {m['estado']}")

    # --- s05
    sel["s05"] = []
    for g in ("alto", "bajo"):
        alc, L = elegir_s05(laminas, g)
        celdas = np.unique(np.stack([(L["cx"][L["orden"][:N_CARGA]] // LADO_PARCHE_PX),
                                     (L["cy"][L["orden"][:N_CARGA]] // LADO_PARCHE_PX)],
                                    axis=1).astype(np.int64), axis=0)
        if abs(len(celdas) * AREA_PARCHE_MM2 - L["carga_mm2"]) > 1e-9:
            sys.exit(f"s05: {L['slide']} da {len(celdas)} parches y la carga es "
                     f"{L['carga_mm2']}")
        cuenta = {e: sum(mm["estado"] == e for mm in L["marcas"])
                  for e in ("recuperada", "no_recuperada", "no_alcanzable")}
        sel["s05"].append(dict(grado=g, regla=f"lámina de {g} grado, alineada, con más marcas "
                                               "alcanzables", slide=L["slide"],
                               alcanzables=alc, carga_mm2=L["carga_mm2"],
                               n_parches=len(celdas), parches=celdas.tolist(),
                               marcas=L["marcas"], cuenta=cuenta,
                               shape_pinst=list(L["shape"])))
        print(f"  s05: {g:<5} {L['slide']}  {alc} alcanzables · {cuenta}  "
              f"{len(celdas)} parches = {L['carga_mm2']:.2f} mm²")

    # --- s06
    sel["s06"] = []
    for g in GRADOS:
        for p in elegir_s06(laminas, g):
            L = next(x for x in laminas if x["slide"] == p["slide"])
            H, W = L["shape"]
            i = p["inst_pos"]
            x0 = origen(L["cx"][i], LADO_GALERIA, W)
            y0 = origen(L["cy"][i], LADO_GALERIA, H)
            nombre = f"s06_{g}_{len([q for q in sel['s06'] if q['grado'] == g])}"
            p.update(grado=g, ventana=f"ventana_{nombre}.npz", x0=x0, y0=y0,
                     lado_px=LADO_GALERIA)
            sel["s06"].append(p)
            ventanas.append((nombre, L, x0, y0, LADO_GALERIA, p))
            print(f"  s06: {g:<8} {p['columna']:<30} {p['slide']:<9} puesto {p['puesto']:>6} "
                  f"p{p['percentil']:5.1f}  {p['area_um2']:5.1f} µm²  "
                  f"(índice {p['indice_elegido']} de {p['n_candidatos']}, objetivo "
                  f"{p['indice_objetivo']})")

    # --- ventanas + gate 2
    cache = {}
    for nombre, L, x0, y0, lado, panel in ventanas:
        s = L["slide"]
        if s not in cache:
            cache[s] = leer_class_inst(paths_de(s) / "class_inst.json")
        cls_de, cen_de, _ = cache[s]
        win = leer_ventana(s, x0, y0, lado)
        presentes = np.unique(win); presentes = presentes[presentes > 0]
        clase_npz = dict(zip(L["z"]["id"].tolist(), L["cls"].tolist()))
        if panel is None:
            dibujados = presentes
        else:
            # la galería dibuja el núcleo marcado y los del top 500 que caen en la ventana
            top = set(L["z"]["id"][L["orden"][:N_CARGA]].tolist())
            dibujados = np.array(sorted({int(i) for i in presentes if int(i) in top}
                                        | {panel["inst_id"]}), dtype=np.int64)
            if panel["inst_id"] not in set(presentes.tolist()):
                sys.exit(f"{nombre}: el núcleo marcado no está en su ventana")
        n = gate_ids(nombre, win, x0, y0, dibujados, cls_de, cen_de, clase_npz)
        puestos = L["puesto"][[int(np.searchsorted(L["z"]["id"], i)) for i in dibujados]]
        np.savez_compressed(OUT / f"ventana_{nombre}.npz", pinst=win.astype(np.int32),
                            x0=x0, y0=y0, ids=dibujados.astype(np.int64),
                            clases=np.array([cls_de[i] for i in dibujados], np.int8),
                            puestos=puestos.astype(np.int64))
        print(f"  ventana {nombre:<14} {s:<9} {lado}×{lado} px en ({x0}, {y0}): "
              f"{len(dibujados)} núcleos dibujados, gate 2 sobre {n}")
    print("  gate 2 OK: el pixel del centroide devuelve el id y la clase coincide")

    sel["gates"] = dict(recuperadas=tot_rec, alcanzables=tot_alc)
    (OUT / "seleccion.json").write_text(json.dumps(sel, indent=1, ensure_ascii=False))
    print(f"\nescrito: {OUT}/seleccion.json y {len(ventanas)} ventanas  ({time.time()-t0:.0f} s)")


if __name__ == "__main__":
    main()
