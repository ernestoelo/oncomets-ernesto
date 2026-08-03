# Los cuatro papers explicados desde cero

> 3-ago-2026. Documento **pedagógico**: explica cómo funciona cada método por dentro,
> construyendo el vocabulario antes de usarlo y con un mini-ejemplo numérico por mecanismo.
>
> **No agrega ninguna afirmación nueva.** Todos los números salen de los estudios ya
> verificados contra los PDF el 2-ago ([`pulearning_estudio.md`](pulearning_estudio.md),
> [`cellvit_estudio.md`](cellvit_estudio.md), [`zoommil_estudio.md`](zoommil_estudio.md),
> [`msclam_estudio.md`](msclam_estudio.md), [`midog_notas.md`](midog_notas.md)). Los ejemplos
> numéricos son **ilustrativos**, construidos acá para que se vea la mecánica, y están
> rotulados como tales.
>
> **Nada de esto está implementado ni pre-registrado.** Regla 9.

---

## 0. Cuál es cuál: los tres documentos de esta carpeta

Hay tres archivos sobre los mismos cuatro papers, y responden preguntas distintas:

| Archivo | Pregunta que responde | Cuándo se usa |
|---|---|---|
| [`papers_mitosis.md`](papers_mitosis.md) (36 KB) | **¿Qué encontramos y con qué evidencia?** Es el entregable largo del encargo del 2-ago: ficha bibliográfica, BibTeX, provenance, inventario de lo descargado, la recomendación con su argumentación completa. | Archivo de referencia. Se consulta, no se lee de corrido. |
| [`hojas_reunion.md`](hojas_reunion.md) (25 KB) | **¿Qué digo el viernes?** Una hoja por paper, ordenada por decisión: qué supervisión exige, qué lo frena, qué prioridad tiene. Lo condensado del anterior. | Se lleva a la reunión con Sebastián del 7-ago. Es exposición. |
| **`papers_explicados.md`** (este) | **¿Cómo funciona por dentro?** Vocabulario, mecanismo, fórmula y ejemplo numérico. | Para entender los métodos, no para decidir ni para presentar. |

Los tres son consistentes entre sí. Si alguna vez divergen, manda `papers_mitosis.md`, que es
el que se escribió con los PDF abiertos.

---

## 1. El vocabulario común, antes de los papers

Cinco términos que los cuatro papers usan y que conviene tener fijos, porque el resto se apoya
en ellos.

**Clasificación, detección y segmentación no son lo mismo.** Sobre la misma imagen:

```
   clasificación   →  "en esta lámina la tasa mitótica es score_3"     (una etiqueta)
   detección       →  "hay una mitosis acá, otra acá, otra acá"        (puntos o cajas)
   segmentación    →  "estos píxeles exactos son el núcleo n° 47"      (máscara por objeto)
```

CLAM hace lo primero. PU learning hace lo segundo. CellViT hace lo tercero. Esa es la mitad
del mapa: los tres papers atacan el mismo problema desde niveles de granularidad distintos.

**MIL (Multiple Instance Learning).** El régimen en el que trabajamos: la etiqueta existe a
nivel de lámina, pero la evidencia está en unos pocos parches y nadie dice cuáles. La analogía
estándar es un llavero: alguien nos dice "este llavero abre la puerta" sin decir qué llave lo
hace. El modelo tiene que aprender a la vez cuál es la llave y qué puerta abre. CLAM, ZoomMIL
y MS-CLAM son todos MIL.

**Supervisión: cuatro grados, y la diferencia entre los dos últimos es la que decide todo acá.**

| Grado | Qué se le da al modelo | Quién lo pide |
|---|---|---|
| Completa | cada objeto anotado, exhaustivamente | (nadie de los cuatro) |
| Mixta | la mayoría solo etiqueta de lámina, unas pocas con anotación exhaustiva | MS-CLAM |
| Débil | solo etiqueta de lámina | CLAM, ZoomMIL |
| **Parcial** | **algunos objetos marcados, y lo no marcado tiene etiqueta desconocida** | **PU learning** |

