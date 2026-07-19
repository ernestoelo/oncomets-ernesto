
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
Sebastián Gaete. Senior: Benjamín. (Eduardo, colaborador, renunció el
1-jun-2026; equipo actual = Ernesto + Sebastián. Su trabajo de mammoth lo
heredó Ernesto — ver memoria `equipo-arquitecturas-mammoth-longnet`.)

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
├── clam_testing/        ← workspace COMPARTIDO y activo (owner sdonoso; Sebastián/sgaete y otros corren ahí). Read-only por defecto; escribir solo si Sebastián lo pide (regla 3.a).
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

### H. NO mover el working-tree mientras un job corre (árbol compartido)

- **Síntoma**: un job SLURM que arrancó OK crashea a mitad de camino con
  `FileNotFoundError` (o, peor, produce resultados con código mezclado sin
  avisar). Caso real: job 4241 (Obj2), un `git checkout` a otra rama durante
  el job borró `data/csv_new_tasks/*.csv` → fold 1 murió (solo 1/40 runs).
- **Causa**: el `.slurm` invoca `python` **por cada run** y cada invocación
  **relee** sus inputs/código del **working-tree vivo y COMPARTIDO** (`sdonoso`).
  Un `git checkout`/branch-switch/edición de archivos versionados **mientras el
  job corre** (propio o de una sesión paralela) le cambia el piso al job.
- **Fix**: con un job en curso, **NO cambiar de rama ni editar archivos
  versionados** del árbol. Antes del `sbatch`, asegurar que **todos los inputs
  del job (CSVs, splits, scripts) estén commiteados en la rama que queda
  checked-out** — idealmente correr desde `main`. Verificar `squeue` (jobs
  propios y ajenos) antes de tocar `git`. Memoria
  [[working-tree-compartido-job-en-curso]]. (Refuerza la regla de commit "el
  working tree es compartido, verificá la rama" — acá el riesgo es contra el
  job, no contra el commit.)

### I. `create_patches_fp --process_list` crashea con slide_id numéricos

- **Síntoma**: patching que corre OK en TCGA pero **falla en toda la cohorte
  privada** con `AttributeError: 'numpy.int64' object has no attribute 'replace'`
  (status `failed` en el log, no en el preflight).
- **Causa**: `create_patches_fp.py` re-lee el `--process_list` con
  `pd.read_csv` **sin `dtype`**; los `slide_id` privados **numéricos puros**
  (`105040`) se infieren `int64` → `get_clean_slide_name` llama `.replace` sobre
  un int (`environ_utils.py:182`). TCGA se salva (IDs con letras).
- **Fix** (clam_environ es read-only → no se puede parchear el `read_csv`): para
  restringir el set NO usar `--process_list`; construir un **symlink-farm plano**
  por cohorte (una symlink por WSI del piloto bajo `clam_testing2/`) y correr
  `create_patches_fp` con `--source <farm>` **sin `--process_list` ni
  `--nested_folders`** (modo flat → nombres string desde `os.listdir`). Cazado por
  el dry-run del gate (c) del B6 (10-jul). Memoria
  [[create-patches-processlist-int64-privado]].

### J. Un proceso CPU largo lanzado desde la sesión muere al cerrarla

- **Síntoma**: un driver CPU post-hoc (interpretabilidad, análisis) que corre
  horas aparece muerto al retomar, con el progreso perdido entero.
- **Causa**: no es SLURM, así que no tiene la protección de un job — cuelga del
  proceso `claude`, que cuelga de la extensión de VSCode. Cerrar la sesión se
  lleva la cadena. Cazado 2 veces sobre `run_b7_expert_interp.sh` (18-jul).
- **Fix**: lanzarlo **desatado** y hacerlo **reanudable**:
  ```bash
  setsid nohup bash scripts/<driver>.sh > logs/<driver>_desatado.log 2>&1 < /dev/null &
  ```
  Verificar `ps -eo pid,ppid,sid,cmd` → **ppid = 1**. El driver debe saltar el
  trabajo hecho marcándolo con el artefacto que se escribe **al final** (uno
  intermedio daría por completa una corrida cortada a mitad). Gotchas al matar y
  relanzar (exit 144 del harness, hijos huérfanos, `pgrep` que se auto-matchea)
  en la memoria. Detalle: [[proceso-cpu-largo-desatado-setsid]].

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
- **`.claude/settings.json` es LOCAL por usuario** (ignorado por
  `.gitignore` desde commit `7359c2f`, 28-may-2026). Acumula permisos
  pre-aprobados durante el uso — allow-list de comandos one-shot, paths
  absolutos a `$HOME`/`$TMP`, IDs de jobs ya cerrados. NO es config del
  proyecto; cada sesión nueva reconstruye su allow-list naturalmente. Si
  alguna sesión cree que necesita un baseline compartido, crear
  `.claude/settings.json.example` curado a mano. Las memorias persistentes
  viven en `~/.claude/projects/<hash-path>/memory/` y están segregadas
  por path-de-repo (verificado 28-may, ver
  `sprints/B4_sprint4/diseño_memoria_versionada.md` §0) — cero
  contaminación entre operadores del server compartido.

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

