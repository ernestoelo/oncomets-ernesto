# Guion hablado del deck del período (B9)

> Las once láminas en un solo archivo, que es el método de `@humanizer-es`: se escribe
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
detección de núcleos sobre las láminas que el patólogo ya nos anotó. Son diez láminas y la
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

Y la tercera era evaluar métricas nuevas para mitosis, y ésa también quedó cerrada. El
ejercicio no fue proponer métricas lindas sino separar cuáles se pueden calcular hoy con lo
que ya está en disco, cuáles piden tarjeta y cuáles no se desbloquean con ningún
presupuesto. Y de las que se podían calcular hoy, las dos que valían la pena están medidas
y las van a ver en el medio de la presentación.

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

## [s03d] El control positivo

Antes de seguir, dos ejes que ya estaban pagados y que corrimos esta semana. Éste es el
primero y es el control positivo del método.

El patólogo dibujó regiones y les puso nombre: unas son epitelio y otras son estroma. Nosotros
contamos, dentro de cada una, qué fracción de los núcleos que el detector encontró ahí adentro
son epiteliales. Si un segmentador de núcleos no acierta eso, no hay nada más que discutir, así
que es lo mínimo exigible.

Y lo acierta. Las dos clases de estroma dan cero exacto en la mediana, o sea que en la mitad
de esas regiones no aparece un solo núcleo epitelial, y las regiones sólidas de epitelio
quedan todas arriba. Cada fila es una clase tal como él la escribió, la barra es el rango
intercuartil y la marca oscura es la mediana. La unidad acá es la región, no la lámina ni la
marca.

Hay una fila que se sale del patrón. Una de las clases de epitelio se comporta como estroma.
Son seis marcas de una sola lámina, así que no aguanta un número propio: queda anotado y no lo
interpreto. La sospecha razonable es que ese patrón tiene ejes
de tejido conectivo por dentro, pero eso hay que preguntarlo, no afirmarlo.

Procedencia: results/b9_nucleos/regiones_epi_estroma.csv, vía scripts/b9_epitelio_estroma.py.
Unidad: región.

## [s03e] El observado contra su nulo

El número que resume esa separación es un área bajo la curva de rangos, y sola no dice mucho,
así que la puse contra su propio nulo, que es lo que contesta si podía haber salido por azar.

El nulo se arma trasladando la máscara de cada región sobre el tejido de su propia lámina, y
me quiero detener ahí un segundo porque es una decisión y no un detalle. Lo cómodo sería
barajar las etiquetas de las regiones, pero las regiones son contiguas, así que barajarlas
rompe la estructura espacial y el nulo sale demasiado fácil de vencer. Trasladar la conserva.

Ninguna traslación llega al observado. La marca de acento queda sola a la derecha y el
percentil de arriba del nulo está más de veinte puntos por debajo.

Dos cosas para leerlo bien. La primera es que el valor de significancia es un piso y no un
valor exacto: con la cantidad de traslaciones que corrimos, lo mínimo que puede dar es uno
sobre doscientos uno, y dio exactamente eso, así que se lee como por debajo de uno en
doscientos uno. La segunda es que el nulo no se centra en la mitad sino un poco más abajo, y
tiene explicación: las regiones de epitelio son más grandes que las de estroma, así que al
trasladarlas no muestrean el mismo fondo. No invalida el contraste, pero conviene decirlo
antes de que alguien lo pregunte.

Procedencia: results/b9_nucleos/regiones_nulo.npy, doscientas traslaciones por región, vía
scripts/b9_epitelio_estroma.py. Unidad: región.

## [s03f] El grado nuclear

El segundo eje es el grado nuclear. Acá el patólogo marcó núcleos sueltos, no áreas, y les
puso uno de tres niveles: bajo, moderado y alto.

Lo que medimos es el tamaño del núcleo que la herramienta segmentó debajo de cada marca, pero
no en micrones sino como percentil dentro de la población epitelial de la propia lámina. Eso
es a propósito. Entre láminas el tamaño nuclear medio cambia por un factor dos, y el percentil
cancela justamente esa diferencia.

Los tres grados ordenan, y ordenan en la dirección esperada. Cada punto es una lámina, puesta
en la mediana de sus marcas, y los dos puntos huecos son las dos láminas cuyo alineamiento
quedó marcado como dudoso.

Y ahora la parte incómoda, que es el tamaño real de esto. El grado está confundido con la
lámina sin un solo cruce: cada lámina tiene un único grado. Entonces comparar grados es
comparar láminas, y el número honesto de observaciones son diez láminas y no las marcas. La
tabla de la derecha está para eso, para que se vea de dónde sale cada punto y con cuántas
marcas.

