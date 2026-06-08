# Experimentos Mammoth en CLAM — OncoMets / Environ (config, datasets, splits, resultados)

> Autor: Ernesto Gamero · Sprint B5 (cierre trimestre jun-2026).
> **FUENTE CANÓNICA Y VERSIONADA** de este doc (vive en el repo, sobrevive a una
> pérdida del workspace y es citable desde GitHub). Si existe una copia en
> `clam_testing/`, es un stub/derivado — editá SIEMPRE acá.
> Doc de referencia para el equipo (Sebastián). Documenta, por tarea: la **config
> fija** de entrenamiento, el **dataset de origen** y el **n por clase**, el **split**
> usado (con rutas a los archivos), y los **resultados**.
>
> **Comparación central:** CLAM (baseline) **vs** CLAM+Mammoth, **k=5 paired** (mismos
> splits ambos brazos, único delta = la 1ª capa lineal → Mixture-of-Experts). Mismo
> harness `train_dsmil.py` (`--model_type clam | clam_mammoth`) → comparación
> apples-to-apples sin confound de training-loop.
>
> Todo el código/datos/resultados viven en `clam_testing2/oncomets-ernesto/`
> (este repo). Rutas de abajo: relativas al repo o con `$REPO`.

---

## 1. Config fija de entrenamiento (idéntica en TODAS las tareas y ambos brazos)

Args "bendecidos" (mismos que el baseline oficial Environ y que el run de microcalc):

| Arg | Valor | | Arg | Valor |
|---|---|---|---|---|
| `--model_type` | `clam` / `clam_mammoth` | | `--max_epochs` | 30 |
| `--B` (k_sample inst-loss) | 8 | | `--early_stopping` | sí |
| `--bag_weight` | 0.7 | | `--patience` | 20 |
| `--lr` | 2e-4 | | `--stop_epoch` | 50 |
| `--reg` | 1e-5 | | `--seed` | 1 |
| `--drop_out` | 0.25 | | `--embed_dim` (CONCH) | 512 |

**Hiperparámetros de Mammoth** (solo brazo `clam_mammoth`; defaults recomendados del
paper, `auto_rank` mantiene el conteo de params comparable a la lineal original):

| `num_experts` | `num_slots` | `num_heads` | `slot_dim` | `dropout` | `keep_slots` | `share_lora_weights` | `auto_rank` |
|---|---|---|---|---|---|---|---|
| 30 | 10 | 16 | 256 | 0.1 | **False** | True | True |

> `keep_slots=False` → Mammoth devuelve los N parches transformados (misma semántica
> de attention/instance-loss que el baseline → comparación limpia).
> Features: **CONCH 512-dim** (todas las slides). Instance-loss: `SmoothTop1SVM`.
> Sampler de train: `weighted` (corrige desbalance de clases).

---

## 2. Tareas, clases, n por clase y dataset de origen

**Cohorte `_pth` = Privado (Environ) + TCGA + HistAI** (la unión grande). Para las
binarias de patrón se excluye `no_identificado` (slides cuyo reporte CAP no menciona
el patrón) → universo = DCIS **identificado**.

### 2.a Patrón arquitectónico de CDIS — 4 tareas BINARIAS (si/no)

Clases = patrones del protocolo CAP (`papers/Breast.Invasive.Bx_1.2.0.0.REL_CAPCP.pdf`,
*DCIS → Architectural Patterns*, "select all that apply" → multi-label → 1 binaria por
patrón). n total por tarea = **513** (idéntico universo; cada slide es si/no para cada
patrón). Fuente: **HistAI 200 + TCGA 238 + Privado 75**.

| Tarea (`--task`) | clase `si` | clase `no` | desbalance | régimen |
|---|---|---|---|---|
| `cdis_patron_cribiforme_pth` | 252 | 261 | ~1:1 | sano |
| `cdis_patron_solido_pth` | 388 | 125 | ~3:1 | ok |
| `cdis_patron_micropapilar_pth` | 34 | 479 | 14:1 | **3 pos/test fold — "estadísticamente ciego"** |
| `cdis_patron_papilar_pth` | 32 | 481 | 15:1 | **3 pos/test fold — idem** |

CSV de labels (snapshot filtrado a slides con `.pt`):
`$REPO/data/csv_new_tasks/dataset_carcinoma_ductal_in_situ_patrones_arquitectonicos_<patrón>_label.csv`

