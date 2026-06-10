#!/usr/bin/env python
"""generate_pathpt_pptx.py — diagrama de ARQUITECTURA de PathPT (.pptx EDITABLE).

Entrega un .pptx editable a mano (NO PNG), mismo estilo que Diagrama_CLAM.pptx
(rounded-rect teal B8D4D9, fuente Carlito, flechas block). Fuente conceptual:
sprints/B5_sprint5/pathpt/funcionamiento_pathpt.md (7 ecuaciones, 3 componentes).

Idea central que comunica el diagrama:
  PathPT clasifica PARCHE por PARCHE sobre CONCH CONGELADO (Φ_v + Φ_t). Reusa las
  features visuales Φ_v ya extraídas, ENCIENDE el encoder de texto Φ_t (que CLAM
  ignora) y entrena solo 2 módulos chicos: θ_v (contexto espacial) y θ_t (prompts).
  Salida doble: clase de slide + mapa de localización.

Código de color (lectura inmediata):
  - TEAL  = bloque estándar del pipeline (igual que la referencia CLAM).
  - GRIS  = CONGELADO (encoders de CONCH; no se entrenan).
  - NARANJO = ENTRENABLE (θ_v, θ_t; lo único que se aprende).

Convenciones de la presentación: SIN nombres, SIN proceso de entrenamiento
(no losses/épocas/optimizador) — solo la arquitectura del forward.

Requiere python-pptx (en /media/administrador/Storage1/sdonoso/clam_testing2/.pylibs).
Uso: PYTHONPATH=/media/administrador/Storage1/sdonoso/clam_testing2/.pylibs \
     /home/sdonoso/miniconda3/envs/clam_latest/bin/python scripts/generate_pathpt_pptx.py
"""
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

REPO = "/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto"
DST = os.path.join(REPO, "papers/presentations/Diagrama_PathPT.pptx")

# ---- paleta (alineada con Diagrama_CLAM.pptx / generate_clam_mammoth_pptx.py) ----
TEAL_F = RGBColor(0xB8, 0xD4, 0xD9)   # bloque estándar del pipeline
TEAL_E = RGBColor(0x2C, 0x7A, 0x8C)
ORA_F  = RGBColor(0xFC, 0xE5, 0xCD)   # ENTRENABLE (θ_v, θ_t)
ORA_E  = RGBColor(0xE2, 0x72, 0x3B)
FRZ_F  = RGBColor(0xE3, 0xE7, 0xEB)   # CONGELADO (encoders CONCH)
FRZ_E  = RGBColor(0x9A, 0xA6, 0xB2)
FRZ_T  = RGBColor(0x5A, 0x64, 0x70)
OUT_E  = RGBColor(0x1F, 0x4E, 0x5F)   # borde del bloque de salida
INK    = RGBColor(0x22, 0x22, 0x22)
GREY_T = RGBColor(0x55, 0x55, 0x55)
TITLE  = RGBColor(0x1F, 0x4E, 0x5F)
CARLITO = "Carlito"


def set_text(shape, lines, align=PP_ALIGN.CENTER):
    """lines = [(text, size, bold, color), ...] -> párrafos."""
    tf = shape.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = tf.margin_right = Pt(3)
    tf.margin_top = tf.margin_bottom = Pt(1)
    for i, (txt, sz, bold, col) in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        r = p.add_run(); r.text = txt
        r.font.size = Pt(sz); r.font.bold = bold; r.font.name = CARLITO
        r.font.color.rgb = col


def add_box(slide, l, t, w, h, lines, fill, edge, lw=1.5, align=PP_ALIGN.CENTER):
    sp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                Inches(l), Inches(t), Inches(w), Inches(h))
    sp.fill.solid(); sp.fill.fore_color.rgb = fill
    sp.line.color.rgb = edge; sp.line.width = Pt(lw)
    sp.shadow.inherit = False
    set_text(sp, lines, align=align)
    return sp


def add_arrow(slide, l, t, w, h, down=False):
    shp = MSO_SHAPE.DOWN_ARROW if down else MSO_SHAPE.RIGHT_ARROW
    a = slide.shapes.add_shape(shp, Inches(l), Inches(t), Inches(w), Inches(h))
    a.fill.solid(); a.fill.fore_color.rgb = RGBColor(0x8A, 0x8A, 0x8A)
    a.line.fill.background(); a.shadow.inherit = False
    return a


def add_textbox(slide, l, t, w, h, lines, align=PP_ALIGN.LEFT):
    tb = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    set_text(tb, lines, align=align)
    return tb


