# A3 — los offsets de las 12 láminas anotadas, y el denominador que habilita B1

> Medido el **21-ago-2026**, CPU post-hoc, sin GPU y sin escribir nada fuera del repo.
> Driver: [scripts/run_a3_offsets.sh](../../../scripts/run_a3_offsets.sh) ·
> denominador: [scripts/a3_denominador_mitosis.py](../../../scripts/a3_denominador_mitosis.py) ·
> log: `logs/a3_offsets_desatado.log`.
> Salidas: `sprints/B8_sprint8/anotaciones_patologo/{offset_<id>.json,parches_anotados_<id>.csv,
> denominador_mitosis_12.json}`.

Sin esto la fase B1 da cero: el geojson del patólogo **no** está en coordenadas de openslide
y, sin corregir, en la 129741 caían **0 de 26** marcas sobre un parche. A3 deriva la
traslación de las 11 láminas que faltaban y verifica que sirva.

## 1. El resultado que habilita B1

**Las 94 marcas de `Mitosis` de las 12 láminas caen sobre un parche extraído. Las 94.**

| lámina | marcas | sobre parche | dx | dy |
|---|---|---|---|---|
| 129741 | 26 | **26** | 3829 | 0 |
| 126504 | 20 | **20** | 8981 | 0 |
| 128194 | 17 | **17** | 7431 | 0 |
| 124729 | 8 | **8** | 13358 | 0 |
| 124806 | 6 | **6** | 8890 | 0 |
| B25-158899 | 6 | **6** | 22708 | 0 |
| 144317 | 3 | **3** | 10349 | 0 |
| 164001 | 3 | **3** | 11261 | 0 |
| 106552 | 2 | **2** | 15501 | 0 |
| 103762 | 1 | **1** | 19148 | 0 |
| 109609 | 1 | **1** | 10030 | 0 |
| 110616 | 1 | **1** | 8981 | 0 |
| **total** | **94** | **94** | | |

Es el **techo del filtro** que va delante de la etapa cara (patrón P2.a): una marca cuyo
centroide no cayera sobre un parche no la recupera nadie, por bueno que sea el detector.
Acá el techo es 94 de 94, así que **la alineación no acota nada** y el denominador honesto de
B1 es el agregado de 94. Un techo alto no promete nada: solo deja la pregunta viva.

Las seis láminas con ≤3 marcas siguen sin sostener un número propio. La tabla va con su `n`
al lado y el recall se reporta **agregado**.

## 2. El offset es la geometría del contenedor, en las 12

En las 12 láminas el offset adoptado es `dx = level0.width − region[0].width`, `dy = 0` — el
mismo control geométrico que ya había ganado en la 129741 el 31-jul. En las 12 el criterio (c)
(refinamiento por área) **no separa** ese candidato de su óptimo empírico dentro de la
tolerancia del 0,5 %, así que gana el que tiene explicación independiente.

Y en los tres casos donde los barridos empíricos (a) y (b) **no se cruzan**
(124729, 164001, B25-158899, más 109609), el offset geométrico es **mejor que cualquier cosa
que los barridos hayan encontrado**: en B25-158899 el mejor de (a) daba 12 de 38 y el
geométrico da 27; en 164001 el mejor de (a) daba 22 de 30 y el geométrico da 23. O sea que el
«revisar a mano» que imprime el script no es un caso sin resolver: es el barrido de centroides
quedándose corto donde el contenedor sí sabe la respuesta.

## 3. Dos láminas no pasan el chequeo de las anotaciones GRANDES, y no importa para B1

El script marca `alineada: false` cuando menos del 80 % de **todas** las anotaciones cae sobre
tejido. Fallan dos:

| lámina | (a) sobre parche | (b) sobre tejido | marcas de Mitosis sobre parche |
|---|---|---|---|
| B25-158899 | 27/38 (71 %) | 27/38 | **6/6** |
| 164001 | 23/30 (77 %) | 23/30 | **3/3** |
| *(control)* 129741 | 58/61 (95 %) | 58/61 | 26/26 |

**El chequeo mide otra cosa que la que B1 necesita.** Lo que se cae son polígonos grandes
(`Negative`, `Tejido Adiposo`, `Tumor`) cuyo centroide queda sobre fondo o sobre tejido que
CLAM no teseló; las marcas de mitosis, que son objetos de ~40 px, caen todas. Se deja el flag
porque describe la calidad general del mapeo parche → clase, **pero la condición de entrada al
agregado de B1 es la columna de la derecha**, y esa da 94 de 94.

