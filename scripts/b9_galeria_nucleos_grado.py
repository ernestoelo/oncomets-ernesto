"""b9_galeria_nucleos_grado.py — el núcleo marcado contra su propia lámina (B9)

Lo que pidió Ernesto tras la reunión del 1-sep: ver el TAMAÑO RELATIVO que hay detrás del
percentil del eje del grado nuclear. El número dice «el núcleo marcado está en el percentil
96 de su lámina»; esta figura lo muestra.

Una fila por lámina (las doce declaran exactamente un grado cada una, verificado sobre
`results/b9_nucleos/marcas_grado.csv`), agrupadas por grado. En cada fila, cuatro núcleos de
la propia lámina en los percentiles 25, 50, 75 y 90 de área, y al final el núcleo que el
patólogo marcó. **Todos al mismo µm por píxel** y con barra de escala, que es lo único que
vuelve comparable un tamaño.

Dos cosas que el pie de la lámina tiene que decir, y por eso el script las respeta:

  - Lo que se dibuja es el **núcleo segmentado por HoVer-NeXt** bajo la marca, no el polígono
    del patólogo: el área de ese polígono es en parte el pincel de QuPath
    ([[anotacion-tamano-objeto-vs-region]]).
  - El área absoluta **no se compara entre clases** de HoVer-NeXt, porque su umbral está
    afinado por clase ([[descriptor-absoluto-trae-el-umbral]]). Por eso la escalera de
    percentiles se construye SÓLO sobre la población epitelial, que es la misma contra la
    que se calculó `pct_area_um2`.

Env `clam_latest`: los `.bif` sólo abren con la `libopenslide` parchada (workaround K).

  CUDA_VISIBLE_DEVICES="" /home/sdonoso/miniconda3/envs/clam_latest/bin/python \
      scripts/b9_galeria_nucleos_grado.py
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw

REPO = Path("/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto")
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.galeria_mitosis_12 import fuente          # noqa: E402

WSI_DIR = Path("/media/administrador/Storage1/sdonoso/wsi")
NUC = REPO / "results/b9_nucleos"
OUT = REPO / "sprints/B9_sprint9/presentacion_b9/assets/nucleos_grado.png"

MPP = 0.465                 # µm/px, cohorte privada a level 0
EPITELIAL = 2               # `hover_next_reference/src/constants.py:31-39`
LADO_PX0 = 64               # 29,8 µm de lado: un núcleo de 12 µm ocupa el 40 % del recorte
ESCALA = 6                  # sobremuestreo del recorte, para que el borde no se vea dentado
PCTS = [25, 50, 75, 90]

FONDO = (255, 255, 255)
TITULO = (0x1A, 0x1A, 0x2E)
CUERPO = (0x1B, 0x4F, 0x8C)
ACENTO = (0x52, 0x93, 0xDE)
SEP = (0x9A, 0xA3, 0xB4)
BLANCO = (255, 255, 255)
ORDEN_GRADO = {"bajo": 0, "moderado": 1, "alto": 2}


def recorte(sl, cx, cy, anillo=None):
    """Recorte nativo centrado en el núcleo. El origen se clampa: `read_region` con origen
    negativo devuelve transparente, que en RGB queda negro y se lee como tejido oscuro."""
    L = LADO_PX0
    x0 = max(0, min(int(round(cx - L / 2)), sl.dimensions[0] - L))
    y0 = max(0, min(int(round(cy - L / 2)), sl.dimensions[1] - L))
    im = sl.read_region((x0, y0), 0, (L, L)).convert("RGB")
    im = im.resize((L * ESCALA, L * ESCALA), Image.LANCZOS)
    if anillo is not None:
        d = ImageDraw.Draw(im)
        u, v = (cx - x0) * ESCALA, (cy - y0) * ESCALA
        r = 15 * ESCALA
        d.ellipse([u - r, v - r, u + r, v + r], outline=anillo, width=5)
    return im


def poblacion_epi(slide):
    """Los núcleos epiteliales de la lámina, con su área en µm². Es la misma población contra
    la que `marcas_grado.csv` calculó `pct_area_um2` (columna `n_pobl_epi`)."""
    z = np.load(NUC / f"{slide}_nucleos.npz")
    sel = z["clase"] == EPITELIAL
    return (z["cx"][sel].astype(np.float64), z["cy"][sel].astype(np.float64),
            z["area_px"][sel].astype(np.float64) * (MPP ** 2))


def fila_de(slide, marcas, sl):
    """Los cuatro percentiles de la lámina más el núcleo marcado, en un solo renglón."""
    cx, cy, area = poblacion_epi(slide)
    items = []
    for p in PCTS:
        objetivo = np.percentile(area, p)
        i = int(np.argmin(np.abs(area - objetivo)))
        items.append((recorte(sl, cx[i], cy[i]), "p%d" % p, area[i], False))

    # Representante: la marca de MEDIANA `pct_area_um2` de la lámina, restringida a las que
    # HoVer-NeXt clasificó como epitelio (las 22 restantes son de otras clases y su área no
    # es comparable contra esta escalera).
    m = marcas[marcas["clase_hovernext"] == "epithelial-cell"]
    if m.empty:
        m = marcas
    j = (m["pct_area_um2"] - m["pct_area_um2"].median()).abs().idxmin()
    r = m.loc[j]
    items.append((recorte(sl, r["x"], r["y"], anillo=BLANCO), "marcado", r["area_um2"], True))
    return items, float(r["pct_area_um2"]), len(marcas), str(r["grado"])


def hoja(filas, path, n_col=2):
    """Las láminas en `n_col` columnas, agrupadas por grado, con barra de escala y percentil.

    Dos columnas y no una: apiladas, las doce filas dan aspecto 0,48 y en una lámina apaisada
    el PNG queda de unas dos pulgadas de ancho, ilegible. Con dos columnas de seis el aspecto
    pasa a 1,9 y **se conservan las doce láminas**, que es lo que Ernesto decidió el 2-sep
    frente a la alternativa de dejar tres filas (una por grado) y perder nueve. Con `n_col=3`
    (D5, ejecutado el 4-sep) son cuatro filas de tres y se conservan igual.

    **Las fuentes están dimensionadas para la lámina, no para el PNG.** El rótulo va quemado,
    así que lo que el público ve es `px * ancho_en_pulgadas * 72 / W`. La caja de la lámina 12
    mide 12,097 x 3,577" (aspecto 3,38), y con n_col=3 la figura entra limitada por el ANCHO,
    así que el denominador es W. Con 15/14/12 px sobre W=4880 los rótulos daban 2,3 pt, muy
    bajo el mínimo de 7 pt del template ([[png-rotulos-quemados-pierden-pt]]).

    Subir la fuente **no alcanza**, y ésta es la trampa: a 45 px `el que marcó el patólogo`
    mide 481 px en una lane de 250 y `grado moderado · 10 marcas` 434 en una de 190, así que
    hay que ensanchar las lanes; pero ensancharlas agranda W, que es el denominador, y el
    punto fijo converge en un recorte MÁS CHICO que el de partida (0,518" contra 0,515").
    Por eso los rótulos se **acortan** en vez de crecer las lanes: la cabecera del quinto tile
    y la de la lane van a dos líneas, `percentil de la marca` queda en `percentil`, y el grado
    se separa de las marcas. Con eso el punto fijo cierra en 47/44/42 px sobre W=5171, o sea
    7,9 / 7,4 / 7,1 pt, con el recorte en 0,561" (contra 0,515" de las dos columnas).

    Si se cambia un rótulo o una lane hay que rehacer la cuenta: la condición que sostiene los
    7,9 pt es que W/H siga por encima de 3,38, o la figura pasa a estar limitada por el alto y
    el denominador deja de ser W.
    """
    tile = 240
    pad, w_lab, w_pct = 10, 237, 200
    h_cab, h_pie_fila, gap = 124, 56, 40
    n = len(filas)
    n_fil = -(-n // n_col)                        # ceil
    w_col = w_lab + 5 * (tile + pad) + pad + w_pct
    W = n_col * w_col + (n_col - 1) * gap
    H = pad + n_fil * (tile + h_pie_fila + pad) + h_cab
    im = Image.new("RGB", (W, H), FONDO)
    d = ImageDraw.Draw(im)
    f_cab = fuente(47, bold=True)
    f_lab = fuente(44, bold=True)
    f_min = fuente(42)

    # La cabecera se repite en CADA columna: sin eso, la columna de la derecha son cinco
    # recortes sin decir de qué percentil es cada uno. Las de dos líneas van así porque a
    # 47 px no entran en el ancho de un tile: `el que marcó el patólogo` mide 547 px de 250.
    h_ln = int(f_cab.size * 1.25)
    for c in range(n_col):
        xc = c * (w_col + gap)
        x0 = xc + w_lab
        for k, txt in enumerate(["p25", "p50", "p75", "p90"]):
            d.text((x0 + k * (tile + pad), 4), txt, fill=CUERPO, font=f_cab)
        for j, txt in enumerate(["marcado", "patólogo"]):
            d.text((x0 + 4 * (tile + pad), 4 + j * h_ln), txt, fill=TITULO, font=f_cab)
        d.text((x0 + 5 * (tile + pad) + pad, 4), "percentil", fill=CUERPO, font=f_cab)
        for j, txt in enumerate(["lámina", "grado"]):
            d.text((xc + pad, 4 + j * h_ln), txt, fill=CUERPO, font=f_cab)

    grado_prev = None
    for i, (slide, grado, items, pct, n_marcas) in enumerate(filas):
        xc = (i // n_fil) * (w_col + gap)
        x0 = xc + w_lab
        y = h_cab + (i % n_fil) * (tile + h_pie_fila + pad)
        col = ACENTO if grado_prev is not None and grado != grado_prev else CUERPO
        # El filete separa GRADOS en el orden de lectura, que es por columnas: la primera
        # fila de la columna 2 continúa el grado de la última de la 1 y por eso no lleva
        # filete. Va ancho de columna, no ancho de hoja.
        if grado != grado_prev:
            d.rectangle([xc, y - 3, xc + w_col, y - 1], fill=SEP)
        grado_prev = grado
        # Tres líneas y no dos: `grado moderado · 10 marcas` mide 434 px a 42 px de fuente y
        # la lane son 237. El «grado» que pierde el sub-rótulo lo pone la cabecera de la lane,
        # y el filete de arriba sigue marcando dónde cambia.
        h_rot = int(f_lab.size * 1.20)
        y_rot = y + tile // 2 - h_rot - int(f_min.size * 0.60)
        d.text((xc + pad, y_rot), slide, fill=TITULO, font=f_lab)
        d.text((xc + pad, y_rot + h_rot), grado, fill=col, font=f_min)
        d.text((xc + pad, y_rot + h_rot + int(f_min.size * 1.20)),
               "%d marcas" % n_marcas, fill=col, font=f_min)
        for k, (rec, _lab, area_um2, es_marca) in enumerate(items):
            cxx = x0 + k * (tile + pad)
            im.paste(rec.resize((tile, tile), Image.LANCZOS), (cxx, y))
            if es_marca:
                d.rectangle([cxx - 2, y - 2, cxx + tile + 1, y + tile + 1],
                            outline=TITULO, width=3)
            d.text((cxx + 3, y + tile + 3), "%.0f µm²" % area_um2,
                   fill=TITULO if es_marca else CUERPO, font=f_min)
        # Barra de escala: 10 µm, la misma en los cinco recortes porque comparten µm/px.
        # Va en el PRIMER recorte y no en el marcado: con la fuente dimensionada para la
        # lámina, el rótulo mide el doble que antes y sobre el quinto chocaba con el anillo.
        # El p25 es el único de la fila que nunca lleva anillo.
        L10 = int(round(10.0 / MPP / LADO_PX0 * tile))
        bx, by = x0 + tile - L10 - 8, y + tile - 12
        d.rectangle([bx, by, bx + L10, by + 4], fill=BLANCO)
        d.rectangle([bx, by, bx + L10, by + 4], outline=TITULO, width=1)
        # Halo blanco: el rótulo en blanco a secas desaparece sobre el tejido pálido, y en
        # negro a secas desaparece sobre el oscuro. Los doce recortes son de los dos tipos.
        d.text((bx, by - f_min.size - 4), "10 µm", fill=TITULO, font=f_min,
               stroke_width=2, stroke_fill=BLANCO)
        d.text((x0 + 5 * (tile + pad) + pad, y + tile // 2 - 8),
               "p%.0f" % pct, fill=TITULO, font=f_lab)
    im.save(path, optimize=True)
    return im.size


def main():
    import openslide
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--n-col", type=int, default=3,
                    help="columnas de la hoja; 3 es lo que se entrega (D5), 2 el layout viejo")
    args = ap.parse_args()
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)

    mg = pd.read_csv(NUC / "marcas_grado.csv")
    filas, meta = [], []
    # Las doce declaran un grado cada una; el orden es bajo -> moderado -> alto, y dentro de
    # cada grado por número de marcas descendente.
    llaves = (mg.groupby(["slide", "grado"]).size().reset_index(name="n")
                .sort_values(["grado", "n"], key=lambda s: s.map(ORDEN_GRADO)
                             if s.name == "grado" else -s))
    for _, k in llaves.iterrows():
        slide, grado = k["slide"], k["grado"]
        sl = openslide.OpenSlide(str(WSI_DIR / slide / f"{slide}.bif"))
        items, pct, n_m, _g = fila_de(slide, mg[mg["slide"] == slide], sl)
        sl.close()
        filas.append((slide, grado, items, pct, n_m))
        meta.append(dict(slide=slide, grado=grado, n_marcas=int(n_m), pct_representante=pct))
        print(f"[ok] {slide}: grado {grado}, {n_m} marcas, representante p{pct:.0f}")
    size = hoja(filas, args.out, n_col=args.n_col)
    print(f"  escrito: {args.out}  {size[0]}x{size[1]}")
    Path(args.out).with_suffix(".json").write_text(json.dumps(dict(
        lado_um=LADO_PX0 * MPP, mpp=MPP, percentiles=PCTS,
        poblacion="núcleos epithelial-cell de la propia lámina",
        filas=meta), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
