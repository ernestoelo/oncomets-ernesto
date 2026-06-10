#!/usr/bin/env python
"""generate_clam_mammoth_pptx.py — copia editable de Diagrama_CLAM.pptx con mammoth.

Entrega .pptx EDITABLE (no PNG), mismo molde que la referencia Diagrama_CLAM.pptx:
  - Slide 1: el diagrama CLAM original, con el bloque de la 1ª capa lineal
    (FULLY CONNECTED) resaltado y re-rotulado como MAMMOTH (MoE) — muestra DÓNDE va.
  - Slide 2 (nueva, lienzo limpio): zoom de QUÉ HACE mammoth (router + expertos de
    bajo rango → suma ponderada). Sin proceso de entrenamiento, sin nombres (convención
    de la presentación). Editable a mano en PowerPoint.

NOTA de arquitectura (codebase models_mammoth/): mammoth reemplaza la **1ª capa lineal**
de CLAM (el FULLY CONNECTED tras el extractor), NO el bloque final rotulado "CAPA LINEAL"
(que es el clasificador por clase). Por eso se modifica el FULLY CONNECTED.

Requiere python-pptx (instalado en /media/administrador/Storage1/sdonoso/clam_testing2/.pylibs).
Uso: PYTHONPATH=/media/administrador/Storage1/sdonoso/clam_testing2/.pylibs \
     /home/sdonoso/miniconda3/envs/clam_latest/bin/python scripts/generate_clam_mammoth_pptx.py
"""
import os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

REPO = "/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto"
SRC = os.path.join(REPO, "papers/presentations/Diagrama_CLAM.pptx")
DST = os.path.join(REPO, "papers/presentations/Diagrama_CLAM_mammoth.pptx")

TEAL_F = RGBColor(0xB8, 0xD4, 0xD9)   # teal de la referencia
ORA_F  = RGBColor(0xFC, 0xE5, 0xCD)   # highlight naranjo (mammoth = lo que cambia)
ORA_E  = RGBColor(0xE2, 0x72, 0x3B)
BLU_F  = RGBColor(0xEA, 0xF2, 0xFB)
BLU_E  = RGBColor(0x5B, 0x8F, 0xB9)
GREY_E = RGBColor(0x9A, 0xA6, 0xB2)
INK    = RGBColor(0x22, 0x22, 0x22)
GREY_T = RGBColor(0x55, 0x55, 0x55)
CARLITO = "Carlito"


def set_text(shape, lines, align=PP_ALIGN.CENTER):
    """lines = [(text, size, bold, color), ...] -> párrafos."""
    tf = shape.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = tf.margin_right = Pt(2)
    tf.margin_top = tf.margin_bottom = Pt(1)
    for i, (txt, sz, bold, col) in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        r = p.add_run(); r.text = txt
        r.font.size = Pt(sz); r.font.bold = bold; r.font.name = CARLITO
        r.font.color.rgb = col


def add_box(slide, l, t, w, h, lines, fill, edge, lw=1.5, shape=MSO_SHAPE.ROUNDED_RECTANGLE):
    sp = slide.shapes.add_shape(shape, Inches(l), Inches(t), Inches(w), Inches(h))
    sp.fill.solid(); sp.fill.fore_color.rgb = fill
    sp.line.color.rgb = edge; sp.line.width = Pt(lw)
    sp.shadow.inherit = False
    set_text(sp, lines)
    return sp


def add_arrow(slide, l, t, w, h, down=False):
    shp = MSO_SHAPE.DOWN_ARROW if down else MSO_SHAPE.RIGHT_ARROW
    a = slide.shapes.add_shape(shp, Inches(l), Inches(t), Inches(w), Inches(h))
    a.fill.solid(); a.fill.fore_color.rgb = RGBColor(0x8A, 0x8A, 0x8A)
    a.line.fill.background(); a.shadow.inherit = False
    return a


def edit_slide1(slide):
    """Resalta el bloque FULLY CONNECTED y lo re-rotula MAMMOTH."""
    # process box detrás del FC (geometría ~L4.85 T1.45)
    for sh in slide.shapes:
        try:
            if (sh.shape_type == 1 and 4.7 < Emu(sh.left).inches < 5.05
                    and 1.40 < Emu(sh.top).inches < 1.55 and 2.8 < Emu(sh.width).inches < 3.3):
                sh.fill.solid(); sh.fill.fore_color.rgb = ORA_F
                sh.line.color.rgb = ORA_E; sh.line.width = Pt(2.25)
        except Exception:
            pass
    # text box "FULLY CONNECTED" -> mammoth
    for sh in slide.shapes:
        if sh.has_text_frame and "FULLY CONNECTED" in sh.text:
            sh.text_frame.clear()
            set_text(sh, [
                ("MAMMOTH  (MoE)", 8, True, ORA_E),
                ("reemplaza la 1ª capa lineal", 7, False, INK),
                ("mezcla de expertos de bajo rango", 6.5, False, GREY_T),
            ])
            break


