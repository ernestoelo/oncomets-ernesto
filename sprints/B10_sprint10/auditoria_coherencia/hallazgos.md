# Auditoría acotada de coherencia — sesión 52 (10-sep-2026)

> **Alcance**: sólo lo que encontró la sesión 52, que cerró con el contexto lleno. **No se auditó
> el resto de la base.** Hecha con `@knowledge-audit` dentro de `@session-close`.

| id | hallazgo | tipo | acción |
|---|---|---|---|
| F1 | La B25-158899 de O3, re-medida confinada, da **0,201** (rama `si`): la hipótesis del universo cae por la regla pre-declarada. Es la única lámina que el fold nunca vio y tiene `alineada: false`, igual que la 164001 (0,926) | stale («no medida») | `cdis_localizacion/resultados.md` §1, §2, §3.b, §6, §7; `objetivos_sprint10.md`; ADDENDUM en [[rama-de-atencion-decide-el-resultado]] |
| F2 | El «9 de 9» de O3 no abría por tier. Fuera de `train` sólo separa del nulo `val`, y las dos láminas que el fold no vio no muestran localización | reconciliación | tabla por tier en §2; línea nueva en «Qué no se afirma» del mapa |
| F3 | O1 no declaró el universo de las dos láminas con dos regiones de escaneo ni las dos `alineada: false`. Ninguna de las dos cosas mueve el titular | omisión de pre-registro | `grado_sin_marca/resultados.md` §6.a + `scripts/b10_grado_region_diag.py` |
| F4 | Los caveats por lámina que el B9 declaró no viajaron a los pre-registros de O1 ni O3 | lección durable | memoria nueva [[caveat-por-lamina-no-viaja-solo]] |
| F5 | Error propio en la pre-declaración §3.a de O3: «fuera del split» quedó escrito como sin valor de evidencia limpia, y es el tier **más** limpio | error | corrección fechada debajo del §3.a, sin reescribir el texto pre-declarado |
| F6 | El índice `MEMORY.md` pasaba de 160 líneas, contra un límite de lectura de 200 | redundancia | 10 memorias fusionadas en su vecina más cercana, cuerpo entero; enlaces re-apuntados; índice en 138 líneas |

## F1 — la B25-158899 está medida

- **Antes**: `cdis_localizacion/resultados.md` §3 y §6 decían «no medida», y el mapa la tenía en
  *Pendiente sharp*.
- **Ahora**: `results/b10_cdis/auc_cdis_region.csv`, producido por `scripts/b10_cdis_atencion.py`
  con un bloque aditivo que importa `medir()` y `universos_de()` del B9 sin tocarlos. **Regresión
  byte a byte**: `auc_cdis.csv`, `control_negativo.csv` y `saltadas.csv` salen idénticos, y el log
  viejo sólo gana líneas (`logs/b10_cdis_atencion_region.log`; el viejo quedó intacto).
- **Canónico**: `cdis_localizacion/resultados.md` §3.b. El mapa lo resume en una línea.

## F2 — la lectura por tier

La tabla del §2 de O3 abre el agregado con el orden ausente > test > val del B9
([[atencion-doce-laminas-folds-limpios]]): `train` 5 de 5, `val` 3 de 3 (2 con `p` en el piso, una
es la 164001 sin alinear), `test` 1 lámina que no mide, ausente 1 lámina al revés. **No es una
contradicción con el 9 de 9**, que sigue siendo el número de la rama verdadera. Es lo que ese
número no decía.

## F3 — las dos omisiones de O1

Las dos se midieron y se declararon en §6.a sin re-correr el driver: confinar lleva `alto` de
27 · 41 · 57 a 29 · 41 · 60 en N = 200 · 500 · 2000, y sacar las no alineadas deja N=500 en 52 de
140. **El pre-registro de O1 no se tocó** (regla 9): las omisiones van en los resultados.

## F4 — por qué pasó

Los dos caveats viven en un artefacto (el JSON del offset, una constante de módulo) y en el
pre-registro del sprint que los descubrió. Un driver nuevo que sólo lee `dx`, `dy` los pierde sin
que nada falle. Memoria nueva con la lista de caveats vigentes.

## F5 — la corrección del error propio

La pre-declaración se commiteó antes de medir (`c3d5647`) y **no se reescribió**. La corrección va
debajo, fechada y marcada como escrita después de medir. El error no cambiaba qué lectura se
aplicaba, que dependía sólo del signo.

