# Frente 2 — Código oficial DSMIL: análisis y mapeo

> **Fuente**: repo oficial `binli123/dsmil-wsi`, clonado read-only como
> hermano del repo personal en
> `clam_testing2/DSMIL_official_reference/` — **HEAD `80465ed`, fecha
> 2024-03-29**. Incluye los *updates 2024* del README (10× speedup,
> cross-validation, init estable).
>
> Convención: cada afirmación cita `archivo:línea`. Las ecuaciones citan
> el paper (ver [`01_paper_resumen.md`](01_paper_resumen.md)).

---

## 1. Estructura del repo (anotada)

```
DSMIL_official_reference/
├── dsmil.py              ← MÓDULO MIL. FCLayer, IClassifier, BClassifier, MILNet. (75 líneas)
├── train_tcga.py         ← Training para WSI con features precomputadas. EL RELEVANTE para nosotros.
├── train_mil.py          ← Training para datasets MIL clásicos (musk/fox/tiger/elephant).
├── compute_feats.py      ← Extracción de features con el embedder SimCLR. NO lo usamos (tenemos CONCH).
├── deepzoom_tiler.py     ← Tessellation de WSI con OpenSlide. NO lo usamos (parches ya extraídos).
├── attention_map.py      ← Genera mapas de detección / heatmaps de atención.
├── testing_tcga.py       ← Inference + detection maps sobre WSI nuevas (TCGA).
├── testing_c16.py        ← Idem Camelyon16.
├── test_crop_single.py   ← Crop de WSI de test.
├── download.py           ← Descarga datasets y features precomputadas.
├── simclr/               ← Entrenamiento del embedder SimCLR. NO lo usamos.
├── env.yml               ← Deps conda (ver §8).
├── init.pth              ← Pesos sueltos (legacy; el training actual usa init ortogonal por código).
├── example_aggregator_weights/  ← Pesos de aggregator de ejemplo. NO descargar/usar (regla 8 del proyecto).
├── tcga-download/, thumbnails/  ← Auxiliares.
└── LICENSE, README.md
```

**Para el Objetivo 3 solo importan `dsmil.py` y `train_tcga.py`.** El
resto es el pipeline de tessellation + SimCLR que reemplazamos por las
features CONCH ya extraídas.

---

## 2. `dsmil.py` — análisis línea por línea

Imports (`dsmil.py:1-4`): `torch`, `torch.nn`, `torch.nn.functional`,
`torch.autograd.Variable`. **PyTorch puro, sin deps externas** — confirma
`requirements_obj3.txt` (cero deps nuevas sobre `clam_latest`).

### 2.1 `FCLayer` (`dsmil.py:6-12`) — clasificador de instancia simple

```
self.fc = nn.Sequential(nn.Linear(in_size, out_size))   # :9
forward(feats) -> (feats, self.fc(feats))               # :10-12
```

Es el `W_0` del Stream 1 (paper Ec. 3) cuando las features ya están
precomputadas. Devuelve las features **sin tocar** y los scores de
instancia. `train_tcga.py:236` lo instancia como i_classifier.

### 2.2 `IClassifier` (`dsmil.py:14-25`) — instance classifier con CNN

Igual que `FCLayer` pero **además** corre un `feature_extractor` (CNN)
sobre imágenes crudas. **No nos sirve**: nuestras features CONCH ya están
extraídas. `train_tcga.py` con features precomputadas usa `FCLayer`, no
`IClassifier`.

### 2.3 `BClassifier` (`dsmil.py:27-62`) — el dual aggregator (Stream 2)

`__init__` (`:28-44`):

| Atributo | Código | Paper | Nota |
|---|---|---|---|
| `self.q` | `:30-33` MLP `Linear(in,128)·ReLU·Linear(128,128)·Tanh` si `nonlinear=True`; si no, `Linear(in,128)` | Ec. 4 `q_i = W_q h_i` | ⚠ **Discrepancia 1**: el paper formaliza `q` lineal; el código por defecto (`non_linearity=1`) usa un MLP no-lineal. Dim de query = **128 hardcoded**. |
| `self.v` | `:34-41` `nn.Identity()` si `passing_v=False`; si no, `Dropout·Linear(in,in)·ReLU` | Ec. 4 `v_i = W_v h_i` | ⚠ **Discrepancia 2**: por defecto `v` es **Identidad** → `v_i = h_i`, NO hay `W_v` aprendido. El paper define `W_v` como matriz de peso. |
| `self.fcc` | `:44` `nn.Conv1d(output_class, output_class, kernel_size=input_size)` | Ec. 7 `c_b = W_b·b` | ⚠ **Discrepancia 4**: el paper dice "vector de pesos `W_b`"; el código usa una **Conv1d** que **mezcla todas las clases** (cada score de salida ve los bag embeddings de todas las clases). |

