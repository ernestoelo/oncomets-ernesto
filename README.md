# oncomets-ernesto

Control center de mi trabajo en OncoMets / EnvironBio. Vive en el **servidor
Environ**. Wrapper alrededor del código de Sebastián Donoso (`clam_environ/`,
read-only, en otro path). Migrado desde el servidor antiguo (Werner) el
19 may 2026 — ver `docs/environ_server.md` y
`sprints/B4_sprint4/reconocimiento_entorno.md`.

## Entorno (servidor Environ)

| Campo | Valor |
|---|---|
| Host | `administrador-PowerEdge-R740xd` |
| Acceso | VPN oficial Environ + SSH |
| Usuario | `sdonoso` (compartido) |
| GPU | 1× RTX A6000 (49 GB), CUDA 12.8 |
| SLURM | partición única `debug`, 1 nodo |
| Conda env CLAM | `clam_latest` |
| Mi workspace | `/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/` |
| Codebase (read-only) | `/media/administrador/Storage1/sdonoso/clam_environ/` |

## Setup (ya hecho — referencia)

El repo ya está clonado en el workspace. La identidad git es **local**
(el global apunta a Seba Donoso, usuario compartido):

```bash
git config --local user.name  "Ernesto Gamero"
git config --local user.email "ernesto.gamero@sansano.usm.cl"
```

Smoke test de acceso al codebase:

```bash
./scripts/verify_clam_access.sh    # lee CLAM_PATH=clam_environ por default
```

## Uso diario

**Camino A — VS Code Remote SSH (recomendado):**
1. VS Code → Remote SSH al servidor Environ (VPN arriba).
2. Abrir carpeta `/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/`.
3. Terminal integrada → `claude`. Lee `CLAUDE.md` automáticamente.

**Camino B — SSH directo (rápido, casual):**
```bash
ssh <host_environ>
cd /media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto
./scripts/bootstrap_environ_server.sh
```

## Lanzar trabajos GPU (SLURM)

**Toda carga GPU va por `sbatch`, nunca `python` directo.** Plantilla en
`scripts/train_clam.slurm` y skill `@slurm-submission`.

```bash
mkdir -p logs
squeue ; sinfo                       # cortesía: GPU única, no monopolizar
sbatch scripts/train_clam.slurm      # editar TASK/EXP_CODE/SPLIT_DIR antes
squeue -u $USER                      # monitorear
tail -f logs/eg_train_<jobid>.out
```

## Estructura

```
oncomets-ernesto/
├── CLAUDE.md                 # Contexto persistente, leído al lanzar Claude Code
├── AGENTS.md                 # Mapa de subagentes
├── README.md                 # Este archivo
├── .claude/
│   ├── settings.local.json
│   ├── agents/
│   │   ├── trainer.md        # ejecuta entrenamientos vía SLURM
│   │   └── reviewer.md       # valida "argumento antes de código"
│   └── skills/               # slurm-submission, environ-server, csv-audit, dev-workflow, harness
├── scripts/
│   ├── bootstrap_environ_server.sh  # lanzamiento SSH → Claude Code (camino B)
│   ├── verify_clam_access.sh        # smoke test de acceso a clam_environ
│   ├── train_clam.slurm             # ← wrapper SLURM sobre main.py (GPU)
│   ├── train_clam.sh                # legacy (CPU/debug; no usar en GPU fuera de SLURM)
│   ├── sync_skills_from_local.sh
│   └── extract_metrics.py           # parsea logs → métricas
├── sprints/
│   ├── B3_sprint3/           # cerrado (artefactos históricos, runs en Werner)
│   └── B4_sprint4/           # sprint actual + reconocimiento_entorno.md
├── docs/
│   ├── codebase_map.md       # paths y líneas clave de clam_environ
│   ├── environ_server.md     # stack, hostname, conda env, paths
│   └── workarounds.md
├── logs/                     # salidas SLURM (.out/.err) — gitignored salvo texto
└── progress/
    ├── current.md            # sesión activa, append-only
    └── history.md            # bitácora cerrada
```

## Reglas críticas (resumen)

- **No tocar** `clam_environ/` (codebase + datos de Sebastián, read-only).
- **No entrar a escribir** en `clam_testing/` (otra persona).
- **GPU solo vía SLURM** (`sbatch`), nunca `python` directo en GPU.
- **Git config LOCAL**, nunca global (el global = Seba Donoso).
- **Diagramas > texto plano** para entregables.
- **Validar contra paper o código** toda afirmación técnica.

Detalle: `CLAUDE.md`.
