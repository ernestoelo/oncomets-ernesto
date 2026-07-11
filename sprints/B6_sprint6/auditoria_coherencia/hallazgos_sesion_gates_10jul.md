# Auditoría de coherencia — sesión GATES (a)+(c) magnificación (10-jul-2026, noche)

> Registra los hallazgos críticos de la sesión (cierre de los gates ejecutables del pre-registro
> de magnificación) y propaga el avance a las 4 frentes (CLAUDE.md, memorias, agentes/skills,
> sprint docs). Doc de hallazgos ANTES de los fixes (workflow `@knowledge-audit`). Branch: main
> (auditoría documental, GPU libre, `squeue` vacío). Continúa `hallazgos_sesion_tier0_magnif_10jul.md`.

## Resumen (id · hallazgo · tipo · acción)

| id | hallazgo | tipo | acción |
|---|---|---|---|
| G1 | Gate (a) reviewer estaba "PENDIENTE por límite de API" → **PASE FORMAL COMPLETADO** (APRUEBA CON OBSERVACIONES) | stale/progreso | actualizar `review_regla9.md` (hecho) + ADDENDUM memoria + current.md |
| G2 | Gate (c) dry-run stage-1 → **cazó BUG bloqueante int64** en `create_patches_fp` + `--process_list` | error/nuevo crítico | fix en `extract_multiscale.slurm` (hecho) + memoria nueva + §Gate(c) en review_regla9 + workaround en CLAUDE.md |
| G3 | Gotcha int64 = fact durable cross-sprint (toda re-extracción con IDs numéricos) | contexto durable | memoria nueva `[[create-patches-processlist-int64-privado]]` (hecha) + workaround CLAUDE.md |
| G4 | Conteo del piloto: pre-registro decía 284 (privado 77) → real **283 (privado 76)** | error | corregido en prereg + investigación (hecho) |
| G5 | O3 reviewer: stage-3 necesita **preflight minpatch** sobre feature dirs NUEVOS (parches grandes → menos parches → crash topk) | forward-looking | anotado en review_regla9 §Bloqueadores; a incorporar en el `.slurm` de stage-3 |
| G6 | Gates (b) co-firma Sebastián y (d) OK Ernesto siguen pendientes | estado | reflejado en current.md + memoria; NO lanzado |
| G7 | Agentes/skills | OK | sin cambios (el `reviewer` se usó tal cual y aprobó) |

## Detalle por hallazgo

### G1 — Gate (a): pase formal del reviewer COMPLETADO
- **Antes:** `review_regla9.md` = "pase formal PENDIENTE (se cortó por límite de API)"; solo self-review inline.
- **Ahora (canónico = `review_regla9.md` nota de gobernanza + §checklist):** subagente `reviewer` ejecutado,
  veredicto **APRUEBA CON OBSERVACIONES**. Regla 9/9.a íntegras, 9.b N/A (magnificación = Eje A recomendado en
  `ejes_futuros_microcalc.md`, no un descarte reabierto — verificado por el reviewer), containment + workflow
  SLURM (workarounds B/G/D) OK, comparación paired, y **código correcto en todas las rutas load-bearing**
  (matching de nombres TCGA barcode+UUID, centro del crop vs grid, nivel de pirámide, fusión promedio→[N,512],
  layout `features/pt_files`). 5 observaciones (O1–O5), ninguna bloquea el commit.
- **Fix:** `review_regla9.md` actualizado (nota de gobernanza + bloqueadores + §Gate(c)); ADDENDUM en
  [[magnificacion-cpathagent-proxima-direccion]]; `progress/current.md` paso 5.

### G2 — Gate (c): BUG bloqueante int64 (el hallazgo crítico de la sesión)
- **Hallazgo:** el dry-run CPU de stage-1 (1 slide/cohorte, sin GPU) reveló que `create_patches_fp.py:277`
  re-lee el `--process_list` con `pd.read_csv` **sin `dtype`** → los `slide_id` privados **numéricos puros**
  (`105040`) se infieren `int64` → `get_clean_slide_name` llama `.replace` sobre un int (`environ_utils.py:182`)
  → crash `'numpy.int64' object has no attribute 'replace'`. **Habría tumbado las 76 slides privadas** del piloto
  (status `failed` en el log, NO en el preflight); TCGA se salva (IDs con letras). Sebastián no lo pega porque su
  flujo normal de privado no usa `--process_list`.
