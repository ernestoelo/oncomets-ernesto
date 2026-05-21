# Run fallido — job 4096 (baseline B=8, MicroCalcificaciones)

**No borrar.** Evidencia del bug de `torch.topk` en `inst_eval`.

## Qué fue

- Job SLURM **4096**, baseline B=8, `microcalcificaciones_pth`, split **canónico**
  (sin filtrar). Arrancó 2026-05-21 08:08, crasheó ~09:51.
- Script: la versión previa de `slurm/baseline_microcalc_B8.slurm` (apuntaba al
  split canónico). Reemplazada por `slurm/baseline_microcalc_B8_minpatch16.slurm`.

## Por qué falló

`models/model_clam.py` → `inst_eval` hace `torch.topk(A, k_sample)` con
`k_sample = --B = 8`. La slide de train `histai_1536_slide_H&E_0` tiene solo
**6 parches** en su `.pt` → `topk(A, 8)` sobre un tensor de 6 elementos:

```
RuntimeError: selected index k out of range
```

Con `--weighted_sample` (muestreo con reemplazo) esa slide se sorteó recién en
una época tardía → el run entrenó bastante (`val_auc` llegó a **0.6581**) antes
de caer. **No escribió `summary.csv`** → sin métricas finales de test.

## Contenido de este directorio

- `baseline_microcalc_B8_4096.out` / `.err` — logs SLURM del run fallido.
- `run_artifacts/baseline_microcalc_pth_B8_20260521_0808_s1/` — checkpoint
  parcial (`s_0_checkpoint.pt`, mejor época por val), `experiment_*.txt`,
  tensorboard. El checkpoint NO se versiona (gitignore de `.pt`).

## Valor

- Evidencia del bug y predictor del comportamiento del re-run: el modelo
  entrena bien (val_auc ~0.66 ya supera el 0.55 de V4, aunque otro split);
  el fallo es puramente el crash de bag pequeño.
- Fix aplicado: split filtrado `minpatch16` (ver
  `splits_local/microcalcificaciones_pth_100_minpatch16/README.md`) +
  preflight (`scripts/preflight_minpatch.py`) en los `.slurm`.

> Nota: el run **4083** (anterior, bug `nvidia-smi|head` bajo `set -o pipefail`)
> no se archivó aquí; sus logs siguen en `logs/` (gitignored) y está
> documentado en `objetivo_1_baseline/resultados.md`.
