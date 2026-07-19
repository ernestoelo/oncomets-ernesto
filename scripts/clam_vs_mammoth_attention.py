"""clam_vs_mammoth_attention.py — comparacion de ATENCION CLAM vs Mammoth (B7, Sprint 7).

Entregable central del Sprint 7: donde mira CLAM vs donde mira Mammoth sobre la MISMA
WSI, con checkpoints entrenados paired (job 4589, mismo split por fold).

Por que es apples-to-apples: `CLAM_MB_Mammoth` es SUBCLASE de `CLAM_MB` y HEREDA su
`forward` (models_mammoth/clam_mammoth.py:125). El unico delta es el patch-embed
(1a capa lineal -> MoE Mammoth). Asi que la atencion de ambos brazos se extrae con el
MISMO codigo: `model(h, attention_only=True)` -> A de shape (n_classes, N).

Gotcha CLAM ([[patron-harness-generico-mil]] / CLAUDE.md "Hechos validados"):
`attention_only` devuelve A **PRE-softmax**. Hay que aplicar softmax sobre N (dim=1)
antes de visualizar. Un test que asuma A.sum(dim=1)==1 sobre el crudo falla.

Produce por slide:
  - attention_clam.png / attention_mammoth.png (rama de la clase predicha)
  - attention_side_by_side.png (comparacion directa + delta)
  - attention_stats.json: correlacion Spearman, solapamiento top-k (Jaccard), entropia

Etapa 0: CPU, post-hoc, sin GPU, sin sbatch. NO toca modelo ni training (regla 9 no aplica).
Uso:
  CUDA_VISIBLE_DEVICES="" /home/sdonoso/miniconda3/envs/clam_latest/bin/python \
      scripts/clam_vs_mammoth_attention.py --selection sprints/B7_sprint7/interp_slides.json \
      --out-root results/b7_mammoth_interp/interpretabilidad
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = Path("/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto")
CLAM_ENVIRON = "/media/administrador/Storage1/sdonoso/clam_environ"
for p in (str(REPO), CLAM_ENVIRON):
    if p not in sys.path:
        sys.path.insert(0, p)

from scripts.mammoth_interpretability import (  # noqa: E402
    load_feats_and_coords, get_wsi_thumbnail, patch_size_at_level0,
    build_overlay_rgba, blend, percentile_scores,
)

EMBED_DIM = 512
DROP_OUT = 0.25
B_SAMPLE = 8  # k_sample del job 4589


def infer_patch_size_level0(coords):
    """Tamano de parche a nivel 0 leido de la GEOMETRIA REAL de las coords del h5.

    Por que no usar `patch_size_at_level0(mag)` (mammoth_interpretability.py:254):
    esa funcion infiere el tamano de la magnificacion y fuerza el fallback 40x cuando
    `mag <= 20`, devolviendo 512px. Verificado 18-jul contra las 7 slides del sprint:
    el spacing REAL es 448px en todas (= parche de magnificacion de Sebastian,
    448@x40 -> 224). Ademas `TCGA-AO-A12D` es genuinamente 20x (mpp 0.4992,
    objective-power 20, AppMag 20 concordantes) y la funcion la habria tratado como
    40x. Las coords no mienten: la moda del paso entre parches contiguos de una fila
    ES el tamano del parche. ([[cohortes-magnificacion-fisica]]: parametrizar en la
    geometria fisica, nunca en `level` ni en el tag de magnificacion.)
    """
    from collections import Counter
    c = np.asarray(coords, dtype=np.int64)
    diffs = []
    for y in np.unique(c[:, 1])[:400]:
        xs = np.sort(c[c[:, 1] == y][:, 0])
        d = np.diff(xs)
        diffs += d[d > 0].tolist()
    if not diffs:
        return None
    return float(Counter(diffs).most_common(1)[0][0])


def build_arm(model_type, n_classes, ckpt_path, device="cpu"):
    """Reconstruye el modelo tal cual lo construyo train_dsmil.build_model y carga pesos."""
    from topk.svm import SmoothTop1SVM
    inst_loss = SmoothTop1SVM(n_classes=2)
    common = dict(gate=True, size_arg="small", dropout=DROP_OUT, k_sample=B_SAMPLE,
                  n_classes=n_classes, subtyping=False, instance_loss_fn=inst_loss,
                  embed_dim=EMBED_DIM)
    if model_type == "clam":
        from models.model_clam import CLAM_MB
        model = CLAM_MB(**common)
    else:
        from models_mammoth import CLAM_MB_Mammoth
        model = CLAM_MB_Mammoth(
            **common,
            mammoth_num_experts=30, mammoth_num_slots=10, mammoth_num_heads=16,
            mammoth_slot_dim=256, mammoth_slot_dropout=0.0, mammoth_keep_slots=False)
    ckpt = torch.load(ckpt_path, map_location=device)
    sd = ckpt.get("model", ckpt) if isinstance(ckpt, dict) else ckpt
    missing, unexpected = model.load_state_dict(sd, strict=False)
    if missing:
        raise ValueError(f"{model_type}: faltan pesos en el checkpoint: {missing[:5]}")
    model.to(device).eval()
    return model, unexpected


def get_attention(model, feats, device="cpu"):
    """A pre-softmax (n_classes, N) -> softmax sobre N. Devuelve tambien logits del slide."""
    x = torch.from_numpy(feats).float().to(device)
    with torch.no_grad():
        A_raw = model(x, attention_only=True)          # (n_classes, N) PRE-softmax
        A = torch.softmax(A_raw, dim=1)                # normalizar sobre los N parches
        logits, y_prob, y_hat, _, _ = model(x)         # forward completo -> prediccion
    return (A.cpu().numpy().astype(np.float64),
            A_raw.cpu().numpy().astype(np.float64),
            y_prob.cpu().numpy().ravel(), int(y_hat.item()))


def spearman(a, b):
    ra = np.argsort(np.argsort(a)).astype(np.float64)
    rb = np.argsort(np.argsort(b)).astype(np.float64)
    ra -= ra.mean(); rb -= rb.mean()
    d = np.sqrt((ra ** 2).sum() * (rb ** 2).sum())
    return float((ra * rb).sum() / d) if d else float("nan")


def topk_jaccard(a, b, frac=0.05):
    k = max(1, int(round(len(a) * frac)))
    sa = set(np.argsort(a)[::-1][:k].tolist())
    sb = set(np.argsort(b)[::-1][:k].tolist())
    return float(len(sa & sb) / len(sa | sb))


def norm_entropy(a):
    """Entropia de la atencion normalizada a [0,1] (1 = uniforme, 0 = un solo parche)."""
    p = np.clip(a / a.sum(), 1e-12, 1.0)
    return float(-(p * np.log(p)).sum() / np.log(len(p)))


def save_pair_figure(thumb, coords, a_clam, a_mam, scale, ps0, out_path, title):
    """CLAM | Mammoth | delta (percentil), lado a lado sobre el mismo thumbnail."""
    th, tw = thumb.shape[:2]
    pc, pm = percentile_scores(a_clam), percentile_scores(a_mam)
    panels = [
        (pc, "CLAM (atencion)"),
        (pm, "Mammoth (atencion)"),
        (np.clip((pm - pc) * 0.5 + 0.5, 0, 1), "delta (Mammoth - CLAM)"),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(3 * 5.2, 5.2 * th / tw + 0.6))
    for ax, (vals, name) in zip(np.atleast_1d(axes).ravel(), panels):
        ov = build_overlay_rgba(coords, vals, scale, tw, th, ps0)
        ax.imshow(blend(thumb, ov))
        ax.set_title(name, fontsize=11)
        ax.set_axis_off()
    fig.suptitle(title, fontsize=12)
    plt.tight_layout()
    plt.savefig(out_path, bbox_inches="tight", dpi=115)
    plt.close()


def save_single(thumb, coords, vals, scale, ps0, out_path, label):
    th, tw = thumb.shape[:2]
    ov = build_overlay_rgba(coords, percentile_scores(vals), scale, tw, th, ps0)
    fig, ax = plt.subplots(figsize=(tw / 150, th / 150))
    ax.imshow(blend(thumb, ov)); ax.set_axis_off()
    ax.text(tw * 0.02, th * 0.98, label, ha="left", va="top", fontsize=12,
            color="white", weight="bold",
            bbox=dict(facecolor="black", alpha=0.4, pad=2, edgecolor="none"))
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    plt.savefig(out_path, bbox_inches="tight", pad_inches=0, dpi=120)
    plt.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selection", default=str(REPO / "sprints/B7_sprint7/interp_slides.json"))
    ap.add_argument("--out-root", default=str(REPO / "results/b7_mammoth_interp/interpretabilidad"))
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--only-task", default=None)
    args = ap.parse_args()

    sel = json.loads(Path(args.selection).read_text())
    out_root = Path(args.out_root); out_root.mkdir(parents=True, exist_ok=True)
    summary = []

    for task, cfg in sel.items():
        if args.only_task and task != args.only_task:
            continue
        n_classes = len(cfg["classes"])
        print(f"\n{'=' * 74}\nTAREA {task}  (n_classes={n_classes}, fold {cfg['fold']})")
        print("  cargando brazos...")
        clam, _ = build_arm("clam", n_classes, cfg["ckpt_clam"], args.device)
        mam, _ = build_arm("clam_mammoth", n_classes, cfg["ckpt_mammoth"], args.device)

        for sl in cfg["slides"]:
            sid = sl["slide_id"]
            short = sid.split(".")[0]
            print(f"\n  --- {short}  (clase real: {sl['label']}, {sl['cohort']})")
            feats, coords = load_feats_and_coords(sl["h5"])
            A_c, Araw_c, prob_c, yhat_c = get_attention(clam, feats, args.device)
            A_m, Araw_m, prob_m, yhat_m = get_attention(mam, feats, args.device)
            print(f"      N={feats.shape[0]} parches | CLAM pred={yhat_c} "
                  f"p={prob_c[yhat_c]:.3f} | Mammoth pred={yhat_m} p={prob_m[yhat_m]:.3f}")

            # rama de atencion de la clase VERDADERA (comparable entre brazos)
            ci = sl["y_true"]
            a_c, a_m = A_c[ci], A_m[ci]

            thumb, scale, mag, w0, h0 = get_wsi_thumbnail(sl["wsi"])
            if np.nanmax(coords) <= 1.1:
                coords = coords * np.array([w0, h0])
            ps0_geom = infer_patch_size_level0(coords)
            ps0_mag = patch_size_at_level0(mag)
            ps0 = ps0_geom if ps0_geom else ps0_mag
            if ps0_geom and abs(ps0_geom - ps0_mag) > 1:
                print(f"      patch_size_level0: {ps0_geom:.0f}px (geometria del h5) "
                      f"— la inferencia por magnificacion daba {ps0_mag:.0f}px, se descarta")
            # Campo fisico real del parche: depende del mpp NATIVO de la slide, que
            # dentro de TCGA no es homogeneo (hay slides 20x y 40x).
            mpp = None
            try:
                import openslide
                _s = openslide.OpenSlide(sl["wsi"])
                mpp = float(_s.properties.get("openslide.mpp-x") or 0) or None
                _s.close()
            except Exception:
                pass
            um_parche = ps0 * mpp if (mpp and ps0) else None

            od = out_root / task / short; od.mkdir(parents=True, exist_ok=True)
            save_single(thumb, coords, a_c, scale, ps0, od / "attention_clam.png",
                        f"CLAM · {short} · {sl['label']}")
            save_single(thumb, coords, a_m, scale, ps0, od / "attention_mammoth.png",
                        f"Mammoth · {short} · {sl['label']}")
            save_pair_figure(thumb, coords, a_c, a_m, scale, ps0,
                             od / "attention_side_by_side.png",
                             f"{short} — clase {sl['label']} (rama {ci})")

            st = dict(
                slide_id=sid, task=task, fold=cfg["fold"], cohort=sl["cohort"],
                clase_real=sl["label"], n_patches=int(feats.shape[0]),
                level0_mag=mag, mpp_x=mpp,
                patch_size_level0=float(ps0),
                patch_size_level0_por_magnif=float(ps0_mag),
                campo_fisico_parche_um=um_parche,
                clam=dict(pred=yhat_c, prob=float(prob_c[yhat_c]),
                          entropia_atencion=norm_entropy(a_c)),
                mammoth=dict(pred=yhat_m, prob=float(prob_m[yhat_m]),
                             entropia_atencion=norm_entropy(a_m)),
                spearman_atencion=spearman(a_c, a_m),
                jaccard_top5pct=topk_jaccard(a_c, a_m, 0.05),
                jaccard_top1pct=topk_jaccard(a_c, a_m, 0.01),
            )
            (od / "attention_stats.json").write_text(json.dumps(st, indent=2))
            summary.append(st)
            print(f"      Spearman(atencion)={st['spearman_atencion']:.3f}  "
                  f"Jaccard top-5%={st['jaccard_top5pct']:.3f}  "
                  f"entropia CLAM={st['clam']['entropia_atencion']:.3f} / "
                  f"Mammoth={st['mammoth']['entropia_atencion']:.3f}")

    (out_root / "attention_summary.json").write_text(json.dumps(summary, indent=2))
    print(f"\n\nListo. {len(summary)} slides. Salida: {out_root}")


if __name__ == "__main__":
    main()
