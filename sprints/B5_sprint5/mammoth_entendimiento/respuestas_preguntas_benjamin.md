# MAMMOTH — entendimiento profundo: las preguntas de Benjamín (reunión 29-jun-2026)

> **Objetivo**: responder, aterrizado en el **paper original** (Shao et al.,
> *Mixture of Mini Experts…*, ICLR 2026, `papers/mammoth_shao_iclr2026.pdf`) y en
> el **código real** (`clam_testing2/MAMMOTH/src/mammoth/mammoth.py` + nuestro
> `models_mammoth/clam_mammoth.py`), cada pregunta que Benjamín hizo y que no
> supimos contestar. **Regla 5**: todo lo de acá está citado contra paper o código;
> lo que NO está en ninguno se marca explícitamente como "razonamiento, no en el
> paper".
>
> Config de referencia = la NUESTRA (CONCH 512): `input_dim=512`, `slot_dim=256`,
> `num_experts(E)=30`, `num_slots(S)=10`, `num_heads(H)=16`, `auto_rank → rank Q=8`.
> (El paper usa encoder de ≈1024 y `S=9`; la diferencia se discute en §0.)

---

## §0 — Tabla maestra de dimensiones (la respuesta al "no entendía el 30×16×10×16")

Traza de un forward con nuestra config, parche por parche. `N` = nº de parches de
la slide (variable, ~miles). Código: `mammoth.py:324-371` (`Mammoth.forward`).

| Paso | Operación (código) | Entra | Sale | Qué es |
|---|---|---|---|---|
| 0. Encoder | (CONCH, fuera de Mammoth) | parches | `z = [N, 512]` | features CONCH |
| 1. Proyección a query | `wq = Linear(512, 256)` + LayerNorm (`mammoth.py:274,341`) | `[N, 512]` | `[N, 256]` | `q = norm(W_q·z)` |
| 2. Split multi-cabeza | `rearrange "b n (h d)->b n h d", h=16` (`:342`) | `[N, 256]` | `[N, 16, 16]` | 256 = **16 cabezas × 16**; `P = slot_dim/H = 256/16 = 16` |
| 3. **Prototipos (tensor S)** | `slot_embeds` (`:281-283`) | — | **`[30, 16, 10, 16]`** | **E×H×S×P** — los prototipos aprendidos |
| 4. Logits de ruteo | `einsum("b n h d, e h s d -> b n e h s")` (`:384`) | q + S | `[N, 30, 16, 10]` | similitud parche↔(experto,cabeza,slot), ec. 3 |
| 5. Dispatch | `softmax(logits, dim=1)` sobre **N** (`:410`) | `[N,30,16,10]` | `[N,30,16,10]` | "cuánto aporta cada parche a cada slot" |
| 6. Slots (pooling) | `einsum("b n h d, b n e h s -> b e h s d")` (`:347`) | q + dispatch | `[30,16,10,16]` | `u` = promedio ponderado de parches → **E·S = 300 slots** |
| 7. Expertos low-rank | `FactorizedLinear` in=16,out=32,rank=8 (`:171,287`) | `[300, 16(P)]` | `[300, 32]` | `z = LN(ReLU(W_low·Φ·u))`, ec. 4 |
| 8. Concat de cabezas | `rearrange "...e h d -> b (e s) (h d)"` (`:351`) | `[300,16,32]` | `[300, 512]` | 16×32 = 512 = `D'`. **Salida `keep_slots=True`** |
| 9. Combine (solo `keep_slots=False`) | `softmax` sobre **E·S=300** + `einsum` (`:359-367`) | `[300,512]` | `[N, 512]` | reconstruye los N parches. **Drop-in = idéntico a `Linear(512,512)`** |

**El "30×16×10×16" es el tensor `slot_embeds`** (`mammoth.py:281-283`), los
**prototipos de slot aprendidos**:

```
slot_embeds : [ num_experts=30 , num_heads=16 , num_slots=10 , head_dim_input=16 ]
                     E                 H               S              P = slot_dim/H
```

