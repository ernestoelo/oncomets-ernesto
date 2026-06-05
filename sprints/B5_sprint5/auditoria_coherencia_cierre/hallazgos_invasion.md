# Auditoría de coherencia — pasada incremental "con lo actual" (invasión EN CURSO, job 4246)

> Addendum a `hallazgos.md` (H1–H9) y `hallazgos_obj2.md` (A1–A6, post-patrón 4243).
> Esta pasada audita la base de conocimiento **con el estado actual**: el job 4246
> (invasión linfática 3-clase, k=5 paired) **se lanzó el 4-jun 09:52 y está RUNNING**.
> Fecha: 2026-06-04 ~16:45. **GPU OCUPADA** (job 4246 corriendo) → pasada **documental**,
> sin git, sin tocar `data/`·`scripts/`·`tests/`·`models_mammoth/` (workaround H,
> [[working-tree-compartido-job-en-curso]]).
>
> Método: cross-lectura CLAUDE.md ↔ memorias (`mammoth-investigacion-integracion`,
> `MEMORY.md`) ↔ `progress/current.md` ↔ READMEs/resultados del hilo mammoth ↔ README
> consolidado `results/README_experimentos_mammoth_environ.md` ↔ borrador
> `resultados_invasion.md`, contra el estado real del job (`squeue -j 4246`, `logs/`,
> verdad de campo `results/obj2_mammoth/invasion_linfatica_vascular_pth/`).

## Resumen ejecutivo

| # | Hallazgo | Severidad | Acción |
|---|---|---|---|
| I1 | **7 fuentes decían invasión "NO lanzada"** — el job 4246 cerró 5-jun 06:18 (10/10 runs); veredicto = mammoth NO es palanca (regresión leve consistente vía colapso a mayoritaria) | stale (por lanzamiento) | **RESUELTO 5-jun** — propagado el veredicto a las **7 fuentes** + README §4.c completado; consistencia numérica verificada cross-doc (Δbal −0.047, ΔAUC −0.011 5/5−, recall pres 0.434 idénticos en los 5 docs de cierre) |
| I2 | Borrador `resultados_invasion.md` ↔ verdad de campo + README §Hipótesis + CLAUDE.md | OK | **sin acción** (coherente; pre-registración intacta) |
| I3 | README consolidado §4.c YA dice "EN CURSO — job 4246" (no stale); wikilinks del borrador + §4.c resuelven; naming (`GROUP=invasion`, dir `objetivo_2` = hilo mammoth) | verificación | **sin acción** |

> **Patrón de esta pasada = el mismo que `hallazgos.md` L30-35** (los fixes cuyo
> experimento motivante NO completó se **flaggean, no se aplican**, hasta que el job
> confirme el flujo). Acá los 7 stale se vuelven "CERRADO, veredicto X" al cerrar 4246
> → aplicarlos ahora a "EN CURSO" sería doble edición + deja el árbol compartido sucio
> 8h. Se difieren **deliberadamente**, enumerados, a la propagación de cierre.

---

## I1 — Stale por lanzamiento: 7 fuentes dicen invasión "NO lanzada"

- **Realidad (fuente de verdad)**: `squeue -j 4246` → RUNNING (~6h53m al auditar);
  `logs/eg_mammoth_patinv_4246.out` → clam f0–f3 completados, clam f4 (último del brazo
  CLAM) en época 0; brazo mammoth aún no arranca. Lanzado 4-jun 09:52 (`GROUP=invasion`,
  10 runs = 3-clase × k=5 × 2 brazos). Verdad de campo viva en
  `results/obj2_mammoth/invasion_linfatica_vascular_pth/clam_..._f{0..4}_20260604_0952_s1/`.
