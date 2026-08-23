# Borrador del guion del presentador · deck del 24-ago

> Escrito el **22-ago-2026** (sesión 23), **SIN aplicar al generador**. La sesión se cerró
> antes de la pasada de recorte, así que este archivo es el insumo de la próxima, no el
> entregable.

## Estado, medido

| | palabras | minutos a 130 pal/min |
|---|---|---|
| guion vigente en `CLAM_Sprint8.pptx` (12 láminas con notas + 5 con marcador) | 7220 | 56 |
| **este borrador** (las 17 escritas) | **7160** | **55** |
| objetivo del plan §13 | ~4500 | ~35 |

O sea: **la cobertura está completa y el recorte NO está hecho**. Las cinco láminas que
tenían `PLACEHOLDER_…` ya tienen guion; las doce viejas están reescritas más cortas que su
versión previa, pero el total sigue un 59 % por encima del objetivo porque las cinco nuevas
suman ~2100 palabras que antes no existían.

## Presupuesto por lámina, para la pasada de recorte

Objetivo por lámina y cuánto sobra hoy. La suma de la columna «objetivo» da 4460.

| # | lámina | hoy | objetivo | recortar |
|---|---|---|---|---|
| 1 | Portada | 185 | 150 | −35 |
| 2 | Objetivos del sprint | 199 | 180 | −19 |
| 3 | ¿Recortar expertos o slots? | 502 | 330 | **−172** |
| 4 | ¿La atención cae sobre los núcleos? | 478 | 330 | **−148** |
| 5 | Atención y marcas del patólogo | 339 | 280 | −59 |
| 6 | El resultado, grupo por grupo | 475 | 300 | **−175** |
| 7 | Los 28 parches de mitosis | 392 | 240 | **−152** |
| 8 | La atención acierta y la clasificación falla | 348 | 200 | **−148** |
| 9 | SI-MIL: qué propone | 417 | 260 | **−157** |
| 10 | Resultados y costo de adopción | 451 | 250 | **−201** |
| 11 | HoVer-NeXt y la clase de mitosis | 497 | 280 | **−217** |
| 12 | Resultados: recortar y detectar | 700 | 380 | **−320** |
| 13 | El detector sobre la lámina completa | 418 | 280 | **−138** |
| 14 | CLAM, Mammoth y el detector a igual carga | 435 | 280 | **−155** |
| 15 | El checkpoint de carcinoma invasivo | 404 | 240 | **−164** |
| 16 | Las 13 que se escapan sí estaban segmentadas | 430 | 230 | **−200** |
| 17 | En qué se fija el detector | 490 | 250 | **−240** |

## Lo que el recorte NO puede comer

Son los pedidos explícitos de `correcciones.txt` y del handoff §7, y el borrador de abajo ya
los cubre. Al recortar, verificar uno por uno que sigan estando:

- **L3** cómo se lee el diagrama divergente: la barra, la línea gris, el cuadro por partición,
  el relleno como dirección, y la escala de ±0,1 de AUC. Ernesto pidió que **no** esté escrito
  en la lámina pero **sí** dicho.
- **L4** que tener las marcas del patólogo es lo que hace medible la pregunta. Y el estadístico
  contado sin nombrar «Mann-Whitney» como jerga suelta (dijo textual que no sabe qué es).
- **L5** los conteos: 61 polígonos con su reparto por clase, 4799 parches, 163 marcados, 28 con
  mitosis; y si coinciden con los mapas. **Sin mencionar las dos regiones de escaneo.**
- **L6** las dos incertidumbres, que salieron del cuerpo de la lámina.
- **L7** qué implica el 2-4 %.
- **L8** las 4 clases de tasa mitótica.
- **L9** HoVer-Net como front-end y de dónde salen las 246 mediciones.
- **L11** cada paso del diagrama y las dimensiones reales de HoVer-NeXt.
- **L15** que el brazo del gate es Mammoth, no CLAM.
- **L17** que las 164 no son falsos positivos.

## Arcos ya corregidos respecto del guion vigente — no reintroducirlos

1. **La portada** ya no dice «al final, después de los objetivos que propongo»: los objetivos
   pasaron a la lámina 2 y lo que cierra es la Fase A.
2. **La lámina 12** ya no dice «falta algo que no medimos, es lo primero que yo haría» sobre si
   los núcleos fallados estaban segmentados: eso lo contesta la lámina 16, y ahora remite a
   ella.
3. **La lámina 13** ya no cierra la presentación («con eso cierro»): entrega a las cuatro de la
   Fase A. El cierre es la 17.
4. **La lámina 13** ya no dice «el recorte no compra marcas, compra área», que Ernesto rechazó
   por poco profesional; el cuerpo de la lámina ya lo dice bien y el guion lo sigue.

## Formato al aplicarlo al generador

Cada bloque de abajo va tal cual a su `notes(s, "...")`, con el punteo guía inicial (los
renglones sueltos de arriba) separado del cuerpo por una línea en blanco, y los párrafos
separados por `\n\n`. Convención vigente: prosa hablada corrida, sin etiquetas de fase, sin
números de job ni nombres propios, cero guiones largos, decimales pronunciados según los que
la lámina muestre.

**Falta la pasada de `@humanizer-es`**, que es el procedimiento de la convención y todavía no
se corrió sobre este texto.

---

## L1 · Portada

Traigo cuatro cosas, y las puse en ese orden a propósito.

Empiezo por un encargo que había quedado del sprint pasado y que ya cerró: si al modelo con expertos le sobra capacidad por dentro, y de qué lado conviene recortarla. Da un resultado negativo y lo dejo cerrado ahí mismo.

