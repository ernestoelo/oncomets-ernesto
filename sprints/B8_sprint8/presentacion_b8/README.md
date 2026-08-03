# Presentación B8 — dos ejes: SI-MIL y la medición de atención

> Construida el **30-jul-2026** como monográfico de SI-MIL. **Rehecha el 3-ago-2026** a
> pedido de Ernesto: SI-MIL se compacta **a la mitad** y entra la medición de atención
> contra las marcas del patólogo, en registro **muy pedagógico**.
>
> Reunión: **viernes 07/08/2026**. `FECHA_REUNION` del generador ya la tiene.

## Qué hay acá

| Archivo | Qué es |
|---|---|
| `generate_b8_deck.py` | genera el deck end-to-end; se corre y reproduce el `.pptx` |
| `prep_assets_atencion.py` | recorta las figuras de `atencion_vs_patologo/` para proyectar |
| `CLAM_Sprint8.pptx` | el deck, **17 láminas**, 13.333 × 7.5 |
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

## Estructura (17 láminas)

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

### 7. Los paneles se dimensionan midiendo el texto

`text_w()` mide con los TTF de Barlow instalados bajo containment, `wrap_lines()` cuenta
las líneas reales, y `panel(..., h=None)` calcula su alto. `auditar(prs)` corre antes del
escalado y avisa de texto que no entra, shapes fuera del lienzo y cuerpos por debajo del
mínimo del template (7 pt). **No reemplaza mirar las láminas**, y de hecho las cuatro
correcciones de layout de esta pasada salieron de mirarlas con la auditoría en cero.

### 8. Extracción de la Fig. 2 del paper

`pdftoppm -f 4 -l 4 -r 400` sobre el PDF y recorte por perfil de contenido. Es la **única
imagen de paper** del deck.

## Guion del presentador

Prosa hablada corrida, sin etiquetas de fase, en primera persona
([[notas-presentador-guion-didactico]]). Sin números de job ni nombres propios: los
checkpoints se rotulan por su cohorte («privado», «privado + TCGA», «5 folds, fold 0»).

Los guiones de las seis láminas fusionadas de SI-MIL se **reescribieron**, no se pegaron, y
absorbieron lo que salió de las láminas. Los ocho de la sección de atención se escribieron
de cero para este deck.

## Lo que NO se hizo

- Las ecuaciones **3 a 10 siguen sin explicarse** una por una. La lámina 3 lo declara con
  su marcador de estado y el remate de esa lámina lo dice en voz alta.
- **Grado nuclear no tiene lámina propia**, por lo dicho arriba.
- No se tocó nada de GPU, ni se re-midió nada de `atencion_vs_patologo/`.
