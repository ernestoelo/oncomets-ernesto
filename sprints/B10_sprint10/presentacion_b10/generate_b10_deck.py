#!/usr/bin/env python
"""generate_b10_deck.py — el deck de la reunión del martes 15-sep, sobre la plantilla oficial.

Siete láminas: la portada tal cual, OBJETIVOS con los tres encargos del 7-sep, una lámina por
encargo (O1, O2, O3), las cinco preguntas y Tareas. El método es el del B9: la plantilla se
RELLENA en sitio (`docs/plantilla_oficial.md` §7) y el deck se construye sobre el `.pptx` del
molde, que embebe Barlow ([[deck-template-fuentes-embebidas]]).

Importa, no reimplementa:
  - de `generate_b9_deck.py`, que es un deck cerrado y **no se edita**: la medición de texto con
    los TTF de Barlow, las tres maniobras de la plantilla, el relleno en sitio y el QA de nivel
    lámina;
  - de `scripts/b10_figuras_o1_o3.py`, `datos_o1()` y `datos_o3()`, que verifican cada número
    contra su `resultados.md` y abortan. Además, el deck compara lo que devuelven contra los CSV
    de `figuras/`, que siguen teniendo un solo escritor: ese script. **Este generador no escribe
    ningún CSV.**

Lo que es propio, y por qué:
  - Las tres figuras van NATIVAS, cada una en un group shape para que se escale entera. Con
    shapes y no con `add_chart` (decisión del 11-sep): un eje logarítmico, un punto hueco o un
    rótulo por fila piden XML a mano dentro del gráfico y cada visor los dibuja distinto.
  - Un auditor que ENTRA en los grupos. `auditar()` y `barrer_rayas()` del B9 recorren
    `slide.shapes`, y un grupo no tiene `text_frame`: sin esto, el texto de las figuras quedaría
    sin medir (I2).
  - Un barrido sobre el XML ya guardado: rayas, punto decimal, nombres y **glifos que Barlow no
    trae**. `text_w()` no ve un glifo faltante porque PIL mide la caja del `.notdef` (K1), así
    que ninguna flecha ni ningún símbolo de leyenda va como carácter: van dibujados.

Dentro de las figuras el texto va en tinta (`TITULO`) o en gris neutro, nunca en `CUERPO`:
`#1B4F8C` es también el color de «alto» en O1 y de «test» en O3, y un rótulo en el color de una
serie se lee como parte de ella (K4). Cuerpo y pie de la lámina siguen en `CUERPO`, que es la
gramática del molde.

El guion vive en `guion_b10.md` y se aplica desde ahí: ese archivo es la fuente y las notas del
`.pptx` son derivadas.

Uso (workaround B; `envs/pruebas` porque el driver de O1 importa zarr al tope):
    PYTHONPATH=/media/administrador/Storage1/sdonoso/clam_testing2/.pylibs \
      /home/sdonoso/miniconda3/envs/pruebas/bin/python generate_b10_deck.py
"""
import html
import json
import math
import os
import re
import sys
import zipfile

import numpy as np
import pandas as pd
from fontTools.ttLib import TTFont
from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE, MSO_SHAPE_TYPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
sys.path.insert(0, os.path.join(RAIZ, "sprints", "B9_sprint9", "presentacion_b9"))
sys.path.insert(0, os.path.join(RAIZ, "scripts"))

from generate_b9_deck import (  # noqa: E402
    BARLOW_DIR, BLANCO, CUERPO, F, G_CUERPO, LINEA, SEP, SH, SW, TITULO, TURBO, _rect, _rgb, _shape,
    _util, add_textbox, auditar, barrer_rayas, borrar_slide, caja_figura, clonar_s03,
    forzar_barlow, llenar_tabla, notes, num, pie_lineas, reordenar, set_cejilla, set_cuerpo,
    set_encabezado, set_titulo, text_w, wrap_lines, wrap_lines_mixto)
from b10_figuras_o1_o3 import (  # noqa: E402
    GRADO_COLOR, TIER_COLOR, TIER_TITULO, datos_o1, datos_o3)
from b9_pleomorfismo import TOL_VECINDAD_UM  # noqa: E402
from cruce_94_marcas import REGION_ANOTADA  # noqa: E402

# ---------------------------------------------------------------------------
# Constantes del período
# ---------------------------------------------------------------------------
FECHA_ARCHIVO = "20260915"          # la reunión
AUTOR = "Ernesto Gamero"
PROYECTO = "Detección Nuclear"      # el mismo del B9: nombra el archivo y la cejilla
PERIODO = "08/09/2026 - 15/09/2026"
FECHA_CIERRE = "09/09"              # los tres encargos cerraron el 9-sep
FECHA_TAREA = "22/09"

TPL = os.path.join(RAIZ, "papers", "presentations",
                   "[AAAAMMDD] [Nombre Apellido] [Image-to-text].pptx")
OUT = os.path.join(AQUI, "[%s] [%s] [%s].pptx" % (FECHA_ARCHIVO, AUTOR, PROYECTO))
GUION = os.path.join(AQUI, "guion_b10.md")
FIG = os.path.join(RAIZ, "sprints", "B10_sprint10", "figuras")
CSV_O1 = os.path.join(FIG, "o1_apertura_grado.csv")
CSV_O3 = os.path.join(FIG, "o3_auc_por_lamina.csv")
RES_O1 = os.path.join(RAIZ, "results", "b10_grado_sin_marca")
ASSETS = os.path.join(AQUI, "assets")
JSON_IMG = os.path.join(ASSETS, "deck_imagenes.json")        # lo escribe scripts/b10_deck_imagenes.py
SEL_IMG = os.path.join(RAIZ, "results", "b10_deck_imagenes", "seleccion.json")
CLAVES = ["s%02d" % i for i in range(1, 12)]

GRADOS = ["alto", "moderado", "bajo"]
TIERS = ["train", "val", "test", "fuera"]


def _hex(h):
    h = h.lstrip("#")
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


# Las rampas vienen del script de figuras, validadas con la skill `dataviz` (ordinales, un solo
# tono, más oscuro = grado más alto o tier más limpio). No se redefinen acá.
COL_GRADO = {g: _hex(c) for g, c in GRADO_COLOR.items()}
COL_TIER = {t: _hex(c) for t, c in TIER_COLOR.items()}
GRIS = RGBColor(0x59, 0x59, 0x59)   # texto secundario dentro de las figuras (K4)


def _lt(fs):
    """Alto de un renglón a `fs` puntos, en pulgadas (la misma cuenta que usa el B9)."""
    return fs * 1.22 / 72.0


# ===========================================================================
# Datos: se LEEN y se comparan, no se transcriben
# ===========================================================================
def _comparar(df, csv, nombre):
    """Lo que devuelve el script de figuras contra lo que ese mismo script escribió.

    Enteros, booleanos y textos se comparan exactos; los reales con 6e-5, porque el CSV va a
    cuatro decimales. Si difieren, el CSV quedó viejo respecto del script (o al revés), y la
    lámina dibujaría otra cosa que la figura versionada."""
    if list(df.columns) != list(csv.columns):
        raise SystemExit("%s: columnas %s contra %s" % (nombre, list(df.columns),
                                                         list(csv.columns)))
    if len(df) != len(csv):
        raise SystemExit("%s: %d filas contra %d" % (nombre, len(df), len(csv)))
    for c in df.columns:
        a = df[c].reset_index(drop=True)
        b = csv[c].reset_index(drop=True)
        if pd.api.types.is_float_dtype(a) or pd.api.types.is_float_dtype(b):
            ok = np.allclose(a.astype(float).values, b.astype(float).values, atol=6e-5, rtol=0)
        else:
            ok = bool((a.astype(str).values == b.astype(str).values).all())
        if not ok:
            raise SystemExit("%s: la columna %r no coincide con el CSV" % (nombre, c))
    print("  %s: %d filas, iguales a las del script de figuras" % (os.path.basename(nombre),
                                                                  len(df)))


def leer_o1():
    filas = datos_o1()
    _comparar(pd.DataFrame(filas), pd.read_csv(CSV_O1, keep_default_na=False), CSV_O1)
    return filas


def leer_o3():
    d = datos_o3()
    csv = pd.read_csv(CSV_O3, keep_default_na=False, dtype={"slide": str})
    faltan = [c for c in csv.columns if c not in d.columns]
    if faltan:
        raise SystemExit("o3: el CSV trae columnas que datos_o3() no devuelve: %s" % faltan)
    # La B25-158899 no tiene fila en el CSV de etiquetas: llega NaN de datos_o3() y vacía del
    # CSV. Se normaliza para compararla; la lámina no la dibuja.
    c = d[list(csv.columns)].copy()
    c["etiqueta"] = c["etiqueta"].fillna("")
    _comparar(c, csv, CSV_O3)
    return d


def leer_escalera():
    """Los cuatro números del pie de O1 que no están en el CSV de la figura (K3), más el tamaño
    del nulo. Se leen de los artefactos de la corrida, no se transcriben."""
    e = pd.read_csv(os.path.join(RES_O1, "escalera.csv"), dtype={"slide": str})
    a = e[(e.brazo == "A_lamina_entera") & (e.desc == "percentil")]
    lam = a.drop_duplicates("slide")
    s5 = a[a.N == 5000].drop_duplicates("slide")
    nulo = np.load(os.path.join(RES_O1, "nulo.npz"))
    iters = {nulo[k].shape[0] for k in nulo.files}
    d = dict(n_laminas=len(lam), marcas=int(lam.n_marcas.sum()),
             alcanzables=int(lam.n_resueltas.sum()),
             n_lam_5000=len(s5), bajo_5000=int(s5[s5.grados == "bajo"].n_resueltas.sum()),
             bajo_2000=int(lam[lam.grados == "bajo"].n_resueltas.sum()),
             n_trasl=iters.pop() if len(iters) == 1 else None)
    duros = dict(n_laminas=21, marcas=187, alcanzables=145, n_lam_5000=19, bajo_5000=9,
                 bajo_2000=16, n_trasl=200)
    for k, v in duros.items():
        if d[k] != v:
            raise SystemExit("escalera.csv: %s = %r, se esperaba %r" % (k, d[k], v))
    if int(TOL_VECINDAD_UM) != 15 or TOL_VECINDAD_UM != int(TOL_VECINDAD_UM):
        raise SystemExit("la tolerancia de emparejamiento se movió: %r µm" % TOL_VECINDAD_UM)
    return d


def leer_guion():
    """Parsea `guion_b10.md` por sus marcadores `## [sNN]`, con el mismo regex que el B9, y
    desenvuelve cada párrafo.

    El `.md` va envuelto a cien columnas para leerse en el editor, y `notes()` convierte cada
    salto de línea en un párrafo del panel de notas: sin esto, las notas salían cortadas a mitad
    de frase (17 a 23 párrafos por lámina para 3 a 6 de guion). Los párrafos quedan separados
    por una línea en blanco, que es el formato del guion."""
    txt = open(GUION, encoding="utf-8").read()
    bloques = {}
    for m in re.finditer(r"^## \[([^\]]+)\][^\n]*\n(.*?)(?=^## \[|\Z)", txt, re.M | re.S):
        pars = [" ".join(p.split()) for p in re.split(r"\n\s*\n", m.group(2)) if p.strip()]
        bloques[m.group(1).strip()] = "\n\n".join(pars)
    faltan = [k for k in CLAVES if k not in bloques]
    if faltan:
        raise SystemExit("faltan bloques del guion: %s" % faltan)
    return bloques