### 2.b Invasión linfática (linfovascular) — 1 tarea de 3 CLASES

Clases = CAP *Lymphatic and/or Vascular Invasion* (Not identified / Present / Cannot
be determined). n total = **2814** (1 slide HistAI `histai_1132_slide_H&E_0` sin `.pt`,
excluida del crudo 2815). Fuente: **HistAI 1418 + TCGA 864 + Privado 532**.

| Tarea (`--task`) | `no_identificado` | `ausente` | `presente` | trivial bal_acc |
|---|---|---|---|---|
| `invasion_linfatica_vascular_pth` | 1967 (70%) | 479 | 368 | 0.333 |

`label_dict = {"ausente":0, "no_identificado":1, "presente":2}` (`--n_classes 3`).
CSV: `$REPO/data/csv_new_tasks/dataset_invasion_linfovascular_label.csv`

### 2.c Referencia: microcalcificaciones — 3 tareas BINARIAS (ya corridas)

| Tarea | `si` | `no` | n_test/fold (pos) | fuente |
|---|---|---|---|---|
| `microcalcificaciones_en_carcinoma_invasivo_pth` | 121 | 212 | 32 (7) | priv+TCGA+HistAI |
| `microcalcificaciones_en_cdis_pth` | 68 | 265 | 36 (11-14) | idem |
| `microcalcificaciones_en_tejido_no_neoplasico_pth` | 195 | 138 | 33 (19-21) | idem |

---

## 3. Splits (verdad de campo — referencias exactas)

**Esquema:** Monte-Carlo CV **k=5** estratificado, `patient_strat`, `val_frac=test_frac=0.1`,
`seed=1`. Generados con `scripts/build_new_tasks_splits.py` (reusa
`Generic_WSI_Classification_Dataset` de CLAM sin forkear). Verificados con
`scripts/verify_kfold_splits.py` (disjuntos, total constante, `.pt` presente) → **rc=0**.

Archivos por tarea (5 folds: `splits_0.csv` … `splits_4.csv`, + `_bool` y `_descriptor`):

```
$REPO/data/splits_kfold/
├── cdis_patron_cribiforme_pth_100/        splits_{0..4}.csv
├── cdis_patron_solido_pth_100/            splits_{0..4}.csv
├── cdis_patron_micropapilar_pth_100/      splits_{0..4}.csv
├── cdis_patron_papilar_pth_100/           splits_{0..4}.csv
└── invasion_linfatica_vascular_pth_100/   splits_{0..4}.csv
```

Columnas de `splits_<f>.csv`: `,train,val,test` (un `slide_id` por celda). Ambos brazos
(CLAM y CLAM+Mammoth) leen **el mismo** `splits_<f>.csv` → Δ pareado por fold.

> Splits de microcalc (referencia): `$REPO/data/splits_kfold/microcalcificaciones_en_<tejido>_pth_100/`.

---

## 4. Resultados

Política de evaluación (B5): se reporta **balanced_acc Y AUC juntos** (test) + matriz de
confusión + n por clase. Métrica decisiva = **Δ pareado por fold** (`mammoth − clam`),
media ± std. Sin gate numérico; interpretación cualitativa (consistencia de signo,
varianza, vs trivial). Binarias = ROC-AUC; invasión = macro one-vs-rest.

### 4.0 Resumen AUC por tarea — media y mejor de los 5 folds (pedido reunión 8-jun)

`test_auc` extraído de `summary.csv` (`folds,test_auc,...`) de cada run, k=5 paired.
**media** = promedio de los 5 folds; **mejor** = máximo de los 5 folds. Binarias = ROC-AUC;
invasión = macro one-vs-rest. Ambos brazos (CLAM / CLAM+Mammoth) leen los mismos
`splits_<f>.csv` (`$REPO/data/splits_kfold/<dir>/`, 5 folds c/u).

