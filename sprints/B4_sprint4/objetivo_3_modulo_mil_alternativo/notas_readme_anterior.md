# Notas — contenido del README anterior que no folió limpio

> El directorio se renombró `objetivo_3_dsmil/` → `objetivo_3_modulo_mil_alternativo/`
> y su `README.md` único se dividió en `README.md` (contexto genérico),
> `propuesta_dsmil.md` (argumento DSMIL) y `plan_integracion.md`
> (integración al pipeline). Casi todo folió limpio. Este archivo registra
> lo que **no** encajó, para que la decisión de conservarlo o descartarlo
> sea explícita y no una pérdida silenciosa.

## Único conflicto: el layout de archivos planificado

El README anterior proponía un layout de archivos **distinto** al que
pidió esta sesión de scaffolding. No es contenido perdido — es una
decisión de estructura que cambió.

### Layout que proponía el README anterior

`section "Output esperado"`:

```
objetivo_3_dsmil/
├── README.md                       # README único
├── dsmil_architecture_notes.md     # derivación matemática + notas de implementación
├── src_local/
│   ├── dsmil_aggregator.py         # módulo DSMIL puro (no toca CLAM)
│   └── clam_dsmil_wrapper.py       # subclase de CLAM_MB con aggregator intercambiado
├── resultados.md                   # baseline vs DSMIL, tabla por tarea
└── logs/
    └── <task>_dsmil_<exp_code>/
```

`section "Cambios concretos al código"` (usaba además, de forma
internamente inconsistente, el prefijo `src/` en vez de `src_local/`):

- `src/dsmil_aggregator.py` — módulo DSMIL puro.
- `src/clam_dsmil_wrapper.py` — subclase de `CLAM_MB`.
- `main_dsmil.py` — entrypoint local que importa `main.py` de Sebastián.
- `scripts/train_dsmil.slurm` — wrapper SLURM de training.

### Layout que adoptó esta sesión

```
objetivo_3_modulo_mil_alternativo/
├── README.md                    # contexto genérico del objetivo
├── propuesta_dsmil.md           # argumento DSMIL (incluye lo que iba en dsmil_architecture_notes.md)
├── alternativas_consideradas.md
├── plan_integracion.md          # incluye "Cambios concretos al código"
├── requirements_obj3.txt
├── notas_readme_anterior.md     # este archivo
└── scaffolding/
    ├── __init__.py
    ├── dsmil_wrapper.py         # aggregator dual-stream + wrapper DSMIL_CLAM_MB en un solo archivo
    ├── train_obj3.py            # esqueleto de training (≈ main_dsmil.py + train_dsmil.slurm)
    └── README_scaffolding.md
```

### Mapeo viejo → nuevo

| Archivo planificado (viejo) | Dónde quedó ahora |
|---|---|
| `dsmil_architecture_notes.md` | Folió en `propuesta_dsmil.md` (formalización + diagrama). |
| `src_local/dsmil_aggregator.py` | Consolidado en `scaffolding/dsmil_wrapper.py` (clase `DSMILAggregator`). |
| `src_local/clam_dsmil_wrapper.py` | Consolidado en `scaffolding/dsmil_wrapper.py` (clase `DSMIL_CLAM_MB`). |
| `main_dsmil.py` | Su rol lo cubre el esqueleto `scaffolding/train_obj3.py`. |
| `scripts/train_dsmil.slurm` | Pendiente — se crea en la implementación post-reunión (no es parte del scaffolding). |
| `resultados.md` | Pendiente — la tabla placeholder vive por ahora en `README.md`. |
| `logs/<task>_dsmil_<exp_code>/` | Pendiente — se crea al ejecutar; los logs SLURM van a `logs/` del repo (containment, ver CLAUDE.md). |

## Decisión a tomar

El scaffolding consolidó dos archivos de código (`dsmil_aggregator.py` +
`clam_dsmil_wrapper.py`) en uno (`dsmil_wrapper.py`). Si en la
implementación efectiva conviene volver a separarlos (aggregator puro vs
wrapper), hacerlo entonces — no es una decisión que el scaffolding deba
forzar. Se reporta aquí para que quede a la vista.
