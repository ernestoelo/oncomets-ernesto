"""prep_assets_paper_hovernext.py — la Figura 1 del paper de HoVer-NeXt, para el deck.

Ernesto pidió (`correcciones.txt`) reemplazar la lámina de estado de la herramienta por
«la figura del diagrama original del paper». Es una figura EXTERNA de un paper, o sea la
excepción explícita a «todo nativo» del deck (CLAUDE.md, ADDENDUM B5 14-jun).

Se toman los paneles A (la tubería de inferencia sobre la lámina entera), B (la
arquitectura de un codificador y dos decodificadores) y C (el cosido de los mosaicos). Se
deja fuera el panel D, que son las distribuciones de clase de los dos conjuntos de
entrenamiento: es del paper, no de lo que corrimos, y compite por el alto.

El recorte se hace por FRACCIÓN de página y después se ajusta al contenido con un recorte
por umbral, para que un cambio de dpi no lo rompa.

Uso:
  PYTHONPATH=/media/administrador/Storage1/sdonoso/clam_testing2/.pylibs \
  /home/sdonoso/miniconda3/envs/clam_latest/bin/python \
    sprints/B8_sprint8/presentacion_b8/prep_assets_paper_hovernext.py
"""
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

REPO = Path("/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto")
PDF = REPO / "sprints/B8_sprint8/hover_next.pdf"
DST = REPO / "sprints/B8_sprint8/presentacion_b8/assets"

PAGINA = 3          # Figure 1 del paper (p. 63 de la numeración de la revista)
DPI = 400
CAJA = (0.150, 0.268, 0.840, 0.601)   # A+B+C, sin el panel D ni la leyenda


def main():
    DST.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        pre = str(Path(td) / "pg")
        subprocess.run(["pdftoppm", "-f", str(PAGINA), "-l", str(PAGINA), "-r", str(DPI),
                        "-png", str(PDF), pre], check=True)
        png = sorted(Path(td).glob("pg*.png"))[0]
        im = Image.open(png).convert("RGB")

    W, H = im.size
    c = im.crop((int(CAJA[0] * W), int(CAJA[1] * H), int(CAJA[2] * W), int(CAJA[3] * H)))
    a = np.asarray(c.convert("L"))
    fil = np.where(a.min(axis=1) < 235)[0]
    col = np.where(a.min(axis=0) < 235)[0]
    c = c.crop((col.min() - 6, fil.min() - 6, col.max() + 7, fil.max() + 7))

    p = DST / "hovernext_paper_fig1.png"
    c.save(p)
    print("  %-30s %s  (razón %.2f)" % (p.name, c.size, c.width / c.height))


if __name__ == "__main__":
    main()
