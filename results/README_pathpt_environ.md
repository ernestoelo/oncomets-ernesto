# Experimentos PathPT-CONCH en CLAM — OncoMets / Environ (config, datasets, splits, resultados)

> Autor: Ernesto Gamero · Sprint B5 (cierre trimestre jun-2026).
> **FUENTE CANÓNICA Y VERSIONADA** de este doc (vive en el repo, sobrevive a una
> pérdida del workspace y es citable desde GitHub). Si existe una copia en
> `clam_testing/`, es un stub/derivado — editá SIEMPRE acá.
> Doc de referencia para el equipo (Sebastián). Documenta, por tarea: la **config
> fija**, el **dataset de origen** y el **n por clase**, el **split** usado, y los
> **resultados** (con balanced_acc + AUC, política B5).
>
> **Qué es PathPT** (alcance A, "full"): CONCH **congelado** + un módulo espacial
> entrenable θ_v + prompt-tuning θ_t (CoOp) sobre descripciones clínicas en texto +
> supervisión a nivel **tile** (pseudo-labels) con un currículum de pérdidas. **Reusa
> las features de visión CONCH ya generadas** (no se regeneran features); solo se
> "enciende" el encoder de **texto** de CONCH para los prompts.
>
> **Comparación central:** PathPT (`train_pathpt.py`) **vs** CLAM (baseline,
> `train_dsmil.py --model_type clam`), **k=5 paired** (mismos splits ambos brazos) →
> Δ pareado por fold, sin confound de sorteo.
>
> Todo el código/datos/resultados viven en `clam_testing2/oncomets-ernesto/` (este
> repo). Detalle largo por tarea: `sprints/B5_sprint5/pathpt/resultados_{necrosis,mitotic}.md`.

---

## 1. Config fija de entrenamiento

Brazo **CLAM** (baseline) — args "bendecidos" Environ:

| Arg | Valor | | Arg | Valor |
|---|---|---|---|---|
| `--model_type` | `clam` | | `--max_epochs` | 30 |
| `--B` | 8 | | `--early_stopping` | sí |
| `--bag_weight` | 0.7 | | `--seed` | 1 |
| `--lr` | 2e-4 | | `--drop_out` | 0.25 |
| `--reg` | 1e-5 | | `--embed_dim` (CONCH) | 512 |

Brazo **PathPT** (`train_pathpt.py`, alcance A full): θ_v (espacial) + θ_t (prompt-tuning
CoOp) + pseudo-labels tile-level + currículum de pérdidas. **20 épocas, lr 1e-4.** Prompts
**v3 anclados en CAP** (`Breast.Invasive.Bx_1.2.0.0`, necrosis = Nota C; mitótica =
Nottingham). Umbral de decisión de PathPT elegido sobre `val` y congelado a `test` (sin
DoF post-hoc). Features: **CONCH 512-dim** (las mismas .pt ya extraídas).

> Política de evaluación (B5): se reporta **balanced_acc Y AUC juntos** (test) + matriz de
> confusión + n por clase. Métrica decisiva = **Δ pareado por fold** (`pathpt − clam`),
> media ± std; interpretación cualitativa (consistencia de signo, varianza, vs trivial).

---

## 2. Tareas, clases, n por clase y dataset de origen

**Cohorte `_pth` = Privado (Environ) + TCGA + HistAI.** Se excluye `no_identificado`
(slides cuyo reporte CAP no menciona el ítem) → universo identificado.

| Tarea (`--task`) | tipo | clases (n por clase) | n total |
|---|---|---|---|
| `cdis_necrosis_2clases_pth` | binaria | `no`=83 / `si`=313 | 396 |
| `grado_mitotic_3clases_pth` | 3 clases ordinales (Nottingham) | `score_1`=636 / `score_2`=287 / `score_3`=254 | 1177 |

CSV de labels y splits: `$REPO/data/splits_kfold/<task>_100/splits_{0..4}.csv`.

---

## 3. Splits (verdad de campo)

**Esquema:** Monte-Carlo CV **k=5** estratificado, `patient_strat`, `val_frac=test_frac=0.1`,
`seed=1`. Ambos brazos (CLAM y PathPT) leen **el mismo** `splits_<f>.csv` → Δ pareado por fold.

```
$REPO/data/splits_kfold/
├── cdis_necrosis_2clases_pth_100/    splits_{0..4}.csv
└── grado_mitotic_3clases_pth_100/    splits_{0..4}.csv
```

---

## 4. Resultados

### 4.0 Resumen AUC por tarea — media y mejor de los 5 folds

`test_auc` de `test_metrics.json` de cada run, k=5 paired. **media** = promedio de los 5 folds;
**mejor** = máximo. Necrosis = ROC-AUC; mitótica = macro one-vs-rest.

| Tarea (`--task`) | Dataset (n) | Split dir (`$REPO/data/splits_kfold/`) | CLAM media | CLAM mejor | PathPT media | PathPT mejor |
|---|---|---|---|---|---|---|
| `cdis_necrosis_2clases_pth` | _pth · 396 (313 si/83 no) | `cdis_necrosis_2clases_pth_100/` | 0.727 | 0.798 | 0.661 | 0.798 |
| `grado_mitotic_3clases_pth` (macro-OVR) | _pth · 1177 (636/287/254) | `grado_mitotic_3clases_pth_100/` | 0.724 | 0.765 | 0.662 | 0.714 |

