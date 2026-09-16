# Guion hablado del deck de la reunión del 15-sep

> Las once láminas en un solo archivo, que es el método de `@humanizer-es`: se escribe entero,
> se pasa entero, y recién después `generate_b10_deck.py` lo lee y lo aplica con `notes()`.
> **Este archivo es la fuente**; las notas del `.pptx` son derivadas.
>
> Convención vigente ([[notas-presentador-guion-didactico]]): prosa hablada, un párrafo por
> viñeta separado por línea en blanco, sin etiquetas de fase, sin números de trabajo ni nombres
> propios, números en palabras y decimales según la regla 12 (uno tal cual, dos en decenas, tres
> en centenas). Lo que está escrito en la lámina se glosa la primera vez que aparece, no se evita
> (regla 13): CAP, fold, checkpoint, alcanzable, nulo, train, val, test, AUC, rama, «fuera del
> split», ensemble y proxy.
>
> El separador de bloque es `## [sNN]` y el generador parsea por ahí. Las líneas de un párrafo
> se juntan al leerlo: el envuelto a cien columnas es sólo para el editor.

## [s01] Portada

Buenos días. Traigo los tres encargos de la reunión pasada, los tres cerrados. Paso por cada uno
con su resultado y dejo para el final cinco preguntas, porque de lo que se conteste hoy depende
qué medimos en el período que viene.

## [s02] OBJETIVOS

Éstos son los tres encargos, en el orden en que los voy a presentar. Los tres cerraron el nueve
de septiembre.

El primero era replicar la medición del grado nuclear sin la marca del patólogo, usando solo el
detector de núcleos, HoVer-NeXt. El tamaño reencuentra las marcas de alto grado y no las de bajo.

El segundo era averiguar cómo se decide el score cuando en una misma lámina conviven núcleos de
grados distintos. El protocolo del Colegio Americano de Patólogos, el CAP, no trae una regla de
cantidad ni de mayoría: separa los scores por cuánta variación hay contra el epitelio mamario
normal.

El tercero era mirar primero el carcinoma ductal in situ, el CDIS, y después el grado. Para leer
esa fila hacen falta dos palabras de la tabla. El fold es una de las cinco particiones con que se
entrenó el modelo, cada una con sus láminas de entrenamiento, de validación y de prueba; y el
checkpoint es la versión del modelo con la que se queda ese fold. La atención cae sobre el CDIS
dibujado en las nueve láminas con etiqueta, pero ocho de ellas el fold las usó para entrenar o
para elegir el checkpoint. En las que no usó, la localización no está mostrada.

De las tareas que dejamos anotadas la vez pasada, la región mitótica, con la ventana de tres
milímetros cuadrados, quedó en la línea de mitosis con el reparto de la reunión pasada, y la
necrosis sigue en espera.

## [s03] HoVer-NeXt encuentra y clasifica cada núcleo

Todo lo que sigue se apoya en lo que entrega el detector, así que empiezo por ahí. HoVer-NeXt
recorre la lámina y devuelve cada núcleo por separado, con su contorno y una clase.

A la izquierda hay un cuadrado de medio milímetro de lado, con cada núcleo pintado según su clase.
Son mil ochocientos uno, y mil cuatrocientos noventa y siete son epiteliales, en verde. En amarillo
están los linfocitos, en azul las células del tejido conectivo, y en gris las otras cuatro clases
del detector, que acá son pocas.

El recuadro mide lo mismo que un parche de los que lee el modelo de atención, ciento diecinueve
micrones de lado, y a la derecha está ampliado. Ahí se ve el contorno de cada núcleo. El punto
negro es una marca de alto grado del patólogo, sobre el núcleo grande del centro.

Dos advertencias. Las clases son las del detector y nadie las revisó en estas láminas. Y el tamaño
no se compara entre clases, porque el detector recorta cada clase con un umbral distinto. Por eso
la medición del grado usa solo los núcleos epiteliales y los compara dentro de su propia lámina.

