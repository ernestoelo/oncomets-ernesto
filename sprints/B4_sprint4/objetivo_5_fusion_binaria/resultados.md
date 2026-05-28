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

---

## ANEXO — DSMIL × 3 binarias × MC-CV k=5 (COMPLETA, job 4179, 28-may 12:15)

**Setup**: train_dsmil.py `--model_type dsmil`, 3 binarias × k=5 MC-CV,
**MISMOS splits que Fase 0** (paired por construcción), args idénticos a
Fase 2 (w_max 0.1 fijo). ~3h29m wall (15 folds; early stopping cortó antes
de 30 epochs en la mayoría). Hipótesis pre-registrada:
`hipotesis_dsmil_binarias.md` (reviewer OK 28-may).

### Por qué este anexo

Cierra simétricamente el cuadro arquitectónico CLAM vs DSMIL aplicando a
DSMIL la misma vara de Fase 0 (MC-CV k=5). El "fracaso DSMIL × binarias"
del job 4137 era **single-split**; Hallazgo 1 Fase 0 nos enseñó que el
single-split engaña fuerte a n≈33 (CLAM carcinoma "0.808" era 0.732 ±
0.167). Sin MC-CV no podíamos sostener "DSMIL falla en binarias".

### Resultados (media ± std, k=5) — comparación pareada vs CLAM Fase 0

| Tarea | CLAM auc (Fase 0) | DSMIL auc | Δ auc pareado | CLAM bal (Fase 0) | DSMIL bal | Δ bal pareado |
|---|---|---|---|---|---|---|
| carcinoma invasivo | 0.732 ± 0.167 | **0.722 ± 0.098** | **−0.011 ± 0.080** | 0.639 ± 0.077 | **0.617 ± 0.117** | **−0.023 ± 0.071** |
| CDIS | 0.652 ± 0.072 | **0.619 ± 0.099** | **−0.034 ± 0.081** | 0.595 ± 0.077 | **0.543 ± 0.077** | **−0.053 ± 0.026** |
| tejido no neoplásico | 0.646 ± 0.025 | **0.682 ± 0.042** | **+0.036 ± 0.048** | 0.577 ± 0.030 | **0.599 ± 0.029** | **+0.021 ± 0.051** |

### Δ pareado por fold (DSMIL − CLAM, mismos splits Fase 0)

| Fold | carcinoma (Δbal / Δauc) | CDIS (Δbal / Δauc) | tejido (Δbal / Δauc) |
|---|---|---|---|
| f0 | −0.020 / +0.143 | −0.036 / −0.068 | −0.067 / +0.081 |
| f1 | −0.040 / −0.034 | −0.019 / +0.061 | +0.063 / +0.046 |
| f2 | −0.143 / −0.057 | −0.045 / −0.101 | +0.024 / −0.053 |
| f3 | +0.071 / −0.085 | −0.091 / +0.066 | +0.010 / +0.033 |
| f4 | +0.017 / −0.020 | −0.071 / −0.126 | +0.077 / +0.073 |
| **Signo Δ bal** | 2/5 positivo, mixto | **5/5 negativo** (consistente) | 4/5 positivo |
| **Δ medio bal** | −0.023 ± 0.071 | **−0.053 ± 0.026** | +0.021 ± 0.051 |

### Veredicto (umbrales pre-registrados — `hipotesis_dsmil_binarias.md`)

| Tarea | Veredicto | Razón |
|---|---|---|
| carcinoma invasivo | **NULL ✅** | \|Δ bal\| = 0.023 < 0.03 Y bandas mean±std solapadas. El "0.824" AUC del 4137 era ruido del sorteo: con MC-CV, DSMIL 0.722 ± 0.098 es **indistinguible** de CLAM 0.732 ± 0.167. Confirma la hipótesis primaria (null). |
| CDIS | **REGRESIÓN leve ⚠️** | Δ bal = **−0.053** ≤ −0.05 (umbral pre-registrado de regresión) **Y** signo negativo en los 5 folds (no ruido aleatorio). El "fracaso DSMIL en CDIS" del 4137 **se sostiene con barras de error**. |
| tejido no neoplásico | **NULL / AMBIGUO** | Δ bal = +0.021 < 0.03 (no llega a "señal" pre-registrada +0.05) Y bandas mean±std solapadas. Δ auc +0.036 ± 0.048 (banda solapada). Aporte marginal, no consistente entre métricas. |

### Hallazgos del anexo

1. **2 de 3 tareas: empate estadístico CLAM vs DSMIL** → **confirma
   Hallazgo 4 de Fase 0** (cuello = datos, no arquitectura) ahora también
   con DSMIL. La arquitectura sola no rompe el techo de balanced_acc
   0.58–0.64 a n=328.
2. **CDIS es la única tarea con regresión consistente.** El signo negativo
   en los 5 folds (no es ruido aleatorio) sostiene la lectura del 4137:
   para CDIS la atención dual de DSMIL **resta** algo que CLAM sí captura.
   Posible explicación a explorar (no de este sprint): la morfología del
   CDIS (microcalcificaciones distribuidas dentro de ductos) podría
   beneficiar más la atención gated absoluta de CLAM que la dual
   relacional de DSMIL.
3. **Carcinoma con MC-CV "limpia" la narrativa del 4137.** El 4137 había
   dado test_auc 0.824 single-split (parecía "DSMIL gana en carcinoma");
   MC-CV dice 0.722 ± 0.098, paired Δ −0.011 con CLAM — **indistinguibles**.
   Mismo patrón empírico que el Hallazgo 1 Fase 0 sobre CLAM (0.808 →
   0.732 ± 0.167): el single-split es ruido del sorteo, no señal.
4. **Coherente con Fase 2 fusionado.** DSMIL en TODOS los regímenes
   evaluado con MC-CV (binarias + fusionado): aporte marginal/ambiguo en
   mejor caso, regresión leve en peor (CDIS). El veredicto arquitectónico
   queda **cerrado simétricamente** — no es la palanca para este pipeline
   de microcalcificaciones.

### Para la presentación

- Slide 12 nueva (`presentacion_contenido_completo.md`): tabla por fold +
  comparación pareada + veredicto por tarea.
- Figuras `figuras/fig3a_anexo_dsmil_vs_clam_binarias_auc.png` y
  `fig3b_..._balacc.png` (barras CLAM vs DSMIL con error, paired).
- Figuras `figuras/fig4{a..d}_*_confusion.png` (heatmaps 2×2 por fold de
  todos los experimentos: Fase 0, Fase 1, Fase 2, Anexo).
- Mensaje honesto: *DSMIL evaluado en TODOS los regímenes (binarias +
  fusionado, ambos con MC-CV). Conclusión arquitectónica cerrada: no es la
  palanca. El cuello sigue siendo datos / contexto / desbalance. CDIS abre
  una pregunta morfológica (atención dual vs gated absoluta) para futuro,
  no decisión de este sprint.*
