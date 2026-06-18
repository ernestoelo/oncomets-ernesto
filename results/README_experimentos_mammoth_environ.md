# Experimentos Mammoth en CLAM — OncoMets / Environ

Autor: Ernesto Gamero. Sprint B5 (cierre de trimestre, junio 2026).

Esta es la fuente canónica y versionada de este doc: vive en el repo, sobrevive a una pérdida
del workspace y se puede citar desde GitHub. Si hay una copia en `clam_testing/`, es derivada;
editar siempre acá. Por cada tarea anoto la config de entrenamiento, el dataset de origen con
el n por clase, el split usado (con rutas) y los resultados.

La comparación central es CLAM como baseline contra CLAM+Mammoth, con validación cruzada k=5
pareada: los dos brazos leen los mismos splits, y lo único que cambia entre ellos es la primera
capa lineal, que pasa a ser una mezcla de expertos (MoE). Uso el mismo harness para los dos
(`train_dsmil.py` con `--model_type clam | clam_mammoth`), así que la comparación es limpia, sin
que el bucle de entrenamiento confunda.

Todo el código, los datos y los resultados viven en `clam_testing2/oncomets-ernesto/`. Las
rutas de abajo son relativas al repo o usan `$REPO`.

---

## 1. Config de entrenamiento (igual en todas las tareas y los dos brazos)

Args bendecidos, los mismos del baseline oficial de Environ y del run de microcalc:

| Arg | Valor | | Arg | Valor |
|---|---|---|---|---|
| `--model_type` | `clam` / `clam_mammoth` | | `--max_epochs` | 30 |
| `--B` (k_sample inst-loss) | 8 | | `--early_stopping` | sí |
| `--bag_weight` | 0.7 | | `--patience` | 20 |
| `--lr` | 2e-4 | | `--stop_epoch` | 50 |
| `--reg` | 1e-5 | | `--seed` | 1 |
| `--drop_out` | 0.25 | | `--embed_dim` (CONCH) | 512 |

Hiperparámetros de Mammoth (solo en el brazo `clam_mammoth`). Son los defaults que recomienda
el paper; `auto_rank` mantiene la cantidad de parámetros parecida a la de la capa lineal
original:

| `num_experts` | `num_slots` | `num_heads` | `slot_dim` | `dropout` | `keep_slots` | `share_lora_weights` | `auto_rank` |
|---|---|---|---|---|---|---|---|
| 30 | 10 | 16 | 256 | 0.1 | **False** | True | True |

Con `keep_slots=False`, Mammoth devuelve los N parches transformados, o sea la misma semántica
de atención e instance-loss que el baseline, lo que deja la comparación limpia. Features CONCH
de 512 dimensiones en todas las slides, instance-loss `SmoothTop1SVM` y sampler de train
`weighted` para corregir el desbalance de clases.

---

## 2. Tareas, clases, n por clase y dataset de origen

La cohorte _pth es Privado (Environ) + TCGA + HistAI. En las binarias de patrón se sacan las
slides cuyo reporte CAP no menciona el patrón (`no_identificado`), así que el universo queda en
el DCIS identificado.

### 2.a Patrón arquitectónico de CDIS: 4 tareas binarias (si/no)

Las clases son los patrones del protocolo CAP (`papers/Breast.Invasive.Bx_1.2.0.0.REL_CAPCP.pdf`,
sección de patrones arquitectónicos de DCIS). Como en el CAP es "marque todos los que apliquen",
queda multi-label y lo abro en una binaria por patrón. El n por tarea es 513, el mismo universo
en las cuatro (cada slide es si/no para cada patrón). Fuente: HistAI 200 + TCGA 238 + Privado 75.

| Tarea (`--task`) | clase `si` | clase `no` | desbalance | régimen |
|---|---|---|---|---|
| `cdis_patron_cribiforme_pth` | 252 | 261 | ~1:1 | sano |
| `cdis_patron_solido_pth` | 388 | 125 | ~3:1 | ok |
| `cdis_patron_micropapilar_pth` | 34 | 479 | 14:1 | **3 pos/test fold — "estadísticamente ciego"** |
| `cdis_patron_papilar_pth` | 32 | 481 | 15:1 | **3 pos/test fold — idem** |

