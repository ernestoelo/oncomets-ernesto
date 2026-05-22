
# CLAUDE.md — Control center OncoMets / Ernesto

> Este archivo es lo primero que Claude Code lee al lanzarse en este repo.
> Contiene contexto persistente del proyecto y reglas operativas.
> Estado en evolución (sprint actual, hallazgos): ver `progress/current.md`.
>
> **Migrado el 19 may 2026** desde el servidor antiguo (Werner / jenny2) al
> **servidor Environ actual**. Detalle del reconocimiento del entorno nuevo:
> `sprints/B4_sprint4/reconocimiento_entorno.md`.

---

## Quién soy y dónde estoy

Soy Ernesto Gamero, estudiante de último año de Ingeniería Civil Electrónica
(esp. Computadores) en la UTFSM. Práctica en EnvironBio en el proyecto
**OncoMets** (IA para diagnóstico oncológico), 20 hrs/sem. Supervisor:
Sebastián Gaete. Senior: Benjamín. Colaborador: Eduardo.

Este repo (`oncomets-ernesto`) es mi **control center** sobre el servidor
Environ. NO contiene el código de CLAM — ese es de Sebastián Donoso
(`clam_environ/`) y es **read-only**.

## Entorno actual (servidor Environ)

Acceso: **VPN oficial Environ + SSH**. Stack registrado el 19 may 2026
(`sprints/B4_sprint4/reconocimiento_entorno.md`):

| Campo | Valor |
|---|---|
| Hostname | `administrador-PowerEdge-R740xd` (Dell PowerEdge R740xd) |
| Usuario | `sdonoso` (uid 1008) — **compartido**, no personal |
| OS / kernel | Ubuntu 22.04 / `6.8.0-101-generic` x86_64 |
| GPU | **1× NVIDIA RTX A6000 (49 GB)** |
| Driver / CUDA | 570.211.01 / CUDA 12.8 |
| SLURM | slurm-wlm 21.08.5 — **1 partición `debug` (default), 1 nodo (este host)** |
| Conda env de CLAM | **`clam_latest`** (NO `base`, NO `memoriaSebaDonoso`) |

> **`which python` está ROTO** en el PATH base (apunta a un ADFRsuite
> python2.7 sin libpython), y **`conda activate clam_latest` NO lo
> arregla** — ADFRsuite va *prepended* al PATH por delante del env conda.
> Atención: ver Workarounds operativos del servidor Environ → Workaround B
> para el procedimiento correcto (usar el binario absoluto del env).

### Paths críticos

```
/media/administrador/Storage1/sdonoso/
├── clam_environ/        ← CODEBASE CLAM de Sebastián. READ-ONLY. No tocar.
│   └── environ/         ← DATOS del proyecto (features .pt, CSVs, splits). READ-ONLY.
├── clam_testing/        ← workspace de OTRA persona. NO entrar a escribir.
└── clam_testing2/       ← MI workspace (todo lo mío vive acá; ver "Workspace containment")
    ├── oncomets-ernesto/        ← este repo
    └── CLAM_official_reference/ ← CLAM oficial Mahmood Lab (REFERENCE ONLY — not in PYTHONPATH)
```

- **Codebase compartido (READ-ONLY)**: `/media/administrador/Storage1/sdonoso/clam_environ/`
- **Datos compartidos (READ-ONLY)**: `/media/administrador/Storage1/sdonoso/clam_environ/environ/`
- **Mi workspace**: `/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/`
- **CLAM oficial (REFERENCE ONLY)**: `/media/administrador/Storage1/sdonoso/clam_testing2/CLAM_official_reference/`
  — repo Mahmood Lab clonado como referencia y fuente de `create_heatmaps.py`.
  HEAD `53e2409` (19 may 2026). **NO se agrega al PYTHONPATH, NO se mezcla ni
  se importa cruzado con el codebase de Sebastián.** Solo lectura/consulta.

## Workarounds operativos del servidor Environ

Consolidación de problemas recurrentes encontrados durante el Sprint 4
y sus fixes verificados. Si tropezás con alguno de estos síntomas,
aplicar el fix correspondiente sin investigar de nuevo.

### A. El filesystem `/dev/sdb` no preserva permisos POSIX

- **Síntoma**: `git status` marca el árbol entero como modificado (cambios
  de modo); `git push` falla con `Bad owner or permissions on
  ~/.ssh/config`.
- **Causa**: el filesystem donde vive todo (`/dev/sdb`) no preserva los
  permisos POSIX — los flipea a `0777`.
