# Hallazgos — auditoría de coherencia · inspección `_ci` + SB6 (16-jul-2026)

> Continúa `hallazgos_sesion_magnif_paths_15jul.md` (M1-M4) y `hallazgos_sesion_sebastian_15jul.md`
> (SB1-SB6). Registra la **inspección read-only de los artefactos `_ci`** que dejó Sebastián en
> `clam_environ/environ/` (los "nuevos splits en carpeta nueva" que confirmó el 15-jul), la
> resolución de **SB6**, y la **decisión de Ernesto: reusar los `_ci` para todas las pruebas de B7**.
> Doc ANTES de los fixes (regla del skill). Branch: main (documental). GPU: **libre** (`squeue`
> vacío; el job ajeno `4588 mammoth_ sgaete` terminó durante la sesión). `origin/main` en sync (0/0).
> Todo lo de esta sesión fue **read-only** sobre `clam_environ/`; sin GPU, sin `sbatch`.

## Contexto (por qué esta auditoría)

El handoff `handoff_B7_gate_paths_prevencion_20260715_1745.md` dejaba como misión inspeccionar
read-only `environ/*_ci*` antes de generar splits, verificar SB6 (`patch_size_level0:512`) y decidir
reuse-vs-generar. Esta sesión ejecutó esa inspección, verificó todo contra el disco (regla 5/10) y
Ernesto cerró la decisión: **reusar los `_ci`**.

## Qué dejó Sebastián (verificado en disco, read-only)

Dejó la **suite completa de la cascada (8 tareas)**, no solo las 3 de B7:

- `clam_environ/environ/csv_balance_ci/` — 8 CSVs `dataset_<task>_ci_label.csv` (schema `case_id,slide_id,label`).
- `clam_environ/environ/splits_5fold_balance_ci/` — 8 carpetas `<task>_ci_100/`, **5 folds** cada una
  (`splits_{0..4}.csv` + `_bool` + `_descriptor`), formato CLAM estándar. Owner `sgaete`, mtime 15-jul 18:00-18:01.

Las 8 tareas: `tipo_histologico_4clases`, `carcinoma_ductal_insitu_presente`, `invasion_linfatica_vascular`,
`grado_histologico_{grado_general, mitotic_rate, diferenciacion_tubular, pleomorfismo_nuclear}`,
`carcinoma_ductal_insitu_grado_nuclear` (todas con sufijo `_ci`).

## Tabla resumen

| id | hallazgo | tipo | sev | acción |
|----|----------|------|-----|--------|
| C1 | Los `_ci` son los "nuevos splits en carpeta nueva" confirmados el 15-jul; completos, 5-fold estratificado, **cross-check regla 10 limpio** (descriptor en sync, 0 missing, cubren el CSV). **Decisión Ernesto: reusarlos para todas las pruebas de B7.** | validación + decisión | alta | ADDENDUM memorias + progress; supersede prereq B del slurm draft ("generar splits") |
| C2 | **`no_identificado` se maneja distinto por tipo de tarea.** Multiclase `tipo_histologico`: no_id **descartado** (n=2027). Binarias CDIS/invasión: no_id **plegado en el negativo** (CDIS `no`=2005=636+1369; invasión `ausente`=2447=479+1968). **Difiere** de lo inferido del audio (SB4: CDIS `{no:636,si:810}`). Re-infla la mayoritaria (CDIS trivial 71%, invasión 87%). | contradicción / stale (supersede SB4) | alta | observación a Sebastián + ADDENDUM cascada |
| C3 | **Slide sin features en los splits.** `histai_1132_slide_H&E_0` NO tiene `.pt` en ninguna carpeta (solo máscara + process_list), pero está en CDIS (train de los 5 folds) e invasión (val f0/train f1-3/test f4) → **crashearía el training** (lo caza el preflight, workaround G). El job de GPU de sgaete **no** lo estaba extrayendo (features/pt_files intacta desde 27-jun; nunca apareció). | error / blocker | alta | observación a Sebastián; resolver antes de cualquier sbatch |
| C4 | `tipo_histologico_4clases_ci` tiene nombre stale: el contenido son **3 clases** (no_especifico/lobulillar/otros), no 4. | stale / cosmético | baja | observación a Sebastián (cosmético) |
| C5 | **SB6 RESUELTO.** `meta.json` de la interp de invasión = `patch_size_level0: 512.0` @ `level0_mag: 40×` → **tercera geometría** distinta de la vieja (224@×40) y del parche nuevo (448@×40→224). h5 de `features/h5_files/`, checkpoint 04-jun (features viejas). | verificación (cierra SB6) | media | marcar SB6 resuelto; refuerza re-entrenar invasión |
| C6 | **Números de memoria superseded por la base grande.** `objetivos_sprint7.md`/memorias citan tipo `{766/183/81}` (del CSV viejo `_4clases`, n=1396) y CDIS `{no:636,si:810}`. Los `_ci` reales usan el set completo: tipo `{1610/240/177}` n=2027, CDIS `{no:2005,si:810}` n=2815, invasión `{ausente:2447,presente:368}` n=2815. | stale | media | ADDENDUM con números reales + puntero |
| C7 | `objetivos_sprint7.md:25` describe invasión como "3 clases {ausente, no_identificado, presente}" → superseded por la binaria `_ci` {ausente, presente}. | stale | baja | ADDENDUM |

