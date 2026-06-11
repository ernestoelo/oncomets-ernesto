# Etapa 1 — PathPT-CONCH en necrosis: pre-registración (regla 9) + diseño de ingeniería

> **Qué es:** el experimento que entrena PathPT (θ_v + θ_t) y lo compara **paired vs
> CLAM** sobre los mismos splits k=5, en la tarea **necrosis binaria** (presente/ausente).
> Es lo que la Etapa 0 (go/no-go) habilitó. **Argumento ANTES de código (regla 9).**
> Este doc se escribe **antes** de tocar `models_pathpt/` o el driver de training; el
> `reviewer` lo evalúa, y recién con su GO + test CPU + OK de Ernesto se lanza el `sbatch`.
>
> Base conceptual (NO re-derivar): [funcionamiento_pathpt.md](funcionamiento_pathpt.md)
> (7 ecuaciones, θ_v/θ_t/pseudo-labels). Resultado habilitante:
> [etapa0_gonogo_necrosis.md](etapa0_gonogo_necrosis.md) §9.
>
> **Encuadre (handoff §0):** esto es **ingeniería de ML** — arquitectura, tensores,
> gradientes, pérdidas, splits, métricas. La validación clínica de los prompts/clases la
> hace **Sebastián vía CAP**, no esta sesión.

---

## 0. Qué habilita esta etapa (y por qué NO es una decisión revisitada)

- **Etapa 0 = LEAN-GO**: necrosis zero-shot CONCH AUC **0.677** (top-5), bal_acc 0.649
  (mejor umbral). Señal real ≫ trivial (0.5) → CONCH **groundea** necrosis; H0 (no
  grounding) descartada. Pero **NO** alcanza la banda GO franca (AUC ≳0.70) → es un
  **FLOOR moderado**, no un techo (§5 de la honestidad del margen).
- **Directiva del supervisor (10-jun):** Sebastián elevó PathPT a **prueba activa**,
  empezar por necrosis. ([[pathpt-testing-necrosis-mitotic]], `progress/current.md` §
  "Dirección VIGENTE 10-jun".)
- **No es regla 9.b (decisión revisitada):** PathPT (frame B) nunca tuvo veredicto NO-GO
  ni quedó en un apéndice "descartado" — fue la recomendación **secundaria** de la
  investigación de retrieval (5-jun) que el supervisor **re-priorizó** el 10-jun, y la
  Etapa 0 la validó con señal real. El evento habilitante es **el go/no-go lean-GO + la
  directiva 10-jun**, citados arriba. (Aun así esta pre-registración cumple regla 9
  estricta: H primaria + alternativa + regresión, métrica + subset + dirección.)

---

## 1. Mecanismo: por qué PathPT *podría* superar a CLAM (y por qué podría no)

CLAM (baseline) es MIL slide-level: atención sobre los **N parches** → 1 vector de slide →
clasificador. Usa **solo visión** y supervisión **slide-level**. PathPT cambia 3 cosas:

1. **Calibra el espacio de texto (θ_t, prompt-tuning CoOp).** El go/no-go mostró un
   `bal_acc@argmax` **degenerado (~0.52–0.58)**: el zero-shot crudo separa por ranking
   (AUC 0.68) pero **no está calibrado** (los logits de "normal" dominan el argmax).
   θ_t aprende la frase latente óptima → **debería** convertir ese 0.68 de ranking en
   una frontera usable. Este es el lever más directo que la Etapa 0 dejó identificado.
2. **Modela contexto espacial (θ_v).** Refina cada parche con su vecindario (conv 3/5/7 +
   transformer sobre la grilla de coords) — dependencias vecino-a-vecino que la atención
   de CLAM **no** modela explícitamente. Necrosis es un hallazgo **regional** (comedonecrosis
   central en un ducto) → el contexto espacial es plausible-mente informativo.
3. **Supervisión tile-level (pseudo-labels + 3 pérdidas).** Aprende **por parche** (no solo
   slide), con un curriculum de confianza que filtra el ruido del profesor CONCH usando el
   label de slide.

