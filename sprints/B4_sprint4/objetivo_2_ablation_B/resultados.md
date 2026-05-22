# Objetivo 2 — Resultados de la ablación B=8 vs B=16 (MicroCalcificaciones, `_pth`)

> Job `4099` (B=16) **COMPLETED** el 21 may 2026. Números reales de
> `results/ablation_microcalc_pth_B16_minpatch16/summary.csv`,
> `split_0_results.pkl` y el `.out`. El brazo B=8 es el baseline del
> Objetivo 1 (job `4098`). No se inventa nada: todo sale de los artefactos.

## Setup

Ablación **estrictamente controlada**: B=8 y B=16 usan el **mismo split
filtrado** `microcalcificaciones_pth_100_minpatch16` (`min_patches=16`
elegido justo para que el mismo split sirva a ambos brazos). La **única**
variable es `--B`.

| Campo | B=8 (baseline, Obj 1) | B=16 (ablación, Obj 2) |
|---|---|---|
| Job SLURM | `4098` | `4099` |
| `--B` | 8 | 16 |
| Script | `slurm/baseline_microcalc_B8_minpatch16.slurm` | `slurm/ablation_microcalc_B16_minpatch16.slurm` |
| Tarea | `microcalcificaciones_pth` (8 clases) | idem |
| Split | `splits_local/microcalcificaciones_pth_100_minpatch16` | idem (mismo archivo) |
| Resto de args | bendecidos (`CLAUDE.md`) | idénticos |
| Duración | 11:06→15:18 (~4h 11m) | 15:18→18:44 (~3h 26m) |
| Mejor checkpoint | época 6 | época 7 |

## Tabla comparativa

| Métrica | B=8 | B=16 | Δ (B16−B8) | Veredicto |
|---|---|---|---|---|
| **test_auc** | 0,812 | 0,821 | **+0,009** | < umbral +0,03 → **banda ambigua** |
| val_auc | 0,686 | 0,691 | +0,005 | — |
| gap val−test | −0,126 | −0,130 | −0,004 | **inversión persiste** (val < test) |
| test_acc | 0,722 | 0,709 | −0,013 | baja; sigue < baseline trivial 0,89 |
| **balanced accuracy** | **0,308** | **0,242** | **−0,066** | **empeora** |
| train_clustering_loss final | 0,0089 | 0,0126 | +0,0037 | **sube** (contradice el mecanismo) |

> Métrica primaria = **balanced accuracy** (recalculada del
> `split_0_results.pkl`, media del recall por clase). El macro-AUC solo,
> nunca — `CLAUDE.md` Hallazgo 6.

## Hipótesis y métrica de éxito (predefinidas, antes de correr)

- **Hipótesis**: aumentar B de 8 a 16 enriquece la señal supervisada del
  `SmoothTop1SVM` en el `instance_classifier` path (top-B/bottom-B
  sampling de `inst_eval`) → mejores pseudo-etiquetas en un régimen focal
  como microcalcificaciones.
- **Métrica de éxito**: **Δtest_auc ≥ +0,03** (B16 − B8), manteniendo o
  reduciendo el gap val−test.
- **Banda ambigua predefinida**: si `|Δ| < 0,02` → reportar literal como
  **"no concluyente / B no relevante"**, sin forzar interpretación.

## Veredicto — hipótesis NO confirmada

El resultado cae **de lleno en la banda ambigua** y, en las métricas
honestas, **empeora**:

1. **Δtest_auc = +0,009** — un tercio del umbral +0,03, y dentro de la
   banda `|Δ| < 0,02` predefinida como "no concluyente". Además el AUC
   sobre 8 clases con 4 clases de n=1 en val/test es ruidoso de origen
   (Objetivo 1): ese +0,009 está **por debajo del piso de ruido** de la
   propia métrica.
2. **Balanced accuracy BAJÓ: 0,308 → 0,242.** La métrica honesta —la que
   trata las 8 clases por igual— se mueve en la **dirección contraria** a
   la hipótesis. B=16 es *peor* repartiendo el acierto entre clases.
