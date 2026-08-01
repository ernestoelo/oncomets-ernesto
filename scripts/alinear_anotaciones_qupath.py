#!/usr/bin/env python
"""Alinea un geojson de anotaciones de QuPath con los parches que CLAM ya extrajo.

Contexto (B8, 31-jul-2026). El patologo anota regiones en QuPath sobre la WSI y exporta
un geojson. Nuestros parches viven en `environ/features/h5_files/<slide>.h5` con coords en
el sistema de openslide. Para la lamina 129741 (Ventana `.bif`, dos regiones de escaneo) los
dos sistemas NO coinciden: hace falta una traslacion. Este script la estima y deja el mapeo
parche -> clase anotada.

La traslacion se estima por tres criterios, los dos primeros independientes entre si:
  (a) que el centroide de la anotacion caiga sobre un parche extraido,
  (b) que caiga sobre tejido, con una mascara de saturacion sobre una miniatura, y
  (c) refinamiento por AREA de poligono: los poligonos de tejido maximizan su fraccion de
      tejido y los de fondo (`Negative`) la minimizan, sobre una miniatura mas fina.
(a) y (b) prueban que el desplazamiento existe y no es un artefacto de la segmentacion;
(c) es el que lo deja con precision util, porque (a) y (b) miran un punto y no un area.

Como control geometrico se reporta ademas el offset que predice el propio contenedor: en un
Ventana `.bif` con varias regiones de escaneo, openslide arma un canvas mas ancho que la
region, y la diferencia `level0.width - region[0].width` es candidata natural al `dx`.

AVISO sobre las etiquetas que produce: el patologo marca **solo** donde la evidencia es
clara, no todo lo que existe. Un parche sin anotacion NO es un negativo. La salida sirve
como positivos y como zona de contraste, nunca como verdad de campo exhaustiva.

Todo es CPU y read-only sobre lo ajeno; solo escribe bajo el repo personal.

Uso:
    python scripts/alinear_anotaciones_qupath.py \
        --geojson "/media/.../hover_net/129741.bif - GDT.geojson" \
        --slide_id 129741 \
        --wsi "/media/.../wsi/129741/129741.bif" \
        --out sprints/B8_sprint8/anotaciones_patologo/
"""
import argparse
import collections
import json
import os

import h5py
import numpy as np

H5_DIR = "/media/administrador/Storage1/sdonoso/clam_environ/environ/features/h5_files"


def cargar_anotaciones(path):
    """Devuelve [(clase, poligono Nx2 en px de level0), ...] del geojson de QuPath."""
    data = json.load(open(path))
    feats = data["features"] if isinstance(data, dict) else data
    out = []
    for ft in feats:
        cl = ft.get("properties", {}).get("classification", {})
        name = cl.get("name") if isinstance(cl, dict) else str(cl)
        geom = ft["geometry"]
        anillos = geom["coordinates"] if geom["type"] == "Polygon" else [c[0] for c in geom["coordinates"]]
        out.append((name, np.asarray(anillos[0], dtype=float)))
    return out


def patch_size_desde_coords(coords):
    """Moda del paso entre coords consecutivas (memoria patch-size-desde-geometria-h5)."""
    pasos = np.concatenate([np.diff(np.unique(coords[:, 0])), np.diff(np.unique(coords[:, 1]))])
    return int(collections.Counter(pasos.tolist()).most_common(1)[0][0])


def mascara_tejido(wsi_path, objetivo_ds=32):
    """Mascara booleana de tejido sobre una miniatura, y su downsample."""
    import openslide

    sl = openslide.OpenSlide(wsi_path)
    lvl = min(range(sl.level_count), key=lambda i: abs(sl.level_downsamples[i] - objetivo_ds))
    ds = sl.level_downsamples[lvl]
    img = np.array(sl.read_region((0, 0), lvl, sl.level_dimensions[lvl]).convert("RGB"))
    gris = img.mean(2)
    mx, mn = img.max(2).astype(float), img.min(2).astype(float)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1), 0)
    props = dict(sl.properties)
    return (sat > 0.10) & (gris < 225) & (gris > 20), ds, props