- **Fix**: para el repo, `git config --local core.fileMode false` (ya
  seteado). Para `~/.ssh/`, ver workaround F + "Reglas de commit y push".

### B. `which python` no refleja `conda activate clam_latest`

- **Síntoma**: tras `conda activate clam_latest`, `which python` sigue
  apuntando al ADFRsuite python2.7 roto (`error while loading shared
  libraries: libpython2.7.so.1.0`).
- **Causa**: ADFRsuite va *prepended* al `PATH` por delante del env conda;
  `conda activate` no lo desplaza.
- **Fix**: usar SIEMPRE el binario absoluto del env —
  `/home/sdonoso/miniconda3/envs/clam_latest/bin/python` — en todos los
  `.slurm` y en cualquier verificación. No confiar en `python` a secas.

### C. `sacct` deshabilitado en este SLURM

- **Síntoma**: `sacct` no devuelve historial de jobs.
- **Causa**: el accounting de SLURM no está habilitado en este cluster.
- **Fix**: no hay post-mortem vía `sacct` — la única traza de un job son
  sus `.out`/`.err`. **Nada se borra de `logs/` ni `results/` hasta el
  cierre del sprint.** Monitorear en vivo con `squeue -j` / `tail -f`.

### D. `cmd | head` bajo `set -euo pipefail` → exit 141 (SIGPIPE)

- **Síntoma**: un `.slurm` con `set -euo pipefail` aborta antes de
  entrenar, con exit code 141. Típico con `nvidia-smi | head` u otro
  comando de stdout grande pipelined.
- **Causa**: `head` cierra el pipe; el comando aguas arriba recibe
  SIGPIPE; `pipefail` propaga el 141 y `-e` aborta el script.
- **Fix**: en diagnósticos pipelined, `cmd | head -N || true` (commit
  `5122ebf`).

### E. `/mnt/project/` no existe en este server

- **Síntoma**: se busca un paper o artefacto en `/mnt/project/` y no está.
- **Causa**: `/mnt/project/` pertenece al entorno claude.ai, no a este
  server.
- **Fix**: los papers y artefactos del proyecto viven en `papers/`,
  `sprints/`, `docs/` del repo personal. No descargar nada de afuera: si
  falta algo, reportarlo y que Ernesto lo suba.

### F. `git push` por SSH

- **Síntoma**: `git push` falla con `Bad owner or permissions on
  ~/.ssh/config`.
- **Causa**: el flip de permisos del workaround A deja `~/.ssh/config` y
  la clave privada en `0777`; SSH los rechaza por inseguros.
- **Fix**: aplicar `chmod 600 ~/.ssh/config ~/.ssh/id_ed25519` (ver
  "Reglas de commit y push"). Verificar auth con
  `ssh -T -p 443 git@ssh.github.com` → debe responder `Hi ernestoelo!`.
  El bloque `Host github.com` de `~/.ssh/config` redirige el puerto
  22 → 443.

### G. Preflight check obligatorio en `.slurm` de entrenamiento

- **Síntoma**: jobs que crashean **tarde** (tras horas de entrenamiento)
  por bugs de datos — ej. el bug `topk` (run 4096): slides con menos
  parches que `k_sample` (`--B`) en `inst_eval` de CLAM.
- **Causa**: `--weighted_sample` muestrea con reemplazo; una slide
  problemática puede no aparecer hasta una época avanzada → el crash es
  tardío y el debug, largo y caro.
- **Fix**: bloque **preflight** en el `.slurm`, **antes de `python
  main.py`**, que ejecute un script validando invariantes del
  split/dataset. `scripts/preflight_minpatch.py` es el ejemplo de
  referencia (valida nº mínimo de parches por slide de train). Si el
  preflight falla, el job termina en segundos en lugar de horas. **Patrón
  obligatorio** en cualquier `.slurm` de entrenamiento futuro, de
  cualquier task — no es específico de microcalcificaciones ni de
  `minpatch`. Ver detalle del bug en `docs/workarounds.md` y la plantilla
  en la skill `@slurm-submission`.

### Reglas de commit y push para Claude Code

- **Commits locales**: SÍ — granulares, mensajes conventional commits.
- **`git push`**: NO autónomo. Solo cuando el prompt de la sesión lo pida
  explícitamente. Default = "commits locales, push lo hace Ernesto".
- **`git config --global`**: NUNCA. Solo `--local` al repo (ver regla 8).
- **Verificar la rama ANTES de cada commit**: `git branch --show-current`.
  El working tree es compartido (user `sdonoso`) y puede haber quedado en
  otra rama por una sesión paralela. No asumir que la rama checked out es
  la correcta.
