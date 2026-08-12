#!/usr/bin/env python
"""prep_assets_papers.py — extrae del PDF la figura de cada uno de los cuatro papers.

Los cuatro son los que Sebastián puso sobre la mesa para la reunión del 12-ago: los dos que
salieron de nuestra búsqueda del 2-ago (PU learning y ZoomMIL, la rama de mitosis) y los dos
que trajo él el 6-ago (NPKC-MIL y el de pleomorfismo nuclear, la rama de grado nuclear).

Receta, la misma que se usó ad-hoc para la Fig. 2 de SI-MIL en el deck del B8, versionada acá
por primera vez:

    pdftoppm -f <pág> -l <pág> -r 400 -png <paper>.pdf <salida>

y después recorte con PIL. Las cajas se **midieron una vez** sobre esos rasterizados y quedan
explícitas como constantes: un detector automático corriendo en cada regeneración es una
fuente de sorpresas silenciosas. `_caja_por_contenido()` está para PROPONER la caja la primera
vez (y para re-proponerla si algún día cambia un PDF), no para decidirla en cada corrida.

La única figura que no se recorta entera es la de PU learning, que es una grilla de cuatro
métodos por tres parches. Completa no se lee proyectada, así que se recompone con las tres
columnas que sostienen el argumento (la anotación de referencia, el baseline y el método
propuesto) y las dos filas de las flechas negras. Lo que se deja afuera va dicho en el pie de
la lámina, que es donde tiene que estar.

Salidas, todas en `assets/`:
  fig_pulearning.png   Fig. 1 de Zhao et al. (pág. 14), recompuesta a 3 columnas x 2 filas
  fig_zoommil.png      Fig. 1 de Thandiackal et al. (pág. 2), entera
  fig_npkcmil.png      Fig. 1 de Wang y Yuan (pág. 3 del paper, 4 del PDF), entera
  fig_pleomorfismo.png Fig. 1 de Mercan et al. (pág. 2), entera

Uso:
  PYTHONPATH=/media/administrador/Storage1/sdonoso/clam_testing2/.pylibs \
  /home/sdonoso/miniconda3/envs/clam_latest/bin/python \
    sprints/B8_sprint8/presentacion_papers_mitosis/prep_assets_papers.py
"""
import os
import subprocess
import tempfile

import numpy as np
from PIL import Image

REPO = "/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto"
GEO = os.path.join(REPO, "sprints/B8_sprint8/tareas_geometricas")
NUEVOS = os.path.join(REPO, "sprints/B8_sprint8/papers_11_agosto")
DST = os.path.join(REPO, "sprints/B8_sprint8/presentacion_papers_mitosis/assets")

DPI = 400
MARGEN = 14          # aire blanco alrededor del recorte, en px
BLANCO = (255, 255, 255)

# --- los cuatro PDF y la página de su figura (verificada por texto, no por memoria) ---
PDF_PU = os.path.join(GEO, "pulearning_zhao2022_melba.pdf")
PDF_ZM = os.path.join(GEO, "zoommil_thandiackal2022.pdf")
PDF_NP = os.path.join(NUEVOS, "NPKC-MIL1-s2.0-S2589004224010484-main.pdf")
PDF_PL = os.path.join(NUEVOS, "Pleomorfismo nuclear s41523-022-00488-w.pdf")

PAG_PU, PAG_ZM, PAG_NP, PAG_PL = 14, 2, 4, 2

# --- cajas medidas sobre el rasterizado a 400 DPI, en píxeles (x0, y0, x1, y1) ---
CAJA_ZM = (402, 411, 2989, 1366)     # Fig. 1 entera, con los rótulos (a) a (d)
CAJA_NP = (790, 576, 2558, 1828)     # Fig. 1 entera, con su marco punteado azul
CAJA_PL = (778, 331, 2583, 897)      # Fig. 1 entera, con los tres rótulos al pie

