# Guion recortado · deck del 24-ago

> Recorte de `guion_borrador_24ago.md` (7160 palabras) con la pasada de `@humanizer-es`
> incorporada. Este es el texto que va a las 17 llamadas `notes()` del generador.

---

## L1 · Portada

Traigo cuatro cosas, y las puse en ese orden a propósito.

Empiezo por un encargo que quedó del sprint pasado y ya cerró: si al modelo con expertos le sobra capacidad por dentro, y de qué lado conviene recortarla. Da un resultado negativo y lo dejo cerrado ahí mismo.

Sigue una medición nuestra: si el modelo mira donde el patólogo marcó las mitosis. Cambió hacia dónde apunta el trabajo, y me voy a detener en cómo se mide, porque el número hay que poder defenderlo.

Después, la revisión de uno de los papers encargados, que propone un modelo que se explica solo. Es una lectura terminada y la cuento comprimida.

Y al final lo que más quiero discutir: un segundo modelo, que trabaja a nivel de núcleo, corriendo sobre el mapa de atención del nuestro. Es el encadenamiento que quedó pedido en la reunión anterior, y ya tiene mapas, número y cuatro láminas.

## L2 · Objetivos del sprint

Los seis objetivos del sprint, y en qué quedó cada uno.
Los cuatro primeros estaban propuestos desde el arranque y están cerrados.
Los dos últimos aparecieron durante el sprint y siguen en curso.

Los dos primeros son el encargo del modelo con expertos: escalar a la tarea completa la medición de capacidad, que veníamos arrastrando de siete láminas, y decidir de qué lado conviene recortar. Los dos cerrados, y el primero es la lámina que sigue.

El tercero es la medición de atención contra las marcas del patólogo, y el cuarto, elegir y justificar hacia dónde sigue la rama de mitosis. También cerrados, y ocupan el grueso de lo que traigo.

Los dos últimos no estaban en el plan de marzo: aparecieron durante el sprint, porque el tercero salió como salió. Investigar e implementar un modelo de detección de mitosis por núcleo, y encadenarlo con la atención para cruzar sus detecciones contra las marcas. Están en curso: el modelo ya corrió y ya hay número, pero medido sobre una sola lámina, y el barrido de las doce anotadas sigue en la cola.

## L3 · ¿Recortar expertos o slots?

Un encargo que quedó del sprint pasado y que este sprint cerró.
El modelo tiene 30 expertos y 10 unidades por experto: 300 en total.
A igual capacidad total, ¿conviene recortar por un lado o por el otro?
Arriba, la diferencia pareada; abajo, qué cuesta ir sacando capacidad.

Empiezo por acá porque es lo más corto. El sprint pasado medimos cómo se reparte el peso entre esas trescientas unidades sobre siete láminas; lo escalamos a las mil ciento setenta y seis de prueba y el número aguanta: se ocupan unas ciento sesenta unidades y los treinta expertos se usan los treinta. De ahí salía que, si sobraba capacidad, sobraba del lado de las unidades. La figura de arriba lo pone a prueba, a igual capacidad total y sobre las mismas particiones.

Cómo se lee. Arriba está escrita la magnitud: la diferencia de área bajo la curva entre los dos recortes, partición por partición. La línea vertical del medio es el cero, y la escala llega a una décima de área bajo la curva hacia cada lado. La barra oscura es el promedio, y sale del cero hacia el lado que gana: a la derecha si conviene recortar unidades, a la izquierda si conviene recortar expertos. La línea gris que la atraviesa es cuánto se mueve entre las cinco particiones. Y los cinco cuadraditos son las particiones: relleno oscuro cuando ésa votó a favor de recortar unidades, claro cuando votó al revés.

Con eso los tres pares se leen solos. El primero va a favor de recortar unidades, dos centésimas; el segundo se da vuelta; el tercero es prácticamente cero, y en los tres la línea gris cruza el cero. Si la dirección importara, el signo sería el mismo en los tres.

