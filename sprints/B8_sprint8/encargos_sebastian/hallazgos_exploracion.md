# Los cuatro encargos de Sebastián — lo que la exploración verificó antes de ejecutar

> Sesión del **21-ago-2026**, CPU y lectura, sin GPU y sin escribir fuera del repo.
> La reunión ya había ocurrido; Ernesto trajo los cuatro encargos y esta sesión los cruzó
> contra lo que hay en disco. El plan ejecutable está en [plan.md](plan.md).

Los encargos, textuales:

1. Generar el mapa de calor con el checkpoint de CLAM para **carcinoma invasivo**, pasarle los
   parches más atendidos a HoVer-NeXt como se hizo con el checkpoint anterior, y comparar.
2. Ver las imágenes del resto de las **177 − 13 = 164** mitosis, para comprobar si se parecen
   entre sí.
3. Revisar si la **necrosis** que señala HoVer-NeXt coincide con las marcas del patólogo.
4. Probar HoVer-NeXt con las **12 WSI anotadas**.

Cinco cosas cambiaron el enunciado. Ninguna lo invalida; todas cambian qué hay que correr.

---

## 1. El checkpoint que Sebastián no recordaba, y cuál es el de invasivo

El de la cadena que ya corrimos es **`carcinoma_ductal_insitu_presente_ci_reform`, fold 4**, del
job 4589, en su par CLAM/Mammoth propio. Está escrito en los dos `meta.json` que sostienen el
resultado:

```
results/b8_hovernext_129741/cruce_marcas/meta.json      → fuente_atencion: .../carcinoma_ductal_insitu_presente_ci_reform/129741/atencion_por_parche.npz
results/b8_hovernext_129741/techo_atencion/meta.json    → idem
```

No era el de carcinoma invasivo: era **CDIS**.

Para carcinoma invasivo la tarea es **`invasion_carcinoma_gate_pth_balance`** — el gate binario
de la cascada que Sebastián introdujo el 14-jul ([[formulacion-cascada-gate-invasivo]]).

| Qué | Valor |
|---|---|
| CSV | `clam_environ/environ/csv_balance/dataset_invasion_carcinoma_gate_label.csv` (creado por `sgaete`, 14-jul) |
| Reparto | **2013 `invasivo` / 802 `no_invasivo`**, 2815 láminas |
| La 129741 | etiquetada **`invasivo`** (línea 240) |
| Splits | `environ/splits_5fold_balanced/invasion_carcinoma_gate_pth_balance_100` |
| Fold donde la 129741 cae en **test** | **fold 0** (en el 3 es val; en 1, 2 y 4 es train) |

Que caiga en test importa: la atención de una lámina vista en entrenamiento no se lee.

## 2. El checkpoint del gate que hay en disco es MAMMOTH, y su `experiment.txt` dice otra cosa

Único checkpoint entrenado del gate:

```
clam_testing/results_mammoth_5fold_balanced_tcga_sc/invasion_carcinoma_gate_pth_balance_mammoth_5fold_s1/
    s_{0..4}_checkpoint.pt          2,53 MB c/u   (+ _best_auc y _best_error)
```

Su `experiment_*.txt` declara `'model_type': 'clam_mb'`, y **eso es engañoso**. El `state_dict`
tiene claves `attention_net.0.mammoth.slot_embeds (30, 16, 10, 16)`, `attention_net.0.mammoth.wq`,
`attention_net.0.mammoth.norm.*` — es **CLAM_MB con el patch-embed reemplazado por el MoE de
Mammoth**, o sea `clam_mammoth`. El campo del txt es lo que registró el parser de args, no lo que
se construyó.

**Regla que se desprende: la familia de un checkpoint se decide leyendo su `state_dict`, no su
`experiment.txt`.** Cuesta cinco segundos y evita presentar como CLAM algo que no lo es.

Consecuencia para el encargo 1: **CLAM plano del gate no existe**. Se resolvió corriendo los dos
brazos — el Mammoth de disco hoy mismo en CPU, y el CLAM plano entrenando el fold 0 sobre el
**mismo `--split_dir` y la misma config**, con lo que queda pareado por construcción (patrón P1).

