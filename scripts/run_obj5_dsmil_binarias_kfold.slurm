#!/bin/bash
#SBATCH --job-name=eg_dsmil_bin_kfold
#SBATCH --partition=debug
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=16
#SBATCH --mem=32G
#SBATCH --time=12:00:00
#SBATCH --output=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/logs/%x_%j.out
#SBATCH --error=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/logs/%x_%j.err
#SBATCH --chdir=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto

# ============================================================
#  OBJETIVO 5 — ANEXO: DSMIL × 3 binarias × MC-CV k=5.
#  Cierre simétrico del cuadro arquitectónico CLAM vs DSMIL en binarias.
# ============================================================
# Aplica MC-CV a DSMIL sobre las 3 binarias de microcalcificaciones,
# REUTILIZANDO EXACTAMENTE los mismos splits de la Fase 0 (job 4170, CLAM).
# Esto deja la comparación CLAM-Fase0 vs DSMIL-este-job PAREADA por fold
# (Δ bien definido por construcción) — el valor del experimento depende
# crítico de no regenerar splits.
#
# DIFERENCIA vs Fase 0 (job 4170, las únicas, todas justificadas):
#   - Modelo: DSMIL (vía train_dsmil.py --model_type dsmil, harness intacto
#     desde jobs 4135/4137 y Fase 2).
#   - Harness: scripts/train_dsmil.py (DSMIL no está en main.py de Sebastián).
#   - --w_max 0.1 (único hiperparámetro DSMIL, R1=B.1.3, fijo idéntico a Fase 2).
# TODO LO DEMÁS es bit-a-bit idéntico a Fase 0: mismos splits, mismas
# features (CONCH 512), mismo B=8, mismo bag_weight 0.7, misma seed 1,
# mismos label_dict, mismos CSVs read-only de Sebastián.
#
# Argumento + métrica: sprints/B4_sprint4/objetivo_5_fusion_binaria/hipotesis_dsmil_binarias.md
# (regla 9). Reviewer OK pendiente al momento de redactar este header — si
# leés este archivo en main, fue aprobado.
#
# NO es pass/fail de proyecto — caracteriza si el "fracaso arquitectónico"
# del 4137 (1 sorteo) se sostiene con barras de error, o era ruido del
# sorteo (como pasó con CLAM en Fase 0, Hallazgo 1).
#
# Lanzamiento (solo con OK explícito de Ernesto, NO autónomo):
#     cd /media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto
#     squeue ; sinfo                # cortesía: GPU única compartida
#     sbatch scripts/run_obj5_dsmil_binarias_kfold.slurm
# Monitor:  tail -f logs/eg_dsmil_bin_kfold_*.out
# Cancel:   scancel <jobid>
# Tiempo estimado: ~7-8h (3 tareas × 5 folds × ~30 min DSMIL). --time 12h.
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
RUN_TS=$(date +%Y%m%d_%H%M)   # timestamp en exp_code: un re-run NO pisa el run previo (workaround C: nada se borra; observación reviewer)

source /home/sdonoso/miniconda3/etc/profile.d/conda.sh
conda activate clam_latest
PYBIN="$CONDA_PREFIX/bin/python"   # 'python' a secas está ROTO (ADFRsuite py2.7, workaround B)

echo "Job $SLURM_JOB_ID started at $(date) on $(hostname)"
"$PYBIN" -c "import torch; assert torch.cuda.is_available(), 'no CUDA'; print('torch', torch.__version__, 'cuda', torch.version.cuda)"
nvidia-smi | head -20 || true   # '|| true': head cierra el pipe -> SIGPIPE (workaround D)

# Verificador determinístico de splits (smoke #1, defensa en profundidad).
# Idiom 'if !' exento de set -e.
if ! "$PYBIN" "$REPO/scripts/verify_kfold_splits.py" ; then
  echo "VERIFY KFOLD FAILED — splits inconsistentes, abortar"
  exit 1
fi

for TEJIDO in carcinoma_invasivo cdis tejido_no_neoplasico; do
  TASK="microcalcificaciones_en_${TEJIDO}_pth"
  SPLIT_DIR="$SPLITS_BASE/${TASK}_100"
  CSV_PATH="$CSV_BASE/dataset_microcalcificaciones_en_${TEJIDO}_label.csv"
  RESULTS_DIR="$REPO/results/obj5_anexo_dsmil_binarias_${TEJIDO}"

  echo ""
  echo "===== TASK: $TASK  (DSMIL, k=$K folds) ====="

  # Preflight obligatorio (workaround G) en CADA fold: ninguna slide de
  # train con n_patches < B, o torch.topk revienta inst_eval (bug 4096).
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

  # Entrenamiento DSMIL, k=5 folds. Args idénticos a Fase 2 (fusionado);
  # único cambio vs Fase 2 = --task / --csv_path / --split_dir / --results_dir.
  for ((f=0; f<K; f++)); do
    echo ""
    echo "----- fold $f / $((K-1)) -----"

    CUDA_VISIBLE_DEVICES=0 "$PYBIN" "$REPO/scripts/train_dsmil.py" \
      --model_type    dsmil \
      --task          "$TASK" \
      --exp_code      "dsmil_${TEJIDO}_f${f}_${RUN_TS}" \
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
      --w_max         0.1 \
      --lr            2e-4 \
      --reg           1e-5 \
      --drop_out      0.25 \
      --embed_dim     512 \
      --seed          1 \
      --label_dict    '{"no": 0, "si": 1}'

    echo "----- fold $f done -----"
  done

  echo "===== $TASK done ====="
done

echo ""
echo "Job $SLURM_JOB_ID done at $(date)"
echo "Results under $REPO/results/obj5_anexo_dsmil_binarias_<tejido>/dsmil_<tejido>_f<0..$((K-1))>_s1/"
echo "  (test_metrics.json con balanced_acc + split_<f>_results.pkl)"