**Riesgo honesto (= la hipótesis nula no es de paja):** el mismo sprint cerró que **ni el
agregador (DSMIL, Hallazgo 11) ni el patch-embed (mammoth, Hallazgo 12) son palanca** en
estos regímenes — el cuello fue **datos / desbalance / contexto espacial**, no el método.
PathPT es una intervención de **otra naturaleza** (agrega lenguaje + supervisión tile-level),
pero **puede igualmente chocar contra el techo de datos** (n=396, 83 negativos) y caer en
banda ambigua. El propio paper reporta *"a ceiling imposed by limited data"* a pocos shots.
La pre-registración **no sobre-promete**: el resultado más probable a priori es señal chica;
la pregunta es si es **positiva y consistente en signo**.

---

## 2. Hipótesis pre-registrada (regla 9)

Comparación **PAIRED por fold** sobre los **mismos** splits k=5 (Δ_i = PathPT_i − CLAM_i),
patrón del proyecto ([[patron-paired-comparison-reuso-splits]]): el Δ pareado cancela la
varianza inter-fold y revela señales chicas que el unpaired aplasta.

- **H1 (primaria):** PathPT mejora la clasificación slide-level de necrosis vs CLAM →
  **Δ balanced_acc pareado > 0, consistente en signo** (mayoría de los 5 folds positivos,
  idealmente |media| ≳ std inter-fold). Interpretación: la supervisión tile-level + texto
  calibrado + contexto espacial **aportan** sobre el MIL slide-level.
- **H_alt (nula / ambigua):** el Δ pareado **cruza 0** (std ≳ |media|, signo inconsistente
  entre folds) → PathPT **no aporta** sobre CLAM en este régimen. Lectura: mismo techo de
  datos que Hallazgos 11/12 — el método no es la palanca, lo es el dato. **Resultado
  publicable/presentable, no fracaso** (reencuadre del paper).
- **H_reg (regresión):** Δ pareado **< 0 consistente** (mayoría de folds negativos) →
  PathPT **regresiona** vs CLAM (p. ej. los pseudo-labels ruidosos contaminan el train, o
  el tile-level pierde la integración global que CLAM sí hace). Es un hallazgo informativo
  (acota dónde PathPT-CONCH **no** ayuda), análogo a la regresión leve de mammoth en invasión.

**Métrica + subset + dirección (predefinidos, política B5):**

| | |
|---|---|
| **Subset** | necrosis **binaria** presente vs ausente, `no_identificado` **excluido** (mal definido a nivel tile). n=396 (313 presente / 83 ausente). |
| **Primaria** | **balanced_acc** en el **test** de cada fold; estadístico decisivo = **Δ pareado por fold** (media ± std sobre 5 folds, + signo por fold). |
| **Secundaria** | **AUC binario** (ROC) en test, mismo Δ pareado. **Reportar SIEMPRE junto a balanced_acc** + matriz de confusión + n por clase ([[eval-reporte-auc-y-umbrales-obj6]]). |
| **Dirección esperada si H1** | Δ > 0 en ambas, consistente en signo a través de folds. |
| **Regla de decisión (regla 9.a, interpretada — NO gate mágico)** | Δ>0 consistente y |media|≳std → **PathPT aporta**. Δ cruza 0 / std≳|media| → **ambiguo/null** (techo de datos). Δ<0 consistente → **regresión**. Con n chico mandan **signo + magnitud relativa a la varianza**, no un umbral automático. |

**Regla de operating point tumor-ratio (pre-registrada — H-2 reviewer, evita grado de
libertad post-hoc):** la agregación tile→slide produce un **score continuo** (fracción de
parches predichos `si`, o top-k pooled de la prob por parche). Ese score continuo alimenta el
**AUC directo** (threshold-free). El **umbral** que binariza el score para balanced_acc +
confusión se **selecciona sobre el `val` de cada fold** (Youden / max balanced_acc en val) y
se **aplica congelado al `test`** de ese fold — **nunca** se calibra sobre test. Es la regla
simétrica al `argmax` del clasificador de CLAM (que tampoco mira test). Sin esto, "elegir el
mejor umbral en test" inflaría artificialmente PathPT y rompería el paired.

