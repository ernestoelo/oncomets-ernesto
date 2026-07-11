# Self-review regla 9 — experimento magnificación multi-escala

> **Nota de gobernanza:** el pase del subagente `reviewer` se interrumpió por límite de API
> en la sesión del 10-jul (dejó esta validación **inline**). **PASE FORMAL COMPLETADO el
> 10-jul (sesión posterior):** veredicto **APRUEBA CON OBSERVACIONES** — regla 9/9.a íntegras,
> 9.b N/A (magnificación = Eje A recomendado, no un descarte reabierto), containment + workflow
> SLURM (workarounds B/G/D) OK, comparación paired por construcción, y código correcto en todas
> las rutas load-bearing (matching de nombres TCGA barcode+UUID, centro del crop vs grid, nivel
> de pirámide, fusión promedio→[N,512], layout `features/pt_files`, containment). Ninguna
> observación bloquea el commit. Observaciones registradas abajo (§Bloqueadores).
>
> Gate (a) ✅ CERRADO. Restan para el `sbatch`: (b) co-firma de Sebastián, (c) dry-run stage-1,
> (d) OK de Ernesto — ver `progress/current.md`.

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
| Lectura eficiente (mejor nivel de pirámide) | ✅ | `get_best_level_for_downsample(size/224)` → lee del nivel correcto y reescala (TCGA fino: crop 482 px @ downsample 2.15 cae en **level0**, lee 482 px y reescala a 224 → 0.5 µm/px físico correcto; el contexto sí baja a un nivel downsampleado). *(Corrección O4: antes decía "level1 = 20× nativo"; el resultado físico es correcto, la nota del nivel era imprecisa.)* |
| Fusión promedio → [N,512] | ✅ | `v=0.5*(vf+vc)`; `torch.cat(...).float()` → float32 [N,512] |
| Bordes | ✅ | clamp de la location a [0, dim−size] (no black-fill) |
| Skip slides sin MPP (HistAI) | ✅ | `resolve_mpp` → None → `skipped` |
| `get_encoder('conch_v1')` → (model, img_transforms) | ✅ | verificado en `clam_environ/models/builder.py:46-82`; forward = `encode_image(normalize=False)` → 512-d |
| Layout `features/pt_files` para train_dsmil | ✅ | corregido: escribe `<out>/features/pt_files` |
| **BUG corregido** — openslide + DataLoader workers | ✅ **FIX** | handle openslide NO es fork-safe → `num_workers` bajado a **0** (era 4) |

## Bloqueadores / observaciones abiertas

1. ✅ **Pase formal del reviewer COMPLETADO** (10-jul) — APRUEBA CON OBSERVACIONES. Ver nota de gobernanza arriba.
2. ✅ **Gate (c) — dry-run CPU de stage-1 EJECUTADO (10-jul)**. Cazó un **BUG bloqueante**: `create_patches_fp`
   re-lee el `--process_list` con `pd.read_csv` sin `dtype` → los slide_id privados **numéricos puros** (105040)
   se infieren `int64` → `get_clean_slide_name` crashea (`'numpy.int64' object has no attribute 'replace'`,
   `environ_utils.py:182`) → **se habría caído toda la cohorte privada (76 slides)**; TCGA se salva (IDs con
   letras). **FIX** (clam_environ es read-only): stage-1 pasa a **symlink-farm plano** por cohorte SIN
   `--process_list` ni `--nested_folders` (nombres = strings desde `os.listdir`, sin coerción). **Verificado
   end-to-end**: TCGA `.svs`→`TCGA-…291.h5` (N=11324, attr patch_size=482), privado `.bif`→`105040.h5`
   (N=3411, attr patch_size=241); los `.h5` caen en `<save_dir>/patches/`, el attr `patch_size` sobre `coords`
   es el que lee el wrapper (L163), y el `.h5` stem = slide_id que usa `find_wsi`. Detalle: §Gate (c) abajo.
