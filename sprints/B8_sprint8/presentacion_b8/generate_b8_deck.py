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

RECORTE del 5-ago: de 20 a 16 láminas, fusionando pares y agrandando lo que queda.

REORDENAMIENTO del 6-ago, pedido por SEBASTIÁN tras ver el deck, y ejecutado el 7-ago. Queda
en 14 láminas y la audiencia pasa a ser Benjamín, la semana del 11-ago:
  - El orden es GRID → ATENCIÓN → SI-MIL. Invierte la decisión del 3-ago (lo cerrado antes que
    lo vivo) y jubila el encuadre del 4-ago (el grid como cierre); las dos eran de encuadre
    nuestro, ésta viene del supervisor y no se re-decide.
  - Se van dos láminas: OBJETIVOS DEL SPRINT y los TRES PAPERS. El molde de la primera no se
    pierde, lo hereda «Objetivos propuestos»; el razonamiento de la segunda baja al guion de
    esa misma lámina, porque es la justificación del objetivo propuesto 2.
  - Las cuatro láminas de la medición pasan a describir el ESTADÍSTICO con precisión: qué es
    (U de Mann-Whitney normalizada), contra qué se mide cada grupo, y con cuánta precisión
    (el IC de Hanley-McNeil, que es una incertidumbre distinta de la sd entre checkpoints).
  - `build()` deja de ser un bloque único: una función por lámina y el orden en un solo lugar.

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
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR, MSO_SHAPE_TYPE
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
# La reunión con Sebastián fue el jueves 6-ago y ya ocurrió; la del viernes 7 con Benjamín
# se cayó (Ernesto tiene clases). Esta versión del deck se presenta a Benjamín la semana del
# 11-ago, sin día confirmado todavía: la portada lleva el mes hasta que haya fecha.
FECHA_REUNION = "19 de agosto de 2026"

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

# --- figuras de la sección de regiones de escaneo (producción NUESTRA) ---
# Preparadas por prep_assets_regiones.py. Las dos regiones vienen recortadas en la misma
# cantidad de columnas, así que la correspondencia entre ellas se conserva; el registro a
# resolución completa se saca de git y no del árbol, porque el re-barrido en curso movió el
# archivo del árbol a su propio subdirectorio.
REG0 = os.path.join(ASSETS, "region0_129741.png")            # ar 1.0437
REG1 = os.path.join(ASSETS, "region1_129741.png")            # ar 1.0021
REGISTRO = os.path.join(ASSETS, "registro_level0_129741.png")  # ar 2.0312

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
#
# La cuarta columna es el SEMIANCHO del intervalo de confianza al 95 % del AUC, calculado el
# 6-ago con la fórmula de Hanley y McNeil sobre `con_region/auc_por_checkpoint.csv`
# (universo `lamina`, rol `primario`): 1,96 × EE, con EE = √([A(1−A) + (n₊−1)(Q₁−A²) +
# (n₋−1)(Q₂−A²)] / (n₊·n₋)), Q₁ = A/(2−A), Q₂ = 2A²/(1+A), n₊ = parches del grupo y
# n₋ = 4799 − n₊. Es la precisión que da ESE tamaño de grupo, y es una incertidumbre
# DISTINTA de la sd entre checkpoints (que mide cambiar de modelo, no cambiar de marcas).
# Por eso el bigote de estroma (n = 12) mide el triple que el de tejido adiposo (n = 27).
ESCALERA = [
    ("Mitosis", 28, 0.890, 0.080, True),
    ("Núcleos de alto grado", 13, 0.828, 0.138, True),
    ("Tumor", 48, 0.826, 0.072, False),
    ("Necrosis", 18, 0.748, 0.131, False),
    ("Estroma", 12, 0.537, 0.167, False),
    ("Linfocitos", 23, 0.322, 0.095, False),
    ("Tejido adiposo", 27, 0.154, 0.050, False),
]

# --- la cuenta que lleva de 26 marcas a 28 parches, calculada el 6-ago sobre la geometría
# real (geojson + coords del h5, con el offset dx = 3829 ya adoptado). La regla de mapeo es
# la de `alinear_anotaciones_qupath.py:252`: un parche cuenta si su cuadrado de 256 px se
# solapa con la caja envolvente del polígono.
#   26 polígonos de mitosis → 36 pares (polígono, parche) → 28 parches distintos
#   16 polígonos caen enteros dentro de un parche · 10 se reparten entre dos  → +10
#   21 parches tienen una sola mitosis · 6 tienen dos · 1 tiene tres          →  −8
CUENTA_26_28 = [("26", "marcas del patólogo"),
                ("+10", "cruzan un borde y ocupan dos parches"),
                ("−8", "siete parches tienen más de una marca"),
                ("28", "parches con mitosis")]

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

# --- objetivos PROPUESTOS para el sprint siguiente ---
# Pedido de Ernesto (5-ago, reafirmado el 6): la lámina de cierre usa el MOLDE DE
# RECAPITULACIÓN, que es el de las presentaciones anteriores, y no dos tarjetas.
#
# El molde venía de la lámina «Objetivos del sprint», que el reordenamiento del 6-ago
# eliminó. Sus medidas quedan acá porque son lo único que había que conservar de ella:
# fila de 19 pt sobre 7,75" de ancho, `row_tops = 1.10 + i * 0.68`, `row_h = 0.62`, y el
# marcador de estado a la derecha en `x = 8.98`. Lo replica `lam_objetivos_propuestos`.
#
# Una línea cada uno: a 19 pt sobre 7,75" un ítem de dos renglones hace que las filas se
# toquen entre sí.
OBJETIVOS_PROP = [
    "1. Llevar la medición de atención a más láminas anotadas.",
    "2. Probar detección de mitosis con positivos parciales.",
]