Después va lo que más me importa dejar claro, que es una medición nuestra: fuimos a ver si el modelo mira donde el patólogo marcó las mitosis. Tiene un resultado, y ese resultado cambió hacia dónde apunta el trabajo que sigue. Me voy a detener en cómo se mide, porque el número es lo que hay que poder defender.

Sigue la revisión de uno de los papers encargados, que propone un modelo que se explica solo. Es una lectura terminada, así que la cuento comprimida.

Y dejo para el final lo que más quiero discutir: un segundo modelo, que trabaja a nivel de núcleo, corriendo sobre el mapa de atención del nuestro. Es el encadenamiento que quedó pedido en la reunión anterior, y ya tiene mapas, tiene número y tiene cuatro láminas de resultados.

## L2 · Objetivos del sprint

Los seis objetivos del sprint, y en qué quedó cada uno.
Los cuatro primeros estaban propuestos desde el arranque y están cerrados.
Los dos últimos aparecieron durante el sprint y siguen en curso.

Los dos primeros son el encargo del modelo con expertos: escalar a la tarea completa la medición de capacidad, que veníamos arrastrando de siete láminas, y decidir de qué lado conviene recortar. Los dos están cerrados y el primero de los dos es la lámina que sigue.

El tercero es la medición de atención contra las marcas del patólogo, y el cuarto es elegir y justificar hacia dónde sigue la rama de mitosis. También cerrados, y ocupan el grueso de lo que traigo.

Los dos últimos no estaban en el plan de marzo: aparecieron durante el sprint, justamente porque el tercero salió como salió. Investigar e implementar un modelo de detección de mitosis que trabaje por núcleo, y encadenarlo con la atención para cruzar sus detecciones contra las marcas. Están marcados en curso y no por formalidad: el modelo ya corrió y ya hay número, pero está medido sobre una sola lámina y el barrido de las doce anotadas todavía está en la cola de cómputo.

## L3 · ¿Recortar expertos o slots?

Un encargo que quedó del sprint pasado y que este sprint cerró.
El modelo tiene 30 expertos y 10 unidades por experto: 300 en total.
A igual capacidad total, ¿conviene recortar por un lado o por el otro?
Arriba, la diferencia pareada; abajo, qué cuesta ir sacando capacidad.

Empiezo por acá porque es lo más corto. El sprint pasado medimos cómo se reparte el peso entre esas trescientas unidades, y quedó el reparo de que estaba medido sobre siete láminas. Lo escalamos a las mil ciento setenta y seis láminas de prueba de las tres tareas, y el número aguanta: se ocupan alrededor de ciento sesenta de las trescientas unidades, y los treinta expertos se usan los treinta, sin una sola excepción. De ahí salía la lectura de que, si sobraba capacidad, sobraba del lado de las unidades.

La figura de arriba pone eso a prueba de frente. A igual capacidad total comparamos recortar por un lado contra recortar por el otro, sobre las mismas particiones. La tarea es presencia de carcinoma ductal in situ.

Cómo se lee, que es lo que quiero que quede claro. La magnitud que se compara está escrita arriba: la diferencia de área bajo la curva entre los dos recortes, calculada partición por partición. La línea vertical del medio es el cero, y la escala de la figura llega a una décima de área bajo la curva hacia cada lado. La barra oscura es el promedio de esa diferencia, y sale del cero hacia el lado que gana: a la derecha si conviene recortar unidades, a la izquierda si conviene recortar expertos. La línea gris que la atraviesa, con los dos topes, es cuánto se mueve esa diferencia entre las cinco particiones. Y los cinco cuadraditos de la derecha son las particiones, una cada uno: relleno oscuro cuando esa partición votó a favor de recortar unidades, claro cuando votó al revés.

Con eso, léanla conmigo. En el primer par la barra va a favor de recortar unidades, dos centésimas, con tres cuadros de cinco rellenos. En el segundo se da vuelta. En el tercero es prácticamente cero. Y en los tres la línea gris cruza el cero de lado a lado. Si la dirección del recorte importara, el signo sería el mismo en los tres.

Abajo está la misma tanda mirada de otra manera: qué pasa a medida que se saca capacidad, cada lado por separado. La barra clara del extremo izquierdo es el modelo completo y es la misma en los dos gráficos. Del lado de las unidades hay un escalón y después una meseta, y en el punto donde el total cae justo sobre lo que habíamos medido de ocupación no se marca ningún quiebre, que era exactamente la predicción. Del lado de los expertos ni siquiera baja de forma ordenada: el peor caso de toda la tanda es el recorte más chico. Una curva de capacidad no se comporta así.

Con eso cierro el encargo, y paso a lo que sí movió el plan.

## L4 · ¿La atención de CLAM cae sobre los núcleos de la mitosis?

Lo que medimos no es un mapa de calor: es un número, y sale de un ranking.
Se ordenan los 4799 parches por atención y se mira dónde cayeron los 28 de mitosis.
Si la atención no supiera nada daría 0,5; observamos 0,89.

Esto empieza con una frase del patólogo. Revisando por qué los modelos fallan en tasa mitótica, dijo que en mitosis los núcleos son finos y dispersos, y que quizá esos parches no reciben atención suficiente.

Esa frase se puede medir, y quiero subrayar por qué. No es una opinión sobre el modelo: es una afirmación sobre dónde cae la atención. Y podemos contrastarla porque tenemos las marcas del patólogo sobre la lámina, o sea que sabemos exactamente en qué parches hay una mitosis. Sin esas marcas solo tendríamos un mapa de calor, y de un mapa de calor uno no puede decir si el rojo está donde corresponde o si está en todas partes. Las marcas son las que convierten una impresión en un número.

