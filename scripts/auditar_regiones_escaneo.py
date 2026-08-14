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
  registro   el test decisivo: ¿son los MISMOS PÍXELES? Registro grueso a baja
             resolución + búsqueda LOCAL de cada ventana a level 0, con control
             de sitio equivocado. Ver el docstring de registro() para el
             criterio y para por qué la primera versión no podía funcionar.

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


def _mapa_ncc(img: np.ndarray, tpl: np.ndarray):
    """NCC de `tpl` deslizada sobre `img`, en modo 'valid'.

    Numerador por FFT y denominador por imagen integral (el mismo algoritmo que
    `match_template` de skimage, que no está en este env). Devuelve un mapa de
    forma (H-h+1, W-w+1) donde cada celda es el coseno centrado entre la
    plantilla y la ventana de `img` que arranca ahí.
    """
    from scipy.signal import fftconvolve
    img = img.astype(np.float64)
    tpl = tpl.astype(np.float64)
    h, w = tpl.shape
    n = h * w
    t0 = tpl - tpl.mean()
    den_t = float(np.sqrt((t0 ** 2).sum()))
    if den_t <= 0:
        return None
    num = fftconvolve(img, t0[::-1, ::-1], mode="valid")
    ii = np.cumsum(np.cumsum(np.pad(img, ((1, 0), (1, 0))), 0), 1)
    ii2 = np.cumsum(np.cumsum(np.pad(img * img, ((1, 0), (1, 0))), 0), 1)

    def ventana(I):
        return I[h:, w:] - I[:-h, w:] - I[h:, :-w] + I[:-h, :-w]

    s1, s2 = ventana(ii), ventana(ii2)
    var = s2 - s1 * s1 / n
    var[var < 1e-9] = np.inf
    return num / (np.sqrt(var) * den_t)


def _pico(mapa: np.ndarray, radio: int = 24):
    """Máximo del mapa de NCC + a cuántas sd está del resto.

    `radio` excluye el entorno del pico al medir el fondo, para que la propia
    campana del pico no infle la sd.
    """
    iy, ix = np.unravel_index(np.argmax(mapa), mapa.shape)
    pico = float(mapa[iy, ix])
    fuera = mapa.copy()
    y0, y1 = max(0, iy - radio), min(mapa.shape[0], iy + radio + 1)
    x0, x1 = max(0, ix - radio), min(mapa.shape[1], ix + radio + 1)
    fuera[y0:y1, x0:x1] = np.nan
    mu, sd = np.nanmean(fuera), np.nanstd(fuera)
    segundo = float(np.nanmax(fuera)) if np.isfinite(fuera).any() else float("nan")
    return {
        "ncc": pico, "iy": int(iy), "ix": int(ix),
        "fondo_medio": float(mu), "fondo_sd": float(sd),
        "sd_sobre_fondo": float((pico - mu) / (sd + 1e-12)),
        "segundo_pico": segundo,
    }


def _buscar_local(sl, tpl_xy, dest_xy, L0: int, M0: int, lvl: int, ds: float):
    """Busca la ventana `L0`×`L0` de level 0 que arranca en `tpl_xy` dentro de
    un entorno de ±`M0` px alrededor de `dest_xy`, trabajando en el nivel `lvl`.

    Devuelve el pico del mapa de NCC y el desplazamiento residual (en px de
    level 0) entre donde se predijo la ventana y donde realmente está. Este es
    el arreglo de fondo del test: la posición NO se deriva de un offset global
    (que a level 6 tiene ±32 px de cuantización, o sea media docena de células),
    se BUSCA.
    """
    lt = int(round(L0 / ds))
    lb = int(round((L0 + 2 * M0) / ds))
    tpl = np.asarray(sl.read_region(tuple(tpl_xy), lvl, (lt, lt)).convert("L"),
                     dtype=np.float64)
    org = (int(dest_xy[0] - M0), int(dest_xy[1] - M0))
    img = np.asarray(sl.read_region(org, lvl, (lb, lb)).convert("L"),
                     dtype=np.float64)
    if tpl.std() < 1.0 or img.std() < 1.0:
        return None
    mapa = _mapa_ncc(img, tpl)
    if mapa is None:
        return None
    r = _pico(mapa)
    # el centro del mapa (offset residual cero) está en (M0/ds, M0/ds)
    c = int(round(M0 / ds))
    r["dx_level0"] = int(round((r["ix"] - c) * ds))
    r["dy_level0"] = int(round((r["iy"] - c) * ds))
    r["ncc_en_prediccion"] = float(mapa[c, c])
    return r