Abajo, qué cuesta ir sacando capacidad. Del lado de las unidades hay un escalón y después una meseta, sin ningún quiebre donde el total cae sobre la ocupación medida; del lado de los expertos ni siquiera baja de forma ordenada, y el peor caso de la tanda es el recorte más chico. Con eso cierro el encargo.

## L4 · ¿La atención de CLAM cae sobre los núcleos de la mitosis?

Lo que medimos no es un mapa de calor: es un número, y sale de un ranking.
Se ordenan los 4799 parches por atención y se mira dónde cayeron los 28 de mitosis.
Si la atención no supiera nada daría 0,5; observamos 0,89.

Esto empieza con una frase del patólogo: en mitosis los núcleos son finos y dispersos, y quizá esos parches no reciben atención suficiente.

Esa frase se puede medir, y por eso la traigo. No es una opinión sobre el modelo: es una afirmación sobre dónde cae la atención. Y la podemos contrastar porque tenemos las marcas del patólogo, o sea que sabemos en qué parches hay una mitosis. Sin ellas solo tendríamos un mapa de calor, y de un mapa de calor uno no puede decir si el rojo está donde corresponde. Las marcas convierten una impresión en un número.

Antes de correr nada dejamos escritas las dos respuestas posibles: que los parches marcados no rankearan mejor que el azar, y el problema estaría en cómo el modelo los combina; o que rankearan alto, y entonces lo que se pierde está antes. Quedó en pie la segunda.

Cómo se mide. Se ordenan los cuatro mil setecientos noventa y nueve parches por la atención que recibieron. Cada casilla de las dos cintas es un parche, y los oscuros son los veintiocho con una mitosis marcada. Si la atención no supiera nada de mitosis estarían repartidos por toda la fila, que es la cinta de arriba y da cero coma cinco; si se concentrara ahí se amontonarían a la izquierda, que es la de abajo.

El número sale de una cuenta simple. Comparo cada uno de esos veintiocho parches contra cada uno de los cuatro mil setecientos setenta y uno restantes y miro cuál recibió más atención: en el ochenta y nueve por ciento de las comparaciones ganó el parche con mitosis. Es un estadístico clásico para comparar dos grupos sin suponer nada sobre sus distribuciones; solo mira el orden, así que sirve entre grupos de tamaños muy distintos, y su referencia es cero coma cinco siempre.

## L5 · Atención y marcas del patólogo

La región anotada, con la atención del modelo y las marcas del patólogo.
A la izquierda pone el color el modelo; a la derecha, las marcas las puso el patólogo.
Al pie, de dónde salió la lámina y qué tiene marcado.

A la izquierda está la atención del modelo sobre el tejido: el rojo es mucha atención, el azul poca. A la derecha, las marcas del patólogo, cada color un tipo de tejido.

Al pie está de dónde sale todo esto. Es una lámina de nuestra cohorte privada, escaneada a veinte aumentos, de la que salen cuatro mil setecientos noventa y nueve parches de doscientos cincuenta y seis píxeles de lado. El patólogo dibujó sesenta y un polígonos en QuPath: veintiséis de mitosis, catorce de núcleos de alto grado, seis de necrosis, cinco de células inmunes, cinco de tumor, dos de tejido adiposo, uno de estroma y dos de fondo. Debajo de alguno de ellos caen ciento sesenta y tres parches, y de ésos, veintiocho contienen una mitosis.

En la última línea están las etiquetas de esta lámina en nuestros datos, las de reporte, que en los CSV se escriben como score dos y score tres: tasa mitótica alta, pleomorfismo nuclear intermedio, diferenciación tubular alta, grado general tres. La primera es coherente con veintiséis mitosis marcadas, y es la que le vamos a pedir al modelo dentro de dos láminas.

Sobre si las marcas coinciden con lo que mira el modelo, mirando de a dos uno intuye que caen en zonas calientes. Pero intuir no es medir, y por eso el resultado es el número de la lámina anterior y no esta imagen. Lo que agrega la imagen es que el número no vive de una casualidad de una esquina.

## L6 · El resultado, grupo por grupo

