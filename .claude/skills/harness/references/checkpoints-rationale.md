# CHECKPOINTS.md — por qué 5 niveles y cómo extenderlos

## Filosofía

> En sistemas multi-agente no se evalúa el camino, se evalúa el destino.

El reviewer no juzga si el implementer "siguió un buen proceso". Juzga si el
**estado final** del repo es correcto. Esto es deliberado: procesos pueden
ser distintos según el agente; un destino correcto es invariante.

## Por qué exactamente 5 niveles

Cada checkpoint cubre una **clase de error** ortogonal:

| Nivel | Pregunta                                 | Error que detecta |
|-------|------------------------------------------|-------------------|
| C1    | ¿Existe la estructura del harness?       | Archivos faltantes (corrupción del repo) |
| C2    | ¿El estado es coherente?                 | Múltiples features `in_progress`, `current.md` con basura |
| C3    | ¿La arquitectura sigue las reglas?       | Capas mezcladas, debug code, deps no documentadas |
| C4    | ¿La verificación es real?                | Tests con mocks que no fallan, asserts vagos |
| C5    | ¿Se cerró bien la sesión?                | Archivos temporales sin trackear, `history.md` no actualizado |

**Si fusionas niveles**: C3+C4 juntos significan que un fallo de tests oculta
un fallo de arquitectura. **Si añades más**: aumenta el costo de cada review
sin valor proporcional. 5 es el sweet spot empírico.

## Cómo extender

Añade un C6 cuando:

- **Hay un dominio externo verificable**: p. ej. proyectos web → "C6:
  accesibilidad WCAG AA validada con axe-core". 
- **Hay compliance**: licencias, GDPR, secretos. P. ej. "C6: ningún archivo
  contiene `API_KEY=` literal".
- **Hay performance no negociable**: "C6: benchmark X termina en < 50ms
  para input de tamaño N".

NO añadas un C6 para preferencias de estilo (eso va en `conventions.md`) ni
para TODOs de roadmap (eso va en `feature_list.json`).

## Cómo personalizar los existentes

`CHECKPOINTS.md.tmpl` usa placeholders `{{SRC_DIR}}`, `{{TESTS_DIR}}`,
`{{TEMP_FIXTURE}}`, `{{TEST_CMD}}`, `{{TMP_PATTERNS}}` que el
`scaffold_harness.py` rellena por runtime. Si tu proyecto Python usa `pytest`
en lugar de `unittest`, edita el `CHECKPOINTS.md` resultante (no el .tmpl) o
ajusta `render_init_template.py`.

## Reviewer ejecuta los checkpoints, no el implementer

Mantén la separación: el implementer hace su impl_*.md, el reviewer recorre
checkpoints en `review_*.md`. Si el implementer auto-evalúa, sesgos.

## Cuándo se ejecuta cada nivel

- **C1**: en cada `./init.sh` (validación rápida, < 1s).
- **C2**: en cada `./init.sh` (validación rápida).
- **C3**: heurística rápida en `./init.sh` (grep de prints/console.log) +
  manual en `review_*.md`.
- **C4**: en cada `./init.sh` (corre tests).
- **C5**: solo al cerrar (hook `Stop`).
