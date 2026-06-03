#!/usr/bin/env python3
"""train_dsmil.py — entrenamiento DSMIL_CLAM_MB (o CLAM_MB baseline) sobre una
tarea binaria.

`--model_type` (default `dsmil`) elige el modelo SIN cambiar el harness
train/val/test (comparación apples-to-apples, Objetivo 5 Fase 1 vs Fase 2):
- `dsmil`: DSMIL_CLAM_MB + L_max (comportamiento original, byte-idéntico a
  jobs 4135/4137).
- `clam`:  CLAM_MB baseline (≡ job 4109; loss bag+inst SIN L_max). En este
  modo NO se generan init/final_snapshot.json y las columnas
  train_max_loss / grad_W0_mean / grad_q_mean del metrics.jsonl salen 0.0
  (son diagnósticos solo-DSMIL, sin efecto en el entrenamiento CLAM).
- `clam_mammoth`: CLAM_MB con la 1ª capa lineal reemplazada por Mammoth
  (Obj 6). MISMA loss y MISMO harness que `clam` (cae en el mismo path, sin
  L_max ni snapshots dual-stream); único delta = el patch embed. Comparación
  paired vs `clam` sobre los mismos splits.

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

Flujo completo: train + val por epoch + test final. Reproduce el patrón
de `clam_environ/main.py` + `core_utils.train()` con:
- `EarlyStopping` heredada de CLAM (R6 §5: stop_epoch=50 > max_epochs=30
  → nunca triggea, pero `save_checkpoint` SÍ guarda best por val_loss).
- Test eval con `balanced_accuracy_score` + `confusion_matrix` de
  sklearn (métrica decisiva de hipotesis.md §2 + extras de auditoría).

Artefactos generados en `<results_dir>/<exp_code>_s<seed>/`:
    metrics.jsonl            train + val por época
    init_snapshot.json       pesos del aggregator pre-train
    final_snapshot.json      pesos del aggregator post-train
    s_<fold>_checkpoint.pt   mejor modelo por val_loss
    summary.csv              folds, test_auc, val_auc, test_acc, val_acc
    split_<fold>_results.pkl patient_results (slide_id → {slide_id, prob, label})
    test_metrics.json        test_auc, test_acc, balanced_acc, confusion 2x2
    test_predictions.csv     slide_id, y_true, y_prob_si, y_pred

Métricas por época impresas y volcadas a `metrics.jsonl`:
    train_loss              media de L_bag       (CE sobre logits)
    train_clustering_loss   media de L_inst      (SmoothTop1SVM)
    train_max_loss          media de L_max       (CE sobre c.max(0))
    grad_W0_mean            ‖grad‖₂ de i_classifier (W_0)
    grad_q_mean             ‖grad‖₂ de q-net
    train_error             (Y_hat != label).mean()
    val_loss / val_auc / val_error
    processed_batches

NUNCA invocar con `python` (workaround B: `which python` apunta a
ADFRsuite python2.7 roto). Siempre vía `sbatch <script.slurm>` o el
binario absoluto `/home/sdonoso/miniconda3/envs/clam_latest/bin/python`.
"""
from __future__ import annotations

import argparse
import json
import os
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn.metrics import (
    balanced_accuracy_score,
    confusion_matrix,
    roc_auc_score,
)

_CLAM_ENVIRON = "/media/administrador/Storage1/sdonoso/clam_environ"
_REPO = "/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto"
for _p in (_CLAM_ENVIRON, _REPO):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from dataset_modules.dataset_generic import Generic_MIL_Dataset  # noqa: E402
from utils.utils import get_split_loader, get_optim  # noqa: E402
from utils.core_utils import Accuracy_Logger, EarlyStopping  # noqa: E402

