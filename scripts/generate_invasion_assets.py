#!/usr/bin/env python
"""Assets insertables (PNG) para invasión linfática 3-clase (Obj2 B5, 2ª ola, job 4246).

Convención CLAUDE.md "Assets PNG insertables": sin logo/header/título de slide, solo el
contenido (matriz/figura/tabla); DPI 220; fondo blanco; DejaVu Sans. Ernesto los arrastra
a OnlyOffice preservando el branding Environ. M## = matrices/figuras, T## = tablas.

Lee la verdad de campo (`test_metrics.json` de los 10 runs) — NO transcribe números.
Reusa `render_table` de generate_slide_assets.py (auto-dimensiona columnas).

Genera:
  M01_invasion_confusion_3x3.png   — confusiones 3×3 sumadas CLAM vs +Mammoth + recall
  M02_invasion_delta_pareado.png   — Δ pareado (bal_acc, AUC) por fold
  M03_invasion_recall_por_clase.png— recall por clase CLAM vs +Mammoth (colapso a mayoritaria)
  T01_invasion_resumen.png         — tabla resumen (brazo × bal_acc × AUC media±std + Δ)
"""
import glob
import json
import os
import statistics as st

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from generate_slide_assets import render_table, COL_TEAL, COL_TEAL_DK, COL_NEGRO, \
    COL_GRIS_TXT, COL_ROJO, COL_VERDE, COL_BORDER, DPI

REPO = "/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto"
BASE = os.path.join(REPO, "results/obj2_mammoth/invasion_linfatica_vascular_pth")
OUT = os.path.join(REPO, "sprints/B5_sprint5/objetivo_2_mammoth_patron_invasion/figuras/slide_assets")
os.makedirs(OUT, exist_ok=True)
ARMS = ["clam", "clam_mammoth"]
ARM_LABEL = {"clam": "CLAM", "clam_mammoth": "CLAM + Mammoth"}
CLS = ["ausente", "no_identificado", "presente"]
CLS_SHORT = ["aus", "no_id", "pres"]


def load(arm, fold):
    d = glob.glob(f"{BASE}/{arm}_invasion_linfatica_vascular_pth_f{fold}_*_s1")[0]
    with open(f"{d}/test_metrics.json") as fh:
        return json.load(fh)


def conf_sum(arm):
    C = np.zeros((3, 3), dtype=int)
    for f in range(5):
        C += np.asarray(load(arm, f)["confusion"], dtype=int)
    return C


def recalls(C):
    return [C[i, i] / C[i].sum() if C[i].sum() else float("nan") for i in range(3)]


def per_fold(arm, key):
    return [load(arm, f)[key] for f in range(5)]


# ---- M01: confusiones 3×3 lado a lado ----
def asset_confusion():
    Cs = {a: conf_sum(a) for a in ARMS}
    vmax = max(C.max() for C in Cs.values())
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8), dpi=DPI)
    for ax, arm in zip(axes, ARMS):
        C = Cs[arm]; r = recalls(C)
        im = ax.imshow(C, cmap="Blues", vmin=0, vmax=vmax)
        for i in range(3):
            for j in range(3):
                v = int(C[i, j])
                color = "white" if v > vmax * 0.55 else COL_NEGRO
                diag = " ✓" if i == j else ""
                ax.text(j, i, f"{v}{diag}", ha="center", va="center",
                        fontsize=13, color=color, weight="bold" if i == j else "normal")
        ax.set_xticks(range(3)); ax.set_xticklabels([f"pred\n{c}" for c in CLS_SHORT], fontsize=10)
        ax.set_yticks(range(3)); ax.set_yticklabels([f"true {c}" for c in CLS_SHORT], fontsize=10)
        rec_txt = "   ".join(f"recall {CLS_SHORT[i]}={r[i]:.2f}" for i in range(3))
        ax.set_xlabel(rec_txt, fontsize=9.5, color=COL_GRIS_TXT, labelpad=10)
        ax.set_title(f"{ARM_LABEL[arm]}  (5 folds sumados)", fontsize=12,
                     color=COL_TEAL_DK, weight="bold", pad=10)
    fig.tight_layout()
    p = os.path.join(OUT, "M01_invasion_confusion_3x3.png")
    fig.savefig(p, dpi=DPI, bbox_inches="tight", facecolor="white"); plt.close(fig)
    print(f"  → {os.path.basename(p)}")


