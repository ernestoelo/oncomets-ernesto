# Auditoría de coherencia — VIRAJE del formato de notas del presentador (guion hablado)

> Generado: 2026-06-25. Branch al correr: `chore/audit-paper-mammoth-b5`.
> Disparador: en la sesión de revisión slide-por-slide del deck B5, Ernesto **cambió el formato
> de las notas del presentador**: de "guion didáctico por fases" (22-jun) a **guion HABLADO
> corrido** (prosa, sin etiquetas de fase). Pidió explícitamente registrarlo vía `@knowledge-audit`
> para que **todas las presentaciones futuras** lo sigan. Supersede el `hallazgos_notas_guion.md`
> (22-jun) en lo relativo al FORMATO (no a su conteo de slides ni a la reconciliación con Benjamín).

## Contexto del viraje (qué pidió Ernesto, validado slide 1–6)

Presenta **online** y va a ir **leyendo**, así que necesita **solo el guion** —lo que dice en voz
alta—. Rechazó, una por una: la línea `PROPÓSITO`, las etiquetas `ABRIR`/`RECORRIDO`/`EXPLICAR`/
`PUNTO CLAVE`/`TRANSICIÓN` ("generan ruido"), la palabra "deck", las frases artificiales ("que se
la lleven desde el primer minuto") y los coloquialismos poco profesionales ("mover la aguja",
"aguas abajo"). Aprobó el resultado: *"me encantaron esas notas más habladas, así deben ser"*.

## Resumen (id · hallazgo · tipo · sev · acción)

| id | hallazgo | tipo | sev | acción |
|---|---|---|---|---|
| V-A | `convenciones_deck_b5.md` §3.b (CANÓNICO) describe el formato por-fases | contradiction | alta | reescritura aditiva: spoken-script = VIGENTE + spec; por-fases → LEGACY |
| V-B | `CLAUDE.md` §Formato de entregables, addendum "Deck B5" (L857-865) describe por-fases | stale | media | update conciso → guion hablado, mantener puntero a §3.b |
| V-C | memoria `notas-presentador-guion-didactico` + `MEMORY.md` | stale | — | YA actualizadas este turno (ADDENDUM 25-jun); enriquecer con refinamientos |
| V-D | motor `set_notes(slide, proposito, sections)` de `generate_b5_deck.py` RINDE por-fases | divergencia intencional | baja | NO tocar el script; documentar que Ernesto edita en OnlyOffice (regenerar pisaría sus notas) |

## V-A — convenciones §3.b describe el formato viejo (contradiction, alta)

- **Dónde:** `sprints/B5_sprint5/presentacion_b5/convenciones_deck_b5.md` §3.b (L52-71).
- **Qué dice (viejo):** `set_notes` rinde un GUION por fases con `PROPÓSITO —` + `ABRIR` + `RECORRIDO`
  + `EXPLICAR` + `ANALOGÍA`/`EJEMPLO` + `PUNTO CLAVE` + `TRANSICIÓN`, ítems anclados en negrita.
- **Por qué es contradicción:** es la fuente CANÓNICA del formato de notas y contradice el formato
  vigente (prosa hablada, sin etiquetas). La memoria ya viró; §3.b quedó atrás.
- **Fix (aditivo):** reescribir §3.b con el **spec del formato hablado como VIGENTE** (las reglas de
  abajo) y degradar el por-fases a un bloque **LEGACY** breve (preservado: no se borra contenido
  único; el detalle histórico también vive en el HISTÓRICO de la memoria).

### Spec del formato VIGENTE (guion hablado) — el registro que pidió Ernesto

