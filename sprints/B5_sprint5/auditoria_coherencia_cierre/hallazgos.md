# Auditoría de coherencia — cierre incremental B5 (post Obj1 + setup Obj2) — Hallazgos

> Generado: 2026-06-03. Branch: `chore/audit-coherencia-b5-cierre`.
> Misión (prompt de Ernesto + `handoff_B5_20260602_224800.md`): tras consolidar en
> `main` (rename skill `knowledge-audit` + resultados Obj1 mammoth microcalc job 4229
> + setup Obj2 patrón/invasión), dejar la base de conocimiento coherente. Sesión
> **documental** (no GPU, no modelo).
>
> Continúa la auditoría B5 previa (`../auditoria_coherencia/hallazgos.md`, findings
> A–F ya aplicados y mergeados en `992be31`). Esta pasada audita lo que cambió
> DESPUÉS: el job 4229 terminó y se analizó, el job 4241 (Obj2) se lanzó y **crasheó**.
>
> Método: cross-lectura CLAUDE.md ↔ memorias ↔ skills ↔ agentes ↔ `progress/current.md`
> ↔ READMEs de objetivo, + revisión del estado real de los jobs (`logs/`, `squeue`).

## Resumen ejecutivo

| # | Hallazgo | Severidad | Acción |
|---|---|---|---|
| H1 | Memoria `mammoth-investigacion-integracion` (L56 "RUNNING", L63 "análisis pendiente") + `MEMORY.md:12` ("análisis pendiente") + `eval-reporte-auc-y-umbrales-obj6.md:38` — el job 4229 **terminó y se analizó** (veredicto: mammoth NO es palanca en microcalc) | stale | **FIX** (memorias + índice) |
| H2 | `progress/current.md` — Obj 1 "CORRIENDO / falta analizar" (ya hecho) y **no menciona** Obj 2 ni el crash del job 4241 | stale | **FIX** (estado vivo) |
| H3 | **Job 4241 (Obj2) CRASHEÓ** ~1 min después del handoff: un `git checkout` a la rama `chore` en el working-tree COMPARTIDO borró `data/csv_new_tasks/*.csv` de input mientras el job corría (fold 1 → `FileNotFoundError`). Lección durable no capturada en ningún lado. `objetivo_2/README.md §Estado` es previo al lanzamiento | error / operacional | **FIX** (workaround nuevo en CLAUDE.md + memoria nueva + README §Estado) |
| H4 | Rename skill `coherence-audit` → `knowledge-audit`: ¿quedan referencias colgadas? | verificación | **sin acción** (grep: 0 refs colgadas; las del worked-example son históricas) |
| H5 | "Obj 6" (B4) / "Obj 1" (B5) / `results/obj6_mammoth_binarias_*` / `run_obj6_*.slurm` — ¿contradicción de numeración? | naming / bajo | **sin acción** (linaje, no contradicción; los cross-refs resuelven — patrón "identificador histórico" como "k-fold = MC-CV") |
| H6 | CAP (College of American Pathologists) = fuente oficial de las formulaciones de clase (patrón→4 binarias, invasión 3-clase). Durable, citado en Obj2 README, sin memoria propia | captura de conocimiento | **FIX** (memoria nueva `cap-fuente-clases-tareas`, handoff §10.3) |

> **Fuera de alcance de esta pasada** (recomendados, NO aplicados): los aprendizajes
> de código del handoff §10 que van a skills vía `/architect` — gotcha de métricas
> multiclase en `train_dsmil.py` (§10.1), receta de splits de tareas nuevas (§10.2),
> slurm parametrizable por GROUP (§10.4). Razón: el experimento Obj2 que los motivó
> **no completó** (crasheó); conviene finalizar esas lecciones reusables cuando el
> re-run confirme el flujo. Se dejan flagged en mi reporte a Ernesto.

---

## H1 — Stale: el job 4229 (mammoth microcalc) figura "corriendo / sin analizar"

- **Fuentes stale**:
  - `mammoth-investigacion-integracion.md:56` — *"LANZADO 2-jun (job 4229...) — RUNNING."*
  - `mammoth-investigacion-integracion.md:63-65` — *"Análisis del 4229 ... queda pendiente cuando termine."*
  - `MEMORY.md:12` (línea índice) — *"...; análisis pendiente."*
  - `eval-reporte-auc-y-umbrales-obj6.md:38` — *"Para 4229: analizar así cuando termine"* (nota forward).
