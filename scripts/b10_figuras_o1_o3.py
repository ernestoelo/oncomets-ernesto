#!/usr/bin/env python
"""Figuras de O1 y O3 del B10, para la reunion del martes 15-sep con Sebastian.

NO MIDE NADA. Lee los artefactos que produjeron los numeros publicados y los dibuja. Antes de
dibujar verifica que esos artefactos reproduzcan lo publicado, y aborta si no:

  O1  sprints/B10_sprint10/grado_sin_marca/resultados.md §3 y §4
      <- results/b10_grado_sin_marca/{escalera.csv, nulo.npz}
  O3  sprints/B10_sprint10/cdis_localizacion/resultados.md §1.a, §2 y §3.b
      <- results/b10_cdis/{auc_cdis.csv, auc_cdis_region.csv}

Lo unico que se agrega sobre esos artefactos es la suma por grado de O1 (recall, alcanzables y
el nulo iteracion a iteracion), que es la tabla del §4. El indice de columna del nulo sale de
`ESCALERA` del driver y el flag `alineada` de `cargar_offset()`, importados y no copiados
([[hallazgo-necesita-forma-presentable]]).

Escribe, y es su UNICO escritor:
  sprints/B10_sprint10/figuras/o1_apertura_grado.{png,csv}
  sprints/B10_sprint10/figuras/o3_auc_por_lamina.{png,csv}
Los CSV son los numeros dibujados, en el orden en que se dibujan
([[sidecar-orden-no-es-el-de-la-figura]]).

Paleta: grado y tier son ORDINALES (cambiar el orden cambia el significado), asi que van en una
rampa de un solo tono, mas oscuro = grado mas alto o tier mas limpio. Validada con la skill
`dataviz` (`validate_palette.py --ordinal --surface #ffffff`): monotona, saltos de L >= 0,06,
un solo tono (3 grados de dispersion) y el extremo claro a 2,50:1 contra el blanco.

Uso (workaround B; `envs/pruebas` porque el driver de O1 importa zarr al tope):
  /home/sdonoso/miniconda3/envs/pruebas/bin/python scripts/b10_figuras_o1_o3.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                                     # noqa: E402
import numpy as np                                                  # noqa: E402
import pandas as pd                                                 # noqa: E402
from matplotlib import font_manager                                 # noqa: E402
from matplotlib.lines import Line2D                                 # noqa: E402
from matplotlib.ticker import FixedLocator, NullLocator             # noqa: E402
from matplotlib.transforms import blended_transform_factory         # noqa: E402

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from b10_grado_sin_marca import ESCALERA, cargar_offset             # noqa: E402

RES_O1 = REPO / "results" / "b10_grado_sin_marca"
RES_O3 = REPO / "results" / "b10_cdis"
OUT = REPO / "sprints" / "B10_sprint10" / "figuras"
FONTS = REPO.parent / "fonts" / "barlow"
DPI = 200

# --------------------------------------------------------------------------------------
# estilo

SUP = "#ffffff"
TINTA = "#1A1A2E"          # titulo de la plantilla oficial (docs/plantilla_oficial.md §4)
TINTA_2 = "#52514e"
TENUE = "#898781"
GRILLA = "#e1e0d9"
EJE = "#c3c2b7"
RAMPA = ["#6da7ec", "#3987e5", "#1B4F8C", "#0d366b"]
GRADO_COLOR = {"bajo": RAMPA[0], "moderado": RAMPA[1], "alto": RAMPA[2]}
TIER_COLOR = {"train": RAMPA[0], "val": RAMPA[1], "test": RAMPA[2], "fuera": RAMPA[3]}


def estilo():
    for f in ("Barlow-Regular.ttf", "Barlow-Italic.ttf", "Barlow-Medium.ttf",
              "Barlow-SemiBold.ttf"):
        font_manager.fontManager.addfont(str(FONTS / f))
    plt.rcParams.update({
        "font.family": "Barlow", "font.size": 9.5,
        "figure.facecolor": SUP, "axes.facecolor": SUP, "savefig.facecolor": SUP,
        "axes.edgecolor": EJE, "axes.linewidth": 0.8, "axes.labelcolor": TINTA_2,
        "xtick.color": EJE, "ytick.color": EJE,
        "xtick.labelcolor": TINTA_2, "ytick.labelcolor": TINTA_2,
    })


def coma(x, dec):
    return f"{x:.{dec}f}".replace(".", ",")


# --------------------------------------------------------------------------------------
# O1

PELDANOS = [10, 20, 50, 100, 200, 500, 1000, 2000]     # los que corren sobre las 21 laminas
GRADOS = ["alto", "moderado", "bajo"]

# resultados.md §3: N -> (recall total, mm2 por lamina, nulo medio, nulo p97,5)
PUB_O1_TOTAL = {10: (8, 0.13, 0.01, 0.0), 20: (10, 0.26, 0.03, 1.0),
                50: (17, 0.60, 0.07, 1.0), 100: (24, 1.15, 0.12, 1.0),
                200: (31, 2.02, 0.27, 2.0), 500: (53, 4.07, 0.64, 3.0),
                1000: (68, 6.45, 1.33, 4.0), 2000: (86, 9.55, 2.51, 7.0)}
# resultados.md §4: N -> recall de (alto, moderado, bajo)
PUB_O1_GRADO = {200: (27, 4, 0), 500: (41, 12, 0), 2000: (57, 23, 6)}
PUB_ALCANZABLES = {"alto": 76, "moderado": 53, "bajo": 16}


def datos_o1():
    e = pd.read_csv(RES_O1 / "escalera.csv", dtype={"slide": str})
    a = e[(e.brazo == "A_lamina_entera") & (e.desc == "percentil")]
    # La suma por grado solo vale si ninguna lamina tiene dos grados (resultados.md §7).
    assert not a.grados.str.contains("/").any(), "una lamina con dos grados"
    lam = a.drop_duplicates("slide").set_index("slide")
    assert len(lam) == 21, len(lam)
    nulo = np.load(RES_O1 / "nulo.npz")

    filas = []
    for N in PELDANOS:
        s = a[a.N == N].set_index("slide")
        assert len(s) == 21 and s.index.is_unique, f"N={N}: {len(s)} filas"
        j = ESCALERA.index(N)
        carga = float(s.carga_mm2.mean())
        tot = None
        for g in GRADOS + ["total"]:
            sl = list(s.index) if g == "total" else list(s.index[s.grados == g])
            arr = [nulo[f"{x}__A_lamina_entera"] for x in sl]
            assert all(v.shape == (200, len(ESCALERA) + 1) for v in arr)
            nu = np.sum([v[:, j] for v in arr], axis=0)     # suma iteracion a iteracion
            alc = int(lam.loc[sl, "n_resueltas"].sum())
            rec = int(s.loc[sl, "recall"].sum())
            filas.append(dict(grupo=g, N=N, n_laminas=len(sl), alcanzables=alc, recall=rec,
                              pct_alcanzables=100.0 * rec / alc,
                              nulo_media=float(nu.mean()),
                              nulo_p975=float(np.percentile(nu, 97.5)),
                              pct_nulo_p975=100.0 * float(np.percentile(nu, 97.5)) / alc,
                              carga_media_mm2_lamina=carga))
    _verificar_o1(filas)
    return filas


def _verificar_o1(filas):
    idx = {(f["grupo"], f["N"]): f for f in filas}
    for g, n in PUB_ALCANZABLES.items():
        assert idx[(g, 500)]["alcanzables"] == n, (g, idx[(g, 500)]["alcanzables"])
    assert idx[("total", 500)]["alcanzables"] == 145
    for N, (rec, carga, med, p975) in PUB_O1_TOTAL.items():
        f = idx[("total", N)]
        got = (f["recall"], round(f["carga_media_mm2_lamina"], 2), round(f["nulo_media"], 2),
               f["nulo_p975"])
        assert got == (rec, carga, med, p975), f"§3 N={N}: {got} != {(rec, carga, med, p975)}"
    for N, recs in PUB_O1_GRADO.items():
        got = tuple(idx[(g, N)]["recall"] for g in GRADOS)
        assert got == recs, f"§4 N={N}: {got} != {recs}"
    print("O1: escalera.csv y nulo.npz reproducen resultados.md §3 y §4")


def figura_o1(filas):
    fig, ax = plt.subplots(figsize=(8.0, 4.8), dpi=DPI)
    fig.subplots_adjust(left=0.075, right=0.80, top=0.80, bottom=0.225)
    ax.set_xscale("log")
    ax.set_xlim(8, 2600)
    ax.set_ylim(0, 100)

    for y in (25, 50, 75, 100):
        ax.axhline(y, color=GRILLA, lw=0.6, zorder=0)
    ax.axvline(500, color=EJE, lw=0.8, zorder=0)

    por = {g: [f for f in filas if f["grupo"] == g] for g in GRADOS}
    # nulo primero y bajo primero, para que alto quede encima de todo
    for g in reversed(GRADOS):
        c = GRADO_COLOR[g]
        ax.plot(PELDANOS, [f["pct_nulo_p975"] for f in por[g]], color=c, lw=1.3,
                ls=(0, (4, 3)), zorder=2)
    for g in reversed(GRADOS):
        c = GRADO_COLOR[g]
        ax.plot(PELDANOS, [f["pct_alcanzables"] for f in por[g]], color=c, lw=2,
                marker="o", ms=6, mfc=c, mec=SUP, mew=1.2, zorder=3,
                solid_capstyle="round", solid_joinstyle="round")

    # etiqueta directa al final de cada linea (N=2000)
    for g in GRADOS:
        f = por[g][-1]
        ax.annotate(f"{g} · {f['recall']} de {f['alcanzables']}",
                    (PELDANOS[-1], f["pct_alcanzables"]), xytext=(9, 0),
                    textcoords="offset points", va="center", ha="left",
                    color=TINTA, fontsize=9.5, annotation_clip=False)

    # el titular, N=500, en bloque a la DERECHA de su linea: a la izquierda choca con la leyenda
    f5 = {g: next(f for f in por[g] if f["N"] == 500) for g in GRADOS}
    carga5 = f5["alto"]["carga_media_mm2_lamina"]
    bloque = [("N = 500", TINTA, "semibold"),
              (f"{coma(carga5, 2)} mm² por lámina", TINTA_2, "normal")]
    bloque += [(f"{g} {f5[g]['recall']} de {f5[g]['alcanzables']}", TINTA_2, "normal")
               for g in GRADOS]
    for k, (txt, col, peso) in enumerate(bloque):
        ax.text(545, 97 - 6 * k, txt, ha="left", va="top", color=col, fontsize=9,
                fontweight=peso)

    # eje x: N arriba, carga media por lamina abajo
    ax.xaxis.set_major_locator(FixedLocator(PELDANOS))
    ax.xaxis.set_minor_locator(NullLocator())
    ax.set_xticklabels([str(n) for n in PELDANOS])
    tr = blended_transform_factory(ax.transData, ax.transAxes)
    for f in por["alto"]:
        ax.text(f["N"], -0.105, coma(f["carga_media_mm2_lamina"], 2), transform=tr,
                ha="center", va="top", color=TENUE, fontsize=8.5)
    ax.text(0.5, -0.20, "N núcleos epiteliales más grandes de cada lámina  ·  debajo, "
            "la carga media que cubren, en mm² por lámina",
            transform=ax.transAxes, ha="center", va="top", color=TINTA_2, fontsize=9)

    ax.yaxis.set_major_locator(FixedLocator([0, 25, 50, 75, 100]))
    ax.set_yticklabels(["0", "25 %", "50 %", "75 %", "100 %"])
    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.tick_params(axis="x", length=3)

    h = [Line2D([], [], color=GRADO_COLOR[g], lw=2, marker="o", ms=6, mfc=GRADO_COLOR[g],
                mec=SUP, label=f"{g} ({PUB_ALCANZABLES[g]} alcanzables)") for g in GRADOS]
    h.append(Line2D([], [], color=TENUE, lw=1.3, ls=(0, (4, 3)),
                    label="p97,5 del nulo, en el color de su grado"))
    ax.legend(handles=h, loc="upper left", bbox_to_anchor=(0.0, 0.99), frameon=False,
              fontsize=8.5, labelcolor=TINTA_2, handlelength=2.4, borderaxespad=0.2)

    fig.text(0.075, 0.955, "O1 · El tamaño reencuentra las marcas de alto grado, no las de bajo",
             ha="left", va="top", color=TINTA, fontsize=12.5, fontweight="semibold")
    fig.text(0.075, 0.895, "% de las marcas alcanzables cuyo núcleo queda entre los N más "
             "grandes de su lámina · 21 láminas, lámina entera, descriptor percentil",
             ha="left", va="top", color=TINTA_2, fontsize=9)
    return fig


# --------------------------------------------------------------------------------------
# O3

TIERS = ["train", "val", "test", "fuera"]
TIER_TITULO = {"train": "train · entrenaron el fold",
               "val": "val · eligieron el checkpoint",
               "test": "test · el fold no la usó",
               "fuera": "ausente · fuera del split"}
# resultados.md §1.a, rama verdadera
PUB_O3 = {"110616": 0.775, "124729": 0.929, "124806": 0.925, "126504": 0.704,
          "128250": 0.745, "131461-1": 0.715, "132844": 0.755, "142541-1": 0.722,
          "164001": 0.926}
PUB_TIER = {"train": {"110616", "124729", "128250", "131461-1", "142541-1"},
            "val": {"124806", "132844", "164001"}, "test": {"126504"}}
PUB_TIER_P05 = {"train": 3, "val": 2, "test": 0}      # resultados.md §2
PUB_NO_ALINEADAS = {"164001", "B25-158899"}


def datos_o3():
    v = pd.read_csv(RES_O3 / "auc_cdis.csv", dtype={"slide": str})
    v = v[v.fuente == "ckpt_1fold_verdadera"].copy()
    v["universo"] = "lamina"
    r = pd.read_csv(RES_O3 / "auc_cdis_region.csv", dtype={"slide": str})
    # La B25-158899 no tiene fila en el CSV de labels: su rama es la `si`, que es la que el
    # fold predice, y se mide confinada a su region anotada (resultados.md §3.a-§3.b).
    r = r[(r.fuente == "ckpt_1fold_predicha") & (r.slide == "B25-158899")].copy()
    assert len(v) == 9 and len(r) == 1, (len(v), len(r))
    d = pd.concat([v, r[list(v.columns)]], ignore_index=True)
    d["alineada"] = [cargar_offset(s)[2] for s in d.slide]
    d["relleno"] = d.p_nulo < 0.05
    d["ic_lo_dibujado"] = d.ic95_lo.clip(0, 1)
    d["ic_hi_dibujado"] = d.ic95_hi.clip(0, 1)
    d["ic_recortado"] = (d.ic95_lo < 0) | (d.ic95_hi > 1)
    _verificar_o3(d)
    d["tier_orden"] = d.tier.map(TIERS.index)
    d = d.sort_values(["tier_orden", "auc"], ascending=[True, False]).reset_index(drop=True)
    d.insert(0, "orden_figura", np.arange(1, len(d) + 1))
    return d


def _verificar_o3(d):
    ver = d[d.fuente == "ckpt_1fold_verdadera"].set_index("slide")
    got = {s: round(float(a), 3) for s, a in ver.auc.items()}
    assert got == PUB_O3, f"§1.a: {got}"
    assert round(float(ver.auc.median()), 3) == 0.755
    assert round(float(ver.auc.min()), 3) == 0.704 and (ver.auc > 0.5).all()
    assert int(ver.relleno.sum()) == 5
    for t, sl in PUB_TIER.items():
        assert set(ver.index[ver.tier == t]) == sl, t
        assert int(ver.relleno[ver.tier == t].sum()) == PUB_TIER_P05[t], t
    b = d[d.slide == "B25-158899"].iloc[0]
    assert (b.tier, b.universo, int(b.n_parches), int(b.n_marcados)) == \
        ("fuera", "region", 2404, 7)
    assert (round(float(b.auc), 3), round(float(b.p_nulo), 3)) == (0.201, 0.995)
    assert set(d.slide[~d.alineada]) == PUB_NO_ALINEADAS, set(d.slide[~d.alineada])
    x = ver.loc["126504"]
    assert (round(float(x.ic95_lo), 3), round(float(x.ic95_hi), 3)) == (0.297, 1.111)
    print("O3: auc_cdis.csv y auc_cdis_region.csv reproducen resultados.md §1.a, §2 y §3.b")


def figura_o3(d):
    # filas: un encabezado por tier y debajo sus laminas
    filas, y = [], 0.0
    for t in TIERS:
        filas.append(("h", t, y)); y += 0.85
        for _, r in d[d.tier == t].iterrows():
            filas.append(("s", r, y)); y += 1.0
        y += 0.25
    y_max = y - 0.25

    fig, ax = plt.subplots(figsize=(8.0, 5.6), dpi=DPI)
    fig.subplots_adjust(left=0.30, right=0.86, top=0.835, bottom=0.155)
    ax.set_xlim(0, 1)
    ax.set_ylim(y_max, -0.75)

    for x in (0.25, 0.75, 1.0):
        ax.axvline(x, color=GRILLA, lw=0.6, zorder=0)
    ax.axvline(0.5, color=TENUE, lw=1.0, ls=(0, (3, 3)), zorder=1)
    ax.text(0.5, -0.75, "azar", ha="center", va="bottom", color=TENUE, fontsize=8.5)

    tr_fig = blended_transform_factory(fig.transFigure, ax.transData)
    tr_ax = blended_transform_factory(ax.transAxes, ax.transData)
    yt, yl = [], []
    for tipo, r, yy in filas:
        if tipo == "h":
            # Barlow no trae U+25CF: el punto va como marcador y no como glifo
            ax.plot([0.037], [yy], transform=tr_fig, ls="none", marker="o", ms=7,
                    mfc=TIER_COLOR[r], mec=TIER_COLOR[r], clip_on=False)
            fig.text(0.052, yy, TIER_TITULO[r], transform=tr_fig, ha="left", va="center",
                     color=TINTA, fontsize=9.5, fontweight="semibold")
            continue
        c = TIER_COLOR[r.tier]
        ax.plot([r.ic_lo_dibujado, r.ic_hi_dibujado], [yy, yy], color=c, lw=2,
                solid_capstyle="round", zorder=2)
        ax.plot(r.auc, yy, "o", ms=7.5, mfc=c if r.relleno else SUP, mec=c, mew=1.8,
                zorder=3)
        yt.append(yy)
        yl.append(r.slide + ("  †" if not r.alineada else ""))
        ax.text(1.035, yy, str(int(r.n_marcados)), transform=tr_ax, ha="left", va="center",
                color=TINTA_2, fontsize=9.5)
        if r.universo == "region":
            ax.text(-0.025, yy + 0.6, "rama si, región anotada", transform=tr_ax,
                    ha="right", va="center", color=TENUE, fontsize=8, fontstyle="italic")
    ax.text(1.035, -0.75, "parches\ncon CDIS", transform=tr_ax, ha="left", va="bottom",
            color=TENUE, fontsize=8.5, linespacing=1.0)

    ax.set_yticks(yt)
    ax.set_yticklabels(yl, fontsize=9.5)
    ax.tick_params(axis="y", length=0, pad=7)
    ax.xaxis.set_major_locator(FixedLocator([0, 0.25, 0.5, 0.75, 1.0]))
    ax.set_xticklabels(["0", "0,25", "0,5", "0,75", "1"])
    ax.tick_params(axis="x", length=3)
    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)
    ax.set_xlabel("AUC de la atención sobre los parches con CDIS dibujado (unidad: parche)",
                  color=TINTA_2, fontsize=9, labelpad=6)

    h = [Line2D([], [], ls="none", marker="o", ms=7.5, mfc=TINTA_2, mec=TINTA_2, mew=1.8,
                label="p < 0,05 (nulo por traslación)"),
         Line2D([], [], ls="none", marker="o", ms=7.5, mfc=SUP, mec=TINTA_2, mew=1.8,
                label="p ≥ 0,05"),
         Line2D([], [], color=TINTA_2, lw=2, label="IC 95 % Hanley-McNeil, recortado a [0, 1]")]
    fig.legend(handles=h, loc="lower left", bbox_to_anchor=(0.03, 0.005), ncol=3,
               frameon=False, fontsize=8.5, labelcolor=TINTA_2, handlelength=1.8,
               columnspacing=1.6)
    fig.text(0.97, 0.034, "† offset con alineada: false", ha="right", va="center",
             color=TINTA_2, fontsize=8.5)

    fig.text(0.03, 0.965, "O3 · La localización se sostiene en train y val; en láminas que "
             "el fold no usó, no está mostrada", ha="left", va="top", color=TINTA,
             fontsize=12.5, fontweight="semibold")
    fig.text(0.03, 0.915, "AUC por lámina con la rama de la clase verdadera, checkpoint de un "
             "fold · el «9 de 9 sobre 0,5», abierto por tier",
             ha="left", va="top", color=TINTA_2, fontsize=9)
    return fig


# --------------------------------------------------------------------------------------
# tablas para el doc de la reunion (se imprimen: el doc copia de aca, no de otra cuenta)

def tabla_o1(filas):
    idx = {(f["grupo"], f["N"]): f for f in filas}
    print("\n| N | mm²/lámina | alto (de 76) | moderado (de 53) | bajo (de 16) | "
          "total (de 145) | p97,5 del nulo, total |")
    print("|---|---|---|---|---|---|---|")
    for N in PELDANOS:
        c = [f"{idx[(g, N)]['recall']} ({coma(idx[(g, N)]['pct_alcanzables'], 1)} %)"
             for g in GRADOS + ["total"]]
        print(f"| {N} | {coma(idx[('total', N)]['carga_media_mm2_lamina'], 2)} | "
              + " | ".join(c) + f" | {int(idx[('total', N)]['nulo_p975'])} |")


def tabla_o3(d):
    print("\n| tier | lámina | parches con CDIS | AUC | IC 95 % | `p` |")
    print("|---|---|---|---|---|---|")
    for _, r in d.iterrows():
        nom = r.slide + (" †" if not r.alineada else "")
        print(f"| {r.tier if r.tier != 'fuera' else 'ausente'} | {nom} | {int(r.n_marcados)} | "
              f"{coma(r.auc, 3)} | {coma(r.ic95_lo, 3)} · {coma(r.ic95_hi, 3)} | "
              f"{coma(r.p_nulo, 3)} |")


def main():
    estilo()
    OUT.mkdir(parents=True, exist_ok=True)

    f1 = datos_o1()
    pd.DataFrame(f1).to_csv(OUT / "o1_apertura_grado.csv", index=False, float_format="%.4f")
    fig = figura_o1(f1)
    fig.savefig(OUT / "o1_apertura_grado.png", dpi=DPI)
    plt.close(fig)

    d3 = datos_o3()
    cols = ["orden_figura", "tier", "slide", "fuente", "rama", "universo", "etiqueta",
            "n_parches", "n_marcados", "auc", "ic95_lo", "ic95_hi", "ic_lo_dibujado",
            "ic_hi_dibujado", "ic_recortado", "p_nulo", "n_iter_nulo", "relleno", "alineada"]
    d3[cols].to_csv(OUT / "o3_auc_por_lamina.csv", index=False, float_format="%.4f")
    fig = figura_o3(d3)
    fig.savefig(OUT / "o3_auc_por_lamina.png", dpi=DPI)
    plt.close(fig)

    tabla_o1(f1)
    tabla_o3(d3)
    print(f"\nescrito: {OUT.relative_to(REPO)}/o1_apertura_grado.{{png,csv}}, "
          f"o3_auc_por_lamina.{{png,csv}}")


if __name__ == "__main__":
    main()
