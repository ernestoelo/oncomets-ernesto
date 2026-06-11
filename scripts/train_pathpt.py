#!/usr/bin/env python3
"""train_pathpt.py — PathPT-CONCH (Etapa 1 B5), paired vs CLAM sobre una tarea.

Driver PROPIO de PathPT (NO un --model_type de CLAM): clasifica por parche con el
encoder de texto de CONCH, usa coords para el módulo espacial θ_v, genera pseudo-labels
tile-level zero-shot y entrena θ_v + θ_t con el curriculum de 3 pérdidas.

Pre-registración (regla 9): sprints/B5_sprint5/pathpt/etapa1_prereg_necrosis.md (reviewer GO).
Modelo: models_pathpt/ (port fiel de MAGIC-AI4Med/PathPT, pin 0ab7f1b).

Produce el MISMO schema de salida que scripts/train_dsmil.py (summary.csv,
test_metrics.json, split_<fold>_results.pkl, test_predictions.csv) → el Δ pareado por
fold se construye 1:1 contra el brazo CLAM (train_dsmil.py --model_type clam, mismos splits).

CLAVE espacio contrastivo: las .pt cacheadas son forward_no_head → se aplica
`v = normalize(feat @ proj_contrast)` (proj de CONCH.visual) ANTES del modelo.

CLAVE binario (necrosis presencia/ausencia, NO subtyping):
- slide ausente (y=0): todos los parches pseudo-label 0 (supervisión negativa fuerte).
- slide presente (y=1): generate_patch_label con clase-tumor=1.
- con logits_thd=0 (ref) no hay candidatos en binario → curriculum inerte; PathPT-binario
  = CE balanceada tile-level vs argmax del teacher + θ_v + θ_t (addendum §7 de la prereg).
  El código es general: mitotic (3-clase) sí generará candidatos.

Eval (H-2 reviewer): score continuo de slide = top-j pooled P(clase positiva) → AUC directo;
el UMBRAL de balanced_acc se elige sobre VAL de cada fold y se congela al TEST (sin DoF post-hoc).

NUNCA invocar con `python` (workaround B). Vía sbatch o el binario absoluto del env.
Para CPU (test): PYTHONPATH debe incluir clam_testing2/.pylibs (nystrom_attention).
"""
from __future__ import annotations

import argparse
import json
import os
import pickle
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
from sklearn.metrics import balanced_accuracy_score, confusion_matrix, roc_auc_score

_CLAM = "/media/administrador/Storage1/sdonoso/clam_environ"
_REPO = "/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto"
_PYLIBS = "/media/administrador/Storage1/sdonoso/clam_testing2/.pylibs"
for _p in (_PYLIBS, _CLAM, _REPO):
    if _p not in sys.path:
        sys.path.insert(0, _p)

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import h5py  # noqa: E402
from conch.open_clip_custom import (  # noqa: E402
    create_model_from_pretrained, get_tokenizer, tokenize,
)
from models_pathpt import PathPTCONCH, PatchSSLoss  # noqa: E402

CKPT = ("/home/sdonoso/.cache/huggingface/hub/models--MahmoodLab--conch/"
        "snapshots/f9ca9f877171a28ade80228fb195ac5d79003357/pytorch_model.bin")

