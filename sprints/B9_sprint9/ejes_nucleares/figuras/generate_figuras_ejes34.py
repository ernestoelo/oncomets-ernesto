#!/usr/bin/env python
"""generate_figuras_ejes34.py — las cuatro figuras de los ejes nucleares, solas.

**Envoltorio delgado.** Desde el 28-ago las cuatro láminas viven en el generador del deck
(`presentacion_b9/generate_b9_deck.py`), que es donde ya vivían las otras siete y todas las
primitivas. Antes la dependencia iba al revés y este archivo importaba de allá; con las
láminas incorporadas al deck eso habría sido un ciclo, y correr el deck como `__main__` habría
cargado una segunda copia de su módulo.

Lo que queda acá es una **hoja de cuatro láminas** para iterar el QA visual de las figuras sin
reconstruir el deck entero. Mismo código, mismos números, mismo guion: la única diferencia es
que no trae ni la portada ni las láminas de mitosis.

**No escribe `numeros_figuras.csv`.** Ese CSV lo escribe el deck, que pasa a ser la única
fuente. Si tocás una figura, el número versionado se actualiza corriendo el deck, no esto.

Uso:
    PYTHONPATH=/media/administrador/Storage1/sdonoso/clam_testing2/.pylibs \
      /home/sdonoso/miniconda3/envs/pruebas/bin/python generate_figuras_ejes34.py

(`envs/pruebas` es el único con zarr y pandas juntos, y `b9_pleomorfismo` importa zarr al
tope; `.pylibs` aporta python-pptx. Workaround B: binario absoluto.)
"""
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(AQUI, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "sprints", "B9_sprint9", "presentacion_b9"))

from generate_b9_deck import (TPL, auditar, barrer_rayas, borrar_slide,   # noqa: E402
                              clonar_s03, datos_eje3, datos_eje4, forzar_barlow,
                              lamina_f1, lamina_f2, lamina_f3, lamina_f4, leer_guion)
from pptx import Presentation                                            # noqa: E402

OUT = os.path.join(AQUI, "figuras_ejes_3_4.pptx")


def main():
    d4 = datos_eje4()
    d3 = datos_eje3()
    R = d3["restringida"]
    guion, _ = leer_guion()          # el guion del deck, para no tener dos textos
    print("Figuras de los ejes nucleares · hoja suelta, no toca el deck")
    print("  eje 4: %d regiones (%d epi / %d estroma), AUC %.3f, p %.4f"
          % (d4["n_reg"], d4["n_epi"], d4["n_est"], d4["obs"], d4["p"]))
    print("  eje 3: %d marcas en %d láminas, rho %.3f, p exacto %.4f sobre %d asignaciones"
          % (R["n_marcas"], R["n_lam"], R["rho"], R["p_bi"], R["k"]))

    prs = Presentation(TPL)
    s01, s02, s03, s04 = list(prs.slides)
    sA, sB, sC, sD = [clonar_s03(prs, s03) for _ in range(4)]
    lamina_f1(sA, d4, guion["s03d"])
    lamina_f2(sB, d4, guion["s03e"])
    lamina_f3(sC, d3, guion["s03f"])
    lamina_f4(sD, d3, guion["s03g"])
    for viejo in (s01, s02, s03, s04):
        borrar_slide(prs, viejo)                # es una hoja de figuras, no un deck

    forzar_barlow(prs)
    problemas = auditar(prs, saltar_idx=())
    problemas += barrer_rayas(prs, saltar_idx=())
    prs.save(OUT)
    print("  escrito: %s" % os.path.basename(OUT))
    return 1 if problemas else 0


if __name__ == "__main__":
    sys.exit(main())
