# Etapa 1 — PathPT-CONCH vs CLAM en necrosis binaria: resultados

> **Veredicto: H_alt — PathPT no aporta sobre CLAM.** El Δ pareado cruza 0 con
> std ≫ |media| en balanced_acc, y lean negativo (no-consistente) en AUC.
> Tercer ángulo del mismo mensaje del sprint: **el cuello es el dato, no el método**
> (converge con Hallazgos 11 = agregador/DSMIL y 12 = patch-embed/mammoth).
>
> Pre-registración (regla 9, reviewer GO): [etapa1_prereg_necrosis.md](etapa1_prereg_necrosis.md).
> Job SLURM: **4309** (terminó 11-jun-2026 01:41). Verdad de campo:
> `results/pathpt_etapa1/necrosis/{clam,pathpt}_cdis_necrosis_2clases_pth_f<0..4>_20260610_2312_s1/`.

---

## 1. Diseño (lo que se corrió)

- **Tarea**: necrosis **binaria** presente (`si`) vs ausente (`no`), `no_identificado`
  **excluido** (mal definido a nivel tile). n=396 (313 `si` / 83 `no`).
- **Comparación PAIRED por fold** sobre los **mismos** splits k=5 MC-CV
  (`data/splits_kfold/cdis_necrosis_2clases_pth_100`, seed 1, estratificado):
  Δ_i = PathPT_i − CLAM_i ([[patron-paired-comparison-reuso-splits]]).
- **Brazo CLAM (baseline)**: `train_dsmil.py --model_type clam`, args bendecidos
  (`--B 8 --bag_weight 0.7 --lr 2e-4 --embed_dim 512 --drop_out 0.25`, CE + SVM inst).
- **Brazo PathPT**: `train_pathpt.py` — alcance **A (full)**: θ_v (espacial) + θ_t
  (prompt-tuning CoOp) + pseudo-labels tile-level + curriculum de pérdidas. Prompts
  **v3 anclados en CAP** (Invasive.Bx Nota C; go/no-go AUC 0.688). 20 épocas, lr 1e-4.
- **Métrica (política B5)**: balanced_acc + AUC + confusión + n, **juntas**. Estadístico
  decisivo = Δ pareado por fold. Umbral de PathPT elegido sobre `val` y congelado a `test`
  (H-2 del reviewer; sin DoF post-hoc).

---

## 2. Δ pareado por fold (PathPT − CLAM)

| Fold | CLAM AUC / bal_acc | PathPT AUC / bal_acc | ΔAUC | Δbal_acc |
|---|---|---|---|---|
| 0 | 0.798 / 0.653 | 0.798 / 0.663 | +0.000 | +0.010 |
| 1 | 0.782 / 0.607 | 0.798 / 0.698 | +0.016 | +0.091 |
| 2 | 0.598 / 0.656 | 0.588 / 0.641 | −0.010 | −0.016 |
| 3 | 0.754 / 0.610 | 0.599 / 0.502 | −0.155 | −0.108 |
| 4 | 0.703 / 0.641 | 0.522 / 0.563 | −0.182 | −0.078 |
| **media** | **0.727 / 0.633** | **0.661 / 0.613** | **−0.066 ± 0.094** | **−0.020 ± 0.078** |

- **Δ balanced_acc**: media −0.020, **std (0.078) ≫ |media|**, signo dividido **2+/3−**
  → **ambiguo/null** sin lugar a dudas (cruza 0).
- **Δ AUC**: media −0.066, **std (0.094) > |media|** → banda ambigua con **lean negativo**
  (1 empate, 1+, 3−), arrastrado por las caídas grandes de los folds 3 y 4 (−0.16, −0.18).
  **No** es regresión limpia y consistente (folds 0-1 empatan o favorecen a PathPT); el peso
  está del lado de CLAM.

---

## 3. Confusión pooled (5 test-folds; entregable obligatorio, H-3 reviewer)

Filas = verdad `[ausente(no), presente(si)]`; columnas = predicho `[no, si]`. Es la lectura
más estable de la clase chica (≈40 `ausente` agregados, vs ~8 por fold).

| Brazo | matriz | recall ausente | recall presente |
|---|---|---|---|
| CLAM | `[[16, 24], [21, 138]]` | 0.400 | 0.868 |
| PathPT | `[[19, 21], [39, 120]]` | 0.475 | 0.755 |

PathPT **no rompe nada**: redistribuye el trade-off — detecta un poco mejor la clase chica
(`ausente` 0.475 vs 0.400) **a costa** de la mayoritaria (`presente` 0.755 vs 0.868). El
balanced_acc neto sale casi igual → Δbal ≈ 0.

---

## 4. Lectura honesta (regla pre-registrada — signo + magnitud vs varianza, sin gate mágico)

- **No se cumple H1** (Δ>0 consistente). Se cumple **H_alt**: el Δ pareado cruza 0, std ≫
  |media|. **PathPT-CONCH no es la palanca** para necrosis en este régimen (n=396, 83 neg).
- **El entrenamiento apenas se despegó del zero-shot.** El `teacher_rank_metric` (AUC del
  teacher zero-shot en train) fue ~**0.61–0.63** por fold, y el AUC de test de PathPT entrenado
  (mean **0.661**) está muy cerca de ese piso → θ_v + θ_t **no agregaron** sustancialmente sobre
  el zero-shot. CLAM (mean AUC **0.727**) sí le gana al teacher. Señal extra: el `val_threshold`
  de PathPT cae siempre en **≈0.4999** (scores apretados alrededor de 0.5) → no separa con fuerza.
- **Matiz de implementación (prereg §7):** en binario la `candidate_loss` (ec.7) es degenerada
  (inerte), así que la maquinaria multiclase de PathPT se reduce — un matiz honesto de la lectura,
  no una excusa. En mitotic (3 clases) ese término sí se activaría.
- **Converge con Hallazgos 11 y 12.** Ni el agregador (DSMIL), ni el patch-embed (mammoth), ni
  ahora el lenguaje + supervisión tile-level (PathPT) mueven la aguja → el cuello es
  **dato / desbalance / contexto espacial**, no el método. Resultado **presentable** (cierra el
  tercer ángulo), no un fracaso.

---

## 5. Qué NO afirma / límites

- PathPT-**CONCH**: un null no condena a PathPT con otro encoder (KEEP), que no tenemos.
- No generaliza a **mitotic** (tarea más sutil, go/no-go 0.648) — experimento aparte.
- n chico (396, 83 neg) → eval ruidosa en la clase chica; el Δ pareado + la confusión pooled
  mitigan, no eliminan. La discretización del AUC con n=39/fold (8 neg × 31 pos = 248 pares)
  explica empates exactos entre brazos (ej. fold 0 ambos 0.7984).
- **Sign-off clínico de los prompts v3 = Sebastián** (pendiente; no bloquea este veredicto de
  ingeniería). Si los ajusta, el go/no-go se re-corre barato y se re-evalúa.

---

## 6. Provenance

- Job **4309** (`logs/eg_pathpt_necrosis_4309.{out,err}`), 5 folds × 2 brazos, sin errores.
- Análisis Δ: `test_metrics.json` de los 10 runs bajo `results/pathpt_etapa1/necrosis/`.
- Prompts CAP v3: [prompts_cap.md](prompts_cap.md) + auditoría `auditoria_cap/hallazgos.md`.
- Memoria: [[pathpt-testing-necrosis-mitotic]], [[cap-fuente-clases-tareas]].
