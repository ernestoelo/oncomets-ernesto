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


def add_connector(slide, x1, y1, x2, y2, color=RGBColor(0x8A, 0x8A, 0x8A), w=1.75):
    """Conector recto con punta de flecha (para el abanico router<->expertos)."""
    from pptx.enum.shapes import MSO_CONNECTOR
    from pptx.oxml.ns import qn
    cxn = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,
                                     Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    cxn.line.color.rgb = color; cxn.line.width = Pt(w)
    cxn.shadow.inherit = False
    ln = cxn.line._get_or_add_ln()
    tail = ln.makeelement(qn("a:tailEnd"), {"type": "triangle", "w": "med", "len": "med"})
    ln.append(tail)
    return cxn


def build_slide2(prs):
    """Zoom limpio: qué hace mammoth (router + expertos -> suma ponderada).

    Layout en abanico con conectores rectos (sin flechas sueltas) y sin caption.
    """
    blank = None
    for lay in prs.slide_layouts:
        if lay.name and "blank" in lay.name.lower():
            blank = lay; break
    blank = blank or prs.slide_layouts[-1]
    s = prs.slides.add_slide(blank)

    # (sin título interno: el header del deck pone el título branded coincidente)

    # geometría (contenido bajo el header del deck, centrado)
    feat = (0.7, 2.95, 2.6, 1.35)
    rout = (3.9, 2.95, 2.6, 1.35)
    ex_x, ex_w, ex_h = 7.1, 2.95, 1.2
    ex_y = [1.45, 3.05, 4.65]
    summ = (10.55, 2.95, 2.55, 1.35)
    cyc = 3.625                              # centro vertical de la fila principal

    # entrada
    add_box(s, *feat,
            [("FEATURE DEL PARCHE", 16, True, INK), ("z ∈ ℝ⁵¹²  (CONCH)", 14, False, GREY_T)],
            TEAL_F, RGBColor(0x2C, 0x7A, 0x8C))
    add_connector(s, feat[0] + feat[2], cyc, rout[0], cyc)

    # router
    add_box(s, *rout,
            [("ROUTER", 18, True, ORA_E), ("g(z) → pesos por experto", 13, False, GREY_T)],
            ORA_F, ORA_E, lw=2.5)

    # expertos (3 representativos)
    for i, lab in enumerate(["EXPERTO 1", "EXPERTO 2", "EXPERTO E"]):
        add_box(s, ex_x, ex_y[i], ex_w, ex_h,
                [(lab, 16, True, INK), ("z · Wₑ ,  rank ≪ 512", 13, False, GREY_T)],
                BLU_F, BLU_E)
        cy = ex_y[i] + ex_h / 2
        add_connector(s, rout[0] + rout[2], cyc, ex_x, cy)
        add_connector(s, ex_x + ex_w, cy, summ[0], cyc)

    # etiqueta
    lb = s.shapes.add_textbox(Inches(ex_x), Inches(6.15), Inches(ex_w), Inches(0.4))
    set_text(lb, [("expertos de bajo rango (especializados)", 13, False, GREY_T)],
             align=PP_ALIGN.CENTER)

    # suma ponderada
    add_box(s, *summ,
            [("SUMA PONDERADA", 16, True, INK), ("h = Σₑ gₑ(z)·(z Wₑ)", 14, False, GREY_T),
             ("h ∈ ℝ⁵¹²", 13, False, GREY_T)],
            TEAL_F, RGBColor(0x2C, 0x7A, 0x8C))
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
