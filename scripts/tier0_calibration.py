#!/usr/bin/env python
"""tier0_calibration.py — Calibración post-hoc del operating-point (Tier 0).

Recalibra el operating-point de checkpoints CLAM ya entrenados **sin reentrenar y
sin GPU**. El bias/umbral por clase se elige **EN VAL** (inferencia CPU con
`s_<fold>_checkpoint.pt` sobre el split de val) y se **CONGELA a TEST** (probs del
`split_<fold>_results.pkl`, re-inferidas aquí y validadas contra el .pkl).

Guardrail duro ([[calibracion-tier0-pendiente-ejecutar]]): el operating-point se
elige SIEMPRE en val, NUNCA en test. El `test-oracle` (bias ajustado en test) se
reporta SOLO como upper-bound de factibilidad, JAMÁS como resultado.

Regla de eval B5: se reporta balanced_accuracy Y AUC juntos + recall minoritaria +
matriz de confusión + n/clase. Comparación PAIRED por fold vs argmax (operating-point
uniforme actual). El AUC es invariante a la calibración (recalibra el operating-point,
no el ranking) → se reporta una vez como contexto del headroom.

CPU-only, post-hoc, no toca training/modelo → regla 9 trivial, sin reviewer.
Uso:  CUDA_VISIBLE_DEVICES="" /home/sdonoso/miniconda3/envs/clam_latest/bin/python \
          scripts/tier0_calibration.py
"""
from __future__ import annotations

import os
os.environ["CUDA_VISIBLE_DEVICES"] = ""  # fuerza CPU (Tier 0 = sin GPU, sin sbatch)

import json
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from sklearn.metrics import balanced_accuracy_score, confusion_matrix, roc_auc_score

_CLAM_ENVIRON = "/media/administrador/Storage1/sdonoso/clam_environ"
_REPO = "/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto"
for _p in (_CLAM_ENVIRON, _REPO):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from dataset_modules.dataset_generic import Generic_MIL_Dataset  # noqa: E402
from utils.utils import get_split_loader  # noqa: E402
from models.model_clam import CLAM_MB  # noqa: E402
from topk.svm import SmoothTop1SVM  # noqa: E402

DATA_ROOT = f"{_CLAM_ENVIRON}/environ"
DEVICE = torch.device("cpu")
OUT_DIR = Path(_REPO) / "sprints/B6_sprint6/tier0_calibracion"

# --------------------------------------------------------------------------- #
# Task specs. label_dict = auto-label-dict alfabético (verificado == .pkl int labels).
# run_tmpl: dir del brazo CLAM baseline por fold (contiene s_<f>_checkpoint.pt + .pkl).
# --------------------------------------------------------------------------- #
TASKS = {
    "invasion_linfatica_vascular": dict(
        n_classes=3,
        csv=f"{_CLAM_ENVIRON}/environ/csv/dataset_invasion_linfovascular_label.csv",
        label_dict={"ausente": 0, "no_identificado": 1, "presente": 2},
        split_dir=f"{_REPO}/data/splits_kfold/invasion_linfatica_vascular_pth_100",
        run_tmpl=f"{_REPO}/results/obj2_mammoth/invasion_linfatica_vascular_pth/"
                 "clam_invasion_linfatica_vascular_pth_f{f}_20260604_0952_s1",
    ),
    "cdis_necrosis_2clases": dict(
        n_classes=2,
        csv=f"{_REPO}/data/csv_new_tasks/dataset_cdis_necrosis_2clases_label.csv",
        label_dict={"no": 0, "si": 1},
        split_dir=f"{_REPO}/data/splits_kfold/cdis_necrosis_2clases_pth_100",
        run_tmpl=f"{_REPO}/results/pathpt_etapa1/necrosis/"
                 "clam_cdis_necrosis_2clases_pth_f{f}_20260610_2312_s1",
    ),
    "grado_mitotic_3clases": dict(
        n_classes=3,
        csv=f"{_REPO}/data/csv_new_tasks/dataset_grado_mitotic_3clases_label.csv",
        label_dict={"score_1": 0, "score_2": 1, "score_3": 2},
        split_dir=f"{_REPO}/data/splits_kfold/grado_mitotic_3clases_pth_100",
        run_tmpl=f"{_REPO}/results/pathpt_etapa1/mitotic/"
                 "clam_grado_mitotic_3clases_pth_f{f}_20260611_1730_s1",
    ),
}

N_FOLDS = 5
EPS = 1e-12


def build_model(n_classes: int) -> CLAM_MB:
    """CLAM_MB idéntico al build del harness (train_dsmil.build_model, brazo 'clam')."""
    inst = SmoothTop1SVM(n_classes=2)  # en CPU; no se usa en el forward de eval
    model = CLAM_MB(
        gate=True, size_arg="small", dropout=0.25, k_sample=8,
        n_classes=n_classes, subtyping=False,
        instance_loss_fn=inst, embed_dim=512,
    )
    return model.to(DEVICE)


