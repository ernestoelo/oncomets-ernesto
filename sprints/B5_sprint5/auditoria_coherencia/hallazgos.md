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
| F | "Hallazgos vigentes" (11 ítems, CLAUDE.md) solapa con memorias microcalc | redundancia estructural | **FIX** (condensados H9/10/11; aprobado por Ernesto) |
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

## F. Redundancia — "Hallazgos vigentes" (CLAUDE.md) ↔ memorias [APLICADO]

- `CLAUDE.md` sección "Hallazgos vigentes" (11 ítems) solapaba con
  `microcalc-dataset-decision`, `microcalc-fusion-objetivo5`,
  `microcalc-hierarchical-proposal`.
- **Tensión de diseño**: CLAUDE.md y MEMORY.md se cargan AMBOS en cada sesión →
  el detalle microcalc se pagaba dos veces en contexto.
- **Aplicado** (Ernesto aprobó "aplica todas las recomendaciones"): condensados
  **H9, H10, H11** (~121 → ~40 líneas). Antes de condensar, **verifiqué que cada
  pieza esté preservada en su memoria canónica**:
  - H10 (reunión 22-may + reglas de dataset) → cubierto íntegro por
    `microcalc-dataset-decision` (cuentas por cohorte, ~548 vs 333, `_balance`,
    `no_identificado`, mapeo multi-label).
  - H11 (CLAM×DSMIL cerrado) → cubierto con MÁS detalle por
    `microcalc-fusion-objetivo5` (todos los Δ por tejido, jobs 4170–4179,
    rótulo MC-CV).
  - H9 (reformulación = trabajo de Sebastián) → cubierto; además sus números
    single-split (job 4109) quedaron **superseded** por los MC-CV → se marcan
    como tales en vez de citarlos como vigentes.
- **Contenido único preservado en CLAUDE.md** (no estaba en memorias): "early
  stopping `stop_epoch=50` hardcoded", pedido de Sebastián (escala/citoplasma →
  Obj 2 B5). Se mantuvieron inline condensados.
- **Numeración preservada** (H10=dataset, H11=arquitectura) para no romper los
  cross-refs internos ("ver Hallazgo 10" en H7; "Hallazgo 11" en H9) ni la
  referencia externa de `microcalc-dataset-decision` ("Hallazgo 10 de CLAUDE.md").

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

5. **F** — condensar Hallazgos 9/10/11 de CLAUDE.md (verificando preservación en
   memorias canónicas antes de recortar).

Commits granulares en `chore/audit-coherencia-b5`. **Push y merge a main los
autoriza Ernesto.** Todas las recomendaciones (A–F) quedaron aplicadas; G no
requería acción.

---

# Pasada incremental — 5-jun-2026 (post-cierre mammoth + apertura retrieval)

> Generado: 2026-06-05. Contexto: hilo mammoth CERRADO (8 tareas, 0 palancas);
> nueva dirección de investigación = **retrieval** (deliverable
> `sprints/B5_sprint5/investigacion_retrieval/analisis.md`). Misión del handoff
> `handoff_B5_20260605_102938.md` paso 1: coherencia post-mammoth + **capturar**
> la dirección retrieval como conocimiento descubrible. Sesión documental (no
> GPU — `squeue` vacío; no modelo). Rama al correr: `main` (en sync con origin).

## Resumen ejecutivo (pasada 5-jun)

| # | Hallazgo | Severidad | Acción |
|---|---|---|---|
| H | Conteo de features CONCH **2935** en 4 fuentes canónicas, pero el conteo vivo es **3013** `.pt` (y 3013 `.h5`) — el dataset creció desde el recon (19-may) | stale/error | **FIX** (CLAUDE.md + skill `@environ-server` + `trainer.md` + `docs/environ_server.md`; B4 recon = histórico, NO se toca) |
| I | Dirección **retrieval** (variantes A/B/C/D, recomendación D primario / B secundario) sin captura descubrible: no hay memoria, `progress/current.md` no la menciona | captura | **FIX** (nueva memoria `retrieval-investigacion-b5` + línea en `MEMORY.md` + nota en `progress/current.md`) |
| J | Cierre mammoth/invasión: coherente entre `progress/current.md`, CLAUDE.md Hallazgo 12 y memoria `mammoth-investigacion-integracion` | verificado, sin issue | sin acción (el handoff lo predijo: "el cierre de invasión ya se auditó") |