- **Fuentes stale** (todas con la misma falsedad "no lanzada"):

  | # | fuente | línea | texto stale |
  |---|---|---|---|
  | 1 | `progress/current.md` (tabla Obj 1b) | :25 | "**Invasión 3-clase = 2ª ola, NO lanzada.**" |
  | 2 | `progress/current.md` (estado inmediato) | :57 | "**Invasión linfática 3-clase (GROUP=invasion, ~25h) NO lanzada**" |
  | 3 | `objetivo_2_mammoth_patron_invasion/README.md` §Estado (checklist) | :142 | "[ ] 2ª ola: invasión 3-clase ... — no lanzada" |
  | 4 | `objetivo_2_mammoth_patron_invasion/resultados.md` (patrón, cerrado) | :139 | "La 2ª ola natural es **invasión linfática** ... aún no [lanzada]" |
  | 5 | `CLAUDE.md` Hallazgo 12 | :723 | "es la 2ª ola natural, **no lanzada**" |
  | 6 | `MEMORY.md` (línea índice) | :12 | "...invasión 3-clase **NO lanzada**." |
  | 7 | memoria `mammoth-investigacion-integracion.md` | :87 | "**Invasión linfática 3-clase (n=2814 ...) NO lanzada**" |

- **NO stale (ya current, no tocar)**: README consolidado §4.c (L172-174 → "EN CURSO —
  job 4246, RUNNING") y el borrador `resultados_invasion.md` (header EN CURSO). Solo
  estos 2 reflejan el lanzamiento → de ahí que las otras 7 queden desincronizadas.
- **Acción (DIFERIDA al cierre del job 4246)**: la propagación de cierre ya planeada
  (handoff §6.4) toca progress/current.md + memoria + MEMORY.md + CLAUDE.md H12 + README
  §4.c. **Esta auditoría añade a esa lista las 2 que el handoff NO enumera**: el checklist
  §Estado de `objetivo_2/README.md:142` (pasa a `[x] ... cerrado job 4246`) y el cierre
  narrativo del patrón `resultados.md:139` (de "aún no" a "lanzada/cerrada job 4246").
  Cada una pasa de "NO lanzada" → "CERRADO, veredicto {H1/H0/regresión}" en **una sola
  edición** cuando el veredicto exista. **NO aplicar ahora la versión intermedia "EN
  CURSO"** (churn + commit diferido por workaround H + handoff).
- **⚠️ Pre-registración**: la fuente #3 es el `objetivo_2/README.md`, que además contiene
  la **§Hipótesis pre-registrada (regla 9)** — esa sección **NO se toca**; el fix es solo
  el checklist §Estado (L142), no la hipótesis. La #4 es el **veredicto del patrón** (ya
  cerrado): su párrafo "2ª ola" es contexto forward, se actualiza el estado de la 2ª ola
  sin reescribir el veredicto del patrón.

## I2 — Coherencia del borrador `resultados_invasion.md` (OK, sin acción)

Verificado contra la verdad de campo del job 4246 y la pre-registración:
- **n y clases**: borrador §3 (total 2814; HistAI 1418 + TCGA 864 + Privado 532; clases
  no_id 1967 / ausente 479 / presente 368) = log `slide-level counts` (1→1967, 0→479,
  2→368) = README objetivo_2 §dataset = README consolidado §4.c. Coherente.
- **Composición de folds**: borrador §4 fold-0 test (ausente 48, no_id 196, presente 37,
  total 281) = suma de filas de la confusión real f0 (`test_metrics.json`: filas
  [48,196,37]). Coherente.
- **§6.4 parcial CLAM** (claramente marcado "NO es veredicto"): f0 bal_acc 0.621, macro-OVR
  AUC 0.816, recall [aus 0.333, no_id 0.801, pres 0.730] = `test_metrics.json` f0 exacto
  (balanced_acc 0.62136; test_auc 0.81601; recall = diagonal/fila de la confusión
  [[16,19,13],[14,157,25],[4,6,27]]). Coherente. Health-check pre-registrado (no colapsa
  a no_identificado) se sostiene en los 4 folds parciales.
