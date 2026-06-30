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

## Guardrails respetados
- En `main`, `git fetch` hecho. **Job mammoth ajeno corriendo (4529, sgaete)** → audit
  **documental, sin GPU, sin branch-switch que toque archivos versionados** (crear
  branch nuevo desde HEAD no modifica el árbol; workaround H respetado).
- Containment: solo bajo `oncomets-ernesto/` + memorias en `~/.claude/...`. Sin tocar
  `clam_environ/` ni `clam_testing/`. NO se commitea `papers/presentations/` (gitignored).
- Integridad de pre-registración: NO se reescribe ningún veredicto cerrado (M1/M5 son
  aditivos/sin-edición). El "0 palancas" queda como registro histórico intacto.
