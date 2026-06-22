# Auditoría de coherencia — notas del presentador (guion didáctico) + conteo de slides

> Generado: 2026-06-22. Branch: `chore/audit-notas-guion-b5`.
> Disparador: esta sesión (a) cerró el deck B5 con la slide keep_slots (19→20 slides) y
> (b) reescribió las 20 notas del presentador a un **guion didáctico por fases** (cambio de
> formato decidido por Ernesto). Hay que propagar ambos cambios por las 4 frentes y reconciliar
> la tensión con la convención previa de "notas concisas" de Benjamín.

## Resumen (id · hallazgo · severidad · acción)

| id | hallazgo | tipo | sev | acción |
|---|---|---|---|---|
| A | CLAUDE.md "Deck B5" addendum dice notas = `PROPÓSITO/narrativa/PUNTOS CLAVE` (ya superado) | stale | media | actualizar additivo → guion por fases, mantener puntero a §3.b |
| B | `convenciones_deck_b5.md` dice "17 slides" en L24 y §7 (deck real = 20) | stale | media | actualizar conteo + enumerar las 3 slides faltantes (6b/6c fused + keep_slots) |
| C | memoria `deck-completo-pptx-buildable` + index dicen "17 slides" (caso 14-jun) | stale | baja | nota mínima preservando el hito histórico 14-jun |
| D | tensión: Benjamín pidió notas "concisas/ultra-minimalistas" vs guion didáctico de Ernesto | reconciliation | media | addendum a `presentacion-convenciones-benjamin` + nueva memoria feedback del guion |

§3.b de `convenciones_deck_b5.md` YA fue actualizado a guion por fases este turno (canónico). El
resto de las frentes lo refleja con retraso → esta auditoría las pone en sync.

---

## A — CLAUDE.md addendum de notas stale (stale, media)

- **Dónde:** `CLAUDE.md:830-832`. Dice: *"Deck B5: el formato de notas evolucionó a `PROPÓSITO —
  …` / narrativa / `PUNTOS CLAVE`, texto blanco — ver §3.b."*
- **Por qué es stale:** esta sesión evolucionó el formato a un **guion didáctico por fases**
  (PROPÓSITO + ABRIR + EXPLICAR + ANALOGÍA/EJEMPLO + PUNTO CLAVE + TRANSICIÓN). El motor
  `set_notes(slide, proposito, sections)` cambió de firma. `narrativa/PUNTOS CLAVE` ya no existe.
- **Canónico:** `convenciones_deck_b5.md` §3.b (ya actualizado).
- **Fix:** reescribir el addendum (es una línea de "fact", NO una regla dura) para nombrar las
  fases y seguir apuntando a §3.b. El bloque B2 "BLOQUE N —" de arriba se conserva (es el formato
  histórico/general; el addendum aclara que para el deck B5 manda §3.b).

## B — `convenciones_deck_b5.md` conteo de slides stale (stale, media)

- **Dónde:** L24 (tabla, *"ensambla el deck end-to-end (17 slides)"*) y L174 (*"## 7. Estructura
  del deck B5 (17 slides)"* + enumeración).
- **Por qué es stale:** el deck real tiene **20 slides** (build 22-jun verificado, `slides=20`).
  Faltan 3 en la enumeración de §7: las dos slides de figura oficial fused (6b figura oficial
  MAMMOTH + 6c variante keep_slots, agregadas por la sesión paralela de slides) y la slide nueva
  de resultados keep_slots (8b, esta sesión).
- **Fix:** L24 y título §7 → "20 slides"; insertar en la enumeración de §7: tras "diagrama zoom
  MoE" → "figura oficial (fused) · variante keep_slots (fused)"; tras "invasión" → "keep_slots
  resultados (tabla)".

## C — memoria `deck-completo-pptx-buildable` conteo stale (stale, baja)

- **Dónde:** memoria `deck-completo-pptx-buildable.md` (cuerpo + description) y `MEMORY.md:34` —
  *"Caso CLAM_Sprint_B5.pptx (17 slides, 3 rondas feedback, 14-jun)."*
- **Por qué es stale (bajo):** es el **caso histórico** del 14-jun (1ª build madura). El valor de
  la memoria es la receta de build nativo, no el conteo. Pero el conteo quedó desactualizado.
- **Fix (mínimo, preserva historia):** "(17 slides en la build 14-jun; 20 al 22-jun con keep_slots
  + notas como guion)". NO reescribir la receta.

## D — Reconciliación: "notas concisas" (Benjamín) vs guion didáctico (Ernesto) (reconciliation, media)

- **Dónde:** memoria `presentacion-convenciones-benjamin.md` punto 1 — *"Notas del presentador
  CONCISAS… ultra-minimalistas, bullets esenciales, una idea una vez… no narrar el gráfico, dar la
  conclusión."* (feedback de Benjamín sobre el deck B4, 1-jun.)
- **Tensión aparente:** esta sesión Ernesto pidió un **guion didáctico completo y autosuficiente**
  ("todo lo que debería decir"), más extenso que "ultra-minimalista".
- **Reconciliación (no es contradicción real):** el dolor que reportó Benjamín fue que Ernesto
  *"no pudo explicar bien"* por notas **sobrecargadas y repetitivas que narraban el gráfico**. El
  guion por fases ataca **el mismo objetivo** (que Ernesto exponga bien) con **estructura** en vez
  de densidad: ABRIR/EXPLICAR/PUNTO CLAVE/TRANSICIÓN no repiten ni narran el gráfico — dan el hilo
  para enseñar y la conclusión va en PUNTO CLAVE. Las **restricciones duras de Benjamín se
  conservan**: sin nº de job, sin nombres, conclusión > narración del gráfico, framing institucional.
- **Matiz a vigilar (surface):** el guion ES más largo que "ultra-minimalista"; mantenerlo
  **escaneable** (las etiquetas en negrita lo permiten) y no volver a la densidad repetitiva del B4.
- **Fix:** (1) addendum dtado a la memoria de Benjamín (no reescribir su feedback) apuntando a la
  reconciliación + §3.b; (2) nueva memoria `feedback` `notas-presentador-guion-didactico` con la
  preferencia de Ernesto y el "why"; (3) línea en `MEMORY.md`.

---

## Frentes sin hallazgos

- **Agentes** (`trainer`, `reviewer`): no tocan formato de notas/deck → sin cambios.
- **Skills**: `handoff` y `knowledge-audit` corrieron OK este sprint; estructura válida. El deck no
  tiene skill propia. Sin cambios.
- **Números/veredictos mammoth (12 tareas, 0 palancas)**: ya canónicos en CLAUDE.md Hallazgo 12 y
  memorias ANTES de esta sesión → no requieren propagación (el deck es gitignored, consume la verdad
  de campo, no la define).
