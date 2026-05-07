
# AGENTS.md — Mapa de subagentes

Setup minimal de subagentes. Sólo un agente especializado por ahora.
Post-Sprint 4 se evaluará escalar a leader/implementer/reviewer con `@harness`.

## trainer

**Definición**: `.claude/agents/trainer.md`

**Foco**: Entrenamiento end-to-end de CLAM en Werner. Cualquier sprint
que requiera lanzar runs, generar splits, parsear logs.

**Lo que SÍ hace**:

- Audita datasets WSI ya presentes en Werner (Camelyon u otros).
- Lee el código de Sebastián (`main.py`, `core_utils.py`, `model_clam.py`)
  para entender qué CSV espera.
- Genera splits train/val/test y los CSV de input bajo el directorio
  del sprint actual: `sprints/<sprint>/<objetivo>/splits/`.
- Lanza entrenamientos vía `scripts/train_clam.sh`.
- Persiste logs y métricas bajo `sprints/<sprint>/<objetivo>/logs/`.
- Documenta config + observaciones en `sprints/<sprint>/<objetivo>/reporte.md`.

**Lo que NO hace**:

- No edita NADA bajo `/mnt/disco_duro/onco/sebastianDonoso/`.
- No infiere métricas que no estén en logs reales.
- No genera diagramas conceptuales ni redacción de informes
  (eso lo hago directo en chat web de claude.ai, no en Claude Code).

## Cuándo usar el agente vs trabajar directo

- **Tareas largas** (lanzar entrenamiento, esperar epochs, parsear logs):
  delegar a `trainer`.
- **Discusión teórica, redacción de notas, generación de diagramas para
  presentación**: trabajar directo en la sesión principal de Claude.
