# Plan de integración — DSMIL sobre el pipeline OncoMets

> Cómo el aggregator DSMIL se enchufa al pipeline existente **sin tocar**
> el codebase de Sebastián (`clam_environ/`, read-only). Wrapper-only.
> Folía la sección "Cambios concretos al código" del README anterior.

## 1. Inputs disponibles (ya existen, read-only)

Nada de esto se genera ni se modifica en este objetivo — se consume tal
cual.

| Input | Path (bajo `clam_environ/environ/`) | Forma |
|---|---|---|
| Features CONCH | `features/pt_files/` | `.pt` por slide, `[N_parches, 512]` float32 |
| Coords / patches | `features/h5_files/` | `.h5` por slide (no se usa para el aggregator) |
| Splits canónicos | `splits/<task>_pth_100/` | `splits_0.csv` train/val/test (priv+TCGA+HistAI) |
| Labels por task | `csv/dataset_<task>_label.csv` | `slide_id → label` (ej. `dataset_microcalcificaciones_label.csv`) |

> El split definitivo (`_pth_100` vs `_100`) y `embed_dim` (512 CONCH)
> los confirma la reunión (decisiones #2 y #7 del sprint). El scaffolding
> asume `_pth_100` + 512 como hipótesis de trabajo, parametrizable.

## 2. Punto de inserción

El aggregator DSMIL reemplaza **únicamente la rama de pooling** de
`CLAM_MB`. Concretamente, sustituye el `Attn_Net_Gated` que vive dentro
de `CLAM_MB.attention_net` (`models/model_clam.py:193-197`) y produce los
attention scores `A`.

```
CLAM_MB.forward(h)            model_clam.py:207-254
  A, h = attention_net(h)     ← attention_net = [Linear·ReLU·Drop·Attn_Net_Gated]
  A = softmax(A, dim=1)            el Linear·ReLU·Drop se CONSERVA
  ...inst_eval sobre A...          el Attn_Net_Gated se REEMPLAZA por DSMIL
  M = torch.mm(A, h)          :239
  logits[c] = classifiers[c](M[c])  ← se CONSERVA
```

DSMIL produce, en lugar de la atención absoluta gated:

1. **Stream 1** — score por instancia `c_i = w_c·h_i`; el `argmax`
   selecciona el parche crítico `h_m`.
2. **Stream 2** — atención relacional `β_{i,c} = softmax(⟨q_i, k_m⟩/√D)`
   y bag rep `M_c = Σ_i β_{i,c} (W_v h_i)`.

El `M` resultante tiene la misma forma `[n_classes, 512]` que el de CLAM,
por lo que los `classifiers` per-class de aguas abajo no se enteran del
cambio. Ver diagrama en [`propuesta_dsmil.md`](propuesta_dsmil.md).

## 3. Qué se modifica y qué queda intacto

| Componente | ¿Cambia? |
|---|---|
| Extracción de features CONCH | **No.** Se reusan los `.pt` existentes. |
| `fc` de entrada (`Linear 512→512·ReLU·Dropout`) | **No.** Se conserva. |
| Rama de pooling / atención | **Sí — único cambio.** Gated → dual-stream DSMIL. |
| Bag classifier (`classifiers`, `Linear 512→1` por clase) | **No.** Se conserva. |
| Instance branch (`inst_eval`/`inst_eval_out`, SmoothTop1SVM) | **No.** Se conserva (`--B` sin tocar). |
| Loss `bag_weight·L_bag + (1−bag_weight)·L_instance` | **No** (default). Decisión abierta — ver `propuesta_dsmil.md` §Riesgos. |
| CSVs de entrada/salida (`dataset_*_label.csv`, `splits_0.csv`, `summary.csv`) | **No.** Mismo formato. |

**Restricción dura**: `/media/administrador/Storage1/sdonoso/clam_environ/`
queda intacto. Solo se importa desde él; nada se copia ni se edita.

## 4. Qué se reusa del codebase de Sebastián

Regla de containment: se **importa**, no se copia.

- **`main.py`** — entrypoint de training. Se reusa vía un wrapper local
  (`scaffolding/train_obj3.py`) que añade `clam_environ/` al `sys.path`,
  importa lo necesario de `main.py` y **solo intercambia la clase de
  modelo** (`CLAM_MB` → `DSMIL_CLAM_MB`). **No se copia `main.py`** al
  repo personal.
- **`utils/core_utils.py`** — train loop con instance loss
  (`train_loop_clam`, `core_utils.py:241`). Se reusa **si es compatible**:
  el train loop opera sobre la interfaz `forward(...) → (logits, Y_prob,
  Y_hat, A_raw, results_dict)`; mientras `DSMIL_CLAM_MB` respete esa
  firma, `core_utils.py` no necesita cambios. Si algún detalle del loop
  asume internals de `CLAM_MB` incompatibles con DSMIL, se cae al train
  loop propio del esqueleto `train_obj3.py`. Esto se confirma en el smoke
  test, no antes.
- **`models/model_clam.py`** — `DSMIL_CLAM_MB` importa `CLAM_MB` y reusa
  `inst_eval` / `inst_eval_out` y los `classifiers`. La decisión de
  subclasear `CLAM_MB` o componer un `nn.Module` que lo contenga se cierra
  en la implementación (el skeleton usa `nn.Module` para ser
  import-safe; ver `scaffolding/README_scaffolding.md`).

## 5. Artefactos nuevos (todos bajo el repo personal)

Ninguno modifica `clam_environ/`. Containment: todo bajo
`clam_testing2/oncomets-ernesto/`.

- `scaffolding/dsmil_wrapper.py` — aggregator DSMIL + `DSMIL_CLAM_MB`.
  **Antes de commitear la versión funcional, pasar por el agente
  `reviewer`** (regla 9 — toca arquitectura de modelo).
- `scaffolding/train_obj3.py` — wrapper de training.
- `scripts/train_dsmil.slurm` — **pendiente, post-reunión.** Wrapper SLURM
  paralelo a `train_clam.slurm`, con `--output`/`--error`/`--results_dir`
  en paths absolutos dentro del repo personal (containment).
- `results/` y `logs/` — checkpoints y logs SLURM; texto/métricas se
  versionan, artefactos pesados no (ver `.gitignore`).

## 6. Esquema de evaluación

Idéntico a Objetivos 1 y 2 — esa es la razón de mantener todo lo demás
intacto.

- **Métricas**: AUC train / val / test sobre el **subset binario
  efectivo** de cada task (mismo criterio que Objetivos 1 y 2; ver
  hallazgo #3 de CLAUDE.md sobre clases minoritarias y AUC `nan`).
- **Tasks**: las 4 prioritarias (MicroCalcificaciones, C.D.I. Grado
  Nuclear, C.D.I. Necrosis, G.H. Dif. Tubular), sujeto a confirmación
  (decisión #5).
- **Comparación lado a lado**: tabla unificada `baseline (Obj 1)` vs
  `B=16 (Obj 2)` vs `DSMIL (Obj 3)`, una fila por task, en el
  `resultados.md` del objetivo.
- **Criterio de éxito**: el predefinido en `propuesta_dsmil.md`
  (Δ test_auc ≥ +0.05 en una task focal; no degradación ≥ −0.02 en la
  difusa).

## 7. Secuencia de ejecución (post-reunión)

1. Confirmar módulo + dataset + splits en la reunión.
2. Implementar el aggregator (rellenar TODOs de `dsmil_wrapper.py`),
   validando contra `DSMIL_official_reference/dsmil.py` y el paper.
3. Pasar por `reviewer` antes del commit de la implementación.
4. Smoke test: forward de un bag sintético `[N, 512]`, verificar shapes
   (`M` → `[n_classes, 512]`) y que el gradiente fluye.
5. Train corto (5 epochs) sobre la task más chica — verificar
   convergencia de ambos streams.
6. Train completo (`max_epochs` del baseline) sobre las 4 tareas, vía
   `sbatch` (regla SLURM — nunca `python` directo en GPU).
7. Volcar resultados a `resultados.md` y comparar.