Antes de correr nada dejamos escritas las respuestas posibles. La primera, la del patólogo: que los parches marcados no rankearan mejor que el azar, y entonces el problema estaría en cómo el modelo combina los parches. La segunda: que rankearan alto, y entonces el modelo sí mira donde hay que mirar y lo que se pierde está antes. Adelanto que quedó en pie la segunda.

Ahora, cómo se mide. Se toman los cuatro mil setecientos noventa y nueve parches de la lámina y se ordenan por la atención que recibieron, de más a menos. Queda una fila larga, y cada casilla de las dos cintas es un parche; los oscuros son los veintiocho que contienen una mitosis marcada. Si la atención no supiera nada de mitosis, los oscuros estarían repartidos por toda la fila, tantos al principio como al final: ésa es la cinta de arriba, y su número es cero coma cinco. Si la atención se concentrara justo ahí, se amontonarían a la izquierda: ésa es la de abajo, y es la que observamos.

El número sale de una cuenta simple. Tomo cada uno de los veintiocho parches con mitosis y lo comparo, de a uno, contra cada uno de los cuatro mil setecientos setenta y uno restantes. En cada comparación miro cuál de los dos recibió más atención. En el ochenta y nueve por ciento de esas comparaciones ganó el parche con mitosis. Eso es todo lo que dice el cero coma ochenta y nueve. Es un estadístico clásico para comparar dos grupos sin suponer nada sobre la forma de sus distribuciones, y tiene dos propiedades que uso después: solo mira el orden, no la escala de la atención, así que se puede comparar entre grupos de tamaños muy distintos y entre modelos que reparten la atención de distinta manera; y su referencia es cero coma cinco siempre.

## L5 · Atención y marcas del patólogo

La región anotada, con la atención del modelo y las marcas del patólogo.
A la izquierda pone el color el modelo; a la derecha, las marcas las puso el patólogo.
Al pie, de dónde salió la lámina y qué tiene marcado.

Los mapas son lo que uno recuerda de un trabajo así, y los muestro después del número a propósito.

A la izquierda está la atención del modelo sobre el tejido: el rojo es mucha atención, el azul poca. A la derecha, las marcas del patólogo, cada color un tipo de tejido.

Al pie está de dónde sale todo esto. Es una lámina de nuestra cohorte privada, escaneada a veinte aumentos, de la que salen cuatro mil setecientos noventa y nueve parches de doscientos cincuenta y seis píxeles de lado. El patólogo dibujó sesenta y un polígonos en QuPath, y su reparto por clase es el que está escrito: veintiséis de mitosis, catorce de núcleos de alto grado, seis de necrosis, cinco de células inmunes, cinco de tumor, dos de tejido adiposo, uno de estroma y dos de fondo. Debajo de alguno de esos sesenta y un polígonos caen ciento sesenta y tres parches, y de ésos, veintiocho contienen una mitosis.

Y en la última línea están las etiquetas de esta lámina en nuestros datos, que son las de siempre, las de reporte: tasa mitótica alta, pleomorfismo nuclear intermedio, diferenciación tubular alta, grado general tres. La de tasa mitótica alta es coherente con veintiséis mitosis marcadas, y es la etiqueta que le vamos a pedir al modelo dentro de dos láminas.

Sobre si las marcas coinciden con lo que mira el modelo, mirando de a dos uno ya intuye que caen en zonas calientes. Pero intuir no es medir, y por eso el resultado de este trabajo es el número de la lámina anterior y no esta imagen. Lo que la imagen agrega es que el número no vive de una casualidad de una esquina: las marcas y el rojo se solapan a lo largo de toda la región.

## L6 · El resultado, grupo por grupo

Una barra por clase de tejido marcada, con el mismo estadístico de recién.
Mitosis queda arriba de todo, y por encima incluso de tumor.
La escalera baja hasta la grasa, que el modelo evita.
La línea sobre cada barra dice cuánta precisión da el número de parches de ese grupo.

El resultado hay que leerlo entero, y no quedarse con el primer renglón.

Cada barra es una de las clases que el patólogo marcó, y su valor es el estadístico que acabo de contar, calculado con los parches de esa clase: la probabilidad de que un parche de ese tejido reciba más atención que un parche cualquiera del resto de la lámina. Importante, y está escrito al pie: cada clase se mide contra todo lo demás, nunca contra otra clase. La línea punteada del medio es el azar.

Mitosis da cero coma ochocientos noventa, muy lejos de la línea. Y por encima de tumor, que es más de lo que esperábamos, porque tumor son regiones grandes y bien delimitadas, mucho más fáciles de acertar que veintiocho parches sueltos.

Lo que convence no es ese número solo, es la escalera completa, porque muestra que la atención tiene estructura y que la estructura tiene sentido clínico. Abajo de todo está el tejido adiposo, en cero coma ciento cincuenta y cuatro. Estar tan por debajo del azar no significa que el modelo lo ignore: significa que lo evita, que un parche de grasa recibe sistemáticamente menos atención que uno tomado al azar. Después los linfocitos, también por debajo. Y arriba, tumor y núcleos de alto grado alrededor de cero coma ochocientos veinticinco. Ese orden no lo diseñó nadie: salió de medir.

Ahora la línea sobre cada barra, porque sin ella la lámina se sobre-lee. Siete barras del mismo grosor invitan a pensar que son siete números de la misma calidad, y no lo son. Hay dos incertidumbres distintas acá. La primera es de modelo: si repito la medición con otros checkpoints, con las marcas fijas, el valor de mitosis se mueve unas cuatro centésimas. La segunda es la que está dibujada, y es la grande: cuánto se movería el número si el patólogo hubiera marcado otras mitosis en vez de éstas. Depende directamente de cuántos parches tiene el grupo, y en mitosis vale unas ocho centésimas, el doble que la otra.

