# Notas del presentador — deck B5 (guion hablado, fuente versionada)

> **Qué es:** la fuente CANÓNICA y versionada de las notas del presentador del deck B5,
> en el formato VIGENTE (guion HABLADO corrido — ver `convenciones_deck_b5.md` §3.b y la
> memoria [[notas-presentador-guion-didactico]]). Ernesto edita las notas en OnlyOffice;
> este archivo es la copia durable (el `.pptx` está gitignored y el motor `set_notes` del
> generador aún emite el formato por-fases LEGACY → NO regenerar el deck para "actualizar notas").
>
> **Estado (26-jun):** slides 1–15 + slide final de próximos pasos FINALIZADAS. El deck se
> recortó de 21 a ~16 slides (ver la sección "Slide final — Próximos pasos" para los recortes).
> No quedan slides pendientes de escribir.
>
> **Convención de estilo:** prosa, solo lo que se dice, sin etiquetas de fase, sin "deck",
> registro profesional, fiel a las ecuaciones del diagrama, sin ejemplos numéricos en el guion,
> definir antes de usar, encadenar slide con slide. Sin nº de job, sin nombres.

---

## Slide 1 — Portada (Integración de MAMMOTH y PathPT)

Esto es el cierre del sprint B5. Todo el trimestre giró en torno a una sola pregunta, y conviene dejarla planteada desde el comienzo.

El título reúne los dos modelos que integramos y medimos este sprint: MAMMOTH y PathPT. En el fondo, lo que sigue son esas dos integraciones, contadas en orden.

El baseline contra el que se compara todo es CLAM, y los tres corren sobre las mismas features CONCH: la misma cancha para todos.

La pregunta de fondo es si alguna modificación de la arquitectura de CLAM nos permite mejorar los resultados en tareas clínicas específicas, donde además el dataset está fuertemente desbalanceado, o si el límite está en otro lado. Para responderla integramos y medimos los dos modelos con un mismo protocolo de evaluación, común y honesto.

El hilo conductor es uno solo: separar el efecto del modelo del efecto del dato.

Antes de cualquier número, dejemos clara la vara con la que vamos a medir.

---

## Slide 2 — Objetivos del sprint

> Contenido de la slide (bullets): MAMMOTH (cómo funciona e integra en CLAM — diagrama +
> resultados) con dos sub-objetivos — reemplazo directo (drop-in) sobre 8 tareas (microcalc,
> patrones histológicos, invasión linfovascular) y variante keep_slots (cuello de botella
> aprendido) sobre 4 tareas — · PathPT (visión + lenguaje — diagrama + resultados) · Marco de
> evaluación común (comparación pareada k=5 mismos splits; métrica honesta balanced acc + AUC +
> confusión). NO se incluye la prueba de loss como objetivo.

Antes de entrar a los resultados, conviene dejar claro cómo los vamos a juzgar; esto es lo que le da credibilidad a todo lo que viene después.

El primer eje es MAMMOTH: vamos a ver cómo funciona y cómo se integra dentro de CLAM, primero con un diagrama y después con los resultados. Lo probamos en dos variantes. La primera es un reemplazo directo de la primera capa de CLAM —lo que llamamos drop-in— y la medimos sobre ocho tareas: las tres binarias de microcalcificaciones, cuatro patrones histológicos y la invasión linfovascular. La segunda es una variante con un cuello de botella aprendido, keep_slots, que probamos sobre cuatro tareas para ver si cambiaba el comportamiento.

El segundo eje es PathPT, de otra familia por completo: combina visión y lenguaje. También lo vamos a ver con su diagrama y sus resultados.

Y atravesando todo, el marco de evaluación común, que es lo que hace creíble la comparación. Tiene dos piezas. La primera es que la comparación es pareada con validación cruzada de cinco particiones: cada modelo se mide contra CLAM sobre exactamente las mismas particiones, una por una, así la diferencia por partición cancela la suerte del sorteo; y son cinco particiones, no un único split que podría salir optimista. La segunda es la métrica: siempre reportamos balanced accuracy junto al AUC y la matriz de confusión, nunca una métrica sola.

