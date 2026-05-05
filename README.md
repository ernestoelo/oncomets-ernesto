# oncomets-ernesto

Control center de mi trabajo en OncoMets / EnvironBio. Vive en Werner.
Wrapper alrededor del código de Sebastián Donoso (read-only, en otro path).

## Despliegue inicial

### 1. Desde mi laptop (una sola vez)

Sincronizar las skills relevantes desde `~/.claude/skills/` al repo:

```bash
cd ~/Documents/EnvironBio/oncomets-ernesto
./scripts/sync_skills_from_local.sh
```

Esto copia `dev-workflow/` y `harness/` a `.claude/skills/`. Versionar:

```bash
git init
git remote add origin git@github.com:ernestoelo/oncomets-ernesto.git
git add -A
git commit -m "feat: initial scaffold for Sprint 3 B3"
git branch -M main
git push -u origin main
```

### 2. En Werner — vía VS Code Remote SSH (camino principal)

Desde la laptop, en VS Code: `Remote-SSH: Connect to Host` → `environbio`.
Eso abre VS Code con el filesystem de Werner. Después, en una terminal
integrada de VS Code:

```bash
cd /mnt/disco_duro/onco/oncologiaEnviron/ernestogamero/
git clone git@github.com:ernestoelo/oncomets-ernesto.git
cd oncomets-ernesto
./scripts/verify_clam_access.sh    # smoke test del workaround importlib
```

Después se lanza Claude Code desde la terminal integrada (`claude`) con
el repo como cwd. Lee `CLAUDE.md` automáticamente.

### 3. SSH alias (referencia)

En `~/.ssh/config` de la laptop:

```
Host environbio
    HostName 200.1.17.169
    User onco
    # Si quieres bootstrap automático cuando hagas SSH directo (no VS Code):
    # RemoteCommand cd /mnt/disco_duro/onco/oncologiaEnviron/ernestogamero/oncomets-ernesto && exec ./scripts/bootstrap_werner.sh
    # RequestTTY yes
```

El `bootstrap_werner.sh` queda como referencia para sesiones SSH directas
casuales. **No es necesario para el flujo VS Code Remote SSH** — ahí Claude
Code lee `CLAUDE.md` directamente y arranca sin script intermedio.

## Uso diario

**Camino A — VS Code Remote SSH (recomendado):**
1. VS Code → Remote SSH a `environbio`.
2. Abrir carpeta `/mnt/disco_duro/onco/oncologiaEnviron/ernestogamero/oncomets-ernesto/`.
3. Terminal integrada → `claude`.

**Camino B — SSH directo (rápido, casual):**
```bash
ssh environbio
cd /mnt/disco_duro/onco/oncologiaEnviron/ernestogamero/oncomets-ernesto
./scripts/bootstrap_werner.sh
```

## Estructura

```
oncomets-ernesto/
├── CLAUDE.md                 # Contexto persistente, leído al lanzar Claude Code
├── AGENTS.md                 # Mapa de subagentes
├── README.md                 # Este archivo
├── .claude/
│   ├── settings.local.json   # Permisos de bash y filesystem
│   ├── agents/
│   │   └── trainer.md        # Subagente único: ejecuta entrenamientos
│   └── skills/               # dev-workflow, harness (sync desde laptop)
├── scripts/
│   ├── bootstrap_werner.sh       # Lanzamiento SSH → Claude Code (camino B)
│   ├── verify_clam_access.sh     # Smoke test del workaround importlib
│   ├── train_clam.sh             # Wrapper sobre main.py de Sebastián
│   ├── sync_skills_from_local.sh # Copia skills desde ~/.claude/skills/
│   └── extract_metrics.py        # Parsea logs → curvas para reportes
├── sprints/
│   └── B3_sprint3/           # Entregables del sprint actual
│       ├── objetivo_1_L_instance/
│       ├── objetivo_2_entrenamiento/
│       ├── objetivo_3_pipeline/
│       └── objetivo_4_propuestas/
├── docs/
│   ├── codebase_map.md       # Paths y líneas clave del código de Sebastián
│   ├── werner_environment.md # Stack, hostname, conda env, paths
│   └── workarounds.md        # importlib.util para CLAM_MB
└── progress/
    ├── current.md            # Sesión activa, append-only
    └── history.md            # Bitácora cerrada
```

## Reglas críticas (resumen)

- **No tocar** `/mnt/disco_duro/onco/sebastianDonoso/`.
- **`/home/onco/` es compartido** — todo lo personal va bajo
  `oncologiaEnviron/ernestogamero/`.
- **Importar** `CLAM_MB` vía `importlib.util` (workaround de `timm` en el
  `__init__.py` de Sebastián).
- **Diagramas > texto plano** para entregables.
- **Validar contra paper o código** toda afirmación técnica.

Detalle: `CLAUDE.md`.
