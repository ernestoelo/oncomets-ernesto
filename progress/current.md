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
| 1 | **mammoth k=5 paired** sobre las 3 binarias (correr + analizar) | **CORRIENDO** (job 4229, ambos brazos, lanzado 2-jun 00:06); falta analizar |
| 2 | **Magnificación**: investigar (papers) ANTES de implementar | pendiente |
| 3 | **k=5 folds** en más tasks débiles (no single-split) | pendiente |
| 4 | **Parches/slides útiles**: selección de los que aportan al train | pendiente |
| 5 | **Pregunta CAP**: ¿1 de las 3 binarias positiva = cáncer c/microcalc? | pendiente (research clínico) |
| 6 | **PCGrad** (gradient surgery, heredado de Eduardo): eje separado | pendiente |

> DSMIL: "entenderlo mejor", menor prioridad (cerrado para microcalc, ver B4).

### Estado inmediato

- **mammoth (Obj 1 de B5) — LANZADO**: job **4229** (`sbatch
  scripts/run_obj6_mammoth_binarias_kfold.slurm`, ambos brazos `clam
  clam_mammoth`, 3 binarias × k=5 = 30 corridas, ~15h, lanzado 2-jun 00:06 con
  OK de Ernesto). Gates pasados: verify_kfold + test CPU + preflight ×5/tarea.
  Resultados → `results/obj6_mammoth_binarias_<tejido>/`. Analizar Δ pareado por
  fold (balanced_acc) cuando termine; escribir
  `sprints/B5_sprint5/objetivo_1_mammoth_run/resultados.md`.
- **Vendorizado HECHO**: `mammoth-moe` copiado a `clam_testing2/MAMMOTH` (pin
  `fe36d4e`) + `pip install -e` reapuntado → `import mammoth` resuelve dentro de
  containment. Resultado ya citable. (El env compartido `clam_latest` quedó
  apuntando al editable nuevo.)
- Monitoreo: `tail -f logs/eg_mammoth_bin_kfold_4229.out` · `squeue -j 4229`.

### Reglas que gobiernan el sprint (de CLAUDE.md)

- Argumento antes de código (regla 9) + reviewer antes de commitear modelo/training.
- Comparación PAIRED por reuso de splits ([[patron-paired-comparison-reuso-splits]]).
- Entregables: notas concisas, **sin números de job**, baselines como "Environ
  vX" ([[presentacion-convenciones-benjamin]]).
- GPU solo vía `sbatch`; cortesía single-GPU; preflight obligatorio.
