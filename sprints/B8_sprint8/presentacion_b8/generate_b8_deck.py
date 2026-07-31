#!/usr/bin/env python
"""generate_b8_deck.py — deck del sprint B8: SI-MIL (Kapse et al., CVPR 2024).

Contenido pedido por Ernesto: las ECUACIONES, la FIGURA ORIGINAL del diagrama del modelo
(Fig. 2, pág. 4 del paper) y el formato de deck del proyecto.

Insumo pedagógico (no se rehace acá, se presenta): `simil_explicacion_matematica.md`.
Números de las tablas y los costos: `simil_estudio.md`.

Alcance: las ecuaciones 1 y 2 van DESARMADAS (que es lo que Ernesto marcó como lo que no
cerraba); las 3 a 10 van en panorama, una línea cada una, con la 9 destacada. Explicarlas
una por una queda pendiente.

Recorte del 31-jul (pedido de Ernesto): de 19 a 14 láminas. Se retiró el EJEMPLO NUMÉRICO
del orden de las operaciones, que ahora entra entero en una sola lámina, y se fusionaron
cuatro pares: divisoria + qué propone, orden + qué queda, atención sin signo + mapeo a
CLAM, resultados + contraste, y costos + preguntas. Lo que salió de las láminas está en el
guion, no borrado.

Reglas que gobiernan el archivo:
  - Se construye SOBRE el template válido (Deep-LLM-V), nunca con Presentation() a secas:
    el template EMBEBE sus fuentes y ese es el motivo real de que un deck "no parezca el
    template" ([[deck-template-fuentes-embebidas]]).
  - TODO nativo salvo la figura del paper, única excepción de la convención de decks.
  - Gramática de diagrama de Deep-LLM-V ([[deck-gramatica-diagrama-deep-llm-v]]).
  - Tipografía: TODO Barlow, forzado con forzar_barlow() sobre theme + master + layouts.
  - Sin rayas «—»/«–», sin la palabra «palanca», sin la expresión «al revés».

Uso:
  PYTHONPATH=/media/administrador/Storage1/sdonoso/clam_testing2/.pylibs \
  /home/sdonoso/miniconda3/envs/clam_latest/bin/python \
    sprints/B8_sprint8/presentacion_b8/generate_b8_deck.py
"""
import os

from lxml import etree
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from PIL import Image

REPO = "/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto"
PRES = os.path.join(REPO, "papers/presentations")
ASSETS_BRAND = os.path.join(PRES, "assets_branding")
OUT_DIR = os.path.join(REPO, "sprints/B8_sprint8/presentacion_b8")
ASSETS = os.path.join(OUT_DIR, "assets")
DST = os.path.join(OUT_DIR, "CLAM_Sprint8_SIMIL.pptx")

TEMPLATE = os.path.join(REPO, "sprints/B7_sprint7/Modelo OncoMets Spatial V1 Deep-LLM-V.pptx")
TPL_KEEP = (0, 1)          # portada de marca + lámina de título, nativas a 13.333
FECHA_REUNION = "30/07/2026"

# --- figura del paper (única imagen del deck), recortada de la página 4 a 400 DPI ---
FIG2_FULL = os.path.join(ASSETS, "simil_fig2_full.png")   # los tres paneles
FIG2_A = os.path.join(ASSETS, "simil_fig2_a.png")         # (a) SI-MIL overview
FIG2_B = os.path.join(ASSETS, "simil_fig2_b.png")         # (b) Conventional MIL branch
FIG2_C = os.path.join(ASSETS, "simil_fig2_c.png")         # (c) Self-Interpretable branch

# ---- paleta Deep-LLM-V (medida sobre el template) ----
ONCO_DARK = RGBColor(0x3E, 0x68, 0x77)    # bloque de proceso
ONCO_CONN = RGBColor(0x38, 0x62, 0x71)    # conector / borde
ONCO_PANEL = RGBColor(0xCD, 0xDF, 0xE1)   # panel contenedor / operador
ONCO_DATA = RGBColor(0xB7, 0xB7, 0xB7)    # bloque de dato
ONCO_INK = RGBColor(0x0E, 0x28, 0x41)     # borde / fondo oscuro

TEAL_TITLE = ONCO_DARK
TEAL_SQ = ONCO_CONN
TEAL_DIV = ONCO_CONN
LAV_TITLE = RGBColor(0xFF, 0xFF, 0xFF)
TEAL_SUB = ONCO_PANEL
TEAL_CARD = ONCO_PANEL
TEAL_CARD2 = RGBColor(0xE9, 0xF1, 0xF2)   # tinte del claro, para banding
GRIS_BODY = RGBColor(0x59, 0x59, 0x59)
GRIS_TXT = RGBColor(0x55, 0x55, 0x55)
INK = RGBColor(0x22, 0x22, 0x22)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
BLACK = RGBColor(0x00, 0x00, 0x00)
PROG_BG = ONCO_DATA

# Los dos caminos de datos de SI-MIL vienen rotulados por COLOR en la figura original
# (naranja = features profundas, verde = PathExpert). El deck no puede inventar dos
# colores nuevos, pero tampoco puede pintar los dos caminos igual: se distinguen por
# peso de tono dentro de la familia del template, y la figura del paper queda como la
# referencia de color cuando se la proyecta.
VIA_PROF = ONCO_DARK          # camino profundo (naranja en la figura)
VIA_INTERP = ONCO_PANEL       # camino interpretable (verde en la figura)

F_TITLE = "Barlow"
F_BODY = "Barlow"
F_MONO = "Barlow"
# Barlow no trae griegas, ℝ, ∈, → ni ⊗: esos glifos caen al fallback del sistema.
# Se rasterizó la alternativa (declarar Cambria Math, que el template también embebe) y
# se ve PEOR: sus griegas son serif finas y contrastan con el Barlow que las rodea,
# mientras que el fallback sans casa bien. Se deja todo declarado Barlow, que además es
# lo que pidió Sebastián. Mismo criterio que el B7 tomó para «→».

# --- geometría de trabajo (se escala x1.3333 al final) ---
SW, SH = 10.0, 5.625
LOGO = os.path.join(ASSETS_BRAND, "logo_header.png")
CHECK_VERDE = os.path.join(ASSETS_BRAND, "check_verde.png")

# --- cabecera OncoMets (láminas técnicas del template) ---
ONCO_LOGO = os.path.join(REPO, "sprints/B7_sprint7/presentacion_b7/assets/logo_oncomets.png")
ONCO_TITLE = RGBColor(0x3E, 0x68, 0x77)
ONCO_LINE = RGBColor(0x3D, 0x68, 0x76)
ONCO_LOGO_L, ONCO_LOGO_T, ONCO_LOGO_W, ONCO_LOGO_H = 0.5625, 0.3278, 1.1033, 0.6630
ONCO_TIT_L, ONCO_TIT_W = 2.0558, 6.8799
ONCO_TIT_BASE = 0.9908
ONCO_TIT_T, ONCO_TIT_H = 0.2950, ONCO_TIT_BASE - 0.2950
ONCO_TIT_SZ = 18.75
ONCO_LINE_T, ONCO_LINE_H = 1.0658, 0.1050
ONCO_BAND = ONCO_LINE_T + ONCO_LINE_H     # 1.1708

# Área de contenido: se maqueta ya en su sitio definitivo para que reflow_onco() no tenga
# que comprimir nada (reancla el bloque a CONTENT_TOP_NEW y escala si se pasa del pie).
TOP = 1.24
BOT = 5.46

_uid = [2000]


# ============================================================================
# Helpers base
# ============================================================================
def _blank(prs):
    for lay in prs.slide_layouts:
        if (lay.name or "").lower().strip() == "blank":
            return lay
    return prs.slide_layouts[6]


def base_from_template():
    """Abre el template válido y le borra las láminas salvo TPL_KEEP.

    Conserva ppt/fonts/*.fntdata + <p:embeddedFontLst> (Barlow, Cambria Math), el theme y
    el master. Borrar una slide no tiene API en python-pptx: hay que sacarla del sldIdLst
    Y soltar la relación, si no queda huérfana en el paquete."""
    prs = Presentation(TEMPLATE)
    keep_ids = {id(prs.slides[i]._element) for i in TPL_KEEP}
    lst = prs.slides._sldIdLst
    for i, sld in enumerate(list(lst)):
        if i in TPL_KEEP:
            continue
        prs.part.drop_rel(sld.get(
            "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"))
        lst.remove(sld)
    return prs, keep_ids


def new_slide(prs):
    """Lámina en blanco SIN los placeholders del layout (el BLANK del template arrastra
    DATE/FOOTER/SLIDE_NUMBER y aparecen como cuadros vacíos)."""
    s = prs.slides.add_slide(_blank(prs))
    for ph in list(s.placeholders):
        ph._element.getparent().remove(ph._element)
    return s


def _add_runs(p, text, size, bold, color, font=F_BODY):
    """Mini-markup de sub/superíndices REALES (baseline OOXML, no caracteres Unicode):
    `_x` / `_(xx)` = subíndice ; `^x` / `^(xx)` = superíndice.

    Hace falta porque Unicode no tiene subíndice para casi ninguna letra (no hay ᵢ de
    molde para `w`, `j`, `ij`…), y este deck es de ecuaciones. Portado de
    generate_clam_mammoth_pptx.py con Barlow en vez de Carlito. Para un `_`/`^` literal,
    escaparlo con backslash en el string fuente."""
    def emit(s, base=None):
        if not s:
            return
        r = p.add_run(); r.text = s
        r.font.name = font; r.font.bold = bold; r.font.color.rgb = color
        r.font.size = Pt(size * 0.74 if base is not None else size)
        if base is not None:
            r._r.get_or_add_rPr().set("baseline", str(base))
    i, n, buf = 0, len(text), ""
    while i < n:
        c = text[i]
        if c == "\\" and i + 1 < n and text[i + 1] in "_^\\":
            buf += text[i + 1]; i += 2; continue
        if c in "_^" and i + 1 < n:
            base = -25000 if c == "_" else 30000
            nxt = text[i + 1]
            if nxt == "(":
                j = text.find(")", i + 2)
                if j != -1:
                    emit(buf); buf = ""
                    emit(text[i + 2:j], base)
                    i = j + 1; continue
                buf += c; i += 1; continue
            emit(buf); buf = ""
            emit(nxt, base)
            i += 2; continue
        buf += c; i += 1
    emit(buf)


def _set_runs(tf, lines, anchor=MSO_ANCHOR.TOP, markup=False):
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    for i, ln in enumerate(lines):
        txt, sz, bold, col = ln[0], ln[1], ln[2], ln[3]
        font = ln[4] if len(ln) > 4 else F_BODY
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = ln[5] if len(ln) > 5 else PP_ALIGN.LEFT
        p.space_after = Pt(4)
        if markup:
            _add_runs(p, txt, sz, bold, col, font)
        else:
            r = p.add_run(); r.text = txt
            r.font.size = Pt(sz); r.font.bold = bold
            r.font.name = font; r.font.color.rgb = col


