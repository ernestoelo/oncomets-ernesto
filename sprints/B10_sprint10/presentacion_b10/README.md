# Deck de la reunión del 15-sep — `[20260915] [Ernesto Gamero] [Detección Nuclear].pptx`

Deck del período 08/09 a 15/09 sobre la **plantilla oficial** (`docs/plantilla_oficial.md`), en
español salvo la portada, que es copy de la empresa. Siete láminas: qué se pidió, los tres
resultados, cinco preguntas y qué sigue. El contenido es el de
[`../reunion_martes.md`](../reunion_martes.md) §1-§5.

| | |
|---|---|
| Fuente de verdad | `generate_b10_deck.py`. El `.pptx` es derivado y está gitignored (`.gitignore:55`) |
| Guion | `guion_b10.md`, que el generador lee y aplica con `notes()`. El `.md` es la fuente |
| Datos | `datos_o1()` y `datos_o3()` de `scripts/b10_figuras_o1_o3.py`, más `results/b10_grado_sin_marca/{escalera.csv,nulo.npz}` para el pie de O1 |
| Molde | `papers/presentations/[AAAAMMDD] [Nombre Apellido] [Image-to-text].pptx`, read-only |
| QA geométrico | `qa_geometria.py` (§QA) |

## Regenerar

```bash
cd sprints/B10_sprint10/presentacion_b10
PYTHONPATH=/media/administrador/Storage1/sdonoso/clam_testing2/.pylibs \
  /home/sdonoso/miniconda3/envs/pruebas/bin/python generate_b10_deck.py
```

Sale con código 1 si algún auditor avisa, y aborta antes de dibujar si los datos no reproducen
los `resultados.md` o si no coinciden con `figuras/*.csv`. El deck **lee** esos CSV y no los
escribe: su único escritor sigue siendo `scripts/b10_figuras_o1_o3.py`.

Rasterizado (el `fonts.conf` está en `fonts/`, no en `fonts/barlow/`):

```bash
FONTCONFIG_FILE=/media/administrador/Storage1/sdonoso/clam_testing2/fonts/fonts.conf \
  soffice --headless --convert-to pdf --outdir <dir> "[20260915] [Ernesto Gamero] [Detección Nuclear].pptx"
pdftoppm -r 110 -png "<dir>/[20260915] [Ernesto Gamero] [Detección Nuclear].pdf" <dir>/r
```

## Estructura

```
s01  portada                                   TAL CUAL, sólo guion
s02  OBJETIVOS 08/09/2026 - 15/09/2026         tabla del molde, 3 filas, Cerrado el 09/09
s03  El tamaño solo reencuentra el alto grado  3 puntos + escalera O1 NATIVA (group shape)
s04  El CAP no cuenta núcleos: mide variación  2 puntos + diagrama O2 NATIVO (group shape)
s05  La atención cae sobre el CDIS ya visto    2 puntos + forest plot O3 NATIVO (group shape)
s06  Cinco preguntas para decidir cómo seguir  1 punto + tabla de 5 filas, celdas de 2 párrafos
s07  Tareas del próximo período                tabla del molde, 1 fila (min_h 1,0), fecha 22/09
```

## Decisiones

| | |
|---|---|
| De Ernesto, 11-sep | español salvo la portada · 7 láminas · gráficos con shapes y no `add_chart` · una fila de tareas |
| De Ernesto, 14-sep | O1 se queda en la lámina entera: no se re-corre confinado a la región anotada |
| La región mitótica | se dice sin nombrar a nadie, porque el dueño de esa línea es quien escucha: «quedó en la línea de mitosis con el reparto de la reunión pasada, y la necrosis sigue en espera» (cierra I1) |
| Defaults del plan | nombre de archivo, período, fecha 22/09 y el diseño lámina por lámina del handoff de la sesión 55 §5 |

## Qué se importa y qué es propio

Del generador del B9, que está cerrado y **no se edita**, se importan la medición con los TTF de
Barlow, las maniobras de la plantilla, el relleno en sitio y `auditar` / `barrer_rayas`. Es propio:

- **Tres figuras nativas, cada una en un group shape**, para que se escalen enteras. Polilíneas
  con `build_freeform(close=False)`, rectas con `add_connector` y punto hueco con relleno blanco.
  `convert_to_shape()` no recalcula la caja del grupo, así que cada figura cierra con
  `recalculate_extents()` (K2).
