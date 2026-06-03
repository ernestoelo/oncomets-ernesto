# Objetivo 2 B5 — Mammoth en CLAM: patrón arquitectónico (4 binarias) + invasión linfática (3 clases), k=5 paired

> Arrancado 2026-06-02 tras reunión con Sebastián. Foco de la semana: estudiar
> mammoth + entrenar **CLAM con y sin mammoth** en estas dos tareas, k=5, y evaluar
> si el modelo mejora. Mammoth ya está portado y validado (Obj 6 / job 4229); acá se
> **aplica a tareas nuevas** (no se toca el modelo). Reusa el harness
> `scripts/train_dsmil.py` (`--model_type clam | clam_mammoth`).

## Contexto y clases (referencia CAP)

Las clases provienen de los **protocolos CAP** (College of American Pathologists)
que usan los patólogos en EE.UU. — `papers/Breast.Invasive.Bx_1.2.0.0.REL_CAPCP.pdf`,
sección *Ductal Carcinoma In Situ*:

- **Patrón arquitectónico** = *Architectural Patterns (select all that apply):*
  Comedo · Paget · **Cribriform · Micropapillary · Papillary · Solid**. Es
  **multi-label por definición** (una lesión puede ser cribiforme *y* sólido). En
  los datos Environ solo aparecen 4 patrones (Comedo/Paget = 0 slides) →
  **reformulado en 4 tareas binarias si/no** (igual jugada que microcalc 8→3).
- **Invasión linfática** = *Lymphatic and/or Vascular Invasion:* Not identified ·
  Present · Cannot be determined → **3 clases** {ausente, presente, no_identificado}.

## Diseño experimental

- **Tareas (cohorte `_pth` = privado+TCGA+HistAI, `no_identificado` excluido en las
  binarias):**

  | Tarea | CSV (read-only, `clam_environ/environ/csv/`) | clases | n | dist |
  |---|---|---|---|---|
  | `cdis_patron_cribiforme_pth` | `..._patrones_arquitectonicos_cribiforme_label.csv` | binaria | 513 | no 261 / **si 252** |
  | `cdis_patron_solido_pth` | `..._solido_label.csv` | binaria | 513 | no 125 / **si 388** |
  | `cdis_patron_micropapilar_pth` | `..._micropapilar_label.csv` | binaria | 513 | no 479 / **si 34** ⚠️ |
  | `cdis_patron_papilar_pth` | `..._papilar_label.csv` | binaria | 513 | no 481 / **si 32** ⚠️ |
  | `invasion_linfatica_vascular_pth` | `dataset_invasion_linfovascular_label.csv` | 3 clases | 2814 | no_id 1967 / ausente 479 / presente 368 |

  > **Snapshot + filtro de features**: los CSV se copian a `data/csv_new_tasks/`
  > filtrando slides sin `.pt` (`scripts/build_new_tasks_splits.py`). Invasión:
  > 2815 → **2814** (1 slide HistAI `histai_1132_slide_H&E_0` sin features). Patrón:
  > sin cambios (513/513 con `.pt`). El 513 = DCIS anotado **identificado** (810 −
  > 297 `no_identificado`) → universo correcto de las binarias.

- **Comparación PAIRED** ([[patron-paired-comparison-reuso-splits]]): ambos brazos
  (CLAM `clam` vs CLAM+mammoth `clam_mammoth`) sobre los **mismos splits k=5**
  generados en `data/splits_kfold/<task>_100/` (MC-CV estratificado, patient_strat,
  val_frac=test_frac=0.1, seed 1 — misma receta que Fase 0, vía
  `scripts/build_new_tasks_splits.py`). Único delta entre brazos = `--model_type`.
- **Config fija idéntica a microcalc** (job 4229, comparación real):
  `max_epochs 30 · early_stopping · patience 20 · stop_epoch 50 · B 8 ·
  bag_weight 0.7 · lr 2e-4 · reg 1e-5 · drop_out 0.25 · embed_dim 512 · seed 1`.
  Mammoth (defaults paper): `experts 30 · slots 10 · heads 16 · slot_dim 256 ·
  dropout 0.1 · keep_slots False · share_lora_weights True · auto_rank True`.
- **label_dict**: binarias `{"no":0,"si":1}`; invasión
  `{"ausente":0,"no_identificado":1,"presente":2}` (orden alfabético = auto-label-dict).
- **Cohorte de seguimiento**: `_balance` solo para `micropapilar`/`papilar` (32-34
  positivos, donde el cap sí cambia la distribución) — variante posterior, no en la
  1ª pasada.

## Argumento (regla 9)

- **Clínico/arquitectónico:** mammoth ataca *instance-gradient interference* —
  parches de fenotipos distintos en una slide tiran gradientes en conflicto sobre la
  1ª capa lineal; el ruteo a expertos los separa. Patrón arquitectónico (patrones
  morfológicos coexistentes en la misma lesión) e invasión linfática (foco invasor
  disperso en estroma heterogéneo) son tareas con **alta heterogeneidad de fenotipos
  por slide + desbalance** → el mecanismo aplica. Pedido explícito de Sebastián.
- **NO es reapertura (regla 9.b NO aplica):** son **tareas nuevas**, no un eje
  descartado que se reabre. (El cierre de DSMIL fue sobre el *agregador* en
  microcalc; esto es mammoth sobre el *patch-embed* en otras tareas.) **Antecedente
  Eduardo:** corrió mammoth sobre `cdis_patron_papilar` en sweeps single-split
  (`sprints/B4_sprint4/objetivo_6_mammoth/eduardo_snapshot/key_sources/ESTUDIO_papilar_v2.md`,
  V1-V3, 29-may), pero **sin veredicto NO-GO** — su propia conclusión (§5) fue que el
  single-split es "estadísticamente ciego" (3 positivos → AUC cuantizado) y que **el
  fix correcto es K=5 estratificado**. Este Obj 2 es esa K=5 que él recomendó (y
  decide por balanced_acc + Δ pareado, no por el AUC que él mismo invalidó) →
  **continuación del autor original, no reapertura de un eje cerrado**.
