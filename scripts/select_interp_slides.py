"""select_interp_slides.py — elige las slides para la comparacion CLAM vs Mammoth (B7).

Criterio: slides del TEST set del fold cuyo checkpoint se usa (no vistas en train),
con h5 de features Y archivo WSI localizable en disco, priorizando casos que AMBOS
brazos clasifican bien (comparar DONDE mira cada uno, sin el ruido de un error).
Cubre las dos/tres clases de cada tarea.

Gotchas aplicados ([[data-gotchas-csv-wsi-interp]]):
  - slide_id TCGA trae UUID, pero el dir del WSI usa la forma corta (${sid%%.*}).
  - hay slides del split sin .pt/.h5 (ej. histai_1132) -> se verifica presencia.
  - los ids privados son numericos puros -> se tratan como string siempre.

Etapa 0: CPU, solo lectura. No toca modelo ni training.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path

REPO = Path("/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto")
H5_DIR = Path("/media/administrador/Storage1/sdonoso/clam_environ/environ/features/h5_files")
RESULTS = REPO / "results/b7_mammoth_interp"

# Raices donde viven las WSI, por cohorte (verificado en disco 18-jul).
WSI_ROOTS = [
    Path("/media/administrador/Storage1/sdonoso/TCGA_dataset_curated"),
    Path("/media/administrador/Storage1/sdonoso/dataset_mama_tcga"),
    Path("/media/administrador/Storage1/sdonoso/wsi"),
    Path("/media/administrador/Storage1/sdonoso/wsi_histai"),
]
WSI_EXT = (".svs", ".tif", ".tiff", ".ndpi", ".mrxs")

TASKS = {
    "tipo_histologico_3clases_ci": ["carcinoma_invasivo_tipo_no_especifico",
                                    "carcinoma_lobulillar_invasivo", "otros"],
    "carcinoma_ductal_insitu_presente_ci_reform": ["no", "si"],
    "invasion_linfatica_vascular_ci_reform": ["ausente", "presente"],
}


def build_wsi_index():
    """basename-sin-extension -> path. Indexa tambien la forma corta (pre-UUID)."""
    idx = {}
    for root in WSI_ROOTS:
        if not root.exists():
            continue
        for dirpath, _dirnames, filenames in os.walk(root):
            for fn in filenames:
                if not fn.lower().endswith(WSI_EXT):
                    continue
                full = Path(dirpath) / fn
                stem = fn
                for ext in WSI_EXT:
                    if stem.lower().endswith(ext):
                        stem = stem[: -len(ext)]
                        break
                idx.setdefault(stem, full)
                short = stem.split(".")[0]  # TCGA-XX-....-DX1 (sin UUID)
                idx.setdefault(short, full)
    return idx


def find_h5(slide_id):
    """El h5 puede estar con el id completo o con la forma corta."""
    for cand in (slide_id, slide_id.split(".")[0]):
        p = H5_DIR / f"{cand}.h5"
        if p.exists():
            return p
    # fallback: prefijo (id corto + UUID distinto)
    short = slide_id.split(".")[0]
    hits = sorted(H5_DIR.glob(f"{short}.*.h5"))
    return hits[0] if hits else None


def run_dir(task, arm, fold):
    pat = f"{arm}_{task}_f{fold}_*_s1"
    hits = sorted((RESULTS / task).glob(pat))
    # 'clam_*' tambien matchea 'clam_mammoth_*' -> filtrar explicito
    if arm == "clam":
        hits = [h for h in hits if not h.name.startswith("clam_mammoth_")]
    if not hits:
        raise SystemExit(f"Sin run para {task}/{arm}/f{fold}")
    return hits[0]


def load_preds(task, arm, fold):
    """slide_id -> dict(y_true, y_pred, probs)"""
    d = run_dir(task, arm, fold)
    out = {}
    with open(d / "test_predictions.csv") as fh:
        for row in csv.DictReader(fh):
            probs = {k: float(v) for k, v in row.items() if k.startswith("y_prob_")
                     and k != "y_prob_si"}
            out[row["slide_id"]] = dict(
                y_true=int(row["y_true"]), y_pred=int(row["y_pred"]), probs=probs)
    return out, d


def cohort_of(slide_id):
    if slide_id.startswith("TCGA"):
        return "TCGA"
    if slide_id.startswith("histai"):
        return "HistAI"
    return "privado"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fold", type=int, default=0)
    ap.add_argument("--per-class", type=int, default=1,
                    help="slides a elegir por clase y tarea")
    ap.add_argument("--out", default=str(REPO / "sprints/B7_sprint7/interp_slides.json"))
    args = ap.parse_args()

    print("Indexando WSI en disco...")
    widx = build_wsi_index()
    print(f"  {len(widx)} entradas de WSI indexadas\n")

    selection = {}
    for task, classes in TASKS.items():
        clam, clam_dir = load_preds(task, "clam", args.fold)
        mam, mam_dir = load_preds(task, "clam_mammoth", args.fold)
        assert set(clam) == set(mam), "test sets difieren entre brazos (no pareado!)"

        # candidatos: ambos brazos aciertan, con h5 y WSI presentes
        cands = {c: [] for c in range(len(classes))}
        skipped = {"sin_h5": 0, "sin_wsi": 0, "mal_clasificado": 0}
        for sid, c in clam.items():
            m = mam[sid]
            if not (c["y_pred"] == c["y_true"] and m["y_pred"] == m["y_true"]):
                skipped["mal_clasificado"] += 1
                continue
            h5 = find_h5(sid)
            if h5 is None:
                skipped["sin_h5"] += 1
                continue
            wsi = widx.get(sid) or widx.get(sid.split(".")[0])
            if wsi is None:
                skipped["sin_wsi"] += 1
                continue
            conf = max(m["probs"].values()) if m["probs"] else 0.0
            cands[c["y_true"]].append(
                dict(slide_id=sid, cohort=cohort_of(sid), y_true=c["y_true"],
                     label=classes[c["y_true"]], h5=str(h5), wsi=str(wsi),
                     conf_mammoth=conf, mpp_confiable=cohort_of(sid) != "HistAI"))

        print(f"### {task}  (fold {args.fold})")
        print(f"  descartados: {skipped}")
        picked = []
        for ci, cname in enumerate(classes):
            # Preferencia de cohorte por MAGNIFICACION FISICA confiable
            # ([[cohortes-magnificacion-fisica]]): HistAI es generic-tiff con MPP
            # placeholder -> el overlay caeria a un patch_size_level0 adivinado y la
            # tabla de um/px que pide Sebastian no seria citable. TCGA (~40x) y
            # privado (~20x) tienen MPP leible por openslide.
            pref = {"TCGA": 0, "privado": 1, "HistAI": 2}
            pool = sorted(cands[ci],
                          key=lambda r: (pref.get(r["cohort"], 3), -r["conf_mammoth"]))
            take = pool[: args.per_class]
            for r in take:
                flag = "" if r["mpp_confiable"] else "  <-- MPP NO CONFIABLE"
                print(f"  clase {ci} ({cname}): {r['slide_id']}  "
                      f"[{r['cohort']}] conf={r['conf_mammoth']:.3f}{flag}")
            if not take:
                print(f"  clase {ci} ({cname}): SIN CANDIDATO con WSI+h5")
            picked.extend(take)
        selection[task] = dict(
            fold=args.fold, classes=classes,
            ckpt_clam=str(clam_dir / f"s_{args.fold}_checkpoint.pt"),
            ckpt_mammoth=str(mam_dir / f"s_{args.fold}_checkpoint.pt"),
            slides=picked)
        print()

    Path(args.out).write_text(json.dumps(selection, indent=2))
    print(f"Seleccion escrita en: {args.out}")


if __name__ == "__main__":
    main()
