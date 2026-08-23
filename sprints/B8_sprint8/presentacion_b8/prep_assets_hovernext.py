"""prep_assets_hovernext.py — los assets de la lámina de resultados del 19-ago.

Dibuja la CADENA que pidió Sebastián: el mapa de atención de CLAM recorta la región, y
HoVer-NeXt detecta adentro. No son dos herramientas por separado puestas una al lado de la
otra: los tres paneles son la misma región y el mismo recorte, en tres estados.

  Panel 1  la atención de CLAM sobre la región anotada
  Panel 2  el recorte: el 12 % más atendido (300 de los 2496 parches)
  Panel 3  las detecciones de HoVer-NeXt, separando las que caen dentro del recorte

Y el CONTROL de esa cadena, que es la herramienta sola: la lámina entera, sus DOS regiones
de escaneo y las 177 detecciones, sin ninguna máscara. Es el brazo contra el que se lee todo
lo demás, porque la corrida fue así de entrada — la lámina completa, y el recorte aplicado
después sobre la salida.

Y el detalle, que es lo que contesta «dónde se fija»: cuatro recortes a resolución nativa
sobre mitosis que la herramienta acertó, con la marca del patólogo encima.

Reglas de lectura que la figura NO puede violar (y por eso están acá y no solo en el guion):

- Las marcas del patólogo son **positivos parciales**: una detección sin marca NO es un
  falso positivo, así que ningún panel las pinta como error.
- El geojson **no** está en coordenadas de openslide: se le suma el offset ya derivado en
  `anotaciones_patologo/offset_129741.json`.
- La lámina tiene **dos regiones de escaneo** y las marcas caen todas en la de abajo. Todo
  se confina ahí, igual que en el cruce.

Es una FIGURA sobre tejido real, o sea la excepción legítima a «todo nativo» del deck
(CLAUDE.md, ADDENDUM 3-ago): un mapa sobre tejido no es dibujable con shapes.

Salidas, en `assets/`:
  cadena_clam_hovernext.png   los tres paneles
  hovernext_zoom.png          los cuatro detalles a resolución nativa
  hovernext_solo.png          la lámina entera, sus dos regiones y las 177 detecciones

Uso (workaround B: binario absoluto del env):
  PYTHONPATH=/media/administrador/Storage1/sdonoso/clam_testing2/.pylibs \
  /home/sdonoso/miniconda3/envs/clam_latest/bin/python \
    sprints/B8_sprint8/presentacion_b8/prep_assets_hovernext.py
"""
from __future__ import annotations

import csv
import json
import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

REPO = Path("/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto")
sys.path.insert(0, str(REPO / "scripts"))

DST = REPO / "sprints/B8_sprint8/presentacion_b8/assets"
WSI = "/media/administrador/Storage1/sdonoso/wsi/129741/129741.bif"
GEOJSON = "/media/administrador/Storage1/sdonoso/hover_net/129741.bif - GDT.geojson"
NPZ = (REPO / "results/b8_hovernext_129741/interp/"
       "carcinoma_ductal_insitu_presente_ci_reform/129741/atencion_por_parche.npz")
TSV = (REPO / "results/b8_hovernext_129741/hovernext/lizard_mitosis/129741/"
       "pred_mitosis.tsv")
OFFSET = REPO / "sprints/B8_sprint8/anotaciones_patologo/offset_129741.json"

Y_CORTE_REGION = 49920      # techo_atencion_topk.py: la región de abajo es la anotada
K_MASCARA = 300             # la fila resaltada del cruce: 12,0 % de la región
MPP = 0.465
TOL_UM = 30.0               # la tolerancia adoptada; el resultado es plano de 7,5 a 75

NIVEL = 4                   # ÷16 → la región queda en ~2050x1680, de sobra para proyectar
ZOOM_LADO = 260             # px de nivel 0 por recorte de detalle = 121 µm
ZOOM_ESCALA = 3

# Paleta del template (Deep-LLM-V), para que la figura no desentone con las láminas nativas
ONCO_DARK = (0x3E, 0x68, 0x77)
ONCO_INK = (0x0E, 0x28, 0x41)
AMARILLO = (0xFF, 0xC1, 0x07)      # detección de HoVer-NeXt
BLANCO = (255, 255, 255)
NEGRO = (20, 20, 20)


# ---------------------------------------------------------------- datos

