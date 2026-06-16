#!/usr/bin/env python
"""generate_cbir_clam_diagram.py — CLAM_MB + rama CBIR integrada (PNG insertable).

Toma el diagrama CLAM_MB de Ernesto (input→CONCH→FC→atención→pooling→clasificador
+ rama instancia) a ALTITUD DE BLOQUE y le añade la rama de RETRIEVAL CBIR como
rama HERMANA que comparte el backbone CONCH y corre en paralelo (NO se inserta en
el forward de CLAM — eso sería la variante A, descartada = "mammoth #2",
`sprints/B5_sprint5/investigacion_retrieval/analisis.md` §3.A).

Dos puntos de derivación (tap) para el vector de slide que alimenta el índice:
  - MVP (sólido, naranjo): mean-pool de las features CONCH crudas (Z).
  - Opción fuerte (punteado): reusar h_slide ya attention-pooled por CLAM
    ("el retrieval reusa lo que CLAM aprendió a mirar").

Estilo = receta `scripts/generate_dsmil_diagram.py` (mathtext fontset 'cm', fondo
BLANCO opaco, conectores ortogonales con punta ▼ POR ENCIMA de las cajas, DPI 220).
math anclado al diagrama de Ernesto + `models/model_clam.py` (CLAM_MB).

Salida: sprints/B5_sprint5/investigacion_retrieval/figuras/D10_clam_cbir_integrado.png
Uso:    PY=/home/sdonoso/miniconda3/envs/clam_latest/bin/python
        $PY scripts/generate_cbir_clam_diagram.py
"""
import os
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

matplotlib.rcParams["mathtext.fontset"] = "cm"
matplotlib.rcParams["mathtext.rm"] = "serif"
matplotlib.rcParams["font.family"] = "DejaVu Sans"

REPO = "/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto"
OUT = os.path.join(REPO, "sprints/B5_sprint5/investigacion_retrieval/figuras")
os.makedirs(OUT, exist_ok=True)

DPI = 220
COL_BG = "white"
COL_NEGRO = "#222222"
COL_GRIS = "#555555"
COL_SHADOW = "#E6E8EA"

# Paletas por tipo de nodo
STYLE = {
    # kind:      (fill,      border,    title_color)
    "shared":    ("#CFE2F3", "#2C7A8C", "#1F4E5F"),  # backbone compartido (teal)
    "clam":      ("#EAF2FB", "#5B8FB9", "#2C5F84"),  # CLAM existente (azul)
    "instance":  ("#EEF3F8", "#9DB8CC", "#5A7A92"),  # rama instancia (azul tenue)
    "cbir":      ("#FCE5CD", "#E2723B", "#9C4A12"),  # CBIR NUEVO (naranjo)
}
COL_CLAM_EDGE = "#5B8FB9"
COL_CBIR_EDGE = "#E2723B"

FIG_W, FIG_H = 16.5, 11.0

# (key, kind, title, eq_mathtext, desc, cx, cy, w, h)
BOXES = [
    # -------- spine compartido + CLAM (izquierda, cx≈31) --------
    ("input", "clam", "ENTRADA · N parches",
     r"$k \in \mathbb{R}^{N \times 256 \times 256 \times 3}$",
     "N parches de la WSI", 31, 95, 30, 7),
    ("conch", "shared", "EXTRACTOR CONCH   ·   BACKBONE COMPARTIDO",
     r"$Z \in \mathbb{R}^{N \times 512}$",
     "Foundation model congelado. Lo comparten CLAM y CBIR.", 31, 83, 38, 10),
    ("fc", "clam", "FULLY CONNECTED",
     r"$H = \mathrm{ReLU}(Z\,W_1^{T}) \in \mathbb{R}^{N \times 512}$",
     "proyección por parche", 31, 68, 30, 11),
    ("atten", "clam", "ATENCIÓN (gated, por rama m)",
     r"$a_m \in \mathbb{R}^{N \times 1},\quad \sum_j a_{m}=1$",
     r"$\tanh \odot$ sigmoid; pesa los N parches", 31, 53, 30, 11),
    ("pool", "clam", "ATTENTION POOLING",
     r"$h_{slide,m} = a_m^{T} H \in \mathbb{R}^{512}$",
     "1 vector de slide por clase", 31, 38, 30, 11),
    ("clf", "clam", "CLASIFICADOR + SOFTMAX",
     r"$\mathrm{logit}_m = h_{slide,m} W_m^{T};\ \ \hat{y}=\mathrm{arg\,max}_m\, p_m$",
     "salida CLAM: la etiqueta de la slide", 31, 21, 30, 12),
    # rama instancia (compacta, izquierda)
    ("inst", "instance", "RAMA INSTANCIA",
     r"$\mathcal{L}_{inst}$ SmoothTop1SVM",
     "top-B / bottom-B; solo entrenamiento", 8.5, 53, 14, 13),
    # -------- rama CBIR NUEVA (derecha, cx≈74) --------
    ("svec", "cbir", "VECTOR DE SLIDE",
     r"$v = \frac{1}{N}\sum_i Z_i \in \mathbb{R}^{512}$",
     "MVP: mean-pool de Z  ·  fuerte: reusar $h_{slide}$", 74, 68, 34, 12),
    ("l2", "cbir", "L2-NORMALIZE",
     r"$\hat{v} = v\, /\, \|v\|_2$",
     "deja la similitud = coseno", 74, 53, 34, 10),
    ("index", "cbir", "ÍNDICE COSENO  ·  galería ~3000 slides",
     r"$\mathrm{sim}(q,g) = \hat{v}_q \cdot \hat{v}_g^{T}$",
     "la 'biblioteca' de casos (CONCH ya calculado)", 74, 38, 34, 12),
    ("knn", "cbir", "kNN  ·  CASOS SIMILARES",
     r"$k \in \{1,3,5\}\ \rightarrow\ \mathrm{voto\ mayoritario}$",
     "top-k slides parecidas + sus diagnósticos", 74, 21, 34, 13),
]
BOX = {b[0]: b for b in BOXES}


