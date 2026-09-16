# Deck de la reunión del 15-sep — `[20260915] [Ernesto Gamero] [Detección Nuclear].pptx`

Deck del período 08/09 a 15/09 sobre la **plantilla oficial** (`docs/plantilla_oficial.md`), en
español salvo la portada, que es copy de la empresa. Once láminas: qué se pidió, qué detecta
HoVer-NeXt, los tres resultados con sus imágenes, cinco preguntas y qué sigue. El contenido es el
de [`../reunion_martes.md`](../reunion_martes.md) §1-§5; las cuatro láminas de imagen, de
[`plan_deck_visual.md`](plan_deck_visual.md).

| | |
|---|---|
| Fuente de verdad | `generate_b10_deck.py`. El `.pptx` es derivado y está gitignored (`.gitignore:55`) |
| Guion | `guion_b10.md`, que el generador lee y aplica con `notes()`. El `.md` es la fuente |
| Datos | `datos_o1()` y `datos_o3()` de `scripts/b10_figuras_o1_o3.py`, más `results/b10_grado_sin_marca/{escalera.csv,nulo.npz}` para el pie de O1 |
| Imágenes | `assets/`: 24 PNG y `deck_imagenes.json`, de `scripts/b10_deck_seleccion.py` (env `pruebas`, elige y verifica contra O1) y `scripts/b10_deck_imagenes.py` (env `clam_latest`, dibuja y verifica los tres AUC de O3). El generador cruza el JSON contra O1 y O3 antes de dibujar |
| Molde | `papers/presentations/[AAAAMMDD] [Nombre Apellido] [Image-to-text].pptx`, read-only |
| QA geométrico | `qa_geometria.py` (§QA) |

## Regenerar

Las imágenes, sólo si cambia la selección o el dibujo (22 s y ~100 s):

```bash
/home/sdonoso/miniconda3/envs/pruebas/bin/python scripts/b10_deck_seleccion.py
CUDA_VISIBLE_DEVICES="" /home/sdonoso/miniconda3/envs/clam_latest/bin/python scripts/b10_deck_imagenes.py
```

El deck:

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
s01  portada                                      TAL CUAL, sólo guion
s02  OBJETIVOS 08/09/2026 - 15/09/2026            tabla del molde, 3 filas, Cerrado el 09/09
s03  HoVer-NeXt encuentra y clasifica cada núcleo 1 punto + contexto 500 µm y centro 119 µm + leyenda con conteos
s04  El tamaño solo reencuentra el alto grado     3 puntos + escalera O1 NATIVA (group shape)
s05  La carga de N = 500 sobre dos láminas        2 puntos + miniatura y zoom por lámina, leyenda de símbolos
s06  Las marcas, núcleo a núcleo                  2 puntos + 12 paneles de 74 µm en dos filas por grado
s07  El CAP no cuenta núcleos: mide variación     2 puntos + diagrama O2 NATIVO (group shape)
s08  La atención cae sobre el CDIS ya visto       2 puntos + forest plot O3 NATIVO (group shape)
s09  Dónde mira la atención en tres láminas       2 puntos + mapa y zoom de 1,9 mm por lámina, leyenda turbo
s10  Cinco preguntas para decidir cómo seguir     1 punto + tabla de 5 filas, celdas de 2 párrafos
s11  Tareas del próximo período                   tabla del molde, 1 fila (min_h 1,0), fecha 22/09
```

Las cuatro de imagen (s03, s05, s06, s09) llevan todo lo que tiene letras o números nativo, y cada
figura en un group shape. Los marcadores del guion son `## [s01]` a `## [s11]`, por número de
lámina.

## Decisiones

| | |
|---|---|
| De Ernesto, 11-sep | español salvo la portada · 7 láminas · gráficos con shapes y no `add_chart` · una fila de tareas |
| De Ernesto, 14-sep | O1 se queda en la lámina entera: no se re-corre confinado a la región anotada |
| De Ernesto, 16-sep | **más visual**: se suman cuatro láminas de imagen (HoVer-NeXt, O1 sobre una lámina, O1 núcleo a núcleo, atención de O3) y el deck pasa a 11. Mismo período y mismo archivo. **Ejecutado** en las sesiones 61 (selección) y 62 (render, láminas, guion y QA). Lo que se decidió al ejecutar está en [`plan_deck_visual.md`](plan_deck_visual.md) §Estado de ejecución |
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
- **`cejilla()`**, que envuelve la del B9 y le saca al color del tema el aclarado del molde (§QA, 5).
- **`sin_efectos()`**, que anula la sombra del theme en las tres figuras, para PowerPoint y para
  LibreOffice (§QA, 6 y 7).
- **Las cuatro láminas de imagen** (`lamina_hovernext`, `lamina_o1_mapa`, `lamina_o1_galeria`,
  `lamina_o3_mapas`): un PNG por panel puesto con su aspecto exacto (`foto()`), las líneas de
  expansión desde el recuadro que guarda el JSON, y `leer_imagenes()`, que cruza ese JSON contra
  O1 y O3 antes de dibujar.

## QA

