#!/usr/bin/env python
"""Análisis Obj2 B5 — Δ pareado CLAM vs CLAM+mammoth en patrón arquitectónico.

Lee results/obj2_mammoth/<task>/<arm>_<task>_f<0..4>_*_s1/{test_metrics.json,test_predictions.csv}
y reporta, por tarea, según política eval B5 (balanced_acc + AUC + confusión + n,
sin gate, lectura cualitativa por consistencia de signo):

- Tareas "sanas" (cribiforme, solido, ~25-40 pos/fold): Δ pareado FOLD A FOLD,
  media ± std POBLACIONAL (ddof=0, convención Obj1), signo, confusión sumada.
- Tareas "ciegas" (micropapilar, papilar, 3 pos/test): POOLED — se agregan las
  predicciones de los 5 folds; sens/spec/AUC global por brazo (régimen
  estadísticamente ciego, no se lee fold a fold). Ver README §lectura especial.

Solo lectura + stdlib. No toca clam_environ ni el working-tree del job.
"""
import csv
import glob
import json
import math
import statistics as st

BASE = "results/obj2_mammoth"
ARMS = ["clam", "clam_mammoth"]
HEALTHY = ["cdis_patron_cribiforme_pth", "cdis_patron_solido_pth"]
BLIND = ["cdis_patron_micropapilar_pth", "cdis_patron_papilar_pth"]


def rundir(task, arm, fold):
    fs = glob.glob(f"{BASE}/{task}/{arm}_{task}_f{fold}_*_s1")
    return fs[0] if fs else None


def load_metrics(task, arm, fold):
    d = rundir(task, arm, fold)
    if not d:
        return None
    with open(f"{d}/test_metrics.json") as fh:
        return json.load(fh)


def load_preds(task, arm, fold):
    """Devuelve lista de (y_true:int, y_prob_si:float)."""
    d = rundir(task, arm, fold)
    rows = []
    with open(f"{d}/test_predictions.csv") as fh:
        for r in csv.DictReader(fh):
            rows.append((int(r["y_true"]), float(r["y_prob_si"])))
    return rows


def auc_rank(pairs):
    """ROC-AUC tie-aware (Mann-Whitney U) sobre lista de (y_true, score)."""
    pos = [s for y, s in pairs if y == 1]
    neg = [s for y, s in pairs if y == 0]
    if not pos or not neg:
        return float("nan")
    allp = sorted([(s, 0) for s in neg] + [(s, 1) for s in pos])
    # ranks promediados para empates
    ranks = [0.0] * len(allp)
    i = 0
    while i < len(allp):
        j = i
        while j < len(allp) and allp[j][0] == allp[i][0]:
            j += 1
        avg = (i + 1 + j) / 2.0
        for k in range(i, j):
            ranks[k] = avg
        i = j
    rsum_pos = sum(ranks[k] for k in range(len(allp)) if allp[k][1] == 1)
    n1, n0 = len(pos), len(neg)
    u = rsum_pos - n1 * (n1 + 1) / 2.0
    return u / (n1 * n0)


def fmt_pm(xs):
    return f"{st.mean(xs):+.3f} ± {st.pstdev(xs):.3f}"


def confusion_sum(task, arm):
    C = [[0, 0], [0, 0]]
    for f in range(5):
        m = load_metrics(task, arm, f)
        for i in range(2):
            for j in range(2):
                C[i][j] += m["confusion"][i][j]
    return C


def recalls(C):
    tn, fp, fn, tp = C[0][0], C[0][1], C[1][0], C[1][1]
    rno = tn / (tn + fp) if (tn + fp) else float("nan")
    rsi = tp / (tp + fn) if (tp + fn) else float("nan")
    return rno, rsi


def analyze_healthy(task):
    print("=" * 80)
    print(f"[SANA · fold-a-fold] {task}")
    db, da = [], []
    print(f"{'fold':<5}{'clam_bAcc':>10}{'mam_bAcc':>10}{'ΔbAcc':>9}"
          f"{'clam_AUC':>10}{'mam_AUC':>9}{'ΔAUC':>9}{'n':>5}")
    bacc = {a: [] for a in ARMS}
    auc = {a: [] for a in ARMS}
    for f in range(5):
        c, m = load_metrics(task, "clam", f), load_metrics(task, "clam_mammoth", f)
        bacc["clam"].append(c["balanced_acc"]); bacc["clam_mammoth"].append(m["balanced_acc"])
        auc["clam"].append(c["test_auc"]); auc["clam_mammoth"].append(m["test_auc"])
        dbacc = m["balanced_acc"] - c["balanced_acc"]
        dauc = m["test_auc"] - c["test_auc"]
        db.append(dbacc); da.append(dauc)
        print(f"{f:<5}{c['balanced_acc']:>10.3f}{m['balanced_acc']:>10.3f}{dbacc:>+9.3f}"
              f"{c['test_auc']:>10.3f}{m['test_auc']:>9.3f}{dauc:>+9.3f}{c['n_test']:>5}")
    print(f"  CLAM   bAcc {fmt_pm(bacc['clam'])} | AUC {fmt_pm(auc['clam'])}")
    print(f"  +Mamm  bAcc {fmt_pm(bacc['clam_mammoth'])} | AUC {fmt_pm(auc['clam_mammoth'])}")
    print(f"  Δ bAcc = {fmt_pm(db)}   signo {sum(x>0 for x in db)}+/{sum(x<0 for x in db)}-   "
          f"folds={[round(x,3) for x in db]}")
    print(f"  Δ AUC  = {fmt_pm(da)}   signo {sum(x>0 for x in da)}+/{sum(x<0 for x in da)}-")
    for a in ARMS:
        C = confusion_sum(task, a); rno, rsi = recalls(C)
        print(f"  conf {a:<12} [[TN,FP],[FN,TP]]={C}  recall_no={rno:.2f} recall_si={rsi:.2f}")


def analyze_blind(task):
    print("=" * 80)
    print(f"[CIEGA · pooled 5 folds] {task}")
    for a in ARMS:
        pooled = []
        for f in range(5):
            pooled += load_preds(task, a, f)
        tp = sum(1 for y, s in pooled if y == 1 and s >= 0.5)
        fn = sum(1 for y, s in pooled if y == 1 and s < 0.5)
        fp = sum(1 for y, s in pooled if y == 0 and s >= 0.5)
        tn = sum(1 for y, s in pooled if y == 0 and s < 0.5)
        npos = tp + fn
        sens = tp / npos if npos else float("nan")
        spec = tn / (tn + fp) if (tn + fp) else float("nan")
        bacc = (sens + spec) / 2.0
        a_auc = auc_rank(pooled)
        print(f"  {a:<12} pooled n={len(pooled)} pos={npos}  "
              f"conf [[TN,FP],[FN,TP]]=[[{tn},{fp}],[{fn},{tp}]]  "
              f"sens={sens:.3f} spec={spec:.3f} bAcc(pool)={bacc:.3f} AUC(pool)={a_auc:.3f}")


if __name__ == "__main__":
    for t in HEALTHY:
        analyze_healthy(t)
    for t in BLIND:
        analyze_blind(t)
    print("=" * 80)
