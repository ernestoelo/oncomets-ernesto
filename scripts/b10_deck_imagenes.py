#!/usr/bin/env python
"""b10_deck_imagenes.py — las imágenes de las cuatro láminas nuevas del deck del 15-sep.

Plan: `sprints/B10_sprint10/presentacion_b10/plan_deck_visual.md`, paso 1.b. NO MIDE NADA: lee
lo que eligió `scripts/b10_deck_seleccion.py` (paso 1.a, env `pruebas`, que tiene zarr y no abre
los `.bif`) y lo dibuja sobre el tejido. Este env (`clam_latest`) abre los `.bif` y no tiene zarr
(workaround K.a), por eso son dos scripts.

Un PNG POR PANEL, sin un solo carácter quemado. Cada panel tiene su registro en
`deck_imagenes.json`, en el orden en que la lámina lo dibuja (`orden_dibujo`), y el deck rotula
desde ese mismo registro: el nombre del archivo y el rótulo salen de la misma fila, así que no
pueden cruzarse ([[sidecar-orden-no-es-el-de-la-figura]]) y ningún rótulo queda bajo 7 pt al
escalar ([[png-rotulos-quemados-pierden-pt]]).

  s03 · qué detecta HoVer-NeXt. La ventana de contexto de 1076 px con cada núcleo pintado por
  clase, y su centro de 256 px (un parche de CLAM) ampliado con los contornos. Tres clases con
  color y las otras cuatro plegadas en «otras», en gris, que absorben la única instancia de
  clase mitosis del recorte: la imagen no dice «mitosis», que es la línea de otra persona.

  s05 · O1 sobre una lámina. Por lámina, la miniatura del tejido con los parches de la carga
  de N = 500, y un zoom sobre las marcas. El zoom es un cuadrado alineado a la grilla de
  `carga_mm2` que contiene todas las marcas con al menos un parche de margen por lado (lado =
  extensión de las marcas más tres parches, redondeado a la grilla); su lado es el mayor de los
  dos, para que los dos zooms tengan la misma escala.

  s06 · O1 núcleo a núcleo. Los doce paneles de la selección, cada uno con el núcleo bajo la
  marca en contorno grueso (borde más aureola por fuera) y los demás del top 500 que caen en la
  ventana en contorno fino.

  s09 · O3 dónde mira la atención. Tres láminas por regla, sobre `auc_cdis.csv`: la de `train`
  con AUC más alto en la rama verdadera, la de `test` y la que está fuera del split (rama `si`,
  la única que tiene, confinada a su región anotada). Rampa del B9 (turbo por percentil, la del
  mosaico de atención que ya vio la audiencia), y el percentil se calcula dentro del universo
  medido: es el mismo conjunto del AUC que se rotula. Por lámina, dos PNG:
    - el mapa, recortado al tejido del universo, que hace de localizador del zoom;
    - un zoom de `LADO_ZOOM_CDIS` parches centrado en el polígono de CDIS con más parches
      positivos (empate: el primero del geojson), con la atención parche a parche y los
      polígonos con su offset. Los polígonos miden 0,2 a 0,5 mm y a escala de lámina no se ven.

Paleta de s03, s05 y s06. Validada el 16-sep-2026 con el gemelo en Python del validador de la
skill `dataviz` (`validate_palette.py "#1baf7a,#eda100,#2a78d6" --mode light --surface "#e6c3d8"
--pairs all`): PASS en banda de luminosidad, croma, CVD (peor par 9,1, protan) y visión normal
(peor par 22,9); WARN de contraste contra el tejido, que obliga a leyenda visible y va nativa,
con los conteos. El gris de «otras» no es un tono categórico (es el pliegue) y se eligió para
quedar lejos de los tres: ΔE 20,6 en visión normal y 20,1 bajo CVD. El verde es epitelial en las
tres láminas, así que los parches de la carga y los núcleos del top 500 van en verde también.
No es la paleta de HoVer-NeXt, que con los pesos de Lizard pinta el epitelial en rojo.

Gates que abortan antes de escribir:
  1. s03 y s06: cada ventana `.npz` tiene el origen y el lado que dice `seleccion.json`, y el
     núcleo marcado de cada panel de s06 está en su ventana.
  2. s05: parches × área del parche = carga publicada, y cada marca cae dentro del zoom.
  3. s09: el AUC recalculado con los mismos scores que se dibujan reproduce `auc_cdis.csv`
     (universo lámina) o `auc_cdis_region.csv` (universo región) con tolerancia 1e-9, y la rama
     de la B25-158899 es `si`. Publicado: 0,929 · 0,704 · 0,201.

  CUDA_VISIBLE_DEVICES="" /home/sdonoso/miniconda3/envs/clam_latest/bin/python \\
      scripts/b10_deck_imagenes.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw

REPO = Path("/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto")
for p in (REPO, REPO / "scripts"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from scripts.mammoth_interpretability import (                       # noqa: E402
    blend, build_overlay_rgba, get_wsi_thumbnail, percentile_scores)
from scripts.atencion_vs_anotaciones import rank_auc, ranks_of        # noqa: E402
from scripts.b9_atencion_12_laminas import (                          # noqa: E402
    leer_h5, paso_de_grilla, universos_de)
from scripts.b10_cdis_atencion import (                               # noqa: E402
    CDIS, OFFSETS, atencion_ckpt, etiquetas, parches_cdis)
from b9_descriptores_nucleos import MPP, geojson_de                   # noqa: E402

WSI_DIR = Path("/media/administrador/Storage1/sdonoso/wsi")
SEL_DIR = REPO / "results" / "b10_deck_imagenes"
CDIS_DIR = REPO / "results" / "b10_cdis"
OUT = REPO / "sprints" / "B10_sprint10" / "presentacion_b10" / "assets"

EPITELIAL, LINFOCITO, CONECTIVO = 2, 3, 6
GRUPOS = [("epitelial", (EPITELIAL,), "#1baf7a"),
          ("linfocito", (LINFOCITO,), "#eda100"),
          ("conectivo", (CONECTIVO,), "#2a78d6"),
          ("otras", (1, 4, 5, 7), "#555555")]
VERDE = GRUPOS[0][2]
TINTA = (0x1A, 0x1A, 0x2E)
BLANCO = (255, 255, 255)

AMPLIA_CENTRO = 4            # 256 px -> 1024
AMPLIA_GALERIA = 4           # 160 px -> 640
LADO_ZOOM_PX = 1024          # salida de los zooms de s05 y s09
LADO_ZOOM_CDIS = 16          # parches por lado del zoom de s09: 4096 px = 1,9 mm
MAX_LADO_MINI = 1200         # salida de las miniaturas de s05 y s09: ~375 dpi a 3,2"


def _rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _osr(slide):
    import openslide
    return openslide.OpenSlide(str(WSI_DIR / slide / f"{slide}.bif"))


def tejido(osr, x0, y0, lado):
    """`read_region` a level 0. El origen ya viene clampado de la selección."""
    return osr.read_region((int(x0), int(y0)), 0, (int(lado), int(lado))).convert("RGB")


def borde(ids, t):
    """Borde interior de cada instancia, de `t` píxeles: el píxel cuyo id difiere de algún
    vecino a distancia de Chebyshev <= t. Sin skimage (el env no lo necesita para esto). El
    padding por borde hace que un núcleo cortado por la ventana no tenga contorno sobre el
    corte."""
    H, W = ids.shape
    pad = np.pad(ids, t, mode="edge")
    b = np.zeros((H, W), dtype=bool)
    for dy in range(-t, t + 1):
        for dx in range(-t, t + 1):
            if dx or dy:
                b |= pad[t + dy:t + dy + H, t + dx:t + dx + W] != ids
    return b & (ids > 0)


def aureola(ids, t):
    """Los píxeles FUERA de una máscara a distancia de Chebyshev <= t: un anillo que rodea el
    núcleo sin taparle el interior."""
    m = ids > 0
    H, W = m.shape
    pad = np.pad(m, t)
    d = np.zeros((H, W), dtype=bool)
    for dy in range(-t, t + 1):
        for dx in range(-t, t + 1):
            d |= pad[t + dy:t + dy + H, t + dx:t + dx + W]
    return d & ~m


def ampliar(a, k):
    return np.repeat(np.repeat(a, k, axis=0), k, axis=1)


def pintar(rgb, mascara, color, alpha=1.0):
    c = np.asarray(_rgb(color), dtype=np.float32)
    rgb[mascara] = (1.0 - alpha) * rgb[mascara] + alpha * c
    return rgb


def anillo(d, u, v, r, relleno=None, ancho=4):
    """Símbolo de marca: tinta por fuera y blanco por dentro, que se ve sobre tejido y sobre
    color. `relleno` tinta = recuperada; blanco = no recuperada."""
    d.ellipse([u - r - ancho, v - r - ancho, u + r + ancho, v + r + ancho], fill=TINTA)
    d.ellipse([u - r, v - r, u + r, v + r], fill=BLANCO)
    if relleno is not None:
        q = r - ancho
        d.ellipse([u - q, v - q, u + q, v + q], fill=relleno)


def guardar(im, nombre):
    """Sin perfil ICC. `read_region` le cuelga a la imagen el del `.bif` (1,8 MB) y `resize`
    lo arrastra: sólo lo traían los dos zooms de s05, que se habrían visto con manejo de color
    en los visores que lo aplican y el resto no. Todos los assets, como los del B9, van en el
    RGB crudo de la lámina."""
    OUT.mkdir(parents=True, exist_ok=True)
    im.info.pop("icc_profile", None)
    im.save(OUT / nombre, optimize=True)
    return nombre


# --------------------------------------------------------------------------------------
# s03

def ventana(nombre, esperado):
    v = np.load(SEL_DIR / f"ventana_{nombre}.npz")
    x0, y0, pinst = int(v["x0"]), int(v["y0"]), v["pinst"]
    if (x0, y0, pinst.shape[0]) != (esperado["x0"], esperado["y0"], esperado["lado_px"]):
        sys.exit(f"gate 1: la ventana {nombre} no es la de seleccion.json")
    return v, x0, y0, pinst


def cuenta_por_grupo(ids, clase_de):
    out = {g: 0 for g, _, _ in GRUPOS}
    for i in ids:
        for g, clases, _ in GRUPOS:
            if clase_de[int(i)] in clases:
                out[g] += 1
    return out


def render_s03(sel):
    s = sel["s03"]
    v, x0, y0, pinst = ventana("s03", s)
    clase_de = dict(zip(v["ids"].tolist(), v["clases"].tolist()))
    lado, lc = s["lado_px"], s["lado_centro_px"]
    osr = _osr(s["slide"])
    mpp = sel["mpp"]

    # contexto: el núcleo entero pintado, porque a esta escala un contorno de un píxel se lee
    # como 0,2 pt; contorno de un píxel encima, del mismo color
    rgb = np.asarray(tejido(osr, x0, y0, lado), dtype=np.float32)
    lut = np.zeros(int(pinst.max()) + 1, dtype=np.int8) - 1
    for i, c in clase_de.items():
        lut[i] = c
    cls = np.where(pinst > 0, lut[pinst], -1)
    b1 = borde(pinst, 1)
    for _g, clases, col in GRUPOS:
        m = np.isin(cls, clases)
        pintar(rgb, m & ~b1, col, 0.45)
        pintar(rgb, m & b1, col, 1.0)
    ctx = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8))

    # el centro: el parche de 256 px centrado en la marca, recuadrado en el contexto
    mx, my = s["marca"]["x"], s["marca"]["y"]
    cx0, cy0 = int(round(mx - lc / 2.0)) - x0, int(round(my - lc / 2.0)) - y0
    if not (0 <= cx0 and 0 <= cy0 and cx0 + lc <= lado and cy0 + lc <= lado):
        sys.exit("s03: el centro no entra en la ventana de contexto")
    d = ImageDraw.Draw(ctx)
    for off, col, w in ((0, TINTA, 5), (5, BLANCO, 2)):
        d.rectangle([cx0 - 5 + off, cy0 - 5 + off, cx0 + lc + 4 - off, cy0 + lc + 4 - off],
                    outline=col, width=w)
    n_ctx = guardar(ctx, "s03_contexto.png")

    k = AMPLIA_CENTRO
    sub = pinst[cy0:cy0 + lc, cx0:cx0 + lc]
    rgb = np.asarray(tejido(osr, x0 + cx0, y0 + cy0, lc).resize((lc * k, lc * k), Image.LANCZOS),
                     dtype=np.float32)
    ids_k = ampliar(sub, k)
    cls_k = np.where(ids_k > 0, lut[ids_k], -1)
    bk = borde(ids_k, 3)
    for _g, clases, col in GRUPOS:
        pintar(rgb, np.isin(cls_k, clases) & bk, col, 1.0)
    cen = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8))
    anillo(ImageDraw.Draw(cen), (mx - x0 - cx0) * k, (my - y0 - cy0) * k, 14, relleno=TINTA,
           ancho=5)
    n_cen = guardar(cen, "s03_centro.png")

    pres_ctx = np.unique(pinst); pres_ctx = pres_ctx[pres_ctx > 0]
    pres_cen = np.unique(sub); pres_cen = pres_cen[pres_cen > 0]
    osr.close()
    reg = dict(slide=s["slide"], marca=s["marca"], grupos=[
        dict(grupo=g, clases=[sel["clases"][str(c)] for c in cl], color=col)
        for g, cl, col in GRUPOS],
        orden_dibujo=[
            dict(png=n_ctx, que="contexto", lado_px=lado, lado_um=lado * mpp,
                 n_nucleos=int(len(pres_ctx)), por_grupo=cuenta_por_grupo(pres_ctx, clase_de),
                 recuadro_centro_px=[cx0, cy0, lc],
                 recuadro_px=[cx0 - 5, cy0 - 5, cx0 + lc + 5, cy0 + lc + 5]),
            dict(png=n_cen, que="centro", lado_px=lc, lado_um=lc * mpp, ampliacion=k,
                 n_nucleos=int(len(pres_cen)), por_grupo=cuenta_por_grupo(pres_cen, clase_de))],
        conteo="núcleos con al menos un píxel dentro de la ventana")
    for p in reg["orden_dibujo"]:
        print(f"  s03 {p['que']:<9} {p['lado_px']:>5} px = {p['lado_um']:6.1f} µm  "
              f"{p['n_nucleos']:>5} núcleos  {p['por_grupo']}")
    return reg


# --------------------------------------------------------------------------------------
# s05

def recorte_tejido(coords, step, scale, tw, th):
    """El bounding box de las coords con dos parches de margen, como el mosaico del B9."""
    m = int(round(step * scale * 2))
    x0 = max(0, int(coords[:, 0].min() * scale) - m)
    y0 = max(0, int(coords[:, 1].min() * scale) - m)
    x1 = min(tw, int((coords[:, 0].max() + step) * scale) + m)
    y1 = min(th, int((coords[:, 1].max() + step) * scale) + m)
    return x0, y0, x1, y1


def achicar(im, max_lado):
    e = min(1.0, max_lado / float(max(im.size)))
    if e < 1.0:
        im = im.resize((max(1, int(round(im.width * e))), max(1, int(round(im.height * e)))),
                       Image.LANCZOS)
    return im, e


def render_s05(sel):
    lp, area = sel["lado_parche_px"], sel["area_parche_mm2"]
    # zoom: cuadrado alineado a la grilla, un parche de margen por lado; el lado común es el
    # mayor de los dos para que los zooms compartan escala. Se suma un tercer parche: redondear
    # el origen a la grilla corre la ventana hasta medio parche, y sin esa holgura el margen de
    # un lado puede quedar en medio parche (el gate lo cazó en la 129741)
    extents = []
    for p in sel["s05"]:
        mxy = np.asarray([[m["x"], m["y"]] for m in p["marcas"]])
        extents.append(float((mxy.max(0) - mxy.min(0)).max()))
    Z = lp * int(np.ceil((max(extents) + 3 * lp) / lp))

    regs = []
    for p in sel["s05"]:
        slide = p["slide"]
        if len(p["parches"]) != p["n_parches"] or \
                abs(p["n_parches"] * area - p["carga_mm2"]) > 1e-9:
            sys.exit(f"gate 2: {slide} parches × área no da la carga")
        _f, coords = leer_h5(slide)
        step = paso_de_grilla(coords)
        thumb, scale, _mag, _w0, _h0 = get_wsi_thumbnail(WSI_DIR / slide / f"{slide}.bif")
        th, tw = thumb.shape[:2]
        tx0, ty0, tx1, ty1 = recorte_tejido(coords, step, scale, tw, th)
        mini = Image.fromarray(thumb).crop((tx0, ty0, tx1, ty1))
        mini, e = achicar(mini, MAX_LADO_MINI)
        k = scale * e

        mxy = np.asarray([[m["x"], m["y"]] for m in p["marcas"]])
        c = (mxy.max(0) + mxy.min(0)) / 2.0
        zx0 = lp * int(np.floor((c[0] - Z / 2.0) / lp + 0.5))
        zy0 = lp * int(np.floor((c[1] - Z / 2.0) / lp + 0.5))
        if not ((mxy[:, 0] >= zx0 + lp).all() and (mxy[:, 0] < zx0 + Z - lp).all()
                and (mxy[:, 1] >= zy0 + lp).all() and (mxy[:, 1] < zy0 + Z - lp).all()):
            sys.exit(f"gate 2: {slide} tiene marcas fuera del zoom con su margen")

        capa = Image.new("RGBA", mini.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(capa)
        verde = _rgb(VERDE)
        lado_m = max(2.0, lp * k)
        for gx, gy in p["parches"]:
            u, v = (gx * lp * scale - tx0) * e, (gy * lp * scale - ty0) * e
            d.rectangle([u, v, u + lado_m, v + lado_m], fill=verde + (235,))
        mini = Image.alpha_composite(mini.convert("RGBA"), capa).convert("RGB")
        d = ImageDraw.Draw(mini)
        u0, v0 = (zx0 * scale - tx0) * e, (zy0 * scale - ty0) * e
        u1, v1 = u0 + Z * k, v0 + Z * k
        for off, col, w in ((0, TINTA, 6), (6, BLANCO, 3)):
            d.rectangle([u0 - 6 + off, v0 - 6 + off, u1 + 6 - off, v1 + 6 - off],
                        outline=col, width=w)
        n_mini = guardar(mini, f"s05_{p['grado']}_miniatura.png")

        osr = _osr(slide)
        nivel = osr.get_best_level_for_downsample(Z / float(LADO_ZOOM_PX))
        ds = osr.level_downsamples[nivel]
        zoom = osr.read_region((zx0, zy0), nivel, (int(np.ceil(Z / ds)),) * 2).convert("RGB")
        zoom = zoom.resize((LADO_ZOOM_PX, LADO_ZOOM_PX), Image.LANCZOS)
        osr.close()
        f = LADO_ZOOM_PX / float(Z)
        capa = Image.new("RGBA", zoom.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(capa)
        en_zoom = 0
        for gx, gy in p["parches"]:
            u, v = (gx * lp - zx0) * f, (gy * lp - zy0) * f
            if u + lp * f <= 0 or v + lp * f <= 0 or u >= LADO_ZOOM_PX or v >= LADO_ZOOM_PX:
                continue
            en_zoom += 1
            d.rectangle([u, v, u + lp * f - 1, v + lp * f - 1], fill=verde + (40,),
                        outline=verde + (255,), width=4)
        zoom = Image.alpha_composite(zoom.convert("RGBA"), capa).convert("RGB")
        d = ImageDraw.Draw(zoom)
        # primero las no recuperadas, así una recuperada vecina queda encima
        orden = sorted(p["marcas"], key=lambda m: m["estado"] == "recuperada")
        for m in orden:
            u, v = (m["x"] - zx0) * f, (m["y"] - zy0) * f
            if m["estado"] == "no_alcanzable":
                d.line([u - 12, v - 12, u + 12, v + 12], fill=TINTA, width=6)
                d.line([u - 12, v + 12, u + 12, v - 12], fill=TINTA, width=6)
            else:
                anillo(d, u, v, 18, relleno=TINTA if m["estado"] == "recuperada" else None, ancho=5)
        n_zoom = guardar(zoom, f"s05_{p['grado']}_zoom.png")

        reg = dict(grado=p["grado"], slide=slide, carga_mm2=p["carga_mm2"],
                   n_parches=p["n_parches"], cuenta=p["cuenta"], n_marcas=len(p["marcas"]),
                   miniatura=dict(png=n_mini, recuadro_px=[u0 - 6, v0 - 6, u1 + 6, v1 + 6],
                                  lado_mm=[(tx1 - tx0) / scale * sel["mpp"] / 1000,
                                                       (ty1 - ty0) / scale * sel["mpp"] / 1000]),
                   zoom=dict(png=n_zoom, origen_px=[zx0, zy0], lado_px=Z,
                             lado_mm=Z * sel["mpp"] / 1000, parches_en_zoom=en_zoom))
        regs.append(reg)
        print(f"  s05 {p['grado']:<5} {slide:<9} miniatura {mini.size} "
              f"({reg['miniatura']['lado_mm'][0]:.1f} × {reg['miniatura']['lado_mm'][1]:.1f} mm) · "
              f"zoom {Z} px = {reg['zoom']['lado_mm']:.2f} mm con {en_zoom} parches de la carga · "
              f"{p['cuenta']}")
    return dict(orden_dibujo=regs, lado_zoom_px=Z)


# --------------------------------------------------------------------------------------
# s06

def render_s06(sel):
    k = AMPLIA_GALERIA
    regs, osrs = [], {}
    for p in sel["s06"]:
        nombre = p["ventana"][len("ventana_"):-len(".npz")]
        v, x0, y0, pinst = ventana(nombre, p)
        ids = set(v["ids"].tolist())
        if p["inst_id"] not in ids:
            sys.exit(f"gate 1: {nombre} no trae el núcleo marcado")
        if p["slide"] not in osrs:
            osrs[p["slide"]] = _osr(p["slide"])
        lado = p["lado_px"]
        rgb = np.asarray(tejido(osrs[p["slide"]], x0, y0, lado).resize((lado * k, lado * k),
                                                                        Image.LANCZOS),
                         dtype=np.float32)
        # sólo los núcleos que la selección dejó en la ventana: el marcado y los del top 500
        visibles = np.where(np.isin(pinst, list(ids)), pinst, 0)
        ids_k = ampliar(visibles, k)
        marcado = ids_k == p["inst_id"]
        # A 1,24" por panel un píxel nativo mide 0,56 pt. Los vecinos: borde interior de un
        # píxel nativo. El marcado: el mismo borde más una aureola de dos píxeles nativos por
        # fuera, que lo distingue sin comerle el interior a un núcleo de 20 píxeles.
        pintar(rgb, borde(np.where(marcado, 0, ids_k), k), VERDE, 1.0)
        pintar(rgb, borde(np.where(marcado, ids_k, 0), k), VERDE, 1.0)
        pintar(rgb, aureola(np.where(marcado, ids_k, 0), 2 * k), VERDE, 1.0)
        png = guardar(Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)), f"{nombre}.png")
        regs.append(dict(png=png, grado=p["grado"], columna=p["columna"], slide=p["slide"],
                         estado=p["estado"], puesto=p["puesto"], percentil=p["percentil"],
                         area_um2=p["area_um2"], n_top500_en_ventana=int(len(ids) - 1),
                         lado_px=lado, lado_um=lado * sel["mpp"]))
    for o in osrs.values():
        o.close()
    print(f"  s06 {len(regs)} paneles de {regs[0]['lado_px']} px = {regs[0]['lado_um']:.1f} µm; "
          f"vecinos del top 500 por panel: {[r['n_top500_en_ventana'] for r in regs]}")
    return dict(orden_dibujo=regs)


# --------------------------------------------------------------------------------------
# s09

def poligonos_cdis(slide):
    off = json.loads((OFFSETS / f"offset_{slide}.json").read_text())
    dx, dy = float(off["dx"]), float(off["dy"])
    out = []
    for ft in json.loads(geojson_de(slide).read_text()).get("features", []):
        cl = ft.get("properties", {}).get("classification", {})
        if (cl.get("name") if isinstance(cl, dict) else str(cl)) not in CDIS:
            continue
        g = ft["geometry"]
        anillos = g["coordinates"] if g["type"] == "Polygon" else g["coordinates"][0]
        p = np.asarray(anillos[0], float) + np.array([dx, dy])
        if len(p) >= 3:
            out.append(p)
    return out, off


def elegir_s09():
    a = pd.read_csv(CDIS_DIR / "auc_cdis.csv", dtype={"slide": str})
    r = pd.read_csv(CDIS_DIR / "auc_cdis_region.csv", dtype={"slide": str})
    v = a[a.fuente == "ckpt_1fold_verdadera"]
    train = v[v.tier == "train"].sort_values("auc", ascending=False, kind="stable").iloc[0]
    test = v[v.tier == "test"]
    # la B25-158899 no tiene etiqueta: su única rama del checkpoint es la predicha, `si`
    fuera = r[(r.tier == "fuera") & (r.universo == "region") & (r.fuente == "ckpt_1fold_predicha")]
    if len(test) != 1 or len(fuera) != 1:
        sys.exit("s09: la regla esperaba una lámina de test y una fuera del split")
    return [(train, "verdadera", "lamina"), (test.iloc[0], "verdadera", "lamina"),
            (fuera.iloc[0], "predicha", "region")]


def overlay_mapa(coords, pct, scale, tw, th, step):
    """`build_overlay_rgba` del B7 y el B9, sin tocarla, con dos arreglos hechos afuera.

    1. La función marca como cubierto TODO píxel (hace `max(c, 1)` antes de `c > 0`), así que
       el vidrio recibe el color de la atención cero y sale violeta. Acá se anula el alfa fuera
       de los parches, con la misma geometría de redondeo que usa ella.
    2. Con `round(step * scale)` los parches dejan rendijas de un píxel que se leen como
       grilla. Se le pasa un parche 1,5 px más ancho en la miniatura, que los solapa."""
    ps = step + 1.5 / scale
    ov = build_overlay_rgba(coords, pct, scale, tw, th, ps)
    pt = max(1, int(round(ps * scale)))
    cub = np.zeros((th, tw), dtype=bool)
    for x, y in coords:
        u, v = int(round(x * scale)), int(round(y * scale))
        cub[max(v, 0):v + pt, max(u, 0):u + pt] = True
    ov[~cub, 3] = 0.0
    return ov


def turbo_rgba(pct, alpha):
    import matplotlib
    c = np.asarray(matplotlib.colormaps["turbo"](np.clip(pct, 0, 1)))
    return [tuple(int(round(255 * v)) for v in fila[:3]) + (int(round(255 * alpha)),) for fila in c]


def trazo_poligono(d, pts, grueso=7, fino=3):
    pts = list(pts) + [pts[0]]
    d.line(pts, fill=TINTA, width=grueso, joint="curve")
    d.line(pts, fill=BLANCO, width=fino, joint="curve")


def render_s09():
    from matplotlib.path import Path as MPath
    from scripts.mammoth_interpretability import HEATMAP_ALPHA
    labs = etiquetas()
    # la † del forest plot: el script de figuras de O3 es el único escritor de este CSV
    fig = pd.read_csv(REPO / "sprints/B10_sprint10/figuras/o3_auc_por_lamina.csv",
                      dtype={"slide": str})
    alineadas = dict(zip(fig.slide, fig.alineada.astype(str) == "True"))
    regs = []
    for fila, cabeza, universo in elegir_s09():
        slide = fila.slide
        feats, coords = leer_h5(slide)
        step = paso_de_grilla(coords)
        idx_pos, n_pol = parches_cdis(slide, coords, step)
        A, rama = atencion_ckpt(feats, cabeza, labs.get(slide))
        if fila.rama != f"{cabeza}:{rama}":
            sys.exit(f"gate 3: {slide} lee la rama {cabeza}:{rama} y el CSV dice {fila.rama}")
        idx_u = universos_de(slide, coords, idx_pos)[universo]
        pos_u = np.array(sorted(set(idx_pos.tolist()) & set(idx_u.tolist())), dtype=np.int64)
        loc = {g: i for i, g in enumerate(idx_u)}
        auc = rank_auc(ranks_of(A[idx_u]), np.array([loc[i] for i in pos_u], dtype=np.int64))
        if abs(auc - fila.auc) > 1e-9 or len(pos_u) != fila.n_marcados:
            sys.exit(f"gate 3: {slide} da AUC {auc} con {len(pos_u)} parches, publicado "
                     f"{fila.auc} con {fila.n_marcados}")
        cu = coords[idx_u]
        pct = percentile_scores(A[idx_u])
        pols, off = poligonos_cdis(slide)

        # el zoom: centrado en el polígono con más parches positivos del universo
        centros = cu.astype(float) + step / 2.0
        n_por_pol = [int(MPath(p).contains_points(centros).sum()) for p in pols]
        k_pol = int(np.argmax(n_por_pol))
        c = (pols[k_pol].max(0) + pols[k_pol].min(0)) / 2.0
        Z = LADO_ZOOM_CDIS * step
        zx0, zy0 = int(round(c[0] - Z / 2.0)), int(round(c[1] - Z / 2.0))

        thumb, scale, _mag, _w0, _h0 = get_wsi_thumbnail(WSI_DIR / slide / f"{slide}.bif")
        th, tw = thumb.shape[:2]
        im = Image.fromarray((blend(thumb, overlay_mapa(cu, pct, scale, tw, th, step)) * 255)
                             .astype(np.uint8))
        tx0, ty0, tx1, ty1 = recorte_tejido(cu, step, scale, tw, th)
        im, e = achicar(im.crop((tx0, ty0, tx1, ty1)), MAX_LADO_MINI)
        d = ImageDraw.Draw(im)
        u0, v0 = (zx0 * scale - tx0) * e, (zy0 * scale - ty0) * e
        u1, v1 = u0 + Z * scale * e, v0 + Z * scale * e
        for o, col, w in ((0, TINTA, 6), (6, BLANCO, 3)):
            d.rectangle([u0 - 6 + o, v0 - 6 + o, u1 + 6 - o, v1 + 6 - o], outline=col, width=w)
        png_mapa = guardar(im, f"s09_{fila.tier}_{slide}_mapa.png")

        osr = _osr(slide)
        nivel = osr.get_best_level_for_downsample(Z / float(LADO_ZOOM_PX))
        ds = osr.level_downsamples[nivel]
        zoom = osr.read_region((zx0, zy0), nivel, (int(np.ceil(Z / ds)),) * 2).convert("RGB")
        zoom = zoom.resize((LADO_ZOOM_PX, LADO_ZOOM_PX), Image.LANCZOS)
        osr.close()
        f = LADO_ZOOM_PX / float(Z)
        capa = Image.new("RGBA", zoom.size, (0, 0, 0, 0))
        dc = ImageDraw.Draw(capa)
        dentro = np.nonzero((cu[:, 0] + step > zx0) & (cu[:, 0] < zx0 + Z)
                            & (cu[:, 1] + step > zy0) & (cu[:, 1] < zy0 + Z))[0]
        for j, col in zip(dentro, turbo_rgba(pct[dentro], HEATMAP_ALPHA)):
            u, v = (cu[j, 0] - zx0) * f, (cu[j, 1] - zy0) * f
            dc.rectangle([u, v, u + step * f, v + step * f], fill=col)
        zoom = Image.alpha_composite(zoom.convert("RGBA"), capa).convert("RGB")
        dz = ImageDraw.Draw(zoom)
        for p in pols:
            trazo_poligono(dz, [((x - zx0) * f, (y - zy0) * f) for x, y in p])
        png_zoom = guardar(zoom, f"s09_{fila.tier}_{slide}_zoom.png")

        regs.append(dict(slide=slide, tier=fila.tier, rama=fila.rama, universo=universo,
                         alineada=bool(alineadas[slide]), auc=float(auc),
                         ic95_lo=float(fila.ic95_lo), ic95_hi=float(fila.ic95_hi),
                         p_nulo=float(fila.p_nulo), n_parches=int(len(idx_u)),
                         n_marcados=int(len(pos_u)), n_poligonos=int(n_pol),
                         mapa=dict(png=png_mapa, recuadro_px=[u0 - 6, v0 - 6, u1 + 6, v1 + 6],
                                   lado_mm=[(tx1 - tx0) / scale * MPP / 1000,
                                                          (ty1 - ty0) / scale * MPP / 1000]),
                         zoom=dict(png=png_zoom, origen_px=[zx0, zy0], lado_px=Z,
                                   lado_mm=Z * MPP / 1000, poligono=k_pol,
                                   parches_positivos_del_poligono=n_por_pol[k_pol],
                                   parches_por_poligono=n_por_pol,
                                   parches_en_zoom=int(len(dentro)))))
        print(f"  s09 {fila.tier:<6} {slide:<11} {fila.rama:<14} {universo:<7} AUC {auc:.3f} "
              f"({len(pos_u)} de {len(idx_u)} parches, {n_pol} polígonos) · mapa {im.size} · "
              f"zoom {Z * MPP / 1000:.2f} mm sobre el polígono {k_pol} ({n_por_pol[k_pol]} parches)")
    return dict(orden_dibujo=regs, rampa="turbo por percentil dentro del universo",
                alfa=HEATMAP_ALPHA,
                fuente_ckpt="results_modelo_pth_balance/carcinoma_ductal_insitu_presente_"
                            "pth_balance_s1/s_0_checkpoint.pt")


# --------------------------------------------------------------------------------------

def main():
    t0 = time.time()
    sel = json.loads((SEL_DIR / "seleccion.json").read_text())
    g = sel["gates"]
    if g["recuperadas"] != {"alto": 41, "moderado": 12, "bajo": 0} or \
            g["alcanzables"] != {"alto": 76, "moderado": 53, "bajo": 16}:
        sys.exit("seleccion.json no es la de los gates publicados: re-correr b10_deck_seleccion.py")
    print("=" * 100)
    print("Imágenes del deck del 15-sep · render de la selección, sin medición nueva")
    print("=" * 100)
    out = dict(plan=sel["plan"], seleccion="results/b10_deck_imagenes/seleccion.json",
               mpp=sel["mpp"], n_carga=sel["n_carga"],
               paleta=dict(grupos=[dict(grupo=gr, color=c) for gr, _, c in GRUPOS],
                           validacion="validate_palette.py --mode light --surface #e6c3d8 "
                                      "--pairs all sobre los tres tonos: PASS banda, croma, CVD "
                                      "9,1, normal 22,9; WARN contraste (leyenda nativa)"),
               s03=render_s03(sel), s05=render_s05(sel), s06=render_s06(sel), s09=render_s09())
    (OUT / "deck_imagenes.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
    print(f"\n  gates OK · escrito: {OUT}/deck_imagenes.json y sus PNG  ({time.time() - t0:.0f} s)")


if __name__ == "__main__":
    main()