1. **Prosa en párrafos**, leíble de corrido. SIN etiquetas de fase.
2. **Solo lo que se dice.** Sin meta-instrucciones ("decir tal cual", "señalá") ni la palabra "deck".
3. **Registro profesional.** Sin frases artificiales ni coloquialismos ("mover la aguja", "aguas
   abajo" → "mejorar los resultados", "las etapas posteriores").
4. **Pedagogía fundida en prosa.** El recorrido de la slide (elementos, paneles de figura A→B,
   colores) se cuenta dentro del párrafo, no como lista rotulada; analogías y definiciones integradas.
5. **Definir antes de usar.** Cada término (slot, prototipo, query…) se define antes de la fórmula.
6. **Fiel a las ecuaciones del diagrama.** Cuando la slide muestra fórmulas/dims por bloque,
   describirlas fielmente (citar la ecuación escrita + explicarla en palabras) y dejar claro el
   **eje/dirección** (ej. softmax ↓ N parches vs ↓ 300 slots; "es al revés: cada slot recoge de
   todos los parches, no parche por parche").
7. **Sin ejemplos numéricos en el guion.** Debe entenderse con la sola explicación; un ejemplo
   numérico queda para responder si preguntan.
8. **Encadenar slide con slide.** Abrir retomando el cierre de la anterior, cerrar anticipando la
   siguiente, sin rótulo de "transición".
9. **Brevedad por tipo.** Divisorias/transición = 1 párrafo muy breve. Slides técnicas centrales
   pueden ser más extensas, sin sobre-extenderse; si algo alarga, recortar lo secundario.
10. **Restricciones duras que se conservan:** texto **blanco**, **sin nº de job, sin nombres**
    (baselines = "Métricas oficiales Environ"), español técnico + pedagógico, autosuficiente para
    leer mientras se expone ([[presentacion-convenciones-benjamin]]).

## V-B — CLAUDE.md addendum "Deck B5" stale (stale, media)

- **Dónde:** `CLAUDE.md` §Formato de entregables, L857-865.
- **Qué dice (viejo):** "las notas evolucionaron a un GUION DIDÁCTICO por fases — PROPÓSITO/ABRIR/
  EXPLICAR/ANALOGÍA/PUNTO CLAVE/TRANSICIÓN…".
- **Fix (conciso, es una línea de "fact" no una regla dura):** reescribir el addendum → guion
  hablado corrido (sin etiquetas), apuntando a §3.b. El bloque B2 "BLOQUE N —" de arriba se conserva
  (formato histórico general).

## V-C — memoria + índice (stale → ya resuelto este turno)

- `notas-presentador-guion-didactico.md` reescrita con **ADDENDUM 25-jun** (viraje) + el por-fases
  pasó a **HISTÓRICO**; `MEMORY.md` línea actualizada. Acción restante: enriquecer el ADDENDUM con
  los refinamientos finos (fiel a ecuaciones, sin ejemplos numéricos, definir antes de usar,
  encadenar slides) + puntero a §3.b como spec completo.

## V-D — el motor set_notes sigue rindiendo por-fases (divergencia intencional, baja)

- **Dónde:** `scripts/generate_b5_deck.py` (`set_notes(slide, proposito, sections)`, def L112).
- **Estado:** Ernesto edita las notas **directo en OnlyOffice**; el `.pptx` con las notas habladas
  NO se regenera desde el script. Regenerar pisaría sus ediciones (formato por-fases).
- **Acción:** NO tocar el script (no es el pedido). Documentar la divergencia como **intencional**
  en §3.b y en la memoria. Propagar el formato nuevo al motor `set_notes` solo si Ernesto lo pide.

---

## Frentes sin hallazgos

- **Agentes** (`trainer`, `reviewer`): no tocan formato de notas → sin cambios.
- **Skills**: sin cambios; el deck no tiene skill propia.
- **Reconciliación con Benjamín** (`presentacion-convenciones-benjamin`): **sigue válida** — el
  guion hablado respeta sus restricciones duras (sin nº de job, sin nombres, conclusión > narrar el
  gráfico, framing institucional). El viraje cambia la FORMA (prosa vs etiquetas), no el objetivo.
  No requiere nuevo fix.
- **Números/veredictos** del deck (mammoth 0 palancas, etc.): canónicos en CLAUDE.md/memorias; el
  deck es gitignored y consume la verdad de campo, no la define → sin propagación.
