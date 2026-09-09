#!/usr/bin/env python
"""O1 del B10 — ¿HoVer-NeXt SOLO reencuentra los nucleos que marco el patologo?

Pre-registro: `sprints/B10_sprint10/grado_sin_marca/prereg.md`, escrito y commiteado ANTES
que este archivo (regla 9). Lo que sigue implementa ese documento y no lo amplia.

La diferencia con el eje 3 del B9 es una sola: alla la marca decia QUE nucleo mirar, aca el
nucleo lo tiene que elegir el descriptor. La marca queda solo como verdad de campo para
contar el recall.

NO REIMPLEMENTA NADA del B9: importa la lectura de `pinst_pp`, la resolucion marca ->
instancia, la rasterizacion de poligonos y los estadisticos. El B9 dejo ese patron y este
driver lo sigue.

CPU puro, sin GPU. Workaround B (binario absoluto) y `envs/pruebas`, que es el unico env con
zarr Y pandas:
  /home/sdonoso/miniconda3/envs/pruebas/bin/python scripts/b10_grado_sin_marca.py
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
sys.path.insert(0, str(REPO / "scripts"))

from b9_descriptores_nucleos import (CLASES, EPITELIAL, MPP, SLIDES,   # noqa: E402
                                     SLIDES_B10, geojson_de, paths_de)
from b9_epitelio_estroma import mascara_region                             # noqa: E402
from b9_pleomorfismo import (GRADOS, OFFSETS, ORDEN, TOL_VECINDAD_UM,      # noqa: E402
                             marcas_de_grado, permutacion_exacta, rank_auc,
                             resolver, spearman)

# La mascara del brazo B. D2 de Ernesto: el pleomorfismo invasivo se mide dentro del tumor, y
# esa region ya existe (162 poligonos en 21 laminas). NO se usan las clases de CDIS: el cruce
# del 8-sep mostro que las marcas de grado siguen la etiqueta de pleomorfismo de la lamina y
# no el grado nuclear del CDIS ([[marcas-grado-son-pleomorfismo-de-lamina]]).
CLASE_MASCARA = "Tumor"

# Las regiones que descalifican a un nucleo como "epitelio normal" para el proxy del CAP. Es
# TODO lo anotado como tejido lesional, no solo `Tumor`: un nucleo dentro de un CDIS no es
# normal aunque este fuera del tumor invasor.
REGIONES_LESIONALES = {"Tumor", "AreaSolida", "AreaTubular",
                       "CDIS_solido", "CDIS_papilar", "DCIS",
                       "CDIS_cribiforme", "CDIS_micropapilar"}

LADO_PARCHE_PX = 256                       # el lado del parche de CLAM
AREA_PARCHE_MM2 = (LADO_PARCHE_PX * MPP / 1000.0) ** 2      # 0,0142 mm2

# La escalera declarada en el prereg §2. El ultimo peldano lo agrega cada lamina: el N que
# agota su mascara, que es el chequeo de sanidad (ahi el recall tiene que dar el gate).
ESCALERA = [10, 20, 50, 100, 200, 500, 1000, 2000, 5000]

CELL = 8                 # px por celda de la rasterizacion, igual que b9_epitelio_estroma
N_NULO = 200             # piso del p = 1/201 = 0,00498
SEMILLA = 20260909


# --------------------------------------------------------------------------------------
# carga

def cargar_offset(slide):
    d = json.loads((OFFSETS / f"offset_{slide}.json").read_text())
    return float(d["dx"]), float(d["dy"]), bool(d.get("alineada", False))


def cargar_poligonos(slide, dx, dy, clases):
    """[(clase, poly Nx2 en coords openslide level 0)] de las clases pedidas."""
    js = json.loads(geojson_de(slide).read_text())
    out = []
    for ft in js.get("features", []):
        cl = ft.get("properties", {}).get("classification", {})
        nombre = cl.get("name") if isinstance(cl, dict) else str(cl)
        if nombre not in clases:
            continue
        g = ft["geometry"]
        anillos = g["coordinates"] if g["type"] == "Polygon" else g["coordinates"][0]
        out.append((nombre, np.asarray(anillos[0], float) + np.array([dx, dy], float)))
    return out


def mascara_union(polys, ny, nx):
    """Union de poligonos rasterizada a resolucion de celda, como matriz (ny, nx) bool."""
    m = np.zeros((ny, nx), dtype=bool)
    for _, p in polys:
        sub, x0, y0 = mascara_region(p, CELL)
        h, w = sub.shape
        y1, x1 = min(y0 + h, ny), min(x0 + w, nx)
        if y0 >= ny or x0 >= nx or y1 <= 0 or x1 <= 0:
            continue
        ay0, ax0 = max(y0, 0), max(x0, 0)
        m[ay0:y1, ax0:x1] |= sub[ay0 - y0:y1 - y0, ax0 - x0:x1 - x0]
    return m


def dentro(mask, xs, ys):
    """Membresia de puntos (px de level 0) en una mascara a resolucion de celda."""
    ny, nx = mask.shape
    ix = np.clip((xs / CELL).astype(np.int64), 0, nx - 1)
    iy = np.clip((ys / CELL).astype(np.int64), 0, ny - 1)
    return mask[iy, ix]


# --------------------------------------------------------------------------------------
# el nucleo del metodo

def rango_de(valores, sel):
    """Rango (1 = el mas grande) de cada nucleo dentro del subconjunto `sel`, por descriptor.

    Devuelve un vector del largo de `valores` con el rango, y NaN para lo que no esta en `sel`.
    """
    r = np.full(len(valores), np.nan)
    idx = np.nonzero(sel)[0]
    if not len(idx):
        return r
    orden = idx[np.argsort(-valores[idx], kind="stable")]
    r[orden] = np.arange(1, len(orden) + 1)
    return r


def carga_mm2(cx, cy, sel_ordenada, n):
    """mm2 de la UNION de parches de 256 px que contienen a los `n` primeros candidatos.

    Union y no `n * AREA_PARCHE_MM2`: dos candidatos pueden caer en el mismo parche, asi que la
    suma seria una cota y no la carga (prereg §2).
    """
    if n <= 0:
        return 0.0
    idx = sel_ordenada[:n]
    px = (cx[idx] / LADO_PARCHE_PX).astype(np.int64)
    py = (cy[idx] / LADO_PARCHE_PX).astype(np.int64)
    return float(len(np.unique(px.astype(np.int64) * (1 << 32) + py))) * AREA_PARCHE_MM2


def resolver_por_centroide(cx, cy, sel, mx, my, tol_px):
    """Nucleo mas cercano a la marca, entre los de `sel` y dentro de `tol_px`. -1 si ninguno.

    Es la regla que usan el brazo observado Y el nulo, para que sean comparables. La regla con
    zarr de `resolver()` se corre aparte, sobre las marcas observadas, como gate y regresion
    contra el B9 (prereg §6): si las dos coinciden, la eleccion no sostiene ninguna conclusion.
    """
    idx = np.nonzero(sel)[0]
    if not len(idx):
        return -1
    d = np.hypot(cx[idx] - mx, cy[idx] - my)
    j = int(np.argmin(d))
    return int(idx[j]) if d[j] <= tol_px else -1


def escalera(cx, cy, valores, sel, marcas_xy, tol_px, peldanos):
    """Recall y carga por peldano. `marcas_xy` son (x, y) en coords de level 0."""
    idx = np.nonzero(sel)[0]
    if not len(idx):
        return [], 0, 0
    orden = idx[np.argsort(-valores[idx], kind="stable")]
    pos = {int(i): k + 1 for k, i in enumerate(orden)}       # instancia -> rango
    rangos = []
    for mx, my in marcas_xy:
        i = resolver_por_centroide(cx, cy, sel, mx, my, tol_px)
        rangos.append(pos.get(i, np.inf) if i >= 0 else np.inf)
    rangos = np.asarray(rangos, float)
    n_res = int(np.isfinite(rangos).sum())
    filas = []
    for n in peldanos:
        n = min(n, len(orden))
        filas.append(dict(N=n, recall=float((rangos <= n).sum()),
                          carga_mm2=carga_mm2(cx, cy, orden, n)))
    return filas, n_res, len(orden)


def nulo_traslacion(cx, cy, valores, sel, marcas_xy, tol_px, peldanos,
                    mask_tejido, rng, n_iter):
    """Nulo por TRASLACION RIGIDA del conjunto de marcas ([[nulo-espacial-traslacion-rigida]]).

    Nunca permutacion de etiquetas: las marcas son contiguas y una permutacion las trataria como
    independientes. Se acepta la traslacion cuyo conjunto desplazado cae entero sobre tejido, con
    el tejido definido por bloque de 256 px y no por celda de 8 px, que es el bug que dejo el
    nulo vacio en el B9 (ejes_nucleares/resultados.md §1.d).
    """
    m = np.asarray(marcas_xy, float)
    ny, nx = mask_tejido.shape
    W, H = nx * CELL, ny * CELL
    x0, y0 = m[:, 0].min(), m[:, 1].min()
    x1, y1 = m[:, 0].max(), m[:, 1].max()
    out, intentos = [], 0
    while len(out) < n_iter and intentos < n_iter * 200:
        intentos += 1
        tx = rng.uniform(-x0, W - x1)
        ty = rng.uniform(-y0, H - y1)
        mm = m + np.array([tx, ty])
        if not dentro(mask_tejido, mm[:, 0], mm[:, 1]).all():
            continue
        filas, _, _ = escalera(cx, cy, valores, sel, mm, tol_px, peldanos)
        out.append([f["recall"] for f in filas])
    return np.asarray(out, float), intentos


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slides", nargs="*", default=SLIDES + SLIDES_B10)
    ap.add_argument("--npz", default=str(REPO / "results/b9_nucleos"))
    ap.add_argument("--out", default=str(REPO / "results/b10_grado_sin_marca"))
    ap.add_argument("--n-nulo", type=int, default=N_NULO)
    ap.add_argument("--sin-gate-zarr", action="store_true",
                    help="salta la resolucion con zarr (gate y regresion). Solo para iterar.")
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEMILLA)

    print("=" * 104)
    print("O1 — HoVer-NeXt SIN la marca: ¿el descriptor reencuentra los nucleos del patologo?")
    print("=" * 104)
    print(f"prereg: sprints/B10_sprint10/grado_sin_marca/prereg.md")
    print(f"mascara del brazo B: '{CLASE_MASCARA}'   |   parche {LADO_PARCHE_PX} px = "
          f"{AREA_PARCHE_MM2:.4f} mm2   |   nulo: {a.n_nulo} traslaciones (piso p = "
          f"{1/(a.n_nulo+1):.5f})")
    print(f"descriptores: (1) percentil de area intra-lamina  (2) razon contra proxy de "
          f"epitelio normal\n")

    tol_px = TOL_VECINDAD_UM / MPP
    filas_esc, filas_marcas, resumen, nulos = [], [], [], {}
    gate_clases = {}

    for slide in a.slides:
        t0 = time.time()
        npz = Path(a.npz) / f"{slide}_nucleos.npz"
        if not npz.is_file():
            print(f"  {slide:<12} SIN npz -> se salta y se declara")
            resumen.append(dict(slide=slide, estado="sin npz"))
            continue
        z = np.load(npz)
        cls, area_px = z["clase"], z["area_px"].astype(float)
        cx, cy = z["cx"].astype(float), z["cy"].astype(float)
        mpp = float(z["mpp"]); H, W = (int(v) for v in z["shape"])
        area_um2 = area_px * mpp * mpp
        vivo = area_px > 0
        epi = (cls == EPITELIAL) & vivo

        dx, dy, alineada = cargar_offset(slide)
        marcas = marcas_de_grado(slide, dx, dy)
        if not marcas:
            resumen.append(dict(slide=slide, estado="sin marcas de grado"))
            continue
        grados = sorted({g for g, _, _ in marcas})
        mxy = np.asarray([p for _, _, p in marcas], float)

        ny, nx = (H + CELL - 1) // CELL, (W + CELL - 1) // CELL
        polys_mask = cargar_poligonos(slide, dx, dy, {CLASE_MASCARA})
        polys_les = cargar_poligonos(slide, dx, dy, REGIONES_LESIONALES)

        # tejido para el nulo: bloque de 256 px con al menos un nucleo (prereg §5)
        blk = LADO_PARCHE_PX // CELL
        h = np.zeros((ny, nx), dtype=np.int32)
        ix = np.clip((cx[vivo] / CELL).astype(np.int64), 0, nx - 1)
        iy = np.clip((cy[vivo] / CELL).astype(np.int64), 0, ny - 1)
        np.add.at(h, (iy, ix), 1)
        py, px_ = (-ny) % blk, (-nx) % blk
        pad = np.pad(h, ((0, py), (0, px_)))
        b = pad.reshape(pad.shape[0] // blk, blk, pad.shape[1] // blk, blk).sum(axis=(1, 3)) > 0
        tejido = np.repeat(np.repeat(b, blk, axis=0), blk, axis=1)[:ny, :nx]

        # --- proxy de epitelio normal: epiteliales FUERA de toda region lesional (prereg §3)
        if polys_les:
            m_les = mascara_union(polys_les, ny, nx)
            fuera = epi & ~dentro(m_les, cx, cy)
        else:
            fuera = epi.copy()
        n_fuera = int(fuera.sum())
        proxy = float(np.median(area_um2[fuera])) if n_fuera else float("nan")

        # --- los dos descriptores
        pct = np.full(len(cls), np.nan)
        if epi.any():
            ae = area_um2[epi]
            orden = np.argsort(ae, kind="stable")
            r = np.empty(len(ae)); r[orden] = np.arange(len(ae))
            pct[np.nonzero(epi)[0]] = 100.0 * r / max(len(ae) - 1, 1)
        razon = area_um2 / proxy if np.isfinite(proxy) and proxy > 0 else np.full(len(cls), np.nan)

        # --- brazos
        if polys_mask:
            m_tum = mascara_union(polys_mask, ny, nx)
            sel_B = epi & dentro(m_tum, cx, cy)
            area_mask_mm2 = float(m_tum.sum()) * (CELL * mpp / 1000.0) ** 2
        else:
            sel_B = np.zeros(len(cls), dtype=bool)
            area_mask_mm2 = 0.0
        brazos = {"A_lamina_entera": epi, "B_mascara_Tumor": sel_B}

        # --- gate con zarr: regresion exacta contra el B9 (prereg §6)
        gate = {}
        if not a.sin_gate_zarr:
            # `resolver` indexa por ID DE INSTANCIA y el npz es POSICIONAL: cen_de sale de
            # class_inst.json (id -> [fila, columna]) igual que en b9_pleomorfismo.py:290-296,
            # y `pos` traduce id -> posicion para leer la clase del npz. Confundirlos daria
            # clases corridas sin ningun error visible.
            d_hn = paths_de(slide)
            ci = json.loads((d_hn / "class_inst.json").read_text())
            nmax = max(int(k) for k in ci)
            cen_de = np.zeros((nmax + 1, 2), np.float64)
            cls_de = np.zeros(nmax + 1, np.int8)
            for k, v in ci.items():
                cls_de[int(k)] = v[0]
                cen_de[int(k)] = v[1]
            zz = zarr.open(zarr.storage.ZipStore(str(d_hn / "pinst_pp.zip"), mode="r"), mode="r")
            for (g, _, p) in marcas:
                r = resolver(zz, cen_de, p[0], p[1], int(round(tol_px)))
                i = int(r["inst"])
                c = "(ninguna)" if i <= 0 else CLASES.get(int(cls_de[i]), str(cls_de[i]))
                gate.setdefault(g, {}).setdefault(c, 0)
                gate[g][c] += 1
            for g, d in gate.items():
                for c, n in d.items():
                    gate_clases.setdefault(g, {}).setdefault(c, 0)
                    gate_clases[g][c] += n

        for nombre_brazo, sel in brazos.items():
            if not sel.any():
                resumen.append(dict(slide=slide, brazo=nombre_brazo, estado="mascara vacia",
                                    grados="/".join(grados), n_marcas=len(marcas)))
                continue
            for nombre_desc, val in (("percentil", pct), ("razon_normal", razon)):
                peld = [n for n in ESCALERA] + [int(sel.sum())]
                filas, n_res, n_cand = escalera(cx, cy, val, sel, mxy, tol_px, peld)
                for f in filas:
                    filas_esc.append(dict(slide=slide, brazo=nombre_brazo, desc=nombre_desc,
                                          grados="/".join(grados), n_marcas=len(marcas),
                                          n_resueltas=n_res, n_candidatos=n_cand,
                                          alineada=alineada, **f))
                # nulo: solo para el descriptor primario, que es donde se lee
                if nombre_desc == "percentil":
                    nu, intentos = nulo_traslacion(cx, cy, val, sel, mxy, tol_px, peld,
                                                   tejido, rng, a.n_nulo)
                    nulos[(slide, nombre_brazo)] = nu
                    resumen.append(dict(
                        slide=slide, brazo=nombre_brazo, estado="ok",
                        grados="/".join(grados), n_marcas=len(marcas), n_resueltas=n_res,
                        n_candidatos=n_cand, n_epi=int(epi.sum()), n_fuera_region=n_fuera,
                        proxy_um2=proxy, area_mascara_mm2=area_mask_mm2,
                        alineada=alineada, nulo_n=len(nu), nulo_intentos=intentos))

        print(f"  {slide:<12} {'/'.join(grados):<9} marcas {len(marcas):>3}  "
              f"epi {int(epi.sum()):>7}  Tumor {len(polys_mask):>2} pol "
              f"({area_mask_mm2:6.1f} mm2)  proxy {proxy:5.1f} um2 (n={n_fuera})  "
              f"{time.time()-t0:5.1f}s")

    _volcar(out, filas_esc, resumen, nulos, gate_clases)


def _volcar(out, filas_esc, resumen, nulos, gate_clases):
    import pandas as pd
    esc = pd.DataFrame(filas_esc)
    esc.to_csv(out / "escalera.csv", index=False)
    pd.DataFrame(resumen).to_csv(out / "resumen_laminas.csv", index=False)
    np.savez_compressed(out / "nulo.npz",
                        **{f"{s}__{b}": v for (s, b), v in nulos.items()})
    (out / "gate_clases.json").write_text(json.dumps(gate_clases, indent=2, sort_keys=True))
    print(f"\nescrito: {out}/escalera.csv ({len(esc)} filas), resumen_laminas.csv, "
          f"nulo.npz, gate_clases.json")


if __name__ == "__main__":
    main()