**Al cerrar un objetivo del sprint** (regla operativa, post Obj 5):
ejecutar `git add results/<objetivo>/` para versionar la **verdad de
campo chica** (predicciones por slide `*_results.pkl`, `summary.csv`,
config snapshots, métricas per-fold). El `.gitignore` ya excluye los
artefactos pesados (`*.pt`, `*.pth`, `*.h5`, `checkpoints/`,
`events.out.tfevents.*`), así que un `git add results/<obj>/` plano es
seguro. Esto deja la verdad de campo citable por los `resultados.md` y
sobrevive a una pérdida del workspace. Detalle del checklist:
`.claude/skills/dev-workflow/references/checklist.md` §13.

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
├── features/pt_files/        ← ~3013 slides (live 5-jun-2026; crece, `ls|wc -l`), features CONCH v1, [N_parches, 512] float32
│                               ⚠ dir LIVE que MUTA: TCGA re-extraído 26-27 jun = PARCHE DE MAGNIFICACIÓN de Sebastián (448px@×40→224
│                               para igualar el campo físico a ×20); backup de las viejas 224@×40 en features_tcga_224x40/ (864). Checkpoints
│                               pre-27jun usan las viejas → re-inferir hoy DIVERGE del .pkl congelado; re-entrenar ([[features-tcga-drift-reextraccion]])
├── features/h5_files/        ← coords/patches (h5), ~3013
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
>
> **Magnificación física ≠ igual entre cohortes** (verificado openslide 10-jul-2026,
> [[cohortes-magnificacion-fisica]]): a `level0` **TCGA ≈ 40× (0.2325 µm/px)**, **privado ≈ 20×
> (0.465 µm/px)**, **HistAI sin MPP confiable** (generic-tiff, placeholder; no recuperable → excluido del
> piloto multi-escala, minoría; ver `magnificacion_microcalc/histai_magnificacion.md`). El pipeline actual extrae a `patch_level=0` → un
> parche 256 px mide **59 µm en TCGA vs 119 µm en privado** (confound latente: a CONCH se le da TCGA
> a ~40×, 2× su nativo). **Cualquier re-extracción / pirámide multi-escala se parametriza en µm/px
> físicos, NO en `level`.** (Contexto: eje magnificación B6, `sprints/B6_sprint6/magnificacion_microcalc/`.)

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

## Patrones operativos para experimentos

Decisiones de diseño experimental que sobreviven sprints. No son
workarounds del server (esos están más arriba): son patrones que
estructuran cómo se diseñan los experimentos comparativos del proyecto.

### P1. Comparación pareada vía reuso de splits

**Cuándo aplica**: cualquier experimento que compare arquitectura,
hiperparámetro o configuración **contra un baseline ya corrido con
MC-CV / k-fold** (típicamente: variante X vs baseline Y sobre la misma
tarea/dataset).

**Regla operativa**: el `.slurm` del experimento nuevo apunta
**exactamente al mismo `--split_dir`** que el baseline. NO regenerar
splits ni usar splits "equivalentes" con la misma semilla. La
comparación queda **pareada por construcción** (Δ por fold = nuevo_i −
baseline_i, sin confound de sorteo) y la varianza inter-fold se cancela
parcialmente en el Δ → señales chicas pero reales se vuelven
detectables.

**Por qué**: MC-CV / k-fold producen test sets correlacionados (en MC-CV
explícitamente solapados). Si el experimento nuevo regenera splits, el Δ
pareado no se puede construir, y el Δ unpaired queda dominado por la
varianza inter-fold (enorme con n chico — Fase 0 del Obj 5: carcinoma
0.732 ± 0.167 single-split). Reusando splits, **la diferencia de sorteo
se cancela en el Δ pareado** y queda solo el efecto de la variable de
estudio.

