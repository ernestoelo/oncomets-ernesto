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


def hoja(filas, path):
    """Una fila por lámina, agrupadas por grado, con barra de escala y percentil impreso."""
    tile = 240
    pad, w_lab, w_pct = 10, 190, 150
    h_cab, h_pie_fila = 26, 22
    n = len(filas)
    W = w_lab + 5 * (tile + pad) + pad + w_pct
    H = pad + n * (tile + h_pie_fila + pad) + h_cab
    im = Image.new("RGB", (W, H), FONDO)
    d = ImageDraw.Draw(im)
    f_cab = fuente(15, bold=True)
    f_lab = fuente(14, bold=True)
    f_min = fuente(12)

    x0 = w_lab
    for k, txt in enumerate(["p25", "p50", "p75", "p90", "el que marcó el patólogo"]):
        cxx = x0 + k * (tile + pad)
        d.text((cxx, 4), txt, fill=TITULO if k == 4 else CUERPO, font=f_cab)
    d.text((x0 + 5 * (tile + pad) + pad, 4), "percentil de la marca", fill=CUERPO, font=f_cab)
    d.text((pad, 4), "lámina · grado", fill=CUERPO, font=f_cab)

    y = h_cab
    grado_prev = None
    for slide, grado, items, pct, n_marcas in filas:
        col = ACENTO if grado_prev is not None and grado != grado_prev else CUERPO
        if grado != grado_prev:
            d.rectangle([0, y - 3, W, y - 1], fill=SEP)
        grado_prev = grado
        d.text((pad, y + tile // 2 - 20), slide, fill=TITULO, font=f_lab)
        d.text((pad, y + tile // 2), "grado %s · %d marcas" % (grado, n_marcas),
               fill=col, font=f_min)
        for k, (rec, _lab, area_um2, es_marca) in enumerate(items):
            cxx = x0 + k * (tile + pad)
            im.paste(rec.resize((tile, tile), Image.LANCZOS), (cxx, y))
            if es_marca:
                d.rectangle([cxx - 2, y - 2, cxx + tile + 1, y + tile + 1],
                            outline=TITULO, width=3)
            d.text((cxx + 3, y + tile + 3), "%.0f µm²" % area_um2,
                   fill=TITULO if es_marca else CUERPO, font=f_min)
        # Barra de escala: 10 µm, la misma en los cinco recortes porque comparten µm/px.
        L10 = int(round(10.0 / MPP / LADO_PX0 * tile))
        bx, by = x0 + 4 * (tile + pad) + tile - L10 - 8, y + tile - 12
        d.rectangle([bx, by, bx + L10, by + 4], fill=BLANCO)
        d.rectangle([bx, by, bx + L10, by + 4], outline=TITULO, width=1)
        # Halo blanco: el rótulo en blanco a secas desaparece sobre el tejido pálido, y en
        # negro a secas desaparece sobre el oscuro. Los doce recortes son de los dos tipos.
        d.text((bx, by - 15), "10 µm", fill=TITULO, font=f_min,
               stroke_width=2, stroke_fill=BLANCO)
        d.text((x0 + 5 * (tile + pad) + pad, y + tile // 2 - 8),
               "p%.0f" % pct, fill=TITULO, font=f_lab)
        y += tile + h_pie_fila + pad
    im.save(path, optimize=True)
    return im.size


def main():
    import openslide
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(OUT))
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
    size = hoja(filas, args.out)
    print(f"  escrito: {args.out}  {size[0]}x{size[1]}")
    Path(args.out).with_suffix(".json").write_text(json.dumps(dict(
        lado_um=LADO_PX0 * MPP, mpp=MPP, percentiles=PCTS,
        poblacion="núcleos epithelial-cell de la propia lámina",
        filas=meta), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
