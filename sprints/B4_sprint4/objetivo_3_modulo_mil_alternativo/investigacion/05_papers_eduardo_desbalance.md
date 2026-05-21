# 05 — Papers de Eduardo: ¿atacan el desbalance de microcalcificaciones?

> **Objetivo 3, Sprint B4 — investigación complementaria.**
> Eduardo aportó 3 papers el 21 may 2026 (ver `papers/README.md`)
> "para atacar el desbalance de clases de `microcalcificaciones_pth`".
> Este documento los lee a fondo y evalúa, paper por paper, si alguna
> idea aplica al problema real — siguiendo la regla 9 de `CLAUDE.md`
> ("argumento antes de código": hipótesis + métrica de éxito explícitas).
>
> **Insumo para la reunión con Sebastián y Eduardo.** Sesión read-only:
> cero GPU, cero SLURM, cero modificación de `clam_environ/`.
>
> Fuentes leídas completas:
> - `papers/2001.06782v4.pdf` — Yu et al., *Gradient Surgery for
>   Multi-Task Learning* (PCGrad), NeurIPS 2020.
> - `papers/2512.18734.pdf` — Chen & Xu, *Breast Cancer Recurrence Risk
>   Prediction Based on MIL*, 2025.
> - `papers/electronics-13-04445.pdf` — Liu et al., *Dual-Attention MIL
>   Framework for Pathology WSI* (DAMIL), Electronics 2024.
>
> Conecta con: `objetivo_1_baseline/resultados.md` (hallazgo del
> multi-label aplastado), `investigacion/00_README.md`–`04_` (DSMIL),
> `alternativas_consideradas.md`.

---

## TL;DR — veredicto por paper

| Paper | Qué es | ¿Ataca el desbalance? | Recomendación |
|---|---|---|---|
| **PCGrad** | Cirugía de gradientes para multi-task learning | **Indirecto pero central**: hace entrenable la reformulación multi-label | **SÍ, condicional** a adoptar la reformulación en 3 binarios con backbone compartido |
| **Recurrence Risk MIL** (Chen & Xu) | Comparación aplicada de 3 MIL en dataset chico y desbalanceado | **No aporta técnica nueva** — pero es la mejor *evidencia* de que el kit anti-desbalance falla con n≈20 | **SÍ como evidencia + toolkit** (focal loss, label smoothing); **NO** como "módulo a adoptar" |
| **DAMIL** (dual-attention) | Mejora del agregador MIL (atención canal + espacial) | **No.** Ataca dilución de instancias en el bag, no desbalance de clases | **NO** para el desbalance; **CONDICIONAL** como candidato de módulo a comparar con DSMIL |

**Conclusión de una línea**: el desbalance **no es un problema de
arquitectura** — es un problema de *formulación del problema* (multi-label
aplastado) + *datos*. La dirección correcta es **reformular en 3 tareas
binarias + PCGrad**, no cambiar el módulo MIL. DSMIL y DAMIL son un eje
distinto (representación), no la solución al desbalance.

---

## 0. El problema que hay que atacar (recap desde `resultados.md`)

Antes de juzgar los papers hay que tener claro **qué** desbalance se
ataca. El baseline B=8 (job 4098) dejó dos hechos:

1. **Desbalance de datos a nivel dataset.** La clase triple
   `en_carcinoma_invasivo-en_cdis-en_tejido_no_neoplasico` tiene **6
   slides en todo el dataset** (3072). Cuatro de las 8 clases tienen
   **1 sola muestra** en val y en test.
2. **Estructura multi-label aplastada.** Las 8 clases NO son categorías
   independientes: son las **7 combinaciones no vacías de 3 tejidos**
   {carcinoma invasivo, CDIS, tejido no neoplásico} + `no_identificado`.

Hay que separar **dos problemas distintos** que la palabra "desbalance"
mezcla:

- **(P1) Escasez real de datos.** Algunas combinaciones de tejido son
  clínicamente raras. Ningún truco de loss ni de arquitectura *fabrica*
  información que no está en los datos. Esto es un techo duro.
- **(P2) Escasez fabricada por la codificación.** Aplastar un problema
  multi-etiqueta en clases-combinación mutuamente excluyentes
  **manufactura** clases ultra-raras. La clase triple tiene 6 slides
  *porque exigimos que las 3 etiquetas coincidan exactamente*. Esto **sí**
  se ataca: des-aplastando.

