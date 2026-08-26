#!/usr/bin/env python
"""generate_b9_deck.py — el deck del período sobre la plantilla oficial nueva.

Registro: **executive deck en inglés**, no deck técnico de sprint. Cuenta un período con la
gramática de la plantilla: qué me propuse (OBJECTIVES), qué salió (dos láminas de contenido),
qué sigue (Tasks for the next period).

El método es lo que lo separa de los seis decks anteriores: **se RELLENA en sitio**, no se
reconstruye. `base_from_template()` de `generate_b8_deck.py` abría el template y le BORRABA
las láminas para dibujar todo de cero; acá no, porque las tablas de s02 y s04 vienen con las
filas de cuerpo vacías pero **ya estilizadas** (relleno de cabecera, bordes por celda,
márgenes de 22860 EMU, `anchor="ctr"`, 16 pt bold blanco) y reproducir eso a mano es trabajo
perdido y una fuente de diferencias contra el molde. Detalle y verificación:
`docs/plantilla_oficial.md` §7.

Sigue en pie el motivo de siempre para abrir el `.pptx` en vez de usar `Presentation()`: la
plantilla **embebe Barlow** ([[deck-template-fuentes-embebidas]]) y un deck construido desde
cero la pierde. Y sigue en pie `forzar_barlow()`, porque el `fontScheme` del theme de ESTA
plantilla también es Arial.

Fuentes de los números, leídas por el script y no transcritas a mano:
  - `results/b9_cruce_94/por_lamina.csv` y `recall_por_tolerancia_agregado.csv`
  - `sprints/B9_sprint9/mitosis_12_laminas/cruce_94.md`
  - `sprints/B9_sprint9/hovernext_tareas/inventario_tareas.md`

El guion vive en `guion_b9.md` y se aplica desde ahí: ese archivo es la fuente y las notas
del `.pptx` son derivadas.

Uso:
    PYTHONPATH=/media/administrador/Storage1/sdonoso/clam_testing2/.pylibs \
      /home/sdonoso/miniconda3/envs/clam_latest/bin/python generate_b9_deck.py
"""
import copy
import csv
import os
import re
import sys

from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_SHAPE_TYPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

# ---------------------------------------------------------------------------
# Constantes del período
# ---------------------------------------------------------------------------
FECHA_ARCHIVO = "20260908"          # fin del período = fecha de la reunión
AUTOR = "Ernesto Gamero"
PROYECTO = "Nuclear Detection"      # NO «Mitosis Detection»: ése es el rótulo con el que
                                    # otra persona del equipo presenta su detector, y es
                                    # literalmente el ejemplo que trae la plantilla
PERIODO = "25/08/2026 - 08/09/2026"

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
TPL = os.path.join(RAIZ, "papers", "presentations",
                   "[AAAAMMDD] [Nombre Apellido] [Image-to-text].pptx")
AQUI = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(AQUI, "[%s] [%s] [%s].pptx" % (FECHA_ARCHIVO, AUTOR, PROYECTO))
GUION = os.path.join(AQUI, "guion_b9.md")
CSV_LAMINA = os.path.join(RAIZ, "results", "b9_cruce_94", "por_lamina.csv")
CSV_TOL = os.path.join(RAIZ, "results", "b9_cruce_94", "recall_por_tolerancia_agregado.csv")

SW, SH = 13.3333, 7.5

# ---------------------------------------------------------------------------
# Paleta de la plantilla oficial (docs/plantilla_oficial.md §4)
# ---------------------------------------------------------------------------
TITULO = RGBColor(0x1A, 0x1A, 0x2E)
CUERPO = RGBColor(0x1B, 0x4F, 0x8C)
ACENTO = RGBColor(0x52, 0x93, 0xDE)
SEP = RGBColor(0x9A, 0xA3, 0xB4)
LINEA = RGBColor(0xE4, 0xE9, 0xEC)
BLANCO = RGBColor(0xFF, 0xFF, 0xFF)

F = "Barlow"
PT_TITULO, PT_CEJILLA, PT_CUERPO = 40, 12, 16
PT_CELDA, PT_PIE = 12, 9

# Geometría verificada sobre el archivo (docs/plantilla_oficial.md §5)
G_CEJILLA = (0.580, 0.380, 9.00, 0.30)
G_TITULO_S03 = (0.575, 0.668, 12.44, 0.72)
G_CUERPO = (0.625, 1.639, 12.097)
T_PIE_S03 = 6.72                    # zona de pie de s03: nada la cruza
# Ojo: `Google Shape;287;p7` NO es una barra 1B4F8C, es un cuadro de texto de pie VACÍO
# (`<a:noFill/>` y `<a:ln><a:noFill/></a:ln>`, verificado en el XML). Lo único que se ve
# ahí es la línea E4E9EC de 7,079. Se respeta como límite igual, porque es el pie.

A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"