CSV de labels (snapshot filtrado a slides con `.pt`):
`$REPO/data/csv_new_tasks/dataset_carcinoma_ductal_in_situ_patrones_arquitectonicos_<patrón>_label.csv`

### 2.b Invasión linfática (linfovascular): 1 tarea de 3 clases

Las clases son las del CAP para invasión linfovascular (no identificada, presente, no se puede
determinar). El n total es 2814; hay una slide de HistAI (`histai_1132_slide_H&E_0`) sin `.pt`
que se cae del crudo de 2815. Fuente: HistAI 1418 + TCGA 864 + Privado 532.

| Tarea (`--task`) | `no_identificado` | `ausente` | `presente` | trivial bal_acc |
|---|---|---|---|---|
| `invasion_linfatica_vascular_pth` | 1967 (70%) | 479 | 368 | 0.333 |

`label_dict = {"ausente":0, "no_identificado":1, "presente":2}` (`--n_classes 3`).
CSV: `$REPO/data/csv_new_tasks/dataset_invasion_linfovascular_label.csv`

### 2.c Microcalcificaciones: 3 binarias, como referencia (ya corridas)

| Tarea | `si` | `no` | n_test/fold (pos) | fuente |
|---|---|---|---|---|
| `microcalcificaciones_en_carcinoma_invasivo_pth` | 121 | 212 | 32 (7) | priv+TCGA+HistAI |
| `microcalcificaciones_en_cdis_pth` | 68 | 265 | 36 (11-14) | idem |
| `microcalcificaciones_en_tejido_no_neoplasico_pth` | 195 | 138 | 33 (19-21) | idem |

---

## 3. Splits (verdad de campo)

El esquema es Monte-Carlo k=5 estratificada, con `patient_strat`, val y test al 10% y seed 1.
Los genera `scripts/build_new_tasks_splits.py` (que reusa `Generic_WSI_Classification_Dataset`
de CLAM sin forkearlo) y los verifica `scripts/verify_kfold_splits.py`, que chequea que sean
disjuntos, que el total se mantenga y que el `.pt` esté presente (terminó con rc=0).

Archivos por tarea (5 folds: `splits_0.csv` … `splits_4.csv`, más `_bool` y `_descriptor`):

```
$REPO/data/splits_kfold/
├── cdis_patron_cribiforme_pth_100/        splits_{0..4}.csv
├── cdis_patron_solido_pth_100/            splits_{0..4}.csv
├── cdis_patron_micropapilar_pth_100/      splits_{0..4}.csv
├── cdis_patron_papilar_pth_100/           splits_{0..4}.csv
└── invasion_linfatica_vascular_pth_100/   splits_{0..4}.csv
```

Las columnas de `splits_<f>.csv` son `,train,val,test`, con un `slide_id` por celda. Los dos
brazos leen el mismo `splits_<f>.csv`, de ahí el Δ pareado por fold. Los splits de microcalc,
como referencia, están en `$REPO/data/splits_kfold/microcalcificaciones_en_<tejido>_pth_100/`.

---

## 4. Resultados

Para evaluar (política B5) reporto balanced_acc y AUC juntos en test, más la matriz de confusión
y el n por clase. La métrica con la que decido es el Δ pareado por fold (mammoth menos clam, en
media ± std). No uso un umbral numérico de éxito o fracaso: leo la consistencia de signo, la
varianza y la comparación contra el trivial. Las binarias usan ROC-AUC y la invasión macro
one-vs-rest.

### 4.0 Resumen de AUC por tarea (media y mejor de los 5 folds, pedido en la reunión del 8-jun)

El AUC sale del `summary.csv` de cada run. La media es el promedio de los 5 folds y "mejor" el
máximo. Los dos brazos leen los mismos `splits_<f>.csv` (en `$REPO/data/splits_kfold/<dir>/`,
5 folds cada uno).

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

La media y el mejor AUC son descriptivos; el veredicto del hilo sale del Δ pareado por fold y
el balanced_acc (secciones 4.a a 4.c). Mammoth no es palanca en ninguna tarea: hay una mejora
leve solo en tejido y cribiforme, las dos más balanceadas, y una regresión leve pero
consistente en invasión.

### 4.a Microcalcificaciones (cerrado el 2-jun)

Mammoth no es palanca: en las tres la señal queda dominada por la varianza. Detalle en
`$REPO/sprints/B5_sprint5/objetivo_1_mammoth_run/resultados.md`.

