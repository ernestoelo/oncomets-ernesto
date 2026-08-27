# Plantilla oficial de presentaciones (desde el 25-ago-2026)

> **Fuente**: `papers/presentations/[AAAAMMDD] [Nombre Apellido] [Image-to-text].pptx`, subida por
> Ernesto el 25-ago-2026 después de borrar todas las plantillas anteriores de esa carpeta.
> **Supersede** a `Modelo OncoMets Spatial V1 Deep-LLM-V.pptx` para todo deck nuevo.
>
> **Este documento existe porque el `.pptx` NO se versiona**: `papers/presentations/` está en
> `.gitignore` (línea 93) por ser carpeta de trabajo local. Si el archivo se pierde, esto es lo
> que permite reconstruirlo. Todo lo de acá está **verificado leyendo el archivo** con python-pptx
> y `unzip`, no inferido.
>
> Procedencia: su `docProps/core.xml` declara `lastModifiedBy = SEBASTIÁN GONZALO GAETE CAROCA`
> y `modified = 2026-08-24`. La plantilla viene del equipo, no la armamos nosotros.

## 1. Lo que cambia respecto de Deep-LLM-V

| | Deep-LLM-V (hasta el 24-ago) | Plantilla oficial (desde el 25-ago) |
|---|---|---|
| Idioma | español | **inglés** |
| Láminas | 19 (portada + título + 17 técnicas) | **4** (portada + objetivos + contenido + tareas) |
| Registro | deck técnico de sprint | **executive deck**: objetivos, resultado, tareas del período |
| Paleta | teal `#3E6877` / `#CDDFE1` / `#B7B7B7` | azul `#1B4F8C` / `#5293DE`, título `#1A1A2E`, teal `#28D5C1` |
| Nombre | libre | `[AAAAMMDD] [Nombre Apellido] [Proyecto].pptx` |

Lo que **no** cambia y sigue vigente: construir el deck **sobre el `.pptx` de la plantilla**
(abrirlo y borrarle las láminas), nunca con `Presentation()`, porque la plantilla **embebe sus
fuentes** y un deck construido desde cero las pierde ([[deck-template-fuentes-embebidas]]); todo
nativo y editable, no PNG ([[deck-completo-pptx-buildable]]); notas del presentador como guion
hablado corrido ([[notas-presentador-guion-didactico]]).

## 2. Nombre del archivo

```
[AAAAMMDD] [Nombre Apellido] [Proyecto].pptx
```

Los tres corchetes son literales y forman parte del nombre. El tercero es el **proyecto o línea de
trabajo** del deck, no la fecha ni el sprint: en el archivo de referencia dice `Image-to-text`.

## 3. Geometría y tipografía

- **13,333 × 7,5 pulgadas** (12192000 × 6858000 EMU), o sea 16:9 al mismo tamaño que Deep-LLM-V.
- **Barlow en todo**, embebida en el paquete (`ppt/fonts/*.fntdata`, con las cuatro variantes:
  regular, bold, italic, boldItalic).
- **El `fontScheme` del theme sigue siendo Arial** y las láminas heredadas traen Calibri en
  `endParaRPr`. Igual que con Deep-LLM-V, **hace falta forzar Barlow run a run**
  (`forzar_barlow(prs)` de `generate_b7_deck.py`) o lo que se escriba encima hereda Arial o
  Calibri. Verificación: `unzip` del `.pptx` y contar `typeface="..."` bajo `ppt/`.

## 4. Paleta

| Uso | Hex |
|---|---|
| Título de lámina | `1A1A2E` |
| Cuerpo, cejilla y relleno de cabecera de tabla | `1B4F8C` |
| Acento de la cejilla y del subtítulo | `5293DE` |
| Separador de la cejilla (el `·`) | `9AA3B4` |
| Acento de portada (sobre foto) | `28D5C1` |
| Línea de remate al pie | `E4E9EC` |

## 5. Las cuatro láminas

