# Plan: el deck del 15-sep, más visual

> Escrito el 16-sep-2026, sesión 60 (sesión de PLAN). **Nada de esto está ejecutado.** Lo toma una
> sesión limpia. Fuente única del plan: el handoff apunta acá.

## Por qué

Ernesto miró el deck del 15-sep (7 láminas) y no le gustó: **le faltan imágenes de los núcleos que
detectó HoVer-NeXt, y tiene que ser más visual y mostrar más resultados**. Hoy cada lámina de
resultado es un gráfico o diagrama nativo con viñetas y pie, y en ninguna se ve el tejido, los
núcleos detectados ni dónde cae la atención.

## Decisiones de Ernesto (16-sep)

| | |
|---|---|
| Destino | **Rehacer el deck del 15-sep**: mismo período 08/09 a 15/09, mismo nombre de archivo, mismo contenido. Nada de lo que pasó en la reunión entra acá |
| Imágenes | Las cuatro: **qué detecta HoVer-NeXt** · **O1 sobre una lámina** · **O1 núcleo a núcleo** · **mapas de atención de O3** |
| Largo | **Hasta ~12 láminas**: se conservan las 7 y se suman las de imagen. Los gráficos nativos de O1, O2 y O3 **no se tocan**, así que su QA de la sesión 59 sigue valiendo |

Todo sale de artefactos que ya están en disco y corre en **CPU**: sin `sbatch` y sin medición nueva,
así que no dispara la regla 9. Las imágenes son fotografías de resultados y van como PNG (excepción
de `CLAUDE.md` §Formato de entregables); leyendas, rótulos y números van **nativos**.

## Estructura nueva (11 láminas)

```
s01  portada                                  sin cambios
s02  OBJETIVOS                                sin cambios
s03  NUEVA  Qué detecta HoVer-NeXt            recorte con contornos por clase, a dos escalas
s04  O1 escalera                              sin cambios
s05  NUEVA  O1 sobre una lámina               alto grado contra bajo grado, carga de N = 500
s06  NUEVA  O1 núcleo a núcleo                galería por grado, recuperadas y no recuperadas
s07  O2 CAP                                   sin cambios
s08  O3 forest plot                           sin cambios
s09  NUEVA  O3 dónde mira la atención         3 mapas con los polígonos de CDIS
s10  cinco preguntas                          sin cambios
s11  Tareas                                   sin cambios
```

## Tres hechos verificados en la sesión 60 que el código tiene que respetar

1. **`envs/pruebas` NO abre los `.bif`.** Trae zarr, pandas y openslide, pero su openslide es el
   wheel `openslide-bin` 4.0.1 **stock**, que carga su propia biblioteca desde `site-packages` y
   revienta con `Bad direction attribute "LEFT"` (verificado sobre la 129741). `clam_latest` abre
   los `.bif` y no tiene zarr. Por eso el trabajo va en **dos scripts**, uno por env.
2. **`results/b9_nucleos/marcas_grado.csv` trae sólo las 12 láminas del B9.** Las marcas de las 9
   nuevas salen del geojson: `marcas_de_grado(slide, dx, dy)` de `scripts/b9_pleomorfismo.py`, con
   `cargar_offset` de `scripts/b10_grado_sin_marca.py`, que es lo que usó O1.
3. **Los colores de HoVer-NeXt con los pesos de Lizard NO son «verde epitelial».**
   `viz_utils.create_geojson` pinta `COLORS_LIZARD[clase - 1]`, así que epitelial es **rojo** y
   neutrófilo verde; el verde epitelial es de la paleta de PanNuke. El docstring de
   `scripts/b9_galeria_regiones_epi.py:10-11` lo atribuye mal. El B9 está cerrado y no se toca;
   acá se declara una **paleta propia** y no se cita la de HoVer-NeXt.

## Paso 1: los assets

### 1.a `scripts/b10_deck_seleccion.py` (env `pruebas`, lee zarr)

