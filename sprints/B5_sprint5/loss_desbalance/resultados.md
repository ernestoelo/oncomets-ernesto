# Eje loss-desbalance B5 — Resultados: CLAM + focal / class_balanced vs CLAM+CE, k=5 paired

> **ESTADO: COMPLETO / FINAL (3 binarias × 2 brazos).** Job **4463** (focal + cb, 30/30,
> CERRADO 24-jun) + job **4472** (re-run `cb` con el fix `ClassBalancedCE`, 15/15,
> CERRADO 24-jun 23:16). **Este documento ES el veredicto final del eje loss-desbalance**
> y cierra el Tier 1 que anticipaba [[calibracion-operating-point-palanca-b5]].
>
> Pre-registración (regla 9, NO reescribir): `prereg.md` (H1 palanca / H_alt null /
> H_reg sobre-corrige; desempate = **gap de recall**; métrica = balanced_acc test paired
> + AUC + confusión + n) + su **ADDENDUM** (bug `cb` no-op a batch=1 + fix). Auditoría del
> bug: `auditoria_hallazgos.md`. Análisis reproducible y verdad de campo:
> `results/loss_desbalance/analysis_4472_full.txt`.
>
> **Política de evaluación B5** ([[eval-reporte-auc-y-umbrales-obj6]]): se reportan
> **balanced_acc Y AUC juntos** (test) + matriz de confusión + **recall por clase con n**.
> Sin gate numérico — lectura cualitativa (consistencia de signo a través de folds,
> magnitud de la varianza vs trivial, y **gap de recall** como diagnóstico decisivo).

---

## 0. Veredicto FINAL

- **`focal` (γ=2, sin α) NO es palanca** (job 4463, válido): Δ bal_acc null-a-negativo
  (carcinoma −0.042 ± 0.081, cdis −0.064 ± 0.093, tejido +0.013 ± 0.052 control), Δ AUC
  negativo, y **baja** el recall de la minoritaria (carcinoma `si` 0.371→0.286, cdis `si`
  0.377→0.262). El γ-focusing sin α **no rescata la minoritaria** → el colapso persiste.
- **`class_balanced` (Cui 2019, β=0.9999, FIX `ClassBalancedCE`) NO es palanca** (job 4472):
  Δ bal_acc y Δ AUC **dentro del ruido** (std ≳ |media| en las 3 tareas: carcinoma
  +0.009 ± 0.074, cdis +0.039 ± 0.091, tejido +0.007 ± 0.032). El **mecanismo SÍ opera**
  (sube fuerte el recall de la minoritaria: carcinoma `si` 0.371→0.714, cdis `si`
  0.377→0.623, tejido `no` 0.500→0.676) **pero a costa de hundir la mayoritaria** (carcinoma
  `no` 0.908→0.588, cdis `no` 0.824→0.648, tejido `si` 0.646→0.485) → bal_acc neta ≈ sin
  cambio. **Lectura H_reg: re-balanceo del operating-point, no mejora neta.**
- **Mecanismo = el mismo que mover el umbral post-hoc** → converge con
  [[calibracion-operating-point-palanca-b5]] (la re-ponderación de la pérdida es el análogo
  *en training* de la calibración del operating-point). cb redistribuye la decisión, no
  agrega señal (el AUC, que mide el ranking, no se mueve).
- **Cierra el 4º ángulo barato del cuello.** Los 3 ejes de **arquitectura** ya estaban
  cerrados con 0 palancas (agregador/DSMIL Hallazgo 11, patch-embed/mammoth Hallazgo 12 —
  12 tareas, lenguaje+tile/PathPT Hallazgo 13). El eje **objetivo de entrenamiento**
  (loss de desbalance) tampoco mueve la aguja → **refuerza el cuello = datos / desbalance /
  contexto espacial**, no la arquitectura ni la función de pérdida.
- **Invasión NO se corrió.** Plan pre-registrado (prereg §4): invasión (n=2814, ~10-15h)
  solo si las binarias mostraban un lean prometedor. Ambos brazos son null/H_reg → cerrar
  el eje sin gastar la GPU pesada.

---

## 1. Configuración fija (idéntica a los baselines y a Obj1/Obj2/Obj3 — paired por construcción)

`max_epochs 30 · early_stopping · patience 20 · stop_epoch 50 · B 8 · bag_weight 0.7 ·
lr 2e-4 · reg 1e-5 · drop_out 0.25 · embed_dim 512 · seed 1 · weighted_sample ON`
(el sampler `weighted=True` está hardcodeado en `train_dsmil.py`). Modelo **CLAM_MB
intacto** → NO es "mammoth #3"; el único delta es la **bag loss**.

Tres brazos por tarea (el baseline ya en disco → **solo focal/cb fueron a GPU**):

