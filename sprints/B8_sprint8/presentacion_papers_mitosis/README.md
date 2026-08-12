# Deck de los cuatro papers (reunión con Sebastián, 12-ago-2026)

> **Estado al 12-ago-2026 (mañana): a medias.** Están las cuatro figuras extraídas, su script
> y el **QA visual de las cuatro cerrado** (§2), más la descripción de qué muestra cada una.
> **El deck no existe todavía**: no hay `generate_papers_deck.py` ni `.pptx`. La sesión que
> siga lo construye con el contenido que ya está escrito (§3) y **sin reabrir ninguna imagen**.

## 1. Qué es

Diez láminas sobre los **cuatro papers** que se abordan en la reunión, con la **figura
original de los autores** en cada lámina de paper y notas del presentador que cargan el peso
explicativo: se leen en vivo y sirven para estudiar mirando la figura.

**Los cuatro, y de dónde salió cada uno:**

| | Paper | Origen | Tarea |
|---|---|---|---|
| 1 | PU learning, Zhao et al., MELBA 2022 | nuestra búsqueda del 2-ago | mitosis |
| 2 | ZoomMIL, Thandiackal et al., ECCV 2022 | nuestra búsqueda del 2-ago | mitosis y escala |
| 3 | NPKC-MIL, Wang y Yuan, iScience 2024 | Sebastián, 6-ago | grado nuclear |
| 4 | Pleomorfismo nuclear, Mercan et al., npj Breast Cancer 2022 | Sebastián, 6-ago | grado nuclear |

**CellViT y MS-CLAM no entran.** El plan aprobado el 11-ago los daba por parte del cuarteto;
Ernesto lo corrigió a mitad de la sesión de construcción. El cuarteto real queda **simétrico,
dos papers por tarea**, y ese es el encuadre del deck.

## 2. Qué hay en este directorio

```
prep_assets_papers.py   extrae y recorta las 4 figuras de los PDF  ← LISTO
assets/                 los 4 PNG, versionados                     ← LISTO, con QA visual
README.md               este archivo
generate_papers_deck.py                                            ← FALTA
Papers_Mitosis.pptx     gitignored por `sprints/**/*.pptx`          ← FALTA
```

### Las figuras

Se corre una vez y deja los cuatro PNG en `assets/`:

```bash
PYTHONPATH=/media/administrador/Storage1/sdonoso/clam_testing2/.pylibs \
/home/sdonoso/miniconda3/envs/clam_latest/bin/python \
  sprints/B8_sprint8/presentacion_papers_mitosis/prep_assets_papers.py
```

| PNG | Figura | Página | Tamaño | ar |
|---|---|---|---|---|
| `fig_pulearning.png` | Fig. 1 de Zhao et al. | 14 | 1840 × 1445 | 1,27 |
| `fig_zoommil.png` | Fig. 1 de Thandiackal et al. | 2 | 2615 × 983 | 2,66 |
| `fig_npkcmil.png` | Fig. 1 de Wang y Yuan | 4 del PDF (3 del paper) | 1796 × 1280 | 1,40 |
| `fig_pleomorfismo.png` | Fig. 1 de Mercan et al. | 2 | 1833 × 594 | 3,09 |

Las páginas se verificaron buscando el texto del epígrafe dentro de cada página, no de
memoria. Las cajas de recorte se **midieron una vez** y quedan como constantes en el script;
`_caja_por_contenido()` está para re-proponerlas si algún PDF cambia, no para decidirlas en
cada corrida.

**La de PU learning es la única que no va entera**: la original es una grilla de cuatro
métodos por tres parches y proyectada no se lee. Se recompone con **tres columnas** (anotación
completa, baseline y método propuesto) y **dos filas**, que son las que sostienen el
argumento. Queda afuera la columna del competidor especializado (BDE) y la fila de las flechas
azules, que es la que compara contra él. **Eso tiene que ir dicho en el pie de la lámina.**

**QA visual COMPLETO sobre las cuatro** ([[image-api-qa-limit]]). Las dos primeras se
miraron el 11-ago apenas generadas; el primer recorte de PU dejaba asomar una tira de la
tercera fila por abajo y se corrigió (`PU_FILA` termina 8 px antes). Las dos que faltaban se
miraron el **12-ago de entrada**, antes de cualquier otra cosa, y **pasan las dos**: paneles
completos, epígrafes enteros, y en ZoomMIL las etiquetas `10x` / `2.5x` sin cortar, en
pleomorfismo la barra de color incluida. **Ninguna necesita re-recorte.**

### Qué muestra cada figura (para escribir el pie y el guion sin reabrir la imagen)