Lo demás del gate está bien: `classifiers.{0,1}` de 512 → 2 clases, `embed_dim` 512, entrenado el
15-jul, o sea **después** de la re-extracción de features de TCGA del 26-27 jun
([[features-tcga-drift-reextraccion]]) — y la 129741 es privada, así que el drift no la toca.

## 3. El checkpoint que corrimos NO tiene clase de necrosis

Las clases salen de `clam_testing2/hover_next_reference/src/constants.py`:

| Juego | Clases |
|---|---|
| **Lizard-Mitosis** (`constants.py:33-39`) — el que corrimos | neutrophil, epithelial-cell, lymphocyte, plasma-cell, eosinophil, connective-tissue-cell, **mitosis** |
| **PanNuke** (`constants.py:44-48`) — nunca lanzado | neoplastic, inflammatory, connective, **dead**, epithelial |

**La necrosis está solo en PanNuke, como `dead`.** El encargo 3 no se puede contestar con lo que
hay en disco: la salida de la 129741 tiene `pred_{connective-tissue-cell, eosinophil,
epithelial-cell, lymphocyte, mitosis, neutrophil, plasma-cell}.tsv` y ningún `pred_dead.tsv`. El
directorio `results/b8_hovernext_129741/hovernext/pannuke/` está **vacío**.

**Esto NO reabre la decisión de no lanzar el ensemble.** Esa decisión decía que el ensemble no
puede mover el 13 de 26 **de mitosis**, y sigue siendo cierta por la misma razón (PanNuke no
tiene la clase). Lo que aparece es una pregunta distinta, que solo el ensemble puede contestar.

**Presupuesto**, sobre los 18 min medidos de la corrida Lizard (job 5008): PanNuke tesela a
0,25 µm/px → **206.382 tiles contra 51.192**, y además promedia 3 checkpoints. La inferencia
escala ~12× y el post-proceso ~4× ⇒ **2 a 2,5 h**. Sin `--keep_raw`: el raw a 4× serían ~40 GB
que no se van a usar.

**Y la unidad no es la misma que en mitosis.** La necrosis del patólogo son **polígonos**
(regiones) y `dead` son **núcleos** (puntos): no hay emparejamiento uno a uno posible, así que el
húngaro de `cruce_hovernext_marcas.py` no aplica. Se mide densidad dentro contra fuera, cuántos
polígonos contienen al menos un `dead`, y el nulo se construye **trasladando la máscara**, no
permutando etiquetas, porque los polígonos son contiguos ([[nulo-espacial-traslacion-rigida]]).

## 4. Las 12 láminas: todas tienen mitosis, pero seis no sostienen un número propio

Conteo sobre los 12 geojson de `sdonoso/anotaciones/` (lectura, no se tocó nada):

| Lámina | Total | Mitosis | Necrosis | WSI (GB) |
|---|---|---|---|---|
| 129741 | 61 | **26** | 6 (`necrosis`) | 0,73 |
| 126504 | 44 | **20** | — | 0,47 |
| 128194 | 52 | **17** | 4 (`Necrosis`) | 0,51 |
| 124729 | 45 | 8 | 3 (`Comedonecrosis`) | 0,43 |
| 124806 | 34 | 6 | 3 (`Comedonecrosis`) | 0,30 |
| B25-158899 | 38 | 6 | 2 (`Necrosis`) | 0,57 |
| 144317 | 40 | 3 | — | 0,46 |
| 164001 | 30 | 3 | — | 0,43 |
| 106552 | 39 | 2 | — | 0,57 |
| 103762 | 34 | 1 | — | 0,46 |
| 109609 | 25 | 1 | — | 0,32 |
| 110616 | 30 | 1 | — | 0,32 |
| **Total** | **472** | **94** | **18** | **5,6** |

Cuatro lecturas operativas:

1. **Las 12 tienen mitosis**, como intuía Ernesto. Pero **tres láminas concentran 63 de las 94**
   (67 %) y **seis tienen ≤3**. Un recall por lámina desde n=1 no distingue nada: el denominador
   que se reporta es el **agregado de 94**, con la tabla por lámina y su `n` al lado.
