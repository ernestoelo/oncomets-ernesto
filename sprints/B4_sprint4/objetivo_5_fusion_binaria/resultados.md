# Resultados — Objetivo 5

> **Objetivo 5 COMPLETO.** Fase 0 (job 4170, 27-may), Fase 1 (4171, 27-may) y
> Fase 2 (4172, 28-may) ya cerradas. Métricas = verdad de campo desde
> `results/obj5_varianza_*/.../summary.csv`,
> `results/obj5_fase{1,2}_*/.../test_metrics.json` y `split_*_results.pkl`.

---

## FASE 0 — Caracterización de varianza (CLAM, 3 binarias, MC-CV k=5)

**Setup**: CLAM_MB, args bendecidos, 328 slides/tarea, 5 repeticiones de
validación cruzada Monte Carlo (test_frac=0.1, semilla 1). Job 4170.

> "k-fold" en nombres de archivo = **Monte Carlo CV** (test solapados), el mismo
> `generate_split` de CLAM (`utils/utils.py:104-141`). No es k-fold canónico.

### Resultados (media ± std sobre 5 repeticiones)

| Tarea | test_auc por fold | **test_auc** | **balanced_acc** | 4109 (1 sorteo) |
|---|---|---|---|---|
| carcinoma invasivo | 0.41 / 0.83 / 0.74 / 0.84 / 0.84 | **0.732 ± 0.167** | **0.639 ± 0.077** | auc 0.808 · bal 0.78 |
| CDIS | 0.69 / 0.53 / 0.63 / 0.74 / 0.68 | **0.652 ± 0.072** | **0.595 ± 0.077** | auc 0.678 · bal 0.59 |
| tejido no neoplásico | 0.64 / 0.64 / 0.66 / 0.69 / 0.62 | **0.646 ± 0.025** | **0.577 ± 0.030** | auc 0.658 · bal 0.58 |

### Veredicto (regla §0.2)

**std(test_auc) > 0.05 en carcinoma (0.167) y CDIS (0.072)** → **varianza
confirmada grande**. Decisión pre-registrada aplicada: toda comparación
downstream (Fase 1/2, Sebastián) se evalúa **solo con MC-CV mean±std**; ningún
Δ de una sola partición cuenta como evidencia.

### Hallazgos

1. **El single-split del 4109 era optimista por suerte de sorteo.** Carcinoma:
   el 0.808 (bal_acc 0.78) que celebramos estaba en el TOPE de la distribución;
   un fold dio test_auc **0.406** (peor que el azar). Estimación honesta:
   **0.732 ± 0.167** / bal_acc **0.639 ± 0.077**. La "ventaja sobre Sebastián"
   en carcinoma **no se sostiene**.
2. **El std escala con los positivos en test, como predijo la hipótesis §0.1.**
   carcinoma (7 pos/test) → ±0.167; CDIS (11-14 pos) → ±0.072; tejido (20 pos)
   → ±0.025. Prueba empírica directa de por qué el método hacía falta.
3. **Frente a Sebastián: indistinguibles, no superiores.** Su número (1 sorteo,
   misma varianza) cae dentro de nuestras bandas en las 3 tareas. La
   contribución del objetivo NO es "ganarle" sino **medir la incertidumbre que
   el single-split escondía**.
4. **balanced_acc honesta**: las 3 tareas quedan en 0.58-0.64 — modestas,
   apenas sobre el piso 0.50. Coherente con el diagnóstico de que el cuello es
   **datos** (328 slides), no formulación ni arquitectura.

### Para la presentación

- Tabla y gráfico de barras con error: `tablas_presentacion.md` §C / §C.1.
- Mensaje: *medir la incertidumbre cambió la lectura* — el single-split decía
  "ganamos en carcinoma"; MC-CV dice "estadísticamente iguales, con barra de
  error grande donde hay pocas positivas".

---

## FASE 1 — CLAM sobre el fusionado (COMPLETA, job 4171, 27-may)

**Setup**: train_dsmil.py `--model_type clam`, 2814 slides, k=3 MC-CV, args
bendecidos. ~5h44m wall (3 folds × 30 epochs).

| Métrica | f0 | f1 | f2 | **media ± std** |
|---|---|---|---|---|
| test_auc | 0.805 | 0.764 | 0.758 | **0.776 ± 0.021** |
| balanced_acc | 0.632 | 0.621 | 0.608 | **0.620 ± 0.010** |
| confusión TP/FN (recall+) | 14/18 (0.44) | 11/21 (0.34) | 10/22 (0.31) | recall+ ≈ 0.36 |
| confusión TN/FP (recall−) | 206/43 (0.83) | 228/26 (0.90) | 225/24 (0.90) | recall− ≈ 0.88 |

### Veredicto (umbrales §1.3)

**balanced_acc 0.620 ± 0.010 → banda PLATEAU** (0.55 ≤ x < 0.65). El modelo NO
colapsa (recall+ ≈ 0.36, no 0 — un colapso daría recall+ = 0). Aprende algo,
pero el desbalance 7.6:1 lo inclina a "no" pese al `weighted_sample`. **No
llega al umbral clínico 0.65.** Coherente con la predicción pre-registrada
(§1.1: "detector modesto, no salto") y el precedente de Sebastián (cdis con
no_id → 0.69 AUC; nosotros 0.776 AUC pero balanced_acc honesta 0.620).

### Hallazgos

1. **Std súper estable (0.010 / 0.021)** porque cada test tiene 281-286 slides
   (32 positivos) — vs Fase 0 binarias con 33 slides (7-20 positivos) →
   confirma el argumento de "k por régimen": el fusionado no necesita k=5.