def refinar_por_area(anot, wsi_path, dx0, dy0, margen=700, paso=16, objetivo_ds=8,
                     fondo=("Negative",), neutro=("Tejido Adiposo",)):
    """Criterio (c): maximiza tejido dentro de los poligonos de tejido y lo minimiza en los de fondo.

    Devuelve (mejor_dx, mejor_dy, score, funcion_score). Rasteriza cada poligono UNA vez en su
    bbox y despues solo desplaza la ventana de muestreo, asi el barrido es barato.
    """
    import openslide
    from PIL import Image, ImageDraw

    sl = openslide.OpenSlide(wsi_path)
    lvl = min(range(sl.level_count), key=lambda i: abs(sl.level_downsamples[i] - objetivo_ds))
    ds = sl.level_downsamples[lvl]
    W, H = sl.level_dimensions[lvl]
    img = np.array(sl.read_region((0, 0), lvl, (W, H)).convert("RGB"))
    gris = img.mean(2)
    mx, mn = img.max(2).astype(float), img.min(2).astype(float)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1), 0)
    tej = (sat > 0.10) & (gris < 225) & (gris > 20)

    items = []
    for clase, poly in anot:
        if clase in neutro:      # el adiposo es tejido para el patologo pero no para una
            continue             # mascara de saturacion; no puede opinar del objetivo
        q = poly / ds
        x0, y0 = np.floor(q.min(0)).astype(int)
        x1, y1 = np.ceil(q.max(0)).astype(int)
        w, h = max(1, int(x1 - x0)), max(1, int(y1 - y0))
        m = Image.new("1", (w, h), 0)
        ImageDraw.Draw(m).polygon([tuple(v) for v in (q - [x0, y0])], fill=1)
        m = np.array(m, bool)
        if m.sum() < 1:                       # poligono sub-pixel a este nivel
            m = np.ones((h, w), bool)
        items.append((clase in fondo, int(x0), int(y0), w, h, m, int(m.sum())))

    def score(dx, dy):
        sx, sy = dx / ds, dy / ds
        s = 0.0
        for es_fondo, x0, y0, w, h, m, area in items:
            X, Y = int(round(x0 + sx)), int(round(y0 + sy))
            if X < 0 or Y < 0 or X + w > W or Y + h > H:
                return -9e9
            frac = float((tej[Y:Y + h, X:X + w] & m).sum()) / area
            s += -frac if es_fondo else frac
        return s

    def barrer(cx, cy, m, p, mejor):
        for dx in range(cx - m, cx + m + 1, p):
            for dy in range(cy - m, cy + m + 1, p):
                v = score(dx, dy)
                if v > mejor[0]:
                    mejor = (v, dx, dy)
        return mejor

    mejor = barrer(dx0, dy0, margen, paso * 4, (-9e9, dx0, dy0))   # gruesa y ancha
    mejor = barrer(mejor[1], mejor[2], paso * 6, paso, mejor)      # fina donde gano
    return mejor[1], mejor[2], mejor[0], score


