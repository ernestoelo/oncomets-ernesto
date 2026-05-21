"""train_obj3.py — SKELETON del training script del Objetivo 3.

================================================================================
ESTADO: SCAFFOLDING NO FUNCIONAL. No entrena nada.
================================================================================

Esqueleto del wrapper de training para `DSMIL_CLAM_MB`. Replica el PATRÓN de
`clam_environ/main.py` de Sebastián (argparse -> carga de dataset/splits ->
build del modelo -> train loop estilo `train_loop_clam` -> summary.csv).
NO es una copia de `main.py`: reusa el patrón, no el archivo.

Regla de containment (CLAUDE.md): `main.py` y `core_utils.py` se IMPORTAN
desde `clam_environ/` vía `sys.path`, NO se copian. Todo output
(`--results_dir`, logs) va a paths absolutos bajo
`clam_testing2/oncomets-ernesto/`.

Regla SLURM: este script NO se corre con `python` directo sobre GPU. La
ejecución efectiva va por `sbatch scripts/train_dsmil.slurm` (pendiente,
post-reunión). Aquí solo se define la lógica.

Cómo se conecta con el resto:
  - modelo  : DSMIL_CLAM_MB  (de dsmil_wrapper.py)
  - dataset : Generic_MIL_Dataset  (de clam_environ/dataset_modules/)
  - loop    : train_loop_clam / validate  (de clam_environ/utils/core_utils.py)
              SI son compatibles con la firma de DSMIL_CLAM_MB.forward;
              si no, se implementa el loop local marcado abajo.
"""

import argparse
import os
import sys

# Path del codebase de Sebastián — para IMPORTAR (no copiar). READ-ONLY.
CLAM_ENVIRON = "/media/administrador/Storage1/sdonoso/clam_environ"


def build_argparser() -> argparse.ArgumentParser:
    """Args del Objetivo 3. Espejo de los 'args bendecidos' de CLAUDE.md
    (run_all_training.sh de Sebastián), más los específicos de DSMIL.
    """
    p = argparse.ArgumentParser(description="Train DSMIL_CLAM_MB (Objetivo 3).")
    # --- datos / splits (mismos que main.py de CLAM) -------------------------
    p.add_argument("--task", type=str, required=True,
                   help="Task de TASK_CONFIGS (ej. microcalcificaciones_pth).")
    p.add_argument("--exp_code", type=str, required=True,
                   help="Identificador del experimento.")
    p.add_argument("--split_dir", type=str, required=True,
                   help="Directorio con splits_0.csv (ej. .../splits/<task>_pth_100).")
    p.add_argument("--data_root_dir", type=str, required=True,
                   help="Raíz de las features .pt (environ/).")
    p.add_argument("--results_dir", type=str, required=True,
                   help="Salida — RUTA ABSOLUTA bajo clam_testing2/ (containment).")
    # --- args bendecidos por Sebastián (CLAUDE.md) ---------------------------
    p.add_argument("--drop_out", type=float, default=0.25)
    p.add_argument("--lr", type=float, default=2e-4)
    p.add_argument("--bag_loss", type=str, default="ce", choices=["ce", "svm"])
    p.add_argument("--inst_loss", type=str, default="svm", choices=["svm", "ce"])
    p.add_argument("--embed_dim", type=int, default=512,
                   help="512 para CONCH (1024 era ResNet legacy).")
    p.add_argument("--k", type=int, default=1, help="nº de folds.")
    p.add_argument("--B", type=int, default=8, help="top-B/bottom-B instance path.")
    p.add_argument("--bag_weight", type=float, default=0.7)
    p.add_argument("--max_epochs", type=int, default=30)
    p.add_argument("--early_stopping", action="store_true")
    p.add_argument("--weighted_sample", action="store_true")
    p.add_argument("--auto_label_dict", action="store_true",
                   help="Genera label_dict desde el CSV (ver CLAUDE.md).")
    # --- específicos de DSMIL ------------------------------------------------
    p.add_argument("--dsmil_q_dim", type=int, default=128,
                   help="Dim del espacio de queries del aggregator DSMIL.")
    p.add_argument("--dsmil_passing_v", action="store_true",
                   help="v-net como MLP en vez de Identidad (ver dsmil_wrapper).")
    return p


