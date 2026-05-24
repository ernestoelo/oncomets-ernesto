# Hipótesis + métrica de éxito — DSMIL sobre los 3 binarios de microcalcificaciones

> **Plantilla post-reunión 22-may-2026.** Esta es la versión vigente del
> argumento (regla 9 — "Argumento antes de código"). Supersede a
> `propuesta_dsmil.md` para el experimento concreto que se va a correr,
> porque `propuesta_dsmil.md` se redactó pre-reunión (4 tareas, métrica
> primaria = AUC, splits canónicos sin definir).
>
> **Instrucciones para el agente que rellena esto:**
>
> 1. Leer los 6 docs listados en el prompt antes de tocar esta plantilla.
> 2. Reemplazar cada `<…>` con el valor concreto. Si decides apartarte de
>    los **seeds sugeridos** (entre paréntesis bajo cada placeholder),
>    justifícalo en una línea.
> 3. NO borrar las secciones que están completas (Contexto, Variables
>    controladas) — ya están cerradas por la reunión.
> 4. Cuando termines de rellenar, **invocar al agente `reviewer`** sobre
>    este archivo. Recién con su OK se puede tocar código de modelo o
>    training.
> 5. Commit en la rama `feature/sprint4-obj3-dsmil-implementacion` con
>    mensaje `docs(B4-obj3): hipótesis + métricas DSMIL pre-implementación`.

---

## Metadatos

- **Fecha de redacción**: 2026-05-24
- **Autor / sesión**: Claude (opus-4.7) en sesión con Ernesto Gamero
- **Branch**: `feature/sprint4-obj3-dsmil-implementacion`
- **Baseline a superar**: job SLURM **4109** (CLAM_MB, B=8, max_epochs 30,
  CONCH 512, 333 slides, `no_identificado` excluido). Detalle en
  `sprints/B4_sprint4/reformulacion_multilabel/resultados.md`.
- **Estado de esta hipótesis**: ☑ borrador · ☐ revisada por `reviewer`
  · ☐ aprobada (cerrar antes de implementar)

---

## Contexto (cerrado por la reunión 22-may — NO editar)

Microcalcificaciones se entrena como **3 tareas binarias** (carcinoma
invasivo, CDIS, tejido no neoplásico), NO como 8 clases (CLAUDE.md
Hallazgo 10). El baseline CLAM_MB sobre los 333 binarios dio:

| Tarea | balanced_acc | umbral predefinido | ¿cumple? |
|---|---|---|---|
| carcinoma invasivo | **0.78** | > 0.60 | ✅ |
| CDIS | 0.59 | > 0.65 | ❌ (apenas sobre 0.50) |
| tejido no neoplásico | 0.58 | > 0.65 | ❌ |

El análisis post-baseline (`reformulacion_multilabel/resultados.md` §c)
diagnosticó que el cuello de botella de CDIS/tejido es **datos** (333
slides → sobreajuste, gap val-test 0.17 en tejido), no formulación.

Este experimento existe para **separar la contribución arquitectónica de
la contribución de datos**: ¿el aggregator dual-stream de DSMIL
(Li et al., CVPR 2021) mueve la aguja sobre el MISMO dataset, o el
plateau es estructural a n=333?

---

## 1. Hipótesis arquitectónica

> Enuncia lo que esperás observar y por qué, en términos del mecanismo
> del modelo y/o de la tarea clínica. **No "DSMIL es mejor" a secas** —
> qué exactamente, sobre qué tarea, y por qué mecánicamente.

**Hipótesis**: el aggregator dual-stream de DSMIL (max-pool de
`c_i = W_0 h_i` para identificar el parche crítico `h_m`, + atención
relacional `β_i = softmax(⟨q_i, q_m⟩/√128)` sobre el resto) modela mejor
que la atención absoluta gated de CLAM (`Attn_Net_Gated`, `α_i`
independiente por parche) las tareas focales donde la señal positiva es
escasa y co-localizada. Sobre features CONCH 512-dim **efectivamente
normalizadas** (norma L2 ≈ 22,65, std 0,01 entre parches y entre slides
— medido en investigación §B.2), el instance scorer lineal `W_0` opera
en su caso fácil. **La ganancia debería ser mayor en carcinoma invasivo
y menor o nula en tejido no neoplásico** — porque el cuello de botella
en tejido es **datos**, no aggregator (gap val-test 0,17 en baseline).

**Mecanismo esperado por tarea**:

