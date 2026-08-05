# Presentación B8 — dos ejes, y una sección de cierre

> Construida el **30-jul-2026** como monográfico de SI-MIL. **Rehecha el 3-ago-2026** a
> pedido de Ernesto: SI-MIL se compacta **a la mitad** y entra la medición de atención
> contra las marcas del patólogo, en registro **muy pedagógico**.
>
> **Ampliada el 4-ago-2026**: el grid E×S entra como **sección de cierre** después de los dos
> ejes (opción (b) de las tres que planteaba el handoff, elegida por Ernesto). La lámina del
> mapa del recorrido **no se toca** y el deck sigue siendo de dos ejes; el grid se cuenta como
> «lo que además cerró este sprint». Tres láminas, de 17 a **20**.
>
> Reunión: **viernes 07/08/2026**. `FECHA_REUNION` del generador ya la tiene.

## Qué hay acá

| Archivo | Qué es |
|---|---|
| `generate_b8_deck.py` | genera el deck end-to-end; se corre y reproduce el `.pptx` |
| `prep_assets_atencion.py` | recorta las figuras de `atencion_vs_patologo/` para proyectar |
| `CLAM_Sprint8.pptx` | el deck, **20 láminas**, 13.333 × 7.5 |
| `assets/simil_fig2_{full,a,b,c}.png` | Fig. 2 del paper, recortada de la pág. 4 a 400 DPI |
| `assets/atencion_dos_regiones.png` | los 4 paneles (atención \| marcas) × (región 1 \| región 2) |
| `assets/mitosis_region_anotada.png` | la región anotada, con el recuadro del detalle |
| `assets/mitosis_zoom.png` | el detalle: los parches de mitosis sobre el rojo |

```bash
PYTHONPATH=/media/administrador/Storage1/sdonoso/clam_testing2/.pylibs \
/home/sdonoso/miniconda3/envs/clam_latest/bin/python \
  sprints/B8_sprint8/presentacion_b8/prep_assets_atencion.py     # solo si cambian las figuras
PYTHONPATH=/media/administrador/Storage1/sdonoso/clam_testing2/.pylibs \
/home/sdonoso/miniconda3/envs/clam_latest/bin/python \
  sprints/B8_sprint8/presentacion_b8/generate_b8_deck.py
```

> El generador **borra `CLAM_Sprint8_SIMIL.pptx`** si lo encuentra: es el nombre previo,
> de cuando el deck era monográfico, y dejarlo al lado del nuevo solo genera confusión.
> Ningún `.pptx` está versionado.

## Estructura (20 láminas)

| # | Lámina | Eje |
|---|---|---|
| 1-2 | portada y lámina de título | heredadas del template |
| 3 | dos cosas, y una cambia el plan | mapa del recorrido |
| 4 | SI-MIL: qué propone, y su arquitectura (Fig. 2) | SI-MIL |
| 5 | dos descripciones del mismo parche, y la ecuación 1 | SI-MIL |
| 6 | ecuación 2: el orden de dos operaciones | SI-MIL |
| 7 | el puente, y la rama que sí se lee | SI-MIL |
| 8 | las ecuaciones 3 a 10, en panorama | SI-MIL |
| 9 | qué reportan, qué costaría, y qué preguntar | SI-MIL |
| 10 | la observación del patólogo, convertida en pregunta medible | atención |
| 11 | qué se mide exactamente: un ranking, no un mapa | atención |
| 12 | los dos mapas, sobre la misma lámina | atención |
| 13 | el resultado: la escalera de los siete grupos | atención |
| 14 | los 28 parches de mitosis, sobre el mapa | atención |
| 15 | el hallazgo: mira bien y responde mal | atención |
| 16 | por qué esto no es una casualidad | atención |
| 17 | qué mueve esto en lo que viene | atención |
| 18 | el encargo de julio: ¿recortar expertos o slots? | grid E×S |
| 19 | cuánto cuesta sacar capacidad, rama por rama | grid E×S |
| 20 | el pipeline es determinista | grid E×S |

## La sección de cierre del grid E×S (láminas 18 a 20)

Todo sale de `../grid_expertos_slots/{prereg.md,resultados.md}`, encargo 3 del B8. **Nada se
re-mide**: el job cerró el 4-ago con 40 de 40 runs. Los números se transcribieron a las
constantes `PELDANOS`, `RAMA_S` y `RAMA_E` del generador, contra los §4 y §6 del
`resultados.md`.

