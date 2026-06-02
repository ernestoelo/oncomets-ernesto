# Auditoría de coherencia documental del repo — Hallazgos (B5)

> Generado: 2026-06-02. Branch: `chore/audit-coherencia-b5`.
> Misión (handoff `handoff_B5_20260602_090531.md`): dejar el repo coherente
> —sin contradicciones, redundancias ni info stale— para arrancar B5. Sesión
> **documental** (no GPU, no modelo). Job 4229 (mammoth k=5) corre en paralelo,
> NO se toca.
>
> Método: cross-lectura CLAUDE.md ↔ memorias (`~/.claude/.../memory/`) ↔ skills
> (`.claude/skills/`) ↔ agentes (`.claude/agents/`). Por cada ítem: qué dice cada
> fuente, cuál es correcta, dónde debe vivir, y el fix aplicado o diferido.

## Resumen ejecutivo

| # | Hallazgo | Severidad | Acción |
|---|---|---|---|
| A | `CLAUDE.md:19` lista "Colaborador: Eduardo" — renunció 1-jun | stale | **FIX** (roster) |
| B | Memoria `mammoth-investigacion-integracion` dice "falta sbatch + vendorizar" — ambas HECHAS hoy | stale | **FIX** (memoria + MEMORY.md) |
| C | Umbrales rígidos del Obj 6 (Δ≥+0.03 / Δ≤−0.05 / ≥4/5) a retirar como GO/NO-GO (decisión 2-jun) | propagación | **FIX** (3 docs, vía addendum donde es pre-registro) |
| D | "AUC siempre + balanced_acc" (decisión 2-jun) tensiona en lectura con Hallazgo 6 ("macro-AUC solo, nunca") | reconciliación | **FIX** (CLAUDE.md Hallazgo 6) |
| E | Retirar umbral rígido roza regla 9 ("métrica de éxito predefinida") | reconciliación regla dura | **FIX** (CLAUDE.md regla 9 + reviewer.md) |
| F | "Hallazgos vigentes" (11 ítems, CLAUDE.md) solapa con memorias microcalc | redundancia estructural | **DIFERIDO** (recomendación; no surgery sin Ernesto) |
| G | Skills: estructura OK; solape `@mammoth`/`@mil-model-integration` defendible | bajo | sin acción (documentado) |

---

## A. Stale — roster "Colaborador: Eduardo"

- **CLAUDE.md:19** (sección "Quién soy y dónde estoy"): *"Senior: Benjamín.
  Colaborador: Eduardo."*
- **Fuente correcta**: memoria `equipo-arquitecturas-mammoth-longnet` +
  `progress/current.md:13` → Eduardo **renunció el 1-jun-2026**; equipo =
  **Ernesto + Sebastián**.
- **Matiz (NO tocar)**: `CLAUDE.md:634` ("reunión con Sebastián + Eduardo",
  22-may) y `CLAUDE.md:816` ("mammoth heredado de Eduardo") son referencias
  **históricas correctas** — la reunión SÍ ocurrió con Eduardo y mammoth SÍ se
  heredó de él. Solo el **roster del equipo actual** (L19) está stale.
- **`trainer.md:25`** ya dice "Eduardo renunció" → sin fix.
- **Fix**: editar solo CLAUDE.md:19. Dónde vive: CLAUDE.md (roster durable).

## B. Stale — memoria `mammoth-investigacion-integracion`

- La memoria dice *"NO lanzado a GPU"*, *"Pendiente antes de citar resultados:
  vendorizar `mammoth-moe`"*; MEMORY.md la resume con *"falta sbatch +
  vendorizar la dep"*.
- **Realidad (handoff §5)**: **ambas hechas el 2-jun** — job **4229** lanzado
  (ambos brazos, RUNNING) + `mammoth-moe` vendorizado a
  `clam_testing2/MAMMOTH` (pin `fe36d4e`), `pip install -e` reapuntado dentro
  de containment.
- **Fix**: actualizar la memoria (sección PORT + bloque "Pendiente") y la línea
  de MEMORY.md. Dónde vive: la memoria (fact atómico de proyecto).

## C. Propagar — retiro de umbrales rígidos del Obj 6

Decisión de Ernesto (2-jun, fuente de verdad: memoria
`eval-reporte-auc-y-umbrales-obj6`): **retirar como GO/NO-GO automático** los
umbrales `Δ≥+0.03 en ≥2/3` (éxito) y `Δ≤−0.05 con signo consistente ≥4/5`
(regresión). Se reporta el Δ pareado por fold (balanced_acc **y** AUC),
media±std e interpretación cualitativa (consistencia de signo, magnitud de
varianza, si supera el trivial 0.5), sin pass/fail comprometido de antemano.

**Apariciones (grep verificado)** — solo 3 lugares (no en B5/README ni
progress/current.md):

1. `sprints/B4_sprint4/objetivo_6_mammoth/README.md:47-65` — **hipótesis
   PRE-REGISTRADA** (regla 9). **NO se reescriben los números**: borrar un
   pre-registro retroactivamente rompe su integridad. → **ADDENDUM** fechado
   que documenta el cambio de política 2-jun; los umbrales originales quedan
   como registro histórico de lo que se comprometió antes de correr.
2. `sprints/B5_sprint5/objetivo_1_mammoth_run/LANZAMIENTO.md:79-80` — doc
   **operativo** → reescribir el "Veredicto" con la política nueva.
