# Experimentos PathPT-CONCH en CLAM — OncoMets / Environ

Autor: Ernesto Gamero. Sprint B5 (cierre de trimestre, junio 2026).

Esta es la fuente canónica y versionada del resumen del hilo PathPT: vive en el repo,
sobrevive a una pérdida del workspace y se puede citar desde GitHub. Si hay una copia en
`clam_testing/`, es derivada; editar siempre acá. El detalle largo por tarea está en
`sprints/B5_sprint5/pathpt/resultados_{necrosis,mitotic}.md`.

Qué es PathPT (en el alcance que probé, el completo): CONCH queda congelado y solo se
entrena un módulo espacial y los prompts de texto (CoOp), con supervisión a nivel de parche.
Lo importante para nosotros es que reusa las features de visión de CONCH que ya teníamos
generadas, no las vuelve a calcular; lo único que enciende es el encoder de texto de CONCH
para los prompts.

La comparación central es PathPT (`train_pathpt.py`) contra CLAM como baseline
(`train_dsmil.py --model_type clam`), con validación cruzada k=5 pareada: los dos brazos leen
los mismos splits, así que puedo mirar la diferencia fold a fold sin que el sorteo confunda.


## 1. Config de entrenamiento

CLAM (baseline) corre con los args bendecidos de Environ:

| Arg | Valor | | Arg | Valor |
|---|---|---|---|---|
| `--model_type` | `clam` | | `--max_epochs` | 30 |
| `--B` | 8 | | `--early_stopping` | sí |
| `--bag_weight` | 0.7 | | `--seed` | 1 |
| `--lr` | 2e-4 | | `--drop_out` | 0.25 |
| `--reg` | 1e-5 | | `--embed_dim` (CONCH) | 512 |

PathPT (`train_pathpt.py`, alcance completo) entrena el módulo espacial, los prompts (CoOp) y
la supervisión por parche durante 20 épocas con lr 1e-4. Los prompts los redacté a partir del
protocolo CAP (`Breast.Invasive.Bx_1.2.0.0`): la Nota C para necrosis y el sistema Nottingham
para la tasa mitótica. El umbral de decisión de PathPT lo elijo en validación y lo congelo
para test, así no hago trampa eligiéndolo después. Features CONCH de 512 dimensiones, las
mismas .pt que ya estaban.

Para la evaluación reporto balanced_acc y AUC juntos (más matriz de confusión y n por clase),
y la decisión la tomo con el Δ pareado por fold (PathPT menos CLAM), mirando consistencia de
signo y varianza, sin un umbral mágico de éxito/fracaso.


## 2. Tareas, clases y dataset

La cohorte _pth es Privado (Environ) + TCGA + HistAI. Se sacan las slides cuyo reporte CAP no
menciona el ítem (`no_identificado`), así que el universo queda en lo identificado.

| Tarea (`--task`) | tipo | clases (n por clase) | n total |
|---|---|---|---|
| `cdis_necrosis_2clases_pth` | binaria | `no`=83 / `si`=313 | 396 |
| `grado_mitotic_3clases_pth` | 3 clases ordinales (Nottingham) | `score_1`=636 / `score_2`=287 / `score_3`=254 | 1177 |

Los CSV de labels y los splits están en `data/splits_kfold/<task>_100/splits_{0..4}.csv`.


## 3. Splits

Validación Monte-Carlo k=5 estratificada, con `patient_strat`, val y test al 10% cada uno y
seed 1. Los dos brazos (CLAM y PathPT) leen el mismo `splits_<f>.csv`, de ahí que la diferencia
sea pareada fold a fold.

```
data/splits_kfold/
├── cdis_necrosis_2clases_pth_100/    splits_{0..4}.csv
└── grado_mitotic_3clases_pth_100/    splits_{0..4}.csv
```


## 4. Resultados

### 4.0 Resumen de AUC por tarea

El AUC sale del `test_metrics.json` de cada run. La media es el promedio de los 5 folds y
"mejor" el máximo. Necrosis usa ROC-AUC y la mitótica macro one-vs-rest.

| Tarea (`--task`) | Dataset (n) | Split dir | CLAM media | CLAM mejor | PathPT media | PathPT mejor |
|---|---|---|---|---|---|---|
| `cdis_necrosis_2clases_pth` | _pth · 396 (313 si/83 no) | `cdis_necrosis_2clases_pth_100/` | 0.727 | 0.798 | 0.661 | 0.798 |
| `grado_mitotic_3clases_pth` (macro-OVR) | _pth · 1177 (636/287/254) | `grado_mitotic_3clases_pth_100/` | 0.724 | 0.765 | 0.662 | 0.714 |

Esta tabla es descriptiva; el veredicto sale del Δ pareado y el balanced_acc de abajo. PathPT
no aporta en ninguna de las dos. Detalle en `sprints/B5_sprint5/pathpt/`.

