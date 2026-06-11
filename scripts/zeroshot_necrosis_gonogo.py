#!/usr/bin/env python
"""
Etapa 0 — Go/No-Go de PathPT-CONCH en NECROSIS (zero-shot, CPU).

Pre-registración (regla 9): sprints/B5_sprint5/pathpt/etapa0_gonogo_necrosis.md
Mide la CONDICIÓN NECESARIA de PathPT: ¿CONCH groundea zero-shot la necrosis a nivel
slide? Si no, los pseudo-labels tile-level de PathPT serían ruido (NO-GO barato).

NO entrena · NO GPU · NO sbatch. Lee features CONCH cacheadas (read-only) + el encoder
de texto de CONCH. Containment: lee clam_environ (RO), escribe solo en results/.

CLAVE TÉCNICA: las features .pt de Sebastián se extrajeron con proj_contrast=False
(forward_no_head) → NO están en el espacio contrastivo imagen-texto. Se reconstruye el
embedding contrastivo con un matmul:  contrastivo = normalize(feat_cacheada @ proj_contrast)
(verificado en CONCH/conch/open_clip_custom/vision_tower.py: forward vs forward_no_head).
"""
import os, sys, json, time, argparse
import numpy as np
import torch
import torch.nn.functional as F
import pandas as pd
from sklearn.metrics import balanced_accuracy_score, roc_auc_score, confusion_matrix, roc_curve

# ---- paths (clam_environ READ-ONLY) ----
CONCH_REPO   = "/media/administrador/Storage1/sdonoso/clam_environ/CONCH"
CKPT         = "/home/sdonoso/.cache/huggingface/hub/models--MahmoodLab--conch/snapshots/f9ca9f877171a28ade80228fb195ac5d79003357/pytorch_model.bin"
FEATURES_DIR = "/media/administrador/Storage1/sdonoso/clam_environ/environ/features/pt_files"
CSV          = "/media/administrador/Storage1/sdonoso/clam_environ/environ/csv/dataset_carcinoma_ductal_in_situ_necrosis_label.csv"
OUT_DIR      = "/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/results/pathpt_gonogo"

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
sys.path.insert(0, CONCH_REPO)
from conch.open_clip_custom import create_model_from_pretrained, get_tokenizer, tokenize

