# Auditoría de coherencia — B9, sesión 31 (27-ago-2026)

Alcance **acotado**: propagar lo que la sesión 31 cambió y registrar lo durable. No es una
pasada completa sobre los cuatro frentes; lo que no toca el deck del período no se revisó.

Disparador: Ernesto pidió tres cambios sobre el deck ya escrito (español con el nombre del
proyecto incluido, dos láminas de recortes de mitosis, y la lámina de ejes con un solo punto
de resumen). Eso dejó stale las decisiones que la sesión 30 había registrado como cerradas.

| id | hallazgo | tipo | severidad | acción |
|---|---|---|---|---|
| A1 | `objetivos_sprint9.md` fija «láminas en inglés», «Nuclear Detection» y «cinco láminas» | stale | media | ADDENDUM fechado, sin reescribir la decisión original |
| A2 | La memoria de la plantilla describe el deck ejecutado como de cinco láminas en inglés | stale | media | ADDENDUM 27-ago |
| A3 | La línea de índice de esa memoria no dice que el deck puede ir en español | stale | baja | reescribir la línea de `MEMORY.md` |
| A4 | Dos capas del QA medían el mismo párrafo con supuestos distintos | error | **alta** | ADDENDUM a `deck-qa-puntos-ciegos-chequeo` + fix en el generador |
| A5 | Dos cantidades distintas del deck valen 68 por construcción | error | **alta** | memoria nueva + desambiguar las dos láminas |
| A6 | `progress/current.md` registra «Nuclear Detection» como decisión de la sesión 30 | — | — | **no se toca**: es registro histórico fechado |
| A7 | `progress/current.md` sin la sesión 31 | stale | media | agregar la sesión |

---

## A1 — El mapa del sprint fija cuatro decisiones que ya cambiaron

**Dónde**: `sprints/B9_sprint9/objetivos_sprint9.md:85-92`.

**Qué dice**: «cuatro decisiones de Ernesto: láminas en **inglés** pero guion hablado en
**español**, proyecto **Nuclear Detection** (…) y **dos** láminas de contenido», y más abajo
«**ESCRITO el 26-ago** (…): cinco láminas».

**Qué es verdad hoy**: el deck va **entero en español**, el proyecto es **Detección Nuclear**
(que además nombra el archivo), las láminas de contenido son **cuatro** y el deck tiene
**siete**. La portada sigue en inglés, ahora por decisión explícita y no por herencia.

**Canonical**: `sprints/B9_sprint9/presentacion_b9/README.md`, que ya está actualizado.

**Fix**: ADDENDUM fechado en el mapa del sprint. La decisión del 26-ago **no se reescribe**:
fue real, se ejecutó, y el 27-ago Ernesto la cambió. Reescribirla borraría que hubo un cambio
de idioma a mitad de camino, que es justamente lo que explica el hallazgo A4.

## A2 — La memoria de la plantilla describe un deck que ya no es ése

**Dónde**: `memory/plantilla-oficial-image-to-text.md:67-68`, dentro del `ADDENDUM 26-ago`.

**Qué dice**: «Primer deck construido sobre esta plantilla (…), cinco láminas: portada
intacta, `OBJECTIVES`, dos de contenido y `Tasks`».

**Fix**: ADDENDUM del 27-ago. El del 26-ago queda **intacto** por la misma razón que A1: es un
registro fechado de lo que se ejecutó ese día. Lo que suma el nuevo es que la plantilla es
inglesa pero el deck no tiene por qué serlo, y qué cuesta esa decisión.

## A3 — La línea de índice de `MEMORY.md`

**Dónde**: `MEMORY.md:117`. Dice que la plantilla es «en inglés y con 4 láminas ejecutivas».

**Sobre la plantilla eso sigue siendo cierto** y no es un error. Lo que falta es que el deck
que se construye encima puede ir en español, que es la decisión con la que se va a encontrar
la próxima sesión. Se reescribe la línea, no la memoria.

## A4 — Dos capas del QA medían el mismo párrafo con supuestos distintos

**El hallazgo durable de la sesión.** Los puntos del cuerpo de las láminas de contenido son
«arranque en bold + resto normal». `set_cuerpo()` medía el párrafo entero **como normal**
(subestima, porque el bold es más ancho) y `auditar()` lo medía entero **como bold**
(sobreestima). Las dos funciones creían estar midiendo lo mismo.

**Por qué no se había visto**: con el inglés, más corto, la diferencia nunca llegaba a cambiar
el número de líneas. Apareció al traducir, como un aviso de «texto que no entra: sobra 0,44"»
que **no era del texto**: era el desacuerdo entre las dos medidas.

**Lo generalizable**: cuando dos capas miden lo mismo con supuestos distintos, el aviso que
sale no describe el objeto medido sino la distancia entre los supuestos. Y el modo de falla
peligroso es el contrario del que se ve: acá el auditor sobreestimaba y **avisó de más**, pero
el mismo desacuerdo con los papeles cambiados **calla** un desborde real.