- **Si el prompt de la sesión NO especifica la rama destino**: PREGUNTAR
  antes de commitear. No improvisar. (Lección Sprint 4: c1-c5 quedaron en
  la rama equivocada y requirieron `reset` + `cherry-pick` para corregir.)
- **Cambios estructurales** (rename de directorio, mover archivos a otro
  path, reorganización): decidir **explícitamente** si se replican a `main`.
  Si se replican, hacerlo en el mismo turno
  (`git checkout main && git mv ... && git commit`). Si no, documentar la
  divergencia como intencional. Un rename en una rama **no** se propaga
  solo a las demás.
- **Después de cada `cherry-pick`**: `git status` — un cherry-pick puede
  arrastrar staged changes no intencionados; verificar que solo se movió
  lo esperado.
- **Si `push` falla con `Bad owner or permissions on ~/.ssh/config`**:
  permitido aplicar `chmod 600 ~/.ssh/config ~/.ssh/id_ed25519` como
  **excepción quirúrgica** al containment. **NO** copiar claves, **NO**
  modificar `~/.gitconfig`, **NO** tocar nada más en `~/.ssh/` ni fuera
  de `~/.ssh/` de `sdonoso`.
  - *Por qué es legítima*: las claves `~/.ssh/id_ed25519` fueron generadas
    por Ernesto el 19-may-2026 para su cuenta GitHub `ernestoelo`. Aunque
    viven en el home del user compartido `sdonoso`, son funcionalmente del
    usuario operativo (Ernesto) en este server. Por eso `chmod 600` sobre
    *ellas específicamente* es excepción quirúrgica autorizada y no viola
    el containment.
- **Si `push` falla por otra razón**: detenerse y reportar a Ernesto.

## Workspace containment (regla dura — Sprint 4 en adelante)

**TODO lo que descarguemos, clonemos, generemos o produzcamos vive bajo
`clam_testing2/`. Sin excepción.** Jamás en `/home/`, `/tmp/` persistente, ni
`clam_environ/`.

- Repos clonados (CLAM oficial; futuros DSMIL, etc.) → `clam_testing2/<nombre>/`.
- Resultados de entrenamiento → `clam_testing2/oncomets-ernesto/results/`.
- Logs SLURM (`.out`, `.err`) → `clam_testing2/oncomets-ernesto/logs/`.
- Checkpoints, modelos, `summary.csv`, `*_results.pkl` → idem `results/`.
- Heatmaps y figuras → `clam_testing2/oncomets-ernesto/sprints/<sprint>/`.
- Temporales, cache, env personal si hace falta → bajo `clam_testing2/`.

**Implicación para los `.slurm`**:
- `--output`, `--error`, `--chdir` → siempre **paths absolutos dentro de
  `clam_testing2/`**.
- `--results_dir` de `main.py` → siempre **absoluto dentro del repo personal**.
- Si al auditar `main.py` aparecen outputs a paths relativos al CWD (logs
  extra, plots, tensorboard, wandb local), **reportarlo antes de lanzar** —
  preferir `--chdir` al repo personal u overrides explícitos antes que confiar
  en defaults. (Nota: `--chdir` al repo personal puede romper paths relativos
  de `main.py` como `environ/...`; si es el caso, usar paths absolutos en los
  args y `--chdir` al codebase, pero mandar TODO output a `clam_testing2/` vía
  args absolutos. Resolver caso por caso y documentar.)

### Estructura del codebase de Sebastián (`clam_environ/`, READ-ONLY)

