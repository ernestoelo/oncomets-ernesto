#!/usr/bin/env python
"""generate_b5_extra_assets.py — assets PNG insertables que faltaban para el deck B5.

Reusa render_table de scripts/generate_slide_assets.py (DPI 220, auto-dimensión de
columnas, paleta Environ). Añade un renderer de confusión NxN (3x3) para mostrar el
colapso de PathPT en mitotic. Convención (Benjamín): SIN números de job, SIN nombres.

Genera:
  T20_pathpt_mitotic_paired.png   — PathPT vs CLAM, mitotic 3-clase ordinal (paired k=5)
  M20_mitotic_confusion_clam.png  — confusión 3x3 CLAM (usa las 3 clases)
  M21_mitotic_confusion_pathpt.png— confusión 3x3 PathPT (colapso a score_1)
  T21_pathpt_microcalc_gonogo.png — go/no-go zero-shot microcalc (3 binarias) -> NO-GO
  T30_tres_ejes_cierre.png        — 3 ejes de arquitectura probados -> 0 palancas

Verdad de campo:
  - mitotic: sprints/B5_sprint5/pathpt/resultados_mitotic.md
  - microcalc: results/pathpt_gonogo/microcalc_*_v*_zeroshot_metrics.json (top-100)
  - cierre: Hallazgos 11/12/13 de CLAUDE.md

Uso: PYTHONPATH=/media/administrador/Storage1/sdonoso/clam_testing2/.pylibs \
     /home/sdonoso/miniconda3/envs/clam_latest/bin/python scripts/generate_b5_extra_assets.py
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from generate_slide_assets import (  # noqa: E402
    render_table, COL_VERDE, COL_ROJO, COL_AMBAR, COL_GRIS_TXT,
    COL_TEAL_DK, COL_NEGRO, COL_GRIS, DPI,
)

REPO = os.path.abspath(os.path.join(HERE, ".."))
OUT_PATHPT = os.path.join(REPO, "sprints/B5_sprint5/pathpt/figuras/slide_assets")
OUT_CIERRE = os.path.join(REPO, "sprints/B5_sprint5/investigacion_que_integrar/figuras")
os.makedirs(OUT_PATHPT, exist_ok=True)
os.makedirs(OUT_CIERRE, exist_ok=True)

COL_MED = "#DCEAEE"


def _sgn(x):
    return f"+{x:.3f}" if x > 0 else (f"−{abs(x):.3f}" if x < 0 else "+0.000")


# ============================================================================
# Confusión 3x3 (renderer propio — el del helper es 2x2)
# ============================================================================

def render_confusion_3x3(conf, out_path, classes, title=None, n_label=None,
                         fontsize=12):
    """Heatmap 3x3 con conteo + % por fila (recall) y recall por clase abajo."""
    conf = np.asarray(conf, dtype=int)
    total = conf.sum()
    recalls = [conf[i, i] / conf[i].sum() if conf[i].sum() else 0 for i in range(3)]
    bal = float(np.mean(recalls))

    fig, ax = plt.subplots(figsize=(5.6, 4.9), dpi=DPI)
    vmax = conf.max() or 1
    ax.imshow(conf, cmap="Blues", vmin=0, vmax=vmax)
    for r in range(3):
        for c in range(3):
            v = conf[r, c]
            color = "white" if v > vmax * 0.55 else COL_NEGRO
            ax.text(c, r, f"{v}", ha="center", va="center",
                    fontsize=fontsize + 1, color=color, weight="bold")
    ax.set_xticks(range(3)); ax.set_xticklabels([f"pred\n{c}" for c in classes],
                                                fontsize=fontsize - 2)
    ax.set_yticks(range(3)); ax.set_yticklabels([f"true {c}" for c in classes],
                                                fontsize=fontsize - 2)
    rec_txt = "   ·   ".join(f"recall {classes[i]}={recalls[i]:.2f}" for i in range(3))
    sub = f"bal_acc = {bal:.3f}\n{rec_txt}"
    if n_label is not None:
        sub = f"n = {n_label}   ·   " + sub
    ax.set_xlabel(sub, fontsize=fontsize - 3, color=COL_GRIS_TXT, labelpad=10)
    if title:
        ax.set_title(title, fontsize=fontsize + 1, color=COL_TEAL_DK,
                     weight="bold", pad=12)
    fig.tight_layout()
    fig.savefig(out_path, dpi=DPI, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  → {os.path.basename(out_path)}")


# ============================================================================
# PathPT mitotic (3 clases ordinales) — paired + confusiones (colapso)
# ============================================================================

# fold: (clam_auc, clam_bal, pathpt_auc, pathpt_bal)  — resultados_mitotic.md §2
MIT_FOLDS = [
    (0, 0.765, 0.506, 0.662, 0.333),
    (1, 0.698, 0.504, 0.566, 0.333),
    (2, 0.684, 0.461, 0.687, 0.333),
    (3, 0.710, 0.435, 0.714, 0.333),
    (4, 0.764, 0.563, 0.681, 0.333),
]
MIT_MEAN = (0.724, 0.494, 0.662, 0.333)
MIT_D_AUC = (-0.062, 0.062)
MIT_D_BAL = (-0.160, 0.049)
MIT_CONF_CLAM = [[231, 53, 36], [77, 27, 38], [26, 28, 72]]
MIT_CONF_PATHPT = [[320, 0, 0], [142, 0, 0], [126, 0, 0]]
MIT_N = 588


def asset_mitotic_paired():
    headers = ["Fold", "CLAM\nAUC / bal_acc", "PathPT\nAUC / bal_acc", "Δ AUC", "Δ bal_acc"]
    rows, cell_colors, row_colors = [], {}, []
    for i, (f, ca, cb, pa, pb) in enumerate(MIT_FOLDS):
        d_auc, d_bal = pa - ca, pb - cb
        rows.append([str(f), f"{ca:.3f} / {cb:.3f}",
                     f"{pa:.3f} / {pb:.3f}*", _sgn(d_auc), _sgn(d_bal)])
        cell_colors[(i, 4)] = {"fg": COL_ROJO, "bold": True}
        if d_auc < 0:
            cell_colors[(i, 3)] = {"fg": COL_ROJO, "bold": True}
        row_colors.append(COL_GRIS if i % 2 else "white")
    rows.append(["media", f"{MIT_MEAN[0]:.3f} / {MIT_MEAN[1]:.3f}",
                 f"{MIT_MEAN[2]:.3f} / {MIT_MEAN[3]:.3f}*",
                 f"−{abs(MIT_D_AUC[0]):.3f} ± {MIT_D_AUC[1]:.3f}",
                 f"−{abs(MIT_D_BAL[0]):.3f} ± {MIT_D_BAL[1]:.3f}"])
    row_colors.append(COL_MED)
    mi = len(rows) - 1
    cell_colors[(mi, 0)] = {"bold": True}
    cell_colors[(mi, 3)] = {"fg": COL_ROJO, "bold": True}
    cell_colors[(mi, 4)] = {"fg": COL_ROJO, "bold": True}
    render_table(
        headers, rows, os.path.join(OUT_PATHPT, "T20_pathpt_mitotic_paired.png"),
        row_colors=row_colors, cell_colors=cell_colors,
        title="PathPT vs CLAM — tasa mitótica (3 clases ordinales, pareada k=5)",
        footnote="* bal_acc = 0.333 EXACTO en los 5 folds = el trivial de 3 clases: "
                 "PathPT colapsa al argmax de la mayoritaria (score_1). El AUC sobrevive "
                 "(ranking latente) pero el operating point (argmax) es inusable.")


def asset_mitotic_confusions():
    cls = ("s1", "s2", "s3")
    render_confusion_3x3(
        MIT_CONF_CLAM, os.path.join(OUT_PATHPT, "M20_mitotic_confusion_clam.png"),
        cls, title="CLAM — mitótica (confusión 3×3, 5 folds)", n_label=MIT_N)
    render_confusion_3x3(
        MIT_CONF_PATHPT, os.path.join(OUT_PATHPT, "M21_mitotic_confusion_pathpt.png"),
        cls, title="PathPT — mitótica: COLAPSO a score_1 (5 folds)", n_label=MIT_N)


# ============================================================================
# PathPT microcalc go/no-go (zero-shot, CPU) -> NO-GO
# ============================================================================

def asset_microcalc_gonogo():
    headers = ["Tarea binaria (microcalc)", "n  (sí / no)", "AUC zero-shot\n(mejor prompt)",
               "vs azar (0.5)", "Veredicto"]
    rows = [
        ["en carcinoma invasivo", "68 / 260", "0.629", "leve", "NO-GO"],
        ["en CDIS",               "118 / 210", "0.533", "≈ azar", "NO-GO"],
        ["en tejido no neoplásico", "192 / 136", "0.444", "bajo azar", "NO-GO"],
    ]
    cell_colors = {
        (0, 4): {"fg": COL_AMBAR, "bold": True}, (0, 2): {"fg": COL_AMBAR, "bold": True},
        (1, 4): {"fg": COL_ROJO, "bold": True},  (1, 2): {"fg": COL_ROJO, "bold": True},
        (2, 4): {"fg": COL_ROJO, "bold": True},  (2, 2): {"fg": COL_ROJO, "bold": True},
    }
    render_table(
        headers, rows, os.path.join(OUT_PATHPT, "T21_pathpt_microcalc_gonogo.png"),
        cell_colors=cell_colors, fontsize=17,
        title="PathPT · microcalcificaciones — go/no-go zero-shot (CPU, sin GPU)",
        footnote="CONCH no «ve» microcalcificaciones zero-shot → pseudo-labels de parche basura. "
                 "Iterar prompts con más morfología EMPEORÓ (carcinoma v2 0.533 / v3 0.552 < v1 0.629). "
                 "El chequeo barato (CPU, ~min) descartó la tarea y ahorró ~18–24 h de GPU.")


# ============================================================================
# Cierre — 3 ejes de arquitectura probados -> 0 palancas
# ============================================================================

def asset_tres_ejes():
    headers = ["Eje atacado", "Modelo / mecanismo", "Tareas (pareadas, MC-CV)", "Resultado"]
    rows = [
        ["Agregador (cómo se\nfusionan los parches)", "DSMIL\n(dual-stream)",
         "microcalc binarias + fusionado", "0 palancas\n(CDIS regresión leve)"],
        ["Patch-embed (1ª capa\nde proyección)", "Mammoth\n(mixture-of-experts)",
         "8 tareas (microcalc, patrón,\ninvasión 3-clase)", "0 palancas\n(efecto gated por balance)"],
        ["Lenguaje + supervisión\ntile-level", "PathPT-CONCH\n(prompt-tuning + θ espacial)",
         "necrosis, mitótica, microcalc", "0 palancas\n(grounding zero-shot débil)"],
    ]
    cell_colors = {(i, 3): {"fg": COL_GRIS_TXT, "bold": True} for i in range(3)}
    render_table(
        headers, rows, os.path.join(OUT_CIERRE, "T30_tres_ejes_cierre.png"),
        cell_colors=cell_colors, fontsize=15,
        title="Tres ejes de arquitectura, triangulados → el cuello NO es el modelo",
        footnote="Tres familias independientes de cambio arquitectónico, todas con comparación pareada y "
                 "evaluación honesta (balanced_acc + AUC + matriz de confusión) → ninguna mueve la aguja. "
                 "El cuello de botella convergente es el DATO: desbalance, pocos positivos, contexto espacial.")


# ============================================================================
# Mammoth — figura conceptual (1 capa lineal -> MoE) para slide "qué es"
# ============================================================================

def asset_mammoth_concept():
    """Antes/después visual: CLAM 1 proyección lineal -> Mammoth mezcla de expertos."""
    from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
    TEAL = "#2C7A8C"; TEALF = "#D7E7EB"; ORA = "#E2723B"; ORAF = "#FCE5CD"
    BLU = "#5B8FB9"; BLUF = "#EAF2FB"; INKc = "#222222"; GT = "#555555"
    fig, ax = plt.subplots(figsize=(6.6, 5.2), dpi=DPI)
    ax.set_xlim(0, 10); ax.set_ylim(0, 8); ax.axis("off")

    def box(x, y, w, h, fc, ec, txt, fs=12, bold=True, tc=INKc):
        p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.04,rounding_size=0.12",
                           fc=fc, ec=ec, lw=2)
        ax.add_patch(p)
        ax.text(x + w / 2, y + h / 2, txt, ha="center", va="center",
                fontsize=fs, fontweight="bold" if bold else "normal", color=tc)

    def arrow(x1, y1, x2, y2, color="#8A8A8A"):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2),
                     arrowstyle="-|>", mutation_scale=18, lw=2.2, color=color))

    # --- Antes (CLAM) ---
    ax.text(2.4, 7.5, "CLAM (antes)", ha="center", fontsize=14, fontweight="bold", color=TEAL)
    box(1.4, 5.7, 2.0, 0.9, TEALF, TEAL, "feature\nz ∈ ℝ⁵¹²", fs=11)
    arrow(2.4, 5.65, 2.4, 5.05)
    box(0.9, 3.9, 3.0, 1.05, ORAF, ORA, "1 capa lineal\nH = ReLU(W·z)", fs=12, tc=ORA)
    arrow(2.4, 3.85, 2.4, 3.25)
    box(1.4, 2.3, 2.0, 0.9, TEALF, TEAL, "resto de\nCLAM", fs=11)
    ax.text(2.4, 1.6, "una sola proyección\npara todos los parches", ha="center",
            fontsize=9.5, color=GT, style="italic")

    # divisor
    ax.plot([5.0, 5.0], [1.2, 7.2], color="#CCCCCC", lw=1.2, ls="--")

    # --- Después (Mammoth) ---
    ax.text(7.6, 7.5, "MAMMOTH (después)", ha="center", fontsize=14, fontweight="bold", color=ORA)
    box(6.6, 5.7, 2.0, 0.9, TEALF, TEAL, "feature\nz ∈ ℝ⁵¹²", fs=11)
    box(6.55, 4.55, 2.1, 0.7, ORAF, ORA, "ROUTER g(z)", fs=11, tc=ORA)
    arrow(7.6, 5.65, 7.6, 5.3)
    # expertos
    for i, lab in enumerate(["E₁", "E₂", "E₃"]):
        bx = 5.6 + i * 1.45
        box(bx, 3.15, 1.2, 0.7, BLUF, BLU, lab, fs=12)
        arrow(7.6, 4.5, bx + 0.6, 3.9)
        arrow(bx + 0.6, 3.1, 7.6, 2.55)
    box(6.5, 1.7, 2.2, 0.8, TEALF, TEAL, "Σ ponderada\nh ∈ ℝ⁵¹²", fs=11)
    ax.text(7.6, 1.05, "expertos especializados\npor tipo de parche", ha="center",
            fontsize=9.5, color=GT, style="italic")

    fig.savefig(os.path.join(OUT_PATHPT, "..", "..", "..",
                "objetivo_2_mammoth_patron_invasion", "figuras", "slide_assets",
                "M00_mammoth_concepto.png"),
                dpi=DPI, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("  → M00_mammoth_concepto.png")


# ============================================================================
# Mammoth — tabla 8 tareas COMPACTA (legible en slide: 5 columnas)
# ============================================================================

# (tarea, balance, balCLAM, balMam, aucCLAM, aucMam, dbal, lectura, color, balance_num)
MAM8 = [
    ("Microcalc · carcinoma inv.", "21%", "0.639", "0.585", "0.732", "0.722", "−0.054 ± 0.125", "nulo", COL_GRIS_TXT, 21),
    ("Microcalc · CDIS", "36%", "0.595", "0.509", "0.652", "0.618", "−0.086 ± 0.113", "leve regresión", COL_ROJO, 36),
    ("Microcalc · tejido no neopl.", "59%", "0.577", "0.626", "0.646", "0.678", "+0.049 ± 0.077", "leve mejora", COL_VERDE, 59),
    ("Patrón · cribiforme", "49%", "0.650", "0.694", "0.710", "0.732", "+0.044 ± 0.048", "leve mejora", COL_VERDE, 49),
    ("Patrón · sólido", "76%", "0.647", "0.632", "0.700", "0.679", "−0.014 ± 0.064", "nulo", COL_GRIS_TXT, 76),
    ("Patrón · micropapilar", "7%", "0.617", "0.561", "0.707", "0.710", "−0.056 ‡", "nulo", COL_GRIS_TXT, 7),
    ("Patrón · papilar", "6%", "0.531", "0.506", "0.583", "0.599", "−0.025 ‡", "nulo", COL_GRIS_TXT, 6),
    ("Invasión linfovascular (3 cl.)", "mayor. 70%", "0.622", "0.575", "0.828", "0.818", "−0.047 ± 0.064", "regresión leve", COL_ROJO, 30),
]


def asset_mammoth_8tareas_compact():
    A_MAM = os.path.join(REPO, "sprints/B5_sprint5/objetivo_2_mammoth_patron_invasion/figuras/slide_assets")
    headers = ["Tarea", "Balance\n(clase +)", "bal_acc\nCLAM → +Mam", "AUC\nCLAM → +Mam",
               "Δ bal_acc\n(pareado)", "Lectura"]
    rows, cell_colors = [], {}
    for i, d in enumerate(MAM8):
        rows.append([d[0], d[1], f"{d[2]} → {d[3]}", f"{d[4]} → {d[5]}", d[6], d[7]])
        cell_colors[(i, 4)] = {"fg": d[8], "bold": True}
        cell_colors[(i, 5)] = {"fg": d[8], "bold": True}
    render_table(
        headers, rows, os.path.join(A_MAM, "T02b_mammoth_8tareas_compact.png"),
        cell_colors=cell_colors, fontsize=17,
        title="Mammoth en CLAM — 8 tareas pareadas (k=5): 0 palancas consistentes",
        footnote="Δ pareado = +Mammoth − CLAM sobre los mismos splits (métrica decisiva).  "
                 "‡ régimen ciego (3 positivos/test) → valor pooled.  Invasión: AUC macro-OVR (3 clases).  "
                 "Lean+ leve SOLO en las 2 tareas más balanceadas (tejido, cribiforme) → el cuello es el balance/dato, no la arquitectura.")
    print("  → T02b_mammoth_8tareas_compact.png")


def asset_mammoth_delta_bars():
    """Gráfico de barras divergentes Δ bal_acc (±std) por tarea, ordenado y coloreado."""
    A_MAM = os.path.join(REPO, "sprints/B5_sprint5/objetivo_2_mammoth_patron_invasion/figuras/slide_assets")
    # ordenar por Δ bal_acc
    data = []
    for d in MAM8:
        dbal = float(d[6].split("±")[0].replace("−", "-").replace("‡", "").strip())
        std = None
        if "±" in d[6]:
            std = float(d[6].split("±")[1].replace("‡", "").strip())
        data.append((d[0].replace(" · ", "·"), dbal, std, d[8]))
    data.sort(key=lambda x: x[1])
    labels = [x[0] for x in data]
    vals = [x[1] for x in data]
    errs = [x[2] if x[2] is not None else 0 for x in data]
    cols = [x[3] for x in data]
    fig, ax = plt.subplots(figsize=(9.2, 5.4), dpi=DPI)
    y = np.arange(len(labels))
    ax.barh(y, vals, xerr=errs, color=cols, edgecolor="#444444", lw=0.7,
            error_kw=dict(ecolor="#888888", lw=1.3, capsize=4), height=0.62)
    ax.axvline(0, color="#222222", lw=1.2)
    ax.set_yticks(y); ax.set_yticklabels(labels, fontsize=13)
    ax.set_xlabel("Δ balanced_acc  (mammoth − CLAM, pareado k=5)", fontsize=13, color=COL_GRIS_TXT)
    ax.set_xlim(-0.20, 0.16)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    # banda "balanceada"
    ax.axvspan(-0.002, 0.16, color="#E8F3EC", alpha=0.0)
    ax.set_title("Mammoth: el (leve) beneficio aparece solo en las tareas balanceadas",
                 fontsize=14.5, color=COL_TEAL_DK, weight="bold", pad=12)
    ax.text(0.012, len(labels) - 0.5, "mejora →", color=COL_VERDE, fontsize=11, weight="bold")
    ax.text(-0.012, len(labels) - 0.5, "← regresión", color=COL_ROJO, fontsize=11,
            weight="bold", ha="right")
    fig.tight_layout()
    out = os.path.join(A_MAM, "M04_mammoth_delta_bars.png")
    fig.savefig(out, dpi=DPI, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("  → M04_mammoth_delta_bars.png")


def asset_invasion_metrics():
    """Barras agrupadas formales: invasión, bal_acc y macro-OVR AUC, CLAM vs +Mammoth."""
    A_MAM = os.path.join(REPO, "sprints/B5_sprint5/objetivo_2_mammoth_patron_invasion/figuras/slide_assets")
    metrics = ["balanced_acc", "macro-OVR AUC"]
    clam = [0.622, 0.828]
    mam = [0.575, 0.818]
    clam_e = [0.028, 0.021]
    mam_e = [0.057, 0.019]
    x = np.arange(len(metrics)); width = 0.34
    fig, ax = plt.subplots(figsize=(6.6, 5.2), dpi=DPI)
    b1 = ax.bar(x - width / 2, clam, width, yerr=clam_e, label="CLAM",
                color="#2C7A8C", edgecolor="#1E5C6B", lw=0.8,
                error_kw=dict(ecolor="#555", lw=1.3, capsize=5))
    b2 = ax.bar(x + width / 2, mam, width, yerr=mam_e, label="+ Mammoth",
                color="#E2723B", edgecolor="#B4521E", lw=0.8,
                error_kw=dict(ecolor="#555", lw=1.3, capsize=5))
    ax.axhline(0.333, ls="--", lw=1.2, color="#999999")
    ax.text(1.46, 0.345, "trivial 0.333", fontsize=10, color="#777777", ha="right")
    for bars in (b1, b2):
        for b in bars:
            ax.annotate(f"{b.get_height():.3f}", (b.get_x() + b.get_width() / 2, b.get_height()),
                        textcoords="offset points", xytext=(0, 4), ha="center",
                        fontsize=12, fontweight="bold", color=COL_NEGRO)
    ax.set_xticks(x); ax.set_xticklabels(metrics, fontsize=13)
    ax.set_ylim(0, 1.0); ax.set_ylabel("valor (test, k=5)", fontsize=12, color=COL_GRIS_TXT)
    ax.legend(fontsize=12, loc="upper left", frameon=False)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.set_title("Invasión linfovascular (3 clases, n=2814)",
                 fontsize=14.5, color=COL_TEAL_DK, weight="bold", pad=12)
    fig.tight_layout()
    out = os.path.join(A_MAM, "M05_invasion_metrics.png")
    fig.savefig(out, dpi=DPI, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("  → M05_invasion_metrics.png")


def main():
    print("=== PathPT mitotic ===")
    asset_mitotic_paired()
    asset_mitotic_confusions()
    print("=== PathPT microcalc go/no-go ===")
    asset_microcalc_gonogo()
    print("=== Cierre 3 ejes ===")
    asset_tres_ejes()
    print("=== Mammoth concepto + tabla compacta + delta bars ===")
    asset_mammoth_concept()
    asset_mammoth_8tareas_compact()
    asset_mammoth_delta_bars()
    asset_invasion_metrics()
    print("OK")


if __name__ == "__main__":
    main()