3. **Co-firma de Sebastián sobre las escalas** (112µm/512µm, fusión promedio) — gate exploratorio
   ([[gobernanza-gate-cofirma-sebastian]]), a llevar a la reunión del lunes.
4. **Re-entrenar brazo A** sobre features actuales (drift TCGA, ver Tier 0) — no reusar checkpoints viejos.
5. **O3 (stage-3 training slurm):** el grid común de 112 µm usa parches más grandes (TCGA 482 px / privado 241 px)
   → **menos parches por slide** → mayor riesgo del crash `topk`/`inst_eval` (B=8, bug run 4096). El `.slurm` de
   ENTRENAMIENTO debe llevar el **preflight minpatch** (workaround G) apuntando a los **nuevos** feature dirs
   (`$FEAT_B0`/`$FEAT_B`), no a los viejos.
6. **O1 (conteo, RESUELTO):** el piloto es **TCGA 207 + privado 76 = 283** (= slidelist + preflight); el pre-registro
   e investigación decían 77/284 — corregido. Una slide privada del set identificado (77) no entró al slidelist;
   confirmar cuál al consolidar los `.h5`.

---

## Gate (c) — dry-run CPU del stage-1 (10-jul-2026)

**Objetivo:** validar en ejecución (sin GPU, sin `sbatch`) el esquema del stage-1 antes del job real:
que `create_patches_fp` acepte el input del piloto, que los `.h5` caigan donde el wrapper los espera, y
que `--nested_folders` resuelva las WSI de ambas cohortes.

**Método:** 1 slide por cohorte del slidelist, existentes en disco (TCGA `TCGA-3C-AALI-01Z-00-DX1.F6E9…291.svs`,
privado `105040.bif`), `create_patches_fp.py` con `CUDA_VISIBLE_DEVICES=""` (CPU), salida a dir throwaway bajo
`clam_testing2/` (borrado tras la corrida). Se replicó primero el flujo **original del `.slurm`** (con
`--process_list --nested_folders`), y luego el **flujo corregido** (flat-farm sin process_list).

**Resultado — bug bloqueante encontrado y corregido:**

| Cohorte | Flujo original (process_list) | Flujo corregido (flat-farm) |
|---|---|---|
| TCGA (`.svs`, ID con letras) | ✅ `…291.h5`, N=11324 | ✅ `…291.h5`, N=11324, attr patch_size=482 |
| privado (`.bif`, ID numérico) | ❌ `AttributeError: 'numpy.int64' object has no attribute 'replace'` | ✅ `105040.h5`, N=3411, attr patch_size=241 |

- **Raíz:** `create_patches_fp.py:277` hace `pd.read_csv(process_list)` sin `dtype`; con slide_id numérico puro
  pandas infiere `int64`; `create_patches_fp.py:310` → `get_clean_slide_name(int64)` → `.replace` sobre int
  (`environ_utils.py:182`). Habría tumbado las **76** slides privadas (toda la cohorte del piloto salvo TCGA).
- **Fix (no toca clam_environ):** stage-1 del `.slurm` pasa a **symlink-farm plano** por cohorte (una symlink por
  WSI del piloto) y corre `create_patches_fp` SIN `--process_list` ni `--nested_folders`. En modo flat los nombres
  vienen de `os.listdir` = strings → sin coerción. Verificado que produce el `.h5` con el stem = slide_id y el attr
  `patch_size` correcto por cohorte (482/241), que es lo que consume el wrapper (`extract_multiscale_features.py:163`).
- **Caveat menor documentado:** el filtro de biomarcadores de flat-mode solo excluye `masson` (no la lista completa
  de nested-mode); ninguna slide del piloto es masson. Si alguna faltara, aparecería como `missing` en el log de
  stage-1 y como menos `.h5` en stage-2 (fail-safe visible, no silencioso).

**Estado del gate (c): ✅ CERRADO** (bug corregido y verificado). El `.slurm` de stage-1 quedó modificado; es un
fix mecánico de invocación (mismas slides, mismo grid, mismas features) — no cambia la semántica del experimento
validada por el reviewer en el gate (a).