@torch.inference_mode()
def infer(model: CLAM_MB, loader) -> tuple[np.ndarray, np.ndarray]:
    """Forward CLAM_MB sobre un split → (probs [N,K], y [N]). Réplica de
    train_dsmil.compute_test_metrics (model(data) sin label ni instance_eval)."""
    model.eval()
    probs, ys = [], []
    for batch in loader:
        if batch is None:
            continue
        data, label = batch
        data = data.to(DEVICE)
        _, Y_prob, _, _, _ = model(data)
        probs.append(Y_prob.cpu().numpy()[0])
        ys.append(int(label.item()))
    return np.asarray(probs), np.asarray(ys)


def _pred(probs: np.ndarray, bias: np.ndarray) -> np.ndarray:
    """Regla de decisión con operating-point recalibrado:
    pred = argmax_c ( log p_c + bias_c ). bias=0 ⇒ argmax estándar."""
    return np.argmax(np.log(probs + EPS) + bias, axis=1)


def fit_bias(probs: np.ndarray, y: np.ndarray, n_classes: int) -> np.ndarray:
    """Coordinate-ascent del bias por clase (b[0]=0 ancla) que MAXIMIZA la
    balanced_accuracy sobre (probs, y). Determinista. Binario ⇒ sweep de un umbral."""
    grid = np.linspace(-8.0, 8.0, 81)
    bias = np.zeros(n_classes)

    def score(b):
        return balanced_accuracy_score(y, _pred(probs, b))

    best_overall = score(bias)
    for _ in range(6):  # pasadas de coordinate ascent
        improved = False
        for c in range(1, n_classes):
            best_g, best_s = bias[c], score(bias)
            for g in grid:
                b = bias.copy(); b[c] = g
                s = score(b)
                if s > best_s + 1e-9:
                    best_s, best_g = s, g
            if best_g != bias[c]:
                bias[c] = best_g
                improved = True
        cur = score(bias)
        if cur <= best_overall + 1e-9 and not improved:
            break
        best_overall = cur
    return bias


def minority_recall(y: np.ndarray, pred: np.ndarray, minority_cls: int) -> float:
    mask = y == minority_cls
    if mask.sum() == 0:
        return float("nan")
    return float((pred[mask] == minority_cls).mean())


def auc_of(y: np.ndarray, probs: np.ndarray, n_classes: int) -> float:
    try:
        if n_classes == 2:
            if len(np.unique(y)) == 2:
                return float(roc_auc_score(y, probs[:, 1]))
        elif len(np.unique(y)) == n_classes:
            return float(roc_auc_score(y, probs, multi_class="ovr",
                                       average="macro", labels=list(range(n_classes))))
    except ValueError:
        pass
    return float("nan")