| Binaria | CLAM bal_acc | +Mammoth bal_acc | Δ pareado bal_acc | Δ pareado AUC | signo |
|---|---|---|---|---|---|
| carcinoma | 0.639 ± 0.077 | 0.585 ± 0.080 | −0.054 ± 0.125 | −0.010 ± 0.065 | 2+/3− (nulo) |
| cdis | 0.595 ± 0.077 | 0.509 ± 0.117 | −0.086 ± 0.113 | −0.035 ± 0.104 | 1+/4− (leve regresión) |
| tejido | 0.577 ± 0.030 | 0.626 ± 0.096 | +0.049 ± 0.077 | +0.032 ± 0.084 | 4+/1− (leve mejora) |

### 4.b Patrón arquitectónico (cerrado el 4-jun, job 4243, 40 runs)

Mismo resultado que microcalc: Mammoth no es palanca. Hay una mejora leve solo en cribiforme,
que es la única binaria balanceada, y nada en el resto. Detalle en
`$REPO/sprints/B5_sprint5/objetivo_2_mammoth_patron_invasion/resultados.md`.

Régimen sano (cribiforme y solido, leído fold a fold con k=5 y std poblacional):

| Binaria | CLAM bal_acc | +Mammoth bal_acc | Δ pareado bal_acc | Δ pareado AUC | signo |
|---|---|---|---|---|---|
| cribiforme | 0.650 ± 0.057 | 0.694 ± 0.078 | +0.044 ± 0.048 | +0.022 ± 0.042 | 4+/1− (leve mejora) |
| solido | 0.647 ± 0.065 | 0.632 ± 0.067 | −0.014 ± 0.064 | −0.022 ± 0.055 | 3+/2− (nulo) |

Régimen ciego (micropapilar y papilar, con 3 positivos por test). Acá junto los 15 positivos de
los 5 folds y miro sens, spec y AUC globales, no fold a fold:

| Binaria | brazo | pooled n (pos) | sens | spec | bal_acc (pool) | AUC (pool) |
|---|---|---|---|---|---|---|
| micropapilar | CLAM | 257 (15) | 0.267 | 0.967 | 0.617 | 0.707 |
| micropapilar | +Mammoth | 257 (15) | 0.200 | 0.921 | 0.561 | 0.710 |
| papilar | CLAM | 256 (15) | 0.133 | 0.929 | 0.531 | 0.583 |
| papilar | +Mammoth | 256 (15) | 0.067 | 0.946 | 0.506 | 0.599 |

Los dos brazos casi no detectan el patrón (los TP globales son 4/15 y 2/15 en CLAM, y 3/15 y
1/15 en mammoth): son tareas con muy pocos positivos, apenas 32 a 34 en toda la cohorte. Como
los folds de Monte-Carlo se solapan, el pool es solo descriptivo. El re-run 4243 cerró los 40
runs sin el crash del 4241, porque corrió desde `main` y sin cambiar de rama (workaround H).

Cruzando Obj1 y Obj2 quedan 7 binarias, y el hallazgo principal es este: la mejora leve de
mammoth aparece solo en las dos tareas más balanceadas (tejido al 58% con +0.049, y cribiforme
al 49% con +0.044), y se apaga apenas manda el desbalance o faltan positivos. Lo que predice el
resultado es el régimen de datos, no el agregador ni el patch-embed. El cuello son los datos, el
desbalance y el contexto espacial, no la arquitectura, así que conviene apuntar el esfuerzo a
los datos (magnificación, parches útiles, más positivos) y no a seguir cambiando de modelo.

### 4.c Invasión linfática de 3 clases (job 4246, 10 runs, cerró el 5-jun a las 06:18)

Esto cierra el hilo, y mammoth tampoco es palanca. Es el n más grande del hilo (2814) y la
evaluación más sana (cada clase tiene al menos 36 por test, así que se lee fold a fold y no
pooled), y aun así no lo rescata.

| brazo | bal_acc (media±std) | macro-OVR AUC | trivial |
|---|---|---|---|
| CLAM (baseline) | 0.622 ± 0.028 | 0.828 ± 0.021 | 0.333 |
| CLAM + Mammoth | 0.575 ± 0.057 | 0.818 ± 0.019 | 0.333 |
| **Δ pareado (mam − clam)** | **−0.047 ± 0.064** (1+/4−) | **−0.011 ± 0.005** (0+/5−) | — |