def add_textbox(slide, l, t, w, h, lines, anchor=MSO_ANCHOR.TOP, markup=False):
    tb = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    _set_runs(tb.text_frame, lines, anchor=anchor, markup=markup)
    return tb


def notes(slide, text):
    """Guion HABLADO en prosa (sin etiquetas de fase, sin nº de job ni nombres)."""
    slide.notes_slide.notes_text_frame.text = text


def _rect(slide, l, t, w, h, color, line=None):
    sp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(l), Inches(t), Inches(w), Inches(h))
    sp.fill.solid(); sp.fill.fore_color.rgb = color
    if line is None:
        sp.line.fill.background()
    else:
        sp.line.color.rgb = line; sp.line.width = Pt(1)
    sp.shadow.inherit = False
    return sp


def header_oncomets(slide, title, size=22):
    """Cabecera técnica del template: logo OncoMets + título Barlow bold + línea teal."""
    pic = slide.shapes.add_picture(ONCO_LOGO, Inches(ONCO_LOGO_L), Inches(ONCO_LOGO_T),
                                   Inches(ONCO_LOGO_W), Inches(ONCO_LOGO_H))
    pic.name = "ONCOHDR_logo"
    if title:
        tb = slide.shapes.add_textbox(Inches(ONCO_TIT_L), Inches(ONCO_TIT_T),
                                      Inches(ONCO_TIT_W), Inches(ONCO_TIT_H))
        tb.name = "ONCOHDR_title"
        _set_runs(tb.text_frame, [(title, min(size, ONCO_TIT_SZ), True, ONCO_TITLE, F_BODY)],
                  anchor=MSO_ANCHOR.BOTTOM)
    _rect(slide, 0.0, ONCO_LINE_T, SW, ONCO_LINE_H, ONCO_LINE).name = "ONCOHDR_line"


def content(prs, title, size=26):
    s = new_slide(prs)
    header_oncomets(s, title, size=size)
    return s


def divider(prs, title, subtitle):
    s = new_slide(prs)
    s.background.fill.solid(); s.background.fill.fore_color.rgb = TEAL_DIV
    s.shapes.add_picture(LOGO, Inches(0.42), Inches(0.36), height=Inches(0.62))
    add_textbox(s, 0.8, 1.85, SW - 1.6, 1.45,
                [(title, 44, True, LAV_TITLE, F_TITLE, PP_ALIGN.CENTER)], anchor=MSO_ANCHOR.MIDDLE)
    add_textbox(s, 0.8, 3.42, SW - 1.6, 0.7,
                [(subtitle, 18, False, TEAL_SUB, F_BODY, PP_ALIGN.CENTER)], anchor=MSO_ANCHOR.TOP)
    return s


def add_image_fit(slide, path, l, t, w, h, align="center"):
    iw, ih = Image.open(path).size
    ar = iw / ih; box_ar = w / h
    if ar > box_ar:
        nw = w; nh = w / ar
    else:
        nh = h; nw = h * ar
    nl = l + (w - nw) / 2
    nt = t + (h - nh) / 2 if align != "top" else t
    slide.shapes.add_picture(path, Inches(nl), Inches(nt), Inches(nw), Inches(nh))


def add_card(slide, l, t, w, h, idx, text, size=14):
    fill = TEAL_CARD if idx % 2 == 0 else TEAL_CARD2
    sp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(l), Inches(t), Inches(w), Inches(h))
    sp.fill.solid(); sp.fill.fore_color.rgb = fill
    sp.line.color.rgb = TEAL_SQ; sp.line.width = Pt(1.25); sp.shadow.inherit = False
    cd = 0.44
    circ = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(l + 0.16), Inches(t + (h - cd) / 2),
                                  Inches(cd), Inches(cd))
    circ.fill.solid(); circ.fill.fore_color.rgb = ONCO_DARK
    circ.line.fill.background(); circ.shadow.inherit = False
    _set_runs(circ.text_frame, [(str(idx), 15, True, WHITE, F_TITLE, PP_ALIGN.CENTER)],
              anchor=MSO_ANCHOR.MIDDLE)
    tb = slide.shapes.add_textbox(Inches(l + 0.74), Inches(t), Inches(w - 0.88), Inches(h))
    _set_runs(tb.text_frame, [(text, size, True, INK, F_BODY)], anchor=MSO_ANCHOR.MIDDLE)


def caption(slide, l, t, w, text, size=11, col=GRIS_TXT, align=PP_ALIGN.CENTER, bold=False):
    add_textbox(slide, l, t, w, 0.4, [(text, size, bold, col, F_BODY, align)])


def status_done(slide, cx, cy, size=0.42):
    slide.shapes.add_picture(CHECK_VERDE, Inches(cx - size / 2), Inches(cy - size / 2),
                             Inches(size), Inches(size))


def status_progress(slide, cx, cy, w=1.5, h=0.44, texto="Pendiente"):
    sp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(cx - w / 2), Inches(cy - h / 2),
                                Inches(w), Inches(h))
    sp.fill.solid(); sp.fill.fore_color.rgb = PROG_BG
    sp.line.color.rgb = ONCO_CONN; sp.line.width = Pt(1.25); sp.shadow.inherit = False
    _set_runs(sp.text_frame, [(texto, 11, True, BLACK, F_BODY, PP_ALIGN.CENTER)],
              anchor=MSO_ANCHOR.MIDDLE)


def takeaway_bar(slide, text, t=4.85, col=TEAL_TITLE, size=14):
    _rect(slide, 0.35, t, SW - 0.7, 0.02, TEAL_SQ)
    add_textbox(slide, 0.35, t + 0.08, SW - 0.7, 0.62,
                [(text, size, True, col, F_BODY, PP_ALIGN.CENTER)], anchor=MSO_ANCHOR.MIDDLE)


# ============================================================================
# Gramática de diagrama de Deep-LLM-V
# ============================================================================
def _proc(slide, l, t, w, h, text, dim=None, size=11, col=None):
    """Bloque de proceso: rounded-rect #3E6877 con Barlow bold BLANCO."""
    sp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(l), Inches(t),
                                Inches(w), Inches(h))
    sp.fill.solid(); sp.fill.fore_color.rgb = col or ONCO_DARK
    sp.line.fill.background(); sp.shadow.inherit = False
    lines = [(text, size, True, WHITE, F_BODY, PP_ALIGN.CENTER)]
    if dim:
        lines.append((dim, size - 2, False, WHITE, F_BODY, PP_ALIGN.CENTER))
    _set_runs(sp.text_frame, lines, anchor=MSO_ANCHOR.MIDDLE, markup=True)
    for p in sp.text_frame.paragraphs:
        p.space_after = Pt(0)
    return sp


def _proc_claro(slide, l, t, w, h, text, size=11, dim=None):
    """Bloque de proceso en el tono CLARO (#CDDFE1 con texto teal): el detalle interno."""
    sp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(l), Inches(t),
                                Inches(w), Inches(h))
    sp.fill.solid(); sp.fill.fore_color.rgb = ONCO_PANEL
    sp.line.fill.background(); sp.shadow.inherit = False
    lines = [(text, size, True, ONCO_DARK, F_BODY, PP_ALIGN.CENTER)]
    if dim:
        lines.append((dim, size - 2, False, ONCO_DARK, F_BODY, PP_ALIGN.CENTER))
    _set_runs(sp.text_frame, lines, anchor=MSO_ANCHOR.MIDDLE, markup=True)
    for p in sp.text_frame.paragraphs:
        p.space_after = Pt(0)
    return sp


def _dato(slide, l, t, w, h, text, size=9.5):
    """Bloque de dato (forma del tensor): rect #B7B7B7 con Barlow NEGRO."""
    sp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(l), Inches(t), Inches(w), Inches(h))
    sp.fill.solid(); sp.fill.fore_color.rgb = ONCO_DATA
    sp.line.fill.background(); sp.shadow.inherit = False
    _set_runs(sp.text_frame, [(text, size, False, BLACK, F_BODY, PP_ALIGN.CENTER)],
              anchor=MSO_ANCHOR.MIDDLE, markup=True)
    return sp


def _grupo(slide, l, t, w, h, fill=None):
    """Panel contenedor que agrupa una región."""
    sp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(l), Inches(t),
                                Inches(w), Inches(h))
    sp.fill.solid(); sp.fill.fore_color.rgb = fill or ONCO_PANEL
    sp.line.color.rgb = fill or ONCO_PANEL; sp.line.width = Pt(0.6)
    sp.shadow.inherit = False
    return sp


def _conn(slide, x0, y0, x1, y1, arrow=True):
    """Conector recto #386271 de 2.37 pt, con punta opcional."""
    ln = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x0), Inches(y0),
                                    Inches(x1), Inches(y1))
    ln.line.color.rgb = ONCO_CONN; ln.line.width = Pt(2.37)
    ln.shadow.inherit = False
    if arrow:
        lnpr = ln.line._get_or_add_ln()
        lnpr.append(lnpr.makeelement(qn('a:tailEnd'),
                                     {'type': 'triangle', 'w': 'med', 'len': 'med'}))
    return ln


def _conn_dash(slide, x0, y0, x1, y1):
    """Línea de expansión punteada: ata un bloque con su detalle ampliado."""
    ln = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x0), Inches(y0),
                                    Inches(x1), Inches(y1))
    ln.line.color.rgb = ONCO_CONN; ln.line.width = Pt(1.0)
    ln.shadow.inherit = False
    lnpr = ln.line._get_or_add_ln()
    lnpr.append(lnpr.makeelement(qn('a:prstDash'), {'val': 'dash'}))
    return ln


def _dim(slide, l, t, w, text, size=9.5, align=PP_ALIGN.CENTER, col=None):
    """Etiqueta de forma del tensor suelta, pegada al bloque."""
    add_textbox(slide, l, t, w, 0.26,
                [(text, size, False, col or ONCO_INK, F_BODY, align)],
                anchor=MSO_ANCHOR.MIDDLE, markup=True)


def _oper(slide, cx, cy, sym="+", d=0.34):
    """Operador: óvalo #CDDFE1 con borde #0E2841."""
    sp = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(cx - d / 2), Inches(cy - d / 2),
                                Inches(d), Inches(d))
    sp.fill.solid(); sp.fill.fore_color.rgb = ONCO_PANEL
    sp.line.color.rgb = ONCO_INK; sp.line.width = Pt(1.0); sp.shadow.inherit = False
    _set_runs(sp.text_frame, [(sym, 11, True, ONCO_INK, F_BODY, PP_ALIGN.CENTER)],
              anchor=MSO_ANCHOR.MIDDLE)
    return sp


