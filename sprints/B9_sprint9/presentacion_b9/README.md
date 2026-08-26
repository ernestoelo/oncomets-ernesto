# Deck del período B9 — `[20260908] [Ernesto Gamero] [Nuclear Detection].pptx`

Primer deck sobre la **plantilla oficial nueva** (`docs/plantilla_oficial.md`), la que
Ernesto fijó el 25-ago y que supersede a Deep-LLM-V. Registro **executive deck en inglés**,
no deck técnico de sprint.

| | |
|---|---|
| Fuente de verdad | `generate_b9_deck.py` (el `.pptx` es derivado y está gitignored, `.gitignore:55`) |
| Guion | `guion_b9.md`, que el generador **lee** y aplica con `notes()`. El `.md` es la fuente; las notas del `.pptx` son derivadas |
| Molde | `papers/presentations/[AAAAMMDD] [Nombre Apellido] [Image-to-text].pptx`, **read-only** |
| Salida | 5 láminas, 13,333 × 7,5, Barlow embebida |

## Regenerar

```bash
cd sprints/B9_sprint9/presentacion_b9
PYTHONPATH=/media/administrador/Storage1/sdonoso/clam_testing2/.pylibs \
  /home/sdonoso/miniconda3/envs/clam_latest/bin/python generate_b9_deck.py
```

Sale con código 1 si la auditoría o el barrido de estilo tienen avisos. Hoy salen los dos
limpios.

## Las cuatro decisiones de Ernesto

| | |
|---|---|
| Guion | **español**. Las láminas en inglés porque la plantilla lo exige; las notas en el idioma en que se habla |
| Proyecto (3er corchete y cejilla) | **Nuclear Detection**. NO `Mitosis Detection`: ése es el rótulo con el que `sgaete` presenta su YOLOv11-m, y es literalmente el ejemplo que trae la plantilla |
| Período del título | **25/08/2026 - 08/09/2026** |
| Láminas de contenido | **dos** (arquetipo s03) |

## Estructura

```
s01  portada          TAL CUAL, es copy de la empresa. Sólo se le pone guion
s02  OBJECTIVES 25/08/2026 - 08/09/2026     tabla 4x4 (se quitó la 4ª fila de cuerpo)
s03  Mitosis: 26 of 94 pathologist marks    cuerpo + figura NATIVA de 12 barras
s04  HoVer-NeXt: what is measurable, ...    cuerpo + tabla NATIVA de 8 ejes
s05  Tasks for the next period              tabla 4x3
```

## El método: rellenar en sitio

Es lo contrario de los seis decks anteriores, que abrían el template y le **borraban** las
láminas (`base_from_template()` de `generate_b8_deck.py:341`). Acá se rellena, porque las
tablas de s02 y s04 traen las filas de cuerpo vacías **pero ya estilizadas** y reproducir eso
a mano es trabajo perdido. Las tres maniobras sin API en python-pptx están en
`docs/plantilla_oficial.md` §7.a e implementadas en `clonar_s03`, `_quitar_fila` / `_alto_fila`
y `reordenar`.

Sigue en pie el motivo de siempre para abrir el `.pptx` en vez de usar `Presentation()`: la
plantilla **embebe Barlow** ([[deck-template-fuentes-embebidas]]). Y sigue haciendo falta
`forzar_barlow()`, porque el `fontScheme` del theme de ESTA plantilla también es Arial.

## Helpers portados de `generate_b8_deck.py`

`forzar_barlow` (`:1185`), `_set_runs` / `add_textbox` (`:406`, `:423`), `_rect` / `notes` /
`pie_lineas` (`:434`, `:429`, `:999`), `_face` / `text_w` / `wrap_lines` / `_alto_bloque`
(`:708`-`:747`), `auditar` (`:1283`) con los límites de esta geometría, y `simple_table`
(`:660`) reescrita como `tabla_ejes` con la paleta nueva.

**No** se portaron `scale_deck_to_1610` (la plantilla ya es 13,333 nativo), `reflow_onco`,
`header_oncomets` ni la gramática de diagrama de Deep-LLM-V, que es de la paleta vieja.

No se portó `_add_runs` (el mini-markup de sub/superíndices): este deck no tiene ecuaciones y
su único superíndice, el `mm²`, es un carácter Unicode que Barlow sí trae.

## Los números salen leídos, no transcritos

`leer_datos()` arma la lámina de mitosis desde `results/b9_cruce_94/por_lamina.csv` y
`recall_por_tolerancia_agregado.csv`: el título, los tres puntos del cuerpo, las doce barras y
el tramo plano de la escalera. Si el CSV cambia, el deck cambia solo. Además **verifica** que
el agregado y el por-lámina coincidan, y **aborta** si no.

