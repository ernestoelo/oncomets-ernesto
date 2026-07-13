# Sprint 7 — Preguntas abiertas resueltas contra el código (regla 5)

> Resuelve las preguntas §6.1 y §6.3 del prompt de entrada del sprint 7. La §6.2
> (matemática de magnificación de Sebastián) vive en `contexto_magnificacion.md`.
> Todo lo de acá está citado contra el código real de la librería Mammoth
> (`clam_testing2/MAMMOTH/src/mammoth/mammoth.py`) y contra nuestro script
> `scripts/mammoth_interpretability.py`. Fuente base ya escrita:
> `sprints/B5_sprint5/mammoth_entendimiento/respuestas_preguntas_benjamin.md` (§0, §Q1, §Q4).

---

## Q1 — "top-k de slots por peso de ruteo" ≠ el "top-k de parches por experto" que ya existe

**Veredicto: son cosas DISTINTAS. El script actual NO rankea slots.** Lo que Sebastián
pide (el peso de cada slot durante el ruteo, para saber cuáles slots son los más
activados / "los más parecidos") es un análisis **nuevo** sobre la dimensión de slots,
que hoy el pipeline colapsa. El término "top-k" que se usó en la reunión es impreciso
para esto: no es un top-k de parches.

### Qué calcula HOY `scripts/mammoth_interpretability.py` (verificado)

1. Forward con `return_weights=True` → devuelve `dispatch_weights` de forma
   **`(1, N, E, H, S)`** = `(1, N, 30, 16, 10)` (`mammoth.py:369-370`,
   `compute_expert_scores` línea 151 del script).
2. Re-normaliza por parche sobre `(E,H,S)` y colapsa **H y S**:
   `scores = dispatch[0].mean(dim=(2,3))` → **`(N, E)`** (script línea 154).
   → un score por (parche, experto). **La dimensión de slots S ya no existe acá.**
3. `expert_usage.csv` = `scores.mean(axis=0)` → **`(E,)`**: ranking de **expertos** por
   uso medio (script líneas 341-345). Columnas: `expert, mean_score`. **No hay slot.**
4. "top-k" existente = `np.argsort(scores[:, e])[::-1][:k]` (script línea 293) → los
   **k PARCHES** que más activan a cada experto. Es un top-k de **parches por experto**,
   no de slots.

**Conclusión:** el `expert_usage.csv` y el top-k actuales viven a nivel **experto** (con
S promediado hacia afuera). No dicen nada del peso por **slot**.

### Qué pide Sebastián y con qué mecanismo del código se hace

Los slots son **E·S = 30·10 = 300** en total (`mammoth.py:281-283`, tensor
`slot_embeds [30,16,10,16]`). Rankearlos por "peso de ruteo" exige **conservar la
dimensión S**, no promediarla. Hay dos pesos de ruteo reales en el código
(`get_weights`, `mammoth.py:387-415`), producidos por **dos softmax distintas** sobre
los mismos logits `(b,n,e,h,s)`:

| Peso | Softmax sobre | Forma | Semántica | ¿Lo devuelve el forward hoy? |
|---|---|---|---|---|
| `dispatch_weights` | **N** (parches), `dim=1` (`:410`) | `(b,n,e,h,s)` | "cuánto aporta cada parche a llenar cada slot" (para el pooling que arma los slots, `:347`) | **Sí** (`return_weights=True`) |
| `combine_weights` | **E·S = 300 slots**, `dim=-1` (`:411-413`) | `(b,n,h,e·s)` | "cuánto aporta cada uno de los 300 slots a reconstruir cada parche" (para el combine, `:366`, solo `keep_slots=False`) | **No** (get_weights lo calcula pero el forward no lo retorna) |

**Recomendación (a confirmar con Sebastián, es una decisión de diseño):**

- El match más literal a *"peso de cada slot durante el ruteo hacia los expertos"* es
  **`combine_weights`**: es una softmax **sobre los 300 slots** (`dim=-1`), o sea el peso
  con que cada slot participa del ruteo. Agregándolo sobre parches `N` y cabezas `H` da
  una importancia global por slot: `slot_importance = combine_weights.mean(dim=(patches, heads))`
  → vector `(300,)` reshapeable a `(E, S)`. Con eso se rankean los slots más activados.
- Alternativa: agregar `dispatch_weights` sobre `N` y `H` → `(E, S)` = "ocupación de
  slot" (cuánta masa de parches recibe cada slot). Da un ranking parecido pero mide
  otra cosa (input al slot, no aporte al output).
- *"Los más parecidos"* apunta a la **similitud cruda** (logits antes de softmax:
  `einsum("b n h d, e h s d -> b n e h s")`, `:384`) entre el query del parche y el
  prototipo de cada slot. Se puede reportar también el logit medio por slot.