def _o1(o1, N, grupo):
    return next(f for f in o1 if f["N"] == N and f["grupo"] == grupo)


# ===========================================================================
# Primitivas de las figuras. Todas aceptan un group shape donde el B9 dice `slide`.
# ===========================================================================
def recta(g, x1, y1, x2, y2, color, ancho_pt=0.75, dash=None, flecha=False):
    """Recta como conector: una freeform de dos puntos tiene ancho o alto cero."""
    c = g.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1),
                               Inches(x2), Inches(y2))
    c.line.color.rgb = color
    c.line.width = Pt(ancho_pt)
    if dash is not None:
        c.line.dash_style = dash
    # el conector trae `effectRef idx="1"` y el theme del molde tiene sombra en las tres
    # `effectStyle`: sin esto cada recta sale con una cola gris de ~0,07" hacia abajo
    c.shadow.inherit = False
    if flecha:
        # la punta va DIBUJADA en el `a:ln`: Barlow no trae la flecha como glifo (K1)
        te = etree.SubElement(c.line._get_or_add_ln(), qn("a:tailEnd"))
        te.set("type", "triangle")
        te.set("w", "med")
        te.set("len", "med")
    return c


def sin_efectos(g):
    """Anula la referencia al efecto del theme en todo lo que haya dentro del grupo.

    Las tres `effectStyle` del theme del molde traen sombra, y las formas de python-pptx la
    referencian (`effectRef` 1 o 2). `shadow.inherit = False` escribe un `<a:effectLst/>` vacío,
    que PowerPoint respeta y LibreOffice no: el PDF y el rasterizado de QA salían con sombra en
    cada recta, bloque y marcador. Con `idx="0"` los visores dibujan lo mismo."""
    for er in g._element.iter(qn("a:effectRef")):
        er.set("idx", "0")


def polilinea(g, pts, color, ancho_pt, dash=None):
    """Polilínea abierta. `convert_to_shape()` no recalcula la caja del grupo (K2): quien arma
    la figura llama a `recalculate_extents()` al terminar."""
    fb = g.shapes.build_freeform(Inches(pts[0][0]), Inches(pts[0][1]), scale=1.0)
    fb.add_line_segments([(Inches(x), Inches(y)) for x, y in pts[1:]], close=False)
    sp = fb.convert_to_shape()
    sp.fill.background()
    sp.line.color.rgb = color
    sp.line.width = Pt(ancho_pt)
    if dash is not None:
        sp.line.dash_style = dash
    sp.shadow.inherit = False
    return sp


def circulo(g, cx, cy, d, relleno, borde=None, ancho_pt=1.0):
    """Marcador. Hueco = relleno BLANCO con borde de color, no `fill.background()`, que deja
    ver lo que hay detrás ([[deck-qa-puntos-ciegos-chequeo]], ADDENDUM 4-ago 20:00)."""
    ov = g.shapes.add_shape(MSO_SHAPE.OVAL, Inches(cx - d / 2.0), Inches(cy - d / 2.0),
                            Inches(d), Inches(d))
    ov.fill.solid()
    ov.fill.fore_color.rgb = relleno
    if borde is None:
        ov.line.fill.background()
    else:
        ov.line.color.rgb = borde
        ov.line.width = Pt(ancho_pt)
    ov.shadow.inherit = False
    return ov


def rotulo(g, x, y, txt, fs, col=TITULO, bold=False, italic=False, alin=PP_ALIGN.LEFT):
    """Rótulo de UNA línea en una caja del ancho de su texto más 0,20".

    `x` es el borde izquierdo, el centro o el borde derecho según `alin`, e `y` el centro
    vertical. La caja mide lo que mide el texto: una holgada no se ve, pero llena de falsos
    positivos cualquier chequeo de intersecciones ([[deck-qa-puntos-ciegos-chequeo]])."""
    ancho = text_w(txt, fs, bold) + 0.20
    alto = _lt(fs) + 0.04
    if alin == PP_ALIGN.CENTER:
        izq = x - ancho / 2.0
    elif alin == PP_ALIGN.RIGHT:
        izq = x - ancho
    else:
        izq = x
    tb = add_textbox(g, izq, y - alto / 2.0, ancho, alto, [(txt, fs, bold, col, alin)],
                     anchor=MSO_ANCHOR.MIDDLE, space_after=0)
    if italic:
        for r in tb.text_frame.paragraphs[0].runs:
            r.font.italic = True
    return tb


def bloque(g, l, t, w, h, txt, relleno, col, fs, bold=True, forma=MSO_SHAPE.RECTANGLE):
    """Bloque de color con su texto centrado, márgenes chicos y conocidos."""
    sp = g.shapes.add_shape(forma, Inches(l), Inches(t), Inches(w), Inches(h))
    sp.fill.solid()
    sp.fill.fore_color.rgb = relleno
    sp.line.fill.background()
    sp.shadow.inherit = False
    tf = sp.text_frame
    tf.margin_left = tf.margin_right = Inches(0.04)
    tf.margin_top = tf.margin_bottom = Inches(0)
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = txt
    r.font.size = Pt(fs)
    r.font.bold = bold
    r.font.name = F
    r.font.color.rgb = col
    return sp


def separar(ys, sep):
    """Separa rótulos verticales hasta que queden a `sep` como mínimo, moviendo cada par por
    igual. Devuelve las posiciones en el orden de entrada."""
    orden = sorted(range(len(ys)), key=lambda i: ys[i])
    v = [ys[i] for i in orden]
    for _ in range(200):
        movido = False
        for i in range(1, len(v)):
            d = v[i] - v[i - 1]
            if d < sep - 1e-9:
                m = (sep - d) / 2.0
                v[i - 1] -= m
                v[i] += m
                movido = True
        if not movido:
            break
    out = [0.0] * len(ys)
    for k, i in enumerate(orden):
        out[i] = v[k]
    return out


# ===========================================================================
# O1 — la escalera por grado
# ===========================================================================
DOM_O1 = (8.0, 2240.0)


def figura_o1(s, l, t, w, h, o1):
    """Porcentaje de marcas alcanzables recuperadas por grado, contra N en escala log.

    Orden de pintado: grilla, vertical de N = 500, nulos de bajo a alto, sólidas, marcadores
    con anillo blanco, rótulos. Así alto queda encima de todo y ninguna curva tapa un texto."""
    g = s.shapes.add_group_shape()
    por = {gr: [f for f in o1 if f["grupo"] == gr] for gr in GRADOS}
    f500 = {gr: _o1(o1, 500, gr) for gr in GRADOS}
    FS_T, FS_R, FS_L = 8.5, 9.0, 8.5

    W_TICK, W_PLOT, W_LAB = 0.62, 8.4, 1.45
    x0 = l + (w - (W_TICK + W_PLOT + W_LAB)) / 2.0 + W_TICK
    x1 = x0 + W_PLOT
    # 0,44 y no 0,40: el título del eje y el titular de N = 500 quedaban a 0,04" del 100 %
    H_BANDA = 0.44
    H_EJE = 0.10 + 2 * (_lt(FS_T) + 0.03) + 0.05 + _lt(FS_R)
    y_top = t + H_BANDA
    y_base = t + h - H_EJE
    PH = y_base - y_top
    lo, hi = math.log(DOM_O1[0]), math.log(DOM_O1[1])

    def X(n):
        return x0 + W_PLOT * (math.log(n) - lo) / (hi - lo)

    def Y(v):
        return y_top + PH * (1.0 - v / 100.0)

    # grilla, base y ticks
    for v in (25, 50, 75, 100):
        recta(g, x0, Y(v), x1, Y(v), LINEA, 0.75)
    recta(g, x0, y_base, x1, y_base, SEP, 0.75)
    for f in por["alto"]:
        recta(g, X(f["N"]), y_base, X(f["N"]), y_base + 0.06, SEP, 0.75)
    # la vertical del titular sube hasta el tope de la banda de cabecera
    recta(g, X(500), y_base, X(500), t, SEP, 1.0)

    for gr in reversed(GRADOS):
        polilinea(g, [(X(f["N"]), Y(f["pct_nulo_p975"])) for f in por[gr]], COL_GRADO[gr],
                  1.25, MSO_LINE_DASH_STYLE.DASH)
    for gr in reversed(GRADOS):
        polilinea(g, [(X(f["N"]), Y(f["pct_alcanzables"])) for f in por[gr]], COL_GRADO[gr],
                  2.0)
    for gr in reversed(GRADOS):
        for f in por[gr]:
            circulo(g, X(f["N"]), Y(f["pct_alcanzables"]), 0.095, COL_GRADO[gr], BLANCO, 1.0)

    # leyenda interna arriba a la izquierda: ahí las curvas no pasan del 20 %. Un rectángulo
    # blanco detrás, para que la grilla no la cruce, con filete del color de la grilla: sin él la
    # línea del 75 % parecía cortada a mitad de eje. El filete queda a 0,09" del 100 % y del 50 %;
    # con 0,02 el borde tapaba media línea de grilla.
    items = [(gr, "%s (%d alcanzables)" % (gr, f500[gr]["alcanzables"])) for gr in GRADOS]
    items.append((None, "p97,5 del nulo, en el color de su grado"))
    paso, w_m = 0.165, 0.34
    lx, ly = x0 + 0.12, y_top + 0.14
    w_txt = max(text_w(txt, FS_L) for _, txt in items) + 0.20
    caja = _rect(g, lx - 0.06, ly - 0.05, w_m + 0.08 + w_txt + 0.06, paso * len(items) + 0.10,
                 BLANCO)
    caja.line.color.rgb = LINEA
    caja.line.width = Pt(0.75)
    for i, (gr, txt) in enumerate(items):
        yc = ly + paso * (i + 0.5)
        if gr is None:
            recta(g, lx, yc, lx + w_m, yc, GRIS, 1.25, MSO_LINE_DASH_STYLE.DASH)
        else:
            recta(g, lx, yc, lx + w_m, yc, COL_GRADO[gr], 2.0)
            circulo(g, lx + w_m / 2.0, yc, 0.085, COL_GRADO[gr], BLANCO, 1.0)
        rotulo(g, lx + w_m + 0.08, yc, txt, FS_L, GRIS)

    # rótulos finales en tinta, separados al menos 0,17": moderado y bajo quedan a ~0,1"
    fin = [Y(por[gr][-1]["pct_alcanzables"]) for gr in GRADOS]
    for gr, yl in zip(GRADOS, separar(fin, 0.17)):
        f = por[gr][-1]
        rotulo(g, x1 + 0.10, yl, "%s · %d de %d" % (gr, f["recall"], f["alcanzables"]), FS_R)

    # banda de cabecera: el título del eje y a la izquierda, el titular a la derecha de su
    # vertical
    rotulo(g, x0 - W_TICK, t + 0.28, "% de las marcas alcanzables recuperadas", FS_R, GRIS)
    xb = X(500) + 0.08
    rotulo(g, xb, t + 0.10, "N = 500 · %s mm² por lámina"
           % num(f500["alto"]["carga_media_mm2_lamina"], 2), FS_R, TITULO, bold=True)
    rotulo(g, xb, t + 0.28, " · ".join("%s %d de %d" % (gr, f500[gr]["recall"],
                                                          f500[gr]["alcanzables"])
                                         for gr in GRADOS), FS_R, GRIS)

    # eje y
    for v in (0, 25, 50, 75, 100):
        rotulo(g, x0 - 0.08, Y(v), "0" if v == 0 else "%d %%" % v, FS_T, GRIS,
               alin=PP_ALIGN.RIGHT)
    # eje x en tres renglones: N, mm² y el título, con «N» y «mm²» en la columna de ticks
    # 0,10 y no 0,07: los ticks bajan 0,06 y a 0,07 los números quedaban a 0,018" de ellos
    y_n = y_base + 0.10 + _lt(FS_T) / 2.0
    y_mm = y_n + _lt(FS_T) + 0.03
    rotulo(g, x0 - 0.08, y_n, "N", FS_T, GRIS, bold=True, alin=PP_ALIGN.RIGHT)
    rotulo(g, x0 - 0.08, y_mm, "mm²", FS_T, GRIS, bold=True, alin=PP_ALIGN.RIGHT)
    for f in por["alto"]:
        rotulo(g, X(f["N"]), y_n, "%d" % f["N"], FS_T, GRIS, alin=PP_ALIGN.CENTER)
        rotulo(g, X(f["N"]), y_mm, num(f["carga_media_mm2_lamina"], 2), FS_T, GRIS,
               alin=PP_ALIGN.CENTER)
    rotulo(g, (x0 + x1) / 2.0, y_mm + _lt(FS_T) / 2.0 + 0.05 + _lt(FS_R) / 2.0,
           "N: núcleos epiteliales más grandes de cada lámina · mm²: superficie de los parches "
           "que los contienen, en promedio por lámina", FS_R, GRIS, alin=PP_ALIGN.CENTER)
    sin_efectos(g)
    g._element.recalculate_extents()
    return g


