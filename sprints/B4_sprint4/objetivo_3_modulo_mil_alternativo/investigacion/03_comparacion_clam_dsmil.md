# Frente 3 — Comparación arquitectónica CLAM vs DSMIL

> **Fuentes**:
> - CLAM: código real en `clam_environ/` (READ-ONLY) — `models/model_clam.py`,
>   `utils/core_utils.py`. Líneas verificadas contra el codebase actual.
> - DSMIL: paper (ver [`01_paper_resumen.md`](01_paper_resumen.md)) +
>   `DSMIL_official_reference/dsmil.py` (ver [`02_codigo_oficial_mapeo.md`](02_codigo_oficial_mapeo.md)).
>
> Notación: `N` = nº de parches del bag; `D` = dim de feature de entrada
> (CONCH = 512); `H` = dim oculta tras la proyección (CLAM usa 512);
> `C` = nº de clases.

---

## 0. Resumen en una frase

CLAM y DSMIL comparten el esqueleto MIL embedding-based (features →
proyección → **pooling con atención** → bag classifier + rama de
supervisión de instancia). **Difieren solo en el bloque de pooling**: CLAM
usa atención *absoluta* (cada parche puntuado de forma independiente);
DSMIL usa atención *relacional* (cada parche puntuado por su distancia al
parche crítico). Eso hace que reemplazar uno por otro sea un swap de un
bloque, no una reescritura.

---

## 1. Tabla comparativa maestra

| Dimensión | CLAM (CLAM_MB, OncoMets) | DSMIL |
|---|---|---|
| **Backbone de features** | CONCH precomputado, `[N,512]` (ResNet legacy `[N,1024]`) | Paper: SimCLR ResNet18 `[N,512]`. Código: cualquier feature precomputada. |
| **Proyección de entrada** | `Linear(512→512)·ReLU·Dropout` (`model_clam.py:191`) | Ninguna fija; `q`/`v` proyectan dentro del aggregator |
| **Mecanismo de pooling** | Atención gated **absoluta** | Dual-stream: instancia crítica + atención **relacional** |
| **Atención** | `A_i = W_c·(tanh(W_a·h_i) ⊙ σ(W_b·h_i))`, softmax sobre N (`Attn_Net_Gated`, `model_clam.py:41-64`) | `β_i = softmax(⟨q_i,q_m⟩/√128)` sobre N (`dsmil.py:55-56`) |
| **Depende de** | solo de `h_i` (independiente entre parches) | de la relación `h_i ↔ h_m` (parche crítico) |
| **Bag embedding** | `M = A·h`, `[C,H]` (`model_clam.py:239`) | `b = Σ U(h_i,h_m)·v_i`, `[C,D]` (`dsmil.py:57`) |
| **Bag classifier** | `Linear(512→1)` por clase (`model_clam.py:198`) | `Conv1d(C,C,kernel=D)` (`dsmil.py:44`) |
| **Salida de bag** | logits `[1,C]` → **softmax** → multi-CLASE | logits `[1,C]` → **sigmoide** → multi-LABEL |
| **Rama de supervisión de instancia** | top-B/bottom-B sobre la atención + pseudo-labels + SmoothTop1SVM | instance classifier separado + max-pooling + BCE |
| **Loss compuesta** | `bag_weight·L_bag + (1−bag_weight)·L_inst`, `bag_weight=0.7` | `0.5·BCE(bag) + 0.5·BCE(max)` |
| **Memoria** | O(N) | O(N) |
| **Mini-batch** | 1 slide (`core_utils.py` itera bag a bag) | 1 bag (`train_tcga.py`) |

---

## 2. Backbone de features — ¿afecta la comparación?

- **CLAM/OncoMets**: usa **CONCH** (foundation model vision-language de
  patología; features `[N,512]` ya extraídas, read-only en
  `environ/features/pt_files/`).
- **DSMIL/paper**: usa un **ResNet18 entrenado con SimCLR** sobre los
  parches del propio dataset (features `[N,512]`).

