# Auditoría de coherencia — respuestas de Sebastián (15-jul-2026)

> Continúa `hallazgos.md` (apertura B7, 13-jul). Registra las **respuestas de Sebastián**
> (WhatsApp + audio 14-15 jul) a las dudas de magnificación y formulación de tareas, ya
> **verificadas contra su código y el disco** (regla 5). Doc ANTES de los fixes.
> Branch: main (documental). GPU: job ajeno `4584 mammoth_ sgaete` CORRIENDO → auditoría
> solo-documental sobre `oncomets-ernesto` + memorias, sin tocar `clam_environ` (de donde
> lee su job), sin cambio de rama (workaround H respetado). `origin/main` en sync (0/0).

## Resumen (id · hallazgo · tipo · acción)

| id | hallazgo | tipo | acción |
|---|---|---|---|
| SB1 | **Magnificación VERIFICADA:** Sebastián usó **448 px @ ×40** en TCGA (`--patch_size 448 --step_size 448`) + `--target_patch_size 224` a CONCH → misma área física (104 µm) que 224@×20, distinta resolución. Privado+HistAI a ×20 sin cambio. Confirma la matemática de `contexto_magnificacion.md` | validación (cierra S6, A VERIFICAR→VERIFICADO) | slurm refs + VALIDADO en `contexto_magnificacion.md` + ADDENDUM [[magnificacion-cpathagent-proxima-direccion]] |
| SB2 | **CRÍTICO — el drift de features del 26-27 jun ES este parche.** Reemplazó las TCGA en la carpeta canónica `environ/features/pt_files` (mtime 27-jun) por las nuevas 448→224; backup de las viejas 224@×40 en `environ/features_tcga_224x40` (864 slides). El checkpoint mammoth de invasión es del **04-jun** → entrenado con las features VIEJAS | hallazgo crítico | memoria [[features-tcga-drift-reextraccion]] EXPLICADA + CLAUDE.md ⚠ |
| SB3 | **CRÍTICO — cambio de formulación de tareas (audio).** Sebastián introduce un **pipeline en cascada**: gate binario carcinoma-invasivo sí/no a la entrada → las positivas pasan a los clasificadores downstream **sin `no_identificado`** (el gate los saca). Todos los clasificadores de abajo entrenan solo con las clases reales. Dejó código del gate en el server | decisión de proyecto (durable) | memoria nueva `formulacion-cascada-gate-invasivo` + `sprint7` |
| SB4 | **Formulación de las 2 tareas — respondida parcial.** `carcinoma_ductal_insitu_presente` = **binaria** {no:636, si:810} sacando no_identificado (1369). `tipo_histologico` = NO dio el listado; aplica el principio (sacar no_id) → probable 3-clase {no_especifico:766, lobulillar:183, otros:81}, **a confirmar**. Splits: no respondió reuso vs regenerar | pendiente | mensaje de seguimiento (próxima sesión) |
| SB5 | **Reconciliación con B6:** el fix de Sebastián = **escala única común (~104 µm ≈ nuestra fina 112 µm)**, NO pirámide. Equivale al brazo **B0 (fine-only @ grid común)** del pre-registro. Nuestra multi-escala AGREGA contexto 512 µm encima → complementarios, no compiten | reconciliación | ADDENDUM `prereg`/memoria magnif |
| SB6 | **Discrepancia a verificar:** el `meta.json` de la interpretabilidad de invasión dice `patch_size_level0: 512` (ni 256 viejo ni 448 nuevo) → chequear con qué geometría se generó ese `.h5` antes de sacar conclusiones de esos heatmaps | gotcha / a verificar | anotado en `contexto_magnificacion.md` + handoff |

## Detalle

### SB1 — Magnificación (VERIFICADO contra su código)
- `run_create_patches_tcga_sc.slurm:14-23`: `create_patches_fp.py --source .../TCGA_dataset_curated
  --patch_size 448 --step_size 448 --preset bwh_biopsy.csv --seg --patch --stitch --nested_folders`.
- `run_extract_features_tcga_sc.slurm:27-35`: `extract_features_fp.py --data_h5_dir environ/patches_tcga_sc/patches
  ... --feat_dir environ/features_tcga_sc --model_name conch_v1 --target_patch_size 224 --nested_folders`.
- A ×40 (0.2325 µm/px) 448 px = 104.2 µm de campo = igual que 224 px a ×20 (0.465 µm/px). El `target 224`
  baja 448→224 antes de CONCH: **misma área física, resolución nativa distinta** (TCGA capturó fino y bajó).
