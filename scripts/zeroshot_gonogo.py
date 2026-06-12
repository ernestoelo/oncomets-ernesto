#!/usr/bin/env python
"""
Go/No-Go zero-shot CONCH — GENERAL (necrosis, mitotic, ...). CPU, sin GPU, sin entrenar.

Generaliza scripts/zeroshot_necrosis_gonogo.py a un tester reusable por tarea (Sebastián
pidió varias). Mide la condición necesaria de PathPT-CONCH: ¿CONCH groundea zero-shot la
morfología de la tarea? Pre-registración: sprints/B5_sprint5/pathpt/etapa0_gonogo_necrosis.md
(necrosis) y ...etapa0_gonogo_mitotic.md (mitotic).

CLAVE: las features .pt se extrajeron con proj_contrast=False (forward_no_head) → se
reconstruye el espacio contrastivo con feats @ visual.proj_contrast (ver vision_tower.py).

Uso:  python zeroshot_gonogo.py --task necrosis [--promptset v2]
      python zeroshot_gonogo.py --task mitotic
"""
import os, sys, json, time, argparse
import numpy as np
import torch
import torch.nn.functional as F
import pandas as pd
from sklearn.metrics import balanced_accuracy_score, roc_auc_score, confusion_matrix, roc_curve

CONCH_REPO   = "/media/administrador/Storage1/sdonoso/clam_environ/CONCH"
CKPT         = "/home/sdonoso/.cache/huggingface/hub/models--MahmoodLab--conch/snapshots/f9ca9f877171a28ade80228fb195ac5d79003357/pytorch_model.bin"
FEATURES_DIR = "/media/administrador/Storage1/sdonoso/clam_environ/environ/features/pt_files"
CSV_DIR      = "/media/administrador/Storage1/sdonoso/clam_environ/environ/csv"
OUT_DIR      = "/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/results/pathpt_gonogo"

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
sys.path.insert(0, CONCH_REPO)
from conch.open_clip_custom import create_model_from_pretrained, get_tokenizer, tokenize

TEMPLATES = [
    "CLASSNAME.",
    "a photomicrograph showing CLASSNAME.",
    "a histopathology image of CLASSNAME.",
    "an H&E stained image showing CLASSNAME.",
    "breast tissue showing CLASSNAME.",
]
TOPJ = (1, 5, 10, 50, 100)

