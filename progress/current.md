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
| 1b | **mammoth en patrón arquitectónico (4 binarias) + invasión (3-clase)** k=5 | **PATRÓN COMPLETADO** (job 4243, 40 runs, cerró 4-jun 01:33): mammoth NO es palanca (lean+ leve solo en cribiforme balanceada; nulo en solido/micropapilar/papilar). `objetivo_2_mammoth_patron_invasion/resultados.md`. **Invasión 3-clase = 2ª ola, NO lanzada.** |
| 2 | **Magnificación**: investigar (papers) ANTES de implementar | pendiente |
| 3 | **k=5 folds** en más tasks débiles (no single-split) | pendiente |
| 4 | **Parches/slides útiles**: selección de los que aportan al train | pendiente |
| 5 | **Pregunta CAP**: ¿1 de las 3 binarias positiva = cáncer c/microcalc? | pendiente (research clínico) |
| 6 | **PCGrad** (gradient surgery, heredado de Eduardo): eje separado | pendiente |

> DSMIL: "entenderlo mejor", menor prioridad (cerrado para microcalc, ver B4).

### Estado inmediato (act. 4-jun, patrón cerrado)

- **mammoth microcalc (Obj 1 de B5) — COMPLETADO Y ANALIZADO**: job **4229**
  (3 binarias × k=5 × 2 brazos, ~9h40m). **Veredicto**: mammoth NO es palanca
  consistente en microcalc (tejido +0.049, cdis −0.086, carcinoma nulo; std >
  |media| → banda ambigua H0; cuello = datos). Brazo CLAM reproduce Fase 0 al 3er
  decimal. Detalle: `sprints/B5_sprint5/objetivo_1_mammoth_run/resultados.md`.
- **mammoth patrón (Obj 1b, `objetivo_2_mammoth_patron_invasion/`) — COMPLETADO Y
  ANALIZADO**: job **4243** (4 binarias × k=5 × 2 brazos = 40 runs), lanzado 3-jun
  desde `main` sin cambiar de rama → **cerró limpio 4-jun 01:33** (sin el crash del
  4241). **Veredicto**: mammoth NO es palanca en patrón tampoco — lean+ leve solo en
  **cribiforme** (Δbal +0.044±0.048, 4+/1−, la única binaria balanceada ~1:1); **nulo**
  en solido (−0.014, desbalance 3:1) y en micropapilar/papilar (régimen ciego, 3 pos/test
  → pooled: ambos brazos casi no detectan, TP global 4/15 y 2/15). **Hallazgo crítico**:
  cruzando Obj1+Obj2 (7 binarias), el lean+ de mammoth aparece SOLO en las 2 tareas más
  balanceadas (tejido ~58%, cribiforme ~49%) → el resultado lo gobierna el **régimen de
  datos**, no el agregador/patch-embed. Refuerza cuello = datos/desbalance/contexto
  espacial. Detalle: `objetivo_2_mammoth_patron_invasion/resultados.md`; README
  consolidado `results/README_experimentos_mammoth_environ.md` §4.b.
  - El intento previo (job **4241**, 2-jun) completó 1/40 y murió porque un `git checkout`
    en el working-tree COMPARTIDO borró `data/csv_new_tasks/` → `FileNotFoundError` en fold
    1 ([[working-tree-compartido-job-en-curso]], workaround H). Parcial segregado en
    `results/failed_runs/4241_*` (NO usar).
  - **Invasión linfática 3-clase (GROUP=invasion, ~25h) NO lanzada** — 2ª ola deliberada,
    con OK + cortesía GPU. Es la mejor chance de señal estable (n=2814 vs ~330).
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