Falta decir otras dos. Los percentiles son altos en los tres grados, el bajo incluido: él
marca núcleos grandes para su lámina en cualquier grado, y lo que separa es cuánto. Y esto no
valida la escala de grado histológico. Esa escala puntúa la variación de una población entera en el
peor campo; lo que tenemos acá son núcleos que él eligió como ejemplares.

Procedencia: results/b9_nucleos/marcas_grado.csv, columna del percentil intra lámina, vía
scripts/b9_pleomorfismo.py. Unidad: lámina.

## [s03g] El nulo exacto del grado

Con ese eje hicimos lo mismo que con el control positivo, ponerlo contra su nulo. Como son
diez láminas no hace falta simularlo: se enumeran todas las formas de repartir los grados
entre ellas y se cuentan. Es exacto.

Las dos poblaciones estaban declaradas de antemano y las reporto juntas. Arriba está la
limpia, que se queda solo con las marcas que cayeron sobre un núcleo epitelial. Abajo está la
completa, con las ciento siete.

La limpia despega del nulo y la completa no, y las dos cosas hay que decirlas con cuidado.

Sobre la limpia: el valor que salió es el mínimo que este diseño puede dar. El reparto que
observamos es el único de todos los posibles que ordena perfecto, así que no existe un
resultado mejor disponible con estas láminas. Leerlo como un margen cómodo contra el corte de
siempre sería un error. No hay margen, hay techo.

Sobre la completa, que uno esperaría que fuera mejor por tener más láminas: no la frena el
diseño. Ahí sí había disponible un valor mucho más chico. Lo que la frena son dos láminas de
grado alto que caen por debajo de las de grado bajo, y las dos tienen sus marcas resueltas a
clases que no son epitelio. El tamaño que devuelve el detector no es comparable entre clases,
porque el umbral con el que recorta cada núcleo está afinado por clase. O sea que la diferencia
entre las dos poblaciones tiene mecanismo, no es ruido.

Entonces la lectura honesta es que ordena, con esos dos valores y esos dos denominadores.
Nada más fuerte que eso.

Procedencia: la misma enumeración que produjo el número, permutacion_exacta de
scripts/b9_pleomorfismo.py. Unidad: asignación.

## [s03h] Los ocho ejes

En la reunión pidieron mirar la herramienta más a fondo, así que en vez de quedarnos en
mitosis listamos contra qué se puede medir, en total, y le pusimos precio a cada cosa. El
contenido de esta lámina es la tabla; la línea de arriba dice cómo leerla.

El vocabulario del patólogo sobre estas doce láminas tiene veintiún etiquetas distintas, y
sólo dos aparecen en las doce. Todo lo demás vive en ocho láminas o menos, y siete etiquetas
viven en tres o menos. Eso ya ordena la lista sin que uno tenga que opinar. Los nombres de la
segunda columna están tal cual él los escribió, con sus mayúsculas y sus mezclas de idioma,
porque son las etiquetas del archivo y no conviene traducirlas.

Hay tres ejes que están pagados, y dos de ellos son los que acaban de ver. Cuando corrimos
el detector no escribió sólo mitosis: escribió las siete clases y el polígono de cada
núcleo, y eso quedó en disco para las doce. Por eso el grado nuclear y la separación entre
epitelio y estroma, que a primera vista parecían pedir tarjeta, salieron con trabajo de
procesador y de esta misma semana. El tercero es el infiltrado inmune, que cuesta lo mismo
y no lo corrimos por otro motivo: son muy pocas marcas y en muy pocas láminas, así que no
sostendría un número propio.

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

Dos cosas para el período que viene.

La primera es correr necrosis en cuanto se libere la tarjeta, y ahí hay un prerrequisito
que no es de formato: el vocabulario de necrosis del patólogo viene inconsistente entre
mayúscula, minúscula y una tercera etiqueta, y hay que unificarlo y dejar declarado con qué
criterio. La medición no es un emparejamiento uno a uno como la de mitosis, porque el
patólogo dibujó áreas y la herramienta devuelve núcleos: se compara densidad dentro contra
fuera, y el nulo se construye trasladando la máscara, no permutando etiquetas, porque las
regiones son contiguas.

Y la segunda es la que tiene forma de entregable: el punto caliente mitótico. Conteo por
milímetro cuadrado, que es el número clínico con el que la escala de grado histológico
trabaja y que hoy no tenemos, el mapa de densidad, y la ventana de área fija que lo
maximiza. Eso es la primera versión de una zona que se le puede proponer al patólogo, que
es lo que se pidió al abrir el período.

Antes de cerrar, una cosa de coordinación que no está en la lámina y creo que hay que
resolver primero. Hay dos solapamientos con otra persona del equipo sobre este mismo
terreno: tiene un pipeline propio que compara atención contra anotaciones sobre varias
tareas, y está corriendo detección de mitosis con otro detector. Antes de escalar esto
conviene sentarse y repartir, porque si no vamos a medir dos veces lo mismo.
