# Diseño — Memoria persistente versionada selectivamente

> Estado: **DISEÑO**. No se migra nada ni se crea infraestructura hasta
> que este doc se discuta y apruebe.
> Sprint: B4 / Sprint 4. Generado 2026-05-28 en sesión de auditoría de
> artefactos durables.

---

## 0. Contexto y motivación

Las memorias persistentes de Claude Code viven en
`~/.claude/projects/<hash-path>/memory/`, **segregadas por path del
proyecto**. Verificado el 28-may-2026 sobre el server Environ:

```
~/.claude/projects/
├── -media-administrador-Storage1                                  (otro hash)
├── -media-administrador-Storage1-dtapia                           (otro)
├── -media-administrador-Storage1-sdonoso                          (otro)
├── -media-administrador-Storage1-sdonoso-clam-environ             (otro)
├── -media-administrador-Storage1-sdonoso-clam-environ-extractor-... (otro)
├── -media-administrador-Storage1-sdonoso-clam-testing2            (otro)
└── -media-administrador-Storage1-sdonoso-clam-testing2-oncomets-ernesto  ← MÍO
```

**Implicación**: si Sebastián, jbarraza, scontrer o cualquier otro
operador abren Claude Code en otros paths del server, escriben memorias
**en otra carpeta hash**. Cero contaminación cruzada en lectura/escritura.
No hay urgencia operativa de versionar.

**Lo que sí justifica versionar selectivamente** (motivos a futuro, no
problemas actuales):

- **(a) Persistencia ante pérdida del home**: el server es compartido y
  el home `sdonoso` no es personal — un cambio de máquina o un wipe
  accidental borra todas las memorias. El repo (con remoto en GitHub) las
  preserva.
- **(b) Trazabilidad git log**: hoy una memoria nueva no deja huella en
  el historial — `git log` no la captura. Versionarlas permite ver
  "cuándo aprendimos qué" y por qué (commit message + diff).

Estos motivos NO aplican a todas las memorias. Las de tipo `feedback` /
`user` pueden incluir crítica personal o preferencias del equipo que no
corresponden ir a GitHub público.

---

## 1. Inventario actual (28-may-2026)

9 memorias totales, derivadas del frontmatter `metadata.type`:

| Slug | Tipo | Origen / sprint |
|---|---|---|
| `git-main-shared-pushes` | project | B4 / shared GPU + main account |
| `microcalc-dataset-decision` | project | B4 / reunión 22-may |
| `microcalc-hierarchical-proposal` | project | B4 / reunión 26-may |
| `microcalc-fusion-objetivo5` | project | B4 / Obj 5 + ANEXO |
| `equipo-arquitecturas-mammoth-longnet` | project | B4 / reunión 26-may |
| `surface-premise-discrepancies` | feedback | B4 / interacción general |
| `meta-regla-decisiones-revisitadas` | feedback | B4 / Obj 5 ANEXO (creada 28-may) |
| `patron-paired-comparison-reuso-splits` | feedback | B4 / Obj 5 ANEXO (creada 28-may) |
| `merge-criterio-contenido-vs-derivables` | feedback | B4 / Obj 5 cierre (creada 28-may) |

`MEMORY.md` es el índice (10 líneas, ~150 chars c/u), vive en el mismo
directorio que las memorias.

**No hay memorias tipo `reference` ni `user` actualmente.**

---

## 2. Qué versionar y qué no

### Versionar (5 actuales + futuras `project`/`reference`)

- **`project`** (5): decisiones del proyecto OncoMets, reuniones con
  Sebastián/Eduardo, estado de objetivos del sprint, mapeos de datasets.
  Información que **ya** convive con el repo (los `resultados.md` citan
  jobs y reuniones) — versionarla solo formaliza la persistencia.
- **`reference`** (0 actuales, futuras posibles): pointers a sistemas
  externos. Información factual sobre dónde buscar X — apto para
  versionar.

### No versionar (4 actuales + futuras `feedback`/`user`)

- **`feedback`** (4): meta-reglas sobre cómo Claude debe trabajar,
  correcciones del usuario, preferencias. Las 4 actuales son seguras de
  versionar (técnicas, no contienen crítica personal), pero el **tipo
  como regla** debe quedar fuera por preventivo: futuras feedback
  podrían capturar correcciones que mencionen a Sebastián/Benjamín por
  nombre con tono crítico, y eso no va a un repo público.
- **`user`** (0 actuales, futuras posibles): perfil del usuario, rol,
  conocimiento. Personal. Fuera.

### Criterio operativo

**Regla por tipo, no caso por caso.** Si una memoria `feedback` futura
es técnicamente segura, igual queda fuera — la regla es predecible y no
requiere juicio editorial en cada commit. Si en algún momento se quiere
versionar una `feedback` específica, **convertirla** a `reference` (con
pointer al doc del repo que la fundamenta) o a `project` (con argumento
clínico/arquitectónico). El tipo es la palanca.

---

## 3. Estructura propuesta — `.claude-memory/` en el repo

Espejo filtrado de `~/.claude/projects/.../memory/`:

```
oncomets-ernesto/
├── .claude-memory/              ← TRACKED en git
│   ├── README.md                ← explica qué es, qué hay, cómo se sync
│   ├── MEMORY.md                ← índice filtrado (solo project + reference)
│   ├── git-main-shared-pushes.md
│   ├── microcalc-dataset-decision.md
│   ├── microcalc-hierarchical-proposal.md
│   ├── microcalc-fusion-objetivo5.md
│   └── equipo-arquitecturas-mammoth-longnet.md
└── .gitignore                   ← excluye explícitamente .claude/projects/
                                   (ya está); .claude-memory/ NO ignorada
```

