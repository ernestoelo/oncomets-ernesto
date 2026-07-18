# Hallazgos — ejecución: generación de splits CDIS/LVI + lanzamiento del entrenamiento (17-jul-2026, tarde/noche)

> Continúa `hallazgos_sesion_reformulacion_sebastian_17jul.md` (R1-R5). Esa sesión dejó
> la formulación aceptada por Sebastián + el plan de generación; **esta sesión lo EJECUTÓ**:
> generó los splits, pasó 2 reviewers, y lanzó el entrenamiento de las 3 tareas.
> Branch: main. GPU: **job 4589 RUNNING** (workaround H activo — esta auditoría es documental,
> no toca inputs del job ni cambia de rama). `origin/main`: 2 commits locales por delante
> (se pushean al cierre de esta sesión, autorizado por Ernesto).

## Qué se ejecutó (la parte que estaba "pendiente" en R5)

| id | avance | evidencia | estado |
|----|--------|-----------|--------|
| E1 | **Splits CDIS/LVI `_ci_reform` GENERADOS + verificados** (ejecuta el plan de R5) | `data/splits_kfold/{carcinoma_ductal_insitu_presente,invasion_linfatica_vascular}_ci_reform_100/` (5 folds c/u), snapshots en `data/csv_new_tasks/*_ci_reform_label.csv`. Commit `1fe7436` | ✅ cerrado |
| E2 | **`tipo_histologico` `_ci` = 3 clases** pese al nombre `_4clases`; snapshot 3-clase creado | `data/csv_new_tasks/dataset_tipo_histologico_3clases_ci_label.csv` (2027 slides, cubre EXACTO el `_ci` de Sebastián: 0 fuera, 0 sin `.pt`). Commit `acbae5f` | ✅ cerrado |
| E3 | **slurm cableado para las 3 tareas + fix de régimen** | `run_b7_mammoth_interp_kfold.slurm`: prereqs A (formulación) y B (splits) resueltos; `max_epochs 30→200` (el draft con `stop_epoch 50` **nunca disparaba early stopping** = subentrenaba a 30 fijas). Commit `acbae5f` | ✅ cerrado |
| E4 | **Prereg + 2 reviewers PASA + `sbatch` lanzado** | `prereg_entrenamiento_interp.md`; reviewer #1 (script splits) PASA; reviewer #2 (slurm+prereg) PASA; **job 4589 RUNNING** (30 runs: 3 tareas × {CLAM, Mammoth} × 5 folds) | ✅ en curso |
| E5 | **Naming `_ci_reform` CONFIRMADO por Ernesto** (era la única decisión abierta de R5) | AskUserQuestion → `_ci_reform` (no pisa los `_ci` superseded de Sebastián) | ✅ cerrado |

## Verificación (regla 5 + regla 10) — re-hecha esta sesión, no reusada

- **Números re-computados en disco** (no del handoff): CDIS {si:730, no:132} n=862; LVI {ausente:470,
  presente:366} n=836 — coinciden con R2/R5.
- **10/10 folds OK** (cross-check inline): disjunción train/val/test, total constante, **0 sin `.pt`,
  0 duplicados, 0 fuga de paciente** (`patient_strat`), y conteos por clase == `_descriptor` (regla 10).
- **tipo `_ci`**: los 2027 slides del split (unión de 5 folds) están 100% en el CSV 3-clase filtrado,
  0 con label fuera de las 3 clases, 0 sin `.pt`.
- **Validación CPU pre-submission** (de-risk del `sbatch`): `import mammoth` OK, `tests/test_mammoth_cpu.py`
  PASA, `preflight_minpatch.py` fold 0 de las 3 tareas OK.

## Gotchas críticos (para futuras sesiones)

1. **`tipo_histologico_4clases_ci_100` contiene 3 clases**, no 4 (el `no_identificado` ya está excluido
   por el gate). El `label_dict` del slurm debe usar los **strings completos** del CSV
   (`carcinoma_invasivo_tipo_no_especifico`, `carcinoma_lobulillar_invasivo`, `otros`), no abreviaturas.
   → registrado en [[formulacion-cascada-gate-invasivo]] y [[sprint7-interpretabilidad-clam-vs-mammoth]].
2. **Régimen de entrenamiento**: `max_epochs` debe ser **> `stop_epoch`** o el early stopping nunca
   dispara (el harness lo warnea, L634-639 de `train_dsmil.py`). Usar el bendecido: `max_epochs 200`,
   `stop_epoch 50`, `patience 20`.
3. **CRLF Windows** en `dataset_invasion_linfovascular_label.csv` (gotcha [[data-gotchas-csv-wsi-interp]])
   → el generador limpia con `.str.strip()` en `case_id/slide_id/label`. Cubierto.
4. **Snapshots con nombres distintivos** (`*_ci_reform_label.csv`, `*_3clases_ci_label.csv`) para NO
   pisar el `dataset_invasion_linfovascular_label.csv` viejo (3-clase) que ya vive en `data/csv_new_tasks/`.
5. **Instrumento, no rendimiento**: el entrenamiento NO reclama que Mammoth gane métrica (Hallazgo 12
   cerrado). Es para producir checkpoints y comparar mapas de atención vs ruteo. `val_auc=nan` en tipo
   3-clase es NORMAL (checkpoint por `val_loss`).

## Propagación a los frentes (fixes de esta auditoría)

- **progress/current.md** §B7: el bloque "Pendiente real" (generar splits + re-entrenar) pasa a
  EJECUTADO (E1-E4, job 4589); añadida la línea de `/knowledge-audit` de esta sesión.
- **Memorias** (ADDENDUM 17-jul noche): [[formulacion-cascada-gate-invasivo]] y
  [[sprint7-interpretabilidad-clam-vs-mammoth]] — de "pendiente generar" a "generado + entrenando";
  gotcha tipo `_4clases`=3. [[data-gotchas-csv-wsi-interp]] — CRLF cubierto por el generador.
- **MEMORY.md**: líneas de índice de las memorias tocadas.
- **CLAUDE.md**: SIN cambios — es estado de sprint (interpretabilidad), no una regla durable ni un
  Hallazgo de eje nuevo. El instrumento no reabre el veredicto de arquitectura (Hallazgo 12).

## Guardarraíles respetados
- Read-only sobre `clam_environ/`; todo output bajo el repo. Ediciones documentales aditivas (ADDENDUMs).
- Workaround H: job 4589 en curso → no cambié de rama ni edité inputs del job (splits, CSVs,
  `train_dsmil.py`, el slurm) durante la auditoría. GPU no tocada.
- Pre-registro (regla 9) NO reescrito retroactivamente; los números de R2/R5 quedan como histórico.