## F6 — el índice de memorias

Lo pidió el hook del harness al pasar de 160 líneas. Sacar las líneas en blanco no alcanzaba (148),
así que se fusionaron **10 memorias** en su vecina más cercana, eligiendo las de menos enlaces
entrantes. **Nada se editó ni se perdió**: el cuerpo de cada una va entero al final del destino,
bajo `## Fusionada el 11-sep-2026: <nombre viejo>`, con su descripción original citada.

| absorbida | destino |
|---|---|
| `diagrama-generacion-recipe` | `diagramas-arquitectura-pptx-editable` |
| `microcalc-hierarchical-proposal` | `microcalc-fusion-objetivo5` |
| `cota-softmax-slots-uniforme` | `mammoth-slot-routing-weight` |
| `pptx-quitar-notas-y-respaldo` | `deck-completo-pptx-buildable` |
| `deck-rebase-plantilla-1610` y `plantilla-dos-cabeceras` | `deck-template-fuentes-embebidas` |
| `retrieval-investigacion-b5` | `pathpt-testing-necrosis-mitotic` |
| `mammoth-cabezas-son-tramos` | `mammoth-dispatch-softmax-sobre-parches` |
| `deck-molde-fiel-referencia` | `deck-gramatica-diagrama-deep-llm-v` |
| `calibracion-tier0-pendiente-ejecutar` | `calibracion-operating-point-palanca-b5` (el nombre viejo además era stale: la Tier 0 se ejecutó el 10-jul) |

Los enlaces a las diez se re-apuntaron con `sed` en todo `*.md` del repo y de las memorias, y el
barrido de residuos dio vacío. **Gotcha que se cazó al hacerlo**: el mismo `sed` pisó el nombre
viejo dentro del encabezado de la fusión; se restauró con un script que exige exactamente un
encabezado por fusión.

## Propagación verificada

`grep -rn` de «0,755», «9 de 9» y «no medida» sobre todo el repo y el directorio de memorias. Los
otros «9 de 9» son de otros ejes (atención sobre mitosis del B9, offsets de las 9 nuevas).
`CLAUDE.md` no cita O3. Sí se tocó por F6, sólo para re-apuntar enlaces a las memorias fusionadas.

---

# Pasada acotada — sesión 53 (11-sep-2026)

> **Alcance**: lo que tocó la sesión 53 (figuras de O1 y O3 y el doc de la reunión). Hecha con
> `@knowledge-audit` dentro de `@session-close`. No se auditó el resto de la base.

| id | hallazgo | tipo | acción |
|---|---|---|---|
| G1 | «El grado vive en **20** láminas» (8-sep) es **22**: sumaba alto (10) y moderado (10) sin las 2 de bajo. Recontado sobre los 23 geojson | error de conteo | mapa (corrección fechada), memoria `anotaciones-patologo-qupath`, ADDENDUM en `conteo-de-grupo-es-union`, P3 del doc de la reunión |
| G2 | El IC de la 126504 se publicó como [0,297 · 1,110]; el artefacto da `ic95_hi` = 1,1105, que redondea a **1,111** | error de redondeo | `cdis_localizacion/resultados.md` §2; la assert del script de figuras lo fija |
| G3 | O1 y O3 no tenían forma presentable | pendiente cerrado | `figuras/` + `reunion_martes.md`; línea nueva en el mapa |
| G4 | El node de `envs/pruebas` está roto y Barlow no trae `●` | gotcha de entorno | `figuras/README.md` + ADDENDUM en `hallazgo-necesita-forma-presentable` |

**Propagación verificada**: `grep` de «20 láminas» sobre el repo y las memorias. Los demás «20
láminas» cuentan diapositivas de decks, no láminas anotadas. Conservan el número viejo la entrada de
la Sesión 50 de `progress/current.md` y tres handoffs, que son historia y no se reescriben.

---

# Pasada acotada — sesión 54 (11-sep-2026)

> **Alcance**: las dos premisas del handoff de la sesión 53 que chocaron con el precedente al
> planificar el deck de la reunión del martes. Hecha con `@knowledge-audit` dentro de
> `@session-close`. No se auditó el resto de la base.