Elige los recortes y deja lo que necesita el render en `results/b10_deck_imagenes/`:
`seleccion.json` más una `ventana_<nombre>.npz` por recorte (el trozo de `pinst_pp` y `{id: clase}`).

Reusa, no reimplementa:
- de `b10_grado_sin_marca.py`: `cargar_offset`, `resolver_por_centroide`, `carga_mm2`,
  `LADO_PARCHE_PX`; de `b9_pleomorfismo.py`: `marcas_de_grado`, `TOL_VECINDAD_UM`;
- de `b9_descriptores_nucleos.py`: `SLIDES`, `EPITELIAL`, `MPP`, `paths_de`, `leer_class_inst` y el
  patrón `zarr.open(zarr.storage.ZipStore(...))`;
- los npz de `results/b9_nucleos/<slide>_nucleos.npz` (clase, área, centroides). El orden por
  tamaño es el de `escalera()` en `b10_grado_sin_marca.py` (`argsort` estable sobre el área de los
  epiteliales vivos), no otro.

Reglas de selección, **deterministas y escritas en el docstring**, para que nada se elija a ojo:
- **s03 HoVer-NeXt**: la marca de alto grado, en lámina alineada, con más núcleos epiteliales en
  su parche de 256 px. Dos ventanas centradas en ella: ~500 µm de contexto y 256 px (un parche de
  CLAM, 119 µm).
- **s05 mapa**: la lámina de alto grado con más marcas alcanzables y la de bajo grado con más
  marcas alcanzables, las dos alineadas. Por lámina: parches de la unión de N = 500, cada marca
  con su estado (recuperada · alcanzable no recuperada · no alcanzable) y la carga en mm².
- **s06 galería**: por grado, entre marcas alcanzables de láminas alineadas: las recuperadas en
  N = 500 en los puestos mínimo, mediano y máximo, y las no recuperadas en los puestos del primer
  cuartil y mediano, con una lámina distinta por panel cuando alcance. Bajo no tiene recuperadas:
  sus paneles son sólo no recuperadas. Cada panel guarda su puesto y su percentil.

**Gates que abortan antes de escribir:**
- las recuperadas en N = 500, sumadas sobre las 21 láminas, reproducen `escalera.csv` filtrado a
  `brazo = A_lamina_entera`, `desc = percentil`, `N = 500`: **41 · 12 · 0**, y sus `n_resueltas`
  suman **76 · 53 · 16**;
- `pinst_pp[y, x]` en el centroide de cada núcleo dibujado devuelve su id, y su clase coincide con
  `class_inst.json` (el chequeo de [[hovernext-salida-geometria-y-clases]]).

### 1.b `scripts/b10_deck_imagenes.py` (env `clam_latest`, abre `.bif`, tiene torch)

Lee `seleccion.json` y las ventanas, y escribe cada PNG con su JSON al lado en
`sprints/B10_sprint10/presentacion_b10/assets/`, versionados como los del B9.

- **Contornos**: borde de instancia = píxel cuyo id difiere de un vecino (numpy, sin skimage),
  sobre `read_region` a level 0 con el origen clampado, como `recorte()` de
  `scripts/b9_galeria_nucleos_grado.py`.
- **s05**: miniatura con `get_wsi_thumbnail` de `scripts/mammoth_interpretability.py`, los parches
  de la carga como cuadros semitransparentes y las marcas con tres símbolos.
- **s06**: el núcleo marcado con contorno grueso y los demás del top 500 que caen en la ventana con
  contorno fino.
- **s09**: tres láminas por regla: la de `train` con AUC más alto (hoy 124729, 0,929), la de `test`
  (126504) y la que está fuera del split (B25-158899). Reusa de `b10_cdis_atencion.py`
  `atencion_ckpt` (rama verdadera; `si` para la B25) y `parches_cdis`; de `b9_atencion_12_laminas.py`
  `leer_h5` y `paso_de_grilla`; y de `mammoth_interpretability.py` `percentile_scores`,
  `build_overlay_rgba` y `blend`. Polígonos de CDIS con su offset, y la región anotada de la B25
  recuadrada. **Gate**: el AUC recalculado con esos mismos scores reproduce `auc_cdis.csv` (fuente
  `ckpt_1fold_verdadera`) y `auc_cdis_region.csv` a tres decimales.
