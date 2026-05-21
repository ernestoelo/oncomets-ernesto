# Frente 1 — Resumen del paper DSMIL

> **Fuente**: Li, B., Li, Y., & Eliceiri, K. W. (2021). *Dual-stream
> Multiple Instance Learning Network for Whole Slide Image Classification
> with Self-supervised Contrastive Learning.* CVPR 2021, pp. 14318–14328.
> arXiv:2011.08939v3 (2 abr 2021). PDF en
> [`../../../papers/dsmil_li2021.pdf`](../../../papers/dsmil_li2021.pdf)
> (leído completo, 8 páginas).
>
> Convención: toda afirmación cita sección / ecuación / figura / tabla del
> paper. Lo que viene **solo del código** y no del paper se marca
> `[CÓDIGO]` y se detalla en [`02_codigo_oficial_mapeo.md`](02_codigo_oficial_mapeo.md).
> Notación de ecuaciones: LaTeX-style inline, sin renderizar.

---

## 1. Problema que aborda

Clasificación de *whole slide images* (WSI) con **solo etiqueta a nivel de
slide** (weakly-supervised). Las WSI son gigapíxel (~40.000×40.000 px,
§1), no caben en memoria y rara vez tienen anotación localizada. El
paradigma estándar las parte en miles de parches y las trata como un
problema de **Multiple Instance Learning (MIL)**: la WSI es un *bag*, los
parches son *instances*; el bag es positivo si al menos un parche lo es,
negativo si ninguno (§3.1, Ec. 1). El paper ataca dos problemas concretos
de los modelos MIL profundos para WSI (§1):

1. **Bags muy desbalanceados**: en un slide positivo, solo una fracción
   pequeña de parches es realmente positiva. El max-pooling clásico
   desplaza la frontera de decisión respecto al caso fully-supervised y
   sobre-ajusta (Fig. 1, §1).
2. **Extracción de features sub-óptima**: entrenar el CNN extractor
   end-to-end es prohibitivo en memoria con bags grandes; usar un CNN
   fijo da features pobres (§1).

---

## 2. Contribución principal

Tres componentes (§1, abstract):

1. **Aggregator MIL dual-stream nuevo** — modela las **relaciones entre
   instancias** con una medición de distancia entrenable (*masked
   non-local operation*). Es la contribución arquitectónica central y la
   única que nos interesa para el Objetivo 3.
2. **Self-supervised contrastive learning (SimCLR)** para entrenar el
   extractor de features sin etiquetas — mitiga el costo de memoria.
3. **Fusión piramidal multiescala** (20× + 5×) con atención
   localmente-restringida.

> **Para OncoMets solo el componente 1 es relevante.** El 2 ya está
> cubierto (y superado) por las features CONCH; el 3 exige rehacer la
> extracción. Ver [`03_comparacion_clam_dsmil.md`](03_comparacion_clam_dsmil.md)
> y [`04_riesgos_y_preguntas_reunion.md`](04_riesgos_y_preguntas_reunion.md).

Resultado declarado (abstract, §1): la precisión de DSMIL supera a otros
modelos MIL recientes en **≥2,3 %** y queda a **<2 %** de los métodos
fully-supervised.

---

## 3. Arquitectura dual-stream (§3.2, Fig. 3)

Bag de N parches `B = {x_1, ..., x_N}`. Un extractor `f` proyecta cada
parche a un embedding `h_i = f(x_i) ∈ R^{L×1}` (§3.2). Los dos streams
operan sobre los `h_i`.

### Stream 1 — instance classifier + max-pooling (Ec. 3)

Clasificador de instancia lineal sobre cada embedding, seguido de
max-pooling sobre los scores:

```
c_m(B) = g_m(f(x_1), ..., f(x_N)) = max{ W_0 h_0, ..., W_0 h_{N-1} }
```

- `W_0` es un vector de pesos (clasificador de instancia).
- El max-pooling **determina la instancia crítica**: el parche con el
  score más alto. Su embedding se denota `h_m`.
- Max-pooling es permutation-invariant → este stream cumple la Ec. 2.

### Stream 2 — masked non-local / dual aggregator (Ec. 4–7)

Toma la instancia crítica `h_m` del Stream 1 como **query de referencia**
y mide la distancia de cada parche a ella.

Cada `h_i` se transforma en una **query** `q_i` y un **information
vector** `v_i` (Ec. 4):

```
q_i = W_q h_i ,   v_i = W_v h_i ,   i = 0, ..., N-1
```

con `W_q`, `W_v` matrices de peso. Se define una **medición de distancia
entrenable** `U` entre cada instancia y la crítica (Ec. 5):