Un caso más muestra que el flag es del instrumento y no de la lámina: **110616 da (a) 30/30 y
(b) 24/30** — el offset ubica *todas* las anotaciones sobre parches y aun así la máscara de
saturación de la miniatura pierde seis. La máscara es gruesa por construcción; los parches son
la evidencia fuerte, porque solo existen donde CLAM detectó tejido.

## 4. Dos correcciones de código que salieron al generalizar

Las dos estaban tapadas porque la 129741 **no las dispara**, y las dos habrían corrompido B1
en silencio.

**(i) El paso de grilla se derivaba mal en 9 de 12 láminas.**
`patch_size_desde_coords()` tomaba la moda del paso sobre el `np.unique` **global** de cada
eje. CLAM arranca la grilla en el bbox de cada contorno de tejido, así que una lámina con
varias islas tiene varias grillas desfasadas y el unique global mezcla los desfases con el
paso real: devolvía **64 o 128 donde el paso real es 256**, en 9 de las 12. La 129741 daba 256
por casualidad, y por eso nadie lo vio. Un paso mal derivado rompe las dos cosas que el script
hace: la pertenencia a celda del criterio (a) y el conteo de parches bajo cada anotación.
Corregido a la moda **por fila y por columna**, que es la forma que ya usaban
`auditar_regiones_escaneo.py`, `auc_atencion_fold4.py` y `atencion_vs_anotaciones.py`. Ahora da
**256 en las 12**. Precisa la memoria [[patch-size-desde-geometria-h5]]: el tamaño sale de la
geometría, sí, pero la moda hay que tomarla dentro de la fila, no sobre el conjunto entero.

**(ii) QuPath deja anotaciones sin clase.** Hay **2 en las 12 láminas** (una en 126504 de
1210 px², una en 106552 de 250 px² — tamaño de núcleo), con `properties = {"objectType":
"annotation"}` y sin `classification`. El script crasheaba al formatear `None`. Se conservan
con el nombre explícito **`(sin clase)`**: cuentan como tejido para el criterio (c) y **no se
suman a ninguna clase real** — en particular **no entran al denominador de Mitosis**.

**Test de regresión**: re-corrida la 129741 con el código nuevo, `parches_anotados_129741.csv`
sale **byte-idéntico** al del 31-jul y `offset_129741.json` solo gana las tres claves de
verificación. El `dx=3829, dy=0` no se movió, así que nada de lo ya publicado sobre esa lámina
cambia.

## 5. Qué queda listo para B1

- `offset_<id>.json` y `parches_anotados_<id>.csv` para las **12**.
- `denominador_mitosis_12.json` con el techo por lámina.
- `Y_CORTE_REGION`: **solo 2 de las 12 tienen dos regiones de escaneo** — la 129741
  (`region[1].y = 49920`, ya en uso) y **B25-158899 (`region[1].y = 30720`)**. Las otras 10
  tienen una sola región y **se saltan el confinamiento**. La constante de módulo de
  [techo_atencion_topk.py:45](../../../scripts/techo_atencion_topk.py#L45) **sigue sin
  generalizar**: la tabla de arriba dice qué valor le corresponde a cada lámina, pero el
  cambio de código no se hizo. Es lo primero que hay que tocar cuando B1 llegue al top-K.

## 6. Qué no se afirma

- **Nada de esto es precisión, y ninguna marca ausente es un negativo.** El patólogo marca
  solo donde la evidencia es clara: un parche sin anotación **no** es un negativo, y las 94
  son «las marcadas», no «las que hay».
- **No se midió nada de HoVer-NeXt.** A3 no lo toca. El 13 de 26 de la 129741 no se mueve.
- **94 de 94 es el techo, no un resultado.** Dice que la alineación no va a ser la excusa;
  no dice cuántas va a recuperar el detector.
- **El flag `alineada` no es un veredicto sobre la lámina**, es un resumen grueso sobre todas
  las clases; ver §3.
- **`(sin clase)` no se interpretó.** No se afirma qué son esas 2 anotaciones.
- Unidad: **marcas (94 en las 12, 26 en la 129741)**. Los **113 parches** que quedan tocados
  por alguna marca en las 12 son otra unidad y no se mezclan; tampoco las 177 detecciones ni
  las 28 marcas-parche de la 129741.