# ===========================================================================
# O2 — lo que dice el CAP, como diagrama
# ===========================================================================
def diagrama_o2(s, l, t, w, h):
    """Fila A: los tres scores de pleomorfismo invasivo con su cita textual, sobre un eje de
    variación. Fila B: el único corte numérico (tamaño, grado nuclear de CDIS) y el único
    componente que es un conteo (el mitótico). Centrado en su caja."""
    g = s.shapes.add_group_shape()
    FS_TIT, FS_Q, FS_N, FS_T = 11, 9.5, 9, 8.5
    tit_a = "Pleomorfismo nuclear del carcinoma invasivo: tres scores"
    # «un solo corte numérico» se leía contra el eje, que dibuja dos cortes: el único es el rasgo
    tit_bi = "Grado nuclear de CDIS: seis rasgos, y solo el tamaño tiene corte numérico"
    tit_bd = "Componente mitótico: el único que es un conteo"
    eje_a = "más variación de tamaño y forma nuclear, contra el epitelio mamario normal"
    nota_bi = ("veces un núcleo epitelial ductal normal o un glóbulo rojo · el protocolo no dice "
               "si es diámetro o área")
    cap_bd = "10 campos de gran aumento, en la parte del tumor con más mitosis"
    scores = [("score 1", "bajo", TITULO, "«little variation in size»"),
              ("score 2", "moderado", BLANCO, "«moderate variability in both size and shape»"),
              ("score 3", "alto", BLANCO, "«marked variation in size and shape»")]

    W_B = max(2.9, max(text_w(q, FS_Q) for *_, q in scores) + 0.25)
    GAP_B, H_B = 0.25, 0.42
    W_A = 3 * W_B + 2 * GAP_B
    W_S, H_BAND = 5.0, 0.30
    D_C, G_C = 0.26, 0.10
    w_izq = max(text_w(tit_bi, FS_TIT, True), text_w(nota_bi, FS_N), W_S + 0.35) + 0.05
    w_der = max(text_w(tit_bd, FS_TIT, True), text_w(cap_bd, FS_N), 5 * D_C + 4 * G_C) + 0.05
    GAP_BB = 0.9
    W_Bt = w_izq + GAP_BB + w_der

    H_A = _lt(FS_TIT) + 0.10 + H_B + 0.07 + _lt(FS_Q) + 0.16 + 0.09 + _lt(FS_N)
    H_Bi = _lt(FS_TIT) + 0.12 + H_BAND + 0.02 + 0.06 + _lt(FS_T) + 0.06 + _lt(FS_N)
    H_Bd = _lt(FS_TIT) + 0.12 + 2 * D_C + G_C + 0.08 + _lt(FS_N)
    GAP_AB = 0.40
    H_tot = H_A + GAP_AB + max(H_Bi, H_Bd)
    y = t + max(0.0, (h - H_tot) / 2.0)

    # fila A
    xa = l + (w - W_A) / 2.0
    rotulo(g, xa, y + _lt(FS_TIT) / 2.0, tit_a, FS_TIT, TITULO, bold=True)
    yb = y + _lt(FS_TIT) + 0.10
    for i, (txt, gr, col, q) in enumerate(scores):
        x = xa + i * (W_B + GAP_B)
        bloque(g, x, yb, W_B, H_B, txt, COL_GRADO[gr], col, 12)
        rotulo(g, x + W_B / 2.0, yb + H_B + 0.07 + _lt(FS_Q) / 2.0, q, FS_Q, TITULO,
               italic=True, alin=PP_ALIGN.CENTER)
    ya = yb + H_B + 0.07 + _lt(FS_Q) + 0.16
    recta(g, xa, ya, xa + W_A, ya, SEP, 1.25, flecha=True)
    # 0,09 y no 0,05: la punta de la flecha baja 0,04 bajo la línea (tinta por renglón)
    rotulo(g, xa + W_A / 2.0, ya + 0.09 + _lt(FS_N) / 2.0, eje_a, FS_N, GRIS,
           alin=PP_ALIGN.CENTER)

    # fila B, izquierda: la escala de tamaño del grado nuclear de CDIS
    y2 = y + H_A + GAP_AB
    xb = l + (w - W_Bt) / 2.0
    rotulo(g, xb, y2 + _lt(FS_TIT) / 2.0, tit_bi, FS_TIT, TITULO, bold=True)
    xs0 = xb + 0.20

    def XS(v):
        return xs0 + W_S * (v - 1.0) / 2.0

    y_band = y2 + _lt(FS_TIT) + 0.12
    y_ax = y_band + H_BAND + 0.02
    bloque(g, XS(1.5), y_band, XS(2.0) - XS(1.5), H_BAND, "grado I", COL_GRADO["bajo"],
           TITULO, 9.5)
    rotulo(g, XS(2.25), y_band + H_BAND / 2.0, "II · intermedio", FS_N, GRIS,
           alin=PP_ALIGN.CENTER)
    # la punta del pentágono hace de «abierta»: el corte de grado III es «más de 2,5»
    bloque(g, XS(2.5), y_band, XS(3.0) - XS(2.5) + 0.18, H_BAND, "grado III",
           COL_GRADO["alto"], BLANCO, 9.5, forma=MSO_SHAPE.PENTAGON)
    recta(g, XS(1.0), y_ax, XS(3.0), y_ax, SEP, 1.0)
    for v, txt in ((1.0, "1×"), (1.5, "1,5×"), (2.0, "2×"), (2.5, "2,5×"), (3.0, "3×")):
        recta(g, XS(v), y_ax, XS(v), y_ax + 0.06, SEP, 1.0)
        rotulo(g, XS(v), y_ax + 0.06 + _lt(FS_T) / 2.0 + 0.01, txt, FS_T, GRIS,
               alin=PP_ALIGN.CENTER)
    rotulo(g, xb, y_ax + 0.06 + _lt(FS_T) + 0.06 + _lt(FS_N) / 2.0, nota_bi, FS_N, GRIS)

    # fila B, derecha: los diez campos del componente mitótico
    xr = xb + w_izq + GAP_BB
    rotulo(g, xr, y2 + _lt(FS_TIT) / 2.0, tit_bd, FS_TIT, TITULO, bold=True)
    yc0 = y2 + _lt(FS_TIT) + 0.12
    for k in range(10):
        fila, col = divmod(k, 5)
        circulo(g, xr + col * (D_C + G_C) + D_C / 2.0, yc0 + fila * (D_C + G_C) + D_C / 2.0,
                D_C, LINEA, SEP, 1.0)
    rotulo(g, xr, yc0 + 2 * D_C + G_C + 0.08 + _lt(FS_N) / 2.0, cap_bd, FS_N, GRIS)
    sin_efectos(g)
    g._element.recalculate_extents()
    return g