- **Realidad (fuente de verdad)**: `sprints/B5_sprint5/objetivo_1_mammoth_run/resultados.md` —
  job 4229 **completó** (~9h40m) y se analizó. **Veredicto**: *mammoth no es palanca
  consistente para microcalcificaciones a esta escala* (tejido +0.049, cdis −0.086,
  carcinoma nulo; std > |media| en los 3 → banda ambigua H0; cuello = datos). El port
  reproduce Fase 0 al 3er decimal (sanity OK).
- **Fix**: actualizar la memoria (sección PORT → "RUNNING" a "COMPLETADO + analizado",
  veredicto + puntero a resultados.md; Obj 2 lanzado y crasheó), la línea de `MEMORY.md`,
  y la nota forward de `eval-reporte-auc-y-umbrales-obj6.md` (marcar "aplicado en Obj1").
  Dónde vive: la memoria (fact atómico de proyecto); el veredicto detallado en resultados.md.

## H2 — Stale: `progress/current.md` no refleja el estado real

- `progress/current.md:24` (tabla) — Obj 1 *"CORRIENDO (job 4229...); falta analizar"*.
- `progress/current.md:35-41` — *"mammoth Obj 1 LANZADO ... Analizar ... cuando termine;
  escribir resultados.md"*.
- **Realidad**: Obj 1 analizado (resultados.md escrito); **Obj 2** (mammoth en patrón
  arquitectónico 4 binarias + invasión 3-clase) **se montó y se lanzó** (job 4241) y
  **crasheó** (ver H3). El doc no menciona Obj 2 ni el crash.
- El propio doc declara ser *"un snapshot — se reemplaza al avanzar el sprint"* →
  actualizarlo es su uso previsto, no reescritura de historia.
- **Fix**: actualizar tabla (Obj 1 = COMPLETADO con veredicto) + "Estado inmediato"
  (agregar Obj 2: lanzado job 4241, CRASHEÓ por branch-switch, pendiente re-run desde
  `main`). Nota: la **tabla del plan** numera por pedido de Benjamín (1=mammoth microcalc,
  2=magnificación...); el directorio `objetivo_2_mammoth_patron_invasion` es la
  **continuación del hilo mammoth**, no el "Objetivo 2 = magnificación" del plan — se
  aclara en una línea para que no se lea como contradicción (ver H5).

## H3 — Error/operacional: el job 4241 crasheó por branch-switch en working-tree compartido

- **Qué pasó** (evidencia en `logs/eg_mammoth_patinv_4241.{out,err}`, timestamp 22:49):
  - 22:30 sbatch job 4241 (GROUP=patron, 4 binarias × 2 brazos × k=5 = 40 runs). El
    working-tree estaba en la rama `feature/...` → `data/csv_new_tasks/*.csv` presentes.
  - Fold 0 de `cdis_patron_cribiforme_pth` (brazo `clam`) **completó** OK (`test_metrics.json`
    escrito; `[TEST FINAL] balanced_acc=0.629`).
  - ~22:48 (handoff): el working-tree se cambió a `chore/rename-skill-knowledge-audit`
    para commitear el rename. Esa rama **NO tiene** `data/csv_new_tasks/`.
  - 22:49 el loop del slurm arrancó el siguiente `python train_dsmil.py` (fold 1), que
    lee el CSV en runtime → `FileNotFoundError: .../data/csv_new_tasks/dataset_carcinoma_ductal_in_situ_patrones_arquitectonicos_cribiforme_label.csv` → job muerto.
  - **Resultado**: 1 de 40 runs completados; Obj 2 sin resultados.
- **Causa raíz (lección durable)**: el `.slurm` invoca `python` **por cada run** dentro
  de un loop; cada invocación **relee** sus inputs/código del working-tree **vivo y
  COMPARTIDO** (`sdonoso`). Cualquier `git checkout` / branch-switch / edición de
  archivos versionados **mientras un job corre** le cambia el piso al job → crash o,
  peor, resultados con código mezclado (silencioso). CLAUDE.md ya avisa "verificá la
  rama antes de commitear" pero **solo en el contexto de commits**, no del riesgo de
  mover el árbol con un job en curso.
- **El handoff lo dio por "RUNNING, ETA 13h"** — premisa stale; el job ya estaba muerto
  cuando se escribió ([[surface-premise-discrepancies]]).