```
clam_environ/
├── main.py                      # entrypoint training (TASK_CONFIGS con 38 tasks, --auto-label-dict)
├── eval.py                      # evaluación de checkpoints
├── create_splits_seq.py         # ← genera splits (no los crees a mano)
├── extract_features_fp.py       # ← extracción de features CONCH (job conch_fe)
├── extract_features.py / extract_supervised_features.py
├── create_patches_fp.py / create_patches.py   # tessellation de WSI
├── create_heatmaps.py           # heatmaps de attention
├── obtener_parches_relevantes.py
├── environ_utils.py             # genera CSVs de labels desde JSON de WSIs
├── run_all_training.sh          # ← loop de training de Sebastián (embed_dim 512)
├── run_training.slurm / train_task.slurm / run.slurm / run_main.slurm
├── run_extract_features.slurm   # ← CONCH feature extraction
├── run_eval_comparative.slurm   # ← eval privado vs combined
├── create_splits_new_tasks.slurm
├── environment.yml / readme_environ.md / index_CAP_environ.md / openslide_solution.md
├── models/
│   ├── model_clam.py            # ← CLAM_SB y CLAM_MB
│   ├── model_mil.py, builder.py, resnet_custom_dep.py, timm_wrapper.py
├── utils/
│   ├── core_utils.py            # ← train loop con instance loss
│   ├── eval_utils.py, file_utils.py, constants.py, transform_utils.py, utils.py
├── dataset_modules/             # dataset_generic.py, dataset_h5.py, wsi_dataset.py
├── wsi_core/                    # WholeSlideImage.py, batch_process_utils.py, ...
├── vis_utils/, extractor_caracteristicas/, openslide/, presets/
├── dataset_csv/                 # CSVs dummy genéricos
└── environ/                     # ← DATOS del proyecto (ver abajo)
```

### Estructura de datos (`clam_environ/environ/`, READ-ONLY)

```
environ/
├── features/pt_files/        ← 2935 slides, features CONCH v1, [N_parches, 512] float32
├── features/h5_files/        ← coords/patches (h5), 2935
├── features_resnet/pt_files/ ← 344 slides, ResNet50, [N, 1024]  (LEGACY)
├── features_256/pt_files/    ← 344 slides, CONCH @ patch 256, [N, 512]
├── csv_privado/              ← labels solo Environn (~533 slides)
├── csv_tcga/ / csv_histai/   ← labels solo TCGA / solo HistAI
├── csv/                      ← labels COMBINADO (~3072), usado por tasks _combined y _pth
├── splits/<task>_100/        ← splits PRIVADO (_100 = label_frac 100%)
├── splits/<task>_combined_100/   ← splits priv+TCGA
├── splits/<task>_pth_100/    ← splits priv+TCGA+HistAI (conjunto GRANDE para pruebas finales)
└── results_modelo*/ results_eval*/   ← checkpoints, summary.csv, .pkl
```

> **No existen archivos `.pth`**. El sufijo `_pth` en tasks/splits significa
> **"privado + TCGA + HistAI"** (la unión grande), NO un archivo `.pth`.
> Las features son `.pt` individuales por slide.

## Pipeline OncoMets (referencia rápida)

```
WSI → patches → CONCH features (512-dim) → CLAM_MB → N clases clínicas
```

> **CONCH = 512-dim** para todas las slides (Environ + TCGA + HistAI). El
> 1024-dim corresponde a las features ResNet legacy. **Usar `--embed_dim 512`.**

## Workflow operativo SLURM

Toda submission que use GPU va por **`sbatch <archivo>.slurm`**, **nunca**
`python` directo en GPU. (En recon read-only ni siquiera eso — solo lectura.)

### Antes de cada `sbatch` (regla de cortesía)

GPU **única** (RTX A6000) y partición **única** (`debug`). No hay GPU de
respaldo como en Werner. Antes de enviar un job grande:

```bash
squeue                  # ¿hay jobs de otros (o el conch_fe de Sebastián) pendientes?
squeue -u $USER         # ¿tengo algo ya en cola?
sinfo                   # estado del nodo
```

Si hay jobs ajenos pendientes por `Resources`, **no monopolizar** — esperar
o coordinar.

### Plantilla mínima `.slurm` (espejo de `run_training.slurm`, con MIS paths)

```bash
#!/bin/bash
#SBATCH --job-name=eg_train
#SBATCH --output=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/logs/%x_%j.out
#SBATCH --error=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/logs/%x_%j.err
#SBATCH --chdir=/media/administrador/Storage1/sdonoso/clam_environ
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=16
#SBATCH --mem=32G
#SBATCH --time=48:00:00
# (sin --partition → usa la default 'debug')

source $(conda info --base)/etc/profile.d/conda.sh
conda activate clam_latest

CUDA_VISIBLE_DEVICES=0 python main.py \
    --task <task> --exp_code <exp> \
    --split_dir environ/splits/<task>_100 \
    --data_root_dir environ/ --results_dir environ/results_modelo \
    --drop_out 0.25 --lr 2e-4 --bag_loss ce --inst_loss svm \
    --model_type clam_mb --embed_dim 512 --k 1 \
    --early_stopping --weighted_sample --auto-label-dict --log_data
```

> Skill asociada: `@slurm-submission` (`.claude/skills/slurm-submission/`).

### Monitoreo / cancelación