# ===========================================================================
# O3 — el forest plot por tier
# ===========================================================================
def figura_o3(s, l, t, w, h, d):
    """AUC por lámina con su IC, agrupado por tier. Columna de tier a la izquierda con un filete
    de su color; rótulo de lámina alineado a la derecha; conteo de parches con CDIS a la
    derecha. La leyenda va en el hueco de la izquierda, a la altura del eje."""
    g = s.shapes.add_group_shape()
    FS, FS_T, FS_R = 9.5, 8.5, 9.0
    H_HEAD, G_TIER, EXTRA = 0.34, 0.08, 0.14
    H_EJE = 0.06 + _lt(FS_T) + 0.05 + _lt(FS_R) + 0.04
    D, H_IC = 0.125, 0.04
    sub_b25 = "rama si, región anotada"
    rot = {r.slide: r.slide + ("  †" if not r.alineada else "") for r in d.itertuples()}

    w_tier = 0.16 + max(text_w(TIER_TITULO[x], FS, True) for x in TIERS) + 0.20
    w_lab = max([text_w(v, FS) for v in rot.values()] + [text_w(sub_b25, 8)]) + 0.20
    w_num = text_w("con CDIS", FS_T) + 0.30
    fijos = w_tier + 0.10 + 0.03 + 0.08 + w_lab + 0.14 + 0.30 + w_num
    PW = min(6.6, w - fijos)
    xt = l + (w - (fijos + PW)) / 2.0
    xf = xt + w_tier + 0.10
    xl = xf + 0.03 + 0.08
    xp = xl + w_lab + 0.14
    xn = xp + PW + 0.30
    xc = xn + w_num / 2.0

    def X(v):
        return xp + PW * v

    paso = (h - H_HEAD - H_EJE - (len(TIERS) - 1) * G_TIER - EXTRA) / len(d)
    y = t + H_HEAD
    filas, grupos = [], []
    for tier in TIERS:
        y0 = y
        for r in d[d.tier == tier].itertuples():
            filas.append((r, y + paso / 2.0))
            y += paso + (EXTRA if r.universo == "region" else 0.0)
        grupos.append((tier, y0, y))
        y += G_TIER
    y_eje = y - G_TIER + 0.04

    # grilla tenue, azar y eje
    for v in (0.25, 0.75, 1.0):
        recta(g, X(v), t + H_HEAD - 0.04, X(v), y_eje, LINEA, 0.75)
    recta(g, X(0.5), t + H_HEAD - 0.06, X(0.5), y_eje, SEP, 1.0, MSO_LINE_DASH_STYLE.DASH)
    rotulo(g, X(0.5), t + H_HEAD - 0.17, "azar", FS_T, GRIS, alin=PP_ALIGN.CENTER)
    recta(g, xp, y_eje, xp + PW, y_eje, SEP, 0.75)
    for v, txt in ((0, "0"), (0.25, "0,25"), (0.5, "0,5"), (0.75, "0,75"), (1.0, "1")):
        recta(g, X(v), y_eje, X(v), y_eje + 0.06, SEP, 0.75)
        rotulo(g, X(v), y_eje + 0.06 + _lt(FS_T) / 2.0 + 0.01, txt, FS_T, GRIS,
               alin=PP_ALIGN.CENTER)
    rotulo(g, xp + PW / 2.0, y_eje + 0.06 + _lt(FS_T) + 0.05 + _lt(FS_R) / 2.0,
           "AUC: probabilidad de que la atención ponga un parche con CDIS por encima de uno "
           "sin CDIS", FS_R, GRIS, alin=PP_ALIGN.CENTER)
    rotulo(g, xc, t + 0.08, "parches", FS_T, GRIS, alin=PP_ALIGN.CENTER)
    # +0,02 sobre el interlineado: los dos renglones quedaban a 0,009" de tinta a tinta
    rotulo(g, xc, t + 0.10 + _lt(FS_T), "con CDIS", FS_T, GRIS, alin=PP_ALIGN.CENTER)

    # columna de tier: punto, título y filete del color del tier, centrados en su grupo
    for tier, y0, y1 in grupos:
        c = COL_TIER[tier]
        ym = (y0 + y1) / 2.0
        circulo(g, xt + 0.055, ym, 0.11, c)
        rotulo(g, xt + 0.14, ym, TIER_TITULO[tier], FS, TITULO, bold=True)
        _rect(g, xf, y0 + 0.02, 0.03, (y1 - y0) - 0.04, c)

    # filas: rótulo, IC, punto encima, conteo
    for r, yc in filas:
        c = COL_TIER[r.tier]
        rotulo(g, xl + w_lab, yc, rot[r.slide], FS, TITULO, alin=PP_ALIGN.RIGHT)
        if r.universo == "region":
            rotulo(g, xl + w_lab, yc + _lt(FS) - 0.01, sub_b25, 8, GRIS, italic=True,
                   alin=PP_ALIGN.RIGHT)
        _rect(g, X(r.ic_lo_dibujado), yc - H_IC / 2.0,
              X(r.ic_hi_dibujado) - X(r.ic_lo_dibujado), H_IC, c)
        if r.relleno:
            circulo(g, X(r.auc), yc, D, c)
        else:
            circulo(g, X(r.auc), yc, D, BLANCO, c, 1.5)
        rotulo(g, xc, yc, "%d" % r.n_marcados, FS, TITULO, alin=PP_ALIGN.CENTER)

    # leyenda con los tres símbolos DIBUJADOS (K1)
    ly = y_eje + 0.12
    circulo(g, xt + 0.055, ly, 0.11, GRIS)
    rotulo(g, xt + 0.14, ly, "p < 0,05", FS_T, GRIS)
    x2 = xt + 0.14 + text_w("p < 0,05", FS_T) + 0.38
    circulo(g, x2 + 0.055, ly, 0.11, BLANCO, GRIS, 1.25)
    rotulo(g, x2 + 0.14, ly, "p ≥ 0,05", FS_T, GRIS)
    ly2 = ly + _lt(FS_T) + 0.07
    _rect(g, xt, ly2 - H_IC / 2.0, 0.26, H_IC, GRIS)
    rotulo(g, xt + 0.32, ly2, "IC 95 %, recortado a [0, 1]", FS_T, GRIS)
    sin_efectos(g)
    g._element.recalculate_extents()
    return g


# ===========================================================================
# s06 — la tabla de las cinco preguntas
# ===========================================================================
def tabla_preguntas(s, l, t, w, filas, fracs, fs=11):
    """`tabla_ejes` del B9 con celdas de VARIOS párrafos.

    `filas` son listas de celdas, y cada celda una lista de párrafos `(texto, bold)`. El alto
    de cada fila se calcula **sumando** párrafos: `auditar()` del B9 toma el máximo y
    subestima (I2)."""
    ML, MR, MT, MB = 0.07, 0.05, 0.04, 0.04
    cab = [[("#", True)], [("Pregunta", True)], [("Qué decide la respuesta", True)]]
    todas = [cab] + list(filas)
    gf = s.shapes.add_table(len(todas), len(fracs), Inches(l), Inches(t), Inches(w),
                            Inches(0.4 * len(todas)))
    tbl = gf.table
    for ci, fr in enumerate(fracs):
        tbl.columns[ci].width = Inches(w * fr)
    tbl.first_row = False
    tbl.horz_banding = False
    altos = []
    for ri, fila in enumerate(todas):
        need = 0.0
        for ci, parrafos in enumerate(fila):
            cell = tbl.cell(ri, ci)
            cell.margin_left, cell.margin_right = Inches(ML), Inches(MR)
            cell.margin_top, cell.margin_bottom = Inches(MT), Inches(MB)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.fill.solid()
            cell.fill.fore_color.rgb = CUERPO if ri == 0 else (LINEA if ri % 2 else BLANCO)
            col = BLANCO if ri == 0 else TITULO
            tf = cell.text_frame
            tf.word_wrap = True
            util = w * fracs[ci] - ML - MR
            alto = 0.0
            for pi, (txt, bold) in enumerate(parrafos):
                p = tf.paragraphs[0] if pi == 0 else tf.add_paragraph()
                p.alignment = PP_ALIGN.LEFT
                ultimo = pi == len(parrafos) - 1
                p.space_after = Pt(0 if ultimo else 3)
                r = p.add_run()
                r.text = txt
                r.font.size = Pt(fs)
                r.font.bold = bold
                r.font.name = F
                r.font.color.rgb = col
                alto += wrap_lines(txt, util, fs, bold) * _lt(fs) + (0 if ultimo else 3 / 72.0)
            need = max(need, alto)
        altos.append(need + MT + MB + (0.10 if ri else 0.08))
    for ri, a in enumerate(altos):
        tbl.rows[ri].height = Inches(a)
    gf.height = Inches(sum(altos))
    return t + sum(altos)


# ===========================================================================
# Las láminas
# ===========================================================================
def cejilla(slide, tema):
    """`set_cejilla` del B9, y además les saca a los colores de sus runs las transformaciones.

    En s02 y s04 del molde el tema viene aclarado (`lumMod`/`lumOff` dentro del `srgbClr`), y
    `font.color.rgb` cambia el `val` pero conserva los hijos: la cejilla de las dos tablas salía
    `#97BEEB` y no `5293DE`. El B9 está cerrado y tiene el mismo tinte en su s2 y su s13."""
    sh = set_cejilla(slide, tema)
    for r in sh.text_frame.paragraphs[0].runs:
        for clr in r._r.iter(qn("a:srgbClr")):
            for hijo in list(clr):
                clr.remove(hijo)
    return sh


def lamina_objetivos(s, o1, o3, guion):
    cejilla(s, PROYECTO)
    set_titulo(s, "OBJETIVOS " + PERIODO)
    gf = _shape(s, "Google Shape;196;p29")
    set_encabezado(gf, ["Objetivo", "Entregable", "Fecha", "Estado"])
    alto, bajo = _o1(o1, 500, "alto"), _o1(o1, 500, "bajo")
    n_etq = int((o3.tier != "fuera").sum())
    n_vistas = int(o3.tier.isin(["train", "val"]).sum())
    llenar_tabla(gf, [
        ("Replicar el grado sin la marca del patólogo",
         "Solo HoVer-NeXt, orden por tamaño. En N = 500, unos %d mm² por lámina, reencuentra "
         "%d de %d marcas de alto grado y %d de %d de bajo"
         % (round(alto["carga_media_mm2_lamina"]), alto["recall"], alto["alcanzables"],
            bajo["recall"], bajo["alcanzables"]),
         FECHA_CIERRE, "Cerrado"),
        ("Cómo se determina el score",
         "El CAP no trae regla de cantidad ni de mayoría: separa los tres scores por la "
         "variación contra el epitelio mamario normal",
         FECHA_CIERRE, "Cerrado"),
        ("El CDIS antes que el grado",
         "La atención cae sobre el CDIS en las %d láminas con etiqueta, pero el fold usó %d para "
         "entrenar o elegir el checkpoint. En las que no usó, la localización no está mostrada"
         % (n_etq, n_vistas),
         FECHA_CIERRE, "Cerrado"),
    ])
    notes(s, guion)


def lamina_o1(s, o1, esc, guion):
    cejilla(s, "Grado nuclear")
    set_titulo(s, "El tamaño solo reencuentra el alto grado", nombre="Text 1")
    f = {g: _o1(o1, 500, g) for g in GRADOS + ["total"]}
    fin = set_cuerpo(s, [
        ("Sin la marca, solo HoVer-NeXt: ",
         "se ordenan por tamaño los núcleos epiteliales de cada lámina."),
        ("En N = 500, unos %d mm² por lámina: " % round(f["alto"]["carga_media_mm2_lamina"]),
         "%d de %d marcas de alto grado, %d de %d de moderado y %d de %d de bajo. El azar no "
         "pasa de %d en total."
         % (f["alto"]["recall"], f["alto"]["alcanzables"], f["moderado"]["recall"],
            f["moderado"]["alcanzables"], f["bajo"]["recall"], f["bajo"]["alcanzables"],
            int(f["total"]["nulo_p975"]))),
        ("Bajo da cero por lo que es bajo grado: ",
         "su núcleo no suele estar entre los más grandes de la lámina. Hace falta la "
         "dispersión."),
    ])
    if esc["n_laminas"] - esc["n_lam_5000"] != 2:
        raise SystemExit("el pie de O1 dice «salen dos láminas» y salen %d"
                         % (esc["n_laminas"] - esc["n_lam_5000"]))
    pie = [
        "Unidad: marca del patólogo, en %d láminas. Una marca cuenta como recuperada si el "
        "núcleo epitelial más cercano, con una tolerancia de %d µm entre la marca y ese núcleo, "
        "está entre los N más grandes de su lámina." % (esc["n_laminas"], int(TOL_VECINDAD_UM)),
        "Alcanzables: las %d de %d marcas que caen sobre un núcleo que HoVer-NeXt llamó "
        "epitelial. Punteada: percentil 97,5 del nulo por traslación rígida de las marcas, %d "
        "traslaciones por lámina." % (esc["alcanzables"], esc["marcas"], esc["n_trasl"]),
        "El eje termina en N = 2000: en 5000 salen dos láminas que no tienen tantos núcleos "
        "epiteliales, y los alcanzables de bajo caen de %d a %d."
        % (esc["bajo_2000"], esc["bajo_5000"]),
    ]
    l, _, w = G_CUERPO
    top, alto, y_pie = caja_figura(fin, pie, w)
    figura_o1(s, l, top, w, alto, o1)
    pie_lineas(s, l, y_pie, w, pie)
    notes(s, guion)


