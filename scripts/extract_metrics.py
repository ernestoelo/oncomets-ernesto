#!/usr/bin/env python3
"""extract_metrics.py — parse CLAM training logs into a tidy CSV.

Reads train.log lines and produces metrics.csv. Regex tuned to the actual
format that Sebastián's `utils/core_utils.py` produces:

- Per-batch (L259):
    "batch X, loss: A.AAAA, instance_loss: B.BBBB, weighted_loss: C.CCCC, ..."

- Per-epoch (L282):
    "Epoch: N, train_loss: A.AAAA, train_clustering_loss:  B.BBBB, train_error: C.CCCC"

- Validation likely emits something like:
    "Val Set, val_loss: ..., val_error: ..., auc: ..."
  (regex below tries common variants — adjust after first run)

Usage:
    python scripts/extract_metrics.py <run_dir>
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Regexes — calibrated to core_utils.py output format
# ---------------------------------------------------------------------------

# Epoch header: "Epoch: 5, train_loss: 0.4321, train_clustering_loss:  0.1234, train_error: 0.0876"
RE_EPOCH_LINE = re.compile(
    r"Epoch:\s*(?P<epoch>\d+),\s*"
    r"train_loss:\s*(?P<train_loss>[0-9.]+),\s*"
    r"train_clustering_loss:\s*(?P<train_inst_loss>[0-9.]+),\s*"
    r"train_error:\s*(?P<train_error>[0-9.]+)"
)

# Validation lines — flexible; tries multiple naming conventions
RE_VAL_LOSS = re.compile(r"val_loss:\s*(?P<v>[0-9.]+)")
RE_VAL_ERROR = re.compile(r"val_error:\s*(?P<v>[0-9.]+)")
RE_VAL_AUC = re.compile(r"(?:val_)?auc[:\s]+(?P<v>[0-9.]+)", re.IGNORECASE)
RE_VAL_ACC = re.compile(r"val_acc:\s*(?P<v>[0-9.]+)")

# Standalone Epoch marker (CLAM sometimes prints just "Epoch: N")
RE_EPOCH_HEADER = re.compile(r"^Epoch:\s*(?P<epoch>\d+)\s*$")


def parse_log(log_path: Path) -> list[dict]:
    """Walk lines, accumulate per-epoch metrics, flush on next epoch / EOF."""
    rows: list[dict] = []
    current: dict = {}

    def flush():
        nonlocal current
        if current.get("epoch") is not None:
            rows.append(current)
        current = {}

    for line in log_path.read_text(errors="ignore").splitlines():
        # Full epoch summary line
        if m := RE_EPOCH_LINE.search(line):
            new_epoch = int(m.group("epoch"))
            if current.get("epoch") is not None and current["epoch"] != new_epoch:
                flush()
            current["epoch"] = new_epoch
            current["train_loss"] = float(m.group("train_loss"))
            current["train_inst_loss"] = float(m.group("train_inst_loss"))
            current["train_error"] = float(m.group("train_error"))
            continue

        # Standalone epoch header (in case CLAM emits it)
        if m := RE_EPOCH_HEADER.match(line.strip()):
            new_epoch = int(m.group("epoch"))
            if current.get("epoch") is not None and current["epoch"] != new_epoch:
                flush()
            current.setdefault("epoch", new_epoch)
            continue

        # Validation metrics — accumulate into current epoch
        for key, regex in (
            ("val_loss", RE_VAL_LOSS),
            ("val_error", RE_VAL_ERROR),
            ("val_auc", RE_VAL_AUC),
            ("val_acc", RE_VAL_ACC),
        ):
            if m := regex.search(line):
                current[key] = float(m.group("v"))

    flush()
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
        print("WARN: no epoch metrics extracted — check regexes against log format", file=sys.stderr)
        print("First 30 lines of log for inspection:", file=sys.stderr)
        for line in log_path.read_text(errors="ignore").splitlines()[:30]:
            print(f"  {line}", file=sys.stderr)
        return 2

    out_path = args.run_dir / "metrics.csv"
    fieldnames = [
        "epoch",
        "train_loss",
        "train_inst_loss",
        "train_error",
        "val_loss",
        "val_error",
        "val_auc",
        "val_acc",
    ]
    with out_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"wrote {out_path} with {len(rows)} epochs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
