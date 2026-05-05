# Entregable 3 — Pipeline + formato de los `.csv`

**Deadline**: 6 mayo 2026.

## Tareas

1. Trazar control flow `main.py → core_utils.py`. Identificar dónde se
   cargan features CONCH, se construyen DataLoaders, se computan losses.
2. Documentar formato del `.csv` de **input** (columnas, encoding de
   etiquetas, manejo de splits) y de los `.csv` de **output** (logs,
   predicciones, métricas).
3. Identificar dónde se generan dinámicamente las pseudo-etiquetas en el
   forward pass y cómo se conectan al cálculo de la loss.

## Output esperado

- `pipeline_diagram.svg` — diagrama del pipeline completo, listo para
  copiar a la presentación.
- `csv_input_schema.md` — esquema columna por columna.
- `csv_output_schema.md` — qué genera el modelo y dónde lo escribe.
