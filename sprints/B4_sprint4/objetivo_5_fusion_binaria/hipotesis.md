# Hipótesis + métrica de éxito — Objetivo 5: fusión binaria de microcalcificaciones + caracterización de varianza + comparación de arquitecturas

> **Post-reunión 26-may-2026 16:30 (Sebastián + Eduardo).** Argumento antes de
> código (regla 9 de CLAUDE.md). Este documento pre-registra **tres fases**
> con guardrails de fase: no se avanza a la siguiente sin leer los resultados
> de la anterior. Reviewer OK obligatorio antes de tocar código de training.

---

## Metadatos

- **Fecha de redacción**: 2026-05-27
- **Autor / sesión**: Claude (opus-4.7) en sesión con Ernesto Gamero
- **Branch**: `feature/sprint4-fusion-microcalc`
- **Baselines a contrastar**:
  - Job **4109** (CLAM_MB, 3 binarias, `_pth` 333 identif., 1 seed, splits_0).
  - Job **4137** (DSMIL, mismas 3 binarias, 1 seed). Veredicto previo: fracaso
    arquitectónico en **balanced_acc**; en **AUC** matizado (ver Tarea 0).
  - **Tabla de Sebastián (26-may)**: carc inv 0.79 (combined), cdis 0.69
    (`pth_balance` **con** no_id), tej no neo 0.63 (`pth_balance` sin no_id).
- **Estado**: ☑ borrador · ☐ revisada por `reviewer` · ☐ aprobada

---

## Contexto (Tarea 0, cerrado — NO editar)

Tarea 0 (read-only, esta sesión) comparó nuestro 4109 vs Sebastián en **test
AUC** (su métrica reportada), verdad de campo desde `summary.csv`:

| Tarea | CLAM 4109 | DSMIL 4137 | Sebastián | Δ (CLAM−Seb) | Dataset nuestro | Dataset Seb |
|---|---|---|---|---|---|---|
| carcinoma invasivo | 0.808 | 0.824 | 0.79 | +0.018 | _pth 333 | combined 284 |
| cdis | 0.678 | 0.570 | 0.69 | −0.012 | _pth 333 | pth_bal **+no_id** |
| tej no neoplásico | 0.658 | 0.577 | 0.63 | +0.028 | _pth 333 | pth_bal 328 |

**Tres hechos que ordenan este objetivo:**

1. **En AUC ya estamos en paridad con Sebastián** en las 3 binarias (|Δ| ≤ 0.03).
   El próximo experimento NO es defensa de un baseline que falla.
