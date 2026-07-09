#!/usr/bin/env python
"""generate_b6_deck.py — deck de la reunión del VIERNES (B6): mammoth / interpretabilidad OBJ-A.

Formato = deck B4 (10x5.625 in, Barlow, paleta teal) — corrige el formato que Benjamín
rechazó del B5 (13.333, Carlito). Contenido = mecanismo mammoth (slides B5 re-formateadas)
+ interpretabilidad OBJ-A (material nuevo del run 30-jun). Eje = ENTENDIMIENTO (no rendimiento).

- Slides de OBJETIVOS/contenido → NATIVAS en Barlow a tamaños B4 (el fix de Benjamín).
- Diagramas de arquitectura → reusados de los .pptx standalone, ESCALADOS x0.75 a 10x5.625
  (mismo aspect ratio; conservan Carlito, convención aceptada para diagramas). Editables.
- Figuras de interpretabilidad (heatmap/top-k/cross-slide) y del paper → como imagen (excepción).
- Notas del presentador → guion HABLADO en prosa (sin etiquetas de fase, sin nº de job/nombres).

Uso:
  PYTHONPATH=/media/administrador/Storage1/sdonoso/clam_testing2/.pylibs \
  /home/sdonoso/miniconda3/envs/clam_latest/bin/python \
    sprints/B6_sprint6/presentacion_viernes/generate_b6_deck.py
"""
import copy
import io
import os

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from PIL import Image

REPO = "/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto"
PRES = os.path.join(REPO, "papers/presentations")
ASSETS_BRAND = os.path.join(PRES, "assets_branding")
PAPER_FIGS = os.path.join(ASSETS_BRAND, "paper_figs")
OBJA = os.path.join(REPO, "sprints/B5_sprint5/mammoth_entendimiento/interpretabilidad")
OUT_DIR = os.path.join(REPO, "sprints/B6_sprint6/presentacion_viernes")
DST = os.path.join(OUT_DIR, "CLAM_Reunion_Mammoth.pptx")

# --- diagramas standalone (13.333x7.5, sin header) que reusamos escalados ---
DIAG_MAM = os.path.join(PRES, "Diagrama_CLAM_mammoth.pptx")     # s0 pipeline · s1 interior/tensor
DIAG_FUSED = os.path.join(PRES, "Diagrama_mammoth_fused.pptx")  # s1 keep_slots
# --- figuras ---
FIG1_MAM = os.path.join(PAPER_FIGS, "mammoth_fig1_overview.png")  # t-SNE + barras (paper Fig 1)
FIG3_MAM = os.path.join(PAPER_FIGS, "mammoth_fig3_routing.png")   # ruteo→fenotipo (paper Fig 3)
A14Q = os.path.join(OBJA, "TCGA-E2-A14Q-01Z-00-DX1_cdis_f0")
HEATMAP_MONTAGE = os.path.join(A14Q, "heatmap_montage.png")
TOPK_SUBSET = os.path.join(A14Q, "topk_subset_6experts.png")
XSLIDE_E8 = os.path.join(OBJA, "cross_slide/expert_08_crossslide.png")
XSLIDE_E26 = os.path.join(OBJA, "cross_slide/expert_26_crossslide.png")

# ---- paleta B4 (valores reales del deck) ----
TEAL_TITLE = RGBColor(0x21, 0x75, 0x89)
TEAL_SQ    = RGBColor(0x31, 0x85, 0x9C)
BAR_GRIS   = RGBColor(0xF2, 0xF2, 0xF2)
TEAL_DIV   = RGBColor(0x2E, 0x7E, 0x8F)
LAV_TITLE  = RGBColor(0xCD, 0xD6, 0xF4)
TEAL_SUB   = RGBColor(0xB8, 0xD4, 0xD9)
TEAL_CARD  = RGBColor(0xDD, 0xEA, 0xEE)
TEAL_CARD2 = RGBColor(0xF3, 0xF8, 0xF9)
GRIS_BODY  = RGBColor(0x59, 0x59, 0x59)
GRIS_TXT   = RGBColor(0x55, 0x55, 0x55)
ORA_T      = RGBColor(0xB4, 0x52, 0x1E)
ORA_ACC    = RGBColor(0xE2, 0x72, 0x3B)
VERDE      = RGBColor(0x1E, 0x84, 0x49)
ROJO       = RGBColor(0xC0, 0x39, 0x2B)
INK        = RGBColor(0x22, 0x22, 0x22)
WHITE      = RGBColor(0xFF, 0xFF, 0xFF)

