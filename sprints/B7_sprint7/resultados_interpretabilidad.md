# Resultados — Sprint 7: interpretabilidad CLAM vs Mammoth

> Job 4589 (entrenamiento pareado) cerrado el 18-jul-2026 14:20:55.
> Pre-registro: `prereg_entrenamiento_interp.md`. Política de eval B5.
> Commit de la verdad de campo: `684723b`.

## 1. Integridad del entrenamiento

30/30 runs completos (3 tareas × 2 brazos × 5 folds): 30 checkpoints, 30 `summary.csv`,
30 `split_*_results.pkl`, las 3 tareas con marca `done` y cero errores en el `.err`
(solo `FutureWarning` de `kaiming_uniform`, benigno).

**Paridad verificada, no asumida**: el md5 de los `slide_id` de test coincide fold a
fold entre brazos en las 3 tareas → el Δ pareado es válido por construcción
([[patron-paired-comparison-reuso-splits]]). Ambos brazos corrieron 52 épocas por fold
(`stop_epoch=50` hardcodeado + paciencia 20).

## 2. Métricas (política B5: balanced_acc Y AUC juntos)

| Tarea | n_test/fold | CLAM bal | MAM bal | Δ bal (folds+) | CLAM AUC | MAM AUC | Δ AUC (folds+) |
|---|---|---|---|---|---|---|---|
| tipo_histologico (3 clases) | ~202 | 0.665 ± 0.056 | 0.655 ± 0.047 | −0.010 ± 0.017 (1/5) | 0.833 ± 0.043 | 0.821 ± 0.056 | −0.012 ± 0.025 (3/5) |
| LVI `_ci_reform` | ~83 | 0.657 ± 0.040 | 0.634 ± 0.050 | −0.023 ± 0.086 (2/5) | 0.720 ± 0.032 | 0.684 ± 0.056 | −0.036 ± 0.073 (2/5) |
| CDIS `_ci_reform` | ~85 | 0.668 ± 0.098 | **0.742 ± 0.099** | **+0.074 ± 0.033 (5/5)** | 0.765 ± 0.111 | **0.825 ± 0.086** | **+0.060 ± 0.042 (5/5)** |

### Recall por clase (confusión sumada sobre los 5 folds)

| Tarea | Clase | n | Recall CLAM | Recall Mammoth |
|---|---|---|---|---|
| tipo_histologico | carcinoma_invasivo_tipo_no_especifico | 802 | 0.817 | 0.839 |
| tipo_histologico | carcinoma_lobulillar_invasivo | 121 | 0.744 | 0.769 |
| tipo_histologico | otros | 90 | 0.433 | 0.356 |
| CDIS | no | 65 | 0.477 | 0.569 |
| CDIS | si | 364 | 0.860 | 0.915 |
| LVI | ausente | 235 | 0.723 | 0.694 |
| LVI | presente | 181 | 0.591 | 0.575 |

**tipo_histologico y LVI confirman lo pre-registrado**: Δ dentro del ruido
(std ≥ |media|), consistente con el Hallazgo 12. La clase `otros` de tipo es la que
más sufre bajo Mammoth (0.433 → 0.356).

### El caso CDIS: la "sorpresa" que el pre-registro anticipó

El prereg §4 fijó: *"Un Δ grande y consistente a favor de Mammoth sería sorpresa
(a investigar, no a celebrar)"*. Es lo que ocurrió, y se reporta en ese registro.

Lo que sostiene la señal:
- 5/5 folds positivos en balanced_acc **y** en AUC, con std < |media| en balanced_acc.
- **No hubo colapso** pese al 85% positivo, y **suben los dos recalls** (`no`
  0.477→0.569, `si` 0.860→0.915). Eso descarta la firma de mover el umbral, que sube
  uno y hunde el otro (Hallazgo 14, [[calibracion-operating-point-palanca-b5]]).
