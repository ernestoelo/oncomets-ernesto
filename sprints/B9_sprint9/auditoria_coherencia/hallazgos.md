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

---

# Tercera pasada — B9, sesión 34 (28-ago-2026)

> Cierre de la sesión que le dio **forma presentable** a los dos ejes nucleares. La sesión 33
> los midió y no dejó pasada de auditoría, así que ésta cubre lo que salió al dibujarlos.
> Los hallazgos son los tres que produjo el acto de hacer la figura, que es exactamente el
> valor que [[hallazgo-necesita-forma-presentable]] le atribuye.

| id | hallazgo | tipo | severidad | acción |
|---|---|---|---|---|
| **C1** | El `p` del eje 3 **también es el piso**, y `resultados.md` §2 no lo dice (§1 sí lo dice para el eje 4) | error de omisión | **media** | ADDENDUM fechado en `resultados.md` §2.a |
| **C2** | La comparación entre las dos poblaciones se puede leer al revés: la completa **no** está limitada por el diseño | error de omisión | **media** | mismo ADDENDUM |
| **C3** | El solape entre dos formas **REINCIDIÓ**; no es una clase nueva (ya está desde el 4-ago), y la regla que la evita se violó en un generador nuevo | reincidencia | media | ADDENDUM en [[deck-qa-puntos-ciegos-chequeo]] |
| **C4** | Los dos ejes ya tienen figura: el pendiente «sin una sola figura» se cierra | stale | baja | `resultados.md` §4, `progress/current.md`, handoff |
| **C5** | La figura importó el código del número con un kwarg **aditivo**, y la regresión se verificó con el log byte a byte | método | baja | ADDENDUM en [[hallazgo-necesita-forma-presentable]] |

---

## C1 — El `p` del eje 3 también es el PISO

`resultados.md` §1 lo dice del eje 4, textual: «**El `p` es el piso**: con 200 traslaciones el
mínimo alcanzable es 1/201 = 0,00498, así que el resultado es "por debajo de 1 en 201", no un
valor exacto». El §2 **no dice lo equivalente del eje 3**, y lo es, por una razón distinta y más
fuerte.

Medido al dibujar el nulo (`permutacion_exacta(..., con_rhos=True)`, población restringida):

| | valor |
|---|---|
| ρ observado | **+0,8090** |
| ρ **máximo** de las 360 asignaciones | **+0,8090** |
| asignaciones con \|ρ\| ≥ observado | **2 de 360** ⇒ `p` bilateral 0,0056 = 2/360 |
| asignaciones con ρ ≥ observado | **1 de 360** ⇒ `p` unilateral 0,0028 = 1/360 |

O sea que **la asignación observada es la única de las 360 que ordena perfecto**: con este
reparto (2 bajo / 1 moderado / 7 alto sobre 10 láminas) no existe un resultado mejor, y
**0,0056 es el mínimo que el diseño puede dar**. El número no es «el `p` que salió»; es el techo
del instrumento, alcanzado.

**Por qué importa y no es cosmético**: quien lea 0,0056 contra el 0,05 convencional va a leerlo
como holgura. No la hay. Un diseño con dos láminas menos en el peldaño chico no podría bajar de
ahí ni con una separación perfecta, y eso condiciona qué se puede pedirle a este eje sin más
láminas. Es el mismo argumento que el §1 ya hacía para el eje 4, aplicado donde faltaba.

**Acción**: ADDENDUM fechado en `resultados.md` §2.a. **No** se toca el pre-registro ni la tabla
de §2: los números publicados no cambian, se les agrega la lectura.

## C2 — La completa NO está limitada por el diseño, y ésa es la mitad que falta

Corolario de C1 que corrige una lectura tentadora. Con el §2.a tal como está («la restringida da
0,0056 y la completa 0,0673»), la conclusión natural es «más láminas, peor `p`», que sería
absurda. Medido, es al revés:

| población | láminas | asignaciones | ρ obs | ρ **máximo** posible | `p` obs | **piso** del `p` |
|---|---|---|---|---|---|---|
| restringida | 10 | 360 | **+0,809** | **+0,809** | 0,0056 | **0,0056** |
| completa | 12 | 2970 | +0,552 | +0,836 | 0,0673 | 0,0007 |

