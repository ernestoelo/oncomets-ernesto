# Convenciones de construcción del deck B5 (registro canónico, versionado)

> **Qué es:** el registro —pedido vía `@knowledge-audit`— de las configuraciones a las
> que convergimos construyendo `CLAM_Sprint_B5.pptx` (3 rondas de feedback de Ernesto,
> 14-jun-2026). Vive acá (versionado) porque `papers/presentations/` está **gitignored**.
> Fuentes canónicas complementarias: regla en `CLAUDE.md` (§Formato de entregables) +
> memoria [[deck-completo-pptx-buildable]]. El `REFERENCIA_branding_environ.md` que está
> en `papers/presentations/` es una copia local de trabajo (no versionada).

## 0. Regla madre (lo que cambió respecto a B4)

El deck branded se construye **end-to-end con python-pptx** (no solo "assets que Ernesto
arma a mano"). Y **TODO es nativo de PowerPoint** — tablas reales, gráficos reales,
diagramas de bloques (shapes) — **NO imágenes matplotlib**. Única excepción legítima:
**figuras externas de un paper** (ej. Fig. 1 de PathPT), que sí van como imagen.

Razón: Ernesto pidió poder **agrandar/achicar y editar** todo en PowerPoint. Una imagen
de una tabla se pixela y no se edita; una tabla nativa sí.

## 1. Scripts y roles (reproducible)

| Script | Produce |
|---|---|
| `scripts/generate_b5_deck.py` | **ensambla el deck** end-to-end (17 slides) |
| `scripts/generate_clam_mammoth_pptx.py` | diagrama CLAM+MoE (slide 1 = integración, slide 2 = zoom MoE) |
| `scripts/generate_pathpt_pptx.py` | diagrama PathPT (slide 1 = arquitectura forward, slide 2 = 3 componentes) |
| `scripts/generate_b5_extra_assets.py` | (legado) PNG de respaldo; el deck ya NO los usa salvo la fig del paper |
| `papers/presentations/assets_branding/` | logos extraídos del B4 (`portada_fullbleed.jpg`, `logo_header.png`) + `paper_figs/` |

Entorno: `PYTHONPATH=/media/administrador/Storage1/sdonoso/clam_testing2/.pylibs`
(python-pptx vive ahí) + `/home/sdonoso/miniconda3/envs/clam_latest/bin/python`.

## 2. Branding (valores reales del B4)

- **Header de contenido** (compacto, alto 0.82"): barra gris `#F2F2F2` full-width +
  **cuadrado teal `#31859C` en la esquina** + **logo blanco** encima (`logo_header.png`,
  es un PNG con alpha → sobre blanco es invisible, por eso va sobre el cuadrado teal) +
  título **Barlow ExtraBold `#217589`** a 28pt.
- **Divisorias**: fondo teal `#2E7E8F`, título lavanda `#CDD6F4` 50pt, subtítulo
  `#B8D4D9` 22pt, logo blanco en la esquina.
- **Portada**: `portada_fullbleed.jpg` full-bleed + título blanco superpuesto arriba.
- Paleta de señal: verde `#1E8449`, rojo `#C0392B`, ámbar `#B9770E`, gris `#555`.
- Tamaño deck: **13.333 × 7.5 in** (para embeber diagramas sin reescalar).

## 3. Tipografía y tamaños (Ernesto pidió "más grande / llenar espacio" 2 veces)

- Títulos de slide: Barlow ExtraBold 28pt. Títulos de divisoria 50pt.
- Bullets de contenido: **24–30pt** (no 18). Vert. centrados para llenar.
- Bullets visuales = **tarjetas** redondeadas con número en círculo teal (no viñetas planas).
- Tablas nativas: fontsize **15–18**, header 13–16.

### 3.b Notas del presentador (formato del deck B5)

`PROPÓSITO — <una frase>` / narrativa (párrafo/s) / `PUNTOS CLAVE` (viñetas), **texto BLANCO
`#FFFFFF`** (Ernesto las lee sobre panel oscuro). Las 17 slides lo usan (`set_notes` en
`generate_b5_deck.py`). Sin nº de job, sin nombres. **Supera el formato B2** "BLOQUE N —
Título" de CLAUDE.md *para este deck*: más legible y orientado a **exponer**, no a re-explicar
el gráfico ([[presentacion-convenciones-benjamin]]). La primera línea (`PROPÓSITO —`) resume
además el objetivo de cada slide.

## 4. Elementos NATIVOS (helpers en generate_b5_deck.py)

- **Tablas** → `add_table()` (GraphicFrame). Se quita el `<a:tableStyleId>` del tema y se
  fijan fills propios: header teal, filas alternas, celdas de veredicto coloreadas.
- **Gráficos** → `add_chart_grouped()` (`add_chart`, COLUMN_CLUSTERED): barras CLAM vs
  Mammoth con data-labels, leyenda, colores de serie, eje 0–1. **Reportar bal_acc Y AUC**.
- **Matrices de confusión** → `add_confusion()`: TABLA nativa (n+1)×(n+1) con celdas tipo
  heatmap (`_blue_shade(v/max)`) + headers pred/true + caption de recalls. Sirve 2×2 y 3×3.
- **Diagramas de bloques** → `.pptx` editable copiado por árbol de shapes (`copy_diagram`,
  `deepcopy` del spTree, re-id de `cNvPr`) — preserva OMML del CLAM original.
- **Esquemas conceptuales** → shapes nativos (`draw_mammoth_concept`: antes/después con
  rounded-rects + flechas).
- **Header en TODA slide** (incl. diagramas): `copy_diagram(..., bar=True)` dibuja el
  header sobre el diagrama; los diagramas se generan **sin título interno** y con el
  contenido por debajo de y=0.82. Excepción: el diagrama CLAM reusado (contenido pegado
  arriba) usa `bar=False` (logo + título sin barra gris, en el hueco superior-izquierdo).

## 5. Diagramas de arquitectura (estilo Diagrama_CLAM.pptx)

- **Matemáticos Y code-accurate**: cada bloque lleva TÍTULO (mayúsculas) + FÓRMULA +
  DIMENSIONES (`v ∈ ℝ^(N×512)`, `P ∈ ℝ^(N×C)`). Las ecuaciones salen del **paper**, pero
  los **parámetros reales** (kernels, heads, landmarks, dims, escalas) salen del **código
  del modelo**, no del paper. Caso PathPT: `models_pathpt/{spatial,prompt,pathpt}.py` (pin
  `0ab7f1b`). Distinción a no perder: `512` = dim contrastivo vs `768` = dim token (`ctx`).
- **Callouts** de dimensión/ecuación a los lados de la cascada (no encima → sin solapes).
- **Cero bullets, cero caption largo.** Color: azul=pipeline, gris=CONGELADO, naranjo=ENTRENABLE.
- Texto en **Carlito + Unicode plano** (`ℝ⁵¹²`, `θ`, `τ`, `⟨⟩`) → rasteriza limpio
  (el OMML/Cambria del CLAM original se ve roto en LibreOffice, OK en PowerPoint —
  [[pptx-qa-omml-libreoffice]]).
- **ADDENDUM 17-jun — subíndices/superíndices con baseline REAL (no solo Unicode plano).**
  El Unicode plano cubre lo que Unicode TIENE (`ℝ⁵¹²`, `θ`, `⟨⟩`), pero **no hay subíndice
  Unicode para muchas letras** (`q`, `w`, …) → `Wq` quedaba con la `q` a tamaño normal. Para
  esos casos `generate_clam_mammoth_pptx.py` trae un mini-markup —`_x`/`_(xx)` subíndice,
  `^x`/`^(xx)` superíndice— y el helper `_add_runs` emite runs con `baseline` OOXML real
  (−25%/+30%, tamaño 0.74×): funciona para **cualquier** letra, rasteriza limpio en
  **LibreOffice y PowerPoint**, y queda editable. Regla: Unicode plano cuando alcanza;
  baseline real (`_add_runs`) para los subíndices que Unicode no representa. **Evitar `_`/`^`
  literales** en los strings fuente (`auto_rank` → `automático`). Detalle:
  `auditoria_coherencia/hallazgos_diagrama_mammoth.md` §N1.

### 5.b Molde "cascada de 3 ramas" (modelo multi-stream, aprobado 16-jun-2026)

Para un modelo de **2+ streams que convergen** (visión + lenguaje, tipo PathPT) el diagrama
de arquitectura converge a este molde (slide 11, `generate_pathpt_pptx.py build_slide1`):

- **3 ramas en paneles etiquetados** con fondo tenue: VISIÓN (`θᵥ`, azul `#ECF2F8`),
  TEXTO (`θₜ`, naranjo `#FBF3EA`), MATCHING (gris `#EEF1F3`); título de panel 14pt.
- **Cascada hacia abajo**: VISIÓN (izq) + TEXTO (der) descienden y **convergen** en
  MATCHING (centro-abajo), que es **su propia mini-cascada** (≥2 bloques, no uno solo).
- **Bloques modulares** (1 operación, nombre corto, fuente ≥13pt) + **callouts laterales**
  con la **fórmula del traspaso** (estilo expansión CLAM: izq visión, der texto), unidos por
  conector fino.
- **Nodo backbone compartido al centro** (`CONCH`, Φᵥ+Φₜ congelados) para llenar el hueco
  medio del árbol sin romper el minimalismo, conectado con líneas finas a ambas ramas
  (arquitectónicamente correcto: son los 2 encoders del mismo modelo congelado).
- **Aristas con flecha**: helper `edge()` (conector + `a:tailEnd` triangle). Dims del
  traspaso sobre las aristas convergentes (`V̄ : N×512`, `T : C×512`).
- **Forward puro**: el diagrama termina en la salida del modelo (`P ∈ ℝ^(N×C)`). La
  **lectura/agregación** (tumor-ratio → clase de slide, mapa de localización) y el
  **training** (pseudo-labels, losses) NO van acá — son de otras slides
  ([[presentacion-convenciones-benjamin]]: sin proceso de entrenamiento).
- **Leyenda en una esquina** (color congelado/entrenable + glosario de dims), fuera de las ramas.
- Detalle del proceso e iteración: `auditoria_coherencia/hallazgos_diagrama_pathpt.md`,
  memoria [[diagramas-arquitectura-pptx-editable]].

### 5.c Molde "árbol ramificado" (fan-out/fan-in) + panel "lentes paralelas" (zoom MoE, slide 6)

Para un modelo con un cuello que **se ABRE** a N unidades paralelas y **se vuelve a CERRAR**
(MoE: ruteo → expertos → combinación), el zoom converge a este molde
(`generate_clam_mammoth_pptx.py build_slide2`, aprobado 17-jun — *"así me gusta más"*):

- **Tronco vertical** (entrada → query → ruteo) que **se ramifica** (fan-out) a 3 nodos
  representativos (`EXPERTO 1 / 2 / 30` + `· · ·`) y **converge** (fan-in) en la combinación →
  salida. Cada bloque: TÍTULO + fórmula + dims. Convención de lectura: el renglón gris chico
  es **definición** ("donde `D = …`"), NO el paso siguiente (el orden de cómputo lo pone el
  lector). Aristas con flecha (`add_connector`).
- **Callouts laterales matemáticos** (estilo expansión CLAM, sin solapes): LoRA a la
  izquierda (familia **azul** = expertos), banner "MISMO PRESUPUESTO" arriba-derecha, nota
  integración arriba-izquierda.
- **Panel "lentes paralelas"** (`add_heads_panel`) para volver visual un concepto fino —acá
  las **CABEZAS / multi-head**—: recuadro con 3 criterios de ejemplo (textura/forma/densidad)
  + `· · · ×16 lentes` + remate "mismo query, N criterios → se concatenan". Va del lado
  **opuesto** al callout LoRA y en la **familia de color del bloque que anota** (naranja =
  query). Reusable para cualquier concepto que necesite un mini-zoom pedagógico.
- **Dimensiones POR BLOQUE, sobre el flujo** (no en un glosario único — Ernesto, 18-jun:
  *"así está mucho mejor"*): cada caja lleva la forma del tensor que produce (`z:[N×512]` →
  `q:[N×256]` → `u→[300 slots]` → `o:[10×512]` → `h:[N×512]`), code-accurate contra
  `mammoth.py` (`forward`/`get_logits`/`get_weights`). Las **dos softmax** se anotan **en su
  propio bloque**: reparto `D = softmax_n ↓ N parches` en RUTEO; mezcla `C softmax ↓ 300
  slots` en COMBINACIÓN (matar la confusión "¿sobre qué eje normaliza?"). `S:[30,16,10,16]`
  va donde se usa, para dejar claro que es **tensor de claves aprendidas, no un escalar**.
  Notación: `[.] = forma del tensor` en la leyenda. **Se probó un panel-glosario único y se
  descartó**: rompe la lectura del flujo (el dato debe verse pasar bloque a bloque). Las
  formas 4-eje van compactas y solo donde aportan; el detalle conceptual queda para las notas
  del presentador, no para el lienzo.
- **Distinto del molde "cascada de 3 ramas"** (§5.b, multi-stream visión+texto que CONVERGEN):
  acá es **1 stream que se abre y se cierra**. Forward puro, sin training, sin nº de job ni
  nombres ([[presentacion-convenciones-benjamin]]). Detalle: `hallazgos_diagrama_mammoth.md` §N2/N3.

## 6. QA

`libreoffice --headless --convert-to pdf` + `pdftoppm -png` → hojas de contacto. **No**
hacer pixel-QA de slides con OMML (falso positivo de LibreOffice). Verificar fidelidad de
diagramas copiados por conteo de shapes + oMath + IDs únicos. Abrir el deck final en
**PowerPoint/OnlyOffice**, no LibreOffice.

## 7. Estructura del deck B5 (17 slides)

Portada · Objetivos · [div MAMMOTH] · qué es (tarjetas + concepto nativo) · diagrama
integración · diagrama zoom MoE · **tabla** 8 tareas (+AUC) · invasión (**chart** +
**confusión** nativos) · [div PathPT] · idea (fig paper) + 3 componentes · diagrama
arquitectura (matemático) · necrosis (**tabla** + **confusión**) · mitótica (2
**confusiones**) · microcalc (**tabla**) · [div Cierre] · cierre 3 ejes (**tabla**) ·
próximos pasos.
