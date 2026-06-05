# Obj 2 B5 (2ª ola) — Resultados: Mammoth en CLAM sobre invasión linfática (3 clases, k=5 paired)

> **ESTADO: CERRADO** — job 4246 (RTX A6000, lanzado 4-jun 09:52, cerró **5-jun 06:18**,
> `GROUP=invasion`). 10 runs = 3-clase × k=5 × 2 brazos (`clam`, `clam_mammoth`) COMPLETOS.
> **Veredicto: mammoth NO es palanca para invasión** — Δ bal_acc −0.047 ± 0.064 (banda
> ambigua por magnitud, lean negativo 4/5) y **regresión leve consistente en AUC** (Δ
> −0.011 ± 0.005, **5/5 folds negativos**), mecánicamente por **mayor colapso a la
> mayoritaria** `no_identificado` (recall 0.792→0.815) a costa de `presente` (0.577→0.434).
> Ni el n más grande del hilo (2814) ni el régimen de eval más sano rescatan a mammoth →
> **refuerza Hallazgo 12** (cuello = datos/desbalance/contexto espacial, NO el patch-embed).
> Análisis reproducible: `scripts/analyze_invasion.py`. Secciones 1-5 y 9 definitivas.
>
> Ambos brazos por el **mismo harness** (`scripts/train_dsmil.py`), único delta
> `--model_type clam | clam_mammoth`. Comparación **pareada** reusando los mismos splits
> ([[patron-paired-comparison-reuso-splits]]). Hipótesis **pre-registrada** (regla 9, NO
> reescribir): `sprints/B5_sprint5/objetivo_2_mammoth_patron_invasion/README.md` §Hipótesis.
>
> **Política de evaluación B5** ([[eval-reporte-auc-y-umbrales-obj6]]): se reportan
> **balanced_acc Y AUC juntos** (test) + matriz de confusión **3×3** + n por clase. **Sin
> gate numérico** — interpretación cualitativa (consistencia de signo a través de folds,
> magnitud de la varianza, si supera el **trivial 0.333**). Dirección pre-registrada (H1):
> mammoth mejora ⇒ Δ pareado > 0 consistente en signo.

## 1. Configuración fija (idéntica a ambos brazos y a Obj1/patrón)

`max_epochs 30 · early_stopping · patience 20 · stop_epoch 50 · B 8 · bag_weight 0.7 ·
lr 2e-4 · reg 1e-5 · drop_out 0.25 · embed_dim 512 · seed 1 · n_classes 3 ·
label_dict {"ausente":0, "no_identificado":1, "presente":2}` (orden alfabético).
Mammoth (defaults del paper): `experts 30 · slots 10 · heads 16 · slot_dim 256 ·
dropout 0.1 · keep_slots False · share_lora_weights True · auto_rank True`.

## 2. Tarea y clases (referencia CAP)

Tarea `invasion_linfatica_vascular_pth`. Clases = protocolo CAP *Lymphatic and/or Vascular
Invasion* (`papers/Breast.Invasive.Bx_1.2.0.0.REL_CAPCP.pdf`): **Not identified · Present ·
Cannot be determined** → lista cerrada (NO "select all that apply") ⇒ **multiclase de 3
clases**, NO binarias ([[cap-fuente-clases-tareas]]). Mapeo a labels Environ:
`{ausente, no_identificado, presente}`.

> Contraste con patrón: patrón era "select all that apply" → multi-label → 4 binarias;
> invasión es lista cerrada → un único clasificador de 3 vías. Trivial bal_acc = **0.333**.

## 3. Dataset y n por clase (validado contra el CSV, 4-jun)

Cohorte `_pth` = Privado (Environ) + TCGA + HistAI. CSV de labels (snapshot filtrado a
slides con `.pt`): `data/csv_new_tasks/dataset_invasion_linfovascular_label.csv`
(columnas `case_id, slide_id, label`).

| clase | n | % | label_dict |
|---|---|---|---|
| `no_identificado` | 1967 | 69.9% | 1 |
| `ausente` | 479 | 17.0% | 0 |
| `presente` | 368 | 13.1% | 2 |
| **total** | **2814** | 100% | — |

Fuente: HistAI 1418 + TCGA 864 + Privado 532. El crudo era 2815; se excluye 1 slide HistAI
(`histai_1132_slide_H&E_0`) sin features `.pt` → **2814**. Es **~8× más dato por run** que
las binarias de patrón (513) → es la tarea con mejor chance de señal estable de todo el
hilo mammoth.

