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
- **QA (9-jul)**: rasterizado con LibreOffice; verificadas 7/11 slides (portada, tarjetas,
  ambos diagramas escalados, top-k, keep_slots, cierre) — layout limpio, Barlow en contenido,
  diagramas escalaron sin distorsión. Scratch de QA borrado.