- **Fix**:
  1. **CLAUDE.md** — workaround nuevo **H** ("No mover el working-tree compartido con un
     job en curso"): regla aditiva, concisa, con el fix (congelar el árbol; o commitear
     los inputs del job a la rama que queda checked-out antes del sbatch).
  2. **Memoria nueva** `working-tree-compartido-job-en-curso` (type feedback/operacional),
     linkeada con [[git-main-shared-pushes]].
  3. **`objetivo_2/README.md §Estado`**: marcar sbatch como *lanzado (job 4241) y crasheado
     por branch-switch; re-lanzar desde `main`* (ahora `main` tiene los CSVs/splits → la
     causa raíz queda neutralizada al correr desde main sin switches).
- **Sinergia con el merge de esta sesión**: al consolidar el `feature/...` en `main`, los
  `data/csv_new_tasks/` y `data/splits_kfold/` quedan en `main`. Re-lanzar Obj2 desde
  `main` (sin cambiar de rama durante el job) elimina la causa raíz del crash.

## H4 — Verificación: rename skill `coherence-audit` → `knowledge-audit` (sin acción)

- `grep -rn coherence-audit` en `.md` del repo y en memorias → **0 referencias colgadas**.
  Las que matchean (`knowledge-audit/SKILL.md` worked-example, `../auditoria_coherencia/`)
  son **históricas correctas** (el branch B5 previo SÍ se llamó así). CLAUDE.md ya lista
  `@knowledge-audit` con la nota "(antes `@coherence-audit`; renombrada 2-jun-2026)".
- **Sin acción.**

## H5 — Naming "Obj 6"/"Obj 1"/`obj6_*` (sin acción, documentado)

- El trabajo de mammoth nació como **B4 Obj 6** (`sprints/B4_sprint4/objetivo_6_mammoth/`,
  donde vive la hipótesis pre-registrada + ADDENDUM) y continuó como **B5 Obj 1**
  (`sprints/B5_sprint5/objetivo_1_mammoth_run/`, la ejecución k=5). Los artefactos
  (`results/obj6_mammoth_binarias_*`, `run_obj6_*.slurm`) conservan el prefijo `obj6_`.
- **No es contradicción, es linaje**: `objetivo_1_mammoth_run/resultados.md:7` apunta
  correctamente a `objetivo_6_mammoth/README.md` para la hipótesis. Renombrar los dirs
  de results/slurm rompería los cross-refs de trazabilidad → mismo criterio que el
  "k-fold = MC-CV (identificador histórico, NO se renombra)" del Hallazgo 11.
- **Sin acción** (más allá de la línea aclaratoria en `progress/current.md`, ver H2).

## H6 — Captura: CAP es la fuente oficial de las formulaciones de clase

- El `objetivo_2/README.md` ancla las clases (patrón arquitectónico → 4 binarias "select
  all that apply"; invasión linfovascular → 3 clases) en los **protocolos CAP**
  (`papers/Breast.Invasive.Bx_*.pdf`). Es la misma jugada que microcalc 8→3 de Sebastián.
- Durable y transversal (grado nuclear, necrosis, etc. también son CAP), pero **sin
  memoria propia** → se pierde como conocimiento descubrible.
- **Fix**: memoria nueva `cap-fuente-clases-tareas` (type project), linkeada con
  [[microcalc-dataset-decision]] (patrón "Sebastián reformula multi-label en binarias").

---

## Plan de fixes (orden de aplicación)

1. **H1** — memoria `mammoth-investigacion-integracion` + `MEMORY.md:12` + nota en `eval-reporte-auc-y-umbrales-obj6`.
2. **H2** — `progress/current.md` (tabla + estado inmediato + línea aclaratoria de numeración).
3. **H3** — CLAUDE.md workaround H + memoria `working-tree-compartido-job-en-curso` + `objetivo_2/README.md §Estado`.
4. **H6** — memoria `cap-fuente-clases-tareas` + línea en `MEMORY.md`.

Commits granulares en `chore/audit-coherencia-b5-cierre` (`docs(audit-b5-cierre): ...`),
identidad local (`ernesto.gamero@sansano.usm.cl`), rama confirmada antes de cada commit.
**Push y merge a `main` autorizados explícitamente por Ernesto** en el prompt de esta sesión.
