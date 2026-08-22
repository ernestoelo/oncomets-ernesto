"""escalera_brazos.py — A2.bis: la escalera de brazos, recall contra CARGA DE REVISION.

Pedido de Ernesto (21-ago). Hasta ahora HoVer-NeXt se leyo contra si mismo. Falta la
pregunta anterior: **¿el detector agrega algo sobre la atencion sola?** Para contestarla el
brazo de atencion pura deja de ser «el techo» y pasa a ser **la linea base contra la que se
lee todo**.

Por que hace falta un eje y no basta una columna
------------------------------------------------
Comparar los brazos por recall a secas dice que HoVer-NeXt **empeora** (19/26 -> 11/26 en
K=300), y eso es un artefacto de mirar una sola columna: el detector baja el recall **y**
cambia la unidad de lo que hay que revisar. Se grafica recall contra carga, con la carga en
**dos unidades y las dos declaradas**:

- **area (mm²)** — la superficie que se le pone delante al patologo;
- **objetos a mirar** — parches en los brazos de atencion, **nucleos puntuales** en los que
  llevan HoVer-NeXt.

Ahi es donde el detector puede ganar aunque su recall sea menor, y es exactamente la
pregunta de Sebastian sobre cuanta superficie ponerle delante al patologo (P2.a.ter: el
recorte compra area, no marcas).

Convenciones declaradas (si se cambian, cambia la figura)
--------------------------------------------------------
1. **La unidad del recall son MARCAS** (26 en la 129741), no parches (28) ni detecciones
   (177). Es la unidad de la pregunta ([[techo-filtro-antes-de-correr]] ADDENDUM).
2. **Area de un brazo de atencion** = (nº de parches de la mascara) × area del parche. Para
   la interseccion y la union la mascara NO mide K: mide lo que mide, y por eso se computa
   su tamaño real.
3. **Area de un brazo con HoVer-NeXt** = (nº de detecciones que el patologo mira) × area de
   una **ventana de inspeccion de 128 px** de lado (≈59,5 µm, la misma de la galeria del
   encargo 2: da contexto alrededor de una figura mitotica de 10-20 µm). Es una
   **convencion**, no una medida: un nucleo es un punto y no tiene area propia. Se declara
   acá y en la figura.
4. **Azar** = top-K sorteado dentro de la region. No se simula: por linealidad de la
   esperanza, E[marcas capturadas] = n_marcas_region × K/n_parches_region, exacto aunque dos
   marcas compartan parche.

Lo que NO es
------------
- **No se calcula precision** contra el geojson y **nada se llama falso positivo**: las
  marcas son positivos parciales.
- El denominador son **las marcadas**, no las mitosis que hay en la lamina.
- Mammoth **no se suma a CLAM, lo reemplaza** (es CLAM con la 1ª capa cambiada): son brazos
  **alternativos**. Lo que si es un brazo nuevo es combinar las dos mascaras.

Uso:
  <clam_latest>/bin/python scripts/escalera_brazos.py            # CDIS fold 4
  <clam_latest>/bin/python scripts/escalera_brazos.py --npz ... --out-dir ...   # gate
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
from cruce_hovernext_marcas import marcas_mitosis, emparejar          # noqa: E402
from techo_atencion_topk import cargar, Y_CORTE_REGION, KS            # noqa: E402

TOL_UM = 30.0          # la adoptada por el cruce; el recall es plano de 7,5 a 75 µm
VENTANA_PX = 128       # lado de la ventana de inspeccion por deteccion (convencion 3)


def mascara_topk(atencion, idx_region, k):
    """Indices globales de los K parches mas atendidos DENTRO de la region."""
    a_reg = atencion[idx_region]
    orden = idx_region[np.argsort(a_reg)[::-1]]
    return set(orden[: min(k, len(orden))].tolist())



def figura(df, n_marcas, ok_det_n, area_region, etiqueta, path):
    """Recall vs carga, en las DOS unidades. Paneles separados a proposito.

    OJO con el eje de objetos: un «objeto» NO es lo mismo en las dos familias de brazos
    (un parche de 256 px mide 119 µm de lado; un nucleo es un punto). Por eso los brazos de
    parches y los de nucleos van con marcador distinto y el caption lo dice. Mezclar las
    unidades sin decirlo es justo lo que las reglas del sprint prohiben.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    estilos = {
        "CLAM":                    ("#386271", "o", "-",  2.0),
        "Mammoth":                 ("#B85C38", "s", "-",  2.0),
        "CLAM\u2229Mammoth":            ("#6A8D73", "^", "-",  1.6),
        "CLAM\u222aMammoth":            ("#9B6A9B", "v", "-",  1.6),
        "CLAM+HoVer-NeXt":         ("#386271", "o", "--", 1.6),
        "Mammoth+HoVer-NeXt":      ("#B85C38", "s", "--", 1.6),
    }
    fig, axes = plt.subplots(1, 2, figsize=(12.6, 5.2))
    for ax, xcol, xlab in ((axes[0], "objetos_a_mirar", "objetos a mirar  (parches \u25cf / n\u00facleos \u25c7)"),
                           (axes[1], "area_mm2", "\u00e1rea propuesta al pat\u00f3logo (mm\u00b2)")):
        for nom, (col, mk, ls, lw) in estilos.items():
            s_ = df[(df.brazo == nom) & (df.K > 0)].sort_values(xcol)
            if not len(s_):
                continue
            hueco = "none" if "HoVer-NeXt" in nom else col
            ax.plot(s_[xcol], s_.recall, ls, marker=mk, color=col, lw=lw, ms=5.5,
                    markerfacecolor=hueco, label=nom)
        s_ = df[(df.brazo == "azar") & (df.K > 0)].sort_values(xcol)
        ax.plot(s_[xcol], s_.recall, ":", color="#999999", lw=1.6, label="azar")
        r = df[df.brazo == "HoVer-NeXt"]
        if len(r):
            ax.plot(r[xcol], r.recall, "*", color="#C1121F", ms=17, ls="none",
                    label="HoVer-NeXt solo (sin m\u00e1scara)", zorder=6)
        ax.axhline(ok_det_n / n_marcas, color="#C1121F", lw=0.9, ls=":", zorder=0)
        ax.text(0.985, ok_det_n / n_marcas + 0.018,
                f"techo de la detecci\u00f3n: {ok_det_n}/{n_marcas}", color="#C1121F",
                fontsize=8.4, ha="right", va="bottom",
                transform=ax.get_yaxis_transform())
        ax.set_xscale("log")
        ax.set_xlabel(xlab, fontsize=9.5)
        ax.set_ylim(-0.03, 1.06)
        ax.grid(alpha=0.25, lw=0.6)
    axes[0].set_ylabel(f"recall  (de {n_marcas} marcas del pat\u00f3logo)", fontsize=9.5)
    axes[0].legend(fontsize=8, loc="upper left", framealpha=0.92)
    fig.suptitle(f"Recall contra carga de revisi\u00f3n \u2014 129741, {etiqueta}\n"
                 f"un «objeto» no es lo mismo en las dos familias: parche de 256 px (119 \u00b5m de lado) "
                 f"vs n\u00facleo puntual; el \u00e1rea de un n\u00facleo es una CONVENCI\u00d3N (ventana de {VENTANA_PX} px)",
                 fontsize=10)
    plt.tight_layout(rect=(0, 0, 1, 0.93))
    plt.savefig(path, dpi=200)
    plt.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--geojson", default="/media/administrador/Storage1/sdonoso/hover_net/"
                                         "129741.bif - GDT.geojson")
    ap.add_argument("--tsv", default=str(REPO / "results/b8_hovernext_129741/hovernext/"
                                                "lizard_mitosis/129741/pred_mitosis.tsv"))
    ap.add_argument("--offset", default=str(REPO / "sprints/B8_sprint8/anotaciones_patologo/"
                                                   "offset_129741.json"))
    ap.add_argument("--npz", default=str(REPO / "results/b8_hovernext_129741/interp/"
                                                "carcinoma_ductal_insitu_presente_ci_reform/"
                                                "129741/atencion_por_parche.npz"))
    ap.add_argument("--anotaciones", default=str(REPO / "sprints/B8_sprint8/"
                                                        "anotaciones_patologo/"
                                                        "parches_anotados_129741.csv"))
    ap.add_argument("--mpp", type=float, default=0.465)
    ap.add_argument("--etiqueta", default="CDIS fold 4",
                    help="como se llama esta tarea en la figura")
    ap.add_argument("--out-dir",
                    default=str(REPO / "results/b8_hovernext_129741/escalera_brazos"))
    a = ap.parse_args()

    import pandas as pd                                                    # noqa: E402

    out = Path(a.out_dir); out.mkdir(parents=True, exist_ok=True)
    off = json.loads(Path(a.offset).read_text())
    mpp = a.mpp

    # ---------------- insumos ----------------
    marcas, _ = marcas_mitosis(a.geojson, off["dx"], off["dy"])
    det = np.asarray([[float(r["x"]), float(r["y"])]
                      for r in csv.DictReader(open(a.tsv), delimiter="\t")])
    coords, ps0, a_clam, a_mam, _, area_parche_mm2 = cargar(Path(a.npz),
                                                            Path(a.anotaciones), mpp)
    idx_region = np.where(coords[:, 1] >= Y_CORTE_REGION)[0]
    n_reg = len(idx_region)

    # deteccion uno a uno (hungaro), la misma del cruce
    dist = np.linalg.norm(marcas[:, None, :] - det[None, :, :], axis=2)
    ok_det = emparejar(dist, TOL_UM / mpp)          # marca -> la detecto HoVer-NeXt

    # cada marca -> el parche del h5 que la contiene (unidad comun de los dos factores)
    parche_de = np.full(len(marcas), -1, dtype=int)
    for i, (mx, my) in enumerate(marcas):
        w = np.where((coords[:, 0] <= mx) & (mx < coords[:, 0] + ps0) &
                     (coords[:, 1] <= my) & (my < coords[:, 1] + ps0))[0]
        if len(w):
            parche_de[i] = w[0]

    # cada deteccion -> su parche (para contar cuantas caen dentro de una mascara)
    parche_det = np.full(len(det), -1, dtype=int)
    for j, (dx_, dy_) in enumerate(det):
        w = np.where((coords[:, 0] <= dx_) & (dx_ < coords[:, 0] + ps0) &
                     (coords[:, 1] <= dy_) & (dy_ < coords[:, 1] + ps0))[0]
        if len(w):
            parche_det[j] = w[0]

    en_region_marca = marcas[:, 1] >= Y_CORTE_REGION
    en_region_det = det[:, 1] >= Y_CORTE_REGION
    area_ventana_mm2 = (VENTANA_PX * mpp / 1000.0) ** 2
    n_marcas = len(marcas)

    print("=" * 78)
    print(f"ESCALERA DE BRAZOS — 129741, {a.etiqueta}")
    print("=" * 78)
    print(f"marcas de Mitosis            : {n_marcas}  ({en_region_marca.sum()} en la region)")
    print(f"detecciones HoVer-NeXt       : {len(det)}  ({en_region_det.sum()} en la region)")
    print(f"parches de la region anotada : {n_reg}   area total "
          f"{n_reg*area_parche_mm2:.2f} mm²")
    print(f"marcas detectadas (30 µm)    : {ok_det.sum()}/{n_marcas}")
    print(f"\nconvencion de area de un nucleo: ventana de {VENTANA_PX} px "
          f"= {VENTANA_PX*mpp:.1f} µm de lado = {area_ventana_mm2*1e6:.0f} µm² "
          f"({area_ventana_mm2:.5f} mm²)")

    # ---------------- brazos de mascara ----------------
    disponibles = [(n, at) for n, at in (("CLAM", a_clam), ("Mammoth", a_mam))
                   if at is not None]
    print(f"brazos de atencion en el npz : {[n for n, _ in disponibles]}")

    filas = []

    def agrega(brazo, k, sel, tipo):
        """sel = set de indices de parche de la mascara (None = sin mascara)."""
        if sel is None:                                   # HoVer-NeXt solo
            en_masc = np.ones(n_marcas, bool)
            n_parches = n_reg
            det_vistas = int(en_region_det.sum())
        else:
            en_masc = np.array([p >= 0 and p in sel for p in parche_de])
            n_parches = len(sel)
            det_vistas = int(sum(1 for j in range(len(det))
                                 if parche_det[j] >= 0 and parche_det[j] in sel))
        lleva_det = tipo.endswith("+HoVer-NeXt") or tipo == "HoVer-NeXt"
        recup = (en_masc & ok_det) if lleva_det else en_masc
        if lleva_det:
            objetos, area = det_vistas, det_vistas * area_ventana_mm2
            unidad = "nucleos"
        else:
            objetos, area = n_parches, n_parches * area_parche_mm2
            unidad = "parches"
        filas.append(dict(
            brazo=brazo, tipo=tipo, K=k, n_parches_mascara=n_parches,
            objetos_a_mirar=objetos, unidad_objetos=unidad,
            area_mm2=round(area, 4), pct_region=round(100 * n_parches / n_reg, 2),
            marcas_recuperadas=int(recup.sum()), n_marcas=n_marcas,
            recall=round(float(recup.sum()) / n_marcas, 4)))

    for k in KS:
        masc = {n: mascara_topk(at, idx_region, k) for n, at in disponibles}
        for n, sel in masc.items():
            agrega(n, k, sel, n)                                  # atencion sola
            agrega(f"{n}+HoVer-NeXt", k, sel, f"{n}+HoVer-NeXt")  # atencion x deteccion
        if len(masc) == 2:
            inter = masc["CLAM"] & masc["Mammoth"]
            union = masc["CLAM"] | masc["Mammoth"]
            agrega("CLAM∩Mammoth", k, inter, "CLAM∩Mammoth")
            agrega("CLAM∪Mammoth", k, union, "CLAM∪Mammoth")
            agrega("CLAM∩Mammoth+HoVer-NeXt", k, inter, "CLAM∩Mammoth+HoVer-NeXt")
            agrega("CLAM∪Mammoth+HoVer-NeXt", k, union, "CLAM∪Mammoth+HoVer-NeXt")
        # azar: esperanza exacta por linealidad, no simulacion (convencion 4)
        p = min(k, n_reg) / n_reg
        filas.append(dict(
            brazo="azar", tipo="azar", K=min(k, n_reg), n_parches_mascara=min(k, n_reg),
            objetos_a_mirar=min(k, n_reg), unidad_objetos="parches",
            area_mm2=round(min(k, n_reg) * area_parche_mm2, 4),
            pct_region=round(100 * min(k, n_reg) / n_reg, 2),
            marcas_recuperadas=round(float(en_region_marca.sum()) * p, 2), n_marcas=n_marcas,
            recall=round(float(en_region_marca.sum()) * p / n_marcas, 4)))
        filas.append(dict(
            brazo="azar+HoVer-NeXt", tipo="azar+HoVer-NeXt", K=min(k, n_reg),
            n_parches_mascara=min(k, n_reg),
            objetos_a_mirar=round(float(en_region_det.sum()) * p, 1), unidad_objetos="nucleos",
            area_mm2=round(float(en_region_det.sum()) * p * area_ventana_mm2, 4),
            pct_region=round(100 * min(k, n_reg) / n_reg, 2),
            marcas_recuperadas=round(float((ok_det & en_region_marca).sum()) * p, 2),
            n_marcas=n_marcas,
            recall=round(float((ok_det & en_region_marca).sum()) * p / n_marcas, 4)))

    # HoVer-NeXt solo: no depende de K, se agrega una vez
    agrega("HoVer-NeXt", -1, None, "HoVer-NeXt")

    df = pd.DataFrame(filas)
    df.to_csv(out / "escalera_brazos.csv", index=False)

    # ---------------- el chequeo de sanidad del plan ----------------
    print("\n" + "=" * 78)
    print("CHEQUEO DE SANIDAD (si esto no cierra, el eje esta mal construido)")
    print("=" * 78)
    fin = df[df.K == min(KS[-1], n_reg)]
    okk = True
    for _, r in fin.iterrows():
        esp = ok_det.sum() if "HoVer-NeXt" in str(r.brazo) else n_marcas
        if r.brazo.startswith("azar"):
            continue
        bien = int(round(r.marcas_recuperadas)) == esp
        okk &= bien
        print(f"  K=region entera  {r.brazo:26s} {int(r.marcas_recuperadas):>3}/{n_marcas}"
              f"   esperado {esp}   {'OK' if bien else '<<< NO CIERRA'}")
    az = fin[fin.brazo == "azar"]
    if len(az):
        print(f"  K=region entera  {'azar':26s} {float(az.iloc[0].marcas_recuperadas):>5.1f}"
              f"/{n_marcas}   converge al mismo punto que los de atencion "
              f"(las {int(en_region_marca.sum())} de la region)")
    print(f"\n  veredicto: {'CIERRA' if okk else 'NO CIERRA — revisar el enmascarado'}")

    # ---------------- la tabla que va al documento ----------------
    print("\n" + "=" * 78)
    print(f"RECALL vs CARGA DE REVISION  (denominador = {n_marcas} marcas)")
    print("=" * 78)
    print(f"  {'brazo':26s} {'K':>5} {'objetos':>9} {'unidad':>8} {'area mm²':>9} {'recall':>12}")
    for k in [100, 189, 300, 500]:
        print(f"  --- K = {k} " + "-" * 58)
        for _, r in df[df.K == k].sort_values("recall", ascending=False).iterrows():
            print(f"  {r.brazo:26s} {int(r.K):>5} {float(r.objetos_a_mirar):>9.0f} "
                  f"{r.unidad_objetos:>8} {r.area_mm2:>9.2f} "
                  f"{float(r.marcas_recuperadas):>6.1f}/{n_marcas:<3} {r.recall:>5.1%}")
    r = df[df.brazo == "HoVer-NeXt"].iloc[0]
    print(f"  --- sin mascara " + "-" * 55)
    print(f"  {r.brazo:26s} {'—':>5} {float(r.objetos_a_mirar):>9.0f} {r.unidad_objetos:>8} "
          f"{r.area_mm2:>9.2f} {float(r.marcas_recuperadas):>6.1f}/{n_marcas:<3} {r.recall:>5.1%}")

    meta = dict(
        que_es="A2.bis — recall contra carga de revision, por brazo",
        unidad_del_recall="marcas del patologo (no parches, no detecciones)",
        n_marcas=int(n_marcas), n_marcas_region=int(en_region_marca.sum()),
        n_detecciones=int(len(det)), n_detecciones_region=int(en_region_det.sum()),
        marcas_detectadas=int(ok_det.sum()),
        convencion_area_nucleo=dict(ventana_px=VENTANA_PX,
                                    lado_um=round(VENTANA_PX * mpp, 1),
                                    area_mm2=round(area_ventana_mm2, 6),
                                    aclaracion="convencion, no medida: un nucleo es un punto"),
        area_parche_mm2=round(area_parche_mm2, 6),
        n_parches_region=int(n_reg), area_region_mm2=round(n_reg * area_parche_mm2, 3),
        brazos_de_atencion=[n for n, _ in disponibles],
        tolerancia_um=TOL_UM, y_corte_region=Y_CORTE_REGION, mpp=mpp,
        etiqueta=a.etiqueta, chequeo_sanidad="CIERRA" if okk else "NO CIERRA",
        no_es=["precision de HoVer-NeXt", "un recall sobre las mitosis que HAY",
               "una comparacion CLAM-vs-Mammoth de rendimiento"],
        fuente_atencion=str(a.npz), fuente_detecciones=str(a.tsv),
    )
    figura(df, n_marcas, int(ok_det.sum()), n_reg * area_parche_mm2, a.etiqueta,
           out / "escalera_brazos.png")
    (out / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    print(f"\nSalida: {out}")
    return 0 if okk else 1


if __name__ == "__main__":
    sys.exit(main())