Una barra por clase de tejido marcada, con el mismo estadístico de recién.
Mitosis queda arriba de todo, y por encima incluso de tumor.
La escalera baja hasta la grasa, que el modelo evita.
La línea sobre cada barra dice cuánta precisión da el número de parches de ese grupo.

Cada barra es una de las clases marcadas, y su valor es el estadístico de recién calculado con los parches de esa clase: la probabilidad de que un parche de ese tejido reciba más atención que uno cualquiera del resto de la lámina. Cada clase se mide contra todo lo demás, nunca contra otra clase.

Mitosis da cero coma ochocientos noventa, muy lejos del azar y por encima de tumor, que son regiones grandes y bien delimitadas, mucho más fáciles de acertar que veintiocho parches sueltos. Pero lo que convence es la escalera completa. Abajo de todo está el tejido adiposo, en cero coma ciento cincuenta y cuatro: tan por debajo del azar significa que el modelo lo evita, no que lo ignore. Arriba, tumor y núcleos de alto grado alrededor de cero coma ochocientos veinticinco. Ese orden no lo diseñó nadie, salió de medir.

Ahora la línea sobre cada barra, porque sin ella siete barras del mismo grosor parecen siete números de la misma calidad. Hay dos incertidumbres. Una es de modelo: si repito la medición con otros checkpoints, con las marcas fijas, el valor de mitosis se mueve unas cuatro centésimas. La otra es la dibujada, y es la grande: cuánto se movería si el patólogo hubiera marcado otras mitosis en vez de éstas. Depende de cuántos parches tiene el grupo, y en mitosis vale unas ocho centésimas, el doble que la primera.

El caso que obliga a mirarla es el estroma: con doce parches su línea va de cero coma treinta y siete a cero coma setenta, así que esta lámina no distingue estroma evitado de estroma atendido. Mitosis aguanta, porque su línea no se acerca al azar. Los núcleos de alto grado tampoco los presento como resultado: su línea es la segunda más larga.

## L7 · Los 28 parches de mitosis

Arriba, de dónde salen 28 parches si el patólogo dibujó 26 marcas.
En blanco, los 28 parches que contienen una mitosis marcada.
Debajo, en colores, dónde puso la atención el modelo.
Los blancos caen sobre el rojo.

Despejo primero la cuenta de arriba, porque los dos números conviven en todo el trabajo y parecen contradecirse. El patólogo dibujó veintiséis marcas y yo vengo hablando de veintiocho parches: son unidades distintas. Diez marcas caen sobre el borde entre dos parches y ocupan los dos; y siete parches tienen más de una mitosis adentro.

La causa de fondo es de escala. Una marca de mitosis mide treinta y seis píxeles de lado y el parche mide doscientos cincuenta y seis: la mitosis ocupa entre el dos y el cuatro por ciento del área del parche. Con ese tamaño, que diez de veintiséis caigan sobre un borde deja de sorprender.

Y hay una implicación más seria. El modelo no ve el parche: ve un vector de quinientos doce números en el que el extractor lo resume entero. Si la mitosis ocupa dos de cada cien píxeles, su aporte a ese resumen es muy chico y el resto lo llena el tejido de alrededor. El parche puede estar bien elegido y la evidencia que justifica elegirlo puede haberse diluido en el camino.

Abajo, el mapa de atención con los veintiocho parches de mitosis en blanco encima. El color lo pone el modelo y los cuadrados los pone el patólogo, así que la pregunta es si los blancos caen sobre el rojo: no están en el borde ni repartidos, están sobre el corazón de la mancha.

Y este mismo modelo se equivoca al clasificar esta lámina.

## L8 · La atención acierta y la clasificación falla

Cuatro modelos de tasa mitótica, ninguno la tuvo en entrenamiento.
La última columna es cuánto mira cada uno las mitosis: todos miran bien.
La fila destacada es el que mejor mira, y es el que responde peor.

Primero, qué tarea es ésta. Tasa mitótica es uno de los tres componentes del grado histológico, y en nuestros datos tiene cuatro etiquetas, que en la tabla aparecen como score uno, dos y tres más no identificado: tasa baja, seiscientas treinta y seis láminas; intermedia, doscientas ochenta y siete; alta, doscientas cincuenta y cuatro; y no identificado, seiscientas noventa y tres, que son aquellas cuyo informe no consigna el dato. Esta lámina es de tasa alta.

