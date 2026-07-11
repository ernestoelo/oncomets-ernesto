# Auditoría de coherencia — sesión Tier 0 + magnificación (10-jul-2026, tarde)

> Registra los hallazgos críticos de la sesión y propaga el avance a las 4 frentes
> (CLAUDE.md, memorias, agentes/skills, sprint docs). Doc de hallazgos ANTES de los fixes
> (workflow `@knowledge-audit`). Branch: main (auditoría documental, GPU libre, `squeue` vacío).

## Resumen (id · hallazgo · tipo · acción)

| id | hallazgo | tipo | acción |
|---|---|---|---|
| F1 | Tier 0 estaba "descrita, nunca ejecutada" → **EJECUTADA** con resultado | stale | actualizar CLAUDE.md L732-734 + memoria (hecho) |
| F2 | **Drift de features TCGA** (re-extraídas 26-27 jun) — hazard nuevo de reproducibilidad | error/nuevo | pointer en CLAUDE.md L288 + memoria nueva (hecho) |
| F3 | HistAI "sin MPP → PENDIENTE" → **resuelto operativamente** (generic-tiff, excluido del piloto) | stale | actualizar [[cohortes-magnificacion-fisica]] + nota CLAUDE.md |
| F4 | Magnificación B6 avanzó: **pre-registrada + wrapper + `.slurm` listos** (no lanzado) | progreso | ADDENDUM en [[magnificacion-cpathagent-proxima-direccion]] |
| F5 | Diseño multi-escala (µm/px por cohorte, 3 brazos A/B0/B) = contexto valioso a persistir | contexto | folded en F4 + prereg_magnificacion.md (canónico) |
| F6 | Agentes/skills | OK | sin cambios (no tocan lo de esta sesión) |

## Detalle por hallazgo

### F1 — Tier 0 ejecutada (era stale como "pendiente")
- **Antes:** CLAUDE.md L732-734 "palanca viva post-cierre = Tier 0" (implica no corrida);
  memoria `calibracion-tier0-pendiente-ejecutar` = "descrita y nunca ejecutada".
- **Ahora (canónico = memoria + `sprints/B6_sprint6/tier0_calibracion/resultados.md`):** ejecutada
  10-jul. **mitotic Δbal_acc +0.046 ± 0.029 (5/5+)** win; **invasión null** (+0.009); **necrosis null**
  (−0.005). Palanca real task-dependiente (rinde donde hay colapso a la mayoritaria).
- **Fix:** memoria actualizada (hecho en la sesión); CLAUDE.md L732-734 → refleja "ejecutada, resultado".

### F2 — Drift de features TCGA (hazard nuevo)
- **Hallazgo:** un subconjunto de `.pt` TCGA en `clam_environ/environ/features/pt_files/` tiene mtime
  **26-27 jun 2026** (posterior a runs de jun 4/10) → re-inferir hoy **diverge del `.pkl` congelado**
  (invasión 92 slides, mitotic 31, necrosis 13). Es el hazard "dir live que muta" materializado.
- **Canónico:** memoria nueva `features-tcga-drift-reextraccion` (creada en la sesión).
- **Fix:** pointer conciso en CLAUDE.md L288 (donde se describe features/pt_files como "live; crece").

### F3 — HistAI MPP resuelto
- **Antes:** [[cohortes-magnificacion-fisica]] fila HistAI = "sin metadata confiable → PENDIENTE".
- **Ahora (canónico = `histai_magnificacion.md`):** `vendor=generic-tiff`, resolución 10 px/cm =
  placeholder → MPP no recuperable; dims level0 ~40× **no concluyente**; **excluido del piloto**
  (minoría 45-49/333); el wrapper lo salta solo (`resolve_mpp`→None).
- **Fix:** actualizar la fila/nota HistAI de la memoria a "resuelto operativamente (excluido)".

### F4/F5 — Avance magnificación B6 (pre-registro + wrapper + slurm)
- **Deliverables nuevos:** `prereg_magnificacion.md` (3 brazos A/B0/B, escalas 112µm+512µm en µm/px
  por cohorte, fusión promedio, H1/H0/H2), `scripts/extract_multiscale_features.py` (wrapper, bug
  openslide+workers corregido), `extract_multiscale.slurm` (preflight + stage1/2), `review_regla9.md`
  (self-review inline; pase formal del reviewer PENDIENTE por límite de API),
  `microcalc_slidelist_tcga_privado.csv` (283 slides).
- **Fix:** ADDENDUM 10-jul (tarde) en [[magnificacion-cpathagent-proxima-direccion]] + refrescar su
  frontmatter description (stale: hablaba de "leer CPathAgent semana 29-jun").

### F6 — Agentes / skills
- `reviewer`/`trainer` y skills: sin cambios necesarios (esta sesión no cambió sus reglas). El
  `reviewer` se usó tal cual (se cortó por API, no por su definición).

## Guardarraíles respetados
- Read-only sobre `clam_environ/`; escritura solo bajo `clam_testing2/` y memorias en `~/.claude/`.
- Sin GPU, sin tocar jobs (squeue vacío). Pre-registro (regla 9) NO reescrito retro — se agrega addendum.
- Ediciones a CLAUDE.md = aditivas/punteros concisos (no reescriben reglas duras).