El Δ de balanced_acc queda en banda ambigua por magnitud (la std es mayor que la media), pero
con lean negativo en 4 de 5 folds; el Δ de AUC es una regresión leve pero consistente (los 5
folds en negativo, sin cruzar cero). El mecanismo es que mammoth colapsa todavía más hacia la
clase mayoritaria, `no_identificado`: el recall sube de 0.792 a 0.815 a costa de `presente`, que
cae de 0.577 a 0.434 (en la confusión 3×3 sumada). Encaja con el efecto gobernado por el balance
de la sección 4.b: invasión está muy desbalanceada (70% en la mayoritaria), así que mammoth se
inclina hacia ella. Detalle y figuras en
`$REPO/sprints/B5_sprint5/objetivo_2_mammoth_patron_invasion/resultados_invasion.md` (análisis en
`$REPO/scripts/analyze_invasion.py`). La evaluación sigue la política B5: balanced_acc, macro-OVR
AUC, confusión 3×3 y n, sin umbral.

---

## 5. Reproducir

El bloque de abajo arma los splits, los verifica y lanza el entrenamiento por SLURM (`$PY` es el
binario absoluto del env `clam_latest`; ojo con no cambiar de rama mientras el job corre,
workaround H):

```bash
REPO=/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto
# (1) splits:   $PY $REPO/scripts/build_new_tasks_splits.py   ($PY = binario absoluto env clam_latest)
# (2) verificar:$PY $REPO/scripts/verify_kfold_splits.py
# (3) entrenar (GPU, vía SLURM; NO cambiar de rama mientras corre, workaround H):
GROUP=patron   sbatch $REPO/scripts/run_obj2_mammoth_patron_invasion_kfold.slurm   # 4 binarias
GROUP=invasion sbatch $REPO/scripts/run_obj2_mammoth_patron_invasion_kfold.slurm   # 3-clase
```

La hipótesis pre-registrada y el diseño están en
`$REPO/sprints/B5_sprint5/objetivo_2_mammoth_patron_invasion/README.md`. Las salidas de cada run
quedan en `$REPO/results/obj2_mammoth/<task>/<modelo>_<task>_f<0..4>_*_s1/`, con `test_metrics.json`
(balanced_acc, AUC, confusión y n) y `test_predictions.csv` (`y_prob_<c>`). El port de Mammoth
está en `$REPO/models_mammoth/clam_mammoth.py` (la clase `CLAM_MB_Mammoth`, subclase de `CLAM_MB`,
cuyo único cambio es la primera capa lineal, que pasa a ser `MammothPatchEmbed`); el paquete
`mammoth` está vendorizado en `clam_testing2/MAMMOTH` con el pin `fe36d4e`.



# Entrenamiento Seba dataset pth balanced + Mammoth 
Tareas:
tipo histologico
gh. aplica
gh grado general
cdi presente
necrosis
dif tubular
pleomorfismo nuclear
---
pendientes:
grado nuclear 
mitotic rate
necrosis 2 clases

## Dataset:
pth balance
tipo histologico:
carcinoma invasivo TNE: 1610
carcinoma lobulillar invasivo: 240
no id: 788
otros: 177

gh. aplica:
no: 797
no se puede determina: 122
si: 976

gh grado general
grado 1: 208
grado 2: 873
grado 3: 625
no identificado: 164


cdi presente
no: 636
no identificado 1369
si: 810

necrosis
ausente: 83
no identificado: 224
presente central: 224
presente focal: 28

dif tubular
no identificado: 376
score 1: 47
score 2: 196
score 3: 376

pleomorfismo nuclear
no identificado: 465
score 1: 62
score 2: 465
score 3: 465

## Resultados
tipo histologico
mejor: 0,91
5 fold: 0,88 ± 0,023

gh. aplica
mejor: 0,9
5 fold: 0,87 ± 0,024

gh grado general
mejor: 0,79
5 fold: 0,74 ± 0,046

cdi presente
mejor: 0,85
5 fold: 0,83 ± 0,015

necrosis
mejor: 0,74
5 fold: 0,65 ±  0,093

dif tubular
mejor: 0,87
5 fold: 0,82 ± 0,062

pleomorfismo nuclear
mejor: 0,78
5 fold: 0,77 ± 0,046
