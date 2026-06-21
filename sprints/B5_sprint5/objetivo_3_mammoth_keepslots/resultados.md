# Obj 3 B5 — Resultados: Mammoth `keep_slots=True` (+ `slot_dropout`), k=5 paired

> **ESTADO: COMPLETO / FINAL (4 de 4 tareas).** Job **4387** CERRADO (RTX A6000, lanzado
> 19-jun ~15:43, cerró **20-jun 17:28:09**, 20 runs = invasión + tejido × k=5 × 2 brazos
> `kst`/`kst_sd`, 5 gates OK por tarea). Job **4400** (extensión §8 = `carcinoma` + `cdis`, 20
> runs) **CERRADO 21-jun** (gates + 10 preflights OK, `.err` solo FutureWarnings) → **matriz
> COMPLETA 4 brazos × 4 tareas, 5/5 (verificado con `scripts/analyze_obj3.py`)**. **Este documento
> ES el veredicto final del Obj 3** y CIERRA el ADDENDUM del Hallazgo 12. Todas las secciones
> (1–6) son definitivas.
>
> Análisis reproducible: `scripts/analyze_obj3.py` (solo lectura de `test_metrics.json`; no toca
> `clam_environ` ni inputs de ningún job). Pre-registración (regla 9, NO reescribir):
> `prereg.md` §2 (H1/H_alt/H_reg + métrica + **desempate: manda el gap de recall**) y §8 (extensión).
>
> **Política de evaluación B5** ([[eval-reporte-auc-y-umbrales-obj6]]): se reportan
> **balanced_acc Y AUC juntos** (test) + matriz de confusión + **recall por clase con n**. Sin
> gate numérico — lectura cualitativa (consistencia de signo a través de folds, magnitud de la
> varianza vs trivial, y **gap de recall** como diagnóstico decisivo, prereg §2).

---

## 0. Veredicto FINAL (matriz completa 4387 + 4400)

- **Matriz de las 3 binarias + invasión cerrada (4 brazos × 4 tareas, 5/5):** `keep_slots=True`
  **NO es palanca vs CLAM en ninguna tarea** (C2 Δ bAcc: invasión −0.031, carcinoma −0.020,
  cdis −0.023, tejido +0.046-ruido → **0/4 supera a CLAM** de forma decidible) → **confirma el
  Hallazgo 12**: el patch-embed, ahora con la variante de mecanismo cambiado incluida, no es la
  palanca; cuello = datos / desbalance / contexto espacial.
- **Matiz mecanístico nuevo (real y reproducible):** el cuello de botella de slots aprendido
  **mitiga consistentemente el colapso a la mayoritaria** que el drop-in (`keep_slots=False`)
  introducía — lean+ within-mammoth (C1) en **3/4** tareas y gap de recall de la minoritaria a
  favor en las 3 desbalanceadas/multiclase (invasión `presente` 0.434→0.516; carcinoma `si`
  0.286→0.314; cdis `si` 0.279→0.443, este último incluso supera a CLAM pero a costa de la
  mayoritaria). **Insuficiente para superar al baseline.**
- **`slot_dropout` descartado** (net-negativo en las 4 tareas; en invasión re-colapsa la
  minoritaria a 0.385).
- **Cierra el hilo mammoth completo:** 8 tareas drop-in (Hallazgo 12) + 4 tareas keep_slots
  (Obj 3) → **0 palancas**. La variante de mecanismo NO testeada (keep_slots) tampoco gana; solo
  aporta un matiz mecanístico (recupera su propia regresión). Detalle por tarea: §2 (invasión),
  §3 (tejido), §6 (carcinoma + cdis), síntesis §6.3.

---

## 0-bis. Veredicto interim original (con 4387, invasión+tejido) — conservado por trazabilidad