```
U(h_i, h_m) = exp(<q_i, q_m>) / Σ_{k=0}^{N-1} exp(<q_k, q_m>)
```

`<·,·>` = producto interno. Es un **softmax de los productos internos de
cada query contra la query de la instancia crítica `q_m`**. Garantiza que
los pesos de atención sumen 1 sin importar el tamaño del bag.

El **bag embedding** es la suma ponderada de los information vectors,
con los pesos de distancia (Ec. 6):

```
b = Σ_{i=0}^{N-1} U(h_i, h_m) v_i
```

El **bag score** del stream 2 (Ec. 7):

```
c_b(B) = g_b(f(x_1),...,f(x_N)) = W_b Σ_i U(h_i,h_m) v_i = W_b b
```

`W_b` = vector de pesos del clasificador de bag.

### Fusión de los dos streams (Ec. 8)

El score final del bag es el **promedio** de los dos streams:

```
c(B) = 0.5 ( g_m(f(x_i),...) + g_b(f(x_i),...) )
      = 0.5 ( W_0 h_m  +  W_b Σ_i U(h_i,h_m) v_i )
```

### Caso multi-clase (§3.2, párrafo tras Ec. 8)

DSMIL maneja MIL multi-clase haciendo el max-pooling de scores y
calculando pesos de atención **para cada clase por separado**. El bag
embedding pasa a ser una **matriz `b ∈ R^{L×C}`** (C = nº de clases) y la
última capa fully-connected tiene C canales de salida.

> **Detalle crítico**: "clase" en DSMIL es multi-**label** (una rama
> sigmoide independiente por clase), no multi-**class** mutuamente
> excluyente con softmax. Esto choca con `CLAM_MB`. Ver
> [`03_comparacion_clam_dsmil.md`](03_comparacion_clam_dsmil.md) §subtyping
> y [`04_riesgos_y_preguntas_reunion.md`](04_riesgos_y_preguntas_reunion.md) §B.

### Por qué "non-local" y por qué funciona en focal (§3.2)

- Es similar a self-attention, pero el *matching* query-key se hace
  **solo entre la instancia crítica y las demás** (no todas-contra-todas).
  Además la query se compara contra otras *queries*, no se aprende un
  vector key separado.
- El producto interno mide similitud: instancias más parecidas a la
  crítica reciben más atención. En una tarea **focal** (un único patrón
  positivo en la WSI), la atención se concentra alrededor del parche
  crítico.
- Como la instancia crítica no depende del orden y `U` es simétrica, el
  bag embedding `b` es permutation-invariant (cumple Ec. 2). Tiene
  **forma constante sin importar el tamaño del bag**.

---

## 4. Loss function

> **El paper NO enuncia la loss de entrenamiento como ecuación.** La
> Ec. 8 da el *score* final, no la *loss*. La loss real se deriva del
> código `[CÓDIGO]` (`train_tcga.py:69-71`, ver
> [`02_codigo_oficial_mapeo.md`](02_codigo_oficial_mapeo.md)).

La loss de DSMIL `[CÓDIGO]`:

```
bag_loss = BCEWithLogitsLoss(bag_prediction, bag_label)   # stream 2
max_loss = BCEWithLogitsLoss(max_prediction, bag_label)   # stream 1
loss     = 0.5 * bag_loss + 0.5 * max_loss
```

- `bag_prediction` = score del stream 2 (dual aggregator).
- `max_prediction` = max sobre N de los scores de instancia (stream 1).
- Ambos streams se supervisan **por separado** con la etiqueta del bag;
  la loss NO se computa sobre el score promediado de la Ec. 8.
- Cada término es **BCE** (Binary Cross-Entropy con logits) → sigmoide
  por clase → DSMIL es **multi-label**.

### Comparación con la loss de CLAM

| | DSMIL | CLAM (OncoMets) |
|---|---|---|
| Loss compuesta | `0.5·BCE(bag) + 0.5·BCE(max)` | `bag_weight·L_bag + (1−bag_weight)·L_inst` |
| Peso | fijo 0.5 / 0.5 `[CÓDIGO]` | `bag_weight` = 0.7 por defecto |
| L_bag | BCE sobre el bag score (stream 2) | CrossEntropy (`--bag_loss ce`) sobre logits multi-clase |
| L "instance" | BCE sobre el **max** de scores de instancia | SmoothTop1SVM (`--inst_loss svm`) sobre top-B/bottom-B parches con pseudo-labels |
| Naturaleza | multi-label (sigmoide) | multi-class (softmax) |