- **Tipografía quemada** dimensionada para la caja real de la lámina, con
  `px = pt × W / (ancho_in × 72)` y al menos 7 pt efectivos ([[png-rotulos-quemados-pierden-pt]]).
  Lo que lleva números va nativo y se lee del JSON **en el orden de dibujo**, que el JSON declara
  explícitamente ([[sidecar-orden-no-es-el-de-la-figura]]).
- El aspecto de cada PNG se decide **después de escribir y medir el pie** con `caja_figura`
  ([[figura-alto-lo-decide-el-pie]]).

Correr con `CUDA_VISIBLE_DEVICES=""` y binario absoluto (workaround B). Si algo tarda más de unos
minutos, desatado con `setsid` (workaround J).

## Paso 2: el deck

`generate_b10_deck.py`:
- cuatro builders nuevos, `lamina_hovernext`, `lamina_o1_mapa`, `lamina_o1_galeria` y
  `lamina_o3_mapas`, con el molde de `lamina_o1`: `cejilla`, `set_titulo`, `set_cuerpo` de una o dos
  líneas, figura y pie. Del generador del B9 se **importan sin editarlo** `poner_figura`,
  `medir_figura`, `leyenda_circulos`, `clonar_s03` y `reordenar`;
- `CLAVES` y el orden de `reordenar` a 11; `auditar_grupos` y `barrer_xml` sin cambios;
- el cruce de contenido suma las cadenas de las láminas nuevas (los tres AUC, las cargas, «N = 500»).

Lo que cada pie tiene que declarar, que es lo que la imagen **no** dice:
- s03: las clases son de HoVer-NeXt y nadie las validó; el área no se compara entre clases porque
  el umbral es por clase ([[descriptor-absoluto-trae-el-umbral]]).
- s05 y s06: unidad marca; alcanzable contra no alcanzable; el patólogo marca ejemplares, así que
  un núcleo grande sin marca **no** es un falso positivo.
- s09: checkpoint de un fold y rama verdadera; `train` y `val` ya vistos por el modelo; † offset sin
  verificar en la B25.
- Nada de mitosis, que es la línea del supervisor. Sin nombres ni números de job.

`guion_b10.md`: cuatro bloques `## [sNN]` nuevos con las convenciones del encabezado, y las
transiciones de O1 a O2 y de O3 a las preguntas ajustadas, porque cambia la lámina anterior.
`@humanizer-es` sólo sobre los párrafos nuevos.

`README.md` del deck: Estructura, la fila de Datos con los dos scripts, y marcar como ejecutada la
fila de Decisiones del 16-sep. Antes de regenerar, copiar el `.pptx` actual (md5 `b6217dcb`) al
scratchpad para comparar.

## Verificación

1. Los dos scripts terminan con los gates en verde: 41 · 12 · 0, 76 · 53 · 16, ids de `pinst_pp` y
   los tres AUC.
2. `generate_b10_deck.py` sale con código 0.
3. Round-trip: 11 láminas en orden, notas en las 11, sólo Barlow en `typeface`, cadenas esperadas
   presentes y prohibidas ausentes.
4. `qa_geometria.py` sigue limpio en O1, O2 y O3.
5. **Mirar las láminas nuevas temprano**, antes de que la sesión se alargue
   ([[image-api-qa-limit]]): rasterizar con el comando del README a 110 dpi y revisar s03, s05, s06
   y s09 (contornos legibles, rótulos nativos bajo el panel correcto contra lo quemado, al menos
   7 pt, nada que tape el pie). Las otras siete, una pasada.
6. Commits locales en `main`, verificando la rama antes de cada uno.