**Caso de referencia**: anexo Obj 5 (job 4179, 28-may-2026) reusó los
splits del job 4170 (CLAM Fase 0). Δ pareado por fold reveló en CDIS
regresión leve consistente (Δ bal_acc −0.053 ± 0.026, 5/5 folds
negativos) que el Δ unpaired hubiera aplastado en ruido. Detalle del
patrón: skill `@slurm-submission` (sección "Comparación pareada por
reuso de splits") y memoria
[[patron-paired-comparison-reuso-splits]].

**Cómo documentarlo en la hipótesis**: declarar `**Comparación**:
paired vs <job baseline> reusando `<path/al/split_dir>`` antes del
sbatch. El reviewer lo verifica como parte del checklist.

## Reglas operativas no negociables

1. **NO `sbatch` / `srun` / GPU** en sesiones de recon o exploración. Cero
   entrenamientos sin que Ernesto lo pida explícitamente.
2. **NO modificar** nada bajo `clam_environ/` — codebase y datos de
   Sebastián, **read-only absoluto**. Cambios de comportamiento → wrapper o
   copia local en mi workspace.
3. **NO entrar a escribir** en `clam_testing/` por defecto — es un workspace
   **compartido y activo** (owner `sdonoso`; Sebastián/`sgaete` y otros corren jobs
   ahí, NO es una carpeta durmiente "de otra persona" ni "ex-Eduardo"; el `MAMMOTH/`
   legacy de Eduardo convive con trabajo vivo del resto). Read-only salvo 3.a.
   - **3.a — Excepción quirúrgica autorizada por Sebastián.** Si Sebastián pide
     **explícitamente** dejar un entregable puntual en `clam_testing/` (precedente:
     `clam_testing/README.md` con los resultados k=5, 8-jun-2026), se permite escribir
     **solo ese archivo** — mismo molde que la excepción `chmod 600 ~/.ssh/...` (Reglas
     de commit y push): acotada a *ese* objetivo, NO abre clam_testing a escritura libre.
     **NO** se commitea en el git de clam_testing (repo ajeno). El árbol es compartido y
     con jobs vivos → aplica workaround H (no cambiar de rama / no tocar archivos que lean
     jobs en curso). La **fuente canónica/versionada** de cualquier doc así vive SIEMPRE en
     este repo (`oncomets-ernesto/`); la copia en clam_testing es derivada. Surfacear +
     confirmar antes de escribir. Memoria [[clam-testing-workspace-compartido]].
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
   - La **métrica de éxito** está predefinida (qué métrica, sobre qué subset,
     con qué **dirección de cambio** esperada).

   Si un cambio toca `model_*.py`, `core_utils.py` o el training wrapper sin
   cumplir esto, el agente `reviewer` bloquea el commit.

   **9.a — "Métrica predefinida" ≠ "umbral mágico de pass/fail"** (aclaración
   2-jun-2026, B5 — memoria `eval-reporte-auc-y-umbrales-obj6`). "Predefinida"
   exige la **métrica + el subset + la dirección esperada** y cómo se
   interpretaría el resultado (consistencia de signo a través de folds, magnitud
   de la varianza, si supera el trivial). **NO** exige un número-gatillo que
   dispare "éxito/regresión" mecánicamente. Un GO/NO-GO numérico rígido (ej.
   `Δ≥+0.03 ⇒ éxito`) es **opcional**, no obligatorio, y con n chico + varianza
   alta puede ser **contraproducente** (fuerza un veredicto binario sobre ruido).
   Pre-registrar *"espero Δ pareado >0 consistente en signo; un Δ<0 consistente
   sería regresión; varianza que cruza 0 = ambiguo"* **cumple regla 9**. El caso
   de referencia es el Obj 6 (mammoth, 2-jun): se retiró su gate `0.03/0.05/4-de-5`
   conservando la métrica + dirección pre-registradas (ver
   `sprints/B4_sprint4/objetivo_6_mammoth/README.md` §ADDENDUM). Esto NO relaja
   9.b: una decisión revisitada sigue exigiendo hipótesis pre-registrada (primaria
   + alternativa + regresión) con métrica y dirección — solo aclara que el
   "umbral numérico" puede ser una dirección esperada interpretada, no un gate
   automático.

   **9.b — Decisiones revisitadas** (ampliación post-Obj 5 ANEXO,
   28-may-2026). Reabrir un experimento o eje que fue descartado
   explícitamente (en `ejes_futuros_*.md`, apéndice "descartado",
   `resultados.md` con veredicto NO-GO, o memoria con status
   "descartado") es legítimo **solo si** un hallazgo posterior del mismo
   sprint contradice el argumento original del descarte. La reapertura:
   - **Cita explícitamente** qué hallazgo posterior cambió la premisa
     (con job ID + número concreto, no generalidad). Si el argumento es
     "ahora tengo más confianza" o "vamos a probarlo igual" → NO se
     reabre.
   - **NO es excepción a regla 9** — sigue exigiendo hipótesis
     pre-registrada (primaria + alternativa + regresión), métrica
     decisiva, umbrales numéricos antes de tocar código.
   - **Va a branch nueva** (no mezclar con sprint en curso).
   - El agente `reviewer` (ítem 6 de su checklist) detecta el caso y
     bloquea si la cita del hallazgo habilitante no está. Caso de
     referencia: anexo Obj 5 (job 4179) reabrió DSMIL × binarias citando
     "Fase 0 invalidó single-split que sostenía el descarte original del
     4137". Ver memoria [[meta-regla-decisiones-revisitadas]].

10. **Antes de confiar en `splits_0_descriptor.csv`**, cross-check con el
    join `splits_0.csv ⨯ dataset_<task>_label.csv` (ver Hallazgos).

11. **Limpieza de branches al cierre del sprint.** Durante un sprint
    activo, las branches mergeadas se PRESERVAN en remoto como
    referencias vivas (permite `git checkout feature/X` si hay que
    re-mirar el contexto). Al CIERRE del sprint (cuando todos los
    objetivos están consolidados en main y no hay trabajo pendiente
    en ninguna feature), borrar local + remoto las branches
    mergeadas en una sola pasada. Verificación previa obligatoria:
    `git branch -a --no-merged main` debe devolver vacío (cero
    pérdida de código). La línea semántica de cada branch queda
    preservada en los merge commits via `git log --graph`. La regla
    NO aplica a branches huérfanas con trabajo no mergeado — esas
    se resuelven caso por caso (rebase, cherry-pick, o discusión).
    Ver memoria [[repo-limpieza-branches-cierre-sprint]].

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
- **`forward` devuelve `A_raw` (atención PRE-softmax)** como 4º valor (la
  softmax sobre N se aplica internamente para el pooling, pero lo retornado es
  crudo). `DSMIL_CLAM_MB`, en cambio, devuelve A **normalizada**. Un test/QA que
  asuma `A.sum(dim=1)==1` falla con CLAM/mammoth → usar `softmax(A,dim=1)` o solo
  la **forma** `(n_classes, N)` (que confirma preservación de los N parches —
  clave con mammoth `keep_slots=False`). Verificado 1-jun (Obj 6).

### `utils/core_utils.py`

- `train_loop_clam`: **L241**.
- `instance_loss = instance_dict['instance_loss']`: **L266**.
- `total_loss = bag_weight * loss + (1-bag_weight) * instance_loss`: **L271**.
- `bag_weight` default 0.7 (slide-level 70% / instance 30%).
- "clustering loss" en prints == instance loss.
- **`val_auc=nan` en el log de training de tasks multiclase (3-clase) es NORMAL, no bug.** El AUC de
  validación OVR sale `nan` época a época (verificado: el baseline invasión job 4246 lo logueaba en las
  310 épocas); el checkpoint se guarda por `val_loss` y el `test_auc` final se computa bien (4246 cerró
  macro-OVR 0.80–0.86). Una variante en prueba (ej. mammoth `keep_slots`) **no** lo introduce → no
  declarar el run roto ni culpar al brazo nuevo (es apples-to-apples: baseline y brazo comparten el nan
  en val). Verificado 19-jun (Obj 3, job 4387).

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

### Modelos alternativos en NUESTRO repo (no `clam_environ`)

- **`scripts/train_dsmil.py` es el harness MIL genérico** (el nombre engaña):
  `--model_type {dsmil, clam, clam_mammoth}`, mismo train/val/test + loss
  bag+inst → comparación **apples-to-apples por construcción**. El path
  `clam`/`clam_mammoth` es byte-idéntico a `core_utils.train_loop_clam`; lo
  específico de DSMIL (L_max + grad-logging) está gated en `== "dsmil"`.
- **Gotcha bag loss (batch=1) — [[mil-weighted-ce-noop-batch1]]:** una loss
  ponderada por clase con `nn.CrossEntropyLoss(weight=w)` `reduction='mean'` es
  **NO-OP** en MIL (`batch_size=1` normaliza por `w_y` → cancela el peso → CE
  plana). Usar `reduction='none'.mean()` (`ClassBalancedCE`) **+ test de regresión
  a batch=1** (testear los pesos en aislado NO basta). `focal` no sufre (modulación
  por-sample). Cazado en el job 4463 (brazo cb byte-idéntico al baseline).
- **`models_dsmil/`** — `DSMIL_CLAM_MB` (agregador dual-stream, Obj 3/5).
- **`models_mammoth/`** — `CLAM_MB_Mammoth` (subclase de `CLAM_MB`; 1ª capa
  lineal → MoE Mammoth, Obj 6). `keep_slots=False` preserva los N parches.
- **Receta para integrar otro modelo** (DSMIL→mammoth la probó): `models_<X>/`
  (subclase de `CLAM_MB` o wrapper) + branch ADITIVO en `build_model` de
  `train_dsmil.py` + slurm reusando `data/splits_kfold/<task>_pth_100` (paired) +
  test CPU en `tests/` + hipótesis (regla 9) + reviewer. Skill `@mammoth` y
  memoria [[patron-harness-generico-mil]].

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
   de confusión, siempre con el `n` por clase**. El macro-AUC **solo** (aislado),
   nunca.
   **Actualización política de eval (2-jun-2026, B5 — memoria
   `eval-reporte-auc-y-umbrales-obj6`):** el veto es al AUC *aislado*, NO a
   reportar AUC. Desde B5 se reporta **SIEMPRE balanced_acc Y AUC** (test, y val
   si aporta) **juntos**, con matriz de confusión + n por clase. Reportar AUC
   junto a balanced_acc es ahora **obligatorio**; lo prohibido sigue siendo
   decidir con AUC a secas. Detalle:
   `sprints/B4_sprint4/objetivo_1_baseline/resultados.md` y
   `sprints/B5_sprint5/auditoria_coherencia/hallazgos.md` §D.
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
9. **Reformulación 8 clases → 3 binarios = trabajo previo de Sebastián, NO
   nuestro** (confirmado reunión 22-may). Su infra: tasks
   `microcalcificaciones_en_{carcinoma_invasivo,cdis,tejido_no_neoplasico}_pth`
   (+ `_pth_balance`), 3 CSVs binarios en `environ/csv/` (333 ident.,
   `no_identificado` excluido, pos 68/121/195), splits estratificados. Nuestro
   aporte real = **diagnóstico** (régimen de eval roto, Hallazgo 6; B no es la
   palanca, Hallazgo 8) + **reproducción/validación independiente**. El régimen
   de eval pasó de "no medible" (clases n=1) a confiable (7–20 positivos/test).
   **Los números single-split del job 4109 (carcinoma 0,78 / cdis 0,59 / tejido
   0,58) quedaron SUPERSEDED por los honestos MC-CV** (Hallazgo 11) — eran
   optimistas por sorteo. Detalle: `sprints/B4_sprint4/reformulacion_multilabel/`.
10. **Reunión 22-may + reglas de dataset de microcalcificaciones (lecciones
    durables; cuentas, paths y citas en la memoria canónica
    [[microcalc-dataset-decision]] + `sprints/B4_sprint4/dataset_microcalcificaciones.md`).**
    - **Foco = las 3 binarias, NO las 8 clases.** El 8-clases queda como
      diagnóstico cerrado (4098/4099) y vía para reproducir el V4. Toda mejora
      se evalúa sobre los binarios, contra el baseline binario, **mismo dataset**.
    - **Dataset por escenario**: binarios = **333 identificadas** (`_pth` sin
      `no_identificado`; privado-solo 77 → inentrenable, usar combined 284 /
      `_pth` 333); **~548 privado (533) = 8-clases**; **`_pth` 3072 reservado
      para PRUEBAS FINALES**. (La diferencia 548 vs 333 es la cohorte, no un
      filtro extra.)
    - **`_balance` para binarios = diseño, NO placeholder** — cap imbalance
      ≤10× ya cumplido (carcinoma 3.8×, cdis 1.8×, tejido 1.4×) → `_balance` ≡
      333 con otro seed. El cap SÍ mueve multiclase (`no_identificado` domina).
    - **`no_identificado`** = WSI cuyo reporte CAP **no menciona** microcalc (no
      ausencia confirmada). HOY **excluido** de los 3 binarios (default, no
      oversight); incluirlo como negativo **dispara la mayoritaria** → propuesta
      abierta de jerarquía presencia/ausencia, adoptada PARCIAL como Obj 5
      ([[microcalc-hierarchical-proposal]]).
    - **Mapeo multi-label → binarios**: WSI con menciones de tejido(s) → `si`
      en el binario de cada tejido mencionado, `no` en los demás.
    - **Early stopping**: `stop_epoch=50` HARDCODEADO; runs cortos `--max_epochs`<50.
    - **Pedido de Sebastián a investigar**: escala / nº de parches (contexto
      espacial) + features de **citoplasma** según tarea → es el **Obj 2 de B5**
      (magnificación). Modelo alternativo: viable solo con argumento clínico +
      comparativo paired mismo dataset (regla 9 + [[patron-paired-comparison-reuso-splits]]).
> **Hallazgos 11-14 — Eje ARQUITECTURA/OBJETIVO cerrado: 4 ángulos, 0 palancas.**
> Los cuatro cierran el MISMO mensaje: cuello = **datos / desbalance / contexto
> espacial**, NO la arquitectura ni la loss. Números exactos, matices y gotchas en
> los sprint docs + memorias enlazadas; acá solo el veredicto durable + punteros.
> La numeración 11-14 se preserva porque memorias y otros docs la citan. La palanca
> viva post-cierre = calibración post-hoc del operating-point (Tier 0,
> [[calibracion-operating-point-palanca-b5]] / [[calibracion-tier0-pendiente-ejecutar]]).
> **Tier 0 EJECUTADA 10-jul** (`scripts/tier0_calibration.py`, `sprints/B6_sprint6/tier0_calibracion/`):
> mitotic Δbal_acc **+0.046 ± 0.029 (5/5 folds+)** = win donde el modelo colapsa al argmax (Hallazgo 13);
> invasión/necrosis **null**. Palanca real pero **task-dependiente** (rinde solo si hay colapso a la mayoritaria).

11. **Agregador (CLAM×DSMIL) NO es palanca en microcalc** — cerrado simétricamente con
    MC-CV + comparación PAIRED (Obj 5 + ANEXO). DSMIL: binarias n=328 (job 4179 → NULL en
    carcinoma/tejido, **regresión leve consistente en CDIS** Δ −0.053 ± 0.026, 5/5 folds−)
    y fusionado n=2814 (job 4172 → banda ambigua). El single-split engañaba fuerte a n≈33
    (carcinoma 0.808→0.732 ± 0.167) → **MC-CV + PAIRED obligatorios**. Detalle:
    [[microcalc-fusion-objetivo5]] + `objetivo_5_fusion_binaria/resultados.md` +
    `ejes_futuros_microcalc.md`. *(Rótulo: "k-fold" en archivos = Monte Carlo CV, test
    solapados; identificador histórico, NO se renombra.)*
12. **Mammoth (MoE en el patch-embed) NO es palanca** — hilo COMPLETO: **8 tareas drop-in
    (`keep_slots=False`) + 4 keep_slots=True = 0 palancas** vs CLAM (jobs 4229/4243/4246/4387/4400,
    todo k=5 paired). El (débil) efecto lo gobierna el BALANCE de clases, no la arquitectura: lean+
    leve solo en las ~2 tareas balanceadas; nulo/regresión leve en las desbalanceadas; std ≳ |media|.
    2ª ola (invasión 3-clase n=2814, job 4246) = regresión leve consistente en AUC (−0.011 ± 0.005,
    5/5−) por mayor colapso a la mayoritaria — el mayor poder estadístico no rescató, afinó. La
    variante `keep_slots=True` mitiga su propio colapso a la mayoritaria pero NO supera al baseline
    (0/4 tareas); `slot_dropout` descartado (net-negativo). Detalle:
    `objetivo_2_mammoth_patron_invasion/{resultados.md,resultados_invasion.md}`,
    `objetivo_3_mammoth_keepslots/{resultados.md,prereg.md}` (§6.3 matriz), README
    `results/README_experimentos_mammoth_environ.md` §4 + [[mammoth-investigacion-integracion]].
    **Eje ORTOGONAL abierto (NO reabre rendimiento):** entendimiento + interpretabilidad de
    expertos/slots (reunión Benjamín 29-jun). El detalle mecanístico (tensor S = `slot_embeds`
    30×16×10×16; cabezas = subespacios multi-head ≠ textura/color; MoE≠PoE; nº cabezas para mama =
    pregunta abierta del paper) vive en [[feedback-benjamin-entender-mammoth]]. OBJ-A ejecutado
    30-jun (CPU post-hoc, `scripts/mammoth_interpretability.py`): los 30 expertos rutean por
    **MORFOLOGÍA, no por la etiqueta de slide** (e8 epitelio, e26 estroma, e3 ductal, estables
    cross-slide) → detectores de tejido, el **cuello no está en la 1ª capa** = confirma este
    Hallazgo 12. **Honestidad (13-jul):** los nombres de tejido son **lectura visual nuestra, NO
    anotación** (no hay tejido por-parche; sí la etiqueta clínica de slide) → sign-off patólogo
    pendiente; pero el ruteo por morfología es **label-independiente** (mismo experto/patrón en
    slides de etiqueta distinta) → el hallazgo aguanta aunque el nombre sea impreciso. Tooling +
    detalle en [[mammoth-interpretabilidad-objA]] + `mammoth_entendimiento/`.
    **DATO ABIERTO (18-jul, job 4589) — NO reabre este Hallazgo, pero queda registrado:** en la
    formulación NUEVA `carcinoma_ductal_insitu_presente_ci_reform` (85% positivo, jamás incluida
    en las 12 configs que cerraron este Hallazgo) Mammoth dio Δbal_acc **+0.074 ± 0.033 (5/5
    folds)** y ΔAUC **+0.060 ± 0.042 (5/5)**, con **ambos** recalls al alza y `val_loss` menor en
    4/5 → no es la firma de mover umbral (Hallazgo 14) ni artefacto del test. Además **invierte**
    el patrón "el balance gobierna" (acá gana la MÁS desbalanceada y regresa la balanceada). Frena
    el n chico (65 negativos totales, ~13/fold) y que es terreno nuevo, no contradicción en el
    mismo terreno. El pre-registro lo había anticipado como caso "sorpresa: a investigar, no a
    celebrar". **Reabrir el eje de rendimiento exige regla 9.b** (pre-registro nuevo + branch +
    reviewer); pendiente natural = réplica con más semillas/folds. Detalle:
    `sprints/B7_sprint7/resultados_interpretabilidad.md` §2.