Diferencia conceptual clave: la "supervisión de instancia" de CLAM es un
**clustering** sobre los 2B parches de mayor/menor atención con
pseudo-etiquetas; la de DSMIL es simplemente **BCE sobre el parche de
score máximo**. Detalle en [`03_comparacion_clam_dsmil.md`](03_comparacion_clam_dsmil.md).

---

## 5. Self-supervised pretraining (SimCLR) — CRÍTICO para nosotros

§3.2 ("Self-Supervised Contrastive Learning of WSI Features") y §4.3
(ablation):

- El extractor `f` se entrena con **SimCLR** (contrastive learning) sobre
  los parches de las WSI, sin etiquetas. Backbone **ResNet18**
  (Implementation Details, §4). Tras converger, el extractor se **congela**
  y se usa para computar las features de los parches.
- Feature dim resultante = **512** (salida de ResNet18).

**Qué tan crítico es** (ablation §4.3, Tabla 3):

- Para bags **desbalanceados** (Camelyon16): las features contrastivas dan
  **≥16 % más accuracy** que entrenar el extractor end-to-end con
  max-pooling.
- Para bags **balanceados** (TCGA-lung): las features contrastivas son
  comparables a las "patch-based" (supervisadas) pero aún **>14 % mejores**
  que el end-to-end max-pooling.
- Conclusión del paper: el contrastive learning es **una pieza grande**
  del resultado, no un detalle.

> **Implicación para OncoMets — punto clave.** Nosotros **NO hacemos
> SimCLR**: usamos features **CONCH** (foundation model vision-language de
> patología, 512-dim, ya extraídas). La pregunta no es "¿perdemos el
> componente 2 de DSMIL?" sino "¿CONCH es un sustituto igual o mejor del
> extractor SimCLR?". CONCH es un extractor mucho más potente que un
> ResNet18-SimCLR entrenado por dataset. La hipótesis razonable es que
> CONCH **satisface y supera** el rol del componente 2. Pero el paper
> nunca evaluó DSMIL sobre features de un foundation model → esto es un
> supuesto, no un hecho verificado. Ver
> [`04_riesgos_y_preguntas_reunion.md`](04_riesgos_y_preguntas_reunion.md) §A.

---

## 6. Datasets de evaluación y régimen de datos (§4)

Preprocesamiento común (§4, "Experiment Setup"): cada WSI se parte en
parches **224×224 sin solape**, a magnificaciones **20× y 5×**. Parches de
fondo (entropía < 5) se descartan. Mejores resultados a 20×.

### Camelyon16 (§4.1) — binario, desbalanceado

- Detección de metástasis en cáncer de mama. **271 train + 129 test**.
- ~3,2 M parches a 20×, ~0,25 M a 5×. **Promedio ~8.000 parches/bag a 20×**
  (~625 a 5×).
- Región tumoral **< 10 %** del área de tejido por slide → bags
  **muy desbalanceados** (foco análogo al de MicroCalcificaciones).
- Tiene anotación pixel-level → permite evaluar localización (FROC).

### TCGA Lung Cancer (§4.2) — binario, balanceado

- Subtipos LUAD vs LUSC. **840 train + 210 test** (1054 slides, 4
  corruptos descartados).
- ~5,2 M parches a 20×, ~0,36 M a 5×. **Promedio ~5.000 parches/bag a 20×**
  (~350 a 5×).
- Región tumoral **> 80 %** por slide → bags **balanceados**.

### Datasets MIL clásicos (§4.3, Tabla 5)

MUSK1, MUSK2, FOX, TIGER, ELEPHANT — vectores de feature ya dados, sirven
para evaluar el aggregator puro sin extractor. 10-fold CV, 5 corridas.

### Métricas reportadas (cita literal)

| Dataset | Modelo | Accuracy | AUC | FROC |
|---|---|---|---|---|
| Camelyon16 (Tabla 1) | DSMIL single-scale | 0,8682 | **0,8944** | 0,4296 |
| Camelyon16 (Tabla 1) | DSMIL-LC multiescala | 0,8992 | **0,9165** | 0,4371 |
| Camelyon16 (Tabla 1) | ABMIL [22] | 0,8450 | 0,8653 | 0,4056 |
| Camelyon16 (Tabla 1) | Max-pooling | 0,8295 | 0,8641 | 0,3313 |
| Camelyon16 (Tabla 1) | Fully-supervised | 0,9147 | 0,9362 | 0,5254 |
| TCGA-lung (Tabla 2, SimCLR feats) | DSMIL single-scale | 0,9190 | **0,9633** | — |
| TCGA-lung (Tabla 2, SimCLR feats) | DSMIL-LC multiescala | 0,9286 | 0,9583 | — |

