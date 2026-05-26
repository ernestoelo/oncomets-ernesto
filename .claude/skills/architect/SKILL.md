---
name: architect
description: Use when the user asks to "create a skill", "scaffold a skill", "validate a skill", mentions "SKILL.md", "skill structure", or discusses skill architecture and plugin development.
---

# Architect

Scaffolds, validates, and maintains skills for Claude Code plugins. This is the meta-skill that creates and refines all other skills.

## When This Skill Applies

- Creating a new skill from scratch
- Reviewing or improving an existing skill's structure
- Validating SKILL.md frontmatter and content quality
- Packaging or reorganizing skills
- Understanding skill anatomy and best practices

## Skill Anatomy

Every skill is a folder inside `skills/` with this structure:

```
skill-name/
├── SKILL.md              (required — metadata + instructions)
├── scripts/              (optional — executable code)
├── references/           (optional — docs loaded on demand)
└── assets/               (optional — templates, images, fonts)
```

**Do NOT create** README.md, CHANGELOG.md, or auxiliary documentation. SKILL.md is the single source of truth. See [references/skill-creator.md](references/skill-creator.md) for the full rationale.

## Creating a New Skill

### Step 1: Understand the domain

Gather concrete examples of what the user wants. Ask: what triggers this skill? What inputs/outputs does it produce? What decisions depend on context vs must be deterministic?

### Step 2: Plan resources

Decide what goes where:

| Resource | When to use |
|---|---|
| **SKILL.md body** | Core workflow, decision trees, essential instructions (<500 lines) |
| **scripts/** | Code that needs deterministic reliability or is rewritten repeatedly |
| **references/** | Detailed docs Claude reads on demand (schemas, API specs, policies) |
| **assets/** | Files used in output (templates, images, boilerplate) |

### Step 3: Scaffold

Run the scaffold script to generate the standard structure:

```bash
python scripts/skill_scaffold.py <skill-name> "<description>"
```

Or create manually — the scaffold is a convenience, not a requirement.

### Step 4: Write the SKILL.md

The most critical file. Follow these rules:

**Frontmatter:**
```yaml
---
name: skill-name
description: This skill should be used when the user asks to "specific phrase", "another phrase", mentions "keyword", or discusses topic-area. Provides [what it does].
---
```

- `description` determines when Claude activates the skill. Include explicit trigger phrases in quotes and topic keywords.
- Be comprehensive but concise — descriptions longer than 250 characters are truncated in the skill listing.
- Only `name` and `description` are required. All other fields are optional.

**Additional frontmatter fields** (use only when needed):

| Field | Purpose |
|---|---|
| `disable-model-invocation` | `true` to prevent Claude auto-loading (manual `/name` only) |
| `user-invocable` | `false` to hide from `/` menu (background knowledge only) |
| `allowed-tools` | Pre-approve tools without per-use prompts (e.g. `Bash(git *)`) |
| `context` | `fork` to run in an isolated subagent |
| `agent` | Subagent type when `context: fork` (e.g. `Explore`, `Plan`) |
| `model` | Model override for this skill |
| `effort` | Effort level: `low`, `medium`, `high`, `max` |
| `hooks` | Hooks scoped to this skill's lifecycle |
| `paths` | Glob patterns to limit when skill activates |
| `argument-hint` | Hint for autocomplete (e.g. `[filename] [format]`) |
| `shell` | `bash` (default) or `powershell` |

**String substitutions** available in skill content:

| Variable | Description |
|---|---|
| `$ARGUMENTS` | All arguments passed when invoking the skill |
| `$ARGUMENTS[N]` or `$N` | Access specific argument by 0-based index |
| `${CLAUDE_SESSION_ID}` | Current session ID |
| `${CLAUDE_SKILL_DIR}` | Directory containing the skill's SKILL.md |

**Dynamic context injection** — run shell commands before content is sent to Claude:

```markdown
## Current state
- Branch: !`git branch --show-current`
- Status: !`git status --short`
```

**Body guidelines:**
- Lead with a one-line summary of what the skill does
- Include "When This Skill Applies" section with bullet points
- Prefer concise examples over verbose explanations
- Keep under 500 lines — split to references/ if approaching this limit
- Reference bundled resources with relative paths and explain when to read them
- Write in English for consistency

### Step 5: Validate

Run the validator to check frontmatter and structure:

```bash
python scripts/quick_validate.py <path/to/skill>
```

### Step 6: Iterate

Test the skill in a real conversation, refine triggers in the description, and update based on activation patterns.

### Step 7: Encode crash guardrails (for system/runtime skills)

If the skill edits compositor, shell, services, or driver/runtime behavior, add a short **Safety/Crash Guardrails** subsection in `SKILL.md`:

- List known crash vectors discovered in real sessions.
- Provide explicit "do not use" patterns (e.g., unsafe reload/force-refresh paths).
- Define the stable control path (single source of truth for toggle state).
- Include rollback/recovery commands (TTY-safe when applicable).

This prevents reintroducing regressions when future sessions or agents "optimize" working logic.

## Progressive Disclosure

Skills use three-level context loading:

1. **Metadata** (~100 words) — Always loaded. Name + description determine activation.
2. **SKILL.md body** (<5k words) — Loaded when skill triggers.
3. **Bundled resources** (unlimited) — Loaded on demand by Claude.

This means: keep SKILL.md lean. Move variant-specific details, large examples, and reference material into `references/`. See [references/skill-creator.md](references/skill-creator.md) for patterns.

**Skill content lifecycle:** Once invoked, skill content stays in the conversation for the session. During auto-compaction, Claude Code re-attaches the most recent invocation (first 5,000 tokens each, 25,000 combined budget). Write guidance as standing instructions, not one-time steps.

## Degrees of Freedom

Match instruction specificity to task fragility:

- **High freedom** (text guidance): Multiple valid approaches, context-dependent decisions
- **Medium freedom** (pseudocode/parameterized scripts): Preferred pattern exists, some variation ok
- **Low freedom** (specific scripts): Operations are fragile, consistency is critical

## Skill vs subagente — when to use which

Both live as `.md` files with YAML frontmatter, but solve different problems:

| | **Skill** (`~/.claude/skills/<name>/`) | **Subagent** (`<project>/.claude/agents/<name>.md`) |
|---|---|---|
| **Trigger** | Auto-loads when Claude detects a match in `description`. | Invoked explicitly via `Agent` tool with `subagent_type`. |
| **Scope** | Global — available across all projects. | Project-local — fixed role within one repo. |
| **Context** | Lives in main conversation; can spawn subagents. | Runs with isolated context (no chat history). |
| **Use case** | Procedure or reference (how to compile LaTeX, validate skills, scaffold a harness). | Role with hard prohibitions (leader can't edit code; reviewer can't fix). |
| **Lifecycle** | Persists across sessions. | Active only during one delegation. |

**Rule of thumb**: if the user could invoke it with `@<name>` in any project, it's a skill. If it's a fixed role within one project's workflow (leader/implementer/reviewer of a harness), it's a subagent.

For multi-agent orchestration patterns (when to combine subagents into a leader/implementer/reviewer team), see [references/subagent-patterns.md](references/subagent-patterns.md). The `@harness` skill scaffolds this exact pattern in a project.

## References

- [references/skill-creator.md](references/skill-creator.md) — Core principles, anatomy details, and what NOT to include
- [references/workflows.md](references/workflows.md) — Sequential and conditional workflow patterns
- [references/output-patterns.md](references/output-patterns.md) — Template patterns for consistent output
- [references/subagent-patterns.md](references/subagent-patterns.md) — Subagent file structure and orchestration patterns