# --- los 4 checkpoints primarios de la medición de atención ---
# Ernesto (5-ago): «5 folds, fold 0» no dice con qué se entrenó el modelo. Estas filas
# son el dataset de ENTRENAMIENTO de cada uno, contado el 5-ago sobre los splits reales:
#   environ/splits/grado_histologico_mitotic_rate_100/splits_0_bool.csv        → 120/15/18 (153)
#   environ/splits/grado_histologico_mitotic_rate_combined_100/splits_0_bool.csv → 783/98/97 (978)
#   environ/splits_5fold/grado_histologico_mitotic_rate_combined_100/          → 934 en total;
#       fold 0 → 746 train, fold 2 → 749 train. La lámina 129741 está en `val` en los dos,
#       y en `train` en los folds 1, 3 y 4 — por eso de la corrida de cinco aparecen SOLO dos.
# Métricas: atencion_vs_patologo/resultados.md §3.
CKPTS_TABLA = [
    ["Privado · 120 láminas", "score_2   ✗", "0,645", "0,840"],
    ["Privado + TCGA · 783 láminas", "score_3   ✓", "0,224", "0,878"],
    ["Privado + TCGA · 746 láminas · fold 0", "score_2   ✗", "0,712", "0,926"],
    ["Privado + TCGA · 749 láminas · fold 2", "score_2   ✗", "0,524", "0,917"],
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


# Las dos piezas de la barra de remate de cada lámina, para que `auditar` pueda ver si
# algún objeto la cruza. Los cuatro cruces del 18-ago pasaron la auditoría porque cada
# objeto estaba DENTRO de su caja: el defecto no es de una caja, es de dos que se tocan.
#
# Se guardan los SHAPES y no la altura: `reflow_onco` corre después y reancla (y a veces
# comprime) el cuerpo entero, así que el 4,85 de acá no es donde la barra termina. Leer la
# posición real al auditar es lo único que sobrevive a esa pasada.
_TAKEAWAY = {}


def takeaway_bar(slide, text, t=4.85, col=TEAL_TITLE, size=14):
    linea = _rect(slide, 0.35, t, SW - 0.7, 0.02, TEAL_SQ)
    tb = add_textbox(slide, 0.35, t + 0.08, SW - 0.7, 0.62,
                     [(text, size, True, col, F_BODY, PP_ALIGN.CENTER)],
                     anchor=MSO_ANCHOR.MIDDLE)
    _TAKEAWAY[id(slide._element)] = (linea, tb)


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
    """Barras horizontales de AUC con la marca del azar y el bigote del IC 95 %.

    `datos` = (nombre, n, auc, ic, interes), con `ic` = semiancho del intervalo. El bigote
    es lo que convierte la escalera en una lámina honesta: sin él, siete barras del mismo
    grosor sugieren siete números de la misma calidad, y no lo son — la precisión la fija
    el n de cada grupo, que va de 12 a 48 parches."""
    fila = h / len(datos)
    alto_barra = min(0.26, fila * 0.62)
    x0 = l + x_eje
    for i, (nombre, n, auc, ic, interes) in enumerate(datos):
        cy = t + i * fila + fila / 2
        add_textbox(slide, l, cy - 0.15, x_eje - 0.14, 0.30,
                    [("%s  (n = %d)" % (nombre, n), fs, interes, ONCO_DARK if interes else INK,
                      F_BODY, PP_ALIGN.RIGHT)], anchor=MSO_ANCHOR.MIDDLE)
        _rect(slide, x0, cy - alto_barra / 2, ancho_eje * auc, alto_barra,
              ONCO_DARK if interes else ONCO_PANEL)
        # bigote: tallo fino de auc−ic a auc+ic, con tope en los dos extremos. Va en el
        # azul oscuro del template para que se lea tanto sobre la barra como sobre el fondo.
        xa = x0 + ancho_eje * max(0.0, auc - ic)
        xb = x0 + ancho_eje * min(1.0, auc + ic)
        _rect(slide, xa, cy - 0.012, xb - xa, 0.024, ONCO_INK)
        for xc in (xa, xb):
            _rect(slide, xc - 0.012, cy - 0.085, 0.024, 0.170, ONCO_INK)
        # El valor va en COLUMNA FIJA al final del eje, no pegado a la punta del bigote.
        # Pegado se rompía con los grupos bajo el azar: el rótulo de linfocitos (0,322)
        # caía justo donde pasa la línea punteada del 0,5 y quedaba tachado. Los dos
        # objetos eran válidos y estaban en su caja, así que ningún chequeo automático lo
        # veía; salió del rasterizado ([[deck-qa-puntos-ciegos-chequeo]]). De paso los siete
        # números quedan alineados, que es como se comparan.
        add_textbox(slide, x0 + ancho_eje + 0.10, cy - 0.15, 0.80, 0.30,
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


def cadena_cuenta(slide, l, t, w, items, h=0.42, fs=14, fs_pie=8):
    """Una cuenta con el resultado ya hecho, en bloques encadenados.

    Es el arquetipo que la convención pide cuando un bullet dice un número que sale de otros
    ([[deck-contenido-visual-no-bullets]]): «26 marcas dan 28 parches» no se explica en una
    frase subordinada, se dibuja. Los extremos son bloques de proceso (los dos números que
    alguien puede cruzar y creer que se contradicen) y el medio son los dos ajustes."""
    n = len(items)
    cw = (w - 0.30 * (n - 1)) / n
    for i, (num, pie) in enumerate(items):
        x = l + i * (cw + 0.30)
        extremo = i in (0, n - 1)
        _rect(slide, x, t, cw, h, ONCO_DARK if extremo else ONCO_PANEL)
        add_textbox(slide, x, t, cw, h,
                    [(num, fs, True, WHITE if extremo else ONCO_INK, F_BODY, PP_ALIGN.CENTER)],
                    anchor=MSO_ANCHOR.MIDDLE)
        add_textbox(slide, x, t + h + 0.04, cw, 0.34,
                    [(l_, fs_pie, False, GRIS_BODY, F_BODY, PP_ALIGN.CENTER)
                     for l_ in pie.split("\n")])
        if i < n - 1:
            _conn(slide, x + cw + 0.04, t + h / 2, x + cw + 0.26, t + h / 2)


def cinta_ranking(slide, l, t, w, marcados, n=34, h=0.40, fs=9, ejes=True):
    """Los N parches de la lámina ordenados por atención, con los anotados resaltados.

    Es la figura del ESTADÍSTICO, que es justamente lo que no dejó ninguna imagen cuando se
    hizo la medición y por eso no se retuvo ([[hallazgo-necesita-forma-presentable]]). Cada
    celda es un parche; el orden es de más a menos atención."""
    cw = w / n
    for i in range(n):
        col = ONCO_DARK if i in marcados else ONCO_PANEL
        sp = _rect(slide, l + i * cw, t, cw * 0.86, h, col)
        sp.line.color.rgb = WHITE; sp.line.width = Pt(0.5)
    # El eje se dibuja una sola vez cuando hay dos cintas apiladas: es el mismo orden en las
    # dos, y repetirlo debajo de cada una lo convierte en ruido.
    if not ejes:
        return
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

    # El rótulo y su subtítulo ocupan `off` arriba y abajo del centro de la fila. Con filas
    # bajas (la lámina fusionada del 5-ago las dejó en 0,39") los 0,26 fijos hacían que el
    # subtítulo de una fila pisara el rótulo de la siguiente.
    off = max(0.17, min(0.26, fila * 0.46))
    for i, (rot, sub, media, sd, signos) in enumerate(filas):
        cy = t + i * fila + fila / 2
        add_textbox(slide, l, cy - off, lab_w, off,
                    [(rot, fs, True, ONCO_DARK, F_BODY, PP_ALIGN.RIGHT)], anchor=MSO_ANCHOR.MIDDLE)
        add_textbox(slide, l, cy + 0.01, lab_w, off - 0.02,
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
            "escala: ± %s de AUC   ·   cada cuadro es una partición, relleno = a favor de "
            "recortar slots" % _num(esc, 2), size=9)


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
# Figuras nativas del rediseño del 5-ago (SI-MIL pedagógico y nulo espacial)
# ============================================================================
def _mezcla(c0, c1, f):
    """Interpola dos colores de la paleta. Sirve para dar INTENSIDAD sin inventar tonos
    nuevos: todos los intermedios caen sobre la recta que une dos colores del template."""
    return RGBColor(*(int(round(a + (b - a) * f)) for a, b in
                      zip((c0[0], c0[1], c0[2]), (c1[0], c1[1], c1[2]))))


def barras_esquema(slide, l, t, w, h, alturas, col, destacados=(), col_dest=None):
    """Tira de barras verticales de altura dada, como ESQUEMA de un vector de pesos.

    No es un dato medido y no lleva eje ni valores: lo que tiene que leerse es la FORMA
    del vector (parejo antes de la compuerta, casi todo en cero después). Por eso las
    alturas se escriben a mano y son las mismas en cada regenerada."""
    n = len(alturas)
    paso = w / n
    ancho = paso * 0.62
    base = t + h
    for i, a in enumerate(alturas):
        alto = max(0.012, a * h)
        c = (col_dest or ONCO_DARK) if i in destacados else col
        _rect(slide, l + i * paso + (paso - ancho) / 2, base - alto, ancho, alto, c)
    return base


# Vector de pesos ANTES y DESPUÉS de la compuerta de la ecuación 5. Escritos a mano y
# fijos: son un esquema del mecanismo del paper, no una medición nuestra.
BETA_ANTES = [.52, .61, .48, .70, .55, .66, .44, .58, .74, .50, .63, .47, .68, .54, .60,
              .45, .72, .56, .49, .64, .53, .67, .46, .59, .71, .51, .62, .57, .43, .65]
BETA_DESPUES = [.04, .06, .03, .92, .05, .07, .03, .04, .98, .05, .08, .03, .06, .04, .05,
                .03, .95, .06, .04, .07, .05, .88, .03, .05, .09, .04, .06, .05, .03, .07]
BETA_VIVOS = (3, 8, 16, 21)


def grilla_contribuciones(slide, l, t, w, h, filas, cols, patron, celda_max=0.20):
    """La ecuación 9 dibujada: una celda por (parche, medición), con SIGNO.

    El punto de la ecuación es que la predicción se descompone en una suma de términos
    legibles, y que cada término tiene dirección. Por eso el color codifica el signo (teal
    = empuja hacia la clase, gris = en contra) y el tamaño codifica cuánto. Los valores son
    un esquema del mecanismo, no números del paper ni nuestros: no se rotula ninguno."""
    lab_w = 1.16
    x0 = l + lab_w
    paso_x = (w - lab_w) / len(cols)
    paso_y = h / len(filas)
    for j, c in enumerate(cols):
        add_textbox(slide, x0 + j * paso_x, t - 0.30, paso_x, 0.28,
                    [(c, 8.5, True, GRIS_BODY, F_BODY, PP_ALIGN.CENTER)],
                    anchor=MSO_ANCHOR.BOTTOM)
    for i, f in enumerate(filas):
        cy = t + i * paso_y + paso_y / 2
        add_textbox(slide, l, cy - 0.13, lab_w - 0.10, 0.26,
                    [(f, 9, False, INK, F_BODY, PP_ALIGN.RIGHT)], anchor=MSO_ANCHOR.MIDDLE)
        for j in range(len(cols)):
            v = patron[i][j]
            cx = x0 + j * paso_x + paso_x / 2
            if v == 0:
                # una contribución nula se DIBUJA, chiquita y casi blanca: dejar el hueco
                # vacío hace que la grilla se lea rota en vez de leerse como un cero
                _rect(slide, cx - 0.03, cy - 0.03, 0.06, 0.06,
                      _mezcla(TEAL_CARD2, ONCO_DATA, 0.18))
                continue
            lado = 0.07 + abs(v) / 3.0 * (celda_max - 0.07)
            col = _mezcla(TEAL_CARD2, ONCO_DARK if v > 0 else ONCO_DATA,
                          0.35 + 0.65 * abs(v) / 3.0)
            _rect(slide, cx - lado / 2, cy - lado / 2, lado, lado, col)
    return t + h


def mapa_traslaciones(slide, l, t, w, h, c=0.055):
    """El nulo por traslación, dibujado sobre una lámina con forma.

    Rehecha el 5-ago: la versión anterior era un rectángulo con otro rectángulo adentro y
    una leyenda de colores al pie, y Ernesto dijo que no se entendía. Acá la zona de
    atención tiene forma orgánica, las copias se atan a la original con flechas punteadas
    (traslación = un movimiento, no cuatro manchas sueltas) y los rótulos van PEGADOS a lo
    que nombran, en vez de en una leyenda ([[deck-qa-puntos-ciegos-chequeo]])."""
    _grupo(slide, l, t, w, h, fill=TEAL_CARD2)
    # zona de atención alta: tres óvalos solapados, para que se lea como una mancha de
    # tejido y no como una caja
    for fx, fy, fw, fh in ((0.30, 0.16, 0.30, 0.62), (0.44, 0.30, 0.26, 0.56),
                           (0.24, 0.42, 0.22, 0.44)):
        sp = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(l + fx * w), Inches(t + fy * h),
                                    Inches(fw * w), Inches(fh * h))
        sp.fill.solid(); sp.fill.fore_color.rgb = ONCO_PANEL
        sp.line.fill.background(); sp.shadow.inherit = False
    # el rótulo de la zona caliente va a la DERECHA de las manchas y no encima: centrado
    # arriba quedaba pegado al de la mancha real y los dos se leían como un título de dos
    # renglones, en vez de como dos rótulos de dos cosas distintas
    add_textbox(slide, l + 0.62 * w, t + 0.20 * h, 0.36 * w, 0.22,
                [("donde el modelo mira", 8.5, True, ONCO_DARK, F_BODY, PP_ALIGN.LEFT)])
    # la mancha real, dentro de la zona caliente
    rx, ry = l + 0.40 * w, t + 0.36 * h
    # las copias: una fuera del tejido caliente, una en el borde y una que cae DENTRO —
    # esa última es la que explica que el nulo parta de 0,67 y no del azar
    copias = [(l + 0.06 * w, t + 0.10 * h), (l + 0.74 * w, t + 0.56 * h),
              (l + 0.31 * w, t + 0.62 * h)]
    for cx, cy in copias:
        _mancha(slide, cx, cy, c=c, solida=False)
        _conn_dash(slide, rx + 1.5 * c, ry + 1.5 * c, cx + 1.5 * c, cy + 1.5 * c)
    _mancha(slide, rx, ry, c=c, solida=True)
    add_textbox(slide, rx - 0.30, ry - 0.30, 1.70, 0.22,
                [("las marcas, donde están", 9, True, ONCO_INK, F_BODY)])
    add_textbox(slide, copias[1][0] - 0.20, copias[1][1] + 4.2 * c, 2.10, 0.22,
                [("la misma mancha, corrida", 9, True, GRIS_BODY, F_BODY)])
    add_textbox(slide, copias[2][0] - 0.10, copias[2][1] + 4.2 * c, 2.60, 0.22,
                [("algunas caen igual en zona caliente", 8.5, True, GRIS_BODY, F_BODY)])
    return t + h


def destilacion(slide, l, t, w, h):
    """La ecuación 10 en tres bloques: las dos ramas se entrenan a la vez y la interpretable
    persigue a la profunda. Sin ese tercer término serían dos modelos en paralelo."""
    bw = (w - 0.30) / 2
    _proc(slide, l, t, bw, h, "Rama profunda", dim="su error", size=10)
    _proc_claro(slide, l + bw + 0.30, t, bw, h, "Rama interpretable", dim="su error", size=10)
    _conn_dash(slide, l + bw, t + h * 0.5, l + bw + 0.30, t + h * 0.5)
    add_textbox(slide, l, t + h + 0.04, w, 0.24,
                [("y un tercer término la empuja a parecerse a la profunda   (10)",
                  9, True, ONCO_DARK, F_BODY, PP_ALIGN.CENTER)])
    return t + h + 0.28


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


def _borde_inferior(problemas, idx, sh, t, h, b_ef, bar_t, propias):
    """Marca el shape que CRUZA la barra de remate.

    Las dos piezas de la barra se excluyen por identidad y no por posición: `reflow_onco`
    le sube el texto por encima de su propia línea, así que por posición la barra se
    marcaría a sí misma en casi toda lámina. Y terminar JUSTO sobre la línea no es
    cruzarla, por eso el margen va hacia abajo."""
    if bar_t is None or id(sh._element) in propias:
        return
    if t < bar_t - 0.01 and b_ef > bar_t + 0.02:
        problemas.append("s%02d  cruza la barra de remate: %s baja hasta %.2f\" "
                         "(la barra va en %.2f)" % (idx, sh.shape_type, b_ef, bar_t))


def auditar(prs, skip=()):
    """Chequeo de defectos que el ojo ve y un chequeo ingenuo no: texto que no entra en su
    caja, shapes fuera del lienzo, cuerpos por debajo del mínimo del template (7 pt) y
    objetos que cruzan la barra de remate.

    Se corre ANTES de escalar, o sea en el espacio de 10 x 5.625. No reemplaza mirar las
    láminas ([[deck-qa-puntos-ciegos-chequeo]]), pero caza la clase de defecto que más
    apareció acá: la última línea de un panel quedando afuera."""
    problemas = []
    for idx, slide in enumerate(prs.slides, start=1):
        if id(slide._element) in skip:
            continue
        par = _TAKEAWAY.get(id(slide._element))
        bar_t, propias = None, ()
        if par is not None:
            linea, tb = par
            bar_t = Emu(linea.top).inches
            propias = (id(linea._element), id(tb._element))
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
                _borde_inferior(problemas, idx, sh, t, h, t + h, bar_t, propias)
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
            # Una caja de texto no se ve: lo que se ve es el texto adentro. Medir la caja
            # marcaba captions de una línea sobre una caja de 0,4" que no cruzan nada, y un
            # chequeo que grita de más se termina ignorando, que es justo el modo de falla
            # que este chequeo vino a tapar. Un panel pintado sí se ve entero.
            b_ef = t + h
            if sh.shape_type == MSO_SHAPE_TYPE.TEXT_BOX and alto < h:
                anc = sh.text_frame.vertical_anchor
                if anc == MSO_ANCHOR.MIDDLE:
                    b_ef = t + (h + alto) / 2
                elif anc != MSO_ANCHOR.BOTTOM:
                    b_ef = t + alto
            _borde_inferior(problemas, idx, sh, t, h, b_ef, bar_t, propias)
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
# ============================================================================
# Las láminas: una función por lámina
# ============================================================================
# Refactor del 7-ago. `build()` era un bloque único de mil líneas, así que cambiar
# el orden del deck significaba mover mil líneas y confiar en que la indentación
# sobreviviera. Ahora cada lámina es una función y `build()` es la lista de
# llamadas: el orden se lee de un vistazo y el próximo reordenamiento es mover
# renglones de una línea. El cuerpo de cada bloque quedó donde estaba, a cuatro
# espacios, porque ya lo estaba dentro de `build()`.
def lam_portada(prs):
    """Portada de marca, heredada del template."""
    s = retitular_portada(prs)
    notes(s, "Traigo tres cosas, y las puse en ese orden a propósito.\n"
             "\n"
             "Empiezo por un encargo que había quedado del sprint pasado y que ya cerró: si al "
             "modelo con expertos le sobra capacidad por dentro, y de qué lado conviene "
             "recortarla. Es corto, da un resultado negativo y lo dejo cerrado ahí mismo.\n"
             "\n"
             "Después va lo que más me importa dejar claro, que es una medición nuestra. Fuimos "
             "a ver si el modelo mira donde el patólogo marcó las mitosis. Tiene un resultado, "
             "y el resultado cambió hacia dónde apunta el trabajo que sigue. En esa parte me "
             "voy a detener bastante en cómo se mide, porque el número es lo que hay que poder "
             "defender, y quiero que quede claro qué dice y qué no dice.\n"
             "\n"
             "Y cierro con la revisión de uno de los papers que habían quedado encargados, que "
             "propone un modelo que se explica solo. Para conseguirlo invierte el reparto de "
             "trabajo habitual: la red profunda deja de ser la que predice y pasa a ser la que "
             "enseña dónde mirar, mientras la predicción la hace un modelo lineal sobre "
             "mediciones de núcleos que tienen nombre de patología. Es una lectura terminada, "
             "así que la voy a contar comprimida.")


def lam_grid(prs):
    # ---- El grid E×S, en una sola lámina ----
    # Fusión pedida por Ernesto el 5-ago: las dos láminas del grid pasan a una, con los tres
    # diagramas y sin los renglones de prosa que los acompañaban. El veredicto sube al primer
    # renglón, que es donde estaba la barra de remate, y las dos lecturas de forma (el escalón
    # con meseta de una rama, la curva no monótona de la otra) bajan al guion.
    #
    # Las dos reglas del pre-registro siguen gobernando:
    #   - El veredicto es H_nula y se cuenta como tal. El +0,022 del primer peldaño es
    #     justamente lo que NO alcanza; presentarlo como hallazgo contradiría el prereg.
    #   - CERO Δ contra CLAM por brazo. El prereg §6 lo prohibió por diseño para no disparar
    #     ocho veces sobre el eje ya cerrado del Hallazgo 12, y encima sobre la tarea del dato
    #     abierto. Por eso CLAM no aparece.
    s = content(prs, "¿Recortar expertos o slots?")
    add_textbox(s, 0.36, TOP, 9.28, 0.28, [
        ("El signo se da vuelta entre peldaños y la desviación supera a la media en los "
         "tres: la dirección es indistinguible.", 12, True, TEAL_TITLE, F_BODY,
         PP_ALIGN.CENTER)], anchor=MSO_ANCHOR.MIDDLE)
    add_textbox(s, 0.36, TOP + 0.30, 9.28, 0.22, [
        ("Presencia de carcinoma ductal in situ · 862 láminas, 730 con presencia y 132 sin · "
         "5 particiones. Abajo, AUC medio por brazo con el eje desde 0,72.",
         9, False, GRIS_BODY, F_BODY, PP_ALIGN.CENTER)])
    barras_divergentes(s, 0.36, TOP + 0.88, 9.28, 1.40, PELDANOS, destacar=0)
    for x, titulo in ((0.36, "Sacando slots, con los 30 expertos fijos"),
                      (5.22, "Sacando expertos, con los 10 slots fijos")):
        add_textbox(s, x, TOP + 2.62, 4.42, 0.24,
                    [(titulo, 11.5, True, ONCO_DARK, F_BODY, PP_ALIGN.CENTER)])
    escalera_capacidad(s, 0.36, TOP + 2.90, 4.42, 0.86, RAMA_S, lo=0.72, hi=0.845)
    escalera_capacidad(s, 5.22, TOP + 2.90, 4.42, 0.86, RAMA_E, lo=0.72, hi=0.845)
    notes(s, "Un encargo que quedó del sprint pasado y que este sprint cerró.\n"
             "El modelo tiene 30 expertos y 10 unidades por experto: 300 en total.\n"
             "A igual capacidad total, ¿conviene recortar por un lado o por el otro?\n"
             "Arriba, la diferencia pareada; abajo, qué cuesta ir sacando capacidad.\n"
             "\n"
             "Empiezo por acá porque es lo más corto y así lo dejamos atrás. No "
             "es de mitosis ni del paper: es el encargo que había quedado sobre el modelo con "
             "expertos.\n"
             "\n"
             "Ese modelo tiene por dentro treinta expertos y diez unidades por experto, "
             "trescientas en total. En el título aparecen como slots, que es lo mismo. El "
             "sprint pasado medimos cómo se reparte el peso entre esas trescientas, y quedó el "
             "reparo de que lo habíamos medido sobre siete láminas, que no son la tarea. Lo "
             "primero que hicimos este sprint fue escalarlo: todas las láminas de prueba de "
             "las tres tareas y las tres cohortes, mil ciento setenta y seis láminas distintas. "
             "Y el número aguanta. El reparto ocupa alrededor de ciento sesenta de las "
             "trescientas, y los treinta expertos se usan los treinta, sin una sola excepción. "
             "De ahí salió la lectura de que, si sobraba capacidad, sobraba del lado de las "
             "unidades y no del lado de los expertos. Lo que quedó pendiente era si eso se "
             "sostenía al ponerlo a prueba de frente.\n"
             "\n"
             "A igual capacidad total, comparamos recortar por un lado contra recortar por el "
             "otro sobre las mismas particiones, midiendo la diferencia en cada una. Tres "
             "pares, uno por peldaño de capacidad. La tarea es presencia de carcinoma ductal in "
             "situ, con ochocientas sesenta y dos láminas repartidas en cinco particiones: "
             "setecientas treinta tienen presencia y ciento treinta y dos no. En cada prueba "
             "quedan unos trece casos de la clase chica, y eso conviene tenerlo presente al "
             "mirar cuánto se mueve el número entre particiones.\n"
             "\n"
             "La figura de arriba es esa diferencia. La barra es el promedio y la línea gris "
             "es cuánto se mueve entre particiones. En el primer par va a favor de recortar "
             "unidades, en el segundo se da vuelta, y en el tercero es prácticamente cero. En "
             "los tres, lo que se mueve entre particiones es más grande que la diferencia "
             "misma. Cuando el signo se da vuelta entre peldaños, lo que queda no es un efecto "
             "chico: es ruido alrededor de cero. Si la dirección del recorte importara, el "
             "signo sería el mismo en los tres. El par resaltado es el de mayor capacidad, o "
             "sea el recorte más chico, y su respuesta es una diferencia de dos centésimas "
             "con tres particiones de cinco, que no alcanza para afirmar una dirección.\n"
             "\n"
             "Abajo está la misma tanda mirada de otra manera: qué pasa a medida que le "
             "sacamos capacidad, con cada lado por separado. A la izquierda dejamos fijos los "
             "expertos y sacamos unidades; a la derecha, fijas las unidades y sacamos "
             "expertos. La barra clara del extremo "
             "izquierdo de cada gráfico es el modelo completo, que es el mismo en los dos.\n"
             "\n"
             "Del lado de las unidades hay un escalón y después una meseta. Baja en el primer "
             "recorte y ahí se queda: desde noventa unidades totales hasta doscientas setenta, "
             "el número se mueve menos de lo que se mueve un solo brazo entre particiones. Y "
             "hay un punto donde el total cae justo sobre lo que habíamos medido de ocupación, "
             "alrededor de ciento sesenta: ahí no se marca ningún quiebre, que es la parte que "
             "más me interesa, porque era exactamente la predicción. Del lado de los expertos "
             "ni siquiera baja de forma ordenada: el peor caso de toda la tanda es el recorte "
             "más chico, y sacando más expertos el número vuelve a subir. Una curva de "
             "capacidad no se comporta así.\n"
             "\n"
             "Para enmarcar los dos gráficos: la distancia entre dos particiones del mismo "
             "brazo es de otro orden que la distancia entre el mejor y el peor brazo, cero "
             "coma veinticinco contra cero coma cero cinco. Con esa relación un efecto de este "
             "tamaño queda debajo del ruido, y por eso comparamos de a pares y partición por "
             "partición en lugar de mirar promedios sueltos.\n"
             "\n"
             "Un detalle de método por si sale la pregunta de si esto es comparable con lo "
             "anterior. El brazo del modelo completo lo volvimos a correr como control, y dio "
             "idéntico a la corrida del sprint pasado, byte por byte en las cinco "
             "particiones. Así que comparar contra una corrida anterior que comparta "
             "particiones y semilla es válido por construcción, y en el otro sentido, repetir "
             "algo con la misma semilla no aporta evidencia nueva.\n"
             "\n"
             "Con eso cierro el encargo, y paso a lo que sí movió el plan.")


def lam_pregunta_medible(prs):
    # ---- La pregunta y el estadístico, en una sola lámina ----
    # Fusión pedida por Ernesto el 5-ago: la lámina de la pregunta se quedaba en bullets (dos
    # paneles de hipótesis y una fila de fichas) y la del estadístico tenía el dibujo. Se
    # juntan, los dos paneles bajan a UNA línea, y lo que ocupa la lámina son las dos cintas
    # de parches reordenados, que es lo que hay que ver. Las hipótesis se cuentan hablando.
    # Los rótulos son los del pre-registro §2 y NO se asignan por cuál ganó: la primaria es
    # la del patólogo, o sea la que el resultado terminó refutando.
    s = content(prs, "La pregunta medible")
    _grupo(s, 0.36, TOP, 9.28, 0.58, fill=TEAL_CARD)
    add_textbox(s, 0.60, TOP, 8.80, 0.58, [
        ("«En mitosis los núcleos son finos y dispersos, y a los modelos se les escapan "
         "porque quizá esos parches no reciben atención suficiente.»",
         12, True, ONCO_DARK, F_BODY, PP_ALIGN.CENTER)], anchor=MSO_ANCHOR.MIDDLE)
    # Corrección R1 (decimoctava pasada): la línea decía «se mira dónde caen los 163
    # marcados» y a diez centímetros mostraba 0,89, que es el número de los 28 de mitosis.
    # Los 163 son la unión de los siete grupos y NO tienen AUC en ningún artefacto: mezclarían
    # números que van de 0,15 a 0,89. Ahora la línea nombra el grupo, y la segunda dice que
    # cada grupo tiene el suyo y que el de las cintas es el de mitosis.
    #
    # Las dos lecturas pre-registradas bajan de su renglón propio a este bloque: son parte de
    # cómo se llegó al número, no un ítem aparte. Rótulos del pre-registro §2, sin reasignar
    # por cuál ganó (la primaria es la del patólogo, o sea la que el resultado refutó).
    add_textbox(s, 0.36, TOP + 0.66, 9.28, 0.64, [
        ("Se ordenan los 4799 parches por atención y se mira dónde cayeron los 28 que "
         "contienen una mitosis marcada.", 12, True, INK, F_BODY, PP_ALIGN.CENTER),
        ("El estadístico es el AUC de ranking, que es la U de Mann-Whitney normalizada. Cada "
         "grupo de tejido tiene el suyo; el de las cintas es el de mitosis.",
         9.5, False, GRIS_BODY, F_BODY, PP_ALIGN.CENTER),
        ("Las dos lecturas quedaron registradas antes de medir: la del patólogo, que los "
         "marcados no rankearían mejor que el azar, y la alternativa, que sí.",
         9.5, False, GRIS_BODY, F_BODY, PP_ALIGN.CENTER)])
    # El eje «más atención / menos atención» va una sola vez, debajo de las dos cintas: el
    # orden es el mismo y repetirlo bajo cada una lo vuelve ruido.
    # Los rótulos de las cintas eran `_rot_label` a 270°, y se PISABAN entre sí: un rótulo
    # rotado ocupa a lo alto lo que mide de ancho (1,60"), y las dos cintas están a 0,56" una
    # de otra. El bbox que reporta el shape es el de antes de rotar, así que la auditoría no
    # podía verlo ([[deck-qa-puntos-ciegos-chequeo]]) y salió del rasterizado. Ahora van
    # horizontales en la calle de la izquierda, que para eso se corrieron las cintas.
    ct1, ct2, CH = TOP + 1.38, TOP + 1.94, 0.42
    for ct, txt, col in ((ct1, "SI FUERA\nAZAR", GRIS_BODY),
                         (ct2, "LO\nOBSERVADO", ONCO_DARK)):
        add_textbox(s, 0.36, ct, 0.80, CH,
                    [(ln, 8, True, col, F_BODY, PP_ALIGN.RIGHT) for ln in txt.split("\n")],
                    anchor=MSO_ANCHOR.MIDDLE)
    cinta_ranking(s, 1.24, ct1, 7.10, marcados={2, 7, 11, 16, 21, 27, 31}, h=CH, ejes=False)
    add_textbox(s, 8.46, ct1, 1.20, CH,
                [("0,5", 15, True, GRIS_BODY, F_BODY, PP_ALIGN.CENTER)],
                anchor=MSO_ANCHOR.MIDDLE)
    cinta_ranking(s, 1.24, ct2, 7.10, marcados={0, 1, 2, 4, 5, 7, 9}, h=CH)
    add_textbox(s, 8.46, ct2, 1.20, CH,
                [("0,89", 15, True, ONCO_DARK, F_BODY, PP_ALIGN.CENTER)],
                anchor=MSO_ANCHOR.MIDDLE)
    # Pedido 6 de Ernesto (6-ago): la lámina tiene que decir con precisión QUÉ es el número,
    # porque de eso depende poder defender qué mide cada tipo de tejido. La cuenta de pares es
    # la definición del estadístico escrita con los números de esta lámina, y sale de
    # `atencion_vs_anotaciones.py:139`: n_neg = n_total − n_pos, o sea 4799 − 28.
    add_textbox(s, 0.36, TOP + 3.00, 9.28, 0.32, [
        ("28 parches con mitosis  ×  4771 con el resto de la lámina  =  133 588 pares  ·  "
         "en el 89 % de ellos gana el marcado", 13, True, TEAL_TITLE, F_BODY,
         PP_ALIGN.CENTER)], anchor=MSO_ANCHOR.MIDDLE)
    # Las tres propiedades que hay que poder decir. Van como tarjetas y no como lista: son
    # tres respuestas a tres preguntas distintas, no tres ítems de lo mismo.
    PROPS = [
        ("Contra qué se mide",
         "La lámina entera, con las marcas de los otros grupos adentro. Nunca un grupo "
         "contra otro."),
        ("Por qué son comparables",
         "Solo usa el orden, no la escala de la atención. El azar es 0,5 con 12 marcados o "
         "con 48."),
        ("Qué dice por debajo de 0,5",
         "Que el modelo evita ese tejido, no que lo ignore. El estadístico es simétrico."),
    ]
    pw = (9.28 - 0.40) / 3
    for i, (tit, cuerpo) in enumerate(PROPS):
        px = 0.36 + i * (pw + 0.20)
        _grupo(s, px, TOP + 3.42, pw, 0.74, fill=TEAL_CARD2)
        add_textbox(s, px + 0.14, TOP + 3.50, pw - 0.28, 0.22,
                    [(tit, 10.5, True, ONCO_DARK, F_BODY)])
        add_textbox(s, px + 0.14, TOP + 3.72, pw - 0.28, 0.40,
                    [(cuerpo, 9, False, INK, F_BODY)])
    notes(s, "La frase del patólogo tiene una virtud: se puede medir.\n"
             "Lo que medimos no es un mapa de calor, es un número, y sale de un ranking.\n"
             "Se ordenan los parches por atención y se pregunta dónde cayeron los 28 de "
             "mitosis.\n"
             "Si la atención no supiera nada daría 0,5; observamos 0,89.\n"
             "\n"
             "El origen de esta parte es la frase de arriba. Cuando revisamos con el patólogo por qué los "
             "modelos fallan en tasa mitótica, dijo que en mitosis los núcleos son finos y "
             "dispersos, y que se les escapan porque quizá esos parches no reciben atención "
             "suficiente. Esa frase tiene una virtud enorme: se puede medir. No es una opinión "
             "sobre el modelo, es una afirmación sobre dónde cae la atención, y la atención la "
             "podemos leer.\n"
             "\n"
             "El material es una sola lámina, la única que tenemos anotada, con cuatro mil "
             "setecientos noventa y nueve parches, de los cuales ciento sesenta y tres quedan "
             "debajo de alguna marca, repartidas en siete grupos de tejido, de los cuales el de "
             "mitosis tiene veintiocho. Es poco y lo digo "
             "de entrada: una lámina y un anotador describen, no establecen.\n"
             "\n"
             "Antes de correr nada dejamos escritas las respuestas posibles, y quiero "
             "subrayar que ninguna se acomodó después. La primera, la que registramos como "
             "primaria, es la del patólogo: los parches marcados no rankearían mejor que el "
             "azar, y eso apuntaría a que el problema está en cómo el modelo combina los "
             "parches. La segunda es que los marcados rankeen alto, y entonces el modelo sí "
             "mira donde hay que mirar y lo que se pierde está antes, en cómo queda "
             "representado cada parche. Y hubo una tercera, mixta: que las regiones grandes "
             "atrajeran atención y los objetos celulares no. Adelanto cuál quedó en pie, "
             "porque el orden en que las leo no es el orden en que salieron: fue la segunda. "
             "Las dejo rotuladas como estaban registradas, sin darlas vuelta ahora que sabemos "
             "el resultado.\n"
             "\n"
             "Ahora, cómo se mide, que es el punto que se pierde cuando uno cuenta esto "
             "rápido. Lo que medimos no es un mapa de calor. Los mapas los generamos, y los "
             "vamos a ver en un momento, pero son el subproducto. El resultado es un número, y "
             "el número sale de un ranking.\n"
             "\n"
             "El procedimiento es el de las dos cintas. Se toman todos los parches de la "
             "lámina y se ordenan por la atención que recibieron, de más a menos. Queda una "
             "fila larguísima, y cada casilla de esas cintas es un parche. Los oscuros son los "
             "que contienen una mitosis marcada. Si la atención no supiera nada de mitosis, los marcados "
             "estarían repartidos por toda la fila, tantos al principio como al final, y el "
             "número da cero coma cinco: esa es la cinta de arriba. Si la atención se "
             "concentrara justo ahí, se amontonarían a la izquierda y el número se acerca a "
             "uno: esa es la de abajo, y es la que observamos.\n"
             "\n"
             "Ese número tiene un nombre y una cuenta detrás, y los dos los quiero dejar "
             "dichos, porque es lo que hay que poder defender. El nombre es área bajo la curva "
             "de ranking, que es la U de Mann-Whitney normalizada, el estadístico clásico para "
             "comparar dos grupos sin suponer nada sobre la forma de sus distribuciones. La "
             "cuenta es la de la línea de abajo. Tomo los veintiocho parches que "
             "contienen una mitosis y los cruzo uno a uno con los cuatro mil setecientos "
             "setenta y uno restantes: ciento treinta y tres mil quinientos ochenta y ocho "
             "pares. En cada par miro cuál de los dos recibió más atención, y el número es la "
             "fracción de pares que gana el marcado. Ochenta y nueve de cada cien.\n"
             "\n"
             "De ahí salen las tres cosas de abajo, que son las que uso para leer la lámina "
             "que viene. La primera es contra qué se mide cada grupo. Del otro lado no está lo "
             "que quedó sin marcar: está la lámina entera menos ese grupo, y ahí adentro "
             "quedan los parches que el patólogo marcó como tumor, como estroma o como grasa. "
             "Cada grupo se mide contra todo lo demás, nunca contra otro grupo. La segunda es "
             "por qué se pueden comparar entre sí grupos de tamaños muy distintos: el número "
             "solo usa el orden, no la escala de la atención, así que también se puede "
             "comparar entre modelos que reparten su atención de manera distinta; y el valor "
             "de referencia es cero coma cinco siempre, con doce parches marcados o con "
             "cuarenta y ocho. La tercera es la que más se malinterpreta: quedar por debajo de "
             "cero coma cinco no significa que el modelo sea indiferente a ese tejido, "
             "significa que lo evita. El estadístico es simétrico, y un valor bajo dice que un "
             "parche cualquiera le gana casi siempre.\n"
             "\n"
             "Comparado con el mapa de calor, la ventaja está justamente en tener esa "
             "referencia: mirando un mapa uno no sabe decir si el rojo está donde corresponde "
             "o si está en todas partes.")


def lam_mapas(prs):
    # ---- Atención y marcas del patólogo ----
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
             "Los mapas son lo que uno recuerda de un trabajo así, y los muestro después del "
             "número a propósito.\n"
             "\n"
             "A la izquierda está la atención del modelo sobre la lámina: el rojo es mucha "
             "atención, el azul poca. A la derecha, las marcas del patólogo, cada color un tipo "
             "de tejido. Mirándolos de a dos uno ya intuye que las marcas caen en zonas "
             "calientes, pero intuir no es medir, y por eso el resultado es "
             "el número de la lámina anterior y no esta imagen.\n"
             "\n"
             "Al pie dejé de dónde sale todo esto, porque es la pregunta natural. Es una lámina "
             "de nuestra cohorte privada, escaneada a veinte aumentos, de la que salen cuatro "
             "mil setecientos noventa y nueve parches; las marcas son sesenta y un polígonos "
             "que el patólogo dibujó, de los cuales veintiséis son mitosis. Veintiséis marcas "
             "dibujadas y veintiocho parches con mitosis adentro, que no es lo mismo; en dos "
             "láminas más cuento de dónde sale esa diferencia. Y su etiqueta en "
             "nuestros datos es tasa mitótica alta, que es coherente con esas veintiséis marcas.\n"
             "\n"
             "Una aclaración sobre lo que están viendo, porque la lámina completa tiene una "
             "particularidad. Se escaneó en dos regiones separadas, y el procesamiento extrajo "
             "parches de las dos: dos mil trescientos tres de una y dos mil cuatrocientos "
             "noventa y seis de la otra. Los ciento sesenta y tres parches marcados caen "
             "todos en la "
             "segunda, así que es la que proyecto acá; la otra no tiene ninguna.\n"
             "\n"
             "Eso abre un problema serio, y fuimos a cerrarlo. Acuérdense de cómo se arma el "
             "número: cada parche marcado compite contra todos los demás de la lámina, y entre "
             "esos demás está la otra región entera, que no tiene ninguna marca. Si la región "
             "de abajo recibiera "
             "de por sí más atención que la de arriba, los parches marcados ganarían por estar "
             "donde están y no por tener una mitosis adentro: el número no estaría midiendo las "
             "marcas, estaría midiendo la región. Lo medimos: la región anotada contra la otra da entre "
             "cero coma cuarenta y seis y cero coma cuarenta y ocho, o sea que recibe algo "
             "menos de "
             "atención, no más. Y después repetimos todo confinando la medición a esa sola "
             "región, con lo cual la pregunta de la región deja de existir: el efecto no baja, "
             "sube, de cero coma ochenta y nueve a cero coma noventa.")