### s01 — portada
Foto a sangre (13,33 × 7,5) más logo arriba a la derecha (0,95 × 1,02 en L=12,14 T=0,28).
Sobre la foto, tres bloques alineados a L=0,72: cejilla `EXECUTIVE DECK ·` en 13 pt bold `28D5C1`
(T=3,14); titular en **54 pt bold blanco** con la última palabra en `28D5C1` (T=3,60); bajada en
17 pt bold (T=5,34).

### s02 — `OBJECTIVES <dd/mm/aaaa – dd/mm/aaaa>`
- Cejilla `ONCOMETS   ·   <Proyecto>` en 12 pt bold, L=0,60 T=0,38: `ONCOMETS` en `1B4F8C`, los
  separadores en `9AA3B4`, el proyecto en `5293DE`.
- Título en **40 pt bold `1A1A2E`**, L=0,58 T=0,77, ancho 12,44.
- **Tabla 5×4** en L=0,87 T=2,24 (11,59 × 3,03), columnas `[3,44 · 6,03 · 1,11 · 1,01]` y filas
  `[0,75 · 0,64 · 0,55 · 0,55 · 0,55]`. Cabecera `Objective · Deliverable · Date · Status`, relleno
  `1B4F8C`, texto **blanco 16 pt bold centrado**.

El rango de fechas del título es el **período que cubre el deck**, no la fecha de la reunión.

### s03 — lámina de contenido (el arquetipo que se repite)
- Misma cejilla que s02, con el **tema** en vez del proyecto (en el archivo: `Mitosis Detection`).
- Título en 40 pt bold `1A1A2E`, L=0,57 T=0,67.
- Cuerpo en un cuadro de texto L=0,62 T=1,64 (12,10 × 2,43), **16 pt `1B4F8C`**, con el arranque de
  cada punto en **bold** y el resto en regular. Ese bold de entrada es la gramática de la lámina:
  hace de rótulo, no de énfasis.
- Figura centrada debajo (en el archivo: 9,12 × 3,80 en L=1,66 T=2,92).
- Remate al pie: línea `E4E9EC` en T=7,08, y encima un **cuadro de texto de pie VACÍO**
  en T=6,72 (12,10 × 0,40), centrado. **No es una barra `1B4F8C`**: su `spPr` trae
  `<a:noFill/>` y `<a:ln><a:noFill/></a:ln>` (verificado en el XML el 26-ago, corrige la
  primera redacción de este §). Lo único visible al pie es la línea; el cuadro se respeta
  como límite inferior del contenido porque es la zona de pie, no porque se vea.

### s04 — `Tasks for the next period`
Igual que s02 pero **tabla 4×3** (`Objective · Deliverable · Date`, sin `Status`) en L=1,37 T=2,72,
10,59 × 2,48.

## 6. Cómo se lee la estructura

El deck cuenta un período, no un sprint entero: **qué me propuse (s02) · qué salió (s03, tantas
como haga falta) · qué sigue (s04)**. Las dos tablas son las que sostienen la reunión, y la de
`Tasks for the next period` es la que después se convierte en los objetivos del período siguiente.

## 7. Cómo se construye un deck sobre esta plantilla

> Verificado el **26-ago-2026** leyendo el archivo con python-pptx. Nada de acá es inferido.

**El deck se RELLENA en sitio, no se reconstruye.** Invierte lo que hicieron los seis decks
anteriores, que abrían el template y le **borraban** las láminas para dibujar todo de cero
(`base_from_template()` de `generate_b8_deck.py:341`, con su `TPL_KEEP`). Con esta plantilla ese
camino cuesta más y sale peor: las tablas de s02 y s04 traen las filas de cuerpo **vacías pero ya
estilizadas** (relleno `1B4F8C` en la cabecera, bordes por celda, márgenes de 22860 EMU,
`anchor="ctr"`, 16 pt bold blanco), y reproducir eso a mano es trabajo perdido y una fuente de
diferencias contra el molde.

El esqueleto queda así:

