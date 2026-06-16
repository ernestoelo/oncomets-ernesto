#!/usr/bin/env python
"""generate_b5_deck.py — ensambla CLAM_Sprint_B5.pptx (deck completo, branding Environ).

Rev. 4 (feedback Ernesto, 3ª ronda): TABLAS NATIVAS (no imágenes) y escalables en S7/
microcalc/cierre; diagrama PathPT matemático estilo Diagrama_CLAM; header consistente
(gris + logo + título Barlow) también en los diagramas; S2 sin "lecciones de B4";
S8 con gráfico formal (bal_acc + AUC); S10 (idea) fusionada con los 3 componentes;
títulos de resultados minimalistas/profesionales.

Deck 13.333x7.5 in. Speaker notes por slide (sin nº de job, sin nombres).

Uso: PYTHONPATH=/media/administrador/Storage1/sdonoso/clam_testing2/.pylibs \
     /home/sdonoso/miniconda3/envs/clam_latest/bin/python scripts/generate_b5_deck.py
"""
import copy
import os

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from PIL import Image

REPO = "/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto"
PRES = os.path.join(REPO, "papers/presentations")
ASSETS_BRAND = os.path.join(PRES, "assets_branding")
PAPER_FIGS = os.path.join(ASSETS_BRAND, "paper_figs")
DST = os.path.join(PRES, "CLAM_Sprint_B5.pptx")

A_MAM = os.path.join(REPO, "sprints/B5_sprint5/objetivo_2_mammoth_patron_invasion/figuras/slide_assets")
A_PPT = os.path.join(REPO, "sprints/B5_sprint5/pathpt/figuras/slide_assets")
DIAG_MAM = os.path.join(PRES, "Diagrama_CLAM_mammoth.pptx")
DIAG_PPT = os.path.join(PRES, "Diagrama_PathPT.pptx")

# ---- paleta ----
TEAL_TITLE = RGBColor(0x21, 0x75, 0x89)
TEAL_SQ    = RGBColor(0x31, 0x85, 0x9C)
BAR_GRIS   = RGBColor(0xF2, 0xF2, 0xF2)
TEAL_DIV   = RGBColor(0x2E, 0x7E, 0x8F)
TEAL_CARD  = RGBColor(0xDD, 0xEA, 0xEE)
TEAL_CARD2 = RGBColor(0xF3, 0xF8, 0xF9)
LAV_TITLE  = RGBColor(0xCD, 0xD6, 0xF4)
TEAL_SUB   = RGBColor(0xB8, 0xD4, 0xD9)
ROW_ALT    = RGBColor(0xF2, 0xF4, 0xF5)
GRIS_BODY  = RGBColor(0x59, 0x59, 0x59)
VERDE      = RGBColor(0x1E, 0x84, 0x49)
ROJO       = RGBColor(0xC0, 0x39, 0x2B)
AMBAR      = RGBColor(0xB9, 0x77, 0x0E)
GRIS_TXT   = RGBColor(0x55, 0x55, 0x55)
ORA_T      = RGBColor(0xB4, 0x52, 0x1E)
INK        = RGBColor(0x22, 0x22, 0x22)
WHITE      = RGBColor(0xFF, 0xFF, 0xFF)

F_TITLE = "Barlow ExtraBold"
F_BODY  = "Barlow"

SW, SH = 13.333, 7.5
HDR = 0.82
LOGO = os.path.join(ASSETS_BRAND, "logo_header.png")
PORTADA = os.path.join(ASSETS_BRAND, "portada_fullbleed.jpg")
_uid = [1000]


# ============================================================================
# Helpers base
# ============================================================================

def _blank(prs):
    for lay in prs.slide_layouts:
        if (lay.name or "").lower().strip() == "blank":
            return lay
    return prs.slide_layouts[6]


def _set_runs(tf, lines, anchor=MSO_ANCHOR.TOP):
    tf.word_wrap = True; tf.vertical_anchor = anchor
    for i, ln in enumerate(lines):
        txt, sz, bold, col = ln[0], ln[1], ln[2], ln[3]
        font = ln[4] if len(ln) > 4 else F_BODY
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = ln[5] if len(ln) > 5 else PP_ALIGN.LEFT
        p.space_after = Pt(6)
        r = p.add_run(); r.text = txt
        r.font.size = Pt(sz); r.font.bold = bold; r.font.name = font; r.font.color.rgb = col


def add_textbox(slide, l, t, w, h, lines, anchor=MSO_ANCHOR.TOP):
    tb = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    _set_runs(tb.text_frame, lines, anchor=anchor)
    return tb


def add_notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text


def _rect(slide, l, t, w, h, color):
    sp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(l), Inches(t), Inches(w), Inches(h))
    sp.fill.solid(); sp.fill.fore_color.rgb = color
    sp.line.fill.background(); sp.shadow.inherit = False
    return sp