> El README del repo oficial reporta además, con los *updates 2024*
> (5-fold-CV): Camelyon16 Acc 94,9 % / AUC 0,961; TCGA-lung Acc 93,78 % /
> AUC 0,981. Son **mejores** que la Tabla del paper — el código actual no
> reproduce literal la tabla del paper. Ver
> [`02_codigo_oficial_mapeo.md`](02_codigo_oficial_mapeo.md) §discrepancias.

DSMIL es además, según §4.3 (Tabla 5), el mejor aggregator en 4 de 5
datasets MIL clásicos (MUSK1 0,932 / MUSK2 0,930 / FOX 0,729 /
ELEPHANT 0,925; TIGER 0,869, donde DP-MINN gana con 0,897).

---

## 7. Hiperparámetros clave (§4, "Implementation Details")

| Hiperparámetro | Valor (paper) | Nota |
|---|---|---|
| Feature dim `L` | 512 | salida ResNet18 |
| Optimizer (MIL) | Adam | |
| Learning rate (MIL) | **0,0001 constante** | ⚠ el código usa cosine annealing — discrepancia, ver `02_` |
| Mini-batch (MIL) | **1 bag** | un slide a la vez |
| Optimizer (SimCLR) | Adam, lr inicial 0,0001, cosine annealing sin warm restarts | |
| Mini-batch (SimCLR) | 512 | recomendado ≥512 para buenas features |
| Backbone CNN | ResNet18 | tanto para MIL como SimCLR |
| Magnificación | 20× (single-scale); 20×+5× (multiescala) | |
| Parche | 224×224 sin solape | fondo entropía<5 descartado |

Lo que el paper **no** especifica y sí está en el código `[CÓDIGO]`:
`num_epochs`, early stopping, weight decay, betas de Adam, dropout,
inicialización de pesos, scheduler exacto. Todo eso en
[`02_codigo_oficial_mapeo.md`](02_codigo_oficial_mapeo.md) §7.

---

## 8. Ablations reportadas (§4.3)

- **Contrastive learning** (Tabla 3): aporta ≥16 % accuracy en bags
  desbalanceados, >14 % en balanceados, frente a end-to-end max-pooling.
  Es el componente con mayor contribución medida.
- **Atención multiescala** (Tabla 4): +3 % accuracy sobre single-scale;
  dos niveles (5×+20×) mejor que tres (1,25×+5×+20×) por +1,6 % acc /
  +1,3 % AUC. El paper conjetura que la escala 1,25× es demasiado gruesa
  y "ensucia" los vectores fusionados.
- **Aggregator DSMIL puro** (Tabla 5, datasets MIL clásicos): supera a
  los bloques non-local NL y ANL en promedio **+3 %**, y a ABMIL.

> El paper **no** reporta un ablation que aísle "Stream 1 solo" vs
> "Stream 2 solo" vs "fusión". La contribución relativa de cada stream
> de la Ec. 8 no está cuantificada. → pregunta abierta, ver `04_` §B.

---

## 9. Limitaciones — reconocidas y observadas

El paper **no tiene una sección explícita de "Limitations"**. Lo que
sigue se separa en lo que los autores reconocen y lo que se observa.

**Reconocido por los autores** (§5, "Conclusion and Future Work"):

- Las estrategias self-supervised actuales **no están adaptadas a las
  características de la histopatología** — proponen diseñarlas como trabajo
  futuro (implica que SimCLR genérico es subóptimo para WSI).
- DSMIL **no modela relaciones espaciales / macroescala**: ignora las
  coordenadas de los parches. Lo dejan como trabajo futuro.

**Observado (no enunciado como limitación por los autores)**:

- Queda ~2 % por debajo del fully-supervised en Camelyon16 (Tabla 1).
- Evaluado **solo en problemas binarios** (Camelyon16; TCGA-lung son 2
  subtipos sin clase negativa). **No hay evaluación en multi-clase
  desbalanceado** tipo MicroCalcificaciones. → riesgo, ver `04_` §A.
- La instancia crítica se elige por `argmax` (Ec. 3): operación no
  diferenciable salvo por el índice ganador. El paper no discute la
  estabilidad de entrenamiento que esto implica. → riesgo, ver `04_` §B.

---

## Afirmaciones a verificar contra el paper (pendientes)

Ninguna sustancial: el paper se leyó completo (8 pp.). Las afirmaciones
marcadas `[CÓDIGO]` en este documento provienen del repo oficial y se
contrastan en [`02_codigo_oficial_mapeo.md`](02_codigo_oficial_mapeo.md);
no contradicen al paper, lo complementan (defaults, scheduler, init).