**Caveat de eval + entregable obligatorio (H-3 reviewer):** con test_frac=0.1 y 83 negativos,
cada test-fold tiene ~8 ausente → balanced_acc del lado negativo es **ruidosa**. Mitigación:
(a) el Δ **pareado** cancela la varianza de sorteo (ambos brazos ven el mismo test); (b) la
**matriz de confusión pooled** sobre los 5 test-folds (≈40 ausente agregados) es **entregable
obligatorio del experimento** (no opcional) — es la única lectura estable de la clase chica.

---

## 3. Decisiones de ingeniería (documentadas ANTES de código — para el reviewer)

### 3.1 Splits — generar MC-CV k=5 del binario necrosis
- **No existe** k=5 de necrosis en `data/splits_kfold/`. El único split de Sebastián
  (`clam_environ/.../splits/carcinoma_ductal_insitu_necrosis_2clases_pth_balance_100`) es
  **single-split, READ-ONLY** y su baseline CLAM aún está en sus PENDIENTES (handoff §10)
  → **genero splits propios** y corro **ambos brazos** sobre ellos (no dependo de la corrida
  de Sebastián).
- **Receta:** misma que `scripts/build_new_tasks_splits.py` (reusa
  `Generic_WSI_Classification_Dataset` + `save_splits` del codebase RO, sin forkearlo):
  k=5, val_frac=test_frac=0.1, seed=1, patient_strat, estratificado → **paired-consistente**
  con microcalc/patrón/invasión.
- **Binarización (el delta vs el generador existente):** el CSV de origen tiene 4 clases
  {`ausente`, `no_identificado`, `presente_central`, `presente_focal`}. Snapshot binario a
  `data/csv_new_tasks/` con `no_identificado` **excluido**, `ausente → "no"` y
  `presente_central ∪ presente_focal → "si"`. **label_dict = `{"no":0, "si":1}`** (misma
  convención que el brazo CLAM `train_dsmil.py` → la matriz de confusión `[[TN,FP],[FN,TP]]`
  se interpreta idéntica en ambos brazos; 0=ausente/negativo, 1=presente/positivo). *(H-1
  reviewer: el doc decía `{ausente,presente}`; el CSV real y el harness usan `no`/`si`.)*
- **Salida:** `data/splits_kfold/cdis_necrosis_2clases_pth_100/splits_{0..4}.csv` (+ `_bool`,
  `_descriptor`).
- **Verificación obligatoria:** `scripts/verify_kfold_splits.py` + cross-check
  `splits_i.csv ⨯ CSV binario` (regla 10: el descriptor puede estar stale) + filtrar slides
  sin `.pt` (las 396 ya tienen features según el go/no-go → drop esperado = 0).

### 3.2 Brazo CLAM (baseline paired) — infra existente, sin código nuevo
- `scripts/train_dsmil.py --model_type clam` sobre el CSV binario + los splits de §3.1,
  `--n_classes 2`, args bendecidos (`--drop_out 0.25 --lr 2e-4 --bag_loss ce --inst_loss svm
  --B 8 --bag_weight 0.7 --embed_dim 512 --early_stopping --weighted_sample`). Produce
  `summary.csv` / `test_metrics.json` / `split_<fold>_results.pkl` / `test_predictions.csv`.

### 3.3 Brazo PathPT — **harness propio** (`models_pathpt/` + `scripts/train_pathpt.py`)
PathPT **no** es un `--model_type` de CLAM (clasifica por parche, usa el encoder de texto,
necesita coords). Diseño del harness:
- **Entrada:** features `.pt` `[N,512]` (RO) **+ coords** del `h5_files/<id>.h5` (RO) para
  ordenar los parches en grilla 2D (θ_v).
- **Espacio contrastivo (CRÍTICO):** las `.pt` cacheadas son `forward_no_head`
  (pre-proyección). Para el coseno texto-imagen (ec. 6) hay que aplicar
  `v_contrastivo = normalize(feat @ proj_contrast)` — `proj_contrast` se saca de CONCH
  (`model.visual.proj_contrast`), igual que en `zeroshot_necrosis_gonogo.py:103`. **Sin esto
  todo el motor de PathPT compara en el espacio equivocado.**
- **θ_v (módulo espacial):** conv residual 3×3/5×5/7×7 (local) + transformer (global) sobre
  la grilla de coords → 1 vector refinado por parche (conserva los N, no colapsa).