El caso que obliga a mirarla es el estroma. Con doce parches marcados su línea va de cero coma treinta y siete a cero coma setenta, así que esta lámina no puede distinguir estroma evitado de estroma atendido: ahí no hay dato. Mitosis, en cambio, aguanta, porque su línea no se acerca al azar. Y los núcleos de alto grado, el segundo renglón, tampoco los presento como resultado: tienen la segunda línea más larga, y al repetir la medición con los otros checkpoints solo uno los sostiene.

## L7 · Los 28 parches de mitosis

Arriba, de dónde salen 28 parches si el patólogo dibujó 26 marcas.
En blanco, los 28 parches que contienen una mitosis marcada.
Debajo, en colores, dónde puso la atención el modelo.
Los blancos caen sobre el rojo.

Despejo primero la cuenta de arriba, porque los dos números conviven en todo el trabajo y parecen contradecirse. El patólogo dibujó veintiséis marcas y yo vengo hablando de veintiocho parches. Son unidades distintas, y lo que las separa son dos efectos que casi se cancelan: diez de las veintiséis marcas caen sobre el borde entre dos parches y ocupan los dos, lo que suma diez; y siete parches tienen más de una mitosis adentro, lo que resta ocho. Que el neto dé más dos es casualidad de esta lámina, no una regla.

La causa de fondo es de escala, y es lo que quiero dejar dicho antes de pasar. Una marca de mitosis mide treinta y seis píxeles de lado y el parche mide doscientos cincuenta y seis: la mitosis ocupa entre el dos y el cuatro por ciento del área del parche. Con ese tamaño, que diez de veintiséis caigan sobre un borde deja de sorprender.

Y hay una implicación más seria, que es el puente a la lámina que sigue. El modelo no ve el parche: ve un vector de quinientos doce números en el que el extractor resume el parche entero. Si la mitosis ocupa dos de cada cien píxeles, su aporte a ese resumen es una fracción muy chica, y el resto del vector lo llena el tejido de alrededor. O sea que el parche puede estar perfectamente elegido y la evidencia que justifica elegirlo puede haberse diluido en el camino.

Ahora sí, la escalera anterior puesta donde se ve de un vistazo. Hay dos capas: el fondo es el mapa de atención, rojo donde el modelo puso más y azul donde puso menos; encima, en blanco sólido, los veintiocho parches con mitosis. El color lo pone el modelo y los cuadrados blancos los pone el patólogo, así que la pregunta es simplemente si los blancos caen sobre el rojo. No están en el borde del tejido, ni sobre el azul, ni repartidos: están sobre el corazón de la mancha. A la derecha, el detalle del recuadro.

Y ahora la parte incómoda: este mismo modelo se equivoca al clasificar esta lámina.

## L8 · La atención acierta y la clasificación falla

Cuatro modelos de tasa mitótica, ninguno la tuvo en entrenamiento.
La última columna es cuánto mira cada uno las mitosis: todos miran bien.
La fila destacada es el que mejor mira, y es el que responde peor.

Primero, qué tarea es ésta, porque tiene cuatro clases y conviene tenerlas. Tasa mitótica es uno de los tres componentes del grado histológico, y en nuestros datos tiene cuatro etiquetas: tasa baja, seiscientas treinta y seis láminas; intermedia, doscientas ochenta y siete; alta, doscientas cincuenta y cuatro; y no identificado, seiscientas noventa y tres, que son aquellas cuyo informe no consigna el dato. Esta lámina es de tasa alta, coherente con las veintiséis mitosis marcadas.

En la tabla hay cuatro modelos entrenados sobre esa tarea, con distinta cantidad de datos, y ninguno vio esta lámina en entrenamiento. Tres de los cuatro responden tasa intermedia: se equivocan, y se equivocan hacia abajo.

La fila destacada es la que hace la lámina. Ese modelo es el que mejor mira de los cuatro, con cero coma novecientos veintiséis en la última columna, y es también el que se equivoca con más convicción, con un setenta y uno por ciento de confianza en la respuesta equivocada. Mirar mejor no lo ayudó a responder mejor.

Quiero ser preciso con lo que eso significa, porque dicho rápido suena a paradoja y no lo es. Este modelo trabaja en dos pasos: primero elige qué parches importan, y después combina los vectores de esos parches en una única respuesta para la lámina. La última columna mide el primer paso, y el primer paso está bien resuelto: los parches que elige son los que tienen las mitosis. Lo que falla es el segundo, y por lo que vimos en la lámina anterior, falla antes de combinar nada: la evidencia de la mitosis ya venía diluida en el vector de cada parche. No hay que enseñarle a mirar. Hay que conseguir que lo que mira sobreviva a la compresión.

Eso mueve el trabajo a un lugar distinto del que teníamos previsto, y es lo que justifica las dos líneas que siguen.

## L9 · SI-MIL: qué propone

La ambición del paper: que la explicación SEA la predicción.
Dos caminos que salen de la misma lámina: uno mide, el otro selecciona.
La rama profunda no llega a producción: se descarta entera.

Paso al paper que había quedado encargado, y viene bien acá porque llega al mismo problema por otro camino. Nosotros miramos un modelo ya entrenado para ver dónde puso la atención; el paper propone construirlo de manera que no haya que ir a mirarlo.

La idea es que la explicación sea la predicción, no un anexo. Para eso, la red profunda deja de predecir y su único producto pasa a ser una selección de veinte parches, los más atendidos. La predicción se calcula aparte, con una combinación lineal de mediciones que un patólogo puede leer. Y cuando el modelo sale a producción, la rama profunda se descarta entera.

