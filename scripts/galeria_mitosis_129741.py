"""galeria_mitosis_129741.py — encargo 2: las imágenes de las 177 detecciones.

Sebastián pidió ver «el resto de las mitosis» (las 177 − 13 = 164 detecciones que no
acreditaron ninguna marca) para comprobar si se parecen entre sí. Se arman tres láminas de
contacto, a resolución nativa, con los recortes **ordenados por parecido**:

  | bloque                | n   | qué muestra                                            |
  |-----------------------|-----|--------------------------------------------------------|
  | detecciones sin marca | 164 | el inventario que pidió Sebastián                      |
  | detecciones acertadas |  13 | con la marca del patólogo dibujada encima              |
  | marcas que se escapan |  13 | centrado en la marca; no hay detección de mitosis cerca|

164 + 13 = 177 = las filas de `pred_mitosis.tsv`. El bloque de las falladas es el que más
informa, porque es el único que muestra en qué se equivoca el detector.

**Las 164 NO son falsos positivos.** Las marcas del patólogo son positivos parciales
([[anotaciones-patologo-qupath]]): marca solo donde la evidencia es clara, así que una
detección fuera de las 26 puede ser una mitosis real sin marcar. Nada acá se llama error.

El orden dentro de cada bloque
------------------------------
Es parecido **de píxeles, no semántico**. Por recorte: 16x16 RGB reducido + histograma de
color; se estandariza, PCA, linkage jerárquico y *optimal leaf ordering*
(`scipy.cluster.hierarchy`), que reordena las hojas del dendrograma para que vecinos en la
fila sean vecinos en el árbol. Dos recortes contiguos se parecen **en color y textura**; que
sean o no la misma entidad biológica es justamente lo que hay que mirar a ojo.

No se ordena por confianza porque `pred_mitosis.tsv` **no trae score**: sus columnas son
`x  y  name  color` y nada más.

Uso:
  PYTHONPATH=/media/administrador/Storage1/sdonoso/clam_testing2/.pylibs \
  /home/sdonoso/miniconda3/envs/clam_latest/bin/python scripts/galeria_mitosis_129741.py
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
from cruce_hovernext_marcas import marcas_mitosis, emparejar_pares  # noqa: E402

MPP = 0.465
TOL_UM = 30.0            # la del cruce; el 13/26 es plano de 7,5 a 75 µm
LADO_PX0 = 128           # ventana de nivel 0 = 59,5 µm de lado
ESCALA = 3               # se dibuja grande (mejor antialias) y se reduce al componer
TILE = 128               # lado del recorte ya compuesto en la lámina de contacto

# El bitmap font por defecto de PIL no trae acentos («detección» sale con cajitas). Barlow
# ya vive bajo containment (clam_testing2/fonts/barlow) y es la tipografía del template.
FONTS = Path("/media/administrador/Storage1/sdonoso/clam_testing2/fonts/barlow")


def fuente(px, bold=False):
    from PIL import ImageFont
    f = FONTS / ("Barlow-SemiBold.ttf" if bold else "Barlow-Regular.ttf")
    try:
        return ImageFont.truetype(str(f), px)
    except OSError:
        return ImageFont.load_default()


AMARILLO = (0xFF, 0xC1, 0x07)     # detección de HoVer-NeXt
BLANCO = (255, 255, 255)          # marca del patólogo
ONCO_INK = (0x0E, 0x28, 0x41)
FONDO = (255, 255, 255)
# franja de familia sobre cada recorte; paleta del template (Deep-LLM-V) + apoyos
COLOR_GRUPO = [(0x3E, 0x68, 0x77), (0xB8, 0x5C, 0x38), (0x7A, 0x9E, 0x7E),
               (0x8E, 0x7C, 0xC3), (0xC9, 0xA2, 0x27)]
K_FAMILIAS = 4                    # corte del dendrograma del bloque de 164


def recorte(sl, cx, cy, det_xy=None, marca_xy=None):
    """Recorte nativo centrado en (cx, cy), con los círculos que correspondan.

    `read_region` con coordenadas negativas devuelve transparente, que al pasar a RGB queda
    negro y se lee como tejido oscuro. Se clampa el origen y se corrige el centro para que
    el círculo siga cayendo sobre el objeto.
    """
    L = LADO_PX0
    x0, y0 = int(round(cx - L / 2)), int(round(cy - L / 2))
    x0 = max(0, min(x0, sl.dimensions[0] - L))
    y0 = max(0, min(y0, sl.dimensions[1] - L))
    im = sl.read_region((x0, y0), 0, (L, L)).convert("RGB")
    im = im.resize((L * ESCALA, L * ESCALA), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    if det_xy is not None:
        u = (det_xy[0] - x0) * ESCALA; v = (det_xy[1] - y0) * ESCALA
        r = 13 * ESCALA                       # ~12 µm, el orden de un núcleo mitótico
        d.ellipse([u - r, v - r, u + r, v + r], outline=AMARILLO, width=5)
    if marca_xy is not None:
        u = (marca_xy[0] - x0) * ESCALA; v = (marca_xy[1] - y0) * ESCALA
        r = 22 * ESCALA
        d.ellipse([u - r, v - r, u + r, v + r], outline=BLANCO, width=5)
    return im


def vector(im):
    """Descriptor de PARECIDO DE PÍXELES: 16x16 RGB + histograma de color."""
    chico = np.asarray(im.resize((16, 16), Image.BILINEAR), dtype=np.float64) / 255.0
    a = np.asarray(im, dtype=np.uint8)
    hist = np.concatenate([np.histogram(a[:, :, c], bins=8, range=(0, 256))[0]
                           for c in range(3)]).astype(np.float64)
    hist /= hist.sum()
    return np.concatenate([chico.ravel(), hist * 4.0])


def orden_por_parecido(vecs, k_grupos=0):
    """PCA + linkage jerárquico + optimal leaf ordering.

    Devuelve `(orden, grupo)`: el orden de las hojas y, si `k_grupos>0`, a qué grupo del
    dendrograma cortado en k cae cada recorte. El *optimal leaf ordering* deja los grupos
    CONTIGUOS en la fila, así que el corte se ve en la lámina y no hay que creerlo.
    """
    from scipy.cluster.hierarchy import (linkage, optimal_leaf_ordering, leaves_list,
                                         fcluster)
    from scipy.spatial.distance import pdist
    n = len(vecs)
    if n < 3:
        return np.arange(n), np.zeros(n, dtype=int)
    X = np.asarray(vecs)
    X = (X - X.mean(0)) / np.maximum(X.std(0), 1e-9)
    ncomp = min(20, X.shape[0] - 1, X.shape[1])
    U, S, _ = np.linalg.svd(X - X.mean(0), full_matrices=False)
    Y = U[:, :ncomp] * S[:ncomp]
    d = pdist(Y)
    Z = optimal_leaf_ordering(linkage(d, method="average"), d)
    grupo = (fcluster(Z, t=k_grupos, criterion="maxclust") if k_grupos > 0
             else np.zeros(n, dtype=int))
    return leaves_list(Z), np.asarray(grupo, dtype=int)


def descriptores(im):
    """Dos descriptores INTERPRETABLES por recorte, para poder decir en qué se parecen.

    No son features del clustering (ése usa 16x16 RGB + histograma): son la forma de
    contar qué tiene adentro cada familia sin apelar a «se ven distintas».
    """
    a = np.asarray(im.convert("RGB"), dtype=np.float64)
    gris = a.mean(2)
    mx, mn = a.max(2), a.min(2)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1), 0)
    # «fondo» = claro y sin color, el criterio de mascara_tejido() de alinear_*
    fondo = float(((sat <= 0.10) | (gris >= 225)).mean())
    return dict(brillo=float(gris.mean()), saturacion=float(sat.mean()),
                fraccion_fondo=fondo)


def contacto(crops, etiquetas, cols, titulo, sub, path, grupos=None):
    """Lámina de contacto: los recortes en grilla, con su índice en la esquina."""
    n = len(crops)
    filas = int(np.ceil(n / cols))
    pad = 4
    cab = 42 + 17 * len(sub) + 10        # la cabecera crece con el subtitulo, no al reves
    W = cols * (TILE + pad) + pad
    H = cab + filas * (TILE + pad) + pad
    f_tit, f_sub, f_idx = fuente(21, bold=True), fuente(14), fuente(12)
    hoja = Image.new("RGB", (W, H), FONDO)
    d = ImageDraw.Draw(hoja)
    d.text((pad + 2, 12), titulo, fill=ONCO_INK, font=f_tit)
    for k, linea in enumerate(sub):
        d.text((pad + 2, 40 + 17 * k), linea, fill=(0x55, 0x66, 0x6E), font=f_sub)
    for i, (im, et) in enumerate(zip(crops, etiquetas)):
        r, c = divmod(i, cols)
        x = pad + c * (TILE + pad); y = cab + r * (TILE + pad)
        hoja.paste(im.resize((TILE, TILE), Image.LANCZOS), (x, y))
        if grupos is not None:
            d.rectangle([x, y - 3, x + TILE, y - 1],
                        fill=COLOR_GRUPO[(grupos[i] - 1) % len(COLOR_GRUPO)])
        d.rectangle([x, y + TILE - 15, x + 24, y + TILE], fill=(255, 255, 255))
        d.text((x + 3, y + TILE - 16), str(et), fill=ONCO_INK, font=f_idx)
    hoja.save(path)
    return hoja.size


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--geojson", default="/media/administrador/Storage1/sdonoso/hover_net/"
                                         "129741.bif - GDT.geojson")
    ap.add_argument("--wsi", default="/media/administrador/Storage1/sdonoso/wsi/129741/"
                                     "129741.bif")
    ap.add_argument("--tsv", default=str(REPO / "results/b8_hovernext_129741/hovernext/"
                                                "lizard_mitosis/129741/pred_mitosis.tsv"))
    ap.add_argument("--offset", default=str(REPO / "sprints/B8_sprint8/anotaciones_patologo/"
                                                   "offset_129741.json"))
    ap.add_argument("--out-dir", default=str(REPO / "results/b8_hovernext_129741/"
                                                    "galeria_mitosis"))
    a = ap.parse_args()

    import openslide
    out = Path(a.out_dir); out.mkdir(parents=True, exist_ok=True)
    (out / "recortes").mkdir(exist_ok=True)
    off = json.loads(Path(a.offset).read_text())

    marcas, _ = marcas_mitosis(a.geojson, off["dx"], off["dy"])
    det = np.asarray([[float(r["x"]), float(r["y"])]
                      for r in csv.DictReader(open(a.tsv), delimiter="\t")])
    dist = np.linalg.norm(marcas[:, None, :] - det[None, :, :], axis=2)
    ok, pares = emparejar_pares(dist, TOL_UM / MPP)

    acreditadas = {int(j) for j in pares if j >= 0}
    sin_marca = [j for j in range(len(det)) if j not in acreditadas]
    print("=" * 74)
    print("GALERÍA DE LAS 177 — encargo 2")
    print("=" * 74)
    print(f"detecciones            : {len(det)}")
    print(f"  acreditan una marca  : {len(acreditadas)}")
    print(f"  sin marca            : {len(sin_marca)}")
    print(f"marcas                 : {len(marcas)}  ({int(ok.sum())} acreditadas, "
          f"{int((~ok).sum())} se escapan)")
    assert len(acreditadas) + len(sin_marca) == len(det), "los bloques no suman 177"
    assert len(acreditadas) == int(ok.sum()), "el emparejamiento es uno a uno: tiene que dar 13"

    sl = openslide.OpenSlide(a.wsi)
    print(f"lámina: {sl.dimensions[0]}x{sl.dimensions[1]} px, "
          f"ventana de {LADO_PX0} px = {LADO_PX0 * MPP:.1f} µm de lado")

    bloques = []
    # ---------------------------------------------------------- 1. sin marca (164)
    crops = [recorte(sl, det[j][0], det[j][1], det_xy=det[j]) for j in sin_marca]
    bloques.append(("sin_marca", sin_marca, crops, None,
                    f"Detecciones sin marca del patólogo — {len(crops)} de 177",
                    ["NO son falsos positivos: el patólogo marca solo la evidencia clara, "
                     "así que una detección fuera de las 26 puede ser una mitosis sin marcar.",
                     "Círculo amarillo = detección de HoVer-NeXt. Ventana de 59,5 µm de lado, "
                     "resolución nativa (0,465 µm/px).",
                     "Orden por parecido de PÍXELES (16x16 RGB + histograma de color), "
                     "no semántico: vecinos se parecen en color y textura."]))
    # ---------------------------------------------------------- 2. acertadas (13)
    idx_ok = [i for i in range(len(marcas)) if ok[i]]
    crops = [recorte(sl, det[pares[i]][0], det[pares[i]][1],
                     det_xy=det[pares[i]], marca_xy=marcas[i]) for i in idx_ok]
    bloques.append(("acertadas", idx_ok, crops, None,
                    f"Detecciones que acreditaron una marca — {len(crops)} de 26 marcas",
                    ["Amarillo = detección de HoVer-NeXt; blanco = marca del patólogo. "
                     "Centrado en la detección.",
                     "Ventana de 59,5 µm de lado, resolución nativa. "
                     "Orden por parecido de píxeles."]))
    # ---------------------------------------------------------- 3. falladas (13)
    idx_no = [i for i in range(len(marcas)) if not ok[i]]
    crops = [recorte(sl, marcas[i][0], marcas[i][1], marca_xy=marcas[i]) for i in idx_no]
    bloques.append(("falladas", idx_no, crops, None,
                    f"Marcas que se escapan — {len(crops)} de 26",
                    ["Centrado en la marca del patólogo (blanco). No hay ninguna detección "
                     "de mitosis a 30 µm.",
                     "Sí hay un núcleo segmentado encima, al que le tocó otra clase: "
                     "12 `epithelial-cell` y 1 `neutrophil` (A0)."]))

    filas_idx, familias = [], []
    for nombre, ids, crops, _, titulo, sub in bloques:
        # El bloque grande se corta en familias; los de 13 no (con n=13 un corte no dice
        # nada y la lamina entera se mira de un vistazo).
        k = K_FAMILIAS if nombre == "sin_marca" else 0
        orden, grupo = orden_por_parecido([vector(im) for im in crops], k_grupos=k)
        crops_ord = [crops[j] for j in orden]
        ids_ord = [ids[j] for j in orden]
        grupo_ord = [int(grupo[j]) for j in orden]
        cols = 14 if len(crops) > 40 else min(len(crops), 7)
        sub_f = list(sub)
        if k:
            # renumerar las familias por orden de aparicion en la lamina, para que la
            # leyenda se lea de izquierda a derecha
            ren, prox = {}, 1
            for g in grupo_ord:
                if g not in ren:
                    ren[g] = prox; prox += 1
            grupo_ord = [ren[g] for g in grupo_ord]
            cuenta = {g: grupo_ord.count(g) for g in sorted(set(grupo_ord))}
            sub_f.append("Franja de color = familia del dendrograma cortado en "
                         f"{k}: " + ", ".join(f"#{g} n={c}" for g, c in cuenta.items()))
        tam = contacto(crops_ord, list(range(len(crops_ord))), cols, titulo, sub_f,
                       out / f"bloque_{nombre}.png",
                       grupos=grupo_ord if k else None)
        print(f"\nbloque {nombre:<10} {len(crops):>4} recortes -> "
              f"bloque_{nombre}.png  ({tam[0]}x{tam[1]} px, {cols} columnas)")
        for pos, (j, im) in enumerate(zip(ids_ord, crops_ord)):
            if nombre != "sin_marca":            # los 26 informativos, uno por archivo
                im.save(out / "recortes" / f"{nombre}_{pos:02d}_id{j}.png")
            xy = det[j] if nombre == "sin_marca" else (
                det[pares[j]] if nombre == "acertadas" else marcas[j])
            desc = descriptores(im)
            filas_idx.append(dict(bloque=nombre, posicion_en_la_lamina=pos,
                                  familia=grupo_ord[pos] if k else "",
                                  id=int(j), x=round(float(xy[0]), 1),
                                  y=round(float(xy[1]), 1),
                                  brillo=round(desc["brillo"], 1),
                                  saturacion=round(desc["saturacion"], 3),
                                  fraccion_fondo=round(desc["fraccion_fondo"], 3)))
        if k:
            for g in sorted(set(grupo_ord)):
                sel = [f for f in filas_idx
                       if f["bloque"] == nombre and f["familia"] == g]
                familias.append(dict(
                    bloque=nombre, familia=g, n=len(sel),
                    brillo_mediano=round(float(np.median([f["brillo"] for f in sel])), 1),
                    saturacion_mediana=round(
                        float(np.median([f["saturacion"] for f in sel])), 3),
                    fraccion_fondo_mediana=round(
                        float(np.median([f["fraccion_fondo"] for f in sel])), 3)))
            print(f"  familias (corte del dendrograma en {k}, orden de aparición):")
            print(f"    {'#':>2} {'n':>4} {'brillo':>8} {'saturac.':>9} {'fondo':>7}")
            for f in familias:
                print(f"    {f['familia']:>2} {f['n']:>4} {f['brillo_mediano']:>8.1f} "
                      f"{f['saturacion_mediana']:>9.3f} "
                      f"{f['fraccion_fondo_mediana']:>7.3f}")
    sl.close()

    if familias:
        with open(out / "familias.csv", "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(familias[0].keys()))
            w.writeheader(); w.writerows(familias)

    with open(out / "indice.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(filas_idx[0].keys()))
        w.writeheader(); w.writerows(filas_idx)

    meta = dict(
        que_es="galeria de las 177 detecciones de mitosis de la 129741, en tres bloques, "
               "ordenada por parecido de pixeles",
        no_es=["una evaluacion de precision: las 164 sin marca NO son falsos positivos",
               "un orden semantico: el parecido es de pixeles (16x16 RGB + histograma)",
               "un orden por confianza: pred_mitosis.tsv no trae score"],
        unidad="detecciones (177) en los bloques 1 y 2; marcas (26) en el bloque 3",
        n_detecciones=len(det), n_acreditan_marca=len(acreditadas),
        n_sin_marca=len(sin_marca), n_marcas=len(marcas),
        n_marcas_acreditadas=int(ok.sum()), n_marcas_falladas=int((~ok).sum()),
        tolerancia_um=TOL_UM, ventana_px_level0=LADO_PX0,
        ventana_um=round(LADO_PX0 * MPP, 1), mpp=MPP,
        orden="scipy.cluster.hierarchy: PCA(20) + linkage average + optimal_leaf_ordering",
        k_familias=K_FAMILIAS,
        familias_son="corte del MISMO dendrograma; agrupan por color y textura, NO por "
                     "entidad biologica",
        descriptores_son="brillo medio, saturacion media y fraccion de pixeles de fondo "
                         "(sat<=0.10 o gris>=225); NO son las features del clustering",
        offset_aplicado=dict(dx=off["dx"], dy=off["dy"]),
        fuente_detecciones=str(a.tsv), fuente_marcas=str(a.geojson),
    )
    (out / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    print(f"\nSalida: {out}")


if __name__ == "__main__":
    main()