**Por qué va al final y no como tercer eje.** De las tres opciones que planteaba el handoff,
Ernesto eligió la (b). El hallazgo que cambia el plan es el de atención, no el grid, y el deck
ya venía largo: meterlo como tercer eje obligaba a rehacer la lámina del mapa del recorrido,
cuya tira de dos tarjetas está **calculada** (`bw = (9.28 - 0.34) / 2`), y a reescribir su
guion. Como sección de cierre, la lámina 3 queda intacta y el grid se presenta por lo que es.

### Las dos reglas que vienen del pre-registro

1. **El veredicto es H_nula y la lámina lo dice como tal.** El +0,022 del primer peldaño es
   justamente lo que **no** alcanza, y venderlo como hallazgo contradiría el pre-registro. Por
   eso el mensaje visual de la lámina 18 no es la magnitud del Δ sino que **el signo se cambia
   de lado entre peldaños** y que el bigote de la desviación cruza el cero en los tres.
2. **Cero Δ contra CLAM por brazo.** El prereg §6 lo prohibió por diseño para no disparar ocho
   veces sobre el eje ya cerrado del Hallazgo 12, y encima sobre la tarea del dato abierto.
   CLAM **no aparece** en ninguna de las tres láminas, ni siquiera como fila de escala: el §8
   del `resultados.md` la tiene y con eso alcanza para el documento.

### Las dos figuras nativas nuevas

- **`barras_divergentes()`** (lámina 18): Δ pareado alrededor del cero, con la desviación como
  bigote y un cuadro por fold. La barra de la media se dibuja **encima** del bigote, y la
  banda del peldaño resaltado va **primero**, porque dibujada después taparía el cero, el
  bigote y los cuadros de esa fila. Un Δ de dos milésimas se dibujaría de ancho cero, así que
  hay un ancho mínimo de 0,03".
- **`escalera_capacidad()`** (lámina 19): AUC medio por brazo con la línea que une los topes.
  El eje arranca en **0,75**, rotulado en la lámina: entre el mejor y el peor brazo hay 0,055
  de AUC y a escala completa los ocho serían la misma barra.

### Lo que la sección declara que NO dice

La lámina 20 lleva su propio límite escrito: el determinismo está medido **en esta GPU y con
este entorno**, y entre máquinas distintas no se probó. Y su panel de la derecha deja la
consecuencia incómoda a la vista, que es la que toca un pendiente real: el control **no**
replicó el resultado del sprint pasado y **no podía**, porque compartía la semilla.

## El recorte de SI-MIL del 3-ago (12 láminas de contenido a 6)

Pedido textual: *«compactando y resumiendo a la mitad las slides actuales de SI-MIL, que
fue una de las tareas de investigación»*. O sea **no se borra**. Es una precisión de la
decisión del 31-jul, que leída sola autorizaba a eliminarlo entero.

Método, el mismo del recorte anterior: se fusionan pares y **lo que sale de la lámina se
cuenta hablando**, con el guion **reescrito**, no pegado.

| Antes (12) | Ahora (6) | Qué se fue al guion |
|---|---|---|
| qué propone + la Fig. 2 | **una** | las 3 tarjetas de consecuencias y la fila de cifras del paper |
| las dos entradas + ecuación 1 | **una** | los tres paneles de glosa de la ecuación (bolsa, proyector, atención) |
| ecuación 2 + qué implica para nuestro modelo | **una** | la tabla de mapeo línea por línea contra `model_clam.py` y el panel de la atención sin signo, que pasa al remate |
| el puente Top-K + la rama interpretable | **una** | el panel del gradiente de la selección y el de por qué se gira la matriz |
| las ecuaciones 3 a 10 | **una** | sin cambios |
| qué reportan + qué costaría + qué preguntar | **una** | la tabla de contraste con lo nuestro y 2 de las 4 preguntas |

Ningún número del paper ni nuestro se fue con las fusiones: lo que salió son glosas y
tablas ilustrativas.

## La sección de atención (láminas 10 a 17)

Todo sale de `../atencion_vs_patologo/{prereg.md,resultados.md,auc_por_checkpoint.csv}`.
**Nada se re-mide**: el experimento cerró el 2-ago, corrida confinada incluida. Los siete
AUC de la escalera se verificaron contra el CSV antes de escribirlos (4 checkpoints
primarios, cabeza de la clase verdadera).

El argumento entra en el orden que fija la memoria `deck-b8-dos-ejes-simil-mitosis`:

1. **El estadístico es el AUC de ranking**, no el mapa de calor, que fue el subproducto.
   Va en su propia lámina y con su propia figura (lámina 11), porque el número sin dibujo
   es exactamente lo que no se retuvo cuando se hizo la medición.