### El des-aplastado, en números

Reformular como **3 tareas binarias** — `¿microcalcificación en
carcinoma invasivo?`, `¿en CDIS?`, `¿en tejido no neoplásico?` — disuelve
las clases-combinación. Cada slide con varias etiquetas cuenta como
positivo en **varias** tareas:

```
              clase-combinación (8)          →   3 tareas binarias
                                                 A:carc  B:cdis  C:tejido
  en_carcinoma_invasivo            38              +38      .       .
  en_carcinoma_invasivo-en_cdis    11              +11     +11      .
  en_carc-en_cdis-en_tejido         6 (triple)     + 6     + 6     + 6
  en_carcinoma_invasivo-en_tejido  13              +13      .      +13
  en_cdis                          89               .     +89      .
  en_cdis-en_tejido                15               .     +15     +15
  en_tejido_no_neoplasico         161               .       .    +161
  no_identificado                2739               .       .       .
  ----------------------------------------------------------------------
  POSITIVOS POR TAREA BINARIA                       68     121     195
```

La clase de **6 slides desaparece**: esos 6 slides pasan a ser positivos
en las 3 tareas. El "rincón" más raro del problema pasa de **6** muestras
a **68 / 121 / 195** positivos repartidos. No es magia — es contar bien:
hay **333 slides con al menos una localización** (3072 − 2739) que
generan **384 etiquetas-tarea positivas**. La reformulación recupera la
señal que el aplastado tiraba.

Tasa de positivos por tarea tras reformular: A ≈ 2,2 % (68/3072),
B ≈ 3,9 % (121), C ≈ 6,3 % (195). **Sigue habiendo desbalance** (P1 no
se va), pero cada tarea pasa de "imposible" (clases de n=1 en val/test) a
"difícil pero medible": con un split estratificado 80/10/10, val/test
tendrían ≈ 7 / 12 / 20 positivos por tarea — un AUC y un balanced
accuracy con sentido, no ruido de 1 muestra.

> **Precondición clínica (pregunta para la reunión).** Todo esto asume
> que `no_identificado` (2739 slides, 89 %) es un **negativo limpio** para
> las 3 tareas — es decir, "no hay microcalcificación". Si significara
> "hay microcalcificación pero sin localizar", esos 2739 slides **no**
> son negativos válidos y habría que excluirlos o tratarlos como un 4.º
> estado. Esto **cambia toda la reformulación** y está sin resolver
> (`resultados.md`, decisión pendiente; `current.md`).

Con esto fijado, se evalúan los papers.

---

## 1. PCGrad — *Gradient Surgery for Multi-Task Learning* (Yu et al., NeurIPS 2020)

### 1.1 Idea central

**Multi-task learning (MTL)** = entrenar un modelo con parámetros
compartidos para resolver varias tareas a la vez. El problema: cada tarea
`i` produce un gradiente `g_i` sobre los parámetros compartidos, y esos
gradientes pueden **apuntar en direcciones opuestas**. El paper define
dos gradientes como **conflictivos** cuando `cos(g_i, g_j) < 0`
(Definición 1).

El paper identifica una **"tríada trágica"** (§2.2) — la combinación que
degrada de verdad el MTL: (a) gradientes conflictivos, (b) gradientes
**dominantes** (una tarea con gradiente mucho más grande aplasta a las
otras), y (c) **alta curvatura** del paisaje de optimización. Bajo esa
tríada, promediar gradientes (el MTL ingenuo) sobre-estima la mejora de
la tarea dominante y sub-estima el daño a la dominada.

**PCGrad** (Projecting Conflicting Gradients, Algoritmo 1) es la
solución, y es minimalista: si `g_i · g_j < 0`, **se proyecta `g_i` sobre
el plano normal de `g_j`**:

```
  g_i  ←  g_i  −  (g_i · g_j / ‖g_j‖²) · g_j        si  g_i · g_j < 0
  g_i  ←  g_i                                       si  no conflictan
```

Se repite para todos los pares de tareas en orden aleatorio. Propiedades
clave: **es model-agnostic** (solo modifica el gradiente antes de pasarlo
al optimizador), **no añade hiperparámetros**, y **se combina con
cualquier arquitectura** y cualquier optimizador (Adam, SGD).