```bash
squeue -j <jobid>
tail -f logs/<job>_<jobid>.out
scancel <jobid>          # cancelación segura de MIS jobs
```

## Reglas operativas no negociables

1. **NO `sbatch` / `srun` / GPU** en sesiones de recon o exploración. Cero
   entrenamientos sin que Ernesto lo pida explícitamente.
2. **NO modificar** nada bajo `clam_environ/` — codebase y datos de
   Sebastián, **read-only absoluto**. Cambios de comportamiento → wrapper o
   copia local en mi workspace.
3. **NO entrar a escribir** en `clam_testing/` — workspace de otra persona.
4. **NO escribir/mover/borrar fuera** de
   `clam_testing2/oncomets-ernesto/`.
5. **Validación factual**: toda afirmación técnica se valida contra el paper
   original y/o el código real en `clam_environ/`. Si no está en ninguno:
   "no encontrado", no inventar.
6. **Referenciar líneas exactas** (`models/model_clam.py:107`). Si la línea
   cambió, actualizar `docs/codebase_map.md`.
7. **No inventar resultados experimentales**. Si una métrica no está en los
   logs, decirlo.
8. **Git config LOCAL, nunca global.** El `git config --global` del usuario
   compartido `sdonoso` apunta a **Seba Donoso** (`ssebastiandonoso@gmail.com`).
   Mi identidad va **local** en el repo:
   - `user.name = "Ernesto Gamero"`
   - `user.email = "ernesto.gamero@sansano.usm.cl"`
9. **Argumento antes de código** (regla nueva, Sprint 4, feedback de Benjamín
   12 may 2026). Toda propuesta de implementación o módulo nuevo viene con
   justificación **clínica o arquitectónica explícita** ANTES de tocar
   código. Una ablation cuenta como argumento sólido **solo si**:
   - La **hipótesis** está enunciada de antemano (qué se espera observar y
     por qué, en términos del mecanismo del modelo o del fenómeno clínico).
   - La **métrica de éxito** está predefinida (qué número, sobre qué subset,
     con qué dirección de cambio).

   Si un cambio toca `model_*.py`, `core_utils.py` o el training wrapper sin
   cumplir esto, el agente `reviewer` bloquea el commit.

10. **Antes de confiar en `splits_0_descriptor.csv`**, cross-check con el
    join `splits_0.csv ⨯ dataset_<task>_label.csv` (ver Hallazgos).

## Args bendecidos por Sebastián (de `run_all_training.sh` real)

```
--drop_out 0.25
--lr 2e-4
--bag_loss ce
--inst_loss svm
--model_type clam_mb
--embed_dim 512              # CONCH (1024 era ResNet legacy)
--k 1                        # un solo fold
--early_stopping
--weighted_sample            # corrige desbalance de clases
--auto-label-dict            # genera label_dict desde el CSV de labels
--log_data
```

`--bag_weight` (default 0.7) y `--B` (default 8) no se pasan explícitos. Si
un sprint los varía, especificarlos.

## Pedagogía de CSVs

Cualquier CSV / artefacto tabular que entra o sale del pipeline se documenta
con este formato fijo. Aplica al introducir un CSV nuevo y para auditar uno
existente. Skill asociada: `@csv-audit`.

```
CSV: <nombre exacto del archivo>
Path en server: <absoluto, bajo clam_environ/environ/...>
Schema (columnas y tipos):
  - col_1: tipo, ejemplo, qué representa
  - col_2: ...
Filas: <cuántas hay o se esperan>
Producido por: <script o paso>
Consumido por: <script o paso>
Ejemplo (head -3): ...
Trampas conocidas: <ej. descriptor stale, label_dict bugs>
```

**Práctica complementaria**: snapshot del CSV al workspace local del sprint
(`sprints/<sprint>/<objetivo>/csv_snapshots/`) — el archivo en el server
puede mutar; el snapshot versionado es la verdad de referencia durante el
sprint.

### CSVs canónicos del pipeline OncoMets

| CSV | Productor | Consumidor | Sirve para |
|---|---|---|---|
| `dataset_<task>_label.csv` | `environ_utils.py` / equipo | `main.py` vía `Generic_MIL_Dataset` | mapear `slide_id` → label por task |
| `splits_0.csv` | `create_splits_seq.py` | `main.py` | partición train/val/test (**verdad de campo**) |
| `splits_0_bool.csv` | `create_splits_seq.py` | exploración manual | versión booleana del split |
| `splits_0_descriptor.csv` | `create_splits_seq.py` | reporte (puede estar **stale**) | conteo por clase del split |
| `summary.csv` | `core_utils.py` (fin) | post-hoc | `test_auc/acc`, `val_auc/acc` por fold |
| `split_0_results.pkl` | `core_utils.py` | post-hoc | predicciones por slide |