La completa tenía **un piso cien veces más bajo disponible** (0,0007) y quedó en 0,0673. No la
frena el diseño: la frenan **dos láminas de `alto` que caen por debajo de las de `bajo`** (la
106552 en 70,3 y la B25-158899 en 73,1, contra 66,7 y 75,1 de las dos de `bajo`), y las dos son
láminas donde la marca resolvió a clases no epiteliales. Es el mecanismo del §2.d escrito en la
unidad del nulo.

**Acción**: entra en el mismo ADDENDUM, con la tabla.

## C3 — El solape entre dos formas reincidió, y NO es una clase nueva

**Primero, la corrección a mí mismo**: al ver los dos defectos escribí que era un punto ciego
nuevo, un «sexto». Es falso, y grepear la memoria antes de editarla lo mostró: el **ADDENDUM del
4-ago-2026** de [[deck-qa-puntos-ciegos-chequeo]] ya nombra la clase («DOS OBJETOS VÁLIDOS
SUPERPUESTOS») y ya trae la regla que la evita: «cuando un bloque auto-dimensionado va seguido de
un elemento fijo, el fijo tiene que posicionarse **desde el alto medido**». El addendum
redundante se retiró antes de quedar escrito.

Lo que sí aporta el caso es **dónde vuelve a aparecer**. `auditar()` devolvió «sin avisos» sobre
las cuatro láminas y el rasterizado mostró dos solapes evidentes: la leyenda de marcadores del
eje 3 encima del pie, y el rótulo del eje de la lámina del nulo encima de los ticks del
histograma de abajo. Los dos salían de un `top` calculado a mano (`t_pl + h_pl + 0.54` y
`top + 2 * h_par - 0.10`), o sea de violar la regla del 4-ago.

**Por qué reincide**: la regla vivía en el generador del deck, no en quien escribe uno nuevo. Un
archivo nuevo que compone paneles propios re-deriva las posiciones a mano y estrena la misma
clase de defecto **aunque importe todos los helpers auditados** del anterior. Los arquetipos ya
posicionados no la disparan; la composición nueva sí.

**Acción**: ADDENDUM en la memoria registrando la reincidencia y la pista barata (grepear los
`top` que suman una constante a mano), no una capa ciega nueva.

## C4 — El pendiente «los dos ejes sin una sola figura» se cierra

Estado verificado al cierre: `sprints/B9_sprint9/ejes_nucleares/figuras/` con el generador, el
CSV de los 48 números dibujados y el `.pptx` de cuatro láminas (gitignored por
`sprints/**/*.pptx`, regenerable en segundos). Los cuatro números de cabecera reproducen los
publicados: eje 4 AUC 0,906 con `p` 0,0050; eje 3 ρ +0,809 con `p` 0,0056 sobre 360.

**Acción**: `resultados.md` §4, `progress/current.md` sesión 34, y sale del handoff.

## C5 — El «cómo» del ADDENDUM 19-ago, con un caso que le agrega una condición

[[hallazgo-necesita-forma-presentable]] fija que la figura **importa** el código del número en
vez de reimplementarlo. Acá la primitiva que hacía falta (`permutacion_exacta`) devolvía el `p`
y **no** la distribución, o sea que dibujar el nulo exigía enumerar de nuevo, que es exactamente
lo que la regla prohíbe.

Se resolvió con un kwarg **aditivo y compatible** (`con_rhos=False`) que agrega la distribución
como quinto elemento sin tocar ningún valor ni ninguna firma existente. La condición que el
ADDENDUM no traía: **eso edita el script que produjo un número ya publicado**, así que hace falta
la regresión. Se corrió `b9_pleomorfismo.py` entero y su salida es **idéntica al log commiteado**
(`logs/b9_pleomorfismo.log`, 164 líneas, diff vacío) y `marcas_grado.csv` no se movió.

**Acción**: ADDENDUM corto en la memoria. La regla no cambia; se le agrega el caso «si para
importar el código hay que tocarlo, el cambio es aditivo y se verifica con el artefacto viejo».

## C6 — Lo que NO se toca

- **El pre-registro** (`prereg.md`): intacto. Ningún hallazgo de esta pasada reescribe una
  hipótesis (regla 9).
- **Las tablas del §2 de `resultados.md`**: los números publicados no cambian. C1 y C2 son
  lectura, y van como ADDENDUM fechado.
