# Deck del período B9 — `[20260908] [Ernesto Gamero] [Detección Nuclear].pptx`

Primer deck sobre la **plantilla oficial nueva** (`docs/plantilla_oficial.md`), la que
Ernesto fijó el 25-ago y que supersede a Deep-LLM-V. Registro **executive deck**, no deck
técnico de sprint.

| | |
|---|---|
| Fuente de verdad | `generate_b9_deck.py` (el `.pptx` es derivado y está gitignored, `.gitignore:55`) |
| Guion | `guion_b9.md`, que el generador **lee** y aplica con `notes()`. El `.md` es la fuente; las notas del `.pptx` son derivadas |
| Figuras | `assets/mitosis_{aciertos,falladas}.png`, que produce `scripts/galeria_mitosis_12.py` |
| Molde | `papers/presentations/[AAAAMMDD] [Nombre Apellido] [Image-to-text].pptx`, **read-only** |
| Salida | 7 láminas, 13,333 × 7,5, Barlow embebida, 9,2 MB |

## Regenerar

```bash
cd sprints/B9_sprint9/presentacion_b9
PYTHONPATH=/media/administrador/Storage1/sdonoso/clam_testing2/.pylibs \
  /home/sdonoso/miniconda3/envs/clam_latest/bin/python generate_b9_deck.py
```

Sale con código 1 si la auditoría o el barrido de estilo tienen avisos. Hoy salen los dos
limpios. Las dos figuras **no** se regeneran desde acá: si cambia el cruce, primero
`scripts/galeria_mitosis_12.py` y después el deck.

> **Cuando se incorporen las cuatro figuras de los ejes nucleares, el intérprete cambia.** El
> deck pasa a depender de `zarr` (por `b9_pleomorfismo`, de donde salen `spearman` y
> `permutacion_exacta`), y `clam_latest` no lo tiene. Verificado el 28-ago:
> `/home/sdonoso/miniconda3/envs/pruebas/bin/python` con el mismo `PYTHONPATH` importa **pptx
> 1.0.2, lxml, PIL, pandas, numpy, zarr y scipy** en un solo proceso y abre los TTF de Barlow.
> No hace falta re-verificarlo.

## Las decisiones de Ernesto

| | |
|---|---|
| Idioma | **todo en español**, decidido el 27-ago. Antes eran láminas en inglés con guion en español |
| Proyecto (3er corchete y cejilla) | **Detección Nuclear**. NO `Mitosis Detection`: ése es el rótulo con el que `sgaete` presenta su YOLOv11-m, y es literalmente el ejemplo que trae la plantilla |
| Período del título | **25/08/2026 - 08/09/2026** |
| Láminas de contenido | **cuatro**: el número, los aciertos, las falladas y los ocho ejes |
| Portada | queda **en inglés y tal cual**: es copy de la empresa, no contenido nuestro |
| Los dos ejes nucleares (28-ago) | las **cuatro figuras entran al cuerpo**, entre los recortes de mitosis y la lámina de ejes. El deck pasa a **once láminas**. **Decidido y NO ejecutado**: ver abajo |

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
s06  HoVer-NeXt: qué se puede medir y qué no    UN punto de cuerpo + tabla NATIVA de 8 ejes
s07  Tareas del próximo período                 tabla 4x3
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
y `reordenar`. La lámina de contenido del molde se clona **cuatro** veces.

Sigue en pie el motivo de siempre para abrir el `.pptx` en vez de usar `Presentation()`: la
plantilla **embebe Barlow** ([[deck-template-fuentes-embebidas]]). Y sigue haciendo falta
`forzar_barlow()`, porque el `fontScheme` del theme de ESTA plantilla también es Arial.

## Los números salen leídos, no transcritos

`leer_datos()` arma la lámina de mitosis desde `results/b9_cruce_94/por_lamina.csv` y
`recall_por_tolerancia_agregado.csv`: el título, los tres puntos del cuerpo, las doce barras y
el tramo plano de la escalera. Los títulos de s04 y s05 también salen de ahí (`26` y `94−26`).
Si el CSV cambia, el deck cambia solo. Además **verifica** que el agregado y el por-lámina
coincidan, y **aborta** si no.

## QA — las cuatro capas ([[deck-qa-puntos-ciegos-chequeo]])

1. **Round-trip estructural**: reabierto con python-pptx. 7 láminas en orden, cada una con
   cejilla y título, las tres tablas del molde con sus filas, la tabla nativa de ejes, las
   dos imágenes y notas en las siete. `auditar` sin avisos.
2. **Medición de texto real** con los TTF de Barlow bajo containment: ninguna caja que
   desborde, ninguna celda que corte, ningún cuerpo bajo los 7 pt del template.
3. **Rasterizado y lectura visual**: LibreOffice con `FONTCONFIG_FILE` del workspace, las
   siete láminas miradas una por una, y las dos figuras miradas aparte antes de insertarlas.
   Hecho **temprano** ([[image-api-qa-limit]]).
4. **Cruce de contenido contra las fuentes**: cada número contra `por_lamina.csv`,
   `recall_por_tolerancia_agregado.csv`, `cruce_94.md` §1-§2 e `inventario_tareas.md` §1 y §4.
   26 + 68 = 94 verificado sobre los doce `pares_*.csv`, y las cinco láminas que acreditan
   alguna marca contadas sobre el mismo archivo.

Más los dos de estilo: `unzip` y contar `typeface` (1290 `Barlow`; los `Arial` que quedan son
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
el deck quedó en **siete**. La discrepancia original no se resolvió: quedó superada.

## Lo que este deck NO dice, a propósito

- El 27,7 % **no es el recall de HoVer-NeXt**: el denominador son **las marcadas**.
- **No** se llama falso positivo a ninguna detección sin marca, ni se calcula precisión, F1 o
  PQ. Contra positivos parciales no son computables, y decirlo es parte del resultado. Por eso
  la lámina de aciertos muestra 26 recortes y no las 732 detecciones.
- El **13 de 26** de la 129741 **no** se presenta como el resultado: era el mejor caso de doce,
  y la lámina lo dice en su segundo punto.
- **No** se mezclan unidades: marcas (26 / 68 / 94), detecciones (732), polígonos (472).
- Los tres NO-GO son **por argumento**, no por presupuesto.

## Pendiente: las cuatro figuras de los ejes nucleares

Ernesto decidió el **28-ago** que **las cuatro entran al cuerpo**, entre los recortes de mitosis
y la lámina de ejes, y que el deck pasa a **once láminas**. Con eso, **tres tablas quedan
contradiciendo al deck** y se actualizan en el mismo movimiento:

| Tabla | Qué cambia |
|---|---|
| OBJETIVOS (s02) | la fila de métricas nuevas pasa de «En curso» a **Cerrado**, nombrando los dos ejes medidos |
| Los ocho ejes | «Grado nuclear» y «Tumor y estroma» pasan de «CPU, en disco / GO» a **medidos**, con la forma de la fila de Mitosis |
| Tareas | pierde la fila de los dos ejes de procesador y **queda con dos**, sin reemplazo |

**Nada de esto está ejecutado.** Hoy el deck tiene siete láminas; el plan de integración lo
ejecuta una sesión limpia y vive en el handoff. Las cuatro láminas ya existen y están
verificadas en [`../ejes_nucleares/figuras/`](../ejes_nucleares/figuras/).

El `.pptx` viejo en inglés, `[20260908] [Ernesto Gamero] [Nuclear Detection].pptx`, **se borró**
el 28-ago por decisión de Ernesto. Era derivado y gitignored: se regenera cambiando `PROYECTO`.
