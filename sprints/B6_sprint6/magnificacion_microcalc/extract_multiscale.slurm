#!/bin/bash
#SBATCH --job-name=eg_msextract
#SBATCH --output=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/logs/%x_%j.out
#SBATCH --error=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/logs/%x_%j.err
#SBATCH --chdir=/media/administrador/Storage1/sdonoso/clam_environ
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=48:00:00
# (sin --partition → default 'debug'; cortesía single-GPU: `squeue` antes de lanzar)
#
# Re-extracción CONCH MULTI-ESCALA (piloto microcalc, B6) — pirámide 112µm + 512µm,
# fusión promedio, parametrizada en µm/px por cohorte. Pre-registro:
#   sprints/B6_sprint6/magnificacion_microcalc/prereg_magnificacion.md
# NO LANZAR sin: (1) OK explícito de Ernesto, (2) co-firma de Sebastián sobre las escalas,
# (3) pase formal del reviewer (esta sesión hizo self-review inline; ver review_regla9.md).

set -uo pipefail  # NB: sin -e para no abortar por SIGPIPE en diagnósticos (workaround D)

REPO=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto
PY=/home/sdonoso/miniconda3/envs/clam_latest/bin/python   # workaround B: binario absoluto
SLIDELIST=$REPO/sprints/B6_sprint6/magnificacion_microcalc/microcalc_slidelist_tcga_privado.csv
COORDS=$REPO/data/coords_112um            # salida stage 1 (grid común por cohorte)
FEAT_B0=$REPO/data/features_ms_fineonly    # arm B0 (fine-only @ grid común)
FEAT_B=$REPO/data/features_ms_multiscale   # arm B  (fino + contexto promediados)
WSI_TCGA=/media/administrador/Storage1/sdonoso/TCGA_dataset_curated
WSI_PRIV=/media/administrador/Storage1/sdonoso/wsi
export CONCH_CKPT_PATH=/home/sdonoso/.cache/huggingface/hub/models--MahmoodLab--conch/snapshots/f9ca9f877171a28ade80228fb195ac5d79003357/pytorch_model.bin

source $(conda info --base)/etc/profile.d/conda.sh
conda activate clam_latest

# ---------------------------------------------------------------------------- #
# PREFLIGHT (workaround G): aborta en segundos si falta un invariante.
# ---------------------------------------------------------------------------- #
echo "=== PREFLIGHT $(date) ==="
fail=0
[ -x "$PY" ]            || { echo "FALTA env python $PY"; fail=1; }
[ -f "$SLIDELIST" ]     || { echo "FALTA slidelist $SLIDELIST"; fail=1; }
[ -f "$CONCH_CKPT_PATH" ] || { echo "FALTA CONCH ckpt $CONCH_CKPT_PATH"; fail=1; }
[ -d "$WSI_TCGA" ]      || { echo "FALTA WSI TCGA $WSI_TCGA"; fail=1; }
[ -d "$WSI_PRIV" ]      || { echo "FALTA WSI privado $WSI_PRIV"; fail=1; }
$PY - "$SLIDELIST" <<'PYEOF' || fail=1
import sys, pandas as pd
df = pd.read_csv(sys.argv[1])
assert {"slide_id","cohort","mpp","fine_px","ctx_px"} <= set(df.columns), "schema slidelist"
assert (df.mpp.between(0.1,1.0)).all(), "mpp fuera de banda"
assert len(df) == 283, f"esperaba 283 slides, hay {len(df)}"
print(f"[preflight] slidelist OK: {len(df)} slides, cohortes={df.cohort.value_counts().to_dict()}")
PYEOF
[ "$fail" -eq 0 ] || { echo "PREFLIGHT FALLÓ — abortando"; exit 1; }
echo "[preflight] OK"; nvidia-smi | head -15 || true

# ---------------------------------------------------------------------------- #
# STAGE 1 — patching por-cohorte en grid COMÚN 112µm (create_patches_fp de clam_environ,
# SIN modificar, solo args). patch_size = round(112/mpp): TCGA 482, privado 241.
#
# FIX (gate c, dry-run CPU 10-jul): create_patches_fp re-lee el --process_list con
# `pd.read_csv` SIN dtype → los slide_id privados NUMÉRICOS puros (p.ej. 105040) se infieren
# como int64 → `get_clean_slide_name` crashea ("'numpy.int64' object has no attribute
# 'replace'", environ_utils.py:182) → se caería TODA la cohorte privada (76 slides). Como
# clam_environ es read-only, se restringe el set del piloto vía SYMLINK-FARM PLANO (nombres
# = strings desde os.listdir → sin coerción int64) y se corre SIN --process_list ni
# --nested_folders. Verificado end-to-end en TCGA (.svs) y privado (.bif) el 10-jul.
# ---------------------------------------------------------------------------- #
for COH in tcga privado; do
  if [ "$COH" = "tcga" ]; then SRC=$WSI_TCGA; PS=482; else SRC=$WSI_PRIV; PS=241; fi
  FARM=$COORDS/_farm/$COH
  mkdir -p "$FARM" "$COORDS/$COH"
  # symlink-farm plano: una symlink por WSI del piloto de esta cohorte (read-only WSI → link).
  $PY - "$SLIDELIST" "$COH" "$SRC" "$FARM" <<'PYEOF'