# ---- M02: Δ pareado por fold (bal_acc, AUC) ----
def asset_delta():
    db = [load("clam_mammoth", f)["balanced_acc"] - load("clam", f)["balanced_acc"] for f in range(5)]
    da = [load("clam_mammoth", f)["test_auc"] - load("clam", f)["test_auc"] for f in range(5)]
    x = np.arange(5); w = 0.38
    fig, ax = plt.subplots(figsize=(8.5, 4.6), dpi=DPI)
    b1 = ax.bar(x - w / 2, db, w, label="Δ bal_acc",
                color=[COL_ROJO if v < 0 else COL_VERDE for v in db])
    b2 = ax.bar(x + w / 2, da, w, label="Δ macro-OVR AUC",
                color=[COL_TEAL if v < 0 else COL_VERDE for v in da], alpha=0.85)
    ax.axhline(0, color=COL_NEGRO, lw=1)
    for bars, vals in ((b1, db), (b2, da)):
        for bar, v in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2,
                    v + (0.004 if v >= 0 else -0.004), f"{v:+.3f}",
                    ha="center", va="bottom" if v >= 0 else "top", fontsize=8.5,
                    color=COL_NEGRO)
    ax.set_xticks(x); ax.set_xticklabels([f"fold {i}" for i in range(5)], fontsize=11)
    ax.set_ylabel("Δ (mammoth − clam)", fontsize=11)
    ax.set_title("Δ pareado por fold — mammoth NO mejora (AUC 5/5 negativo; f3 = colapso)",
                 fontsize=11.5, color=COL_TEAL_DK, weight="bold", pad=10)
    ax.legend(fontsize=10, loc="lower left", framealpha=0.9)
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color=COL_BORDER, lw=0.6, alpha=0.7)
    fig.tight_layout()
    p = os.path.join(OUT, "M02_invasion_delta_pareado.png")
    fig.savefig(p, dpi=DPI, bbox_inches="tight", facecolor="white"); plt.close(fig)
    print(f"  → {os.path.basename(p)}")


# ---- M03: recall por clase CLAM vs mammoth ----
def asset_recall():
    rc = {a: recalls(conf_sum(a)) for a in ARMS}
    x = np.arange(3); w = 0.38
    fig, ax = plt.subplots(figsize=(8, 4.6), dpi=DPI)
    b1 = ax.bar(x - w / 2, rc["clam"], w, label="CLAM", color=COL_TEAL)
    b2 = ax.bar(x + w / 2, rc["clam_mammoth"], w, label="CLAM + Mammoth", color=COL_ROJO, alpha=0.85)
    for bars in (b1, b2):
        for bar in bars:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.012,
                    f"{bar.get_height():.2f}", ha="center", va="bottom", fontsize=9.5,
                    color=COL_NEGRO, weight="bold")
    ax.set_xticks(x); ax.set_xticklabels(CLS, fontsize=11)
    ax.set_ylim(0, 1.0); ax.set_ylabel("recall (test, 5 folds sumados)", fontsize=11)
    ax.set_title("Recall por clase — mammoth sube la mayoritaria a costa de 'presente'",
                 fontsize=11.5, color=COL_TEAL_DK, weight="bold", pad=10)
    ax.legend(fontsize=10, loc="upper right", framealpha=0.9)
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color=COL_BORDER, lw=0.6, alpha=0.7)
    fig.tight_layout()
    p = os.path.join(OUT, "M03_invasion_recall_por_clase.png")
    fig.savefig(p, dpi=DPI, bbox_inches="tight", facecolor="white"); plt.close(fig)
    print(f"  → {os.path.basename(p)}")


# ---- T01: tabla resumen ----
def asset_resumen():
    def pm(xs):
        return f"{st.mean(xs):.3f} ± {st.pstdev(xs):.3f}"
    bc = {a: per_fold(a, "balanced_acc") for a in ARMS}
    au = {a: per_fold(a, "test_auc") for a in ARMS}
    db = [bc["clam_mammoth"][f] - bc["clam"][f] for f in range(5)]
    da = [au["clam_mammoth"][f] - au["clam"][f] for f in range(5)]
    headers = ["brazo", "balanced_acc", "macro-OVR AUC"]
    rows = [
        ["CLAM (baseline)", pm(bc["clam"]), pm(au["clam"])],
        ["CLAM + Mammoth", pm(bc["clam_mammoth"]), pm(au["clam_mammoth"])],
        ["Δ pareado (mam − clam)",
         f"{st.mean(db):+.3f} ± {st.pstdev(db):.3f}  ({sum(v>0 for v in db)}+/{sum(v<0 for v in db)}−)",
         f"{st.mean(da):+.3f} ± {st.pstdev(da):.3f}  ({sum(v>0 for v in da)}+/{sum(v<0 for v in da)}−)"],
    ]
    render_table(headers, rows, os.path.join(OUT, "T01_invasion_resumen.png"),
                 title="Invasión linfática 3-clase · k=5 paired · trivial bal_acc = 0.333",
                 footnote="Mammoth NO es palanca: Δ bal_acc en banda ambigua con lean negativo; "
                          "Δ AUC regresión leve consistente (5/5 folds−). std poblacional (ddof=0).")
    print("  → T01_invasion_resumen.png")


if __name__ == "__main__":
    print(f"Assets invasión → {OUT}")
    asset_confusion()
    asset_delta()
    asset_recall()
    asset_resumen()
    print("Listo.")