Evidencia más relevante para nosotros: el experimento **CelebA** (Tabla 3,
§5.1). CelebA es un problema **multi-etiqueta** (40 atributos de cara);
los autores lo convierten en un **MTL de 40 tareas binarias** y PCGrad
mejora sobre el estado del arte. **Es exactamente el patrón
multi-label → multi-task que propone `resultados.md`** — solo que con 3
tareas en vez de 40.

### 1.2 Aplicabilidad al desbalance de microcalcificaciones

La conexión es directa y **es la pieza que faltaba** para la propuesta de
reformulación:

- La reformulación en 3 binarios (§0) **es** un problema de multi-task
  learning. La señal común a las 3 tareas es *"¿este parche tiene un foco
  de microcalcificación?"*; lo que cambia entre tareas es el **contexto
  de tejido**. Eso pide un **backbone CLAM compartido** (encoder de
  features + red de atención) con **3 cabezas binarias** — para aprender
  *una vez* dónde están las microcalcificaciones y *tres veces* en qué
  tejido. Es el caso de uso canónico de MTL: tareas que comparten
  estructura.
- Backbone compartido ⇒ las 3 tareas escriben gradiente sobre los mismos
  parámetros ⇒ **puede haber conflicto de gradientes**. Y las 3 tareas
  tienen tasas de positivos muy distintas (2,2 % / 3,9 % / 6,3 %) y
  dificultad distinta ⇒ **magnitudes de gradiente distintas** ⇒ riesgo de
  *gradiente dominante*. Es decir: la reformulación cae de lleno en las
  condiciones (a) y (b) de la tríada trágica. PCGrad es la respuesta
  diseñada para exactamente eso.
- **Límite honesto — qué NO hace PCGrad.** PCGrad ataca la *interferencia
  de optimización*, no el desbalance de clases. **No fabrica datos** para
  la tarea A (68 positivos). PCGrad hace que el entrenamiento conjunto de
  las 3 tareas **no sea destructivo**; el desbalance *dentro* de cada
  tarea binaria sigue necesitando su propio tratamiento (ver §2:
  weighted sampling / focal loss). PCGrad y el tratamiento de desbalance
  intra-tarea son **ortogonales y se suman**.
- Costo de adopción: **mínimo**. El loop de training de CLAM
  (`utils/core_utils.py`) ya calcula losses y gradientes; PCGrad es una
  función que intercepta los gradientes por-tarea antes del
  `optimizer.step()`. Cero dependencias nuevas sobre `clam_latest`. Cero
  cambio de arquitectura del modelo (solo del paso de optimización).
  Código oficial de referencia: `github.com/tianheyu927/PCGrad`.

### 1.3 Recomendación — **SÍ, condicional**

**Condicional a** adoptar la reformulación multi-label con **backbone
compartido + 3 cabezas** (no a 3 modelos binarios independientes). El
matiz importa:

- **3 modelos binarios independientes** (opción simple): no hay
  parámetros compartidos ⇒ no hay conflicto de gradientes ⇒ PCGrad **no
  aplica ni hace falta**. Es el baseline trivial para *validar la
  reformulación* — 3 corridas de `main.py` con 3 CSVs binarios.
- **1 backbone compartido + 3 cabezas** (opción con transferencia): más
  eficiente en datos (la señal de detección se aprende una vez, crítico
  cuando los positivos son pocos) — y **aquí PCGrad gana su lugar**.

Recomendación operativa: **validar primero la reformulación con 3
binarios independientes** (barato, sin tocar el modelo); **si se decide
mover a backbone compartido para ganar eficiencia de datos, PCGrad entra
como la pieza de optimización** que evita que las 3 tareas se peleen.

> **Argumento antes de código (regla 9).**
> **Hipótesis PCGrad**: con backbone CLAM compartido + 3 cabezas
> binarias, los gradientes de las 3 tareas conflictúan (`cos < 0` en una
> fracción no trivial de los pasos) por sus tasas de positivos y
> dificultad dispares; PCGrad mejora el **balanced accuracy promedio de
> las 3 tareas** frente al multi-task ingenuo (suma de losses), a igual
> backbone y épocas.
> **Métrica de éxito**: (1) balanced accuracy promedio de las 3 tareas,
> PCGrad vs suma-ingenua — éxito si Δ ≥ +0,05 a favor de PCGrad;
> (2) loguear el **% de pasos con `cos(g_i,g_j) < 0`** — si el conflicto
> es ~0 %, PCGrad no aplica y la hipótesis se cae *antes* de invertir
> tiempo. Esa es la verificación falsable barata.