Vale la pena detenerse en por qué usamos balanced accuracy. Con clases desbalanceadas, un modelo que siempre responde la clase más común puede tener una accuracy alta y aun así ser inútil; la balanced accuracy lo deja en evidencia.

En resumen: comparación pareada, cinco particiones, y balanced accuracy junto a AUC y matriz de confusión. Con eso evitamos engañarnos solos.

Con la vara fijada, abrimos el primer eje: MAMMOTH.

---

## Slide 3 — Divisoria MAMMOTH (transición)

Entramos al primer eje: MAMMOTH, una intervención sobre la primera capa de CLAM, la que proyecta los parches. La pregunta es si reemplazar esa única capa por una mezcla de expertos mejora los resultados en nuestras tareas. Lo recorremos en orden: qué es, dónde entra, qué hace por dentro, y qué dieron los resultados.

---

## Slide 4 — MAMMOTH: qué es y por qué (tarjetas + 2 figuras del paper)

En CLAM, una sola capa lineal proyecta todos los parches al espacio interno del modelo. Esa única capa es el cuello que MAMMOTH ataca.

Esa capa es una matriz W que multiplica al vector de cada parche: toma los 512 números de CONCH y los re-mezcla en otra combinación. El problema es que hay una sola W para todos los parches, y en una lámina los parches son muy distintos: tumor, estroma, grasa, necrosis. Son distintos fenotipos, distintos tipos visuales de tejido.

Por qué una sola matriz limita: durante el entrenamiento, los parches de tumor "tiran" de esa W en una dirección y los de grasa tiran en otra. Como la W es una sola y compartida, esos tirones opuestos se pelean entre sí y se cancelan en parte, así que la matriz queda en un punto intermedio que no le sirve bien a ninguno. Eso es lo que el paper llama interferencia de gradientes entre parches. MAMMOTH le da a cada fenotipo su propia transformación —eso es una mezcla de expertos—, así el tumor ajusta la suya y la grasa la suya, sin pelearse: cada una se especializa de verdad. El cómo —router, slots, expertos de bajo rango— lo abrimos en las próximas dos slides.

La figura de arriba lo confirma. En el panel A hay dos mapas del espacio interno en dos dimensiones: arriba, con la capa original, una nube continua sin estructura; abajo, con MAMMOTH, el espacio se separa en grupos nítidos, un color por experto. En el panel B hay ocho agregadores distintos: para cada uno, el punto rojo es con MAMMOTH y el negro sin él, y el rojo queda siempre a la derecha del negro, en los ocho, con el mismo presupuesto de parámetros. Se enchufa a cualquier agregador y lo mejora.

La figura de abajo muestra el por qué, y es un resultado del propio paper. Son dos láminas de histopatología —no radiografías—, una de cada subtipo de cáncer de pulmón. En el panel A, cada lámina está pintada con un mapa de calor según a qué slot se rutea cada parche: se ven regiones nítidas, cada zona de tejido se va a un slot distinto. En el panel B, tres slots con los parches que más activa cada uno, mezclando las dos láminas: uno reúne el tejido tumoral, otro el estroma y los alvéolos, y el tercero los linfocitos y los glóbulos rojos. Dos patólogos certificados etiquetaron esos grupos y confirmaron que cada slot reúne tejido morfológicamente coherente. Y todo esto surge solo durante el entrenamiento, sin que nadie le marque los tejidos al modelo.

En resumen: un cambio quirúrgico en una sola capa, que nos da una comparación limpia contra CLAM. Ahora veamos dónde entra exactamente esa capa en el pipeline.

---

## Slide 5 — Diagrama de integración (dónde entra MAMMOTH)

Este es el pipeline completo de CLAM; el objetivo de esta slide es ubicar dónde se integra MAMMOTH. Los parches entran por la izquierda, CONCH los convierte en vectores de 512, y el primer bloque naranja —la capa que los proyecta— es el único punto que cambia: ahí MAMMOTH reemplaza esa capa por la mezcla de expertos. Las etapas posteriores —atención, pooling y clasificador final— permanecen idénticas a CLAM. Una precisión: MAMMOTH interviene la capa de entrada, no el clasificador final. Pasemos a su interior.

---