- **Invasión (3-clase, n=2814, eval sano fold-a-fold — el subset decisivo del prereg):**
  `keep_slots=True` **recupera PARCIALMENTE el colapso a la mayoritaria que `keep_slots=False`
  había introducido** (es el modo de falla pre-registrado del job 4246). Sobre el **diagnóstico
  decisivo** (gap de recall), `presente` sube **0.434 → 0.516** (hacia CLAM 0.577) y
  `no_identificado` baja levemente **0.815 → 0.808** → **el gap se angosta** (dirección **H1**).
  Pero la mejora **es within-mammoth (C1)**: contra el baseline real `keep_slots=True` **sigue
  por debajo de CLAM** (C2 Δ bAcc −0.031 ± 0.047, 4/5−). En magnitud, C1 está en **banda
  ambigua** (Δ bAcc +0.016 ± 0.023, |media| < std) aunque con **signo 4+/1−** y el gap a favor.
  **Lectura honesta: `keep_slots=True` deshace parte de su propia regresión, pero NO es palanca
  vs CLAM.**
- **`slot_dropout` (Brazo 2) es net-negativo:** Δ bAcc kst_sd−kst −0.041 ± 0.030 (4/5−) y en
  invasión **vuelve a hundir** `presente` recall a **0.385** (peor que el propio `keep_slots=False`).
  El regularizador **acentúa el colapso** → se descarta como mejora.
- **Tejido (binaria balanceada, n=333, test ~50):** dominado por ruido. C1 ≈ null (Δ bAcc
  −0.003 ± 0.072; Δ AUC −0.030 ± 0.148, std enorme). Consistente con "test chico → no resuelve".
- **No contradice el Hallazgo 12** en lo que hace al *veredicto de palanca*: con invasión cerrada,
  `keep_slots=True` **no le gana a CLAM**. El matiz nuevo y real es **mecanístico** (recupera su
  propio colapso de minoritaria), no de performance vs baseline. **El cierre completo del ADDENDUM
  espera a carcinoma/cdis (4400)** — donde, por desbalance (Hallazgo 12), la expectativa
  pre-registrada (§8) es H_alt/H_reg.

---

## 1. Configuración fija (idéntica a los baselines y a Obj1/Obj2 — paired por construcción)

`max_epochs 30 · early_stopping · patience 20 · stop_epoch 50 · B 8 · bag_weight 0.7 ·
lr 2e-4 · reg 1e-5 · drop_out 0.25 · embed_dim 512 · seed 1`. Mammoth (defaults del paper):
`experts 30 · slots 10 · heads 16 · slot_dim 256 · auto_rank True · share_lora_weights True`.

Cuatro brazos por tarea (los 2 baselines ya en disco → **solo `kst`/`kst_sd` fueron a GPU**):

| brazo | qué es | origen |
|---|---|---|
| `clam`   | CLAM_MB baseline | obj2/obj6 (en disco) |
| `ksf`    | mammoth `keep_slots=False` (drop-in, Hallazgo 12) | obj2/obj6 (en disco) |
| `kst`    | mammoth `keep_slots=True` (**Brazo 1, Obj 3**) | **job 4387** |
| `kst_sd` | mammoth `keep_slots=True` + `slot_dropout=0.1` (**Brazo 2**) | **job 4387** |

Contrastes paired por fold (mismos splits k=5 — `prereg.md` §3.1, [[patron-paired-comparison-reuso-splits]]):
**C1 (primario, within-mammoth) = kst − ksf** · **C2 (vs baseline real) = kst − CLAM** ·
**slot_dropout aislado = kst_sd − kst** (atribuye el efecto del regularizador, Obs 4.b reviewer).

---

## 2. Invasión linfática vascular (3 clases) — n=2814, eval sano fold-a-fold

Clases `{ausente:0, no_identificado:1, presente:2}` (orden alfabético, `--auto-label-dict`).
Trivial bAcc = **0.333**. Test por clase n≥36 → lectura **fold-a-fold** (el de más poder del hilo).

### 2.1 Balanced accuracy y AUC (macro-OVR) por fold

