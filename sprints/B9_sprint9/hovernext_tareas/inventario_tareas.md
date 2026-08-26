# Contra qué tareas se puede medir HoVer-NeXt, y contra cuáles no

> Escrito el **25-ago-2026**, CPU y lectura. Es lo que Ernesto pidió primero al abrir el B9:
> evaluar **todas** las tareas contra las que HoVer-NeXt se puede medir, no sólo mitosis.
>
> Encuadre de la reunión: *ahondar en HoVer-NeXt y hacer más pruebas que ayuden a demarcar una
> zona importante para el patólogo*. La pregunta que este doc contesta es cuáles de esas pruebas
> existen, cuánto cuestan y en qué unidad se miden.

---

## 0. Corrección de entrada: los `n` se cuentan sobre DOCE geojson, no trece

El directorio `sdonoso/anotaciones/` tiene **trece** archivos `.geojson` y **doce** láminas. El
extra es `103762.bif - Series 0-full.geojson`, una segunda exportación de la 103762 con 35
anotaciones contra las 34 del `- GDT` de la misma lámina. Contar sobre el glob **duplica esa
lámina**.

La trampa ya estaba cazada para `Mitosis` (94 y no 95), pero no para el resto. Cuatro clases
llegaban infladas a este inventario:

| Clase | Contando el glob de 13 | **Correcto, sobre las 12** | Diferencia |
|---|---|---|---|
| `Tumor` | 108 | **98** | +10 del duplicado |
| `AreaSolida` | 54 | **45** | +9 |
| `AreaTubular` | 30 | **25** | +5 |
| `NucleosBajoGrado` | 25 | **16** | +9 |
| `Mitosis` | 95 | **94** | +1 (ya estaba corregida) |

Todos los `n` de este documento son sobre los **doce** `- GDT`, y suman **472** anotaciones, que
es el total que el B8 ya había verificado.

## 1. El vocabulario completo del patólogo sobre las 12

Veintiún etiquetas distintas. Ninguna sesión anterior lo había listado entero.

| Clase | `n` | Láminas | | Clase | `n` | Láminas |
|---|---|---|---|---|---|---|
| `Tumor` | 98 | 12 | | `Tejido Adiposo` | 9 | 4 |
| `Mitosis` | 94 | 12 | | `Permeaciones vasculares` | 9 | 6 |
| `Nucleos alto grado` | 77 | 8 | | `CDIS_solido` | 8 | 3 |
| `AreaSolida` | 45 | 6 | | `microcalcificaciones` | 8 | 3 |
| `AreaTubular` | 25 | 5 | | `Immune cells` | 7 | 3 |
| `NucleosBajoGrado` | 16 | 2 | | `Negative` | 7 | 3 |
| `Nucleos mod grado` | 14 | 2 | | `necrosis` / `Necrosis` / `Comedonecrosis` | 6+6+6 | 1+2+2 |
| `Stroma` | 12 | 7 | | `DCIS` | 6 | 2 |
| `Mucinoso` | 11 | 1 | | `CDIS_papilar` | 6 | 1 |
| | | | | `(sin clase)` | 2 | 2 |

Tres cosas que se leen de acá y gobiernan todo lo que sigue:

- **Sólo dos clases están en las doce láminas**: `Tumor` y `Mitosis`. Todo lo demás vive en 8
  láminas o menos, y siete clases en 3 o menos.
- **El vocabulario de necrosis es inconsistente** en mayúscula, minúscula y `Comedonecrosis`.
  Unificarlo y **declarar** la decisión es prerrequisito de cualquier medición de necrosis, no un
  detalle de formato.
- **`DCIS` y `CDIS_solido` conviven** como dos nombres de lo mismo en distinto idioma, y
  `(sin clase)` son dos marcas que el patólogo dibujó sin etiquetar (126504 y 106552). Nunca se
  suman a ninguna clase real.

## 2. La simetría de los dos juegos de pesos, que decide casi todo

HoVer-NeXt tiene dos juegos de pesos y **ninguno cubre las dos preguntas**:

| Juego | Clases | Escala nativa | Tiene mitosis | Tiene necrosis |
|---|---|---|---|---|
| **Lizard-Mitosis** | neutrophil, epithelial-cell, lymphocyte, plasma-cell, eosinophil, connective-tissue-cell, **mitosis** | 0,5 µm/px | **sí** | **no** |
| **PanNuke** | neoplastic, inflammatory, connective, **dead**, epithelial | 0,25 µm/px | **no** | **sí** (`dead`) |

Las dos afirmaciones son verdaderas a la vez y **ninguna reabre nada**
([[hovernext-clases-necrosis-solo-pannuke]]). La decisión del B8 de no lanzar el ensemble decía
que PanNuke no puede mover el 13 de 26 **de mitosis**, y eso sigue siendo cierto por la misma
razón: no tiene la clase. Lo que aparece con necrosis es una pregunta **distinta**, que sólo el
ensemble puede contestar.

Corolario de escala: la cohorte privada está a **0,465 µm/px**, así que Lizard-Mitosis corre casi
en su escala nativa y **PanNuke corre sobre píxeles interpolados** (0,465 contra 0,25 que espera).