def _cx(b): return b[5]
def _cy(b): return b[6]
def _w(b):  return b[7]
def _h(b):  return b[8]
def top(b):    return _cy(b) + _h(b) / 2.0
def bottom(b): return _cy(b) - _h(b) / 2.0
def left(b):   return _cx(b) - _w(b) / 2.0
def right(b):  return _cx(b) + _w(b) / 2.0


def _fit_fontsize(ax, mathtext, max_width_in, base_fs=17.0, min_fs=11.0):
    """Mayor fontsize <= base que cabe en max_width_in (mide el Text real)."""
    fig_tmp = plt.figure(dpi=DPI)
    r = fig_tmp.canvas.get_renderer()
    t = fig_tmp.text(0, 0, mathtext, fontsize=base_fs)
    w_in = t.get_window_extent(r).width / DPI
    plt.close(fig_tmp)
    if w_in <= max_width_in:
        return base_fs
    return max(min_fs, base_fs * max_width_in / w_in)


def connector(ax, pts, color, lw=2.6, dashed=False, tip=True, zorder=4):
    style = (0, (6, 4)) if dashed else "solid"
    for i in range(len(pts) - 1):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        ax.plot([x0, x1], [y0, y1], color=color, lw=lw, zorder=zorder,
                solid_capstyle="round", linestyle=style)
    if tip:
        (x0, y0), (x1, y1) = pts[-2], pts[-1]
        if abs(x1 - x0) >= abs(y1 - y0):
            m = ">" if x1 > x0 else "<"
        else:
            m = "v" if y1 < y0 else "^"
        ax.plot(x1, y1, marker=m, markersize=13, color=color,
                markeredgecolor=color, zorder=zorder + 1)


def draw_box(ax, b):
    key, kind, title, eq, desc, cx, cy, w, h = b
    fill, border, tcol = STYLE[kind]
    x0, y0 = cx - w / 2.0, cy - h / 2.0
    # sombra
    ax.add_patch(FancyBboxPatch((x0 + 0.4, y0 - 0.6), w, h,
                 boxstyle="round,pad=0,rounding_size=1.6", linewidth=0,
                 facecolor=COL_SHADOW, zorder=1))
    # caja
    lw = 2.4 if kind in ("shared", "cbir") else 1.5
    ax.add_patch(FancyBboxPatch((x0, y0), w, h,
                 boxstyle="round,pad=0,rounding_size=1.6", linewidth=lw,
                 edgecolor=border, facecolor=fill, zorder=2))
    # título
    ax.text(cx, top(b) - 1.9, title, fontsize=10.2, color=tcol,
            ha="center", va="top", fontweight="bold", zorder=5)
    # ecuación (auto-fit)
    max_w_in = (w / 100.0) * FIG_W - 0.5
    fs = _fit_fontsize(ax, eq, max_w_in, base_fs=16.0, min_fs=10.0)
    ax.text(cx, cy + 0.3, eq, fontsize=fs, color=COL_NEGRO,
            ha="center", va="center", zorder=5)
    # descripción
    wrapped = textwrap.fill(desc, width=max(24, int(w * 1.25)))
    ax.text(cx, bottom(b) + 1.3, wrapped, fontsize=8.6, color=COL_GRIS,
            ha="center", va="bottom", zorder=5)