# ===== PROMPTS por tarea (clase 0 = normal/negativo; clases ≥1 = positivas) =====
# necrosis: reusa el pool del go/no-go (zeroshot_necrosis_gonogo.py). Validación
# clínica = Sebastián/CAP; acá es ingeniería.
TEMPLATES = [
    "CLASSNAME.",
    "a photomicrograph showing CLASSNAME.",
    "a histopathology image of CLASSNAME.",
    "an H&E stained image showing CLASSNAME.",
    "breast tissue showing CLASSNAME.",
]
TASK_PROMPTS = {
    "necrosis": {
        # índice 0 = "no"/ausente/normal ; índice 1 = "si"/presente.
        # Prompts v3 = anclados en CAP Invasive.Bx Nota C (comedo/central/focal +
        # distinción negativa vs material secretorio "without nuclear debris").
        # go/no-go: v3 AUC 0.688 > v1 0.677 > v2 0.649. Sign-off clínico = Sebastián.
        # Detalle/provenance: sprints/B5_sprint5/pathpt/prompts_cap.md
        "classnames": [
            ["ductal carcinoma in situ without necrosis",
             "viable tumor cells",
             "secretory material without nuclear debris",
             "benign breast tissue"],
            ["comedonecrosis",
             "central necrosis in a ductal space",
             "expansive necrosis with ghost cells and karyorrhectic debris",
             "tumor necrosis",
             "single cell necrosis"],
        ],
        # init del contexto aprendible θ_t (CoOp)
        "ctx_init": "a histopathology image of ",
    },
    "mitotic": {
        # 3 clases ORDINALES (Nottingham). Clase 0 = score_1 = nivel basal ordinal
        # (prereg mitotic §3.1: a nivel tile, slides score_1 ≈ baja densidad). Prompts
        # del go/no-go validado (macro-OVR AUC 0.648), anclados en CAP Invasive.Bx Nota B /
        # Nottingham (prompts_cap.md §2). Sign-off clínico = Sebastián.
        # índice 0=score_1 (bajo) · 1=score_2 (intermedio) · 2=score_3 (alto).
        "classnames": [
            ["breast carcinoma with a low mitotic count", "few mitotic figures", "rare mitoses"],
            ["breast carcinoma with an intermediate mitotic count", "occasional mitotic figures"],
            ["breast carcinoma with a high mitotic count", "frequent mitotic figures", "numerous mitoses"],
        ],
        "ctx_init": "a histopathology image of ",
    },
}
TOPJ_TEACHER = 5  # top-j pooling para el score de slide (consistente con el go/no-go)


# ----------------------------------------------------------------------------- data
def expand_prompts(classnames):
    """classnames: lista por-clase de nombres → lista por-clase de frases (templates×nombres)."""
    pool = []
    for names in classnames:
        phrases = []
        for name in names:
            phrases += [t.replace("CLASSNAME", name) for t in TEMPLATES]
        pool.append(phrases)
    return pool


def load_split_slides(split_dir, fold, label_map):
    """splits_<fold>.csv → dict {train,val,test} de (slide_id, y_int)."""
    df = pd.read_csv(os.path.join(split_dir, f"splits_{fold}.csv"))
    out = {}
    for col in ("train", "val", "test"):
        ids = df[col].dropna().astype(str).tolist()
        out[col] = [(sid, label_map[sid]) for sid in ids]
    return out


def load_contrastive(slide_id, pt_dir, h5_dir, proj):
    """.pt (forward_no_head) + coords del h5 → features contrastivas [N,512] ORDENADAS por
    coords (raster y,x) para que el conv1d de θ_v capture vecindarios locales."""
    feats = torch.load(os.path.join(pt_dir, f"{slide_id}.pt"), map_location="cpu").float()
    with h5py.File(os.path.join(h5_dir, f"{slide_id}.h5"), "r") as h:
        coords = np.asarray(h["coords"][:])
    assert coords.shape[0] == feats.shape[0], (
        f"{slide_id}: coords {coords.shape[0]} != feats {feats.shape[0]}")
    order = np.lexsort((coords[:, 0], coords[:, 1]))  # ordena por y, luego x (raster)
    feats = feats[order]
    # proj puede estar en GPU; hacer el matmul en su device y CACHEAR en CPU (memoria).
    contrastive = F.normalize(feats.to(proj.device) @ proj, dim=-1)   # forward_project + L2
    return contrastive.cpu()


def precompute_features(slides, pt_dir, h5_dir, proj):
    cache = {}
    for sid, _ in slides:
        cache[sid] = load_contrastive(sid, pt_dir, h5_dir, proj)
    return cache


