"""auc_atencion_fold4.py — AUC de ranking del par CLAM/Mammoth del fold 4 (fase 1, paso 6).

Cierra el paso 6 de la fase 1 del plan del 17-ago: «da el AUC de ranking de este checkpoint,
que NO es el mismo que el 0,890 ya medido». Sirve de referencia para dimensionar la fase 3.

Por que es un script APARTE y no un flag de `atencion_vs_anotaciones.py`
-----------------------------------------------------------------------
El `CKPTS` de aquel script fija la familia de checkpoints del **pre-registro** de
`sprints/B8_sprint8/atencion_vs_patologo/prereg.md` y no se toca despues de ver numeros.
Este par (CDIS `_ci_reform`, fold 4, job 4589) es de **otra tarea** y entra por otra puerta.
Lo que si se reusa —por import, no por copia— son sus estadisticos: `rank_auc`, `ranks_of`,
`p_permutacion` y el nulo honesto `p_traslacion`.

Y ademas es BARATO: la atencion por parche ya esta persistida en `atencion_por_parche.npz`
(la dejo `--dump-attention`), asi que no hay que reconstruir CLAM ni cargar pesos. CPU, segundos.

Que NO es
---------
- **No es el 0,890.** Aquel sale de 12 checkpoints de **tasa mitotica** de Sebastian; este es
  UN par de **CDIS `_ci_reform`**, fold 4. No son comparables como si fueran replicas.
- **No hay sd entre checkpoints**: es un solo par. La unica incertidumbre reportable aca es el
  IC de Hanley-McNeil, que es la grande igual ([[auc-atencion-dos-incertidumbres]]).
- Los positivos son **parciales**: el sesgo empuja el AUC hacia 0,5, o sea es conservador.

Uso (workaround B — binario absoluto):
  CUDA_VISIBLE_DEVICES="" /home/sdonoso/miniconda3/envs/clam_latest/bin/python \
      scripts/auc_atencion_fold4.py
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.atencion_vs_anotaciones import (  # noqa: E402  (reuso, no copia)
    p_permutacion, p_traslacion, rank_auc, ranks_of,
)

# Misma frontera de region de escaneo que usa todo el hilo de esta lamina.
Y_CORTE_REGION = 49920

# Grupos para los que vale la pena pagar los nulos (el resto solo lleva AUC + IC).
GRUPOS_CON_NULO = ["Mitosis", "Nucleos alto grado", "Tumor"]


def ic_hanley_mcneil(auc: float, n_pos: int, n_neg: int, z: float = 1.96):
    """IC del AUC por Hanley y McNeil (1982). Varia LO QUE EL PATOLOGO MARCO, con el modelo fijo.

    Es la incertidumbre grande cuando el grupo tiene n chico, y es la unica reportable acá
    porque hay un solo par de checkpoints (no hay sd entre modelos que promediar).
    """
    if not np.isfinite(auc) or n_pos < 2 or n_neg < 2:
        return float("nan"), float("nan"), float("nan")
    q1 = auc / (2.0 - auc)
    q2 = 2.0 * auc * auc / (1.0 + auc)
    var = (auc * (1 - auc)
           + (n_pos - 1) * (q1 - auc ** 2)
           + (n_neg - 1) * (q2 - auc ** 2)) / (n_pos * n_neg)
    ee = float(np.sqrt(max(var, 0.0)))
    return ee, float(auc - z * ee), float(auc + z * ee)


def figura(df, universo, path, clase_verdadera, titulo):
    """Forest plot: AUC por grupo con el ANCHO de su IC a la vista.

    Es deliberado que no sean barras. Siete barras del mismo grosor sugieren siete numeros
    de la misma calidad, y aca el IC va de 0.05 (tejido adiposo) a 0.27 (nucleos alto grado)
    — [[auc-atencion-dos-incertidumbres]]. Con el IT dibujado, «estroma queda en el azar»
    se lee como lo que es: una ausencia de dato, no un dato.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    sub = df[df.es_cabeza_verdadera & (df.universo == universo)]
    presentes = [b for b in ("CLAM", "Mammoth") if (sub.brazo == b).any()]
    orden = (sub[sub.brazo == presentes[-1]].sort_values("auc_ranking", ascending=False)
             .grupo.tolist())
    col = {"CLAM": "#386271", "Mammoth": "#B85C38"}
    off = ({"CLAM": -0.17, "Mammoth": 0.17} if len(presentes) > 1
           else {presentes[0]: 0.0})

    fig, ax = plt.subplots(figsize=(7.8, 4.6))
    ax.axvline(0.5, color="#888888", lw=1.1, ls="--", zorder=1)
    for gi, g in enumerate(orden):
        for brazo in presentes:
            r = sub[(sub.grupo == g) & (sub.brazo == brazo)].iloc[0]
            y = len(orden) - 1 - gi + off[brazo]
            ax.plot([r.ic95_lo, r.ic95_hi], [y, y], "-", color=col[brazo], lw=2.0, alpha=.85)
            ax.plot([r.auc_ranking], [y], "o", color=col[brazo], ms=6.5,
                    label=brazo if gi == 0 else None)
    ax.set_yticks(range(len(orden)))
    ax.set_yticklabels([f"{g}  (n={int(sub[sub.grupo == g].n_parches.iloc[0])})"
                        for g in orden][::-1], fontsize=9)
    ax.set_xlabel("AUC de ranking de la atencion  (nulo 0.5; barra = IC 95 % de Hanley-McNeil)")
    ax.set_title(f"{titulo}\n"
                 f"cabeza de la clase verdadera '{clase_verdadera}'; universo = {universo}",
                 fontsize=10.5)
    ax.set_xlim(-0.02, 1.02)
    ax.grid(axis="x", alpha=0.25, lw=0.6)
    ax.legend(fontsize=9, loc="lower right")
    plt.tight_layout()
    plt.savefig(path, dpi=200)
    plt.close()