2. **0,890 ± 0,039**, percentil mediano 91, el mejor de los siete grupos, con la escalera
   completa hasta grasa 0,154 (lámina 13, barras nativas).
3. **Los cuatro controles**, con el nulo por traslación rígida al frente (lámina 16).
4. **Mira bien y responde mal** (lámina 15).
5. **La consecuencia sobre las cuatro familias**, que es por qué la búsqueda de papers
   apuntó a B, C y D (lámina 17).

### La leyenda obligatoria de las figuras

Las dos figuras muestran el tejido **dos veces**, porque el `.bif` tiene dos regiones de
escaneo y el pipeline extrajo parches de las dos (2303 arriba, 2496 abajo; las 163
anotaciones caen **todas** abajo). En una lámina proyectada, sin explicación, eso se lee
como un defecto de la figura. La lámina 12 lleva el panel que lo explica **y** el dato de
que se midió y se descartó el efecto de región (0,462 a 0,478, o sea que la región anotada
recibe *algo menos* de atención). Hallazgo **F4** de la sexta pasada de la auditoría.

### Lo que la sección declara que NO dice

Una lámina y un anotador **describen, no establecen**; está pre-registrado así y la lámina
16 lo dice. Grado nuclear **no entra a la par de mitosis**: da 0,828 pero solo 1 de 4
checkpoints baja de p = 0,05, y aparece únicamente como advertencia hablada sobre la
escalera. Las clases de contraste **no son control negativo**.

## Decisiones de construcción

### 1. Las figuras de atención van como imagen, y es legítimo

La convención pide **todo nativo** salvo figuras de paper. Estas no son de un paper: son
producción nuestra, y son mapas de una lámina real, que no se pueden redibujar con shapes.
Van como imagen; las tablas y la escalera que las acompañan van **nativas**.

### 2. Por qué las figuras se recortan antes de entrar

Se generaron para archivo, no para proyectar: traen los títulos de matplotlib y un hueco
de ~390 px entre las dos regiones de escaneo. Puestas tal cual, el tejido queda del tamaño
de una moneda. `prep_assets_atencion.py` las recompone **sin alterar el contenido**, y
conserva las dos regiones en la figura de los mapas, porque esconder una sería esconder
justo lo que la leyenda tiene que explicar.

Gotcha del detector del zoom: buscar los parches de mitosis por «blanco puro» **no
funciona**, porque el fondo del lienzo también es casi blanco y aporta 27 000 píxeles de
ruido. Lo que los distingue es la **vecindad saturada**: son los únicos blancos rodeados
de mapa de calor. Con eso salen 11 grupos limpios.

### 3. Las cajas de imagen se dimensionan con la relación de aspecto exacta

`add_image_fit` centra la imagen dentro de su caja. Si la caja no tiene la relación de
aspecto de la figura, sobra aire a los costados y los rótulos de columna quedan corridos
respecto de lo que rotulan. Pasó en la primera pasada de la lámina 12. Se corrige fijando
`h = w / ar` en vez de elegir los dos valores a ojo.

### 4. Las tiras de paneles se igualan en alto después de dibujarlas

`panel(..., h=None)` calcula su propio alto midiendo el texto, así que una tira de cuatro
sale dentada. Se igualan al más alto **después**, con `sp.height = Inches(alto_max)`: el
texto está anclado arriba, así que alargar la caja no mueve nada. Y el bloque siguiente se
posiciona desde ese alto medido, no desde una constante.

### 5. Tipografía de las ecuaciones: Barlow con fallback, NO Cambria Math

Barlow **no trae griegas** (`α β ψ γ λ Σ`) ni `ℝ ∈ → ⊗`, y este deck es de ecuaciones. El
template embebe Barlow **y Cambria Math**, así que declarar Cambria Math era una opción
real. **Se rasterizaron las dos y se miró:** gana Barlow con el fallback del sistema, cuyas
griegas salen en un sans de peso parecido, mientras que las de Cambria Math son serif finas
y contrastan con el Barlow que las rodea. `pdffonts` lista `Barlow-Bold` y `Barlow-Regular`
embebidos más `DejaVuSans`, que es ese fallback y **no es un defecto**.

### 6. Subíndices y superíndices REALES

`_add_runs()` emite runs con `baseline` OOXML: `_x` / `_(xx)` subíndice, `^x` / `^(xx)`
superíndice. Hace falta porque Unicode no tiene subíndice para casi ninguna letra.

**Gotcha:** en un shape con `markup=True` el `_` de `model_clam.py` se interpreta como
subíndice y el archivo queda escrito «model_lam.py». Se escapa con `model\\_clam.py`. Por
eso los `score_2` / `score_3` de la sección de atención van en tablas y textboxes **sin**
markup, donde el guión bajo es literal.