13. **PathPT-CONCH (lenguaje + tile) NO es palanca** — 3er ángulo. necrosis H_alt (job 4309,
    Δbal_acc −0.020 ± 0.078, apenas despega del teacher zero-shot ~0.62 vs CLAM 0.727); mitotic
    COLAPSO de formulación (job 4326, bal_acc 0.333 EXACTO, siempre predice `score_1` — NO bug,
    el ranking/AUC latente sobrevive; formulación clase0=score_1, sign-off pendiente); microcalc
    NO-GO (go/no-go CPU: CONCH no groundea microcalc, AUC 0.44–0.63; prompts con más morfología
    EMPEORAN — CONCH prefiere términos simples). Cuello = CONCH/datos, no el método. El go/no-go
    zero-shot CPU ANTES de la GPU ahorró ~18–24h (patrón Etapa 0 antes de Etapa 1). Detalle:
    [[pathpt-testing-necrosis-mitotic]] + `sprints/B5_sprint5/pathpt/`.
14. **La loss de desbalance (focal / class_balanced) NO es palanca** — 4º ángulo (objetivo de
    entrenamiento, NO arquitectura; CLAM_MB intacto, único delta = la bag loss). focal (job 4463)
    null-a-negativo, baja el recall de la minoritaria; class_balanced (Cui 2019, job 4472, con el
    fix) = **H_reg**: sube recall minoritaria (carcinoma `si` 0.371→0.714) **pero hunde la
    mayoritaria en igual medida** → Δ bal_acc/AUC dentro del ruido (std ≳ |media|). Idéntico a
    mover el umbral post-hoc → converge con [[calibracion-operating-point-palanca-b5]]. Bug `cb`
    no-op a batch=1 RESUELTO ([[mil-weighted-ce-noop-batch1]]). Detalle: [[loss-desbalance-eje-c1]]
    + `sprints/B5_sprint5/loss_desbalance/` + `results/loss_desbalance/analysis_4472_full.txt`.

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
> **Notas del presentador (act. 25-jun, VIGENTE para toda presentación):** se escriben
> como **guion HABLADO corrido** — prosa en párrafos, solo lo que se DICE, leíble de
> corrido (Ernesto presenta online). **SIN etiquetas de fase** (no `PROPÓSITO`/`ABRIR`/
> `RECORRIDO`/`PUNTO CLAVE`/`TRANSICIÓN`), sin la palabra "deck", sin frases artificiales ni
> coloquialismos ("aguas abajo"); texto blanco, sin nº de job ni nombres; fiel a las
> ecuaciones del diagrama y SIN ejemplos numéricos en el guion. **Supersede** el formato
> por-fases del 22-jun (queda LEGACY; motor `set_notes` aún lo emite → Ernesto edita en
> OnlyOffice, NO regenerar el deck para "actualizar notas"). Canónico:
> `sprints/B5_sprint5/presentacion_b5/convenciones_deck_b5.md` §3.b + memoria
> [[notas-presentador-guion-didactico]]. Reconcilia "notas concisas" de Benjamín
> ([[presentacion-convenciones-benjamin]]): mismo objetivo con prosa en vez de densidad.