- **El deck del período** y su generador: la sesión paró antes de tocarlo, como pedía el handoff.
- **`b9_epitelio_estroma.py` y `b9_descriptores_nucleos.py`**: sin cambios.

---

# Cuarta pasada — 28-ago-2026 (sesión 35, de PLAN)

> Sesión sin código: Ernesto decidió qué pasa con las cuatro figuras y el plan quedó escrito
> **sin ejecutar**, para que lo tome una sesión limpia. Esta pasada registra la decisión y
> limpia lo que el avance de las sesiones 33 y 34 dejó stale en el **mapa del sprint**, que es
> el índice que toda sesión lee antes de elegir en qué trabajar.

| id | hallazgo | tipo | acción |
|---|---|---|---|
| D1 | El mapa del sprint dice que el eje 3 **sigue sin correr** | stale | corregido en dos lugares |
| D2 | El eje 3 medido y las cuatro figuras no tienen línea en «Decisiones tomadas» | falta | dos líneas nuevas |
| D3 | Las cuatro decisiones de Ernesto sobre el deck no están en ningún doc | falta | README + ADDENDUM |
| D4 | Dos pendientes que Ernesto acaba de decidir siguen escritos como abiertos | stale | cerrados |
| D5 | `envs/pruebas` corre el generador del deck entero | dato | al README, no a memoria |

## D1 — El mapa del sprint dice que el eje 3 sigue sin correr

`objetivos_sprint9.md:122` cierra la línea del eje 4 con «**El eje 3 sigue sin correr.**», y la
sección «Pendiente sharp» lo vuelve a enunciar como «**Ya pre-registrado** y **sin correr**».
Las dos eran verdad al escribirlas el 27-ago. El eje 3 se midió el 28 (sesión 33) y se dibujó el
mismo día (sesión 34), con su `resultados.md` §2 y su ADDENDUM.

Es el peor lugar donde puede quedar algo stale: por el formato de `objetivos_sprintN.md`
(CLAUDE.md §«índice, no almacén»), ese archivo es lo que una sesión nueva lee para orientarse, y
hoy le dice que lo principal del período está por hacer.

**Acción**: la frase del §Decisiones pasa a apuntar al resultado; el bullet de «Pendiente sharp»
se **elimina** de ahí, porque graduó a decisión tomada.

## D2 — Faltan las dos líneas de decisión

El §Decisiones tomadas tiene línea para el pre-registro y para el eje 4, y no para lo que salió
después: el **eje 3 medido** y las **cuatro figuras**. Se agregan las dos, con enlace y con el
número que las resume, en el formato de una línea por asunto.

## D3 — Las cuatro decisiones de Ernesto sobre el deck

Tomadas hoy, y no estaban escritas en ningún lado:

1. **Las cuatro figuras entran al cuerpo del deck**, entre los recortes de mitosis y la lámina
   de los ocho ejes. El deck pasa de **7 a 11 láminas**.
2. **Se actualizan OBJETIVOS y Tareas**, que si no quedan contradiciendo al deck: hoy dicen que
   los dos ejes de procesador son tarea del 08/09 y que el objetivo está «En curso».
3. **La tabla de Tareas queda con dos filas** (necrosis y punto caliente mitótico). No se
   reemplaza la fila que se libera.
4. **Se borra el `.pptx` huérfano en inglés.**

**Acción**: README de `presentacion_b9/` §Las decisiones de Ernesto, y ADDENDUM en la línea del
deck del mapa del sprint. **Nada de esto está ejecutado**: el plan lo ejecuta una sesión limpia
y hasta entonces el deck tiene siete láminas.

## D4 — Dos pendientes que ya no son pendientes

- README de `presentacion_b9/` §Pendiente: «Borrarlo lo decide Ernesto» sobre el `.pptx` en
  inglés. **Decidido**: se borra, y la sección se cierra.
- El docstring de `generate_figuras_ejes34.py` dice que las láminas están «listas para entrar al
  deck del período **cuando Ernesto lo decida**». Decidido también. **No se toca el archivo**: el
  plan lo reescribe entero (las cuatro láminas se mudan al generador del deck), así que editarlo
  hoy es churn. Queda en el handoff.

## D5 — Un env que corre el generador del deck entero

