# Deck del período B9 — `[20260907] [Ernesto Gamero] [Detección Nuclear].pptx`

Primer deck sobre la **plantilla oficial nueva** (`docs/plantilla_oficial.md`), la que
Ernesto fijó el 25-ago y que supersede a Deep-LLM-V. Registro **executive deck**, no deck
técnico de sprint.

| | |
|---|---|
| Fuente de verdad | `generate_b9_deck.py` (el `.pptx` es derivado y está gitignored, `.gitignore:55`) |
| Guion | `guion_b9.md`, que el generador **lee** y aplica con `notes()`. El `.md` es la fuente; las notas del `.pptx` son derivadas |
| Figuras | `assets/mitosis_{aciertos,falladas}.png`, que produce `scripts/galeria_mitosis_12.py`. Las cuatro de los ejes nucleares son **nativas** y las dibuja el propio generador |
| Molde | `papers/presentations/[AAAAMMDD] [Nombre Apellido] [Image-to-text].pptx`, **read-only** |
| Salida | **13 láminas** desde el 3-sep (sesión 47), 13,333 × 7,5, Barlow embebida. Las cinco nuevas están escritas y el deck compila limpio; lo que falta es el pase de `@humanizer-es` y dos figuras a regenerar (§Estado al 3-sep, sesión 47) |

## Regenerar

```bash
cd sprints/B9_sprint9/presentacion_b9
PYTHONPATH=/media/administrador/Storage1/sdonoso/clam_testing2/.pylibs \
  /home/sdonoso/miniconda3/envs/pruebas/bin/python generate_b9_deck.py
```

Sale con código 1 si la auditoría o el barrido de estilo tienen avisos. Hoy salen los dos
limpios. Las dos figuras de recortes **no** se regeneran desde acá: si cambia el cruce, primero
`scripts/galeria_mitosis_12.py` y después el deck.

> **El intérprete es `envs/pruebas`, no `clam_latest`** (cambió el 28-ago, al incorporar las
> cuatro figuras de los ejes nucleares). El deck pasa a depender de `zarr`, que
> `b9_pleomorfismo` importa al tope y de donde salen `spearman` y `permutacion_exacta`, y
> `clam_latest` no lo tiene. `envs/pruebas` con el mismo `PYTHONPATH` importa **pptx 1.0.2,
> lxml, PIL, pandas, numpy, zarr y scipy** en un solo proceso y abre los TTF de Barlow.

## Las decisiones de Ernesto

| | |
|---|---|
| Idioma | **todo en español**, decidido el 27-ago. Antes eran láminas en inglés con guion en español |
| Proyecto (3er corchete y cejilla) | **Detección Nuclear**. NO `Mitosis Detection`: ése es el rótulo con el que `sgaete` presenta su YOLOv11-m, y es literalmente el ejemplo que trae la plantilla |
| Período del título | **25/08/2026 - 08/09/2026** |
| Láminas de contenido | **cuatro**: el número, los aciertos, las falladas y los ocho ejes |
| Portada | queda **en inglés y tal cual**: es copy de la empresa, no contenido nuestro |
| Los dos ejes nucleares (28-ago) | las **cuatro figuras entran al cuerpo**, entre los recortes de mitosis y la lámina de ejes. El deck quedó en **once láminas**. Ejecutado el 28-ago: ver abajo |

Lo que **no** se traduce, a propósito: los nombres de clase del patólogo (`Mitosis`,
`Tumour`, `Stroma`, `AreaTubular`, `Comedonecrosis`…). Son las etiquetas literales de su
geojson, con sus mayúsculas y su mezcla de idiomas, y traducirlas rompe el vínculo con el
material. La lámina de los ejes lo dice y el guion lo aclara al pasar.

## Estructura

```
s01  portada                                    TAL CUAL, copy de la empresa. Sólo se le pone guion
s02  OBJETIVOS 25/08/2026 - 07/09/2026          tabla 4x4 (se quitó la 4ª fila de cuerpo)
s03  Mitosis: 26 de 94 marcas del patólogo      cuerpo + figura NATIVA de 12 barras
s04  Las 26 marcas que el detector reencuentra  cuerpo + leyenda nativa + lámina de contacto
s05  Las 68 marcas que se escapan               cuerpo + leyenda nativa + lámina de contacto
s06  El control positivo separa epitelio…       cuerpo + 8 barras de rango intercuartil NATIVAS
s07  Los tres grados ordenan sobre diez…        cuerpo + strip de 10 puntos + tabla NATIVA 11x5
s08  Tareas del próximo período                 tabla 4x3 con DOS filas de cuerpo (`min_h=1.14`)
```

**Cambió el 2-sep**: salieron las dos láminas de nulo y la tabla de los ocho ejes (§1 de la
revisión). **Ese bloque de ocho quedó atrás el 3-sep**: el orden vigente es el de trece, y está
en §«Estado al 3-sep-2026 (sesión 47)». Se conserva acá porque es el estado contra el que se
escribió el plan de las cinco láminas.

## Las dos láminas de recortes (s04 y s05)

Ernesto las pidió el 27-ago: ver **las mitosis que detecta HoVer-NeXt contra las que etiquetó
el patólogo**, y eligió partirlas en aciertos y falladas en vez de agrupar por lámina.

`scripts/galeria_mitosis_12.py` **no re-mide nada**: el emparejamiento húngaro uno a uno con
corte a 30 µm ya está resuelto en `results/b9_cruce_94/pares_<slide>.csv`, con el offset del
geojson aplicado, así que sólo recorta y dibuja. Si el cruce cambia, las figuras cambian
solas. Aborta si no cuenta 94 marcas y 26 aciertos.

- Recorte de **128 px de nivel 0 = 59,5 µm** de lado, centrado en la marca.
- Anillo **blanco** = marca del patólogo. Anillo **amarillo** = detección que la acredita.
  Son los mismos colores de la galería de la 129741 del B8.
- Agrupados por lámina y en el orden del deck. El rótulo va **una vez por grupo**, con su
  `n`, y una banda superior que alterna entre los dos azules marca dónde empieza cada grupo:
  repetir `129741` trece veces no informa nada.
- **No se dibuja ninguna detección que no acredite una marca.** No hay cómo distinguirla de
  una mitosis real sin marcar, así que llamarla falso positivo sería inventar.

