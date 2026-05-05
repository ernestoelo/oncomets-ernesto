# AGENTS.md — Mapa de subagentes

Setup minimal pre-deadline B3. Sólo un agente especializado.
Post-cierre se escalará a leader/implementer/reviewer con `@harness`.

## trainer

**Definición**: `.claude/agents/trainer.md`

**Foco**: Entregable 2 del Sprint 3 — entrenamiento end-to-end de CLAM en
Werner con dataset público.

**Lo que SÍ hace**:
- Audita datasets WSI ya presentes en Werner (Camelyon u otros).
- Lee el código de Sebastián (`main.py`, `core_utils.py`, `model_clam.py`)
  para entender qué CSV espera.
- Genera splits train/val/test y los CSV de input bajo
  `sprints/B3_sprint3/objetivo_2_entrenamiento/splits/`.
- Lanza entrenamientos vía `scripts/train_clam.sh`.
- Persiste logs y métricas bajo
  `sprints/B3_sprint3/objetivo_2_entrenamiento/logs/`.
- Documenta config + observaciones en `objetivo_2_entrenamiento/reporte.md`.

**Lo que NO hace**:
- No edita NADA bajo `/mnt/disco_duro/onco/sebastianDonoso/`.
- No infiere métricas que no estén en logs reales.
- No genera diagramas de los entregables 1, 3, 4 (eso lo hago directo en chat
  o post-cierre con un agente analyst dedicado).

## Cuándo usar el agente vs trabajar directo

- **Tareas largas** (lanzar entrenamiento, esperar epochs, parsear logs):
  delegar a `trainer`.
- **Discusión teórica, redacción de notas, generación de diagramas para
  presentación**: trabajar directo en la sesión principal de Claude.