Se lee: hay **30 expertos**; cada experto, **dentro de cada una de las 16 cabezas**,
tiene **10 slots**; cada slot es un **vector-prototipo de 16 dimensiones** — y esas
16 son exactamente la dimensión del query-por-cabeza (paso 2), porque el ruteo
compara prototipo vs query con un **producto interno** y ambos tienen que vivir en
el mismo espacio de 16 (paso 4). Por eso el 16 aparece **dos veces**: una es el nº
de cabezas, la otra es la dimensión de cada sub-vector por cabeza. Total de slots =
`E·S = 30·10 = 300` (de ahí los "300 slots" del deck).

> **Discrepancia paper vs nuestra config**: el paper (§4, "We use E=30 experts,
> H=16 heads, and **S=9 slots**", línea 436 del PDF) usa **9 slots/experto** →
> 270 slots; nuestro default `num_slots=10` → 300. Es un hiperparámetro, ambos
> caen en la banda recomendada (ver §Q5). Si Benjamín pregunta "¿270 o 300?": el
> paper principal usa 270; nosotros 300 por el default del README de la lib.

---

## §1 — Qué es MAMMOTH, en una frase (y el acrónimo, que sí importa)

**MAMMOTH = *MAtrix-factorized Mixture Module of Transformation Heads*** (paper §3,
línea 218 del PDF). El acrónimo nombra los 4 pasos del forward:

1. **Transformation Heads** → procesamiento **multi-cabeza** de la entrada (§3.1).
2. **Mixture** → **ruteo por slots** = mezcla de expertos suave (§3.2).
3. **MAtrix-factorized** → expertos de **bajo rango / LoRA** (§3.3).
4. **Module** → **concatena** las cabezas y entrega la salida (§3.4).

Reemplaza **una sola capa**: el `nn.Linear` que en CLAM proyecta los features del
encoder al espacio interno de la MIL (`fMIL_linear`, ec. 1 del paper). Es
**drop-in** y con **el mismo presupuesto de parámetros** (de ahí `auto_rank`, §Q5).
NO es un modelo MIL aparte (a diferencia de DSMIL).

---

## §2 — El "porqué": el cuello de botella de la capa lineal única

Esto es el corazón conceptual y lo que hay que poder explicarle a un niño de 14.

**El problema (paper §2, líneas 73-86):** una sola matriz lineal aplica **la misma
transformación a TODOS los parches**, sin importar qué tejido sean. Pero una slide
de mama mezcla morfologías muy distintas. El paper lo dice con **nuestro** dominio:

> *"In breast cancer lesion subtyping… diverse concepts such as **epithelial cell
> morphology, spatial arrangement, and stromal layer architectures** are
> collectively important factors for diagnosis."* (paper, líneas 76-78)

Si una sola W tiene que servir para epitelio, estroma y disposición espacial a la
vez, queda en un punto intermedio mediocre para todos → el espacio interno sale
como **una nube continua sin estructura** (paper Fig 1A, arriba).

**La analogía (para los 14 años):** es un solo traductor que tiene que traducir
del chino, del árabe y del ruso al mismo tiempo con una sola plantilla. Le va más o
menos en los tres. MAMMOTH contrata **30 traductores especialistas** (expertos) y
un **recepcionista** (el ruteo) que manda cada documento al especialista que
corresponde. Cada uno se vuelve bueno en lo suyo.

**Dos nombres para el mismo mecanismo de daño** (importante para no contradecirnos):
- El **paper** lo enmarca como: asignación *dura* de expertos → *"poor gradient
  flow… imbalanced expert utilization"* (líneas 110-127). Su fix es **asignación
  suave** (cada experto procesa una combinación lineal de **todos** los parches).
- **Nuestro README/skill** lo llama ***instance-gradient interference***: los
  parches de tumor "tiran" de la W en una dirección y los de grasa en otra; al ser
  una sola W compartida, esos gradientes opuestos se cancelan. Es la **misma idea**
  contada desde el gradiente. Ambas valen; si Benjamín quiere "la del paper", usar
  la de gradient flow / expert utilization.

**La evidencia (paper Fig 1):** panel A, t-SNE — la capa original da una nube
continua, MAMMOTH la separa en grupos nítidos (un color por experto). Panel B —
en 8 agregadores distintos (ABMIL, CLAM, TransMIL, DSMIL…) el punto MAMMOTH queda
siempre a la derecha del original. Mejora **transversal** y con el mismo presupuesto.

---

## §Q1 — "¿Qué significa cada cabeza? ¿Cada feature es textura/forma/color?"

**Respuesta honesta y aterrizada: NO, las cabezas NO están pre-asignadas a
textura/forma/color.** Lo que respondiste en la reunión (textura, forma, color) es
una intuición razonable pero **no es lo que el modelo hace por construcción**, y por
eso hiciste bien en decir que no estabas seguro.

**Qué ES una cabeza (mecánica, §3.1 + `mammoth.py:342`):** el query de 256 se parte
en **16 trozos no solapados de 16 dimensiones** (ec. 2 del paper:
`x̄_{i,h} = (W·x_i)[(h-1)P+1 : hP]`). Cada cabeza corre **su propio ruteo + sus
propios expertos en paralelo**, sobre su trozo. Es **exactamente la idea de
multi-head attention**: cada cabeza mira un **subespacio aprendido** distinto del
embedding. No hay nada que le diga a la cabeza 3 "tú eres textura". Son subespacios
**emergentes**, sin semántica impuesta.

**Dónde SÍ aparece semántica reconocible: en los SLOTS/expertos, no en las cabezas.**
El paper demuestra interpretabilidad a nivel **(experto, slot)**, no de cabeza
(paper Fig 3 + §5.2). Los parches de mayor similitud a cada slot forman grupos
morfológicamente coherentes que **dos patólogos certificados** etiquetaron:
*Tumor Cells, Alveoli, Stroma, Lymphocytes, Red Blood Cells* (Fig 3B). Y **emerge
solo durante el entrenamiento**, sin supervisión de tejido.

**Entonces la respuesta correcta a Benjamín es:**
> "Cada cabeza es una **vista paralela sobre un subespacio aprendido** del
> embedding del parche, como en multi-head attention; **no** corresponde por diseño
> a textura/forma/color. La especialización morfológica que el paper demuestra
> (tumor, estroma, linfocitos…) está en los **slots/expertos**, no en las cabezas,
> y **se descubre empíricamente** con análisis de interpretabilidad — no es una
> etiqueta que pongamos a mano. Si quieres saber qué mira una cabeza o un experto
> **concreto en mama**, hay que correr el análisis de interpretabilidad (§Q6), que
> es justo lo que propongo como objetivo."

Esto convierte el "no sé" de la reunión en un objetivo concreto y defendible.

---

## §Q2 — "Las dimensiones del vector S (30×16×10×16) y cómo calza"

Resuelto en **§0**. Resumen para decir en voz alta:

> "El **30×16×10×16** es el tensor de **prototipos de slot** (`slot_embeds`).
> Significa: **30 expertos × 16 cabezas × 10 slots × 16 dimensiones por prototipo**.
> Los 30 son los expertos; los 16 (primeros) son las cabezas porque el ruteo corre
> en paralelo por cabeza; los 10 son los slots de cada experto; y los 16 finales son
> la dimensión de cada prototipo, que coincide con la del query-por-cabeza
> (slot_dim/cabezas = 256/16 = 16) **porque se comparan con un producto interno**.
> En total son E·S = **300 slots**, cada uno un resumen de un fenotipo."

Tu guion del deck (línea 110 de `notas_presentador_guion.md`) **ya lo dice
correctamente** — el problema fue solo no haberlo verbalizado bajo presión.

---

## §Q3 — "Los 3 cuadros de colores distintos que se dividían en cada experto"

Esto es de la **Figura 2 del paper** (la que pusimos después de nuestro diagrama).
Lo verifiqué renderizando la figura. La **leyenda** de la Fig 2 define los colores:

| Color en la figura | Qué es |
|---|---|
| Cajas **lila/morado claro** | **Linear layer** → `W`, `Φ`, `W_low` |
| **3 tonos de verde** | **"Partitioned embed."** → las particiones por cabeza / slot embeddings |
| **Verde rayado/hachurado** | **"MAMMOTH embed."** → la salida transformada |
| **Naranja** | **"Slide embed."** → el embedding final de slide |

El **interior de UN experto** (zoom inferior de la Fig 2) es esta cadena:

```
particiones → [Weight. avg] → Slot 1 … Slot S → [ Φ ] → [ W_low ] → [Nonlinearity] → salida
   (verde)                      (azul)         (lila)   (lila)        (amarillo)     (verde rayado)
```

**Hay dos lecturas posibles de "los 3 cuadros", y conviene tener ambas listas:**

1. **Si Benjamín señaló los 3 tonos de verde** → son las **"Partitioned embed."**:
   el embedding del parche **partido entre las cabezas** (la leyenda dibuja 3 tonos
   solo como ejemplo de que hay varias particiones). **Clave didáctica: los 3 verdes
   NO son 3 tipos de feature (textura/forma/color); son 3 particiones del mismo
   vector**, una por cabeza. (Esto conecta con §Q1.)
2. **Si señaló los 3 bloques de proceso dentro del experto** → son las **3
   operaciones del experto de bajo rango**: `Φ` (proyección compartida que baja a
   rango 8), `W_low` (proyección propia del experto que sube a 32) y `Nonlinearity`
   (ReLU + LayerNorm). Es decir, la ecuación 4: `z = LN(ReLU(W_low · Φ · u))`.

> **Pendiente honesto**: sin que Benjamín apunte con el dedo no puedo afirmar
> **cuál** de los dos quería. La acción es **llevar la Fig 2 con la leyenda** a la
> próxima y preguntar/anticipar ambas. Lo que sí está cerrado es **qué es cada
> color** (tabla de arriba) y **qué hace cada bloque** (cadena de arriba).

---

## §Q4 — "¿Por qué MoE y no PoE?"

> **Marca importante (regla 5):** verifiqué el PDF completo — **el paper NO menciona
> "Product of Experts" ni "PoE"** en ningún lado. Así que esta respuesta es
> **razonamiento arquitectónico general**, no una cita del paper. Hay que decirlo así.

**MoE (Mixture of Experts) — lo que MAMMOTH hace:**
- La salida es una **suma ponderada (combinación convexa)** de las contribuciones de
  los expertos. El ruteo es **asignación suave**: una **softmax** de similitudes
  (ec. 3) produce pesos que **suman 1** → un promedio/mezcla.
- Cada experto se especializa en una **región** del espacio de entrada (un
  fenotipo); el router decide **cuánto** aporta cada uno. Entrenable directo, sin
  constante de normalización intratable.

**PoE (Product of Experts, Hinton 2002) — lo que MAMMOTH NO hace:**
- La salida combina a los expertos **multiplicando** sus distribuciones y
  renormalizando. Cada experto actúa como una **restricción/veto**: puede "apagar"
  una región poniéndole probabilidad baja. Sirve para distribuciones muy **afiladas**
  (todos los expertos deben "estar de acuerdo").
- Pero entrenar PoE exige la **constante de partición** (normalizador) → intratable
  → se recurre a *contrastive divergence*. Y PoE modela una **distribución de
  probabilidad**, no una **transformación de features**.

**Por qué MoE es la elección natural acá (el argumento para Benjamín):**
1. **El mecanismo de MAMMOTH ya es aditivo por construcción.** El pooling por slots
   es un **promedio ponderado por softmax** de parches (ec. 3); la reconstrucción
   recombina slots con **otra softmax** (`combine_weights`, `mammoth.py:411`). Son
   **mezclas**, no productos. Meter PoE rompería la formulación.
2. **El objetivo es "darle a cada fenotipo su propia transformación y SUMAR"** — eso
   es semántica de mezcla. El "veto multiplicativo / todos deben coincidir" de PoE
   no calza con "rutear parches distintos a especialistas distintos".
3. **La motivación central del paper es la ESTABILIDAD de entrenamiento** (gradient
   flow, §2). PoE reintroduce justo el problema que MAMMOTH evita: su normalizador
   intratable hace el entrenamiento inestable. MoE suave lo evita.

Frase corta: *"MAMMOTH es MoE porque combina expertos **sumando** contribuciones
suaves (dos softmax que suman 1), lo que es estable y entrenable; PoE los
**multiplica** como vetos, necesita un normalizador intratable y modela
probabilidades, no transformaciones de features — no calza con el diseño. El paper
no contrasta PoE; esto es razonamiento arquitectónico."*

---

## §Q5 — "¿Por qué 16 cabezas? ¿Cuántas deberían ser para cáncer de mama?"

**Parte 1 — por qué 16 (lo que SÍ se puede afirmar):**
- **16 es un hiperparámetro**, el **default recomendado** del paper (§4, línea 436),
  **no** un número derivado de la biología de la mama.
- **Restricción dura**: `input_dim` y `slot_dim` deben ser divisibles por H
  (`mammoth.py:251`): 512/16 = 32, 256/16 = 16. Así que H tiene que dividir a 512 y
  256 (8, 16, 32… son válidos).
- **Evidencia de ablación (paper Tabla 4a, "Num. heads 16 ⇒ 1 = 67.7, −5.4%"):**
  pasar de 16 a **1 cabeza cuesta −5.4%** → el multi-head **sí** aporta.
- **Banda óptima (paper §5.3, líneas 713-730):** con pocas cabezas (H∈{2,4}) el
  rendimiento es inestable y depende mucho de E; con **H∈{8,16,32} se estabiliza**, y
  **8-48 expertos con H∈{16,32} dan el mejor rendimiento**. O sea **16 cae en la
  banda empíricamente mejor y estable** — ese es el argumento, no la biología.
- **Tradeoff mecánico**: a presupuesto de parámetros fijo, más cabezas = ruteo más
  fino por subespacios pero **menor rango por cabeza** → hay un "sweet spot"
  capacidad-vs-especialización (el paper lo dice explícito).

**Parte 2 — cuántas para mama (la respuesta honesta, y por qué es un GRAN punto):**
- **No hay un número principista conocido.** Y esto **no es ignorancia nuestra**: el
  **propio paper lo marca como LIMITACIÓN** (§6, Conclusión):
  > *"Limitations include the use of a **fixed configuration of experts, slots, and
  > heads for each task**. Future works could investigate **dynamically selecting the
  > hyperparameters**, initializing the slot embeddings with morphological
  > prototypes…"*
- Es decir: **"cuántas cabezas para mama" es una pregunta abierta de investigación
  que el paper deja como trabajo futuro.** Que Benjamín la haya hecho es agudo
  precisamente porque toca un límite reconocido del método.
- **Cómo responderla de verdad (esto es el objetivo nuevo, §Q6 + objetivos):**
  (a) **ablación de H** sobre NUESTRAS tareas de mama (paired, mismos splits;
  H∈{8,16,32}), midiendo balanced_acc — ¿16 es lo mejor para mama o no?; y
  (b) **interpretabilidad**: ¿más cabezas dan especializaciones morfológicas más
  distintas en tejido mamario, o se vuelven redundantes? Una sin la otra no alcanza.

Frase corta para la reunión: *"16 es el default estable del paper (bajar a 1 cuesta
−5.4%, y H∈{8,16,32} es la banda buena); para mama no hay número principista — el
propio paper marca el E/S/H fijo como limitación y proponer cuántas es trabajo
futuro. Lo correcto es una ablación de cabezas en nuestras tareas de mama + ver si
más cabezas se especializan más. Eso es lo que propongo correr."*

