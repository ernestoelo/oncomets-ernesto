# Obj 1 B5 — Lanzamiento de mammoth k=5 (LEER + VERIFICAR ANTES de `sbatch`)

> Este doc **NO lanza nada**. Es para que la sesión nueva (a) lea y **analice el
> slurm**, (b) verifique los invariantes, y recién con **OK explícito de Ernesto**
> haga el `sbatch`. Hipótesis (regla 9) y diseño:
> `sprints/B4_sprint4/objetivo_6_mammoth/README.md`. Reviewer ya dio GO.

## Paso 0 — Vendorizar la dependencia (recomendado; muta env compartido → con OK)

`mammoth-moe` está instalado editable desde `clam_testing/MAMMOTH` (fuera de
containment). Para un resultado **citable** conviene moverlo a `clam_testing2`.
Para una **1ª pasada exploratoria** se puede saltar (ya importa y funciona).

```bash
# Copia (offline-safe; preserva el .git con el pin fe36d4e)
cp -r /media/administrador/Storage1/sdonoso/clam_testing/MAMMOTH \
      /media/administrador/Storage1/sdonoso/clam_testing2/MAMMOTH
# Reinstalar editable apuntando DENTRO de containment
/home/sdonoso/miniconda3/envs/clam_latest/bin/pip install -e \
      /media/administrador/Storage1/sdonoso/clam_testing2/MAMMOTH
# Verificar que importa desde el nuevo path
/home/sdonoso/miniconda3/envs/clam_latest/bin/python -c "import mammoth; print(mammoth.__file__)"
# Esperado: .../clam_testing2/MAMMOTH/src/mammoth/__init__.py
```

## Paso 1 — Analizar el slurm ANTES de lanzar

Leer `scripts/run_obj6_mammoth_binarias_kfold.slurm` y confirmar (todo ya debería
estar así — es verificación, no edición):

- [ ] `--chdir`, `--output`, `--error` → bajo `clam_testing2/oncomets-ernesto/` (containment).
- [ ] `SPLITS_BASE=$REPO/data/splits_kfold` y `SPLIT_DIR=$SPLITS_BASE/${TASK}_100`
      → **mismos splits que Fase 0** (paired). Existen `splits_0..4.csv` por tarea.
- [ ] **Gates con `exit 1`** presentes y en orden: `verify_kfold_splits.py` →
      `tests/test_mammoth_cpu.py` (CPU) → `preflight_minpatch.py` por fold.
- [ ] `MODEL_TYPES` = `clam clam_mammoth` (ambos brazos) — comparación paired
      limpia por el mismo harness.
- [ ] Args bendecidos: `B=8`, `lr 2e-4`, `bag_weight 0.7`, `embed_dim 512`,
      `seed 1`, `max_epochs 30`, `early_stopping`, `label_dict {"no":0,"si":1}`.
- [ ] `PYBIN` = binario absoluto del env (workaround B); `nvidia-smi | head ... || true` (workaround D).
- [ ] `--results_dir` → `$REPO/results/obj6_mammoth_binarias_<tejido>` (el driver
      aborta si no está bajo `clam_testing2/`).
- [ ] `--time=24:00:00` cubre ~15h (3 tareas × 5 folds × 2 brazos).

## Paso 2 — Cortesía GPU (única y compartida)

```bash
cd /media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto
squeue ; sinfo        # ¿hay jobs ajenos esperando por Resources? si sí, NO monopolizar
git fetch && git status   # main limpio, sin sorpresas
```

## Paso 3 — Lanzar (SOLO con OK de Ernesto)

```bash
# Opción A — ambos brazos, comparación paired completa (~15h):
sbatch scripts/run_obj6_mammoth_binarias_kfold.slurm

# Opción B — brazo liviano (~7-8h), compara contra baseline Fase 0 ya computado:
MODEL_TYPES="clam_mammoth" sbatch scripts/run_obj6_mammoth_binarias_kfold.slurm
```

Si algún gate falla, el job termina en **segundos** (no gasta GPU) — leer el `.out`.

## Paso 4 — Monitorear

```bash
squeue -u $USER
tail -f logs/eg_mammoth_bin_kfold_*.out
# cancelar si hace falta: scancel <jobid>
```

## Paso 5 — Analizar (métrica decisiva)

Por cada tejido y brazo: `results/obj6_mammoth_binarias_<tejido>/<modelo>_<tejido>_f<f>_*_s1/test_metrics.json`
(tiene `balanced_acc` + matriz de confusión) y `summary.csv`.

- **Δ pareado por fold** = `clam_mammoth_f − clam_f` en balanced_acc → media ± std (k=5).
- **Veredicto** (umbral del Obj 6): éxito si Δ ≥ +0.03 (media) en ≥2/3 binarias con
  bandas no solapadas; regresión si Δ ≤ −0.05 con signo consistente (≥4/5 folds);
  si no, banda ambigua → "arquitectura no es la palanca tampoco acá".
- Escribir `sprints/B5_sprint5/objetivo_1_mammoth_run/resultados.md`. Entregables
  **sin números de job**, baseline como "Environ vX".
