# Objetivo 2 — Ablation cuantitativa `B=8` vs `B=16`

> Sprint B4. **Depende de Objetivo 1** (baseline reproducido) para tener
> referencia.

## Hipótesis

En tareas con `n < 600` slides y **patrones focales** (positivo localizado
en pocas regiones de la WSI, como MicroCalcificaciones o C.D.I. Necrosis),
incrementar `--B` de 8 a 16 enriquece la señal supervisora del
SmoothTop1SVM en el `instance_classifier` path al aumentar el número de
parches positivos / negativos seleccionados por slide. Esto debería:

- **Bajar `train_clustering_loss`** final (más muestras = mejor
  estimación del margen del SVM en el subset top/bottom).
- **Reducir el gap val/test** que hoy se observa en MicroCalcificaciones
  (0.27 absoluto entre val 0.82 y test 0.55).
- **No afectar materialmente las tareas con n ≥ 900** (G.H. Dif. Tubular,
  n=934), donde la mejora en señal del SVM ya está saturada con B=8.

**Conexión al código** (`models/model_clam.py:107–135`, `inst_eval` y
`inst_eval_out`): `B` controla el `k` de `torch.topk(A, B)` que selecciona
los top-B y bottom-B parches por attention score. El gradiente del
SmoothTop1SVM se computa solo sobre esos `2B` parches binarizados como
pseudo-positivos / pseudo-negativos.

## Métrica de éxito

Métrica primaria:

- **Δ `test_auc` (B=16 − B=8) ≥ +0.03** en al menos una tarea con n < 600.

Métricas secundarias (para descartar artefactos):

- **`train_clustering_loss` final con B=16 ≤ B=8** (señal de que la
  hipótesis del SVM más rico es correcta).
- **Gap val/test con B=16 ≤ gap con B=8** (señal de que la mejora no es
  por suerte de seed sino por enriquecimiento de la supervisión).
- **Δ `test_auc` (B=16 − B=8)** sobre tareas con n ≥ 900 dentro de
  ±0.02 (no efecto adverso por saturación).

Si Δ es **negativo** en alguna tarea, reportar y discutir antes de
avanzar (puede ser bias del seed; en ese caso replicar con `--seed 2`).

## Diseño experimental

- **Tareas**: mismas 4 prioritarias del Objetivo 1.
- **Splits**: los mismos splits del Objetivo 1 (mismo seed, misma
  composición). Sin esto la ablation no es controlada.
- **Variable controlada**: `--B` (8 → 16). Resto idéntico al baseline.
- **Replicación**: una seed para empezar (`seed=1`). Si Δ es marginal,
  replicar con `seed={2,3}` para confirmar.
- **Costo**: 2× los runs del baseline (~6 min por run en GPU 1 con
  `max_epochs=30`). Total ~48 min para 4 tareas × 2 valores de B.

## Dependencias

- [ ] **Objetivo 1 ejecutado** (baseline reproducible disponible para
      comparar). Sin baseline confirmado, una mejora de +0.03 puede ser
      ruido del entorno y no señal real.
- [ ] **Splits canónicos** definidos en la reunión.

## Output esperado

```
objetivo_2_ablation_B/
├── README.md                       # este archivo
├── resultados.md                   # tabla comparativa B=8 vs B=16 + análisis
└── logs/
    ├── <task>_B8_<exp_code>/       # reusable desde Objetivo 1 si los args son idénticos
    └── <task>_B16_<exp_code>/
```

## Placeholder de resultados

_Pendiente — completar tras ejecutar._

| Tarea | n | test_auc B=8 | test_auc B=16 | Δ test_auc | gap B=8 | gap B=16 | Veredicto |
|---|---|---|---|---|---|---|---|
| MicroCalcificaciones | 548 | — | — | — | 0.27 (V4) | — | — |
| C.D.I. Grado Nuclear | 508 | — | — | — | — | — | — |
| C.D.I. Necrosis | 508 | — | — | — | — | — | — |
| G.H. Dif. Tubular | 934 | — | — | — | 0.16 (V4) | — | — |

## Riesgo identificado

- **Confounder de seed**: con `n` pequeño un cambio de ±0.03 en AUC puede
  caer dentro del ruido de un solo seed. Tener listo el plan B de
  replicación con seeds adicionales.
- **Si Δ ≈ 0 en todas las tareas**: significa que la hipótesis del SVM
  saturado con B=8 no se sostiene en este dataset, y la implementación
  de DSMIL (Objetivo 3) tiene mayor prioridad porque el cuello no es el
  pseudo-label sampling sino la arquitectura MIL en sí.
