# Auditoría de coherencia — sesión DECK magnificación + gate (d) (12-jul-2026)

> Registra los avances y hallazgos de la sesión del 12-jul (viabilidad de lanzamiento B6 +
> extensión del deck con la sección magnificación para Sebastián) y propaga a las 4 frentes
> (CLAUDE.md, memorias, agentes/skills, sprint docs). Doc de hallazgos ANTES de los fixes
> (workflow `@knowledge-audit`). Branch: main (documental, GPU libre `squeue` vacío,
> `origin/main` sincronizado). Continúa `hallazgos_sesion_gates_10jul.md`.

## Resumen (id · hallazgo · tipo · acción)

| id | hallazgo | tipo | acción |
|---|---|---|---|
| S1 | **Gate (d) DECIDIDO: Ernesto eligió ESPERAR la co-firma de Sebastián (lunes) antes de lanzar** — NADA lanzado a GPU | progreso/decisión | actualizar `current.md` gate (d) + ADDENDUM memoria magnif |
| S2 | Git ya sincronizado (`origin/main`=`HEAD`=`ccea1da`); el "2 commits ahead" del handoff ya lo resolvió una sesión previa | stale (handoff, no en fronts) | sin acción en fronts; nota en findings |
| S3 | **Deck extendido 11→17 slides**: sección MAGNIFICACIÓN (12-17) para reunión Sebastián; nuevo `render_multiscale_crop.py` | proyecto/nuevo | documentado en `convenciones_deck_b6.md` §8 + `current.md` (hecho); memoria magnif |
| S4 | **Matiz de gobernanza:** gate NO bloqueante ≠ "siempre saltar" — Ernesto puede ELEGIR esperar cuando el costo de esperar es bajo y quiere co-firmar una decisión delegada | reconciliación | ADDENDUM `[[gobernanza-gate-cofirma-sebastian]]` |
| S5 | **Patrón nuevo:** imagen didáctica de patología desde WSI REAL (openslide read-only + coord de `.h5` existente) para slides — 2 escalas, mismo centro | contexto durable | memoria nueva `[[deck-imagen-didactica-wsi-real]]` + puntero en convenciones §8 |
| S6 | Agentes/skills sin cambios (no se tocó modelo/training; el `reviewer` ya aprobó el 10-jul) | OK | sin cambios |

## Detalle por hallazgo

### S1 — Gate (d): Ernesto decidió ESPERAR la co-firma del lunes
- **Contexto:** la sesión presentó (1) explicación pedagógica del experimento y (2) análisis de
  viabilidad de lanzar el fin de semana SIN la co-firma (b). Conclusión del análisis: **era viable**
  lanzar con el OK de Ernesto (la co-firma es gate NO bloqueante, [[gobernanza-gate-cofirma-sebastian]];
  Sebastián delegó la decisión de escala a Ernesto; pre-registro fechado; GPU libre).
- **Decisión de Ernesto:** **esperar al lunes** — presentar el pre-registro a Sebastián primero y
  lanzar después con su co-firma. Trade-off asumido conscientemente: se pierde el fin de semana de
  GPU a cambio de co-firmar una decisión delegada antes de gastar cómputo.
- **Estado:** NADA lanzado a GPU. Los 4 gates: (a) ✅, (c) ✅, (b) ⏳ lunes, (d) → **Ernesto optó por
  supeditarlo a (b)**. Todo el pipeline sigue armado y listo (stage-2 + stage-3 encadenable).
- **Fix:** `progress/current.md` paso 5 gate (d) + ADDENDUM en [[magnificacion-cpathagent-proxima-direccion]].

### S2 — Git ya sincronizado (el handoff estaba stale en ese punto)
- El handoff (`handoff_B6_lanzamiento_viabilidad_20260711.md`) decía "2 commits por delante de
  origin, hay que commitear+pushear". Verificado hoy: `origin/main`=`HEAD`=`ccea1da`; los 3 commits
  (`932c29f`, `dc356df`, `ccea1da`) **ya están pusheados**. Una sesión previa (o Ernesto) lo resolvió.
- **Acción:** ninguna sobre los fronts (el handoff es un doc point-in-time, no una frente viva; los
  fronts no afirman lo contrario). Registrado acá para trazabilidad.

### S3 — Deck extendido con la sección magnificación (avance principal)
- **Pedido de Ernesto:** anexar al deck `CLAM_Reunion_Mammoth.pptx` (el que usará con Sebastián) una
  sección con lo estudiado + referencias microcalc + imágenes didácticas + la **decisión de escalas**.
- **Hecho:** slides 12-17 (divisoria + 5 contenido), aditivo, sin tocar mammoth. Imagen didáctica =
  esquema nativo + crop REAL a 2 escalas. Helpers nuevos (`simple_table`, `panel`, `nested_fields`).
  QA LibreOffice 6/6 tras 2 pasadas de ajuste.
- **Canónico:** `convenciones_deck_b6.md` §8 (mapa + provenance) + `progress/current.md` (deck bullet).
  El `.pptx` y los crops son gitignored (`papers/presentations/`); tracked = `generate_b6_deck.py` (M,
  bundlea el WIP de mammoth ronda 2) + `render_multiscale_crop.py` (nuevo).

### S4 — Matiz de gobernanza (reconciliación, no contradicción)
- [[gobernanza-gate-cofirma-sebastian]] dice que Ernesto **asume** el gate no bloqueante y procede sin
  Sebastián. Hoy hizo lo contrario (esperar). **No es contradicción:** el gate no bloqueante da la
  OPCIÓN de proceder, no la obligación. La lección durable: cuando el **costo de esperar es bajo** (un
  fin de semana de GPU, sin urgencia) y la decisión fue **delegada** por Sebastián (querés su input
  para acertar), esperar la co-firma es legítimo y prudente. Futuras sesiones NO deben asumir
  "no bloqueante → lanzar siempre".
- **Fix:** ADDENDUM conciso a la memoria.

### S5 — Patrón nuevo: imagen didáctica desde WSI real (read-only)
- Para la slide de escalas se renderizó un crop REAL de mama (TCGA-BRCA) a 2 campos físicos (112µm y
  512µm, mismo centro) con `render_multiscale_crop.py`: openslide **read-only** en CPU, reusa una
  coord de tejido de un `.h5` de parches existente (garantiza tejido, no fondo), reescala a display,
  dibuja la caja del campo fino dentro del contexto. Reproducible (`--coord-idx`). Reusable para
  cualquier deck que necesite ilustrar magnificación/campo de visión con tejido real.
- **Fix:** memoria nueva concisa + puntero desde `convenciones_deck_b6.md` §8 (ya menciona el script).

### S6 — Agentes / skills
- No se tocó modelo/training/data-pipeline en esta sesión → `reviewer` no se re-invocó (ya aprobó el
  pre-registro el 10-jul, gate a). `trainer` no se usó (sin GPU). Skills sin cambios.

## Guardarraíles respetados
- Read-only sobre `clam_environ/` (openslide solo lectura del WSI) y `clam_testing/`; escritura solo
  bajo `clam_testing2/` y memorias en `~/.claude/`.
- Sin GPU (render en CPU); sin tocar jobs (`squeue` vacío); sin `sbatch` (gate d no dado para lanzar).
- Deck: todo nativo salvo el crop real (imagen); notas del presentador = guion hablado en prosa.
- Ediciones a memorias = ADDENDUM aditivo (no reescriben pre-registro ni reglas duras).
