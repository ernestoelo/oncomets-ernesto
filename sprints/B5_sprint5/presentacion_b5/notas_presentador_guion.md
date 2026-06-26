# Notas del presentador — deck B5 (guion hablado, fuente versionada)

> **Qué es:** la fuente CANÓNICA y versionada de las notas del presentador del deck B5,
> en el formato VIGENTE (guion HABLADO corrido — ver `convenciones_deck_b5.md` §3.b y la
> memoria [[notas-presentador-guion-didactico]]). Ernesto edita las notas en OnlyOffice;
> este archivo es la copia durable (el `.pptx` está gitignored y el motor `set_notes` del
> generador aún emite el formato por-fases LEGACY → NO regenerar el deck para "actualizar notas").
>
> **Estado:** slides 1–6 FINALIZADAS y aprobadas (sesión 25-jun). Slides 7–21 pendientes
> (se construyen en la próxima sesión, mismo estilo, una por una).
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

En el tope entran los parches de la slide, el tensor z de N por 512. El primer bloque, la proyección a query, aplica q igual a la normalización de W_q por z, y lleva cada parche de 512 a 256 dimensiones: ese query de 256 está organizado en 16 cabezas de 16, es decir, el mismo parche mirado por 16 criterios en paralelo.

El segundo bloque es el ruteo por slots, la ecuación 3 del paper y el corazón de MAMMOTH. Acá se materializa la idea de los fenotipos que vimos antes: una lámina mezcla parches de tejidos muy distintos —tumor, estroma, alvéolos— y a cada uno de esos fenotipos conviene tratarlo por separado. Para eso están los 300 slots: cada slot tiene un vector aprendido —su prototipo— que con el entrenamiento termina representando un fenotipo, una morfología concreta. Lo que hace el ruteo es agrupar en cada slot los parches de su fenotipo.

No es que cada parche se asigne a un slot; es al revés: cada slot recoge una contribución de todos los N parches a la vez, y esto se hace por separado —en paralelo— para los 300 slots, cada uno con su propio reparto de pesos. La fórmula es u igual a la suma, sobre los N parches, de D por q: el slot es el promedio de los queries de todos los parches, cada uno pesado por un coeficiente D. Ese peso se obtiene comparando el prototipo del slot con el query de cada parche mediante un producto interno —un puntaje de parecido—, que una softmax sobre los N parches normaliza para que sumen uno. De este modo, un parche muy parecido al prototipo pesa mucho y uno distinto casi nada: cada slot termina siendo un resumen de toda la lámina, sesgado hacia los parches afines a su prototipo. Los 300 slots son esos resúmenes, fijos y ordenados, que reemplazan a los N parches sueltos y de número variable.

Esos 300 slots se reparten entre 30 expertos, 10 cada uno, y cada experto aplica a sus slots una transformación propia —la especialización por fenotipo que buscábamos—. Esa transformación, o igual a u por A por B, es un LoRA de bajo rango: la matriz A baja de 16 a 8 dimensiones y es compartida, la matriz B sube de 8 a 32 y es propia de cada experto, con el rango 8 ajustado automáticamente para no sumar parámetros. Después, el bloque de combinación vuelve a armar los parches con la fórmula h igual a la suma sobre los slots de C por o, donde una segunda softmax, C, reparte sobre los 300 slots. Las dos softmax se diferencian por su eje: la primera reparte sobre los N parches para construir los slots; la segunda, sobre los 300 slots para reconstruir cada parche.

Lo importante: entra un tensor de N por 512 y sale otro de N por 512, así que es un reemplazo transparente de la capa lineal, y como el rango se ajusta solo pesa casi lo mismo —es el banner "mismo presupuesto"—. Por eso, si MAMMOTH no mejora, no será por falta de capacidad. Veamos ahora esto mismo sobre la figura oficial del paper, con las dimensiones reales.

---

## Slides 7–21 — PENDIENTES

Se construyen en la próxima sesión, una por una, en el mismo formato hablado. Orden:
7 (figura oficial fused) · 8 (variante keep_slots fused) · 9 (resultados drop-in 8 tareas) ·
10 (invasión linfovascular) · 11 (resultados keep_slots 4 tareas) · 12 (div PathPT) ·
13 (idea/figura paper) · 14 (arquitectura forward) · 15 (necrosis) · 16 (tasa mitótica) ·
17 (microcalc go/no-go) · 18 (div cierre) · 19 (3 ejes 0 palancas) · 20 (CLAM + loss) ·
21 (próximos pasos).
