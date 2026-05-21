# Objetivo 1 — Resultados del baseline CLAM (MicroCalcificaciones, B=8)

> Job `4098` **COMPLETED** el 21 may 2026. Números reales de
> `results/baseline_microcalc_pth_B8_minpatch16/`. No inventar nada acá:
> todo sale de `summary.csv`, `split_0_results.pkl` y el `.out`.

## Setup

| Campo | Valor |
|---|---|
| Tarea | `microcalcificaciones_pth` — CSV `environ/csv/dataset_microcalcificaciones_label.csv` |
| Clases | **8** (auto-label-dict, ver distribución abajo) |
| Split | `splits_local/microcalcificaciones_pth_100_minpatch16` (train 2436 / val 319 / test 315) |
| Features | CONCH 512-dim (`environ/features/pt_files/`) |
| Args | bendecidos + `--B 8` (ver `CLAUDE.md` → "Args bendecidos") |
| env | `clam_latest` (torch 2.8.0+cu128) |
| Job | `4098` — 11:06→15:18 (~4h 11m); early stopping época 51; **mejor checkpoint época 6** |
| N efectivo | train 2386 / val 295 / test 302 (resto sin `.pt`, el dataloader las salta) |

## El dataset: 8 clases, desbalance severo

CSV total 3072 slides. Las 8 clases NO son benigno/maligno — son la
**ubicación del tejido** donde aparece la microcalcificación:

| id | clase | total | % |
|---|---|---|---|
| 7 | `no_identificado` | 2739 | **89.2 %** |
| 6 | `en_tejido_no_neoplasico` | 161 | 5.2 % |
| 4 | `en_cdis` | 89 | 2.9 % |
| 0 | `en_carcinoma_invasivo` | 38 | 1.2 % |
| 5 | `en_cdis-en_tejido_no_neoplasico` | 15 | 0.5 % |
| 3 | `en_carcinoma_invasivo-en_tejido_no_neoplasico` | 13 | 0.4 % |
| 1 | `en_carcinoma_invasivo-en_cdis` | 11 | 0.4 % |
| 2 | `en_carcinoma_invasivo-en_cdis-en_tejido_no_neoplasico` | 6 | 0.2 % |

Distribución por split (join `splits_0.csv ⨯ dataset_label.csv`):

| clase | train | val | test |
|---|---|---|---|
| en_carcinoma_invasivo | 30 | 4 | 4 |
| en_carcinoma_invasivo-en_cdis | 9 | **1** | **1** |
| en_carcinoma_invasivo-en_cdis-en_tejido_no_neoplasico | 4 | **1** | **1** |
| en_carcinoma_invasivo-en_tejido_no_neoplasico | 11 | **1** | **1** |
| en_cdis | 73 | 8 | 8 |
| en_cdis-en_tejido_no_neoplasico | 13 | **1** | **1** |
| en_tejido_no_neoplasico | 128 | 16 | 17 |
| no_identificado | 2168 | 287 | 282 |

## Métricas finales (de `summary.csv`)

| test_auc | val_auc | test_acc | val_acc |
|---|---|---|---|
| 0.8117 | 0.6863 | 0.7219 | 0.7017 |

**Balanced accuracy (test) = 0.3076** — calculada del `split_0_results.pkl`
(media del recall por clase). Es la métrica honesta; ver abajo.

## Matriz de confusión (test, 302 slides) — fila = verdadera, col = predicha

```
verdadera \ predicha     cl0  cl1  cl2  cl3  cl4  cl5  cl6  cl7   total
carc_inv                   1    .    .    .    .    .    1    2      4
carc_inv+cdis              .    .    .    .    .    .    .    1      1
carc_inv+cdis+tejido       .    .    1    .    .    .    .    .      1
carc_inv+tejido            .    .    .    .    .    .    .    1      1
cdis                       .    .    .    1    2    .    1    4      8
cdis+tejido                .    .    .    .    .    .    1    .      1
tejido_no_neo              3    1    .    .    3    1    3    6     17
no_identificado            5    4    1    1   21    .   26  211    269
```

