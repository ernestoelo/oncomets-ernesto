"""galeria_mitosis_12.py — las dos láminas de contacto del deck del período.

Ernesto pidió ver, en el deck, **las mitosis que detecta HoVer-NeXt contra las que etiquetó
el patólogo**, y decidió mostrarlas en dos láminas: los aciertos por un lado y las falladas
por el otro. Este script arma esas dos figuras a partir de material que YA está medido.

  | figura                 | n  | qué muestra                                              |
  |------------------------|----|----------------------------------------------------------|
  | `mitosis_aciertos.png` | 26 | marca del patólogo (blanco) + detección que la acredita (amarillo) |
  | `mitosis_falladas.png` | 68 | la marca sola: no hubo detección de mitosis dentro de la tolerancia |

26 + 68 = 94 = las marcas de `Mitosis` de las doce láminas anotadas.

**No re-mide nada.** El emparejamiento húngaro uno a uno con corte a 30 µm ya está resuelto
en `results/b9_cruce_94/pares_<slide>.csv` (`cruce_94_marcas.py`, 25-ago), con el offset del
geojson ya aplicado: las columnas `x, y` y `det_x, det_y` están en coordenadas de openslide.
Acá sólo se recortan y se dibujan. Si el cruce cambia, estas figuras cambian solas.

Reglas de lectura, las mismas del cruce y por los mismos motivos:

- La unidad es **marcas** (94), no detecciones (732) ni polígonos (472).
- Las marcas son **positivos parciales**. Una detección sin marca **no es un falso positivo**
  y por eso este script **no dibuja** las detecciones que no acreditan ninguna marca: no hay
  cómo distinguir un error de una mitosis real que el patólogo no marcó.
- Las 68 de la segunda figura son **marcas que se escapan**, no errores del patólogo.

Las láminas de contacto salen a ~250 ppp sobre el ancho útil del deck (12,097"), así que el
recorte se ve con detalle aunque el `.pptx` lo escale.

Uso:
  PYTHONPATH=/media/administrador/Storage1/sdonoso/clam_testing2/.pylibs \
  /home/sdonoso/miniconda3/envs/clam_latest/bin/python scripts/galeria_mitosis_12.py
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REPO = Path(__file__).resolve().parents[1]
WSI_DIR = Path("/media/administrador/Storage1/sdonoso/wsi")
PARES = REPO / "results" / "b9_cruce_94" / "pares_%s.csv"
CSV_LAMINA = REPO / "results" / "b9_cruce_94" / "por_lamina.csv"

MPP = 0.465
LADO_PX0 = 128           # ventana de nivel 0 = 59,5 µm de lado
ESCALA = 4               # se dibuja grande (mejor antialias) y se reduce al componer

# Paleta: los dos colores son los de la galería de la 129741, y el rótulo va en el azul de
# cuerpo de la plantilla oficial (docs/plantilla_oficial.md §4).
AMARILLO = (0xFF, 0xC1, 0x07)     # detección de HoVer-NeXt
BLANCO = (255, 255, 255)          # marca del patólogo
CUERPO = (0x1B, 0x4F, 0x8C)
ACENTO = (0x52, 0x93, 0xDE)
FONDO = (255, 255, 255)

FONTS = Path("/media/administrador/Storage1/sdonoso/clam_testing2/fonts/barlow")


def fuente(px, bold=False):
    f = FONTS / ("Barlow-SemiBold.ttf" if bold else "Barlow-Regular.ttf")
    try:
        return ImageFont.truetype(str(f), px)
    except OSError:
        return ImageFont.load_default()


def orden_laminas():
    """El orden del deck: por marcas descendente, y el slide_id como desempate."""
    with open(CSV_LAMINA) as fh:
        filas = list(csv.DictReader(fh))
    filas.sort(key=lambda r: (-int(r["marcas"]), r["slide_id"]))
    return [r["slide_id"] for r in filas]


def leer_pares(slide):
    with open(str(PARES) % slide) as fh:
        return list(csv.DictReader(fh))


def recorte(sl, cx, cy, det_xy=None):
    """Recorte nativo centrado en la marca, con los círculos que correspondan.

    `read_region` con origen negativo devuelve transparente, que al pasar a RGB queda negro y
    se lee como tejido oscuro: se clampa el origen y los círculos se dibujan contra el origen
    ya clampado, así que siguen cayendo sobre el objeto."""
    L = LADO_PX0
    x0 = max(0, min(int(round(cx - L / 2)), sl.dimensions[0] - L))
    y0 = max(0, min(int(round(cy - L / 2)), sl.dimensions[1] - L))
    im = sl.read_region((x0, y0), 0, (L, L)).convert("RGB")
    im = im.resize((L * ESCALA, L * ESCALA), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    if det_xy is not None:
        u, v = (det_xy[0] - x0) * ESCALA, (det_xy[1] - y0) * ESCALA
        r = 13 * ESCALA                       # ~12 µm, el orden de un núcleo mitótico
        d.ellipse([u - r, v - r, u + r, v + r], outline=AMARILLO, width=6)
    u, v = (cx - x0) * ESCALA, (cy - y0) * ESCALA
    r = 22 * ESCALA
    d.ellipse([u - r, v - r, u + r, v + r], outline=BLANCO, width=6)
    return im


def contacto(items, cols, tile, path):
    """Grilla de recortes AGRUPADOS por lámina, en el orden del deck.

    El rótulo va una vez por grupo, sobre su primer recorte, y no en cada recorte: los grupos
    van de 1 a 15 y repetir `129741` trece veces no informa nada. Para que el límite entre
    grupos se vea sin leer los rótulos, cada grupo lleva una banda superior que alterna entre
    los dos azules de la plantilla. El rótulo dice además cuántos recortes tiene el grupo, que
    es el `n` con el que se lee cada lámina."""
    pad = max(3, tile // 40)
    banda = max(4, tile // 28)
    filas = (len(items) + cols - 1) // cols
    W = cols * (tile + pad) + pad
    H = filas * (tile + pad) + pad
    hoja = Image.new("RGB", (W, H), FONDO)
    d = ImageDraw.Draw(hoja)
    f_lab = fuente(max(12, tile // 11), bold=True)

    grupos = []                     # (slide, i_inicial, n) en el orden en que aparecen
    for i, (slide, _) in enumerate(items):
        if not grupos or grupos[-1][0] != slide:
            grupos.append([slide, i, 0])
        grupos[-1][2] += 1
    inicio = {g[1]: (g[0], g[2]) for g in grupos}
    tono = {g[0]: (CUERPO if k % 2 == 0 else ACENTO) for k, g in enumerate(grupos)}

    for i, (slide, im) in enumerate(items):
        r, c = divmod(i, cols)
        x, y = pad + c * (tile + pad), pad + r * (tile + pad)
        hoja.paste(im.resize((tile, tile), Image.LANCZOS), (x, y))
        d.rectangle([x, y, x + tile - 1, y + banda - 1], fill=tono[slide])
        if i in inicio:
            txt = "%s · %d" % inicio[i]
            w_t = d.textlength(txt, font=f_lab)
            h_t = f_lab.size + 5
            d.rectangle([x, y + tile - h_t, x + w_t + 9, y + tile], fill=BLANCO)
            d.text((x + 5, y + tile - h_t - 1), txt, fill=CUERPO, font=f_lab)
    hoja.save(path)
    return hoja.size


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(REPO / "sprints/B9_sprint9/presentacion_b9/assets"))
    ap.add_argument("--ancho-px", type=int, default=3000,
                    help="ancho de la lámina de contacto; 3000 px sobre 12,097\" ~ 250 ppp")
    a = ap.parse_args()

    import openslide

    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    aciertos, falladas = [], []
    for slide in orden_laminas():
        pares = leer_pares(slide)
        wsi = WSI_DIR / slide / ("%s.bif" % slide)
        sl = openslide.OpenSlide(str(wsi))
        try:
            for p in pares:
                cx, cy = float(p["x"]), float(p["y"])
                if p["acreditada"] == "True":
                    aciertos.append((slide, recorte(sl, cx, cy,
                                                    (float(p["det_x"]), float(p["det_y"])))))
                else:
                    falladas.append((slide, recorte(sl, cx, cy)))
        finally:
            sl.close()
        print("  %-11s %2d marcas -> %2d acreditadas" %
              (slide, len(pares), sum(1 for p in pares if p["acreditada"] == "True")))

    assert len(aciertos) + len(falladas) == 94, "no son las 94 marcas"
    assert len(aciertos) == 26, "no son los 26 aciertos del cruce"

    for nombre, items, cols in (("mitosis_aciertos", aciertos, 9),
                                ("mitosis_falladas", falladas, 15)):
        tile = a.ancho_px // cols
        p = out / ("%s.png" % nombre)
        wh = contacto(items, cols, tile, p)
        print("  %s: %d recortes, %d x %d px" % (p.name, len(items), wh[0], wh[1]))


if __name__ == "__main__":
    main()