## Slide 6 — MAMMOTH: qué hace (zoom de la 1ª capa, MoE)

Esta es la caja naranja de la slide anterior, abierta por dentro. Seguimos un parche desde que entra hasta que sale.

En el tope entran los parches de la slide, el tensor z de N por 512. El primer bloque, la proyección a query, aplica q igual a la normalización de W_q por z, y lleva cada parche de 512 a 256 dimensiones: ese query de 256 está organizado en 16 cabezas de 16, es decir, el mismo parche mirado por 16 lentes en paralelo —subespacios aprendidos, no criterios con nombre fijo como textura o color—.

El segundo bloque es el ruteo por slots, la ecuación 3 del paper y el corazón de MAMMOTH. Acá se materializa la idea de los fenotipos que vimos antes: una lámina mezcla parches de tejidos muy distintos —tumor, estroma, alvéolos— y a cada uno de esos fenotipos conviene tratarlo por separado. Para eso están los 300 slots: cada slot tiene un vector aprendido —su prototipo— que con el entrenamiento termina representando un fenotipo, una morfología concreta. Lo que hace el ruteo es agrupar en cada slot los parches de su fenotipo.

No es que cada parche se asigne a un slot; es al revés: cada slot recoge una contribución de todos los N parches a la vez, y esto se hace por separado —en paralelo— para los 300 slots, cada uno con su propio reparto de pesos. La fórmula es u igual a la suma, sobre los N parches, de D por q: el slot es el promedio de los queries de todos los parches, cada uno pesado por un coeficiente D. Ese peso se obtiene comparando el prototipo del slot con el query de cada parche mediante un producto interno —un puntaje de parecido—, que una softmax sobre los N parches normaliza para que sumen uno. De este modo, un parche muy parecido al prototipo pesa mucho y uno distinto casi nada: cada slot termina siendo un resumen de toda la lámina, sesgado hacia los parches afines a su prototipo. Los 300 slots son esos resúmenes, fijos y ordenados, que reemplazan a los N parches sueltos y de número variable.

Esos 300 slots se reparten entre 30 expertos, 10 cada uno, y cada experto aplica a sus slots una transformación propia —la especialización por fenotipo que buscábamos—. Esa transformación, o igual a u por A por B, es un LoRA de bajo rango: la matriz A baja de 16 a 8 dimensiones y es compartida, la matriz B sube de 8 a 32 y es propia de cada experto, con el rango 8 ajustado automáticamente para no sumar parámetros. Después, el bloque de combinación vuelve a armar los parches con la fórmula h igual a la suma sobre los slots de C por o, donde una segunda softmax, C, reparte sobre los 300 slots. Las dos softmax se diferencian por su eje: la primera reparte sobre los N parches para construir los slots; la segunda, sobre los 300 slots para reconstruir cada parche.

Lo importante: entra un tensor de N por 512 y sale otro de N por 512, así que es un reemplazo transparente de la capa lineal, y como el rango se ajusta solo pesa casi lo mismo —es el banner "mismo presupuesto"—. Por eso, si MAMMOTH no mejora, no será por falta de capacidad. Veamos ahora esto mismo sobre la figura oficial del paper, con las dimensiones reales.

---

## Slide 7 — MAMMOTH: flujo de datos sobre la arquitectura oficial

Acabamos de recorrer esa primera capa por dentro, paso a paso. Esta es la misma mecánica, ahora sobre la figura de arquitectura tal como la publican los autores, de punta a punta y en su propio lenguaje visual.

En el encoder los parches entran y salen como z, de tamaño N por 512: el punto de partida. La proyección W_q los lleva a la query q, de N por 256, con esos 256 organizados en 16 cabezas de 16.