| brazo | f0 | f1 | f2 | f3 | f4 | **media ± std** | métrica |
|---|---|---|---|---|---|---|---|
| clam   | 0.621 | 0.582 | 0.609 | 0.630 | 0.668 | **0.622 ± 0.028** | bAcc |
| ksf    | 0.607 | 0.614 | 0.566 | 0.468 | 0.621 | **0.575 ± 0.057** | bAcc |
| kst    | 0.600 | 0.624 | 0.566 | 0.526 | 0.637 | **0.591 ± 0.040** | bAcc |
| kst_sd | 0.606 | 0.585 | 0.498 | 0.500 | 0.560 | **0.550 ± 0.044** | bAcc |
| clam   | 0.816 | 0.835 | 0.812 | 0.812 | 0.867 | **0.828 ± 0.021** | AUC |
| ksf    | 0.806 | 0.830 | 0.805 | 0.799 | 0.848 | **0.818 ± 0.019** | AUC |
| kst    | 0.818 | 0.839 | 0.801 | 0.827 | 0.839 | **0.825 ± 0.014** | AUC |
| kst_sd | 0.817 | 0.836 | 0.786 | 0.827 | 0.856 | **0.824 ± 0.023** | AUC |

### 2.2 Δ pareados por fold

| contraste | Δ bAcc | signo | Δ AUC | signo |
|---|---|---|---|---|
| **C1** (kst − ksf, primario) | **+0.016 ± 0.023** | 4+/1− | +0.007 ± 0.013 | 3+/2− |
| **C2** (kst − CLAM) | **−0.031 ± 0.047** | 1+/4− | −0.003 ± 0.015 | 3+/2− |
| slot_dropout (kst_sd − kst) | **−0.041 ± 0.030** | 1+/4− | −0.001 ± 0.010 | 2+/3− |

C1 bAcc folds `[-0.007, 0.010, 0.000, 0.058, 0.016]` · C2 bAcc folds `[-0.021, 0.042, -0.043, -0.104, -0.031]` ·
slot_dropout bAcc folds `[0.005, -0.039, -0.069, -0.026, -0.077]`.

### 2.3 Confusión sumada (rows=true) + recall por clase — **el diagnóstico decisivo**

| brazo | ausente (recall) | no_identificado (recall) | presente (recall) |
|---|---|---|---|
| clam   | [120, 46, 75] **0.498** | [99, 780, 106] **0.792** | [45, 32, 105] **0.577** |
| ksf    | [115, 64, 62] **0.477** | [97, 803, 85]  **0.815** | [47, 56, 79]  **0.434** |
| **kst**    | [108, 57, 76] **0.448** | [85, 796, 104] **0.808** | [42, 46, 94]  **0.516** |
| kst_sd | [110, 65, 66] **0.456** | [90, 797, 98]  **0.809** | [63, 49, 70]  **0.385** |

**Lectura (desempate prereg §2 = manda el gap de recall):** el modo de falla de mammoth-F
(`keep_slots=False`) era el **colapso a `no_identificado`** (recall 0.792→0.815) a costa de
`presente` (0.577→0.434). `keep_slots=True` (`kst`) **lo revierte parcialmente**: `presente`
**0.434 → 0.516** y `no_identificado` **0.815 → 0.808** → **gap angostado, dirección H1**. Pero
NO alcanza a CLAM (`presente` 0.516 < 0.577; `ausente` incluso baja 0.477→0.448) → en C2 sigue
por debajo. `slot_dropout` (`kst_sd`) **deshace la recuperación**: `presente` cae a **0.385**
(re-colapso) → confirma H_reg para el regularizador.

**Veredicto invasión (DEFINITIVO, 5/5):** `keep_slots=True` **no es palanca vs CLAM** (C2−),
pero **mitiga su propia regresión** (C1 lean+ con gap a favor, banda ambigua en magnitud);
`slot_dropout` es **net-negativo**. Coherente con Hallazgo 12 a nivel performance, con un matiz
mecanístico nuevo (el cuello de botella de slots **sí** da algo de capacidad a la minoritaria,
pero no lo suficiente para superar al baseline).

---

## 3. Microcalc en tejido no neoplásico (binaria balanceada) — n=333, test ~50

Clases `{no:0, si:1}` (si 195 / no 138, ~58% pos — la más balanceada del hilo). Trivial bAcc 0.500.
Test chico → confusión **pooled** (5 folds), no fold-a-fold.

### 3.1 Balanced accuracy y AUC (ROC) por fold

