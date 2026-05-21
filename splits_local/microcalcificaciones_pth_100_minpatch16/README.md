# Split filtrado — `microcalcificaciones_pth_100_minpatch16`

Copia **filtrada** del split canónico de `microcalcificaciones_pth`, usada en
el Sprint 4 para el baseline B=8 y la ablation B=16.

## Origen (split canónico)

```
/media/administrador/Storage1/sdonoso/clam_environ/environ/splits/microcalcificaciones_pth_100/splits_0.csv
```

`clam_environ/` es **read-only** (codebase de Sebastián) — por eso la copia
filtrada vive aquí, en el workspace personal.

## Razón de la desviación

Bug observado en el run **4096** (Sprint 4): `models/model_clam.py` →
`inst_eval` hace `torch.topk(A, k_sample)` con `k_sample = --B`. Si una slide
del **train** tiene menos de `B` parches, `topk` falla con
`RuntimeError: selected index k out of range` y mata el entrenamiento.
Con `--weighted_sample` (muestreo con reemplazo) la slide problemática se
sortea de forma estocástica → el crash apareció en una época tardía.

## Slides removidas (solo del split de **train**)

| slide_id | nº parches (`.pt` shape[0]) | rompe |
|---|---|---|
| `histai_1536_slide_H&E_0` | 6 | B=8 y B=16 |
| `histai_1196_slide_H&E_0` | 8 | B=16 |

`val` y `test` se dejan **intactos**: el path de evaluación (`summary()`) hace
forward plano sin `inst_eval`, así que slides chicas en val/test no crashean.
(test tiene 1 slide de 6 parches, `histai_0959_slide_H&E_0` — inofensiva.)

## Threshold

**`min_patches = 16`.** Se elige 16 (no 8) para que el MISMO split sirva a
B=8 y a B=16 → ablation controlada: idénticos datos de train, la única
variable es `--B`.

## Conteos

| Partición | Canónico | Filtrado |
|---|---|---|
| train | 2438 | **2436** (−2) |
| val | 319 | 319 |
| test | 315 | 315 |

(50 slides de train no tienen `.pt` extraído — se **mantienen** en el split;
el dataloader de Sebastián las salta con warning, no causan el crash de topk.)

## Cómo se generó (reproducible)

```bash
python scripts/filter_split_by_minpatch.py \
  --canonical_split /media/administrador/Storage1/sdonoso/clam_environ/environ/splits/microcalcificaciones_pth_100/splits_0.csv \
  --features_dir    /media/administrador/Storage1/sdonoso/clam_environ/environ/features/pt_files \
  --min_patches     16 \
  --out_dir         splits_local/microcalcificaciones_pth_100_minpatch16
```

Detalle de la corrida: `report.txt` en este mismo directorio.
Fecha de generación: **2026-05-21**.

## Implicaciones

- **Comparabilidad con V4** (`Environ_OncoMets_Metricas_V4.pdf`): V4 usó el
  split canónico completo. La diferencia por remover 2 de 2438 slides de
  train (0.08 %) es **despreciable**, pero queda documentada. De todos modos
  V4 es referencia histórica, no blanco de reproducción exacta del Sprint 4.
- La ablation B=8 vs B=16 **sí es estrictamente controlada**: ambos brazos
  usan este mismo split filtrado.
- Las 2 slides removidas (biopsias HistAI con muy pocos parches) se llevan a
  la reunión como pregunta para Sebastián — ver
  `sprints/B4_sprint4/objetivo_3_dsmil/investigacion/04_riesgos_y_preguntas_reunion.md`.
