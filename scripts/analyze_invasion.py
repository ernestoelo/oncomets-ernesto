#!/usr/bin/env python
"""Análisis invasión linfática (Obj2 B5, 2ª ola) — Δ pareado CLAM vs CLAM+mammoth, 3 clases.

Lee results/obj2_mammoth/invasion_linfatica_vascular_pth/<arm>_<task>_f<0..4>_*_s1/test_metrics.json
y reporta, según política eval B5 (balanced_acc + macro-OVR AUC + confusión 3×3 + n,
sin gate, lectura cualitativa por consistencia de signo):

- Δ pareado FOLD A FOLD (régimen SANO: cada clase n≥36/test → NO pooled, a diferencia
  de micropapilar/papilar), media ± std POBLACIONAL (ddof=0, convención Obj1/patrón).
- Confusión 3×3 sumada por brazo + recall por clase (diagonal/fila) → vigila el colapso
  a `no_identificado` (mayoritaria 70%), el modo de fallo pre-registrado.

Nota grad-sanity: `|grad W_0|`/`|grad q|` del log salen 0.0 para clam_mammoth porque el
grad-logging está gated a `model_type=="dsmil"` (train_dsmil.py:255,271). NO indica mammoth
desconectado; el engagement se confirma porque los resultados DIFIEREN entre brazos + test CPU.

Solo lectura + stdlib. No toca clam_environ ni inputs de ningún job.
"""
import glob
import json
import statistics as st

BASE = "results/obj2_mammoth"
TASK = "invasion_linfatica_vascular_pth"
ARMS = ["clam", "clam_mammoth"]
CLASSES = ["ausente", "no_identificado", "presente"]  # 0, 1, 2


def load_metrics(arm, fold):
    fs = glob.glob(f"{BASE}/{TASK}/{arm}_{TASK}_f{fold}_*_s1")
    with open(f"{fs[0]}/test_metrics.json") as fh:
        return json.load(fh)


def fmt_pm(xs):
    return f"{st.mean(xs):+.3f} ± {st.pstdev(xs):.3f}"


def confusion_sum(arm):
    C = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    for f in range(5):
        m = load_metrics(arm, f)
        for i in range(3):
            for j in range(3):
                C[i][j] += m["confusion"][i][j]
    return C


def recalls(C):
    """recall por clase = diagonal / suma de la fila (true)."""
    return [C[i][i] / sum(C[i]) if sum(C[i]) else float("nan") for i in range(3)]


def main():
    print("=" * 84)
    print(f"[3-CLASE · fold-a-fold] {TASK}   clases={CLASSES}  trivial bAcc=0.333")
    print("=" * 84)
    bacc = {a: [] for a in ARMS}
    auc = {a: [] for a in ARMS}
    db, da = [], []
    hdr = (f"{'fold':<5}{'clam_bAcc':>10}{'mam_bAcc':>10}{'ΔbAcc':>9}"
           f"{'clam_AUC':>10}{'mam_AUC':>9}{'ΔAUC':>9}{'n':>5}")
    print(hdr)
    for f in range(5):
        c, m = load_metrics("clam", f), load_metrics("clam_mammoth", f)
        bacc["clam"].append(c["balanced_acc"]); bacc["clam_mammoth"].append(m["balanced_acc"])
        auc["clam"].append(c["test_auc"]); auc["clam_mammoth"].append(m["test_auc"])
        dbacc = m["balanced_acc"] - c["balanced_acc"]
        dauc = m["test_auc"] - c["test_auc"]
        db.append(dbacc); da.append(dauc)
        print(f"{f:<5}{c['balanced_acc']:>10.3f}{m['balanced_acc']:>10.3f}{dbacc:>+9.3f}"
              f"{c['test_auc']:>10.3f}{m['test_auc']:>9.3f}{dauc:>+9.3f}{c['n_test']:>5}")
    print("-" * 84)
    print(f"  CLAM   bAcc {fmt_pm(bacc['clam'])} | macro-OVR AUC {fmt_pm(auc['clam'])}")
    print(f"  +Mamm  bAcc {fmt_pm(bacc['clam_mammoth'])} | macro-OVR AUC {fmt_pm(auc['clam_mammoth'])}")
    print(f"  Δ bAcc = {fmt_pm(db)}   signo {sum(x>0 for x in db)}+/{sum(x<0 for x in db)}-   "
          f"folds={[round(x, 3) for x in db]}")
    print(f"  Δ AUC  = {fmt_pm(da)}   signo {sum(x>0 for x in da)}+/{sum(x<0 for x in da)}-   "
          f"folds={[round(x, 3) for x in da]}")
    print("-" * 84)
    for a in ARMS:
        C = confusion_sum(a); r = recalls(C)
        print(f"  conf {a:<12} (rows=true {CLASSES}):")
        for i in range(3):
            print(f"      {CLASSES[i]:<16} {C[i]}   recall={r[i]:.3f}")
    # vigilancia colapso a mayoritaria: masa predicha en col 'no_identificado'
    for a in ARMS:
        C = confusion_sum(a)
        pred_noid = sum(C[i][1] for i in range(3))
        print(f"  [colapso] {a:<12} pred=no_identificado en {pred_noid}/{sum(sum(r) for r in C)} casos")
    print("=" * 84)


if __name__ == "__main__":
    main()
