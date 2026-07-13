# Auditoría de coherencia — sesión DECK (pulido magnif + slide 7) + reunión Sebastián (13-jul-2026)

> Registra los avances y hallazgos de la sesión del 13-jul (pulido de la sección magnificación
> del deck + mejora de la slide 7 del diagrama central) y la **reunión con Sebastián** (deck
> presentado, salió bien). Doc de hallazgos ANTES de los fixes (workflow `@knowledge-audit`).
> Branch: main (documental, GPU libre `squeue` vacío, `origin/main` sincronizado).
> Continúa `hallazgos_sesion_deck_magnif_12jul.md`.

## Resumen (id · hallazgo · tipo · acción)

| id | hallazgo | tipo | acción |
|---|---|---|---|
| S1 | **Deck magnif comprimido 6→4 slides** (elim slide 17 diseño-pareado; **fusión** 13 contexto + 15 hallazgo físico en una); deck **17→15**. + limpieza de estilo (fuera «—» y «palanca» en la sección) | progreso | `convenciones_deck_b6.md` §8 + `current.md` (hechos); registrar |
| S2 | **Slide 7 mejorada**: notas reescritas (narración completa `x_i → W → x̄ → ruteo → x ponderada → slots → Φ·W_low → concat → CLAM` + respuesta **MoE-vs-PoE**); pipeline al pie relabel **`z`→`x_i`** + paso `ruteo` explícito | progreso | `convenciones_deck_b6.md` §7 (hecho); registrar |
| S3 | **CRÍTICO — honestidad interpretabilidad:** los nombres de tejido (e8 epitelio tumoral / e26 estroma / e3 ductal) son **interpretación VISUAL nuestra, NO ground truth**. Sí tenemos la etiqueta **clínica de slide**; NO hay anotación de tejido por parche. El argumento "morfología≠clase" es **LABEL-INDEPENDIENTE** (mismo experto sobre el mismo patrón en 4 slides de etiqueta distinta) → se sostiene aunque el nombre sea impreciso. Sign-off de patólogo **pendiente**. | reconciliación/riesgo | reforzar [[mammoth-interpretabilidad-objA]] + caveat corto en CLAUDE.md Hallazgo 12 |
| S4 | **Provenance del deck (¿qué es nuestro?):** las figuras del paper (Fig 1 t-SNE, Fig 2 arquitectura, Fig 3 ruteo→fenotipo) son **de Shao et al. ICLR 2026, NO nuestras** (van como imagen, excepción); los heatmaps de ruteo + top-k + cross-slide (slides 10-11) **SÍ son nuestros** (`scripts/mammoth_interpretability.py`, 30-jun, nuestro checkpoint sobre TCGA-E2-A14Q). | contexto/nuevo | nota en [[mammoth-interpretabilidad-objA]] |
| S5 | **Error corregido:** el pipeline al pie de la slide 7 rotulaba el encoder-output como **`z`**, pero la Fig 2 del paper lo llama **`x_i`** y el caption dice "variables de la figura" → «z» era inconsistente. Corregido a `x_i`. | error | `convenciones_deck_b6.md` §7 (hecho); registrar |
| S6 | **Feedback nuevo de Ernesto (estilo de deck/prosa):** **cero guiones largos «—»** (los lee como tell de IA) + **evitar la palabra «palanca»**. Refina/override de `@humanizer-es` §14 (que marca la raya como "NO constraint-cero, la casa la usa"): para los decks de Ernesto SÍ es constraint-cero. | feedback | memoria nueva `[[deck-estilo-sin-rayas-ni-palanca]]` + clause concisa en el skill humanizer |
| S7 | **Contexto reunión 13-jul (Sebastián):** el deck se **presentó y salió bien**. Los **objetivos del sprint 7** (hablados por Sebastián) y las **correcciones de slides** (de Sebastián + las de Ernesto) los aportará Ernesto **la próxima sesión** como contexto. Gate (d) sin cambio operativo: **NADA lanzado a GPU**. NO asumir el resultado de la co-firma (b) ni lanzar sin OK explícito. | contexto | ADDENDUM [[magnificacion-cpathagent-proxima-direccion]] + `current.md`; el handoff prepara la próxima sesión |
| S8 | Agentes/skills: `reviewer`/`trainer` no se re-invocaron (sesión de deck/prosa, sin modelo/training/GPU). Único cambio de skill = clause de S6 en humanizer. | OK | annotate humanizer |

