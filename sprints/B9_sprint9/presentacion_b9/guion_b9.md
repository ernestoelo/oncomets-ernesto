# Guion hablado del deck del período (B9)

> Las trece láminas en un solo archivo, que es el método de `@humanizer-es`: se escribe
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
>
> Pasado por `@humanizer-es` el 4-sep. Los cierres «Procedencia: … Unidad: …» que tenían
> `[s03d]` y `[s03f]` salieron: leían paths en voz alta, y las dos láminas ya declaran su
> unidad en el pie nativo.

## [s01] Portada

Buenos días. Les voy a contar en qué quedó el período, que fue corto y tuvo un solo eje: la
detección de núcleos sobre las láminas que el patólogo ya nos anotó. Son doce láminas y la
idea es que la discusión quede para el final.

## [s02] OBJETIVOS

Al abrir el período nos pusimos tres cosas y voy a pasar por las tres con el estado real,
no con el estado que me gustaría.

La primera era escalar la detección de mitosis a más láminas anotadas, y ésa está cerrada.
Veníamos de haber medido una sola lámina y ahora están las doce que el patólogo marcó,
cruzadas contra sus marcas una por una.

La segunda era evaluar el detector para necrosis. Ahí llegamos hasta la decisión: sabemos
con qué pesos hay que correrlo y sabemos cuánto cuesta, pero no está lanzado, porque la
tarjeta lleva más de un día tomada por otra persona del equipo y no hay forma de colarse
antes. Está listo para salir el día que se libere.

La tercera era evaluar métricas nuevas para mitosis, y también quedó cerrada. El ejercicio
no fue proponer métricas lindas sino separar cuáles se pueden calcular hoy con lo que ya
está en disco, cuáles piden tarjeta y cuáles no se desbloquean con ningún presupuesto. De
las que se podían calcular hoy, las dos que valían la pena están medidas y las van a ver en
el medio de la presentación.

## [s03hn] Cómo funciona el detector

Antes del resultado, medio minuto sobre la herramienta, porque quedó una pregunta dando
vueltas de la reunión pasada y es cuánto mide lo que el detector mira.

El detector no clasifica la lámina entera de una vez. La recorre en teselas, y de cada tesela
devuelve el contorno de cada núcleo y a qué clase pertenece. La cadena de la derecha es esa
geometría, y la sacamos del código y no del paper, porque el paper describe el método y lo que
hacía falta era el número exacto sobre nuestras láminas.

Dos cosas conviene saber. La primera es que el parámetro que en su configuración se llama
solapamiento no es un solapamiento sino un paso: define cada cuánto se planta la tesela
siguiente, y lo que finalmente escribe es el centro, así que los bordes le sirven nada más de
contexto. La segunda es la magnificación. Los pesos que usamos están entrenados a veinte
aumentos y nuestras láminas están casi exactamente ahí, dentro de la tolerancia que él mismo
declara, así que lee el nivel original sin reescalar nada. Eso importa porque un remuestreo
silencioso habría cambiado el tamaño de todo lo que viene después.

El último bloque es la razón de ser de la lámina. La tesela del detector, sobre estas láminas,
mide lo mismo que un parche del modelo de atención. Exactamente lo mismo. Por eso más adelante
vamos a poder recortar por parches de atención y hablar de lo que el detector encontró sin estar
mezclando dos rejillas distintas. Si no midieran lo mismo, ese cruce habría que justificarlo;
como miden lo mismo, no hay nada que justificar.

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

La segunda línea es lo importante de la lámina. La lámina que usamos todo el período anterior
como caso de referencia aporta ella sola la mitad de los aciertos. Sacándola, las otras once dan
diecinueve por ciento. O sea que el cincuenta por ciento con el que veníamos trabajando no era
el caso típico: era el mejor de doce. Todo lo que construimos apoyado en esa lámina hereda ese
sesgo, y va a reaparecer más adelante.

## [s03b] Las marcas reencontradas

Las dos láminas que siguen son el mismo cruce, pero mirándolo una marca por vez. El número
solo no alcanza para saber si esto anda o no anda, así que las puse todas.

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

Éstas son las que no, y son la parte que más informa, porque es la única que muestra en qué
se equivoca.

Son las marcas para las que no hubo ninguna detección de mitosis dentro de la tolerancia.
Sólo está el anillo blanco del patólogo, y vale la pena mirarlas con calma: en muchas se ve
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

## [s03at] La atención sobre las marcas

Ahora el primero de los dos ejes que abrimos esta semana sobre el modelo de atención. La
pregunta es simple: cuando el modelo mira una lámina y decide su nivel de mitosis, ¿le presta
atención a los lugares donde el patólogo marcó mitosis, o mira otra cosa?

