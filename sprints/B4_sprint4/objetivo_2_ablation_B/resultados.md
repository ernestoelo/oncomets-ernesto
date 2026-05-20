# Objetivo 2 — Resultados ablation B=8 vs B=16 (MicroCalcificaciones, _pth)

> Esqueleto — el brazo B=16 (`slurm/ablation_microcalc_B16.slurm`) se encola
> **solo después** de que el baseline B=8 (job 4083) complete y se revise.
> GPU única → secuencial. **Pendiente de ejecución.**

## Setup (idéntico al baseline salvo --B)

| Campo | B=8 (baseline) | B=16 (ablation) |
|---|---|---|
| Script | `slurm/baseline_microcalc_B8.slurm` | `slurm/ablation_microcalc_B16.slurm` |
| `--B` | 8 | 16 |
| Job ID | 4083 | _pendiente_ |
| results_dir | `results/baseline_microcalc_pth_B8/` | `results/ablation_microcalc_pth_B16/` |
| Resto de args | idénticos | idénticos |

## Tabla comparativa

| Métrica | B=8 | B=16 | Δ (B16−B8) | Veredicto |
|---|---|---|---|---|
| test_auc | _pend_ | _pend_ | _pend_ | _pend_ |
| val_auc | _pend_ | _pend_ | _pend_ | — |
| gap val−test | _pend_ | _pend_ | _pend_ | _pend_ |
| train_clustering_loss final | _pend_ | _pend_ | _pend_ | — |

## Hipótesis y métrica de éxito (predefinidas)

- **Hipótesis**: aumentar B de 8 a 16 enriquece la señal supervisada del
  SmoothTop1SVM en el `instance_classifier` path → mejora pseudo-etiquetas en
  régimen focal (microcalcificaciones).
- **Métrica de éxito**: **ΔAUC test ≥ +0.03** (B16 − B8), manteniendo o reduciendo
  el gap val−test.
- **Banda ambigua**: si `|Δ| < 0.02` o `nan` en alguna clase → reportar literal
  como **"no concluyente bajo single seed"**. Múltiples seeds → próximo sprint.
  NO forzar interpretación para que cuadre.

## Régimen / caveats

> Mismo régimen de desbalance que el baseline. Documentar subset efectivo de AUC.

## Costos

| | tiempo cola | tiempo run | mem pico |
|---|---|---|---|
| B=8 | _pend_ | _pend_ | _pend_ |
| B=16 | _pend_ | _pend_ | _pend_ |