## 4. Splits (verdad de campo — validado, 4-jun)

`data/splits_kfold/invasion_linfatica_vascular_pth_100/splits_{0..4}.csv` (+ `_bool`,
`_descriptor`). Esquema: **Monte-Carlo CV k=5** estratificado, `patient_strat`,
`val_frac=test_frac=0.1`, `seed=1` (`scripts/build_new_tasks_splits.py`; verificado con
`scripts/verify_kfold_splits.py` → rc=0). Ambos brazos leen **el mismo** `splits_<f>.csv`.

**Composición por fold (test) — validada contra el CSV de labels:**

| fold | train (n) | val (n) | test n | test: ausente | test: no_id | test: presente |
|---|---|---|---|---|---|---|
| 0 | 2254 | 279 | 281 | 48 | 196 | 37 |
| 1 | 2247 | 284 | 283 | 49 | 198 | 36 |
| 2 | 2249 | 282 | 283 | 48 | 199 | 36 |
| 3 | 2253 | 279 | 282 | 48 | 197 | 37 |
| 4 | 2249 | 286 | 279 | 48 | 195 | 36 |

> **Régimen de eval SANO para las 3 clases**: cada clase tiene n≥36 en cada test fold
> (incluso la minoritaria `presente` ~37). Esto **valida la lectura fold-a-fold** del Δ
> pareado — NO se necesita el pooling que sí requerían micropapilar/papilar (3 pos/test,
> régimen "ciego"). Es el primer escenario del hilo mammoth donde la minoritaria es
> medible por fold.

## 5. Métrica y política de lectura

- **Decisiva:** `balanced_acc` (test), **Δ pareado por fold** = `mammoth_f − clam_f`,
  media ± std **poblacional** (ddof=0, convención Obj1/patrón).
- **Secundaria (se reporta SIEMPRE, no decide):** **macro-OVR AUC** (one-vs-rest promediado
  sobre las 3 clases; computado por el fix multiclase de `train_dsmil.py`). Confusión **3×3**
  + n por clase, siempre.
- **Dirección pre-registrada (H1):** mammoth mejora ⇒ Δ pareado > 0 consistente en signo.
  **H0:** Δ en banda ambigua (signo mixto ó |media| < std) ⇒ no es palanca. **Regresión:**
  Δ < 0 consistente (≥4/5 folds) sin cruzar 0 trivialmente.
- **Mecanismo a vigilar:** (a) **colapso a `no_identificado`** (mayoritaria 70%) vía la
  confusión 3×3 — el modo de fallo esperable; (b) en el brazo mammoth, `|grad W_0|` y
  `|grad q|` > 0 (en `clam` valen 0).

---

## 6. Resultados

### 6.1 Tabla por brazo (test, k=5) + detalle por fold

| brazo | bal_acc (media±std) | macro-OVR AUC (media±std) |
|---|---|---|
| CLAM | **0.622 ± 0.028** | **0.828 ± 0.021** |
| +Mammoth | **0.575 ± 0.057** | **0.818 ± 0.019** |

Detalle por fold (`scripts/analyze_invasion.py`; std poblacional ddof=0):

| fold | CLAM bAcc | Mam bAcc | Δ bAcc | CLAM AUC | Mam AUC | Δ AUC | n |
|---|---|---|---|---|---|---|---|
| 0 | 0.621 | 0.607 | −0.015 | 0.816 | 0.806 | −0.010 | 281 |
| 1 | 0.582 | 0.614 | **+0.032** | 0.835 | 0.830 | −0.005 | 283 |
| 2 | 0.609 | 0.566 | −0.044 | 0.812 | 0.805 | −0.007 | 283 |
| 3 | 0.630 | **0.468** | **−0.162** | 0.812 | 0.799 | −0.013 | 282 |
| 4 | 0.668 | 0.621 | −0.046 | 0.867 | 0.848 | −0.019 | 279 |

> Ambos brazos quedan **bien sobre el trivial 0.333** (bAcc ~0.47-0.67), confirmando que
> el n grande (2814) sostiene señal estable — el régimen de eval es sano. El fold 3 es un
> **outlier de colapso** del brazo mammoth (bAcc 0.468; ver §6.3): mammoth f3 manda casi
> todo a `no_identificado` (recall_no_id 0.944, recall_presente 0.189).

