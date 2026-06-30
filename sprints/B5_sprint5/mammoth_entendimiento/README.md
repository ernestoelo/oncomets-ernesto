# MAMMOTH — entendimiento + interpretabilidad (apertura tras reunión 29-jun-2026)

> Abierto el **29-jun-2026** tras la reunión semanal con **Benjamín, Sebastián y
> Fernando**. Recoge el feedback de Benjamín sobre la presentación B5 de MAMMOTH,
> deja constancia del trabajo de entendimiento hecho, y propone los **objetivos del
> próximo sprint** que salen de sus preguntas.
>
> **Documento técnico hermano (el material de estudio):**
> [`respuestas_preguntas_benjamin.md`](respuestas_preguntas_benjamin.md) — responde,
> aterrizado en paper + código, cada pregunta que no supimos contestar.

---

## 1. Contexto de la reunión

Benjamín dijo que **no dominaba MAMMOTH lo suficiente** y que necesita dedicarle más
tiempo para **poder explicarlo de forma que hasta un niño de 14 años lo entienda**.
Pidió alcanzar un entendimiento real del mecanismo (no solo "uso mammoth"). Surgieron
varias preguntas que **no supimos responder bien** y quedaron como deuda para la
**presentación del sprint siguiente**.

## 2. Comentarios de Benjamín (registrados textualmente, para no perderlos)

1. **"No dominaba MAMMOTH"** — hay que dedicarle más tiempo y poder **explicarlo a
   nivel de un niño de 14 años** sin que sepa del tema. (Que no se note que no lo
   manejamos a fondo.)
2. **Formato (.ppt) de las slides de objetivos.** *"El formato de nuestros objetivos
   del sprint, tanto los hechos como los propuestos, no es el adecuado, y que no vuelva
   a pasar"* — Benjamín se enojó bastante. **"Recuperar la fuente tal cual del
   original"** = aquí **"fuente" es TIPOGRAFÍA** (no "source"/paper): las slides de
   objetivos usaron **letra / color / tamaño** que no matcheaban el **template original
   del deck**. (Confirmado por Ernesto, 29-jun.) → Acción: las slides de objetivos
   deben respetar **exactamente** la tipografía/paleta/tamaños del branding del deck —
   ver `presentacion_b5/convenciones_deck_b5.md` (fuentes 24-30, header teal, etc.) y
   [[deck-completo-pptx-buildable]]. Es un problema de **formato visual del .ppt**, NO
   de contenido ni de fidelidad al paper. (Objetivo OBJ-E en §4.)
3. **"¿Qué significa cada cabeza?"** — En la reunión respondí *"podría ser textura,
   forma, color…"* y al repreguntar **dije que no sabía** si cada feature de la cabeza
   representa eso. Benjamín pidió **investigarlo para estar seguros**. → Respuesta en
   [respuestas §Q1]: **NO** por construcción; son subespacios aprendidos; la semántica
   morfológica está en los **slots/expertos**, no en las cabezas.
4. **Dimensiones del vector S (30×16×10×16).** Benjamín **no entendía cómo calzaba** y
   pidió que la **interpretabilidad de esas dimensiones** se pueda mapear a expertos /
   cabezas / slots. → Respuesta en [respuestas §0 y §Q2]: `slot_embeds = E×H×S×P =
   30×16×10×16` (prototipos de slot).
5. **Explicar el diagrama original del paper.** No mencioné **las dimensiones de las
   variables de entrada en cada paso** del diagrama que pusimos después del nuestro.
   Hay que hacerlo: el diagrama ayuda visual, pero **falta narrar las dimensiones en
   cada etapa**. → Tabla maestra en [respuestas §0]; checklist en [respuestas §8].
6. **Los 3 cuadros de colores distintos que se dividen en cada experto** — qué
   significan, qué representa cada slot, y **qué operaciones hay entre medio con sus
   dimensiones**. → Respuesta en [respuestas §Q3] (leyenda de la Fig 2 + cadena
   interna del experto). Queda **pendiente confirmar cuál de las dos lecturas** quería.
