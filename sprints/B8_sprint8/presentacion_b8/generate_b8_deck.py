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

Sección de cierre (4-ago): el grid E×S (`../grid_expertos_slots/resultados.md`, encargo 3 del
B8) entra DESPUÉS de los dos ejes y NO como tercer eje, por decisión de Ernesto. Cero Δ contra
CLAM por brazo, que es lo que el pre-registro §6 prohibió por diseño, y el veredicto es H_nula
y se cuenta como tal.

REDISEÑO del 4-ago (doce puntos pedidos por Ernesto tras revisar el deck armado). Sigue en 20
láminas, con la estructura cambiada en las dos puntas y el cuerpo aligerado:
  - Abre con OBJETIVOS DEL SPRINT (molde de recapitulación del B7) en vez del mapa del
    recorrido. El objetivo 1, el escalado de slots, es el único sin lámina: se cuenta en el
    guion, y de paso deja dicho uno de los mensajes que hay que llevar a la reunión.
  - Cierra con los TRES PAPERS de la rama de mitosis (heredan el lugar de la lámina de las
    cuatro familias, cuyo reordenamiento pasó al guion; sin las letras A/B/C/D) y una lámina
    nueva de OBJETIVOS PROPUESTOS. La lámina del determinismo se retiró: lo que quedaba en
    pie de ella es una línea de comparabilidad en el guion del grid.
  - Dos láminas se volvieron figura donde antes había un panel de texto: el estadístico
    (`escala_auc`) y, sobre todo, el nulo por traslación (`_mancha` + `nube_traslaciones`),
    que era la lámina que Ernesto dijo no entender. La de los mapas pasa a la región anotada
    sola, al doble de lado, con la procedencia al pie (`pie_lineas`).
  - Transversales: títulos minimalistas, y cada guion abre con un punteo de 3 a 5 renglones
    de una línea antes de la prosa hablada, que sigue siendo prosa
    ([[notas-presentador-guion-didactico]]).
  - Corrección que atraviesa el deck: los checkpoints primarios NO vieron la lámina anotada
    «en entrenamiento» (está en validación), que es lo que sostienen el prereg y el
    resultados. La formulación anterior, «nunca vieron esta lámina», se pasaba de eso.

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
FIG_MAPAS = os.path.join(ASSETS, "atencion_dos_regiones.png")      # grilla 2x2 (ar 1.1827)
# Preparado para el rediseño de la lámina 12: solo la región anotada, atención | marcas, que
# es el doble de lado y no arrastra la fila que se lee como imagen repetida. ar = 2.407, así
# que la caja de la lámina hay que recalcularla al adoptarlo (add_image_fit usa `h = w / ar`).
FIG_MAPAS_ANOTADA = os.path.join(ASSETS, "atencion_region_anotada.png")
FIG_MITOSIS = os.path.join(ASSETS, "mitosis_region_anotada.png")   # con el recuadro de foco
FIG_ZOOM = os.path.join(ASSETS, "mitosis_zoom.png")                # el detalle del recuadro

# --- procedencia de la lámina anotada, para la lámina de los mapas ---
# Sebastián preguntó de dónde salió la lámina y con qué checkpoints se midió. Las tres líneas
# de abajo son la respuesta, verificadas el 4-ago contra los CSV de labels de `environ/`, el
# `offset_129741.json` de `anotaciones_patologo/` y los `splits_*_bool.csv` de cada corrida.
PROVENANCIA = [
    "Lámina 129741, cohorte privada. H&E Ventana .bif a 20× (0,465 µm/px), bajo wsi/129741/. "
    "4799 parches de 256 px, 163 bajo alguna marca.",
    "Marcas del patólogo, 61 polígonos exportados de QuPath: 26 mitosis · 14 núcleos de alto "
    "grado · 6 necrosis · 5 células inmunes · 5 tumor · 2 tejido adiposo · 1 estroma · 2 fondo.",
    "Sus etiquetas en nuestros CSV: tasa mitótica score_3 · pleomorfismo nuclear score_2 · "
    "diferenciación tubular score_3 · grado general 3 · grado nuclear del CDIS alto.",
]

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

# --- números del grid E×S, verificados contra grid_expertos_slots/resultados.md ---
# Contraste primario del pre-registro §6: (brazo que recorta S) menos (brazo que recorta E),
# pareado por fold, dentro de cada peldaño de igual capacidad total E·S. Signo positivo =
# a favor de recortar slots. Los signos por fold salen de la tabla del §4.
PELDANOS = [
    ("E·S = 270", "30×9  contra  27×10", +0.022, 0.063, "+-+-+"),
    ("E·S = 210", "30×7  contra  21×10", -0.014, 0.034, "--+-+"),
    ("E·S = 150", "30×5  contra  15×10", -0.002, 0.048, "--++-"),
]
# AUC medio por brazo (§6 del resultados.md). Rótulo, AUC, capacidad total.
RAMA_S = [("30×10", 0.825, "300"), ("30×9", 0.792, "270"), ("30×7", 0.797, "210"),
          ("30×5", 0.802, "150"), ("30×3", 0.786, "90")]
RAMA_E = [("30×10", 0.825, "300"), ("27×10", 0.770, "270"), ("21×10", 0.812, "210"),
          ("15×10", 0.804, "150")]

# --- los tres papers de la rama de mitosis (../tareas_geometricas/hojas_reunion.md, hoja 0) ---
# Se ordenan por el único criterio que descarta rápido: qué supervisión exige cada uno contra
# la que efectivamente tenemos, que son POSITIVOS PARCIALES. Sin las letras de familia, que
# fuera de nuestros documentos no significan nada.
PAPERS = [
    ("Detección con positivos parciales", "Zhao et al., MELBA 2022",
     "Marcas parciales, las nuestras", "Montar un detector nuevo cuesta"),
    ("Segmentación de núcleos", "Hörst et al., MedIA 2024",
     "Ninguna nuestra: pesos públicos", "No tiene clase mitótica"),
    ("Atención multi-escala", "Thandiackal et al., ECCV 2022",
     "Solo la etiqueta de lámina", "En el privado no hay 40× al que acercarse"),
]

# --- objetivos del sprint, de la reunión del 24-jul más la redirección del 31-jul ---
# En infinitivo, sin resultados, con el marcador de estado del molde de recapitulación.
OBJETIVOS = [
    ("1. Escalar a toda la tarea la medición de slots ocupados.", "done"),
    ("2. Entrenar los slots del modelo con nuestro dataset.", "prog"),
    ("3. Medir, a igual capacidad, si conviene recortar expertos o slots.", "done"),
    ("4. Estudiar el paper de MIL auto-interpretable y decidir si se adopta.", "done"),
    ("5. Medir si la atención cae donde el patólogo marcó las mitosis.", "done"),
    ("6. Revisar la literatura para una rama dedicada a mitosis.", "done"),
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
                    [(_num(auc), fs, interes, ONCO_DARK if interes else GRIS_BODY, F_BODY)],
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
# Figuras nativas de la sección del grid E×S
# ============================================================================
def _num(v, dec=3, signo=False):
    """Número con coma decimal y, si se pide, el signo delante (menos tipográfico)."""
    s = ("%+.*f" % (dec, v)) if signo else ("%.*f" % (dec, v))
    return s.replace("-", "−").replace(".", ",")


def barras_divergentes(slide, l, t, w, h, filas, esc=0.10, fs=10.5, destacar=None,
                       izq="gana recortar expertos", der="gana recortar slots"):
    """Δ pareado por peldaño alrededor del cero, con la desviación como bigote.

    Esta figura NO está para leer la magnitud del Δ. Está para que se vea que el bigote cruza
    el cero en los tres peldaños y que la media se cambia de lado entre ellos: eso es lo que
    separa un resultado nulo de un «casi», y es justo lo que una tabla de tres números deja
    sin mostrar. Por eso el cero es una línea con peso, la escala va rotulada y la barra de
    la media se dibuja ENCIMA del bigote, no al lado."""
    lab_w, val_w, chip_w = 2.50, 1.42, 0.96
    x0 = l + lab_w + 0.12
    ancho = w - lab_w - val_w - chip_w - 0.42
    semi = ancho / 2
    xc = x0 + semi
    fila = h / len(filas)

    # la banda del peldaño que se resalta va PRIMERO: si se dibujara después taparía el
    # cero, el bigote y los cuadros de esa misma fila
    if destacar is not None:
        _grupo(slide, l, t + destacar * fila + 0.02, w, fila - 0.04, fill=TEAL_CARD2)
    # los dos lados, que es lo que le da sentido al signo
    add_textbox(slide, xc - 2.70, t - 0.34, 2.58, 0.26,
                [(izq, 9.5, True, GRIS_BODY, F_BODY, PP_ALIGN.RIGHT)], anchor=MSO_ANCHOR.MIDDLE)
    add_textbox(slide, xc + 0.12, t - 0.34, 2.58, 0.26,
                [(der, 9.5, True, ONCO_DARK, F_BODY)], anchor=MSO_ANCHOR.MIDDLE)
    ln = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(xc), Inches(t - 0.04),
                                    Inches(xc), Inches(t + h + 0.04))
    ln.line.color.rgb = ONCO_INK; ln.line.width = Pt(1.5); ln.shadow.inherit = False

    for i, (rot, sub, media, sd, signos) in enumerate(filas):
        cy = t + i * fila + fila / 2
        add_textbox(slide, l, cy - 0.26, lab_w, 0.26,
                    [(rot, fs, True, ONCO_DARK, F_BODY, PP_ALIGN.RIGHT)], anchor=MSO_ANCHOR.MIDDLE)
        add_textbox(slide, l, cy + 0.01, lab_w, 0.24,
                    [(sub, fs - 1.5, False, GRIS_BODY, F_BODY, PP_ALIGN.RIGHT)],
                    anchor=MSO_ANCHOR.MIDDLE)
        # el bigote primero: la barra de la media va encima
        xa, xb = xc + (media - sd) / esc * semi, xc + (media + sd) / esc * semi
        _rect(slide, xa, cy - 0.015, xb - xa, 0.03, ONCO_DATA)
        for x in (xa, xb):
            _rect(slide, x - 0.01, cy - 0.11, 0.02, 0.22, ONCO_DATA)
        # la media, con ancho mínimo para que un Δ de dos milésimas no desaparezca
        dx = media / esc * semi
        ancho_bar = max(abs(dx), 0.03)
        _rect(slide, xc if dx >= 0 else xc - ancho_bar, cy - 0.10, ancho_bar, 0.20, ONCO_DARK)
        add_textbox(slide, l + w - chip_w - val_w - 0.10, cy - 0.14, val_w, 0.28,
                    [("%s ± %s" % (_num(media, 3, True), _num(sd)), fs - 0.5, True, INK,
                      F_BODY, PP_ALIGN.RIGHT)], anchor=MSO_ANCHOR.MIDDLE)
        # un cuadro por fold: relleno = a favor de recortar slots
        cw, gap = 0.16, 0.04
        xs = l + w - chip_w
        for j, sg in enumerate(signos):
            sp = _rect(slide, xs + j * (cw + gap), cy - cw / 2, cw, cw,
                       ONCO_DARK if sg == "+" else TEAL_CARD2)
            sp.line.color.rgb = ONCO_CONN; sp.line.width = Pt(0.75)
    caption(slide, x0 - 0.90, t + h + 0.06, ancho + 1.80,
            "escala: ± %s de AUC   ·   cada cuadro es un fold, relleno = a favor de recortar "
            "slots" % _num(esc, 2), size=9)


