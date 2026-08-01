"""atencion_vs_anotaciones.py — ¿la atención de CLAM cae donde marcó el patólogo? (B8)

Responde el experimento del §4 de `sprints/B8_sprint8/tareas_geometricas/README.md` sobre la
lámina 129741, la única con anotaciones de objeto del patólogo (vía QuPath, ya realineadas
por `scripts/alinear_anotaciones_qupath.py`).

Pre-registro: `sprints/B8_sprint8/atencion_vs_patologo/prereg.md` (escrito ANTES de correr;
fija la familia de checkpoint y el estadístico).

Qué mide, por checkpoint y por cabeza de clase:
  - AUC de ranking = P(un parche anotado recibe más atención que uno no anotado).
    Nulo = 0.5. Es Mann-Whitney U normalizado.
  - percentil mediano de los parches anotados entre los N de la lámina.
  - p por permutación simple de etiquetas (OPTIMISTA a propósito, se reporta para contraste).
  - p por TRASLACIÓN RÍGIDA de la máscara anotada sobre la grilla (el nulo honesto: preserva
    forma y contigüidad del grupo, solo mueve dónde está).

Gotcha CLAM (CLAUDE.md, hechos validados): `model(x, attention_only=True)` devuelve A
**PRE-softmax**. Hay que aplicar `softmax(A_raw, dim=1)` sobre los N parches. CLAM_MB tiene
una cabeza por clase ⇒ todo se reporta por clase.

Etapa 0: CPU, post-hoc, sin GPU, sin sbatch. NO toca modelo ni training.
Uso (workaround B — binario absoluto del env, nunca `python` a secas):
  CUDA_VISIBLE_DEVICES="" /home/sdonoso/miniconda3/envs/clam_latest/bin/python \
      scripts/atencion_vs_anotaciones.py \
      --out-dir sprints/B8_sprint8/atencion_vs_patologo
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
import torch

REPO = Path("/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto")
CLAM_ENVIRON = "/media/administrador/Storage1/sdonoso/clam_environ"
ENVIRON = Path(CLAM_ENVIRON) / "environ"
for p in (str(REPO), CLAM_ENVIRON):
    if p not in sys.path:
        sys.path.insert(0, p)

EMBED_DIM = 512
DROP_OUT = 0.25
B_SAMPLE = 8
SLIDE = "129741"

# Orden de clases: sale de --auto-label-dict (alfabético sobre los labels del CSV).
# Verificado contra los CSV de labels el 1-ago-2026 (prereg §4).
CLASSES_4 = ["no_identificado", "score_1", "score_2", "score_3"]
CLASSES_3 = ["score_1", "score_2", "score_3"]

# Registro de checkpoints con el ROL fijado en el pre-registro. No se reordena
# después de ver los números.
CKPTS = [
    # --- PRIMARIO: 129741 nunca vista en entrenamiento ---
    dict(id="seba_privado_s0", rol="primario", split="val", classes=CLASSES_4,
         desc="privado, 4 clases, single-split",
         path=f"{ENVIRON}/results_modelo/grado_histologico_mitotic_rate_s1/s_0_checkpoint.pt"),
    dict(id="seba_combined_s0", rol="primario", split="val", classes=CLASSES_4,
         desc="priv+TCGA, 4 clases, single-split",
         path=f"{ENVIRON}/results_modelo_combined/grado_histologico_mitotic_rate_combined_s1/s_0_checkpoint.pt"),
    dict(id="seba_5fold_f0", rol="primario", split="val", classes=CLASSES_4,
         desc="priv+TCGA, 4 clases, 5-fold fold 0",
         path=f"{ENVIRON}/results_modelo_combined_5fold/grado_histologico_mitotic_rate_combined_s1/s_0_checkpoint.pt"),
    dict(id="seba_5fold_f2", rol="primario", split="val", classes=CLASSES_4,
         desc="priv+TCGA, 4 clases, 5-fold fold 2",
         path=f"{ENVIRON}/results_modelo_combined_5fold/grado_histologico_mitotic_rate_combined_s1/s_2_checkpoint.pt"),
    # --- CONTROL INTERNO: misma corrida, lámina vista en train ---
    dict(id="seba_5fold_f1", rol="control_interno", split="train", classes=CLASSES_4,
         desc="priv+TCGA, 4 clases, 5-fold fold 1",
         path=f"{ENVIRON}/results_modelo_combined_5fold/grado_histologico_mitotic_rate_combined_s1/s_1_checkpoint.pt"),
    dict(id="seba_5fold_f3", rol="control_interno", split="train", classes=CLASSES_4,
         desc="priv+TCGA, 4 clases, 5-fold fold 3",
         path=f"{ENVIRON}/results_modelo_combined_5fold/grado_histologico_mitotic_rate_combined_s1/s_3_checkpoint.pt"),
    dict(id="seba_5fold_f4", rol="control_interno", split="train", classes=CLASSES_4,
         desc="priv+TCGA, 4 clases, 5-fold fold 4",
         path=f"{ENVIRON}/results_modelo_combined_5fold/grado_histologico_mitotic_rate_combined_s1/s_4_checkpoint.pt"),
]
# --- CORROBORACIÓN: nuestro k-fold de Tier 0, 3 clases, lámina en train en los 5 ---
for _f in range(5):
    CKPTS.append(dict(
        id=f"tier0_f{_f}", rol="corroboracion", split="train", classes=CLASSES_3,
        desc=f"nuestro k-fold Tier 0, 3 clases, fold {_f}",
        path=str(REPO / "results/pathpt_etapa1/mitotic"
                 / f"clam_grado_mitotic_3clases_pth_f{_f}_20260611_1730_s1"
                 / f"s_{_f}_checkpoint.pt")))

# Grupos de anotación: los dos de interés y los de contraste (prereg §4/§5).
GRUPOS_INTERES = ["Mitosis", "Nucleos alto grado"]


def build_clam(n_classes, ckpt_path, device="cpu"):
    """Reconstruye CLAM_MB tal como lo arma main.py y carga los pesos.

    Mismos args que `build_arm` de scripts/clam_vs_mammoth_attention.py:81 — se replica
    en vez de importarse para no arrastrar la dependencia de la librería Mammoth.
    """
    from topk.svm import SmoothTop1SVM
    from models.model_clam import CLAM_MB
    model = CLAM_MB(gate=True, size_arg="small", dropout=DROP_OUT, k_sample=B_SAMPLE,
                    n_classes=n_classes, subtyping=False,
                    instance_loss_fn=SmoothTop1SVM(n_classes=2), embed_dim=EMBED_DIM)
    ckpt = torch.load(ckpt_path, map_location=device)
    sd = ckpt.get("model", ckpt) if isinstance(ckpt, dict) else ckpt
    missing, unexpected = model.load_state_dict(sd, strict=False)
    if missing:
        raise ValueError(f"faltan pesos en {ckpt_path}: {missing[:5]}")
    model.to(device).eval()
    return model, unexpected


def get_attention(model, feats, device="cpu"):
    """A pre-softmax (n_classes, N) -> softmax sobre N. Devuelve también la predicción."""
    x = torch.from_numpy(feats).float().to(device)
    with torch.no_grad():
        A_raw = model(x, attention_only=True)      # (n_classes, N) PRE-softmax
        A = torch.softmax(A_raw, dim=1)            # normalizar sobre los N parches
        _, y_prob, y_hat, _, _ = model(x)
    return A.cpu().numpy().astype(np.float64), y_prob.cpu().numpy().ravel(), int(y_hat.item())


def ranks_of(scores):
    """Rangos medios (empates promediados): la atención puede saturar y repetir valores."""
    from scipy.stats import rankdata
    return rankdata(scores)


def rank_auc(ranks, pos_idx, n_total=None):
    """P(un anotado rankea por encima de uno no anotado). Mann-Whitney U normalizado.

    Toma los RANGOS ya calculados (no los scores) porque el nulo hace miles de llamadas
    sobre el mismo vector de atención — recalcular `rankdata` cada vez lo domina todo.
    """
    n = n_total if n_total is not None else len(ranks)
    n_pos = len(pos_idx)
    n_neg = n - n_pos
    if n_pos == 0 or n_neg == 0:
        return float("nan")
    return float((ranks[pos_idx].sum() - n_pos * (n_pos + 1) / 2.0) / (n_pos * n_neg))


def p_permutacion(ranks, pos_idx, n_iter, rng):
    """Nulo INGENUO: reasigna al azar qué parches son 'anotados'. Rompe la contigüidad
    espacial ⇒ p optimista. Se reporta solo para mostrar la diferencia con el nulo bueno."""
    obs = rank_auc(ranks, pos_idx)
    n, k = len(ranks), len(pos_idx)
    ge = 0
    for _ in range(n_iter):
        if rank_auc(ranks, rng.choice(n, size=k, replace=False)) >= obs:
            ge += 1
    return (1 + ge) / (1 + n_iter), obs


def p_traslacion(ranks, coords, pos_idx, step, n_iter, rng, min_frac=0.9, max_try=200000,
                 universo=None):
    """Nulo HONESTO: traslada rígidamente la máscara anotada sobre la grilla de la lámina.

    Preserva forma, tamaño y contigüidad del grupo; solo cambia DÓNDE está. Se aceptan
    las traslaciones donde al menos `min_frac` de los parches desplazados sigue cayendo
    sobre un parche extraído (si no, se estaría comparando contra el fondo).

    `universo`: si se pasa, las traslaciones se restringen a ese subconjunto de parches
    (se usa para confinar el nulo a la REGIÓN DE ESCANEO anotada — ver `--y-cut`).
    """
    if universo is None:
        universo = np.arange(len(coords))
    n_u = len(universo)
    obs = rank_auc(ranks, pos_idx, n_total=n_u)
    idx_of = {(int(a), int(b)): i for i, (a, b) in zip(universo, coords[universo])}
    pos_xy = coords[pos_idx]
    cu = coords[universo]
    xs = np.arange(cu[:, 0].min(), cu[:, 0].max() + step, step)
    ys = np.arange(cu[:, 1].min(), cu[:, 1].max() + step, step)
    dxs = ((xs - pos_xy[:, 0].min()) // step * step).astype(np.int64)
    dys = ((ys - pos_xy[:, 1].min()) // step * step).astype(np.int64)
    ge, acc, tries = 0, 0, 0
    nulls = []
    while acc < n_iter and tries < max_try:
        tries += 1
        dx = int(rng.choice(dxs)); dy = int(rng.choice(dys))
        if dx == 0 and dy == 0:
            continue
        shifted = [idx_of.get((int(a) + dx, int(b) + dy)) for a, b in pos_xy]
        keep = [i for i in shifted if i is not None]
        if len(keep) < min_frac * len(pos_xy):
            continue
        acc += 1
        v = rank_auc(ranks, np.array(keep), n_total=n_u)
        nulls.append(v)
        if v >= obs:
            ge += 1

    if acc == 0:
        return float("nan"), obs, 0, float("nan")
    return (1 + ge) / (1 + acc), obs, acc, float(np.mean(nulls))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--h5", default=f"{ENVIRON}/features/h5_files/{SLIDE}.h5")
    ap.add_argument("--anotaciones",
                    default=str(REPO / "sprints/B8_sprint8/anotaciones_patologo"
                               / f"parches_anotados_{SLIDE}.csv"))
    ap.add_argument("--out-dir", default=str(REPO / "sprints/B8_sprint8/atencion_vs_patologo"))
    ap.add_argument("--n-perm", type=int, default=2000)
    ap.add_argument("--n-transl", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--y-cut", type=int, default=49920,
                    help="frontera y entre las dos REGIONES DE ESCANEO del .bif "
                         "(openslide.region[1].y). Los parches anotados caen todos en la "
                         "de abajo; con esto se repite la medición confinada a esa región, "
                         "que descarta que el efecto sea 'una región recibe más atención'. "
                         "0 para desactivar.")
    args = ap.parse_args()

    out = Path(args.out_dir); out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)

    import h5py
    with h5py.File(args.h5, "r") as f:
        feats = np.array(f["features"])
        coords = np.array(f["coords"])
    N = len(coords)
    print(f"[data] {SLIDE}: N={N} parches, features {feats.shape}")

    # Paso de la grilla desde la GEOMETRÍA REAL de las coords, nunca desde la
    # magnificación ([[patch-size-desde-geometria-h5]]).
    diffs = []
    for y in np.unique(coords[:, 1])[:400]:
        xs = np.sort(coords[coords[:, 1] == y][:, 0])
        d = np.diff(xs)
        diffs += d[d > 0].tolist()
    step = int(Counter(diffs).most_common(1)[0][0])
    print(f"[data] paso de grilla (moda) = {step} px")

    ann = pd.read_csv(args.anotaciones)
    idx_of = {(int(a), int(b)): i for i, (a, b) in enumerate(coords)}
    ann["idx"] = [idx_of.get((int(r.x), int(r.y))) for r in ann.itertuples()]
    if ann["idx"].isna().any():
        raise ValueError(f"{int(ann['idx'].isna().sum())} parches anotados no están en el h5")
    ann["idx"] = ann["idx"].astype(int)

    # Un parche puede tener varias clases ('Mitosis|Tumor'): pertenece a los dos grupos.
    grupos = {}
    for r in ann.itertuples():
        for c in str(r.clases).split("|"):
            grupos.setdefault(c.strip(), []).append(r.idx)
    grupos = {k: np.array(sorted(set(v))) for k, v in grupos.items()}
    for k in sorted(grupos, key=lambda z: -len(grupos[z])):
        print(f"[data] grupo {k:22s} n={len(grupos[k])}")

    # Universos de comparación. La lámina 129741 es un Ventana .bif con DOS regiones de
    # escaneo (region[1].y = 49920) y el pipeline extrajo parches de las dos, pero el
    # patólogo anotó solo una. Si esa región recibiera de por sí más atención, el efecto
    # medido sería el de la región y no el de las marcas: por eso se repite todo confinado
    # a la región anotada, incluidas las traslaciones del nulo.
    universos = {"lamina": np.arange(N)}
    if args.y_cut:
        y_ann = coords[ann["idx"].values, 1]
        abajo = bool((y_ann >= args.y_cut).all())
        if abajo or bool((y_ann < args.y_cut).all()):
            sel = (coords[:, 1] >= args.y_cut) if abajo else (coords[:, 1] < args.y_cut)
            universos["region_anotada"] = np.where(sel)[0]
            print(f"[data] región anotada (y {'>=' if abajo else '<'} {args.y_cut}): "
                  f"{int(sel.sum())} parches; la otra región: {int((~sel).sum())}")
        else:
            print(f"[warn] las anotaciones cruzan y={args.y_cut}: no se confina por región")

    filas, por_parche = [], []
    for ck in CKPTS:
        if not Path(ck["path"]).exists():
            print(f"[warn] no existe, se salta: {ck['path']}")
            continue
        n_cls = len(ck["classes"])
        model, _ = build_clam(n_cls, ck["path"])
        A, y_prob, y_hat = get_attention(model, feats)
        i_true = ck["classes"].index("score_3")
        print(f"\n=== {ck['id']} [{ck['rol']}/{ck['split']}] {ck['desc']}")
        print(f"    pred={ck['classes'][y_hat]}  probs={np.round(y_prob, 3).tolist()}"
              f"  (verdadera: score_3)")

        for ci, cname in enumerate(ck["classes"]):
            scores = A[ci]
            ranks = ranks_of(scores)
            pct = 100.0 * (ranks - 1) / (N - 1)
            for uname, uidx in universos.items():
                # Dentro de un universo los rangos se recalculan SOLO sobre sus parches:
                # comparar contra la lámina entera metería de vuelta la otra región.
                u_ranks = ranks if uname == "lamina" else ranks_of(scores[uidx])
                u_n = len(uidx)
                u_pct = pct if uname == "lamina" else 100.0 * (u_ranks - 1) / (u_n - 1)
                for g, idx in grupos.items():
                    es_interes = g in GRUPOS_INTERES
                    # posiciones del grupo DENTRO del universo
                    gi = idx if uname == "lamina" else np.searchsorted(uidx, idx)
                    auc = rank_auc(u_ranks, gi, n_total=u_n)
                    # Los p-valores solo para las cabezas y grupos que importan: la de la
                    # clase verdadera, la predicha, y los dos grupos de interés + Tumor.
                    pp = pt = nacc = nmean = float("nan")
                    if (ci in (i_true, y_hat)) and (es_interes or g == "Tumor"):
                        pp, _ = p_permutacion(u_ranks, gi, args.n_perm, rng)
                        # El nulo por traslación se confina al mismo universo.
                        if uname == "lamina":
                            pt, _, nacc, nmean = p_traslacion(
                                ranks, coords, idx, step, args.n_transl, rng)
                        else:
                            sub_ranks = np.empty(N); sub_ranks[uidx] = u_ranks
                            pt, _, nacc, nmean = p_traslacion(
                                sub_ranks, coords, idx, step, args.n_transl, rng,
                                universo=uidx)
                    filas.append(dict(
                        ckpt=ck["id"], rol=ck["rol"], split_129741=ck["split"],
                        universo=uname, n_universo=u_n,
                        n_clases=n_cls, cabeza=cname, es_cabeza_verdadera=(ci == i_true),
                        es_cabeza_predicha=(ci == y_hat), pred=ck["classes"][y_hat],
                        grupo=g, n_parches=len(idx), grupo_de_interes=es_interes,
                        auc_ranking=auc, percentil_mediano=float(np.median(u_pct[gi])),
                        percentil_medio=float(np.mean(u_pct[gi])),
                        p_permutacion=pp, p_traslacion=pt,
                        n_traslaciones=nacc, auc_nula_media=nmean))
            if ci == i_true:
                for g, idx in grupos.items():
                    for i in idx:
                        por_parche.append(dict(
                            ckpt=ck["id"], grupo=g, idx=int(i),
                            x=int(coords[i, 0]), y=int(coords[i, 1]),
                            atencion=float(scores[i]), percentil=float(pct[i])))

    df = pd.DataFrame(filas)
    df.to_csv(out / "auc_por_checkpoint.csv", index=False)
    pd.DataFrame(por_parche).to_csv(out / "percentiles_por_parche.csv", index=False)

    # Resumen: cabeza de la clase verdadera (score_3), grupos de interés, por rol.
    print("\n" + "=" * 78)
    print("RESUMEN — cabeza de la clase VERDADERA (score_3), AUC de ranking (nulo 0.5)")
    print("=" * 78)
    for uname in universos:
        print(f"\n### universo = {uname}")
        sub = df[df.es_cabeza_verdadera & (df.universo == uname)]
        for rol in ["primario", "control_interno", "corroboracion"]:
            s = sub[sub.rol == rol]
            if s.empty:
                continue
            print(f"  [{rol}]")
            for g in GRUPOS_INTERES + ["Tumor", "Tejido Adiposo"]:
                v = s[s.grupo == g]["auc_ranking"].values
                if len(v):
                    print(f"    {g:22s} AUC {v.mean():.3f} ± {v.std(ddof=0):.3f}   "
                          f"(n_ckpt={len(v)}, rango {v.min():.3f}–{v.max():.3f})")
    print(f"\n[out] {out}/auc_por_checkpoint.csv  ({len(df)} filas)")
    json.dump(dict(slide=SLIDE, N=int(N), step=int(step), seed=args.seed,
                   n_perm=args.n_perm, n_transl=args.n_transl,
                   grupos={k: int(len(v)) for k, v in grupos.items()}),
              open(out / "meta.json", "w"), indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
