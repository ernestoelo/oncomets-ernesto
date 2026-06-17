# Obj 2 B5 — Resultados: Mammoth en CLAM sobre patrón arquitectónico de CDIS (4 binarias, k=5 paired)

> Job 4243 (RTX A6000, lanzado 3-jun 10:36 → terminó 4-jun 01:33, ~15h). 40 runs
> (4 tareas × 2 brazos × 5 folds). Ambos brazos por el **mismo harness**
> (`scripts/train_dsmil.py`), único delta `--model_type clam | clam_mammoth`.
> Comparación **pareada** reusando `data/splits_kfold/<task>_pth_100/splits_0..4.csv`
> (mismos splits MC-CV ambos brazos). Hipótesis pre-registrada + diseño:
> `sprints/B5_sprint5/objetivo_2_mammoth_patron_invasion/README.md`.
>
> **Política de evaluación B5** (memoria `eval-reporte-auc-y-umbrales-obj6`): se
> reportan **balanced_acc Y AUC juntos** (test) + matriz de confusión + n por
> clase. **Sin gate numérico** — interpretación cualitativa (consistencia de signo
> a través de folds, magnitud de la varianza, si supera el trivial 0.5). Dirección
> pre-registrada (H1): mammoth mejora ⇒ Δ pareado > 0 consistente en signo.
>
> **El crash previo está neutralizado:** el job 4241 (2-jun) murió tras 1/40 runs
> por un branch-switch en el working-tree compartido (workaround H). El 4243 corrió
> desde `main` sin tocar `git` → cerró los 40 runs sin `FileNotFoundError`.

## Configuración fija (idéntica a ambos brazos y a Obj1/microcalc)

`max_epochs 30 · early_stopping · patience 20 · stop_epoch 50 · B 8 · bag_weight 0.7 ·
lr 2e-4 · reg 1e-5 · drop_out 0.25 · embed_dim 512 · seed 1 · label_dict {"no":0,"si":1}`.
Mammoth (defaults del paper): `experts 30 · slots 10 · heads 16 · slot_dim 256 ·
dropout 0.1 · keep_slots False · share_lora_weights True · auto_rank True`.

## Dos regímenes de lectura (por construcción de la tarea)

Patrón arquitectónico es multi-label CAP aplastado en 4 binarias si/no sobre el mismo
universo (513 DCIS identificados). El **desbalance por patrón** parte la lectura en dos:

| Binaria | n `si` / `no` | desbalance | n_test/fold (pos) | régimen | lectura |
|---|---|---|---|---|---|
| cribiforme | 252 / 261 | ~1:1 | 51 (~25) | **balanceada** | fold a fold |
| solido | 388 / 125 | ~3:1 | 50–51 (~38) | desbalance moderado | fold a fold |
| micropapilar | 34 / 479 | 14:1 | 51 (3) | **estadísticamente ciego** | **pooled 5 folds** |
| papilar | 32 / 481 | 15:1 | 51 (3) | **estadísticamente ciego** | **pooled 5 folds** |

> No hay baseline Fase 0 previo para patrón (tareas nuevas) → el **brazo CLAM es el
> baseline** de la comparación pareada; el Δ es atribuible solo a mammoth.

## Resultados — régimen sano (fold a fold, k=5)

| Binaria | CLAM bal_acc | +Mammoth bal_acc | CLAM AUC | +Mammoth AUC |
|---|---|---|---|---|
| cribiforme | 0.650 ± 0.057 | 0.694 ± 0.078 | 0.710 ± 0.042 | 0.732 ± 0.047 |
| solido | 0.647 ± 0.065 | 0.632 ± 0.067 | 0.700 ± 0.048 | 0.679 ± 0.050 |

### Δ pareado por fold (mammoth − clam)

| Binaria | Δ bal_acc (media±std) | folds Δbal | signo | Δ AUC (media±std) | signo |
|---|---|---|---|---|---|
| cribiforme | **+0.044 ± 0.048** | [+0.076, −0.038, +0.040, +0.104, +0.038] | **4+/1−** | +0.022 ± 0.042 | 4+/1− |
| solido | **−0.014 ± 0.064** | [+0.013, +0.072, +0.020, −0.074, −0.103] | 3+/2− | −0.022 ± 0.055 | 2+/2− |