# ------------------------------------------------------------------- teacher prompts
@torch.no_grad()
def encode_prompt_pool(conch, pool, device):
    """pool: lista por-clase de frases → lista por-clase de text features [n_var,512] (norm)."""
    tok = get_tokenizer()
    feats = []
    for phrases in pool:
        ids = tokenize(tok, phrases).to(device)
        e = conch.encode_text(ids)
        feats.append(F.normalize(e, dim=-1))
    return feats


def topj_pool_score(logits, topj):
    """logits [N,C] → P(positiva) por top-j pooling (réplica go/no-go). Devuelve score escalar
    en [0,1] para binario (P de la clase 1). Para multiclase devuelve el vector softmax pooled."""
    maxj = min(topj, logits.size(0))
    vals, _ = logits.topk(maxj, 0, True, True)        # [maxj, C]
    pooled = vals.mean(0)                              # [C]
    return torch.softmax(pooled, 0)


@torch.no_grad()
def select_teacher(conch, train_cache, train_labels, pool, device, n_classes,
                   prompt_num=200, select_num=100, seed=1):
    """wsi_prompt_selector (port): rankea `prompt_num` combos aleatorios de prompts por AUC
    (binario) / macro-OVR (multi) del score de slide en train, y promedia el top-`select_num`
    → teacher embedding [n_classes,512] (norm). Adaptado a presencia/ausencia: el ranking usa
    AUC del score continuo (no argmax sobre subtipos, que en binario es degenerado)."""
    cls_feats = encode_prompt_pool(conch, pool, device)   # lista n_classes de [n_var,512]
    rng = np.random.RandomState(seed)
    combos = []   # cada uno [n_classes,512]
    for _ in range(prompt_num):
        emb = torch.stack([cf[rng.randint(len(cf))] for cf in cls_feats])  # [n_classes,512]
        combos.append(emb)

    ys = np.array([y for _, y in train_labels])
    # score por (combo, slide): P(clase positiva) top-j pooled
    scores = np.zeros((prompt_num, len(train_labels)), dtype=np.float32)
    for si, (sid, _) in enumerate(train_labels):
        feats = train_cache[sid].to(device)               # [N,512]
        for ci, emb in enumerate(combos):
            logits = feats @ emb.t()                       # [N,n_classes]
            p = topj_pool_score(logits, TOPJ_TEACHER)      # [n_classes]
            scores[ci, si] = float(p[1].item()) if n_classes == 2 else float(p.argmax().item())

    # rankear combos
    metric = np.zeros(prompt_num)
    for ci in range(prompt_num):
        try:
            if n_classes == 2:
                metric[ci] = roc_auc_score(ys, scores[ci])
            else:
                metric[ci] = balanced_accuracy_score(ys, scores[ci].astype(int))
        except ValueError:
            metric[ci] = 0.0
    top = np.argsort(metric)[::-1][:min(select_num, prompt_num)]
    teacher = torch.stack([combos[i] for i in top]).mean(0)   # [n_classes,512]
    teacher = F.normalize(teacher, dim=-1)
    return teacher, float(metric[top].mean())


# ------------------------------------------------------------------- pseudo-labels
def generate_patch_label(probs, logits_thd, tumor_class):
    """Port de wsi_selecter_CONCH.generate_patch_label, clase-tumor explícita.
    probs [N,C] (softmax). Devuelve [N]: 0=normal, tumor_class=positivo confiable,
    -tumor_class=candidato. En binario+thd0 no hay candidatos."""
    N = probs.shape[0]
    argmax = probs.argmax(1)
    labels = torch.full((N,), -tumor_class, dtype=torch.long)
    normal = (probs[:, 0] > logits_thd) & (argmax == 0)
    tumor = (probs[:, tumor_class] > logits_thd) & (argmax == tumor_class)
    labels[normal] = 0
    labels[tumor] = tumor_class
    return labels


def make_patch_labels(cache, labels, teacher, device, logits_thd):
    """pseudo-labels por slide. Binario presencia/ausencia: y=0 ⇒ todos 0; y>=1 ⇒ generate_patch_label
    con clase-tumor = y (en binario y=1)."""
    out = {}
    for sid, y in labels:
        feats = cache[sid].to(device)
        if y == 0:
            out[sid] = torch.zeros(feats.shape[0], dtype=torch.long)   # ausente → todo normal
        else:
            with torch.no_grad():
                probs = torch.softmax(feats @ teacher.t(), dim=-1).cpu()
            out[sid] = generate_patch_label(probs, logits_thd, tumor_class=y)
    return out


