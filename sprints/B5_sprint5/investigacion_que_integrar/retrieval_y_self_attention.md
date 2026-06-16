# Deep-dive: ¿retrieval o self-attention global sobre CLAM para subir AUC / balanced_acc?

> **Sprint B5 — fase de ARGUMENTO (regla 9).** No toca `model_*.py` / training /
> GPU. Responde a fondo la pregunta de Ernesto (11-jun): *"en base a lo aprendido
> con PathPT, ¿es viable incorporar al pipeline de CLAM algún tipo de **retrieval**
> o **módulo de self-attention global** para mejorar AUC y balanced_acc?"*
>
> Complementa `analisis.md` (síntesis de candidatos). Acá se entra al detalle
> técnico de las DOS ideas concretas que preguntó, con su veredicto anclado.
> Anclas: código real (`models_pathpt/spatial.py`, `models/model_clam.py`),
> resultados (jobs 4309/4326), y los 2 papers leídos (PathPT, Alfasly).

---

## 0. Veredicto en una tabla (para no enterrar la conclusión)

| Idea preguntada | ¿Viable técnicamente? | Prior honesto sobre AUC/bal_acc | Por qué |
|---|---|---|---|
| **Self-attention global** (estilo TransMIL) | ✅ **Sí — infra YA existe** (`nystrom_attention` vendorizado, `TransLayer` en `models_pathpt/spatial.py`) | ⚠️ **Null probable** | Es un swap de agregador (eje cerrado, Hallazgos 11/12). Y **ya lo corrimos dentro de PathPT** (θ_v = Nyström self-attention) → no levantó necrosis sobre el zero-shot. TransMIL es baseline-techo en el paper PathPT. |
| **Retrieval en el pipeline** | Depende del flavor | ⚠️ **No mueve AUC, o null** | CBIR (variante D) = herramienta, **no toca el AUC del clasificador**. Retrieval-augmented = o swap de agregador (var A, "mammoth #2") o **acotado por CONCH** (= el cuello diagnosticado). |
| *(lo que SÍ apunta a más AUC, según PathPT)* | — | — | **El ENCODER es el techo** (KEEP > CONCH) + **calibración del operating-point** (palanca barata, ya documentada en `analisis.md`). |

**Resumen:** las dos ideas son **implementables** (una casi gratis), pero la evidencia
—nuestra y del paper PathPT— predice que **ninguna sube el AUC/bal_acc de forma
consistente sobre CONCH**, porque ambas siguen siendo arquitectura o están acotadas
por el mismo encoder que diagnosticamos como cuello. Lo honesto: si se corren, es
para **cerrar la pregunta limpiamente** (barato, infra lista), no porque se espere un
salto. La palanca con prior positivo está en **calibración** (barata) y **encoder más
fuerte** (caro).

---

## 1. El marco: qué pregunta estamos respondiendo (y cuál NO)

Ernesto pregunta por **integrar algo a CLAM para subir AUC/bal_acc**. Eso es distinto
de "entregar valor por otra vía" (CBIR como herramienta, `analisis.md` §4). Acá la
vara es dura: **mover la métrica de clasificación**. Y sobre esa vara pesa todo lo
que ya probamos:

```
  3 EJES DE ARQUITECTURA CERRADOS (0 palancas):
    Hallazgo 11  agregador (DSMIL)          → NULL
    Hallazgo 12  patch-embed (mammoth/MoE)  → NULL · 8 tareas
    Hallazgo 13  lenguaje+tile (PathPT)     → necrosis H_alt / mitotic colapso / microcalc NO-GO
  + confirmación SOTA externa: PathPT, TransMIL, DGRMIL convergen a 0.54-0.55
    a 10-shot = "a ceiling imposed by limited data" [He 2025/26, leído].
```

La pregunta correcta entonces no es "¿qué módulo nuevo?", sino **"¿la idea X escapa
de la categoría 'swap de arquitectura sobre CONCH', que ya sabemos que da null?"**.
Aplico ese filtro a las dos.

---

## 2. SELF-ATTENTION GLOBAL — la pregunta directa

### 2.1 Qué sería, y en qué difiere REALMENTE de CLAM