---

## 2. *Breast Cancer Recurrence Risk Prediction Based on MIL* (Chen & Xu, 2025)

### 2.1 Idea central

No es un paper de método — es un **estudio aplicado comparativo**.
Predicen el riesgo de recurrencia de cáncer de mama a 5 años en **3
niveles** (bajo / medio / alto) desde WSIs H&E, y comparan 3 frameworks
MIL: un **CLAM-SB modificado**, un **ABMIL** custom, y un
**ConvNeXt-MIL-XGBoost**.

El parecido con OncoMets es casi un espejo, y por eso el paper es
valioso:

- Dataset **chico**: 210 pacientes. **Desbalance severo**: la clase
  media es **21/210 ≈ 10 %**.
- Features extraídas con **foundation models** — **UNI y CONCH** (CONCH
  es el mismo extractor que usa OncoMets).
- Mejor resultado: el **CLAM-SB modificado**, AUC media **0,836**,
  accuracy **76,2 %** en 5-fold CV.

Su **kit anti-desbalance** (§3.5.1) — relevante porque es transferible:

- **Focal Loss** con peso de clase alto `α = 3.0` en la clase minoritaria
  y un parámetro de foco `γ` que **baja el peso de los ejemplos
  bien clasificados** → el modelo se concentra en los casos difíciles.
- **Label smoothing** `ε = 0.1` (etiquetas one-hot → distribución suave)
  para mejorar calibración y no sobre-ajustar a las pocas muestras de la
  clase media.
- **Dropout agresivo e independiente** en encoder, atención y
  clasificador.
- Variante ABMIL: **Cross-Entropy ponderada**. Variante
  ConvNeXt-MIL-XGBoost: focal loss + XGBoost (robusto a desbalance).

### 2.2 Aplicabilidad — el hallazgo más útil del paper

El valor del paper **no es una técnica nueva**. Es la **evidencia
empírica más fuerte de los 3 papers** de que el desbalance no se arregla
con trucos de loss/arquitectura cuando la clase rara tiene ~20 muestras:

- **Pese a todo el kit** (focal loss `α=3`, label smoothing, dropout
  agresivo, CE ponderada, XGBoost), el rendimiento en la clase media se
  quedó pobre: el CLAM-SB modificado acertó **1 de 2** casos medios en su
  mejor fold; el ABMIL custom dio **0 % en la clase media** (fallo
  total).
- Los autores lo atribuyen, sin rodeos, al tamaño de muestra: *"the small
  sample size (n=21) was likely insufficient for learning a robust
  feature representation"* (§5).
- Y la frase de la discusión que conviene llevar a la reunión: *"MIL is
  not a panacea; its success is intrinsically linked to the distinctness
  of the underlying histological patterns and **the balance of the
  training data**"* (§5).

Esto **valida directamente** dos hallazgos de OncoMets:

- `resultados.md` Hallazgo 4 — "el dataset grande no ayuda al
  desbalance". El paper lo confirma desde el otro lado: el problema no es
  el tamaño total del dataset, es el `n` de la clase rara.
- El régimen de evaluación roto (`resultados.md`, hallazgo central). El
  paper hace lo mismo que recomendamos: reporta la clase media "con
  cautela por el bajo número de muestras anotadas" y mira por-clase, no
  solo el promedio agregado.

Además, dato lateral útil para el Objetivo 3: en este estudio el
**CLAM-SB modificado le ganó** al ABMIL custom y al ConvNeXt-XGBoost.
Es evidencia *suave* (un solo dataset, binario-adyacente) de que un CLAM
bien afinado es competitivo — no descarta DSMIL/DAMIL, pero quita urgencia
a "hay que cambiar de módulo sí o sí". (OncoMets usa **CLAM_MB**, no
CLAM_SB; el matiz no cambia la lectura.)

### 2.3 Recomendación — **SÍ como evidencia y como toolkit; NO como "módulo"**

- **NO hay un módulo nuevo que adoptar** acá. No es un paper de
  arquitectura.
- **SÍ usarlo como evidencia en la reunión**: es un precedente cuasi-
  espejo (CLAM + CONCH + dataset chico desbalanceado de patología) que
  demuestra que el kit anti-desbalance por fuerza bruta **no rescata una
  clase de n≈20**. Es el respaldo bibliográfico de por qué hay que
  reformular el problema (§0) en vez de solo apretar la loss.