---

## §Q6 — Interpretabilidad de expertos/slots: "en qué se fijan" (¡la librería lo trae!)

**Buena noticia: NO hay que inventar nada.** La librería ya incluye el código de
interpretabilidad: `clam_testing2/MAMMOTH/examples/tutorial_mammoth_visualization.py`.
Hace exactamente lo que Benjamín pide, a partir de un **checkpoint entrenado**:

1. **`dispatch_weights` de forma `(1, N, E, H, S)`** (`mammoth.py:369`, `return_weights=True`)
   → para cada parche, cuánto se rutea a cada (experto, cabeza, slot).
2. **Heatmap por experto sobre la WSI** — pinta la lámina según el score de ruteo de
   ese experto (qué zonas "enciende").
3. **Top-10 parches por experto** — recorta y guarda los parches que más activa cada
   experto → se ve, literalmente, **qué morfología mira cada uno**.

Esto es **exactamente la Figura 3 del paper** (heatmap de ruteo + top patches por
slot → tipos de tejido, anotados por patólogos). Aplicado a **nuestros checkpoints
de mama** responde, con imágenes, "¿en qué se fija cada experto/slot?":
¿epitelio? ¿estroma? ¿calcificaciones? ¿es clínicamente coherente?

**Costo**: barato — es **post-hoc, CPU**, sobre checkpoints que **ya tenemos**
(jobs mammoth de B5: 4229/4243/4246/4387/4400). Solo necesita la **WSI .svs** + los
**h5 con coords** (tenemos `clam_environ/environ/features/h5_files/`, READ-ONLY).
Patrón **Etapa 0** (sin GPU, sin reviewer) → [[calibracion-operating-point-palanca-b5]].