**Fix**: `wrap_lines_mixto()` mide cada tramo con su peso, y las dos funciones la usan.
Registrado como ADDENDUM en [[deck-qa-puntos-ciegos-chequeo]], que es la memoria de los puntos
ciegos del QA de decks.

## A5 — Dos cantidades distintas del deck valen 68, y coinciden por construcción

En la lámina del número, «las otras once reencuentran **13 de sus 68** marcas» → 68 = 94 − las
26 marcas de la 129741. En la lámina nueva, «las **68** marcas que se escapan» → 68 = 94 − los
26 aciertos. **Son denominadores distintos con el mismo valor**, y coinciden porque la 129741
tiene exactamente tantas marcas como aciertos hay en total. No es casualidad numérica pura:
es una identidad que se sostiene mientras esos dos números sean iguales, y se rompe sola si
mañana cambia el cruce.

Un lector que ve los dos en láminas contiguas los va a leer como el mismo número. Es la misma
familia de error que [[conteo-de-grupo-es-union]] y que la mezcla de unidades de
[[techo-filtro-antes-de-correr]], pero **no la cubre ninguna de las dos**: acá la unidad es la
misma (marcas) y el número es el mismo; lo único que cambia es el denominador.

**Fix**: las dos láminas nombran su denominador. Memoria nueva.

## A6 — Lo que NO se toca

`progress/current.md:4554` registra «Proyecto: **Nuclear Detection**» como decisión de la
sesión 30. Es correcto **como registro de esa sesión** y no se reescribe: el 27-ago cambió, y
eso se cuenta en la sesión 31. Reescribir hacia atrás destruiría la traza de que hubo un
cambio.

## A7 — `progress/current.md` sin la sesión 31

Se agrega, con las tres cosas que pidió Ernesto, lo que encontró el QA y los pendientes.

---

# Segunda pasada — B9, sesión 32 (27-ago-2026)

Alcance **acotado**: registrar lo que salió del reconocimiento de los dos ejes nucleares de CPU
(ejes 4 y 3 del inventario) antes de medirlos. No es una pasada sobre los cuatro frentes.

Disparador: el handoff mandaba correr los dos ejes GO y baratos. Al mirar el material de verdad
aparecieron **tres correcciones de premisa** que cambian el diseño de uno de ellos, y dos
gotchas de herramienta que valen para cualquier sesión futura.

| id | hallazgo | tipo | severidad | acción |
|---|---|---|---|---|
| B1 | El inventario clasifica el eje 3 como «región contra población»: las 107 anotaciones de grado son **núcleos sueltos** | error | **alta** | ADDENDUM fechado en `inventario_tareas.md` §4, sin reescribir la rúbrica |
| B2 | El área del polígono del patólogo es en parte el **pincel de QuPath**, no el objeto | error | **alta** | memoria nueva + ADDENDUM en el inventario |
| B3 | El grado está confundido con la lámina **sin un solo cruce** (8/2/2 disjuntas) | stale | media | ADDENDUM: el `n` del ordenamiento es 12 láminas, no 107 marcas |
| B4 | Gate nuevo: **107 de 107** marcas caen sobre un núcleo segmentado | — | — | se registra en el inventario y en el pre-registro |
| B5 | La memoria de la salida de HoVer-NeXt dice «el env con zarr no tiene pandas»: `envs/pruebas` tiene **los dos** | stale | media | ADDENDUM a la memoria + línea de `MEMORY.md` |
| B6 | Los 131 extras de `MultiPolygon` son **astillas** de digitalización; el loader actual está bien | reconciliation | media | nota en el inventario §0 para que nadie los «arregle» |

---

## B1 — Las 107 anotaciones de grado son núcleos, no regiones

**Dónde**: `sprints/B9_sprint9/hovernext_tareas/inventario_tareas.md:109` (fila del eje 3) y
`:128-129` (la definición de «región contra población»).

**Qué dice hoy**: que el eje 3 se mide con «descriptores de tamaño y forma de los núcleos
**dentro** de cada región, contra los de fuera», y que «la región no marca *dónde* está el
objeto sino *cómo son* los objetos que contiene».

**Qué es verdad**: las tres clases de grado tienen el perfil de tamaño de una marca puntual, y
es el mismo de `Mitosis`:

| Clase | `n` | área mediana | diámetro equivalente | bbox mediano | % bajo 400 µm² |
|---|---|---|---|---|---|
| `Mitosis` (referencia) | 94 | 218,8 µm² | 16,7 µm | 36×36 px | 82 % |
| `Nucleos alto grado` | 77 | **218,8 µm²** | 16,7 µm | **36×36 px** | 78 % |
| `Nucleos mod grado` | 14 | 35,5 µm² | 6,7 µm | 16×14 px | 100 % |
| `NucleosBajoGrado` | 16 | 25,6 µm² | 5,7 µm | 12×12 px | 100 % |

Un núcleo epitelial mamario mide 7 a 9 µm de diámetro. Las clases que **sí** son regiones se ven
distintas por dos órdenes de magnitud: `Tumor` 4.025 µm² (216×219 px), `AreaTubular` 7.055 µm²,
`Tejido Adiposo` 191.364 µm².