- **SÍ tomar prestado el toolkit** — focal loss (`α` alto en la clase
  minoritaria) + label smoothing — como **tratamiento del desbalance
  intra-tarea** *después* de reformular. En la tarea A reformulada
  (68 positivos, 2,2 %) el desbalance sigue ahí; focal loss + weighted
  sampling es el tratamiento razonable. **Pero con expectativas
  calibradas por este mismo paper**: ayuda en el margen, no hace milagros.

> **Argumento antes de código (regla 9).**
> **Hipótesis**: añadir focal loss (`α` alto en el positivo) sobre cada
> tarea binaria reformulada mejora el **recall de la clase positiva** sin
> hundir la precisión, frente a CE + `--weighted_sample` solo.
> **Métrica de éxito**: balanced accuracy y recall del positivo por
> tarea; éxito si recall del positivo sube ≥ +0,05 con caída de precisión
> ≤ 0,05. Subordinado a la reformulación: focal loss sobre las 8 clases
> aplastadas es justo lo que el paper muestra que **no** alcanza.

---

## 3. DAMIL — *Dual-Attention MIL Framework for Pathology WSI* (Liu et al., Electronics 2024)

### 3.1 Idea central

DAMIL es una **mejora del agregador MIL**. La matriz de features de un
WSI, `F ∈ ℝ^{N×C}` (N parches × C canales), se trata como un mapa de
features 1D y se le aplica **doble atención** estilo CBAM:

- **Atención de canal** `H_c(F)` — qué **dimensiones de feature** son las
  más informativas en todo el bag (eq. 9: MLP sobre avg-pool + max-pool).
- **Atención espacial** `H_s(F)` — qué **instancias/parches** importan
  (eq. 10).
- Se aplican en **serie, canal → espacial**, con conexión residual
  `F₃ = F₂ + F` (eq. 6–8). La ablación (Tabla 6) confirma que el orden
  canal→espacial es el mejor.

Qué problema resuelve, según el paper: que las instancias positivas
(< 10 % de un bag positivo) se **diluyan** al agregar, y el sobreajuste
bajo supervisión débil. Captura relaciones **inter-instancia e
inter-canal** que un agregador de atención simple ignora.

Validación: **Camelyon16** y **TCGA-Lung** — y aquí está el punto
crítico: **ambos son binarios** (normal vs tumor; LUAD vs LUSC) y
razonablemente balanceados. DAMIL le gana a ABMIL, DSMIL, CLAM y TransMIL
en ACC/AUC/F1 (Tablas 1–3).

### 3.2 Aplicabilidad al desbalance — baja y mal encuadrada

Hay que ser preciso con qué "desbalance" resuelve DAMIL:

- El "desbalance" del que habla DAMIL es **dilución de instancias dentro
  de un bag** — los < 10 % de parches tumorales que se pierden en el
  pooling. Es un desbalance **intra-bag, a nivel de instancia**.
- El desbalance de OncoMets es **a nivel de clase, entre slides** del
  dataset (la clase triple, 6 slides). Es **otro problema**. DAMIL no lo
  toca: una mejor agregación no cambia que solo existan 6 slides de esa
  combinación.
- DAMIL **nunca se evaluó en multi-clase ni en desbalance de clases** —
  exactamente la misma limitación que el `04_` §A.2 marcó como riesgo 🔴
  para DSMIL (H3). El "DAMIL es SOTA" de las Tablas 1–3 es sobre tareas
  binarias balanceadas; **no se traslada** a nuestro régimen.

El **único** ángulo donde DAMIL es genuinamente pertinente: las
microcalcificaciones son focos pequeños, dispersos y escasos dentro de un
WSI de miles de parches — justo el caso de "instancia positiva diluida"
que DAMIL dice atacar. Pero eso mejoraría la **nitidez de detección de la
señal**, no el **desbalance de clases**. Es un argumento para DAMIL como
*módulo de representación*, no como solución al desbalance.

### 3.3 Recomendación — **NO para el desbalance; CONDICIONAL como candidato de módulo**

- **NO** es una respuesta al desbalance de `microcalcificaciones_pth`.
  Si se presenta así en la reunión, se está vendiendo lo que el paper no
  demuestra.