**Ojo / matiz importante para no sobre-vender:** que cerremos *"mammoth no es palanca
de accuracy"* (Hallazgo 12, 0 palancas) **no contradice** estudiar su
interpretabilidad. Son ejes **ortogonales**: una cosa es *"¿mejora la métrica?"*
(cerrado: no) y otra *"¿qué aprende y mira por dentro, y tiene sentido clínico en
mama?"* (abierto, y es lo que Benjamín quiere). Hay que decirlo así para no parecer
que reabrimos un veredicto cerrado.

---

## §7 — Cómo conecta con el "0 palancas" (para no contradecir la base de conocimiento)

- **Eje de RENDIMIENTO (cerrado, Hallazgo 12 de CLAUDE.md):** mammoth (8 drop-in + 4
  keep_slots) **no supera a CLAM** en ninguna tarea. Eso **no cambia**.
- **Eje de ENTENDIMIENTO / INTERPRETABILIDAD (abierto, lo que pidió Benjamín):**
  entender el mecanismo (cabezas, slots, S, MoE/PoE) y **ver qué miran los expertos
  en mama** — valioso para la presentación y la ciencia, **independiente** del
  veredicto de palanca. Es un eje **nuevo y ortogonal**, no una reapertura del 9.b.

---

## §8 — Checklist para que esto no vuelva a pasar (preparación de la próxima)