def logo_mark(slide):
    _rect(slide, 0, 0, HDR, HDR, TEAL_SQ)
    slide.shapes.add_picture(LOGO, Inches(0.09), Inches(0.09), height=Inches(0.64))


def header(slide, title, bar=True):
    """Header consistente: (barra gris) + cuadrado teal + logo + título Barlow teal."""
    if bar:
        _rect(slide, 0, 0, SW, HDR, BAR_GRIS)
    logo_mark(slide)
    tb = slide.shapes.add_textbox(Inches(1.05), Inches(0.04), Inches(12.0), Inches(0.74))
    _set_runs(tb.text_frame, [(title, 28, True, TEAL_TITLE, F_TITLE)], anchor=MSO_ANCHOR.MIDDLE)


def add_bullets(slide, l, t, w, h, items, size=26, sub_size=22, anchor=MSO_ANCHOR.TOP):
    tb = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = tb.text_frame; tf.word_wrap = True; tf.vertical_anchor = anchor
    for i, it in enumerate(items):
        txt, lvl = (it if isinstance(it, tuple) else (it, 0))
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(int(size * 0.7) if lvl == 0 else int(sub_size * 0.45))
        p.level = lvl
        b = "•  " if lvl == 0 else "–  "
        r = p.add_run(); r.text = ("     " * lvl) + b + txt
        r.font.size = Pt(size if lvl == 0 else sub_size); r.font.bold = (lvl == 0)
        r.font.name = F_BODY; r.font.color.rgb = INK if lvl == 0 else GRIS_BODY
    return tb


def add_card(slide, l, t, w, h, text, idx=0, size=21):
    fill = TEAL_CARD if idx % 2 == 0 else TEAL_CARD2
    sp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(l), Inches(t), Inches(w), Inches(h))
    sp.fill.solid(); sp.fill.fore_color.rgb = fill
    sp.line.color.rgb = TEAL_SQ; sp.line.width = Pt(1.5); sp.shadow.inherit = False
    cd = 0.62
    circ = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(l + 0.22), Inches(t + (h - cd) / 2),
                                  Inches(cd), Inches(cd))
    circ.fill.solid(); circ.fill.fore_color.rgb = TEAL_SQ
    circ.line.fill.background(); circ.shadow.inherit = False
    _set_runs(circ.text_frame, [(str(idx + 1), 20, True, WHITE, F_TITLE, PP_ALIGN.CENTER)],
              anchor=MSO_ANCHOR.MIDDLE)
    tb = slide.shapes.add_textbox(Inches(l + 1.05), Inches(t), Inches(w - 1.25), Inches(h))
    _set_runs(tb.text_frame, [(text, size, True, INK, F_BODY)], anchor=MSO_ANCHOR.MIDDLE)


def add_vcard(slide, l, t, w, h, title, body, tcol=ORA_T):
    """Tarjeta vertical: título color + cuerpo gris (para los 3 componentes)."""
    sp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(l), Inches(t), Inches(w), Inches(h))
    sp.fill.solid(); sp.fill.fore_color.rgb = TEAL_CARD2
    sp.line.color.rgb = TEAL_SQ; sp.line.width = Pt(1.5); sp.shadow.inherit = False
    _set_runs(sp.text_frame, [(title, 17, True, tcol, F_BODY, PP_ALIGN.CENTER),
                              (body, 14, False, GRIS_BODY, F_BODY, PP_ALIGN.CENTER)],
              anchor=MSO_ANCHOR.MIDDLE)


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


def _style_cell(cell, text, size, bold, color, align=PP_ALIGN.CENTER):
    cell.vertical_anchor = MSO_ANCHOR.MIDDLE
    cell.margin_left = cell.margin_right = Inches(0.06)
    cell.margin_top = cell.margin_bottom = Inches(0.02)
    tf = cell.text_frame; tf.word_wrap = True
    parts = str(text).split("\n")
    p = tf.paragraphs[0]; p.alignment = align
    r = p.add_run(); r.text = parts[0]
    r.font.size = Pt(size); r.font.bold = bold; r.font.name = F_BODY; r.font.color.rgb = color
    for extra in parts[1:]:
        p2 = tf.add_paragraph(); p2.alignment = align
        r2 = p2.add_run(); r2.text = extra
        r2.font.size = Pt(size); r2.font.bold = bold; r2.font.name = F_BODY; r2.font.color.rgb = color


