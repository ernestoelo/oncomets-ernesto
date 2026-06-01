#!/usr/bin/env python
"""generate_dsmil_diagram.py — ecuaciones DSMIL bonitas como PNG insertables.

Renderiza las fórmulas del diagrama "DSMIL en cascada" (y un par de extras)
como PNG con FONDO BLANCO opaco y matplotlib **mathtext** (fontset 'cm', estilo
LaTeX, sin necesidad de instalar LaTeX). Cada PNG es UNA ecuación, recortada al
texto (bbox tight) → se arrastra encima de la caja correspondiente en OnlyOffice,
reemplazando el monospace plano que se veía feo.

Fondo BLANCO (no transparente) a propósito: los visores/thumbnails pintan la
transparencia de NEGRO y el texto gris oscuro quedaba negro-sobre-negro
(invisible). Como las cajas de la cascada son blancas, el fondo blanco blanquea
limpio sobre ellas. Si alguna vez se necesita transparente, poner TRANSPARENT=True.

Por qué mathtext y no mermaid: mermaid escupe texto plano (subíndices falsos,
'<>' en vez de '⟨⟩', 'Σ_k' sin barra de fracción). mathtext da subíndices
reales, ⟨·⟩, √, Σ y fracciones bien tipografiadas. (CLAUDE.md → "math bonito =
mathtext, no mermaid".)

Fórmulas validadas contra:
  - DSMIL: `DSMIL_official_reference/dsmil.py:44,55-57` y paper Li et al. 2021.
    Mapeo en `objetivo_3_modulo_mil_alternativo/investigacion/03_comparacion_clam_dsmil.md` §3.
    CLAVE: la atención lleva escalado /√d_q (d_q=128, dim de la proyección q),
    que la slide de cascada original OMITÍA.
  - CLAM: `clam_environ/models/model_clam.py:41-64` (Attn_Net_Gated).
  - Loss compuesta (nuestra impl., w_max añadido): `diagrama_dsmil.md` §1.
Notación U(h_i,h_m) = atención (≡ β_i en la fuente canónica). Se usa U para ser
consistente con las 2 slides DSMIL de Ernesto (notación + cascada).

Salida: sprints/B4_sprint4/objetivo_5_fusion_binaria/figuras/slide_assets/D##_*.png
Uso:    PY=/home/sdonoso/miniconda3/envs/clam_latest/bin/python
        $PY scripts/generate_dsmil_diagram.py
"""
import os
import textwrap
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

# -- Config mathtext: fontset 'cm' = look LaTeX clásico, sin usetex --
matplotlib.rcParams["mathtext.fontset"] = "cm"
matplotlib.rcParams["mathtext.rm"] = "serif"
matplotlib.rcParams["font.family"] = "DejaVu Sans"   # texto NO-math (títulos/desc)

REPO = "/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto"
OUT = os.path.join(REPO, "sprints/B4_sprint4/objetivo_5_fusion_binaria/figuras/slide_assets")
os.makedirs(OUT, exist_ok=True)

COL_NEGRO = "#222222"   # texto de ecuación (cae sobre cajas crema/blancas)
COL_BG = "white"        # fondo opaco (ver docstring: transparente salía negro)
TRANSPARENT = False     # True solo si la caja destino NO es blanca
DPI = 220
FONTSIZE = 36

# Paleta Environ (espejo del deck) para el diagrama completo
COL_TEAL = "#2C7A8C"     # títulos de caja
COL_GRIS_TXT = "#555555" # descripciones
COL_BORDER = "#CFD4D8"   # borde de caja
COL_ORANGE = "#E2723B"   # conectores + badges de nodo (estilo cascada de Ernesto)
COL_SHADOW = "#E6E8EA"   # sombra sutil
COL_BADGE_FILL = "#FCEAD6"