def lam_escalera(prs):
    # ---- El resultado: la escalera de los siete grupos ----
    s = content(prs, "El resultado, grupo por grupo")
    barras_ranking(s, 0.36, TOP + 0.52, 9.28, 2.30, ESCALERA)
    # Hallazgo R3 de la decimoctava pasada: siete barras del mismo grosor sugieren siete
    # números de la misma calidad, y el ancho del IC va de 0,10 a 0,33. El bigote ya se
    # dibuja; lo que faltaba es el renglón que lo explique y el caso que obliga a leerlo.
    add_textbox(s, 0.36, TOP + 2.88, 9.28, 0.44, [
        ("El bigote es el intervalo al 95 %: cuánta precisión da el tamaño de cada grupo.",
         11.5, True, INK, F_BODY, PP_ALIGN.CENTER),
        ("Estroma (n = 12) lo tiene tres veces más ancho que tejido adiposo (n = 27), y con "
         "ese ancho la lámina no puede distinguir estroma evitado de estroma atendido.",
         9.5, False, GRIS_BODY, F_BODY, PP_ALIGN.CENTER)])
    # Las dos tarjetas repetían el 0,890 (que la barra ya dice) y el percentil (que está en el
    # guion). Pedido 6: acá van las DOS INCERTIDUMBRES, que es lo que el deck contaba a
    # medias. Son cosas distintas y la segunda es la grande ([[auc-atencion-dos-incertidumbres]]).
    _grupo(s, 0.36, TOP + 3.40, 4.54, 0.74, fill=TEAL_CARD)
    add_textbox(s, 0.36, TOP + 3.40, 4.54, 0.74, [
        ("± 0,039   si cambia el modelo", 16, True, ONCO_DARK, F_BODY, PP_ALIGN.CENTER),
        ("dispersión entre los 4 checkpoints, con las marcas fijas", 9.5, False, GRIS_BODY,
         F_BODY, PP_ALIGN.CENTER)], anchor=MSO_ANCHOR.MIDDLE)
    _grupo(s, 5.10, TOP + 3.40, 4.54, 0.74, fill=TEAL_CARD2)
    add_textbox(s, 5.10, TOP + 3.40, 4.54, 0.74, [
        ("± 0,080   si cambian las marcas", 16, True, TEAL_TITLE, F_BODY, PP_ALIGN.CENTER),
        ("el bigote de mitosis: depende del n del grupo, y es la grande", 9.5, False,
         GRIS_BODY, F_BODY, PP_ALIGN.CENTER)], anchor=MSO_ANCHOR.MIDDLE)
    notes(s, "Una barra por grupo de tejido: cuánto atiende el modelo lo que el patólogo marcó "
             "de cada cosa.\n"
             "Mitosis queda arriba de todo, y por encima incluso de tumor.\n"
             "La escalera baja hasta la grasa, que el modelo evita activamente.\n"
             "El orden no lo diseñó nadie: salió de medir, y tiene sentido clínico.\n"
             "El bigote dice cuánta precisión da el n de cada grupo: estroma no es un dato.\n"
             "\n"
             "El resultado hay que leerlo entero, y no quedarse con el primer "
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
             "muy lejos de la línea del azar. Dicho de la otra forma, la que se entiende "
             "sola: el parche de mitosis típico está dentro del nueve por ciento más atendido de "
             "la lámina.\n"
             "\n"
             "Pero lo que convence no es ese número solo, es la escalera completa, porque "
             "muestra que la atención tiene estructura y que la estructura tiene sentido "
             "clínico. Abajo de todo está el tejido adiposo, en cero coma quince. Ese número "
             "está bien por debajo del azar, y eso no significa que el modelo lo ignore: significa "
             "que lo evita, que un parche de grasa recibe sistemáticamente menos atención que "
             "un parche tomado al azar, que es exactamente lo que uno querría. Después los "
             "linfocitos, también por debajo. Y arriba, tumor y núcleos de "
             "alto grado alrededor de cero coma ochenta y tres, con mitosis por encima de los "
             "dos.\n"
             "\n"
             "Ese orden no lo diseñó nadie: salió de medir. Y que mitosis quede por encima de "
             "tumor es más de lo que esperábamos, porque tumor son regiones grandes y bien "
             "delimitadas, mucho más fáciles de acertar que veintiocho parches sueltos.\n"
             "\n"
             "Ahora, los bigotes, porque sin ellos esta lámina se sobre-lee. Siete barras del "
             "mismo grosor invitan a pensar que son siete números de la misma calidad, y no lo "
             "son. Acá hay dos incertidumbres distintas, y mezclarlas es fácil. La primera es "
             "la que veníamos contando, el más menos cero coma cero treinta y nueve de mitosis: "
             "mide qué pasa si cambio de modelo, con las marcas del patólogo fijas. La segunda "
             "es el bigote, y mide algo distinto: qué pasaría si el patólogo hubiera marcado "
             "otras mitosis, con el modelo fijo. Esa depende del tamaño del grupo, y es la "
             "grande: en mitosis vale más menos cero coma cero ochenta, el doble que la otra.\n"
             "\n"
             "El caso que obliga a mirarlos es el estroma. Con doce parches marcados su bigote "
             "va de cero coma treinta y siete a cero coma setenta, así que la lámina no puede "
             "distinguir estroma evitado de estroma atendido. Yo venía diciendo que el estroma "
             "queda justo en el azar, que es donde uno esperaría algo que no informa ni "
             "estorba, y eso era leer como dato lo que en realidad es una ausencia de dato. "
             "Mitosis, en cambio, aguanta: su bigote no toca el cero coma cinco ni de lejos.\n"
             "\n"
             "Dos advertencias más sobre esta lámina. Los grupos de abajo no son un control "
             "negativo: son regiones marcadas con otro criterio, y que la grasa dé cero coma "
             "quince muestra que la atención distingue tejido, no que el método esté validado. Y "
             "los núcleos de alto grado, el segundo renglón, no aguantan el estirón: dan un "
             "número parecido, pero cuando lo sometemos a las pruebas que vienen ahora, solo uno "
             "de cuatro modelos lo pasa. Además es el segundo bigote más ancho de los siete, "
             "así que hay dos razones independientes para no presentarlo como resultado.")


def lam_28_parches(prs):
    # ---- Dónde caen los 28 parches ----
    s = content(prs, "Los 28 parches de mitosis")
    # Mismo criterio que la lámina anterior: cada caja con la relación de aspecto exacta de
    # su figura, y las dos a la MISMA altura, para que los pies queden en una sola línea.
    # Pedido 6 de Ernesto (6-ago): acá va la cuenta que lleva de 26 marcas a 28 parches. Va
    # ARRIBA, pegada al título, porque el título dice 28 y la pregunta nace ahí. El costo es
    # que las dos figuras bajan de 3,34 a 2,68 de alto (−20 %); si se prefiere el tamaño
    # anterior, lo que hay que mover es esta banda, no las figuras.
    #
    # El neto de +2 es coincidencia de ESTA lámina y no se presenta como regla: son dos
    # efectos grandes que casi se cancelan (`atencion_vs_patologo/resultados.md` §1.a).
    cadena_cuenta(s, 0.36, TOP, 9.28, CUENTA_26_28, h=0.32, fs=13)
    FIG_H = 2.68
    reg_w = FIG_H * (800 / 676.0)
    zoom_w = FIG_H * (453 / 552.0)
    FIG_T = TOP + 0.74
    add_image_fit(s, FIG_MITOSIS, 0.36, FIG_T, reg_w, FIG_H, align="top")
    add_image_fit(s, FIG_ZOOM, 0.36 + reg_w + 0.15, FIG_T, zoom_w, FIG_H, align="top")
    # Una línea: a dos renglones el segundo cae bajo la barra de remate y queda tachado.
    caption(s, 0.36, FIG_T + FIG_H + 0.04, reg_w,
            "la región anotada, con los 28 parches en blanco", size=9.5)
    caption(s, 0.36 + reg_w + 0.15, FIG_T + FIG_H + 0.04, zoom_w, "el detalle del recuadro",
            size=9.5)
    # El panel de dos renglones baja a UNA línea, y sin caja: un panel alrededor de una sola
    # frase es una caja alrededor de nada, y acá la lámina la manda la figura.
    COL_L = 0.36 + reg_w + zoom_w + 0.46
    COL_W = 9.64 - COL_L
    add_textbox(s, COL_L, FIG_T + 0.10, COL_W, 1.10,
                [("Los parches blancos caen sobre el rojo, no sobre el borde ni sobre el "
                  "azul.", 13.5, True, ONCO_DARK, F_BODY)], anchor=MSO_ANCHOR.MIDDLE)
    # La escala, que es la causa de fondo de la cuenta de arriba Y el puente a la lámina
    # siguiente: lo que el modelo comprime a un vector es un parche que es casi todo otra cosa.
    add_textbox(s, COL_L, FIG_T + 1.34, COL_W, 1.20, [
        ("Una mitosis ocupa entre el 2 % y el 4 % del parche.", 12, True, TEAL_TITLE, F_BODY),
        ("36 px de lado contra los 256 del parche. De ahí que 10 de las 26 caigan sobre un "
         "borde, y que lo que el modelo comprime sea un parche que es casi todo otra cosa.",
         9.5, False, GRIS_BODY, F_BODY)])
    takeaway_bar(s, "Y aun así, este modelo predice mal esta lámina.", t=TOP + 3.78,
                 size=13)
    notes(s, "Arriba, de dónde salen 28 parches si el patólogo dibujó 26 marcas.\n"
             "El mismo resultado, pero puesto donde se ve de un vistazo.\n"
             "En blanco, los 28 parches que contienen una mitosis marcada.\n"
             "Debajo, en colores, dónde puso la atención el modelo.\n"
             "Los blancos caen sobre el rojo, y el rojo es donde el modelo mira.\n"
             "\n"
             "Arriba dejé una cuenta que prefiero despejar primero, porque los dos números "
             "conviven en todo el trabajo y parecen contradecirse. El patólogo dibujó "
             "veintiséis marcas de mitosis, y yo vengo hablando de veintiocho parches. No es "
             "un error de ninguno de los dos: son unidades distintas, y lo que las separa son "
             "dos efectos grandes que casi se cancelan. Diez de las veintiséis marcas caen "
             "sobre el borde entre dos parches, así que ocupan dos y suman uno cada una. Y "
             "siete parches tienen más de una mitosis adentro, lo que resta ocho. Veintiséis "
             "más diez menos ocho, veintiocho. Que el neto dé más dos es casualidad de esta "
             "lámina y no una regla: en otra con las marcas más dispersas la diferencia sería "
             "bastante mayor.\n"
             "\n"
             "La causa de fondo es de escala, y es la que quiero dejar dicha antes de pasar. "
             "Una marca de "
             "mitosis mide treinta y seis píxeles de lado y el parche mide doscientos cincuenta "
             "y seis, así que una mitosis ocupa entre el dos y el cuatro por ciento del área "
             "del parche. Con ese tamaño, que diez de veintiséis caigan sobre un borde deja de "
             "sorprender. Y queda planteado lo otro: eso que el modelo comprime a un vector es "
             "un parche que, en su enorme mayoría, es otra cosa.\n"
             "\n"
             "Ahora sí, la escalera anterior puesta donde se ve de un vistazo. Es la imagen que "
             "a mí me terminó de convencer.\n"
             "\n"
             "Hay dos capas superpuestas. El fondo es el "
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
             "Y ahora la parte incómoda. Este modelo, el que produjo este "
             "mapa, se equivoca al clasificar esta lámina.")


