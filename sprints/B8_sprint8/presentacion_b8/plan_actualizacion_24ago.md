# Actualizar el deck del B8 para la reunión del lunes 24-ago

> **Escrito el 22-ago-2026 (sesión 21, sesión de PLAN).** NO ejecutado: la sesión se cerró
> con el plan escrito para que una sesión limpia lo ejecute. Origen:
> [`correcciones.txt`](correcciones.txt), que Ernesto escribió sobre el deck del 19-ago, más
> las cuatro decisiones que tomó al revisar este plan (necrosis fuera, fecha 24-ago, los
> objetivos reemplazan la lámina de título, y solo material ya medido).
>
> Los paths de los enlaces son **relativos a la raíz del repo**, no a este directorio.


## Contexto

El deck `CLAM_Sprint8.pptx` se armó el 19-ago con 16 láminas y quedó desactualizado: no tiene
nada de la **Fase A**, que cerró entera el 21-ago (A0, A1, A2, A2.bis, A3, A4), y arrastra
correcciones de forma que Ernesto listó en
[correcciones.txt](sprints/B8_sprint8/presentacion_b8/correcciones.txt).

**Restricción que ordena todo el trabajo: no entra ningún resultado nuevo.** B3 (job 5069) y
B1 (job 5070) siguen `PD` detrás de un job ajeno con `TimeLimit=UNLIMITED`, y B2 nunca se
lanzó. El deck se arma **solo con lo que ya está medido en disco**.

Consecuencias decididas con Ernesto:

- **La necrosis queda FUERA del deck.** Lo pedido era comparar la necrosis de HoVer-NeXt
  contra las marcas del patólogo, y esa mitad exige la clase `dead`, que vive solo en
  PanNuke (B2, sin lanzar). A4 (la atención de CLAM sobre la necrosis, AUC 0,899) **no se
  presenta**: sin la mitad de HoVer-NeXt contesta otra pregunta.
- El brazo del gate de carcinoma invasivo se presenta **con Mammoth**, que es el único
  checkpoint que existe, y con esa salvedad escrita.
- Fecha del deck: **24 de agosto de 2026**.

Resultado: **17 láminas** (16 − 3 eliminadas + 4 nuevas).

---

## Archivo a modificar

Prácticamente todo el trabajo es sobre un solo archivo:
[generate_b8_deck.py](sprints/B8_sprint8/presentacion_b8/generate_b8_deck.py) (2897 líneas).
El deck se regenera end-to-end con él; **no se edita el `.pptx` a mano**.

```bash
PYTHONPATH=/media/administrador/Storage1/sdonoso/clam_testing2/.pylibs \
/home/sdonoso/miniconda3/envs/clam_latest/bin/python \
  sprints/B8_sprint8/presentacion_b8/generate_b8_deck.py
```

Helpers existentes que se reusan sin escribir nada nuevo: `content`, `add_textbox`, `panel`,
`simple_table`, `_grupo`, `caption`, `pie_lineas`, `takeaway_bar`, `add_image_fit`,
`status_done`, `status_progress`, `barras_divergentes`, `escalera_capacidad`,
`barras_ranking`, `cinta_ranking`, `notes`.

---

## Estructura final del deck

| # | Lámina | Estado |
|---|---|---|
| 1 | Portada (template) | fecha → 24-ago |
| 2 | **Objetivos del sprint** | NUEVA en esa posición (hereda el molde de la ex-13) |
| 3 | ¿Recortar expertos o slots? | correcciones |
| 4 | ¿La atención de CLAM cae sobre los núcleos de la mitosis? | correcciones + título |
| 5 | Atención y marcas del patólogo | solo notas |
| 6 | El resultado, grupo por grupo | correcciones |
| 7 | Los 28 parches de mitosis | correcciones |
| 8 | La atención acierta y la clasificación falla | correcciones + título |
| 9 | SI-MIL: qué propone | correcciones |
| 10 | SI-MIL: resultados y costo | sin cambios |
| 11 | HoVer-NeXt y la clase de mitosis | correcciones |
| 12 | Resultados: recortar y detectar | correcciones (tabla) |
| 13 | El detector sobre la lámina completa | correcciones + título |
| 14 | **CLAM, Mammoth y el detector a igual carga** | NUEVA (A2.bis) |
| 15 | **El checkpoint de carcinoma invasivo** | NUEVA (A2) |
| 16 | **Las 13 que se escapan sí estaban segmentadas** | NUEVA (A0) |
| 17 | **Las 164 detecciones sin marca** | NUEVA (A1) |