| brazo | f0 | f1 | f2 | f3 | f4 | **media ± std** | métrica |
|---|---|---|---|---|---|---|---|
| clam   | 0.608 | 0.544 | 0.585 | 0.609 | 0.540 | **0.577 ± 0.030** | bAcc |
| ksf    | 0.646 | 0.498 | 0.767 | 0.676 | 0.542 | **0.626 ± 0.096** | bAcc |
| kst    | 0.577 | 0.419 | 0.739 | 0.729 | 0.650 | **0.623 ± 0.117** | bAcc |
| kst_sd | 0.654 | 0.496 | 0.777 | 0.676 | 0.449 | **0.610 ± 0.121** | bAcc |
| clam   | 0.635 | 0.635 | 0.656 | 0.688 | 0.615 | **0.646 ± 0.025** | AUC |
| ksf    | 0.692 | 0.654 | 0.830 | 0.605 | 0.608 | **0.678 ± 0.083** | AUC |
| kst    | 0.638 | 0.400 | 0.725 | 0.763 | 0.711 | **0.647 ± 0.130** | AUC |
| kst_sd | 0.638 | 0.508 | 0.709 | 0.740 | 0.645 | **0.648 ± 0.080** | AUC |

### 3.2 Δ pareados por fold

| contraste | Δ bAcc | signo | Δ AUC | signo |
|---|---|---|---|---|
| **C1** (kst − ksf, primario) | **−0.003 ± 0.072** | 2+/3− | −0.030 ± 0.148 | 2+/3− |
| **C2** (kst − CLAM) | **+0.046 ± 0.106** | 3+/2− | +0.002 ± 0.122 | 4+/1− |
| slot_dropout (kst_sd − kst) | −0.012 ± 0.106 | 3+/2− | +0.001 ± 0.058 | 1+/4− |

### 3.3 Confusión pooled (rows=true) + recall

| brazo | no (recall) | si (recall) |
|---|---|---|
| clam   | [34, 34] **0.500** | [35, 64] **0.646** |
| ksf    | [49, 19] **0.721** | [48, 51] **0.515** |
| **kst**    | [36, 32] **0.529** | [28, 71] **0.717** |
| kst_sd | [37, 31] **0.544** | [32, 67] **0.677** |

**Lectura:** todas las std ≳ |media| en los Δ → **banda H_alt** (ruido). El único patrón legible
es que `kst` re-equilibra el recall (`si` 0.717 vs el `no`-sesgado de `ksf`), pero con n≈50 de
test el Δ pareado cruza 0 en C1. **Tejido = null**, como se esperaba para un test tan chico.

---

## 4. Síntesis de los 3 puntos (KSF / Brazo 1 / Brazo 2) — atribución de `slot_dropout`

| tarea | KSF (keep_slots=F) | **B1 kst (keep_slots=T)** | B2 kst_sd (+slot_dropout) | efecto slot_dropout |
|---|---|---|---|---|
| invasión bAcc | 0.575 | **0.591** | 0.550 | **−0.041 (perjudica)** |
| invasión `presente` recall | 0.434 | **0.516** | 0.385 | **re-colapsa** |
| tejido bAcc | 0.626 | **0.623** | 0.610 | −0.012 (ruido) |
| carcinoma bAcc | 0.585 | **0.620** | 0.611 | −0.009 (null) |
| carcinoma `si` recall | 0.286 | **0.314** | 0.314 | ≈0 |
| cdis bAcc | 0.509 | **0.572** | 0.556 | −0.016 (null) |
| cdis `si` recall | 0.279 | **0.443** | 0.459 | ≈0 |

`slot_dropout` **no ayuda en ninguna de las 4 tareas** y daña la minoritaria de invasión →
**descartado**. El Brazo 1 (`keep_slots=True` puro) es la única variante con señal mecanística:
recupera consistentemente el `si`/`presente` recall que KSF colapsaba (3/4 tareas), **pero solo
within-mammoth** — no supera a CLAM (ver §6.3, veredicto de la matriz completa).

---

## 5. Lectura vs hipótesis pre-registrada (prereg §2)