Esas mediciones son el punto que quiero que quede claro, porque son doscientas cuarenta y seis y no salen de la nada. Antes de todo esto pasa por el parche un segmentador de núcleos, HoVer-Net, que separa cada núcleo de sus vecinos y le pone una de cinco clases: epitelial neoplásico, conectivo, inflamatorio, necrótico y epitelial no neoplásico. Sobre ese mapa de núcleos se calculan las mediciones. Doscientas cinco son morfométricas y salen de una cuenta ordenada: diez propiedades por núcleo, cosas como el área, la excentricidad o la solidez; cuatro estadísticos que resumen cada propiedad en el parche, la media, la desviación, la asimetría y la curtosis; y las cinco clases de núcleo. Diez por cuatro por cinco, doscientas, más cinco conteos, uno por clase. Las cuarenta y una restantes describen cómo están distribuidos los núcleos en el espacio: medidas de grafo, tratando a las células como nodos, y medidas de mezcla de tipos celulares.

Lo importante es que cada una de esas doscientas cuarenta y seis tiene nombre legible. Una es, textualmente, la asimetría de la solidez de los núcleos neoplásicos. Otra, la mezcla de células conectivas dentro de la región neoplásica. Por eso pueden decir que el reporte del modelo es la predicción misma.

En la figura, los dos caminos que bajan de la lámina describen exactamente los mismos parches en el mismo orden, de dos maneras. La caja del medio es la bisagra: toma la atención del camino profundo, elige con ella los veinte parches, y esa selección se aplica sobre el otro camino. Y el recuadro punteado de arriba a la derecha es el clasificador profundo, marcado como descartado en inferencia.

## L10 · Resultados y costo de adopción

La tabla compara el método sobre distintos modelos de base, y uno es el nuestro.
Sobre el nuestro, la fila destacada, las dos métricas bajan.
Publican el dataset ya procesado, y la cohorte de mama está adentro.

Los resultados. Esta tabla nos interesa más que las otras del paper porque no compara el método contra otros métodos, sino el método aplicado sobre distintos modelos de base, y uno de esos modelos es el nuestro.

Sobre el primero, que es el modelo de atención más simple, la exactitud sube un poco al agregarle la rama interpretable. Sobre el segundo, que es el nuestro y es la fila destacada, bajan las dos: la exactitud algo más de un punto y el área bajo la curva un punto y medio. Sobre el tercero baja apenas. Lo digo sin ánimo de desacreditar el trabajo, que me parece sólido: el titular de que no hay compromiso entre rendimiento e interpretabilidad se sostiene sobre el primer modelo, y la fila que nos correspondería es la que baja.

Lo que sí sostienen con firmeza es lo otro, y es un resultado en sí mismo: un modelo que use únicamente las mediciones con nombre pierde bastante, y entrenar las dos ramas juntas recupera casi todo.

Vale la comparación con lo nuestro, que es nítida sin ser una competencia. La interpretación de ellos aparece durante el entrenamiento y por diseño, sobre mediciones que tienen nombre desde antes. La nuestra aparece después, sobre modelos ya congelados. Lo de ellos cambia el modelo, lo nuestro no lo toca, y por eso el costo de equivocarse también es distinto: allá empeora el modelo, acá queda mal la descripción. Hay una crítica en su introducción que nos apunta directo: explicar un modelo después sufre de una desconexión entre las características con las que fue entrenado y aquellas con las que uno lo explica.

Si quisiéramos probarlo acá, el costo más duro es de escala física: el segmentador de núcleos está entrenado a cuarenta aumentos y solo a cuarenta, tanto que ellos mismos filtraron sus datasets para quedarse con láminas de esa magnificación, y nuestras cohortes están a escalas distintas entre sí. El costo de cómputo, en cambio, se desarma solo: publican el dataset ya procesado, con mapas de núcleos y mediciones incluidos, y la cohorte pública de mama está adentro. Cruzar esas láminas con las nuestras es una tarde de trabajo.

Y dejo una pregunta de fondo. Cuando le mostraron los reportes a un patólogo, algo más de un cuarto de las mediciones que el modelo declara importantes le resultaron no relevantes. Me parece muy honesto que lo publiquen, y la pregunta es si ese número es aceptable para el estándar clínico que manejamos.

## L11 · HoVer-NeXt y la clase de mitosis

Un segmentador de núcleos con una clase de mitosis entre las suyas.
La figura del paper: el teselado, la red, y el cosido de las teselas.
Encaja sin reescalar: trabaja a media micra por píxel, como nuestras láminas privadas.

Vuelvo a nuestra línea, con el segundo modelo. La idea viene de la reunión anterior: si el modelo mira donde hay mitosis y aun así falla, quizá lo que falta no es atención sino resolución de detalle, y conviene tener un instrumento que trabaje a nivel de núcleo en vez de a nivel de parche.

Recorro la figura, que es del paper y muestra las tres piezas. Arriba está el flujo completo: la lámina se parte en teselas, cada tesela pasa por la red, y un segundo componente vuelve a coser las salidas en una sola imagen del tamaño de la lámina. Abajo a la izquierda está la red, que es un codificador y dos decodificadores que comparten ese codificador. Y abajo a la derecha está el cosido, que es la parte de ingeniería: las teselas se procesan con solapamiento, así que hay que resolver los núcleos que caen en el borde para no contarlos dos veces ni partirlos.

Las dimensiones, que es lo que quería precisar. La entrada de la red es una tesela de tres canales, rojo, verde y azul, muestreada a media micra por píxel. El codificador es una ConvNeXt versión dos, tamaño tiny, preentrenada en imágenes naturales. El primer decodificador es el de instancia y saca cinco canales: dos son mapas de regresión de distancia, que son los que permiten separar un núcleo pegado a otro, y los otros tres son una clasificación por píxel en fondo, interior del núcleo y borde del núcleo. El segundo decodificador es el de clase y saca ocho canales: fondo más las siete clases de núcleo con las que se entrenó, entre ellas mitosis. En total la red saca trece canales por píxel, y el mapa final sale de combinar las dos salidas: el decodificador de instancia dice dónde empieza y termina cada núcleo, y el de clase dice qué es.