def run_task(name: str, spec: dict) -> dict:
    n_classes = spec["n_classes"]
    print(f"\n{'='*74}\nTASK: {name}  (n_classes={n_classes})\n{'='*74}")
    dataset = Generic_MIL_Dataset(
        csv_path=spec["csv"],
        data_dir=os.path.join(DATA_ROOT, "features"),
        shuffle=False, seed=1, print_info=False,
        label_dict=spec["label_dict"], patient_strat=False, ignore=[],
    )

    fold_rows = []
    cm_base_tot = np.zeros((n_classes, n_classes), dtype=int)
    cm_cal_tot = np.zeros((n_classes, n_classes), dtype=int)

    for f in range(N_FOLDS):
        run_dir = Path(spec["run_tmpl"].format(f=f))
        ckpt = run_dir / f"s_{f}_checkpoint.pt"
        pkl = run_dir / f"split_{f}_results.pkl"
        split_csv = os.path.join(spec["split_dir"], f"splits_{f}.csv")
        assert ckpt.is_file(), f"falta checkpoint {ckpt}"
        assert pkl.is_file(), f"falta pkl {pkl}"

        train_s, val_s, test_s = dataset.return_splits(from_id=False, csv_path=split_csv)
        model = build_model(n_classes)
        model.load_state_dict(torch.load(ckpt, map_location=DEVICE))

        # Evaluación sobre features ACTUALES: val y test re-inferidos aquí comparten
        # procedencia (clave — el dir features/pt_files es live y algunas TCGA se
        # re-extrajeron el 26-27 jun, posterior a estos runs). Así el bias elegido en
        # val y el test al que se congela ven la MISMA versión de features → paired limpio.
        val_probs, val_y = infer(model, get_split_loader(val_s))
        test_probs, test_y = infer(model, get_split_loader(test_s))

        # --- transparencia: baseline congelado del .pkl histórico + drift de features ---
        d = pickle.load(open(pkl, "rb"))
        frozen_bal = balanced_accuracy_score(
            [v["label"] for v in d.values()],
            [int(np.argmax(v["prob"][0])) for v in d.values()],
        )
        sids_test = list(test_s.slide_data["slide_id"])
        n_drift = sum(
            int(np.argmax(test_probs[i]) != np.argmax(d[str(s)]["prob"][0]))
            for i, s in enumerate(sids_test) if str(s) in d
        )

        # minoritaria = clase con menor soporte en TEST
        supports = np.bincount(test_y, minlength=n_classes)
        minority = int(np.argmin(supports))

        # baseline (argmax) frozen-a-test
        base_pred = np.argmax(test_probs, axis=1)
        base_bal = balanced_accuracy_score(test_y, base_pred)
        base_rec = minority_recall(test_y, base_pred, minority)

        # calibrado: bias ajustado EN VAL → congelado a TEST
        bias = fit_bias(val_probs, val_y, n_classes)
        cal_pred = _pred(test_probs, bias)
        cal_bal = balanced_accuracy_score(test_y, cal_pred)
        cal_rec = minority_recall(test_y, cal_pred, minority)

        # oracle (bias en TEST) = SOLO upper-bound de factibilidad, NUNCA resultado
        bias_or = fit_bias(test_probs, test_y, n_classes)
        or_bal = balanced_accuracy_score(test_y, _pred(test_probs, bias_or))

        test_auc = auc_of(test_y, test_probs, n_classes)

        cm_base_tot += confusion_matrix(test_y, base_pred, labels=list(range(n_classes)))
        cm_cal_tot += confusion_matrix(test_y, cal_pred, labels=list(range(n_classes)))

        fold_rows.append(dict(
            fold=f, n_test=int(len(test_y)), minority=minority,
            support=supports.tolist(), test_auc=test_auc,
            base_bal=base_bal, cal_bal=cal_bal, oracle_bal=or_bal,
            delta=cal_bal - base_bal,
            base_minrec=base_rec, cal_minrec=cal_rec,
            bias=[round(float(x), 3) for x in bias],
            frozen_bal=float(frozen_bal), n_drift=int(n_drift),
        ))
        print(f"  fold {f}: n_test={len(test_y):3d} minoria=cls{minority}(n={supports[minority]:2d}) "
              f"AUC={test_auc:.3f} | bal base={base_bal:.3f} cal={cal_bal:.3f} "
              f"(Δ={cal_bal-base_bal:+.3f}) oracle={or_bal:.3f} | "
              f"minrec {base_rec:.2f}→{cal_rec:.2f} | drift={n_drift} slides (.pkl bal={frozen_bal:.3f})")

    df = pd.DataFrame(fold_rows)
    agg = dict(
        task=name, n_classes=n_classes,
        auc_mean=float(df.test_auc.mean()), auc_std=float(df.test_auc.std(ddof=0)),
        base_mean=float(df.base_bal.mean()), base_std=float(df.base_bal.std(ddof=0)),
        cal_mean=float(df.cal_bal.mean()), cal_std=float(df.cal_bal.std(ddof=0)),
        oracle_mean=float(df.oracle_bal.mean()),
        delta_mean=float(df.delta.mean()), delta_std=float(df.delta.std(ddof=0)),
        delta_signs_pos=int((df.delta > 1e-9).sum()),
        delta_signs_neg=int((df.delta < -1e-9).sum()),
        base_minrec_mean=float(df.base_minrec.mean()),
        cal_minrec_mean=float(df.cal_minrec.mean()),
        cm_base=cm_base_tot.tolist(), cm_cal=cm_cal_tot.tolist(),
        frozen_mean=float(df.frozen_bal.mean()), n_drift_total=int(df.n_drift.sum()),
    )
    print(f"\n  AGREGADO {name}:")
    print(f"    AUC test              = {agg['auc_mean']:.3f} ± {agg['auc_std']:.3f}")
    print(f"    bal_acc base (argmax) = {agg['base_mean']:.3f} ± {agg['base_std']:.3f}")
    print(f"    bal_acc calibrado     = {agg['cal_mean']:.3f} ± {agg['cal_std']:.3f}")
    print(f"    Δ pareado (cal-base)  = {agg['delta_mean']:+.3f} ± {agg['delta_std']:.3f}  "
          f"(signos: +{agg['delta_signs_pos']} / -{agg['delta_signs_neg']} de {N_FOLDS})")
    print(f"    oracle (upper-bound)  = {agg['oracle_mean']:.3f}  [factibilidad, NO resultado]")
    print(f"    recall minoritaria    = {agg['base_minrec_mean']:.2f} → {agg['cal_minrec_mean']:.2f}")
    print(f"    confusión sumada base = {agg['cm_base']}")
    print(f"    confusión sumada cal  = {agg['cm_cal']}")
    print(f"    baseline .pkl congelado (histórico) = {agg['frozen_mean']:.3f}  "
          f"[drift total {agg['n_drift_total']} slides re-extraídas, features actuales usadas]")
    return dict(agg=agg, folds=fold_rows)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    results = {}
    for name, spec in TASKS.items():
        results[name] = run_task(name, spec)
    out = OUT_DIR / "tier0_results.json"
    json.dump(results, open(out, "w"), indent=2)
    print(f"\n[OK] resultados → {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