**Sesión 62, el deck de 11.** Imágenes: los gates de los dos scripts en verde (41 · 12 · 0,
76 · 53 · 16, ids de `pinst_pp`, marcas dentro de su zoom y los tres AUC de O3 iguales a 1e-9).
Generador: código 0, los cuatro auditores sin avisos, y el JSON de imágenes cruzado contra O1 y O3.
Round-trip: 11 láminas en orden, notas en las 11 (1 a 6 párrafos), 441 `typeface="Barlow"` y
ninguna otra, 4 `.fntdata`, las 26 cadenas esperadas de las láminas nuevas presentes, «mitosis»
sólo en la cita del CAP de s07 y ningún dígito ni identificador de lámina en los bloques nuevos
del guion. `qa_geometria.py` sin colisiones en las once (O1, O2 y O3 con los mismos conteos de la
sesión 59). **Se miraron las once a 110 dpi**: cuatro correcciones antes de dar el deck por hecho,
en `auditoria_coherencia/hallazgos.md`, sesión 62. `@humanizer-es` corrió sobre los párrafos
nuevos; la lectura en voz alta es de Ernesto.

La tabla de abajo es la del deck de 7 (sesión 59), y sigue valiendo para esas siete láminas.

| Capa | Resultado |
|---|---|
| Datos | `datos_o1()` y `datos_o3()` reproducen los `resultados.md`, y lo que devuelven coincide con `figuras/*.csv` (32 y 10 filas). `escalera.csv` da 21 láminas, 187 marcas, 145 alcanzables, 19 láminas en N = 5000 y bajo de 16 a 9 |
| Auditores del generador | los cuatro sin avisos, código 0 |
| Geometría dentro de los grupos (`qa_geometria.py`) | sin colisiones texto/texto, línea/texto ni forma/texto en O1 (34 textos, 60 segmentos), O2 (15, 7) ni O3 (37, 10) |
| Tinta por renglón | tres correcciones: el rótulo del eje de O2 a 0,03" de la punta de la flecha, los números del eje x de O1 a 0,018" de sus ticks y los dos renglones de «parches con CDIS» a 0,009". Después, el hueco mínimo de cada lámina es interlineado normal |
| Solapes de primer nivel | ninguno entre cuerpo, figura, tabla y pie; la tinta de las siete cae dentro del área del molde |
| Round-trip | 7 láminas en orden, notas en las 7 (1 a 6 párrafos), 301 `typeface="Barlow"` y ninguna otra tipografía en las láminas, 4 `.fntdata` en el paquete |
| Cruce de contenido | las 24 cadenas esperadas presentes (22 láminas · 145 de 187 · 41 de 76 · 12 de 53 · 0 de 16 · no pasa de 3 · 0,755 · 0,704 · 0,201 …) y ninguna de las prohibidas («20 láminas», «9 de 9», «evita el CDIS», precisión, F1, «otra persona») |
| **Mirar las láminas** | Sesión 59, a 110 dpi y midiendo a 300 dpi lo sospechoso: seis defectos corregidos (5 a 10 abajo). Después, 0 formas con `effectRef` distinto de 0 y `qa_geometria.py` sin colisiones |

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
3. **La tinta por renglón no se lee sin la columna.** Mide filas completas del rasterizado, así
   que junta objetos que están en la misma altura y lejos entre sí: el hueco mínimo de O3 (0,009")
   es entre dos rótulos separados por cuatro pulgadas. `qa_geometria.py` imprime la extensión
   horizontal de cada banda por eso.
4. **Costuras del guion**: tres láminas seguidas abrían con «La … pregunta era», la de preguntas
   decía «Cierro con» y detrás viene Tareas, la tabla escribe «set completo» y el guion decía
   «conjunto», y «ensemble» iba sin glosar. Corregidos.
5. **La cejilla de s02 y s07 salía `#97BEEB`**, no `5293DE`: en el molde el tema de esas láminas
   viene aclarado con `lumMod`/`lumOff`, y `set_cejilla()` del B9 cambia el `val` sin sacarlos.
   `cejilla()` los saca. El `.pptx` del B9 lo tiene en s2 y s13.
6. **35 conectores con la sombra del theme**, cuyas tres `effectStyle` traen `outerShdw`: `recta()`
   era la única primitiva sin `shadow.inherit = False`.
7. **El rasterizado no mostraba el arreglo de 6**: LibreOffice dibuja la sombra del theme aunque la
   forma traiga `<a:effectLst/>` vacío, así que el PDF y el QA tenían sombra en las 115 formas de
   las figuras. `sin_efectos()` pone `effectRef idx="0"` en los tres grupos. Lo separó una copia
   con los `effectRef` en 0: la grilla pasó de ~20 px de cola a 4 px.
8. **«seis rasgos y un solo corte numérico»** se leía contra un eje que dibuja dos cortes. Dice
   ahora «seis rasgos, y solo el tamaño tiene corte numérico», como el guion.
9. **El pie de O3 dejaba «anotada.» sola en un renglón.** Unidad y AUC van en dos párrafos, con los
   mismos tres renglones.
10. **O1**: el título del eje y el titular de N = 500 quedaban a 0,04" de la línea del 100 % y la
    leyenda tapaba media línea. La banda de cabecera pasa de 0,40 a 0,44, y la leyenda baja y
    lleva filete del color de la grilla, porque sin sombra quedaba sin marco y la línea del 75 %
    parecía cortada. Queda a 0,08" del 100 % y a 0,09" del 50 %.

Lo descartado al medir está en `auditoria_coherencia/hallazgos.md`, sesión 59.

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