def _ajuste_rigido(u: np.ndarray, v: np.ndarray, con_escala: bool = True):
    """Ajusta v = esc·R(θ)·u + t por mínimos cuadrados (Procrustes 2D).

    `u` y `v` son (N,2) en (x,y). Devuelve θ en grados, la escala, la
    traslación y el residuo por punto. El residuo es lo que más pesa: si un
    ÚNICO cuerpo rígido explica el campo de desplazamiento de fragmentos de
    tejido separados, es porque los fragmentos no se movieron entre una imagen
    y la otra.
    """
    cu, cv = u.mean(0), v.mean(0)
    U, V = u - cu, v - cv
    num = float((U[:, 0] * V[:, 1] - U[:, 1] * V[:, 0]).sum())
    den = float((U * V).sum())
    th = np.arctan2(num, den)
    c, s = np.cos(th), np.sin(th)
    R = np.array([[c, -s], [s, c]])
    esc = float(np.sqrt((num ** 2 + den ** 2)) / (U ** 2).sum()) if con_escala else 1.0
    t = cv - esc * (R @ cu)
    pred = (esc * (R @ u.T)).T + t
    res = v - pred
    return {
        "theta_grados": float(np.degrees(th)), "escala": esc,
        "traslacion": [float(t[0]), float(t[1])],
        "residuo_px": [[float(a), float(b)] for a, b in res],
        "rms_px": float(np.sqrt((res ** 2).sum(1).mean())),
        "max_px": float(np.sqrt((res ** 2).sum(1)).max()),
    }


def _alinear_array(I: np.ndarray, lado: int, theta_grados: float, esc: float):
    """Rota y escala el array `I` al marco de la región 0 y devuelve el recorte
    central de `lado`×`lado`.

    Convención verificada end-to-end contra una transformación sintética
    conocida (ver `tests/test_registro_geometria.py`): con el ajuste
    v = esc·R(θ)·u + t, el muestreo de la entrada para el píxel de salida `o`
    es esc·R_rc·(o − centro) + S/2, con R_rc la matriz en orden (fila, columna).
    """
    from scipy.ndimage import affine_transform
    th = np.radians(theta_grados)
    c, s = np.cos(th), np.sin(th)
    M = esc * np.array([[c, s], [-s, c]])
    S = I.shape[0]
    off = np.array([S / 2.0, S / 2.0]) - M @ np.array([lado / 2.0, lado / 2.0])
    return affine_transform(I, M, offset=off, output_shape=(lado, lado), order=1)


