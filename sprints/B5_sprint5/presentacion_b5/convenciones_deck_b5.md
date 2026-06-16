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