def lam_mira_responde(prs):
    # ---- Mira bien y responde mal ----
    # Tabla rehecha el 5-ago: Ernesto no entendía a qué modelo correspondía cada fila, ni
    # por qué de la corrida de cinco particiones aparecían dos y no cinco. La columna ahora
    # nombra el DATASET DE ENTRENAMIENTO con su tamaño (contado sobre los splits reales, ver
    # CKPTS_TABLA) y el pie dice por qué son esas dos particiones: son las únicas donde esta
    # lámina cayó en validación.
    s = content(prs, "Mira bien y responde mal")
    add_textbox(s, 0.36, TOP, 9.28, 0.56, [
        ("Cuatro modelos de tasa mitótica, 4 clases. La lámina cayó en validación en los "
         "cuatro: ninguno la tuvo en entrenamiento.", 12, True, GRIS_BODY, F_BODY,
         PP_ALIGN.CENTER),
        ("La etiqueta verdadera es score_3, tasa mitótica alta, coherente con las 26 marcas "
         "de mitosis.", 11, False, GRIS_BODY, F_BODY, PP_ALIGN.CENTER)])
    simple_table(s, 0.50, TOP + 0.66, 9.00,
                 ["Entrenado con", "Qué respondió", "Confianza en score_2",
                  "AUC de atención"],
                 CKPTS_TABLA,
                 col_fracs=[0.34, 0.20, 0.23, 0.23], row_h=0.34, fs=11, destacar=2)
    caption(s, 0.50, TOP + 2.42, 9.00,
            "Los folds 0 y 2 son los dos únicos de la corrida de cinco donde esta lámina no "
            "quedó en entrenamiento.", size=9.5, col=GRIS_BODY)
    # Los dos paneles se funden en UNA lectura: la tabla ya dice quién falla y quién mira
    # mejor, así que enumerarlo al lado era leerla en voz alta. Lo que hay que agregar es la
    # consecuencia, y eso es una frase. El resto (los 8 modelos que sí la vieron, el cambio
    # de diagnóstico) baja al guion.
    add_textbox(s, 0.36, TOP + 2.76, 9.28, 0.70, [
        ("El que mejor mira es el que más se equivoca: el problema no está en elegir los "
         "parches, sino en lo que queda del parche una vez comprimido.",
         13.5, True, TEAL_TITLE, F_BODY, PP_ALIGN.CENTER)], anchor=MSO_ANCHOR.MIDDLE)
    takeaway_bar(s, "Ese desacople entre mirar bien y responder mal es el resultado, y es "
                    "lo que reordenó el trabajo que sigue.", t=TOP + 3.52, size=12.5)
    notes(s, "La lámina tiene tasa mitótica alta, y tres de los cuatro modelos la subestiman.\n"
             "La última columna es cuánto mira cada uno las mitosis: todos miran bien.\n"
             "La fila destacada es el que mejor mira, y es el que responde peor.\n"
             "Los modelos que sí la tenían en entrenamiento la aciertan, así que no es una "
             "lámina rara.\n"
             "\n"
             "El desenlace no lo esperábamos, y hace que esta medición valga más que la "
             "respuesta a la pregunta original.\n"
             "\n"
             "La lámina tiene tasa mitótica alta, que es coherente con las veintiséis mitosis "
             "que el patólogo marcó. Tres de los cuatro modelos que no la vieron en "
             "entrenamiento responden que tiene tasa intermedia. O sea que se equivocan, y se "
             "equivocan hacia abajo: subestiman.\n"
             "\n"
             "Lo llamativo es la fila destacada. Ese modelo es el que mejor mira de los cuatro, "
             "con cero coma noventa y tres de atención sobre las mitosis, y es también el que "
             "se equivoca con más convicción, con un setenta y uno por "
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


def lam_controles(prs):
    # ---- Los cuatro controles ----
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

    # Segunda pasada sobre el dibujo, 5-ago: Ernesto dijo que seguía sin quedar claro. Lo
    # que fallaba era que la lámina y la zona caliente eran dos rectángulos, que la
    # traslación se leía como cuatro manchas sueltas y que el color lo explicaba una leyenda
    # al pie. Ahora la zona de atención tiene forma, las copias cuelgan de la original por
    # una línea punteada, y los rótulos van pegados a lo que nombran. Detalle en
    # `mapa_traslaciones`.
    PL, PT, PW, PH = 0.36, 1.90, 5.60, 1.70
    mapa_traslaciones(s, PL, PT, PW, PH)

    # La distribución de los nulos contra el valor observado, que es el argumento entero:
    # la brecha entre la banda y la marca oscura. La banda va rotulada CON SUS VALORES, que
    # es lo que dice que el nulo ya parte alto y no del azar.
    nube_traslaciones(s, PL, PT + PH + 0.08, PW, 0.38, lo=0.60, hi=0.95, banda=(0.67, 0.75),
                      obs=0.890, rot_banda="las ~440 traslaciones: 0,67 a 0,75",
                      rot_obs="en su lugar real")

    # Los otros tres controles, a una línea cada uno.
    CL, CT, CW = 6.16, 1.90, 3.48
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
                    "una lámina y un anotador describen, no establecen.", t=4.72, size=12.5)
    notes(s, "Cuatro cosas fuimos a descartar antes de creerle al número.\n"
             "La primera es la del dibujo: mover la mancha de marcas a otro lado de la lámina "
             "y ver si el número aguanta.\n"
             "De unas 440 posiciones, ninguna llegó a lo que da en su lugar real.\n"
             "Los otros tres controles están a la derecha, y ninguno explica el resultado.\n"
             "\n"
             "Un número alto sin controles no vale gran cosa, así que fuimos a descartar "
             "cuatro.\n"
             "\n"
             "La primera es la más importante y es una lección que me llevo, así que la dibujé. "
             "La manera obvia de poner a prueba un resultado así es barajar al azar cuáles "
             "parches están marcados y ver cuántas veces sale un valor tan alto por casualidad. "
             "Eso lo hicimos, da significativo, y no sirve para nada: también da significativo "
             "donde no debería. El motivo es que las marcas están pegadas unas a otras y la "
             "atención también viene en manchas, así que cualquier mancha compacta le gana a un "
             "sorteo que rompe la contigüidad.\n"
             "\n"
             "La prueba honesta es la del dibujo. El recuadro grande es la lámina, y las "
             "manchas celestes son donde el modelo concentra su atención. El grupito oscuro y "
             "relleno son las marcas en el lugar donde realmente están. Los tres grupitos "
             "vacíos que cuelgan de él por una línea punteada son esa misma mancha, con la "
             "misma forma y el mismo tamaño, corrida a otro lado; hicimos eso unas "
             "cuatrocientas cuarenta veces, en todas las posiciones donde entra completa. "
             "Miren la copia de abajo a la izquierda, que cae otra vez sobre el celeste: esa "
             "es la que explica lo que viene ahora.\n"
             "\n"
             "Y abajo está lo que salió de esas cuatrocientas cuarenta. La banda gris es dónde "
             "caen las traslaciones: entre cero coma sesenta y siete y cero coma setenta y "
             "cinco. Fíjense que no parten del azar, y eso tiene una explicación que el dibujo "
             "muestra: si uno mueve la mancha dentro del tumor, como pasa con una de las copias "
             "huecas, sigue "
             "cayendo en zona de atención alta, así que el nulo ya es exigente de entrada. La "
             "marca oscura de la derecha es el valor en el lugar real. Ninguna de las "
             "cuatrocientas cuarenta llegó ahí, y esa brecha es el resultado.\n"
             "\n"
             "Los otros tres los paso rápido. El de la región ya lo conté. La memorización: los "
             "cuatro modelos no tenían esta lámina en su entrenamiento, y podemos medir cuánto "
             "ayudaría haberla tenido, porque hay otros que sí; la diferencia es de cero coma "
             "cero cincuenta y seis, chica al lado de la distancia que hay hasta el azar. Y el "
             "cuarto "
             "juega a nuestro favor sin que hiciéramos nada: el patólogo marca donde la "
             "evidencia es clara, no marca todas las mitosis, y las que no marcó quedan "
             "contadas como si no tuvieran nada, lo cual empuja el número hacia el azar. El "
             "cero coma ochenta y nueve es creíble justamente porque el sesgo lo empuja para "
             "abajo.\n"
             "\n"
             "Queda lo que el resultado no dice, que también estaba pre-registrado. "
             "Sigue en pie lo que dije al empezar: una lámina y un anotador describen, no "
             "establecen. No estamos diciendo que la "
             "atención de nuestros modelos esté bien en general, ni damos por buenos los "
             "nombres de tejido que le pusimos a las unidades internas la vez pasada, que "
             "siguen esperando el visto bueno de un patólogo. Y un parche sin marca que reciba "
             "mucha atención no es un error del modelo: puede ser tejido que el patólogo "
             "simplemente no marcó.")


def lam_simil_propone(prs):
    # ---- Qué propone + la figura del paper ----
    # Rediseño del 5-ago (pedido de Ernesto): los bullets al mínimo para que la figura del
    # paper crezca todo lo que da. La figura es más ancha que alta (ar 3,195), así que en la
    # caja anterior de 9,56 x 2,52 la limitaba el ALTO y se dibujaba a 8,05 x 2,52. Ahora la
    # limita el ancho de la lámina y sale a 9,60 x 3,00, un 19 % más de lado. El bloque de
    # tres líneas de arriba baja a una frase y la barra de remate se retira: su texto ERA esa
    # frase, y repetirla costaba media pulgada de figura.
    s = content(prs, "SI-MIL: qué propone")
    add_textbox(s, 0.36, TOP, 9.28, 0.50, [
        ("Que la explicación SEA la predicción: predecir con una combinación lineal de "
         "mediciones de núcleos que tienen nombre de patología, y dejar la red profunda como "
         "el maestro que enseña dónde mirar.", 13.5, True, TEAL_TITLE, F_BODY,
         PP_ALIGN.CENTER)], anchor=MSO_ANCHOR.MIDDLE)
    FIG_H_S3 = 9.60 / 3.195
    add_image_fit(s, FIG2_FULL, 0.20, TOP + 0.56, 9.60, FIG_H_S3, align="top")
    pie_lineas(s, 0.36, TOP + 0.56 + FIG_H_S3 + 0.08, 9.28, [
        "Taming Deep MIL for Self-Interpretability in Gigapixel Histopathology · Kapse et al., "
        "CVPR 2024.",
        "(a) el recorrido completo, de la lámina a las dos predicciones · (b) y (c) el detalle "
        "de cada rama.",
    ], size=9)
    notes(s, "La ambición del paper: que la explicación SEA la predicción.\n"
             "Dos caminos que salen de la misma lámina: uno mide, el otro selecciona.\n"
             "La rama profunda no llega a producción, se descarta entera.\n"
             "\n"
             "Cierro con el paper que había quedado encargado, y viene bien justo detrás de "
             "esto, porque llega al mismo problema por otro camino. Nosotros acabamos de mirar un "
             "modelo ya entrenado para ver dónde puso la atención; el paper propone construir "
             "el modelo de manera que no haya que ir a mirarlo.\n"
             "\n"
             "El nombre completo habla de domesticar un modelo profundo "
             "para que se explique solo, y eso resume bien la ambición: no acompañar la "
             "predicción con una explicación, sino conseguir que la explicación sea la "
             "predicción.\n"
             "\n"
             "La idea cabe en la frase de arriba, y tiene tres consecuencias. "
             "La red profunda deja de predecir, y su único producto pasa a ser una "
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


def lam_simil_ramas(prs):
    # ---- Las dos ramas y el puente, en un solo diagrama ----
    # Fusión pedida por Ernesto el 5-ago: las tres láminas de ecuaciones (las dos entradas,
    # el orden de las operaciones y el puente Top-K) pasan a UN diagrama, sin tablas. Lo que
    # se pierde de la lámina se cuenta hablando, que es el método de los recortes anteriores.
    # Las dos tablas que había (los dos anchos, y α contra β) salen enteras: su contenido es
    # una frase cada una y ocupaban media lámina.
    s = content(prs, "Las dos ramas y el puente")
    y1, y2, BH = TOP + 0.06, TOP + 0.70, 0.52
    # entrada
    _proc(s, 0.36, (y1 + y2) / 2 + BH / 2 - 0.26, 1.20, BH, "N parches", size=11,
          dim="una lámina")
    _conn(s, 1.56, (y1 + y2) / 2 + BH / 2, 1.86, y1 + BH / 2)
    _conn(s, 1.56, (y1 + y2) / 2 + BH / 2, 1.86, y2 + BH / 2)
    # rama profunda
    _proc(s, 1.86, y1, 1.64, BH, "Extractor profundo", dim="CONCH en nuestro caso", size=10)
    _dato(s, 3.68, y1 + 0.04, 1.52, 0.44, "g_i ∈ ℝ^D   ·   D = 512", size=10)
    _proc_claro(s, 5.38, y1, 2.04, BH, "Proyector + atención", size=10, dim="ecuación (1)")
    _dato(s, 7.60, y1 + 0.04, 0.96, 0.44, "α_i", size=11)
    _dim(s, 8.66, y1 + 0.13, 1.24, "un peso por parche", size=9, align=PP_ALIGN.LEFT)
    for xa, xb in ((3.50, 3.68), (5.20, 5.38), (7.42, 7.60)):
        _conn(s, xa, y1 + BH / 2, xb, y1 + BH / 2)
    # rama de mediciones
    _proc_claro(s, 1.86, y2, 1.64, BH, "PathExpert", size=10, dim="sobre el mapa de núcleos")
    _dato(s, 3.68, y2 + 0.04, 1.52, 0.44, "f_i ∈ ℝ^d   ·   d = 246", size=10)
    _conn(s, 3.50, y2 + BH / 2, 3.68, y2 + BH / 2)
    # El bloque termina antes de x = 7,90: por ahí baja el conector que lleva la atención al
    # Top-K, y con el ancho completo la línea le cruzaba el segundo renglón por el medio.
    add_textbox(s, 5.38, y2 + 0.02, 2.48, 0.48, [
        ("Mediciones con nombre clínico sobre el mapa de núcleos que produce el "
         "segmentador.", 9.5, False, INK, F_BODY)])
    # el puente: la atención del camino de arriba baja y elige los parches del de abajo
    yb = TOP + 1.48
    _conn(s, 8.08, y1 + 0.48, 8.08, yb - 0.16, arrow=False)
    _conn(s, 8.08, yb - 0.16, 1.46, yb - 0.16, arrow=False)
    _conn(s, 1.46, yb - 0.16, 1.46, yb)
    _proc_claro(s, 0.36, yb, 2.20, BH, "Top-K sobre la atención", size=10,
                dim="K = 20 parches   (3)")
    _conn(s, 2.56, yb + BH / 2, 3.00, yb + BH / 2)
    _dato(s, 3.00, yb + 0.04, 1.30, 0.44, "20 índices", size=10)
    _conn(s, 4.30, yb + BH / 2, 4.74, yb + BH / 2)
    _proc(s, 4.74, yb, 2.20, BH, "20 × 246 = 4920", size=11,
          dim="las 20 filas de mediciones")
    add_textbox(s, 7.14, yb + 0.02, 2.76, 0.48, [
        ("En una lámina de diez mil parches, los más de cinco millones de números del "
         "camino profundo se descartan enteros.", 9.5, False, GRIS_BODY, F_BODY)])
    # el orden de las dos operaciones, que es la ecuación 2 y lo que nos toca a nosotros
    yo = TOP + 2.16
    pa = panel(s, 0.36, yo, 4.54, None, "Orden A, el de nuestro modelo", TEAL_TITLE,
               ["Ŷ = C( Σ_i α_i · g̃_i )",
                "Funde primero y clasifica después: queda un logit y ningún desglose por "
                "parche."],
               TEAL_SQ, tsize=13, bsize=10.5, markup=True)
    pb = panel(s, 5.10, yo, 4.54, None, "Orden B, la ecuación 2", ONCO_DARK,
               ["Ŷ = ψ( Σ_i C( α_i · g̃_i ) )",
                "Clasifica cada parche y suma después: el mismo logit, y además N "
                "contribuciones con signo."],
               ONCO_DARK, fill=TEAL_CARD, tsize=13, bsize=10.5, markup=True)
    alto_ord = max(Emu(sp.height).inches for sp in (pa, pb))
    for sp in (pa, pb):
        sp.height = Inches(alto_ord)
    takeaway_bar(s, "Nuestro modelo es el orden A. Y su atención sale de una softmax, así "
                    "que dice CUÁNTO mira cada parche, nunca hacia qué clase empuja.",
                 t=yo + alto_ord + 0.16, size=12)
    notes(s, "Un solo diagrama para las tres ecuaciones del principio.\n"
             "Arriba, dos descripciones de los mismos parches: una que eligió una red y otra "
             "que eligió la patología.\n"
             "En el medio, el puente: la atención de arriba elige veinte parches y esos "
             "veinte se leen abajo.\n"
             "Abajo, el orden de dos operaciones, que es lo que nos toca a nosotros.\n"
             "\n"
             "Es el mismo recorrido de la figura anterior, redibujado con lo que a nosotros "
             "nos interesa: los anchos y la notación.\n"
             "\n"
             "Arriba está la entrada, con los dos caminos que acabamos de ver, y lo que agrega "
             "el dibujo son los números. Por el de arriba cada parche queda como un vector de "
             "quinientos doce números, que es el ancho que ya usamos nosotros. Por el de abajo "
             "queda "
             "como doscientas cuarenta y seis mediciones con nombre: solidez, densidad, mezcla "
             "de tipos celulares. Mismos parches y mismo orden; lo único que cambia es el "
             "ancho y quién eligió esos números.\n"
             "\n"
             "Fíjense en la convención de la notación, que el paper usa sin remarcarla y que "
             "confunde si se pasa por alto: el ancho del camino profundo va en mayúscula y el "
             "del otro en minúscula, la misma letra. Y de paso queda ordenada la relación "
             "entre los dos papers que habían quedado encargados: el mapa de núcleos del que "
             "salen esas mediciones lo produce el segmentador, que es el otro. No son dos "
             "ángulos, son la misma cadena.\n"
             "\n"
             "La primera ecuación es la caja clara de la derecha y tiene dos pasos. Primero un "
             "proyector, que reescribe el vector midiéndolo contra unas varas que se aprenden; "
             "en nuestro modelo es la primera capa lineal con su activación. Después la "
             "atención: hay un presupuesto de importancia del cien por ciento para repartir "
             "entre todos los parches, y el módulo convierte el puntaje crudo de cada uno en "
             "una fracción de ese total. De ahí sale algo que vale la pena releer con lo que "
             "acabamos de ver: la atención de un parche depende de cuántos y cuáles sean los "
             "demás. No es una propiedad del parche, es su tajada.\n"
             "\n"
             "El renglón del medio es el puente: la caja amarilla, puesta en limpio. "
             "La atención que calculó el camino de "
             "arriba se usa para quedarse con los veinte parches más atendidos, y esos veinte "
             "índices son lo único que ese camino aporta. En una lámina de diez mil parches "
             "eso significa que más de cinco millones de números se descartan enteros. Los "
             "veinte índices se aplican sobre la otra rama, quedan veinte filas de doscientas "
             "cuarenta y seis mediciones, y sobre esos cuatro mil novecientos veinte números "
             "se predice. Y no es tan directo como suena: quedarse con los veinte mayores es "
             "una operación escalonada, que no tiene derivada, así que usan una versión "
             "perturbada que sí deja pasar el gradiente.\n"
             "\n"
             "Los dos cuadros de abajo son la ecuación dos, que es la que cuesta porque parece "
             "decir algo obvio. En realidad dice algo muy específico sobre el orden de dos "
             "operaciones. En el de la izquierda se pesa cada parche por su atención, se suman "
             "todos y queda una única ficha promedio, y a esa ficha se le aplica el "
             "clasificador. Es una licuadora: se echan las frutas en su proporción, se licúa, "
             "se prueba el jugo y se dictamina. En el de la derecha se pesa cada parche por su "
             "atención igual que antes, pero el clasificador se aplica a cada uno por "
             "separado, y recién después se suma. Se prueba cada fruta ya medida en su "
             "proporción, se anota su puntaje y se suma la columna.\n"
             "\n"
             "Escrita, la diferencia es solamente dónde cierra el paréntesis, y el número que "
             "sale es el mismo por los dos caminos. Lo que cambia es qué queda en memoria "
             "cuando el modelo termina. Arriba queda una ficha fundida y ningún desglose; "
             "abajo no hay ficha fundida, pero quedan tantos puntajes como parches, con signo, "
             "que suman exacto el resultado. Una vez licuado el jugo no hay manera de "
             "separarlo en frutas: uno se acuerda de las proporciones, pero la proporción dice "
             "cuánta fruta se puso, no si esa fruta era dulce o ácida.\n"
             "\n"
             "Fui a verificar dónde cae nuestro modelo, línea por línea, y cae en el de la "
             "izquierda: funde y después clasifica, con dos diferencias menores, que nuestra "
             "atención es por clase y que tenemos ramas de instancia que en esta formulación "
             "no existen. Y el remate es el punto que más nos toca. Uno podría pensar que la "
             "atención rescata lo que ese orden pierde, y no: sale de un reparto del cien por "
             "ciento, así que todos sus valores son positivos, y un número positivo expresa "
             "cuánto, nunca hacia dónde. El caso que le preocupa al paper es un parche que se "
             "lleva más de la mitad de la atención y que al mismo tiempo es el que más empuja "
             "en contra: el mapa de calor le pinta un rojo intenso, y quien lo mira lee que "
             "ahí estaba la evidencia. Esto acota lo que podemos decir de los mapas que "
             "proyecté hace un rato: que la atención caiga sobre las mitosis dice que el "
             "modelo las mira, y no dice hacia dónde las está usando.")


def lam_simil_reporte(prs):
    # ---- Del embudo al reporte: las ecuaciones 4 a 10, dibujadas ----
    # Rediseño del 5-ago (pedido de Ernesto): esta lámina era una tabla de siete ecuaciones
    # con su glosa al lado, o sea el objeto que la convención pide convertir en dibujo
    # ([[deck-contenido-visual-no-bullets]]). Ahora son tres figuras: la compuerta que apaga
    # mediciones, la grilla de contribuciones que ES el reporte, y el entrenamiento conjunto.
    # Las ecuaciones no desaparecen: la 9, que es la que hay que llevarse, se escribe entera.
    # Retitulada el 7-ago (pedido 5 de Ernesto, que llamó «terrible» a «Del embudo al
    # reporte»): el título nuevo dice la tesis del paper, casa con el registro de los otros
    # («Mira bien y responde mal») y ya estaba escrito en la barra de remate de la lámina.
    s = content(prs, "La predicción es el reporte")
    add_textbox(s, 0.36, TOP, 5.30, 0.24,
                [("PRIMERO: CASI TODAS LAS MEDICIONES SE APAGAN   (4) (5)", 10, True,
                  GRIS_BODY, F_BODY)])
    barras_esquema(s, 0.36, TOP + 0.32, 2.30, 0.58, BETA_ANTES, ONCO_PANEL)
    _oper(s, 2.98, TOP + 0.61, sym="β", d=0.40)
    barras_esquema(s, 3.36, TOP + 0.32, 2.30, 0.58, BETA_DESPUES, ONCO_PANEL,
                   destacados=BETA_VIVOS)
    caption(s, 0.36, TOP + 0.92, 2.30, "los 246 pesos, antes", size=8.5, col=GRIS_BODY)
    caption(s, 3.36, TOP + 0.92, 2.30, "después de la compuerta", size=8.5, col=ONCO_DARK)
    add_textbox(s, 0.36, TOP + 1.20, 5.30, 0.46, [
        ("Cada medición tiene su propia compuerta y se calcula por separado: no reparten un "
         "presupuesto. Por eso se pueden empujar casi todas a cero.",
         9.5, False, INK, F_BODY)])
    add_textbox(s, 6.10, TOP, 3.54, 0.24,
                [("Y LAS DOS RAMAS SE ENTRENAN JUNTAS", 10, True, GRIS_BODY, F_BODY)])
    destilacion(s, 6.10, TOP + 0.36, 3.54, 0.56)
    add_textbox(s, 6.10, TOP + 1.24, 3.54, 0.42, [
        ("Sin ese término serían dos modelos corriendo en paralelo.",
         9.5, False, INK, F_BODY)])
    add_textbox(s, 0.36, TOP + 1.76, 9.28, 0.24,
                [("DESPUÉS: LA PREDICCIÓN QUEDA DESARMADA EN CONTRIBUCIONES QUE SE LEEN   "
                  "(6) (7) (8)", 10, True, GRIS_BODY, F_BODY)])
    PATRON = [[3, 0, 1, -1], [2, -2, 0, 1], [0, 1, 3, 0], [1, 0, -1, 2], [2, 1, 0, -2]]
    grilla_contribuciones(s, 0.36, TOP + 2.40, 5.60, 1.00,
                          ["parche 1", "parche 2", "parche 3", "…", "parche 20"],
                          ["solidez", "densidad", "mezcla de tipos", "grafo"], PATRON)
    caption(s, 0.36, TOP + 3.46, 5.60,
            "teal = empuja hacia la clase   ·   gris = empuja en contra   ·   el tamaño, "
            "cuánto", size=8.5, col=GRIS_BODY)
    eq(s, 6.10, TOP + 2.20, 3.54, "Ŷ_f = ψ( Σ_i Σ_j w_j β_j M_(ij) + b )", num="(9)",
       size=11, h=0.46, fill=TEAL_CARD)
    add_textbox(s, 6.10, TOP + 2.76, 3.54, 0.70, [
        ("Cada celda de la izquierda es un sumando de esa cuenta: un parche por una "
         "medición. La explicación no se calcula después, ES la cuenta.",
         10, False, INK, F_BODY)])
    # El remate decía «ES el reporte que ve el patólogo», que es de donde salió el título
    # nuevo. Con el título arriba diciéndolo, el remate pasa a decir QUÉ trae ese reporte:
    # repetir la misma frase a treinta centímetros de distancia se oye como tartamudeo.
    takeaway_bar(s, "Si hay que quedarse con una sola ecuación, es la 9: cada sumando dice "
                    "qué región, por qué medición, y cuánto aportó.", t=TOP + 3.76, size=12.5)
    notes(s, "Las ecuaciones del final las cuento dibujadas, no una por una.\n"
             "Arriba a la izquierda, la compuerta que deja vivas unas pocas mediciones.\n"
             "Abajo, la predicción desarmada en contribuciones, que es el reporte.\n"
             "Arriba a la derecha, las dos ramas entrenándose juntas.\n"
             "\n"
             "El resto de las ecuaciones las paso dibujadas y en bloque, porque desarmadas "
             "una por una con el mismo detalle que las primeras todavía no las tengo, y "
             "prefiero decirlo antes que improvisar.\n"
             "\n"
             "Arriba a la izquierda está el paso que más me llamó la atención. Cada una de las "
             "doscientas cuarenta y seis mediciones recibe un peso, y ese peso pasa por una "
             "compuerta. A la izquierda dibujé cómo llegan los pesos, todos parecidos; a la "
             "derecha, cómo quedan después. La compuerta es una sigmoide con temperatura, y lo "
             "que hace es empujar la enorme mayoría hacia cero y dejar unas pocas vivas. Eso "
             "es posible porque cada compuerta se calcula por separado, no reparten un "
             "presupuesto entre todas como sí hace la atención sobre los parches. Y no es un "
             "tecnicismo: es exactamente lo que permite que el reporte que ve el patólogo "
             "tenga pocos renglones en vez de doscientos cuarenta y seis.\n"
             "\n"
             "Abajo está el reporte. Cada fila es uno de los veinte parches "
             "elegidos y cada columna es una de las mediciones que sobrevivieron. En cada "
             "cruce hay un número, y ese número es la contribución de ese parche por esa "
             "medición. El color dice hacia dónde empuja y el tamaño dice cuánto. La "
             "predicción es, literalmente, la suma de todos esos cuadraditos.\n"
             "\n"
             "Esa es la ecuación de la derecha, la nueve, y es la que hay que retener. No es "
             "una explicación que alguien calcula después de que el modelo respondió: es la "
             "cuenta misma que hizo el modelo, escrita término a término. Por eso el reporte "
             "puede decir esta región, por esta medición, aportó esto a favor.\n"
             "\n"
             "Y arriba a la derecha, la última: las dos ramas se entrenan a la vez, cada una "
             "con su propio error, más un tercer término que empuja a la rama interpretable a "
             "acercarse a la profunda. Ese tercero pesa veinte y los otros dos pesan uno cada "
             "uno, así que no es un detalle de ajuste: es el que manda. Sin él serían "
             "dos modelos corriendo en paralelo, y el puente de la lámina anterior no tendría "
             "con qué aprender.")


def lam_simil_resultados(prs):
    # ---- Resultados y costo de adopción ----
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
             "Dos preguntas que dejo planteadas: si el interés es entenderlo o evaluarlo, y si "
             "vale una tarde cruzar su dataset con el nuestro.\n"
             "\n"
             "Los resultados. Esta tabla nos interesa más que las otras porque no compara el "
             "método contra otros métodos, sino el método aplicado sobre distintos modelos de "
             "base, y uno de esos modelos es el nuestro.\n"
             "\n"
             "Sobre el primero, que es el modelo de atención más simple, la exactitud sube un "
             "poco al agregarle la rama interpretable. Sobre el segundo, que es el nuestro y es "
             "la fila destacada, bajan las dos: la exactitud algo más de un punto y el área "
             "bajo la curva un punto y medio, y los valores exactos están en la fila. Sobre el "
             "tercero baja apenas. Lo digo sin ánimo de desacreditar "
             "el trabajo, que me "
             "parece muy sólido, pero el titular de que no hay compromiso entre rendimiento e "
             "interpretabilidad se sostiene sobre el primer modelo, y la fila destacada es "
             "justo la que nos correspondería.\n"
             "\n"
             "Lo que sí sostienen con firmeza es lo otro: un modelo que use únicamente las "
             "mediciones con nombre pierde bastante, y el co-aprendizaje recupera casi todo.\n"
             "\n"
             "Vale la comparación con lo nuestro, que es nítida sin ser una competencia. La "
             "interpretación de ellos aparece durante el entrenamiento y por diseño, sobre "
             "mediciones que tienen nombre desde antes; la nuestra aparece después, sobre "
             "modelos ya congelados, y sobre unidades internas cuyos nombres los pusimos "
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
             "De ahí salen dos preguntas, y las dejo planteadas para cuando volvamos sobre esta "
             "línea. La primera es de alcance y de ella depende todo lo "
             "demás: si el interés es entender esta línea, eso ya está hecho; si es evaluarla "
             "como candidata, empieza por poner a andar el segmentador sobre nuestras láminas, y "
             "eso no cabe al lado de lo que ya está en marcha. La segunda es lo más barato que "
             "hay sobre la mesa. Y dejo una tercera, más de fondo: cuando le mostraron los "
             "reportes a un patólogo, algo más de un cuarto de las mediciones que el modelo "
             "declara importantes le resultaron no relevantes. Me parece muy honesto publicarlo, "
             "y la pregunta es si ese número es aceptable para el estándar clínico que "
             "manejamos.")


