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


if __name__ == "__main__":
    fase0()
    fase12()
    print(f"Figuras en: {OUT}")