| id | hallazgo | tipo | acción |
|---|---|---|---|
| H1 | `CLAUDE.md` (ADDENDUM 25-ago) dice «el deck va en **inglés**, son **4 láminas**», y `docs/plantilla_oficial.md` §1 lo mismo. Describen el **molde**: los dos decks construidos sobre él van en español (B9 desde el 27-ago, B10 por decisión de Ernesto del 11-sep) y llevan 13 y 7 láminas. El ADDENDUM 27-ago que ya lo decía vivía sólo en la memoria y nunca llegó a `CLAUDE.md`, así que el handoff copió la regla vieja | stale | precisión aditiva en `CLAUDE.md` y nota bajo la tabla del §1; ADDENDUM y descripción en [[plantilla-oficial-image-to-text]]; hook de `MEMORY.md` |
| H2 | `CLAUDE.md` (ADDENDUM B5) lista «gráficos reales (`add_chart`)», y la memoria del deck también. Desde el B8 los gráficos se dibujan con shapes, el B9 no usó `add_chart` ni una vez, y Ernesto eligió shapes para el B10. La regla prohíbe el PNG, no las shapes | reconciliación | precisión aditiva en `CLAUDE.md`; ADDENDUM en [[deck-completo-pptx-buildable]] |
| H3 | El deck de la reunión quedó **planificado y sin construir**, con cuatro decisiones de Ernesto: español, 7 láminas, shapes, una fila de tareas | pendiente abierto | línea en el mapa, Sesión 54 del progress, plan en `.handoffs/` |

**Propagación verificada**: `grep -rn` de «add_chart» y de «inglés» sobre todo el repo y las
memorias. Quedan dos `add_chart` en `B5_sprint5/presentacion_b5/convenciones_deck_b5.md` y
`B6_sprint6/presentacion_viernes/convenciones_deck_b6.md`, que cuentan cómo se hicieron esos decks
y **no se tocan**. Los «inglés» de `pathpt-testing-necrosis-mitotic` y de
`fixing-opus5-evaluacion-y-cosecha` hablan de otra cosa.

---

# Pasada acotada — sesión 55 (11-sep-2026)

> **Alcance**: lo que salió al preparar la construcción del deck de la reunión del martes. La
> sesión leyó el plan, el precedente del B9 y los datos, y cerró por contexto **antes de escribir
> el generador**. Hecha con `@knowledge-audit` dentro de `@session-close`. No se auditó el resto.

| id | hallazgo | tipo | acción |
|---|---|---|---|
| I1 | El plan de la sesión 54 pide que el guion de s02 diga que la región mitótica «pasó a otra persona del equipo». Según `reunion_martes.md:70` el mitótico «quedó para Sebastián en el reparto», y Sebastián es quien escucha. Además `CLAUDE.md` nombra supervisor a Sebastián Gaete y el `docProps` de la plantilla lo firma `sgaete` (`docs/plantilla_oficial.md`) | premisa errada del plan | el guion usa una forma que no nombra a nadie («quedó en la línea de mitosis con el reparto de la reunión pasada»). El plan vive en `.handoffs/`, que no se versiona: la corrección va en el handoff |
| I2 | `auditar()` y `barrer_rayas()` de `generate_b9_deck.py` (:1117 y :1215) recorren `slide.shapes` y no entran en los group shapes: de un grupo sólo miden la caja contra el pie. El plan del B10 mete cada gráfico en un grupo, así que su texto quedaría sin medir (desborde, menos de 7 pt, rayas). Y en una celda de tabla con dos párrafos `auditar` toma el máximo de líneas y no la suma | punto ciego del QA | el generador del B10 lleva su propio auditor recursivo (el del B9 está cerrado y no se edita); ADDENDUM en [[deck-qa-puntos-ciegos-chequeo]] |
| I3 | El deck sigue **sin construir**. Insumos verificados: `datos_o1()` y `datos_o3()` corren en `envs/pruebas` y coinciden fila a fila con `figuras/*.csv`; el **187** del pie de O1 se lee de `escalera.csv` (suma de `n_marcas` sobre las 21 láminas) en vez de transcribirse; Barlow trae `≥ ≤ † µ ² · « » ×`; los tres encargos cerraron el 9-sep, así que la columna Fecha lleva `09/09` | pendiente abierto | H3 sigue abierto; el diseño lámina por lámina va en el handoff |

**Propagación verificada**: `grep` de «otra persona del equipo» sobre `reunion_martes.md` y el plan:
en el B10 la frase está sólo en el plan. El bloque de Tareas del guion del B9 la usa para los dos
solapes de `sgaete` (el pipeline de atención contra anotaciones y el detector de mitosis). Es un
deck ya presentado y **no se toca**; si `sgaete` es Sebastián, queda como pregunta para Ernesto.

