#!/usr/bin/env python
"""pathpt_localization_heatmap.py — localización tile-level de necrosis (zero-shot CONCH).

Material visual para la presentación PathPT: valida el GROUNDING tile-level del go/no-go
(sprints/B5_sprint5/pathpt/etapa0_gonogo_necrosis.md §9, AUC zero-shot ~0.677). Para
slides `presente_central` (necrosis marcada), pinta cada parche en sus coordenadas (x,y)
del h5 coloreado por su probabilidad zero-shot de "necrosis presente" → muestra que CONCH
localiza la necrosis SIN entrenar, que es lo que PathPT explota (θ_v + pseudo-labels).

CPU, sin GPU, sin entrenar, read-only sobre clam_environ. Mismo truco que el go/no-go:
features extraídas con proj_contrast=False → se reconstruye el espacio contrastivo con
feats @ visual.proj_contrast antes del coseno vs texto.

Ejemplos ILUSTRATIVOS: se computan varias candidatas y se eligen las de mayor contraste
espacial (para claridad de la figura); NO es una métrica (la métrica es el AUC del go/no-go).

Uso: /home/sdonoso/miniconda3/envs/clam_latest/bin/python scripts/pathpt_localization_heatmap.py
"""
import os, sys, time
import numpy as np
import torch
import torch.nn.functional as F
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

CONCH_REPO   = "/media/administrador/Storage1/sdonoso/clam_environ/CONCH"
CKPT         = "/home/sdonoso/.cache/huggingface/hub/models--MahmoodLab--conch/snapshots/f9ca9f877171a28ade80228fb195ac5d79003357/pytorch_model.bin"
H5_DIR       = "/media/administrador/Storage1/sdonoso/clam_environ/environ/features/h5_files"
CSV          = "/media/administrador/Storage1/sdonoso/clam_environ/environ/csv/dataset_carcinoma_ductal_in_situ_necrosis_label.csv"
OUT_DIR      = "/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/sprints/B5_sprint5/pathpt/figuras/slide_assets"

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
sys.path.insert(0, CONCH_REPO)
from conch.open_clip_custom import create_model_from_pretrained, get_tokenizer, tokenize  # noqa: E402
import h5py  # noqa: E402

TEMPLATES = [
    "CLASSNAME.",
    "a photomicrograph showing CLASSNAME.",
    "a histopathology image of CLASSNAME.",
    "an H&E stained image showing CLASSNAME.",
    "breast tissue showing CLASSNAME.",
]
# necrosis v1 (idéntico al go/no-go): clase 0 = ausente, clase 1 = presente
CLASSNAMES = [
    ["ductal carcinoma in situ without necrosis", "viable tumor cells without necrosis", "benign breast tissue"],
    ["tumor necrosis", "comedonecrosis", "necrotic cellular debris", "central necrosis in ductal carcinoma in situ"],
]
N_CANDIDATES = 12      # cuántas presente_central evaluar
N_SHOW = 3             # cuántas mostrar (mayor contraste)
TOPK = 25              # tiles top-necrosis a resaltar


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
    return torch.stack(weights, 1)          # [512, 2]