from models_dsmil import DSMIL_CLAM_MB  # noqa: E402


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--task", required=True)
    p.add_argument("--exp_code", default=None,
                   help="default: <model_type>_<task> (ej. dsmil_<task> / clam_<task>)")
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
    p.add_argument("--model_type", choices=["dsmil", "clam", "clam_mammoth"],
                   default="dsmil",
                   help="dsmil = DSMIL_CLAM_MB (default; path byte-idéntico a "
                        "jobs 4135/4137). clam = CLAM_MB baseline (MISMO harness "
                        "train/val/test, SIN L_max ni aggregator dual-stream) — "
                        "para comparación apples-to-apples (Obj 5 Fase 1 vs Fase 2). "
                        "clam_mammoth = CLAM_MB con la 1ª capa lineal reemplazada "
                        "por Mammoth (Obj 6; MISMO harness y MISMA loss que clam, "
                        "único delta = el patch embed → comparación paired vs clam).")

    # Hiperparámetros de Mammoth (solo aplican con --model_type clam_mammoth;
    # ignorados en dsmil/clam). Defaults = recomendados del paper (README MAMMOTH).
    p.add_argument("--mammoth_num_experts", type=int, default=30)
    p.add_argument("--mammoth_num_slots", type=int, default=10)
    p.add_argument("--mammoth_num_heads", type=int, default=16)
    p.add_argument("--mammoth_slot_dim", type=int, default=256)
    p.add_argument("--mammoth_keep_slots", action="store_true",
                   help="si se pasa, Mammoth devuelve E·S features agregadas en "
                        "vez de los N parches (cambia la semántica de attention/"
                        "instance-loss). Obj 6 #1: por defecto FALSE — mantiene N "
                        "parches, comparación limpia vs el baseline CLAM.")

    p.add_argument("--early_stopping", action="store_true",
                   help="activa EarlyStopping de CLAM. R6 §5: con "
                        "stop_epoch=50 > max_epochs=30 nunca triggea, "
                        "pero save_checkpoint sí guarda el best por "
                        "val_loss → el test se evalúa sobre ese best.")
    p.add_argument("--patience", type=int, default=20,
                   help="patience de EarlyStopping (default CLAM)")
    p.add_argument("--stop_epoch", type=int, default=50,
                   help="stop_epoch de EarlyStopping (default CLAM). "
                        "Si max_epochs<=stop_epoch, el corte nunca "
                        "triggea (R6 §5).")

    p.add_argument("--label_dict", default='{"no": 0, "si": 1}',
                   help='JSON con label_dict (binario por default)')
    return p.parse_args()


def build_model(args: argparse.Namespace, device: torch.device) -> nn.Module:
    if args.embed_dim != 512:
        raise ValueError("CONCH requiere embed_dim=512")
    from topk.svm import SmoothTop1SVM
    instance_loss_fn = SmoothTop1SVM(n_classes=2)
    if device.type == "cuda":
        instance_loss_fn = instance_loss_fn.cuda()
    if args.model_type == "clam":
        # CLAM_MB baseline (idéntico al job 4109: --model_type clam_mb
        # --inst_loss svm --B 8 --bag_weight 0.7). Mismo instance_loss_fn
        # SmoothTop1SVM. Sin aggregator dual-stream ni L_max.
        from models.model_clam import CLAM_MB  # noqa: E402
        model = CLAM_MB(
            gate=True, size_arg="small",
            dropout=args.drop_out, k_sample=args.B,
            n_classes=args.n_classes, subtyping=False,
            instance_loss_fn=instance_loss_fn,
            embed_dim=args.embed_dim,
        )
    elif args.model_type == "clam_mammoth":
        # CLAM_MB con la 1ª capa lineal reemplazada por Mammoth (Obj 6). MISMO
        # instance_loss_fn (SmoothTop1SVM), MISMO harness; único delta vs 'clam'
        # = el patch embed. forward/inst_eval heredados de CLAM_MB → la
        # comparación clam vs clam_mammoth es paired a nivel de arquitectura.
        from models_mammoth import CLAM_MB_Mammoth  # noqa: E402
        model = CLAM_MB_Mammoth(
            gate=True, size_arg="small",
            dropout=args.drop_out, k_sample=args.B,
            n_classes=args.n_classes, subtyping=False,
            instance_loss_fn=instance_loss_fn,
            embed_dim=args.embed_dim,
            mammoth_num_experts=args.mammoth_num_experts,
            mammoth_num_slots=args.mammoth_num_slots,
            mammoth_num_heads=args.mammoth_num_heads,
            mammoth_slot_dim=args.mammoth_slot_dim,
            mammoth_keep_slots=args.mammoth_keep_slots,
        )
    else:
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
                    bag_weight, w_max, device, model_type="dsmil"):
    """Réplica de `core_utils.train_loop_clam` + L_max sobre c (solo DSMIL).

    Con model_type="clam" el path es EXACTAMENTE core_utils.train_loop_clam
    (L_bag + L_inst, sin L_max ni grad-logging del aggregator dual-stream).
    """
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
        if model_type == "dsmil":
            c = instance_dict["instance_scores_c"]      # [N, n_classes]
            max_pred, _ = c.max(dim=0)                  # [n_classes]
            L_max = F.cross_entropy(max_pred.view(1, -1), label)
            total = (bag_weight * L_bag
                     + (1.0 - bag_weight) * L_inst
                     + w_max * L_max)
        else:
            # CLAM baseline: idéntico a core_utils.train_loop_clam (sin L_max).
            L_max = torch.zeros((), device=logits.device)
            total = bag_weight * L_bag + (1.0 - bag_weight) * L_inst
        total.backward()

        # Métricas de gradiente del aggregator dual-stream: solo DSMIL.
        # Post-backward, pre-step (los grads siguen disponibles hasta
        # zero_grad, pero pre-step es más limpio conceptualmente).
        if model_type == "dsmil":
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


