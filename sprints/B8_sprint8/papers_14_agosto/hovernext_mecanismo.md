# HoVer-NeXt por dentro: el mecanismo, pieza por pieza

> Baumann, Dislich, Rumberger, Nagtegaal, Rodríguez Martínez, Zlobec. *HoVer-NeXt: A Fast Nuclei
> Segmentation and Classification Pipeline for Next Generation Histopathology*. PMLR 250:61-86,
> MIDL 2024.
>
> **Qué es este documento.** Cómo funciona el modelo y su pipeline, explicado desde cero. Es el
> complemento de [`hovernext_estudio.md`](hovernext_estudio.md), que verifica los **números** contra
> el PDF; acá no se re-verifica ninguno. Si un número aparece, es porque el mecanismo no se entiende
> sin él, y sale del estudio o de la línea citada del volcado.
>
> **Fuentes.** El PDF [`../hover_next.pdf`](../hover_next.pdf) y su volcado
> [`../hover_next.txt`](../hover_next.txt) (las citas `L###` son líneas de ese volcado). Las
> **figuras** se leyeron del PDF directo: Fig. 1 en la página 3 y Fig. 5 en la 16 (página impresa =
> página PDF + 60). No se bajaron pesos ni se clonó el repo.
>
> **Prerrequisito.** HoVer-NeXt se define como un delta contra HoVer-Net, así que este documento
> asume [`../hovernet_estudio.md`](../hovernet_estudio.md), que ya está en el repo y leído. Cada
> pieza se presenta como *qué hacía HoVer-Net · qué cambió · por qué*. El mini ejemplo de una
> dimensión del §3 de ese estudio se reusa acá con una fila más, para que los dos documentos hablen
> el mismo idioma.

---

## 1. El problema, y el vocabulario mínimo

Tres términos distintos, y el diseño entero sale de la diferencia entre ellos:

- **Segmentación semántica**: por cada píxel, decir de qué tipo es. Sale un mapa pintado por
  categoría. No dice dónde termina un objeto y empieza el siguiente.
- **Segmentación de instancias**: por cada píxel, decir **a cuál** objeto pertenece. Salen objetos
  numerados, pero sin tipo.
- **Segmentación panóptica**: las dos a la vez. Cada núcleo numerado **y** con su tipo.

La analogía que funciona es un bosque visto desde arriba. La semántica pinta todo el bosque de
verde y el pastizal de amarillo, pero no sabés cuántos árboles hay. La de instancias le pone un
número a cada árbol, sin decirte la especie. La panóptica te da árbol 47, roble.

**El problema real es que los núcleos vienen en racimo.** Pegados. La máscara binaria de un racimo
de cinco núcleos es una sola mancha: contás uno donde hay cinco, y toda la morfometría posterior
queda envenenada. Todo lo que sigue existe para cortar esa mancha en cinco.

Y hay un segundo problema, que es el que motiva este paper en particular y no el anterior: **una
WSI a 40× pasa los 100 000 × 100 000 píxeles**, así que un método que tarda horas por lámina no se
puede correr sobre una cohorte (L71-73).

## 2. De tres decodificadores a dos

Un **decodificador** es la mitad de subida de la U: toma el mapa comprimido que produjo el encoder
y lo vuelve a llevar a la resolución de la imagen, prediciendo algo por píxel. Cada decodificador
predice **una cosa distinta** sobre la misma imagen, compartiendo el mismo encoder.

| | HoVer-Net (2019) | HoVer-NeXt (2024) |
|---|---|---|
| Encoder | Preact-ResNet50, sub-muestreo bajado de 32 a 8 | **ConvNeXt-v2** (Tiny, Base, Large) + un upsampling extra |
| Decodificadores | **tres**: NP (núcleo/fondo), HoVer (2 canales de distancia), NC (tipo) | **dos**: instancia y clase |
| Cómo separa instancias | gradiente Sobel de los mapas HV, en post-proceso | **BCB-map**, predicho directo |
| Los mapas HV | son el mecanismo central | **tarea auxiliar** |

El cambio de fondo es de **dónde ocurre el trabajo de separar**. En HoVer-Net la red predice una
señal (los mapas HV) de la cual *se deriva* el corte, con una cadena de operaciones clásicas sobre
CPU. En HoVer-NeXt la red predice **el corte mismo** (L182-187).

