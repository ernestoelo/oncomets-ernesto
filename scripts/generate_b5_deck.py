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
import io
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
# slide 0 = figura oficial fusionada (overlay de dims) · slide 1 = variante keep_slots.
# Generado por scripts/generate_mammoth_fused_slide.py (correr ANTES del deck).
DIAG_FUSED = os.path.join(PRES, "Diagrama_mammoth_fused.pptx")
# figura oficial de PathPT (panel b) con callouts overlay del forward.
# Generado por scripts/generate_pathpt_fused_slide.py (correr ANTES del deck).
DIAG_PPT_FUSED = os.path.join(PRES, "Diagrama_pathpt_fused.pptx")

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


def set_notes(slide, proposito, narrativa, puntos=None, nsz=13):
    """Notas del presentador estructuradas y legibles:
       PROPÓSITO — <una frase>  +  narrativa (párrafo/s)  +  PUNTOS CLAVE (viñetas).
    Sin nº de job, sin nombres (convención de la presentación)."""
    tf = slide.notes_slide.notes_text_frame
    tf.clear(); tf.word_wrap = True

    def _para(first=False):
        return tf.paragraphs[0] if first else tf.add_paragraph()

    # Todo el texto en BLANCO (las notas se leen sobre fondo oscuro) — pedido de Ernesto.
    # PROPÓSITO (etiqueta + frase)
    p = _para(first=True); p.space_after = Pt(9)
    r = p.add_run(); r.text = "PROPÓSITO — "
    r.font.bold = True; r.font.size = Pt(nsz); r.font.name = F_BODY; r.font.color.rgb = WHITE
    r2 = p.add_run(); r2.text = proposito
    r2.font.size = Pt(nsz); r2.font.name = F_BODY; r2.font.color.rgb = WHITE

    # narrativa (uno o más párrafos bien elaborados)
    for para in (narrativa if isinstance(narrativa, (list, tuple)) else [narrativa]):
        pp = _para(); pp.space_after = Pt(9)
        rr = pp.add_run(); rr.text = para
        rr.font.size = Pt(nsz); rr.font.name = F_BODY; rr.font.color.rgb = WHITE

    # PUNTOS CLAVE (viñetas)
    if puntos:
        ph = _para(); ph.space_before = Pt(3); ph.space_after = Pt(4)
        rh = ph.add_run(); rh.text = "PUNTOS CLAVE"
        rh.font.bold = True; rh.font.size = Pt(nsz); rh.font.name = F_BODY; rh.font.color.rgb = WHITE
        for pt in puntos:
            pb = _para(); pb.space_after = Pt(3)
            rb = pb.add_run(); rb.text = "•  " + pt
            rb.font.size = Pt(nsz); rb.font.name = F_BODY; rb.font.color.rgb = WHITE


def _rect(slide, l, t, w, h, color):
    sp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(l), Inches(t), Inches(w), Inches(h))
    sp.fill.solid(); sp.fill.fore_color.rgb = color
    sp.line.fill.background(); sp.shadow.inherit = False
    return sp


def logo_mark(slide):
    _rect(slide, 0, 0, HDR, HDR, TEAL_SQ)
    slide.shapes.add_picture(LOGO, Inches(0.09), Inches(0.09), height=Inches(0.64))


def header(slide, title, bar=True):
    """Header consistente: (barra gris) + cuadrado teal + logo + título Barlow teal.
    title=None → solo logo (para diagramas a sangre que no deben taparse con el título)."""
    if bar:
        _rect(slide, 0, 0, SW, HDR, BAR_GRIS)
    logo_mark(slide)
    if title:
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