def lamina_o2(s, guion):
    cejilla(s, "Protocolo CAP")
    set_titulo(s, "El CAP no cuenta núcleos: mide variación", nombre="Text 1")
    fin = set_cuerpo(s, [
        ("Sin regla de cantidad ni de mayoría: ",
         "los tres scores de pleomorfismo se separan por cuánta variación hay contra el "
         "epitelio mamario normal."),
        ("Para el método: ",
         "el descriptor fiel al protocolo mide dispersión, y la mide contra epitelio normal."),
    ])
    # Sin el número de versión del protocolo: «1.2.0.0» dispara el barrido de punto decimal.
    pie = [
        "El protocolo no dice nada del grado que varía dentro de un mismo carcinoma: solo pide "
        "reportar aparte los carcinomas distintos que difieren en grado.",
        "Fuente: protocolo del CAP para biopsias de carcinoma invasivo de mama, páginas 4, 8, "
        "10 y 11. Las citas entre comillas son textuales.",
    ]
    l, _, w = G_CUERPO
    top, alto, y_pie = caja_figura(fin, pie, w)
    diagrama_o2(s, l, top, w, alto)
    pie_lineas(s, l, y_pie, w, pie)
    notes(s, guion)


def lamina_o3(s, d, guion):
    cejilla(s, "Localización del CDIS")
    set_titulo(s, "La atención cae sobre el CDIS ya visto", nombre="Text 1")
    etq = d[d.tier != "fuera"]
    test = d[d.tier == "test"].iloc[0]
    fuera = d[d.tier == "fuera"].iloc[0]
    n_vistas = int(d.tier.isin(["train", "val"]).sum())
    if not ((etq.auc > 0.5).all() and test.ic95_lo < 0.5 < test.ic95_hi
            and len(etq) - n_vistas == 1):
        raise SystemExit("O3: el cuerpo de la lámina ya no describe los datos")
    fin = set_cuerpo(s, [
        ("Las %d láminas con etiqueta dan AUC sobre 0,5: " % len(etq),
         "mediana %s y mínimo %s, pero el fold usó %d de ellas para entrenar o para elegir el "
         "checkpoint." % (num(etq.auc.median(), 3), num(etq.auc.min(), 3), n_vistas)),
        ("En las dos que no usó, la localización no está mostrada: ",
         "la de test tiene %d parches con CDIS y su intervalo contiene 0,5; la que quedó fuera "
         "del split da %s." % (int(test.n_marcados), num(fuera.auc, 3))),
    ])
    n_it = int(d.n_iter_nulo.mode().iloc[0])
    n110 = int(d[d.slide == "110616"].n_iter_nulo.iloc[0])
    # Unidad y AUC en dos párrafos: juntos envolvían y dejaban «anotada.» sola en un renglón
    pie = [
        "Unidad: parche. Un parche vale 1 si su centro cae dentro de un polígono de CDIS del "
        "patólogo.",
        "AUC con la rama de la clase verdadera del checkpoint de un fold; la B25-158899, sin "
        "etiqueta, con la rama si y confinada a su región anotada.",
        "Relleno: p < 0,05 contra %d traslaciones rígidas (%d en la 110616, cuyo p queda en el "
        "piso de ese nulo). †: offset sin verificar." % (n_it, n110),
    ]
    l, _, w = G_CUERPO
    top, alto, y_pie = caja_figura(fin, pie, w)
    figura_o3(s, l, top, w, alto, d)
    pie_lineas(s, l, y_pie, w, pie)
    notes(s, guion)


def lamina_preguntas(s, esc, guion):
    cejilla(s, "Preguntas abiertas")
    set_titulo(s, "Cinco preguntas para decidir cómo seguir", nombre="Text 1")
    fin = set_cuerpo(s, [
        ("En orden de lo que cuesta si se contestan tarde: ",
         "las dos primeras deciden qué mide el próximo período."),
    ])
    # Las filas son las de reunion_martes.md §5. `Tumor` y `NucleosBajoGrado` van literales:
    # son etiquetas del geojson del patólogo.
    filas = [
        [[("P1", True)],
         [("¿Qué región corresponde para medir el pleomorfismo?", True),
          ("Tumor no sirve: ninguna de las %d marcas de grado cae dentro de un polígono, de "
           "ninguna clase, y la mediana de distancia al Tumor más cercano es 2,9 mm."
           % esc["marcas"], False)],
         [("Sobre qué superficie corre la medición del grado. Hoy, la lámina entera.", False)]],
        [[("P2", True)],
         [("¿Las marcas de grado son pleomorfismo invasivo o grado nuclear de CDIS?", True),
          ("Siguen la etiqueta de pleomorfismo de la lámina: las 10 láminas con marcas de "
           "moderado tienen pleomorfismo score 2, y 8 láminas con marcas de grado no tienen "
           "CDIS.", False)],
         [("Qué máscara corresponde, y si se mide lo que se pidió.", False)]],
        [[("P3", True)],
         [("¿Se confirman tres conteos que cambian con el set completo?", True),
          ("NucleosBajoGrado son 16 marcas y no 25; las marcas de grado están en 22 láminas y "
           "no en 12; de las 30 láminas faltan 8, no 18.", False)],
         [("Qué conteos valen de acá en adelante.", False)]],
        [[("P4", True)],
         [("¿Cuáles son las 8 láminas que faltan para llegar a 30, y cuándo llegan?", True),
          ("Hoy hay marcas de grado en 22 láminas, %d de ellas medibles." % esc["n_laminas"],
           False)],
         [("Si el próximo período mide sobre 22 láminas o sobre 30.", False)]],
        [[("P5", True)],
         [("¿Cómo seguimos con «CDIS primero, grado después»?", True),
          ("La localización del CDIS no está mostrada en láminas que el fold no usó, y la "
           "B25-158899 no tiene fila en el CSV de CDIS.", False)],
         [("Si la cadena de dos etapas sigue sobre este checkpoint, y si la B25-158899 está "
           "en la cohorte.", False)]],
    ]
    l, _, w = G_CUERPO
    tabla_preguntas(s, l, fin + 0.22, w, filas, [0.06, 0.58, 0.36])
    notes(s, guion)


def lamina_tareas(s, guion):
    cejilla(s, PROYECTO)
    set_titulo(s, "Tareas del próximo período")
    gf = _shape(s, "Google Shape;196;p29")
    set_encabezado(gf, ["Objetivo", "Entregable", "Fecha"])
    fin = llenar_tabla(gf, [
        ("Medir la dispersión nuclear",
         "Dispersión del tamaño nuclear por lámina (coeficiente de variación y rango "
         "intercuartil) contra el proxy de epitelio normal, los núcleos epiteliales fuera de "
         "toda región anotada. Sobre la región que se decida en P1",
         FECHA_TAREA),
    ], min_h=1.0)
    frase = "El resto de las tareas depende de lo que se conteste a las cinco preguntas"
    add_textbox(s, Emu(gf.left).inches, fin + 0.35, text_w(frase, 14) + 0.20, 0.32,
                [(frase, 14, False, CUERPO)])
    notes(s, guion)


# ===========================================================================
# Las cuatro láminas de imagen (plan_deck_visual.md, paso 2)
# ===========================================================================
# Cada panel es un PNG propio, sin texto quemado, con su registro en `deck_imagenes.json`. El
# rótulo y la imagen salen del MISMO registro, así que no pueden cruzarse
# ([[sidecar-orden-no-es-el-de-la-figura]]); y como el PNG no trae letras, ningún rótulo pierde
# puntos al escalar ([[png-rotulos-quemados-pierden-pt]]). Cada figura va en un group shape,
# para que `auditar_grupos()` la mida y la zona de pie la vigile.
def leer_imagenes(o1, o3):
    """El JSON del render, verificado contra los números de las láminas que ya existen: los
    gates de la selección contra O1 en N = 500, y cada mapa de s09 contra su fila de O3."""
    d = json.load(open(JSON_IMG, encoding="utf-8"))
    sel = json.load(open(SEL_IMG, encoding="utf-8"))
    for g in GRADOS:
        f = _o1(o1, 500, g)
        if (sel["gates"]["recuperadas"][g], sel["gates"]["alcanzables"][g]) != \
                (f["recall"], f["alcanzables"]):
            raise SystemExit("imágenes: la selección no es la de O1 en N = 500 (%s)" % g)
    for r in d["s09"]["orden_dibujo"]:
        f = o3[o3.slide == r["slide"]]
        if len(f) != 1 or f.tier.iloc[0] != r["tier"] or abs(f.auc.iloc[0] - r["auc"]) > 6e-5 \
                or int(f.n_marcados.iloc[0]) != r["n_marcados"] \
                or bool(f.alineada.iloc[0]) != r["alineada"]:
            raise SystemExit("imágenes: el mapa de %s no es la fila de O3" % r["slide"])
    pngs = re.findall(r'"png": "([^"]+)"', json.dumps(d))
    faltan = [p for p in pngs if not os.path.isfile(os.path.join(ASSETS, p))]
    if faltan:
        raise SystemExit("imágenes: faltan %s; correr scripts/b10_deck_imagenes.py" % faltan)
    d["seleccion"] = sel
    print("  imágenes: %d PNG, gates de O1 y los tres AUC de O3 iguales" % len(pngs))
    return d


def tam_png(nombre):
    from PIL import Image
    with Image.open(os.path.join(ASSETS, nombre)) as im:
        return im.size


def foto(g, nombre, l, t, w=None, h=None):
    """PNG con su aspecto EXACTO: se da el ancho o el alto y el otro sale de la imagen, así que
    la caja nunca centra la foto con aire a los costados. Devuelve (ancho, alto, pulgadas por
    píxel del PNG)."""
    W, H = tam_png(nombre)
    if w is None:
        w = h * W / float(H)
    h = w * H / float(W)
    g.shapes.add_picture(os.path.join(ASSETS, nombre), Inches(l), Inches(t), Inches(w),
                         Inches(h))
    return w, h, w / float(W)


def marco(g, l, t, w, h, borde, ancho_pt=1.5, relleno=None):
    sp = g.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(l), Inches(t), Inches(w), Inches(h))
    if relleno is None:
        sp.fill.background()
    else:
        sp.fill.solid()
        sp.fill.fore_color.rgb = relleno
    sp.line.color.rgb = borde
    sp.line.width = Pt(ancho_pt)
    sp.shadow.inherit = False
    return sp


def simbolo_marca(g, cx, cy, d, recuperada):
    """El símbolo de marca de los PNG (`anillo()` del render de s05: tinta de radio 23, blanco
    de 18 y tinta de 13), dibujado nativo para la leyenda."""
    circulo(g, cx, cy, d, TITULO)
    circulo(g, cx, cy, d * 18 / 23.0, BLANCO)
    if recuperada:
        circulo(g, cx, cy, d * 13 / 23.0, TITULO)


def leyenda_fila(g, cx, y, items, fs=9):
    """Items `(dibujar(x, y), texto)` en una fila centrada en `cx`. Cada dibujo ocupa 0,20"."""
    anchos = [0.28 + text_w(t, fs) for _, t in items]
    total = sum(anchos) + 0.34 * (len(items) - 1)
    x = cx - total / 2.0
    for (dib, txt), a in zip(items, anchos):
        dib(x + 0.10, y)
        # el texto de `rotulo` empieza 0,02" a la derecha de su x (margen del cuadro)
        rotulo(g, x + 0.26, y, txt, fs, GRIS)
        x += a + 0.34


def expansion(g, pares):
    """Las rectas punteadas que abren un recuadro en su zoom (gramática del molde)."""
    for (x1, y1), (x2, y2) in pares:
        recta(g, x1, y1, x2, y2, TITULO, 1.0, MSO_LINE_DASH_STYLE.DASH)


