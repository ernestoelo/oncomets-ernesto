# OBJ-A — Estudio para la reunión del viernes (interpretabilidad de MAMMOTH)

> **Sprint B6.** Doc de estudio **VIVO** — se llena a medida que repasamos los 5 bloques.
> Objetivo: **dominar OBJ-A** (no mecánicamente, como la primera vez) para presentarlo el viernes.
> Eje **ORTOGONAL** al "0 palancas" (Hallazgo 12): entender *qué mira* mammoth ≠ mejorar métrica.
> Sale de la reunión 29-jun de Benjamín ([[feedback-benjamin-entender-mammoth]]).

---

## Dónde vive cada cosa (provenance — NO duplicar)

**Resultados canónicos (run del 30-jun, artefacto de B5) — NO se mueven de acá:**
`sprints/B5_sprint5/mammoth_entendimiento/interpretabilidad/`
- `resultados.md` — documento de resultados del OBJ-A
- `TCGA-E2-A14Q-01Z-00-DX1_cdis_f0/heatmap_montage.png` — 30 heatmaps de ruteo (Fig 3.1)
- `TCGA-E2-A14Q-01Z-00-DX1_cdis_f0/topk_subset_6experts.png` — morfología top-k (Fig 3.2)
- `TCGA-E2-A14Q-01Z-00-DX1_cdis_f0/topk_contact_sheet.png` — los 30 expertos × top-8
- `cross_slide/expert_{08,26,03,15}_crossslide.png` — un experto fijo en las 4 slides
- otras 3 slides (2 pos + 2 neg): `TCGA-D8-A1XF...`, `TCGA-BH-A0EE...`, `TCGA-UU-A93S...`

**Referencia teórica (aterrizada en paper + código):**
`sprints/B5_sprint5/mammoth_entendimiento/respuestas_preguntas_benjamin.md` (§0 dims, §Q1-Q6)

**Script (reusable):** `scripts/mammoth_interpretability.py`

**Este doc (B6):** notas de estudio + material NUEVO para el viernes. Las figuras que
regeneremos para la presentación se guardan **acá** (B6), no en B5.

---

## Qué es OBJ-A (una frase)

Interpretabilidad **post-hoc** de MAMMOTH en mama: sobre un checkpoint ya entrenado (cdis,
drop-in) y en CPU, se miran (a) **qué región de la slide reclama cada experto** (heatmaps de
ruteo) y (b) **qué morfología** hay en esas regiones (top-k parches a alta resolución).
Convierte los "no sé" de la reunión 29-jun en evidencia con imágenes.

**Hallazgo central:** los 30 expertos se especializan por **MORFOLOGÍA** (e8 epitelio tumoral,
e26 estroma, e3 ductal), estable entre slides — pero rutean por **tejido, no por la etiqueta
de la slide** (un experto es un *detector de tejido*, no de clase). Confirma Hallazgo 12: la
especialización existe, pero el cuello de botella no está en la 1ª capa.

---

## Roadmap de estudio (5 bloques)

| # | Bloque | Qué domino | Pregunta de Benjamín | Estado |
|---|---|---|---|---|
| 1 | Qué es un panel del montage | qué cantidad se pinta (ruteo) | base para leer la figura | ✅ estudiado |
| 2 | Qué muestran los top-k | morfología por experto | Q3, Q6 ("en qué se fija") | ✅ estudiado |
| 3 | El hallazgo fino | morfología ≠ clase (detector de tejido) | por qué no contradice "0 palancas" | ✅ estudiado |
| 4 | La mecánica del tensor | 30×16×10×16, cabezas, slots, MoE≠PoE | Q1, Q2, Q4, Q5 | ✅ estudiado |
| 5 | Honestidad + guion | limitaciones, sign-off patólogo | no sobre-vender | ✅ estudiado |

---

## Bloque 1 — ¿Qué es realmente un panel del montage?  ✅

**Dónde vive MAMMOTH.** CLAM, apenas recibe los features CONCH de cada parche (un vector de
512 números por parche), lo primero que hace es pasarlos por **una sola capa lineal** — una
matriz `W` que transforma esos 512 en otros 512, *igual para todos los parches*. MAMMOTH
**reemplaza exactamente esa capa, nada más**. Atención + clasificador de CLAM quedan idénticos.

**Analogía (la de "explicar a un niño de 14", literal del paper §2).** Esa capa única es **un
solo traductor** obligado a traducir chino, árabe y ruso con la misma plantilla → mediocre en
los tres, porque una slide de mama mezcla morfologías muy distintas (epitelio tumoral, estroma,
ductos). MAMMOTH contrata **30 traductores especialistas** (los *expertos*) y un
**recepcionista** (el *router*) que decide, para cada documento (parche), **cuánto** mandarlo a
cada especialista.