# ===========================================================================
# Medición de texto real, con los TTF de Barlow bajo containment
# ===========================================================================
# Portado tal cual de generate_b8_deck.py:708. Es la única capa de QA que ve un desborde:
# un chequeo de bounding boxes da «todo limpio» sobre texto que se sale de su caja
# ([[deck-qa-puntos-ciegos-chequeo]]).
BARLOW_DIR = "/media/administrador/Storage1/sdonoso/clam_testing2/fonts/barlow"
_FCACHE = {}
_MEDIDA = 40


def _face(bold):
    from PIL import ImageFont
    key = bool(bold)
    if key not in _FCACHE:
        nombre = "Barlow-Bold.ttf" if bold else "Barlow-Regular.ttf"
        _FCACHE[key] = ImageFont.truetype(os.path.join(BARLOW_DIR, nombre), _MEDIDA)
    return _FCACHE[key]


def text_w(txt, size, bold=False):
    """Ancho del texto en pulgadas de la lámina (72 pt/in)."""
    f = _face(bold)
    limpio = "".join(c if f.getbbox(c) else "n" for c in txt)
    return f.getlength(limpio) / _MEDIDA * size / 72.0


def wrap_lines(txt, ancho, size, bold=False):
    """Cuántas líneas ocupa `txt` en `ancho` pulgadas (wrap por palabra)."""
    if not txt.strip():
        return 1
    n, actual = 1, ""
    for palabra in txt.split(" "):
        cand = (actual + " " + palabra).strip()
        if actual and text_w(cand, size, bold) > ancho:
            n += 1
            actual = palabra
        else:
            actual = cand
    return n


def _alto_bloque(lineas, ancho, size, bold=False, space_after=3):
    total = 0.0
    for ln in lineas:
        total += wrap_lines(ln, ancho, size, bold) * size * 1.22 / 72.0 + space_after / 72.0
    return total


# ===========================================================================
# Primitivas
# ===========================================================================
def _set_runs(tf, lines, anchor=MSO_ANCHOR.TOP, space_after=3):
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    for i, ln in enumerate(lines):
        txt, sz, bold, col = ln[0], ln[1], ln[2], ln[3]
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = ln[4] if len(ln) > 4 else PP_ALIGN.LEFT
        p.space_after = Pt(space_after)
        r = p.add_run()
        r.text = txt
        r.font.size = Pt(sz)
        r.font.bold = bold
        r.font.name = F
        r.font.color.rgb = col


def add_textbox(slide, l, t, w, h, lines, anchor=MSO_ANCHOR.TOP, space_after=3):
    tb = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tb.text_frame.margin_left = Inches(0.02)
    tb.text_frame.margin_right = Inches(0.02)
    tb.text_frame.margin_top = Inches(0)
    tb.text_frame.margin_bottom = Inches(0)
    _set_runs(tb.text_frame, lines, anchor=anchor, space_after=space_after)
    return tb


def _rect(slide, l, t, w, h, color):
    sp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(l), Inches(t), Inches(w), Inches(h))
    sp.fill.solid()
    sp.fill.fore_color.rgb = color
    sp.line.fill.background()
    sp.shadow.inherit = False
    return sp


def pie_lineas(slide, l, t, w, lineas, size=PT_PIE, col=CUERPO):
    """Pie de figura o de tabla: mide exactamente lo que mide su texto y devuelve el alto."""
    h = _alto_bloque(lineas, w - 0.06, size, space_after=1.5)
    tb = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tb.text_frame.margin_left = Inches(0.02)
    tb.text_frame.margin_right = Inches(0.02)
    tb.text_frame.margin_top = Inches(0)
    tb.text_frame.margin_bottom = Inches(0)
    _set_runs(tb.text_frame, [(ln, size, False, col) for ln in lineas], space_after=1.5)
    return h


def notes(slide, text):
    """Guion HABLADO en prosa. El texto viene de guion_b9.md, que es la fuente."""
    slide.notes_slide.notes_text_frame.text = text


# ===========================================================================
# Las tres maniobras que python-pptx no tiene (docs/plantilla_oficial.md §7.a)
# ===========================================================================
def clonar_s03(prs, src):
    """Maniobra 1: lámina nueva del layout DEFAULT + deepcopy del XML de las formas.

    De las siete formas de s03 **sólo la imagen tiene relación** (`r:embed` del `a:blip`).
    Como la figura de este deck es NATIVA, la imagen no se clona y no hay ni una rel que
    copiar. El `Text 2` vacío tampoco se clona: está en L=0,41 T=1,41, justo donde va el
    cuerpo."""
    s = prs.slides.add_slide(prs.slide_layouts[0])   # DEFAULT: sin shapes ni placeholders
    for ph in list(s.placeholders):
        ph._element.getparent().remove(ph._element)
    tree = s.shapes._spTree
    for sp in src.shapes:
        if sp.shape_type == MSO_SHAPE_TYPE.PICTURE:
            continue
        if sp.name == "Text 2":
            continue
        tree.append(copy.deepcopy(sp._element))
    return s


