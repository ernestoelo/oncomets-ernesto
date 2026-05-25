# Resultados — Objetivo 3 / DSMIL sobre 3 binarios de microcalcificaciones

> **Estado: FRACASO ARQUITECTÓNICO según `hipotesis.md` §2.**
> Veredicto cerrado, no reabrir umbrales post-hoc.

## TL;DR

DSMIL_CLAM_MB sobre las 3 tareas binarias (job SLURM **4137**, 49:32
wall, exit 0, `.err` 0 B) **degrada `balanced_acc` vs baseline CLAM_MB
(job 4109) en las 3 tareas**, superando el guardrail anti-regresión en
carcinoma (Δ = −0.10 vs umbral Δ ≥ −0.05). El best checkpoint queda en
**epoch 0–3** en las 3 tareas: el modelo overfittea antes de poder
ejercer su ventaja arquitectónica. El baseline 4109 muestra el **mismo
patrón en 2 de 3 tareas** (best ep 1 en carcinoma, ep 4 en cdis) → el
cuello de botella primario es **datos, no arquitectura** (Caso A,
predominante).

## Setup

Mismo dataset que job 4109 (333 slides identificadas,
`no_identificado` excluido) sobre los splits canónicos
`microcalcificaciones_en_<tejido>_pth_100/splits_0.csv`. Mismos args
bendecidos, 30 epochs, seed 1, `--early_stopping`. **Única variable**:
aggregator (CLAM `Attn_Net_Gated` → DSMIL dual-stream con instance
scorer + atención relacional). Único hiperparámetro nuevo:
`w_max = 0.1` sobre `L_max` para que el instance scorer reciba
gradiente (decisión R1 = B.1.3 de `hipotesis.md` §5). EarlyStopping
heredado de CLAM con `stop_epoch=50` → nunca triggea con
`max_epochs=30`, pero `save_checkpoint` SÍ guarda el best por val_loss
y el test final se evalúa sobre ESE checkpoint cargado explícitamente
(R6 de `hipotesis.md` §5).

## Métricas comparativas

### Balanced accuracy (test) — métrica decisiva de §2

| Tarea | bal_acc DSMIL | bal_acc 4109 | Δ | Umbral §2 | ¿Pasa? |
|---|---|---|---|---|---|
| carcinoma_invasivo | **0.6758** | 0.78 | **−0.104** | Δ ≥ −0.05 (guardrail) | ❌ **FALLA guardrail** |
| cdis | 0.5455 | 0.59 | **−0.045** | Δ ≥ +0.05 | ❌ no cumple (negativo) |
| tejido_no_neoplasico | 0.5019 | 0.58 | **−0.078** | Δ ≥ +0.05 | ❌ no cumple (negativo) |

### AUC y accuracy

| Tarea | test_auc DSMIL | test_auc 4109 | Δ | test_acc DSMIL | val_auc DSMIL | val_acc DSMIL |
|---|---|---|---|---|---|---|
| carcinoma | 0.824 | 0.81 | **+0.014** | 0.818 | 0.658 | 0.800 |
| cdis | 0.570 | 0.68 | −0.110 | 0.636 | 0.762 | 0.758 |
| tejido | 0.577 | 0.66 | −0.083 | 0.576 | 0.632 | 0.548 |

Detalle de carcinoma: `test_auc` sube +0.014 pero `balanced_acc` cae
10 pp. La degradación está en el **threshold de decisión /
calibración**, no en el ranking de probabilidades. La métrica decisiva
de §2 es `balanced_acc`, no AUC, **el veredicto no cambia**.

### Matrices de confusión (rows = true, cols = pred)

| Tarea | n_test | TN | FP | FN | TP | recall+ | precision+ |
|---|---|---|---|---|---|---|---|
| carcinoma | 33 | 24 | 2 | 4 | 3 | 3/7 = 0.43 | 3/5 = 0.60 |
| cdis | 33 | 18 | 4 | 8 | 3 | 3/11 = 0.27 | 3/7 = 0.43 |
| tejido | 33 | 2 | 11 | 3 | 17 | 17/20 = 0.85 | 17/28 = 0.61 |