def validate_one_epoch(epoch, model, loader, loss_fn, device,
                       early_stopping=None, ckpt_path=None):
    """Réplica conceptual de `core_utils.validate_clam` (sin tensorboard).

    Devuelve (should_stop, val_metrics_dict). Si `early_stopping` es no-None,
    guarda el best checkpoint en `ckpt_path` cuando val_loss mejora
    (lógica de save_checkpoint en clam_environ/utils/core_utils.py:86-91).
    Con max_epochs <= stop_epoch, `should_stop` siempre es False (R6 §5)
    — pero el best checkpoint SÍ se va guardando, que es lo único que
    usamos al cargar al final del training.
    """
    model.eval()
    val_loss = 0.0
    val_error = 0.0
    prob_list = []
    labels_list = []

    with torch.inference_mode():
        for batch in loader:
            if batch is None:
                continue
            data, label = batch
            data, label = data.to(device), label.to(device)
            # No pasamos instance_eval=True en val: el wrapper devuelve
            # results_dict sin instance_loss (acc_logger no se usa acá).
            logits, Y_prob, Y_hat, _, _ = model(data)
            val_loss += loss_fn(logits, label).item()
            val_error += float((Y_hat != label).item())
            prob_list.append(Y_prob.cpu().numpy())
            labels_list.append(label.item())

    processed = len(prob_list)
    if processed == 0:
        return False, {"val_loss": float("nan"), "val_error": float("nan"),
                       "val_auc": float("nan"), "val_processed": 0}

    val_loss /= processed
    val_error /= processed
    prob = np.vstack(prob_list)
    labels = np.array(labels_list)
    n_classes = model.n_classes
    if n_classes == 2:
        # Solo computable si hay >= 1 muestra de cada clase.
        if len(np.unique(labels)) == 2:
            val_auc = float(roc_auc_score(labels, prob[:, 1]))
        else:
            val_auc = float("nan")
    else:
        val_auc = float("nan")  # multi-clase no se usa en este experimento

    should_stop = False
    if early_stopping is not None:
        assert ckpt_path is not None
        early_stopping(epoch, val_loss, model, ckpt_name=ckpt_path)
        should_stop = bool(early_stopping.early_stop)

    return should_stop, {
        "val_loss": val_loss,
        "val_error": val_error,
        "val_auc": val_auc,
        "val_processed": processed,
    }