def borrar_slide(prs, slide):
    """Saca la lámina del `sldIdLst` y suelta su relación."""
    idx = list(prs.slides).index(slide)
    lst = prs.slides._sldIdLst
    sldId = list(lst)[idx]
    prs.part.drop_rel(sldId.rId)
    lst.remove(sldId)


def reordenar(prs, orden):
    """Maniobra 3: mueve los `sldId` dentro del `sldIdLst`. `orden` = lista de slides."""
    lst = prs.slides._sldIdLst
    actuales = list(prs.slides)
    elems = list(lst)
    porslide = {id(s._element): e for s, e in zip(actuales, elems)}
    for e in elems:
        lst.remove(e)
    for s in orden:
        lst.append(porslide[id(s._element)])


def _quitar_fila(gf, i):
    """Maniobra 2: saca el `<a:tr>` i-ésimo y le resta su alto al graphicFrame."""
    tbl = gf._element.graphic.graphicData.tbl
    trs = tbl.findall(A + "tr")
    tr = trs[i]
    h = int(tr.get("h"))
    tbl.remove(tr)
    gf.height = Emu(gf.height - h)


def _alto_fila(gf, i, alto_in):
    """Fija el alto de una fila y ajusta el del graphicFrame por la diferencia."""
    tbl = gf._element.graphic.graphicData.tbl
    tr = tbl.findall(A + "tr")[i]
    nuevo = int(round(alto_in * 914400))
    gf.height = Emu(gf.height - int(tr.get("h")) + nuevo)
    tr.set("h", str(nuevo))


# ===========================================================================
# Rellenado en sitio
# ===========================================================================
def _shape(slide, nombre):
    for sh in slide.shapes:
        if sh.name == nombre:
            return sh
    raise KeyError("no está la forma %r en la lámina" % nombre)


def _solo_run(par, texto):
    """Deja el párrafo con UN run, conservando el formato del primero.

    El texto del template viene partido en varios runs (el título de s02 llega en tres), así
    que escribir solo `runs[0]` dejaría la cola del original pegada detrás."""
    runs = par.runs
    runs[0].text = texto
    for r in runs[1:]:
        r._r.getparent().remove(r._r)


def set_titulo(slide, texto, nombre="Text 2", size=PT_TITULO):
    sh = _shape(slide, nombre)
    _solo_run(sh.text_frame.paragraphs[0], texto)
    for r in sh.text_frame.paragraphs[0].runs:
        r.font.size = Pt(size)
    ancho = Emu(sh.width).inches
    if text_w(texto, size, True) > ancho:
        raise SystemExit("título que no entra en una línea: %r (%.2f\" en %.2f\")"
                         % (texto, text_w(texto, size, True), ancho))
    return sh


def set_cejilla(slide, tema, nombre=None):
    """`ONCOMETS   ·   <tema>`, conservando los tres colores del molde.

    s02 y s04 traen CUATRO runs (el tema partido en dos) y s03 trae tres: se normaliza a
    tres y se reescriben los colores, que es lo único que hay que preservar."""
    sh = None
    for cand in (nombre, "Google Shape;409;p22", "Text 0"):
        if cand is None:
            continue
        try:
            sh = _shape(slide, cand)
            break
        except KeyError:
            continue
    if sh is None:
        raise KeyError("no está la cejilla")
    p = sh.text_frame.paragraphs[0]
    runs = p.runs
    for r in runs[3:]:
        r._r.getparent().remove(r._r)
    textos = ["ONCOMETS", "   ·   ", tema]
    colores = [CUERPO, SEP, ACENTO]
    for r, txt, col in zip(p.runs, textos, colores):
        r.text = txt
        r.font.color.rgb = col
        r.font.size = Pt(PT_CEJILLA)
        r.font.bold = True
        r.font.name = F
    return sh


def set_cuerpo(slide, puntos, nombre="CuadroTexto 6"):
    """Cuerpo de s03: pares (arranque_bold, resto), `algn="just"` conservado.

    El cuadro usa `spAutoFit` y python-pptx **no lo recalcula**: la altura guardada es la que
    dejó PowerPoint para el texto anterior. Se fija midiendo con los TTF de Barlow. Devuelve
    el borde inferior en pulgadas, para que quien llama apoye la figura debajo."""
    sh = _shape(slide, nombre)
    tf = sh.text_frame
    modelo = copy.deepcopy(tf.paragraphs[0]._p)
    for p in list(tf._txBody.findall(A + "p")):
        tf._txBody.remove(p)
    for bold, resto in puntos:
        nuevo = copy.deepcopy(modelo)
        tf._txBody.append(nuevo)
    for par, (bold, resto) in zip(tf.paragraphs, puntos):
        runs = par.runs
        for r in runs[2:]:
            r._r.getparent().remove(r._r)
        runs[0].text = bold
        runs[1].text = resto
        for r in par.runs:
            r.font.size = Pt(PT_CUERPO)
            r.font.name = F
            r.font.color.rgb = CUERPO

    l, t, w = G_CUERPO
    ancho_txt = w - 0.20                      # lIns/rIns por defecto del cuadro de texto
    alto = 0.05
    for bold, resto in puntos:
        alto += wrap_lines(bold + resto, ancho_txt, PT_CUERPO) * PT_CUERPO * 1.22 / 72.0
    alto += 0.05
    sh.left, sh.top, sh.width = Inches(l), Inches(t), Inches(w)
    sh.height = Inches(alto)
    return t + alto


