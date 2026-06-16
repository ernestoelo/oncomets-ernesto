#!/usr/bin/env python
"""generate_pathpt_pptx.py — diagrama de ARQUITECTURA de PathPT (.pptx EDITABLE).

Rev. 5 (feedback Ernesto): MÁS ecuaciones + dimensiones de entrada/salida por bloque y
SIN solapamientos. Estilo calcado de Diagrama_CLAM.pptx: cascada central de bloques con
fórmula + dim, callouts de expansión a izquierda (dims visión) y derecha (ecuaciones del
matching), rama de texto a la derecha. Sin título interno (lo pone el header del deck),
sin bullets.

Ecuaciones (paper He et al. 2025, validadas en funcionamiento_pathpt.md §2; Fig 1b):
  vᵢ = Φᵥ(xᵢ)                          (extractor visión, congelado)
  ṽ = Ψ(v ; θᵥ)                        (módulo espacial: grilla 2D, conv 3/5/7 + transf.)
  c̄ⱼ = [T]₁…[T]ₖ [CLSⱼ] ;  tⱼ = Φₜ(c̄ⱼ)  (prompt-tuning + extractor texto, congelado)
  Pᵢⱼ = softmaxⱼ( ⟨tⱼ, ṽᵢ⟩ / τ )       (clasificación por parche; coseno texto–visión)
  ŷ = tumor-ratio_i(P) ;  mᵢ = argmaxⱼ Pᵢⱼ   (clase de slide + mapa de localización)

Color: azul = pipeline (como CLAM); gris = CONGELADO (CONCH); naranjo = ENTRENABLE (θ).

Uso: PYTHONPATH=/media/administrador/Storage1/sdonoso/clam_testing2/.pylibs \
     /home/sdonoso/miniconda3/envs/clam_latest/bin/python scripts/generate_pathpt_pptx.py
"""
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

REPO = "/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto"
DST = os.path.join(REPO, "papers/presentations/Diagrama_PathPT.pptx")

BLUE_F = RGBColor(0x6E, 0x9B, 0xC5)
BLUE_E = RGBColor(0x3C, 0x6A, 0x95)
NAVY   = RGBColor(0x14, 0x2A, 0x42)
FRZ_F  = RGBColor(0xE3, 0xE7, 0xEB)
FRZ_E  = RGBColor(0x9A, 0xA6, 0xB2)
FRZ_T  = RGBColor(0x4A, 0x54, 0x60)
ORA_F  = RGBColor(0xFB, 0xE2, 0xC8)
ORA_E  = RGBColor(0xE2, 0x72, 0x3B)
ORA_T  = RGBColor(0xB4, 0x52, 0x1E)
DIMF   = RGBColor(0xEC, 0xF1, 0xF5)
DIME   = RGBColor(0xB7, 0xC6, 0xD4)
DIM_T  = RGBColor(0x1F, 0x4E, 0x5F)
INK    = RGBColor(0x22, 0x22, 0x22)
GREY_T = RGBColor(0x55, 0x55, 0x55)
CARLITO = "Carlito"


def set_text(shape, lines, align=PP_ALIGN.CENTER):
    tf = shape.text_frame
    tf.word_wrap = True; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = tf.margin_right = Pt(3); tf.margin_top = tf.margin_bottom = Pt(1)
    for i, (txt, sz, bold, col) in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        r = p.add_run(); r.text = txt
        r.font.size = Pt(sz); r.font.bold = bold; r.font.name = CARLITO; r.font.color.rgb = col


def box(slide, l, t, w, h, lines, fill, edge, lw=1.5):
    sp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(l), Inches(t), Inches(w), Inches(h))
    sp.fill.solid(); sp.fill.fore_color.rgb = fill
    sp.line.color.rgb = edge; sp.line.width = Pt(lw); sp.shadow.inherit = False
    set_text(sp, lines)
    return sp


def callout(slide, l, t, w, h, lines):
    return box(slide, l, t, w, h, lines, DIMF, DIME, lw=1)


def arrow(slide, l, t, w, h, direction="down"):
    shp = {"down": MSO_SHAPE.DOWN_ARROW, "right": MSO_SHAPE.RIGHT_ARROW,
           "left": MSO_SHAPE.LEFT_ARROW}[direction]
    a = slide.shapes.add_shape(shp, Inches(l), Inches(t), Inches(w), Inches(h))
    a.fill.solid(); a.fill.fore_color.rgb = BLUE_E
    a.line.fill.background(); a.shadow.inherit = False
    return a


