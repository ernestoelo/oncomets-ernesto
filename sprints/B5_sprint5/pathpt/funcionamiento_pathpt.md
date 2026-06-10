# PathPT — funcionamiento y arquitectura (base de estudio + fuente de la presentación)

> **Paper:** He et al., *Boosting Pathology Foundation Models via Few-shot Prompt-tuning
> for Rare Cancer Subtyping* (2025, Nature Communications). PDF en
> `papers/Boosting Pathology Foundation Models via Few-shot.pdf`. Código:
> `github.com/MAGIC-AI4Med/PathPT` (referencia; NO mezclar con `clam_environ`).
>
> **Para qué sirve este doc:** (1) base de estudio para dominar el modelo; (2) fuente
> de la **presentación del lunes** (los diagramas ASCII de acá se convierten en assets
> PNG insertables — ver `scripts/generate_slide_assets.py`, convenciones
> [[presentacion-convenciones-benjamin]]: **sin nombres, sin proceso de entrenamiento**,
> genérico/claro/preciso). Registrado en el audit 10-jun (hallazgo P).
>
> **Estado:** PathPT validado por el supervisor → **prueba activa** (empezar por
> **necrosis**, luego **mitotic rate**). Memoria [[pathpt-testing-necrosis-mitotic]].

---

## 0. La idea de fondo (una línea)

CLAM comprime una WSI a **un vector de slide** y la clasifica (usa solo visión).
**PathPT clasifica parche por parche**, usa **el encoder de TEXTO** del modelo
visión-lenguaje (que CLAM ignora) y, como solo hay labels de slide, **fabrica labels
de parche** con el *grounding* zero-shot del modelo. Todo con los encoders **congelados**;
solo entrena 2 módulos chicos.

```
   CLAM (MIL clásico)                          PathPT
   ─────────────────                           ──────
   N parches → atención → 1 vector slide       N parches → se REFINA cada parche con su
        → clasificador slide-level                  vecindario → se CLASIFICA cada parche
   visión SOLA · supervisión slide-level            → se agrega a slide al final
                                                visión + LENGUAJE · supervisión tile-level
```

---

## 1. El sustrato: CONCH (visión-lenguaje), CONGELADO

CONCH tiene **dos encoders** en el **mismo espacio de 512-dim**:

- **Φ_v** (visión): parche → `v ∈ ℝ⁵¹²`. *Son las features `.pt` que ya tenemos en
  `environ/features/pt_files/` — CONCH aplicado a cada parche.*
- **Φ_t** (texto): frase → `t ∈ ℝ⁵¹²`. *CLAM nunca lo usa; es el "activo dormido" de CONCH.*

Como viven en el mismo espacio, se puede comparar imagen vs frase por **coseno**.

> **Relación CONCH↔PathPT↔CLAM (la confusión típica):** PathPT **NO reemplaza** a CONCH;
> es una carcasa chica **encima de CONCH congelado**. Reusa las features `Φ_v` que ya
> tenemos, **enciende `Φ_t`**, y agrega 2 módulos entrenables (`θ_v`, `θ_t`). **CLAM no
> se descarta:** queda como **baseline/vara de medir**; PathPT se evalúa **paired vs CLAM**
> sobre los mismos splits. Ambos consumen las mismas features CONCH.

```
        ┌──────────── CONCH (CONGELADO) ────────────┐
        │   Φ_v (visión)            Φ_t (texto)      │
        └──────┬────────────────────────┬───────────┘
        features .pt YA TENEMOS    DORMIDO (CLAM no lo usa; PathPT sí)
               │                        │
               ▼                        ▼
        ┌───────────────────────────────────────────┐
        │  PathPT = + θ_v (módulo espacial)          │
        │           + θ_t (32 prompts aprendibles)   │   ← lo único que entrena
        └───────────────────────────────────────────┘
        CLAM = otro consumidor de Φ_v (baseline, NO se descarta)
```

---

## 2. Las 7 ecuaciones clave (lo que hay que saber)

| Ec. | Qué expresa | En una frase |
|---|---|---|
| **1** | `ŷ = argmax_i ⟨v, t_i⟩` | zero-shot: clasifico un parche por la frase-clase más parecida (coseno) |
| **2** | `ŷ_i = F_MIL({v_ij}; θ_v)` | CLAM: agrega los parches → 1 predicción por **slide** `i` |
| **3** | `ŷ_ij = F_PathPT(v_ij; θ_v, θ_t)` | PathPT: predicción por **parche** `ij` (¡ahí está el cambio!) |
| **4** | `v̄₁..v̄_M = Ψ(Φ_v(x₁)..Φ_v(x_M))` | módulo espacial: refina cada parche con su vecindario; sigue 1 vector/parche |
| **5** | `c̄ = [T]₁..[T]_K [CLASS]` | prompt aprendible: K=32 tokens de contexto + nombre de clase |
| **6** | `p(y=j\|x_i) = softmax(⟨Φ_t(c̄_j), v̄_i⟩/τ)` | prob. del parche por clase = coseno texto-imagen con temperatura τ |
| **7** | `L_unlabeled = −log(p(y=0\|x)+p(y=i\|x))` | pérdida de "etiqueta parcial": el parche es normal **o** el subtipo de la slide |

