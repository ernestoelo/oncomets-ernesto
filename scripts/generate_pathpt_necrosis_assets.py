#!/usr/bin/env python3
"""Assets insertables (PNG, estilo Environ teal) de la Etapa 1 PathPT necrosis.

Reusa render_table / render_confusion de scripts/generate_slide_assets.py (DPI 220,
auto-dimensión de columnas, fix e88032f). Convención de presentación (Benjamín,
[[presentacion-convenciones-benjamin]]): SIN números de job, SIN nombres de personas.

Verdad de campo (committeada): results/pathpt_etapa1/necrosis/{clam,pathpt}_*_s1/.
Salida: sprints/B5_sprint5/pathpt/figuras/slide_assets/  (T## tablas, M## matrices).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from generate_slide_assets import render_table, render_confusion  # noqa: E402

OUT = os.path.join(
    HERE, "..", "sprints", "B5_sprint5", "pathpt", "figuras", "slide_assets")
OUT = os.path.abspath(OUT)
os.makedirs(OUT, exist_ok=True)

COL_POS = "#2E7D32"   # verde Δ>0
COL_NEG = "#C62828"   # rojo  Δ<0
COL_MED = "#DCEAEE"   # teal claro fila media
COL_GRIS = "#F4F4F4"

# --- Verdad de campo (de los 10 test_metrics.json; ver resultados_necrosis.md) ---
# fold: (clam_auc, clam_bal, pathpt_auc, pathpt_bal)
FOLDS = [
    (0, 0.798, 0.653, 0.798, 0.663),
    (1, 0.782, 0.607, 0.798, 0.698),
    (2, 0.598, 0.656, 0.588, 0.641),
    (3, 0.754, 0.610, 0.599, 0.502),
    (4, 0.703, 0.641, 0.522, 0.563),
]
MEAN = (0.727, 0.633, 0.661, 0.613)        # medias por brazo
D_AUC_MS = (-0.066, 0.094)                  # Δ AUC media ± std
D_BAL_MS = (-0.020, 0.078)                  # Δ bal_acc media ± std
CONF_CLAM = [[16, 24], [21, 138]]           # pooled (5 folds), [[TN,FP],[FN,TP]]
CONF_PATHPT = [[19, 21], [39, 120]]
N_POOL = 199


def _sgn(x):
    return f"+{x:.3f}" if x > 0 else (f"−{abs(x):.3f}" if x < 0 else "+0.000")


def _color(x):
    return COL_POS if x > 0 else (COL_NEG if x < 0 else None)


def asset_paired_table():
    headers = ["Fold", "CLAM\nAUC / bal_acc", "PathPT\nAUC / bal_acc", "Δ AUC", "Δ bal_acc"]
    rows, cell_colors, row_colors = [], {}, []
    for i, (f, ca, cb, pa, pb) in enumerate(FOLDS):
        d_auc, d_bal = pa - ca, pb - cb
        rows.append([str(f), f"{ca:.3f} / {cb:.3f}", f"{pa:.3f} / {pb:.3f}",
                     _sgn(d_auc), _sgn(d_bal)])
        for col, dv in ((3, d_auc), (4, d_bal)):
            c = _color(dv)
            if c:
                cell_colors[(i, col)] = {"fg": c, "bold": True}
        row_colors.append(COL_GRIS if i % 2 == 1 else "white")
    # fila media ± std
    rows.append(["media", f"{MEAN[0]:.3f} / {MEAN[1]:.3f}", f"{MEAN[2]:.3f} / {MEAN[3]:.3f}",
                 f"−{abs(D_AUC_MS[0]):.3f} ± {D_AUC_MS[1]:.3f}",
                 f"−{abs(D_BAL_MS[0]):.3f} ± {D_BAL_MS[1]:.3f}"])
    row_colors.append(COL_MED)
    mi = len(rows) - 1
    cell_colors[(mi, 3)] = {"fg": COL_NEG, "bold": True}
    cell_colors[(mi, 4)] = {"fg": COL_NEG, "bold": True}
    cell_colors[(mi, 0)] = {"bold": True}

    render_table(
        headers, rows, os.path.join(OUT, "T10_pathpt_necrosis_paired.png"),
        row_colors=row_colors, cell_colors=cell_colors,
        title="PathPT vs CLAM — necrosis (comparación pareada, k=5)",
        footnote="Δ = PathPT − CLAM sobre los mismos splits.  Empate / ambiguo: "
                 "std ≫ |media| en bal_acc (signo 2+/3−); lean negativo en AUC.")


def asset_confusions():
    render_confusion(
        CONF_CLAM, os.path.join(OUT, "M11_necrosis_confusion_clam.png"),
        title="CLAM — necrosis (confusión agregada 5 folds)",
        n_label=N_POOL, classes=("ausente", "presente"))
    render_confusion(
        CONF_PATHPT, os.path.join(OUT, "M12_necrosis_confusion_pathpt.png"),
        title="PathPT — necrosis (confusión agregada 5 folds)",
        n_label=N_POOL, classes=("ausente", "presente"))


if __name__ == "__main__":
    print(f"Generando assets en {OUT}")
    asset_paired_table()
    asset_confusions()
    print("OK")