### 4.a Necrosis binaria (job 4309, 11-jun)

CLAM saca 0.633 de balanced_acc y PathPT 0.613.

| brazo | bal_acc (media) | AUC (media) |
|---|---|---|
| CLAM (baseline) | 0.633 | 0.727 |
| PathPT | 0.613 | 0.661 |
| Δ pareado (pathpt − clam) | −0.020 ± 0.078 (2+/3−, cruza 0) | −0.066 ± 0.094 (lean negativo) |

El Δ cruza cero con una varianza más grande que la media, así que es ambiguo y se lee como
nulo. El modelo entrenado se queda casi pegado al CONCH zero-shot (~0.62), mientras que CLAM
sí le gana. En la confusión sumada PathPT solo redistribuye el trade-off: detecta un poco
mejor la clase chica a costa de la mayoritaria, y no rompe nada.

### 4.b Tasa mitótica de 3 grados (job 4326, 11-jun)

Acá PathPT colapsa: predice siempre el grado más bajo (`score_1`) y no emite una sola
predicción de `score_2` ni `score_3` en las 588 slides de test, así que su balanced_acc cae
al 0.333 trivial. CLAM, con los mismos datos, sí usa los tres grados.

| brazo | bal_acc (media) | macro-OVR AUC | confusión sumada (s1/s2/s3) |
|---|---|---|---|
| CLAM (baseline) | 0.494 | 0.724 | `[[231,53,36],[77,27,38],[26,28,72]]` |
| PathPT | 0.333 (trivial exacto) | 0.662 | `[[320,0,0],[142,0,0],[126,0,0]]` |
| Δ pareado (pathpt − clam) | −0.160 ± 0.049 (5/5−) | −0.062 ± 0.062 (amb) | — |

El AUC macro mide el ranking y no la decisión final, y ahí no colapsa (0.662): la señal
existe, pero el punto de operación (el argmax) es inservible bajo este desbalance. La causa
está en cómo definí la tarea. Tomé el grado más bajo (`score_1`) como clase base, y como PathPT
etiqueta parche por parche, la mayoría de los parches caen en ese grado incluso en slides de
grado alto (las mitosis son eventos raros y localizados), así que el modelo termina contestando
siempre el grado bajo. No es un bug: el eval está validado (test CPU 9/9) y CLAM con los mismos
splits no colapsa, porque clasifica a nivel slide y corrige el desbalance con `weighted_sample`.
Esa decisión de formulación es justo la que dejé con sign-off pendiente de Sebastián, así que
antes de re-correrla hay que revisarla con él.

### 4.c Microcalcificaciones: prueba previa sin entrenar

Antes de gastar GPU hice una prueba rápida en CPU para decidir si valía la pena entrenar:
clasificar cada slide solo por la similitud entre CONCH y el texto de los prompts, sin entrenar
nada. Tomé el mejor AUC sobre los parches más parecidos (top-100).

| Binaria (`microcalcificaciones_en_..._pth`) | n (no/si) | AUC sin entrenar (mejor) |
|---|---|---|
| `..._carcinoma_invasivo_pth` | 260 / 68 | 0.629 |
| `..._cdis_pth` | 210 / 118 | 0.533 |
| `..._tejido_no_neoplasico_pth` | 136 / 192 | 0.444 |

Quedaron cerca del azar (0.5). CONCH no reconoce las microcalcificaciones desde el texto, y
cuando le metí más morfología a los prompts de carcinoma la cosa empeoró (las versiones v2 y
v3 bajaron a 0.533 y 0.552). Por eso no lo llevé a entrenamiento, que nos habría costado del
orden de 18 a 24 horas de GPU. Los JSON están en `results/pathpt_gonogo/`.


## 5. Lectura del hilo

PathPT no movió la aguja. Es el tercer enfoque que probamos junto con Mammoth (que cambia el
patch-embed) y DSMIL (que cambia el agregador), y los tres apuntan a lo mismo: el límite está
en los datos, el desbalance y CONCH, no en el modelo que le pongamos encima. La prueba previa
barata para microcalc valió la pena, porque lo descartó sin gastar GPU.

## 6. Reproducir

- Hipótesis pre-registrada (regla 9, reviewer aprobado): `sprints/B5_sprint5/pathpt/etapa1_prereg_{necrosis,mitotic}.md`.
- Resultados largos: `sprints/B5_sprint5/pathpt/resultados_{necrosis,mitotic}.md`.
- Prompts CAP: `sprints/B5_sprint5/pathpt/prompts_cap.md`.
- Port de PathPT: `models_pathpt/` (pin `0ab7f1b`); driver `train_pathpt.py`; test CPU
  `tests/test_pathpt_cpu.py`.
- Salidas por run: `results/pathpt_etapa1/<tarea>/<modelo>_<task>_f<0..4>_*_s1/`
  (`test_metrics.json` con balanced_acc, AUC, confusión y n).