## 3. El BCB-map, que es la pieza central

**BCB = Boundary, Center, Background.** Borde, centro, fondo. Por cada píxel el modelo elige una de
esas tres, igual que un clasificador de tres clases pero repetido en cada píxel (L183-185).

La analogía: en vez de pintar «acá hay núcleo» y después calcular dónde están los bordes, se le
pide al modelo que **pinte los bordes con un color propio**. Queda una franja de tierra de nadie
entre dos núcleos vecinos, y adentro de cada uno un corazón marcado.

### El mini ejemplo, con la fila que faltaba

La misma fila de 10 píxeles del §3 de `hovernet_estudio.md`. Dos núcleos pegados: A ocupa las
columnas 1 a 4, B las columnas 5 a 8.

| columna | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|---|---|
| máscara binaria (NP de HoVer-Net) | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 0 |
| mapa horizontal (HoVer-Net) | 0 | −1 | −0.33 | +0.33 | +1 | −1 | −0.33 | +0.33 | +1 | 0 |
| **BCB (HoVer-NeXt)** | fondo | **borde** | centro | centro | **borde** | **borde** | centro | centro | **borde** | fondo |

Leído así, la diferencia salta:

- La **máscara binaria** es una sola mancha de ocho píxeles. No hay nada que separar.
- El **mapa horizontal** sí tiene la información, pero **latente**: hay que calcular la derivada
  entre columnas contiguas para que aparezca el −2 de la costura contra el 0.67 de adentro. La
  información existe, pero hay que ir a buscarla.
- El **BCB** ya viene cortado. Los píxeles `centro` forman dos grupos separados, {2,3} y {6,7}, y
  los `borde` son la pared entre ellos. No hay nada que derivar.

### Por qué eso le sirve tanto al watershed

**Watershed** («línea divisoria de aguas») es un algoritmo clásico de inundación. Se le dan dos
cosas: **semillas** (los puntos desde donde empieza a inundar) y **barreras** (dónde el agua se
frena). Cada charco resultante es un objeto.

Y el BCB entrega **exactamente esos dos ingredientes, ya listos**: las semillas son los píxeles
`centro`, las barreras son los píxeles `borde`. El paso de post-proceso se reduce a umbralar los
tres canales y correr el watershed (L217-219). HoVer-Net, en cambio, tiene que fabricarse los dos
ingredientes con la cadena Sobel → máximo → marcadores → paisaje de energía, cada paso una pasada
a resolución completa y con dos umbrales libres (`h` y `k`) que hay que elegir.

### La figura lo muestra literal

La **Fig. 5 (PDF p.16)** trae un panel rotulado *Model BCB Output*: fondo **rojo**, blobs
**verdes** que son los núcleos y una franja **azul** finita rodeando cada uno. En los paneles de
zoom de abajo (*Model output before rotation*) se ven las tres bandas con la grilla de píxeles
encima. El código de color no está escrito en el epígrafe, así que la correspondencia rojo/verde/azul
con fondo/centro/borde es **lectura visual de la figura**, no una cita.

### La tensión con HoVer-Net

**HoVer-Net existía justamente para NO tener que predecir el contorno como clase.** Su §2 argumenta
que el contorno es una línea de uno o dos píxeles, o sea la clase más chica, la más desbalanceada y
la más frágil justo donde dos núcleos se aprietan, y que por eso conviene una señal gruesa y
redundante como los mapas HV.

HoVer-NeXt **vuelve a predecir el borde como clase**. Dos cosas amortiguan la contradicción, y una
tercera la deja abierta:

1. El borde no está solo: viene con una clase `centro` al lado. Las semillas del watershed salen del
   `centro`, así que **no dependen de que el borde sea perfecto**, solo de que exista algo de pared.
   En HoVer-Net los marcadores se obtenían restándole la costura a la máscara, o sea que sí dependían.
2. Los mapas HV **siguen entrenándose** (§5), así que el encoder sigue viendo esa señal gruesa.
3. Pero el resultado no mejora: en PanNuke, con la misma validación cruzada de 3 folds, el
   **bPQ**<sub>Tiss</sub> (panoptic quality **binaria**, o sea instancias puras sin clases) da
   **0.656 para HNTiny contra 0.659 de HoVer-Net** (Fig. 3, L382-384). Empate, un pelo abajo.

