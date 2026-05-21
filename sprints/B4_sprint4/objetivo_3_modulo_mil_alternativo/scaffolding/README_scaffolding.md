# scaffolding/ — mapa del esqueleto del Objetivo 3

> **Esto es scaffolding, no implementación.** Ningún archivo de aquí
> entrena ni infiere nada. La lógica central levanta `NotImplementedError`.
> El propósito es tener la estructura lista para que, si la reunión
> confirma el módulo MIL, la implementación sea "rellenar TODOs" y no
> "diseñar desde cero".

## Archivos

| Archivo | Qué es | Estado |
|---|---|---|
| `__init__.py` | Hace de `scaffolding/` un paquete Python importable. | Hecho. |
| `dsmil_wrapper.py` | Skeleton del aggregator DSMIL y del wrapper sobre `CLAM_MB`. | Skeleton — `forward` levanta `NotImplementedError`. |
| `train_obj3.py` | Skeleton del training script (patrón de `main.py`). | Skeleton — funciones levantan `NotImplementedError`. |
| `README_scaffolding.md` | Este archivo. | Hecho. |

## `dsmil_wrapper.py`

Dos clases:

- **`DSMILAggregator(nn.Module)`** — la rama de pooling dual-stream de
  DSMIL. Es lo único arquitectónicamente nuevo del objetivo.
  - **Implementado**: firma de `__init__` (hiperparámetros: `in_dim`,
    `n_classes`, `q_dim`, `passing_v`, `nonlinear`), docstrings con la
    formalización y la correspondencia con `dsmil.py` oficial, esquema
    del `forward` en comentarios.
  - **TODO**: las 3 sub-redes (`instance_scorer`, `q_net`, `v_net`) están
    en `None`; el `forward` levanta `NotImplementedError`.
- **`DSMIL_CLAM_MB(nn.Module)`** — el wrapper. Enchufa el aggregator en
  lugar del `Attn_Net_Gated` de `CLAM_MB`, conservando `fc` de entrada,
  bag classifier e instance branch.
  - **Implementado**: firma de `__init__` alineada con `CLAM_MB`
    (`model_clam.py:186`), `size_dict`, docstrings, esquema del `forward`.
  - **TODO**: los bloques (`fc`, `aggregator`, `classifiers`,
    `instance_classifiers`) están en `None`; el `forward` levanta
    `NotImplementedError`.

Decisión de diseño registrada: el skeleton subclasea `nn.Module` (no
`CLAM_MB`) para que `import scaffolding.dsmil_wrapper` nunca falle — no
importa nada de `clam_environ/` a nivel de módulo. La implementación
decidirá entre subclasear o componer `CLAM_MB`; ese import irá dentro de
`__init__`.

## `train_obj3.py`

Skeleton del wrapper de training. Replica el **patrón** de
`clam_environ/main.py` (no lo copia):

- **Implementado**: `build_argparser()` completo (args bendecidos de
  CLAUDE.md + args específicos de DSMIL), estructura de funciones
  (`build_model`, `get_datasets`, `train_one_fold`, `write_summary`,
  `main`), y el plan de cada una en comentarios `TODO(impl)`.
- **TODO**: toda la lógica. `main()` y las funciones levantan
  `NotImplementedError`.

Punto clave: `train_one_fold` documenta dos caminos — (A) reusar
`utils/core_utils.py` de Sebastián si la firma de `DSMIL_CLAM_MB.forward`
es compatible, (B) loop local si no. Cuál aplica se decide en el smoke
test, no antes.

## Verificación del skeleton (sin GPU)

```bash
conda activate clam_latest
cd sprints/B4_sprint4/objetivo_3_modulo_mil_alternativo
python -c "import scaffolding.dsmil_wrapper; print('import ok')"
python scaffolding/dsmil_wrapper.py     # construye skeletons; forward -> NotImplementedError
```

No usa GPU, no entra a `clam_environ/`, no encola nada.

## Cómo se integra post-reunión

1. La reunión confirma el módulo (DSMIL u otro) — decisión #6 del sprint.
2. Se valida la arquitectura contra `DSMIL_official_reference/dsmil.py` y
   el paper, y se rellenan los TODOs de `dsmil_wrapper.py`.
3. **Antes de commitear esa implementación: agente `reviewer`** (regla 9
   — toca arquitectura de modelo; la hipótesis y la métrica de éxito ya
   están en `../propuesta_dsmil.md`).
4. Se rellenan los TODOs de `train_obj3.py` y se crea
   `scripts/train_dsmil.slurm`.
5. Smoke test -> train corto -> train completo vía `sbatch`.

Detalle de la integración: [`../plan_integracion.md`](../plan_integracion.md).
