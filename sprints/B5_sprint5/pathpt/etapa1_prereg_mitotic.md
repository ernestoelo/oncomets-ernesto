# Etapa 1 — PathPT-CONCH en TASA MITÓTICA (3 clases ordinales): pre-registración (regla 9)

> **Qué es:** entrenar PathPT (θ_v + θ_t) y compararlo **paired vs CLAM** sobre los mismos
> splits k=5 en **tasa mitótica**, formulada como **3 clases ordinales** (`score_1/2/3`,
> Nottingham). Continuación natural de la Etapa 1 necrosis (no es decisión revisitada: mitotic
> siempre fue la 2ª tarea del plan, [[pathpt-testing-necrosis-mitotic]], y su go/no-go ya dio
> lean-GO). **Argumento ANTES de código (regla 9).** El reviewer evalúa este doc + los cambios
> de código antes del `sbatch`.
>
> Base: [funcionamiento_pathpt.md](funcionamiento_pathpt.md), go/no-go
> [etapa0_gonogo_mitotic.md](etapa0_gonogo_mitotic.md) (macro-OVR AUC **0.648**, bal_acc@argmax
> 0.46; trivial 0.333/0.5), y el molde de [etapa1_prereg_necrosis.md](etapa1_prereg_necrosis.md).

---

## 0. Qué habilita esta etapa (NO es regla 9.b)

- **Go/no-go mitotic = LEAN-GO** (10-jun, CPU): macro-OVR AUC 0.648 ≫ trivial 0.5; bal_acc@argmax
  0.46 ≫ trivial 0.333 → CONCH **groundea** densidad mitótica zero-shot pese a ser tarea sutil.
  Es un **FLOOR**, no un techo.
- **Directiva del supervisor (10-jun):** Sebastián elevó PathPT a prueba activa, necrosis → mitotic.
- **No revisitada:** mitotic nunca tuvo NO-GO ni quedó "descartado"; es la 2ª tarea planeada. El
  evento habilitante es el go/no-go lean-GO + la directiva. (Aun así esta pre-registración cumple
  regla 9 estricta.)

---

## 1. Mecanismo: por qué PathPT *podría* superar a CLAM en mitotic (y por qué quizá no)

CLAM (baseline) = MIL slide-level, solo visión, supervisión slide. PathPT agrega: texto calibrado
(θ_t), contexto espacial (θ_v) y **supervisión tile-level multiclase**. **Lo nuevo vs necrosis:**

- Necrosis era **binaria** → la `candidate_loss` (ec.7, etiqueta parcial) quedó **degenerada/inerte**
  (−log(p0+p1)=0). En mitotic (3 clases) **p0+pk < 1 → la `candidate_loss` se activa**: mitotic
  prueba PathPT en su **régimen multiclase completo** (el diferenciador real vs necrosis).
- La tarea es **ordinal**: `score_1<score_2<score_3` mide **densidad** de figuras mitóticas. La
  agregación tile→slide vía top-j pooling captura "cuántos parches de alta densidad hay" — alineado
  con cómo Nottingham cuenta mitosis por área.

**Riesgo honesto (H0 no es de paja):** el go/no-go de mitotic (0.648) es **más débil** que necrosis
(0.677) → CONCH "ve" peor la morfología mitótica (figuras chicas, dependientes de aumento). Y
necrosis ya dio **H_alt** (PathPT no aportó) convergiendo con DSMIL/mammoth (cuello = dato). A priori
el resultado más probable es **otra vez señal chica/ambigua**, ahora con más desbalance ordinal. La
pregunta es si el régimen multiclase + la candidate_loss activa cambian algo.

---

## 2. Hipótesis pre-registrada (regla 9)

Comparación **PAIRED por fold** sobre los mismos splits k=5 (Δ_i = PathPT_i − CLAM_i),
[[patron-paired-comparison-reuso-splits]].

- **H1 (primaria):** PathPT mejora la clasificación ordinal → **Δ balanced_acc pareado > 0,
  consistente en signo** (mayoría de folds +, idealmente |media| ≳ std). Lectura: la supervisión
  tile-level multiclase + texto + contexto aportan sobre el MIL slide-level.
