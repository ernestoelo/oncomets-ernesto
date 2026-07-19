# Hallazgos — sesión "template válido + fuentes embebidas" (19-jul-2026, tarde)

> Auditoría acotada al eje **deck B7 / template**. Dispara el hallazgo de esta sesión:
> Ernesto fijó cuál es el template válido, y la causa raíz del síntoma "no tiene el
> template" resultó ser otra que la diagnosticada por la mañana.
>
> Sesión previa del mismo día: `hallazgos.md` (migración de cabeceras, commit `42280de`).

## Resumen

| id | hallazgo | tipo | severidad | acción |
|---|---|---|---|---|
| T1 | El template válido es `Modelo OncoMets Spatial V1 Deep-LLM-V.pptx`, no `Plantilla.pptx` | error | **alta** | ADDENDUM en CLAUDE.md §Formato de entregables |
| T2 | La causa raíz del deck "fuera de template" eran las **fuentes embebidas**, no las cabeceras | error | **alta** | memoria nueva + ADDENDUM en [[plantilla-dos-cabeceras]] |
| T3 | El "How to apply" de [[plantilla-dos-cabeceras]] quedó superseded (banda compactada, tope de títulos) | stale | media | ADDENDUM fechado, no reescritura |
| T4 | Pendiente §7.2 del handoff ("confirmar que Barlow está instalada") quedó resuelto estructuralmente | stale | media | cerrar, NO arrastrar al handoff nuevo |
| T5 | Los diagramas reusados referencian Carlito (354 veces), que no existe en Windows | reference | baja | registrar como gotcha conocido, sin acción |

---

## T1 — El template válido es Deep-LLM-V

**Qué decía CLAUDE.md** (§Formato de entregables, L875-877): *"Estilo visual:
`Modelo_OncoMets_Spatial_V1.pdf`. Estructura: `Plantilla.pdf`."* Y el ADDENDUM del
19-jul (L879-889) hace de `Plantilla.pptx` la fuente de verdad de las cabeceras.

**Qué dijo Ernesto hoy**: *"el template que debemos considerar como válido es: Modelo
OncoMets Spatial V1 Deep-LLM-V"*.

**Verificado** (python-pptx, `sprints/B7_sprint7/`):

| | Plantilla.pptx | Deep-LLM-V.pptx |
|---|---|---|
| láminas | 30 | 19 |
| composición | 13 administrativas + 17 técnicas | **solo técnicas** + portada + lámina de título |
| cabecera técnica | s04-s18 | s02-s16 — **idéntica al píxel** |
| cabecera Environ | sí, 13 láminas | **no existe** |
| fuentes embebidas | 4 (Barlow, Barlow ExtraBold, Cambria Math, Consolas) | **2** (Barlow, Cambria Math) |

La cabecera técnica es literalmente la misma en los dos: mismos nombres de shape
(`Google Shape;115;p13`, `197;p29`, `198;p29`) y misma geometría (logo `0.750/0.437/
1.471×0.884`, título 25pt Barlow bold `3E6877`, línea a `1.421`). **Las geometrías
documentadas en [[plantilla-dos-cabeceras]] siguen siendo correctas** — no hay que
re-medir nada.

Lo que **sí** cambia: Deep-LLM-V no tiene cabecera Environ en ninguna lámina, así que la
regla "la Environ queda para agenda/recapitulación" no aplica a este template. La
recapitulación del B7 migró a cabecera OncoMets (era la última lámina con logo Environ en
la banda, y es exactamente lo que Ernesto reportó ver).

**Canonical**: CLAUDE.md §Formato de entregables, vía ADDENDUM aditivo. El ADDENDUM de la
mañana **no se reescribe** — sus geometrías valen y el hallazgo de las dos cabeceras de
Plantilla es real; se le encadena la aclaración de cuál archivo es el template.

## T2 — La causa raíz eran las fuentes embebidas

**Qué se creía** (sesión de la mañana, memoria [[plantilla-dos-cabeceras]] §Why): el deck
se veía fuera de template porque usaba la cabecera Environ en todas sus láminas.

**Qué se verificó hoy**: los templates **embeben sus fuentes** en el paquete
(`ppt/fonts/*.fntdata` + `<p:embeddedFontLst>` en `presentation.xml`). El generador
construía con `Presentation()` — el template default de python-pptx — que **no embebe
ninguna**. Barlow no está en el servidor (`fc-list | grep -ci barlow` → 0) ni
necesariamente en la máquina donde se presenta.