## 3. Lo que ya está en disco, y por qué eso mueve dos ejes a CPU

El barrido de las doce (jobs 5008 y 5070) escribió **las siete clases de Lizard**, no sólo
mitosis, más la máscara de instancias:

| Artefacto | Cobertura | Detecciones | Versionado |
|---|---|---|---|
| `pred_mitosis.tsv` | 12/12 | 732 | **sí** (8,5 KB) |
| `pred_epithelial-cell.tsv` | 12/12 | 497.083 | no, gitignored por peso |
| `pred_connective-tissue-cell.tsv` | 12/12 | 733.563 | no |
| `pred_lymphocyte.tsv` | 12/12 | 485.245 | no |
| `pred_plasma-cell.tsv` | 12/12 | 97.042 | no |
| `pred_neutrophil.tsv` | 12/12 | 8.858 | no |
| `pred_eosinophil.tsv` | 12/12 | 2.675 | no |
| `pinst_pp.zip` (polígono por núcleo) | 12/12 | 12 GB en total | no |

**Gitignored no es ausente**: los archivos están, verificado el 25-ago. Eso vuelve **CPU post-hoc**
los ejes de pleomorfismo y de tumor/estroma, que a primera vista parecían pedir GPU.

Lo que **no** está: el raw. Las once corrieron **sin `--keep_raw`**, así que
`<slide>_raw_256_cls.zip` existe **sólo para la 129741**. Cualquier pregunta que necesite las
probabilidades por tesela (recalibrar un umbral, ver si `mitosis` quedó segunda por poco) se
puede hacer en una lámina y en once no.

## 4. La rúbrica: los ocho ejes

| Eje | Clase de HoVer-NeXt y dónde vive | Anotación del patólogo (`n` / láminas) | Tarea CLAM | Unidad, y por lo tanto qué cruce aplica | Costo | Veredicto |
|---|---|---|---|---|---|---|
| **1. Mitosis** | Lizard `mitosis` | `Mitosis` 94 / 12 | `grado_histologico_mitotic_rate` | punto contra punto: **húngaro uno a uno** | **hecho** | **MEDIDO: 26 de 94 a 30 µm** ([`cruce_94.md`](../mitosis_12_laminas/cruce_94.md)) |
| **2. Necrosis** | PanNuke `dead` | `necrosis` 6 + `Necrosis` 6 + `Comedonecrosis` 6 = **18** / 5 | `carcinoma_ductal_insitu_necrosis` | **región contra punto**: no hay uno a uno. Densidad dentro contra fuera, polígonos con al menos un `dead`, nulo por **traslación** de la máscara | GPU: 2 a 2,5 h la 129741 (B2); las 5 con necrosis son 3,25× su canvas, o sea del orden de **7 a 9 h** | **GO**, pero exige autorización de Ernesto y GPU libre |
| **3. Pleomorfismo y grado nuclear** | ninguna clase directa: el insumo es el **polígono por núcleo** de `pinst_pp.zip` | `Nucleos alto grado` 77 / 8 · `Nucleos mod grado` 14 / 2 · `NucleosBajoGrado` 16 / 2 | `grado_histologico_pleomorfismo_nuclear`, `carcinoma_ductal_insitu_grado_nuclear` | **región contra población**: no se empareja nada. Descriptores de tamaño y forma de los núcleos **dentro** de cada región, contra los de fuera | **CPU, ya en disco** | **GO, y es el más barato**: hay 107 regiones con grado declarado y tres niveles ordenados |
| **4. Tumor y estroma** | Lizard `epithelial-cell` + `connective-tissue-cell` | `Tumor` 98 / 12 · `Stroma` 12 / 7 · `AreaSolida` 45 / 6 · `AreaTubular` 25 / 5 | `tipo_histologico`, `grado_histologico_diferenciacion_tubular` | **región contra punto con clase**: fracción de cada clase dentro contra fuera | **CPU, ya en disco** | **GO**: es el control positivo natural del método, porque epitelio contra estroma es lo que cualquier segmentador nuclear debería acertar |
| **5. Infiltrado inmune** | Lizard `lymphocyte` + `plasma-cell` + `eosinophil` + `neutrophil` | `Immune cells` **7** / 3 | ninguna | igual que el eje 4 | CPU, ya en disco | **no sostiene número propio**: 7 marcas en 3 láminas. Se puede mirar, no se puede reportar |
| **6. Permeaciones vasculares** | **ninguna**: no hay clase de endotelio ni de luz vascular | `Permeaciones vasculares` 9 / 6 | `invasion_linfatica_vascular` | no aplica | no aplica | **NO-GO**: el objeto de la tarea es una **estructura** (émbolo dentro de una luz revestida) y la salida es una **población de núcleos**. Falta la clase, no la escala |
| **7. Microcalcificaciones** | **ninguna**: no es un núcleo | `microcalcificaciones` 8 / 3 | `microcalcificaciones` | no aplica | no aplica | **NO-GO** doble: no hay clase, y además el oxalato (Tipo I) es **invisible en H&E** ([[luz-polarizada-oxalato-birrefringencia]]) |
| **8. Arquitectura (tubular, papilar, mucinoso)** | **ninguna**: exige segmentación **glandular**, no nuclear | `AreaTubular` 25 / 5 · `Mucinoso` 11 / 1 · `CDIS_papilar` 6 / 1 | `carcinoma_ductal_insitu_patron_arquitectonico` | no aplica | no aplica | **NO-GO**: la unidad es la glándula y su luz. Se podría **derivar** de la densidad nuclear, pero eso es un método nuevo, no una medición de HoVer-NeXt |

