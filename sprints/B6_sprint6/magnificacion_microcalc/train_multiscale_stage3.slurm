#!/bin/bash
#SBATCH --job-name=eg_ms_train
#SBATCH --output=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/logs/%x_%j.out
#SBATCH --error=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/logs/%x_%j.err
#SBATCH --chdir=/media/administrador/Storage1/sdonoso/clam_environ
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=48:00:00
# (sin --partition → default 'debug'; cortesía single-GPU: `squeue` antes de lanzar)
#
# STAGE 3 — CLAM_MB PAIRED multi-escala (piloto microcalc, B6). 3 brazos × 3 binarias × 5 folds
# = 45 runs, reusando los MISMOS splits k=5 ([[patron-paired-comparison-reuso-splits]]).
# Pre-registro: sprints/B6_sprint6/magnificacion_microcalc/prereg_magnificacion.md (§3, brazos A/B0/B).
#
#   Brazo A  (baseline)   : features single-scale ACTUALES (clam_environ/environ) — re-entrenado
#                           sobre las features de hoy (drift TCGA, [[features-tcga-drift-reextraccion]]).
#   Brazo B0 (fine-only)  : tile fino @ grid común 112µm            → data/features_ms_fineonly (stage 2a).
#   Brazo B  (multiscale) : fino 112µm + contexto 512µm promediados → data/features_ms_multiscale (stage 2b).
#
# ─ PAIRING / HistAI ─ el universo de las 3 binarias = 328 slides (TCGA 207 + privado 76 + HistAI 45).
#   La re-extracción (stage 2) cubre solo TCGA+privado (283); HistAI (45) NO tiene MPP fiable → se
#   excluyó. Para que los 3 brazos entrenen sobre EL MISMO conjunto (pairing limpio), este script
#   BACKFILLEA en B0/B las .pt single-scale de las slides que la re-extracción no cubrió (las 45
#   HistAI + cualquier slide que stage 2 haya saltado), symlinkeadas desde clam_environ. Así HistAI
#   "conserva su single-scale en los 3 brazos" (prereg §3, impureza acotada ~15% documentada): su Δ
#   B−A es 0 por construcción; la señal viene de las 283 re-extraídas.
#
# ── NO LANZAR sin: (a) reviewer ✅ (gate a, review_regla9.md) · (b) co-firma Sebastián · (c) dry-run
#    stage-1 ✅ (gate c) · (d) OK explícito de Ernesto · y ADEMÁS: stage 2 (extract_multiscale.slurm)
#    COMPLETADO (produce features_ms_fineonly / features_ms_multiscale). El preflight aborta si faltan. ──

set -uo pipefail  # sin -e (workaround D: no abortar por SIGPIPE en diagnósticos)

REPO=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto
PY=/home/sdonoso/miniconda3/envs/clam_latest/bin/python   # workaround B: binario absoluto
CLAM_ENV=/media/administrador/Storage1/sdonoso/clam_environ
CSV_DIR=$CLAM_ENV/environ/csv                # dataset_microcalcificaciones_en_<bin>_label.csv (case_id,slide_id,label)
SPLITS=$REPO/data/splits_kfold               # microcalcificaciones_en_<bin>_pth_100/splits_<fold>.csv
RESULTS=$REPO/results/b6_magnif              # gitignored; 45 subdirs <brazo>_<bin>_f<fold>_s1/
ORIG_PT=$CLAM_ENV/environ/features/pt_files  # fuente single-scale para el backfill del pairing

FEAT_A=$CLAM_ENV/environ                      # brazo A  (features/pt_files single-scale, 328 slides)
FEAT_B0=$REPO/data/features_ms_fineonly       # brazo B0 (stage 2a)
FEAT_B=$REPO/data/features_ms_multiscale      # brazo B  (stage 2b)

BINARIAS="cdis carcinoma_invasivo tejido_no_neoplasico"
BRAZOS="A B0 B"
FOLDS="0 1 2 3 4"
MIN_PATCHES=8   # == --B (bug topk run 4096; workaround G)

source $(conda info --base)/etc/profile.d/conda.sh
conda activate clam_latest

# ---------------------------------------------------------------------------- #
# PREFLIGHT global (workaround G): aborta en segundos si falta un invariante.
# ---------------------------------------------------------------------------- #
echo "=== PREFLIGHT $(date) ==="
fail=0
[ -x "$PY" ] || { echo "FALTA env python $PY"; fail=1; }
[ -d "$ORIG_PT" ] || { echo "FALTA $ORIG_PT"; fail=1; }
[ -d "$FEAT_A/features/pt_files" ]  || { echo "FALTA brazo A $FEAT_A/features/pt_files"; fail=1; }
[ -d "$FEAT_B0/features/pt_files" ] || { echo "FALTA brazo B0 — correr stage 2a (extract_multiscale.slurm --mode fine_only) primero"; fail=1; }
[ -d "$FEAT_B/features/pt_files" ]  || { echo "FALTA brazo B — correr stage 2b (extract_multiscale.slurm --mode multiscale) primero"; fail=1; }
for BIN in $BINARIAS; do
  [ -f "$CSV_DIR/dataset_microcalcificaciones_en_${BIN}_label.csv" ] || { echo "FALTA label CSV en_${BIN}"; fail=1; }
  [ -f "$SPLITS/microcalcificaciones_en_${BIN}_pth_100/splits_4.csv" ] || { echo "FALTA splits en_${BIN} (esperaba 5 folds)"; fail=1; }
