# progress/history.md

> Bitácora append-only de sprints cerrados. Al cerrar un sprint, el
> contenido de `current.md` se mueve acá y `current.md` se reinicia.

---

## Sprint 4 (B4) — CERRADO (1-jun-2026)

> Bitácora cronológica del sprint. Resumen final consolidado abajo
> ("Cierre B4"). El sprint B5 arranca con el deck B4 como base y mammoth
> como objetivo headline.

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

### Cierre B4 (1-jun-2026) — consolidación

- **Obj 1 baseline + Obj 2 ablación B**: el régimen de eval de las 8 clases es
  ruido (4 clases n=1); **B no es la palanca** (Δ ambiguo, balanced_acc bajó).
  El cuello es la **formulación**, no el hiperparámetro.
- **Reformulación 3 binarios** (carcinoma/cdis/tejido, `no_identificado`
  excluido): infra de Sebastián reproducida y validada; eval pasó de no-medible
  a confiable. Igualamos/mejoramos sus métricas oficiales.
- **Obj 3 + Obj 5 + ANEXO (DSMIL)**: cuadro CLAM×DSMIL cerrado **simétricamente**
  con MC-CV k=5. Veredicto: **la arquitectura del agregador NO es la palanca** a
  ninguna escala (fusionado = banda ambigua; binarias = NULL en 2/3 + regresión
  leve consistente en CDIS). El cuello sigue siendo **datos / contexto espacial /
  desbalance**. Hallazgo metodológico fuerte: el single-split engaña fuerte a
  n≈33 → MC-CV obligatorio + comparación PAIRED por reuso de splits.
- **Deck B4** presentado (1-jun). Base legacy: `papers/presentations/CLAM_Sprint_B4.pdf`.
- **Cambio de equipo**: **Eduardo renunció** (1-jun) → queda Ernesto + Sebastián.
  Heredó su trabajo de **mammoth** (sin commitear en `clam_testing`).
- **Obj 6 — mammoth (puente a B5)**: investigado + portado a `models_mammoth/`
  (subclase de CLAM_MB, 1ª capa → MoE) + driver `train_dsmil.py --model_type
  clam_mammoth` + slurm k=5 paired + test CPU + hipótesis (regla 9) + reviewer GO.
  **Snapshot** del trabajo de Eduardo preservado. Listo para correr en B5.