**Positivos parciales** es lo que tenemos: la lámina 129741, 26 marcas de mitosis, un anotador.
La frase operativa, que se repite en todo este documento, es que **lo no marcado no es
negativo**. Un parche sin marca puede ser tejido sano o puede ser una mitosis que el patólogo
no marcó, y nada en el dato distingue los dos casos.

**Recall, precisión y F1.** Sobre una detección:

- **Recall** = de las mitosis que hay, cuántas encontré. Castiga lo que se me escapa.
- **Precisión** = de las que dije que eran mitosis, cuántas lo eran. Castiga lo que invento.
- **F1** = media armónica de las dos, o sea un resumen que se cae si cualquiera de las dos se
  cae.

Con positivos parciales la precisión **deja de ser medible honestamente**, porque un "falso
positivo" puede ser una célula real sin marcar. Eso no es una sutileza: es la razón por la que
el paper de PU learning elige su hiperparámetro por recall, y es el mismo razonamiento que
nosotros ya habíamos escrito solos el 1-ago.

**µm/px (micrómetros por píxel).** Cuánto tejido real cubre un píxel. Es la unidad honesta
para hablar de escala, porque el rótulo de aumento ("20×", "40×") no significa lo mismo entre
fabricantes. Los números del proyecto: **TCGA 0.2325 µm/px**, **privado 0.465 µm/px**, o sea
que el privado es el doble de grueso. Un núcleo de 8 µm ocupa 34 px en TCGA y 17 px en el
privado, y nada se lo dice al modelo.

---

## 2. PU learning (Zhao et al., MELBA 2022): arreglar la loss cuando faltan anotaciones

> Familia D. Prioridad 1. Es el único cuyo régimen de supervisión es el nuestro.

### 2.1 El término nuevo: PU learning

**PU** = **P**ositive-**U**nlabeled, positivo y no-etiquetado. Es un régimen de aprendizaje
donde el dato viene en dos pilas y **ninguna es la de los negativos**:

```
   pila P   →  ejemplos confirmados positivos          (nuestras 26 marcas)
   pila U   →  todo lo demás, etiqueta DESCONOCIDA     (los otros 4773 parches)
```

La analogía: una lista de clientes confirmados de un negocio. Todo el que no está en la lista
no es "no cliente", es "no sé". Un sistema que trate la lista de no-clientes como verdad
aprende a rechazar clientes reales que simplemente no estaban registrados.

Contra esto, el régimen habitual (**PN**, positivo-negativo) asume que las dos pilas son P y N.
Ese es el supuesto que se rompe con anotación incompleta.

### 2.2 Dónde está el error, concretamente

Un detector tipo Faster R-CNN propone miles de cajas candidatas por imagen y para cada una
decide "mitosis / no mitosis". Su loss de clasificación (ec. 1 del paper) es:

```
L_cls = 1/(Nn+Np) · [ Σ_j H(c_n^j, 0)  +  Σ_i H(c_p^i, 1) ]
        └──────────────────┬─────────┘   └────────┬───────┘
              "esto NO es mitosis"          "esto SÍ es mitosis"
```

`H` es la entropía cruzada, o sea el costo de equivocarse. Los `Np` positivos son las cajas
que solapan mucho con una marca. Los `Nn` negativos son **todo lo demás**.

Ese "todo lo demás" es el problema. El paper lo dice en la pág. 4: *"the regions with no
instances labeled as positive are not necessarily all truly negative"*.

**Mini-ejemplo ilustrativo.** Supongamos 1000 cajas candidatas en una región, de las cuales 40
son mitosis de verdad (el 4 %), y el patólogo marcó 26:

```
   26 cajas  →  marcadas, entran al término "SÍ es mitosis"      gradiente correcto
   14 cajas  →  mitosis reales SIN marcar, entran al término
                "NO es mitosis"                                   gradiente EQUIVOCADO
  960 cajas  →  tejido, entran al término "NO es mitosis"         gradiente correcto
```

Una de cada tres mitosis de la región está empujando al modelo en la dirección contraria. Y no
es ruido aleatorio: son sistemáticamente las mitosis menos evidentes, justo las difíciles.

### 2.3 El arreglo, en una idea