Las figuras van como **imagen** y no como shapes porque son la fotografía de un resultado,
que es la excepción declarada en CLAUDE.md §"Formato de entregables". Todo lo que las
acompaña (título, cuerpo, leyenda y pie) es nativo. La leyenda dibuja el anillo sobre un
cuadradito del rosa del tejido: un anillo blanco sobre el fondo blanco de la lámina sería
invisible.

## El método: rellenar en sitio

Es lo contrario de los seis decks anteriores, que abrían el template y le **borraban** las
láminas (`base_from_template()` de `generate_b8_deck.py:341`). Acá se rellena, porque las
tablas de s02 y s07 traen las filas de cuerpo vacías **pero ya estilizadas** y reproducir eso
a mano es trabajo perdido. Las tres maniobras sin API en python-pptx están en
`docs/plantilla_oficial.md` §7.a e implementadas en `clonar_s03`, `_quitar_fila` / `_alto_fila`
y `reordenar`. La lámina de contenido del molde se clona **ocho** veces.

Sigue en pie el motivo de siempre para abrir el `.pptx` en vez de usar `Presentation()`: la
plantilla **embebe Barlow** ([[deck-template-fuentes-embebidas]]). Y sigue haciendo falta
`forzar_barlow()`, porque el `fontScheme` del theme de ESTA plantilla también es Arial.

## Los números salen leídos, no transcritos

`leer_datos()` arma la lámina de mitosis desde `results/b9_cruce_94/por_lamina.csv` y
`recall_por_tolerancia_agregado.csv`: el título, los tres puntos del cuerpo, las doce barras y
el tramo plano de la escalera. Los títulos de s04 y s05 también salen de ahí (`26` y `94−26`).
Si el CSV cambia, el deck cambia solo. Además **verifica** que el agregado y el por-lámina
coincidan, y **aborta** si no.

`datos_eje4()` y `datos_eje3()` hacen lo mismo con las cuatro láminas de los ejes nucleares,
sobre `results/b9_nucleos/{regiones_epi_estroma.csv,regiones_nulo.npy,marcas_grado.csv}`, y con
una vuelta de tuerca: no re-implementan el estadístico, **importan el del script que produjo el
número** (`rank_auc` de `scripts/b9_epitelio_estroma.py`; `spearman` y `permutacion_exacta` de
`scripts/b9_pleomorfismo.py`). Los dos imports viven **dentro** de esas funciones y no al tope,
para que abrir el módulo no exija `zarr`.

## La revisión de Ernesto, 1-sep-2026 — DECIDIDA y sin ejecutar

Es la primera vez que Ernesto mira el deck armado. Devolvió cuatro cosas y **ninguna está
aplicada todavía**: el plan lo ejecuta una sesión limpia. El deck en disco sigue siendo el de
once láminas del 28-ago.

| # | Lámina | Qué devolvió | Qué se decidió |
|---|---|---|---|
| 1 | s03 | «no entiendo a qué te referís con 30 µm»; «¿qué número? ¿qué significa plano?»; «¿trabajamos en diferentes resoluciones o es la mitosis de diferentes tamaños?» | Nombrar la **tolerancia de emparejamiento** con su sustantivo, decir que las doce están a la misma resolución, y explicar «plano» como «no depende del corte» ([[parametro-necesita-su-semantica]]) |
| 2 | s03 | «"el caso de referencia…" eliminalo todo» | Sale **sólo de la lámina**. El guion conserva el párrafo del sesgo heredado |
| 3 | s06 | «está genial pero no la entiendo» | El **eje horizontal no tiene rótulo**. Se agrega, y el guion explica desde cero qué es un control positivo, qué es una región y qué es la fracción epitelial |
| 4 | s07-s09 | «no entiendo nada, ¿de qué traslación estás hablando?»; «que sean más pedagógicas, especialmente las notas»; títulos «más profesionales, precisos y minimalistas» | Títulos nuevos del juego **objeto medido**, dos rótulos de «cómo se lee», y el guion de las cuatro reescrito de cero |
| 5 | — | «¿se le pasaron los parches con más atención seleccionados con CLAM a HoVer-NeXt?» | **No**: la WSI entera en las doce. Se dice en el pie de s03, y se abre el eje de medir la atención sobre las doce, con **dos láminas nuevas** |

### Los títulos nuevos

Medidos con `text_w()` del propio generador; los tres entran en una línea a 40 pt en 12,44".

| | hoy | nuevo | ancho |
|---|---|---|---|
| s07 | Ninguna traslación del nulo llega al observado | **El azar no separa epitelio de estroma** | 9,02" |
| s08 | Los tres grados ordenan sobre diez láminas | **El tamaño nuclear ordena los tres grados** | 10,01" |
| s09 | El nulo exacto, y la población que no despega | **Las dos poblaciones contra el mismo azar** | 10,23" |

### Lo que esto le enseñó al QA

Las cuatro capas de abajo estaban **las cuatro en verde** cuando salieron estas cuatro fallas.
No es que hayan fallado: miden **defectos**, y un lector que no entiende es una **ausencia**.
El caso más limpio es el eje sin rótulo de s06, que pasó las cuatro. Detalle en el ADDENDUM
1-sep de [[deck-qa-puntos-ciegos-chequeo]]. Consecuencia operativa: **«el deck está terminado»
no es una conclusión que el QA pueda emitir**, y cerrarlo antes de que el destinatario lo lea
hace que su primera lectura llegue como reapertura.

## QA — las cuatro capas ([[deck-qa-puntos-ciegos-chequeo]])

1. **Round-trip estructural**: reabierto con python-pptx. 11 láminas en orden, cada una con
   cejilla y título, OBJETIVOS con 3 filas de cuerpo y Tareas con **2**, las dos tablas nativas
   (8 ejes y 10 láminas), las dos imágenes y notas en las once. `auditar` sin avisos.
2. **Medición de texto real** con los TTF de Barlow bajo containment: ninguna caja que
   desborde, ninguna celda que corte, ningún cuerpo bajo los 7 pt del template.
3. **Rasterizado y lectura visual**: LibreOffice con `FONTCONFIG_FILE` del workspace, las
   once láminas miradas una por una. Hecho **temprano** ([[image-api-qa-limit]]). Es la capa que
   encontró los tres defectos de geometría de s06 a s09, y **ninguno de los tres** disparó un
   aviso de `auditar`.