En la tabla hay cuatro modelos entrenados sobre esa tarea, con distinta cantidad de datos, y ninguno vio esta lámina en entrenamiento. Tres de los cuatro responden tasa intermedia: se equivocan hacia abajo.

La fila destacada hace la lámina. Ese modelo mira mejor que los otros tres, con cero coma novecientos veintiséis en la última columna, y se equivoca con más convicción, con un setenta y uno por ciento de confianza en la respuesta equivocada.

Suena a paradoja y no lo es. El modelo trabaja en dos pasos: primero elige qué parches importan, después combina sus vectores en una única respuesta. La última columna mide el primer paso, y está bien resuelto; falla el segundo, y falla antes de combinar nada, porque la evidencia ya venía diluida en cada parche. No hay que enseñarle a mirar, hay que conseguir que lo que mira sobreviva a la compresión.

## L9 · SI-MIL: qué propone

La ambición del paper: que la explicación SEA la predicción.
Dos caminos que salen de la misma lámina: uno mide, el otro selecciona.
La rama profunda no llega a producción: se descarta entera.

Paso al paper encargado, que llega al mismo problema por otro camino: nosotros miramos un modelo ya entrenado para ver dónde puso la atención, y ellos proponen construirlo para que no haya que ir a mirarlo.

La idea es que la explicación sea la predicción, no un anexo. La red profunda deja de predecir y su único producto pasa a ser una selección de veinte parches, los más atendidos. La predicción se calcula aparte, con una combinación lineal de mediciones que un patólogo puede leer, y en producción la rama profunda se descarta entera.

Esas mediciones son doscientas cuarenta y seis y no salen de la nada. Antes pasa por el parche un segmentador de núcleos, HoVer-Net, que separa cada núcleo de sus vecinos y le pone una de cinco clases: epitelial neoplásico, conectivo, inflamatorio, necrótico y epitelial no neoplásico. Sobre ese mapa se calculan las mediciones. Doscientas cinco son morfométricas: diez propiedades por núcleo, como el área, la excentricidad o la solidez; cuatro estadísticos que resumen cada propiedad en el parche, la media, la desviación, la asimetría y la curtosis; y las cinco clases. Diez por cuatro por cinco, doscientas, más cinco conteos, uno por clase. Las cuarenta y una restantes describen cómo están distribuidos en el espacio: medidas de grafo, tratando a las células como nodos, y medidas de mezcla de tipos celulares.

Cada una tiene nombre legible: una es la asimetría de la solidez de los núcleos neoplásicos, otra la mezcla de células conectivas dentro de la región neoplásica. Por eso pueden decir que el reporte del modelo es la predicción misma.

En la figura, los dos caminos que bajan de la lámina describen los mismos parches de dos maneras, y la caja del medio es la bisagra: toma la atención del camino profundo y con ella elige los veinte parches sobre el otro camino.

## L10 · Resultados y costo de adopción

La tabla compara el método sobre distintos modelos de base, y uno es el nuestro.
Sobre el nuestro, la fila destacada, las dos métricas bajan.
Publican el dataset ya procesado, y la cohorte de mama está adentro.

Esta tabla nos interesa más que las otras porque no compara el método contra otros métodos, sino aplicado sobre distintos modelos de base, y uno de ellos es el nuestro.

Sobre el primero, el modelo de atención más simple, la exactitud sube un poco al agregarle la rama interpretable. Sobre el segundo, que es el nuestro y es la fila destacada, bajan las dos: la exactitud algo más de un punto y el área bajo la curva un punto y medio. Lo digo sin ánimo de desacreditar el trabajo: el titular de que no hay compromiso entre rendimiento e interpretabilidad se sostiene sobre el primer modelo, y la fila que nos correspondería es la que baja.

La comparación con lo nuestro es nítida sin ser una competencia. La interpretación de ellos aparece durante el entrenamiento, sobre mediciones que tienen nombre desde antes; la nuestra aparece después, sobre modelos ya congelados. Por eso el costo de equivocarse es distinto: allá empeora el modelo, acá queda mal la descripción.