| brazo | qué es | origen |
|---|---|---|
| `ce`    | CLAM_MB + CrossEntropy plana (baseline) | obj6 (en disco) |
| `focal` | CLAM_MB + focal loss (γ=2, sin α) | **job 4463** |
| `cb`    | CLAM_MB + class_balanced CE (`ClassBalancedCE`, β=0.9999) | **job 4472** (fix) |

Contrastes paired por fold (mismos splits k=5 — [[patron-paired-comparison-reuso-splits]]):
**C_focal = focal − CE** · **C_cb = cb − CE**, ambos vs el MISMO baseline CE en disco.

> **Confound declarado (prereg §1):** `cb` se apila SOBRE `weighted_sample` (ambos
> re-balancean). La pregunta exacta es *"¿la re-ponderación de la pérdida agrega algo POR
> ENCIMA del re-muestreo que ya tiene el baseline?"*. Respuesta empírica: **no** (H_reg).

---

## 2. Resultados por tarea (balanced_acc + AUC por fold, k=5)

Binarias ROC-AUC. Trivial bal_acc = **0.500**.

### 2.1 Carcinoma invasivo — n=328 {no:260, si:68}, minoritaria=`si` (21% pos)

| brazo | f0 | f1 | f2 | f3 | f4 | **media ± std** | métrica |
|---|---|---|---|---|---|---|---|
| ce    | 0.531 | 0.746 | 0.583 | 0.640 | 0.697 | **0.639 ± 0.077** | bAcc |
| focal | 0.551 | 0.654 | 0.531 | 0.712 | 0.537 | **0.597 ± 0.073** | bAcc |
| cb    | 0.506 | 0.657 | 0.709 | 0.616 | 0.754 | **0.648 ± 0.085** | bAcc |
| ce    | 0.406 | 0.834 | 0.743 | 0.836 | 0.842 | **0.732 ± 0.167** | AUC |
| focal | 0.354 | 0.817 | 0.623 | 0.852 | 0.837 | **0.697 ± 0.190** | AUC |
| cb    | 0.606 | 0.840 | 0.777 | 0.730 | 0.837 | **0.758 ± 0.086** | AUC |

### 2.2 CDIS — n=328 {no:210, si:118}, minoritaria=`si` (36% pos)

| brazo | f0 | f1 | f2 | f3 | f4 | **media ± std** | métrica |
|---|---|---|---|---|---|---|---|
| ce    | 0.718 | 0.494 | 0.588 | 0.636 | 0.541 | **0.595 ± 0.077** | bAcc |
| focal | 0.731 | 0.496 | 0.481 | 0.409 | 0.541 | **0.531 ± 0.108** | bAcc |
| cb    | 0.640 | 0.563 | 0.549 | 0.818 | 0.604 | **0.635 ± 0.097** | bAcc |
| ce    | 0.692 | 0.528 | 0.627 | 0.740 | 0.675 | **0.652 ± 0.072** | AUC |
| focal | 0.731 | 0.463 | 0.578 | 0.550 | 0.632 | **0.591 ± 0.089** | AUC |
| cb    | 0.714 | 0.532 | 0.539 | 0.781 | 0.688 | **0.651 ± 0.099** | AUC |

### 2.3 Tejido no neoplásico — n≈328–333 {si:~192, no:~136}, minoritaria=`no` (59% pos)

| brazo | f0 | f1 | f2 | f3 | f4 | **media ± std** | métrica |
|---|---|---|---|---|---|---|---|
| ce    | 0.608 | 0.544 | 0.585 | 0.609 | 0.540 | **0.577 ± 0.030** | bAcc |
| focal | 0.621 | 0.646 | 0.587 | 0.618 | 0.478 | **0.590 ± 0.059** | bAcc |
| cb    | 0.621 | 0.498 | 0.621 | 0.650 | 0.531 | **0.584 ± 0.059** | bAcc |
| ce    | 0.635 | 0.635 | 0.656 | 0.688 | 0.615 | **0.646 ± 0.025** | AUC |
| focal | 0.635 | 0.685 | 0.628 | 0.668 | 0.564 | **0.636 ± 0.042** | AUC |
| cb    | 0.635 | 0.650 | 0.676 | 0.684 | 0.615 | **0.652 ± 0.026** | AUC |

---

## 3. Δ pareados por fold (variante − CE)

| tarea | contraste | Δ bal_acc | signo | Δ AUC | signo |
|---|---|---|---|---|---|
| carcinoma | C_focal | −0.042 ± 0.081 | 2+/3− | −0.036 ± 0.048 | 1+/4− |
| carcinoma | **C_cb** | **+0.009 ± 0.074** | 2+/3− | **+0.026 ± 0.099** | 3+/2− |
| cdis | C_focal | −0.064 ± 0.093 | 2+/2− | −0.062 ± 0.074 | 1+/4− |
| cdis | **C_cb** | **+0.039 ± 0.091** | 3+/2− | **−0.001 ± 0.045** | 4+/1− |
| tejido | C_focal | +0.013 ± 0.052 | 4+/1− | −0.010 ± 0.034 | 1+/3− |
| tejido | **C_cb** | **+0.007 ± 0.032** | 3+/2− | **+0.006 ± 0.009** | 3+/1− |