def render():
    fig = plt.figure(figsize=(FIG_W, FIG_H), dpi=DPI)
    fig.patch.set_facecolor(COL_BG)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    # ---- conectores CLAM (spine azul) ----
    spine = ["input", "conch", "fc", "atten", "pool", "clf"]
    for a, c in zip(spine[:-1], spine[1:]):
        pa, pc = BOX[a], BOX[c]
        connector(ax, [(_cx(pa), bottom(pa)), (_cx(pc), top(pc) + 0.8)],
                  COL_CLAM_EDGE)
    # atención -> rama instancia (izquierda)
    pa, pc = BOX["atten"], BOX["inst"]
    connector(ax, [(left(pa), _cy(pa)), (right(pc) + 0.8, _cy(pc))],
              STYLE["instance"][1])

    # ---- conectores CBIR (spine naranjo) ----
    cbir = ["svec", "l2", "index", "knn"]
    for a, c in zip(cbir[:-1], cbir[1:]):
        pa, pc = BOX[a], BOX[c]
        connector(ax, [(_cx(pa), bottom(pa)), (_cx(pc), top(pc) + 0.8)],
                  COL_CBIR_EDGE)

    # ---- TAP 1: CONCH -> VECTOR DE SLIDE (mean-pool, MVP, sólido) ----
    pconch, psvec = BOX["conch"], BOX["svec"]
    connector(ax, [(right(pconch), _cy(pconch)),
                   (_cx(psvec), _cy(pconch)),
                   (_cx(psvec), top(psvec) + 0.8)], COL_CBIR_EDGE)
    ax.text(60, _cy(pconch) + 2.4, "mean-pool de Z  (MVP)", fontsize=9.5,
            color=COL_CBIR_EDGE, ha="center", va="center", fontweight="bold",
            zorder=6, bbox=dict(boxstyle="round,pad=0.2", facecolor="white",
                                edgecolor="none"))

    # ---- TAP 2: POOLING (h_slide) -> VECTOR DE SLIDE (opción fuerte, punteado) ----
    ppool = BOX["pool"]
    xmid = 51.0
    connector(ax, [(right(ppool), _cy(ppool)),
                   (xmid, _cy(ppool)),
                   (xmid, _cy(psvec)),
                   (left(psvec), _cy(psvec))], COL_CBIR_EDGE, dashed=True)
    ax.text(xmid, 60.0, "opción fuerte:\nreusar $h_{slide}$\n(lo que CLAM\naprendió a mirar)",
            fontsize=8.8, color=COL_CBIR_EDGE, ha="center", va="center",
            zorder=6, bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                                edgecolor=COL_CBIR_EDGE, linewidth=0.8))

    # ---- cajas ----
    for b in BOXES:
        draw_box(ax, b)

    # ---- leyenda (arriba-izquierda) ----
    leg = [("shared", "Backbone compartido (CONCH)"),
           ("clam", "CLAM · clasificación (existente)"),
           ("cbir", "CBIR · retrieval (NUEVO)")]
    lx, ly = 2.5, 97.0
    for i, (kind, lab) in enumerate(leg):
        fill, border, _ = STYLE[kind]
        yy = ly - i * 3.0
        ax.add_patch(FancyBboxPatch((lx, yy - 1.0), 3.0, 2.0,
                     boxstyle="round,pad=0,rounding_size=0.4", linewidth=1.6,
                     edgecolor=border, facecolor=fill, zorder=6))
        ax.text(lx + 4.0, yy, lab, fontsize=9.2, color=COL_NEGRO,
                ha="left", va="center", zorder=6)

    # ---- caption (franja inferior con el mensaje clave / surface-premise) ----
    cap = ("CBIR NO se inserta dentro del forward de CLAM (eso sería la variante A "
           "— agregador-retrieval — descartada). Comparte el backbone CONCH y corre "
           "como rama paralela: indexar + buscar, sin entrenar (CPU). El retrieval es "
           "una herramienta de apoyo por casos similares, no un clasificador clínico-grado.")
    ax.add_patch(FancyBboxPatch((3, 2.2), 94, 6.6,
                 boxstyle="round,pad=0,rounding_size=1.0", linewidth=1.2,
                 edgecolor="#C9CDD2", facecolor="#F7F8FA", zorder=2))
    ax.text(50, 5.5, textwrap.fill(cap, width=118), fontsize=9.4,
            color="#333333", ha="center", va="center", zorder=5)

    path = os.path.join(OUT, "D10_clam_cbir_integrado.png")
    fig.savefig(path, dpi=DPI, facecolor=COL_BG, bbox_inches="tight",
                pad_inches=0.18)
    plt.close(fig)
    return path


if __name__ == "__main__":
    from PIL import Image
    try:
        p = render()
        im = Image.open(p).convert("RGB")
        w, h = im.size
        corner = im.getpixel((0, 0))
        bg = "blanco" if corner == (255, 255, 255) else f"NO-BLANCO {corner}"
        print(f"OK  {os.path.relpath(p, REPO)}  {w}x{h}px  fondo={bg}")
    except Exception as e:  # noqa: BLE001
        print(f"FAIL  {type(e).__name__}: {e}")
        raise
