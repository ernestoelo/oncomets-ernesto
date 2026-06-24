# Pre-registración (regla 9) — Loss de desbalance: focal / class-balanced vs CLAM-CE

> **Fase ARGUMENTO antes de código.** Este documento se escribe ANTES de tocar
> `scripts/train_dsmil.py`. Toca el objetivo de entrenamiento (la bag loss) → exige
> regla 9 (hipótesis + métrica + dirección) + reviewer + sbatch con OK explícito de
> Ernesto. NO toca `clam_environ/` (regla 2). NO es un swap de arquitectura
> (Hallazgos 11/12/13) — el modelo es CLAM_MB intacto; el único delta es **cómo se
> pondera el gradiente del clasificador de bag**. Eje = **desbalance** (Eje C1 de
> `investigacion_que_integrar/analisis.md` §3).

---

## 0. Encuadre — por qué este eje y por qué NO es "mammoth #3"

Los 3 ejes de **arquitectura** están cerrados con 0 palancas (agregador/DSMIL H11,
patch-embed/mammoth H12 — 12 tareas, lenguaje+tile/PathPT H13). El cuello = **datos /
desbalance / contexto espacial**. Este experimento NO cambia el modelo: ataca la
**mitad "desbalance"** del cuello por la vía de menor fricción posible.

El modo de falla está **documentado en nuestras propias matrices de confusión**: bajo
desbalance, CLAM colapsa hacia la mayoritaria (sub-detecta la minoritaria). Es lo
mismo que `keep_slots=True` mitigaba *mecánicamente* (Obj 3 §6.3), pero acá se ataca
por el **objetivo de entrenamiento**, no por la arquitectura.

`--weighted_sample` (arg bendecido, ya activo: `train_dsmil.py` usa
`weighted=True` en el train loader) re-balancea el **muestreo**. Pero la bag loss
sigue siendo **CE plana** (`train_dsmil.py:518` → `nn.CrossEntropyLoss()`). La
re-ponderación a nivel **pérdida** es la palanca complementaria **nunca probada**.

**Relación con calibración (Eje C0):** la re-ponderación de la pérdida es el análogo
*en training* de la calibración del operating-point *post-hoc*. C0 mueve el umbral
sobre scores fijos; este mueve el gradiente para que el modelo aprenda a no colapsar.
Son hermanos, no sustitutos.

---

## 1. Cambio mínimo (lo que tocará el código)

- Nuevo flag `--bag_loss {ce, focal, class_balanced}` (default `ce` → **retro-compatible**:
  los baselines en disco siguen siendo el mismo CE).
- `focal`: focal loss multiclase (Lin et al. 2017), `--focal_gamma` (default 2.0),
  **sin** α de clase (el focusing por γ es ortogonal al `weighted_sample`).
- `class_balanced`: CE con pesos por clase "class-balanced" por número efectivo
  (Cui et al. 2019), `w_c = (1-β)/(1-β^{n_c})`, `--cb_beta` (default 0.9999),
  normalizados a media 1. Los `n_c` se leen de `train_split.slide_cls_ids[c]`
  (mismo conteo que usa el sampler `weighted`).
- La **misma** loss se usa en train y en val (objetivo consistente para la selección
  de checkpoint por `val_loss`). Decisión de diseño pre-registrada: bajo desbalance,
  un `val_loss` re-ponderado selecciona checkpoints alineados con balanced_acc (la
  métrica que nos importa), no con accuracy. **Nota de análisis (Obs O2 reviewer):** esto
  hace que el `val_loss` *en valor absoluto* de los brazos focal/CB **no sea comparable**
  con el del baseline CE (escalas distintas) → NO comparar curvas de val_loss entre brazos;
  la métrica decisiva sigue siendo el test balanced_acc paired.
- Modelo, harness, splits, hiperparámetros: **idénticos** a los baselines.

**Confound declarado (honestidad):** `class_balanced` se apila SOBRE `weighted_sample`
(ambos re-balancean). La pregunta exacta que responde es *"¿la re-ponderación de la
pérdida agrega algo POR ENCIMA del re-muestreo que ya tiene el baseline?"*. Si
sobre-corrige (hunde la mayoritaria más de lo que rescata la minoritaria → bal_acc
neta ≤ CLAM), eso es **H_reg**, un hallazgo válido. `focal` (sin α) apila un mecanismo
distinto (focusing por confianza), menos propenso a la doble corrección.

---

## 2. Hipótesis (mecanismo)

Una pérdida que sube el gradiente de la clase minoritaria (CB-CE) o baja el de los
ejemplos fáciles de la mayoritaria (focal-γ) debe **reducir el colapso a la
mayoritaria** → subir el **recall de la(s) minoritaria(s)** → subir **balanced_acc**,
**sin** cambiar la calidad del ranking (AUC ≈ igual: las features discriminativas son
las mismas; se redistribuye la capacidad de decisión, como hacía `keep_slots`
mecánicamente).

