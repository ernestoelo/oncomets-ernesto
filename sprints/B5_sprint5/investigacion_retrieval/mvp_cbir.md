# MVP — Variante D (CBIR sobre embeddings CONCH) — spec de implementación

> **Spec, NO implementación** (regla 9 = fase de argumento). Este doc detalla
> *qué* se construiría y confirma que *se puede*. La implementación/corrida es
> otra sesión. Complementa `analisis.md` (§3.D, §6).
>
> **Veredicto de feasibility: ✅ VIABLE.** CPU-only, sin GPU, sin sbatch, sin
> entrenar, dentro de containment. Verificado con datos reales (5-jun, §4).

---

## 1. Qué entrega el MVP (2 cosas, 1 frame)

El frame es **"herramienta de apoyo", no "subir la métrica de clasificación"**
(la métrica no se mueve por arquitectura — Hallazgos 11/12). Entregables:

1. **CBIR cualitativo (el "wow" de la presentación).** Dada una slide query, el
   sistema devuelve las **top-k slides más parecidas** del archivo (con sus
   labels y la similitud). Es el buscador "mostrame casos como este".
2. **Validación cuantitativa honesta (paired).** El mismo índice, usado como
   **clasificador kNN por voto mayoritario** sobre NUESTRAS tareas de 2–3
   clases, evaluado **con los mismos splits que el baseline CLAM** → número
   defendible (política B5) que dice cuán lejos/cerca queda el retrieval
   zero-training del CLAM entrenado.

---

## 2. Arquitectura del pipeline (3 pasos)

```
   PASO 1: slide-vector builder (1 sola vez, ~155s CPU)
   ┌─────────────────────────────────────────────────────────┐
   │ por cada slide_id:                                        │
   │   environ/features/pt_files/<slide_id>.pt  [N_parches,512]│
   │            │  agregación (mean-pool MVP)                  │
   │            ▼                                              │
   │        v_slide  [512]   (1 vector por slide)             │
   └─────────────────────────────────────────────────────────┘
              │  apilar + L2-normalizar
              ▼
        X  [S, 512]  (~3013×512 ≈ 6 MB)  →  results/retrieval/embeddings.npz

   PASO 2: índice coseno (instantáneo, S pequeño → sin FAISS/ANN)
        coseno(q, g) = q·gᵀ  (con filas L2-normalizadas)

   PASO 3: evaluación / consulta
        gallery = slides de TRAIN (con label) del split
        query   = slides de TEST  del split
        para cada query: top-k gallery por coseno → voto mayoritario → ŷ
        métricas política B5 (paired vs CLAM, mismo split)
```

> **Por qué NO necesitamos FAISS / ANN / la maquinaria O(1) de SISH:** SISH
> resuelve búsqueda en repos de decenas de miles de slides. Nosotros tenemos
> ~3013 → una matriz S×S (≈9M floats) es trivial. Mantener el MVP simple
> (numpy/sklearn) es correcto a esta escala; ANN sería sobre-ingeniería.

---

## 3. Decisiones de diseño (y qué ablacionar)

| Decisión | MVP | Alternativas a ablacionar | Por qué importa |
|---|---|---|---|
| **Agregación parches→slide** | **mean-pool** | L2-norm-mean, GeM (p-pooling), max, top-k atención | §1.3 de `analisis.md`: es **LA** decisión; mean-pool pierde estructura espacial/MIL (límite honesto) |
| Métrica de similitud | **coseno** | L2, (Yottixel barcode/Hamming → no, es otra liga) | coseno es el estándar para embeddings de foundation models |
| k (vecinos) | **{1, 3, 5}** | hasta 10 | replicar top-1 / mayoría@3 / @5 de [Alfasly 2024] |
| Gallery | **train del split** | train+val | mantener paired honesto vs CLAM (mismo train visible) |
| Voto | **mayoría simple** | ponderado por similitud | el ponderado da un "score" → permite AUC |

**Ablación primaria pre-registrable**: agregación (mean vs L2-norm-mean vs GeM).
Hipótesis: L2-norm-mean ≥ mean (reduce el efecto de slides con muchos parches).

---

## 4. Feasibility verificada (datos reales, 5-jun-2026)

| Pregunta | Resultado | Cómo se verificó |
|---|---|---|
| ¿`slide_id` (CSV) ↔ `<slide_id>.pt`? | ✅ join directo, 5/5 | `head` CSV invasión + `test -f <id>.pt` |
| ¿Shape de las features? | ✅ `[N,512]` float32 | `torch.load` (env python) |
| N_parches por slide | 380 … 82318 (mediana 5339) | muestra 30 slides |
| Costo construir índice completo | **~155s (1 vez), CPU** | cargar+mean-pool 30 → extrapolado a 3013 |
| Tamaño del índice | ~6 MB (`float32 [3013,512]`) | cálculo |
| ¿GPU? | **NO** | es `torch.load`+numpy, sin CUDA |
| ¿sbatch? | **NO** — script CPU read-only | precedente: `scripts/analyze_invasion.py` corre directo |