F_TITLE = "Barlow ExtraBold"
F_BODY  = "Barlow"

# --- geometría B4 (10 x 5.625), extraída del volcado real ---
SW, SH = 10.0, 5.625
HDR = 0.785
LOGO = os.path.join(ASSETS_BRAND, "logo_header.png")
PORTADA = os.path.join(ASSETS_BRAND, "portada_fullbleed.jpg")
_uid = [2000]


# ============================================================================
# Helpers base
# ============================================================================
def _blank(prs):
    for lay in prs.slide_layouts:
        if (lay.name or "").lower().strip() == "blank":
            return lay
    return prs.slide_layouts[6]


def _set_runs(tf, lines, anchor=MSO_ANCHOR.TOP):
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    for i, ln in enumerate(lines):
        txt, sz, bold, col = ln[0], ln[1], ln[2], ln[3]
        font = ln[4] if len(ln) > 4 else F_BODY
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = ln[5] if len(ln) > 5 else PP_ALIGN.LEFT
        p.space_after = Pt(4)
        r = p.add_run(); r.text = txt
        r.font.size = Pt(sz); r.font.bold = bold; r.font.name = font; r.font.color.rgb = col


def add_textbox(slide, l, t, w, h, lines, anchor=MSO_ANCHOR.TOP):
    tb = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    _set_runs(tb.text_frame, lines, anchor=anchor)
    return tb


def notes(slide, text):
    """Guion HABLADO en prosa (sin etiquetas de fase, sin nº de job ni nombres)."""
    slide.notes_slide.notes_text_frame.text = text


def _rect(slide, l, t, w, h, color):
    sp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(l), Inches(t), Inches(w), Inches(h))
    sp.fill.solid(); sp.fill.fore_color.rgb = color
    sp.line.fill.background(); sp.shadow.inherit = False
    return sp


def logo_mark(slide, size=0.785, logo_h=0.645):
    _rect(slide, 0, 0, size, size, TEAL_SQ)
    slide.shapes.add_picture(LOGO, Inches(0.065), Inches(0.045), height=Inches(logo_h))


def header(slide, title, bar=True):
    """Header B4: barra gris + cuadrado teal + logo + título Barlow ExtraBold teal."""
    if bar:
        _rect(slide, 0.0, 0.0, SW, HDR, BAR_GRIS)
    logo_mark(slide)
    if title:
        tb = slide.shapes.add_textbox(Inches(0.99), Inches(0.12), Inches(8.85), Inches(0.56))
        _set_runs(tb.text_frame, [(title, 26, True, TEAL_TITLE, F_TITLE)], anchor=MSO_ANCHOR.MIDDLE)


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
    """Tarjeta numerada estilo B4: óvalo naranja + texto Barlow."""
    fill = TEAL_CARD if idx % 2 == 0 else TEAL_CARD2
    sp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(l), Inches(t), Inches(w), Inches(h))
    sp.fill.solid(); sp.fill.fore_color.rgb = fill
    sp.line.color.rgb = TEAL_SQ; sp.line.width = Pt(1.25); sp.shadow.inherit = False
    cd = 0.44
    circ = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(l + 0.16), Inches(t + (h - cd) / 2),
                                  Inches(cd), Inches(cd))
    circ.fill.solid(); circ.fill.fore_color.rgb = ORA_ACC
    circ.line.fill.background(); circ.shadow.inherit = False
    _set_runs(circ.text_frame, [(str(idx), 15, True, WHITE, F_TITLE, PP_ALIGN.CENTER)],
              anchor=MSO_ANCHOR.MIDDLE)
    tb = slide.shapes.add_textbox(Inches(l + 0.74), Inches(t), Inches(w - 0.88), Inches(h))
    _set_runs(tb.text_frame, [(text, size, True, INK, F_BODY)], anchor=MSO_ANCHOR.MIDDLE)


def caption(slide, l, t, w, text, size=11, col=GRIS_TXT, align=PP_ALIGN.CENTER, bold=False):
    add_textbox(slide, l, t, w, 0.4, [(text, size, bold, col, F_BODY, align)])