## Detalle y verificación

### C1 — Los `_ci` validados; decisión de reusar
- Cross-check regla 10 para las 3 tareas de B7: para cada fold, join `splits_N.csv ⨯ dataset_<task>_ci_label.csv`
  → `missing_in_label=0`, distribución del descriptor == join, `train+val+test` == CSV completo. Descriptor NO stale.
- Presencia de features: tipo 2027/2027 con `.pt`; CDIS e invasión 2814/2815 (falta 1 → C3).
- Distribuciones reales (`value_counts`, verdad de campo):

  | tarea `_ci` | n | distribución |
  |---|---|---|
  | tipo_histologico | 2027 | no_especifico 1610 · lobulillar 240 · otros 177 |
  | CDIS_presente | 2815 | no 2005 · si 810 |
  | invasión | 2815 | ausente 2447 · presente 368 |

- Cita textual (cabecera de los CSV, mismo `slide_id`/orden en CDIS e invasión = mismo set de 2815;
  tipo arranca en `patient_6` porque patient_0-5 eran no_id descartados):
  - CDIS: `patient_0,B25-158771_2,no` / `patient_1,110379,no`
  - invasión: `patient_0,B25-158771_2,ausente` / `patient_1,110379,ausente`
  - tipo: `patient_6,AP_494_OT_1808_15-0559_MxBr_107_HE,carcinoma_invasivo_tipo_no_especifico`
- **Decisión (Ernesto, esta sesión): reusar los `_ci` para todas las pruebas.** Esto **resuelve el prereq B**
  del `run_b7_mammoth_interp_kfold.slurm` ("splits+CSV NO existen → generar"): ahora existen (los de Sebastián).
  El `.slurm` apuntará a `environ/splits_5fold_balance_ci/<task>_ci_100` (paired). NO regeneramos splits.

### C2 — `no_identificado` plegado en las binarias (aritmética exacta)
- CDIS original (`objetivos_sprint7.md`): `{no:636, no_id:1369, si:810}`. En `_ci`: `no = 2005 = 636 + 1369`.
- invasión original (`dataset_invasion_linfovascular_label.csv`): `{ausente:479, no_identificado:1968, presente:368}`.
  En `_ci`: `ausente = 2447 = 479 + 1968`.
- tipo original (`dataset_tipo_histologico_4clases_label.csv`, n=1396): `{no_especifico:766, no_id:366, lobulillar:183, otros:81}`.
  En `_ci` (base 2815): `2815 − 788(no_id) = 2027`; `otros:177` = suma de los subtipos invasivos raros del CSV completo
  `dataset_tipo_histologico_label.csv` (mixto 41 + mucinoso 39 + metaplásico 20 + … = 177).
- **Lectura:** binarias → "reporte no menciona" queda como negativo (no/ausente); multiclase → "no menciona" se descarta.
  Es **defendible** (en una binaria de presencia, no-mencionado ≈ ausente) y puede ser intencional, pero **difiere** de
  lo inferido en SB4 y **re-infla la mayoritaria** (el problema de microcalc, Hallazgos 6-10) → **confirmar con Sebastián**.