def lam_objetivos_propuestos(prs):
    # ---- Objetivos propuestos ----
    # Los dos que eligió Ernesto. La réplica del resultado del sprint pasado y HoVer-Net
    # sobre los mejores parches quedan FUERA a propósito: siguen abiertos, pero no se
    # proponen como objetivo. La lámina tiene que dejar a la vista de qué depende el primero,
    # que es la pregunta concreta que hay que hacer en la reunión.
    # Rehecha el 5-ago: Ernesto marcó que no usaba el molde con el que las presentaciones
    # anteriores cierran. Puesta al molde EXACTO el 7-ago, que es su pedido 4: el molde de la
    # lámina «Objetivos del sprint», la misma que el reordenamiento eliminó. Título 32 pt,
    # lista numerada en infinitivo, marcador de estado a la derecha, y NADA MÁS: se retiran el
    # panel de la pregunta y la barra de remate, y los dos bajan al guion. La geometría es la
    # de la lámina que se fue, sin re-derivar: `row_tops = 1.10 + i * 0.68`, `row_h = 0.62`,
    # fila de 19 pt sobre 7,75", marcador en `x = 8.98`.
    s = content(prs, "Objetivos propuestos", size=32)
    row_tops = [1.10 + i * 0.68 for i in range(len(OBJETIVOS_PROP))]
    row_h = 0.62
    for item, rt in zip(OBJETIVOS_PROP, row_tops):
        add_textbox(s, 0.35, rt, 7.75, row_h, [(item, 19, True, GRIS_BODY, F_BODY)],
                    anchor=MSO_ANCHOR.MIDDLE)
        status_progress(s, 8.98, rt + row_h / 2, texto="Propuesto")
    notes(s, "Propongo dos objetivos, y los dos empiezan sin gastar cómputo.\n"
             "El primero es llevar la medición de atención a todas las láminas anotadas que "
             "haya.\n"
             "El segundo es probar el paper de marcas parciales por su camino más barato.\n"
             "Por qué ese paper: es el único de los tres cuya supervisión encaja con lo que "
             "tenemos.\n"
             "Los dos dependen de una sola pregunta, que es la que quiero hacer hoy.\n"
             "\n"
             "Con todo lo anterior sobre la mesa, propongo dos cosas para lo que viene, y las "
             "dos se pueden empezar sin pedir cómputo.\n"
             "\n"
             "La primera es llevar la medición de atención a más láminas anotadas. Hoy tengo "
             "una, y con una lámina el resultado describe pero no establece; lo dije al "
             "principio y lo sostengo. La herramienta ya está "
             "construida y puesta a prueba: el nulo por traslación, que fue lo que más costó, "
             "sirve tal cual para cualquier lámina que tenga marcas. El trabajo "
             "pesado ya está hecho y lo que falta es material.\n"
             "\n"
             "La segunda es el paper de detección con marcas parciales. No propongo montarlo "
             "entero, propongo entrar por donde es barato: correr un detector de mitosis ya "
             "entrenado sobre nuestra lámina y ver cuánto acierta contra las veintiséis "
             "marcas que tenemos. Eso responde si hay señal aprovechable antes de invertir "
             "nada, y si la respuesta es que no, nos ahorramos el resto.\n"
             "\n"
             "Quiero decir por qué ese paper y no otro, porque la búsqueda no fue a ciegas: la "
             "orientó la medición que acabo de contar. Teníamos cuatro maneras posibles de "
             "atacar el problema de mitosis, escritas antes de medir. La primera era cambiar la "
             "forma en que el modelo combina los parches. La segunda, el campo de visión, "
             "porque la mitosis se cuenta a cuarenta aumentos y buena parte de nuestra cohorte "
             "está a veinte. La tercera, cambiar la unidad con la que representamos el tejido, "
             "pasando del parche al núcleo. Y la cuarta, aprovechar las marcas del patólogo "
             "como supervisión, aunque sean parciales.\n"
             "\n"
             "La medición reordenó eso. La primera pierde su motivación principal, porque su "
             "argumento de cabecera era precisamente la frase del patólogo, y la frase quedó "
             "refutada. Y quiero ser cuidadoso: pierde ese argumento, no todos. Le queda uno "
             "intacto, que esta medición no evalúa, y es que contar mitosis en el criterio "
             "clínico es buscar el máximo en un puñado de campos vecinos, no promediar toda la "
             "lámina. Las otras tres se fortalecen o quedan abiertas, y por eso la búsqueda "
             "apuntó ahí.\n"
             "\n"
             "Miré tres papers para esa rama, y el que propongo es el de detección con "
             "positivos parciales, "
             "por una razón que es de encaje y no de calidad. Nuestras anotaciones son "
             "positivos parciales: el patólogo marcó veintiséis mitosis, pero no marcó todas, "
             "así que lo que no está marcado no podemos tratarlo como negativo. Ese paper está "
             "construido exactamente para ese caso, y es el único de los tres que lo está. De "
             "los otros dos, uno trae pesos públicos de segmentación de núcleos, o sea que no "
             "necesita nada nuestro, pero no distingue mitosis entre sus clases; y el otro pide "
             "poder acercarse a cuarenta aumentos, que en nuestra cohorte privada no está. De "
             "cada uno preparé una hoja aparte con el detalle, así que no hace falta decidir "
             "nada hoy sobre la marcha.\n"
             "\n"
             "Y las dos cuelgan de la misma pregunta, la que necesito que conversemos "
             "hoy: cuántas láminas anotadas hay además de esta, y quién las anotó. Con una "
             "sola lámina el primer objetivo no tiene materia, y el segundo se queda sin con "
             "qué evaluarse. Lo "
             "pregunto porque el archivo de anotaciones que tengo viene firmado con unas "
             "iniciales que no sé de quién son, y eso importa por dos motivos. Uno práctico: "
             "si hay más láminas del mismo anotador, el primer objetivo arranca la semana que "
             "viene. Y otro de método: si las que aparezcan son de anotadores distintos, hay "
             "que tenerlo en cuenta al juntarlas, porque no todos marcan con el mismo "
             "criterio.")


# ============================================================================
# El orden del deck
# ============================================================================
# Datos de la sección del 19-ago
# ============================================================================
# Todo lo de acá sale de sprints/B8_sprint8/anotaciones_patologo/regiones_escaneo/resultados.md
# (§3, §8, §10, §11) y de sprints/B8_sprint8/hovernext_129741/ (techo_atencion.md,
# coordinacion_gpu.md, plan_semana_17ago.md). Se escriben a mano acá para que la lámina no
# dependa de leer los CSV en tiempo de build, y cada bloque dice de qué sección viene.

# §3: el barrido de las 589 carpetas de wsi/
REGIONES_ALCANCE = [("Con 1 sola región", "351"), ("Con 2 regiones", "130"),
                    ("Con 3 regiones", "8"), ("Con 4 regiones", "1")]

# §12: el reparto rehecho sobre las 109 medidas del re-barrido CON giro en la etapa A
PERFILES = [("La etapa A no localiza", "32", "29 %"),
            ("Perfil de re-escaneo", "31", "28 %"),
            ("Ambiguo", "34", "31 %"),
            ("Perfil de secciones seriadas", "12", "11 %")]

# §12: la sensibilidad, que hace falta porque los cortes son posteriores a ver los datos
SENSIBILIDAD = [("Laxo", "41", "27", "9"), ("Base", "31", "34", "12"),
                ("Estricto", "18", "46", "13")]

# §10.b: el probe de rotación, leído en el orden que manda su pre-registro
PROBE = [("Control positivo", "4", "0,76 → 0,83", "ya lo eran"),
         ("Silueta ≥ 0,95", "8", "0,12 → 0,48", "4 de 8"),
         ("Silueta < 0,95", "4", "0,29 → 0,45", "2 de 4")]

# techo_atencion.md: los 11 K del plan, con rótulo solo en los que la lámina nombra
TECHO_KS = [("20", ""), ("50", ""), ("100", "1,4 mm²"), ("189", ""), ("300", "4,3 mm²"),
            ("500", ""), ("750", "10,6 mm²"), ("1000", ""), ("1392", ""), ("2000", ""),
            ("2496", "la región")]
TECHO_CLAM = [2, 6, 12, 15, 19, 23, 25, 26, 27, 27, 28]
TECHO_MAMM = [3, 4, 13, 18, 22, 23, 28, 28, 28, 28, 28]
TECHO_AZAR = [0.22, 0.56, 1.12, 2.12, 3.37, 5.61, 8.41, 11.22, 15.62, 22.44, 28.0]

# coordinacion_gpu.md: el estado de la cola, sin nombres de usuario ni números de trabajo
COLA = [("Servidor de inferencia", "corriendo", "365 días", "tiene la GPU"),
        ("Trabajo de otro grupo", "en espera", "sin límite", "delante nuestro"),
        ("Trabajo de otro grupo", "en espera", "sin límite", "delante nuestro"),
        ("El nuestro", "en espera", "12 horas", "tercero en la fila")]


# ============================================================================
# Figuras nativas de la sección del 19-ago
# ============================================================================
def barra_reparto(slide, l, t, w, h, tramos, fs=10.5, fs_num=15):
    """Un total repartido en tramos contiguos, cada uno proporcional a su cuenta.

    Un reparto es una proporción, y una proporción se dibuja ([[deck-contenido-visual-no-bullets]]).
    Se usa solo donde los tramos son anchos: con un tramo de 1 sobre 108 el rótulo no cabría
    debajo, y para ese caso la tabla cuenta mejor. `tramos` = (rótulo, n, color, texto_blanco)."""
    total = sum(n for _, n, _, _ in tramos)
    x = l
    for rot, n, col, blanco in tramos:
        aw = w * n / total
        _rect(slide, x, t, aw, h, col)
        add_textbox(slide, x, t, aw, h,
                    [(str(n), fs_num, True, WHITE if blanco else ONCO_INK, F_BODY,
                      PP_ALIGN.CENTER)], anchor=MSO_ANCHOR.MIDDLE)
        add_textbox(slide, x, t + h + 0.06, aw, 0.30,
                    [(rot, fs, True, ONCO_DARK if blanco else GRIS_BODY, F_BODY,
                      PP_ALIGN.CENTER)])
        x += aw
    return t + h + 0.42


def eje_angulos(slide, l, t, w, hi=12.0, bandas=(), marcas=(), fs=9.5, h=0.30):
    """El ángulo de giro sobre su recorrido, con lo que el método barría y lo que hacía falta.

    Es el hallazgo entero en una figura: dos bandas de diseño y tres marcas medidas, y se ve
    de un vistazo que las marcas caen fuera de la banda chica. Dicho en texto («barríamos
    hasta ocho grados y hacían falta siete coma ocho de mediana») hay que reconstruirlo
    mentalmente; dibujado no hay nada que reconstruir.

    `bandas` = (hasta_grados, rótulo, color), en orden creciente de `hasta`;
    `marcas` = (grados, rótulo, destacada).

    Dos cosas que salieron del rasterizado del 18-ago y que la auditoría no ve, porque cada
    objeto estaba dentro de su caja ([[deck-qa-puntos-ciegos-chequeo]]):

    - **Las bandas se pintan de la más ancha a la más angosta.** Todas arrancan en cero, así
      que pintarlas en el orden en que se declaran deja a la última tapando a las anteriores,
      y la banda chica, que es la que carga el hallazgo, no se ve.
    - **Los rótulos no van al lado de cada banda, van a una leyenda debajo del eje.** Al lado
      se pisaban entre sí. Las marcas se escalonan en dos alturas por el mismo motivo, con la
      destacada más alta y sola en su fila."""
    def px(g):
        return l + w * g / hi

    def grados(g):
        return ("%g" % g).replace(".", ",") + "°"

    base = t + 1.20
    for i, (hasta, _rot, col) in reversed(list(enumerate(bandas))):
        alto = h * (0.55 if i == 0 else 1.0)
        _rect(slide, l, base - alto, px(hasta) - l, alto, col)
    _conn(slide, l, base, l + w, base, arrow=False)
    for g in range(0, int(hi) + 1, 2):
        _rect(slide, px(g) - 0.006, base, 0.012, 0.07, ONCO_INK)
        add_textbox(slide, px(g) - 0.30, base + 0.10, 0.60, 0.24,
                    [(grados(g), fs - 0.5, False, GRIS_BODY, F_BODY, PP_ALIGN.CENTER)])
    for g, rot, dest in marcas:
        col = ONCO_DARK if dest else ONCO_CONN
        alto = 0.96 if dest else 0.66
        _rect(slide, px(g) - 0.022, base - alto, 0.044, alto, col)
        add_textbox(slide, px(g) - 1.10, base - alto - 0.32, 2.20, 0.30,
                    [(rot, fs + (1.5 if dest else 0.0), dest, col, F_BODY, PP_ALIGN.CENTER)],
                    anchor=MSO_ANCHOR.BOTTOM)
    ly = base + 0.38
    x = l
    for hasta, rot, col in bandas:
        _rect(slide, x, ly + 0.05, 0.20, 0.14, col)
        tw = 0.30 + 0.062 * len(rot)
        add_textbox(slide, x + 0.26, ly - 0.02, tw, 0.28,
                    [(rot, fs, False, GRIS_BODY, F_BODY)], anchor=MSO_ANCHOR.MIDDLE)
        x += 0.26 + tw + 0.22
    return ly + 0.34


