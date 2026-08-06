---
name: knowledge-audit
description: Audita la coherencia de la base de conocimiento (CLAUDE.md, memorias, agentes, skills) — contradicciones, stale, redundancias, enlaces rotos. Triggers — knowledge audit, auditar el conocimiento/espacio, depurar contradicciones, revisar memoria.
---

# Knowledge Audit

Audits the four "fronts" of the repo's documented knowledge for contradictions,
stale/incorrect info, and redundancy — then depurates errors with criteria that
preserve unique content and pre-registration integrity. **Findings doc first,
fixes second.**

## When This Skill Applies

- The user asks to audit/clean the repo's instructions, memory, agents, or skills.
- A handoff or sprint-open asks to leave the space coherent before new work.
- You notice CLAUDE.md has grown and accumulated possibly-contradictory rules.
- A decision was made that must be **propagated** across many docs (rules, memories, slurm headers).
- After a team/scope change (someone left, dataset rule changed) that makes roster/facts stale.

## The four fronts of "the space"

1. **Instrucciones** — `CLAUDE.md` (control center; durable rules + validated facts).
2. **Memoria** — `~/.claude/projects/<hash-path>/memory/*.md` + `MEMORY.md` (index).
   Path for THIS repo: `/home/sdonoso/.claude/projects/-media-administrador-Storage1-sdonoso-clam-testing2-oncomets-ernesto/memory/`.
3. **Agentes** — `.claude/agents/*.md` (`trainer`, `reviewer`).
4. **Skills** — `.claude/skills/*/SKILL.md` (validate structure with `/architect`).

## Workflow (read-only → findings doc → fixes → commit)