La atención de CLAM (`models/model_clam.py`, gated-attention, L239 pooling) puntúa
**cada parche por separado**: una red chica le da un peso `a_k` a cada parche *sin
mirar a los otros*, y agrupa `M = Σ a_k h_k`. **No hay interacción parche-parche.**

Self-attention **global** (TransMIL, Shao et al. NeurIPS 2021) hace que **cada parche
atienda a todos los demás** antes de agrupar → modela *correlación espacial /
contexto entre parches*. Es la diferencia entre "cada parche vota solo" vs "los
parches se ponen de acuerdo mirándose entre sí". **Ese contexto parche-parche es,
literalmente, lo único que CLAM no modela** — y conecta con "contexto espacial", que
venimos nombrando como parte del cuello (Hallazgos 11/12, `funcionamiento_pathpt.md`
§3.1).

> Por eso la pregunta de Ernesto es **buena**: de todos los swaps de arquitectura, el
> de self-attention global es el **menos redundante** con lo ya probado (DSMIL y
> mammoth NO agregan contexto parche-parche). Es el único que ataca un eje —contexto
> espacial— que nombramos pero no aislamos.

### 2.2 EL HALLAZGO: ya lo tenemos implementado y parcialmente medido

Acá está la vuelta de tuerca. **PathPT incluye exactamente este mecanismo** y lo
corrimos. El módulo espacial θ_v (`models_pathpt/spatial.py`) es:

```
  MultiKernelConv1DTrans (θ_v):
    ├─ Conv1d multi-kernel 3/5/7  → contexto LOCAL (vecindario, parches ordenados por x,y)
    └─ TransLayer = LayerNorm + NystromAttention(heads=8, landmarks=256) residual
                                  ↑ ESTO es self-attention GLOBAL (Nyström-aproximada)
```

`NystromAttention` **es** el núcleo de TransMIL (TransMIL = Nyströmformer sobre tokens
-parche + position encoding por convolución). El `Conv1d` multi-kernel cumple el rol
del PPEG de TransMIL (codificación posicional por conv). En otras palabras: **θ_v ≈
un bloque TransMIL.** La dependencia `nystrom_attention` que instalamos en
`clam_testing2/.pylibs` es la misma que usaría un TransMIL.

**Lo corrimos** (necrosis job 4309, mitotic job 4326, alcance "A full" = θ_v + θ_t +
pseudo-labels). Resultado de necrosis (`resultados_necrosis.md` §4):

> *"El entrenamiento apenas se despegó del zero-shot... θ_v + θ_t **no agregaron**
> sustancialmente sobre el zero-shot."* (PathPT AUC 0.661 vs teacher zero-shot
> ~0.61-0.63; CLAM 0.727 le gana a ambos.)

### 2.3 La evidencia (3 fuentes) apunta a null — pero con un caveat de honestidad

```
  Fuente 1 (nuestra, directa):  3 ejes de arquitectura cerrados, 0 palancas.
                                Un agregador-self-attention es otro swap → mismo prior.
  Fuente 2 (nuestra, del θ_v):  el bloque Nyström-self-attention, en la config que
                                corrimos (dentro de PathPT), NO levantó necrosis.
  Fuente 3 (SOTA, paper leído): TransMIL es baseline en PathPT y converge al MISMO
                                techo de datos (0.54-0.55) que los demás métodos.
```

**Caveat honesto (importante, no lo escondo):** la Fuente 2 **no aísla** "self-
attention global no sirve". En PathPT, θ_v está *entrelazado* con θ_t (prompt-tuning)
y la supervisión tile-level por texto; el null de necrosis puede deberse al
**grounding débil de CONCH** (θ_t / pseudo-labels), no a θ_v. **La ablación limpia
—TransMIL como agregador puro: self-attention global → class token → clasificador de
slide, supervisado por labels de slide igual que CLAM— NO la corrimos.** Lo que sí
tenemos es: (a) el prior de los 3 ejes, (b) que el mecanismo ya está implementado y
no brilló en la única config que lo ejercitó, y (c) que TransMIL toca el techo en el
benchmark SOTA. Los tres apuntan al mismo lado, pero el dato limpio falta.

### 2.4 Veredicto + el experimento más barato si se quiere CERRAR la pregunta

