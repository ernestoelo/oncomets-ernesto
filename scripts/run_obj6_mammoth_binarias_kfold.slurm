#!/bin/bash
#SBATCH --job-name=eg_mammoth_bin_kfold
#SBATCH --partition=debug
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=16
#SBATCH --mem=32G
#SBATCH --time=24:00:00
#SBATCH --output=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/logs/%x_%j.out
#SBATCH --error=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/logs/%x_%j.err
#SBATCH --chdir=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto

# ============================================================
#  OBJETIVO 6 — mammoth (CLAM_MB + MoE en la 1ª capa) × 3 binarias × MC-CV k=5.
#  Trabajo heredado de Eduardo (renunció 1-jun). Prioridad de Benjamín.
# ============================================================
# Compara CLAM baseline vs CLAM+mammoth sobre las 3 binarias de
# microcalcificaciones, REUTILIZANDO EXACTAMENTE los mismos splits de la Fase 0
# (job 4170, CLAM) y del anexo DSMIL (4179). Comparación PAIRED por fold
# (Δ = mammoth_i − clam_i bien definido), [[patron-paired-comparison-reuso-splits]].
#
# DISEÑO (ver sprints/B4_sprint4/objetivo_6_mammoth/README.md — argumento regla 9):
#   - Ambos brazos corren por el MISMO harness (scripts/train_dsmil.py), único
#     delta = --model_type. clam_mammoth = CLAM_MB con la 1ª capa lineal
#     reemplazada por Mammoth (keep_slots=False → N parches preservados, decisión
#     Obj 6 #1). Mismo instance_loss (SmoothTop1SVM), misma loss bag+inst, mismos
#     args bendecidos, misma seed 1 → la comparación NO tiene confound de harness.
#   - El brazo 'clam' re-establece el baseline por el harness idéntico (los
#     números de Fase 0 / job 4170, vía main.py, quedan como referencia sanity).
#
# Hiperparámetros mammoth = recomendados del paper (e30 s10 h16 d256, auto_rank,
# share_lora). PCGrad (gradient surgery) NO entra acá — eje separado (Obj 6 #3).
#
# MÉTRICA DECISIVA: Δ pareado por fold en balanced_acc Y AUC, media±std (k=5),
# + matriz de confusión y n por clase. Política B5 (2-jun, memoria
# eval-reporte-auc-y-umbrales-obj6): SIN gate numérico — los umbrales rígidos
# Δ≥+0.03 / Δ≤−0.05 / ≥4/5 se RETIRARON como GO/NO-GO. Interpretación cualitativa
# (consistencia de signo, varianza, vs trivial 0.5); dirección esperada Δ>0.
#
# Economía de GPU: por defecto corre AMBOS brazos (~15h, comparación rigurosa).
# Si la GPU única está apretada, setear MODEL_TYPES="clam_mammoth" y comparar
# contra el baseline Fase 0 (4170) ya computado.
#
# Lanzamiento (SOLO con OK explícito de Ernesto — NO autónomo):
#     cd /media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto
#     squeue ; sinfo                  # cortesía: GPU única compartida
#     sbatch scripts/run_obj6_mammoth_binarias_kfold.slurm
# Monitor:  tail -f logs/eg_mammoth_bin_kfold_*.out
# Cancel:   scancel <jobid>
# ============================================================

set -euo pipefail

REPO=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto
CLAM=/media/administrador/Storage1/sdonoso/clam_environ
ENVIRON="$CLAM/environ"
FEATURES_DIR="$ENVIRON/features/pt_files"
SPLITS_BASE="$REPO/data/splits_kfold"     # mismos splits que Fase 0 (job 4170)
CSV_BASE="$ENVIRON/csv"                    # CSVs binarios read-only de Sebastián
B=8
K=5
RUN_TS=$(date +%Y%m%d_%H%M)   # timestamp en exp_code: un re-run NO pisa el previo (workaround C)
MODEL_TYPES="${MODEL_TYPES:-clam clam_mammoth}"   # brazos (override: MODEL_TYPES="clam_mammoth")

