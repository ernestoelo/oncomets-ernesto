#!/usr/bin/env python
"""Análisis loss-desbalance B5 (Eje C1) — CLAM_MB + {focal, class_balanced} vs CLAM_MB + CE, paired k=5.

Lee test_metrics.json de 3 brazos por tarea:
  - ce    = CLAM baseline (bag loss CE, en disco; NO se re-corre)
  - focal = CLAM + --bag_loss focal (γ=2.0, sin α)
  - cb    = CLAM + --bag_loss class_balanced (Cui 2019, β=0.9999)

Tareas (job 4463, GROUP=binarias; mismos splits/seed que los baselines CLAM+CE):
  - carcinoma : microcalc en carcinoma invasivo, binaria, n=328, ~21% pos (`si` minoritaria)
  - cdis      : microcalc en cdis,              binaria, n=328, ~36% pos (`si` minoritaria)
  - tejido    : microcalc en tejido no neopl.,  binaria, n=328, ~58% pos (`no` minoritaria, control)
(invasión 3-clase en pausa — se agrega si se lanza GROUP=invasion.)

Contrastes pareados (mismos splits k=5 → Δ por fold):
  - C_focal = focal − ce   (focusing por confianza)
  - C_cb    = cb    − ce   (re-ponderación por número efectivo; apilada sobre weighted_sample)

Desempate mecanístico (prereg §2): ante conflicto bal_acc↔recall manda el GAP de recall.
Una palanca genuina sube recall de la minoritaria Y bal_acc neta > CE. Si sube recall
pero hunde la mayoritaria y bal_acc neta ≤ CE → re-balanceo (H_reg), no palanca.

Política eval B5: balanced_acc Y AUC juntos + confusión + recall por clase con n.
Solo lectura + stdlib. No toca clam_environ ni inputs de ningún job.
"""
import glob
import json
import statistics as st

# (base_dir, run_name_template con {f}) por (tarea, brazo)
RUNS = {
    "carcinoma": {
        "ce":    ("results/obj6_mammoth_binarias_carcinoma_invasivo",
                  "clam_carcinoma_invasivo_f{f}_*_s1"),
        "focal": ("results/loss_desbalance/microcalcificaciones_en_carcinoma_invasivo_pth",
                  "focal_microcalcificaciones_en_carcinoma_invasivo_pth_f{f}_*_s1"),
        "cb":    ("results/loss_desbalance/microcalcificaciones_en_carcinoma_invasivo_pth",
                  "cb_microcalcificaciones_en_carcinoma_invasivo_pth_f{f}_*_s1"),
    },
    "cdis": {
        "ce":    ("results/obj6_mammoth_binarias_cdis",
                  "clam_cdis_f{f}_*_s1"),
        "focal": ("results/loss_desbalance/microcalcificaciones_en_cdis_pth",
                  "focal_microcalcificaciones_en_cdis_pth_f{f}_*_s1"),
        "cb":    ("results/loss_desbalance/microcalcificaciones_en_cdis_pth",
                  "cb_microcalcificaciones_en_cdis_pth_f{f}_*_s1"),
    },
    "tejido": {
        "ce":    ("results/obj6_mammoth_binarias_tejido_no_neoplasico",
                  "clam_tejido_no_neoplasico_f{f}_*_s1"),
        "focal": ("results/loss_desbalance/microcalcificaciones_en_tejido_no_neoplasico_pth",
                  "focal_microcalcificaciones_en_tejido_no_neoplasico_pth_f{f}_*_s1"),
        "cb":    ("results/loss_desbalance/microcalcificaciones_en_tejido_no_neoplasico_pth",
                  "cb_microcalcificaciones_en_tejido_no_neoplasico_pth_f{f}_*_s1"),
    },
}
CLASSES = {
    "carcinoma": ["no", "si"],   # 0,1 ; minoritaria = si
    "cdis":      ["no", "si"],   # minoritaria = si
    "tejido":    ["no", "si"],   # minoritaria = no (pos=si=58%)
}
# clase minoritaria por tarea (para leer el gap de recall sin ambigüedad)
MINORITY = {"carcinoma": "si", "cdis": "si", "tejido": "no"}
TASK_ORDER = ["carcinoma", "cdis", "tejido"]
ARMS = ["ce", "focal", "cb"]


def load_metrics(task, arm, fold):
    base, tmpl = RUNS[task][arm]
    # globear el JSON directo: un dir de run existe antes de que test_metrics.json
    # se escriba (run en progreso) → solo matchear runs COMPLETADAS.
    fs = sorted(glob.glob(f"{base}/{tmpl.format(f=fold)}/test_metrics.json"))
    if not fs:
        return None
    # fs[-1] = run de timestamp más reciente (YYYYMMDD_HHMM ordena lexicográfico):
    # ante un re-run del mismo brazo/fold gana el último (ej. cb re-corrido tras el
    # fix del bug no-op). Los runs buggy del 4463 ya están segregados en
    # results/loss_desbalance/_buggy_noop_cb_4463/ (fuera de este glob).
    with open(fs[-1]) as fh:
        return json.load(fh)