def buscar_traslacion(centroides, acierta, rango, paso):
    """Barre (dx, dy) y devuelve el mejor conteo y el plateau que lo alcanza."""
    mejor, plateau = -1, []
    for dx in range(-rango, rango + 1, paso):
        for dy in range(-rango, rango + 1, paso):
            n = acierta(centroides + np.array([dx, dy]))
            if n > mejor:
                mejor, plateau = n, [(dx, dy)]
            elif n == mejor:
                plateau.append((dx, dy))
    return mejor, np.asarray(plateau)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--geojson", required=True)
    ap.add_argument("--slide_id", required=True)
    ap.add_argument("--wsi", default=None, help="si se da, valida el offset contra tejido real")
    ap.add_argument("--h5_dir", default=H5_DIR)
    ap.add_argument("--out", default=None, help="directorio donde escribir el CSV parche->clase")
    ap.add_argument("--rango", type=int, default=9000)
    ap.add_argument("--paso", type=int, default=64)
    ap.add_argument("--margen", type=int, default=1400, help="ventana del refinamiento (c)")
    ap.add_argument("--tol_geo", type=float, default=0.005,
                    help="si el offset geometrico queda a menos de esta fraccion del optimo, se adopta el geometrico")
    args = ap.parse_args()

    anot = cargar_anotaciones(args.geojson)
    centro = np.array([p.mean(0) for _, p in anot])
    clases = [c for c, _ in anot]
    with h5py.File(os.path.join(args.h5_dir, f"{args.slide_id}.h5"), "r") as f:
        coords = f["coords"][:].astype(int)
    ps = patch_size_desde_coords(coords)

    print(f"lamina {args.slide_id}: {len(coords)} parches de {ps} px, {len(anot)} anotaciones")
    inv = collections.Counter(clases)
    print("\ninventario de anotaciones:")
    for k, v in inv.most_common():
        areas = np.array([0.5 * abs(np.dot(p[:, 0], np.roll(p[:, 1], 1)) - np.dot(p[:, 1], np.roll(p[:, 0], 1)))
                          for c, p in anot if c == k])
        print(f"  {k:22s} n={v:3d}  area mediana {np.median(areas):10.0f} px2 = "
              f"{100 * np.median(areas) / (ps * ps):6.2f} % de un parche de {ps} px")

    celdas = set(map(tuple, (coords // ps).tolist()))

    def acierta_parche(pts):
        q = (pts // ps).astype(int)
        return sum(1 for a, b in q.tolist() if (a, b) in celdas)

    n0 = acierta_parche(centro)
    print(f"\ncriterio (a) parche extraido, SIN traslacion: {n0}/{len(anot)}")
    mejor_a, plat_a = buscar_traslacion(centro, acierta_parche, args.rango, args.paso)
    print(f"criterio (a) mejor: {mejor_a}/{len(anot)}  plateau dx [{plat_a[:,0].min()}, {plat_a[:,0].max()}]"
          f"  dy [{plat_a[:,1].min()}, {plat_a[:,1].max()}]")

    plat_b = None
    if args.wsi:
        tej, ds, props = mascara_tejido(args.wsi)
        print(f"\nWSI: mpp={props.get('openslide.mpp-x')} mag={props.get('openslide.objective-power')} "
              f"vendor={props.get('openslide.vendor')}; tejido {tej.mean():.3f} de la miniatura")
        for k in sorted(props):
            if k.startswith("openslide.region"):
                print(f"   {k} = {props[k]}")

        def acierta_tejido(pts):
            q = (pts / ds).astype(int)
            return sum(1 for x, y in q.tolist()
                       if 0 <= y < tej.shape[0] and 0 <= x < tej.shape[1] and tej[y, x])

        print(f"\ncriterio (b) tejido, SIN traslacion: {acierta_tejido(centro)}/{len(anot)}")
        mejor_b, plat_b = buscar_traslacion(centro, acierta_tejido, args.rango, args.paso)
        print(f"criterio (b) mejor: {mejor_b}/{len(anot)}  plateau dx [{plat_b[:,0].min()}, {plat_b[:,0].max()}]"
              f"  dy [{plat_b[:,1].min()}, {plat_b[:,1].max()}]")

    if plat_b is not None:
        sa, sb = set(map(tuple, plat_a.tolist())), set(map(tuple, plat_b.tolist()))
        inter = np.asarray(sorted(sa & sb))
        if len(inter):
            DX, DY = int(round(inter[:, 0].mean())), int(round(inter[:, 1].mean()))
            print(f"\nINTERSECCION de los dos plateaus: {len(inter)} offsets, "
                  f"dx [{inter[:,0].min()}, {inter[:,0].max()}] dy [{inter[:,1].min()}, {inter[:,1].max()}]"
                  f"  -> punto de partida dx={DX} dy={DY}")
        else:
            DX, DY = int(plat_a[:, 0].mean()), int(plat_a[:, 1].mean())
            print("\nlos plateaus NO se cruzan: el desplazamiento no queda establecido, revisar a mano")
    else:
        DX, DY = int(plat_a[:, 0].mean()), int(plat_a[:, 1].mean())

    adoptado = "interseccion de centroides"
    if args.wsi:
        DX, DY, sc, fscore = refinar_por_area(anot, args.wsi, DX, DY, margen=args.margen)
        adoptado = "criterio (c), optimo empirico por area"
        print(f"\ncriterio (c) refinamiento por area: dx={DX} dy={DY}  score={sc:.3f}")
        print(f"   control, sin traslacion:            score={fscore(0, 0):.3f}")
        w0 = props.get("openslide.region[0].width")
        sl_w = props.get("openslide.level[0].width")
        if w0 is not None and sl_w is not None:
            geo = int(sl_w) - int(w0)
            sgeo = fscore(geo, 0)
            print(f"   control geometrico del contenedor: dx = level0.width - region[0].width = "
                  f"{sl_w} - {w0} = {geo}, dy = 0  ->  score={sgeo:.3f}")
            print(f"   distancia entre el optimo empirico y el geometrico: {abs(DX - geo)} px en x, "
                  f"{abs(DY)} px en y")
            # el objetivo es plano a escala de cientos de px (el tejido es una estructura grande):
            # si el dato no separa los dos candidatos, gana el que tiene explicacion independiente
            if sgeo >= sc - args.tol_geo * abs(sc):
                DX, DY = geo, 0
                adoptado = "geometria del contenedor (el area no separa los candidatos)"
                print(f"   -> el dato no los separa (tolerancia {args.tol_geo:.1%}); se adopta el geometrico")
    print(f"\noffset adoptado: dx={DX} dy={DY}  [{adoptado}]")

    # mapeo parche -> clases, con el offset adoptado
    filas, tocados = [], collections.defaultdict(set)
    for (clase, poly) in anot:
        p = poly + np.array([DX, DY])
        x0, y0 = p.min(0)
        x1, y1 = p.max(0)
        for cx, cy in coords.tolist():
            if cx < x1 and cx + ps > x0 and cy < y1 and cy + ps > y0:
                tocados[(cx, cy)].add(clase)
    for (cx, cy), cs in sorted(tocados.items()):
        filas.append((args.slide_id, cx, cy, ps, "|".join(sorted(cs))))

    print(f"\ncon dx={DX} dy={DY}: {len(filas)} parches distintos quedan bajo alguna anotacion "
          f"({100*len(filas)/len(coords):.2f} % de la lamina)")
    porclase = collections.Counter()
    for _, _, _, _, cs in filas:
        for c in cs.split("|"):
            porclase[c] += 1
    for k, v in porclase.most_common():
        print(f"   {k:22s} {v:4d} parches")

    if args.out:
        os.makedirs(args.out, exist_ok=True)
        dest = os.path.join(args.out, f"parches_anotados_{args.slide_id}.csv")
        with open(dest, "w") as fh:
            fh.write("slide_id,x,y,patch_size,clases\n")
            for r in filas:
                fh.write(",".join(map(str, r)) + "\n")
        meta = os.path.join(args.out, f"offset_{args.slide_id}.json")
        json.dump({"slide_id": args.slide_id, "dx": DX, "dy": DY, "patch_size": ps,
                   "offset_adoptado_por": adoptado,
                   "n_parches": int(len(coords)), "n_anotaciones": len(anot),
                   "criterio_a_mejor": int(mejor_a),
                   "criterio_b_mejor": int(mejor_b) if plat_b is not None else None,
                   "parches_bajo_anotacion": len(filas),
                   "parches_por_clase": dict(porclase),
                   "aviso": "un parche sin anotacion NO es un negativo: el patologo marca solo la evidencia clara",
                   "geojson": args.geojson}, open(meta, "w"), indent=2)
        print(f"\nescrito: {dest}\n         {meta}")
        print("RECORDATORIO: un parche sin anotacion NO es un negativo.")


if __name__ == "__main__":
    main()