def escalera_capacidad(slide, l, t, w, h, puntos, lo=0.75, hi=0.84, nota=None, fs=9.5):
    """Una rama del grid: AUC medio por brazo, con la línea que une los topes de las barras.

    El eje arranca en 0,75 y no en cero, y va rotulado en la lámina: entre el mejor y el peor
    brazo hay 0,055 de AUC, y a escala completa los ocho brazos serían la misma barra. Lo que
    la figura tiene que dejar ver es la FORMA (un escalón y después una meseta en una rama,
    una curva que ni siquiera es monótona en la otra), no la altura de cada barra."""
    paso = w / len(puntos)
    ancho_barra = min(0.58, paso * 0.50)
    base = t + h
    topes = []
    for i, (rot, auc, cap) in enumerate(puntos):
        cx = l + paso * (i + 0.5)
        alto = max(0.06, (auc - lo) / (hi - lo) * h)
        _rect(slide, cx - ancho_barra / 2, base - alto, ancho_barra, alto,
              ONCO_PANEL if i == 0 else ONCO_DARK)
        # el valor va DENTRO de la barra, no encima: la línea de tendencia llega al tope de
        # cada barra desde el tope del vecino, así que a los costados del rótulo pasa mucho
        # más arriba y lo cruza. Adentro no hay nada que la línea pueda tapar.
        add_textbox(slide, cx - 0.52, base - alto + 0.05, 1.04, 0.24,
                    [(_num(auc), fs, True, ONCO_DARK if i == 0 else WHITE, F_BODY,
                      PP_ALIGN.CENTER)], anchor=MSO_ANCHOR.MIDDLE)
        add_textbox(slide, cx - 0.52, base + 0.04, 1.04, 0.24,
                    [(rot, fs, True, INK if i else GRIS_BODY, F_BODY, PP_ALIGN.CENTER)])
        add_textbox(slide, cx - 0.52, base + 0.25, 1.04, 0.22,
                    [(cap, fs - 1.0, False, GRIS_BODY, F_BODY, PP_ALIGN.CENTER)])
        topes.append((cx, base - alto))
    for (x0, y0), (x1, y1) in zip(topes, topes[1:]):
        ln = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x0), Inches(y0),
                                        Inches(x1), Inches(y1))
        ln.line.color.rgb = ONCO_INK; ln.line.width = Pt(1.25); ln.shadow.inherit = False
    if nota:
        i, texto = nota
        cx = l + paso * (i + 0.5)
        add_textbox(slide, cx - 1.10, base + 0.48, 2.20, 0.24,
                    [(texto, fs - 1.0, True, ONCO_DARK, F_BODY, PP_ALIGN.CENTER)])


# ============================================================================
# Figuras y pies del rediseño del 4-ago
# ============================================================================
def pie_lineas(slide, l, t, w, lineas, size=8, col=GRIS_BODY, space_after=1.5):
    """Pie de varias líneas en UN solo textbox, con el interlineado al mínimo.

    `caption` gasta 0,4" por renglón y con tres renglones se come el alto que necesita la
    figura de arriba. Acá el bloque mide exactamente lo que mide su texto, y devuelve ese
    alto para que quien lo llama pueda cerrar la lámina debajo."""
    h = _alto_bloque(lineas, w - 0.22, size, space_after=space_after)
    tb = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    _set_runs(tb.text_frame, [(ln, size, False, col, F_BODY) for ln in lineas])
    for p in tb.text_frame.paragraphs:
        p.space_after = Pt(space_after)
    return h


def escala_auc(slide, l, t, w, valor, alto=0.16, fs=9.5, pie=None):
    """El estadístico puesto sobre su recorrido de 0 a 1, con el azar marcado.

    Un número suelto dentro de un renglón de texto no dice dónde cae. Sobre la escala, la
    distancia hasta el azar se lee sin que nadie la explique, que es de lo que se trata
    volver visual un panel de texto ([[deck-contenido-visual-no-bullets]])."""
    yb = t + 0.26
    _rect(slide, l, yb, w, alto, ONCO_PANEL)
    x_az = l + w * 0.5
    ln = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x_az), Inches(yb - 0.07),
                                    Inches(x_az), Inches(yb + alto + 0.07))
    ln.line.color.rgb = ONCO_INK; ln.line.width = Pt(1.25); ln.shadow.inherit = False
    lnpr = ln.line._get_or_add_ln()
    lnpr.append(lnpr.makeelement(qn('a:prstDash'), {'val': 'dash'}))
    x_v = l + w * valor
    _rect(slide, x_v - 0.035, yb - 0.08, 0.07, alto + 0.16, ONCO_DARK)
    add_textbox(slide, x_v - 0.80, t - 0.03, 1.60, 0.28,
                [(_num(valor), 16, True, ONCO_DARK, F_BODY, PP_ALIGN.CENTER)],
                anchor=MSO_ANCHOR.MIDDLE)
    ye = yb + alto + 0.05
    add_textbox(slide, l - 0.24, ye, 0.48, 0.22,
                [("0", fs, False, GRIS_BODY, F_BODY, PP_ALIGN.CENTER)])
    add_textbox(slide, x_az - 0.80, ye, 1.60, 0.22,
                [("azar = 0,5", fs, True, ONCO_INK, F_BODY, PP_ALIGN.CENTER)])
    add_textbox(slide, l + w - 0.24, ye, 0.48, 0.22,
                [("1", fs, False, GRIS_BODY, F_BODY, PP_ALIGN.CENTER)])
    if pie:
        add_textbox(slide, l, ye + 0.26, w, 0.24,
                    [(pie, 11, False, INK, F_BODY, PP_ALIGN.CENTER)])
    return ye + (0.50 if pie else 0.22) - t


# El racimo es SIEMPRE el mismo: que la forma se conserve es justamente lo que define al
# nulo por traslación, así que una sola función dibuja la mancha real y sus copias, y lo
# único que cambia entre ellas es de dónde arrancan.
_RACIMO = [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1), (3, 1),
           (1, 2), (2, 2), (3, 2), (2, 3)]


def _mancha(slide, x, y, c=0.052, solida=True, col=None):
    """El racimo de parches marcados, sólido si es el real y hueco si es una traslación."""
    for dx, dy in _RACIMO:
        sp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x + dx * c), Inches(y + dy * c),
                                    Inches(c * 0.86), Inches(c * 0.86))
        if solida:
            sp.fill.solid(); sp.fill.fore_color.rgb = col or ONCO_INK
            sp.line.fill.background()
        else:
            # relleno BLANCO, no transparente: sobre el celeste de la zona caliente un
            # contorno sin relleno se lee casi como la mancha sólida, y la diferencia entre
            # las dos cosas es justamente lo que la figura tiene que mostrar.
            sp.fill.solid(); sp.fill.fore_color.rgb = WHITE
            sp.line.color.rgb = col or GRIS_BODY; sp.line.width = Pt(0.75)
        sp.shadow.inherit = False


