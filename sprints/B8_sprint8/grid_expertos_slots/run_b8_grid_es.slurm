#!/bin/bash
#SBATCH --job-name=eg_b8_grid_es
#SBATCH --partition=debug
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=16
#SBATCH --mem=32G
#SBATCH --time=48:00:00
#SBATCH --output=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/logs/%x_%j.out
#SBATCH --error=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/logs/%x_%j.err
#SBATCH --chdir=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto
# ============================================================
# B8 objetivo 3 — Grid de expertos (E) y slots (S) de Mammoth sobre
# carcinoma_ductal_insitu_presente_ci_reform. 8 brazos × 5 folds = 40 runs.
#
# PRE-REGISTRO (leer antes de tocar nada):
#   sprints/B8_sprint8/grid_expertos_slots/prereg.md
#
# PROPÓSITO (para el reviewer): pregunta de CAPACIDAD, no de rendimiento. Cuántos E y
# cuántos S hace falta que tenga Mammoth para mama y nuestras features, dado que 30×10
# está afinado por los autores para tipo histológico y otros cánceres. El contraste
# primario es Mammoth contra Mammoth (cada brazo vs el control 30×10), NO contra CLAM:
# el eje de rendimiento está CERRADO (CLAUDE.md Hallazgo 12) y este job no lo reabre.
#
# HIPÓTESIS pre-registrada (prereg §3): a igual capacidad total E·S, recortar S se
# tolera mejor que recortar E. Sale del encargo 1 de este sprint, que midió sobre 1858
# láminas-fold expertos 29.98/30 (reparto uniforme) y slots 159.5/300 => el margen de
# recorte está en S, no en E. Métrica: balanced_acc Y AUC juntos, Δ pareado por fold
# contra el control, con consistencia de signo; sin gate numérico rígido (regla 9.a).
#
# COMPARACIÓN PAIRED: mismo --split_dir que el job 4589
# (data/splits_kfold/carcinoma_ductal_insitu_presente_ci_reform_100), splits NO
# regenerados ([[patron-paired-comparison-reuso-splits]]). Los baselines CLAM del 4589
# se reusan (features sin cambios desde el 17-jul, verificado 2-ago); el Mammoth 30×10
# se RE-CORRE acá como control de reproducibilidad del reuso.
#
# ÚNICO DELTA entre brazos = --mammoth_num_experts y --mammoth_num_slots. Todo lo demás
# (heads 16, slot_dim 256, slot_dropout 0.0, keep_slots False, régimen de training,
# seed 1) es idéntico al 4589.
#
# ORDEN de ejecución elegido para que un corte temprano deje algo interpretable:
# control -> pares de igual total, de menos a más agresivo (270, 210, 150) -> piso 90.
#
# GATES antes del sbatch: pre-registro escrito + reviewer (regla 9) + commit en main +
# GPU libre (cortesía single-GPU). Preflight obligatorio (workaround G): test CPU del
# modelo, chequeo CPU de las 8 configs y preflight de parches por fold.
#
# PRESUPUESTO: 36.2 min/run (mediana medida del 4589 en esta tarea) × 40 ≈ 24 h.
# ============================================================

set -euo pipefail

REPO=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto
CLAM=/media/administrador/Storage1/sdonoso/clam_environ
ENVIRON="$CLAM/environ"
FEATURES_DIR="$ENVIRON/features/pt_files"

TASK=carcinoma_ductal_insitu_presente_ci_reform
CSV="$REPO/data/csv_new_tasks/dataset_${TASK}_label.csv"
SPLIT_DIR="$REPO/data/splits_kfold/${TASK}_100"
LABELDICT='{"no": 0, "si": 1}'
NCLS=2
RESULTS_DIR="$REPO/results/b8_grid_es/${TASK}"

B=8
K=5
RUN_TS=$(date +%Y%m%d_%H%M)

# Brazos del grid: "E S". Ver prereg §4. C=control, A=recorta E, B=recorta S.
#   30 10 -> control (= 4589)      27 10 / 30  9 -> par E·S=270
#   21 10 / 30  7 -> par E·S=210   15 10 / 30  5 -> par E·S=150
#   30  3 -> piso (solo rama S)
ARMS="${ARMS:-30:10 27:10 30:9 21:10 30:7 15:10 30:5 30:3}"

source /home/sdonoso/miniconda3/etc/profile.d/conda.sh
conda activate clam_latest
PYBIN="$CONDA_PREFIX/bin/python"                  # workaround B: 'python' a secas ROTO

mkdir -p "$REPO/logs" "$RESULTS_DIR"

