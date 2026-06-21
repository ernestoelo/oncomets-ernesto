# Experimentos Mammoth en CLAM — OncoMets / Environ

Autor: Ernesto Gamero, Sprint B5. CLAM (baseline) vs CLAM+Mammoth, k=5 pareado: los dos brazos
leen los mismos splits y lo único que cambia es la 1ª capa lineal de CLAM, que pasa a ser una
mezcla de expertos (mismo harness `train_dsmil.py`). Detalle por tarea (n por clase, matrices de
confusión, Δ pareado) en `sprints/B5_sprint5/objetivo_1_mammoth_run/resultados.md` y
`sprints/B5_sprint5/objetivo_2_mammoth_patron_invasion/`.

## Tareas

- Microcalcificaciones (binarias): en carcinoma invasivo, en CDIS, en tejido no neoplásico.
- Patrón arquitectónico de CDIS (binarias): cribiforme, sólido, micropapilar, papilar.
- Invasión linfática vascular (3 clases).

## Dataset

Cohorte `_pth` = Privado (Environ) + TCGA + HistAI. En las binarias se excluye `no_identificado`.

- microcalc carcinoma: si 68 / no 260 (n 328)
- microcalc cdis: si 118 / no 210 (n 328)
- microcalc tejido: si 192 / no 136 (n 328)
- cribiforme: si 252 / no 261 (n 513)
- sólido: si 388 / no 125 (n 513)
- micropapilar: si 34 / no 479 (n 513)
- papilar: si 32 / no 481 (n 513)
- invasión: no_identificado 1967 / ausente 479 / presente 368 (n 2814)

## Splits

`data/splits_kfold/<task>_100/splits_{0..4}.csv` — Monte-Carlo k=5 estratificado (`patient_strat`,
val=test=10%, seed 1). Los dos brazos leen el mismo `splits_<f>.csv`, de ahí el Δ pareado por fold.

## Comando

```
train_dsmil.py --model_type clam | clam_mammoth --B 8 --bag_weight 0.7 --lr 2e-4 --reg 1e-5 \
  --drop_out 0.25 --embed_dim 512 --max_epochs 30 --early_stopping --weighted_sample --seed 1
```

Mammoth (solo brazo `clam_mammoth`): num_experts 30, num_slots 10, num_heads 16, slot_dim 256,
dropout 0.1, keep_slots False, auto_rank True. Lanzamiento:
`sbatch scripts/run_obj2_mammoth_patron_invasion_kfold.slurm` (`GROUP=patron|invasion`).

## Resultados (5 folds)

AUC como media / mejor de los 5 folds; balanced_acc como media ± std. Binarias ROC-AUC, invasión
macro one-vs-rest.

| Tarea | CLAM AUC | +Mam AUC | CLAM bal | +Mam bal |
|---|---|---|---|---|
| microcalc carcinoma | 0.732 / 0.842 | 0.722 / 0.846 | 0.639 ± 0.077 | 0.585 ± 0.080 |
| microcalc cdis | 0.652 / 0.740 | 0.618 / 0.737 | 0.595 ± 0.077 | 0.509 ± 0.117 |
| microcalc tejido | 0.646 / 0.688 | 0.678 / 0.830 | 0.577 ± 0.030 | 0.626 ± 0.096 |
| cribiforme | 0.710 / 0.786 | 0.732 / 0.800 | 0.650 ± 0.057 | 0.694 ± 0.078 |
| sólido | 0.700 / 0.763 | 0.679 / 0.776 | 0.647 ± 0.065 | 0.632 ± 0.067 |
| micropapilar | 0.727 / 0.903 | 0.722 / 0.931 | 0.617 (pool) | 0.561 (pool) |
| papilar | 0.616 / 0.722 | 0.570 / 0.722 | 0.531 (pool) | 0.506 (pool) |
| invasión | 0.828 / 0.867 | 0.818 / 0.848 | 0.622 ± 0.028 | 0.575 ± 0.057 |

micropapilar y papilar tienen 3 positivos por test, así que el balanced va pooled (los 15
positivos de los 5 folds juntos, no fold a fold).

Resumen: Mammoth no supera a CLAM de forma consistente. Hay una mejora leve solo en tejido y
cribiforme, las dos tareas más balanceadas.

## Variante keep_slots=True (Obj 3)

Mismo harness y splits, pero Mammoth con `keep_slots=True` (la 1ª capa devuelve E·S=300
slot-tokens en vez de los N parches — cuello de botella aprendido) sobre 4 tareas. Detalle por
fold, confusión y Δ pareado en `sprints/B5_sprint5/objetivo_3_mammoth_keepslots/resultados.md`.

| Tarea | CLAM AUC | +Mam(kst) AUC | CLAM bal | +Mam(kst) bal |
|---|---|---|---|---|
| microcalc carcinoma | 0.732 / 0.842 | 0.738 / 0.803 | 0.639 ± 0.077 | 0.620 ± 0.083 |
| microcalc cdis | 0.652 / 0.740 | 0.652 / 0.740 | 0.595 ± 0.077 | 0.572 ± 0.075 |
| microcalc tejido | 0.646 / 0.688 | 0.647 / 0.763 | 0.577 ± 0.030 | 0.623 ± 0.117 |
| invasión | 0.828 / 0.867 | 0.825 / 0.839 | 0.622 ± 0.028 | 0.591 ± 0.040 |

Resumen: `keep_slots=True` tampoco supera a CLAM (0/4 tareas). Mitiga el colapso a la clase
mayoritaria que tenía la versión drop-in (recupera recall de la minoritaria), pero no alcanza al
baseline. La variante con `slot_dropout` queda descartada (net-negativa). Con esto el hilo
Mammoth queda cerrado: 8 tareas drop-in + 4 keep_slots, sin palanca.



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