(Ec. 8 = balanced accuracy; ec. 9/10 = AUC/DICE para segmentación.)

---

## 3. Los 3 componentes (innovaciones)

### 3.1 Agregación espacial (rama `θ_v`, ec. 4)
Ordena los parches por **coordenadas (x,y)** → grilla 2D, y los pasa por `Ψ`:
- **Bloque local:** convolución residual con kernels **3×3, 5×5, 7×7** → vecindario inmediato.
- **Bloque global:** **transformer** (self-attention) → dependencias de largo alcance.

Salida: **un vector refinado por parche** (NO se colapsa a slide → conserva granularidad
espacial = localización del tumor). Requiere las coords (`h5_files/`, que tenemos). Es el
**contexto espacial** que CLAM no modela entre vecinos.

### 3.2 Prompt-tuning (rama `θ_t`, ec. 5-6, estilo CoOp)
En vez de escribir la frase de cada clase a mano, **aprende K=32 tokens** de contexto
(compartidos entre clases; solo cambia el `[CLASS]`), inicializados desde un prompt manual.
"Busca la frase latente óptima" sin tocar el encoder. Barato → **few-shot-friendly**.

### 3.3 Pseudo-labels tile-level + 3 pérdidas (el corazón)
**Generación (zero-shot, sin entrenar, CPU):**
1. **Selección de prompts:** pool de 200 (templates × clases) → rankear por accuracy de
   clasificación de slides en train → top-100 → **mean-pool** → 1 vector de texto/clase robusto.
2. **Etiquetado selectivo:** coseno texto-parche → predicción; **retener SOLO** parches
   predichos "normal" o **consistentes** con el label de slide; **descartar** los que
   predicen *otro* subtipo. (Usa el label de slide para filtrar el ruido del profesor CONCH.)

**Las 3 pérdidas (curriculum de confianza):**

```
   época:  0 ── 2 ──────── 10 ──────────── 20
   L_labeled  (1.0) ███████████████████████  ← CE balanceada sobre parches con pseudo-label
   L_unlabeled(0.5) ███████████████████████  ← ec. 7, etiqueta parcial sobre los descartados
   L_pseudo   (0.1)         ████████████████  ← self-training (el modelo se re-etiqueta)
```
- `L_pseudo` arranca recién época 10 (el modelo ya es mejor que CONCH crudo) y con peso
  bajo (0.1) → evita amplificar errores propios (confirmation bias).
- **Se habilita SOLO con CONCH y KEEP** (con PLIP/MUSK es inestable) → **CONCH está en el
  tier confiable.**

Entrenamiento: 20 épocas, lr 1e-4, warm-up 2 épocas, 1 GPU (RTX 4090 en el paper).

---

## 4. Qué entrena vs qué NO (define el costo + el gate)

| Pieza | ¿Entrena? | Implicación |
|---|---|---|
| `Φ_v`, `Φ_t` (encoders CONCH) | ❌ congelados | no re-entrenamos CONCH |
| `θ_v` (módulo espacial) | ✅ sí | **GPU + regla 9 + reviewer** |
| `θ_t` (32 prompts) | ✅ sí | idem |
| Generar pseudo-labels | ❌ inferencia zero-shot | CPU, barato (= el go/no-go) |

**PathPT toca training → cae en regla 9 + reviewer + `sbatch`** (≠ el CBIR/D, que era CPU
sin entrenar). Y **NO es un `--model_type` de CLAM** como mammoth: es un **harness propio**
(clasifica por parche, usa texto, necesita coords + prompts) → integrarlo es más trabajo.

---

## 5. Por qué construir los prompts de clase, y por qué es el RIESGO

PathPT compara parches contra **frases** (ec. 1, 6). Para obtener `t_i` hay que pasar una
**frase clínica** por `Φ_t`. **Los CSVs del dataset dan el NOMBRE de la clase, NO el prompt:**