`forward(feats, c)` (`:46-62`), `feats` = `[N,K]`, `c` = scores de
instancia `[N,C]`:

```
V = self.v(feats)                                  # :48  [N,K]  (Identity -> = feats)
Q = self.q(feats).view(N, -1)                      # :49  [N,128]
_, m_indices = torch.sort(c, 0, descending=True)   # :52  ordena scores por instancia
m_feats = feats[m_indices[0, :]]                   # :53  instancia CRÍTICA por clase -> [C,K]
q_max = self.q(m_feats)                            # :54  query de la crítica -> [C,128]
A = torch.mm(Q, q_max.transpose(0,1))              # :55  [N,C]  productos internos
A = F.softmax(A / sqrt(Q.shape[1]), 0)             # :56  softmax sobre N
B = torch.mm(A.transpose(0,1), V)                  # :57  [C,K]  bag embedding
B = B.view(1, C, K)                                # :59
C_out = self.fcc(B).view(1, -1)                    # :60-61  [1,C]  bag score
return C_out, A, B                                 # :62
```

- `:52-53` — la **instancia crítica** (paper Ec. 3): se ordenan los
  scores `c` y se toma `m_indices[0,:]`, el índice del parche de mayor
  score **por cada clase**. `m_feats` es `[C,K]`.
- `:56` — ⚠ **Discrepancia 3**: el código divide por `sqrt(Q.shape[1]) =
  sqrt(128)` (scaled dot-product, estilo Transformer). El paper Ec. 5
  **no tiene** ese factor de escala.
- El softmax es sobre `dim=0` (las N instancias) → los pesos de atención
  suman 1 sobre el bag, consistente con el paper.

### 2.4 `MILNet` (`dsmil.py:64-74`) — wrapper de los dos streams

```
forward(x):                                        # :70
    feats, classes = self.i_classifier(x)          # :71  Stream 1
    prediction_bag, A, B = self.b_classifier(feats, classes)  # :72  Stream 2
    return classes, prediction_bag, A, B           # :74
```

- `classes` `[N,C]` = scores de instancia (Stream 1, **sin** max-pooling).
- `prediction_bag` `[1,C]` = score de bag (Stream 2).
- ⚠ **El max-pooling del Stream 1 NO está en el modelo**: se hace en el
  training loop (`train_tcga.py:68`, ver §3). El modelo solo entrega los
  scores por instancia.

---

## 3. Mapeo paper → código (tabla maestra)

| Componente (paper) | Ecuación | Código | Tensor in → out |
|---|---|---|---|
| Instancia → embedding `h_i` | §3.2 | features precomputadas (CONCH/SimCLR) | imagen → `[N,K]` |
| Stream 1: score de instancia `W_0 h_i` | Ec. 3 | `FCLayer.fc` `dsmil.py:9` | `[N,K]` → `[N,C]` |
| Stream 1: max-pooling → instancia crítica | Ec. 3 | `torch.max(ins_prediction,0)` `train_tcga.py:68` | `[N,C]` → `[C]` |
| Stream 2: query `q_i = W_q h_i` | Ec. 4 | `BClassifier.q` `dsmil.py:30-33` | `[N,K]` → `[N,128]` |
| Stream 2: info vector `v_i = W_v h_i` | Ec. 4 | `BClassifier.v` `dsmil.py:34-41` | `[N,K]` → `[N,K]` (Identity) |
| Stream 2: instancia crítica `h_m` | Ec. 3→5 | `sort` + `index_select` `dsmil.py:52-53` | `[N,C]` → `[C,K]` |
| Stream 2: distancia `U(h_i,h_m)` | Ec. 5 | `mm`+`softmax` `dsmil.py:55-56` | `[N,128]×[C,128]` → `[N,C]` |
| Stream 2: bag embedding `b` | Ec. 6 | `mm(A.T,V)` `dsmil.py:57` | `[N,C]×[N,K]` → `[C,K]` |
| Stream 2: bag score `c_b = W_b b` | Ec. 7 | `Conv1d` `dsmil.py:44,60` | `[1,C,K]` → `[1,C]` |
| Fusión de streams | Ec. 8 | **NO en el modelo**; `train_tcga.py:107` solo si `--average` | — |

Dtype en todo el pipeline: `float32`, tensores en `cuda` (`train_tcga.py:59,90`).