7. **"¿Por qué MoE y no PoE?"** — lo estudiamos pero no recordamos el porqué. →
   Respuesta en [respuestas §Q4]. **OJO: el paper NO menciona PoE** → es razonamiento
   arquitectónico, hay que decirlo así.
8. **"¿Por qué 16 cabezas? ¿Cuántas deberían existir para cáncer de mama?"** — nos lo
   preguntó a todos y **nadie pudo responder**. Siento que sin entender el mecanismo
   de las cabezas, el "16" parece un hiperparámetro sin relevancia — y Benjamín hizo
   un vuelco en mi forma de pensarlo. → Respuesta en [respuestas §Q5]: 16 = default
   estable del paper (bajar a 1 = −5.4%); **para mama es pregunta abierta que el
   propio paper marca como limitación** (§6).
9. **Interpretabilidad de expertos/slots** — Benjamín fue **enfático**: estudiar en
   qué se fijan para determinar cierta zona importante. Se relaciona con el punto 3.
   → Respuesta + herramienta lista en [respuestas §Q6] (la librería trae el tutorial
   de visualización: heatmaps por experto + top-k parches).

## 3. Estado del entendimiento (constancia de avance — 29-jun-2026)

**Hecho en esta sesión** (todo verificado contra paper + código, regla 5):
- ✅ Resuelto el **30×16×10×16** = `slot_embeds` (prototipos), con la traza completa
  de dimensiones paso a paso ([respuestas §0]).
- ✅ Aclarado **qué es una cabeza** (subespacio multi-head, NO textura/forma/color) y
  **dónde vive la semántica** (slots/expertos, validado por patólogos en Fig 3).
- ✅ **MoE vs PoE** argumentado (con la marca de que el paper no discute PoE).
- ✅ **16 cabezas** justificado (default estable, ablación −5.4%); "cuántas para mama"
  identificado como **pregunta abierta del propio paper** (§6).
- ✅ Localizada la **herramienta de interpretabilidad** ya existente en la librería.
- ✅ Verificado que **nuestro guion del deck ya explica bien las dimensiones** (líneas
  92-122) — la falla fue de **ensayo/verbalización**, no de material.

## 4. Objetivos propuestos para el próximo sprint (anclados a la fuente)

> Formato source-anchored (respuesta al feedback 2): cada objetivo cita el lugar
> exacto del paper/código que lo motiva. Argumento antes de código (regla 9) +
> reviewer donde toque modelo/harness.

### OBJ-A — Interpretabilidad de expertos/slots en MAMMOTH sobre mama *(prioridad de Benjamín)*
- **Qué**: correr `tutorial_mammoth_visualization.py` sobre nuestros checkpoints
  mammoth ya entrenados (jobs B5: 4229/4243/4246/4387/4400) → heatmaps por experto +
  top-k parches por experto/slot sobre WSIs de mama.
- **Fuente**: paper Fig 3 + §5.2; código `examples/tutorial_mammoth_visualization.py`.
- **Hipótesis (regla 9)**: los slots/expertos se especializan en morfologías
  reconocibles de mama (epitelio, estroma, calcificación, linfocitos). Métrica =
  **coherencia morfológica cualitativa** de los top-k (idealmente sign-off de
  Sebastián/patólogo), NO una métrica de accuracy (eje ortogonal al "0 palancas").
- **Costo**: Etapa 0, **CPU, post-hoc**, sin reviewer. Insumo: `.svs` + `h5_files`.
- **Responde**: preguntas 3, 6, 9 con **evidencia visual** (convierte los "no sé").