- El AUC sube 5/5 → mejoró el **ranking**, no el punto de operación.
- **Corroborado en validación**: el mejor `val_loss` de Mammoth es menor que el de CLAM
  en 4/5 folds, y `val_loss` es el criterio de selección de checkpoint → no es un
  artefacto del test set.

Lo que obliga a frenar antes de llamarlo mejora:
- **n chico**: 65 negativos en total (~13 por fold); cada negativo vale ~7.7 puntos de
  recall de la clase 0. En bruto son 6 negativos y 20 positivos más acertados sobre 429.
- **`_ci_reform` es formulación nueva**, jamás incluida en las 12 configuraciones de
  Mammoth que cerraron el Hallazgo 12 → no contradice esos resultados en el mismo
  terreno; abre terreno nuevo.
- **Invierte el patrón declarado** en el Hallazgo 12 ("el efecto lo gobierna el balance:
  leve a favor en las balanceadas, nulo o en contra en las desbalanceadas"). Acá la
  tarea **más desbalanceada** (85/15) es la que gana y la **balanceada** (LVI 56/44) la
  que regresa.

**No se reabre el eje de rendimiento.** El Hallazgo 12 sigue cerrado; reabrirlo exige
regla 9.b (pre-registro nuevo, hipótesis primaria/alternativa/regresión, branch,
reviewer). Queda como candidato a réplica con más semillas o folds antes de presentarlo
a nadie como mejora.

## 3. Entregable central: comparación de atención CLAM vs Mammoth

7 slides (una por clase y tarea), todas del **test set del fold 0** (no vistas en
entrenamiento) y **bien clasificadas por ambos brazos**, para comparar *dónde mira* cada
uno sin el ruido de un error. Tooling: `scripts/clam_vs_mammoth_attention.py`.

Es apples-to-apples por construcción: `CLAM_MB_Mammoth` es subclase de `CLAM_MB` y
hereda su `forward`, así que la atención de ambos brazos sale del mismo código
(`model(h, attention_only=True)`). Gotcha aplicado: eso devuelve A **pre-softmax**; se
normaliza sobre los N parches antes de visualizar.

| Slide | Tarea | Clase | N parches | Spearman | Jaccard top-5% | Entropía CLAM | Entropía Mammoth |
|---|---|---|---|---|---|---|---|
| TCGA-AO-A12D | tipo | inv. tipo no especifico | 7097 | 0.848 | 0.079 | 0.873 | 0.929 |
| TCGA-AC-A8OS | tipo | lobulillar invasivo | 4201 | 0.885 | 0.243 | 0.760 | 0.830 |
| TCGA-E9-A1NE | tipo | otros | 5592 | 0.669 | 0.315 | 0.341 | 0.675 |
| TCGA-A7-A4SB | CDIS | no | 2793 | 0.921 | 0.261 | 0.887 | 0.938 |
| TCGA-D8-A1XB | CDIS | si | 16442 | 0.847 | 0.202 | 0.642 | 0.927 |
| TCGA-D8-A1XW | LVI | ausente | 22206 | 0.796 | 0.101 | 0.985 | 0.975 |
| TCGA-D8-A1X5 | LVI | presente | 28170 | 0.668 | 0.008 | 0.978 | 0.986 |

**Agregado (n=7):** Spearman 0.805 (rango 0.668–0.921) · Jaccard top-5% 0.172
(0.008–0.315) · Jaccard top-1% 0.073 · entropía CLAM 0.781 vs Mammoth 0.894
(Δ +0.113, **6/7 slides con Mammoth más difuso**).

### Lectura

1. **Coinciden en el mapa grueso.** La correlación de rangos alta (0.805 medio) dice que
   ambos ordenan el tejido de forma parecida: la región que importa es la misma.
2. **Difieren en los picos.** El solapamiento del top-5% de parches es bajo (0.172) y el
   del top-1% casi nulo (0.073). O sea: **mismo barrio, distintas casas**. Los parches
   concretos que cada modelo pone arriba son en su mayoría distintos.
3. **Mammoth reparte la atención; CLAM la concentra.** Mammoth es más difuso en 6/7
   slides. El contraste más fuerte está en la slide CDIS positiva (0.642 → 0.927) y en
   `otros` de tipo (0.341 → 0.675), justo las dos donde CLAM más se concentra.

La observación de que la mayor difusión aparezca en CDIS, la tarea donde Mammoth también
mide mejor, es **sugerente pero no demostrada**: con 7 slides no se puede atribuir la
diferencia de métrica a la forma de la atención. Queda como hipótesis, no como
explicación.

**Nombres de tejido**: cuando se describan las regiones, va la advertencia de
[[mammoth-interpretabilidad-objA]] — son **lectura visual nuestra, no anotación**; no
hay ground truth de tejido por parche y el sign-off de patólogo sigue pendiente.

Figuras por slide en `results/b7_mammoth_interp/interpretabilidad/<tarea>/<slide>/`:
`attention_clam.png`, `attention_mammoth.png`, `attention_side_by_side.png` (CLAM |
Mammoth | delta) y `attention_stats.json`.

## 4. Hallazgo lateral: la geometría del parche no se puede inferir de la magnificación

Al montar los heatmaps apareció un **bug en el tooling heredado de OBJ-A**.
`patch_size_at_level0()` (`mammoth_interpretability.py:254`) infiere el tamaño de parche
desde la magnificación y **fuerza el fallback de 40× cuando `mag <= 20`**. Sobre las 7
slides devolvía **512 px**, cuando la geometría real de las coords del h5 es **448 px**
en todas (= el parche de magnificación de Sebastián, 448@×40→224). Cada parche se
dibujaba ~14% sobredimensionado.

Peor: `TCGA-AO-A12D` es **genuinamente 20×** (mpp 0.4992, `objective-power` 20 y
`AppMag` 20, los tres concordantes — acá el tag Aperio *no* miente) y la función la
habría tratado como 40×.

**Fix**: derivar el tamaño de parche de la **moda del paso entre coords contiguas del
h5** — las coords no mienten. Implementado en `clam_vs_mammoth_attention.py`
(`infer_patch_size_level0`) y expuesto como flag `--patch-size-level0` en
`mammoth_interpretability.py` (aditivo, default = comportamiento OBJ-A, no altera su
reproducibilidad).

### Consecuencia de datos: TCGA no es homogénea en magnificación

Muestreo de 200 de las 864 slides TCGA de estas 3 tareas (leído con openslide):

| Magnificación nativa | Slides | Campo físico de un parche de 448 px |
|---|---|---|
| ~40× (mpp 0.233–0.253) | 189 (94.5%) | 104–113 µm |
| **~20× (mpp 0.499)** | **7 (3.5%)** | **224 µm (el doble)** |
| ~61× (mpp 0.164) | 3 (1.5%) | 74 µm |
| sin mpp | 1 (0.5%) | no determinable |

Extrapolado a las 864 slides TCGA de estas tareas: ~30 slides reciben el doble de campo
físico por parche y ~13 reciben dos tercios. Esto **extiende
[[cohortes-magnificacion-fisica]]**: el confound de escala no vive solo *entre* cohortes
(TCGA vs privado vs HistAI), también **dentro de TCGA**, porque la extracción se
parametriza en píxeles a nivel 0 y no en µm/px físicos. Es minoritario y acotado, pero
es exactamente el modo de falla que esa memoria anticipa.

## 5. Q1 — ¿cuántos expertos/slots usa Mammoth?

Ver `respuesta_q1_expertos_slots.md` (generado por
`scripts/answer_q1_expertos_slots.py` sobre los `slot_usage.csv`).

> **Estado 19-jul: CERRADA con las 7/7 láminas.** El ruteo desatado terminó limpio el
> 18-jul 22:24 (`setsid`, ppid=1, log en `logs/b7_expert_interp_desatado.log`), tras morir
> dos veces por colgar del shell de la sesión (workaround J,
> [[proceso-cpu-largo-desatado-setsid]]).

«Peso por slot» = `combine_weights`, la segunda softmax sobre los E·S=300 slots
(`mammoth.py:411`) — **no** el top-k de parches por experto
([[mammoth-slot-routing-weight]]).

### 5.1 Respuesta

| Lámina | Parches | Slots efect. (de 300) | Expertos efect. (de 30) |
|---|---|---|---|
| `TCGA-A7-A4SB` (CDIS) | 2 793 | 89.7 | 30.0 |
| `TCGA-AC-A8OS` (tipo) | 4 201 | 156.0 | 30.0 |
| `TCGA-E9-A1NE` (tipo) | 5 592 | 147.5 | 30.0 |
| `TCGA-AO-A12D` (tipo) | 7 097 | 178.3 | 30.0 |
| `TCGA-D8-A1XB` (CDIS) | 16 442 | 180.3 | 30.0 |
| `TCGA-D8-A1XW` (LVI) | 22 206 | 196.4 | 30.0 |
| `TCGA-D8-A1X5` (LVI) | 28 170 | 162.4 | 30.0 |
| **media** | | **158.7** | **30.0** |

**Expertos: no están sobredimensionados.** 30.0/30 en las 7 láminas, y los cuantiles dan
`e50=15`, `e90=27` **idénticos en todas** — exactamente el reparto uniforme. Transversal a
las 3 tareas.

**Slots: ahí está el margen de recorte.** Media 158.7/300 (sd 34.6): cerca de la mitad del
presupuesto aporta poco al peso final.

**La dispersión NO es por tarea, sigue al tamaño de la lámina.** Las dos láminas de CDIS son
los **dos extremos** del rango (89.7 y 180.3), lo que descarta el efecto de tarea. El orden
sigue al nº de parches: Spearman ρ=0.750 (p=0.052, n=7); excluyendo la lámina chica (2 793
parches, la mitad que la siguiente) queda **170.2 ± 18.1**. Lectura mecánica: menos parches,
menos morfología distinta que rutear.

> **Fuerza de la evidencia.** Con n=7 esto **describe** el comportamiento, no lo establece:
> la correlación con el tamaño se apoya en **un solo** caso de lámina chica, y p=0.052 está
> al borde. Lo que sí es sólido es el resultado de expertos (idéntico en 7/7).

**Gotcha del agregador (fix `f0d043e`):** `answer_q1_expertos_slots.py` globeaba
`slot_usage.csv`, que es un artefacto **intermedio** — podía promediar una lámina en vuelo
(CSV a medio escribir) o de una corrida cortada, **sin avisar**. Ahora filtra por `meta.json`
(marcador final, misma regla que el driver reanudable) y reporta las excluidas.

## 6. Tabla por tarea (requisito de Sebastián)

`tabla_por_tarea.md`: slides usadas, magnificación física µm/px leída de cada WSI,
dataset/cohorte/n y etiqueta del patólogo. Los n y las distribuciones coinciden
exactamente con el pre-registro (2027 / 862 / 836).

## 7. Reproducir

```bash
PY=/home/sdonoso/miniconda3/envs/clam_latest/bin/python   # workaround B
# metricas agregadas de los 30 runs
$PY scripts/extract_metrics.py    # o el parser del sprint
# seleccion de slides (prefiere cohortes con MPP confiable)
$PY scripts/select_interp_slides.py --fold 0 --per-class 1
# comparacion de atencion CLAM vs Mammoth (CPU)
CUDA_VISIBLE_DEVICES="" $PY scripts/clam_vs_mammoth_attention.py
# ruteo por experto/slot (CPU, patch size real del h5)
bash scripts/run_b7_expert_interp.sh
# Q1
$PY scripts/answer_q1_expertos_slots.py
# tabla por tarea
$PY scripts/build_interp_task_table.py
```

Todo lo de interpretabilidad es **Etapa 0: CPU, post-hoc, sin GPU y sin sbatch** —
inferencia sobre checkpoints congelados, no toca modelo ni training.