El siguiente bloque es el ruteo por slots, y conviene seguirlo sobre el diagrama. Fíjense cómo la columna de N parches se condensa en un bloque fijo de 300 slots: ese es el paso. Cada slot tiene un vector aprendido, su prototipo, que con el entrenamiento representa un fenotipo —tumor, estroma, alvéolos—. Y no es que cada parche caiga en un slot; es al revés: cada slot recoge una contribución ponderada de todos los parches. Ese peso es justo lo que dice el cartel, D igual a softmax sobre los N parches del producto interno entre la query q y el prototipo S del slot —S es el tensor de prototipos aprendidos, 30 expertos por 16 cabezas por 10 slots, y cada prototipo es un vector de 16, la misma dimensión que el query por cabeza—: un puntaje de parecido que la softmax convierte en pesos que suman uno. Así, un parche parecido al prototipo pesa mucho y uno distinto casi nada, y cada slot termina siendo un resumen de toda la lámina, inclinado hacia su fenotipo; por eso los N parches sueltos, variables en número, quedan reemplazados por 300 resúmenes fijos.

Un detalle conecta con las cabezas: todo este ruteo corre por separado dentro de cada una de las 16 cabezas —en la figura, x_i,cabeza—, así que el mecanismo se repite en paralelo, una vez por cabeza. Sobre los slots actúan los expertos: cada uno aplica a los suyos su propia transformación de bajo rango, el LoRA, con una matriz A que baja de 16 a 8 dimensiones, compartida, y una B_e que sube de 8 a 32, propia de cada experto. Esa transformación propia es la especialización: cada experto ajusta la suya sin pelear con las demás, y los 300 slots salen transformados como o, de 300 por 512.

El último bloque es el cross-head concat: vuelve a unir las 16 cabezas que veníamos procesando por separado y, con la segunda softmax —la que reparte sobre los 300 slots—, reconstruye cada parche como una mezcla de slots; así sale h, otra vez de N por 512, que entra a CLAM intacto. Lo esencial se ve solo: entra N por 512 y sale N por 512, un reemplazo transparente de la capa lineal. De esta misma figura sale la variante que medimos a continuación, keep_slots, que cambia un único punto: la salida.

---

## Slide 8 — MAMMOTH: la variante keep_slots

De esta misma arquitectura sale una variante, keep_slots, que cambia un solo punto: la salida.

El tronco de arriba es idéntico a la slide anterior, hasta los 300 slots transformados, o de 300 por 512. Lo único nuevo es el nodo de bifurcación: keep_slots decide qué recibe CLAM, y de ahí salen dos caminos.

A la izquierda, keep_slots en falso, es la base que ya medimos: el bloque de combinación recompone los 300 slots de vuelta en parches y devuelve h, de N por 512, así que CLAM agrega sobre los N parches, como siempre. Es el reemplazo transparente de la capa lineal.

A la derecha, keep_slots en verdadero, es la variante nueva: se salta esa recombinación y le entrega a CLAM los 300 slots directamente, de modo que ahora agrega sobre 300 slots en lugar de sobre los N parches. Eso es un cuello de botella aprendido: en vez de un número variable de parches, todo pasa por un conjunto fijo de 300.

La cabeza de CLAM y la pérdida son las mismas en los dos caminos; lo único que cambia es sobre qué agrega. La idea es que un slot puede concentrarse en unos pocos parches raros, así que quedarse con los slots le da capacidad dedicada a la clase minoritaria, esa que la base suele perder cuando colapsa hacia la mayoritaria. Medimos las dos posiciones del interruptor en pareado. Empecemos por la base, en ocho tareas.

---

## Slide 9 — MAMMOTH drop-in: resultados (8 tareas, k=5)

Ocho tareas, todas pareadas contra CLAM. Leemos el delta pareado de arriba a abajo, en balanced accuracy y AUC.

Solo dos tareas mejoran en las dos métricas: tejido no neoplásico y cribiforme, con cuatro a cinco centésimas de balanced accuracy y dos a tres de AUC. Y son, justamente, las dos de dataset más balanceado, con positivos y negativos casi parejos en la columna del dataset. En el resto, donde el dataset está desbalanceado, el delta queda en cero o levemente negativo. La pequeña mejora sigue al balance de los datos, no a la arquitectura: como reemplazo directo, MAMMOTH no es una palanca. A continuación, una de ellas en detalle: la invasión linfovascular.

---

## Slide 10 — MAMMOTH: invasión linfovascular

Esta es la tarea con más datos, casi 2.800 láminas, y la evaluación más sana: cada una de las tres clases —ausente, no identificado y presente— tiene casos suficientes en cada partición. Si MAMMOTH iba a destacar, era acá.

