
# AGENTS.md — Mapa de subagentes

Setup minimal de subagentes para el control center. Post-Sprint 4 se
evaluará escalar a leader/implementer/reviewer formal con `@harness`.

## trainer

**Definición**: `.claude/agents/trainer.md`

**Foco**: Entrenamiento end-to-end de CLAM (y wrappers — ej. DSMIL en
Sprint 4) en Werner. Cualquier sprint que requiera lanzar runs, generar
splits, parsear logs.

**Lo que SÍ hace**:

- Audita datasets WSI ya presentes en Werner (Camelyon, TCGA, Environ).
- Lee el código de Sebastián (`main.py`, `core_utils.py`, `model_clam.py`)
  para entender qué CSV espera.
- Genera splits train/val/test y los CSV de input bajo el directorio
  del sprint actual: `sprints/<sprint>/<objetivo>/splits/`.
- Lanza entrenamientos vía `scripts/train_clam.sh` (o wrapper análogo).
- Persiste logs y métricas bajo `sprints/<sprint>/<objetivo>/logs/`.
- Documenta config + observaciones en `sprints/<sprint>/<objetivo>/reporte.md`.
- Cross-check programático de `splits_0_descriptor.csv` (Hallazgo 1
  del Sprint 3 — el descriptor puede estar stale).

**Lo que NO hace**:

- No edita NADA bajo `/mnt/disco_duro/onco/sebastianDonoso/`.
- No infiere métricas que no estén en logs reales.
- No genera diagramas conceptuales ni redacción de informes
  (eso lo hago directo en chat web de claude.ai, no en Claude Code).
- **No comitea cambios a modelo / training sin pasar por `reviewer`**
  (regla operativa nueva del Sprint 4, "Argumento antes de código").

## reviewer

**Definición**: `.claude/agents/reviewer.md`

**Foco**: Validar propuestas de cambio a modelo / entrenamiento contra
la regla operativa nueva del Sprint 4 — **"Argumento antes de código"**.

**Trigger**: invocar **antes de cualquier commit que toque**:

- `models/*.py` o sus wrappers locales (ej. `src/dsmil_aggregator.py`).
- `utils/core_utils.py` o wrappers que reimplementen el train loop.
- Scripts de entrenamiento (`scripts/train_clam.sh`, `train_dsmil.sh`,
  variantes).
- Configuración de hiperparámetros que se desvíe de los args bendecidos
  por Sebastián.
- Wrappers de evaluación que introduzcan métricas nuevas.

**Lo que SÍ hace**:

- Lee el diff propuesto y el `objetivo_*/README.md` del sprint
  correspondiente.
- Verifica que estén presentes **hipótesis explícita** + **métrica de
  éxito predefinida** asociadas al cambio.
- **Bloquea** (report sin commit) si falta alguno de los dos.
- Reporta riesgos no negociables: ¿el cambio toca `/mnt/disco_duro/onco/
  sebastianDonoso/`? ¿inventa métricas? ¿modifica configuración global
  de git?

**Lo que NO hace**:

- No ejecuta entrenamientos (eso es del `trainer`).
- No escribe código nuevo. Solo lee y reporta.
- No emite opinión sobre estética del código ni refactors que no toquen
  el modelo o el training.

## Cuándo usar agentes vs trabajar directo

- **Tareas largas** (lanzar entrenamiento, esperar epochs, parsear logs):
  delegar a `trainer`.
- **Validar propuesta de cambio a modelo o training**: invocar `reviewer`
  antes del commit.
- **Discusión teórica, redacción de notas, generación de diagramas para
  presentación**: trabajar directo en la sesión principal de Claude.
