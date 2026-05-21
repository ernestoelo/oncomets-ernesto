# progress/current.md

> Estado vivo del sprint actual. Es un **snapshot** — se reemplaza al avanzar
> el sprint. Al cerrar el sprint, el resumen pasa a `history.md`.

---

## Sprint actual: B4 / Sprint 4

**Snapshot: 21 may 2026** (re-encolado del baseline tras el bug topk).

### Estado por objetivo

- **Objetivo 1 — Baseline CLAM reproducible**: **EN CURSO**.
  Job SLURM `4098` (B=8, tarea `microcalcificaciones_pth`, split filtrado
  `minpatch16`) RUNNING. El preflight pasó OK. Reemplaza al run 4096, que
  falló por el bug `topk`. Resultados →
  `results/baseline_microcalc_pth_B8_minpatch16/`.
- **Objetivo 2 — Ablation B=8 vs B=16**: **ENCOLADO**.
  Job `4099` (B=16) en `PD` con `--dependency=afterok:4098` — arranca solo
  si el baseline completa COMPLETED.
- **Objetivo 3 — Módulo MIL alternativo (propuesta DSMIL)**: **EN INVESTIGACIÓN**.
  Scaffolding (`dsmil_wrapper.py`, `train_obj3.py`) + investigación (paper,
  mapeo de código oficial, comparación CLAM/DSMIL, riesgos y preguntas) en la
  rama `feature/sprint4-obj3-mil-alternativo`. DSMIL **sujeto a confirmación**
  en la reunión.
- **Objetivo 4 — Heatmaps comparativos**: **PENDIENTE** (bloqueado por Obj 1/2).
  Viabilidad verificada (`sprints/B4_sprint4/objetivo_4_heatmaps/viabilidad_script.md`):
  `create_heatmaps.py` requiere GPU + los WSI originales. Se ejecuta tras
  baseline + B=16.

### Jobs SLURM activos (snapshot)

| Job | Qué | Estado |
|---|---|---|
| `4098` | baseline B=8 `minpatch16` | RUNNING |
| `4099` | ablation B=16 `minpatch16` | PD (`Dependency` afterok:4098) |

Monitoreo en otra sesión. Esta sesión NO toca SLURM.

### Decisiones pendientes — reunión Sebastián + Eduardo

Tabla completa en `sprints/B4_sprint4/README.md` (decisiones 1-7). Las más
bloqueantes: composición del dataset / splits canónicos, confirmación del
módulo MIL (DSMIL u otro), lista de 4 tareas prioritarias, `embed_dim`.
Pregunta operativa nueva: slides con `<B` parches tras CONCH — ver
`docs/workarounds.md` §3 y la sección C de
`sprints/B4_sprint4/objetivo_3_modulo_mil_alternativo/investigacion/04_riesgos_y_preguntas_reunion.md`.

### Trabajo humano pendiente (Ernesto)

- Revisar la investigación DSMIL en la rama `feature` antes de la reunión.
- Agendar la reunión con Sebastián + Eduardo.
- `git push` de `main` y `feature` cuando 4098/4099 terminen y haga sentido
  empujar todo junto con los resultados.
- Tras la reunión: confirmar el módulo MIL y actualizar `objetivo_3`.

### Ramas

- `main`: infraestructura compartida del Sprint 4 (baseline, ablation,
  scripts, preflight, split filtrado, docs operativas).
- `feature/sprint4-obj3-mil-alternativo`: trabajo de Objetivo 3 (DSMIL).
