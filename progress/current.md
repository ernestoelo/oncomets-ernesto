# progress/current.md

> Estado vivo del sprint actual. Es un **snapshot** — se reemplaza al avanzar
> el sprint. Al cerrar el sprint, el resumen pasa a `history.md`.

---

## Sprint actual: B5 / Sprint 5 — cierre de trimestre

**Abierto 1-jun-2026.** Sprint de la **recta final del trimestre**: Benjamín
(jefe) vuelve ~21-jun, a fin de mes se cierra el trimestre y **esta presentación
decide la continuidad de Ernesto** ([[sprint-cierre-trimestre-junio]]). Equipo =
**Ernesto + Sebastián** (Eduardo renunció el 1-jun). Consigna de Benjamín:
avanzar **más rápido** y **lucirse**. Base del deck: B4 cerrado
(`papers/presentations/CLAM_Sprint_B4.pdf`, legacy local).

### Plan del sprint

Detalle y argumentos en `sprints/B5_sprint5/README.md`. Objetivos priorizados
según los pedidos de Benjamín (1-jun):

| # | Objetivo | Estado |
|---|---|---|
| 1 | **mammoth k=5 paired** sobre las 3 binarias (correr + analizar) | port LISTO (B4 Obj 6), falta `sbatch` |
| 2 | **Magnificación**: investigar (papers) ANTES de implementar | pendiente |
| 3 | **k=5 folds** en más tasks débiles (no single-split) | pendiente |
| 4 | **Parches/slides útiles**: selección de los que aportan al train | pendiente |
| 5 | **Pregunta CAP**: ¿1 de las 3 binarias positiva = cáncer c/microcalc? | pendiente (research clínico) |
| 6 | **PCGrad** (gradient surgery, heredado de Eduardo): eje separado | pendiente |

> DSMIL: "entenderlo mejor", menor prioridad (cerrado para microcalc, ver B4).

### Estado inmediato

- **mammoth (Obj 1 de B5)**: `models_mammoth/CLAM_MB_Mammoth` + driver
  `train_dsmil.py --model_type clam_mammoth` + `scripts/run_obj6_mammoth_binarias_kfold.slurm`
  + `tests/test_mammoth_cpu.py` (pasa) + hipótesis en
  `sprints/B4_sprint4/objetivo_6_mammoth/README.md`. Reviewer GO. **NO lanzado a
  GPU** (espera OK de Ernesto). Splits k=5 ya existen en `data/splits_kfold/`.
- **Pendiente técnico antes de citar mammoth**: vendorizar `mammoth-moe` bajo
  `clam_testing2` (hoy editable desde `clam_testing`, fuera de containment).
- Jobs SLURM activos: **ninguno**.

### Reglas que gobiernan el sprint (de CLAUDE.md)

- Argumento antes de código (regla 9) + reviewer antes de commitear modelo/training.
- Comparación PAIRED por reuso de splits ([[patron-paired-comparison-reuso-splits]]).
- Entregables: notas concisas, **sin números de job**, baselines como "Environ
  vX" ([[presentacion-convenciones-benjamin]]).
- GPU solo vía `sbatch`; cortesía single-GPU; preflight obligatorio.