Verificado hoy: `/home/sdonoso/miniconda3/envs/pruebas/bin/python` con
`PYTHONPATH=.../.pylibs` importa **pptx 1.0.2, lxml, PIL, pandas, numpy, zarr y scipy** en un
solo proceso, y abre los TTF de Barlow. Importa porque al meter las figuras el deck pasa a
depender de `zarr` (vía `b9_pleomorfismo`) y hoy se corre con `clam_latest`.

**No va a memoria**: la del env (`hovernext-salida-geometria-y-clases`) es de la salida de
HoVer-NeXt y éste es un dato de decks; y el intérprete del deck **todavía no cambió**, porque el
plan no se ejecutó. Va al README, como condición del plan.

## D6 — Lo que NO se toca

> **ADDENDUM 28-ago (sesión 36): la primera viñeta quedó cumplida.** El plan se ejecutó el
> mismo día y el deck tiene once láminas. Ver §Quinta pasada.

- **El deck y su generador**: la decisión está tomada y **no ejecutada**. Ningún doc puede decir
  todavía que el deck tiene once láminas.
- **`resultados.md`, `prereg.md` y los scripts de los dos ejes**: sin cambios, no hubo medición.
- **Las memorias**: esta sesión no produjo un hecho durable nuevo. La tentación era registrar el
  env; D5 explica por qué no.

---

# Quinta pasada — 28-ago-2026 (sesión 36, de EJECUCIÓN)

> La cuarta pasada registró una decisión **no ejecutada** y por eso escribió, en D3 y D6, que
> ningún doc podía decir todavía que el deck tiene once láminas. Esta pasada la ejecuta y
> **levanta esa condición**. La cuarta no se reescribe: era verdad cuando se escribió, y es el
> registro de lo que la sesión de plan sabía.

| id | hallazgo | tipo | acción |
|---|---|---|---|
| E1 | La condición de D6 se cumple: el deck tiene once láminas | resuelto | ADDENDUM acá, docs al día |
| E2 | El intérprete del deck **sí** cambió, así que D5 dejó de ser condicional | stale | README |
| E3 | `resultados.md` §2 redondeaba mal un `p25` | error | corregido |
| E4 | Tres defectos de geometría que ninguna capa automática ve | dato | README §Lo que el QA visual encontró acá |

## E1 — La condición de D6, levantada

Ejecutado el plan del handoff: las cuatro figuras entran al cuerpo (s06 a s09), las tres tablas
dejan de contradecirlo, el guion suma cuatro bloques y la lámina de los ocho ejes pasa de `s03d`
a `s03h`. Se propagó a `presentacion_b9/README.md`, al ADDENDUM 28-ago de
`objetivos_sprint9.md` y a `ejes_nucleares/resultados.md` §4.

La **dependencia entre los dos generadores se invirtió**, que es lo único del plan que no era
contenido: las cuatro láminas y sus primitivas viven ahora en `generate_b9_deck.py` y
`generate_figuras_ejes34.py` quedó como envoltorio delgado. Al revés habría sido un ciclo, y
correr el deck como `__main__` habría cargado una segunda copia de su propio módulo.

## E2 — D5 dejó de ser condicional

La cuarta pasada dejó el dato del env `pruebas` en el README «como condición del plan», y
explicó que no iba a memoria porque el intérprete **todavía no había cambiado**. Cambió: el deck
importa `zarr` vía `b9_pleomorfismo` y `clam_latest` no lo tiene. El bloque «Regenerar» del
README ya no habla en futuro. **Sigue sin ir a memoria**: es un dato de este deck, y el README es
donde se busca.

## E3 — Un `p25` mal redondeado

`resultados.md` §2 daba `p25` = 83,8 para el grado `moderado` de la población restringida. El
valor es **83,7476**, o sea 83,7, que es lo que ya decía `numeros_figuras.csv`. Lo cazó el cruce
de la figura contra el doc, que es exactamente para lo que está esa capa: los dos venían del
mismo CSV y discrepaban sólo en el redondeo escrito a mano. **Corregido el doc**, que era el que
estaba mal.

## E4 — Tres defectos que ninguna capa automática ve

Los tres salieron de mirar el rasterizado y **ninguno** disparó un aviso de `auditar`. El
primero además no lo habría visto un chequeo de intersecciones, que es la herramienta que el
handoff anotaba como construible: la leyenda de s08 estaba a **0,08"** de la nube de puntos de
`alto`, alineada con ella y leyéndose como dos puntos más, **sin cruzarse**. El defecto era la
proximidad, no el solape.

