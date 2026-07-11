# Self-review regla 9 — experimento magnificación multi-escala

> **Nota de gobernanza:** el pase del subagente `reviewer` se **interrumpió por límite de
> sesión de la API** (no por un hallazgo). Esta es una validación **inline** hecha por la
> sesión principal contra el checklist del reviewer. **El pase formal del `reviewer` queda
> PENDIENTE** y es requisito antes de commitear el wrapper/pipeline y antes de cualquier
> `sbatch`. No se commitea el pipeline sin ese OK.

## Checklist regla 9 (+9.a/9.b)

| Ítem | Veredicto | Evidencia |
|---|---|---|
| Hipótesis enunciada de antemano (primaria + alternativa + regresión) | ✅ | `prereg_magnificacion.md` §4 (H1/H0/H2) |
| Métrica + subset + dirección predefinidos | ✅ | §4-§5: balanced_acc **Y** AUC, subset context-hungry (`en_cdis`, `en_carcinoma_invasivo`), dirección Δ pareado ≥0 consistente |
| Argumento clínico/arquitectónico ANTES del código | ✅ | `investigacion_magnificacion.md` §2-§5 (etiqueta CAP contextual → falta contexto, no zoom) |
| 9.a — evita umbral GO/NO-GO rígido, interpreta por signo/magnitud | ✅ | §5: "sin GO/NO-GO numérico; consistencia de signo + magnitud vs varianza" |
| 9.b — ¿decisión revisitada de un eje descartado? | ✅ **NO aplica** | magnificación = **Eje A** *futuro recomendado* en `sprints/B4_sprint4/ejes_futuros_microcalc.md` L10/L114 ("magnificación primero — argumento clínico más fuerte"), propuesto por Sebastián. NO es un descarte reabierto → 9.b no gatilla. El eje arquitectura (Hallazgos 11-14) NO se reabre: magnificación ataca dato/contexto |
| Comparación PAIRED (reuso splits, Δ pareado) | ✅ | §3: 3 brazos (A/B0/B) sobre los mismos splits k=5; Δ pareado por fold |
| Containment + read-only clam_environ (regla 2) | ✅ | wrapper importa de clam_environ pero escribe solo bajo `clam_testing2/`; check de containment en `main()` |
| GPU solo vía sbatch + preflight (workaround B/G) | ✅ | `extract_multiscale.slurm`: binario absoluto del env, bloque PREFLIGHT que aborta en segundos |

## Refinamiento del Eje A (no es contradicción)

`ejes_futuros_microcalc.md` §Eje A lo planteó como *"más zoom"*. La investigación B6 lo **refina**
con argumento clínico: la etiqueta CAP es contextual → lo que falta es una escala **más gruesa**
(contexto del anfitrión), NO más zoom (§2.3 de la investigación aborda explícitamente esa "trampa").
El diseño **supera** el encuadre naïve del Eje A, no lo contradice.

## Revisión de código — `scripts/extract_multiscale_features.py`

| Aspecto | Veredicto | Nota |
|---|---|---|
| µm/px → px por slide | ✅ | `fine_px=round(112/mpp)`, `ctx_px=round(512/mpp)`; `mpp` leído por slide (`resolve_mpp`) con banda [0.1,1.0] |
| Contexto centrado en el mismo center del grid | ✅ | `center = coord + patch_size_l0//2`; fino y contexto leen centrados en (cx,cy) |
| Lectura eficiente (mejor nivel de pirámide) | ✅ | `get_best_level_for_downsample(size/224)` → lee del nivel correcto y reescala (TCGA fino cae en level1 = 20× nativo → escala física correcta) |
| Fusión promedio → [N,512] | ✅ | `v=0.5*(vf+vc)`; `torch.cat(...).float()` → float32 [N,512] |
| Bordes | ✅ | clamp de la location a [0, dim−size] (no black-fill) |
| Skip slides sin MPP (HistAI) | ✅ | `resolve_mpp` → None → `skipped` |
| `get_encoder('conch_v1')` → (model, img_transforms) | ✅ | verificado en `clam_environ/models/builder.py:46-82`; forward = `encode_image(normalize=False)` → 512-d |
| Layout `features/pt_files` para train_dsmil | ✅ | corregido: escribe `<out>/features/pt_files` |
| **BUG corregido** — openslide + DataLoader workers | ✅ **FIX** | handle openslide NO es fork-safe → `num_workers` bajado a **0** (era 4) |

## Bloqueadores / observaciones abiertas (para el pase formal)

1. **PENDIENTE pase formal del reviewer** (se cortó por API). No commitear pipeline sin él.
2. **Stage 1 (create_patches_fp) sin dry-run:** el esquema exacto del `--process_list` (nombres de
   columna que espera) no se validó en ejecución → confirmar con un dry-run CPU antes del job real.
3. **Co-firma de Sebastián sobre las escalas** (112µm/512µm, fusión promedio) — gate exploratorio
   ([[gobernanza-gate-cofirma-sebastian]]), a llevar a la reunión del lunes.
4. **Re-entrenar brazo A** sobre features actuales (drift TCGA, ver Tier 0) — no reusar checkpoints viejos.