- **Expectativa informada por el job 4229 (microcalc):** mammoth resultó **nulo/leve-
  mixto** en las 3 binarias de microcalc (cuello = datos, no arquitectura). Por eso
  acá **no se promete mejora**: se mide. Invasión linfática tiene mucho más n (2815
  vs ~330) → mejor chance de señal estable; patrón micropapilar/papilar (32-34 pos)
  está en régimen ruidoso tipo-microcalc.

## Hipótesis pre-registrada (regla 9 + 9.a — sin gate numérico, política B5)

Aplica **por tarea** (5 comparaciones paired independientes):

- **Métrica decisiva:** `balanced_acc` (test), **Δ pareado por fold** = `mammoth_f −
  clam_f`, media ± std (k=5).
- **Secundaria (se reporta SIEMPRE, no decide):** AUC — binarias = ROC-AUC; invasión
  = **macro one-vs-rest** (requiere fix de métricas multiclase en `train_dsmil.py`,
  ver Decisiones técnicas #1). Política B5: balanced_acc **y** AUC juntos + matriz de
  confusión + n por clase. Nunca AUC aislado (Hallazgo 6).
- **Dirección esperada (H1 primaria):** mammoth mejora ⇒ **Δ pareado > 0 consistente
  en signo** a través de los 5 folds, con la varianza sin aplastar el efecto.
- **H0 (alternativa):** Δ en banda ambigua (signo mixto entre folds, ó |media| < std)
  ⇒ mammoth no es palanca a esta escala ⇒ refuerza "el cuello es datos".
- **Regresión:** Δ < 0 **consistente en signo** (≥4/5 folds) y con magnitud que no
  cruza 0 de forma trivial ⇒ mammoth perjudica (como DSMIL/mammoth en CDIS).
- **Sin umbral-gatillo** (regla 9.a): no hay `Δ≥+0.03 ⇒ éxito` automático. Se
  interpreta cualitativamente: consistencia de signo, magnitud de varianza, si supera
  el **trivial** (binarias 0.5; invasión 3-clase **0.333**).
- **Lectura especial micropapilar/papilar (3 positivos/test fold):** régimen
  "estadísticamente ciego" (mismo cuello que el papilar single-split de Eduardo) —
  balanced_acc y AUC se mueven en saltos gruesos por fold. El resultado primario en
  estas dos se lee **agregando los ~15 positivos de los 5 folds** (sensibilidad /
  especificidad global), NO fold a fold. La variante `_balance` (sube la fracción
  positiva) queda como seguimiento si el agregado no concluye.
- **Mecanismo a verificar:** convergencia del bag-loss + `clustering_loss`;
  `|grad W_0|` y `|grad q|` **> 0** en el brazo mammoth (en el brazo `clam` valen 0).
  Para invasión, vigilar **colapso a `no_identificado`** (mayoritaria 70%) vía la
  matriz de confusión 3×3.

## Decisiones técnicas del harness (a validar con reviewer)

1. **Fix de métricas multiclase en `scripts/train_dsmil.py`** (nuestro repo, NO
   `clam_environ`): `compute_test_metrics` hoy solo computa AUC para `n_classes==2`
   (L424-425). Para invasión (3 clases) se agrega: (a) macro-OVR AUC cuando
   `n_classes>2`, (b) guardar las probs de las 3 clases en `test_predictions.csv`.
   Cambio **idéntico para ambos brazos** y para binarias/multiclase → no rompe el
   pareo ni la reproducibilidad de microcalc (la rama `n_classes==2` queda igual).
   El reviewer lo valida como parte del checklist.
2. **`keep_slots=False`** (igual que Obj 6): preserva los N parches → semántica de
   attention/instance-loss idéntica al baseline.
3. **Preflight obligatorio** (workaround G) por fold + `verify_kfold_splits.py`
   extendido a las nuevas tareas + `test_mammoth_cpu.py` antes de gastar GPU.

## Estado

- [x] Clases confirmadas contra CAP + Sebastián (4 binarias patrón, 3 clases invasión).
- [x] Hipótesis pre-registrada (este doc).
- [x] Splits k=5 (`scripts/build_new_tasks_splits.py` → `data/splits_kfold/`; verify rc=0).
- [x] Fix métricas multiclase (`train_dsmil.py`) + slurm + test CPU (3-clase, pasa).
- [x] reviewer **GO con observaciones** (2-jun; aplicadas obs 1/2/3).
- [~] sbatch GROUP=patron **LANZADO 2-jun (job 4241) y CRASHEÓ** tras 1/40 runs
  (cribiforme f0 CLAM OK). Causa: branch-switch en el working-tree compartido borró
  `data/csv_new_tasks/` durante el job → `FileNotFoundError` en fold 1 (workaround H
  de CLAUDE.md, [[working-tree-compartido-job-en-curso]]). **Re-lanzar desde `main`**
  (ya tiene CSVs+splits tras el merge de cierre) **sin cambiar de rama durante el job**.
- [ ] 2ª ola: invasión 3-clase (GROUP=invasion, ~25h) — no lanzada (con OK + cortesía GPU).
- [ ] Resultados (`objetivo_2/resultados.md`, política eval B5) + README en `clam_testing/`.
