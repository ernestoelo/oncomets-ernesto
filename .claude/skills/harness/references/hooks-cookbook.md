# Hooks por runtime

Recetas de `.claude/settings.json` listas para copiar. El
`scaffold_harness.py` ya rellena estos valores automáticamente vía
`render_init_template.py`; este archivo es la fuente de verdad si necesitas
ajustarlos a mano.

## Estructura común

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [{ "type": "command", "command": "<TEST_QUICK>" }]
      }
    ],
    "Stop": [
      {
        "hooks": [{ "type": "command", "command": "./init.sh > /tmp/harness_init.log 2>&1 && echo '[harness] OK' || (echo '[harness] FAIL' && tail -20 /tmp/harness_init.log)" }]
      }
    ]
  },
  "permissions": {
    "allow": [/* lista por runtime */]
  }
}
```

## Python (default)

```json
"PostToolUse": "python3 -m unittest discover -s tests -q 2>&1 | tail -3"
"permissions.allow": [
  "Bash(./init.sh)",
  "Bash(python3 -m unittest*)",
  "Bash(python3 -m src*)"
]
```

Si usas `pytest`:

```json
"PostToolUse": "pytest -q 2>&1 | tail -5"
"permissions.allow": [
  "Bash(./init.sh)",
  "Bash(pytest*)",
  "Bash(python3 -m src*)"
]
```

## Node / TypeScript

```json
"PostToolUse": "npm test --silent 2>&1 | tail -5"
"permissions.allow": [
  "Bash(./init.sh)",
  "Bash(npm test*)",
  "Bash(npm start*)",
  "Bash(npm run*)"
]
```

Si usas `pnpm` / `yarn`, sustituye `npm` en ambos.

## Rust

```json
"PostToolUse": "cargo test --quiet 2>&1 | tail -5"
"permissions.allow": [
  "Bash(./init.sh)",
  "Bash(cargo test*)",
  "Bash(cargo run*)",
  "Bash(cargo build*)"
]
```

## Go

```json
"PostToolUse": "go test ./... 2>&1 | tail -5"
"permissions.allow": [
  "Bash(./init.sh)",
  "Bash(go test*)",
  "Bash(go run*)",
  "Bash(go build*)"
]
```

## Ninguno (`runtime: none`)

Solo el hook `Stop` validando estructura:

```json
"PostToolUse": "echo '[harness] runtime=none, sin tests'"
"permissions.allow": ["Bash(./init.sh)"]
```

## Anti-patrones

- **Hook `PostToolUse` lento**: si tus tests tardan > 5s, el feedback se
  vuelve molesto. Usa un subset rápido (`pytest -m fast`, `cargo test --lib`).
  Los tests completos los corre `Stop`.
- **Hook `Stop` que abre prompt interactivo**: nunca uses comandos que
  requieran input. Si necesitas validación humana, hazla en review_*.md.
- **Hooks globales** en `~/.claude/settings.json`: el harness asume un
  runtime concreto. Hooks globales rompen sesiones sysadmin / docs / etc.
  Mantén estos hooks **solo en `.claude/settings.json` del proyecto**.
- **Permissions allowlist demasiado amplia**: empezar con `Bash(*)` deshabilita
  el gate. Mejor empezar restrictivo y añadir según necesites.
