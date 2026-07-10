# Hallazgos de la sesión 9-jul (tarde) — captura para futuras sesiones

> Captura vía `@knowledge-audit` de los hallazgos con valor de contexto que dejó la
> ronda de ediciones del deck del viernes (B6, mammoth/interpretabilidad). Findings
> primero; los fixes ya aplicados se marcan RESUELTO. NO toca modelo/training (regla 9
> N/A). Estado git al momento: rama `main`, working tree con cambios sin commitear
> (deck + docs); commit/push = decisión de Ernesto.

## Resumen

| id | hallazgo | tipo | severidad | acción |
|---|---|---|---|---|
| F1 | Recap "Recapitulación de objetivos" debía usar el molde B4 (lista numerada), no tarjetas | feedback | media | RESUELTO — memoria [[deck-molde-fiel-referencia]] + slide corregida |
| F2 | `convenciones_deck_b6.md` §5: mapa de slides + diagramas reusados quedaron stale | stale | baja | RESUELTO — ADDENDUM 9-jul en §5 |
| F3 | `MEMORY.md`: link `humanizer-es.md` roto (archivo real = `humanizer-es-skill.md`) | error | baja | RESUELTO — link corregido en el índice |

## Detalle

### F1 — Molde de la slide de objetivos (feedback durable)
Armé el recap con tarjetas; Ernesto pidió *"el mismo formato que el sprint B4"*. El
volcado real de `CLAM_Sprint_B4.pptx` slide 2 = **lista numerada en un cuadro** (título
32pt Barlow ExtraBold `#217589`; cuerpo 24pt Barlow bold `#595959`, línea entre ítems).
Corregido. Lección durable (reusable en cualquier deck): **replicar el molde real, no
reinventarlo** → memoria [[deck-molde-fiel-referencia]]. Refuerza el ítem 6 de
[[feedback-benjamin-entender-mammoth]] ("fuente"=tipografía, match del template).

### F2 — Mapa de slides de convenciones stale
El §5 describía la estructura del build de las 15:25 (interior/tensor y keep_slots como
diagramas reusados; heatmaps y top-k en slides separadas). La ronda 9-jul cambió eso
(ver ADDENDUM en `convenciones_deck_b6.md` §5). Mapa vigente: 1 portada · 2 recap · 3
divisoria MAMMOTH · 4 qué es y por qué (acrónimo + Fig1+Fig3) · 5 pipeline (reusado) · 6
interior math+código (nativo) · 7 flujo arquitectura oficial (reusado DIAG_FUSED s0 +
variables) · 8 keep_slots math+código (nativo) · 9 divisoria Interpretabilidad · 10
heatmaps+top-k (fusión) · 11 tejido≠clase + honestidad (fusión).

### F3 — Link roto en el índice de memorias
`MEMORY.md` apuntaba a `humanizer-es.md`; el archivo real es `humanizer-es-skill.md`.
Corregido el destino del link (no se renombró el archivo).

## Verificación de coherencia (sin contradicciones nuevas)
- La slide 6 del deck rotula las cabezas como **subespacios (multi-head), no
  textura/forma/color** → alineado con la corrección del ítem 1 de
  [[feedback-benjamin-entender-mammoth]] (el error del deck B5 no se reprodujo en B6).
- Eje = ENTENDIMIENTO, ortogonal al "0 palancas" (Hallazgo 12) → sin reapertura de
  rendimiento. Consistente con CLAUDE.md.