El modelo manda **74.5 % de las predicciones (225/302) a `no_identificado`**.

## Régimen de evaluación — el hallazgo crítico

`test_auc = 0.81` parece superar el 0.55 de V4, **pero no es un resultado
fuerte ni comparable**. Tres evidencias:

1. **Inversión val < test.** val_auc 0.69 < test_auc 0.81 → gap −0.125. Una
   generalización sana da test ≤ val. El AUC es un `nanmean` sobre 8 clases
   one-vs-rest, y **4 clases tienen 1 sola muestra en val/test** → un AUC con
   1 muestra es ruido. La inversión es la prueba de que la métrica es
   inestable: el 0.81 y el 0.69 son el mismo cálculo ruidoso que cayó
   distinto.
2. **`test_acc` 0.72 < baseline trivial 0.89.** Predecir siempre
   `no_identificado` acertaría 269/302 = 0.891. El modelo (0.722) es *peor*
   en accuracy cruda que la respuesta trivial — `weighted_sample` lo empuja a
   intentar clases minoritarias y las falla.
3. **Balanced accuracy 0.31.** Trata las 8 clases por igual. Random/trivial =
   0.125; el modelo (0.31) aprendió una señal débil pero está lejísimos de
   ser útil (>0.6–0.7 sería útil).

**Conclusión**: el baseline corre, es reproducible y termina limpio. El
cuello de botella **no es el entrenamiento sino el régimen de evaluación** de
esta task. Métrica recomendada de aquí en adelante: **balanced accuracy +
matriz de confusión**, nunca el macro-AUC solo, y siempre con el `n` por
clase.

## Hallazgo: estructura multi-label disfrazada de 8 clases

Las 8 clases son exactamente las combinaciones no vacías de **3 tejidos**
{carcinoma invasivo, CDIS, tejido no neoplásico} (2³−1 = 7) + `no_identificado`.
Es un **problema multi-etiqueta (3 binarios) aplastado en 8 clases
mutuamente excluyentes**. Aplastar multi-label en clases-combinación es lo
que fabrica las clases ultra-raras (la triple combinación: 6 slides totales).

**Propuesta para la reunión**: reformular como **3 tareas binarias**
(`¿microcalcificación en carcinoma invasivo? ¿en CDIS? ¿en tejido no
neoplásico?`). Cada binario tendría clases evaluables y un AUC con sentido.
Pendiente confirmar con Sebastián qué significa `no_identificado` (¿no hay
microcalcificación, o hay pero sin ubicar? — cambia toda la interpretación).

## Comparación contra V4 (referencia histórica)

V4 reportó microcalcificaciones test ≈ 0.55, val ≈ 0.82, gap 0.27, **n=548**.
Nuestra task `_pth` tiene **3072** slides (dataset post-expansión). **No es
blanco de reproducción**: distinto conjunto, y ambas métricas son ruidosas.
Reportar el número observado sin interpretarlo como mejora. Confirmar con
Sebastián la composición exacta de V4 (decisión #1 de la reunión).

## Convergencia (de los logs)

El modelo **sobreajusta de inmediato**: `train_error` baja a ~2 % y el mejor
checkpoint (mejor `val_loss`) es de la **época 6**; las ~45 épocas restantes
no mejoraron val. `EarlyStopping(patience=20, stop_epoch=50)` está hardcoded
en `utils/core_utils.py:194` → el job corre hasta la época 51 aunque el
`counter` sature en 20 mucho antes. El instance loss (`train_clustering_loss`)
converge; el bag loss se estanca — consistente con el Hallazgo 4 de `CLAUDE.md`.

## Run previo fallido

`results/failed_runs/4096_baseline_B8_topk_bug/` — job 4096 cayó por el bug
`topk` (slides de train con `<B` parches). Mitigado con el split filtrado
`minpatch16` + `scripts/preflight_minpatch.py`. Ver `docs/workarounds.md` §3.