- **El texto de las figuras va en tinta o gris neutro**: `CUERPO` es también el color de «alto»
  en O1 y de «test» en O3 (K4).
- **Ningún símbolo va como carácter**: Barlow no trae `● ○ ▬ →` y `text_w()` no lo detecta (K1).
  La leyenda de O3 y la flecha de O2 van dibujadas.
- **`auditar_grupos()`**, que entra en los grupos y suma párrafos en las celdas (I2), y
  **`barrer_xml()`**, que barre el `.pptx` ya guardado: rayas, punto decimal, nombres y glifos
  fuera del cmap de Barlow.
- **`leer_guion()` desenvuelve los párrafos** (§QA, hallazgo 1).

## QA

| Capa | Resultado |
|---|---|
| Datos | `datos_o1()` y `datos_o3()` reproducen los `resultados.md`, y lo que devuelven coincide con `figuras/*.csv` (32 y 10 filas). `escalera.csv` da 21 láminas, 187 marcas, 145 alcanzables, 19 láminas en N = 5000 y bajo de 16 a 9 |
| Auditores del generador | los cuatro sin avisos, código 0 |
| Geometría dentro de los grupos (`qa_geometria.py`) | sin colisiones texto/texto, línea/texto ni forma/texto en O1 (34 textos, 60 segmentos), O2 (15, 7) ni O3 (37, 10) |
| Tinta por renglón | una corrección: el rótulo del eje de O2 quedaba a 0,03" de la punta de la flecha |
| Round-trip | 7 láminas en orden, notas en las 7 (1 a 6 párrafos), 301 `typeface="Barlow"` y ninguna otra tipografía en las láminas, 4 `.fntdata` en el paquete |
| Cruce de contenido | las 24 cadenas esperadas presentes (22 láminas · 145 de 187 · 41 de 76 · 12 de 53 · 0 de 16 · no pasa de 3 · 0,755 · 0,704 · 0,201 …) y ninguna de las prohibidas («20 láminas», «9 de 9», «evita el CDIS», precisión, F1, «otra persona») |
| **Mirar las láminas** | **PENDIENTE.** La sesión que lo construyó no pudo abrir imágenes: el hook que precede a `Read` no respondió en toda la sesión. Los rasterizados se le mandaron a Ernesto |

### Lo que encontró el QA

1. **Las notas salían partidas por renglón.** El `.md` va envuelto a cien columnas y `notes()`
   convierte cada `\n` en un párrafo: 17 a 23 párrafos por lámina para 3 a 6 de guion, cortados a
   mitad de frase. Lo cazó el round-trip contando párrafos. `leer_guion()` ahora junta las líneas
   de cada párrafo. **El deck del B9 tiene el mismo defecto**, medido sobre su `.pptx`: 11 a 22
   párrafos por lámina, 7 a 16 de ellos sin puntuación final. No se tocó, porque es un deck
   cerrado y ya presentado.
2. **Una premisa falsa en el guion de O1**: decía que los mm² eran la superficie de los núcleos, y
   son la de los parches que los contienen, que es lo que dice el eje
   ([[parametro-necesita-su-semantica]]).
3. **Costuras del guion**: tres láminas seguidas abrían con «La … pregunta era», la de preguntas
   decía «Cierro con» y detrás viene Tareas, la tabla escribe «set completo» y el guion decía
   «conjunto», y «ensemble» iba sin glosar. Corregidos.

`@humanizer-es` **no se corrió**: medido antes, el guion dio 1699 palabras, oración de 16,7 ± 7,8,
cero párrafos que abren con «Y», cero vocabulario del clúster, cero dígitos y cero rayas. Es el
criterio del ADDENDUM 19-ago de [[deck-qa-puntos-ciegos-chequeo]]: en prosa limpia, la capa de
estilo sobre-edita. La relectura en frío la hizo la sesión; **la lectura en voz alta es de
Ernesto**.

## Lo que el deck NO dice

- «20 láminas» (son 22), el «9 de 9» sin abrir por tier, ni que la B25-158899 «evita» el CDIS.
- Precisión, F1 o PQ: el patólogo marca ejemplares, no todos los núcleos de un grado.
- Los dos descriptores de O1 como dos resultados: dentro de una lámina, la razón contra el proxy
  es una transformación monótona del percentil.
- Nombres, números de job o de sprint, ni en el cuerpo ni en las notas.