echo "Job ${SLURM_JOB_ID:-local} started at $(date) on $(hostname)"
echo "TASK=$TASK  K=$K  brazos=$ARMS"
# Provenance: el árbol es compartido y el job relee su código en cada invocación
# (workaround H). Dejar el HEAD en el log cierra de qué commit salió lo que corrió.
echo "commit=$(git -C "$REPO" rev-parse HEAD 2>/dev/null || echo desconocido)  rama=$(git -C "$REPO" branch --show-current 2>/dev/null || echo desconocida)"
"$PYBIN" -c "import torch; assert torch.cuda.is_available(), 'no CUDA'; print('torch', torch.__version__)"
"$PYBIN" -c "import mammoth; print('mammoth OK:', mammoth.__file__)"
nvidia-smi | head -20 || true                     # workaround D

if [ ! -d "$SPLIT_DIR" ]; then
  echo "SPLITS AUSENTES: $SPLIT_DIR no existe. ABORTA."; exit 1
fi
if [ ! -f "$CSV" ]; then
  echo "CSV AUSENTE: $CSV no existe. ABORTA."; exit 1
fi

# --- Preflight 1: gate CPU del modelo (segundos). ---
if ! CUDA_VISIBLE_DEVICES="" "$PYBIN" "$REPO/tests/test_mammoth_cpu.py" ; then
  echo "TEST CPU MAMMOTH FAILED — abortar"; exit 1
fi

# --- Preflight 2: las 8 configuraciones del grid construyen y hacen forward (CPU). ---
# Una config rota se paga en horas de GPU si aparece a mitad del grid.
if ! CUDA_VISIBLE_DEVICES="" "$PYBIN" "$REPO/scripts/grid_es_config_check.py" ; then
  echo "CONFIG CHECK DEL GRID FAILED — abortar"; exit 1
fi

# --- Preflight 3: invariante del split por fold (workaround G). ---
# Los 5 folds son los mismos para los 8 brazos, así que se valida una sola vez.
for ((f=0; f<K; f++)); do
  if ! "$PYBIN" "$REPO/scripts/preflight_minpatch.py" \
      --split_dir "$SPLIT_DIR" --features_dir "$FEATURES_DIR" \
      --min_patches "$B" --fold "$f" ; then
    echo "PREFLIGHT FAILED en $TASK fold $f"; exit 1
  fi
done

echo ""
echo "===== GRID E×S | $TASK | $(echo "$ARMS" | wc -w) brazos × $K folds ====="
echo "       split_dir=$SPLIT_DIR"
echo "       csv=$CSV"
echo "       results=$RESULTS_DIR"

for ARM in $ARMS; do
  E="${ARM%%:*}"
  S="${ARM##*:}"
  echo ""
  echo "----- brazo E=$E S=$S (E·S=$((E * S))) -----"
  for ((f=0; f<K; f++)); do
    echo "  $TASK | e${E}s${S} | fold $f / $((K-1))"
    CUDA_VISIBLE_DEVICES=0 "$PYBIN" "$REPO/scripts/train_dsmil.py" \
      --model_type    clam_mammoth \
      --task          "$TASK" \
      --exp_code      "mammoth_e${E}s${S}_f${f}_${RUN_TS}" \
      --csv_path      "$CSV" \
      --data_root_dir "$ENVIRON" \
      --split_dir     "$SPLIT_DIR" \
      --results_dir   "$RESULTS_DIR" \
      --fold          "$f" \
      --n_classes     "$NCLS" \
      --max_epochs    200 \
      --early_stopping --patience 20 --stop_epoch 50 \
      --B "$B" --bag_weight 0.7 --lr 2e-4 --reg 1e-5 --drop_out 0.25 \
      --embed_dim 512 --seed 1 \
      --mammoth_num_experts "$E" \
      --mammoth_num_slots   "$S" \
      --mammoth_num_heads   16 \
      --mammoth_slot_dim    256 \
      --label_dict "$LABELDICT"
  done
  echo "----- brazo E=$E S=$S done -----"
done

echo ""
echo "Job ${SLURM_JOB_ID:-local} done at $(date)"
echo "Artefactos en $RESULTS_DIR/mammoth_e<E>s<S>_f<0..$((K-1))>_${RUN_TS}_s1/"
echo "Baselines a reusar (job 4589, mismos splits):"
echo "  $REPO/results/b7_mammoth_interp/${TASK}/"
echo "Siguiente paso: sprints/B8_sprint8/grid_expertos_slots/resultados.md con"
echo "balanced_acc Y AUC por brazo y fold, Δ pareado vs el control 30×10."
