---
name: session-close
description: Orquesta el cierre de sesión OncoMets — documenta con @knowledge-audit, genera el @handoff con TODOS los pendientes sin terminar, y commitea + pushea. Triggers — cerrar sesión, cierre de sesión, terminar la sesión, rutina de cierre.
argument-hint: "¿foco de la próxima sesión? (1 línea, opcional — se pasa a @handoff)"
---

# session-close — Rutina de cierre de sesión (documentar → handoff → push)

Ejecuta, en orden estricto, la rutina con la que Ernesto cierra cada sesión:
**(1)** documentar los hallazgos críticos y la evidencia de progreso de la
sesión con `@knowledge-audit`, **(2)** generar un `@handoff` que arrastre
**todos los pendientes sin terminar** para que una sesión limpia los retome, y
**(3)** commitear + pushear. Reemplaza tener que escribir el prompt de cierre a
mano cada vez.

## Cuándo invocar esta skill

- Al terminar una sesión de trabajo y querer dejar el espacio consolidado.
- Cuando pedís explícitamente "cerrar sesión" / "rutina de cierre".
- Cuando la sesión ya cumplió su misión y otra sesión limpia sigue el trabajo.

## Cuándo NO invocarla

- A mitad de una tarea que vas a continuar en la misma sesión (no hay nada que
  handoffear todavía).
- Si NO querés pushear: invocala igual pero avisá "sin push" → la Fase 3 se
  queda en commits locales (ver Fase 3).
- Para un handoff aislado sin documentar/commitear → usá `@handoff` directo.

## Las 3 fases (orden estricto — no saltear ni reordenar)

### Fase 0 — Preflight (read-only, antes de tocar nada)

- `git branch --show-current` → esperar `main` (default de Ernesto,
  [[git-trabajar-en-main-por-defecto]]). Si NO es `main`, superficializar antes
  de seguir ([[surface-premise-discrepancies]]).
- `git fetch` — `main` es compartido con varios autores ([[git-main-shared-pushes]]).
- `squeue -u $USER` y `squeue` — anotar jobs propios/ajenos en curso.
  **Si hay un job corriendo (workaround H):** NO cambiar de rama y NO editar los
  inputs que el job relee (`main.py`, CSVs, splits, scripts bajo `clam_environ`).
  El cierre es documental sobre `main` (CLAUDE.md, memorias, docs de sprint,
  `progress/`) → seguro mientras no toques los inputs del job ni hagas
  branch-switch.
- `git status` — inventariar el trabajo sin commitear que la Fase 3 va a versionar.

### Fase 1 — Documentar (`@knowledge-audit`)

Invocar `@knowledge-audit` para registrar en la base de conocimiento **los
hallazgos críticos de ESTA sesión** y actualizar el repo con la evidencia de
progreso:

- Hallazgos durables → `CLAUDE.md` (aditivo, canonical vs referencia) y/o memorias
  (`~/.claude/.../memory/*.md` + línea en `MEMORY.md`).
- Verdad de campo del progreso → `sprints/<sprint>/.../resultados.md`,
  `progress/current.md`, y `git add results/<obj>/` si se cerró un objetivo.
- Respetar los criterios de `@knowledge-audit`: nunca borrar contenido único,
  edición aditiva de reglas duras, integridad de pre-registración (ADDENDUM
  fechado, no reescribir hipótesis regla 9).

Esta fase **edita** los docs; los commits se consolidan en la Fase 3 (o si
`@knowledge-audit` ya commiteó granular, la Fase 3 solo verifica + pushea).

### Fase 2 — Handoff (`@handoff`) con TODOS los pendientes

**Antes** de invocar `@handoff`, compilar la lista de pendientes de la sesión
(ver "Regla clave" abajo). Luego invocar `@handoff` pasándole el foco de la
próxima sesión (el argumento  si se dio; si no, derivarlo del pendiente
principal). Asegurar que **cada pendiente compilado** aparezca explícito en el
handoff (§1 misión, §6 plan, §10 contexto efímero).

El handoff se guarda en `/tmp/` o `.handoffs/` (gitignored) y **NO se commitea**
— es efímero entre sesiones (ver `@handoff`, "Dónde guardar").

### Fase 3 — Commit + push

- `git branch --show-current` de nuevo (el árbol es compartido; confirmar `main`).
- Commits **granulares por tema**, conventional commits, **identidad LOCAL**
  (`Ernesto Gamero` / `ernesto.gamero@sansano.usm.cl`, nunca `--global`).
- **NO commitear**: el handoff (`.handoffs/`), artefactos pesados de `results/`
  (`*.pt/*.pth/*.h5/checkpoints/`, ya gitignored), papers/presentaciones.
- Si algún cambio tocó `model_*.py` / `core_utils.py` / training → **reviewer OK
  antes del commit** (regla 9); un cierre normal es documental y no aplica.
- Push: `git fetch` ya corrido en Fase 0; si `origin/main` avanzó, integrar
  primero; luego `git push`. **Nunca `--force`**; encolar detrás de jobs ajenos
  ([[git-main-shared-pushes]]). Si el push falla por `~/.ssh` → workaround F
  (`chmod 600`, excepción quirúrgica); por otra razón → parar y reportar.

> **Autorización de push:** invocar esta skill **es** la autorización explícita
> de push que pide CLAUDE.md (default = "push lo hace Ernesto"). Si dijiste
> "sin push", la Fase 3 termina en commits locales y reporta qué quedó por pushear.

## Regla clave — los pendientes van COMPLETOS al handoff

El handoff debe listar como pendientes **todos** los puntos/temas que la sesión
**no alcanzó a terminar**. Antes de la Fase 2, compilá:

- Jobs SLURM en curso o encolados (ID, estado, qué producen, cómo verificarlos).
- Análisis/entregables a medias, TODOs abiertos, preguntas sin responder.
- Bloqueos (falta un dato, espera de confirmación de Sebastián/Benjamín, etc.).
- Decisiones tomadas en la sesión pero no ejecutadas.

**Verificá que cada pendiente siga realmente abierto** antes de listarlo — el
handoff arrastra pendientes efímeros ya resueltos; grepeá memorias/repo primero
([[verificar-antes-de-pedir-dato]]). Un pendiente resuelto se cierra, no se
copia al handoff.

## Guardrails

- **Containment**: escribir solo bajo `clam_testing2/oncomets-ernesto/` (memorias
  bajo `~/.claude/...` = excepción conocida). Nunca `clam_environ/` (read-only)
  ni `clam_testing/`.
- **Job en curso** (workaround H): sin branch-switch ni edición de inputs del job.
- **GPU**: el cierre nunca usa GPU ni cancela jobs.
- **Push**: `git fetch` antes, nunca `--force`, encolar detrás de jobs ajenos.

## Anti-patrones a evitar

- **Saltear la Fase 1** ("ya lo tengo en la cabeza") → los hallazgos se pierden
  para la próxima sesión.
- **Handoff sin los pendientes** → la sesión nueva no sabe qué quedó a medias
  (es el error que esta skill existe para evitar).
- **Commitear el handoff** → es efímero, va gitignored.
- **Pushear con `--force` o sin `fetch`** → `main` es compartido.