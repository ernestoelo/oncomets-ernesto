
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
├── hover_net/           ← HoVer-Net de sgaete (29-jul-2026), CON TRABAJO VIVO. Ajeno → READ-ONLY, misma lógica que clam_testing/. [[hovernet-ya-corriendo-sgaete]]
├── anotaciones/         ← 12 geojson del PATÓLOGO (`<slide>.bif - GDT.geojson`) + pipeline atención/overlays de sgaete. Ajeno → READ-ONLY. [[anotaciones-patologo-qupath]]
└── clam_testing2/       ← MI workspace (todo lo mío vive acá; ver "Workspace containment")
    ├── oncomets-ernesto/        ← este repo
    ├── CLAM_official_reference/ ← CLAM oficial Mahmood Lab (REFERENCE ONLY — not in PYTHONPATH)
    ├── ILSC_reference/          ← ILSC (Liu et al., MedIA 2026) (REFERENCE ONLY — not in PYTHONPATH)
    ├── PUcell_reference/        ← PU learning cell detection, Zhao MELBA 2022  ┐ los 4 del encargo
    ├── CellViT_reference/       ← CellViT, Hörst MedIA 2024                    │ de mitosis (2-ago),
    ├── ZoomMIL_reference/       ← ZoomMIL, Thandiackal ECCV 2022               │ MISMA regla:
    └── MSCLAM_reference/        ← MS-CLAM, Tourniaire MedIA 2023               ┘ REFERENCE ONLY
