---
name: csv-audit
description: Audita y documenta CSVs / artefactos tabulares del pipeline OncoMets. Detecta descriptors stale, cross-check splits×labels. Triggers — auditar CSV, documentar CSV, cross-check de splits, descriptor desactualizado, csv stale.
---

# csv-audit — Auditoría pedagógica y cross-check de CSVs del pipeline

Skill para documentar y auditar cualquier CSV / artefacto tabular que
entra o sale del pipeline OncoMets. Resuelve dos problemas recurrentes
del proyecto:

1. **CSVs nuevos sin documentar**: cuando el equipo introduce un CSV
   (caso vivo: dataset compartido del Sprint 4), nadie sabe sus
   columnas, productor, consumidor, ni trampas conocidas. Esta skill
   fija un formato pedagógico mínimo.
2. **Metadata stale**: un CSV puede estar en disco pero **no reflejar
   la verdad de campo**. Caso confirmado en Sprint 3:
   `splits_0_descriptor.csv` de `grado_histologico_grado_general_100`
   tenía counts que no matcheaban el join `splits_0.csv ⨯
   dataset_<task>_label.csv`. Esta skill estandariza el cross-check
   programático.

## Cuándo activar

Triggers explícitos del usuario:

- "auditemos este CSV"
- "documentar el nuevo CSV del dataset compartido"
- "qué columnas tiene `<archivo>.csv`"
- "el descriptor está desactualizado"
- "hagamos cross-check del split"

Triggers implícitos (la skill **debe** activarse aunque el usuario no
la nombre):

- Discusión sobre un paso del pipeline que produce o consume un CSV.
- Introducción de un CSV nuevo al repo (especialmente con el dataset
  compartido del Sprint 4).
- Sospecha o sospecha potencial de metadata stale en `splits_0_descriptor.csv`,
  `summary.csv`, o cualquier resumen que dependa de un CSV fuente.
- Reportes de resultados que citen counts de splits sin haberlos
  verificado programáticamente.

## Formato pedagógico de CSV (canónico)

Toda documentación de un CSV en este repo usa este formato exacto:

```
CSV: <nombre exacto del archivo>
Path en server: <absoluto, ej. /media/administrador/Storage1/sdonoso/clam_environ/environ/csv/dataset_X_label.csv>
Schema (columnas y tipos):
  - col_1: tipo, ejemplo, qué representa
  - col_2: ...
Filas: <cuántas hay o se esperan>
Producido por: <script o paso (ej. create_splits_seq.py, paso manual)>
Consumido por: <script o paso (ej. main.py vía Generic_MIL_Dataset)>
Ejemplo (head -3): ...
Trampas conocidas: <ej. descriptor stale, label_dict bugs, encoding>
```

Donde:

- **Path en server**: absoluto (bajo `clam_environ/environ/...`). Si el CSV
  también vive snapshoteado en el repo del control center, añadir un segundo path.
- **Schema**: una línea por columna. Tipo (string / int / float),
  ejemplo concreto (real, copiado del archivo), descripción semántica.
  Para columnas que parecen booleanas pero en disco son strings
  `True`/`False`, **anotarlo**.
- **Filas**: count exacto si se conoce; rango esperado si no (ej.
  "una por slide etiquetada, ~500 para Environ"). Para CSVs que crecen
  con el tiempo, anotar la dimensión variable.
- **Producido por / Consumido por**: identificar el script o paso del
  pipeline, no solo "el equipo". Si es manual, decir "manual (Sebastián
  / Eduardo / Ernesto)".
- **Ejemplo (head -3)**: tres filas reales del archivo. Si tiene
  encoding peculiar (semicolons, BOM, comillas), conservarlas como están.
- **Trampas conocidas**: lista de gotchas vivos (descriptor stale,
  label_dict propagating typos, pandas 3.x rechazando int en columna
  str, etc.).

## Práctica complementaria — snapshot local

Cuando el CSV vive en `clam_environ/` (read-only) y el sprint depende de él:

1. **Copiar el CSV al workspace local del sprint**:
   `sprints/<sprint>/<objetivo>/csv_snapshots/<nombre>.csv`.
2. **Anotar la fecha y el path original** en el documento del objetivo:
   ```
   Snapshot: 2026-05-19 UTC-4
   Origen:   /media/administrador/Storage1/sdonoso/clam_environ/environ/csv/<archivo>.csv
   ```
3. **El snapshot es la verdad de referencia** durante el sprint. El archivo
   en el server puede mutar (re-etiquetado, regeneración de splits) sin que
   el sprint se entere.
4. Al cerrar el sprint, **revisar si el snapshot se desincronizó** del
   archivo en el server y dejar nota en `progress/history.md`.

## Cross-check programático (anti-stale)

Plantilla en Python para verificar que un descriptor / resumen no está
stale contra el archivo fuente. Adaptar según el caso:

```python
import pandas as pd

# Caso canónico: descriptor de split vs join con CSV de labels
split_path  = "<...>/splits/<task>_100/splits_0.csv"
labels_path = "<...>/csv/dataset_<task>_label.csv"
descriptor_path = "<...>/splits/<task>_100/splits_0_descriptor.csv"

split      = pd.read_csv(split_path, index_col=0)
labels     = pd.read_csv(labels_path)
descriptor = pd.read_csv(descriptor_path, index_col=0)

sid2lab = dict(zip(labels['slide_id'], labels['label']))

# Counts reales por partición × clase desde el join
real_counts = {}
for part in ['train', 'val', 'test']:
    slides = [s for s in split[part].dropna() if str(s).strip()]
    lab_series = pd.Series([sid2lab.get(s) for s in slides])
    real_counts[part] = lab_series.value_counts().to_dict()

print("Real counts (cross-check):")
for part, cnts in real_counts.items():
    print(f"  {part}: {cnts}")

print("\nDescriptor counts (file):")
print(descriptor)

# Reportar divergencias
divergences = []
for part in ['train', 'val', 'test']:
    if part not in descriptor.columns:
        continue
    for klass, real_n in real_counts[part].items():
        desc_n = int(descriptor.loc[klass, part]) if klass in descriptor.index else 0
        if real_n != desc_n:
            divergences.append((part, klass, desc_n, real_n))

if divergences:
    print("\nDIVERGENCES detected (descriptor stale):")
    for part, klass, desc_n, real_n in divergences:
        print(f"  {part} / {klass}: descriptor={desc_n}, real={real_n}")
else:
    print("\nDescriptor in sync with split.")
```

**Regla**: si hay divergencias, **el descriptor pierde**. El join
programático es la verdad de campo. Reportar al usuario y documentar
en `Trampas conocidas` del CSV.

## Tabla de CSVs canónicos del pipeline OncoMets

Mantener actualizada cuando aparezca un CSV nuevo (especialmente con el
dataset compartido del Sprint 4).

| CSV | Productor | Consumidor | Sirve para |
|---|---|---|---|
| `dataset_<task>_label.csv` | manual (equipo) | `main.py` vía `Generic_MIL_Dataset` | mapear `slide_id` → label por task |
| `splits_0.csv` | `create_splits_seq.py` | `main.py` | partición train/val/test por fold (verdad de campo) |
| `splits_0_bool.csv` | `create_splits_seq.py` | exploración manual | versión booleana del split |
| `splits_0_descriptor.csv` | `create_splits_seq.py` | nadie de confianza (puede estar stale) | conteo por clase del split |
| `summary.csv` | `core_utils.py` (fin del entrenamiento) | análisis post-hoc | métricas finales (test_auc/acc, val_auc/acc) por fold |
| `split_0_results.pkl` | `core_utils.py` | análisis post-hoc | predicciones por slide en val/test (no es CSV, pero misma lógica) |

## Cuándo NO usar esta skill

- Para CSVs que no tocan el pipeline (ej. tracking interno como
  `Excel_Objetivo_Especifico_*.xlsx` — eso es seguimiento, no pipeline).
- Para inspección casual de "cuántas filas tiene" — un `wc -l` directo
  basta.
- Para parsear logs de training — eso es `extract_metrics.py`, no esta
  skill.

## Hallazgos del proyecto que esta skill encapsula

1. **`splits_0_descriptor.csv` puede estar stale vs `splits_0.csv`**
   (Sprint 3, caso `grado_histologico_grado_general_100`). Causa
   probable: re-etiquetado del CSV de labels después de generar el
   descriptor. La regla operativa es **cross-checkear siempre antes de
   reportar**.
2. **`--auto-label-dict` propaga bugs de etiquetado** del CSV fuente
   (caso `invasion_linfatica_vascular_100`: `'no identificada'`
   masculino vs femenino). Verificar siempre el set de labels únicos
   en el CSV antes de un run.
3. **pandas 3.x rompe `dataset_generic.py:120`** porque rechaza `int`
   en columna `str`. Pinear `pandas>=2.0,<3.0` en el env.
4. **El `summary.csv` post-training puede tener `test_auc=∅` o `nan`**
   cuando una clase tiene < 2 ejemplos en val/test (sklearn requiere
   ≥ 2 clases en y_true). No confundir AUC vacío con AUC=0.
5. **Auditar la distribución por clase × split ANTES de reportar una task
   multiclase.** El join `splits_0.csv ⨯ dataset_<task>_label.csv` da la
   verdad. Clases con **1 muestra** en val/test no hacen `nan` pero sí
   producen un AUC one-vs-rest de puro ruido: el macro-AUC (`nanmean`) queda
   dominado por esos términos. Síntoma confirmado (baseline B=8,
   `microcalcificaciones_pth`, 21 may 2026): val_auc 0.69 < test_auc 0.81
   (inversión). **Regla**: para tasks multiclase desbalanceadas, reportar
   **balanced accuracy + matriz de confusión** desde el `split_0_results.pkl`,
   nunca el macro-AUC solo, y siempre con el `n` por clase visible.