### OBJ-B — Ablación del nº de cabezas (H) en tareas de mama
- **Qué**: ablación paired de `H∈{8,16,32}` sobre 1-2 tareas de mama, mismos splits.
- **Fuente**: paper §5.3 + Tabla 4a (16→1 = −5.4%; H∈{8,16,32} estabiliza) + §6
  (limitación "fixed config… of heads").
- **Hipótesis (regla 9, pre-registrar)**: si 16 NO es el mejor para mama, esperamos
  ver el óptimo desplazado; si la interpretabilidad (OBJ-A) muestra que más cabezas
  no añaden especializaciones distintas, esperamos saturación. Métrica = balanced_acc
  media±std + lectura de interpretabilidad. **Pre-registrar dirección esperada** (9.a).
- **Responde**: pregunta 8 ("cuántas cabezas para mama") con **datos**, no opinión.
- **Gate**: GPU vía sbatch + cortesía single-GPU; reviewer (toca config del modelo).

### OBJ-C — Explicación de MAMMOTH con el diagrama original + dimensiones
- **Qué**: rehacer la explicación de MAMMOTH para la próxima presentación con (i) la
  **Fig 2 original del paper** + su leyenda, (ii) **dimensiones anotadas en cada paso**
  (tabla §0), (iii) las 3 frases cortas (MoE/PoE, cabezas, cabezas≠features), (iv)
  ensayo en voz alta del guion existente.
- **Fuente**: [respuestas §8] (checklist) + feedback 5 (no narrar las dimensiones).
- **Responde**: feedback 1, 5, 6. *(Esto es CONTENIDO; el formato visual va en OBJ-E.)*

### OBJ-D *(opcional, si Benjamín lo pide)* — "explícalo a un niño de 14"
- Versión ultra-simplificada (analogía de los 30 traductores + recepcionista, ver
  [respuestas §2]) para abrir la slide, antes de bajar al detalle técnico.

### OBJ-E — Formato (.ppt) de las slides de objetivos *(feedback 2 — se enojó)*
- **Qué**: corregir la **tipografía / color / tamaño** de las slides de objetivos
  (hechos y propuestos) para que matcheen **exactamente** el template/branding del
  deck. Aplica a TODAS las slides de objetivos, no solo a mammoth.
- **Fuente**: `presentacion_b5/convenciones_deck_b5.md` (fuentes 24-30, header gris +
  cuadrado teal + logo, paleta) + [[deck-completo-pptx-buildable]] +
  [[diagramas-arquitectura-pptx-editable]].
- **Responde**: feedback 2 ("recuperar la fuente/tipografía tal cual del original").
  Es **formato visual**, no contenido. **Que no vuelva a pasar.**

## 5. Pendiente / a confirmar con Benjamín (no asumir)

- **Formato de objetivos (feedback 2) — RESUELTO 29-jun**: NO era fidelidad al paper;
  era el **formato visual del .ppt** (tipografía/color/tamaño) de las slides de
  objetivos, que no matcheaba el template original. Ver OBJ-E. (Queda confirmar con
  Benjamín si hay un template/fuente exacta de referencia que quiere que usemos.)
- **Los "3 cuadros de colores" (feedback 6)**: confirmar cuál de las dos lecturas de
  [respuestas §Q3] quería (3 verdes = particiones, vs Φ/W_low/Nonlinearity).
- **OBJ-B**: confirmar con Sebastián la cortesía de GPU (hay jobs ajenos corriendo) y
  el sign-off de la formulación antes de lanzar.

## 6. Reglas que gobiernan estos objetivos
Containment (`clam_testing2/`), `clam_environ/` READ-ONLY, GPU solo vía `sbatch` +
cortesía single-GPU, **argumento antes de código + reviewer** donde toque modelo
(OBJ-B), interpretabilidad post-hoc es Etapa 0 sin reviewer (OBJ-A). El eje
**entendimiento/interpretabilidad es ORTOGONAL** al "0 palancas" (Hallazgo 12) — NO
es reapertura 9.b. Push lo autoriza Ernesto.