---

## 4. Loop de entrenamiento (`train_tcga.py`)

### 4.1 Carga de features

- `generate_pt_files` (`:36-51`): *update 2024* para el "10× speedup".
  Lee el CSV de bags, y para cada bag concatena `[features | label
  repetida]` y lo guarda como `.pt` en `temp_train/`. Cada `.pt` es un
  tensor `[N, feats_size + num_classes]`.
- `train` (`:55-76`): por cada bag (orden barajado, `:57`):
  `stacked_data = torch.load(...)` → separa `bag_label` (`:63`) y
  `bag_feats` `[N, feats_size]` (`:64`).
- `dropout_patches` (`:78-83`): descarta aleatoriamente una fracción de
  parches en entrenamiento (`dropout_patch`, default 0 → no descarta).

> **Nota de containment**: `generate_pt_files` escribe `temp_train/` en el
> CWD. En nuestra integración esto se reemplaza por el `Generic_MIL_Dataset`
> de CLAM (que ya lee los `.pt` de CONCH); no se usa `generate_pt_files`.

### 4.2 Forward + loss (`train_tcga.py:67-74`) — pieza crítica

```
ins_prediction, bag_prediction, _, _ = milnet(bag_feats)   # :67
max_prediction, _ = torch.max(ins_prediction, 0)           # :68  max-pooling Stream 1
bag_loss = criterion(bag_prediction.view(1,-1), bag_label.view(1,-1))  # :69
max_loss = criterion(max_prediction.view(1,-1), bag_label.view(1,-1))  # :70
loss = 0.5*bag_loss + 0.5*max_loss                         # :71
loss.backward(); optimizer.step()                          # :72-73
```

- `criterion` = `nn.BCEWithLogitsLoss()` (`:240`).
- **Los dos streams se supervisan por separado** con la etiqueta del bag,
  peso fijo 0.5/0.5. La loss NO se computa sobre el score promediado.
- **Mini-batch = 1 bag**: el loop itera bag por bag, no hay batching de
  slides (consistente con el paper).

### 4.3 Optimizer, scheduler, init (`train_tcga.py:229-243`)

| Ítem | Valor | Línea | Nota |
|---|---|---|---|
| Init de pesos | `nn.init.orthogonal_` para Linear/Conv1d/Conv2d, bias=0 | `:229-233` | *update 2024* "stable model initialization". El paper no lo menciona. |
| Loss | `nn.BCEWithLogitsLoss()` | `:240` | sigmoide → multi-label |
| Optimizer | `Adam(lr=args.lr, betas=(0.5,0.9), weight_decay=1e-3)` | `:241` | ⚠ `betas=(0.5,0.9)` NO es el default de Adam (0.9,0.999). El paper no lo dice. |
| Scheduler | `CosineAnnealingLR(optimizer, num_epochs, eta_min=5e-6)` | `:242` | ⚠ **Discrepancia 5**: el paper dice "constant lr 0.0001". |

### 4.4 Esquemas de evaluación (`train_tcga.py`)

Argumento `--eval_scheme`:

- `5-fold-cv` (default, `:252-294`): KFold(5, shuffle, seed 42). AUC/acc
  por fold, promediado.
- `5-fold-cv-standalone-test` (`:350-429`): reserva 20 % como test, 5-fold
  CV sobre el 80 %; los 5 mejores modelos votan por mayoría sobre el test.
- `5-time-train+valid+test` (`:297-348`): 5 corridas con split
  train/val/test.
- Early stopping: `stop_epochs` (default 10) épocas sin mejorar →
  `break` (`:287`). "Mejorar" = `current_score = (sum(aucs)+avg_score)/2`
  (`:179-181`).

### 4.5 Inference (`test`, `train_tcga.py:85-132`)

- ⚠ **Discrepancia 6**: predicción por defecto =
  `torch.sigmoid(bag_prediction)` **solo el Stream 2** (`:108`). El
  promedio de los dos streams (paper Ec. 8) se usa **solo si
  `--average`** (default `False`, `:214`):
  `sigmoid(max)+sigmoid(bag)` (`:107`).
- Umbral de decisión: óptimo del ROC (`optimal_thresh`, `:165-168`), no
  un 0.5 fijo.

---

## 5. Defaults numéricos: código vs paper