### 1. Setup
- `git branch --show-current`. A documental-only audit (no model/training edits) may
  stay on `main` (Ernesto's default, [[git-trabajar-en-main-por-defecto]]); create a NEW
  branch `chore/audit-coherencia-<sprint>` only if the audit will carry changes into
  model/training code (regla 9). **With a GPU job running, do NOT branch — workaround H
  forbids branch-switching while a job reads the shared tree; stay on `main` and touch
  only files the job does not read.**
- `git fetch` (main is shared, multiple authors — [[git-main-shared-pushes]]).
- **Do NOT touch running GPU jobs** (`squeue` first): neither cancel them **nor**
  `git checkout`/merge that changes tracked files while one runs — the job reads its
  inputs from the live **shared** working-tree and you crash it (job 4241 died this
  way; CLAUDE.md workaround H, [[working-tree-compartido-job-en-curso]]). The audit is
  documental; do branch-switch/merge/cleanup only with the GPU free.
- Note `python` is broken at base PATH → use the env binary
  `/home/sdonoso/miniconda3/envs/clam_latest/bin/python` for any script.

### 2. Read phase (read-only, evidence with exact `file:line`)
- Cross-read the four fronts. For each candidate issue record: what each source
  says, which is correct, and where it should live.
- Use `grep -n` to locate every occurrence of a fact being propagated (e.g. a
  retired threshold) — a decision usually lives in 3-6 places.
  **Barrer el repo ENTERO (`grep -rn --include="*.md"`) + el directorio de memorias, no
  los frentes donde uno recuerda haberla escrito**, y buscar primero el documento que
  **originó** la frase: ahí está enunciada con más fuerza y sin las salvedades que los
  demás le agregaron al citarla. Caso: H1 de la octava pasada del B8 corrigió 5 lugares y
  dejó afuera el `resultados.md` de origen y una segunda memoria
  (`auditoria_coherencia/hallazgos.md`, decimosexta pasada).
- For skills: confirm each has `SKILL.md` with valid `name`/`description`
  frontmatter; run `/architect`'s `quick_validate.py` if structure is in doubt.

### 3. Produce the findings doc FIRST
Write `sprints/<sprint>/auditoria_coherencia/hallazgos.md` **before editing**:
a summary table (id · finding · severity · action) plus, per finding, what each
source says, which is canonical, and the planned fix. This is the deliverable the
user reviews; do not skip straight to edits.

### 4. Apply fixes — criteria (the hard-won rules)
- **Canonical vs reference.** CLAUDE.md = durable rules/facts; memories = atomic
  facts; sprint docs = detail/history. Redundancy = same fact in 2+ places → keep
  ONE canonical, the others point to it (`[[memory-name]]` / file path).
- **Never delete unique content.** If a fact lives in only one place, it MOVES,
  it is not deleted. Before condensing anything away, **verify the piece is
  preserved in its canonical home** (open the memory and confirm). Redundancy ≠
  unique-content-in-the-wrong-place.
- **Preserve pre-registration integrity.** Never rewrite a pre-registered
  hypothesis (regla 9) retroactively — that destroys its value. Add a dated
  **ADDENDUM** instead; the original numbers stay as historical record.
- **Edit hard rules additively.** For non-negotiable rules (regla 9, containment,
  read-only), add a clarifying sub-clause (e.g. `9.a`), do not rewrite the
  meaning. Touch with care.
- **Preserve cross-references.** Keep numbered references resolvable (if "ver
  Hallazgo 10" points at a section, keep that section's number/semantics) and
  `[[wikilinks]]` valid. Check both internal and external (a memory citing
  "Hallazgo 10 de CLAUDE.md").
- **Concise edits to agents/skills.** Agent/skill files are loaded as operational
  context — add a one-line clause + pointer to the canonical source, NOT a verbose
  paragraph ([[edicion-concisa-agentes-skills]]).
- **Surface, don't assume.** If a premise in the prompt clashes with what the repo
  actually says, stop and surface it with evidence ([[surface-premise-discrepancies]]).

### 5. Finding taxonomy
- **stale** — info contradicted by a newer source (roster, "pendiente" already done).
- **contradiction** — two live sources disagree; pick the correct one, reconcile wording.
- **redundancy** — same fact in 2+ places; condense to canonical + pointers.
- **reconciliation** — two things look contradictory but aren't (e.g. "AUC solo
  nunca" vs "reportar AUC siempre" → reconcile: the veto is to AUC *isolated*).
- **error** — a plain factual mistake; fix and cite the source of truth.

### 6. Commit / memory hygiene
- Commit granularly per theme (`docs(audit-<sprint>): ...`), local identity
  (`ernesto.gamero@sansano.usm.cl`), branch confirmed first.
- Update `MEMORY.md` index lines for any memory you changed; **delete memories
  that turned out wrong**; add a new `feedback` memory for any working preference
  the user revealed during the audit.
- Mark resolved tensions as RESOLVED in the relevant memory/index.

## Guardrails
- **Containment**: write only under `clam_testing2/oncomets-ernesto/` (memories
  under `~/.claude/...` are the known exception). Never touch `clam_environ/`
  (read-only) or `clam_testing/`.
- **Do NOT commit** `results/` (job outputs), handoffs, or `papers/presentations/` (gitignored).
- **Do NOT cancel or disturb** a running SLURM job; the audit never uses GPU.
- **Push/merge to main** only when the session prompt authorizes it explicitly
  (default = local commits, Ernesto pushes). When authorized: `git fetch` first,
  **never `--force`**, integrate if `origin/main` advanced, merge `--no-ff` to
  preserve the branch's semantic line. Branch cleanup at sprint close or per
  explicit instruction ([[repo-limpieza-branches-cierre-sprint]]).

## Worked example (use as the reference of "good")
B5 audit, branch `chore/audit-coherencia-b5`,
`sprints/B5_sprint5/auditoria_coherencia/hallazgos.md`: 7 findings (stale roster,
stale memory, threshold propagation via addendum, AUC-reconciliation, regla 9.a
sub-clause, redundancy condensation of Hallazgos 9/10/11 verified against
canonical memories, skills OK). That doc + this skill's criteria are the template.