### 4.a Cómo leer la columna de unidad, que es la que decide

Los tres cruces no son intercambiables, y confundirlos es lo que hace que un resultado no
signifique nada:

- **punto contra punto** (eje 1): las dos partes son objetos puntuales del mismo tipo, así que
  el emparejamiento uno a uno tiene sentido y la métrica es **recall**.
- **región contra punto** (ejes 2, 4, 5): el patólogo dibujó un área y HoVer-NeXt devuelve
  núcleos. **No hay emparejamiento posible**, y forzarlo inventa un número. La métrica es
  densidad o fracción dentro contra fuera, con el nulo construido **trasladando la máscara**,
  nunca permutando etiquetas: los polígonos son contiguos ([[nulo-espacial-traslacion-rigida]]).
- **región contra población** (eje 3): la región no marca *dónde* está el objeto sino *cómo son*
  los objetos que contiene. La métrica es un descriptor agregado, y la validación es que los tres
  grados **ordenen**.

### 4.b Lo que ningún eje puede dar

**Precisión, F1 y PQ / bPQ / mPQ no son computables** contra este material, en ninguno de los
ocho ejes. El geojson no es una segmentación exhaustiva ni son contornos nucleares: son
**positivos parciales** dibujados donde la evidencia es clara. Se dice, no se omite.

## 5. Objetivo 3: qué métricas nuevas de mitosis son computables

El tercer objetivo de la reunión pidió evaluar métricas nuevas para mitosis. Separadas por lo
único que importa, si se pueden calcular con lo que hay:

### Computables hoy, en CPU, con lo que está en disco

| Métrica | Qué es | Por qué importa |
|---|---|---|
| **Conteo por mm²** | detecciones de `mitosis` por milímetro cuadrado de tejido | Es **el número clínico de Nottingham**, el que conecta con `grado_histologico_mitotic_rate`. Hoy tenemos un recall y no un conteo |
| **Mapa de densidad** | el conteo anterior, espacializado | Es el insumo del hotspot y lo que se le muestra al patólogo |
| **Hotspot** | la ventana de **área fija** que maximiza el conteo | **Ésta es la zona que Sebastián quiere proponerle al patólogo**, y es el entregable con forma del sprint |
| **Recall a carga fija** | recall contra **mm² de tejido** entregados, no contra top-K de parches | A K fijo **gana siempre la máscara más grande**, que es un artefacto de la unidad ([[carga-fija-no-k-fijo]]). La carga es lo que el patólogo realmente paga |
| **Concordancia ordinal** | el score mitótico del patólogo por lámina contra el conteo, `n=12` | Es la única que se mide a nivel lámina, que es el nivel en el que CLAM decide |

### No computables, y por qué

- **Precisión, F1, valor predictivo positivo**: exigen que lo no marcado sea negativo, y no lo es.
  Contra positivos parciales **no son computables**. Decirlo es parte del resultado.
- **Cualquier métrica con umbral de confianza**: `pred_mitosis.tsv` trae `x  y  name  color` y
  **ningún score**. Barrer un umbral exige el raw, y **las once corrieron sin `--keep_raw`**.
- **Curva precision-recall**: se cae por las dos razones anteriores a la vez.

### La advertencia que las cinco computables comparten

El §3.b del cruce mostró que las detecciones por lámina van de **5 a 252**, con mediana 16, y que
eso **no acompaña** a cuánto marcó el patólogo. Ninguna de las cinco métricas se puede promediar
entre láminas como si fueran homogéneas: van con su `n` y su dispersión, o no van.

## 6. Qué no se afirma

- **No se midió nada nuevo acá.** Los ejes 3, 4 y 5 están declarados **GO** porque el insumo está
  en disco, no porque se hayan corrido.
- **No se afirma que los ejes GO vayan a dar señal.** Se afirma que son computables y baratos.
- **Los tres NO-GO son por falta de clase o de unidad, no por falta de presupuesto.** Correrlos
  más tiempo o con más láminas no los habilita.
- **El eje 2 no está corrido**, y su costo es una extrapolación por área de canvas sobre los 18
  min medidos de Lizard, no una medición.
- **No se afirma que las 12 láminas alcancen** para ninguno de los ejes. Sólo `Tumor` y `Mitosis`
  están en las doce; siete clases viven en 3 láminas o menos.
- **No se verificó si `sgaete` piensa correr esto**. Tiene un pipeline propio de atención contra
  anotaciones sobre 8 tareas y está corriendo detección de mitosis con YOLOv11-m
  ([[sgaete-yolo-mitosis-solapamiento]]). **Coordinar antes de escalar** sigue pendiente.