## Hechos validados contra el código real (19 may 2026, server Environ)

Números de línea del codebase actual en `clam_environ/`. Si Sebastián edita,
re-validar y actualizar `docs/codebase_map.md`.

### `models/model_clam.py`

- **Dos clases**: `CLAM_SB` y `CLAM_MB`. OncoMets usa `CLAM_MB`.
- `self.subtyping = subtyping`: **L96** (CLAM_SB), **L205** (CLAM_MB).
- `inst_eval`: **L107**; `inst_eval_out`: **L128**. Operan sobre el subset
  top-B/bottom-B de parches, NO sobre los N totales.
- Attention pooling `M = torch.mm(A, h)`: **L172** (CLAM_SB), **L239**
  (CLAM_MB). Usa **todos los N parches**.

### `utils/core_utils.py`

- `train_loop_clam`: **L241**.
- `instance_loss = instance_dict['instance_loss']`: **L266**.
- `total_loss = bag_weight * loss + (1-bag_weight) * instance_loss`: **L271**.
- `bag_weight` default 0.7 (slide-level 70% / instance 30%).
- "clustering loss" en prints == instance loss.

### `main.py`

- Parser de args desde **L446**. Defaults: `embed_dim=1024`, `lr=1e-4`,
  `max_epochs=200`, `bag_weight=0.7`, `B=8`, `model_type=clam_sb`, `k=10`.
  (Los `.slurm`/`.sh` reales sobre-escriben con los args bendecidos.)
- Toma **`--split_dir`**, NO `--csv_path`.
- `TASK_CONFIGS`: 38 tasks. Variantes `_combined` (priv+TCGA) y `_pth`
  (priv+TCGA+HistAI) con `label_dict={}` → requieren `--auto-label-dict`.
- `--auto-label-dict` genera el `label_dict` ordenando alfabéticamente los
  labels únicos del CSV → **sobre-escribe** los `label_dict` hardcoded (que
  están stale respecto a los CSVs reales).
- `--pretrain_path`: warm-start desde un checkpoint CLAM (capas con nombre y
  shape compatibles se transfieren).

## Hallazgos vigentes (relevantes para sprints)

1. **`splits_0_descriptor.csv` puede estar stale.** Regla: verdad de campo =
   join `splits_0.csv ⨯ dataset_<task>_label.csv`. **En las 4 tareas
   prioritarias del Sprint 4 el descriptor está en sync** (verificado
   19 may 2026) — el caso stale del Sprint 3 (`grado_general`) no se
   reproduce; probablemente regeneraron los splits.
2. **Bug `invasion_linfatica_vascular` RESUELTO.** Labels ahora limpias
   `{ausente, no_identificado, presente}`. El typo `'no identificada'` vs
   `'no identificado'` del Sprint 3 ya no está. La task vuelve a ser usable.
3. **Clases minoritarias quedan enteras en train** con `val_frac=test_frac=0.1`.
   Genera AUC vacíos/`nan`. Evaluar sobre el subset binario efectivo o
   regenerar con stratification.
4. **Bag loss puede no converger en datasets pequeños** cuando
   `--auto-label-dict` registra clases que el modelo nunca ve en val/test.
   El instance loss SmoothTop1SVM sí converge. Fragilidad del slide-level
   classifier, no del pseudo-etiquetado.
5. **Severo desbalance** en las prioritarias (ej. `gh_dif_tubular` score_1=4
   en train; `cdi_necrosis` presente_focal=1) — probable causa del AUC bajo.
6. **Régimen de evaluación roto en `microcalcificaciones_pth`** (confirmado
   empíricamente, baseline B=8 job 4098, 21 may 2026). 8 clases; 4 con **1
   sola muestra** en val/test → el macro-AUC (`nanmean` one-vs-rest) está
   dominado por ruido: el job dio val_auc 0.69 < test_auc 0.81 (inversión =
   prueba de inestabilidad). `test_acc` 0.72 cae *bajo* el baseline trivial
   (0.89). **Métrica honesta = balanced accuracy** (job 4098: 0.31) **+ matriz
   de confusión, siempre con el `n` por clase**. El macro-AUC solo, nunca.
   Detalle: `sprints/B4_sprint4/objetivo_1_baseline/resultados.md`.