- **Viable:** sí, y **barato** — la infra ya está (`nystrom_attention` vendorizado,
  `TransLayer` portado). Un `models_transmil/` (TransLayer × L + class token + cabeza
  de slide) + branch aditivo en `train_dsmil.py` (`--model_type transmil`) + slurm
  reusando splits = la receta `@mil-model-integration` que ya aplicaron DSMIL y
  mammoth. Costo: bajo. Una ola GPU k=5 paired.
- **Prior:** null. Sería el **4º swap de arquitectura**.
- **Cuándo SÍ tiene sentido correrlo:** si se quiere **convertir "sospechamos que el
  contexto espacial importa" en "lo medimos"** — cerrar el eje *contexto espacial*
  limpiamente con la ablación que falta (§2.3). Eso es presentable (refuerza la tesis
  "arquitectura no es la palanca" con un 4º punto, esta vez el menos redundante) y
  barato. **NO es la apuesta para "subir el AUC"** — es ciencia de cierre.
- **Pre-registración (regla 9), si se corre:**
  - *Hipótesis:* si el cuello fuera el contexto parche-parche que CLAM ignora,
    TransMIL (self-attention global) debería superar a CLAM, **más** en tareas con
    señal espacial difusa (necrosis multifocal, patrón arquitectónico). *Alternativa
    (la esperada):* Δ pareado cruza 0 → contexto espacial tampoco es la palanca.
  - *Métrica/dirección:* balanced_acc + AUC + confusión + n, **paired por fold** vs
    CLAM (mismos splits). Dirección esperada honesta: null (std ≳ |media|).
  - *Toca training → reviewer + sbatch + branch.*

---

## 3. RETRIEVAL — la pregunta directa

Hay que separar **dos cosas que se llaman "retrieval"** y tienen veredictos opuestos.

### 3.1 Flavor 1 — CBIR como herramienta (variante D): NO mueve el AUC

Es el "buscador de slides parecidas" (`analisis.md` §4, `investigacion_retrieval/`).
**No toca el clasificador** → no cambia el AUC/bal_acc de CLAM. Es un **entregable
clínico** distinto. Excelente para la presentación (bajo riesgo, CPU, diagrama D10
hecho), pero **fuera de la vara de esta pregunta** (que es subir la métrica). No
confundir: CBIR ≠ "mejor clasificador".

### 3.2 Flavor 2 — Retrieval-augmented classification: o swap, o acotado por CONCH

Acá sí se busca **subir el AUC** usando vecinos recuperados para informar la
predicción. Sub-variantes y su veredicto:

| Sub-variante | Qué es | Veredicto |
|---|---|---|
| **A — retrieval en el agregador** (RAM-MIL) | pesar/combinar parches por cercanía a ejemplos recuperados, en vez de atención aprendida | **Swap de agregador = "mammoth #2"**, prior null (`analisis.md` §5, `investigacion_retrieval` §3.A). Su ganancia reportada es robustez *out-of-domain* — que NO es nuestro cuello. |
| **B — prototipos / kNN / memory-bank** (PANTHER, SISH) | clasificar por distancia a centroides de clase / banco de embeddings | Ataca **pocos positivos** (data-efficiency real), pero **acotado por la calidad del embedding = CONCH = el cuello**. Y choca el techo de datos. Research-grade, no quick-win. |
| **C — RAG sobre el train** (kNN-attention) | recuperar slides/parches similares del train y concatenar/atender como contexto extra | Añade complejidad; **sigue acotado por CONCH**; sin evidencia de que rompa el techo. |

### 3.3 Lo que PathPT ya nos dice sobre retrieval (clave: no es especulación)

PathPT **ya contiene retrieval por similitud** y lo medimos:
- La **selección de prompts** (componente 3.3, `funcionamiento_pathpt.md`): rankea 200
  prompts por accuracy de clasificación de slides, retiene top-100, mean-pool → 1
  vector-texto robusto por clase. **Es retrieval sobre prototipos de texto.**
- El **etiquetado tile-level**: coseno texto-parche → retener los parches consistentes.
  **Es retrieval-by-similarity en el espacio CONCH.**

