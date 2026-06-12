# Etapa 1 — PathPT-CONCH vs CLAM en tasa mitótica (3 clases ordinales): resultados

> **Veredicto: PathPT COLAPSA al argmax de la clase mayoritaria (score_1) — no es una
> comparación pareja.** Los 5 folds dan `balanced_acc = 0.333` exacto (el trivial de 3 clases):
> PathPT predice `score_1` para las 588 slides de test, **cero** predicciones de `score_2`/`score_3`.
> CLAM, en cambio, usa las 3 clases (bal_acc 0.494). El **macro-OVR AUC** de PathPT (0.662) NO
> colapsa del todo (el *ranking* continuo retiene señal), pero el *operating point* (argmax) es
> inusable bajo este desbalance. **Causa = la formulación ordinal "clase 0 = score_1 basal"**
> (prereg §3.1, sign-off de Sebastián que estaba pendiente), no un bug de código.
>
> Pre-registración: [etapa1_prereg_mitotic.md](etapa1_prereg_mitotic.md). Job SLURM: **4326**
> (terminó 11-jun-2026 22:29). Verdad de campo: `results/pathpt_etapa1/mitotic/`.

---

## 1. Diseño (lo que se corrió)

- **Tarea**: tasa mitótica **3 clases ordinales** `score_1/2/3` (Nottingham), `no_identificado`
  excluido. n=1177 (636/287/254). Paired k=5 PathPT (`train_pathpt.py --task mitotic`) vs CLAM
  (`train_dsmil.py --model_type clam --n_classes 3`), mismos splits.
- **Métrica (política B5)**: balanced_acc + macro-OVR AUC + confusión 3×3 + n. Δ pareado por fold.
  Operating point = **argmax** del score de slide (pre-registrado, simétrico al argmax de CLAM).

---

## 2. Δ pareado por fold (PathPT − CLAM)

| Fold | CLAM AUC / bal_acc | PathPT AUC / bal_acc | ΔAUC | Δbal_acc |
|---|---|---|---|---|
| 0 | 0.765 / 0.506 | 0.662 / **0.333** | −0.102 | −0.173 |
| 1 | 0.698 / 0.504 | 0.566 / **0.333** | −0.132 | −0.171 |
| 2 | 0.684 / 0.461 | 0.687 / **0.333** | +0.003 | −0.127 |
| 3 | 0.710 / 0.435 | 0.714 / **0.333** | +0.004 | −0.101 |
| 4 | 0.764 / 0.563 | 0.681 / **0.333** | −0.083 | −0.230 |
| **media** | **0.724 / 0.494** | **0.662 / 0.333** | **−0.062 ± 0.062** | **−0.160 ± 0.049** |

- **Δ balanced_acc**: −0.160 ± 0.049, **5/5 folds negativos**. Pero NO es "PathPT un poco peor":
  el 0.333 es el **trivial exacto** de un clasificador degenerado (siempre la mayoritaria).
- **Δ macro-OVR AUC**: −0.062 ± 0.062 (signo 3−/2+, std ≈ |media| → **ambiguo**). El ranking
  continuo de PathPT NO colapsa del todo: retiene señal latente comparable a CLAM en 2 folds.

---

## 3. Confusión pooled 3×3 (5 test-folds; filas=verdad s1/s2/s3, cols=pred)

| Brazo | matriz | recall por clase [s1, s2, s3] |
|---|---|---|
| CLAM | `[[231,53,36],[77,27,38],[26,28,72]]` | [0.72, 0.19, 0.57] |
| PathPT | `[[320,0,0],[142,0,0],[126,0,0]]` | **[1.00, 0.00, 0.00]** |

CLAM **usa las 3 clases** (acierta s1 y s3, flojo en s2). PathPT manda **todo a score_1**:
0 predicciones de score_2 o score_3 en 588 slides.

---

## 4. Lectura honesta — por qué colapsó (y por qué NO es un bug)

- **No es código.** El eval multiclase está validado (test CPU 9/9, incl. `test_eval_multiclass_auc`),
  y **CLAM sobre los mismos splits NO colapsa** (clasifica a nivel slide con `weighted_sample`, que
  corrige el desbalance). El colapso es del **modelo PathPT**, no del harness.
- **Es la formulación.** "Clase 0 = score_1 = basal ordinal" (prereg §3.1) hace que, a nivel **tile**,
  los parches de baja densidad mitótica dominen **todas** las slides — incluso las score_2/3, donde
  las figuras mitóticas son eventos raros y localizados. El pseudo-etiquetado tile quedó
  abrumadoramente clase 0 → el modelo aprendió a predecir clase 0 siempre. El `balanced_ce_loss`
  por-clase no alcanzó a rescatar a las minoritarias con tan pocos parches confiables de s2/s3.
  **Este es exactamente el supuesto que se marcó con sign-off pendiente de Sebastián.**
- **El ranking sobrevive, la decisión no.** El macro-OVR AUC (0.66) muestra que el score continuo
  de PathPT ordena parcialmente las clases — la señal latente existe — pero el **argmax** es inusable
  bajo este desbalance. El cuello es la **calibración del operating point multiclase**, no el ranking.
- **Conexión con el sprint.** Refuerza el patrón (Hallazgos 11/12 + necrosis H_alt): el cuello es
  **dato / desbalance / calibración**, no el agregador ni el método. Mitotic-ordinal además expone
  que la supervisión tile-level de PathPT es **frágil al desbalance ordinal** donde la clase basal
  domina los tiles.

---

## 5. Qué NO afirma / próximos pasos posibles

- **NO es un veredicto limpio de "PathPT no aporta"** (como sí fue necrosis, H_alt). Es un **colapso
  del clasificador** atribuible a la formulación → la comparación de balanced_acc no es pareja.
- **Antes de cualquier re-corrida**, el sign-off clínico de Sebastián sobre la formulación ordinal
  es lo prioritario (es su llamada). Caminos de fix posibles (no decididos): re-balancear el
  pseudo-etiquetado tile, calibrar umbrales por clase en val (en vez de argmax crudo), o tratar la
  tarea como ranking ordinal (usar el AUC como métrica primaria).
- La señal latente (AUC ~0.66) sugiere que **no está todo perdido** si se corrige el operating point;
  pero eso es un experimento aparte, con su prereg.

## 6. Provenance

- Job **4326** (`logs/eg_pathpt_mitotic_4326.{out,err}`), 5 folds × 2 brazos, sin errores de ejecución.
- Análisis Δ: `test_metrics.json` de los 10 runs bajo `results/pathpt_etapa1/mitotic/`.
- Formulación + prompts: [etapa1_prereg_mitotic.md](etapa1_prereg_mitotic.md) §3.1/§3.5,
  [prompts_cap.md](prompts_cap.md) §2. Memoria: [[pathpt-testing-necrosis-mitotic]].
