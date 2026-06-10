# Etapa 0 — Go/No-Go de PathPT-CONCH en necrosis (pre-registración regla 9)

> **Qué es:** la prueba **más barata posible** (CPU, sin entrenar, sin GPU) que decide
> si vale la pena el desarrollo grande de PathPT. Materializa el pedido del supervisor
> ("generar los embeddings de texto CONCH para necrosis") como un experimento honesto.
> **Argumento ANTES de código (regla 9).** Implementación = recién tras OK.
>
> Base conceptual: [funcionamiento_pathpt.md](funcionamiento_pathpt.md) (es el
> **componente 3, paso 2** de PathPT — etiquetado zero-shot — aislado y medido).

---

## 1. Por qué esta prueba decide (el mecanismo)

PathPT-CONCH se sostiene sobre una premisa: **CONCH groundea zero-shot la morfología de
la tarea** → puede producir pseudo-labels tile-level limpios (ec. 1: `ŷ = argmax_i ⟨v, t_i⟩`).
Si CONCH **no** groundea necrosis, los pseudo-labels son ruido → todo el entrenamiento se
construye sobre arena → **null** (es el modo de fallo de EBRAINS en el paper).

**Condición necesaria:** si CONCH no clasifica necrosis a **nivel slide** zero-shot
(donde tiene *máxima* señal, agregando miles de parches), **menos** va a producir buenos
pseudo-labels a nivel parche. Medir el slide-level zero-shot es un **filtro necesario
(no suficiente)** y cuesta horas, no semanas.

---

## 2. Hipótesis pre-registrada (regla 9)

- **H1 (primaria):** los prompts clínicos de "necrosis presente" dan **mayor** similitud
  coseno (agregada a slide) en las slides etiquetadas `presente_*` que en las `ausente`
  → CONCH **groundea** necrosis zero-shot.
- **H0 (nula):** la similitud no separa presente vs ausente (balanced_acc ≈ trivial,
  AUC ≈ 0.5) → CONCH **no** groundea necrosis zero-shot.
- **Regresión / señal mala:** separación **invertida** (ausente puntúa más alto que
  presente) → prompts mal construidos o concepto fuera del vocabulario de CONCH.

**Mecanismo esperado si H1:** comedonecrosis (el patrón clásico de necrosis en CDIS) es
morfología marcada (restos celulares eosinofílicos, núcleos picnóticos) → CONCH, entrenado
con captions de patología, *debería* tener señal. Si no la tiene, es un hallazgo en sí.

---

## 3. Datos y subset (verdad de campo, read-only)

`dataset_carcinoma_ductal_in_situ_necrosis_label.csv` — 810 slides:
`ausente` 83 · `no_identificado` 414 · `presente_central` 285 · `presente_focal` 28.

- **Excluir `no_identificado`** (414): mal definido a nivel tile (= el CAP no lo menciona,
  no una apariencia) → no se le puede escribir un prompt morfológico.
- **Binario para el go/no-go:** `presente` = `presente_central` ∪ `presente_focal` (313)
  vs `ausente` (83). Desbalance ~3.8:1 → por eso **balanced_acc**, no accuracy cruda.
- Features: `environ/features/pt_files/<slide_id>.pt` `[N,512]` (read-only, ya cacheadas).
- *(Etapa 0 = todas las slides identificadas; no hay train/test porque NO se entrena. Para
  el paired vs CLAM de Etapa 1 se restringe a los test de `data/splits_kfold/...`.)*

---

## 4. Métrica (predefinida, política B5)

- **Agregación tile→slide:** "tumor-ratio" = fracción de parches predichos `presente`
  (o media de similitud-ponderada como score continuo para AUC). Probar k-pooling top-k
  como en CONCH zero-shot.
- **Reportar SIEMPRE juntos** ([[eval-reporte-auc-y-umbrales-obj6]]): **balanced_acc +
  AUC (macro-OVR) + matriz de confusión + n por clase**.
- **Cualitativo:** para ~3 slides `presente`, los parches top-necrosis (con sus coords del
  `h5`) ¿caen en zonas plausiblemente necróticas? (sanity check del grounding tile-level).

---

## 5. Dirección y regla de decisión (interpretada, NO gate mágico — regla 9.a)

| Resultado | Lectura | Acción |
|---|---|---|
| balanced_acc ≳ 0.65–0.70 **y** AUC ≳ 0.70, signo correcto | CONCH groundea necrosis | **GO** → Etapa 1 (PathPT completo, paired vs CLAM, regla 9 + reviewer + sbatch) |
| balanced_acc ≈ 0.5 / AUC ≈ 0.5 | CONCH no groundea zero-shot | **NO-GO** barato — null #2 confirmado sin quemar GPU; reportar como hallazgo |
| en el medio / signo inconsistente | ambiguo | iterar **prompts** (pool más rico) + mirar tiles; re-decidir |

> Los números son **dirección esperada interpretada**, no umbrales automáticos (regla 9.a:
> "métrica predefinida ≠ umbral mágico"). Con n chico la magnitud y el signo mandan, no un
> gatillo binario.

---

## 6. Diseño de prompts (el trabajo clínico — a validar con Ernesto/CAP)

