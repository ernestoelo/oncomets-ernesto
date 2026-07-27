"""q1_slots_escalado.py — B8 encargo 1: escalar la medición de slots ocupados.

Benjamín, en la reunión del 24-jul-2026: los 158.7 slots efectivos de 300 se midieron
sobre 7 láminas y con ese n no generalizan al conjunto de la tarea. Este script mide lo
mismo sobre **todas las láminas de test de los 5 folds de las 3 tareas** del job 4589
(tipo histológico 3 clases, CDIS presente, invasión linfovascular), o sea 1858 pares
(tarea, fold, lámina) sobre 1176 láminas únicas.

Qué mide, idéntico a lo que respondió la Q1 del B7 (`answer_q1_expertos_slots.py`):

  * «peso por slot» = `combine_weights`, la 2ª softmax sobre los E·S=300 slots
    (`mammoth.py:411`). NO es el top-k de parches por experto.
  * «uso por experto» = `dispatch_weights` normalizado por parche y promediado sobre
    (H, S) y sobre los parches, igual que `mammoth_interpretability.compute_expert_scores`.
  * **número efectivo** = exp(entropía de la distribución de pesos). Todos los slots
    reciben peso > 0 (es una softmax), así que contar «los que reciben algo» daría
    siempre 300.
  * **cota del uniforme** = 1/300: cuántos slots la superan y qué masa concentran.

Diferencias con `mammoth_interpretability.py`, que es de donde se reusa el modelo:

  * **Sin openslide y sin matplotlib.** La medición sale entera del h5 (features y coords
    viven en el mismo archivo); la WSI sólo hacía falta para dibujar. Eso es lo que saca
    la restricción que limitó el B7 a 7 láminas TCGA con `.svs` disponible.
  * **Streaming por chunks de parches**, porque `dispatch_weights = softmax(logits, dim=n)`
    normaliza SOBRE LOS PARCHES: no es separable por chunk. Se resuelve con dos pasadas,
    la primera acumulando el logsumexp sobre n de forma incremental (max online) y la
    segunda aplicando el denominador global. El resultado es exacto, no aproximado, y
    `--self-test` lo verifica contra la implementación original del B7.

Etapa 0: CPU, post-hoc, inferencia sobre checkpoints congelados. NO toca modelo ni
training, así que la regla 9 no aplica (igual que todo el trabajo post-hoc del B7).

Reanudable (workaround J): cada fold escribe `laminas.csv` fila a fila y se marca
terminado con `meta.json`, que es el artefacto FINAL. Un fold sin `meta.json` se retoma
desde la última fila íntegra del CSV.

NUNCA correr con `python` a secas (workaround B). Binario absoluto del env:

  CUDA_VISIBLE_DEVICES="" /home/sdonoso/miniconda3/envs/clam_latest/bin/python \
      scripts/q1_slots_escalado.py --validate-b7 --self-test
  CUDA_VISIBLE_DEVICES="" /home/sdonoso/miniconda3/envs/clam_latest/bin/python \
      scripts/q1_slots_escalado.py            # barrido completo
  CUDA_VISIBLE_DEVICES="" /home/sdonoso/miniconda3/envs/clam_latest/bin/python \
      scripts/q1_slots_escalado.py --solo-agregar   # re-agrega sin recalcular
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

REPO = Path("/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto")
H5_DIR = Path("/media/administrador/Storage1/sdonoso/clam_environ/environ/features/h5_files")
RESULTS_4589 = REPO / "results/b7_mammoth_interp"
RUN_TS_4589 = "20260717_1812"

# Reuso del tooling del B7: misma config de Mammoth y misma carga de features, para que
# el número sea comparable con el de las 7 láminas y no una segunda implementación.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from mammoth_interpretability import (  # noqa: E402
    build_mammoth,
    load_feats_and_coords,
)
from answer_q1_expertos_slots import masa_acumulada, numero_efectivo  # noqa: E402

TAREAS = [
    "tipo_histologico_3clases_ci",
    "carcinoma_ductal_insitu_presente_ci_reform",
    "invasion_linfatica_vascular_ci_reform",
]

CAMPOS = [
    "task", "fold", "slide_id", "cohorte", "n_parches",
    "n_eff_expertos", "expertos_50", "expertos_90", "expertos_sobre_uniforme",
    "n_eff_slots", "slots_50", "slots_90", "slots_sobre_cota", "masa_sobre_cota",
    "y_true", "y_pred", "top5_slots", "segundos",
]


def cohorte_de(slide_id: str) -> str:
    """TCGA / HistAI / privado, por el prefijo del slide_id (los privados son numéricos)."""
    if slide_id.startswith("TCGA-"):
        return "TCGA"
    if slide_id.lower().startswith("histai"):
        return "HistAI"
    return "privado"


# =============================================================================
# 1. Medición por lámina (streaming exacto sobre los parches)
# =============================================================================
def _proyectar(mammoth, feats, chunk, device):
    """Pasos 1-2 del forward (`mammoth.py:341-342`): wq + norm + split multi-cabeza.

    Devuelve q de forma (1, N, H, P). Es chico (N x slot_dim floats), así que se
    materializa entero y las dos pasadas de logits lo reusan sin recalcular la
    proyección.
    """
    partes = []
    with torch.no_grad():
        for i in range(0, feats.shape[0], chunk):
            x = torch.from_numpy(feats[i:i + chunk]).float().unsqueeze(0).to(device)
            q = mammoth.norm(mammoth.wq(x))
            partes.append(q.reshape(1, q.shape[1], mammoth.num_heads, -1))
    return torch.cat(partes, dim=1)


def medir_lamina(mammoth, feats, chunk=2048, device="cpu"):
    """Pesos de ruteo agregados de una lámina: uso por experto y peso por slot.

    Equivale a `compute_expert_scores` + `compute_slot_weights` del B7, pero sin
    materializar los logits de los N parches a la vez.

    Devuelve (usage (E,), slot_combine (E, S)).
    """
    E, S, H = mammoth.num_experts, mammoth.num_slots, mammoth.num_heads
    N = int(feats.shape[0])
    q_all = _proyectar(mammoth, feats, chunk, device)

    combine_sum = torch.zeros(E * S, dtype=torch.float64)
    max_n = None   # (1, E, H, S) máximo de logits sobre los parches vistos
    sum_n = None   # (1, E, H, S) suma de exp(logits - max_n) sobre esos parches

    with torch.no_grad():
        # Pasada 1: combine (softmax local por parche y cabeza, se acumula directo) y el
        # logsumexp sobre parches que necesita dispatch (softmax global sobre n).
        for i in range(0, N, chunk):
            logits = mammoth.get_logits(q_all[:, i:i + chunk])      # (1, nc, E, H, S)
            comb = F.softmax(
                logits.permute(0, 1, 3, 2, 4).reshape(1, logits.shape[1], H, E * S),
                dim=-1,
            )                                                       # (1, nc, H, E*S)
            combine_sum += comb.sum(dim=(0, 1, 2)).double()

            m_chunk = logits.amax(dim=1)                            # (1, E, H, S)
            if max_n is None:
                max_n = m_chunk
                sum_n = torch.exp(logits - max_n.unsqueeze(1)).sum(dim=1)
            else:
                m_new = torch.maximum(max_n, m_chunk)
                sum_n = (sum_n * torch.exp(max_n - m_new)
                         + torch.exp(logits - m_new.unsqueeze(1)).sum(dim=1))
                max_n = m_new

        # Pasada 2: dispatch con el denominador global, normalizado por parche sobre
        # (E, H, S) y promediado sobre (H, S), idéntico a compute_expert_scores.
        scores_sum = torch.zeros(E, dtype=torch.float64)
        for i in range(0, N, chunk):
            logits = mammoth.get_logits(q_all[:, i:i + chunk])
            disp = torch.exp(logits - max_n.unsqueeze(1)) / sum_n.unsqueeze(1)
            disp = disp / disp.sum(dim=(2, 3, 4), keepdim=True)
            scores_sum += disp.mean(dim=(3, 4))[0].sum(dim=0).double()

    usage = (scores_sum / N).numpy()
    slot_combine = (combine_sum / (N * H)).numpy().reshape(E, S)
    return usage, slot_combine


def metricas(usage, slot_combine):
    """Números efectivos, masa acumulada y cota del uniforme, para una lámina."""
    E, S = slot_combine.shape
    w = slot_combine.ravel()
    cota = 1.0 / (E * S)
    sobre = w > cota
    orden = np.argsort(w)[::-1][:5]
    # `usage` NO suma 1: viene de promediar sobre (H, S) un dispatch que suma 1 sobre
    # (E, H, S), así que suma 1/(H·S). Hay que normalizarlo antes de compararlo con el
    # uniforme 1/E, o la cuenta da 0 siempre. `slot_combine` sí suma 1 (combine es una
    # softmax sobre los E·S slots), por eso su cota se aplica directa.
    usage_p = usage / usage.sum()
    return dict(
        n_eff_expertos=numero_efectivo(usage),
        expertos_50=masa_acumulada(usage, 0.50),
        expertos_90=masa_acumulada(usage, 0.90),
        expertos_sobre_uniforme=int((usage_p > 1.0 / E).sum()),
        n_eff_slots=numero_efectivo(w),
        slots_50=masa_acumulada(w, 0.50),
        slots_90=masa_acumulada(w, 0.90),
        slots_sobre_cota=int(sobre.sum()),
        masa_sobre_cota=float(w[sobre].sum() / w.sum()),
        top5_slots=" ".join(f"e{int(i)//S}·s{int(i)%S}" for i in orden),
    )


# =============================================================================
# 2. Inventario del barrido: qué láminas, con qué checkpoint
# =============================================================================
def ckpt_de(task, fold):
    return (RESULTS_4589 / task /
            f"clam_mammoth_{task}_f{fold}_{RUN_TS_4589}_s1" / f"s_{fold}_checkpoint.pt")


def laminas_de_test(task, fold):
    """Láminas de test del fold, desde la verdad de campo del propio job 4589.

    Se lee `test_predictions.csv` en vez de re-derivar el split (columna `test` del
    `splits_<f>.csv` intersecada con el CSV de labels y el label_dict): así el conjunto
    medido es exactamente el que evaluó el job, sin reimplementar el filtro.
    """
    p = (RESULTS_4589 / task / f"clam_mammoth_{task}_f{fold}_{RUN_TS_4589}_s1"
         / "test_predictions.csv")
    filas = []
    for row in csv.DictReader(open(p)):
        filas.append((row["slide_id"], int(row["y_true"]), int(row["y_pred"])))
    return filas


def h5_de(slide_id):
    return H5_DIR / f"{slide_id}.h5"


def preflight(tareas):
    """Checkpoints, predicciones y h5 presentes antes de gastar horas de CPU."""
    problemas, total = [], 0
    for task in tareas:
        for fold in range(5):
            ck = ckpt_de(task, fold)
            if not ck.exists():
                problemas.append(f"falta checkpoint {ck}")
                continue
            try:
                filas = laminas_de_test(task, fold)
            except FileNotFoundError as e:
                problemas.append(f"falta test_predictions: {e}")
                continue
            total += len(filas)
            faltan = [s for s, _, _ in filas if not h5_de(s).exists()]
            if faltan:
                problemas.append(
                    f"{task} f{fold}: {len(faltan)} h5 ausentes (p.ej. {faltan[:3]})")
    return total, problemas


# =============================================================================
# 3. Barrido reanudable
# =============================================================================
def _filas_intactas(path):
    """Filas ya escritas de un CSV parcial, descartando una última línea truncada."""
    if not path.exists():
        return []
    with open(path, newline="") as fh:
        lineas = fh.read().splitlines()
    if not lineas:
        return []
    filas = list(csv.DictReader(lineas))
    # Una corrida cortada a mitad de un write deja la última fila incompleta.
    if filas and any(filas[-1].get(c) in (None, "") for c in CAMPOS):
        filas = filas[:-1]
    return filas


def correr_fold(task, fold, out_dir, chunk, device, forzar=False):
    """Mide las láminas de test de un (tarea, fold). Devuelve nº de láminas medidas."""
    d = out_dir / task / f"fold{fold}"
    d.mkdir(parents=True, exist_ok=True)
    csv_path, meta_path = d / "laminas.csv", d / "meta.json"

    filas_todas = laminas_de_test(task, fold)
    if meta_path.exists() and not forzar:
        print(f"  {task} f{fold}: ya completo ({len(filas_todas)} láminas), se salta")
        return 0

    hechas = [] if forzar else _filas_intactas(csv_path)
    ya = {r["slide_id"] for r in hechas}
    pendientes = [f for f in filas_todas if f[0] not in ya]
    if not pendientes:
        # Todas medidas pero sin marcar: sólo faltaba el artefacto final.
        _escribir_meta(meta_path, task, fold, len(filas_todas), chunk)
        print(f"  {task} f{fold}: completo (se marca meta.json)")
        return 0

    # Reescribir el CSV con las filas íntegras evita heredar una línea truncada.
    with open(csv_path, "w", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=CAMPOS)
        wr.writeheader()
        for r in hechas:
            wr.writerow(r)

    print(f"  {task} f{fold}: {len(pendientes)} láminas por medir "
          f"({len(ya)} ya hechas)", flush=True)
    mammoth, _ = build_mammoth(str(ckpt_de(task, fold)), keep_slots=False, device=device)

    t_fold = time.time()
    with open(csv_path, "a", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=CAMPOS)
        for j, (sid, y_true, y_pred) in enumerate(pendientes, 1):
            t0 = time.time()
            feats, _ = load_feats_and_coords(str(h5_de(sid)))
            usage, slot_combine = medir_lamina(mammoth, feats, chunk, device)
            fila = dict(task=task, fold=fold, slide_id=sid, cohorte=cohorte_de(sid),
                        n_parches=int(feats.shape[0]), y_true=y_true, y_pred=y_pred,
                        **metricas(usage, slot_combine))
            fila["segundos"] = round(time.time() - t0, 2)
            wr.writerow(fila)
            fh.flush()
            os.fsync(fh.fileno())
            if j % 25 == 0 or j == len(pendientes):
                print(f"    [{j}/{len(pendientes)}] {sid[:28]:<30} "
                      f"N={fila['n_parches']:>6} slots={fila['n_eff_slots']:.1f} "
                      f"exp={fila['n_eff_expertos']:.1f} ({fila['segundos']:.1f}s)",
                      flush=True)

    _escribir_meta(meta_path, task, fold, len(filas_todas), chunk)
    print(f"  {task} f{fold}: listo en {(time.time() - t_fold) / 60:.1f} min", flush=True)
    return len(pendientes)


def _escribir_meta(meta_path, task, fold, n_laminas, chunk):
    """Artefacto FINAL del fold. Su ausencia es lo que marca un fold en vuelo."""
    meta_path.write_text(json.dumps(dict(
        task=task, fold=fold, n_laminas=n_laminas,
        ckpt=str(ckpt_de(task, fold)),
        fuente_laminas="test_predictions.csv del brazo clam_mammoth (job 4589)",
        chunk=chunk, medida="combine_weights (slots) + dispatch_weights (expertos)",
        terminado=time.strftime("%Y-%m-%d %H:%M:%S"),
    ), indent=2))


# =============================================================================
# 4. Agregación
# =============================================================================
def agregar(out_dir, tareas):
    """Junta los folds terminados y escribe el CSV por lámina y el resumen por tarea."""
    from scipy.stats import spearmanr

    filas = []
    incompletos = []
    for task in tareas:
        for fold in range(5):
            d = out_dir / task / f"fold{fold}"
            if not (d / "meta.json").exists():
                if (d / "laminas.csv").exists():
                    incompletos.append(f"{task} f{fold}")
                continue
            filas.extend(_filas_intactas(d / "laminas.csv"))
    if not filas:
        raise SystemExit(f"Sin folds terminados bajo {out_dir}")
    if incompletos:
        print(f"[aviso] folds en vuelo o incompletos, EXCLUIDOS: {', '.join(incompletos)}")

    num = ("n_parches", "n_eff_expertos", "n_eff_slots", "slots_sobre_cota",
           "masa_sobre_cota", "expertos_50", "expertos_90", "slots_50", "slots_90",
           "expertos_sobre_uniforme")
    for r in filas:
        for c in num:
            r[c] = float(r[c])

    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "q1_escalado_laminas.csv", "w", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=CAMPOS)
        wr.writeheader()
        wr.writerows(filas)

    def resumen(sub):
        s = np.array([r["n_eff_slots"] for r in sub])
        e = np.array([r["n_eff_expertos"] for r in sub])
        c = np.array([r["slots_sobre_cota"] for r in sub])
        m = np.array([r["masa_sobre_cota"] for r in sub])
        n = np.array([r["n_parches"] for r in sub])
        rho, p = (spearmanr(n, s) if len(sub) > 2 else (float("nan"), float("nan")))
        return dict(
            n_laminas=len(sub),
            slots_media=s.mean(), slots_std=s.std(ddof=1) if len(s) > 1 else 0.0,
            slots_min=s.min(), slots_max=s.max(), slots_mediana=float(np.median(s)),
            expertos_media=e.mean(), expertos_std=e.std(ddof=1) if len(e) > 1 else 0.0,
            expertos_min=e.min(), expertos_max=e.max(),
            sobre_cota_media=c.mean(), sobre_cota_min=c.min(), sobre_cota_max=c.max(),
            masa_sobre_cota_media=m.mean(),
            parches_media=n.mean(), parches_min=n.min(), parches_max=n.max(),
            rho_slots_vs_parches=float(rho), p_spearman=float(p),
        )

    grupos = [("TODAS", filas)]
    for task in tareas:
        sub = [r for r in filas if r["task"] == task]
        if sub:
            grupos.append((task, sub))
    for coh in ("TCGA", "HistAI", "privado"):
        sub = [r for r in filas if r["cohorte"] == coh]
        if sub:
            grupos.append((f"cohorte:{coh}", sub))

    campos_res = ["grupo"] + list(resumen(filas).keys())
    with open(out_dir / "q1_escalado_por_grupo.csv", "w", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=campos_res)
        wr.writeheader()
        for nombre, sub in grupos:
            wr.writerow(dict(grupo=nombre, **resumen(sub)))

    print(f"\n{'grupo':<46}{'n':>6}{'slots ef.':>12}{'±':>8}{'rango':>16}"
          f"{'expertos ef.':>14}{'sobre cota':>12}")
    print("-" * 116)
    for nombre, sub in grupos:
        r = resumen(sub)
        rango = f"{r['slots_min']:.0f} a {r['slots_max']:.0f}"
        print(f"{nombre[:44]:<46}{r['n_laminas']:>6}{r['slots_media']:>12.1f}"
              f"{r['slots_std']:>8.1f}{rango:>16}"
              f"{r['expertos_media']:>14.2f}{r['sobre_cota_media']:>12.1f}")

    glob = resumen(filas)
    print(f"\nSlots efectivos sobre {glob['n_laminas']} láminas-fold: "
          f"**{glob['slots_media']:.1f} de 300** (std {glob['slots_std']:.1f}, "
          f"rango {glob['slots_min']:.0f} a {glob['slots_max']:.0f})")
    print(f"Expertos efectivos: **{glob['expertos_media']:.2f} de 30** "
          f"(std {glob['expertos_std']:.2f})")
    print(f"Correlación slots efectivos vs nº de parches: rho={glob['rho_slots_vs_parches']:.3f} "
          f"p={glob['p_spearman']:.2e}")
    print(f"\nEscrito: {out_dir}/q1_escalado_laminas.csv y q1_escalado_por_grupo.csv")
    return filas


# =============================================================================
# 5. Validación contra el n=7 del B7
# =============================================================================
def self_test(device, chunk):
    """El camino streaming tiene que dar lo mismo que la implementación del B7.

    Compara contra `compute_expert_scores` y `compute_slot_weights`, que materializan
    los logits de los N parches de una vez. Si esto falla, el barrido grande no es
    comparable con el número de las 7 láminas.
    """
    from mammoth_interpretability import compute_expert_scores, compute_slot_weights

    sel = json.loads((REPO / "sprints/B7_sprint7/interp_slides.json").read_text())
    task = "carcinoma_ductal_insitu_presente_ci_reform"
    slide = sel[task]["slides"][0]
    print(f"[self-test] {slide['slide_id'][:34]} contra la implementación del B7")
    mammoth, _ = build_mammoth(sel[task]["ckpt_mammoth"], keep_slots=False, device=device)
    feats, _ = load_feats_and_coords(slide["h5"])

    scores_ref, _ = compute_expert_scores(mammoth, feats, device)
    usage_ref = scores_ref.mean(axis=0)
    slot_ref, _ = compute_slot_weights(mammoth, feats, device)
    usage, slot = medir_lamina(mammoth, feats, chunk, device)

    # Tolerancia RELATIVA: las dos implementaciones suman los mismos términos float32 en
    # distinto orden (por chunks contra todos los parches de una), así que coinciden hasta
    # el redondeo de float32, no bit a bit. Sobre pesos de ~3e-3 un |Δ| de 3e-9 es error
    # relativo ~1e-6. Un error de lógica daría órdenes de magnitud, no esto.
    d_e = float(np.abs(usage - usage_ref).max() / np.abs(usage_ref).max())
    d_s = float(np.abs(slot - slot_ref).max() / np.abs(slot_ref).max())
    n_e = abs(numero_efectivo(usage) / numero_efectivo(usage_ref) - 1.0)
    n_s = abs(numero_efectivo(slot.ravel()) / numero_efectivo(slot_ref.ravel()) - 1.0)
    print(f"           N={feats.shape[0]} chunk={chunk} | max |Δ| relativo: expertos "
          f"{d_e:.2e} slots {d_s:.2e} | n_eff: expertos {n_e:.2e} slots {n_s:.2e}")
    ok = max(d_e, d_s, n_e, n_s) < 1e-5
    print(f"           {'PASS' if ok else 'FAIL'} (tolerancia relativa 1e-5)")
    return ok


def validar_b7(out_dir, chunk, device):
    """Mide las 7 láminas del B7 y compara con `respuesta_q1_expertos_slots.json`."""
    sel = json.loads((REPO / "sprints/B7_sprint7/interp_slides.json").read_text())
    ref = {}
    ref_path = REPO / "sprints/B7_sprint7/respuesta_q1_expertos_slots.json"
    if ref_path.exists():
        for r in json.loads(ref_path.read_text()):
            ref[(r["task"], r["slide"])] = r

    print(f"\n{'tarea':<44}{'lámina':<22}{'slots':>9}{'ref':>9}{'Δ':>8}"
          f"{'exp':>7}{'ref':>7}")
    print("-" * 106)
    filas, deltas = [], []
    for task, cfg in sel.items():
        mammoth, _ = build_mammoth(cfg["ckpt_mammoth"], keep_slots=False, device=device)
        for s in cfg["slides"]:
            feats, _ = load_feats_and_coords(s["h5"])
            usage, slot_combine = medir_lamina(mammoth, feats, chunk, device)
            m = metricas(usage, slot_combine)
            corto = s["slide_id"].split(".")[0]
            r = ref.get((task, corto))
            d = m["n_eff_slots"] - r["slots_efectivos"] if r else float("nan")
            deltas.append(abs(d) / r["slots_efectivos"] if r else np.nan)
            print(f"{task[:42]:<44}{corto[:20]:<22}{m['n_eff_slots']:>9.1f}"
                  f"{(r['slots_efectivos'] if r else float('nan')):>9.1f}{d:>12.2e}"
                  f"{m['n_eff_expertos']:>8.1f}"
                  f"{(r['expertos_efectivos'] if r else float('nan')):>8.1f}")
            filas.append(dict(task=task, slide=corto, n_parches=int(feats.shape[0]), **m))

    media = float(np.mean([f["n_eff_slots"] for f in filas]))
    media_e = float(np.mean([f["n_eff_expertos"] for f in filas]))
    print(f"\nMEDIA sobre {len(filas)} láminas: slots {media:.1f} de 300 · "
          f"expertos {media_e:.1f} de 30")
    print("Referencia del B7 (n=7): slots 158.7 · expertos 30.0")
    peor = np.nanmax(deltas) if deltas else float("nan")
    ok = np.isfinite(peor) and peor < 1e-5
    print(f"Peor |Δ| RELATIVO por lámina contra el JSON del B7: {peor:.2e}  "
          f"{'PASS' if ok else 'REVISAR'} (tolerancia 1e-5)")

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "validacion_b7.json").write_text(json.dumps(
        dict(laminas=filas, media_slots=media, media_expertos=media_e,
             peor_delta_vs_b7=None if not np.isfinite(peor) else peor), indent=2))
    print(f"Escrito: {out_dir}/validacion_b7.json")
    return ok


# =============================================================================
def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out-dir", default=str(REPO / "results/b8_q1_slots_escalado"))
    ap.add_argument("--tasks", nargs="*", default=TAREAS)
    ap.add_argument("--folds", nargs="*", type=int, default=list(range(5)))
    ap.add_argument("--chunk", type=int, default=2048,
                    help="parches por chunk. Acota la memoria de los logits (1,nc,E,H,S).")
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--threads", type=int, default=8,
                    help="hilos de torch en CPU. Cortesía: el nodo es compartido y los "
                         "jobs SLURM ajenos también usan CPU. 0 = default de torch.")
    ap.add_argument("--self-test", action="store_true",
                    help="verifica el streaming contra la implementación del B7 y sale")
    ap.add_argument("--validate-b7", action="store_true",
                    help="mide las 7 láminas del B7 y compara con su JSON; no barre")
    ap.add_argument("--solo-agregar", action="store_true",
                    help="re-agrega los folds ya terminados sin recalcular nada")
    ap.add_argument("--forzar", action="store_true", help="rehace folds ya completos")
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    torch.set_grad_enabled(False)
    if args.threads > 0:
        torch.set_num_threads(args.threads)

    if args.self_test:
        ok = self_test(args.device, args.chunk)
        if not args.validate_b7:
            raise SystemExit(0 if ok else 1)
        if not ok:
            raise SystemExit("self-test FAIL: no seguir con la validación")

    if args.validate_b7:
        raise SystemExit(0 if validar_b7(out_dir / "validacion", args.chunk, args.device) else 1)

    if args.solo_agregar:
        agregar(out_dir, args.tasks)
        return

    total, problemas = preflight(args.tasks)
    if problemas:
        for p in problemas:
            print(f"PREFLIGHT: {p}")
        raise SystemExit("preflight falló, no se barre nada")
    print(f"Preflight OK: {total} láminas-fold, checkpoints y h5 presentes.\n")

    t0 = time.time()
    medidas = 0
    for task in args.tasks:
        print(f"== {task} ==")
        for fold in args.folds:
            medidas += correr_fold(task, fold, out_dir, args.chunk, args.device, args.forzar)
    print(f"\nBarrido: {medidas} láminas medidas en {(time.time() - t0) / 60:.1f} min")
    agregar(out_dir, args.tasks)


if __name__ == "__main__":
    main()