Si quisiéramos probarlo acá, el costo más duro es de escala física: el segmentador de núcleos está entrenado a cuarenta aumentos y solo a cuarenta, tanto que ellos mismos filtraron sus datasets para quedarse con láminas de esa magnificación, y nuestras cohortes están a escalas distintas. El costo de cómputo se desarma solo: publican el dataset ya procesado y la cohorte pública de mama está adentro.

Y dejo una pregunta de fondo. Cuando le mostraron los reportes a un patólogo, algo más de un cuarto de las mediciones que el modelo declara importantes le resultaron no relevantes. Me parece muy honesto que lo publiquen, y la pregunta es si ese número es aceptable para nuestro estándar clínico.

## L11 · HoVer-NeXt y la clase de mitosis

Un segmentador de núcleos con una clase de mitosis entre las suyas.
La figura del paper: el teselado, la red, y el cosido de las teselas.
Encaja sin reescalar: trabaja a media micra por píxel, como nuestras láminas privadas.

Vuelvo a nuestra línea. La idea viene de la reunión anterior: si el modelo mira donde hay mitosis y aun así falla, quizá lo que falta no es atención sino detalle, y conviene un instrumento a nivel de núcleo.

La figura es del paper y muestra las tres piezas. Arriba, el flujo completo: la lámina se parte en teselas, cada tesela pasa por la red, y un segundo componente cose las salidas en una sola imagen del tamaño de la lámina. Abajo a la izquierda, la red, que es un codificador y dos decodificadores que lo comparten. Y abajo a la derecha, el cosido: las teselas se procesan con solapamiento, así que hay que resolver los núcleos del borde para no contarlos dos veces ni partirlos.

Las dimensiones. La entrada es una tesela de tres canales, rojo, verde y azul, muestreada a media micra por píxel. El codificador es una ConvNeXt versión dos, tamaño tiny, preentrenada en imágenes naturales. El primer decodificador es el de instancia y saca cinco canales: dos son mapas de regresión de distancia, que permiten separar un núcleo pegado a otro, y los otros tres son una clasificación por píxel en fondo, interior del núcleo y borde del núcleo. El segundo es el de clase y saca ocho canales: fondo más las siete clases de núcleo con las que se entrenó, entre ellas mitosis. En total trece canales por píxel, y el mapa final sale de combinar las dos salidas: el de instancia dice dónde empieza y termina cada núcleo, y el de clase dice qué es.

Corrijo algo que quedó dando vueltas de la última vez. Las doscientas cuarenta y seis mediciones no son de este modelo: son del paper anterior, que usa HoVer-Net, sin la equis, como front-end de segmentación. Éste no produce ningún vector de características por parche, produce el mapa de núcleos que describí.

Por qué elegimos éste. La escala: está pensado para media micra por píxel y nuestras láminas privadas están casi exactamente ahí, así que no hay que reescalar nada, que es donde aparecen los problemas silenciosos. Y entre sus clases tiene una de mitosis.

## L12 · Resultados: recortar y detectar

La atención de CLAM recorta la región, y el detector de núcleos trabaja adentro.
Recupera 13 de las 26 marcas del patólogo: la mitad.
Desde el 7,6 % de la región el cuello deja de ser el recorte y pasa a ser el detector.
Las 13 que faltan no fallan por poco: no hay ninguna detección de mitosis cerca.

Esto es lo que quedó pedido en la reunión anterior: integrar el modelo de atención al camino de detección.

La cadena tiene tres pasos, y cada uno lo hace una herramienta distinta. Primero nuestro modelo mira la lámina entera y reparte atención entre sus parches. Segundo, el recorte: nos quedamos con el doce por ciento más atendido y apagamos el resto. Ese porcentaje ordena toda la lámina: la región anotada tiene dos mil cuatrocientos noventa y seis parches, así que el doce por ciento son trescientos parches encendidos, y en superficie, cuatro coma veinticinco milímetros cuadrados. Tercero, el detector de núcleos trabaja adentro de ese recorte, y es un modelo ajeno que no sabe nada del nuestro ni de nuestra tarea.