- **Fix (no toca clam_environ, regla 2):** stage-1 del `.slurm` pasa a **symlink-farm plano** por cohorte (una
  symlink por WSI del piloto) y corre `create_patches_fp` SIN `--process_list` ni `--nested_folders` — en modo
  flat los nombres salen de `os.listdir` = strings. **Verificado end-to-end** TCGA(.svs)→`…291.h5` (N=11324,
  patch_size=482) y privado(.bif)→`105040.h5` (N=3411, patch_size=241); `.h5` en `<save_dir>/patches/`, attr
  `patch_size` sobre `coords` = el que lee el wrapper (L163), stem = slide_id que usa `find_wsi`.
- **Canónico:** `review_regla9.md` §Gate(c) (tabla + raíz + fix) + memoria [[create-patches-processlist-int64-privado]].

### G3 — Gotcha int64 durable (contexto para futuras sesiones)
- Cualquier pipeline propio que restrinja slides vía `--process_list` sobre una cohorte de IDs numéricos falla
  igual; y clam_environ es read-only → no se puede parchear el `pd.read_csv`. El patrón "flat-farm sin
  process_list" vale para **toda** re-extracción futura que reuse `create_patches_fp`.
- **Fix:** memoria nueva (hecha) + entrada concisa en la sección **Workarounds** de CLAUDE.md (workaround I) con
  puntero a la memoria — es un "síntoma → fix sin re-investigar", exactamente el propósito de esa sección.

### G4 — Conteo del piloto (283, no 284)
- El slidelist real (`microcalc_slidelist_tcga_privado.csv`) y el preflight = **283** (TCGA 207 + privado 76). El
  pre-registro decía 284 (privado 77). Una slide privada del set identificado (77) no entró al slidelist.
- **Fix:** corregido en `prereg_magnificacion.md` y nota en `investigacion_magnificacion.md` (privado 76 en el
  piloto; el 77 es el set identificado completo). Confirmar cuál cae al consolidar los `.h5`.

### G5 — O3: preflight minpatch en el stage-3 (forward-looking)
- El grid común de 112 µm usa parches **más grandes** (TCGA 482 px, privado 241 px) que el 256 estándar → **menos
  parches/slide** → mayor riesgo del crash `topk`/`inst_eval` (B=8, bug run 4096). El `.slurm` de **entrenamiento**
  debe llevar el **preflight minpatch** (workaround G) apuntando a los feature dirs NUEVOS (`$FEAT_B0`/`$FEAT_B`).
- **Acción:** anotado en `review_regla9.md` §Bloqueadores #5; a incorporar al `.slurm` de stage-3 cuando se prepare.

### G6 — Gates (b)/(d) pendientes (estado, no cerrado por esta sesión)
- (b) co-firma de Sebastián sobre las escalas (112µm/512µm, fusión promedio) → reunión **lunes** (13-jul), gate
  NO bloqueante ([[gobernanza-gate-cofirma-sebastian]]). (d) OK explícito de Ernesto para `sbatch` (job de fin de
  semana). Reflejado en `progress/current.md`. **Nada lanzado a GPU; nada pusheado sin pedido.**

### G7 — Agentes / skills
- `reviewer` se invocó tal cual y aprobó; su definición no cambió. `trainer` no se usó (sin GPU). Skills sin cambios.

## Guardarraíles respetados
- Read-only sobre `clam_environ/`; escritura solo bajo `clam_testing2/` y memorias en `~/.claude/`. Dry-run a dir
  throwaway bajo el repo, borrado tras verificar (containment).
- Sin GPU (dry-run en CPU con `CUDA_VISIBLE_DEVICES=""`), sin tocar jobs (squeue vacío).
- Pre-registro (regla 9) NO reescrito retro (solo corrección factual del conteo + registro del pase del reviewer).
- Ediciones a CLAUDE.md = aditivas (workaround I nuevo + puntero conciso), no reescriben reglas duras.