# (filename, mathtext, descripción para el log)  — orden = nodos de la cascada
EQUATIONS = [
    ("D01_raiz_mil",
     r"$c(B) = g\left(f(x_0),\ \ldots,\ f(x_N)\right)$",
     "Raiz (nodo 2): MIL general"),
    ("D02_stream1_critica",
     r"$c_m(B) = \max_i\ W_0\, h_i$",
     "Stream 1 (nodo 3): instancia critica / max-pool"),
    ("D03_proyecciones",
     r"$q_i = W_q\, h_i \qquad v_i = W_v\, h_i$",
     "Proyecciones (nodo 4): q compara, v aporta"),
    ("D04_atencion_anclada",
     r"$U(h_i, h_m) = \mathrm{softmax}\left(\langle q_i, q_m\rangle / \sqrt{d_q}\right)$",
     "Atencion anclada (nodo 5): softmax ESCALADO /sqrt(d_q), d_q=128"),
    ("D05_bag_embedding",
     r"$b = \sum_i U(h_i, h_m)\, v_i$",
     "Bag embedding (nodo 6): suma ponderada"),
    ("D06_fusion_final",
     r"$c(B) = \frac{1}{2}\left(W_0\, h_m + W_b\, b\right)$",
     "Fusion final (nodo 8): promedio critico + bolsa"),
    # --- Extras (no estan en la slide de cascada; por si los querES) ---
    ("D07_clam_atencion_absoluta",
     r"$A_i = W_c\left(\tanh(W_a\, h_i)\ \odot\ \sigma(W_b\, h_i)\right)$",
     "EXTRA: atencion ABSOLUTA de CLAM (para comparar vs DSMIL)"),
    ("D08_loss_compuesta",
     r"$\mathcal{L} = 0.7\,\mathcal{L}_{\mathrm{bag}} + 0.3\,\mathcal{L}_{\mathrm{inst}}"
     r" + 0.1\,\mathcal{L}_{\mathrm{max}}$",
     "EXTRA: loss compuesta (nuestra impl., w_max=0.1 anadido)"),
]


def render_equation(fname, mathtext, color=COL_NEGRO):
    """Renderiza UNA ecuación mathtext a PNG (fondo blanco) recortado al texto.

    Correcto-por-construcción: bbox_inches='tight' garantiza cero clipping; el
    facecolor blanco opaco evita el problema de "transparencia = negro" en los
    visores. Si el mathtext no parsea, savefig lanza excepción y la capturamos
    arriba (no se traga errores).
    """
    fig = plt.figure(figsize=(0.1, 0.1), dpi=DPI)
    fig.patch.set_facecolor(COL_BG)
    fig.text(0.5, 0.5, mathtext, fontsize=FONTSIZE, color=color,
             ha="center", va="center")
    path = os.path.join(OUT, fname + ".png")
    fig.savefig(path, dpi=DPI, facecolor=COL_BG, transparent=TRANSPARENT,
                bbox_inches="tight", pad_inches=0.12)
    plt.close(fig)
    return path


# =============================================================================
# Diagrama COMPLETO (árbol en cascada en UNA sola imagen)
# =============================================================================

FIG_W, FIG_H = 12.6, 7.0   # pulgadas; layout en coords 0-100

# (key, num_nodo, título, ecuación mathtext, descripción, cx, cy, w, h)
CASCADE_BOXES = [
    ("raiz", 2, "RAÍZ",
     r"$c(B)=g\left(f(x_0),\ \ldots,\ f(x_N)\right)$",
     "MIL general: un bag se obtiene agregando embeddings o scores de instancias.",
     50, 90, 46, 14),
    ("stream1", 3, "STREAM 1 · INSTANCIA CRÍTICA",
     r"$c_m(B)=\max_i\ W_0\,h_i$",
     "Encuentra el parche más sospechoso; este nodo guía toda la rama derecha.",
     24, 63, 40, 15),
    ("proy", 4, "PROYECCIONES Y ATENCIÓN",
     r"$q_i=W_q\,h_i \qquad v_i=W_v\,h_i$",
     "Se proyectan embeddings para medir similitud y preparar la suma ponderada.",
     73, 63, 44, 15),
    ("aten", 5, "ATENCIÓN ANCLADA",
     r"$U(h_i,h_m)=\mathrm{softmax}\left(\langle q_i,q_m\rangle/\sqrt{d_q}\right)$",
     "Softmax respecto a la instancia crítica: las instancias similares reciben más peso.",
     44, 36, 40, 18),
    ("bag", 6, "BAG EMBEDDING",
     r"$b=\sum_i U(h_i,h_m)\,v_i$",
     "Suma ponderada de información de toda la bolsa.",
     82, 36, 32, 18),
    ("fusion", 8, "FUSIÓN FINAL",
     r"$c(B)=\frac{1}{2}\left(W_0\,h_m + W_b\,b\right)$",
     "Promedia evidencia local y global para la decisión final.",
     66, 12, 42, 15),
]