def cargar_todo():
    from alinear_anotaciones_qupath import cargar_anotaciones
    from scipy.optimize import linear_sum_assignment

    z = np.load(NPZ)
    coords, ps0 = z["coords_level0"], float(z["patch_size_level0"])
    aten = z["atencion_clam"]

    off = json.loads(OFFSET.read_text())
    marcas = []
    for cl, poly in cargar_anotaciones(GEOJSON):
        if cl == "Mitosis":
            marcas.append((poly + np.array([off["dx"], off["dy"]], float)).mean(axis=0))
    marcas = np.asarray(marcas)

    det = np.asarray([[float(r["x"]), float(r["y"])]
                      for r in csv.DictReader(open(TSV), delimiter="\t")])

    # emparejamiento uno a uno, idéntico al de scripts/cruce_hovernext_marcas.py
    dist = np.linalg.norm(marcas[:, None, :] - det[None, :, :], axis=2)
    c = dist.copy(); c[c > TOL_UM / MPP] = 1e9
    fi, ci = linear_sum_assignment(c)
    pares = [(i, j) for i, j in zip(fi, ci) if dist[i, j] <= TOL_UM / MPP]
    return coords, ps0, aten, marcas, det, pares


def mascara_topk(coords, aten, k):
    """Los k parches más atendidos DENTRO de la región anotada."""
    idx = np.where(coords[:, 1] >= Y_CORTE_REGION)[0]
    orden = idx[np.argsort(aten[idx])[::-1]]
    return idx, orden[:k]


# ---------------------------------------------------------------- dibujo

def turbo(v):
    """turbo de matplotlib, sin importar pyplot para una sola paleta."""
    import matplotlib
    r, g, b, _ = matplotlib.colormaps["turbo"](float(v))
    return int(r * 255), int(g * 255), int(b * 255)


def _tinte(base, col, alfa):
    """Mezcla un color plano sobre una imagen RGB ya cargada como array."""
    return (base * (1 - alfa) + np.asarray(col, float) * alfa).astype(np.uint8)


def region_thumb(sl, x0, y0, x1, y1):
    ds = sl.level_downsamples[NIVEL]
    w, h = int((x1 - x0) / ds), int((y1 - y0) / ds)
    im = sl.read_region((int(x0), int(y0)), NIVEL, (w, h)).convert("RGB")
    return im, ds


def panel_atencion(base, coords, aten, idx_region, x0, y0, ds):
    """El mapa de atención por percentil, como en la figura del 31-jul."""
    arr = np.asarray(base, float)
    a_reg = aten[idx_region]
    pct = np.argsort(np.argsort(a_reg)) / (len(a_reg) - 1)
    ov = np.zeros(arr.shape, float)
    al = np.zeros(arr.shape[:2], float)
    ps = 256
    for i, p in zip(idx_region, pct):
        cx, cy = coords[i]
        a = int((cx - x0) / ds); b = int((cy - y0) / ds)
        c = int((cx + ps - x0) / ds); d = int((cy + ps - y0) / ds)
        ov[b:d, a:c] = turbo(p)
        al[b:d, a:c] = 0.58
    al = al[:, :, None]
    return Image.fromarray(np.clip(ov * al + arr * (1 - al), 0, 255).astype(np.uint8))


def panel_mascara(base, coords, sel, x0, y0, ds, marcar=None):
    """El tejido apagado, y encima el recorte. `marcar` pinta puntos sobre el recorte."""
    arr = np.asarray(base, float)
    gris = arr.mean(axis=2, keepdims=True).repeat(3, axis=2)
    arr = _tinte(gris, (255, 255, 255), 0.55).astype(float)   # tejido lavado, de fondo

    al = np.zeros(arr.shape[:2], float)
    ps = 256
    for i in sel:
        cx, cy = coords[i]
        a = int((cx - x0) / ds); b = int((cy - y0) / ds)
        c = int((cx + ps - x0) / ds); d = int((cy + ps - y0) / ds)
        al[b:d, a:c] = 1.0
    # el recorte recupera el tejido real y se tiñe del teal del template
    orig = np.asarray(base, float)
    m = al[:, :, None]
    dentro = _tinte(orig, ONCO_DARK, 0.42).astype(float)
    im = Image.fromarray(np.clip(dentro * m + arr * (1 - m), 0, 255).astype(np.uint8))

    if marcar is not None:
        d = ImageDraw.Draw(im)
        dentro_pts, fuera_pts = marcar
        for (px, py) in fuera_pts:
            u, v = (px - x0) / ds, (py - y0) / ds
            d.ellipse([u - 6, v - 6, u + 6, v + 6], outline=(110, 110, 110), width=3)
        for (px, py) in dentro_pts:
            u, v = (px - x0) / ds, (py - y0) / ds
            d.ellipse([u - 11, v - 11, u + 11, v + 11], fill=AMARILLO,
                      outline=ONCO_INK, width=3)
    return im