- **H1 (primaria):** Δ balanced_acc (variante − CLAM-CE) **> 0**, consistente en signo
  a través de folds, y **mayor donde hay más headroom de ranking** (brecha AUC↔bal_acc
  grande), con |Δ AUC| chico.
- **H_alt:** Δ cruza 0 / std ≫ |media| → la pérdida **no es palanca** (mismo veredicto
  que los 3 ejes de arquitectura; el cuello no es el objetivo sino los datos).
- **H_reg:** Δ balanced_acc **< 0** consistente → la re-ponderación **perjudica**
  (sobre-corrige; hunde la mayoritaria). Esperable sobre todo en `class_balanced`
  apilado sobre `weighted_sample`.
- **Desempate mecanístico (manda el gap de recall, como Obj 3 §2):** una palanca
  genuina sube el recall de la minoritaria **y** la bal_acc neta por encima de CLAM.
  Si el recall de la minoritaria sube pero la mayoritaria se hunde y la bal_acc neta
  queda ≤ CLAM, es **re-balanceo, no palanca** (el matiz de `keep_slots`).

---

## 3. Métrica + subset + dirección (política eval B5)

- **Primaria:** balanced_acc en **test**, **paired por fold** (Δ_i = variante_i −
  CLAM-CE_i sobre el mismo `splits_<f>.csv`).
- **Reportadas siempre juntas** ([[eval-reporte-auc-y-umbrales-obj6]]): balanced_acc
  **y** AUC (binarias ROC; invasión macro-OVR) **+ matriz de confusión + recall por
  clase con n**. Sin gate numérico (regla 9.a): lectura cualitativa
  (consistencia de signo, magnitud vs varianza vs trivial, y gap de recall decisivo).
- **Contrastes:** C_focal = (CLAM+focal) − (CLAM+CE) · C_cb = (CLAM+class_balanced) −
  (CLAM+CE). Ambos paired vs el MISMO baseline CLAM-CE en disco.

### Expectativa por tarea (números base de los baselines CLAM-CE ya en disco)

| tarea | n / %pos | CLAM bal / AUC | recall minoritaria (CLAM) | headroom (brecha AUC↔bal) | expectativa pre-registrada |
|---|---|---|---|---|---|
| **invasión** 3-clase | 2814 | 0.622 / 0.828 | `presente` 0.577, `ausente` 0.498 | **alta (0.21)** | **mejor candidata** → H1 si la palanca existe |
| **carcinoma** | 328 / 21% | 0.639 / 0.732 | `si` 0.371 | media | desbalance alto, AUC modesto → probable re-balanceo |
| **cdis** | 328 / 36% | 0.595 / 0.652 | `si` 0.377 | baja (AUC 0.65) | poco headroom → probable H_alt/re-balanceo |
| **tejido** | 328 / 58% | 0.577 / 0.646 | `no` 0.500 | baja, ya balanceada | **control** → esperado ≈ null |

### Expectativa global honesta (regla 9.a + [[completitud-matriz-por-defensibilidad]])

Dado el techo de datos confirmado en 3 ejes (+ PathPT externo), la expectativa
**primaria honesta** es **modesta/null como palanca** sobre balanced_acc (es probable
que el cuello no sea el objetivo). PERO: (a) el **mecanismo** (recuperación del recall
de la minoritaria) es probable que sea visible; (b) es el knob de desbalance **más
barato y nunca probado**, y completarlo es **defensible ante la presentación** (cierra
el eje desbalance igual que cerramos arquitectura); (c) si invasión (mayor headroom)
diera H1, sería la primera señal positiva del trimestre. No se vende como "le ganamos
a CLAM": se reporta dirección + consistencia + gap, sin gate mágico.

---

## 4. Diseño paired (patrón [[patron-paired-comparison-reuso-splits]])

- **Baseline (en disco, NO se re-corre):** CLAM_MB + CE + weighted_sample.
  - invasión: `results/obj2_mammoth/invasion_linfatica_vascular_pth/` (brazo `clam_*`).
  - tejido: `results/obj6_mammoth_binarias_tejido_no_neoplasico/` (brazo `clam_*`).
  - carcinoma: `results/obj6_mammoth_binarias_carcinoma_invasivo/`.
  - cdis: `results/obj6_mammoth_binarias_cdis/`.
- **Brazos nuevos a GPU:** `clam` + `--bag_loss focal` y `clam` + `--bag_loss class_balanced`.
- **Splits:** `data/splits_kfold/<task>_pth_100/splits_{0..4}.csv` (idénticos al
  baseline; el nombre de tarea ya incluye el sufijo `_pth`).