def build_model(args):
    """Construye DSMIL_CLAM_MB. SKELETON."""
    # import local — mantiene este módulo import-safe a nivel top-level.
    from dsmil_wrapper import DSMIL_CLAM_MB  # noqa: F401

    # TODO(impl): instanciar la loss de instancia (SmoothTop1SVM si
    #   inst_loss == "svm"), igual que main.py de CLAM, y pasarla al modelo.
    # TODO(impl):
    #   model = DSMIL_CLAM_MB(
    #       n_classes=<n_clases de la task>, embed_dim=args.embed_dim,
    #       k_sample=args.B, dropout=args.drop_out,
    #       instance_loss_fn=<inst_loss_fn>)
    #   return model.cuda()
    raise NotImplementedError("build_model: skeleton — implementar post-reunión.")


def get_datasets(args):
    """Carga dataset + splits con la maquinaria de CLAM. SKELETON."""
    if CLAM_ENVIRON not in sys.path:
        sys.path.insert(0, CLAM_ENVIRON)
    # TODO(impl): from dataset_modules.dataset_generic import Generic_MIL_Dataset
    # TODO(impl): construir el dataset desde dataset_<task>_label.csv y
    #   data_root_dir; aplicar return_splits(from_id=False,
    #   csv_path=<split_dir>/splits_0.csv) -> (train, val, test).
    # TODO(impl): resolver label_dict (--auto_label_dict: orden alfabético
    #   de labels únicos del CSV; ver CLAUDE.md "main.py").
    raise NotImplementedError("get_datasets: skeleton — implementar post-reunión.")


def train_one_fold(datasets, fold: int, args):
    """Entrena un fold. SKELETON.

    Plan: reutilizar `utils/core_utils.py` de Sebastián.
        from utils.core_utils import train  (o train_loop_clam + validate)
    `train_loop_clam` combina la loss como
        total = bag_weight*L_bag + (1-bag_weight)*L_instance   (core_utils.py)
    y es agnóstico al modelo MIENTRAS DSMIL_CLAM_MB.forward respete la firma
        (logits, Y_prob, Y_hat, A_raw, results_dict).
    Si algún detalle del loop asume internals de CLAM_MB incompatibles, caer
    al loop local marcado abajo.
    """
    # TODO(impl, opción A — reusar): from utils.core_utils import train
    #   results, test_auc, val_auc, test_acc, val_acc = train(datasets, fold, args)
    #
    # TODO(impl, opción B — loop local, solo si A no es compatible):
    #   for epoch in range(args.max_epochs):
    #       for bag, label in train_loader:
    #           logits, Y_prob, Y_hat, _, res = model(bag, label,
    #                                                  instance_eval=True)
    #           loss = bag_weight*bag_loss(logits, label) \
    #                  + (1-bag_weight)*res["instance_loss"]
    #           loss.backward(); opt.step(); opt.zero_grad()
    #       validate(...)  # early stopping sobre val_loss/val_auc
    raise NotImplementedError("train_one_fold: skeleton — implementar post-reunión.")


def write_summary(all_results, args):
    """Escribe summary.csv (mismas columnas que core_utils.py). SKELETON."""
    # TODO(impl): DataFrame con columnas test_auc/test_acc/val_auc/val_acc por
    #   fold y volcarlo a os.path.join(args.results_dir, "summary.csv").
    #   Mantener el formato del summary.csv de CLAM para que la comparación
    #   lado a lado con Objetivos 1 y 2 sea directa.
    raise NotImplementedError("write_summary: skeleton — implementar post-reunión.")


def main():
    args = build_argparser().parse_args()
    os.makedirs(args.results_dir, exist_ok=True)

    # TODO(impl): orquestación — espejo de main.py de CLAM:
    #   datasets = get_datasets(args)
    #   all_results = []
    #   for fold in range(args.k):
    #       model = build_model(args)
    #       all_results.append(train_one_fold(datasets, fold, args))
    #   write_summary(all_results, args)
    raise NotImplementedError(
        "train_obj3.py es un skeleton no funcional. La ejecución efectiva va "
        "post-reunión, vía sbatch (regla SLURM — nunca python directo en GPU)."
    )


if __name__ == "__main__":
    main()