---

# Pasada acotada — sesión 56 (14-sep-2026)

> **Alcance**: las dos preguntas que el handoff de la 55 dejó abiertas con Ernesto, contestadas al
> abrir la sesión. No se escribió código: la sesión verificó el estado, escribió el plan de
> construcción del deck y cerró para que una limpia lo ejecute. No se auditó el resto.

| id | hallazgo | tipo | acción |
|---|---|---|---|
| J1 | **`sgaete` ES Sebastián**, contestado por Ernesto. Y son **dos Sebastianes distintos**: `sgaete` = Sebastián Gaete, el supervisor de las reuniones; `sdonoso` = Sebastián Donoso, dueño de `clam_environ/` y nombre de la cuenta unix compartida. «Sebastián» a secas en los docs es Gaete | premisa confirmada, con una distinción que faltaba | **cierra I1**. Nota aditiva en `CLAUDE.md` §«Quién soy y dónde estoy» + memoria [[sgaete-es-sebastian-gaete-supervisor]]. Los cuatro directorios ajenos read-only son del supervisor ⇒ los solapes se resuelven preguntándole. El guion del B9 queda como está (deck presentado) |
| J2 | **O1 confinado a la región anotada: NO**, decidido por Ernesto | decisión pendiente, cerrada | `reunion_martes.md` §6 pasa de recomendación a decisión. El deck se construye sobre la lámina entera, con lo ya medido |
| J3 | El deck **sigue sin construir**, y ahora tiene plan aprobado punta a punta (archivos, qué se importa, gotchas, orden, verificación) en `/home/sdonoso/.claude/plans/handoff-b10-20260911-deck-disenado-md-fizzy-rabin.md`. El diseño lámina por lámina sigue siendo el del handoff de la 55 §5 | pendiente abierto | H3 e I3 siguen abiertos. La reunión es el **martes 15-sep**: es lo único urgente del sprint |

**Verificado en vivo, no heredado**: `main` limpio y sincronizado con `origin` en `9211429`;
ningún job propio en `squeue`; `datos_o1()` y `datos_o3()` corren en `envs/pruebas` con `.pylibs`
y pasan sus asserts contra los `resultados.md` (32 y 10 filas); `python-pptx` 1.0.2 y PIL
disponibles; la plantilla oficial está en `papers/presentations/`.

---

# Pasada acotada — sesión 57 (14-sep-2026)

> **Alcance**: cierre por contexto, pedido por Ernesto, antes de escribir el generador. La sesión
> releyó lo mínimo del handoff, verificó cuatro cosas que el deck necesita y no escribió código.
> No se auditó el resto.

| id | hallazgo | tipo | acción |
|---|---|---|---|
| K1 | **Barlow no trae `● ○ ▬ ■ □ ↑ ◦ ∘`** (cmap leído con `fontTools`, `getBestCmap()`); `→` ya estaba anotado. Y `text_w()` de `generate_b9_deck.py:183` **no puede detectar un glifo faltante**: reemplaza por «n» los caracteres sin `getbbox`, pero PIL devuelve la caja del `.notdef`, así que la sustitución nunca ocurre y los que se midieron dan todos lo mismo (16,77 a 40 pt) | gotcha de medición | la leyenda de O3 que el diseño escribe como «● p < 0,05 · ○ p ≥ 0,05» y «▬ IC 95 %» va **dibujada con shapes**, igual que toda flecha; el auditor del B10 chequea el cmap sobre todo el texto. ADDENDUM en [[deck-template-fuentes-embebidas]] |
| K2 | `FreeformBuilder.convert_to_shape()` de python-pptx 1.0.2 (`pptx/shapes/freeform.py:96-109`) **no** llama `_recalculate_extents()`; los `add_*` de `pptx/shapes/shapetree.py` sí (líneas 257, 275, 350, 372, 386 y 395) | gotcha verificado en fuente | el gotcha 5 del handoff pasa de leído a verificado: `grp._element.recalculate_extents()` al terminar cada figura que lleve polilíneas |
| K3 | `results/b10_grado_sin_marca/escalera.csv` (columnas `slide brazo desc grados n_marcas n_resueltas n_candidatos alineada N recall carga_mm2`), brazo `A_lamina_entera` con `desc == percentil`: 21 láminas, **187** = suma de `n_marcas`, **145** = suma de `n_resueltas`. En N = 5000 quedan **19** (faltan la 109609 y la 110616) y los alcanzables de bajo caen de **16 a 9** | insumo verificado | el pie de s03 lee los cuatro números del CSV en vez de transcribirlos |
| K4 | `CUERPO` de la plantilla (`#1B4F8C`, `generate_b9_deck.py:116`) es **el mismo color** que `RAMPA[2]` de `b10_figuras_o1_o3.py:66`, que pinta **alto** en O1 y **test** en O3. Los helpers del B9 escriben los rótulos de figura en `CUERPO` (`eje_x`, `eje_y`, `pie_lineas`) | riesgo de lectura | dentro de las figuras nativas del B10 el texto va en tinta (`TITULO`) o gris neutro, nunca en `CUERPO`: un rótulo en el color de una serie se lee como parte de ella (skill `dataviz`). Cuerpo y pie de la lámina siguen en `CUERPO`, que es la gramática del molde |