**El BCB no separa mejor: separa igual y más barato.** El paper no lo presenta como una mejora de
calidad, y justifica la elección citando a Caicedo 2018, o sea resultados en **otras modalidades**,
no los propios (L184-185).

## 4. Cuánto del 17× compra realmente el BCB

Esta es la primera de las dos preguntas del handoff, y tiene una respuesta cuantitativa gracias a
que **medimos HoVer-Net nosotros**.

Del job 4714 (`hovernet_estudio.md` §10 y §12), sobre una lámina de TCGA en la A6000:

| Etapa | Tiempo | Fracción |
|---|---:|---:|
| Inferencia en GPU | ~2 h 11 | ~61 % |
| **Post-proceso (watershed y compañía), CPU, 16 workers** | **1 h 15** | **~35 %** |
| Guardado | 10 min | ~5 % |
| **Total** | **3 h 36** | |

Y de ahí sale la cuenta que importa: **aunque el BCB eliminara el 100 % del post-proceso, el ahorro
sería 216/141 ≈ 1,5×.** No 17×.

**Entonces el BCB no es donde vive el 17×.** Lo que hace es volver barato un tercio del costo. El
resto sale de una lista de ingeniería, toda en §2.2 y §2.3, y ninguna pieza es glamorosa:

- **Encoder más chico y más moderno**, y la comparación del 17× se hace con **HNTiny**, el más
  pequeño de los tres (L425-426).
- **Media precisión** en el forward (L231).
- **Salida cuantizada**: los softmax, que son flotantes entre 0 y 1, se mapean a enteros de 0 a 255,
  o sea un byte por valor en vez de cuatro (L231-232).
- **Escritura en un proceso aparte**, para que la GPU no espere al disco (L232-233).
- **Zarr comprimido con LZ4**, que admite lecturas y escrituras concurrentes (L233-235).
- **Pre-stitching** de los tiles crudos antes de post-procesar (§9), que reduce la cantidad de
  costuras a resolver.
- **Se sacó el convex hull** del post-proceso porque calcularlo por objeto es caro (L205-206).
- **Se sacó la normalización por tile**, que además producía artefactos fuera de dominio (L206-208).

**Y el convex hull se pagó.** El propio paper lo dice en la Discusión: quitarlo «likely leads to more
segmentation outliers increasing the Hausdorff distance» (L447-448), y la tabla lo confirma: contra
su propia entrada al CoNiC, la distancia de Hausdorff **empeora** en casi todas las clases (en
neutrófilos 1.966 → 2.250 en HNLarge y → 2.663 en HNTiny; Fig. 2). Hausdorff mide error de **forma**,
así que la lectura es: los núcleos quedan un poco peor dibujados, y lo cambiaron por velocidad a
sabiendas.

> **Salvedad de la comparación**: nuestras 3 h 36 son HoVer-Net en `model_mode=fast` sobre una lámina
> de TCGA a 40× en la A6000; el 17,2× del paper es HNTiny contra HoVer-Net sobre su propio conjunto
> de cinco WSI en una A40. La **proporción** del post-proceso sí es medición nuestra sobre el mismo
> pipeline, así que la descomposición sirve como orden de magnitud, no como ablación.

## 5. Los mapas HV, degradados a tarea auxiliar

Una **tarea auxiliar** es algo que el modelo aprende a predecir durante el entrenamiento aunque no
se use en producción. La analogía: hacer solfeo mientras aprendés a tocar un instrumento. En el
recital nadie te evalúa el solfeo, pero te hace mejor músico. Acá, obligar al decodificador a
predecir *a qué distancia y para qué lado le queda el centro de su núcleo* a cada píxel fuerza al
encoder a codificar la **geometría** del núcleo, no solo su textura.

Lo verificado y lo que queda ambiguo:

- **Verificado**: §2.1 dice que los mapas HV «are thus only used as an auxiliary task» (L186-187), y
  A.1 confirma que se entrenan, con MSELoss (L722-723).
- **Verificado**: el pipeline de inferencia (§2.3) construye semillas y barreras **solo desde el
  BCB**, y no menciona los HV en ningún paso (L217-219).
