# Viabilidad del script de heatmaps — `create_heatmaps.py` de Sebastián

> Verificación **en seco** (sin `sbatch`, sin GPU), 20 may 2026. No se generó
> ningún heatmap todavía. Objetivo: confirmar qué inputs necesita antes de
> invertir un turno de GPU en la Fase 7.
>
> Nota: el directorio real del objetivo es `objetivo_4_heatmaps/` (el prompt lo
> llamaba `objetivo_4_heatmaps_atencion/`; se usa el que ya existe en el scaffold).

## Script y workflow

- **Script**: `clam_environ/create_heatmaps.py` (506 líneas) — el de Sebastián.
  Preferido sobre el oficial: produce/consume checkpoints con la misma API que
  entrenamos (`clam_mb`, `embed_dim 512`, `conch_v1`).
- **Invocación** (de `clam_environ/run_heatmaps.sh`):
  ```
  python create_heatmaps.py --config_file config_template.yaml \
         --task <task> --data_dir <path al WSI>
  ```
- **Config**: `clam_environ/heatmaps/configs/config_template.yaml`, sección
  `TASKS:` con un bloque por task (hay un bloque `microcalcificaciones`, privado).

## VEREDICTO: viable, pero **requiere GPU** y **requiere `sbatch`**

`create_heatmaps.py` **NO** consume los `.pt` ya extraídos. Para cada WSI:
1. Re-parcha el WSI desde cero (`patching_arguments`, `preset presets/bwh_biopsy.csv`).
2. Re-encodea los parches con **CONCH v1 on-the-fly** (`encoder_arguments:
   model_name conch_v1`, `batch_size 256`).
3. Corre el modelo CLAM entrenado y pinta el mapa de atención.

→ El paso 2 (encoder CONCH) corre en **GPU**. **No es posible "en seco sin
GPU".** La Fase 7 será un job SLURM (`sbatch`), secuencial tras baseline+B16.

## Inputs que necesita (todos verificados como disponibles)

| Input | Fuente | Estado |
|---|---|---|
| WSI original (`.bif`/`.tiff`/`.svs`) | ver abajo | ✅ disponible (muestra verificada) |
| Checkpoint entrenado `s_0_checkpoint.pt` | `results/baseline_microcalc_pth_B8/<exp>_s1/` y `.../ablation_microcalc_pth_B16/<exp>_s1/` | ⏳ tras jobs 4096 / 4097 |
| Preset de tessellation | `clam_environ/presets/bwh_biopsy.csv` | ✅ existe |
| CSV de labels | `clam_environ/environ/csv/dataset_microcalcificaciones_label.csv` | ✅ existe |
| Encoder CONCH v1 | checkpoint HF ya en `~/.cache/huggingface` (usado por `conch_fe`) | ✅ (asumido; mismo que feature extraction) |

### WSI originales — disponibilidad por tipo de slide (test set microcalcificaciones_pth)

Test set = 315 slides: **54 Environ + 175 HistAI + 86 TCGA**. Muestra verificada:

| Tipo | slide_id ejemplo | WSI encontrado | Formato |
|---|---|---|---|
| Environ | `114357` | `wsi/114357/114357.bif` (symlink a `scontreras/Imagines_IA/`) | `.bif` |
| HistAI | `histai_0976_slide_H&E_0` | `wsi_histai/case_0976/histai_0976_slide_H&E_0.tiff` | `.tiff` |
| TCGA | `TCGA-A7-A0D9-...DX2.66CD9ED8...` | `TCGA_dataset_curated/TCGA-A7-A0D9-01Z-00-DX2/<id>.svs` | `.svs` |

- Mapeo `slide_id → WSI`: Environ `<id>` → `wsi/<id>/<id>.bif` (ojo: la carpeta
  trae además `.bif` de IHQ — HER2/KI67/RE/RP — usar el H&E `<id>.bif`).
  HistAI `histai_NNNN_slide_H&E_K` → `wsi_histai/case_NNNN/<slide_id>.tiff`.
  TCGA `<full id>` → `.svs` bajo `TCGA_dataset_curated/` o `dataset_mama_tcga/`.
- `slide_ext: auto` en el config maneja la mezcla de extensiones.
- Los WSI Environ son **symlinks** a `scontreras/Imagines_IA/` (read-only de
  otro usuario) — el pipeline de Sebastián ya los usa, acceso de lectura OK.
- openslide 1.4.2 (en `clam_latest`) soporta `.svs`/`.tiff`; `.bif` (Ventana)
  también — confirmar al primer run.

## Ajustes necesarios para la Fase 7 (cuando lleguemos)

1. **Config propio** versionado en el repo (`slurm/heatmap_config_microcalc.yaml`),
   copia del template con:
   - Bloque para `microcalcificaciones_pth` (csv combinado `environ/csv/...`).
   - `ckpt_path` → nuestros checkpoints en `results/.../s_0_checkpoint.pt`.
   - **`raw_save_dir` / `production_save_dir` → dentro de `clam_testing2/`**
     (el template apunta a `clam_environ/environ/heatmap_*` → violaría
     containment). Override obligatorio.
   - `embed_dim: 512`, `model_type: clam_mb`, `model_name: conch_v1`.
2. Un `.slurm` de heatmaps (`slurm/heatmaps_microcalc.slurm`) con `--chdir` a
   `clam_environ` y outputs absolutos a `clam_testing2/`.
3. Selección de N=6-10 slides del **test set** cruzando `split_0_results.pkl`
   (predicciones) con `splits_0.csv` — 2 generaciones por slide (ckpt B=8 y B=16).
4. El script genera 1 WSI a la vez (`--data_dir <path>`) — loop sobre las slides
   elegidas, como hace `run_heatmaps.sh`.

## Bloqueos / pendientes

- **No bloquea nada ahora.** El script es viable; los inputs existen.
- Depende de: checkpoints de 4096 (B=8) y 4097 (B=16) → no se puede generar
  heatmaps hasta que ambos completen.
- Confirmar al primer run: (a) openslide lee `.bif` sin fricción, (b) el encoder
  CONCH v1 carga desde caché HF dentro del job.