def add_table(slide, headers, rows, l, t, w, h, col_fracs=None, cell_colors=None,
              fontsize=14, header_fontsize=14):
    """Tabla NATIVA pptx (escalable/editable) con estilo Environ."""
    nrows, ncols = len(rows) + 1, len(headers)
    gf = slide.shapes.add_table(nrows, ncols, Inches(l), Inches(t), Inches(w), Inches(h))
    table = gf.table
    table.first_row = False; table.horz_banding = False
    # quitar el tableStyle del tema (para que manden mis fills)
    tbl = table._tbl
    tblPr = tbl.find(qn("a:tblPr"))
    if tblPr is not None:
        sid = tblPr.find(qn("a:tableStyleId"))
        if sid is not None:
            tblPr.remove(sid)
    if col_fracs:
        tot = sum(col_fracs)
        for j, fr in enumerate(col_fracs):
            table.columns[j].width = Inches(w * fr / tot)
    for j, htxt in enumerate(headers):
        c = table.cell(0, j); c.fill.solid(); c.fill.fore_color.rgb = TEAL_SQ
        _style_cell(c, htxt, header_fontsize, True, WHITE)
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            c = table.cell(i + 1, j)
            bg = WHITE if i % 2 == 0 else ROW_ALT
            fg = INK; bold = (j == 0)
            if cell_colors and (i, j) in cell_colors:
                cc = cell_colors[(i, j)]
                fg = cc.get("fg", fg); bold = cc.get("bold", bold); bg = cc.get("bg", bg)
            c.fill.solid(); c.fill.fore_color.rgb = bg
            _style_cell(c, val, fontsize, bold, fg)
    rh = h / nrows
    for r in table.rows:
        r.height = Inches(rh)
    return gf


def _blue_shade(frac):
    frac = max(0.0, min(1.0, frac))
    return RGBColor(int(255 - (255 - 0x31) * frac),
                    int(255 - (255 - 0x85) * frac),
                    int(255 - (255 - 0x9C) * frac))


def add_confusion(slide, conf, classes, l, t, w, h, caption=None, vfont=15):
    """Matriz de confusión como TABLA NATIVA con celdas tipo heatmap (no imagen)."""
    n = len(classes)
    mx = max(max(r) for r in conf) or 1
    gf = slide.shapes.add_table(n + 1, n + 1, Inches(l), Inches(t), Inches(w), Inches(h))
    table = gf.table; table.first_row = False; table.horz_banding = False
    tblPr = table._tbl.find(qn("a:tblPr"))
    if tblPr is not None:
        sid = tblPr.find(qn("a:tableStyleId"))
        if sid is not None:
            tblPr.remove(sid)
    lblw = w * 0.20
    for j in range(n + 1):
        table.columns[j].width = Inches(lblw if j == 0 else (w - lblw) / n)
    c = table.cell(0, 0); c.fill.solid(); c.fill.fore_color.rgb = WHITE; _style_cell(c, "", 10, False, INK)
    for j in range(n):
        c = table.cell(0, j + 1); c.fill.solid(); c.fill.fore_color.rgb = TEAL_SQ
        _style_cell(c, f"pred\n{classes[j]}", 12, True, WHITE)
    for i in range(n):
        c = table.cell(i + 1, 0); c.fill.solid(); c.fill.fore_color.rgb = TEAL_SQ
        _style_cell(c, f"true\n{classes[i]}", 12, True, WHITE)
        for j in range(n):
            v = conf[i][j]; frac = v / mx
            cc = table.cell(i + 1, j + 1); cc.fill.solid(); cc.fill.fore_color.rgb = _blue_shade(frac)
            _style_cell(cc, str(v), vfont, True, WHITE if frac > 0.55 else INK)
    rh = h / (n + 1)
    for r in table.rows:
        r.height = Inches(rh)
    if caption:
        add_textbox(slide, l - 0.3, t + h + 0.06, w + 0.6, 0.5,
                    [(caption, 12, False, GRIS_TXT, F_BODY, PP_ALIGN.CENTER)])
    return gf


def add_chart_grouped(slide, cats, series, colors, l, t, w, h, ymax=1.0, hline=None):
    """Barras agrupadas como GRÁFICO NATIVO pptx (editable, no imagen)."""
    from pptx.chart.data import CategoryChartData
    from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
    cd = CategoryChartData(); cd.categories = cats
    for name, vals in series:
        cd.add_series(name, vals)
    gf = slide.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED,
                                Inches(l), Inches(t), Inches(w), Inches(h), cd)
    chart = gf.chart; chart.has_title = False
    chart.has_legend = True; chart.legend.position = XL_LEGEND_POSITION.BOTTOM
    chart.legend.include_in_layout = False; chart.legend.font.size = Pt(13)
    plot = chart.plots[0]; plot.has_data_labels = True; plot.gap_width = 80
    dl = plot.data_labels; dl.number_format = "0.000"; dl.number_format_is_linked = False
    dl.font.size = Pt(12); dl.font.bold = True
    for srs, col in zip(chart.series, colors):
        srs.format.fill.solid(); srs.format.fill.fore_color.rgb = col
    va = chart.value_axis; va.minimum_scale = 0; va.maximum_scale = ymax
    va.tick_labels.font.size = Pt(11); va.has_major_gridlines = True
    chart.category_axis.tick_labels.font.size = Pt(13)
    return gf