def _acotar(im, ancho_max):
    """Los paneles se DIBUJAN a resolución generosa y se guardan acotados.

    En la lámina la cadena mide 4,62 pulgadas, así que el montaje a 6205 px iría a 1340 DPI:
    son megabytes que nadie ve y que el deck arrastra. Se dibuja igual de grande, porque el
    antialias de los puntos y de los bordes de parche sale mejor, y se reduce al final."""
    if im.width <= ancho_max:
        return im
    h = round(im.height * ancho_max / im.width)
    return im.resize((ancho_max, h), Image.LANCZOS)


def componer(paneles, sep=26):
    w = max(p.width for p in paneles); h = max(p.height for p in paneles)
    out = Image.new("RGB", (w * len(paneles) + sep * (len(paneles) - 1), h), BLANCO)
    for i, p in enumerate(paneles):
        out.paste(p, (i * (w + sep), 0))
    return out


def detalles(sl, det, marcas, pares, n=4):
    """Recortes a resolución nativa sobre mitosis acertadas: dónde se fija la herramienta.

    Se eligen los pares más separados entre sí para no mostrar cuatro veces el mismo foco.
    """
    cand = [(i, j) for i, j in pares]
    elegidos = [cand[0]]
    while len(elegidos) < n and len(elegidos) < len(cand):
        mejor, dmax = None, -1
        for p in cand:
            if p in elegidos:
                continue
            dm = min(np.linalg.norm(marcas[p[0]] - marcas[q[0]]) for q in elegidos)
            if dm > dmax:
                mejor, dmax = p, dm
        elegidos.append(mejor)

    crops = []
    L = ZOOM_LADO
    for i, j in elegidos:
        cx, cy = det[j]
        im = sl.read_region((int(cx - L / 2), int(cy - L / 2)), 0, (L, L)).convert("RGB")
        im = im.resize((L * ZOOM_ESCALA, L * ZOOM_ESCALA), Image.LANCZOS)
        d = ImageDraw.Draw(im)
        c = L * ZOOM_ESCALA / 2
        r = 13 * ZOOM_ESCALA                       # ~12 µm, el orden de un núcleo mitótico
        d.ellipse([c - r, c - r, c + r, c + r], outline=AMARILLO, width=6)
        # la marca del patólogo, en su posición real relativa a la detección
        mx, my = marcas[i]
        u = c + (mx - cx) * ZOOM_ESCALA; v = c + (my - cy) * ZOOM_ESCALA
        rr = r * 1.9
        d.ellipse([u - rr, v - rr, u + rr, v + rr], outline=BLANCO, width=5)
        # barra de escala: 25 µm
        px25 = int(25 / MPP * ZOOM_ESCALA)
        y = L * ZOOM_ESCALA - 34
        d.rectangle([26, y, 26 + px25, y + 9], fill=NEGRO)
        crops.append(im)
    return componer(crops, sep=18), elegidos


def panel_detecciones(sl, coords, ps0, idx, det, x0=None):
    """Una región de escaneo con TODAS sus detecciones, sin máscara de ninguna clase.

    Es el brazo de control: la herramienta sola. Las detecciones van todas del mismo color
    a propósito — son la misma salida, y pintar de distinto las de la región sin anotar
    sugeriría una diferencia de calidad que no medimos."""
    # La caja se toma sobre los parches y se ENSANCHA hasta cubrir las detecciones de la
    # banda: tres de las 177 caen unos 700 px por encima del teselado, en tejido que el
    # umbral no llegó a cubrir. Recortarlas dejaría el panel mostrando 174 y el guion
    # diciendo 177.
    c = coords[idx]
    a, b = float(c[:, 0].min()), float(c[:, 1].min())
    d, e = float(c[:, 0].max() + ps0), float(c[:, 1].max() + ps0)
    banda = det[(det[:, 1] >= b - 6000) & (det[:, 1] < e + 6000)] if len(det) else det
    if len(banda):
        a = min(a, float(banda[:, 0].min()) - 200); b = min(b, float(banda[:, 1].min()) - 200)
        d = max(d, float(banda[:, 0].max()) + 200); e = max(e, float(banda[:, 1].max()) + 200)
    im, ds = region_thumb(sl, a, b, d, e)
    dr = ImageDraw.Draw(im)
    n = 0
    for (px, py) in det:
        if not (a <= px < d and b <= py < e):
            continue
        u, v = (px - a) / ds, (py - b) / ds
        dr.ellipse([u - 10, v - 10, u + 10, v + 10], fill=AMARILLO, outline=ONCO_INK, width=3)
        n += 1
    return im, n


# ---------------------------------------------------------------- main