No se puede calcular una esperanza sobre los negativos si no se sabe quiénes son. Pero sí se
puede calcular la misma cantidad **por diferencia**:

```
   riesgo sobre los NEGATIVOS  =  riesgo sobre TODO  −  riesgo sobre los POSITIVOS
                                                        (pesado por el prior π)
```

Las dos cantidades de la derecha son medibles: "todo" son las 1000 cajas y "los positivos" son
las 26 marcadas. El truco entero está ahí. Formalmente es la ec. 4 del paper, que sale de
despejar la densidad de los negativos de la mezcla.

**El prior π** es el único hiperparámetro nuevo: la fracción de cajas candidatas que son
positivas de verdad. En mitosis vive entre **0.02 y 0.05**. En el código público está fijo en
`0.04`.

Hay un segundo detalle, y es la contribución específica del paper para detección. El PU
learning clásico estima "el riesgo sobre todo" usando solo la pila U. En detección eso está
mal, porque P y U salen de la **misma imagen** y sacar los positivos sesga la estimación. Ellos
unen las dos pilas (ec. 6), y muestran que la versión sin unir rinde peor en los 5 folds.

La loss final (ec. 7), término a término:

```
max{ 0,   1/(Nu+Np)·[ Σ_u H(c_u,0) + Σ_p H(c_p,0) ]   −   π/Np · Σ_p H(c_p,0) }
     │    └───────────────────┬──────────────────┘        └────────┬────────┘
     │      "cuánto me cuesta llamar negativo             "lo que de ese costo
     │       a TODO, positivos incluidos"                  corresponde a los positivos,
     │                                                     y hay que devolverlo"
     └─ truncado en cero: la resta puede dar negativo por sobreajuste, y un riesgo
        negativo no tiene sentido
```

**Mini-ejemplo numérico ilustrativo.** Con `Nu = 974`, `Np = 26`, `π = 0.04`, y suponiendo que
el modelo asigna un costo medio de llamar negativo de `H = 0.10` a las no-etiquetadas y
`H = 2.0` a las marcadas (le cuesta caro, porque está seguro de que son mitosis):

```
   término 1  =  (974·0.10 + 26·2.0) / 1000  =  (97.4 + 52) / 1000  =  0.1494
   término 2  =  0.04 · (52/26)              =  0.04 · 2.0          =  0.0800
   loss       =  max(0,  0.1494 − 0.0800)                           =  0.0694
```

La resta le devuelve al modelo, en promedio, el castigo que le habría tocado por las mitosis
escondidas en la pila U. Y si el modelo sobreajusta y ese costo se dispara (por ejemplo
`H = 8.0` sobre las marcadas), la cuenta da `0.3054 − 0.3200 = −0.0146`, negativo, y el
`max(0, ·)` la corta ahí.

### 2.4 Qué consigue

MITOS-ATYPIA-14 (mitosis en mama), 5-fold, anotación incompleta simulada:

| Método | Recall | Precisión | F1 |
|---|---|---|---|
| Baseline (lo no marcado es negativo) | 0.570 | 0.403 | 0.470 |
| BDE (competidor) | 0.598 | 0.427 | 0.496 |
| **Propuesto** | **0.608** | **0.439** | **0.507** |
| *Upper bound* (anotación completa) | 0.613 | 0.461 | 0.523 |

La forma de leerlo: la anotación incompleta abre un hueco de `0.523 − 0.470 = 0.053` de F1, y
el método recupera `0.037` de esos `0.053`, o sea el **70 %**. En recall recupera casi todo
(0.608 contra un techo de 0.613), que es coherente con lo que arregla.

### 2.5 La salvedad que hay que decir siempre

**El régimen "incompleto" que ellos evalúan retiene el ~73 % de las marcas** (borran hasta
dejar una célula por parche de 500×500). El nuestro son **26 marcas en 4799 parches**. El paper
no evalúa ese régimen y no hay forma de extrapolar la curva.

Y el código existe (`github.com/zipeizhao/PU-learning-for-cell-detection`, clonado en
`clam_testing2/PUcell_reference/`) pero pide **PyTorch 0.4.0 y CUDA 8.0**: no hay kernels para
una RTX A6000. Sirve como referencia exacta de la loss, no como software que se clone y corra.