4. **Cruce de contenido contra las fuentes**: cada número contra `por_lamina.csv`,
   `recall_por_tolerancia_agregado.csv`, `cruce_94.md` §1-§2 e `inventario_tareas.md` §1 y §4.
   26 + 68 = 94 verificado sobre los doce `pares_*.csv`, y las cinco láminas que acreditan
   alguna marca contadas sobre el mismo archivo. Para las cuatro nuevas, cada número dibujado
   contra `numeros_figuras.csv` y `../ejes_nucleares/resultados.md` §1-§2 (AUC 0,906 · nulo
   0,439 · p97,5 0,528 · ρ +0,809 · p 0,0056 sobre 360 · completa +0,552 y 0,0673 sobre 2970 ·
   75,1 / 92,1 / 98,9), más que 26 / 68 / 94 no se movió.

Más los dos de estilo: `unzip` y contar `typeface` (1456 `Barlow`; los `Arial` que quedan son
entradas `<a:font script="Arab|Viet|Hebr">` del theme y `tableStyles.xml`, que no gobiernan
texto latino) y `ppt/fonts/*.fntdata` sigue en el paquete con las cuatro variantes · barrido
de «—», «–» y «palanca» **saltando s01**, cuyo titular trae un «—» que es copy de la empresa.

## Lo que encontró el QA de la versión en español

1. **El generador y el auditor medían distinto el mismo párrafo, y con el inglés nunca se
   notó.** Los puntos del cuerpo son «arranque en bold + resto normal»: `set_cuerpo` los medía
   enteros como normales (subestima) y `auditar` enteros como bold (sobreestima). Con el texto
   más largo del español la diferencia llegó a cambiar el número de líneas y salió como un
   aviso de 0,44" que no era del texto sino del desacuerdo. `wrap_lines_mixto()` mide **cada
   tramo con su peso** y ahora los dos usan la misma función.
2. **Hay dos `68` en el deck y coinciden por casualidad.** En s03, `13 de sus 68 marcas` son
   las de las otras once láminas (94 − 26 marcas de la 129741); en s05, `68` son las marcas
   sin detección (94 − 26 aciertos). Coinciden porque la 129741 tiene exactamente tantas
   marcas como aciertos hay en total. Las dos láminas **nombran su denominador** para que
   nadie lea una como continuación de la otra ([[techo-filtro-antes-de-correr]] sobre no
   mezclar unidades).
3. **`%.1f` escribe punto decimal.** La misma lámina decía «7,5 a 50 µm» en la tabla y «7.5»
   en el cuerpo. `num()` formatea con coma; el auditor no ve esto, se ve mirando.
4. **`reencontradas de marcas` no entra donde entraba `recovered of marks`.** El rótulo de la
   columna de números de las doce barras pasó a `reencontradas`, y la columna de 1,18" a 1,30".

## Discrepancia declarada: el handoff de la sesión 29 decía 6 láminas

Se construyeron **cinco** el 26-ago, porque la aritmética de ese handoff daba cinco y no había
contenido especificado para una sexta. El 27-ago Ernesto pidió las dos láminas de recortes y
el deck quedó en **siete**, y el 28-ago, con las cuatro figuras de los ejes nucleares, en
**once**. La discrepancia original no se resolvió: quedó superada.

## Lo que este deck NO dice, a propósito

- El 27,7 % **no es el recall de HoVer-NeXt**: el denominador son **las marcadas**.
- **No** se llama falso positivo a ninguna detección sin marca, ni se calcula precisión, F1 o
  PQ. Contra positivos parciales no son computables, y decirlo es parte del resultado. Por eso
  la lámina de aciertos muestra 26 recortes y no las 732 detecciones.
- El **13 de 26** de la 129741 **no** se presenta como el resultado: era el mejor caso de doce,
  y la lámina lo dice en su segundo punto.
- **No** se mezclan unidades: marcas (26 / 68 / 94 · 107), regiones (209), láminas (10 · 12),
  asignaciones (360 · 2970), detecciones (732), polígonos (472). Cada figura declara la suya.
- Los tres NO-GO son **por argumento**, no por presupuesto.
- El `p` = 0,0056 del grado nuclear **no es holgura contra el 0,05**: es el piso que ese diseño
  puede dar, alcanzado. Y el 0,0050 del control positivo es el piso de 200 traslaciones. Las dos
  láminas lo dicen en su pie.
- El ordenamiento de los tres grados **no valida Nottingham**, y su `n` honesto son **10 láminas**
  y no las 85 marcas: el grado está confundido con la lámina sin un solo cruce.
- **No** se cita ningún AUC por lámina de la población restringida: valen 1,000 con `n` = 1 de un
  lado. Y **no** se presenta el área cruda como el resultado: el primario es el percentil.

## Las cuatro láminas de los ejes nucleares (s06 a s09)

Ernesto decidió el **28-ago** que **las cuatro entran al cuerpo**, entre los recortes de mitosis
y la lámina de ejes, y el deck quedó en **once láminas**. Nacieron como una hoja suelta en
[`../ejes_nucleares/figuras/`](../ejes_nucleares/figuras/); al incorporarlas **la dependencia se
invirtió**: las láminas y sus primitivas viven ahora en `generate_b9_deck.py`, y la hoja quedó
como envoltorio delgado que las arma solas para iterar el QA visual sin reconstruir el deck. Al
revés habría sido un ciclo, y correr el deck como `__main__` habría cargado una segunda copia de
su propio módulo.

| Lámina | Qué muestra | Unidad |
|---|---|---|
| s06 | La fracción epitelial por clase del patólogo: rango intercuartil y mediana, epitelio contra estroma | **región** (209) |
| s07 | El AUC observado contra las 200 traslaciones de su nulo, con la media y el p97,5 marcados | **región** (209) |
| s08 | Los tres grados sobre diez láminas, un punto por lámina, más la tabla de dónde sale cada punto | **lámina** (10) |
| s09 | Los dos nulos exactos, restringida y completa, con el ρ observado marcado sobre cada uno | **asignación** (360 y 2970) |

**Cada figura declara su unidad en el pie**, que en este deck no es decorativo: conviven marcas
(26 / 68 / 94 · 107), regiones (209), láminas (10 · 12) y asignaciones (360 · 2970) en láminas
contiguas, y dos de esos números coinciden por casualidad
([[dos-numeros-iguales-denominador-distinto]]).