```

> **`anotaciones/` (READ-ONLY, descubierto el 17-ago-2026).** Es el material de patólogo del
> proyecto y **ninguna sesión anterior lo había mirado**: `grep` sobre el repo entero daba cero.
> Contiene **12** láminas anotadas (`103762 106552 109609 110616 124729 124806 126504 128194
> 129741 144317 164001 B25-158899`), las 12 con features `.h5` y WSI, y **las 12 con marcas de
> `Mitosis`** — 94 en total contra las 26 de la 129741 sola. Su vocabulario de clases es más ancho
> que el de la 129741 (`AreaTubular`, `AreaSolida`, `CDIS_solido`, `CDIS_papilar`, `Comedonecrosis`,
> `Permeaciones vasculares`, `NucleosBajoGrado`, `Nucleos mod grado`, `Mucinoso`,
> `microcalcificaciones`). **Sebastián habló de 30 láminas: faltan 18, y por qué es pregunta
> abierta para él.** Además `sgaete` tiene ahí un pipeline **propio** de atención-vs-anotaciones
> (`atencion/` sobre 8 tareas, `overlays/`, jobs 4838/4839) que **mide lo mismo** que nuestro
> `sprints/B8_sprint8/atencion_vs_patologo/` ⇒ **riesgo de trabajo duplicado: coordinar antes de
> barrer las 12.**

- **Codebase compartido (READ-ONLY)**: `/media/administrador/Storage1/sdonoso/clam_environ/`
- **Datos compartidos (READ-ONLY)**: `/media/administrador/Storage1/sdonoso/clam_environ/environ/`
- **Mi workspace**: `/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/`
- **CLAM oficial (REFERENCE ONLY)**: `/media/administrador/Storage1/sdonoso/clam_testing2/CLAM_official_reference/`
  — repo Mahmood Lab clonado como referencia y fuente de `create_heatmaps.py`.
  HEAD `53e2409` (19 may 2026). **NO se agrega al PYTHONPATH, NO se mezcla ni
  se importa cruzado con el codebase de Sebastián.** Solo lectura/consulta.
- **ILSC (REFERENCE ONLY)**: `/media/administrador/Storage1/sdonoso/clam_testing2/ILSC_reference/`
  — implementación oficial de Liu et al., *Co-assistant networks…*, Medical Image
  Analysis 2026 (`github.com/lZhuoRan/ILSC`). Clonado el **30-jul-2026** con
  autorización de Ernesto porque **el paper es de suscripción**: el código es la
  única vía abierta al método. HEAD `f193187`, 117 MB. Su PFM es **PLIP, no
  CONCH** (verificado: 89 menciones de plip, cero de conch). Mismas reglas que
  el anterior: **NO al PYTHONPATH, NO import cruzado**, solo lectura. Ficha del
  paper en `sprints/B8_sprint8/papers_b8.md` §4.
- **Los 4 repos del encargo de mitosis (REFERENCE ONLY)**, clonados el 2-ago-2026
  con autorización explícita de Ernesto, bajo `clam_testing2/`: `PUcell_reference/`
  (`1bce728`), `CellViT_reference/` (`05097e1`), `ZoomMIL_reference/` (`da7bb7f`),
  `MSCLAM_reference/` (`18e8827`). **Mismas reglas que los dos anteriores: solo
  lectura, NO al PYTHONPATH, NO import cruzado.** Sin checkpoints descargados.
  Estudios y correcciones en `sprints/B8_sprint8/tareas_geometricas/` +
  [[papers-rama-mitosis-bcd]].

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
- **E.a — «No descargar» es POLÍTICA, no una limitación técnica** (verificado
  2-ago-2026): el server **SÍ tiene salida a internet** (`curl` a arXiv y
  `git clone` de GitHub funcionan). Los `WebFetch` de las sesiones salen por el
  harness, que es otra cosa y no prueba nada sobre la máquina. El default sigue
  siendo **no bajar nada sin autorización explícita de Ernesto**; lo que cambia
  es que, cuando la autoriza, se baja **desde el server y al destino correcto**,
  sin pedirle que suba archivos a mano. Precedente: los 5 papers de mitosis y sus
  repos, autorizados el 2-ago ([[papers-rama-mitosis-bcd]]). Una autorización es
  **para esa lista**, no para el tema.
  - **Segundo precedente, 17-ago-2026**: Ernesto autorizó clonar
    `github.com/digitalpathologybern/hover_next_inference` y bajar **los dos** juegos de pesos
    (Lizard-Mitosis y PanNuke), destino `clam_testing2/hover_next_reference/`, REFERENCE ONLY y
    fuera del `PYTHONPATH` como los 4 del 2-ago. **Supersede** el «no hay autorización» que
    arrastraban `hovernext_estudio.md` §11 y los handoffs previos.
    Sigue valiendo que la autorización es para **esa lista** y no para el tema.
- **E.b — Gotcha del cache del harness**: un `WebFetch` sobre la URL de un PDF
  deja una copia en `~/.claude/projects/<hash>/<sesión>/tool-results/*.pdf`,
  **fuera del containment**. Si la regla vigente es no descargar, borrarla en el
  momento; si está autorizado, bajar **a propósito y al destino correcto**, no de
  rebote.

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

### K. Un env conda NUEVO no puede abrir los `.bif` privados

- **Síntoma**: `openslide.OpenSlideError: Bad direction attribute "LEFT"` al abrir
  cualquier `.bif` de la cohorte privada desde un entorno recién creado. Las
  sesiones nunca lo ven porque `clam_latest` ya está arreglado.
- **Causa**: los `.bif` Ventana traen `direction="LEFT"` en su XML y el OpenSlide
  **oficial** (hasta 4.0.0 inclusive) solo entiende `RIGHT` y `UP`. **No es un
  problema de versión**: instalar `openslide=4.0.0` de conda-forge **tampoco
  funciona** (verificado 17-ago). Hace falta la build **parchada** que documenta
  `clam_environ/openslide_solution.md` (agrega `DIRECTION_LEFT` a
  `src/openslide-vendor-ventana.c` y compila).
- **Fix**: copiar la biblioteca parchada de `clam_latest` al env nuevo —
  ```bash
  cp /home/sdonoso/miniconda3/envs/clam_latest/lib/libopenslide.so.1.0.0 $ENVP/lib/
  export LD_LIBRARY_PATH=$ENVP/lib          # al invocar por binario absoluto (workaround B)
  ```
  **El tamaño delata cuál es**: **1,2 MB la parchada**, 287 KB la stock. `ldd`
  resuelve sus deps dentro del env nuevo, así que no arrastra nada de
  `clam_latest` en runtime. Cazado por el preflight de la fase 2 del B8, en
  segundos y antes de pedir GPU. Memoria [[openslide-parchado-bif-env-nuevo]].

### L. Un job `PD (Priority)` puede NO estar esperando su turno

- **Síntoma**: `squeue` muestra el job propio en `PD (Priority)`, que se lee como
  «hay gente delante, ya me toca», y pasan horas o días sin que arranque.
- **Causa**: `squeue` no muestra por qué. `scontrol show job <id>` sí. Dos cosas
  bloquean de verdad en este cluster:
  1. **La GPU es UN token** (`Gres=gpu:1`): quien la toma la tiene hasta terminar.
     No se comparte por SLURM (los jobs que "comparten GPU" son los que **no**
     piden el GRES y usan CUDA por su cuenta — ver la nota de cortesía de arriba).
  2. **Un job con `TimeLimit=UNLIMITED` delante mata el backfill.** Para colar un
     job chico antes que uno grande, SLURM necesita saber **cuándo termina** el
     grande. Con `UNLIMITED` esa ventana no existe.
- **Fix / qué hacer**: `scontrol show job <id>` y mirar `StartTime`, más el
  `TimeLimit` y el `TresPerNode` **de los que están delante**. Un
  `StartTime` a un año **no es una predicción**: es lo que devuelve cuando no
  puede planificar.
  **Corolario contraintuitivo: si el bloqueo es este, achicar el propio job
  (`--mem`, `--cpus`) NO lo adelanta.** Solo ayuda *después* de que el token se
  libere. Lo que destraba es coordinación (que los de delante declaren un
  `--time` real), no ingeniería. Caso de referencia: job 4998 del B8,
  `sprints/B8_sprint8/hovernext_129741/coordinacion_gpu.md`.
  Memoria [[slurm-cola-backfill-timelimit]].
- **L.b — un `StartTime` CONCRETO tampoco es una predicción.** Si el que tiene la GPU
  declara `--time` real, SLURM sí planifica y devuelve una hora creíble — pero es la
  **primera disponibilidad del recurso**, sin descontar lo que dure un `UNLIMITED` que
  vaya delante. Modo de falla opuesto al de arriba y por eso más peligroso: el
  `StartTime` de un año hace desconfiar, el concreto tranquiliza. **Mirar el `TimeLimit`
  de cada job que va delante**; con un `UNLIMITED` ahí, el `StartTime` propio es **cota
  inferior**. Y `squeue -u $USER` **mezcla operadores** (cuenta `sdonoso` compartida):
  antes de dar por propio un job, `scontrol show job <id>` y mirar `WorkDir`.
- **L.a — `--export` es hostil a los valores con coma.** `sbatch
  --export=ALL,VAR=valor` separa **variables** por coma, así que cualquier valor
  que a su vez **espere** comas (ej. `--cp a,b,c` de HoVer-NeXt, que promedia un
  ensemble) llega partido en variables basura, y sin error claro. Pasarlo con
  otro separador (`+`) y traducirlo dentro del `.slurm` (`VAR=${VAR//+/,}`), que
  además es idempotente para el caso de un solo valor.

### M. Una herramienta ajena puede rechazar el `.bif` por EXTENSIÓN

- **Síntoma**: un job que esperó horas en cola arranca y muere en segundos con
  `NotImplementedError: Only *.svs, *.tif, *.czi, and *.mrxs files supported`
  (HoVer-NeXt, `src/data_utils.py:241`). El preflight había dado OK.
- **Causa**: la herramienta valida la **extensión del nombre** contra una whitelist,
  y recién después abre la lámina con OpenSlide, que **detecta el formato leyendo el
  archivo**. El `.bif` Ventana es TIFF por dentro, así que el gate es cosmético.
  Que OpenSlide abra la lámina **no alcanza**: hay una segunda puerta, y corre primero.
- **Fix**: symlink con la extensión aceptada, **bajo containment**, sin tocar el repo
  ajeno (que es REFERENCE ONLY):
  ```bash
  ln -sfn /media/.../wsi/<id>/<id>.bif /media/.../clam_testing2/wsi_shim/<id>.tif
  ```
  **Verificar que no degrade**, que es el riesgo real: OpenSlide tiene que seguir
  eligiendo el driver `ventana` con el mismo `mpp` y las mismas dims. Si cae a
  `generic-tiff` se pierde la magnificación y todo lo aguas abajo queda mal.
- **Regla que se desprende**: un preflight que valida «lo abre mi stack» no cubre «lo
  acepta la herramienta que voy a correr». Chequear la puerta **de la herramienta**.
  Ya está en `scripts/preflight_hovernext.py`. Memoria
  [[hovernext-bif-extension-whitelist]].

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

> **El caso inverso también existe: jobs ajenos que alargan EL NUESTRO** (3-ago-2026).
> SLURM admite varios jobs concurrentes en el único nodo, así que un job propio ya
> lanzado **comparte la GPU** con los que entren después. Caso real: el 4774 (grid E×S)
> pasó de ~37 a ~70 min por run en la ventana en que aparecieron **tres** jobs de
> `capstone`. **Antes de concluir que un `.slurm` es lento o que la ETA se estimó mal,
> correr `squeue` y mirar quién más está en el nodo**, y anotarlo en el `resultados.md`.
> Afecta el **tiempo de pared, no la métrica** — no invalida nada. Con `sacct`
> deshabilitado (workaround C) no hay traza retrospectiva de utilización por job, así que
> el dato hay que capturarlo **en vivo** o se pierde.

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

**P1.a — El pipeline es DETERMINISTA bit a bit** (verificado 4-ago-2026, job
4774 contra 4589). Re-correr una config con **la misma semilla, los mismos
splits y las mismas features** reproduce hasta el `s_<f>_checkpoint.pt` **byte
a byte** (`md5` idéntico en los 5 folds). Dos consecuencias operativas
opuestas, las dos importan:

- **A favor del reuso**: un baseline viejo que comparta semilla/splits/features
  es comparador válido **por construcción**, no "referencia informativa". No
  hace falta presupuestar runs de control por miedo al no-determinismo de GPU.
- **Contra el mal uso**: re-correr la misma config con la misma semilla **no
  aporta ni un bit de evidencia nueva**. **Toda réplica que pretenda ser
  independiente TIENE que cambiar la semilla.** Un "lo volvimos a correr y dio
  igual" con `--seed` fijo no replica nada.
- **Corolario de debugging**: si dos runs que deberían ser idénticos difieren,
  hay una variable oculta real (features mutadas, código distinto, otra
  semilla), **no** "ruido de GPU". El `md5sum` del checkpoint es un test de
  regresión barato y concluyente.

Acotado a esta GPU (RTX A6000) y este stack; el determinismo cross-hardware no
se midió. Detalle: [[pipeline-determinista-bit-a-bit]].

**Cómo documentarlo en la hipótesis**: declarar `**Comparación**:
paired vs <job baseline> reusando `<path/al/split_dir>`` antes del
sbatch. El reviewer lo verifica como parte del checklist.

### P2. Un top-k de parches se dimensiona por PERCENTIL, no por AUC

**Cuándo aplica**: cualquier prueba o pipeline que restrinja a los `k` parches de mayor
atención (la forma de la segunda etapa que propuso Sebastián el 12-ago).

**Regla operativa**: antes de fijar `k`, **calcular el percentil de atención del objeto que se
quiere recuperar** y derivar `k` de ahí; y **declarar el denominador alcanzable** junto al `k`
(«el top-k contiene N de M positivos, así que el máximo recuperable es N»). Si N es chico, la
prueba no distingue nada y hay que rediseñarla, no correrla.

**Por qué**: un AUC alto **no** implica que el top-k capture los positivos. El AUC resume
**todos** los umbrales; un top-k es **UN** umbral, y de los extremos. Caso de referencia
(14-ago-2026): con AUC de atención **0.890**, el top-20 de los 4799 parches de la 129741
contiene **3 de los 28** parches con mitosis (mediana de 12 checkpoints, rango 0 a 5), porque el
percentil mediano de esos parches es ~96 (puesto ~190) y el top-20 es el percentil 99.58. Para
la mitad de las marcas hacen falta 189 parches; para todas, 1392.

**P2.a — El techo de una prueba restringida se mide SIN correr la etapa cara** (17-ago-2026).
Cuando la prueba encadena **un filtro barato** (un top-k por atención) con **una etapa cara** (un
detector, una corrida de GPU), el filtro **solo** ya acota el resultado por arriba: un candidato
que no entra en la máscara no lo recupera nadie, por bueno que sea el detector.

```
resultado(k)  ≤  min( techo_del_filtro(k) ,  poder_de_la_etapa_cara )
```

y **el primer factor no depende de la etapa cara**. Entonces se calcula **antes** — es la forma
operativa de «declarar el denominador alcanzable» cuando el denominador depende de dos etapas.
Un techo bajo **condena** la prueba y ahorra la corrida entera; uno alto **no promete nada**, solo
deja la pregunta viva. **No confundir el techo con el resultado**: es una cota, y decirlo en cada
figura y caption es parte del patrón.

De yapa suele regalar el **chequeo de sanidad** del barrido: en el `k` que cubre todo, los brazos
tienen que coincidir. Caso de referencia: `sprints/B8_sprint8/hovernext_129741/techo_atencion.md`
(la fase 3 acotada con la GPU bloqueada) + memoria [[techo-filtro-antes-de-correr]].

**P2.a.bis — cuando el segundo factor SE mide, `min()` no alcanza: contar la INTERSECCIÓN**
(19-ago-2026, el cruce que cerró el caso de referencia de arriba). Medidos los dos factores sobre
la 129741, aparecen tres cosas que la cota sola no da:

- **Cuál factor manda puede cambiar con `k`, y hay que decir desde dónde.** Acá el techo del filtro
  mandaba hasta `k`=189 (7,6 % de la región) y de ahí en adelante manda la **detección** (13 de 26).
  O sea que **un techo alto puede además significar que el filtro ya dejó de ser el problema**, y
  eso solo se sabe midiendo el otro factor. Antes de medirlo, toda la discusión era sobre el tamaño
  del recorte; después, el recorte dejó de importar.
- **La cota `min()` es floja: sirve para condenar, no para presupuestar.** En el 12 % de la región
  `min()` prometía 13 y la intersección real fue **11**. Contar la intersección cuesta lo mismo una
  vez que están los dos factores.
- **Testear si los dos factores son independientes.** Si lo son (acá sin evidencia de asociación,
  p = 0,200 y 0,383), la intersección queda cerca del producto y lejos de `min()`. Si estuvieran
  asociados, `min()` sería peor cota todavía.

Y una trampa de unidad al juntar las dos etapas: el techo se midió en **parches** (28) y el cruce
en **marcas** (26). Coinciden en algunas celdas por casualidad. **Declarar la unidad en cada tabla**
o alguien va a leer una como continuación de la otra. Detalle:
`sprints/B8_sprint8/hovernext_129741/cruce_marcas.md`.

**P2.a.ter — si la etapa cara se puede pagar entera, CORRERLA SIN EL FILTRO** (19-ago-2026).
P2.a dice cómo medir el techo del filtro sin correr lo caro. Ésta es la decisión **anterior**, y
gobierna a las otras dos: cuando el presupuesto alcanza, se corre la etapa cara **sobre todo** y el
filtro se aplica **post-hoc, sobre la salida**. Con eso quedan medibles **todos** los `k` de una
sola corrida, y **el brazo sin filtro sale gratis** — que es contra el que se lee cualquier
resultado restringido. Filtrar **antes** ahorra cómputo una vez y **destruye la comparación para
siempre**. Caso de referencia: HoVer-NeXt sobre la 129741 corrió la lámina entera (18 min), y por
eso la escalera existe sin correr nada nuevo: **68,0 mm² → 13 de 26 · 35,4 mm² → 13 de 26 ·
4,3 mm² → 11 de 26**, o sea que **el recorte no compra marcas, compra área** (factor 16 por dos
marcas). Eso convierte el corolario de costo de abajo en un número: la pregunta «cuánta superficie
ponerle delante al patólogo» **no es** la pregunta «cuántas mitosis encontramos».
[[techo-filtro-antes-de-correr]].

**Corolario de costo**: restringir para **ahorrar cómputo** y restringir para **controlar falsos
positivos** son motivos distintos y **no fijan el mismo `k`**. Cuando el cómputo deja de ser
caro, solo sobrevive el segundo. Detalle: [[topk-percentil-no-auc]].

### P3. Un control positivo CALIBRA el criterio, no solo valida el instrumento

**Cuándo aplica**: cualquier prueba con un criterio de decisión cuyo **corte numérico es
posterior a ver los datos** (una sd, un umbral de consistencia, un margen), y que incluya un
grupo de control positivo — casos donde ya se sabe que el instrumento funciona.

**Regla operativa**: **antes** de aplicar el corte al grupo de estudio, aplicárselo al **control
positivo**. Si el control no lo pasa, el corte está mal, no el grupo de estudio. Y el corte se
fija en **el peor del control**, no a ojo. Reportar además la **sensibilidad** del corte y decir
qué conclusiones se mueven con él y cuáles no.

**Por qué**: la función obvia del control positivo es validar el instrumento («¿mide?»). Tiene una
segunda, que se pasa por alto: **acotar cuánto vale el estadístico cuando la respuesta es SÍ**. Sin
eso, cualquier corte elegido mirando el grupo de estudio confunde «no cumple mi corte» con «no hay
efecto».

**Caso de referencia** (17-ago-2026, probe de rotación del B8): el criterio pre-registrado era «θ
consistente entre ventanas = rotación; θ disperso = ruido», sin número. El corte que se había
escrito, `sd ≤ 4°` sobre **todas** las ventanas, **rechazaba 3 de las 4 láminas del control** — que
localizaban perfectamente. Causa: θ se elige por máximo de NCC y, en una ventana que no localiza, la
superficie es plana y su argmax vaga, inflando la sd de la lámina entera. Medida **solo sobre las
unidades que sí responden**, las 4 del control pasan y el peor da 2,2°, que es el corte adoptado.
La sensibilidad mostró además que el resultado principal (6 de 12) **no depende del corte** y que el
reparto secundario es estable en todo el rango donde el control pasa entero. Detalle:
`sprints/B8_sprint8/anotaciones_patologo/regiones_escaneo/resultados.md` §10.a-10.b.bis +
[[control-positivo-calibra-el-criterio]].

**Corolario**: si el control positivo **no** corrió, el resultado **no se lee** — y esa condición se
escribe en el pre-registro, antes, no después. El mismo probe lo llevaba escrito y por eso la
sesión que lo vio a medio correr no lo leyó.

### P4. Una categoría residual puede ser FABRICADA por el instrumento que la mide

**Cuándo aplica**: cualquier clasificación con una categoría definida por la **conjunción de dos
fallos** («señal débil **y** ajuste malo», «no converge **y** no separa»), especialmente si es la
categoría que representa el hallazgo interesante.

**Regla operativa**: antes de contar esa categoría, preguntarse **si el propio instrumento produce
las dos condiciones a la vez cuando no da abasto**. Si la respuesta es sí, la categoría no se puede
leer sobre las unidades donde el instrumento está al límite: hay que **separarlas** y reportar el
reparto de ese subgrupo **contra** el de las unidades donde el instrumento sí trabaja cómodo, más la
descomposición de **cuál** de los dos criterios falló en cada caso.

**Por qué**: una categoría residual (el `else` de la cascada, o la definida por dos negaciones) hereda
todo lo que el instrumento no supo medir. Cuando además se amplía la población medida — se arregla
una etapa previa y entran unidades **más difíciles por construcción** — esa categoría crece **sin que
haya pasado nada en los datos**. El aumento se lee como hallazgo y es un artefacto.

**Caso de referencia** (18-ago-2026, re-barrido de regiones de escaneo): «perfil de secciones
seriadas» se define por `razón < 2,0` **y** ajuste no rígido. Las láminas que la rotación recupera
son por construcción **las más giradas** (|θ*| mediano 7,8°) y la etapa B **barre solo ±8° y no busca
escala** ⇒ tendrán las dos propiedades a la vez y caerán en «seriadas» por incapacidad del
instrumento. **Es lectura del criterio, no conjetura sobre los datos**: las dos condiciones que
definen la categoría son las dos que produce una etapa B que no da abasto. Detalle:
`sprints/B8_sprint8/anotaciones_patologo/regiones_escaneo/resultados.md` §11.b +
[[categoria-residual-fabricada-por-el-instrumento]].
**CONFIRMADO con dato el 19-ago** (§12.d): al cosechar el re-barrido, «seriadas» pasó de 1 a 12 y
**7 de las 12 son recuperadas** (29 % contra 10 % de las ya medibles); de las 18 recuperadas que no
dan re-escaneo, **10 fallan los dos criterios a la vez**. El patrón dejó de ser mecanismo con n=1.

**Corolario que emparenta P2, P3 y P4**: los tres son formas de que **el instrumento se cuele en la
conclusión** — el umbral en P2, el corte en P3, la categoría en P4. Frente a un resultado que
sorprende, el primer sospechoso es la herramienta, no el mundo.

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

## Formato de `objetivos_sprintN.md` — índice, no almacén

Fijado el **5-ago-2026** al reestructurar el B8 (319 → 168 líneas, sin perder un dato).
Adoptado de la skill *wayfinder* de mattpocock; la evaluación de por qué se tomó la
gramática y no la skill entera está en [[wayfinder-evaluacion-y-cosecha]].

**Regla: cada decisión vive en exactamente UN lugar, su archivo.** El doc de objetivos la
resume en una línea y enlaza. Si algo se explica dos veces, la copia del doc de objetivos
es la que sobra. Esto ataca la acumulación de ADDENDUMs, que es la forma en que estos docs
se venían pudriendo (el B8 llegó a 3, `CLAUDE.md` tiene 20).

Cinco secciones fijas:

| Sección | Qué va |
|---|---|
| **Destino** | Qué significa llegar al final del sprint. 1-2 líneas; toda sesión se orienta con esto antes de elegir en qué trabajar |
| **Notas** | Dominio, skills que toda sesión debe consultar, restricciones permanentes del sprint |
| **Decisiones tomadas** | El índice. Una línea por asunto cerrado: lo justo para juzgar si hay que abrir el enlace |
| **Todavía sin especificar** | La niebla: se intuye que viene, no se puede formular todavía. Gradúa a pre-registro cuando una resolución la aclara. Sub-sección **Pendiente sharp** para lo ya enunciable que aún no es accionable |
| **Fuera de alcance** | Descartado **por decisión**, no por falta de nitidez. NO gradúa: vuelve solo si se redibuja el destino, y como esfuerzo nuevo |

**El test para separar niebla de pendiente sharp es si podés ENUNCIAR la pregunta con
precisión ahora, no si podés responderla ahora.** No pre-cortes la niebla en pedazos del
tamaño de una pregunta.

La sección **Qué no se afirma** (invención propia, B8) se conserva: es higiene epistémica y
no tiene equivalente en la gramática importada.

Esto le da a la **regla 9.b** un lugar único donde mirar qué fue descartado. Hoy eso vive
repartido en `ejes_futuros_*.md`, apéndices "descartado", veredictos NO-GO y memorias (33
archivos bajo `sprints/` lo mencionan), y por eso la regla tiene que enumerar los cuatro.

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
    **Q1 del B7 CERRADA (19-jul, n=7 láminas, CPU post-hoc):** medido el «peso por slot»
    (`combine_weights`, la 2ª softmax sobre los E·S=300 slots, **NO** el top-k de parches), el
    número efectivo = exp(entropía) da **expertos 30.0 de 30 en las 7 láminas** (con `e50=15` /
    `e90=27`, los valores exactos del reparto uniforme, idénticos en las 3 tareas) → **E=30 no está
    sobredimensionado**; y **slots 158.7 de 300** → el margen de recorte de capacidad está en **S,
    no en E** (⚠ esa última inferencia quedó **acotada el 4-ago**: describe el reparto, no predice
    capacidad; ver los dos ADDENDUM de abajo). La dispersión de slots (89.7–196.4) sigue al **tamaño de la lámina**, no a la tarea
    (las 2 láminas de CDIS cubren casi todo el rango solas: la más baja y la 2ª más alta; el máximo
    196.4 es de LVI). Refuerza este Hallazgo: el modelo ocupa todos sus
    expertos, así que el cuello no es falta de capacidad de ruteo. Detalle:
    [[mammoth-slot-routing-weight]] + `sprints/B7_sprint7/resultados_interpretabilidad.md` §5.
    **ADDENDUM 24-jul (reunión con Sebastián y Benjamín) — «CERRADA» vale para los expertos,
    no para el número de slots.** Benjamín observó que **158.7 sale de 7 láminas y no
    generaliza** al dataset de la tarea → escalarlo es el encargo 1 del B8. **Sigue en pie**
    lo de los expertos (30.0/30 con los cuantiles exactos del uniforme, transversal a las 3
    tareas) y por lo tanto que **E=30 no está sobredimensionado** y que el margen está en
    **S**; **queda pendiente de escalar** el 158.7 como número de la tarea y la correlación
    con el tamaño de lámina (ρ=0.750, p=0.052, que con n=7 describe y no establece). No es
    corrección: el resultado ya llevaba esa salvedad. **Dato que lo destraba:** la medición
    **no necesita la WSI** (features y coords salen del mismo h5,
    `scripts/mammoth_interpretability.py:128`; openslide solo dibuja) → se puede barrer el
    test de los 5 folds de las 3 tareas en CPU. [[reunion-24jul-encargos-b8]] +
    `sprints/B8_sprint8/objetivos_sprint8.md` §1.
    **ADDENDUM 27-jul (encargo 1 EJECUTADO, `scripts/q1_slots_escalado.py`) — el número
    aguanta, la explicación de la dispersión NO.** Barridas **1858 láminas-fold** (1176
    únicas: los test de los 5 folds de las 3 tareas, las 3 cohortes) en 18 min de CPU
    post-hoc. **Slots efectivos 159.5 ± 26.3 de 300** contra 158.7 ± 34.6 con n=7 → el
    número se sostiene y ahora **es** el de la tarea. **Expertos 29.98/30**, con `e50=15` y
    `e90=27` exactos en las 1858 sin una sola excepción → **E=30 no está sobredimensionado**
    y **el margen de capacidad está en S**, confirmado con n grande (insumo directo del grid
    del encargo 3). **⚠ ACOTADO 4-ago por el grid E×S (job 4774): «el margen está en S» vale
    como descripción del reparto del peso, NO como predicción de capacidad.** Puesta a prueba
    de frente, la dirección del recorte resultó indistinguible (§ADDENDUM 4-ago del cierre de
    este Hallazgo). **Los números de arriba no cambian** — 159.5/300 y 29.98/30 siguen
    medidos y vigentes; lo que no se sostiene es inferir de ellos **dónde** conviene recortar.
    **Lo que sí se corrige:** el B7 decía que la dispersión «sigue al TAMAÑO
    de la lámina y no a la tarea» (ρ=0.750, n=7); con n grande **se invierte el orden y las
    dos explican poco** — tarea eta²=0.086, tamaño ρ²=0.020 (ρ cae 0.750→0.141), cohorte
    0.018; el ~88 % de la varianza es variabilidad entre láminas. **La cohorte casi no mueve
    la aguja** (privado 162.7 vs TCGA 162.2 vs HistAI 154.9), lo que descarta que medir solo
    TCGA en el B7 sesgara el número. Detalle:
    `sprints/B8_sprint8/q1_slots_escalado/{resultados.md,metodologia.md}` +
    [[mammoth-slot-routing-weight]]. Gotcha mecanístico que salió al implementarlo:
    [[mammoth-dispatch-softmax-sobre-parches]].
    **Precisión 23-jul:** la morfología la captura el **slot**, no el experto — la Fig. 3 del paper
    rotula sus mapas por **par experto+slot** y el mismo experto tiene slots de tejido distinto
    (e16·s1 alvéolos vs e16·s4 estroma). Explica por qué los expertos salen uniformes y el margen
    está en S. Nuestro OBJ-A midió a nivel de **experto**, no de slot: no presentarlo como si
    hubiéramos medido morfología por slot. [[slot-unidad-de-morfologia]].
    **Precisión 23-jul (2):** tampoco lo captura la **cabeza** — las 16 cabezas son un *corte* del
    query de 256 en 16 tramos de 16, no miradas semánticas, y los prototipos son **300 cortados
    igual** (NO uno por cabeza) ⇒ **16 tablas de N×300**, 4800 parecidos por parche.
    [[mammoth-cabezas-son-tramos]].
    **Precisión 23-jul (3) — slots no redundantes + heatmap por slot:** medido en nuestras láminas,
    la correlación espacial entre los **top-8 slots** es **−0.00** de media y el #1 vs #2 da **−0.62**
    (regiones opuestas) → slots distintos se concentran en tejido distinto (qué tejido = lectura
    visual, sign-off pendiente). El **heatmap por slot** usa `combine` (2ª softmax) **sin colapsar N**
    y NO es el heatmap por **experto** que ya existía (ese usa `dispatch`, 1ª softmax, y a nivel
    experto el ruteo es uniforme) — no cruzarlos. Tablas + mapas en `sprints/B7_sprint7/slot_softmax/`.
    [[slot-unidad-de-morfologia]].
    **Precisión 23-jul (4) — compartir experto no predice qué ve el slot, y la cota es el uniforme:**
    sobre 198 pares, los 6 del **mismo experto** cubren **−0.56 a +0.71**, casi el rango entero de
    los 192 de expertos distintos (−0.78 a +0.89); `e28·s4` (#1) vs `e28·s5` (#4) en CDIS da
    **−0.56** (regiones opuestas) pero `e13·s6` vs `e13·s5` da +0.71 → decir "dos slots del mismo
    experto encienden regiones distintas" (medido), NO "siempre ven cosas distintas" (falso). Y la
    **cota** para decidir qué slot aporta es el **reparto uniforme 1/300 = 0.333 %**, único corte
    sin parámetro libre (a ojo la respuesta va de 25 a 300 slots): deja **63–96 slots por lámina**
    que concentran el **73 %** del peso, estable entre tareas. Los 85 (concentran) y el `N_eff` 159
    (cuenta cada slot en proporción a su peso) **no se contradicen**, miden cosas distintas. Detalle:
    `sprints/B7_sprint7/resultados_interpretabilidad.md` §5.3 + [[cota-softmax-slots-uniforme]]. **Eje de trabajo abierto (NO reabre rendimiento):** afinar **E y S**
    para mama reduciendo uno con el otro fijo a igual total (27×10 vs 30×9), regla 9 + reviewer +
    paired sobre los splits del 4589 — [[mammoth-grid-expertos-slots]].
    **ADDENDUM 4-ago-2026 — ese eje EJECUTADO y CERRADO en H_nula (job 4774, 8 brazos × 5 folds,
    40/40 runs). Este Hallazgo 12 NO se movió:** el grid midió **capacidad**, no rendimiento, y por
    diseño no calculó ningún Δ contra CLAM por brazo. Lo que cerró: el contraste primario
    `(recorta S) − (recorta E)` a igual E·S dio **+0.022 / −0.014 / −0.002** de AUC en los peldaños
    270 / 210 / 150 → **el signo de la media se invierte entre peldaños**, sd > |media| en los tres,
    y el único peldaño a favor tiene 3/5 folds ⇒ **la dirección del recorte es indistinguible** y la
    ocupación medida (§ADDENDUM 27-jul) **describe el reparto pero no dimensiona la capacidad**.
    Secundarios, los dos hacia que la capacidad sobra: el piso **30×3 (−70 % de capacidad) pierde
    solo 0.039 ± 0.062 de AUC** (cruza cero), y dentro de la rama S **no hay dosis-respuesta**
    (0.792 → 0.797 → 0.802 → 0.786 de 270 a 90, rango menor que la sd de un brazo); la rama E ni
    siquiera es monótona (el **peor** brazo del grid es 27×10, el recorte más chico). **Hallazgo
    operativo transversal que salió de acá:** el control 30×10 reprodujo al 4589 **bit a bit**
    (`md5` idéntico en los 5 folds, checkpoint de 2.5 MB incluido) ⇒ el pipeline es **determinista**
    en esta GPU con la misma semilla, lo que valida el reuso pareado por construcción (patrón P1) y
    a la vez confirma que el control **no** replicó el DATO ABIERTO de abajo y no podía hacerlo
    (misma semilla) — esa réplica **sigue pendiente y exige semillas nuevas**. Detalle:
    `sprints/B8_sprint8/grid_expertos_slots/{prereg.md,resultados.md}` +
    [[mammoth-grid-expertos-slots]] + [[pipeline-determinista-bit-a-bit]].
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

> **Aclaración 19-jul-2026 — no son dos plantillas, son dos CABECERAS de la
> misma.** `Plantilla.pptx` (30 láminas) contiene las dos: la **Environ**
> (cuadro teal + barra gris) en sus 13 láminas administrativas (portada,
> agenda, recapitulación, cierre) y la **OncoMets** (logo OncoMets + línea
> teal) en las **17 técnicas, s04-s18**. Misma familia: 13.333×7.5, Barlow,
> misma paleta. **Regla: el contenido técnico va con cabecera OncoMets**; la
> Environ queda para agenda/recapitulación. El arquetipo técnico es Plantilla
> s05 ("Patch Encoder"). Un deck que use la Environ en todo se lee como fuera
> de template (le pasó al B7 hasta el commit `42280de`). Geometrías, extracción
> del logo desde el `blipFill` y gotchas de banda/títulos:
> [[plantilla-dos-cabeceras]].
>
> **ADDENDUM 19-jul-2026 (tarde) — el template VÁLIDO es `Modelo OncoMets
> Spatial V1 Deep-LLM-V.pptx`**, fijado por Ernesto. `Plantilla.pptx` sirvió para
> entender las dos cabeceras (y sus geometrías **siguen siendo correctas**: la
> cabecera técnica es idéntica al píxel en los dos archivos, mismos nombres de
> shape), pero el archivo a respetar es Deep-LLM-V. Diferencia que importa: es
> **solo técnico** (19 láminas = portada + lámina de título + 17 técnicas) y **no
> tiene cabecera Environ en ninguna lámina** → en un deck basado en él, TODO el
> contenido va con cabecera OncoMets, incluida la recapitulación. La regla "la
> Environ queda para agenda/recapitulación" aplica a Plantilla, no acá.
>
> **ADDENDUM 23-jul-2026 — TODA la tipografía del deck va en Barlow** (regla de
> Sebastián). Poner Barlow en los runs que uno escribe **no alcanza**: el
> `fontScheme` del theme de Deep-LLM-V es el de Office (**Arial**) y las láminas
> heredadas del template traen **Calibri** en `endParaRPr`/`buFont`, que gobierna
> lo que se escriba encima en OnlyOffice. Los paneles de código pierden Consolas
> (no viaja embebida). Fix reusable = `forzar_barlow(prs)` en
> `generate_b7_deck.py`; verificación = `unzip` del `.pptx` y contar
> `typeface="..."` bajo `ppt/`. Detalle: [[deck-template-fuentes-embebidas]].
>
> **ADDENDUM 23-jul (noche) — Barlow ya está instalada en el servidor**, bajo
> containment: `clam_testing2/fonts/barlow/` (18 TTF) + `fonts.conf` que hereda el
> del sistema. Se activa por `FONTCONFIG_FILE`; sin esa variable el server queda
> como estaba. Con eso **el rasterizado de LibreOffice ya sirve para juzgar
> tipografía**. Matplotlib no lee fontconfig: `font_manager.addfont()` +
> `rcParams["font.family"]`. Barlow **no trae** `→`, `⟨⟩`, `≡` ni U+2011, que caen
> a DejaVu: es esperado y PowerPoint hará lo mismo, **no es un defecto**.
> Procedimiento: `sprints/B7_sprint7/presentacion_b7/fuentes_barlow.md`.
>
> **ADDENDUM 30-jul-2026 — esa lista de glifos NO es exhaustiva, y en un deck de
> ECUACIONES la diferencia importa.** Barlow tampoco trae **griegas** (`α β ψ γ λ
> Σ`) ni `ℝ ∈ ⊗`. Con cuatro flechas el fallback era despreciable; con griegas en
> cada fórmula, no. El template embebe **Barlow + Cambria Math**, así que declarar
> Cambria Math en esos glifos era una opción real; se rasterizaron las variantes y
> **gana Barlow con el fallback** (las griegas de Cambria Math son serif finas y
> contrastan con el Barlow que las rodea). Sub/superíndices: `_add_runs()` con
> `baseline` OOXML, y **escapar el `_` de los nombres de archivo** (`model\_clam.py`,
> si no queda «model_lam.py»). Detalle: [[deck-template-fuentes-embebidas]] y
> `sprints/B8_sprint8/presentacion_b8/README.md`.
>
> **Y la causa raíz de un deck que "no se ve como el template" suele ser
> tipográfica, no de branding**: los templates **embeben sus fuentes** y
> `Presentation()` (default de python-pptx) no embebe ninguna → PowerPoint
> sustituye Barlow y el deck se ve fuera de template aunque el branding esté
> perfecto. **Regla: construir el deck SOBRE el .pptx del template** (abrirlo y
> borrarle las láminas), nunca con `Presentation()`. Detalle y método de
> verificación: [[deck-template-fuentes-embebidas]].
>
> **ADDENDUM 19-jul-2026 (noche) — migrar la cabecera NO es migrar el deck.** Tras el
> re-base, el branding estaba y el cuerpo seguía en la paleta de B4: **18 de 22 láminas**
> con colores que Deep-LLM-V no tiene (incluida una familia naranja entera), y las tiras
> de bloques dibujadas como **claro-con-texto-teal**, que es el **negativo** del molde. La
> gramática real del template son cinco arquetipos: **proceso** = rounded-rect `#3E6877`
> con Barlow bold **BLANCO**; **dato** = rect `#B7B7B7` con Barlow negro; **panel** =
> rounded-rect `#CDDFE1`; **operador** = óvalo `#CDDFE1` borde `#0E2841`; **conector** =
> línea `#386271` 2.37 pt. Mínimo tipográfico del template: **7 pt** (bloques a 12).
> **Regla: al re-basar un deck, auditar cuerpo y diagramas contra el template, no solo la
> cabecera** — y un diagrama viejo traído con `copy_diagram_scaled()` casi nunca se salva
> con restyling (el de B7 venía a 6 pt: hay que **recrearlo nativo**). Helpers listos en
> `sprints/B7_sprint7/presentacion_b7/generate_b7_deck.py`: `_proc` / `_dato` / `_grupo` /
> `_conn` + `pipeline_mammoth()` como ejemplo. Detalle: [[deck-gramatica-diagrama-deep-llm-v]].
>
> **ADDENDUM 19-jul-2026 (cierre) — «más visual, menos bullets» es criterio general.**
> Feedback de Ernesto sobre seis láminas a la vez: un bullet de dos renglones no se acorta,
> **se convierte en dibujo** si su contenido tiene forma (fracción → barra de proporción;
> comparación de tamaños → eje de escala; cuenta → cadena de bloques con la cuenta hecha;
> topología o anidamiento → diagrama). Lo que sobrevive como bullet queda de **una línea**;
> el resto va al guion hablado. Cuando la prosa compite con una tabla, **gana la tabla** (se
> agranda). Una figura del paper puede valer la lámina entera: si es el contenido, se le
> saca el título y todo lo que compita por el alto. Los cinco arquetipos son el vocabulario,
> no la sintaxis: el template usa además **dos tonos de bloque** (oscuro = camino principal,
> claro `#CDDFE1` = detalle interno), la **dimensión como etiqueta suelta** al lado del
> bloque, **expansión punteada** para abrir un bloque en su interior y **rótulo rotado** al
> costado del panel; y en sus láminas de arquitectura **no pone subtítulo ni barra de
> remate**. Helpers nuevos en el mismo generador: `ratio_bar`, `scale_axis`, `_proc_claro`,
> `_dim`, `_oper`, `_conn_dash`, `_rot_label`. Dos gotchas: un shape rotado 270° reporta el
> bbox **sin rotar** (falso positivo en chequeos de límites), y un `run <10pt` que no
> escribiste delata una **lámina sobrecargada** que `reflow_onco` comprimió. Detalle:
> [[deck-contenido-visual-no-bullets]] + [[deck-gramatica-diagrama-deep-llm-v]].

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
> Única excepción: **figuras externas de un paper** (van como imagen). **Precisión 3-ago-2026:
> la excepción cubre también las figuras de producción PROPIA que no se pueden dibujar con
> shapes** — un mapa de atención sobre tejido es la fotografía de un resultado, no un diagrama
> (deck B8, `atencion_dos_regiones.png` y las dos de mitosis). Lo que las acompaña sigue siendo
> nativo, incluida una escalera de AUC, que va como barras con la gramática del template y NO
> como PNG de matplotlib. El criterio real no es «de dónde salió la imagen» sino **si el objeto
> es dibujable**: tabla, gráfico o diagrama ⇒ nativo, siempre. Los PNG de
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
- `@grilling` — interroga por rondas (árbol de decisiones + frontera) hasta el
  entendimiento compartido, **antes** de escribir un `prereg.md`. Los hechos los busca
  ella con Read/Grep/Bash (sin subagentes); las decisiones son de Ernesto. Levanta en la
  1ª ronda si la premisa no calza ([[surface-premise-discrepancies]]) o si es decisión
  revisitada (regla 9.b). Aterriza en el prereg o en las secciones del mapa del sprint.
  Portada de mattpocock (`8b36d4f`) el 5-ago-2026.
- `@session-close` — rutina de cierre de sesión en 3 fases (orden estricto):
  documentar con `@knowledge-audit` → `@handoff` arrastrando TODOS los pendientes
  sin terminar → commit + push. Invocarla **es** la autorización de push (default
  del repo = "push lo hace Ernesto"); "sin push" la deja en commits locales.
  Triggers — "cerrar sesión", "rutina de cierre".

## Contexto del usuario para sesiones rápidas

Idioma: **español**. Tono: técnico + explicativo. No simplificar conceptos
generales de ML/DL/CV. SÍ explicar pedagógicamente al introducir notación
específica del subcampo (MIL, weakly-supervised, computational pathology).
