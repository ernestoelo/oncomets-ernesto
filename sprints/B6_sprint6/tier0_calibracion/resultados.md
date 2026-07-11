# Tier 0 — calibración post-hoc del operating-point (resultados)

> **Palanca #1 de la escalera de palancas vivas** ([[calibracion-tier0-pendiente-ejecutar]]):
> gratis, CPU, sin GPU, sin reviewer (post-hoc, no toca training → regla 9 trivial).
> Re-umbraliza el operating-point de checkpoints CLAM ya entrenados SIN reentrenar.
> Ejecutado 10-jul-2026. Script: `scripts/tier0_calibration.py`. Datos: `tier0_results.json`.

## Qué se hizo

Por tarea y fold: el bias por clase (`pred = argmax_c(log p_c + b_c)`) se elige **en VAL**
(inferencia CPU con `s_<fold>_checkpoint.pt`) maximizando balanced_accuracy, y se **congela a
TEST**. Comparación **paired por fold** vs el argmax actual (bias 0). Binario ⇒ un umbral;
multiclase ⇒ coordinate-ascent del bias por clase. Guardrail duro: **el operating-point se elige
SIEMPRE en val, nunca en test**; el `oracle` (bias ajustado en test) se reporta SOLO como
upper-bound de factibilidad, jamás como resultado.

**Regla de eval B5:** balanced_acc **Y** AUC juntos + recall minoritaria + confusión + n/clase.
El AUC es **invariante** a la calibración (recalibra el operating-point, no el ranking) → sirve de
cota del headroom disponible.

## Resultados (5-fold, features actuales, paired)

| Tarea | n_cls | AUC test | bal_acc base (argmax) | bal_acc **calibrado** | Δ pareado | signos | recall minoritaria | oracle (cota) |
|---|---|---|---|---|---|---|---|---|
| **grado_mitotic_3clases** | 3 | 0.721 ± 0.036 | 0.484 ± 0.053 | **0.531 ± 0.026** | **+0.046 ± 0.029** | **+5 / −0** | 0.49 → 0.58 | 0.571 |
| invasion_linfatica_vascular | 3 | 0.823 ± 0.025 | 0.607 ± 0.017 | 0.616 ± 0.024 | +0.009 ± 0.020 | +4 / −1 | 0.65 → 0.43 | 0.650 |
| cdis_necrosis_2clases | 2 | 0.718 ± 0.057 | 0.655 ± 0.058 | 0.650 ± 0.075 | −0.005 ± 0.024 | +2 / −2 | 0.50 → 0.57 | 0.731 |

## Lectura (honesta)

**La calibración es una palanca REAL pero task-dependiente: entrega un lift consistente de
balanced_acc exactamente donde el modelo colapsa a la mayoritaria, y es null/ruido donde el modelo
ya reparte sus predicciones.**

- **mitotic = win limpio (+0.046, 5/5 folds+).** Es la tarea que en B5 (Hallazgo 13) **colapsaba al
  argmax** (siempre `score_1`, bal 0.333 exacto) con AUC latente sobreviviente. Re-umbralizar
  recupera la minoritaria (`score_3` 0.49→0.58 recall) y sube bal 0.484→0.531 — captura casi todo el
  headroom del oracle (0.571). Supera también el histórico congelado (0.494). **Confirma la predicción
  de la memoria:** bajo desbalance el argmax optimiza accuracy (métrica equivocada) mientras el ranking
  sobrevive → la calibración "lee mejor" a CLAM, acotada por el AUC.
- **invasión = null en términos absolutos.** Δ +0.009 dentro del ruido (+4/−1) y, por el drift de
  features (abajo), el calibrado 0.616 **ni siquiera supera** el baseline histórico congelado (0.622).
  Además el operating-point de val cambia la mezcla (sube `ausente`, hunde `presente`: recall
  minoritaria 0.65→0.43) → no es free lunch, redistribuye. El modelo ya tenía bal 0.607 y AUC 0.823
  (poco colapso) → poco que recuperar.
- **necrosis = null (−0.005, +2/−2).** El oracle tiene headroom (0.731 vs 0.655) pero el umbral de val
  **no transfiere** a test (n_test≈40, val≈39 → estimación del umbral ruidosa con tan pocas muestras).

**Convergencia:** esto es la misma física que el eje loss de desbalance (Hallazgo 14, `class_balanced`
= H_reg): re-thresholding ≡ mover el operating-point → sube recall minoritaria, puede hundir la
mayoritaria, y la balanced_acc neta sube **solo si** el modelo estaba colapsado. Mitotic lo estaba;
invasión/necrosis no. [[calibracion-operating-point-palanca-b5]].

## Matrices de confusión (sumadas sobre folds) — base → calibrado

- **mitotic** (filas=verdad `score_1/2/3`): base `[[234,58,28],[76,33,33],[25,39,62]]` →
  cal `[[227,61,32],[64,43,35],[23,30,73]]` (score_3 correctos 62→73; score_2 33→43).
- **invasión** (`ausente/no_ident/presente`): base `[[92,46,103],[76,774,135],[31,32,119]]` →
  cal `[[157,32,52],[162,756,67],[72,32,78]]` (ausente 92→157 pero presente 119→78 = el trade-off).
- **necrosis** (`no/si`): base `[[20,20],[30,129]]` → cal `[[23,17],[44,115]]`.

## Caveat de reproducibilidad — drift de features TCGA (hallazgo colateral)

Las features `clam_environ/environ/features/pt_files/*.pt` son un dir **live que muta**
(workaround del CLAUDE.md). Un subconjunto de slides **TCGA se re-extrajo el 26-27 jun 2026**
(mtime posterior a estos runs, que son de jun 4/10) → re-inferir hoy **diverge del `.pkl` congelado**
en esas slides: invasión 92 slides drift, mitotic 31, necrosis 13. Todo el análisis se corre sobre
**features actuales para val Y test** (procedencia consistente → el Δ pareado es válido); el baseline
histórico congelado del `.pkl` se reporta solo como contexto. **Implicación:** cualquier resultado
previo con slides TCGA cambia levemente si se re-infiere. **A surfacear con Sebastián** (¿re-extracción
intencional? ¿ligada a `features_tcga_224x40` / la magnificación x40?). No se toca nada — read-only.

## Estado y siguiente

- **Entregable presentable** para Sebastián (lunes): "calibración post-hoc sube bal_acc de mitotic
  +0.046 (5/5) sin reentrenar; null en invasión/necrosis — la palanca rinde donde el modelo colapsa".
  Hermana del CBIR/retrieval ([[retrieval-investigacion-b5]]).
- **NO cierra** con umbral rígido GO/NO-GO (regla 9.a). La dirección esperada (sube recall minoritaria,
  puede hundir mayoritaria, neto positivo solo si hay colapso) **se cumplió**.
- Pendiente opcional: extender a las 3 binarias de microcalc (target del B6) para tener el baseline
  calibrado antes del experimento de magnificación.