def _node(slide, l, t, w, h, lines, fill, edge, lw=1.5):
    sp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(l), Inches(t), Inches(w), Inches(h))
    sp.fill.solid(); sp.fill.fore_color.rgb = fill
    sp.line.color.rgb = edge; sp.line.width = Pt(lw); sp.shadow.inherit = False
    _set_runs(sp.text_frame, lines, anchor=MSO_ANCHOR.MIDDLE)
    return sp


def _arrow(slide, l, t, w, h, direction="down"):
    shp = {"down": MSO_SHAPE.DOWN_ARROW, "right": MSO_SHAPE.RIGHT_ARROW}[direction]
    a = slide.shapes.add_shape(shp, Inches(l), Inches(t), Inches(w), Inches(h))
    a.fill.solid(); a.fill.fore_color.rgb = RGBColor(0x8A, 0x8A, 0x8A)
    a.line.fill.background(); a.shadow.inherit = False
    return a


def draw_mammoth_concept(slide, ox, oy):
    """Concepto antes/después (1 capa lineal → MoE) como BLOQUES nativos (no imagen)."""
    TEALF = RGBColor(0xD7, 0xE7, 0xEB); TEALE = TEAL_SQ
    ORAF = RGBColor(0xFC, 0xE5, 0xCD); ORAE = RGBColor(0xE2, 0x72, 0x3B); ORATT = ORA_T
    BLUF = RGBColor(0xEA, 0xF2, 0xFB); BLUE2 = RGBColor(0x5B, 0x8F, 0xB9)
    # --- CLAM (antes), columna izquierda ---
    add_textbox(slide, ox, oy, 2.4, 0.4, [("CLAM (antes)", 16, True, TEAL_TITLE, F_TITLE, PP_ALIGN.CENTER)])
    _node(slide, ox + 0.2, oy + 0.5, 2.0, 0.75, [("z ∈ ℝ⁵¹²", 13, True, INK)], TEALF, TEALE)
    _arrow(slide, ox + 1.05, oy + 1.28, 0.3, 0.32)
    _node(slide, ox, oy + 1.66, 2.4, 0.9, [("1 capa lineal", 14, True, ORATT),
                                           ("H = ReLU(W·z)", 11, False, GRIS_BODY)], ORAF, ORAE, lw=2)
    _arrow(slide, ox + 1.05, oy + 2.6, 0.3, 0.32)
    _node(slide, ox + 0.2, oy + 2.98, 2.0, 0.75, [("resto de CLAM", 13, True, INK)], TEALF, TEALE)
    # divisor
    ln = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(ox + 2.75), Inches(oy + 0.3),
                                Pt(1.4), Inches(3.4))
    ln.fill.solid(); ln.fill.fore_color.rgb = RGBColor(0xCC, 0xCC, 0xCC); ln.line.fill.background()
    ln.shadow.inherit = False
    # --- MAMMOTH (después), columna derecha ---
    rx = ox + 3.1
    add_textbox(slide, rx, oy, 2.9, 0.4, [("MAMMOTH (después)", 16, True, ORATT, F_TITLE, PP_ALIGN.CENTER)])
    _node(slide, rx + 0.9, oy + 0.5, 1.7, 0.62, [("z ∈ ℝ⁵¹²", 12, True, INK)], TEALF, TEALE)
    _arrow(slide, rx + 1.65, oy + 1.14, 0.26, 0.28)
    _node(slide, rx + 0.85, oy + 1.45, 1.8, 0.6, [("ROUTER g(z)", 12, True, ORATT)], ORAF, ORAE, lw=2)
    for i, lab in enumerate(["E₁", "E₂", "E₃"]):
        bx = rx + 0.1 + i * 1.15
        _node(slide, bx, oy + 2.3, 0.95, 0.6, [(lab, 13, True, INK)], BLUF, BLUE2)
        _arrow(slide, rx + 1.7, oy + 2.07, 0.22, 0.22) if i == 1 else None
    _node(slide, rx + 0.7, oy + 3.2, 2.1, 0.7, [("Σ ponderada", 12, True, INK),
                                                ("h ∈ ℝ⁵¹²", 11, False, GRIS_BODY)], TEALF, TEALE)
    add_textbox(slide, rx, oy + 3.95, 2.9, 0.5,
                [("expertos especializados por parche", 11, False, GRIS_TXT, F_BODY, PP_ALIGN.CENTER)])


# ---- datos necrosis (paired, para tabla nativa) ----
NEC_HEAD = ["Fold", "CLAM\nAUC / bal", "PathPT\nAUC / bal", "Δ AUC", "Δ bal_acc"]
NEC = [
    ("0", "0.798 / 0.653", "0.798 / 0.663", "+0.000", "+0.010"),
    ("1", "0.782 / 0.607", "0.798 / 0.698", "+0.016", "+0.091"),
    ("2", "0.598 / 0.656", "0.588 / 0.641", "−0.010", "−0.016"),
    ("3", "0.754 / 0.610", "0.599 / 0.502", "−0.155", "−0.108"),
    ("4", "0.703 / 0.641", "0.522 / 0.563", "−0.182", "−0.078"),
    ("media", "0.727 / 0.633", "0.661 / 0.613", "−0.066 ± 0.094", "−0.020 ± 0.078"),
]