### Matrices de confusión (sumadas sobre los 5 folds) + recall por clase

| Binaria | brazo | [[TN, FP], [FN, TP]] | recall `no` | recall `si` |
|---|---|---|---|---|
| cribiforme | CLAM | [[92, 38], [51, 74]] | 0.71 | 0.59 |
| cribiforme | +Mammoth | [[91, 39], [39, 86]] | 0.70 | **0.69** |
| solido | CLAM | [[26, 34], [27, 165]] | 0.43 | 0.86 |
| solido | +Mammoth | [[29, 31], [42, 150]] | 0.48 | 0.78 |

## Resultados — régimen ciego (pooled, agregando los 15 positivos de los 5 folds)

3 positivos por fold de test → balanced_acc y AUC saltan en escalones gruesos fold a
fold. Se lee el **agregado de las predicciones de los 5 folds** (sens/spec/AUC global),
como pre-registró el README (§lectura especial micropapilar/papilar).

| Binaria | brazo | pooled n (pos) | [[TN, FP], [FN, TP]] | sens | spec | bal_acc (pool) | AUC (pool) |
|---|---|---|---|---|---|---|---|
| micropapilar | CLAM | 257 (15) | [[234, 8], [11, 4]] | 0.267 | 0.967 | 0.617 | 0.707 |
| micropapilar | +Mammoth | 257 (15) | [[223, 19], [12, 3]] | 0.200 | 0.921 | 0.561 | 0.710 |
| papilar | CLAM | 256 (15) | [[224, 17], [13, 2]] | 0.133 | 0.929 | 0.531 | 0.583 |
| papilar | +Mammoth | 256 (15) | [[228, 13], [14, 1]] | 0.067 | 0.946 | 0.506 | 0.599 |

> **Caveat MC-CV:** los test sets de los 5 folds se solapan (Monte-Carlo CV) → el pool
> recuenta algunas slides. El AUC/sens/spec pooled son **descriptivos globales**, no un
> test set independiente. Aun así el cuadro es nítido: ambos brazos **casi no detectan**
> el patrón (TP global = 4/15 y 2/15; mammoth 3/15 y 1/15).

## Interpretación (cualitativa, sin gate)

- **cribiforme — leve mejora, el caso más consistente del estudio.** Único con **4/5
  folds positivos en AMBAS métricas** (Δbal +0.044, ΔAUC +0.022). La confusión lo
  respalda: mammoth sube recall `si` **0.59 → 0.69 a igual recall `no`** (0.71→0.70) —
  recupera positivos sin pagar especificidad. PERO la std (0.048) ≈ la media (0.044) →
  la banda **cruza 0**: señal sugestiva, **no concluyente**. Es la única binaria
  **balanceada (~1:1)** del set.
- **solido — NULO.** Signo mixto (3+/2− en bal_acc, 2+/2− en AUC) y std muy por encima
  de la media (0.064 vs −0.014). La confusión muestra puro trade-off (recall `si`
  0.86→0.78, recall `no` 0.43→0.48) sin ganancia neta. Desbalance 3:1 → el modelo (ambos
  brazos) ya sesga a la mayoritaria `si`; mammoth no lo corrige.
- **micropapilar — NULO / leve regresión, régimen ciego.** Ambos brazos casi no detectan
  (CLAM 4/15, mammoth 3/15 TP). Δ bal_acc(pool) −0.056 (mammoth peor), Δ AUC(pool) +0.003
  (empate). Ninguno usable a esta escala de positivos.
- **papilar — NULO, ambos ≈ trivial.** bal_acc(pool) 0.531 (CLAM) y 0.506 (mammoth) ≈ el
  trivial 0.5; TP global 2/15 y 1/15. AUC(pool) leve a favor de mammoth (0.583→0.599) pero
  ambos rondan el azar. La tarea está **hambrienta de datos** (32 positivos en toda la
  cohorte).