def _rot_label(slide, l, t, w, h, text, size=9, col=None):
    """Rótulo vertical al costado de un panel."""
    tb = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    _set_runs(tb.text_frame, [(text, size, True, col or ONCO_DARK, F_BODY, PP_ALIGN.CENTER)],
              anchor=MSO_ANCHOR.MIDDLE)
    tb.rotation = 270
    return tb


def eq(slide, l, t, w, texto, num=None, size=15, h=0.52, fill=None, col=None):
    """Ecuación en su propio panel claro, con el número del paper a la derecha.

    Las ecuaciones son el objeto de este deck, así que se tratan como los bloques de
    arquitectura del template: caja propia, cuerpo grande, nada compitiendo al lado. El
    número va afuera del panel, chico, como lo pone el paper."""
    _grupo(slide, l, t, w, h, fill=fill or TEAL_CARD2)
    add_textbox(slide, l + 0.16, t, w - (0.62 if num else 0.32), h,
                [(texto, size, False, col or ONCO_INK, F_BODY, PP_ALIGN.CENTER)],
                anchor=MSO_ANCHOR.MIDDLE, markup=True)
    if num:
        add_textbox(slide, l + w - 0.58, t, 0.44, h,
                    [(num, 11, False, GRIS_BODY, F_BODY, PP_ALIGN.RIGHT)],
                    anchor=MSO_ANCHOR.MIDDLE)


def simple_table(slide, l, t, w, headers, rows, col_fracs, row_h=0.32, fs=9.5,
                 destacar=None, markup=False):
    """Tabla nativa: header teal + banding claro. `destacar` = índice de fila (0-based
    sobre `rows`) que se pinta con el celeste sólido, para la fila que importa."""
    ncol = len(headers); nrow = len(rows) + 1
    tbl = slide.shapes.add_table(nrow, ncol, Inches(l), Inches(t), Inches(w),
                                 Inches(row_h * nrow)).table
    for ci, fr in enumerate(col_fracs):
        tbl.columns[ci].width = Inches(w * fr)
    tbl.first_row = False; tbl.horz_banding = False
    for ri, row in enumerate([headers] + list(rows)):
        for ci, txt in enumerate(row):
            cell = tbl.cell(ri, ci)
            cell.margin_left = Inches(0.06); cell.margin_right = Inches(0.04)
            cell.margin_top = Inches(0.015); cell.margin_bottom = Inches(0.015)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            if ri == 0:
                cell.fill.solid(); cell.fill.fore_color.rgb = TEAL_SQ
                col, bold = WHITE, True
            elif destacar is not None and ri - 1 == destacar:
                cell.fill.solid(); cell.fill.fore_color.rgb = TEAL_CARD
                col, bold = ONCO_DARK, True
            else:
                cell.fill.solid(); cell.fill.fore_color.rgb = TEAL_CARD2 if ri % 2 else TEAL_CARD
                col, bold = INK, (ci == 0)
            tf = cell.text_frame; tf.word_wrap = True
            p = tf.paragraphs[0]; p.alignment = PP_ALIGN.LEFT
            if markup:
                _add_runs(p, txt, fs, bold, col, F_BODY)
            else:
                r = p.add_run(); r.text = txt
                r.font.size = Pt(fs); r.font.bold = bold
                r.font.name = F_BODY; r.font.color.rgb = col
    return tbl


# ---------------------------------------------------------------------------
# Medición de texto real
# ---------------------------------------------------------------------------
# El chequeo programático de conformidad da «todo limpio» con texto que desborda su caja
# ([[deck-qa-puntos-ciegos-chequeo]]), porque nadie mide el texto. Acá se mide de verdad,
# con los mismos TTF de Barlow que están instalados bajo containment, y los paneles se
# dimensionan solos. Es el equivalente al auto-dimensionado de `render_table`.
BARLOW_DIR = "/media/administrador/Storage1/sdonoso/clam_testing2/fonts/barlow"
_FCACHE = {}
_MEDIDA = 40          # se mide a 40 px y se divide: da precisión sin depender del hinting


def _face(bold):
    from PIL import ImageFont
    key = bool(bold)
    if key not in _FCACHE:
        nombre = "Barlow-Bold.ttf" if bold else "Barlow-Regular.ttf"
        _FCACHE[key] = ImageFont.truetype(os.path.join(BARLOW_DIR, nombre), _MEDIDA)
    return _FCACHE[key]


def text_w(txt, size, bold=False):
    """Ancho del texto en PULGADAS del espacio de trabajo (lámina de 10 in, 72 pt/in).

    Las griegas y los símbolos que Barlow no tiene caen al fallback y miden distinto; se
    aproximan con el ancho de una «n», que es del orden correcto y sobreestima poco."""
    f = _face(bold)
    limpio = "".join(c if f.getbbox(c) else "n" for c in txt)
    return f.getlength(limpio) / _MEDIDA * size / 72.0


def wrap_lines(txt, ancho, size, bold=False):
    """Cuántas líneas ocupa `txt` dentro de `ancho` pulgadas (wrap por palabra)."""
    if not txt.strip():
        return 1
    n, actual = 1, ""
    for palabra in txt.split(" "):
        cand = (actual + " " + palabra).strip()
        if actual and text_w(cand, size, bold) > ancho:
            n += 1; actual = palabra
        else:
            actual = cand
    return n


def _alto_bloque(lineas, ancho, size, bold=False, space_after=3):
    """Alto en pulgadas de un bloque de párrafos ya envueltos."""
    total = 0.0
    for ln in lineas:
        total += wrap_lines(ln, ancho, size, bold) * size * 1.22 / 72.0 + space_after / 72.0
    return total


def panel(slide, l, t, w, h, title, tcol, lines, border, fill=TEAL_CARD2, tsize=14.5,
          bsize=12, markup=False):
    """Panel con título + líneas de cuerpo.

    `h=None` calcula el alto midiendo el texto, que es lo que evita que la última línea
    quede fuera de la caja. Con `h` explícito, el valor se respeta salvo que el texto no
    entre: en ese caso gana el texto, porque una caja corta y un renglón afuera se ve
    peor que una caja un poco más alta."""
    ancho_txt = w - 0.36
    necesario = (0.12 + _alto_bloque([title], ancho_txt, tsize, True)
                 + _alto_bloque(lines, ancho_txt, bsize) + 0.16)
    h = necesario if h is None else max(h, necesario)
    sp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(l), Inches(t), Inches(w), Inches(h))
    sp.fill.solid(); sp.fill.fore_color.rgb = fill
    sp.line.color.rgb = border; sp.line.width = Pt(1.5); sp.shadow.inherit = False
    tb = slide.shapes.add_textbox(Inches(l + 0.18), Inches(t + 0.08), Inches(ancho_txt), Inches(h - 0.12))
    runs = [(title, tsize, True, tcol, F_TITLE)] + [(ln, bsize, False, INK, F_BODY) for ln in lines]
    _set_runs(tb.text_frame, runs, markup=markup)
    for p in tb.text_frame.paragraphs:
        p.space_after = Pt(3)
    return sp


# ============================================================================
# Reflow, tipografía y re-base al tamaño del template
# ============================================================================
CONTENT_TOP_OLD = 0.86
CONTENT_TOP_NEW = ONCO_BAND + 0.05        # 1.221
SAFE_BOTTOM = SH - 0.14


def _scale_block(el, f):
    """Escala un shape completo por f: geometría, cuerpo tipográfico y métrica de tabla.
    El alto real de una tabla lo manda el texto de sus filas, no el alto del shape, así que
    hay que bajar también el `sz` y el alto de fila para que encoja de verdad."""
    for off in el.iter(qn("a:off")):
        off.set("x", str(int(round(int(off.get("x")) * f))))
        off.set("y", str(int(round(int(off.get("y")) * f))))
    for ext in el.iter(qn("a:ext")):
        ext.set("cx", str(int(round(int(ext.get("cx")) * f))))
        ext.set("cy", str(int(round(int(ext.get("cy")) * f))))
    for tag in ("a:rPr", "a:defRPr", "a:endParaRPr"):
        for rpr in el.iter(qn(tag)):
            if rpr.get("sz"):
                rpr.set("sz", str(max(100, int(round(int(rpr.get("sz")) * f)))))
    for gc in el.iter(qn("a:gridCol")):
        if gc.get("w"):
            gc.set("w", str(int(round(int(gc.get("w")) * f))))
    for tr in el.iter(qn("a:tr")):
        if tr.get("h"):
            tr.set("h", str(int(round(int(tr.get("h")) * f))))


def reflow_onco(prs, skip=()):
    """Reancla el contenido de las láminas con cabecera OncoMets bajo la banda teal, y lo
    comprime si no entra. Como acá se maqueta ya desde TOP=1.24, el ajuste típico es nulo:
    la función queda como red de seguridad."""
    for slide in prs.slides:
        if id(slide._element) in skip:
            continue
        cuerpo = [sh for sh in slide.shapes if not (sh.name or "").startswith("ONCOHDR_")]
        if len(cuerpo) == len(list(slide.shapes)):
            continue
        tops = [Emu(sh.top).inches for sh in cuerpo]
        bots = [Emu(sh.top).inches + Emu(sh.height).inches for sh in cuerpo]
        if not tops:
            continue
        top0, bot0 = min(tops), max(bots)
        f = 1.0
        if bot0 + (CONTENT_TOP_NEW - top0) > SAFE_BOTTOM and bot0 > top0:
            f = max(0.80, (SAFE_BOTTOM - CONTENT_TOP_NEW) / (bot0 - top0))
        if f < 1.0:
            for sh in cuerpo:
                _scale_block(sh._element, f)
        desplaz = CONTENT_TOP_NEW - top0 * f
        for sh in cuerpo:
            sh.top = Inches(Emu(sh.top).inches + desplaz)


def forzar_barlow(prs, fuente=F_BODY):
    """Deja Barlow como única tipografía del archivo (pedido de Sebastián).

    Los runs propios ya salen en Barlow, pero quedan tres focos fuera de alcance directo:
    el `endParaRPr`/`buFont` de las láminas heredadas, el fontScheme del theme (que en
    este template es el de Office, o sea Arial) y los `defRPr` del master y los layouts.
    Se normaliza el XML entero."""
    A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
    tags = tuple(A + t for t in ("latin", "ea", "cs", "sym", "buFont"))

    def normaliza(root):
        tocados = 0
        for el in root.iter():
            if el.tag in tags and el.get("typeface") != fuente:
                el.set("typeface", fuente)
                tocados += 1
        return tocados

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


