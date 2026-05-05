#!/usr/bin/env python3
"""extract_metrics.py — parse CLAM training logs into a tidy CSV.

Reads train.log lines and produces metrics.csv with one row per epoch.
Adjust REGEX_* constants if Sebastián's logging format differs from the
default CLAM output.

Usage:
    python scripts/extract_metrics.py <run_dir>

Where <run_dir> is a directory under
sprints/B3_sprint3/objetivo_2_entrenamiento/logs/ containing train.log.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

# Default regexes — adapt to Sebastián's actual log format after first run.
REGEX_EPOCH = re.compile(r"Epoch:\s*(\d+)")
REGEX_TRAIN_LOSS = re.compile(r"train_loss:\s*([0-9.]+)")
REGEX_VAL_LOSS = re.compile(r"val_loss:\s*([0-9.]+)")
REGEX_VAL_AUC = re.compile(r"val_auc:\s*([0-9.]+)")
REGEX_VAL_ACC = re.compile(r"val_acc:\s*([0-9.]+)")


def parse_log(log_path: Path) -> list[dict]:
    """Group lines by epoch and pull metrics.

    Strategy: walk lines, accumulate metrics per epoch. Flush when next epoch
    appears or EOF.
    """
    rows: list[dict] = []
    current: dict = {}

    for line in log_path.read_text(errors="ignore").splitlines():
        if m := REGEX_EPOCH.search(line):
            if current.get("epoch") is not None and current["epoch"] != int(m.group(1)):
                rows.append(current)
                current = {}
            current["epoch"] = int(m.group(1))

        for key, regex in (
            ("train_loss", REGEX_TRAIN_LOSS),
            ("val_loss", REGEX_VAL_LOSS),
            ("val_auc", REGEX_VAL_AUC),
            ("val_acc", REGEX_VAL_ACC),
        ):
            if m := regex.search(line):
                current[key] = float(m.group(1))

    if current.get("epoch") is not None:
        rows.append(current)
    return rows


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("run_dir", type=Path, help="directory with train.log")
    args = p.parse_args()

    log_path = args.run_dir / "train.log"
    if not log_path.exists():
        print(f"ERROR: {log_path} not found", file=sys.stderr)
        return 1

    rows = parse_log(log_path)
    if not rows:
        print("WARN: no epoch metrics extracted — check regexes", file=sys.stderr)
        return 2

    out_path = args.run_dir / "metrics.csv"
    fieldnames = ["epoch", "train_loss", "val_loss", "val_auc", "val_acc"]
    with out_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"wrote {out_path} with {len(rows)} epochs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
