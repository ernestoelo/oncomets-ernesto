# Auditoría de coherencia B5 — notación matemática del deck + zoom MoE (slide 6)

> Mini-audit puntual (17-jun-2026), gatillada al cerrar la sesión de **estudio del deck**
> `CLAM_Sprint_B5`. Cubre lo NUEVO de la sesión (motor de notación sub/superíndice real,
> panel "lentes paralelas" para las cabezas, molde "árbol ramificado" del zoom MoE) + los
> **pendientes de registro** del handoff §10 + el **typo de balance** ya corregido. NO
> reabre el grueso B5 (`hallazgos.md`, `hallazgos_pathpt.md`, `hallazgos_diagrama_pathpt.md`).
> Fronts tocados: **skills/convenciones** (`convenciones_deck_b5.md`), **instrucciones**
> (`CLAUDE.md`, pointer), **memoria** ([[diagramas-arquitectura-pptx-editable]]).

## Resumen

| id | hallazgo | tipo | sev | acción |
|----|----------|------|-----|--------|
| N1 | "Carlito + Unicode plano" (§5) no alcanza: no hay subíndice Unicode para muchas letras (`q`, `w`...) → `Wq` quedaba con `q` a tamaño normal | reconciliation | media | ADDENDUM §5: motor `_add_runs` (baseline OOXML real) |
| N2 | molde "árbol ramificado" (fan-out/fan-in) del zoom MoE sin registrar (handoff §10b) | stale (pendiente) | media | §5.c nuevo |
| N3 | panel "lentes paralelas" (cómo volver visual un concepto fino: multi-head) sin registrar | stale (pendiente) | baja | §5.c |
| N4 | formato de notas `PROPÓSITO/PUNTOS CLAVE` (blanco) supera el B2 de CLAUDE.md, sin registrar (handoff §10a) | stale | baja | §3.b nuevo + pointer en CLAUDE.md |
| N5 | balance microcalc·CDIS rotulado `~20%` en la tabla del "hallazgo crítico" (real 36%) | error | media | YA corregido; queda tensión de prosa (detalle abajo) |

## Detalle

### N1 — notación: baseline real, no solo Unicode plano  *(reconciliation)*
- **Qué decía** `convenciones_deck_b5.md` §5: *"Texto en Carlito + Unicode plano (`ℝ⁵¹²`,
  `θ`, `⟨⟩`) → rasteriza limpio"*. Correcto para lo que Unicode SÍ tiene.
- **El problema**: Unicode **no tiene subíndice** para `q`, `w` y muchas letras → `Wq`
  renderizaba la `q` a tamaño normal (lo que Ernesto reportó: *"los índices no quedaron
  bien en todos los símbolos"*).
- **Canónico/fix**: ADDENDUM a §5. `generate_clam_mammoth_pptx.py` ahora trae un mini-markup
  (`_x` / `_(xx)` subíndice, `^x` / `^(xx)` superíndice) → helper `_add_runs` que emite runs
  con `baseline` OOXML real (−25%/+30%, tamaño 0.62×). Funciona para CUALQUIER letra,
  rasteriza limpio en **LibreOffice y PowerPoint**, y queda editable. Verificado: 22 sub +
  8 super en slide 6, 0 markup crudo filtrado.
- **Regla**: Unicode plano cuando alcanza; baseline real (`_add_runs`) para subíndices que
  Unicode no representa. **Evitar `_`/`^` literales** en los strings fuente (`auto_rank` →
  `automático`).

### N2 + N3 — molde "árbol ramificado" + panel "lentes paralelas"  *(pendiente §10b / nuevo)*
- Pendiente del handoff §10b (registrar el molde del zoom MoE) + el panel de cabezas nuevo.
- **Canónico/fix**: §5.c nuevo en `convenciones_deck_b5.md`. Resumen: tronco vertical que se
  abre (fan-out) a 3 expertos representativos + `· · ·` y converge (fan-in) en la combinación;
  callouts laterales (LoRA azul, banner "mismo presupuesto", nota integración); **panel
  "lentes paralelas"** para explicar las CABEZAS (3 criterios + `×16` + "se concatenan"), del
  lado opuesto al callout LoRA, en la familia de color del bloque que anota. Aprobado 17-jun
  (*"así me gusta más"*). Distinto del molde **cascada de 3 ramas** (§5.b, multi-stream): acá
  es **1 stream que se abre y cierra**.

### N4 — formato de notas del presentador  *(stale)*
- Pendiente del handoff §10a. CLAUDE.md (§Formato de entregables) fija el formato de notas
  "BLOQUE N — Título" de B2, pero el deck B5 usa `PROPÓSITO — …/ narrativa / PUNTOS CLAVE`,
  **texto blanco** (`set_notes` en `generate_b5_deck.py`), porque Ernesto las lee sobre panel
  oscuro y orientadas a exponer (no a re-explicar el gráfico).
- **Canónico/fix**: §3.b nuevo en `convenciones_deck_b5.md` + **pointer aditivo** en CLAUDE.md
  (la línea B2 queda, con "(deck B5 evolucionó a …)").

### N5 — balance microcalc·CDIS 20% → 36%  *(error, ya corregido)*
- La tabla del "Hallazgo crítico" de `objetivo_2_mammoth_patron_invasion/resultados.md`
  rotulaba CDIS `~20%`; el real es **36%** (118 pos / 328, desbalance 1.8×). El **deck SÍ
  decía 36%** (correcto); el error era solo del doc fuente. **Corregido** (`~20%`→`~36%`).
- **Tensión residual (NO tocada — toca un argumento cerrado)**: con 36%, la prosa que sigue
  agrupa a cdis entre *"domina el desbalance o faltan positivos"*, lo cual queda flojo (cdis
  es moderadamente balanceada). La afirmación fuerte del deck **sobrevive** (el lean+ solo
  asoma en las 2 MÁS balanceadas, tejido/cribiforme; cdis no aporta lean+). Recomendación:
  reformular cdis como *contraejemplo* (balanceada pero regresa) — **queda a decisión de
  Ernesto** (es editar un hallazgo cerrado; surfaceado, sin respuesta aún). El deck es
  internamente consistente (36% + leve regresión).

## Guardrails respetados
- En `main`, sincronizado (0/0), `git fetch` hecho; jobs ajenos en GPU **no tocados** (audit
  documental, sin GPU, sin branch-switch — workaround H).
- Containment: solo bajo `oncomets-ernesto/` + memorias en `~/.claude/...`. Sin tocar
  `clam_environ/` ni `clam_testing/`. NO se commitea `papers/presentations/` (gitignored).
- Pre-registración intacta: N5 NO reescribe el argumento cerrado (solo el número factual).
