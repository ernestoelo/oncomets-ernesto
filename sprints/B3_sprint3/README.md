# B3 — Sprint 3 (cerrado)

> **Estado**: cerrado en lo técnico el 5 mayo 2026. Presentación al equipo
> y feedback de Benjamín: 12 mayo 2026. Sprint 4 abierto post-feedback.

## Objetivo macro del sprint

Profundizar en la maquinaria de **pseudo-etiquetas + instance loss** de
CLAM (`L_instance`, SmoothTop1SVM, top-B/bottom-B), correr el modelo
end-to-end en Werner contra datos reales del proyecto, documentar el
pipeline a nivel de CSVs y emitir ≥ 2 propuestas de mejora teóricas.

## Entregables (4) — estado final

| # | Entregable | Estado | Artefactos |
|---|---|---|---|
| 1 | Estudio profundo `L_instance` + diagrama + tabla de hiperparámetros | Completado | [`objetivo_1_L_instance/`](objetivo_1_L_instance/) |
| 2 | Entrenamiento end-to-end de CLAM en Werner (≥ 1 task) | Completado — 2 runs | [`objetivo_2_entrenamiento/reporte.md`](objetivo_2_entrenamiento/reporte.md), `logs/` |
| 3 | Pipeline + formato de los CSV | Completado | [`objetivo_3_pipeline/`](objetivo_3_pipeline/), [`objetivo_2_entrenamiento/csv_format.md`](objetivo_2_entrenamiento/csv_format.md) |
| 4 | ≥ 2 propuestas de mejora algorítmica (teóricas) | Completado | [`objetivo_4_propuestas/`](objetivo_4_propuestas/) |

> El PDF final del sprint (`CLAM_Sprint_B3.pdf`) vive en **project files
> de claude.ai**, no en este repo. La presentación se construyó sobre el
> material acá referenciado.

## Métricas de los 2 runs CLAM ejecutados

Ambos runs sobre **dataset Environ**, args bendecidos por Sebastián
(`--drop_out 0.25 --lr 2e-4 --bag_loss ce --inst_loss svm --model_type
clam_mb --embed_dim 1024 --k 1 --early_stopping --weighted_sample
--auto-label-dict --max_epochs 30`), GPU 1.

### Run 1 — `tipo_histologico` (5 mayo 2026, 16:02 UTC-4)

- `exp_code`: `B3_sprint3_20260505_1602`
- Composición real (cross-check `splits_0.csv ⨯ labels.csv`):

  | Clase | train | val | test |
  |---|---|---|---|
  | carcinoma invasivo ductal | 30 | 3 | 4 |
  | carcinoma lobulillar invasivo | 4 | 0 | 0 |

- `summary.csv`: `test_auc=∅`, `val_auc=∅`, `test_acc=1.0`, `val_acc=1.0`.
- Lectura: AUC indefinido por single-class en val/test; `acc=1.0`
  engañosamente perfecto (4/4 sobre única clase presente).
- Instance loss **sí converge** (`train_clustering_loss` 0.7 → 0.075;
  `class 0/1 clustering acc = 1.0`). Bag loss `train_error` llega a 0.

### Run 2 — `grado_histologico_grado_general` (5 mayo 2026, 23:00 UTC-4)

- `exp_code`: `B3_sprint3_20260505_2300_grado_general`
- Composición real (cross-check, descriptor estaba **stale**):

  | Clase | train | val | test |
  |---|---|---|---|
  | grado 1 | 5 | 0 | 0 |
  | grado 2 | 9 | 3 | 1 |
  | grado 3 | 10 | 1 | 3 |
  | no identificado | 6 | 0 | 0 |

- `summary.csv`: `test_auc=1.0`, `val_auc=0.0`, `test_acc=0.25`, `val_acc=0.75`.
- Evaluación **efectivamente binaria** sobre `grado 2` vs `grado 3`.
- `test_auc=1.0` + `test_acc=0.25` = ranking correcto, argmax desplazado
  (threshold mal calibrado en multi-clase con clases minoritarias).
- Bag loss **NO converge** (`train_error=0.6667` en epoch 29). Instance
  loss **sí converge** (`train_clustering_loss=0.0889`,
  `class 0/1 clustering acc=1.0`).