- **θ_t (prompt-tuning, CoOp):** K=32 tokens de contexto aprendibles + `[CLASS]`,
  inicializados desde los prompts manuales del go/no-go. Solo se entrena esto y θ_v; CONCH
  (Φ_v, Φ_t) **congelado**.
- **Pseudo-labels tile-level:** reusar la lógica zero-shot de `zeroshot_necrosis_gonogo.py`
  (coseno texto-parche) para generar la etiqueta parcial por parche; retener `normal` o
  consistente-con-slide, descartar el que predice otra clase.
- **Pérdidas (curriculum):** L_labeled (CE balanceada sobre parches con pseudo-label, peso
  1.0) + L_unlabeled (ec. 7, etiqueta parcial, 0.5) + L_pseudo (self-training, 0.1, **desde
  época 10**). 20 épocas, lr 1e-4, warm-up 2.
- **Agregación tile→slide (eval):** "tumor-ratio" (fracción de parches predichos presente) →
  score de slide. **Mismo schema de salida** que `train_dsmil.py` (`summary.csv`,
  `test_metrics.json`, `split_<fold>_results.pkl`, `test_predictions.csv`) → el Δ pareado se
  construye 1:1 contra el brazo CLAM.
- **Containment:** `--results_dir` bajo `clam_testing2/`; GPU solo vía `sbatch` con preflight.

### 3.4 Código de referencia (a clonar bajo containment, fase de implementación)
`github.com/MAGIC-AI4Med/PathPT` → `clam_testing2/PathPT_reference/` (REFERENCE ONLY, **NO**
al PYTHONPATH del codebase de Sebastián, **NO** mezclar con `clam_environ`). Guía la
implementación de θ_v/θ_t/pseudo-labels; el código que corre es **nuestro**, en
`models_pathpt/`.

### 3.5 Prompts
Reusar el pool del go/no-go (`zeroshot_necrosis_gonogo.py` `CLASSNAMES`/`TEMPLATES`, necrosis
v1). La **validación clínica** de la redacción la define **Sebastián/CAP** — no es trabajo de
ingeniería de esta sesión ([[cap-fuente-clases-tareas]]).

---

## 4. Alcance — DECIDIDO: **A (Full PathPT)** (Ernesto, sesión 10-jun)

Tres caminos se evaluaron:

| | Qué entrena | Costo | Qué testea |
|---|---|---|---|
| **A — Full PathPT (ELEGIDO)** | θ_v + θ_t + pseudo-labels + 3 pérdidas | alto | fidelidad al paper; **mejor shot de ganar a CLAM** |
| B — PathPT-min | solo θ_t (prompt-tuning) + tumor-ratio, sin θ_v | bajo | si calibrar el texto ya cierra la brecha |
| C — Fásico | B primero, θ_v si B muestra señal | incremental | lever más barato primero |

**Decisión = A.** Razón: el **módulo espacial θ_v es el diferenciador real de PathPT vs
CLAM** (modela el vecindario entre parches, que la atención de CLAM no captura). Un harness
**full** da el **test paired más decisivo** — si PathPT no le gana a CLAM ni con su
componente más fuerte, el veredicto "el método no es la palanca, lo es el dato" (H_alt) queda
**sólido**, no atribuible a una implementación recortada. Se asume el **mayor costo de
ingeniería** a cambio de un resultado no-ambiguo en su capacidad de discriminar H1 vs H_alt.
(B/C quedan como fallback **solo** si el costo de A se vuelve inviable en implementación —
no como plan A.)

**Criterio de "inviable" (pre-definido — H-4 reviewer, para que la caída a B/C no sea una
decisión post-hoc bajo presión):** se considera A inviable si (i) el módulo θ_v no pasa el
test CPU de shapes / preservación de los N parches tras un esfuerzo acotado de debug, o (ii)
el smoke de 1 época diverge / produce NaN de forma irrecuperable. Solo entonces se cae a B
(θ_t-solo), documentándolo. Mientras A pase el test CPU y el smoke, se sigue con A.

---

## 5. Orden de ejecución (estricto — handoff §6)

1. ✅/⏳ **Splits k=5** del binario (§3.1) + verificación (data prep, no toca training → no
   dispara reviewer; pero queda pre-registrado acá).