Consecuencia: PowerPoint **sustituye la tipografía** y el deck se ve fuera de template
**aunque el branding esté perfecto**. Explica por qué Ernesto seguía sin reconocerlo
después de la migración de cabeceras del commit `42280de`.

**No invalida la migración de la mañana** — las cabeceras estaban efectivamente mal y
había que arreglarlas. Es una **segunda causa, independiente y dominante**: la tipografía
afecta a las 22 láminas, la cabecera a unas pocas.

**Verificación** (round-trip, este es el método reusable): abrir el template con
python-pptx, borrarle todas las láminas, guardar → los 11 `.fntdata` y los 4
`embeddedFont` sobreviven. Construir **sobre el archivo** en vez de con `Presentation()`
hereda fuentes + theme + master.

**Canonical**: memoria nueva `deck-template-fuentes-embebidas` (es un gotcha durable y
generalizable a cualquier deck futuro, no específico del B7).

## T3 — El "How to apply" de la memoria quedó superseded

Dos ítems de [[plantilla-dos-cabeceras]] §How to apply ya no son lo implementado:

- *"Compactar la banda"* (1.17 → 0.785 `HDR`): hoy se usa la **banda literal** del
  template. El argumento de la mañana ("reescribir 20 layouts para ganar 0.28" es mal
  negocio") se resolvió sin reescribir nada: `reflow_onco()` baja el bloque de contenido y,
  cuando no entra, lo escala entero (~8%).
- *"Topar los títulos a 19 authored"*: sigue vigente como tope, pero el problema que
  resolvía (la 2ª línea cortada por la línea teal) hoy lo resuelve el **anclaje inferior**
  de la caja del título — los de una línea caen en la base del template y los de dos crecen
  hacia el aire de la banda.

**Acción**: ADDENDUM fechado en la memoria. No se reescribe el cuerpo — documenta una
decisión tomada con su argumento, y el argumento era válido con la información de esa hora.

## T4 — Pendiente "confirmar que Barlow está instalada": cerrado

El handoff `handoff_B7_20260719_1600.md` §7.2 lo listaba como *"la primera hipótesis a
descartar si vuelve a decir que no se ve como el template"*. **Ya no depende de la máquina
de Ernesto**: las fuentes viajan dentro del `.pptx`. Verificado en la salida: 5 `.fntdata`
+ `embeddedFontLst` con Barlow y Cambria Math.

Se cierra, **no se arrastra** al handoff nuevo ([[verificar-antes-de-pedir-dato]]).

## T5 — Carlito en los diagramas reusados (gotcha, sin acción)

Las láminas que copian diagramas de `papers/presentations/*.pptx` traen **354 referencias
a Carlito**, que es el clon métrico de Calibri de Linux y no existe en Windows. Degrada
limpio: PowerPoint sustituye por Calibri y, al ser métricamente compatible, **las cajas no
se rompen**.

**Sin acción deliberada**: remapear a Barlow cambiaría las métricas y podría desbordar
recuadros de diagramas ya revisados. Queda registrado por si alguna vez se quiere fidelidad
tipográfica total — sería un cambio aparte, con QA visual propio. Ernesto está informado.

---

## Fixes aplicados

| id | archivo | cambio |
|---|---|---|
| T1 | `CLAUDE.md` §Formato de entregables | ADDENDUM: cuál es el template válido y qué implica |
| T2 | `memory/deck-template-fuentes-embebidas.md` | memoria NUEVA + línea en `MEMORY.md` |
| T2,T3 | `memory/plantilla-dos-cabeceras.md` | ADDENDUM fechado (causa raíz + qué quedó superseded) |
| T4 | — | se cierra; no entra al handoff nuevo |
| T5 | este doc | registrado, sin acción |

Código: commit `170f7bd` (re-base del generador sobre el template válido).

---

# Sesión siguiente (19-jul, noche) — migración del CUERPO al template

Ernesto validó el deck en PowerPoint: el branding estaba. Pidió entonces revisar lámina por
lámina que se siguiera la arquitectura de Deep-LLM-V **y recrear los diagramas con ese
formato**. La auditoría encontró que la sesión anterior había migrado la **cabecera** pero
no el **cuerpo**.

## T6 — La paleta del cuerpo seguía siendo la de B4

`generate_b7_deck.py` conservaba el bloque `# paleta B4 (valores reales del deck)`. Medido
contra el template, el cuerpo usaba **diez colores que Deep-LLM-V no tiene**: `#217589`,
`#31859C`, `#DDEAEE`, `#F3F8F9`, `#B8D4D9`, `#1E2A2E` y una familia cálida completa
(`#E2723B`, `#B4521E`, `#FDEFE6`, `#FCE5CD`, `#FDF1E5`). Afectaba a 18 de 22 láminas.

**Fix**: se remapearon los **valores** de las constantes conservando sus **nombres** (los usa
`build()` en ~700 líneas). El deck quedó en cero fills fuera de paleta.

## T7 — La gramática de diagrama estaba invertida

Deep-LLM-V dibuja con cinco arquetipos, medidos sobre el template:

| rol | shape del template | forma | relleno | texto |
|---|---|---|---|---|
| proceso | `Google Shape;395` | rounded-rect | `#3E6877` | Barlow 12 **bold BLANCO** |
| dato | `Google Shape;391` | rect | `#B7B7B7` | Barlow 12 regular NEGRO |
| panel | `Google Shape;323` | rounded-rect | `#CDDFE1` | — |
| operador | `Google Shape;374` | óvalo | `#CDDFE1`, borde `#0E2841` | símbolo (+, ×) |
| conector | `Google Shape;399` | línea | `#386271` 2.37 pt | — |

Nuestras tiras `dim_pipeline` eran **bloques claros con texto teal**: el negativo exacto del
molde. Se invirtieron, y se añadieron los helpers `_proc` / `_dato` / `_grupo` / `_conn` para
que cualquier diagrama nuevo hable ese idioma sin re-medir el template.

## T8 — La lámina 6 no era recuperable por restyling (supersede T5)

"Dónde entra MAMMOTH en el pipeline" se traía de B4 con `copy_diagram_scaled()`: **96 runs en
Carlito** y **129 runs bajo 10 pt**, la mayoría a **6 pt**, contra un mínimo de 7 pt en el
template. No era un problema de color sino de legibilidad a escala de proyección, y subir la
tipografía habría desbordado las cajas — que es justo el riesgo que T5 había anticipado.

**Fix**: se reconstruyó **nativa** (`pipeline_mammoth()`), horizontal en vez de vertical
—como la lámina de flujo general del propio template— con los cinco arquetipos y tipografía
de 12/10 pt.

**Decisión editorial registrada**: se dejaron fuera los paneles de fórmulas del original. No
es pérdida de contenido: la lámina siguiente ya lleva esa matemática en una tabla nativa y
legible, y el trabajo de la 6 es **ubicar** el bloque en el pipeline. Se agregó en cambio la
forma del tensor antes y después de MAMMOTH — las dos dicen `[N, 512]`, que es la evidencia
visual de que es drop-in.

**Efecto colateral bueno**: las fórmulas del original eran el único OMML del deck. Al salir,
`Cambria Math` cae a cero y **desaparece el artefacto de LibreOffice** descrito en
[[pptx-qa-omml-libreoffice]] → el render rasterizado vuelve a ser confiable para QA.

## T9 — El recuadro del crop de contexto quedó en el naranja viejo

Al pasar el esquema nativo a teal, la foto de al lado seguía marcando el mismo campo en
naranja (lo dibuja `render_multiscale_crop.py` de B6 en `#E2723B`), y el pie decía "la caja
naranja". Una sola cosa con dos colores.

**Fix**: `recolor_crop_box.py` sustituye esos píxeles exactos (1552, un anillo limpio; el
recuadro se dibuja sin antialias) por `#3E6877`, en una **copia bajo `presentacion_b7/assets/`**
— el asset compartido de `assets_branding/` lo usa también el deck B6, que sigue en la paleta
vieja. El pie ya no nombra el color.

## Verificación final

| chequeo | resultado |
|---|---|
| láminas · tamaño | 22 · 13.333 × 7.5 |
| fills fuera de paleta | **ninguno** (eran 10 colores) |
| fuentes | Barlow 219 + Consolas 31 (paneles de código, deliberado) |
| Carlito | **0** (eran 96) |
| runs < 10 pt | **0** (eran 129) |
| fuentes embebidas | `fntdata: 5` · `['Barlow', 'Cambria Math']` — el re-base sobrevive |
| colisiones en las 20 técnicas | ninguna nueva |

Las 4 portadillas siguen sin cabecera OncoMets por diseño: es el pendiente abierto del logo
Environ, no una regresión.
