#!/usr/bin/env python
"""generate_slide_assets.py — assets PNG insertables para slides Environ.

Genera tablas y matrices de confusión como PNG transparentes, listos para
arrastrar a slides del template Environ (NO incluyen logo, header ni título —
eso lo agrega Ernesto en la slide).

Paleta inspirada en el deck (CLAM_Sprint_B4.pdf):
  - teal petróleo  #2C7A8C  (headers/tablas, títulos cuando aplica)
  - gris claro     #F3F4F5  (filas alternadas/headers)
  - negro          #222222  (texto)
  - rojo señal     #C0392B  (regresión/destacar negativo)
  - verde señal    #1E8449  (positivo/cumple)
  - ámbar señal    #B9770E  (ambiguo/plateau)

Tipografía: DejaVu Sans (garantizada en el env). DPI 220 → tablas legibles
incluso al insertar y ampliar en slide.

Salida: sprints/B4_sprint4/objetivo_5_fusion_binaria/figuras/slide_assets/
Uso:    PY=/home/sdonoso/miniconda3/envs/clam_latest/bin/python
        $PY scripts/generate_slide_assets.py
"""
import glob
import json
import os
import pickle

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import balanced_accuracy_score

# -- Config global --
matplotlib.rcParams["font.family"] = "DejaVu Sans"
matplotlib.rcParams["font.weight"] = "normal"
matplotlib.rcParams["axes.titleweight"] = "bold"

REPO = "/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto"
OUT = os.path.join(REPO, "sprints/B4_sprint4/objetivo_5_fusion_binaria/figuras/slide_assets")
os.makedirs(OUT, exist_ok=True)

# Paleta Environ
COL_TEAL = "#2C7A8C"
COL_TEAL_DK = "#1E5C6B"
COL_GRIS = "#F3F4F5"
COL_NEGRO = "#222222"
COL_GRIS_TXT = "#555555"
COL_ROJO = "#C0392B"
COL_VERDE = "#1E8449"
COL_AMBAR = "#B9770E"
COL_BORDER = "#D5D8DC"

DPI = 220
TEJIDOS = ["carcinoma_invasivo", "cdis", "tejido_no_neoplasico"]
TEJIDO_LABEL = {
    "carcinoma_invasivo": "carcinoma invasivo",
    "cdis": "CDIS",
    "tejido_no_neoplasico": "tejido no neoplásico",
}


# =============================================================================
# Helpers tabla
# =============================================================================