## [s04] El tamaño solo reencuentra el alto grado

Con eso vuelvo al primer encargo, el grado. La pregunta era si el detector, sin que nadie le diga
dónde están las marcas, llega a los mismos núcleos que marcó el patólogo.

Lo que hicimos fue ordenar por tamaño todos los núcleos epiteliales de cada lámina y quedarnos
con los N más grandes. Una marca cuenta como recuperada si el núcleo que tiene debajo está en esa
lista, con una tolerancia de quince micrones entre la marca y el núcleo.

En el eje horizontal está ese N, y debajo de cada valor, la superficie de los parches que
contienen esos núcleos, en milímetros cuadrados por lámina. La vertical marca quinientos, unos
cuatro milímetros cuadrados por lámina. Ahí se recuperan cuarenta y una de las setenta y seis
marcas de alto grado, doce de las cincuenta y tres de moderado y ninguna de las dieciséis de bajo.

Esos porcentajes son sobre las marcas alcanzables, que son las que caen sobre un núcleo que el
detector llamó epitelial: ciento cuarenta y cinco de ciento ochenta y siete. Las demás no las
recupera ningún orden, porque su núcleo no entra en la lista.

Las punteadas son el nulo, lo que da el azar, en su percentil noventa y siete coma cinco, que es
el valor que el azar casi nunca supera. Se construye moviendo todas las marcas de una lámina
juntas, como un bloque, a otro lugar del tejido, doscientas veces en cada lámina, y repitiendo la
cuenta. Así se conserva cómo el patólogo agrupa sus marcas y solo se rompe su relación con los
núcleos. En quinientos, el azar no pasa de tres marcas en total, contra cincuenta y tres
observadas.

Que bajo dé cero no es una falla: es lo que quiere decir bajo grado. Ese núcleo no suele estar
entre los más grandes de su lámina, y una lista de los más grandes lo deja afuera. Antes de ver
qué medir en su lugar, muestro las mismas marcas sobre el tejido.

## [s05] La carga de N = 500 sobre dos láminas

Así se ve la carga de quinientos sobre dos láminas: la de alto grado y la de bajo grado con más
marcas alcanzables. No las elegimos a ojo, salen de esa regla.

En cada par, a la izquierda está la lámina entera, y en verde los parches que contienen los
quinientos núcleos epiteliales más grandes. A la derecha, ampliada, la zona de las marcas, de poco
más de un milímetro de lado. El punto negro es una marca que cae dentro de la carga, o sea
recuperada, y el círculo blanco, una que no.

En la de alto grado quedan dentro cuatro de sus catorce marcas. Esa lámina tiene además dos
regiones de escaneo del mismo tejido, y casi la mitad de la carga se va a la otra región, donde no
hay marcas. En la de bajo grado no queda ninguna de nueve, aunque diecisiete parches de la carga
caen dentro de la zona ampliada: hay núcleos grandes cerca, pero no son los que marcó el patólogo.

Eso no los vuelve falsos positivos. El patólogo marca ejemplos y no todos los núcleos de un grado,
así que un núcleo grande sin marca no quiere decir que el orden se equivocó.

## [s06] Las marcas, núcleo a núcleo

Ahora núcleo a núcleo. Cada cuadro mide setenta y cuatro micrones de lado, todos a la misma escala.
El contorno grueso es el núcleo que está debajo de la marca, y el fino, los otros núcleos de la
lista de los quinientos más grandes que caen en el cuadro.

Arriba están las marcas recuperadas y abajo las que no. El puesto es el lugar del núcleo cuando se
ordenan por tamaño los de su lámina. Los cuadros tampoco están elegidos a mano: en cada grado van
el mejor puesto, el del medio y el peor entre las recuperadas, y entre las no recuperadas el del
primer cuarto y el del medio, cada uno de una lámina distinta.

Recuperadas y no recuperadas se parecen. Las no recuperadas de alto grado están en los percentiles
noventa y ocho coma ocho y noventa y siete coma seis de su lámina: son núcleos grandes que quedan
fuera de los quinientos por poco. En bajo grado no hay ninguna recuperada, y las dos del panel
están en los percentiles setenta y seis coma tres y ochenta y nueve coma tres.

