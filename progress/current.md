# progress/current.md

> Estado vivo del sprint actual. Es un **snapshot** — se reemplaza al avanzar
> el sprint. Al cerrar el sprint, el resumen pasa a `history.md`.

---

## Sprint actual: B4 / Sprint 4

**Snapshot: 21 may 2026** (baseline B=8 completado; B=16 en curso).

### Estado por objetivo

- **Objetivo 1 — Baseline CLAM reproducible**: **COMPLETADO**.
  Job `4098` (B=8, `microcalcificaciones_pth`, split `minpatch16`) terminó
  COMPLETED. Resultados y análisis completos en
  `sprints/B4_sprint4/objetivo_1_baseline/resultados.md`.
  **Hallazgo central**: el régimen de evaluación de la task NO es confiable
  (ver abajo). Métricas: test_auc 0.81 (ruidoso), val_auc 0.69, test_acc 0.72,
  **balanced accuracy 0.31**.
- **Objetivo 2 — Ablation B=8 vs B=16**: **EN CURSO**.
  Job `4099` (B=16) RUNNING. Comportamiento preliminar idéntico a B=8
  (sobreajuste en época 6, val AUC plateau ~0.66). `summary.csv` al terminar.
- **Objetivo 3 — Módulo MIL alternativo (propuesta DSMIL)**: **EN INVESTIGACIÓN**.
  Scaffolding + investigación en la rama `feature/sprint4-obj3-mil-alternativo`.
  Eduardo subió 3 papers nuevos a `papers/` (ver inventario en `papers/README.md`).
  DSMIL **sujeto a confirmación** en la reunión.
- **Objetivo 4 — Heatmaps comparativos**: **PENDIENTE** (bloqueado por Obj 2).
  Viabilidad verificada (`objetivo_4_heatmaps/viabilidad_script.md`).

### Hallazgos críticos del baseline (21 may 2026)

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

### Jobs SLURM (snapshot)

| Job | Qué | Estado |
|---|---|---|
| `4098` | baseline B=8 `minpatch16` | COMPLETED |
| `4099` | ablation B=16 `minpatch16` | RUNNING |

Monitoreo en otra sesión. Esta sesión NO toca SLURM.

### Decisiones pendientes — reunión Sebastián + Eduardo

Tabla completa en `sprints/B4_sprint4/README.md` (decisiones 1-7). Sumar:
- **Reformular microcalcificaciones como 3 binarios** (multi-label) — ver
  `objetivo_1_baseline/resultados.md`.
- **Confirmar la composición de V4** (n=548 vs nuestro `_pth` 3072) — el 0.55
  de V4 NO es blanco de reproducción.
- **Qué significa `no_identificado`** (¿sin microcalcificación, o sin ubicar?).

### Trabajo humano pendiente (Ernesto)

- Presentación del Sprint 4 (`sprints/B4_sprint4/presentacion_contenido.md`).
- Revisar la investigación DSMIL + los 3 papers de Eduardo antes de la reunión.
- Agendar la reunión con Sebastián + Eduardo.
- `git push` de `main` y `feature` cuando haga sentido empujar todo junto.

### Ramas

- `main`: infraestructura + resultados del baseline (Obj 1, 2, scripts,
  preflight, split filtrado, docs, presentación).
- `feature/sprint4-obj3-mil-alternativo`: trabajo de Objetivo 3 (DSMIL).
  **Pendiente unificar con `main`** (sesión dedicada — ver prompt entregado).