def render_table(headers, rows, out_path, col_widths=None,
                 row_colors=None, cell_colors=None,
                 header_bg=COL_TEAL, header_fg="white",
                 title=None, footnote=None,
                 figsize=None, fontsize=11):
    """Render a matplotlib table as a high-DPI PNG.

    headers: list[str]
    rows: list[list[str]]
    col_widths: opcional, lista de pesos (suma debe ser ~1.0)
    row_colors: opcional, color de fondo por fila (len == n_rows)
    cell_colors: opcional, dict {(i, j): color} para destacar celdas
    header_bg / header_fg: estilo del header
    title: opcional, texto en negrita arriba
    footnote: opcional, texto chico debajo
    """
    n_rows = len(rows); n_cols = len(headers)
    if col_widths is None:
        col_widths = [1.0 / n_cols] * n_cols

    # Heuristica tamaño: ancho por nº cols, alto por nº rows (compacto)
    if figsize is None:
        w = max(8, 1.6 * n_cols)
        h = 0.45 * (n_rows + 1) + (0.45 if title else 0.1) + (0.25 if footnote else 0.1)
        figsize = (w, h)

    fig, ax = plt.subplots(figsize=figsize, dpi=DPI)
    ax.axis("off")

    table = ax.table(
        cellText=rows,
        colLabels=headers,
        colWidths=col_widths,
        loc="center",
        cellLoc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(fontsize)
    table.scale(1, 1.6)

    # Estilo: header
    for j in range(n_cols):
        c = table[0, j]
        c.set_facecolor(header_bg)
        c.set_text_props(color=header_fg, weight="bold", fontsize=fontsize)
        c.set_edgecolor(COL_BORDER)
        c.set_linewidth(0.6)
        c.set_height(c.get_height() * 1.0)

    # Estilo: cuerpo
    for i in range(n_rows):
        bg = COL_GRIS if (row_colors is None and i % 2 == 1) else (
            row_colors[i] if row_colors else "white")
        for j in range(n_cols):
            c = table[i + 1, j]
            c.set_facecolor(bg)
            c.set_edgecolor(COL_BORDER)
            c.set_linewidth(0.6)
            # primera columna en negrita (label)
            weight = "bold" if j == 0 else "normal"
            color = COL_NEGRO
            # cell overrides
            if cell_colors and (i, j) in cell_colors:
                cc = cell_colors[(i, j)]
                if isinstance(cc, dict):
                    if "bg" in cc:
                        c.set_facecolor(cc["bg"])
                    if "fg" in cc:
                        color = cc["fg"]
                    if "bold" in cc and cc["bold"]:
                        weight = "bold"
                else:
                    color = cc
                    weight = "bold"
            c.set_text_props(color=color, weight=weight, fontsize=fontsize)

    if title:
        fig.suptitle(title, fontsize=fontsize + 3, color=COL_TEAL_DK, weight="bold", y=0.97)
    if footnote:
        fig.text(0.5, 0.015, footnote, ha="center", fontsize=fontsize - 2,
                 color=COL_GRIS_TXT, style="italic")

    fig.tight_layout(rect=[0, 0.03 if footnote else 0, 1, 0.93 if title else 1])
    fig.savefig(out_path, dpi=DPI, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  → {os.path.basename(out_path)}")


def render_confusion(conf, out_path, title=None, n_label=None,
                     classes=("no", "sí"), vmax=None, fontsize=13):
    """Heatmap 2x2 con anotación TN/FP/FN/TP + porcentaje + recall+/-."""
    conf = np.asarray(conf, dtype=int)
    tn, fp, fn, tp = conf[0, 0], conf[0, 1], conf[1, 0], conf[1, 1]
    total = conf.sum()
    rec_p = tp / (tp + fn) if (tp + fn) else 0
    rec_n = tn / (tn + fp) if (tn + fp) else 0
    bal = (rec_p + rec_n) / 2

    fig, ax = plt.subplots(figsize=(5.5, 4.5), dpi=DPI)
    vmax = vmax or conf.max()
    im = ax.imshow(conf, cmap="Blues", vmin=0, vmax=vmax if vmax > 0 else 1)
    labels = [["TN", "FP"], ["FN", "TP"]]
    for r in range(2):
        for c in range(2):
            v = conf[r, c]
            color = "white" if v > vmax * 0.55 else COL_NEGRO
            ax.text(c, r, f"{labels[r][c]}\n{v}\n({v/total:.0%})",
                    ha="center", va="center",
                    fontsize=fontsize, color=color, weight="bold")
    ax.set_xticks([0, 1]); ax.set_xticklabels([f"pred {classes[0]}", f"pred {classes[1]}"],
                                              fontsize=fontsize - 2)
    ax.set_yticks([0, 1]); ax.set_yticklabels([f"true {classes[0]}", f"true {classes[1]}"],
                                              fontsize=fontsize - 2)
    sub = f"recall+ = {rec_p:.2f}   ·   recall− = {rec_n:.2f}   ·   bal_acc = {bal:.2f}"
    if n_label is not None:
        sub = f"n_test = {n_label}   ·   " + sub
    ax.set_xlabel(sub, fontsize=fontsize - 2, color=COL_GRIS_TXT, labelpad=10)
    if title:
        ax.set_title(title, fontsize=fontsize + 1, color=COL_TEAL_DK, weight="bold", pad=12)

    fig.tight_layout()
    fig.savefig(out_path, dpi=DPI, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  → {os.path.basename(out_path)}")


def render_confusion_grid(items, out_path, suptitle=None, ncols=5, fontsize=11):
    """Grid de matrices de confusión 2x2 (un subplot por fold)."""
    n = len(items)
    nrows = int(np.ceil(n / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(2.6 * ncols, 2.8 * nrows + 0.5), dpi=DPI)
    axes = np.atleast_2d(axes).reshape(nrows, ncols)
    vmax = max(np.asarray(c).max() for _, c, _ in items)
    for i in range(nrows * ncols):
        ax = axes[i // ncols, i % ncols]
        if i >= n:
            ax.axis("off"); continue
        title, conf, n_test = items[i]
        conf = np.asarray(conf, dtype=int)
        tn, fp, fn, tp = conf[0, 0], conf[0, 1], conf[1, 0], conf[1, 1]
        total = conf.sum()
        rec_p = tp / (tp + fn) if (tp + fn) else 0
        rec_n = tn / (tn + fp) if (tn + fp) else 0
        bal = (rec_p + rec_n) / 2
        ax.imshow(conf, cmap="Blues", vmin=0, vmax=vmax if vmax > 0 else 1)
        for r in range(2):
            for c in range(2):
                v = conf[r, c]
                color = "white" if v > vmax * 0.55 else COL_NEGRO
                ax.text(c, r, f"{v}\n({v/total:.0%})", ha="center", va="center",
                        fontsize=fontsize - 1, color=color, weight="bold")
        ax.set_xticks([0, 1]); ax.set_xticklabels(["pred no", "pred sí"], fontsize=fontsize - 3)
        ax.set_yticks([0, 1]); ax.set_yticklabels(["true no", "true sí"], fontsize=fontsize - 3)
        ax.set_title(f"{title}  ·  bal={bal:.2f}  ·  r+={rec_p:.2f}",
                     fontsize=fontsize - 1, color=COL_TEAL_DK, weight="bold")
    if suptitle:
        fig.suptitle(suptitle, fontsize=fontsize + 3, color=COL_TEAL_DK, weight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.94 if suptitle else 1])
    fig.savefig(out_path, dpi=DPI, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  → {os.path.basename(out_path)}")


# =============================================================================
# Lectores de resultados (verdad de campo)
# =============================================================================

def _read_split_descriptor(split_dir, fold):
    f = os.path.join(split_dir, f"splits_{fold}_descriptor.csv")
    df = pd.read_csv(f, index_col=0)
    return df  # index: ['no', 'si'], cols: ['train','val','test']


def _bal_acc_folds(rundir):
    out = []
    for pkl in sorted(glob.glob(os.path.join(rundir, "split_*_results.pkl"))):
        with open(pkl, "rb") as f:
            r = pickle.load(f)
        yt = [v["label"] for v in r.values()]
        yp = [int(np.argmax(np.asarray(v["prob"]).squeeze())) for v in r.values()]
        out.append(balanced_accuracy_score(yt, yp))
    return np.array(out)


def _conf_from_pkl(pkl_path):
    with open(pkl_path, "rb") as f:
        r = pickle.load(f)
    yt = np.array([v["label"] for v in r.values()])
    yp = np.array([int(np.argmax(np.asarray(v["prob"]).squeeze())) for v in r.values()])
    tn = int(((yt == 0) & (yp == 0)).sum())
    fp = int(((yt == 0) & (yp == 1)).sum())
    fn = int(((yt == 1) & (yp == 0)).sum())
    tp = int(((yt == 1) & (yp == 1)).sum())
    return np.array([[tn, fp], [fn, tp]])


def fase0_per_fold(t):
    """Devuelve (auc[5], bal[5], conf[5]) para CLAM binaria t en Fase 0."""
    rundir = glob.glob(os.path.join(REPO, f"results/obj5_varianza_{t}/*"))[0]
    aucs = pd.read_csv(glob.glob(os.path.join(rundir, "summary.csv"))[0])["test_auc"].values
    bals = _bal_acc_folds(rundir)
    confs = [_conf_from_pkl(p) for p in sorted(glob.glob(os.path.join(rundir, "split_*_results.pkl")))]
    return aucs, bals, confs


def fused_per_fold(results_subdir, prefix):
    """Fase 1 (CLAM) o Fase 2 (DSMIL) sobre el fusionado."""
    aucs, bals, confs = [], [], []
    for d in sorted(glob.glob(os.path.join(REPO, results_subdir, f"{prefix}_f*_s1"))):
        f = os.path.join(d, "test_metrics.json")
        if not os.path.isfile(f): continue
        with open(f) as fh:
            m = json.load(fh)
        aucs.append(m["test_auc"]); bals.append(m["balanced_acc"])
        confs.append(np.array(m["confusion"]))
    return np.array(aucs), np.array(bals), confs


def anexo_per_fold(t):
    """Anexo DSMIL × binaria t × k=5."""
    aucs, bals, confs = [], [], []
    for d in sorted(glob.glob(os.path.join(REPO, f"results/obj5_anexo_dsmil_binarias_{t}/dsmil_*_f*_s1"))):
        f = os.path.join(d, "test_metrics.json")
        if not os.path.isfile(f): continue
        with open(f) as fh:
            m = json.load(fh)
        aucs.append(m["test_auc"]); bals.append(m["balanced_acc"])
        confs.append(np.array(m["confusion"]))
    return np.array(aucs), np.array(bals), confs


# =============================================================================
# Slide assets: TABLAS DE DATOS / SPLITS
# =============================================================================

def asset_binarias_composicion():
    """Composición de las 3 binarias (CSV read-only de Sebastián, 328 slides)."""
    headers = ["Tarea binaria", "Positivos (sí)", "Negativos (no)", "Total", "Ratio neg:pos"]
    rows = [
        ["micro en carcinoma invasivo", "68",  "260", "328", "3.8 : 1"],
        ["micro en CDIS",                "118", "210", "328", "1.8 : 1"],
        ["micro en tejido no neoplásico", "192", "136", "328", "0.7 : 1"],
    ]
    footnote = "no_identificado excluido · CSVs read-only en clam_environ/environ/csv/"
    render_table(headers, rows, os.path.join(OUT, "T01_binarias_composicion.png"),
                 col_widths=[0.35, 0.16, 0.16, 0.13, 0.20],
                 title="Composición de las 3 tareas binarias (328 slides identificadas)",
                 footnote=footnote)


def asset_fusionado_composicion():
    """Composición del binario fusionado (Fase 1/2)."""
    headers = ["Clase", "Slides", "Qué incluye"]
    rows = [
        ["sí (positivo)", "328",  "micro en CUALQUIER tejido (une las 3 binarias)"],
        ["no (negativo)", "2486", "no_identificado (CAP no menciona micro)"],
        ["Total",         "2814", "ratio 7.6 : 1 — cumple cap ≤10× sin oversampling"],
    ]
    footnote = "Excluida 1 slide sin features CONCH (histai_1132)"
    render_table(headers, rows, os.path.join(OUT, "T02_fusionado_composicion.png"),
                 col_widths=[0.22, 0.13, 0.65],
                 title='Composición del binario fusionado "¿tiene microcalcificaciones?"',
                 footnote=footnote)


def asset_splits_por_fase():
    """Tabla resumen de splits por fase (train/val/test típico por fold)."""
    headers = ["Fase / experimento", "Tarea", "k folds", "train (sí/no)", "val (sí/no)", "test (sí/no)"]
    # Tomo fold 0 como representativo (los otros son ±1-2 slides)
    rows = []
    for t in TEJIDOS:
        df = _read_split_descriptor(
            os.path.join(REPO, f"data/splits_kfold/microcalcificaciones_en_{t}_pth_100"), 0)
        rows.append([f"Fase 0 / Anexo (binaria)", TEJIDO_LABEL[t], "5",
                     f"{int(df.loc['si','train'])} / {int(df.loc['no','train'])}",
                     f"{int(df.loc['si','val'])} / {int(df.loc['no','val'])}",
                     f"{int(df.loc['si','test'])} / {int(df.loc['no','test'])}"])
    df = _read_split_descriptor(
        os.path.join(REPO, "data/splits_kfold/microcalcificaciones_presencia_100"), 0)
    rows.append(["Fase 1 / Fase 2 (fusionado)", "presencia (sí/no)", "3",
                 f"{int(df.loc['si','train'])} / {int(df.loc['no','train'])}",
                 f"{int(df.loc['si','val'])} / {int(df.loc['no','val'])}",
                 f"{int(df.loc['si','test'])} / {int(df.loc['no','test'])}"])
    footnote = "Conteos del fold 0 (los demás folds varían ±1-2 slides) · MC-CV val_frac=test_frac=0.1 · semilla 1"
    render_table(headers, rows, os.path.join(OUT, "T03_splits_por_fase.png"),
                 col_widths=[0.27, 0.20, 0.08, 0.15, 0.13, 0.17],
                 title="Splits train/val/test por fase (MC-CV)", footnote=footnote)


def asset_resumen_fases():
    """Tabla resumen Fase 0/1/2/Anexo: qué pregunta responde cada una."""
    headers = ["Fase", "Pregunta", "Tarea(s)", "Modelo", "Slides", "k MC-CV", "Job"]
    rows = [
        ["Fase 0", "¿Cuánto baila la métrica por suerte del sorteo?",
         "3 binarias separadas", "CLAM_MB", "328 c/u", "5", "4170"],
        ["Fase 1", "¿Fusionar 'tiene/no tiene' + no_identificado como negativo mejora?",
         "fusionada (presencia)", "CLAM_MB", "2814", "3", "4171"],
        ["Fase 2", "¿DSMIL le gana a CLAM sobre el fusionado?",
         "fusionada (presencia)", "DSMIL", "2814", "3", "4172"],
        ["Anexo",  "¿El 'fracaso DSMIL en binarias' del 4137 era ruido del sorteo?",
         "3 binarias separadas", "DSMIL", "328 c/u", "5", "4179"],
    ]
    footnote = "Anexo reutiliza los MISMOS splits de Fase 0 → comparación CLAM vs DSMIL paired por construcción"
    render_table(headers, rows, os.path.join(OUT, "T04_resumen_fases.png"),
                 col_widths=[0.07, 0.42, 0.14, 0.08, 0.08, 0.08, 0.07],
                 fontsize=10, title="Objetivo 5: 4 experimentos · qué responde cada uno",
                 footnote=footnote)


# =============================================================================
# Slide assets: TABLAS DE RESULTADOS
# =============================================================================

def _fmt(x): return f"{x:.3f}"
def _fmt_ms(m, s): return f"{m:.3f} ± {s:.3f}"


def asset_fase0_mean_std():
    headers = ["Tarea binaria", "AUC por fold", "AUC mean ± std", "bal_acc mean ± std", "4109 (1 sorteo)"]
    rows = []
    for t in TEJIDOS:
        aucs, bals, _ = fase0_per_fold(t)
        per_fold = " / ".join(f"{a:.2f}" for a in aucs)
        ref_auc = {"carcinoma_invasivo": "0.808 · bal 0.78",
                   "cdis": "0.678 · bal 0.59",
                   "tejido_no_neoplasico": "0.658 · bal 0.58"}[t]
        rows.append([TEJIDO_LABEL[t], per_fold, _fmt_ms(aucs.mean(), aucs.std()),
                     _fmt_ms(bals.mean(), bals.std()), ref_auc])
    footnote = "Job 4170 · CLAM_MB · k=5 MC-CV · 27-may"
    render_table(headers, rows, os.path.join(OUT, "T05_fase0_resultados.png"),
                 col_widths=[0.21, 0.27, 0.16, 0.18, 0.18], fontsize=10,
                 title="Fase 0 · CLAM × 3 binarias × MC-CV k=5 (caracterización de varianza)",
                 footnote=footnote)


def asset_fase1_per_fold():
    aucs, bals, confs = fused_per_fold("results/obj5_fase1_clam_fusionado", "clam_presencia")
    headers = ["Métrica", "fold 0", "fold 1", "fold 2", "media ± std"]
    rows = [
        ["test_auc",        *[_fmt(x) for x in aucs], _fmt_ms(aucs.mean(), aucs.std())],
        ["balanced_acc",    *[_fmt(x) for x in bals], _fmt_ms(bals.mean(), bals.std())],
    ]
    # recall+ / recall- por fold
    rec_p = [c[1,1]/(c[1,1]+c[1,0]) for c in confs]
    rec_n = [c[0,0]/(c[0,0]+c[0,1]) for c in confs]
    rows.append(["recall+ (TP/(TP+FN))",  *[f"{r:.2f}" for r in rec_p], _fmt_ms(np.mean(rec_p), np.std(rec_p))])
    rows.append(["recall− (TN/(TN+FP))",  *[f"{r:.2f}" for r in rec_n], _fmt_ms(np.mean(rec_n), np.std(rec_n))])
    rows.append(["confusión TN/FP",
                 *[f"{c[0,0]}/{c[0,1]}" for c in confs], "—"])
    rows.append(["confusión FN/TP",
                 *[f"{c[1,0]}/{c[1,1]}" for c in confs], "—"])
    footnote = "Job 4171 · CLAM_MB sobre fusionado · k=3 · veredicto §1.3 = PLATEAU (0.55 ≤ bal_acc < 0.65)"
    render_table(headers, rows, os.path.join(OUT, "T06_fase1_resultados.png"),
                 col_widths=[0.30, 0.16, 0.16, 0.16, 0.22], fontsize=11,
                 title="Fase 1 · CLAM × fusionado (presencia) · k=3 MC-CV",
                 footnote=footnote)


def asset_fase2_per_fold():
    aucs, bals, confs = fused_per_fold("results/obj5_fase2_dsmil_fusionado", "dsmil_presencia")
    headers = ["Métrica", "fold 0", "fold 1", "fold 2", "media ± std"]
    rows = [
        ["test_auc",     *[_fmt(x) for x in aucs], _fmt_ms(aucs.mean(), aucs.std())],
        ["balanced_acc", *[_fmt(x) for x in bals], _fmt_ms(bals.mean(), bals.std())],
    ]
    rec_p = [c[1,1]/(c[1,1]+c[1,0]) for c in confs]
    rec_n = [c[0,0]/(c[0,0]+c[0,1]) for c in confs]
    rows.append(["recall+ (TP/(TP+FN))", *[f"{r:.2f}" for r in rec_p], _fmt_ms(np.mean(rec_p), np.std(rec_p))])
    rows.append(["recall− (TN/(TN+FP))", *[f"{r:.2f}" for r in rec_n], _fmt_ms(np.mean(rec_n), np.std(rec_n))])
    rows.append(["confusión TN/FP",  *[f"{c[0,0]}/{c[0,1]}" for c in confs], "—"])
    rows.append(["confusión FN/TP",  *[f"{c[1,0]}/{c[1,1]}" for c in confs], "—"])
    footnote = "Job 4172 · DSMIL sobre fusionado · k=3 · gate Fase 1 PASÓ · veredicto §2.2 = banda AMBIGUA"
    render_table(headers, rows, os.path.join(OUT, "T07_fase2_resultados.png"),
                 col_widths=[0.30, 0.16, 0.16, 0.16, 0.22], fontsize=11,
                 title="Fase 2 · DSMIL × fusionado (presencia) · k=3 MC-CV",
                 footnote=footnote)


def asset_fase12_paired():
    clam_a, clam_b, _ = fused_per_fold("results/obj5_fase1_clam_fusionado", "clam_presencia")
    dsmil_a, dsmil_b, _ = fused_per_fold("results/obj5_fase2_dsmil_fusionado", "dsmil_presencia")
    d_a = dsmil_a - clam_a; d_b = dsmil_b - clam_b
    headers = ["Fold", "CLAM bal", "DSMIL bal", "Δ bal", "CLAM auc", "DSMIL auc", "Δ auc"]
    rows = []
    for i in range(3):
        rows.append([f"fold {i}", _fmt(clam_b[i]), _fmt(dsmil_b[i]), f"{d_b[i]:+.3f}",
                     _fmt(clam_a[i]), _fmt(dsmil_a[i]), f"{d_a[i]:+.3f}"])
    rows.append(["media ± std", _fmt_ms(clam_b.mean(), clam_b.std()),
                 _fmt_ms(dsmil_b.mean(), dsmil_b.std()),
                 f"{d_b.mean():+.3f} ± {d_b.std():.3f}",
                 _fmt_ms(clam_a.mean(), clam_a.std()),
                 _fmt_ms(dsmil_a.mean(), dsmil_a.std()),
                 f"{d_a.mean():+.3f} ± {d_a.std():.3f}"])
    # Destacar última fila + Δ positivo verde, negativo rojo
    cell_colors = {(3, 0): {"bg": COL_GRIS, "bold": True}}
    for j in range(1, 7):
        cell_colors[(3, j)] = {"bg": COL_GRIS, "bold": True}
    for i in range(4):
        for j_d, col_arr in [(3, d_b), (6, d_a)]:
            val = col_arr[i] if i < 3 else col_arr.mean()
            if val > 0.005:
                cell_colors[(i, j_d)] = {"fg": COL_VERDE, "bold": True,
                                         "bg": cell_colors.get((i,j_d), {}).get("bg", COL_GRIS if i==3 else ("white" if i%2==0 else COL_GRIS))}
            elif val < -0.005:
                cell_colors[(i, j_d)] = {"fg": COL_ROJO, "bold": True,
                                         "bg": cell_colors.get((i,j_d), {}).get("bg", COL_GRIS if i==3 else ("white" if i%2==0 else COL_GRIS))}
    footnote = "Comparación pareada (mismos splits Fase 1) · banda AMBIGUA: Δ bal positivo en 3/3 folds pero std grande y AUC retrocede"
    render_table(headers, rows, os.path.join(OUT, "T08_fase12_paired.png"),
                 col_widths=[0.10, 0.12, 0.13, 0.15, 0.12, 0.13, 0.15], fontsize=11,
                 cell_colors=cell_colors,
                 title="Comparación pareada CLAM (Fase 1) vs DSMIL (Fase 2) · fusionado · k=3",
                 footnote=footnote)


def asset_anexo_mean_std():
    """Anexo: tabla mean±std por tarea + Δ pareado vs Fase 0."""
    headers = ["Tarea binaria", "DSMIL auc", "DSMIL bal_acc", "Δ auc pareado", "Δ bal pareado", "Veredicto"]
    rows = []
    veredicto = {"carcinoma_invasivo": ("NULL  (OK)", COL_VERDE),
                 "cdis": ("Regresión leve  (!)", COL_ROJO),
                 "tejido_no_neoplasico": ("NULL / ambigua", COL_AMBAR)}
    cell_colors = {}
    for i, t in enumerate(TEJIDOS):
        clam_a, clam_b, _ = fase0_per_fold(t)
        ds_a, ds_b, _ = anexo_per_fold(t)
        d_a = ds_a - clam_a; d_b = ds_b - clam_b
        ver, col = veredicto[t]
        rows.append([TEJIDO_LABEL[t],
                     _fmt_ms(ds_a.mean(), ds_a.std()),
                     _fmt_ms(ds_b.mean(), ds_b.std()),
                     f"{d_a.mean():+.3f} ± {d_a.std():.3f}",
                     f"{d_b.mean():+.3f} ± {d_b.std():.3f}",
                     ver])
        # Color Δ
        if d_a.mean() > 0.005: cell_colors[(i, 3)] = {"fg": COL_VERDE, "bold": True}
        elif d_a.mean() < -0.005: cell_colors[(i, 3)] = {"fg": COL_ROJO, "bold": True}
        if d_b.mean() > 0.005: cell_colors[(i, 4)] = {"fg": COL_VERDE, "bold": True}
        elif d_b.mean() < -0.005: cell_colors[(i, 4)] = {"fg": COL_ROJO, "bold": True}
        cell_colors[(i, 5)] = {"fg": col, "bold": True}
    footnote = ("Mismos splits que Fase 0 (paired) · k=5 · job 4179 · "
                "umbrales pre-registrados: NULL |Δbal|<0.03 + bandas solapadas · "
                "Regresión Δbal ≤ −0.05 · Señal Δbal > +0.05 + bandas no solapadas")
    render_table(headers, rows, os.path.join(OUT, "T09_anexo_resultados.png"),
                 col_widths=[0.20, 0.13, 0.15, 0.15, 0.15, 0.22], fontsize=11,
                 cell_colors=cell_colors,
                 title="Anexo · DSMIL × 3 binarias × MC-CV k=5 · veredicto por tarea",
                 footnote=footnote)


def asset_anexo_paired_per_fold():
    """Anexo: Δ pareado por fold y tarea (5 folds × 3 tareas)."""
    headers = ["Fold", "carcinoma  Δbal / Δauc", "CDIS  Δbal / Δauc",
               "tejido  Δbal / Δauc"]
    rows = []
    cell_colors = {}
    deltas_per_task = {}
    for t in TEJIDOS:
        clam_a, clam_b, _ = fase0_per_fold(t)
        ds_a, ds_b, _ = anexo_per_fold(t)
        deltas_per_task[t] = (ds_b - clam_b, ds_a - clam_a)
    for f in range(5):
        cells = [f"fold {f}"]
        for j, t in enumerate(TEJIDOS, start=1):
            db, da = deltas_per_task[t]
            cells.append(f"{db[f]:+.3f}  /  {da[f]:+.3f}")
            # color por signo Δ bal
            if db[f] > 0.005:
                cell_colors[(f, j)] = {"fg": COL_VERDE, "bold": True}
            elif db[f] < -0.005:
                cell_colors[(f, j)] = {"fg": COL_ROJO, "bold": True}
        rows.append(cells)
    # Fila resumen signo Δ bal
    signs_row = ["signo Δ bal"]
    for t in TEJIDOS:
        db, _ = deltas_per_task[t]
        n_pos = (db > 0).sum(); n_neg = (db < 0).sum()
        if n_neg == 5:
            txt, col = "5/5 negativo (consistente)", COL_ROJO
        elif n_pos == 5:
            txt, col = "5/5 positivo (consistente)", COL_VERDE
        else:
            txt, col = f"{n_pos}/5 positivo, {n_neg}/5 negativo (mixto)", COL_AMBAR
        signs_row.append(txt)
    rows.append(signs_row)
    for j in range(1, 4):
        cell_colors[(5, j)] = {"fg": COL_ROJO if "negativo" in rows[5][j] else (COL_VERDE if "positivo" in rows[5][j] else COL_AMBAR), "bold": True, "bg": COL_GRIS}
    cell_colors[(5, 0)] = {"bg": COL_GRIS, "bold": True}

    footnote = "Δ = DSMIL Anexo − CLAM Fase 0 · mismos splits · CDIS único caso con signo consistente negativo en los 5 folds"
    render_table(headers, rows, os.path.join(OUT, "T10_anexo_paired_per_fold.png"),
                 col_widths=[0.16, 0.28, 0.28, 0.28], fontsize=11,
                 cell_colors=cell_colors,
                 title="Anexo · Δ pareado DSMIL − CLAM por fold (mismos splits Fase 0)",
                 footnote=footnote)


def asset_comparativa_maestra():
    """Tabla maestra: las 16 filas de la comparativa global."""
    headers = ["#", "Job", "Experimento", "Modelo", "Formulación", "Slides", "k", "test_auc", "balanced_acc"]
    rows = [
        ["1", "4098", "Baseline 8 clases",                   "CLAM_MB", "8 clases",  "3072", "1", "0.81",         "0.31"],
        ["2", "4099", "Ablación B=16",                       "CLAM_MB", "8 clases",  "3072", "1", "0.82",         "0.24"],
        ["3", "4109", "Reformulación · carcinoma inv.",      "CLAM_MB", "binaria",   "333",  "1", "0.808",        "0.78"],
        ["4", "4109", "Reformulación · CDIS",                "CLAM_MB", "binaria",   "333",  "1", "0.678",        "0.59"],
        ["5", "4109", "Reformulación · tejido no neo.",      "CLAM_MB", "binaria",   "333",  "1", "0.658",        "0.58"],
        ["6", "4137", "DSMIL · carcinoma inv. (1 sorteo)",   "DSMIL",   "binaria",   "333",  "1", "0.824",        "(fracaso)"],
        ["7", "4137", "DSMIL · CDIS (1 sorteo)",             "DSMIL",   "binaria",   "333",  "1", "0.570",        "(fracaso)"],
        ["8", "4137", "DSMIL · tejido no neo. (1 sorteo)",   "DSMIL",   "binaria",   "333",  "1", "0.577",        "(fracaso)"],
        ["9", "4170", "Fase 0 varianza · carcinoma",         "CLAM_MB", "binaria",   "328",  "5", "0.732 ± 0.167","0.639 ± 0.077"],
        ["10","4170", "Fase 0 varianza · CDIS",              "CLAM_MB", "binaria",   "328",  "5", "0.652 ± 0.072","0.595 ± 0.077"],
        ["11","4170", "Fase 0 varianza · tejido",            "CLAM_MB", "binaria",   "328",  "5", "0.646 ± 0.025","0.577 ± 0.030"],
        ["12","4171", "Fase 1 · fusionado",                  "CLAM_MB", "fusionada", "2814", "3", "0.776 ± 0.021","0.620 ± 0.010 (plateau)"],
        ["13","4172", "Fase 2 · fusionado",                  "DSMIL",   "fusionada", "2814", "3", "0.756 ± 0.024","0.661 ± 0.046 (ambigua)"],
        ["14","4179", "Anexo · DSMIL × carcinoma (k=5)",     "DSMIL",   "binaria",   "328",  "5", "0.722 ± 0.098","0.617 ± 0.117  (NULL)"],
        ["15","4179", "Anexo · DSMIL × CDIS (k=5)",          "DSMIL",   "binaria",   "328",  "5", "0.619 ± 0.099","0.543 ± 0.077  (regr.)"],
        ["16","4179", "Anexo · DSMIL × tejido (k=5)",        "DSMIL",   "binaria",   "328",  "5", "0.682 ± 0.042","0.599 ± 0.029  (NULL/amb)"],
    ]
    cell_colors = {}
    # Filas 6-8 grisadas (fracaso single-split, superado por anexo)
    for i in (5, 6, 7):
        for j in range(len(headers)):
            cell_colors[(i, j)] = {"fg": COL_GRIS_TXT, "bg": "white"}
    # Veredicto del anexo (14-16): colorear última columna
    cell_colors[(13, 8)] = {"fg": COL_VERDE, "bold": True}
    cell_colors[(14, 8)] = {"fg": COL_ROJO,  "bold": True}
    cell_colors[(15, 8)] = {"fg": COL_AMBAR, "bold": True}
    cell_colors[(11, 8)] = {"fg": COL_AMBAR, "bold": True}
    cell_colors[(12, 8)] = {"fg": COL_AMBAR, "bold": True}
    footnote = ("Filas 6-8 (4137 single-split) reemplazadas en honestidad por filas 14-16 (anexo MC-CV) · "
                "k=1 split → optimista/ruidoso · k=3/5 con barras de error = honesto")
    render_table(headers, rows, os.path.join(OUT, "T11_comparativa_maestra.png"),
                 col_widths=[0.03, 0.05, 0.22, 0.07, 0.08, 0.06, 0.04, 0.15, 0.30],
                 fontsize=9, cell_colors=cell_colors,
                 title="Comparativa maestra · todos los entrenamientos del Objetivo 5",
                 footnote=footnote)


def asset_comparativa_sebastian():
    headers = ["Tarea", "4109 (1 sorteo)", "Fase 0 MC-CV (honesto)", "Sebastián (1 sorteo)", "¿distinguibles?"]
    rows = [
        ["micro carcinoma invasivo",  "0.808", "0.732 ± 0.167", "0.79", "NO — Sebastián cae dentro de nuestra banda"],
        ["micro CDIS",                 "0.678", "0.652 ± 0.072", "0.69", "NO — se solapan"],
        ["micro tejido no neoplásico", "0.658", "0.646 ± 0.025", "0.63", "NO — se solapan"],
    ]
    footnote = ("Métrica = test_auc · single-split del 4109 era optimista por suerte · "
                "con barras de error las 3 tareas son indistinguibles de Sebastián")
    render_table(headers, rows, os.path.join(OUT, "T12_comparativa_sebastian.png"),
                 col_widths=[0.24, 0.14, 0.20, 0.18, 0.24], fontsize=11,
                 title="Comparativa contra Sebastián · single-split vs MC-CV honesto",
                 footnote=footnote)


def asset_cuadro_arquitecturas():
    """Cuadro 2x2 modelos x regímenes (DSMIL evaluado en todo)."""
    headers = ["", "Binarias separadas (n=328, k=5)", "Fusionado (n=2814, k=3)"]
    rows = [
        ["CLAM",  "Fase 0 (job 4170)  ·  bal 0.58–0.64", "Fase 1 (job 4171)  ·  bal 0.620 ± 0.010 (plateau)"],
        ["DSMIL", "Anexo (job 4179)  ·  bal 0.54–0.62  ·  Δ pareado ≈ 0 (CDIS regresión leve)",
                  "Fase 2 (job 4172)  ·  bal 0.661 ± 0.046 (ambigua)  ·  Δ pareado +0.040 ± 0.038"],
    ]
    footnote = ("DSMIL evaluado en TODOS los regímenes con MC-CV · "
                "la arquitectura sola NO es la palanca a ninguna escala disponible")
    render_table(headers, rows, os.path.join(OUT, "T13_cuadro_arquitecturas.png"),
                 col_widths=[0.10, 0.40, 0.50], fontsize=11,
                 title="Cuadro CLAM × DSMIL × {binarias, fusionado} cerrado simétricamente",
                 footnote=footnote)


# =============================================================================
# Slide assets: MATRICES DE CONFUSIÓN
# =============================================================================

def assets_confusion():
    # Fase 0: una grid por tarea (5 folds)
    for t in TEJIDOS:
        _, _, confs = fase0_per_fold(t)
        items = [(f"f{i}", c, c.sum()) for i, c in enumerate(confs)]
        render_confusion_grid(items, os.path.join(OUT, f"M01_fase0_{t}.png"),
                               suptitle=f"Fase 0 · CLAM × {TEJIDO_LABEL[t]} · k=5 (job 4170)",
                               ncols=5)

    # Fase 1: 3 folds CLAM fusionado
    _, _, confs = fused_per_fold("results/obj5_fase1_clam_fusionado", "clam_presencia")
    items = [(f"f{i}", c, c.sum()) for i, c in enumerate(confs)]
    render_confusion_grid(items, os.path.join(OUT, "M02_fase1_clam_fusionado.png"),
                           suptitle="Fase 1 · CLAM × fusionado (presencia) · k=3 (job 4171)",
                           ncols=3)

    # Fase 2: 3 folds DSMIL fusionado
    _, _, confs = fused_per_fold("results/obj5_fase2_dsmil_fusionado", "dsmil_presencia")
    items = [(f"f{i}", c, c.sum()) for i, c in enumerate(confs)]
    render_confusion_grid(items, os.path.join(OUT, "M03_fase2_dsmil_fusionado.png"),
                           suptitle="Fase 2 · DSMIL × fusionado (presencia) · k=3 (job 4172)",
                           ncols=3)

    # Anexo: una grid por tarea (5 folds DSMIL binaria)
    for t in TEJIDOS:
        _, _, confs = anexo_per_fold(t)
        items = [(f"f{i}", c, c.sum()) for i, c in enumerate(confs)]
        render_confusion_grid(items, os.path.join(OUT, f"M04_anexo_{t}.png"),
                               suptitle=f"Anexo · DSMIL × {TEJIDO_LABEL[t]} · k=5 (job 4179)",
                               ncols=5)


# =============================================================================
# Main
# =============================================================================

def main():
    print("=== Slide assets — Tablas de datos / splits ===")
    asset_resumen_fases()
    asset_binarias_composicion()
    asset_fusionado_composicion()
    asset_splits_por_fase()

    print("\n=== Slide assets — Tablas de resultados ===")
    asset_fase0_mean_std()
    asset_fase1_per_fold()
    asset_fase2_per_fold()
    asset_fase12_paired()
    asset_anexo_mean_std()
    asset_anexo_paired_per_fold()
    asset_comparativa_maestra()
    asset_comparativa_sebastian()
    asset_cuadro_arquitecturas()

    print("\n=== Slide assets — Matrices de confusión ===")
    assets_confusion()

    print(f"\nAssets en: {OUT}")
    print(f"Total: {len(glob.glob(os.path.join(OUT, '*.png')))} PNG")


if __name__ == "__main__":
    main()