---

## 3. CellViT (Hörst et al., MedIA 2024): segmentar cada núcleo

> Familia C. Prioridad 2, y para **grado nuclear**, no para mitosis.

### 3.1 El problema: separar núcleos que se tocan

Segmentar núcleos es fácil hasta que dos se pegan. Una máscara binaria de "esto es núcleo" los
funde en una sola mancha, y contar o medir se vuelve imposible.

### 3.2 El vocabulario de HoVer-Net, que CellViT hereda entero

CellViT es **HoVer-Net con el encoder cambiado**, así que hay que entender HoVer-Net primero.

**Encoder y decoder.** El encoder comprime la imagen a una representación interna; el decoder
la expande de vuelta a mapas del tamaño de la imagen. La analogía: el encoder resume, el decoder
redacta a partir del resumen.

**Las tres ramas de decoder.** De la misma representación salen tres mapas:

```
   NP  →  ¿este píxel es núcleo?              (máscara binaria)
   HV  →  ¿hacia dónde está el centro de SU núcleo?   (dos mapas: horizontal y vertical)
   NT  →  ¿de qué tipo es?                    (5 clases de PanNuke)
```

**Los mapas HV son la idea central.** Cada píxel de núcleo guarda su distancia con signo al
centro del núcleo al que pertenece, normalizada entre -1 y 1. La analogía es una brújula por
píxel: cada píxel apunta a su propio centro. Dos núcleos pegados forman una sola mancha en NP,
pero en HV hay un **salto brusco** justo en la frontera, porque los píxeles de un lado apuntan
a un centro y los del otro a otro.

**Watershed** (línea divisoria de aguas). Se calcula el gradiente de los mapas HV, que convierte
esos saltos en "crestas", y después se inunda el terreno desde los mínimos: el agua de dos
cuencas se encuentra exactamente en la cresta, y ahí queda la línea que separa los dos núcleos.
Es post-procesamiento clásico de CPU, y **es donde está el costo**: 75 min de CPU por lámina en
nuestra medición de HoVer-Net.

**Panoptic Quality (PQ).** La métrica de segmentación de instancias: combina cuántos objetos se
detectaron bien con cuán bien se dibujó cada uno.

### 3.3 Qué cambia CellViT

Reemplaza el encoder CNN por un **Vision Transformer pre-entrenado** (ViT-S, o el encoder de
SAM), y hace inferencia sobre parches de 1024×1024 en vez de 256×256.

**Vision Transformer**: corta la imagen en parches chicos, los trata como una secuencia y deja
que cada uno mire a todos los demás. Frente a una CNN, que mira vecindarios, el ViT tiene
contexto global desde la primera capa.

Detección en PanNuke (agnóstica de clase):

| Modelo | Precisión | Recall | F1 |
|---|---|---|---|
| HoVer-Net | 0.82 | 0.79 | 0.80 |
| CellViT256 | 0.83 | 0.82 | 0.82 |
| **CellViT-SAM-H** | 0.84 | 0.81 | **0.83** |
| CellViT-Random (**sin** pre-entrenar) | 0.79 | 0.81 | 0.80 |

La última fila es la que ordena la lectura: sin pre-entrenamiento cae al nivel de HoVer-Net, o
sea que buena parte de la ganancia viene de los pesos, no de la arquitectura.

### 3.4 El dato que más nos toca: qué pasa a la escala del privado

| Modelo | Recall @ 0.25 µm/px | Recall @ 0.50 µm/px |
|---|---|---|
| CellViT256 | 0.82 | **0.60** |
| CellViT-SAM-H | 0.81 | **0.63** |

**Por qué se cae, en una cuenta.** Un núcleo de 8 µm de diámetro:

```
   a 0.25 µm/px  →  32 px de lado  →  ~1024 px de área
   a 0.50 µm/px  →  16 px de lado  →   ~256 px de área      (una cuarta parte)
```

Con la cuarta parte de los píxeles, los mapas HV tienen mucha menos resolución para marcar la
frontera entre dos núcleos pegados, y el watershed los funde. Se pierden núcleos (recall cae de
0.82 a 0.60) pero los que quedan son los grandes y aislados, que son fáciles, así que la
precisión hasta sube.

