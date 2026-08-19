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
> **Recortada y rehecha el 5-ago-2026**, a pedido de Ernesto: nueve cambios que dejan el
> deck en **16 láminas**. Ver §«El recorte del 5-ago» al final, que es la sección vigente.
>
> **Recortada el 19-ago-2026** a 16 láminas (`correcciones.txt` + la de control que pidió
> Ernesto después): ver §«El recorte del 19-ago»
> al final, que es la sección vigente.
>
> Reunión: **jueves 06/08/2026** con Sebastián. Se adelantó un día (el viernes 7 es la de
> Benjamín, a la que Ernesto probablemente no llegue por clases). `FECHA_REUNION` del
> generador ya la tiene.

## Qué hay acá

| Archivo | Qué es |
|---|---|
| `generate_b8_deck.py` | genera el deck end-to-end; se corre y reproduce el `.pptx` |
| `prep_assets_atencion.py` | recorta las figuras de `atencion_vs_patologo/` para proyectar |
| `CLAM_Sprint8.pptx` | el deck, **27 láminas**, 13.333 × 7.5 |
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

## Estructura (16 láminas, vigente desde el 5-ago)

| # | Lámina | Eje |
|---|---|---|
| 1-2 | portada y lámina de título | heredadas del template |
| 3 | Objetivos del sprint | recorrido |
| 4 | SI-MIL: qué propone | SI-MIL |
| 5 | Las dos ramas y el puente | SI-MIL |
| 6 | Del embudo al reporte | SI-MIL |
| 7 | Resultados y costo de adopción | SI-MIL |
| 8 | La pregunta medible | atención |
| 9 | Atención y marcas del patólogo | atención |
| 10 | El resultado, grupo por grupo | atención |
| 11 | Los 28 parches de mitosis | atención |
| 12 | Mira bien y responde mal | atención |
| 13 | Los cuatro controles | atención |
| 14 | ¿Recortar expertos o slots? | grid E×S |
| 15 | Tres papers para la rama de mitosis | mitosis |
| 16 | Objetivos propuestos | cierre |

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

## El recorte del 5-ago (de 20 a 16 láminas) — VIGENTE

Ernesto pidió nueve cambios. **Los nueve están ejecutados**, la auditoría da cero avisos y
**ningún número cambió**: no se tocó el `prereg.md` ni el `resultados.md` de ninguno de los
dos experimentos. Todo lo que sale de una lámina se cuenta **hablando**, que es el método
de los recortes anteriores. La numeración de esta sección es la **nueva**.

| Pedido | Qué se hizo |
|---|---|
| **4** con menos bullets, para agrandar la figura | el bloque de tres líneas baja a una y se retira la barra de remate, que repetía esa misma frase. La figura pasa de **8,05 × 2,52 a 9,60 × 3,00** |
| **5 + 6 + 7 en un solo diagrama, sin tablas** | una lámina: las dos ramas, el puente Top-K y el orden de las operaciones. Las dos tablas (los dos anchos, α contra β) salen enteras |
| **8 pedagógica, con diagramas y no una tabla de ecuaciones** | tres figuras: la compuerta que apaga mediciones, la grilla de contribuciones que **es** la ecuación 9, y el entrenamiento conjunto |
| **10 + 11 en una, sin los bullets de la 10** | los dos paneles de hipótesis bajan a **una línea**; la lámina la mandan las dos cintas de parches reordenados |
| **12, 13 y 14 no se tocan** | quedan idénticas (son las 9, 10 y 11 de la numeración nueva) |
| **15: la tabla no decía con qué se entrenó cada modelo** | la columna nombra el **dataset de entrenamiento con su tamaño**, y el pie explica por qué de la corrida de cinco aparecen dos filas |
| **16: el dibujo no se entendía** | `mapa_traslaciones()`: zona de atención con forma, copias atadas por línea punteada, rótulos pegados a lo que nombran |
| **17 + 18 en una, solo diagramas** | los tres gráficos juntos; el veredicto sube al primer renglón y las dos lecturas de forma bajan al guion |
| **20 con el molde de objetivos de la 3** | lista numerada 19 pt + marcador «Propuesto», igual que la lámina de objetivos del sprint |

### La corrección que salió al hacer la tabla de la 15

El §«La procedencia» de más arriba decía que los datasets de entrenamiento eran «153
láminas (privado), 978 (privado + TCGA) y 934». **Esos son los totales del split, no la
parte de entrenamiento.** Contado el 5-ago sobre los `splits_*_bool.csv` reales:

| Corrida | Total | Train | 129741 |
|---|---:|---:|---|
| privado, single-split | 153 | **120** | val |
| privado + TCGA, single-split | 978 | **783** | val |
| privado + TCGA, 5 folds, fold 0 | 934 | **746** | val |
| privado + TCGA, 5 folds, fold 2 | 934 | **749** | val |

La lámina usa los de **train**, que es lo que la columna dice. Y el pie responde la
pregunta que la tabla vieja dejaba abierta: los folds 0 y 2 aparecen porque **son los dos
únicos de los cinco donde esta lámina no quedó en entrenamiento** (en 1, 3 y 4 está en
train). Eso ya estaba en `../atencion_vs_patologo/resultados.md` §2.d.

### Los cuatro helpers nuevos

| Helper | Para qué |
|---|---|
| `barras_esquema` | la tira de pesos antes y después de la compuerta. Alturas escritas a mano y fijas: es un **esquema del mecanismo**, no una medición |
| `grilla_contribuciones` | la ecuación 9 dibujada. Color = signo, tamaño = magnitud, y un cero **se dibuja** chiquito y casi blanco, porque el hueco vacío rompe la grilla |
| `mapa_traslaciones` | el nulo espacial con la lámina y la zona caliente con forma |
| `destilacion` | la ecuación 10 en tres bloques |

### Lo que el QA visual cazó y la auditoría no

Auditoría en cero y **ocho defectos a la vista**, todos de la clase que ningún chequeo de
cajas ve. Los dos que valen como lección:

- **La 5**: el conector que baja la atención hasta el Top-K **cruzaba por el medio** el
  segundo renglón del bloque de mediciones. Las dos cosas están en su caja; lo que se pisa
  es una línea contra un texto. Se acorta el bloque a 2,48" para que la línea pase por
  fuera.
- **La 14**: al bajar la figura de peldaños a 1,16" de alto, el subtítulo de una fila
  pisaba el rótulo de la siguiente, porque `barras_divergentes` los ponía a **0,26 fijos**
  del centro. Ahora el desplazamiento se calcula desde el alto de la fila.

Los otros seis: el «5 120 000» partido en dos renglones, los ceros de la grilla que dejaban
la tabla rota, el eje «más atención / menos atención» repetido bajo las dos cintas, los dos
rótulos del dibujo del nulo que se leían como un título de dos renglones, los objetivos
propuestos a dos renglones con las filas tocándose, y **«fold» y «partición» conviviendo en
la lámina 14**, que es exactamente el defecto que aparece cuando dos láminas se fusionan y
sus vocabularios se vuelven vecinos.

## El guion de las ocho, por `@humanizer-es` y en voz alta (5-ago, 22:40)