Se eliminan: `lam_simil_ramas` (ex-10), `lam_simil_reporte` (ex-11) y
`lam_objetivos_propuestos` en su posición de cierre (ex-13, se muda a la 2).

---

## 1. Lámina 2 — los objetivos reemplazan la lámina de título

`TPL_KEEP` pasa de `(0, 1)` a `(0,)`: la lámina de título del template se retira y la
posición 2 la ocupa una lámina nuestra.

- `retitular_portada()` deja de devolver `prs.slides[1]`; ajusta solo la portada y le pone
  `FECHA_REUNION = "24 de agosto de 2026"` como caption al pie.
- Las notas de apertura, que hoy cuelgan de la lámina de título, pasan a la portada.
- Nueva `lam_objetivos_sprint(prs)`, llamada entre `lam_portada` y `lam_grid`. Replica el
  molde **exacto** de `lam_objetivos_propuestos` (título 32 pt, filas de 19 pt sobre 7,75",
  `row_tops = 1.10 + i*0.68`, `row_h = 0.62`, marcador de estado en `x = 8.98`).
- Nueva constante `OBJETIVOS_SPRINT`, una línea por objetivo con su estado real. Los cuatro
  propuestos al abrir el sprint más los dos que aparecieron durante:

  1. Escalar a la tarea la medición de capacidad del modelo con expertos. → `status_done`
  2. Decidir si conviene recortar expertos o unidades. → `status_done`
  3. Medir si la atención cae sobre las mitosis que marcó el patólogo. → `status_done`
  4. Elegir y justificar la dirección de la rama de mitosis. → `status_done`
  5. Investigar e implementar un detector de mitosis a nivel de núcleo. → `status_progress("En curso")`
  6. Encadenar la atención con el detector y cruzarla contra las marcas. → `status_progress("En curso")`

  Los 5 y 6 son los que Ernesto pidió explicitar como surgidos a lo largo del sprint.
- `build()` deja de llamar a `lam_objetivos_propuestos`; la función y `OBJETIVOS_PROP` se
  retiran del archivo.

## 2. Lámina 3 — el grid

