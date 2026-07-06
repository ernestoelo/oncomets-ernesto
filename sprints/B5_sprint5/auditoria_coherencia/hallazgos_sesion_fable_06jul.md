# Auditoría de conocimiento + análisis de mejoras — sesión Fable (6-jul-2026)

> Primera sesión de **Claude Fable 5** en este repo. Encargo de Ernesto: análisis
> profundo del trabajo para encontrar mejoras, documentar contexto valioso,
> registrar hallazgos críticos, auditar la base de conocimiento (`/knowledge-audit`)
> y **proponer mejoras para subir AUC / balanced accuracy** — foco en **mammoth** y
> **CPathAgent** con CLAM como base.
>
> Metodología skill `@knowledge-audit`: **hallazgos primero, fixes después**. Solo
> lectura + edición documental (cero GPU, cero `regla 9`). `squeue` vacío al abrir →
> git libre (workaround H no vigente). Rama `main` (preferencia de Ernesto,
> [[git-trabajar-en-main-por-defecto]]); sin push (default).

---

## 0. Estado del repo (foto al abrir la sesión)

- **B5 está de facto CERRADO**: el deck existe (`papers/presentations/CLAM_Sprint_B5.pptx`),
  la reunión CPathAgent del **jueves 2-jul ya pasó** (hoy es 6-jul), y el cierre de
  trimestre era "fin de junio". El repo está **en frontera de sprint**, pero `progress/current.md`
  sigue enmarcado como **B5-en-curso, pre-reunión**.
- **4 ejes de arquitectura CERRADOS, 0 palancas** (Hallazgos 11-14): agregador/DSMIL,
  patch-embed/mammoth (8 drop-in + 4 keep_slots), lenguaje+tile/PathPT, loss (focal/cb).
  Cuello confirmado y triangulado = **datos / desbalance / contexto espacial**.
- **Hilo mammoth COMPLETO** (12 tareas pareadas k=5) + eje ortogonal de
  **interpretabilidad** ejecutado (OBJ-A, expertos rutean por morfología no por clase).
- **CPathAgent leído y aterrizado**: la palanca portable NO es el agente LMM
  (8×H800 + 278K Gemini + reportes pareados) sino la **fusión de features multi-escala**
  del baseline MIL (Ap. C.1.2) = **Obj 2 magnificación**, dentro de CONCH v1 512.

---

## 1. Tabla resumen de hallazgos

| id | hallazgo | tipo | severidad | acción |
|----|----------|------|-----------|--------|
| **A1** | Palanca **Tier 0 calibración** documentada pero **NUNCA ejecutada** pese a 230 `.pkl` de predicción en disco | oportunidad / gap | **ALTA** | ejecutar (propuesta §3); es la mejora bal-acc más barata y segura |
| **A2** | `progress/current.md` enmarcado B5-en-curso pre-reunión; B5 cerrado + reunión 2-jul pasó | stale (temporal) | media | banner de transición añadido; roll-over a `history.md` = decisión de Ernesto |
| **A3** | CLAUDE.md a **980 líneas / 60 KB**; Hallazgos 11-14 repiten "0 palancas/cuello=datos"; Hallazgo 12 gigante con 4 ADDENDUMs | mantenibilidad / redundancia | media | plan de condensación §2.3 (NO ejecutado — necesita OK; el detalle vive en sprint docs) |
| **A4** | Tensión: skill `@knowledge-audit` fuerza branch `chore/...` vs memoria [[git-trabajar-en-main-por-defecto]] | contradicción (proceso) | baja | cláusula de reconciliación añadida a la skill |
| **A5** | `cheatsheet_reunion_cpathagent.md` sin trackear (valioso, dateado, referenciado) | higiene | baja | commiteado |
| **A6** | `trainer.md` con frontmatter malformado (`---` extra al inicio) | error | baja | corregido |
| **A7** | `trainer.md` §"Contexto del Sprint actual (B5)" quedará stale al abrir el próximo sprint | stale (latente) | baja | anotado; se actualiza al definir el sprint nuevo |

Wikilinks: **0 rotos** (41 memorias, 41 indexadas en MEMORY.md, integridad OK).
Agentes/skills: estructura OK salvo A6. Splits/CSVs: fuera de alcance de esta pasada
documental (los cubre `@csv-audit`).

---

## 2. Detalle de hallazgos y criterio

### A1 — Tier 0 calibración: la palanca barata sobreviviente, nunca ejecutada  ⭐

**Qué dice cada fuente:**
- Memoria [[calibracion-operating-point-palanca-b5]]: "Tier 0 (empezar acá):
  re-umbralizar post-hoc los scores YA guardados... CPU, sin GPU, sin reviewer...
  Demostrable sobre artefactos existentes." Marcada como **la única palanca nueva y
  genuina** ortogonal a los 3 ejes de arquitectura, **reforzada** tras el cierre del loss
  (Tier 1 = H_reg, [[loss-desbalance-eje-c1]]).