Se anota acá porque leer las cuatro imágenes cuesta contexto y el QA ya las miró: la sesión
que escriba el generador **no necesita abrirlas de nuevo**.

| PNG | Qué se ve |
|---|---|
| `fig_pulearning.png` | Grilla de parches de tejido, tres columnas por dos filas. Las columnas son anotación completa, baseline y método propuesto; cada parche lleva marcadas las células detectadas. Queda afuera la columna del competidor especializado (BDE) y la fila de las flechas azules |
| `fig_zoommil.png` | Cuatro esquemas en perspectiva de la misma lámina, rotulados abajo: **(a) Pathologist**, **(b) Single-scale MIL**, **(c) Multi-scale MIL**, **(d) ZoomMIL (ours)**. Cada uno cruza dos planos etiquetados `2.5x` y `10x`; en (d) la grilla del plano `10x` está pintada como mapa de calor sobre las dos regiones tumorales |
| `fig_npkcmil.png` | Diagrama de bloques con seis rótulos rojos: **A** extracción de features del parche por transfer learning, **B** ordenamiento de los parches por puntaje de atención (columna de parches de `low` a `high`), y las tres pérdidas en cajas punteadas rojas, **C** de lámina (attention pooling), **D** de parche (CNN) y **E** de núcleos (red convolucional de grafos). **F** es el ⊕ que las suma y da `diagnosis`. La rama de núcleos sale del extremo `high` de la columna B, que es la lectura visual del «8 parches de atención más alta» |
| `fig_pleomorfismo.png` | Tres paneles rotulados abajo: **Input slide** (la lámina H&E entera), **Tumor output** (la misma lámina con el tumor invasivo resaltado en gris) y **Pleomorphism spectrum** (el puntaje continuo pintado sobre el tejido, con un recuadro naranja de detalle a gran aumento y la barra de color verde a rojo a la derecha). Entre panel y panel, dos redes dibujadas como grafo, azul la primera y magenta la segunda |

## 3. De dónde sale el contenido de las diez láminas

Todo escrito y verificado contra los PDF. **No hace falta reabrir ningún paper.**

- Papers 1 y 2, y el marco de la recomendación:
  [`../tareas_geometricas/hojas_reunion.md`](../tareas_geometricas/hojas_reunion.md), hojas 0,
  1 y 3 más el anexo de MIDOG.
- Papers 3 y 4, y el encuadre del cuarteto:
  [`../papers_11_agosto/hojas_papers_nuevos.md`](../papers_11_agosto/hojas_papers_nuevos.md),
  hojas 0, 5 y 6.
- Mecanismos desde cero, si una nota necesita explicar algo:
  [`../tareas_geometricas/papers_explicados.md`](../tareas_geometricas/papers_explicados.md).

**Cero números nuevos**: si una cifra no está en esos documentos, no entra al deck.

### Las diez láminas

| # | Lámina | Qué lleva |
|---|---|---|
| 1 | Portada | heredada del template, retitulada |
| 2 | Por qué estos cuatro | diagrama nativo: dos tareas, dos papers cada una; y el criterio que los ordena, que es qué supervisión exige cada uno contra la que tenemos |
| 3 | PU learning | figura + qué propone · los números · lo que lo frena |
| 4 | ZoomMIL | idem |
| 5 | NPKC-MIL | idem, con la rama de núcleos sobre los 8 parches de atención más alta |
| 6 | Pleomorfismo nuclear | idem, con el 0,5 µm/px y el promedio de 10 patólogos |
| 7 | Los cuatro en un cuadro | tabla nativa: supervisión que exige · compatible con lo nuestro · qué habilita · costo · lo que lo frena |
| 8 | La recomendación | dos carriles: mitosis sigue siendo D en dos pasos; grado nuclear entra por el paper de pleomorfismo, que es el único que calza con nuestra escala |
| 9 | Las tres cosas que hay que decir sí o sí | el paso 1 de mitosis no depende del paper de Zhao · el régimen de anotación que ellos evalúan no es el nuestro · la escala juega al revés en cada rama |
| 10 | Las preguntas que deciden | mitosis: ¿hay más láminas anotadas y quién es «GDT»? · grado nuclear: ¿se puede conseguir puntaje por región, y hay GPU para segmentar núcleos sobre los mejores parches? |

El molde de las cuatro láminas de paper es el mismo para que se lean igual: figura a la
izquierda con la procedencia al pie (`pie_lineas`), tres bloques cortos a la derecha con la
gramática del template, y `takeaway_bar` de remate. Es la excepción explícita a «todo
nativo»: **la figura de un paper va como imagen**; la tabla de la 7 y el diagrama de la 2 van
nativos.