def _util(cell, ancho_col):
    """Ancho utilizable de una celda: el de la columna menos sus márgenes REALES."""
    return ancho_col - Emu(cell.margin_left).inches - Emu(cell.margin_right).inches


def llenar_tabla(gf, filas, size=PT_CELDA, min_h=0.76):
    """Rellena las filas de cuerpo respetando el estilizado que ya traen las celdas.

    Quita las que sobren restándole el alto al `graphicFrame`, y le da a cada una el alto que
    su texto pide de verdad, medido con Barlow, en vez de confiar en que PowerPoint la crezca
    al abrir el archivo.

    `min_h` existe porque el molde trae CUATRO filas de cuerpo y acá van tres: con el alto
    justo del texto la tabla se encoge, queda pegada al título y deja media lámina vacía. Con
    0,76 conserva la huella del molde (0,745 + 3 x 0,76 = 3,03, su alto original)."""
    tbl = gf.table
    while len(tbl.rows) - 1 > len(filas):
        _quitar_fila(gf, len(tbl.rows) - 1)
    if len(tbl.rows) - 1 < len(filas):
        raise SystemExit("la tabla del molde tiene %d filas de cuerpo y se piden %d"
                         % (len(tbl.rows) - 1, len(filas)))
    anchos = [Emu(c.width).inches for c in tbl.columns]
    for ri, fila in enumerate(filas, start=1):
        nlin = 1
        for ci, txt in enumerate(fila):
            cell = tbl.cell(ri, ci)
            p = cell.text_frame.paragraphs[0]
            cell.text_frame.word_wrap = True
            r = p.add_run()
            r.text = txt
            r.font.size = Pt(size)
            r.font.name = F
            r.font.bold = False
            r.font.color.rgb = TITULO
            nlin = max(nlin, wrap_lines(txt, _util(cell, anchos[ci]), size))
        _alto_fila(gf, ri, max(min_h, nlin * size * 1.22 / 72.0 + 0.14))
    return Emu(gf.top).inches + Emu(gf.height).inches


# ===========================================================================
# Las dos figuras nativas
# ===========================================================================
def barras_marcas(slide, l, t, w, alto_max, datos):
    """Doce barras horizontales, una por lámina, ordenadas por marcas.

    Largo proporcional a las marcas; la parte reencontrada rellena, el resto en el gris de la
    plantilla. La 129741 va en el celeste de acento porque es la que aporta la mitad de los
    aciertos y la lámina lo dice. El `n of m` va a la derecha en **columna fija**: es lo único
    que se lee cuando la barra mide un píxel, y siete láminas tienen de 1 a 3 marcas."""
    w_lab, w_num, gap = 1.30, 1.18, 0.14
    x_bar = l + w_lab + gap
    w_bar = w - w_lab - w_num - 2 * gap
    x_num = l + w - w_num
    maxm = max(d["marcas"] for d in datos)

    # leyenda
    fs_leg = 8.5
    cx = x_bar
    for col, txt in ((CUERPO, "recovered at 30 µm"), (LINEA, "not recovered")):
        _rect(slide, cx, t + 0.045, 0.16, 0.105, col)
        add_textbox(slide, cx + 0.21, t, 1.9, 0.18,
                    [(txt, fs_leg, False, CUERPO)], anchor=MSO_ANCHOR.MIDDLE)
        cx += 0.21 + text_w(txt, fs_leg) + 0.30
    add_textbox(slide, x_num, t, w_num, 0.18,
                [("recovered of marks", fs_leg, True, CUERPO, PP_ALIGN.RIGHT)],
                anchor=MSO_ANCHOR.MIDDLE)

    y0 = t + 0.30
    paso = (alto_max - 0.30) / len(datos)
    h_bar = min(0.17, paso - 0.10)
    fs = 9.5
    for i, d in enumerate(datos):
        y = y0 + i * paso
        yc = y + (paso - h_bar) / 2.0
        destacada = d["slide_id"] == "129741"
        largo = w_bar * d["marcas"] / float(maxm)
        _rect(slide, x_bar, yc, largo, h_bar, LINEA)
        if d["tp"]:
            _rect(slide, x_bar, yc, largo * d["tp"] / float(d["marcas"]), h_bar,
                  ACENTO if destacada else CUERPO)
        add_textbox(slide, l, y, w_lab, paso,
                    [(d["slide_id"], fs, destacada, CUERPO, PP_ALIGN.RIGHT)],
                    anchor=MSO_ANCHOR.MIDDLE)
        add_textbox(slide, x_num, y, w_num, paso,
                    [("%d of %d" % (d["tp"], d["marcas"]), fs, destacada, CUERPO,
                      PP_ALIGN.RIGHT)], anchor=MSO_ANCHOR.MIDDLE)
    return t + alto_max