**Nuestro privado está a 0.465 µm/px.** A esa escala CellViT queda por debajo de HoVer-Net a
0.25 (F1 0.71-0.73 contra 0.80). En TCGA (0.2325) el problema no existe.

### 3.5 Los dos frenos

1. **No tiene clase mitótica.** La palabra "mitosis" no aparece ni una vez en las 23 páginas.
   No es que la clase esté y rinda mal: el problema no está planteado.
2. **Sigue usando watershed**, así que no elimina el costo de CPU que es lo que hizo pausar la
   familia C. Y su speedup (1.85× la variante chica, 1.39× la buena) viene sobre todo del
   parche de 1024 px, no de la arquitectura.

**La cuenta que reordena la familia:** cambiar de modelo rinde 1.85×; acotar de 4799 parches a
los 20 mejores de CLAM rinde **~240×**. Si C se reabre, se reabre por el subconjunto de parches.

**Dónde sí calza:** en grado nuclear. Una vez segmentado el núcleo, "más grande que su
vecindario" es una razón entre áreas, y una razón es **invariante a la escala**, que es justo
nuestro confundido de magnificación.

---

## 4. ZoomMIL (Thandiackal et al., ECCV 2022): aprender dónde hacer zoom

> Familia B. Prioridad 3 para mitosis, y candidato real para otra cosa.

### 4.1 La idea, con la analogía obvia

Un patólogo no mira la lámina entera a 40×. Barre a aumento bajo, encuentra las zonas
sospechosas y solo ahí sube el aumento. ZoomMIL hace exactamente eso, y lo importante es que
**aprende dónde subir**, entrenando solo con la etiqueta de lámina.

```
   1.25×   toda la lámina, pocos parches      →  elige K
      ↓
   2.5×    solo los hijos de esos K           →  elige K'
      ↓
   10×     solo los hijos de esos K'          →  clasifica
```

El ahorro es real: en BRIGHT usa **12.8× menos FLOPs** que CLAM-SB.

### 4.2 Las tres piezas nuevas

**a) Dos atenciones por nivel, no una.**

Primero el término base: **atención con compuerta** (gated attention), que es la misma familia
que usa CLAM. A cada parche se le asigna un peso `a_i` entre 0 y 1 que suman 1, y la lámina se
representa como la suma pesada `g = Σ a_i h_i`. La "compuerta" es el producto
`tanh(V·h) ⊙ σ(U·h)`: una rama propone y la otra deja pasar o no.

ZoomMIL pone **dos** de estos por nivel de aumento:

```
   GA_m   →  produce la representación de la lámina en ese nivel   (para clasificar)
   GA'_m  →  decide qué parches se amplían                          (para elegir)
```

El motivo: un mismo puntaje no puede servir bien a dos objetivos distintos. "Este parche es
evidencia de la clase" y "este parche merece que lo mire de cerca" no son la misma pregunta.

**b) Un top-K derivable, que es el truco técnico del paper.**

Elegir "los K de mayor atención" es una operación discreta: el resultado es un vector de ceros
y unos que **no cambia** si movés los pesos un poquito, y por lo tanto su derivada es cero en
todas partes. Sin derivada no hay gradiente, y sin gradiente el modelo no puede aprender a
elegir mejor.

La solución es el **máximo perturbado**: en vez de preguntar una vez, se le suma ruido
gaussiano a los pesos y se pregunta 100 veces, promediando las respuestas.

**Mini-ejemplo ilustrativo.** Tres parches con atención `[0.50, 0.30, 0.20]`, `K = 1`:

```
   top-K duro          →  [1, 0, 0]           derivada 0, no aprende
   máximo perturbado   →  [0.62, 0.27, 0.11]  (62 de 100 sorteos los gana el primero)
```

El segundo vector **sí** se mueve si los pesos se mueven: si el parche 2 sube a 0.35, gana más
sorteos y su coordenada sube. Eso es lo que da gradiente. En inferencia se vuelve al top-K duro,
así que entrenamiento e inferencia no son el mismo grafo, y el paper lo declara.