**Qué pinta el heatmap.** El router no manda cada parche a *un* experto y listo: le asigna un
**peso a cada experto** ("este parche va 0.7 al e8, 0.1 al e26, ..."). Ese peso es el **score
de ruteo**. Entonces:

> Un panel del montage = fijás **un experto** (p. ej. e8), recorrés **todos los parches** de la
> slide, y pintás cada parche con el peso que el router le dio *a ese experto*. Rojo = "el router
> manda mucho de este parche al e8"; azul = "casi nada".

Por eso los 30 paneles tienen la misma silueta pero **encienden zonas distintas**: cada
experto se quedó con un "barrio" morfológico de la lámina.

**Matiz honesto (defendible ante Benjamín):** el color está normalizado **por percentil dentro
de cada experto** — cada panel usa todo el rango 0→1 por construcción. Por eso se ve "moteado" y
**no** se puede comparar magnitud absoluta *entre* paneles. El panel muestra *estructura espacial
relativa* (qué regiones prefiere ese experto), **no** "este experto se usa más que aquel". Para
eso está `expert_usage.csv` (que sale **casi uniforme** → ver Bloque 3).

**En una frase para el viernes:** *"Cada panel es la slide pintada por cuánto el router manda
cada parche a ese experto; los 30 encienden regiones distintas = la capa lineal única se
reemplazó por especialistas que miran zonas distintas."*

---

## Bloque 2 — ¿Qué muestran los top-k?  ✅

**Del "dónde" al "qué".** El Bloque 1 leyó el heatmap: *dónde* de la slide enciende un
experto. Pero un mapa de calor no dice **qué tejido** hay en esas zonas rojas — solo dice
"acá el router manda mucho al e8". El **top-k** cierra ese hueco: fijás un experto, tomás
los **parches que más rutea** (los de score de ruteo más alto) y los **recortás a alta
resolución real del `.svs`** (`read_region`, no del thumbnail borroso) para **mirar la
morfología con los ojos**. Heatmap = *dónde*; top-k = *qué*.

**Las dos figuras.** `topk_subset_6experts.png` (legible: 6 expertos × sus top parches) para
mostrar en la slide; `topk_contact_sheet.png` (los 30 expertos × top-8) como respaldo si
Benjamín quiere ver todos. Cada fila es un experto; cada columna, uno de sus parches más
característicos.

**Qué se ve (lectura provisional — ver Bloque 5).**

| Experto | Morfología dominante en sus top parches |
|---|---|
| **e8** | Nidos epiteliales densos, núcleos basófilos apiñados → **epitelio tumoral** |
| **e26** | Estroma fibroso fuertemente eosinófilo (colágeno rosado) → **estroma** |
| **e3** | Estructuras ductales con revestimiento epitelial → **epitelio ductal / pared de ducto** |
| **e15, e13, e20** | Mixtos (epitelio + zonas laxas/quísticas) → solapamiento esperado |

**Por qué hay expertos "mixtos" y eso NO es un fallo.** El ruteo es **suave** (Bloque 4): el
router reparte cada parche entre varios expertos, no lo asigna a uno solo. Sumado a que solo
miramos los top-k (un puñado de parches), es **esperable** que e15/e13/e20 mezclen fenotipos.
El solapamiento es una propiedad del diseño, no ruido.

**El anclaje al paper (Fig 3 / §5.2).** Esto no lo inventamos: el paper hace exactamente este
análisis y **dos patólogos certificados** etiquetaron los grupos que emergen —
*Tumor Cells, Alveoli, Stroma, Lymphocytes, Red Blood Cells*. Y lo clave: **emerge sin
supervisión de tejido** (nadie le dijo al modelo "esto es estroma"; salió solo del
entrenamiento). Nuestros e8/e26/e3 reproducen cualitativamente esa historia en mama.

**Cómo responde a Benjamín.** Su pregunta 6 ("los cuadros que se dividen en cada experto") y
la 9 ("en qué se fijan para una zona importante") se contestan **con imágenes**: "este experto
se fija en epitelio tumoral, este otro en estroma". El "no sé" de la reunión pasa a ser
evidencia visual.

**En una frase para el viernes:** *"El top-k son los parches que cada experto más rutea,
recortados a alta resolución: se ve directamente que e8 mira epitelio tumoral, e26 estroma y
e3 ductos — la misma especialización morfológica que el paper validó con patólogos, ahora en
nuestras slides de mama."*

---

## Bloque 3 — El hallazgo fino: morfología ≠ clase  ✅

**El experimento que lo prueba (estabilidad cross-slide).** Los prototipos de cada experto
(`slot_embeds`) son **parámetros compartidos del modelo**: el e8 es el **mismo** e8 en
*todas* las slides. Entonces hay una prueba limpia — si su especialización es real, e8 debe
elegir **la misma morfología** en las 4 slides. Se fijó un experto y se miró su top-k en las
4 (2 positivas + 2 negativas): **`cross_slide/expert_08_crossslide.png`** etc. Resultado: e8
enciende epitelio celular en las 4; e26, estroma en las 4. **Estable.**