def paso_de_grilla(coords: np.ndarray) -> int:
    """Moda del paso entre coords contiguas — NUNCA desde la magnificacion
    ([[patch-size-desde-geometria-h5]])."""
    diffs = []
    for y in np.unique(coords[:, 1])[:400]:
        xs = np.sort(coords[coords[:, 1] == y][:, 0])
        d = np.diff(xs)
        diffs += d[d > 0].tolist()
    return int(Counter(diffs).most_common(1)[0][0])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--npz", default=str(
        REPO / "results/b8_hovernext_129741/interp/carcinoma_ductal_insitu_presente_ci_reform"
               "/129741/atencion_por_parche.npz"))
    ap.add_argument("--anotaciones", default=str(
        REPO / "sprints/B8_sprint8/anotaciones_patologo/parches_anotados_129741.csv"))
    ap.add_argument("--out-dir", default=str(
        REPO / "results/b8_hovernext_129741/auc_fold4"))
    ap.add_argument("--clases", default="no,si", help="orden de --auto-label-dict")
    # La tarea deja de estar cableada: el encargo 1 corre el MISMO analisis sobre el gate
    # de invasivo. Los defaults reproducen la corrida del fold 4 tal cual.
    ap.add_argument("--tarea", default="carcinoma_ductal_insitu_presente_ci_reform")
    ap.add_argument("--fold", type=int, default=4)
    ap.add_argument("--job-origen", default="4589")
    ap.add_argument("--prefijo", default="auc_atencion_fold4",
                    help="prefijo de los PNG y del CSV; distinto por tarea para no pisar")
    ap.add_argument("--titulo", default="129741 — atencion vs marcas del patologo, "
                                        "par del fold 4 (CDIS `_ci_reform`)")
    ap.add_argument("--n-perm", type=int, default=2000)
    ap.add_argument("--n-transl", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--from-csv", action="store_true",
                    help="reusa el CSV ya calculado y solo rehace las figuras (los nulos "
                         "por traslacion son lo caro y no cambian con la seed fija)")
    a = ap.parse_args()

    out = Path(a.out_dir); out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(a.seed)
    clases = [c.strip() for c in a.clases.split(",")]

    z = np.load(a.npz)
    coords = z["coords_level0"].astype(np.int64)
    N = len(coords)
    # Un brazo puede faltar: el gate de invasivo solo tiene Mammoth hasta que B3 entrene
    # el CLAM plano. Se mide con el que hay.
    brazos = {nom: z[k] for nom, k in (("CLAM", "atencion_clam_todas"),
                                       ("Mammoth", "atencion_mammoth_todas")) if k in z}
    if not brazos:
        raise ValueError(f"{a.npz}: no trae ningun brazo de atencion")
    i_true = int(z["clase_rama"])          # la cabeza de la clase verdadera ("si")
    step = paso_de_grilla(coords)

    ann = pd.read_csv(a.anotaciones)
    idx_of = {(int(x), int(y)): i for i, (x, y) in enumerate(coords)}
    ann["idx"] = [idx_of.get((int(r.x), int(r.y))) for r in ann.itertuples()]
    if ann["idx"].isna().any():
        raise ValueError(f"{int(ann['idx'].isna().sum())} parches anotados no estan en el h5")
    ann["idx"] = ann["idx"].astype(int)

    # Un parche puede llevar varias clases ('Mitosis|Tumor'): cuenta en los dos grupos.
    grupos = {}
    for r in ann.itertuples():
        for c in str(r.clases).split("|"):
            grupos.setdefault(c.strip(), []).append(r.idx)
    grupos = {k: np.array(sorted(set(v))) for k, v in grupos.items()}

    universos = {"lamina": np.arange(N)}
    y_ann = coords[ann["idx"].values, 1]
    if bool((y_ann >= Y_CORTE_REGION).all()):
        universos["region_anotada"] = np.where(coords[:, 1] >= Y_CORTE_REGION)[0]
    else:
        print(f"[warn] las anotaciones NO caen todas bajo y={Y_CORTE_REGION}: sin confinar")

    print("=" * 78)
    print("AUC DE RANKING — par CLAM/Mammoth del fold 4, CDIS `_ci_reform` (job 4589)")
    print("=" * 78)
    print(f"parches {N} | paso de grilla {step} px | cabeza verdadera = '{clases[i_true]}'")
    for k, v in universos.items():
        print(f"  universo {k:16s} n={len(v)}")
    for k in sorted(grupos, key=lambda g: -len(grupos[g])):
        print(f"  grupo    {k:22s} n={len(grupos[k])}")

    csv_path = out / f"{a.prefijo}.csv"
    filas = []
    for brazo, A in ({} if a.from_csv else brazos).items():
        for ci, cname in enumerate(clases):
            scores = A[ci]
            for uname, uidx in universos.items():
                # Los rangos se recalculan DENTRO del universo: usar los de la lamina
                # entera volveria a meter la region no anotada por la ventana.
                u_ranks = ranks_of(scores[uidx])
                u_n = len(uidx)
                u_pct = 100.0 * (u_ranks - 1) / (u_n - 1)
                for g, idx in grupos.items():
                    gi = idx if uname == "lamina" else np.searchsorted(uidx, idx)
                    auc = rank_auc(u_ranks, gi, n_total=u_n)
                    ee, lo, hi = ic_hanley_mcneil(auc, len(idx), u_n - len(idx))

                    pp = pt = nacc = nmean = float("nan")
                    if ci == i_true and g in GRUPOS_CON_NULO:
                        pp, _ = p_permutacion(u_ranks, gi, a.n_perm, rng)
                        sub = np.empty(N); sub[uidx] = u_ranks
                        pt, _, nacc, nmean = p_traslacion(
                            sub, coords, idx, step, a.n_transl, rng, universo=uidx)

                    filas.append(dict(
                        brazo=brazo, cabeza=cname, es_cabeza_verdadera=(ci == i_true),
                        universo=uname, n_universo=u_n,
                        grupo=g, n_parches=len(idx),
                        auc_ranking=round(auc, 4),
                        ee_hanley=round(ee, 4),
                        ic95_lo=round(lo, 4), ic95_hi=round(hi, 4),
                        ancho_ic=round(hi - lo, 4),
                        percentil_mediano=round(float(np.median(u_pct[gi])), 2),
                        p_permutacion=pp, p_traslacion=pt,
                        n_traslaciones=nacc, auc_nula_media=nmean))

    if a.from_csv:
        df = pd.read_csv(csv_path)
    else:
        df = pd.DataFrame(filas)
        df.to_csv(csv_path, index=False)

    for uname in universos:
        figura(df, uname, out / f"{a.prefijo}_{uname}.png", clases[i_true], a.titulo)

    for uname in universos:
        print("\n" + "-" * 78)
        print(f"universo = {uname}   (cabeza de la clase verdadera '{clases[i_true]}')")
        print("-" * 78)
        print(f"{'grupo':22s} {'n':>4} {'brazo':>8} {'AUC':>7} {'IC 95 %':>16} "
              f"{'pct med':>8} {'p_trasl':>8}")
        sub = df[df.es_cabeza_verdadera & (df.universo == uname)]
        primero = list(brazos)[0]     # el rotulo va en la 1a fila del grupo, sea cual sea
        for g in sorted(grupos, key=lambda k: -df[(df.grupo == k)].auc_ranking.max()):
            for brazo in brazos:
                r = sub[(sub.grupo == g) & (sub.brazo == brazo)].iloc[0]
                pt = "     -  " if not np.isfinite(r.p_traslacion) else f"{r.p_traslacion:>8.4f}"
                print(f"{g if brazo==primero else '':22s} "
                      f"{r.n_parches if brazo==primero else '':>4} {brazo:>8} "
                      f"{r.auc_ranking:>7.3f} {r.ic95_lo:>7.3f}–{r.ic95_hi:<8.3f} "
                      f"{r.percentil_mediano:>7.1f}% {pt}")

    meta = dict(
        que_es=f"AUC de ranking atencion-vs-marcas, brazos {list(brazos)}, "
               f"fold {a.fold}",
        tarea=a.tarea, fold=a.fold, job_origen=a.job_origen, brazos=list(brazos),
        no_es=["el 0.890 de atencion_vs_patologo (esos son 12 ckpt de tasa mitotica)",
               "una medida con sd entre checkpoints (aca hay UN par)"],
        clases=clases, cabeza_verdadera=clases[i_true],
        n_parches=int(N), paso_grilla=int(step), y_corte_region=Y_CORTE_REGION,
        universos={k: int(len(v)) for k, v in universos.items()},
        grupos={k: int(len(v)) for k, v in grupos.items()},
        seed=a.seed, n_perm=a.n_perm, n_transl=a.n_transl, fuente_atencion=str(a.npz),
    )
    (out / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    print(f"\n[out] {csv_path}  ({len(df)} filas)")


if __name__ == "__main__":
    main()