**c) Traer los hijos: el producto de Kronecker.**

Si el parche `i` del nivel bajo se selecciona, hay que traer los parches del nivel alto que caen
adentro de él. El paper lo escribe como `H̃ = (T ⊗ 1)ᵀ · H`, que suena peor de lo que es.

**Mini-ejemplo ilustrativo.** Tres parches a aumento bajo, cada uno se subdivide en 4 al
siguiente nivel (12 en total). Se selecciona el segundo:

```
   selección     T  =  [0, 1, 0]
   expansión     T ⊗ [1,1,1,1]  =  [0,0,0,0,  1,1,1,1,  0,0,0,0]
                                    └─hijos─┘ └─hijos─┘ └─hijos─┘
                                     del 1°     del 2°    del 3°
```

O sea que el producto de Kronecker es "repetí cada decisión tantas veces como hijos tenga". El
factor no está hardcodeado (se calcula como la razón medida entre la cantidad de parches de los
dos niveles), pero **el supuesto sí importa**: la grilla del nivel alto tiene que ser una
subdivisión anidada exacta de la del bajo, con los hijos contiguos. **Nuestros `.h5` actuales no
cumplen eso**: son un solo nivel, sin jerarquía padre-hijo.

### 4.3 Qué consigue, y dónde no

| Dataset | Método | Weighted-F1 | TFLOPs |
|---|---|---|---|
| **BRIGHT** (mama) | CLAM-SB (10×) | 63.1 | 16.45 |
| **BRIGHT** (mama) | **ZoomMIL** (1.25×→2.5×→10×) | **68.3** | **1.29** |
| CAMELYON16 | CLAM-SB (20×) | 83.3 | 39.12 |
| CAMELYON16 | ZoomMIL (10×→20×) | 83.3 | 14.94 |

En mama le saca **5.2 puntos a CLAM-SB con 12.8× menos cómputo**. En CAMELYON16 queda a la par.

### 4.4 Por qué queda tercero para mitosis

Dos razones, y la primera es del propio paper (pág. 9, sobre CAMELYON16):

> *"As the metastatic regions can be extremely small, we set the lowest magnification to 10× in
> ours. Nevertheless, this still has an adverse impact on the performance."*

O sea: **cuando el objeto a encontrar es chico, el mecanismo de zoom se degrada**, y ellos
tuvieron que renunciar a arrancar en aumento bajo. Es lógico: si el objeto no deja ninguna
firma visible a 1.25×, la atención de ese nivel no tiene con qué elegir bien. Una
micro-metástasis mide cientos de micras; **una figura mitótica marcada mide 16.7 µm**.

La segunda razón es de la cohorte, no del método: **nuestro privado está escaneado a 20×** y la
mitosis se cuenta a 40×. Un método que aprende dónde ampliar no puede ampliar a una
magnificación que el archivo no contiene.

**Gotcha del código, verificado**, que nos mordería exactamente a nosotros: su preprocesamiento
lee el aumento nativo solo de `aperio.AppMag` y, si no está, **asume 40× con un warning**.
Nuestra cohorte privada es Ventana `.bif`, que no expone esa propiedad: se la trataría como 40×
estando a 20×. Es el error silencioso de factor 2 contra el que advierte nuestra regla de
proyecto.

**Dónde sí aporta:** en el confundido de magnificación entre cohortes. Si la pirámide se
parametriza en µm/px físicos y no en `level`, un modelo multi-escala es la vía natural para que
TCGA a 0.2325 y el privado a 0.465 dejen de ser dos escalas distintas sin avisar. Esa
infraestructura ya está escrita y sin lanzar del B6 (`scripts/extract_multiscale_features.py`).

---

## 5. MS-CLAM (Tourniaire et al., MedIA 2023): supervisar la atención de CLAM

> Fuera de las tres familias. Prioridad 5, y se lleva igual a la reunión.

### 5.1 Qué es

CLAM, el mismo, entrenado con **supervisión mixta**: la mayoría de las láminas aporta solo su
etiqueta, y unas pocas aportan además la etiqueta de **cada parche**, que se usa para supervisar
directamente los puntajes de atención en vez de dejar que emerjan solos.