**Implicación.** El componente #2 de DSMIL (self-supervised contrastive
learning) es, en el paper, responsable de ≥14–16 % de accuracy
(Tabla 3, ver `01_`). En OncoMets ese componente **no se ejecuta**: CONCH
ya es un extractor de features mucho más potente que un ResNet18-SimCLR
entrenado por dataset. La hipótesis razonable —pero **no verificada por el
paper**— es que CONCH **cubre y supera** ese rol. La consecuencia práctica:
del paper DSMIL **solo transplantamos el aggregator (componente #1)**; la
comparación CLAM↔DSMIL en OncoMets es, por construcción, una comparación
**de aggregators a igualdad de features (CONCH)**. Eso es bueno: aísla la
variable. Coincidencia útil: SimCLR-ResNet18 y CONCH son ambos 512-dim →
`feats_size=512` encaja sin cambios.

---

## 3. Mecanismo de pooling — el corazón de la diferencia

### CLAM — atención absoluta gated

`Attn_Net_Gated` (`model_clam.py:41-64`):

```
a_i = tanh(W_a · h_i)        # rama "qué tan informativo"
b_i = sigmoid(W_b · h_i)     # rama "gate"
A_i = W_c · (a_i ⊙ b_i)      # score de atención  [N,C]
A   = softmax(A, sobre N)    # model_clam.py:213
M   = A · h                  # bag embedding [C,H]   model_clam.py:239
```

`A_i` depende **solo de `h_i`**. Dos parches idénticos reciben el mismo
peso sin importar qué más hay en el bag.

### DSMIL — atención relacional dual-stream

```
Stream 1:  c_i = W_0 · h_i ;  m = argmax_i c_i ;  h_m = parche crítico
Stream 2:  q_i = q_net(h_i) ;  v_i = h_i (Identity por defecto)
           β_i = softmax( ⟨q_i, q_m⟩ / √128 )  sobre N
           b   = Σ_i β_i · v_i                 # bag embedding [C,D]
```

`β_i` depende de **la relación entre `h_i` y el parche crítico `h_m`**.

### Por qué importa para tareas focales

En una tarea **focal** (la evidencia positiva está en una región
pequeña, p. ej. MicroCalcificaciones <1 % de la WSI):

- CLAM: la atención absoluta puede **dispersarse** entre muchos parches
  con apariencia parecida; no hay un mecanismo que diga "este es EL
  parche, los demás compáralos con él".
- DSMIL: el Stream 1 fija el parche crítico; el Stream 2 colapsa la
  atención alrededor de él. Estructuralmente más adecuado al caso focal.

Este es el **argumento arquitectónico** del Objetivo 3 (ver
[`../propuesta_dsmil.md`](../propuesta_dsmil.md)). Es una hipótesis, no un
resultado: el paper nunca lo midió en multi-clase desbalanceado.

---

## 4. Supervisión de instancia — dos filosofías

| | CLAM | DSMIL |
|---|---|---|
| Qué parches supervisa | los `B` de mayor atención (pseudo-positivos) y los `B` de menor (pseudo-negativos) | **todos** los parches reciben score; solo el de score máximo entra a la loss |
| Pseudo-labels | sí: top-B → 1, bottom-B → 0 (`inst_eval`, `model_clam.py:107-125`) | no: la loss compara `max(scores)` con la etiqueta real del bag |
| Loss | `SmoothTop1SVM` (`--inst_loss svm`) sobre `2B` parches | `BCEWithLogitsLoss` sobre 1 score (el máximo) |
| Clasificador | `Linear(H,2)` por clase (`model_clam.py:200`) | `FCLayer`: `Linear(D,C)` (`dsmil.py:9`) |
| Hiperparámetro | `--B` (top-B/bottom-B count, default 8) | ninguno equivalente |
| Rol en el modelo | regularización tipo *clustering* del espacio de embeddings | es **el Stream 1**, mitad de la predicción final |

**Diferencia conceptual.** En CLAM la supervisión de instancia es una
**regularización auxiliar**: empuja el espacio de features a que los
parches de alta/baja atención sean separables. En DSMIL el "instance
branch" **no es auxiliar**: es un stream de predicción de pleno derecho
(Ec. 8) y además **provee la instancia crítica** que el Stream 2
necesita. No se pueden tratar como equivalentes.

> El Objetivo 2 del sprint hace ablation de `--B`. Ese hiperparámetro
> **no existe en DSMIL**: si la reunión confirma DSMIL, la ablation de `B`
> y el módulo DSMIL son experimentos sobre mecanismos distintos (ver
> [`../alternativas_consideradas.md`](../alternativas_consideradas.md)).

---

## 5. Loss compuesta — comparación directa

```
CLAM :  total = bag_weight · L_bag      + (1 − bag_weight) · L_inst
              = 0.7 · CE(logits,label)  + 0.3 · SmoothTop1SVM(2B parches)
        (core_utils.py:271 ; bag_weight default 0.7)

DSMIL:  total = 0.5 · BCE(bag_pred, label) + 0.5 · BCE(max_pred, label)
        (train_tcga.py:71)
```

Verificado: `core_utils.py:263` `loss = loss_fn(logits,label)` (bag),
`:266` `instance_loss = instance_dict['instance_loss']`, `:271` la
combinación. `bag_weight` default 0.7 = 70 % slide-level / 30 % instance.

Diferencias:
- **Peso**: CLAM 0.7/0.3 ajustable; DSMIL 0.5/0.5 fijo.
- **L_bag**: CLAM `CrossEntropy` (multi-clase, softmax); DSMIL `BCE`
  (multi-label, sigmoide).
- **L_inst**: CLAM `SmoothTop1SVM` sobre `2B` parches con pseudo-labels;
  DSMIL `BCE` sobre el parche de score máximo.

**Decisión de integración** (ya propuesta como default en
[`../propuesta_dsmil.md`](../propuesta_dsmil.md)): **mantener la loss
compuesta de CLAM** (`bag_weight·L_bag + (1−bag_weight)·L_inst`,
`--bag_loss ce --inst_loss svm`) para que la **única variable** sea el
aggregator. Replicar la loss nativa de DSMIL es una alternativa, pero
mete dos variables a la vez. → pregunta de reunión, `04_` §C.2.

---

## 6. Subtyping / multi-clase — el choque más serio

| | CLAM_MB | DSMIL |
|---|---|---|
| Formulación | multi-**clase** mutuamente excluyente | multi-**label** independiente |
| Bag classifier | `Linear(H,1)` por clase → logits `[1,C]` → **softmax** | `Conv1d` → logits `[1,C]` → **sigmoide** por clase |
| Loss de bag | `CrossEntropyLoss` | `BCEWithLogitsLoss` |
| `n_classes` | nº total de clases | nº de clases **positivas** (binario → 1; clase negativa → label `N`) |
| Bandera | `subtyping` (`model_clam.py:205`) activa `inst_eval_out` para ramas fuera-de-clase | — |
| Multi-clase en paper | sí, validado en tareas multi-clase clínicas | **no validado**: Camelyon16 binario, TCGA-lung = 2 subtipos sin clase negativa |

**El choque.** Si MicroCalcificaciones (u otra de las 4 prioritarias) es
**multi-clase mutuamente excluyente**, la formulación nativa de DSMIL
(sigmoide multi-label) es un **mismatch semántico**: trataría las clases
como independientes cuando son excluyentes.

**Pero la integración propuesta lo resuelve**: al conservar el bag
classifier de CLAM (`Linear` por clase + `softmax` + `CrossEntropy`) y
descartar el `Conv1d` de DSMIL, la salida vuelve a ser multi-clase
correcta. El precio: el Stream 1 de DSMIL (instance scorer + max-pooling +
BCE) sigue siendo multi-label por naturaleza. Hay que decidir si el
Stream 1 se mantiene con su BCE nativo o se reemplaza por la rama
instance de CLAM. → riesgo técnico, `04_` §B; pregunta `04_` §C.2.

---

## 7. Memoria GPU — ambos O(N), sin sorpresas

| Operación | CLAM | DSMIL |
|---|---|---|
| Proyección / atención por parche | O(N·H) | `q`,`v` O(N·H) |
| Producto de atención | `A·h`: O(N·C·H) | `mm(Q,q_max^T)`: O(N·C·128); `mm(A^T,V)`: O(N·C·D) |
| Selección de instancia | `topk` O(N) | `sort(c)` O(N log N) compute, O(N) memoria |
| **Pico de memoria** | **O(N)** | **O(N)** |

Ambos son **lineales en N**. Ninguno materializa una matriz N×N. Esto
contrasta con TransMIL (self-attention completa, O(N²) sin la
aproximación de Nyström — ver
[`../alternativas_consideradas.md`](../alternativas_consideradas.md)).
Para la RTX A6000 (49 GB) única del servidor, DSMIL **no agrega riesgo de
OOM** respecto a CLAM. (Matiz: el `sort` de todo el bag tiene costo de
cómputo O(N log N); con N≈50k es despreciable. Ver `04_` §B.)

---

## 8. Punto de inserción — qué se conserva, reemplaza, agrega

Mapa de la integración (`DSMIL_CLAM_MB`, ver
[`../plan_integracion.md`](../plan_integracion.md) y el skeleton
`../scaffolding/dsmil_wrapper.py`):

**SE CONSERVA del pipeline CLAM:**
- Features CONCH `.pt` y su carga (`Generic_MIL_Dataset`).
- Proyección de entrada `Linear(512→512)·ReLU·Dropout` (`model_clam.py:191`).
- Bag classifier: `Linear(512→1)` por clase (`model_clam.py:198`) →
  softmax → multi-clase.
- Rama de supervisión de instancia de CLAM: `inst_eval` / `inst_eval_out`
  + `SmoothTop1SVM` (`model_clam.py:107-138`).
- Loss compuesta `bag_weight·L_bag + (1−bag_weight)·L_inst`
  (`core_utils.py:271`).
- Splits, CSVs, `summary.csv`, training loop `train_loop_clam`.

**SE REEMPLAZA:**
- El `Attn_Net_Gated` (`model_clam.py:193`) → aggregator dual-stream de
  DSMIL. Único cambio arquitectónico.

**SE AGREGA (interno al aggregator):**
- Stream 1: instance scorer `c = W_0·h` para **seleccionar la instancia
  crítica** (no necesariamente para la loss — ver matiz abajo).
- Stream 2: proyecciones `q`/`v` y la atención relacional
  `β = softmax(⟨q_i,q_m⟩/√128)`.

**Matiz no trivial.** CLAM y DSMIL tienen *cada uno* una noción de
"instancia": CLAM hace `inst_eval` sobre la **atención** `A`; DSMIL elige
el parche crítico por `argmax` del **instance scorer** `c`. Al integrar,
conviven dos mecanismos:
- El instance scorer de DSMIL (`c`) es **obligatorio** — sin él no hay
  parche crítico ni Stream 2.
- La rama `inst_eval` de CLAM puede seguir operando sobre la atención
  relacional `β` de DSMIL (top-B/bottom-B sobre `β`).
Decisión abierta: ¿el `c` de DSMIL se supervisa (BCE nativo, sumándolo a
la loss) o se deja como componente puramente interno para elegir la
crítica? → `04_` §B y §C.2.

---

## 9. Veredicto del Frente 3

- El swap es **arquitectónicamente limpio**: un solo bloque cambia, el
  resto del pipeline CLAM sobrevive intacto. Coherente con la
  [`../plan_integracion.md`](../plan_integracion.md) ya escrita.
- **No hay riesgo de memoria** (ambos O(N)).
- El punto **genuinamente delicado** no es el pooling sino la
  **reconciliación de la supervisión de instancia y de la formulación
  multi-clase** (§6, §8). La integración propuesta lo resuelve en papel
  conservando el bag classifier y la loss de CLAM, pero deja una decisión
  de diseño (qué hacer con el Stream 1 de DSMIL) que debe cerrarse en la
  reunión. Detalle y mitigaciones en
  [`04_riesgos_y_preguntas_reunion.md`](04_riesgos_y_preguntas_reunion.md).