| Tarea (`--task`) | Dataset (fuente · n) | Split dir (`$REPO/data/splits_kfold/`) | CLAM media | CLAM mejor | +Mammoth media | +Mammoth mejor |
|---|---|---|---|---|---|---|
| `microcalcificaciones_en_carcinoma_invasivo_pth` | _pth (priv+TCGA+HistAI) · 333 | `microcalcificaciones_en_carcinoma_invasivo_pth_100/` | 0.732 | 0.842 | 0.722 | 0.846 |
| `microcalcificaciones_en_cdis_pth` | _pth · 333 | `microcalcificaciones_en_cdis_pth_100/` | 0.652 | 0.740 | 0.618 | 0.737 |
| `microcalcificaciones_en_tejido_no_neoplasico_pth` | _pth · 333 | `microcalcificaciones_en_tejido_no_neoplasico_pth_100/` | 0.646 | 0.688 | 0.678 | 0.830 |
| `cdis_patron_cribiforme_pth` | _pth (HistAI200+TCGA238+Priv75) · 513 | `cdis_patron_cribiforme_pth_100/` | 0.710 | 0.786 | 0.732 | 0.800 |
| `cdis_patron_solido_pth` | _pth · 513 | `cdis_patron_solido_pth_100/` | 0.700 | 0.763 | 0.679 | 0.776 |
| `cdis_patron_micropapilar_pth` | _pth · 513 | `cdis_patron_micropapilar_pth_100/` | 0.727 | 0.903 | 0.722 | 0.931 |
| `cdis_patron_papilar_pth` | _pth · 513 | `cdis_patron_papilar_pth_100/` | 0.616 | 0.722 | 0.570 | 0.722 |
| `invasion_linfatica_vascular_pth` (macro-OVR) | _pth (HistAI1418+TCGA864+Priv532) · 2814 | `invasion_linfatica_vascular_pth_100/` | 0.828 | 0.867 | 0.818 | 0.848 |

> La media/mejor AUC es **resumen descriptivo**; el **veredicto** del hilo usa el Δ pareado
> por fold + balanced_acc (§4.a–4.c). Mammoth NO es palanca en ninguna (lean+ leve solo en
> `tejido` y `cribiforme`, las 2 más balanceadas; regresión leve consistente en invasión).

### 4.a Microcalcificaciones (COMPLETO — 2-jun)

**Veredicto: Mammoth NO es palanca** (señal dominada por varianza en las 3). Detalle:
`$REPO/sprints/B5_sprint5/objetivo_1_mammoth_run/resultados.md`.

| Binaria | CLAM bal_acc | +Mammoth bal_acc | Δ pareado bal_acc | Δ pareado AUC | signo |
|---|---|---|---|---|---|
| carcinoma | 0.639 ± 0.077 | 0.585 ± 0.080 | −0.054 ± 0.125 | −0.010 ± 0.065 | 2+/3− (nulo) |
| cdis | 0.595 ± 0.077 | 0.509 ± 0.117 | −0.086 ± 0.113 | −0.035 ± 0.104 | 1+/4− (leve regresión) |
| tejido | 0.577 ± 0.030 | 0.626 ± 0.096 | +0.049 ± 0.077 | +0.032 ± 0.084 | 4+/1− (leve mejora) |

### 4.b Patrón arquitectónico (COMPLETO — 4-jun, job 4243, 40 runs)

**Veredicto: Mammoth NO es palanca** (igual que microcalc). Lean positivo leve solo en
**cribiforme** (la única binaria balanceada); nulo en el resto. Detalle:
`$REPO/sprints/B5_sprint5/objetivo_2_mammoth_patron_invasion/resultados.md`.

**Régimen sano** (cribiforme/solido — fold a fold, k=5, std poblacional):

| Binaria | CLAM bal_acc | +Mammoth bal_acc | Δ pareado bal_acc | Δ pareado AUC | signo |
|---|---|---|---|---|---|
| cribiforme | 0.650 ± 0.057 | 0.694 ± 0.078 | +0.044 ± 0.048 | +0.022 ± 0.042 | 4+/1− (leve mejora) |
| solido | 0.647 ± 0.065 | 0.632 ± 0.067 | −0.014 ± 0.064 | −0.022 ± 0.055 | 3+/2− (nulo) |

**Régimen ciego** (micropapilar/papilar — 3 pos/test → **pooled** los 15 positivos de los
5 folds; sens/spec/AUC global, NO fold a fold):

| Binaria | brazo | pooled n (pos) | sens | spec | bal_acc (pool) | AUC (pool) |
|---|---|---|---|---|---|---|
| micropapilar | CLAM | 257 (15) | 0.267 | 0.967 | 0.617 | 0.707 |
| micropapilar | +Mammoth | 257 (15) | 0.200 | 0.921 | 0.561 | 0.710 |
| papilar | CLAM | 256 (15) | 0.133 | 0.929 | 0.531 | 0.583 |
| papilar | +Mammoth | 256 (15) | 0.067 | 0.946 | 0.506 | 0.599 |