**Acción para el sprint 7:** extender el script para (a) capturar `combine_weights`
(hoy el forward solo devuelve `dispatch`; agregar una rama que llame a `get_weights` o
retorne ambos), (b) agregarlo a `(E,S)` y (c) emitir un `slot_usage.csv` (columnas
`expert, slot, mean_routing_weight`) + un heatmap por slot top. Es un cambio a un
**script de análisis post-hoc de solo lectura del forward** (no toca modelo/training) →
regla 9 no se dispara, pero conviene pasar el diseño por el reviewer igual si Ernesto
lo prefiere. **No reportar esto como "top-k" a secas** en el deck: es "ranking de los
300 slots por peso de ruteo".

---

## Q3 — Relación 16 cabezas × 30 expertos × slots (la pregunta de Sebastián: ¿16 expertos?)

**Veredicto: NO es "1 experto por cabeza". Son 30 expertos, y cada una de las 16
cabezas corre su propia mezcla de los 30.** La confusión de Sebastián (16 cabezas →
16 expertos) es natural pero incorrecta: cabezas y expertos son ejes **ortogonales**.

Fuente: `respuestas_preguntas_benjamin.md` §0 (tabla maestra de dimensiones) +
`mammoth.py:281-357`.

### El tensor de prototipos `slot_embeds` (`mammoth.py:281-283`)

```
slot_embeds : [ num_experts=30 , num_heads=16 , num_slots=10 , head_dim_input=16 ]
                     E                 H              S              P = slot_dim/H = 256/16
```

Se lee: hay **30 expertos**; cada experto, **dentro de cada una de las 16 cabezas**,
tiene **10 slots**; cada slot es un vector-prototipo de **16 dimensiones** (que coincide
con la dimensión del query-por-cabeza porque se comparan por producto interno).

### Por qué NO es 1 experto por cabeza

- Las **16 cabezas corren en paralelo** (`rearrange "b n (h d) -> b n h d", h=16`,
  `:342`): el query de 256 se parte en 16 sub-vectores de 16 dims, uno por cabeza. Es
  exactamente multi-head attention: cada cabeza mira un subespacio aprendido distinto.
- El ruteo se computa **para todos los pares (experto, cabeza, slot) a la vez**:
  `logits = einsum("b n h d, e h s d -> b n e h s")` (`:384`) → forma `(N,30,16,10)`.
  O sea: para cada parche, cada cabeza evalúa su similitud con los slots de **los 30
  expertos**, no con uno.
- Total de slots efectivos = **E·S = 30·10 = 300** (de ahí los "300 slots" del deck).
  La salida `keep_slots=True` es `[N, 300, 512]`; el drop-in (`keep_slots=False`)
  recombina los 300 de vuelta a `[N, 512]` (`:359-367`).

### Las dos softmax (clave para la slide nueva §2.4)

Ambas salen del mismo tensor de logits `(b,n,e,h,s)` (`get_weights`, `:410-413`):

1. **dispatch** = `softmax` sobre **N** (parches): "de todos los parches, cuánto aporta
   cada uno a llenar este slot". Arma los slots (pooling, `:347`).
2. **combine** = `softmax` sobre **E·S = 300** (slots): "para reconstruir este parche,
   cuánto pesa cada uno de los 300 slots". Recombina la salida (`:366`).

### Frase para responderle a Sebastián / Benjamín

> "Cabezas y expertos son ejes distintos. Hay 16 cabezas que corren en paralelo, como
> en multi-head attention, cada una sobre un subespacio de 16 dimensiones del parche. Y
> hay 30 expertos. Cada cabeza NO manda a un solo experto: cada cabeza calcula, para
> cada parche, su similitud con los 10 slots de cada uno de los 30 expertos, y de ahí
> salen dos softmax, una que reparte los parches hacia los slots y otra que recombina
> los 300 slots para reconstruir el parche. Por eso son 30 y no 16."

---

## Fuentes verificadas (esta sesión, 13-jul-2026)

- Código lib: `clam_testing2/MAMMOTH/src/mammoth/mammoth.py` — `slot_embeds :281-283`,
  `forward :324-371`, `get_logits :373-385`, `get_weights :387-415` (dispatch `:410`,
  combine `:411-413`).
- Nuestro script: `scripts/mammoth_interpretability.py` — `compute_expert_scores :147-155`
  (mean sobre H,S), `expert_usage.csv :341-345`, top-k parches `:293`.
- Doc base: `sprints/B5_sprint5/mammoth_entendimiento/respuestas_preguntas_benjamin.md`
  §0 (dimensiones), §Q1 (cabezas ≠ features), §Q4 (MoE vs PoE).