**Assets PNG insertables para slides (patrón Obj 5)**. Cuando el deck vive
en OnlyOffice (o cualquier herramienta con branding Environ — logo, header
teal, paleta corporativa) y Claude no puede editar el `.pptx` directamente,
generar **PNG estilo "asset insertable"** (sin logo, sin header, sin
título — solo el contenido: tabla, matriz, figura) que Ernesto arrastra
a la slide preservando 100% el branding. Script de referencia:
`scripts/generate_slide_assets.py` (28-may, Obj 5 — produjo los 21 PNG en
`sprints/B4_sprint4/objetivo_5_fusion_binaria/figuras/slide_assets/`).
Convención: nombrar `M##_*.png` para matrices/figuras y `T##_*.png` para
tablas; DPI 220; fondo blanco; tipografía neutra. Esto resuelve el
problema de "Claude entrega contenido, Ernesto controla branding" sin
duplicar trabajo. **NO** intentar editar el `.pptx` ni el PDF del deck
(el PDF transitorio `CLAM_Sprint_*.pdf` está gitignored — ver
`.gitignore`).
> **`render_table` auto-dimensiona columnas** (fix 1-jun, commit `e88032f`):
> mide el ancho real de cada string (mathtext/Text artist sobre canvas Agg) y
> calcula col widths + figura, con el eje al 100% del ancho → cada columna
> recibe `≥ ancho_texto + padding` por construcción (sin solape ni clip). **NO
> volver a pasar `col_widths` a mano** (el arg se ignora). Si una tabla se ve
> mal, es **padding/wrap de celdas largas** (insertá `\n`), nunca proporciones.
> Para math bonito en diagramas usar **mathtext** (`$...$`), NO mermaid (texto
> plano, feo) ni `usetex` (requiere LaTeX instalado).

