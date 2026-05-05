# Plantillas de subagentes — leader / implementer / reviewer

Las plantillas viven en `assets/templates/.claude/agents/*.tmpl` y son lo que
copia `scaffold_harness.py`. Esta nota explica **cuándo personalizarlas** y
qué ajustar.

## Estructura común

Todos los subagentes son archivos `.md` con frontmatter YAML:

```yaml
---
name: <id>
description: <una línea, qué hace>
tools: <lista coma-separada o vacío>
---
```

Validable con `~/.claude/skills/architect/scripts/quick_validate.py`. Si tu
proyecto crea subagentes adicionales, valida con esa misma utilidad — no
reimplementes la verificación.

## Cuándo personalizar `leader.md`

- **Cambiar la tabla de escalado** si tu dominio tiene unidades de trabajo
  distintas a "feature de software" (p. ej. proyectos de datos: lote-de-datos,
  modelo, evaluación).
- **Permitir editar fuera de `src/`**: por defecto el leader puede tocar
  `docs/` y `progress/`. Si tu proyecto separa más, restringe explícitamente.
- **Añadir/quitar tipos de subagente**: si necesitas un `data-curator` o un
  `benchmark-runner`, añádelo a la tabla y créalo en `.claude/agents/`.

## Cuándo personalizar `implementer.md`

- **Test command**: el template asume `./init.sh` corre los tests. Si tu
  pipeline es distinto (`make test`, `cargo test --release`), ajústalo.
- **Convenciones de naming en `progress/`**: el template usa
  `impl_<id>_<name>.md`. Si tu proyecto prefiere `impl_YYYYMMDD_<name>.md`,
  cambia el patrón aquí.
- **Iteración límite**: añade "máximo N iteraciones de fallar tests antes de
  bloquear" si quieres acotar costos.

## Cuándo personalizar `reviewer.md`

- **Anti-patrones específicos del dominio**: el template lista los genéricos
  (mocks de fs, prints sueltos). Añade los tuyos: "no SQL inline", "no
  llamadas síncronas en handlers async", etc.
- **Citar refs específicas**: en lugar de `docs/conventions.md §3.2`, cita
  archivos de tu proyecto.
- **Severidad**: el template usa APPROVED / CHANGES_REQUESTED. Si quieres
  un nivel intermedio (NITS_ONLY), añádelo.

## Patrón "explorer" (subagente ad-hoc)

El leader puede lanzar `subagent_type: "Explore"` (built-in de Claude Code)
para exploración paralela. NO necesitas un archivo `.claude/agents/explorer.md`
— Explore es estándar.

Cuando lances Explore desde el leader, el prompt **debe** incluir:

> "Escribe tus hallazgos en `progress/explore_<tema>.md`. Tu respuesta debe
> ser solo: `done -> progress/explore_<tema>.md`."

Esto fuerza el patrón anti-teléfono-descompuesto incluso con subagentes
built-in.

## Errores comunes

- **Frontmatter sin `description`**: Claude no sabe cuándo invocarlo
  automáticamente. Siempre incluye una descripción específica.
- **`tools` excesivo**: el reviewer NO necesita `Edit` ni `Write`. Si lo
  tiene, perderá la separación de roles. Mantén `Read, Glob, Grep, Bash`.
- **Frontmatter con campos no estándar**: Claude Code ignora campos
  desconocidos pero `quick_validate.py` puede fallar. Stick a `name`,
  `description`, `tools`, opcionalmente `model`.