def tabla_ejes(slide, l, t, w, headers, filas, fracs, fs=9.5, row_h=0.30):
    """Tabla nativa con la paleta de la plantilla: cabecera 1B4F8C con texto blanco y banding
    en E4E9EC. Es `simple_table` de generate_b8_deck.py:660 con la paleta nueva."""
    ncol, nrow = len(headers), len(filas) + 1
    gf = slide.shapes.add_table(nrow, ncol, Inches(l), Inches(t), Inches(w),
                                Inches(row_h * nrow))
    tbl = gf.table
    for ci, fr in enumerate(fracs):
        tbl.columns[ci].width = Inches(w * fr)
    tbl.first_row = False
    tbl.horz_banding = False
    for ri, fila in enumerate([headers] + list(filas)):
        for ci, txt in enumerate(fila):
            cell = tbl.cell(ri, ci)
            cell.margin_left = Inches(0.07)
            cell.margin_right = Inches(0.05)
            cell.margin_top = Inches(0.01)
            cell.margin_bottom = Inches(0.01)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.fill.solid()
            if ri == 0:
                cell.fill.fore_color.rgb = CUERPO
                col, bold = BLANCO, True
            else:
                cell.fill.fore_color.rgb = LINEA if ri % 2 else BLANCO
                col, bold = TITULO, (ci == 0)
            tf = cell.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT
            r = p.add_run()
            r.text = txt
            r.font.size = Pt(fs)
            r.font.bold = bold
            r.font.name = F
            r.font.color.rgb = col
    for ri in range(nrow):
        tbl.rows[ri].height = Inches(row_h)
    gf.height = Inches(row_h * nrow)
    return t + row_h * nrow


# ===========================================================================
# Datos: se LEEN, no se transcriben
# ===========================================================================
def leer_datos():
    with open(CSV_LAMINA) as fh:
        filas = list(csv.DictReader(fh))
    datos = [{"slide_id": r["slide_id"], "marcas": int(r["marcas"]),
              "tp": int(r["tp_30um"]), "det": int(r["detecciones"])} for r in filas]
    datos.sort(key=lambda d: (-d["marcas"], d["slide_id"]))
    with open(CSV_TOL) as fh:
        tol = list(csv.DictReader(fh))
    d = {"n_laminas": len(datos),
         "marcas": sum(x["marcas"] for x in datos),
         "tp": sum(x["tp"] for x in datos),
         "det": sum(x["det"] for x in datos)}
    fila30 = [r for r in tol if float(r["tolerancia_um"]) == 30.0][0]
    d["recall"] = float(fila30["recall"])
    assert int(fila30["tp"]) == d["tp"] and int(fila30["n"]) == d["marcas"], \
        "el agregado y el por-lámina no coinciden"
    # el tramo plano de la escalera, que es lo que la lámina afirma
    plano = [float(r["tolerancia_um"]) for r in tol if int(r["tp"]) == d["tp"]]
    d["plano"] = (min(plano), max(plano))
    ref = [x for x in datos if x["slide_id"] == "129741"][0]
    d["ref_tp"], d["ref_marcas"] = ref["tp"], ref["marcas"]
    d["resto_tp"] = d["tp"] - ref["tp"]
    d["resto_marcas"] = d["marcas"] - ref["marcas"]
    d["resto_recall"] = d["resto_tp"] / float(d["resto_marcas"])
    return datos, d


def leer_guion():
    """Parsea `guion_b9.md` por sus marcadores `## [sNN]`. El .md es la fuente."""
    txt = open(GUION, encoding="utf-8").read()
    bloques, orden = {}, []
    for m in re.finditer(r"^## \[([^\]]+)\][^\n]*\n(.*?)(?=^## \[|\Z)",
                         txt, re.M | re.S):
        clave = m.group(1).strip()
        bloques[clave] = m.group(2).strip()
        orden.append(clave)
    return bloques, orden