> **ADDENDUM B5 (14-jun-2026) — el deck SÍ se construye end-to-end con python-pptx,
> y TODO va NATIVO (no imágenes).** Supera el "Claude no puede editar el `.pptx` / NO
> intentar editar el `.pptx`" de arriba (que valía cuando solo se entregaban PNG): con
> python-pptx (`.pylibs`) se arma el deck branded completo y **todo elemento es nativo y
> editable** — tablas reales (`add_table`), gráficos reales (`add_chart`), matrices de
> confusión como tabla-heatmap nativa (`add_confusion`), diagramas de bloques (shapes /
> copia de spTree) y esquemas (`draw_*`). **Regla de ahora en más: tablas, gráficos y
> diagramas = NATIVOS de PowerPoint, NO PNG matplotlib** (Ernesto quiere agrandar/editar).
> Única excepción: **figuras externas de un paper** (van como imagen). Los PNG de
> `generate_slide_assets.py` quedan como respaldo, no como entrega por defecto. Receta y
> branding completos: `sprints/B5_sprint5/presentacion_b5/convenciones_deck_b5.md` +
> memoria [[deck-completo-pptx-buildable]]. Diagramas de arquitectura: estilo
> `Diagrama_CLAM.pptx` (fórmula + dimensiones por bloque, sin bullets, sin solapes).