# ====== TAREAS (prompts EDITABLES — validar clínicamente / CAP) ======
TASKS = {
    "necrosis": {
        "csv": "dataset_carcinoma_ductal_in_situ_necrosis_label.csv",
        "binary": True,
        # clase 0 = ausente ; clase 1 = presente (central+focal); no_identificado excluido
        "keep": ["ausente", "presente_central", "presente_focal"],
        "pos_labels": ["presente_central", "presente_focal"],
        "class_labels": ["ausente", "presente"],
        "prompts": {
            "v1": [
                ["ductal carcinoma in situ without necrosis", "viable tumor cells without necrosis", "benign breast tissue"],
                ["tumor necrosis", "comedonecrosis", "necrotic cellular debris", "central necrosis in ductal carcinoma in situ"],
            ],
            "v2": [
                ["ductal carcinoma in situ without necrosis", "viable tumor cells", "intact ductal epithelium", "benign breast tissue"],
                ["comedonecrosis", "central necrosis with karyorrhectic debris", "tumor necrosis", "necrotic ductal carcinoma in situ", "eosinophilic necrotic debris in duct lumen"],
            ],
        },
    },
    "mitotic": {
        "csv": "dataset_grado_histologico_tasa_mitotica_label.csv",
        "binary": False,
        # 3 clases ordinales (Nottingham); no_identificado excluido
        "keep": ["score_1", "score_2", "score_3"],
        "class_order": ["score_1", "score_2", "score_3"],
        "class_labels": ["score_1", "score_2", "score_3"],
        "prompts": {
            "v1": [
                ["breast carcinoma with a low mitotic count", "few mitotic figures", "rare mitoses"],
                ["breast carcinoma with an intermediate mitotic count", "occasional mitotic figures"],
                ["breast carcinoma with a high mitotic count", "frequent mitotic figures", "numerous mitoses"],
            ],
        },
    },
    # --- microcalcificaciones (3 binarias; CAP Invasive.Bx Nota D). clase 0=no, 1=si.
    #     Sign-off clínico de los prompts = Sebastián. no_identificado ya excluido del CSV (328 ident.).
    "microcalc_carcinoma": {
        "csv": "dataset_microcalcificaciones_en_carcinoma_invasivo_label.csv",
        "binary": True, "keep": ["no", "si"], "pos_labels": ["si"], "class_labels": ["no", "si"],
        "prompts": {
            "v1": [
                ["invasive breast carcinoma without calcifications", "tumor without calcium deposits", "no microcalcifications"],
                ["microcalcifications within invasive carcinoma", "calcifications in invasive breast carcinoma", "calcium deposits in invasive tumor"],
            ],
            # v2: morfología H&E de la calcificación (basófila, amorfa, granular)
            "v2": [
                ["invasive breast carcinoma without calcifications", "invasive carcinoma without calcium deposits", "tumor without calcific debris"],
                ["basophilic microcalcifications within invasive carcinoma", "amorphous calcium deposits within invasive tumor", "granular calcific debris in invasive carcinoma", "calcifications within invasive breast carcinoma"],
            ],
            # v3: apariencia H&E (depósitos púrpura/laminados, psammomatous) + negativo explícito
            "v3": [
                ["invasive breast carcinoma with no calcifications", "viable invasive tumor without calcium", "invasive carcinoma without basophilic deposits"],
                ["dark basophilic calcifications within invasive carcinoma", "purple amorphous microcalcifications in invasive tumor", "laminated psammomatous calcification in carcinoma", "calcific debris within invasive breast carcinoma"],
            ],
        },
    },
    "microcalc_cdis": {
        "csv": "dataset_microcalcificaciones_en_cdis_label.csv",
        "binary": True, "keep": ["no", "si"], "pos_labels": ["si"], "class_labels": ["no", "si"],
        "prompts": {"v1": [
            ["ductal carcinoma in situ without calcifications", "DCIS without calcium deposits", "no microcalcifications"],
            ["microcalcifications within ductal carcinoma in situ", "calcifications in DCIS", "calcium deposits in ductal carcinoma in situ"],
        ]},
    },
    "microcalc_tejido": {
        "csv": "dataset_microcalcificaciones_en_tejido_no_neoplasico_label.csv",
        "binary": True, "keep": ["no", "si"], "pos_labels": ["si"], "class_labels": ["no", "si"],
        "prompts": {"v1": [
            ["non-neoplastic breast tissue without calcifications", "benign breast tissue without calcium deposits", "no microcalcifications"],
            ["microcalcifications in benign breast tissue", "calcifications in non-neoplastic breast tissue", "calcium deposits in benign breast tissue"],
        ]},
    },
}
# =====================================================================


@torch.no_grad()
def build_text_weights(model, tokenizer, classnames):
    weights = []
    for class_cnames in classnames:
        embs = []
        for cname in class_cnames:
            ids = tokenize(tokenizer, [t.replace("CLASSNAME", cname) for t in TEMPLATES])
            embs.append(F.normalize(model.encode_text(ids), dim=-1))
        ce = torch.stack(embs, 0).mean(dim=(0, 1)); ce = ce / ce.norm()
        weights.append(ce)
    return torch.stack(weights, 1)          # [512, C]


@torch.no_grad()
def slide_tile_logits(feats, proj, text_w):
    fc = F.normalize(feats @ proj, dim=-1)
    return fc @ text_w                       # [N, C]


