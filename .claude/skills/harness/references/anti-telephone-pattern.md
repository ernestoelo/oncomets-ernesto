# Anti-teléfono-descompuesto — prompts que fuerzan escritura a disco

## El problema

Cuando un subagente devuelve 300 líneas de hallazgos en chat, el leader las
**resume** al integrarlas. El resumen pierde detalle. Si otro subagente lee
ese resumen, re-resume. Acumulación de errores de transcripción.

Síntomas típicos:

- "El reviewer aprobó pero olvidó verificar X" — el implementer mencionó X en
  chat, el reviewer leyó el resumen del leader sin X.
- "Decidimos usar la estrategia A" — en realidad un explorer dijo "A o B
  según contexto"; en el resumen quedó solo A.

## La solución

Los subagentes **escriben en archivos** con detalle completo. Devuelven al
leader solo:

```
done -> progress/<archivo>.md
```

o, si hay bloqueo:

```
blocked -> progress/current.md
```

El leader nunca ve el contenido en chat — lee del archivo cuando lo necesita,
con cita exacta.

## Plantillas de prompt

### Explorer (lectura, análisis)

```
Investiga <pregunta concreta> en <scope acotado>. Escribe tus hallazgos
en `progress/explore_<tema>.md` con esta estructura:

  ## Pregunta
  <repite la pregunta>

  ## Hallazgos
  - <fact 1> (file.py:LL)
  - <fact 2> (file.py:LL)

  ## Recomendación
  <1-2 frases>

Tu respuesta a mí debe ser **solo una línea**:
  done -> progress/explore_<tema>.md

NO incluyas hallazgos en tu respuesta de chat.
```

### Implementer

```
Implementa la feature de id=N de feature_list.json. Sigue
docs/architecture.md y docs/conventions.md. Escribe en
progress/impl_<id>_<name>.md:

  ## Archivos modificados
  - <ruta> (creado | modificado)

  ## Decisiones de diseño
  - <1-3 bullets>

  ## Salida de tests
  ```
  <pegar últimas 10 líneas de ./init.sh>
  ```

Tu respuesta a mí debe ser **una línea**:
  done -> progress/impl_<id>_<name>.md
```

### Reviewer

```
Revisa progress/impl_<id>_<name>.md contra CHECKPOINTS.md y docs/.
Escribe veredicto en progress/review_<id>_<name>.md:

  ## Veredicto
  APPROVED | CHANGES_REQUESTED

  ## C1-C5
  <recorre cada checkpoint con [x] o [ ] + cita>

  ## Cambios requeridos (si aplica)
  1. <archivo>:<línea> — <qué falta> (regla violada: <ref>)

Tu respuesta a mí debe ser **una línea**:
  APPROVED -> progress/review_<id>_<name>.md
o
  CHANGES_REQUESTED -> progress/review_<id>_<name>.md
```

## Cuándo NO aplicar

- **Preguntas conceptuales** ("¿qué hace este módulo?"): el leader responde
  directamente sin lanzar subagente.
- **Cambios triviales** (renombrar variable en 1 archivo): el leader puede
  delegar pero el archivo `impl_*.md` sería overkill — basta una línea en
  `progress/current.md`.
- **Sesiones exploratorias** sin features definidas: usa el flujo libre de
  Claude Code, no el harness.

## Verificación

El reviewer rechaza tareas cuyo `impl_*.md` no exista:

> "No encuentro `progress/impl_<id>_<name>.md`. El implementer debe escribir
> ahí antes de cerrar. CHANGES_REQUESTED."

Esto fuerza el patrón sin que el leader tenga que recordarlo.