- **H_alt (nula/ambigua):** Δ pareado **cruza 0** (std ≳ |media|, signo inconsistente) → PathPT no
  aporta; mismo techo de datos que necrosis/Hallazgos 11/12. Resultado **presentable**, no fracaso.
- **H_reg (regresión):** Δ pareado **< 0 consistente** → PathPT regresiona (p. ej. el pseudo-etiquetado
  ordinal ruidoso contamina, o el tile-level pierde la integración global de CLAM).

**Métrica + subset + dirección (política B5):**

| | |
|---|---|
| **Subset** | mitotic **3-clase ordinal** `score_1/2/3`, `no_identificado` **excluido** (mal definido a nivel tile). n=1177 (636/287/254). |
| **Primaria** | **balanced_acc** multiclase (argmax) en test; estadístico = **Δ pareado por fold** (media ± std + signo). Trivial = 0.333. |
| **Secundaria** | **macro-OVR AUC** (one-vs-rest, threshold-free) en test, mismo Δ pareado. **Reportar SIEMPRE junto a balanced_acc** + **confusión 3×3** + n por clase ([[eval-reporte-auc-y-umbrales-obj6]]). Trivial AUC = 0.5. |
| **Dirección si H1** | Δ > 0 en ambas, consistente en signo. |
| **Regla de decisión (9.a interpretada — NO gate mágico)** | Δ>0 consistente y |media|≳std → aporta. Δ cruza 0 / std≳|media| → ambiguo/null. Δ<0 consistente → regresión. Mandan **signo + magnitud vs varianza**. |

**Operating point multiclase (pre-registrado):** sin umbral — la predicción de clase es el **argmax**
del score de slide (vector softmax 3-dim top-j pooled), simétrico al argmax del clasificador de CLAM.
El **macro-OVR AUC** se computa sobre el vector de scores continuo (threshold-free). No hay grado de
libertad de umbral que calibrar (a diferencia del binario).

**Caveat de eval + entregable obligatorio:** con test_frac=0.1, los test-folds tienen ~25 (score_2/3)
a ~64 (score_1) por clase → la clase chica (`score_3`, ~25/fold) es ruidosa. Mitigación: (a) Δ
**pareado** cancela la varianza de sorteo; (b) **confusión 3×3 pooled** sobre los 5 test-folds
(~127 score_2, ~127 score_3 agregados) es **entregable obligatorio**.

---

## 3. Decisiones de ingeniería (ANTES de código — para el reviewer)

### 3.1 Formulación ordinal y pseudo-etiquetado (la decisión clave)

PathPT (subtyping) asume **clase 0 = normal/background** presente en toda slide + `tumor_class` = el
subtipo de la slide. Mitotic ordinal **no tiene una clase "normal"** explícita. **Decisión (fiel al
go/no-go validado + clínicamente defendible):**

- **Mapeo:** `label_dict = {"score_1":0, "score_2":1, "score_3":2}`. **Clase 0 = `score_1` = nivel
  basal ordinal.** Justificación a nivel **tile**: una slide `score_1` (baja densidad) está compuesta
  **mayoritariamente de parches sin figuras mitóticas destacables** → etiquetar sus tiles como clase 0
  ("baseline / baja densidad") es una aproximación tile-level razonable, **no** afirma "sin mitosis en
  ninguna parte". Las slides `score_2/3` aportan más tiles de clase 1/2 (mayor densidad).
- **Pseudo-etiquetado (reusa la maquinaria existente, sin reinterpretarla mal):**
  - slide `score_1` (y=0): todos los parches → 0 (baseline). *(misma rama que necrosis y=0; aquí
    significa "baja densidad", no "ausencia".)*
  - slide `score_2/3` (y∈{1,2}): `generate_patch_label(tumor_class=y)` → parches confiables a {0, y},
    resto **candidatos** → **`candidate_loss` ACTIVA** (3 clases, p0+pk<1). Este es el diferenciador
    multiclase vs necrosis.