def scale_deck_to_1610(prs, k=13.333 / 10.0, skip=()):
    """Escala el deck entero por k y fija el tamaño de lámina en 13.333 x 7.5. Misma
    relación de aspecto que 10 x 5.625, así que la escala es uniforme y no deforma.
    `skip` = láminas heredadas, que ya están a 13.333."""
    for slide in prs.slides:
        if id(slide._element) in skip:
            continue
        tree = slide.shapes._spTree
        for off in tree.iter(qn("a:off")):
            off.set("x", str(int(round(int(off.get("x")) * k))))
            off.set("y", str(int(round(int(off.get("y")) * k))))
        for ext in tree.iter(qn("a:ext")):
            ext.set("cx", str(int(round(int(ext.get("cx")) * k))))
            ext.set("cy", str(int(round(int(ext.get("cy")) * k))))
        for tag in ("a:rPr", "a:defRPr", "a:endParaRPr"):
            for rpr in tree.iter(qn(tag)):
                if rpr.get("sz"):
                    rpr.set("sz", str(max(100, int(round(int(rpr.get("sz")) * k)))))
        for gc in tree.iter(qn("a:gridCol")):
            if gc.get("w"):
                gc.set("w", str(int(round(int(gc.get("w")) * k))))
        for tr in tree.iter(qn("a:tr")):
            if tr.get("h"):
                tr.set("h", str(int(round(int(tr.get("h")) * k))))
        for ln in tree.iter(qn("a:ln")):
            if ln.get("w"):
                ln.set("w", str(int(round(int(ln.get("w")) * k))))
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)


def auditar(prs, skip=()):
    """Chequeo de defectos que el ojo ve y un chequeo ingenuo no: texto que no entra en su
    caja, shapes fuera del lienzo y cuerpos por debajo del mínimo del template (7 pt).

    Se corre ANTES de escalar, o sea en el espacio de 10 x 5.625. No reemplaza mirar las
    láminas ([[deck-qa-puntos-ciegos-chequeo]]), pero caza la clase de defecto que más
    apareció acá: la última línea de un panel quedando afuera."""
    problemas = []
    for idx, slide in enumerate(prs.slides, start=1):
        if id(slide._element) in skip:
            continue
        for sh in slide.shapes:
            try:
                l, t = Emu(sh.left).inches, Emu(sh.top).inches
                w, h = Emu(sh.width).inches, Emu(sh.height).inches
            except TypeError:
                continue
            # Un shape rotado 270° reporta su bbox SIN rotar: da falso positivo de límites.
            if not getattr(sh, "rotation", 0):
                if l < -0.02 or t < -0.02 or l + w > SW + 0.02 or t + h > SH + 0.02:
                    problemas.append("s%02d  fuera del lienzo: %s (%.2f, %.2f, %.2f x %.2f)"
                                     % (idx, sh.shape_type, l, t, w, h))
            if not sh.has_text_frame:
                continue
            alto, chico = 0.0, None
            for p in sh.text_frame.paragraphs:
                if not p.runs:
                    continue
                sz = max((r.font.size.pt for r in p.runs if r.font.size), default=12)
                bold = any(r.font.bold for r in p.runs)
                txt = "".join(r.text for r in p.runs)
                # los runs de sub/superíndice vienen a 0.74x: no son un cuerpo chico real
                if sz >= 6 and (chico is None or sz < chico):
                    if not any(r._r.get_or_add_rPr().get("baseline") for r in p.runs):
                        chico = sz
                alto += wrap_lines(txt, max(w - 0.14, 0.2), sz, bold) * sz * 1.22 / 72.0
            if alto > h + 0.06:
                problemas.append("s%02d  texto que no entra: sobra %.2f\" en «%s…»"
                                 % (idx, alto - h, sh.text_frame.text[:44].replace("\n", " ")))
            if chico is not None and chico < 7.0:
                problemas.append("s%02d  cuerpo por debajo del mínimo: %.1f pt" % (idx, chico))
    if problemas:
        print("  AUDITORÍA: %d avisos" % len(problemas))
        for p in problemas:
            print("   ·", p)
    else:
        print("  AUDITORÍA: sin avisos")
    return problemas


def _set_solo_run(par, texto):
    """Deja el párrafo con un solo run, conservando el formato del primero. El texto del
    template viene partido en varios runs, así que escribir solo runs[0] dejaría la cola
    del original pegada detrás."""
    runs = par.runs
    runs[0].text = texto
    for r in runs[1:]:
        r._r.getparent().remove(r._r)


def retitular_portada(prs):
    """Ajusta las dos láminas de apertura heredadas del template sin redibujarlas."""
    portada = prs.slides[0]
    for sh in portada.shapes:
        if not sh.has_text_frame:
            continue
        txt = sh.text_frame.text.strip()
        if txt.startswith("Care in people"):
            # Marcador sin reemplazar que viene del propio template.
            for par in list(sh.text_frame.paragraphs)[1:]:
                par._p.getparent().remove(par._p)
        elif txt.startswith("OncoMETS is an AI-powered platform"):
            # El párrafo arranca tan abajo que se sale por el borde inferior.
            sh.top = Inches(5.62)
            sh.left = Inches(0.28)
            sh.width = Inches(6.30)
    titulo = prs.slides[1]
    for sh in titulo.shapes:
        if not sh.has_text_frame:
            continue
        txt = sh.text_frame.text.strip()
        if txt == "OncoMets - Spatial":
            _set_solo_run(sh.text_frame.paragraphs[0], "OncoMets · SI-MIL")
        elif txt == "14/11/2025":
            _set_solo_run(sh.text_frame.paragraphs[0], FECHA_REUNION)
    return titulo


