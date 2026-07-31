# Presentación B8 — SI-MIL

> Construida el **30-jul-2026**. Pedido de Ernesto: **las ecuaciones**, la **figura original
> del diagrama del modelo** (Fig. 2 del paper, pág. 4) y el **formato de deck del proyecto**.
>
> **Recortada el 31-jul-2026** de 19 a 14 láminas, también a pedido de Ernesto, sacando el
> ejemplo numérico del orden de las operaciones. Ver «El recorte del 31-jul» más abajo.

## Qué hay acá

| Archivo | Qué es |
|---|---|
| `generate_b8_deck.py` | genera el deck end-to-end; se corre y reproduce el `.pptx` |
| `CLAM_Sprint8_SIMIL.pptx` | el deck, **14 láminas**, 13.333 × 7.5 |
| `assets/simil_fig2_full.png` | Fig. 2 completa, recortada de la pág. 4 a 400 DPI |
| `assets/simil_fig2_{a,b,c}.png` | los tres paneles por separado |

```bash
PYTHONPATH=/media/administrador/Storage1/sdonoso/clam_testing2/.pylibs \
/home/sdonoso/miniconda3/envs/clam_latest/bin/python \
  sprints/B8_sprint8/presentacion_b8/generate_b8_deck.py
```

## Alcance de contenido (lo que entra y lo que no)

El insumo es [`simil_explicacion_matematica.md`](../simil_explicacion_matematica.md) y los
números salen de [`simil_estudio.md`](../simil_estudio.md). No se rehízo ninguno de los dos.

- **Ecuaciones 1 y 2: desarmadas.** Son las que Ernesto marcó como las que no cerraban.
  La 2 entra ahora en **una sola lámina**: la analogía de la licuadora contra la libreta
  quedó en el guion, y en la lámina van los dos caminos dibujados más la tabla de qué queda
  en memoria tras el forward, que era el malentendido de fondo. El mini ejemplo numérico
  **se retiró** (ver «El recorte del 31-jul»).
- **Ecuaciones 3 a 10: en panorama**, una línea de glosa cada una, con la **9 destacada**.
  Desarmarlas con el mismo detalle sigue **pendiente**, y la lámina de objetivos lo declara
  con su marcador de estado en vez de disimularlo.
- **No se presenta como mejora de rendimiento.** En la celda que nos corresponde (CLAM de
  base, su Tabla 2) rinde menos: 0.937 → 0.925 en accuracy y 0.972 → 0.957 en AUC. La
  lámina de resultados lo dice con esa fila destacada.
- **HoVer-Net y SI-MIL son la misma cadena**, no dos ángulos. Está en la lámina de las dos
  entradas y en el guion.

## Estructura (14 láminas)

Portada y lámina de título (heredadas del template) · objetivos · qué propone en una frase ·
**la Fig. 2 completa** · dos descripciones del mismo parche · **ecuación 1** · **ecuación 2,
el orden de dos operaciones** · qué implica para nuestro modelo · el puente PAG Top-K · la
otra rama, α contra β · las ecuaciones 3 a 10 · qué reportan y el contraste con lo nuestro ·
qué costaría llevarlo acá y qué preguntar.

## El recorte del 31-jul (19 → 14 láminas)

Pedido de Ernesto: menos láminas, y sobre todo **fuera el ejemplo numérico del orden**, que
debía quedar claro en una sola lámina. Esto **supersede** la decisión del 30-jul de conservar
la secuencia «analogía → ejemplo numérico → tabla de qué queda».

Salió una lámina entera (el ejemplo numérico) y se fusionaron cuatro pares:

| Antes | Ahora | Qué se hizo |
|---|---|---|
| divisoria de sección + «qué propone» | **una** | la divisoria solo aportaba la ficha del paper, que entra como línea de referencia sobre la lámina |
| «ecuación 2, el orden» + «el mismo número, distinto lo que queda» | **una** | se borró el ejemplo numérico entero y la tabla de qué queda tras el forward pasó abajo de los dos caminos, recortada a las 3 filas que separan a los órdenes |
| «por qué la atención no rescata» + «dónde queda nuestro modelo» | **una** | se borró la segunda tabla numérica (α contra contribución) y las tres tarjetas de diferencias; queda el mapeo a `model_clam.py` arriba y dos paneles abajo |
| «qué reportan» + «el contraste con lo nuestro» | **una** | dos tablas, sin los cuatro paneles; la celda que nos toca ya está destacada en la Tabla 2 |
| «qué costaría» + «preguntas» | **una** | los tres bloqueos como tira de paneles y las preguntas en rejilla 2 × 2 |

**Nada de lo que salió de las láminas se perdió: está en el guion hablado.** La crítica del
paper a la interpretación post-hoc, los dos puntos donde nuestro trabajo coincide con el de
ellos, y las dos diferencias entre la formulación del paper y nuestro modelo se cuentan
hablando.

El guion de las fusionadas se **reescribió**, no se pegó, y ninguna estrenó las aperturas de
párrafo formulaicas que la primera pasada había corregido:

