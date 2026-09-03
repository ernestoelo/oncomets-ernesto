"""b9_escalera_area.py — ¿cuánta ÁREA compra cada marca retenida? (B9, §6 del prereg)

Es la pregunta que Ernesto trajo de la reunión del 1-sep, y NO es «¿filtrar encuentra más
mitosis?». Filtrar **no puede** subir el conteo: HoVer-NeXt ya corrió sobre la lámina entera
en las doce, así que «HoVer-NeXt + CLAM» es un SUBCONJUNTO de las 732 detecciones y de las 26
marcas acreditadas, y el conteo sólo puede bajar (P2.a.ter, [[techo-filtro-antes-de-correr]],
[[carga-fija-no-k-fijo]]). Lo que la restricción compra es SUPERFICIE que el patólogo no mira.

Pre-registro: `sprints/B9_sprint9/atencion_12_laminas/prereg.md` §6 y su ADDENDUM §6.a,
escritos ANTES de este archivo. Las tres cosas que el ADDENDUM fijó y que gobiernan el código:

  F1  De las 732 detecciones sólo 707 caen dentro de la teselación de CLAM (las 25 restantes
      están sobre tejido que el segmentador descartó). Las 94 marcas y las 26 acreditadas
      caen todas dentro. ⇒ la escalera lleva DOS controles: `sin_filtro` (732 · 26, lo que el
      patólogo mira hoy) y `teselado` (707 · 26, el techo real de todo brazo enmascarado). El
      chequeo del peldaño «lámina entera» se lee contra el SEGUNDO.

  F2  La grilla del h5 NO es un retículo regular (de 7 a 29 valores distintos de `x mod 256`
      por lámina). ⇒ la contención va por INTERVALO y exacta, nunca por hash de retículo: un
      `//256` da 166 detecciones donde la exacta da 168 en la 129741 sola.

  F3  Una marca tiene DOS mapeos a parche. Por centroide, las 94 caen en 94 parches; por
      solape del polígono, `parches_anotados_*.csv` cuenta 113. **Esta escalera cuenta por
      CENTROIDE (94)**; el eje de atención cuenta por solape (113)
      ([[dos-numeros-iguales-denominador-distinto]]).

Todo se IMPORTA, nada se re-implementa: `SLIDES`, `paths_de`, `leer_detecciones`,
`REGION_ANOTADA` y `MPP` de `cruce_94_marcas.py`; `marcas_mitosis` de
`cruce_hovernext_marcas.py` (que aplica el offset del geojson); `leer_h5`, `paso_de_grilla`,
`atencion_json_out`, `TAREA_MITOSIS` y `TAREA_GATE` de `b9_atencion_12_laminas.py`. La
columna `acreditada` sale de `results/b9_cruce_94/pares_<slide>.csv`.

CPU, post-hoc, sin GPU, sin re-correr nada. Uso (workaround B — binario absoluto):

  CUDA_VISIBLE_DEVICES="" /home/sdonoso/miniconda3/envs/clam_latest/bin/python \
      scripts/b9_escalera_area.py
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path("/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto")
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.atencion_vs_anotaciones import ranks_of                        # noqa: E402
from scripts.b9_atencion_12_laminas import (                                # noqa: E402
    TAREA_GATE, TAREA_MITOSIS, atencion_json_out, leer_h5, paso_de_grilla,
)
from scripts.cruce_94_marcas import (                                       # noqa: E402
    MPP, REGION_ANOTADA, SLIDES, leer_detecciones, paths_de,
)
from scripts.cruce_hovernext_marcas import marcas_mitosis                   # noqa: E402

# Los peldaños, en mm². `None` = la lámina entera (k = N parches). El 3 es el que pidió
# Sebastián y el que va como objetivo a la lámina de tareas.
PRESUPUESTOS = [None, 30.0, 10.0, 3.0, 1.0]

# Repeticiones del brazo `azar`, y el cuantil que se reporta al lado de la media.
N_AZAR, Q_AZAR = 200, 97.5

BRAZOS = ["sin_filtro", "teselado", "clam_mitosis", "clam_gate", "clam_combinado", "azar"]


# --------------------------------------------------------------------------- geometría
def parche_de(puntos: np.ndarray, coords: np.ndarray, step: int) -> np.ndarray:
    """Índice del parche que CONTIENE cada punto; -1 si ninguno.

    Contención por INTERVALO y exacta (F2): `coords[j,0] <= x < coords[j,0]+step` y lo mismo
    en `y`. Nunca un hash de retículo: la grilla del h5 no es regular. Fuerza bruta alcanza
    (5.203 parches × 252 detecciones en el peor caso).
    """
    out = np.full(len(puntos), -1, dtype=np.int64)
    multiples = 0
    for i, (x, y) in enumerate(puntos):
        sel = np.flatnonzero((coords[:, 0] <= x) & (x < coords[:, 0] + step) &
                             (coords[:, 1] <= y) & (y < coords[:, 1] + step))
        if len(sel):
            out[i] = sel[0]
            multiples += len(sel) > 1
    return out, multiples


def top_k(score: np.ndarray, k: int) -> np.ndarray:
    """Los `k` índices de mayor score. Orden estable: los empates se rompen por índice."""
    return np.argsort(-score, kind="stable")[:k]


# --------------------------------------------------------------------------- por lámina
def cargar_lamina(slide: str) -> dict:
    p = paths_de(slide)
    for k, v in p.items():
        if not Path(v).exists():
            raise SystemExit(f"falta {k} de {slide}: {v}")

    _feats, coords = leer_h5(slide)
    step = paso_de_grilla(coords)

    off = json.loads(Path(p["offset"]).read_text())
    marcas, _lados = marcas_mitosis(str(p["geojson"]), off["dx"], off["dy"])
    det = leer_detecciones(p["tsv"])

    # `acreditada` viene del cruce de las 94, que emparejó uno a uno con el húngaro a 30 µm.
    # El orden de sus filas es el de `marcas_mitosis`, así que el join es POSICIONAL.
    pares = pd.read_csv(REPO / "results/b9_cruce_94" / f"pares_{slide}.csv")
    if len(pares) != len(marcas):
        raise SystemExit(f"{slide}: pares_{slide}.csv tiene {len(pares)} filas y "
                         f"marcas_mitosis devuelve {len(marcas)}")
    acred = pares["acreditada"].astype(bool).to_numpy()

    p_marcas, mult_m = parche_de(marcas, coords, step)
    p_det, mult_d = parche_de(det, coords, step)

    sc_mit, _pred_m, _c = atencion_json_out(slide, TAREA_MITOSIS, coords)
    sc_gate, _pred_g, _c = atencion_json_out(slide, TAREA_GATE, coords)

    return dict(
        slide=slide, coords=coords, step=step, n=len(coords),
        a_parche=(step * MPP / 1000.0) ** 2,
        marcas=marcas, acred=acred, det=det,
        p_marcas=p_marcas, p_det=p_det, mult=mult_m + mult_d,
        sc={"clam_mitosis": sc_mit, "clam_gate": sc_gate,
            "clam_combinado": ranks_of(sc_mit) * ranks_of(sc_gate)},
    )


def filas_de(L: dict, rng) -> list[dict]:
    """Una fila por brazo × presupuesto. `sin_filtro` sólo tiene el peldaño de la lámina."""
    n, a = L["n"], L["a_parche"]
    filas = []

    def contar(mask_parches: np.ndarray | None) -> tuple[int, int, int]:
        """(marcas, acreditadas, detecciones) dentro de la máscara de parches."""
        if mask_parches is None:                    # sin_filtro: la lámina completa
            return len(L["marcas"]), int(L["acred"].sum()), len(L["det"])
        dentro_m = mask_parches[L["p_marcas"]] & (L["p_marcas"] >= 0)
        dentro_d = mask_parches[L["p_det"]] & (L["p_det"] >= 0)
        return int(dentro_m.sum()), int((dentro_m & L["acred"]).sum()), int(dentro_d.sum())

    def fila(brazo, pres, k, area, m, ac, d, **extra):
        return dict(slide=L["slide"], brazo=brazo,
                    presupuesto_mm2=("lamina_entera" if pres is None else pres),
                    k_parches=k, area_real_mm2=area,
                    marcas_dentro=m, acreditadas_dentro=ac, detecciones_dentro=d,
                    det_por_mm2=(d / area if area and area > 0 else float("nan")),
                    **extra)

    # --- los dos controles ---------------------------------------------------
    # `sin_filtro` no tiene área comparable: es la lámina como corrió el detector, que
    # incluye el tejido que el segmentador de CLAM descartó. Su rol es el CONTEO (F1).
    m, ac, d = contar(None)
    filas.append(fila("sin_filtro", None, np.nan, float("nan"), m, ac, d))

    todos = np.ones(n, bool)
    m, ac, d = contar(todos)
    filas.append(fila("teselado", None, n, n * a, m, ac, d))

    # --- los brazos con filtro ------------------------------------------------
    for pres in PRESUPUESTOS:
        k = n if pres is None else min(n, int(np.ceil(pres / a)))
        for brazo in ("clam_mitosis", "clam_gate", "clam_combinado"):
            mask = np.zeros(n, bool)
            mask[top_k(L["sc"][brazo], k)] = True
            m, ac, d = contar(mask)
            filas.append(fila(brazo, pres, k, k * a, m, ac, d))

        # `azar`: misma carga de parches, 200 repeticiones, media y p97,5.
        rep = np.empty((N_AZAR, 3))
        for r in range(N_AZAR):
            mask = np.zeros(n, bool)
            mask[rng.choice(n, size=k, replace=False)] = True
            rep[r] = contar(mask)
        filas.append(fila("azar", pres, k, k * a, *rep.mean(axis=0),
                          marcas_dentro_p975=float(np.percentile(rep[:, 0], Q_AZAR)),
                          acreditadas_dentro_p975=float(np.percentile(rep[:, 1], Q_AZAR)),
                          detecciones_dentro_p975=float(np.percentile(rep[:, 2], Q_AZAR))))
    return filas


# --------------------------------------------------------------------------- chequeos
def chequear(esc: pd.DataFrame, geo: pd.DataFrame) -> list[str]:
    """Los chequeos del prereg §6 + ADDENDUM §6.a. Un fallo es bug, no resultado."""
    err = []
    ent = esc[esc["presupuesto_mm2"] == "lamina_entera"]
    tot = {b: ent[ent["brazo"] == b][["marcas_dentro", "acreditadas_dentro",
                                      "detecciones_dentro"]].sum() for b in ent["brazo"].unique()}

    for nom, (m, ac, d) in (("sin_filtro", (94, 26, 732)), ("teselado", (94, 26, 707))):
        got = tot[nom]
        ok = (int(got["marcas_dentro"]), int(got["acreditadas_dentro"]),
              int(got["detecciones_dentro"])) == (m, ac, d)
        print(f"  peldaño lámina entera · {nom:<11} "
              f"{int(got['marcas_dentro']):>3} marcas · {int(got['acreditadas_dentro']):>2} "
              f"acreditadas · {int(got['detecciones_dentro']):>3} detecciones   "
              f"esperado {m} · {ac} · {d}   {'OK' if ok else 'FALLA'}")
        if not ok:
            err.append(f"peldaño lámina entera, {nom}: {list(got)} != {[m, ac, d]}")

    # Los brazos con filtro, con k = N, tienen que coincidir con `teselado` (F1).
    for b in ("clam_mitosis", "clam_gate", "clam_combinado"):
        ok = tot[b].equals(tot["teselado"])
        print(f"  peldaño lámina entera · {b:<15} == teselado   {'OK' if ok else 'FALLA'}")
        if not ok:
            err.append(f"peldaño lámina entera, {b} != teselado: {list(tot[b])}")

    # Monotonía: `acreditadas_dentro` nunca sube al bajar el presupuesto.
    orden = {p: i for i, p in enumerate(["lamina_entera", 30.0, 10.0, 3.0, 1.0])}
    fallos_mono = 0
    con_filtro = ["clam_mitosis", "clam_gate", "clam_combinado"]
    for (s, b), g in esc[esc["brazo"].isin(con_filtro)].groupby(["slide", "brazo"]):
        g = g.assign(o=g["presupuesto_mm2"].map(orden)).sort_values("o")
        if (np.diff(g["acreditadas_dentro"].to_numpy()) > 1e-9).any():
            err.append(f"monotonía rota en {s}/{b}")
            fallos_mono += 1
    print(f"  monotonía de acreditadas_dentro al bajar el presupuesto   "
          f"{'OK' if not fallos_mono else f'FALLA ({fallos_mono})'}")

    # Conteos duros que no se mueven.
    for nom, got, exp in (("láminas", len(geo), 12),
                          ("parches", int(geo["n_parches"].sum()), 49832),
                          ("marcas", int(geo["marcas"].sum()), 94),
                          ("acreditadas", int(geo["acreditadas"].sum()), 26),
                          ("detecciones", int(geo["detecciones"].sum()), 732),
                          ("det. en la teselación", int(geo["detecciones_en_tesela"].sum()), 707)):
        ok = got == exp
        print(f"  {nom:<22} {got:>6}  esperado {exp:>6}  {'OK' if ok else 'FALLA'}")
        if not ok:
            err.append(f"{nom}: {got} != {exp}")

    mm2 = float(geo["mm2"].sum())
    ok = abs(mm2 - 706.1) < 0.1
    print(f"  {'área teselada (mm²)':<22} {mm2:>6.1f}  esperado  706.1  {'OK' if ok else 'FALLA'}")
    if not ok:
        err.append(f"área teselada: {mm2:.1f} != 706.1")
    return err


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(REPO / "results/b9_escalera_area"))
    ap.add_argument("--seed", type=int, default=1)
    args = ap.parse_args()

    out = Path(args.out_dir); out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)

    print("=" * 82)
    print("ESCALERA DE ÁREA — cuánta superficie compra cada marca retenida, las 12 anotadas")
    print("=" * 82)
    print("NO mide si filtrar encuentra más mitosis: no puede. HoVer-NeXt ya corrió sobre la")
    print("lámina entera, así que todo filtro es un subconjunto y el conteo sólo puede bajar.")
    print("Unidad de marca = CENTROIDE (94). El eje de atención cuenta por solape (113).\n")

    filas, geo = [], []
    print(f"  {'lámina':<12} {'N':>6} {'paso':>5} {'mm2':>7} {'marcas':>7} {'acred':>6} "
          f"{'detec':>6} {'det.tes':>8}")
    for slide in SLIDES:
        L = cargar_lamina(slide)
        if L["mult"]:
            print(f"  [aviso] {slide}: {L['mult']} puntos caen en más de un parche "
                  f"(parches solapados); se toma el de menor índice")
        filas += filas_de(L, rng)
        reg = REGION_ANOTADA.get(slide)
        geo.append(dict(
            slide=slide, n_parches=L["n"], paso_px=L["step"],
            area_parche_mm2=round(L["a_parche"], 6), mm2=L["n"] * L["a_parche"],
            marcas=len(L["marcas"]), acreditadas=int(L["acred"].sum()),
            detecciones=len(L["det"]),
            marcas_en_tesela=int((L["p_marcas"] >= 0).sum()),
            marcas_fuera=int((L["p_marcas"] < 0).sum()),
            detecciones_en_tesela=int((L["p_det"] >= 0).sum()),
            detecciones_fuera=int((L["p_det"] < 0).sum()),
            region_anotada=f"[{reg[0]}, {reg[1]})" if reg else "",
        ))
        g = geo[-1]
        print(f"  {slide:<12} {g['n_parches']:>6} {g['paso_px']:>5} {g['mm2']:>7.1f} "
              f"{g['marcas']:>7} {g['acreditadas']:>6} {g['detecciones']:>6} "
              f"{g['detecciones_en_tesela']:>8}")

    esc = pd.DataFrame(filas)
    dgeo = pd.DataFrame(geo)

    # El agregado sobre las doce, que es el número que va al deck.
    agg = (esc.groupby(["brazo", "presupuesto_mm2"], as_index=False)
              .agg(k_parches=("k_parches", "sum"), area_real_mm2=("area_real_mm2", "sum"),
                   marcas_dentro=("marcas_dentro", "sum"),
                   acreditadas_dentro=("acreditadas_dentro", "sum"),
                   detecciones_dentro=("detecciones_dentro", "sum"),
                   n_laminas=("slide", "nunique")))
    agg["det_por_mm2"] = agg["detecciones_dentro"] / agg["area_real_mm2"]
    # `sin_filtro` no tiene ni `k` ni área: el `sum` de pandas convierte su NaN en 0 y un 0
    # ahí se leería como «cero área», que es exactamente lo contrario de lo que significa.
    agg.loc[agg["brazo"] == "sin_filtro", ["k_parches", "area_real_mm2"]] = np.nan

    esc.to_csv(out / "escalera.csv", index=False)
    dgeo.to_csv(out / "por_lamina.csv", index=False)
    agg.to_csv(out / "agregado.csv", index=False)

    print("\n" + "=" * 82)
    print("AGREGADO SOBRE LAS DOCE — 26 acreditadas es el techo, y filtrar sólo puede bajarlo")
    print("=" * 82)
    print(f"  {'brazo':<16} {'presupuesto':>12} {'k':>7} {'área mm2':>9} {'marcas':>7} "
          f"{'acred':>6} {'detec':>6} {'det/mm2':>8}")
    orden = {"lamina_entera": 0, 30.0: 1, 10.0: 2, 3.0: 3, 1.0: 4}
    def _f(v, w, d=1):
        return f"{v:>{w}.{d}f}" if np.isfinite(v) else f"{'':>{w}}"
    for _, r in agg.assign(o=agg["presupuesto_mm2"].map(orden)).sort_values(
            ["o", "brazo"]).iterrows():
        print(f"  {r['brazo']:<16} {str(r['presupuesto_mm2']):>12} "
              f"{_f(r['k_parches'], 7, 0)} {_f(r['area_real_mm2'], 9)} "
              f"{_f(r['marcas_dentro'], 7)} {_f(r['acreditadas_dentro'], 6)} "
              f"{_f(r['detecciones_dentro'], 6)} {_f(r['det_por_mm2'], 8, 2)}")

    print("\n" + "=" * 82)
    print("CHEQUEOS")
    print("=" * 82)
    err = chequear(esc, dgeo)

    meta = dict(
        que_es="cuánta ÁREA compra cada marca de mitosis retenida, al restringir las "
               "detecciones de HoVer-NeXt con la atención de CLAM, sobre las 12 anotadas",
        no_es=["una medida de si filtrar encuentra MÁS mitosis: no puede, HoVer-NeXt ya "
               "corrió sobre la lámina entera y todo filtro es un subconjunto",
               "precisión, F1, recall ni PQ contra las marcas: son positivos parciales",
               "una medida por lámina: seis láminas tienen <=3 marcas"],
        unidad_marca="CENTROIDE (94 marcas). El eje de atención cuenta por SOLAPE (113 "
                     "parches). Los dos números NO son el mismo "
                     "([[dos-numeros-iguales-denominador-distinto]])",
        contencion="por intervalo y exacta: coords[j] <= p < coords[j]+step en los dos ejes. "
                   "La grilla del h5 no es un retículo regular",
        presupuestos_mm2=[("lamina_entera" if p is None else p) for p in PRESUPUESTOS],
        area_parche_mm2=round((256 * MPP / 1000.0) ** 2, 6),
        nota_area_parche="derivada de la geometría del h5 (paso 256 px × 0,465 µm/px), no de "
                         "la magnificación. Redondea a los 0,0142 mm² de la tesela de "
                         "HoVer-NeXt, que mide exactamente lo mismo sobre estas láminas",
        brazos=dict(
            sin_filtro="la lámina completa, tal como corrió el detector: 732 · 26. Su área "
                       "no se reporta porque incluye tejido que el segmentador de CLAM "
                       "descartó, así que no es comparable con la de los brazos enmascarados",
            teselado="los N parches del h5: 707 · 26. Es el TECHO REAL de todo brazo "
                     "enmascarado por parches, y contra él se lee el peldaño «lámina entera»",
            clam_mitosis=TAREA_MITOSIS, clam_gate=TAREA_GATE,
            clam_combinado="top-k por el PRODUCTO DE LOS RANGOS de las dos. EXPLORATORIO",
            azar=f"k parches al azar, {N_AZAR} repeticiones, media y p{Q_AZAR}"),
        seed=args.seed, n_azar=N_AZAR, cuantil_azar=Q_AZAR, mpp=MPP,
        declaracion_json_out=[
            "ensemble de los CINCO folds ponderado por confianza: contaminado por construcción",
            "lee la rama de la clase PREDICHA por cada fold, no la verdadera",
            "familia _pth_balance, NO la _combined_5fold de los números del B8",
            "su campo patch_size no se usa: da 127 y 64 donde la geometría del h5 da 256",
        ],
        procedencia=dict(
            atencion="clam_ensemble/attn_batch/json_out/<slide>__<tarea>.json (sgaete, RO)",
            detecciones="results/b8_hovernext_{129741,12laminas}/hovernext/lizard_mitosis/",
            acreditadas="results/b9_cruce_94/pares_<slide>.csv (húngaro uno a uno, 30 µm)",
            teselacion="clam_environ/environ/features/h5_files/<slide>.h5",
            prereg="sprints/B9_sprint9/atencion_12_laminas/prereg.md §6 + ADDENDUM §6.a"),
        chequeos_fallidos=err,
    )
    (out / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    print(f"\nSalida: {out}")
    if err:
        raise SystemExit("\nHAY CHEQUEOS FALLIDOS: es un bug del emparejamiento, "
                         "no un resultado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