# ====== PROMPTS — versionados (anclados en CAP Invasive.Bx Nota C; ver
#        sprints/B5_sprint5/pathpt/prompts_cap.md). CLASE 0 = ausente/normal ; 1 = presente.
PROMPT_SETS = {
    # v1: actual del driver — mejor AUC 0.677 (top-5). Ya es lenguaje CAP (comedo/central).
    "v1": [
        ["ductal carcinoma in situ without necrosis",
         "viable tumor cells without necrosis",
         "benign breast tissue"],
        ["tumor necrosis",
         "comedonecrosis",
         "necrotic cellular debris",
         "central necrosis in ductal carcinoma in situ"],
    ],
    # v3: CAP Nota C — palanca no probada = distinción NEGATIVA vs material secretorio
    # ("does not include nuclear debris") + firma low-mag del comedo (ghost cells / karyorrhectic).
    "v3": [
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
}
CLASSNAMES = PROMPT_SETS["v1"]   # default; main() lo re-selecciona según --version
CLASS_LABELS = ["ausente", "presente"]
TEMPLATES = [
    "CLASSNAME.",
    "a photomicrograph showing CLASSNAME.",
    "a histopathology image of CLASSNAME.",
    "an H&E stained image showing CLASSNAME.",
    "breast tissue showing CLASSNAME.",
]
TOPJ = (1, 5, 10, 50, 100)
# =============================================================


@torch.no_grad()
def build_text_weights(model, tokenizer):
    """Réplica de conch.downstream.zeroshot_path.zero_shot_classifier → [512, n_clases]."""
    weights = []
    for class_cnames in CLASSNAMES:
        embs = []
        for cname in class_cnames:
            texts = [t.replace("CLASSNAME", cname) for t in TEMPLATES]
            ids = tokenize(tokenizer, texts)
            e = model.encode_text(ids)            # ya normalizado por encode_text
            embs.append(F.normalize(e, dim=-1))
        ce = torch.stack(embs, 0).mean(dim=(0, 1))
        ce = ce / ce.norm()
        weights.append(ce)
    return torch.stack(weights, 1)                # [512, n_clases]


@torch.no_grad()
def slide_tile_logits(feats, proj, text_w):
    """feats [N,512] (forward_no_head cacheado) -> contrastivo -> coseno vs texto [N,C]."""
    fc = feats @ proj                              # forward_project (= @ proj_contrast)
    fc = F.normalize(fc, dim=-1)
    return fc @ text_w                             # [N, C]


def topj_pool(logits, topj):
    """Réplica de topj_pooling de CONCH: por clase, media de los top-j parches."""
    maxj = min(max(topj), logits.size(0))
    vals, _ = logits.topk(maxj, 0, True, True)     # [maxj, C] (top-k por columna/clase)
    return {j: vals[:min(j, maxj)].mean(0) for j in topj}   # cada uno [C]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="máx slides (0=todas, para smoke-test)")
    ap.add_argument("--version", default="v1", choices=list(PROMPT_SETS),
                    help="set de prompts (v1=actual 0.677; v3=CAP Nota C, lado negativo refinado)")
    args = ap.parse_args()
    global CLASSNAMES
    CLASSNAMES = PROMPT_SETS[args.version]
    os.makedirs(OUT_DIR, exist_ok=True)
    t0 = time.time()
    print(f"[prompts] versión={args.version}  presente={CLASSNAMES[1]}", flush=True)

    print("[1/4] cargando CONCH (CPU)...", flush=True)
    model = create_model_from_pretrained("conch_ViT-B-16", checkpoint_path=CKPT,
                                          device="cpu", return_transform=False)
    model.eval()
    tokenizer = get_tokenizer()
    proj = model.visual.proj_contrast.detach().float()
    print(f"      proj_contrast: {tuple(proj.shape)}", flush=True)

    print("[2/4] embeddings de texto (prompts)...", flush=True)
    text_w = build_text_weights(model, tokenizer).float()   # [512, C]

    print("[3/4] leyendo CSV + filtrando subset binario...", flush=True)
    df = pd.read_csv(CSV)
    df = df[df.label.isin(["ausente", "presente_central", "presente_focal"])].copy()
    df["y"] = (df.label != "ausente").astype(int)            # 0=ausente, 1=presente
    if args.limit:
        df = df.groupby("y", group_keys=False).head(max(1, args.limit // 2))

    ys, preds, scores, missing = [], {j: [] for j in TOPJ}, {j: [] for j in TOPJ}, 0
    print(f"[4/4] eval zero-shot sobre {len(df)} slides...", flush=True)
    for i, (_, r) in enumerate(df.iterrows()):
        fp = os.path.join(FEATURES_DIR, f"{r.slide_id}.pt")
        if not os.path.exists(fp):
            missing += 1
            continue
        feats = torch.load(fp, map_location="cpu").float()
        with torch.no_grad():
            pooled = topj_pool(slide_tile_logits(feats, proj, text_w), TOPJ)
        ys.append(int(r.y))
        for j in TOPJ:
            m = pooled[j]
            preds[j].append(int(m.argmax().item()))
            scores[j].append(float(torch.softmax(m, 0)[1].item()))   # P(presente)
        if (i + 1) % 50 == 0:
            print(f"      {i+1}/{len(df)}  ({time.time()-t0:.0f}s)", flush=True)

    ys = np.array(ys)
    out = {
        "tarea": "necrosis (binario presente vs ausente, no_identificado excluido)",
        "prompts": {"classnames": CLASSNAMES, "templates": TEMPLATES, "labels": CLASS_LABELS},
        "n_total_subset": int(len(df)), "n_evaluadas": int(len(ys)), "n_missing_pt": int(missing),
        "n_por_clase": {"ausente": int((ys == 0).sum()), "presente": int((ys == 1).sum())},
        "trivial_balanced_acc": 0.5,
        "por_topj": {},
    }
    for j in TOPJ:
        p, s = np.array(preds[j]), np.array(scores[j])
        try:
            auc = roc_auc_score(ys, s)
            # mejor balanced_acc sobre umbrales del score (Youden) = techo de separabilidad
            fpr, tpr, _ = roc_curve(ys, s)
            bacc_bestthr = float(np.max(0.5 * (tpr + (1 - fpr))))
        except Exception:
            auc, bacc_bestthr = float("nan"), float("nan")
        out["por_topj"][str(j)] = {
            "auc": round(float(auc), 4),                                  # PRIMARIA (threshold-free)
            "balanced_acc_bestthr": round(bacc_bestthr, 4),              # techo de separabilidad
            "balanced_acc_argmax": round(float(balanced_accuracy_score(ys, p)), 4),  # degenerado (zero-shot sin calibrar)
            "confusion_argmax_[rows=true 0,1][cols=pred 0,1]": confusion_matrix(ys, p, labels=[0, 1]).tolist(),
        }

    tag = "" if args.version == "v1" else f"_{args.version}"   # v1 preserva el nombre histórico
    with open(os.path.join(OUT_DIR, f"necrosis{tag}_zeroshot_metrics.json"), "w") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    pd.DataFrame([{"topj": j, "auc": out["por_topj"][str(j)]["auc"],
                   "balanced_acc_bestthr": out["por_topj"][str(j)]["balanced_acc_bestthr"],
                   "balanced_acc_argmax": out["por_topj"][str(j)]["balanced_acc_argmax"]} for j in TOPJ]
                 ).to_csv(os.path.join(OUT_DIR, f"necrosis{tag}_zeroshot_metrics.csv"), index=False)

    print("\n===== RESULTADO go/no-go (necrosis, zero-shot CONCH) =====", flush=True)
    print(f"slides evaluadas: {out['n_evaluadas']}  (ausente {out['n_por_clase']['ausente']} / "
          f"presente {out['n_por_clase']['presente']}) | missing .pt: {out['n_missing_pt']}", flush=True)
    print("trivial: AUC=0.5, balanced_acc=0.5   (AUC = métrica PRIMARIA, threshold-free)", flush=True)
    for j in TOPJ:
        d = out["por_topj"][str(j)]
        print(f"  top-{j:<3d}  AUC={d['auc']:.3f}  bal_acc@bestthr={d['balanced_acc_bestthr']:.3f}  "
              f"(bal_acc@argmax={d['balanced_acc_argmax']:.3f}, degenerado)", flush=True)
    print(f"\n[done {time.time()-t0:.0f}s] -> {OUT_DIR}/necrosis{tag}_zeroshot_metrics.{{json,csv}}", flush=True)


if __name__ == "__main__":
    main()
