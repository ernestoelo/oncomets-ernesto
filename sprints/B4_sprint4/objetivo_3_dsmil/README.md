# Objetivo 3 — Módulo MIL alternativo (propuesta: DSMIL)

> Sprint B4. **Implementación con argumento arquitectónico explícito**
> (regla "Argumento antes de código"). Wrapper-only sobre el codebase de
> Sebastián (`clam_environ/`) — no duplicar su código.
>
> ⚠ **DSMIL es la propuesta, NO una decisión cerrada.** La elección del
> módulo MIL alternativo queda **sujeta a confirmación en la reunión con
> Sebastián y Eduardo** (ver `../README.md`, decisiones pendientes). Lo que
> sigue enuncia y justifica la propuesta DSMIL; si la reunión elige otro
> aggregator, este README se reescribe.

## Hipótesis

El **attention pooling lineal** de CLAM (`M = torch.mm(A, h)` en
`models/model_clam.py:172` para CLAM_SB y `:239` para CLAM_MB) calcula la
representación del bag como **combinación lineal de embeddings de parche
ponderada por attention scores escalares**. Bajo esta formulación:

- Cada parche aporta independientemente al bag embedding.
- Las relaciones inter-parche (¿este parche es el "crítico" comparado con
  el resto? ¿hay una sola región positiva o múltiples?) no se modelan.

Este es **estructuralmente el peor caso** para tareas con patrones
**focales** — donde un único parche o región pequeña contiene la
evidencia positiva (MicroCalcificaciones es el ejemplo más claro: la
señal positiva ocupa < 1% de la WSI).

**DSMIL** (Li, Li & Eliceiri, CVPR 2021, [`../../papers/dsmil_li2021.pdf`](../../papers/dsmil_li2021.pdf))
agrega una **segunda rama dual-stream**:

1. **Stream 1 (max-pooling instance branch)**: identifica el parche con
   score más alto — el "parche crítico" `h_m`.
2. **Stream 2 (dual aggregator)**: para cada parche `h_i`, computa
   atención **relativa al parche crítico** vía una distancia entrenable
   (producto interno proyectado). El bag embedding final es la suma
   ponderada por esa atención **relacional**, no absoluta.

Predicción: DSMIL debería **mejorar `test_auc` en MicroCalcificaciones y
C.D.I. Necrosis** (tareas focales) más que la ablation de `B` del
Objetivo 2, porque ataca el cuello arquitectónico, no el sampling.

## Métrica de éxito

Métrica primaria:

- **Δ `test_auc` (DSMIL − baseline CLAM) ≥ +0.05** en MicroCalcificaciones
  o C.D.I. Necrosis.

Métricas secundarias:

- **No degradación material** en G.H. Dif. Tubular (n=934, patrón
  presumiblemente difuso): Δ `test_auc` ≥ −0.02. Si baja más, hay regresión.
- **Convergencia de la dual stream**: ambos componentes (max-pooling y
  dual aggregator) deben converger por separado, monitoreado vía
  inspección de logs.

## Argumento arquitectónico (formalización)

Notación (siguiendo el paper DSMIL §3):

- Bag de N parches: `H = [h_1, h_2, …, h_N] ∈ R^{N×D}` (CONCH features,
  D=512 o 1024).
- **CLAM attention**: `α_i = softmax(w^T tanh(V h_i))`,
  `M = Σ_i α_i h_i`. Atención **absoluta**.
- **DSMIL critical instance**: `m = argmax_i c_i`, donde
  `c_i = w_c^T h_i`. Parche crítico: `h_m`.
- **DSMIL relational attention**: para cada parche,
  `q_i = W_q h_i`, `k_m = W_k h_m`. Atención:
  `β_i = softmax(<q_i, k_m> / √D)`.
- Bag embedding final: `b = Σ_i β_i (W_v h_i)`.

Lo que cambia: `α_i` depende solo de `h_i`; `β_i` depende de **la
relación entre `h_i` y `h_m`**. Para una tarea focal donde el "patrón
positivo" es único en la WSI, `β_i` colapsa a un one-hot alrededor del
parche crítico, mientras que `α_i` puede dispersarse.

## Cambios concretos al código (wrapper, NO modificar Sebastián)

