"""Recorta los assets de la sección de regiones de escaneo (deck del 19-ago).

Dos cosas y nada más:

1. Las dos regiones de escaneo de la 129741. Los PNG de origen traen una banda negra
   de 59 px a la izquierda, idéntica en las dos, que es margen vacío del propio escaneo
   y en pantalla se lee como un defecto de la figura. Se recorta el MISMO número de
   columnas en las dos para no romper la correspondencia, y se conserva el alto entero:
   las dos regiones están al mismo downsample (64), así que dibujadas al mismo ALTO
   quedan a la misma escala y la comparación que la lámina propone es legítima.

2. La figura de registro a level 0 de la 129741, que es la evidencia de §2.d. Se saca
   de git (`HEAD`) y no del árbol, porque el re-barrido en curso movió el archivo del
   árbol a su propio subdirectorio y el que vale para el deck es el medido el 14-ago,
   que es el que el documento cita.

Los tres pasan por `sin_icc()`. Los PNG que salen del pipeline traen un perfil de color
enorme, y el Pillow que usa python-pptx lo rechaza al insertar la imagen: el build muere
con «Decompressed data too large». Se descarta el perfil al reescribir; son figuras en
escala de grises o miniaturas de tejido, así que no cambia lo que se ve.

Uso:
  PYTHONPATH=/media/administrador/Storage1/sdonoso/clam_testing2/.pylibs \
  /home/sdonoso/miniconda3/envs/clam_latest/bin/python prep_assets_regiones.py
"""
import io
import os
import subprocess

from PIL import Image, PngImagePlugin

# los PNG de origen traen un perfil ICC grande y Pillow lo rechaza con el tope por defecto
PngImagePlugin.MAX_TEXT_CHUNK = 100 * 1024 * 1024

REPO = "/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto"
SRC = os.path.join(REPO, "sprints/B8_sprint8/anotaciones_patologo/regiones_escaneo")
ASSETS = os.path.join(REPO, "sprints/B8_sprint8/presentacion_b8/assets")

BANDA_NEGRA = 59          # medido: idéntica en las dos regiones


def sin_icc(im):
    """Copia sin metadatos: el perfil de color viaja en `info` y sobrevive a un crop."""
    limpia = Image.new(im.mode, im.size)
    limpia.putdata(list(im.getdata()))
    return limpia


def recorta_regiones():
    for n in (0, 1):
        src = os.path.join(SRC, "129741_region%d.png" % n)
        im = Image.open(src).convert("RGB")
        w, h = im.size
        out = sin_icc(im.crop((BANDA_NEGRA, 0, w, h)))
        dst = os.path.join(ASSETS, "region%d_129741.png" % n)
        out.save(dst)
        print("  region %d: %s -> %s  (ar %.4f)"
              % (n, im.size, out.size, out.size[0] / out.size[1]))


def saca_registro_de_git():
    rel = "sprints/B8_sprint8/anotaciones_patologo/regiones_escaneo/129741_registro_level0.png"
    dst = os.path.join(ASSETS, "registro_level0_129741.png")
    blob = subprocess.run(["git", "-C", REPO, "show", "HEAD:" + rel],
                          capture_output=True, check=True).stdout
    im = sin_icc(Image.open(io.BytesIO(blob)).convert("RGB"))
    im.save(dst)
    print("  registro level 0: %s  (ar %.4f)" % (im.size, im.size[0] / im.size[1]))


if __name__ == "__main__":
    os.makedirs(ASSETS, exist_ok=True)
    recorta_regiones()
    saca_registro_de_git()