# ===========================================================================
# Tipografía y auditoría
# ===========================================================================
def forzar_barlow(prs, fuente=F):
    """Deja Barlow como única tipografía del archivo. Portado de generate_b8_deck.py:1185.

    **No se puede saltear**: el `fontScheme` del theme de esta plantilla también es el de
    Office (Arial) y las láminas heredadas traen Calibri en `endParaRPr`/`buFont`, que
    gobierna lo que se escriba encima."""
    tags = tuple(A + t for t in ("latin", "ea", "cs", "sym", "buFont"))

    def normaliza(root):
        n = 0
        for el in root.iter():
            if el.tag in tags and el.get("typeface") != fuente:
                el.set("typeface", fuente)
                n += 1
        return n

    cola = [prs.part] + [s.part for s in prs.slides]
    cola += [s.notes_slide.part for s in prs.slides if s.has_notes_slide]
    vistos, partes = set(), []
    while cola:
        p = cola.pop()
        if id(p) in vistos:
            continue
        vistos.add(id(p))
        partes.append(p)
        for rel in p.rels.values():
            if not rel.is_external and rel.reltype.endswith(
                    ("slideLayout", "slideMaster", "notesMaster", "theme")):
                cola.append(rel.target_part)
    n = 0
    for p in partes:
        el = getattr(p, "_element", None)
        if el is not None:
            n += normaliza(el)
            continue
        if str(p.partname).startswith("/ppt/theme/"):
            raiz = etree.fromstring(p.blob)
            tocados = 0
            for cual in ("majorFont", "minorFont"):
                for fs in raiz.iter(A + cual):
                    for lat in fs.findall(A + "latin"):
                        if lat.get("typeface") != fuente:
                            lat.set("typeface", fuente)
                            tocados += 1
            if tocados:
                p._blob = etree.tostring(raiz, xml_declaration=True,
                                         encoding="UTF-8", standalone=True)
                n += tocados
    print("  tipografía: %d referencias forzadas a %s" % (n, fuente))


def auditar(prs, saltar_idx=(1,)):
    """Texto que no entra en su caja, formas fuera del lienzo, cuerpos por debajo del mínimo
    del template (7 pt) y objetos que cruzan la zona de pie de s03.

    `saltar_idx` = láminas heredadas que no escribimos (la portada). No reemplaza mirar las
    láminas ([[deck-qa-puntos-ciegos-chequeo]])."""
    problemas = []
    for idx, slide in enumerate(prs.slides, start=1):
        if idx in saltar_idx:
            continue
        pie = None
        for sh in slide.shapes:
            if sh.name == "Google Shape;287;p7":
                pie = Emu(sh.top).inches
        for sh in slide.shapes:
            try:
                l, t = Emu(sh.left).inches, Emu(sh.top).inches
                w, h = Emu(sh.width).inches, Emu(sh.height).inches
            except TypeError:
                continue
            if not getattr(sh, "rotation", 0):
                if l < -0.02 or t < -0.02 or l + w > SW + 0.02 or t + h > SH + 0.02:
                    problemas.append("s%02d  fuera del lienzo: %s (%.2f, %.2f, %.2f x %.2f)"
                                     % (idx, sh.name, l, t, w, h))
            if sh.has_table:
                tbl = sh.table
                anchos = [Emu(c.width).inches for c in tbl.columns]
                acum = 0.0
                for ri, row in enumerate(tbl.rows):
                    hr = Emu(row.height).inches
                    nl = 1
                    for ci, cell in enumerate(row.cells):
                        util = _util(cell, anchos[ci])
                        for p in cell.text_frame.paragraphs:
                            if not p.runs:
                                continue
                            sz = max((r.font.size.pt for r in p.runs if r.font.size),
                                     default=12)
                            bold = any(r.font.bold for r in p.runs)
                            txt = "".join(r.text for r in p.runs)
                            nl = max(nl, wrap_lines(txt, util, sz, bold))
                            # una celda de UNA línea que llega al borde no cuenta como
                            # desborde y aun así se ve pegada al filete: 0,06" de guarda
                            ancho = text_w(txt, sz, bold)
                            if util >= ancho > util - 0.06:
                                problemas.append(
                                    "s%02d  celda al límite de su columna (%.2f de %.2f in): «%s»"
                                    % (idx, ancho, util, txt[:44]))
                            if sz < 7.0:
                                problemas.append("s%02d  celda por debajo del mínimo: %.1f pt"
                                                 % (idx, sz))
                    need = nl * sz * 1.22 / 72.0
                    if need > hr + 0.02:
                        problemas.append("s%02d  fila %d de tabla corta: pide %.2f\", tiene %.2f\""
                                         % (idx, ri, need, hr))
                    acum += max(hr, need)
                if pie is not None and t + acum > pie + 0.02:
                    problemas.append("s%02d  la tabla cruza la zona de pie (%.2f > %.2f)"
                                     % (idx, t + acum, pie))
                continue
            if not sh.has_text_frame:
                if pie is not None and sh.name not in ("Google Shape;287;p7",
                                                       "Google Shape;286;p7") \
                        and t + h > pie + 0.02:
                    problemas.append("s%02d  %s cruza la zona de pie (%.2f > %.2f)"
                                     % (idx, sh.name, t + h, pie))
                continue
            # Los márgenes REALES del cuadro, no un 0,20" supuesto: los cuadros propios
            # usan 0,02" por lado y suponer el default del template daba falso positivo.
            tf = sh.text_frame
            ins = (Emu(tf.margin_left).inches + Emu(tf.margin_right).inches)
            alto, chico = 0.0, None
            for p in tf.paragraphs:
                if not p.runs:
                    continue
                sz = max((r.font.size.pt for r in p.runs if r.font.size), default=12)
                bold = any(r.font.bold for r in p.runs)
                txt = "".join(r.text for r in p.runs)
                if sz >= 6 and (chico is None or sz < chico):
                    chico = sz
                alto += wrap_lines(txt, max(w - ins, 0.2), sz, bold) * sz * 1.22 / 72.0
            if alto > h + 0.06:
                problemas.append("s%02d  texto que no entra: sobra %.2f\" en «%s…»"
                                 % (idx, alto - h, sh.text_frame.text[:44].replace("\n", " ")))
            if chico is not None and chico < 7.0:
                problemas.append("s%02d  cuerpo por debajo del mínimo: %.1f pt" % (idx, chico))
            if pie is not None and t + alto > pie + 0.02:
                problemas.append("s%02d  texto que cruza la zona de pie (%.2f > %.2f)"
                                 % (idx, t + alto, pie))
    if problemas:
        print("  AUDITORÍA: %d avisos" % len(problemas))
        for p in problemas:
            print("   ·", p)
    else:
        print("  AUDITORÍA: sin avisos")
    return problemas