def add_vcard(slide, l, t, w, h, title, body, tcol=ORA_T, tsize=17, bsize=14):
    """Tarjeta vertical: título color + cuerpo gris (para los 3 componentes)."""
    sp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(l), Inches(t), Inches(w), Inches(h))
    sp.fill.solid(); sp.fill.fore_color.rgb = TEAL_CARD2
    sp.line.color.rgb = TEAL_SQ; sp.line.width = Pt(1.5); sp.shadow.inherit = False
    _set_runs(sp.text_frame, [(title, tsize, True, tcol, F_BODY, PP_ALIGN.CENTER),
                              (body, bsize, False, GRIS_BODY, F_BODY, PP_ALIGN.CENTER)],
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
    src_slide = src.slides[idx]
    spTree = s.shapes._spTree
    for shp in src_slide.shapes:
        el = copy.deepcopy(shp._element)
        for cNvPr in el.iter(qn("p:cNvPr")):
            _uid[0] += 1; cNvPr.set("id", str(_uid[0]))
        # imágenes embebidas: el deepcopy NO arrastra la relación r:embed → copiar el
        # image part al slide destino y remapear el rId (si no, la figura desaparece).
        for blip in el.iter(qn("a:blip")):
            r_embed = blip.get(qn("r:embed"))
            if r_embed:
                img_part = src_slide.part.related_part(r_embed)
                _, new_rid = s.part.get_or_add_image_part(io.BytesIO(img_part.blob))
                blip.set(qn("r:embed"), new_rid)
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
# keep_slots=True (cuello de botella aprendido N→300, vs el drop-in keep_slots=False de MAM8).
# C2 = Δ bal_acc vs CLAM (¿palanca?) · recall clase rara drop-in→keep_slots · CLAM (ref.).
MAM_KST_HEAD = ["Tarea  (config keep_slots = True)", "Δ bal_acc\nvs CLAM", "Recall clase rara\ndrop-in → keep_slots",
                "CLAM\n(ref.)", "Lectura"]
MAM_KST = [
    ("Invasión linfovascular (3 cl.)", "−0.031 ± 0.047", "presente  0.43 → 0.52", "0.58", "no supera", GRIS_TXT),
    ("Microcalc · carcinoma inv.",     "−0.020 ± 0.121", "sí  0.29 → 0.31",        "0.37", "no supera", GRIS_TXT),
    ("Microcalc · CDIS",               "−0.023 ± 0.120", "sí  0.28 → 0.44",        "0.38", "no supera *", AMBAR),
    ("Microcalc · tejido no neopl.",   "+0.046 ± 0.106", "balanceada (sin rara)",  "—",    "ruido", GRIS_TXT),
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
    ("Patch-embed\n(1ª capa de proyección)", "Mammoth\n(mixture-of-experts)", "12 tareas (microcalc, patrón, invasión)", "0 palancas\n(8 drop-in + 4 keep_slots)"),
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
    set_notes(s,
        "abrir la presentación y encuadrar el sprint en una sola frase.",
        "Este es el cierre del sprint B5. El trimestre giró en torno a una pregunta concreta: "
        "¿alguna modificación de la arquitectura de CLAM mueve la aguja en nuestras tareas "
        "clínicas? Para responderla integramos y medimos dos modelos —MAMMOTH y PathPT— con un "
        "protocolo de evaluación común y honesto.",
        ["Dos encargos: integrar y medir MAMMOTH; integrar y explicar PathPT (visión + lenguaje).",
         "Todo corre sobre features CONCH y se compara contra CLAM como baseline.",
         "El hilo conductor del deck: separar el 'efecto del modelo' del 'efecto del dato'."])

    # 2 · Objetivos
    s = content(prs, "Objetivos del sprint")
    add_bullets(s, 0.9, 1.05, 11.7, 6.0, [
        ("MAMMOTH: cómo funciona e integra en CLAM — diagrama + resultados.", 0),
        ("PathPT: integrar y explicar el modelo (visión + lenguaje) — diagrama + resultados.", 0),
        ("Marco de evaluación común:", 0),
        ("Comparación PAREADA con validación cruzada k=5 (mismos splits).", 1),
        ("Métrica honesta: balanced accuracy + AUC + matriz de confusión.", 1),
    ], size=30, sub_size=25, anchor=MSO_ANCHOR.MIDDLE)
    set_notes(s,
        "fijar la vara de medición ANTES de mostrar cualquier resultado.",
        "Antes de los números conviene dejar claro cómo vamos a juzgarlos. Cada modelo se compara "
        "contra CLAM sobre exactamente los mismos splits (comparación pareada), con validación "
        "cruzada k=5 para no fiarnos de un único sorteo. Y reportamos siempre balanced accuracy "
        "junto al AUC y la matriz de confusión, porque con clases desbalanceadas una sola métrica "
        "engaña.",
        ["Comparación PAREADA: el Δ por fold cancela la varianza del sorteo y revela señales chicas.",
         "k=5 (validación cruzada) en lugar de un solo split optimista.",
         "Métrica honesta = balanced_acc + AUC + matriz de confusión, nunca el AUC a secas."])

    # ===== MAMMOTH =====
    s = divider(prs, "MAMMOTH", "Mixture-of-Experts en la primera capa de CLAM (patch-embed)")
    set_notes(s,
        "abrir el primer bloque y anticipar el eje que ataca MAMMOTH.",
        "Empezamos por MAMMOTH, una intervención en la primera capa de CLAM (el patch-embed). La "
        "pregunta de este bloque: reemplazar esa capa por una mezcla de expertos, ¿reduce la "
        "interferencia de gradientes y mejora la predicción?",
        ["Eje atacado: la capa de proyección de los parches.",
         "Estructura del bloque: qué es → dónde va → qué hace → resultados."])

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
    set_notes(s,
        "dar la intuición de MAMMOTH y por qué podría ayudar, sin matemática.",
        "En CLAM, una única capa lineal proyecta todos los parches al espacio interno del MIL. El "
        "problema: parches de fenotipos muy distintos en la misma slide empujan gradientes en "
        "conflicto sobre esa capa —la 'interferencia de gradientes'—. MAMMOTH la reemplaza por una "
        "mezcla de expertos, de modo que cada experto puede especializarse en un sub-fenotipo sin "
        "pisar a los demás.",
        ["Reemplaza SOLO la 1ª capa lineal; el resto de CLAM queda intacto → comparación limpia.",
         "Motivación: desacoplar los gradientes de parches heterogéneos.",
         "Es un cambio quirúrgico: cualquier diferencia es atribuible a esa capa."])

    s = copy_diagram(prs, DIAG_MAM, 0, None, bar=False)   # sin título: tapaba el diagrama
    set_notes(s,
        "ubicar visualmente DÓNDE entra MAMMOTH en el pipeline de CLAM.",
        "Sobre nuestro diagrama de CLAM, el bloque naranja marca el único punto que cambia: la "
        "primera capa totalmente conectada, justo después del extractor CONCH. Todo lo de aguas "
        "abajo —atención, pooling, clasificadores— es CLAM sin tocar.",
        ["El bloque naranja = la capa que MAMMOTH sustituye.",
         "OJO: no es la capa lineal FINAL (esa es el clasificador por clase).",
         "Drop-in: misma forma de entrada y de salida."])

    s = copy_diagram(prs, DIAG_MAM, 1, "MAMMOTH — qué hace (zoom de la 1ª capa)")
    set_notes(s,
        "abrir la caja negra y mostrar QUÉ HACE MAMMOTH por dentro, con dimensiones reales; "
        "dejar claro que cuesta el mismo presupuesto de parámetros que la capa lineal.",
        "Cada parche entra como una ficha CONCH de 512 números. W_q la reescribe contra 256 'varas' "
        "aprendidas y LayerNorm la normaliza: queda el query q, una ficha de búsqueda de 256 vista "
        "como 16 cabezas de 16. Hay 300 'slots' aprendidos (30 expertos x 10), cada uno con una "
        "clave S de 16 números por cabeza; comparamos q con cada clave por producto interno (puntaje "
        "de parecido). Atención a las DOS softmax distintas: el reparto D normaliza sobre los N "
        "parches (para cada slot, qué parches junta); la mezcla C normaliza sobre los 300 slots "
        "(para cada parche, a qué expertos escucha). Misma matriz de puntajes, dos normalizaciones "
        "por ejes opuestos.",
        ["Entra y sale [N, 512]: drop-in exacto de la 1a capa lineal.",
         "Query: q = LN(W_q z), 256 dims = 16 cabezas x 16 (las 'lentes' del panel derecho).",
         "DOS softmax: reparto D baja por los N parches; mezcla C baja por los 300 slots.",
         "Experto = LoRA: bajada COMPARTIDA 16->8 (rank 8) + subida PROPIA 8->32 (x16 cab = 512).",
         "rank 8 automatico => MoE pesa casi lo mismo que la FC 512x512 que reemplaza.",
         "Si MAMMOTH no mejora, NO es por falta de capacidad (ver resultados)."])

    # 6b · La MISMA mecánica del zoom, ahora sobre la figura OFICIAL del paper (+ dims overlay)
    s = copy_diagram(prs, DIAG_FUSED, 0, None, bar=False)   # full-bleed (lleva su propio título); logo only
    set_notes(s,
        "cerrar el lazo entre NUESTRO zoom y la figura oficial del paper: es el mismo pipeline, "
        "ahora con las dimensiones reales anotadas paso a paso encima de la figura de los autores.",
        "Esta es la figura oficial de MAMMOTH. Es exactamente lo que abrimos en el zoom anterior, pero "
        "vista de punta a punta: el encoder CONCH entrega z de 512; W_q proyecta al query; el ruteo por "
        "slots arma los 300 slots; los expertos de bajo rango los transforman; la combinación cross-head "
        "recompone y CLAM clasifica. Cada cartel verde es la forma del tensor que entra y sale de ese paso.",
        ["Es la MISMA 1ª capa del zoom anterior, ahora en la figura de los autores.",
         "Los carteles = forma del tensor entrada → salida por paso (verificados contra el código).",
         "Abajo a la izquierda: el experto por dentro (LoRA, slots → Φ·W → no-linealidad)."])

    # 6c · La variante keep_slots que también medimos (mismo tronco, bifurca la salida)
    s = copy_diagram(prs, DIAG_FUSED, 1, None, bar=False)   # nativo (lleva su propio título); logo only
    set_notes(s,
        "presentar la variante que también medimos: cambia SOLO la salida de MAMMOTH, no el tronco; "
        "anticipa el modo de falla que ataca (colapso a la mayoritaria).",
        "El tronco —encoder, query, ruteo, expertos— es idéntico al de la slide anterior. La variante "
        "cambia un único interruptor, keep_slots. En FALSE (el drop-in que medimos primero) MAMMOTH "
        "recombina los 300 slots de vuelta a los N parches: es un reemplazo transparente de la capa "
        "lineal. En TRUE (lo que también medimos) se queda con los 300 slot-tokens: un cuello de botella "
        "aprendido, más slot_dropout, pensado para darle capacidad dedicada a la clase minoritaria. Misma "
        "cabeza CLAM y misma pérdida: cambia solo qué se agrega, N parches o 300 slots.",
        ["keep_slots decide la salida: recombinar a N parches (False) o quedarse con 300 slots (True).",
         "TRUE = cuello de botella aprendido N→300 + slot_dropout (atención en 2 etapas).",
         "Motivación: recuperar recall de la clase rara que la variante drop-in colapsa.",
         "Evaluación pareada k=5 completada → resultados en las dos slides siguientes."])

    # 7 · Resultados 8 tareas drop-in (TABLA NATIVA)
    s = content(prs, "MAMMOTH drop-in — resultados (8 tareas, k=5)")
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
    set_notes(s,
        "mostrar la evidencia agregada: MAMMOTH no es palanca en 8 tareas.",
        "Ocho tareas pareadas, y el patrón es nítido: cero palancas consistentes. El único lean "
        "positivo —y leve— aparece en las dos tareas más balanceadas (tejido no neoplásico y patrón "
        "cribiforme). En el resto el efecto es nulo o una leve regresión, y en todas la varianza "
        "entre folds es mayor o igual al efecto medio.",
        ["Lo que predice el signo del efecto es el BALANCE de la clase, no la arquitectura.",
         "Donde hay pocos positivos, MAMMOTH no rescata nada.",
         "Varianza ≳ |efecto| → no hay señal por encima del ruido."])

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
                [("n = 2814 (el caso más sano): el drop-in agrava el colapso a la mayoritaria; AUC y "
                  "bal_acc bajan levemente. La variante keep_slots ataca justo este modo de falla → "
                  "siguiente slide.", 15, False, GRIS_TXT)])
    set_notes(s,
        "mostrar el modo de falla del drop-in en el caso más favorable a la medición.",
        "Esta es la tarea con más datos y la evaluación más sana (cada clase con suficientes casos "
        "por fold). Si MAMMOTH iba a brillar, sería acá. En cambio el drop-in agrava el colapso hacia "
        "la clase mayoritaria 'no identificado': sube su recall a costa de la clase 'presente', y tanto "
        "balanced accuracy como AUC bajan levemente en los 5 folds. Más poder estadístico no lo "
        "rescató: lo afinó. Este colapso es exactamente lo que la variante keep_slots intenta revertir.",
        ["n = 2814 y evaluación fold-a-fold: el escenario más limpio de todo el hilo.",
         "bal_acc 0.622 → 0.575 y AUC 0.828 → 0.818 (5/5 folds a la baja).",
         "El colapso a la mayoritaria es el modo de falla que ataca keep_slots (siguiente slide)."])

    # 8b · keep_slots=True — resultados (4 tareas, TABLA NATIVA) → cierre del hilo MAMMOTH
    s = content(prs, "MAMMOTH keep_slots — resultados (4 tareas, k=5)")
    rows = [[d[0], d[1], d[2], d[3], d[4]] for d in MAM_KST]
    cc = {}
    for i, d in enumerate(MAM_KST):
        cc[(i, 1)] = {"fg": GRIS_TXT, "bold": True}
        cc[(i, 4)] = {"fg": d[5], "bold": True}
    add_table(s, MAM_KST_HEAD, rows, 0.4, 1.05, 12.55, 4.35,
              col_fracs=[0.29, 0.16, 0.24, 0.10, 0.21],
              cell_colors=cc, fontsize=15, header_fontsize=14)
    add_textbox(s, 0.5, 5.6, 12.4, 1.6,
                [("El cuello de botella de slots revierte PARCIALMENTE el colapso a la mayoritaria del "
                  "drop-in (3/4 tareas: ↑ recall de la clase rara) — pero NO supera a CLAM en ninguna. "
                  "slot_dropout: descartado (net-negativo en las 4).", 15, False, GRIS_TXT),
                 ("→ Hilo MAMMOTH completo: 12 tareas (8 drop-in + 4 keep_slots), 0 palancas.",
                  17, True, INK),
                 ("* CDIS: keep_slots sube el recall de la clase rara por encima de CLAM, pero a costa "
                  "de la mayoritaria → la bal_acc total no mejora.", 12, False, GRIS_TXT)])
    set_notes(s,
        "mostrar el resultado de la variante keep_slots y cerrar el hilo MAMMOTH en 12 tareas.",
        "Esta es la variante diseñada para atacar justo el modo de falla anterior: el colapso a la "
        "clase mayoritaria. Y en parte lo logra: el cuello de botella de slots recupera recall de la "
        "clase rara en tres de las cuatro tareas. Pero esa redistribución no alcanza para superar a "
        "CLAM en ninguna —en balanced accuracy queda por debajo o en empate ruidoso—. El regularizador "
        "slot_dropout no aporta y se descarta. Con esto el hilo cierra en doce tareas y cero palancas.",
        ["keep_slots revierte PARCIALMENTE el colapso a la mayoritaria (3/4 tareas).",
         "Recupera recall de la clase rara, pero NO supera a CLAM en bal_acc en ninguna.",
         "slot_dropout descartado: net-negativo en las 4 tareas.",
         "Cierre del hilo MAMMOTH: 12 tareas, 0 palancas → el cuello sigue siendo el dato."])

    # ===== PATHPT =====
    s = divider(prs, "PathPT", "Visión + lenguaje: clasificación parche-a-parche sobre CONCH congelado")
    set_notes(s,
        "abrir el segundo bloque y marcar que cambiamos de eje.",
        "Cambiamos de eje: PathPT no toca el agregador ni la capa de proyección. Suma una palanca "
        "distinta —lenguaje y supervisión a nivel de parche— sobre el mismo CONCH congelado.",
        ["Visión + texto: cada parche se compara contra descripciones de clase.",
         "Clasifica parche a parche (y localiza), no solo la slide entera."])

    # 10 · Figura 1 COMPLETA del paper (a=MIL · b=PathPT · c=tareas · d=benchmarks) + caption de las 3 piezas
    s = content(prs, "PathPT — la idea y el alcance (figura del paper)")
    add_image_fit(s, os.path.join(PAPER_FIGS, "pathpt_fig1_full.png"), 0.5, 0.95, 12.33, 5.55, align="center")
    add_textbox(s, 0.5, 6.58, 12.33, 0.78,
                [("Arriba:  a) MIL clásico   vs   b) PathPT (clasifica parche-a-parche; visión + texto sobre "
                  "CONCH congelado).   Abajo:  c) abanico de tareas   ·   d) benchmarks del paper.",
                  13, False, GRIS_TXT),
                 ("3 piezas livianas entrenables:   θᵥ contexto espacial   ·   θₜ prompt-tuning   ·   "
                  "pseudo-labels (tile).   Todo lo demás (CONCH) queda congelado.", 13, True, ORA_T)],
                anchor=MSO_ANCHOR.MIDDLE)
    set_notes(s,
        "presentar la idea de PathPT y su alcance con la figura oficial completa del paper.",
        "Esta es la figura del paper completa. Arriba, la comparación: a la izquierda el MIL clásico "
        "—comprime la slide a un vector y clasifica la slide entera—; a la derecha PathPT, que clasifica "
        "parche a parche comparando contra texto y además localiza el hallazgo. Abajo, el alcance: el "
        "abanico de tareas que cubre y los benchmarks donde PathPT compite contra los MIL. Todo corre "
        "sobre CONCH congelado; solo se entrenan tres piezas livianas.",
        ["a) MIL clásico  vs  b) PathPT (parche-a-parche, visión + texto).",
         "c) abanico de tareas  ·  d) benchmarks del paper (PathPT vs MIL).",
         "Solo se entrenan θᵥ (contexto espacial), θₜ (prompt) + pseudo-labels tile; CONCH congelado."])

    # 11 · Diagrama arquitectura (matemático)
    s = copy_diagram(prs, DIAG_PPT, 0, "PathPT — arquitectura (forward)")
    set_notes(s,
        "mostrar el forward completo de PathPT, code-accurate, con el mismo estilo que el de CLAM.",
        "El diagrama tiene tres ramas que convergen: visión, texto y matching. Lo gris está "
        "congelado (los encoders CONCH); lo naranja se entrena (θᵥ y θₜ). La clase de cada parche "
        "sale del coseno texto-visión y luego se agrega a una predicción de slide más un mapa de "
        "localización del hallazgo.",
        ["Φᵥ / Φₜ congelados; θᵥ / θₜ entrenables.",
         "512 = dimensión contrastiva (matching); 768 = dimensión del token donde viven los ctx.",
         "Es el forward puro: la lectura/agregación y el entrenamiento van en otras slides."])

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
    set_notes(s,
        "primer resultado de PathPT — no aporta sobre CLAM.",
        "En necrosis el veredicto es H_alt: PathPT no aporta. El Δ pareado de balanced accuracy "
        "cruza el cero y el de AUC es levemente negativo. De hecho el modelo apenas se despega de "
        "su 'teacher' zero-shot (~0.62), mientras CLAM llega a 0.727.",
        ["Δ bal_acc −0.020 ± 0.078;  Δ AUC −0.066 ± 0.094 (cruzan o rozan el 0).",
         "El entrenamiento casi no mejora sobre el etiquetado zero-shot de partida.",
         "Mismo split que CLAM (pareado) → la comparación es limpia."])

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
    set_notes(s,
        "mostrar un colapso instructivo y de dónde sale la próxima palanca.",
        "Acá PathPT colapsa: predice siempre la clase mayoritaria (score_1), con balanced accuracy "
        "exactamente 0.333 y cero predicciones de score_2 o 3. No es un bug —CLAM, sobre los mismos "
        "splits, no colapsa—. Es la formulación ordinal (clase 0 = score basal) la que domina el "
        "pseudo-etiquetado. Lo interesante: el AUC sobrevive (~0.66), o sea el ranking latente está "
        "pero el punto de corte está mal.",
        ["bal_acc 0.333 (trivial) vs CLAM 0.494, sobre los mismos splits.",
         "No es bug: es la formulación; pendiente de sign-off clínico.",
         "El AUC sobrevive → el cuello es la CALIBRACIÓN del punto de operación."])

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
    set_notes(s,
        "mostrar un descarte barato y bien hecho — el patrón Etapa 0 (CPU antes que GPU).",
        "Antes de gastar GPU probamos un etiquetado zero-shot en CPU, en minutos. CONCH no logra "
        "separar microcalcificaciones: el AUC va de 0.44 a 0.63 según la tarea y —contraintuitivo— "
        "afinar los prompts con más morfología lo empeoró. Veredicto NO-GO, sin quemar ~18–24 h de "
        "GPU.",
        ["Patrón Etapa 0: zero-shot barato ANTES del entrenamiento caro.",
         "CONCH no 'groundea' microcalcificaciones (AUC ≤ 0.63).",
         "Iterar prompts con más detalle morfológico no ayudó (mismo patrón que necrosis)."])

    # ===== CIERRE =====
    s = divider(prs, "Cierre y próximos pasos", "Tres ejes de arquitectura → dónde sí hay palanca")
    set_notes(s,
        "abrir la síntesis y los próximos pasos.",
        "Con los tres ejes ya medidos, toca juntar el resultado en una sola lectura y decir, a "
        "partir de eso, dónde sí conviene invertir esfuerzo.",
        ["Cierra los 3 ejes de arquitectura del sprint.",
         "La conclusión converge: por eso el último mensaje son los próximos pasos."])

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
    set_notes(s,
        "la tesis del sprint en una sola tabla — 3 ejes independientes, 0 palancas.",
        "Atacamos tres familias independientes de cambio arquitectónico —el agregador (DSMIL), la "
        "capa de proyección (MAMMOTH) y el lenguaje + supervisión tile (PathPT)—, todas pareadas y "
        "con evaluación honesta. Ninguna mueve la aguja. Esa triangulación ES el resultado: el "
        "cuello de botella no es el modelo, es el dato.",
        ["Tres ejes distintos, mismo veredicto → conclusión robusta, no un accidente de una prueba.",
         "El cuello convergente: desbalance, pocos positivos y contexto espacial.",
         "Deja de tener sentido buscar la palanca dentro de la arquitectura."])

    # 17 · Próximos pasos
    s = content(prs, "Próximos pasos — dónde sí hay palanca")
    add_bullets(s, 0.9, 1.05, 11.7, 6.1, [
        ("Calibración del punto de operación (umbral por clase): salió del colapso mitótico "
         "(el AUC sobrevive, el argmax colapsa). Barato: re-umbralizar sin re-entrenar.", 0),
        ("Recuperación de casos similares (CBIR sobre features CONCH): valor clínico, sin re-entrenar.", 0),
        ("Magnificación / nº de parches (contexto espacial): atacar el cuello REAL = el dato.", 0),
        ("Más positivos y mejor balance en las tareas hambrientas de datos.", 0),
    ], size=24, anchor=MSO_ANCHOR.MIDDLE)
    set_notes(s,
        "convertir el 'no-resultado' en una agenda con palancas reales.",
        "Que la arquitectura no sea palanca no nos deja sin jugadas; nos las reordena hacia cosas "
        "ortogonales al modelo. La más barata salió del colapso mitótico: calibrar el punto de "
        "operación, porque el AUC ya está pero el argmax no. Después, recuperación de casos "
        "similares (valor clínico sin re-entrenar) y, sobre todo, atacar el dato.",
        ["Calibración del umbral por clase: barata, sin re-entrenar.",
         "CBIR sobre features CONCH: valor clínico inmediato.",
         "Magnificación / nº de parches y más positivos: atacar el cuello REAL = el dato."])

    prs.save(DST)
    return prs


def main():
    prs = build()
    print(f"OK  {os.path.relpath(DST, REPO)}  slides={len(prs.slides)}")


if __name__ == "__main__":
    main()
