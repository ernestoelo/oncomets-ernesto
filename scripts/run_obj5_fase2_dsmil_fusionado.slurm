#!/bin/bash
#SBATCH --job-name=eg_f2_dsmil_fus
#SBATCH --partition=debug
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=16
#SBATCH --mem=32G
#SBATCH --time=12:00:00
#SBATCH --output=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/logs/%x_%j.out
#SBATCH --error=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/logs/%x_%j.err
#SBATCH --chdir=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto

# ============================================================
#  OBJETIVO 5 — FASE 2: CLAM vs DSMIL sobre el binario fusionado.
#  Modelo DSMIL_CLAM_MB (harness train_dsmil.py --model_type dsmil, default).
# ============================================================
# Compara la arquitectura DSMIL contra el CLAM de Fase 1 sobre EXACTAMENTE
# el mismo fusionado (mismo CSV, mismos k=3 splits, mismo harness). Reabre
# DSMIL SOLO para el régimen fusionado (hipotesis.md §2.1): el fusionado tiene
# ~2250 train slides → DSMIL ya NO está data-starved (el cuello "datos" del
# veredicto previo, job 4137 sobre 264 slides, no aplica acá).
#
# GATE DE COLAPSO (guardrail hipotesis.md §1.3): antes de gastar GPU, verifica
# que Fase 1 (CLAM) no colapsó a la mayoritaria (mean balanced_acc >= 0.55).
# Si colapsó, comparar arquitecturas sobre una task degenerada no tiene
# sentido → sale limpio (exit 0) sin correr DSMIL.
#
# w_max=0.1 (R1=B.1.3, único hiperparámetro DSMIL, fijo). Resto idéntico a
# Fase 1 (B=8, bag_weight 0.7, lr 2e-4, drop_out 0.25, CONCH 512, 30 epochs).
#
# Lanzamiento encadenado (NO autónomo — solo con OK de Ernesto):
#     sbatch --dependency=afterany:<job_fase1> scripts/run_obj5_fase2_dsmil_fusionado.slurm
# Monitor: tail -f logs/eg_f2_dsmil_fus_*.out
# Tiempo estimado: ~7h (3 folds × 30 epochs × ~2250 slides, DSMIL más lento). --time 12h.
# ============================================================

set -euo pipefail

REPO=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto
CLAM=/media/administrador/Storage1/sdonoso/clam_environ
FEATURES_DIR="$CLAM/environ/features/pt_files"
CSV="$REPO/data/csv_fusion/dataset_microcalcificaciones_presencia_label.csv"
SPLIT_DIR="$REPO/data/splits_kfold/microcalcificaciones_presencia_100"
RESULTS_DIR="$REPO/results/obj5_fase2_dsmil_fusionado"
FASE1_GLOB="$REPO/results/obj5_fase1_clam_fusionado/clam_presencia_f*_s1"
B=8
K=3

source /home/sdonoso/miniconda3/etc/profile.d/conda.sh
conda activate clam_latest
PYBIN="$CONDA_PREFIX/bin/python"   # 'python' a secas está ROTO (ADFRsuite py2.7)

echo "Job $SLURM_JOB_ID started at $(date) on $(hostname)"
"$PYBIN" -c "import torch; assert torch.cuda.is_available(), 'no CUDA'; print('torch', torch.__version__, 'cuda', torch.version.cuda)"
nvidia-smi | head -20 || true   # '|| true': head cierra el pipe -> SIGPIPE (workaround D)

# ── GATE DE COLAPSO (guardrail §1.3) ─────────────────────────────────
# Si Fase 1 (CLAM) colapsó (mean balanced_acc < 0.55) o no produjo
# resultados, NO correr Fase 2. Salir LIMPIO (exit 0) para no marcar el
# job como fallido ni quemar GPU compartida. Idiom 'if !' exento de set -e.
if ! "$PYBIN" "$REPO/scripts/gate_no_colapso.py" \
    --results_glob "$FASE1_GLOB" --threshold 0.55 --expected_folds "$K" ; then
  echo "GATE: Fase 1 colapsó/incompleta/no corrió → NO se corre Fase 2 (guardrail §1.3). Salida limpia."
  echo "Job $SLURM_JOB_ID done (SKIPPED Fase 2) at $(date)"
  exit 0
fi

# Verificador de splits (defensa en profundidad: por si Fase 2 se lanza
# standalone sobre splits regenerados; idiom 'if !' exento de set -e).
if ! "$PYBIN" "$REPO/scripts/verify_kfold_splits.py" ; then
  echo "VERIFY KFOLD FAILED — splits inconsistentes, abortar"; exit 1
fi

# k=3 folds de DSMIL sobre el fusionado (mismos splits que Fase 1).
for ((f=0; f<K; f++)); do
  echo ""
  echo "===== FASE 2 DSMIL fusionado — fold $f / $((K-1)) ====="

  if ! "$PYBIN" "$REPO/scripts/preflight_minpatch.py" \
      --split_dir "$SPLIT_DIR" --features_dir "$FEATURES_DIR" \
      --min_patches "$B" --fold "$f" ; then
    echo "PREFLIGHT FAILED en fold $f"; exit 1
  fi

  CUDA_VISIBLE_DEVICES=0 "$PYBIN" "$REPO/scripts/train_dsmil.py" \
    --model_type    dsmil \
    --task          microcalcificaciones_presencia \
    --exp_code      "dsmil_presencia_f${f}" \
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
    --w_max         0.1 \
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
echo "Results under $RESULTS_DIR/dsmil_presencia_f<0..$((K-1))>_s1/  (test_metrics.json con balanced_acc)"
