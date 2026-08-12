# Deck de los cuatro papers (reunión con Sebastián, 12-ago-2026)

> **Estado al 11-ago-2026 (noche): a medias.** Están las cuatro figuras extraídas y su script.
> **El deck no existe todavía**: no hay `generate_papers_deck.py` ni `.pptx`. La sesión que
> siga lo construye con el contenido que ya está escrito (§3).

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

**QA visual hecho** sobre `fig_pulearning.png` y `fig_npkcmil.png` leyéndolos apenas
generados, que es cuando se puede ([[image-api-qa-limit]]). El primer recorte de PU dejaba
asomar una tira de la tercera fila por abajo y se corrigió (`PU_FILA` termina 8 px antes).
**Faltan de mirar `fig_zoommil.png` y `fig_pleomorfismo.png`**: sus cajas salieron del perfil
de tinta de la página, que es fiable, pero nadie los miró.

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
  hablado en prosa corrida. Sin guiones largos, sin la palabra «palanca», números con coma
  decimal en las láminas y en letras en el guion.
- `python-pptx` **no** está en `clam_latest`: va por
  `PYTHONPATH=/media/administrador/Storage1/sdonoso/clam_testing2/.pylibs` (1.0.2).