### C3 — Slide sin features en los splits
- `histai_1132_slide_H&E_0`: `find environ/ -iname "*histai_1132*"` → solo `patches/masks/histai_1132_slide_H&E_0.jpg`
  y `patches/process_list_histai_1132.csv`. **Ningún `.pt`** (ni en `features/pt_files`, ni en backups).
  → fue pareado pero la extracción CONCH nunca completó para ese slide.
- Está en los splits: CDIS `train` de los 5 folds; invasión `val` f0, `train` f1-f3, `test` f4.
- El job GPU `4588 mammoth_ sgaete` **no** era una extracción (nombre = training; `features/pt_files` sin escrituras
  desde 27-jun; el `.pt` de histai_1132 nunca apareció; `scontrol`/`ps` de otro user restringidos → conclusión por evidencia).
- **Acción:** o se le extraen features a ese slide, o se saca del CSV/split, antes de cualquier `sbatch`. El preflight
  (workaround G) lo cazaría en segundos, pero mejor resolverlo con Sebastián de una.

### C5 — SB6 resuelto (`patch_size_level0: 512`)
- `sprints/B7_sprint7/interpretabilidad_invasion/TCGA-AR-A24L_invasion_f0/meta.json`: `patch_size_level0: 512.0`,
  `level0_mag: 40.0`, `h5: environ/features/h5_files/TCGA-AR-A24L-…​.h5`, `ckpt: results/obj2_mammoth/…_20260604_0952_s1`.
- 512 px @ ×40 (0.2325 µm/px) = **119 µm** de campo → distinto de 224@×40 (52 µm, features viejas) y de 448@×40→224
  (104 µm, parche nuevo). Tercera geometría → los heatmaps de invasión de esa corrida están sobre una grilla que NO
  coincide con las features de entrenamiento. Refuerza **re-entrenar invasión sobre las features actuales** (SB2) y
  regenerar h5 consistente antes de sacar conclusiones geométricas.

## Fixes aplicados (esta sesión)
1. Este doc de hallazgos (C1-C7) — deliverable primero.
2. Memoria [[formulacion-cascada-gate-invasivo]]: ADDENDUM 16-jul — `_ci` inspeccionados + reuso decidido;
   el plegado de no_id en binarias (C2, difiere de {no:636}); distribuciones reales.
3. Memoria [[sprint7-interpretabilidad-clam-vs-mammoth]]: ADDENDUM 16-jul — reuso `_ci` (prereq B resuelto),
   slide sin features (C3), SB6 resuelto (512).
4. Memoria [[data-gotchas-csv-wsi-interp]]: línea del slide sin features `histai_1132` en splits `_ci`.
5. `progress/current.md` §B7: inspección `_ci` + decisión reuso; SB6 resuelto; observaciones pendientes; C3.
6. `sprints/B7_sprint7/objetivos_sprint7.md`: ADDENDUM formulación real (`_ci`) + prereq B resuelto.
7. `MEMORY.md`: líneas de índice de las memorias tocadas.

## Guardarraíles respetados
- Read-only absoluto sobre `clam_environ/` (solo lectura de CSV/splits/features/meta.json). Sin `sbatch`, sin GPU.
- Sin cambio de rama ni edición de versionados con job ajeno corriendo (workaround H); al terminar 4588, GPU libre.
- Ediciones a memorias/docs = **aditivas** (ADDENDUM + punteros); no se reescriben pre-registros ni reglas duras.
- Números `_ci` reales dejan como **superseded** (no borrados) los de memoria; el histórico queda citable.
- Binarios `.pptx`/`.pdf` de B7 NO tocados (gitignored).

## Observaciones para Sebastián (derivadas — las relaya Ernesto)
1. (C2) En las binarias `no_identificado` quedó como negativo (CDIS `no`=2005=636+1369; invasión `ausente`=2447=479+1968);
   en tipo se descartó. ¿Intencional? Re-infla la mayoritaria (CDIS trivial 71%, invasión 87%).
2. (C3) `histai_1132_slide_H&E_0` está en los splits de CDIS e invasión pero no tiene features CONCH → crashea el training.
3. (C4) `tipo_histologico_4clases_ci` tiene nombre "4clases" pero contenido de 3 clases (cosmético).