**READMEs de resultados (`results/README_*.md` y la copia derivada en `clam_testing/`)** —
formato **minimalista estilo Sebastián** (fijado 18-jun-2026): secciones **Tareas / Dataset /
Splits / Comando / Resultados** (tabla con **balanced_acc Y AUC juntos** — regla eval B5,
[[eval-reporte-auc-y-umbrales-obj6]]) + **una línea de resumen**. SIN política de eval, hallazgo
crítico, lectura del hilo, mecanismos ni provenance: ese detalle vive en los
`sprints/.../resultados.md`, referenciados en una línea, y **no se duplica** en el README
canónico. Números exactos (no redondear en el canónico). El minimalismo recorta **prosa**, nunca
el balanced. Memoria [[readme-resultados-formato-minimalista]].

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
- `@mammoth` — Mammoth (MoE de bajo rango que reemplaza la 1ª capa lineal de
  CLAM; heredado de Eduardo, prioridad de Benjamín): modelo `models_mammoth/`,
  driver `train_dsmil.py --model_type clam_mammoth`, slurm Obj 6, test CPU.
- `@mil-model-integration` — receta reusable para integrar un modelo MIL
  alternativo (variante de CLAM o agregador nuevo) paired vs CLAM, sin tocar
  `clam_environ`: `models_<X>/` + branch aditivo en `train_dsmil.py` + slurm +
  test CPU + hipótesis + reviewer. La probaron DSMIL y mammoth.