A la izquierda, las dos métricas bajan con MAMMOTH: balanced accuracy de 0.62 a 0.58 y AUC de 0.83 a 0.82. A la derecha, la matriz de confusión muestra por qué: el modelo manda casi todo a la clase mayoritaria, no identificado, y vacía la que importa clínicamente, presente, cuyo acierto cae a 0.43. Eso es un colapso hacia la clase mayoritaria.

La lección es que más datos no rescataron a MAMMOTH; al contrario, afinaron la medición y dejaron ver una regresión leve pero consistente en las cinco particiones. Ese colapso es justo lo que la variante keep_slots fue diseñada para revertir.

---

## Slide 11 — MAMMOTH keep_slots: resultados (4 tareas, k=5)

Esta es la variante hecha a medida para revertir aquel colapso. La tabla tiene la misma estructura y el mismo CLAM de baseline que la del drop-in, así que se comparan fila a fila. Y la respuesta, leyendo las columnas de delta pareado, es la misma: keep_slots no supera a CLAM en ninguna de las cuatro tareas, ni en balanced accuracy ni en AUC; todos los deltas quedan en cero o negativo, dentro del ruido.

Eso sí, en parte hace lo que prometía. El cuello de botella de slots recupera el acierto de la clase rara que el drop-in había vaciado: en la invasión linfovascular, la clase presente sube de 0.43 a 0.52. Pero ese recall lo paga con la clase mayoritaria, así que la balanced accuracy total no se mueve; en CDIS incluso supera a CLAM en la clase rara, al mismo costo.

Con esto cierra el eje de MAMMOTH: doce tareas en total —ocho del reemplazo directo y cuatro de keep_slots—, cero palancas. Ni reemplazar la capa ni cambiar qué se agrega mejora los resultados; el cuello está en los datos, no en la arquitectura. Ahora cambiamos de eje por completo: visión más lenguaje, con PathPT.

---

## Slide 12 — Divisoria: PathPT

PathPT es de otra familia por completo: combina visión y lenguaje. En lugar de tocar el agregador, clasifica parche a parche apoyándose en descripciones de texto de cada tejido, todo sobre CONCH congelado. Lo recorremos como antes: la idea, la arquitectura y los resultados.

---

## Slide 13 — PathPT: la idea y el alcance

Esta es la figura del paper, con cuatro paneles; los recorremos en orden. El panel a, arriba a la izquierda, es el MIL clásico, lo que hace CLAM: comprime toda la lámina en un vector y predice una sola etiqueta para toda la lámina. El panel b, a su derecha, es PathPT: clasifica parche por parche y, además, marca en la lámina dónde está el hallazgo.

¿Cómo clasifica cada parche? Comparándolo contra texto, que es justo lo que dibuja ese panel b. La clave es que CONCH no es solo un extractor de imágenes: fue entrenado con imágenes y descripciones a la vez, así que a cada parche se le puede preguntar a qué descripción de tejido se parece más.

Abajo, los otros dos paneles dan el alcance: el panel c, la variedad de tareas de patología que cubre el método; el panel d, sus comparaciones contra los MIL clásicos del paper. Y lo barato del enfoque es que CONCH queda congelado: solo se entrenan tres piezas chicas, que vemos en la arquitectura. Abramos ese forward.

---

## Slide 14 — PathPT: arquitectura (forward)

Lo abrimos con el mismo estilo de diagrama que usamos para CLAM. Son tres ramas que convergen: visión a la izquierda, texto a la derecha, y abajo el matching, donde se encuentran. En el centro está CONCH, el modelo base, congelado; lo único que se entrena son las piezas naranjas de los costados. En el diagrama, las partes de CONCH llevan la letra fi y van en gris, y las piezas entrenables la letra theta, en naranja: theta-uve en visión, theta-te en texto.

La rama de visión arranca con los N parches, cada uno una imagen con su coordenada en la lámina. Pasan por la visión de CONCH y quedan como vectores de 512, igual que en CLAM. La diferencia es que CONCH mira cada parche aislado, así que PathPT le agrega contexto espacial en dos escalas: primero unas convoluciones, que mezclan cada parche con sus vecinos cercanos —contexto local—, y después una atención, que deja que cada parche mire a toda la lámina —contexto global—. Sale uve-barra, un vector mejorado por parche.

