#!/usr/bin/env python3
"""preflight_minpatch.py — chequeo previo al entrenamiento CLAM.

Falla rápido (exit 1) si alguna slide del split de **train** tiene un tensor
de features `.pt` con `shape[0] < --min_patches`. Esas slides hacen crashear
`torch.topk(A, k_sample)` en `inst_eval` (k_sample = --B). Ver el bug del run
4096 (Sprint 4) y `splits_local/.../README.md`.

Se invoca desde los `.slurm` ANTES de `python main.py`:

    python scripts/preflight_minpatch.py \
        --split_dir    <path al split (dir con splits_<fold>.csv)> \
        --features_dir <path a pt_files/> \
        --min_patches  <= --B del run>
    [ $? -ne 0 ] && exit 1

Slides de train sin `.pt`: NO fallan el preflight — el dataloader las salta
(return None), no causan el crash de topk.

Exit 0 = OK para entrenar. Exit 1 = hay slides problemáticas (no entrenar).
"""
from __future__ import annotations

import argparse
import os
import sys

import pandas as pd
import torch


def count_patches(pt_path: str) -> int:
    try:
        t = torch.load(pt_path, map_location="cpu", mmap=True)
    except Exception:
        t = torch.load(pt_path, map_location="cpu")
    return int(t.shape[0])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--split_dir", required=True,
                    help="directorio con splits_<fold>.csv")
    ap.add_argument("--features_dir", required=True,
                    help="directorio pt_files/")
    ap.add_argument("--min_patches", type=int, required=True,
                    help="umbral mínimo de parches por slide de train (>= --B)")
    ap.add_argument("--fold", type=int, default=0)
    args = ap.parse_args()

    csv = os.path.join(args.split_dir, f"splits_{args.fold}.csv")
    if not os.path.isfile(csv):
        print(f"PREFLIGHT FAIL: no existe {csv}", file=sys.stderr)
        return 1
    if not os.path.isdir(args.features_dir):
        print(f"PREFLIGHT FAIL: no existe {args.features_dir}", file=sys.stderr)
        return 1

    df = pd.read_csv(csv)
    if "train" not in df.columns:
        print(f"PREFLIGHT FAIL: {csv} no tiene columna 'train'", file=sys.stderr)
        return 1
    train = [str(x) for x in df["train"].dropna().tolist()]

    bad: list[tuple[str, int]] = []
    checked = 0
    missing = 0
    for sid in train:
        pt = os.path.join(args.features_dir, sid + ".pt")
        if not os.path.exists(pt):
            missing += 1
            continue
        n = count_patches(pt)
        checked += 1
        if n < args.min_patches:
            bad.append((sid, n))

    if bad:
        print(f"PREFLIGHT FAIL: {len(bad)} slide(s) de train con < {args.min_patches} "
              f"parches (crashearían torch.topk en inst_eval):", file=sys.stderr)
        for sid, n in sorted(bad, key=lambda x: x[1]):
            print(f"  {sid}: {n} parches", file=sys.stderr)
        return 1

    print(f"PREFLIGHT OK: {checked} slides de train con >= {args.min_patches} parches "
          f"({missing} sin .pt -> el dataloader las salta).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
