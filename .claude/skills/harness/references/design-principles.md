# Principios de diseño del harness

Destilados del repo `hyprland-rice/ejemplo-harness-subagentes-main/` y
contrastados con la guía oficial de Anthropic (subagents, skills, hooks).

## 1. Estado como fuente de verdad

El **repositorio** es el sistema. El chat es efímero. Los agentes escriben en
disco (`feature_list.json`, `progress/*.md`) y leen del disco. Una sesión
nueva puede continuar sin el historial de chat anterior.

**Por qué importa**: el context window es finito. Si la única memoria es el
chat, una compaction destruye el plan. Con bitácora persistente, el agente
retoma desde `progress/current.md`.

## 2. Separación dura de roles

| Rol           | Edita código | Marca `done` | Decide qué hacer | Valida |
|---------------|--------------|--------------|------------------|--------|
| `leader`      | ❌           | ❌           | ✅               | ❌     |
| `implementer` | ✅           | ❌¹          | ❌               | ❌     |
| `reviewer`    | ❌           | ❌           | ❌               | ✅     |

¹ El implementer puede solicitar el cambio de status, pero solo tras revisión
aprobada y en una sesión posterior.

**Por qué importa**: los conflictos vienen de roles superpuestos. Cuando el
mismo agente decide-implementa-valida, los sesgos se acumulan. La separación
fuerza comunicación asíncrona y verificación independiente.

## 3. Ciclo explore → impl → review

Cada feature pasa por 3 fases:

```
[Explore opcional] → Implementer → Reviewer → done
       ↓                   ↓             ↓
 progress/explore_*.md  impl_*.md   review_*.md
```

**Reglas de escalado** (ver `leader.md.tmpl`):

- Trivial (1 archivo): solo implementer.
- Media (2-3 archivos): implementer + reviewer.
- Compleja (refactor): 2-3 explorers en paralelo → implementer → reviewer.

## 4. Anti-teléfono-descompuesto

Los subagentes **escriben en archivos**, no en chat. Devuelven solo la
referencia: `done -> progress/impl_<feature>.md`.

**Por qué**: cuando el subagente devuelve un bloque de 300 líneas en chat, el
leader lo resume al integrarlo. El resumen pierde detalle. Otro subagente lee
ese resumen, lo re-resume, etc. Acumulación de errores de transcripción
("teléfono descompuesto"). El archivo en disco preserva el detalle exacto.

## 5. Checkpoints ejecutables, no aspiracionales

`CHECKPOINTS.md` no es una lista de buenas intenciones. El `reviewer` lo
recorre marcando `[x]` o `[ ]` con cita concreta, y el hook `Stop` ejecuta
`./init.sh` antes de cerrar la sesión.

Los 5 niveles cubren: (C1) integridad estructural, (C2) coherencia de estado,
(C3) arquitectura respetada, (C4) verificación real, (C5) cierre limpio.
Detalle en [checkpoints-rationale.md](checkpoints-rationale.md).

## 6. Una feature por sesión

`init.sh` valida `len([f for f in features if f.status == "in_progress"]) <= 1`.
Previene mezcla de cambios cruzados que rompen `git bisect` y reviews.

## 7. Hooks que el sistema ejecuta, no el agente

`PostToolUse(Edit|Write) → tests`: tras cada cambio, el harness ejecuta tests.
El agente no decide saltárselo.

`Stop → ./init.sh`: antes de cerrar, gate completo. Si falla, alerta.

**Anti-patrón**: meter "siempre corre los tests" en el CLAUDE.md. Eso depende
del agente recordarlo. Los hooks no dependen.

## 8. Divulgación progresiva

`AGENTS.md` es un mapa con tabla "cuándo leerlo". El agente no recibe todas
las reglas de golpe; busca bajo demanda. `CHECKPOINTS.md` se lee solo antes
de cerrar; `docs/conventions.md` solo antes de escribir código.

**Por qué**: pre-cargar 5000 líneas de reglas en cada sesión consume contexto
y baja la adherencia. Cargar lo justo cuando importa, eleva ambas.

## Alineación con guía Anthropic

| Principio harness                | ¿Anthropic lo recomienda? |
|----------------------------------|---------------------------|
| Subagentes con contexto separado | ✅ (subagents.md)         |
| Hooks en `settings.json`         | ✅ (hooks.md)             |
| CLAUDE.md < 200 líneas           | ✅ (memory.md)            |
| Plan mode + ExitPlanMode         | ✅ (parcial — agent teams) |
| Bitácora persistente             | ✅ (auto-memory)          |
| "Harness" como término oficial   | ❌ (no documentado)        |

El patrón es **comunitario emergente**, compatible con la guía oficial pero
no canónico. Razón para adoptarlo como skill opt-in, no como dogma global.