- **Pre-registración intacta**: §Hipótesis del `objetivo_2/README.md` (H1/H0/regresión,
  métrica = balanced_acc + Δ pareado, secundaria = macro-OVR AUC, sin gate, trivial 0.333)
  NO fue reescrita; el borrador la **cita**, no la altera. Política eval B5 (bal_acc Y AUC
  juntos + confusión 3×3 + n) correctamente reflejada.
- **Placeholders correctos**: §6.1-6.3/§7/§8 marcados ⏳ (requieren brazo mammoth) — NO son
  stale, son pendientes legítimos del experimento en curso.

## I3 — Verificaciones sin acción

- **README consolidado §4.c**: L172 "Invasión linfática 3-clase (EN CURSO — job 4246,
  lanzado 4-jun)" + L174 "RUNNING ... 10 runs ... ETA ~5-jun". Current. Falta solo la tabla
  de resultados + puntero a `resultados_invasion.md` (pendiente del cierre, no stale).
- **Wikilinks**: borrador + §4.c → `[[patron-paired-comparison-reuso-splits]]`,
  `[[eval-reporte-auc-y-umbrales-obj6]]`, `[[cap-fuente-clases-tareas]]` → todos resuelven
  a memorias existentes (índice `MEMORY.md`).
- **Naming**: `GROUP=invasion` (slurm) consistente en borrador §9, README §4.c L190 y
  `objetivo_2/README.md`. El dir `objetivo_2_mammoth_patron_invasion` = continuación del
  hilo mammoth (no el "Obj 2 = magnificación" del plan) — ya aclarado en H5/progress.md.

---

## Conclusión y plan de cierre (cuando 4246 termine)

Esta pasada es **pre-cierre**: el único hallazgo real (I1) es **stale por lanzamiento**,
**diferido deliberadamente** a la propagación de cierre para no editar 7 fuentes dos veces.
El borrador y el README §4.c son coherentes; la pre-registración está intacta.

**Checklist de propagación al cerrar el job 4246** (folda I1 + handoff §6.4) — **APLICADO 5-jun**:
1. [x] `resultados_invasion.md` §6.1-6.3/§7/§8 rellenas + "EN CURSO" → "CERRADO" (veredicto:
   mammoth no es palanca; Δbal −0.047±0.064, ΔAUC −0.011±0.005 5/5−; colapso a mayoritaria).
2. [x] Veredicto propagado a las **7 fuentes de I1**: progress.md ×2, `objetivo_2/README.md:142`
   (checklist §Estado — la §Hipótesis NO se tocó), patrón `resultados.md:139`, CLAUDE.md H12,
   MEMORY.md:12, memoria `mammoth-investigacion-integracion`. `grep "no lanzada"` → 0 residuos.
3. [x] README consolidado §4.c COMPLETO (tabla 3-clase + Δ + mecanismo + puntero).
4. [x] **Addendum aditivo** a Hallazgo 12 de CLAUDE.md (hallazgo crítico: el n más grande del
   hilo NO rescató a mammoth → confirma cuello=datos; cierra el hilo: 8 tareas, 0 palancas).
   Pre-registración (§Hipótesis regla 9) intacta.
5. [x] Artefactos nuevos: `scripts/analyze_invasion.py` (análisis reproducible) +
   `figuras/slide_assets/{M01,M02,M03,T01}_invasion_*.png` (QA visual OK).
6. [ ] Commit granular → `git fetch` → push (autorizado este flujo) — GPU libre (cola vacía).

**Consistencia cross-doc verificada (estilo A2/A3):** Δbal −0.047, ΔAUC −0.011, 5/5 folds−,
recall presente 0.434, recall no_id 0.815 → **idénticos** en los 5 docs de cierre
(resultados_invasion.md, README §4.c, CLAUDE.md H12, progress, memoria). Sin drift de
transcripción. Esta pasada incremental queda **CERRADA**.