- *Carcinoma invasivo* (68 positivos / 7 en test): foco más focal y
  bien delimitado dentro de la WSI → `β_i` colapsa alrededor de `h_m`
  con menos dispersión que el `α_i` gated de CLAM. **Ganancia esperada
  pequeña**: el baseline 0.78 ya está cerca del techo aprendible con
  solo 7 positivos en test; el techo es estadístico, no arquitectónico.
- *CDIS* (121 positivos / 13 en test): focos más extendidos y
  heterogéneos. Si la arquitectura es el cuello de botella, la atención
  relacional podría desambiguar regiones similares; si el cuello es
  datos (mi predicción, basada en el diagnóstico del baseline), DSMIL no
  aporta más allá del ruido.
- *Tejido no neoplásico* (195 positivos / 20 en test): patrón más
  difuso, microcalcificaciones distribuidas por estroma. La noción de
  "parche crítico único" pierde fuerza cuando hay múltiples focos
  equivalentes → DSMIL pierde su ventaja arquitectónica. **Predigo
  plateau** (Δ ≤ +0.02).

---

## 2. Métrica de éxito predefinida

> **Predefinida ANTES de correr**. No se ajusta después de ver los
> números. Sigue el formato del baseline para que la comparación sea
> apples-to-apples.

**Métrica decisiva**: balanced_accuracy (test) + matriz de confusión.
AUC (test) se **reporta pero no decide** — régimen ruidoso a n=7–20
positivos/test (CLAUDE.md Hallazgo 6).

**Umbrales por tarea** (solo Δ vs baseline 4109 — el umbral clínico
absoluto NO es criterio de éxito de este experimento; ver nota abajo):

| Tarea | balanced_acc baseline 4109 | Umbral de éxito (Δ vs baseline) |
|---|---|---|
| carcinoma invasivo | 0.78 | Δ ≥ −0.05 (**guardrail anti-regresión**, NO umbral de éxito) |
| CDIS | 0.59 | Δ ≥ +0.05 |
| tejido no neoplásico | 0.58 | Δ ≥ +0.05 |

**Asimetría de carcinoma — intencional.** Carcinoma ya está en 0.78 con
**7 positivos en test** → cerca del techo aprendible a ese `n`. Exigirle
Δ ≥ +0.05 sería un test injusto de la arquitectura (techo estadístico,
no arquitectónico). Por eso entra como **guardrail anti-regresión**
(no degradar > 0.05), no como umbral de éxito. El éxito arquitectónico
se mide en CDIS/tejido (ver criterio combinado).

**Nota sobre el umbral clínico 0.65** (los del baseline original). NO es
criterio de éxito de este experimento — se **reporta como contexto** en
`resultados.md` pero la decisión arquitectónica se evalúa solo con Δ vs
baseline 4109. La pregunta "¿llegamos al umbral clínico?" se evalúa en
el siguiente experimento (post-`balanced_pth_100` + pérdidas sensibles
al desbalance), donde el eje variable es **datos**, no arquitectura.
Mezclar ambos criterios reabriría la conversación al ver los números —
queda cerrado acá.

**Criterio combinado de éxito del experimento**:

- **Éxito arquitectónico** = carcinoma no degrada (Δ ≥ −0.05) **Y** al
  menos una de CDIS/tejido sube Δ ≥ +0.05 balanced_acc. → la atención
  relacional aportó donde la formulación lo permitía.
- **Plateau confirmado** = carcinoma iguala (|Δ| ≤ 0.03) **Y**
  CDIS/tejido se quedan en Δ ≤ +0.02. → la arquitectura no es el cuello
  de botella; siguiente paso = datos (`balanced_pth_100` cuando exista)
  + posibles pérdidas focal/LDAM (fase distinta, no en este experimento).
- **Fracaso arquitectónico** = carcinoma degrada Δ < −0.05. → el
  aggregator no es transferible a este régimen; descartar DSMIL para
  microcalcificaciones y revisar `alternativas_consideradas.md`.

---

## 3. Dataset y splits (cerrado por la reunión — NO editar)

- **Tareas**: `microcalcificaciones_en_{carcinoma_invasivo,cdis,tejido_no_neoplasico}_pth`
  (las 3 binarias; `no_identificado` excluido en CSV).
- **Splits**: `clam_environ/environ/splits/microcalcificaciones_en_<tejido>_pth_100/`
  (val_frac=test_frac=0.1, seed=1).
- **Slides totales**: 333 (mismo dataset que job 4109; apples-to-apples).
- **Features**: CONCH 512-dim, ya extraídas en
  `clam_environ/environ/features/pt_files/`.
- **NO usar**: `_pth_balance_*` (placeholder hoy = 333), 3072 completo
  (reservado a validación final), privado-solo (77 identificadas →
  inentrenable).

