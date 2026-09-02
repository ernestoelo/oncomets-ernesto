"""b9_mapas_atencion_12.py — los doce mapas de atención de CLAM, con las marcas encima (B9)

Es la fotografía del número que mide `scripts/b9_atencion_12_laminas.py`: dónde cae la
atención de CLAM sobre cada una de las doce láminas anotadas, y dónde marcó mitosis el
patólogo. Va al deck como IMAGEN (excepción declarada de CLAUDE.md: es la fotografía de un
resultado, no un diagrama).

La atención se LEE del `json_out` de `sgaete`, la misma fuente que el driver, para que la
figura y el número no puedan divergir. Sus tres propiedades se declaran en el pie de la
lámina, no acá: ensemble de los cinco folds, rama de la clase PREDICHA, familia
`_pth_balance` ⇒ contaminada por construcción.

Primitivas REUSADAS, no reimplementadas (`hechos_verificados.md` §6.a):
  `percentile_scores`, `get_wsi_thumbnail`, `build_overlay_rgba`, `blend`
      de `scripts/mammoth_interpretability.py:217,229,260,293`
  el molde de mosaico y la tipografía, de `scripts/galeria_mitosis_12.py:105`

Env `clam_latest`: los `.bif` de la cohorte privada sólo abren con la `libopenslide`
parchada de 1,2 MB (workaround K).

  CUDA_VISIBLE_DEVICES="" /home/sdonoso/miniconda3/envs/clam_latest/bin/python \
      scripts/b9_mapas_atencion_12.py
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

REPO = Path("/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto")
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.mammoth_interpretability import (          # noqa: E402
    blend, build_overlay_rgba, get_wsi_thumbnail, percentile_scores,
)
from scripts.galeria_mitosis_12 import fuente           # noqa: E402
from scripts.b9_atencion_12_laminas import (            # noqa: E402
    TAREA_MITOSIS, atencion_json_out, leer_h5, paso_de_grilla,
)
from scripts.cruce_94_marcas import SLIDES              # noqa: E402

WSI_DIR = Path("/media/administrador/Storage1/sdonoso/wsi")
OUT = REPO / "sprints/B9_sprint9/presentacion_b9/assets/atencion_12_laminas.png"

# Paleta de la plantilla oficial (docs/plantilla_oficial.md §4), para que el mosaico no
# introduzca colores que el deck no tiene.
FONDO = (255, 255, 255)
CUERPO = (0x1B, 0x4F, 0x8C)
ACENTO = (0x52, 0x93, 0xDE)
BLANCO = (255, 255, 255)

# 6x2 y no 4x3: la caja de la lámina es de 12,1 x 4,3 pulgadas (relación 2,8) y una grilla
# de 4x3 sale cuadrada, así que entra limitada por el alto y desperdicia media lámina.
TILE = 420
COLS = 6
NEGRO = (0x1A, 0x1A, 0x2E)


def marca_xy(slide, coords, step):
    """Centros (en px de level 0) de los parches con `Mitosis`. Unidad: PARCHE, no marca."""
    import csv
    p = REPO / "sprints/B8_sprint8/anotaciones_patologo" / f"parches_anotados_{slide}.csv"
    xy = []
    with open(p) as fh:
        for r in csv.DictReader(fh):
            if "Mitosis" in [c.strip() for c in r["clases"].split("|")]:
                xy.append((int(r["x"]) + step / 2.0, int(r["y"]) + step / 2.0))
    return np.array(xy, dtype=np.float64).reshape(-1, 2)


def panel(slide):
    """Una lámina: mapa de atención sobre el tejido, recortado a lo que el pipeline teseló.

    El recorte al bounding box de las `coords` no es cosmético: el thumbnail completo de un
    `.bif` es sobre todo fondo, y sin recortar el tejido queda tan chico que las marcas no se
    ven. Devuelve también las marcas en coordenadas de la imagen recortada, para dibujarlas
    DESPUÉS del reescalado (a esta escala un parche de 256 px mide 3 px: dibujarlas acá las
    haría invisibles)."""
    feats, coords = leer_h5(slide)
    step = paso_de_grilla(coords)
    sc, pred, conf = atencion_json_out(slide, TAREA_MITOSIS, coords)

    thumb, scale, _mag, _w0, _h0 = get_wsi_thumbnail(WSI_DIR / slide / f"{slide}.bif")
    th, tw = thumb.shape[:2]
    ov = build_overlay_rgba(coords, percentile_scores(sc), scale, tw, th, step)
    im = Image.fromarray((blend(thumb, ov) * 255).astype(np.uint8))

    m = int(round(step * scale * 2))                      # dos parches de margen
    x0 = max(0, int(coords[:, 0].min() * scale) - m)
    y0 = max(0, int(coords[:, 1].min() * scale) - m)
    x1 = min(tw, int((coords[:, 0].max() + step) * scale) + m)
    y1 = min(th, int((coords[:, 1].max() + step) * scale) + m)
    im = im.crop((x0, y0, x1, y1))

    xy = marca_xy(slide, coords, step)
    marcas = [(cx * scale - x0, cy * scale - y0) for cx, cy in xy]
    return im, marcas, len(xy), pred, conf


def mosaico(paneles, path):
    pad = max(4, TILE // 40)
    banda = max(5, TILE // 26)
    filas = (len(paneles) + COLS - 1) // COLS
    W = COLS * (TILE + pad) + pad
    H = filas * (TILE + pad) + pad
    hoja = Image.new("RGB", (W, H), FONDO)
    d = ImageDraw.Draw(hoja)
    f = fuente(max(13, TILE // 22), bold=True)
    for i, (slide, im, marcas, n) in enumerate(paneles):
        rr, cc = divmod(i, COLS)
        x, y = pad + cc * (TILE + pad), pad + rr * (TILE + pad)
        # `contain` y no `resize`: las doce láminas tienen relaciones de aspecto distintas y
        # estirarlas cambiaría la forma del tejido, que es justo lo que la figura muestra.
        pan = Image.new("RGB", (TILE, TILE), FONDO)
        w, h = im.size
        e = min(TILE / float(w), (TILE - banda) / float(h))
        chico = im.resize((max(1, int(w * e)), max(1, int(h * e))), Image.LANCZOS)
        ox, oy = (TILE - chico.width) // 2, banda + (TILE - banda - chico.height) // 2
        # Las marcas se dibujan acá, a tamaño FIJO en píxeles de la hoja: son señales de
        # «acá marcó el patólogo», no una medida de área. Anillo oscuro por fuera del blanco
        # para que se vean sobre el rojo del mapa y sobre el fondo claro.
        dp = ImageDraw.Draw(chico)
        r = 7.0
        for mx, my in marcas:
            u, v = mx * e, my * e
            dp.ellipse([u - r - 1, v - r - 1, u + r + 1, v + r + 1], outline=NEGRO, width=4)
            dp.ellipse([u - r, v - r, u + r, v + r], outline=BLANCO, width=2)
        pan.paste(chico, (ox, oy))
        hoja.paste(pan, (x, y))
        d.rectangle([x, y, x + TILE - 1, y + banda - 1],
                    fill=CUERPO if i % 2 == 0 else ACENTO)
        txt = "%s · %d parches" % (slide, n)
        w_t = d.textlength(txt, font=f)
        d.rectangle([x, y + banda, x + w_t + 10, y + banda + f.size + 6], fill=BLANCO)
        d.text((x + 5, y + banda + 2), txt, fill=CUERPO, font=f)
    hoja.save(path, optimize=True)
    return hoja.size


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)

    paneles, meta = [], []
    for slide in SLIDES:
        im, marcas, n, pred, conf = panel(slide)
        paneles.append((slide, im, marcas, n))
        meta.append(dict(slide=slide, parches_mitosis=n, predicha=pred, confianza=conf))
        print(f"[ok] {slide}: {n} parches con Mitosis, predicha={pred} ({conf:.3f})")
    size = mosaico(paneles, args.out)
    print(f"  escrito: {args.out}  {size[0]}x{size[1]}")
    print(f"  total parches con Mitosis: {sum(m['parches_mitosis'] for m in meta)} (esperado 113)")
    (Path(args.out).with_suffix(".json")).write_text(
        json.dumps(dict(fuente="clam_ensemble/attn_batch/json_out", tarea=TAREA_MITOSIS,
                        laminas=meta), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
