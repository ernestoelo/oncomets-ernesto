# Objetivo 1 — Baseline CLAM reproducible

> Sprint B4. **Punto de partida** del sprint: los otros 3 hilos comparan
> contra estos números.

## Hipótesis

Sobre el **dataset compartido** (composición pendiente de reunión), con
los args bendecidos por Sebastián, CLAM_MB reproduce métricas **dentro
de ±0.02 AUC** de las reportadas en `Environ_OncoMets_Metricas_V4.pdf`
para cada una de las tareas prioritarias.

Si la reproducción no cae dentro de tolerancia, hay drift en datos,
splits o ambiente que debe diagnosticarse antes de avanzar a los hilos
2–4 (ablation, DSMIL, heatmaps).

## Métrica de éxito

- **`test_auc` reproducido** dentro de ±0.02 del valor reportado para
  cada tarea prioritaria con AUC < 0.65.
- **`val_auc` reproducido** dentro de ±0.05 (más tolerante porque val
  set es más pequeño y suele variar).
- **Convergencia**: tanto bag loss como instance loss (`L_instance`)
  convergen — confirmar contra el patrón observado en Sprint 3 (instance
  loss converge incluso cuando bag loss no lo hace en datasets pequeños).

## Configuración

Args bendecidos por Sebastián (de `run_all_training.sh` y validados
en Sprint 3):

```
--drop_out 0.25
--lr 2e-4
--bag_loss ce
--inst_loss svm
--model_type clam_mb
--embed_dim 1024            # 512 si el dataset compartido usa CONCH-TCGA
--k 1
--early_stopping
--weighted_sample
--auto-label-dict
```

**`--B`** queda al default `8` para este baseline. La variación de `B`
es Objetivo 2, no este.

## Dependencias (pendientes de reunión)

- [ ] **Dataset compartido**: path en Werner a `dataset_<task>_label.csv`
      y a `features/pt_files/<slide_id>.pt`. Confirmar `embed_dim`
      (512 vs 1024).
- [ ] **Splits canónicos**: path a `splits_0.csv` por tarea. Si no
      existen, generarlos con `create_splits_seq.py` siguiendo el
      protocolo de Sebastián.
- [ ] **Cross-check del descriptor** (Hallazgo 1 del Sprint 3) antes de
      reportar composición de splits.
- [ ] **Lista final de tareas prioritarias** (candidatas: MicroCalcificaciones,
      C.D.I. Grado Nuclear, C.D.I. Necrosis, G.H. Dif. Tubular).

## Plan de ejecución

1. Pre-vuelo: smoke test contra una task ya conocida del Sprint 3
   (`tipo_histologico` o `grado_general`) para confirmar que el entorno
   sigue sano. Sin esto, un fallo en el baseline puede confundirse con
   drift del entorno.
2. Lanzar baseline en GPU 1, una tarea prioritaria a la vez (no paralelo
   — interferencia de memoria con jobs de `jenny2` en GPUs 2/3).
3. Persistir bajo `logs/<task>_<exp_code>/` con `config_snapshot.txt` y
   `train.log` (delegar a agente `trainer`).
4. Cross-check de splits antes de reportar (no confiar en descriptor).
5. Llenar `resultados.md` con tabla **task × {test_auc, val_auc,
   test_acc, val_acc, train_clustering_loss_final, train_error_final}**.
6. Comparar contra `Environ_OncoMets_Metricas_V4.pdf` y reportar drift
   (si lo hay) con hipótesis del origen.

## Output esperado

```
objetivo_1_baseline/
├── README.md                       # este archivo
├── resultados.md                   # tabla final + análisis de drift
├── logs/
│   └── <task>_<exp_code>/          # uno por tarea
│       ├── config_snapshot.txt
│       ├── train.log
│       ├── metrics.csv
│       └── summary.csv
└── splits_crosscheck/              # composición real de splits (cross-check programático)
    └── <task>_split_composition.md
```

## Placeholder de resultados

_Pendiente de ejecutar — completar tras reunión y primer run._

| Tarea | test_auc obs | test_auc V4 | Δ | val_auc obs | val_auc V4 | Δ | Comentario |
|---|---|---|---|---|---|---|---|
| MicroCalcificaciones | — | 0.55 | — | — | 0.82 | — | — |
| C.D.I. Grado Nuclear | — | 0.60 | — | — | n/r | — | — |
| C.D.I. Necrosis | — | 0.61 | — | — | n/r | — | — |
| G.H. Dif. Tubular | — | 0.65 | — | — | 0.81 | — | — |

> `n/r` = no reportado en el resumen de V4 que distribuyó Sebastián el
> 12 mayo 2026. Verificar contra el PDF cuando se obtenga acceso; si
> el val_auc aparece, completar acá.
