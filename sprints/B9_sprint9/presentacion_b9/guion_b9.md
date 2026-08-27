# Guion hablado del deck del período (B9)

> Las siete láminas en un solo archivo, que es el método de `@humanizer-es`: se escribe
> entero, se pasa entero, y recién después `generate_b9_deck.py` lo lee y lo aplica con
> `notes()`. **Este archivo es la fuente**; las notas del `.pptx` son derivadas.
>
> Convención vigente ([[notas-presentador-guion-didactico]]): prosa hablada corrida, sin
> etiquetas de fase, sin números de trabajo ni nombres propios, sin ejemplos numéricos que
> no estén en la lámina. Desde el 27-ago **el deck entero va en español**, así que ya no hay
> desajuste entre lo que se lee y lo que se dice.
>
> El separador de bloque es `## [sNN]` y el generador parsea por ahí. No cambiar el formato
> sin tocar `leer_guion()`.

## [s01] Portada

Buenos días. Les voy a contar en qué quedó el período, que fue corto y tuvo un solo eje: la
detección de núcleos sobre las láminas que el patólogo ya nos anotó. Son seis láminas y la
idea es que la discusión quede para el final.

## [s02] OBJETIVOS

Al abrir el período nos pusimos tres cosas y quiero pasar por las tres con el estado real,
no con el estado que me gustaría.

La primera era escalar la detección de mitosis a más láminas anotadas, y ésa está cerrada.
Veníamos de haber medido una sola lámina y ahora están las doce que el patólogo marcó,
cruzadas contra sus marcas una por una.

La segunda era evaluar el detector para necrosis. Ahí llegamos hasta la decisión: sabemos
con qué pesos hay que correrlo y sabemos cuánto cuesta, pero no está lanzado, porque la
tarjeta lleva más de un día tomada por otra persona del equipo y no hay forma de colarse
antes. Está listo para salir el día que se libere.

Y la tercera era evaluar métricas nuevas para mitosis. Eso es lo que quedó en curso y es lo
que le da forma al período que viene, porque el ejercicio no fue proponer métricas lindas
sino separar cuáles se pueden calcular hoy con lo que ya está en disco, cuáles piden
tarjeta, y cuáles no se desbloquean con ningún presupuesto.

## [s03a] Mitosis sobre las doce láminas

Éste es el resultado del período. Sobre las doce láminas anotadas, el detector reencuentra
veintiséis de las noventa y cuatro marcas de mitosis del patólogo.

Antes del número, la condición para leerlo, porque sin ella significa otra cosa. Eso no es
el desempeño del detector sobre las mitosis que hay en la lámina. El denominador son las
marcas, y las marcas son positivos parciales: el patólogo señaló donde la evidencia es
clara, no todo lo que existe. Por eso tampoco hablamos de falsos positivos ni calculamos
precisión: una detección sin marca encima puede ser una mitosis real que nadie marcó, y no
tenemos cómo distinguirla de un error. Decir eso es parte del resultado, no una omisión.

El emparejamiento es uno a uno, así que ninguna detección se cuenta dos veces, y el
resultado no depende del corte que elijamos: es plano en todo el rango con el que la
literatura de mitosis trabaja. Mover la tolerancia no compra nada, y eso es bueno, porque
quiere decir que no hay un número escondido detrás de una elección nuestra.

Lo importante de la lámina es la segunda línea. La lámina que usamos todo el período
anterior como caso de referencia aporta ella sola la mitad de los aciertos. Sacándola, las
otras once dan diecinueve por ciento. O sea que el cincuenta por ciento con el que veníamos
trabajando no era el caso típico: era el mejor de doce. Todo lo que construimos apoyado en
esa lámina hereda ese sesgo, y prefiero decirlo acá antes de que aparezca más adelante.

## [s03b] Las marcas reencontradas

Las dos láminas que siguen son el mismo cruce, pero mirándolo una marca por vez. Me parece
que el número solo no alcanza para saber si esto anda o no anda, así que las puse todas.

Acá están las que sí. Cada recorte está centrado en una marca del patólogo, el anillo
blanco es esa marca y el amarillo es la detección que la acredita. Están agrupadas por
lámina y el rótulo dice cuántas aporta cada una.

Donde acierta, acierta encima del objeto. Los dos anillos caen prácticamente concéntricos,
muy por debajo de la tolerancia más chica que barrimos, y en casi todos se ve la figura
mitótica en el medio, con la cromatina condensada. No es un acierto de casualidad ni de
estar cerca: está sobre la célula.

Acá se ve también de dónde salen los aciertos. Son de cinco láminas nada más; las otras
siete no acreditan ninguna, así que acá no tienen ni un recorte.

## [s03c] Las marcas que se escapan

Y acá están las que no, que son la parte que más informa, porque es la única que muestra en
qué se equivoca.

Son las marcas para las que no hubo ninguna detección de mitosis dentro de la tolerancia.
Sólo está el anillo blanco del patólogo, y les pido que las miren con calma: en muchas se ve
perfectamente la figura mitótica que el detector no señaló. No es que la imagen sea mala ni
que la marca esté puesta sobre nada.