| Lámina fusionada | Suma de los originales | Ahora |
|---|---|---|
| qué propone (con la ficha del paper) | 229 | 225 |
| ecuación 2, el orden | 454 | 268 |
| qué implica para nuestro modelo | 452 | 316 |
| qué reportan y el contraste | 441 | 373 |
| qué costaría y qué preguntar | 472 | 360 |

El guion completo bajó de **3705 a 3199 palabras**.

Los dos numéricos que salieron eran ilustrativos, no resultados: no hay ningún número del
paper ni nuestro que se haya ido con ellos.

## Decisiones de construcción

### 1. Tipografía de las ecuaciones: Barlow con fallback, NO Cambria Math

Barlow **no trae griegas** (`α β ψ γ λ Σ`) ni `ℝ ∈ → ⊗`, y este deck es de ecuaciones, así
que el problema pesa mucho más que el de las cuatro flechas del B7. El template embebe
Barlow **y Cambria Math**, así que declarar Cambria Math en esos glifos era una opción real
y con la ventaja de viajar embebida.

**Se rasterizaron las dos y se miró.** Gana Barlow con el fallback del sistema: sus griegas
salen en un sans de peso parecido y la línea se lee homogénea, mientras que las de Cambria
Math son serif finas y contrastan con el Barlow que las rodea. Verificado con
`FONTCONFIG_FILE` apuntando a `clam_testing2/fonts/fonts.conf`, o sea con Barlow real.

`pdffonts` sobre el PDF lista `Barlow-Bold` y `Barlow-Regular` embebidos, más `DejaVuSans`,
que es el fallback de esos glifos y **no es un defecto**.

### 2. Subíndices y superíndices REALES

`_add_runs()` (portado de `scripts/generate_clam_mammoth_pptx.py`, con Barlow en vez de
Carlito) emite runs con `baseline` OOXML: `_x` / `_(xx)` subíndice, `^x` / `^(xx)`
superíndice. Hace falta porque Unicode no tiene subíndice para casi ninguna letra, y acá se
escriben cosas como `M_(ij)`, `w_j`, `β_j`, `A^p`.

**Gotcha que ya mordió:** en una tabla con `markup=True`, el `_` de `model_clam.py` se
interpretó como subíndice y el archivo quedó escrito **«model_lam.py»** con la `c` chiquita.
Se escapa con `model\\_clam.py`.

### 3. Los paneles se dimensionan midiendo el texto

El chequeo programático de conformidad da «todo limpio» con texto que desborda su caja,
porque nadie mide el texto ([[deck-qa-puntos-ciegos-chequeo]]). En la primera pasada **seis
láminas** tenían la última línea de un panel afuera, y una tenía una tabla montada sobre un
panel.

`text_w()` mide con los TTF de Barlow instalados bajo containment, `wrap_lines()` cuenta las
líneas reales dentro del ancho disponible, y `panel(..., h=None)` calcula su propio alto. La
posición del panel siguiente se toma de `Emu(sp.height).inches`, no de una constante.

`auditar(prs)` corre antes del escalado y avisa de tres cosas: texto que no entra en su caja,
shapes fuera del lienzo y cuerpos por debajo del mínimo del template (7 pt). Ignora los
shapes rotados para los límites, porque un shape a 270° reporta su bbox sin rotar y daba
falso positivo. **No reemplaza mirar las láminas**: caza la clase de defecto que más apareció
acá, nada más.

### 4. Extracción de la Fig. 2

`pdftoppm -f 4 -l 4 -r 400` sobre el PDF y recorte por perfil de contenido: la figura vive
entre las filas 402 y 1221 de la página, con el caption abajo separado por una franja
blanca. Los tres paneles se cortan del recorte grande. La figura del paper es la **única
imagen** del deck; todo lo demás es nativo.

## Guion del presentador

Prosa hablada corrida, sin etiquetas de fase, en primera persona
([[notas-presentador-guion-didactico]]). Pasado por `@humanizer-es`: el vocabulario salió
limpio y **los tells eran de ritmo**, como suele pasar en un guion maduro. Los dos
dominantes, con su corrección:

- **Diez láminas abrían su último párrafo con «Y »**. Quedaron cero.
- **Casi todos los párrafos medios abrían señalando una posición** («La tabla de la
  derecha…», «El panel de la derecha…»), que es cadencia de máquina recorriendo un plano.
  Bajaron de catorce a seis, que es lo que la convención pide para seguir la figura.

Más «vale la pena» ×3 → cero. El largo de oración quedó con mediana 15 palabras, decil
inferior 5 y superior 29, y 47 oraciones de ocho palabras o menos: variedad suficiente para
leerlo en voz alta.

Al fusionar el 31-jul se verificó que ninguno de los párrafos reescritos reintrodujera esas
dos cadencias: ningún párrafo de cierre abre con «Y », y los que abren señalando una
posición siguen siendo seis en todo el deck.

## Lo que NO se hizo

- ~~La fecha de la lámina de título es la de construcción.~~ **Resuelto el 31-jul**: Ernesto
  confirmó que la reunión es **el viernes 07/08/2026** y `FECHA_REUNION` ya la tiene.
- Las ecuaciones **3 a 10 no están explicadas** una por una. El plan de cómo desarmarlas está
  en la §6.2 del insumo.
- No se tocó nada de GPU, ni se descargó nada del repositorio ni del dataset de SI-MIL.