source /home/sdonoso/miniconda3/etc/profile.d/conda.sh
conda activate clam_latest
PYBIN="$CONDA_PREFIX/bin/python"   # 'python' a secas está ROTO (ADFRsuite py2.7, workaround B)

echo "Job ${SLURM_JOB_ID:-local} started at $(date) on $(hostname)"
"$PYBIN" -c "import torch; assert torch.cuda.is_available(), 'no CUDA'; print('torch', torch.__version__, 'cuda', torch.version.cuda)"
"$PYBIN" -c "import mammoth; print('mammoth OK:', mammoth.__file__)"
nvidia-smi | head -20 || true   # '|| true': head cierra el pipe -> SIGPIPE (workaround D)

# Verificador determinístico de splits (smoke #1, defensa en profundidad).
if ! "$PYBIN" "$REPO/scripts/verify_kfold_splits.py" ; then
  echo "VERIFY KFOLD FAILED — splits inconsistentes, abortar"
  exit 1
fi

# Smoke #2: tests CPU del modelo Mammoth (preflight de código, segundos).
if ! CUDA_VISIBLE_DEVICES="" "$PYBIN" "$REPO/tests/test_mammoth_cpu.py" ; then
  echo "TEST CPU MAMMOTH FAILED — port roto, abortar antes de gastar GPU"
  exit 1
fi

for TEJIDO in carcinoma_invasivo cdis tejido_no_neoplasico; do
  TASK="microcalcificaciones_en_${TEJIDO}_pth"
  SPLIT_DIR="$SPLITS_BASE/${TASK}_100"
  CSV_PATH="$CSV_BASE/dataset_microcalcificaciones_en_${TEJIDO}_label.csv"
  RESULTS_DIR="$REPO/results/obj6_mammoth_binarias_${TEJIDO}"

  echo ""
  echo "===== TASK: $TASK  (brazos: $MODEL_TYPES, k=$K folds) ====="

  # Preflight obligatorio (workaround G) en CADA fold: ninguna slide de train
  # con n_patches < B, o torch.topk revienta inst_eval (bug 4096).
  for ((f=0; f<K; f++)); do
    if ! "$PYBIN" "$REPO/scripts/preflight_minpatch.py" \
        --split_dir    "$SPLIT_DIR" \
        --features_dir "$FEATURES_DIR" \
        --min_patches  "$B" \
        --fold         "$f" ; then
      echo "PREFLIGHT FAILED en $TASK fold $f"
      exit 1
    fi
  done

  for MT in $MODEL_TYPES; do
    echo ""
    echo "----- modelo: $MT -----"
    for ((f=0; f<K; f++)); do
      echo "  fold $f / $((K-1))  [$MT]"

      CUDA_VISIBLE_DEVICES=0 "$PYBIN" "$REPO/scripts/train_dsmil.py" \
        --model_type    "$MT" \
        --task          "$TASK" \
        --exp_code      "${MT}_${TEJIDO}_f${f}_${RUN_TS}" \
        --csv_path      "$CSV_PATH" \
        --data_root_dir "$ENVIRON" \
        --split_dir     "$SPLIT_DIR" \
        --results_dir   "$RESULTS_DIR" \
        --fold          "$f" \
        --max_epochs    30 \
        --early_stopping \
        --patience      20 \
        --stop_epoch    50 \
        --B             "$B" \
        --bag_weight    0.7 \
        --lr            2e-4 \
        --reg           1e-5 \
        --drop_out      0.25 \
        --embed_dim     512 \
        --seed          1 \
        --label_dict    '{"no": 0, "si": 1}'
    done
  done

  echo "===== $TASK done ====="
done

echo ""
echo "Job ${SLURM_JOB_ID:-local} done at $(date)"
echo "Results under $REPO/results/obj6_mammoth_binarias_<tejido>/<modelo>_<tejido>_f<0..$((K-1))>_s1/"
echo "  (test_metrics.json con balanced_acc + split_<f>_results.pkl por fold/brazo)"
