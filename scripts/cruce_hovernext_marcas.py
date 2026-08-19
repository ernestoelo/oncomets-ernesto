"""cruce_hovernext_marcas.py — el SEGUNDO factor del techo de la fase 3.

`techo_atencion_topk.py` midió el primer factor: cuánto deja pasar la máscara de atención.
Éste mide el segundo: cuánto se come la DETECCIÓN. Cruza las 177 mitosis que HoVer-NeXt
detectó en la 129741 (job 5008) contra las 26 marcas de `Mitosis` del patólogo, y después
combina los dos factores para cerrar la desigualdad del patrón P2.a:

    recall_fase3(K)  <=  min( techo_atencion(K) , detección_hovernext )

y, mejor que la cota, el conteo REAL de la intersección: marcas que están a la vez dentro
de la máscara y detectadas.

Reglas que gobiernan la lectura (no son adorno):

- Las marcas son **positivos parciales** ([[anotaciones-patologo-qupath]] trampa 2): lo no
  marcado NO es negativo. Por eso se reporta **recall y nada más**. Una detección fuera de
  las 26 puede ser una mitosis real sin marcar, así que **no se calcula precisión**, ni se
  la llama falso positivo.
- El geojson **no está en coordenadas de openslide**: se le suma el offset ya derivado en
  `sprints/B8_sprint8/anotaciones_patologo/offset_129741.json` (dx=3829, dy=0).
- La lámina tiene **dos regiones de escaneo** y las marcas caen todas en la de abajo. Todo
  lo que se compare contra ellas se confina ahí.
- El emparejamiento es **uno a uno** (húngaro): una detección no puede acreditar dos marcas.
  Contar por "distancia mínima" infla el recall reusando la misma detección.

Uso:
  PYTHONPATH=/media/administrador/Storage1/sdonoso/clam_testing2/.pylibs \
  /home/sdonoso/miniconda3/envs/clam_latest/bin/python scripts/cruce_hovernext_marcas.py
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
from alinear_anotaciones_qupath import cargar_anotaciones          # noqa: E402
from techo_atencion_topk import cargar, techo, Y_CORTE_REGION, KS  # noqa: E402

# Tolerancias del barrido, en µm. Las de detección de mitosis en la literatura viven entre
# 7,5 y 30 µm; se barre hasta 300 para MOSTRAR dónde el emparejamiento deja de ser creíble.
TOLS_UM = [7.5, 15, 22.5, 30, 50, 75, 100, 150, 200, 300]
TOL_ADOPTADA_UM = 30.0     # se justifica sola: el resultado es plano de 7,5 a 75


def marcas_mitosis(geojson: str, dx: int, dy: int):
    """Centroides y lado de las marcas de Mitosis, en coordenadas openslide level 0."""
    cen, lados = [], []
    for cl, poly in cargar_anotaciones(geojson):
        if cl != "Mitosis":
            continue
        p = poly + np.array([dx, dy], dtype=float)
        cen.append(p.mean(axis=0))
        lados.append(max(np.ptp(p[:, 0]), np.ptp(p[:, 1])))
    return np.asarray(cen), np.asarray(lados)


def emparejar(dist, tol_px):
    """Húngaro con corte: devuelve la máscara booleana de marcas acreditadas."""
    c = dist.copy()
    c[c > tol_px] = 1e9
    fi, ci = linear_sum_assignment(c)
    ok = np.zeros(dist.shape[0], bool)
    for i, j in zip(fi, ci):
        if dist[i, j] <= tol_px:
            ok[i] = True
    return ok


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
    ap.add_argument("--out-dir", default=str(REPO / "results/b8_hovernext_129741/cruce_marcas"))
    a = ap.parse_args()

    out = Path(a.out_dir); out.mkdir(parents=True, exist_ok=True)
    off = json.loads(Path(a.offset).read_text())
    mpp = a.mpp

    marcas, lados = marcas_mitosis(a.geojson, off["dx"], off["dy"])
    det = np.asarray([[float(r["x"]), float(r["y"])]
                      for r in csv.DictReader(open(a.tsv), delimiter="\t")])
    en_region = det[:, 1] >= Y_CORTE_REGION

    print("=" * 74)
    print("CRUCE HoVer-NeXt × MARCAS DEL PATÓLOGO — el segundo factor del techo")
    print("=" * 74)
    print(f"marcas de Mitosis      : {len(marcas)}  (lado mediano {np.median(lados):.0f} px "
          f"= {np.median(lados)*mpp:.1f} µm)")
    print(f"  en la región anotada : {(marcas[:, 1] >= Y_CORTE_REGION).sum()}")
    print(f"detecciones HoVer-NeXt : {len(det)}  ({en_region.sum()} en la región anotada, "
          f"{(~en_region).sum()} en la otra)")

    dist = np.linalg.norm(marcas[:, None, :] - det[None, :, :], axis=2)
    dmin = dist.min(axis=1)
    print("\ndistancia de cada marca a la detección más cercana:")
    for q in (0, 25, 50, 75, 100):
        v = float(np.percentile(dmin, q))
        print(f"  p{q:<4} {v:7.1f} px  {v*mpp:7.1f} µm")

    print("\nrecall por tolerancia, emparejamiento UNO A UNO "
          f"(denominador = las {len(marcas)} marcas):")
    print(f"  {'tol µm':>7} {'tol px':>7} {'TP':>4} {'recall':>8}")
    filas = []
    for t_um in TOLS_UM:
        ok = emparejar(dist, t_um / mpp)
        filas.append(dict(tolerancia_um=t_um, tolerancia_px=round(t_um / mpp, 1),
                          tp=int(ok.sum()), recall=round(ok.sum() / len(marcas), 4)))
        print(f"  {t_um:7.1f} {t_um/mpp:7.1f} {ok.sum():4d} {ok.sum()/len(marcas):8.1%}")
    pd.DataFrame(filas).to_csv(out / "recall_por_tolerancia.csv", index=False)

    ok = emparejar(dist, TOL_ADOPTADA_UM / mpp)
    print(f"\nSe adopta {TOL_ADOPTADA_UM:g} µm, y el corte NO decide nada: el recall es PLANO "
          f"de 7,5 a 75 µm")
    print(f"  detectadas {ok.sum()}/{len(marcas)} = {ok.sum()/len(marcas):.1%}   "
          f"sin detectar {(~ok).sum()}")
    print(f"  las no detectadas no son 'por poco': su detección más cercana está a "
          f"{np.median(dmin[~ok])*mpp:.0f} µm de mediana (mínimo {dmin[~ok].min()*mpp:.0f})")

    # ---------------- los dos factores, juntos ----------------
    coords, ps0, a_clam, a_mam, mit_xy, area_mm2 = cargar(Path(a.npz), Path(a.anotaciones), mpp)
    idx_region = np.where(coords[:, 1] >= Y_CORTE_REGION)[0]

    # cada marca -> el parche del h5 que la contiene (la unidad común de los dos factores)
    parche_de = np.full(len(marcas), -1, dtype=int)
    for i, (mx, my) in enumerate(marcas):
        d = (coords[:, 0] <= mx) & (mx < coords[:, 0] + ps0) & \
            (coords[:, 1] <= my) & (my < coords[:, 1] + ps0)
        w = np.where(d)[0]
        if len(w):
            parche_de[i] = w[0]
    print(f"\nmarcas casadas con un parche del h5: {(parche_de >= 0).sum()}/{len(marcas)}")

    print("\n" + "=" * 74)
    print("LOS DOS FACTORES JUNTOS — P2.a cerrada sobre las 26 marcas")
    print("=" * 74)
    print("  'máscara' = la marca cae en el top-K por atención dentro de la región anotada")
    print("  'detectada' = HoVer-NeXt puso una mitosis encima (uno a uno, 30 µm)")
    filas2 = []
    for nombre, at in (("CLAM", a_clam), ("Mammoth", a_mam)):
        a_reg = at[idx_region]
        orden = idx_region[np.argsort(a_reg)[::-1]]
        print(f"\n{nombre}")
        print(f"  {'K':>6} {'% región':>9} {'máscara':>9} {'detect.':>8} {'AMBAS':>7} "
              f"{'cota min()':>11}")
        for k in KS:
            k = min(k, len(orden))
            sel = set(orden[:k].tolist())
            en_masc = np.array([p >= 0 and p in sel for p in parche_de])
            ambas = int((en_masc & ok).sum())
            cota = min(int(en_masc.sum()), int(ok.sum()))
            filas2.append(dict(brazo=nombre, K=k, pct_region=round(100*k/len(idx_region), 1),
                               en_mascara=int(en_masc.sum()), detectadas=int(ok.sum()),
                               ambas=ambas, cota_min=cota,
                               recall_conjunto=round(ambas/len(marcas), 4)))
            print(f"  {k:>6} {100*k/len(idx_region):>8.1f}% {en_masc.sum():>4}/{len(marcas):<4} "
                  f"{ok.sum():>3}/{len(marcas):<4} {ambas:>3}/{len(marcas):<3} {cota:>7}/{len(marcas)}")
    pd.DataFrame(filas2).to_csv(out / "techo_conjunto.csv", index=False)

    meta = dict(
        que_es="segundo factor del techo de la fase 3: cuanto se come la deteccion",
        no_es=["precision de HoVer-NeXt", "una medida de cuantas mitosis HAY en la lamina",
               "un recall sobre las mitosis reales: el denominador son LAS MARCADAS"],
        n_marcas=int(len(marcas)), n_detecciones=int(len(det)),
        n_detecciones_region_anotada=int(en_region.sum()),
        tolerancia_adoptada_um=TOL_ADOPTADA_UM,
        recall=round(float(ok.sum()) / len(marcas), 4), tp=int(ok.sum()),
        plano_entre_um=[7.5, 75.0],
        offset_aplicado=dict(dx=off["dx"], dy=off["dy"]),
        y_corte_region=Y_CORTE_REGION, mpp=mpp,
        fuente_detecciones=str(a.tsv), fuente_atencion=str(a.npz),
    )
    (out / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    print(f"\nSalida: {out}")


if __name__ == "__main__":
    main()