- Ej. `label = presente` / `ausente` / `no_identificado` → es el `[CLASS]`, no una frase.
- Además están **en español** y son jerga abreviada; CONCH fue entrenado mayormente con
  caption **en inglés** → hay que **expandir/traducir** a frases clínicas reales
  (ej. *"a histopathology image showing tumor necrosis"*) y armar un **pool de variantes**.

**El riesgo (lo honesto):** todo el motor depende de que CONCH **groundee zero-shot
NUESTRA morfología puntual**. Si no "ve" necrosis / microcalcificación / invasión zero-shot
→ pseudo-labels basura → entrenamiento sobre arena → **null**. Es **task-específico y no
testeado**, PERO **barato de chequear** → §7 (go/no-go).

---

## 6. Verdad de campo — las 2 tareas que pidió el supervisor (read-only, 10-jun)

| Tarea | CSV | Slides | Clases (conteo) |
|---|---|---|---|
| **Necrosis** (CDIS) | `dataset_carcinoma_ductal_in_situ_necrosis_label.csv` | 810 | `ausente` 83 · `no_identificado` 414 · `presente_central` 285 · `presente_focal` 28 |
| **Tasa mitótica** | `dataset_grado_histologico_tasa_mitotica_label.csv` | 1870 | `no_identificado` 693 · `score_1` 636 · `score_2` 287 · `score_3` 254 |

- **Necrosis** mapea bien a "hallazgo focal" (`presente_*` = pocos parches positivos) —
  régimen donde la supervisión tile-level brilla. Pero `presente_focal` (28) es rarísimo.
- **Mitotic rate** es un **score ordinal** (Nottingham 1/2/3) — ¿lo trata como 3 clases
  nominales? Decisión de diseño a definir.
- **`no_identificado` es el problema en ambas:** mayoritario y **mal definido a nivel tile**
  (= el reporte CAP no lo menciona, no una apariencia visual). No se le puede escribir un
  prompt morfológico → decidir si se excluye (como en los binarios de microcalc) o se trata
  como "normal/sin hallazgo". **Crítico para el diseño de prompts.** ([[cap-fuente-clases-tareas]])

---

## 7. Plan de prueba (orden, con el go/no-go barato primero)

1. **Etapa 0 — go/no-go (CPU, sin GPU, sin entrenar):** generar los **embeddings de texto
   CONCH** de los prompts de **necrosis**, etiquetar zero-shot los parches (componente 3.3
   paso 2) y mirar: (a) ¿algún prompt clasifica las slides mejor que el trivial? (b) ¿los
   parches "positivos" caen donde un patólogo esperaría? **Decide si vale invertir GPU.**
   Pre-registrar hipótesis + dirección (regla 9, [[eval-reporte-auc-y-umbrales-obj6]]).
2. **Etapa 1 (solo si Etapa 0 pasa):** implementación completa, **paired vs CLAM** reusando
   los mismos splits ([[patron-paired-comparison-reuso-splits]]); pre-registración regla 9
   + **reviewer** + `sbatch`; branch nueva.
3. Repetir el ciclo con **mitotic rate**.

> **Contexto favorable:** el supervisor corre **mammoth sobre las mismas tareas** (necrosis,
> mitotic) → habrá **baselines CLAM/mammoth** listos para el paired (ver README mammoth).

---

## 8. Métricas y eval (política B5)

Inferencia: predicción por parche (ec. 6) → agregación **"tumor-ratio"** (como KEEP) → label
de slide. Reportar **SIEMPRE juntos**: `balanced_acc + AUC + matriz de confusión + n por
clase` ([[eval-reporte-auc-y-umbrales-obj6]]); comparación **paired vs CLAM**, mismos splits.
Bonus de PathPT: mapa de localización del tumor (grounding) que CLAM no da.

---

## 9. Resultados del paper (para citar en la presentación, sin nombres ni training)

- **PathPT-CONCH** = mejor en **9/11** benchmarks vs MIL (incl. CLAM); PathPT-KEEP 8/11.
- EBRAINS (30 subtipos, el más duro): PathPT-KEEP **0.679** bal-acc (+0.271 vs zero-shot);
  ahí CONCH flaquea (grounding pobre → malos pseudo-labels).
- Cánceres comunes de pocas clases: CONCH **competitivo** con KEEP.
- **Techo de datos honesto:** a 10-shot varios métodos convergen a 0.54-0.55 — *"a ceiling
  imposed by limited data"* → **misma conclusión que nuestros Hallazgos 11/12** (el método
  deja de ser la palanca cuando faltan datos). Reencuadre presentable, no fracaso.

---

*Doc de estudio/registro. No se entrenó, no se usó GPU. Verificaciones read-only sobre datos
reales (regla 5). Los diagramas ASCII se convierten en assets PNG para la presentación.*
