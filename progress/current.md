# progress/current.md

> Sesión activa. Append-only. Cada sesión nueva = entrada nueva al final.
> Al cerrar el sprint, mover este contenido a `history.md` y reiniciar acá.

---

## Sprint actual: B3 / Sprint 3

**Deadline**: miércoles 6 de mayo de 2026.

**Estado por entregable** (actualizar tras cada sesión):

- [ ] **Entregable 1** — Estudio L_instance + diagrama + tabla de hiperparámetros.
  - Próximo paso: re-leer Sec 2.2 del paper CLAM con foco en SmoothTop1SVM.
- [ ] **Entregable 2** — Entrenamiento end-to-end de CLAM en Werner.
  - Próximo paso: leer `run_all_splits.sh` y `run_all_training.sh` de Sebastián.
  - Bloqueante de los entregables 3 y parcialmente del 4.
- [ ] **Entregable 3** — Pipeline + formato `.csv` (split_dir).
  - Próximo paso: trazar control flow `main.py → utils/core_utils.py`.
  - Depende parcialmente de E2 (formato real lo confirma corriendo).
- [ ] **Entregable 4** — ≥2 propuestas de mejora.
  - Idea 1: aumentar top-B/bottom-B (ya planteada en reunión).
  - Idea 2: candidatas en memoria — adaptive pseudo-label selection,
    fragility de mutual exclusivity, asimetría 9:1 bajo subtyping.

---

## Sesión 0 — Setup del repo (5 mayo 2026, antes del trabajo en Werner)

### Logros

- Scaffold inicial del control center creado y subido a
  `github.com/ernestoelo/oncomets-ernesto` (privado).
- Skills `dev-workflow` y `harness` bundleadas en `.claude/skills/`.
- Subagente único `trainer` definido para el Entregable 2.

### Hallazgos al validar contra el código real de Werner

Los siguientes paths/líneas/argumentos del scaffold inicial estaban
**incorrectos** y se corrigieron antes de la primera sesión real:

| Ítem | Asunción inicial | Realidad confirmada |
|---|---|---|
| `model_clam.py` | en raíz | en `models/model_clam.py` |
| `core_utils.py` | en raíz | en `utils/core_utils.py` |
| Líneas `inst_eval` | 107–123 | 107–125 (correcto) |
| `subtyping=True` | L226 | L96 (CLAM_SB) y L203 (CLAM_MB). L226 es `train_loop_clam` |
| `torch.mm(A, h)` | L237 | L170 (CLAM_SB) y L237 (CLAM_MB) — hay DOS clases |
| Arg de `main.py` | `--csv_path` | `--split_dir` (apunta a directorio con CSVs) |
| Generación de splits | manual | `create_splits_seq.py` los genera |
| `core_utils.py:243–251` | "instance loss" | L246 extrae instance_loss, L251 combina con bag_weight |

### Archivos descubiertos que vale la pena leer

- `run_all_splits.sh` — workflow de Sebastián para generar splits
- `run_all_training.sh` — workflow de Sebastián para training
- `readme_environ.md`, `index_CAP_environ.md`, `openslide_solution.md`
- `dataset_csv/` — splits ya generados, posibles para reusar

### Decisiones tomadas

- **No generar splits a mano**: usar `create_splits_seq.py` como Sebastián.
- **Workaround de `importlib.util` queda en duda**: re-validar al primer
  uso. Puede no ser necesario con el `__init__.py` actual.

---

## Sesión 1 — Primera ejecución en Werner _(pendiente)_

### Setup

- [ ] `git clone` del repo en Werner exitoso.
- [ ] `verify_clam_access.sh` confirma:
  - paths reales OK
  - PyTorch + CUDA OK
  - import de CLAM_MB OK (con o sin workaround)
- [ ] `nvidia-smi` muestra 4 GPUs disponibles.

### Decisiones tomadas

_(vacío)_

### Bloqueos

_(vacío)_

### Próxima sesión arranca con

_(vacío)_

---