def compute_test_metrics(model, loader, device):
    """Réplica de `core_utils.summary` + extras de auditoría.

    Devuelve:
        patient_results: dict slide_id → {slide_id, prob, label}
            (mismo schema que main.py split_<i>_results.pkl).
        test_metrics: dict con test_auc, test_acc, balanced_acc,
            confusion (lista 2x2).
        predictions: DataFrame con columnas
            slide_id, y_true, y_prob_si, y_pred (1 fila por slide).
    """
    model.eval()
    slide_ids = loader.dataset.slide_data['slide_id']

    patient_results = {}
    rows = []
    prob_mat = []  # probs completas [N, n_classes] (AUC multiclase + trazabilidad)
    n_classes = model.n_classes

    with torch.inference_mode():
        for batch_idx, batch in enumerate(loader):
            if batch is None:
                continue
            data, label = batch
            data, label = data.to(device), label.to(device)
            slide_id = slide_ids.iloc[batch_idx]
            logits, Y_prob, Y_hat, _, _ = model(data)
            probs = Y_prob.cpu().numpy()             # [1, n_classes]
            y_true = int(label.item())
            y_pred = int(Y_hat.item())
            patient_results[slide_id] = {
                'slide_id': np.array(slide_id),
                'prob': probs,
                'label': y_true,
            }
            prob_mat.append(probs[0])
            rows.append({
                'slide_id': slide_id,
                'y_true': y_true,
                'y_prob_si': float(probs[0, 1]) if n_classes >= 2 else float("nan"),
                'y_pred': y_pred,
            })

    if not rows:
        return patient_results, {
            "test_auc": float("nan"), "test_acc": float("nan"),
            "balanced_acc": float("nan"), "confusion": None,
            "n_test": 0,
        }, pd.DataFrame(columns=['slide_id', 'y_true', 'y_prob_si', 'y_pred'])

    preds_df = pd.DataFrame(rows)
    prob_full = np.vstack(prob_mat)                 # [N, n_classes]
    # probs por clase (y_prob_0..k-1) para AUC multiclase post-hoc / trazabilidad.
    for c in range(n_classes):
        preds_df[f'y_prob_{c}'] = prob_full[:, c]
    y_true_arr = preds_df['y_true'].to_numpy()
    y_pred_arr = preds_df['y_pred'].to_numpy()

    test_acc = float((y_true_arr == y_pred_arr).mean())
    bal_acc = float(balanced_accuracy_score(y_true_arr, y_pred_arr))
    cm = confusion_matrix(y_true_arr, y_pred_arr, labels=list(range(n_classes)))
    # AUC: binario = ROC-AUC; multiclase = macro one-vs-rest. Requiere >=1 muestra de
    # cada clase en test; si no, queda nan. Política B5: el AUC se reporta SIEMPRE
    # junto a balanced_acc, nunca como métrica única (Hallazgo 6). La rama binaria es
    # idéntica a la anterior (prob_full[:,1] == y_prob_si) → reproduce microcalc.
    test_auc = float("nan")
    try:
        if n_classes == 2:
            if len(np.unique(y_true_arr)) == 2:
                test_auc = float(roc_auc_score(y_true_arr, prob_full[:, 1]))
        elif len(np.unique(y_true_arr)) == n_classes:
            test_auc = float(roc_auc_score(
                y_true_arr, prob_full, multi_class='ovr',
                average='macro', labels=list(range(n_classes))))
    except ValueError:
        test_auc = float("nan")

    test_metrics = {
        "test_auc": test_auc,
        "test_acc": test_acc,
        "balanced_acc": bal_acc,
        "confusion": cm.tolist(),  # binario [[TN,FP],[FN,TP]]; multiclase n×n (sklearn)
        "n_test": int(len(preds_df)),
    }
    return patient_results, test_metrics, preds_df


