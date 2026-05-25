#!/usr/bin/env python3
"""train_dsmil.py — entrenamiento DSMIL_CLAM_MB sobre una tarea binaria.

Replica el patrón de `clam_environ/main.py` + `core_utils.train_loop_clam`
SIN modificar nada bajo `clam_environ/` (regla 2 de CLAUDE.md). Añade
el término L_max sobre el instance scorer W_0 del aggregator DSMIL,
necesario porque el `argmax` del Stream 1 es no diferenciable
(decisión R1 = B.1.3, w_max = 0.1; `hipotesis.md` §5).

Loss total por bag:
    L = bag_weight · L_bag(CE)
      + (1 - bag_weight) · L_inst(SmoothTop1SVM sobre β)
      + w_max · L_max(CE sobre c.max(0))

Args bendecidos (CLAUDE.md "Args bendecidos por Sebastián"):
    --drop_out 0.25 --lr 2e-4 --B 8 --bag_weight 0.7 --embed_dim 512
Nuevo en DSMIL:
    --w_max 0.1   (R1 = B.1.3; valor fijo, no se tunea)

Estado: training loop SOLO (sin val/test/summary/checkpoint).
Suficiente para §6.3 mini-train (1 epoch, observar que train_loss
decrece y que las métricas de gradiente son sanas). El flujo completo
(val por epoch, early_stopping, summary de test, checkpoint) se
implementa en una iteración posterior cuando se prepare el SLURM del
experimento de las 3 tareas × 30 epochs.

Métricas por época impresas y volcadas a `metrics.jsonl`:
    train_loss              media de L_bag       (CE sobre logits)
    train_clustering_loss   media de L_inst      (SmoothTop1SVM)
    train_max_loss          media de L_max       (CE sobre c.max(0))
    grad_W0_mean            ‖grad‖₂ de i_classifier (W_0)
    grad_q_mean             ‖grad‖₂ de q-net
    train_error             (Y_hat != label).mean()
    processed_batches

NUNCA invocar con `python` (workaround B: `which python` apunta a
ADFRsuite python2.7 roto). Siempre vía `sbatch <script.slurm>` o el
binario absoluto `/home/sdonoso/miniconda3/envs/clam_latest/bin/python`.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

_CLAM_ENVIRON = "/media/administrador/Storage1/sdonoso/clam_environ"
_REPO = "/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto"
for _p in (_CLAM_ENVIRON, _REPO):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from dataset_modules.dataset_generic import Generic_MIL_Dataset  # noqa: E402
from utils.utils import get_split_loader, get_optim  # noqa: E402
from utils.core_utils import Accuracy_Logger  # noqa: E402

from models_dsmil import DSMIL_CLAM_MB  # noqa: E402


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--task", required=True)
    p.add_argument("--exp_code", default=None,
                   help="default: dsmil_<task>")
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--fold", type=int, default=0)

    p.add_argument("--csv_path", required=True,
                   help="CSV de labels (absoluto, bajo clam_environ/)")
    p.add_argument("--data_root_dir", required=True,
                   help="dir absoluto que contiene features/pt_files/")
    p.add_argument("--split_dir", required=True,
                   help="dir absoluto con splits_<fold>.csv")
    p.add_argument("--results_dir", required=True,
                   help="dir absoluto BAJO clam_testing2/ (containment)")

    p.add_argument("--drop_out", type=float, default=0.25)
    p.add_argument("--lr", type=float, default=2e-4)
    p.add_argument("--reg", type=float, default=1e-5)
    p.add_argument("--B", type=int, default=8)
    p.add_argument("--bag_weight", type=float, default=0.7)
    p.add_argument("--w_max", type=float, default=0.1,
                   help="peso de L_max sobre c (R1 = B.1.3; fijo)")
    p.add_argument("--embed_dim", type=int, default=512)
    p.add_argument("--max_epochs", type=int, default=1)
    p.add_argument("--n_classes", type=int, default=2)

    p.add_argument("--label_dict", default='{"no": 0, "si": 1}',
                   help='JSON con label_dict (binario por default)')
    return p.parse_args()


def build_model(args: argparse.Namespace, device: torch.device) -> nn.Module:
    if args.embed_dim != 512:
        raise ValueError("DSMIL_CLAM_MB con CONCH requiere embed_dim=512")
    from topk.svm import SmoothTop1SVM
    instance_loss_fn = SmoothTop1SVM(n_classes=2)
    if device.type == "cuda":
        instance_loss_fn = instance_loss_fn.cuda()
    model = DSMIL_CLAM_MB(
        gate=True, size_arg="small",
        dropout=args.drop_out, k_sample=args.B,
        n_classes=args.n_classes, subtyping=False,
        instance_loss_fn=instance_loss_fn,
        embed_dim=args.embed_dim,
        dsmil_nonlinear=True, dsmil_passing_v=False,
    )
    return model.to(device)


def grad_l2_norm(module: nn.Module) -> float:
    """‖grad‖₂ sumado sobre todos los params del submódulo."""
    sq = 0.0
    any_grad = False
    for p in module.parameters():
        if p.grad is not None:
            sq += p.grad.data.norm(2).item() ** 2
            any_grad = True
    return sq ** 0.5 if any_grad else 0.0


def train_one_epoch(epoch, model, loader, optimizer, loss_fn,
                    bag_weight, w_max, device):
    """Réplica de `core_utils.train_loop_clam` + L_max sobre c."""
    model.train()
    acc_logger = Accuracy_Logger(n_classes=model.n_classes)
    inst_logger = Accuracy_Logger(n_classes=model.n_classes)

    sums = {"loss": 0.0, "inst_loss": 0.0, "max_loss": 0.0, "error": 0.0,
            "grad_W0": 0.0, "grad_q": 0.0}
    processed = 0

    for batch_idx, batch in enumerate(loader):
        if batch is None:
            continue
        data, label = batch
        data, label = data.to(device), label.to(device)

        logits, Y_prob, Y_hat, _, instance_dict = model(
            data, label=label, instance_eval=True
        )
        acc_logger.log(Y_hat, label)

        L_bag = loss_fn(logits, label)
        L_inst = instance_dict["instance_loss"]
        c = instance_dict["instance_scores_c"]      # [N, n_classes]
        max_pred, _ = c.max(dim=0)                  # [n_classes]
        L_max = F.cross_entropy(max_pred.view(1, -1), label)

        total = (bag_weight * L_bag
                 + (1.0 - bag_weight) * L_inst
                 + w_max * L_max)
        total.backward()

        # Métricas de gradiente: post-backward, pre-step (después step
        # los grads siguen disponibles hasta zero_grad, pero pre-step es
        # más limpio conceptualmente).
        sums["grad_W0"] += grad_l2_norm(model.dsmil_aggregator.i_classifier)
        sums["grad_q"] += grad_l2_norm(model.dsmil_aggregator.q)

        optimizer.step()
        optimizer.zero_grad()

        inst_logger.log_batch(
            instance_dict["inst_preds"], instance_dict["inst_labels"]
        )
        sums["loss"] += L_bag.item()
        sums["inst_loss"] += L_inst.item()
        sums["max_loss"] += L_max.item()
        sums["error"] += float((Y_hat != label).item())
        processed += 1

    if processed == 0:
        return {"epoch": epoch, "processed_batches": 0,
                "train_loss": float("nan")}, acc_logger, inst_logger

    metrics = {
        "epoch": epoch,
        "train_loss": sums["loss"] / processed,
        "train_clustering_loss": sums["inst_loss"] / processed,
        "train_max_loss": sums["max_loss"] / processed,
        "train_error": sums["error"] / processed,
        "grad_W0_mean": sums["grad_W0"] / processed,
        "grad_q_mean": sums["grad_q"] / processed,
        "processed_batches": processed,
    }
    return metrics, acc_logger, inst_logger


def main() -> int:
    args = parse_args()
    if args.exp_code is None:
        args.exp_code = f"dsmil_{args.task}"
    args.opt = "adam"   # get_optim de Sebastián lo lee como atributo

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(args.seed)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[INFO] device: {device}  (cuda available: {torch.cuda.is_available()})")
    if device.type == "cuda":
        print(f"[INFO] GPU: {torch.cuda.get_device_name(0)}")

    # Containment: results_dir DEBE vivir bajo clam_testing2/.
    results_root = Path(args.results_dir).resolve()
    expected = "/media/administrador/Storage1/sdonoso/clam_testing2/"
    if not str(results_root).startswith(expected):
        raise ValueError(
            f"--results_dir debe estar bajo {expected} (containment). "
            f"Recibido: {results_root}"
        )
    results_dir = results_root / f"{args.exp_code}_s{args.seed}"
    results_dir.mkdir(parents=True, exist_ok=True)
    print(f"[INFO] results_dir: {results_dir}")

    # Dataset: idéntico patrón a clam_environ/main.py L686-701.
    label_dict = json.loads(args.label_dict)
    if args.n_classes != len(set(label_dict.values())):
        raise ValueError(
            f"n_classes={args.n_classes} no coincide con "
            f"label_dict={label_dict}"
        )
    data_dir = os.path.join(args.data_root_dir, "features")
    if not os.path.isdir(os.path.join(data_dir, "pt_files")):
        raise FileNotFoundError(
            f"no existe {data_dir}/pt_files/  "
            f"(--data_root_dir debe apuntar a clam_environ/environ)"
        )

    dataset = Generic_MIL_Dataset(
        csv_path=args.csv_path,
        data_dir=data_dir,
        shuffle=False, seed=args.seed, print_info=True,
        label_dict=label_dict,
        patient_strat=False, ignore=[],
    )
    split_csv = os.path.join(args.split_dir, f"splits_{args.fold}.csv")
    if not os.path.isfile(split_csv):
        raise FileNotFoundError(f"no existe {split_csv}")
    train_split, val_split, test_split = dataset.return_splits(
        from_id=False, csv_path=split_csv
    )
    print(f"[INFO] train={len(train_split)}  "
          f"val={len(val_split)}  test={len(test_split)}")

    loss_fn = nn.CrossEntropyLoss()
    model = build_model(args, device)
    optimizer = get_optim(model, args)
    train_loader = get_split_loader(
        train_split, training=True, testing=False, weighted=True
    )

    # Snapshot inicial de pesos del aggregator (para inspección manual).
    init_snap = {
        "W0_weight_norm": float(
            model.dsmil_aggregator.i_classifier.weight.data.norm().item()
        ),
        "q0_weight_norm": float(
            model.dsmil_aggregator.q[0].weight.data.norm().item()
        ),
    }
    with open(results_dir / "init_snapshot.json", "w") as f:
        json.dump(init_snap, f, indent=2)

    log_path = results_dir / "metrics.jsonl"
    with open(log_path, "w") as logf:
        for epoch in range(args.max_epochs):
            metrics, acc_log, inst_log = train_one_epoch(
                epoch, model, train_loader, optimizer, loss_fn,
                args.bag_weight, args.w_max, device,
            )
            print(
                f"[EPOCH {epoch}] "
                f"train_loss={metrics.get('train_loss', float('nan')):.4f}  "
                f"clustering_loss={metrics.get('train_clustering_loss', float('nan')):.4f}  "
                f"max_loss={metrics.get('train_max_loss', float('nan')):.4f}  "
                f"|grad W_0|={metrics.get('grad_W0_mean', 0.0):.4f}  "
                f"|grad q|={metrics.get('grad_q_mean', 0.0):.4f}  "
                f"error={metrics.get('train_error', float('nan')):.4f}  "
                f"batches={metrics['processed_batches']}",
                flush=True,
            )
            logf.write(json.dumps(metrics) + "\n")
            logf.flush()

    # Snapshot final del aggregator (para comparar contra init).
    final_snap = {
        "W0_weight_norm": float(
            model.dsmil_aggregator.i_classifier.weight.data.norm().item()
        ),
        "q0_weight_norm": float(
            model.dsmil_aggregator.q[0].weight.data.norm().item()
        ),
    }
    with open(results_dir / "final_snapshot.json", "w") as f:
        json.dump(final_snap, f, indent=2)
    print(f"[INFO] init  W0_norm={init_snap['W0_weight_norm']:.4f}  "
          f"q0_norm={init_snap['q0_weight_norm']:.4f}")
    print(f"[INFO] final W0_norm={final_snap['W0_weight_norm']:.4f}  "
          f"q0_norm={final_snap['q0_weight_norm']:.4f}")
    print(f"[DONE] §6.3 mini-train completado. metrics.jsonl en {log_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
