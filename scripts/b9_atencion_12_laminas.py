"""b9_atencion_12_laminas.py — ¿la atención de CLAM cae sobre las mitosis, en las DOCE? (B9)

Extiende a las doce láminas anotadas la medición que el B8 hizo sobre una sola
(`scripts/atencion_vs_anotaciones.py`). Pre-registro:
`sprints/B9_sprint9/atencion_12_laminas/prereg.md`, escrito ANTES de este archivo.

Dos fuentes de atención, MISMO esquema de salida (prereg §2):

  --fuente json_out     PRIMARIO. Lee `clam_ensemble/attn_batch/json_out/<slide>__<tarea>.json`,
                        de `sgaete`, SÓLO LECTURA. Es un ENSEMBLE de los cinco folds con la rama
                        de la clase PREDICHA y familia `_pth_balance` ⇒ CONTAMINADO por
                        construcción. Las tres propiedades se escriben en `meta.json` y hay que
                        declararlas en toda tabla. Su campo `patch_size` NO se usa: miente
                        ([[patch-size-desde-geometria-h5]]).

  --fuente ckpt_limpio  CONTROL de honestidad. Recalcula la atención desde
                        `results_modelo_combined_5fold/...` promediando SÓLO los folds donde la
                        lámina no estuvo en `train`, y reporta el tier (ausente > test > val).

Estadísticos IMPORTADOS de los scripts del B8, no copiados (prereg §4). El `CKPTS` de
`atencion_vs_anotaciones.py` está atado a otro pre-registro y NO se toca.

Gate de regresión (prereg §5.a): `--gate` recomputa la 129741 con la cabeza VERDADERA por
checkpoint 5fold y compara a 1e-6 contra los cuatro valores del B8.

CPU, post-hoc, sin GPU. Uso (workaround B — binario absoluto, `clam_latest` por `topk`):

  CUDA_VISIBLE_DEVICES="" /home/sdonoso/miniconda3/envs/clam_latest/bin/python \
      scripts/b9_atencion_12_laminas.py --fuente json_out
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path("/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto")
CLAM_ENVIRON = Path("/media/administrador/Storage1/sdonoso/clam_environ")
ENVIRON = CLAM_ENVIRON / "environ"
JSON_OUT = Path("/media/administrador/Storage1/sdonoso/clam_ensemble/attn_batch/json_out")
for _p in (str(REPO), str(CLAM_ENVIRON)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from scripts.atencion_vs_anotaciones import (      # noqa: E402
    build_clam, get_attention, p_traslacion, rank_auc, ranks_of,
)
from scripts.auc_atencion_fold4 import ic_hanley_mcneil                    # noqa: E402
from scripts.cruce_94_marcas import MPP, REGION_ANOTADA, SLIDES            # noqa: E402

# Las dos tareas que pidió Ernesto. El `json_out` las tiene para las doce.
TAREA_MITOSIS = "grado_histologico_mitotic_rate_pth_balance"
TAREA_GATE = "invasion_carcinoma_gate_pth_balance"

# Familia del brazo limpio: es la del gate de regresión del B8 y la única con 5 folds propios
# de la tarea de tasa mitótica ([[gate-regresion-valor-exacto-no-banda]]).
DIR_5FOLD = ENVIRON / "results_modelo_combined_5fold/grado_histologico_mitotic_rate_combined_s1"
SPLITS_5FOLD = ENVIRON / "splits_5fold/grado_histologico_mitotic_rate_combined_100"
CSV_LABEL = ENVIRON / "csv/dataset_grado_histologico_tasa_mitotica_label.csv"

# Orden alfabético de --auto-label-dict sobre los labels del CSV (verificado en el B8).
CLASSES_4 = ["no_identificado", "score_1", "score_2", "score_3"]

# Población primaria: las nueve con score_1/2/3 (prereg §3, decisión de Ernesto del 1-sep).
NO_PRIMARIO = {"106552": "no_identificado", "110616": "no_identificado",
               "B25-158899": "sin fila en el CSV de la tarea"}

# Gate exacto del B8, universo x checkpoint, sobre la 129741 y la cabeza VERDADERA.
# `sprints/B8_sprint8/atencion_vs_patologo/{,con_region/}auc_por_checkpoint.csv`.
GATE = {("seba_5fold_f0", "lamina"): 0.925697, ("seba_5fold_f0", "region"): 0.936444,
        ("seba_5fold_f2", "lamina"): 0.916527, ("seba_5fold_f2", "region"): 0.927269}

GRUPO = "Mitosis"


# --------------------------------------------------------------------------- geometría
def paso_de_grilla(coords: np.ndarray) -> int:
    """Moda del paso entre coords consecutivas, POR FILA ([[patch-size-desde-geometria-h5]]).

    Nunca desde la magnificación, y nunca sobre el `unique` global del eje: el `patch_size`
    del `json_out` es justamente lo que sale de hacerlo mal (da 127 y 64 donde acá da 256).
    """
    diffs = []
    for y in np.unique(coords[:, 1])[:400]:
        xs = np.sort(coords[coords[:, 1] == y][:, 0])
        d = np.diff(xs)
        diffs += d[d > 0].tolist()
    if not diffs:
        raise ValueError("no se pudo derivar el paso de la grilla")
    return int(Counter(diffs).most_common(1)[0][0])


def leer_h5(slide: str):
    import h5py
    with h5py.File(ENVIRON / "features/h5_files" / f"{slide}.h5", "r") as f:
        return np.array(f["features"]), np.array(f["coords"])


def universos_de(slide: str, coords: np.ndarray, idx_pos: np.ndarray) -> dict:
    """`lamina` siempre; `region` sólo en las dos con más de una región de escaneo.

    El confinamiento va como INTERVALO por lámina: el escalar `Y_CORTE_REGION = 49920` de
    `techo_atencion_topk.py:45` es de la 129741 y da vuelta la B25-158899, donde el patólogo
    anotó la región de ARRIBA.
    """
    u = {"lamina": np.arange(len(coords))}
    if slide in REGION_ANOTADA:
        lo, hi = REGION_ANOTADA[slide]
        sel = (coords[:, 1] >= lo) & (coords[:, 1] < hi)
        y_pos = coords[idx_pos, 1]
        if not ((y_pos >= lo) & (y_pos < hi)).all():
            raise ValueError(f"{slide}: hay marcas fuera de REGION_ANOTADA {lo}-{hi}")
        u["region"] = np.where(sel)[0]
    return u


# --------------------------------------------------------------------------- membresía
def membresia_folds() -> dict:
    """Por lámina: en qué folds NO estuvo en `train`, y con qué tier.

    «Limpio» son TRES cosas y el orden es ausente > test > val (`hechos_verificados.md` §3):
    una lámina en `val` gobernó el early stopping, así que su limpieza es más débil.
    """
    out = {s: {} for s in SLIDES}
    for f in range(5):
        df = pd.read_csv(SPLITS_5FOLD / f"splits_{f}.csv", dtype=str)
        rol = {}
        for col in ("train", "val", "test"):
            for v in df[col].dropna():
                rol[str(v).strip()] = col
        for s in SLIDES:
            r = rol.get(s)
            if r is None:
                out[s][f] = "ausente"
            elif r != "train":
                out[s][f] = r
    return out


def etiquetas() -> dict:
    df = pd.read_csv(CSV_LABEL, dtype=str)
    col_id = "slide_id" if "slide_id" in df.columns else df.columns[0]
    col_lb = "label" if "label" in df.columns else df.columns[-1]
    m = {str(a).strip(): str(b).strip() for a, b in zip(df[col_id], df[col_lb])}
    return {s: m.get(s) for s in SLIDES}


# --------------------------------------------------------------------------- fuentes
def atencion_json_out(slide: str, tarea: str, coords: np.ndarray) -> tuple:
    """Lee la atención ya calculada del `json_out` de `sgaete`. SÓLO LECTURA.

    El join es por COORDENADA y es exacto (mismo h5). Devuelve el vector alineado al orden
    de `coords` del h5, más la etiqueta predicha y la confianza del ensemble.
    """
    p = JSON_OUT / f"{slide}__{tarea}.json"
    d = json.loads(p.read_text())
    c = np.asarray(d["coords"], dtype=np.int64)
    w = np.asarray(d["weights"], dtype=np.float64)
    if len(c) != len(coords):
        raise ValueError(f"{slide}/{tarea}: {len(c)} coords en el json vs {len(coords)} en el h5")
    pos = {(int(a), int(b)): i for i, (a, b) in enumerate(c)}
    orden = np.array([pos[(int(a), int(b))] for a, b in coords], dtype=np.int64)
    return w[orden], d.get("predicted_label"), float(d.get("confidence", float("nan")))


def atencion_ckpt(slide: str, feats: np.ndarray, folds: dict, cabeza: str):
    """Promedia la atención de los checkpoints 5fold LIMPIOS de esta lámina.

    `cabeza` = 'verdadera' (la clase del CSV de labels) o 'predicha' (la del fold). Con la
    verdadera, una lámina sin fila en el CSV no se puede medir y se salta.
    """
    lab = etiquetas().get(slide)
    acc, usados = [], []
    for f in sorted(folds):
        ck = DIR_5FOLD / f"s_{f}_checkpoint.pt"
        if not ck.exists():
            continue
        model, _ = build_clam(len(CLASSES_4), str(ck))
        A, _prob, y_hat = get_attention(model, feats)
        if cabeza == "verdadera":
            if lab not in CLASSES_4:
                return None, [], lab
            j = CLASSES_4.index(lab)
        else:
            j = int(y_hat)
        acc.append(A[j])
        usados.append(f)
    if not acc:
        return None, [], lab
    return np.mean(np.vstack(acc), axis=0), usados, lab


# --------------------------------------------------------------------------- medición
def medir(slide, scores, coords, idx_pos, step, n_transl, rng, extra):
    """Una fila por universo: AUC de rango, IC de Hanley-McNeil y p por traslación rígida."""
    filas = []
    for uni, idx_u in universos_de(slide, coords, idx_pos).items():
        pos_u = np.array(sorted(set(idx_pos.tolist()) & set(idx_u.tolist())), dtype=np.int64)
        r = ranks_of(scores[idx_u])
        # `rank_auc` toma rangos posicionales dentro del universo.
        loc = {g: i for i, g in enumerate(idx_u)}
        pos_loc = np.array([loc[i] for i in pos_u], dtype=np.int64)
        auc = rank_auc(r, pos_loc)
        n_pos, n_neg = len(pos_u), len(idx_u) - len(pos_u)
        ee, lo, hi = ic_hanley_mcneil(auc, n_pos, n_neg)
        # `p_traslacion` indexa por posición GLOBAL, pero los rangos tienen que ser los
        # LOCALES del universo o el `obs` del nulo no sería el `auc` que se reporta. Se
        # dispersan los locales en un vector de largo N, igual que `atencion_vs_anotaciones`
        # hace para su universo `region_anotada` (:311).
        r_glob = np.empty(len(coords), dtype=np.float64)
        r_glob[idx_u] = r
        p, obs, acc, _m = p_traslacion(r_glob, coords, pos_u, step, n_transl, rng,
                                       universo=idx_u)
        if abs(obs - auc) > 1e-9:
            raise AssertionError(f"{slide}/{uni}: obs del nulo {obs} != auc {auc}")
        filas.append(dict(slide=slide, universo=uni, n_parches=len(idx_u), n_marcados=n_pos,
                          auc=auc, ee=ee, ic95_lo=lo, ic95_hi=hi,
                          p_nulo=p, n_iter_nulo=acc, auc_nulo_obs=obs, **extra))
    return filas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fuente", choices=["json_out", "ckpt_limpio"], default="json_out")
    ap.add_argument("--cabeza", choices=["verdadera", "predicha"], default=None,
                    help="sólo para ckpt_limpio; json_out trae la predicha por construcción")
    ap.add_argument("--n-transl", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--out-dir", default=str(REPO / "results/b9_atencion_12"))
    ap.add_argument("--gate", action="store_true",
                    help="corre SÓLO el gate de regresión del prereg §5.a y sale")
    args = ap.parse_args()

    if args.gate:
        return gate()

    out = Path(args.out_dir); out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)
    memb, labs = membresia_folds(), etiquetas()
    filas, geo = [], []

    for slide in SLIDES:
        feats, coords = leer_h5(slide)
        step = paso_de_grilla(coords)
        ann = pd.read_csv(REPO / "sprints/B8_sprint8/anotaciones_patologo"
                          / f"parches_anotados_{slide}.csv")
        idx_of = {(int(a), int(b)): i for i, (a, b) in enumerate(coords)}
        marc = []
        for r in ann.itertuples():
            if GRUPO in [c.strip() for c in str(r.clases).split("|")]:
                i = idx_of.get((int(r.x), int(r.y)))
                if i is None:
                    raise ValueError(f"{slide}: parche anotado ({r.x},{r.y}) no está en el h5")
                marc.append(i)
        idx_pos = np.array(sorted(set(marc)), dtype=np.int64)
        tier = sorted(set(memb[slide].values()),
                      key=lambda t: ["ausente", "test", "val"].index(t)) or ["contaminada"]
        geo.append(dict(slide=slide, n_parches=len(coords), paso_px=step,
                        mm2=len(coords) * (step * MPP / 1000.0) ** 2,
                        n_marcados=len(idx_pos), label=labs.get(slide),
                        folds_limpios="+".join(str(f) for f in sorted(memb[slide])),
                        tier="/".join(tier),
                        primario=slide not in NO_PRIMARIO))
        base = dict(fuente=args.fuente, label=labs.get(slide),
                    primario=slide not in NO_PRIMARIO,
                    tier_fold="/".join(tier),
                    folds_usados="+".join(str(f) for f in sorted(memb[slide])))

        if args.fuente == "json_out":
            for tarea in (TAREA_MITOSIS, TAREA_GATE):
                sc, pred, conf = atencion_json_out(slide, tarea, coords)
                filas += medir(slide, sc, coords, idx_pos, step, args.n_transl, rng,
                               dict(base, tarea=tarea, cabeza="predicha_ensemble",
                                    predicha=pred, confianza=conf))
        else:
            cab = args.cabeza or "verdadera"
            sc, usados, lab = atencion_ckpt(slide, feats, memb[slide], cab)
            if sc is None:
                print(f"[skip] {slide}: cabeza {cab} no disponible (label={lab})")
                continue
            filas += medir(slide, sc, coords, idx_pos, step, args.n_transl, rng,
                           dict(base, tarea=TAREA_MITOSIS.replace("_pth_balance",
                                                                  "_combined_5fold"),
                                cabeza=cab, predicha=None, confianza=float("nan"),
                                folds_usados="+".join(str(f) for f in usados)))
        print(f"[ok] {slide}: N={len(coords)} paso={step} marcados={len(idx_pos)} "
              f"tier={'/'.join(tier)}")

    df = pd.DataFrame(filas)
    dg = pd.DataFrame(geo)
    suf = "" if args.fuente == "json_out" else f"_{args.fuente}"
    df.to_csv(out / f"auc_por_lamina{suf}.csv", index=False)
    dg.to_csv(out / "geometria_por_lamina.csv", index=False)

    meta = dict(
        fuente=args.fuente, seed=args.seed, n_transl=args.n_transl, grupo=GRUPO, mpp=MPP,
        prereg="sprints/B9_sprint9/atencion_12_laminas/prereg.md",
        conteos=dict(laminas=len(SLIDES), primario=int(dg["primario"].sum()),
                     parches_marcados=int(dg["n_marcados"].sum()),
                     parches_marcados_primario=int(dg.loc[dg["primario"], "n_marcados"].sum())),
        declaracion_json_out=[
            "ensemble de los CINCO folds ponderado por confianza: contaminado por construcción",
            "lee la rama de la clase PREDICHA por cada fold, no la verdadera",
            "familia _pth_balance, NO la _combined_5fold de los números del B8",
            "su campo patch_size no se usa: da 127 y 64 donde la geometría del h5 da 256",
        ],
        unidades="parche (no marca, no detección, no lámina)",
    )
    (out / f"meta{suf}.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))

    prim = df[df["primario"] & (df["universo"] == "lamina")]
    print("\n== agregado (media sin ponderar sobre láminas, universo lámina) ==")
    for t, g in prim.groupby("tarea"):
        print(f"  {t:52s} n={len(g):2d}  AUC {g['auc'].mean():.3f} ± {g['auc'].std():.3f}")
    todo = df[df["universo"] == "lamina"]
    for t, g in todo.groupby("tarea"):
        print(f"  [las doce] {t:41s} n={len(g):2d}  AUC {g['auc'].mean():.3f}")
    print(f"\n  escrito: {out / ('auc_por_lamina' + suf + '.csv')}")
    return 0


def gate():
    """Prereg §5.a: reproducir a 1e-6 los cuatro valores del B8 sobre la 129741."""
    slide = "129741"
    feats, coords = leer_h5(slide)
    ann = pd.read_csv(REPO / "sprints/B8_sprint8/anotaciones_patologo"
                      / f"parches_anotados_{slide}.csv")
    idx_of = {(int(a), int(b)): i for i, (a, b) in enumerate(coords)}
    idx_pos = np.array(sorted({idx_of[(int(r.x), int(r.y))] for r in ann.itertuples()
                               if GRUPO in [c.strip() for c in str(r.clases).split("|")]}))
    lab = etiquetas()[slide]
    j = CLASSES_4.index(lab)
    print(f"[gate] {slide} label={lab} cabeza j={j} marcados={len(idx_pos)}")
    ok = True
    for cid, f in (("seba_5fold_f0", 0), ("seba_5fold_f2", 2)):
        model, _ = build_clam(len(CLASSES_4), str(DIR_5FOLD / f"s_{f}_checkpoint.pt"))
        A, _p, _y = get_attention(model, feats)
        for uni, idx_u in universos_de(slide, coords, idx_pos).items():
            r = ranks_of(A[j][idx_u])
            loc = {g: i for i, g in enumerate(idx_u)}
            pos_loc = np.array([loc[i] for i in idx_pos if i in loc])
            got = rank_auc(r, pos_loc)
            exp = GATE[(cid, uni)]
            d = abs(got - exp)
            print(f"  {cid:16s} {uni:7s} esperado {exp:.6f}  obtenido {got:.6f}  "
                  f"|Δ|={d:.2e}  {'OK' if d < 1e-6 else 'FALLA'}")
            ok &= d < 1e-6
    print("[gate]", "PASA" if ok else "FALLA — es bug del driver, no resultado")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