### 6.2 Δ pareado por fold (mammoth − clam)

| métrica | Δ media±std | folds | signo |
|---|---|---|---|
| Δ bal_acc | **−0.047 ± 0.064** | [−0.015, +0.032, −0.044, −0.162, −0.046] | **1+/4−** |
| Δ macro-OVR AUC | **−0.011 ± 0.005** | [−0.010, −0.005, −0.007, −0.013, −0.019] | **0+/5−** |

> **Lectura (política B5, sin gate):** la métrica **decisiva** `Δ bal_acc` tiene std (0.064)
> > |media| (0.047) → cae en la **banda ambigua** por magnitud, pero con **lean negativo
> consistente** (4/5 folds, único positivo f1 +0.032), arrastrada por el colapso de f3. La
> **secundaria** `Δ AUC` es **5/5 negativa** con |media| (0.011) > std (0.005) → cumple el
> criterio pre-registrado de **regresión** (signo consistente, no cruza 0 trivialmente),
> aunque de **magnitud chica**. Quitando el outlier f3, Δ bAcc = −0.018 (3/4−): el lean
> negativo persiste, más suave. Síntesis honesta: **mammoth no mejora; regresión leve pero
> consistente**, clara en AUC, dentro del ruido en bAcc.

### 6.3 Confusiones 3×3 sumadas (5 folds) + recall por clase

Orden filas/cols = (ausente, no_identificado, presente). Recall = diagonal / fila.

| brazo | confusión 3×3 sumada | recall ausente | recall no_id | recall presente |
|---|---|---|---|---|
| CLAM | [[120, 46, 75], [99, 780, 106], [45, 32, 105]] | 0.498 | 0.792 | **0.577** |
| +Mammoth | [[115, 64, 62], [97, 803, 85], [47, 56, 79]] | 0.477 | **0.815** | **0.434** |

> **Mecanismo = el colapso a la mayoritaria pre-registrado.** Mammoth **sube** el recall de
> `no_identificado` (mayoritaria 70%): 0.792→**0.815**, pero **baja** el de la minoritaria
> `presente`: 0.577→**0.434** (−0.143). La masa total predicha como `no_identificado` pasa de
> **858→923** (de 1408) → mammoth **inclina más hacia la mayoritaria**. Como `balanced_acc`
> pondra las 3 clases por igual, ese sesgo a la mayoritaria es exactamente lo que **deprime
> el bal_acc** del brazo mammoth. Ningún brazo colapsa del todo (ambos predicen las 3
> clases), pero mammoth lo hace **más**.

### 6.4 Sanity de mecanismo (mammoth engaged)

- **`|grad W_0|` / `|grad q|` = 0.0 en el log del brazo mammoth NO indica mammoth
  desconectado.** El grad-logging está **gated a `model_type=="dsmil"`** (`train_dsmil.py`
  L255, L271-273; para `clam`/`clam_mammoth` se hardcodea 0.0 en L239). Es un artefacto de
  logging, no del modelo. Por eso la sanity de grad pre-registrada **no es medible por esta
  vía** para clam_mammoth.
- **Mammoth SÍ está engaged**, confirmado por dos vías independientes: (a) los resultados
  **difieren** materialmente entre brazos (ej. f3 0.630 vs 0.468) — un no-op daría brazos
  idénticos; (b) `tests/test_mammoth_cpu.py` (5/5) verifica el wiring del `MammothPatchEmbed`
  con `keep_slots=False` (preserva los N parches). El bag-loss converge en ambos brazos
  (train_loss ~0.10, clustering_loss ~0.001 a la época 29).

---

## 7. Interpretación (cualitativa, sin gate)

- **¿H1, H0 o regresión?** Ni H1 (mammoth mejora) ni H0-puro (ruido simétrico). El cuadro es
  **H0 en la métrica decisiva con lean a regresión, y regresión leve en la secundaria**:
  Δ bal_acc cae en banda ambigua por magnitud (std > |media|) pero **4/5 folds negativos**;
  Δ AUC es **5/5 negativa** (cumple el criterio formal de regresión, magnitud chica). El
  brazo mammoth **nunca supera** al CLAM en AUC en ningún fold.