Carcinoma se acerca al "todo NO" (sesgo a la mayoritaria, 5 positivos
predichos de 33). Tejido invierte el sesgo (28 positivos predichos de
33) — coherente con que la clase positiva es mayoría (20/33).

## Diagnóstico del sobreajuste temprano

### Curvas train_loss vs val_loss (ep0 → ep29)

| Tarea | train ep0 → ep29 | val ep0 → ep29 | Brecha al ep29 |
|---|---|---|---|
| carcinoma (DSMIL) | 0.654 → 0.054 | 0.488 → 1.666 | **+1.612** |
| carcinoma (4109) | 0.591 → 0.049 | 0.874 → 1.593 | +1.544 |
| cdis (DSMIL) | 0.714 → 0.143 | 0.611 → 0.896 | +0.753 |
| cdis (4109) | 0.708 → 0.081 | 0.641 → 1.821 | +1.740 |
| tejido (DSMIL) | 0.714 → 0.191 | 0.699 → 1.016 | +0.825 |
| tejido (4109) | 0.695 → 0.077 | 0.686 → 0.902 | +0.825 |

`train_loss` decrece monótonamente en las 6 corridas (sanity de
optimización OK). `val_loss` **diverge** después del best epoch en
todas — sobreajuste severo en ambos modelos.

### Best epoch — el corazón del diagnóstico

| Tarea | Best ep DSMIL (job 4137) | Best ep CLAM_MB (job 4109) | Lectura |
|---|---|---|---|
| carcinoma | **0** | **1** | **Caso A**: ambos overfittean inmediatamente |
| cdis | **3** | **4** | **Caso A**: ambos overfittean muy temprano |
| tejido | **1** | **22** | Matiz **Caso B**: CLAM_MB explotó 22 epochs, DSMIL solo 1 |

**Lectura combinada**: en 2 de 3 tareas (carcinoma, cdis) el baseline
también overfittea en epoch 0–4 → el patrón **no es exclusivo de
DSMIL**, el cuello de botella primario es **DATOS** (264 train slides
no bancan ningún aggregator más expresivo que un linear). En tejido
hay un matiz: CLAM_MB sí aprovechó 22 epochs antes de saturarse,
mientras DSMIL se quedó en ep 1 — sugiere que la capacidad extra del
q-net + W_0 acelera el overfit específicamente cuando el patrón es más
difuso (tejido vs focal-de-carcinoma).

### Sanity del aggregator: ¿entrenó?

| Tarea | W0 norm init → final (ep29) | q0 norm init → final |
|---|---|---|
| carcinoma | 0.825 → **1.643** (+99%) | 6.506 → 7.300 (+12%) |
| cdis | 0.825 → **1.386** (+68%) | 6.506 → 7.111 (+9%) |
| tejido | 0.825 → **1.302** (+58%) | 6.506 → 6.890 (+6%) |

W0 dobló su norma en carcinoma → el aggregator **sí entrenó**. El
problema **no es** gradiente muerto ni desconexión de L_max. Es
**generalización**: el optimizador encuentra una configuración que
ajusta los 264 train pero no transfiere a val/test.

## Análisis

### El veredicto formal está cerrado

Carcinoma cae a Δ = −0.104, **supera el guardrail anti-regresión en
2×** (Δ ≥ −0.05 era el límite). Para el criterio combinado de §2 esto
es exactamente la cláusula de **fracaso arquitectónico** (carcinoma
degrada Δ < −0.05). No movemos el umbral post-hoc.

### Pero la causa más probable es Caso A, no Caso B puro

Si el problema fuera **DSMIL intrínsecamente peor que CLAM_MB**
(Caso B), uno esperaría que CLAM_MB sí aprovechara epochs adicionales
mientras DSMIL no. **Eso solo pasa en tejido** (ep 22 vs ep 1) y aun
ahí el resultado final de CLAM_MB en bal_acc (0.58) está apenas sobre
el piso 0.50 — el "extra" que CLAM_MB exprime con sus epochs no es
grande. En carcinoma y cdis, **ambos modelos overfittean en epochs
1–4** → el cuello de botella es shared, no atribuible al aggregator.