2. **Fusionar no fue bala de plata** — balanced_acc 0.620 es comparable al
   promedio de las binarias separadas (Fase 0: carcinoma 0.639, cdis 0.595,
   tejido 0.577). Aprovechar las ~2486 no_identificado no movió la métrica
   honesta.
3. **El gate de Fase 2 PASA** (0.620 > 0.55) → DSMIL corre. Comparación
   pareada CLAM vs DSMIL con barras de error chicas → el umbral arquitectónico
   +0.03 (§2.2) es exigente y honesto (DSMIL necesita bal_acc ≥ 0.65 mean).

## FASE 2 — DSMIL sobre el fusionado (COMPLETA, job 4172, 28-may)

**Setup**: train_dsmil.py `--model_type dsmil` (path DSMIL byte-idéntico a
4135/4137, reviewer-verificado), 2814 slides, **mismos splits k=3 que Fase 1**
(comparación pareada), args bendecidos + `w_max=0.1` ya validado. ~6h09m wall.
Gate de colapso §1.3 PASÓ (Fase 1 bal_acc 0.620 > 0.55) → DSMIL corrió como
estaba pre-registrado.

| Métrica | f0 | f1 | f2 | **media ± std** |
|---|---|---|---|---|
| test_auc | 0.781 | 0.723 | 0.764 | **0.756 ± 0.024** |
| balanced_acc | 0.726 | 0.630 | 0.626 | **0.661 ± 0.046** |
| confusión TP/FN (recall+) | 21/11 (0.66) | 12/20 (0.38) | 14/18 (0.44) | recall+ ≈ 0.49 ± 0.12 |
| confusión TN/FP (recall−) | 198/51 (0.80) | 225/29 (0.89) | 203/46 (0.82) | recall− ≈ 0.83 ± 0.04 |

### Comparación pareada CLAM vs DSMIL (mismos splits, 3 folds)

| Fold | CLAM bal_acc | DSMIL bal_acc | Δ bal_acc | CLAM AUC | DSMIL AUC | Δ AUC |
|---|---|---|---|---|---|---|
| f0 | 0.632 | 0.726 | **+0.094** | 0.805 | 0.781 | −0.024 |
| f1 | 0.621 | 0.630 | +0.009 | 0.764 | 0.723 | −0.041 |
| f2 | 0.608 | 0.626 | +0.018 | 0.758 | 0.764 | +0.006 |
| **media ± std** | 0.620 ± 0.010 | 0.661 ± 0.046 | **+0.040 ± 0.038** | 0.776 ± 0.021 | 0.756 ± 0.024 | **−0.020 ± 0.019** |

### Veredicto (umbrales §2.2 + adenda estadística)

**Banda AMBIGUA.** Lectura honesta:

- DSMIL media **0.661 ± 0.046** cruza el umbral pre-registrado §2.2 (≥0.65 mean
  para "supera") por +0.011 — dentro de la barra de error.
- Δ pareado **+0.040 ± 0.038** en balanced_acc: **signo positivo en los 3
  folds** (consistente), pero magnitud chica y std grande con k=3.
- **Bandas mean ± std SE SOLAPAN** (CLAM [0.610, 0.630] vs DSMIL [0.615, 0.707])
  → el heurístico §2.2 de "bandas no solapadas" NO se cumple.
- **AUC retrocede** (Δ = −0.020 ± 0.019), no acompaña al balanced_acc.

No es éxito arquitectónico (§2.2 exige Δ ≥ +0.03 mean **Y** bandas no
solapadas: cumple Δ pero NO bandas) ni regresión (Δ ≥ −0.05). Tampoco
"plateau" estricto (signo consistente en los 3 folds). **Lectura: banda
ambigua — NO sobre-vender como "supera a CLAM".**

### Hallazgos

1. **DSMIL es menos conservador, no necesariamente mejor discriminador.**
   Recupera más positivos (recall+ ≈ 0.49 vs CLAM 0.36) — detecta 1 de cada 2
   casos con micro vs 1 de cada 3 — pero a costa de más falsos positivos
   (recall− cae de 0.88 → 0.83). El AUC (independiente del umbral) **baja**
   −0.020 → DSMIL no rankea mejor, solo desplaza el umbral implícito.
2. **El régimen ya NO está data-starved** (era el argumento §2.1 para reabrir
   DSMIL en el fusionado), pero la arquitectura **no rinde aporte claro** ni
   siquiera con ~262 positivos en train (vs ~54 en las binarias del 4137).
   El cuello de botella no era solo el tamaño.
3. **Adenda §2.2 confirmada empíricamente.** Con MC-CV k=3 el `std` mismo es
   ruidoso; el Δ pareado es +0.040 en media pero su std (0.038) abarca cero.
   Sin paired test formal (paired t-test sobre 3 folds no es robusto), la
   evidencia direccional es **no concluyente**.
4. **Frente a CLAM Fase 1**: la accuracy DSMIL es similar (~0.79 vs 0.82),
   pero el patrón cambia — DSMIL acepta más FP por más TP. Para una decisión
   clínica con costo asimétrico (un FN vale más que un FP en screening), la
   balanced_acc 0.066 mayor podría preferirse — pero NO con k=3 como única
   evidencia. Sería un eje para validación externa.

### Para la presentación

- Slide 10 (`presentacion_contenido_completo.md`): tabla por fold + Δ pareado
  + veredicto ambiguo. Fig 2 (`figuras/fig2_fusionado_clam_vs_dsmil.png`).
- Mensaje: *DSMIL aporta direccionalmente en balanced_acc pero no en AUC, y
  las bandas se solapan a k=3. No es éxito ni fracaso — es "no concluyente",
  y eso vale como dato: la arquitectura sola tampoco mueve la aguja, el
  cuello sigue siendo datos / contexto espacial / desbalance.*