Acá quiero corregir algo que quedó dando vueltas de la última vez, porque es fácil de mezclar. Las doscientas cuarenta y seis mediciones de las que hablé recién no son de este modelo: son del paper anterior, que usa HoVer-Net, sin la equis, como front-end de segmentación y deriva de ahí sus mediciones. Éste es otro modelo y no produce ningún vector de características por parche. Produce el mapa de núcleos que acabo de describir, con un objeto por núcleo, su contorno, su centroide y su clase.

Por qué elegimos éste y no otro. La razón concreta es la escala: está pensado para trabajar a media micra por píxel, y nuestras láminas privadas están casi exactamente en ese punto, así que no hay que reescalar nada, que es donde suelen aparecer los problemas silenciosos. Y entre sus clases tiene una de mitosis, que es la que necesitamos.

## L12 · Resultados: recortar y detectar

La atención de CLAM recorta la región, y el detector de núcleos trabaja adentro.
Recupera 13 de las 26 marcas del patólogo: la mitad.
Desde el 7,6 % de la región el cuello deja de ser el recorte y pasa a ser el detector.
Las 13 que faltan no fallan por poco: no hay ninguna detección de mitosis cerca.

Esto es lo que quedó pedido en la reunión anterior: integrar el modelo de atención al camino de detección. Está armado y con número, así que lo traigo con el resultado puesto.

La cadena tiene tres pasos, y cada uno lo hace una herramienta distinta. Primero nuestro modelo mira la lámina entera y reparte atención entre sus parches. Segundo, el recorte: nos quedamos con el doce por ciento más atendido y apagamos el resto. Ese porcentaje conviene decirlo bien, porque es el que ordena toda la lámina: la región anotada tiene dos mil cuatrocientos noventa y seis parches, así que el doce por ciento son trescientos parches encendidos, y en superficie, cuatro coma veinticinco milímetros cuadrados. Tercero, el detector de núcleos trabaja adentro de ese recorte. Es un modelo ajeno, entrenado por otro grupo, que no sabe nada del nuestro ni de nuestra tarea.

Lo que produce no es un mapa de calor ni una caja alrededor de una zona sospechosa: es un inventario de núcleos. En esta lámina segmentó más de doscientas treinta y ocho mil células y a cada una le puso una clase. A ciento setenta y siete de ellas les puso mitosis. Entonces cada marca amarilla de la figura es un núcleo, uno solo, con su posición; y las marcas blancas son las veintiséis mitosis que dibujó el patólogo. Dos fuentes independientes sobre la misma imagen, y toda la lámina consiste en compararlas.

Los tres paneles de la izquierda son la misma región en tres estados: la atención, el recorte, y encima lo que encontró el detector, con los puntos llenos para las detecciones que caen dentro del recorte y los círculos vacíos para las de afuera. Lo que se ve es que las detecciones se agrupan sobre el recorte: la atención y el detector están mirando el mismo tejido sin haberse consultado. Abajo hay cuatro coincidencias a resolución nativa: el círculo amarillo es la detección y el blanco la marca del patólogo, y se superponen sobre el mismo núcleo. No están de acuerdo sobre una zona: están de acuerdo sobre una célula.

El número es trece de veintiséis, la mitad, y el emparejamiento es uno a uno. Eso importa: si uno le pregunta a cada marca cuál es la detección más cercana, el número sube a catorce o dieciocho según la tolerancia, pero son siempre las mismas trece detecciones contadas varias veces. Una detección no puede acreditar dos marcas.

Sobre las otras trece, dos cosas. La primera es que no fallan por poco: movimos la tolerancia en un rango de diez veces, de siete micras y media a setenta y cinco, y el número se queda clavado en trece; y la detección de mitosis más cercana a una marca fallada está a ciento quince micras de mediana, que son unos seis núcleos de distancia. No apunta al lado: no hay nada ahí. La segunda es que averiguamos por qué, y es la lámina dieciséis.

La tabla junta los dos límites de esta prueba, y es lo que cambió la conversación. Cada fila es un tamaño de recorte; una columna dice cuántas marcas entran en el recorte, y la de al lado, cuántas de ésas además se detectan. Veníamos discutiendo cuán grande convenía hacer el recorte, y la tabla dice que a partir del siete coma seis por ciento de la región eso deja de ser el problema: por generoso que uno lo haga, el techo se queda en trece. El factor que manda pasó a ser la detección.

Y una cosa que este número no dice. La mitad no es la exhaustividad del detector en mitosis: el denominador son las marcas del patólogo, no las mitosis que hay en la lámina. Tampoco calculamos precisión, y es deliberado: el patólogo marca solo donde la evidencia es clara, así que una detección sin marca no es un error.

## L13 · El detector sobre la lámina completa

El brazo de control: el detector solo, sin nada del modelo de atención encima.
La lámina entera son 68 mm² y 177 detecciones.
Recupera las mismas 13 de 26 que con el recorte puesto.
De la región sin marcas no se afirma nada.

Falta el brazo de control, y va después a propósito, porque es el que hace legible al anterior. Si digo trece de veintiséis con el recorte puesto, la pregunta inmediata es comparado con qué.

No hubo que correr nada nuevo para tenerlo, porque la corrida fue así desde el principio: la lámina completa, y el recorte aplicado después, sobre la salida. Fue deliberado. Si hubiéramos recortado antes para ahorrar cómputo, este brazo no existiría y no habría manera de construirlo sin volver a empezar.

