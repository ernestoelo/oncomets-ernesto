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
| 1 | **mammoth k=5 paired** sobre las 3 binarias (correr + analizar) | **COMPLETADO** (job 4229, analizado): mammoth NO es palanca en microcalc (cuello=datos). `objetivo_1_mammoth_run/resultados.md` |
| 1b | **mammoth en patrón arquitectónico (4 binarias) + invasión (3-clase)** k=5 | **lanzado job 4241 y CRASHEÓ** (branch-switch borró los CSVs de input); re-lanzar desde `main`. `objetivo_2_mammoth_patron_invasion/` |
| 2 | **Magnificación**: investigar (papers) ANTES de implementar | pendiente |
| 3 | **k=5 folds** en más tasks débiles (no single-split) | pendiente |
| 4 | **Parches/slides útiles**: selección de los que aportan al train | pendiente |
| 5 | **Pregunta CAP**: ¿1 de las 3 binarias positiva = cáncer c/microcalc? | pendiente (research clínico) |
| 6 | **PCGrad** (gradient surgery, heredado de Eduardo): eje separado | pendiente |

> DSMIL: "entenderlo mejor", menor prioridad (cerrado para microcalc, ver B4).

### Estado inmediato (act. 3-jun, auditoría de cierre)

- **mammoth microcalc (Obj 1 de B5) — COMPLETADO Y ANALIZADO**: job **4229**
  (3 binarias × k=5 × 2 brazos, ~9h40m). **Veredicto**: mammoth NO es palanca
  consistente en microcalc (tejido +0.049, cdis −0.086, carcinoma nulo; std >
  |media| → banda ambigua H0; cuello = datos). Brazo CLAM reproduce Fase 0 al 3er
  decimal. Detalle: `sprints/B5_sprint5/objetivo_1_mammoth_run/resultados.md`.
- **mammoth patrón+invasión (`objetivo_2_mammoth_patron_invasion/`) — LANZADO Y
  CRASHEÓ**: job **4241** (GROUP=patron, 4 binarias × k=5 × 2 brazos = 40 runs).
  Completó 1 run (cribiforme f0, CLAM) y murió: durante el job, un `git checkout`
  a la rama `chore` en el working-tree COMPARTIDO borró `data/csv_new_tasks/*.csv`
  → `FileNotFoundError` en fold 1 ([[working-tree-compartido-job-en-curso]],
  workaround H de CLAUDE.md). **Re-lanzar desde `main`** (ya tiene CSVs+splits tras
  el merge de cierre) **sin cambiar de rama durante el job**. Invasión (3-clase, ~25h)
  NO lanzada (2ª ola deliberada, con OK).
  > Nota de numeración: la tabla del plan numera por pedido de Benjamín (1=mammoth
  > microcalc, 2=magnificación...). El dir `objetivo_2_mammoth_patron_invasion` es la
  > **continuación del hilo mammoth**, NO el "Objetivo 2 = magnificación" del plan.
- **Vendorizado HECHO**: `mammoth-moe` en `clam_testing2/MAMMOTH` (pin `fe36d4e`),
  `pip install -e` reapuntado → `import mammoth` resuelve dentro de containment.
- **GPU**: job ajeno `sgaete` (feature extraction, job 4242) corría al cierre — cortesía.

### Reglas que gobiernan el sprint (de CLAUDE.md)

- Argumento antes de código (regla 9) + reviewer antes de commitear modelo/training.
- Comparación PAIRED por reuso de splits ([[patron-paired-comparison-reuso-splits]]).
- Entregables: notas concisas, **sin números de job**, baselines como "Environ
  vX" ([[presentacion-convenciones-benjamin]]).
- GPU solo vía `sbatch`; cortesía single-GPU; preflight obligatorio.