## Detalle por hallazgo

### S1 — Deck magnif comprimido (6→4 slides) + limpieza de estilo
- Pedido de Ernesto: eliminar la slide 17 (diseño pareado + expectativa honesta) y **fusionar** la
  13 (contexto: detectar vs localizar) con la 15 (hallazgo físico µm/px) en **una sola** de dos
  columnas. Además: **fuera todos los «—»** (reemplazados por «,», «:», «·») y **fuera «palanca»**.
- Hecho: nueva slide 13 de dos columnas (izq. detectar/localizar, der. tabla µm/px compacta),
  slide 14 patología con separadores «·» en las citas, slide 15 (era 16) decisión de escalas.
  Deck **17→15**. Re-QA LibreOffice **4/4** (12-15), sin solapes, sin «—» ni «palanca» en contenido.
- **Alcance respetado:** solo la sección magnif (líneas ≥734); las 11 slides de mammoth quedaron
  intactas (aún conservan sus «—»; ver S6 para el override de estilo, no aplicado a 1-11 sin pedido).
- Canónico: `convenciones_deck_b6.md` §8 (mapa nuevo + nota 13-jul) + `current.md`.

### S2 / S5 — Slide 7 (diagrama central) mejorada + notación alineada a la figura
- Pedido: mejorar las notas del presentador de la slide 7 (Fig 2 del paper) para (i) responder
  **por qué MoE y no PoE** y (ii) narrar el pipeline con **las variables del paper**, dejando
  clara la cadena `x_i → x ponderada → ruteo` que faltaba.
- Hecho: notas reescritas (guion hablado) recorriendo `x_i → W → x̄ (por cabeza) → ruteo
  (producto interno + softmax) → x ponderada = promedio ponderado que llena cada slot → Φ·W_low →
  cross-head concat → CLAM`. **MoE-vs-PoE**: suma convexa de dos softmax (=mezcla, estable) vs
  producto/veto con normalizador intratable (=PoE, modela probabilidad no features). **Caveat de
  honestidad EN las notas: el paper NO menciona PoE** (razonamiento arquitectónico, regla 5).
- **S5 (error):** el pipeline al pie rotulaba `z` el encoder-output, pero la Fig 2 usa `x_i` y el
  caption dice "variables de la figura". Corregido: `x_i[N,512] → W→x̄[N,16,16] → ruteo(sim+softmax)
  → slots s(300) → Φ·W_low[300,512] → concat[N,512] → CLAM(logits)`. Re-QA slide 7 OK.
- Fuente de la respuesta: `sprints/B5_sprint5/mammoth_entendimiento/respuestas_preguntas_benjamin.md`
  §Q4 (MoE-vs-PoE) + §0 (tabla de dimensiones). Canónico deck: `convenciones_deck_b6.md` §7.

### S3 — CRÍTICO: honestidad de la interpretabilidad (nombres de tejido = lectura visual nuestra)
- Al preparar el guion surgió la pregunta de Ernesto: en las figuras de expertos, ¿teníamos la
  etiqueta de la slide y **sabemos** que es epitelio tumoral / estroma / ductal? Verificado contra
  los archivos:
  - `expert_usage.csv` = solo índice de experto + score de uso (sin tipo de tejido).
  - `scripts/mammoth_interpretability.py` **no asigna** nombres de tejido (grep vacío).
  - Los rótulos "e8 → epitelio tumoral / e26 → estroma / e3 → ductal" son **strings escritos a mano
    en el deck** (`generate_b6_deck.py` slides 10-11), a partir de mirar los parches top-k.
  - `meta.json` sí trae la etiqueta **clínica de slide** (`y_true=1, y_pred=1, prob=0.98`, tarea cdis).