done
[ "$fail" -eq 0 ] || { echo "PREFLIGHT FALLÓ — abortando"; exit 1; }
echo "[preflight] OK"; nvidia-smi | head -15 || true

# ---------------------------------------------------------------------------- #
# BACKFILL del pairing: en B0 y B, symlink de las .pt single-scale (desde clam_environ)
# de toda slide del universo de las binarias que NO tenga feature multi-escala. Deja los 3
# brazos con la MISMA cobertura de slides (328) → Δ pareado limpio.
# ---------------------------------------------------------------------------- #
echo "=== BACKFILL HistAI/faltantes single-scale en B0/B $(date) ==="
for FEAT in "$FEAT_B0" "$FEAT_B"; do
  $PY - "$CSV_DIR" "$FEAT/features/pt_files" "$ORIG_PT" "$BINARIAS" <<'PYEOF' || { echo "BACKFILL FALLÓ"; exit 1; }
import sys, os, pandas as pd
csv_dir, dst, orig, binarias = sys.argv[1:5]
U = set()
for b in binarias.split():
    d = pd.read_csv(os.path.join(csv_dir, f"dataset_microcalcificaciones_en_{b}_label.csv"))
    U |= set(d["slide_id"].astype(str))
n_link = 0; n_orphan = 0
for sid in sorted(U):
    if os.path.exists(os.path.join(dst, sid + ".pt")):
        continue                       # ya tiene feature multi-escala
    src = os.path.join(orig, sid + ".pt")
    if not os.path.exists(src):
        n_orphan += 1; continue         # ni multi-escala ni single-scale → el dataloader la salta
    os.symlink(src, os.path.join(dst, sid + ".pt")); n_link += 1
print(f"[backfill] {dst}: +{n_link} symlinks single-scale; {n_orphan} sin ninguna feature; universo={len(U)}")
PYEOF
done

# ---------------------------------------------------------------------------- #
# BUCLE de entrenamiento paired: brazo × binaria × fold (45 runs).
# Cada fold → results/b6_magnif/<brazo>_<bin>_f<fold>_s1/ (summary.csv + split_<fold>_results.pkl
# + test_metrics.json con balanced_acc + confusión 2×2 + n/clase). model_type clam = CLAM_MB
# baseline (≡ job 4109); único delta entre brazos = el contenido de las features.
# ---------------------------------------------------------------------------- #
for BIN in $BINARIAS; do
  TASK=microcalcificaciones_en_${BIN}_pth
  CSV=$CSV_DIR/dataset_microcalcificaciones_en_${BIN}_label.csv
  SPLIT=$SPLITS/microcalcificaciones_en_${BIN}_pth_100
  for BRAZO in $BRAZOS; do
    case $BRAZO in
      A)  DR=$FEAT_A  ;;
      B0) DR=$FEAT_B0 ;;
      B)  DR=$FEAT_B  ;;
    esac
    for FOLD in $FOLDS; do
      echo "=== PREFLIGHT minpatch brazo=$BRAZO bin=$BIN fold=$FOLD ==="
      $PY $REPO/scripts/preflight_minpatch.py \
          --split_dir "$SPLIT" --features_dir "$DR/features/pt_files" \
          --min_patches $MIN_PATCHES --fold $FOLD \
        || { echo "PREFLIGHT minpatch FALLÓ ($BRAZO/$BIN/f$FOLD)"; exit 1; }

      echo "=== TRAIN brazo=$BRAZO bin=$BIN fold=$FOLD $(date) ==="
      CUDA_VISIBLE_DEVICES=0 $PY $REPO/scripts/train_dsmil.py \
          --model_type clam --task $TASK --n_classes 2 \
          --csv_path "$CSV" --label_dict '{"no": 0, "si": 1}' \
          --split_dir "$SPLIT" --fold $FOLD \
          --data_root_dir "$DR" --results_dir "$RESULTS" \
          --exp_code ${BRAZO}_${BIN}_f${FOLD} \
          --embed_dim 512 --drop_out 0.25 --lr 2e-4 --bag_loss ce \
          --B 8 --bag_weight 0.7 --max_epochs 200 \
          --early_stopping --patience 20 --stop_epoch 50 --seed 1 \
        || { echo "TRAIN FALLÓ ($BRAZO/$BIN/f$FOLD)"; exit 1; }
    done
  done
done

echo "=== STAGE 3 COMPLETO $(date) — 45 runs en $RESULTS ==="
echo "Post-proceso: Δ pareado por fold B−A y B−B0 (balanced_acc Y AUC) por binaria; matriz de confusión + n/clase."
