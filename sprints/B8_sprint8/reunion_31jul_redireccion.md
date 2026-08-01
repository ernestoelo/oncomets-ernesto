# Reunión con Sebastián: se descarta SI-MIL y el sprint gira hacia mitosis y grado nuclear

> Registrado el **31-jul-2026** con lo que transmitió Ernesto al volver de la reunión.
> ⚠ **La fecha exacta de la reunión está sin confirmar en este documento.** El calendario
> del repo tenía anotada una reunión para el **viernes 07/08/2026**, con el deck de SI-MIL
> ya construido para ella. Si esta conversación fue esa reunión adelantada, o una distinta,
> corregir acá y en `progress/current.md`.

## 1. Lo que se decidió

**SI-MIL no se implementa.** El argumento fue que lo que se gana es interpretabilidad a
costa de empeorar levemente la métrica, y lo que se busca con Sebastián es **mejorar la
métrica**.

La decisión coincide con lo que el estudio del paper ya había medido, así que no hay
sorpresa que registrar: en la celda que nos corresponde, con CLAM de base, su Tabla 2 baja
de **0.937 a 0.925** en accuracy y de **0.972 a 0.957** en AUC
([`simil_estudio.md`](simil_estudio.md)). El deck del B8 ya lo decía en esos términos y
nunca lo presentó como mejora de rendimiento.

**HoVer-Net y las 246 features queda descartado por ahora, por costo.** Sebastián lo corrió
él mismo y midió **3.3 h por lámina**, que es lo que nosotros habíamos medido leyendo sus
logs (3 h 36 min en el job 4714, [[hovernet-ya-corriendo-sgaete]]). O sea que el número
llega por dos vías independientes y no está en discusión.

**Lo que sí se conserva de esa línea:** la idea, que propuso el propio Sebastián, de correrlo
solo sobre los **20 mejores parches que CLAM selecciona** en vez de sobre la lámina completa.
Es la misma asimetría que habíamos anotado (SI-MIL corre sobre todo porque entrena su rama;
nosotros solo queremos leer lo que el modelo ya destacó). **Queda pendiente para cuando haya
más GPU**, no descartada.

## 2. El encargo nuevo

Dos cosas, las dos de Sebastián:

1. **Seguir probando configuraciones de hiperparámetros de Mammoth con CLAM.** Es el encargo
   3 de la reunión del 24-jul, que ya estaba enunciado y sigue **sin pre-registro escrito**.
   Ahora queda confirmado como prioridad y no como opción.
2. **Investigar variantes o modelos como ramas aparte de CLAM**, dedicados por completo a una
   tarea específica: **mitosis** o **grado nuclear**, tareas que dependen de una geometría
   particular. Con el etiquetado del patólogo y lectura del área, la idea es construir
   representaciones específicas para esas tareas.

El argumento técnico, las medidas que lo sostienen y las cuatro familias de respuesta están
en [`tareas_geometricas/README.md`](tareas_geometricas/README.md). No se escribió una línea
de modelo: regla 9, primero el argumento.

## 3. De dónde salió el encargo: el patólogo

Ernesto está trabajando con un patólogo, que le mostró la lámina en una herramienta donde se
ven los puntos marcados de distinto color según el tipo de lesión y las zonas de tumor
encerradas, y compartió esas etiquetas con él. Tres cosas que dijo el patólogo, y que son
las que dan forma al encargo:

- **Mitosis**: los núcleos son muy particulares y aparecen dispersos en zonas distintas de la
  lámina; son detalles tan finos que a CLAM y a Mammoth se les escapan, porque quizá esos
  parches no reciben atención suficiente y otros embeddings se los comen.
- **Grado nuclear**: lo que se ve es que hay núcleos **más grandes de lo normal comparados
  con su vecindario**.
- **Sobre cómo anota**: el cáncer cubre toda la zona, pero él **solo marca donde se evidencia
  con mayor exactitud**; después el modelo del software identifica dónde se propaga en menor
  medida.

La tercera es la más importante para nosotros y la más fácil de pasar por alto: las
anotaciones son **positivos parciales**, no una segmentación. Lo no marcado no es negativo.
Está desarrollado en [`anotaciones_patologo/hallazgos.md`](anotaciones_patologo/hallazgos.md)
§3.

## 4. Lo que esta sesión verificó, y que no era obvio

La herramienta es **QuPath**, y el archivo que exportó es el mismo geojson que la sesión
paralela había encontrado el 31-jul en el directorio de HoVer-Net de `sgaete` y anotado como
autoría desconocida. **El pendiente «quién anotó la lámina» queda resuelto en lo esencial:**
es la anotación del patólogo. Sigue sin confirmarse el nombre detrás de «GDT» y si hay más
láminas anotadas.

Y algo que había que cazar antes de que alguien construyera encima: **el geojson no está en
las coordenadas de openslide**. Superpuesto tal cual, **0 de las 26 marcas de mitosis** caen
sobre un parche extraído. Con el desplazamiento correcto, `dx = 3829` (que se deriva de las
propiedades del propio `.bif`) y `dy = 0`, caen **58 de 61**, y las 3 que no son fondo y
grasa. El detalle, los tres criterios con que se estimó y el script reproducible están en
[`anotaciones_patologo/hallazgos.md`](anotaciones_patologo/hallazgos.md) §2.

## 5. Qué cambia en el estado del sprint

| Encargo del 24-jul | Estado |
|---|---|
| 1. Escalar el N_eff de slots | **Cerrado** el 27-jul (1858 láminas-fold) |
| 2. «Entrenar los slots» | Sigue con la premisa sin aclarar; no se tocó |
| 3. Grid de E y S | **Prioridad confirmada.** Falta pre-registro y `reviewer` |
| 4. Papers | **Cerrado con decisión**: SI-MIL no se implementa; HoVer-Net en pausa por costo |
| (nuevo) 5. Ramas por tarea: mitosis y grado nuclear | Abierto, argumento escrito, sin código |

Lo que **no** cambia: los Hallazgos 11 a 14 siguen cerrados. Ninguna de las dos líneas nuevas
es una reapertura del eje de arquitectura. La rama por tarea ataca **qué entra al agregador**,
que es justamente lo que esos cuatro ejes dejaron señalado como cuello.

## 6. Preguntas abiertas

- **La fecha de la reunión del 07/08 y qué pasa con el deck de SI-MIL de 14 láminas**, que
  está construido y aprobado. Si la discusión del paper ya ocurrió, hay que decidir si el
  deck se presenta igual como registro de lo estudiado y de por qué no se implementa, o si se
  reemplaza por el material de la línea nueva.
- **Quién es «GDT»**, si hay más láminas anotadas y con qué criterio se eligieron las clases.
- **Cuántas láminas anotadas se podrían conseguir**, que es lo que decide si la familia D
  (detector dedicado) es viable o teórica.
- **Del encargo 2 sigue sin respuesta** qué quiso decir con entrenar los slots, dado que ya
  se entrenan con nuestro dataset.