def pct_txt(p):
    """Percentil con un decimal, redondeado como en la selección y el guion. Un 100,0 sólo si
    es el núcleo más grande de la lámina: 99,97 redondeado también daría 100,0."""
    t = num(p, 1)
    if t == "100,0" and p < 100.0:
        raise SystemExit("percentil %r se leería como el máximo de la lámina" % p)
    return t


def lamina_hovernext(s, img, guion):
    """s03: una ventana de 500 µm con cada núcleo pintado por clase, y su centro de 119 µm (un
    parche de CLAM) con los contornos. Los conteos van en una leyenda nativa a la derecha."""
    r = img["s03"]
    ctx, cen = r["orden_dibujo"]
    if (ctx["que"], cen["que"]) != ("contexto", "centro"):
        raise SystemExit("s03: el JSON no trae contexto y centro en ese orden")
    col = {x["grupo"]: _hex(x["color"]) for x in r["grupos"]}
    cejilla(s, "Detección de núcleos")
    set_titulo(s, "HoVer-NeXt encuentra y clasifica cada núcleo", nombre="Text 1")
    fin = set_cuerpo(s, [
        ("Cada núcleo es una instancia con su clase: ",
         "en %s µm hay %d, y %d son epiteliales, la clase que mide el grado."
         % (num(ctx["lado_um"], 0), ctx["n_nucleos"],
                        ctx["por_grupo"]["epitelial"])),
    ])
    pie = [
        "Clases del detector con los pesos de Lizard, sin validar en estas láminas. «Otras» junta "
        "sus cuatro clases minoritarias. Los colores son propios, no los del detector.",
        "Conteo: núcleos con al menos un píxel dentro del cuadrado. La ventana está centrada en "
        "la marca de alto grado con más núcleos epiteliales en su parche.",
        "El área no se compara entre clases: el detector corta cada clase con su propio umbral, "
        "y una plasmática sale más grande que una epitelial.",
    ]
    l, _, w = G_CUERPO
    top, alto, y_pie = caja_figura(fin, pie, w)
    g = s.shapes.add_group_shape()
    FS = 9
    nombres = {"epitelial": "epitelial", "linfocito": "linfocito", "conectivo": "conectivo",
               "otras": "otras"}
    t_marca = "marca de alto grado del patólogo"
    t_rec = "un parche de CLAM, centrado en la marca"
    W_NUM = text_w("119 µm", FS, True) + 0.20
    W_LEG = max(0.26 + max(text_w(v, FS, True) for v in nombres.values()) + 0.25 + 2 * W_NUM,
                0.30 + max(text_w(t_marca, FS), text_w(t_rec, FS)) + 0.10)
    G_PAN, G_LEG = 0.55, 0.45
    lab_ctx = "ventana de %s µm" % num(ctx["lado_um"], 0)
    lab_cen = "centro de %s µm: un parche de CLAM" % num(cen["lado_um"], 0)
    H_LAB = 0.08 + _lt(FS)
    P = min(alto - H_LAB, (w - W_LEG - G_PAN - G_LEG) / 2.0)
    x0 = l + (w - (2 * P + G_PAN + G_LEG + W_LEG)) / 2.0
    xb = x0 + P + G_PAN
    _, _, k = foto(g, ctx["png"], x0, top, w=P)
    foto(g, cen["png"], xb, top, w=P)
    rx0, ry0, rx1, ry1 = ctx["recuadro_px"]
    expansion(g, [((x0 + rx1 * k, top + ry0 * k), (xb, top)),
                  ((x0 + rx1 * k, top + ry1 * k), (xb, top + P))])
    yl = top + P + 0.08 + _lt(FS) / 2.0
    rotulo(g, x0 + P / 2.0, yl, lab_ctx, FS, GRIS, alin=PP_ALIGN.CENTER)
    rotulo(g, xb + P / 2.0, yl, lab_cen, FS, GRIS, alin=PP_ALIGN.CENTER)

    # leyenda: tabla de conteos con muestra de color, y los dos símbolos
    xl = xb + P + G_LEG
    PASO = 0.25
    filas = len(nombres) + 1
    h_leg = PASO * (filas + 1) + 0.16 + 2 * PASO
    y = top + max(0.0, (P - h_leg) / 2.0) + PASO / 2.0
    xr2 = xl + W_LEG
    xr1 = xr2 - W_NUM
    rotulo(g, xr1, y, lab_ctx.split(" de ")[1], FS, GRIS, bold=True, alin=PP_ALIGN.RIGHT)
    rotulo(g, xr2, y, "%s µm" % num(cen["lado_um"], 0), FS, GRIS, bold=True,
           alin=PP_ALIGN.RIGHT)
    for grupo, nombre in nombres.items():
        y += PASO
        _rect(g, xl, y - 0.08, 0.16, 0.16, col[grupo])
        rotulo(g, xl + 0.26, y, nombre, FS, TITULO)
        rotulo(g, xr1, y, "%d" % ctx["por_grupo"][grupo], FS, TITULO, alin=PP_ALIGN.RIGHT)
        rotulo(g, xr2, y, "%d" % cen["por_grupo"][grupo], FS, TITULO, alin=PP_ALIGN.RIGHT)
    for c in (ctx, cen):
        if sum(c["por_grupo"].values()) != c["n_nucleos"]:
            raise SystemExit("s03: los grupos no suman el total de la ventana %s" % c["que"])
    y += PASO
    recta(g, xl, y - PASO / 2.0, xr2, y - PASO / 2.0, LINEA, 0.75)
    rotulo(g, xl + 0.26, y, "total", FS, TITULO, bold=True)
    rotulo(g, xr1, y, "%d" % ctx["n_nucleos"], FS, TITULO, bold=True, alin=PP_ALIGN.RIGHT)
    rotulo(g, xr2, y, "%d" % cen["n_nucleos"], FS, TITULO, bold=True, alin=PP_ALIGN.RIGHT)
    y += PASO + 0.16
    simbolo_marca(g, xl + 0.08, y, 0.17, True)
    rotulo(g, xl + 0.26, y, t_marca, FS, GRIS)
    y += PASO
    marco(g, xl, y - 0.08, 0.16, 0.16, TITULO, 1.5)
    rotulo(g, xl + 0.26, y, t_rec, FS, GRIS)
    sin_efectos(g)
    g._element.recalculate_extents()
    pie_lineas(s, l, y_pie, w, pie)
    notes(s, guion)


def lamina_o1_mapa(s, img, guion):
    """s05: las dos láminas que eligió la regla, cada una con su miniatura y el zoom sobre sus
    marcas. Las cuentas de la carga y de las marcas van nativas debajo de cada par."""
    pares = img["s05"]["orden_dibujo"]
    if [p["grado"] for p in pares] != ["alto", "bajo"]:
        raise SystemExit("s05: el JSON no trae alto y bajo en ese orden")
    if any(p["cuenta"]["no_alcanzable"] for p in pares):
        raise SystemExit("s05: el pie dice que todas las marcas son alcanzables y no lo son")
    sel = {p["slide"]: p for p in img["seleccion"]["s05"]}
    a, b = pares
    cejilla(s, "Grado nuclear")
    set_titulo(s, "La carga de N = 500 sobre dos láminas", nombre="Text 1")
    fin = set_cuerpo(s, [
        ("En verde, la carga de N = 500: ",
         "los parches con los 500 núcleos epiteliales más grandes de la lámina."),
        ("Alto grado, %d de %d marcas dentro de la carga; bajo grado, %d de %d, "
         % (a["cuenta"]["recuperada"], a["n_marcas"], b["cuenta"]["recuperada"], b["n_marcas"]),
         "aunque %d parches de la carga caen en su zona ampliada."
         % b["zoom"]["parches_en_zoom"]),
    ])
    # la 129741 tiene dos regiones de escaneo: cuántos parches de la carga caen en la que tiene
    # las marcas, con el mismo intervalo que usó O3
    reg = []
    for p in pares:
        if p["slide"] in REGION_ANOTADA:
            lo, hi = REGION_ANOTADA[p["slide"]]
            en = sum(lo <= gy * img["seleccion"]["lado_parche_px"] < hi
                     for _gx, gy in sel[p["slide"]]["parches"])
            if not all(lo <= m["y"] < hi for m in sel[p["slide"]]["marcas"]):
                raise SystemExit("s05: %s tiene marcas fuera de su región anotada" % p["slide"])
            reg.append("la %s tiene dos regiones de escaneo del mismo tejido, y %d de sus %d "
                       "parches caen en la que tiene las marcas" % (p["slide"], en, p["n_parches"]))
    if len(reg) != 1:
        raise SystemExit("s05: el pie espera exactamente una lámina con dos regiones")
    pie = [
        "Carga: parches de 256 px que contienen al menos uno de los 500 núcleos. Unidad de las "
        "cuentas: marca del patólogo; las %d marcas de estas dos láminas son alcanzables."
        % (a["n_marcas"] + b["n_marcas"]),
        reg[0][0].upper() + reg[0][1:] + ".",
        "Las dos láminas salen de una regla: la de cada grado con más marcas alcanzables y "
        "alineación verificada. Un núcleo grande sin marca no es un falso positivo: el patólogo "
        "marca ejemplares.",
    ]
    l, _, w = G_CUERPO
    top, alto, y_pie = caja_figura(fin, pie, w)
    g = s.shapes.add_group_shape()
    FS, FS_H = 9, 9.5
    H_LEG = 0.30
    H_HEAD = _lt(FS_H) + 0.08
    H_LAB = 0.06 + 2 * _lt(FS)
    G_IN, G_PAR = 0.35, 0.60
    asp = []
    for p in pares:
        W, H = tam_png(p["miniatura"]["png"])
        Wz, Hz = tam_png(p["zoom"]["png"])
        asp += [W / float(H), Wz / float(Hz)]
    H = min(alto - H_LEG - H_HEAD - H_LAB, (w - 2 * G_IN - G_PAR) / sum(asp))
    total = H * sum(asp) + 2 * G_IN + G_PAR
    verde = {x["grupo"]: _hex(x["color"]) for x in img["s03"]["grupos"]}["epitelial"]

    leyenda_fila(g, l + w / 2.0, top + H_LEG / 2.0 - 0.04, [
        (lambda x, y: marco(g, x - 0.08, y - 0.08, 0.16, 0.16, verde, 1.25, verde),
         "parche de la carga"),
        (lambda x, y: simbolo_marca(g, x, y, 0.17, True), "marca recuperada"),
        (lambda x, y: simbolo_marca(g, x, y, 0.17, False), "marca no recuperada"),
        (lambda x, y: marco(g, x - 0.08, y - 0.08, 0.16, 0.16, TITULO, 1.5),
         "zona ampliada, %s mm de lado" % num(a["zoom"]["lado_mm"], 2)),
    ])
    x = l + (w - total) / 2.0
    y_img = top + H_LEG + H_HEAD
    for p, nombre in zip(pares, ("alto grado", "bajo grado")):
        xp = x
        circulo(g, xp + 0.055, top + H_LEG + H_HEAD / 2.0 - 0.02, 0.11, COL_GRADO[p["grado"]])
        rotulo(g, xp + 0.14, top + H_LEG + H_HEAD / 2.0 - 0.02, "%s · %s" % (nombre, p["slide"]),
               FS_H, TITULO, bold=True)
        wm, hm, km = foto(g, p["miniatura"]["png"], x, y_img, h=H)
        xz = x + wm + G_IN
        foto(g, p["zoom"]["png"], xz, y_img, h=H)
        rx0, ry0, rx1, ry1 = p["miniatura"]["recuadro_px"]
        expansion(g, [((x + rx1 * km, y_img + ry0 * km), (xz, y_img)),
                      ((x + rx1 * km, y_img + ry1 * km), (xz, y_img + H))])
        y1 = y_img + H + 0.06 + _lt(FS) / 2.0
        rotulo(g, xp, y1, "carga: %d parches = %s mm²" % (p["n_parches"], num(p["carga_mm2"], 2)),
               FS, GRIS)
        rotulo(g, xp, y1 + _lt(FS), "marcas recuperadas: %d de %d"
               % (p["cuenta"]["recuperada"], p["n_marcas"]), FS, TITULO, bold=True)
        x = xz + H + G_PAR
    sin_efectos(g)
    g._element.recalculate_extents()
    pie_lineas(s, l, y_pie, w, pie)
    notes(s, guion)


