# Auditoría de coherencia — apertura Sprint 7 (13-jul-2026)

> Registra los avances y hallazgos de la sesión de apertura del sprint 7 (documentar
> objetivos + correcciones del deck + resolver preguntas + interpretabilidad invasión +
> re-base del deck). Doc de hallazgos ANTES de los fixes (workflow `@knowledge-audit`).
> Branch: main (documental, GPU libre `squeue` vacío, `origin/main` sin avanzar, ahead 6).
> Continúa `sprints/B6_sprint6/auditoria_coherencia/hallazgos_sesion_deck_13jul.md`.

## Resumen (id · hallazgo · tipo · acción)

| id | hallazgo | tipo | acción |
|---|---|---|---|
| S1 | **Sprint 7 abierto**: interpretabilidad CLAM vs Mammoth en 3 tareas + ¿cuántos expertos/slots? Docs en `sprints/B7_sprint7/`, roll-over `current.md` B6→B7, 6 commits locales | progreso | memoria [[sprint7-interpretabilidad-clam-vs-mammoth]] + `current.md` (hecho) |
| S2 | **CRÍTICO / LOAD-BEARING — factibilidad de checkpoints:** de las 3 tareas del sprint 7, solo `invasion_linfatica_vascular` tiene checkpoint mammoth nuestro (obj2/obj3). `tipo_histologico` y `carcinoma_ductal_insitu_presente` NO → sus mapas de expertos requieren entrenar mammoth = **GPU (gate d/b + regla 9)** | hallazgo crítico | documentado en `objetivos_sprint7.md` + slurm draft con prereqs + memoria |
| S3 | **Q1 resuelta contra código:** "peso de cada slot en el ruteo" = `combine_weights` (2ª softmax sobre los 300 slots, `mammoth.py:411`), **≠ el top-k de parches por experto** que ya existía. Script extendido (`slot_usage.csv`) | reference/error-de-terminología | memoria [[mammoth-slot-routing-weight]] + `preguntas_resueltas.md` §Q1 |
| S4 | **Gotchas de datos nuevos** (interpretabilidad/CSV): (a) `dataset_invasion_linfovascular_label.csv` tiene **CRLF de Windows** → `$3=="presente"` en awk falla por el `\r` final; (b) el CSV `_pth` se llama `linfovascular`, NO `linfatica_vascular` (el task); (c) el `slide_id` TCGA del CSV trae el **UUID completo**, pero el dir del WSI usa la **forma corta** (`${sid%%.*}`) | gotcha nuevo | memoria nueva `data-gotchas-csv-wsi-interp` |
| S5 | **Técnica de re-base del deck:** el deck B4 (10×5.625) YA usa la paleta/fuentes de Plantilla → re-base = construir a 10×5.625 y **escalar ×1.3333** al final; los diagramas reusados se auto-corrigen; portada extraída de Plantilla s00 | reference | memoria [[deck-rebase-plantilla-1610]] |
| S6 | **Matemática de magnificación de Sebastián** (interpretación de Ernesto, **A VERIFICAR**): igualar campo físico, 224@×20 (104µm) ≡ 448@×40 → `lado=P×MPP`, consistente con [[cohortes-magnificacion-fisica]] | contexto | `contexto_magnificacion.md` + ADDENDUM [[magnificacion-cpathagent-proxima-direccion]] |
| S7 | **Deck corregido y re-basado** (17 slides, 13.333×7.5): honestidad §2.3 (nombres de tejido = inspección visual, sin sign-off), 2 slides nuevas (cabezas/expertos/slots + matemática magnif), estilo (cero «—», 3ª persona, sin diálogo), subíndices s,e en slide 7 | progreso | `correcciones_deck.md` + `generate_b7_deck.py` (hecho) |
| S8 | **Agentes/skills:** `@mammoth` menciona la interpretabilidad pero no el peso de slots → clause concisa. `reviewer`/`trainer` sin cambios (sesión documental + análisis CPU, sin modelo/training/GPU) | OK/annotate | clause en `.claude/skills/mammoth/SKILL.md` |
| S9 | **Consistencia verificada:** CLAUDE.md Hallazgo 12 ya tiene el eje interpretabilidad + caveat honestidad (13-jul); `current.md` apunta a B7; sin contradicciones nuevas. La referencia "deck B6 = 15 slides" en `correcciones_deck.md` es correcta (el deck B7 re-basado son 17) | OK | sin fix |