# ============================================================================
# Build
# ============================================================================
def build():
    prs, keep_ids = base_from_template()
    prs.slide_width = Inches(SW); prs.slide_height = Inches(SH)

    # ---- 1. Apertura (heredada del template) ----
    s = retitular_portada(prs)
    notes(s, "Esta presentación es la revisión de uno de los papers que quedaron encargados, "
             "SI-MIL, publicado en CVPR el año pasado. Lo que propone es un modelo que se explica "
             "solo, y para eso invierte el reparto de trabajo habitual: la red profunda deja de ser "
             "la que predice y pasa a ser la que enseña dónde mirar, mientras la predicción la hace "
             "un modelo lineal sobre mediciones de núcleos que tienen nombre de patología. El "
             "recorrido tiene dos partes. Primero la mecánica, sobre la figura original y las "
             "ecuaciones del paper, con las dos primeras desarmadas con calma porque son la base de "
             "cualquier modelo de este tipo, incluido el nuestro. Después, dónde queda parado "
             "nuestro trabajo frente a esto y qué costaría llevarlo a nuestros datos.")

    # ---- 2. Objetivos de la revisión ----
    s = content(prs, "Objetivos de la revisión", size=32)
    objetivos = [
        ("1. Situar qué propone SI-MIL y de dónde viene.", "done"),
        ("2. Recorrer la arquitectura sobre la figura original del paper.", "done"),
        ("3. Desarmar las ecuaciones 1 y 2, que son la base de todo MIL.", "done"),
        ("4. Precisar qué puede y qué no puede decir un mapa de atención.", "done"),
        ("5. Explicar las ecuaciones 3 a 10 con el mismo detalle.", "prog"),
        ("6. Situar el método frente a lo nuestro, con sus costos reales.", "done"),
    ]
    row_tops = [TOP + 0.06 + i * 0.68 for i in range(6)]
    row_h = 0.62
    for (it, st), rt in zip(objetivos, row_tops):
        add_textbox(s, 0.35, rt, 7.75, row_h, [(it, 19, True, GRIS_BODY, F_BODY)],
                    anchor=MSO_ANCHOR.MIDDLE)
        cy = rt + row_h / 2
        if st == "done":
            status_done(s, 8.98, cy)
        else:
            status_progress(s, 8.98, cy)
    notes(s, "Antes de entrar, fijemos qué me propuse con esta lectura.\n"
             "\n"
             "1. Lo primero es situar el método: qué propone y de qué línea de trabajo viene.\n"
             "\n"
             "2. Lo segundo es recorrer la arquitectura, y para eso voy a usar la figura original "
             "del paper en vez de redibujarla, porque está muy bien armada y conviene que la "
             "veamos tal cual.\n"
             "\n"
             "3. Lo tercero es desarmar las dos primeras ecuaciones. Son las que el paper escribe "
             "como repaso de lo que ya existía, así que describen también a nuestro modelo, y "
             "resultan más interesantes de lo que parecen a primera vista.\n"
             "\n"
             "4. De ahí sale el cuarto punto, que es el que más nos toca: precisar qué puede y qué "
             "no puede decir un mapa de atención, porque es exactamente la herramienta con la que "
             "venimos mirando nuestros modelos.\n"
             "\n"
             "5. El quinto queda pendiente y lo digo de entrada: las ecuaciones de la tres a la "
             "diez las voy a mostrar y a comentar en bloque, pero desarmadas con el mismo detalle "
             "todavía no están.\n"
             "\n"
             "6. Y el sexto es situar todo esto frente a lo que venimos haciendo nosotros, con los "
             "costos reales que tendría llevarlo a nuestros datos.")

    # ---- 3. Qué propone, en una frase ----
    # La divisoria de sección se retiró al recortar el deck: lo único que aportaba era la
    # ficha del paper, y esa cabe como línea de referencia sobre esta misma lámina.
    s = content(prs, "SI-MIL: qué propone, en una frase")
    caption(s, 0.36, TOP, 9.28,
            "Taming Deep MIL for Self-Interpretability in Gigapixel Histopathology · "
            "Kapse et al., CVPR 2024", size=11, col=GRIS_BODY, bold=True)
    add_textbox(s, 0.36, TOP + 0.32, 9.28, 0.52, [
        ("Que el modelo prediga con una combinación lineal de mediciones de núcleos que "
         "tienen nombre de patología, y que la red profunda quede como el maestro que le "
         "enseña dónde mirar.", 15, True, TEAL_TITLE, F_BODY, PP_ALIGN.CENTER)],
        anchor=MSO_ANCHOR.MIDDLE)
    tarjetas = [
        "La red profunda no predice: selecciona los 20 parches que valen la pena.",
        "La predicción sale de 246 mediciones con nombre, sobre esos 20 parches.",
        "En inferencia la rama profunda se descarta entera.",
    ]
    for i, txt in enumerate(tarjetas):
        add_card(s, 0.36, TOP + 1.04 + i * 0.76, 9.28, 0.64, i + 1, txt, size=13)
    # La ficha del paper como bloques de dato: es metadato, no argumento.
    fichas = [("CVPR 2024", "Kapse et al."), ("246", "features con nombre"),
              ("20", "parches por lámina"), ("625 K", "parámetros en total")]
    fw, fgap = 2.20, 0.16
    fx = (SW - (4 * fw + 3 * fgap)) / 2
    for i, (val, sub) in enumerate(fichas):
        x = fx + i * (fw + fgap)
        _grupo(s, x, TOP + 3.34, fw, 0.68, fill=TEAL_CARD2)
        add_textbox(s, x, TOP + 3.38, fw, 0.34,
                    [(val, 17, True, TEAL_TITLE, F_TITLE, PP_ALIGN.CENTER)])
        add_textbox(s, x, TOP + 3.70, fw, 0.28,
                    [(sub, 10, False, GRIS_BODY, F_BODY, PP_ALIGN.CENTER)])
    notes(s, "Empecemos por el método. El nombre completo habla de domesticar un modelo profundo "
             "para que se explique solo, y eso resume bien la ambición: no acompañar la predicción "
             "con una explicación, sino conseguir que la explicación sea la predicción.\n"
             "\n"
             "La idea cabe en una frase, y está arriba. Que el modelo prediga con una "
             "combinación lineal de mediciones de núcleos que tienen nombre de patología, y que la "
             "red profunda quede como el maestro que le enseña dónde mirar.\n"
             "\n"
             "Las tres líneas de abajo son las consecuencias de esa frase. La primera es que la red "
             "profunda deja de predecir: su único producto es una selección, veinte parches de toda "
             "la lámina. La segunda es que la predicción se calcula sobre mediciones que un patólogo "
             "puede leer. Son doscientas cuarenta y seis, cosas como la asimetría de la solidez de "
             "los núcleos neoplásicos o la mezcla de tipos celulares en una región. Y la "
             "tercera es la más audaz de las tres: cuando el modelo se pone a funcionar, la rama "
             "profunda se descarta entera, no viaja con el modelo.\n"
             "\n"
             "La fila de números da la escala. Es un trabajo del año pasado, y el modelo que "
             "sale a producción tiene seiscientos veinticinco mil parámetros, que es del mismo "
             "orden que el modelo profundo con el que lo comparan. La mejora no viene de tamaño.")

    # ---- 4. La figura oficial (única imagen del deck) ----
    s = content(prs, "La arquitectura, en la figura del paper")
    add_image_fit(s, FIG2_FULL, 0.22, TOP + 0.02, 9.56, 3.10, align="top")
    # Rótulos de panel bajo la figura, alineados a los tercios que ocupa cada uno.
    rot = [(0.22, 5.40, "(a) el recorrido completo, de la lámina a las dos predicciones"),
           (5.66, 4.12, "(b) y (c) el detalle de cada rama")]
    for x, w, txt in rot:
        caption(s, x, TOP + 3.20, w, txt, size=10.5, col=TEAL_TITLE, bold=True)
    takeaway_bar(s, "Dos caminos que salen de la misma lámina: uno mide, el otro selecciona.",
                 t=TOP + 3.62, size=13)
    notes(s, "La figura completa conviene verla antes que las fórmulas, porque todo lo que sigue "
             "está acá.\n"
             "\n"
             "Arriba a la izquierda está la lámina cuadriculada en parches. De ahí salen dos "
             "caminos paralelos, y lo importante es que describen exactamente los mismos parches, "
             "en el mismo orden, de dos maneras distintas. El de arriba pasa por un extractor "
             "profundo y produce, por cada parche, un vector de números que eligió una red para sí "
             "misma; nosotros usaríamos CONCH acá. El de abajo parte de los mapas de núcleos, ya "
             "segmentados, y produce mediciones de morfología, de grafo de células y de "
             "heterogeneidad espacial, todas con nombre legible.\n"
             "\n"
             "En el medio está la caja amarilla, que es la bisagra de todo el diseño: toma la "
             "atención que calculó el camino profundo y con ella elige un puñado de parches, pero "
             "esa selección se aplica sobre el otro camino, el de las mediciones con nombre. Y "
             "fíjense en el recuadro punteado de arriba a la derecha, que dice descartado en "
             "inferencia: ese es el clasificador del camino profundo, y no llega a producción.\n"
             "\n"
             "Los dos paneles de la derecha son ampliaciones de esas dos ramas, y los vamos a ir "
             "viendo de a uno.")

    # ---- 5. Las dos entradas ----
    s = content(prs, "Dos descripciones del mismo parche")
    BW, BH = 2.36, 0.74
    y1, y2 = TOP + 0.30, TOP + 1.34
    _proc(s, 0.36, (y1 + y2) / 2 - 0.10, 1.72, BH, "Un parche", size=12)
    # camino profundo (arriba)
    _proc(s, 2.58, y1, BW, BH, "Extractor profundo", dim="CONCH en nuestro caso", size=11.5)
    _dato(s, 5.36, y1 + 0.10, 1.52, 0.54, "g_i ∈ ℝ^D", size=12)
    _dim(s, 7.06, y1 + 0.12, 2.60, "D = 512 · números que eligió una red",
         size=10, align=PP_ALIGN.LEFT)
    # camino interpretable (abajo)
    _proc_claro(s, 2.58, y2, BW, BH, "PathExpert", size=11.5, dim="sobre el mapa de núcleos")
    _dato(s, 5.36, y2 + 0.10, 1.52, 0.54, "f_i ∈ ℝ^d", size=12)
    _dim(s, 7.06, y2 + 0.06, 2.60, "d = 246 · mediciones con nombre",
         size=10, align=PP_ALIGN.LEFT)
    # Los dos papers encargados no son dos ángulos: HoVer-Net es el front-end de este
    # camino. Conviene que se vea en la lámina y no solo en el guion.
    _dim(s, 7.06, y2 + 0.34, 2.60, "el mapa lo produce HoVer-Net",
         size=9.5, align=PP_ALIGN.LEFT, col=GRIS_BODY)
    _conn(s, 2.08, (y1 + y2) / 2 + 0.27, 2.58, y1 + BH / 2)
    _conn(s, 2.08, (y1 + y2) / 2 + 0.27, 2.58, y2 + BH / 2)
    _conn(s, 2.58 + BW, y1 + BH / 2, 5.36, y1 + BH / 2)
    _conn(s, 2.58 + BW, y2 + BH / 2, 5.36, y2 + BH / 2)
    simple_table(s, 0.36, TOP + 2.34, 9.28,
                 ["", "Ancho del vector", "Quién eligió los números", "¿Se puede leer?"],
                 [["Camino profundo", "D = 512", "una red, para su propio objetivo", "no"],
                  ["Camino PathExpert", "d = 246", "la literatura de patología", "sí, cada columna tiene nombre"]],
                 col_fracs=[0.22, 0.16, 0.36, 0.26], row_h=0.36, fs=11)
    takeaway_bar(s, "Misma cantidad de filas, mismos parches, mismo orden. Lo único que "
                    "cambia es el ancho.", t=TOP + 3.58, size=13)
    notes(s, "Antes de la primera ecuación hay que dejar fijada una convención de notación que el "
             "paper usa sin remarcarla, y que si se pasa por alto vuelve confuso todo lo demás.\n"
             "\n"
             "El paper trabaja con dos anchos distintos y los escribe con la misma letra, una en "
             "mayúscula y otra en minúscula. La mayúscula es el ancho del camino profundo, el "
             "vector que produce el extractor de features; en nuestro pipeline son quinientos doce "
             "números por parche. La minúscula es el ancho del otro camino, doscientos cuarenta y "
             "seis mediciones de núcleos. Son dos espacios completamente distintos.\n"
             "\n"
             "Lo que hay que retener es lo de abajo de todo. Los dos caminos tienen la misma "
             "cantidad de filas, son los mismos parches y en el mismo orden. Lo único que cambia "
             "es el ancho y, sobre todo, quién eligió esos números: en un caso una red, para un "
             "objetivo que no es el nuestro; en el otro, la literatura de patología, de antemano y "
             "con un nombre pegado a cada columna. Esa diferencia es la que sostiene todo el "
             "trabajo.\n"
             "\n"
             "Una aclaración que ordena los dos papers que quedaron encargados. El mapa "
             "de núcleos del que salen esas mediciones lo produce HoVer-Net, que es el otro. O sea "
             "que no son dos ángulos distintos: son la misma cadena, y HoVer-Net es la primera "
             "mitad.")

    # ---- 6. Ecuación 1 ----
    s = content(prs, "Ecuación 1: proyectar y repartir la atención")
    eq(s, 0.36, TOP, 9.28, "g̃_i = H(g_i)          α_i = A^p(g̃_i)          i ∈ {1, 2, … N}",
       num="(1)", size=16, h=0.60)
    add_image_fit(s, FIG2_B, 0.30, TOP + 0.74, 5.30, 1.95, align="top")
    caption(s, 0.30, TOP + 2.66, 5.30, "panel (b) de la figura del paper", size=9.5)
    bloques = [
        ("La bolsa", ["Los N parches son un conjunto SIN orden: si se permutan, "
                      "la predicción tiene que salir igual."], False),
        ("H, el proyector", ["Una traducción aprendida. En CLAM es una línea: "
                             "nn.Linear(512, 512) + ReLU + Dropout."], False),
        ("A^p, la atención por parche", ["Reparte un presupuesto del 100 % entre los N "
                                         "parches. La softmax corre sobre N, así que los "
                                         "α_i suman 1."], True),
    ]
    yy = TOP + 0.74
    for tit, cuerpo, mk in bloques:
        sp = panel(s, 5.82, yy, 3.86, None, tit, TEAL_TITLE, cuerpo, TEAL_SQ,
                   tsize=13, bsize=10.5, markup=mk)
        yy += Emu(sp.height).inches + 0.14
    takeaway_bar(s, "La atención de un parche depende de los demás parches: no es una "
                    "propiedad suya, es su tajada.", t=TOP + 3.86, size=12.5)
    notes(s, "La primera ecuación tiene dos pasos y describe algo que ya conocemos, porque es "
             "también lo que hace nuestro modelo.\n"
             "\n"
             "El primer paso es el proyector. Cada parche llega como un vector que escribió el "
             "extractor de features para su propio objetivo, que no es nuestra tarea, y el "
             "proyector lo reescribe midiéndolo contra unas varas que se aprenden durante el "
             "entrenamiento. En nuestro modelo eso es literalmente una capa lineal seguida de una "
             "activación, y es exactamente la capa que veníamos estudiando la vez pasada.\n"
             "\n"
             "El segundo paso es la atención. Hay un presupuesto de importancia del cien por "
             "ciento para repartir entre todos los parches de la lámina: el módulo le pone un "
             "puntaje crudo a cada uno y después los convierte en porcentajes que suman uno. El "
             "superíndice de la letra indica que es la atención sobre parches, porque más adelante "
             "va a aparecer una hermana que trabaja sobre el otro eje.\n"
             "\n"
             "Queda un detalle, y es la línea de abajo. Como el "
             "reparto suma uno sobre todos los parches, la atención de un parche depende de cuántos "
             "y cuáles sean los demás. No es una propiedad del parche, es su tajada del "
             "presupuesto. El mismo tejido en una lámina chica y en una grande recibe atención "
             "distinta.")

    # ---- 7. Ecuación 2: el orden, en UNA lámina ----
    # El ejemplo numérico que acompañaba a esta ecuación se retiró al recortar el deck
    # (pedido de Ernesto). El argumento son dos cosas, el orden de las operaciones y qué
    # queda en memoria después del forward, y ninguna de las dos necesita que la cuenta
    # esté hecha en la lámina: la tabla de abajo la reemplaza entera.
    s = content(prs, "Ecuación 2: el orden de dos operaciones")
    eq(s, 0.36, TOP, 9.28, "Ŷ_g = ψ( Σ_i C( α_i · g̃_i ) )", num="(2)", size=17, h=0.50)
    ya, yb = TOP + 0.60, TOP + 1.28
    _rot_label(s, -0.30, ya + 0.13, 1.40, 0.32, "ORDEN A", col=GRIS_BODY)
    _rot_label(s, -0.30, yb + 0.13, 1.40, 0.32, "ORDEN B", col=ONCO_DARK)
    axs = [0.52, 2.66, 4.80, 6.94]
    pasos_a = [("Pesar cada parche", "α_i · g̃_i"), ("Sumar", "una sola ficha"),
               ("Clasificar", "C( · )"), ("Un logit", "y nada más")]
    for x, (t1, t2) in zip(axs, pasos_a):
        _proc_claro(s, x, ya, 1.86, 0.58, t1, size=11.5, dim=t2)
    for i in range(3):
        _conn(s, axs[i] + 1.86, ya + 0.29, axs[i + 1], ya + 0.29)
    _dim(s, 8.92, ya + 0.16, 1.00, "= CLAM", size=11, align=PP_ALIGN.LEFT, col=GRIS_BODY)
    pasos_b = [("Pesar cada parche", "α_i · g̃_i"), ("Clasificar cada uno", "C( · ) N veces"),
               ("Sumar los puntajes", "N sumandos"), ("El mismo logit", "y el desglose")]
    for x, (t1, t2) in zip(axs, pasos_b):
        _proc(s, x, yb, 1.86, 0.58, t1, size=11.5, dim=t2)
    for i in range(3):
        _conn(s, axs[i] + 1.86, yb + 0.29, axs[i + 1], yb + 0.29)
    _dim(s, 8.92, yb + 0.16, 1.10, "= ecuación 2", size=11, align=PP_ALIGN.LEFT, col=ONCO_DARK)
    simple_table(s, 0.36, TOP + 1.98, 9.28,
                 ["Después del forward queda", "Orden A", "Orden B"],
                 [["la ficha fundida", "sí, un vector de 512", "no existe"],
                  ["el logit final", "un número", "el mismo número"],
                  ["desglose por parche", "no existe", "N números CON SIGNO"]],
                 col_fracs=[0.30, 0.34, 0.36], row_h=0.36, fs=11, destacar=2)
    takeaway_bar(s, "Toda la diferencia está en dónde cierra el paréntesis de C: el número "
                    "es el mismo, lo que queda en la mano no.", t=TOP + 3.46, size=12.5)
    notes(s, "Esta es la ecuación que cuesta, y cuesta porque parece decir algo obvio. Uno la lee "
             "y entiende multiplicá por la atención, sumá y clasificá. En realidad está diciendo "
             "algo muy específico sobre el orden de dos operaciones.\n"
             "\n"
             "El camino de arriba es el que usa nuestro modelo. Se pesa cada parche por su "
             "atención, se suman todos y queda una única ficha promedio; a esa ficha se le aplica "
             "el clasificador y sale un número. Pensémoslo como una licuadora: se echan las frutas "
             "en su proporción, se licúa, queda un solo jugo, se prueba y se dictamina.\n"
             "\n"
             "El camino de abajo es el de la ecuación. Se pesa cada parche igual que antes, pero "
             "el clasificador se aplica a cada parche por separado, tantas veces como parches "
             "haya, y recién después se suma. Siguiendo la analogía: se prueba cada fruta ya "
             "medida en su proporción, se anota su puntaje en una libreta y se suma la columna.\n"
             "\n"
             "Escrita, la diferencia es solamente dónde cierra el paréntesis del clasificador. Y "
             "acá viene lo que importa, que es la tabla de abajo: el logit final es el mismo "
             "número por los dos caminos. Lo que cambia es qué queda en memoria cuando el modelo "
             "termina de calcular. Arriba queda una ficha fundida y ningún desglose; abajo no hay "
             "ficha fundida, pero quedan tantos puntajes como parches, con signo, que suman exacto "
             "el resultado. Una vez licuado el jugo no hay manera de separarlo en frutas; uno se "
             "acuerda de las proporciones que usó, pero la proporción dice cuánta fruta se puso, "
             "no si esa fruta era dulce o ácida.")

    # ---- 8. Qué implica para nuestro modelo (atención sin signo + mapeo a CLAM) ----
    s = content(prs, "Qué implica para nuestro modelo")
    # El `_` de model_clam.py va escapado: sin la barra, el markup de subíndices se come
    # la «c» y el archivo queda escrito «model_lam.py».
    simple_table(s, 0.36, TOP, 9.28,
                 ["De la ecuación 1 y 2", "En nuestro modelo", "Verificado en"],
                 [["H( · ), el proyector", "nn.Linear(512, 512) + ReLU + Dropout",
                   "model\\_clam.py:191"],
                  ["A^p( · ), la atención", "atención con compuerta, softmax sobre N",
                   "model\\_clam.py:193 y 213"],
                  ["C( · ), el predictor", "nn.Linear(512, 1), uno por clase",
                   "model\\_clam.py:198"],
                  ["el orden", "ORDEN A: funde y después clasifica",
                   "model\\_clam.py:239 y 243"]],
                 col_fracs=[0.26, 0.46, 0.28], row_h=0.36, fs=10.5, destacar=3, markup=True)
    panel(s, 0.36, TOP + 1.90, 4.54, None, "La atención no dice hacia dónde", TEAL_TITLE,
          ["Sale de una softmax: todos sus valores son positivos, y un número positivo "
           "expresa cuánto, nunca hacia dónde.",
           "El parche más atendido puede ser el que más empuja EN CONTRA de la clase, y el "
           "mapa lo pinta rojo intenso igual."],
          TEAL_SQ, tsize=12.5, bsize=10)
    panel(s, 5.10, TOP + 1.90, 4.54, None, "Qué acota de nuestros mapas", ONCO_DARK,
          ["Los de CLAM contra Mammoth son de ATENCIÓN: dicen dónde mira cada modelo, no "
           "hacia qué clase empujó lo que miró.",
           "Al presentarlos: «acá el modelo puso su atención», no «acá el modelo encontró "
           "el tumor»."],
          ONCO_DARK, fill=TEAL_CARD, tsize=12.5, bsize=10)
    takeaway_bar(s, "Nuestro predictor también es lineal, así que el desglose por parche se "
                    "PODRÍA calcular después. En SI-MIL ese desglose ES el modelo.",
                 t=TOP + 3.42, size=12.5)
    notes(s, "Aterricemos las dos ecuaciones en nuestro propio código, porque el paper las "
             "escribe como repaso de lo que ya existía y eso incluye a nuestro modelo.\n"
             "\n"
             "La tabla de arriba es el mapeo, verificado línea por línea. El proyector es nuestra "
             "primera capa lineal con su activación, la atención es nuestro módulo con compuerta "
             "normalizando sobre los parches, y el predictor son nuestras capas de salida, una "
             "por clase. El orden, que es la fila destacada, es el primero de los dos: nuestro "
             "modelo funde y después clasifica. Con dos diferencias, porque el paper escribe una "
             "versión más limpia que la nuestra: nuestra atención es por clase, y tenemos ramas "
             "de instancia que en esta formulación no existen.\n"
             "\n"
             "Uno podría pensar que la atención rescata lo que el orden A pierde, y no. Sale de "
             "una softmax, así que todos sus valores son positivos, y un número positivo expresa "
             "cuánto, nunca hacia dónde. El caso que le preocupa al paper es un parche que se "
             "lleva más de la mitad de la atención y que al mismo tiempo es el que más empuja en "
             "contra de la clase: el mapa de calor le pinta un rojo intenso, y quien lo mira lee "
             "que ahí estaba la evidencia, cuando el modelo lo usó como evidencia de lo "
             "contrario.\n"
             "\n"
             "Esto nos toca directamente. Los mapas que presentamos la vez pasada son de "
             "atención: comparamos dónde mira cada modelo, y para esa pregunta la herramienta es "
             "la correcta. No invalida nada de lo que mostramos, pero marca el límite exacto.\n"
             "\n"
             "Queda algo que sí podríamos hacer. Como nuestro predictor también es lineal, el "
             "resultado se podría desarmar por parche a posteriori. La diferencia es que en el "
             "paper ese desglose es la definición del modelo, no algo que uno deriva cuando ya "
             "terminó, y esa distinción entre interpretable por construcción y explicado después "
             "es la tesis entera del trabajo.")

    # ---- 9. El puente: PAG Top-K ----
    s = content(prs, "El puente: los índices salen de un camino, la selección se aplica al otro")
    add_textbox(s, 0.36, TOP, 9.28, 0.40, [
        ("Sobre una lámina nuestra de 10 000 parches", 12, True, GRIS_BODY, F_BODY,
         PP_ALIGN.CENTER)], anchor=MSO_ANCHOR.MIDDLE)
    # Embudo con la cuenta hecha. El camino profundo entrega su único producto por un
    # codo que baja hasta la selección; el camino PathExpert corre por debajo y es el que
    # atraviesa la lámina de punta a punta, que es exactamente lo que dice el método.
    y = TOP + 0.50
    y2 = y + 1.12
    _proc(s, 0.36, y, 3.30, 0.72, "Camino profundo", dim="10 000 × 512 = 5 120 000 números",
          size=12)
    _dim(s, 6.30, y + 0.16, 3.34, "se descarta entero", size=11, align=PP_ALIGN.LEFT,
         col=GRIS_BODY)
    _proc_claro(s, 0.36, y2, 3.30, 0.72, "Camino PathExpert", size=12,
                dim="10 000 × 246 = 2 460 000 números")
    _oper(s, 4.28, y2 + 0.36, sym="K", d=0.46)
    _proc(s, 5.16, y2, 2.60, 0.72, "20 × 246 = 4920", dim="esto es lo que predice", size=13)
    # codo del camino profundo hacia la selección
    _conn(s, 3.66, y + 0.36, 4.28, y + 0.36, arrow=False)
    _conn(s, 4.28, y + 0.36, 4.28, y2 + 0.10)
    _dim(s, 4.46, y + 0.74, 3.20, "su ÚNICO producto: 20 índices", size=10,
         align=PP_ALIGN.LEFT, col=ONCO_DARK)
    # el camino PathExpert atraviesa la selección
    _conn(s, 3.66, y2 + 0.36, 4.03, y2 + 0.36)
    _conn(s, 4.53, y2 + 0.36, 5.16, y2 + 0.36)
    _dim(s, 3.44, y2 + 0.78, 1.70, "se queda con 20 filas", size=10, col=GRIS_BODY)
    add_textbox(s, 0.36, TOP + 2.60, 9.28, 0.44, [
        ("De cinco millones de números ilegibles a 4920 que tienen nombre.",
         15, True, TEAL_TITLE, F_BODY, PP_ALIGN.CENTER)], anchor=MSO_ANCHOR.MIDDLE)
    panel(s, 0.36, TOP + 3.14, 4.54, None, "La rama profunda no aporta ni un número",
          TEAL_TITLE,
          ["Aporta 20 enteros: cuáles parches valen la pena. Es la ecuación 3, donde lo "
           "que sale son ÍNDICES."], TEAL_SQ, tsize=13, bsize=10.5)
    panel(s, 5.10, TOP + 3.14, 4.54, None, "Por qué hace falta una versión especial",
          ONCO_DARK,
          ["Elegir los K mayores no tiene gradiente: es una selección, escalonada. Usan "
           "una variante perturbada para que el gradiente pueda bajar por ahí y las dos "
           "ramas se co-aprendan."],
          ONCO_DARK, fill=TEAL_CARD, tsize=13, bsize=10.5)
    notes(s, "Este es el movimiento central del diseño, y es el que hace que las dos ramas dejen "
             "de ser dos modelos corriendo en paralelo.\n"
             "\n"
             "Tomemos una lámina nuestra de diez mil parches, que es un tamaño realista. Por el "
             "camino profundo eso son más de cinco millones de números, y todos se descartan: ni "
             "uno solo llega a la predicción final. Lo único que ese camino aporta son veinte "
             "enteros, veinte índices que dicen cuáles parches valen la pena mirar. Por el camino "
             "de las mediciones con nombre hay dos millones y medio de números, de los que se "
             "conservan las veinte filas que la otra rama señaló. Quedan cuatro mil novecientos "
             "veinte números, y sobre esos se predice.\n"
             "\n"
             "Ese embudo es la figura entera: de cinco millones de números que nadie puede leer a "
             "menos de cinco mil que tienen nombre.\n"
             "\n"
             "Esto no es tan directo como suena. Quedarse "
             "con los veinte mayores es una operación de selección, escalonada, y una operación "
             "así no tiene derivada, así que el entrenamiento no puede atravesarla. Por eso "
             "usan una versión perturbada de esa selección, que sí deja pasar el gradiente. Si no, "
             "las dos ramas nunca aprenderían la una de la otra.")

    # ---- 10. La rama interpretable ----
    s = content(prs, "La otra rama: de pesar parches a pesar mediciones")
    add_image_fit(s, FIG2_C, 0.30, TOP, 5.30, 1.85, align="top")
    caption(s, 0.30, TOP + 1.90, 5.30, "panel (c) de la figura del paper", size=9.5)
    panel(s, 0.30, TOP + 2.26, 5.30, None, "Por qué la matriz se gira", TEAL_TITLE,
          ["La maquinaria de atención sabe hacer una sola cosa: recibir una matriz y "
           "devolver un puntaje POR FILA.",
           "Si se quiere un puntaje por medición, no hay que inventar nada: se gira para "
           "que las mediciones sean las filas."],
          TEAL_SQ, tsize=13, bsize=10.5)
    # La tabla mide 4 filas de 0.46: hay que reservarle el alto real antes de poner el
    # panel debajo, si no se montan (pasó en la primera pasada).
    T_ROW, T_N = 0.46, 4
    simple_table(s, 5.82, TOP, 3.86,
                 ["", "α", "β"],
                 [["¿cuántos hay?", "N, uno por parche (miles)", "246, uno por medición"],
                  ["¿qué contestan?", "qué región importa", "qué medición importa"],
                  ["¿suman 1?", "sí, softmax sobre N", "no, sigmoide una por una"]],
                 col_fracs=[0.28, 0.36, 0.36], row_h=T_ROW, fs=10, destacar=2)
    panel(s, 5.82, TOP + T_ROW * T_N + 0.18, 3.86, None,
          "Por qué esa última fila no es un detalle", ONCO_DARK,
          ["α reparte un presupuesto fijo: subir uno baja los demás.",
           "β termina en una sigmoide, que no reparte nada: son 246 compuertas "
           "independientes, no una torta.",
           "Por eso el paper puede después empujarlas casi todas a cero y forzar que el "
           "reporte tenga pocos renglones."],
          ONCO_DARK, fill=TEAL_CARD, tsize=13, bsize=10, markup=True)
    notes(s, "La otra rama tiene la misma forma que la primera: una pila de datos, un módulo de "
             "atención, unos puntajes y una multiplicación. Lo único que agrega son esas dos "
             "vueltitas que se ven en el panel, al principio y al final, que son transposiciones.\n"
             "\n"
             "El motivo es simple y está a la izquierda. La maquinaria de atención sabe hacer una "
             "sola cosa: recibe una matriz y devuelve un puntaje por cada fila. En la rama "
             "anterior las filas eran parches, así que devolvió un puntaje por parche. Acá "
             "queremos un puntaje por medición, así que no hay que inventar ningún módulo nuevo: "
             "se gira la matriz para que las mediciones pasen a ser las filas, se pasa la misma "
             "maquinaria, y al final se gira de vuelta.\n"
             "\n"
             "Los dos conjuntos de pesos están comparados a la derecha, y quiero detenerme en la "
             "última fila, que es la que suele confundirse. Los pesos de parche reparten un "
             "presupuesto fijo: si uno sube, los otros bajan. Los pesos de medición no: cada uno "
             "sale de su propia sigmoide, un número entre cero y uno calculado por separado. Son "
             "doscientas cuarenta y seis compuertas independientes, no una torta repartida.\n"
             "\n"
             "Eso no es un tecnicismo: es lo que le permite al paper empujar después casi todas "
             "esas compuertas a cero, para que el reporte que ve el patólogo tenga pocos renglones "
             "en vez de doscientos cuarenta y seis. Con un reparto de suma fija esa dispersión "
             "vendría impuesta de fábrica y no se podría regular.")

    # ---- 11. Las ecuaciones 3 a 10 ----
    s = content(prs, "Las ecuaciones 3 a 10, en panorama")
    filas = [("S_K = TopK(α, K)", "(3)", "elegir los K parches más atendidos: salen ÍNDICES"),
             ("β_j = G(PF(M^T))", "(4)", "un peso por cada medición, sobre la matriz girada"),
             ("β_j = (β_j − Pr_γ(β)) / std(β)", "(5a)", "centrar en un percentil γ y estandarizar"),
             ("β_j = 1 / (1 + e^(−β_j × t))", "(5b)", "sigmoide con temperatura: fuerza la dispersión"),
             ("M′_(ij) = β_j × M_(ij)", "(6)", "atenuar o realzar cada columna de mediciones"),
             ("M″_i = Σ_j w_j M′_(ij) + b", "(7)", "el predictor lineal, parche por parche"),
             ("Ŷ_f = ψ( Σ_i M″_i )", "(8)", "sumar los K puntajes y activar")]
    yy = TOP + 0.02
    for txt, num, gloss in filas:
        _grupo(s, 0.36, yy, 9.28, 0.42, fill=TEAL_CARD2)
        add_textbox(s, 0.50, yy, 3.30, 0.42, [(txt, 12, False, ONCO_INK, F_BODY)],
                    anchor=MSO_ANCHOR.MIDDLE, markup=True)
        add_textbox(s, 3.86, yy, 0.50, 0.42, [(num, 9.5, False, GRIS_BODY, F_BODY)],
                    anchor=MSO_ANCHOR.MIDDLE)
        add_textbox(s, 4.42, yy, 5.10, 0.42, [(gloss, 10.5, False, INK, F_BODY)],
                    anchor=MSO_ANCHOR.MIDDLE)
        yy += 0.46
    # la 9, destacada: es la que hay que llevarse
    _grupo(s, 0.36, yy + 0.06, 9.28, 0.62, fill=TEAL_CARD)
    add_textbox(s, 0.50, yy + 0.06, 4.60, 0.62, [
        ("Ŷ_f = ψ( Σ_i Σ_j w_j β_j M_(ij) + b )", 14.5, True, ONCO_DARK, F_BODY)],
        anchor=MSO_ANCHOR.MIDDLE, markup=True)
    add_textbox(s, 5.20, yy + 0.06, 4.30, 0.62, [
        ("(9)  cada sumando es la contribución del parche i por su medición j.",
         11, True, ONCO_DARK, F_BODY)], anchor=MSO_ANCHOR.MIDDLE)
    _grupo(s, 0.36, yy + 0.74, 9.28, 0.42, fill=TEAL_CARD2)
    add_textbox(s, 0.50, yy + 0.74, 3.30, 0.42, [
        ("L = L_CE(Y, Ŷ_g) + L_CE(Y, Ŷ_f) + λ L_KD(Ŷ_g, Ŷ_f)", 11, False, ONCO_INK, F_BODY)],
        anchor=MSO_ANCHOR.MIDDLE, markup=True)
    add_textbox(s, 3.86, yy + 0.74, 0.50, 0.42, [("(10)", 9.5, False, GRIS_BODY, F_BODY)],
                anchor=MSO_ANCHOR.MIDDLE)
    add_textbox(s, 4.42, yy + 0.74, 5.10, 0.42, [
        ("las dos ramas se entrenan juntas: la interpretable persigue a la profunda",
         10.5, False, INK, F_BODY)], anchor=MSO_ANCHOR.MIDDLE)
    takeaway_bar(s, "Si hay que quedarse con una sola ecuación, es la 9: ES el reporte que "
                    "ve el patólogo.", t=yy + 1.22, size=12.5)
    notes(s, "El resto de las ecuaciones las paso en bloque, porque desarmadas con el mismo "
             "detalle que las dos primeras todavía no las tengo, y prefiero decirlo antes que "
             "improvisar.\n"
             "\n"
             "La tres es la selección de la que hablábamos recién. La cuatro calcula un peso por "
             "cada medición, sobre la matriz girada. La cinco tiene dos partes y es la que fuerza "
             "que pocas mediciones sobrevivan: primero centra los pesos en un percentil y los "
             "estandariza, después los pasa por una sigmoide con temperatura, que es lo que empuja "
             "a la mayoría hacia cero. La seis aplica esos pesos, atenuando o realzando cada "
             "columna. La siete y la ocho son el predictor lineal y la suma sobre los parches "
             "elegidos.\n"
             "\n"
             "La novena, la destacada, es la que hay que llevarse. Es simplemente lo "
             "anterior escrito de corrido, pero puesta así muestra que la predicción se descompone "
             "en una suma de términos, y que cada término es la contribución de un parche por una "
             "medición concreta. Eso no es una explicación que alguien calcula después: es la "
             "cuenta misma que hizo el modelo. Ese es el reporte que le muestran al patólogo.\n"
             "\n"
             "La última junta todo en el entrenamiento. Las dos ramas se entrenan a la vez, cada "
             "una con su error de clasificación, y hay un tercer término que empuja a la rama "
             "interpretable a acercarse a la profunda, con un peso bastante alto. Sin ese término "
             "serían dos modelos separados corriendo en paralelo.")

    # ---- 12. Qué reportan y el contraste con lo nuestro ----
    # Fusión de dos láminas al recortar el deck. Los cuatro paneles que tenían entre las
    # dos se fueron al guion: la celda que nos toca ya está destacada en la tabla, y las
    # dos tablas juntas cuentan el contraste sin ayuda.
    s = content(prs, "Qué reportan, y el contraste con lo nuestro")
    add_textbox(s, 0.36, TOP, 9.28, 0.30, [
        ("Su Tabla 2: el mismo método aplicado sobre distintos modelos de base, en TCGA-BRCA",
         11, False, GRIS_BODY, F_BODY, PP_ALIGN.CENTER)])
    simple_table(s, 1.30, TOP + 0.32, 7.40,
                 ["Modelo de base", "Profundo  Acc / AUC", "Con SI-MIL  Acc / AUC"],
                 [["ABMIL", "0,937 / 0,974", "0,944 / 0,968"],
                  ["CLAM (el nuestro)", "0,937 / 0,972", "0,925 / 0,957"],
                  ["TransMIL", "0,934 / 0,936", "0,929 / 0,933"]],
                 col_fracs=[0.32, 0.34, 0.34], row_h=0.38, fs=12, destacar=1)
    simple_table(s, 0.36, TOP + 2.06, 9.28,
                 ["", "SI-MIL", "Lo nuestro"],
                 [["Cuándo aparece la interpretación", "durante el entrenamiento, por diseño",
                   "después, sobre modelos ya entrenados"],
                  ["Qué se interpreta", "mediciones con nombre de patología",
                   "expertos y slots aprendidos, sin nombre"],
                  ["Qué afecta al modelo", "lo cambia: la rama reorienta la atención",
                   "nada: el modelo ya está entrenado"]],
                 col_fracs=[0.30, 0.36, 0.34], row_h=0.34, fs=10.5)
    takeaway_bar(s, "Responden preguntas distintas: la nuestra es qué hace este modelo; la de "
                    "ellos, cómo construir uno que se explique solo.", t=TOP + 3.50, size=12.5)
    notes(s, "Los resultados. Esta tabla nos interesa más que las otras porque no compara el "
             "método contra otros métodos, sino el método aplicado sobre distintos modelos de "
             "base, y uno de esos modelos es el nuestro.\n"
             "\n"
             "Sobre el primero, que es el modelo de atención más simple, la exactitud sube un "
             "poco al agregarle la rama interpretable. Sobre el tercero baja apenas. Y sobre el "
             "nuestro, que es la fila destacada, baja: la exactitud pasa de nueve coma tres siete "
             "a nueve coma dos cinco, y el área bajo la curva de nueve coma siete dos a nueve "
             "coma cinco siete. Lo digo sin ánimo de desacreditar el trabajo, que me parece muy "
             "sólido, pero el titular de que no hay compromiso entre rendimiento e "
             "interpretabilidad se sostiene sobre el primer modelo, y esa fila del medio es "
             "exactamente la que nos correspondería a nosotros.\n"
             "\n"
             "Lo que sí sostienen con firmeza es lo otro: un modelo que use únicamente las "
             "mediciones con nombre pierde bastante, y el co-aprendizaje recupera casi todo. "
             "Cuando sacan cualquiera de las dos piezas centrales el rendimiento cae de forma "
             "clara, así que ninguna está de adorno.\n"
             "\n"
             "La tabla de abajo pone el método al lado de lo nuestro, y el contraste es nítido "
             "sin ser una competencia. La interpretación de ellos aparece durante el "
             "entrenamiento y por diseño, sobre mediciones que tienen nombre desde antes; la "
             "nuestra aparece después, sobre modelos ya congelados, y sobre expertos y unidades "
             "internas cuyos nombres se los pusimos nosotros mirando, todavía sin visto bueno. Lo "
             "de ellos cambia el modelo, lo nuestro no lo toca, y por eso el costo de equivocarse "
             "también es distinto: allá empeora el modelo, acá queda mal la descripción.\n"
             "\n"
             "Hay una crítica en su introducción que nos apunta directamente. Dicen que explicar "
             "un modelo después sufre de una desconexión entre las características con las que "
             "fue entrenado y aquellas con las que uno lo explica. Nuestro trabajo cae justo ahí. "
             "Aunque también coincidimos en dos cosas: ellos comparan qué parches elige un modelo "
             "y cuáles otro y encuentran muy poco solapamiento, que es lo mismo que medimos "
             "nosotros entre nuestros dos modelos, y para esa comparación eligen solo láminas "
             "donde los dos aciertan, que es nuestro mismo criterio.")

    # ---- 13. Qué costaría llevarlo acá, y qué preguntar ----
    # Fusión del inventario de costos con la lámina de preguntas: las preguntas 2 y 3 son
    # consecuencia directa de los dos bloqueos, así que se leen mejor debajo de ellos.
    s = content(prs, "Qué costaría llevarlo acá, y qué preguntar")
    bloqueos = [
        ("La magnificación es un bloqueo duro", TEAL_CARD2, ONCO_DARK,
         ["El segmentador de núcleos anda solo a 40 aumentos.",
          "Nuestras cohortes están a escalas distintas: sin pelear con esto, solo se "
          "aplicaría la cohorte pública."]),
        ("El preprocesamiento es de otro orden", TEAL_CARD2, ONCO_DARK,
         ["Cerca de 2 horas por lámina, unas 4400 para 2200, con tres tarjetas.",
          "Nosotros tenemos una sola, compartida y hoy con cola."]),
        ("El dato que puede cambiar todo", TEAL_CARD, TEAL_SQ,
         ["Publican el dataset YA PROCESADO, con la cohorte pública de mama adentro "
          "(910 láminas).",
          "Verificar el cruce es una tarde, y evita las 4400 horas."]),
    ]
    bw = (9.28 - 2 * 0.16) / 3
    alto_max = 0.0
    for i, (tit, fill, borde, lineas) in enumerate(bloqueos):
        sp = panel(s, 0.36 + i * (bw + 0.16), TOP, bw, None, tit,
                   ONCO_DARK if fill is TEAL_CARD2 else TEAL_TITLE, lineas, borde,
                   fill=fill, tsize=12, bsize=9.5)
        alto_max = max(alto_max, Emu(sp.height).inches)
    yy = TOP + alto_max + 0.16
    add_textbox(s, 0.36, yy, 9.28, 0.28, [
        ("Preguntas para la discusión", 13, True, TEAL_TITLE, F_BODY, PP_ALIGN.CENTER)],
        anchor=MSO_ANCHOR.MIDDLE)
    preguntas = [
        "¿El interés es ENTENDER esta línea, o EVALUARLA como candidata? Entenderla ya está "
        "hecho; evaluarla empieza por el segmentador de núcleos.",
        "Si es lo segundo, ¿se acepta acotarla a la cohorte pública, por la escala física?",
        "¿Vale una tarde verificar si su dataset publicado cubre nuestras láminas?",
        "Su patólogo declaró no relevante el 27 % de las mediciones. ¿Es aceptable para el "
        "estándar clínico?",
    ]
    yq = yy + 0.36
    for i, q in enumerate(preguntas):
        add_card(s, 0.36 + (i % 2) * 4.74, yq + (i // 2) * 0.94, 4.54, 0.82, i + 1, q,
                 size=10.5)
    notes(s, "Si en algún momento quisiéramos probar esto acá, conviene tener el inventario de "
             "costos antes que después. No es una propuesta, es lo que costaría.\n"
             "\n"
             "El primer bloqueo es el más duro y es de escala física. El segmentador de núcleos "
             "que usan está entrenado a cuarenta aumentos y solo a cuarenta, tanto que ellos "
             "mismos filtraron sus datasets para quedarse con láminas de esa magnificación. "
             "Nuestras cohortes están a escalas distintas entre sí: la pública cerca de cuarenta, "
             "la privada cerca de veinte, y de la tercera no tenemos un dato confiable.\n"
             "\n"
             "El segundo es de cómputo, y el número asusta un poco: cerca de dos horas por "
             "lámina, unas cuatro mil cuatrocientas en total para su colección, con tres tarjetas "
             "y una máquina muy grande. Nosotros tenemos una sola, compartida, hoy con trabajos "
             "de otra gente en cola. Pero ellos publican el dataset ya procesado, mapas de "
             "núcleos y mediciones incluidos, y la cohorte pública de mama está adentro. Si esas "
             "láminas se cruzan con las nuestras, el problema de cómputo desaparece entero.\n"
             "\n"
             "De ahí salen las preguntas que me gustaría conversar. La primera es de alcance y de "
             "ella depende todo lo demás: si el interés es entender esta línea de trabajo, eso ya "
             "está hecho; si es evaluarla como candidata, empieza por poner a andar el "
             "segmentador sobre nuestras láminas, y no cabe al lado de lo que ya está en marcha. "
             "La segunda y la tercera son consecuencia de los dos bloqueos: acotar la prueba a la "
             "cohorte pública, y gastar una tarde en verificar el cruce con su dataset, que es lo "
             "más barato que hay sobre la mesa.\n"
             "\n"
             "La cuarta es más de fondo. Cuando le mostraron los reportes a un patólogo, algo más "
             "de un cuarto de las mediciones que el modelo declara importantes le resultaron no "
             "relevantes. Me parece muy honesto publicarlo, y la pregunta es si ese número es "
             "aceptable para el estándar clínico que manejamos, o si es el argumento de que la "
             "interpretabilidad automática todavía no llega. Me queda un pendiente: desarmar las "
             "ecuaciones de la tres a la diez con el mismo detalle que las dos primeras.")

    # ---- cierre: reflow, auditoría, escala al tamaño del template, tipografía ----
    reflow_onco(prs, skip=keep_ids)
    auditar(prs, skip=keep_ids)
    scale_deck_to_1610(prs, skip=keep_ids)
    forzar_barlow(prs)
    os.makedirs(OUT_DIR, exist_ok=True)
    prs.save(DST)
    print("Guardado:", DST, "·", len(prs.slides), "slides · 13.333x7.5")


if __name__ == "__main__":
    build()