Lo que se ve son las ciento setenta y siete detecciones sobre la lámina entera. De las noventa y cinco de la izquierda no afirmo nada: en esa parte no hay marcas del patólogo, así que no son ni aciertos ni errores, y van dibujadas del mismo color justamente para no sugerir lo contrario.

La tabla es lo que quiero discutir. Cada fila es una manera de usar el modelo, y las columnas dicen qué cuesta y qué devuelve. Revisando la lámina entera, sesenta y ocho milímetros cuadrados, se recuperan trece de las veintiséis marcas. Revisando solo la región anotada, que es la mitad de la superficie, se recuperan las mismas trece; eso no es una sorpresa sino una comprobación, porque las veintiséis marcas caen todas ahí. Y revisando el doce por ciento más atendido, cuatro milímetros cuadrados, se recuperan once.

O sea que entre el primer brazo y el último la superficie a revisar baja dieciséis veces y las marcas recuperadas bajan de trece a once. Eso separa dos preguntas que conviene no mezclar, porque no tienen la misma respuesta. Si la pregunta es cuánta superficie hay que ponerle delante a un patólogo, el recorte responde bien: divide el área por dieciséis y cuesta dos marcas. Si la pregunta es cuántas mitosis se encuentran, el recorte no ayuda, porque el techo lo pone el detector.

Una última cosa sobre el costo, que ordena lo anterior: la lámina entera tardó dieciocho minutos. Recortar para ahorrar cómputo hoy no hace falta. Recortar para achicar lo que hay que revisar sí tiene sentido. Son dos motivos distintos y no piden el mismo tamaño de recorte.

Con eso queda planteada la cadena, y las cuatro láminas que siguen son las pruebas que le hicimos.

## L14 · CLAM, Mammoth y el detector a igual carga

Cuántos objetos hay que mirar para llegar al mismo número de marcas.
A recorte fijo la comparación premia a la máscara más grande por ser más grande.
Los dos caminos piden una carga parecida hasta 13 marcas, y de ahí el detector se topa.

Hay una comparación que faltaba y es la primera: el detector, ¿agrega algo sobre la atención sola? Para contestarla la atención deja de ser el techo y pasa a ser la línea base contra la que se lee todo.

Antes, cómo está armada la tabla, porque la forma de compararlos importa más que los números. Si uno compara los brazos a recorte fijo, dejando entrar la misma cantidad de parches en cada uno, gana el que tenga la máscara más grande, y gana por tamaño y no por calidad. Así que damos vuelta la pregunta: fijamos el resultado y medimos el costo. Cada fila es un nivel de marcas recuperadas, y cada celda dice cuántos objetos hay que mirar para llegar ahí con ese brazo.

Los brazos son cuatro de atención y uno de detección. Los dos primeros son nuestro modelo y la variante con expertos, que no se suman: son alternativos, porque la variante es el mismo modelo con la primera capa cambiada. Los dos del medio son combinaciones de sus máscaras, la intersección y la unión. Y el último es el detector trabajando solo, sin recorte.

Tres cosas que solo aparecen con esta forma de mirar. La primera es que la unión nunca es el mejor brazo. A recorte fijo parecía el mejor de todos, y acá queda al nivel del peor de los dos que la componen: su ventaja era el tamaño de la máscara. La segunda es que la intersección es el brazo más eficiente donde la carga es chica: donde los dos modelos coinciden, aciertan. La tercera es la que quiero discutir: hasta trece marcas los dos caminos piden una carga parecida en número de objetos, ochenta y dos núcleos el detector contra ochenta y cuatro parches la intersección, pero los objetos son de tamaño muy distinto, porque un parche mide ciento diecinueve micras de lado y un núcleo es un punto ya localizado. Y por encima de trece el detector deja de ser una opción a cualquier carga: está topado ahí, no pasa de trece ni con la lámina entera, mientras que la atención sola llega a las veintiséis.

Una precisión sobre lo que esta lámina no dice: es sobre dónde pone la atención cada modelo en una lámina, no sobre cuál clasifica mejor. Eso está cerrado desde el sprint pasado y no lo reabre.

## L15 · El checkpoint de carcinoma invasivo

El encargo era repetir la cadena con el otro checkpoint.
Por AUC los dos parecen equivalentes: los intervalos se solapan de sobra.
Por recorte no: el checkpoint del gate es claramente peor.

El otro encargo era repetir la cadena con el checkpoint de carcinoma invasivo, en vez del de carcinoma in situ que veníamos usando, y comparar. No hubo que volver a correr el detector: la lámina se corrió entera y el recorte se aplica después.

La lámina es que las dos lecturas no coinciden, y por eso está partida en dos.

A la izquierda, por área bajo la curva parecen equivalentes: cero coma ochocientos sesenta y cinco el checkpoint del gate contra cero coma novecientos diecinueve el otro, con intervalos que se solapan de sobra. Con este número solo uno concluiría que da igual cuál usar.

A la derecha, la misma pregunta hecha por recorte, que es como se usa en la práctica, y no da igual. En el recorte más chico, el cuatro por ciento de la región, el checkpoint del gate mete una marca de veintiséis y el otro catorce. En el siete coma seis por ciento, ocho contra dieciocho. En el doce, once contra veintidós. Para poner las mismas marcas delante del patólogo hay que darle bastante más superficie.

La explicación de por qué discrepan está en la línea del medio, y es un patrón que ya nos había aparecido este sprint. El área bajo la curva resume todos los umbrales a la vez; el recorte es un umbral solo, y de los extremos. El checkpoint del gate deja los parches con mitosis en el percentil ochenta y seis, y el otro en el noventa y cinco. Esa diferencia casi no mueve el área bajo la curva y decide entera la lista de los trescientos más atendidos.

