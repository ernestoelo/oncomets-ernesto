# Deck del período B9 — `[20260908] [Ernesto Gamero] [Detección Nuclear].pptx`

Primer deck sobre la **plantilla oficial nueva** (`docs/plantilla_oficial.md`), la que
Ernesto fijó el 25-ago y que supersede a Deep-LLM-V. Registro **executive deck**, no deck
técnico de sprint.

| | |
|---|---|
| Fuente de verdad | `generate_b9_deck.py` (el `.pptx` es derivado y está gitignored, `.gitignore:55`) |
| Guion | `guion_b9.md`, que el generador **lee** y aplica con `notes()`. El `.md` es la fuente; las notas del `.pptx` son derivadas |
| Figuras | `assets/mitosis_{aciertos,falladas}.png`, que produce `scripts/galeria_mitosis_12.py`. Las cuatro de los ejes nucleares son **nativas** y las dibuja el propio generador |
| Molde | `papers/presentations/[AAAAMMDD] [Nombre Apellido] [Image-to-text].pptx`, **read-only** |
| Salida | 11 láminas, 13,333 × 7,5, Barlow embebida, 9,2 MB. **Van a trece**: ver §La revisión de Ernesto, decidida el 1-sep y sin ejecutar |

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
s02  OBJETIVOS 25/08/2026 - 08/09/2026          tabla 4x4 (se quitó la 4ª fila de cuerpo)
s03  Mitosis: 26 de 94 marcas del patólogo      cuerpo + figura NATIVA de 12 barras
s04  Las 26 marcas que el detector reencuentra  cuerpo + leyenda nativa + lámina de contacto
s05  Las 68 marcas que se escapan               cuerpo + leyenda nativa + lámina de contacto
s06  El control positivo separa epitelio…       cuerpo + 8 barras de rango intercuartil NATIVAS
s07  Ninguna traslación del nulo llega al…      cuerpo + histograma NATIVO + tres marcadores
s08  Los tres grados ordenan sobre diez…        cuerpo + strip de 10 puntos + tabla NATIVA 11x5
s09  El nulo exacto, y la población que no…     cuerpo + dos histogramas NATIVOS apilados
s10  HoVer-NeXt: qué se puede medir y qué no    UN punto de cuerpo + tabla NATIVA de 8 ejes
s11  Tareas del próximo período                 tabla 4x3 con DOS filas de cuerpo (`min_h=1.14`)
```

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
