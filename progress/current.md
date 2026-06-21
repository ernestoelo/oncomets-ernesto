# progress/current.md

> Estado vivo del sprint actual. Es un **snapshot** — se reemplaza al avanzar
> el sprint. Al cerrar el sprint, el resumen pasa a `history.md`.

---

## Sprint actual: B5 / Sprint 5 — cierre de trimestre

**Abierto 1-jun-2026.** Sprint de la **recta final del trimestre**: Benjamín
(jefe) vuelve ~21-jun, a fin de mes se cierra el trimestre y **esta presentación
decide la continuidad de Ernesto** ([[sprint-cierre-trimestre-junio]]). Equipo =
**Ernesto + Sebastián** (Eduardo renunció el 1-jun). Consigna de Benjamín:
avanzar **más rápido** y **lucirse**. Base del deck: B4 cerrado
(`papers/presentations/CLAM_Sprint_B4.pdf`, legacy local).

### Plan del sprint

Detalle y argumentos en `sprints/B5_sprint5/README.md`. Objetivos priorizados
según los pedidos de Benjamín (1-jun):

| # | Objetivo | Estado |
|---|---|---|
| 1 | **mammoth k=5 paired** sobre las 3 binarias (correr + analizar) | **COMPLETADO** (job 4229, analizado): mammoth NO es palanca en microcalc (cuello=datos). `objetivo_1_mammoth_run/resultados.md` |
| 1b | **mammoth en patrón arquitectónico (4 binarias) + invasión (3-clase)** k=5 | **COMPLETADO** — PATRÓN (job 4243, 40 runs, 4-jun 01:33) + INVASIÓN (job 4246, 10 runs, 5-jun 06:18): mammoth NO es palanca en ninguna (lean+ leve solo en cribiforme balanceada; invasión = regresión leve consistente vía colapso a mayoritaria). `objetivo_2_mammoth_patron_invasion/{resultados.md,resultados_invasion.md}`. **Cierra el hilo mammoth drop-in (8 tareas, 0 palancas)** — extendido luego por Obj 3 keep_slots (+4 tareas, también 0 palancas; ver sección Obj 3 abajo). |
| 2 | **Magnificación**: investigar (papers) ANTES de implementar | pendiente |
| 3 | **k=5 folds** en más tasks débiles (no single-split) | pendiente |
| 4 | **Parches/slides útiles**: selección de los que aportan al train | pendiente |
| 5 | **Pregunta CAP**: ¿1 de las 3 binarias positiva = cáncer c/microcalc? | pendiente (research clínico) |
| 6 | **PCGrad** (gradient surgery, heredado de Eduardo): eje separado | pendiente |

> DSMIL: "entenderlo mejor", menor prioridad (cerrado para microcalc, ver B4).

### Estado inmediato (act. 5-jun, invasión cerrada → hilo mammoth cerrado)

- **mammoth microcalc (Obj 1 de B5) — COMPLETADO Y ANALIZADO**: job **4229**
  (3 binarias × k=5 × 2 brazos, ~9h40m). **Veredicto**: mammoth NO es palanca
  consistente en microcalc (tejido +0.049, cdis −0.086, carcinoma nulo; std >
  |media| → banda ambigua H0; cuello = datos). Brazo CLAM reproduce Fase 0 al 3er
  decimal. Detalle: `sprints/B5_sprint5/objetivo_1_mammoth_run/resultados.md`.
