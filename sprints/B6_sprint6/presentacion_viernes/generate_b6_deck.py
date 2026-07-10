#!/usr/bin/env python
"""generate_b6_deck.py — deck de la reunión del VIERNES (B6): mammoth / interpretabilidad OBJ-A.

Formato = deck B4 (10x5.625 in, Barlow, paleta teal) — corrige el formato que Benjamín
rechazó del B5 (13.333, Carlito). Contenido = mecanismo mammoth (slides B5 re-formateadas)
+ interpretabilidad OBJ-A (material nuevo del run 30-jun). Eje = ENTENDIMIENTO (no rendimiento).

- Slides de OBJETIVOS/contenido → NATIVAS en Barlow a tamaños B4 (el fix de Benjamín).
- Diagramas de arquitectura → reusados de los .pptx standalone, ESCALADOS x0.75 a 10x5.625
  (mismo aspect ratio; conservan Carlito, convención aceptada para diagramas). Editables.
- Slides de mecanismo (interior/tensor, keep_slots) → NATIVAS con matrices+dims Y código real
  de mammoth.py en paralelo (pedido de Ernesto para la reunión).
- Figuras de interpretabilidad (heatmap/top-k/cross-slide) y del paper → como imagen (excepción).
- Notas del presentador → guion HABLADO en prosa (sin etiquetas de fase, sin nº de job/nombres),
  integrando las explicaciones del estudio (5 bloques de estudio_reunion_viernes.md).

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
DIAG_FUSED = os.path.join(PRES, "Diagrama_mammoth_fused.pptx")  # s0 flujo oficial · s1 keep_slots
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
CODE_BG    = RGBColor(0x1E, 0x2A, 0x2E)   # panel de código (teal muy oscuro)
CODE_FG    = RGBColor(0xE6, 0xEE, 0xF0)   # texto de código
CODE_CMT   = RGBColor(0x8F, 0xB8, 0xC0)   # comentarios de código
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
F_MONO  = "Consolas"

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


def _rect(slide, l, t, w, h, color, line=None):
    sp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(l), Inches(t), Inches(w), Inches(h))
    sp.fill.solid(); sp.fill.fore_color.rgb = color
    if line is None:
        sp.line.fill.background()
    else:
        sp.line.color.rgb = line; sp.line.width = Pt(1)
    sp.shadow.inherit = False
    return sp


def logo_mark(slide, size=0.785, logo_h=0.645):
    _rect(slide, 0, 0, size, size, TEAL_SQ)
    slide.shapes.add_picture(LOGO, Inches(0.065), Inches(0.045), height=Inches(logo_h))


def header(slide, title, bar=True, size=26):
    """Header B4: barra gris + cuadrado teal + logo + título Barlow ExtraBold teal."""
    if bar:
        _rect(slide, 0.0, 0.0, SW, HDR, BAR_GRIS)
    logo_mark(slide)
    if title:
        tb = slide.shapes.add_textbox(Inches(0.99), Inches(0.10), Inches(8.9), Inches(0.62))
        _set_runs(tb.text_frame, [(title, size, True, TEAL_TITLE, F_TITLE)], anchor=MSO_ANCHOR.MIDDLE)


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


def takeaway_bar(slide, text, t=4.85, col=TEAL_TITLE, size=14):
    """Barra de remate al pie (línea teal + frase centrada)."""
    _rect(slide, 0.35, t, SW - 0.7, 0.02, TEAL_SQ)
    add_textbox(slide, 0.35, t + 0.08, SW - 0.7, 0.62,
                [(text, size, True, col, F_BODY, PP_ALIGN.CENTER)], anchor=MSO_ANCHOR.MIDDLE)


def code_panel(slide, l, t, w, h, lines, title=None):
    """Panel de código nativo: fondo oscuro + texto monoespaciado (Consolas).
    `lines` = lista de strings; los que empiezan con '#' se pintan como comentario."""
    _rect(slide, l, t, w, h, CODE_BG)
    tb = slide.shapes.add_textbox(Inches(l + 0.12), Inches(t + 0.08), Inches(w - 0.24), Inches(h - 0.16))
    tf = tb.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_ANCHOR.TOP
    runs = []
    if title:
        runs.append((title, 10, True, CODE_CMT, F_MONO))
    for ln in lines:
        col = CODE_CMT if ln.strip().startswith("#") else CODE_FG
        runs.append((ln if ln else " ", 9.5, False, col, F_MONO))
    _set_runs(tf, runs)
    for p in tf.paragraphs:
        p.space_after = Pt(1)
    return tb


def dims_table(slide, l, t, w, rows, row_h=0.345, hdr=("paso", "forma del tensor")):
    """Tabla nativa de dimensiones (2 columnas: descripción del paso · forma)."""
    n = len(rows) + 1
    gtbl = slide.shapes.add_table(n, 2, Inches(l), Inches(t), Inches(w), Inches(row_h * n)).table
    gtbl.columns[0].width = Inches(w * 0.60)
    gtbl.columns[1].width = Inches(w * 0.40)
    gtbl.first_row = False; gtbl.horz_banding = False
    data = [hdr] + list(rows)
    for ri, (c0, c1) in enumerate(data):
        for ci, txt in enumerate((c0, c1)):
            cell = gtbl.cell(ri, ci)
            cell.margin_left = Inches(0.06); cell.margin_right = Inches(0.04)
            cell.margin_top = Inches(0.01); cell.margin_bottom = Inches(0.01)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            if ri == 0:
                cell.fill.solid(); cell.fill.fore_color.rgb = TEAL_SQ
                col, bold, sz, fnt = WHITE, True, 9.5, F_BODY
            else:
                cell.fill.solid(); cell.fill.fore_color.rgb = TEAL_CARD2 if ri % 2 else TEAL_CARD
                col = INK if ci == 0 else TEAL_TITLE
                bold = ci == 1; sz = 9.5; fnt = F_BODY if ci == 0 else F_MONO
            tf = cell.text_frame; tf.word_wrap = True
            p = tf.paragraphs[0]; p.alignment = PP_ALIGN.LEFT
            r = p.add_run(); r.text = txt
            r.font.size = Pt(sz); r.font.bold = bold; r.font.name = fnt; r.font.color.rgb = col
    return gtbl


# ============================================================================
# Arquetipos B4
# ============================================================================
def portada(prs):
    """Portada B4: imagen full-bleed limpia, sin overlay (el título va horneado en la imagen)."""
    s = prs.slides.add_slide(_blank(prs))
    s.shapes.add_picture(PORTADA, Inches(0), Inches(-0.02), Inches(SW), Inches(SH + 0.04))
    return s


def divider(prs, title, subtitle):
    s = prs.slides.add_slide(_blank(prs))
    s.background.fill.solid(); s.background.fill.fore_color.rgb = TEAL_DIV
    s.shapes.add_picture(LOGO, Inches(0.42), Inches(0.36), height=Inches(0.62))
    add_textbox(s, 0.8, 2.05, SW - 1.6, 1.1,
                [(title, 44, True, LAV_TITLE, F_TITLE, PP_ALIGN.CENTER)], anchor=MSO_ANCHOR.MIDDLE)
    add_textbox(s, 0.8, 3.25, SW - 1.6, 0.7,
                [(subtitle, 18, False, TEAL_SUB, F_BODY, PP_ALIGN.CENTER)], anchor=MSO_ANCHOR.TOP)
    return s


def content(prs, title, bar=True, size=26):
    s = prs.slides.add_slide(_blank(prs))
    header(s, title, bar=bar, size=size)
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

    # ---- 1. Portada (limpia, sin overlay) ----
    s = portada(prs)
    notes(s, "Hoy no vengo a decir que mammoth mejora la métrica: eso ya lo cerramos, no es "
             "una palanca de rendimiento. Lo que traigo es qué aprende y qué mira mammoth por "
             "dentro, que es una pregunta distinta y quedó abierta. Primero el mecanismo, con "
             "calma esta vez, y después las imágenes de en qué se fija cada experto sobre "
             "nuestras propias slides de mama.")

    # ---- 2. Recapitulación de objetivos (MISMO formato que B4 slide 2:
    #        título 32pt + lista numerada en un solo cuadro, 24pt Barlow bold gris) ----
    s = content(prs, "Recapitulación de objetivos", size=32)
    recap = [
        "1. Cerramos cuatro ejes de arquitectura y objetivo (agregador, mammoth, PathPT, "
        "loss): ninguno movió la métrica.",
        "2. Cero palancas de rendimiento: el cuello de botella es el dato, no la arquitectura.",
        "3. Se abren dos frentes: magnificación multi-escala e interpretar qué aprende mammoth.",
        "4. Hoy traigo el segundo eje: entender mammoth por dentro, no rendimiento.",
    ]
    tb = s.shapes.add_textbox(Inches(0.35), Inches(1.20), Inches(9.30), Inches(3.95))
    tf = tb.text_frame; tf.word_wrap = True
    for i, it in enumerate(recap):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT; p.space_after = Pt(18)
        r = p.add_run(); r.text = it
        r.font.size = Pt(24); r.font.bold = True; r.font.name = F_BODY; r.font.color.rgb = GRIS_BODY
    notes(s, "Antes de entrar en mammoth, ubico la reunión. En los últimos sprints probamos "
             "cuatro maneras distintas de cambiar el modelo: cambiar el agregador, meter una "
             "mezcla de expertos en la primera capa —que es mammoth—, usar lenguaje sobre los "
             "parches con PathPT, y cambiar la función de pérdida para el desbalance. Ninguna de "
             "las cuatro movió la métrica. Y las cuatro apuntan al mismo lugar: el problema no "
             "está en la arquitectura, está en el dato, en el desbalance y en la falta de "
             "contexto espacial. De ahí salen dos caminos: uno es inyectar señal nueva con "
             "magnificación multi-escala, que es el frente que estamos armando ahora; el otro es "
             "entender qué aprende mammoth por dentro. Hoy vengo con el segundo.")

    # ---- 3. Divisoria: MAMMOTH ----
    s = divider(prs, "MAMMOTH", "Mixture-of-Experts en la primera capa de CLAM (patch-embed)")
    notes(s, "Arrancamos por el mecanismo. Mammoth es una intervención quirúrgica en la primera "
             "capa de CLAM, la que proyecta los parches. Nada más de CLAM se toca.")

    # ---- 4. Qué es y por qué (título = acrónimo completo; 3 tarjetas + Fig 1 + Fig 3) ----
    s = content(prs, "MAMMOTH — MAtrix-factorized Mixture Module of Transformation Heads", size=17)
    cards = [
        "Reemplaza la 1ª capa lineal de CLAM por una mezcla de expertos (MoE).",
        "Un router reparte cada parche entre expertos especializados por morfología.",
        "Objetivo: bajar la interferencia de gradientes entre parches distintos.",
    ]
    cy = 1.05
    for i, txt in enumerate(cards):
        add_card(s, 0.30, cy, 5.35, 0.95, i + 1, txt, size=13)
        cy += 1.10
    add_image_fit(s, FIG1_MAM, 5.95, 0.98, 3.85, 1.85, align="top")
    caption(s, 5.95, 2.86, 3.85,
            "Fig. 1 — el espacio interno pasa de una nube continua a grupos por experto,\n"
            "y mejora a todos los agregadores MIL (Shao et al., ICLR 2026)", size=8)
    add_image_fit(s, FIG3_MAM, 5.95, 3.42, 3.85, 1.42, align="top")
    caption(s, 5.95, 4.86, 3.85,
            "Fig. 3 — cada color es el ruteo de un experto sobre la slide; abajo, la "
            "morfología que resume (tumor, estroma, alvéolos…)", size=8)
    notes(s, "El nombre es un acrónimo: mammoth junta cabezas de transformación, una mezcla de "
             "expertos y una factorización de matrices de bajo rango. En CLAM, una sola capa "
             "lineal proyecta todos los parches al espacio interno del modelo. Esa única matriz "
             "tiene que servir para epitelio, estroma y ductos a la vez, así que queda mediocre "
             "para todo. La analogía del paper es un solo traductor obligado a traducir chino, "
             "árabe y ruso con la misma plantilla. Mammoth contrata treinta traductores "
             "especialistas y un recepcionista, el router, que decide cuánto de cada parche "
             "mandar a cada especialista. Las dos figuras son la evidencia. Arriba, el espacio "
             "interno pasa de una nube continua a grupos separados, uno por experto, y la mejora "
             "es transversal a todos los agregadores. Abajo, cada color es un experto pintado "
             "sobre la lámina, y debajo se ve la morfología que ese experto resume; esa figura "
             "es exactamente el análisis que después reproduzco sobre nuestras slides de mama.")

    # ---- 5. Diagrama: pipeline CLAM + punto de integración (reusado, escalado) ----
    s = copy_diagram_scaled(prs, DIAG_MAM, 0, title=None, bar=False)
    notes(s, "Este es el pipeline completo de CLAM. Entra la slide como parches, el extractor "
             "CONCH le da a cada parche un vector de quinientos doce números, y de ahí siguen la "
             "atención y el clasificador. El único bloque que cambia es el naranja: ahí es donde "
             "mammoth reemplaza la primera capa lineal. Todo lo demás es CLAM tal cual.")

    # ---- 6. Interior de MAMMOTH: matrices+dims Y código en paralelo (NATIVO) ----
    s = content(prs, "Por dentro de MAMMOTH: dimensiones y código")
    add_textbox(s, 0.30, 0.86, 4.7, 0.3, [("El tensor, paso a paso", 13, True, TEAL_TITLE, F_TITLE)])
    dims_table(s, 0.30, 1.20, 4.72, [
        ("z · features CONCH (parche)", "[N, 512]"),
        ("q = LN(Wq · z)", "[N, 256]"),
        ("split en 16 cabezas", "[N, 16, 16]"),
        ("S · prototipos (slot_embeds)", "[30,16,10,16]"),
        ("logits de ruteo ⟨q, S⟩", "[N,30,16,10]"),
        ("D = softmax sobre N (dispatch)", "[N,30,16,10]"),
        ("u · slots (media ponderada)", "[30,16,10,16]"),
        ("expertos LoRA + concat cabezas", "[300, 512]"),
        ("combine → salida drop-in", "[N, 512]"),
    ], row_h=0.30)
    add_textbox(s, 0.30, 4.24, 4.72, 0.44, [
        ("El 16 aparece dos veces: nº de cabezas y dimensión de cada prototipo (256/16), para "
         "compararlos con un producto interno. 30 expertos × 10 slots = 300.",
         8.5, False, GRIS_BODY, F_BODY)])
    add_textbox(s, 5.20, 0.86, 4.6, 0.3, [("El código real (mammoth.py)", 13, True, TEAL_TITLE, F_TITLE)])
    code_panel(s, 5.20, 1.20, 4.60, 3.00, [
        "q = norm(wq(z))              # [N,512]->[N,256]",
        'q = rearrange(q,             # -> [N,16,16]',
        '      "n (h d)->n h d", h=16)',
        'logits = einsum("n h d, e h s d',
        '                 -> n e h s", q, S)',
        "                             # S=[30,16,10,16]",
        "dispatch = softmax(logits, dim=N)",
        'u = einsum("n h d, n e h s',
        '            -> e h s d", q, dispatch)',
        "out = expert_heads(u)        # LoRA -> [300,512]",
        "# drop-in (keep_slots=False):",
        'out = einsum("h p d, n h p -> n h d",',
        "             out, combine)   # -> [N,512]",
    ])
    takeaway_bar(s, "Las cabezas son subespacios aprendidos (multi-head), no textura/forma/color: "
                    "la semántica de tejido vive en los slots.", t=4.80, size=12)
    notes(s, "Este es el interior de mammoth, y es la parte que se me cayó la vez pasada, así que "
             "la voy a decir despacio, con las dimensiones y el código al lado. Cada parche entra "
             "como un vector de quinientos doce, la z. Lo primero es proyectarlo a un query de "
             "doscientos cincuenta y seis y partirlo en dieciséis cabezas de dieciséis. En "
             "paralelo el modelo tiene sus prototipos aprendidos, el tensor treinta por dieciséis "
             "por diez por dieciséis: treinta expertos, cada uno con dieciséis cabezas, cada "
             "cabeza con diez slots, y cada slot es un vector de dieciséis. El dieciséis aparece "
             "dos veces porque el número de cabezas y la dimensión del prototipo tienen que "
             "coincidir para compararlos con un producto interno; en total son trescientos slots. "
             "El ruteo compara query contra prototipos, una softmax reparte cada parche entre los "
             "slots, y con esos pesos se arma el promedio ponderado que llena los slots. Cada "
             "experto los procesa con una transformación de bajo rango y se concatenan las "
             "cabezas. En la variante normal un segundo softmax recombina los trescientos slots y "
             "reconstruye los parches, así que la salida tiene la misma forma que una capa lineal; "
             "por eso es drop-in. La aclaración importante: las cabezas no son textura, forma y "
             "color; son subespacios aprendidos, como en atención multi-cabeza. La semántica de "
             "tejido no vive en las cabezas, vive en los slots.")

    # ---- 7. Flujo de datos sobre la arquitectura oficial (reusado B5-s7 + variables) ----
    s = copy_diagram_scaled(prs, DIAG_FUSED, 0, title=None, bar=False, scale=0.72)
    add_textbox(s, 0.30, 4.98, SW - 0.6, 0.5, [
        ("Variables por bloque:  z → q (query) → ⟨q, S⟩ → D (dispatch) → u = 300 slots → "
         "o [300,512] → h [N,512] → CLAM.",
         11, True, TEAL_TITLE, F_BODY, PP_ALIGN.CENTER)], anchor=MSO_ANCHOR.MIDDLE)
    notes(s, "Esta es la misma figura oficial del paper, y quiero recorrerla bloque por bloque "
             "diciendo qué entra y qué sale de cada uno, porque acá es donde se arma toda la "
             "cadena. Entra la slide y el encoder CONCH le da a cada parche su vector z de "
             "quinientos doce. La proyección lo convierte en el query q de doscientos cincuenta y "
             "seis, que ya está partido en dieciséis cabezas. El ruteo por slots compara ese query "
             "contra los prototipos y produce el dispatch D, que reparte cada parche entre los "
             "trescientos slots. Con eso se llenan los slots, u, y los expertos de bajo rango los "
             "transforman en la salida o de trescientos por quinientos doce. La concatenación de "
             "cabezas reconstruye h, otra vez con la forma de N parches por quinientos doce, y "
             "recién ahí entra CLAM con su atención y su clasificador para dar el diagnóstico. "
             "El punto es que mammoth solo reemplaza ese tramo del principio; lo de CLAM queda "
             "igual.")

    # ---- 8. keep_slots: la bifurcación, con math+código (NATIVO) ----
    s = content(prs, "La variante keep_slots: dónde cambia la salida")
    # tronco compartido
    trunk = _rect(s, 0.30, 0.98, 9.4, 0.66, TEAL_CARD, line=TEAL_SQ)
    add_textbox(s, 0.46, 1.00, 9.1, 0.62, [
        ("Tronco compartido — idéntico a la slide anterior:  z → q → ruteo → expertos  →  "
         "out = concat de expertos  [300, 512]", 12.5, True, INK, F_BODY)], anchor=MSO_ANCHOR.MIDDLE)
    # rama izquierda: keep_slots=False
    add_textbox(s, 0.30, 1.80, 4.6, 0.3, [("keep_slots = False  ·  drop-in (base)", 12.5, True, TEAL_TITLE, F_TITLE)])
    code_panel(s, 0.30, 2.14, 4.6, 1.5, [
        "# 2º softmax recombina los 300 slots",
        'out = einsum("h p d, n h p -> n h d",',
        "             out, combine)",
        'out = rearrange(out,"n h d->n (h d)")',
        "                          # -> [N, 512]",
    ])
    add_textbox(s, 0.30, 3.72, 4.6, 0.95, [
        ("Reconstruye los N parches (cardinalidad N → N). CLAM agrega sobre los N parches, "
         "igual que la capa lineal original.", 12, False, GRIS_BODY, F_BODY)])
    # rama derecha: keep_slots=True
    add_textbox(s, 5.10, 1.80, 4.6, 0.3, [("keep_slots = True  ·  variante nueva", 12.5, True, ORA_T, F_TITLE)])
    code_panel(s, 5.10, 2.14, 4.6, 1.5, [
        "# se salta la recombinación",
        "return out                # -> [300, 512]",
        "#     300 slot-tokens como salida",
        "#     (+ slot_dropout opcional)",
    ])
    add_textbox(s, 5.10, 3.72, 4.6, 0.95, [
        ("Se queda con los 300 slots (cuello de botella aprendido N → 300). CLAM agrega sobre "
         "los 300 slots, no sobre los parches.", 12, False, GRIS_BODY, F_BODY)])
    takeaway_bar(s, "Misma cabeza CLAM y misma pérdida — cambia solo qué se agrega. La "
                    "interpretabilidad se calcula antes de la bifurcación → vale para las dos.",
                 t=4.78, size=12)
    notes(s, "Hay una variante que se llama keep_slots y quiero mostrar exactamente dónde cambia. "
             "Hasta arriba todo es igual: proyección, ruteo, expertos, y quedan los trescientos "
             "slots. La bifurcación es una sola línea. En la versión normal, keep_slots en falso, "
             "un segundo softmax recombina los trescientos slots y reconstruye los N parches, así "
             "que CLAM sigue agregando sobre los parches como siempre; es un reemplazo directo de "
             "la capa lineal. En la versión nueva, keep_slots en verdadero, el modelo se salta esa "
             "recombinación y entrega los trescientos slots como salida, y entonces CLAM agrega "
             "sobre trescientos tokens en vez de sobre los parches. La menciono para completar el "
             "mecanismo, pero es una variante de rendimiento; para lo de hoy da igual, porque la "
             "interpretabilidad se calcula antes de esta bifurcación y vale para las dos.")

    # ---- 9. Divisoria: Interpretabilidad (OBJ-A) ----
    s = divider(prs, "¿Qué mira cada experto?",
                "Interpretabilidad post-hoc sobre un checkpoint entrenado · 4 slides TCGA-BRCA")
    notes(s, "Con el mecanismo claro, pasamos a lo nuevo: mirar, sobre nuestras propias slides, "
             "qué región reclama cada experto y qué morfología hay ahí. Es análisis post-hoc en "
             "CPU sobre un modelo ya entrenado, no reentrena nada.")

    # ---- 10. Ruteo espacial (dónde) + morfología top-k (qué) — FUSIÓN ----
    s = content(prs, "Qué mira cada experto: dónde y qué morfología")
    add_image_fit(s, HEATMAP_MONTAGE, 0.30, 0.98, 4.95, 3.35, align="top")
    caption(s, 0.30, 4.38, 4.95, "Ruteo espacial: los 30 expertos encienden zonas distintas", size=9)
    add_image_fit(s, TOPK_SUBSET, 5.42, 0.98, 2.55, 3.05, align="top")
    add_textbox(s, 8.05, 1.05, 1.80, 3.2, [
        ("Top-k a alta resolución:", 11.5, True, INK, F_BODY),
        ("e8 → epitelio tumoral", 12, True, TEAL_TITLE, F_BODY),
        ("e26 → estroma fibroso", 12, True, TEAL_TITLE, F_BODY),
        ("e3 → epitelio ductal", 12, True, TEAL_TITLE, F_BODY),
        ("Color = percentil por experto (estructura relativa, no magnitud de uso).",
         9.5, False, ORA_T, F_BODY),
    ], anchor=MSO_ANCHOR.TOP)
    caption(s, 5.42, 4.12, 2.55, "Morfología que cada experto rutea (Fig 3.2)", size=9)
    takeaway_bar(s, "Heatmap = dónde · top-k = qué morfología. Emergió sin supervisión de tejido "
                    "(el paper lo validó con patólogos).", t=4.82, size=12)
    notes(s, "Junté las dos vistas porque cuentan una sola historia. A la izquierda, cada uno de "
             "los treinta cuadros es la misma slide pintada según cuánto el router manda cada "
             "parche a un experto: rojo mucho, azul casi nada. Lo que importa es que los treinta "
             "encienden zonas distintas, así que la capa lineal única se reemplazó por "
             "especialistas que miran regiones diferentes del tejido. Un aviso honesto: el color "
             "está normalizado por percentil dentro de cada experto, sirve para ver dónde prefiere "
             "mirar cada uno, no para decir cuál se usa más; medido aparte, el uso sale casi "
             "uniforme, no hay expertos muertos ni acaparadores. Pero el mapa de calor dice dónde, "
             "no qué tejido hay ahí. Eso lo cierra la derecha: para cada experto tomo los parches "
             "que más rutea y los recorto a alta resolución. Se ve directo: el experto ocho mira "
             "nidos de epitelio tumoral, el veintiséis mira estroma fibroso rosado, el tres mira "
             "ductos. Es la misma especialización que el paper validó con dos patólogos, y lo "
             "notable es que emerge sola, nadie le dijo al modelo qué es estroma. Los expertos "
             "mixtos que aparecen son esperables, porque el ruteo es suave y reparte cada parche "
             "entre varios.")

    # ---- 11. Morfología ≠ clase (cross-slide) + honestidad/cierre — FUSIÓN ----
    s = content(prs, "El experto detecta tejido, no clase")
    add_image_fit(s, XSLIDE_E8, 0.30, 0.98, 4.95, 1.62, align="top")
    add_image_fit(s, XSLIDE_E26, 0.30, 2.70, 4.95, 1.62, align="top")
    caption(s, 0.30, 4.40, 4.95, "e8 (epitelio) y e26 (estroma) en las 4 slides (2 pos + 2 neg)", size=8.5, align=PP_ALIGN.LEFT)
    add_textbox(s, 5.45, 0.98, 4.35, 3.7, [
        ("El mismo experto elige la misma morfología en las 4 slides, incluidas las negativas.",
         13, True, INK, F_BODY),
        ("«Negativo» = cdis sin microcalcificación, no «sin tumor» → sigue habiendo epitelio.",
         12, False, GRIS_BODY, F_BODY),
        ("Un experto es un detector de TEJIDO, no de clase. La clase se decide después "
         "(atención + clasificador).", 12.5, True, ORA_T, F_BODY),
        ("", 6, False, INK, F_BODY),
        ("Honestidad:  4 slides · 1 tarea · 1 fold. Etiquetas de tejido provisionales → "
         "falta sign-off de patólogo.", 11.5, False, GRIS_BODY, F_BODY),
    ], anchor=MSO_ANCHOR.TOP)
    takeaway_bar(s, "Que la especialización sea real y aun así no mueva la métrica es la evidencia "
                    "de que el cuello no está en la 1ª capa, sino en el dato.", t=4.82, size=12)
    notes(s, "Esta es la prueba más fina, y con ella cierro. Como los prototipos son parámetros "
             "compartidos del modelo, el experto ocho es el mismo experto en todas las slides. "
             "Entonces hay una prueba limpia: si su especialización es real, tiene que elegir la "
             "misma morfología en todas. Y así es: el ocho enciende epitelio en las cuatro, el "
             "veintiséis estroma en las cuatro, incluidas las negativas. La clave es que negativo "
             "acá quiere decir cdis sin microcalcificación, no sin tumor: siguen siendo slides de "
             "mama con epitelio. Es decir, el experto detecta tejido, no clase; la decisión de si "
             "la slide es positiva viene después, en la atención y el clasificador. Y esto es lo "
             "más valioso para la discusión: que los expertos separen bien los tejidos y aun así "
             "mammoth no le gane a CLAM en métrica es justamente la evidencia de que el cuello de "
             "botella no está en la primera capa, está en el dato. Con la honestidad por delante: "
             "es una cala chica, cuatro slides, una tarea, un fold, y las etiquetas de tejido "
             "todavía son mías, faltan los ojos de un patólogo. Son dos ejes distintos: que "
             "mammoth no mejore la métrica está cerrado; qué aprende por dentro está abierto, y es "
             "lo que traje. Mostrar qué mira no reabre nada, le pone un mecanismo.")

    os.makedirs(OUT_DIR, exist_ok=True)
    prs.save(DST)
    print("Guardado:", DST, "·", len(prs.slides), "slides")


if __name__ == "__main__":
    build()