Lectura conjunta:
- **Carcinoma y cdis = Caso A** (datos). Ningún aggregator más
  expresivo que un linear puede ayudar acá; **DSMIL no aportó porque
  no podía aportar en este régimen**.
- **Tejido = Caso A con sabor a Caso B**. CLAM_MB consigue marginal
  más de capacidad útil; DSMIL la pierde por sobreajustar antes. El
  diagnóstico de "capacidad extra es lujo que el dataset no banca" se
  sostiene **solo** en tejido, y aun ahí el techo final es bajo.

**El diagnóstico Caso A no exonera a DSMIL.** El veredicto formal de
§2 (fracaso arquitectónico) se sostiene literalmente — DSMIL no
cumplió los umbrales pre-registrados. El análisis Caso A vs Caso B
explica el *por qué* (el régimen de datos no le da margen), no cambia
el *qué* (degradó balanced_acc en las 3 tareas). Si se quisiera
"rescatar" a DSMIL habría que cambiar de tarea, no relajar el umbral.

### El AUC vs balanced_acc en carcinoma

`test_auc` sube +0.014 mientras `balanced_acc` cae 10 pp. El ranking
de probabilidades por slide es marginalmente mejor en DSMIL, pero el
threshold óptimo de decisión se mueve — el modelo asigna más slides a
"NO" (5 positivos predichos vs un baseline plausible más balanceado).
Esto sería relevante si pudiéramos calibrar el threshold a posteriori,
pero **la métrica decisiva de §2 es `balanced_acc` con threshold
fijo** — no reabrimos esa discusión.

## Implicaciones para los próximos sprints

1. **DSMIL queda descartado para microcalcificaciones en el régimen
   actual (333 slides)**. NO se prueba con más hiperparámetros (más
   dropout, menos epochs, smaller q-net, etc.) — sería p-hacking
   sobre un experimento cerrado con umbrales pre-registrados.
2. **El próximo paso del Objetivo 3 NO es otra arquitectura todavía**.
   Va `balanced_pth_100` cuando Sebastián lo finalice (CLAUDE.md
   Hallazgo 10). Si la causa real es **DATOS** (Caso A predominante),
   ese experimento lo va a revelar primero — **con CLAM_MB, no con
   DSMIL**. La arquitectura volverá a la mesa solo si los datos
   adicionales no alcanzan. Bifurcación condicional:
   - **Si CLAM_MB sobre `balanced_pth_100` sube `balanced_acc`
     significativamente** (Δ ≥ +0.05 en al menos 2 de 3 tareas) →
     Caso A confirmado, datos era el cuello. DSMIL queda enterrado
     definitivamente para esta tarea.
   - **Si CLAM_MB sobre `balanced_pth_100` NO mejora** o mejora
     marginal (Δ < +0.03) → el cuello deja de ser solo datos y
     reabre la pregunta arquitectónica. Alternativas (TransMIL, HMIL)
     vuelven a la mesa como candidatas reales, no como deuda
     diferida.
3. **Alternativas arquitectónicas** (TransMIL, HMIL) quedan en
   `alternativas_consideradas.md` para un sprint futuro, **no el
   siguiente**. Primero arreglar datos.
4. La traza completa del experimento (job 4137,
   `results/sprint4_obj3_dsmil_full/`, logs en `logs/`) queda como
   evidencia auditable del veredicto.

## Caveats

- **1 seed (PRELIMINAR)**, igual que el baseline 4109. El veredicto es
  estable porque la magnitud de Δ es grande:
  - carcinoma Δ = −0.104 (2× el guardrail).
  - cdis Δ = −0.045 (negativo, fuera de banda ambigua estricta < 0.03).
  - tejido Δ = −0.078 (idem).
  La regla "ampliar a 3 seeds si |Δ| < 0.03" de `hipotesis.md` §4 **no
  se dispara** — la consistencia entre las 3 tareas independientes
  (3/3 negativas) hace muy improbable que la varianza entre seeds
  invierta el veredicto.
