"""Recolorea el recuadro del crop de contexto a la paleta Deep-LLM-V.

`render_multiscale_crop.py` (B6) dibuja el recuadro del campo fino con PIL en el naranja
de B4, (226,114,59) = #E2723B. Al migrar el deck B7 al template Deep-LLM-V el esquema
nativo de al lado pasó a marcar ese mismo campo en teal, y la lámina quedaba diciendo dos
colores para una sola cosa.

El recuadro se dibuja SIN antialias, así que sus píxeles son ese RGB exacto y se pueden
sustituir sin tocar el tejido: en context_512um.png son 1552 px que forman un anillo
cuadrado limpio (y180-280, x180-280). En fine_112um.png no hay ninguno — el recuadro solo
va sobre la imagen de contexto.

La salida se escribe en assets/ del deck B7, NO sobre el asset compartido de
assets_branding/: ese lo usa también el deck B6, que sigue en la paleta vieja.

Uso:
    PYTHONPATH=/media/administrador/Storage1/sdonoso/clam_testing2/.pylibs \
      /home/sdonoso/miniconda3/envs/clam_latest/bin/python recolor_crop_box.py
"""
import os

import numpy as np
from PIL import Image

REPO = "/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto"
SRC = os.path.join(REPO, "papers/presentations/assets_branding/multiscale_crop/context_512um.png")
DST = os.path.join(REPO, "sprints/B7_sprint7/presentacion_b7/assets/context_512um_onco.png")

ORA = (226, 114, 59)      # #E2723B, el naranja de B4 que usa render_multiscale_crop.py
ONCO_DARK = (62, 104, 119)  # #3E6877, el bloque de proceso del template


def main():
    a = np.array(Image.open(SRC).convert("RGB"))
    m = (a[:, :, 0] == ORA[0]) & (a[:, :, 1] == ORA[1]) & (a[:, :, 2] == ORA[2])
    if not m.any():
        raise SystemExit(f"No se encontró el recuadro {ORA} en {SRC}")
    a[m] = ONCO_DARK
    os.makedirs(os.path.dirname(DST), exist_ok=True)
    Image.fromarray(a).save(DST)
    print(f"Guardado: {DST} · {int(m.sum())} px recoloreados")


if __name__ == "__main__":
    main()