# (padre, hijo, etiqueta mathtext o None)
CASCADE_EDGES = [
    ("raiz", "stream1", r"$f(x_i)\rightarrow h_i$"),
    ("raiz", "proy", r"$h_i\rightarrow q_i,v_i$"),
    ("proy", "aten", None),
    ("proy", "bag", None),
    ("bag", "fusion", None),
]


def _fit_fontsize(mathtext, max_width_in, base_fs=20.0, min_fs=11.0):
    """Mayor fontsize <= base que hace caber la ecuación en max_width_in.

    Mide el ancho real del mathtext (Text artist sobre canvas Agg) → garantiza
    por construcción que la ecuación NO se desborda de su caja.
    """
    fig_tmp = plt.figure(dpi=DPI)
    r = fig_tmp.canvas.get_renderer()
    t = fig_tmp.text(0, 0, mathtext, fontsize=base_fs)
    w_in = t.get_window_extent(r).width / DPI
    plt.close(fig_tmp)
    if w_in <= max_width_in:
        return base_fs
    return max(min_fs, base_fs * max_width_in / w_in)


def render_full_cascade(fname="D09_cascada_completo"):
    """Dibuja el árbol DSMIL completo (cajas + conectores + ecuaciones) en 1 PNG."""
    boxes = {b[0]: b for b in CASCADE_BOXES}
    fig = plt.figure(figsize=(FIG_W, FIG_H), dpi=DPI)
    fig.patch.set_facecolor(COL_BG)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100)
    ax.set_ylim(-1, 100)
    ax.axis("off")

    def top(b):    return b[6] + b[7] / 2.0
    def bottom(b): return b[6] - b[7] / 2.0

    # bus horizontal por padre: a media altura entre el padre y su hijo más alto
    children = defaultdict(list)
    for par, ch, _ in CASCADE_EDGES:
        children[par].append(ch)
    bus_y = {par: (bottom(boxes[par]) + max(top(boxes[ch]) for ch in chs)) / 2.0
             for par, chs in children.items()}

    # -- Conectores ortogonales (codo) con punta de flecha hacia el hijo --
    for parent, child, label in CASCADE_EDGES:
        p, c = boxes[parent], boxes[child]
        px, py = p[5], bottom(p)     # padre: centro del borde inferior
        cx_, ct = c[5], top(c)       # hijo: centro del borde superior
        by = bus_y[parent]
        # codo en 3 segmentos (zorder 4 => ENCIMA de las cajas, así se ve completo):
        # 1) caída del padre  2) bus horizontal  3) bajada al hijo + punta ▼.
        tip = ct + 1.0   # centro de la punta, casi tocando el tope del hijo
        ax.plot([px, px], [py, by], color=COL_ORANGE, lw=2.4, zorder=4,
                solid_capstyle="round")
        ax.plot([px, cx_], [by, by], color=COL_ORANGE, lw=2.4, zorder=4,
                solid_capstyle="round")
        ax.plot([cx_, cx_], [by, tip], color=COL_ORANGE, lw=2.4, zorder=4,
                solid_capstyle="round")
        # punta de flecha hacia ABAJO (triángulo ▼) entrando al hijo
        ax.plot(cx_, tip, marker="v", markersize=14, color=COL_ORANGE,
                markeredgecolor=COL_ORANGE, zorder=4)
        if label:
            ax.text((px + cx_) / 2.0, by + 1.6, label, fontsize=11.5,
                    color=COL_GRIS_TXT, ha="center", va="center", zorder=6,
                    bbox=dict(boxstyle="round,pad=0.2", facecolor="white",
                              edgecolor="none"))

    # -- Cajas --
    for key, num, title, eq, desc, cx, cy, w, h in CASCADE_BOXES:
        x0, y0 = cx - w / 2.0, cy - h / 2.0
        # sombra sutil (detrás de todo)
        ax.add_patch(FancyBboxPatch(
            (x0 + 0.5, y0 - 0.7), w, h,
            boxstyle="round,pad=0,rounding_size=1.8",
            linewidth=0, facecolor=COL_SHADOW, zorder=1))
        # caja (debajo de los conectores: zorder 2 < 4)
        ax.add_patch(FancyBboxPatch(
            (x0, y0), w, h,
            boxstyle="round,pad=0,rounding_size=1.8",
            linewidth=1.3, edgecolor=COL_BORDER, facecolor="white", zorder=2))
        # título (teal, arriba) — zorder 5 (encima de conectores)
        ax.text(cx, cy + h / 2.0 - 2.1, title, fontsize=11.5, color=COL_TEAL,
                ha="center", va="top", fontweight="bold", zorder=5)
        # ecuación (auto-fit al ancho de la caja, tamaño parejo entre cajas)
        max_w_in = (w / 100.0) * FIG_W - 0.7
        fs = _fit_fontsize(eq, max_w_in, base_fs=20.0, min_fs=17.0)
        ax.text(cx, cy, eq, fontsize=fs, color=COL_NEGRO,
                ha="center", va="center", zorder=5)
        # descripción (gris, abajo, wrap)
        wrapped = textwrap.fill(desc, width=max(26, int(w * 1.15)))
        ax.text(cx, cy - h / 2.0 + 1.6, wrapped, fontsize=9.3, color=COL_GRIS_TXT,
                ha="center", va="bottom", zorder=5)
        # badge de nodo: esquina sup-derecha, por FUERA del borde (no pisa título)
        bx, by = cx + w / 2.0 - 1.4, cy + h / 2.0 + 0.8
        ax.plot(bx, by, marker="o", markersize=19, color=COL_BADGE_FILL,
                markeredgecolor=COL_ORANGE, markeredgewidth=1.4, zorder=6)
        ax.text(bx, by, str(num), fontsize=10.5, color=COL_ORANGE,
                ha="center", va="center", fontweight="bold", zorder=7)

    path = os.path.join(OUT, fname + ".png")
    fig.savefig(path, dpi=DPI, facecolor=COL_BG, transparent=TRANSPARENT,
                bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)
    return path