---

## H. Stale/error — conteo de features CONCH (2935 → 3013)

**Qué dice cada fuente** (todas afirman **2935**):
- `CLAUDE.md:288-289` (estructura de datos: `features/pt_files/` y `h5_files/`).
- `.claude/skills/environ-server/SKILL.md:49,50,78`.
- `.claude/agents/trainer.md:82,169` (incl. el comando de verificación con `# 2935`).
- `docs/environ_server.md:63`.
- `sprints/B4_sprint4/reconocimiento_entorno.md:167,168,181,205,307` — **HISTÓRICO**
  (snapshot ddel recon 19-may-2026). **NO se edita**: era verdad esa fecha; reescribir
  un doc-fecha rompería su valor de registro (criterio "preserve pre-registration").

**Verdad de campo (5-jun-2026):**
```
ls .../environ/features/pt_files/*.pt | wc -l  → 3013
ls .../environ/features/h5_files/*.h5  | wc -l  → 3013
```
**Cuál es correcta:** 3013 (conteo vivo, pt y h5 consistentes). El dataset
**creció** +78 slides desde el recon. No es un error de medición; es drift de un
dataset compartido y vivo.

**Fix (durable, no hardcodear un número que vuelve a quedar stale):** en las
fuentes canónicas, poner **~3013 (live 5-jun-2026; el dataset crece — verificar
con `ls … | wc -l`)**. Severidad baja: lo que define qué slides se usan es el
**split**, no el conteo crudo; pero la cifra canónica debe reflejar la realidad.

## I. Captura — dirección retrieval como conocimiento descubrible

**Gap:** la investigación retrieval (4 variantes, 2 papers leídos, recomendación
razonada) vive solo en `investigacion_retrieval/analisis.md`. Sin memoria ni
puntero en `progress/current.md`, una sesión futura no la "descubre".

**Fix:** (a) memoria `retrieval-investigacion-b5` (type project) con el veredicto
+ punteros; (b) línea en `MEMORY.md`; (c) nota en `progress/current.md`
ligándola al Eje B (parches útiles = variante C) y marcando D como entregable
lucible. Captura análoga a la de CAP (Hallazgo cap-fuente-clases-tareas).

## J. Verificado coherente — cierre mammoth/invasión (sin acción)