Detalle exhaustivo: [`objetivo_2_entrenamiento/reporte.md`](objetivo_2_entrenamiento/reporte.md).

## Hallazgos metodológicos del sprint

Los siguientes hallazgos son **transversales** y aplican a sprints futuros.
También están consolidados en `CLAUDE.md` (root del repo) y en
`docs/codebase_map.md`.

### 1. `splits_0_descriptor.csv` puede estar desincronizado con `splits_0.csv`

Caso confirmado en `grado_histologico_grado_general_100`: el descriptor
reporta para val/test counts que **no matchean** el join programático
`splits_0.csv ⨯ dataset_<task>_label.csv`. Train counts sí matchean.
Causa probable: re-etiquetado del CSV de labels posterior a la generación
del descriptor — `splits_0.csv` (solo `slide_id`) sobrevive, el
descriptor queda stale.

**Verdad de campo**: derivar las particiones programáticamente del join.
**Regla operativa**: no confiar en el descriptor para reportes ni
decisiones de splits sin haberlo cross-checkeado.

### 2. Bug en `invasion_linfatica_vascular_100`

El descriptor lista tres clases: `'no identificada'` (femenino),
`'no identificado'` (masculino), `'presente'`. `--auto-label-dict` las
trata como tres clases distintas porque difieren en un carácter. Bug de
etiquetado en el CSV fuente que el flag propaga. **No usar esta task
hasta que Sebastián resuelva el typo.**

### 3. Clases minoritarias quedan enteras en train

En todas las tasks Environ con `seed=1`, `val_frac=test_frac=0.1` (defaults
de `create_splits_seq.py`), al menos una clase con < 10 slides queda
**100% en train**, con 0 ejemplos en val/test. Consecuencia directa:
`--auto-label-dict` registra clases que el modelo ve en train pero nunca
se evalúan, contaminando el espacio de output y generando AUC vacíos o
`nan`. Para tener AUC computables: o se evalúa sobre el subset binario
efectivo, o se regeneran splits con stratification.

### 4. Bag loss puede no converger en datasets pequeños

Cuando `--auto-label-dict` registra clases que el modelo nunca ve en
val/test (caso `grado_general`), el slide-level classifier **no aprende
a discriminar las 4 clases** — gradientes que el modelo no puede
calibrar contra señal externa. El instance loss SmoothTop1SVM converge
igual en esos casos (separa top-B / bottom-B parches dentro de cada
slide). Síntoma de fragilidad del slide-level classifier, **no** del
mecanismo de pseudo-etiquetado.

### 5. Identidad git en Werner

El `git config --global` del user compartido `onco` apunta a Sebastián
Donoso. Para commits desde Werner, **siempre setear
`git config --local user.name/user.email` dentro del repo**, nunca tocar
el global. Si no se setea local, los commits aparecerán como de Sebastián.

## Feedback de Benjamín (12 mayo 2026)

- Felicitó al equipo por el trabajo del sprint.
- **Dirección para Sprint 4**: pasar de propuestas teóricas a
  implementación con **argumento clínico / arquitectónico explícito**.
  No probar por probar.
- Una ablation cuenta como argumento sólido solo si la hipótesis está
  enunciada de antemano y la métrica de éxito está predefinida.

Este feedback se internaliza como **regla operativa nueva** en
`CLAUDE.md` ("Argumento antes de código").

## Conexión con Sprint 4

Ver [`../B4_sprint4/README.md`](../B4_sprint4/README.md). En corto, el
Sprint 4 abre **4 hilos** sobre el dataset compartido que se definirá
en la próxima reunión con Sebastián y Eduardo:

1. **Baseline CLAM reproducible** con los args bendecidos.
2. **Ablation B=8 vs B=16** sobre tareas con AUC < 0.65.
3. **Implementar DSMIL** como módulo MIL alternativo (wrapper-only).
4. **Heatmaps cualitativos** (con upgrade a cuantitativo si hay
   anotaciones de patólogo disponibles).

## Notas para el futuro

- Los subdirectorios `objetivo_1..4/` quedan como **artefactos
  históricos** del sprint, no se borran ni reorganizan.
- Si Sebastián edita su codebase, hay que **re-validar** los números de
  línea citados en `objetivo_2_entrenamiento/reporte.md` y en
  `docs/codebase_map.md`.