3. `scripts/run_obj6_mammoth_binarias_kfold.slurm:33-34` — header (comentario).
   Editar el comentario es seguro: SLURM copió el script al lanzar el 4229; el
   archivo en disco no afecta al job en curso. → reescribir a "métrica decisiva
   = Δ pareado bal_acc+AUC, interpretación cualitativa".

> `eduardo_snapshot/key_sources/ESTUDIO_papilar_v2.md` también matchea el grep
> pero es un **snapshot vendorizado** (trabajo de Eduardo, congelado) → NO se
> toca.

## D. Reconciliar — "AUC siempre + balanced_acc" vs Hallazgo 6

- Decisión 2-jun #1: **reportar SIEMPRE AUC junto a balanced_acc** (+ confusión
  + n). Nunca una sola métrica.
- `CLAUDE.md:597` (Hallazgo 6) dice *"El macro-AUC solo, nunca."*
- **NO se contradicen**: "AUC **solo**" sigue vetado; la regla nueva es **AUC
  **junto con** balanced_acc, siempre**. El riesgo es de **lectura** (parece
  contradicción). → Redactar la reconciliación en Hallazgo 6: el veto es al AUC
  *aislado*, no a reportar AUC; de hecho ahora es **obligatorio** reportarlo
  junto a balanced_acc + confusión + n.

## E. Reconciliar — retiro de umbral rígido ↔ regla 9 (regla dura)

- `CLAUDE.md:417-418` (regla 9): *"La métrica de éxito está predefinida (qué
  número, sobre qué subset, con qué dirección de cambio)."*
- `CLAUDE.md:433-435` (regla 9.b): exige *"umbrales numéricos antes de tocar
  código"* para decisiones revisitadas.
- `.claude/agents/reviewer.md:53-54` (checklist ítem 1) y `:206-209` ("ejemplo
  de argumento bien formado" cita `Δtest_auc ≥ +0,03`).
- **Tensión**: retirar el GO/NO-GO numérico roza la exigencia de "qué número".
- **Reconciliación** (de la memoria): la métrica predefinida sigue siendo
  obligatoria = **Δ pareado en balanced_acc+AUC, con dirección esperada e
  interpretación de consistencia/varianza**. Lo que se retira es el **pass/fail
  numérico automático** (un Δ≥+0.03 que dispara "éxito" mecánicamente), NO la
  pre-registración de qué se espera y en qué dirección. Pre-registrar "espero
  Δ>0 consistente en signo a través de folds; un Δ<0 consistente sería
  regresión; varianza grande que cruza 0 = ambiguo" **cumple regla 9** sin
  comprometer un umbral mágico.
- **Fix** (aditivo, regla dura → no se reescribe, se aclara): sub-cláusula en
  regla 9 + nota en reviewer.md (checklist ítem 1 y el "ejemplo bien formado").

## F. Redundancia — "Hallazgos vigentes" (CLAUDE.md) ↔ memorias [DIFERIDO]

- `CLAUDE.md` sección "Hallazgos vigentes" (11 ítems, ~Hallazgos 6–11 con
  mucho detalle microcalc) solapa con `microcalc-dataset-decision`,
  `microcalc-fusion-objetivo5`, `microcalc-hierarchical-proposal`.
- **Tensión de diseño**: CLAUDE.md y MEMORY.md se cargan AMBOS en cada sesión →
  el detalle microcalc se paga dos veces en contexto. Pero parte de "Hallazgos
  vigentes" son hechos durables que justifican vivir en CLAUDE.md (régimen de
  eval roto, B no es la palanca, mapeo multi-label→3 binarios).
- **Recomendación** (NO aplicada — es surgery estructural sobre la regla dura
  del control center; requiere criterio de Ernesto): condensar Hallazgos 9–11 a
  1–2 líneas + puntero a la memoria canónica, dejando en CLAUDE.md solo el
  *hecho durable* y delegando el detalle histórico (jobs, números por fold) a la
  memoria/sprint doc. **No borrar contenido único.** Decisión para Ernesto.

## G. Skills y agentes — estructura

- Las 9 skills (`architect`, `csv-audit`, `dev-workflow`, `environ-server`,
  `handoff`, `harness`, `mammoth`, `mil-model-integration`, `slurm-submission`)
  tienen `SKILL.md` con frontmatter `name`/`description` válido.
- `architect` está presente aunque el handoff §1 no la listó — es la skill
  estándar de scaffolding de skills, no un problema.
- **Solape `@mammoth` vs `@mil-model-integration`**: defendible — `mammoth` es
  la instancia específica, `mil-model-integration` la **receta general** de
  integrar cualquier MIL alternativo paired vs CLAM. Jerarquía general↔específico
  clara; sin acción.
- **Agentes** (`reviewer`, `trainer`): `trainer.md` ya refleja equipo post-Eduardo
  y sprint B5. `reviewer.md` se ajusta en el Fix E (reconciliación regla 9).

---

## Plan de fixes (orden de aplicación)

1. **A** — CLAUDE.md:19 roster.
2. **B** — memoria `mammoth-investigacion-integracion` + MEMORY.md.
3. **C** — addendum Obj6 README + reescritura "Veredicto" LANZAMIENTO + header slurm.
4. **D+E** — reconciliación en CLAUDE.md (Hallazgo 6 + regla 9) + reviewer.md.

Commits granulares en `chore/audit-coherencia-b5`. **Push y merge a main los
autoriza Ernesto.** F queda como recomendación documentada.