Lo que produce es un inventario de núcleos: en esta lámina segmentó más de doscientas treinta y ocho mil células y a ciento setenta y siete les puso mitosis. Cada marca amarilla es un núcleo, uno solo; las blancas son las veintiséis mitosis que dibujó el patólogo. Dos fuentes independientes sobre la misma imagen, y toda la lámina consiste en compararlas.

Los tres paneles de la izquierda son la misma región en tres estados: la atención, el recorte, y encima lo que encontró el detector. Las detecciones se agrupan sobre el recorte, o sea que la atención y el detector miran el mismo tejido sin haberse consultado. Abajo, cuatro coincidencias a resolución nativa: no están de acuerdo sobre una zona, están de acuerdo sobre una célula.

El número es trece de veintiséis, la mitad, con emparejamiento uno a uno: si uno le pregunta a cada marca cuál es la detección más cercana el número sube, pero son siempre las mismas trece contadas varias veces, y una detección no puede acreditar dos marcas.

Las otras trece no fallan por poco: movimos la tolerancia en un rango de diez veces y el número se queda clavado en trece, y la detección de mitosis más cercana a una marca fallada está a ciento quince micras de mediana, unos seis núcleos. No apunta al lado, no hay nada ahí. Averiguamos por qué, y es la lámina dieciséis.

La tabla junta los dos límites de la prueba, y es lo que cambió la conversación. Cada fila es un tamaño de recorte; una columna dice cuántas marcas entran, y la de al lado cuántas de ésas además se detectan. Veníamos discutiendo cuán grande convenía hacer el recorte, y a partir del siete coma seis por ciento de la región eso deja de ser el problema: por generoso que uno lo haga, el techo se queda en trece. El factor que manda pasó a ser la detección.

Una cosa que este número no dice. La mitad no es la exhaustividad del detector en mitosis: el denominador son las marcas del patólogo, no las mitosis que hay en la lámina. Tampoco calculamos precisión, y es deliberado: el patólogo marca solo donde la evidencia es clara, así que una detección sin marca no es un error.

## L13 · El detector sobre la lámina completa

El brazo de control: el detector solo, sin nada del modelo de atención encima.
La lámina entera son 68 mm² y 177 detecciones.
Recupera las mismas 13 de 26 que con el recorte puesto.
De la región sin marcas no se afirma nada.

Falta el brazo de control, y va después a propósito: si digo trece de veintiséis con el recorte puesto, la pregunta inmediata es comparado con qué.

No hubo que correr nada nuevo, porque la corrida fue así desde el principio: la lámina completa, y el recorte aplicado después sobre la salida. Si hubiéramos recortado antes para ahorrar cómputo, este brazo no existiría.

Se ven las ciento setenta y siete detecciones sobre la lámina entera. De las noventa y cinco de la izquierda no afirmo nada: ahí no hay marcas del patólogo, así que no son ni aciertos ni errores.

La tabla es lo que quiero discutir. Revisando la lámina entera, sesenta y ocho milímetros cuadrados, se recuperan trece de las veintiséis marcas. Revisando solo la región anotada, la mitad de la superficie, se recuperan las mismas trece; no es una sorpresa sino una comprobación, porque las veintiséis marcas caen todas ahí. Y revisando el doce por ciento más atendido, cuatro coma tres milímetros cuadrados, se recuperan once.

Entre el primer brazo y el último la superficie a revisar baja dieciséis veces y las marcas bajan de trece a once. Eso separa dos preguntas que conviene no mezclar. Si la pregunta es cuánta superficie hay que ponerle delante a un patólogo, el recorte responde bien; si la pregunta es cuántas mitosis se encuentran, no ayuda, porque el techo lo pone el detector.

Sobre el costo: la lámina entera tardó dieciocho minutos, así que recortar para ahorrar cómputo hoy no hace falta. Recortar para achicar lo que hay que revisar sí tiene sentido, y los dos motivos no piden el mismo tamaño de recorte.