def build(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])   # blank

    # ---- título ----
    add_textbox(s, 0.4, 0.18, 12.5, 0.6,
                [("PathPT — arquitectura: clasificación por parche sobre CONCH congelado",
                  20, True, TITLE)])

    # ---- leyenda (los colores se explican solos) ----
    add_box(s, 0.4, 1.0, 2.85, 0.34,
            [("CONGELADO — no se entrena", 9, True, FRZ_T)], FRZ_F, FRZ_E, lw=1)
    add_box(s, 3.4, 1.0, 2.85, 0.34,
            [("ENTRENABLE — θ_v , θ_t", 9, True, ORA_E)], ORA_F, ORA_E, lw=1)

    # ============ RAMA DE TEXTO (arriba): θ_t -> Φ_t -> (baja a clasificación) ====
    add_box(s, 4.7, 1.55, 2.45, 1.15,
            [("θ_t · PROMPTS APRENDIBLES", 10, True, ORA_E),
             ("[T]₁ … [T]₃₂  [CLASE]", 9.5, False, INK),
             ("frase de clase optimizada", 8, False, GREY_T)],
            ORA_F, ORA_E, lw=2)
    add_arrow(s, 7.18, 1.96, 0.34, 0.32)
    add_box(s, 7.55, 1.55, 2.45, 1.15,
            [("Φ_t · CONCH TEXTO", 10, True, FRZ_T),
             ("CONGELADO", 8.5, True, FRZ_E),
             ("t_j ∈ ℝ⁵¹²", 9.5, False, INK)],
            FRZ_F, FRZ_E)
    add_arrow(s, 8.60, 2.74, 0.36, 0.40, down=True)   # Φ_t -> clasificación

    # ============ RAMA VISUAL (fila principal): WSI -> Φ_v -> θ_v -> clasif ======
    add_box(s, 0.40, 3.15, 2.15, 1.25,
            [("WSI → N PARCHES", 10.5, True, INK),
             ("+ coordenadas (x , y)", 9, False, GREY_T)],
            TEAL_F, TEAL_E)
    add_arrow(s, 2.62, 3.56, 0.34, 0.32)
    add_box(s, 3.05, 3.15, 2.30, 1.25,
            [("Φ_v · CONCH VISIÓN", 10.5, True, FRZ_T),
             ("CONGELADO", 8.5, True, FRZ_E),
             ("v_i ∈ ℝ⁵¹²  (features .pt)", 9, False, INK)],
            FRZ_F, FRZ_E)
    add_arrow(s, 5.42, 3.56, 0.34, 0.32)
    add_box(s, 5.85, 3.15, 2.60, 1.25,
            [("θ_v · AGREGACIÓN ESPACIAL", 10, True, ORA_E),
             ("grilla 2D · conv 3/5/7 + transformer", 7.5, False, GREY_T),
             ("→ vector refinado por parche", 8.5, False, INK)],
            ORA_F, ORA_E, lw=2)
    add_arrow(s, 8.52, 3.56, 0.34, 0.32)
    add_box(s, 8.95, 3.15, 2.60, 1.25,
            [("CLASIFICACIÓN POR PARCHE", 10, True, INK),
             ("p(clase | parche) =", 8.5, False, GREY_T),
             ("softmax( cos(t_j , ṽ) / τ )", 8.5, False, GREY_T)],
            TEAL_F, TEAL_E)

    # ============ SALIDA (abajo-derecha) ============
    add_arrow(s, 10.07, 4.50, 0.36, 0.78, down=True)   # clasif -> salida
    add_box(s, 8.60, 5.35, 3.50, 1.25,
            [("AGREGACIÓN tumor-ratio", 10, True, INK),
             ("→ CLASE DE LA SLIDE", 9.5, True, INK),
             ("+ MAPA DE LOCALIZACIÓN", 9.5, True, TEAL_E)],
            TEAL_F, OUT_E, lw=2.25)

    # ============ caption (abajo-izquierda) ============
    cap = ("PathPT clasifica PARCHE por PARCHE usando el encoder de TEXTO de CONCH (Φ_t), "
           "que un MIL clásico como CLAM ignora. Reusa las features visuales Φ_v ya extraídas "
           "y entrena solo dos módulos chicos — θ_v (contexto espacial entre parches vecinos) "
           "y θ_t (prompts de clase) — con los encoders de CONCH congelados → apto para pocos "
           "datos. Da la clase de la slide y, además, un mapa de localización del hallazgo que "
           "CLAM no entrega.")
    cb = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                            Inches(0.40), Inches(5.35), Inches(7.95), Inches(1.25))
    cb.fill.solid(); cb.fill.fore_color.rgb = RGBColor(0xF7, 0xF8, 0xFA)
    cb.line.color.rgb = RGBColor(0xC9, 0xCD, 0xD2); cb.line.width = Pt(1)
    cb.shadow.inherit = False
    set_text(cb, [(cap, 10.5, False, RGBColor(0x33, 0x33, 0x33))], align=PP_ALIGN.LEFT)
    return s


def main():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    build(prs)
    prs.save(DST)
    chk = Presentation(DST)
    sh = chk.slides[0].shapes
    has_pathpt = any(x.has_text_frame and "POR PARCHE" in x.text for x in sh)
    print(f"OK  {os.path.relpath(DST, REPO)}  slides={len(chk.slides)}  "
          f"shapes={len(sh)}  clasif_por_parche={has_pathpt}")


if __name__ == "__main__":
    main()
