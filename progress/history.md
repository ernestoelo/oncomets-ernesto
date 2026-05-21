# progress/history.md

> Bitácora append-only de sprints cerrados. Al cerrar un sprint, el
> contenido de `current.md` se mueve acá y `current.md` se reinicia.

---

## Sprint 4 (B4) — en curso

> Bitácora cronológica del sprint. Cuando B4 cierre, su resumen final
> consolida acá; mientras tanto se registran los hitos.

### 21 may 2026 — re-encolado del baseline tras el bug `topk`

- **Bug `topk`** en `inst_eval` (run 4096): slides de train con `<B` parches
  crashean `torch.topk`. Mitigado con split filtrado `minpatch16` +
  `scripts/preflight_minpatch.py` (preflight obligatorio en los `.slurm`).
- **Baseline B=8** re-encolado como job `4098` (RUNNING); **ablation B=16**
  como `4099` (PD, `dependency=afterok:4098`).
- **Limpieza de ramas**: c1-c4 (infraestructura compartida) movidos a `main`
  vía cherry-pick; c5 (pregunta de Obj 3) rehecho en `feature`; rename del
  dir de Obj 3 alineado en `main`.
- **Consolidación operativa**: preflight como patrón obligatorio, bug `topk`
  y reglas de git workflow documentados (`CLAUDE.md`, `docs/workarounds.md`).

### 21 may 2026 — resultados del baseline B=8 (job 4098)

- **Baseline B=8 COMPLETADO** (job `4098`, ~4h 11m). Métricas: test_auc 0.81,
  val_auc 0.69, test_acc 0.72, **balanced accuracy 0.31**. Detalle en
  `sprints/B4_sprint4/objetivo_1_baseline/resultados.md`.
- **Hallazgo central**: el régimen de evaluación de `microcalcificaciones_pth`
  NO es confiable — 4 de 8 clases tienen 1 muestra en val/test → macro-AUC
  dominado por ruido (inversión val < test). Métrica recomendada: balanced
  accuracy + matriz de confusión.
- **Hallazgo**: las 8 clases son un problema multi-label (3 tejidos) aplastado;
  propuesta para la reunión = reformular como 3 binarios.
- **B=16** (job `4099`) lanzado; mismo patrón de sobreajuste temprano.
- Eduardo aportó 3 papers a `papers/` para atacar el desbalance.