def topj_pool(logits, topj):
    maxj = min(max(topj), logits.size(0))
    vals, _ = logits.topk(maxj, 0, True, True)
    return {j: vals[:min(j, maxj)].mean(0) for j in topj}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", required=True, choices=list(TASKS))
    ap.add_argument("--promptset", default="v1")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    cfg = TASKS[args.task]
    classnames = cfg["prompts"][args.promptset]
    os.makedirs(OUT_DIR, exist_ok=True)
    t0 = time.time()

    print(f"[1/4] CONCH (CPU) | tarea={args.task} promptset={args.promptset}", flush=True)
    model = create_model_from_pretrained("conch_ViT-B-16", checkpoint_path=CKPT, device="cpu", return_transform=False)
    model.eval()
    tokenizer = get_tokenizer()
    proj = model.visual.proj_contrast.detach().float()
    print("[2/4] embeddings de texto...", flush=True)
    text_w = build_text_weights(model, tokenizer, classnames).float()

    print("[3/4] CSV + subset...", flush=True)
    df = pd.read_csv(os.path.join(CSV_DIR, cfg["csv"]))
    df = df[df.label.isin(cfg["keep"])].copy()
    if cfg["binary"]:
        df["y"] = df.label.isin(cfg["pos_labels"]).astype(int)
    else:
        idx = {c: i for i, c in enumerate(cfg["class_order"])}
        df["y"] = df.label.map(idx).astype(int)
    if args.limit:
        df = df.groupby("y", group_keys=False).head(max(1, args.limit // len(cfg["class_labels"])))
    C = len(cfg["class_labels"])

    ys, preds, scores, missing = [], {j: [] for j in TOPJ}, {j: [] for j in TOPJ}, 0
    print(f"[4/4] zero-shot sobre {len(df)} slides ({C} clases)...", flush=True)
    for i, (_, r) in enumerate(df.iterrows()):
        fp = os.path.join(FEATURES_DIR, f"{r.slide_id}.pt")
        if not os.path.exists(fp):
            missing += 1; continue
        feats = torch.load(fp, map_location="cpu").float()
        with torch.no_grad():
            pooled = topj_pool(slide_tile_logits(feats, proj, text_w), TOPJ)
        ys.append(int(r.y))
        for j in TOPJ:
            m = pooled[j]
            preds[j].append(int(m.argmax().item()))
            scores[j].append(torch.softmax(m, 0).tolist())     # prob por clase
        if (i + 1) % 50 == 0:
            print(f"      {i+1}/{len(df)} ({time.time()-t0:.0f}s)", flush=True)

    ys = np.array(ys)
    out = {"tarea": args.task, "promptset": args.promptset, "n_clases": C,
           "prompts": {"classnames": classnames, "templates": TEMPLATES, "labels": cfg["class_labels"]},
           "n_evaluadas": int(len(ys)), "n_missing_pt": int(missing),
           "n_por_clase": {cfg["class_labels"][k]: int((ys == k).sum()) for k in range(C)},
           "trivial_balanced_acc": round(1.0 / C, 4), "por_topj": {}}
    for j in TOPJ:
        p = np.array(preds[j]); s = np.array(scores[j])          # s: [n, C]
        rec = {"balanced_acc_argmax": round(float(balanced_accuracy_score(ys, p)), 4),
               "confusion_argmax": confusion_matrix(ys, p, labels=list(range(C))).tolist()}
        try:
            if C == 2:
                rec["auc"] = round(float(roc_auc_score(ys, s[:, 1])), 4)
                fpr, tpr, _ = roc_curve(ys, s[:, 1])
                rec["balanced_acc_bestthr"] = round(float(np.max(0.5 * (tpr + (1 - fpr)))), 4)
            else:
                rec["auc_macro_ovr"] = round(float(roc_auc_score(ys, s, multi_class="ovr", average="macro")), 4)
        except Exception as e:
            rec["auc_error"] = str(e)
        out["por_topj"][str(j)] = rec

    tag = f"{args.task}_{args.promptset}"
    with open(os.path.join(OUT_DIR, f"{tag}_zeroshot_metrics.json"), "w") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print(f"\n===== {args.task} ({args.promptset}) zero-shot CONCH =====", flush=True)
    print(f"n={out['n_evaluadas']} | clases {out['n_por_clase']} | trivial={out['trivial_balanced_acc']}", flush=True)
    for j in TOPJ:
        d = out["por_topj"][str(j)]
        auc = d.get("auc", d.get("auc_macro_ovr", float('nan')))
        extra = f"bal_acc@bestthr={d['balanced_acc_bestthr']:.3f} " if "balanced_acc_bestthr" in d else ""
        print(f"  top-{j:<3d} AUC={auc:.3f}  {extra}bal_acc@argmax={d['balanced_acc_argmax']:.3f}", flush=True)
    print(f"[done {time.time()-t0:.0f}s] -> {OUT_DIR}/{tag}_zeroshot_metrics.json", flush=True)


if __name__ == "__main__":
    main()