2. **Los test sets son minúsculos (n≈33).** ±1 slide mueve la AUC ~0.05.
   Las inversiones val/test (carc test 0.808 > val 0.704; tej val 0.831 ≫
   test 0.658) lo confirman. **Todos los Δ de arriba caen dentro del ruido
   de 1 seed sobre 1 sola partición.** Antes de comparar nada más hay que
   caracterizar esa varianza — y `--seed` con split fijo NO la captura
   ([main.py:514](../../../../clam_environ/main.py#L514) → seed mueve init/
   dropout/sampling, NO qué slides caen en test, que lo fija `splits_0.csv`).
   La palanca correcta es **k-fold** (varias particiones de test).
3. **Sebastián ya incluye `no_identificado` como negativo en cdis** (rango
   118-2010 **según su tabla del 26-may**; los 118 positivos coinciden exacto
   con los positivos cdis del CSV — los 2010 negativos NO se auditaron contra
   sus splits, se infieren de la tabla) **y aun así solo saca 0.69.** Tempera
   la expectativa del binario fusionado: incluir no_id no fue bala de plata
   para él.

**Regla operacional nueva de Sebastián (reunión 26-may, sobre necrosis):**
al unir varias preguntas binarias en **una sola** ("tiene / no tiene"), SÍ
incluye la clase `ausente/no_identificado` como negativo y las trata
equivalentes; cuando son **varias** binarias separadas, NO la incluye porque
"absorbería la información del modelo". **Aprobó replicar esto en
microcalcificaciones**, con la condición de **no tocar sus CSVs/splits y crear
los nuestros** (bajo `clam_testing2/`).

---

## Estructura del objetivo: 3 fases con guardrails

```
Fase 0 — Varianza / paridad     →  ¿son reales los Δ a n≈33?  (CLAM, 3 binarias, k-fold)
   │  guardrail: si std grande → TODO downstream va con k-fold
   ▼
Fase 1 — Binario fusionado      →  ¿"tiene/no tiene" + no_id como negativo es usable?  (CLAM, k-fold)
   │  guardrail: si colapsa a mayoritaria → registrar y NO seguir a arquitecturas sobre fusionado
   ▼
Fase 2 — Arquitecturas          →  CLAM vs DSMIL sobre el fusionado (régimen ya NO data-starved)
```

**Mammoth queda FUERA de este objetivo** (no hay wrapper; requiere hipótesis
propia). Se registra como horizonte por su evidencia interna (Eduardo +
3 tasks de Sebastián), no como experimento de este documento.

---

## FASE 0 — Caracterización de varianza y paridad (CLAM, 3 binarias)

### 0.1 Hipótesis

A n≈33 en test, la **varianza de partición** del `test_auc` es grande
(predicción: `std ≈ 0.04–0.07`). Si se cumple, el "empate" de Tarea 0 con
Sebastián es, en rigor, **indistinguible** — y cualquier Δ futuro (fusión,
DSMIL, mammoth) debe medirse con k-fold, no con una sola partición. El número
`splits_0` del 4109 (0.808 / 0.678 / 0.658) es **un solo draw**; debería caer
dentro de `mean ± std` del k-fold (sanity check del baseline).

### 0.2 Métrica y regla de decisión (predefinida)

- **Reportar**: `mean ± std` de `test_auc` **y** `balanced_acc` por tarea,
  sobre k folds. Además, dónde cae el draw `splits_0` (4109) en esa distribución.
- **Regla de decisión (calibra todo el objetivo):**
  - `std(test_auc) > 0.05` en alguna tarea → **varianza confirmada grande**:
    Fases 1 y 2 se evalúan **solo con k-fold mean±std**; ningún Δ de una sola
    partición cuenta como evidencia. *(Resultado esperado.)*
  - `std(test_auc) ≤ 0.03` en las 3 → varianza chica: las comparaciones de
    una sola partición son legítimas (improbable a este n, pero se deja la puerta).
  - `0.03 < std ≤ 0.05` → banda intermedia: k-fold recomendado, se documenta.
- **NO es un pass/fail de modelo** — es una caracterización del régimen de
  evaluación. No hay "éxito/fracaso", hay un número que decide la metodología
  downstream.

### 0.3 Dataset y splits

- **Tareas**: las 3 binarias **idénticas al 4109** (carcinoma_invasivo, cdis,
  tejido_no_neoplasico), `_pth` identificadas, `no_identificado` **excluido**
  (apples-to-apples con 4109).
- **Conteos verificados (CSV real, esta sesión)**: carcinoma 68 pos, cdis 118
  pos, tejido 192 pos; total identif. = 328 (no 333 — drift de Sebastián;
  registrado como dato de campo).
- **Splits NUEVOS, generados por nosotros bajo `clam_testing2/`**:
  `data/splits_kfold/microcalcificaciones_en_<tejido>_kfold/` con
  `create_splits_seq.py --k 5 --val_frac 0.1 --test_frac 0.1 --seed 1`
  (Monte-Carlo CV: 5 draws independientes del mismo régimen test_frac=0.1 →
  caracteriza exactamente la varianza del número single-split). **NO se tocan
  los splits de Sebastián.** Los label CSVs se leen **read-only** de
  `clam_environ/environ/csv/`.
- **k = 5** (no 10): con 68 positivos (carcinoma, la más rara), k=5 deja
  ~13 pos por fold de test → AUC por fold con menos ruido que k=10 (~7 pos),
  y 5 draws bastan para un `std` indicativo. Si la banda sale intermedia,
  ampliar a k=10 es la extensión natural.

### 0.4 Variables controladas

Args bendecidos idénticos al 4109: `--drop_out 0.25 --lr 2e-4 --bag_loss ce
--inst_loss svm --model_type clam_mb --embed_dim 512 --B 8 --max_epochs 30
--early_stopping --weighted_sample --auto-label-dict --log_data`. **Diferencias
vs 4109**: (a) `--k 5` y el `--split_dir` propio; (b) el universo cambió de 333
a **328 identificadas** por drift del CSV de Sebastián (deriva de su edición, no
decisión nuestra — R2). El "apples-to-apples vs 4109" es a nivel de tarea/args,
no slide-idéntico. El modelo, features y demás args no cambian.

---

## FASE 1 — Binario fusionado "tiene / no tiene microcalcificaciones" (CLAM)

### 1.1 Hipótesis (clínica + de datos)

La decisión clínica real es **jerárquica**: primero "¿hay
microcalcificaciones?", luego "¿en qué tejido?". Aplastar a 3 binarios planos
descarta el nivel 1 — y con él las ~2487 WSIs `no_identificado`, que en el
nivel "presencia/ausencia" **sí son negativos legítimos** (regla de Sebastián
para 1 sola binaria). Fusionar las 3 binarias en una sola pregunta de
presencia permite usar esas 2487 slides.

**Predicción honesta (no optimista):** el detector de presencia será
**modesto**, no un salto. Razón: (a) el precedente más cercano —cdis de
Sebastián **con** no_id— solo llegó a 0.69 AUC; (b) el negativo domina
(2487:328 ≈ 7.6:1) → riesgo de colapso a "no". `--weighted_sample` mitiga
pero no elimina. La pregunta científica no es "¿gana?" sino "¿es **usable** un
detector de presencia que aprovecha las no_id, o colapsa a la mayoritaria como
pasó en el 8-clases?".

### 1.2 Construcción del CSV (regla determinística, pre-registrada)

Desde `clam_environ/environ/csv/dataset_microcalcificaciones_label.csv`
(READ-ONLY, 2815 filas hoy):

```
label_fused = "no"  si  label == "no_identificado"      (2487 slides)
label_fused = "si"  en cualquier otro caso              (328 slides)
```

→ CSV nuevo `data/csv_fusion/dataset_microcalcificaciones_presencia_label.csv`
bajo `clam_testing2/`. Positivos 328, negativos 2487, **ratio 7.6:1** (cumple
el cap ≤10× de Sebastián sin oversampling). Un script verificador
(`scripts/verify_fusion_csv.py`, estilo `verify_binary_microcalc_csvs.py`)
confirma determinísticamente los conteos antes de cualquier split.

> **Pendiente de confirmar con Sebastián (no bloquea Fase 0):** el universo.
> El CSV 8-clases tiene 2815 filas hoy (no 3072 de la memoria). Si Sebastián
> quiere el universo `_pth` completo, se re-deriva; si el 2815 es el vigente,
> se usa ese. La construcción del label es idéntica en ambos casos.

### 1.3 Métrica de éxito (predefinida)

- **Decisiva**: `balanced_acc` (test), `mean ± std` sobre **k=3 folds** + matriz
  de confusión agregada. AUC se reporta pero no decide (régimen desbalanceado).
  **k=3 (no 5) por régimen de datos**: la fusionada tiene ~33 positivos en test
  (vs 7 en las binarias) → varianza de partición baja → 3 draws bastan para
  barras de error estables. Las binarias (Fase 0) sí van a k=5 porque con 7
  positivos la AUC por fold oscila fuerte. Decisión de presupuesto + cortesía
  GPU única (chain ~15h vs ~24h con k=5), confirmada con Ernesto 27-may.
- **Umbrales** (sobre `mean` k-fold):
  - **Usable** = balanced_acc ≥ 0.65 (umbral clínico) → detector de presencia
    aprovecha las no_id sin colapsar.
  - **Plateau** = 0.55 ≤ balanced_acc < 0.65 → aprende algo pero el desbalance
    pesa; documentar y comparar contra el precedente cdis-con-no_id (0.69 AUC).
  - **Colapso a mayoritaria** = balanced_acc < 0.55 **o** recall_positivo < 0.20
    → el modelo predice "no" casi siempre. **Riesgo pre-registrado** (ya pasó
    en 8-clases). Se registra como resultado válido (refuta la utilidad del
    fusionado plano) y se NO avanza a Fase 2 sobre el fusionado.
- **Comparación de formulación** (reportar, no decide): balanced_acc del
  fusionado vs el promedio de las 3 binarias separadas (Fase 0) — ¿la fusión
  gana, empata o pierde frente a mantenerlas separadas?

### 1.4 Variables controladas

Args bendecidos idénticos a Fase 0. **Únicas diferencias**: `--task` apunta a
la tarea fusionada nueva (registrada como config local, no en el `main.py` de
Sebastián — vía CSV propio + `--auto-label-dict`), y `--split_dir` propio
(k=3, generado con `scripts/build_fusion_splits.py`, misma lógica que Fase 0).
Modelo CLAM_MB, CONCH 512, B=8, 30 epochs. Harness: `scripts/train_dsmil.py
--model_type clam` (mismo train/val/test que DSMIL → apples-to-apples con Fase 2).

---

## FASE 2 — Comparación de arquitecturas sobre el fusionado (CLAM vs DSMIL)

### 2.1 Hipótesis

El cierre previo de DSMIL ("fracaso arquitectónico", job 4137) se diagnosticó
como **Caso A: cuello = datos** (264 train slides en las binarias). **El
fusionado rompe ese cuello**: ~2815 slides, ~262 positivos en train (k-fold),
~1990 negativos → DSMIL **ya no está data-starved**. La comparación
arquitectónica recién acá es **justa**. El aggregator dual-stream de DSMIL
(parche crítico + atención relacional) podría capturar mejor la señal focal de
una microcalcificación (punto pequeño) que la atención gated absoluta de CLAM
— exactamente el argumento de contexto/focalidad que Sebastián levantó en la
reunión.

> Esto **reabre** el veredicto DSMIL **solo para el régimen fusionado**, con
> justificación explícita (más datos), NO retuneando sobre las binarias (eso
> sigue cerrado). El wrapper DSMIL (`models_dsmil/`, jobs 4135/4137) se reusa
> **intacto** — cambiarlo rompería comparabilidad.

### 2.2 Métrica de éxito (predefinida)

- Mismo k=3 que CLAM en Fase 1 (mismos splits fusionados). Δ = DSMIL − CLAM
  sobre el fusionado, en `balanced_acc` (decisiva) y `test_auc` (reporte).
- **Éxito arquitectónico** = DSMIL Δ balanced_acc ≥ +0.03 (mean k-fold) sobre
  CLAM **Y** sin solaparse las bandas `mean ± std`. → el dual-stream aporta en
  el régimen con datos.
- **Plateau** = |Δ| < 0.03 o bandas solapadas → la arquitectura no es la
  palanca ni con datos; cierra DSMIL también para el fusionado.
- **Regresión** = Δ ≤ −0.05 → DSMIL peor; documentar y cerrar.

### 2.3 Variables controladas

CLAM (Fase 1) vs DSMIL: **única variable = el aggregator**. Mismo CSV
fusionado, mismos k=3 splits, mismos args bendecidos + el `w_max=0.1` de DSMIL
ya validado (R1 del objetivo 3). Features CONCH 512, B=8, 30 epochs.

---

## Riesgos transversales

- **R1 — Colapso a la mayoritaria en el fusionado** (Fase 1): negativo domina
  7.6:1. Pre-registrado como resultado posible y válido (§1.3). `--weighted_sample`
  ya en args. Evidencia previa de colapso en 8-clases.
- **R2 — Drift del CSV de Sebastián**: 2815 filas hoy vs 3072 en memoria.
  Verdad de campo = el CSV físico al momento de construir (snapshot al workspace
  del sprint, `@csv-audit`). Re-verificar conteos antes de cada fase.
- **R3 — `early_stopping` inerte** (`stop_epoch=50 > max_epochs=30`, heredado
  de CLAM, `core_utils.py:79`): los 30 epochs corren completos; el test se
  evalúa sobre el best checkpoint por val_loss. Heredado del baseline → se
  mantiene para apples-to-apples (igual que objetivo 3).
- **R4 — Monte-Carlo CV ≠ k-fold disjunto**: `create_splits_seq.py --k 5` hace
  5 draws independientes (test sets pueden solaparse), no folds disjuntos. Es
  **lo correcto** para caracterizar la varianza del estimador a test_frac=0.1
  (mismo régimen que el single split que queremos calibrar). Se documenta
  explícitamente para no confundir con k-fold canónico.
- **R5 — Preflight obligatorio** (workaround G): cada `.slurm` corre
  `scripts/preflight_minpatch.py` (o análogo) ANTES del `python main.py`,
  validando nº mínimo de parches por slide de train y existencia de `.pt`.

---

## Plan de validación pre-entrenamiento (smoke tests)

1. **Verificador de splits/CSV (CPU)**: conteos por clase de cada fold suman al
   total esperado; ningún slide_id sin `.pt` en `features/pt_files/`; positivos/
   negativos por fold dentro de lo esperado.
2. **Smoke CLAM fusionado (GPU, 1 epoch, 1 fold)**: `train_loss` decrece, no NaN.
3. **Smoke DSMIL fusionado (GPU, 1 epoch)**: reusar el smoke ya validado (4135),
   solo cambia la task → confirmar que el wrapper carga el CSV fusionado.
4. **Preflight enchufado** al `.slurm` antes del `python`.

| Smoke | Estado |
|---|---|
| 1. Verificador CSV/splits | ☐ |
| 2. CLAM fusionado 1 epoch | ☐ |
| 3. DSMIL fusionado 1 epoch | ☐ |
| 4. Preflight en `.slurm` | ☐ |

---

## Autorización de Sebastián (reunión 26-may-2026 16:30)

Según el reporte de Ernesto de la reunión, Sebastián **aprobó** la fusión de
las 3 binarias en **una sola pregunta "tiene/no tiene"** incluyendo
`no_identificado` como negativo (extensión a microcalcificaciones de su regla
de necrosis). Condición: **no tocar sus CSVs/splits, crear los nuestros** bajo
`clam_testing2/`. **Esto autoriza Fase 1.**

Alcance preciso de lo aprobado: el **binario fusionado plano** (nivel 1 de la
jerarquía: presencia/ausencia). **NO** se construye el nivel 2 condicionado
(los 3 binarios condicionados a presencia=SI) — esa parte de la propuesta
jerárquica original queda fuera de este objetivo. Aquí solo: 3 binarias
separadas (Fase 0, ya existen) + 1 fusionado plano (Fase 1, nuevo).

---

## Acuerdo de cierre (firmar antes de tocar código de training)

- ☑ Las secciones de hipótesis y métrica de las 3 fases están completas.
- ☑ Los umbrales se fijaron **antes** de ver cualquier número nuevo.
- ☑ El agente `reviewer` revisó este archivo y dio OK (2026-05-27, veredicto:
  **APROBADO CON OBSERVACIONES**, ninguna bloqueante; observaciones 1-3
  incorporadas al doc, observación 4 = recordatorio operativo de casillas).
- ☐ Este archivo está commiteado en `feature/sprint4-fusion-microcalc` ANTES
  de generar splits/CSV propios o de cualquier `.slurm`.

> Si alguna casilla está vacía al tocar código de training, `reviewer` bloquea
> el commit (regla 9 de CLAUDE.md).