def main():
    from PIL import Image
    print(f"Salida: {OUT}\n")
    ok, fail = 0, 0
    for fname, mathtext, desc in EQUATIONS:
        try:
            path = render_equation(fname, mathtext)
            im = Image.open(path).convert("RGB")
            w, h = im.size
            corner = im.getpixel((0, 0))  # esquina = fondo; debe ser blanco
            bg = "blanco" if corner == (255, 255, 255) else f"NO-BLANCO {corner}"
            print(f"  OK   {fname:30s} {w:4d}x{h:<4d}px  fondo={bg}  · {desc}")
            ok += 1
        except Exception as e:  # noqa: BLE001 — queremos ver CUÁL falló
            print(f"  FAIL {fname:30s} · {desc}\n       -> {type(e).__name__}: {e}")
            fail += 1

    # -- Diagrama completo (árbol en cascada) --
    try:
        path = render_full_cascade()
        im = Image.open(path).convert("RGB")
        w, h = im.size
        corner = im.getpixel((0, 0))
        bg = "blanco" if corner == (255, 255, 255) else f"NO-BLANCO {corner}"
        print(f"  OK   {'D09_cascada_completo':30s} {w:4d}x{h:<4d}px  fondo={bg}"
              f"  · DIAGRAMA COMPLETO (árbol)")
        ok += 1
    except Exception as e:  # noqa: BLE001
        print(f"  FAIL D09_cascada_completo\n       -> {type(e).__name__}: {e}")
        fail += 1

    print(f"\n{ok} OK, {fail} FAIL.")
    if fail:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