def connector(slide, x1, y1, x2, y2):
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.line.color.rgb = DIME; c.line.width = Pt(1.25); c.shadow.inherit = False
    return c


def textbox(slide, l, t, w, h, lines, align=PP_ALIGN.LEFT):
    tb = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    set_text(tb, lines, align=align)
    return tb


# ============================================================================
# Slide 1 — cascada matemática (forward), callouts a ambos lados (sin solape)
# ============================================================================

def build_slide1(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    cx, cw = 3.55, 3.35
    cmid = cx + cw / 2
    aw = 0.42

    # ----- cascada central (visión → matching → salida) -----
    box(s, cx, 0.95, cw, 0.74,
        [("INPUT — N PARCHES", 12.5, True, NAVY),
         ("xₖ , k = 1..N   ·   coords (x, y)", 10.5, False, NAVY)], BLUE_F, BLUE_E)
    arrow(s, cmid - aw / 2, 1.70, aw, 0.26)

    box(s, cx, 1.99, cw, 0.92,
        [("Φᵥ · EXTRACTOR VISIÓN  (congelado)", 11.5, True, FRZ_T),
         ("vᵢ = Φᵥ(xᵢ)   ·   vᵢ ∈ ℝ⁵¹²", 12, True, INK)], FRZ_F, FRZ_E)
    arrow(s, cmid - aw / 2, 2.92, aw, 0.26)

    box(s, cx, 3.21, cw, 1.12,
        [("θᵥ · AGREGACIÓN ESPACIAL  (entrenable)", 11, True, ORA_T),
         ("ṽ = Ψ(v ; θᵥ)", 12.5, True, INK),
         ("ṽ ∈ ℝ^(N×512)", 11, True, DIM_T)], ORA_F, ORA_E, lw=2)
    arrow(s, cmid - aw / 2, 4.34, aw, 0.26)

    box(s, cx, 4.63, cw, 1.12,
        [("MATCHING POR PARCHE", 12, True, NAVY),
         ("Pᵢⱼ = softmaxⱼ( ⟨ tⱼ , ṽᵢ ⟩ / τ )", 12.5, True, NAVY),
         ("P ∈ ℝ^(N×C)", 11, True, DIM_T)], BLUE_F, BLUE_E)
    arrow(s, cmid - aw / 2, 5.76, aw, 0.26)

    box(s, cx, 6.05, cw, 0.95,
        [("AGREGACIÓN tumor-ratio", 12, True, NAVY),
         ("ŷ ∈ ℝ^C  (clase slide)   ·   mapa loc. ∈ ℝ^N", 10.5, True, NAVY)], BLUE_F, BLUE_E)

    # ----- callouts de dimensión a la IZQUIERDA (visión) -----
    lx, lw_ = 0.42, 2.75
    connector(s, lx + lw_, 2.45, cx, 2.45)
    callout(s, lx, 2.15, lw_, 0.62, [("v ∈ ℝ^(N×512)  ·  features .pt", 11.5, True, DIM_T),
                                      ("(ya extraídas, no se recalculan)", 9.5, False, GREY_T)])
    connector(s, lx + lw_, 3.77, cx, 3.77)
    callout(s, lx, 3.40, lw_, 0.78, [("ordena parches por coords → grilla 2D", 10.5, True, INK),
                                      ("conv 3/5/7 (local) ⊕ transformer (global)", 9.5, False, GREY_T)])
    connector(s, lx + lw_, 5.19, cx, 5.19)
    callout(s, lx, 4.88, lw_, 0.62, [("UNA predicción por CADA parche", 11, True, INK),
                                      ("(C = nº de clases)", 9.5, False, GREY_T)])

    # ----- rama de TEXTO a la derecha (alimenta el matching) -----
    tx, tw = 7.55, 3.30
    box(s, tx, 3.20, tw, 1.00,
        [("θₜ · PROMPTS  (entrenable)", 11.5, True, ORA_T),
         ("c̄ⱼ = [T]₁ … [T]ₖ [CLSⱼ]", 11.5, True, INK)], ORA_F, ORA_E, lw=2)
    arrow(s, tx + tw / 2 - aw / 2, 4.21, aw, 0.26)
    box(s, tx, 4.50, tw, 1.05,
        [("Φₜ · EXTRACTOR TEXTO  (congelado)", 11, True, FRZ_T),
         ("tⱼ = Φₜ(c̄ⱼ)", 12, True, INK),
         ("t ∈ ℝ^(C×512)", 11, True, DIM_T)], FRZ_F, FRZ_E)
    # Φ_t → matching (flecha a la izquierda)
    arrow(s, cx + cw + 0.02, 4.92, tx - (cx + cw) - 0.06, 0.30, direction="left")

    # ----- callouts de ECUACIÓN a la derecha -----
    rx, rw = 11.05, 2.20
    callout(s, rx, 3.22, rw, 0.95, [("K = 32 tokens", 11, True, INK),
                                    ("aprendidos (CoOp)", 9.5, False, GREY_T),
                                    ("init. desde frase clínica", 9, False, GREY_T)])
    callout(s, rx, 4.55, rw, 0.98, [("⟨tⱼ, ṽᵢ⟩ = coseno", 11, True, DIM_T),
                                    ("texto ↔ visión", 9.5, False, GREY_T),
                                    ("τ = temperatura", 10, True, DIM_T)])

    # ----- callout tumor-ratio (abajo-derecha, junto a la salida) -----
    callout(s, 7.10, 6.05, 3.9, 0.95,
            [("tumor-ratio = fracción de parches positivos → clase de slide", 11, True, INK),
             ("mᵢ = argmaxⱼ Pᵢⱼ  →  mapa de localización ∈ ℝ^N", 10.5, True, DIM_T)])
    connector(s, cx + cw, 6.52, 7.10, 6.52)

    return s


# ============================================================================
# Slide 2 — los 3 componentes entrenables (zoom, referencia)
# ============================================================================

def _panel(s, x, header, steps):
    W = 4.0
    box(s, x, 1.20, W, 0.72, [(header, 14, True, ORA_T)], ORA_F, ORA_E, lw=2.25)
    y = 2.30
    for i, st in enumerate(steps):
        h = 0.82
        box(s, x + 0.25, y, W - 0.5, h, st, DIMF, DIME, lw=1)
        y += h
        if i < len(steps) - 1:
            arrow(s, x + W / 2 - 0.17, y - 0.02, 0.34, 0.30)
            y += 0.30


def build_slide2(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    _panel(s, 0.45, "θᵥ · MÓDULO ESPACIAL", [
        [("parches en grilla 2D (x, y)", 12, True, INK)],
        [("conv 3×3 / 5×5 / 7×7", 12, True, INK), ("vecindario local", 9.5, False, GREY_T)],
        [("transformer (global)", 12, True, INK)],
        [("ṽᵢ refinado · N×512", 12, True, DIM_T)],
    ])
    _panel(s, 4.65, "θₜ · PROMPT-TUNING", [
        [("[T]₁ [T]₂ ⋯ [T]ₖ [CLASE]", 12, True, INK)],
        [("Φₜ · CONCH texto (congelado)", 11.5, True, FRZ_T)],
        [("tⱼ vector de clase · C×512", 12, True, DIM_T)],
        [("aprende la frase, no la escribe", 11, True, ORA_T)],
    ])
    _panel(s, 8.85, "PSEUDO-LABELS (tile)", [
        [("coseno( parche , frase )", 12, True, INK)],
        [("clase tentativa del parche", 12, True, INK)],
        [("retener si concuerda con slide", 11.5, True, INK)],
        [("→ CE balanceada por clase", 12, True, DIM_T)],
    ])
    return s


def main():
    prs = Presentation()
    prs.slide_width = Inches(13.333); prs.slide_height = Inches(7.5)
    build_slide1(prs); build_slide2(prs)
    prs.save(DST)
    chk = Presentation(DST)
    has = any(x.has_text_frame and "MATCHING" in x.text for x in chk.slides[0].shapes)
    print(f"OK  {os.path.relpath(DST, REPO)}  slides={len(chk.slides)}  "
          f"s1_shapes={len(chk.slides[0].shapes)}  matching={has}")


if __name__ == "__main__":
    main()