### Hallazgo crítico — el efecto de mammoth está condicionado por el balance, no por la arquitectura

Cruzando Obj1 (microcalc) + Obj2 (patrón) = **7 binarias** con el mismo harness pareado.
Mammoth muestra un lean **positivo** SOLO en las **dos tareas más balanceadas**:

| Tarea | fracción positiva | Δ bal_acc pareado | dirección |
|---|---|---|---|
| microcalc · tejido | ~58% | +0.049 ± 0.077 (4+/1−) | leve mejora |
| **patrón · cribiforme** | **~49%** | **+0.044 ± 0.048 (4+/1−)** | **leve mejora** |
| microcalc · carcinoma | ~22% | −0.054 ± 0.125 | nulo |
| patrón · solido | desbalance 3:1 | −0.014 ± 0.064 | nulo |
| microcalc · cdis | ~36% | −0.086 ± 0.113 | leve regresión |
| patrón · micropapilar | 7% (ciego) | −0.056 (pool) | nulo/regresión |
| patrón · papilar | 6% (ciego) | −0.025 (pool) | nulo |

El predictor del resultado **no es** el agregador ni el patch-embed (lo que mammoth
ataca), sino el **régimen de datos**: cuando la clase está balanceada y hay positivos
suficientes (tejido, cribiforme) mammoth recupera algo de recall en la minoritaria;
cuando domina el desbalance o faltan positivos (solido, micropapilar, papilar, carcinoma,
cdis) cualquier señal se aplasta en varianza. Y aun en los dos casos "buenos",
**std ≈ |media|** → ninguno cruza a mejora dura.

### Veredicto

**Mammoth no es una palanca consistente para patrón arquitectónico** — mismo desenlace
que microcalc (Obj1). Cae en la **hipótesis alternativa H0** pre-registrada: Δ en banda
ambigua (signo mixto y/o |media| < std) en 3 de las 4 binarias; la 4ª (cribiforme) es un
lean positivo leve pero con la varianza al borde del efecto. **Refuerza —ahora sobre una
2ª familia de tareas— que el cuello de botella es datos / desbalance / contexto espacial,
no la arquitectura del modelo** (consistente con el cierre simétrico CLAM×DSMIL del Obj 5
y con Obj1). El hallazgo nuevo es que **el (débil) beneficio de mammoth aparece gobernado
por el balance de clases**, lo que apunta el esfuerzo de B5 hacia **datos** (magnificación,
parches útiles, más positivos) y no hacia más swaps de arquitectura.

Esto **no descarta** mammoth en absoluto: cribiforme deja la puerta abierta a que, con
una tarea balanceada + más datos, el mecanismo (instance-gradient interference) rinda.
La 2ª ola natural fue **invasión linfática** (3 clases, n=2814 — mucho más dato): **CERRADA**
(job 4246, 5-jun) y la puerta quedó **cerrada** — mammoth tampoco es palanca ahí (regresión
leve consistente vía colapso a la mayoritaria; el n grande no rescató). Detalle:
`resultados_invasion.md`. Con eso el hilo mammoth queda cerrado (8 tareas, 0 palancas).

## Trazabilidad

- Verdad de campo: `results/obj2_mammoth/<task>/<brazo>_<task>_f<0..4>_20260603_1036_s1/`
  (`test_metrics.json` con balanced_acc + AUC + confusión + n; `test_predictions.csv` con
  `y_prob_si`; `split_<f>_results.pkl`; `summary.csv`).
- Análisis: `scripts/analyze_obj2.py` (lectura pura; fold-a-fold para sanas, pooled para
  ciegas; std poblacional ddof=0, convención Obj1).
- Log del job: `logs/eg_mammoth_patinv_4243.{out,err}` (cierre `Job 4243 done` 4-jun 01:33).
- *(Nota: en assets para slides, los números de job se omiten y el baseline se rotula
  "Métricas oficiales Environ vX" — memoria `presentacion-convenciones-benjamin`.)*