def barrer_rayas(prs, saltar_idx=(1,)):
    """Cero «—» y «–» en lo que escribimos, y nada de «palanca»
    ([[deck-estilo-sin-rayas-ni-palanca]]).

    **Excluye la portada**: su titular trae un «—» y es copy de la empresa, no contenido
    nuestro, así que sin la exclusión el barrido reporta un falso positivo en cada corrida."""
    malos = []
    for idx, slide in enumerate(prs.slides, start=1):
        if idx in saltar_idx:
            continue
        textos = []
        for sh in slide.shapes:
            if sh.has_text_frame:
                textos.append(sh.text_frame.text)
            if sh.has_table:
                for row in sh.table.rows:
                    for c in row.cells:
                        textos.append(c.text)
        if slide.has_notes_slide:
            textos.append(slide.notes_slide.notes_text_frame.text)
        for txt in textos:
            for tok in ("—", "–", "palanca"):
                if tok in txt:
                    malos.append("s%02d  %r en «%s…»" % (idx, tok, txt[:50]))
    if malos:
        print("  ESTILO: %d avisos" % len(malos))
        for m in malos:
            print("   ·", m)
    else:
        print("  ESTILO: sin rayas ni «palanca» (portada excluida)")
    return malos


# ===========================================================================
# Las láminas
# ===========================================================================
def lamina_objetivos(s, guion):
    set_cejilla(s, PROYECTO)
    set_titulo(s, "OBJECTIVES " + PERIODO)
    gf = _shape(s, "Google Shape;196;p29")
    llenar_tabla(gf, [
        ("Scale mitosis detection to 12 annotated WSI",
         "Cross-checked against 94 pathologist marks over 12 slides: 26 recovered at "
         "30 µm, one to one matching, flat from 7.5 to 50 µm",
         "25/08", "Done"),
        ("Evaluate HoVer-NeXt for necrosis",
         "GO with the PanNuke weights, the only ones carrying a dead cell class. Five "
         "slides, 7 to 9 h of GPU. Not launched: the node has been taken",
         "08/09", "Blocked"),
        ("Evaluate new metrics for mitosis",
         "Eight axes scored: what is computable today, what needs GPU, and three that no "
         "amount of compute unlocks",
         "08/09", "In progress"),
    ])
    notes(s, guion)


def lamina_mitosis(s, datos, agg, guion):
    set_cejilla(s, PROYECTO)
    set_titulo(s, "Mitosis: %d of %d pathologist marks" % (agg["tp"], agg["marcas"]),
               nombre="Text 1")
    fin = set_cuerpo(s, [
        ("Twelve annotated slides, %d marks: " % agg["marcas"],
         "%d recovered at 30 µm, one to one, flat from %.1f to %d µm."
         % (agg["tp"], agg["plano"][0], int(agg["plano"][1]))),
        ("One slide carries half the hits: ",
         "129741 alone accounts for %d of the %d. Without it the other eleven give "
         "%d of %d, or %.1f %%." % (agg["ref_tp"], agg["tp"], agg["resto_tp"],
                                    agg["resto_marcas"], 100 * agg["resto_recall"])),
        ("The reference case of the last period was the best of twelve: ",
         "everything built on that slide inherits the bias."),
    ])
    pie = ["The denominator is what the pathologist marked, not the mitoses in the slide. "
           "No precision or F1 against partial positives."]
    l, _, w = G_CUERPO
    h_pie = _alto_bloque(pie, w - 0.06, PT_PIE, space_after=1.5)
    top = fin + 0.16
    alto_fig = T_PIE_S03 - 0.12 - h_pie - 0.10 - top
    barras_marcas(s, l, top, w, alto_fig, datos)
    pie_lineas(s, l, top + alto_fig + 0.10, w, pie)
    notes(s, guion)