Los números **no se transcriben**: `datos_eje4()` y `datos_eje3()` leen los CSV de
`results/b9_nucleos/` y recalculan con `rank_auc`, `spearman` y `permutacion_exacta` **del propio
script de cada eje**, así que «la figura muestra otra cosa que la tabla» no es representable
([[hallazgo-necesita-forma-presentable]]). Los 48 que quedan dibujados se escriben a
`../ejes_nucleares/figuras/numeros_figuras.csv`, versionado; **lo escribe el deck y sólo el
deck**, que es la única fuente.

Van **nativas** y no como PNG: son objetos dibujables (barras, puntos, histogramas, ejes), que es
el criterio del ADDENDUM B5 de `CLAUDE.md`. La excepción de imagen es sólo para s04 y s05, que
son la fotografía de un resultado.

Con esto **tres tablas dejaron de contradecir al deck** y se actualizaron en el mismo movimiento:

| Tabla | Qué cambió |
|---|---|
| OBJETIVOS (s02) | la fila de métricas nuevas pasó de «En curso» a **Cerrado** y nombra los dos ejes medidos |
| Los ocho ejes (s10) | «Grado nuclear» y «Tumor y estroma» pasaron de «CPU, en disco / GO» a **medidos**, con la forma de la fila de Mitosis; y el punto de cuerpo dejó de decir que son trabajo por hacer |
| Tareas (s11) | perdió la fila de los dos ejes de procesador y **quedó con dos**, sin reemplazo |

### Lo que el QA visual encontró acá

1. **La leyenda de s08 estaba a 0,08" de la nube de `alto`, alineada con ella.** No se cruzaban,
   así que ni `auditar` ni un chequeo de intersecciones lo veían: el defecto era la **proximidad**,
   no el solape, y sólo se ve mirando. Causa de fondo: los puntos de `alto` viven en el percentil
   95 a 100 **por construcción**, o sea que el borde superior del panel es la única banda que está
   ocupada siempre, y ahí es donde estaba puesta la leyenda. Ahora va **dentro del panel y abajo**,
   apoyada bajo el punto más bajo que haya, medido y no supuesto.
2. **En s09 las etiquetas del eje del panel de arriba entraban 0,05" en la caja del rótulo del de
   abajo.** El histograma cede 0,14" de alto a cambio.
3. **Las cajas de la leyenda de s06 medían 1,7" para 0,9" de texto** y se cruzaban entre sí sin que
   se cruzara la tinta. Pasan a medir lo que mide su texto: una caja de más no se ve, pero llena de
   falsos positivos cualquier chequeo de intersecciones y lo vuelve inservible.

El `.pptx` viejo en inglés, `[20260908] [Ernesto Gamero] [Nuclear Detection].pptx`, **se borró**
el 28-ago por decisión de Ernesto. Era derivado y gitignored: se regenera cambiando `PROYECTO`.

## La reunión del 1-sep-2026 — el deck se presentó, y vuelve con seis pedidos

El deck de once láminas **se presentó**. Lo que sigue es lo que Ernesto trajo de vuelta, decidido y
**sin ejecutar**: lo toma una sesión limpia. **Supersede la sección anterior** en un punto: las
láminas 7 y 9 ya no se re-titulan ni se hacen más pedagógicas, **se borran**. El resto de esa
sección (los 30 µm de la lámina 3, el rótulo que le falta al eje de la 6) **sigue vigente entero**.

**La próxima reunión es el lunes 07/09**, no el 08/09. Por defecto el archivo pasa a
`[20260907] …` y la tabla OBJETIVOS cierra el período el 07/09; si Ernesto prefiere conservar el
período declarado, cambia sólo el nombre del archivo.

### 1. Borrar tres láminas

| # | var | función | título |
|---|---|---|---|
| 7 | `sF` | `lamina_f2` | Ninguna traslación del nulo llega al observado |
| 9 | `sH` | `lamina_f4` | El nulo exacto, y la población que no despega |
| 10 | `sD` | `lamina_ejes` | HoVer-NeXt: qué se puede medir y qué no |

Son las dos láminas de nulo y la tabla de los ocho ejes. **Se sacan de la lista de `reordenar()`**,
no se borra su código: `lamina_f2` y `lamina_f4` las **importa**
`../ejes_nucleares/figuras/generate_figuras_ejes34.py`, que es el envoltorio de QA visual de las
cuatro figuras, y borrarlas lo rompe. `lamina_ejes` sí se puede borrar entera.

> **Lo que se pierde y hay que saber que se pierde:** con la lámina 10 sale del deck el único lugar
> donde vivía el **argumento de los tres NO-GO** (permeaciones, microcalcificaciones,
> arquitectura). Queda sólo en `../hovernext_tareas/inventario_tareas.md` §4.

### 2. Lo que entra

Seis pedidos, tres de ellos láminas nuevas de imagen:

| pedido | forma |
|---|---|
| Cruzar la **atención de CLAM** con HoVer-NeXt: ¿mejora el conteo de mitosis? | dos láminas — los doce mapas (imagen) y la **escalera de área** (nativa) |
| ¿Qué **tamaño de parche** toma HoVer-NeXt? (lo preguntó Sebastián) | va en la lámina introductoria |
| Una lámina de **cómo funciona HoVer-NeXt**, con el diagrama del paper y las dimensiones | figura del paper (descarga autorizada) + tira nativa |
| Para el **grado nuclear**, ver los núcleos de cada lámina y su tamaño relativo | galería, imagen |
| Para el **núcleo epitelial**, ver regiones comparadas | galería, imagen |
| La **zona de ~3 mm²** para contar mitosis, como objetivo propuesto del próximo sprint | fila en la lámina de tareas |

El deck queda en **trece láminas**. El orden y los detalles de cada una están en el plan de la
sesión 39; los insumos verificados, en
[`../atencion_12_laminas/insumos_json_out.md`](../atencion_12_laminas/insumos_json_out.md).

### 3. La restricción que cambia cómo se dibuja la lámina del cruce

**Filtrar por atención no puede subir el número de mitosis encontradas.** HoVer-NeXt ya corrió
sobre la lámina entera en las doce, así que «HoVer-NeXt + CLAM» es un **subconjunto** de las 732
detecciones y de las 26 marcas acreditadas. Lo que la restricción compra es **área**: por eso la
lámina es una **escalera de presupuesto en mm²** con el brazo sin filtro como control, y no un
top-K ([[techo-filtro-antes-de-correr]], [[carga-fija-no-k-fijo]]). Prometer una mejora de conteo
sería prometer algo que la aritmética no permite.


