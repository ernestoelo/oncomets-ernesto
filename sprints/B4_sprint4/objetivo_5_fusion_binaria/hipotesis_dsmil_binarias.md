# Hipótesis + métrica de éxito — Anexo Objetivo 5: DSMIL × 3 binarias × MC-CV k=5

> **Anexo simétrico del Objetivo 5** (regla 9 de CLAUDE.md, "argumento antes
> de código"). Cierra el cuadro CLAM-vs-DSMIL en TODOS los regímenes:
> binarias (este doc) + fusionado (ya hecho, `hipotesis.md` §2.2 = banda
> ambigua). Reviewer OK obligatorio antes de tocar código de training.

---

## Metadatos

- **Fecha de redacción**: 2026-05-28
- **Autor / sesión**: Claude (opus-4.7) en sesión con Ernesto Gamero
- **Branch**: `feature/sprint4-dsmil-binarias-varianza`
- **Baseline pareado**: **Fase 0** del Obj 5 (CLAM_MB × 3 binarias × MC-CV
  k=5, job **4170**, splits bajo `data/splits_kfold/microcalcificaciones_en_
  <tejido>_pth_100/`). Resultados ya publicados en `resultados.md` §Fase 0:
  | Tarea | CLAM bal_acc (k=5) | CLAM test_auc (k=5) |
  |---|---|---|
  | carcinoma invasivo | 0.639 ± 0.077 | 0.732 ± 0.167 |
  | cdis | 0.595 ± 0.077 | 0.652 ± 0.072 |
  | tejido no neoplásico | 0.577 ± 0.030 | 0.646 ± 0.025 |
- **Referencia previa single-split**: Job **4137** (DSMIL × mismas 3
  binarias × 1 seed, fracaso bal_acc en cdis/tejido, AUC competitivo en
  carcinoma 0.824). Esa lectura fue de **1 sorteo** y entra como dato de
  contexto, NO como baseline (Hallazgo 1 Fase 0 ya nos enseñó por qué).
- **Estado**: ☑ borrador · ☐ revisada por `reviewer` · ☐ aprobada

---

## Motivación (por qué este anexo ahora)

`hipotesis.md` original **cerró el régimen DSMIL en binarias** apoyándose
en el job 4137 (1 sorteo) — diagnóstico "fracaso arquitectónico, Caso A:
cuello = datos (264 train)". Cuando aplicamos MC-CV a CLAM (Fase 0)
descubrimos que **el single-split engaña fuerte a n≈33** (Hallazgo 1:
carcinoma "0.808" era 0.732 ± 0.167). **El "fracaso" del 4137 no puede
sostenerse sin MC-CV** — podría ser ruido del sorteo, como pasó con CLAM.

Este anexo aplica la **misma vara de Fase 0 a DSMIL** para tener
comparación pareada honesta (mismos splits, mismas k=5 repeticiones, mismos
args bendecidos hasta donde DSMIL los soporta). Cierra simétricamente el
cuadro: si la lectura "el cuello es datos, no arquitectura" (Hallazgo 4
Fase 0) se sostiene, DSMIL × binarias deberá quedar **estadísticamente
indistinguible** de CLAM × binarias. Si no, hay señal arquitectónica que
ningún experimento previo pudo ver.

---

## Hipótesis primaria — NULL arquitectónico (predicción honesta)

**A n≈328 slides / ~7-20 positivos en test, DSMIL × binarias dará
balanced_acc media ± std esencialmente igual a CLAM × binarias (Fase 0)
con bandas mean±std solapadas en las 3 tareas.**

Razones:

1. **Cuello = datos, no arquitectura** (Hallazgo 4 Fase 0): las 3 binarias
   quedan en bal_acc 0.58–0.64 — modestas, apenas sobre piso 0.50. La
   arquitectura sola no rompe ese techo cuando los positivos son 7-20 por
   fold.
2. **Precedente del fusionado** (Fase 2, `hipotesis.md` §2.2 cerrada): con
   ~33 positivos por fold (≈5× más que las binarias), DSMIL apenas mejoró
   bal_acc +0.040 ± 0.038 sobre CLAM, sin separar bandas, y peor AUC. Si
   en régimen MENOS data-starved el aporte ya es marginal y ambiguo, en
   régimen MÁS data-starved (binarias) es razonable esperar Δ ≈ 0 con
   ruido grande.
3. **DSMIL es más sensible al desbalance que CLAM** (visto en Fase 2:
   recall+ 0.49 vs 0.36, menos conservador). En binarias con 68 positivos
   totales (carcinoma, la más rara), la atención dual puede sobre-pesar
   ruido en los ~7 positivos de test → varianza por fold tan grande o
   mayor que CLAM, no necesariamente media mejor.

## Hipótesis alternativa — Señal arquitectónica (sorpresa interpretable)

**Si DSMIL > CLAM por Δ pareado > +0.05 mean Y bandas mean±std no
solapadas en ≥1 binaria específica**, entonces el aggregator dual-stream
de DSMIL sí aporta señal en régimen n chico de microcalcificaciones —
hallazgo que motivaría reabrir DSMIL como arquitectura candidata para el
fusionado **con más datos** (re-extraer CONCH a mayor magnificación, otra
cohorte, etc.). Esta alternativa **no se espera**, pero el experimento
está diseñado para detectarla si existe.

## Hipótesis de regresión — DSMIL peor (confirmación del 4137 con barras)

**Si DSMIL < CLAM por Δ pareado ≤ −0.05 mean en ≥1 binaria**, el "fracaso
arquitectónico" del 4137 queda **confirmado con barras de error** — no era
ruido del sorteo. Cierra DSMIL para binarias definitivamente, esta vez
con evidencia honesta.

---

## Dataset y splits (apples-to-apples con Fase 0, MISMOS splits)

- **Tareas**: las 3 binarias `_pth` identificadas, `no_identificado`
  **excluido**. Mismos CSVs **READ-ONLY** que Fase 0:
  - `clam_environ/environ/csv/dataset_microcalcificaciones_en_carcinoma_invasivo_label.csv` (68 pos / 260 neg)
  - `clam_environ/environ/csv/dataset_microcalcificaciones_en_cdis_label.csv` (118 pos / 210 neg)
  - `clam_environ/environ/csv/dataset_microcalcificaciones_en_tejido_no_neoplasico_label.csv` (192 pos / 136 neg)
  - Total 328 identificadas por tarea (verificado determinísticamente esta
    sesión: `wc -l` y `cut -f3 | sort | uniq -c`).
- **Splits**: **REUTILIZA EXACTAMENTE los mismos** de Fase 0 — directorios
  `data/splits_kfold/microcalcificaciones_en_<tejido>_pth_100/` (creados
  por `scripts/build_fusion_splits.py` con seed 1, `--k 5`, `val_frac=
  test_frac=0.1`). Esto es **crítico**: la comparación CLAM-Fase0 vs
  DSMIL-este-doc queda **pareada por construcción** (Δ por fold bien
  definido, sin confound de partición). NO se generan splits nuevos.

## Variables controladas

Args idénticos a Fase 2 (`hipotesis.md` §2.1) hasta donde DSMIL los expone
vía `scripts/train_dsmil.py --model_type dsmil` (default, byte-idéntico al
harness validado en jobs 4135/4137 y reusado en Fase 2):

```
--B 8 --bag_weight 0.7 --w_max 0.1 --lr 2e-4 --reg 1e-5
--drop_out 0.25 --embed_dim 512 --max_epochs 30 --early_stopping
--patience 20 --stop_epoch 50 --seed 1
--label_dict '{"no": 0, "si": 1}'
```

**Diferencias controladas vs Fase 0** (las únicas, todas justificadas):
1. **Modelo**: DSMIL en vez de CLAM_MB (es el punto del experimento).
2. **Harness**: `scripts/train_dsmil.py` en vez de `main.py` (DSMIL no
   está en el `main.py` de Sebastián; el wrapper es nuestro, intacto desde
   Fase 2).
3. **`--max_epochs 30`** (no 200): mismo presupuesto que Fase 0/1/2 +
   `--early_stopping`. Documentado.
4. **`w_max 0.1`** (hiperparámetro único de DSMIL, R1=B.1.3 del paper):
   fijo, idéntico a Fase 2 — no se retunea (rompería comparabilidad).
5. **CSV por task**: `--csv_path` apunta al CSV binario read-only de
   `clam_environ/environ/csv/dataset_microcalcificaciones_en_<tejido>_label.csv`
   (mismo que Fase 0 leyó vía `main.py --task` + `--auto-label-dict`).

**NO cambia**: features (CONCH 512), splits (los mismos de Fase 0), seed
(1), B (8). El régimen de evaluación es **idéntico bit-a-bit** al de
Fase 0; lo único distinto es el modelo.

---

## Métrica de éxito (predefinida — regla de decisión)

### Métrica decisiva
`balanced_acc` (test), `mean ± std` sobre **k=5 folds** + matriz de
confusión agregada por tarea, idéntico al pipeline de Fase 0. AUC se
reporta pero no decide (régimen desbalanceado a n chico — vimos en Fase 0
que es ruidoso, std hasta ±0.167).

### Comparación pareada (CLAM Fase 0 vs DSMIL este doc)
Por tarea y por fold (mismos splits), calcular **Δ = DSMIL − CLAM**
en `balanced_acc` y `test_auc`. Reportar:
- **Δ mean ± std** sobre los 5 folds (pareado).
- Signo del Δ en cada fold (consistencia).
- Bandas `mean ± std` de cada modelo (¿se solapan?).

### Umbrales pre-registrados (regla de decisión, escritos antes del sbatch)

| Resultado | Criterio (sobre las 3 binarias) | Lectura |
|---|---|---|
| **NULL arquitectónico** (esperado) | `|Δ pareado mean| < 0.03` Y bandas mean±std solapadas en las 3 tareas | Confirma Hallazgo 4 Fase 0 (cuello = datos). Cierra simétricamente DSMIL × binarias. |
| **Señal arquitectónica** (sorpresa) | `Δ pareado mean > +0.05` Y bandas mean±std NO solapadas en ≥1 binaria | DSMIL aporta en régimen n chico para esa tarea. Justifica reabrir DSMIL como candidato del fusionado con más datos. |
| **Regresión** (confirmación 4137) | `Δ pareado mean ≤ −0.05` en ≥1 binaria | DSMIL es peor que CLAM con barras. Cierra DSMIL para binarias definitivamente. |
| **Ambiguo** | nada de lo anterior cumple limpio | Documentar Δ por fold con cautela; no sobre-interpretar (mismo guardrail estadístico §2.2). |

### Adenda estadística (heredada de `hipotesis.md` §2.2)

- MC-CV con test que se solapan → AUC/bal_acc por fold **correlacionados**
  → std levemente optimista; "bandas no solapadas" es heurístico de
  screening, NO test de significancia formal.
- Con k=5 + comparación pareada (mismos splits, mismo seed) → el Δ por
  fold cancela parcialmente la correlación. La paired-comparison es más
  estadísticamente sólida que comparar means independientes.
- Reportar con esa cautela. Si pasa el umbral pero por <2σ, banda ambigua.

### NO es pass/fail de proyecto
Es caracterización honesta del régimen arquitectónico en binarias —
cualquier resultado es informativo. El experimento está diseñado para que
**los 3 escenarios sean publicables** sin p-hacking.

---

## Lo que NO se hace (anti-scope)

- **NO se retunea DSMIL** sobre las binarias. Mismo `w_max 0.1`, mismo
  `B 8`, mismo `bag_weight 0.7` que jobs 4135/4137/Fase 2. Retunear
  rompería la pregunta arquitectónica pura.
- **NO se generan splits nuevos** — se reusan los de Fase 0. Generar
  nuevos haría no-pareada la comparación y mataría el valor del
  experimento.
- **NO se incluyen `no_identificado`** — mismo tratamiento que Fase 0
  (apples-to-apples). El régimen "con no_id" es el fusionado, ya cubierto
  por Fase 1/2.
- **NO se tocan los CSVs ni splits de Sebastián** (`clam_environ/` es
  read-only).
- **NO se reabre la pregunta del fusionado** ni los veredictos previos —
  este anexo cierra binarias, no toca lo cerrado.

---

## Riesgos pre-registrados

| Riesgo | Mitigación |
|---|---|
| Crash tardío por slide con `n_patches < B` (bug 4096) | Preflight obligatorio por fold (workaround G, mismo `preflight_minpatch.py` que Fase 0/1/2). |
| DSMIL diverge en alguna fold (loss NaN, gradientes explotan) | Logs `|grad W_0|` / `|grad q|` ya instrumentados en `train_dsmil.py`; `--early_stopping` + `--patience 20`; el fold se marca degenerado en post-hoc, no contamina los demás. |
| Tiempo de cómputo > presupuesto (>10h) | `--time 12:00:00` margen. 3 tareas × 5 folds × ~30 min (DSMIL más lento que CLAM por la segunda corriente) ≈ 7-8h estimado. Si pasa de 10h, scancel + investigar antes de re-lanzar. |
| `summary.csv` no se escribe por crash de un fold | Cada fold escribe su `test_metrics.json` + `split_<f>_results.pkl` por separado (mismo patrón Fase 2). Post-hoc agrega los que existan; folds faltantes se registran como missing en la tabla final. |

---

## Cómo se publica el resultado

Cuando termine el job:

1. **Tabla por fold y tarea** (5 folds × 3 tareas) en
   `resultados.md` §"Anexo — DSMIL × binarias × k=5", con
   `test_auc`, `balanced_acc`, `confusion`, `recall+`, `recall-` por fold.
2. **Tabla pareada CLAM vs DSMIL por tarea**: `Δ pareado mean ± std` en
   bal_acc y AUC; signo del Δ por fold; bandas mean±std de cada modelo.
3. **Veredicto explícito**: cuál de las 4 filas de la tabla de umbrales
   se aplica, citando la regla del doc.
4. **Slide 12** (nueva) en `presentacion_contenido_completo.md`: cierra
   simétricamente el cuadro arquitectónico — "DSMIL en TODOS los regímenes
   evaluado; veredicto final = cuello es datos / contexto / desbalance, no
   arquitectura sola".
5. **Actualizar `ejes_futuros_microcalc.md`**: mover "DSMIL × binarias ×
   k=5" de "opcional descartado" a "ejecutado, ver `hipotesis_dsmil_
   binarias.md` + `resultados.md` §Anexo".

---

## Reviewer (regla 9, obligatorio)

Antes de commitear este doc y el `.slurm`, invocar `@reviewer` sobre:
- Este archivo (hipótesis primaria + alternativa + regresión + métrica +
  umbrales pre-registrados — todos los componentes que regla 9 exige).
- `scripts/run_obj5_dsmil_binarias_kfold.slurm` (preflight obligatorio,
  paths absolutos a `clam_testing2/`, reuso de splits Fase 0, args
  idénticos a Fase 2, sin retuneo).

Si reviewer bloquea: ajustar el doc o el `.slurm`, NO commitear hasta OK.