def main() -> int:
    args = parse_args()
    if args.exp_code is None:
        args.exp_code = f"{args.model_type}_{args.task}"  # dsmil_* (default) o clam_*
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
    val_loader = get_split_loader(val_split)
    test_loader = get_split_loader(test_split)

    # Snapshot inicial de pesos del aggregator (solo DSMIL — CLAM no tiene
    # dsmil_aggregator; para CLAM no aplica este diagnóstico).
    if args.model_type == "dsmil":
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

    # EarlyStopping (R6 §5: con stop_epoch=50 > max_epochs=30 nunca
    # triggea, pero save_checkpoint guarda el best por val_loss). El
    # ckpt vive bajo results_dir como s_<fold>_checkpoint.pt (patrón
    # CLAM: main.py:214-217).
    ckpt_path = str(results_dir / f"s_{args.fold}_checkpoint.pt")
    if args.early_stopping:
        if args.max_epochs <= args.stop_epoch:
            print(f"[WARN] R6: max_epochs={args.max_epochs} <= "
                  f"stop_epoch={args.stop_epoch} → early_stop nunca "
                  f"triggea (el loop corre completo). save_checkpoint "
                  f"sí guarda best por val_loss.")
        early_stopping = EarlyStopping(
            patience=args.patience, stop_epoch=args.stop_epoch, verbose=True
        )
    else:
        early_stopping = None

    log_path = results_dir / "metrics.jsonl"
    with open(log_path, "w") as logf:
        for epoch in range(args.max_epochs):
            train_metrics, _, _ = train_one_epoch(
                epoch, model, train_loader, optimizer, loss_fn,
                args.bag_weight, args.w_max, device, args.model_type,
            )
            should_stop, val_metrics = validate_one_epoch(
                epoch, model, val_loader, loss_fn, device,
                early_stopping=early_stopping, ckpt_path=ckpt_path,
            )
            metrics = {**train_metrics, **val_metrics}
            print(
                f"[EPOCH {epoch}] "
                f"train_loss={metrics.get('train_loss', float('nan')):.4f}  "
                f"clustering_loss={metrics.get('train_clustering_loss', float('nan')):.4f}  "
                f"max_loss={metrics.get('train_max_loss', float('nan')):.4f}  "
                f"|grad W_0|={metrics.get('grad_W0_mean', 0.0):.4f}  "
                f"|grad q|={metrics.get('grad_q_mean', 0.0):.4f}  "
                f"train_err={metrics.get('train_error', float('nan')):.4f}  "
                f"val_loss={metrics.get('val_loss', float('nan')):.4f}  "
                f"val_auc={metrics.get('val_auc', float('nan')):.4f}  "
                f"val_err={metrics.get('val_error', float('nan')):.4f}",
                flush=True,
            )
            logf.write(json.dumps(metrics) + "\n")
            logf.flush()
            if should_stop:
                print(f"[EARLY-STOP] triggered at epoch {epoch}")
                break

    # Snapshot final del aggregator (solo DSMIL; pre-load del best
    # checkpoint, para capturar el estado al cierre del training; el best
    # puede ser de un epoch anterior y eso se ve en el delta).
    if args.model_type == "dsmil":
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

    # Patrón CLAM (main.py:214-217): si early_stopping activado, cargar
    # best por val_loss (EXPLÍCITO — NO usar el modelo del último epoch).
    # Si no, guardar el del último epoch como fallback.
    if args.early_stopping:
        if os.path.isfile(ckpt_path):
            print(f"[INFO] cargando best checkpoint para val/test final: "
                  f"{ckpt_path}")
            model.load_state_dict(torch.load(ckpt_path, map_location=device))
        else:
            print(f"[WARN] {ckpt_path} no existe — val_loss nunca mejoró. "
                  f"Usando modelo del último epoch.")
    else:
        torch.save(model.state_dict(), ckpt_path)
        print(f"[INFO] sin --early_stopping: guardado modelo del último "
              f"epoch en {ckpt_path}")

    # Val final (sobre el best checkpoint, NO sobre el último epoch).
    _, val_final = validate_one_epoch(
        epoch=-1, model=model, loader=val_loader, loss_fn=loss_fn,
        device=device, early_stopping=None, ckpt_path=None,
    )
    print(f"[VAL FINAL] val_loss={val_final['val_loss']:.4f}  "
          f"val_auc={val_final['val_auc']:.4f}  "
          f"val_err={val_final['val_error']:.4f}  "
          f"n={val_final['val_processed']}")

    # Test final con métricas extendidas (balanced_acc + confusion).
    patient_results, test_metrics, preds_df = compute_test_metrics(
        model, test_loader, device,
    )
    print(f"[TEST FINAL] test_auc={test_metrics['test_auc']:.4f}  "
          f"test_acc={test_metrics['test_acc']:.4f}  "
          f"balanced_acc={test_metrics['balanced_acc']:.4f}  "
          f"n={test_metrics['n_test']}")
    print(f"[TEST FINAL] confusion (rows=true, cols=pred): "
          f"{test_metrics['confusion']}")

    # Volcados: summary.csv (formato CLAM), .pkl (patient_results),
    # test_metrics.json (extendido), test_predictions.csv (auditoría).
    summary_df = pd.DataFrame({
        'folds': [args.fold],
        'test_auc': [test_metrics['test_auc']],
        'val_auc': [val_final['val_auc']],
        'test_acc': [test_metrics['test_acc']],
        'val_acc': [1.0 - val_final['val_error']],
    })
    summary_path = results_dir / "summary.csv"
    summary_df.to_csv(summary_path, index=False)
    print(f"[INFO] summary.csv -> {summary_path}")

    pkl_path = results_dir / f"split_{args.fold}_results.pkl"
    with open(pkl_path, "wb") as f:
        pickle.dump(patient_results, f)
    print(f"[INFO] split_{args.fold}_results.pkl -> {pkl_path}")

    with open(results_dir / "test_metrics.json", "w") as f:
        json.dump(test_metrics, f, indent=2)
    preds_df.to_csv(results_dir / "test_predictions.csv", index=False)
    print(f"[INFO] test_metrics.json + test_predictions.csv -> {results_dir}")

    print(f"[DONE] train + val + test completado. Artefactos en {results_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