Ese aparato —retrieval de prototipos + similitud en CONCH— **no levantó** necrosis
(H_alt) y **colapsó** en mitotic. La lectura: **el retrieval en el espacio CONCH
hereda el límite de CONCH.** Si CONCH no separa bien nuestra morfología (microcalc
AUC 0.44-0.63, grounding débil), un kNN/prototipo sobre CONCH tampoco lo hará — la
métrica de distancia es tan buena como el embedding. **Retrieval no crea señal que el
encoder no tenga.**

### 3.4 Veredicto retrieval

- **CBIR (D):** viable, valioso, **pero no es palanca de AUC** — es herramienta.
  Mantener para la presentación, no venderlo como "mejor clasificador".
- **Retrieval-augmented (A/B/C):** o es un swap de agregador (null), o está **acotado
  por CONCH** (el cuello). El único nicho con argumento real es **B (prototipos para
  pocos positivos)**, pero es KEEP-dependiente y PathPT-con-CONCH ya mostró el límite.
  Prior: modesto/null sobre CONCH. **No quick-win.**

---

## 4. La lección de fondo de PathPT: el ENCODER es el techo (esto es lo que de verdad sube el AUC)

Si el objetivo literal es **más AUC/bal_acc**, el paper PathPT —leído— es explícito
sobre dónde está la palanca que SÍ funciona, y **no es el agregador ni el retrieval:**

- PathPT gana **según el modelo base**: con **KEEP** (mejor grounding zero-shot) sube
  fuerte (EBRAINS +0.271); con CONCH/PLIP/MUSK, modesto o null. **La variable que
  movió la métrica en el paper fue cambiar el encoder, no el módulo encima.**
- Nuestra propia evidencia converge: 3 ejes de "lo que va encima de CONCH" cerrados;
  lo que no probamos es **cambiar CONCH**.

```
   Lo que NO mueve la métrica          Lo que SÍ la mueve (según PathPT + lo nuestro)
   ──────────────────────────          ─────────────────────────────────────────────
   agregador (DSMIL)            ✗       encoder más fuerte (KEEP/UNI/Virchow/GigaPath) ✓ caro
   patch-embed (mammoth)        ✗       calibración del operating-point                ✓ barato
   self-attention global        ✗?      (más datos / mejores positivos)                ✓ lento
   retrieval sobre CONCH        ✗
```

**Las dos palancas con prior positivo:**
1. **Calibración / operating-point** (barata, ortogonal, demostrable post-hoc sobre
   los scores ya guardados) — desarrollada en `analisis.md` §3 y memoria
   [[calibracion-operating-point-palanca-b5]]. Acotada por el AUC, pero rescata el
   colapso y rebalancea sensibilidad sin re-entrenar.
2. **Encoder más fuerte** (cara): re-extraer features con KEEP/UNI/Virchow. Es la
   palanca que el paper muestra funcionando, pero implica **conseguir el modelo +
   re-correr extracción sobre ~3000 slides (GPU, infra grande)** y **no tenemos
   KEEP**. Honesto: es el verdadero techo, pero es trabajo de trimestre(s), no de
   aquí al lunes. Conecta con el pedido de Sebastián de "magnificación / nº de
   parches" (Eje A/B del plan B5) — ambos son *mejorar la materia prima*, no el
   modelo encima.

---

## 5. Tabla integrada — todas las opciones contra la vara "subir AUC/bal_acc"

| Opción | Categoría | Prior AUC | Costo | Regla 9 | Recom. |
|---|---|---|---|---|---|
| **Self-attention global** (TransMIL agregador) | swap arquitectura (el menos redundante) | null | **bajo** (infra lista) | training → reviewer | correr **solo para CERRAR el eje contexto-espacial**, no como apuesta |
| **CBIR** (retrieval-herramienta) | frame distinto | **no aplica** (no toca clasificador) | bajo (CPU) | trivial | sí, pero **como entregable**, no como lever de AUC |
| **Retrieval-augmented** (A/B/C) | swap o acotado-por-CONCH | modesto/null | medio-alto | training → reviewer | no (B = research trimestre siguiente, KEEP-dep) |
| **Calibración operating-point** | leer mejor la salida (ortogonal) | **positivo, acotado por AUC** | **muy bajo** (post-hoc CPU) | trivial (Tier 0) | **SÍ — la apuesta técnica** |
| **Encoder más fuerte** (KEEP/UNI…) | cambiar la materia prima | **positivo** (lo que el paper muestra) | **alto** (re-extracción GPU, conseguir modelo) | sí | research de fondo; conecta con magnificación (Eje A/B) |