def main():
    import openslide

    DST.mkdir(parents=True, exist_ok=True)
    coords, ps0, aten, marcas, det, pares = cargar_todo()
    idx_region, sel = mascara_topk(coords, aten, K_MASCARA)

    c = coords[idx_region]
    x0, y0 = float(c[:, 0].min()), float(c[:, 1].min())
    x1, y1 = float(c[:, 0].max() + ps0), float(c[:, 1].max() + ps0)

    sl = openslide.OpenSlide(WSI)
    base, ds = region_thumb(sl, x0, y0, x1, y1)
    print(f"región {x0:.0f},{y0:.0f}–{x1:.0f},{y1:.0f}  ·  panel {base.size}  ·  ÷{ds:.0f}")

    # qué detecciones caen dentro del recorte (mismo criterio que el cruce: por parche)
    sel_set = set(int(i) for i in sel)
    dentro, fuera = [], []
    for (px, py) in det:
        if py < Y_CORTE_REGION:
            continue
        w = np.where((coords[:, 0] <= px) & (px < coords[:, 0] + ps0) &
                     (coords[:, 1] <= py) & (py < coords[:, 1] + ps0))[0]
        (dentro if (len(w) and int(w[0]) in sel_set) else fuera).append((px, py))
    print(f"detecciones en la región: {len(dentro) + len(fuera)}  "
          f"(dentro del recorte {len(dentro)}, fuera {len(fuera)})")

    p1 = panel_atencion(base, coords, aten, idx_region, x0, y0, ds)
    p2 = panel_mascara(base, coords, sel, x0, y0, ds)
    p3 = panel_mascara(base, coords, sel, x0, y0, ds, marcar=(dentro, fuera))
    cadena = _acotar(componer([p1, p2, p3]), 3400)     # ~735 DPI en la lámina
    cadena.save(DST / "cadena_clam_hovernext.png")
    print("  %-30s %s" % ("cadena_clam_hovernext.png", cadena.size))

    # El detalle se acota menos: su información real son 260 px de nivel 0 por recorte, y
    # conviene que aguante un acercamiento en pantalla sin verse interpolado.
    zoom, elegidos = detalles(sl, det, marcas, pares)
    zoom = _acotar(zoom, 2400)
    zoom.save(DST / "hovernext_zoom.png")
    print("  %-30s %s  (pares %s)" % ("hovernext_zoom.png", zoom.size,
                                      [p[0] for p in elegidos]))

    # ---- el control: la herramienta sola sobre la lámina entera ----
    idx_otra = np.where(coords[:, 1] < Y_CORTE_REGION)[0]
    pa, na = panel_detecciones(sl, coords, ps0, idx_otra, det)
    pb, nb = panel_detecciones(sl, coords, ps0, idx_region, det)
    solo = _acotar(componer([pa, pb]), 3400)
    solo.save(DST / "hovernext_solo.png")
    print("  %-30s %s  (región sin marcas %d · región anotada %d)"
          % ("hovernext_solo.png", solo.size, na, nb))

    # ---- las dos láminas de contacto de la galería (encargo 2) ----
    # Se copian y no se re-dibujan: las produce `scripts/galeria_mitosis_129741.py` a
    # resolución nativa y el deck solo las inserta. Van con nombre propio en `assets/` para
    # que regenerar el deck no dependa de un `cp` a mano.
    GAL = REPO / "results/b8_hovernext_129741/galeria_mitosis"
    for orig, destino in (("bloque_sin_marca.png", "galeria_sin_marca.png"),
                          ("bloque_falladas.png", "galeria_falladas.png")):
        src = GAL / orig
        if not src.exists():
            print("  FALTA %s — corré scripts/galeria_mitosis_129741.py" % src)
            continue
        shutil.copyfile(src, DST / destino)
        with Image.open(DST / destino) as im:
            print("  %-30s %s  (copiada de %s)" % (destino, im.size, orig))

    (DST / "cadena_clam_hovernext.json").write_text(json.dumps(dict(
        region=[x0, y0, x1, y1], nivel=NIVEL, downsample=ds,
        parches_region=int(len(idx_region)), k_mascara=K_MASCARA,
        pct_region=round(100 * K_MASCARA / len(idx_region), 1),
        detecciones_region=len(dentro) + len(fuera),
        detecciones_dentro=len(dentro), detecciones_fuera=len(fuera),
        marcas=int(len(marcas)), pares_uno_a_uno=len(pares),
        tolerancia_um=TOL_UM, mpp=MPP,
        parches_lamina=int(len(coords)), parches_otra_region=int(len(idx_otra)),
        detecciones_otra_region=na, detecciones_region_anotada=nb,
    ), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