- Borrar la línea `"El signo se da vuelta entre peldaños y la desviación supera a la media…"`
  ([generate_b8_deck.py:1416](sprints/B8_sprint8/presentacion_b8/generate_b8_deck.py#L1416)).
- Borrar `"Abajo, AUC medio por brazo con el eje desde 0,72."` de la línea de contexto
  ([:1421](sprints/B8_sprint8/presentacion_b8/generate_b8_deck.py#L1421)).
- **Hacer legible el diagrama divergente**, que es el pedido de fondo. En
  `barras_divergentes` ([:864](sprints/B8_sprint8/presentacion_b8/generate_b8_deck.py#L864)):
  - retirar del dibujo la leyenda de escala (`± 0,1 AUC`) y la de los cuadros;
  - dejar los cuadros por partición dibujados, sin rótulo;
  - poner sobre la figura un encabezado de eje que nombre la métrica y las dos direcciones:
    `← a favor de recortar expertos · diferencia de AUC entre los dos recortes · a favor de recortar unidades →`.
- Notas: agregar cómo se lee el diagrama (qué es la barra, qué es la línea gris, qué es cada
  cuadro y por qué el relleno indica la dirección), que es lo que Ernesto pidió que no
  estuviera escrito en la lámina pero sí dicho.

## 3. Lámina 4 — la pregunta medible

- Título → **«¿La atención de CLAM cae sobre los núcleos de la mitosis?»**
- Eliminar la caja con la cita del patólogo (`_grupo` + textbox,
  [:1508-1514](sprints/B8_sprint8/presentacion_b8/generate_b8_deck.py#L1508)): el título
  absorbe su contenido y la frase se cuenta hablando.
- En el bloque del estadístico ([:1524-1531](sprints/B8_sprint8/presentacion_b8/generate_b8_deck.py#L1524)):
  quitar `«que es la U de Mann-Whitney normalizada»` y borrar entera la línea
  `«Las dos lecturas quedaron registradas antes de medir…»`.
- Reescribir la cuenta de pares ([:1559](sprints/B8_sprint8/presentacion_b8/generate_b8_deck.py#L1559)),
  que hoy es una fórmula comprimida, en dos renglones de lenguaje corriente:
  > Se compara cada uno de los 28 parches con mitosis contra cada uno de los 4771 restantes.
  > En el 89 % de esas comparaciones, el parche con mitosis recibió más atención.
- Eliminar las tres tarjetas `PROPS`
  ([:1563-1585](sprints/B8_sprint8/presentacion_b8/generate_b8_deck.py#L1563)). Su contenido
  baja al guion.
- Con el alto liberado (≈1,4"), agrandar las dos cintas de ranking, que son lo que hay que ver.
- Notas: incorporar que **tener las marcas del patólogo es lo que permite medir** si el modelo
  atiende las zonas marcadas — sin ellas solo habría un mapa de calor sin referencia.

## 4. Lámina 5 — los mapas (solo notas)

Reescribir el guion entero: minimalista, preciso y pedagógico, **sin mencionar que la lámina
se divide en dos regiones de escaneo**. Lo que sí tiene que decir, con los números de
`PROVENANCIA` ([:165](sprints/B8_sprint8/presentacion_b8/generate_b8_deck.py#L165)):

- **61 polígonos** dibujados por el patólogo en QuPath sobre la lámina 129741;
- su reparto por clase: 26 mitosis · 14 núcleos de alto grado · 6 necrosis · 5 células
  inmunes · 5 tumor · 2 tejido adiposo · 1 estroma · 2 fondo;
- **4799 parches** en la lámina, **163** bajo alguna marca, **28** con mitosis;
- y la respuesta visual: los parches marcados caen sobre el rojo del mapa de CLAM.

## 5. Lámina 6 — la escalera por grupo

- Eliminar las dos tarjetas de incertidumbre `± 0,039 si cambia el modelo` y
  `± 0,080 si cambian las marcas`
  ([:1738-1749](sprints/B8_sprint8/presentacion_b8/generate_b8_deck.py#L1738)).
- Reemplazar el bloque del bigote
  ([:1730-1735](sprints/B8_sprint8/presentacion_b8/generate_b8_deck.py#L1730)) por dos
  renglones que digan qué se muestra y cómo se midió:
  > Cada barra es el AUC de la atención sobre los parches que el patólogo marcó de esa clase,
  > medidos contra todo el resto de la lámina.
  > La línea sobre cada barra es la precisión que da el número de parches marcados: cuantos
  > menos hay, más larga.
- Con el alto liberado (≈0,74"), agrandar `barras_ranking`.
- Las dos incertidumbres bajan al guion.

## 6. Lámina 7 — los 28 parches

- Reescribir el cierre del bloque de escala
  ([:1846-1850](sprints/B8_sprint8/presentacion_b8/generate_b8_deck.py#L1846)):
  > 36 px de lado contra los 256 del parche. De ahí que 10 de las 26 caigan sobre un borde, y
  > que el vector con el que el modelo representa el parche resuma, sobre todo, tejido que no
  > es la mitosis.
- Notas: explicar qué implica el 2-4 % — que el modelo comprime el parche entero a un solo
  vector, y que la mitosis aporta a ese vector una fracción muy chica de la señal, así que
  puede quedar diluida aunque el parche esté bien elegido. Es el puente a la lámina siguiente.

## 7. Lámina 8 — mira bien y responde mal

- Título → **«La atención acierta y la clasificación falla»**.
- Explicitar las 4 clases de la tarea, verificadas contra
  `environ/csv/dataset_grado_histologico_tasa_mitotica_label.csv`:
  `score_1` (tasa baja, 636) · `score_2` (intermedia, 287) · `score_3` (alta, 254) ·
  `no_identificado` (el informe no la consigna, 693). Va como línea bajo el encabezado.
- Eliminar el `caption` `«Los folds 0 y 2 son los dos únicos…»`
  ([:1916-1918](sprints/B8_sprint8/presentacion_b8/generate_b8_deck.py#L1916)); el
  encabezado ya dice que ninguno la tuvo en entrenamiento.
- Reescribir el bloque central
  ([:1924-1926](sprints/B8_sprint8/presentacion_b8/generate_b8_deck.py#L1924)):
  > El modelo que mejor localiza las mitosis es el que peor clasifica la lámina. El problema
  > no está en elegir los parches: está en la información que sobrevive cuando el parche se
  > resume en un vector.
- Eliminar la `takeaway_bar` del desacople
  ([:1927](sprints/B8_sprint8/presentacion_b8/generate_b8_deck.py#L1927)).

## 8. Lámina 9 — SI-MIL

- Bajar el nivel de detalle arquitectónico en la lámina: se retiran las dimensiones y los
  nombres de módulo, y queda **qué propone** y **por qué**.
- Notas, que es donde Ernesto pidió la claridad:
  - SI-MIL usa **HoVer-Net como front-end**: segmenta y clasifica los núcleos de cada parche
    en 5 clases (`papers_b8.md:87`);
  - de ese mapa de núcleos salen las **246 mediciones por parche** — 205 morfométricas
    (10 propiedades × 4 estadísticos × 5 clases, más 5 conteos) y el resto de grafo celular y
    heterogeneidad espacial (`simil_estudio.md:40`);
  - cada una tiene **nombre legible de patología** («células neoplásicas: asimetría de la
    solidez»), y eso es lo que hace que la predicción sea el reporte.

## 9. Lámina 11 — HoVer-NeXt

- **Eliminar los dos `panel`** («Por qué encaja», «Qué corrimos»,
  [:2467-2478](sprints/B8_sprint8/presentacion_b8/generate_b8_deck.py#L2467)) y ampliar la
  Figura 1 a todo el ancho disponible (de 4,90" a ≈9,28"; `ar = 1,621` fija el alto).
- Notas: recorrer **cada paso del diagrama** — teselado de la lámina, paso por la red,
  cosido de las teselas solapadas, y la combinación de las dos salidas en el mapa de
  instancias.
- Notas: **corregir la confusión que planteó Ernesto**. Las 246 dimensiones son de SI-MIL, no
  de HoVer-NeXt. Las dimensiones reales de HoVer-NeXt, verificadas contra
  `hover_next_reference/lizard_convnextv2_tiny/params.toml` y `src/inference.py:249-250`:
  - **entrada**: tesela RGB (3 canales) a 0,5 µm/px;
  - **codificador**: ConvNeXtV2-tiny (`convnextv2_tiny.fcmae_ft_in22k_in1k`);
  - **decodificador de instancia**: 5 canales — 2 mapas de regresión de distancia + 3 clases
    (fondo / interior del núcleo / borde);
  - **decodificador de clase**: 8 canales — fondo + las 7 clases de núcleo de
    Lizard-Mitosis (`neutrophil`, `epithelial-cell`, `lymphocyte`, `plasma-cell`,
    `eosinophil`, `connective-tissue-cell`, `mitosis`);
  - la combinación de las dos salidas es el mapa final, donde cada núcleo es un objeto con
    su clase.

## 10. Lámina 12 — resultados: recortar y detectar

Simplificar `CRUCE_CONJUNTA` ([:2439](sprints/B8_sprint8/presentacion_b8/generate_b8_deck.py#L2439))
de 5 columnas a 3. Se van «Ambas» (redundante con la última) y «Cota mín( )» (una cota floja
que el propio pie declaraba floja):

| Recorte por atención | Marcas dentro del recorte | Y además detectadas |
|---|---|---|
| 4,0 % de la región | 12 de 26 | 8 |
| 7,6 % | 15 de 26 | 10 |
| **12,0 %** | **19 de 26** | **11** |
| la región entera | 26 de 26 | 13 |

- Agregar al pie qué es el porcentaje: **la fracción de los 2496 parches de la región anotada
  que quedan encendidos tras el recorte**, con su superficie al lado.
- El pie conserva la línea de unidad (marcas, no parches) y la de «sin precisión, y es
  deliberado». Se retira la línea de la cota mínima.

## 11. Lámina 13 — el detector solo

- Título: `«La herramienta sola, sin recorte»` → **«El detector sobre la lámina completa»**.
- Reescribir el pie ([:2765](sprints/B8_sprint8/presentacion_b8/generate_b8_deck.py#L2765)):
  > Del brazo sin recorte al del 12 %, la superficie a revisar baja 16 veces y las marcas
  > recuperadas bajan de 13 a 11.
- Reescribir la `takeaway_bar` ([:2768](sprints/B8_sprint8/presentacion_b8/generate_b8_deck.py#L2768)):
  > El recorte reduce la superficie a revisar, no aumenta las marcas recuperadas.

---

## 12. Las cuatro láminas nuevas

Todas con datos ya en disco. Tres son **tablas nativas** (regla del deck: tablas, gráficos y
diagramas nativos, nunca PNG de matplotlib) y una lleva las láminas de contacto, que son
fotografías de tejido y por eso caen en la excepción legítima.

### Lámina 14 — `lam_escalera_brazos` · CLAM, Mammoth y el detector a igual carga

Fuente: [a2bis_escalera_brazos.md](sprints/B8_sprint8/encargos_sebastian/a2bis_escalera_brazos.md) §2-§3,
verificable contra `results/b8_hovernext_129741/escalera_brazos/escalera_brazos.csv`.

`simple_table` con la comparación a **carga fija** (cuántos objetos pide cada brazo para
llegar al mismo recall), que es lo que evita el artefacto de comparar a K fijo:

| llegar a | CLAM | Mammoth | CLAM∩Mammoth | CLAM∪Mammoth | HoVer-NeXt |
|---|---|---|---|---|---|
| 8 de 26 | 71 parches | 70 | **33** | 80 | — |
| 13 de 26 | 130 | 95 | **84** | 126 | **82 núcleos** |
| 19 de 26 | 300 | **217** | 241 | 251 | imposible |
| 26 de 26 | 2496 | 2496 | 2496 | 2496 | imposible |

Bloque de conclusión + pie con las tres salvedades que el documento exige: la unión nunca es
el mejor brazo a carga fija; **Mammoth no se suma a CLAM, lo reemplaza**; y el detector está
**topado en 13 de 26** — por encima de ahí no es una opción a ninguna carga.

### Lámina 15 — `lam_gate_invasivo` · el checkpoint de carcinoma invasivo

Fuente: [a2_atencion_gate_invasivo.md](sprints/B8_sprint8/encargos_sebastian/a2_atencion_gate_invasivo.md)
§2-§4. Es el **encargo 1 de Sebastián**: repetir la cadena con el otro checkpoint.

Dos bloques, porque el hallazgo es justamente que discrepan:

- **Por AUC parecen equivalentes**: gate 0,865 (0,778-0,951) contra CDIS 0,919 (0,848-0,989);
  los intervalos se solapan de sobra.
- **Por recorte el gate es claramente peor**, tabla nativa con el top-K:

  | Recorte | gate de invasivo | CDIS |
  |---|---|---|
  | 4,0 % | 1 de 26 | 14 de 26 |
  | 7,6 % | 8 de 26 | 18 de 26 |
  | 12,0 % | 11 de 26 | 22 de 26 |
  | 20,0 % | 17 de 26 | 23 de 26 |

Pie obligatorio: el brazo del gate es **Mammoth** (el CLAM plano de esa tarea no existe en
disco y lo entrena un job encolado), así que **todavía no se separa si el efecto es de la
tarea o del brazo**; y el chequeo de sanidad pasa (en la región entera los dos convergen a
13 de 26).

### Lámina 16 — `lam_a0_falla_la_clase` · las 13 que se escapan sí estaban segmentadas

Fuente: [a0_segmentadas_o_no.md](sprints/B8_sprint8/encargos_sebastian/a0_segmentadas_o_no.md).
Es lo que explica por qué el número se queda en 13 de 26, y por eso va antes de las imágenes.

Tabla nativa con las dos mitades una al lado de la otra (patrón P3: el grupo acreditado es el
control positivo que hace legible al fallado):

| | acreditadas (13) | falladas (13) |
|---|---|---|
| núcleo segmentado bajo la marca | 13 | **13** |
| distancia mediana al centroide | 1,9 µm | 2,1 µm |
| clase que le puso el detector | `mitosis` ×13 | `epithelial-cell` ×12, `neutrophil` ×1 |
| instancias dentro de 15 µm | 9 | 9 |

Conclusión: **falla la cabeza de clase, no la segmentación**, y eso cambia el costo del
arreglo. Pie con la explicación de dominio: la clase de mitosis del detector se entrenó y
validó **solo en colon**, y esta lámina es de mama.

### Lámina 17 — `lam_galeria_164` · en qué se fija el detector

Fuente: [a1_galeria_177.md](sprints/B8_sprint8/encargos_sebastian/a1_galeria_177.md).
Es el pedido literal de Ernesto («imágenes de en qué se está fijando el modelo con las otras
164 mitosis que predice»).

- Figura principal: `bloque_sin_marca.png` (1852×1708, las 164 detecciones sin marca).
- Figura secundaria: `bloque_falladas.png` (928×354, las 13 marcas que se escaparon), que es
  la que se lee junto con la lámina anterior.
- Bloque de números: **145 de las 164 (88 %) caen en una sola familia** — epitelio tumoral
  denso, núcleo hipercromático y condensado; y se despega **una familia de 15** con 65 % de
  fondo (tejido laxo o borde de lámina).
- Pie obligatorio, y acá importa más que en ninguna otra lámina: **las 164 no son falsos
  positivos**. El patólogo marca solo donde la evidencia es clara, así que una detección sin
  marca puede ser una mitosis real sin marcar. **No se calcula precisión y ningún panel las
  pinta como error.** Y el parecido es **de píxeles, no semántico**.

**Assets**: las dos láminas de contacto viven hoy solo en
`results/b8_hovernext_129741/galeria_mitosis/`. Se agrega a
[prep_assets_hovernext.py](sprints/B8_sprint8/presentacion_b8/prep_assets_hovernext.py) un
paso que las copia a `assets/` con nombre propio (`galeria_sin_marca.png`,
`galeria_falladas.png`), para que el deck se reproduzca desde el generador y no dependa de un
`cp` a mano.

---

## 13. Las notas del presentador, en todas las láminas

Pedido transversal de Ernesto: **más minimalistas y objetivas**. El guion actual son
**9131 palabras (~70 min)**, que no entra en la reunión.

Se conserva la convención vigente ([[notas-presentador-guion-didactico]]): punteo de 3 a 5
renglones al abrir + guion **hablado corrido en prosa**, sin etiquetas de fase, sin números de
job ni nombres propios. Lo que cambia es la densidad:

- **Objetivo: ~4500 palabras (~35 min)**, la mitad del actual.
- Se recorta la digresión metodológica larga (la explicación de Mann-Whitney en la lámina 4
  pasa de ~600 palabras a ~150) y la repetición entre láminas del bloque de HoVer-NeXt.
- Lo que **entra** aunque el texto se acorte, porque son pedidos explícitos: cómo se lee el
  diagrama divergente (lámina 3), que las marcas del patólogo son lo que hace medible la
  pregunta (lámina 4), los conteos de polígonos y clases (lámina 5), qué implica el 2-4 %
  (lámina 7), las 4 clases de tasa mitótica (lámina 8), HoVer-Net como front-end de SI-MIL y
  las 246 mediciones (lámina 9), y las dimensiones reales de HoVer-NeXt (lámina 11).
- Pasar el resultado por `@humanizer-es`, que es el procedimiento de la convención.

---

## Verificación

1. **Regenerar** el deck con el comando de arriba. Debe imprimir
   `17 slides · 13.333x7.5` y no dejar salir ninguna advertencia de `auditar()`, que es la
   que caza texto fuera de los márgenes y runs comprimidos por `reflow_onco`.
2. **Regenerar los derivados**:
   - `sprints/B8_sprint8/presentacion_b8/sin_notas.py` → `CLAM_Sprint8_sin_notas.pptx`
   - `scripts/extraer_guion_deck.py` → `CLAM_Sprint8_guion.md`; verificar que el conteo de
     palabras que imprime esté cerca de las 4500.
3. **Rasterizar y mirar** las 17 láminas con LibreOffice bajo `FONTCONFIG_FILE` apuntando a
   `clam_testing2/fonts/`, que es lo único que hace válido el juicio tipográfico
   (`sprints/B7_sprint7/presentacion_b7/fuentes_barlow.md`). El QA automático es la capa más
   ciega de las cuatro ([[deck-qa-puntos-ciegos-chequeo]]): hay que mirar las imágenes.
   Chequear en particular las cuatro láminas nuevas y las tres cuya figura se agranda (4, 6, 11).
4. **Verificar la tipografía**: `unzip -p CLAM_Sprint8.pptx` y contar `typeface="…"` bajo
   `ppt/` — todo tiene que ser Barlow salvo Cambria Math.
5. **Cross-check de números**: cada cifra nueva contra su fuente —
   `escalera_brazos.csv`, `cruce_marcas_gate/recall_por_tolerancia.csv`,
   `a0_falladas/marcas_vs_instancias.csv`, `galeria_mitosis/familias.csv`. Ninguna cifra se
   escribe de memoria.
6. **Actualizar** `sprints/B8_sprint8/presentacion_b8/README.md` con una sección «El recorte
   del 22-ago», que es donde el archivo lleva la traza de cada rehecha.

## Lo que este plan NO hace

- **No lanza ningún job.** B2 sigue sin lanzar y B1/B3 siguen encolados; el deck no depende
  de ellos.
- **No presenta necrosis**, por decisión de Ernesto: sin la mitad de HoVer-NeXt (clase `dead`,
  solo en PanNuke) la pregunta del encargo 3 no se contesta.
- **No toca `clam_environ/`, `clam_testing/`, `hover_net/` ni `anotaciones/`**, que son
  ajenos y de solo lectura.
- **No hace `push`.** Commits locales granulares; el push lo decide Ernesto.