def _recorte_alineado(sl, centro_xy, lado: int, theta_grados: float, esc: float):
    """`_alinear_array` leyendo de la WSI alrededor de `centro_xy`, a level 0."""
    S = int(esc * lado * 1.45) + 8
    org = (int(centro_xy[0] - S // 2), int(centro_xy[1] - S // 2))
    I = np.asarray(sl.read_region(org, 0, (S, S)).convert("L"), dtype=np.float64)
    return _alinear_array(I, lado, theta_grados, esc)


def _mejor_con_rotacion(sl, tpl, centro_xy, Lo, thetas):
    """Busca `tpl` alrededor de `centro_xy` probando varias rotaciones.

    Lee UNA vez y rota en memoria. Devuelve el mejor pico sobre todo el barrido,
    para que la señal y el control tengan exactamente los mismos grados de
    libertad: si al control se le niega el barrido de rotación, la comparación
    queda amañada a favor de la señal.
    """
    S = int(Lo * 1.45) + 8
    org = (int(centro_xy[0] - S // 2), int(centro_xy[1] - S // 2))
    I = np.asarray(sl.read_region(org, 0, (S, S)).convert("L"), dtype=np.float64)
    if I.std() < 1.0 or tpl.std() < 1.0:
        return None
    mejor = None
    for th in thetas:
        m = _mapa_ncc(_alinear_array(I, Lo, th, 1.0), tpl)
        if m is None:
            continue
        r = _pico(m)
        if mejor is None or r["ncc"] > mejor["ncc"]:
            r["theta"] = float(th)
            mejor = r
    return mejor


def registro(args):
    """El test decisivo: ¿son los MISMOS PÍXELES, o sea las mismas células?

    Un re-escaneo de la misma lámina muestra las mismas células en la misma
    posición; dos secciones seriadas del mismo bloque muestran el mismo tejido,
    con la misma disposición de fragmentos, pero con células DISTINTAS. Las
    features CONCH no separan los dos casos porque son suaves sobre el tejido
    (el coseno con el parche de al lado ya da 0.90), así que hay que ir al píxel.

    POR QUÉ LA PRIMERA VERSIÓN NO PODÍA FUNCIONAR (13-ago). Derivaba la posición
    en la región 1 de un ÚNICO offset global medido a level 6, donde 1 px de
    miniatura son 64 px de level 0, o sea unas cinco células. Aun con el mapeo
    perfecto, la cuantización deja hasta ±32 px de error, y cualquier rotación
    o deformación entre los dos escaneos agrega mucho más. Un NCC a level 0
    necesita precisión de pocos píxeles: daba cero por construcción, midiera lo
    que midiera. Acá la posición NO se deriva, se BUSCA, ventana por ventana y
    en dos etapas.

    CRITERIO, fijado antes de correr:
      - MISMA LÁMINA escaneada dos veces: la etapa A localiza cada ventana con
        un pico alto y ÚNICO, los desplazamientos son consistentes entre
        ventanas (un cuerpo rígido los explica con residuo de pocos píxeles), y
        el NCC a level 0 queda muy por encima del control de sitio equivocado.
      - SECCIONES SERIADAS del mismo bloque: la silueta registra bien (mismo
        bloque, misma disposición de fragmentos), pero el campo de
        desplazamiento NO es rígido (deformación elástica del montaje, decenas
        o cientos de µm) y a level 0 el NCC cae al nivel del control.
      - El control de sitio equivocado corre con los MISMOS grados de libertad
        que la señal (misma búsqueda de traslación y mismo barrido de rotación).
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
    mpp = float(p.get("openslide.mpp-x", 0) or 0)

    # --- 1. la silueta: ¿se parecen las dos regiones a escala de arquitectura? ---
    lvl = sl.get_best_level_for_downsample(args.downsample)
    ds = sl.level_downsamples[lvl]
    gw, gh = int(min(w0, w1) / ds), int(min(h0, h1) / ds)
    g0 = np.asarray(sl.read_region((x0, y0), lvl, (gw, gh)).convert("L"), dtype=np.float64)
    g1 = np.asarray(sl.read_region((x1, y1), lvl, (gw, gh)).convert("L"), dtype=np.float64)
    print(f"[silueta] level {lvl} (downsample {ds:.0f}), miniatura {gw}x{gh}")
    ncc0 = _ncc(g0, g1)
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
    a = g0[max(0, oy):gh + min(0, oy), max(0, ox):gw + min(0, ox)]
    b = g1[max(0, -oy):gh + min(0, -oy), max(0, -ox):gw + min(0, -ox)]
    ncc_esp = _ncc(a, b[:, ::-1])
    print(f"[silueta] NCC sin registrar {ncc0:.4f}, registrada {ncc_reg:.4f} "
          f"(dx={int(ox*ds)} dy={int(oy*ds)} px de level 0)")
    print(f"[silueta] control contra la región 1 espejada: {ncc_esp:.4f}")
    print(f"[silueta] OJO: esta medida la domina el CONTORNO del tejido, no las "
          f"células. Dos secciones seriadas del mismo bloque también la pasan.")

    # --- 2. ventanas de tejido REPARTIDAS por toda la región ---
    # repartirlas importa: si se toman las más densas a secas, los empates al
    # 100 % las amontonan todas en un fragmento y el campo de desplazamiento
    # queda medido en un solo punto del vidrio.
    LA, MA = args.plantilla_a, args.margen_a
    lado = max(1, int(LA / ds))
    tej = ((g0 > args.umbral_fondo) & (g0 < args.umbral_tejido)).astype(np.float64)
    integral = np.cumsum(np.cumsum(tej, 0), 1)

    def dens(y, x):
        y2, x2 = y + lado, x + lado
        return (integral[y2, x2] - integral[y, x2] - integral[y2, x] + integral[y, x])

    G = int(np.ceil(np.sqrt(args.ventanas * 2)))
    ventanas = []
    for gy in range(G):
        for gx in range(G):
            y_a, y_b = gy * gh // G, min((gy + 1) * gh // G, gh - lado - 1)
            x_a, x_b = gx * gw // G, min((gx + 1) * gw // G, gw - lado - 1)
            mej = None
            for y in range(y_a, y_b, max(1, lado // 2)):
                for x in range(x_a, x_b, max(1, lado // 2)):
                    d = dens(y, x) / (lado * lado)
                    if mej is None or d > mej[0]:
                        mej = (d, y, x)
            if mej and mej[0] >= args.min_tejido:
                ventanas.append(mej)
    ventanas.sort(reverse=True)
    ventanas = ventanas[:args.ventanas]

    # --- 3. etapa A: localizar cada ventana con margen ANCHO, a escala media ---
    lva = args.nivel_a
    dsa = sl.level_downsamples[lva]
    print(f"\n[etapa A] {len(ventanas)} ventanas de {LA} px ({LA*mpp:.0f} µm) "
          f"repartidas en grilla {G}x{G}; búsqueda ±{MA} px ({MA*mpp:.0f} µm) "
          f"a level {lva}")
    print(f"{'vent':>4} {'x0':>7} {'y0':>7} {'NCC':>8} {'dx':>7} {'dy':>7} "
          f"{'sd':>6} {'2do':>7}")
    filas = []
    for n, (d, cy, cx) in enumerate(ventanas):
        ax, ay = x0 + int(cx * ds), y0 + int(cy * ds)
        bx, by = x1 + (ax - x0), y1 + (ay - y0)
        if not (x1 + MA <= bx <= x1 + w1 - LA - MA and y1 + MA <= by <= y1 + h1 - LA - MA):
            continue
        r = _buscar_local(sl, (ax, ay), (bx, by), LA, MA, lva, dsa)
        if r is None:
            continue
        r["en_borde"] = bool(max(abs(r["dx_level0"]), abs(r["dy_level0"])) >= MA - dsa)
        filas.append({"n": n, "tejido": float(d), "region0": [ax, ay],
                      "prediccion": [bx, by], "etapa_a": r})
        print(f"{n:>4} {ax:>7} {ay:>7} {r['ncc']:>8.4f} {r['dx_level0']:>7} "
              f"{r['dy_level0']:>7} {r['sd_sobre_fondo']:>6.1f} {r['segundo_pico']:>7.4f}")
    if len(filas) < 3:
        print(f"[stop] solo {len(filas)} ventanas utilizables")
        sl.close()
        return

    # ¿un cuerpo rígido explica el campo? Es el discriminante de forma: dos
    # imágenes del MISMO vidrio se llevan una a otra con rotación + traslación;
    # dos secciones montadas por separado, no.
    buenas = [f_ for f_ in filas if not f_["etapa_a"]["en_borde"]]
    fit = None
    if len(buenas) >= 3:
        u = np.array([[f_["region0"][0] - x0 + LA / 2, f_["region0"][1] - y0 + LA / 2]
                      for f_ in buenas])
        v = np.array([[f_["prediccion"][0] + f_["etapa_a"]["dx_level0"] - x1 + LA / 2,
                       f_["prediccion"][1] + f_["etapa_a"]["dy_level0"] - y1 + LA / 2]
                      for f_ in buenas])
        fit = _ajuste_rigido(u, v)
        span = float(np.hypot(*(u.max(0) - u.min(0))))
        fit["span_px"] = span
        print(f"\n[rígido] ajuste con {len(buenas)} ventanas sobre "
              f"{span*mpp/1000:.1f} mm de vidrio: rotación {fit['theta_grados']:+.3f}°, "
              f"escala {fit['escala']:.5f}")
        print(f"[rígido] residuo: RMS {fit['rms_px']:.0f} px = {fit['rms_px']*mpp:.0f} µm, "
              f"máximo {fit['max_px']*mpp:.0f} µm")

    # --- 4. etapa B: level 0, el test decisivo, con control de igual libertad ---
    LB, MB = args.plantilla_b, args.margen_b
    Lo = LB + 2 * MB
    thetas = np.arange(-args.rot_max, args.rot_max + 1e-9, args.rot_paso)
    print(f"\n[etapa B] level 0, plantilla {LB} px ({LB*mpp:.0f} µm), residual "
          f"±{MB} px, rotación ±{args.rot_max}° en pasos de {args.rot_paso}°")
    print(f"{'vent':>4} {'NCC':>8} {'ctrl':>8} {'θ':>6} {'dx':>5} {'dy':>5} "
          f"{'sd':>6} {'2do':>7}")
    for i_, f_ in enumerate(filas):
        ax, ay = f_["region0"]
        cx0 = ax + (LA - LB) // 2
        cy0 = ay + (LA - LB) // 2
        tpl = np.asarray(sl.read_region((cx0, cy0), 0, (LB, LB)).convert("L"),
                         dtype=np.float64)
        ra = f_["etapa_a"]
        vc = (f_["prediccion"][0] + ra["dx_level0"] + (LA - LB) // 2 + LB / 2,
              f_["prediccion"][1] + ra["dy_level0"] + (LA - LB) // 2 + LB / 2)
        r = _mejor_con_rotacion(sl, tpl, vc, Lo, thetas)
        # control de SITIO EQUIVOCADO: la misma plantilla, misma maquinaria y
        # mismo barrido, en el destino localizado de OTRA ventana
        o = filas[(i_ + 1) % len(filas)]
        vco = (o["prediccion"][0] + o["etapa_a"]["dx_level0"] + (LA - LB) // 2 + LB / 2,
               o["prediccion"][1] + o["etapa_a"]["dy_level0"] + (LA - LB) // 2 + LB / 2)
        c = _mejor_con_rotacion(sl, tpl, vco, Lo, thetas)
        f_["etapa_b"] = r
        f_["control"] = c
        f_["centro_region1"] = [float(vc[0]), float(vc[1])]
        if r:
            print(f"{f_['n']:>4} {r['ncc']:>8.4f} "
                  f"{(c['ncc'] if c else float('nan')):>8.4f} {r['theta']:>+6.2f} "
                  f"{r['ix']-MB:>5} {r['iy']-MB:>5} {r['sd_sobre_fondo']:>6.1f} "
                  f"{r['segundo_pico']:>7.4f}")

    n0 = np.array([f_["etapa_b"]["ncc"] for f_ in filas if f_.get("etapa_b")])
    nc = np.array([f_["control"]["ncc"] for f_ in filas if f_.get("control")])
    print(f"\n[resumen] NCC a level 0, señal  : medio {n0.mean():.4f}, mediana "
          f"{np.median(n0):.4f}, rango {n0.min():.4f}..{n0.max():.4f}")
    print(f"[resumen] NCC a level 0, control: medio {nc.mean():.4f}, mediana "
          f"{np.median(nc):.4f}, máximo {nc.max():.4f}")
    sep = (n0.mean() - nc.mean()) / (nc.std() + 1e-12)
    print(f"[resumen] separación señal-control: {sep:.1f} sd del control; "
          f"ventanas con señal > máximo del control: "
          f"{int((n0 > nc.max()).sum())}/{len(n0)}")

    # --- 5. la mejor ventana, lado a lado, para mirarla ---
    mejor_f = max((f_ for f_ in filas if f_.get("etapa_b")),
                  key=lambda f_: f_["etapa_b"]["ncc"])
    ax, ay = mejor_f["region0"]
    cx0, cy0 = ax + (LA - LB) // 2, ay + (LA - LB) // 2
    rb = mejor_f["etapa_b"]
    c0 = sl.read_region((cx0, cy0), 0, (LB, LB)).convert("RGB")
    ali = _recorte_alineado(sl, mejor_f["centro_region1"], Lo, rb["theta"], 1.0)
    rec = ali[rb["iy"]:rb["iy"] + LB, rb["ix"]:rb["ix"] + LB]
    c1 = Image.fromarray(rec.astype(np.uint8)).convert("RGB")
    par = Image.new("RGB", (LB * 2 + 16, LB), "white")
    par.paste(c0.convert("L").convert("RGB"), (0, 0))
    par.paste(c1, (LB + 16, 0))
    out = OUT_DIR / f"{sid}_registro_level0.png"
    par.save(out)
    print(f"\n[out] {out}  (izq = región 0 en ({cx0},{cy0}), der = lo mejor que "
          f"se encontró en la región 1, NCC {rb['ncc']:.4f})")

    res = {
        "slide_id": sid, "regiones": regs, "mpp": mpp,
        "silueta": {"level": lvl, "downsample": ds, "ncc_sin_registrar": ncc0,
                    "ncc_registrada": ncc_reg, "ncc_control_espejo": ncc_esp,
                    "dx_level0": int(ox * ds), "dy_level0": int(oy * ds)},
        "etapa_a": {"nivel": lva, "plantilla": LA, "margen": MA,
                    "n_ventanas": len(filas)},
        "ajuste_rigido": fit,
        "etapa_b": {
            "plantilla": LB, "margen": MB,
            "rotaciones": [float(t) for t in thetas],
            "ncc_medio": float(n0.mean()), "ncc_mediana": float(np.median(n0)),
            "ncc_min": float(n0.min()), "ncc_max": float(n0.max()),
            "control_medio": float(nc.mean()), "control_max": float(nc.max()),
            "separacion_sd": float(sep),
            "ventanas_sobre_control": int((n0 > nc.max()).sum()),
        },
        "ventanas": filas,
    }
    (OUT_DIR / f"registro_{sid}.json").write_text(json.dumps(res, indent=2))
    print(f"[out] {OUT_DIR / f'registro_{sid}.json'}")
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
    r.add_argument("--ventanas", type=int, default=8)
    r.add_argument("--min-tejido", type=float, default=0.5,
                   help="fracción mínima de tejido para aceptar una ventana")
    # etapa A: localizar cada ventana con margen ancho, a escala media
    r.add_argument("--nivel-a", type=int, default=2)
    r.add_argument("--plantilla-a", type=int, default=1024,
                   help="lado de la plantilla de la etapa A, px de level 0")
    r.add_argument("--margen-a", type=int, default=2048,
                   help="radio de búsqueda de la etapa A, px de level 0")
    # etapa B: el test decisivo, a level 0
    r.add_argument("--plantilla-b", type=int, default=512)
    r.add_argument("--margen-b", type=int, default=48)
    r.add_argument("--rot-max", type=float, default=1.5,
                   help="barrido de rotación de la etapa B, en grados")
    r.add_argument("--rot-paso", type=float, default=0.5)
    r.add_argument("--umbral-tejido", type=float, default=210.0)
    r.add_argument("--umbral-fondo", type=float, default=40.0)
    r.add_argument("--rango-grueso", type=int, default=24)
    r.set_defaults(func=registro)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    sys.exit(main())
