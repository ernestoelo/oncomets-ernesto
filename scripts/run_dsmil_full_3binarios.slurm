#!/bin/bash
# run_dsmil_full_3binarios.slurm — experimento completo DSMIL sobre las
# 3 tareas binarias de microcalcificaciones.
#
# Replica APPLES-TO-APPLES el patrón del job 4109 (baseline CLAM_MB,
# sprints/B4_sprint4/reformulacion_multilabel/train_microcalc_3binarios.slurm)
# sustituyendo `main.py` por `scripts/train_dsmil.py` extendido con
# val_loop + early_stopping + test eval (balanced_acc + confusion).
#
# Setup canónico (hipotesis.md §4, variables congeladas):
#   - 30 epochs, --early_stopping (R6 §5: nunca triggea con
#     stop_epoch=50 hardcoded > max_epochs=30, pero save_checkpoint
#     guarda el best por val_loss — el test eval carga ESE checkpoint).
#   - seed 1, B=8, bag_weight=0.7, lr=2e-4, drop_out=0.25.
#   - w_max=0.1 (B.1.3, único hiperparámetro nuevo, valor fijo).
#   - splits canónicos microcalcificaciones_en_<tejido>_pth_100/.
#   - 333 slides identificadas (no_identificado excluido) — MISMO
#     dataset que job 4109 → comparación limpia.
#
# Lanzamiento (solo con OK explícito de Ernesto, NO autónomo):
#     cd /media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto
#     squeue ; sinfo                # cortesía: GPU única
#     sbatch scripts/run_dsmil_full_3binarios.slurm
#
# Monitor:  tail -f logs/eg_dsmil_full_*.out
# Cancel:   scancel <jobid>
#
# Tiempo estimado: ~92 s/epoch × 30 epochs × 3 tasks ≈ 2h20m wall +
# overhead val/test → 3h. --time=04:00:00 por las dudas.

#SBATCH --job-name=eg_dsmil_full
#SBATCH --output=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/logs/%x_%j.out
#SBATCH --error=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/logs/%x_%j.err
#SBATCH --chdir=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=16
#SBATCH --mem=32G
#SBATCH --time=04:00:00
# (no --partition → usa la default 'debug')

set -euo pipefail

# Workaround B: `which python` apunta a ADFRsuite py2.7 roto.
PYBIN=/home/sdonoso/miniconda3/envs/clam_latest/bin/python

REPO=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto
CLAM=/media/administrador/Storage1/sdonoso/clam_environ
FEATURES_DIR=$CLAM/environ/features/pt_files
B=8

echo "===== Job $SLURM_JOB_ID started at $(date) on $(hostname) ====="
echo "PYBIN  = $PYBIN"
echo "REPO   = $REPO"
echo "CLAM   = $CLAM (READ-ONLY)"
nvidia-smi -L || true   # || true defensa workaround D (SIGPIPE)
"$PYBIN" -c "import torch; assert torch.cuda.is_available(), 'no CUDA'; print('torch', torch.__version__, 'cuda', torch.version.cuda)"

# 3 tareas binarias SECUENCIALES, mismo patrón que job 4109.
for TEJIDO in carcinoma_invasivo cdis tejido_no_neoplasico; do
  TASK="microcalcificaciones_en_${TEJIDO}_pth"
  CSV=$CLAM/environ/csv/dataset_microcalcificaciones_en_${TEJIDO}_label.csv
  SPLIT_DIR=$CLAM/environ/splits/${TASK}_100

  echo ""
  echo "===== TASK: $TASK ====="

  # ── PREFLIGHT (workaround G obligatorio) ─────────────────────────────
  # Reusa scripts/preflight_minpatch.py: falla rápido si alguna slide
  # de train tiene N parches < B. Idiom `if !` exento de set -e.
  if ! "$PYBIN" "$REPO/scripts/preflight_minpatch.py" \
      --split_dir    "$SPLIT_DIR" \
      --features_dir "$FEATURES_DIR" \
      --min_patches  "$B" ; then
    echo "PREFLIGHT FAILED en $TASK"
    exit 1
  fi

  # ── TRAINING + VAL + TEST ────────────────────────────────────────────
  CUDA_VISIBLE_DEVICES=0 "$PYBIN" "$REPO/scripts/train_dsmil.py" \
    --task          "$TASK" \
    --exp_code      "dsmil_full_${TEJIDO}_B${B}" \
    --csv_path      "$CSV" \
    --data_root_dir "$CLAM/environ" \
    --split_dir     "$SPLIT_DIR" \
    --results_dir   "$REPO/results/sprint4_obj3_dsmil_full" \
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
    --fold          0 \
    --label_dict    '{"no": 0, "si": 1}'

  echo "===== $TASK done ====="
done

echo ""
echo "===== Job $SLURM_JOB_ID done at $(date) ====="
echo "Artefactos en $REPO/results/sprint4_obj3_dsmil_full/dsmil_full_<tejido>_B${B}_s1/"