Las doce láminas están con el mapa de atención encima del tejido, y los anillos son los parches
donde hay una marca de mitosis. La respuesta corta es que sí, y bastante bien. El número, eso
sí, viene con una condición, y la condición va antes.

Ese mapa sale de un ensemble de los cinco pliegues del entrenamiento. Cada una de estas láminas
estuvo en el entrenamiento de alguno de ellos, así que el modelo ya las vio. Está contaminado
por construcción, y por eso no lo presento solo. Al lado están los otros dos brazos: el mismo
cálculo con una familia de modelos limpia, y después el mismo cálculo quedándonos, para cada
lámina, sólo con los pliegues que nunca la vieron.

El orden en que quedan es lo que hay que mirar. El contaminado da más alto, el intermedio queda
en el medio y el limpio queda abajo. Ese orden lo dejamos escrito antes de correr nada,
precisamente porque es lo que tenía que pasar si el mecanismo es el que creemos. Si hubiera
salido al revés no sería un descubrimiento, sería un error en la tabla de qué lámina estuvo en
qué pliegue.

Aun con el brazo limpio, que es el honesto, las nueve láminas que se pueden medir quedan todas
por encima del azar. O sea que el resultado no vive de la contaminación.

Hay una cosa que no sabemos y está en el pie. Cuánto infla exactamente ese ensemble respecto de
un modelo limpio de su propia familia no lo medimos. Lo que medimos es cuánto infla la
contaminación dentro de una misma familia, y eso no se traslada. Lo digo para que no quede la
impresión de que el primer número ya está descontado.

## [s03es] La escalera de área

Para esto sirve. Si la atención señala dónde están las mitosis, entonces se puede usar para
recortar: en vez de darle al patólogo la lámina entera, darle la parte que el modelo señala.

La pregunta es cuánto se pierde al recortar, y la respuesta está en esta escalera. Cada barra es
un presupuesto de superficie por lámina, desde la lámina completa hasta un milímetro cuadrado, y
a la derecha está cuántas de las marcas acreditadas siguen adentro.

Hay algo que tiene que quedar clarísimo porque es fácil leerlo al revés. Recortar no puede
aumentar el conteo. El detector ya corrió sobre las láminas completas, así que cualquier recorte
es un subconjunto de lo que ya encontró y el número sólo puede bajar. Lo que compra el recorte
no son mitosis, es superficie: menos tejido para mirar.

El trato es bueno. Bajando a un veinteavo de la superficie se conserva más de la mitad de las
marcas, contra casi ninguna si el recorte fuera al azar con la misma cantidad de parches. Ése es
el resultado.

La otra lectura está en la columna del medio. Ahí hicimos el mismo ejercicio pero usando la
atención de otra cabeza del modelo, la que decide si hay carcinoma invasivo. Esa se derrumba: en
el mismo presupuesto retiene la tercera parte, y en el más chico no retiene ninguna. O sea que
esto no es que la atención en general caiga sobre tejido interesante. Localizar mitosis lo hace
la cabeza de mitosis. La cabeza decide, y elegirla mal es la diferencia entre que funcione y que
no funcione.

## [s03d] El control positivo

Antes de seguir, dos ejes que ya estaban pagados y que corrimos esta semana. Éste es el
primero y es el control positivo del método.

El patólogo dibujó regiones y les puso nombre: unas son epitelio y otras son estroma. Nosotros
contamos, dentro de cada una, qué fracción de los núcleos que el detector encontró ahí adentro
son epiteliales. No es un resultado interesante en sí mismo: es la condición para que cualquier
resultado posterior signifique algo. Si un segmentador de núcleos no acierta esto, no hay nada
más que discutir.

Y lo acierta. Las dos clases de estroma dan cero exacto en la mediana, o sea que en la mitad
de esas regiones no aparece un solo núcleo epitelial, y las regiones sólidas de epitelio
quedan todas arriba. Cada fila es una clase tal como él la escribió, la barra es el rango
intercuartil y la marca oscura es la mediana. La unidad acá es la región, no la lámina ni la
marca.

Hay una fila que se sale del patrón. Una de las clases de epitelio se comporta como estroma.
Son seis marcas de una sola lámina, así que no aguanta un número propio: queda anotado y no lo
interpreto. La sospecha razonable es que ese patrón tiene ejes de tejido conectivo por dentro,
pero eso hay que preguntarlo, no afirmarlo.

## [s03re] Las regiones sobre tejido

Lo mismo, ahora sobre el tejido en vez de sobre un gráfico, porque el gráfico dice que acierta
y esto deja verlo.