def divider(prs, title, subtitle):
    s = prs.slides.add_slide(_blank(prs))
    s.background.fill.solid(); s.background.fill.fore_color.rgb = TEAL_DIV
    s.shapes.add_picture(LOGO, Inches(0.45), Inches(0.40), height=Inches(0.72))
    add_textbox(s, 1.0, 2.7, 11.3, 1.4,
                [(title, 50, True, LAV_TITLE, F_TITLE, PP_ALIGN.CENTER)], anchor=MSO_ANCHOR.MIDDLE)
    add_textbox(s, 1.0, 4.15, 11.3, 0.9,
                [(subtitle, 22, False, TEAL_SUB, F_BODY, PP_ALIGN.CENTER)], anchor=MSO_ANCHOR.TOP)
    return s


def content(prs, title):
    s = prs.slides.add_slide(_blank(prs)); header(s, title); return s


def copy_diagram(prs, src_path, idx, title, notes=None, bar=True):
    s = prs.slides.add_slide(_blank(prs))
    src = Presentation(src_path)
    spTree = s.shapes._spTree
    for shp in src.slides[idx].shapes:
        el = copy.deepcopy(shp._element)
        for cNvPr in el.iter(qn("p:cNvPr")):
            _uid[0] += 1; cNvPr.set("id", str(_uid[0]))
        spTree.append(el)
    header(s, title, bar=bar)
    if notes:
        add_notes(s, notes)
    return s


# ============================================================================
# Datos de tablas
# ============================================================================

MAM8_HEAD = ["Tarea", "Balance\n(clase +)", "bal_acc\nCLAM → +Mam", "AUC\nCLAM → +Mam",
             "Δ bal_acc\n(pareado)", "Lectura"]
MAM8 = [
    ("Microcalc · carcinoma inv.", "21%", "0.639 → 0.585", "0.732 → 0.722", "−0.054 ± 0.125", "nulo", GRIS_TXT),
    ("Microcalc · CDIS", "36%", "0.595 → 0.509", "0.652 → 0.618", "−0.086 ± 0.113", "leve regresión", ROJO),
    ("Microcalc · tejido no neopl.", "59%", "0.577 → 0.626", "0.646 → 0.678", "+0.049 ± 0.077", "leve mejora", VERDE),
    ("Patrón · cribiforme", "49%", "0.650 → 0.694", "0.710 → 0.732", "+0.044 ± 0.048", "leve mejora", VERDE),
    ("Patrón · sólido", "76%", "0.647 → 0.632", "0.700 → 0.679", "−0.014 ± 0.064", "nulo", GRIS_TXT),
    ("Patrón · micropapilar", "7%", "0.617 → 0.561", "0.707 → 0.710", "−0.056 ‡", "nulo", GRIS_TXT),
    ("Patrón · papilar", "6%", "0.531 → 0.506", "0.583 → 0.599", "−0.025 ‡", "nulo", GRIS_TXT),
    ("Invasión linfovascular (3 cl.)", "may. 70%", "0.622 → 0.575", "0.828 → 0.818", "−0.047 ± 0.064", "regresión leve", ROJO),
]
MICRO_HEAD = ["Tarea binaria (microcalc)", "n  (sí / no)", "AUC zero-shot\n(mejor prompt)", "vs azar (0.5)", "Veredicto"]
MICRO = [
    ("en carcinoma invasivo", "68 / 260", "0.629", "leve", "NO-GO", AMBAR),
    ("en CDIS", "118 / 210", "0.533", "≈ azar", "NO-GO", ROJO),
    ("en tejido no neoplásico", "192 / 136", "0.444", "bajo azar", "NO-GO", ROJO),
]
EJES_HEAD = ["Eje atacado", "Modelo / mecanismo", "Tareas (pareadas, MC-CV)", "Resultado"]
EJES = [
    ("Agregador\n(cómo se fusionan los parches)", "DSMIL\n(dual-stream)", "microcalc binarias + fusionado", "0 palancas\n(CDIS regresión leve)"),
    ("Patch-embed\n(1ª capa de proyección)", "Mammoth\n(mixture-of-experts)", "8 tareas (microcalc, patrón, invasión)", "0 palancas\n(efecto gated por balance)"),
    ("Lenguaje + supervisión tile", "PathPT-CONCH\n(prompt-tuning + θ espacial)", "necrosis, mitótica, microcalc", "0 palancas\n(grounding zero-shot débil)"),
]


# ============================================================================
# Construcción
# ============================================================================