- **mammoth patrón (Obj 1b, `objetivo_2_mammoth_patron_invasion/`) — COMPLETADO Y
  ANALIZADO**: job **4243** (4 binarias × k=5 × 2 brazos = 40 runs), lanzado 3-jun
  desde `main` sin cambiar de rama → **cerró limpio 4-jun 01:33** (sin el crash del
  4241). **Veredicto**: mammoth NO es palanca en patrón tampoco — lean+ leve solo en
  **cribiforme** (Δbal +0.044±0.048, 4+/1−, la única binaria balanceada ~1:1); **nulo**
  en solido (−0.014, desbalance 3:1) y en micropapilar/papilar (régimen ciego, 3 pos/test
  → pooled: ambos brazos casi no detectan, TP global 4/15 y 2/15). **Hallazgo crítico**:
  cruzando Obj1+Obj2 (7 binarias), el lean+ de mammoth aparece SOLO en las 2 tareas más
  balanceadas (tejido ~58%, cribiforme ~49%) → el resultado lo gobierna el **régimen de
  datos**, no el agregador/patch-embed. Refuerza cuello = datos/desbalance/contexto
  espacial. Detalle: `objetivo_2_mammoth_patron_invasion/resultados.md`; README
  consolidado `results/README_experimentos_mammoth_environ.md` §4.b.
  - El intento previo (job **4241**, 2-jun) completó 1/40 y murió porque un `git checkout`
    en el working-tree COMPARTIDO borró `data/csv_new_tasks/` → `FileNotFoundError` en fold
    1 ([[working-tree-compartido-job-en-curso]], workaround H). Parcial segregado en
    `results/failed_runs/4241_*` (NO usar).
  - **Invasión linfática 3-clase (GROUP=invasion) — COMPLETADA Y ANALIZADA**: job **4246**
    (3-clase × k=5 × 2 brazos = 10 runs, cerró 5-jun 06:18). **Veredicto**: mammoth tampoco
    es palanca — Δ bal_acc −0.047 ± 0.064 (banda ambigua, lean negativo 4/5) y **regresión
    leve consistente en AUC** (−0.011 ± 0.005, 5/5 folds−), por **mayor colapso a la
    mayoritaria** `no_identificado` (recall presente 0.577→0.434). El n más grande del hilo
    (2814) y el eval más sano no rescataron a mammoth → confirma cuello = datos. Detalle:
    `objetivo_2_mammoth_patron_invasion/resultados_invasion.md` (análisis
    `scripts/analyze_invasion.py`; figuras en `figuras/slide_assets/`). **→ Cierra el hilo
    mammoth: 8 tareas pareadas k=5, 0 palancas.** Próximo foco = ejes de datos (magnificación,
    parches útiles), no más swaps de modelo.
  > Nota de numeración: la tabla del plan numera por pedido de Benjamín (1=mammoth
  > microcalc, 2=magnificación...). El dir `objetivo_2_mammoth_patron_invasion` es la
  > **continuación del hilo mammoth**, NO el "Objetivo 2 = magnificación" del plan.
- **Vendorizado HECHO**: `mammoth-moe` en `clam_testing2/MAMMOTH` (pin `fe36d4e`),
  `pip install -e` reapuntado → `import mammoth` resuelve dentro de containment.
- **GPU**: job ajeno `sgaete` (feature extraction, job 4242) corría al cierre — cortesía.

### Nueva dirección (5-jun): investigación retrieval (fase argumento)