## Detalle por hallazgo

### S2 — Factibilidad de checkpoints (LOAD-BEARING)
Verificado 13-jul: `results/obj2_mammoth/invasion_linfatica_vascular_pth/` y
`results/obj3_mammoth_keepslots/…` tienen checkpoints `clam_mammoth_*`/`kst_*` de invasión.
Para `tipo_histologico` y `carcinoma_ductal_insitu_presente` NO hay mammoth en `results/`, y
tampoco splits_kfold ni csv_new_tasks preparados. Generar sus mapas de expertos exige
entrenar mammoth (GPU). Decisión (13-jul): **opción A** — invasión CPU ya + `.slurm` draft
para las 2 (sin lanzar). El slurm tiene 3 prereqs que hoy bloquean el sbatch: formulación
(n_clases/label_dict), splits+CSV inexistentes, reviewer+OK. Detalle: `objetivos_sprint7.md`.

### S3 — Q1: "peso de slot" ≠ "top-k de parches"
El script colapsaba H y S (`mean(dim=(2,3))`) → solo tenía ranking de **expertos**. Rankear
slots exige conservar S y usar `combine_weights` (softmax sobre los 300 slots). Es un análisis
NUEVO. Implementado + validado (top slot ≈11× el uniforme). No reportar como "top-k" a secas.
Detalle: [[mammoth-slot-routing-weight]] + `preguntas_resueltas.md` §Q1.

### S4 — Gotchas de datos (nuevos)
Cazados al ubicar una slide de invasión para la corrida CPU. Costaron varios intentos:
- El CSV `_pth` de invasión (`environ/csv/dataset_invasion_linfovascular_label.csv`) tiene
  line-endings **Windows** → el campo `label` termina en `\r`; `awk '$3=="presente"'` da 0
  matches aunque `uniq` muestre "presente". Fix: `gsub(/\r/,"",$3)`.
- El CSV se llama `linfovascular` mientras el task es `invasion_linfatica_vascular_pth`.
- El `slide_id` TCGA en el CSV = `TCGA-…-DX1.<UUID>`, pero el dir del WSI en
  `TCGA_dataset_curated/` usa solo `TCGA-…-DX1` (forma corta) → `${sid%%.*}` para el dir,
  `${sid}.svs` para el archivo. El `.h5` sí usa el nombre completo.
Registrado en memoria nueva para no re-tropezar en futuras corridas de interpretabilidad.

## Fixes aplicados (esta sesión)
1. Clause concisa en `.claude/skills/mammoth/SKILL.md` (interpretabilidad ahora incluye peso de slots).
2. Memoria nueva `data-gotchas-csv-wsi-interp` (S4) + línea en `MEMORY.md`.
3. Memorias `sprint7-interpretabilidad-clam-vs-mammoth`, `mammoth-slot-routing-weight`,
   `deck-rebase-plantilla-1610` (creadas antes del audit) + ADDENDUM en la de magnificación.
4. `current.md` roll-over B6→B7 (hecho).

## Guardarraíles respetados
- Read-only sobre `clam_environ/` (solo lectura de CSV/WSI/h5/checkpoints) y `clam_testing/`;
  escritura solo bajo `clam_testing2/` + memorias en `~/.claude/`.
- Sin GPU, sin `sbatch`. La corrida de interpretabilidad fue **CPU post-hoc** (`CUDA_VISIBLE_DEVICES=""`).
- Binarios de Sebastián (`.pptx`/`.pdf` de B7) NO tocados ni commiteados (gitignored, verificado).
- Ediciones a CLAUDE.md/memorias/skills = aditivas (clause + puntero), sin reescribir reglas ni pre-registros.