- **Conclusión durable:** tenemos la etiqueta de slide (clínica); NO tenemos anotación de tejido por
  parche; los nombres de morfología son **interpretación nuestra, pendiente sign-off de patólogo**.
  El hallazgo "morfología≠clase" **no depende** de que el nombre sea exacto: se sostiene porque el
  **mismo experto** enciende el **mismo patrón** en 4 slides de etiqueta distinta (label-independiente).
- **Riesgo a evitar** (sobre todo de cara a la presentación con Benjamín): NO presentar "e8 = epitelio
  tumoral" como hecho anotado. Framing honesto: *"cada experto se especializa consistentemente en un
  patrón de tejido; nosotros nombramos esos patrones por inspección, y falta el sign-off de patólogo."*
- La memoria [[mammoth-interpretabilidad-objA]] ya decía "etiquetas provisionales (mías, no de
  patólogo)"; se refuerza con el matiz label-independiente + que se usaron en el deck.

### S4 — Provenance del deck (qué es nuestro vs del paper)
- Figuras del paper (imagen, excepción a "todo nativo"): Fig 1 t-SNE + barras, Fig 2 arquitectura,
  Fig 3 ruteo→fenotipo → **Shao et al., ICLR 2026** (`papers/mammoth_shao_iclr2026.pdf`). NO nuestras.
- Nuestros outputs (slides 10-11): `heatmap_montage.png`, `topk_subset_6experts.png`,
  `expert_08/26_crossslide.png` → generados por `scripts/mammoth_interpretability.py` (30-jun) con
  nuestro checkpoint mammoth (config CONCH 512, 30 expertos) sobre una WSI H&E real (TCGA-E2-A14Q).
- **No hay ninguna radiografía/mamografía en el deck** — todo es histopatología H&E.

### S6 — Feedback de estilo de deck/prosa (nuevo)
- Ernesto: quitar **todos** los guiones largos «—» de decks/prosa (los lee como tell de IA) y
  **no usar la palabra «palanca»**. Aplicado a la sección magnif (12-15) y a lo nuevo de la slide 7.
- **Reconciliación con `@humanizer-es`:** el skill (§14) dice que la raya "NO es constraint cero, la
  casa la usa". Para los decks de Ernesto SÍ es constraint-cero → es un **override de proyecto**, no
  una contradicción (el skill marca el abuso rítmico; Ernesto lo lleva a cero por preferencia).
- **NO aplicado a las slides 1-11 de mammoth** sin pedido explícito (regla dura del handoff). Quedan
  con sus «—» de citas/títulos; si Ernesto lo pide, se extiende.

### S7 — Reunión con Sebastián (13-jul) y qué queda para la próxima sesión
- El deck `CLAM_Reunion_Mammoth.pptx` (15 slides: 11 mammoth + 4 magnif) se **presentó a Sebastián**
  y la reunión **salió bien**.
- **Pendiente de documentar la próxima sesión (Ernesto lo aporta como contexto):** (1) los
  **objetivos del sprint 7** hablados por Sebastián; (2) las **correcciones/consideraciones de las
  slides** mencionadas por Sebastián **y** las de Ernesto, para mejorar la presentación de cara al
  sprint 7 (donde también la verá **Benjamín**).
- **NO asumir** el resultado de la co-firma de escalas (gate b) ni lanzar el multi-escala:
  **NADA en GPU**; el pipeline B6 sigue armado (stage-2 + stage-3 encadenable) y solo se lanza con
  OK explícito de Ernesto. [[surface-premise-discrepancies]].

### S8 — Agentes / skills
- Sesión de deck/prosa, sin tocar modelo/training/data-pipeline → `reviewer` y `trainer` no se
  re-invocaron. Único cambio: clause concisa en el skill `@humanizer-es` por S6.

## Guardarraíles respetados
- Read-only sobre `clam_environ/` (solo lectura de la WSI/h5 para verificar provenance) y
  `clam_testing/`; escritura solo bajo `clam_testing2/` y memorias en `~/.claude/`.
- Sin GPU, sin `sbatch`, sin tocar jobs (`squeue` vacío). `B7_sprint7/` (binarios pesados de
  Ernesto) NO se toca ni se commitea.
- Ediciones a memorias/CLAUDE.md = ADDENDUM/clause aditivo (no reescriben pre-registro ni reglas).