Cross-lectura: `progress/current.md` (Obj 1/1b COMPLETADOS, "8 tareas, 0
palancas"), CLAUDE.md Hallazgo 12 (mismo veredicto + números invasión), memoria
`mammoth-investigacion-integracion` ("HILO MAMMOTH CERRADO"). **Sin
contradicción** — el cierre ya estaba auditado (commit `0dd32f4`). Confirmado.

## Plan de fixes (pasada 5-jun)

1. **H** — reconciliar conteo en CLAUDE.md + `@environ-server` + `trainer.md` +
   `docs/environ_server.md` (B4 recon NO se toca).
2. **I** — memoria `retrieval-investigacion-b5` + `MEMORY.md` + `progress/current.md`.

Edits aplicados en el working-tree (rama `main`). **Commit / branch destino:
los decide Ernesto** (default CLAUDE.md = commits locales, push lo hace Ernesto;
y la rama no se asume — se pregunta).

---

# Pasada incremental — 8-jun-2026 (reunión Sebastián: registrar resultados en clam_testing)

> Generado: 2026-06-08. Contexto: tras reunión con Sebastián, pedido de **registrar los
> resultados k=5 (media + mejor AUC por tarea, ruta de split, dataset) en un README de
> `clam_testing/`**. Al ejecutarlo emergió que la premisa "carpeta ex-Eduardo" no calza con
> el estado real del árbol. Sesión documental + un write autorizado a `clam_testing/`
> (excepción a reglas duras, ver L). Rama al correr: `main` (en sync con origin tras
> `git fetch`). Jobs vivos al momento (`squeue`): 4291 (scontrer), 4296 (gvenegas) RUNNING;
> 4297 (capstone), 4298 (**sgaete** mammoth_) PENDING — **no se tocan**; los edits son
> markdown en MI repo + un README nuevo (untracked) en clam_testing → no afectan inputs de
> ningún job ni cambian de rama (workaround H respetado).

## Resumen ejecutivo (pasada 8-jun)

| # | Hallazgo | Severidad | Acción |
|---|---|---|---|
| K | `clam_testing/` descrito como "workspace de **OTRA persona**" (CLAUDE.md:54 + regla 3:417) y como "carpeta de Eduardo… heredada" (memoria `equipo-arquitecturas-mammoth-longnet:14`). Realidad 8-jun: workspace **COMPARTIDO y ACTIVO** — owner `sdonoso`; **`sgaete` (Sebastián, supervisor) corre ahí HOY** (`run_mammoth_5fold_balanced.slurm` 17:48, jobs 4276/4277/4278 + 4298 PENDING), también `jbarraza`. El legacy MAMMOTH/ de Eduardo (may-8) sigue, pero la carpeta NO está durmiente. | stale/error | **FIX** (CLAUDE.md:54 + regla 3 + memoria equipo) |
| L | Escritura en `clam_testing/` (creado `README.md` con resultados k=5) **autorizada explícitamente por Sebastián** — excepción quirúrgica a reglas duras 3/4 + containment, **sin documentar**. Sin nota, una sesión futura o rechaza un pedido legítimo del supervisor, o (peor) lee "ya escribimos ahí" y trata clam_testing como libremente escribible. | excepción regla dura | **FIX aditivo** (sub-cláusula en regla 3, espejo del precedente `~/.ssh`; memoria nueva) |
| M | Tras el write hay **dos** READMEs de resultados en clam_testing: el puntero stub `README_experimentos_mammoth_environ.md` ("MOVIDO — editar en repo") y el `README.md` nuevo. Ambos declaran que la **fuente canónica/versionada es el doc del repo** (`results/README_experimentos_mammoth_environ.md`). | redundancia gestionada | sin fix (nota): canónico = repo; copias en clam_testing son derivadas/conveniencia. |

---

## K. Stale/error — `clam_testing/` no es "workspace de otra persona" durmiente

**Qué dice cada fuente:**
- `CLAUDE.md:54` (Paths críticos): *"clam_testing/ ← workspace de OTRA persona. NO entrar a escribir."*
- `CLAUDE.md:417` (regla 3): *"NO entrar a escribir en clam_testing/ — workspace de otra persona."*
- Memoria `equipo-arquitecturas-mammoth-longnet:14`: *"clam_testing/ (carpeta de Eduardo, antes 'otra persona', ahora heredada)."*

**Verdad de campo (8-jun-2026, `ls -la` + `squeue`):** owner `sdonoso`; archivos y jobs
**activos** de `sgaete` (Sebastián Gaete — supervisor: `run_mammoth_5fold_balanced.slurm`
tocado 17:48 hoy, `results_mammoth_5fold_balanced/`, jobs 4276/4277/4278, **4298 PENDING**)
y de `jbarraza` (`analyze_*.py`, `generate_report.py`, `run_*sweep*.slurm`). El `MAMMOTH/`
de Eduardo (may-8) y `ESTUDIO_papilar_v2.md` siguen ahí, pero la carpeta es un **workspace
compartido vivo**, no la carpeta durmiente de un ex-colaborador.

**Cuál es correcta:** la realidad observada. El framing "otra persona / ex-Eduardo" llevó a
tratar la carpeta como dormida cuando el propio Sebastián opera ahí en paralelo. Importa
operativamente: refuerza workaround H (árbol compartido, jobs vivos) y explica por qué
escribir ahí necesita cuidado (no es "mi" workspace ni uno muerto).

**Fix:** reescribir CLAUDE.md:54 + regla 3 a "workspace **compartido** (owner `sdonoso`;
Sebastián y otros operan ahí) — **read-only por defecto**", y corregir la memoria de equipo.
NO se toca el matiz histórico (mammoth SÍ se heredó de Eduardo — sigue siendo cierto).

