# Codebase map — código de Sebastián Donoso

Mapa de archivos y líneas clave del CLAM fork de Sebastián. Validado contra
las versiones de `model_clam.py` y `core_utils.py` presentes en project files.

**Path raíz**: `/mnt/disco_duro/onco/sebastianDonoso/testMIL/CLAM/`

**Reglas**: ningún archivo bajo este path se modifica. Si algo necesita
cambiar, se hace en este repo (vía wrapper o copia local).

## model_clam.py

| Líneas | Función / símbolo | Qué hace |
|---|---|---|
| L107–123 | `inst_eval` | Instance classifier — rama in-class. Usa top-k positivos + top-k negativos del attention. |
| L125–136 | `inst_eval_out` | Instance classifier — rama out-of-class. Bajo `subtyping=True`, contribuye 9× la rama in-class al gradiente total de `L_instance`. |
| L226 | flag `subtyping` | Activa mutual exclusivity entre clases para el cómputo de la instance loss. |
| L237 | `torch.mm(A, h)` | **Attention pooling** — opera sobre todos los N parches. La selección top-B/bottom-B NO interviene acá (ese mecanismo es exclusivo del instance classifier path). |

### Notación clave

- `A` — matriz de atención de dimensión `n × N` (no `256 × 512`, error
  común y ya corregido en sprints anteriores).
- `h` — features post-encoder, dimensión `N × D` con `D ∈ {512, 1024}`
  según el dataset (CONCH 512-dim para TCGA, 1024-dim para Environ).

## core_utils.py

| Líneas | Función / símbolo | Qué hace |
|---|---|---|
| L243–251 | cómputo de `instance_loss` en train loop | Suma `inst_eval` + `inst_eval_out` por clase, divide por `n_classes`. **Acá vive la interacción con `bag_weight`** que combina instance loss + slide loss en la loss total. |

## main.py

Entrypoint. Argumentos clave (validar con `--help` real al primer run):
- `--csv_path` — CSV de splits con `case_id`, `slide_id`, `label`.
- `--data_root_dir` — raíz de las features CONCH precomputadas (`.pt` por slide).
- `--results_dir` — donde se guardan checkpoints y logs.
- `--task`, `--model_type`, `--B`, `--inst_loss`, `--bag_weight`,
  `--subtyping` — config principal.

## builder.py

Construcción del modelo. Si necesito leer cómo se ensambla CLAM_MB con
CONCH features, empezar acá.

## Workaround obligatorio

`__init__.py` del CLAM fork importa `timm`, lo que rompe imports laterales.
Mitigación: cargar `model_clam.py` directo via `importlib.util`. Ver
`docs/workarounds.md`.

## Hechos validados (no re-derivar en chat)

1. Attention pooling NO usa top-B/bottom-B — son mecanismos disjuntos.
2. Bajo `subtyping=True` la asimetría 9:1 (out vs in) en `L_instance` es
   estructural, no un bug ni un artefacto de tuning.
3. `L_instance` se divide por `n_classes` y luego se pesa con `bag_weight`
   en la loss total. **Entender `bag_weight` y la división juntas, no
   aisladas.**