Los CSVs dan el **nombre** (`presente`/`ausente`), no la frase. Construir un **pool** en
inglés clínico (templates × clases), estilo CONCH (`zeroshot_path.py`):

- **Templates** (del set CONCH): `"a histopathology image of {}"`, `"an image showing {}"`,
  `"{} in breast tissue"`, … (mean-pool de los mejores, como PathPT).
- **Clase `presente`** `{}` ∈ {`tumor necrosis`, `comedonecrosis`, `necrotic debris`,
  `necrotic tumor cells`, `central necrosis in ductal carcinoma in situ`}.
- **Clase `ausente`** `{}` ∈ {`viable tumor cells without necrosis`, `ductal carcinoma in
  situ without necrosis`, `benign breast tissue`}.

⚠️ **Validar la redacción clínica con Ernesto/Sebastián (CAP)** antes de fijarla — es el
factor que más mueve el grounding ([[cap-fuente-clases-tareas]]).

---

## 7. Plan del script (CPU, containment) — a implementar tras OK

`scripts/zeroshot_necrosis_gonogo.py`:
1. Cargar CONCH (`create_model_from_pretrained('conch_ViT-B-16', 'hf_hub:MahmoodLab/conch')`,
   checkpoint ya en cache; `sys.path` a `clam_environ/CONCH`, **import read-only**).
2. Construir pool de prompts → `tokenize` → `model.encode_text` → mean-pool → 1 vector/clase.
3. Por slide identificada: `torch.load(<id>.pt)` → L2-norm → coseno vs vectores de clase →
   predicción por parche → agregación tumor-ratio → score + ŷ de slide.
4. balanced_acc + AUC + confusión + n (vs CSV). Volcar ejemplos top-k tiles (coords `h5`).
5. **Output → `results/pathpt_gonogo/`** (containment). CPU, sin GPU, sin sbatch (liga
   `analyze_invasion.py`, que corre directo).

**Gate:** es **inferencia zero-shot** (no toca `model_*.py`/`core_utils`/training) → NO
dispara el `reviewer` (sí lo hará la Etapa 1, que entrena `θ_v`/`θ_t`). Igual cumple regla 9
por esta pre-registración.

---

## 8. Qué NO afirma esta prueba (límites)

- Un GO **no** garantiza que PathPT gane a CLAM (eso lo dice el paired de Etapa 1); dice que
  la premisa de grounding **no está rota**.
- Un NO-GO con CONCH **no** condena a PathPT en general — condena a PathPT-**CONCH para
  necrosis** (KEEP podría, pero no lo tenemos). Es exactamente el caveat refinado del audit.

---

---

## 9. RESULTADO (10-jun-2026) — corrida sobre las 396 slides

Script `scripts/zeroshot_necrosis_gonogo.py` (CPU, 142s). Subset binario: **83 ausente /
313 presente** (no_identificado excluido), 0 `.pt` faltantes. Salida en
`results/pathpt_gonogo/necrosis_zeroshot_metrics.{json,csv}`.

| top-j | **AUC** (primaria) | bal_acc @ mejor umbral | bal_acc @ argmax (degenerado) |
|---|---|---|---|
| 1   | 0.662 | 0.635 | 0.580 |
| 5   | **0.677** | **0.649** | 0.564 |
| 10  | 0.674 | 0.635 | 0.557 |
| 50  | 0.662 | 0.640 | 0.532 |
| 100 | 0.657 | 0.628 | 0.524 |

**Lectura honesta (vs §5):**
- **AUC ~0.66–0.68, consistente en todos los top-j → señal REAL, NO null** (≫ trivial 0.5).
  CONCH **sí groundea** necrosis zero-shot. H0 (no grounding) se **descarta**.
- Pero **NO llega a la banda GO fuerte** (AUC ≳0.70 / bal_acc ≳0.65–0.70 que pre-registramos).
  Cae en la **banda intermedia / ambigua-favorable**.
- El **bal_acc@argmax degenerado (~0.52–0.58)** confirma que el zero-shot crudo **no está
  calibrado** para presente-vs-ausente (los logits de "normal" dominan). **Esto valida la
  NECESIDAD del prompt-tuning de PathPT** (`θ_t`), que justamente calibra/optimiza la frase.

**Por qué esto es un FLOOR, no el techo:** es zero-shot puro, con prompts **borrador sin
validar clínicamente**, sin módulo espacial, sin entrenar. PathPT construye **encima** de este
0.67: prompt-tuning (calibra), contexto espacial (`θ_v`) y pseudo-labels self-training. La
pregunta del go/no-go era *"¿hay señal para bootstrapear?"* → **sí, moderada.**

**Veredicto: LEAN-GO con palanca barata pendiente.** No es null (seguimos), pero antes de
invertir GPU conviene agotar el lever más barato y de mayor impacto (según el paper): **iterar
los prompts con validación clínica** (Sebastián/CAP) + **chequeo cualitativo de localización**
(coords `h5`), para ver si el AUC sube hacia ≥0.70. Recién con eso, decisión GO→Etapa 1
(PathPT completo, paired vs CLAM, **regla 9 + reviewer + sbatch**).

*Pre-registración (§1–8) escrita ANTES del código. Feasibility verificada read-only en
`clam_latest` el 10-jun. Resultados (§9) = corrida real, sin GPU, sin entrenar (regla 5/9).*