# --- geometría de la grilla de PU learning, medida sobre la misma página ---
# El separador entre columnas es una banda blanca de 2 a 3 px; las filas de imagen se
# distinguen de las de texto porque están cubiertas de rosa de punta a punta.
PU_COLS = [(518, 1108), (1108, 1690), (2276, 2864)]   # Full Annotation · Baseline · Propuesto
# El corte de abajo va 8 px ANTES de donde arranca la tercera fila de parches: a ras deja
# asomar una tira rosa de la fila que se descarta, y en la lámina se lee como un defecto.
PU_FILA = (514, 1931)                # rótulos de columna + las dos primeras filas de parches
PU_SEP = 26                          # aire entre columnas al recomponer, en px


def _pagina(pdf, pagina, dpi=DPI):
    """Rasteriza UNA página a `dpi` y la devuelve como imagen RGB."""
    with tempfile.TemporaryDirectory() as tmp:
        base = os.path.join(tmp, "p")
        subprocess.run(["pdftoppm", "-f", str(pagina), "-l", str(pagina),
                        "-r", str(dpi), "-png", pdf, base], check=True)
        salida = [f for f in os.listdir(tmp) if f.endswith(".png")]
        return Image.open(os.path.join(tmp, salida[0])).convert("RGB")


def _caja_por_contenido(im, busqueda, umbral=245):
    """PROPONE la caja de la tinta dentro de `busqueda`. No se usa en la corrida normal.

    Está para medir una caja la primera vez, o para volver a medirla si algún PDF cambia:
    se imprime, se mira, y el valor se congela a mano en las constantes de arriba."""
    a = np.array(im.convert("L").crop(busqueda))
    tinta = a < umbral
    fil = np.nonzero(tinta.any(axis=1))[0]
    col = np.nonzero(tinta.any(axis=0))[0]
    if not len(fil):
        return None
    return (busqueda[0] + int(col.min()), busqueda[1] + int(fil.min()),
            busqueda[0] + int(col.max()) + 1, busqueda[1] + int(fil.max()) + 1)


def _recorte(im, caja, margen=MARGEN):
    """Recorta con un borde blanco alrededor, para que la figura no toque su propio canto."""
    x0, y0, x1, y1 = caja
    out = Image.new("RGB", (x1 - x0 + 2 * margen, y1 - y0 + 2 * margen), BLANCO)
    out.paste(im.crop(caja), (margen, margen))
    return out


def _columnas_pu(im, cols=PU_COLS, fila=PU_FILA, sep=PU_SEP, margen=MARGEN):
    """Recompone la grilla de PU learning con las columnas elegidas, pegadas y sin el hueco.

    Se conservan los rótulos de columna de arriba y los recuentos TP/FP al pie de cada fila:
    son los que convierten la figura en un argumento y no en tres fotos de tejido."""
    y0, y1 = fila
    tiras = [im.crop((x0, y0, x1, y1)) for x0, x1 in cols]
    ancho = sum(t.width for t in tiras) + sep * (len(tiras) - 1)
    out = Image.new("RGB", (ancho + 2 * margen, (y1 - y0) + 2 * margen), BLANCO)
    x = margen
    for t in tiras:
        out.paste(t, (x, margen))
        x += t.width + sep
    return out


def main():
    os.makedirs(DST, exist_ok=True)

    def guarda(img, nombre):
        p = os.path.join(DST, nombre)
        img.save(p)
        print("  %-24s %s  ar %.2f" % (nombre, img.size, img.width / img.height))

    guarda(_columnas_pu(_pagina(PDF_PU, PAG_PU)), "fig_pulearning.png")
    guarda(_recorte(_pagina(PDF_ZM, PAG_ZM), CAJA_ZM), "fig_zoommil.png")
    guarda(_recorte(_pagina(PDF_NP, PAG_NP), CAJA_NP), "fig_npkcmil.png")
    guarda(_recorte(_pagina(PDF_PL, PAG_PL), CAJA_PL), "fig_pleomorfismo.png")


if __name__ == "__main__":
    main()