---

## 6. Recomendación

1. **Respuesta directa a Ernesto:** **sí, las dos son técnicamente viables** (la self-
   attention global casi gratis — la infra ya está). **Pero ninguna tiene prior
   positivo para subir el AUC/bal_acc**, porque ambas siguen siendo "algo encima de
   CONCH" (swap de arquitectura o retrieval acotado por el encoder), que es justo la
   categoría que cerramos en 3 ejes. Y de hecho **la self-attention global ya la
   corrimos dentro de PathPT (θ_v = Nyström) y no levantó.**
2. **Si se quiere convertir la corazonada en evidencia:** la ablación **TransMIL-como-
   agregador, paired vs CLAM** es barata (infra lista) y **cierra el eje contexto-
   espacial** —el único swap menos redundante— con la prueba limpia que hoy falta
   (§2.3). Va con regla 9 + reviewer + sbatch. Prior honesto: null; valor: cierre
   presentable (4º punto de "arquitectura ≠ palanca").
3. **Para de verdad mover la métrica:** la palanca barata y con prior positivo es
   **calibración del operating-point** (`analisis.md` §3); la palanca de fondo (cara,
   research) es **un encoder más fuerte** (lo que PathPT muestra funcionando), que se
   alinea con el eje de datos/magnificación que Sebastián ya pidió.
4. **CBIR** se mantiene como **entregable de presentación** (no como lever de AUC).

**Orden sugerido (todo argumento → luego código con OK de Ernesto):** (a) cerrar este
análisis; (b) demostrar **calibración Tier 0** (post-hoc, CPU, sin GPU); (c) si se
quiere el cierre del eje espacial, **TransMIL ablation** paired (barato, prior null);
(d) CBIR MVP para la slide. El encoder más fuerte = hoja de ruta del trimestre
siguiente.

---

## 7. Caveats, honestidad y qué falta

- **No sobre-vender el cierre de self-attention:** lo que tenemos es prior + un null
  *entrelazado* (θ_v dentro de PathPT). La ablación limpia (TransMIL agregador) no se
  corrió; afirmar "self-attention global no sirve" **sin** esa ablación sería ir más
  allá de la evidencia. Lo correcto: "prior null fuerte; la prueba limpia es barata si
  se quiere certeza".
- **Retrieval no crea señal:** un kNN/prototipo es tan bueno como el embedding (CONCH)
  → hereda el cuello. Esto es mecanismo, no opinión.
- **PDFs que faltan para profundizar** (regla 5 — no inventar specs): **TransMIL**
  (Shao 2021), **RAM-MIL** (Cui 2023), **SISH** (Chen 2022), **PANTHER** (Song 2024)
  **no están en `papers/`**. El *mecanismo* de TransMIL está validado vía el código
  (`models_pathpt/spatial.py` usa su núcleo Nyström) y vía el paper PathPT que lo lista
  como baseline; para specs finas (capas, PPEG exacto) habría que subir el PDF. Lo
  marco como "literatura, PDF no en repo".
- **La gran no-probada honesta = encoder más fuerte.** Es la única con prior positivo
  fuerte que NO hemos tocado, pero es cara y no tenemos KEEP. No prometer que entra al
  lunes.
- **Nada de esto toca `clam_environ/`** ni el working tree ajeno. Sin GPU, sin
  training en esta fase (regla 9).

---

*Fase de argumento (regla 9). No se tocó modelo, no se usó GPU, no se entrenó. Claims
anclados al código real (`models_pathpt/spatial.py`, `models/model_clam.py`), a los
resultados (jobs 4309/4326, `resultados_{necrosis,mitotic}.md`) y a los 2 PDFs leídos
(PathPT [He 2025/26], Alfasly [2024]). Mecanismos de papers sin PDF en repo, marcados
como tales.*
