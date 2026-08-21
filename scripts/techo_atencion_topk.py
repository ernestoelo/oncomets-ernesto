"""techo_atencion_topk.py — el TECHO de los brazos 2 y 3 de la fase 3, medible sin GPU.

Patron P2 del CLAUDE.md aplicado de frente: «un top-k se dimensiona por PERCENTIL, no por
AUC», y hay que **declarar el denominador alcanzable** antes de correr nada.

Que calcula
-----------
Para cada K del barrido de la fase 3, cuantos de los 28 parches con marca de Mitosis del
patologo caen dentro del top-K por atencion, confinado a la region anotada.

Por que es un TECHO y no un resultado del pipeline
--------------------------------------------------
Un parche que NO entra en la mascara top-K no puede ser recuperado por los brazos 2 y 3,
por bueno que sea HoVer-NeXt. Entonces esta curva **acota por arriba** el recall de esos dos
brazos, y lo hace **sin depender de la corrida de HoVer-NeXt**. El brazo 1 (sin mascara)
fija el otro techo, el de deteccion, y ese si exige la GPU.

  recall_fase3(K)  <=  min( techo_atencion(K) , deteccion_hovernext )

Lo que NO es
------------
- **No es el recall de la fase 3.** Es su cota superior. Un techo alto no promete nada; un
  techo bajo si condena.
- **No mide a HoVer-NeXt en absoluto.** No lo toca.
- Las marcas del patologo son **positivos parciales**: lo no marcado puede tener mitosis
  reales. El denominador 28 es «las marcadas», no «las que hay».

Uso:
  <clam_latest>/bin/python scripts/techo_atencion_topk.py
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]

# La lamina tiene DOS regiones de escaneo y las 163 marcas caen todas en la de abajo
# (region[1].y = 49920 segun openslide). Confinar es obligatorio: si una region recibiera
# mas atencion que la otra estariamos midiendo la region, no las marcas.
Y_CORTE_REGION = 49920

# El barrido de K del plan del 17-ago, fase 3.
KS = [20, 50, 100, 189, 300, 500, 750, 1000, 1392, 2000, 2496]


def cargar(npz_path: Path, csv_path: Path, mpp: float):
    z = np.load(npz_path)
    coords = z["coords_level0"]
    ps0 = float(z["patch_size_level0"])
    # Un brazo puede faltar (el gate de invasivo corre solo con Mammoth hasta que B3
    # entrene el CLAM plano). Se devuelve None y el que llama filtra; NO se rellena con
    # NaN, que se propagaria en silencio hasta la figura.
    a_clam = z["atencion_clam"] if "atencion_clam" in z else None
    a_mam = z["atencion_mammoth"] if "atencion_mammoth" in z else None

    ann = pd.read_csv(csv_path)
    # `clases` es multi-etiqueta separada por '|': un parche puede ser "Mitosis|Tumor".
    es_mit = ann["clases"].str.split("|").apply(lambda cs: any(c.strip() == "Mitosis" for c in cs))
    mit_xy = set(map(tuple, ann.loc[es_mit, ["x", "y"]].to_numpy().tolist()))

    area_parche_mm2 = (ps0 * mpp / 1000.0) ** 2
    return coords, ps0, a_clam, a_mam, mit_xy, area_parche_mm2


def techo(coords, atencion, idx_region, mit_idx, ks):
    """Para cada K: cuantos parches-mitosis entran en el top-K DENTRO de la region."""
    a_reg = atencion[idx_region]
    orden = idx_region[np.argsort(a_reg)[::-1]]          # indices globales, de mayor a menor
    filas = []
    for k in ks:
        k = min(k, len(orden))
        sel = set(orden[:k].tolist())
        cae = len(mit_idx & sel)
        filas.append((k, cae))
    return filas


def figura(df, denom, area_total, path):
    """La curva techo-vs-area: la forma que va a tener el entregable de la fase 3."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(7.4, 4.8))
    estilos = {"CLAM": ("#386271", "o", "-"), "Mammoth": ("#B85C38", "s", "-")}
    presentes = [b for b in estilos if (df.brazo == b).any()]
    for nombre in presentes:
        col, mk, ls = estilos[nombre]
        s = df[df.brazo == nombre].sort_values("area_mm2")
        ax.plot(s.area_mm2, s.techo_recall, ls, marker=mk, color=col,
                lw=1.9, ms=5, label=f"{nombre} (techo)")

    # la referencia sin informacion: top-K sorteado al azar dentro de la region
    s = df[df.brazo == presentes[0]].sort_values("area_mm2")
    ax.plot(s.area_mm2, s.esperado_al_azar / denom, ":", color="#999999", lw=1.6,
            label="azar (top-K sorteado)")

    ax.set_xlabel("area propuesta al patologo (mm²)")
    ax.set_ylabel(f"techo del recall de mitosis  (de {denom} marcas)")
    ax.set_title("Techo del filtro de atencion — 129741, region anotada\n"
                 "cota SUPERIOR de los brazos 2 y 3; no es el recall del pipeline",
                 fontsize=10.5)
    ax.set_ylim(-0.03, 1.05)
    ax.axhline(1.0, color="#cccccc", lw=0.8, zorder=0)
    ax.grid(alpha=0.25, lw=0.6)
    ax.legend(fontsize=9, loc="lower right")
    sec = ax.secondary_xaxis("top", functions=(lambda v: 100 * v / area_total,
                                               lambda p: p * area_total / 100))
    sec.set_xlabel("% de la region anotada", fontsize=9)
    plt.tight_layout()
    plt.savefig(path, dpi=200)
    plt.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--npz", default=str(
        REPO / "results/b8_hovernext_129741/interp/carcinoma_ductal_insitu_presente_ci_reform"
               "/129741/atencion_por_parche.npz"))
    ap.add_argument("--anotaciones", default=str(
        REPO / "sprints/B8_sprint8/anotaciones_patologo/parches_anotados_129741.csv"))
    ap.add_argument("--mpp", type=float, default=0.465)
    ap.add_argument("--out-dir", default=str(REPO / "results/b8_hovernext_129741/techo_atencion"))
    a = ap.parse_args()

    out = Path(a.out_dir); out.mkdir(parents=True, exist_ok=True)
    coords, ps0, a_clam, a_mam, mit_xy, area_mm2 = cargar(
        Path(a.npz), Path(a.anotaciones), a.mpp)

    n = len(coords)
    idx_region = np.where(coords[:, 1] >= Y_CORTE_REGION)[0]
    idx_arriba = np.where(coords[:, 1] < Y_CORTE_REGION)[0]

    # mapear las marcas a indices de parche del h5
    xy_a_idx = {(int(x), int(y)): i for i, (x, y) in enumerate(coords)}
    mit_idx, sin_casar = set(), []
    for xy in mit_xy:
        i = xy_a_idx.get(xy)
        (mit_idx.add(i) if i is not None else sin_casar.append(xy))

    print("=" * 74)
    print("TECHO DEL FILTRO DE ATENCION — cota superior de los brazos 2 y 3 de la fase 3")
    print("=" * 74)
    print(f"parches totales      : {n}")
    print(f"  region de arriba   : {len(idx_arriba)}   (sin anotaciones)")
    print(f"  region ANOTADA     : {len(idx_region)}   <- se confina aca")
    print(f"parches con Mitosis  : {len(mit_xy)} marcados, {len(mit_idx)} casados con el h5")
    if sin_casar:
        print(f"  !! {len(sin_casar)} marcas NO casaron: {sin_casar[:3]}")
    fuera = {i for i in mit_idx if i in set(idx_arriba.tolist())}
    print(f"  de ellos en la region anotada: {len(mit_idx) - len(fuera)}")
    print(f"area por parche      : {area_mm2:.6f} mm²  (ps0={ps0:.0f}px, mpp={a.mpp})")
    print(f"area region anotada  : {len(idx_region) * area_mm2:.2f} mm²")
    print("-" * 74)

    denom = len(mit_idx)
    brazos = [(nom, at) for nom, at in (("CLAM", a_clam), ("Mammoth", a_mam))
              if at is not None]
    if len(brazos) < 2:
        print(f"brazos presentes en el npz : {[b for b, _ in brazos]}")
    filas = []
    for nombre, at in brazos:
        for k, cae in techo(coords, at, idx_region, mit_idx, KS):
            # Referencia sin informacion: si el top-K se sorteara al azar dentro de la
            # region, cuantas marcas esperariamos. Es el punto de comparacion honesto.
            esperado_azar = denom * k / len(idx_region)
            filas.append(dict(
                brazo=nombre, K=k,
                area_mm2=round(k * area_mm2, 3),
                pct_region=round(100 * k / len(idx_region), 1),
                mitosis_en_mascara=cae,
                techo_recall=round(cae / denom, 4),
                esperado_al_azar=round(esperado_azar, 2),
                enriquecimiento=round(cae / esperado_azar, 2) if esperado_azar > 0 else float("nan"),
            ))

    df = pd.DataFrame(filas)
    df.to_csv(out / "techo_atencion_topk.csv", index=False)

    for nombre, _ in brazos:
        sub = df[df.brazo == nombre]
        print(f"\n{nombre}")
        print(f"{'K':>6} {'area mm²':>9} {'% region':>9} {'mitosis':>8} "
              f"{'techo':>7} {'azar':>6} {'enriq':>6}")
        for _, r in sub.iterrows():
            print(f"{r.K:>6} {r.area_mm2:>9.2f} {r.pct_region:>8.1f}% "
                  f"{r.mitosis_en_mascara:>4}/{denom:<3} {r.techo_recall:>7.3f} "
                  f"{r.esperado_al_azar:>6.2f} {r.enriquecimiento:>6.2f}")

    figura(df, denom, len(idx_region) * area_mm2, out / "techo_atencion_topk.png")

    meta = dict(
        que_es="cota superior del recall de mitosis de los brazos 2 y 3 de la fase 3",
        no_es=["el recall de la fase 3", "una medicion de HoVer-NeXt"],
        n_parches=int(n), n_region_anotada=int(len(idx_region)),
        n_mitosis_marcadas=len(mit_xy), n_mitosis_casadas=denom,
        area_parche_mm2=area_mm2, area_region_anotada_mm2=len(idx_region) * area_mm2,
        y_corte_region=Y_CORTE_REGION, patch_size_level0=ps0, mpp=a.mpp,
        ks=KS, brazos=[b for b, _ in brazos], fuente_atencion=str(a.npz),
    )
    (out / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    print(f"\nSalida: {out}")


if __name__ == "__main__":
    main()
