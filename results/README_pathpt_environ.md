# Experimentos PathPT-CONCH en CLAM — OncoMets / Environ

Autor: Ernesto Gamero, Sprint B5. PathPT (`train_pathpt.py`) vs CLAM (baseline), k=5 pareado:
los dos brazos leen los mismos splits. PathPT deja CONCH congelado y entrena un módulo espacial
y los prompts de texto (CAP); reusa las features de visión CONCH ya generadas, no las regenera.
Detalle por tarea (matrices de confusión, Δ pareado, mecanismos) en
`sprints/B5_sprint5/pathpt/resultados_{necrosis,mitotic}.md`.

## Tareas

- Necrosis (binaria: si / no).
- Tasa mitótica (3 grados ordinales Nottingham: score_1 / score_2 / score_3).
- Microcalcificaciones (3 binarias) — solo prueba zero-shot previa, sin entrenar.

## Dataset

Cohorte `_pth` = Privado (Environ) + TCGA + HistAI, sin `no_identificado`.

- necrosis: si 313 / no 83 (n 396)
- mitótica: score_1 636 / score_2 287 / score_3 254 (n 1177)
- microcalc (zero-shot): carcinoma si 68 / no 260; cdis si 118 / no 210; tejido si 192 / no 136

## Splits

`data/splits_kfold/{cdis_necrosis_2clases_pth,grado_mitotic_3clases_pth}_100/splits_{0..4}.csv`
— Monte-Carlo k=5 estratificado, seed 1. Los dos brazos leen el mismo `splits_<f>.csv`, de ahí
el Δ pareado por fold.

## Comando

```
# PathPT (alcance full: módulo espacial θ_v + prompts θ_t + supervisión tile)
train_pathpt.py --task <tarea>   # 20 épocas, lr 1e-4, prompts CAP (necrosis Nota C, mitótica Nottingham)
# CLAM (baseline)
train_dsmil.py --model_type clam --B 8 --bag_weight 0.7 --lr 2e-4 --embed_dim 512 --drop_out 0.25
# Microcalc: prueba zero-shot sin entrenar (CPU)
scripts/zeroshot_gonogo.py
```

## Resultados (5 folds)

AUC como media / mejor de los 5 folds; balanced_acc como media. Necrosis ROC-AUC, mitótica
macro one-vs-rest.

| Tarea | CLAM AUC | PathPT AUC | CLAM bal | PathPT bal |
|---|---|---|---|---|
| necrosis | 0.727 / 0.798 | 0.661 / 0.798 | 0.633 | 0.613 |
| mitótica (macro-OVR) | 0.724 / 0.765 | 0.662 / 0.714 | 0.494 | 0.333 |

Microcalcificaciones (zero-shot, sin entrenar, solo AUC): carcinoma 0.629, cdis 0.533,
tejido 0.444.

Resumen: PathPT no supera a CLAM. En mitótica colapsa al grado mayoritario (balanced 0.333 = el
trivial de 3 clases), por la formulación de la clase base (tomé score_1 como base y domina los
parches), con sign-off de Sebastián pendiente. En microcalc el zero-shot quedó cerca del azar,
así que no se entrenó.
