#!/bin/bash
#SBATCH --job-name=eg_f1_clam_fus
#SBATCH --partition=debug
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=16
#SBATCH --mem=32G
#SBATCH --time=10:00:00
#SBATCH --output=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/logs/%x_%j.out
#SBATCH --error=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/logs/%x_%j.err
#SBATCH --chdir=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto

# ============================================================
#  OBJETIVO 5 — FASE 1: binario fusionado "tiene/no tiene microcalcificaciones".
#  Modelo CLAM_MB baseline (harness train_dsmil.py --model_type clam).
# ============================================================
# Task fusionada (hipotesis.md §1.2): label="si" si hay micro en cualquier
# tejido, "no" si no_identificado. CSV propio (2814 slides: 328 si / 2486 no,
# ratio 7.58:1, cumple cap 10x). k=3 (régimen de test grande, ~33 pos/fold →
# pocas folds bastan; hipotesis.md §1.3).
#
# Harness = scripts/train_dsmil.py --model_type clam → MISMO train/val/test
# que Fase 2 (DSMIL) → comparación apples-to-apples. Reproduce el config
# bendecido del job 4109 (CLAM_MB, SmoothTop1SVM, B=8, bag_weight=0.7,
# lr=2e-4, drop_out=0.25, CONCH 512, weighted_sample, 30 epochs).
#
# Argumento + métrica: sprints/B4_sprint4/objetivo_5_fusion_binaria/hipotesis.md
# (Fase 1). Reviewer OK 2026-05-27.
#
# CONTAINMENT: lee CSV/splits propios (clam_testing2/) y features read-only de
# clam_environ; TODO output bajo clam_testing2/. train_dsmil.py fuerza
# results_dir bajo clam_testing2/ (guard interno).
#
# Lanzamiento encadenado (NO autónomo — solo con OK de Ernesto):
#     sbatch --dependency=afterany:<job_fase0> scripts/run_obj5_fase1_clam_fusionado.slurm
# Monitor: tail -f logs/eg_f1_clam_fus_*.out
# Tiempo estimado: ~5-9h (3 folds × 30 epochs × ~2250 slides, según velocidad
# real por bag). --time 10h con holgura.
# ============================================================

set -euo pipefail

REPO=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto
CLAM=/media/administrador/Storage1/sdonoso/clam_environ
FEATURES_DIR="$CLAM/environ/features/pt_files"
CSV="$REPO/data/csv_fusion/dataset_microcalcificaciones_presencia_label.csv"
SPLIT_DIR="$REPO/data/splits_kfold/microcalcificaciones_presencia_100"
RESULTS_DIR="$REPO/results/obj5_fase1_clam_fusionado"
B=8
K=3

source /home/sdonoso/miniconda3/etc/profile.d/conda.sh
conda activate clam_latest
PYBIN="$CONDA_PREFIX/bin/python"   # 'python' a secas está ROTO (ADFRsuite py2.7)

echo "Job $SLURM_JOB_ID started at $(date) on $(hostname)"
"$PYBIN" -c "import torch; assert torch.cuda.is_available(), 'no CUDA'; print('torch', torch.__version__, 'cuda', torch.version.cuda)"
nvidia-smi | head -20 || true   # '|| true': head cierra el pipe -> SIGPIPE (workaround D)

# Verificador determinístico de los splits fusionados (smoke #1).
if ! "$PYBIN" "$REPO/scripts/verify_kfold_splits.py" ; then
  echo "VERIFY KFOLD FAILED — splits inconsistentes, abortar"; exit 1
fi

# k=3 folds de CLAM sobre el fusionado. Cada fold = exp_code propio (no
# colisiona) con su summary.csv + test_metrics.json (balanced_acc).
for ((f=0; f<K; f++)); do
  echo ""
  echo "===== FASE 1 CLAM fusionado — fold $f / $((K-1)) ====="

  # Preflight obligatorio (workaround G): ninguna slide de train con
  # n_patches < B (crashearía torch.topk en inst_eval).
  if ! "$PYBIN" "$REPO/scripts/preflight_minpatch.py" \
      --split_dir "$SPLIT_DIR" --features_dir "$FEATURES_DIR" \
      --min_patches "$B" --fold "$f" ; then
    echo "PREFLIGHT FAILED en fold $f"; exit 1
  fi

  CUDA_VISIBLE_DEVICES=0 "$PYBIN" "$REPO/scripts/train_dsmil.py" \
    --model_type    clam \
    --task          microcalcificaciones_presencia \
    --exp_code      "clam_presencia_f${f}" \
    --csv_path      "$CSV" \
    --data_root_dir "$CLAM/environ" \
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

  echo "===== fold $f done ====="
done

echo ""
echo "Job $SLURM_JOB_ID done at $(date)"
echo "Results under $RESULTS_DIR/clam_presencia_f<0..$((K-1))>_s1/  (test_metrics.json con balanced_acc)"