Es un matiz que vale guardar sobre [[deck-qa-puntos-ciegos-chequeo]]: un chequeo de
intersecciones habría cazado el segundo defecto (s09, 0,05" de invasión) y no el primero.
**Escrito ahí como ADDENDUM 28-ago (noche)**, porque corrige una predicción que esa memoria
tenía en firme: decía que el chequeo no era construible, y sí lo era. Y para
que sirva de algo hay que **medir las cajas de texto**, no dárselas holgadas: las de la leyenda
de s06 medían 1,7" para 0,9" de texto y ensuciaban la salida con falsos positivos. Detalle en
`presentacion_b9/README.md`.

## E5 — Lo que NO se toca

- **`prereg.md` y los scripts de los dos ejes**: sin cambios, no hubo medición nueva. Los números
  del deck son los mismos de la sesión 33.
- **La cuarta pasada**: se le pone ADDENDUM, no se reescribe.

---

# Sexta pasada — 3-sep-2026 (sesión 46, de PLAN)

Alcance **muy acotado**: la sesión no tocó el deck ni midió nada. Verificó el plan de las cinco
láminas contra el archivo, Ernesto lo aprobó y cortó antes de ejecutar. La pasada registra lo que
esa verificación destapó, que **no** es sobre el plan sino sobre dos artefactos que quedaron
atrás de la sesión 45.

| id | hallazgo | tipo | severidad | acción |
|---|---|---|---|---|
| F1 | El aviso a `sgaete` pide una referencia que **ya tenemos** desde el 3-sep | stale | **alta** | reescribir esas líneas: lo abierto es su confirmación, no la referencia |
| F2 | El aviso dice «**tres** solapes» y desde el 3-sep son **cuatro**, y el cuarto es el más directo | stale | **alta** | encabezado + una pregunta nueva en el mensaje |
| F3 | `leer_atencion()` y `leer_escalera()` están escritos y **nunca se llaman**; los seis `PNG_*`/`JSON_*` de las cinco láminas, declarados y sin usar | — | media | anotarlo en el README y en el handoff: la sesión que ejecute tiene que cablearlos |
| F2.a | El mensaje abría con «tres cosas cortas» y ya traía seis; y «las otras **dos** preguntas» eran tres | stale | baja | opener sin número + encabezado corregido |
| F4 | Lo que NO se toca | — | — | — |

---

## F1 — El aviso pide el paper de las 3 mm², que apareció el mismo día

**Dónde**: `sprints/B9_sprint9/atencion_12_laminas/aviso_sgaete.md:83`, en la sección de preguntas
que **no** van en el mensaje.

**Qué dice**: «**El paper de las 3 mm²** que citó en la reunión: falta la referencia. El número
entra al deck como objetivo a demostrar, atribuido a él, **sin cita**.»

**Qué es verdad hoy**: la referencia **está**. La sesión 45 la encontró en su propio workspace,
`MitosisDetection/AreaMitosis.md`: Ibrahim, Lashen, Katayama, Mihai, Ball, Toss y Rakha,
*Defining the area of mitoses counting in invasive breast cancer using whole slide image*,
**Modern Pathology (2022) 35:739-748**, doi:10.1038/s41379-021-00981-w. Lo que sigue abierto es
**su confirmación de que ése es el que citó**, que es otra pregunta y más chica.

**Por qué importa y no es cosmético**: el aviso es un mensaje que **Ernesto va a mandar**. Tal
como está le pide a Sebastián un dato que ya tenemos, que es justo lo que
[[verificar-antes-de-pedir-dato]] existe para evitar, y encima delante de la persona que lo tenía
guardado. La misma línea sostiene el «sin cita» de la fila de la lámina 13, que también cambió.

**Acción**: reescribir el ítem — la referencia se da por encontrada, se pide confirmación, y se
declara que atribuirla a su cita es una **inferencia** nuestra ([[paper-3mm2-ibrahim-modern-pathology]]).

## F2 — El aviso cuenta tres solapes y son cuatro

**Dónde**: `aviso_sgaete.md:4` («ahora hay **tres** solapes y no uno») y el cuerpo del mensaje,
que pregunta por el pipeline de atención y por el `json_out` pero **no menciona** el cuarto.

**Qué es verdad hoy**: son **cuatro** desde el 3-sep, y el cuarto es el más directo de todos. Sus
jobs `5213 hnx_time` y `5249 hnx_win` corren **HoVer-NeXt con `lizard_convnextv2_tiny`, nuestro
mismo checkpoint**, sobre **81 ventanas** de **nuestras mismas láminas**
([[sgaete-yolo-mitosis-solapamiento]], ADDENDUM del 3-sep).

**Por qué importa**: el aviso **es** el mensaje de coordinación sobre solapes, y el que falta toca
de frente la **fila 2 de la lámina 13** del deck, el punto caliente por ventana de área fija. El
handoff ya lo sabía y lo dejó anotado como pendiente; el artefacto que se manda, no. Presentar esa
fila como tarea nueva delante de él, sabiendo que ya la corre, se lee mal, y ése es el riesgo
concreto: no es técnico, es de reunión.

**Acción**: encabezado a cuatro solapes y una pregunta nueva en el cuerpo, **¿qué cubre
`hnx_win`?**, antes de presentar la fila. Las otras dos preguntas del 6-ago siguen **deliberadamente
afuera**.

## F3 — Los dos lectores están escritos y nadie los llama

**Dónde**: `presentacion_b9/generate_b9_deck.py` — `leer_atencion()` en :722 y `leer_escalera()`
en :766; `main()` (:1533-1535) sólo llama a `leer_datos`, `datos_eje4` y `datos_eje3`. Los seis
constantes de las cinco láminas (`PNG_HOVERNEXT`, `PNG_ATENCION`, `PNG_REGIONES`, `PNG_NUCLEOS`,
`JSON_REGIONES`, `JSON_NUCLEOS`, :91-97) están declarados y **sin una sola referencia** aguas abajo.

**No es un defecto**: es exactamente lo que la sesión 44 dejó a propósito, y el deck compila limpio
en ocho láminas porque nada de eso se usa todavía. Se registra porque **«los dos lectores ya existen
y están verificados»** (handoff §1) se puede leer como «ya están conectados», y no lo están.

**Verificado corriéndolos** en esta sesión, con el intérprete del deck: `leer_atencion()` devuelve
**0,8086 ± 0,1273 · 0,7924 ± 0,1221 · 0,7701 ± 0,1279**, n = 9 en los tres brazos y **9 de 9 sobre
el azar** en los tres; `leer_escalera()` devuelve los cinco peldaños y los seis conteos duros sin
moverse. Los dos abortan solos si algo se corrió.

**Acción**: una línea en `presentacion_b9/README.md` y el punto explícito en el handoff.

## F2.a — Y el mensaje abría prometiendo tres cosas cuando ya traía seis

**Dónde**: el opener del mensaje, «Tres cosas cortas sobre las láminas anotadas».

**Qué pasaba**: ya el 2-sep el mensaje tenía Una / Dos / Tres **más** la respuesta al tamaño de
parche y la pregunta por la rama predicha, o sea cinco; con la de `hnx_win` quedaban seis. El
número del opener nunca se movió.

**Por qué se anota aparte**: es el mismo síntoma que F2 en chico, y el barato de cazar. Un
artefacto que **cuenta cosas** («tres solapes», «las otras dos preguntas» sobre una lista de tres,
«tres cosas cortas») lleva un número que se desactualiza solo cada vez que alguien agrega un ítem,
y ninguna capa automática lo mira. Los tres estaban mal en el mismo archivo.

**Acción**: opener sin número, que además ordena la lectura («las tres primeras son estado; las
del final son preguntas»), y el encabezado de la sección de abajo pasa de «las otras **dos**
preguntas» a «las otras preguntas». Regla que se desprende: [[tracker-al-dia-artefacto-stale]].

## F4 — Lo que NO se toca

- **El plan aprobado** (`.handoffs/plan_B9_20260903_cinco_laminas_D4_D5.md`): es efímero y
  gitignored. Su §«La lámina 13» dice «sin cita» y quedó atrás del handoff §6.3, que es posterior
  y manda; se deja como está y la corrección vive en el handoff nuevo.
- **El deck y la galería**: en ocho láminas, sin tocar. Cero medición nueva.
- **Las cinco pasadas anteriores**: se les agrega abajo, no se reescriben.