7. **Las 8 clases de microcalcificaciones son un problema multi-label
   aplastado.** Son las combinaciones de 3 tejidos {carcinoma invasivo, CDIS,
   tejido no neoplásico} + `no_identificado`. Aplastar multi-label en
   clases-combinación fabrica clases ultra-raras (la triple: 6 slides).
   Propuesta para la reunión: reformular como 3 tareas binarias. Entrenar con
   el dataset grande (`_pth`, 3072) NO ayuda al desbalance — la expansión vs
   V4 (n=548 ≈ cohorte privada 533, ver Hallazgo 10) fue casi toda
   `no_identificado` (2739/3072); las clases raras siguen fijas (6–161 slides).
8. **`B` no es la palanca (ablación Obj 2, jobs 4098 vs 4099).** Doblar `--B`
   (8→16) sobre `microcalcificaciones_pth` dio Δtest_auc +0,009 (umbral
   predefinido +0,03 → banda ambigua), **balanced accuracy BAJÓ** 0,31→0,24 y
   `train_clustering_loss` SUBIÓ 0,0089→0,0126 (contradice el mecanismo de la
   hipótesis). Lección: ajustar hiperparámetros no mueve la aguja — el cuello
   de botella es la **FORMULACIÓN** de la tarea. Detalle:
   `sprints/B4_sprint4/objetivo_2_ablation_B/resultados.md`.
9. **Reformulación en 3 binarios: NO es hallazgo nuestro — es trabajo previo
   de Sebastián que reprodujimos (confirmado en reunión 22 may 2026).**
   Sebastián ya había des-aplastado las 8 clases en 3 preguntas binarias hace
   tiempo; la infra (tasks
   `microcalcificaciones_en_{carcinoma_invasivo,cdis,tejido_no_neoplasico}_pth`
   + variantes `_pth_balance` en `main.py`; 3 CSVs binarios en `environ/csv/`,
   333 slides, `no_identificado` **excluido** → positivos 68/121/195,
   verificado determinísticamente con
   `scripts/verify_binary_microcalc_csvs.py`; 3 splits estratificados) es de
   él. Nuestro aporte real es el **diagnóstico** (régimen de eval roto +
   ablación B negativa) y la **reproducción/validación independiente**: dimos
   con su CSV y replicamos sus resultados. **Comparación en la reunión: igualamos
   en carcinoma invasivo y obtuvimos métricas algo MEJORES que las de él en CDIS
   y tejido no neoplásico.** Resultados nuestros (job 4109, CLAM_MB, B=8,
   `--max_epochs 30`, CONCH 512): carcinoma invasivo balanced acc **0,78**
   (umbral 0,60 ✅), CDIS 0,59, tejido 0,58 (apenas sobre el piso 0,50). El
   régimen de eval pasó de "no medible" (clases n=1) a confiable (7–20
   positivos/test). PRELIMINAR (1 semilla). Detalle:
   `sprints/B4_sprint4/reformulacion_multilabel/`.
10. **Reunión 22 may 2026 — dirección del sprint y reglas de dataset.** Acordado
   con Sebastián + Eduardo:
   - **Dataset de trabajo para microcalcificaciones = ~548 slides, NO el
     universo `_pth` (3072).** Verificado determinísticamente (read-only) el
     22 may: el ~548 del doc V4 ≈ **cohorte PRIVADA** `microcalcificaciones_100`
     = **533 slides hoy** (deriva de snapshot de 15 vs V4). Mapa de tamaños:
     privado 533 · combined (priv+TCGA) 1397 · `_pth` (priv+TCGA+HistAI) 3072 ·
     binarios identificados (`no_identificado` excluido) 333. Regla: entrenar
     solo con las slides de interés (≈548); **el universo completo (3072) se
     reserva para las PRUEBAS FINALES** de una incorporación.
     **Matiz crítico:** el "~548 privado" aplica al **8-clases**. Para los **3
     binarios** (`no_identificado` excluido) lo útil son las **identificadas**:
     privado solo 77 → inentrenable; combined 284; `_pth` 333. Los binarios
     necesitan combined/`_pth`-identificado, NO privado solo. Cuentas, paths y
     decisión por escenario: `sprints/B4_sprint4/dataset_microcalcificaciones.md`.
   - **`balanced_pth_100` (en construcción por Sebastián):** dataset donde la
     mayoritaria (`no_identificado`) no supera a la minoritaria por más de 10×.
     **Aún no existe como split** — verificado el 22 may: `csv_balance/` y los
     splits `_pth_balance` son **byte-idénticos** a los 333 (placeholder).
     Sebastián nos invitó a entrenar sobre él cuando esté.
   - **Early stopping efectivo:** cortar cuando el modelo deja de mejorar por
     época (recordar `stop_epoch=50` hardcoded; en runs cortos usar
     `--max_epochs` < 50).
   - **Modelo alternativo (DSMIL u otro):** viable **solo con** (a) justificación
     clínica/arquitectónica para microcalcificaciones y (b) resultados
     comparativos contra nuestro baseline **sobre el mismo dataset**. Puede
     reemplazar a CLAM en una tarea o integrarse en CLAM.
   - **Factores a investigar (pedido de Sebastián):** escala / nº de parches
     (algunas tareas necesitan más contexto espacial), y features de
     **citoplasma** según la tarea. Buscar papers que evalúen tareas donde
     estamos débiles con buenos resultados y, ojalá, llegar con una
     implementación corrida para comparar contra el baseline.
   - **Pendiente de confirmar:** qué define exactamente el subconjunto de 548
     (privado 533 incluye `no_identificado`) vs los 333 identificados de los
     binarios; y qué es `no_identificado` (¿sin microcalcificación, o sin
     ubicar?).