def _lcg(semilla=7):
    """Generador propio para el jitter de la nube: el dibujo tiene que salir igual en cada
    regenerada, y `random` sin semilla haría que el deck cambie de una corrida a otra."""
    x = semilla
    while True:
        x = (1103515245 * x + 12345) % 2147483648
        yield x / 2147483648.0


def nube_traslaciones(slide, l, t, w, h, lo, hi, banda, obs, fs=9,
                      n_marcas=54, rot_banda=None, rot_obs=None):
    """Dónde caen las traslaciones del nulo contra dónde cayó la mancha en su lugar real.

    `banda` es el RANGO MEDIDO de los AUC nulos, que es el dato que existe: la corrida
    guardó el rango, no los ~440 valores uno por uno. Por eso lo medido se dibuja como
    banda rotulada con sus dos extremos, y las marcas de adentro solo dicen «acá hay
    muchas», sin fingir un histograma que no tenemos."""
    def X(v):
        return l + (v - lo) / (hi - lo) * w
    yb = t + 0.30
    _rect(slide, l, yb, w, h, TEAL_CARD2)
    b0, b1 = X(banda[0]), X(banda[1])
    _rect(slide, b0, yb, b1 - b0, h, ONCO_PANEL)
    g = _lcg()
    for i in range(n_marcas):
        fx, fy = next(g), next(g)
        cx = b0 + fx * (b1 - b0 - 0.05)
        cy = yb + 0.05 + fy * (h - 0.14)
        _rect(slide, cx, cy, 0.045, 0.045, ONCO_DATA)
    _rect(slide, X(obs) - 0.035, yb - 0.10, 0.07, h + 0.20, ONCO_DARK)
    add_textbox(slide, X(obs) - 0.80, yb - 0.34, 1.60, 0.24,
                [(_num(obs), 13, True, ONCO_DARK, F_BODY, PP_ALIGN.CENTER)],
                anchor=MSO_ANCHOR.MIDDLE)
    ye = yb + h + 0.04
    if rot_banda:
        add_textbox(slide, b0 - 0.60, ye, (b1 - b0) + 1.20, 0.22,
                    [(rot_banda, fs, True, GRIS_BODY, F_BODY, PP_ALIGN.CENTER)])
    if rot_obs:
        add_textbox(slide, X(obs) - 1.30, ye, 1.60, 0.22,
                    [(rot_obs, fs, True, ONCO_DARK, F_BODY, PP_ALIGN.RIGHT)])
    return ye + 0.22 - t


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

    # ---- 2. Objetivos del sprint ----
    # Antes acá iba el mapa del recorrido. Pedido de Ernesto (4-ago): la lámina de apertura
    # tiene que fijar QUÉ nos propusimos, no cómo está armado el deck. Molde de
    # recapitulación del B7: título 32 pt, lista numerada en infinitivo, marcador de estado.
    # El objetivo 1 es el único que no tiene lámina propia: se cuenta en el guion, y de paso
    # cubre uno de los tres mensajes que hay que dejar dichos hoy.
    s = content(prs, "Objetivos del sprint", size=32)
    row_tops = [1.10 + i * 0.68 for i in range(len(OBJETIVOS))]
    row_h = 0.62
    for (item, estado), rt in zip(OBJETIVOS, row_tops):
        add_textbox(s, 0.35, rt, 7.75, row_h, [(item, 19, True, GRIS_BODY, F_BODY)],
                    anchor=MSO_ANCHOR.MIDDLE)
        cy = rt + row_h / 2
        if estado == "done":
            status_done(s, 8.98, cy)
        else:
            status_progress(s, 8.98, cy, texto="En curso")
    notes(s, "Seis objetivos, cinco cerrados y uno en curso.\n"
             "El primero se cuenta acá mismo y no tiene lámina.\n"
             "El segundo es el que sigue abierto, y su premisa quiero aclararla hoy.\n"
             "El quinto es el que cambió el plan, y es al que le voy a dedicar más tiempo.\n"
             "\n"
             "Antes de entrar en materia dejo a la vista qué me propuse este sprint, porque son "
             "cosas de naturaleza bastante distinta y conviene tenerlas ordenadas.\n"
             "\n"
             "El primero lo cierro acá mismo, porque el resultado cabe en una frase y no "
             "necesita lámina. Veníamos de medir sobre siete láminas cuántas unidades internas "
             "usa de verdad el modelo con expertos, y había quedado el reparo de que siete "
             "láminas no son la tarea. Lo escalamos a mil ochocientas cincuenta y ocho "
             "láminas por partición, que son todas las de prueba de las tres tareas y las tres "
             "cohortes, y el número aguanta: se ocupan alrededor de ciento sesenta unidades de "
             "las trescientas, y los treinta expertos se usan los treinta, sin una sola "
             "excepción. Lo que sí se cayó con el número grande fue la explicación que "
             "habíamos dado de por qué ese número varía entre láminas: con siete parecía "
             "seguir al tamaño de la lámina, y con el conjunto completo eso casi desaparece.\n"
             "\n"
             "El segundo es el único que sigue abierto, y está abierto porque la premisa no me "
             "quedó clara: entrenar las unidades del modelo con nuestro conjunto de datos "
             "admite más de una lectura, y prefiero preguntarlo antes que elegir una por mi "
             "cuenta.\n"
             "\n"
             "El tercero y el cuarto son la parte de cierre de hoy y el paper que revisé. El "
             "quinto y el sexto son la medición de atención y la búsqueda de literatura que "
             "salió de ella, y ahí es donde está lo que quiero conversar: esa medición cambió "
             "hacia dónde apunta el trabajo que sigue.")

    # =======================================================================
    # EJE 1 — SI-MIL, compactado a la mitad (12 láminas de contenido a 6)
    # =======================================================================
    # Método del recorte, el mismo del 31-jul: se fusionan pares y lo que sale de la
    # lámina se cuenta HABLANDO. El guion de cada fusionada se reescribe, no se pega.

    # ---- 3. Qué propone + la figura del paper ----
    # Fusión de «qué propone, en una frase» con «la arquitectura en la figura». La figura
    # ES el qué propone dibujado, así que separarlas obligaba a repetir la frase. Las tres
    # tarjetas de consecuencias y la fila de cifras del paper pasaron al guion.
    s = content(prs, "SI-MIL: qué propone")
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
    notes(s, "La ambición del paper: que la explicación SEA la predicción.\n"
             "Dos caminos que salen de la misma lámina: uno mide, el otro selecciona.\n"
             "La rama profunda no llega a producción, se descarta entera.\n"
             "\n"
             "Empiezo por el método. El nombre completo habla de domesticar un modelo profundo "
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
    s = content(prs, "Ecuación 1: las dos entradas")
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
    notes(s, "Dos anchos escritos con la misma letra: mayúscula el camino profundo, minúscula "
             "el otro.\n"
             "Mismos parches y mismo orden en los dos; cambia quién eligió los números.\n"
             "La ecuación tiene dos pasos: el proyector y la atención.\n"
             "Lo que hay que retener: la atención es una tajada de un presupuesto, no una "
             "propiedad del parche.\n"
             "\n"
             "Antes de la primera ecuación hay que fijar una convención de notación que el "
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
    s = content(prs, "Ecuación 2: el orden")
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
    notes(s, "La misma cuenta en dos órdenes: fundir y clasificar, o clasificar y sumar.\n"
             "El resultado final es el mismo número; cambia qué queda cuando el modelo "
             "termina.\n"
             "Nuestro modelo es el primero de los dos, así que no hay desglose por parche.\n"
             "Y la atención no lo rescata: dice cuánto mira, nunca hacia qué clase empuja.\n"
             "\n"
             "Esta es la ecuación que cuesta, y cuesta porque parece decir algo obvio. Uno la "
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
    s = content(prs, "El puente entre las dos ramas")
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
    notes(s, "El embudo: de cinco millones de números ilegibles a 4920 que tienen nombre.\n"
             "El único producto del camino profundo son veinte índices.\n"
             "La selección no tiene derivada, y por eso usan una versión perturbada.\n"
             "Los pesos de parche reparten una torta; los de medición no, y eso es lo que "
             "permite acortar el reporte.\n"
             "\n"
             "Este es el movimiento central del diseño, el que hace que las dos ramas dejen de "
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
    s = content(prs, "Ecuaciones 3 a 10")
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
        ("L = L_(CE)(Y, Ŷ_g) + L_(CE)(Y, Ŷ_f) + λ L_(KD)(Ŷ_g, Ŷ_f)", 11, False, ONCO_INK, F_BODY)],
        anchor=MSO_ANCHOR.MIDDLE, markup=True)
    add_textbox(s, 3.86, yy + 0.74, 0.50, 0.42, [("(10)", 9.5, False, GRIS_BODY, F_BODY)],
                anchor=MSO_ANCHOR.MIDDLE)
    add_textbox(s, 4.42, yy + 0.74, 5.10, 0.42, [
        ("las dos ramas se entrenan juntas: la interpretable persigue a la profunda",
         10.5, False, INK, F_BODY)], anchor=MSO_ANCHOR.MIDDLE)
    takeaway_bar(s, "Si hay que quedarse con una sola ecuación, es la 9: ES el reporte que "
                    "ve el patólogo.", t=yy + 1.22, size=12.5)
    notes(s, "Las paso en bloque: desarmadas una por una con el mismo detalle todavía no las "
             "tengo.\n"
             "La cinco es la que fuerza que sobrevivan pocas mediciones.\n"
             "La nueve es la que hay que llevarse: ES el reporte que ve el patólogo.\n"
             "La diez entrena las dos ramas juntas, y sin ella serían dos modelos separados.\n"
             "\n"
             "El resto de las ecuaciones las paso en bloque, porque desarmadas con el mismo "
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

    # ---- 8. Resultados y costo de adopción ----
    # Rediseño del 4-ago: la tabla es el objeto de la lámina, así que se agranda a todo el
    # ancho y se queda sola. Los tres paneles del inventario de costos y las dos tarjetas de
    # preguntas salieron: su contenido ya estaba entero en el guion, y acá competían con la
    # única fila que hay que leer ([[deck-contenido-visual-no-bullets]]).
    s = content(prs, "Resultados y costo de adopción")
    caption(s, 0.36, TOP, 9.28,
            "Su Tabla 2: el mismo método aplicado sobre distintos modelos de base, en "
            "TCGA-BRCA", size=10.5, col=GRIS_BODY, bold=True)
    simple_table(s, 0.36, TOP + 0.34, 9.28,
                 ["Modelo de base", "Profundo  Acc / AUC", "Con SI-MIL  Acc / AUC"],
                 [["ABMIL", "0,937 / 0,974", "0,944 / 0,968"],
                  ["CLAM (el nuestro)", "0,937 / 0,972", "0,925 / 0,957"],
                  ["TransMIL", "0,934 / 0,936", "0,929 / 0,933"]],
                 col_fracs=[0.32, 0.34, 0.34], row_h=0.50, fs=13, destacar=1)
    add_textbox(s, 0.36, TOP + 2.54, 9.28, 0.62, [
        ("Sobre nuestro modelo de base bajan las dos: la exactitud y el área bajo la curva. "
         "El titular de que no hay compromiso entre rendimiento e interpretabilidad se "
         "sostiene sobre el modelo más simple.", 13, True, TEAL_TITLE, F_BODY,
         PP_ALIGN.CENTER)], anchor=MSO_ANCHOR.MIDDLE)
    takeaway_bar(s, "Publican el dataset ya procesado, y la cohorte pública de mama está "
                    "adentro: verificar el cruce es una tarde.", t=TOP + 3.34, size=13)
    notes(s, "La tabla compara el método sobre distintos modelos de base, y uno de ellos es "
             "el nuestro.\n"
             "Sobre el nuestro, la fila destacada, las dos métricas bajan.\n"
             "Tres cosas costaría traerlo: la magnificación, el cómputo, y el dato que "
             "desarma el cómputo.\n"
             "Dos preguntas para hoy: si el interés es entenderlo o evaluarlo, y si vale una "
             "tarde cruzar su dataset con el nuestro.\n"
             "\n"
             "Los resultados. Esta tabla nos interesa más que las otras porque no compara el "
             "método contra otros métodos, sino el método aplicado sobre distintos modelos de "
             "base, y uno de esos modelos es el nuestro.\n"
             "\n"
             "Sobre el primero, que es el modelo de atención más simple, la exactitud sube un "
             "poco al agregarle la rama interpretable. Sobre el tercero baja apenas. Y sobre el "
             "nuestro, que es la fila destacada, baja: la exactitud pasa de cero coma nueve "
             "tres siete a cero coma nueve dos cinco, y el área bajo la curva de cero coma "
             "nueve siete dos a cero coma nueve cinco siete. Lo digo sin ánimo de desacreditar "
             "el trabajo, que me "
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
    s = content(prs, "La pregunta medible")
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
    # Los rótulos son los del pre-registro §2 y NO se asignan por cuál ganó: la primaria es
    # la del patólogo, o sea la que el resultado terminó refutando. Darlos vuelta para que
    # la primaria fuera la que se sostuvo tergiversaría el pre-registro, que es justo lo que
    # el rótulo tiene que hacer verificable.
    izq = panel(s, 0.36, TOP + 1.62, 4.54, None,
                "Hipótesis primaria", TEAL_TITLE,
                ["Es la del patólogo: los parches marcados no rankearían mejor que el azar.",
                 "Entonces el problema estaría en CÓMO se combinan los parches, y habría "
                 "que cambiar la manera de agregarlos."],
                TEAL_SQ, tsize=13, bsize=10.5)
    der = panel(s, 5.10, TOP + 1.62, 4.54, None,
                "Hipótesis alternativa", ONCO_DARK,
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
    notes(s, "La frase del patólogo tiene una virtud: se puede medir.\n"
             "Una lámina anotada, 4799 parches, 163 bajo alguna marca, siete grupos.\n"
             "Las dos hipótesis quedaron escritas antes de correr nada.\n"
             "La primaria es la del patólogo, y adelanto que la que se sostuvo fue la otra.\n"
             "\n"
             "Paso a la segunda parte, que es una medición nuestra.\n"
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
             "escribieron antes de correr nada. La primaria, la de la izquierda, es la del "
             "patólogo: los parches marcados no rankearían mejor que el azar, y eso apuntaría a "
             "que el problema está en cómo el modelo combina los parches; habría que cambiar la "
             "manera de agregarlos. La alternativa es que los parches marcados rankeen alto, y "
             "entonces el modelo sí mira donde hay que mirar, y lo que se pierde está antes, en "
             "cómo queda representado cada parche.\n"
             "\n"
             "Adelanto cuál de las dos se sostuvo, porque el orden en que las leo no es el orden "
             "en que salieron: la que quedó en pie fue la alternativa, y la primaria quedó "
             "refutada. Las dejo rotuladas tal como estaban registradas, sin darlas vuelta "
             "ahora que sabemos el resultado.\n"
             "\n"
             "Insisto en esto porque es lo que hace que el resultado valga: las dos lecturas, y "
             "también la mixta, quedaron escritas y guardadas antes de ver un solo número. "
             "Ninguna se acomodó después.")

    # ---- 10. Cómo se mide: es un ranking, no un mapa de calor ----
    s = content(prs, "El estadístico: un ranking, no un mapa")
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
    # El panel de texto que definía el número pasa a ser el número puesto sobre su escala: la
    # distancia hasta el azar es lo que había que ver, y un renglón de prosa no la muestra.
    # La segunda propiedad que enumeraba el panel (que no depende de la escala de la atención,
    # y por eso se compara entre modelos) baja entera al guion.
    escala_auc(s, 0.36, TOP + 2.96, 9.28, 0.890,
               pie="Es la probabilidad de que un parche marcado reciba más atención que uno "
                   "sin marca tomado al azar.")
    notes(s, "Lo que medimos no es un mapa de calor: es un número, y sale de un ranking.\n"
             "Se ordenan los parches por atención y se pregunta dónde cayeron los marcados.\n"
             "Si la atención no supiera nada, daría 0,5; observamos 0,89.\n"
             "El número no depende de la escala de la atención, y por eso se puede comparar.\n"
             "\n"
             "Acá está el punto que quiero que quede, porque es el que se pierde cuando uno "
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

    # ---- 11. Atención y marcas del patólogo ----
    # Rediseño del 4-ago, y es el cambio que Ernesto pidió con más énfasis. Se proyecta SOLO
    # la región anotada, que ocupa el doble de lado: la grilla 2x2 anterior arrastraba la
    # fila de la región sin marcas, cuyo panel de anotaciones es tejido pelado y se leía como
    # la misma imagen dos veces. Con esa fila fuera, el panel que explicaba las dos regiones
    # ya no explica nada de lo que se ve, así que se va entero al guion: una leyenda no
    # arregla una figura confusa, y la parte confusa acá no aportaba
    # ([[deck-qa-puntos-ciegos-chequeo]]).
    s = content(prs, "Atención y marcas del patólogo")
    # Caja con la relación de aspecto EXACTA del asset (1502 x 624 = 2,407), para que
    # add_image_fit no deje aire a los costados y los rótulos caigan sobre su panel. El ancho
    # tiene tope: con más de 8,10 la figura no deja lugar para las tres líneas del pie.
    MAP_L, MAP_W = 0.95, 8.10
    MAP_H = MAP_W / 2.407
    MAP_GAP = 22 / 1502.0 * MAP_W        # el aire de 22 px del montaje, en pulgadas
    col_w = (MAP_W - MAP_GAP) / 2
    add_image_fit(s, FIG_MAPAS_ANOTADA, MAP_L, TOP + 0.28, MAP_W, MAP_H, align="top")
    for i, rot in enumerate(("Atención del modelo", "Marcas del patólogo")):
        cx = MAP_L + i * (col_w + MAP_GAP) + col_w / 2
        caption(s, cx - 1.40, TOP, 2.80, rot, size=12, col=TEAL_TITLE, bold=True)
    # La procedencia al pie, que es lo que preguntó Sebastián: de qué lámina salió esto y con
    # qué se midió. Va en un solo textbox porque tres `caption` gastarían 1,2" de alto.
    pie_lineas(s, 0.36, TOP + 0.28 + MAP_H + 0.10, 9.28, PROVENANCIA, size=8)
    notes(s, "La región anotada, con la atención del modelo y las marcas del patólogo.\n"
             "Al pie, de dónde salió la lámina y qué tiene marcado.\n"
             "La lámina se escaneó en dos regiones; esta es la única que tiene marcas.\n"
             "Medimos si esa región atrae atención de por sí, y no: atrae algo menos.\n"
             "\n"
             "Estos son los mapas, que es lo que uno recuerda de un trabajo así, y por eso "
             "quiero mostrarlos después del número y no antes.\n"
             "\n"
             "A la izquierda está la atención del modelo sobre la lámina: el rojo es mucha "
             "atención, el azul poca. A la derecha, las marcas del patólogo, cada color un tipo "
             "de tejido. Mirándolos de a dos uno ya intuye que las marcas caen en zonas "
             "calientes, pero intuir no es medir, y es exactamente por eso que el resultado es "
             "el número de la lámina anterior y no esta imagen.\n"
             "\n"
             "Al pie dejé de dónde sale todo esto, porque es la pregunta natural. Es una lámina "
             "de nuestra cohorte privada, escaneada a veinte aumentos, de la que salen cuatro "
             "mil setecientos noventa y nueve parches; las marcas son sesenta y un polígonos "
             "que el patólogo dibujó, de los cuales veintiséis son mitosis. Y su etiqueta en "
             "nuestros datos es tasa mitótica alta, que es coherente con esas veintiséis marcas.\n"
             "\n"
             "Una aclaración sobre lo que están viendo, porque la lámina completa tiene una "
             "particularidad. Se escaneó en dos regiones separadas, y el pipeline extrajo "
             "parches de las dos: dos mil trescientos tres de una y dos mil cuatrocientos "
             "noventa y seis de la otra. Las ciento sesenta y tres marcas caen todas en la "
             "segunda, así que es la que proyecto acá; la otra no tiene ninguna.\n"
             "\n"
             "Eso abre un problema serio, y fuimos a cerrarlo. Si la región de abajo recibiera "
             "de por sí más atención que la de arriba, el número no estaría midiendo las marcas, "
             "estaría midiendo la región. Lo medimos: la región anotada contra la otra da entre "
             "cero coma cuatro seis y cero coma cuatro ocho, o sea que recibe algo menos de "
             "atención, no más. Y después repetimos todo confinando la medición a esa sola "
             "región, con lo cual la pregunta de la región deja de existir: el efecto no baja, "
             "sube, de cero coma ochenta y nueve a cero coma noventa.")

    # ---- 12. El resultado: la escalera de los siete grupos ----
    s = content(prs, "El resultado, grupo por grupo")
    barras_ranking(s, 0.36, TOP + 0.52, 9.28, 2.62, ESCALERA)
    _grupo(s, 0.36, TOP + 3.34, 4.54, 0.72, fill=TEAL_CARD)
    add_textbox(s, 0.36, TOP + 3.34, 4.54, 0.72, [
        ("Mitosis: 0,890 ± 0,039", 17, True, ONCO_DARK, F_BODY, PP_ALIGN.CENTER),
        ("media sobre 4 modelos que NO la vieron en entrenamiento", 9.5, False, GRIS_BODY,
         F_BODY, PP_ALIGN.CENTER)], anchor=MSO_ANCHOR.MIDDLE)
    _grupo(s, 5.10, TOP + 3.34, 4.54, 0.72, fill=TEAL_CARD2)
    add_textbox(s, 5.10, TOP + 3.34, 4.54, 0.72, [
        ("Percentil mediano: 91 de 100", 17, True, TEAL_TITLE, F_BODY, PP_ALIGN.CENTER),
        ("el parche de mitosis típico está en el 9 % más atendido", 9.5, False, GRIS_BODY,
         F_BODY, PP_ALIGN.CENTER)], anchor=MSO_ANCHOR.MIDDLE)
    notes(s, "Una barra por grupo de tejido: cuánto atiende el modelo lo que el patólogo marcó "
             "de cada cosa.\n"
             "Mitosis queda arriba de todo, y por encima incluso de tumor.\n"
             "La escalera baja hasta la grasa, que el modelo evita activamente.\n"
             "El orden no lo diseñó nadie: salió de medir, y tiene sentido clínico.\n"
             "\n"
             "Este es el resultado, y conviene leerlo entero antes de quedarse con el primer "
             "renglón.\n"
             "\n"
             "Primero, cómo se lee cada barra, porque son siete números del mismo tipo. Cada "
             "grupo es una clase de tejido que el patólogo marcó, y su barra es el mismo "
             "estadístico de recién, calculado con esas marcas: la probabilidad de que un "
             "parche de ese tejido reciba más atención que un parche cualquiera sin marca. La "
             "línea punteada del medio es el azar. Una barra a la derecha de la línea es tejido "
             "que el modelo mira más que al resto; una barra a la izquierda es tejido que mira "
             "menos.\n"
             "\n"
             "Mitosis da cero coma ochocientos noventa, con una dispersión de cero coma cero "
             "treinta y nueve entre los cuatro modelos que no la vieron en entrenamiento. Está "
             "muy lejos de la línea del azar. Dicho de la otra forma, que es la que se entiende "
             "sola: el parche de mitosis típico está entre el nueve por ciento más atendido de "
             "la lámina.\n"
             "\n"
             "Pero lo que convence no es ese número solo, es la escalera completa, porque "
             "muestra que la atención tiene estructura y que la estructura tiene sentido "
             "clínico. Abajo de todo está el tejido adiposo, en cero coma quince. Ese número es "
             "bien por debajo del azar, y eso no significa que el modelo lo ignore: significa "
             "que lo evita, que un parche de grasa recibe sistemáticamente menos atención que "
             "un parche tomado al azar, que es exactamente lo que uno querría. Después los "
             "linfocitos, también por debajo. El estroma queda justo en el azar, que es donde "
             "uno esperaría algo que no es informativo ni estorba. Y arriba, tumor y núcleos de "
             "alto grado alrededor de cero coma ochenta y tres, con mitosis por encima de los "
             "dos.\n"
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
    s = content(prs, "Los 28 parches de mitosis")
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
    # El panel de dos renglones baja a UNA línea, y sin caja: un panel alrededor de una sola
    # frase es una caja alrededor de nada, y acá la lámina la manda la figura.
    add_textbox(s, 0.36 + reg_w + zoom_w + 0.46, TOP + 1.00, 2.26, 1.40,
                [("Los parches blancos caen sobre el rojo, no sobre el borde ni sobre el "
                  "azul.", 13.5, True, ONCO_DARK, F_BODY)], anchor=MSO_ANCHOR.MIDDLE)
    takeaway_bar(s, "Y aun así, este modelo predice mal esta lámina.", t=TOP + 3.76,
                 size=13)
    notes(s, "El mismo resultado, pero puesto donde se ve de un vistazo.\n"
             "En blanco, los 28 parches que contienen una mitosis marcada.\n"
             "Debajo, en colores, dónde puso la atención el modelo.\n"
             "Los blancos caen sobre el rojo, y el rojo es donde el modelo mira.\n"
             "\n"
             "Esta es la misma información de la escalera, pero puesta donde se ve de un "
             "vistazo, y es la imagen que a mí me terminó de convencer.\n"
             "\n"
             "Explico primero cómo leerla, porque hay dos capas superpuestas. El fondo es el "
             "mapa de atención del modelo sobre esta región: el rojo es donde puso más "
             "atención, el azul donde puso menos. Encima, pintados de blanco sólido, están los "
             "veintiocho parches que contienen alguna de las mitosis que marcó el patólogo. O "
             "sea que el color lo pone el modelo y los cuadraditos blancos los pone el "
             "patólogo, y la pregunta es simplemente si los blancos caen sobre el rojo. A la "
             "derecha está el detalle del recuadro, que es donde se concentran.\n"
             "\n"
             "Miren dónde caen los blancos. No están en el borde del tejido, ni sobre las zonas "
             "azules, ni repartidos por la lámina: están sobre el corazón rojo de la mancha, que "
             "es exactamente donde el modelo concentró su atención. Un parche de mitosis y el "
             "pico de atención del modelo son, en esta lámina, el mismo lugar.\n"
             "\n"
             "Y ahora la parte incómoda, que es la que sigue. Este modelo, el que produjo este "
             "mapa, se equivoca al clasificar esta lámina.")

    # ---- 14. Mira bien y responde mal ----
    s = content(prs, "Mira bien y responde mal")
    add_textbox(s, 0.36, TOP, 9.28, 0.36, [
        ("La lámina es score_3, tasa mitótica alta, coherente con las 26 marcas de mitosis.",
         12.5, True, GRIS_BODY, F_BODY, PP_ALIGN.CENTER)], anchor=MSO_ANCHOR.MIDDLE)
    simple_table(s, 0.86, TOP + 0.44, 8.28,
                 ["Modelo", "Qué respondió", "Confianza en score_2", "AUC de atención"],
                 [["privado", "score_2   ✗", "0,645", "0,840"],
                  ["privado + TCGA", "score_3   ✓", "0,224", "0,878"],
                  ["5 folds, fold 0", "score_2   ✗", "0,712", "0,926"],
                  ["5 folds, fold 2", "score_2   ✗", "0,524", "0,917"]],
                 col_fracs=[0.26, 0.24, 0.26, 0.24], row_h=0.36, fs=11, destacar=2)
    # Los dos paneles se funden en UNA lectura: la tabla ya dice quién falla y quién mira
    # mejor, así que enumerarlo al lado era leerla en voz alta. Lo que hay que agregar es la
    # consecuencia, y eso es una frase. El resto (los 8 modelos que sí la vieron, el cambio
    # de diagnóstico) baja al guion.
    add_textbox(s, 0.36, TOP + 2.50, 9.28, 0.70, [
        ("El que mejor mira es el que más se equivoca: el problema no está en elegir los "
         "parches, sino en lo que queda del parche una vez comprimido.",
         13.5, True, TEAL_TITLE, F_BODY, PP_ALIGN.CENTER)], anchor=MSO_ANCHOR.MIDDLE)
    takeaway_bar(s, "Ese desacople entre mirar bien y responder mal es el resultado, y es "
                    "lo que reordenó el trabajo que sigue.", t=TOP + 3.40, size=12.5)
    notes(s, "La lámina tiene tasa mitótica alta, y tres de los cuatro modelos la subestiman.\n"
             "La última columna es cuánto mira cada uno las mitosis: todos miran bien.\n"
             "La fila destacada es el que mejor mira, y es el que responde peor.\n"
             "Los modelos que sí la tenían en entrenamiento la aciertan, así que no es una "
             "lámina rara.\n"
             "\n"
             "Y acá está el desenlace, que no esperábamos y que es lo que hace que esta "
             "medición valga más que la respuesta a la pregunta original.\n"
             "\n"
             "La lámina tiene tasa mitótica alta, que es coherente con las veintiséis mitosis "
             "que el patólogo marcó. Tres de los cuatro modelos que no la vieron en "
             "entrenamiento responden que tiene tasa intermedia. O sea que se equivocan, y se "
             "equivocan hacia abajo: subestiman.\n"
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

    # ---- 15. Los cuatro controles ----
    # Rehecha entera el 4-ago: Ernesto dijo que esta lámina no se entendía. La versión
    # anterior eran cuatro paneles de texto en fila, y el primero, que es el que sostiene el
    # resultado, contaba un procedimiento espacial con palabras. Acá el nulo por traslación
    # ES el objeto visual, y los otros tres controles bajan a una línea cada uno. La vara es
    # que la lámina se entienda sin nadie que la explique.
    s = content(prs, "Los cuatro controles")
    add_textbox(s, 0.36, TOP, 9.28, 0.62, [
        ("El nulo honesto traslada la mancha de marcas entera, en vez de barajar qué "
         "parches están marcados.", 12.5, True, ONCO_DARK, F_BODY),
        ("Barajar no sirve: las marcas están pegadas unas a otras y la atención también "
         "viene en manchas, así que cualquier mancha compacta gana.", 10, False, GRIS_BODY,
         F_BODY)])

    # La lámina, con su zona de atención alta, la mancha real adentro y tres traslaciones.
    # Una de las tres cae TAMBIÉN dentro de la zona caliente, y es deliberado: es lo que
    # explica que las traslaciones ya partan de 0,67 y no de 0,5.
    PL, PT, PW, PH = 0.36, 1.92, 5.60, 1.50
    _grupo(s, PL, PT, PW, PH, fill=TEAL_CARD2)
    _grupo(s, PL + 1.54, PT + 0.22, 2.20, 1.06, fill=ONCO_PANEL)
    _mancha(s, PL + 2.24, PT + 0.50, solida=True)
    _mancha(s, PL + 2.98, PT + 0.86, solida=False)
    _mancha(s, PL + 0.42, PT + 0.28, solida=False)
    _mancha(s, PL + 4.52, PT + 0.92, solida=False)
    caption(s, PL, PT + PH + 0.04, PW,
            "lleno = donde están   ·   hueco = tres de las ~440 traslaciones   ·   "
            "celeste = atención alta", size=8)

    # La distribución de los nulos contra el valor observado, que es el argumento entero:
    # la brecha entre la banda y la marca oscura. La banda va rotulada CON SUS VALORES, que
    # es lo que dice que el nulo ya parte alto y no del azar.
    nube_traslaciones(s, PL, 3.80, PW, 0.44, lo=0.60, hi=0.95, banda=(0.67, 0.75),
                      obs=0.890, rot_banda="las ~440 traslaciones: 0,67 a 0,75",
                      rot_obs="en su lugar real")

    # Los otros tres controles, a una línea cada uno.
    CL, CT, CW = 6.16, 1.92, 3.48
    _grupo(s, CL, CT, CW, 2.60, fill=TEAL_CARD2)
    add_textbox(s, CL + 0.18, CT + 0.10, CW - 0.36, 0.26,
                [("LOS OTROS TRES", 10, True, GRIS_BODY, F_BODY)])
    otros = [
        ("El efecto de región",
         "Descartado: la región anotada recibe algo menos de atención que la otra."),
        ("La memorización",
         "Los 4 modelos no la vieron en entrenamiento, y haberla visto suma solo 0,056."),
        ("El sesgo de la anotación",
         "El patólogo no marca todas las mitosis, y las que faltan acercan el número a 0,5."),
    ]
    for i, (tit, linea) in enumerate(otros):
        yy = CT + 0.42 + i * 0.70
        add_textbox(s, CL + 0.18, yy, CW - 0.36, 0.24,
                    [(tit, 11, True, ONCO_DARK, F_BODY)])
        add_textbox(s, CL + 0.18, yy + 0.24, CW - 0.36, 0.40,
                    [(linea, 9.5, False, INK, F_BODY)])
    takeaway_bar(s, "Ninguna de las ~440 traslaciones alcanzó el valor observado. Y aun así: "
                    "una lámina y un anotador describen, no establecen.", t=4.76, size=12.5)
    notes(s, "Cuatro cosas fuimos a descartar antes de creerle al número.\n"
             "La primera es la del dibujo: mover la mancha de marcas a otro lado de la lámina "
             "y ver si el número aguanta.\n"
             "De unas 440 posiciones, ninguna llegó a lo que da en su lugar real.\n"
             "Los otros tres controles están a la derecha, y ninguno explica el resultado.\n"
             "\n"
             "Antes de sacar conclusiones quiero mostrar las cuatro cosas que fuimos a "
             "descartar, porque un número alto sin esto no vale gran cosa.\n"
             "\n"
             "La primera es la más importante y es una lección que me llevo, así que la dibujé. "
             "La manera obvia de poner a prueba un resultado así es barajar al azar cuáles "
             "parches están marcados y ver cuántas veces sale un valor tan alto por casualidad. "
             "Eso lo hicimos, da significativo, y no sirve para nada: también da significativo "
             "donde no debería. El motivo es que las marcas están pegadas unas a otras y la "
             "atención también viene en manchas, así que cualquier mancha compacta le gana a un "
             "sorteo que rompe la contigüidad.\n"
             "\n"
             "La prueba honesta es la del dibujo. El rectángulo grande es la lámina y la zona "
             "celeste es donde el modelo concentra su atención. El grupito relleno son las "
             "marcas en el lugar donde realmente están. Los tres grupitos huecos son la misma "
             "mancha, con la misma forma y el mismo tamaño, corrida a otras posiciones "
             "posibles; hicimos eso unas cuatrocientas cuarenta veces, en todas las posiciones "
             "donde la mancha entra completa.\n"
             "\n"
             "Y abajo está lo que salió de esas cuatrocientas cuarenta. La banda gris es dónde "
             "caen las traslaciones: entre cero coma sesenta y siete y cero coma setenta y "
             "cinco. Fíjense que no parten del azar, y eso tiene una explicación que el dibujo "
             "muestra: como una de las copias, si uno mueve la mancha dentro del tumor sigue "
             "cayendo en zona de atención alta, así que el nulo ya es exigente de entrada. La "
             "marca oscura de la derecha es el valor en el lugar real. Ninguna de las "
             "cuatrocientas cuarenta llegó ahí, y esa brecha es el resultado.\n"
             "\n"
             "Los otros tres los paso rápido. El de la región ya lo conté. La memorización: los "
             "cuatro modelos no tenían esta lámina en su entrenamiento, y podemos medir cuánto "
             "ayudaría haberla tenido, porque hay otros que sí; la diferencia es de cero coma "
             "cero cinco seis, chica al lado de la distancia que hay hasta el azar. Y el cuarto "
             "juega a nuestro favor sin que hiciéramos nada: el patólogo marca donde la "
             "evidencia es clara, no marca todas las mitosis, y las que no marcó quedan "
             "contadas como si no tuvieran nada, lo cual empuja el número hacia el azar. El "
             "cero coma ochenta y nueve es creíble justamente porque el sesgo lo empuja para "
             "abajo.\n"
             "\n"
             "Y cierro con lo que el resultado no dice, porque también estaba pre-registrado. "
             "Una lámina y un anotador describen, no establecen. No estamos diciendo que la "
             "atención de nuestros modelos esté bien en general, ni damos por buenos los "
             "nombres de tejido que le pusimos a las unidades internas la vez pasada, que "
             "siguen esperando el visto bueno de un patólogo. Y un parche sin marca que reciba "
             "mucha atención no es un error del modelo: puede ser tejido que el patólogo "
             "simplemente no marcó.")

    # =======================================================================
    # CIERRE — el grid E×S, como «lo que además cerró este sprint»
    # =======================================================================
    # Entra DESPUÉS de los dos ejes y no como tercer eje (decisión de Ernesto, 4-ago): el
    # hallazgo que cambia el plan es el de atención, el deck ya venía largo y la lámina del
    # mapa del recorrido queda intacta. La sección se marca con su propio rótulo.
    #
    # Dos reglas que vienen del pre-registro y gobiernan estas tres láminas:
    #   - El veredicto es H_nula y se cuenta como tal. El +0,022 del primer peldaño es
    #     justamente lo que NO alcanza; presentarlo como hallazgo contradiría el prereg.
    #   - CERO Δ contra CLAM por brazo. El prereg §6 lo prohibió por diseño para no
    #     disparar ocho veces sobre el eje ya cerrado del Hallazgo 12, y encima sobre la
    #     tarea del dato abierto. Por eso CLAM no aparece en ninguna de las tres.

    # ---- 17. La pregunta y el veredicto ----
    s = content(prs, "¿Recortar expertos o slots?")
    # El rótulo de sección se queda: ubica la lámina dentro del sprint, y eso sigue siendo
    # cierto. Lo que sale es «el encargo de julio», acá y en la línea del peldaño resaltado.
    add_textbox(s, 0.36, TOP, 9.28, 0.22,
                [("LO QUE ADEMÁS CERRÓ ESTE SPRINT", 10.5, True, GRIS_BODY, F_BODY)])
    add_textbox(s, 0.36, TOP + 0.22, 9.28, 0.56, [
        ("A igual capacidad total, la diferencia pareada fold por fold entre recortar "
         "slots y recortar expertos.", 11.5, False, INK, F_BODY),
        ("Presencia de carcinoma ductal in situ · 862 láminas, 730 con presencia y 132 sin "
         "· 5 particiones, unos 13 casos de la clase chica por prueba.", 9, False,
         GRIS_BODY, F_BODY)])
    barras_divergentes(s, 0.36, TOP + 0.84, 9.28, 1.80, PELDANOS, destacar=0)
    add_textbox(s, 0.36, TOP + 2.96, 9.28, 0.26,
                [("El peldaño resaltado es el de mayor capacidad: la diferencia es de dos "
                  "centésimas, con 3 folds de 5.", 11, True, ONCO_DARK, F_BODY,
                  PP_ALIGN.CENTER)])
    takeaway_bar(s, "El signo se cambia de lado entre peldaños y la desviación supera a la "
                    "media en los tres: la dirección del recorte es indistinguible.",
                 t=TOP + 3.42, size=13)
    notes(s, "Una pregunta que quedó del sprint pasado y que este sprint cerró.\n"
             "El modelo tiene 30 expertos y 10 unidades por experto: 300 en total.\n"
             "A igual capacidad total, ¿conviene recortar por un lado o por el otro?\n"
             "La respuesta es que no se distingue: el signo se da vuelta entre niveles.\n"
             "\n"
             "Cierro con un encargo que había quedado del sprint pasado, y que este sprint "
             "cerró. No es de mitosis ni del paper.\n"
             "\n"
             "El modelo con expertos tiene por dentro treinta expertos y diez unidades por "
             "experto, trescientas en total. Habíamos medido cómo se reparte el peso entre "
             "esas trescientas y vimos que poco más de la mitad concentra casi todo. De ahí "
             "salió la lectura de que, si sobraba capacidad, sobraba del lado de las unidades "
             "y no del lado de los expertos. Lo que quedó pendiente era si eso se sostenía al "
             "ponerlo a prueba de frente.\n"
             "\n"
             "A igual capacidad total, comparamos recortar por un lado contra recortar por el "
             "otro, con las mismas particiones y midiendo la diferencia fold por fold. Tres "
             "pares, uno por nivel de capacidad. La tarea es presencia de carcinoma ductal in "
             "situ, con ochocientas sesenta y dos láminas, de las cuales setecientas treinta "
             "tienen presencia y ciento treinta y dos no, repartidas en cinco particiones; en "
             "cada prueba quedan unos trece casos de la clase chica, y eso conviene tenerlo "
             "presente al mirar cuánto se mueve el número entre particiones.\n"
             "\n"
             "Lo que ven es esa diferencia. La barra es el promedio y la línea gris es cuánto "
             "se mueve entre folds. En el primer par va a favor de recortar unidades, en el "
             "segundo se da vuelta, y en el tercero es prácticamente cero. En los tres, lo "
             "que se mueve entre folds es más grande que la diferencia misma.\n"
             "\n"
             "Cuando el signo se da vuelta entre niveles, lo que queda no es un efecto chico: "
             "es ruido alrededor de cero. Si la dirección del recorte importara, el signo "
             "sería el mismo en los tres.\n"
             "\n"
             "El par resaltado es el de mayor capacidad, o sea el recorte más chico de los "
             "tres. Su respuesta es que la diferencia es de dos centésimas a favor de "
             "recortar unidades, con tres folds de cinco, y eso no alcanza para afirmar una "
             "dirección.")

    # ---- 18. La escalera de capacidad ----
    # Las dos ramas por separado. El objeto de la lámina es la FORMA de cada una: escalón y
    # meseta en la de slots, y una curva que ni siquiera es monótona en la de expertos. Esa
    # segunda es la que convence de que lo de la lámina anterior es ruido y no un efecto
    # chico, así que va con el mismo peso visual y no como nota al pie.
    s = content(prs, "El costo de sacar capacidad")
    for x, titulo in ((0.36, "Sacando slots, con los 30 expertos fijos"),
                      (5.22, "Sacando expertos, con los 10 slots fijos")):
        add_textbox(s, x, TOP, 4.42, 0.26,
                    [(titulo, 12, True, ONCO_DARK, F_BODY, PP_ALIGN.CENTER)])
    escalera_capacidad(s, 0.36, TOP + 0.36, 4.42, 1.66, RAMA_S,
                       nota=(3, "150 slots ≈ los 159,5 que medimos"))
    escalera_capacidad(s, 5.22, TOP + 0.36, 4.42, 1.66, RAMA_E)
    caption(s, 0.36, TOP + 2.82, 4.42,
            "Un escalón en el primer recorte y después una meseta: de 270 a 90 el AUC se "
            "mueve 0,016.", size=9.5, col=INK)
    caption(s, 5.22, TOP + 2.82, 4.42,
            "Ni siquiera es monótona: el peor brazo de la tanda es el recorte más chico.",
            size=9.5, col=INK)
    caption(s, 0.36, TOP + 3.30, 9.28,
            "AUC medio de los 5 folds. Eje vertical recortado, desde 0,75, o los ocho brazos "
            "serían la misma barra.", size=9, col=GRIS_BODY)
    takeaway_bar(s, "La distancia entre dos folds del mismo brazo es de otro orden que la "
                    "distancia entre el mejor y el peor brazo: 0,25 contra 0,05 de AUC.",
                 t=TOP + 3.62, size=13)
    notes(s, "La misma tanda mirada de otra manera: qué pasa al ir sacando capacidad.\n"
             "A la izquierda sacando unidades, a la derecha sacando expertos.\n"
             "De un lado hay un escalón y después una meseta; del otro ni siquiera baja "
             "ordenado.\n"
             "Con el modelo entero recortado en un setenta por ciento, el número casi no se "
             "mueve.\n"
             "\n"
             "Acá está la misma tanda mirada de otra manera: qué pasa a medida que le "
             "sacamos capacidad, con cada lado por separado.\n"
             "\n"
             "A la izquierda, dejando fijos los expertos y sacando unidades. A la derecha, "
             "dejando fijas las unidades y sacando expertos. La barra clara del extremo "
             "izquierdo de cada gráfico es el modelo completo, que es el mismo en los dos.\n"
             "\n"
             "Del lado de las unidades hay un escalón y después una meseta. Baja en el primer "
             "recorte y ahí se queda: entre doscientas setenta y noventa unidades totales el "
             "número se mueve menos de lo que se mueve un solo brazo entre folds. Y el punto "
             "donde el total cae justo sobre lo que habíamos medido de ocupación no marca "
             "ningún quiebre, que es la parte que más me interesa, porque era exactamente la "
             "predicción.\n"
             "\n"
             "Del lado de los expertos ni siquiera baja de forma ordenada. El peor caso de "
             "toda la tanda es el recorte más chico, y sacando más expertos el número vuelve "
             "a subir. Una curva de capacidad no se comporta así.\n"
             "\n"
             "La distancia entre dos folds del mismo brazo es de otro orden que la distancia "
             "entre el mejor y el peor brazo, y eso enmarca todo lo demás. Con esa relación "
             "un efecto de este tamaño queda debajo del ruido, y por eso comparamos de a "
             "pares y fold por fold en lugar de mirar promedios sueltos.\n"
             "\n"
             "Un detalle de método por si sale la pregunta de si esto es comparable con lo "
             "anterior. El brazo del modelo completo lo volvimos a correr como control, y dio "
             "idéntico a la corrida del sprint pasado, byte por byte en las cinco "
             "particiones. Así que comparar contra una corrida anterior que comparta "
             "particiones y semilla es válido por construcción, y en el otro sentido, repetir "
             "algo con la misma semilla no aporta evidencia nueva.")

    # =======================================================================
    # CIERRE — los papers de la rama de mitosis y hacia dónde sigue
    # =======================================================================

    # ---- 19. Los tres papers ----
    # Hereda el lugar de la lámina de las cuatro familias, cuyo reordenamiento pasó entero al
    # guion. SIN las letras A/B/C/D: fuera de nuestros documentos no significan nada, y lo
    # que decide acá es una sola columna, la de qué supervisión exige cada uno.
    s = content(prs, "Tres papers para la rama de mitosis")
    caption(s, 0.36, TOP, 9.28,
            "Ordenados por lo único que descarta rápido: qué supervisión exige cada uno "
            "contra la que tenemos.", size=11, col=GRIS_BODY, bold=True)
    simple_table(s, 0.36, TOP + 0.34, 9.28,
                 ["Paper", "Cita", "Qué supervisión exige", "Qué lo frena"],
                 [list(p) for p in PAPERS],
                 col_fracs=[0.26, 0.20, 0.27, 0.27], row_h=0.50, fs=11.5, destacar=0)
    add_textbox(s, 0.36, TOP + 2.54, 9.28, 0.62, [
        ("El primero es el único cuyo régimen de supervisión coincide con el nuestro: "
         "marcas incompletas, donde lo que no está marcado no es un negativo.",
         13, True, TEAL_TITLE, F_BODY, PP_ALIGN.CENTER)], anchor=MSO_ANCHOR.MIDDLE)
    takeaway_bar(s, "Las hojas con cada paper por separado las dejé aparte, para que no "
                    "haya que decidir nada hoy sobre la marcha.", t=TOP + 3.34, size=13)
    notes(s, "Tres papers, ordenados por qué supervisión exige cada uno.\n"
             "El primero es el único que encaja con lo que tenemos: marcas parciales.\n"
             "El segundo tiene pesos públicos, pero no tiene clase de mitosis.\n"
             "El tercero necesita una magnificación que en el privado no tenemos.\n"
             "\n"
             "Y termino con los papers, que es lo que salió de todo lo anterior. Antes de "
             "listarlos quiero explicar por qué son estos y no otros, porque la medición que "
             "acabo de mostrar es la que decidió hacia dónde buscar.\n"
             "\n"
             "Teníamos cuatro maneras posibles de atacar el problema de mitosis, escritas "
             "antes de la medición. La primera era cambiar la forma en que el modelo combina "
             "los parches. La segunda, el campo de visión, porque la mitosis se cuenta a "
             "cuarenta aumentos y buena parte de nuestra cohorte está a veinte. La tercera, "
             "cambiar la unidad con la que representamos el tejido, pasando del parche al "
             "núcleo. Y la cuarta, aprovechar las marcas del patólogo como supervisión, "
             "aunque sean parciales.\n"
             "\n"
             "La medición reordenó eso. La primera pierde su motivación principal, porque su "
             "argumento de cabecera era precisamente la frase del patólogo, y la frase quedó "
             "refutada. Y quiero ser cuidadoso: pierde ese argumento, no todos. Le queda uno "
             "intacto, que esta medición no evalúa, y es que contar mitosis en el criterio "
             "clínico es buscar el máximo en un puñado de campos vecinos, no promediar toda "
             "la lámina. Las otras tres se fortalecen o quedan abiertas, y por eso la "
             "búsqueda apuntó ahí.\n"
             "\n"
             "De los tres, el primero es el que más nos sirve, y por una razón que es de "
             "encaje y no de calidad. Nuestras anotaciones son positivos parciales: el "
             "patólogo marcó veintiséis mitosis, pero no marcó todas, así que lo que no está "
             "marcado no podemos tratarlo como negativo. Ese paper está construido "
             "exactamente para ese caso, y es el único de los tres que lo está. El segundo "
             "tiene la ventaja de traer pesos públicos, o sea que no necesita nada nuestro, "
             "pero no distingue mitosis entre sus clases. Y el tercero pide poder acercarse a "
             "cuarenta aumentos, que en nuestra cohorte privada no está.\n"
             "\n"
             "De cada uno preparé una hoja aparte con el detalle, así que no hace falta "
             "decidir nada hoy sobre la marcha.")

    # ---- 20. Objetivos propuestos ----
    # Los dos que eligió Ernesto. La réplica del resultado del sprint pasado y HoVer-Net
    # sobre los mejores parches quedan FUERA a propósito: siguen abiertos, pero no se
    # proponen como objetivo. La lámina tiene que dejar a la vista de qué depende el primero,
    # que es la pregunta concreta que hay que hacer en la reunión.
    s = content(prs, "Objetivos propuestos")
    add_textbox(s, 0.36, TOP, 9.28, 0.40, [
        ("Dos, y los dos entran por el camino barato: sin GPU hasta saber si hay materia.",
         12.5, True, GRIS_BODY, F_BODY, PP_ALIGN.CENTER)], anchor=MSO_ANCHOR.MIDDLE)
    props = [
        ("1. Llevar la medición a más láminas anotadas", TEAL_CARD, TEAL_SQ, TEAL_TITLE,
         ["Repetir la medición de atención sobre cada lámina anotada que exista, con el "
          "nulo por traslación ya construido y puesto a prueba.",
          "Es lo que convierte un resultado que describe en uno que establece."]),
        ("2. Detección con positivos parciales", TEAL_CARD2, ONCO_DARK, ONCO_DARK,
         ["El paper que encaja con nuestras marcas incompletas.",
          "Entrar por lo barato y desacoplado: un detector de mitosis público contra las 26 "
          "marcas, para saber si hay señal antes de montar nada."]),
    ]
    # Cuerpos generosos y separaciones amplias: con los tamaños del resto del deck esta
    # lámina cerraba a tres cuartos del alto y se leía corta.
    cajas = [panel(s, 0.36 + i * 4.74, TOP + 0.62, 4.54, None, tit, tcol, lineas, borde,
                   fill=fill, tsize=13.5, bsize=11.5)
             for i, (tit, fill, borde, tcol, lineas) in enumerate(props)]
    alto_max = max(Emu(sp.height).inches for sp in cajas)
    for sp in cajas:
        sp.height = Inches(alto_max)
    panel(s, 0.36, TOP + 0.62 + alto_max + 0.34, 9.28, None,
          "Los dos dependen de la misma pregunta, y es la que traigo para hoy", TEAL_TITLE,
          ["¿Cuántas láminas anotadas hay además de esta, y quién las anotó?",
           "Con una sola lámina, el primero no tiene materia y el segundo se queda sin con "
           "qué evaluarse."],
          TEAL_SQ, fill=TEAL_CARD, tsize=13.5, bsize=11.5)
    notes(s, "Propongo dos objetivos, y los dos empiezan sin gastar cómputo.\n"
             "El primero es llevar la medición de atención a todas las láminas anotadas que "
             "haya.\n"
             "El segundo es probar el paper de marcas parciales por su camino más barato.\n"
             "Los dos dependen de una sola pregunta, que es la que quiero hacer hoy.\n"
             "\n"
             "Con todo lo anterior sobre la mesa, propongo dos cosas para lo que viene, y las "
             "propongo así porque las dos se pueden empezar sin pedir cómputo.\n"
             "\n"
             "La primera es llevar la medición de atención a más láminas anotadas. Hoy tengo "
             "una, y con una lámina el resultado describe pero no establece; lo dije al "
             "principio y lo sostengo. La buena noticia es que la herramienta ya está "
             "construida y puesta a prueba: el nulo por traslación, que fue lo que más costó, "
             "sirve tal cual para cualquier lámina que tenga marcas. O sea que el trabajo "
             "pesado ya está hecho y lo que falta es material.\n"
             "\n"
             "La segunda es el paper de detección con marcas parciales. No propongo montarlo "
             "entero, propongo entrar por donde es barato: agarrar un detector de mitosis "
             "público, pasarlo por nuestra lámina y ver cuánto acierta contra las veintiséis "
             "marcas que tenemos. Eso responde si hay señal aprovechable antes de invertir "
             "nada, y si la respuesta es que no, nos ahorramos el resto.\n"
             "\n"
             "Y las dos cuelgan de la misma pregunta, que es la que necesito que conversemos "
             "hoy: cuántas láminas anotadas hay además de esta, y quién las anotó. Lo "
             "pregunto porque el archivo de anotaciones que tengo viene firmado con unas "
             "iniciales que no sé de quién son, y eso importa por dos motivos. Uno práctico: "
             "si hay más láminas del mismo anotador, el primer objetivo arranca la semana que "
             "viene. Y otro de método: si las que aparezcan son de anotadores distintos, hay "
             "que tenerlo en cuenta al juntarlas, porque no todos marcan con el mismo "
             "criterio.")

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