**Gotcha inverso, y es silencioso:** `_x` baja **un solo carácter**. Un subíndice de dos o más
escrito sin paréntesis no falla ni avisa, simplemente sale a medias: `L_CE` baja la C y deja la
E a tamaño completo («L꜀E»). Para dos o más va siempre `_(CE)`. Cazado el 4-ago en la ecuación
10, que llevaba `L_CE` y `L_KD`.

### 7. Los paneles se dimensionan midiendo el texto

`text_w()` mide con los TTF de Barlow instalados bajo containment, `wrap_lines()` cuenta
las líneas reales, y `panel(..., h=None)` calcula su alto. `auditar(prs)` corre antes del
escalado y avisa de texto que no entra, shapes fuera del lienzo y cuerpos por debajo del
mínimo del template (7 pt). **No reemplaza mirar las láminas**, y de hecho las cuatro
correcciones de layout de esta pasada salieron de mirarlas con la auditoría en cero.

Volvió a pasar con la sección del grid el 4-ago: **auditoría en cero y tres defectos a la
vista**. Los tres son de una clase que ningún chequeo de cajas puede ver, porque no hay texto
fuera de su caja ni shape fuera del lienzo, sino **dos objetos válidos superpuestos**.

| Defecto | Por qué la auditoría no lo ve | Fix |
|---|---|---|
| La línea de tendencia cruzaba los rótulos de valor de la lámina 19 | el rótulo entra perfecto en su caja; lo que lo tapa es un conector | el valor se dibuja **dentro** de la barra, en blanco |
| Los paneles de la lámina 20 chocaban con la regla de `takeaway_bar` | el panel se auto-dimensiona y queda dentro del lienzo, y la regla está en su sitio | subir el bloque 0,10" y bajar los cuerpos de 3 líneas a 2 |
| El pie de la lámina 18 no decía qué significaba el relleno de los cuadros | es una omisión de contenido, no de layout | se completó la leyenda |

Y volvió a pasar la noche del 4-ago, en la primera pasada que miró **las 20 de una sentada** y
leyó el guion **de corrido**: auditoría en cero y **seis defectos**. El reparto es el hallazgo,
más que los defectos:

| Láminas | Cuándo se escribieron | Defectos |
|---|---|---|
| 4 a 9 (SI-MIL) | 30-jul, recortadas el 3-ago | 2 |
| 10 a 17 (atención) | 3-ago | 4 |
| **18 a 20 (grid)** | **4-ago, ya miradas** | **0** |

**Al ampliar un deck, el QA de las láminas nuevas es el barato y se hace solo. El que paga es
releer lo que ya estaba**, porque lo viejo acumula la deriva de las convenciones que llegaron
después, las promesas de continuidad que la ampliación invalidó, y los choques de números entre
láminas que antes no eran vecinas. Ninguno se ve mirando la lámina sola.

| Defecto | Por qué la auditoría no lo ve | Fix |
|---|---|---|
| Los 7 valores de la escalera de la lámina 13 salían con **punto** decimal, junto a su propio `0,890 ± 0,039` y `azar = 0,5` | `_num()` llegó con las figuras del grid y `barras_ranking()`, de la tanda anterior, siguió con `"%.3f"`. No es layout | `barras_ranking` pasa a `_num()`; y el barrido `\d+\.\d+` sobre el deck entero queda como chequeo |
| Ecuación 10: `L_CE` / `L_KD` bajaban solo la C y la K («L꜀E») | el subíndice `_x` es de UN carácter; el resultado es texto válido en su caja | `L_(CE)` / `L_(KD)` |
| La lámina 17 remataba con «Es la parte que sigue», apuntando a los papers, y detrás quedó el grid | es de arco: exige saber qué viene después | «Los traigo aparte, en las hojas que preparé para hoy»; y abre con «Termino esta parte con…» para no repetir el «Cierro con» de la 18 |
| La 15 decía «26 mitosis marcadas» al lado de la 13 y la 14, que dicen 28 parches | los dos números son correctos y salen del mismo `resultados.md`; chocan solo por ser vecinos | «26 **marcas** de mitosis»: se nombra la unidad, no se cambia el número |
| Guion de la 9: «la exactitud pasa de **nueve coma tres siete**» por 0,937 | las notas no se auditan, y leído suena a una exactitud de 9,37 | «cero coma nueve tres siete», y los otros tres números de la frase |
| Guion de la 12: «cero coma cuatro seis y cero coma **cuarenta y ocho**» | dos formas de decir el número en la misma frase | «cuatro seis» y «cuatro ocho» |

