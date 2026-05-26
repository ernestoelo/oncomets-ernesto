# Subagent patterns

Reference for subagent files (`.claude/agents/<name>.md`) and orchestration
patterns. Companion to the `@harness` skill, which scaffolds these in a
project.

## File anatomy

```yaml
---
name: <id>                     # required, lowercase, no spaces
description: <one-line summary> # required, drives auto-invocation
tools: <comma-separated list>  # optional, restricts the subagent's toolbox
model: <opus|sonnet|haiku>     # optional, override
---

# Subagent body in Markdown.
# Sections typically: Protocolo, Reglas, Anti-patrones, Output format.
```

Validate with `python3 ~/.claude/skills/architect/scripts/quick_validate.py
<path>` — same validator as for skills, since the frontmatter rules match.

## The 3-role pattern (leader / implementer / reviewer)

The canonical multi-agent pattern. Each role has hard prohibitions to prevent
overlapping authority.

| Role           | Edits code | Marks `done` | Decides what to do | Validates |
|----------------|------------|--------------|--------------------|-----------|
| `leader`       | ❌         | ❌           | ✅                 | ❌        |
| `implementer`  | ✅         | ❌¹          | ❌                 | ❌        |
| `reviewer`     | ❌         | ❌           | ❌                 | ✅        |

¹ Only after the reviewer approves and only in a later session.

**Why prohibitions matter**: when one agent decides-implements-validates, biases
accumulate. Separation forces asynchronous communication via files on disk and
independent verification.

## Anti-telephone pattern

Subagents **write to disk** (`progress/explore_<topic>.md`,
`progress/impl_<feature>.md`, `progress/review_<feature>.md`) and return only
the reference: `done -> progress/<file>.md`.

The leader never sees the content in chat — reads the file when needed, with
exact citation. This survives context window compaction.

Templates for these prompts live in
`~/.claude/skills/harness/references/anti-telephone-pattern.md`.

## Tools allowlist by role

| Role         | Recommended `tools:` |
|--------------|----------------------|
| leader       | `Read, Glob, Grep, Bash, Agent` |
| implementer  | `Read, Glob, Grep, Bash, Edit, Write` |
| reviewer     | `Read, Glob, Grep, Bash` |
| explorer     | (use built-in `Explore`, no custom file needed) |

Giving the reviewer `Edit` collapses the role separation — it would start
fixing instead of dictating. Resist.

## Common mistakes

- **`description` too generic** ("helps with code"). Auto-invocation needs
  specific trigger phrases.
- **Including chat-history assumptions**: subagents don't see the main
  conversation. Pass context in the prompt.
- **Missing prohibitions**: roles drift without explicit `❌ NUNCA edites X`.
- **No output format**: subagent returns prose. Specify the exact one-line
  response (`done -> <file>` or `blocked -> <file>`).

## Where the patterns live

- **Templates**: `~/.claude/skills/harness/assets/templates/.claude/agents/*.tmpl`
  — copy these and customize.
- **Customization guide**: `~/.claude/skills/harness/references/role-separation.md`
  — when to add/remove fields, how to extend the role table.
- **Hooks integration**: `~/.claude/skills/harness/references/hooks-cookbook.md`
  — wire subagent output to PostToolUse hooks for automatic verification.