def build_slide2(prs):
    """Zoom limpio: qué hace mammoth (router + expertos -> suma ponderada)."""
    blank = None
    for lay in prs.slide_layouts:
        if lay.name and "blank" in lay.name.lower():
            blank = lay; break
    blank = blank or prs.slide_layouts[-1]
    s = prs.slides.add_slide(blank)

    # título
    tb = s.shapes.add_textbox(Inches(0.5), Inches(0.25), Inches(12.3), Inches(0.7))
    set_text(tb, [("MAMMOTH — qué hace (zoom de la 1ª capa de CLAM)", 20, True, RGBColor(0x1F,0x4E,0x5F))],
             align=PP_ALIGN.LEFT)

    # entrada
    add_box(s, 0.6, 3.05, 2.5, 1.1,
            [("FEATURE DEL PARCHE", 11, True, INK), ("z ∈ ℝ⁵¹²  (CONCH)", 10, False, GREY_T)],
            TEAL_F, RGBColor(0x2C,0x7A,0x8C))
    add_arrow(s, 3.2, 3.42, 0.55, 0.38)

    # router
    add_box(s, 3.9, 3.05, 2.2, 1.1,
            [("ROUTER / GATING", 11, True, ORA_E), ("g(z) → pesos por experto", 9.5, False, GREY_T)],
            ORA_F, ORA_E, lw=2)

    # expertos (3 representativos + "…")
    ex_x = 6.55
    for i, lab in enumerate(["EXPERTO 1", "EXPERTO 2", "EXPERTO E"]):
        add_box(s, ex_x, 1.6 + i*1.5, 2.5, 1.05,
                [(lab + "  (bajo rango)", 10, True, INK), ("z · Wₑ ,  rank ≪ 512", 9, False, GREY_T)],
                BLU_F, BLU_E)
    tb2 = s.shapes.add_textbox(Inches(ex_x), Inches(4.15), Inches(2.5), Inches(0.4))
    set_text(tb2, [("⋮", 16, True, GREY_T)])
    # router -> expertos (3 flechitas)
    for i in range(3):
        add_arrow(s, 6.05, 1.95 + i*1.5, 0.45, 0.32)

    # suma ponderada
    add_box(s, 9.55, 3.05, 2.55, 1.15,
            [("SUMA PONDERADA", 11, True, INK), ("h = Σₑ gₑ(z) · (z Wₑ)", 10, False, GREY_T),
             ("h ∈ ℝ⁵¹²", 9.5, False, GREY_T)],
            TEAL_F, RGBColor(0x2C,0x7A,0x8C))
    for i in range(3):
        add_arrow(s, 9.1, 1.95 + i*1.5, 0.42, 0.30)

    # caption
    cap = ("En CLAM, la 1ª capa es UNA proyección lineal (H = ReLU(Z·W₁ᵀ)). Mammoth la reemplaza por una "
           "MEZCLA DE EXPERTOS de bajo rango con un router que enruta cada parche a expertos especializados "
           "(mitiga la interferencia de gradientes entre instancias). El resto de CLAM no cambia.")
    cb = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(5.55), Inches(12.1), Inches(1.25))
    cb.fill.solid(); cb.fill.fore_color.rgb = RGBColor(0xF7,0xF8,0xFA)
    cb.line.color.rgb = RGBColor(0xC9,0xCD,0xD2); cb.line.width = Pt(1); cb.shadow.inherit = False
    set_text(cb, [(cap, 11, False, RGBColor(0x33,0x33,0x33))], align=PP_ALIGN.LEFT)
    return s


def main():
    prs = Presentation(SRC)
    edit_slide1(prs.slides[0])
    build_slide2(prs)
    prs.save(DST)
    # verificación textual (sin imagen)
    chk = Presentation(DST)
    s1_has = any(sh.has_text_frame and "MAMMOTH" in sh.text for sh in chk.slides[0].shapes)
    print(f"OK  {os.path.relpath(DST, REPO)}  slides={len(chk.slides)}  "
          f"slide1_mammoth={s1_has}  slide2_shapes={len(chk.slides[1].shapes)}")


if __name__ == "__main__":
    main()
