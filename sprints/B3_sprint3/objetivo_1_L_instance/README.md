# Entregable 1 — Estudio profundo de L_instance

**Deadline**: 6 mayo 2026.

## Tareas

1. Re-leer Sección 2.2 del paper CLAM con foco en SmoothTop1SVM y su rol
   como mecanismo supervisado por pseudo-etiquetas.
2. Mapear cada término de la loss a su implementación exacta en
   `model_clam.py:107–136` y `core_utils.py:243–251`.
3. Identificar y caracterizar hiperparámetros que regulan la rigurosidad de
   las pseudo-etiquetas (top-B/bottom-B, peso instance vs slide, parámetro
   de suavizado).

## Output esperado

- `notas_teoria.md` — derivación + conexión código↔paper.
- `diagrama.svg` — `attention → top-B/bottom-B → pseudo-labels → SmoothTop1SVM → L_instance`.
- `tabla_hiperparametros.md` — tabla con cada hiperparámetro y efecto cualitativo.