import sys, csv
from pathlib import Path
slidelist, coh, src, farm = sys.argv[1:5]
exts = [".svs", ".bif", ".tiff", ".tif"]
rows = [r for r in csv.DictReader(open(slidelist)) if r["cohort"] == coh]
n = 0; missing = []
for r in rows:
    sid = r["slide_id"]; found = None
    for ext in exts:
        h = list(Path(src).rglob(f"{sid}{ext}"))
        if h:
            found = h[0]; break
    if found is None:
        missing.append(sid); continue
    link = Path(farm) / found.name
    if not link.exists():
        link.symlink_to(found)
    n += 1
print(f"[stage1] {coh}: {n} symlinks en {farm}; missing={len(missing)}")
if missing:
    print("  MISSING (revisar):", missing[:20])
PYEOF
  echo "=== STAGE 1 patching cohorte=$COH patch_size=$PS (flat-farm, sin process_list) ==="
  $PY create_patches_fp.py \
      --source "$FARM" --save_dir "$COORDS/$COH" \
      --patch_size "$PS" --step_size "$PS" --patch_level 0 \
      --seg --patch --stitch || { echo "STAGE 1 $COH FALLÓ"; exit 1; }
done
# consolidar los .h5 de coords de ambas cohortes en un solo dir para stage 2
mkdir -p "$COORDS/all_h5"
find "$COORDS"/{tcga,privado}/patches -name "*.h5" -exec ln -sf {} "$COORDS/all_h5/" \; 2>/dev/null || true

# ---------------------------------------------------------------------------- #
# STAGE 2 — extracción CONCH multi-escala (wrapper propio; regla 2 no toca clam_environ).
# Dos brazos: B0 (fine_only) y B (multiscale). El wrapper lee el mpp real por slide y
# salta HistAI (sin MPP) automáticamente.
# ---------------------------------------------------------------------------- #
echo "=== STAGE 2a — arm B0 (fine_only) $(date) ==="
CUDA_VISIBLE_DEVICES=0 $PY $REPO/scripts/extract_multiscale_features.py \
    --h5_dir "$COORDS/all_h5" --wsi_dirs "$WSI_TCGA" "$WSI_PRIV" \
    --out_dir "$FEAT_B0" --mode fine_only --batch_size 64 || { echo "STAGE 2a FALLÓ"; exit 1; }

echo "=== STAGE 2b — arm B (multiscale) $(date) ==="
CUDA_VISIBLE_DEVICES=0 $PY $REPO/scripts/extract_multiscale_features.py \
    --h5_dir "$COORDS/all_h5" --wsi_dirs "$WSI_TCGA" "$WSI_PRIV" \
    --out_dir "$FEAT_B" --mode multiscale --batch_size 64 || { echo "STAGE 2b FALLÓ"; exit 1; }

echo "=== EXTRACCIÓN MULTI-ESCALA COMPLETA $(date) ==="

# ---------------------------------------------------------------------------- #
# STAGE 3 — CLAM paired (documentado; se lanza en un .slurm aparte por brazo × binaria × fold,
# reusando splits data/splits_kfold/microcalcificaciones_en_<X>_pth_100, preflight minpatch).
# Brazos: A (features actuales, re-entrenado), B0 ($FEAT_B0), B ($FEAT_B). Ejemplo (1 celda):
#   $PY $REPO/scripts/train_dsmil.py --model_type clam \
#       --task microcalcificaciones_en_cdis_pth --n_classes 2 \
#       --csv_path .../dataset_microcalcificaciones_en_cdis_label.csv \
#       --label_dict '{"no":0,"si":1}' \
#       --split_dir $REPO/data/splits_kfold/microcalcificaciones_en_cdis_pth_100 --fold 0 \
#       --data_root_dir $FEAT_B  --results_dir $REPO/results/b6_magnif/B_cdis \
#       --embed_dim 512 --drop_out 0.25 --lr 2e-4 --B 8 --bag_weight 0.7 --max_epochs 200 --seed 1
# El wrapper ya escribe $FEAT_B/features/pt_files → --data_root_dir $FEAT_B lo consume directo.
