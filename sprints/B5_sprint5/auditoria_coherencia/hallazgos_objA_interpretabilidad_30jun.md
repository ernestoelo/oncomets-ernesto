# Auditoría de coherencia — integración OBJ-A (interpretabilidad MAMMOTH) — 30-jun-2026

> Audit documental tras ejecutar OBJ-A (interpretabilidad de expertos/slots de MAMMOTH
> en mama, Etapa 0 CPU post-hoc). Objetivo: propagar al repo completo que el objetivo que
> estaba **propuesto/planeado** ahora está **ejecutado**, con sus hallazgos, sin reabrir el
> eje RENDIMIENTO ("0 palancas", Hallazgo 12 — el eje entendimiento es ORTOGONAL).
> Trabajo en `main` (preferencia de Ernesto, [[git-trabajar-en-main-por-defecto]]); audit
> es documental, no toca modelo/training ni reabre 9.b → ninguna regla dura exige branch.

## Tabla resumen

| id | hallazgo | tipo | severidad | acción |
|---|---|---|---|---|
| A1 | CLAUDE.md Hallazgo 12 ADDENDUM 29-jun describe la interpretabilidad como "objetivo barato Etapa 0" (PLAN) | stale | media | ADDENDUM 30-jun aditivo: OBJ-A ejecutado + hallazgo clave |
| A2 | `respuestas_preguntas_benjamin.md` §Q6 enmarca la interpretabilidad como objetivo futuro ("lo que propongo como objetivo") | stale | baja | nota/pointer a `interpretabilidad/resultados.md` (no reescribir §Q6) |
| A3 | `mammoth_entendimiento/README.md` §4 OBJ-A + §5 listan OBJ-A como propuesto/pendiente | stale | media | marcar EJECUTADO con pointer; actualizar §5 |
| A4 | Memoria [[feedback-benjamin-entender-mammoth]] (item 5 + how-to 4) pide "correr la interpretabilidad" como pendiente | stale | media | ADDENDUM 30-jun: ejecutado + hallazgo morfología-no-clase |
| A5 | Memoria [[mammoth-investigacion-integracion]] (hilo rendimiento) no enlaza la confirmación visual del mecanismo | redundancy/link | baja | 1 línea: la especialización morfológica se confirmó visual (OBJ-A), coherente con cuello=datos |
| A6 | No hay memoria atómica del tooling + hallazgo de interpretabilidad (reusable para OBJ-B / más slides) | gap | media | NUEVA memoria `mammoth-interpretabilidad-objA` + índice |
| A7 | Skill `@mammoth` no apunta al script de interpretabilidad | gap | baja | 1 línea + pointer (edición concisa, [[edicion-concisa-agentes-skills]]) |
| A8 | Preferencia "trabajar siempre en main" no estaba registrada | feedback | media | RESUELTO esta sesión: memoria [[git-trabajar-en-main-por-defecto]] + índice |

## Detalle por hallazgo

### A1 — CLAUDE.md Hallazgo 12, ADDENDUM 29-jun (stale: plan → ejecutado)
- **Dice** (CLAUDE.md:787-789): *"La librería trae el tutorial de interpretabilidad
  (`tutorial_mammoth_visualization.py`…) → objetivo barato Etapa 0."* — redactado como plan.
- **Realidad**: OBJ-A ejecutado 30-jun. Script propio `scripts/mammoth_interpretability.py`
  (adaptación del tutorial), 4 slides TCGA-BRCA (2 pos + 2 neg) del checkpoint cdis drop-in.
- **Canónico**: CLAUDE.md = regla/hecho durable. **Fix**: ADDENDUM 30-jun **aditivo** (no
  reescribir el texto 29-jun pre-registrado) con el hallazgo clave + pointer a `resultados.md`.
- **Hallazgo clave a registrar**: los expertos rutean por **MORFOLOGÍA, no por la etiqueta de
  la slide** (e8 epitelio celular también en negativos) → detectores de tejido, no de clase →
  **coherente con Hallazgo 12** (la especialización existe pero el cuello no está en la 1ª capa).

### A2 — respuestas_preguntas_benjamin.md §Q6 (stale: pointer)
- **Dice** (:309-312): "Costo barato… Etapa 0… lo que propongo como objetivo".
- **Fix**: nota de 1 línea al final de §Q6 ("EJECUTADO 30-jun → ver interpretabilidad/resultados.md").
  NO reescribir el cuerpo (es el material de estudio de la reunión; conserva valor histórico).

### A3 — mammoth_entendimiento/README.md §4 OBJ-A + §5 (stale)
- **Dice**: OBJ-A como objetivo propuesto ("Qué: correr tutorial…"); §5 pendientes.
- **Fix**: encabezar OBJ-A con **EJECUTADO (30-jun)** + pointer a `interpretabilidad/resultados.md`;
  conservar el cuerpo (hipótesis pre-registrada regla 9 — NO reescribir, integridad de pre-registro).

### A4 — Memoria feedback-benjamin-entender-mammoth (stale: pendiente → hecho)
- **Dice**: item 5 "objetivo barato Etapa 0"; how-to-apply 4 "correr la interpretabilidad" (pendiente).
- **Fix**: ADDENDUM 30-jun: ejecutado, 4 slides, hallazgo morfología-no-clase, script. Actualizar índice.

### A5 — Memoria mammoth-investigacion-integracion (link)
- **Fix**: 1 línea: la confirmación VISUAL del mecanismo (OBJ-A) es coherente con "cuello=datos,
  no patch-embed"; eje entendimiento ORTOGONAL al rendimiento. Pointer a la nueva memoria A6.

### A6 — NUEVA memoria mammoth-interpretabilidad-objA (gap)
- Facts durables y reusables (OBJ-B, más slides): script + cómo correr (CPU, env-python, prefijo
  `attention_net.0.mammoth.`, config CONCH-512/auto_rank→8, `dispatch return_weights`); el h5 trae
  **features + coords juntos** (corrige el handoff §6); hallazgo morfología-no-clase + especialización
  estable cross-slide (e8 epitelio, e26 estroma, e3 ductal). Tipo `project`.

### A7 — Skill @mammoth (gap, edición concisa)
- **Fix**: 1 línea en `@mammoth` SKILL.md apuntando al script de interpretabilidad + memoria A6.

### A8 — Preferencia "main por defecto" (feedback) — RESUELTO
- Memoria [[git-trabajar-en-main-por-defecto]] creada + índice. Branch solo si regla 9/9.b lo exige.

## Coherencia verificada (sin acción)
- Agentes `trainer`/`reviewer`: OBJ-A no toca modelo/training → sin cambios.
- El eje entendimiento NO contradice "0 palancas" (Hallazgo 12): se preserva el framing ortogonal
  en todas las ediciones (ningún texto afirma que mammoth "mejora la métrica").
- `git-main-shared-pushes` sigue vigente (fetch antes de push, nunca --force).