---

## Estado al 2-sep-2026 — ejecutada la mitad de la revisión

Lo que la sesión 40 **sí** dejó hecho del plan del 07/09:

| # | qué | estado |
|---|---|---|
| 1 | **Borrar las tres láminas** | **hecho**. `lamina_f2` y `lamina_f4` siguen definidas (las importa `../ejes_nucleares/figuras/generate_figuras_ejes34.py`); `lamina_ejes` se borró entera |
| 2 | **Renombrar a `[20260907]`** y cerrar el período el 07/09 | **hecho**, confirmado por Ernesto |
| 3 | **La lámina de mitosis** (§A.2 del plan) | **hecho**: la tolerancia nombrada como distancia de emparejamiento, fuera el punto del caso de referencia (queda en el guion), pie de cuatro líneas |
| 4 | **El rótulo del eje** del control positivo (§A.3) | **hecho**, con `h_eje` de 0,25 a 0,52 para que no se monte sobre el pie |
| 5 | **La figura del paper de HoVer-NeXt** (§C.1) | **hecho**: `papers/presentations/assets_branding/paper_figs/hovernext_fig1_pipeline.png`, paneles A-B-C |
| 6 | **El mosaico de atención de las doce** (§C.2) | **hecho**: `assets/atencion_12_laminas.png`, 2590×870, grilla 6×2 |

**Lo que falta, y es la mayor parte:** las **cinco láminas nuevas** (HoVer-NeXt, la atención, la
escalera de área, las regiones epiteliales, los núcleos del grado), la **escalera de área** que
las alimenta, las **dos galerías** que faltan renderizar, el **guion** de las cinco y el pase por
`@humanizer-es`.

---

## Estado al 2-sep-2026 (sesión 42) — los INSUMOS de las cinco láminas están todos

El deck sigue en **ocho** láminas: la sesión 42 no lo tocó. Lo que sí hizo fue dejar medido y
renderizado **todo lo que las cinco láminas nuevas necesitan**, que era el bloqueo real.

| lámina nueva | insumo | estado |
|---|---|---|
| 3 · Cómo funciona HoVer-NeXt | `paper_figs/hovernext_fig1_pipeline.png` (2332×1476) | **listo** desde la sesión 40 |
| 7 · La atención sobre las doce | `assets/atencion_12_laminas.png` (2590×870) + los **tres brazos** de `results/b9_atencion_12/` | **listo** |
| 8 · La escalera de área | `results/b9_escalera_area/agregado.csv` | **listo**, y con los trece chequeos en verde |
| 10 · Una región epitelial y una de estroma | `assets/regiones_epi.png` (2300×648) | **listo**, script nuevo |
| 12 · Los núcleos marcados | `assets/nucleos_grado.png` (1600×3300) | **renderizado, pero ver el aviso de abajo** |

### El aviso: `nucleos_grado.png` NO entra en una lámina apaisada tal como está

Su aspecto es **0,48** (alto, doce filas apiladas) y la caja de figura del molde es apaisada:
escalado a lo alto quedaría de unas **2,2 pulgadas de ancho** y sería ilegible. **Hay que
rehacer su composición antes de insertarlo**, y la vía barata es un layout de **dos columnas de
seis filas**: ancho por columna 1600, con dos da 3240×1658 y aspecto **1,95**, que sí entra. No se
hizo en esta sesión.

> **RESUELTO el 3-sep (sesión 44):** `hoja()` ya recibe `n_col` (default 2, más el flag
> `--n-col`) y el PNG nuevo sale **3240 × 1668**, aspecto **1,94**, con las doce filas. El
> tamaño que el plan mandaba verificar, 3240 × 1658, estaba mal por diez píxeles: su propia
> fórmula da `10 + 6·272 + 26 = 1668`.
>
> **Corrección del 2-sep (sesión 43):** `hoja()` de `scripts/b9_galeria_nucleos_grado.py`
> **no tiene** el parámetro `n_col` que esta sección daba por existente (lo verificó la sesión 43
> leyendo la función, línea 110). Hay que **agregarlo**, y con él el llenado por columnas, la
> cabecera repetida por columna y el filete separador de grado evaluado dentro de cada columna.
> No es más trabajo del que la sección suponía, pero no es un flag que ya esté.

Las otras cuatro imágenes tienen aspecto 1,58 · 2,98 · 3,55 y entran sin tocar nada.

### Los números que van a la lámina de la atención, con el brazo limpio al lado

| brazo | familia | cabeza | folds | AUC, nueve del primario |
|---|---|---|---|---:|
| `json_out` (primario) | `_pth_balance` | predicha, ensemble | los cinco | **0,809 ± 0,127** |
| `ckpt --folds todos` | `_combined_5fold` | verdadera | los cinco | **0,792 ± 0,122** |
| `ckpt --folds limpios` | `_combined_5fold` | verdadera | los limpios | **0,770 ± 0,128** |

**El 0,809 no va sin esta tabla al lado**, y el pie declara las tres propiedades del `json_out`.

### Los números que van a la lámina de la escalera

| presupuesto | área total | `clam_mitosis` | `clam_gate` | azar |
|---|---:|---:|---:|---:|
| lámina entera | 706,1 mm² | 26 de 26 | 26 | 26,0 |
| 30 mm² por lámina | 360,2 mm² | **26 de 26** | 26 | 12,6 |
| 10 mm² por lámina | 120,1 mm² | **23 de 26** | 15 | 4,2 |
| **3 mm² por lámina** | **36,0 mm²** | **14 de 26** | 5 | 1,3 |
| 1 mm² por lámina | 12,1 mm² | **11 de 26** | 0 | 0,4 |

Dos cosas que el pie tiene que decir o los números se leen mal: el **presupuesto es por lámina y
el área es total** (3 mm² por lámina son 36,0 mm² sumados), y el control `sin_filtro` da **732
detecciones · 26 acreditadas** contra las **707 · 26** del `teselado`.

### Un `26` que era ambiguo, y ahora no

El cuerpo de la lámina de mitosis decía «la 129741 pone **13 de los 26**» (los aciertos del
total) y su columna derecha decía «**13 de 26**» (las marcas **de esa lámina**). Son la misma
unidad con **distinto denominador** y coinciden por casualidad, así que en láminas contiguas se
leen como el mismo número ([[dos-numeros-iguales-denominador-distinto]]). Ahora el cuerpo dice
«de los 26 **aciertos del total**» y el encabezado de la columna «**de sus marcas**».

