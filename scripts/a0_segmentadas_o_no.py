"""a0_segmentadas_o_no.py — por qué se escapan las 13 marcas que HoVer-NeXt no acreditó.

El cruce (`cruce_hovernext_marcas.py`) cerró que HoVer-NeXt acredita **13 de las 26** marcas
de `Mitosis` del patólogo en la 129741. Nunca preguntó qué pasó con las otras 13, porque solo
miró la clase `mitosis`. Esta pregunta está en el camino crítico: desde K=189 el factor que
manda es la detección, así que agrandar la máscara ya no compra marcas y lo único que mueve el
número es el detector. Las dos fallas posibles cuestan cosas muy distintas:

  - **segmentada y mal clasificada** -> la instancia existe, falla la cabeza de clase. Se
    arregla recalibrando/reentrenando la clase, o con una segunda etapa barata encima.
  - **no segmentada** -> falla la segmentación. No hay objeto que reclasificar: mucho más caro.

Se contesta **sin GPU**, con lo que ya está en disco gracias a `--keep_raw`:

  - `pinst_pp.zip`  mapa de instancias post-procesado, int32, (80496, 39426)
  - `class_inst.json`  {id_instancia: [clase, [fila, columna]]}, 238.329 instancias

Geometría verificada antes de usarla (no se asume):
  `ds_factor = LUT_MAGNIFICATION_X[argmax] / level = 20/20 = 1` para esta lámina
  (mpp 0,465 casa con 0,485 a rtol 0,2, y Lizard tesela a 20x), así que **el mapa de
  instancias está en coordenadas openslide level 0, sin reescalar**: `pinst_pp[y, x]`.
  Comprobado contra los 177 de `pred_mitosis.tsv`: los 177 centroides de `class_inst.json`
  con clase 7 reproducen las 177 filas del tsv con (x=columna, y=fila).

Lo que NO es
------------
- **No es una medida de precisión de HoVer-NeXt.** Las marcas son positivos parciales
  ([[anotaciones-patologo-qupath]]): lo no marcado NO es negativo, y nada de acá se llama
  falso positivo.
- **No mide cuántas mitosis HAY.** El denominador son las 26 marcadas.
- El reparto de clases de las falladas describe **a qué clase fue a parar el núcleo**, no
  qué es el núcleo. La verdad de campo dice `Mitosis` y nada más.

Control positivo (patrón P3): las 13 acreditadas pasan por el mismo procedimiento. Si el
criterio de «hay instancia debajo» no las recupera a ellas, el criterio está mal, no el grupo
de estudio.

Uso (env de HoVer-NeXt: es el único con zarr):
  ENVP=/media/administrador/Storage1/sdonoso/clam_testing2/envs/hovernext
  LD_LIBRARY_PATH=$ENVP/lib $ENVP/bin/python scripts/a0_segmentadas_o_no.py
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import zarr

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
from cruce_hovernext_marcas import marcas_mitosis, emparejar_pares  # noqa: E402

# Lizard-Mitosis, `hover_next_reference/src/constants.py:31-39`. El 0 no es una clase: es el
# fondo del mapa de instancias (`fill_value` del zarr).
CLASES = {0: "(sin instancia)", 1: "neutrophil", 2: "epithelial-cell", 3: "lymphocyte",
          4: "plasma-cell", 5: "eosinophil", 6: "connective-tissue-cell", 7: "mitosis"}

TOL_EMPAREJAMIENTO_UM = 30.0   # la misma que adoptó el cruce, para no cambiar el 13/26
TOL_VECINDAD_UM = 15.0         # radio para «la instancia que el patólogo señaló»


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--geojson", default="/media/administrador/Storage1/sdonoso/hover_net/"
                                         "129741.bif - GDT.geojson")
    ap.add_argument("--tsv", default=str(REPO / "results/b8_hovernext_129741/hovernext/"
                                                "lizard_mitosis/129741/pred_mitosis.tsv"))
    ap.add_argument("--pinst", default=str(REPO / "results/b8_hovernext_129741/hovernext/"
                                                  "lizard_mitosis/129741/pinst_pp.zip"))
    ap.add_argument("--class-inst", default=str(REPO / "results/b8_hovernext_129741/hovernext/"
                                                       "lizard_mitosis/129741/class_inst.json"))
    ap.add_argument("--offset", default=str(REPO / "sprints/B8_sprint8/anotaciones_patologo/"
                                                   "offset_129741.json"))
    ap.add_argument("--mpp", type=float, default=0.465)
    ap.add_argument("--out-dir", default=str(REPO / "results/b8_hovernext_129741/a0_falladas"))
    a = ap.parse_args()

    out = Path(a.out_dir); out.mkdir(parents=True, exist_ok=True)
    off = json.loads(Path(a.offset).read_text())
    mpp = a.mpp

    marcas, lados = marcas_mitosis(a.geojson, off["dx"], off["dy"])
    det = np.asarray([[float(r["x"]), float(r["y"])]
                      for r in csv.DictReader(open(a.tsv), delimiter="\t")])
    dist = np.linalg.norm(marcas[:, None, :] - det[None, :, :], axis=2)
    ok, pares = emparejar_pares(dist, TOL_EMPAREJAMIENTO_UM / mpp)

    print("=" * 78)
    print("A0 — ¿los núcleos que se escapan fueron SEGMENTADOS y mal clasificados,")
    print("     o no fueron segmentados?")
    print("=" * 78)
    print(f"marcas de Mitosis        : {len(marcas)}  "
          f"(lado mediano {np.median(lados):.0f} px = {np.median(lados)*mpp:.1f} µm)")
    print(f"acreditadas por el cruce : {int(ok.sum())}   se escapan: {int((~ok).sum())}")

    ci = json.load(open(a.class_inst))
    ids = np.fromiter((int(k) for k in ci.keys()), dtype=np.int64, count=len(ci))
    vals = list(ci.values())
    cls_de = np.zeros(ids.max() + 1, dtype=np.int8)
    cen_de = np.zeros((ids.max() + 1, 2), dtype=np.float32)     # (fila=y, columna=x)
    for i, v in zip(ids, vals):
        cls_de[i] = v[0]
        cen_de[i] = v[1]
    print(f"instancias del mapa      : {len(ci)}  "
          f"({Counter(int(v[0]) for v in vals)[7]} de clase mitosis)")

    z = zarr.open(zarr.storage.ZipStore(a.pinst, mode="r"), mode="r")
    assert z.shape[0] > marcas[:, 1].max() and z.shape[1] > marcas[:, 0].max(), \
        "las marcas caen fuera del mapa de instancias: revisar el offset"

    rad = int(round(TOL_VECINDAD_UM / mpp))     # 32 px
    filas = []
    for i, (mx, my) in enumerate(marcas):
        cx, cy = int(round(mx)), int(round(my))
        bajo_centro = int(z[cy, cx])

        # ventana de +-rad: el centroide del polígono puede caer en un borde o en el hueco
        # entre dos núcleos, así que «hay instancia» no se decide con un solo píxel.
        v = np.asarray(z[max(cy - rad, 0):cy + rad + 1, max(cx - rad, 0):cx + rad + 1])
        pres = np.unique(v)
        pres = pres[pres > 0]
        if len(pres):
            d = np.linalg.norm(cen_de[pres] - np.array([my, mx], dtype=np.float32), axis=1)
            j = int(np.argmin(d))
            vecina, d_vecina = int(pres[j]), float(d[j])
        else:
            vecina, d_vecina = 0, float("nan")

        clases_ventana = Counter(int(cls_de[p]) for p in pres)
        hay_mitosis_cerca = 7 in clases_ventana
        filas.append(dict(
            marca=i,
            x=round(float(mx), 1), y=round(float(my), 1),
            lado_um=round(float(lados[i]) * mpp, 1),
            acreditada=int(ok[i]),
            deteccion_pareada=int(pares[i]),
            inst_bajo_centroide=bajo_centro,
            clase_bajo_centroide=CLASES[int(cls_de[bajo_centro]) if bajo_centro else 0],
            n_instancias_en_radio=int(len(pres)),
            inst_mas_cercana=vecina,
            clase_mas_cercana=CLASES[int(cls_de[vecina]) if vecina else 0],
            dist_mas_cercana_um=round(d_vecina * mpp, 1) if vecina else "",
            hay_clase_mitosis_en_radio=int(hay_mitosis_cerca),
            clases_en_radio="|".join(f"{CLASES[c]}:{n}" for c, n in
                                     sorted(clases_ventana.items())),
        ))

    with open(out / "marcas_vs_instancias.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(filas[0].keys()))
        w.writeheader(); w.writerows(filas)

    # ------------------------------------------------------------------ el reparto
    def reparto(sub, titulo):
        print(f"\n{titulo}  (n = {len(sub)})")
        seg = [f for f in sub if f["inst_bajo_centroide"] != 0]
        nseg = [f for f in sub if f["inst_bajo_centroide"] == 0]
        print(f"  con instancia BAJO el centroide de la marca : {len(seg)}")
        print(f"  sin instancia bajo el centroide             : {len(nseg)}")
        if nseg:
            con_vecina = [f for f in nseg if f["inst_mas_cercana"] != 0]
            print(f"     de ésas, con una instancia a <= {TOL_VECINDAD_UM:g} µm : "
                  f"{len(con_vecina)}  (o sea segmentada, con el centroide del polígono "
                  f"cayendo en el hueco)")
            print(f"     de ésas, sin ninguna instancia a <= {TOL_VECINDAD_UM:g} µm: "
                  f"{len(nseg) - len(con_vecina)}  (no segmentada)")
        c = Counter(f["clase_bajo_centroide"] for f in sub)
        print("  clase que recibió la instancia bajo el centroide:")
        for k, n in c.most_common():
            print(f"     {k:<26} {n}")
        return seg, nseg

    print("\n" + "=" * 78)
    print("CONTROL POSITIVO — las 13 que SÍ acreditó (patrón P3: si el criterio no las")
    print("recupera a ellas, el criterio está mal)")
    print("=" * 78)
    reparto([f for f in filas if f["acreditada"]], "acreditadas")

    print("\n" + "=" * 78)
    print("GRUPO DE ESTUDIO — las 13 que se escapan")
    print("=" * 78)
    seg_f, nseg_f = reparto([f for f in filas if not f["acreditada"]], "falladas")

    falladas = [f for f in filas if not f["acreditada"]]
    n_seg = sum(1 for f in falladas if f["inst_bajo_centroide"] != 0
                or f["inst_mas_cercana"] != 0)
    n_noseg = len(falladas) - n_seg
    print("\n" + "-" * 78)
    print(f"RESPUESTA: de las {len(falladas)} falladas, **{n_seg} estaban segmentadas** "
          f"(hay una instancia\n           encima o a <= {TOL_VECINDAD_UM:g} µm) y le tocó "
          f"otra clase; **{n_noseg} no tenían instancia**.")
    print("-" * 78)
    print("\ndetalle de las falladas, marca por marca:")
    print(f"  {'#':>3} {'clase bajo el centroide':<26} {'más cercana':<26} {'dist µm':>8}")
    for f in falladas:
        print(f"  {f['marca']:>3} {f['clase_bajo_centroide']:<26} "
              f"{f['clase_mas_cercana']:<26} {str(f['dist_mas_cercana_um']):>8}")

    meta = dict(
        que_es="A0: reparto segmentada-y-mal-clasificada vs no-segmentada, sobre las marcas "
               "que HoVer-NeXt no acredito en la 129741",
        no_es=["precision de HoVer-NeXt", "cuantas mitosis HAY en la lamina",
               "una afirmacion sobre que ES cada nucleo: la verdad de campo dice Mitosis"],
        unidad="marcas (26 en la 129741). NO parches (28) ni detecciones (177)",
        n_marcas=len(marcas), n_acreditadas=int(ok.sum()), n_falladas=int((~ok).sum()),
        n_falladas_segmentadas=int(n_seg), n_falladas_sin_instancia=int(n_noseg),
        tolerancia_emparejamiento_um=TOL_EMPAREJAMIENTO_UM,
        tolerancia_vecindad_um=TOL_VECINDAD_UM,
        clases_falladas_bajo_centroide={k: v for k, v in Counter(
            f["clase_bajo_centroide"] for f in falladas).most_common()},
        clases_acreditadas_bajo_centroide={k: v for k, v in Counter(
            f["clase_bajo_centroide"] for f in filas if f["acreditada"]).most_common()},
        n_instancias_mapa=len(ci),
        ds_factor_verificado=1,
        offset_aplicado=dict(dx=off["dx"], dy=off["dy"]), mpp=mpp,
        fuente_pinst=str(a.pinst), fuente_class_inst=str(a.class_inst),
        fuente_detecciones=str(a.tsv),
    )
    (out / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    print(f"\nSalida: {out}")


if __name__ == "__main__":
    main()
