# Auditoría de coherencia — apertura "entendimiento + interpretabilidad MAMMOTH" (29-jun-2026)

> Mini-audit gatillada por la reunión del 29-jun con Benjamín/Sebastián/Fernando.
> Integra el feedback de Benjamín y el trabajo de entendimiento de MAMMOTH a la base
> de conocimiento, **sin contradecir** el cierre "0 palancas" de B5. Fronts tocados:
> **instrucciones** (CLAUDE.md, addendum), **memoria** (nueva feedback + update de
> próxima-dirección + addendum mammoth), **skills** (`@mammoth`, pointer).
> NO reabre el grueso B5 (`hallazgos.md`, `hallazgos_pathpt.md`, `hallazgos_diagrama_mammoth.md`).

## Resumen

| id | hallazgo | tipo | sev | acción |
|----|----------|------|-----|--------|
| M1 | La base dice "hilo mammoth CERRADO, 0 palancas"; Benjamín abre un eje ORTOGONAL (entender mecanismo + interpretabilidad + justificar hiperparámetros). No se contradicen. | reconciliation | media | ADDENDUM aditivo a Hallazgo 12 + nueva memoria; el veredicto "0 palancas" queda intacto |
| M2 | `[[magnificacion-cpathagent-proxima-direccion]]` da la próxima dirección como SOLO magnificación/CPathAgent; ahora coexiste con el eje entendimiento/interpretabilidad de Benjamín | stale (incompleto) | media | update aditivo de la memoria + cross-link |
| M3 | Feedback nuevo de Benjamín (explicar-a-14, qué significa cada cabeza, cuántas para mama, interpretabilidad, formato .ppt de las slides de objetivos) sin registrar | nuevo (feedback) | alta | nueva memoria `feedback-benjamin-entender-mammoth` + índice |
| M4 | `@mammoth` skill no apunta al material de entendimiento profundo (preguntas de Benjamín resueltas) | redundancy-gap | baja | pointer de 1 línea en SKILL.md (edición concisa) |
| M5 | Guion del deck usa "10 slots → 300"; paper principal §4 usa S=9 → 270 | reconciliation | baja | NO editar (10 = nuestro default, correcto); nota para que nadie lo "corrija" a 9 |
| **M6** | **Nuestro propio deck rotula las CABEZAS como "textura/forma/densidad"** (`convenciones_deck_b5.md:187`, panel `add_heads_panel`) → **contradice el paper** (cabezas = subespacios aprendidos, la morfología vive en los slots). **Es la raíz** de la respuesta equivocada de Ernesto en la reunión. | **error / contradicción** | **alta** | corregir el rótulo en convenciones (hecho, sin commitear) + memoria `[[diagramas-arquitectura-pptx-editable]]` (hecho); regenerar el panel del .pptx queda a Ernesto |

## Detalle

### M1 — "0 palancas" (cerrado) vs entendimiento/interpretabilidad (abierto) *(reconciliation)*
- **Qué dice la base**: CLAUDE.md Hallazgo 12 + ADDENDUM 19-jun: *"Cierra el hilo
  mammoth completo: 8 tareas drop-in + 4 keep_slots = 0 palancas."* Memorias
  [[mammoth-investigacion-integracion]] y [[equipo-arquitecturas-mammoth-longnet]] idem.
- **Qué abre Benjamín**: no cuestiona el rendimiento (sigue cerrado), sino el
  **entendimiento del mecanismo** y la **interpretabilidad** (qué miran los
  expertos/slots en mama, qué significa cada cabeza, cuántas para mama).
- **Cuál es correcto / cómo se reconcilia**: ambos. Son **ejes ortogonales** —
  *"¿mejora la métrica?"* (cerrado: no) vs *"¿qué aprende/mira por dentro y tiene
  sentido clínico?"* (abierto). Documentado en
  [`respuestas_preguntas_benjamin.md` §7](../mammoth_entendimiento/respuestas_preguntas_benjamin.md).
- **Fix**: **ADDENDUM aditivo** al final de Hallazgo 12 de CLAUDE.md (NO se toca el
  veredicto ni los números) + nueva memoria. Preserva el cierre y añade el eje nuevo.

### M2 — próxima dirección incompleta *(stale)*
- **Qué dice**: [[magnificacion-cpathagent-proxima-direccion]] → "post-B5 la próxima
  dirección es magnificación / CPathAgent (semana del ~29-jun)".
- **Por qué quedó incompleto**: sigue vigente, pero el 29-jun Benjamín añadió un eje
  paralelo (entender+interpretar mammoth) que la memoria no menciona.
- **Fix**: update aditivo — añadir el eje de Benjamín como segunda línea de trabajo
  post-B5, con cross-link a la nueva memoria. NO borrar lo de magnificación.

### M3 — feedback de Benjamín sin registrar *(nuevo)*
- Comentarios textuales en
  [`README.md` §2](../mammoth_entendimiento/README.md). Lo durable (preferencias de
  trabajo + el "explica como a un niño de 14" + "fuente tal cual del original") va a
  una **memoria `feedback`** nueva con su *Why* + *How to apply*.
- **Fix**: crear `feedback-benjamin-entender-mammoth.md` + línea en MEMORY.md.

### M4 — `@mammoth` sin pointer al entendimiento *(gap)*
- La skill cubre integración/corrida pero no el material que responde el mecanismo a
  fondo. **Fix**: **una línea** (edición concisa, [[edicion-concisa-agentes-skills]])
  apuntando a `sprints/B5_sprint5/mammoth_entendimiento/`.