# ============================================================================
# Arquetipos B4
# ============================================================================
def portada(prs, title, subtitle):
    s = prs.slides.add_slide(_blank(prs))
    s.shapes.add_picture(PORTADA, Inches(0), Inches(-0.02), Inches(SW), Inches(SH + 0.04))
    # banda translúcida no: título sobre la imagen (caja de texto blanca con leve panel)
    panel = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.0), Inches(3.55), Inches(SW), Inches(1.35))
    panel.fill.solid(); panel.fill.fore_color.rgb = TEAL_DIV
    panel.fill.transparency = 0  # sólido
    panel.line.fill.background(); panel.shadow.inherit = False
    _set_alpha(panel, 62000)  # ~62% opaco
    add_textbox(s, 0.6, 3.62, SW - 1.2, 0.8,
                [(title, 30, True, WHITE, F_TITLE, PP_ALIGN.LEFT)], anchor=MSO_ANCHOR.MIDDLE)
    add_textbox(s, 0.62, 4.42, SW - 1.2, 0.45,
                [(subtitle, 15, False, LAV_TITLE, F_BODY, PP_ALIGN.LEFT)], anchor=MSO_ANCHOR.TOP)
    return s


def _set_alpha(shape, alpha):
    """Transparencia del relleno sólido (alpha en 1/1000 %: 62000 = 62%)."""
    sp = shape.fill._xPr.find(qn("a:solidFill"))
    srgb = sp.find(qn("a:srgbClr"))
    a = srgb.makeelement(qn("a:alpha"), {"val": str(alpha)})
    srgb.append(a)


def divider(prs, title, subtitle):
    s = prs.slides.add_slide(_blank(prs))
    s.background.fill.solid(); s.background.fill.fore_color.rgb = TEAL_DIV
    s.shapes.add_picture(LOGO, Inches(0.42), Inches(0.36), height=Inches(0.62))
    add_textbox(s, 0.8, 2.05, SW - 1.6, 1.1,
                [(title, 44, True, LAV_TITLE, F_TITLE, PP_ALIGN.CENTER)], anchor=MSO_ANCHOR.MIDDLE)
    add_textbox(s, 0.8, 3.25, SW - 1.6, 0.7,
                [(subtitle, 18, False, TEAL_SUB, F_BODY, PP_ALIGN.CENTER)], anchor=MSO_ANCHOR.TOP)
    return s


def content(prs, title, bar=True):
    s = prs.slides.add_slide(_blank(prs))
    header(s, title, bar=bar)
    return s


def _scale_el(el, s):
    """Escala geométrica (off/ext) y tipográfica (sz) de un shape XML por factor s."""
    for off in el.iter(qn("a:off")):
        off.set("x", str(int(int(off.get("x")) * s)))
        off.set("y", str(int(int(off.get("y")) * s)))
    for ext in el.iter(qn("a:ext")):
        ext.set("cx", str(int(int(ext.get("cx")) * s)))
        ext.set("cy", str(int(int(ext.get("cy")) * s)))
    for tag in ("a:rPr", "a:defRPr", "a:endParaRPr"):
        for rpr in el.iter(qn(tag)):
            sz = rpr.get("sz")
            if sz:
                rpr.set("sz", str(max(100, int(int(sz) * s))))


def copy_diagram_scaled(prs, src_path, idx, title=None, scale=0.75, bar=False):
    """Copia el diagrama standalone (13.333x7.5) escalado a 10x5.625 (x0.75, full-bleed).
    Conserva nativo/editable + remapea imágenes embebidas. Header opcional (logo only por defecto)."""
    s = prs.slides.add_slide(_blank(prs))
    src = Presentation(src_path)
    src_slide = src.slides[idx]
    spTree = s.shapes._spTree
    for shp in src_slide.shapes:
        el = copy.deepcopy(shp._element)
        for cNvPr in el.iter(qn("p:cNvPr")):
            _uid[0] += 1; cNvPr.set("id", str(_uid[0]))
        for blip in el.iter(qn("a:blip")):
            r_embed = blip.get(qn("r:embed"))
            if r_embed:
                img_part = src_slide.part.related_part(r_embed)
                _, new_rid = s.part.get_or_add_image_part(io.BytesIO(img_part.blob))
                blip.set(qn("r:embed"), new_rid)
        _scale_el(el, scale)
        spTree.append(el)
    header(s, title, bar=bar)  # logo mark (+ barra/título si se pide)
    return s


