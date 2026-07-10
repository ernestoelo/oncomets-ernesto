# Auditoría de coherencia — integración de registros 10-jul (magnificación / luz polarizada)

> Scope acotado (pedido de Ernesto): integrar coherentemente los 3 registros nuevos del 10-jul
> — investigación de magnificación para microcalc, hallazgo x40/x20 (magnif. física de cohortes),
> luz polarizada/oxalato Tipo I — sin auditoría full del espacio. Findings-doc-primero (skill).

## Resumen

| id | hallazgo | tipo | severidad | acción |
|---|---|---|---|---|
| F1 | CLAUDE.md §"Estructura de datos" dice "CONCH=512 para todas las slides" pero NO registra que las cohortes están a **distinta magnif. física a level0** (TCGA 40× / privado 20×), hecho validado con implicación de pipeline | stale/incompleto | media | nota **aditiva** en CLAUDE.md → puntero [[cohortes-magnificacion-fisica]] |
| F2 | `progress/current.md` lista "confirmar magnif. física de las cohortes" como **bloqueador (a) pendiente** — ya RESUELTO para TCGA/privado (HistAI pendiente) | stale (pendiente hecho) | media | actualizar current.md: bloqueador resuelto 2/3; doc de investigación cerrado |
| F3 | El eje magnificación no contradice el marco "cuello=datos, 0 palancas" | reconciliación | — | sin fix (ataca el DATO/contexto = la única señal nueva; consistente con [[insuficiencia-datos-ejes-investigacion]]) |
| F4 | Redundancia controlada del hallazgo x40/x20 (memoria canónica + doc §4 + ADDENDUM cpathagent) y de luz polarizada (doc + memoria + doc §2.1) | redundancia | baja | sin fix — canónico = memorias; los demás son punteros/detalle, no duplicación plana |
| F5 | ¿El eje magnificación merece un "Hallazgo N" en CLAUDE.md? | criterio | — | **NO** — los Hallazgos 11-14 son ejes CERRADOS; magnificación es eje ABIERTO (B6) → vive en current.md + sprint doc + memoria, no como Hallazgo |

## Detalle y verificación

**F1 (fix).** CLAUDE.md L284-311 describe las features CONCH sin nota de magnificación física. El hallazgo
(verificado con openslide, 10-jul: TCGA `mpp-x` 0.2325 ≈40×, privado 0.465 ≈20×, HistAI sin MPP) tiene
implicación durable: cualquier re-extracción o pirámide se define en **µm/px**, no en `level`, y el single-scale
actual mete un confound. Canónico = [[cohortes-magnificacion-fisica]]; CLAUDE.md solo lleva la **nota + puntero**
(no el detalle) — respeta "canonical vs reference".

**F2 (fix).** `current.md` §"Decisión de diseño pendiente" (bloqueador (a)) y §"Próximos pasos" item 2. El
bloqueador está resuelto para TCGA/privado; HistAI queda pendiente aparte (minoritario). Marcar como tal + linkear
el doc `magnificacion_microcalc/investigacion_magnificacion.md`.

**F3–F5 (sin fix).** Verificado que no hay contradicción con el marco cerrado ni Hallazgo forzado; la redundancia
es canónico+punteros (no plana). Memorias nuevas no duplican entre sí (una = magnif. física de cohortes; otra =
óptica/luz polarizada); ambas linkean a [[magnificacion-cpathagent-proxima-direccion]] como hilo padre.

## Fixes aplicados
- CLAUDE.md: nota aditiva en §"Estructura de datos" (F1).
- progress/current.md: bloqueador (a) marcado resuelto 2/3 + doc de investigación referenciado (F2).
- MEMORY.md: compactado (hook del sistema, 19.9→<17KB) — una línea por entrada, detalle en cada archivo.