def fmt_pm(xs):
    return f"{st.mean(xs):+.3f} ± {st.pstdev(xs):.3f}" if xs else "n/a"


def confusion_sum(task, arm):
    nc = len(CLASSES[task])
    C = [[0] * nc for _ in range(nc)]
    ok = True
    for f in range(5):
        m = load_metrics(task, arm, f)
        if m is None:
            ok = False
            continue
        for i in range(nc):
            for j in range(nc):
                C[i][j] += m["confusion"][i][j]
    return C, ok


def recalls(C):
    return [C[i][i] / sum(C[i]) if sum(C[i]) else float("nan") for i in range(len(C))]


def completeness():
    print("[completeness] runs encontradas por (tarea, brazo):")
    done = True
    for task in TASK_ORDER:
        for arm in ARMS:
            n = sum(load_metrics(task, arm, f) is not None for f in range(5))
            flag = "" if n == 5 else "  <-- INCOMPLETO"
            if n < 5:
                done = False
            print(f"    {task:<9} {arm:<6} {n}/5{flag}")
    return done


def per_arm_table(task):
    nc = len(CLASSES[task])
    print("=" * 92)
    print(f"[{task}] clases={CLASSES[task]}  minoritaria='{MINORITY[task]}'  "
          f"trivial bAcc={1.0/nc:.3f}   (AUC = ROC)")
    print("=" * 92)
    bacc = {a: [] for a in ARMS}
    auc = {a: [] for a in ARMS}
    for a in ARMS:
        for f in range(5):
            m = load_metrics(task, a, f)
            if m is None:
                bacc[a].append(float("nan")); auc[a].append(float("nan"))
            else:
                bacc[a].append(m["balanced_acc"]); auc[a].append(m["test_auc"])
    print(f"{'arm':<8}" + "".join(f"{'f'+str(f):>9}" for f in range(5)) + f"{'mean±std':>18}")
    for a in ARMS:
        row = "".join(f"{x:>9.3f}" for x in bacc[a])
        print(f"{a:<8}{row}{fmt_pm([x for x in bacc[a] if x == x]):>18}   bAcc")
    for a in ARMS:
        row = "".join(f"{x:>9.3f}" for x in auc[a])
        print(f"{a:<8}{row}{fmt_pm([x for x in auc[a] if x == x]):>18}   AUC")
    return bacc, auc


def paired(task, bacc, auc, hi, lo, label):
    """Δ pareado hi − lo, fold a fold (bAcc y AUC). Salta folds con nan."""
    db = [bacc[hi][f] - bacc[lo][f] for f in range(5)
          if bacc[hi][f] == bacc[hi][f] and bacc[lo][f] == bacc[lo][f]]
    da = [auc[hi][f] - auc[lo][f] for f in range(5)
          if auc[hi][f] == auc[hi][f] and auc[lo][f] == auc[lo][f]]
    print(f"  Δ {label}:")
    print(f"     Δ bAcc = {fmt_pm(db)}   signo {sum(x>0 for x in db)}+/{sum(x<0 for x in db)}-   "
          f"folds={[round(x,3) for x in db]}")
    print(f"     Δ AUC  = {fmt_pm(da)}   signo {sum(x>0 for x in da)}+/{sum(x<0 for x in da)}-   "
          f"folds={[round(x,3) for x in da]}")


def confusion_block(task):
    print("-" * 92)
    print(f"  [{task}] confusión pooled (rows=true) + recall por clase  (gap de recall = diagnóstico):")
    cls = CLASSES[task]
    for a in ARMS:
        C, ok = confusion_sum(task, a)
        r = recalls(C)
        tag = "" if ok else "  (INCOMPLETO)"
        print(f"    {a:<6}{tag}")
        for i in range(len(cls)):
            star = "  <-- minoritaria" if cls[i] == MINORITY[task] else ""
            print(f"        {cls[i]:<6} {C[i]}   recall={r[i]:.3f}{star}")


def main():
    full = completeness()
    print()
    for task in TASK_ORDER:
        bacc, auc = per_arm_table(task)
        print("-" * 92)
        paired(task, bacc, auc, "focal", "ce", "C_focal (focal − CE)")
        paired(task, bacc, auc, "cb", "ce", "C_cb (class_balanced − CE)")
        confusion_block(task)
        print()
    if not full:
        print(">>> AVISO: faltan runs — el veredicto NO es definitivo hasta 5/5 en los 3 brazos × 3 tareas.")
    print("=" * 92)


if __name__ == "__main__":
    main()