def curva_techo(slide, l, t, w, h, series, ks, fs=9.5, ymax=28.0):
    """Recall alcanzable contra el tamaño de la máscara, con las tres curvas superpuestas.

    El objeto es una curva, así que va como curva y no como tabla: lo que hay que ver es que
    las dos de atención despegan del azar temprano y se vuelven a juntar al final, que es
    justo donde el chequeo de sanidad exige que coincidan. El eje horizontal va por índice y
    no por K: los K están espaciados de forma casi logarítmica y a escala lineal los seis
    primeros se apilarían contra el margen izquierdo."""
    n = len(ks)
    paso = w / (n - 1)

    def pt(i, v):
        return l + i * paso, t + h - h * v / ymax
    _conn(slide, l, t + h, l + w, t + h, arrow=False)
    for g in (0, 7, 14, 21, 28):
        y = t + h - h * g / ymax
        add_textbox(slide, l - 0.56, y - 0.13, 0.46, 0.26,
                    [("%d" % g, fs - 0.5, False, GRIS_BODY, F_BODY, PP_ALIGN.RIGHT)],
                    anchor=MSO_ANCHOR.MIDDLE)
    for serie in series:
        nombre, vals, col, grueso = serie[:4]
        marca = serie[4] if len(serie) > 4 else ("cuad" if grueso else None)
        pts = [pt(i, v) for i, v in enumerate(vals)]
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            ln = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x0), Inches(y0),
                                            Inches(x1), Inches(y1))
            ln.line.color.rgb = col; ln.line.width = Pt(2.25 if grueso else 1.25)
            ln.shadow.inherit = False
            if not grueso:
                lnpr = ln.line._get_or_add_ln()
                lnpr.append(lnpr.makeelement(qn('a:prstDash'), {'val': 'dash'}))
        # El color solo no alcanzaba: las dos series de atención venían en dos teales que
        # difieren en tres unidades por canal y en el rasterizado son el mismo. Se separan
        # por color Y por forma del marcador, que es lo que sobrevive a un proyector malo.
        for x0, y0 in pts:
            if marca == "circ":
                sp = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x0 - 0.043),
                                            Inches(y0 - 0.043), Inches(0.086), Inches(0.086))
                sp.fill.solid(); sp.fill.fore_color.rgb = col
                sp.line.color.rgb = WHITE; sp.line.width = Pt(0.75)
                sp.shadow.inherit = False
            elif marca == "cuad":
                _rect(slide, x0 - 0.035, y0 - 0.035, 0.07, 0.07, col)
    return t + h + 0.30


# ============================================================================
# Láminas del 19-ago
# ============================================================================
# Ernesto eligió EXTENDER el deck del 6-ago en vez de hacer uno nuevo, y que el material
# entre en orden CRONOLÓGICO, después de «Objetivos propuestos». Con eso el deck queda
# como el recorrido completo del sprint y la reunión de mañana ocurre en su última parte.
# El bloque del 6-ago no se toca: ni una lámina, ni un número, ni una nota.
def lam_desde_6ago(prs):
    # ---- El mapa del bloque nuevo ----
    s = content(prs, "Lo que se hizo desde el 6 de agosto")
    cw, gap = 3.0, 0.30
    xs = [0.35 + i * (cw + gap) for i in range(3)]
    panel(s, xs[0], TOP + 0.30, cw, 2.12, "Regiones de escaneo", ONCO_DARK, [
        "139 de 490 láminas privadas tienen más de una región de escaneo.",
        "130 barridas, 109 medidas, con giro.",
        "El recuento quedó cerrado."], ONCO_CONN)
    panel(s, xs[1], TOP + 0.30, cw, 2.12, "HoVer-NeXt", ONCO_DARK, [
        "Instalado y auditado, con tres correcciones al plan.",
        "La interpretabilidad corrió sobre la lámina del patólogo.",
        "Y la segmentación corrió: 177 mitosis, sin cruzar."], ONCO_CONN)
    panel(s, xs[2], TOP + 0.30, cw, 2.12, "Método", ONCO_DARK, [
        "Tres patrones nuevos, escritos y ya en uso.",
        "Los tres dicen lo mismo: el instrumento se mete en la conclusión.",
        "Uno de ellos ahorró una corrida entera."], ONCO_CONN)
    status_done(s, xs[0] + cw / 2, TOP + 2.70)
    status_done(s, xs[1] + cw / 2, TOP + 2.70)
    status_done(s, xs[2] + cw / 2, TOP + 2.70)
    takeaway_bar(s, "Los tres hilos con resultado, y el que faltaba cerró de madrugada")
    notes(s, "Hasta acá, lo que traía del 6 de agosto. Ahora, las dos semanas desde entonces.\n"
             "Tres hilos: regiones de escaneo, segmentación de núcleos y método.\n"
             "Los tres tienen resultado, y el último cerró de madrugada.\n"
             "\n"
             "Lo que vimos hasta acá es el bloque que traía preparado de la reunión anterior. "
             "A partir de esta lámina cambia el marco: esto es lo que pasó en las dos semanas "
             "que siguieron, y lo cuento en el orden en que ocurrió, que no siempre es el "
             "orden en que uno lo contaría después.\n"
             "\n"
             "Son tres hilos. El primero es una pregunta que apareció mirando los archivos de "
             "la cohorte privada y que terminó en un recuento sobre casi quinientas láminas. "
             "El segundo es la segmentación de núcleos, que llevaba una semana esperando turno "
             "de cómputo y entró de madrugada. El tercero no es un resultado sino una forma de "
             "trabajar: tres patrones que escribimos en estas dos semanas y que ya están en uso.\n"
             "\n"
             "Aviso algo sobre el primero, porque va a volver a aparecer: es el hilo donde más "
             "nos equivocamos, y prefiero dejarlo dicho de entrada. Hay una predicción nuestra "
             "que el dato terminó refutando, y la voy a contar cuando llegue.")


def lam_regiones_pregunta(prs):
    # ---- Las dos regiones, y cuántas láminas alcanza ----
    # Las dos imágenes van al MISMO alto a propósito: las dos regiones están al mismo
    # downsample, así que a igual alto quedan a igual escala y la comparación que la lámina
    # propone es legítima. Dibujarlas a igual ANCHO las pondría a escalas distintas.
    s = content(prs, "Dos regiones de escaneo dentro del mismo archivo")
    hi = 2.16
    w0, w1 = hi * 1.0437, hi * 1.0021
    x0 = 0.38
    x1 = x0 + w0 + 0.14
    s.shapes.add_picture(REG0, Inches(x0), Inches(TOP + 0.40), Inches(w0), Inches(hi))
    s.shapes.add_picture(REG1, Inches(x1), Inches(TOP + 0.40), Inches(w1), Inches(hi))
    caption(s, x0, TOP + 0.14, w0, "región 0", size=10.5, col=ONCO_DARK, bold=True)
    caption(s, x1, TOP + 0.14, w1, "región 1", size=10.5, col=ONCO_DARK, bold=True)
    caption(s, x0, TOP + 2.62, w0 + 0.14 + w1,
            "la 129741: los seis fragmentos, en las dos", size=9.5)
    xt = x1 + w1 + 0.40
    wt = 9.62 - xt
    simple_table(s, xt, TOP + 0.32, wt, ["Láminas privadas con imagen", "490"],
                 REGIONES_ALCANCE, [0.66, 0.34], row_h=0.34, fs=10.5, destacar=1)
    _grupo(s, xt, TOP + 2.14, wt, 0.76, fill=TEAL_CARD)
    add_textbox(s, xt, TOP + 2.14, wt, 0.76, [
        ("139 de 490   =   28,4 %", 17, True, ONCO_DARK, F_BODY, PP_ALIGN.CENTER),
        ("tienen más de una región de escaneo", 10, False, GRIS_BODY, F_BODY,
         PP_ALIGN.CENTER)], anchor=MSO_ANCHOR.MIDDLE)
    pie_lineas(s, xt, TOP + 3.02, wt, [
        "Del mismo barrido: las 490 están a 0,465 µm/px y 20 aumentos, sin una excepción."])
    takeaway_bar(s, "Casi tres de cada diez láminas privadas, y el archivo lo declara solo")
    notes(s, "Una región de escaneo es un recorte que el aparato guarda dentro del mismo archivo.\n"
             "139 de 490 láminas privadas tienen más de una.\n"
             "En ésta, los seis fragmentos de tejido aparecen en las dos.\n"
             "Las 490 están a la misma resolución, sin una excepción.\n"
             "\n"
             "Empiezo por explicar qué es una región de escaneo, porque es una palabra del "
             "formato y no del microscopio. Cuando se digitaliza un vidrio, el aparato no "
             "siempre guarda una sola imagen: puede guardar varios recortes distintos, cada "
             "uno con su propio sistema de coordenadas, todos dentro del mismo archivo. Cada "
             "uno de esos recortes es una región. Y esto no es algo que hayamos deducido "
             "mirando el tejido: el archivo lo declara solo, en su encabezado, y basta leerlo "
             "para saber cuántas tiene.\n"
             "\n"
             "Lo que ven son las dos regiones de la lámina que tenemos anotada, dibujadas al "
             "mismo tamaño a propósito, porque están a la misma resolución y así la "
             "comparación es legítima. Si las hubiera puesto al mismo ancho quedarían a "
             "escalas distintas y no se podrían mirar juntas. Los seis fragmentos de tejido "
             "que hay sobre el vidrio aparecen en las dos.\n"
             "\n"
             "Cuando fuimos a contar cuántas láminas de la cohorte privada están en esta "
             "situación, la respuesta fue casi tres de cada diez. Es una fracción grande, y "
             "por eso dejó de ser una curiosidad del archivo y pasó a ser una pregunta.\n"
             "\n"
             "Ahora, lo que esta lámina todavía no dice, y quiero ser cuidadoso porque es la "
             "tentación entera de este hilo. Que los seis fragmentos aparezcan en las dos "
             "regiones no prueba que sean el mismo tejido. Podría ser el mismo vidrio "
             "digitalizado dos veces, y entonces la segunda región es material repetido; o "
             "podrían ser dos cortes distintos del mismo bloque, y entonces es material nuevo. "
             "Las dos cosas se ven parecidas a esta distancia. Distinguirlas es lo que ocupa "
             "las láminas que siguen, y hace falta un instrumento, no una mirada.")


def lam_regiones_metodo(prs):
    # ---- El instrumento: dos etapas y una puerta ----
    s = content(prs, "Cómo se mide si son la misma lámina")
    xl, wl = 0.35, 4.42
    y = TOP + 0.30
    _proc(s, xl, y, wl, 0.62,
          "Etapa A · se eligen ventanas de tejido en la región 0 y se buscan en la región 1",
          dim="a 1 de cada 4 píxeles · plantilla de 1024")
    _conn(s, xl + wl / 2, y + 0.62, xl + wl / 2, y + 0.96)
    _oper(s, xl + wl / 2, y + 1.13, sym="?")
    add_textbox(s, xl + wl / 2 + 0.26, y + 0.94, wl / 2 - 0.26, 0.40,
                [("puerta: el pico tiene que ser alto y único", 10, True, ONCO_DARK, F_BODY)],
                anchor=MSO_ANCHOR.MIDDLE)
    _conn(s, xl + wl / 2, y + 1.30, xl + wl / 2, y + 1.62)
    _proc(s, xl, y + 1.62, wl, 0.62,
          "Etapa B · cada ventana que pasó se vuelve a buscar a resolución completa",
          dim="plantilla de 512 · correspondencia celular")
    _conn(s, xl + wl / 2, y + 2.24, xl + wl / 2, y + 2.56)
    _proc_claro(s, xl, y + 2.56, wl, 0.56,
                "Y contra ventanas de control, que son tejido que no corresponde")
    xr, wr = 5.10, 4.55
    hr = wr / 2.0312
    s.shapes.add_picture(REGISTRO, Inches(xr), Inches(TOP + 0.30), Inches(wr), Inches(hr))
    caption(s, xr, TOP + 0.34 + hr, wr,
            "la misma célula, en las dos regiones", size=9.5)
    _grupo(s, xr, TOP + 0.64 + hr, wr, 0.62, fill=TEAL_CARD)
    add_textbox(s, xr, TOP + 0.64 + hr, wr, 0.62, [
        ("0,382   contra   0,049 del control", 15, True, ONCO_DARK, F_BODY, PP_ALIGN.CENTER),
        ("8 de 8 ventanas, en la lámina del patólogo", 9.5, False, GRIS_BODY, F_BODY,
         PP_ALIGN.CENTER)], anchor=MSO_ANCHOR.MIDDLE)
    takeaway_bar(s, "Tres ejes deciden: pico único, cuerpo rígido y señal muy sobre el control")
    notes(s, "Dos etapas, con una puerta en el medio.\n"
             "La etapa A busca ventanas de tejido de una región en la otra, en miniatura.\n"
             "La que pasa la puerta se vuelve a buscar a resolución completa.\n"
             "Y todo corre también contra ventanas de control, que son tejido que no corresponde.\n"
             "\n"
             "El instrumento tiene dos etapas y una puerta entre las dos, y la puerta es lo "
             "más importante del diseño.\n"
             "\n"
             "La primera etapa trabaja en miniatura, a uno de cada cuatro píxeles. Toma "
             "pedazos de tejido de la primera región y los va a buscar dentro de la segunda, "
             "deslizándolos por encima y midiendo en cada posición cuánto se parecen. Queda "
             "una superficie de parecido, y lo que interesa de esa superficie no es solo dónde "
             "está el punto más alto sino si ese punto es alto y además está solo. Un pico "
             "único quiere decir que el pedazo tiene un lugar en la otra región y no otro. Una "
             "superficie plana, con muchos picos parecidos, quiere decir que el pedazo encaja "
             "más o menos en cualquier parte, que es lo mismo que no haber encontrado nada.\n"
             "\n"
             "Ésa es la puerta: solo lo que tiene pico alto y único pasa a la segunda etapa. "
             "Lo que no pasa, no se mide, y no se mide a propósito.\n"
             "\n"
             "La segunda etapa toma lo que pasó y lo vuelve a buscar a resolución completa, "
             "con pedazos más chicos, hasta el nivel en que se distinguen células "
             "individuales. Ahí ya no se pregunta si el tejido está, se pregunta cuánto se "
             "movió y si todo se movió junto.\n"
             "\n"
             "Y hay una tercera cosa que corre en paralelo y que es la que hace que el número "
             "signifique algo. Además de buscar cada pedazo donde debería estar, lo buscamos "
             "en sitios donde sabemos que no corresponde. Eso es el control. La clave está en "
             "que el control corre con exactamente los mismos grados de libertad que la señal: "
             "la misma cantidad de posiciones probadas, el mismo margen de giro, el mismo "
             "tamaño de pedazo. Si le diéramos menos libertad, cualquier parecido nuestro "
             "parecería enorme al lado suyo, y estaríamos midiendo la generosidad del método y "
             "no el tejido.\n"
             "\n"
             "De acá salen los tres ejes que uso en las dos láminas que siguen, y los dejo "
             "nombrados porque después los doy por sabidos. Uno, que el pico sea único, que es "
             "la puerta. Dos, que el cuerpo se mueva rígido, o sea que el desplazamiento se "
             "explique sin estirar ni encoger nada. Y tres, que la señal esté muy por encima "
             "del control.")


def lam_regiones_mitad(prs):
    # ---- El primer resultado, que es el que nadie esperaba ----
    s = content(prs, "El primer resultado: tres de cada diez no localizan")
    cadena_cuenta(s, 0.35, TOP + 0.20, 9.28, [
        ("490", "láminas privadas\ncon imagen"),
        ("139", "con más de una\nregión de escaneo"),
        ("130", "barridas"),
        ("109", "midieron")], h=0.46, fs=17)
    caption(s, 0.35, TOP + 1.20, 9.28,
            "las 21 restantes las rechazó el propio test antes de medir, un 16 %", size=9.5)
    barra_reparto(s, 1.60, TOP + 1.56, 6.80, 0.62, [
        ("la etapa A localiza", 77, ONCO_DARK, True),
        ("la etapa A no localiza", 32, ONCO_PANEL, False)], fs_num=18)
    panel(s, 1.60, TOP + 2.58, 6.80, 0.90, "No medible no es tejido distinto", ONCO_DARK, [
        "Una etapa A que no localiza deja a la etapa B midiendo ruido, y eso es "
        "indistinguible de que el tejido sea de verdad otro. Las 32 resisten también "
        "el barrido con giro."], ONCO_CONN, tsize=13, bsize=11)
    takeaway_bar(s, "Tres de cada diez no localizan ni con giro, y eso sigue sin decir qué tejido son")
    notes(s, "De 490 láminas, 139 tienen más de una región; barrimos 130 y midieron 109.\n"
             "Las 21 que faltan las rechazó el propio test antes de medir.\n"
             "De las 109, en 77 la primera etapa localiza y en 32 no.\n"
             "Esas 32 resisten también el barrido con giro.\n"
             "\n"
             "Éste es el primer resultado, y es el que menos esperábamos.\n"
             "\n"
             "La cadena de arriba se lee de izquierda a derecha. De las láminas privadas con "
             "imagen, poco menos de un tercio tiene más de una región. Barrimos casi todas, y "
             "de ésas midieron algo menos, porque unas cuantas las descartó el propio "
             "procedimiento antes de intentar medirlas: no tenían tejido suficiente, o la "
             "miniatura no daba para elegir pedazos. Que el test rechace por su cuenta a una "
             "de cada seis me parece buena señal y no mala: prefiero un instrumento que avise "
             "que no puede a uno que devuelva un número igual.\n"
             "\n"
             "Y la barra de abajo es el resultado. En siete de cada diez la primera etapa "
             "encuentra el tejido en la otra región. En las tres restantes, no. No es que "
             "encuentre poco: no encuentra, la superficie de parecido queda plana y no hay pico "
             "que valga.\n"
             "\n"
             "Acá está el punto que quiero que quede, porque es el que se malinterpreta "
             "siempre. Que una lámina no sea medible no significa que su segunda región sea "
             "tejido distinto. Significa que no lo sabemos. Cuando la primera etapa no "
             "localiza, la segunda queda midiendo ruido, y el ruido se parece exactamente a lo "
             "que uno esperaría si el tejido fuera de verdad otro. Las dos situaciones dan el "
             "mismo aspecto y el instrumento no las separa. Contarlas como material nuevo "
             "sería regalarnos un resultado que no medimos.\n"
             "\n"
             "Agrego algo que en la versión anterior de esta lámina no podía decir. Esas "
             "treinta y dos "
             "resisten también un barrido con giro, que es la mejora que cuento en un momento. "
             "O sea que no son un problema del método que se arregle buscando mejor: por ahora "
             "son un grupo duro, y su falta de señal se sostuvo cuando le dimos al instrumento "
             "más libertad para encontrarla.")


