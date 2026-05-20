# Objetivo 1 — Resultados del baseline CLAM (MicroCalcificaciones, B=8)

> Esqueleto — se llena cuando el job `4083` complete. **Pendiente de ejecución.**

## Setup

| Campo | Valor |
|---|---|
| Tarea | `microcalcificaciones_pth` (priv+TCGA+HistAI) |
| Split | `environ/splits/microcalcificaciones_pth_100` (train 2438 / val 319 / test 315) |
| Features | CONCH 512-dim (`environ/features/pt_files/`) |
| Args | `--drop_out 0.25 --lr 2e-4 --bag_loss ce --inst_loss svm --model_type clam_mb --embed_dim 512 --k 1 --early_stopping --weighted_sample --auto-label-dict --B 8` |
| env | `clam_latest` (torch 2.8.0+cu128) |
| Script | `slurm/baseline_microcalc_B8.slurm` |
| Job ID | `4083` |
| Encolado | 2026-05-20, ST=PD (al final de la cola, tras `conch_fe`) |
| Inicio (PD→R) | _pendiente_ |
| Fin | _pendiente_ |
| Duración | _pendiente_ |

## N efectivo (cobertura de features al ejecutar)

> Verificar en el log cuántas slides se saltaron por `.pt` ausente (warnings
> "Feature file not found"). Al preparar: 128 histai sin `.pt` (train 83/val 28/test 17),
> en extracción por `conch_fe`.

| Partición | Nominal | Saltadas (log) | Efectivo |
|---|---|---|---|
| train | 2438 | _pend_ | _pend_ |
| val | 319 | _pend_ | _pend_ |
| test | 315 | _pend_ | _pend_ |

## Métricas (de `results/baseline_microcalc_pth_B8/<exp>_s1/summary.csv`)

| Fold | test_auc | val_auc | test_acc | val_acc |
|---|---|---|---|---|
| 0 | _pend_ | _pend_ | _pend_ | _pend_ |

## Régimen de evaluación (clases efectivas en val/test)

> Documentar qué clases quedaron con <2 ejemplos en val/test y sobre qué subset
> el AUC es computable (hallazgo Sprint 3). 8 clases; las compuestas raras tienen
> 1 ej. en val/test.

## Comparación contra V4 (referencia histórica)

> V4 reportó AUC test ≈ 0.55 (n=548, probablemente otro conjunto). NO es blanco
> de reproducción exacta — se usa `_pth` (3072). Registrar el número observado
> sin forzar interpretación.

## Convergencia (de los logs)

> bag loss (`train_error`) y instance loss (`train_clustering_loss`): ¿convergen?
> (Sprint 3: instance loss converge aunque bag loss no, en datasets con clases
> ausentes en val/test.)

## Warnings / errores del `.err`

_pendiente_
