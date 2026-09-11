#!/usr/bin/env python
"""O3 del B10 — ¿la atención de CLAM localiza el CDIS?

Pre-registro: `sprints/B10_sprint10/cdis_localizacion/prereg.md`, escrito y commiteado ANTES
que este archivo (regla 9). Implementa ese documento y no lo amplía.

D4 de Ernesto: se mide la atención que YA está en disco. Sin BRACS y sin entrenar. CPU, cero GPU.

NO REIMPLEMENTA NADA: importa `build_clam`, `get_attention`, `ranks_of`, `rank_auc` y
`p_traslacion` de `atencion_vs_anotaciones.py`, el `ic_hanley_mcneil` de `auc_atencion_fold4.py`
y el `paso_de_grilla` / `leer_h5` / `atencion_json_out` de `b9_atencion_12_laminas.py`, que es el
mismo esquema aplicado a Mitosis.

Dos brazos, y el segundo NO es opcional: `json_out` lee la rama de la clase PREDICHA, y eso ya
produjo un 0,500 exacto en otro eje ([[rama-de-atencion-decide-el-resultado]]).

Universo REGIÓN (agregado el 10-sep, resultados §3.a): en las láminas con más de una región de
escaneo se mide además confinado al intervalo de `REGION_ANOTADA`, con el `medir` del B9. Sale
en `auc_cdis_region.csv` y no mueve ni un bit de `auc_cdis.csv` (regresión byte a byte).

  /home/sdonoso/miniconda3/envs/clam_latest/bin/python scripts/b10_cdis_atencion.py
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

REPO = Path("/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto")
CLAM_ENVIRON = Path("/media/administrador/Storage1/sdonoso/clam_environ")
ENVIRON = CLAM_ENVIRON / "environ"
JSON_OUT = Path("/media/administrador/Storage1/sdonoso/clam_ensemble/attn_batch/json_out")
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

from scripts.atencion_vs_anotaciones import (       # noqa: E402
    build_clam, get_attention, p_traslacion, rank_auc, ranks_of)
from scripts.auc_atencion_fold4 import ic_hanley_mcneil                     # noqa: E402
from scripts.b9_atencion_12_laminas import leer_h5, paso_de_grilla          # noqa: E402
from scripts.b9_atencion_12_laminas import medir as medir_por_universo      # noqa: E402
from scripts.cruce_94_marcas import REGION_ANOTADA                          # noqa: E402
from b9_descriptores_nucleos import geojson_de                              # noqa: E402

# Los offsets viven junto a los del B8 a proposito (un offset es por lamina, no por sprint) y
# todos los consumidores leen de ahi. No se importa de b9_pleomorfismo: ese modulo necesita
# zarr y este driver corre en `clam_latest`, que no lo tiene.
OFFSETS = REPO / "sprints/B8_sprint8/anotaciones_patologo"

TAREA = "carcinoma_ductal_insitu_presente_pth_balance"
DIR_CKPT = ENVIRON / "results_modelo_pth_balance" / f"{TAREA}_s1"
CKPT = DIR_CKPT / "s_0_checkpoint.pt"
SPLITS = DIR_CKPT / "splits_0.csv"
CSV_LABEL = ENVIRON / "csv/dataset_carcinoma_ductal_in_situ_presente_label.csv"

# `--auto-label-dict` ordena alfabeticamente los labels unicos del CSV. El state_dict tiene
# classifiers.0/1/2, o sea 3 clases, lo que confirma el orden.
CLASES = ["no", "no_identificado", "si"]

# Las cinco clases del geojson que son CDIS. Las dos ultimas NO existian en el vocabulario de
# las doce del B9; son patrones arquitectonicos de DCIS en el checklist del CAP (Nota C).
CDIS = {"CDIS_solido", "DCIS", "CDIS_papilar", "CDIS_cribiforme", "CDIS_micropapilar"}

# El censo del prereg §0.a, para que el script falle ruidosamente si el material cambia.
CON_POLIGONOS = ["110616", "124729", "124806", "126504", "128250",
                 "131461-1", "132844", "142541-1", "164001", "B25-158899"]
CONTROL_NEGATIVO = ["103762", "106552", "109609", "110962",
                    "128194", "132208", "141426-1", "144317"]
# Etiqueta `si` y CERO poligonos: positivos NO ANOTADOS. No son negativos y salen de los dos
# grupos (prereg §0.a.1).
SI_SIN_POLIGONO = ["129741", "133677", "154144"]

N_TRANSL = 200
SEMILLA = 20260909


def tiers() -> dict:
    """slide_id -> train/val/test, del unico fold que existe para esta tarea."""
    import pandas as pd
    df = pd.read_csv(SPLITS, dtype=str)
    t = {}
    for c in ("train", "val", "test"):
        for v in df[c].dropna().astype(str).str.strip():
            t[v] = c
    return t


def etiquetas() -> dict:
    import pandas as pd
    df = pd.read_csv(CSV_LABEL, dtype=str)
    return dict(zip(df["slide_id"].astype(str).str.strip(),
                    df["label"].astype(str).str.strip()))


def parches_cdis(slide: str, coords: np.ndarray, step: int) -> np.ndarray:
    """Indices de los parches cuyo CENTRO cae dentro de algun poligono de CDIS."""
    from matplotlib.path import Path as MPath
    off = json.loads((OFFSETS / f"offset_{slide}.json").read_text())
    dx, dy = float(off["dx"]), float(off["dy"])
    js = json.loads(geojson_de(slide).read_text())
    centros = coords.astype(float) + step / 2.0
    dentro = np.zeros(len(coords), dtype=bool)
    n_pol = 0
    for ft in js.get("features", []):
        cl = ft.get("properties", {}).get("classification", {})
        nombre = cl.get("name") if isinstance(cl, dict) else str(cl)
        if nombre not in CDIS:
            continue
        g = ft["geometry"]
        anillos = g["coordinates"] if g["type"] == "Polygon" else g["coordinates"][0]
        p = np.asarray(anillos[0], float) + np.array([dx, dy])
        if len(p) < 3:
            continue
        n_pol += 1
        dentro |= MPath(p).contains_points(centros)
    return np.nonzero(dentro)[0], n_pol


def atencion_json_out(slide: str, coords: np.ndarray):
    """Atencion del ensemble de sgaete, alineada al orden de `coords` del h5. SOLO LECTURA."""
    d = json.loads((JSON_OUT / f"{slide}__{TAREA}.json").read_text())
    c = np.asarray(d["coords"], dtype=np.int64)
    w = np.asarray(d["weights"], dtype=np.float64)
    if len(c) != len(coords):
        raise ValueError(f"{slide}: {len(c)} coords en el json vs {len(coords)} en el h5")
    pos = {(int(a), int(b)): i for i, (a, b) in enumerate(c)}
    orden = np.array([pos[(int(a), int(b))] for a, b in coords], dtype=np.int64)
    return w[orden], d.get("predicted_label"), float(d.get("confidence", float("nan")))


def atencion_ckpt(feats: np.ndarray, cabeza: str, lab: str | None):
    """Atencion del UNICO fold, leyendo la rama pedida. Devuelve (A, rama_usada)."""
    model, _ = build_clam(len(CLASES), str(CKPT))
    A, _prob, y_hat = get_attention(model, feats)
    if cabeza == "verdadera":
        if lab not in CLASES:
            return None, None
        j = CLASES.index(lab)
    else:
        j = int(y_hat)
    return A[j], CLASES[j]


def medir(slide, scores, coords, idx_pos, step, rng, extra, n_transl=N_TRANSL):
    """AUC de rango + IC de Hanley-McNeil + p por traslacion rigida. Una fila."""
    r = ranks_of(scores)
    auc = rank_auc(r, idx_pos)
    n_pos, n_neg = len(idx_pos), len(coords) - len(idx_pos)
    ee, lo, hi = ic_hanley_mcneil(auc, n_pos, n_neg)
    p, obs, acc, _m = p_traslacion(r, coords, idx_pos, step, n_transl, rng)
    if abs(obs - auc) > 1e-9:
        raise AssertionError(f"{slide}: obs del nulo {obs} != auc {auc}")
    return dict(slide=slide, n_parches=len(coords), n_marcados=n_pos, auc=auc, ee=ee,
                ic95_lo=lo, ic95_hi=hi, p_nulo=p, n_iter_nulo=acc, **extra)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(REPO / "results/b10_cdis"))
    ap.add_argument("--n-transl", type=int, default=N_TRANSL)
    ap.add_argument("--slides", nargs="*", default=None,
                    help="restringe el grupo con poligonos (para probar el driver)")
    ap.add_argument("--sin-control", action="store_true")
    a = ap.parse_args()
    import pandas as pd
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEMILLA)
    tier, labs = tiers(), etiquetas()

    print("=" * 108)
    print("O3 — ¿la atención de CLAM localiza el CDIS?")
    print("=" * 108)
    print(f"prereg: sprints/B10_sprint10/cdis_localizacion/prereg.md")
    print(f"tarea: {TAREA}   |   UN solo fold ({CKPT.name}), no hay familia 5fold")
    print(f"nulo: traslación rígida, {a.n_transl} iteraciones (piso p = {1/(a.n_transl+1):.5f})")
    print(f"unidad: parche. positivos = centro dentro de un polígono de CDIS\n")

    filas, saltadas = [], []
    print(f"  {'lámina':<12} {'tier':<6} {'etiq':<16} {'pol':>4} {'parches':>8} {'CDIS':>5}  "
          f"{'fuente':<22} {'rama':<16} {'AUC':>6} {'p':>8}")

    con_pol = a.slides if a.slides else CON_POLIGONOS
    for slide in con_pol:
        feats, coords = leer_h5(slide)
        step = paso_de_grilla(coords)
        idx_pos, n_pol = parches_cdis(slide, coords, step)
        lab = labs.get(slide)
        tr = tier.get(slide, "fuera")
        if len(idx_pos) == 0:
            saltadas.append(dict(slide=slide, motivo="cero parches bajo polígono de CDIS",
                                 n_pol=n_pol))
            print(f"  {slide:<12} {tr:<6} {str(lab):<16} {n_pol:>4} {len(coords):>8} "
                  f"{0:>5}  -> sin parches positivos, se declara y sale")
            continue

        # brazo 1: json_out (ensemble 5 folds, rama PREDICHA, familia _pth_balance)
        try:
            sc, pred, conf = atencion_json_out(slide, coords)
            f = medir(slide, sc, coords, idx_pos, step, rng,
                      dict(fuente="json_out_ensemble", rama=f"predicha:{pred}", tier=tr,
                           etiqueta=str(lab), n_poligonos=n_pol, confianza=conf),
                      n_transl=a.n_transl)
            filas.append(f)
            print(f"  {slide:<12} {tr:<6} {str(lab):<16} {n_pol:>4} {len(coords):>8} "
                  f"{len(idx_pos):>5}  {'json_out_ensemble':<22} {str(pred):<16} "
                  f"{f['auc']:>6.3f} {f['p_nulo']:>8.4f}")
        except Exception as e:                      # noqa: BLE001
            saltadas.append(dict(slide=slide, motivo=f"json_out: {type(e).__name__}: {e}"))

        # brazo 2: checkpoint, las dos ramas. La VERDADERA es la que manda (prereg §1.b)
        for cabeza in ("verdadera", "predicha"):
            A, rama = atencion_ckpt(feats, cabeza, lab)
            if A is None:
                saltadas.append(dict(slide=slide,
                                     motivo=f"ckpt/{cabeza}: sin etiqueta usable ({lab})"))
                print(f"  {slide:<12} {'':<6} {'':<16} {'':>4} {'':>8} {'':>5}  "
                      f"{'ckpt_' + cabeza:<22} {'(sin etiqueta)':<16}")
                continue
            f = medir(slide, A, coords, idx_pos, step, rng,
                      dict(fuente=f"ckpt_1fold_{cabeza}", rama=f"{cabeza}:{rama}", tier=tr,
                           etiqueta=str(lab), n_poligonos=n_pol, confianza=float("nan")),
                      n_transl=a.n_transl)
            filas.append(f)
            print(f"  {slide:<12} {'':<6} {'':<16} {'':>4} {'':>8} {'':>5}  "
                  f"{'ckpt_1fold_' + cabeza:<22} {rama:<16} {f['auc']:>6.3f} "
                  f"{f['p_nulo']:>8.4f}")

    # --- control negativo: no hay AUC que calcular (no hay polígonos). Se mide otra cosa y
    #     se dice: qué predice el modelo y cuánta atención concentra, sin promediar con arriba.
    print(f"\n  control negativo ({len(CONTROL_NEGATIVO)} láminas etiquetadas `no`): "
          f"no tienen polígonos, así que NO hay AUC. Se reporta predicción y concentración.")
    neg = []
    for slide in ([] if a.sin_control else CONTROL_NEGATIVO):
        feats, coords = leer_h5(slide)
        lab, tr = labs.get(slide), tier.get(slide, "fuera")
        try:
            sc, pred, conf = atencion_json_out(slide, coords)
        except Exception:                            # noqa: BLE001
            sc, pred, conf = None, None, float("nan")
        A, rama = atencion_ckpt(feats, "verdadera", lab)
        fila = dict(slide=slide, tier=tr, etiqueta=str(lab), n_parches=len(coords),
                    pred_ensemble=str(pred), confianza=conf)
        for nom, v in (("json_out", sc), ("ckpt_verdadera", A)):
            if v is None:
                continue
            w = np.asarray(v, float); w = w / w.sum() if w.sum() > 0 else w
            ent = float(-(w[w > 0] * np.log(w[w > 0])).sum())
            fila[f"n_eff_{nom}"] = float(np.exp(ent))
            fila[f"frac_eff_{nom}"] = float(np.exp(ent) / len(coords))
        neg.append(fila)
        print(f"  {slide:<12} {tr:<6} {str(lab):<16} {len(coords):>8} parches  "
              f"pred={str(pred):<16} n_eff_ckpt="
              f"{fila.get('n_eff_ckpt_verdadera', float('nan')):8.1f} "
              f"({100*fila.get('frac_eff_ckpt_verdadera', float('nan')):.1f} %)")

    print(f"\n  positivos NO anotados (etiqueta `si`, cero polígonos), fuera de los dos grupos: "
          f"{', '.join(SI_SIN_POLIGONO)}")

    # --- universo REGIÓN (agregado el 10-sep, resultados §3.a). Sólo las láminas con más de una
    #     región de escaneo, con el `medir` y el `universos_de` del B9 sin tocar: el intervalo
    #     viene fijado desde el B9 en `cruce_94_marcas.REGION_ANOTADA`, no se elige acá. RNG
    #     propio, para que las filas de arriba, ya publicadas, no se muevan ni un bit.
    rng_reg = np.random.default_rng(SEMILLA)
    reg = []
    multi = [s for s in con_pol if s in REGION_ANOTADA]
    if multi:
        print(f"\n  universo REGIÓN (láminas con más de una región de escaneo): {', '.join(multi)}")
    for slide in multi:
        feats, coords = leer_h5(slide)
        step = paso_de_grilla(coords)
        idx_pos, n_pol = parches_cdis(slide, coords, step)
        lab, tr = labs.get(slide), tier.get(slide, "fuera")
        sc, pred, conf = atencion_json_out(slide, coords)
        brazos = [(sc, "json_out_ensemble", f"predicha:{pred}", conf)]
        for cabeza in ("verdadera", "predicha"):
            A, rama = atencion_ckpt(feats, cabeza, lab)
            if A is not None:
                brazos.append((A, f"ckpt_1fold_{cabeza}", f"{cabeza}:{rama}", float("nan")))
        for v, fuente, rama, cf in brazos:
            extra = dict(fuente=fuente, rama=rama, tier=tr, etiqueta=str(lab),
                         n_poligonos=n_pol, confianza=cf)
            ref = [g["auc"] for g in filas if g["slide"] == slide and g["fuente"] == fuente]
            for f in medir_por_universo(slide, v, coords, idx_pos, step, a.n_transl, rng_reg,
                                        extra):
                # Chequeo gratis: en el universo `lamina` el AUC tiene que ser el de la tabla
                # principal, que salió por el otro camino (`medir` de este archivo). La fila NO
                # se guarda: su `p` sale de otro RNG, y dos `p` para la misma celda confunden.
                if f["universo"] == "lamina":
                    if not ref or abs(ref[0] - f["auc"]) > 1e-12:
                        raise AssertionError(f"{slide}/{fuente}: AUC lamina {f['auc']} != {ref}")
                    continue
                reg.append(dict(f, auc_lamina_entera=ref[0] if ref else float("nan")))
                print(f"  {slide:<12} {f['universo']:<7} {f['n_parches']:>6} parches "
                      f"{f['n_marcados']:>3} CDIS  {fuente:<22} {rama:<16} "
                      f"AUC {f['auc']:.3f} [{f['ic95_lo']:.3f} · {f['ic95_hi']:.3f}]  "
                      f"p {f['p_nulo']:.4f} ({f['n_iter_nulo']} trasl.)  "
                      f"lámina entera {ref[0] if ref else float('nan'):.3f}")

    pd.DataFrame(filas).to_csv(Path(a.out) / "auc_cdis.csv", index=False)
    if reg:
        pd.DataFrame(reg).to_csv(Path(a.out) / "auc_cdis_region.csv", index=False)
        print(f"escrito: {a.out}/auc_cdis_region.csv ({len(reg)} filas)")
    pd.DataFrame(neg).to_csv(Path(a.out) / "control_negativo.csv", index=False)
    if saltadas:
        pd.DataFrame(saltadas).to_csv(Path(a.out) / "saltadas.csv", index=False)
    print(f"\nescrito: {a.out}/auc_cdis.csv ({len(filas)} filas), control_negativo.csv"
          + (f", saltadas.csv ({len(saltadas)})" if saltadas else ""))


if __name__ == "__main__":
    main()
