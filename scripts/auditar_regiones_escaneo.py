#!/usr/bin/env python
"""Auditoría de regiones de escaneo en la cohorte privada.

Encargo B de la reunión del 12-ago-2026. Sebastián atribuyó las «dos láminas»
de la 129741 a un csv que repetía dos veces lo mismo; los CSV del pipeline ya
se auditaron y no tienen duplicados (ver el resultados.md de al lado), así que
lo que queda por testear es si el .bif contiene DOS ESCANEOS DE LA MISMA
LÁMINA, y cuántas WSI más están en la misma situación.

Tres subcomandos, independientes entre sí:

  barrido    geometría de toda la cohorte: propiedades openslide.region[N].* de
             cada .bif + la geometría de la grilla del h5. Reanudable.
  contenido  ¿son el mismo tejido las dos regiones de una lámina? Barrido 2D de
             traslación sobre las features CONCH del h5, sin abrir la WSI.
  miniaturas vuelca las dos regiones a PNG para comparar píxeles a ojo.

Lee `clam_environ/` y `wsi/` (read-only), escribe SOLO bajo este repo.
Python: /home/sdonoso/miniconda3/envs/clam_latest/bin/python (workaround B).
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from collections import Counter
from pathlib import Path

import numpy as np

WSI_DIR = Path("/media/administrador/Storage1/sdonoso/wsi")
H5_DIR = Path("/media/administrador/Storage1/sdonoso/clam_environ/environ/features/h5_files")
PT_DIR = Path("/media/administrador/Storage1/sdonoso/clam_environ/environ/features/pt_files")
REPO = Path("/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto")
OUT_DIR = REPO / "sprints/B8_sprint8/anotaciones_patologo/regiones_escaneo"

# columnas del CSV del barrido
CAMPOS = [
    "slide_id", "bif", "tiene_h5", "vendor", "mpp_x", "objective_power",
    "level0_w", "level0_h", "n_regiones", "regiones_json",
    "n_parches", "paso_grilla", "n_bandas_h5", "bandas_json", "error",
]


# --------------------------------------------------------------------------
# geometría del h5
# --------------------------------------------------------------------------
def paso_de_grilla(coords: np.ndarray) -> int:
    """Paso de la grilla desde la geometría REAL de las coords, nunca desde la
    magnificación ([[patch-size-desde-geometria-h5]])."""
    diffs = []
    for y in np.unique(coords[:, 1])[:400]:
        xs = np.sort(coords[coords[:, 1] == y][:, 0])
        d = np.diff(xs)
        diffs += d[d > 0].tolist()
    if not diffs:
        return 0
    return int(Counter(diffs).most_common(1)[0][0])


def bandas_verticales(coords: np.ndarray, paso: int, factor: float = 3.0):
    """Parte las filas de la grilla en bandas separadas por huecos verticales.

    Una lámina con dos regiones de escaneo deja un hueco vertical grande entre
    ellas. `factor` es cuántos pasos de grilla tiene que medir el hueco para
    contarlo como separación de banda (3 pasos = 768 px con parche 256).
    """
    if paso <= 0:
        return []
    ys = np.unique(coords[:, 1])
    if len(ys) == 0:
        return []
    cortes = np.where(np.diff(ys) > factor * paso)[0]
    tramos = np.split(ys, cortes + 1)
    bandas = []
    for t in tramos:
        sel = coords[np.isin(coords[:, 1], t)]
        bandas.append({
            "y_min": int(t.min()), "y_max": int(t.max()),
            "x_min": int(sel[:, 0].min()), "x_max": int(sel[:, 0].max()),
            "n_parches": int(len(sel)),
        })
    return bandas


def geometria_h5(slide_id: str):
    h5 = H5_DIR / f"{slide_id}.h5"
    if not h5.exists():
        return None
    import h5py
    with h5py.File(h5, "r") as f:
        coords = np.array(f["coords"])
    paso = paso_de_grilla(coords)
    return {"n_parches": int(len(coords)), "paso": paso,
            "bandas": bandas_verticales(coords, paso)}


# --------------------------------------------------------------------------
# subcomando: barrido
# --------------------------------------------------------------------------
def bif_limpio(carpeta: Path) -> Path | None:
    """El .bif que usa el pipeline es el que NO lleva sufijo de tinción.

    En cada carpeta conviven el H&E y los .bif de inmunohistoquímica
    (`<id> HER-2.bif`, `KI67`, `RE`, `RP`). El del pipeline es `<id>.bif`.
    """
    cand = carpeta / f"{carpeta.name}.bif"
    return cand if cand.exists() else None


def props_openslide(path: Path) -> dict:
    import openslide
    sl = openslide.OpenSlide(str(path))
    try:
        p = dict(sl.properties)
        w, h = sl.level_dimensions[0]
    finally:
        sl.close()
    regiones = []
    i = 0
    while f"openslide.region[{i}].width" in p:
        regiones.append({
            "i": i,
            "x": int(p[f"openslide.region[{i}].x"]),
            "y": int(p[f"openslide.region[{i}].y"]),
            "w": int(p[f"openslide.region[{i}].width"]),
            "h": int(p[f"openslide.region[{i}].height"]),
        })
        i += 1
    return {
        "vendor": p.get("openslide.vendor", ""),
        "mpp_x": p.get("openslide.mpp-x", ""),
        "objective_power": p.get("openslide.objective-power", ""),
        "level0_w": w, "level0_h": h,
        "regiones": regiones,
    }


def barrido(args):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    salida = OUT_DIR / "regiones_por_slide.csv"

    hechos = set()
    if salida.exists() and not args.rehacer:
        with open(salida, newline="") as f:
            hechos = {r["slide_id"] for r in csv.DictReader(f)}
        print(f"[reanuda] {len(hechos)} láminas ya auditadas, se saltan", flush=True)

    carpetas = sorted(d for d in WSI_DIR.iterdir() if d.is_dir())
    print(f"[barrido] {len(carpetas)} carpetas en {WSI_DIR}", flush=True)

    nuevo = not salida.exists() or args.rehacer
    with open(salida, "a" if not nuevo else "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS)
        if nuevo:
            w.writeheader()
        for n, carpeta in enumerate(carpetas, 1):
            sid = carpeta.name
            if sid in hechos:
                continue
            fila = {c: "" for c in CAMPOS}
            fila["slide_id"] = sid
            try:
                bif = bif_limpio(carpeta)
                if bif is None:
                    fila["error"] = "sin .bif sin sufijo de tincion"
                else:
                    fila["bif"] = bif.name
                    pr = props_openslide(bif)
                    fila.update({
                        "vendor": pr["vendor"], "mpp_x": pr["mpp_x"],
                        "objective_power": pr["objective_power"],
                        "level0_w": pr["level0_w"], "level0_h": pr["level0_h"],
                        "n_regiones": len(pr["regiones"]),
                        "regiones_json": json.dumps(pr["regiones"], separators=(",", ":")),
                    })
                g = geometria_h5(sid)
                fila["tiene_h5"] = int(g is not None)
                if g:
                    fila.update({
                        "n_parches": g["n_parches"], "paso_grilla": g["paso"],
                        "n_bandas_h5": len(g["bandas"]),
                        "bandas_json": json.dumps(g["bandas"], separators=(",", ":")),
                    })
            except Exception as e:  # una lámina rota no puede matar el barrido
                fila["error"] = f"{type(e).__name__}: {e}"
            w.writerow(fila)
            f.flush()
            if n % 25 == 0:
                print(f"[barrido] {n}/{len(carpetas)}  ultima={sid}", flush=True)
    print(f"[barrido] listo -> {salida}", flush=True)


# --------------------------------------------------------------------------
# subcomando: contenido
# --------------------------------------------------------------------------
def contenido(args):
    """¿Las dos regiones son el mismo tejido escaneado dos veces?

    Criterio fijado ANTES de mirar (§3.b del handoff): dos secciones seriadas
    del mismo bloque se parecen mucho sin ser el mismo escaneo, así que un
    coseno alto NO alcanza. Lo que separa un re-escaneo de una sección vecina
    es que el emparejamiento óptimo sea CASI BIYECTIVO y con un desplazamiento
    ÚNICO Y CONSISTENTE para toda la región. Si el óptimo es difuso o depende
    de la zona, son secciones distintas.
    """
    import h5py
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    sid = args.slide

    with h5py.File(H5_DIR / f"{sid}.h5", "r") as f:
        coords = np.array(f["coords"])
        feats = np.array(f["features"]).astype(np.float64)
    paso = paso_de_grilla(coords)
    print(f"[data] {sid}: N={len(coords)} parches, features {feats.shape}, paso={paso}")

    # normalizar para que el producto punto SEA el coseno
    feats /= np.linalg.norm(feats, axis=1, keepdims=True)

    bandas = bandas_verticales(coords, paso)
    print(f"[data] {len(bandas)} bandas por hueco vertical en el h5:")
    for i, b in enumerate(bandas):
        print(f"   banda {i}: y {b['y_min']}..{b['y_max']}  x {b['x_min']}..{b['x_max']}  "
              f"n={b['n_parches']}")
    if len(bandas) != 2:
        print(f"[stop] esta lámina no tiene exactamente 2 bandas; nada que emparejar")
        return

    ba, bb = bandas
    ia = np.where((coords[:, 1] >= ba["y_min"]) & (coords[:, 1] <= ba["y_max"]))[0]
    ib = np.where((coords[:, 1] >= bb["y_min"]) & (coords[:, 1] <= bb["y_max"]))[0]
    ca, cb = coords[ia], coords[ib]
    fa, fb = feats[ia], feats[ib]
    print(f"[data] banda 0: {len(ia)} parches   banda 1: {len(ib)} parches")

    # ---- línea base correcta: pares al azar DENTRO de la misma banda ----
    rng = np.random.default_rng(args.seed)
    def azar_intra(fx, n=20000):
        i = rng.integers(0, len(fx), n)
        j = rng.integers(0, len(fx), n)
        m = i != j
        return (fx[i[m]] * fx[j[m]]).sum(1)
    base_a, base_b = azar_intra(fa), azar_intra(fb)
    inter = (fa[rng.integers(0, len(fa), 20000)] * fb[rng.integers(0, len(fb), 20000)]).sum(1)
    print(f"\n[base] coseno de pares AL AZAR dentro de la banda 0: "
          f"{base_a.mean():.3f} ± {base_a.std():.3f}")
    print(f"[base] coseno de pares AL AZAR dentro de la banda 1: "
          f"{base_b.mean():.3f} ± {base_b.std():.3f}")
    print(f"[base] coseno de pares AL AZAR entre las dos bandas:  "
          f"{inter.mean():.3f} ± {inter.std():.3f}")

    # ---- barrido 2D de traslación, en múltiplos del paso de grilla ----
    # la grilla arranca en (0,0) con paso fijo, así que una traslación por un
    # múltiplo del paso manda lattice sobre lattice y los «gemelos» son
    # coincidencias EXACTAS de coordenada. Eso es lo que el test viejo no hizo.
    idx_a = {(int(x), int(y)): k for k, (x, y) in enumerate(ca)}
    r = args.rango
    dxs = np.arange(-r, r + 1) * paso
    dy0 = int(round((bb["y_min"] - ba["y_min"]) / paso)) * paso
    dys = dy0 + np.arange(-r, r + 1) * paso

    print(f"\n[barrido] dx en {dxs[0]}..{dxs[-1]}, dy en {dys[0]}..{dys[-1]} "
          f"(paso {paso}, {len(dxs)}x{len(dys)} offsets); dy nominal = {dy0}")
    filas = []
    for dy in dys:
        for dx in dxs:
            pa, pb = [], []
            for k, (x, y) in enumerate(cb):
                j = idx_a.get((int(x) - int(dx), int(y) - int(dy)))
                if j is not None:
                    pa.append(j); pb.append(k)
            if len(pa) < args.min_pares:
                continue
            cos = (fa[pa] * fb[pb]).sum(1)
            filas.append((int(dx), int(dy), len(pa), float(cos.mean()), float(np.median(cos))))
    if not filas:
        print("[stop] ningún offset alcanzó el mínimo de pares")
        return
    filas.sort(key=lambda t: -t[3])

    print(f"\n[barrido] top 10 offsets por coseno medio:")
    print(f"{'dx':>8} {'dy':>8} {'n_pares':>8} {'cos_medio':>10} {'cos_mediana':>12}")
    for dx, dy, n, m, md in filas[:10]:
        print(f"{dx:>8} {dy:>8} {n:>8} {m:>10.4f} {md:>12.4f}")

    dx, dy, npares, cmed, cmedian = filas[0]
    # ¿el óptimo destaca, o la superficie es plana? (si es plana, no hay
    # desplazamiento único y consistente -> no es un re-escaneo)
    todos = np.array([f[3] for f in filas])
    print(f"\n[optimo] dx={dx} dy={dy}: {npares} pares, coseno {cmed:.4f} "
          f"(mediana {cmedian:.4f})")
    print(f"[optimo] coseno medio sobre TODOS los offsets: {todos.mean():.4f} ± {todos.std():.4f}")
    print(f"[optimo] el óptimo está a {(cmed - todos.mean()) / (todos.std() + 1e-12):.2f} "
          f"desviaciones del offset típico")

    # cobertura: qué fracción de la banda chica encuentra gemelo en el óptimo
    cob = npares / min(len(ia), len(ib))
    print(f"[optimo] cobertura (biyectividad): {npares}/{min(len(ia), len(ib))} = {cob:.3f}")

    # ---- distribución en el óptimo vs la línea base ----
    pa, pb = [], []
    for k, (x, y) in enumerate(cb):
        j = idx_a.get((int(x) - dx, int(y) - dy))
        if j is not None:
            pa.append(j); pb.append(k)
    cos_opt = (fa[pa] * fb[pb]).sum(1)
    qs = [1, 5, 25, 50, 75, 95, 99]
    print(f"\n[dist] coseno de los gemelos en el óptimo, percentiles:")
    print("   " + "  ".join(f"p{q}={np.percentile(cos_opt, q):.3f}" for q in qs))
    print(f"[dist] fracción de gemelos con coseno > 0.95: "
          f"{(cos_opt > 0.95).mean():.4f}   > 0.99: {(cos_opt > 0.99).mean():.4f}")

    # ---- vecino más cercano: si es duplicado, casi todos tienen gemelo casi exacto ----
    print(f"\n[vecino] coseno con el MEJOR parche de la otra banda (no el geométrico)...")
    best = np.empty(len(fa))
    blk = 256
    for s in range(0, len(fa), blk):
        best[s:s + blk] = (fa[s:s + blk] @ fb.T).max(1)
    print(f"[vecino] banda 0 -> banda 1: medio {best.mean():.4f}, mediana "
          f"{np.median(best):.4f}, p5 {np.percentile(best, 5):.4f}")
    print(f"[vecino] fracción con vecino > 0.95: {(best > 0.95).mean():.4f}   "
          f"> 0.99: {(best > 0.99).mean():.4f}")
    # control: el mismo estadístico DENTRO de la banda 0 (excluyéndose a sí mismo)
    ctrl = np.empty(len(fa))
    for s in range(0, len(fa), blk):
        g = fa[s:s + blk] @ fa.T
        for t in range(g.shape[0]):
            g[t, s + t] = -1.0
        ctrl[s:s + blk] = g.max(1)
    print(f"[vecino] CONTROL banda 0 -> banda 0 (sin sí mismo): medio {ctrl.mean():.4f}, "
          f"mediana {np.median(ctrl):.4f}")
    print(f"[vecino] control, fracción > 0.95: {(ctrl > 0.95).mean():.4f}")

    res = {
        "slide_id": sid, "paso": paso,
        "n_banda_0": int(len(ia)), "n_banda_1": int(len(ib)),
        "bandas": bandas,
        "base_intra_banda0": [float(base_a.mean()), float(base_a.std())],
        "base_intra_banda1": [float(base_b.mean()), float(base_b.std())],
        "base_entre_bandas": [float(inter.mean()), float(inter.std())],
        "optimo": {"dx": dx, "dy": dy, "n_pares": npares, "cos_medio": cmed,
                   "cos_mediana": cmedian, "cobertura": float(cob)},
        "superficie_offsets": {"media": float(todos.mean()), "std": float(todos.std()),
                               "n_offsets": len(filas)},
        "gemelos_optimo": {f"p{q}": float(np.percentile(cos_opt, q)) for q in qs}
        | {"frac_gt_095": float((cos_opt > 0.95).mean()),
           "frac_gt_099": float((cos_opt > 0.99).mean())},
        "vecino_mas_cercano": {
            "medio": float(best.mean()), "mediana": float(np.median(best)),
            "p5": float(np.percentile(best, 5)),
            "frac_gt_095": float((best > 0.95).mean()),
            "frac_gt_099": float((best > 0.99).mean()),
            "control_intra_medio": float(ctrl.mean()),
            "control_intra_frac_gt_095": float((ctrl > 0.95).mean()),
        },
        "top_offsets": filas[:10],
    }
    p = OUT_DIR / f"contenido_{sid}.json"
    p.write_text(json.dumps(res, indent=2))
    print(f"\n[out] {p}")


# --------------------------------------------------------------------------
# subcomando: miniaturas
# --------------------------------------------------------------------------
def miniaturas(args):
    """El test barato y decisivo: mirar los píxeles de las dos regiones."""
    import openslide
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    sid = args.slide
    bif = bif_limpio(WSI_DIR / sid)
    sl = openslide.OpenSlide(str(bif))
    p = sl.properties
    regs = []
    i = 0
    while f"openslide.region[{i}].width" in p:
        regs.append((int(p[f"openslide.region[{i}].x"]), int(p[f"openslide.region[{i}].y"]),
                     int(p[f"openslide.region[{i}].width"]), int(p[f"openslide.region[{i}].height"])))
        i += 1
    print(f"[wsi] {bif.name}: level0={sl.level_dimensions[0]}, {len(regs)} regiones")
    lvl = sl.get_best_level_for_downsample(args.downsample)
    ds = sl.level_downsamples[lvl]
    print(f"[wsi] level {lvl}, downsample real {ds:.1f}")
    for k, (x, y, w, h) in enumerate(regs):
        print(f"   region[{k}] = ({x},{y}) {w}x{h}")
        im = sl.read_region((x, y), lvl, (int(w / ds), int(h / ds))).convert("RGB")
        out = OUT_DIR / f"{sid}_region{k}.png"
        im.save(out)
        print(f"   -> {out}  ({im.size[0]}x{im.size[1]} px)")
    sl.close()


# --------------------------------------------------------------------------
# subcomando: registro
# --------------------------------------------------------------------------
def _ncc(a: np.ndarray, b: np.ndarray) -> float:
    """Correlación cruzada normalizada entre dos arrays de igual forma."""
    a = a.astype(np.float64).ravel(); b = b.astype(np.float64).ravel()
    a -= a.mean(); b -= b.mean()
    d = np.linalg.norm(a) * np.linalg.norm(b)
    return float(a @ b / d) if d > 0 else 0.0


def _fase(a: np.ndarray, b: np.ndarray):
    """Correlación de fase: devuelve el (dy, dx) que lleva `b` sobre `a`."""
    A, B = np.fft.fft2(a - a.mean()), np.fft.fft2(b - b.mean())
    R = A * np.conj(B)
    R /= np.abs(R) + 1e-12
    r = np.fft.ifft2(R).real
    dy, dx = np.unravel_index(np.argmax(r), r.shape)
    if dy > a.shape[0] // 2:
        dy -= a.shape[0]
    if dx > a.shape[1] // 2:
        dx -= a.shape[1]
    return int(dy), int(dx), float(r.max() / (r.std() + 1e-12))


def registro(args):
    """El test decisivo: ¿son los MISMOS PÍXELES, o sea las mismas células?

    Un re-escaneo de la misma lámina muestra las mismas células en la misma
    posición; dos secciones seriadas del mismo bloque muestran el mismo tejido
    con células DISTINTAS. Las features CONCH no separan los dos casos porque
    son suaves sobre el tejido (el coseno con el vecino de al lado ya da 0.90),
    así que hay que ir al píxel.
    """
    import openslide
    from PIL import Image
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    sid = args.slide
    sl = openslide.OpenSlide(str(bif_limpio(WSI_DIR / sid)))
    p = sl.properties
    regs = []
    i = 0
    while f"openslide.region[{i}].width" in p:
        regs.append((int(p[f"openslide.region[{i}].x"]), int(p[f"openslide.region[{i}].y"]),
                     int(p[f"openslide.region[{i}].width"]), int(p[f"openslide.region[{i}].height"])))
        i += 1
    if len(regs) != 2:
        print(f"[stop] {sid} tiene {len(regs)} regiones, no 2")
        return
    (x0, y0, w0, h0), (x1, y1, w1, h1) = regs

    # --- 1. registro grueso por correlación de fase, a baja resolución ---
    lvl = sl.get_best_level_for_downsample(args.downsample)
    ds = sl.level_downsamples[lvl]
    w = min(w0, w1); h = min(h0, h1)
    gw, gh = int(w / ds), int(h / ds)
    g0 = np.asarray(sl.read_region((x0, y0), lvl, (gw, gh)).convert("L"), dtype=np.float64)
    g1 = np.asarray(sl.read_region((x1, y1), lvl, (gw, gh)).convert("L"), dtype=np.float64)
    print(f"[grueso] level {lvl} (downsample {ds:.0f}), miniatura {gw}x{gh}")
    ncc0 = _ncc(g0, g1)
    # búsqueda exhaustiva de la traslación entera: a 540x480 cuesta nada y es
    # más robusta que la correlación de fase, que acá encontraba un pico falso
    R = args.rango_grueso
    mejor = (-2.0, 0, 0)
    for oy in range(-R, R + 1):
        for ox in range(-R, R + 1):
            a = g0[max(0, oy):gh + min(0, oy), max(0, ox):gw + min(0, ox)]
            b = g1[max(0, -oy):gh + min(0, -oy), max(0, -ox):gw + min(0, -ox)]
            v = _ncc(a, b)
            if v > mejor[0]:
                mejor = (v, ox, oy)
    ncc_reg, ox, oy = mejor
    print(f"[grueso] mejor traslación: dx={ox} dy={oy} px de miniatura, o sea "
          f"dx={int(ox*ds)} dy={int(oy*ds)} px de level 0")
    print(f"[grueso] NCC sin registrar: {ncc0:.4f}   registrada: {ncc_reg:.4f}")

    # control: la misma comparación contra la región 1 puesta del revés. Es el
    # «mismo tejido, mala alineación» y acota cuánto NCC regala la silueta sola.
    a = g0[max(0, oy):gh + min(0, oy), max(0, ox):gw + min(0, ox)]
    b = g1[max(0, -oy):gh + min(0, -oy), max(0, -ox):gw + min(0, -ox)]
    ncc_esp = _ncc(a, b[:, ::-1])
    print(f"[control] NCC contra la región 1 espejada: {ncc_esp:.4f}")

    DX, DY = int(ox * ds), int(oy * ds)

    # --- 2. al píxel, en level 0, sobre un recorte con tejido DE VERDAD ---
    # se elige la ventana de la miniatura con más tejido, no la mediana de las
    # coordenadas del tejido (que cae en el hueco entre fragmentos)
    L = args.recorte
    lado = max(1, int(L / ds))
    # el borde negro del lienzo (fuera de la región) NO es tejido: la banda de
    # abajo lo excluye. Sin esto la ventana «más densa» cae en el relleno.
    tej = ((g0 > args.umbral_fondo) & (g0 < args.umbral_tejido)).astype(np.float64)
    integral = np.cumsum(np.cumsum(tej, 0), 1)
    def dens(y, x):
        y2, x2 = y + lado, x + lado
        return (integral[y2, x2] - integral[y, x2] - integral[y2, x] + integral[y, x])
    mejor_d, cy, cx = -1.0, 0, 0
    for y in range(0, gh - lado - 1, max(1, lado // 2)):
        for x in range(0, gw - lado - 1, max(1, lado // 2)):
            d = dens(y, x)
            if d > mejor_d:
                mejor_d, cy, cx = d, y, x
    print(f"\n[fino] ventana más densa en tejido: ({cx},{cy}) de la miniatura, "
          f"{mejor_d/(lado*lado):.0%} tejido")
    ax = x0 + int(cx * ds)
    ay = y0 + int(cy * ds)
    print(f"\n[fino] recorte de {L}x{L} en level 0, centro de masa del tejido "
          f"-> región 0 en ({ax},{ay})")
    c0 = sl.read_region((ax, ay), 0, (L, L)).convert("RGB")
    # la región 1 arranca en y1; el mismo punto físico está en (ax - DX, ay - y0 + y1 - DY)
    bx, by = ax - DX, ay - y0 + y1 - DY
    print(f"[fino] mismo punto físico en la región 1 -> ({bx},{by})")
    c1 = sl.read_region((bx, by), 0, (L, L)).convert("RGB")

    a = np.asarray(c0.convert("L"), dtype=np.float64)
    b = np.asarray(c1.convert("L"), dtype=np.float64)
    dy2, dx2, pico2 = _fase(a, b)
    print(f"[fino] residuo de registro dentro del recorte: dx={dx2} dy={dy2} px "
          f"(pico {pico2:.1f} sd)")
    b2 = np.roll(np.roll(b, dy2, 0), dx2, 1)
    mm = slice(abs(dy2) + 8, L - abs(dy2) - 8), slice(abs(dx2) + 8, L - abs(dx2) - 8)
    ncc_fino = _ncc(a[mm], b2[mm])
    print(f"[fino] NCC al píxel, level 0, tras registrar: {ncc_fino:.4f}")
    # control en el mismo recorte: contra un desplazamiento de media célula
    ctrl = _ncc(a[mm], np.roll(b2, args.control_shift, 1)[mm])
    print(f"[fino] control, el mismo recorte corrido {args.control_shift} px: {ctrl:.4f}")

    par = Image.new("RGB", (L * 2 + 16, L), "white")
    par.paste(c0, (0, 0)); par.paste(c1, (L + 16, 0))
    out = OUT_DIR / f"{sid}_registro_level0.png"
    par.save(out)
    print(f"\n[out] {out}  (izq = región 0, der = región 1, mismo punto físico)")

    res = {
        "slide_id": sid, "regiones": regs,
        "grueso": {"level": lvl, "downsample": ds, "dx_level0": DX, "dy_level0": DY,
                   "ncc_sin_registrar": ncc0, "ncc_registrada": ncc_reg,
                   "ncc_control_espejo": ncc_esp},
        "fino": {"recorte": L, "origen_region0": [ax, ay], "origen_region1": [bx, by],
                 "residuo_dx": dx2, "residuo_dy": dy2, "pico_sd": pico2,
                 "ncc": ncc_fino, "ncc_control_corrido": ctrl},
    }
    (OUT_DIR / f"registro_{sid}.json").write_text(json.dumps(res, indent=2))
    sl.close()


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("barrido", help="geometría de toda la cohorte privada")
    b.add_argument("--rehacer", action="store_true", help="ignorar el CSV previo")
    b.set_defaults(func=barrido)

    c = sub.add_parser("contenido", help="¿son el mismo tejido las dos regiones?")
    c.add_argument("--slide", default="129741")
    c.add_argument("--rango", type=int, default=10, help="offsets a barrer, en pasos de grilla")
    c.add_argument("--min-pares", type=int, default=50)
    c.add_argument("--seed", type=int, default=0)
    c.set_defaults(func=contenido)

    m = sub.add_parser("miniaturas", help="vuelca las regiones a PNG")
    m.add_argument("--slide", default="129741")
    m.add_argument("--downsample", type=float, default=64.0)
    m.set_defaults(func=miniaturas)

    r = sub.add_parser("registro", help="¿son los mismos píxeles? (el test decisivo)")
    r.add_argument("--slide", default="129741")
    r.add_argument("--downsample", type=float, default=64.0)
    r.add_argument("--recorte", type=int, default=1024, help="lado del recorte en level 0")
    r.add_argument("--umbral-tejido", type=float, default=210.0)
    r.add_argument("--umbral-fondo", type=float, default=40.0)
    r.add_argument("--rango-grueso", type=int, default=12)
    r.add_argument("--control-shift", type=int, default=64)
    r.set_defaults(func=registro)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    sys.exit(main())
