#!/usr/bin/env python3
"""filter_split_by_minpatch.py — filtra un split de CLAM por nº mínimo de parches.

Problema que resuelve: `inst_eval` en `models/model_clam.py` hace
`torch.topk(A, k_sample)` con `k_sample = --B`. Si una slide del TRAIN tiene
menos de B parches, `topk` revienta con "selected index k out of range" y mata
el entrenamiento (bug observado en el run 4096, Sprint 4).

Este script produce una copia filtrada del split canónico removiendo del
**split de train** las slides cuyo tensor de features `.pt` tiene
`shape[0] < --min_patches`. val y test se dejan **intactos** (el path de
evaluación — `summary()` — no llama `inst_eval`, así que no crashea).

Las slides sin `.pt` se DEJAN en el split: el dataloader de Sebastián
(`dataset_generic.py`) las salta con un warning (return None), no causan el
crash de topk.

Uso (CPU, sin GPU):
    python scripts/filter_split_by_minpatch.py \
        --canonical_split /.../clam_environ/environ/splits/<task>_100/splits_0.csv \
        --features_dir    /.../clam_environ/environ/features/pt_files \
        --min_patches     16 \
        --out_dir         splits_local/<task>_100_minpatch16

Escribe `<out_dir>/splits_0.csv` (split filtrado) y `<out_dir>/report.txt`.
"""
from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime

import pandas as pd
import torch


def count_patches(pt_path: str) -> int:
    """Devuelve shape[0] del tensor de features. Usa mmap para no cargar el
    tensor completo en RAM (algunos bags son ~100+ MB)."""
    try:
        t = torch.load(pt_path, map_location="cpu", mmap=True)
    except Exception:
        t = torch.load(pt_path, map_location="cpu")
    return int(t.shape[0])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--canonical_split", required=True,
                    help="path al splits_0.csv canónico (read-only, en clam_environ/)")
    ap.add_argument("--features_dir", required=True,
                    help="path al directorio pt_files/")
    ap.add_argument("--min_patches", type=int, required=True,
                    help="umbral: slides de train con < min_patches se remueven")
    ap.add_argument("--out_dir", required=True,
                    help="directorio donde escribir el split filtrado + report.txt")
    args = ap.parse_args()

    if not os.path.isfile(args.canonical_split):
        print(f"ERROR: no existe {args.canonical_split}", file=sys.stderr)
        return 1
    if not os.path.isdir(args.features_dir):
        print(f"ERROR: no existe {args.features_dir}", file=sys.stderr)
        return 1

    df = pd.read_csv(args.canonical_split)
    for col in ("train", "val", "test"):
        if col not in df.columns:
            print(f"ERROR: el split canónico no tiene columna '{col}'", file=sys.stderr)
            return 1

    parts = {c: [str(x) for x in df[c].dropna().tolist()] for c in ("train", "val", "test")}

    removed: list[tuple[str, int]] = []
    missing_pt: list[str] = []
    kept_train: list[str] = []

    for sid in parts["train"]:
        pt = os.path.join(args.features_dir, sid + ".pt")
        if not os.path.exists(pt):
            # sin .pt -> el dataloader la salta (return None); no causa crash de topk.
            missing_pt.append(sid)
            kept_train.append(sid)
            continue
        n = count_patches(pt)
        if n < args.min_patches:
            removed.append((sid, n))
        else:
            kept_train.append(sid)

    os.makedirs(args.out_dir, exist_ok=True)
    out_csv = os.path.join(args.out_dir, "splits_0.csv")
    new = pd.DataFrame({
        "train": pd.Series(kept_train),
        "val": pd.Series(parts["val"]),
        "test": pd.Series(parts["test"]),
    })
    new.to_csv(out_csv, index=True)

    report = os.path.join(args.out_dir, "report.txt")
    lines = [
        "filter_split_by_minpatch.py — report",
        f"generado:           {datetime.now().isoformat(timespec='seconds')}",
        f"canonical_split:    {os.path.abspath(args.canonical_split)}",
        f"features_dir:       {os.path.abspath(args.features_dir)}",
        f"min_patches:        {args.min_patches}",
        f"out_dir:            {os.path.abspath(args.out_dir)}",
        "",
        f"train: {len(parts['train'])} -> {len(kept_train)}  (removidas {len(removed)})",
        f"val:   {len(parts['val'])} (intacto)",
        f"test:  {len(parts['test'])} (intacto)",
        "",
        "slides removidas de train (shape[0] < min_patches):",
    ]
    for sid, n in sorted(removed, key=lambda x: x[1]):
        lines.append(f"  {sid}: {n} parches")
    lines.append("")
    lines.append(f"train slides sin .pt (se mantienen; el dataloader las salta): {len(missing_pt)}")
    with open(report, "w") as f:
        f.write("\n".join(lines) + "\n")

    print("\n".join(lines))
    print(f"\nescrito: {out_csv}")
    print(f"escrito: {report}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