Las ocho láminas nuevas o fusionadas del recorte (4, 5, 6, 8, 12, 13, 14 y 16) no tenían
las dos capas de QA de prosa que sí tenían las demás. Ahora las tienen, más la tercera.
**14 ediciones, todas dentro de `notes(...)`**: verificado a máquina que ninguna de las 33
líneas modificadas cae fuera de una llamada `notes()`, así que el cuerpo de las láminas no
se tocó y no hubo que volver a mirarlas. Auditoría en cero. El guion baja de 6532 a 6512
palabras.

**Lo que encontró la extracción a un archivo** (los arcos entre láminas, que dentro del
generador no se ven):

| Hallazgo | Qué se hizo |
|---|---|
| **La 4 y la 5 contaban el mismo montaje dos veces** — los dos caminos y el puente, unas 110 palabras a veinte segundos de distancia. Es el arco que rompió la fusión: la 4 describe la figura del paper y la 5 volvía a empezar de cero | la 5 pasa a apoyarse en la 4 («es el mismo recorrido, redibujado con los anchos y la notación») y va directo a lo que agrega. La lámina baja de 887 a 846 palabras |
| «dos modelos corriendo en paralelo» en el guion de la 5, en el **cuerpo** de la 6 y en el guion de la 6 | manda el cuerpo: se saca del guion de la 5 y queda en la 6, donde está escrita |
| «una lámina y un anotador describen, no establecen» **textual** en la 8 y en la 13 (la 16 ya lo citaba reconociéndolo) | **la salvedad se preserva entera**, por la decisión del 4-ago ([[humanizer-es-skill]] §5): repetida a propósito, no es fórmula de IA. Solo se le agrega a la 13 el reconocimiento que ya tenían las otras dos |
| «la parte que hay que llevarse» y «la que hay que retener» en la 6, más el remate del cuerpo que dice lo mismo: tres veces el mismo movimiento | la primera pasa a «abajo está el reporte» |
| La 8 anunciaba **«las dos respuestas posibles»** y después nombraba una tercera, colgada detrás del adelanto del resultado | «las respuestas posibles», y la tercera sube a su lugar, antes del adelanto |

**Lo que encontró la lectura en voz alta** (la tercera capa, cinco hallazgos):

- **La 14 decía «unidades» y «niveles» donde el cuerpo escribe «slots» y «peldaños»**, sin
  puentearlo nunca; y «slots» está en el **título**. Es el mismo defecto que el 5-ago cazó
  entre «fold» y «partición», que reaparece porque la lámina es una fusión. Se **glosa** una
  vez («en el título aparecen como slots, que es lo mismo») y se adopta «peldaño», que es lo
  que está escrito. Ver [[deck-qa-puntos-ciegos-chequeo]].
- «un vector de quinientos doce» perdía la unidad al oírse: vuelve «números».
- «Ese tercero pesa veinte, contra uno de cada uno de los otros dos» tenía tres «uno» en
  una frase.
- «trescientas» dos veces en la misma oración de la 14.
- «responde con más convicción la respuesta equivocada» (la 12) → «se equivoca con más
  convicción».

**Una imprecisión de dato, que es el hallazgo que más importa.** La 14 decía que del reparto
del peso entre los 300 slots «poco más de la mitad concentra casi todo». Eso mezcla dos
mediciones distintas que `../q1_slots_escalado/resultados.md:38` separa a propósito: el
número efectivo es **159.5 de 300**, y por otro lado **38 slots llevan la mitad del peso y
hacen falta 169 para el 90 %**. El propio archivo advierte que *«`N_eff = 159.5` no significa
159 slots trabajando por partes iguales»*. Ahora la 14 dice lo mismo que la lámina 3, que ya
había pasado las dos capas: **el reparto ocupa alrededor de ciento sesenta**. Ningún número
del sprint cambió.

**Un dato que estaba vago y tenía valor.** La 6 decía que el tercer término de la pérdida
pesa «bastante alto». Es **λ = 20**, contra 1 de cada uno de los otros dos
(`../simil_estudio.md:68` y `../simil_explicacion_matematica.md:438`, verificados contra el
paper). Ahora lo dice.

### Lo que quedó sin tocar, a propósito

- **El cuerpo de la 12 escribe «folds» y el de la 14 «particiones», y está bien así.** No es
  un pendiente: la R5 de la decimocuarta pasada lo decidió a propósito, porque en la tabla de
  los cuatro modelos «fold» es el **identificador del checkpoint**. La regla es no mezclarlos
  **dentro** de una lámina, no unificarlos entre láminas. Verificado antes de tocar nada.
- Títulos, punteos guía, rótulos de figura y remates de lámina, por el pedido del rediseño
  del 4-ago.

## Lo que NO se hizo

- Las ecuaciones **3 a 10 siguen sin explicarse** una por una. Se cuentan dibujadas y en
  bloque, y el guion lo dice en voz alta.
- **Grado nuclear no tiene lámina propia**, por lo dicho arriba.
- No se tocó nada de GPU, ni se re-midió nada de `atencion_vs_patologo/`.
- **La leyenda de la figura de la lámina 9** (la de marcas) sigue mezclando español e
  inglés. Ernesto dijo que esa lámina queda como está.
- ~~El guion de las láminas nuevas y fusionadas no pasó por `@humanizer-es` ni por la
  lectura en voz alta.~~ **Hecho el 5-ago a las 22:40**, ver la sección de arriba. Las 14
  láminas con notas tienen ahora las tres capas.

---

## El reordenamiento del 7-ago (de 16 a 14 láminas) — VIGENTE

Lo pidió **Sebastián** el jueves 6 después de ver el deck, y **no se re-decide**: abre el
**grid de expertos y slots**, sigue la **medición de atención**, y **SI-MIL queda al final**.
Invierte la decisión del 3-ago (lo cerrado antes que lo vivo) y jubila el encuadre del 4-ago
(el grid como sección de cierre). Las dos eran de encuadre nuestro; ésta viene del supervisor.
La presentación es a **Benjamín**, la semana del 11-ago, sin día confirmado.

Los seis pedidos de Ernesto están ejecutados, más los dos entregables. **Ningún número
cambió**, y ni el `prereg.md` ni el `resultados.md` de los dos experimentos se tocaron.

### El orden nuevo, 14 láminas

| # | Lámina | Sección |
|---|---|---|
| 1-2 | portada + título | heredadas del template |
| 3 | ¿Recortar expertos o slots? | el grid abre |
| 4 | La pregunta medible | la medición de atención |
| 5 | Atención y marcas del patólogo | |
| 6 | El resultado, grupo por grupo | |
| 7 | Los 28 parches de mitosis | |
| 8 | Mira bien y responde mal | |
| 9 | Los cuatro controles | |
| 10 | SI-MIL: qué propone | SI-MIL, al final |
| 11 | Las dos ramas y el puente | |
| 12 | **La predicción es el reporte** (retitulada) | |
| 13 | Resultados y costo de adopción | |
| 14 | Objetivos propuestos | cierre |

**Se van dos láminas.** «Objetivos del sprint» y «Tres papers para la rama de mitosis», con
sus constantes `OBJETIVOS` y `PAPERS`. Nada de su contenido se pierde: el **molde** de la
primera lo hereda «Objetivos propuestos» (y sus medidas quedan escritas al lado de
`OBJETIVOS_PROP`, que era lo único que había que conservar), y el **razonamiento** de la
segunda baja al guion de esa misma lámina, porque es la justificación del objetivo
propuesto 2. **SI-MIL conserva sus 4 láminas**: Ernesto eligió explícitamente no
comprimirlas a 2.