### M5 — 10 slots (nuestro) vs 9 slots (paper) *(reconciliation, sin edición)*
- El guion y `MAMMOTH_DEFAULTS` usan `num_slots=10` (→ E·S=300). El paper §4
  (línea 436 del PDF) usa **S=9** (→ 270) en sus experimentos principales. **Ambos**
  caen en la banda recomendada (E∈24-96 → 200-400 slots totales, §5.3). **NO es
  error nuestro** — 10 es el default del README de la librería. **Acción: ninguna
  edición**; se documenta acá y en [respuestas §0] para que nadie "corrija" el guion
  a 9 pensando que está mal.

### M6 — el deck rotula las cabezas como "textura/forma/densidad" *(error / contradicción — el más importante)*
- **Qué dice cada fuente**:
  - **`convenciones_deck_b5.md:187`** (panel `add_heads_panel`): las CABEZAS = *"3
    criterios de ejemplo (textura/forma/densidad)"*. **← afirmación falsa.**
  - **Paper** (§3.1 + Fig 3) + [respuestas §Q1]: las cabezas son **subespacios
    multi-head APRENDIDOS**, sin semántica impuesta; la morfología reconocible (tumor,
    estroma, linfocitos…) vive en los **SLOTS/expertos**, NO en las cabezas.
  - Ecos **más suaves** (no nombran los features, menos dañinos): memoria
    `[[diagramas-arquitectura-pptx-editable]]` ("3 criterios") y
    `notas_presentador_guion.md:92` ("16 criterios en paralelo").
- **Cuál es correcto**: el paper. El rótulo del deck es un **error factual**.
- **Por qué importa (es la RAÍZ del incidente)**: Ernesto respondió "textura, forma,
  color" en la reunión **porque nuestro propio deck lo dice así**. Benjamín repreguntó
  si de verdad representan eso → la respuesta honesta es **no**. El deck nos llevó al error.
- **Fix aplicado**:
  - `convenciones_deck_b5.md:187` → reescrito a "lentes/subespacios ilustrativos, sin
    etiqueta semántica" + corrección explícita (**hecho; dejado SIN commitear** porque el
    archivo ya tenía cambios pendientes de otra sesión — Ernesto lo revisa y commitea).
  - memoria `[[diagramas-arquitectura-pptx-editable]]` → nota de corrección (hecho).
  - `notas_presentador_guion.md:92` ("16 criterios"): **no editado** (es metáfora, no
    nombra features falsos; el archivo está dirty). Recomendación: presentar "criterios"
    como "lentes/subespacios aprendidos", no como features con nombre.
  - **Regenerar el panel del .pptx** (etiquetas neutras o caption "ilustrativo, no
    asignaciones") **queda a Ernesto** (el deck es gitignored, lo controla él).

## Completitud — los 9 puntos de la reunión, mapeados a dónde quedan resueltos
(verificación de que NINGUNO quedó huérfano)

| # | Punto de Benjamín (reunión 29-jun) | Dónde queda | Estado |
|---|---|---|---|
| 1 | "No dominaba mammoth" / explicar a un niño de 14 | README §2.1, OBJ-D, [respuestas §2 analogía], feedback memory | ✅ |
| 2 | Formato (.ppt) de objetivos / "fuente tal cual" | README §2.2 + OBJ-E, feedback pt6 | ✅ (corregido: =tipografía) |
| 3 | Qué significa cada cabeza (¿textura/forma/color?) | [respuestas §Q1], feedback pt1, CLAUDE.md ADDENDUM, **+ M6** | ✅ |
| 4 | Cómo funcionan las cabezas + dims del vector S 30×16×10×16 | [respuestas §0 + §Q2], feedback pt2, CLAUDE.md ADDENDUM | ✅ |
| 5 | No narró las dimensiones del diagrama original paso a paso | [respuestas §0 tabla + §8], OBJ-C | ✅ |
| 6 | 3 cuadros de colores por experto + qué representa cada slot + operaciones/dims | [respuestas §Q3], README §5 (confirmar lectura con Benjamín) | ✅ (1 sub-punto a confirmar) |
| 7 | ¿Por qué MoE y no PoE? | [respuestas §Q4], feedback pt3, CLAUDE.md ADDENDUM | ✅ (marcado: paper no menciona PoE) |
| 8 | ¿Por qué 16 cabezas? ¿Cuántas para mama? | [respuestas §Q5], OBJ-B, feedback pt4, CLAUDE.md ADDENDUM | ✅ |
| 9 | Interpretabilidad de expertos/slots (en qué se fijan) | [respuestas §Q6], OBJ-A, feedback pt5, CLAUDE.md ADDENDUM | ✅ |

## Guardrails respetados
- En `main`, `git fetch` hecho. **Job mammoth ajeno corriendo (4529, sgaete)** → audit
  **documental, sin GPU, sin branch-switch que toque archivos versionados** (crear
  branch nuevo desde HEAD no modifica el árbol; workaround H respetado).
- Containment: solo bajo `oncomets-ernesto/` + memorias en `~/.claude/...`. Sin tocar
  `clam_environ/` ni `clam_testing/`. NO se commitea `papers/presentations/` (gitignored).
- Integridad de pre-registración: NO se reescribe ningún veredicto cerrado (M1/M5 son
  aditivos/sin-edición). El "0 palancas" queda como registro histórico intacto.