Referencia completa: `sprints/B4_sprint4/dataset_microcalcificaciones.md`.

---

## 4. Variables controladas vs experimental

Para que la comparación aísle el efecto del aggregator, **todo lo demás
se congela**. Cualquier desviación de esta tabla rompe la apples-to-apples.

| Eje | Baseline (job 4109) | Este experimento (DSMIL) | ¿Cambia? |
|---|---|---|---|
| Modelo de bag classifier | `nn.Linear` por clase | `nn.Linear` por clase (de `CLAM_MB`) | NO |
| Aggregator | `Attn_Net_Gated` (lineal) | DSMIL dual-stream | **SÍ — única variable** |
| Features | CONCH 512 | CONCH 512 | NO |
| Bag loss | `--bag_loss ce` | `--bag_loss ce` | NO |
| Instance loss | `--inst_loss svm` (SmoothTop1SVM) | `--inst_loss svm` | NO (default; ver Riesgo R1) |
| `B` | 8 | 8 | NO |
| `bag_weight` | 0.7 (default) | 0.7 | NO |
| `lr` / `drop_out` | 2e-4 / 0.25 | 2e-4 / 0.25 | NO |
| `embed_dim` | 512 | 512 | NO |
| `max_epochs` | 30 | 30 | NO |
| Early stopping | activado | activado | NO |
| Splits | `..._pth_100/` (val=test=0.1, seed=1) | mismos | NO |
| Semillas | 1 (PRELIMINAR) | **1** (PRELIMINAR, igual que baseline) | NO |

**Decisión semillas — cerrada en 1 seed (PRELIMINAR)** para el primer
pase comparativo. Justificación: replica el régimen del baseline 4109
(también 1 seed) → comparación apples-to-apples. **Regla de
escalamiento**: si el resultado cae en banda ambigua (|Δ| < 0.03 en
CDIS o tejido), ampliar a 3 seeds antes de declarar veredicto. Si Δ es
nítido en cualquiera de las 3 direcciones (éxito / plateau / fracaso),
el veredicto se sostiene a 1 seed.

**Nueva variable derivada del aggregator (R1 — cerrada en §5)**: un
único hiperparámetro nuevo `w_max = 0.1` (peso del término L_max sobre
el instance scorer `c` de DSMIL). Valor fijo, no se tunea. Ver §5 R1.

---

## 5. Riesgos identificados (revisar y completar)

- **R1 — Supervisión del Stream 1 de DSMIL (CERRADO en opción B.1.3
  de `investigacion/04_riesgos_y_preguntas_reunion.md` §B.1)**. El
  `argmax` que elige el parche crítico es no diferenciable
  (`DSMIL_official_reference/dsmil.py:52`) → el instance scorer `W_0`
  **no recibe gradiente** si no hay una loss aplicada directamente a
  `c = W_0·h`. Sin esa loss, `W_0` queda en su inicialización aleatoria
  y el "parche crítico" del Stream 2 es un parche arbitrario fijo,
  vaciando de sentido el mecanismo central de DSMIL.

  **Decisión cerrada — opción B.1.3**: mantener
  `--bag_loss ce --inst_loss svm` de CLAM (operando `inst_eval` sobre
  la atención relacional `β` de DSMIL en lugar de la atención gated de
  CLAM) **AGREGAR** un término `L_max` de bajo peso (`w_max = 0.1`,
  cross-entropy sobre el parche de score máximo) que supervise
  directamente a `c`. Loss total:

  ```
  total = bag_weight · L_bag(CE) + (1 − bag_weight) · L_inst(SmoothTop1SVM)
                                 + w_max · L_max(CE sobre c[m])
        = 0.7 · L_bag + 0.3 · L_inst + 0.1 · L_max
  ```

  **Justificación**: aísla mejor el efecto del aggregator que B.1.1
  (reemplazo de inst loss → cambia 2 cosas: aggregator + tipo de inst
  loss) y que B.1.2 (triple loss con 2 hiperparámetros nuevos).
  Introduce **1 hiperparámetro nuevo con valor fijo de paper**
  (`w_max = 0.1`, valor bajo para no dominar el gradiente de
  `bag_classifier` ni de `inst_classifier`), costo aceptable a cambio
  de aislar el efecto del aggregator. No se tunea — si los resultados
  son ambiguos, se ajusta como variante posterior, no en este
  experimento.