def lamina_o1_galeria(s, img, o1, guion):
    """s06: los doce núcleos de la selección, en dos filas (recuperadas y no recuperadas) y con
    los grados como columnas, que es lo que deja los paneles a ~1,2" en vez de ~0,9"."""
    pan = img["s06"]["orden_dibujo"]
    esperado = {"alto": ["recuperada:mínimo", "recuperada:mediano", "recuperada:máximo",
                         "no_recuperada:primer cuartil", "no_recuperada:mediano"],
                "moderado": ["recuperada:mínimo", "recuperada:mediano", "recuperada:máximo",
                             "no_recuperada:primer cuartil", "no_recuperada:mediano"],
                "bajo": ["no_recuperada:primer cuartil", "no_recuperada:mediano"]}
    for gr, cols in esperado.items():
        if [p["columna"] for p in pan if p["grado"] == gr] != cols:
            raise SystemExit("s06: los paneles de %s no vienen en el orden de la regla" % gr)
    nr = {gr: [p for p in pan if p["grado"] == gr and p["estado"] == "no_recuperada"]
          for gr in GRADOS}
    cejilla(s, "Grado nuclear")
    set_titulo(s, "Las marcas, núcleo a núcleo", nombre="Text 1")
    fin = set_cuerpo(s, [
        ("Recuperadas y no recuperadas se parecen: ",
         "las no recuperadas de alto grado quedan en los percentiles %s y %s."
         % tuple(pct_txt(p["percentil"]) for p in nr["alto"])),
        ("Bajo grado no tiene ninguna recuperada: ",
         "las dos del panel quedan en los percentiles %s y %s."
         % tuple(pct_txt(p["percentil"]) for p in nr["bajo"])),
    ])
    pie = [
        "Cada panel mide %s µm de lado, todos a la misma escala. Contorno grueso: el núcleo bajo "
        "la marca; fino: los demás de los 500 más grandes que caen en el panel."
        % num(pan[0]["lado_um"], 0),
        "Recuperadas: puestos mínimo, mediano y máximo; no recuperadas: primer cuartil y "
        "mediana; una lámina por panel. Puesto y percentil de área son dentro de la propia lámina.",
        "Sólo marcas alcanzables de láminas con alineación verificada. Un núcleo grande sin marca "
        "no es un falso positivo: el patólogo marca ejemplares.",
    ]
    l, _, w = G_CUERPO
    top, alto, y_pie = caja_figura(fin, pie, w)
    g = s.shapes.add_group_shape()
    FS, FS_H, FS_R = 8.5, 9.5, 9.5
    slots = {"alto": 3, "moderado": 3, "bajo": 2}
    G_S, G_GR, G_FILA = 0.08, 0.34, 0.12
    W_ROW = max(text_w("no recuperadas", FS_R, True), text_w("recuperadas", FS_R, True),
                text_w("en N = 500", FS_R)) + 0.30
    H_HEAD = _lt(FS_H) + 0.14
    H_LAB = 0.05 + 2 * _lt(FS)
    n_s = sum(slots.values())
    n_gap = sum(v - 1 for v in slots.values())
    T = min((w - W_ROW - 2 * G_GR - n_gap * G_S) / n_s, (alto - H_HEAD - 2 * H_LAB - G_FILA) / 2)
    total = W_ROW + n_s * T + n_gap * G_S + 2 * G_GR
    x = l + (w - total) / 2.0
    ys = [top + H_HEAD, top + H_HEAD + T + H_LAB + G_FILA]
    rotulo(g, x + W_ROW - 0.14, ys[0] + T / 2.0 - _lt(FS_R) / 2.0, "recuperadas", FS_R, TITULO,
           bold=True, alin=PP_ALIGN.RIGHT)
    rotulo(g, x + W_ROW - 0.14, ys[0] + T / 2.0 + _lt(FS_R) / 2.0, "en N = 500", FS_R, GRIS,
           alin=PP_ALIGN.RIGHT)
    rotulo(g, x + W_ROW - 0.14, ys[1] + T / 2.0, "no recuperadas", FS_R, TITULO, bold=True,
           alin=PP_ALIGN.RIGHT)
    x += W_ROW
    for gr in GRADOS:
        f = _o1(o1, 500, gr)
        ancho = slots[gr] * T + (slots[gr] - 1) * G_S
        circulo(g, x + 0.055, top + _lt(FS_H) / 2.0, 0.11, COL_GRADO[gr])
        rotulo(g, x + 0.14, top + _lt(FS_H) / 2.0, "%s · %d de %d recuperadas"
               % (gr, f["recall"], f["alcanzables"]), FS_H, TITULO, bold=True)
        _rect(g, x, top + _lt(FS_H) + 0.05, ancho, 0.03, COL_GRADO[gr])
        for fila, estado in enumerate(("recuperada", "no_recuperada")):
            ps = [p for p in pan if p["grado"] == gr and p["estado"] == estado]
            if not ps:
                rotulo(g, x + ancho / 2.0, ys[fila] + T / 2.0, "ninguna", FS_R, GRIS, italic=True,
                       alin=PP_ALIGN.CENTER)
                continue
            for j, p in enumerate(ps):
                xt = x + j * (T + G_S)
                foto(g, p["png"], xt, ys[fila], w=T)
                # sin la lámina: a ~1" por panel no entra junto al puesto, y el pie ya dice que
                # es una por panel (queda en `deck_imagenes.json`)
                l1 = "puesto %d" % p["puesto"]
                l2 = "percentil %s" % pct_txt(p["percentil"])
                if max(text_w(l1, FS, True), text_w(l2, FS)) + 0.20 > T + G_S:
                    raise SystemExit("s06: el rótulo «%s» no entra bajo su panel" % l1)
                yl = ys[fila] + T + 0.05 + _lt(FS) / 2.0
                rotulo(g, xt - 0.02, yl, l1, FS, TITULO, bold=True)
                rotulo(g, xt - 0.02, yl + _lt(FS), l2, FS, GRIS)
        x += ancho + G_GR
    sin_efectos(g)
    g._element.recalculate_extents()
    pie_lineas(s, l, y_pie, w, pie)
    notes(s, guion)


def lamina_o3_mapas(s, img, guion):
    """s09: por lámina, el mapa entero como localizador y un zoom de 1,9 mm sobre su polígono
    de CDIS con más parches. La leyenda va en una columna a la derecha: en una fila arriba le
    robaba alto a los zooms, que es lo que la lámina existe para mostrar."""
    r = img["s09"]["orden_dibujo"]
    if [x["tier"] for x in r] != ["train", "test", "fuera"]:
        raise SystemExit("s09: el JSON no trae train, test y fuera en ese orden")
    tr, te, fu = r
    sin_parches = sum(1 for n in fu["zoom"]["parches_por_poligono"] if n == 0)
    if sin_parches != 1 or fu["alineada"]:
        raise SystemExit("s09: el cuerpo dice que un polígono de la %s, sin verificar, no contiene "
                         "parches" % fu["slide"])
    cejilla(s, "Localización del CDIS")
    set_titulo(s, "Dónde mira la atención en tres láminas", nombre="Text 1")
    fin = set_cuerpo(s, [
        ("En la de train, AUC %s: " % num(tr["auc"], 3),
         "los parches dentro del CDIS están entre los de más atención de la lámina."),
        ("En las que el fold no usó no se lee: ",
         "test tiene %d parches con CDIS, y un polígono de la de fuera del split no contiene "
         "ninguno." % te["n_marcados"]),
    ])
    # dos renglones y no tres: el alto que se ahorra va a los zooms
    pie = [
        "Atención del checkpoint de un fold, rama de la clase verdadera; la %s, sin etiqueta, con "
        "la rama si y sólo su región anotada. Color: percentil de atención dentro de la lámina."
        % fu["slide"],
        "Train: el modelo ya la vio. †: alineación sin verificar. Unidad del AUC: parche, positivo "
        "si su centro cae dentro de un polígono de CDIS. Zoom de %d parches, centrado en el "
        "polígono con más parches." % round(tr["zoom"]["lado_px"] / 256.0),
    ]
    l, _, w = G_CUERPO
    top, alto, y_pie = caja_figura(fin, pie, w)
    g = s.shapes.add_group_shape()
    FS = 9
    TIER = {"train": "train", "test": "test", "fuera": "fuera del split"}
    t_pol = "polígono de CDIS del patólogo"
    t_zona = "zona ampliada, %s mm de lado" % num(tr["zoom"]["lado_mm"], 1)
    W_LEG = 0.38 + max(text_w(t_pol, FS), text_w(t_zona, FS),
                       text_w("percentil dentro de la lámina", FS)) + 0.10
    G_COL, G_LEG, H_MAP, G_EXP = 0.40, 0.45, 0.62, 0.22
    H_LAB = 0.06 + 2 * _lt(FS)
    Z = min((w - W_LEG - G_LEG - 2 * G_COL) / 3.0, alto - H_MAP - G_EXP - H_LAB)
    total = 3 * Z + 2 * G_COL + G_LEG + W_LEG
    x = l + (w - total) / 2.0
    yz = top + H_MAP + G_EXP
    for p in r:
        Wm, Hm = tam_png(p["mapa"]["png"])
        if Wm / float(Hm) > Z / H_MAP:
            wm, hm, km = Z, Z * Hm / float(Wm), Z / float(Wm)
        else:
            wm, hm, km = H_MAP * Wm / float(Hm), H_MAP, H_MAP / float(Hm)
        xm, ym = x + (Z - wm) / 2.0, top + (H_MAP - hm)
        foto(g, p["mapa"]["png"], xm, ym, w=wm)
        foto(g, p["zoom"]["png"], x, yz, w=Z)
        rx0, ry0, rx1, ry1 = p["mapa"]["recuadro_px"]
        expansion(g, [((xm + rx0 * km, ym + ry1 * km), (x, yz)),
                      ((xm + rx1 * km, ym + ry1 * km), (x + Z, yz))])
        y1 = yz + Z + 0.06 + _lt(FS) / 2.0
        circulo(g, x + 0.055, y1, 0.11, COL_TIER[p["tier"]])
        rotulo(g, x + 0.14, y1, "%s · %s%s" % (TIER[p["tier"]], p["slide"],
                                               "" if p["alineada"] else "  †"),
               FS, TITULO, bold=True)
        rotulo(g, x + 0.14, y1 + _lt(FS), "AUC %s · %d parches con CDIS"
               % (num(p["auc"], 3), p["n_marcados"]), FS, GRIS)
        x += Z + G_COL
    # leyenda: la rampa del B9, el polígono y el recuadro
    xl = x - G_COL + G_LEG
    y = yz + Z / 2.0 - 0.55
    rotulo(g, xl - 0.02, y, "atención", FS, TITULO, bold=True)
    y += 0.24
    W_R = W_LEG - 0.10
    paso = W_R / float(len(TURBO))
    for i, c in enumerate(TURBO):
        _rect(g, xl + i * paso, y - 0.07, paso + 0.005, 0.14, _rgb(c))
    y += 0.20
    rotulo(g, xl - 0.02, y, "baja", FS, GRIS)
    rotulo(g, xl + W_R + 0.02, y, "alta", FS, GRIS, alin=PP_ALIGN.RIGHT)
    y += _lt(FS)
    rotulo(g, xl - 0.02, y, "percentil dentro de la lámina", FS, GRIS)
    y += 0.34
    for dd, colr, ancho in ((0.0, TITULO, 2.5), (0.035, BLANCO, 1.0)):
        ov = g.shapes.add_shape(MSO_SHAPE.OVAL, Inches(xl + dd), Inches(y - 0.09 + dd),
                                Inches(0.26 - 2 * dd), Inches(0.18 - 2 * dd))
        ov.fill.background()
        ov.line.color.rgb = colr
        ov.line.width = Pt(ancho)
        ov.shadow.inherit = False
    rotulo(g, xl + 0.34, y, t_pol, FS, GRIS)
    y += 0.28
    marco(g, xl + 0.05, y - 0.08, 0.16, 0.16, TITULO, 1.5)
    rotulo(g, xl + 0.34, y, t_zona, FS, GRIS)
    sin_efectos(g)
    g._element.recalculate_extents()
    pie_lineas(s, l, y_pie, w, pie)
    notes(s, guion)