- `@knowledge-audit` — audita la base de conocimiento completa (CLAUDE.md, memorias,
  agentes, skills) y depura contradicciones, info stale y redundancias: doc de
  hallazgos primero, fixes después, con criterio (canonical vs referencia, no
  borrar contenido único, addendum para pre-registración, edición aditiva de
  reglas duras). Caso de referencia: `sprints/B5_sprint5/auditoria_coherencia/`
  (antes `@coherence-audit`; renombrada 2-jun-2026).
- `@humanizer-es` — reescribe prosa española quitando tells de IA (loop de 4 pasos:
  identificar→borrador→auto-auditoría→final). Alcance: guion HABLADO del presentador
  (es el *procedimiento* de la convención de notas, ver §"Notas del presentador" +
  [[notas-presentador-guion-didactico]]) y prosa de entregables; NO toca docs técnicos
  estructurados, tablas, READMEs canónicos, código ni memorias. Probada en sesión fresca
  9-jul (PASS): `sprints/B6_sprint6/humanizer_es_validacion.md`.
- `@session-close` — rutina de cierre de sesión en 3 fases (orden estricto):
  documentar con `@knowledge-audit` → `@handoff` arrastrando TODOS los pendientes
  sin terminar → commit + push. Invocarla **es** la autorización de push (default
  del repo = "push lo hace Ernesto"); "sin push" la deja en commits locales.
  Triggers — "cerrar sesión", "rutina de cierre".

## Contexto del usuario para sesiones rápidas

Idioma: **español**. Tono: técnico + explicativo. No simplificar conceptos
generales de ML/DL/CV. SÍ explicar pedagógicamente al introducir notación
específica del subcampo (MIL, weakly-supervised, computational pathology).