La rama de texto es la novedad: en lugar de escribir a mano la descripción de cada clase, la aprende. Las palabras de contexto del prompt son vectores entrenables, que arrancan desde la frase "una imagen de histopatología de". Se arma el prompt con el nombre de cada clase, pasa por el transformer de texto de CONCH y se proyecta, y sale te: un vector de 512 por cada clase.

Acá está la idea clave: tanto los parches como las clases terminan como vectores de 512 en el mismo espacio, el que CONCH aprendió para comparar imágenes con texto. Por eso, abajo, el matching compara cada parche contra cada clase con el coseno —cuánto apuntan en la misma dirección dos vectores—, y un softmax convierte esos parecidos en probabilidades. El resultado es P: para cada parche, qué clase es. Eso es clasificar parche a parche; con esta arquitectura, veamos los resultados.

---

## Slide 15 — PathPT: necrosis (cierre del eje PathPT)

Primer resultado de PathPT: necrosis, una tarea binaria —ausente o presente—, pareada contra CLAM sobre los mismos splits. El veredicto, anticipándolo, es que no aporta.

A la izquierda, cada fila es una partición y la columna del delta muestra el efecto fold a fold: está repartido, sin un signo que domine. La fila de la media lo resume: el delta de balanced accuracy es −0.020, con una variabilidad que cruza el cero, y el de AUC, −0.066. A la derecha, la matriz confirma que no es un clasificador redondo: acierta presente 0.76, pero ausente solo 0.48.

El dato que explica el porqué está abajo: PathPT apenas se despega de su punto de partida sin entrenar nada —lo que CONCH ya da por sí solo, un AUC cercano a 0.62—, mientras que CLAM llega a 0.727. Entrenar las piezas nuevas casi no agrega nada, y se queda por debajo del baseline. Ese es el balance de PathPT: sumar lenguaje a la visión, sobre CONCH congelado, no logra superar a CLAM. Con esto cerramos el segundo eje y pasamos al balance final.

---

## Slide final — Próximos pasos (Magnificación)

> Nota estructural (26-jun): recortes al cierre. Eliminadas del deck B5: tasa mitótica,
> microcalc go/no-go (PathPT cierra en necrosis, slide 15), divisoria de cierre, síntesis
> "3 ejes / 0 palancas" y CLAM + loss. **El único cierre es esta slide de PRÓXIMOS PASOS.**
> Deck final ≈ 16 slides (1–15 + próximos pasos). Falta borrar esas slides en el `.pptx`
> (OnlyOffice); `generate_b5_deck.py` y `convenciones §7` aún las listan (LEGACY; propagar solo
> si se pide). Próxima dirección = magnificación (paper CPathAgent) — memoria
> [[magnificacion-cpathagent-proxima-direccion]].
>
> Contenido de la slide (bullets) — **Magnificación y contexto espacial**: (1) Múltiples
> magnificaciones: bajo aumento (contexto del tejido) + alto aumento (detalle celular); (2) Más
> contexto espacial: más parches y región más amplia por lámina; (3) Enfoque tipo agente sobre
> alta resolución (CPathAgent): navegar la lámina como un patólogo, dónde y a qué aumento mirar.

Para cerrar, hacia dónde sigue esto. Después de ver que cambiar el modelo no mejoró los resultados, el camino que vamos a explorar es la magnificación: cómo y a qué nivel de aumento mira el modelo el tejido.

Tiene tres frentes. El primero es trabajar a múltiples magnificaciones, combinando el bajo aumento, que aporta el contexto del tejido, con el alto aumento, que aporta el detalle celular. El segundo es ampliar el contexto espacial: usar más parches y una región más grande de la lámina. Y el tercero es un enfoque tipo agente sobre imágenes de alta resolución, en la línea de CPathAgent, donde el modelo navega la lámina como lo haría un patólogo, decidiendo dónde y a qué aumento mirar.

Esa es la dirección para el próximo período.