Por eso el tamaño reencuentra una parte del alto grado y nada del bajo. Para moderado y bajo hace
falta medir otra cosa, y la lámina siguiente dice qué.

## [s07] El CAP no cuenta núcleos

Sobre el score, lo que se quería saber era si gana la mayoría o si hay alguna regla de cantidad
cuando en una lámina conviven núcleos de grados distintos. Fuimos al protocolo del CAP, que es el
que usa el proyecto para definir las clases, y no hay ninguna de las dos.

Arriba están los tres scores de pleomorfismo del carcinoma invasivo, con la frase textual del
protocolo debajo de cada uno: poca variación de tamaño, variación moderada de tamaño y forma,
variación marcada de tamaño y forma. Lo que los separa es cuánto varían los núcleos, y la
comparación es contra el epitelio mamario normal, no contra el resto de la lámina. En ningún lado
dice cuántos núcleos grandes hacen falta ni qué fracción del tumor.

Abajo están las dos únicas partes del protocolo que traen un número. A la izquierda, el grado
nuclear del CDIS: usa seis rasgos, y el único con un corte numérico es el tamaño, entre una vez y
media y dos veces un núcleo epitelial normal para el grado uno, y más de dos veces y media para
el grado tres. El intermedio queda definido por descarte. El protocolo no dice si ese tamaño es
diámetro o área, y no da lo mismo: si es diámetro, en área el corte queda elevado al cuadrado.

A la derecha, el componente mitótico, que es el único que es un conteo y el único que dice dónde
mirar: diez campos de gran aumento en la parte del tumor con más mitosis.

Lo que el protocolo no dice es justo lo que se preguntó: qué hacer cuando el grado varía dentro
de un mismo carcinoma. Solo pide reportar aparte los carcinomas distintos. La consecuencia para
el método es concreta: lo fiel al protocolo no es el tamaño de los núcleos más grandes sino la
dispersión del tamaño, medida contra epitelio normal.

## [s08] La atención cae sobre el CDIS ya visto

El tercer encargo cambia el orden: mirar primero el CDIS y medir el grado solo ahí. Para eso hace
falta que la atención del modelo ya encuentre el CDIS, y lo medimos con el AUC por lámina, que
acá es la probabilidad de que la atención ponga un parche con CDIS dibujado por encima de uno sin
CDIS. Cero coma cinco es el azar.

Cada fila es una lámina, agrupada según el papel que jugó en el fold. Train son las láminas con
que el modelo aprendió. Val son las que usó para elegir el checkpoint. Test es la única que no
usó para nada. Y la de abajo está fuera del split, o sea que no cayó en ninguno de los tres
grupos.

Las nueve láminas con etiqueta quedan sobre el azar, con una mediana de cero coma setecientos
cincuenta y cinco. Pero ocho de las nueve el modelo ya las había visto, en train o en val. Lo que
esto muestra es que la atención se concentra en el CDIS de láminas conocidas.

Las dos que no vio no alcanzan para decir que localiza en láminas nuevas. La de test tiene solo
dos parches con CDIS, y su intervalo cruza el azar. La que está fuera del split no tiene
etiqueta, así que se leyó como positiva, que es lo que implican sus polígonos, y se midió solo
dentro de su región anotada: da cero coma doscientos uno, por debajo del azar. Eso no quiere
decir que la atención evite el CDIS. Esa lámina tiene la alineación de sus anotaciones sin
verificar, que es lo que marca la cruz, y así no se distingue entre que el modelo mire a otro
lado y que el dibujo esté corrido.

Una advertencia que sirve para cualquier análisis de atención con este modelo. La atención se
calcula por separado para cada clase, y a cada una le decimos rama. Hay que leer la rama de la
clase verdadera. Si se lee la de la clase que el modelo predice, el resultado se borra en una
lámina y aparece en otra donde no estaba. Los mapas de atención que guarda el ensemble de los
cinco folds se escribieron con la rama predicha, así que heredan ese riesgo.