def lamina_ejes(s, guion):
    set_cejilla(s, PROYECTO)
    set_titulo(s, "HoVer-NeXt: what is measurable, and what is not", nombre="Text 1")
    fin = set_cuerpo(s, [
        ("Eight axes scored against the pathologist's vocabulary: ",
         "21 classes over 472 annotations, and only Tumour and Mitosis appear in all "
         "twelve slides."),
        ("Three axes are already paid for: ",
         "the seven Lizard classes and the per nucleus polygons are on disk for the "
         "twelve, so nuclear grade and tumour/stroma are CPU, not GPU."),
        ("Three are NO-GO by argument, not by budget: ",
         "the object of those tasks is not a nucleus, so more GPU or more slides does "
         "not unlock them."),
    ])
    l, _, w = G_CUERPO
    # `107 / 12` y no `107 / 8`: el «/8» es el de `Nucleos alto grado` sola. Las tres clases
    # de grado (alto 8, moderado 2, bajo 2) son DISJUNTAS y parten las doce láminas exactas,
    # verificado sobre los doce geojson `- GDT` el 26-ago. O sea que el grado está declarado
    # en TODAS, que es lo que vuelve a este eje el más barato de los tres GO.
    filas = [
        ("Mitosis", "Mitosis, 94 / 12 slides", "done",
         "Measured: 26 of 94 at 30 µm"),
        ("Necrosis", "necrosis + Necrosis + Comedonecrosis, 18 / 5", "7 to 9 h GPU",
         "GO, needs the PanNuke weights"),
        ("Nuclear grade", "107 graded regions / 12", "CPU, on disk",
         "GO, and the cheapest"),
        ("Tumour and stroma", "Tumour 98 / 12, Stroma 12 / 7", "CPU, on disk",
         "GO, the positive control of the method"),
        ("Immune infiltrate", "Immune cells, 7 / 3", "CPU, on disk",
         "Too few to report a number"),
        ("Vascular permeation", "Permeaciones vasculares, 9 / 6", "not applicable",
         "NO-GO: no endothelial or lumen class"),
        ("Microcalcification", "microcalcificaciones, 8 / 3", "not applicable",
         "NO-GO: not a nucleus, and type I is invisible in H&E"),
        ("Architecture", "AreaTubular 25 / 5, Mucinoso 11 / 1", "not applicable",
         "NO-GO: the unit is the gland, not the nucleus"),
    ]
    pie = ["No precision, F1 or PQ against this material, on any axis: the geojson marks "
           "partial positives, not an exhaustive segmentation."]
    h_pie = _alto_bloque(pie, w - 0.06, PT_PIE, space_after=1.5)
    top = fin + 0.16
    disp = T_PIE_S03 - 0.12 - h_pie - 0.10 - top
    row_h = min(0.34, disp / (len(filas) + 1))
    fin_tabla = tabla_ejes(s, l, top, w,
                           ["Axis", "Pathologist annotation", "Cost", "Verdict"],
                           filas, [2.60 / 12.10, 3.90 / 12.10, 1.70 / 12.10, 3.90 / 12.10],
                           row_h=row_h)
    pie_lineas(s, l, fin_tabla + 0.10, w, pie)
    notes(s, guion)


def lamina_tareas(s, guion):
    set_cejilla(s, PROYECTO)
    set_titulo(s, "Tasks for the next period")
    gf = _shape(s, "Google Shape;196;p29")
    llenar_tabla(gf, [
        ("Run the necrosis axis",
         "Density of dead cell detections inside against outside the pathologist's "
         "polygons, null by translation of the mask. Needs the vocabulary unified first",
         "08/09"),
        ("Two CPU axes already on disk",
         "Do nuclear descriptors order the three grades over 107 regions, and does the "
         "epithelium against stroma fraction hold as a positive control",
         "08/09"),
        ("Mitotic hotspot",
         "Count per mm², density map, and the fixed area window that maximises it: "
         "the first version of a zone proposed to the pathologist",
         "15/09"),
    ])
    notes(s, guion)


# ===========================================================================
def main():
    datos, agg = leer_datos()
    guion, _ = leer_guion()
    print("Deck del período · %s · %s" % (PROYECTO, PERIODO))
    print("  datos: %d láminas, %d marcas, %d detecciones, %d TP (%.1f %%)"
          % (agg["n_laminas"], agg["marcas"], agg["det"], agg["tp"], 100 * agg["recall"]))

    prs = Presentation(TPL)
    s01, s02, s03, s04 = list(prs.slides)

    sA = clonar_s03(prs, s03)
    sB = clonar_s03(prs, s03)

    lamina_objetivos(s02, guion["s02"])
    lamina_mitosis(sA, datos, agg, guion["s03a"])
    lamina_ejes(sB, guion["s03b"])
    lamina_tareas(s04, guion["s04"])
    notes(s01, guion["s01"])

    borrar_slide(prs, s03)                      # trae el ejemplo de otra persona
    reordenar(prs, [s01, s02, sA, sB, s04])

    forzar_barlow(prs)
    problemas = auditar(prs)
    problemas += barrer_rayas(prs)

    prs.save(OUT)
    print("  escrito: %s" % os.path.basename(OUT))
    return 1 if problemas else 0


if __name__ == "__main__":
    sys.exit(main())
