# Job 4241 — Obj2 patrón, CRASH por branch-switch (NO es resultado válido)

> Segregado acá (patrón `failed_runs/`) para no contaminar `results/obj2_mammoth/`.
> **No usar para análisis.** El run válido es el re-lanzamiento (job 4243, desde `main`).

**Qué pasó (2-jun-2026 ~22:30→22:49):** el job 4241 (GROUP=patron) arrancó con el
working-tree en la rama `feature/...` (CSVs presentes), completó 1 run
(`cribiforme f0`, brazo CLAM) y murió en `fold 1` con `FileNotFoundError`: durante
el job, un `git checkout` a otra rama en el **working-tree COMPARTIDO** borró
`data/csv_new_tasks/*.csv`, y el `.slurm` relee el CSV en cada invocación de python.

**Contenido:** `..._f0_20260602_2230_s1/` (run completo, pero config/seed-idéntico a
lo que regenera el 4243 → sin valor único) + `..._f1_20260602_2230_s1/` (vacío, murió
al cargar el dataset).

**Trazas y lección durable:**
- Post-mortem: `logs/eg_mammoth_patinv_4241.{out,err}`.
- Regla: CLAUDE.md **Workaround H** ("No mover el working-tree con un job en curso") +
  memoria `working-tree-compartido-job-en-curso`.