### Dos cosas que salieron del QA visual y no de la auditoría automática

- **El rótulo del eje se montaba sobre el pie.** `h_eje = 0.25` alcanzaba para la línea y sus
  ticks, no para un renglón más de texto debajo. `auditar()` no lo vio.
- **El mosaico de atención era ilegible en su primera versión.** Dos causas: el thumbnail de un
  `.bif` es sobre todo fondo (se recorta al bounding box de las `coords`), y a escala de mosaico
  un parche de 256 px mide **3 píxeles**, así que las marcas hay que dibujarlas **después** del
  reescalado y a tamaño fijo en píxeles de la hoja.
- **Falta la leyenda nativa del mosaico**: qué significa el rojo del mapa y qué son los círculos
  blancos. Va como `leyenda_circulos()` en la lámina, igual que en s04 y s05.

### Dónde vive ahora el argumento de los tres NO-GO

Al borrar `lamina_ejes`, su tabla de los ocho ejes queda como **única fuente** en
[`../hovernext_tareas/inventario_tareas.md`](../hovernext_tareas/inventario_tareas.md) §4. Es lo
que el plan anticipó; queda anotado acá para que no se pierda.

---

## Estado al 2-sep-2026 (sesión 43) — el plan de las cinco láminas, con la forma DECIDIDA

Sesión de plan: **no tocó el deck ni la galería**. Lo que dejó es
`.handoffs/plan_B9_20260902_cinco_laminas_y_guion.md`, y **tres decisiones de Ernesto sobre la
forma de tres láminas**, que eran lo único que el plan anterior dejaba abierto.