> El AUC media/mejor es **resumen descriptivo**; el veredicto usa Δ pareado + balanced_acc
> (§4.a–4.b). **PathPT no es palanca en ninguna.**

### 4.a Necrosis binaria (COMPLETO — job 4309, 11-jun)

**Veredicto: H_alt — PathPT no aporta sobre CLAM.** Detalle:
`$REPO/sprints/B5_sprint5/pathpt/resultados_necrosis.md`.

| brazo | bal_acc (media±std) | AUC (media±std) |
|---|---|---|
| CLAM (baseline) | 0.633 | 0.727 |
| PathPT | 0.613 | 0.661 |
| **Δ pareado (pathpt − clam)** | **−0.020 ± 0.078** (2+/3−, cruza 0) | **−0.066 ± 0.094** (lean negativo) |

> El Δ cruza 0 con std ≫ |media| → ambiguo/null. PathPT entrenado apenas se despega del
> CONCH zero-shot (~0.62) mientras CLAM le gana (0.727). Confusión pooled: PathPT redistribuye
> el trade-off (detecta algo mejor la clase chica a costa de la mayoritaria), no rompe nada.

### 4.b Tasa mitótica 3-clase (COMPLETO — job 4326, 11-jun)

**Veredicto: PathPT COLAPSA al argmax de la clase mayoritaria (`score_1`)** — la comparación
de balanced_acc no es pareja. Detalle:
`$REPO/sprints/B5_sprint5/pathpt/resultados_mitotic.md`.

| brazo | bal_acc (media±std) | macro-OVR AUC | confusión pooled (s1/s2/s3) |
|---|---|---|---|
| CLAM (baseline) | 0.494 | 0.724 | `[[231,53,36],[77,27,38],[26,28,72]]` |
| PathPT | **0.333** (trivial exacto) | 0.662 | `[[320,0,0],[142,0,0],[126,0,0]]` |
| **Δ pareado (pathpt − clam)** | **−0.160 ± 0.049** (5/5−) | **−0.062 ± 0.062** (3−/2+, amb) | — |

> PathPT manda **todo a `score_1`** (0 predicciones de score_2/score_3 en 588 slides). El
> macro-OVR AUC NO colapsa (el ranking continuo retiene señal), pero el **argmax es inusable**
> bajo este desbalance. **Causa = la formulación ordinal "clase 0 = score_1 basal"** (los tiles
> de baja densidad mitótica dominan todas las slides), **NO un bug** (eval validado test CPU 9/9;
> CLAM con los mismos splits no colapsa, bal 0.494). **El sign-off clínico de esa formulación es
> de Sebastián (pendiente)** antes de cualquier re-corrida.

### 4.c Microcalcificaciones — go/no-go zero-shot (NO entrenado)

Prueba barata (CPU, ~minutos, **sin GPU**): clasificar cada slide por similitud CONCH
imagen↔texto de los prompts, sin entrenar nada. AUC mejor sobre top-j parches (top-j=100):

| Binaria (`microcalcificaciones_en_..._pth`) | n (no/si) | AUC zero-shot (mejor) |
|---|---|---|
| `..._carcinoma_invasivo_pth` | 260 / 68 | 0.629 |
| `..._cdis_pth` | 210 / 118 | 0.533 |
| `..._tejido_no_neoplasico_pth` | 136 / 192 | 0.444 |

> **NO-GO**: CONCH no "groundea" microcalcificaciones desde el texto (AUC ≈ trivial 0.5).
> Iterar los prompts de carcinoma con más morfología (v2/v3) **empeoró** (0.533 / 0.552 < 0.629)
> → CONCH prefiere términos simples. No se llevó a entrenamiento GPU (ahorro ~18–24 h GPU).
> JSON: `$REPO/results/pathpt_gonogo/microcalc_*_zeroshot_metrics.json`.

---

## 5. Lectura del hilo PathPT

**PathPT-CONCH no resultó ser palanca.** Converge con Mammoth (patch-embed) y DSMIL
(agregador): 3 ejes distintos, 0 palancas → **el cuello es el dato / desbalance / CONCH /
calibración, no el método**. El go/no-go zero-shot barato (CPU) demostró su valor: descartó
microcalc antes de gastar GPU.

## 6. Reproducir / trazabilidad

- Hipótesis pre-registrada (regla 9, reviewer GO): `$REPO/sprints/B5_sprint5/pathpt/etapa1_prereg_{necrosis,mitotic}.md`.
- Resultados largos: `$REPO/sprints/B5_sprint5/pathpt/resultados_{necrosis,mitotic}.md`.
- Prompts CAP: `$REPO/sprints/B5_sprint5/pathpt/prompts_cap.md`.
- Port PathPT: `$REPO/models_pathpt/` (pin `0ab7f1b`); driver `$REPO/train_pathpt.py`;
  test CPU `$REPO/tests/test_pathpt_cpu.py`.
- Salidas por run: `$REPO/results/pathpt_etapa1/<tarea>/<modelo>_<task>_f<0..4>_*_s1/`
  (`test_metrics.json`: balanced_acc + AUC + confusión + n).
