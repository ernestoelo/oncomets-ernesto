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