→ En las 6 celdas, **std ≳ |media|** (banda H_alt/H0). El único Δ bal_acc con magnitud
notable (cdis cb +0.039) tiene std 0.091 (cruza 0) y Δ AUC ≈ 0 → re-balanceo, no señal.

---

## 4. Confusión pooled (rows=true) + recall por clase — el diagnóstico decisivo (gap de recall)

### 4.1 Carcinoma (test pooled: no=131, si=35)

| brazo | clase | [TN/FN, FP/TP] | recall |
|---|---|---|---|
| ce    | no | [119, 12] | 0.908 |
| ce    | **si** (min.) | [22, 13] | **0.371** |
| focal | no | [119, 12] | 0.908 |
| focal | **si** (min.) | [25, 10] | **0.286** |
| cb    | no | [77, 54] | 0.588 |
| cb    | **si** (min.) | [10, 25] | **0.714** |

### 4.2 CDIS (test pooled: no=108, si=61)

| brazo | clase | recall |
|---|---|---|
| ce    | no | 0.824 |
| ce    | **si** (min.) | **0.377** |
| focal | no | 0.815 |
| focal | **si** (min.) | **0.262** |
| cb    | no | 0.648 |
| cb    | **si** (min.) | **0.623** |

### 4.3 Tejido (test pooled: no=68, si=99) — minoritaria=`no`

| brazo | clase | recall |
|---|---|---|
| ce    | **no** (min.) | **0.500** |
| ce    | si | 0.646 |
| focal | **no** (min.) | **0.529** |
| focal | si | 0.646 |
| cb    | **no** (min.) | **0.676** |
| cb    | si | 0.485 |

**Lectura del gap de recall (desempate del prereg §2):**
- **`cb`** sube la minoritaria en las 3 tareas **pero hunde la mayoritaria en igual o mayor
  medida** → bal_acc neta sin cambio. Es exactamente el patrón "**re-balanceo, no palanca**"
  pre-registrado como H_reg (el matiz de `keep_slots` en Obj 3, ahora por la pérdida).
- **`focal`** apenas mueve el recall (carcinoma/cdis incluso lo **baja**) → el γ-focusing
  sin α no toca el colapso. H_alt.

---

## 5. Lectura vs pre-registración (regla 9.a — sin gate, dirección + consistencia + gap)

| hipótesis (prereg §2) | ¿se cumplió? | evidencia |
|---|---|---|
| **H1** (Δ bal_acc > 0 consistente, AUC ≈ igual) | **NO** | ningún Δ bal_acc consistente; std ≳ |media| |
| **H_alt** (Δ cruza 0 / std ≫ media → no palanca) | **SÍ (focal, y cb en bal_acc neta)** | las 6 celdas en banda H0 |
| **H_reg** (cb sube minoritaria pero hunde mayoritaria) | **SÍ (cb)** | gap de recall §4: rescate + colapso simétricos |

La **invasión** (mejor candidata por headroom AUC↔bal, prereg §3) **no se corrió**: ambos
brazos en binarias dieron null/H_reg → el plan pre-registrado (correr invasión solo ante un
lean prometedor) lo descartó por defecto. No hay señal que justifique la GPU pesada.

---

## 6. Cierre y trazabilidad

- **El eje loss-desbalance cierra como los 3 ejes de arquitectura: 0 palancas.** Es el
  análogo *en training* de la calibración del operating-point: acotado por el AUC (la señal
  en CONCH), no rompe el techo de datos.
- **Bug `cb` resuelto** (commit `2cab10f`, `ClassBalancedCE` + test de regresión a batch=1
  6/6): la versión válida es el job 4472. Los runs buggy del 4463 (`cb` no-op byte-idéntico
  a CE) quedan segregados en `results/loss_desbalance/_buggy_noop_cb_4463/` como **evidencia
  del bug** (NO borrar). Gotcha durable: [[mil-weighted-ce-noop-batch1]].
- **Provenance:** flag inicial `055efe1` · fix `2cab10f` · script de análisis `7d245fd` ·
  auditoría del bug `0b70dfd`. Branch `feat/loss-desbalance-b5`.
- Memoria del eje: [[loss-desbalance-eje-c1]]. Hermana post-hoc:
  [[calibracion-operating-point-palanca-b5]]. Marco de datos:
  [[insuficiencia-datos-ejes-investigacion]].