- **C1 invasión:** Δ bAcc +0.016 (4+/1−) en banda ambigua por magnitud, **pero gap de recall
  angostado** → por el **desempate (manda el gap)**, lean **H1** within-mammoth. No es "gana":
  es "el cuello de botella recupera parte de la capacidad para la minoritaria que el drop-in
  perdía".
- **C2 invasión:** Δ bAcc −0.031 (4/5−) → `keep_slots=True` **no supera a CLAM**. **H_alt como
  palanca** (no es lever vs baseline real), aunque el gap vs CLAM se angostó respecto de ksf.
- **Tejido:** **H_alt** (Δ cruza 0, std≫|media|).
- **Carcinoma:** C1 lean+ (Δ bAcc +0.035, 3+/1−) con gap de recall a favor leve (`si` 0.286→0.314)
  → **H1 within-mammoth débil**; C2 cruza 0 (−0.020 ± 0.121) → **H_alt como palanca**.
- **CDIS:** C1 el lean+ más marcado (Δ bAcc +0.063, 3+/1−), `si` recall rescatado hasta superar a
  CLAM (0.279→0.443 vs 0.377) **pero a costa de la mayoritaria** → **H1 within-mammoth** claro en
  el mecanismo; C2 sigue bajo CLAM (−0.023 ± 0.120, 1+/4−) → **H_alt como palanca**.
- **slot_dropout:** **H_reg** acotado al regularizador (net-negativo/null en las 4; re-colapsa la
  minoritaria de invasión).

Convergencia con el hilo (matriz completa): a nivel **performance vs baseline**, refuerza el
Hallazgo 12 (el patch-embed no es la palanca; cuello = datos/desbalance). Matiz nuevo y
reproducible en 3/4 tareas: el **cuello de botella de slots** sí toca el mecanismo del colapso
(recupera capacidad para la minoritaria), solo que insuficiente para superar a CLAM. Veredicto
final en §6.3.

---

## 6. Microcalc carcinoma + cdis (extensión §8) — **job 4400 CERRADO, 5/5**

> Job **4400** (`eg_mammoth_kst_binarias`) cerró sin errores (gates + 10 preflights OK, `.err`
> solo FutureWarnings). `kst`/`kst_sd` **5/5** en carcinoma y cdis → **matriz completa 4 brazos ×
> 4 tareas**. Mismas dos binarias desbalanceadas que el resto del hilo microcalc. Test chico →
> confusión **pooled** (5 folds), no fold-a-fold.

### 6.1 Microcalc en carcinoma invasivo (binaria, ~21% pos) — n=328, test ~33

Clases `{no:260, si:68}` (la más desbalanceada de las 3). Trivial bAcc 0.500.

**Balanced accuracy y AUC (ROC) por fold**

| brazo | f0 | f1 | f2 | f3 | f4 | **media ± std** | métrica |
|---|---|---|---|---|---|---|---|
| clam   | 0.531 | 0.746 | 0.583 | 0.640 | 0.697 | **0.639 ± 0.077** | bAcc |
| ksf    | 0.511 | 0.500 | 0.686 | 0.675 | 0.554 | **0.585 ± 0.080** | bAcc |
| kst    | 0.551 | 0.500 | 0.654 | 0.730 | 0.663 | **0.620 ± 0.083** | bAcc |
| kst_sd | 0.531 | 0.500 | 0.614 | 0.802 | 0.608 | **0.611 ± 0.105** | bAcc |
| clam   | 0.406 | 0.834 | 0.743 | 0.836 | 0.842 | **0.732 ± 0.167** | AUC |
| ksf    | 0.480 | 0.846 | 0.737 | 0.709 | 0.837 | **0.722 ± 0.132** | AUC |
| kst    | 0.583 | 0.777 | 0.726 | 0.799 | 0.803 | **0.738 ± 0.082** | AUC |
| kst_sd | 0.577 | 0.771 | 0.720 | 0.804 | 0.808 | **0.736 ± 0.086** | AUC |

**Δ pareados por fold**