# ------------------------------------------------------------------- eval
@torch.no_grad()
def slide_scores(model, cache, labels, device, n_classes):
    """score continuo de slide = top-j pooled P(positiva) sobre los patch_logits del modelo."""
    model.eval()
    ys, ss = [], []
    for sid, y in labels:
        feats = cache[sid].to(device)
        _, patch_logits = model(feats)                 # [N,n_classes] (ya softmax)
        p = topj_pool_score(torch.log(patch_logits + 1e-8), TOPJ_TEACHER)  # re-pool en log-space
        ys.append(int(y))
        ss.append(float(p[1].item()) if n_classes == 2 else p.cpu().numpy())
    return np.array(ys), np.array(ss)


def best_threshold(ys, scores):
    """umbral que maximiza balanced_acc sobre VAL (binario)."""
    cands = np.unique(scores)
    best_t, best_b = 0.5, -1.0
    for t in cands:
        b = balanced_accuracy_score(ys, (scores > t).astype(int))
        if b > best_b:
            best_b, best_t = b, float(t)
    return best_t


# ------------------------------------------------------------------- main
def parse_args():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--task", required=True, help="rótulo + clave de TASK_PROMPTS (ej. necrosis)")
    p.add_argument("--prompt_task", default=None, help="clave de TASK_PROMPTS (default: --task)")
    p.add_argument("--exp_code", default=None)
    p.add_argument("--csv_path", required=True, help="CSV de labels binario (slide_id,label)")
    p.add_argument("--data_root_dir", required=True, help="dir con features/{pt_files,h5_files}/")
    p.add_argument("--split_dir", required=True)
    p.add_argument("--results_dir", required=True, help="dir absoluto BAJO clam_testing2/")
    p.add_argument("--fold", type=int, default=0)
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--n_classes", type=int, default=2)
    p.add_argument("--label_dict", default='{"no": 0, "si": 1}')
    p.add_argument("--n_ctx", type=int, default=32)
    p.add_argument("--epochs", type=int, default=20)
    p.add_argument("--lr", type=float, default=1e-4)
    p.add_argument("--logits_thd", type=float, default=0.0)
    p.add_argument("--loss_weight", default="[1.0,0.5,0.1]")
    p.add_argument("--no_balance", action="store_true", help="desactiva balanced CE")
    p.add_argument("--prompt_num", type=int, default=200)
    p.add_argument("--select_num", type=int, default=100)
    p.add_argument("--max_slides", type=int, default=0, help="cap de slides/spLit (smoke; 0=todas)")
    p.add_argument("--ckpt", default=CKPT)
    return p.parse_args()