# ===========================================================================
# QA propio: lo que el del B9 no ve
# ===========================================================================
def _todas(shapes):
    for sh in shapes:
        yield sh
        if sh.shape_type == MSO_SHAPE_TYPE.GROUP:
            yield from _todas(sh.shapes)


def _alto_parrafos(tf, ancho):
    """Alto del texto de un cuadro SUMANDO párrafos, cada tramo medido con su peso."""
    alto, chico = 0.0, None
    pars = [p for p in tf.paragraphs if p.runs]
    for i, p in enumerate(pars):
        sz = max((r.font.size.pt for r in p.runs if r.font.size), default=12)
        chico = sz if chico is None else min(chico, sz)
        tramos = [(r.text, bool(r.font.bold)) for r in p.runs]
        alto += wrap_lines_mixto(tramos, max(ancho, 0.2), sz) * _lt(sz)
        if i < len(pars) - 1 and p.space_after is not None:
            alto += p.space_after.pt / 72.0
    return alto, chico


def auditar_grupos(prs, saltar_idx=(1,)):
    """Las mismas medidas que `auditar()` del B9, pero ENTRANDO en los grupos, y las tablas de
    varios párrafos por celda medidas sumando."""
    problemas = []
    for idx, slide in enumerate(prs.slides, start=1):
        if idx in saltar_idx:
            continue
        pie = None
        for sh in slide.shapes:
            if sh.name == "Google Shape;287;p7":
                pie = Emu(sh.top).inches
        for top in slide.shapes:
            if top.shape_type == MSO_SHAPE_TYPE.GROUP:
                for sh in _todas(top.shapes):
                    if sh.shape_type == MSO_SHAPE_TYPE.GROUP:
                        continue
                    l, t = Emu(sh.left).inches, Emu(sh.top).inches
                    w, h = Emu(sh.width).inches, Emu(sh.height).inches
                    if l < -0.02 or t < -0.02 or l + w > SW + 0.02 or t + h > SH + 0.02:
                        problemas.append("s%02d  grupo: fuera del lienzo %s" % (idx, sh.name))
                    if getattr(sh, "has_text_frame", False) and sh.text_frame.text.strip():
                        tf = sh.text_frame
                        ins = Emu(tf.margin_left).inches + Emu(tf.margin_right).inches
                        alto, chico = _alto_parrafos(tf, w - ins)
                        if alto > h + 0.03:
                            problemas.append("s%02d  grupo: texto que no entra, sobra %.2f\" en «%s»"
                                             % (idx, alto - h, tf.text[:44]))
                        if chico is not None and chico < 7.0:
                            problemas.append("s%02d  grupo: texto a %.1f pt" % (idx, chico))
                    if pie is not None and t + h > pie + 0.02:
                        problemas.append("s%02d  grupo: %s cruza la zona de pie (%.2f > %.2f)"
                                         % (idx, sh.name, t + h, pie))
            if top.has_table:
                tbl = top.table
                anchos = [Emu(c.width).inches for c in tbl.columns]
                for ri, row in enumerate(tbl.rows):
                    need = 0.0
                    for ci, cell in enumerate(row.cells):
                        a, _ = _alto_parrafos(cell.text_frame, _util(cell, anchos[ci]))
                        need = max(need, a + Emu(cell.margin_top).inches
                                   + Emu(cell.margin_bottom).inches)
                    if need > Emu(row.height).inches + 0.02:
                        problemas.append("s%02d  fila %d corta sumando párrafos: pide %.2f\", "
                                         "tiene %.2f\"" % (idx, ri, need,
                                                           Emu(row.height).inches))
                fondo = Emu(top.top).inches + sum(Emu(r.height).inches for r in tbl.rows)
                if pie is not None and fondo > pie + 0.02:
                    problemas.append("s%02d  la tabla cruza la zona de pie" % idx)
    if problemas:
        print("  GRUPOS Y TABLAS: %d avisos" % len(problemas))
        for p in problemas:
            print("   ·", p)
    else:
        print("  GRUPOS Y TABLAS: sin avisos")
    return problemas


PROHIBIDO = [
    (re.compile(r"\d+\.\d+"), "punto decimal"),
    (re.compile("[—–]"), "raya"),
    (re.compile("palanca", re.I), "«palanca»"),
    (re.compile(r"Sebasti[aá]n|Benjam[ií]n|sgaete|\bB(?:9|10)\b|\bjob\b", re.I),
     "nombre o jerga interna"),
]


def barrer_xml(path, prs):
    """Red de respaldo sobre el `.pptx` YA GUARDADO: todo `<a:t>` de cada lámina y de sus notas,
    grupos y celdas incluidos. La portada se salta (su titular es copy de la empresa y trae un
    «—»), pero sus notas no, que son nuestras. Además, ningún carácter fuera del cmap de Barlow
    (K1): un glifo que falta cae a otra fuente y `text_w()` no lo ve."""
    cmap = set(TTFont(os.path.join(BARLOW_DIR, "Barlow-Regular.ttf")).getBestCmap())
    malos = []
    with zipfile.ZipFile(path) as z:
        for idx, sl in enumerate(prs.slides, start=1):
            partes = [] if idx == 1 else [("lámina", sl.part.partname)]
            if sl.has_notes_slide:
                partes.append(("notas", sl.notes_slide.part.partname))
            for que, pn in partes:
                xml = z.read(str(pn).lstrip("/")).decode("utf-8")
                txt = "\n".join(html.unescape(m) for m in
                                re.findall(r"<a:t(?:\s[^>]*)?>([^<]*)</a:t>", xml))
                for rx, cual in PROHIBIDO:
                    for m in rx.finditer(txt):
                        ctx = txt[max(0, m.start() - 25):m.end() + 25].replace("\n", " ")
                        malos.append("s%02d %s  %s: «%s»" % (idx, que, cual, ctx))
                fuera = sorted({c for c in txt if ord(c) >= 32 and ord(c) not in cmap})
                if fuera:
                    malos.append("s%02d %s  glifos que Barlow no trae: %s"
                                 % (idx, que, " ".join("U+%04X" % ord(c) for c in fuera)))
    if malos:
        print("  XML: %d avisos" % len(malos))
        for m in malos:
            print("   ·", m)
    else:
        print("  XML: sin rayas, decimales con punto, nombres ni glifos fuera de Barlow")
    return malos


# ===========================================================================
def main():
    o1 = leer_o1()
    o3 = leer_o3()
    esc = leer_escalera()
    guion = leer_guion()
    f5 = {g: _o1(o1, 500, g) for g in GRADOS + ["total"]}
    etq = o3[o3.tier != "fuera"]
    print("Deck de la reunión · %s · %s" % (PROYECTO, PERIODO))
    print("  O1: N = 500, %s mm² por lámina · alto %d/%d · moderado %d/%d · bajo %d/%d · "
          "p97,5 del nulo %d"
          % (num(f5["alto"]["carga_media_mm2_lamina"], 2), f5["alto"]["recall"],
             f5["alto"]["alcanzables"], f5["moderado"]["recall"], f5["moderado"]["alcanzables"],
             f5["bajo"]["recall"], f5["bajo"]["alcanzables"], int(f5["total"]["nulo_p975"])))
    print("  O1: %d láminas, %d de %d alcanzables; en N = 5000 quedan %d y bajo cae a %d"
          % (esc["n_laminas"], esc["alcanzables"], esc["marcas"], esc["n_lam_5000"],
             esc["bajo_5000"]))
    print("  O3: %d con etiqueta, mediana %s, mínimo %s; B25-158899 %s"
          % (len(etq), num(etq.auc.median(), 3), num(etq.auc.min(), 3),
             num(o3[o3.tier == "fuera"].auc.iloc[0], 3)))

    img = leer_imagenes(o1, o3)

    prs = Presentation(TPL)
    s01, s02, s03, s04 = list(prs.slides)
    sHN, sO1, sMA, sGA, sO2, sO3, sMP, sPR = [clonar_s03(prs, s03) for _ in range(8)]

    lamina_objetivos(s02, o1, o3, guion["s02"])
    lamina_hovernext(sHN, img, guion["s03"])
    lamina_o1(sO1, o1, esc, guion["s04"])
    lamina_o1_mapa(sMA, img, guion["s05"])
    lamina_o1_galeria(sGA, img, o1, guion["s06"])
    lamina_o2(sO2, guion["s07"])
    lamina_o3(sO3, o3, guion["s08"])
    lamina_o3_mapas(sMP, img, guion["s09"])
    lamina_preguntas(sPR, esc, guion["s10"])
    lamina_tareas(s04, guion["s11"])
    notes(s01, guion["s01"])

    borrar_slide(prs, s03)                      # trae el ejemplo de otra persona
    reordenar(prs, [s01, s02, sHN, sO1, sMA, sGA, sO2, sO3, sMP, sPR, s04])

    forzar_barlow(prs)
    problemas = auditar(prs)
    problemas += barrer_rayas(prs)
    problemas += auditar_grupos(prs)
    prs.save(OUT)
    problemas += barrer_xml(OUT, prs)
    print("  escrito: %s" % os.path.basename(OUT))
    return 1 if problemas else 0


if __name__ == "__main__":
    sys.exit(main())