- **Límite honesto + sign-off:** la interpretación "score_1 = clase 0 basal" es una **decisión de
  ingeniería con supuesto clínico** (que los tiles de slides score_1 son mayoritariamente baja
  densidad). **Sign-off clínico = Sebastián** (igual que los prompts; no bloquea el run de
  ingeniería). Si Sebastián la objeta, se revisa la formulación. El reviewer evalúa este supuesto.

### 3.2 Brazo CLAM (baseline paired) — infra existente
`scripts/train_dsmil.py --model_type clam --n_classes 3` sobre el CSV 3-clase + splits §3.3, args
bendecidos. CLAM_MB es multiclase nativo → no necesita la reinterpretación ordinal (clasifica las 3
clases slide-level directo). Produce el mismo schema (summary/test_metrics/pkl/predictions).

### 3.3 Splits — generar MC-CV k=5 propios
- No reuso los splits single-split de Sebastián (`environ/splits/grado_histologico_mitotic_rate_*`,
  RO). Genero k=5 propios del subset 3-clase (mismo patrón que necrosis): seed 1, val=test=0.1,
  estratificado por las 3 clases, patient_strat. Salida:
  `data/splits_kfold/grado_mitotic_3clases_pth_100/splits_{0..4}.csv`.
- **Verificación:** `verify_kfold_splits.py` + cross-check `splits ⨯ CSV` (regla 10) + drop de slides
  sin `.pt` (esperado 0 — las 1177 ya tienen features según el go/no-go).

### 3.4 Eval multiclase (código NUEVO en train_pathpt.py — el grueso del cambio)
El driver hoy es **binario-only** en el eval (umbral + AUC binario + dump `[[1-s,s]]`). Cambios
**aditivos, gated por `n_classes`** (no tocan el path binario de necrosis):
- `yhat = argmax(score_vector)` para multiclase (sin umbral).
- `macro-OVR AUC = roc_auc_score(y, scores, multi_class="ovr", average="macro")`.
- `confusion_matrix` K×K; dump `prob` = vector softmax [1,K].
- `summary.csv`/`test_metrics.json` con `balanced_acc` + `test_auc`(macro-OVR) + `confusion` + n.

### 3.5 Prompts (del go/no-go validado, anclados en CAP Nottingham)
Reusar los 3 conjuntos del go/no-go (`zeroshot_gonogo.py`, AUC 0.648), anclados en CAP Invasive.Bx
Nota B / Nottingham ([prompts_cap.md](prompts_cap.md) §2):
- `score_1`: low mitotic count · few mitotic figures · rare mitoses
- `score_2`: intermediate mitotic count · occasional mitotic figures
- `score_3`: high mitotic count · frequent mitotic figures · numerous mitoses
Sign-off clínico e iteración (v2/v3) = Sebastián (no bloquea).

---

## 4. Alcance — A (Full PathPT), consistente con necrosis
θ_v + θ_t + pseudo-labels + 3 pérdidas, **con la candidate_loss ahora activa** (3 clases). Mismo
harness (`train_pathpt.py`), mismos hiperparámetros base (20 épocas, lr 1e-4, n_ctx 32). Criterio de
"inviable" → fallback documentado (idéntico a necrosis §4): si θ_v/eval multiclase no pasa test CPU o
el smoke diverge, se reporta y se decide.

---

## 5. Orden de ejecución (estricto)
1. ✅ go/no-go (Etapa 0). 2. ⏳ **esta prereg** + data prep (CSV+splits, no toca training).
3. ⏳ código eval multiclase + prompts + slurm + **test CPU 3-clase**. 4. ⏳ **reviewer** sobre prereg
+ cambios. 5. ⏳ `sbatch` paired (con OK de Ernesto — ya dado para "dejarlo entrenando", condicionado
a reviewer GO + test CPU). **PARAR antes del merge a main sin OK; escribir solo bajo clam_testing2/.**

## 6. Qué NO afirma / límites
- Un resultado en mitotic no generaliza a otras tareas. n chico en score_2/3 → eval ruidosa; Δ pareado
  + confusión pooled mitigan, no eliminan. La interpretación ordinal "score_1=basal" tiene sign-off
  pendiente de Sebastián. PathPT-**CONCH**: un null no condena a PathPT con otro encoder.