- Realidad del disco (verificado esta sesión): **230 `.pkl`** de predicción; cada
  `split_N_results.pkl` es `{slide_id → {prob:(1,n_clases), label}}` (test por fold).
  Checkpoints `s_N_checkpoint.pt` presentes para inferir val. **NO existe** ningún
  `scripts/*calibrat*`, `*threshold*`, ni `resultados` de re-umbralización.

**Veredicto:** la palanca está **descrita pero sin ejecutar**; todos sus insumos están
en disco. Es el **gap de mayor EV y menor costo** de todo el repo para el objetivo del
encargo (subir bal-acc). Propuesta técnica completa en §3.

### A2 — progress/current.md desfasado del calendario real

`progress/current.md` describe el Obj 2/magnificación como "investigación HECHA,
implementación pendiente, para reunión jueves 2-jul". Hoy es 6-jul → la reunión pasó y
**el resultado de la reunión no está en el repo**. El deck B5 ya existe. **Fix aplicado:**
banner de transición al tope de `current.md` (aditivo, no borra el detalle B5) marcando
qué está verificado (deck construido, fecha de reunión pasada) vs desconocido (outcome de
la reunión). El roll-over B5→`history.md` + apertura del sprint nuevo = decisión de Ernesto
(no invento el nombre del sprint ni el outcome de la reunión).

### A3 — CLAUDE.md creció a 980 líneas (plan de condensación, NO ejecutado)

Los Hallazgos 11, 12, 13, 14 cierran el **mismo mensaje** ("0 palancas, cuello=datos") por
4 ejes; el Hallazgo 12 solo tiene ~90 líneas con 4 ADDENDUMs. Todo el detalle numérico ya
vive canónico en `sprints/.../resultados.md` + memorias. **Redundancia ≠ contenido único
en el lugar equivocado**: aquí es redundancia real (el detalle está preservado aguas abajo),
así que es condensable a "titular + punteros" **verificando preservación**. Propuesta:
- Condensar Hallazgos 11-14 a **1 bloque "Eje arquitectura CERRADO (0 palancas)"** de ~8
  líneas con la tabla `eje → veredicto → job → memoria/sprint-doc`, moviendo el detalle
  numérico a los sprint docs (que ya lo tienen).
- Mantener **intactas** las reglas duras (regla 9/9.a/9.b, containment, read-only) y los
  "Hechos validados contra código" (números de línea) — esos NO son redundancia.
- **NO ejecutado esta sesión**: tocar el control-center a mano arriesga las citas cruzadas
  ("ver Hallazgo N"). Requiere OK de Ernesto + una pasada cuidadosa que re-mapee referencias.

### A4 — branch-vs-main en la propia skill de auditoría

`@knowledge-audit` §1 dice "create a NEW branch `chore/audit-coherencia-<sprint>`". La
memoria [[git-trabajar-en-main-por-defecto]] dice trabajar en main por defecto salvo regla
dura (9/9.b). La auditoría es **documental** → no dispara regla 9 → main es válido. **Fix:**
cláusula de una línea en la skill: "auditoría documental puede ir en `main` (default de
Ernesto); branch solo si la auditoría arrastra cambios a modelo/training o si hay job en
curso (workaround H)". Edición concisa ([[edicion-concisa-agentes-skills]]).

### A5/A6/A7 — higiene

- **A5:** cheatsheet commiteado (contenido pedagógico de la reunión, referenciado por
  [[magnificacion-cpathagent-proxima-direccion]]).
- **A6:** `trainer.md` tenía `---\n---\nname:` (frontmatter vacío + cuerpo) → corregido a
  `---\nname:...`. Riesgo real de que el harness no parsee `tools:`/`description:`.
- **A7:** la sección de sprint de `trainer.md` se actualiza al abrir el sprint nuevo
  (ya lo pide su propia nota "Actualizar esta sección al abrir cada sprint nuevo").

---

## 3. Propuesta técnica — mejorar AUC / balanced accuracy (foco del encargo)

**Marco (heredado, correcto):** la arquitectura NO es la palanca (4 ejes, 0 palancas). Las
palancas vivas atacan el **dato / el operating-point**, no el modelo. Escalera por
costo/riesgo:

### Palanca #1 (INMEDIATA, gratis) — Tier 0 calibración post-hoc  ⭐
- **Qué:** para cada tarea con headroom de AUC (invasión AUC≈0.83, necrosis, mitotic
  0.66), elegir **umbral por clase en VAL** (inferencia CPU con `s_N_checkpoint.pt` sobre
  el split de val) y **congelarlo a TEST** (probs ya en los `.pkl`). Métrica: balanced_acc
  y recall de la minoritaria, paired por fold vs el argmax/0.5 actual.