Acá están cuatro de esas regiones, dos que él llamó epitelio y dos que llamó estroma, y encima
cada núcleo que el detector encontró adentro, pintado del color de su clase. Son los colores del
propio detector, no los nuestros.

Las dos de la izquierda son casi todo verde. Las dos de la derecha no tienen un solo punto
verde: cero exacto, no cero redondeado. Y el tejido se ve, que es la gracia: en las de la
derecha se nota a ojo que son haces de estroma y en las de la izquierda se ven las glándulas. O
sea que el detector está de acuerdo con el patólogo sobre algo que se puede verificar mirando.

Elegimos las que tenían más núcleos adentro, entre las regiones cuyo alineamiento está
confirmado.

## [s03f] El grado nuclear

El segundo eje es el grado nuclear. Acá el patólogo marcó núcleos sueltos, no áreas, y les
puso uno de tres niveles: bajo, moderado y alto.

Medimos el tamaño del núcleo que la herramienta segmentó debajo de cada marca, pero no en
micrones sino como percentil dentro de la población epitelial de la propia lámina. Eso es a
propósito. Entre láminas el tamaño nuclear medio cambia por un factor dos, y el percentil
cancela justamente esa diferencia. Si comparáramos micrones contra micrones estaríamos midiendo
la lámina y no el núcleo.

Los tres grados ordenan, y ordenan en la dirección esperada. Cada punto es una lámina, puesta
en la mediana de sus marcas, y los dos puntos huecos son las dos láminas cuyo alineamiento
quedó marcado como dudoso.

Ahora el tamaño real de esto. El grado está confundido con la lámina sin un solo cruce: cada
lámina tiene un único grado. Entonces comparar grados es comparar láminas, y el número honesto
de observaciones son diez láminas y no las marcas. La tabla de la derecha está para eso, para
que se vea de dónde sale cada punto y con cuántas marcas.

Falta una salvedad. Esto no valida la escala de grado histológico. Esa escala puntúa la
variación de una población entera en el peor campo; lo que tenemos acá son núcleos que él eligió
como ejemplares.

## [s03nu] Los núcleos contra su lámina

Un percentil es abstracto, así que acá está el mismo percentil hecho imagen.

Cada fila es una lámina. Los cuatro primeros recortes son núcleos de esa misma lámina ordenados
por tamaño: uno chico, uno mediano, uno grande y uno muy grande, siempre dentro de su propia
población. El quinto, el del recuadro, es el núcleo que el patólogo marcó. Todos a la misma
escala y con la misma barra de referencia.

Recorriendo la figura se ve que el núcleo marcado casi siempre queda a la altura de los dos
últimos de su fila, o más allá. En los tres grados, el bajo incluido. Él marca núcleos grandes
para su lámina siempre; lo que separa un grado de otro es cuánto más grandes. Eso también
explica por qué el percentil se calcula dentro de cada lámina: si el grado bajo ya está arriba
en la suya, el corte no puede ser un tamaño absoluto.

Una cosa más, que es un límite de lo que están viendo. Lo que dibujamos es el núcleo que
segmentó la herramienta debajo de la marca, no el contorno que trazó el patólogo. El área de ese
contorno depende en parte del grosor del pincel con el que él lo dibujó, así que como medida de
tamaño no serviría.

## [s04] Tareas del próximo período

Dos cosas para el período que viene.

La primera es correr necrosis en cuanto se libere la tarjeta, y ahí hay un prerrequisito
que no es de formato: el vocabulario de necrosis del patólogo viene inconsistente entre
mayúscula, minúscula y una tercera etiqueta, y hay que unificarlo y dejar declarado con qué
criterio. La medición no es un emparejamiento uno a uno como la de mitosis, porque el
patólogo dibujó áreas y la herramienta devuelve núcleos: se compara densidad dentro contra
fuera, y el nulo se construye trasladando la máscara, no permutando etiquetas, porque las
regiones son contiguas.

La segunda es la que tiene forma de entregable: el punto caliente mitótico. Conteo por
milímetro cuadrado, que es el número clínico con el que la escala de grado histológico
trabaja y que hoy no tenemos, el mapa de densidad, y la ventana de área fija que lo
maximiza. Eso es la primera versión de una zona que se le puede proponer al patólogo, que
es lo que se pidió al abrir el período.

Antes de cerrar, una cosa de coordinación que no está en la lámina y conviene resolver
primero. Hay dos solapamientos con otra persona del equipo sobre este mismo terreno: tiene un
pipeline propio que compara atención contra anotaciones sobre varias tareas, y está corriendo
detección de mitosis con otro detector. Antes de escalar esto hay que sentarse y repartir, o
vamos a medir dos veces lo mismo.