> **NOTA — archivos planificados, no presentes**: los archivos listados
> abajo (`src/dsmil_aggregator.py`, `src/clam_dsmil_wrapper.py`,
> `main_dsmil.py`, `scripts/train_dsmil.slurm`) **NO existen todavía** en
> el repo. Crearlos es el **trabajo central de este objetivo del
> sprint**, no parte del scaffolding inicial. Antes de cualquier commit
> que los introduzca, pasa por el agente `reviewer` (regla "Argumento
> antes de código").

- **Archivo nuevo** en este repo: `src/dsmil_aggregator.py` (a crear).
  Módulo DSMIL puro: `nn.Module` con `forward(H) -> (β, b, c_max)`
  donde `H` son CONCH features, `β` la atención relacional, `b` el bag
  embedding, `c_max` el score del parche crítico.
- **Subclase** `src/clam_dsmil_wrapper.py` (a crear) de `CLAM_MB` que
  sobrescribe el forward para reemplazar el `attention_net` por el
  aggregator DSMIL. Mantiene:
  - Pipeline CONCH features → embeddings (mismo `embed_dim`).
  - Bag classifier final (mismo `nn.Linear`).
  - `instance_classifier` path con SmoothTop1SVM (mismo `inst_eval` /
    `inst_eval_out`, sin tocar `--B`).
  - CSVs de entrada y salida (mismo `dataset_<task>_label.csv`,
    `splits_0.csv`, `summary.csv`).
- **Wrapper de training**: `scripts/train_dsmil.slurm` (a crear),
  paralelo a `train_clam.sh`. Llama a un `main_dsmil.py` local (a
  crear) que importa `main.py` de Sebastián y solo intercambia la clase
  de modelo.

**Restricción**: `/media/administrador/Storage1/sdonoso/clam_environ/`
queda intacto. Solo se importa.

## Dependencias

- [ ] **Objetivo 1 completado** (baseline reproducible — comparable
      contra DSMIL).
- [ ] **Validar contra el repo oficial** <https://github.com/binli123/dsmil-wsi>
      al implementar (no inventar la arquitectura: replicar la del paper
      + repo).
- [ ] **Splits canónicos** definidos.

## Riesgos identificados

- **DSMIL fue diseñado pensando en CTransPath / SimCLR features**, no
  CONCH. La adaptación al feature space de CONCH (1024-dim) no debería
  ser problemática (es solo cambiar `D` y las dimensiones de
  `W_q, W_k, W_v`), pero requiere validación temprana con un smoke test.
- **Combinación con SmoothTop1SVM**: el paper DSMIL usa una loss
  diferente (bag-level BCE + max-pooling BCE). Decisión a tomar:
  ¿se replica la loss del paper o se mantiene `--bag_loss ce --inst_loss
  svm` para comparabilidad con el baseline? **Default: mantener bag+inst
  loss de CLAM** para que la única variable sea el aggregator.

## Plan de ejecución (post-reunión)

1. Smoke test del aggregator: forward de un batch sintético, verificar
   shapes y que el gradiente fluye.
2. Train de 5 epochs sobre la task más chica (probablemente
   MicroCalcificaciones), verificar convergencia.
3. Train completo (`max_epochs=30`) sobre las 4 tareas prioritarias.
4. Comparar contra baseline (Objetivo 1) y B=16 (Objetivo 2) en la
   tabla unificada de `resultados.md`.

## Output esperado

```
objetivo_3_dsmil/
├── README.md                       # este archivo
├── dsmil_architecture_notes.md     # derivación matemática + notas de implementación
├── src_local/
│   ├── dsmil_aggregator.py         # módulo DSMIL puro (no toca CLAM)
│   └── clam_dsmil_wrapper.py       # subclase de CLAM_MB con aggregator intercambiado
├── resultados.md                   # baseline vs DSMIL, tabla por tarea
└── logs/
    └── <task>_dsmil_<exp_code>/
```

## Placeholder de resultados

_Pendiente — completar tras implementación + ejecución._

| Tarea | test_auc baseline | test_auc DSMIL | Δ | Veredicto |
|---|---|---|---|---|
| MicroCalcificaciones | — | — | — | — |
| C.D.I. Grado Nuclear | — | — | — | — |
| C.D.I. Necrosis | — | — | — | — |
| G.H. Dif. Tubular | — | — | — | (no degradación) |