def main():
    args = parse_args()
    prompt_task = args.prompt_task or args.task
    if prompt_task not in TASK_PROMPTS:
        raise ValueError(f"--prompt_task '{prompt_task}' no está en TASK_PROMPTS {list(TASK_PROMPTS)}")
    if args.exp_code is None:
        args.exp_code = f"pathpt_{args.task}"

    # containment
    results_root = Path(args.results_dir).resolve()
    if not str(results_root).startswith("/media/administrador/Storage1/sdonoso/clam_testing2/"):
        raise ValueError(f"--results_dir debe estar bajo clam_testing2/ (containment): {results_root}")
    results_dir = results_root / f"{args.exp_code}_s{args.seed}"
    results_dir.mkdir(parents=True, exist_ok=True)

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    use_amp = device.type == "cuda"
    print(f"[INFO] device={device} amp={use_amp} exp={args.exp_code} fold={args.fold}", flush=True)

    pt_dir = os.path.join(args.data_root_dir, "features", "pt_files")
    h5_dir = os.path.join(args.data_root_dir, "features", "h5_files")
    for d in (pt_dir, h5_dir):
        if not os.path.isdir(d):
            raise FileNotFoundError(d)

    # labels + splits
    label_dict = json.loads(args.label_dict)
    labels_df = pd.read_csv(args.csv_path)
    label_map = {str(r.slide_id): int(label_dict[str(r.label)]) for r in labels_df.itertuples()}
    splits = load_split_slides(args.split_dir, args.fold, label_map)
    if args.max_slides:
        # subset ESTRATIFICADO (smoke): hasta max_slides//n_classes por clase y split,
        # para garantizar ambas clases (AUC computable). Inactivo en runs reales (max_slides=0).
        per = max(1, args.max_slides // args.n_classes)
        strat = {}
        for k, v in splits.items():
            by_cls = {}
            for sid, y in v:
                by_cls.setdefault(y, []).append((sid, y))
            strat[k] = [s for lst in by_cls.values() for s in lst[:per]]
        splits = strat
    print(f"[INFO] train={len(splits['train'])} val={len(splits['val'])} test={len(splits['test'])}",
          flush=True)

    # CONCH + proj_contrast
    print("[1/5] cargando CONCH...", flush=True)
    conch = create_model_from_pretrained("conch_ViT-B-16", checkpoint_path=args.ckpt,
                                         device=str(device), return_transform=False)
    conch.eval()
    proj = conch.visual.proj_contrast.detach().float().to(device)

    # features contrastivas (precompute)
    print("[2/5] precomputando features contrastivas (.pt @ proj)...", flush=True)
    cache = {}
    for split in splits.values():
        for sid, _ in split:
            if sid not in cache:
                cache[sid] = load_contrastive(sid, pt_dir, h5_dir, proj)

    # teacher prompts (ranking fiel)
    print("[3/5] seleccionando teacher prompts (ranking 200 combos)...", flush=True)
    pool = expand_prompts(TASK_PROMPTS[prompt_task]["classnames"])
    teacher, teacher_metric = select_teacher(
        conch, cache, splits["train"], pool, device, args.n_classes,
        prompt_num=args.prompt_num, select_num=args.select_num, seed=args.seed)
    print(f"      teacher rank metric (train)={teacher_metric:.4f}", flush=True)

    # pseudo-labels por parche (teacher fijo → deterministas)
    patch_labels = make_patch_labels(cache, splits["train"], teacher, device, args.logits_thd)

    # modelo
    print("[4/5] construyendo PathPTCONCH...", flush=True)
    model = PathPTCONCH(
        TASK_PROMPTS[prompt_task]["classnames"], conch, device, n_ctx=args.n_ctx,
        ctx_init=TASK_PROMPTS[prompt_task]["ctx_init"], vfeat_dim=512).to(device)
    optimizer = torch.optim.Adam(model.trainable_parameters(), lr=args.lr)
    warm = max(1, int(args.epochs * 0.1))
    sched = torch.optim.lr_scheduler.LambdaLR(
        optimizer, lr_lambda=lambda e: e / warm if e < warm
        else 0.5 * (1 + np.cos(np.pi * (e - warm) / max(1, args.epochs - warm))))
    scaler = torch.amp.GradScaler(device.type, enabled=use_amp)
    weights = tuple(json.loads(args.loss_weight))
    balance = not args.no_balance

    print("[5/5] entrenando...", flush=True)
    t0 = time.time()
    order = list(range(len(splits["train"])))
    for epoch in range(args.epochs):
        model.train()
        rng = np.random.RandomState(args.seed + epoch)
        rng.shuffle(order)
        run = 0.0
        for idx in order:
            sid, _ = splits["train"][idx]
            feats = cache[sid].to(device)
            plab = patch_labels[sid].to(device)
            with torch.amp.autocast(device.type, enabled=use_amp):
                _, patch_logits = model(feats)
                ld = PatchSSLoss(patch_logits, plab, epoch=epoch, total_epoch=args.epochs,
                                 weights=weights, balance=balance)
                loss = ld["loss"]
            optimizer.zero_grad()
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
            run += float(loss.item())
        sched.step()
        if epoch == 0 or (epoch + 1) % 5 == 0 or epoch == args.epochs - 1:
            print(f"  [epoch {epoch}] loss={run/max(1,len(order)):.4f} "
                  f"lr={sched.get_last_lr()[0]:.2e} ({time.time()-t0:.0f}s)", flush=True)

    # eval: binario → umbral en val (H-2) congelado a test; multiclase → argmax (sin umbral).
    yv, sv = slide_scores(model, cache, splits["val"], device, args.n_classes)
    yt, st = slide_scores(model, cache, splits["test"], device, args.n_classes)
    test_auc = float("nan"); val_auc = float("nan")
    if args.n_classes == 2:
        thr = best_threshold(yv, sv)
        yhat = (st > thr).astype(int)
        val_yhat = (sv > thr).astype(int)
        if len(np.unique(yt)) == 2:
            test_auc = float(roc_auc_score(yt, st))
        if len(np.unique(yv)) == 2:
            val_auc = float(roc_auc_score(yv, sv))
    else:
        thr = None                                       # argmax, sin grado de libertad de umbral
        yhat = st.argmax(1)
        val_yhat = sv.argmax(1)
        labs = list(range(args.n_classes))
        try:    # macro-OVR AUC (threshold-free) sobre el score softmax 3-dim
            test_auc = float(roc_auc_score(yt, st, multi_class="ovr",
                                           average="macro", labels=labs))
        except ValueError:
            test_auc = float("nan")
        try:
            val_auc = float(roc_auc_score(yv, sv, multi_class="ovr",
                                          average="macro", labels=labs))
        except ValueError:
            val_auc = float("nan")

    bal = float(balanced_accuracy_score(yt, yhat))
    acc = float((yt == yhat).mean())
    cm = confusion_matrix(yt, yhat, labels=list(range(args.n_classes)))
    val_acc = float((yv == val_yhat).mean())

    test_metrics = {"test_auc": test_auc, "test_acc": acc, "balanced_acc": bal,
                    "confusion": cm.tolist(), "n_test": int(len(yt)),
                    "val_threshold": thr, "teacher_rank_metric": teacher_metric}
    print(f"[TEST] auc={test_auc:.4f} bal_acc={bal:.4f} acc={acc:.4f} thr={thr} "
          f"confusion={cm.tolist()} n={len(yt)}", flush=True)

    # volcados (schema CLAM, espejo de train_dsmil.py)
    patient_results = {}
    rows = []
    for (sid, y), score, pred in zip(splits["test"], st, yhat):
        if args.n_classes == 2:
            prob = np.array([[1.0 - float(score), float(score)]])
            row = {"slide_id": sid, "y_true": int(y),
                   "y_prob_si": float(score), "y_pred": int(pred)}
        else:
            sc = np.asarray(score, dtype=float)
            prob = sc.reshape(1, -1)                      # [1, C] softmax por clase
            row = {"slide_id": sid, "y_true": int(y), "y_pred": int(pred)}
            row.update({f"y_prob_{c}": float(sc[c]) for c in range(args.n_classes)})
        patient_results[sid] = {"slide_id": np.array(sid), "prob": prob, "label": int(y)}
        rows.append(row)
    pd.DataFrame({"folds": [args.fold], "test_auc": [test_auc], "val_auc": [val_auc],
                  "test_acc": [acc], "val_acc": [val_acc]}).to_csv(
        results_dir / "summary.csv", index=False)
    with open(results_dir / f"split_{args.fold}_results.pkl", "wb") as f:
        pickle.dump(patient_results, f)
    with open(results_dir / "test_metrics.json", "w") as f:
        json.dump(test_metrics, f, indent=2)
    pd.DataFrame(rows).to_csv(results_dir / "test_predictions.csv", index=False)
    torch.save(model.prompt_learner.ctx.detach().cpu(), results_dir / f"s_{args.fold}_ctx.pt")
    print(f"[DONE] artefactos en {results_dir}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