2. **Todas las marcas de Mitosis son `Polygon`**, no puntos — igual que en la 129741, así que
   `marcas_mitosis()` sirve tal cual (toma el centroide).
3. **El vocabulario de necrosis es inconsistente**: `necrosis` en minúscula (129741), `Necrosis`
   en mayúscula (128194, B25-158899) y `Comedonecrosis` (124729, 124806). Hay que normalizar y
   **declarar** que Comedonecrosis se contó como necrosis, o no contarla — pero decidido y escrito.
4. **Las 12 tienen WSI + `.h5` + `.pt`**, verificado con `ls`. Las 11 restantes promedian 0,44 GB
   contra los 0,73 de la 129741 ⇒ **~2,5 h** para el barrido completo, y ~1,5 GB de salida si se
   corre **sin `--keep_raw`** (con él serían 121 GB).

El geojson de las otras 11 **tampoco** va a estar en coordenadas de openslide: sin corregir el
offset, en la 129741 caían **0 de 26** marcas sobre un parche. `alinear_anotaciones_qupath.py` ya
es genérico y deriva dx/dy por lámina, así que es CPU y va antes del barrido, no después.

## 5. `sgaete` ya midió atención contra anotaciones — pero no el gate, y leyendo la rama predicha

`sdonoso/anotaciones/atencion/resumen_atencion.csv`: **108 filas = 8 tareas × las 12 láminas**,
con AUC de la atención como detector de parches anotados, percentil medio dentro y fuera, y un
PNG por par. Las 8 tareas son `tipo_histologico`, `carcinoma_ductal_insitu_presente`,
**`carcinoma_ductal_insitu_necrosis`**, `grado_histologico_{mitotic_rate, pleomorfismo_nuclear,
diferenciacion_tubular}`, `invasion_linfatica_vascular` y `microcalcificaciones`.

- **`invasion_carcinoma_gate` NO está en su lista** ⇒ el encargo 1 es trabajo nuevo, no duplicado.
- **La necrosis SÍ está** ⇒ la mitad CLAM del encargo 3 ya tiene un antecedente suyo, y hay que
  citarlo en vez de rehacerlo a ciegas.

Y un detalle metodológico que cambia el número: su columna `rama_atencion` es **la clase
predicha**. Para la 129741 en necrosis el modelo predice `no identificado` (prob 0,599) cuando la
etiqueta es `presente_central`, así que **mide la atención de la rama equivocada** y le da
**AUC 0,382** — bajo el azar. Nuestra versión lee la rama de la clase verdadera **y** la predicha,
y reporta las dos.

Su tabla también expone que **de las 12 láminas casi ninguna está en un split de esas tareas**:
74 de 108 filas son `split=fuera`, 26 train, 5 test, 3 val. Para necrosis, la 129741 es una de
las que **sí** cae en test.

## 6. El 177, confirmado en el archivo

`results/b8_hovernext_129741/hovernext/lizard_mitosis/129741/pred_mitosis.tsv` tiene **178 líneas
= 1 cabecera + 177 detecciones**, con columnas `x  y  name  color` y **sin score de confianza**
(por eso la galería del encargo 2 no se puede ordenar por confianza; se ordena por parecido de
píxeles). El reparto ya documentado es **82 en la región anotada + 95 en la otra**, y los 164 de
Sebastián son las 177 menos las 13 que acreditaron una marca.

---

## Qué NO se afirma

- **Nada de esto midió nada nuevo.** Es inventario verificado sobre archivos que ya existían.
- **No se corrió GPU** ni se escribió fuera de `clam_testing2/oncomets-ernesto/`.
- **El 0,382 de `sgaete` no se corrige acá**: se explica de dónde sale. Puede que su elección de
  rama sea deliberada, y hay que preguntárselo antes de presentarlo como error.
- **No se verificó si `sgaete` piensa correr HoVer-NeXt sobre las 12.** Decisión de Ernesto:
  seguimos y le avisamos después.