## [s09] Dónde mira la atención en tres láminas

Detrás de esos números hay mapas como estos tres, todos del checkpoint de un fold y con la rama que
corresponde. Arriba está cada lámina entera, con la atención en colores: rojo es más atención y azul
menos, y el color es el percentil, o sea el lugar del parche en el orden de atención de su lámina. El recuadro negro marca la zona ampliada abajo, de casi dos milímetros de lado, alrededor
del CDIS que dibujó el patólogo, en blanco.

La de la izquierda es de train, una lámina con la que el modelo aprendió, y la de AUC más alto,
cero coma novecientos veintinueve. Los parches dentro del CDIS están en rojo, entre los de más
atención de la lámina.

La del medio es la de test, la única que el modelo no usó. Su CDIS son dos parches, que en promedio
quedan por encima de la mitad de la lámina, pero con dos parches el intervalo cruza el azar y el
número no se puede leer.

La de la derecha es la que quedó fuera del split, medida solo en su región anotada. El polígono con
más parches cae en azul, y otro de sus polígonos no contiene ningún parche: cae sobre el vidrio.
Esa lámina tiene la alineación de las anotaciones sin verificar, y un polígono sobre el vidrio puede
ser eso, un dibujo corrido. Si lo es, un AUC bajo no dice que el modelo mire a otro lado.

## [s10] Las cinco preguntas

Antes de las tareas, cinco preguntas, ordenadas por lo que cuesta si se contestan tarde. Las dos
primeras deciden qué mide el período que viene.

La primera es qué región corresponde para medir el pleomorfismo. Las regiones marcadas como
tumor no sirven: ninguna de las marcas de grado cae dentro de un polígono, de ninguna clase, y el
polígono de tumor más cercano queda, en mediana, a dos coma nueve milímetros. Son recortes de
ejemplo y no el contorno del tumor. Mientras no haya respuesta, todo se mide sobre la lámina
entera.

La segunda es qué son las marcas de grado: pleomorfismo del carcinoma invasivo o grado nuclear
del CDIS. Siguen la etiqueta de pleomorfismo de la lámina, y ocho láminas con marcas de grado no
tienen CDIS, donde no puede haber grado nuclear de CDIS. La respuesta decide qué máscara usar y
si lo que medimos es lo que se pidió.

Después vienen tres conteos que cambiaron con el set completo, y conviene confirmarlos. Las
marcas de núcleos de bajo grado son dieciséis y no veinticinco, porque una lámina estaba
exportada dos veces. Las marcas de grado están en veintidós láminas y no en doce. Y de las treinta
láminas que se mencionaron faltan ocho, no dieciocho.

La cuarta pregunta sale de ahí: cuáles son esas ocho láminas y cuándo llegan, porque decide si el
período que viene mide sobre veintidós láminas o sobre treinta.

La última es cómo seguimos con la idea de mirar primero el CDIS y después el grado, si la
localización del CDIS no está mostrada en láminas que el modelo no vio. De paso, la lámina que
quedó fuera del split no tiene fila en la tabla de etiquetas de CDIS: conviene saber si es un
olvido o si esa lámina está fuera de la cohorte.

## [s11] Tareas del próximo período

Para el período que viene propongo una sola tarea firme, para el veintidós de septiembre: medir
la dispersión del tamaño nuclear en cada lámina, con el coeficiente de variación y el rango
intercuartil, que es lo que describe el protocolo.

La referencia es un proxy del epitelio normal, o sea un sustituto, porque no hay epitelio normal
marcado: los núcleos epiteliales que quedan fuera de toda región anotada. Lo vamos a llamar proxy
en todas las tablas, porque ese sustituto confunde lo normal con lo que no está marcado.

Esa medición corre sobre la región que se decida en la primera pregunta. El resto de las tareas
depende de lo que se conteste hoy.