**El giro que hay que entender bien.** e8 enciende epitelio **también en las slides
negativas**. Y acá está el matiz que evita malinterpretar todo: "negativo" en esta tarea es
**cdis sin microcalcificación** — *no* "sin tumor". Las negativas siguen siendo slides de
mama con epitelio, estroma, ductos. Por eso e8 (detector de epitelio) se enciende igual. **Un
experto es un detector de TEJIDO, no un detector de CLASE.**

**Dónde se decide la clase, entonces.** La decisión slide-level ("¿hay microcalcificación en
cdis?") **no** la toma el experto. Viene **después**: el ruteo opera a nivel de
parche/fenotipo (1ª capa), y recién aguas abajo el **attention pooling + el clasificador de
bag** de CLAM combinan todo en una etiqueta de slide. El experto solo dice "esto es
epitelio", no "esta slide es positiva".

**Por qué esto CONFIRMA el "0 palancas" (Hallazgo 12) en vez de contradecirlo.** Es el punto
más fino y el más valioso para la reunión. Los expertos **sí** se especializan (separan bien
los tejidos) — y aun así mammoth **no** le gana a CLAM en métrica. La conclusión encaja
sola: **si la 1ª capa ya separa correctamente los tejidos y el rendimiento no sube, entonces
el cuello de botella no está en la 1ª capa.** Está aguas abajo — en los datos, el desbalance,
el contexto espacial. La interpretabilidad no reabre el veredicto de rendimiento: **le da un
mecanismo**.

**En una frase para el viernes:** *"El mismo experto elige la misma morfología en todas las
slides, incluidas las negativas — porque detecta tejido, no clase. Que la especialización sea
real y aun así no mueva la métrica es justamente la evidencia de que el cuello no está en la
primera capa, sino en el dato."*

---

## Bloque 4 — La mecánica del tensor (30×16×10×16, cabezas, slots, MoE≠PoE)  ✅

Este es el bloque denso — el que se cayó bajo presión en la reunión. Lo construimos de a un
concepto. (Fuente: `respuestas_preguntas_benjamin.md` §0/§Q1/§Q2/§Q4/§Q5, citado al código.)

**El tensor, leído de izquierda a derecha.** `slot_embeds = [30, 16, 10, 16] = E × H × S × P`:
**30 expertos**, cada uno con **16 cabezas**, cada cabeza con **10 slots**, cada slot es un
**vector-prototipo de 16 dimensiones**. Total de prototipos = E·S = **300 slots** (los "300"
del deck).

**Por qué el 16 aparece dos veces (la trampa que confunde).** El primer 16 = **nº de
cabezas**. El último 16 = **dimensión de cada prototipo**, y sale de `slot_dim / H = 256/16 =
16`. Tienen que ser iguales **porque el ruteo compara prototipo contra query con un producto
interno** — y un producto interno exige que ambos vectores vivan en el mismo espacio de 16.
No es casualidad: es la condición para poder multiplicarlos.

**Qué es una cabeza (Q1 — la que respondiste con "textura/forma/color").** Honestidad: **NO**,
las cabezas **no** están pre-asignadas a textura/forma/color. El query de 256 se parte en **16
trozos de 16**, y cada cabeza corre **su propio ruteo en paralelo** sobre su trozo — es
**exactamente** multi-head attention: cada cabeza mira un **subespacio aprendido** del
embedding. Nadie le dice a la cabeza 3 "sos textura"; son subespacios **emergentes, sin
semántica impuesta**. La semántica reconocible (epitelio, estroma…) **no vive en las cabezas,
vive en los slots/expertos** (Bloque 2). Decir esto **corrige** la respuesta de la reunión y
suena mucho más sólido que improvisar.

**El forward en 6 pasos (para narrarlo, no para recitarlo).** query `q = norm(W_q·z)`
[N,256] → se parte en 16 cabezas [N,16,16] → se compara con los prototipos por producto
interno → **softmax de ruteo** (reparte cada parche entre slots) → **slots** = promedio
ponderado de parches → **expertos de bajo rango** (`z = LN(ReLU(W_low·Φ·u))`) → concat de
cabezas [300,512]. En drop-in (`keep_slots=False`) un **segundo softmax** recombina los 300
slots y reconstruye los N parches → la salida es idéntica en forma a un `Linear(512,512)`.
Por eso es **drop-in**: reemplaza una sola capa de CLAM, nada más.

**MoE ≠ PoE (Q4).** ⚠️ El paper **no** menciona PoE — esto es razonamiento arquitectónico,
decirlo así. **MoE** = combina expertos **sumando** (dos softmax que suman 1 → mezcla convexa);
cada experto se especializa en una región y el router decide *cuánto* aporta. **PoE** = combina
**multiplicando** distribuciones (cada experto es un **veto**), necesita un normalizador
**intratable** (contrastive divergence) y modela una *distribución de probabilidad*, no una
*transformación de features*. MAMMOTH es aditivo por construcción → PoE rompería la
formulación y reintroduciría la inestabilidad de entrenamiento que MAMMOTH justamente evita.
Frase: *"Es MoE porque suma contribuciones suaves —estable y entrenable—; PoE las multiplica
como vetos, necesita un normalizador intratable y modela probabilidades, no features."*

**¿Por qué 16 cabezas? ¿Cuántas para mama? (Q5 — gran pregunta).** 16 es un **hiperparámetro**,
el default estable del paper (bajar a **1 cabeza cuesta −5.4%**; la banda buena es
**H∈{8,16,32}**), **no** un número derivado de la biología de la mama. Restricción dura: H
debe dividir a 512 y 256. **Para mama no hay número principista** — y esto **no es ignorancia
nuestra**: el **propio paper marca el E/S/H fijo como LIMITACIÓN** (§6) y deja "elegirlos
dinámicamente" como trabajo futuro. Que Benjamín lo preguntara toca un límite reconocido del
método. La respuesta de verdad = **ablación de H** en nuestras tareas de mama (paired,
H∈{8,16,32}) + ver si más cabezas se especializan más o se vuelven redundantes.

**En una frase para el viernes:** *"El 30×16×10×16 son los prototipos: 30 expertos × 16
cabezas × 10 slots × 16 dims; el 16 aparece dos veces porque cabezas y dimensión-de-prototipo
coinciden para poder compararlos con producto interno. Las cabezas son subespacios aprendidos
tipo multi-head, no textura/forma/color; la semántica vive en los slots. Es MoE (suma suave),
no PoE (producto/veto). Y 16 cabezas es el default estable del paper — cuántas para mama es
una pregunta abierta que el propio paper deja como trabajo futuro."*

---

## Bloque 5 — Honestidad + guion (no sobre-vender)  ✅

**Las limitaciones, dichas de frente (esto suma credibilidad, no la resta).**
- **Alcance chico**: 4 slides, **una sola tarea** (cdis), **un solo fold** (f0). Es una
  cala cualitativa, no un estudio sistemático.
- **Etiquetas provisionales**: la lectura morfológica (e8 epitelio, e26 estroma…) es **mía,
  no de un patólogo**. La hipótesis OBJ-A pide **sign-off de Sebastián/patólogo** antes de
  afirmar tejido con certeza — eso es lo que cierra la métrica de la regla 9. Solo inspeccioné
  a fondo e8/e26/e3/e15; los 30 están en el contact sheet para revisión.
- **Color del heatmap = percentil por experto**: sirve para ver estructura relativa (qué
  regiones prefiere un experto), **no** magnitud absoluta ni "cuál experto se usa más". Para
  eso está `expert_usage.csv`, que sale **casi uniforme** (Bloque 3: ni expertos muertos ni
  acaparadores).
- **Solapamiento entre expertos**: esperado con ruteo suave + top-k. No es defecto.

**El encuadre que evita el malentendido (repetir explícitamente en la reunión).** Son dos ejes
**ortogonales**: *"¿mammoth mejora la métrica?"* está **cerrado: no** (Hallazgo 12, 0
palancas) — eso **no** se toca. *"¿qué aprende y mira por dentro, tiene sentido clínico en
mama?"* está **abierto** y es lo que Benjamín pidió. Presentar interpretabilidad **no reabre**
el veredicto de rendimiento; le da un mecanismo. Decirlo así de entrada evita parecer que
revivimos algo cerrado.

**El arco del guion para el viernes** (cómo encadenar los bloques):
1. **Mecanismo** (Bloque 4, apoyado en las slides B5 reusadas 4/7): qué reemplaza mammoth y
   qué es el tensor — dominarlo esta vez.
2. **Qué miran los expertos** (Bloque 2): heatmap = dónde, top-k = qué morfología. Mostrar las
   figuras.
3. **El hallazgo fino** (Bloque 3): morfología ≠ clase → detector de tejido → **por eso
   confirma que el cuello es el dato, no la 1ª capa**.
4. **Honestidad** (este bloque): alcance chico, etiquetas provisionales, sign-off pendiente;
   ejes ortogonales.

**En una frase para el viernes:** *"Lo que traigo es evidencia de qué mira mammoth por
dentro, no una mejora de métrica —eso está cerrado—; es una cala cualitativa de 4 slides con
etiquetas que todavía necesitan el visto bueno de un patólogo, pero ya muestra que los
expertos detectan tejido de forma estable y clínicamente coherente."*