Cerrado el hilo mammoth, Ernesto propuso explorar **retrieval**. Investigación
**sin código/GPU** (regla 9): deliverable
`sprints/B5_sprint5/investigacion_retrieval/analisis.md` (4 variantes A/B/C/D,
2 papers leídos). **Recomendación**: **D (CBIR, buscador de slides parecidas)**
primario para la presentación (bajo riesgo, usa CONCH as-is, NO entrena, CPU) +
**B (few-shot estilo PathPT)** secundario para research. **A descartado**
(mammoth #2); **C = el Eje B "parches útiles" (Obj 4)** ya en plan. Los 2 papers
(PathPT, Zero-Shot Retrieval) **confirman cuello=datos** (*"ceiling imposed by
limited data"*). Memoria [[retrieval-investigacion-b5]]. Próximo paso si Ernesto
elige D: pre-registración regla 9 + branch + reviewer (otra sesión).

### Obj 3 CERRADO (21-jun): mammoth keep_slots=True + slot_dropout — matriz completa, 0 palancas

**PathPT CERRADO en diagnóstico (11-jun)** — necrosis H_alt + mitotic colapso de formulación +
microcalc NO-GO → cuello = CONCH/datos, no el método (CLAUDE.md Hallazgo 13,
[[pathpt-testing-necrosis-mitotic]]). El frame PathPT ya no es trabajo activo.

**Trabajo activo:** Obj 3 reabre el patch-embed de mammoth con una **variante NO testeada**
(`keep_slots=True` = cuello de botella de 300 slot-tokens en vez de drop-in N→N; + el arg nuevo
`--mammoth_slot_dropout`). El hilo mammoth estaba "cerrado" para la config drop-in (`keep_slots=False`,
8 tareas, 0 palancas, Hallazgo 12) — esto **NO lo contradice**: prueba un punto NO testeado del espacio
de config, apuntado al modo de falla del 4246 (colapso a la mayoritaria). **Reviewer GO-con-obs** (NO
9.b estricta sino variante no testeada). Gobernanza: Ernesto asumió el gate (no molestar a Sebastián;
maximizar mammoth = prioridad de Benjamín; co-firma recomendable a posteriori).

- **Estado (act. 21-jun):** pre-reg + reviewer GO + código + test CPU 7/7 sobre branch
  `feat/mammoth-keepslots`. **Jobs 4387 (invasión+tejido) + 4400 (carcinoma+cdis) CERRADOS** →
  **matriz completa 4 brazos × 4 tareas, 5/5** (verificado `scripts/analyze_obj3.py`). 4400 fue la
  **extensión §8** (expansión de alcance por completitud/defensibilidad, no 9.b; expectativa honesta
  pre-reg = probable null en desbalanceadas → CONFIRMADA).
- **Resultado FINAL (4/4 tareas, `resultados.md` §0 FINAL + §6.3):** `keep_slots=True` **NO es palanca
  vs CLAM en NINGUNA tarea** (C2 Δ bAcc: invasión −0.031, carcinoma −0.020, cdis −0.023, tejido
  +0.046-ruido → 0/4 supera a CLAM) → **refuerza Hallazgo 12**. **Matiz mecanístico nuevo (3/4):** el
  cuello de botella de slots **mitiga consistentemente su propio colapso a la mayoritaria** (gap de
  recall de la minoritaria a favor: invasión `presente` 0.434→0.516, carcinoma `si` 0.286→0.314, cdis
  `si` 0.279→0.443 — supera a CLAM pero a costa de la mayoritaria) **pero insuficiente para superar al
  baseline**. `slot_dropout` **descartado** (net-negativo en las 4). **ADDENDUM Hallazgo 12 CERRADO**
  en CLAUDE.md + memoria + MEMORY.md. **Hilo mammoth completo: 8 drop-in + 4 keep_slots = 0 palancas.**
- **`val_auc=nan` en invasión (3-clase) = normal**, no bug (baseline 4246 igual; checkpoint por val_loss). Ver CLAUDE.md core_utils.
- **Workaround H ya NO vigente** (4400 cerró, cola vacía) — branch/edición libres de nuevo.
  Pendiente: commit de docs (resultados.md §6 + cierres) en `feat/mammoth-keepslots`; push lo hace Ernesto.
- Pre-reg + detalle: `sprints/B5_sprint5/objetivo_3_mammoth_keepslots/prereg.md` (§8 = extensión).

### Dirección VIGENTE (10-jun): PathPT (frame B) pasa a PRUEBA ACTIVA

**Reunión 10-jun con Sebastián** (supersede el framing del 5-jun): validó PathPT
como interesante/viable y pidió **PROBARLO ya** — empezar por **necrosis**, luego
**mitotic rate**, generando los **embeddings de texto CONCH** de cada tarea. Esto
**eleva B** de "research del trimestre siguiente" a **candidato activo en prueba**.
(El CBIR/D no se descarta, pero ya no es el foco primario.)

- **Tarea de Ernesto al lunes:** presentación del **funcionamiento/arquitectura de
  PathPT** (con diagramas) + **tablas resumen mammoth** (slides por clase, clases,
  tarea, métricas) + **diagrama copia de `Diagrama_CLAM.pptx`** con el bloque de capa
  lineal reemplazado por **mammoth**. Restricciones: **sin nombres** (Sebastián),
  **sin proceso de entrenamiento**, genérico/claro/preciso
  ([[presentacion-convenciones-benjamin]]).
- **Base de estudio registrada:** `sprints/B5_sprint5/pathpt/funcionamiento_pathpt.md`
  (arquitectura + 7 ecuaciones + relación CONCH↔PathPT↔CLAM + pseudo-labels + verdad de
  campo necrosis/mitotic + go/no-go). Memoria [[pathpt-testing-necrosis-mitotic]].
- **Caveat CONCH≠KEEP refinado** (lectura completa del paper, audit 10-jun, hallazgo O):
  PathPT-CONCH gana 9/11 benchmarks vs MIL; CONCH habilita el loop de pseudo-labels;
  el fallo es específico de EBRAINS (30 subtipos). En nuestras 2–4 clases CONCH está en
  su régimen favorable. Riesgo real = grounding zero-shot de NUESTRA morfología (no
  testeado) → **go/no-go barato = etiquetado zero-shot CPU antes de invertir GPU**.
- **PathPT toca training** (entrena `θ_v` + `θ_t`, usa GPU) → **regla 9 + reviewer +
  `sbatch`** aplican (≠ el CBIR que era CPU sin entrenar).
- **Contexto del árbol compartido:** Sebastián está corriendo **mammoth sobre las
  mismas tareas** (necrosis, mitotic; ver notas ajenas sin commitear en el README
  mammoth) → habrá baselines CLAM/mammoth para la comparación **paired**.

### Etapa 1 PathPT (necrosis) — IMPLEMENTADA + validada CPU, lista para lanzar (10-jun)

Branch `feat/pathpt-etapa1` (mergeada a main este turno). Pre-registración + reviewer
**GO**, alcance **A (Full PathPT)**. Todo el código escrito y validado **sin GPU**:
- `models_pathpt/` (θ_v + θ_t + 3 pérdidas, port fiel de PathPT pin 0ab7f1b), `scripts/train_pathpt.py`
  (driver propio), `tests/test_pathpt_cpu.py` **5/5 PASA**, smoke end-to-end exit 0, `.slurm`
  paired con 3 gates de preflight. Splits k=5 propios `cdis_necrosis_2clases_pth_100` (396, 83/313).
- **Prompts anclados en CAP** (Invasive.Bx Nota C): v3 AUC 0.688 > v1 0.677 (go/no-go CPU).
  Provenance `sprints/B5_sprint5/pathpt/prompts_cap.md`; Bmk PDF = IHC, no aplica.
- **Dep**: `nystrom_attention`+`einops` en `clam_testing2/.pylibs` (torch de clam_latest).
- **ÚNICO PENDIENTE = GPU**: `sbatch scripts/run_pathpt_etapa1_necrosis_kfold.slurm` (paired CLAM+PathPT
  k=5). Correr desde **main**, verificar `squeue` (cortesía single-GPU). [[pathpt-testing-necrosis-mitotic]]

### Reglas que gobiernan el sprint (de CLAUDE.md)

- Argumento antes de código (regla 9) + reviewer antes de commitear modelo/training.
- Comparación PAIRED por reuso de splits ([[patron-paired-comparison-reuso-splits]]).
- Entregables: notas concisas, **sin números de job**, baselines como "Environ
  vX" ([[presentacion-convenciones-benjamin]]).
- GPU solo vía `sbatch`; cortesía single-GPU; preflight obligatorio.