### `build()` dejó de ser un bloque único

Cada lámina es ahora una función `lam_*(prs)` y `build()` es la lista de llamadas. El cuerpo
de cada bloque quedó **donde estaba, a cuatro espacios**, porque ya lo estaba dentro de
`build()`, así que la conversión no movió una sola línea de indentación. Dos consecuencias:
el orden del deck se lee y se cambia en un lugar, y el próximo reordenamiento es mover
renglones de una línea.

**Los comentarios `# ---- N. Título ----` perdieron el número.** Quedaba stale en cada
reorden y obligaba a mantener un mapeo entre «la lámina N» de los pedidos y el código, que
es exactamente la fricción que el ADDENDUM del 4-ago (19:00) tuvo que documentar. Ahora el
comentario dice solo el título.

### Las cuatro láminas de la medición, con la estadística adentro

Es el pedido de fondo: Ernesto dijo que le falta entender la parte estadística para poder
defender qué mide cada tipo de tejido.

- **«La pregunta medible» (4)** ahora **nombra** el estadístico (AUC de ranking = U de
  Mann-Whitney normalizada), **hace la cuenta** de pares en pantalla
  (`28 × 4771 = 133 588`, y en el 89 % gana el marcado), y cierra con **tres tarjetas**:
  contra qué se mide cada grupo (la lámina entera, marcas de los otros grupos incluidas),
  por qué son comparables (solo usa el orden; el azar es 0,5 con 12 marcados o con 48), y
  qué dice por debajo de 0,5 (evita, no ignora). **Acá se aplicó R1**: la línea decía «se
  mira dónde caen los 163 marcados» y mostraba 0,89, que es el número de los 28 de mitosis.
- **«Atención y marcas» (5)** no cambió como lámina. Su **nota** sí: entró la oración que
  faltaba del Q1 de la decimoséptima pasada (cada parche marcado compite contra todos los
  demás de la lámina, **incluidos los 2303 de la otra región**), que es el eslabón que
  volvía rival a la región.
- **«El resultado, grupo por grupo» (6)** explica el bigote y cambia sus dos tarjetas, que
  repetían el 0,890 y el percentil, por **las dos incertidumbres**: `± 0,039` si cambia el
  modelo, `± 0,080` si cambian las marcas, que es la grande. Y **sale del guion la frase de
  estroma** («queda justo en el azar, que es donde uno esperaría»): con n = 12 su intervalo
  va de 0,37 a 0,70, así que es una ausencia de dato contada como dato.
- **«Los 28 parches» (7)** abre con la **cadena `26 → +10 → −8 → 28`** pegada al título, que
  es donde nace la pregunta, y suma la **escala** (una mitosis ocupa entre el 2 % y el 4 %
  del parche) como puente a «mira bien y responde mal». **Costo**: las dos figuras bajan de
  3,34 a 2,68 de alto, un 20 %. Si se prefiere el tamaño anterior, lo que hay que mover es
  la banda de la cuenta, no las figuras.

### El QA visual cazó dos cruces de línea sobre texto, con la auditoría en cero

Las dos son de la clase que ningún chequeo de cajas ve, y las dos salieron del rasterizado.

