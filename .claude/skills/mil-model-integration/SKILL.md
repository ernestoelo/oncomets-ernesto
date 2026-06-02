---
name: mil-model-integration
description: Integrar un modelo MIL alternativo (variante de CLAM o agregador nuevo) en OncoMets sin tocar clam_environ, paired vs CLAM. Triggers — integrar modelo, modelo alternativo, nuevo MIL, agregar model_type, portar modelo, models_dsmil, models_mammoth.
---

# mil-model-integration — Integrar un modelo MIL alternativo en OncoMets

Receta **reusable y probada** (DSMIL Obj 3/5 → mammoth Obj 6) para agregar un
modelo MIL alternativo y compararlo **paired** contra el baseline CLAM, sin
modificar el codebase READ-ONLY de Sebastián (`clam_environ/`). Evita reinventar
el harness cada vez.

## Cuándo aplica

- Querés probar una arquitectura/variante nueva (otro agregador, otra capa,
  gradient surgery, etc.) contra CLAM sobre las tasks de microcalcificaciones u
  otra.
- Tenés que portar trabajo heredado (ej. el de Eduardo) a nuestro workspace.
- NO aplica para cambiar hiperparámetros del CLAM existente (eso es ablation, no
  integración) ni para reformular etiquetas (eso es cambio de tarea).

## El harness ya existe y es genérico

`scripts/train_dsmil.py` (el nombre engaña) es **el harness MIL genérico**:
`--model_type {dsmil, clam, clam_mammoth}` con train/val/test + loss bag+inst
IDÉNTICOS → comparación apples-to-apples por construcción. El path
`clam`/`clam_mammoth` es byte-idéntico a `core_utils.train_loop_clam`; lo
específico de DSMIL (L_max + grad-logging) está gated en `== "dsmil"`. **No
escribas un driver nuevo: extendelo.**

## Receta (6 pasos)

1. **Código del modelo** → `models_<X>/` bajo el repo (containment, nunca en
   `clam_environ/` ni `clam_testing/`):
   - Variante de CLAM (ej. mammoth, cambiás una capa): **subclase de `CLAM_MB`**
     importado read-only de `clam_environ` → heredás `forward`/`inst_eval`
     verbatim, el delta es explícito y mínimo. Ejemplo: `models_mammoth/clam_mammoth.py`.
   - Agregador nuevo (ej. DSMIL): **wrapper** que emule la firma de
     `CLAM_MB.forward` → `(logits, Y_prob, Y_hat, A, results_dict)`. Ejemplo:
     `models_dsmil/wrapper.py`.
2. **Driver**: branch **ADITIVO** `elif args.model_type == "<X>":` en
   `build_model` de `train_dsmil.py` + args propios del modelo con defaults. **NO
   toques los paths `dsmil`/`clam`** (reproducibilidad de jobs 4135/4137/4170).
3. **SLURM** (espejá `scripts/run_obj5_dsmil_binarias_kfold.slurm`): reusá
   `data/splits_kfold/<task>_pth_100` (mismos splits que Fase 0 → **PAIRED**,
   ver skill de comparación pareada). Gates antes de GPU, todos con `exit 1`:
   `verify_kfold_splits.py` + el test CPU del modelo + `preflight_minpatch.py`
   por fold (workaround G). `set -euo pipefail` + `nvidia-smi | head ... || true`
   (workaround D). `PYBIN` absoluto del env (workaround B).
4. **Test CPU** en `tests/test_<X>_cpu.py` (espejá `test_dsmil_cpu.py` /
   `test_mammoth_cpu.py`): forward bag random + `.pt` real, shapes, no-NaN,
   gradiente fluye. **Gotcha**: `CLAM_MB.forward` devuelve `A_raw` PRE-softmax
   (no asumir `A.sum==1`; usar `softmax` o solo la forma `(n_classes, N)`).
5. **Hipótesis (regla 9)** en `sprints/<sprint>/objetivo_*/README.md`: primaria +
   alternativa + regresión, métrica decisiva (balanced_acc media±std k=5, Δ
   pareado), umbrales anclados al baseline real. Comparación = "paired vs CLAM
   Fase 0 reusando <split_dir>".
6. **Reviewer** (subagente, OBLIGATORIO antes de commit). Si el modelo toca un
   componente que un veredicto previo descartó, distinguí **eje ortogonal**
   (otra capa → no es reapertura) de **reapertura** (mismo componente → exige
   citar hallazgo habilitante, regla 9.b).

## Reglas que NO se saltan

- Containment (`clam_testing2/`), `clam_environ/` READ-ONLY, GPU solo vía
  `sbatch`, `--seed 1`, `exp_code` con timestamp, `--embed_dim 512` (CONCH).
- Dependencias externas (paquetes del modelo): vendorizarlas bajo `clam_testing2`
  o como mínimo pinear el commit y documentarlo (no depender de paths fuera del
  containment, como pasó con `mammoth-moe` editable desde `clam_testing`).

## Ejemplos vivos

- `models_dsmil/` + `train_dsmil.py --model_type dsmil` (agregador nuevo).
- `models_mammoth/` + `train_dsmil.py --model_type clam_mammoth` (variante CLAM).
  Detalle operacional de mammoth: skill `@mammoth`.