| # | lámina | qué se decidió | por qué se preguntó |
|---|---|---|---|
| D1 | 7 · la atención | mosaico casi a todo el ancho (~3,1" de alto) y debajo los **tres brazos como barras** sobre eje 0,5 a 1,0, con su valor impreso. **No** una tabla | el mosaico solo (aspecto 2,98) ya llena la caja de figura, y el 0,809 no va sin los brazos al lado |
| D2 | 8 · la escalera | **barras de área** con el conteo impreso a la derecha (`26 de 26 · azar 26,0` … `14 de 26 · azar 1,3`). **No** la tabla de cinco filas | el plan pedía «nativa» y este README había dejado los números como tabla |
| D3 | 12 · los núcleos | **dos columnas de seis**: se conservan las doce láminas, cada recorte al doble de tamaño que hoy | la alternativa era tres filas (una por grado) con recortes al doble otra vez, perdiendo nueve láminas |

Las cinco láminas quedan en las posiciones **3 · 7 · 8 · 10 · 12** de un deck de trece, y el
orden completo está en el plan. Tres cosas que el plan fija y conviene no re-decidir:

- **La lámina 7 no lleva el AUC por lámina como tabla**: no hay sitio, y el mosaico ya rotula
  cada tile. Lo que sí lleva, obligatorio, es el pie con las tres propiedades del `json_out` más
  la cuarta línea de que **cuánto infla no se sabe**.
- **`clam_combinado` no entra en la lámina 8**: es exploratorio y así está declarado en
  `../atencion_12_laminas/resultados.md` §5.
- **La fila de los 3 mm² de la lámina 13 propone una ventana CONTIGUA, que sigue sin medir.** Lo
  que la escalera midió es una máscara **no contigua** de top-k por atención. Confundirlas sería
  presentar como hecho algo que no se midió.

Y una trampa que la sesión verificó al escribir el lector de los tres brazos: la columna `tarea`
trae el sufijo de familia, así que un filtro por igualdad contra un nombre fijo **devuelve cero
filas en dos de los tres CSV, sin error**. Va por prefijo. Detalle en
[`../atencion_12_laminas/csv_audit.md`](../atencion_12_laminas/csv_audit.md) §1, trampa 5.


---

## Estado al 3-sep-2026 (sesión 44) — el paso 0 hecho, los dos lectores escritos, tres correcciones

Sesión cortada a pedido de Ernesto con el **paso 0 completo** y el **primer tercio del paso 1**.
**Las cinco láminas no se escribieron**: el deck sigue en **ocho** y compila limpio.

### Lo que quedó hecho

| # | qué | dónde |
|---|---|---|
| 1 | **`nucleos_grado.png` recompuesto a dos columnas**, 3240 × 1668, aspecto 1,94 | `scripts/b9_galeria_nucleos_grado.py`, `hoja(..., n_col=2)` + flag `--n-col` |
| 2 | **`leer_atencion()`**, filtro por prefijo, `n = 9` en los tres brazos | `generate_b9_deck.py` |
| 3 | **`leer_escalera()`**, cinco peldaños y los seis conteos duros | `generate_b9_deck.py` |

Los dos lectores **abortan** en vez de dibujar mal: `leer_atencion` si algún brazo no da nueve
láminas, si los tres no cubren las mismas, o si el ordenamiento `json_out ≥ todos ≥ limpios` se
rompe; `leer_escalera` si las acreditadas no bajan al bajar el presupuesto o si se movió alguno de
los conteos (94 · 26 · 12 · 49.832 · 732/26 · 707/26).

**Un dato que el lector dejó servido para el guion:** las nueve láminas del primario están **sobre
el azar en los TRES brazos**, no sólo en el primario.

### Tres correcciones al plan, medidas contra el archivo

1. **El título de la lámina 7 no entra.** «La atención de CLAM cae sobre las mitosis marcadas»
   mide **12,98"** en una caja de **12,44"** ⇒ `set_titulo` aborta. Va la reserva del propio plan,
   **«La atención cae sobre las mitosis marcadas»** (10,70"). Los otros cuatro entran holgados:
   6,74 · 9,83 · 9,63 · 11,38.
2. **El reparto vertical de la lámina 7 no cabe.** Entre el tope del cuerpo (1,639) y el fin de la
   zona útil (6,60) hay **4,96"** para cuerpo, leyenda, mosaico, barras **y pie**. Con cuerpo de
   una línea y pie de cuatro, al mosaico le quedan **~2,44" de alto ⇒ ~7,3" de ancho**. «Casi a
   todo el ancho» (D1) **no es alcanzable apilado**; la salida que lo agranda a ~8,3" es poner las
   tres barras **al lado** del mosaico y no debajo, y **eso lo decide Ernesto**, porque D1 dijo
   «debajo». [[figura-alto-lo-decide-el-pie]]
3. **La leyenda nativa de la lámina 10 no es redundante.** `regiones_epi.png` ya trae leyenda y
   rótulos quemados, pero a escala de lámina caen a **5,7 y 6,4 pt**, bajo el mínimo de 7 pt del
   template. Va nativa, y con ella una fila con los cuatro `f_epi` leídos del JSON.
   [[png-rotulos-quemados-pierden-pt]]

### Un dato para el QA visual de la lámina 12

Con dos columnas (D3) el PNG entra limitado por el alto: **~7,1" de ancho**, y cada recorte queda
en **~0,53"** de lado. Con **tres columnas de cuatro** el aspecto sería 4,34, entraría limitado por
el **ancho** (los 12,097" completos) y el recorte subiría a **~0,60"**. Las doce láminas se
conservan en las dos. **No se cambió nada**: D3 dice dos columnas y el flag `--n-col` deja probar
la alternativa en un comando, si el QA visual muestra que a 0,53" no se lee.

---

## Estado al 3-sep-2026 (sesión 45) — sesión de plan: D4 y D5, y el paper de las 3 mm² apareció

**No tocó el deck ni la galería**: sigue en **ocho** láminas. Dejó el plan de ejecución con las dos
decisiones que faltaban y cerró un pendiente que venía arrastrado desde la sesión 41.

### Las dos decisiones de Ernesto

| # | lámina | decidido | por qué se preguntó |
|---|---|---|---|
| **D4** | 7 · la atención | **las tres barras van AL LADO del mosaico**, no debajo. El mosaico crece a **8,3"** (tile ~1,38") y las barras ocupan 3,5" a su derecha | D1 pedía «casi a todo el ancho» y «debajo», y apilado el mosaico caía a 7,3". Las dos cosas no entraban ([[figura-alto-lo-decide-el-pie]], ahora cerrada) |
| **D5** | 12 · los núcleos | se entrega a **dos columnas** (D3); si el QA visual muestra que a ~0,53" no se lee, se pasa a **`--n-col 3`** (~0,60") **sin volver a preguntar**, y se reporta al entregar | el flag ya existe desde la sesión 44 y las doce láminas se conservan en las dos |

Con D4 el reparto vertical de la lámina 7 cierra con holgura: cuerpo de una línea (fin ≈ 2,01),
`leyenda_mapa` 0,20, mosaico 8,30 × 2,79" al lado de `barras_auc` en 3,50", y quedan ~0,5" que pagan
una **quinta** línea de pie (las nueve láminas están sobre el azar en los tres brazos).

### Verificado contra el archivo al abrir la sesión

| qué | resultado |
|---|---|
| aspectos de las cuatro imágenes | 1,58 · 2,98 · 3,55 · **1,94** (la galería recompuesta) |
| los cinco títulos a 40 pt bold en 12,44" | 6,74 · **12,98 no entra** · 9,83 · 9,63 · 11,38 ⇒ confirmada la corrección 1 de la sesión 44 |
| `agregado.csv` | los cinco peldaños y los dos controles, tal como `leer_escalera()` los espera |
| `main` contra `origin` | sincronizada, árbol limpio, cero jobs propios |

### El paper de las 3 mm² apareció, y con él un cuarto solape

`AreaMitosis.md` en el workspace de `sgaete` **es** el paper que Sebastián citó: Ibrahim, Lashen,
Katayama, Mihai, Ball, Toss y Rakha, *Defining the area of mitoses counting in invasive breast
cancer using whole slide image*, **Modern Pathology (2022) 35:739-748**,
doi:10.1038/s41379-021-00981-w. Contar en **3 mm² es lo más representativo** en saturación y
concordancia; por debajo de **2 mm²** el conteo baja significativamente (P = 0,02); de **4 mm²** para
arriba se vuelve caro en tiempo. **La fila de la lámina 13 puede llevar la cita**, con la salvedad
de que es una inferencia razonable y no una confirmación de él.
[[paper-3mm2-ibrahim-modern-pathology]]

En el mismo directorio están sus jobs `5213 hnx_time` y `5249 hnx_win`, que corren **HoVer-NeXt con
nuestro mismo checkpoint** sobre 81 ventanas de **nuestras mismas láminas**. Es el **cuarto solape**
con `sgaete` y toca la **fila 2 de la lámina 13** (el punto caliente por ventana de área fija).
**Preguntarle qué cubre `hnx_win` antes de presentar esa fila.**

---

## Estado al 3-sep-2026 (sesión 46) — el plan verificado y aprobado, y un cable que falta

**No tocó el deck**: sigue en **ocho** láminas. Sesión de plan: verificó el plan de la sesión 45
contra el archivo, Ernesto lo aprobó y cortó antes de ejecutar. Lo único que cambió en el repo son
dos correcciones al aviso a `sgaete` (`../auditoria_coherencia/hallazgos.md`, sexta pasada, F1 y F2).

### Lo verificado corriendo, no leyendo

| qué | resultado |
|---|---|
| `leer_atencion()` | **0,8086 ± 0,1273** · **0,7924 ± 0,1221** · **0,7701 ± 0,1279**, n = 9 en los tres, **9 de 9 sobre el azar** en los tres, conteos `12/9/113/103` |
| `leer_escalera()` | 706,1 → 360,2 → 120,1 → **36,0** → 12,1 mm²; mitosis 26·26·23·**14**·11, gate 26·26·15·**5**·0, azar 26,0·12,6·4,2·**1,3**·0,4; los seis conteos duros sin moverse |
| los seis títulos a 40 pt bold en 12,44" | 6,74 · **12,98 no entra** · **10,70** (la reserva) · 9,83 · 9,63 · 11,38 |
| aspectos de las cuatro imágenes | 1,58 · 2,98 · 3,55 · **1,94** |

### El cable que falta, y que «los lectores ya existen» no dice

`leer_atencion()` (:722) y `leer_escalera()` (:766) están escritos y **no se llaman desde
`main()`**, que sólo invoca `leer_datos`, `datos_eje4` y `datos_eje3` (:1533-1535). Los seis
constantes de las cinco láminas (`PNG_HOVERNEXT`, `PNG_ATENCION`, `PNG_REGIONES`, `PNG_NUCLEOS`,
`JSON_REGIONES`, `JSON_NUCLEOS`, :91-97) están declarados y **sin una sola referencia** aguas
abajo. No es un defecto: es lo que la sesión 44 dejó a propósito, y por eso el deck compila limpio
en ocho. Se anota porque la sesión que ejecute tiene que **cablearlos**, y el handoff decía «los
dos lectores ya existen y están verificados», que se puede leer como «ya están conectados».

### La fila de los 3 mm² SÍ lleva cita

El plan del 3-sep §«La lámina 13» dice «sin cita, pedirle la referencia sigue pendiente». Quedó
atrás: el paper apareció ese mismo día y el handoff §6.3 lo supersede. La fila cita a **Ibrahim
et al., Modern Pathology 2022**, declarando que atribuírsela a la cita de Sebastián es una
**inferencia** nuestra ([[paper-3mm2-ibrahim-modern-pathology]]). Lo que sigue abierto es su
confirmación, no la referencia.

---

## Estado al 3-sep-2026 (sesión 47) — las cinco láminas escritas, el deck en TRECE

Sesión de ejecución pura: corrió el plan
`.handoffs/plan_B9_20260903_cinco_laminas_D4_D5.md` de punta a punta con las correcciones
del handoff de la sesión 46 encima. **El deck pasa de ocho a trece láminas**, sale con
código 0 y `auditar()` y `barrer_rayas()` no reportan nada.

### Lo que se escribió

| # | qué | dónde |
|---|---|---|
| 0 | **El cable que faltaba**: `leer_atencion()` y `leer_escalera()` entran a `main()`, y los seis constantes de las cinco láminas quedan referenciados | `generate_b9_deck.py` |
| 1 | **Cuatro primitivas**: `leyenda_mapa` (rampa turbo nativa + el anillo), `barras_auc` (eje truncado en 0,50 **y declarado**), `barras_area`, `tira_dimensiones` | ídem, §Primitivas |
| 1.a | **`medir_figura()`**, que `poner_figura` usa por dentro: existe porque dos láminas alinean rótulos nativos con los paneles de un PNG y `poner_figura` centra | ídem |
| 2 | **Las cinco láminas** 3 · 7 · 8 · 10 · 12 y `reordenar()` a trece | ídem |
| 3 | **La fila de los 3 mm²** en la lámina 13, `min_h` de vuelta al default 0,76 | `lamina_tareas` |
| 4 | **El guion a trece bloques**, con los tres huérfanos afuera y los dos números corregidos | `guion_b9.md` |

### El orden final, trece

```
s01  portada                                     TAL CUAL, copy de la empresa
s02  OBJETIVOS 25/08/2026 - 07/09/2026           tabla 4x4, 3 filas de cuerpo
s03  Cómo funciona HoVer-NeXt                    figura del paper + tira NATIVA de 6 bloques
s04  Mitosis: 26 de 94 marcas del patólogo       cuerpo + 12 barras NATIVAS
s05  Las 26 marcas que el detector reencuentra   leyenda nativa + lámina de contacto
s06  Las 68 marcas que se escapan                leyenda nativa + lámina de contacto
s07  La atención cae sobre las mitosis marcadas  leyenda_mapa + mosaico 8,30" + barras_auc AL LADO
s08  El recorte compra superficie, no marcas     barras_area, cinco peldaños
s09  El control positivo separa epitelio…        8 barras de rango intercuartil NATIVAS
s10  Una región de epitelio y una de estroma     figura + leyenda nativa + 4 rótulos nativos
s11  Los tres grados ordenan sobre diez láminas  strip de 10 puntos + tabla NATIVA
s12  Los núcleos marcados contra su propia lámina  galería a dos columnas
s13  Tareas del próximo período                  tabla 4x3 con TRES filas de cuerpo
```

### Las decisiones, ejecutadas

- **D4** (las barras al lado del mosaico) ejecutada tal cual. Con cuerpo de dos líneas y pie
  de cinco, el techo del mosaico da **8,49"** y se usan los **8,30"** que fijó la decisión.
- **D5** (los núcleos a dos columnas, con permiso de pasar a tres) **queda pendiente**: el QA
  visual muestra que a ~0,55" los rótulos quemados no se leen, así que corresponde el
  `--n-col 3`. No se ejecutó por falta de tiempo de sesión, y **no hay que volver a
  preguntarlo**.
- La fila de los 3 mm² **lleva la cita** (Ibrahim et al., *Modern Pathology* 2022). En la
  lámina va la cita a secas, que es correcta; **la salvedad de que ése sea el paper que citó
  Sebastián es una inferencia nuestra**, y por eso vive acá y no en la lámina.

### Lo que encontró el QA visual, y `auditar()` no

Se rasterizó con LibreOffice y `FONTCONFIG_FILE` apenas existieron las láminas, que es lo que
pide [[image-api-qa-limit]]. Tres hallazgos, dos ya corregidos:

1. **Los cuatro rótulos de la lámina 10 salían CRUZADOS.** `regiones_epi.json` lista los
   paneles en el orden en que se **midieron** y el PNG los dibuja **ordenados**
   (`b9_galeria_regiones_epi.main()` hace el `sort` después de armar el `meta`). **Corregido**
   reproduciendo la misma clave de orden. Ningún chequeo de cajas podía verlo: las cajas
   estaban bien y el texto era correcto, sólo que debajo del panel de al lado.
   [[sidecar-orden-no-es-el-de-la-figura]]
2. **«tasa mitótica» y «gate invasivo» quedaban pegadas** en la cabecera de `barras_area`.
   **Corregido** ensanchando las dos columnas.
3. **Dos PNG tienen los rótulos quemados muy por debajo de 7 pt** y no se corrigió:
   `atencion_12_laminas.png` a **4,4 pt** y `nucleos_grado.png` a **2,5 pt**. En los dos el
   rótulo está dentro de una grilla, así que el rótulo nativo de la lámina 10 **no** es la
   salida: hay que **regenerar el PNG con la fuente dimensionada para la lámina**. Queda
   pendiente, con la cuenta en [[png-rotulos-quemados-pierden-pt]].

### Lo que NO alcanzó a hacerse

- **`@humanizer-es` sobre el guion entero**, que era el paso 5 del plan.
- **El `--n-col 3` de la galería** (D5) y las **dos regeneraciones de PNG** del punto 3.
- **Darle el deck a leer a Ernesto** en su versión de trece. Al entregar hay que ofrecerle
  las trece rasterizadas: el QA certifica corrección, no comprensión.