- **Por qué mueve bal-acc:** bajo desbalance el argmax optimiza accuracy = métrica
  equivocada; el AUC (ranking) **sobrevive** aunque el argmax colapse (diagnóstico de
  mitotic job 4326: bal 0.333 exacto / AUC 0.66). Re-umbralizar recupera bal-acc **sin
  tocar el modelo ni agregar señal** — es "leer CLAM mejor", acotado por el AUC.
- **Costo/riesgo:** CPU, minutos, **sin GPU, sin reviewer, sin sbatch** (regla 9 trivial:
  es análisis post-hoc, no toca training). Guardrail: **umbral SIEMPRE en val, nunca en
  test** (test-oracle = solo upper-bound de feasibility, jamás resultado). Pre-registrar
  la expectativa honesta: sube recall minoritaria; puede hundir la mayoritaria (como el
  cb H_reg) → decidir por **balanced_acc neta**, no por una sola clase.
- **Entregable presentable:** curva "bal-acc vs umbral" + matriz de confusión antes/después,
  paired k=5. Hermana del CBIR/D como entregable lúcido ([[retrieval-investigacion-b5]]).

### Palanca #2 (GPU, señal nueva) — Magnificación / fusión multi-escala = Obj 2
- **Qué:** re-extraer CONCH a ≥2 escalas y fusionar por región (promedio, mantiene
  `[N,512]` y CLAM intacto), réplica del baseline MIL de CPathAgent (Ap. C.1.2) dentro de
  CONCH v1. Paired k=5 vs CLAM single-scale, reusando splits ([[patron-paired-comparison-reuso-splits]]).
- **Por qué es distinta de los 4 ejes cerrados:** **inyecta señal nueva** (contexto
  arquitectural: estroma, interfaz tumor-estroma, patrón glandular) que un parche 256 de un
  solo nivel no ve. Los 4 ejes solo reordenaban info de un nivel.
- **Costo/riesgo:** GPU de **extracción** (no de LLM) sobre ~3.072 slides; almacenamiento
  ×2-3 de `.pt`; toca data-pipeline → **regla 9 + reviewer + sbatch**. Pre-registrar lift
  probablemente chico (el paper gana +2.9% vs ABMIL multi-escala; NO rompe el techo de datos).
- **Bloqueadores a resolver con Sebastián (reunión 2-jul):** ¿misma magnificación física
  private/TCGA/HistAI al `level` base? ¿promedio vs multi-token? ¿tareas primero =
  invasión/patrón (contexto = diagnóstico)? costo `conch_fe` por slide.

### Palanca #3 (GPU, medio, no probada) — HistAug (augmentación en espacio de features)
- **Qué:** fabricar más bags sin más slides, on-the-fly, CONCH congelado (HistAug ICCV
  2025, +6.3pts@10%-datos externo, probado con CLAM). Hermanos: RankMix (explícito para
  "imbalanced"), PseMix. Toca data-pipeline → regla 9 + reviewer.
- **Caveat:** verificar que el generador HistAug exista para **CONCH v1 512-dim** (no solo
  UNI/CONCHv1.5). Detalle: [[insuficiencia-datos-ejes-investigacion]].

### Lo que NO hay que volver a intentar (cerrado con argumento)
- **Otra arquitectura de agregador / otro patch-embed / "mammoth #3"** → null garantizado
  (Hallazgos 11/12). Modificar mammoth "más grande / ruteo más expresivo" erosiona su
  bajo-rango → contraproducente con pocos datos.
- **El agente LMM de CPathAgent completo** → fuera de presupuesto (8×H800 + Gemini +
  reportes pareados que la cohorte privada no tiene).

**Orden recomendado:** #1 (esta semana, gratis, resultado demostrable) → #2 (si Sebastián
aprueba Nivel 1 en la reunión) → #3 (si #2 no basta). Ninguno rompe el techo de datos;
todos son honestos sobre eso.

---

## 4. Recomendaciones estructurales (memoria / agentes / skills / instrucciones)

1. **Roll-over de sprint** (Ernesto decide nombre + outcome de la reunión): mover el
   resumen B5 a `history.md`, reescribir `progress/current.md` con el nuevo foco
   (magnificación Obj 2 + interpretabilidad mammoth). Actualizar `trainer.md` §sprint.
2. **Condensar CLAUDE.md** (plan A3): −~120 líneas sin perder una cita, moviendo detalle a
   los sprint docs que ya lo tienen. Es la mayor ganancia de mantenibilidad.
3. **Memoria nueva** de la palanca Tier 0 como *next-action* (creada esta sesión:
   [[calibracion-tier0-pendiente-ejecutar]]) para que ninguna sesión futura la vuelva a
   "descubrir" sin ejecutarla.
4. **Skills sanas**: `@mammoth`, `@mil-model-integration`, `@slurm-submission` vigentes;
   `@knowledge-audit` recibió la cláusula branch/main (A4).