Que una marca se escape no la vuelve un error del patólogo, y al revés tampoco: una
detección que quede sin marca encima no es un falso positivo, porque bien puede ser una
mitosis real que no fue marcada. Por eso no van a ver un número de precisión en ninguna de
estas láminas.

Sobre las siete láminas que no acreditan ninguna marca, la sospecha natural es que estén
mal alineadas. No lo están, y hay dos razones. Donde algo empareja, empareja apretado, que
es lo que acaban de ver en la lámina anterior; y un desplazamiento global equivocado movería
todas las marcas de esa lámina por igual, así que no dejaría aciertos pegados junto a fallas
lejísimos dentro de la misma lámina. Además, casi todas las que dan cero son las que tienen
muy pocas detecciones en la lámina entera, y con esa densidad la distancia esperada a la
detección más cercana es enorme aunque la alineación sea perfecta.

## [s03d] Los ocho ejes

En la reunión pidieron mirar la herramienta más a fondo, así que en vez de quedarnos en
mitosis listamos contra qué se puede medir, en total, y le pusimos precio a cada cosa. El
contenido de esta lámina es la tabla; la línea de arriba dice cómo leerla.

El vocabulario del patólogo sobre estas doce láminas tiene veintiún etiquetas distintas, y
sólo dos aparecen en las doce. Todo lo demás vive en ocho láminas o menos, y siete etiquetas
viven en tres o menos. Eso ya ordena la lista sin que uno tenga que opinar. Los nombres de la
segunda columna están tal cual él los escribió, con sus mayúsculas y sus mezclas de idioma,
porque son las etiquetas del archivo y no conviene traducirlas.

Hay tres ejes que están pagados. Cuando corrimos el detector no escribió sólo mitosis:
escribió las siete clases y el polígono de cada núcleo, y eso está en disco para las doce.
Entonces grado nuclear y la separación entre epitelio y estroma, que a primera vista
parecían pedir tarjeta, son trabajo de procesador y de esta semana. El de epitelio contra
estroma me interesa especialmente porque es el control positivo natural del método: si un
segmentador de núcleos no acierta eso, no hay nada más que discutir.

Hay uno que sí pide tarjeta, que es necrosis, y ahí aparece una simetría incómoda entre los
dos juegos de pesos: el que tiene mitosis no tiene necrosis, y el que tiene necrosis no
tiene mitosis. Las dos cosas son ciertas a la vez y ninguna reabre lo que ya cerramos.

Y hay tres que son no, y quiero ser preciso en por qué, porque no es por presupuesto. En
esos tres el objeto de la tarea no es un núcleo. Uno pide reconocer una estructura, un
émbolo dentro de una luz revestida, y lo que tenemos es una población de núcleos. Otro pide
un depósito mineral, que además en su forma más frecuente es invisible en la tinción con la
que trabajamos. Y el tercero pide la glándula y su luz, que es una unidad más grande que la
célula. Correrlo más tiempo o con más láminas no los habilita: falta la clase, no el
cómputo.

Una cosa que atraviesa los ocho y que conviene dejar dicha. Contra este material no se
puede calcular precisión, ni efe uno, ni las métricas de calidad de segmentación que se
usan en los papers, en ningún eje. El archivo del patólogo no es una segmentación
exhaustiva ni son contornos de núcleo: son marcas puestas donde la evidencia es clara.

## [s04] Tareas del próximo período

Tres cosas para el período que viene.

La primera es correr necrosis en cuanto se libere la tarjeta, y ahí hay un prerrequisito
que no es de formato: el vocabulario de necrosis del patólogo viene inconsistente entre
mayúscula, minúscula y una tercera etiqueta, y hay que unificarlo y dejar declarado con qué
criterio. La medición no es un emparejamiento uno a uno como la de mitosis, porque el
patólogo dibujó áreas y la herramienta devuelve núcleos: se compara densidad dentro contra
fuera, y el nulo se construye trasladando la máscara, no permutando etiquetas, porque las
regiones son contiguas.

La segunda junta los dos ejes que ya están en disco, porque son un solo bloque de trabajo.
La pregunta concreta es si los descriptores de los núcleos ordenan los tres grados que el
patólogo declaró, y si la fracción de epitelio contra estroma se sostiene como control
positivo.

Y la tercera es la que tiene forma de entregable: el punto caliente mitótico. Conteo por
milímetro cuadrado, que es el número clínico con el que la escala de grado histológico
trabaja y que hoy no tenemos, el mapa de densidad, y la ventana de área fija que lo
maximiza. Eso es la primera versión de una zona que se le puede proponer al patólogo, que
es lo que se pidió al abrir el período.

Antes de cerrar, una cosa de coordinación que no está en la lámina y creo que hay que
resolver primero. Hay dos solapamientos con otra persona del equipo sobre este mismo
terreno: tiene un pipeline propio que compara atención contra anotaciones sobre varias
tareas, y está corriendo detección de mitosis con otro detector. Antes de escalar esto
conviene sentarse y repartir, porque si no vamos a medir dos veces lo mismo.
