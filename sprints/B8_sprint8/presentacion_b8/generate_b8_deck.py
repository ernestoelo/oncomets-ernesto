#!/usr/bin/env python
"""generate_b8_deck.py — deck del sprint B8, con DOS EJES.

Eje 1, SI-MIL (Kapse et al., CVPR 2024): la tarea de investigación cerrada. Las ECUACIONES,
la FIGURA ORIGINAL del modelo (Fig. 2, pág. 4) y el formato de deck del proyecto.
Insumo: `simil_explicacion_matematica.md`; números: `simil_estudio.md`.

Eje 2, la medición de atención contra las marcas del patólogo
(`../atencion_vs_patologo/{prereg.md,resultados.md}`): el resultado que reordenó las cuatro
familias del objetivo de mitosis. Nada se re-mide acá: el experimento cerró el 2-ago y este
archivo solo lo presenta.

Reparto del 3-ago (pedido de Ernesto): SI-MIL se COMPACTA A LA MITAD, de 12 láminas de
contenido a 6, y NO se borra, porque fue una de las tareas de investigación. Entra la
sección de mitosis en registro muy pedagógico, con sus dos figuras. Método de compactado,
el mismo del recorte del 31-jul: se fusionan pares y lo que sale de la lámina se cuenta
hablando, con el guion REESCRITO, no pegado.

Las seis fusiones de SI-MIL: qué propone + la figura del paper · las dos entradas +
ecuación 1 · ecuación 2 + qué implica para nuestro modelo · el puente Top-K + la rama
interpretable · las ecuaciones 3 a 10 · qué reportan y el contraste + qué costaría y qué
preguntar.

Recorte previo del 31-jul: de 19 a 14 láminas, retirando el ejemplo numérico del orden.

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
DST = os.path.join(OUT_DIR, "CLAM_Sprint8.pptx")
DST_LEGACY = os.path.join(OUT_DIR, "CLAM_Sprint8_SIMIL.pptx")   # nombre previo, monográfico

TEMPLATE = os.path.join(REPO, "sprints/B7_sprint7/Modelo OncoMets Spatial V1 Deep-LLM-V.pptx")
TPL_KEEP = (0, 1)          # portada de marca + lámina de título, nativas a 13.333
FECHA_REUNION = "07/08/2026"      # confirmada por Ernesto el 31-jul: «el próximo viernes»

# --- figura del paper (única imagen del deck), recortada de la página 4 a 400 DPI ---
FIG2_FULL = os.path.join(ASSETS, "simil_fig2_full.png")   # los tres paneles
FIG2_A = os.path.join(ASSETS, "simil_fig2_a.png")         # (a) SI-MIL overview
FIG2_B = os.path.join(ASSETS, "simil_fig2_b.png")         # (b) Conventional MIL branch
FIG2_C = os.path.join(ASSETS, "simil_fig2_c.png")         # (c) Self-Interpretable branch

# --- figuras de la medición de atención (producción NUESTRA, no figura de paper) ---
# Recortadas de las originales por prep_assets_atencion.py: las de archivo traen títulos de
# matplotlib y un hueco de ~390 px entre las dos regiones de escaneo del .bif.
FIG_MAPAS = os.path.join(ASSETS, "atencion_dos_regiones.png")      # grilla 2x2
FIG_MITOSIS = os.path.join(ASSETS, "mitosis_region_anotada.png")   # con el recuadro de foco
FIG_ZOOM = os.path.join(ASSETS, "mitosis_zoom.png")                # el detalle del recuadro

# --- números de la medición, verificados contra auc_por_checkpoint.csv (4 ckpt primarios,
# cabeza de la clase verdadera). El orden es el de la escalera que se dibuja en la lámina.
ESCALERA = [
    ("Mitosis", 28, 0.890, True),
    ("Núcleos de alto grado", 13, 0.828, True),
    ("Tumor", 48, 0.826, False),
    ("Necrosis", 18, 0.748, False),
    ("Estroma", 12, 0.537, False),
    ("Linfocitos", 23, 0.322, False),
    ("Tejido adiposo", 27, 0.154, False),
]

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
# Figuras nativas de la sección de mitosis
# ============================================================================
# Una escalera de siete AUC pide un gráfico y no una lista ([[deck-contenido-visual-no-bullets]]).
# Se dibuja con la gramática del template en vez de add_chart: un gráfico de python-pptx
# arrastra la paleta de Office y hay que repintarlo entero, y acá el objeto es una barra por
# fila, que es exactamente el arquetipo «dato» del template.
def barras_ranking(slide, l, t, w, h, datos, x_eje=2.62, ancho_eje=5.40, fs=10.5):
    """Barras horizontales de AUC con la marca del azar. `datos` = (nombre, n, auc, interes)."""
    fila = h / len(datos)
    alto_barra = min(0.26, fila * 0.62)
    x0 = l + x_eje
    for i, (nombre, n, auc, interes) in enumerate(datos):
        cy = t + i * fila + fila / 2
        add_textbox(slide, l, cy - 0.15, x_eje - 0.14, 0.30,
                    [("%s  (n = %d)" % (nombre, n), fs, interes, ONCO_DARK if interes else INK,
                      F_BODY, PP_ALIGN.RIGHT)], anchor=MSO_ANCHOR.MIDDLE)
        _rect(slide, x0, cy - alto_barra / 2, ancho_eje * auc, alto_barra,
              ONCO_DARK if interes else ONCO_PANEL)
        add_textbox(slide, x0 + ancho_eje * auc + 0.08, cy - 0.15, 0.72, 0.30,
                    [("%.3f" % auc, fs, interes, ONCO_DARK if interes else GRIS_BODY, F_BODY)],
                    anchor=MSO_ANCHOR.MIDDLE)
    # el azar, que es la única referencia que este estadístico tiene
    x_nulo = x0 + ancho_eje * 0.5
    ln = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x_nulo), Inches(t - 0.16),
                                    Inches(x_nulo), Inches(t + h + 0.02))
    ln.line.color.rgb = ONCO_INK; ln.line.width = Pt(1.25)
    lnpr = ln.line._get_or_add_ln()
    lnpr.append(lnpr.makeelement(qn('a:prstDash'), {'val': 'dash'}))
    ln.shadow.inherit = False
    add_textbox(slide, x_nulo - 0.80, t - 0.42, 1.60, 0.26,
                [("azar = 0,5", 9.5, True, ONCO_INK, F_BODY, PP_ALIGN.CENTER)],
                anchor=MSO_ANCHOR.MIDDLE)


def cinta_ranking(slide, l, t, w, marcados, n=34, h=0.40, fs=9):
    """Los N parches de la lámina ordenados por atención, con los anotados resaltados.

    Es la figura del ESTADÍSTICO, que es justamente lo que no dejó ninguna imagen cuando se
    hizo la medición y por eso no se retuvo ([[hallazgo-necesita-forma-presentable]]). Cada
    celda es un parche; el orden es de más a menos atención."""
    cw = w / n
    for i in range(n):
        col = ONCO_DARK if i in marcados else ONCO_PANEL
        sp = _rect(slide, l + i * cw, t, cw * 0.86, h, col)
        sp.line.color.rgb = WHITE; sp.line.width = Pt(0.5)
    _conn(slide, l, t + h + 0.20, l + w, t + h + 0.20)
    add_textbox(slide, l, t + h + 0.26, 2.60, 0.26,
                [("más atención", fs, True, ONCO_DARK, F_BODY)])
    add_textbox(slide, l + w - 2.60, t + h + 0.26, 2.60, 0.26,
                [("menos atención", fs, True, GRIS_BODY, F_BODY, PP_ALIGN.RIGHT)])


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
            _set_solo_run(sh.text_frame.paragraphs[0], "OncoMets · Sprint 8")
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
    notes(s, "Esta vez traigo dos cosas, y son de naturaleza distinta.\n"
             "\n"
             "La primera es la revisión de uno de los papers que habían quedado encargados, que "
             "propone un modelo que se explica solo. Para conseguirlo invierte el reparto de "
             "trabajo habitual: la red profunda deja de ser la que predice y pasa a ser la que "
             "enseña dónde mirar, mientras la predicción la hace un modelo lineal sobre "
             "mediciones de núcleos que tienen nombre de patología. Es una lectura terminada, "
             "así que la voy a contar más comprimida que la vez pasada.\n"
             "\n"
             "La segunda es una medición nuestra, y es lo que más me importa dejar claro hoy. "
             "Fuimos a ver si el modelo mira donde el patólogo marcó las mitosis. Tiene un "
             "resultado, y el resultado cambió hacia dónde apunta el trabajo que sigue.")

    # ---- 2. Los dos ejes de hoy ----
    # Antes era la lámina de objetivos de la revisión de SI-MIL. Con el deck a dos ejes, lo
    # que tiene que fijar es el mapa del recorrido y el peso relativo de cada parte.
    s = content(prs, "Dos cosas, y una cambia el plan", size=30)
    ejes = [
        (TEAL_CARD2, ONCO_DARK, "Un paper leído", "SI-MIL, CVPR 2024",
         ["Qué propone, sobre la figura y las ecuaciones del paper.",
          "Qué acota de los mapas de atención que venimos mostrando.",
          "Qué costaría traerlo acá, y qué preguntas deja abiertas."],
         "lectura terminada"),
        (TEAL_CARD, TEAL_SQ, "Una medición nuestra", "¿mira el modelo donde marcó el patólogo?",
         ["Un número, con su nulo y sus controles.",
          "Mira bien y responde mal, que es el hallazgo.",
          "Por qué eso reordenó las cuatro respuestas posibles."],
         "cambia el plan"),
    ]
    bw = (9.28 - 0.34) / 2
    for i, (fill, borde, rot, tit, lineas, pie) in enumerate(ejes):
        x = 0.36 + i * (bw + 0.34)
        _grupo(s, x, TOP, bw, 3.46, fill=fill)
        add_textbox(s, x + 0.24, TOP + 0.16, bw - 0.48, 0.28,
                    [(rot.upper(), 10.5, True, GRIS_BODY, F_BODY)])
        add_textbox(s, x + 0.24, TOP + 0.46, bw - 0.48, 0.62,
                    [(tit, 17, True, TEAL_TITLE, F_BODY)], anchor=MSO_ANCHOR.TOP)
        for j, ln in enumerate(lineas):
            add_card(s, x + 0.24, TOP + 1.22 + j * 0.62, bw - 0.48, 0.52, j + 1, ln, size=11)
        _rect(s, x + 0.24, TOP + 3.10, bw - 0.48, 0.02, borde)
        add_textbox(s, x + 0.24, TOP + 3.14, bw - 0.48, 0.28,
                    [(pie, 12, True, borde, F_BODY, PP_ALIGN.CENTER)], anchor=MSO_ANCHOR.MIDDLE)
    takeaway_bar(s, "Del paper quedó pendiente desarmar sus ecuaciones 3 a 10 con el detalle "
                    "de las dos primeras.", t=TOP + 3.62, size=12)
    notes(s, "Dejo fijado el mapa del recorrido, porque las dos partes no pesan igual.\n"
             "\n"
             "La de la izquierda es la lectura del paper. Voy a contar qué propone apoyándome en "
             "la figura y en las ecuaciones originales, después qué nos acota respecto de los "
             "mapas de atención que venimos presentando, y termino con lo que costaría traerlo a "
             "nuestros datos y las preguntas que me gustaría conversar. Es una lectura que ya está "
             "terminada, y la traigo bastante más comprimida que la vez pasada; me quedó "
             "pendiente desarmar sus ecuaciones de la tres a la diez con el mismo cuidado que las "
             "dos primeras, y prefiero decirlo de entrada.\n"
             "\n"
             "La de la derecha es una medición que hicimos nosotros, y es la parte a la que le "
             "quiero dedicar tiempo. La pregunta salió de una observación del patólogo: que en "
             "mitosis los núcleos son finos y dispersos, y que a nuestros modelos se les escapan "
             "porque quizá esos parches no reciben atención suficiente. Esa frase se puede medir. "
             "Voy a mostrar el número, cómo nos aseguramos de que no fuera casualidad, y un "
             "desenlace que no esperábamos. Lo digo ya para que se escuche todo lo demás con eso "
             "en la cabeza: el resultado cambió hacia dónde apunta el trabajo que sigue.")

    # =======================================================================
    # EJE 1 — SI-MIL, compactado a la mitad (12 láminas de contenido a 6)
    # =======================================================================
    # Método del recorte, el mismo del 31-jul: se fusionan pares y lo que sale de la
    # lámina se cuenta HABLANDO. El guion de cada fusionada se reescribe, no se pega.

    # ---- 3. Qué propone + la figura del paper ----
    # Fusión de «qué propone, en una frase» con «la arquitectura en la figura». La figura
    # ES el qué propone dibujado, así que separarlas obligaba a repetir la frase. Las tres
    # tarjetas de consecuencias y la fila de cifras del paper pasaron al guion.
    s = content(prs, "SI-MIL: qué propone, y su arquitectura")
    caption(s, 0.36, TOP, 9.28,
            "Taming Deep MIL for Self-Interpretability in Gigapixel Histopathology · "
            "Kapse et al., CVPR 2024", size=10.5, col=GRIS_BODY, bold=True)
    add_textbox(s, 0.36, TOP + 0.26, 9.28, 0.46, [
        ("Que el modelo prediga con una combinación lineal de mediciones de núcleos que "
         "tienen nombre de patología, y que la red profunda quede como el maestro que le "
         "enseña dónde mirar.", 13.5, True, TEAL_TITLE, F_BODY, PP_ALIGN.CENTER)],
        anchor=MSO_ANCHOR.MIDDLE)
    add_image_fit(s, FIG2_FULL, 0.22, TOP + 0.80, 9.56, 2.52, align="top")
    caption(s, 0.22, TOP + 3.34, 9.56,
            "(a) el recorrido completo, de la lámina a las dos predicciones · "
            "(b) y (c) el detalle de cada rama", size=10, col=TEAL_TITLE, bold=True)
    takeaway_bar(s, "Dos caminos que salen de la misma lámina: uno mide, el otro "
                    "selecciona.", t=TOP + 3.62, size=13)
    notes(s, "Empiezo por el método. El nombre completo habla de domesticar un modelo profundo "
             "para que se explique solo, y eso resume bien la ambición: no acompañar la "
             "predicción con una explicación, sino conseguir que la explicación sea la "
             "predicción.\n"
             "\n"
             "La idea cabe en la frase de arriba, y tiene tres consecuencias que conviene "
             "anticipar. La red profunda deja de predecir, y su único producto pasa a ser una "
             "selección de veinte parches. La predicción se calcula sobre mediciones que un "
             "patólogo puede leer, doscientas cuarenta y seis, cosas como la asimetría de la "
             "solidez de los núcleos o la mezcla de tipos celulares de una región. Y la más "
             "audaz de las tres: cuando el modelo se pone a funcionar, la rama profunda se "
             "descarta entera, no viaja con el modelo. El que sale a producción tiene "
             "seiscientos veinticinco mil parámetros, del mismo orden que el modelo profundo "
             "con el que lo comparan, así que la mejora no viene del tamaño.\n"
             "\n"
             "La figura es la del paper y prefiero mostrarla tal cual. Arriba a la izquierda "
             "está la lámina cuadriculada en parches, y de ahí salen dos caminos paralelos que "
             "describen exactamente los mismos parches, en el mismo orden, de dos maneras "
             "distintas. El de arriba pasa por un extractor profundo y produce, por cada "
             "parche, un vector de números que eligió una red para sí misma; nosotros usaríamos "
             "aquí nuestro extractor. El de abajo parte de los mapas de núcleos ya segmentados "
             "y produce mediciones de morfología, de grafo de células y de heterogeneidad "
             "espacial, todas con nombre legible.\n"
             "\n"
             "En el medio está la caja amarilla, que es la bisagra del diseño: toma la atención "
             "que calculó el camino profundo, con ella elige un puñado de parches, y esa "
             "selección se aplica sobre el otro camino. Y fíjense en el recuadro punteado de "
             "arriba a la derecha, que dice descartado en inferencia: ese es el clasificador "
             "del camino profundo, y no llega a producción.")

    # ---- 4. Las dos entradas + la ecuación 1 ----
    # Fusión: la ecuación 1 opera justamente sobre la entrada del camino profundo, así que
    # la convención de notación y la ecuación se explican juntas. Los tres paneles de glosa
    # de la ecuación se fueron al guion; la tabla de los dos anchos se queda, porque es la
    # que fija la convención que el paper usa sin remarcarla.
    s = content(prs, "Dos descripciones del mismo parche, y la ecuación 1")
    BW, BH = 2.30, 0.62
    y1, y2 = TOP + 0.06, TOP + 0.90
    _proc(s, 0.36, (y1 + y2) / 2 - 0.06, 1.60, BH, "Un parche", size=11.5)
    _proc(s, 2.44, y1, BW, BH, "Extractor profundo", dim="CONCH en nuestro caso", size=11)
    _dato(s, 5.10, y1 + 0.06, 1.40, 0.50, "g_i ∈ ℝ^D", size=11.5)
    _dim(s, 6.66, y1 + 0.08, 2.92, "D = 512 · números que eligió una red",
         size=9.5, align=PP_ALIGN.LEFT)
    _proc_claro(s, 2.44, y2, BW, BH, "PathExpert", size=11, dim="sobre el mapa de núcleos")
    _dato(s, 5.10, y2 + 0.06, 1.40, 0.50, "f_i ∈ ℝ^d", size=11.5)
    _dim(s, 6.66, y2 + 0.00, 2.92, "d = 246 · mediciones con nombre",
         size=9.5, align=PP_ALIGN.LEFT)
    _dim(s, 6.66, y2 + 0.26, 2.92, "el mapa lo produce HoVer-Net",
         size=9, align=PP_ALIGN.LEFT, col=GRIS_BODY)
    _conn(s, 1.96, (y1 + y2) / 2 + 0.25, 2.44, y1 + BH / 2)
    _conn(s, 1.96, (y1 + y2) / 2 + 0.25, 2.44, y2 + BH / 2)
    _conn(s, 2.44 + BW, y1 + BH / 2, 5.10, y1 + BH / 2)
    _conn(s, 2.44 + BW, y2 + BH / 2, 5.10, y2 + BH / 2)
    simple_table(s, 0.36, TOP + 1.70, 9.28,
                 ["", "Ancho del vector", "Quién eligió los números", "¿Se puede leer?"],
                 [["Camino profundo", "D = 512", "una red, para su propio objetivo", "no"],
                  ["Camino PathExpert", "d = 246", "la literatura de patología",
                   "sí, cada columna tiene nombre"]],
                 col_fracs=[0.22, 0.16, 0.36, 0.26], row_h=0.34, fs=10.5)
    eq(s, 0.36, TOP + 2.90, 9.28,
       "g̃_i = H(g_i)          α_i = A^p(g̃_i)          i ∈ {1, 2, … N}",
       num="(1)", size=14.5, h=0.52)
    takeaway_bar(s, "La atención de un parche depende de los demás: no es una propiedad "
                    "suya, es su tajada de un presupuesto que suma 100 %.",
                 t=TOP + 3.56, size=12)
    notes(s, "Antes de la primera ecuación hay que fijar una convención de notación que el "
             "paper usa sin remarcarla, y que si se pasa por alto vuelve confuso todo lo "
             "demás.\n"
             "\n"
             "Se trabaja con dos anchos distintos y se escriben con la misma letra, una en "
             "mayúscula y otra en minúscula. La mayúscula es el ancho del camino profundo, el "
             "vector que produce el extractor; en nuestro pipeline son quinientos doce números "
             "por parche. La minúscula es el ancho del otro camino, doscientas cuarenta y seis "
             "mediciones de núcleos. Son dos espacios completamente distintos, y de paso queda "
             "ordenada la relación entre los dos papers que habían quedado encargados: el mapa "
             "de núcleos del que salen esas mediciones lo produce el segmentador, que es el "
             "otro paper. No son dos ángulos, son la misma cadena.\n"
             "\n"
             "Lo que hay que retener de la tabla es que los dos caminos tienen la misma "
             "cantidad de filas, los mismos parches y en el mismo orden. Lo único que cambia es "
             "el ancho y, sobre todo, quién eligió esos números: en un caso una red, para un "
             "objetivo que no es el nuestro; en el otro, la literatura de patología, de "
             "antemano y con un nombre pegado a cada columna.\n"
             "\n"
             "La ecuación de abajo tiene dos pasos y describe algo que ya conocemos, porque es "
             "también lo que hace nuestro modelo. El primero es el proyector, que toma el vector "
             "del extractor y lo reescribe midiéndolo contra unas varas que se aprenden durante "
             "el entrenamiento; en nuestro modelo es una capa lineal con su activación. El "
             "segundo es la atención: hay un presupuesto de importancia del cien por ciento para "
             "repartir entre todos los parches, y el módulo convierte un puntaje crudo por "
             "parche en porcentajes que suman uno.\n"
             "\n"
             "De ahí sale lo de abajo de todo, que va a importar mucho más adelante. Como el "
             "reparto suma uno sobre todos los parches, la atención de un parche depende de "
             "cuántos y cuáles sean los demás. No es una propiedad del parche, es su tajada. El "
             "mismo tejido en una lámina chica y en una grande recibe atención distinta.")

    # ---- 5. Ecuación 2: el orden, y qué implica para nosotros ----
    # Fusión: el orden de las operaciones y el mapeo a nuestro código son la misma
    # discusión, porque lo que se mapea es precisamente en cuál de los dos órdenes cae
    # nuestro modelo. La tabla línea por línea contra model_clam.py pasó al guion.
    s = content(prs, "Ecuación 2: el orden de dos operaciones")
    eq(s, 0.36, TOP, 9.28, "Ŷ_g = ψ( Σ_i C( α_i · g̃_i ) )", num="(2)", size=16, h=0.48)
    ya, yb = TOP + 0.58, TOP + 1.24
    _rot_label(s, -0.30, ya + 0.11, 1.40, 0.32, "ORDEN A", col=GRIS_BODY)
    _rot_label(s, -0.30, yb + 0.11, 1.40, 0.32, "ORDEN B", col=ONCO_DARK)
    axs = [0.52, 2.66, 4.80, 6.94]
    pasos_a = [("Pesar cada parche", "α_i · g̃_i"), ("Sumar", "una sola ficha"),
               ("Clasificar", "C( · )"), ("Un logit", "y nada más")]
    for x, (t1, t2) in zip(axs, pasos_a):
        _proc_claro(s, x, ya, 1.86, 0.54, t1, size=11, dim=t2)
    for i in range(3):
        _conn(s, axs[i] + 1.86, ya + 0.27, axs[i + 1], ya + 0.27)
    _dim(s, 8.92, ya + 0.14, 1.00, "= CLAM", size=10.5, align=PP_ALIGN.LEFT, col=GRIS_BODY)
    pasos_b = [("Pesar cada parche", "α_i · g̃_i"), ("Clasificar cada uno", "C( · ) N veces"),
               ("Sumar los puntajes", "N sumandos"), ("El mismo logit", "y el desglose")]
    for x, (t1, t2) in zip(axs, pasos_b):
        _proc(s, x, yb, 1.86, 0.54, t1, size=11, dim=t2)
    for i in range(3):
        _conn(s, axs[i] + 1.86, yb + 0.27, axs[i + 1], yb + 0.27)
    _dim(s, 8.92, yb + 0.14, 1.10, "= ecuación 2", size=10.5, align=PP_ALIGN.LEFT,
         col=ONCO_DARK)
    simple_table(s, 0.36, TOP + 1.94, 9.28,
                 ["Después del forward queda", "Orden A", "Orden B"],
                 [["la ficha fundida", "sí, un vector de 512", "no existe"],
                  ["el logit final", "un número", "el mismo número"],
                  ["desglose por parche", "no existe", "N números CON SIGNO"]],
                 col_fracs=[0.30, 0.34, 0.36], row_h=0.34, fs=10.5, destacar=2)
    takeaway_bar(s, "Nuestro modelo es el orden A. Y su atención sale de una softmax, así "
                    "que dice CUÁNTO mira cada parche, nunca hacia qué clase empuja.",
                 t=TOP + 3.34, size=12)
    notes(s, "Esta es la ecuación que cuesta, y cuesta porque parece decir algo obvio. Uno la "
             "lee y entiende multiplicá por la atención, sumá y clasificá. En realidad está "
             "diciendo algo muy específico sobre el orden de dos operaciones.\n"
             "\n"
             "El camino de arriba es el que usa nuestro modelo. Se pesa cada parche por su "
             "atención, se suman todos y queda una única ficha promedio; a esa ficha se le "
             "aplica el clasificador y sale un número. Pensémoslo como una licuadora: se echan "
             "las frutas en su proporción, se licúa, queda un solo jugo, se prueba y se "
             "dictamina. El camino de abajo es el de la ecuación: se pesa cada parche igual, "
             "pero el clasificador se aplica a cada uno por separado, tantas veces como parches "
             "haya, y recién después se suma. Se prueba cada fruta ya medida en su proporción, "
             "se anota su puntaje en una libreta, y se suma la columna.\n"
             "\n"
             "Escrita, la diferencia es solamente dónde cierra el paréntesis del clasificador, y "
             "el logit final es el mismo número por los dos caminos. Lo que cambia es qué queda "
             "en memoria cuando el modelo termina de calcular. Arriba queda una ficha fundida y "
             "ningún desglose; abajo no hay ficha fundida, pero quedan tantos puntajes como "
             "parches, con signo, que suman exacto el resultado. Una vez licuado el jugo no hay "
             "manera de separarlo en frutas: uno se acuerda de las proporciones que usó, pero la "
             "proporción dice cuánta fruta se puso, no si esa fruta era dulce o ácida.\n"
             "\n"
             "Fui a verificar dónde cae nuestro modelo, línea por línea. El proyector es nuestra "
             "primera capa lineal con su activación, la atención es nuestro módulo con compuerta "
             "normalizando sobre los parches, el predictor son nuestras capas de salida, una por "
             "clase, y el orden es el primero de los dos: nuestro modelo funde y después "
             "clasifica. Con dos diferencias, porque el paper escribe una versión más limpia que "
             "la nuestra: nuestra atención es por clase, y tenemos ramas de instancia que en "
             "esta formulación no existen.\n"
             "\n"
             "Y queda el punto que más nos toca, el de abajo. Uno podría pensar que la atención "
             "rescata lo que el orden A pierde, y no: sale de una softmax, así que todos sus "
             "valores son positivos, y un número positivo expresa cuánto, nunca hacia dónde. El "
             "caso que le preocupa al paper es un parche que se lleva más de la mitad de la "
             "atención y que al mismo tiempo es el que más empuja en contra de la clase: el mapa "
             "de calor le pinta un rojo intenso, y quien lo mira lee que ahí estaba la "
             "evidencia. Esto acota exactamente lo que podemos decir de nuestros mapas, y lo "
             "vamos a necesitar en la segunda parte. Lo que sí podríamos hacer, porque nuestro "
             "predictor también es lineal, es desarmar el resultado por parche a posteriori. La "
             "diferencia es que en el paper ese desglose es la definición del modelo, no algo "
             "que uno deriva cuando ya terminó.")

    # ---- 6. El puente Top-K + la rama interpretable ----
    # Fusión: el embudo termina justo donde empieza la otra rama, así que contarlas
    # seguidas evita repetir la cuenta de los 20 parches. El panel del gradiente y el de
    # por qué se gira la matriz se fueron al guion.
    s = content(prs, "El puente, y la rama que sí se lee")
    y = TOP + 0.10
    y2 = y + 1.00
    _proc(s, 0.36, y, 3.20, 0.66, "Camino profundo",
          dim="10 000 × 512 = 5 120 000 números", size=11.5)
    _dim(s, 6.10, y + 0.14, 3.50, "se descarta entero", size=10.5, align=PP_ALIGN.LEFT,
         col=GRIS_BODY)
    _proc_claro(s, 0.36, y2, 3.20, 0.66, "Camino PathExpert", size=11.5,
                dim="10 000 × 246 = 2 460 000 números")
    _oper(s, 4.10, y2 + 0.33, sym="K", d=0.44)
    _proc(s, 4.94, y2, 2.46, 0.66, "20 × 246 = 4920", dim="esto es lo que predice", size=12)
    _conn(s, 3.56, y + 0.33, 4.10, y + 0.33, arrow=False)
    _conn(s, 4.10, y + 0.33, 4.10, y2 + 0.09)
    _dim(s, 4.28, y + 0.68, 3.20, "su ÚNICO producto: 20 índices", size=9.5,
         align=PP_ALIGN.LEFT, col=ONCO_DARK)
    _conn(s, 3.56, y2 + 0.33, 3.87, y2 + 0.33)
    _conn(s, 4.33, y2 + 0.33, 4.94, y2 + 0.33)
    add_textbox(s, 0.36, TOP + 1.92, 9.28, 0.38, [
        ("De cinco millones de números ilegibles a 4920 que tienen nombre.",
         14, True, TEAL_TITLE, F_BODY, PP_ALIGN.CENTER)], anchor=MSO_ANCHOR.MIDDLE)
    simple_table(s, 0.36, TOP + 2.40, 4.86,
                 ["", "α", "β"],
                 [["¿cuántos hay?", "N, uno por parche", "246, uno por medición"],
                  ["¿qué contestan?", "qué región importa", "qué medición importa"],
                  ["¿suman 1?", "sí, softmax sobre N", "no, sigmoide una por una"]],
                 col_fracs=[0.28, 0.36, 0.36], row_h=0.36, fs=9.5, destacar=2)
    panel(s, 5.46, TOP + 2.40, 4.18, None, "Por qué esa última fila no es un detalle",
          ONCO_DARK,
          ["α reparte un presupuesto fijo: subir uno baja los demás.",
           "β son 246 compuertas independientes, no una torta. Por eso el paper puede "
           "empujarlas casi todas a cero y forzar que el reporte tenga pocos renglones."],
          ONCO_DARK, fill=TEAL_CARD, tsize=12.5, bsize=9.5, markup=True)
    notes(s, "Este es el movimiento central del diseño, el que hace que las dos ramas dejen de "
             "ser dos modelos corriendo en paralelo.\n"
             "\n"
             "Tomemos una lámina nuestra de diez mil parches, que es un tamaño realista. Por el "
             "camino profundo eso son más de cinco millones de números, y todos se descartan: ni "
             "uno solo llega a la predicción final. Lo único que ese camino aporta son veinte "
             "enteros, veinte índices que dicen cuáles parches valen la pena mirar. Por el otro "
             "camino hay dos millones y medio de números, de los que se conservan las veinte "
             "filas que la primera rama señaló. Quedan cuatro mil novecientos veinte números, y "
             "sobre esos se predice. Ese embudo es la figura entera.\n"
             "\n"
             "Y no es tan directo como suena. Quedarse con los veinte mayores es una operación "
             "de selección, escalonada, y una operación así no tiene derivada, así que el "
             "entrenamiento no puede atravesarla. Por eso usan una versión perturbada de esa "
             "selección, que sí deja pasar el gradiente. Sin eso, las dos ramas nunca "
             "aprenderían la una de la otra.\n"
             "\n"
             "La otra rama tiene la misma forma que la primera: una pila de datos, un módulo de "
             "atención, unos puntajes y una multiplicación. Lo único que agrega son dos "
             "transposiciones, al principio y al final, y el motivo es simple: la maquinaria de "
             "atención sabe hacer una sola cosa, que es recibir una matriz y devolver un puntaje "
             "por cada fila. En la rama anterior las filas eran parches, así que devolvió un "
             "puntaje por parche. Acá queremos un puntaje por medición, así que se gira la "
             "matriz para que las mediciones pasen a ser las filas, y al final se gira de "
             "vuelta.\n"
             "\n"
             "La tabla compara los dos conjuntos de pesos, y quiero detenerme en la última fila. "
             "Los pesos de parche reparten un presupuesto fijo: si uno sube, los otros bajan. "
             "Los pesos de medición no; cada uno sale de su propia compuerta, calculada por "
             "separado. Eso no es un tecnicismo: es lo que le permite al paper empujar después "
             "casi todas esas compuertas a cero, para que el reporte que ve el patólogo tenga "
             "pocos renglones en vez de doscientos cuarenta y seis.")

    # ---- 7. Las ecuaciones 3 a 10, en panorama ----
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
             "estandariza, después los pasa por una sigmoide con temperatura, que es lo que "
             "empuja a la mayoría hacia cero. La seis aplica esos pesos, atenuando o realzando "
             "cada columna. La siete y la ocho son el predictor lineal y la suma sobre los "
             "parches elegidos.\n"
             "\n"
             "La novena, la destacada, es la que hay que llevarse. Es lo anterior escrito de "
             "corrido, pero puesta así muestra que la predicción se descompone en una suma de "
             "términos, y que cada término es la contribución de un parche por una medición "
             "concreta. Eso no es una explicación que alguien calcula después: es la cuenta "
             "misma que hizo el modelo, y ese es el reporte que le muestran al patólogo.\n"
             "\n"
             "La última junta todo en el entrenamiento. Las dos ramas se entrenan a la vez, cada "
             "una con su error de clasificación, y hay un tercer término que empuja a la rama "
             "interpretable a acercarse a la profunda, con un peso bastante alto. Sin ese "
             "término serían dos modelos separados corriendo en paralelo.")

    # ---- 8. Qué reportan, qué costaría y qué preguntar ----
    # Fusión de tres cosas: los resultados, el inventario de costos y las preguntas. La
    # tabla de contraste con lo nuestro y dos de las cuatro preguntas se fueron al guion.
    s = content(prs, "Qué reportan, qué costaría, y qué preguntar")
    caption(s, 0.36, TOP, 9.28,
            "Su Tabla 2: el mismo método aplicado sobre distintos modelos de base, en "
            "TCGA-BRCA", size=10.5, col=GRIS_BODY, bold=True)
    simple_table(s, 1.42, TOP + 0.28, 7.16,
                 ["Modelo de base", "Profundo  Acc / AUC", "Con SI-MIL  Acc / AUC"],
                 [["ABMIL", "0,937 / 0,974", "0,944 / 0,968"],
                  ["CLAM (el nuestro)", "0,937 / 0,972", "0,925 / 0,957"],
                  ["TransMIL", "0,934 / 0,936", "0,929 / 0,933"]],
                 col_fracs=[0.32, 0.34, 0.34], row_h=0.36, fs=11, destacar=1)
    bloqueos = [
        ("La magnificación bloquea", TEAL_CARD2, ONCO_DARK,
         ["El segmentador de núcleos anda solo a 40 aumentos.",
          "Sin pelear con eso, solo aplicaría a la cohorte pública."]),
        ("El cómputo es de otro orden", TEAL_CARD2, ONCO_DARK,
         ["Cerca de 2 horas por lámina, unas 4400 para 2200, con tres tarjetas.",
          "Nosotros tenemos una sola, compartida y hoy con cola."]),
        ("El dato que puede cambiar todo", TEAL_CARD, TEAL_SQ,
         ["Publican el dataset YA PROCESADO, con la cohorte pública de mama adentro.",
          "Verificar el cruce es una tarde, y evita las 4400 horas."]),
    ]
    bw = (9.28 - 2 * 0.16) / 3
    alto_max = 0.0
    for i, (tit, fill, borde, lineas) in enumerate(bloqueos):
        sp = panel(s, 0.36 + i * (bw + 0.16), TOP + 1.86, bw, None, tit,
                   ONCO_DARK if fill is TEAL_CARD2 else TEAL_TITLE, lineas, borde,
                   fill=fill, tsize=11.5, bsize=9.5)
        alto_max = max(alto_max, Emu(sp.height).inches)
    yq = TOP + 1.86 + alto_max + 0.14
    preguntas = [
        "¿El interés es ENTENDER esta línea, o EVALUARLA como candidata?",
        "¿Vale una tarde verificar si su dataset publicado cubre nuestras láminas?",
    ]
    for i, q in enumerate(preguntas):
        add_card(s, 0.36 + i * 4.74, yq, 4.54, 0.56, i + 1, q, size=10.5)
    notes(s, "Los resultados. Esta tabla nos interesa más que las otras porque no compara el "
             "método contra otros métodos, sino el método aplicado sobre distintos modelos de "
             "base, y uno de esos modelos es el nuestro.\n"
             "\n"
             "Sobre el primero, que es el modelo de atención más simple, la exactitud sube un "
             "poco al agregarle la rama interpretable. Sobre el tercero baja apenas. Y sobre el "
             "nuestro, que es la fila destacada, baja: la exactitud pasa de nueve coma tres "
             "siete a nueve coma dos cinco, y el área bajo la curva de nueve coma siete dos a "
             "nueve coma cinco siete. Lo digo sin ánimo de desacreditar el trabajo, que me "
             "parece muy sólido, pero el titular de que no hay compromiso entre rendimiento e "
             "interpretabilidad se sostiene sobre el primer modelo, y esa fila del medio es "
             "exactamente la que nos correspondería.\n"
             "\n"
             "Lo que sí sostienen con firmeza es lo otro: un modelo que use únicamente las "
             "mediciones con nombre pierde bastante, y el co-aprendizaje recupera casi todo.\n"
             "\n"
             "Vale la comparación con lo nuestro, que es nítida sin ser una competencia. La "
             "interpretación de ellos aparece durante el entrenamiento y por diseño, sobre "
             "mediciones que tienen nombre desde antes; la nuestra aparece después, sobre "
             "modelos ya congelados, y sobre unidades internas cuyos nombres se los pusimos "
             "nosotros mirando, todavía sin visto bueno. Lo de ellos cambia el modelo, lo "
             "nuestro no lo toca, y por eso el costo de equivocarse también es distinto: allá "
             "empeora el modelo, acá queda mal la descripción. Hay una crítica en su "
             "introducción que nos apunta directamente: dicen que explicar un modelo después "
             "sufre de una desconexión entre las características con las que fue entrenado y "
             "aquellas con las que uno lo explica.\n"
             "\n"
             "Si en algún momento quisiéramos probar esto acá, los tres bloques son el "
             "inventario de costos. El primero es de escala física y es el más duro: el "
             "segmentador está entrenado a cuarenta aumentos y solo a cuarenta, tanto que ellos "
             "mismos filtraron sus datasets para quedarse con láminas de esa magnificación, y "
             "nuestras cohortes están a escalas distintas entre sí. El segundo es de cómputo, y "
             "el número asusta un poco. Pero el tercero lo desarma: ellos publican el dataset ya "
             "procesado, mapas de núcleos y mediciones incluidos, y la cohorte pública de mama "
             "está adentro, así que si esas láminas se cruzan con las nuestras el problema de "
             "cómputo desaparece entero.\n"
             "\n"
             "De ahí salen las dos preguntas. La primera es de alcance y de ella depende todo lo "
             "demás: si el interés es entender esta línea, eso ya está hecho; si es evaluarla "
             "como candidata, empieza por poner a andar el segmentador sobre nuestras láminas, y "
             "eso no cabe al lado de lo que ya está en marcha. La segunda es lo más barato que "
             "hay sobre la mesa. Y dejo una tercera, más de fondo: cuando le mostraron los "
             "reportes a un patólogo, algo más de un cuarto de las mediciones que el modelo "
             "declara importantes le resultaron no relevantes. Me parece muy honesto publicarlo, "
             "y la pregunta es si ese número es aceptable para el estándar clínico que "
             "manejamos.")

    # =======================================================================
    # EJE 2 — La medición de atención contra las marcas del patólogo
    # =======================================================================
    # El resultado que reordenó el objetivo de mitosis y que decidió hacia dónde apuntó la
    # búsqueda de papers. Nada se re-mide acá: todo sale de `atencion_vs_patologo/`, que
    # cerró el 2-ago. Registro deliberadamente pedagógico: es la parte que hay que poder
    # defender en voz alta ([[hallazgo-necesita-forma-presentable]]).

    # ---- 9. La pregunta, y las dos respuestas posibles ----
    s = content(prs, "La observación del patólogo, convertida en pregunta medible")
    _grupo(s, 0.36, TOP, 9.28, 0.62, fill=TEAL_CARD)
    add_textbox(s, 0.60, TOP, 8.80, 0.62, [
        ("«En mitosis los núcleos son finos y dispersos, y a los modelos se les escapan "
         "porque quizá esos parches no reciben atención suficiente.»",
         12.5, True, ONCO_DARK, F_BODY, PP_ALIGN.CENTER)], anchor=MSO_ANCHOR.MIDDLE)
    fichas = [("1", "lámina anotada"), ("4799", "parches"), ("163", "bajo alguna marca"),
              ("7", "grupos de tejido")]
    fw, fgap = 2.20, 0.16
    fx = (SW - (4 * fw + 3 * fgap)) / 2
    for i, (val, sub) in enumerate(fichas):
        x = fx + i * (fw + fgap)
        _grupo(s, x, TOP + 0.78, fw, 0.62, fill=TEAL_CARD2)
        add_textbox(s, x, TOP + 0.80, fw, 0.34,
                    [(val, 16, True, TEAL_TITLE, F_TITLE, PP_ALIGN.CENTER)])
        add_textbox(s, x, TOP + 1.10, fw, 0.26,
                    [(sub, 9.5, False, GRIS_BODY, F_BODY, PP_ALIGN.CENTER)])
    izq = panel(s, 0.36, TOP + 1.62, 4.54, None,
                "Si tuviera razón", TEAL_TITLE,
                ["Los parches marcados no rankearían mejor que el azar.",
                 "Entonces el problema estaría en CÓMO se combinan los parches, y habría "
                 "que cambiar la manera de agregarlos."],
                TEAL_SQ, tsize=13, bsize=10.5)
    der = panel(s, 5.10, TOP + 1.62, 4.54, None,
                "Si no la tuviera", ONCO_DARK,
                ["Los parches marcados rankearían alto.",
                 "Entonces el modelo sí mira ahí, y lo que se pierde está antes, en cómo "
                 "queda representado el parche."],
                ONCO_DARK, fill=TEAL_CARD, tsize=13, bsize=10.5)
    alto_hip = max(Emu(sp.height).inches for sp in (izq, der))
    for sp in (izq, der):
        sp.height = Inches(alto_hip)
    takeaway_bar(s, "Las dos lecturas quedaron escritas y registradas ANTES de correr "
                    "nada. Ninguna se decidió mirando el número.",
                 t=TOP + 1.62 + alto_hip + 0.22, size=12.5)
    notes(s, "Paso a la segunda parte, que es una medición nuestra.\n"
             "\n"
             "El origen es la frase de arriba. Cuando revisamos con el patólogo por qué los "
             "modelos fallan en tasa mitótica, dijo que en mitosis los núcleos son finos y "
             "dispersos, y que se les escapan porque quizá esos parches no reciben atención "
             "suficiente. Esa frase tiene una virtud enorme: se puede medir. No es una opinión "
             "sobre el modelo, es una afirmación sobre dónde cae la atención, y la atención la "
             "podemos leer.\n"
             "\n"
             "El material es el de la fila del medio. Una lámina, la única que tenemos anotada, "
             "con cuatro mil setecientos noventa y nueve parches, de los cuales ciento sesenta y "
             "tres quedan debajo de alguna marca, repartidas en siete grupos de tejido. Es poco "
             "y lo digo de entrada: una lámina y un anotador describen, no establecen.\n"
             "\n"
             "Los dos paneles de abajo son las dos respuestas posibles, y quiero subrayar que se "
             "escribieron antes de correr nada. Si el patólogo tuviera razón, los parches "
             "marcados no rankearían mejor que el azar, y eso apuntaría a que el problema está "
             "en cómo el modelo combina los parches; habría que cambiar la manera de agregarlos. "
             "Si no la tuviera, los parches marcados rankearían alto, y entonces el modelo sí "
             "mira donde hay que mirar, y lo que se pierde está antes, en cómo queda "
             "representado cada parche.\n"
             "\n"
             "Insisto en esto porque es lo que hace que el resultado valga: las dos lecturas, y "
             "también la mixta, quedaron escritas y guardadas antes de ver un solo número. "
             "Ninguna se acomodó después.")

    # ---- 10. Cómo se mide: es un ranking, no un mapa de calor ----
    s = content(prs, "Qué se mide exactamente: un ranking, no un mapa")
    add_textbox(s, 0.36, TOP, 9.28, 0.40, [
        ("Se ordenan los 4799 parches de la lámina por la atención que recibieron, de más a "
         "menos, y se mira dónde caen los marcados.", 12.5, True, GRIS_BODY, F_BODY,
         PP_ALIGN.CENTER)], anchor=MSO_ANCHOR.MIDDLE)
    _rot_label(s, -0.42, TOP + 0.72, 1.60, 0.32, "SI FUERA AZAR", col=GRIS_BODY)
    cinta_ranking(s, 0.94, TOP + 0.62, 7.30, marcados={2, 7, 11, 16, 21, 27, 31})
    add_textbox(s, 8.46, TOP + 0.62, 1.20, 0.40,
                [("0,5", 15, True, GRIS_BODY, F_BODY, PP_ALIGN.CENTER)],
                anchor=MSO_ANCHOR.MIDDLE)
    _rot_label(s, -0.42, TOP + 1.90, 1.60, 0.32, "LO OBSERVADO", col=ONCO_DARK)
    cinta_ranking(s, 0.94, TOP + 1.80, 7.30, marcados={0, 1, 2, 4, 5, 7, 9})
    add_textbox(s, 8.46, TOP + 1.80, 1.20, 0.40,
                [("0,89", 15, True, ONCO_DARK, F_BODY, PP_ALIGN.CENTER)],
                anchor=MSO_ANCHOR.MIDDLE)
    panel(s, 0.36, TOP + 2.86, 9.28, None, "El número que sale de ahí", TEAL_TITLE,
          ["Es la probabilidad de que un parche marcado reciba MÁS atención que un parche "
           "sin marca tomado al azar. Va de 0 a 1 y el azar está en 0,5.",
           "No depende de la escala de la atención, así que se puede comparar entre "
           "modelos y entre grupos de tejido. Es lo que un mapa de calor no permite hacer."],
          TEAL_SQ, tsize=13, bsize=10.5)
    notes(s, "Acá está el punto que quiero que quede, porque es el que se pierde cuando uno "
             "cuenta esto rápido. Lo que medimos no es un mapa de calor. Los mapas los "
             "generamos, y los vamos a ver en un momento, pero son el subproducto. El resultado "
             "es un número, y el número sale de un ranking.\n"
             "\n"
             "El procedimiento es el de arriba. Se toman los cuatro mil setecientos noventa y "
             "nueve parches de la lámina y se ordenan por la atención que recibieron, de más a "
             "menos. Queda una fila larguísima. Y entonces uno pregunta dónde cayeron los "
             "parches que el patólogo marcó.\n"
             "\n"
             "Las dos cintas son los dos extremos. Si la atención no supiera nada de mitosis, "
             "los marcados estarían repartidos por toda la fila, tantos al principio como al "
             "final, y el número da cero coma cinco. Si la atención se concentrara justo ahí, "
             "los marcados se amontonarían a la izquierda, y el número se acerca a uno.\n"
             "\n"
             "Ese número tiene una lectura directa: es la probabilidad de que, si tomo un parche "
             "marcado y un parche sin marca al azar, el marcado tenga más atención. Y tiene dos "
             "propiedades que lo hacen preferible al mapa. No depende de la escala de la "
             "atención, así que se puede comparar entre modelos distintos y entre tejidos "
             "distintos. Y da un valor de comparación, el cero coma cinco, que un mapa de calor "
             "no da: mirando un mapa uno no sabe decir si el rojo está donde corresponde o si "
             "está en todas partes.")

    # ---- 11. Los mapas: dónde mira y dónde marcó ----
    # Las dos figuras son producción NUESTRA, no figura de paper, así que van como imagen
    # con todo derecho. La leyenda de las dos regiones es OBLIGATORIA: sin ella la figura
    # se lee como un error (hallazgo F4 de la sexta pasada de la auditoría).
    s = content(prs, "Los dos mapas, sobre la misma lámina")
    # La caja se dimensiona con la relación de aspecto EXACTA de la figura (1.183), para que
    # add_image_fit no la centre dejando aire a los costados: si lo hiciera, los rótulos de
    # columna quedarían corridos respecto de los paneles que rotulan.
    MAP_L, MAP_W = 0.42, 4.40
    MAP_H = MAP_W / 1.1827
    add_image_fit(s, FIG_MAPAS, MAP_L, TOP + 0.34, MAP_W, MAP_H, align="top")
    col_w = (MAP_W - 0.064) / 2          # el gap de 22 px del montaje, en pulgadas
    for i, rot in enumerate(("Atención del modelo", "Marcas del patólogo")):
        cx = MAP_L + i * (col_w + 0.064) + col_w / 2
        caption(s, cx - 1.20, TOP + 0.02, 2.40, rot, size=11, col=TEAL_TITLE, bold=True)
    panel(s, 5.08, TOP + 0.30, 4.56, None, "Por qué el tejido aparece dos veces",
          ONCO_DARK,
          ["La lámina se escaneó en DOS regiones, y el pipeline extrajo parches de las "
           "dos: 2303 arriba y 2496 abajo.",
           "Las 163 marcas caen TODAS en la de abajo.",
           "Se midió si esa región recibe de por sí más atención, que arruinaría la "
           "comparación: da 0,462 a 0,478, o sea que recibe algo MENOS.",
           "Y al repetir todo confinado a esa región el efecto sube, de 0,890 a 0,903."],
          ONCO_DARK, fill=TEAL_CARD, tsize=12.5, bsize=9.5)
    notes(s, "Estos son los mapas, que es lo que uno recuerda de un trabajo así, y por eso "
             "quiero mostrarlos después del número y no antes.\n"
             "\n"
             "A la izquierda está la atención del modelo sobre la lámina: el rojo es mucha "
             "atención, el azul poca. A la derecha, las marcas del patólogo, cada color un tipo "
             "de tejido. Mirándolos de a dos uno ya intuye que las marcas caen en zonas "
             "calientes, pero intuir no es medir, y es exactamente por eso que el resultado es "
             "el número de la lámina anterior y no esta imagen.\n"
             "\n"
             "Hay algo en la figura que hay que explicar antes de que distraiga: el tejido "
             "aparece dos veces. No es un error ni una duplicación de la imagen. La lámina se "
             "escaneó en dos regiones separadas, el archivo las guarda una debajo de la otra, y "
             "nuestro pipeline extrajo parches de las dos: dos mil trescientos tres arriba y dos "
             "mil cuatrocientos noventa y seis abajo. Las ciento sesenta y tres marcas caen "
             "todas en la de abajo.\n"
             "\n"
             "Eso abre un problema serio, y fuimos a cerrarlo. Si la región de abajo recibiera "
             "de por sí más atención que la de arriba, el número no estaría midiendo las marcas, "
             "estaría midiendo la región. Lo medimos: la región anotada contra la otra da entre "
             "cero coma cuatro seis y cero coma cuarenta y ocho, o sea que recibe algo menos de "
             "atención, no más. Y después repetimos todo confinando la medición a esa sola "
             "región, con lo cual la pregunta de la región deja de existir: el efecto no baja, "
             "sube, de cero coma ochenta y nueve a cero coma noventa.")

    # ---- 12. El resultado: la escalera de los siete grupos ----
    s = content(prs, "El resultado: mitosis es el grupo mejor rankeado de los siete")
    barras_ranking(s, 0.36, TOP + 0.52, 9.28, 2.62, ESCALERA)
    _grupo(s, 0.36, TOP + 3.34, 4.54, 0.72, fill=TEAL_CARD)
    add_textbox(s, 0.36, TOP + 3.34, 4.54, 0.72, [
        ("Mitosis: 0,890 ± 0,039", 17, True, ONCO_DARK, F_BODY, PP_ALIGN.CENTER),
        ("media sobre 4 checkpoints que NUNCA vieron esta lámina", 9.5, False, GRIS_BODY,
         F_BODY, PP_ALIGN.CENTER)], anchor=MSO_ANCHOR.MIDDLE)
    _grupo(s, 5.10, TOP + 3.34, 4.54, 0.72, fill=TEAL_CARD2)
    add_textbox(s, 5.10, TOP + 3.34, 4.54, 0.72, [
        ("Percentil mediano: 91 de 100", 17, True, TEAL_TITLE, F_BODY, PP_ALIGN.CENTER),
        ("el parche de mitosis típico está en el 9 % más atendido", 9.5, False, GRIS_BODY,
         F_BODY, PP_ALIGN.CENTER)], anchor=MSO_ANCHOR.MIDDLE)
    notes(s, "Este es el resultado, y conviene leerlo entero antes de quedarse con el primer "
             "renglón.\n"
             "\n"
             "Mitosis da cero coma ochocientos noventa, con una dispersión de cero coma cero "
             "treinta y nueve entre los cuatro modelos que nunca vieron esta lámina. Está muy "
             "lejos de la línea punteada del azar. Dicho de la otra forma, que es la que se "
             "entiende sola: el parche de mitosis típico está entre el nueve por ciento más "
             "atendido de la lámina.\n"
             "\n"
             "Pero lo que convence no es ese número solo, es la escalera completa, porque "
             "muestra que la atención tiene estructura y que la estructura tiene sentido "
             "clínico. Abajo de todo está el tejido adiposo, en cero coma quince, o sea que el "
             "modelo lo evita activamente. Después los linfocitos, también por debajo del azar. "
             "El estroma queda justo en el azar, que es donde uno esperaría algo que no es "
             "informativo ni estorba. Y arriba, tumor y núcleos de alto grado alrededor de cero "
             "coma ochenta y tres, con mitosis por encima de los dos.\n"
             "\n"
             "Ese orden no lo diseñó nadie: salió de medir. Y que mitosis quede por encima de "
             "tumor es más de lo que esperábamos, porque tumor son regiones grandes y bien "
             "delimitadas, mucho más fáciles de acertar que veintiocho parches sueltos.\n"
             "\n"
             "Dos advertencias sobre esta lámina. Los grupos de abajo no son un control "
             "negativo: son regiones marcadas con otro criterio, y que la grasa dé cero coma "
             "quince muestra que la atención distingue tejido, no que el método esté validado. Y "
             "los núcleos de alto grado, el segundo renglón, no aguantan el estirón: dan un "
             "número parecido, pero cuando lo sometemos a las pruebas que vienen ahora, solo uno "
             "de cuatro modelos lo pasa. Ese no lo presento como resultado.")

    # ---- 13. Dónde caen los 28 parches ----
    s = content(prs, "Los 28 parches de mitosis, sobre el mapa de atención")
    # Mismo criterio que la lámina anterior: cada caja con la relación de aspecto exacta de
    # su figura, y las dos a la MISMA altura, para que los pies queden en una sola línea.
    FIG_H = 3.34
    reg_w = FIG_H * (800 / 676.0)
    zoom_w = FIG_H * (453 / 552.0)
    add_image_fit(s, FIG_MITOSIS, 0.36, TOP + 0.06, reg_w, FIG_H, align="top")
    add_image_fit(s, FIG_ZOOM, 0.36 + reg_w + 0.15, TOP + 0.06, zoom_w, FIG_H, align="top")
    caption(s, 0.36, TOP + 3.44, reg_w,
            "la región anotada, con los parches de mitosis en blanco", size=9.5)
    caption(s, 0.36 + reg_w + 0.15, TOP + 3.44, zoom_w, "el detalle del recuadro", size=9.5)
    panel(s, 0.36 + reg_w + zoom_w + 0.46, TOP + 0.50, 2.26, None, "Lo que se ve", ONCO_DARK,
          ["Los parches blancos caen sobre el rojo, que es donde el modelo puso su "
           "atención.",
           "No sobre el borde, ni sobre el azul, ni repartidos por la lámina."],
          ONCO_DARK, fill=TEAL_CARD, tsize=12.5, bsize=10)
    takeaway_bar(s, "Y aun así, este modelo predice mal esta lámina.", t=TOP + 3.76,
                 size=13)
    notes(s, "Esta es la misma información de la escalera, pero puesta donde se ve de un "
             "vistazo, y es la imagen que a mí me terminó de convencer.\n"
             "\n"
             "A la izquierda está la región anotada con el mapa de atención debajo, y los "
             "veintiocho parches de mitosis pintados de blanco encima. A la derecha, el detalle "
             "del recuadro rojo, que es donde se concentran.\n"
             "\n"
             "Miren dónde caen los blancos. No están en el borde del tejido, ni sobre las zonas "
             "azules, ni repartidos por la lámina: están sobre el corazón rojo de la mancha, que "
             "es exactamente donde el modelo concentró su atención. Un parche de mitosis y el "
             "pico de atención del modelo son, en esta lámina, el mismo lugar.\n"
             "\n"
             "Y ahora la parte incómoda, que es la que sigue. Este modelo, el que produjo este "
             "mapa, se equivoca al clasificar esta lámina.")

    # ---- 14. Mira bien y responde mal ----
    s = content(prs, "El hallazgo: mira bien y responde mal")
    add_textbox(s, 0.36, TOP, 9.28, 0.36, [
        ("La lámina es score_3, tasa mitótica alta, coherente con las 26 mitosis marcadas.",
         12.5, True, GRIS_BODY, F_BODY, PP_ALIGN.CENTER)], anchor=MSO_ANCHOR.MIDDLE)
    simple_table(s, 0.86, TOP + 0.44, 8.28,
                 ["Modelo", "Qué respondió", "Confianza en score_2", "AUC de atención"],
                 [["privado", "score_2   ✗", "0,645", "0,840"],
                  ["privado + TCGA", "score_3   ✓", "0,224", "0,878"],
                  ["5 folds, fold 0", "score_2   ✗", "0,712", "0,926"],
                  ["5 folds, fold 2", "score_2   ✗", "0,524", "0,917"]],
                 col_fracs=[0.26, 0.24, 0.26, 0.24], row_h=0.36, fs=11, destacar=2)
    panel(s, 0.36, TOP + 2.42, 4.54, None, "La disociación", ONCO_DARK,
          ["3 de 4 subestiman la tasa mitótica.",
           "El que MEJOR mira, con 0,926, es el que MÁS se equivoca.",
           "Los 8 modelos que sí vieron esta lámina la aciertan con confianza."],
          ONCO_DARK, fill=TEAL_CARD, tsize=13, bsize=10)
    panel(s, 5.10, TOP + 2.42, 4.54, None, "Qué significa", TEAL_TITLE,
          ["El problema NO está en elegir los parches: eso el modelo lo hace bien.",
           "Está en lo que queda del parche una vez comprimido, y en cómo esos parches se "
           "convierten en un puntaje."],
          TEAL_SQ, tsize=13, bsize=10)
    takeaway_bar(s, "Ese desacople entre mirar bien y responder mal es el resultado, y es "
                    "lo que reordenó el trabajo que sigue.", t=TOP + 3.72, size=12.5)
    notes(s, "Y acá está el desenlace, que no esperábamos y que es lo que hace que esta "
             "medición valga más que la respuesta a la pregunta original.\n"
             "\n"
             "La lámina tiene tasa mitótica alta, que es coherente con las veintiséis mitosis "
             "que el patólogo marcó. Tres de los cuatro modelos que nunca la vieron responden "
             "que tiene tasa intermedia. O sea que se equivocan, y se equivocan hacia abajo: "
             "subestiman.\n"
             "\n"
             "Lo llamativo es la fila destacada. Ese modelo es el que mejor mira de los cuatro, "
             "con cero coma noventa y tres de atención sobre las mitosis, y es también el que "
             "responde con más convicción la respuesta equivocada, con un setenta y uno por "
             "ciento de confianza. Mirar mejor no lo ayudó a responder mejor. Los ocho modelos "
             "que sí tenían esta lámina en su entrenamiento la aciertan cómodamente, lo cual "
             "confirma que el problema no es que la lámina sea rara.\n"
             "\n"
             "La conclusión es la del panel derecho, y es un cambio de diagnóstico. Veníamos "
             "pensando que el modelo fallaba porque no encontraba las mitosis. No es eso: las "
             "encuentra. Lo que falla está en otro lado, en lo que queda del parche una vez que "
             "se lo comprime a un vector, y en cómo un conjunto de parches bien elegidos se "
             "convierte en un puntaje. Eso mueve el trabajo a un lugar distinto del que "
             "teníamos previsto.")

    # ---- 15. Por qué no es una casualidad ----
    s = content(prs, "Por qué esto no es una casualidad")
    controles = [
        ("1. El nulo espacial", TEAL_CARD, TEAL_SQ,
         ["Permutar al azar qué parches están marcados es DEMASIADO fácil de pasar: da "
          "significativo hasta donde no debería.",
          "El nulo honesto TRASLADA la mancha de marcas entera por la lámina, "
          "conservando su forma. De ~440 posiciones válidas, NINGUNA llega al valor "
          "observado."]),
        ("2. El efecto de región", TEAL_CARD2, ONCO_DARK,
         ["Descartado: la región anotada recibe algo MENOS de atención que la otra "
          "(0,462 a 0,478).",
          "Confinando la medición a esa región, el efecto sube a 0,903."]),
        ("3. La memorización", TEAL_CARD2, ONCO_DARK,
         ["Los 4 modelos primarios nunca vieron la lámina.",
          "Haberla visto suma solo 0,056 de AUC (0,890 contra 0,946)."]),
        ("4. El sesgo de la anotación", TEAL_CARD2, ONCO_DARK,
         ["El patólogo marca donde la evidencia es clara, no todo: las mitosis no "
          "marcadas quedan del lado 'sin marca' y ACERCAN el número a 0,5.",
          "O sea que el sesgo juega en contra, y un 0,890 es creíble por eso."]),
    ]
    bw = (9.28 - 3 * 0.14) / 4
    # Los cuatro paneles se auto-dimensionan por su texto, así que salen de altos distintos
    # y la tira queda dentada. Se igualan al más alto DESPUÉS de dibujarlos: el texto está
    # anclado arriba, así que alargar la caja no mueve nada de lo escrito.
    cajas = [panel(s, 0.36 + i * (bw + 0.14), TOP, bw, None, tit,
                   TEAL_TITLE if fill is TEAL_CARD else ONCO_DARK, lineas, borde,
                   fill=fill, tsize=11.5, bsize=9)
             for i, (tit, fill, borde, lineas) in enumerate(controles)]
    alto_max = max(Emu(sp.height).inches for sp in cajas)
    for sp in cajas:
        sp.height = Inches(alto_max)
    panel(s, 0.36, TOP + alto_max + 0.20, 9.28, None, "Lo que este resultado NO dice",
          GRIS_BODY,
          ["Una lámina y un anotador DESCRIBEN, no establecen. Está pre-registrado así.",
           "No dice que la atención esté bien en general, ni valida los nombres de tejido "
           "que le pusimos a las unidades internas en el trabajo anterior. Y un parche sin "
           "marca con atención alta no es un error del modelo: puede ser tejido que el "
           "patólogo no marcó."],
          ONCO_DATA, fill=TEAL_CARD2, tsize=12.5, bsize=10)
    notes(s, "Antes de sacar conclusiones quiero mostrar las cuatro cosas que fuimos a "
             "descartar, porque un número alto sin esto no vale gran cosa.\n"
             "\n"
             "La primera es la más importante y es una lección que me llevo. La manera obvia de "
             "poner a prueba un resultado así es barajar al azar qué parches están marcados y "
             "ver cuántas veces sale un valor tan alto por casualidad. Eso lo hicimos y da "
             "significativo, pero también da significativo donde no debería, así que no sirve "
             "para nada. El motivo es que los parches marcados están pegados unos a otros, y la "
             "atención también viene en manchas: cualquier mancha compacta le gana a un sorteo "
             "que rompe la contigüidad. La prueba honesta es otra: agarrar la mancha de marcas "
             "entera, con su forma y su tamaño, y deslizarla por la lámina a otras posiciones "
             "válidas. De unas cuatrocientas cuarenta posiciones posibles, ninguna alcanzó el "
             "valor que observamos en su lugar real.\n"
             "\n"
             "La segunda es la de las dos regiones, que ya conté.\n"
             "\n"
             "La tercera es memorización. Los cuatro modelos principales nunca vieron esta "
             "lámina, pero podemos medir cuánto ayudaría haberla visto, porque hay otros que sí "
             "la tenían: la diferencia es de cero coma cero cinco seis, chica al lado de la "
             "distancia que hay hasta el azar.\n"
             "\n"
             "Y la cuarta juega a nuestro favor sin que hiciéramos nada. El patólogo marca donde "
             "la evidencia es clara, no marca todas las mitosis de la lámina; las que no marcó "
             "quedan contadas como si no tuvieran nada, y eso empuja el número hacia el azar. El "
             "cero coma ochenta y nueve es creíble justamente porque el sesgo lo empuja para "
             "abajo.\n"
             "\n"
             "Abajo dejo lo que el resultado no dice, porque también estaba pre-registrado. Una "
             "lámina y un anotador describen, no establecen. No estamos diciendo que la atención "
             "de nuestros modelos esté bien en general, ni damos por buenos los nombres de "
             "tejido que le pusimos a las unidades internas la vez pasada, que siguen esperando "
             "el visto bueno de un patólogo.")

    # ---- 16. Qué mueve esto ----
    s = content(prs, "Qué mueve esto en lo que viene")
    familias = [
        ("A", "Cambiar cómo se agregan los parches", ONCO_DATA,
         "pierde su motivación principal", False),
        ("B", "Campo de visión: la escala física", ONCO_DARK,
         "se fortalece", True),
        ("C", "Unidad de representación: del parche al núcleo", ONCO_DARK,
         "se fortalece", True),
        ("D", "Usar las marcas como supervisión parcial", ONCO_CONN,
         "abierta, depende de cuántas láminas anotadas haya", True),
    ]
    yy = TOP + 0.10
    for cod, texto, col, estado, vivo in familias:
        _proc(s, 0.36, yy, 0.62, 0.62, cod, size=15, col=col)
        add_textbox(s, 1.16, yy, 4.60, 0.62, [(texto, 12.5, True, INK, F_BODY)],
                    anchor=MSO_ANCHOR.MIDDLE)
        add_textbox(s, 5.90, yy, 3.74, 0.62,
                    [(estado, 11, vivo, ONCO_DARK if vivo else GRIS_BODY, F_BODY)],
                    anchor=MSO_ANCHOR.MIDDLE)
        yy += 0.74
    panel(s, 0.36, TOP + 3.12, 4.54, None, "Por qué A no se cae del todo", GRIS_BODY,
          ["Su primer argumento era la frase del patólogo, y quedó refutado.",
           "Le queda el segundo, intacto: contar mitosis es un MÁXIMO local sobre parches "
           "vecinos, no un promedio ponderado."],
          ONCO_DATA, fill=TEAL_CARD2, tsize=12.5, bsize=10)
    panel(s, 5.10, TOP + 3.12, 4.54, None, "Y por eso los papers que traje", ONCO_DARK,
          ["La búsqueda apuntó a B, C y D, no a A.",
           "Es la parte que sigue en la agenda de hoy."],
          ONCO_DARK, fill=TEAL_CARD, tsize=12.5, bsize=10)
    notes(s, "Cierro con lo que esto cambia, que es la razón por la que le dediqué tanto "
             "tiempo.\n"
             "\n"
             "Teníamos cuatro maneras posibles de atacar el problema de mitosis, y estaban "
             "escritas antes de esta medición. La primera era cambiar la forma en que el modelo "
             "combina los parches. La segunda, el campo de visión, porque la mitosis se cuenta a "
             "cuarenta aumentos y buena parte de nuestra cohorte está a veinte. La tercera, "
             "cambiar la unidad con la que representamos el tejido, pasando del parche al "
             "núcleo. Y la cuarta, aprovechar las marcas del patólogo como supervisión, aunque "
             "sean parciales.\n"
             "\n"
             "La medición reordenó eso. La primera pierde su motivación principal, porque su "
             "argumento de cabecera era precisamente la frase del patólogo, y la frase quedó "
             "refutada. Y quiero ser cuidadoso acá: pierde ese argumento, no todos. Le queda uno "
             "intacto, que esta medición no evalúa: contar mitosis en el criterio clínico es "
             "buscar el máximo en un puñado de campos vecinos, no promediar toda la lámina, y "
             "eso sigue siendo una diferencia real de operador.\n"
             "\n"
             "La segunda y la tercera se fortalecen, y se fortalecen por lo mismo: si el modelo "
             "mira el parche correcto y aun así subestima, lo que falla es cómo está "
             "representado ese parche. La cuarta queda abierta, y depende de una pregunta muy "
             "concreta que traigo para hoy, que es cuántas láminas anotadas hay realmente y "
             "quién las anotó.\n"
             "\n"
             "Y esto explica por qué los papers que revisé apuntan a las tres últimas y no a la "
             "primera. Esa es la parte que sigue.")

    # ---- cierre: reflow, auditoría, escala al tamaño del template, tipografía ----
    reflow_onco(prs, skip=keep_ids)
    auditar(prs, skip=keep_ids)
    scale_deck_to_1610(prs, skip=keep_ids)
    forzar_barlow(prs)
    os.makedirs(OUT_DIR, exist_ok=True)
    prs.save(DST)
    print("Guardado:", DST, "·", len(prs.slides), "slides · 13.333x7.5")
    # El deck dejó de ser monográfico de SI-MIL, así que el archivo con el nombre viejo
    # quedaría al lado del nuevo, desactualizado y sin dueño. Se retira acá y no a mano,
    # para que regenerar desde cero no lo resucite.
    if os.path.exists(DST_LEGACY):
        os.remove(DST_LEGACY)
        print("Retirado el nombre previo:", os.path.basename(DST_LEGACY))


if __name__ == "__main__":
    build()
