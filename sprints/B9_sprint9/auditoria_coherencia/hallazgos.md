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