| contraste | Δ bAcc | signo | Δ AUC | signo |
|---|---|---|---|---|
| **C1** (kst − ksf, primario) | **+0.035 ± 0.048** | 3+/1− | +0.016 ± 0.069 | 2+/3− |
| **C2** (kst − CLAM) | **−0.020 ± 0.121** | 3+/2− | +0.005 ± 0.087 | 1+/4− |
| slot_dropout (kst_sd − kst) | −0.009 ± 0.044 | 1+/3− | −0.001 ± 0.005 | 2+/3− |

**Confusión pooled (rows=true) + recall**

| brazo | no (recall) | si (recall) |
|---|---|---|
| clam   | [119, 12] **0.908** | [22, 13] **0.371** |
| ksf    | [116, 15] **0.885** | [25, 10] **0.286** |
| **kst**    | [121, 10] **0.924** | [24, 11] **0.314** |
| kst_sd | [119, 12] **0.908** | [24, 11] **0.314** |

**Lectura:** `kst` recupera **parcialmente** el `si` recall que `ksf` había colapsado (0.286 →
0.314) pero queda **muy por debajo de CLAM** (0.371), mientras la mayoritaria `no` sube (0.885 →
0.924). C2 cruza 0 (banda ambigua). El AUC casi no se mueve (~0.73 en los 4). Mismo patrón que
invasión: recuperación parcial within-mammoth, **no palanca vs CLAM**.

### 6.2 Microcalc en CDIS (binaria, ~36% pos) — n=328, test ~33

Clases `{no:210, si:118}`. Trivial bAcc 0.500.

**Balanced accuracy y AUC (ROC) por fold**

| brazo | f0 | f1 | f2 | f3 | f4 | **media ± std** | métrica |
|---|---|---|---|---|---|---|---|
| clam   | 0.718 | 0.494 | 0.588 | 0.636 | 0.541 | **0.595 ± 0.077** | bAcc |
| ksf    | 0.666 | 0.613 | 0.412 | 0.500 | 0.355 | **0.509 ± 0.117** | bAcc |
| kst    | 0.614 | 0.699 | 0.536 | 0.500 | 0.513 | **0.572 ± 0.075** | bAcc |
| kst_sd | 0.558 | 0.699 | 0.536 | 0.500 | 0.489 | **0.556 ± 0.076** | bAcc |
| clam   | 0.692 | 0.528 | 0.627 | 0.740 | 0.675 | **0.652 ± 0.072** | AUC |
| ksf    | 0.737 | 0.615 | 0.575 | 0.702 | 0.459 | **0.618 ± 0.098** | AUC |
| kst    | 0.653 | 0.740 | 0.565 | 0.715 | 0.589 | **0.652 ± 0.068** | AUC |
| kst_sd | 0.640 | 0.762 | 0.565 | 0.727 | 0.576 | **0.654 ± 0.079** | AUC |

**Δ pareados por fold**

| contraste | Δ bAcc | signo | Δ AUC | signo |
|---|---|---|---|---|
| **C1** (kst − ksf, primario) | **+0.063 ± 0.078** | 3+/1− | +0.035 ± 0.082 | 3+/2− |
| **C2** (kst − CLAM) | **−0.023 ± 0.120** | 1+/4− | +0.000 ± 0.108 | 1+/4− |
| slot_dropout (kst_sd − kst) | −0.016 ± 0.022 | 0+/2− | +0.002 ± 0.014 | 2+/2− |

**Confusión pooled (rows=true) + recall**

| brazo | no (recall) | si (recall) |
|---|---|---|
| clam   | [89, 19] **0.824** | [38, 23] **0.377** |
| ksf    | [82, 26] **0.759** | [44, 17] **0.279** |
| **kst**    | [77, 31] **0.713** | [34, 27] **0.443** |
| kst_sd | [72, 36] **0.667** | [33, 28] **0.459** |

**Lectura:** el caso más nítido del mecanismo. `kst` rescata el `si` recall de forma fuerte
(ksf 0.279 → **0.443**) e incluso **supera a CLAM** (0.377), pero **a costa de la mayoritaria**
`no` (0.824 → 0.713) → re-balanceo, no mejora neta: la bAcc total queda **por debajo de CLAM**
(0.572 vs 0.595, C2 1+/4−). AUC empatado con CLAM (0.652). Confirma el patrón: el cuello de
botella de slots redistribuye capacidad hacia la minoritaria, **sin ganar al baseline**.