## Entorno conda — deps esperadas

El env de CLAM es **`clam_latest`**. Las deps del Sprint 3 (validadas en
Werner sobre `memoriaSebaDonoso`) que `main.py` necesita: `h5py`,
`tensorboardX`, `topk` (smooth-topk) — requerido por `--inst_loss svm`,
`future`, `pandas>=2,<3` (pandas 3.x rompe `dataset_generic.py`).

> **No se verificó `pip list` de `clam_latest`** en esta sesión read-only (no
> se activó el env). Confirmar deps al primer uso real. Si faltan:
> ```bash
> conda activate clam_latest
> pip install h5py tensorboardX 'pandas>=2.0,<3.0' future
> pip install 'git+https://github.com/oval-group/smooth-topk.git'
> ```

## Importar `CLAM_MB` desde un script propio

Import directo (validado en Werner; re-validar en `clam_latest`):

```python
import sys
sys.path.insert(0, "/media/administrador/Storage1/sdonoso/clam_environ")
from models.model_clam import CLAM_MB
```

Si falla por `timm` en `models/__init__.py`, aplicar fallback `importlib.util`
(ver `docs/workarounds.md`). NO hace falta para correr `main.py` directo.

## Formato de entregables (regla de oro)

**Diagramas > texto plano. Siempre.** Sebastián rechaza informes de texto
plano. Estilo visual: `Modelo_OncoMets_Spatial_V1.pdf`. Estructura:
`Plantilla.pdf`.

**Speaker notes (formato fijado en B2)**: bloques `BLOQUE N — Título`,
sub-items con `-> `, fórmulas inline sin LaTeX (`h_k = ReLU(W₁·z_k)`), sin
emojis ni corchetes de gesto, destacados en línea propia (`Punto clave:` /
`Detalle crítico:`), ultra-minimalista para copy-paste a OnlyOffice.

## Subagentes disponibles

| Agente | Foco | Cuándo invocarlo |
|---|---|---|
| `trainer` | Entrenamiento end-to-end de CLAM **vía SLURM** (y wrappers, ej. DSMIL) | Tareas que tocan `main.py`, `create_splits_seq.py`, splits, lanzamiento GPU |
| `reviewer` | Validar propuestas de cambio a modelo/training contra "Argumento antes de código" | **Antes** de cualquier commit que toque `model_*.py`, `core_utils.py`, scripts de training o config. Bloquea si falta hipótesis + métrica |

## Skills cargadas en este repo

- `@slurm-submission` — plantilla `.slurm`, recursos típicos, monitoreo y la
  prohibición de python directo en GPU.
- `@environ-server` — inventario del servidor: scripts de `clam_environ/`,
  features CONCH, CSVs, splits, reglas read-only y de cortesía.
- `@csv-audit` — formato pedagógico de CSVs y cross-check contra el archivo
  físico.
- `@dev-workflow` — estructura del repo, Gitflow, validación.
- `@harness` — referencia para escalado post-sprint.

## Contexto del usuario para sesiones rápidas

Idioma: **español**. Tono: técnico + explicativo. No simplificar conceptos
generales de ML/DL/CV. SÍ explicar pedagógicamente al introducir notación
específica del subcampo (MIL, weakly-supervised, computational pathology).