**El molde no puede fijar el ancho de la columna izquierda**, y conviene saberlo antes de
maquetar: las cuatro figuras van de **1,27 a 3,09** de relación de aspecto (§2), así que una
columna de ancho fijo deja a ZoomMIL y a pleomorfismo dibujadas a menos de la mitad del alto
disponible mientras sobra blanco debajo. Lo que se fija es el **alto** de la caja de figura,
más o menos 3,0 pulgadas entre la banda teal y la barra de remate; el ancho sale de
`alto × ar`, topeado para que la columna de bloques no baje de unas 4,1 pulgadas. Con eso cada
figura queda tan grande como su forma permite y las cuatro láminas siguen leyéndose iguales.
El pie va **pegado al borde inferior real de la imagen dibujada**, no al de la caja, si no
queda flotando lejos en las anchas.

## 4. Reglas que gobiernan el generador cuando se escriba

- Se construye **SOBRE** `sprints/B7_sprint7/Modelo OncoMets Spatial V1 Deep-LLM-V.pptx`,
  nunca con `Presentation()`: el template embebe Barlow y es la razón real de que un deck
  «no parezca el template» ([[deck-template-fuentes-embebidas]]).
- `forzar_barlow(prs)` antes de guardar, y `auditar(prs)` en cero avisos.
- Helpers a copiar del generador del B8 (solo los que este deck usa, no el módulo entero):
  `base_from_template` · `new_slide` · `_add_runs` / `_set_runs` / `add_textbox` · `notes` ·
  `_rect` · `header_oncomets` · `content` · `add_image_fit` · `caption` · `takeaway_bar` ·
  `_proc` / `_proc_claro` / `_dato` / `_grupo` / `_conn` · `pie_lineas` · `_num` ·
  `simple_table` · `forzar_barlow` · `auditar` · `retitular_portada` · `reflow_onco` ·
  `scale_deck_to_1610` · las funciones de medición de texto (`text_w`, `wrap_lines`,
  `_alto_bloque`, `panel`).
- Notas: punteo de tres a cinco renglones de una línea, línea en blanco, y después el guion
  hablado en prosa corrida. Sin guiones largos, sin la palabra «palanca», sin la expresión
  «al revés» (rechazada por coloquial, [[deck-estilo-sin-rayas-ni-palanca]]), números con coma
  decimal en las láminas y en letras en el guion.

**De dónde se copian los helpers, por rango de líneas** (relevado el 12-ago sobre
`generate_b8_deck.py`, 2594 líneas). Extraerlos con `sed -n '<rango>p'` en vez de leer el
archivo: son seis bloques contiguos y cubren la lista de arriba entera.

| Rango | Qué trae |
|---|---|
| `215-276` | paleta Deep-LLM-V, fuentes, geometría de trabajo y la cabecera OncoMets |
| `281-628` | `_blank` · `base_from_template` · `new_slide` · `_add_runs` · `_set_runs` · `add_textbox` · `notes` · `_rect` · `header_oncomets` · `content` · `add_image_fit` · `add_card` · `caption` · `takeaway_bar` · los cinco arquetipos de diagrama · `eq` · `simple_table` |
| `633-704` | medición de texto real (`_face`, `text_w`, `wrap_lines`, `_alto_bloque`) y `panel` |
| `808-812` | `_num` |
| `919-930` | `pie_lineas` |
| `1161-1362` | `CONTENT_TOP_NEW` / `SAFE_BOTTOM` · `_scale_block` · `reflow_onco` · `forzar_barlow` · `scale_deck_to_1610` · `auditar` · `_set_solo_run` · `retitular_portada` |

**Dos cosas que hay que tocar al copiarlos:**

- `retitular_portada` trae hardcodeado «OncoMets · Sprint 8»: acá el título es otro, así que
  toma el texto por parámetro.
- **`auditar` NO ve dos defectos que este deck puede tener**, y son distintos de los que ya
  lista [[deck-qa-puntos-ciegos-chequeo]]: (a) una tabla nativa cuyo texto no entra, porque
  `row_h` de `simple_table` es un mínimo y PowerPoint crece la fila por su cuenta; y (b) una
  pila de `panel(h=None)` que se pasa hacia abajo y se mete debajo de la `takeaway_bar`, que
  no es «fuera del lienzo» y por eso no dispara aviso. Como acá las cuatro láminas de paper
  son tres paneles apilados de alto automático, el generador tiene que **imprimir el borde
  inferior del último panel de cada lámina** y compararlo contra el alto de la barra de
  remate.
- `python-pptx` **no** está en `clam_latest`: va por
  `PYTHONPATH=/media/administrador/Storage1/sdonoso/clam_testing2/.pylibs` (1.0.2).