Es el más cercano a nuestra infraestructura de los cuatro: el repo es un fork del CLAM de
Mahmood Lab.

### 5.2 La pieza que importa: la loss de atención

Para láminas tumorales con etiquetas de parche, la ec. 3 tiene tres partes:

```
L_att  =  Σ_{no tumorales} a_i   +   (1/log m)·Σ_{tumorales} a_j log a_j   −   Σ_{tumorales} a_j
          └───────┬───────┘           └────────────┬────────────┘            └───────┬──────┘
       "bajá a cero la atención     "repartí parejo entre los         "y que entre todos
        de lo NO tumoral"            tumorales" (entropía máxima)      sumen 1"
```

El término del medio usa **entropía** como medida de cuán repartida está la atención: entropía
alta significa que todos pesan parecido, entropía baja que uno se lleva todo. Maximizarla dentro
del grupo tumoral evita que el modelo se enganche con un solo parche.

**Mini-ejemplo ilustrativo.** Cinco parches con atención `[0.50, 0.30, 0.10, 0.05, 0.05]`, y el
patólogo marcó como tumorales solo los dos primeros:

```
   término 1  =  0.10 + 0.05 + 0.05  =  0.20     →  el gradiente lo empuja a 0
   término 3  = −(0.50 + 0.30)       = −0.80     →  el gradiente lo empuja a 1
   término 2  →  empuja el 0.50/0.30 hacia 0.40/0.40
```

### 5.3 Por qué no nos sirve hoy, con precisión

**La escasez no es lo que lo mata.** Tiene una sección entera (§2.5) para el caso sin anotación:
las láminas sin etiquetas de parche usan las pseudo-etiquetas de atención de CLAM de siempre, y
el método **degrada con gracia** hasta volver a ser CLAM.

**Lo que lo mata es la parcialidad.** Volvamos al mini-ejemplo: el parche 3, con atención 0.10,
no fue marcado. Si ese parche fuera una mitosis real que el patólogo no marcó, el término 1
**empuja activamente su atención hacia cero**. O sea que el método castigaría al modelo por
mirar exactamente lo que queremos que mire.

Es la **hipótesis opuesta** a la de PU learning:

```
   MS-CLAM      →  "lo no marcado es negativo, y lo uso como señal"
   PU learning  →  "lo no marcado tiene etiqueta desconocida, y reescribo la loss"
```

Por eso los dos no se pueden mezclar sin reescribir esa ecuación.

**Una ironía útil:** su propio dataset tiene el problema. Aclaran que en Camelyon16 todas las
láminas metastásicas están anotadas exhaustivamente *"except for 20 slides which were only
partially annotated"*. La anotación parcial aparece en sus datos como una excepción molesta, no
como un régimen que el método modele.

**Y llegamos con el síntoma que arregla ya bastante ausente.** Su aporte más visible es en
localización, porque la atención de CLAM **se derrama** (Dice 0.520 en Camelyon16, cubriendo a
veces casi todo el tejido). En nuestra medición del 1-ago la atención no se derramó: cayó sobre
las marcas (AUC de ranking 0.890 para mitosis, y grasa en 0.154).

**Para qué llevarlo igual:** es la respuesta preparada si en la reunión sale "¿y por qué no le
agregamos supervisión de parche a CLAM y listo?". Se puede, está publicado, funciona, y necesita
un orden de magnitud más de anotación del que tenemos, con un supuesto que nuestras marcas no
cumplen. Y vuelve a la mesa si el patólogo alguna vez anota **regiones** en vez de puntos.

---

## 6. Anexo: MIDOG, que no es un método sino un dataset

> Aubreville et al., MedIA 2023. No es candidato: es el insumo que vuelve ejecutable el paso 1
> de la familia D.

**Qué es.** 200 casos de cáncer de mama humano de entrenamiento y 100 de test, en 4 escáneres,
dos de ellos **no vistos** en el test. Licencia CC-BY.

