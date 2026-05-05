---
name: harness
description: Use when the user asks to "scaffold a harness", "set up subagent orchestration", mentions "feature_list.json", "leader/implementer/reviewer", "AGENTS.md", or starts a code project needing multi-agent orchestration with checkpoints and progress logs.
---

# Harness — Orquestación multi-agente con checkpoints

Esta skill arma en un proyecto el patrón **harness**: un wrapper ejecutable de
buenas prácticas alrededor de subagentes (`leader` → `implementer` → `reviewer`),
con bitácora persistente, checkpoints objetivos y hooks que verifican
automáticamente. Inspirado en
`hyprland-rice/ejemplo-harness-subagentes-main/`, pero adaptado a múltiples
runtimes (Python, Node, Rust, Go).

## Cuándo SÍ aplica

| Situación                                              | ¿Aplicar? |
|--------------------------------------------------------|-----------|
| Proyecto de código nuevo con ≥3 features identificables | ✅ |
| Refactor grande con múltiples capas (modo `--retrofit`) | ✅ |
| Sesión sysadmin / one-shot Hyprland / debugging        | ❌ usa skills directas |
| Documento LaTeX / análisis exploratorio de datos       | ❌ |
| Crear una skill nueva                                  | ❌ usa `@architect` |

## Skills relacionadas (no duplicar)

- **`@architect`** — fuente canónica de cómo se ve un `.md` con frontmatter en
  `.claude/agents/`. Esta skill reusa `architect/scripts/skill_scaffold.py` y
  `architect/scripts/quick_validate.py`.
- **`@dev-workflow`** — init de proyecto (uv, Gitflow). Correr ANTES de
  `@harness` cuando el proyecto es Python AI/ML.
- **`@sys-env`** — validar entorno (Arch, conda) ANTES de scaffoldar.

Orden recomendado: `@sys-env` → `@dev-workflow` → `@harness` → contenido.

## Anatomía del harness scaffolded

```
proyecto/
├── AGENTS.md                  # Mapa de navegación con divulgación progresiva
├── CHECKPOINTS.md             # 5 niveles objetivos (C1-C5) con checkboxes
├── feature_list.json          # Cola declarativa de tareas con acceptance
├── init.sh                    # Gate de sanidad: deps + tests + estado
├── progress/
│   ├── current.md             # Sesión activa, en tiempo real
│   └── history.md             # Append-only, una entrada por sesión
├── docs/
│   ├── architecture.md        # Capas, principios, prohibiciones
│   ├── conventions.md         # Estilo, naming, patrones de error
│   └── verification.md        # Cómo testear (anti-patrones)
├── .claude/
│   ├── settings.json          # Hooks PostToolUse + Stop por runtime
│   └── agents/
│       ├── leader.md          # Orquesta — NUNCA edita código
│       ├── implementer.md     # Una feature, escribe en disco
│       └── reviewer.md        # Valida contra CHECKPOINTS — no arregla
└── CLAUDE.md                  # Fija el rol "leader" desde la primera sesión
```

## Workflow de scaffolding

### 1. Pre-requisitos

Ya hay un proyecto base inicializado (por `@dev-workflow` o manual). Estás
dentro de su raíz.

### 2. Decidir runtime

El script detecta o pregunta:

- `python` (default si hay `pyproject.toml` / `requirements.txt`)
- `node` (si hay `package.json`)
- `rust` (si hay `Cargo.toml`)
- `go` (si hay `go.mod`)
- `none` (sin runner — `init.sh` solo valida estructura)

Decide los hooks de `.claude/settings.json` y el cuerpo de `init.sh`.

### 3. Scaffold

```bash
python3 ~/.claude/skills/harness/scripts/scaffold_harness.py \
    --runtime python \
    --features feature_a,feature_b,feature_c
```

Genera todos los archivos desde `assets/templates/*`. No sobreescribe si ya
existen — pide confirmación archivo a archivo.

### 4. Validar

```bash
bash ~/.claude/skills/harness/scripts/validate_harness.sh .
```

Recorre los 5 checkpoints (C1-C5) y reporta `OK` o lista huecos.

### 5. Primera sesión

```bash
./init.sh         # Debe terminar con exit 0
claude            # Claude lee CLAUDE.md → asume rol leader
```

Claude lanza `implementer` (vía Agent tool con definición en
`.claude/agents/implementer.md`) por cada feature `pending` de menor `id`, y
luego `reviewer` antes de marcar `done`.

## Principios no negociables

1. **Una feature en `in_progress` a la vez.** `init.sh` lo valida.
2. **Subagentes escriben en disco**, no en chat (`progress/explore_*.md`,
   `impl_*.md`, `review_*.md`). Devuelven solo la referencia.
3. **`done` solo lo marca el implementer tras revisión aprobada.**
4. **Hooks ejecutan tests automáticamente** — el agente no decide saltárselos.
5. **`progress/current.md` se actualiza en tiempo real**, no al final.

Detalle por principio en
[references/design-principles.md](references/design-principles.md).

## Recursos incluidos

| Recurso | Propósito |
|---|---|
| `scripts/scaffold_harness.py` | Genera todo el harness desde templates. |
| `scripts/validate_harness.sh` | Recorre C1-C5 y reporta huecos. |
| `scripts/render_init_template.py` | Personaliza `init.sh` por runtime. |
| `references/design-principles.md` | Los 8 principios destilados. |
| `references/role-separation.md` | Plantillas leader/implementer/reviewer. |
| `references/checkpoints-rationale.md` | Por qué 5 niveles, cómo extender. |
| `references/anti-telephone-pattern.md` | Prompts que fuerzan escritura a disco. |
| `references/hooks-cookbook.md` | Hooks por runtime (Python, Node, Rust, Go). |
| `assets/templates/*` | Todos los `.tmpl` del scaffold. |

## Anti-patrones

- **No** scaffoldar en sesiones sysadmin / one-shots — el harness asume ciclo
  multi-feature.
- **No** sobreescribir un proyecto existente sin `--retrofit` (dry-run con
  confirmación archivo a archivo).
- **No** copiar hooks de un runtime a otro — usa
  `references/hooks-cookbook.md`.
- **No** hardcodear paths `/home/<user>` en templates — todo con `~/` o
  `$HOME`. Esta skill vive bajo el repo dotfiles personal y debe respetar §1
  de su `CLAUDE.md`.