- **Ambiguo**: la **Fig. 1B** dibuja una sola caja rotulada *«HV maps & BCB-map»* con **una** flecha
  saliendo hacia *Instance map*, lo que se puede leer como que las dos salidas alimentan la
  instancia. El texto no dice que se descarten en inferencia; dice que son auxiliares. **La
  respuesta exacta está en el código, que no bajamos.**

## 6. El encoder, y el upsampling que hubo que agregar

**ConvNeXt-v2** es una red convolucional moderna, diseñada tomando prestadas ideas de los
transformers. Se usa **pre-entrenada en ImageNet** (L719-720) y en tres tamaños: Tiny, Base y Large.

El detalle que importa es geométrico. Una **U-Net** baja resolución en el encoder y la sube en el
decodificador, con conexiones laterales que reinyectan el detalle fino de cada nivel. ConvNeXt-v2
**agrupa más agresivamente** que el encoder anterior, o sea que llega más abajo en resolución; para
que la U mantenga la misma profundidad hubo que **agregar un paso de upsampling** del lado de la
subida (L200-202).

HoVer-Net había atacado el mismo problema por el lado contrario: bajó el factor de
sub-muestreo total **de 32 a 8**, poniendo stride 1 en la primera convolución y sacando el
max-pooling. **Mismo problema, dos soluciones opuestas**: uno le saca profundidad al encoder, el
otro se la agrega al decodificador. En segmentación no podés tirar resolución de entrada y esperar
recuperarla después.

## 7. El pipeline de inferencia, paso a paso

Es la contribución número 4 del paper y donde vive el 17×. La Fig. 1A lo dibuja en tres cajas: el
modelo, un **caché** en disco y un **stitcher** que corre aparte.

1. **Encontrar el tejido** (A.3). Se toma el **thumbnail** que OpenSlide expone para cualquier WSI
   (entre 1/75 y 1/160 de la resolución completa), se pasa a gris, se difumina con un kernel de
   promedio 5×5, y se queda con todo lo que esté **por debajo de 240** de intensidad. Después filtra
   los objetos menores al 0,01 % de la imagen (fragmentos y artefactos) y **dilata** lo que quedó con
   un kernel circular de diámetro 0,01 % de la dimensión más larga, para no comerse esquinas de
   tejido claro que el desenfoque borró (L748-770). Todo esto sobre el thumbnail, o sea que cuesta
   milisegundos.
2. **Recorrer el tejido en tiles con solape**: 8 px a 0,5 µm/px y 16 px a 0,25 (L212-213).
3. **Aplicar las TTA** (§8) y promediar.
4. **Guardar crudo**: el mapa de clases y el BCB se comprimen y van a disco **sin post-procesar**,
   escritos por otro proceso. Acá termina el trabajo de la GPU.
5. **Recortar al centro y pre-pegar** los tiles en regiones grandes (L216-217). El solape del paso 2
   se consume en este recorte.
6. **Watershed sobre el BCB**, por región, en paralelo. Umbrales por clase para el área de tejido y
   las semillas (L217-219).
7. **Limpiar**: tapar huecos chicos dentro de las instancias y deshacer fusiones falsas (L219-220).
8. **Asignar la clase por voto de mayoría**: la instancia ya está definida por el BCB; se miran los
   píxeles de esa máscara en el mapa del **otro** decodificador y gana la clase más votada
   (L220-221).
9. **Filtrar por tamaño**, con umbrales por clase buscados en el conjunto de validación (L220-222).
10. **Resolver los solapes entre regiones** (§9).

**El punto de diseño más limpio de todo el pipeline está en el paso 8**: un decodificador dice
**dónde** está cada núcleo y el otro dice **qué** es, y el voto de mayoría los casa. Eso garantiza
**una clase por núcleo** en vez de un mosaico de píxeles en desacuerdo, y hace que un puñado de
píxeles mal clasificados no cambie nada. Es exactamente el mismo truco que ya usaba HoVer-Net con su
rama NC, y es de las pocas piezas que sobrevivió intacta.

## 8. Las TTA, y por qué solo tres

**TTA (test-time augmentation)** es pedirle al modelo su opinión sobre la misma imagen vista de
varias maneras, y promediar las respuestas. La intuición es la de un jurado: varias miradas
imperfectas promedian mejor que una sola.

Pero en segmentación tiene un costo que en clasificación no existe: **la salida también hay que
des-transformarla**. Si girás la entrada, tenés que girar la predicción de vuelta para que los
píxeles vuelvan a su lugar. Y ahí está el filtro que explica la lista corta.