- **val set chico** (33–35 slides por tarea). El "best ep 0" podría
  estar inflado por suerte en una muestra chica. Pero la consistencia
  entre las 3 tareas independientes (todas overfittean temprano) hace
  poco probable que sea ruido puro.
- **CONCH features ya son foundation-model semánticas**. El instance
  scorer lineal W_0 de DSMIL opera sobre el "caso fácil" (R2 ya
  mitigado por la norma uniforme 22.65 ± 0.01 medida en investigación
  §A.1). El problema no es el espacio de features.
- **Init reproducible en ambos jobs**. Tanto 4109 (CLAM_MB) como 4137
  (DSMIL) fijan `torch.manual_seed(1)` antes de construir el modelo
  → la randomness de la inicialización **no es una variable
  confounder** entre los dos experimentos; solo el aggregator (y los
  parámetros que introduce, q-net + W_0) difiere. Los aggregator son
  arquitectónicamente distintos (no son "init idéntica" en sentido
  literal), pero **el mismo seed garantiza que la diferencia observada
  no es ruido de inicialización**.

## Lo que NO se hizo y por qué

- **NO se retuneó DSMIL para mitigar overfit** (dropout más alto,
  weight_decay mayor, q-net más chico, fewer epochs). Sería p-hacking
  sobre un experimento con umbrales pre-registrados.
- **NO se corrió con 3 seeds**. La magnitud de Δ excede ampliamente
  la varianza esperada entre seeds (>0.045 vs banda ambigua <0.03).
- **NO se cambió el régimen de stop / patience / dropout**. La regla
  "una variable a la vez" del §4 lo prohíbe — cambiar dos cosas a la
  vez deja la comparación sin sentido.
- **NO se mergeó a `main`**. La rama
  `feature/sprint4-obj3-dsmil-implementacion` sigue activa.
- **NO se reabrió `propuesta_dsmil.md`** ni se descartaron DSMIL en
  general (solo para microcalcificaciones en este régimen de datos).
  Podría volver a la mesa en una tarea distinta o con
  `balanced_pth_100`.

## Job SLURM 4137 — artefactos auditables

- Wall time: **49:32** (22:34:56 → 23:24:28, 24-may-2026).
- Exit code: **0**. `.err`: **0 bytes**, sin warnings.
- Preflight: PASS para las 3 tasks (264/264 train con N ≥ B=8).
- Cold start del .out: GPU NVIDIA RTX A6000, CUDA 12.8, torch 2.x.
- Artefactos por tarea en
  `results/sprint4_obj3_dsmil_full/dsmil_full_<tejido>_B8_s1/`:
  - `s_0_checkpoint.pt` (best por val_loss, ep 0/3/1)
  - `summary.csv` (folds, test_auc, val_auc, test_acc, val_acc)
  - `split_0_results.pkl` (predicciones por slide)
  - `test_metrics.json` (auc, acc, balanced_acc, confusion 2x2)
  - `test_predictions.csv` (slide_id, y_true, y_prob_si, y_pred)
  - `metrics.jsonl` (train + val por epoch)
  - `init_snapshot.json` / `final_snapshot.json` (pesos del aggregator)
- Log unificado del .slurm: `logs/eg_dsmil_full_4137.out` (26 KB).

## Procedencia de los números del baseline 4109

- Best epoch y curvas train/val extraídas de `logs/mc_3binarios_4109.out`.
- `balanced_acc` del baseline tomada de la tabla de
  `sprints/B4_sprint4/reformulacion_multilabel/resultados.md` (no se
  recomputó; se asume confiable).
- Mismo seed (1), mismo fold (0), mismos splits, misma cohorte de
  333 slides — apples-to-apples por construcción.