# ============================================================================
# Build
# ============================================================================
def build():
    prs = Presentation()
    prs.slide_width = Inches(SW); prs.slide_height = Inches(SH)

    # ---- 1. Portada ----
    s = portada(prs, "MAMMOTH — qué mira por dentro",
                "Interpretabilidad de expertos y slots · CLAM con Mixture-of-Experts en el patch-embed")
    notes(s, "Hoy no vengo a decir que mammoth mejora la métrica: eso ya lo cerramos, no es "
             "una palanca de rendimiento. Vengo a mostrar qué aprende y qué mira mammoth por "
             "dentro, que es una pregunta distinta y que quedó abierta. Voy a explicar primero "
             "el mecanismo, con calma esta vez, y después voy a enseñar con imágenes en qué se "
             "fija cada experto sobre nuestras propias slides de mama.")

    # ---- 2. Divisoria: MAMMOTH ----
    s = divider(prs, "MAMMOTH", "Mixture-of-Experts en la primera capa de CLAM (patch-embed)")
    notes(s, "Arrancamos por el mecanismo. Mammoth es una intervención quirúrgica en la primera "
             "capa de CLAM, la que proyecta los parches. Nada más de CLAM se toca.")

    # ---- 3. Qué es y por qué (nativo Barlow: 4 tarjetas + Fig 1 del paper) ----
    s = content(prs, "MAMMOTH — qué es y por qué")
    cards = [
        "Reemplaza la 1ª capa lineal de CLAM por una mezcla de expertos (MoE).",
        "Un router envía cada parche a expertos especializados por morfología.",
        "Objetivo: reducir la interferencia de gradientes entre parches.",
        "El resto de CLAM no cambia → comparación limpia.",
    ]
    cy = 1.02
    for i, txt in enumerate(cards):
        add_card(s, 0.30, cy, 5.55, 0.86, i + 1, txt, size=13)
        cy += 0.96
    add_image_fit(s, FIG1_MAM, 6.05, 1.0, 3.75, 3.55, align="top")
    caption(s, 6.05, 4.62, 3.75,
            "Fig. 1 — el espacio interno pasa de una nube continua a grupos por experto,\n"
            "y mejora a todos los agregadores MIL (Shao et al., ICLR 2026)", size=9)
    notes(s, "En CLAM, una sola capa lineal proyecta todos los parches al espacio interno del "
             "modelo. Esa única matriz tiene que servir para epitelio, estroma y ductos a la vez, "
             "así que queda mediocre para todo. La analogía es un solo traductor obligado a "
             "traducir chino, árabe y ruso con la misma plantilla. Mammoth contrata treinta "
             "traductores especialistas y un recepcionista, el router, que decide cuánto de cada "
             "parche mandar a cada especialista. La figura de la derecha es la evidencia del "
             "paper: a la izquierda el espacio se separa en grupos, uno por experto, y a la "
             "derecha se ve que la mejora es transversal a todos los agregadores. Lo importante "
             "para nosotros es la última tarjeta: el resto de CLAM queda intacto, así que la "
             "comparación es limpia.")

    # ---- 4. Diagrama: pipeline CLAM + punto de integración (reusado, escalado) ----
    s = copy_diagram_scaled(prs, DIAG_MAM, 0, title=None, bar=False)
    notes(s, "Este es el pipeline completo de CLAM. Entra la slide como parches, el extractor "
             "CONCH le da a cada parche un vector de quinientos doce números, y de ahí siguen la "
             "atención y el clasificador. El único bloque que cambia es el naranja: ahí es donde "
             "mammoth reemplaza la primera capa lineal. Todo lo demás es CLAM tal cual.")

    # ---- 5. Diagrama: interior de MAMMOTH — el tensor 30x16x10x16 (reusado, escalado) ----
    s = copy_diagram_scaled(prs, DIAG_MAM, 1, title=None, bar=False)
    notes(s, "Este es el interior de mammoth, y es la parte que se me cayó la vez pasada, así "
             "que la voy a decir despacio. Los parches entran como un query. Ese query se compara "
             "con unos prototipos aprendidos: el tensor de treinta por dieciséis por diez por "
             "dieciséis. Se lee así: treinta expertos, cada uno con dieciséis cabezas, cada cabeza "
             "con diez slots, y cada slot es un vector de dieciséis. El dieciséis aparece dos "
             "veces porque el número de cabezas y la dimensión de cada prototipo tienen que "
             "coincidir para poder compararlos con un producto interno. En total son trescientos "
             "slots. El router reparte cada parche entre esos slots con una softmax, cada experto "
             "los procesa con una transformación de bajo rango, y al final se recombina todo y se "
             "reconstruyen los parches. Una aclaración importante: las cabezas no son textura, "
             "forma y color; son subespacios aprendidos, como en atención multi-cabeza. La "
             "semántica de tejido no vive en las cabezas, vive en los slots.")

    # ---- 6. keep_slots: dónde se bifurca la salida (reusado, escalado) ----
    s = copy_diagram_scaled(prs, DIAG_FUSED, 1, title="MAMMOTH — la variante keep_slots", bar=True)
    notes(s, "Hay una variante, keep_slots, que en vez de reconstruir los parches se queda con "
             "los trescientos slots como salida. La menciono para completar el mecanismo, pero es "
             "una variante de rendimiento; para lo de hoy, que es entender qué mira el modelo, la "
             "interpretabilidad se calcula antes de esta bifurcación y vale igual para las dos.")

    # ---- 7. Divisoria: Interpretabilidad (OBJ-A) ----
    s = divider(prs, "¿Qué mira cada experto?",
                "Interpretabilidad post-hoc sobre un checkpoint entrenado · 4 slides TCGA-BRCA")
    notes(s, "Con el mecanismo claro, pasamos a lo nuevo: mirar, sobre nuestras propias slides, "
             "qué región reclama cada experto y qué morfología hay ahí. Es análisis post-hoc en "
             "CPU sobre un modelo ya entrenado, no reentrena nada.")

    # ---- 8. Ruteo espacial: heatmaps por experto ----
    s = content(prs, "Ruteo espacial — cada experto reclama regiones distintas")
    add_image_fit(s, HEATMAP_MONTAGE, 0.30, 0.95, 6.7, 4.35, align="top")
    add_textbox(s, 7.15, 1.05, 2.65, 4.2, [
        ("Cada panel = la slide pintada por cuánto el router manda cada parche a ese experto.",
         13, True, INK, F_BODY),
        ("Los 30 encienden regiones distintas → la capa única se volvió especialistas "
         "espaciales.", 12, False, GRIS_BODY, F_BODY),
        ("Color = percentil por experto: muestra estructura relativa, no magnitud de uso.",
         11, False, ORA_T, F_BODY),
    ], anchor=MSO_ANCHOR.TOP)
    notes(s, "Cada uno de estos treinta cuadros es la misma slide, pintada según cuánto el "
             "router manda cada parche a un experto. Rojo es mucho, azul es casi nada. Lo que "
             "importa es que los treinta encienden zonas distintas: la capa lineal única se "
             "reemplazó por especialistas que miran regiones diferentes del tejido. Un aviso "
             "honesto: el color está normalizado por percentil dentro de cada experto, así que "
             "sirve para ver dónde prefiere mirar cada uno, no para decir cuál se usa más. Eso "
             "por separado sale casi uniforme: no hay expertos muertos ni acaparadores.")

    # ---- 9. Morfología por experto: top-k ----
    s = content(prs, "Morfología por experto — del «dónde» al «qué»")
    add_image_fit(s, TOPK_SUBSET, 0.30, 0.95, 6.5, 4.4, align="top")
    add_textbox(s, 6.95, 1.05, 2.85, 4.2, [
        ("El top-k recorta a alta resolución los parches que cada experto más rutea.", 13, True, INK, F_BODY),
        ("e8 → epitelio tumoral", 13, True, TEAL_TITLE, F_BODY),
        ("e26 → estroma fibroso", 13, True, TEAL_TITLE, F_BODY),
        ("e3 → epitelio ductal", 13, True, TEAL_TITLE, F_BODY),
        ("Heatmap = dónde; top-k = qué morfología.", 12, False, GRIS_BODY, F_BODY),
        ("Emergió sin supervisión de tejido (paper Fig 3, validado por patólogos).",
         11, False, ORA_T, F_BODY),
    ], anchor=MSO_ANCHOR.TOP)
    notes(s, "El mapa de calor dice dónde, pero no qué tejido hay ahí. El top-k cierra ese "
             "hueco: para cada experto tomo los parches que más rutea y los recorto a alta "
             "resolución para mirarlos con los ojos. Se ve directo: el experto ocho mira nidos de "
             "epitelio tumoral, el veintiséis mira estroma fibroso rosado, el tres mira ductos. "
             "Es la misma especialización que el paper validó con dos patólogos, y lo notable es "
             "que emerge sola durante el entrenamiento, nadie le dijo al modelo qué es estroma. "
             "Los expertos mixtos que se ven son esperables, porque el ruteo es suave y reparte "
             "cada parche entre varios.")

    # ---- 10. Estabilidad cross-slide → morfología ≠ clase ----
    s = content(prs, "Estabilidad cross-slide — el experto detecta tejido, no clase")
    add_image_fit(s, XSLIDE_E8, 0.30, 0.95, 6.4, 2.05, align="top")
    add_image_fit(s, XSLIDE_E26, 0.30, 3.10, 6.4, 2.05, align="top")
    caption(s, 0.30, 5.18, 6.4, "e8 (epitelio) y e26 (estroma), cada uno en las 4 slides — 2 positivas + 2 negativas", size=9, align=PP_ALIGN.LEFT)
    add_textbox(s, 6.85, 1.05, 2.95, 4.2, [
        ("El mismo experto elige la misma morfología en las 4 slides — incluidas las negativas.",
         13, True, INK, F_BODY),
        ("«Negativo» = cdis sin microcalcificación, no «sin tumor» → sigue habiendo epitelio.",
         12, False, GRIS_BODY, F_BODY),
        ("Un experto es un detector de TEJIDO, no de clase. La clase se decide después "
         "(atención + clasificador).", 12, True, ORA_T, F_BODY),
    ], anchor=MSO_ANCHOR.TOP)
    notes(s, "Como los prototipos son parámetros compartidos del modelo, el experto ocho es el "
             "mismo experto en todas las slides. Entonces hay una prueba limpia: si su "
             "especialización es real, tiene que elegir la misma morfología en todas. Y así es: "
             "el ocho enciende epitelio en las cuatro, el veintiséis estroma en las cuatro, "
             "incluidas las negativas. La clave es que negativo acá quiere decir cdis sin "
             "microcalcificación, no sin tumor: siguen siendo slides de mama con epitelio. Es "
             "decir, el experto detecta tejido, no clase. La decisión de si la slide es positiva "
             "viene después, en la atención y el clasificador.")

    # ---- 11. Honestidad + cierre (dos ejes ortogonales) ----
    s = content(prs, "Lo que muestra — y lo que todavía falta")
    add_textbox(s, 0.35, 1.0, 4.55, 4.3, [
        ("Lo que sí afirmamos", 16, True, TEAL_TITLE, F_TITLE),
        ("Los expertos se especializan por morfología (epitelio, estroma, ducto).", 13, False, INK, F_BODY),
        ("La especialización es estable entre slides.", 13, False, INK, F_BODY),
        ("Detectan tejido, no clase → confirma que el cuello no está en la 1ª capa.", 13, False, INK, F_BODY),
    ], anchor=MSO_ANCHOR.TOP)
    add_textbox(s, 5.15, 1.0, 4.5, 4.3, [
        ("Honestidad", 16, True, ORA_T, F_TITLE),
        ("Cala cualitativa: 4 slides, 1 tarea, 1 fold.", 13, False, GRIS_BODY, F_BODY),
        ("Etiquetas de tejido provisionales → falta sign-off de patólogo.", 13, False, GRIS_BODY, F_BODY),
        ("Dos ejes ortogonales: rendimiento (cerrado) vs entendimiento (abierto).", 13, True, INK, F_BODY),
    ], anchor=MSO_ANCHOR.TOP)
    _rect(s, 0.35, 4.75, SW - 0.7, 0.02, TEAL_SQ)
    add_textbox(s, 0.35, 4.85, SW - 0.7, 0.6, [
        ("Mostrar qué mira mammoth no reabre el veredicto de rendimiento — le da un mecanismo.",
         14, True, TEAL_TITLE, F_BODY, PP_ALIGN.CENTER)], anchor=MSO_ANCHOR.MIDDLE)
    notes(s, "Cierro con lo que sí puedo afirmar y lo que falta. Sí: los expertos se especializan "
             "por morfología, de forma estable, y detectan tejido y no clase. Eso último es "
             "justamente la evidencia de que el cuello de botella no está en la primera capa, "
             "sino en el dato. La honestidad: es una cala chica, cuatro slides, una tarea, y las "
             "etiquetas de tejido todavía son mías, faltan los ojos de un patólogo. Y lo más "
             "importante para no confundir: son dos ejes distintos. Que mammoth no mejore la "
             "métrica está cerrado; qué aprende por dentro está abierto, y es lo que traje. "
             "Mostrar qué mira no reabre nada, le pone un mecanismo.")

    os.makedirs(OUT_DIR, exist_ok=True)
    prs.save(DST)
    print("Guardado:", DST, "·", len(prs.slides), "slides")


if __name__ == "__main__":
    build()