**Las tres que sobreviven** (L214-215) y por qué:

| TTA | Por qué es segura |
|---|---|
| **Rotación de 90°** | Es una **permutación exacta de píxeles**: rotar una grilla 90° es renombrar índices. Deshacerla devuelve exactamente los valores originales. |
| **Espejado** | Ídem, permutación exacta. |
| **Aumentación de color HED** | Toca el **color**, no la geometría, así que no hay transformación inversa espacial que aplicar a la salida. (HED es el espacio de la deconvolución de tinción; el paper lo toma de Tellez 2019 y no lo define.) |

**Las que quedaron afuera y por qué** (A.4, L772-786):

- **Rotar cualquier ángulo que no sea múltiplo de 90°** obliga a **interpolar**, o sea a inventar
  valores intermedios promediando vecinos. Al deshacer la rotación, la interpolación se aplica **dos
  veces**, y los bordes de los núcleos salen suavizados. El paper apunta que la diferencia de **un
  solo píxel** ya mueve la distancia de Hausdorff de ese núcleo de manera apreciable.
- **Rotar 45° o desplazar** además **pierde píxeles**: las esquinas de la imagen original quedan
  fuera del cuadro y no hay predicción para ellas.
- **Ruido gaussiano y desenfoque** directamente **quitan información**. No tiene sentido pedirle al
  modelo que adivine sobre una versión peor de la imagen que ya tenés.

**La Fig. 5 es toda esa explicación en una imagen** y es la razón por la que vale abrirla. Sus siete
paneles siguen una rotación de menos de 90° de punta a punta: *Input Image* → *Augmented (Rotated)*
con las esquinas negras → *Model BCB Output* → *Inverse Augmentation*, que vuelve con **cuñas negras
donde ya no hay información**. Abajo, *Missed input area* dibuja el cuadrado rotado sobre la imagen
original para que se vea **qué pedazo del tejido el modelo nunca miró**, y los dos paneles de zoom
comparan el mapa antes y después de la rotación con la grilla de píxeles a la vista: se ve cómo la
interpolación **ablanda los bordes** entre el verde y el azul.

**La asimetría entre entrenamiento e inferencia es deliberada.** En entrenamiento
sí usan las peligrosas (rotación hasta 179°, elástica, shear, zoom, ruido, desenfoque; tabla C.1),
porque ahí el objetivo es lo contrario: que el modelo aprenda a dar una respuesta aceptable **incluso
con una imagen mala** (L777-779).

**Cuánto rinden** (L358-370): la ganancia se concentra en las clases raras. Con 4 TTA, **mitosis
+4,87 % de F1**, neutrófilos +4,16, eosinófilos +2,16, mientras las clases comunes ganan menos del
1 % y las plasmáticas **pierden** 0,35 %. Y **satura**: de 8 a 16 vistas la ganancia es +0,0004.
Traducido a decisión: si esto se corre para mitosis, se corre con TTA, y con 4 alcanza.

> **Detalle fino, marcado como inferencia**: la tabla C.1 lista **probabilidades** también en la
> columna de test (HED p=1.0, espejo p=0.5, rotación 90° p=0.75), lo que sugiere que las vistas se
> **sortean** y no se enumeran las 16 del grupo diedral. El paper no lo dice.

## 9. El stitcher, y la regla de los cuartos

Hay **dos niveles de costura**, y son problemas distintos:

- **Entre tiles**: el solape es de 8 px (0,5 µm/px) y se resuelve **recortando al centro** antes de
  pegar. Barato y sin decisiones.
- **Entre regiones grandes (ROI)**: el solape es de **512 px** y ahí sí hay núcleos duplicados o
  partidos a caballo de la juntura, que hay que resolver de verdad.

**Por qué pre-pegar antes de post-procesar** (L235-237): si corrieras el watershed tile por tile,
tendrías una juntura cada 256 px y miles de conflictos que resolver. Pegando primero los tiles
crudos en regiones grandes, las junturas problemáticas se cuentan por decenas. Además permite
paralelizar el watershed por región y mantiene el pico de memoria bajo.

**La regla de los cuartos** (A.2, L734-745) es cómo un único worker decide, en esos 512 px de
solape, quién gana. Se divide el solape en cuartos, contando desde el borde exterior de lo que ya
está escrito:

| Zona | Quién manda |
|---|---|
| Cuarto más externo de lo ya escrito | **lo viejo**. Lo nuevo en esa zona se descarta. |
| Segundo cuarto, si un núcleo viejo lo toca aunque sea en parte | **lo viejo**, el núcleo entero. |
| Del segundo cuarto hacia adentro | **lo nuevo**. Lo viejo se borra y se reemplaza. |

La lógica es que las predicciones cerca del borde de una región son las peores (el modelo vio menos
contexto de ese lado), así que **cada región aporta su interior y cede su periferia**. Los IDs de
instancia se renumeran a partir del mayor ya escrito, y quedan **no contiguos**, cosa que importa si
alguna vez se lee esa salida. El propio paper marca el supuesto: esto solo falla si un núcleo es más
grande que los 512 px de solape, que en sus datos no pasa.

## 10. El entrenamiento

Todo de A.1 (L716-731):

| Qué | Valor |
|---|---|
| Pasos | 200 000, batch 48 |
| Optimizador | AdamW, weight decay 1e-4 |
| Learning rate | cosine annealing de 1e-4 a 1e-8 |
| Encoder | ConvNeXt-v2 pre-entrenado en ImageNet (timm) |
| Dropout | **50 % en el encoder, cero en los decodificadores** |
| Loss del BCB | entropía cruzada |
| Loss de los vectores al centro (HV) | MSE |
| Loss de clase | focal, γ = 2.0 |
| Peso entre las dos ramas | λ = 0.02 |
| Selección de modelo | **por la mejor métrica de validación, no por la loss más baja** |

Dos comentarios:

- **El λ = 0.02 es una asimetría fuerte y el paper no dice de qué lado va.** Dice que «class and
  instance arm losses are summed and weighted using a weighting parameter (lambda = 0.02)», sin
  aclarar cuál de las dos ramas se multiplica por 0.02. La diferencia es de un factor 50 en cuál
  domina el gradiente. Al código.
- **Seleccionar por métrica y no por loss** contrasta con lo que hacemos nosotros: nuestro CLAM
  guarda el checkpoint por `val_loss`. Tiene sentido en su caso, porque con seis o siete clases muy
  desbalanceadas la loss puede bajar mientras la clase rara empeora.

## 11. La ablación de muestreo contra ponderación dice menos de lo que parece

Hay dos formas clásicas de atacar el desbalance de clases, y el paper las ablaciona en C.2:

- **Ponderar la loss (LW)**: a un error sobre una clase rara se le cobra más caro.
- **Muestrear por distribución (DS)**: se arman los batches sobre-representando las clases raras.

§2.2 justifica quedarse solo con muestreo diciendo «data sampling is already sufficient to treat the
label imbalance» y remite a C.2 (L203-205). **La tabla no dice exactamente eso** (L1055-1058, HNLarge
con 16 TTA):

| LW | DS | mAcc | bF1 | mF1 | mPQ |
|:---:|:---:|---:|---:|---:|---:|
| sí | sí | 0.762 | 0.844 | 0.607 | 0.453 |
| no | **sí** *(la config que publican)* | 0.759 | 0.841 | 0.606 | 0.454 |
| **sí** | no | **0.766** | **0.846** | 0.605 | 0.452 |
| no | no | 0.755 | 0.836 | 0.571 | 0.414 |

**La fila que gana en mAcc y en bF1 es la de ponderación sola**, que es justamente la que
descartaron. Las tres primeras filas están dentro de 0.007 entre sí. **Lo único que la tabla
establece con claridad es que sacar las dos duele** (mF1 0.571 contra ~0.606, mPQ 0.414 contra
~0.453).

O sea que la conclusión correcta es **«hace falta una de las dos y cuál importa poco»**, no
«muestrear es mejor». Y los propios autores lo dicen así en la Discusión: la loss y el muestreo
«have varied impact on rare cell types, however with no clear best configuration» (L443-445). La
frase de §2.2 es la que se queda corta.

*(Observación nueva de esta lectura, no estaba en `hovernext_estudio.md`. No cambia ningún veredicto:
es una nota de mecanismo, no de números.)*

## 12. Qué entra y qué sale exactamente