- **Los rótulos de las cintas de la lámina 4 se pisaban entre sí**, y era un defecto
  **preexistente** que el reordenamiento vertical agravó. Un `_rot_label` a 270° ocupa **a lo
  alto lo que mide de ancho** (1,60"), y las dos cintas están a 0,56" una de otra; el bbox
  que reporta el shape es el de **antes** de rotar. Fix: rótulos horizontales en la calle de
  la izquierda, con las cintas corridas a `x = 1,24`.
- **La línea punteada del azar cruzaba el «0,322» de Linfocitos** en la escalera.
  `barras_ranking` ponía el valor pegado a la punta del bigote, y para los grupos que quedan
  bajo el azar esa punta cae **antes** de la línea del 0,5. Fix: el valor va en **columna
  fija** al final del eje. De paso los siete números quedan alineados, que es como se
  comparan.

Además, el caption de la lámina 7 pasaba a dos renglones y el segundo quedaba **tachado por
la barra de remate**. Se acortó a «la región anotada, con los 28 parches en blanco», que de
paso repite el 28.

### El guion, reescrito para el orden nuevo

Lo que **obligaba** a tocarlo, más allá del orden:

- La **portada** describía un deck de dos cosas en el orden viejo. Ahora son tres, en orden.
- La nota del **grid** abría «Hago un paréntesis con un encargo que había quedado» y ahora
  **abre el deck**; y se apoyaba en «el número que conté al principio» (los ~160 slots), que
  se contaba en la lámina de objetivos que se eliminó. Quedó **autocontenida**, y de paso
  dice el escalado a 1176 láminas, que es la respuesta al reparo que puso el propio Benjamín.
- La primera nota de **SI-MIL** abría el deck y ahora **transiciona desde** la atención.
- **Dos referencias cruzadas quedaron al revés con el reorden** y se corrigieron: las dos
  frases de la lámina 11 que prometían algo «en la segunda parte» apuntaban a la medición,
  que ahora ya ocurrió.
- La nota de cierre absorbe la **pregunta del panel** que se retiró de la lámina y el
  **razonamiento de los tres papers**.

Pasó por `@humanizer-es` (8 ediciones: «no es casual», dos «conviene», un gerundio, un
coloquialismo, un anuncio ceremonial) y por la **lectura en voz alta**, que cazó cosas que
ninguna cuenta automática ve:

- Dos «paso a» seguidos en el cambio de lámina 3 a 4.
- «Empiezo por acá porque es lo único que llega cerrado» **contradecía la portada**, que
  presenta SI-MIL como lectura terminada.
- El **26 contra 28** se oía como contradicción desde la lámina 5 y no se resolvía hasta la
  7. Ahora la 5 lo adelanta en media oración.
- **Tres preguntas «para hoy» apiladas al final**, porque SI-MIL pasó al cierre. Las dos de
  SI-MIL pasan a «las dejo planteadas»; la de la lámina 14 queda como la única que bloquea.
- «Tomar un detector de mitosis **público**» chocaba, dos párrafos después, con «uno trae
  pesos **públicos** pero no distingue mitosis».

Barrido final de reglas duras sobre **cuerpo y notas** del `.pptx` construido: cero rayas,
cero «palanca», cero decimales con punto, cero «al revés» (había uno, preexistente, en la
nota del grid).

### La copia sin notas para Sebastián

La pidió para mirar los mapas de calor y los parches sin el guion encima.
`sin_notas.py`, al lado del generador: **cirugía de zip, no python-pptx**
([[pptx-quitar-notas-y-respaldo]]). Saca `ppt/notesSlides/*`, la `<Relationship>` de tipo
notesSlide de cada `slideN.xml.rels` y su `<Override>` de `[Content_Types].xml`. Resultado:
**14 notesSlides eliminados, 15 partes reescritas, 82 byte-idénticas** (fuentes embebidas,
imágenes y theme intactos) y 0 láminas con notas. Se versionó el script y no el `.pptx`,
porque Sebastián va a querer la copia de nuevo cada vez que el deck cambie.

### Lo que queda para que lo decida Ernesto

- **«Objetivos propuestos» queda muy vacía.** Es el molde exacto que pidió, pero con dos
  ítems donde la lámina original tenía seis. Su guion, en cambio, es el más largo del deck.
- El **20 % de alto** que cedieron las dos figuras de mitosis, que él había llamado
  «geniales».
- La **leyenda mezclada español/inglés** de la figura de marcas sigue abierta, y él ya dijo
  que esa lámina queda como está.

---

## La extensión del 18-ago (de 14 a 26 láminas) — VIGENTE

Reunión con **Sebastián, miércoles 19-ago**. `FECHA_REUNION` del generador ya la tiene.

**La decisión la tomó Ernesto y no se re-decide**: se **extiende** el deck del 6-ago en vez de
hacer uno nuevo, el material entra **al final y en orden cronológico** (después de «Objetivos
propuestos»), y entran **tres hilos**: regiones de escaneo, HoVer-NeXt y metodología. **Los
papers de mitosis quedan afuera.** El bloque del 6-ago queda **intacto**: ni una lámina, ni un
número, ni una nota.

### Las doce nuevas

| # | Lámina | Qué lleva |
|---|---|---|
| 15 | Lo que se hizo desde el 6 de agosto | tres paneles + estado; el mapa del bloque |
| 16 | Dos regiones de escaneo dentro del mismo archivo | las dos regiones de la 129741 + el reparto 490 |
| 17 | Cómo se mide si son la misma lámina | el instrumento en dos etapas + el registro a resolución completa |
| 18 | El primer resultado: la mitad no es medible | la cadena 490 → 108 + el reparto 54/54 |
| 19 | Entre las medibles, 33 de 54 | el reparto y su sensibilidad, en la misma lámina |
| 20 | Faltaba buscar giro | el eje de ángulos + la tabla del probe |
| 21 | El recuento se está rehaciendo | las dos trampas de §11 |
| 22 | HoVer-NeXt: instalado, auditado y sin números | fases, con estado |
| 23 | El techo de la prueba, medido sin gastar GPU | la desigualdad + la curva de las tres series |
| 24 | La GPU: un pedido de coordinación | la cola + los tres pedidos |
| 25 | Tres patrones nuevos en dos semanas | P2, P3 y P4 |
| 26 | Qué sigue | los tres pasos + las dos preguntas |

### De dónde sale cada número

Las constantes viven arriba de las láminas, cada bloque con la sección de la que viene:
`regiones_escaneo/resultados.md` §3 (alcance), §8.b (perfiles y sensibilidad), §10.b (el probe);
`hovernext_129741/techo_atencion.md` (los once K); `coordinacion_gpu.md` (la cola, **sin nombres
de usuario ni números de trabajo**). **Nada se lee de un CSV en tiempo de build** y **nada sale
del parcial del re-barrido**.

### Las tres prohibiciones del handoff, respetadas

El **33 va siempre sobre 54 medibles** y la lámina 19 lo dice en su barra de remate; **no aparece
un solo número de HoVer-NeXt**; y ninguna lámina afirma que las recuperadas sean re-escaneos ni
que vayan a caer en seriadas (la 21 presenta eso como mecanismo del método, que es lo que §11.b
sostiene).

### Tres helpers nativos nuevos

- **`barra_reparto`** — un total repartido en tramos contiguos proporcionales. Se usa solo donde
  los tramos son anchos: con un tramo de 1 sobre 108 el rótulo no cabe y la tabla cuenta mejor.
- **`eje_angulos`** — el giro sobre su recorrido, con las dos bandas de diseño y las marcas
  medidas. Es el hallazgo entero en una figura: se ve de un vistazo que las marcas caen fuera de
  la banda chica.
- **`curva_techo`** — recall alcanzable contra el tamaño de la máscara. El eje horizontal va por
  índice y no por K, porque los K están espaciados casi de forma logarítmica y a escala lineal los
  seis primeros se apilarían contra el margen.

### Los assets, y el motivo de cada decisión

`prep_assets_regiones.py`, al lado del generador:

- **Las dos regiones se recortan la MISMA cantidad de columnas** (59 px de banda negra, idéntica
  en las dos), así que la correspondencia entre ellas se conserva.
- **Se dibujan al mismo ALTO, no al mismo ancho.** Las dos están al mismo downsample; a igual alto
  quedan a igual escala y la comparación que la lámina propone es legítima. A igual ancho estarían
  a escalas distintas y la lámina mentiría.
- **La figura de registro se saca de `git show HEAD:`**, no del árbol: el re-barrido en curso movió
  la del árbol a su propio subdirectorio, y la que vale para el deck es la del 14-ago, que es la
  que el documento cita.
- **Los tres pasan por `sin_icc()`.** Los PNG del pipeline traen un perfil de color enorme y el
  Pillow que usa python-pptx lo rechaza al insertar la imagen: el build muere con «Decompressed
  data too large», sin decir de qué archivo. Se descarta el perfil al reescribir.

### Los siete defectos, ARREGLADOS el 18-ago (noche)

El rasterizado había listado **seis**, con la auditoría automática en «sin avisos» sobre las 26.
Están los seis arreglados, y el chequeo nuevo del punto 1 encontró **un séptimo** que la pasada
visual no había visto.

| # | Lámina | Qué era | Cómo quedó |
|---|---|---|---|
| 1 | 17, 18, 23, 26 | el último objeto cruza la barra de remate (termina bajo `4,85`) | el bloque sube; ver la nota de abajo |
| 2 | 20 | los dos rótulos de banda del eje de ángulos se pisan | a una leyenda debajo del eje, y las marcas escalonadas en dos alturas |
| 3 | 23 | CLAM y Mammoth salen del mismo color | CLAM pasa a `ONCO_INK`, y cada serie lleva su marcador (cuadrado / círculo) |
| 4 | 15 | «Dos de ellos ahorraron una corrida entera», y fue uno | «Uno de ellos ahorró una corrida entera», que es lo que dice la 25 |
| 5 | 19 | la columna de porcentaje no decía su denominador | el encabezado dice **«de 108»** |
| 6 | 17 | no rotulaba «etapa A» / «etapa B», que la 18 usa como definidos | los dos bloques de proceso abren con **«Etapa A ·»** y **«Etapa B ·»** |
| **7** | **24** | **el tercer panel de la derecha cruza la barra** | los tres paneles suben; lo cazó el chequeo nuevo, no el ojo |

**El séptimo importa más de lo que parece**: la lámina 24 había pasado el QA visual completo de
la sesión anterior. Su panel cruza porque `panel()` **crece** para que entre su texto, así que el
defecto no está escrito en ninguna constante del generador y mirar la lámina es la única forma de
verlo, salvo que se lo mida. Se lo midió.

### El chequeo de la barra de remate, que antes no existía

`auditar` ahora marca cualquier shape que cruce la barra (`_TAKEAWAY`, `_borde_inferior`). Las
26 láminas dan cero. Construirlo tuvo tres trampas, y las tres dan un chequeo que **parece**
andar (detalle en [[deck-qa-puntos-ciegos-chequeo]], ADDENDUM del 18-ago noche):

- **La `t` con la que se dibuja la barra no es donde la barra queda**: `reflow_onco` corre
  después y reancla o comprime el cuerpo, así que el `4,85` termina en `4,82` o en `4,49`. Se
  guardan los **shapes** y se lee su posición al auditar.
- **La barra se marcaba a sí misma**: el reflow le sube el rótulo por encima de su propia línea,
  así que se excluye **por identidad**, no por geometría.
- **Una caja de texto no se ve, se ve el texto**: medir la caja marcaba captions de una línea
  dentro de la caja de `0,4"` de `caption()`, en láminas del 6-ago que rasterizaron perfectas. Un
  chequeo que grita de más se termina ignorando. Caja de texto ⇒ se mide el texto con su anclaje;
  panel pintado ⇒ se mide la caja.

**Y un defecto que ningún chequeo de cajas puede ver**, arreglado de paso: en `eje_angulos` las
dos bandas nacen las dos en cero y se pintaban en el orden declarado, así que la más ancha cubría
entera a la chica, **que es la que carga el hallazgo**. Se pintan de la más grande a la más chica.

### Lo que NO se verificó — CERRADO el 19-ago (ver § final)

**Las láminas tocadas no se volvieron a mirar.** La auditoría da cero y eso es exactamente lo que
daba con los seis defectos adentro: no alcanza. Quedan por rasterizar y mirar una por una las
**15, 17, 18, 19, 20, 23, 24 y 26**, que son las ocho que cambiaron de geometría o de texto.

### El guion, sin escribir — CERRADO el 19-ago (ver § final)

**Las doce láminas nuevas no tienen `notes()`.** Es lo más grande que queda, y falta además la
pasada de `@humanizer-es` y la lectura en voz alta, que es la capa que caza lo que ninguna cuenta
automática ve.

### El plan del guion, escrito el 18-ago (noche) — EJECUTADO el 19-ago (ver § final)

Sesión de plan, **sin tocar el generador**. El plan completo vive en
`~/.claude/plans/handoffs-handoff-b8-20260818-1920-md-hazy-dijkstra.md` y lo ejecuta una **sesión
limpia**, por decisión de Ernesto: el paso que abre es el rasterizado y necesita el presupuesto de
lecturas de imagen entero ([[image-api-qa-limit]]).

**Las dos decisiones de Ernesto:**

- **Medir primero, mirar después.** Rasterizar con `FONTCONFIG_FILE` puesto, correr la medición de
  tinta por renglón sobre las ocho láminas tocadas **sin gastar lecturas de imagen**, y recién
  entonces mirarlas una por una. El rasterizado queda autorizado en ese orden.
- **La portada no se toca.** Su nota abre con «Traigo tres cosas» y ahora hay un cuarto bloque
  detrás; la regla «ni una nota del bloque del 6-ago» queda entera y **la costura la resuelve la
  nota de la lámina 15**, que hace el pivote explícito.

**Las dos precisiones de contenido**, las dos de la lámina 22, que es nueva y se puede tocar:

| Qué | Por qué | Cómo queda |
|---|---|---|
| «0,872 y 0,914» proyectados sin nombrar la medida | **son el percentil medio de atención, no el AUC** (`../hovernext_129741/auc_ranking_fold4.md:88` lo dice explícito; los AUC de ese par son 0,876 y 0,918). Al lado de una sección que habla de ranking de atención, se leen como AUC | la lámina dice «percentil medio», y el guion no los llama AUC |
| «los cuatro juegos de pesos» | es correcto (en disco hay `lizard_convnextv2_tiny` y `pannuke_convnextv2_tiny_{1,2,3}`) pero se lee raro contra el plan, que habla de **dos** | el guion lo dice como es: un modelo con clase de mitosis y tres del otro, que se promedian |

**El reparto del guion por lámina** está en el plan, con la sección de la que sale cada nota. La
que más trabajo pide es la **20**: el hallazgo del giro no se entiende sin contar que el control
positivo se leyó primero y que además **calibró el corte**.

**Y una costura que ningún chequeo automático puede ver**, anotada acá porque es de la clase que
reaparece: al **extender** un deck, la nota de la portada sigue anunciando el número de bloques
**viejo**. Es lo primero que se oye y no está escrito en ninguna lámina.

---

## La sesión del 19-ago: el cuerpo cosechado y el guion escrito — VIGENTE

El plan del 18-ago se ejecutó, **pero no como estaba escrito**: entre que se escribió y que se
ejecutó, **el job de HoVer-NeXt corrió de madrugada** y el re-barrido con giro cerró. El paso 0
de la sesión fue reevaluar el plan contra ese estado nuevo, y el alcance resultó **mayor** que el
presupuestado: **nueve** de las doce láminas nuevas necesitaban edición de cuerpo, no cinco.

### Lo que movió el recuento (láminas 18 a 21)

Cosechado con `cosechar_barrido_registro.py` + `comparar_barridos_rotacion.py`; la verdad de campo
está en `../anotaciones_patologo/regiones_escaneo/resultados.md` §12.

| | Antes | Ahora |
|---|---|---|
| Cadena | 490 → 139 → 129 → 108 | 490 → 139 → **130 → 109** |
| Medibles | 54 de 108 (50 %) | **77 de 109 (70 %)** |
| Re-escaneo | 33 de 54 (61 %) | **31 de 77 (40 %)** |
| Seriadas | 1 | **12** |

**La lámina 20 afirmaba «el 33 es un piso» y el dato lo refutó.** El cuerpo lo dice ahora como
predicción fallida, y el guion la cuenta en voz alta. La otra predicción de esa lámina (pool a
«unas 81», rango 65-97) acertó: 77. **Se reportan las dos**, que es el punto.

**El patrón P4 quedó medido, no conjeturado**: las recuperadas caen en «seriadas» al 29 % contra
el 10 % de las ya medibles, y 10 de las 18 que no dan re-escaneo fallan **los dos** criterios. La
lámina 21 pasó de contar un riesgo futuro a contar un resultado.

### Lo que movió la corrida (láminas 15, 22, 23, 26)

`../hovernext_129741/corrida_5008.md` §4 las listaba stale. La segmentación corrió en **18 min** y
dio **177 mitosis crudas**, sin cruzar contra las 26 marcas. Las cuatro se reescribieron con ese
estado, y las tres precisiones que la lámina 22 debía cargar están puestas: **percentil medio** y
no AUC (los AUC del par son 0,874 y 0,919, casi iguales, que es la trampa), la composición de los
cuatro juegos de pesos, y el freno explícito de que 177 **no es** precisión ni exhaustividad.

### La lámina 24, reencuadrada

Pedía coordinar una fila de GPU que **se drenó sola**. Decisión de Ernesto: **reencuadrarla como
lección** en vez de borrarla. Conserva la tabla como evidencia del momento y cambia los tres
paneles por las tres cosas que la fila enseñó (workaround L): un turno en espera por prioridad
puede no estar esperando, sin tope declarado adelante no hay forma de colar, y achicar el propio
pedido no adelanta. Deja de pedirle algo a Sebastián que ya no aplica.

### Los dos defectos visuales, arreglados

- **Lámina 23**: el rótulo `marcas / de 28` se centraba verticalmente y caía en el renglón de la
  etiqueta `14` del eje Y (`curva_techo` dibuja los ticks 0/7/14/21/28 en `l-0.56`); se leía
  «de 2814». Ahora va **arriba del eje, alineado a la izquierda**, en `TOP+0.20`, que queda libre
  porque el tick más alto ocupa `TOP+0.53` a `TOP+0.79`.
- **Lámina 24**: `pie_lineas` arrancaba en `TOP+2.10` y la tabla termina en `TOP+2.14`. Bajó a
  `TOP+2.24`.

### El guion de las doce

**5.036 palabras**, dentro del presupuesto de 4.500 a 6.000, con la 15 corta (**201**) porque es
de tránsito y carga la **costura de la portada**. Cobertura: **25 de 26** láminas con nota (la 1
es la portada del template y no lleva).

Formato verificado a máquina contra las 13 notas previas: punteo de 1 a 5 líneas con las cifras,
línea en blanco, prosa hablada en párrafos y **cero dígitos en la prosa** (los números van en
letras). Cero guiones largos, cero «palanca», cero nombres propios, cero números de trabajo.

| Lámina | Palabras | | Lámina | Palabras |
|---|---|---|---|---|
| 15 | 201 | | 21 | 488 |
| 16 | 325 | | 22 | 541 |
| 17 | 427 | | 23 | 494 |
| 18 | 352 | | 24 | 399 |
| 19 | 440 | | 25 | 451 |
| 20 | **633** | | 26 | 285 |

La **20** es la más larga, como el plan anticipaba: el hallazgo del giro no se entiende sin contar
que el control positivo se leyó primero y que además **calibró el corte**.

### Lo que NO se hizo en esta sesión

- **Las tres capas de QA del guion**: `@humanizer-es`, la lectura en voz alta de las doce notas
  extraídas a un archivo, y el barrido de reglas duras **ya corrido a máquina** (esa sí está: cero
  guiones largos, cero «palanca», cero nombres, cero cifras en prosa). Faltan las dos primeras,
  que son las que ven los arcos rotos entre láminas.
- **El brazo de ensemble de HoVer-NeXt**: sin lanzar, por decisión de Ernesto (el foco era el
  deck). La cola está vacía y es un solo envío.
- **El cruce de las 177 contra las 26 marcas**: sin hacer. Es el segundo factor del techo.

## La sesión del 19-ago (tarde): entra el cruce, y con él caen seis frases — VIGENTE

Única misión, aprobada por Ernesto al cierre de la sesión anterior y ejecutada tal cual: **meter
el cruce al deck**. La reunión con Sebastián **seguía sin ocurrir** al arrancar, así que no hubo
feedback que replanificara nada.

**De 26 a 27 láminas.** La nueva va **después de la 23** (el techo), así que **24 → 25, 25 → 26,
26 → 27**. Las dos referencias por posición del deck se verificaron y ninguna se rompe: la de la
lámina 5 («en dos láminas más» → 7) y la de la 19 («retomo en dos láminas más» → 21) apuntan
**antes** del punto de inserción.

### La lámina 24 nueva: el segundo factor del techo

Todo sale de `../hovernext_129741/cruce_marcas.md`. Se transcribió a `CRUCE_TOL` (§2) y
`CRUCE_CONJUNTA` (§3); nada se re-mide en tiempo de build.

Tres objetos, y cada uno está por una razón:

- **El titular**, `13 de las 26 marcas = 50,0 %`, con el **emparejamiento uno a uno** al lado y no
  en el guion. Sin eso la primera pregunta de la sala es por qué no son 18, que es lo que da
  contar por distancia mínima reusando la misma detección.
- **La meseta** (`meseta_tolerancia`, helper nuevo), que es lo que hace **robusto** al 13. Como
  curva, un tramo plano de seis puntos es una recta que no llama la atención de nadie; como tira
  de celdas, el mensaje es el mismo número repetido seis veces. Las dos celdas de fuera de la
  meseta van en **gris y a la vista**, para que se vea de dónde sale el número que sube en vez de
  esconderlo.
- **La tabla conjunta** con la columna **«ambas»**, que es la intersección contada y no la cota.
  Se recortó a **cuatro filas** (4,0 % / 7,6 % / 12,0 % / la región entera) por espacio: la de
  20,0 % no agrega una lectura, y la de la región entera es el chequeo de sanidad y no se toca.

Las tres salvedades de `cruce_marcas.md` §5 que más fácil se pierden van en el **cuerpo** y no
solo en el guion: la **unidad** (marcas 26, contra los parches con marca 28 de la lámina 23, que
**no se encadenan**), que la **cota `mín( )` es floja** (promete 13 donde la intersección real es
11) y que el número de la región entera es el **chequeo de sanidad**. **No hay precisión en
ninguna parte del deck**, y es deliberado.

El remate es el hallazgo y no el número: **el cuello se movió**. Hasta esta lámina la discusión
era el tamaño del recorte por atención; desde el 7,6 % de la región el que manda es la detección.

### Las seis frases stale, corregidas

Cuatro las traía listadas el handoff; **dos aparecieron al barrer el generador** y son del mismo
defecto, así que se corrigieron en el mismo pase.

| Lámina | Dónde | Qué decía | Por qué era falsa |
|---|---|---|---|
| 15 | cuerpo, panel HoVer-NeXt | «177 mitosis, sin cruzar» | el mapa del bloque, y el bloque ya incluye el cruce |
| 15 | cuerpo, panel Método | «Uno de ellos **ahorró** una corrida entera» | el techo dio alto y la corrida se hizo. La 26 ya lo decía en condicional desde la mañana; acá había quedado en pasado |
| 22 | guion, punteo | «sin cruzar contra las marcas» | anunciaba pendiente lo que se cuenta dos láminas después |
| 22 | guion, prosa | «No lo cruzamos todavía… y cuando lo crucemos» | idem |
| 23 | guion, cierre | «Eso es lo primero que sigue» | ahora es «lo que viene en la lámina siguiente» |
| 27 | cuerpo, tarjeta 1 + remate + guion | «Cruzar las 177 contra las 26 marcas» como paso pendiente | listaba como futuro lo que la 24 acaba de mostrar |

La lámina 27 quedó con **tres tarjetas nuevas**: el brazo de ensemble (ahora con el molde del
cruce armado, así que el Δ sale sin trabajo extra), la coordinación antes de extender a las doce,
y una **dirección** que sale del cruce: para subir el 13 de 26 hay que mover la detección, porque
agrandar el recorte ya no compra nada.

Lo que **no** se tocó: el cuerpo de la lámina 22 («nada cruzado todavía») y su remate («cruzarlas
es lo que sigue»). En ese punto del recorrido son verdad, y ahora además **arman** la lámina 24.

### Verificación

- **`AUDITORÍA: sin avisos`** en las 27, y la copia sin notas regenerada (27 láminas, 0 con notas).
- **AST contra el diff**: de 178 líneas nuevas, **87 caen dentro de un `notes()`** y las 91
  restantes son cuerpo o código, todas justificables una por una (los dos bloques de datos, el
  helper, la lámina entera, las tres tarjetas de la 27 y la línea de `build()`).
- **Estilo, medido sobre el `.pptx` y no sobre el fuente**: cero rayas, cero «palanca», cero «al
  revés» en las 27 láminas y sus notas.
- **Guion nuevo (762 palabras)**: 37 oraciones, media 19,1 y **sd 10,2** (la variedad humana que
  `@humanizer-es` pide), cero vocabulario del cluster de IA, cero colas de gerundio y **cero
  dígitos en la prosa**. Medido con `grep` **antes** de invocar la skill, que es lo que evitó una
  pasada que habría sobre-editado prosa limpia ([[deck-qa-puntos-ciegos-chequeo]]).
- **Rasterizadas y miradas**: la 15, la 24 y la 27. El titular de la 24 salió en dos renglones
  pegado al borde del panel y se acortó el subtítulo hasta que entra en uno.

---

## El recorte del 19-ago (de 27 a 15 láminas) — VIGENTE

> Ernesto dejó la orden en `correcciones.txt` (**sin trackear**, decisión suya). El criterio
> es la reunión pendiente con Sebastián: **lo que no sirva para llegar a ella, sale.**

### Las dos lecturas que había que resolver ANTES de borrar

El texto ordena eliminar las láminas 9, 15, 16-21, 22, 25, 26 y 27, y sobre la 23 y la 24 dice
otra cosa: que esperaba **los mapas de calor de HoVer-NeXt con imágenes de dónde se fija**, y que
eso es lo más importante **junto con los datos de si identifica las mitosis**. Leerlo como «borrar
las dos» se habría llevado el **13 de 26**, que es exactamente el dato que la misma frase pide
conservar. Y el otro renglón, «eliminá la 26, deberíamos tener una que mencione RESULTADOS»,
describe esa misma lámina.

Resuelto con Ernesto en la primera ronda: **las dos tensiones se cierran juntas.** La 23 (el techo
del filtro) sale, porque es método; la 24 **cambia de forma** y se convierte en la lámina de
resultados, con los mapas primero y el número al lado. Conserva el 13 de 26 y la tabla de los dos
factores; pierde la meseta de tolerancia.

### El deck que queda, 16 láminas

| # | Función | |
|---|---|---|
| 1-2 | heredadas del template | |
| 3 | `lam_grid` | el grid E×S |
| 4-8 | `lam_pregunta_medible` … `lam_mira_responde` | la medición de atención |
| 9-12 | `lam_simil_*` | SI-MIL |
| 13 | `lam_objetivos_propuestos` | |
| **14** | **`lam_hovernext_paper`** | nueva: la Figura 1 del paper |
| **15** | **`lam_resultados`** | nueva: la fusión de 23 y 24 |
| **16** | **`lam_hovernext_solo`** | nueva: el control, la herramienta sola |

### La lámina de resultados, y por qué tiene esa forma

Su eje es **el encadenamiento que pidió Sebastián**: la atención de CLAM recorta y el detector
trabaja adentro. No son dos herramientas contadas por separado, así que los tres paneles son **la
misma región en tres estados** (atención · el 12 % más atendido · las detecciones), y abajo el
detalle a resolución nativa, que es lo que contesta «dónde se fija».

Tres salvedades van en el **cuerpo** y no solo en el guion, porque son las que más fácil se pierden:

- la unidad de la tabla son **marcas (26)**, no los 28 parches con marca de la lámina 7;
- la cota `mín( )` es **floja**: donde promete 13, la intersección real es 11;
- **no hay precisión y es deliberado** — las marcas son positivos parciales, así que una detección
  sin marca no es un error.

### La lámina de control (pedido posterior de Ernesto, el mismo día)

«Una última lámina donde se use puramente HoVer-NeXt para la misma WSI, sin CLAM.» **Se pudo sin
correr nada**: la corrida fue sobre la **lámina entera** y el recorte se aplicó después, sobre la
salida, precisamente para conservar esta comparación.

Es la lámina que hace legible a la de resultados: sin un brazo sin recorte, «13 de 26 con el
recorte puesto» no se compara con nada. La escalera que arma, toda medida:

| Qué se revisa | Parches | Área | Det. | Marcas |
|---|---|---|---|---|
| La lámina entera, sin recorte | 4799 | 68,0 mm² | 177 | 13 de 26 |
| Solo la región anotada | 2496 | 35,4 mm² | 82 | 13 de 26 |
| El 12 % más atendido por CLAM | 300 | 4,3 mm² | 48 | 11 de 26 |

**El recorte no compra marcas, compra área**: un factor de 16 en superficie por dos marcas. Es la
respuesta a «cuánta superficie hay que ponerle delante al patólogo», que es distinta de «cuántas
mitosis encontramos» — y ésa ya se contestó en la lámina anterior (manda el detector).

Las dos primeras filas dan lo mismo **por construcción**: las 26 marcas caen todas en la región
anotada, así que restringirse a ella no puede perder ninguna. Verificado igual, no asumido: el
emparejamiento con las 82 detecciones de esa región sola da los mismos 13 que con las 177.

**Lo que la lámina NO afirma**: nada sobre las **95 detecciones de la región sin anotar**. No hay
marcas ahí, así que no son ni aciertos ni errores, y van dibujadas **del mismo color** que las
otras para no sugerir lo contrario.

### Los assets nuevos, y que ninguno necesitó GPU

Todo salió de lo que ya estaba en disco. `prep_assets_hovernext.py` reusa el emparejamiento uno a
uno de `scripts/cruce_hovernext_marcas.py` (húngaro, 30 µm, el mismo offset del geojson y el mismo
corte de región), así que la figura **no puede** contar algo distinto del número:

- `cadena_clam_hovernext.png` — los tres paneles, dibujados a ÷16 y **acotados a 3400 px** al
  guardar: en la lámina miden 4,62", o sea que el montaje original iba a 1340 DPI de puro peso.
- `hovernext_zoom.png` — cuatro recortes de 260 px de nivel 0, elegidos **por separación máxima
  entre sí** para no mostrar cuatro veces el mismo foco.
- `hovernext_solo.png` — las dos regiones de escaneo con las 177 detecciones. Su caja se toma
  sobre los parches y se **ensancha** hasta cubrirlas: tres caen unos 700 px por encima del
  teselado, y recortarlas dejaría el panel mostrando 174 con el guion diciendo 177.
- `hovernext_paper_fig1.png` — paneles A, B y C de la Figura 1 del paper, por
  `prep_assets_paper_hovernext.py`. Queda fuera el panel D (distribuciones de clase de los
  conjuntos de entrenamiento): es del paper, no de lo que corrimos, y competía por el alto.

### El barrido de referencias cruzadas, que es donde esto falla

Borrar seis láminas seguidas deja punteros colgando, y **no se encuentran grepeando la frase**:
hay que grepear por sustantivo y verbo. Lo que apareció:

- La portada prometía **«tres cosas»** y el deck recortado entrega cuatro. Es la costura que ya
  falló una vez; ahora anuncia el hilo de HoVer-NeXt como la cuarta.
- El guion de la 7 (`lam_escalera`) decía «cuando lo sometemos a **las pruebas que vienen ahora**»,
  apuntando a la lámina de controles. El hecho se conserva; el puntero se fue.
- El guion de la 13 (`lam_objetivos_propuestos`) se apoyaba en **el nulo por traslación** por su
  nombre, y la audiencia ya no lo ve.
- «En **dos láminas más** cuento de dónde sale esa diferencia», en la 6, **sigue resolviendo bien**:
  el recorte solo tocó láminas posteriores. Verificado, no asumido.

Y en el generador: 13 constantes y 4 funciones quedaron sin uso, todas retiradas. Las que ya
estaban huérfanas **antes** del recorte se dejaron como estaban, que no son de esta sesión.

### Lo que NO se hizo

- **No se versionó `correcciones.txt`** — decisión de Ernesto.
- **No se borraron** `region0/region1/registro_level0_129741.png` de `assets/`. El deck ya no los
  usa, pero son producto de un trabajo real y `prep_assets_regiones.py` sigue ahí.
- **Cero GPU**, cero `sbatch`, y el brazo de ensemble sigue sin lanzarse.

### Verificación

- **`AUDITORÍA: sin avisos`** en las 16, copia sin notas regenerada (16 láminas, 0 con notas).
- **Rasterizado y mirado**: las 15 en contacto, y las dos nuevas a tamaño. Tres defectos que la
  auditoría no ve, arreglados: el rótulo «Detecciones de HoVer-NeXt» se partía y la segunda línea
  quedaba tapada por la figura; la cabecera de tabla partía «Detectada / s»; y la tabla decía
  «máscara» mientras el resto de la lámina decía «recorte».
- **Los dos títulos nuevos entraban en dos renglones** y eran los únicos del deck: acortados a
  «HoVer-NeXt y la clase de mitosis» y «Resultados: recortar y detectar». El mensaje largo vive en
  la barra de remate, que es su lugar.
- El deck bajó de 12,3 a **17,1 MB**, y no a los 21 que daba antes de acotar los assets.

## La sesión del 19-ago (noche): las notas de la 15 y la 16, reescritas para presentarse solas — VIGENTE

**Cambio de alcance decidido por Ernesto a mitad de sesión.** La sesión entró con el encargo de
leer el guion de las 16 de corrido y decidir el recorte de tiempo; ese trabajo se hizo y su
resultado queda abajo como registro, pero **no se ejecutó**, porque Ernesto redefinió la reunión:
**hoy solo se presentan la 15 y la 16**, y el reloj deja de importar. El pedido pasó a ser
pedagógico y explícito: que cada una quede muy bien explicada, y que las notas digan **qué
hicimos**, **qué genera HoVer-NeXt**, **qué representan las marcas que genera** y **por qué no
rescató las 26 mitosis del patólogo**.

### La consecuencia de diseño que gobierna la reescritura

Presentadas solas, las dos láminas **pierden todo el andamiaje** que les daban las anteriores: la
1 a la 8 establecían qué es la atención de CLAM, de dónde salen las 26 marcas y que son positivos
parciales; la 14 presentaba la herramienta. Nada de eso va a estar en la sala. Las notas nuevas
**cargan ese contexto ellas mismas**, sin suponer ninguna lámina previa. Ése es el motivo del
crecimiento, no la verborragia: **715 → 1419 palabras** en la 15 y **441 → 693** en la 16, unos
16 minutos hablados para las dos.

### Lo que se agregó, y de dónde sale cada dato

| Bloque nuevo | Fuente |
|---|---|
| Qué **produce** HoVer-NeXt: un inventario de núcleos, no un mapa de calor. **238 329 células** segmentadas, 7 clases, **177** de mitosis | `corrida_5008.md` §2 (tabla por clase) |
| Qué **representa** cada marca: la amarilla es **un núcleo** que el clasificador etiquetó mitosis; la blanca es el dibujo del patólogo. Dos fuentes independientes en la misma imagen | `cruce_marcas.md` §1, [[anotaciones-patologo-qupath]] |
| **Por qué falla la mitad**, en cuatro capas: no es artefacto de medición (meseta de 10× en la tolerancia, 115 µm de mediana a la detección más cercana) → la clase de mitosis se entrenó **solo en colon** y la lámina es de **mama** → ni en colon es exhaustiva (**recall 0,720** de HNTiny, que es el checkpoint que corrimos) → y las 26 marcadas deberían ser **las fáciles**, así que el sesgo empeora la lectura | `cruce_marcas.md` §2 y **§2.b nueva**, `papers_14_agosto/hovernext_estudio.md` §3.a y §3.b |
| Lo que **no** se midió y es lo barato que sigue: si el núcleo fallado fue segmentado y **mal clasificado** o no fue segmentado. Se contesta con los `raw` guardados, sin GPU | `cruce_marcas.md` §2.b, `corrida_5008.md` §2 (`--keep_raw`) |

La 16 cierra ahora abriendo la discusión hacia dónde mover el número, con las dos vías baratas y
la advertencia de escáner de MIDOG (`tareas_geometricas/midog_notas.md` §3.a).

### El error que se corrigió de paso, y que iba a costar GPU

`cruce_marcas.md` §6 afirmaba que **el brazo de ensemble «ahora tiene contra qué compararse»** y
que el mismo cruce sobre su salida daría el Δ. **Es falso.** El ensemble son los tres folds de
**PanNuke**, y PanNuke **no tiene clase de mitosis** (`out_channels_cls` 6 = 5 + fondo, contra 8 =
7 + fondo de Lizard-Mitosis; `auditoria_codigo.md`). Sobre su salida el cruce **no es computable**.
Corregido en el documento, tachando el enunciado viejo en vez de borrarlo. **Correr el ensemble no
contesta la pregunta de mitosis**, y por eso las notas de la 16 no lo proponen.

### El análisis de arcos y de reloj que sí se hizo, y quedó sin ejecutar

Se leyó el guion completo de las 16 de corrido. Vale para cuando se retome el deck entero:

- **Desfase entre las prioridades declaradas y el presupuesto real.** La portada llama «corto» al
  encargo de expertos (**6,0 min**, su lámina es la 3ª más larga), «comprimida» a la lectura de
  SI-MIL (**17,4 min, 27,6 %**) y «lo que más quiero discutir» a HoVer-NeXt (**11,8 min**). O sea
  que lo declarado comprimido ocupa más que lo declarado prioritario. Si hay que recortar, el
  propio texto dice dónde: la lámina 10 sola son 866 palabras.
- **La 13 propone como futuro lo que la 14 a la 16 muestran hecho** («correr un detector ya
  entrenado y ver cuánto acierta contra las 26 marcas»). Es problema de tiempo verbal.
- **La 13 descarta un paper «porque no distingue mitosis entre sus clases»** (es CellViT, y es
  cierto) y dos láminas después entra un segmentador de pesos públicos que **sí** la tiene. No es
  contradicción, son herramientas distintas, pero sin una cláusula que lo diga suena a una.
- **Dato stale de fondo**: la 4 dice «la única que tenemos anotada» y la 13 pregunta cuántas hay.
  Esas notas son del 6-ago; el **17-ago** aparecieron **12 láminas anotadas** con 94 marcas de
  mitosis. Está **solo en las notas habladas**, ningún cuerpo de lámina lo afirma. **No se tocó**,
  porque esas láminas no se presentan hoy y la decisión de cómo reencuadrar el objetivo 1 quedó
  sin tomar.
- Redundancias medidas entre la 14 y la 16 (el «si hubiéramos recortado antes» casi textual, y los
  18 minutos): **la de la 14 ya no aplica** porque la 14 no se presenta; la de la 16 se conservó
  porque ahora es la única vez que se dice.

### Lo que NO se hizo

- **No se recortó el guion de las otras catorce**, ni se tocó su contenido: el alcance cambió.
- **No se cambió la fecha de portada**: Ernesto decidió dejar el 19 de agosto.
- **Cero GPU**, cero `sbatch`. El brazo de ensemble sigue sin lanzarse, y ahora hay una razón
  documentada para no lanzarlo con la mitosis como objetivo.