Ningún número cambió y no se tocaron el `prereg.md` ni el `resultados.md` de ninguno de los dos
experimentos. Detalle: `../auditoria_coherencia/hallazgos.md`, **décima pasada**.

### 8. Extracción de la Fig. 2 del paper

`pdftoppm -f 4 -l 4 -r 400` sobre el PDF y recorte por perfil de contenido. Es la **única
imagen de paper** del deck.

## Rediseño pedido el 4-ago (17:30) — EJECUTADO el 4-ago (20:00)

Ernesto revisó el deck construido y pidió doce cambios. **Los doce están ejecutados**, más los
dos transversales de títulos y notas. El deck sigue en **20 láminas**, regenera limpio y la
auditoría da cero avisos; **ningún número cambió** y ni el `prereg.md` ni el `resultados.md` de
los dos experimentos se tocaron.

> La tabla de abajo es la estructura **destino**, que ahora es la vigente. La sección
> «Estructura (20 láminas)» del principio de este README describe el deck **anterior al
> rediseño** y quedó stale: los títulos y el reparto de las dos puntas cambiaron.

### Lo que quedó sin hacer

- ~~**QA visual de nueve láminas tocadas**: 9, 10, 11, 13, 14, 15, 17, 18 y 19.~~ **HECHO el
  4-ago a las 22:00**, ver §«El QA de las nueve» abajo.
- ~~**El guion sin pasar por `@humanizer-es`**.~~ **HECHO el 4-ago a las 22:30**, ver
  §«La pasada de `@humanizer-es`» abajo. **Queda la lectura EN VOZ ALTA**: se verificaron
  los números en letras uno por uno, falta leer las 19 de corrido.
- **Un defecto que no es del deck**: la leyenda de la figura de marcas de la lámina 12 mezcla
  español e inglés («Immune cells», «Stroma», «Nucleos» sin tilde). Sale de la figura de
  `../atencion_vs_patologo/`, así que arreglarlo es regenerar esa figura, no tocar el generador.

### El QA de las nueve (4-ago, 22:00)

Un defecto real de nueve láminas, y era la **17**. El deck sigue en 20 láminas, **ningún número
cambió**, y ni los `prereg.md` ni los `resultados.md` se tocaron.

| Lámina | Qué se miró | Resultado |
|---|---|---|
| **17** | los rótulos de lado de `barras_divergentes` | **defecto**: se dibujan en `t − 0,34` y caían sobre el renglón de dataset de 9 pt. Se leía «5 particiones» tachado |
| 9 | la tabla agrandada a `row_h=0,50`, `fs=13` | limpia, sin desborde |
| 15 | dos paneles menos y remate más abajo | limpia |
| 18 | la polilínea de las dos escaleras | **falsa alarma**: a 100 dpi parecía arrancar en la esquina de la primera barra; arranca en el centro |
| 14 | el pie «la región anotada» | correcto: el asset ya viene recortado a esa región |
| 10, 11, 13, 19 | layout y contenido | limpias |

**El fix de la 17**: la figura baja a `TOP + 1,06` y **cede 0,10" de alto** para pagarlo, así que
el remate y todo lo de abajo quedan donde estaban. La lección durable, que una figura puede
dibujar por encima de su propio `t` y el que la llama no lo sabe, está en la memoria de puntos
ciegos del QA.

**El método que lo verificó**, y que conviene reusar: medir **tinta por renglón** sobre el PNG
(`(im < 200).sum(axis=1)`) y listar las bandas. Antes de arreglarlo, una sola banda de 25 px con
el renglón y los rótulos fundidos; después, dos bandas de 15 y 16 px con 24 px limpios entre
medio. Distingue la colisión real del solape nominal de cajas (el chequeo de solapes reportaba
tres en esa lámina y solo uno era real) y no gasta presupuesto de imágenes. **No reemplaza
mirar.**

**Barrido de reglas duras sobre las 20 láminas, cuerpo y notas**: cero `\d+\.\d+`, cero `—`,
cero letras A/B/C/D.

### Los cuatro helpers nuevos

Van todos después de `escalera_capacidad()`, que es donde termina el bloque de figuras nativas.

| Helper | Para qué | Detalle que importa |
|---|---|---|
| `pie_lineas` | las tres líneas de procedencia de la 12 | un solo textbox: `caption` gasta 0,4" por renglón y tres renglones se comen la figura |
| `escala_auc` | el estadístico de la 11, que era un panel de texto | barra de 0 a 1 + azar punteado + la marca del valor |
| `_mancha` / `_RACIMO` | el racimo de parches de la 16 | «hueco» se dibuja con relleno **blanco**, no con `fill.background()` |
| `nube_traslaciones` | la distribución del nulo de la 16 | la banda es el **rango medido**; el jitter usa `_lcg`, semilla fija, para no cambiar entre regeneradas |