Esta es la segunda pregunta del handoff, y la respuesta importa para la plomería de cualquier
go/no-go.

**Entra**: una **WSI** en un formato que OpenSlide sepa abrir, más una magnificación objetivo
(0,5 µm/px para los pesos de Lizard-Mitosis, 0,25 para los de PanNuke).

**Sale**: un mapa de instancias con una clase por instancia, en arrays **Zarr comprimidos con LZ4**,
con los mapas crudos cuantizados a 0-255 en el caché intermedio.

**El veredicto de plomería: el pipeline, tal como está, espera una lámina completa.** Dos razones
verificadas, y ninguna es de costo:

1. **El foreground sale del thumbnail de OpenSlide** (A.3). Un parche suelto no tiene thumbnail, así
   que el paso 1 no aplica y hay que saltearlo.
2. **El stitcher existe para resolver solapes entre ROI grandes** (A.2). Con parches sueltos no hay
   nada que pegar, así que la mitad de la Fig. 1A queda sin uso.

Nada de eso es imposible de rodear: por debajo el modelo es una U-Net que come tiles y devuelve
mapas, y el propio entrenamiento se hace sobre recortes de 256×256. Pero **es tocar el código, no
configurarlo**, y sin bajar el repo no se puede confirmar si la entrada por tiles está expuesta.

**Y hay un costo de borde, que importa si alguna vez se propone correrlo sobre parches sueltos.** El propio paper evalúa las métricas de detección de Lizard sobre **recortes centrales de
248×248** de tiles de 256, explícitamente «to avoid having to detect nuclei with their center
outside of the tile» (L269-271). Es decir: los núcleos del perímetro de un tile son un problema
conocido, y el pipeline de WSI lo resuelve con el solape del paso 2. **Un parche suelto de 256 px
tiene ese problema en todo su perímetro**, y a 0,465 µm/px un núcleo mide del orden de 15 a 20 px.
Sobre un parche aislado se perdería una franja perimetral que no es despreciable.

Lo cual, dicho sea de paso, refuerza por el lado del mecanismo lo que §7 del estudio ya decía por el
lado del costo: **correr la lámina entera no solo es barato, además es el modo para el que la
herramienta está construida.**

## 13. Lo que este documento no afirma

- **No afirma nada sobre rendimiento en nuestros datos.** No se corrió nada; todo sale del PDF y de
  nuestro propio estudio de HoVer-Net.
- **No afirma que los mapas HV se descarten en inferencia.** Dice que son auxiliares y que el
  pipeline documentado usa solo el BCB; la Fig. 1B admite la otra lectura y el código no se leyó.
- **No afirma que el BCB sea la causa del 17×.** Muestra lo contrario: con nuestra propia medición,
  el post-proceso era ~35 % del costo, así que el BCB compra del orden de 1,5× y el resto es
  ingeniería de inferencia.
- **La descomposición de costo del §4 no es una ablación.** Cruza nuestra medición de HoVer-Net con
  el número agregado del paper, en hardware y láminas distintas.
- **El código de color de la Fig. 5 es lectura visual**, no una cita del epígrafe.
- **No afirma que el pipeline no acepte parches sueltos**, solo que los dos primeros pasos
  documentados asumen una WSI y que averiguarlo exige el repo, que no está autorizado.
- **No reabre la rama de núcleos.** Sigue pausada desde el 31-jul; reabrirla es regla 9.b.
- **No propone implementar nada.** Es un documento de entendimiento.

## 14. Lo que quedó como pregunta de mecanismo

Cuatro cosas que solo se cierran con el código, y que valdría juntar si alguna vez se autoriza
clonarlo:

1. **¿Los mapas HV entran al post-proceso o no?** (§5)
2. **¿De qué lado va el λ = 0.02?** (§10)
3. **¿Las vistas de TTA se sortean o se enumeran?** (§8)
4. **¿La entrada por tiles sueltos está expuesta, o hay que escribirla?** (§12)

---

Relacionadas: [[hovernext-especialista-segunda-etapa]], [[pedagogia-nomenclatura-desde-cero]],
[[hovernet-ya-corriendo-sgaete]], [[papers-rama-mitosis-bcd]], [[topk-percentil-no-auc]],
[[anotaciones-patologo-qupath]], [[simil-hovernet-decision-31jul]],
[[cohortes-magnificacion-fisica]].