2. ⏳ **reviewer** sobre esta pre-registración + diseño (§2–4), **antes** de escribir
   `models_pathpt/` o el driver. Cierra el alcance (A/B/C).
3. ⏳ **Implementar** el harness elegido + **test CPU** (`tests/`, estilo
   `test_mammoth_cpu.py`: wiring, shapes, preserva N parches, smoke 1 época). Clonar la
   referencia (§3.4) en este paso.
4. ⏳ **`sbatch`** (GPU, branch `feat/pathpt-etapa1`, preflight, cortesía single-GPU) —
   paired PathPT vs CLAM. **PARAR antes y confirmar con Ernesto.**

**Se PARA antes de:** el `sbatch`/GPU, el merge a `main`, y cualquier escritura en
`clam_environ/`.

---

## 6. Qué NO afirma / límites
- Un Δ>0 en necrosis **no** generaliza a mitotic (tarea más sutil, go/no-go 0.648) — esa es
  un experimento aparte.
- n chico (396, 83 negativos) → eval ruidosa en la clase chica; el Δ pareado + la confusión
  pooled mitigan, no eliminan.
- PathPT-**CONCH**: un null no condena a PathPT con otro encoder (KEEP), que no tenemos.

---

## 7. ADDENDUM — hallazgos de implementación (post-reviewer, 10-jun)

Surgieron al portar `models_pathpt/` (reviewer ya había dado GO sobre la propuesta). NO
cambian el veredicto ni la hipótesis; refinan la interpretación. Validados con smoke CPU
sobre CONCH real.

1. **Adaptación del pseudo-etiquetado a presencia/ausencia (no subtyping).** La referencia
   PathPT es de *subtyping*: toda slide tiene un subtipo positivo (parche clase 0=Normal,
   1..K=subtipos). Necrosis es **binaria presencia/ausencia**. Adaptación (fiel a la tarea):
   - slide `presente` (y=1): `generate_patch_label` con clase-tumor=1 → parches en {0, 1, −1}.
   - slide `ausente` (y=0): **todos los parches = 0** (no hay necrosis en ninguna parte →
     supervisión negativa fuerte, más informativa que en subtyping).
   Es una adaptación *requerida* por el binario, consistente con el subset pre-registrado.

2. **`candidate_loss` (ec.7, etiqueta parcial) es DEGENERADA en binario.** `−log(p0+pk)` con
   k=1 y softmax de 2 clases = `−log(p0+p1) = −log(1) = 0` **siempre**. ⇒ con 2 clases el
   término "partial-label" es **inerte** (verificado: 0.0000 en el smoke). En binario PathPT
   queda gobernado por `labeled_loss` (parches confiables) + `pseudo_loss` (self-training
   época≥10) + θ_v (espacial) + θ_t (prompt-tuning). El mecanismo central sigue activo; solo
   la componente de curriculum de etiqueta-parcial no aplica al régimen 2-clases. **Implicación
   para H_alt:** si PathPT no aporta, parte de la lectura es que su maquinaria multi-clase se
   reduce en binario — un matiz honesto, no una excusa.

3. **Prompts refinados y anclados en CAP (supersede §3.5 "pool v1").** §3.5 (histórico) decía
   reusar el pool v1 del go/no-go. Tras revisar los protocolos CAP oficiales
   (`papers/Breast.Invasive.Bx_1.2.0.0`, Nota C de necrosis), se construyó un set **v3**
   anclado en el texto literal CAP — clave la **distinción negativa** (necrosis vs *material
   secretorio* "without nuclear debris"). go/no-go CPU: **v3 AUC 0.688 > v1 0.677 > v2 0.649**.
   v3 es el default del driver (`train_pathpt.py`). Bmk PDF = IHC, no aplica a H&E. Provenance:
   `prompts_cap.md`. Sign-off clínico final = Sebastián. (No reescribe §3.5; la registra
   superada.) [[cap-fuente-clases-tareas]]

*Pre-registración (§0–6) escrita ANTES del código de training; §7 = hallazgos durante la
implementación (post-reviewer GO), validados read-only/CPU. El entrenamiento GPU sigue
pendiente: requiere test CPU completo + OK de Ernesto + `sbatch`.*