> Ambos brazos casi no detectan el patrón (TP global 4/15 y 2/15; mammoth 3/15 y 1/15) →
> tareas hambrientas de positivos (32–34 en toda la cohorte). MC-CV: los folds solapan,
> el pool es descriptivo. El re-run 4243 cerró los 40 runs sin el crash del 4241
> (corrió desde `main`, sin branch-switch — workaround H).

**Hallazgo crítico (cruce Obj1+Obj2 = 7 binarias):** el lean positivo de mammoth aparece
**solo en las 2 tareas más balanceadas** (microcalc·tejido ~58% +0.049; patrón·cribiforme
~49% +0.044) y se apaga en cuanto domina el desbalance o faltan positivos. El predictor del
resultado es el **régimen de datos**, no el agregador/patch-embed → el cuello es **datos /
desbalance / contexto espacial**, no la arquitectura. Apunta el esfuerzo a datos
(magnificación, parches útiles, más positivos), no a más swaps de modelo.

### 4.c Invasión linfática 3-clase (COMPLETO — job 4246, 10 runs, cerró 5-jun 06:18)

> **Veredicto: mammoth NO es palanca** (cierra el hilo). El n más grande del hilo (2814) y
> el eval más sano (cada clase n≥36/test → fold-a-fold, no pooled) **no rescatan** a mammoth.

| brazo | bal_acc (media±std) | macro-OVR AUC | trivial |
|---|---|---|---|
| CLAM (baseline) | 0.622 ± 0.028 | 0.828 ± 0.021 | 0.333 |
| CLAM + Mammoth | 0.575 ± 0.057 | 0.818 ± 0.019 | 0.333 |
| **Δ pareado (mam − clam)** | **−0.047 ± 0.064** (1+/4−) | **−0.011 ± 0.005** (0+/5−) | — |

> Δ bal_acc en **banda ambigua** por magnitud (std > |media|) pero con **lean negativo**
> 4/5; Δ AUC **regresión leve consistente** (5/5 folds−, no cruza 0). Mecanismo = **mayor
> colapso a la mayoritaria** `no_identificado`: recall 0.792→0.815, a costa de `presente`
> 0.577→0.434 (confusión 3×3 sumada). Encaja con el **efecto gated por balance** (§4.b):
> invasión es fuertemente desbalanceada (70% mayoritaria) → mammoth inclina a la mayoritaria.
> Detalle + figuras: `$REPO/sprints/B5_sprint5/objetivo_2_mammoth_patron_invasion/resultados_invasion.md`
> (análisis `$REPO/scripts/analyze_invasion.py`). _Política eval B5: balanced_acc + macro-OVR
> AUC + confusión 3×3 + n, sin gate._

---

## 5. Reproducir / trazabilidad

```bash
REPO=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto
# (1) splits:   $PY $REPO/scripts/build_new_tasks_splits.py   ($PY = binario absoluto env clam_latest)
# (2) verificar:$PY $REPO/scripts/verify_kfold_splits.py
# (3) entrenar (GPU, vía SLURM; NO cambiar de rama mientras corre — workaround H):
GROUP=patron   sbatch $REPO/scripts/run_obj2_mammoth_patron_invasion_kfold.slurm   # 4 binarias
GROUP=invasion sbatch $REPO/scripts/run_obj2_mammoth_patron_invasion_kfold.slurm   # 3-clase
```

- Hipótesis pre-registrada + diseño: `$REPO/sprints/B5_sprint5/objetivo_2_mammoth_patron_invasion/README.md`.
- Salidas por run: `$REPO/results/obj2_mammoth/<task>/<modelo>_<task>_f<0..4>_*_s1/`
  (`test_metrics.json`: balanced_acc + AUC + confusión + n; `test_predictions.csv`: `y_prob_<c>`).
- Port de Mammoth: `$REPO/models_mammoth/clam_mammoth.py` (clase `CLAM_MB_Mammoth`,
  subclase de `CLAM_MB`, único delta = la 1ª capa lineal → `MammothPatchEmbed`). Paquete
  `mammoth` vendorizado en `clam_testing2/MAMMOTH` (pin `fe36d4e`).