## L. Excepción regla dura — write autorizado por Sebastián a `clam_testing/`

- Reglas duras: `CLAUDE.md:417` (regla 3, no escribir en clam_testing), `:418` (regla 4,
  no escribir fuera de clam_testing2), "Workspace containment" (*"Sin excepción"*).
- **Acción ejecutada esta sesión**: creado `clam_testing/README.md` (resultados k=5: media +
  mejor AUC por tarea, ruta de split, dataset) **a pedido explícito de Sebastián** en la
  reunión. Surfaced antes de escribir (AskUserQuestion ×2: destino + archivo) y autorizado.
- **Precedente análogo ya en CLAUDE.md**: el `chmod 600 ~/.ssh/...` ("Reglas de commit y
  push") = excepción **quirúrgica** al containment, legítima por contexto (claves de Ernesto)
  y acotada a *ese* objetivo. Mismo molde acá: un **entregable puntual que Sebastián pide
  explícitamente**, acotado a *ese archivo* — NO abre clam_testing a escritura libre.
- **Fix (aditivo, regla dura → se aclara, no se reescribe el sentido):** sub-cláusula en
  regla 3 documentando la excepción quirúrgica autorizada por el supervisor (con el
  precedente `README.md` 8-jun) y reiterando default read-only + cuidado con jobs vivos
  (workaround H). Memoria nueva `clam-testing-workspace-compartido` como fact atómico.

## M. Redundancia gestionada — dos READMEs de resultados en clam_testing (sin fix)

El `README.md` nuevo y el puntero stub coexisten; ambos apuntan al canónico del repo. No es
contradicción: la **fuente versionada es el repo** (sobrevive a limpiezas del workspace
compartido y es citable desde GitHub). Se deja constancia para que una sesión futura edite
SIEMPRE el doc del repo y trate las copias en clam_testing como derivadas.

## Plan de fixes (pasada 8-jun)

1. **K** — CLAUDE.md:54 + regla 3 (caracterización compartido/activo) + memoria
   `equipo-arquitecturas-mammoth-longnet:14`.
2. **L** — sub-cláusula aditiva en regla 3 (excepción quirúrgica autorizada por Sebastián) +
   memoria nueva `clam-testing-workspace-compartido` + línea en `MEMORY.md`.

Edits en el working-tree (rama `main`). **Commit / branch destino: los decide Ernesto.**

---

# Pasada incremental — 10-jun-2026 (reunión Sebastián: PathPT pasa a PRUEBA ACTIVA)

> Disparador: reunión 10-jun cerrada. Sebastián validó PathPT (frame B) y pidió
> **probarlo ya** — empezar por la tarea **necrosis**, luego **mitotic rate**,
> generando los embeddings de texto CONCH. Deliverable de Ernesto para el lunes:
> presentación del FUNCIONAMIENTO de PathPT (con diagramas) + tablas resumen de
> mammoth + diagrama CLAM con el bloque de capa lineal reemplazado por mammoth.
> Sesión = estudio + registro (read-only de datos; GPU libre, sin lanzar nada).

## Resumen ejecutivo (pasada 10-jun)

La reunión **cambió la prioridad**: PathPT deja de ser "research del trimestre
siguiente" (framing del 5-jun) y pasa a **prueba activa**. Eso vuelve **stale** la
dirección registrada el 5-jun (D primario / B secundario) y obliga a **refinar el
caveat CONCH≠KEEP**, que la lectura *completa* del paper matiza (era demasiado
pesimista). Se **registra la base de conocimiento de PathPT** (arquitectura + 7
ecuaciones + relación CONCH↔PathPT↔CLAM + mecanismo de pseudo-labels + el requisito
de construir prompts) como doc canónico para el deliverable, y la **verdad de campo**
de las 2 tareas nuevas. Hallazgo colateral surfaced: el README mammoth tiene cambios
ajenos sin commitear (no se toca).

| id | hallazgo | sev. | acción |
|---|---|---|---|
| N | Stale: dirección retrieval (5-jun) superada por reunión 10-jun | media | update `progress/current.md` + addendum a memoria |
| O | Reconciliar: caveat CONCH≠KEEP demasiado pesimista vs paper completo | media | NOTA dated en `analisis.md` §4.2 (aditiva) |
| P | Captura: base de conocimiento PathPT (arquitectura/ecuaciones/relación) | **alta** | nuevo doc `pathpt/funcionamiento_pathpt.md` + memoria |
| Q | Verdad de campo: CSVs necrosis + mitotic (clases/conteos) | **alta** | tabla en el doc nuevo |
| R | Surface (sin fix): README mammoth con 91 líneas ajenas sin commitear | info | NO tocar; documentar |
| S | Verificado coherente: agentes/skills/regla 9 aplican a PathPT | — | sin acción |

## N. Stale — dirección retrieval (5-jun) superada por la reunión 10-jun

- **Dice (stale):** `progress/current.md` §"Nueva dirección (5-jun)" y memoria
  `retrieval-investigacion-b5` → "**D (CBIR) primario** para la presentación; **B
  (PathPT) secundario para research trimestre siguiente**".
- **Realidad (10-jun):** Sebastián validó PathPT y pidió **probarlo ahora**
  (necrosis → mitotic rate). B sube de "no quick-win" a **candidato activo en prueba**.
- **Canónico:** `progress/current.md` es el snapshot vivo → se actualiza. La memoria
  era una recomendación **point-in-time** → **no se reescribe**; se le agrega un
  **addendum dated** (preservar integridad histórica, criterio del skill).
- **Fix:** update `progress/current.md` (sección dirección + tabla plan) + addendum a
  `retrieval-investigacion-b5` + línea en `MEMORY.md`.

## O. Reconciliación — el caveat "CONCH≠KEEP / null #2" era demasiado pesimista

- **Dice:** `analisis.md` §4.2 punto 3 → "con CONCH estaríamos en el brazo *moderado*,
  no el ganador; riesgo real de **null #2**; para ganar habría que conseguir KEEP".
  (Escrito el 5-jun con lectura parcial del paper.)
- **La lectura completa lo matiza (evidencia sólida):**
  - **Fig 1d (caption explícito):** *PathPT-CONCH es el mejor en **9/11** benchmarks*
    vs los baselines MIL (incl. CLAM); PathPT-KEEP 8/11. → PathPT-CONCH **le gana a
    CLAM** en la gran mayoría de tareas.
  - **§4.5:** el loop completo de **pseudo-labels (self-training) se habilita SOLO con
    CONCH y KEEP** (con PLIP/MUSK lo apagan por inestable) → CONCH está en el **tier
    confiable**, no es un base "de segunda".
  - El *underperform* de CONCH es **específico de EBRAINS** (30 subtipos, el más duro).
    Nuestras tareas son de **2–4 clases**.
- **Reconciliación (no es contradicción, es matiz):** el riesgo "null #2" es específico
  de regímenes de **muchos subtipos** con grounding pobre. En nuestras tareas de 2–4
  clases, CONCH está en su **régimen favorable**. El riesgo **real reformulado** = el
  *grounding zero-shot task-específico* de **nuestra** morfología (¿CONCH "ve"
  microcalcificación / necrosis / invasión / patrón cribiforme?), **no testeado** — pero
  **barato de chequear** (etiquetado zero-shot CPU = go/no-go antes de GPU).
- **Fix:** **NOTA dated** al final de §4.2 (aditiva, no reescribe el texto original del
  5-jun). *Cautela de exactitud:* la afirmación sólida es Fig 1d (9/11) + tier de
  pseudo-labels + fallo específico EBRAINS; NO afirmar números puntuales por-backbone que
  el dotplot deja ambiguos (ej. quién logró el 0.820 en UBC-OCEAN).

## P. Captura — base de conocimiento PathPT para el deliverable del lunes

- **Problema:** el entendimiento profundo de PathPT (3 componentes, 7 ecuaciones,
  relación CONCH↔PathPT↔CLAM, mecanismo de pseudo-labels + 3 pérdidas, el requisito de
  construir prompts y su riesgo) vivía **disperso en la conversación**, sin doc canónico.
- **Fix:** nuevo doc `sprints/B5_sprint5/pathpt/funcionamiento_pathpt.md` = **base de
  estudio + fuente de la presentación** (con diagramas ASCII a convertir luego en assets).
  Memoria `pathpt-testing-necrosis-mitotic` como fact atómico de la nueva dirección.

## Q. Verdad de campo — CSVs de las 2 tareas nuevas (necrosis, mitotic rate)

Verificado read-only contra `clam_environ/environ/csv/` (10-jun):

- **`dataset_carcinoma_ductal_in_situ_necrosis_label.csv`** — 810 slides:
  `ausente` 83 · `no_identificado` 414 · `presente_central` 285 · `presente_focal` 28.
- **`dataset_grado_histologico_tasa_mitotica_label.csv`** — 1870 slides:
  `no_identificado` 693 · `score_1` 636 · `score_2` 287 · `score_3` 254.
- **Trampa clave:** los CSVs dan **nombres de clase en español**, NO prompts. PathPT
  necesita **frases clínicas (en inglés, pool de variantes)** para `Φ_t`. `no_identificado`
  es **mayoritario** y **mal definido a nivel tile** (= "el reporte CAP no lo menciona",
  no una apariencia) → rompe el supuesto "clase = algo que se ve en el parche".
- **Fix:** tabla documentada en `funcionamiento_pathpt.md` §verdad-de-campo.

## R. Surface (sin fix) — README mammoth con cambios ajenos sin commitear

- `git status`: `M results/README_experimentos_mammoth_environ.md` (+91 líneas **no mías**).
- Contenido: *"Entrenamiento Seba dataset pth balanced + Mammoth"* — lista de tareas
  (tipo histológico, gh aplica, **necrosis**, dif tubular, pleomorfismo; pendientes:
  grado nuclear, **mitotic rate**, necrosis 2 clases) + conteos `pth balance`.
- **Lectura:** Sebastián está corriendo **mammoth sobre las MISMAS tareas** que pidió
  probar con PathPT (necrosis, mitotic) → **habrá baselines CLAM/mammoth** para el paired.
- **Acción: NINGUNA.** Trabajo ajeno en árbol compartido + `results/` no se commitea en el
  audit. NO tocar/revertir/commitear (containment + workaround H). Solo se documenta.

## S. Verificado coherente (sin acción)

- `reviewer` y `trainer` (agentes) siguen válidos. **PathPT toca training** (entrena
  `θ_v` + `θ_t`, usa GPU) → **regla 9 + reviewer + `sbatch` aplican** (≠ el CBIR que era
  CPU sin entrenar). El doc nuevo lo deja explícito.
- Skills sin cambios estructurales. `@mil-model-integration` es la receta si PathPT pasa
  el go/no-go (pero PathPT es harness propio, no un `--model_type` de CLAM como mammoth).

## Plan de fixes (pasada 10-jun)

1. **N** — `progress/current.md`: nueva subsección dated (reunión 10-jun, PathPT activo,
   necrosis→mitotic, deliverable lunes) + tabla del plan. Addendum a memoria
   `retrieval-investigacion-b5` + línea `MEMORY.md`.
2. **O** — NOTA dated aditiva en `analisis.md` §4.2 (refina caveat, no reescribe).
3. **P** — nuevo `sprints/B5_sprint5/pathpt/funcionamiento_pathpt.md` + memoria
   `pathpt-testing-necrosis-mitotic` + línea `MEMORY.md`.
4. **Q** — tabla verdad-de-campo dentro del doc del fix 3.
5. **R/S** — sin edición (documentados acá).

Edits en el working-tree (rama `main`, GPU libre). **Commit / branch destino: los decide Ernesto.**