- **R2 — Features CONCH vs CTransPath/SimCLR**: DSMIL se diseñó con
  ResNet18+SimCLR. CONCH es un foundation model vision-language de
  patología (Lu et al., *Nature Medicine* 2024), distinto. Sin embargo,
  inspección directa de 6 `.pt` reales (investigación §B.2) confirma
  que CONCH entrega features **efectivamente normalizadas** (norma L2
  ≈ 22,65 ± 0,01) — caso favorable para el instance scorer lineal de
  DSMIL. **Mitigación**: smoke test en CPU + mini-train 1 epoch sobre
  la task más chica (carcinoma invasivo) antes del run completo (§6).
- **R3 — Sobre-confianza en carcinoma**: baseline ya en 0.78 con 7
  positivos en test → techo estadístico cercano. Una mejora pequeña o
  nula NO significa fracaso arquitectónico. Por eso carcinoma entra
  como **guardrail anti-regresión** (Δ ≥ −0.05), no como umbral de
  éxito (§2).
- **R4 — Discrepancias paper↔código (investigación §6, doc 02)**:
  `q` MLP no-lineal (no Linear del paper Ec. 4), escala `/√128` no
  presente en paper Ec. 5, `v = nn.Identity()` por default. Decisión:
  **replicar el código oficial** (`DSMIL_official_reference/dsmil.py`,
  HEAD `80465ed`), no el paper. `passing_v = False` (Identity, como
  default oficial); si los resultados son ambiguos, `passing_v = True`
  queda como variante para smoke test, no para este experimento.
- **R5 — Régimen multi-clase desbalanceado no validado por el paper
  (investigación §A.2, 🔴 documentado)**: DSMIL nunca evaluado fuera de
  binarios balanceados. Mitigado **por construcción**: la integración
  conserva el bag classifier de CLAM (`Linear(512→1)` por clase →
  softmax → CE) — descarta el `Conv1d` de DSMIL que mezclaría clases.
  En este experimento las 3 tareas son **binarias independientes**
  (3 modelos separados, no multi-clase aplastado), lo que además
  esquiva el problema multi-clase del paper. Riesgo residual: enunciar
  explícitamente en `resultados.md` que el régimen es no validado por
  el paper.

---

## 6. Plan de validación pre-entrenamiento (smoke tests)

Antes de lanzar las 3 corridas SLURM, validar en este orden. Cada paso
debe pasar antes del siguiente.

1. **Forward CPU**: bag random `H ∈ R^{200×512}` → wrapper DSMIL devuelve
   `logits ∈ R^{n_classes}` sin NaN, gradiente fluye en
   `loss.backward()`. Test en `clam_testing2/oncomets-ernesto/tests/`.
2. **Forward con datos reales (CPU)**: cargar un `.pt` real de
   `clam_environ/environ/features/pt_files/`, pasarlo por el wrapper, ver
   shapes y rango de outputs.
3. **Mini-train (GPU, 1 epoch)**: lanzar 1 epoch sobre una de las
   binarias con `--max_epochs 1`, ver que `train_loss` decrece y que el
   stream max + el stream attention generan attention scores sanos
   (no todo en un solo parche, no uniformes).
4. **Preflight check**: el `.slurm` final corre el preflight
   (`scripts/preflight_minpatch.py` o análogo) ANTES del `python ...`
   (workaround G).

Resultados de los smoke tests:

- **1. Forward CPU**: ☐ pendiente (post-implementación de `models_dsmil/`).
- **2. Forward con datos reales (CPU)**: ☐ pendiente.
- **3. Mini-train (GPU, 1 epoch)**: ☐ pendiente.
- **4. Preflight check**: ☐ pendiente (adaptar
  `scripts/preflight_minpatch.py` para las 3 tareas binarias antes del
  `.slurm` final).

---

## 7. Acuerdo de cierre (firmar al final)

- ☑ Las secciones 1, 2, 4, 5 están completas (sin `<…>` pendientes).
- ☑ El umbral de "mejora arquitectónica real" en la sección 2 fue
  decidido **antes** de ver cualquier número del experimento.
- ☑ El agente `reviewer` revisó este archivo y dio OK (2026-05-24,
  veredicto: APROBADO, sin observaciones bloqueantes; observación
  única no bloqueante: confirmar al cerrar el experimento que las 4
  casillas de smoke tests §6 quedaron marcadas ANTES del SLURM, no
  después).
- ☑ Este archivo está commiteado en `feature/sprint4-obj3-dsmil-implementacion`
  ANTES de la primera edición de código de modelo (`models_dsmil/`)
  o de cualquier `.slurm` de entrenamiento (commit `af78545`).

> Si alguno de estos checks está vacío al momento de tocar código de
> modelo, el agente `reviewer` bloquea el commit (regla 9 de CLAUDE.md).