| Hiperparámetro | Código (`train_tcga.py`) | Paper | ¿Coincide? |
|---|---|---|---|
| `feats_size` | 512 (`:202`) | 512 (ResNet18) | ✅ |
| `lr` | 1e-4 (`:203`) | 1e-4 | ✅ valor; ❌ schedule |
| schedule | CosineAnnealing→5e-6 (`:242`) | "constant" | ❌ |
| `num_epochs` | 50 (`:204`) | no especificado | — |
| `stop_epochs` (early stop) | 10 (`:205`) | no especificado | — |
| `weight_decay` | 1e-3 (`:207`) | no especificado | — |
| Adam betas | (0.5, 0.9) (`:241`) | no especificado | — |
| mini-batch | 1 bag | 1 bag | ✅ |
| `num_classes` | 2 (`:201`) | — | TCGA-lung = 2 subtipos |
| `dropout_patch` | 0 (`:211`) | no especificado | — |
| `dropout_node` (v-net) | 0 (`:212`) | no especificado | — |
| `non_linearity` (q-net MLP) | 1 = activado (`:213`) | Ec. 4 lineal | ❌ |
| `average` (fusión inference) | False (`:214`) | Ec. 8 promedia | ❌ |

`--num_classes` (README §"Feature vector csv files", líneas 315-317):
**binario → `num_classes=1`** (una sola rama sigmoide); **N clases
positivas → `num_classes=N`**; si hay clase negativa, su label es `N`.
Es decir, `num_classes` cuenta **clases positivas**, no clases totales.

---

## 6. Discrepancias paper ↔ código — resumen

| # | Paper | Código | Impacto para la integración |
|---|---|---|---|
| 1 | `q` lineal (Ec. 4) | `q` = MLP no-lineal (default) | Bajo. Más capacidad; replicar el código. |
| 2 | `v_i = W_v h_i` (Ec. 4) | `v` = Identidad (default) | **Medio.** Sin `W_v`, el bag embedding es media ponderada de features CRUDAS. Con CONCH (512-dim, ya semántico) puede estar bien, pero conviene probar `passing_v=True`. Ver `04_` §B. |
| 3 | sin escala (Ec. 5) | `/sqrt(128)` | Bajo. Estabiliza el softmax; replicar el código. |
| 4 | `W_b` vector (Ec. 7) | `Conv1d` que mezcla clases | **Medio** en multi-clase. En la integración con CLAM **no se usa** el `fcc` de DSMIL — se conserva el bag classifier de CLAM. Anula la discrepancia. |
| 5 | lr constante | CosineAnnealingLR | Bajo. Decidir schedule al integrar. |
| 6 | score final = promedio (Ec. 8) | inference usa solo Stream 2 (default) | **Medio.** Define qué reportar como predicción. Ver `03_` y `04_`. |
| — | (init no mencionado) | init ortogonal | Bajo. Buena práctica; adoptar. |
| — | (betas no mencionados) | Adam betas (0.5,0.9) | Bajo–medio. `beta1=0.5` es inusual; probar y, si hay ruido, considerarlo. |

**Conclusión §6**: las discrepancias 1, 3, 5 son menores (replicar el
código). La 2 (sin `W_v`) y la 6 (qué stream se reporta) son decisiones
de diseño reales para la integración. La 4 se **neutraliza** porque la
integración con CLAM descarta el `fcc` de DSMIL.

---

## 7. Qué se reutiliza y qué se descarta para el Objetivo 3

| Del repo oficial | Acción |
|---|---|
| `dsmil.py` `BClassifier` (Stream 2) | **Replicar** como el aggregator dual-stream. |
| `dsmil.py` `FCLayer` (Stream 1) | **Replicar** como el instance scorer. |
| `dsmil.py` `MILNet` | Inspirar el wrapper `DSMIL_CLAM_MB`. |
| `compute_feats.py`, `simclr/`, `deepzoom_tiler.py` | **Descartar** — usamos features CONCH. |
| `train_tcga.py` loop, schemes, métricas | **Inspirar** `train_obj3.py`; pero la integración reusa el `core_utils.py` de CLAM. |
| `init.pth`, `example_aggregator_weights/` | **No usar** — regla 8 (no descargar/usar pesos pre-entrenados). |

---

## 8. Dependencias (`env.yml`)

`env.yml` lista: `numpy, pillow, matplotlib, scikit-learn, pyyaml,
pandas, scikit-image, jupyterlab, opencv, tqdm` (torch se instala
aparte). **Todas las que importan `compute_feats`/`simclr`/`tiler` — el
pipeline que NO usamos.** El módulo MIL (`dsmil.py`) solo importa torch.
Confirma `requirements_obj3.txt`: **cero deps nuevas** sobre `clam_latest`
para el aggregator. (Ya validado en la sesión de scaffolding.)
