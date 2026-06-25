# Auditoría de coherencia — cierre del eje loss-desbalance + 3 tablas del deck (B5)

> Fecha: 2026-06-25. Disparador: cierre del eje loss-desbalance (jobs 4463 focal + 4472 cb)
> y construcción de las 3 tablas comparativas del deck. Auditoría documental (read-only →
> findings → fixes). GPU: 5 jobs ajenos, 0 míos; no se toca ningún job (workaround H).
> main sincronizado con origin al iniciar.

## Resumen (id · hallazgo · tipo · severidad · acción)

| id | hallazgo | tipo | sev | acción |
|---|---|---|---|---|
| F1 | Memoria [[calibracion-operating-point-palanca-b5]] dice **Tier 1 "INICIADO/lanzado job 4463"** (L33-36) + índice MEMORY.md "Tier 1 INICIADO 23-jun". El Tier 1 (loss) está **CERRADO = H_reg**. | stale | media | actualizar a "Tier 1 CERRADO = NO palanca (H_reg)"; el fracaso del análogo en-training **refuerza** Tier 0 (post-hoc) como la palanca barata sobreviviente |
| F2 | Memoria [[insuficiencia-datos-ejes-investigacion]] dice loss "**en ejecución**" (L40) y "**barato, en curso**" (L46). Cerrado null/H_reg. | stale | media | actualizar el eje 3 (desbalance) y la escalera de riesgo a "loss-desbalance CERRADO: null/H_reg" |
| F3 | Memoria [[deck-completo-pptx-buildable]] dice **"20 slides"** (L12, L63). El deck tiene **21** (slide CLAM+loss agregada). | stale | baja | L12 → 21 slides; L63 extender la cadena evolutiva (17→20→21) con la slide CLAM+loss |
| F4 | Cierre del eje (focal/cb NO palanca, H_reg) — ¿está canónicamente documentado? | — (verificación) | — | **SÍ, sin acción**: CLAUDE.md Hallazgo 14 (único), `resultados.md`, [[loss-desbalance-eje-c1]], MEMORY.md ya consistentes (hechos en Fase A/B de la sesión) |
| F5 | Gotcha del bug cb (no-op batch=1) — ¿canónico y propagado? | — (verificación) | — | **SÍ, sin acción**: [[mil-weighted-ce-noop-batch1]] (gotcha reusable) + línea en CLAUDE.md "Modelos alternativos" + ADDENDUM prereg + test 6/6. Coherente |

## Detalle

### F1 — calibración: Tier 1 (loss) cerrado, refuerza Tier 0
- **Qué dice cada fuente:** la memoria de calibración enumera Tier 0 (post-hoc, gratis) y
  Tier 1 (loss, toca training). El Tier 1 quedó marcado "INICIADO 23-jun, lanzado job 4463".
  La verdad de campo (jobs 4463 focal + 4472 cb): **NI focal NI cb son palanca = H_reg**
  (re-balanceo del operating-point; el AUC no se mueve) — ver [[loss-desbalance-eje-c1]],
  CLAUDE.md Hallazgo 14, `sprints/B5_sprint5/loss_desbalance/resultados.md`.
- **Canónico:** el veredicto del eje vive en `loss-desbalance-eje-c1` + Hallazgo 14. La
  memoria de calibración solo necesita **apuntar al cierre** y extraer la implicación: el
  análogo *en-training* de la calibración (re-pesar la pérdida) **falló igual** → la
  calibración **post-hoc** (Tier 0) sigue siendo la palanca barata sobreviviente, y el
  fracaso de Tier 1 la **refuerza** (no la invalida): el mecanismo H_reg es exactamente
  "mover el punto de operación", que post-hoc se hace sin re-entrenar y eligiendo el umbral
  en val.
- **Fix:** actualizar L33-36 de la memoria + la línea de índice MEMORY.md.

### F2 — insuficiencia de datos: loss cerrado
- La memoria lista 3 ejes que atacan los DATOS; el 3º (desbalance: loss + calibración) dice
  loss "en ejecución". Cerrado null/H_reg. La escalera de riesgo (Tier 0 → loss → HistAug →
  TITAN) sigue válida, solo que **loss ya se subió y no movió la aguja**; HistAug/TITAN
  (mayor techo, sobre los datos) quedan como los ejes no probados.
- **Fix:** L40 y L46 → "loss-desbalance CERRADO: null/H_reg (jobs 4463/4472)".

### F3 — deck 20 → 21 slides
- La memoria del deck buildable cita "20 slides" como estado del caso de referencia. Se
  agregó la slide **CLAM + loss rebalanceada** (entre cierre-3-ejes y próximos pasos) → 21.
  `convenciones_deck_b5.md` (repo, canónico) ya está en 21 (actualizado en la sesión).
- **Fix:** L12 → 21; L63 extender la cadena evolutiva con la slide CLAM+loss (25-jun).

### F4/F5 — verificaciones sin acción (ya canónico)
- **F4 (cierre del eje):** Hallazgo 14 es único en CLAUDE.md, números coherentes con
  `resultados.md` y la memoria; links `[[...]]` resuelven (verificado en Fase B). El snapshot
  AM de `auditoria_hallazgos.md` quedó con su ADDENDUM de cierre (no reescrito).
- **F5 (gotcha bug cb):** [[mil-weighted-ce-noop-batch1]] es el canónico reusable; CLAUDE.md
  lo referencia en "Modelos alternativos en NUESTRO repo"; el ADDENDUM del prereg da la
  provenance; el test de regresión a batch=1 (6/6) lo blinda. Sin redundancia dañina.

## Fixes aplicados por esta auditoría (todos en memorias — fuera del repo)
1. [[calibracion-operating-point-palanca-b5]] L33-36 + MEMORY.md índice: Tier 1 CERRADO = H_reg, refuerza Tier 0.
2. [[insuficiencia-datos-ejes-investigacion]] L40/L46 + MEMORY.md índice: loss CERRADO null/H_reg.
3. [[deck-completo-pptx-buildable]] L12/L63 + MEMORY.md índice: deck 21 slides.

> El único artefacto **versionado** de esta auditoría es este findings doc. Las 3 fixes son a
> memorias (`~/.claude/...`, no en el git del repo). El cierre del eje y el gotcha ya quedaron
> canónicos en la Fase A/B de la sesión (CLAUDE.md Hallazgo 14, resultados.md, prereg ADDENDUM).