def lam_regiones_perfil(prs):
    # ---- El reparto, con su sensibilidad al lado ----
    # La sensibilidad va en la MISMA lámina que el reparto y no en el guion: los cortes son
    # posteriores a ver los datos, así que el número y su fragilidad son un solo objeto.
    s = content(prs, "Entre las medibles, 31 de 77")
    xl, wl = 0.35, 4.60
    simple_table(s, xl, TOP + 0.34, wl, ["Perfil", "Láminas", "de 109"],
                 PERFILES, [0.58, 0.21, 0.21], row_h=0.36, fs=10.5, destacar=1)
    panel(s, xl, TOP + 2.28, wl, 1.02, "Las 31, en mediana", ONCO_DARK, [
        "Señal 5,3 veces el control · escala 1,0022 · residuo 34 µm.",
        "Un cuerpo rígido explica el desplazamiento entero."], ONCO_CONN, tsize=13, bsize=10.5)
    xr, wr = 5.28, 4.34
    caption(s, xr, TOP + 0.02, wr, "Y qué pasa si se mueve el corte", size=11,
            col=ONCO_DARK, bold=True, align=PP_ALIGN.LEFT)
    simple_table(s, xr, TOP + 0.34, wr,
                 ["Corte", "Re-escaneo", "Ambiguo", "Seriadas"],
                 SENSIBILIDAD, [0.28, 0.26, 0.23, 0.23], row_h=0.36, fs=10.5, destacar=1)
    pie_lineas(s, xr, TOP + 1.86, wr, [
        "Lo que se mueve es el reparto entre re-escaneo y ambiguo. Las seriadas se quedan "
        "entre 9 y 13 con los tres cortes, pero 7 de las 12 son láminas que el giro acaba "
        "de recuperar, que es justo donde la segunda etapa tiene menos con qué medir."], size=9.5)
    _grupo(s, xr, TOP + 2.86, wr, 0.44, fill=ONCO_DATA)
    add_textbox(s, xr, TOP + 2.86, wr, 0.44,
                [("El recuento ya está cerrado", 11.5, True, BLACK,
                  F_BODY, PP_ALIGN.CENTER)], anchor=MSO_ANCHOR.MIDDLE)
    takeaway_bar(s, "El denominador honesto es 31 de 77 medibles, nunca 31 de 490")
    notes(s, "De las 77 medibles, 31 tienen perfil de re-escaneo.\n"
             "En mediana: señal 5,3 veces el control, escala 1,0022, residuo 34 µm.\n"
             "Los cortes son posteriores a ver los datos, así que va la sensibilidad al lado.\n"
             "El denominador honesto son las medibles, nunca las 490.\n"
             "\n"
             "Entre las que sí se pueden medir, la tabla de la izquierda reparte por perfil, y "
             "el grupo grande es el que se comporta como re-escaneo: la segunda región es el "
             "mismo tejido, digitalizado otra vez.\n"
             "\n"
             "Las tres medianas de abajo son las que sostienen esa lectura, y conviene mirarlas "
             "juntas porque cada una sola no alcanza. La señal está más de cinco veces por "
             "encima del control, o sea que el parecido no es el que sale por probar muchas "
             "posiciones. La escala da prácticamente uno, y eso quiere decir que el tejido no "
             "está estirado ni encogido respecto de la otra región. Y el residuo, que es lo que "
             "queda sin explicar después de mover el pedazo, son unas pocas decenas de "
             "micrómetros, que a esta resolución es del orden de unas pocas células. Las tres "
             "juntas dicen lo mismo: un cuerpo rígido explica el desplazamiento entero.\n"
             "\n"
             "Ahora la mitad derecha, que está en la misma lámina a propósito y no en un "
             "apéndice. Los cortes que separan un perfil de otro los elegimos después de ver "
             "los datos. Eso no está mal en sí, es lo normal cuando uno explora, pero obliga a "
             "mostrar cuánto depende el resultado del corte elegido, porque si no el número se "
             "lee más firme de lo que es. Moviendo el criterio de laxo a estricto, el grupo de "
             "re-escaneo va de cuarenta y una láminas a dieciocho. Es mucho movimiento, y "
             "prefiero decirlo yo a que se note después.\n"
             "\n"
             "Lo que se mueve, en realidad, es el reparto entre re-escaneo y ambiguo: lo que "
             "sale de un grupo entra en el otro. Y hay un detalle en la última columna que "
             "retomo en dos láminas más: las que quedan clasificadas como secciones seriadas "
             "son estables en número, pero más de la mitad son láminas que acabamos de "
             "recuperar con una mejora del método, que es justo el lugar donde la segunda etapa "
             "tiene menos con qué medir. O sea que ese grupo hay que mirarlo con desconfianza, "
             "y no porque el tejido sea raro.\n"
             "\n"
             "Y el remate de abajo es la regla que me impuse para hablar de esto. El "
             "denominador honesto son las láminas que se pudieron medir. No las que tienen dos "
             "regiones, y muchísimo menos el total de la cohorte. Decir treinta y una sobre "
             "cuatrocientas noventa sería una cifra tranquilizadora y falsa.")


def lam_regiones_rotacion(prs):
    # ---- Por qué el número quedó provisional ----
    s = content(prs, "Faltaba buscar giro, y estaba fuera de rango por diseño")
    eje_angulos(s, 0.90, TOP + 0.24, 5.20, hi=12.0, bandas=[
        (1.5, "la etapa B barre 1,5° por defecto", ONCO_DATA),
        (8.0, "y puede llegar a 8°", ONCO_PANEL)], marcas=[
        (3.8, "control: 3,8°", False),
        (7.8, "recuperadas: 7,8°", True),
        (10.5, "la mayor: 10,5°", False)])
    simple_table(s, 0.35, TOP + 2.14, 5.75,
                 ["Grupo", "n", "Ventanas que localizan", "Pasan a medible"],
                 PROBE, [0.30, 0.09, 0.35, 0.26], row_h=0.34, fs=10.5, destacar=1)
    xr, wr = 6.42, 3.20
    _grupo(s, xr, TOP + 0.34, wr, 0.86, fill=TEAL_CARD)
    add_textbox(s, xr, TOP + 0.34, wr, 0.86, [
        ("6 de 12", 24, True, ONCO_DARK, F_BODY, PP_ALIGN.CENTER),
        ("no medibles se recuperan al buscar giro", 10, False, GRIS_BODY, F_BODY,
         PP_ALIGN.CENTER)], anchor=MSO_ANCHOR.MIDDLE)
    panel(s, xr, TOP + 1.34, wr, 1.02, "El pool subió, como predijo", ONCO_DARK, [
        "Predijo unas 81, con un rango de 65 a 97. Medido: 77."], ONCO_CONN,
          tsize=12.5, bsize=10.5)
    panel(s, xr, TOP + 2.48, wr, 1.02, "El 33 no era un piso", ONCO_DARK, [
        "El pool creció y el recuento bajó a 31. La predicción falló."],
          ONCO_CONN, tsize=12.5, bsize=10.5)
    takeaway_bar(s, "El giro que hacía falta era mayor que el que el método buscaba")
    notes(s, "La primera etapa no buscaba giro, y el giro que hacía falta era mayor que el que barría.\n"
             "El control positivo pasó primero: por eso el resto se puede leer.\n"
             "Y además fijó el corte, que estaba mal escrito.\n"
             "Predijo un pool de unas 81, con rango de 65 a 97: medimos 77.\n"
             "Predijo que 33 era un piso, y eso falló: bajó a 31.\n"
             "\n"
             "Ésta es la lámina donde el hilo se corrige a sí mismo, así que la cuento despacio.\n"
             "\n"
             "El punto de partida fue desconfiar del número anterior. Si la mitad de las "
             "láminas no era medible, la primera pregunta razonable es si el instrumento estaba "
             "mal ajustado. Fuimos a descartar eso primero, y quedó descartado: el modo en que "
             "fallaban no era el de un parámetro mal puesto, era el de no encontrar señal. Lo "
             "que quedaba era una sospecha distinta, sobre algo que el método directamente no "
             "hacía.\n"
             "\n"
             "La primera etapa buscaba el tejido desplazándolo, pero sin girarlo. Y si al "
             "digitalizar por segunda vez el vidrio quedó apoyado con otra inclinación, un "
             "pedazo de tejido girado no se encuentra por más que uno lo deslice: hay que "
             "girarlo también. Así que armamos una prueba chica, de doce de estas láminas, "
             "para ver si "
             "buscar giro cambiaba algo.\n"
             "\n"
             "Y acá viene lo que quiero subrayar del método, más que del resultado. La prueba "
             "tenía cuatro láminas de control, que son las que ya sabíamos que localizan bien. "
             "Están ahí para contestar una pregunta previa: si el instrumento con la mejora "
             "puesta sigue funcionando donde ya funcionaba. Si el control hubiera fallado, "
             "nada del resto se podía leer, y estaba escrito de antemano que en ese caso no lo "
             "íbamos a leer.\n"
             "\n"
             "El control sirvió además para algo que no habíamos previsto, y que terminó siendo "
             "la lección más útil. El criterio que teníamos escrito para decidir cuándo un giro "
             "es de verdad era demasiado exigente: aplicado tal cual, rechazaba a tres de las "
             "cuatro láminas de control, que son justamente las que sí localizan. O sea que el "
             "corte estaba mal, no las láminas. Lo volvimos a medir usando solo los pedazos que "
             "efectivamente responden, y ahí las cuatro pasan. El corte quedó fijado en el peor "
             "del control, que es la única manera de fijarlo sin elegir el número que nos "
             "conviene.\n"
             "\n"
             "El resultado de la prueba está en la tabla: la mitad de las no medibles se "
             "recuperan al buscar giro. Y el eje de arriba explica por qué se escapaban. La "
             "segunda etapa barre giro, pero muy poco por defecto, y puede llegar a unos pocos "
             "grados. El giro que las recuperadas piden en mediana está justo afuera de ese "
             "rango, y la que más pide está claramente afuera. No era un error: era una "
             "decisión de diseño que nadie había puesto a prueba contra este material.\n"
             "\n"
             "Hay un detalle que me parece el más interesante de todo el hilo. Al buscar giro, "
             "el parecido sube también en las láminas de control, que ya localizaban sin él. "
             "Eso quiere decir que la primera etapa venía tolerando el giro, no evitándolo: "
             "encontraba el tejido a pesar de la inclinación, pagando en calidad de "
             "coincidencia. Lo veníamos leyendo como que no había giro, y lo que había era un "
             "método que lo aguantaba callado.\n"
             "\n"
             "Y cierro con las dos predicciones que hicimos acá, porque una salió y la otra no. "
             "Dijimos que el conjunto de medibles iba a subir a unas ochenta, con un rango "
             "amplio, y medimos setenta y siete, que cae adentro. Y dijimos que el recuento de "
             "re-escaneos era un piso, que solo podía subir. Eso falló: el conjunto creció y el "
             "recuento bajó. Lo dejo dicho tal cual porque es el tipo de cosa que uno no "
             "descubre si solo se acuerda de sus aciertos.")


def lam_regiones_rebarrido(prs):
    # ---- El recuento que viene, y las dos trampas que ya tiene puestas ----
    s = content(prs, "El recuento se rehízo, y las dos trampas saltaron")
    _grupo(s, 0.35, TOP + 0.24, 9.28, 0.60, fill=TEAL_CARD)
    add_textbox(s, 0.35, TOP + 0.24, 9.28, 0.60,
                [("130 láminas rebarridas con giro en la primera etapa, y 109 midieron. "
                  "Las dos trampas se resolvieron al cosechar.", 13, True, ONCO_DARK,
                  F_BODY, PP_ALIGN.CENTER)], anchor=MSO_ANCHOR.MIDDLE)
    pw = 4.54
    panel(s, 0.35, TOP + 1.06, pw, 2.10, "Una razón que se dispara a cien millones",
          ONCO_DARK, [
          "La fuerza de la señal se mide dividiendo por el control. Cuando el control sale "
          "negativo, el divisor queda clavado en un valor mínimo de guarda y el cociente se "
          "va a cien millones.",
          "Ese número supera cualquier corte, así que la lámina entraría a re-escaneo por el "
          "signo del divisor y no por su señal.",
          "Pasó en 1 de las 109. No cruza la puerta, así que no entra al reparto: quedó "
          "listada aparte y resultó inocua."],
          ONCO_CONN, tsize=13, bsize=10.5)
    panel(s, 5.09, TOP + 1.06, pw, 2.10, "Secciones seriadas que fabrica el método",
          ONCO_DARK, [
          "Una lámina cae en seriadas cuando la señal es débil y el ajuste no es rígido.",
          "Las seriadas pasaron de 1 a 12, y 7 de las 12 son recuperadas: caen ahí al 29 %, "
          "contra el 10 % de las que ya eran medibles.",
          "De las 18 recuperadas que no dan re-escaneo, 10 fallan los dos criterios a la vez. "
          "Es el instrumento, no el tejido."],
          ONCO_CONN, tsize=13, bsize=10.5)
    takeaway_bar(s, "Más seriadas entre las recuperadas no es evidencia de seriadas")
    notes(s, "El re-barrido con giro corrió sobre 130 láminas y midieron 109.\n"
             "Trampa uno: una razón que se dispara a cien millones cuando el divisor cambia de signo.\n"
             "Trampa dos: una categoría que fabrica el propio método.\n"
             "Las dos estaban previstas por escrito, y las dos saltaron.\n"
             "\n"
             "El recuento se rehízo entero con giro en la primera etapa, y antes de correrlo "
             "dejamos anotadas dos maneras concretas en que el resultado nos podía engañar. Las "
             "dos aparecieron, así que esta lámina es el chequeo de esas dos anotaciones.\n"
             "\n"
             "La primera es aritmética y es fácil de pasar por alto. La fuerza de la señal la "
             "medimos dividiéndola por el control. Cuando el control sale negativo, y puede "
             "salir negativo porque es una correlación, el divisor queda clavado en un valor "
             "mínimo de protección que alguien puso para no dividir por cero, y el cociente se "
             "dispara a cien millones. Ese número supera cualquier corte que uno ponga, así que "
             "esa lámina entraría al grupo de re-escaneo por el signo del divisor y no por "
             "haber encontrado nada. El detalle feo es que un valor de protección así no falla: "
             "miente, y devuelve un número que parece buenísimo. Pasó en una sola lámina, esa "
             "lámina no cruza la puerta por otros motivos, y quedó listada aparte. Resultó "
             "inocua, pero lo cuento porque si en vez de una hubieran sido veinte, el recuento "
             "entero se habría inflado sin que nada avisara.\n"
             "\n"
             "La segunda es más sutil y es la que me interesa. Una lámina cae en el grupo de "
             "secciones seriadas cuando pasan dos cosas a la vez: la señal es débil y el ajuste "
             "no es rígido. Ahora bien, las láminas que el giro acaba de recuperar son, por "
             "construcción, las más giradas de todas. Y la segunda etapa barre poco giro y "
             "además no busca cambio de tamaño. O sea que sobre esas láminas la segunda etapa "
             "trabaja al límite, y cuando trabaja al límite produce exactamente esas dos cosas "
             "juntas: señal débil y ajuste malo. Que caigan en seriadas era esperable, y no por "
             "lo que muestra el tejido.\n"
             "\n"
             "Los números lo confirmaron. Ese grupo pasó de una lámina a doce, y más de la "
             "mitad son recuperadas: caen ahí a casi el triple de la tasa de las que ya eran "
             "medibles. Y cuando se abre por cuál de los dos criterios falló cada una, la "
             "mayoría de las recuperadas falla los dos a la vez, que es la firma de un "
             "instrumento que no da abasto y no la de un hallazgo.\n"
             "\n"
             "Por eso el remate. Si mañana alguien mira la tabla y ve que las secciones "
             "seriadas se multiplicaron por doce, la lectura tentadora es que encontramos "
             "material nuevo. No lo encontramos. Ampliamos la población medida metiendo adentro "
             "a las láminas más difíciles, y la categoría creció sola. Dejar esto escrito antes "
             "de correr es lo que permite decirlo ahora sin que suene a excusa.")


def lam_hovernext_estado(prs):
    # ---- Dónde está HoVer-NeXt, y por qué no hay ni un número de segmentación ----
    s = content(prs, "HoVer-NeXt: instalado, auditado y con su primera corrida")
    cw, gap = 3.0, 0.30
    xs = [0.35 + i * (cw + gap) for i in range(3)]
    panel(s, xs[0], TOP + 0.30, cw, 1.94, "Instalación y auditoría", ONCO_DARK, [
        "Repositorio y entorno propio, con cuatro juegos de pesos: uno trae la clase de "
        "mitosis y los otros tres se promedian.",
        "Seis preguntas de auditoría, contestadas contra el código."], ONCO_CONN,
          tsize=13, bsize=10.5)
    panel(s, xs[1], TOP + 0.30, cw, 1.94, "Atención sobre la lámina anotada", ONCO_DARK, [
        "Primera vez que la interpretabilidad corre sobre una lámina privada.",
        "Mitosis es el grupo más atendido de los siete: percentil medio 0,872 y 0,914.",
        "Y los dos modelos igual clasifican mal la lámina."], ONCO_CONN,
          tsize=13, bsize=10.5)
    panel(s, xs[2], TOP + 0.30, cw, 1.94, "La corrida", ONCO_DARK, [
        "Corrió de madrugada, en 18 minutos de pared.",
        "177 mitosis en la lámina entera, y seis clases más.",
        "Es salida cruda: nada cruzado todavía contra las marcas."], ONCO_CONN,
          tsize=13, bsize=10.5)
    status_done(s, xs[0] + cw / 2, TOP + 2.52)
    status_done(s, xs[1] + cw / 2, TOP + 2.52)
    status_done(s, xs[2] + cw / 2, TOP + 2.52)
    pie_lineas(s, 0.35, TOP + 2.86, 9.28, [
        "Tres hallazgos de la auditoría cambiaron el plan: hay que pedir explícitamente que "
        "guarde sus mapas internos, porque los borra al terminar; el costo de dos minutos por "
        "lámina no aplica a esta lámina, que no expone miniatura y obliga a recorrer el lienzo "
        "entero, y la corrida lo confirmó; y los mapas de distancia se descartan en inferencia, "
        "así que la figura de la cadena interna tiene tres paneles y no cuatro."], size=9.5)
    takeaway_bar(s, "Hay 177 mitosis crudas, y cruzarlas contra las 26 marcas es lo que sigue")
    notes(s, "Un segmentador de núcleos con clase de mitosis, pensado para media micra por píxel.\n"
             "La auditoría cambió tres cosas del plan antes de correr.\n"
             "La atención sobre la lámina anotada: mitosis es el grupo más atendido de los siete.\n"
             "Corrió de madrugada: 18 minutos, 177 mitosis en la lámina entera.\n"
             "Es salida cruda, sin cruzar contra las marcas.\n"
             "\n"
             "Éste es el segundo hilo. La idea de fondo viene de la reunión anterior: si el "
             "modelo mira donde hay mitosis pero igual falla, quizás lo que falta no es "
             "atención sino resolución de detalle, y conviene tener un segundo instrumento que "
             "trabaje a nivel de núcleo.\n"
             "\n"
             "La herramienta que elegimos segmenta y clasifica núcleos uno por uno, y tiene una "
             "clase de mitosis entre las suyas, que es lo que nos interesa. Encaja bien por una "
             "razón concreta: está pensada para trabajar a media micra por píxel, y nuestras "
             "láminas privadas están casi exactamente ahí. No hay que reescalar nada, que es "
             "donde suelen aparecer los problemas.\n"
             "\n"
             "Antes de correr nada hicimos una auditoría contra el código, con seis preguntas "
             "escritas, y tres de las respuestas cambiaron el plan. La primera: la herramienta "
             "borra sus mapas internos al terminar, así que si uno quiere conservarlos hay que "
             "pedírselo explícitamente, y son justamente los que sirven para entender por qué "
             "decidió lo que decidió. La segunda: el costo de un par de minutos por lámina que "
             "promete no aplica a esta lámina, porque el archivo no expone una miniatura y "
             "obliga a recorrer el lienzo entero en vez de saltarse el fondo. La tercera es "
             "menor pero afectaba una figura: los mapas de distancia se descartan en "
             "inferencia, así que la cadena interna tiene tres pasos y no cuatro como "
             "dibujábamos.\n"
             "\n"
             "El panel del medio es la primera vez que corremos nuestra medición de atención "
             "sobre la lámina anotada con esta herramienta puesta al lado, y el número dice que "
             "de los siete grupos de tejido el que más atención recibe es el de mitosis. "
             "Aclaro qué son esos dos valores porque se confunden con facilidad: son el "
             "percentil medio de los parches marcados, no el área bajo la curva. Los dos "
             "números quedan casi iguales por casualidad, y por eso conviene decir cuál es cuál.\n"
             "\n"
             "Y hay algo que no quiero que pase inadvertido: los dos modelos, mirando donde hay "
             "que mirar, igual clasifican mal esta lámina. Que la atención caiga bien no "
             "alcanza.\n"
             "\n"
             "El tercer panel es la novedad de anoche. El trabajo llevaba una semana esperando "
             "turno de cómputo y entró de madrugada. Tardó menos de veinte minutos, contra las "
             "más de tres horas y media que había tardado la herramienta anterior sobre "
             "material equivalente. Encontró ciento setenta y siete mitosis en la lámina "
             "entera, además de las otras seis clases de célula.\n"
             "\n"
             "Ese número hay que leerlo con cuidado, y prefiero frenarlo yo. Es salida cruda. "
             "No lo cruzamos todavía contra las veintiséis marcas del patólogo, así que no es "
             "ni acierto ni error: no hay precisión ni exhaustividad calculadas. Y cuando lo "
             "crucemos va a haber que tener presente que las marcas son positivos parciales, o "
             "sea que fuera de ellas puede haber mitosis reales sin marcar, y eso empuja "
             "cualquier medida de precisión hacia abajo por construcción.")