**Por qué importa**: la unidad decide el cruce, y el inventario §4.a lo dice él mismo. Con la
unidad mal, el eje 3 se hubiera implementado rasterizando regiones y comparando poblaciones
dentro contra fuera, sobre «regiones» de 12×12 px que contienen **un** núcleo. El resultado
habría sido ruido con forma de método.

**Fix**: ADDENDUM fechado en `inventario_tareas.md` §4. La rúbrica original no se reescribe: es
el registro de lo que se creía el 25-ago y de por qué.

## B2 — El área del polígono es en parte el pincel

`Mitosis` y `Nucleos alto grado` comparten la mediana **exacta**, 218,82 µm². No es
coincidencia de redondeo: ese valor aparece **14 veces** en `Mitosis` y **4** en `alto`, siempre
con los mismos **53 vértices**; 155,25 µm² aparece **8** y **4** veces, con 65 vértices. Es un
pincel de radio fijo de QuPath. `NucleosBajoGrado`, en cambio, tiene 16 áreas distintas en 16
marcas, o sea trazado a mano.

**Por qué importa**: el orden de las medianas de las marcas (alto 16,7 µm > moderado 6,7 >
bajo 5,7) **ordena bien**, así que es tentador reportarlo. Sería medir el pincel. Cualquier
descriptor nuclear tiene que salir de `pinst_pp.zip`, nunca del polígono del patólogo.

**Fix**: memoria nueva, porque no es del B9: vale para cualquier medición futura contra este
geojson, incluida la de necrosis del eje 2.

## B3 — El grado está confundido con la lámina

Verificado: `alto` vive en 8 láminas, `moderado` en 2, `bajo` en 2, y **ninguna lámina tiene dos
grados**. El inventario dice «107 regiones … repartidas en las 12 láminas», que es cierto, y el
deck lo corrigió respecto del `107 / 8` viejo ([[conteo-de-grupo-es-union]]). Lo que falta decir
es la consecuencia: **comparar grados es comparar láminas**, con tinción, escáner y grosor de
corte adentro, y el `n` efectivo del ordenamiento es **12 láminas**, no 107 marcas.

**Fix**: ADDENDUM, y en el pre-registro la mitigación (percentil intra-lámina como resultado
primario).

## B4 — Gate: 107 de 107 marcas caen sobre un núcleo segmentado

| Grado | Marcas | Segmentadas | Clase del núcleo |
|---|---|---|---|
| alto | 77 | **77 (100 %)** | 67 epithelial, 8 connective, 2 lymphocyte |
| moderado | 14 | **14 (100 %)** | 4 epithelial, 3 connective, **7 plasma-cell** |
| bajo | 16 | **16 (100 %)** | 15 epithelial, 1 lymphocyte |

Los 7 `plasma-cell` son todos de la 109609. Restringir a epitelio deja `moderado` en **n = 4**,
así que las dos poblaciones se corren y se reportan juntas.

## B5 — Hay un env con zarr **y** pandas

**Dónde**: memoria `hovernext-salida-geometria-y-clases`, y los comentarios que la citan en
`scripts/cruce_hovernext_marcas.py:45-47` y `scripts/a0_segmentadas_o_no.py:38-40`.

**Qué dice hoy**: «el env con zarr no tiene pandas», que llevó a importar pandas dentro de
`main()` para que los helpers siguieran siendo importables desde el env de zarr.

**Qué es verdad**: eso es cierto de `clam_testing2/envs/hovernext`, pero
**`/home/sdonoso/miniconda3/envs/pruebas`** tiene zarr 2.18.3 **y** pandas 2.3.3, más numpy,
scipy, matplotlib, h5py y openslide. Verificado abriendo un `pinst_pp.zip` con él.

**Por qué importa**: quita la restricción de partir en dos procesos cualquier análisis que
necesite las dos cosas, que es exactamente el caso del eje 3.

**Fix**: ADDENDUM a la memoria. El código existente **no se toca**: su import diferido sigue
siendo correcto y no molesta.

## B6 — Los extras de `MultiPolygon` son astillas, no contenido

`cargar_anotaciones()` (`scripts/alinear_anotaciones_qupath.py:59-61`) toma el primer anillo del
primer sub-polígono, y a primera vista parece que pierde 131 sub-polígonos en las clases justo
donde duele (`Tumor`, `Stroma`, `AreaSolida`). Medido: de esos 131, **105 miden menos de 10 µm²
y 127 menos de 400**, con mediana **0,4 µm²**. Son astillas de digitalización.

Expandirlos hincharía los conteos del vocabulario que el inventario §0 fijó con cuidado:
`Tumor` 98 → 170, `Stroma` 12 → 42, `AreaSolida` 45 → 63. O sea que «arreglarlo» rompería la
corrección del 25-ago.

**Fix**: nota en el inventario §0, que es donde vive la cuenta de las 472 anotaciones, para que
la próxima sesión no lo lea como bug.