def build():
    prs = Presentation(); prs.slide_width = Inches(SW); prs.slide_height = Inches(SH)

    # 1 · Portada
    s = prs.slides.add_slide(_blank(prs))
    s.shapes.add_picture(PORTADA, 0, 0, width=Inches(SW), height=Inches(SH))
    add_textbox(s, 0.8, 0.45, 11.7, 1.6,
                [("Sprint B5 — Integración de MAMMOTH y PathPT", 34, True, WHITE, F_TITLE, PP_ALIGN.CENTER),
                 ("OncoMets · CLAM sobre features CONCH · junio 2026", 17, False, WHITE, F_BODY, PP_ALIGN.CENTER)])
    add_notes(s, "Sprint B5, cierre de trimestre. Dos encargos: integrar y medir MAMMOTH, e "
                 "integrar y explicar PathPT (visión + lenguaje), con sus diagramas y resultados.")

    # 2 · Objetivos
    s = content(prs, "Objetivos del sprint")
    add_bullets(s, 0.9, 1.05, 11.7, 6.0, [
        ("MAMMOTH: cómo funciona e integra en CLAM — diagrama + resultados.", 0),
        ("PathPT: integrar y explicar el modelo (visión + lenguaje) — diagrama + resultados.", 0),
        ("Marco de evaluación común:", 0),
        ("Comparación PAREADA con validación cruzada k=5 (mismos splits).", 1),
        ("Métrica honesta: balanced accuracy + AUC + matriz de confusión.", 1),
    ], size=30, sub_size=25, anchor=MSO_ANCHOR.MIDDLE)
    add_notes(s, "Marco común a los dos modelos: comparar contra CLAM sobre los mismos splits "
                 "(pareado) y reportar balanced_acc junto al AUC y la matriz de confusión.")

    # ===== MAMMOTH =====
    divider(prs, "MAMMOTH", "Mixture-of-Experts en la primera capa de CLAM (patch-embed)")

    s = content(prs, "MAMMOTH — qué es y por qué")
    cards = [
        "Reemplaza la 1ª capa lineal de CLAM por una mezcla de expertos (MoE).",
        "Un router envía cada parche a expertos especializados.",
        "Objetivo: reducir la interferencia de gradientes entre parches.",
        "El resto de CLAM no cambia → comparación limpia.",
    ]
    cy = 1.15
    for i, c in enumerate(cards):
        add_card(s, 0.5, cy, 6.2, 1.25, c, idx=i, size=21); cy += 1.42
    draw_mammoth_concept(s, 7.05, 1.7)   # bloques nativos (no imagen)
    add_notes(s, "Cambio quirúrgico: una sola capa cambia, todo lo demás queda igual → la diferencia "
                 "es atribuible solo a mammoth. Motivación: interferencia de gradientes entre instancias.")

    copy_diagram(prs, DIAG_MAM, 0, "MAMMOTH — integración en CLAM", bar=False,
                 notes="El bloque naranja es lo ÚNICO que cambia: la 1ª capa totalmente conectada de "
                       "CLAM pasa a ser MAMMOTH (MoE). Todo el resto es nuestro diagrama de CLAM.")
    copy_diagram(prs, DIAG_MAM, 1, "MAMMOTH — qué hace (zoom de la 1ª capa)",
                 notes="Router que asigna pesos por experto; cada experto es una proyección de bajo "
                       "rango; la salida es la suma ponderada.")

    # 7 · Resultados 8 tareas (TABLA NATIVA)
    s = content(prs, "MAMMOTH — resultados (8 tareas, k=5)")
    rows = [[d[0], d[1], d[2], d[3], d[4], d[5]] for d in MAM8]
    cc = {}
    for i, d in enumerate(MAM8):
        cc[(i, 4)] = {"fg": d[6], "bold": True}; cc[(i, 5)] = {"fg": d[6], "bold": True}
    add_table(s, MAM8_HEAD, rows, 0.4, 1.05, 12.55, 5.65,
              col_fracs=[0.255, 0.12, 0.165, 0.155, 0.165, 0.14],
              cell_colors=cc, fontsize=15, header_fontsize=14)
    add_textbox(s, 0.5, 6.85, 12.4, 0.5,
                [("0 palancas consistentes. El lean+ leve solo asoma en las 2 tareas más "
                  "balanceadas (tejido, cribiforme) → lo gobierna el balance, no la arquitectura.",
                  14, False, GRIS_TXT)])
    add_notes(s, "Ocho tareas, cero palancas. Único lean+ leve en las 2 balanceadas. En todas la "
                 "varianza entre folds ≳ el efecto. Lo gobierna el balance de clases, no el patch-embed.")

    # 8 · Invasión (gráfico nativo + confusión nativa)
    s = content(prs, "MAMMOTH — invasión linfovascular")
    add_chart_grouped(s, ["balanced_acc", "macro-OVR AUC"],
                      [("CLAM", (0.622, 0.828)), ("+ Mammoth", (0.575, 0.818))],
                      [RGBColor(0x2C, 0x7A, 0x8C), RGBColor(0xE2, 0x72, 0x3B)],
                      0.5, 1.15, 6.0, 4.95, ymax=1.0)
    add_confusion(s, [[115, 64, 62], [97, 803, 85], [47, 56, 79]], ["aus", "no_id", "pres"],
                  7.7, 1.45, 4.9, 3.55,
                  caption="+Mammoth (5 folds): recall  aus 0.48 · no_id 0.82↑ · pres 0.43↓")
    add_textbox(s, 0.5, 6.25, 12.4, 0.95,
                [("n = 2814 (el caso más sano): mammoth agrava el colapso a la mayoritaria; AUC y "
                  "bal_acc bajan levemente. Cierre del hilo: 8 tareas, 0 palancas.", 15, False, GRIS_TXT)])
    add_notes(s, "El dataset más grande y el eval más sano. Mammoth manda más masa a la mayoritaria "
                 "'no identificado': bal_acc 0.622→0.575 y AUC 0.828→0.818 (5/5 folds−). Más poder "
                 "estadístico no rescató a mammoth.")

    # ===== PATHPT =====
    divider(prs, "PathPT", "Visión + lenguaje: clasificación parche-a-parche sobre CONCH congelado")

    # 10 · Idea (paper) + 3 componentes (fusión)
    s = content(prs, "PathPT — la idea y sus 3 piezas entrenables")
    add_image_fit(s, os.path.join(PAPER_FIGS, "pathpt_fig1_ab.png"), 0.5, 1.0, 12.3, 3.7, align="top")
    comps = [
        ("θᵥ · contexto espacial", "refina cada parche con su vecindario (grilla 2D + transformer)"),
        ("θₜ · prompt-tuning", "aprende la frase de clase en vez de escribirla a mano"),
        ("pseudo-labels (tile)", "etiqueta parches con CONCH y filtra con el label de slide"),
    ]
    cw = 4.0; cx = 0.55
    for i, (tt, bd) in enumerate(comps):
        add_vcard(s, cx + i * (cw + 0.18), 5.05, cw, 1.95, tt, bd)
    add_notes(s, "Figura del paper: CLAM comprime a 1 vector de slide; PathPT clasifica cada parche "
                 "usando también texto y localiza el hallazgo. Solo se entrenan θ_v y θ_t (las 3 piezas "
                 "de abajo); CONCH queda congelado.")

    # 11 · Diagrama arquitectura (matemático)
    copy_diagram(prs, DIAG_PPT, 0, "PathPT — arquitectura (forward)",
                 notes="Cascada con fórmulas y dimensiones por bloque, estilo de nuestro diagrama de "
                       "CLAM. Φᵥ/Φₜ (gris) congelados; θᵥ/θₜ (naranjo) entrenables. La clase de cada "
                       "parche = coseno texto-visión; se agrega a clase de slide (ŷ ∈ ℝ^C) + mapa.")

    # 12 · Necrosis (tabla nativa + confusión nativa)
    s = content(prs, "PathPT — Necrosis")
    rows = [list(r) for r in NEC]
    cc = {}
    for i, r in enumerate(NEC):
        for col in (3, 4):
            v = r[col]
            if v.startswith("+") and v != "+0.000":
                cc[(i, col)] = {"fg": VERDE, "bold": True}
            elif v.startswith("−"):
                cc[(i, col)] = {"fg": ROJO, "bold": True}
    add_table(s, NEC_HEAD, rows, 0.5, 1.2, 7.6, 4.4,
              col_fracs=[0.11, 0.27, 0.27, 0.18, 0.17], cell_colors=cc, fontsize=15, header_fontsize=13)
    add_confusion(s, [[19, 21], [39, 120]], ["aus", "pres"], 8.75, 1.55, 4.0, 3.0,
                  caption="PathPT (5 folds): recall  aus 0.48 · pres 0.76")
    add_textbox(s, 0.5, 6.1, 12.4, 1.0,
                [("H_alt: PathPT no aporta. El Δ pareado cruza 0 (bal_acc); apenas supera el teacher "
                  "zero-shot ~0.62, mientras CLAM llega a 0.727.", 15, False, GRIS_TXT)])
    add_notes(s, "Veredicto H_alt: PathPT no aporta. El Δ pareado cruza 0 (bal_acc), lean negativo en "
                 "AUC; apenas se despega del teacher zero-shot (~0.62), CLAM llega a 0.727.")

    # 13 · Mitótica (dos confusiones nativas)
    s = content(prs, "PathPT — Tasa mitótica")
    add_textbox(s, 0.6, 1.0, 5.6, 0.4, [("CLAM — usa las 3 clases", 16, True, TEAL_TITLE, F_BODY, PP_ALIGN.CENTER)])
    add_confusion(s, [[231, 53, 36], [77, 27, 38], [26, 28, 72]], ["s1", "s2", "s3"],
                  1.1, 1.55, 4.7, 3.5, caption="bal_acc 0.494 · recall [0.72, 0.19, 0.57]")
    add_textbox(s, 7.1, 1.0, 5.6, 0.4, [("PathPT — colapsa a score_1", 16, True, ORA_T, F_BODY, PP_ALIGN.CENTER)])
    add_confusion(s, [[320, 0, 0], [142, 0, 0], [126, 0, 0]], ["s1", "s2", "s3"],
                  7.6, 1.55, 4.7, 3.5, caption="bal_acc 0.333 (trivial) · 0 predicciones de s2 / s3")
    add_textbox(s, 0.5, 6.1, 12.4, 1.0,
                [("No es bug: CLAM no colapsa sobre los mismos splits. Es la formulación ordinal "
                  "(clase 0 = score_1 basal). El AUC (0.66) sobrevive → calibración del punto de operación.",
                  15, False, GRIS_TXT)])
    add_notes(s, "PathPT colapsa al argmax mayoritario (score_1): bal_acc 0.333 exacto, cero "
                 "predicciones de score_2/3. CLAM, mismos splits, no colapsa (0.494). No es bug: es la "
                 "formulación ordinal, pendiente de validación clínica. El AUC (0.66) sobrevive → "
                 "el cuello es la calibración del punto de operación.")

    # 14 · Microcalc (TABLA NATIVA)
    s = content(prs, "PathPT — Microcalcificaciones (go/no-go)")
    rows = [[d[0], d[1], d[2], d[3], d[4]] for d in MICRO]
    cc = {}
    for i, d in enumerate(MICRO):
        cc[(i, 2)] = {"fg": d[5], "bold": True}; cc[(i, 4)] = {"fg": d[5], "bold": True}
    add_table(s, MICRO_HEAD, rows, 1.1, 1.4, 11.1, 3.8,
              col_fracs=[0.30, 0.16, 0.22, 0.16, 0.16], cell_colors=cc,
              fontsize=18, header_fontsize=16)
    add_textbox(s, 0.9, 5.6, 11.5, 1.4,
                [("Chequeo zero-shot en CPU (~min, sin GPU): CONCH no groundea microcalcificaciones.",
                  18, True, INK),
                 ("Iterar prompts con más morfología EMPEORÓ. NO-GO → ahorró ~18–24 h de GPU.",
                  16, False, GRIS_BODY)])
    add_notes(s, "Patrón Etapa 0: antes de gastar GPU, etiquetamos zero-shot en CPU. CONCH no separa "
                 "(AUC 0.44–0.63). NO-GO sin quemar GPU.")

    # ===== CIERRE =====
    divider(prs, "Cierre y próximos pasos", "Tres ejes de arquitectura → dónde sí hay palanca")

    # 16 · Cierre 3 ejes (TABLA NATIVA)
    s = content(prs, "Cierre — 3 ejes, 0 palancas → el cuello es el dato")
    rows = [list(r) for r in EJES]
    cc = {(i, 3): {"fg": GRIS_TXT, "bold": True} for i in range(len(EJES))}
    add_table(s, EJES_HEAD, rows, 0.5, 1.15, 12.3, 4.7,
              col_fracs=[0.24, 0.22, 0.30, 0.24], cell_colors=cc,
              fontsize=16, header_fontsize=15)
    add_textbox(s, 0.6, 6.15, 12.1, 1.0,
                [("Tres familias independientes de cambio arquitectónico, todas pareadas y con eval "
                  "honesta → ninguna mueve la aguja.", 16, True, INK),
                 ("El cuello convergente es el DATO: desbalance, pocos positivos, contexto espacial.",
                  15, False, GRIS_BODY)])
    add_notes(s, "Síntesis del sprint (y de B4): agregador (DSMIL), 1ª capa (mammoth), lenguaje+tile "
                 "(PathPT) — 0 palancas. La triangulación es el resultado: el cuello es el dato, no el modelo.")

    # 17 · Próximos pasos
    s = content(prs, "Próximos pasos — dónde sí hay palanca")
    add_bullets(s, 0.9, 1.05, 11.7, 6.1, [
        ("Calibración del punto de operación (umbral por clase): salió del colapso mitótico "
         "(el AUC sobrevive, el argmax colapsa). Barato: re-umbralizar sin re-entrenar.", 0),
        ("Recuperación de casos similares (CBIR sobre features CONCH): valor clínico, sin re-entrenar.", 0),
        ("Magnificación / nº de parches (contexto espacial): atacar el cuello REAL = el dato.", 0),
        ("Más positivos y mejor balance en las tareas hambrientas de datos.", 0),
    ], size=24, anchor=MSO_ANCHOR.MIDDLE)
    add_notes(s, "Palancas ortogonales al modelo: calibrar el punto de operación (barato, sale de "
                 "mitótica), retrieval para valor clínico, y atacar el dato (magnificación, balance).")

    prs.save(DST)
    return prs


def main():
    prs = build()
    print(f"OK  {os.path.relpath(DST, REPO)}  slides={len(prs.slides)}")


if __name__ == "__main__":
    main()