### 6.3 Síntesis de la matriz COMPLETA (3 binarias + invasión) — veredicto final

**C1 (within-mammoth, kst − ksf) Δ bAcc** — ¿recupera keep_slots=True el colapso del drop-in?

| tarea | Δ bAcc C1 | signo | gap de recall minoritaria (ksf → kst) |
|---|---|---|---|
| invasión | +0.016 ± 0.023 | 4+/1− | `presente` 0.434 → 0.516 (↑ hacia CLAM 0.577) |
| carcinoma | +0.035 ± 0.048 | 3+/1− | `si` 0.286 → 0.314 (↑ leve, CLAM 0.371) |
| cdis | +0.063 ± 0.078 | 3+/1− | `si` 0.279 → 0.443 (↑ fuerte, supera CLAM 0.377) |
| tejido | −0.003 ± 0.072 | 2+/3− | null (test balanceado chico) |

→ **3 de 4 con lean+ consistente y gap de recall a favor.** `keep_slots=True` **deshace de forma
reproducible parte del colapso a la mayoritaria** que `keep_slots=False` introducía. Es el
hallazgo **mecanístico** nuevo del Obj 3.

**C2 (vs baseline real, kst − CLAM) Δ bAcc** — ¿es palanca?

| tarea | Δ bAcc C2 | signo |
|---|---|---|
| invasión | −0.031 ± 0.047 | 1+/4− |
| carcinoma | −0.020 ± 0.121 | 3+/2− |
| cdis | −0.023 ± 0.120 | 1+/4− |
| tejido | +0.046 ± 0.106 | 3+/2− (ruido) |

→ **0 de 4 supera a CLAM de forma decidible.** Las binarias cruzan 0 (banda H_alt por magnitud);
invasión lean negativo consistente. **`keep_slots=True` NO es palanca vs CLAM.**

**slot_dropout (kst_sd − kst):** net-negativo o null en las 4 tareas (invasión −0.041, carcinoma
−0.009, cdis −0.016, tejido −0.012) y en invasión re-colapsa la minoritaria → **descartado.**

**VEREDICTO FINAL del Obj 3 (matriz completa, regla 9 / prereg §2 + §8):**
- A nivel **palanca de performance**, `keep_slots=True` **NO supera a CLAM en ninguna de las 4
  tareas** → **confirma el Hallazgo 12** (el patch-embed, ahora con la variante de mecanismo
  cambiado incluida, no es la palanca; cuello = datos / desbalance / contexto espacial).
- El **matiz mecanístico nuevo y real**: el cuello de botella de slots aprendido (`keep_slots=True`)
  **mitiga consistentemente el colapso a la mayoritaria** que el drop-in (`keep_slots=False`)
  introducía — lean+ within-mammoth (C1) en 3/4 tareas y gap de recall a favor en las 3
  desbalanceadas/multiclase. Pero la redistribución de capacidad hacia la minoritaria es
  **insuficiente para superar al baseline**.
- `slot_dropout` **descartado** (net-negativo en las 4).
- Expectativa pre-registrada §8 (probable null/H_alt en carcinoma/cdis por desbalance):
  **CONFIRMADA** para la pregunta de palanca, con el mismo matiz mecanístico que invasión.

---

## 7. Provenance

- Job 4387: `logs/eg_mammoth_keepslots_4387.{out,err}`. Resultados:
  `results/obj3_mammoth_keepslots/{invasion_linfatica_vascular_pth,microcalcificaciones_en_tejido_no_neoplasico_pth}/<brazo>_*_f<0..4>_*_s1/{test_metrics.json,test_predictions.csv}`.
- Baselines paired (en disco): invasión `results/obj2_mammoth/invasion_linfatica_vascular_pth/`;
  tejido `results/obj6_mammoth_binarias_tejido_no_neoplasico/`.
- Análisis: `scripts/analyze_obj3.py`. Pre-reg: `prereg.md`. Slurm: `scripts/run_obj3_mammoth_keepslots_kfold.slurm`.