- **¿Mammoth corrige o agrava el colapso?** Lo **agrava**: sube recall de la mayoritaria
  `no_identificado` (0.792→0.815) y **hunde** la minoritaria `presente` (0.577→0.434). Es el
  modo de fallo pre-registrado, no su corrección. El fold 3 lo exhibe en extremo (mammoth
  manda 186/197 no_id correctos pero solo 7/37 presente → bAcc 0.468).
- **¿El n grande cambia el cuadro o lo confirma?** Lo **confirma y lo afina**. La 2ª ola se
  lanzó porque invasión es la tarea con más dato (2814 vs ~330-513) y el régimen de eval más
  sano (cada clase n≥36/test → lectura fold-a-fold, **no pooled** como micro/papilar). Ese
  mayor poder estadístico **no rescató** a mammoth: al contrario, **redujo la varianza lo
  suficiente para exponer un signo negativo consistente** (Δ AUC 5/5−) que en las binarias
  hambrientas quedaba ahogado en ruido simétrico. O sea: con la mejor chance de todo el hilo,
  mammoth **no ayuda** — y si algo, perjudica levemente.
- **Coherencia con patrón/microcalc (Hallazgo 11/12).** Encaja con el **efecto gated por
  balance**: el lean+ de mammoth aparecía solo en las 2 tareas más balanceadas (tejido ~58%,
  cribiforme ~49%); invasión es fuertemente desbalanceada (mayoritaria 70%) → mammoth inclina
  hacia la mayoritaria → mild regression. Es el **mismo cierre, una escala más arriba**: el
  cuello es **datos / desbalance / contexto espacial**, no el agregador ni el patch-embed.
- **Sanity de mecanismo:** mammoth está engaged (resultados divergentes + test CPU; ver §6.4);
  el grad=0 del log es artefacto de gating a dsmil, no del modelo.

## 8. Veredicto

**Mammoth NO es palanca para invasión linfática 3-clase.** Bajo política eval B5 (sin gate,
lectura cualitativa): la métrica decisiva `Δ bal_acc = −0.047 ± 0.064` queda en **banda
ambigua por magnitud** pero con **lean negativo consistente** (4/5 folds); la secundaria
`Δ macro-OVR AUC = −0.011 ± 0.005` es **regresión leve consistente** (5/5 folds negativos,
no cruza 0). Mecánicamente, mammoth **agrava el colapso a la mayoritaria** `no_identificado`
(recall 0.792→0.815) a costa de `presente` (0.577→0.434).

Este es el **cierre del hilo mammoth**: 8 tareas (3 microcalc + 4 patrón + 1 invasión 3-clase)
con el mismo harness pareado k=5, y en **ninguna** mammoth es palanca. El lean+ leve aparece
**solo** en las 2 tareas más balanceadas; en las desbalanceadas/hambrientas es nulo o —como
acá, con el n más grande— **mild regression vía colapso a la mayoritaria**. La 2ª ola
confirma con el mejor poder estadístico del hilo que **el cuello es datos / desbalance /
contexto espacial, no la arquitectura del patch-embed** (Hallazgo 12). No hay 3ª ola
planeada para mammoth; los ejes abiertos (magnificación, parches útiles, k=5 en más tasks)
atacan el cuello real = los datos.

## 9. Trazabilidad

- Verdad de campo: `results/obj2_mammoth/invasion_linfatica_vascular_pth/<brazo>_invasion_linfatica_vascular_pth_f<0..4>_20260604_0952_s1/`
  (`test_metrics.json`: balanced_acc + macro-OVR AUC + confusión 3×3 + n; `test_predictions.csv`:
  `y_prob_0..2`; `split_<f>_results.pkl`; `summary.csv`).
- Log del job: `logs/eg_mammoth_patinv_4246.{out,err}`.
- Análisis reproducible (3-clase, stdlib, solo lectura): `scripts/analyze_invasion.py`.
- Slurm: `scripts/run_obj2_mammoth_patron_invasion_kfold.slurm` (`GROUP=invasion`).
- Hipótesis pre-registrada + diseño: `objetivo_2_mammoth_patron_invasion/README.md`.
- README consolidado equipo: `results/README_experimentos_mammoth_environ.md` §4.c.
- *(Nota: en assets para slides, los números de job se omiten y el baseline se rotula
  "Métricas oficiales Environ vX" — [[presentacion-convenciones-benjamin]].)*
