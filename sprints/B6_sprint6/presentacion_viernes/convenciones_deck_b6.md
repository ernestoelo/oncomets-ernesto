# Convenciones del deck del VIERNES (B6) — formato B4 + contenido mammoth/OBJ-A

> **Sprint B6.** Deck para la reunión del **viernes 10-jul** con Benjamín. Eje =
> **entendimiento/interpretabilidad** de mammoth (su pedido del 29-jun), NO rendimiento.
> **Formato = deck B4** (el que Benjamín validó); **contenido = mecanismo mammoth de B5 +
> interpretabilidad OBJ-A (nuevo)**. Este doc fija los params de formato extraídos del
> volcado real de `CLAM_Sprint_B4.pptx` (regla 5, no inventados).

---

## 0. Por qué existe este doc (hallazgo de la recon 9-jul)

Benjamín se enojó con el formato del deck B5 el 29-jun ("recuperar la fuente tal cual del
original"; **"fuente" = TIPOGRAFÍA**, [[feedback-benjamin-entender-mammoth]] ítem 6). El
volcado comparado B4 vs B5 localiza **empíricamente** la deriva — dos causas concretas:

| Dimensión | **B4 (correcto)** | **B5 (rechazado)** |
|---|---|---|
| Tamaño de página | **10.0 × 5.625 in** | 13.333 × 7.5 in |
| Fuente de contenido | **Barlow ExtraBold** (títulos) / **Barlow** (cuerpo) / **Aptos** (diagramas) | **Carlito** domina (326 runs) + Cambria Math + Arial |
| Tamaños | limpios: 32-36 (título), 24 (cuerpo), 48 (divisoria) | caóticos: 8pt domina + decenas fraccionarios (6.29, 8.51, 9.61…) |
| Teal título | `#217589` | `#217589` (esto sí se preservó) |

**Causa raíz** (documentada como decisión *intencional* en `REFERENCIA_branding_environ.md`
§4): B5 se construyó a 13.333×7.5 *"para embeber los diagramas sin reescalar"*. Ese atajo es
lo que rompió el match: los diagramas entraron a tamaño nativo en **Carlito** con tamaños
escalados fraccionarios, en vez de contenido nativo en **Barlow** a los tamaños limpios de B4.

**Decisión B6 (Ernesto, 9-jul):** construir a **10×5.625 como B4**. Los diagramas de
arquitectura (13.333×7.5) se **re-escalan** al insertarse, o se re-generan al canvas chico.

---

## 1. Formato canónico B4 (target del deck B6)

- **Tamaño de slide:** `10.0 × 5.625 in` (16:9). *(python-pptx: `prs.slide_width=Inches(10)`,
  `prs.slide_height=Inches(5.625)`.)*
- **Un solo layout** en el master de B4 (`DEFAULT`) → las slides se arman con **shapes
  manuales** sobre slide en blanco (mismo patrón que `generate_b5_deck.py`). No hay
  placeholders que reusar.

### Tipografía (lo que Benjamín quiere "tal cual")

| Rol | Fuente | Tamaño | Color |
|---|---|---|---|
| Título de contenido | **Barlow ExtraBold** (bold) | **32 pt** (36 pt si prominente) | `#217589` |
| Cuerpo / bullets | **Barlow** (bold) | **24 pt** | `#595959` |
| Anotaciones de diagrama | **Aptos** | 8–13.5 pt | `#0F5F74` / tinta |
| Título divisoria | Liberation Sans / Arial (bold) | **48 pt** | `#CDD6F4` |
| Subtítulo divisoria | Calibri | **24 pt** | `#B8D4D9` |

> Regla dura: **el contenido va en Barlow**, no en Carlito. Carlito solo si se re-usa un
> diagrama generado por nosotros tal cual (y aun así, preferir re-escalar el diagrama entero).

### Paleta (valores reales del deck)

- Teal título `#217589` · Teal barra/acento `#31859C` · Teal divisoria (fondo) `#2E7E8F`
- Lavanda título divisoria `#CDD6F4` · Teal claro subtítulo `#B8D4D9`
- Gris cuerpo `#595959` · Gris header bar `#F2F2F2`
- Naranja acento / "lo nuevo" `#F06D2F` (variante `#E2723B`)
- Δ+ verde `#1E8449` · Δ− rojo `#C0392B` · ambiguo `#B9770E`

---

## 2. Arquetipos de slide (geometría exacta, del volcado B4)

### 2.1 Portada (slide 1)
- **Imagen full-bleed** `assets_branding/portada_fullbleed.jpg` cubriendo 10×5.625
  (en B4 la imagen mide 10.0×5.668, leve overscan; `L=0, T≈-0.02`).
- En B4 el título va **horneado en la imagen** (la slide solo tiene la foto). Si se quiere
  título editable, superponer un text box.

### 2.2 Divisoria de sección (slide 3)
- **Fondo de slide** relleno sólido `#2E7E8F` (es el `bg` de la slide, no un shape).
- Título centrado: text box `L=0.5 T=2.3 W=9.0 H=1.0`, 48 pt bold `#CDD6F4`, `CENTER`.
- Subtítulo centrado: text box `L=0.5 T=3.3 W=9.0 H=0.5`, 24 pt `#B8D4D9`, `CENTER`.

### 2.3 Contenido con header (slide 6/9)
Header (reutilizable tal cual en cada slide de contenido):
- **Barra gris**: AUTO_SHAPE `fill=#F2F2F2`, `L=0.28 T=0.0 W=9.66 H=0.785`.
- **Cuadrado teal**: AUTO_SHAPE `fill=#31859C`, `L=0.0 T=0.0 W=0.785 H=0.785`.
- **Logo**: imagen `assets_branding/logo_header.png` dentro del cuadrado,
  `L=0.064 T=0.042 W=0.654 H=0.645`.
- **Título**: text box Barlow ExtraBold `32 pt` (36 si prominente) `#217589`,
  `L≈0.95 T=0.15 W=8.84 H=0.63`, alineación izquierda/justify.
- **Región de cuerpo** (tabla/figura/bullets): `L≈0.25 T≈0.88 W≈9.3 H≈4.6`.

### 2.4 Notación + puntos clave (antes de un diagrama complejo)
- Cajas numeradas con óvalos naranja `#F06D2F` (patrón DSMIL, B4 slide 20). Anotaciones Aptos.

### 2.5 Diagrama de arquitectura
- `.pptx` editable (cajas redondeadas + flechas), estilo `Diagrama_CLAM.pptx`. **Se re-escala
  de 13.333×7.5 a 10×5.625** al insertar (o se re-genera al canvas chico).

Secuencia típica por tema: **divisoria → (notación/puntos clave) → diagrama → interpretabilidad**.

---

## 3. Contenido a reusar (decidido con Ernesto, 9-jul)

El deck B5 es del **25-jun**; OBJ-A se corrió el **30-jun** → **la interpretabilidad NO está
en B5**. De B5 se reusa el **mecanismo mammoth**; las figuras OBJ-A son **material nuevo**.

**Slides B5 a reusar (re-formateadas a B4):**
- **3** — MAMMOTH (divisoria de sección)
- **4** — MAMMOTH: qué es y por qué (mecanismo)
- **5 / 6** — Feature extractor CONCH / parches de la slide (background del pipeline)
- **7** — MAMMOTH: flujo de datos sobre la arquitectura oficial (diagrama)
- **8** — MAMMOTH: variante keep_slots (dónde se bifurca la salida)

**Material NUEVO (interpretabilidad OBJ-A)** — de
`sprints/B5_sprint5/mammoth_entendimiento/interpretabilidad/` (canónico, NO se mueve):
- `heatmap_montage.png` (30 heatmaps de ruteo — Fig 3.1)
- `topk_subset_6experts.png` (morfología top-k — Fig 3.2)
- `cross_slide/expert_{08,26,03,15}_crossslide.png` (un experto fijo en 4 slides)
- Guion = los 5 bloques de `../mammoth_interpretabilidad/estudio_reunion_viernes.md`.

**Figuras del paper disponibles** (van como imagen, excepción a la regla nativa):
`assets_branding/paper_figs/mammoth_fig1_overview.png`, `mammoth_fig3_routing.png`.

**FUERA para el viernes:** resultados mammoth (B5 slides 9/10/11 = "0 palancas" — NO presentar
"mammoth mejora"), PathPT (12-17), cierre/loss/próximos (18-21).

---

## 4. Reglas de build (de CLAUDE.md, vigentes)

- **Todo NATIVO** (tablas `add_table`, diagramas = shapes/spTree, gráficos `add_chart`);
  única excepción = figura de un paper (va como imagen). [[deck-completo-pptx-buildable]]
- **Diagramas de arquitectura editables** (.pptx shapes), no PNG matplotlib.
  [[diagramas-arquitectura-pptx-editable]]
- **Notas del presentador** = guion HABLADO en prosa, sin etiquetas de fase, sin nº de job
  ni nombres. [[notas-presentador-guion-didactico]]
- Baselines rotulados "Métricas oficiales Environ vX"; figuras/tablas sin nº de job.
- **QA visual**: rasterizar con LibreOffice engaña con OMML/Cambria Math (se ve roto, OK en
  PowerPoint) — comparar contra el original. [[pptx-qa-omml-libreoffice]]. Para diagramas
  propios: Carlito + Unicode plano (rasteriza limpio) — pero el **texto de slide va en Barlow**.

## 5. Motor de build — EJECUTADO (9-jul)

Build autocontenido en el sprint (repo limpio, decisión de Ernesto): **todo vive en
`sprints/B6_sprint6/presentacion_viernes/`** — script + deck + este doc.

- **Script**: `generate_b6_deck.py` (python-pptx en `.pylibs`). Reimplementa los arquetipos
  con geometría B4 (§1-2); helpers genéricos copiados del motor B5.
  ```
  PYTHONPATH=/media/administrador/Storage1/sdonoso/clam_testing2/.pylibs \
  /home/sdonoso/miniconda3/envs/clam_latest/bin/python \
    sprints/B6_sprint6/presentacion_viernes/generate_b6_deck.py
  ```
- **Deck**: `CLAM_Reunion_Mammoth.pptx` — **11 slides**, 10×5.625, contenido en Barlow.
- **Diagramas reusados** (nativos, editables) vía `copy_diagram_scaled` (escala geométrica
  **y tipográfica** ×0.75; 13.333×7.5 → 10×5.625, mismo aspect ratio):
  - s4 = `Diagrama_CLAM_mammoth.pptx` slide 0 (pipeline CLAM + CONCH + punto de integración)
  - s5 = `Diagrama_CLAM_mammoth.pptx` slide 1 (interior mammoth — **tensor 30×16×10×16**)
  - s6 = `Diagrama_mammoth_fused.pptx` slide 1 (keep_slots)
  Conservan Carlito/Unicode (convención de diagramas). El diagrama s4 trae fragmentos OMML/
  Cambria Math que **se ven rotos al rasterizar con LibreOffice pero están OK en PowerPoint**
  ([[pptx-qa-omml-libreoffice]]) — es el mismo diagrama presentado en B5.
- **Figuras** (imagen, excepción a la regla nativa): Fig 1 del paper (s3), heatmap_montage
  (s8), topk_subset_6experts (s9), cross_slide e8/e26 (s10).
- **Mapa de slides**: 1 portada · 2 divisoria MAMMOTH · 3 qué es y por qué · 4 pipeline ·
  5 interior/tensor · 6 keep_slots · 7 divisoria Interpretabilidad · 8 heatmaps · 9 top-k ·
  10 cross-slide (morfología≠clase) · 11 honestidad+cierre.
- **Notas del presentador**: guion hablado en prosa por slide (sin etiquetas de fase, sin
  nº de job ni nombres) — del estudio OBJ-A (Bloques 1-5).
- **QA (9-jul mañana)**: rasterizado con LibreOffice; verificadas 7/11 slides (portada, tarjetas,
  ambos diagramas escalados, top-k, keep_slots, cierre) — layout limpio, Barlow en contenido,
  diagramas escalaron sin distorsión. Scratch de QA borrado.

## 6. ADDENDUM 9-jul (tarde) — ronda de ediciones de Ernesto (supersede el mapa de §5)

Ernesto revisó el build de las 15:25 y pidió una ronda de cambios; aplicados y regenerados
(sigue en **11 slides**). Cambios:

- **s1 portada**: full-bleed limpia, sin panel ni overlay (título horneado en la imagen).
- **s2 NUEVA "Recapitulación de objetivos"**: molde **B4 exacto** = lista numerada en UN
  cuadro (título 32pt Barlow ExtraBold `#217589`; cuerpo `1.…2.…` 24pt Barlow bold `#595959`,
  línea entre ítems), **NO tarjetas** (Ernesto rechazó la versión con tarjetas →
  [[deck-molde-fiel-referencia]]).
- **s4 "qué es y por qué"**: título = **acrónimo completo** ("MAtrix-factorized Mixture Module
  of Transformation Heads", 17pt); quitada la tarjeta 4; **Fig 1 + Fig 3** del paper apiladas
  a la derecha (Fig 3 = colores↔expertos).
- **s6 interior/tensor**: **refactor a NATIVO** — tabla de dims (`add_table`) + panel de código
  real de `mammoth.py` (Consolas, fondo oscuro) lado a lado. Reemplaza el diagrama reusado.
- **s7 NUEVA (flujo sobre arquitectura oficial)**: `copy_diagram_scaled(DIAG_FUSED, 0, scale=0.72)`
  + traza de variables `z→q→⟨q,S⟩→D→u→o→h→CLAM` al pie (era la slide B5-s7 que faltaba).
- **s8 keep_slots**: **refactor a NATIVO** con math+código (tronco compartido → 2 ramas).
  Reemplaza el diagrama reusado.
- **s10/s11 fusiones**: heatmaps+top-k → una slide; cross-slide+honestidad/cierre → una slide.
- **Humanización**: `@humanizer-es` sobre títulos (quitados tells: "en paralelo",
  "del «dónde» al «qué»", "— y lo que falta") y una nota; sin nombres ni nº de job en el deck.
- **Helpers nuevos** en `generate_b6_deck.py`: `dims_table`, `code_panel`, `takeaway_bar`;
  `header(size=)` y `copy_diagram_scaled(scale=)` parametrizados; `content(size=)`.

**Mapa de slides VIGENTE**: 1 portada · 2 recap · 3 divisoria MAMMOTH · 4 qué es y por qué
(acrónimo) · 5 pipeline (reusado) · 6 interior math+código (nativo) · 7 flujo arquitectura
oficial (reusado + variables) · 8 keep_slots math+código (nativo) · 9 divisoria
Interpretabilidad · 10 heatmaps+top-k · 11 tejido≠clase + honestidad.

**Pendiente**: verificación fina en **PowerPoint** (no solo LibreOffice — OMML del diagrama
s5 se ve roto en LibreOffice pero OK en PowerPoint, [[pptx-qa-omml-libreoffice]]) + ensayo del
guion. Working tree con `generate_b6_deck.py` sin commitear (commit/push = decisión de Ernesto).

## 7. ADDENDUM 10-jul — ronda 2 de Ernesto (supersede lo aplicable de §6)

Ernesto revisó el build del 9-jul y pidió otra ronda; aplicada y regenerada (sigue **11 slides**).

- **s2 recap — estados tipo B3 + reescritura de objetivos.** Se añadió la **columna de estado**
  del molde B3: **check verde** (`assets_branding/check_verde.png`, extraído del deck B3 vía
  `status_done`) para lo cerrado, y **pill "En progreso"** (naranja `#E2723B`, `status_progress`)
  para lo abierto. Y sobre todo: los enunciados se reescribieron a los **objetivos REALES del eje**
  (pedido de Benjamín 29-jun: mecanismo + cabezas + interpretabilidad; ver
  `estudio_reunion_viernes.md` y [[feedback-benjamin-entender-mammoth]]) — **en infinitivo (sin 1ª
  persona), concisos y SIN resultados** (fuera "ninguno movió la métrica" y "el cuello de botella
  es el dato"; eso es conclusión, no objetivo). Estado actual: 1-2-3 cerrados (✓), 4
  interpretabilidad "En progreso" (falta sign-off de patólogo). Tipografía B4 24pt intacta.
- **s7 arquitectura oficial — figura sola, grande y limpia + pipeline en bloques.** Se **quitó
  el logo Environ y el título** y se **descartaron los callouts** que se montaban sobre las
  variables de la figura del paper. Ahora va la **Fig 2 del paper extraída**
  (`assets_branding/paper_figs/mammoth_fig2_arch.png`, 4375×1758, aspect 2.489) **a 9.42" de
  ancho, centrada**, con TODAS sus variables visibles (W, x̄, MoE, slots s, Φ, W_low, cross-head
  concat, slide embed, Patch-Slot similarity). Al pie, **pipeline en bloques** (`dim_pipeline`):
  `x_i[N,512] → W→x̄[N,16,16] → ruteo(sim+softmax) → slots s(300) → Φ·W_low[300,512] → concat[N,512] → CLAM(logits)`
  — con la **notación de la propia figura** (regla de Ernesto: referenciarnos en sus variables,
  también en las notas). Ya **no usa** `copy_diagram_scaled(DIAG_FUSED,…)`.
  > **Revisión 13-jul (pedido de Ernesto):** el 1er bloque se realineó de `z` a **`x_i`** (la figura
  > rotula el encoder-output como x_i, y el caption dice "variables de la figura" → «z» era inconsistente);
  > se explicitó el paso de **ruteo** entre x̄ y slots. **Notas de s7 reescritas**: narran el pipeline
  > completo `x_i → W → x̄ → ruteo → x ponderada (promedio ponderado que llena cada slot) → Φ·W_low →
  > concat → CLAM`, y responden **por qué MoE y no PoE** (suma convexa de dos softmax que suman 1 =
  > mezcla, estable/entrenable; PoE = producto/veto con normalizador intratable, modela probabilidad
  > no features). **Caveat honesto en las notas: el paper NO menciona PoE** (razonamiento arquitectónico,
  > regla 5). Fuente: `sprints/B5_sprint5/mammoth_entendimiento/respuestas_preguntas_benjamin.md` §Q4 + §0.
- **s11 tejido≠clase — imágenes agrandadas.** Las dos grillas cross-slide (e8, e26; 704×593, cada
  una = 4 slides × 5 parches) pasaron de ~1.9×1.6" a **~3.6×3.0" lado a lado** (`add_picture`
  explícito, centradas), con los 20 parches ya legibles. Texto compactado abajo + takeaway intacta.
- **Notas del presentador**: revisadas en las 11 slides; s7 reescrita para recorrer las variables
  de la figura + los bloques de dimensiones; s2 reescrita a los objetivos nuevos; framing "mammoth
  no mejora la métrica (cerrado) vs entender (abierto)" preservado en s1/s9/s11 (es el encuadre del
  Bloque 5, no un "resultado" del recap). Sin nombres ni nº de job.
- **Helpers nuevos**: `status_done`, `status_progress`, `dim_pipeline`; constante `FIG2_ARCH`.
- **Assets nuevos** (dentro del repo, sin commitear): `check_verde.png`, `mammoth_fig2_arch.png`.

**Mapa de slides VIGENTE (10-jul)**: 1 portada · 2 recap (objetivos + estados) · 3 divisoria
MAMMOTH · 4 qué es y por qué (acrónimo) · 5 pipeline (reusado) · 6 interior math+código (nativo) ·
7 **arquitectura oficial: figura grande + pipeline de dimensiones en bloques** · 8 keep_slots
math+código (nativo) · 9 divisoria Interpretabilidad · 10 heatmaps+top-k · 11 tejido≠clase
(imágenes grandes) + honestidad.

**Pendiente**: QA fino en **PowerPoint** (OMML del diagrama s5) + ensayo del guion.

## 8. ADDENDUM 12-jul — sección MAGNIFICACIÓN MULTI-ESCALA (reunión Sebastián, lunes)

Ernesto pidió **anexar** al mismo deck (`CLAM_Reunion_Mammoth.pptx`) una sección para la reunión
con Sebastián: qué se estudió, las **referencias** de los papers de microcalcificaciones, **imágenes
didácticas** de lo que se quiere hacer, y la **decisión de escalas** para que Sebastián guíe las
dimensiones. Es **aditivo**: NO toca las 11 slides de mammoth (se construye sobre la versión viva
del `.py`, con el WIP de la ronda 2 sin pisar).

> **Revisión 13-jul (pedido de Ernesto):** la sección pasó de 6 a **4 slides de contenido** (deck
> **11 → 15 slides**): se **eliminó la slide 17** (diseño pareado + expectativa honesta) y se
> **fusionaron la 13 (contexto) y la 15 (hallazgo físico) en una sola** de dos columnas. Además,
> limpieza de estilo: **fuera todos los guiones largos «—»** (tell de IA, reemplazados por «,», «:»
> o «·» según el caso) y **fuera la palabra «palanca»** en la sección magnificación. Solo se tocó
> la sección magnif (líneas ≥734); las 11 de mammoth quedaron intactas (aún conservan sus «—»).

**Slides de la sección (12-15):**
- **12** divisoria "Magnificación multi-escala".
- **13** "No es más zoom, es contexto: cohortes a distinta escala" (**fusión** de las viejas 13+15) —
  **columna izq.**: dos paneles nativos (detectar 20-40× vs localizar 5-10×), la etiqueta CAP es
  contextual; **columna der.**: el hallazgo físico, tabla µm/px compacta (TCGA ~40× → 59µm, privado
  ~20× → 119µm, HistAI sin MPP → excluida) + "la pirámide se define en µm/px, no en «level»".
- **14** "Lo que estudiamos: patología" — tabla nativa dos tipos de calcio (Tipo I oxalato invisible
  → techo; Tipo II visible) + **panel de referencias** (microcalc clínica + CPathAgent/DSMIL/DMMN/CONCH/CAP;
  separador «·», sin «—»).
- **15** "La decisión de escalas" (**LA slide para Sebastián**, era la 16) — esquema **nativo** de campos
  concéntricos (contexto 512µm ⊃ fino 112µm) + **crop REAL** a dos escalas + tabla px-por-cohorte
  (TCGA 482/2202, privado 241/1101) + fusión promedio → [N,512]. Pill "Decisión delegada: pido tu guía".

**Imagen didáctica (decisión de Ernesto): esquema nativo + crop real.** El crop real se genera con
`render_multiscale_crop.py` (read-only, openslide en CPU; reusa una coord de tejido de un `.h5`
existente; renderiza fino 112µm + contexto 512µm del **mismo centro** de una lámina TCGA-BRCA,
con la caja del campo fino dentro del contexto). Assets en `assets_branding/multiscale_crop/`
(gitignored).

**Helpers nuevos** en `generate_b6_deck.py`: `simple_table` (tabla nativa n-columnas), `panel`
(panel con título+cuerpo), `nested_fields` (esquema de campos concéntricos). Constantes `MSCROP/
MS_FINE/MS_CTX`. Todo nativo salvo el crop real (imagen). **QA (12-jul)**: rasterizado LibreOffice,
6/6 nuevas verificadas (tablas, paneles, esquema, crop, referencias) — layout limpio, Barlow en
contenido, sin solapes tras 2 pasadas de ajuste. **Re-QA (13-jul)** tras la fusión + limpieza de
estilo: 4/4 slides (12-15) verificadas, sin solapes, sin «—» ni «palanca» en contenido visible.

**Pendiente**: co-firma de Sebastián sobre las escalas (es el objetivo de la slide 15, ex-16) + QA en
PowerPoint + decisión de Ernesto sobre commitear (el `.py` bundlea el WIP de mammoth previo).