@torch.no_grad()
def tile_prob_present(coords, feats, proj, text_w):
    """prob zero-shot de 'presente' por parche = softmax([cos_aus, cos_pres])[1]."""
    fc = F.normalize(feats @ proj, dim=-1)
    logits = fc @ text_w                     # [N, 2]
    return torch.softmax(logits, dim=1)[:, 1].numpy()


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    t0 = time.time()
    print("[1/4] CONCH (CPU)...", flush=True)
    model = create_model_from_pretrained("conch_ViT-B-16", checkpoint_path=CKPT, device="cpu", return_transform=False)
    model.eval()
    tokenizer = get_tokenizer()
    proj = model.visual.proj_contrast.detach().float()
    text_w = build_text_weights(model, tokenizer, CLASSNAMES).float()

    print("[2/4] candidatas presente_central...", flush=True)
    df = pd.read_csv(CSV)
    pc = [s for s in df[df.label == "presente_central"].slide_id
          if os.path.exists(os.path.join(H5_DIR, f"{s}.h5"))][:N_CANDIDATES]

    print("[3/4] scoring por parche...", flush=True)
    items = []
    for sid in pc:
        with h5py.File(os.path.join(H5_DIR, f"{sid}.h5"), "r") as h:
            coords = h["coords"][:].astype(np.float64)
            feats = torch.from_numpy(h["features"][:]).float()
        p = tile_prob_present(coords, feats, proj, text_w)
        n = len(p)
        pct = p.argsort().argsort() / max(1, n - 1) * 100.0    # ranking relativo intra-slide
        # forma de la nube (descartar franjas degeneradas)
        w = np.ptp(coords[:, 0]); hh = np.ptp(coords[:, 1])
        ar = hh / (w + 1e-9)
        # concentración espacial de los top-5% tiles = evidencia de localización
        ktop = max(10, int(0.05 * n))
        top = np.argsort(p)[-ktop:]
        cen = coords[top].mean(0)
        diag = np.hypot(w, hh) + 1e-9
        disp = np.sqrt(((coords[top] - cen) ** 2).sum(1)).mean() / diag
        items.append({"sid": sid, "coords": coords, "pct": pct, "n": n,
                      "disp": disp, "ok_shape": 0.25 < ar < 4.0})
        print(f"    {sid}: N={n:5d}  disp_top={disp:.3f}  ar_ok={items[-1]['ok_shape']}", flush=True)

    # ejemplos = menor dispersión espacial de los top tiles (más localizado), con forma sana
    cand = [d for d in items if d["ok_shape"]] or items
    cand.sort(key=lambda d: d["disp"])
    show = cand[:N_SHOW]

    print("[4/4] figura...", flush=True)
    fig = plt.figure(figsize=(4.3 * N_SHOW + 0.6, 4.7), dpi=220)
    gs = GridSpec(1, N_SHOW + 1, width_ratios=[1] * N_SHOW + [0.05], wspace=0.12)
    sc = None
    for k, it in enumerate(show):
        ax = fig.add_subplot(gs[0, k])
        x, y, pct = it["coords"][:, 0], it["coords"][:, 1], it["pct"]
        order = np.argsort(pct)                     # dibujar altos al final (encima)
        sc = ax.scatter(x[order], y[order], c=pct[order], cmap="magma",
                        s=12, marker="s", vmin=0, vmax=100, linewidths=0)
        top = np.argsort(pct)[-TOPK:]
        ax.scatter(x[top], y[top], s=46, marker="o", facecolors="none",
                   edgecolors="#00E5FF", linewidths=1.3)
        ax.set_aspect("equal"); ax.invert_yaxis(); ax.set_axis_off()
        ax.set_title(f"necrosis presente · {it['n']} parches", fontsize=11, color="#222222")
    cax = fig.add_subplot(gs[0, N_SHOW])
    cb = fig.colorbar(sc, cax=cax)
    cb.set_label("ranking de necrosis intra-slide (percentil)", fontsize=10)
    fig.suptitle("CONCH localiza la necrosis sin entrenar — los tiles top-necrosis se agrupan (○ = top-25)",
                 fontsize=13, weight="bold", color="#1E5C6B", y=1.02)
    fig.text(0.5, -0.04,
             "Color = ranking RELATIVO de necrosis por parche dentro de cada slide (percentil del coseno texto-imagen "
             "sobre prompts {necrosis presente / ausente}, espacio contrastivo CONCH reconstruido con feats @ proj_contrast). "
             "Resalta la LOCALIZACIÓN, no la calibración absoluta — esa la aporta el prompt-tuning de PathPT. Ejemplos "
             "elegidos por concentración espacial de los top tiles. Sin GPU, sin entrenar.",
             ha="center", va="top", fontsize=8.2, style="italic", color="#555555", wrap=True)

    out = os.path.join(OUT_DIR, "M10_necrosis_localizacion_tile.png")
    fig.savefig(out, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    rel = os.path.relpath(out, "/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto")
    print(f"[done {time.time()-t0:.0f}s] -> {rel}\n  mostradas: {[d['sid'] for d in show]}")


if __name__ == "__main__":
    main()
