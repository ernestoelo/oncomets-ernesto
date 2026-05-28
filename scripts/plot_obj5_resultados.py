#!/usr/bin/env python
"""plot_obj5_resultados.py — figuras del Objetivo 5 para la presentación.

Genera barras con barra de error (media ± std sobre las repeticiones de
Monte Carlo CV). Reutilizable: usa lo que exista hoy y se re-corre cuando
terminen Fase 1/2.

- Fig 1: Fase 0 — 3 binarias (CLAM). test_auc y balanced_acc (media±std),
  con el single-split del 4109 (marcador) y Sebastián (marcador, solo AUC)
  para mostrar que el número suelto engañaba.
- Fig 2: fusionado — CLAM (Fase 1) vs DSMIL (Fase 2), balanced_acc + test_auc
  (media±std, comparación pareada). Solo si hay test_metrics.json.

Salida: sprints/B4_sprint4/objetivo_5_fusion_binaria/figuras/*.png

Uso: PY=/home/sdonoso/miniconda3/envs/clam_latest/bin/python
     $PY scripts/plot_obj5_resultados.py
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

REPO = "/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto"
OUT = os.path.join(REPO, "sprints/B4_sprint4/objetivo_5_fusion_binaria/figuras")
os.makedirs(OUT, exist_ok=True)

TEJIDOS = ["carcinoma_invasivo", "cdis", "tejido_no_neoplasico"]
LABELS = ["carcinoma\ninvasivo", "CDIS", "tejido no\nneoplásico"]

# Referencias single-split (job 4109) y Sebastián (su tabla 26-may, test_auc).
REF_4109_AUC = {"carcinoma_invasivo": 0.808, "cdis": 0.678, "tejido_no_neoplasico": 0.658}
REF_4109_BAL = {"carcinoma_invasivo": 0.78, "cdis": 0.59, "tejido_no_neoplasico": 0.58}
REF_SEB_AUC = {"carcinoma_invasivo": 0.79, "cdis": 0.69, "tejido_no_neoplasico": 0.63}


def _bal_acc_folds(rundir):
    out = []
    for pkl in sorted(glob.glob(os.path.join(rundir, "split_*_results.pkl"))):
        with open(pkl, "rb") as f:
            r = pickle.load(f)
        yt = [v["label"] for v in r.values()]
        yp = [int(np.argmax(np.asarray(v["prob"]).squeeze())) for v in r.values()]
        out.append(balanced_accuracy_score(yt, yp))
    return np.array(out)


def fase0():
    auc_m, auc_s, bal_m, bal_s = [], [], [], []
    for t in TEJIDOS:
        dirs = glob.glob(os.path.join(REPO, f"results/obj5_varianza_{t}/*"))
        if not dirs:
            print(f"[fase0] sin resultados para {t} — abortar fig 1")
            return False
        rundir = dirs[0]
        aucs = pd.read_csv(glob.glob(os.path.join(rundir, "summary.csv"))[0])["test_auc"].values
        bals = _bal_acc_folds(rundir)
        auc_m.append(aucs.mean()); auc_s.append(aucs.std())
        bal_m.append(bals.mean()); bal_s.append(bals.std())

    x = np.arange(len(TEJIDOS))
    for metric, (m, s, ref4109, refseb, ylab, fname) in {
        "auc": (auc_m, auc_s, REF_4109_AUC, REF_SEB_AUC, "test AUC", "fig1a_fase0_auc.png"),
        "bal": (bal_m, bal_s, REF_4109_BAL, None, "balanced accuracy", "fig1b_fase0_balacc.png"),
    }.items():
        fig, ax = plt.subplots(figsize=(7, 4.5))
        ax.bar(x, m, yerr=s, capsize=6, color="#4C78A8", alpha=0.85,
               label="CLAM — Monte Carlo CV (media ± std, k=5)")
        ax.scatter(x, [ref4109[t] for t in TEJIDOS], color="#E45756", marker="X",
                   s=90, zorder=5, label="single-split (job 4109)")
        if refseb is not None:
            ax.scatter(x, [refseb[t] for t in TEJIDOS], color="#000000", marker="D",
                       s=55, zorder=5, label="Sebastián (1 sorteo)")
        ax.axhline(0.5, ls="--", lw=1, color="gray", label="piso trivial 0.50")
        ax.set_xticks(x); ax.set_xticklabels(LABELS)
        ax.set_ylabel(ylab); ax.set_ylim(0.3, 1.0)
        ax.set_title(f"Microcalcificaciones — 3 binarias · {ylab}\n"
                     f"el single-split engañaba; con barra de error son indistinguibles")
        ax.legend(fontsize=8, loc="lower right")
        for xi, (mi, si) in enumerate(zip(m, s)):
            ax.text(xi, mi + si + 0.02, f"{mi:.2f}±{si:.2f}", ha="center", fontsize=8)
        fig.tight_layout(); fig.savefig(os.path.join(OUT, fname), dpi=150)
        plt.close(fig); print(f"[fase0] {fname}")
    return True


def _fused_metrics(results_dir, prefix):
    """media±std de test_auc y balanced_acc desde test_metrics.json por fold."""
    aucs, bals = [], []
    for d in sorted(glob.glob(os.path.join(REPO, results_dir, f"{prefix}_f*_s1"))):
        f = os.path.join(d, "test_metrics.json")
        if not os.path.isfile(f):
            continue
        with open(f) as fh:
            m = json.load(fh)
        if m.get("test_auc") == m.get("test_auc"):
            aucs.append(m["test_auc"])
        bals.append(m["balanced_acc"])
    return np.array(aucs), np.array(bals)


def fase12():
    clam_auc, clam_bal = _fused_metrics("results/obj5_fase1_clam_fusionado", "clam_presencia")
    dsmil_auc, dsmil_bal = _fused_metrics("results/obj5_fase2_dsmil_fusionado", "dsmil_presencia")
    if len(clam_bal) == 0 and len(dsmil_bal) == 0:
        print("[fase12] aún sin test_metrics.json — fig 2 pendiente")
        return False

    fig, ax = plt.subplots(figsize=(7, 4.5))
    groups = ["balanced acc", "test AUC"]
    x = np.arange(len(groups)); w = 0.35

    def stat(arr):
        return (arr.mean(), arr.std()) if len(arr) else (np.nan, 0)
    clam = [stat(clam_bal), stat(clam_auc)]
    dsmil = [stat(dsmil_bal), stat(dsmil_auc)]
    ax.bar(x - w/2, [c[0] for c in clam], w, yerr=[c[1] for c in clam], capsize=6,
           color="#4C78A8", label="CLAM (Fase 1)")
    ax.bar(x + w/2, [d[0] for d in dsmil], w, yerr=[d[1] for d in dsmil], capsize=6,
           color="#F58518", label="DSMIL (Fase 2)")
    ax.axhline(0.5, ls="--", lw=1, color="gray")
    ax.set_xticks(x); ax.set_xticklabels(groups)
    ax.set_ylim(0.3, 1.0); ax.set_ylabel("score")
    ax.set_title("Binario fusionado ¿tiene microcalcificaciones?\n"
                 "CLAM vs DSMIL · Monte Carlo CV (media ± std, k=3) · comparación pareada")
    ax.legend(fontsize=9)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig2_fusionado_clam_vs_dsmil.png"), dpi=150)
    plt.close(fig); print("[fase12] fig2_fusionado_clam_vs_dsmil.png")
    return True


def anexo_dsmil_binarias():
    """Fig 3: CLAM Fase 0 vs DSMIL anexo, 3 binarias × k=5 (paired)."""
    clam_auc_m, clam_auc_s, clam_bal_m, clam_bal_s = [], [], [], []
    dsmil_auc_m, dsmil_auc_s, dsmil_bal_m, dsmil_bal_s = [], [], [], []
    for t in TEJIDOS:
        f0_dirs = glob.glob(os.path.join(REPO, f"results/obj5_varianza_{t}/*"))
        anx_dirs = sorted(glob.glob(os.path.join(REPO, f"results/obj5_anexo_dsmil_binarias_{t}/dsmil_*_f*_s1")))
        if not f0_dirs or not anx_dirs:
            print(f"[anexo] sin resultados para {t} — abortar fig 3")
            return False
        # CLAM Fase 0
        aucs = pd.read_csv(glob.glob(os.path.join(f0_dirs[0], "summary.csv"))[0])["test_auc"].values
        bals = _bal_acc_folds(f0_dirs[0])
        clam_auc_m.append(aucs.mean()); clam_auc_s.append(aucs.std())
        clam_bal_m.append(bals.mean()); clam_bal_s.append(bals.std())
        # DSMIL anexo
        d_auc, d_bal = [], []
        for d in anx_dirs:
            with open(os.path.join(d, "test_metrics.json")) as fh:
                m = json.load(fh)
            d_auc.append(m["test_auc"]); d_bal.append(m["balanced_acc"])
        d_auc = np.array(d_auc); d_bal = np.array(d_bal)
        dsmil_auc_m.append(d_auc.mean()); dsmil_auc_s.append(d_auc.std())
        dsmil_bal_m.append(d_bal.mean()); dsmil_bal_s.append(d_bal.std())

    x = np.arange(len(TEJIDOS)); w = 0.35
    for metric, (cm, cs, dm, ds, ylab, fname) in {
        "auc": (clam_auc_m, clam_auc_s, dsmil_auc_m, dsmil_auc_s, "test AUC",
                "fig3a_anexo_dsmil_vs_clam_binarias_auc.png"),
        "bal": (clam_bal_m, clam_bal_s, dsmil_bal_m, dsmil_bal_s, "balanced accuracy",
                "fig3b_anexo_dsmil_vs_clam_binarias_balacc.png"),
    }.items():
        fig, ax = plt.subplots(figsize=(8, 4.8))
        ax.bar(x - w/2, cm, w, yerr=cs, capsize=6, color="#4C78A8",
               label="CLAM (Fase 0)")
        ax.bar(x + w/2, dm, w, yerr=ds, capsize=6, color="#F58518",
               label="DSMIL (Anexo)")
        ax.axhline(0.5, ls="--", lw=1, color="gray", label="piso trivial 0.50")
        ax.set_xticks(x); ax.set_xticklabels(LABELS)
        ax.set_ylabel(ylab); ax.set_ylim(0.3, 1.0)
        ax.set_title(f"Anexo · 3 binarias × MC-CV k=5 (mismos splits, paired) · {ylab}\n"
                     "CLAM (Fase 0, job 4170) vs DSMIL (Anexo, job 4179)")
        ax.legend(fontsize=9, loc="lower right")
        for xi, (cmi, csi, dmi, dsi) in enumerate(zip(cm, cs, dm, ds)):
            ax.text(xi - w/2, cmi + csi + 0.02, f"{cmi:.2f}±{csi:.2f}",
                    ha="center", fontsize=7)
            ax.text(xi + w/2, dmi + dsi + 0.02, f"{dmi:.2f}±{dsi:.2f}",
                    ha="center", fontsize=7)
        fig.tight_layout(); fig.savefig(os.path.join(OUT, fname), dpi=150)
        plt.close(fig); print(f"[anexo] {fname}")
    return True


def _confusion_from_pkl(pkl_path):
    """Calcula matriz 2x2 [[TN,FP],[FN,TP]] desde un split_*_results.pkl."""
    with open(pkl_path, "rb") as f:
        r = pickle.load(f)
    yt = np.array([v["label"] for v in r.values()])
    yp = np.array([int(np.argmax(np.asarray(v["prob"]).squeeze())) for v in r.values()])
    tn = int(((yt == 0) & (yp == 0)).sum())
    fp = int(((yt == 0) & (yp == 1)).sum())
    fn = int(((yt == 1) & (yp == 0)).sum())
    tp = int(((yt == 1) & (yp == 1)).sum())
    return np.array([[tn, fp], [fn, tp]])


def _confusion_from_metrics_json(json_path):
    with open(json_path) as fh:
        m = json.load(fh)
    return np.array(m["confusion"])


def _plot_confusion_grid(rows, suptitle, fname, ncols=5):
    """rows = list of (title, conf 2x2). Plotea grid de heatmaps con anotaciones."""
    n = len(rows)
    nrows = int(np.ceil(n / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(2.4*ncols, 2.4*nrows + 0.6))
    axes = np.atleast_2d(axes).reshape(nrows, ncols)
    for i in range(nrows * ncols):
        ax = axes[i // ncols, i % ncols]
        if i >= n:
            ax.axis("off"); continue
        title, conf = rows[i]
        total = conf.sum()
        im = ax.imshow(conf, cmap="Blues", vmin=0, vmax=conf.max() if conf.max() > 0 else 1)
        for r in range(2):
            for c in range(2):
                v = conf[r, c]
                color = "white" if v > conf.max() * 0.5 else "black"
                ax.text(c, r, f"{v}\n({v/total:.0%})", ha="center", va="center",
                        fontsize=8, color=color)
        ax.set_xticks([0, 1]); ax.set_xticklabels(["pred no", "pred sí"], fontsize=7)
        ax.set_yticks([0, 1]); ax.set_yticklabels(["true no", "true sí"], fontsize=7)
        ax.set_title(title, fontsize=8)
    fig.suptitle(suptitle, fontsize=11)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(os.path.join(OUT, fname), dpi=150)
    plt.close(fig); print(f"[confusion] {fname}")


def matrices_confusion():
    """Fig 4: matrices de confusión por fold para todos los experimentos."""
    # --- Fase 0 (3 binarias × 5 folds) ---
    for t, label in zip(TEJIDOS, ["carcinoma invasivo", "CDIS", "tejido no neoplásico"]):
        rundir_list = glob.glob(os.path.join(REPO, f"results/obj5_varianza_{t}/*"))
        if not rundir_list: continue
        rundir = rundir_list[0]
        rows = []
        for i, pkl in enumerate(sorted(glob.glob(os.path.join(rundir, "split_*_results.pkl")))):
            conf = _confusion_from_pkl(pkl)
            rows.append((f"f{i}", conf))
        if rows:
            _plot_confusion_grid(rows, f"Fase 0 · CLAM × {label} · k=5 (job 4170)",
                                  f"fig4a_fase0_{t}_confusion.png", ncols=5)

    # --- Fase 1 (CLAM fusionado × 3 folds) ---
    rows = []
    for d in sorted(glob.glob(os.path.join(REPO, "results/obj5_fase1_clam_fusionado/clam_presencia_f*_s1"))):
        f = os.path.join(d, "test_metrics.json")
        if not os.path.isfile(f): continue
        fold = d.split("_f")[-1].split("_")[0]
        rows.append((f"f{fold}", _confusion_from_metrics_json(f)))
    if rows:
        _plot_confusion_grid(rows, "Fase 1 · CLAM × fusionado (presencia) · k=3 (job 4171)",
                              "fig4b_fase1_clam_fusionado_confusion.png", ncols=3)

    # --- Fase 2 (DSMIL fusionado × 3 folds) ---
    rows = []
    for d in sorted(glob.glob(os.path.join(REPO, "results/obj5_fase2_dsmil_fusionado/dsmil_presencia_f*_s1"))):
        f = os.path.join(d, "test_metrics.json")
        if not os.path.isfile(f): continue
        fold = d.split("_f")[-1].split("_")[0]
        rows.append((f"f{fold}", _confusion_from_metrics_json(f)))
    if rows:
        _plot_confusion_grid(rows, "Fase 2 · DSMIL × fusionado (presencia) · k=3 (job 4172)",
                              "fig4c_fase2_dsmil_fusionado_confusion.png", ncols=3)

    # --- Anexo (DSMIL × 3 binarias × 5 folds) ---
    for t, label in zip(TEJIDOS, ["carcinoma invasivo", "CDIS", "tejido no neoplásico"]):
        dirs = sorted(glob.glob(os.path.join(REPO, f"results/obj5_anexo_dsmil_binarias_{t}/dsmil_*_f*_s1")))
        rows = []
        for d in dirs:
            f = os.path.join(d, "test_metrics.json")
            if not os.path.isfile(f): continue
            fold = d.split("_f")[-1].split("_")[0]
            rows.append((f"f{fold}", _confusion_from_metrics_json(f)))
        if rows:
            _plot_confusion_grid(rows, f"Anexo · DSMIL × {label} · k=5 (job 4179)",
                                  f"fig4d_anexo_{t}_confusion.png", ncols=5)
    return True


if __name__ == "__main__":
    fase0()
    fase12()
    anexo_dsmil_binarias()
    matrices_confusion()
    print(f"Figuras en: {OUT}")