- **CONDICIONAL como candidato de módulo MIL alternativo** — es decir, en
  el eje del **Objetivo 3**, compitiendo con DSMIL, no con la
  reformulación. DAMIL es otro "swap del bloque de pooling", igual de
  O(N) en memoria que CLAM/DSMIL. Acción concreta: **registrarlo en
  [`../alternativas_consideradas.md`](../alternativas_consideradas.md)
  como 4.º candidato**, con su caveat (validado solo en binario
  balanceado; el orden canal→espacial y la doble atención son su aporte).
  **No desplaza a DSMIL** como propuesta firme del `00_README.md` — el
  argumento focal de DSMIL (atención *relacional* al parche crítico) sigue
  en pie y DSMIL ya tiene scaffolding. DAMIL entra como alternativa
  documentada, no como nueva recomendación.

---

## 4. Cómo encajan los 3 papers: los 4 niveles del stack

El error a evitar es meter los 3 papers en la misma bolsa de "ideas
contra el desbalance". Atacan **niveles distintos** del problema, y solo
dos de ellos tocan el desbalance:

```
  NIVEL                        PIEZA                       ¿DESBALANCE?
  ─────────────────────────────────────────────────────────────────────
  1. Formulación del problema  Reformular 8 clases → 3      SÍ — ataca P2
     (raíz)                    binarias  (resultados.md)    (escasez fabricada)
                                       │
  2. Optimización              PCGrad  (paper 1)            SÍ — hace
                               de-conflicta las 3 tareas    entrenable el nivel 1
                                       │
  3. Loss / muestreo           Focal loss + label smooth.   PARCIAL — desbalance
                               (paper 2) + weighted_sample  intra-tarea (P1), margen
                                       │
  4. Arquitectura / agregador  DSMIL (Obj 3) · DAMIL        NO — eje ortogonal
                               (paper 3)                    (representación)
```

Lectura:

- El **nivel 1** (reformulación) es la **raíz** — no sale de los papers
  de Eduardo, sale de `resultados.md`. Es lo que ataca la escasez
  *fabricada* (P2).
- **PCGrad (nivel 2)** es lo que hace que el nivel 1 **funcione** cuando
  se entrena con backbone compartido. Sin PCGrad, el multi-task ingenuo
  puede auto-sabotearse por conflicto de gradientes.
- El paper de **Chen & Xu (nivel 3)** aporta el toolkit intra-tarea y,
  sobre todo, la **evidencia** de que los niveles 3–4 solos no alcanzan.
- **DSMIL y DAMIL (nivel 4)** son un **eje ortogonal**: cambian *cómo se
  agregan los parches*, no *cómo está planteado el problema*. Pueden
  mejorar la representación, pero **no son la solución al desbalance** —
  y el paper de Chen & Xu lo prueba: cambiar de módulo (CLAM→ABMIL→
  ConvNeXt) no rescató la clase rara.

---

## 5. Conclusión — dirección recomendada para el desbalance

**La pregunta de la reunión era: ¿módulo DSMIL / reformulación
multi-label + PCGrad / dual-attention / combinación?**

Respuesta, con el orden de prioridad:

### Dirección recomendada: reformulación multi-label + PCGrad

1. **Reformular `microcalcificaciones_pth` en 3 tareas binarias**
   (nivel 1). Es la pieza con más impacto y la única que ataca la raíz:
   disuelve la clase de 6 slides en 68/121/195 positivos y arregla el
   régimen de evaluación (cada binario tiene un AUC y un balanced accuracy
   medibles). **Primer paso barato y sin tocar el modelo**: 3 CSVs
   binarios + 3 corridas de `main.py` como 3 modelos independientes — eso
   ya *valida o refuta* la reformulación.
2. **PCGrad** (nivel 2) entra **si y cuando** se pase a un **backbone
   CLAM compartido + 3 cabezas** para ganar eficiencia de datos. Es
   barato, model-agnostic, sin hiperparámetros nuevos, y de-conflicta el
   multi-task. Con verificación falsable previa: medir el % de pasos con
   gradientes en conflicto antes de invertir en él.
3. **Focal loss + label smoothing** (nivel 3, paper Chen & Xu) como
   tratamiento del desbalance que *queda dentro* de cada tarea binaria —
   con expectativas calibradas por ese mismo paper (ayuda en el margen).

### Qué NO hacer