Dos salvedades del pie, y la primera es importante. El brazo del gate es la variante con expertos, no el modelo plano: el plano de esa tarea no existe en disco y lo entrena un trabajo que sigue en la cola. Así que todavía no separamos si esto es propiedad de la tarea o del brazo, y ésa es la pregunta que queda abierta acá. La segunda es el chequeo de sanidad, y pasa: en la región entera los dos brazos convergen a trece de veintiséis, que es el factor de detección solo. Si ahí no coincidieran, habría un error en el código.

## L16 · Las 13 que se escapan sí estaban segmentadas

Las 13 marcas que el detector no acredita tienen un núcleo segmentado encima. Las 13.
No se escaparon por falta de segmentación: se escaparon por la clase.
Las acreditadas son el control, y las dos mitades salen indistinguibles salvo en la etiqueta.

Vuelvo a las trece que se escapan, que era lo que había quedado sin contestar. Habíamos cerrado en que no hay ninguna detección de mitosis cerca, y nos detuvimos ahí sin preguntar ausencia de qué.

La respuesta es que el núcleo estaba. Las trece marcas falladas tienen una instancia segmentada encima. Las trece, sin excepción. Y no cerca: encima, a dos coma un micras de mediana entre el centro de la marca y el centro del núcleo, sobre marcas cuyo lado mediano es dieciséis coma siete micras. Lo que falló no es la segmentación, es la etiqueta que le puso la cabeza de clasificación.

La columna de la izquierda es lo que hace legible a la de la derecha, y por eso está: son las trece acreditadas, pasadas por exactamente el mismo procedimiento. Si el procedimiento no las recuperara a ellas, el problema sería el procedimiento y no el grupo de estudio. Y las dos mitades salen indistinguibles en todo: misma distancia al centroide, uno coma nueve contra dos coma un micras; misma densidad de núcleos alrededor, nueve instancias dentro de quince micras en las dos; mismo tamaño de marca. La única variable que las separa es la clase.

Adónde fueron a parar dice algo. Doce de las trece recibieron la clase célula epitelial, que es la clase padre: en un carcinoma de mama una figura mitótica es una célula epitelial, así que el modelo no la está confundiendo con estroma ni con un linfocito, está perdiendo la distinción fina. La restante salió neutrófilo.

Esto cambia el costo del arreglo, y es el motivo por el que me importa. Lo caro, barrer la lámina y segmentar doscientas treinta y ocho mil células, ya está pagado y su salida está guardada. Si lo que falla es la etiqueta, alcanza con una segunda etapa de clasificación sobre los objetos que ya existen. No hace falta tocar la segmentación ni volver a correr el detector.

Y la explicación de fondo es de dominio: la clase de mitosis de este detector se entrenó y se validó solo en colon, mientras que segmentar y tipificar núcleos en mama sí tiene número propio y bueno. Se ve exactamente esa forma: lo que sabe hacer fuera de su tejido lo hace bien, y lo que nunca se validó fuera de colon es lo que falla.

## L17 · En qué se fija el detector

Las 164 detecciones que no acreditan ninguna marca, y las 13 que se escaparon.
145 de las 164 son el mismo tipo de recorte: el 88 %.
No son falsos positivos, y no se calcula precisión.

Cierro con las imágenes, que es lo que pediste ver: en qué se está fijando el detector con las otras ciento sesenta y cuatro detecciones.

La lámina de contacto grande son ésas: las ciento sesenta y cuatro que no acreditaron ninguna marca. Ciento sesenta y cuatro más las trece acreditadas son las ciento setenta y siete de la lámina entera. Cada recorte está a resolución nativa, con una ventana de sesenta micras de lado, que le da contexto a una figura mitótica de diez o veinte micras.

Se parecen entre sí, y bastante más de lo que esperábamos. Agrupándolas por color y textura, ciento cuarenta y cinco de las ciento sesenta y cuatro, el ochenta y ocho por ciento, caen en un solo grupo: epitelio tumoral denso, recortes oscuros y saturados prácticamente sin fondo, con un núcleo hipercromático y condensado en el centro. Es exactamente la forma que el detector busca, y es la misma que tienen las trece que sí acertó. Lo que se despega es un grupo chico y bien delimitado: quince recortes claros, con dos tercios de fondo, que son tejido laxo o borde de lámina.

A la derecha están las trece falladas de la lámina anterior, centradas, cada una sin ninguna detección cerca. En varias se ve una figura mitótica de manual. Ése es el bloque que más informa, porque muestra en qué se equivoca.

Y lo que no se puede decir de esta lámina, que acá importa más que en ninguna otra: las ciento sesenta y cuatro no son falsos positivos. El patólogo marca solo donde la evidencia es clara, no pretende marcarlo todo, así que una detección sin marca puede ser perfectamente una mitosis real sin marcar. Por eso no calculamos precisión y ningún panel las pinta como error. Y el parecido que acabo de describir es de píxeles, no semántico: que dos recortes sean vecinos significa que comparten color y textura, no que sean la misma entidad.

Con esto cierro. Lo que me gustaría discutir es hacia dónde movemos el número del detector, y hay dos cosas baratas antes de tocar nada. Una es mirar si en esos trece la clase mitosis quedó segunda por poco, que se responde con lo que ya está guardado y decide entre recalibrar un umbral o reentrenar la cabeza. La otra es de fondo: si el problema es que su clase de mitosis nunca vio mama, existe un conjunto público de mitosis en mama, con doscientos casos y licencia abierta, que es el material natural para atacarlo. Y una advertencia que viene con ese mismo conjunto, porque nos toca: los detectores de mitosis se caen al cambiar de escáner, y ésa es justamente la razón por la que ese desafío existe.