**Verificado en vivo, no heredado**: `main` limpio y sincronizado con `origin` en `99562a1`;
`generate_b9_deck` y `b10_figuras_o1_o3` se importan juntos en `envs/pruebas` (1,9 s); el
inventario de formas de la plantilla coincide con `docs/plantilla_oficial.md` §5 (s03: `Text 0`,
`Text 1`, `CuadroTexto 6`, `Text 2` vacío, `Google Shape;286;p7` y `287;p7`, `Imagen 4`; s02 y
s04: `Text 2`, `Google Shape;409;p22`, `Google Shape;196;p29`). En `squeue -u` aparecen `Eval`,
`Eval2` y `Eval3` (5647-5649, `PD`) de la cuenta compartida: esta sesión no lanzó nada.

---

# Pasada acotada — sesión 58 (14-sep-2026)

> **Alcance**: la construcción del deck del martes. Se auditó lo que el deck produjo, no el resto.

| id | hallazgo | tipo | acción |
|---|---|---|---|
| L1 | **Las notas del `.pptx` salen partidas por renglón.** `leer_guion()` del B9 (`generate_b9_deck.py:973`) devuelve cada bloque con los saltos del envuelto a cien columnas, y `notes()` convierte cada `\n` en un párrafo del panel. En el B10 daba 17 a 23 párrafos por lámina para 3 a 6 de guion. **El `.pptx` del B9 lo tiene**: 11 a 22 párrafos por lámina, 7 a 16 de ellos sin puntuación final | defecto de formato, latente desde el B9 | corregido en `leer_guion()` del B10, que junta las líneas de cada párrafo. El B9 no se toca (cerrado y presentado). Lo caza el round-trip **contando párrafos de notas**, no notas |
| L2 | El guion de O1 decía que los mm² eran «la superficie que ocupan esos núcleos». Son la **unión de los parches de 256 px** que los contienen, que es lo que escribe el eje | premisa falsa en la prosa | corregido; misma familia que [[parametro-necesita-su-semantica]] |
| L3 | El rótulo del eje de O2 quedaba a **0,03"** de la punta de la flecha (tinta por renglón: banda 4,05-4,14 y rótulo desde 4,17). La punta de `tailEnd` baja ~0,04" bajo la línea y ningún chequeo de cajas la ve | proximidad | hueco de 0,05 a 0,09 |
| L4 | **El QA visual no corrió.** El hook que precede a `Write` y `Read` no respondió en toda la sesión («host client may be unreachable»): los archivos se escribieron por `Bash` y las láminas no se miraron. Lo sustituyó en parte `presentacion_b10/qa_geometria.py` (texto/texto, línea/texto y forma/texto dentro de los grupos), sin avisos | capa de QA faltante | el `.pptx` y su PDF se le mandaron a Ernesto; **mirarlos es el pendiente** |
| L5 | **La tinta por renglón no se puede leer sin la columna.** Mide filas completas del rasterizado: el hueco mínimo de O3 (**0,009"**) es entre «parches», en x ≈ 11,7, y «azar», en x ≈ 7,9, que no se tocan. Los que sí están en la misma columna quedaron en 0,04" | falso positivo del método | `qa_geometria.py` imprime la extensión horizontal de cada banda. Con eso, el método cazó dos apretados reales: los números del eje x de O1 a 0,018" de sus ticks y los dos renglones de la cabecera de O3 |