def lam_techo(prs):
    # ---- El techo, que es la mitad de la prueba y no necesitaba la GPU ----
    s = content(prs, "El techo de la prueba, medido sin gastar GPU")
    eq(s, 1.30, TOP + 0.06, 7.38,
       "lo que la prueba puede recuperar  ≤  mín ( lo que la máscara deja pasar ,  lo que el "
       "detector detecta )", size=12.5, h=0.44)
    curva_techo(s, 1.05, TOP + 0.66, 7.30, 1.90, [
        ("Atención de Mammoth", TECHO_MAMM, ONCO_DARK, True, "cuad"),
        ("Atención de CLAM", TECHO_CLAM, ONCO_INK, True, "circ"),
        ("Azar", TECHO_AZAR, ONCO_DATA, False, None)], TECHO_KS)
    # El rotulo va ARRIBA del eje y alineado a la izquierda: centrado verticalmente caia en
    # el renglon de la etiqueta «14» del eje Y (que curva_techo dibuja en l-0.56) y se leia
    # «de 2814». Los ticks son 0/7/14/21/28, el mas alto ocupa TOP+0.53 a TOP+0.79.
    add_textbox(s, 0.15, TOP + 0.20, 1.10, 0.26,
                [("marcas de 28", 9.5, True, GRIS_BODY, F_BODY, PP_ALIGN.LEFT)],
                anchor=MSO_ANCHOR.MIDDLE)
    for i, (k, rot) in enumerate(TECHO_KS):
        if not rot:
            continue
        x = 1.05 + i * (7.30 / (len(TECHO_KS) - 1))
        add_textbox(s, x - 0.70, TOP + 2.60, 1.40, 0.24,
                    [(rot, 9, False, GRIS_BODY, F_BODY, PP_ALIGN.CENTER)])
    add_textbox(s, 8.55, TOP + 0.66, 1.20, 1.90, [
        ("Mammoth", 10, True, ONCO_DARK, F_BODY),
        ("CLAM", 10, True, ONCO_INK, F_BODY),
        ("azar", 10, False, GRIS_BODY, F_BODY)], anchor=MSO_ANCHOR.MIDDLE)
    _grupo(s, 1.05, TOP + 2.92, 7.30, 0.56, fill=TEAL_CARD)
    add_textbox(s, 1.05, TOP + 2.92, 7.30, 0.56,
                [("Con el 12 % de la región ya entran 19 y 22 de las 28 marcas, seis veces "
                  "más de lo que daría tomar esa misma área al azar", 12, True, ONCO_DARK,
                  F_BODY, PP_ALIGN.CENTER)], anchor=MSO_ANCHOR.MIDDLE)
    takeaway_bar(s, "El techo no condena la prueba, y el segundo factor ya se puede medir")
    notes(s, "La prueba encadena un filtro barato y una etapa cara.\n"
             "El techo lo pone el filtro solo, y se calcula sin gastar cómputo.\n"
             "Con el 12 % de la región ya entran 19 y 22 de las 28 marcas, seis veces el azar.\n"
             "Un techo bajo condena la prueba; uno alto no promete nada.\n"
             "\n"
             "Esta lámina es el patrón que más nos sirvió en estas dos semanas, así que la "
             "cuento como método y no solo como resultado.\n"
             "\n"
             "La prueba que queríamos hacer encadena dos cosas: primero un filtro barato, que "
             "se queda con los parches más atendidos, y después una etapa cara, que es correr "
             "el segmentador ahí adentro. La desigualdad de arriba dice algo que suena obvio "
             "cuando uno lo escribe y que sin embargo no habíamos usado nunca: lo que la prueba "
             "entera puede recuperar es, como mucho, el menor de dos límites. Lo que la máscara "
             "deja pasar, y lo que el detector es capaz de detectar. Un candidato que no entra "
             "en la máscara no lo recupera nadie, por bueno que sea el detector.\n"
             "\n"
             "Y el punto operativo es que el primer límite no depende del segundo. Se puede "
             "calcular con la atención que ya teníamos guardada, sin pedir turno de cómputo y "
             "sin esperar a que corra nada. Eso fue justamente lo que hicimos mientras el "
             "trabajo estaba encolado.\n"
             "\n"
             "La curva muestra, para cada tamaño de máscara, cuántas de las marcas quedarían "
             "adentro. La línea de puntos es lo que daría tomar esa misma superficie al azar, y "
             "es la referencia contra la que hay que leer todo lo demás. Con poco más de una "
             "décima parte de la región ya entran alrededor de veinte de las veintiocho, que es "
             "unas seis veces lo que daría el azar. Al final las tres curvas se juntan, y eso "
             "no es un hallazgo sino el chequeo de sanidad: cuando la máscara es la región "
             "entera, todos los criterios tienen que dar lo mismo. Si ahí no coincidieran, "
             "habría un error en el código.\n"
             "\n"
             "Ahora, cómo se lee esto, que es la parte que quiero dejar clavada. Un techo alto "
             "no promete nada. No dice que la prueba vaya a funcionar, solo dice que no está "
             "condenada de antemano. La pregunta sigue viva. Lo que sí sería concluyente es lo "
             "contrario: si el techo hubiera sido bajo, la prueba estaba muerta y nos "
             "ahorrábamos la corrida entera. Ésa es toda la utilidad de medirlo antes.\n"
             "\n"
             "Y una precisión sobre el denominador, que vale para toda esta parte. Las "
             "veintiocho son los parches que contienen una marca del patólogo. No son las "
             "mitosis que hay en la lámina. El patólogo marcó lo que marcó, y fuera de eso "
             "puede haber más. Así que esto mide cuánto recuperamos de lo anotado, que no es lo "
             "mismo que cuánto hay.\n"
             "\n"
             "Con la corrida de anoche ya tenemos con qué medir el segundo factor, que era el "
             "que faltaba. Eso es lo primero que sigue.")


def lam_gpu(prs):
    # ---- El pedido de coordinación, que es un pedido y no una excusa ----
    s = content(prs, "La cola de la GPU: lo que se aprendió")
    simple_table(s, 0.35, TOP + 0.34, 5.30,
                 ["El nodo tiene un solo turno de GPU", "Estado", "Declarado"],
                 [(a, b, c) for a, b, c, _ in COLA], [0.50, 0.24, 0.26],
                 row_h=0.36, fs=10.5, destacar=3)
    # pie_lineas baja de TOP+2.10 a TOP+2.24: la tabla son 5 filas x 0.36 desde TOP+0.34,
    # o sea termina en TOP+2.14, y la nota quedaba pegada a la ultima fila.
    pie_lineas(s, 0.35, TOP + 2.24, 5.30, [
        "Así estaba la fila el lunes. Para colar un trabajo chico antes que uno grande, el "
        "planificador necesita saber cuándo termina el grande, y con dos trabajos sin límite "
        "declarado adelante esa cuenta no existía.",
        "",
        "Se drenó sola de madrugada y el trabajo entró sin que coordináramos nada."], size=9.5)
    xr, wr = 6.00, 3.62
    for i, (t_, txt) in enumerate([
            ("Esperar por prioridad no es esperar", "La fila lo muestra como turno normal. "
             "No lo era, y solo el planificador lo dice si se le pregunta."),
            ("Sin tope no hay forma de colar", "Para adelantar un trabajo chico, el "
             "planificador necesita saber cuándo termina el grande."),
            ("Achicar el pedido no adelanta", "Menos memoria solo importa después de que el "
             "turno se libere, nunca antes.")]):
        panel(s, xr, TOP + 0.28 + i * 1.12, wr, 0.98, t_, ONCO_DARK, [txt], ONCO_CONN,
              tsize=12.5, bsize=10)
    takeaway_bar(s, "Se destrabó sola, y la lección queda escrita para la próxima vez")
    notes(s, "El nodo tiene un solo turno de cómputo, y no se comparte.\n"
             "Con dos trabajos sin tiempo declarado adelante, no hay forma de colar uno chico.\n"
             "Achicar el propio pedido no adelanta nada.\n"
             "La fila se destrabó sola, y la lección queda.\n"
             "\n"
             "Esta lámina la traía preparada como un pedido, y entre que la escribí y hoy dejó "
             "de hacer falta, así que la cuento como lo que aprendimos.\n"
             "\n"
             "La situación era la de la tabla, y es del principio de la semana. El nodo tiene "
             "un solo turno de cómputo, que no se reparte: quien lo toma lo tiene hasta "
             "terminar. Adelante nuestro había un servicio corriendo con un tiempo declarado "
             "larguísimo y dos trabajos más esperando, los dos sin declarar cuánto iban a "
             "durar. El nuestro estaba último, con su tope puesto y a propósito.\n"
             "\n"
             "Lo primero que aprendimos es que la fila mentía, o mejor dicho, que la miramos "
             "mal. El estado que muestra se lee como turno normal, como decir que hay gente "
             "adelante y ya nos toca. No era eso. Para saber qué pasaba de verdad había que "
             "preguntarle al planificador directamente, y recién ahí aparece el motivo.\n"
             "\n"
             "El motivo es el segundo punto, y es el que me pareció menos evidente. Para colar "
             "un trabajo chico antes que uno grande, el planificador necesita saber cuándo "
             "termina el grande. Si el grande no declaró cuánto va a durar, esa cuenta no "
             "existe, y entonces no hay ventana en la que meter a nadie. No es que estuviéramos "
             "en mala posición: es que no había forma de calcular una posición.\n"
             "\n"
             "Y de ahí sale el tercero, que es el más contraintuitivo y por eso el que anoté. "
             "Achicar el propio pedido no adelanta. La reacción natural cuando uno espera es "
             "pedir menos memoria, menos procesadores, hacerse chiquito para caber. Eso solo "
             "sirve después de que el turno se libere. Mientras el bloqueo sea éste, hacerse "
             "chico no cambia absolutamente nada, y uno puede pasar días optimizando algo que "
             "no es el problema.\n"
             "\n"
             "El final es casi cómico: la fila se drenó sola de madrugada, sin que "
             "coordináramos nada y sin que nadie cancelara nada, y el trabajo entró y terminó "
             "en menos de veinte minutos. Así que el pedido que traía ya no tiene objeto. La "
             "lección sí queda escrita, porque el nodo sigue teniendo un solo turno y esto va a "
             "volver a pasar.")


def lam_patrones(prs):
    # ---- Los tres patrones, que es cómo se está trabajando ----
    s = content(prs, "Tres patrones nuevos en dos semanas")
    cw, gap = 3.0, 0.30
    xs = [0.35 + i * (cw + gap) for i in range(3)]
    panel(s, xs[0], TOP + 0.30, cw, 2.30, "El umbral", ONCO_DARK, [
        "Un recorte de los k parches más atendidos se dimensiona por el percentil de lo que "
        "se quiere recuperar, no por el AUC.",
        "Con un AUC de 0,890, los veinte parches más atendidos contienen tres de veintiocho "
        "mitosis."], ONCO_CONN, tsize=13.5, bsize=10.5)
    panel(s, xs[1], TOP + 0.30, cw, 2.30, "El corte", ONCO_DARK, [
        "Un control positivo no solo dice si el instrumento mide: fija el corte, y se le "
        "aplica antes que al grupo de estudio.",
        "El corte que teníamos escrito rechazaba a tres de las cuatro láminas que sí "
        "localizan."], ONCO_CONN, tsize=13.5, bsize=10.5)
    panel(s, xs[2], TOP + 0.30, cw, 2.30, "La categoría", ONCO_DARK, [
        "Una categoría definida por dos fallos a la vez puede fabricarla el propio "
        "instrumento cuando llega a su límite.",
        "Crece sola al ampliar la población medida, y el aumento se lee como hallazgo."],
          ONCO_CONN, tsize=13.5, bsize=10.5)
    _grupo(s, 0.35, TOP + 2.78, 9.28, 0.62, fill=TEAL_CARD)
    add_textbox(s, 0.35, TOP + 2.78, 9.28, 0.62,
                [("Uno de ellos mide el techo de una prueba antes de pedir la GPU: un techo "
                  "bajo la ahorra entera", 12.5, True, ONCO_DARK, F_BODY, PP_ALIGN.CENTER)],
                anchor=MSO_ANCHOR.MIDDLE)
    takeaway_bar(s, "Frente a un resultado que sorprende, el primer sospechoso es la herramienta")
    notes(s, "Tres patrones escritos en estas dos semanas, y los tres ya en uso.\n"
             "El umbral: un recorte por percentil, no por área bajo la curva.\n"
             "El corte: el control positivo lo fija, y se le aplica primero.\n"
             "La categoría: un grupo definido por dos fallos lo puede fabricar el instrumento.\n"
             "\n"
             "Estos tres son lo que más me interesa de estas dos semanas, porque no son "
             "resultados de un experimento sino cosas que ya cambiaron cómo trabajamos.\n"
             "\n"
             "El primero salió de proponer quedarnos con los parches más atendidos. La "
             "intuición era que si la atención ordena bien, quedarse con los de arriba tiene "
             "que capturar lo que buscamos. Y es falso, o por lo menos no se sigue. Un valor "
             "alto de área bajo la curva resume todos los umbrales a la vez; quedarse con los "
             "de arriba es un umbral solo, y de los extremos. Con la atención ordenando muy "
             "bien, los veinte parches más atendidos contenían tres de veintiocho mitosis, "
             "porque el percentil típico de esos parches deja al grueso bastante más abajo. La "
             "regla que queda es mirar el percentil de lo que uno quiere recuperar antes de "
             "elegir cuántos se queda, y declarar cuántos son alcanzables en el mejor caso.\n"
             "\n"
             "El segundo salió de la prueba de giro que conté hace un rato. Un control positivo "
             "sirve para lo obvio, que es comprobar que el instrumento mide. Tiene una segunda "
             "función que se nos había escapado: acota cuánto vale el estadístico cuando la "
             "respuesta es que sí. Sin eso, cualquier corte elegido mirando el grupo de estudio "
             "confunde no cumple mi corte con no hay efecto. En nuestro caso el corte que "
             "teníamos escrito rechazaba a tres de las cuatro láminas que sí funcionan, y eso "
             "lo descubrimos solamente porque se lo aplicamos al control antes que al resto.\n"
             "\n"
             "El tercero es el que conté al cerrar el recuento con giro. Una categoría "
             "definida por dos fallos "
             "simultáneos hereda todo lo que el instrumento no supo medir. Y si además uno "
             "amplía la población arreglando una etapa previa, entran las unidades más "
             "difíciles por construcción, esa categoría crece sola, y el crecimiento se lee "
             "como hallazgo. La defensa es separar esas unidades y mostrar por cuál de los dos "
             "criterios falló cada una.\n"
             "\n"
             "Los tres dicen lo mismo desde ángulos distintos, y es lo que puse abajo. En los "
             "tres casos el instrumento se estaba metiendo en la conclusión: el umbral en el "
             "primero, el corte en el segundo, la categoría en el tercero. Cuando un resultado "
             "sorprende, el primer sospechoso es la herramienta y no el mundo.\n"
             "\n"
             "Y el primero tiene un corolario que ya usamos: medir el techo de una prueba "
             "antes de pedir turno. Esta vez dio alto y la corrida se hizo igual, pero si "
             "hubiera dado bajo nos la ahorrábamos entera.")


def lam_que_sigue(prs):
    # ---- El cierre: lo que sigue y lo que bloquea ----
    s = content(prs, "Qué sigue")
    for i, txt in enumerate([
            "Cruzar las 177 mitosis contra las 26 marcas del patólogo, que es el segundo "
            "factor del techo y el único que faltaba medir.",
            "Lanzar el brazo de ensemble, que ahora es un solo envío con la fila vacía, y "
            "recién entonces comparar los dos brazos sobre la lámina anotada.",
            "Antes de extender a las doce láminas anotadas, coordinar: hay otro trabajo del "
            "equipo midiendo atención contra las mismas marcas."]):
        add_card(s, 0.35, TOP + 0.16 + i * 0.80, 9.28, 0.66, i + 1, txt, size=12.5)
    panel(s, 0.35, TOP + 2.54, 9.28, 0.90, "Y dos preguntas para vos", ONCO_DARK, [
        "De las treinta láminas anotadas que mencionaste, en el servidor hay doce. Faltan "
        "dieciocho, y no sabemos si existen o si están en otro lado.",
        "Las anotaciones vienen firmadas con tres iniciales que no sabemos de quién son."],
          ONCO_CONN, tsize=13, bsize=10.5)
    takeaway_bar(s, "El recuento cerró y la segmentación corrió; falta cruzarlas y comparar")
    notes(s, "Tres pasos, y los tres son cortos.\n"
             "Cruzar las 177 contra las 26 marcas es el segundo factor del techo.\n"
             "El brazo que falta es un solo envío, con la fila vacía.\n"
             "Y antes de extender, coordinar: hay otro trabajo del equipo midiendo lo mismo.\n"
             "\n"
             "Cierro con lo que sigue, y son tres cosas cortas.\n"
             "\n"
             "La primera es cruzar las detecciones de anoche contra las marcas del patólogo. "
             "Ése es exactamente el segundo factor del techo, el que hasta ayer no podíamos "
             "medir porque no había con qué. Ahora hay, y es trabajo de análisis, sin turno de "
             "cómputo de por medio.\n"
             "\n"
             "La segunda es lanzar el brazo que falta. La herramienta trae varios juegos de "
             "pesos: corrimos el que tiene clase de mitosis, y queda el otro, que promedia tres "
             "modelos y sirve de contraste. Con la fila vacía es un solo envío y menos de media "
             "hora. Recién con los dos se pueden comparar.\n"
             "\n"
             "La tercera es la que quería conversar. Cuando armé el bloque anterior creía que "
             "teníamos una sola lámina anotada; buscando en el servidor aparecieron doce, y "
             "eso cambia el tamaño de lo que se puede hacer. Antes de extender la medición a "
             "esas doce, conviene coordinar, porque hay otro trabajo del "
             "equipo que está midiendo atención contra las mismas marcas. Sería una pena "
             "duplicar el esfuerzo, y peor todavía llegar a dos números distintos sobre lo "
             "mismo sin saber por qué.\n"
             "\n"
             "Y quedan dos preguntas para vos, que no son retóricas. Mencionaste treinta "
             "láminas anotadas y en el servidor encontramos doce. Faltan dieciocho y no sabemos "
             "si existen, si están en otro lado o si el número era otro. La segunda es más "
             "chica pero conviene resolverla: las anotaciones vienen firmadas con tres "
             "iniciales, y no sabemos de quién son. Si vamos a apoyarnos en ese material, "
             "necesitamos saber quién lo anotó.")


# ============================================================================
# Orden pedido por Sebastián el 6-ago, y no se re-decide acá: abre el grid de
# expertos y slots, sigue la medición de atención contra las marcas del patólogo,
# y SI-MIL queda al final. Invierte la decisión del 3-ago (lo cerrado antes que lo
# vivo) y jubila el encuadre del 4-ago (el grid como sección de cierre): las dos
# eran de encuadre nuestro, ésta viene del supervisor.
def build():
    prs, keep_ids = base_from_template()
    prs.slide_width = Inches(SW); prs.slide_height = Inches(SH)

    lam_portada(prs)

    # ---- el grid abre ----
    lam_grid(prs)

    # ---- la medición de atención ----
    lam_pregunta_medible(prs)
    lam_mapas(prs)
    lam_escalera(prs)
    lam_28_parches(prs)
    lam_mira_responde(prs)
    lam_controles(prs)

    # ---- SI-MIL, al final ----
    lam_simil_propone(prs)
    lam_simil_ramas(prs)
    lam_simil_reporte(prs)
    lam_simil_resultados(prs)

    # ---- cierre del bloque del 6-ago ----
    lam_objetivos_propuestos(prs)

    # ---- lo hecho desde el 6-ago, en orden cronológico (elección de Ernesto, 18-ago) ----
    lam_desde_6ago(prs)
    lam_regiones_pregunta(prs)
    lam_regiones_metodo(prs)
    lam_regiones_mitad(prs)
    lam_regiones_perfil(prs)
    lam_regiones_rotacion(prs)
    lam_regiones_rebarrido(prs)
    lam_hovernext_estado(prs)
    lam_techo(prs)
    lam_gpu(prs)
    lam_patrones(prs)
    lam_que_sigue(prs)

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