Las cuatro láminas que siguen son las pruebas que le hicimos a esta cadena.

## L14 · CLAM, Mammoth y el detector a igual carga

Cuántos objetos hay que mirar para llegar al mismo número de marcas.
A recorte fijo la comparación premia a la máscara más grande por ser más grande.
Los dos caminos piden una carga parecida hasta 13 marcas, y de ahí el detector se topa.

Faltaba una comparación, y es la primera: el detector, ¿agrega algo sobre la atención sola?

Antes, cómo está armada la tabla, porque la forma de comparar importa más que los números. A recorte fijo, dejando entrar la misma cantidad de parches en cada brazo, gana el que tenga la máscara más grande, y gana por tamaño y no por calidad. Así que damos vuelta la pregunta: fijamos el resultado y medimos el costo, así que cada fila es un nivel de marcas recuperadas y cada celda dice cuántos objetos hay que mirar para llegar ahí.

Los brazos son cuatro de atención y uno de detección. Los dos primeros son nuestro modelo y la variante con expertos, que no se suman: son alternativos, porque la variante es el mismo modelo con la primera capa cambiada. Los dos del medio son la intersección y la unión de sus máscaras. Y el último es el detector solo, sin recorte. Su columna lleva dos marcadores distintos: no aplica cuando se le pide menos de trece, porque no ordena sus detecciones y no se le puede pedir una carga menor; e imposible por encima de trece, que es su techo.

Tres cosas que solo aparecen así. La unión nunca es el mejor brazo: a recorte fijo parecía el mejor de todos, y acá queda al nivel del peor de los dos que la componen, porque su ventaja era el tamaño. La intersección es la más eficiente donde la carga es chica: donde los dos modelos coinciden, aciertan. Y la tercera: hasta trece marcas los dos caminos piden una carga parecida, ochenta y dos núcleos contra ochenta y cuatro parches, pero los objetos son de tamaño muy distinto, porque un parche mide ciento diecinueve micras de lado y un núcleo es un punto ya localizado. Por encima de trece el detector deja de ser una opción a cualquier carga, mientras que la atención sola llega a las veintiséis.

Esta lámina es sobre dónde pone la atención cada modelo, no sobre cuál clasifica mejor.

## L15 · El checkpoint de carcinoma invasivo

El encargo era repetir la cadena con el otro checkpoint.
Por AUC los dos parecen equivalentes: los intervalos se solapan de sobra.
Por recorte no: el checkpoint del gate es claramente peor.

El otro encargo era repetir la cadena con el checkpoint de carcinoma invasivo, en vez del de carcinoma in situ. No hubo que volver a correr el detector: la lámina se corrió entera y el recorte se aplica después. Las dos lecturas no coinciden, y por eso la lámina está partida en dos.

A la izquierda, por área bajo la curva parecen equivalentes: cero coma ochocientos sesenta y cinco el gate contra cero coma novecientos diecinueve el otro, con intervalos que se solapan de sobra. Con este número solo uno concluiría que da igual cuál usar.

A la derecha, la misma pregunta hecha por recorte, que es como se usa en la práctica. En el cuatro por ciento de la región el gate mete una marca de veintiséis y el otro catorce; en el siete coma seis por ciento, ocho contra dieciocho; en el doce, once contra veintidós. Para poner las mismas marcas delante del patólogo hay que darle bastante más superficie.

Por qué discrepan está en la línea del medio. El área bajo la curva resume todos los umbrales a la vez; el recorte es un umbral solo, y de los extremos. El checkpoint del gate deja los parches con mitosis en el percentil ochenta y seis y el otro en el noventa y cinco: esa diferencia casi no mueve el área bajo la curva y decide entera la lista de los trescientos más atendidos.

Dos salvedades del pie. El brazo del gate es la variante con expertos, no el modelo plano: el plano de esa tarea no existe en disco y lo entrena un trabajo que sigue en la cola, así que todavía no separamos si esto es propiedad de la tarea o del brazo. La otra es el chequeo de sanidad, y pasa: en la región entera los dos brazos convergen a trece de veintiséis.