## QA — las cuatro capas ([[deck-qa-puntos-ciegos-chequeo]])

1. **Round-trip estructural**: reabierto con python-pptx. 5 láminas en orden, cada una con
   cejilla y título, las tres tablas con las filas esperadas, `auditar` sin avisos.
2. **Medición de texto real** con los TTF de Barlow bajo containment: ninguna caja que
   desborde, ninguna celda que corte, ningún cuerpo bajo los 7 pt del template. Cazó dos
   cosas que un chequeo de bounding boxes no ve, las dos abajo.
3. **Rasterizado y lectura visual**: LibreOffice con `FONTCONFIG_FILE` del workspace, las
   láminas miradas una por una. Hecho **temprano** ([[image-api-qa-limit]]).
4. **Cruce de contenido contra las fuentes**: cada número contra `por_lamina.csv`,
   `recall_por_tolerancia_agregado.csv`, `cruce_94.md` §1-§2 e `inventario_tareas.md` §1 y §4,
   y los `n` de las clases **recontados sobre los doce geojson `- GDT`**.

Más los dos de estilo: `unzip` y contar `typeface` (1265 `Barlow`; los `Arial` que quedan son
entradas `<a:font script="Arab|Viet|Hebr">` del theme y `tableStyles.xml`, que no gobiernan
texto latino, igual que en el deck del B8) y `ppt/fonts/*.fntdata` sigue en el paquete con las
cuatro variantes · barrido de «—», «–» y «palanca» **saltando s01**, cuyo titular trae un «—»
que es copy de la empresa.

## Cuatro cosas que el QA encontró y que el handoff no traía

1. **`107 graded regions / 8` estaba mal: son `/ 12`.** El «/8» es el de `Nucleos alto grado`
   sola. Las tres clases de grado son **disjuntas** (alto 8, moderado 2, bajo 2) y parten las
   doce láminas exactas, así que el grado está declarado en **todas**, lo que refuerza que sea
   el más barato de los tres GO. Recontado sobre los doce geojson; el resto de los `n` del
   inventario dio **exacto** (472 anotaciones, 21 clases, necrosis 18 / 5).
2. **`Google Shape;287;p7` NO es una barra `1B4F8C`.** Es un cuadro de texto de pie **vacío**
   (`<a:noFill/>`), y lo único visible al pie es la línea `E4E9EC` de 7,079. Corregido en
   `docs/plantilla_oficial.md` §5, que lo daba como barra de color.
3. **El título de la segunda lámina de contenido no entraba.** El del handoff pide 14,07" a
   40 pt contra los 12,44" de la caja, o sea dos líneas encima del cuerpo, o bajar a 34 pt y
   romper el 40 pt del molde. Se reformuló a **`HoVer-NeXt: what is measurable, and what is
   not`** (11,99"), que dice lo mismo y entra en una línea. `set_titulo` **aborta** si un
   título futuro no entra, en vez de dejarlo desbordar.
4. **El primer objetivo llegaba al filete de su columna** (3,37" de 3,39"): pasó a
   `Scale mitosis detection to 12 annotated WSI`. El auditor ahora avisa cuando una celda de
   una línea queda a menos de 0,06" de su borde, que es un defecto que no cuenta como desborde
   y aun así se ve.

Y un ajuste de composición: el molde trae **cuatro** filas de cuerpo y acá van **tres**, así
que con el alto justo del texto la tabla se encogía y dejaba media lámina vacía. `llenar_tabla`
tiene `min_h=0.76` para conservar la huella original del molde (0,745 + 3 × 0,76 = 3,03).

## Discrepancia declarada: el deck tiene 5 láminas, no 6

El handoff dice «seis láminas» en §1, §10 y §11, pero su propia aritmética es
«las cuatro de la plantilla más una lámina de contenido extra», que da **cinco**; §5 fija
**dos** láminas de contenido y §7 manda **borrar** la s03 original. El contenido literal de §8
cubre exactamente s02, s03(a), s03(b) y s04, más la portada intacta: **cinco**. No hay material
especificado para una sexta. Se construyeron las cinco.

## Lo que este deck NO dice, a propósito

- El 27,7 % **no es el recall de HoVer-NeXt**: el denominador son **las marcadas**.
- **No** se llama falso positivo a ninguna detección sin marca, ni se calcula precisión, F1 o
  PQ. Contra positivos parciales no son computables, y decirlo es parte del resultado.
- El **13 de 26** de la 129741 **no** se presenta como el resultado: era el mejor caso de doce,
  y la lámina lo dice en su segundo punto.
- **No** se mezclan unidades: marcas (26 / 94), detecciones (732), polígonos (472 anotaciones).
- Los tres NO-GO son **por argumento**, no por presupuesto.
