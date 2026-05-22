# progress/current.md

> Estado vivo del sprint actual. Es un **snapshot** — se reemplaza al avanzar
> el sprint. Al cerrar el sprint, el resumen pasa a `history.md`.

---

## Sprint actual: B4 / Sprint 4

**Snapshot: 21 may 2026** (Objetivos 1 y 2 completados; investigación del
Objetivo 3 unificada a `main`; run preliminar de la reformulación en cola).

### Estado por objetivo

- **Objetivo 1 — Baseline CLAM reproducible**: **COMPLETADO**.
  Job `4098` (B=8, `microcalcificaciones_pth`, split `minpatch16`) terminó
  COMPLETED. Resultados y análisis completos en
  `sprints/B4_sprint4/objetivo_1_baseline/resultados.md`.
  **Hallazgo central**: el régimen de evaluación de la task NO es confiable
  (ver abajo). Métricas: test_auc 0.81 (ruidoso), val_auc 0.69, test_acc 0.72,
  **balanced accuracy 0.31**.
- **Objetivo 2 — Ablation B=8 vs B=16**: **COMPLETADO**.
  Job `4099` (B=16) terminó COMPLETED. **Veredicto: hipótesis NO confirmada.**
  Δtest_auc +0.009 (umbral predefinido era +0.03 → banda ambigua); balanced
  accuracy *bajó* 0.31→0.24; train_clustering_loss *subió* 0.0089→0.0126
  (contradice el mecanismo de la hipótesis). **Conclusión de fondo**: `B` es
  un hiperparámetro — ajustarlo no mueve la aguja porque el cuello de botella
  es la **FORMULACIÓN** de la tarea, no los hiperparámetros. La ablación
  negativa es la evidencia que justifica la reformulación. Detalle:
  `sprints/B4_sprint4/objetivo_2_ablation_B/resultados.md`.
- **Objetivo 3 — Módulo MIL alternativo (propuesta DSMIL)**: **INVESTIGACIÓN
  COMPLETA, unificada a `main`**. Docs `00`–`06` en
  `objetivo_3_modulo_mil_alternativo/investigacion/`: DSMIL + evaluación de
  los 3 papers de Eduardo (`05`) y de HMIL vía búsqueda web (`06`). DSMIL es
  un eje **ortogonal** al desbalance; **sujeto a confirmación** en la reunión.
- **Objetivo 4 — Heatmaps comparativos**: **PENDIENTE** (Obj 2 ya no lo
  bloquea). Viabilidad verificada (`objetivo_4_heatmaps/viabilidad_script.md`).

### Hallazgos críticos (21 may 2026)

1. **Régimen de evaluación roto.** `microcalcificaciones_pth` tiene 8 clases;
   4 de ellas tienen **1 sola slide** en val y en test. El macro-AUC es un
   promedio dominado por ruido → la inversión val(0.69) < test(0.81) lo
   confirma. **Usar balanced accuracy + matriz de confusión, no el AUC solo.**
2. **El modelo colapsa a la clase mayoritaria.** Predice `no_identificado`
   para el 74.5 % de las slides de test; `test_acc` 0.72 está por *debajo*
   del baseline trivial (0.89).
3. **Estructura multi-label.** Las 8 clases son combinaciones de 3 tejidos +
   `no_identificado` → es un problema multi-etiqueta aplastado. Propuesta:
   reformular como 3 tareas binarias. Ver `objetivo_1_baseline/resultados.md`.
4. **El dataset grande no ayuda al desbalance.** 3072 vs 548 de V4: la
   expansión fue casi toda `no_identificado`; las clases raras siguen con
   6–15 slides. Más datos de la clase mayoritaria no enseña las minoritarias.
5. **B no es la palanca (ablación Obj 2).** Doblar B (8→16) deja todo igual o
   peor — confirma empíricamente que el problema está en la formulación.

### Jobs SLURM (snapshot)

| Job | Qué | Estado |
|---|---|---|
| `4098` | baseline B=8 `minpatch16` | COMPLETED |
| `4099` | ablation B=16 `minpatch16` | COMPLETED |
| `4109` | reformulación: 3 tareas binarias (PRELIMINAR) | PENDING — en cola detrás del job `4108` (ajeno, cuenta compartida) |

### Reformulación multi-label — run PRELIMINAR EN CURSO

Job `4109` lanzado el 21 may 2026: las **3 tareas binarias** de
microcalcificaciones (carcinoma invasivo / CDIS / tejido no neoplásico),
secuenciales en un mismo job, CLAM_MB, B=8, `--max_epochs 30`, sobre los
CSVs/splits binarios **existentes** del equipo (333 slides,
`no_identificado` excluido). Quedó **PENDING** en cola detrás del job
ajeno `4108`; arranca cuando el GPU se libere. Las 3 tareas juntas toman
~1 h de cómputo.

- **Resultados** → `results/reformulacion_3binarios_<tejido>/`.
- **PRELIMINAR**: contingente a que la reunión confirme la reformulación y
  ratifique la interpretación de `no_identificado`.
- **Análisis pendiente (próxima sesión)**: balanced accuracy + matriz de
  confusión por tarea, ancladas contra el piso trivial 0.5 (un binario se
  ancla solo; el "antes" es el baseline de 8 clases, job `4098`). No hace
  falta un baseline binario.
- `.slurm` usado: `sprints/B4_sprint4/reformulacion_multilabel/train_microcalc_3binarios.slurm`.

### Decisiones pendientes — reunión Sebastián + Eduardo

Tabla completa en `sprints/B4_sprint4/README.md` (decisiones 1-7). Sumar:
- **Reformular microcalcificaciones como 3 binarios** (multi-label) — ver
  `objetivo_1_baseline/resultados.md` y `reformulacion_multilabel/`.
- **Confirmar la composición de V4** (n=548 vs nuestro `_pth` 3072) — el 0.55
  de V4 NO es blanco de reproducción.
- **Qué significa `no_identificado`** (¿sin microcalcificación, o sin ubicar?).
- Preguntas de los papers / DSMIL: ver
  `objetivo_3_modulo_mil_alternativo/investigacion/04_…` (§C) y `05_`/`06_`.

### Trabajo humano pendiente (Ernesto)

- Presentación del Sprint 4 (`sprints/B4_sprint4/presentacion_contenido.md`).
- Revisar la investigación DSMIL + los 3 papers de Eduardo + HMIL (`06_`)
  antes de la reunión.
- Agendar la reunión con Sebastián + Eduardo.

### Ramas

- `main`: todo el Sprint 4 — Objetivos 1, 2, 3 (investigación) unificados,
  scripts, preflight, splits, presentación, docs.
- `feature/sprint4-obj3-mil-alternativo`: **ya unificada a `main`** (merge
  `43d2ae4`).
- `feature/sprint4-reformulacion-multilabel`: **ya unificada a `main`**
  (merge `c4982ed`).