- Confirma `contexto_magnificacion.md` §Q2 y tu cálculo (448 px). WhatsApp de Sebastián: "para 40x use 448 ...
  eso en las WSI de tcga. La data privada e histai está a 20x".

### SB2 — El drift ES el parche (verificado en disco)
- `environ/features/pt_files`: 3013 total; los `.pt` de TCGA tienen mtime **2026-06-27** (los privados/marzo no).
- `environ/features_tcga_224x40/pt_files`: **864** = backup de las TCGA viejas (224@×40, medio campo físico).
- `environ/features_tcga_sc/pt_files`: **vacía** (las movió a `features/`, coincide con su WhatsApp:
  "Reemplacé directamente las nuevas features en la carpeta features, las de 224 creo que las copie en una
  carpeta en el mismo directorio").
- **Checkpoint invasión** (`results/obj2_mammoth/.../clam_mammoth_invasion_linfatica_vascular_pth_f0_20260604_0952_s1`)
  = **04-jun** < 27-jun → entrenado con las features viejas. Re-inferir hoy sobre `features/` = mismatch de escala.
- **Recomendación para el sprint:** como las 2 tareas nuevas se entrenan de cero, **re-entrenar también invasión**
  sobre las features actuales deja las 3 tareas sobre la misma extracción → comparación CLAM vs Mammoth consistente.

### SB3 — Pipeline en cascada (cambio de formulación, audio 14-jul)
Transcripción del audio (parafraseada): trabajan con el **protocolo de carcinoma invasivo** → solo se
categorizan WSI de carcinoma invasivo. Cambio que quiere hacer: **un clasificador binario a la entrada
(carcinoma invasivo / no)**. Las WSI que dan invasivo pasan a los clasificadores de abajo, que entrenan
**solo con Score/grado 1-2-3, sin `no_identificado`** (el gate ya los descartó). "Esto aplicará para
todas las tareas". Ej. dado: DCIS queda en **dos clases (presente/no)**. Dejó el código del gate en el server.
→ Es una **decisión de arquitectura de pipeline** de Sebastián, no solo un número de clases.

### SB4 — Las 2 tareas (distribuciones de `objetivos_sprint7.md`)
- `carcinoma_ductal_insitu_presente` {no:636, **no_id:1369**, si:810} → binaria sacando no_id = {no:636, si:810}.
- `tipo_histologico` `_4clases` {no_especifico:766, lobulillar:183, **no_id:366**, otros:81} → sacando no_id
  = 3 clases {no_especifico:766, lobulillar:183, otros:81}. **Sebastián no lo enumeró → confirmar.**
- **Splits**: no respondió reuso vs regenerar; como cambian formulación (drop no_id) + features (TCGA), lo
  probable es regenerar. Generar splits toca data-pipeline → **regla 9 + reviewer** antes de correr.

## Fixes aplicados (esta sesión)
1. `contexto_magnificacion.md`: sección **VALIDADO 15-jul** (SB1/SB2/SB5/SB6), A-VERIFICAR→VERIFICADO.
2. Memoria [[features-tcga-drift-reextraccion]]: drift **EXPLICADO** (= parche magnif; backup; checkpoint 04-jun).
3. Memoria [[magnificacion-cpathagent-proxima-direccion]]: ADDENDUM 15-jul (448 verificado; escala única = B0).
4. Memoria nueva `formulacion-cascada-gate-invasivo` (SB3) + línea en `MEMORY.md`.
5. Memoria [[sprint7-interpretabilidad-clam-vs-mammoth]]: formulación respondida + drift → re-entrenar las 3.
6. `progress/current.md`: sección B7 con las respuestas de Sebastián + pendientes.
7. CLAUDE.md: ⚠ de `features/pt_files` enriquecida (causa del drift + backup).

## Guardarraíles respetados
- **Job GPU ajeno `4584` corriendo** → sin `sbatch`, sin cambio de rama, sin tocar `clam_environ`/`clam_testing`
  (workaround H). Auditoría solo-documental sobre `oncomets-ernesto` + memorias en `~/.claude/`.
- Read-only sobre `clam_environ` (solo lectura de slurm/features/checkpoints).
- Ediciones a CLAUDE.md/memorias = aditivas (VALIDADO/ADDENDUM + punteros), sin reescribir reglas ni pre-registros.
- Binarios `.pptx`/`.pdf` de B7 NO tocados (gitignored).
