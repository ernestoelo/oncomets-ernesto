#!/usr/bin/env python
"""prep_assets_atencion.py — recorta para el deck las dos figuras de `atencion_vs_patologo/`.

Las figuras originales se generaron para ARCHIVO, no para proyectar: traen los títulos de
matplotlib y, sobre todo, un hueco vertical de ~390 px entre las dos regiones de escaneo del
`.bif`. Puestas tal cual en una lámina, el tejido queda del tamaño de una moneda.

Acá se recortan SIN alterar el contenido: se quitan los títulos (pasan a ser texto nativo de
la lámina) y el aire muerto entre filas. Las dos regiones se conservan en la figura de los
mapas, porque esconder una de las dos sería esconder la trampa de lectura que la leyenda
obligatoria tiene que explicar (hallazgo F4 de la sexta pasada de la auditoría).

Salidas, todas en `assets/`:
  atencion_dos_regiones.png   los 4 paneles (atención | anotaciones) x (región 1 | región 2)
  mitosis_region_anotada.png  la región anotada con los 28 parches de mitosis en blanco
  mitosis_zoom.png            detalle del foco donde se concentran esos parches

Uso:
  PYTHONPATH=/media/administrador/Storage1/sdonoso/clam_testing2/.pylibs \
  /home/sdonoso/miniconda3/envs/clam_latest/bin/python \
    sprints/B8_sprint8/presentacion_b8/prep_assets_atencion.py
"""
import os

import numpy as np
from PIL import Image, ImageDraw

REPO = "/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto"
SRC = os.path.join(REPO, "sprints/B8_sprint8/atencion_vs_patologo")
DST = os.path.join(REPO, "sprints/B8_sprint8/presentacion_b8/assets")

FIG_MAPAS = os.path.join(SRC, "figura_atencion_vs_anotaciones.png")
FIG_MITOSIS = os.path.join(SRC, "figura_mitosis_sobre_atencion.png")

# Cajas de los paneles, medidas sobre las figuras (perfil de filas y de columnas con umbral
# 245, las columnas medidas DENTRO de cada fila). Se dejan explícitas en vez de
# re-detectarlas: las figuras están congeladas desde el 31-jul y un detector automático es
# una fuente de sorpresas silenciosas al regenerar el deck.
MAPAS_FILAS = [(122, 745), (1135, 1759)]      # región 1 (arriba), región 2 (la anotada)
MAPAS_COLS = [(96, 832), (1488, 2228)]        # atención, anotaciones
MITOSIS_REGION2 = (1171, 1847)                # la fila con las marcas
MITOSIS_COLS = (278, 1078)

SEP = 22                                       # aire entre paneles, en px
BLANCO = (255, 255, 255)
ROJO = (214, 39, 40)


def _grilla_paneles(im, filas, cols, sep=SEP):
    """Recompone los paneles en una grilla compacta, sin el aire muerto del original.

    La figura de archivo separa los paneles con cientos de píxeles en blanco, que en una
    lámina proyectada dejan el tejido del tamaño de una moneda."""
    pw = max(x1 - x0 for x0, x1 in cols)
    ph = max(y1 - y0 for y0, y1 in filas)
    out = Image.new("RGB", (pw * len(cols) + sep * (len(cols) - 1),
                            ph * len(filas) + sep * (len(filas) - 1)), BLANCO)
    for fi, (y0, y1) in enumerate(filas):
        for ci, (x0, x1) in enumerate(cols):
            out.paste(im.crop((x0, y0, x1, y1)), (ci * (pw + sep), fi * (ph + sep)))
    return out


def _foco_blancos(img, margen=34):
    """Caja del grupo más denso de parches de mitosis sobre el mapa de atención.

    Los 28 parches se pintaron blanco sólido encima del mapa de colores. Buscarlos por
    «blanco puro» a secas NO sirve: el fondo del lienzo también es casi blanco y aporta
    27 000 píxeles de ruido. Lo que los distingue es la VECINDAD: son los únicos blancos
    rodeados de píxeles muy saturados, porque están dentro del mapa de calor. Con eso
    quedan 11 grupos limpios."""
    from scipy.ndimage import uniform_filter  # noqa: PLC0415

    hsv = np.array(img.convert("HSV")).astype(float)
    S, V = hsv[:, :, 1], hsv[:, :, 2]
    blanco = (V > 250) & (S < 12)
    vecindad_saturada = uniform_filter((S > 90).astype(float), size=41)
    marcas = blanco & (vecindad_saturada > 0.25)
    ys, xs = np.nonzero(marcas)
    if len(ys) == 0:
        return None
    W, H = img.size
    lado = int(min(W, H) * 0.33)
    mejor, caja = -1, None
    for y0 in range(0, H - lado, 15):
        for x0 in range(0, W - lado, 15):
            n = int(((ys >= y0) & (ys < y0 + lado) & (xs >= x0) & (xs < x0 + lado)).sum())
            if n > mejor:
                mejor, caja = n, (x0, y0, x0 + lado, y0 + lado)
    # re-centrar sobre las marcas que caen dentro de esa ventana: la ventana ganadora suele
    # traer aire de un lado, y el detalle se lee mucho mejor ajustado.
    x0, y0, x1, y1 = caja
    dentro = (ys >= y0) & (ys < y1) & (xs >= x0) & (xs < x1)
    bx0, bx1 = int(xs[dentro].min()), int(xs[dentro].max())
    by0, by1 = int(ys[dentro].min()), int(ys[dentro].max())
    return (max(0, bx0 - margen), max(0, by0 - margen),
            min(W, bx1 + margen), min(H, by1 + margen))


def main():
    os.makedirs(DST, exist_ok=True)

    mapas = Image.open(FIG_MAPAS).convert("RGB")
    out = _grilla_paneles(mapas, MAPAS_FILAS, MAPAS_COLS)
    p = os.path.join(DST, "atencion_dos_regiones.png")
    out.save(p)
    print("  %-28s %s" % ("atencion_dos_regiones.png", out.size))

    mit = Image.open(FIG_MITOSIS).convert("RGB")
    reg = mit.crop((MITOSIS_COLS[0], MITOSIS_REGION2[0], MITOSIS_COLS[1], MITOSIS_REGION2[1]))
    caja = _foco_blancos(reg)
    if caja:
        zoom = reg.crop(caja)
        zoom = zoom.resize((zoom.width * 3, zoom.height * 3), Image.LANCZOS)
        zoom.save(os.path.join(DST, "mitosis_zoom.png"))
        print("  %-28s %s  (de %s)" % ("mitosis_zoom.png", zoom.size, caja))
        d = ImageDraw.Draw(reg)
        d.rectangle(caja, outline=ROJO, width=5)
    reg.save(os.path.join(DST, "mitosis_region_anotada.png"))
    print("  %-28s %s" % ("mitosis_region_anotada.png", reg.size))


if __name__ == "__main__":
    main()