**El término nuevo: generalización de dominio** (domain generalization). Entrenar en unos
escáneres y evaluar en otros distintos, a propósito. La razón de existir del challenge es que
**los detectores de mitosis se caen al cambiar de escáner**, y esa es la advertencia central
para nosotros: nuestra cohorte privada es Ventana `.bif`, que no está entre los seis.

**Tres cosas lo vuelven el candidato natural del paso 1.**

1. **La escala calza con TCGA.** Sus escáneres van de 0.23 a 0.26 µm/px. TCGA (0.2325) cae
   dentro y corre **sin reescalar**; el privado (0.465) está al doble y necesita reescalado, que
   es el brazo con riesgo. Detalle que refuerza nuestra regla de proyecto: su escáner E declara
   "0.24 µm/px @ 20×", o sea que el rótulo de aumento y la escala física no se corresponden entre
   fabricantes.
2. **Su unidad de dato es el campo de recuento clínico.** No son WSI: son **regiones de 2.0 mm²**
   elegidas por un patólogo, que es la definición de los 10 campos de gran aumento del recuento
   de Nottingham. MIDOG resuelve el "cuántas mitosis hay acá dentro" y nos deja el "dónde está el
   acá dentro". Y la densidad es comparable: la mayoría de sus ROI tienen 20 o menos figuras
   mitóticas, nuestra 129741 tiene 26. La diferencia son los 200 casos contra nuestra lámina.
3. **La evaluación contra el geojson es viable sin inventar tolerancias.** Su criterio de acierto
   es centroide a menos de **7.5 µm**, que cae holgadamente dentro de nuestras marcas de 16.7 µm.

**Los números.** Ganador F1 **0.748**, ensamble de los 5 mejores 0.773. El ganador supera a seis
expertos humanos en la misma tarea.

**Estado.** Su tooling público (`MIDOG_reference_docker`, `MIDOG_evaluation_docker`) **no se
bajó**: está fuera de la lista que Ernesto autorizó el 2-ago, y bajarlo **requiere autorización
nueva**.

---

## 7. Los cuatro en un solo cuadro

Dónde actúa cada uno sobre el pipeline que ya tenemos:

```
   WSI  →  parches  →  CONCH (512-d)  →  CLAM_MB  →  score_1/2/3
            │             │                │
            │             │                └── MS-CLAM: supervisa la atención acá
            │             │                    (necesita etiqueta de parche exhaustiva)
            │             │
            │             └── ZoomMIL: cambia QUÉ parches llegan hasta acá,
            │                 con una pirámide de aumentos y un top-K derivable
            │
            ├── CellViT: cambia la UNIDAD, del parche al núcleo
            │   (segmenta, mide, y de ahí salen features geométricas)
            │
            └── PU learning: rama aparte, NO es MIL.
                Detecta mitosis una por una con las marcas parciales del patólogo,
                y de ahí sale un conteo en el punto caliente
```

Y el criterio único que los ordena, que es qué supervisión exige cada uno contra la que tenemos
(una lámina, 26 marcas, lo no marcado no es negativo):

| | Supervisión que exige | ¿Compatible? | Prioridad |
|---|---|---|---|
| **PU learning** | positivos parciales, **los nuestros** | **sí, por construcción** | **1** |
| **CellViT** | ninguna nuestra (pesos públicos) | sí, no las usa | 2 (grado nuclear) |
| **ZoomMIL** | solo etiqueta de lámina | sí, no las usa | 3 |
| **MS-CLAM** | etiqueta de parche **exhaustiva** | **no** | 5 |

---

## 8. Lo que este documento no afirma

- **Que alguno de los cuatro suba nuestra métrica.** Ninguno se probó en nuestros datos, y el
  historial del proyecto son cuatro ejes cerrados sin mejora (Hallazgos 11 a 14).
- **Que los ejemplos numéricos sean nuestros datos.** Son ilustrativos, construidos acá para que
  se vea la mecánica de cada fórmula.
- **Que la familia D vaya a transferir a nuestra cohorte.** MIDOG existe justamente porque los
  detectores de mitosis se caen al cambiar de escáner.
- **Nada de esto está implementado ni pre-registrado.** Si alguna rama avanza, va con hipótesis
  pre-registrada, métrica y dirección esperada, y `reviewer` antes de tocar código (regla 9).
