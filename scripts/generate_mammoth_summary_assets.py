#!/usr/bin/env python
"""generate_mammoth_summary_assets.py — tabla maestra del hilo mammoth (8 tareas).

Asset PNG insertable (recipe render_table de generate_slide_assets.py) que consolida
las 8 tareas pareadas k=5 del hilo mammoth en una sola tabla para la presentación:
3 microcalc (job microcalc) + 4 patrón CDIS (job patrón) + 1 invasión 3-clase.

Historia que cuenta: mammoth (MoE que reemplaza la 1ª capa lineal de CLAM) NO es palanca
en NINGUNA de las 8 — lean+ leve solo en las 2 tareas más balanceadas (tejido, cribiforme);
nulo o regresión leve en el resto → cuello = datos/desbalance, no la arquitectura.

Datos: sprints/B5_sprint5/objetivo_1_mammoth_run/resultados.md (microcalc) +
objetivo_2_mammoth_patron_invasion/{resultados.md, resultados_invasion.md}.
n por clase de microcalc VERIFICADA contra environ/csv/*.csv (10-jun): carcinoma 68/260,
cdis 118/210, tejido 192/136 — corrige el ~20% stale de la tabla cruzada (cdis = 36%).

Convenciones (presentacion-convenciones-benjamin): SIN números de job, SIN nombres.

Uso: /home/sdonoso/miniconda3/envs/clam_latest/bin/python scripts/generate_mammoth_summary_assets.py
"""
import os
import sys

REPO = "/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto"
sys.path.insert(0, os.path.join(REPO, "scripts"))
from generate_slide_assets import render_table, COL_VERDE, COL_ROJO, COL_GRIS_TXT  # noqa: E402

OUT = os.path.join(REPO, "sprints/B5_sprint5/objetivo_2_mammoth_patron_invasion/figuras/slide_assets")
os.makedirs(OUT, exist_ok=True)

# color por veredicto
MEJ = COL_VERDE          # leve mejora
REG = COL_ROJO           # regresión leve
NUL = COL_GRIS_TXT       # nulo

# filas: (tarea, clases, n_por_clase, balCLAM, balMam, aucCLAM, aucMam, dbal, lectura, veredicto)
ROWS = [
    ("Microcalc · carcinoma inv.", "2", "si 68 / no 260", "0.639", "0.585", "0.732", "0.722", "−0.054 ± 0.125", "nulo", NUL),
    ("Microcalc · CDIS",           "2", "si 118 / no 210", "0.595", "0.509", "0.652", "0.618", "−0.086 ± 0.113", "leve regresión", REG),
    ("Microcalc · tejido no neopl.","2", "si 192 / no 136", "0.577", "0.626", "0.646", "0.678", "+0.049 ± 0.077", "leve mejora", MEJ),
    ("Patrón · cribiforme",        "2", "si 252 / no 261", "0.650", "0.694", "0.710", "0.732", "+0.044 ± 0.048", "leve mejora", MEJ),
    ("Patrón · sólido",            "2", "si 388 / no 125", "0.647", "0.632", "0.700", "0.679", "−0.014 ± 0.064", "nulo", NUL),
    ("Patrón · micropapilar ‡",    "2", "si 34 / no 479",  "0.617", "0.561", "0.707", "0.710", "−0.056 ‡",       "nulo", NUL),
    ("Patrón · papilar ‡",         "2", "si 32 / no 481",  "0.531", "0.506", "0.583", "0.599", "−0.025 ‡",       "nulo", NUL),
    ("Invasión linfovascular",     "3", "no_id 1967 / aus 479 / pres 368", "0.622", "0.575", "0.828", "0.818", "−0.047 ± 0.064", "regresión leve", REG),
]

HEADERS = ["Tarea", "Clases", "n por clase",
           "bal_acc\nCLAM", "bal_acc\n+Mammoth",
           "AUC\nCLAM", "AUC\n+Mammoth",
           "Δ bal_acc\n(pareado)", "Lectura"]

DBAL_COL = 7
LECT_COL = 8


def main():
    rows = [list(r[:9]) for r in ROWS]
    cell_colors = {}
    for i, r in enumerate(ROWS):
        vcol = r[9]
        cell_colors[(i, DBAL_COL)] = {"fg": vcol, "bold": True}
        cell_colors[(i, LECT_COL)] = {"fg": vcol, "bold": True}

    out_path = os.path.join(OUT, "T02_mammoth_8tareas_resumen.png")
    render_table(
        HEADERS, rows, out_path,
        cell_colors=cell_colors,
        title="Mammoth en CLAM — 8 tareas pareadas (k=5): 0 palancas consistentes",
        footnote=("Pareado k=5 (mismos splits); único delta = 1ª capa lineal → mezcla de expertos (mammoth). "
                  "Celdas bal_acc/AUC = media de 5 folds; ±std reportado en el Δ pareado (decisivo). "
                  "‡ micropapilar/papilar: régimen ciego (3 pos/test) → valor pooled de 5 folds, sin ±.   "
                  "Invasión: AUC macro-OVR (3 clases).   "
                  "Lean+ leve solo en las 2 tareas más balanceadas (tejido 59%, cribiforme 49%) → cuello = datos/desbalance, no la arquitectura."),
        fontsize=11,
    )
    print(f"OK  {os.path.relpath(out_path, REPO)}")


if __name__ == "__main__":
    main()