- [ ] **Llevar la Fig 2 del paper** (la original) **con su leyenda**, y anotar las
      dimensiones de §0 **en cada flecha** (entra/sale). El diagrama solo no basta:
      hay que **decir las dimensiones en cada paso**.
- [ ] **Internalizar el guion** (`notas_presentador_guion.md` líneas 92-122) — ya
      es correcto; el problema fue verbalizarlo bajo presión. Ensayar en voz alta.
- [ ] Tener listas las **3 frases cortas** (§Q4 MoE/PoE, §Q5 cabezas, §Q1 cabezas≠features).
- [ ] **Correr la interpretabilidad** (§Q6) y traer **2-3 heatmaps/top-patches de
      mama** → convierte todos los "no sé" en evidencia.
- [ ] Para "cuántas cabezas para mama": traer la **ablación de H** corrida (o al
      menos su diseño), citando la **limitación del paper §6**.

---

### Fuentes (todas verificadas en esta sesión, 29-jun-2026)
- Paper: `papers/mammoth_shao_iclr2026.pdf` — §2 (líneas 73-86, motivación mama),
  §3.1-3.4 (líneas 305-391, arquitectura), §4 (línea 436, E/H/S), Fig 1 (t-SNE +
  barras), Fig 2 (arquitectura + leyenda), Fig 3 (interpretabilidad por slot),
  §5.3 + Tabla 4a (ablaciones H/E/S), §6 (limitaciones).
- Código lib: `clam_testing2/MAMMOTH/src/mammoth/mammoth.py` (forward `:324-371`,
  `slot_embeds :281`, `get_logits :384`, `get_weights :410`, `FactorizedLinear :73`,
  `_compute_auto_rank :297`) + `examples/tutorial_mammoth_visualization.py`.
- Nuestro: `models_mammoth/clam_mammoth.py`, `sprints/B5_sprint5/presentacion_b5/notas_presentador_guion.md`.