### Estructura destino (sigue en 20 láminas)

| # | Lámina | Qué cambia |
|---|---|---|
| 3 | **Objetivos del sprint** | reemplaza «dos cosas, y una cambia el plan»; molde de recapitulación del B6/B7 (título 32 pt, lista numerada, marcador de estado) |
| 9 | resultados y costo de adopción | menos renglones, sintética alrededor de la tabla |
| 10 | la pregunta medible | los rótulos «si tuviera razón» / «si no la tuviera» pasan a hipótesis primaria y alternativa |
| 11 | el estadístico | el renglón que define el número se vuelve figura |
| 12 | atención y marcas | figuras al doble, sin panel de texto, con la procedencia |
| 13 | la escalera | solo el guion, más pedagógico |
| 14 | los 28 parches | «lo que se ve» a una línea; guion pedagógico |
| 15 | mira bien y responde mal | se conserva la tabla, una sola lectura sintética |
| 16 | por qué el resultado aguanta | rehecha: el nulo por traslación pasa a ser la figura |
| 17-18 | el grid | sin «el encargo de julio»; se nombra el dataset |
| ~~19~~ | ~~el determinismo~~ | **se borra**; la sección cierra en la escalera de capacidad |
| 19 | **los tres papers** | hereda la lámina de las cuatro familias, sin las letras A/B/C/D |
| 20 | **objetivos propuestos** | nueva |

Y dos pedidos transversales: **todos los títulos** a minimalistas, precisos y profesionales, y
**todas las notas** con un punteo guía arriba antes de la prosa hablada.

### El asset de la lámina 12

`prep_assets_atencion.py` emite `assets/atencion_region_anotada.png` (1502 × 624, relación de
aspecto **2,407**), que es solo la región anotada, atención y marcas. La grilla 2×2 anterior
arrastraba la fila de la región sin marcas, cuyo panel de anotaciones es tejido pelado y se lee
como la misma imagen dos veces; ese es exactamente el defecto que Ernesto marcó. Esa fila no
aporta, porque las 163 marcas caen todas en la otra región y el efecto de región ya está medido
y descartado.

**La lámina 12 ya lo adopta**, con la caja recalculada (`add_image_fit` usa `h = w / ar`, y la
relación pasó de 1,183 a 2,407): `w = 8,10 → h = 3,37`, centrada en `l = 0,95`, con las tres
líneas de `PROVENANCIA` al pie a 8 pt. `FIG_MAPAS` sigue declarado apuntando a la grilla vieja,
que ya **no se usa en ninguna lámina**. Las constantes `PROVENANCIA`, `PAPERS` y `OBJETIVOS`
están las tres en uso.

### La procedencia, que es lo que preguntó Sebastián

Verificada de punta a punta el 4-ago. La lámina es **129741** de la cohorte privada, H&E Ventana
`.bif` a 20× (0,465 µm/px), bajo `wsi/129741/`; las marcas son
`hover_net/129741.bif - GDT.geojson`, 61 polígonos de QuPath (26 mitosis, 14 núcleos de alto
grado, 6 necrosis, 5 células inmunes, 5 tumor, 2 adiposo, 1 estroma, 2 fondo); y sus etiquetas
en nuestros CSV son tasa mitótica `score_3`, pleomorfismo nuclear `score_2`, diferenciación
tubular `score_3`, grado general `grado_3` y grado nuclear del CDIS `grado_3_alto`.

**Y una corrección que el rediseño tiene que llevar**: el deck dice «checkpoints que NUNCA
vieron esta lámina» y eso se pasa de lo que sostienen el `prereg.md` y el `resultados.md`, que
dicen «nunca se vio **en entrenamiento**». En los cuatro primarios la lámina está en
**validación**, que gobierna el early stopping. Se corrobora con la fila `129741` de los
`splits_*_bool.csv`: `False,True,False` en los dos single-split, y val en los folds 0 y 2 de la
corrida de cinco. Sus datasets de entrenamiento son 153 láminas (privado), 978 (privado + TCGA)
y 934 (privado + TCGA, cinco particiones).

### Preparado para ejecutarlo (sesión del 4-ago, 19:00)

Sesión de lectura y plan, **sin editar el generador**. Lo que queda escrito acá es lo que la
sesión de ejecución necesitaría volver a derivar.