## L16 · Las 13 que se escapan sí estaban segmentadas

Las 13 marcas que el detector no acredita tienen un núcleo segmentado encima. Las 13.
No se escaparon por falta de segmentación: se escaparon por la clase.
Las acreditadas son el control, y las dos mitades salen indistinguibles salvo en la etiqueta.

Vuelvo a las trece que se escapan. Habíamos cerrado en que no hay ninguna detección de mitosis cerca, y nos detuvimos ahí sin preguntar ausencia de qué.

El núcleo estaba. Las trece marcas falladas tienen una instancia segmentada encima, las trece, sin excepción. Y no cerca: encima, a dos coma un micras de mediana, sobre marcas cuyo lado mediano es dieciséis coma siete micras. No falló la segmentación, falló la etiqueta que le puso la cabeza de clasificación.

La columna de la izquierda son las trece acreditadas, pasadas por el mismo procedimiento: si no las recuperara a ellas, el problema sería el procedimiento y no el grupo de estudio. Las dos mitades salen indistinguibles en todo, y la única variable que las separa es la clase.

Adónde fueron a parar dice algo. Doce de las trece recibieron la clase célula epitelial, que es la clase padre: en un carcinoma de mama una figura mitótica es una célula epitelial, así que el modelo no la confunde con estroma ni con un linfocito, sino que pierde la distinción fina.

Esto cambia el costo del arreglo. Lo caro, barrer la lámina y segmentar doscientas treinta y ocho mil células, ya está pagado y guardado: si lo que falla es la etiqueta, alcanza con una segunda etapa de clasificación sobre los objetos que ya existen.

Y la explicación de fondo es de dominio: la clase de mitosis de este detector se entrenó y se validó solo en colon, mientras que segmentar y tipificar núcleos en mama sí tiene número propio y bueno. Lo que sabe hacer fuera de su tejido lo hace bien; lo que nunca se validó fuera de colon es lo que falla.

## L17 · En qué se fija el detector

Las 164 detecciones que no acreditan ninguna marca, y las 13 que se escaparon.
145 de las 164 son el mismo tipo de recorte: el 88 %.
No son falsos positivos, y no se calcula precisión.

Cierro con las imágenes, que es lo que pediste ver. La lámina de contacto grande son las ciento sesenta y cuatro detecciones que no acreditaron ninguna marca; ésas más las trece acreditadas son las ciento setenta y siete. Cada recorte está a resolución nativa, en una ventana de sesenta micras de lado.

Se parecen entre sí bastante más de lo que esperábamos. Agrupándolas por color y textura, ciento cuarenta y cinco de las ciento sesenta y cuatro, el ochenta y ocho por ciento, caen en un solo grupo: epitelio tumoral denso, recortes oscuros y saturados casi sin fondo, con un núcleo hipercromático y condensado en el centro. Es la forma que el detector busca, y la misma que tienen las trece que sí acertó. Se despega un grupo chico: quince recortes claros, con dos tercios de fondo, que son tejido laxo o borde de lámina.

A la derecha están las trece falladas, centradas, cada una sin ninguna detección cerca. En varias se ve una figura mitótica de manual, y ése es el bloque que más informa.

Y lo que no se puede decir de esta lámina, que acá importa más que en ninguna otra: las ciento sesenta y cuatro no son falsos positivos. El patólogo marca solo donde la evidencia es clara, no pretende marcarlo todo, así que una detección sin marca puede ser perfectamente una mitosis real sin marcar. Por eso no calculamos precisión y ningún panel las pinta como error. Y el parecido que describí es de píxeles, no semántico.

Lo que me gustaría discutir es hacia dónde movemos el número del detector, y hay dos cosas baratas antes de tocar nada. Una es mirar si en esos trece la clase mitosis quedó segunda por poco, que se responde con lo que ya está guardado y decide entre recalibrar un umbral o reentrenar la cabeza. La otra: si el problema es que su clase de mitosis nunca vio mama, existe un conjunto público de mitosis en mama, con doscientos casos y licencia abierta. Y viene con una advertencia que nos toca: los detectores de mitosis se caen al cambiar de escáner.