**Notas**:

- El nombre `.claude-memory/` evita colisión con `.claude/` (skills,
  agents, settings) — son cosas distintas.
- `MEMORY.md` en `.claude-memory/` es el **índice filtrado** (solo
  versionables). El `MEMORY.md` del home queda como índice **completo**
  (incluye también las `feedback`/`user`). Claude lee el del home (es la
  fuente primaria — ver §5).
- Cada `.md` versionado conserva su frontmatter original.

---

## 4. Script `sync-memory.sh` propuesto

### Dirección: **home → repo**, una sola vía

El home es la **fuente primaria** (Claude lee y escribe ahí). El repo es
**snapshot derivado** (read-only desde el sync; manual). No hay sync
inverso automático para evitar que un revert de git altere lo que Claude
está usando en vivo.

### Forma: script bash invocado manualmente

```bash
scripts/sync-memory.sh
```

**Qué hace**:

1. Para cada `.md` en `~/.claude/projects/-media-...-oncomets-ernesto/memory/`:
   - Lee frontmatter; si `type` ∈ {project, reference}, copia a
     `.claude-memory/<slug>.md`.
   - Si `type` ∈ {feedback, user}, **skip** (no toca).
2. Regenera `.claude-memory/MEMORY.md` filtrando el del home: solo
   líneas cuyo slug está en los versionables.
3. Reporta diff sin commitear: el usuario decide qué commit hace
   (mensaje, alcance).

**Frecuencia**: manual (no cron, no pre-commit hook). El usuario corre
`sync-memory.sh` cuando quiere snapshot — al cerrar un objetivo, antes
de una reunión, antes de un push importante. Forzar sync automático
genera churn de commits y mezcla cambios reales con sincronización.

**Conflictos**: si un archivo cambió en el home y en el repo (ej. una
sesión editó la memoria; otra persona/sesión editó el `.claude-memory/`
correspondiente), el script:

- Detecta divergencia (diff entre versión home y versión repo).
- **Para y reporta** — no sobre-escribe. El usuario decide cuál es la
  verdad (probablemente el home, ya que es la fuente primaria) y aplica
  manualmente.

### NO se crea hoy

El script es solo propuesta. Implementarlo requiere otro pase (lectura
de frontmatter en bash con awk/yq, manejo de slugs con caracteres
especiales, escritura idempotente). Si este diseño se aprueba, va a
sprint nuevo con hipótesis + casos de prueba.

---

## 5. Implicaciones para el harness (Claude Code)

**Claude lee del home, siempre.** Cuando una sesión arranca y se carga
`MEMORY.md` (vía el system prompt automático), lee
`~/.claude/projects/.../memory/MEMORY.md` — NO
`.claude-memory/MEMORY.md` del repo. Esto se mantiene.

**El repo es backup + trazabilidad, no fuente primaria.** El
`.claude-memory/` versionado existe para:

- Restaurar el home si se pierde (`cp -r .claude-memory/*.md
  ~/.claude/projects/.../memory/` + regenerar el `MEMORY.md` del home
  combinando con las no-versionables).
- Auditar `git log` / `git blame` sobre las memorias técnicas.
- Compartir con futuros operadores del repo (si en algún momento
  alguien más arranca Claude Code en este path desde otra máquina).

**No hay conflicto.** El home tiene 9 memorias; el repo tiene 5. Claude
sigue viendo las 9 desde el home. La diferencia es invisible en sesión.

---

## 6. Riesgos y recuperación

### R1: el script de sync rompe una memoria del repo

**Mitigación**: el script copia con `cp`, no edita. Si el frontmatter
parse falla, el archivo no se toca. Si el sync genera un commit malo,
`git revert <sha>` restaura el `.claude-memory/` previo sin afectar al
home (porque el home no se toca en la dirección home → repo).

### R2: el repo y el home divergen sin saberlo

**Mitigación**: el script reporta diff antes de copiar. El usuario ve
qué cambia. Si una memoria del repo está más nueva que la del home (no
debería pasar nunca, pero pasaría si alguien edita `.claude-memory/`
directamente), el script para.

### R3: una memoria con datos sensibles termina en el repo

**Mitigación principal**: filtro por tipo (las `feedback`/`user` que
podrían contener crítica no se copian nunca).
**Mitigación secundaria**: revisar el diff del sync antes de commitear.
Si una `project` accidentalmente contiene email/teléfono/PII, removerla
del repo y agregar al criterio editorial.

### R4: el repo se borra o el remoto se cae

**Mitigación**: el home sigue siendo la fuente primaria. El repo es
backup; perderlo no rompe Claude.

### R5: alguien edita `.claude-memory/<slug>.md` directamente y commitea

**Mitigación**: convención documentada en
`.claude-memory/README.md`: "este directorio es snapshot; editar las
memorias en `~/.claude/projects/.../memory/` y correr `sync-memory.sh`".
Si igual alguien edita directo, el próximo sync detecta divergencia y
para.

---

## 7. Decisión pendiente

- [ ] ¿Se aprueba el diseño general (sí/no/con cambios)?
- [ ] Si sí: ¿qué sprint implementa el script `sync-memory.sh` y la
  estructura `.claude-memory/`?
- [ ] Si sí: ¿`.claude-memory/README.md` lo escribimos en ese sprint o
  ahora como anexo de este doc?
- [ ] ¿Algún tipo `feedback` específico de las 4 actuales que vos
  consideres seguro y quieras versionar excepcionalmente (saltando la
  regla por tipo)?

NO migrar ni crear infraestructura hasta resolver estas decisiones.