**Numeración**: la «lámina N» de los pedidos de Ernesto es el comentario `# ---- N-1 ----` del
`build()`, porque las dos láminas de apertura salen del template y no llevan comentario. Así,
la 3 es el `# ---- 2.`, la 12 es el `# ---- 11.` y la 20 que se borra es el `# ---- 19.`.

**Cuál hipótesis es la primaria, que el punto 3 puede invertir.** Verificado contra
`../atencion_vs_patologo/prereg.md` §2: la **primaria es la del patólogo**, o sea que los
parches marcados **no** rankean mejor que el azar. Entonces el rótulo «Si tuviera razón» pasa a
**hipótesis primaria** y «Si no la tuviera» a **alternativa**, y lo que el resultado apoyó fue
la **alternativa**. Cambiarlos de lado convertiría la lámina en una tergiversación del
pre-registro, que es justo lo que el rótulo profesional tiene que evitar.

**La caja de la lámina 12, con la cuenta hecha.** `atencion_region_anotada.png` mide
1502 × 624, o sea **ar = 2,407**, y `add_image_fit` impone `h = w / ar`. Con las tres líneas de
`PROVENANCIA` al pie (8 pt, interlineado mínimo, unas 0,49") el ancho tiene tope: **w ≈ 8,10 →
h ≈ 3,37**, imagen desde `TOP + 0,28` y pie desde ≈ 4,92. Cada panel queda en ≈ 4,05" contra
los 2,17" de la grilla 2×2 actual, que es el «al doble» que pidió. `caption` no sirve de pie
acá, porque gasta 0,4" por renglón.

**Títulos propuestos** para el pedido transversal, a confirmar al ejecutar: 3 Objetivos del
sprint · 4 SI-MIL: qué propone · 5 Ecuación 1: las dos entradas · 6 Ecuación 2: el orden ·
7 El puente entre las dos ramas · 8 Ecuaciones 3 a 10 · 9 Resultados y costo de adopción ·
10 La pregunta medible · 11 El estadístico: un ranking, no un mapa · 12 Atención y marcas del
patólogo · 13 El resultado, grupo por grupo · 14 Los 28 parches de mitosis · 15 Mira bien y
responde mal · 16 Los cuatro controles · 17 ¿Recortar expertos o slots? · 18 El costo de sacar
capacidad · 19 Tres papers para la rama de mitosis · 20 Objetivos propuestos.

## Guion del presentador

Prosa hablada corrida, sin etiquetas de fase, en primera persona
([[notas-presentador-guion-didactico]]). Sin números de job ni nombres propios: los
checkpoints se rotulan por su cohorte («privado», «privado + TCGA», «5 folds, fold 0»).

Los guiones de las seis láminas fusionadas de SI-MIL se **reescribieron**, no se pegaron, y
absorbieron lo que salió de las láminas. Los ocho de la sección de atención se escribieron
de cero para este deck.

### La pasada de `@humanizer-es` (4-ago, 22:30)

Loop de 4 pasos sobre las **19 láminas con notas**, con el alcance acotado a la **prosa
hablada**: los punteos guía, los títulos, los rótulos de figura y los remates de lámina
**no se tocaron** (son pedido explícito de Ernesto del rediseño). **16 ediciones**, de
7112 a **7028 palabras**, un **−1,2 %** casi calcado del −1,1 % del guion del B7, que es
la señal de que no se sobre-editó.

Como anticipa la memoria de la skill, en un guion ya maduro **no había tells de
vocabulario**: el barrido §7 salió en cero y las reglas duras ya estaban limpias. Lo que
había era **ritmo**, y solo se ve contando a lo largo de las 19 láminas:

| Racimo | Antes | Después |
|---|---|---|
| aperturas «Acá está» | 3 | **0** |
| «conviene» | 4 | **1** |
| «es la que» | 7 | **3** |
| «es lo que» | 7 | **4** |
| «exactamente» | 8 | **5** |
| aperturas «Est* es el/la» | 5 | **1** |

El rewrite **no introdujo ningún tell nuevo**: ninguna palabra que no estuviera antes
aparece más de una vez. Reglas duras después de la pasada, sobre las 20 láminas, cuerpo y
notas: cero rayas, cero «palanca», cero decimales en la prosa, cero letras A/B/C/D.

**El hallazgo de contenido, que ninguna cuenta caza:** la lámina 17 abría con «Cierro con
un encargo», y después venían **tres láminas más**. Ahora dice «Hago un paréntesis», y la
19 abre «Vuelvo a la mitosis», que lo cierra. Aparece solo al leer las 19 de corrido, que
es para lo que sirve extraer el guion a un archivo aparte.

**Criterio de corte.** Los diez quiasmos «X, no Y» son contrastes reales («describen, no
establecen»), no retórica, así que **no se aplanaron**. Y la salvedad «una lámina y un
anotador describen, no establecen» **se repite a propósito** en las láminas 10, 16 y 20:
es una consigna que el guion sostiene, y la 20 lo dice en voz alta («lo dije al principio
y lo sostengo»).

### La lectura en voz alta (4-ago, 23:00)

La otra mitad de la tanda del guion, y la capa que faltaba. Las **19 láminas con notas**
leídas de corrido: **20 hallazgos**, **13 aplicados** (defecto o frase que no entra en un
respiro) y **7 abiertos** por ser decisiones de vocabulario. De 6089 a **6114 palabras**
de prosa, +25 netas. Las láminas no se tocaron.

Los dos que justifican la pasada, porque ninguna de las otras dos capas puede verlos:

- **La 12 decía «las ciento sesenta y tres marcas»** veinte segundos después de decir que
  las marcas son «sesenta y un polígonos». Son **163 parches**
  (`atencion_vs_patologo/resultados.md:45`). Escrito uno lo completa solo; **dicho, es una
  contradicción**.
- **La 6 decía «se pesa cada parche igual»**, queriendo decir «igual que arriba». Al oírlo
  se entiende «todos pesan lo mismo», que es lo contrario de la ecuación que la lámina
  enseña. Ahora dice «por su atención igual que antes».

Los otros once: la unidad de la 3 («1858 láminas **por partición**» se oye como 1858 en
cada una, y ahora dice los dos números), cuatro concordancias y una comparación colgada
(láminas 8, 9, 10, 13 y 16), los cuatro decimales seguidos de la 9 (que la tabla ya
muestra, y la convención pide leer la fila por su dirección), dos frases de 55 y 48
palabras partidas en dos (17 y 6), el rango de la 18 dicho de menor a mayor, y el
trabalenguas de oclusivas de la 5.

**Las tres capas cazan cosas disjuntas**, y conviene tenerlo presente al planificar un
cierre de deck: el barrido automático ve reglas duras y geometría, `@humanizer-es` **cuenta**
(racimos de ritmo, arcos rotos), y la lectura en voz alta **entiende de a una frase**.
Detalle y las siete abiertas: `auditoria_coherencia/hallazgos.md`, duodécima pasada (L1 a L5).

### Las siete de vocabulario, resueltas (4-ago, 23:20)

Ernesto aprobó las siete recomendaciones: **once ediciones**, todas en notas, ninguna en
lámina y ninguna sobre un número de valor. La prosa pasó de 6104 a **6117 palabras**. El
detalle edición por edición está en `auditoria_coherencia/hallazgos.md`, decimotercera
pasada.

**Lo que cambió el enfoque de la tanda:** tres de las siete se dieron vuelta al abrir el
generador, porque el término estaba escrito **en el cuerpo de la lámina**. `logit`,
`softmax` y `sigmoide con temperatura` se leen en las láminas 6, 7 y 8, así que no se
quitaron: se **glosaron**, que es lo que pide la convención (§3.b, regla 5, definir antes
de usar). «rankearían» está en los dos paneles de hipótesis de la 10 y **no se tocó**. Y
«fold» aparece en el cuerpo de tres láminas —la tabla de la 15, el rótulo de la figura de
la 17, el rótulo y el remate de la 18—, con la 17 usando «fold» y «partición» en el mismo
bloque: la mezcla era del deck, no del guion, así que se arregló **la única frase del
guion donde conviven** en lugar de unificar todo.

**La regla que queda fijada** para cualquier guion futuro: un decimal se dice tal cual,
dos se agrupan en decenas, tres en centenas. No toca el «0,89 vs 0,890» de las láminas,
que es qué se escribe y está cerrado.

**Lo que sí se unificó sin reparos**: «pipeline» salió de las dos notas donde estaba (la 5
y la 12), «agarrar» pasó a «tomar» en la 20, el 4799 se dice entero solo en la 10 y la 12
—la 11 lo tiene proyectado—, la 13 dice «dentro del» en vez de «entre», y la 9 recorre la
tabla en el orden en que se lee, con un solo apodo para la fila.

## Lo que NO se hizo

- Las ecuaciones **3 a 10 siguen sin explicarse** una por una. La lámina 3 lo declara con
  su marcador de estado y el remate de esa lámina lo dice en voz alta.
- **Grado nuclear no tiene lámina propia**, por lo dicho arriba.
- No se tocó nada de GPU, ni se re-midió nada de `atencion_vs_patologo/`.
