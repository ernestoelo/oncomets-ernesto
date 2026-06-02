# Snapshot del trabajo de mammoth heredado de Eduardo

> Capturado el 2026-06-01 desde `clam_testing/` (carpeta de Eduardo, heredada a
> Ernesto tras su renuncia). **Motivo:** la integración de mammoth de Eduardo
> estaba **SIN COMMITEAR** — vivía como modificaciones del working-tree sobre el
> fork público de CLAM (`git log` de `clam_testing` = solo historia upstream de
> Mahmood Lab). Cualquier `git checkout` la habría destruido. Esto la preserva.

## Procedencia

- Origen: `/media/administrador/Storage1/sdonoso/clam_testing/` (READ-ONLY para
  nosotros; copiamos, no escribimos ahí — workspace containment).
- `MAMMOTH/` dentro de esa carpeta = clon limpio de `github.com/mahmoodlab/MAMMOTH`
  @ `fe36d4e` (recuperable de GitHub; no es código de Eduardo).
- `mammoth-moe` está **instalado editable** en el env `clam_latest` desde
  `clam_testing/MAMMOTH/src`.

## Contenido

- `eduardo_clam_testing_src_20260601.tar.gz` — backup completo del **código**
  (excluye `.git`, checkpoints, results, logs, `*.pt/.pth/.h5`, `*.out/.err`).
  Gitignored (23 MB). Es el respaldo full.
- `key_sources/` — los archivos de código **irremplazables** extraídos para diff
  cómodo (committeados):
  - `models/model_clam.py` — integración mammoth: clase `MammothPatchEmbed` +
    flags `use_mammoth`, `mammoth_num_{experts,slots,heads}`, `mammoth_slot_dim`.
    Reemplaza el `nn.Linear(size[0], size[1])` del `attention_net`.
    **`keep_slots=True` hardcodeado** (salida E·S agregadas, no N parches).
  - `main.py` — args de CLI de mammoth + del sweep papilar.
  - `utils/core_utils.py` — training loop fuertemente modificado (+749 líneas):
    `grad_cosine`, schedulers (plateau/cosine), confidence_penalty, weighted
    positive. **Maquinaria de los sweeps, no requerida por el port mínimo.**
  - `utils/pcgrad.py` — **PCGrad (gradient surgery)**: proyecta gradientes en
    conflicto. Eduardo atacó el *instance-gradient interference* por DOS vías:
    mammoth (arquitectura) + PCGrad (optimización). Eje futuro propio.
  - `utils/utils.py`, `models/builder.py` — cambios de soporte.
  - `slurm/run_papilar_clam_mammoth_sweep*.slurm` — sus 3 campañas (V1→V3).
  - `ESTUDIO_papilar_v2.md` — su análisis: la tarea era
    `cdis_patron_papilar_pth_balance` (NO microcalcificaciones), y ya chocó con
    el **test estadísticamente ciego** (~3 positivos → AUC cuantizado a 1/75).
    Su conclusión: el fix real es **K=5 estratificado**.

## Qué tomamos para nuestro port

El **delta mínimo de mammoth** (no toda la maquinaria de sweeps): `MammothPatchEmbed`
+ los flags `use_mammoth`. Se porta a `models_mammoth/` sobre una copia limpia del
codebase de Sebastián (no sobre el fork divergido de Eduardo), para que la
comparación PAIRED vs el baseline CLAM Environ no tenga confounds de training-loop.
Ver el plan en `../README.md` (objetivo 6) y la memoria
`mammoth-investigacion-integracion`.