- **No** esperar que cambiar el módulo MIL (DSMIL o DAMIL) resuelva el
  desbalance. Es un eje ortogonal. El paper de Chen & Xu es la evidencia:
  el desbalance sobrevivió a CLAM, ABMIL y ConvNeXt-XGBoost por igual.
- **No** aplicar focal loss / label smoothing sobre las **8 clases
  aplastadas** y esperar que alcance — es exactamente el experimento que
  Chen & Xu muestra que se queda corto con n≈20.
- **No** presentar DAMIL como respuesta al desbalance.

### El Objetivo 3 (DSMIL) se mantiene, pero re-encuadrado

La investigación `00_`–`04_` recomienda DSMIL como módulo MIL alternativo
y esa recomendación **no cambia** — pero queda claro que DSMIL es un eje
**de representación**, decidido por el argumento focal (atención
relacional al parche crítico), **no una solución al desbalance**. Las dos
direcciones son **compatibles y se pueden combinar**: el módulo (CLAM o
DSMIL) y la formulación (8 clases o 3 binarios + PCGrad) son ejes
independientes. La combinación más fuerte a futuro sería *DSMIL como
backbone compartido + 3 cabezas binarias + PCGrad* — pero el orden
sensato es **primero la reformulación** (mayor impacto, menor costo,
ataca la raíz), y el módulo después.

> **Argumento antes de código (regla 9) — la propuesta global.**
> **Hipótesis**: reformular las 8 clases-combinación en 3 tareas binarias
> elimina las clases manufacturadas ultra-raras y produce, por tarea, un
> régimen de evaluación medible; el balanced accuracy por tarea binaria
> supera con holgura el del modelo 8-clases (0,31) porque el modelo deja
> de gastar capacidad separando combinaciones que comparten tejido.
> **Métrica de éxito**: por cada tarea binaria — balanced accuracy y AUC
> en test, **siempre con el `n` por clase**. Umbral: balanced accuracy
> > 0,65 al menos en las tareas B (CDIS) y C (tejido), las de más
> positivos; la tarea A (carcinoma invasivo, 68 pos.) se reporta con
> honestidad sobre su `n`. Comparación contra (i) el baseline trivial por
> tarea y (ii) el modelo 8-clases proyectado a cada eje binario.
> **Precondición**: confirmar con Sebastián que `no_identificado` es un
> negativo limpio (ver §0) — si no lo es, la reformulación se rediseña.

---

## 6. Preguntas nuevas para la reunión

Extienden las 9 de
[`04_riesgos_y_preguntas_reunion.md`](04_riesgos_y_preguntas_reunion.md) §C.

| # | Pregunta | Qué desbloquea |
|---|---|---|
| 10 | ¿`no_identificado` significa "sin microcalcificación" o "con microcalcificación sin localizar"? | **Precondición** de toda la reformulación (§0). Si es lo segundo, los 2739 slides no son negativos limpios. |
| 11 | ¿Se aprueba reformular `microcalcificaciones_pth` en 3 tareas binarias? | Habilita el nivel 1 — la dirección recomendada para el desbalance. |
| 12 | Si se reformula: ¿3 modelos binarios independientes o 1 backbone compartido + 3 cabezas? | Decide si PCGrad entra (solo aplica al backbone compartido). |
| 13 | ¿Eduardo ya tenía pensado un uso concreto de PCGrad / dual-attention, o eran lectura exploratoria? | Evita trabajo duplicado; alinea quién toma qué nivel del stack. |
| 14 | ¿Se registra DAMIL como 4.º candidato de módulo en `alternativas_consideradas.md`? | Cierra el rol de DAMIL: candidato de módulo, no solución al desbalance. |

---

## Anexo — fichas BibTeX-lite

- **PCGrad** — Yu, Kumar, Gupta, Levine, Hausman, Finn. *Gradient
  Surgery for Multi-Task Learning*. NeurIPS 2020. arXiv:2001.06782.
  Código: `github.com/tianheyu927/PCGrad`.
- **Recurrence Risk MIL** — Chen, Xu. *Breast Cancer Recurrence Risk
  Prediction Based on MIL*. 2025. arXiv:2512.18734.
- **DAMIL** — Liu, Li, Hu, Hu. *Dual-Attention Multiple Instance Learning
  Framework for Pathology Whole-Slide Image Classification*.
  Electronics 2024, 13, 4445. doi:10.3390/electronics13224445.
