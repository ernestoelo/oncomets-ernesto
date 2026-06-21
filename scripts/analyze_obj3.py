#!/usr/bin/env python
"""Análisis Obj3 B5 — mammoth keep_slots=True (+slot_dropout), paired k=5.

Lee test_metrics.json de 4 brazos por tarea:
  - clam   = CLAM baseline
  - ksf    = mammoth keep_slots=False (drop-in, Hallazgo 12)
  - kst    = mammoth keep_slots=True   (Brazo 1, Obj 3)
  - kst_sd = mammoth keep_slots=True + slot_dropout 0.1 (Brazo 2, Obj 3)

Tareas (job 4387 = invasion+tejido; job 4400 = carcinoma+cdis, extensión §8):
  - invasion  : 3-clase, n=2814 (eval sano, fold-a-fold)
  - tejido    : binaria balanceada (~58% pos), n=333
  - carcinoma : binaria desbalanceada (~21% pos), n=328
  - cdis      : binaria desbalanceada (~36% pos), n=328

Contrastes pareados (mismos splits k=5 → Δ por fold):
  - C1 (primario, within-mammoth): kst − ksf
  - C2 (vs CLAM):                  kst − clam
  - slot_dropout aislado:          kst_sd − kst
Reporta los 3 puntos KSF/B1/B2 (Obs 4.b reviewer) + gap de recall por clase
(diagnóstico decisivo, prereg §2: ante conflicto bal_acc↔gap manda el gap).

Política eval B5: balanced_acc Y AUC juntos + confusión + recall por clase con n.
Solo lectura + stdlib. No toca clam_environ ni inputs de ningún job.
"""
import glob
import json
import statistics as st

# (base_dir, run_name_template con {f}) por (tarea, brazo)
RUNS = {
    "invasion": {
        "clam":   ("results/obj2_mammoth/invasion_linfatica_vascular_pth",
                   "clam_invasion_linfatica_vascular_pth_f{f}_*_s1"),
        "ksf":    ("results/obj2_mammoth/invasion_linfatica_vascular_pth",
                   "clam_mammoth_invasion_linfatica_vascular_pth_f{f}_*_s1"),
        "kst":    ("results/obj3_mammoth_keepslots/invasion_linfatica_vascular_pth",
                   "kst_invasion_linfatica_vascular_pth_f{f}_*_s1"),
        "kst_sd": ("results/obj3_mammoth_keepslots/invasion_linfatica_vascular_pth",
                   "kst_sd_invasion_linfatica_vascular_pth_f{f}_*_s1"),
    },
    "tejido": {
        "clam":   ("results/obj6_mammoth_binarias_tejido_no_neoplasico",
                   "clam_tejido_no_neoplasico_f{f}_*_s1"),
        "ksf":    ("results/obj6_mammoth_binarias_tejido_no_neoplasico",
                   "clam_mammoth_tejido_no_neoplasico_f{f}_*_s1"),
        "kst":    ("results/obj3_mammoth_keepslots/microcalcificaciones_en_tejido_no_neoplasico_pth",
                   "kst_microcalcificaciones_en_tejido_no_neoplasico_pth_f{f}_*_s1"),
        "kst_sd": ("results/obj3_mammoth_keepslots/microcalcificaciones_en_tejido_no_neoplasico_pth",
                   "kst_sd_microcalcificaciones_en_tejido_no_neoplasico_pth_f{f}_*_s1"),
    },
    "carcinoma": {
        "clam":   ("results/obj6_mammoth_binarias_carcinoma_invasivo",
                   "clam_carcinoma_invasivo_f{f}_*_s1"),
        "ksf":    ("results/obj6_mammoth_binarias_carcinoma_invasivo",
                   "clam_mammoth_carcinoma_invasivo_f{f}_*_s1"),
        "kst":    ("results/obj3_mammoth_keepslots/microcalcificaciones_en_carcinoma_invasivo_pth",
                   "kst_microcalcificaciones_en_carcinoma_invasivo_pth_f{f}_*_s1"),
        "kst_sd": ("results/obj3_mammoth_keepslots/microcalcificaciones_en_carcinoma_invasivo_pth",
                   "kst_sd_microcalcificaciones_en_carcinoma_invasivo_pth_f{f}_*_s1"),
    },
    "cdis": {
        "clam":   ("results/obj6_mammoth_binarias_cdis",
                   "clam_cdis_f{f}_*_s1"),
        "ksf":    ("results/obj6_mammoth_binarias_cdis",
                   "clam_mammoth_cdis_f{f}_*_s1"),
        "kst":    ("results/obj3_mammoth_keepslots/microcalcificaciones_en_cdis_pth",
                   "kst_microcalcificaciones_en_cdis_pth_f{f}_*_s1"),
        "kst_sd": ("results/obj3_mammoth_keepslots/microcalcificaciones_en_cdis_pth",
                   "kst_sd_microcalcificaciones_en_cdis_pth_f{f}_*_s1"),
    },
}
CLASSES = {
    "invasion":  ["ausente", "no_identificado", "presente"],   # 0,1,2
    "tejido":    ["no", "si"],                                  # 0,1
    "carcinoma": ["no", "si"],
    "cdis":      ["no", "si"],
}
TASK_ORDER = ["invasion", "tejido", "carcinoma", "cdis"]
ARMS = ["clam", "ksf", "kst", "kst_sd"]


def load_metrics(task, arm, fold):
    base, tmpl = RUNS[task][arm]
    # globear el JSON directo: un dir de run existe antes de que test_metrics.json
    # se escriba (run en progreso) → solo matchear runs COMPLETADAS.
    fs = sorted(glob.glob(f"{base}/{tmpl.format(f=fold)}/test_metrics.json"))
    if not fs:
        return None
    with open(fs[0]) as fh:
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
            print(f"    {task:<9} {arm:<7} {n}/5{flag}")
    return done


def per_arm_table(task):
    nc = len(CLASSES[task])
    auc_label = "macro-OVR AUC" if nc == 3 else "ROC-AUC"
    print("=" * 92)
    print(f"[{task}] clases={CLASSES[task]}  trivial bAcc={1.0/nc:.3f}   (AUC = {auc_label})")
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
    print(f"  [{task}] confusión sumada (rows=true) + recall por clase  (gap de recall = diagnóstico):")
    cls = CLASSES[task]
    for a in ARMS:
        C, ok = confusion_sum(task, a)
        r = recalls(C)
        tag = "" if ok else "  (INCOMPLETO)"
        print(f"    {a:<7}{tag}")
        for i in range(len(cls)):
            print(f"        {cls[i]:<16} {C[i]}   recall={r[i]:.3f}")


def main():
    full = completeness()
    print()
    for task in TASK_ORDER:
        bacc, auc = per_arm_table(task)
        print("-" * 92)
        paired(task, bacc, auc, "kst", "ksf", "C1 (kst − ksf, within-mammoth, PRIMARIO)")
        paired(task, bacc, auc, "kst", "clam", "C2 (kst − CLAM)")
        paired(task, bacc, auc, "kst_sd", "kst", "slot_dropout aislado (kst_sd − kst)")
        confusion_block(task)
        print()
    if not full:
        print(">>> AVISO: faltan runs — el veredicto NO es definitivo hasta 5/5 en los 4 brazos × 4 tareas.")
    print("=" * 92)


if __name__ == "__main__":
    main()