- **Hiperparámetros fijos:** `B 8 · bag_weight 0.7 · lr 2e-4 · reg 1e-5 · drop_out 0.25 ·
  embed_dim 512 · max_epochs 30 · early_stopping · patience 20 · stop_epoch 50 · seed 1 ·
  weighted_sample ON`.
- **Escala:** 4 tareas × 2 brazos × 5 folds = 40 runs. **Olas:** prudente primero
  (3 binarias, n=328, livianas → validan pipeline) y luego invasión (n=2814, pesada).

---

## 5. Validación previa (gates del .slurm — workaround G)

1. `verify_kfold_splits.py` (splits consistentes).
2. `tests/test_loss_cpu.py` (NUEVO): valida que `focal`/`class_balanced` corren en CPU,
   producen loss finita, `ce` == baseline, y que CB-weights reproducen `(1-β)/(1-β^n)`.
3. `preflight_minpatch.py` por fold (ninguna slide de train con n_patches < B).

Si cualquiera falla, el job aborta en segundos (no gasta GPU).

---

## 6. Qué NO promete (caveats — regla 5)

- **No rompe el techo de datos.** Acotado por la señal en CONCH/el AUC (igual que la
  calibración C0). Su valor es atacar el colapso documentado, no "ganar como modelo".
- `class_balanced` apilado sobre `weighted_sample` puede sobre-corregir (H_reg) — es
  una pregunta legítima, no un bug.
- Todo número se reporta paired + con n por clase; el AUC nunca aislado.

---

## ADDENDUM (2026-06-24) — bug de implementación en el brazo `cb` del job 4463 + fix

**Qué pasó.** El job 4463 (binarias, focal+cb × 3 tareas × k=5) terminó 30/30. Al
verificar, el brazo **`cb` (class_balanced) salió byte-idéntico al baseline CE** en las
3 tareas (Δ bAcc = Δ AUC = +0.000 ± 0.000, todos los folds 0.0; predicciones idénticas
slide a slide, diff vacío). El brazo `focal` sí difería de CE (válido).

**Causa raíz (no es un hallazgo, es un bug).** `build_bag_loss("class_balanced", …)`
devolvía `nn.CrossEntropyLoss(weight=w)` con `reduction='mean'` (default). En MIL el
loader usa **`batch_size=1`** (un slide = un bag por forward). La CE ponderada con
reduction='mean' normaliza por la **suma de pesos de los targets del batch**; con un
único sample de clase `y` el denominador es `w_y` → `L = w_y·CE / w_y = CE`: **el peso
se cancela**. Verificado numéricamente (`CE_w(mean) == CE_plana` exacto a batch=1). El
print `[INFO] class_balanced weights` confirmaba que la rama corría con pesos correctos
(`[0.413, 1.587]` etc.), pero la loss los anulaba. `focal` no sufre esto: su modulación
`(1-pt)^γ` es multiplicativa **por sample** y sobrevive el `.mean()` de un elemento.

**Fix (NO cambia la hipótesis/métrica/dirección registradas — solo hace funcional el
diseño ya argumentado §1-§3).** Nueva clase `ClassBalancedCE` que computa
`F.cross_entropy(logits, target, weight=w, reduction='none').mean()` = `mean_i w_{y_i}·CE_i`
(class-balanced de Cui textbook), que con batch=1 da `w_y·CE` (peso aplicado) y es robusto
a cualquier batch size. Es la **misma fórmula de pesos** (número efectivo, β=0.9999,
normalizados a media 1); el único cambio es **cómo se reduce** la loss para que el peso no
se cancele. Es bug-fix de implementación, **no** reapertura de una decisión descartada
(no aplica regla 9.b) ni un mecanismo nuevo.

**Test de regresión.** `tests/test_loss_cpu.py::test_class_balanced_applies_weight_batch1`
exige que a batch=1 `CB == w_y·CE` y que `CB ≠ CE` plana — el invariante que el test de
pesos previo no cubría y que dejó pasar el bug.

**Consecuencia para los resultados.**
- `focal` del 4463 es **válido** y se reporta (no es palanca: null-a-negativo, baja el
  recall de la minoritaria — contra H1).
- `cb` del 4463 se **descarta** (no-op, ≡ baseline CE); se **re-corre** el brazo `cb`
  con el fix (3 binarias × k=5 = 15 runs, paired vs el MISMO baseline CE en disco).
- Hiperparámetros, splits, baseline: sin cambios. La expectativa pre-registrada §2/§3
  (probable null como palanca + posible H_reg por apilar sobre `weighted_sample`) se
  mantiene tal cual — ahora sí evaluable.