```
abrir la plantilla
├── s01 portada     → se conserva TAL CUAL (titular de la empresa, no contenido nuestro)
├── s02 OBJECTIVES  → reescribir el título y rellenar la tabla, quitando las filas que sobren
├── s03 contenido   → clonar tantas veces como láminas de contenido, reescribir, y BORRAR
│                     el s03 original (trae el ejemplo de otra persona)
└── s04 Tasks       → reescribir el título y rellenar la tabla
reordenar el sldIdLst · forzar_barlow · auditar · guardar
```

Sigue en pie el motivo de siempre para abrir el `.pptx` en vez de usar `Presentation()`: la
plantilla **embebe Barlow** y un deck construido desde cero la pierde
([[deck-template-fuentes-embebidas]]).

### 7.a Las tres maniobras de python-pptx que esto exige

1. **Clonar s03.** De sus siete formas, **sólo la imagen tiene una relación** (`r:embed` del
   `a:blip`). Las otras seis (cejilla, título, cuerpo, la línea de remate, el **cuadro de pie
   vacío** del §5 y un `Text 2` también vacío) no referencian nada, así que se clonan con un
   `deepcopy` del XML a una lámina nueva del layout `DEFAULT` **sin copiar rels**. Si la
   figura va a ser nativa, la imagen no se clona y el problema de las relaciones no existe.
   **Ejecutado el 26-ago** en `clonar_s03()` de
   `sprints/B9_sprint9/presentacion_b9/generate_b9_deck.py`: funcionó tal cual.
2. **Quitar o agregar una fila de tabla**: sacar o insertar el `<a:tr>` y ajustarle la altura al
   `graphicFrame` por el `h` de esa fila. No hay API en python-pptx.
3. **Reordenar láminas**: mover el `sldId` dentro del `sldIdLst`. Tampoco hay API.

### 7.b Dos detalles que muerden al escribir

- El cuerpo de s03 usa `algn="just"` con **`spAutoFit`**, que python-pptx **no recalcula**: la
  altura guardada es la que dejó PowerPoint para el texto anterior. Fijarla midiendo el texto con
  los TTF de Barlow (`_face` / `text_w` / `wrap_lines` de `generate_b8_deck.py:708`) en vez de
  confiar en el autofit.
- El `Text 2` vacío de s03 está en L=0,41 T=1,41, **justo donde va el cuerpo**. Conviene no
  clonarlo.
- La portada trae un «—» en el titular de la empresa. Es copy ajeno y no se edita, así que
  cualquier barrido de rayas ([[deck-estilo-sin-rayas-ni-palanca]]) **tiene que excluir s01** o
  reporta un falso positivo en cada corrida.

### 7.c Tres restricciones que sólo aparecen al rellenarla de verdad

> Del primer deck construido sobre esta plantilla (`sprints/B9_sprint9/presentacion_b9/`,
> 26-ago-2026). El §7.a y el §7.b son el método; esto es lo que el método no anticipaba.

1. **El título de 40 pt en UNA línea es una restricción de redacción, no de formato.** La caja
   mide 12,44" con `lIns=0`, así que a 40 pt bold entran unos **46 caracteres** de Barlow. Un
   título descriptivo se pasa fácil: el de la segunda lámina de contenido pedía 14,07" y las
   dos salidas eran envolver a dos líneas encima del cuerpo, o bajar a 34 pt y romper el 40 pt
   del molde. **Se reformula el título.** Conviene que el generador **aborte** si no entra, en
   vez de dejarlo desbordar (`set_titulo()` lo hace).
2. **Con menos filas de las que trae el molde, la tabla hay que estirarla.** Las de s02 y s04
   traen **cuatro** filas de cuerpo. Con tres y el alto justo del texto, la tabla se encoge,
   queda pegada al título y deja media lámina vacía. Un alto mínimo de fila de **0,76"**
   conserva la huella original (0,745 + 3 × 0,76 = 3,03, que es el alto del molde).
3. **Las celdas de cuerpo son de 12 pt, centradas y con márgenes de 22860 EMU** (0,025" por
   lado), o sea **3,39" utilizables** en la columna `Objective` y **5,98"** en `Deliverable`.
   Medir contra el ancho de la columna sin descontar los márgenes deja celdas pegadas al
   filete ([[deck-qa-puntos-ciegos-chequeo]]).