**Riesgo residual:** ninguno bloqueante. El único *unknown* de diseño (no de
feasibility) es cuál agregación rinde mejor → es justo lo que ablaciona el MVP.

---

## 5. Protocolo de evaluación (política B5, paired)

Por cada task ∈ {invasión 3-clase, microcalc binarias ×3, CDIS patrón ×N} y por
cada fold del split del baseline CLAM:
- **Gallery** = slides de train (con label); **Query** = slides de test.
- kNN top-k coseno → voto mayoritario → ŷ por query.
- **Reportar SIEMPRE juntos** (política B5, [[eval-reporte-auc-y-umbrales-obj6]]):
  **balanced_acc + macro-OVR AUC** (vía score = fracción de votos o
  similitud-ponderada) **+ matriz de confusión + n por clase**.
- **Paired vs CLAM**: Δ por fold = `kNN_f − CLAM_f`, mismos splits
  ([[patron-paired-comparison-reuso-splits]]). Dirección esperada (pre-registro):
  el kNN zero-training quedará **≤ CLAM** como clasificador, pero **≫ trivial**;
  si queda *cerca* de CLAM sin entrenar, es un resultado fuerte (y el valor de
  CBIR como herramienta es independiente del Δ).

**Referencia de magnitud** ([Alfasly 2024], pero 117 subtipos ≫ duro que lo
nuestro): macro-F1 ~0.42 top-5. En 2–3 clases esperamos **bastante más alto** —
hay que **medirlo en lo nuestro**, no extrapolar.

---

## 6. Estructura de archivos (containment)

```
clam_testing2/oncomets-ernesto/
├── scripts/
│   ├── build_slide_embeddings.py   # PASO 1 (lee clam_environ RO → escribe results/)
│   └── eval_cbir_knn.py            # PASOS 2–3 (índice + eval paired + métricas B5)
├── results/retrieval/
│   ├── embeddings_<agg>.npz        # X[S,512] + slide_ids (gitignored si pesa; ~6MB ok)
│   ├── cbir_<task>_metrics.csv     # balanced_acc/AUC/F1 por fold + confusión
│   └── cbir_examples_<task>.json   # top-k cualitativo para el deck
└── sprints/B5_sprint5/investigacion_retrieval/
    ├── analisis.md                 # conceptual (este árbol)
    └── mvp_cbir.md                 # este doc
```

Lee features de `clam_environ` (**read-only**), escribe **solo** bajo
`oncomets-ernesto/`. Cero escritura fuera de containment.

---

## 7. Esfuerzo y plan de corrida (otra sesión)

- **Esfuerzo**: bajo. 2 scripts CPU (~150–250 líneas c/u). Sin entrenar, sin GPU.
  Construcción del índice ~3 min; eval por task segundos.
- **Encaja en pista corta** (cierre de trimestre) → es la razón de elegir D.
- **Orden sugerido**: (1) build_slide_embeddings (mean-pool); (2) eval_cbir_knn
  en invasión (n grande, eval sano) como smoke-test; (3) extender a binarias;
  (4) ablación agregación; (5) ejemplos cualitativos para el deck.

---

## 8. Lo que el MVP NO hace (límites honestos, anclados)

- **No supera a CLAM como clasificador** — mean-pool descarta la estructura
  MIL/atención que es justo el aporte de CLAM. El valor está en el **frame CBIR**
  + el **"sin entrenar"**, no en ganar la métrica.
- **No es clínico-grado** ([Alfasly 2024] lo dice explícito para zero-shot) →
  venderlo como **apoyo al diagnóstico por casos similares**.
- **CONCH no está medido para retrieval** en la literatura que tenemos (Alfasly
  midió UNI/Virchow/GigaPath) → el número que demos es **nuestro**, generado
  acá, no asumido.
- **Slide-vector por mean-pool es crudo** — la ablación (L2-norm/GeM) puede
  mover; documentar la elección.

---

## 9. Gate regla 9 (cuándo y cuán pesado)

El MVP **no toca** `model_*.py`/`core_utils.py`/training ni usa GPU → es
**script de análisis read-only** (liga `analyze_invasion.py`), NO un cambio de
modelo. El gate del `reviewer` (pensado para cambios de modelo/training) es
**ligero** acá, pero igual aplica el espíritu de regla 9: **pre-registrar
hipótesis + métrica + dirección** (§5) antes de correr. La pre-registración
formal va en la sesión de implementación (branch nueva), no en esta.

---

*Spec de feasibility. No se implementó, no se corrió pipeline, no se usó GPU.
Verificaciones read-only sobre datos reales (regla 5).*