3. **train_clustering_loss SUBIÓ: 0,0089 → 0,0126.** Esto **contradice el
   mecanismo mismo** de la hipótesis: si más B enriqueciera la señal
   supervisada al SVM, el instance loss debería **bajar**, no subir. El
   instance classifier converge igual de bien en ambos brazos (~99 % de
   clustering acc en los logs), pero **más B no produjo mejores
   pseudo-etiquetas** — produjo, si acaso, un instance loss algo mayor.
4. **La inversión val < test persiste** (gap −0,126 → −0,130). La firma
   de inestabilidad del régimen de evaluación del Objetivo 1 **no se
   corrige** subiendo B — porque no era un problema de B.

## Matriz de confusión — B=16 (test, 302 slides) — fila = verdadera, col = predicha

```
verdadera \ predicha     cl0  cl1  cl2  cl3  cl4  cl5  cl6  cl7   total
carc_inv                   2    .    .    .    .    .    1    1      4
carc_inv+cdis              .    .    .    .    .    .    .    1      1
carc_inv+cdis+tejido       .    .    .    1    .    .    .    .      1
carc_inv+tejido            .    .    .    .    .    .    .    1      1
cdis                       .    .    .    .    4    .    1    3      8
cdis+tejido                .    .    .    .    .    .    1    .      1
tejido_no_neo              3    1    .    .    3    1    3    6     17
no_identificado            6    4    2    4   24    .   24  205    269
```

B=16 manda **71,9 % de las predicciones (217/302) a `no_identificado`**
(B=8: 74,5 %). El colapso a la clase mayoritaria sigue intacto. El swing
de las clases de n=1 entre brazos (cl2 recall 1,00 en B=8 → 0,00 en B=16;
cl0 0,25 → 0,50) es **puro ruido de muestra única** — la misma evidencia
del Objetivo 1 de que con n=1 no hay métrica.

## Conclusión de fondo — la ablación justifica la reformulación

La ablación es **negativa, y eso es exactamente lo informativo**:

> **`B` es un hiperparámetro. Ajustarlo no mueve la aguja porque el cuello
> de botella no son los hiperparámetros — es la FORMULACIÓN de la tarea.**

Duplicar B (de 8 a 16) toca el muestreo top-B/bottom-B de `inst_eval`,
pero deja **intacto** el problema real: las 8 clases son un multi-etiqueta
de 3 tejidos aplastado en clases-combinación, con 4 clases de 1 sola
muestra en val/test (Objetivo 1, `resultados.md`). Ningún valor de B
arregla eso.

Por eso esta ablación **es la evidencia empírica que respalda la
reformulación**: se probó la palanca barata (un hiperparámetro), se midió
con una métrica de éxito predefinida, y el resultado dice —sin
ambigüedad— que la palanca correcta está en otro nivel: **reformular la
tarea en 3 binarios** (ver `sprints/B4_sprint4/reformulacion_multilabel/`
y `objetivo_3_modulo_mil_alternativo/investigacion/05_…desbalance.md`).

## Convergencia

Mismo patrón que el baseline: B=16 **sobreajusta de inmediato** — mejor
checkpoint (mejor `val_loss`) en la **época 7**; el run llega a la época
51 (`EarlyStopping` con `stop_epoch=50` hardcoded en
`utils/core_utils.py:194`) sin que las ~44 épocas restantes mejoren val.
`train_error` cae a ~1,4 %. Subir B no cambió la dinámica de sobreajuste.

## Costos

| | inicio | fin | duración | mem |
|---|---|---|---|---|
| B=8 (4098) | 21 may 11:06 | 21 may 15:18 | ~4h 11m | `--mem=32G` |
| B=16 (4099) | 21 may 15:18 | 21 may 18:44 | ~3h 26m | `--mem=32G` |

Régimen de evaluación: idéntico al baseline (8 clases, 4 con n=1 en
val/test). Todos los caveats del Objetivo 1 aplican sin cambios.
