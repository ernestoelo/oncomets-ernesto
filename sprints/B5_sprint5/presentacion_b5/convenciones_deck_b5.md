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
| `scripts/generate_b5_deck.py` | **ensambla el deck** end-to-end (21 slides) |
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

### 3.b Notas del presentador (formato VIGENTE: GUION HABLADO corrido)

> **VIRAJE 25-jun-2026** (revisión slide-por-slide del deck B5, validado slides 1–6 con Ernesto):
> las notas se escriben como **guion HABLADO corrido** — prosa en párrafos, exactamente lo que el
> presentador va a DECIR, para leer de corrido (presenta online). **Supersede** el formato por-fases
> del 22-jun (abajo, LEGACY). Aplica a **toda presentación futura**, no solo al deck B5. Detalle del
> viraje y reconciliación: `auditoria_coherencia/hallazgos_notas_guion_viraje.md`; memoria
> [[notas-presentador-guion-didactico]].

Reglas del formato vigente:

1. **Prosa en párrafos**, leíble de corrido. **SIN etiquetas de fase** (nada de `PROPÓSITO`/`ABRIR`/
   `RECORRIDO`/`EXPLICAR`/`PUNTO CLAVE`/`TRANSICIÓN` — "generan ruido").
2. **Solo lo que se dice.** Sin meta-instrucciones ("decir tal cual", "señalá") ni la palabra "deck".
3. **Registro profesional.** Sin frases artificiales ("que se la lleven desde el primer minuto") ni
   coloquialismos poco profesionales ("mover la aguja", "aguas abajo" → "mejorar los resultados",
   "las etapas posteriores").
4. **Pedagogía fundida en prosa.** El recorrido de la slide (elementos, paneles de figura A→B,
   colores) se cuenta DENTRO del párrafo, no como lista rotulada; analogías y definiciones integradas.
5. **Definir antes de usar.** Cada término (slot, prototipo, query…) se define antes de la fórmula.
6. **Fiel a las ecuaciones del diagrama.** Si la slide muestra fórmulas/dims por bloque, describirlas
   fielmente (citar la ecuación escrita + explicarla en palabras) y dejar claro el **eje/dirección**
   (ej. softmax ↓ N parches vs ↓ 300 slots; "es al revés: cada slot recoge de todos los parches, no
   parche por parche").
7. **Sin ejemplos numéricos en el guion** — debe entenderse con la sola explicación; el ejemplo
   numérico queda para responder si preguntan.
8. **Encadenar slide con slide.** Abrir retomando el cierre de la anterior, cerrar anticipando la
   siguiente, sin rótulo de "transición".
9. **Brevedad por tipo.** Divisorias/transición = 1 párrafo muy breve. Slides técnicas centrales
   pueden ser más extensas, sin sobre-extenderse; si algo alarga, recortar lo secundario.
10. **Restricciones duras que se conservan:** **texto BLANCO `#FFFFFF`**, **sin nº de job, sin
    nombres** (baselines = "Métricas oficiales Environ"), español técnico + pedagógico, autosuficiente
    para leer mientras se expone ([[presentacion-convenciones-benjamin]]).
11. **Slides de resultados (tabla)** (validado 26-jun): leerla por la **columna del Δ pareado** de
    arriba a abajo (no fila por fila); mencionar **solo bal_acc y AUC** (varianza/colores no se
    narran); **atar el patrón al dataset** de cada tarea; cerrar con una **conclusión breve del
    porqué**. Para una slide técnica que el presentador no domina: explicársela primero, luego la
    nota, y **referenciar los paneles de la figura** para que el guion siga la imagen. Refuerza la
    regla 5: **no introducir nomenclatura no presentada antes** (cazado: `slot_dropout`, "token")
    — definirla o quitarla.
12. **Decimales, cómo se pronuncian** (fijado 4-ago-2026, deck B8): **un decimal se dice tal
    cual** («cero coma cinco»), **dos se agrupan en decenas** («cero coma ochenta y nueve»),
    **tres en centenas** («cero coma ochocientos noventa»). Dígito a dígito solo si la cifra no
    entra en ninguno de los tres casos. Es independiente de **cuántos decimales se escriben en
    la lámina**, que es otra decisión: el guion pronuncia según los que la lámina muestre.
13. **Si el término está escrito en el cuerpo, el guion lo hereda** (4-ago-2026). Antes de
    quitar del guion un término técnico o un anglicismo, **grepear el generador**: si la palabra
    está proyectada, sacarla desajusta lo que se oye de lo que se lee, y eso cuesta más que el
    tell. En ese caso aplica la regla 5 en su forma literal — **definirla, no evitarla**.
    Cazado con `logit`/`softmax` y con «fold» ([[deck-qa-puntos-ciegos-chequeo]]).

**Autoría / divergencia intencional:** Ernesto edita las notas **directo en OnlyOffice**. El motor
`set_notes(slide, proposito, sections)` de `generate_b5_deck.py` todavía RINDE el formato por-fases
(LEGACY) → **NO regenerar el deck para "actualizar notas"** (pisaría las ediciones de OnlyOffice).
Propagar el formato hablado al motor `set_notes` solo si Ernesto lo pide.

#### LEGACY — formato por fases (22-jun, SUPERSEDED por el viraje de arriba)

El motor `set_notes(slide, proposito, sections)` rendía un GUION por fases con etiqueta en negrita:
`PROPÓSITO —` + `ABRIR` (apertura literal) · `RECORRIDO` (guía elemento-por-elemento, cada
caja/panel/bullet y cada panel de figura a/b/c/d en orden visual) · `EXPLICAR` (pasos `→`) ·
`ANALOGÍA`/`EJEMPLO` · `PUNTO CLAVE` · `TRANSICIÓN`; ítems `(ancla, texto)` con ancla en negrita.
Se conserva porque el motor del script aún lo emite; el contenido pedagógico de cada fase ahora va
fundido en la prosa del guion hablado.

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
  las **CABEZAS / multi-head**—: recuadro con 3 lentes/subespacios de ejemplo
  **(ILUSTRATIVOS, sin etiqueta semántica fija)** + `· · · ×16 lentes` + remate "mismo
  query, N subespacios → se concatenan". **CORRECCIÓN 29-jun (reunión Benjamín): las
  cabezas NO son "textura/forma/color/densidad"** — son subespacios APRENDIDOS sin
  semántica impuesta (la morfología vive en los SLOTS, no en las cabezas; paper Fig 3).
  El rótulo viejo "(textura/forma/densidad)" indujo la respuesta equivocada de Ernesto y
  el reproche de Benjamín → usar etiquetas neutras o un caption "ejemplos ilustrativos,
  no asignaciones". Detalle: `mammoth_entendimiento/respuestas_preguntas_benjamin.md §Q1`.
  Va del lado
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

## 7. Estructura del deck B5 (21 slides)

> **ADDENDUM 26-jun-2026 — recorte a ~16 slides.** Eliminadas del deck: **tasa mitótica**,
> **microcalc go/no-go** (PathPT cierra en necrosis), **div Cierre**, **cierre 3 ejes** y
> **CLAM + loss**. El único cierre es **próximos pasos** (reenfocado a magnificación). La
> estructura de abajo es la de 21 slides ORIGINAL (LEGACY); el estado vigente y las notas
> finales viven en `notas_presentador_guion.md` (sección "Slide final — Próximos pasos").
> El generador `generate_b5_deck.py` aún arma las 21 (no se regenera; Ernesto edita el `.pptx`).

Portada · Objetivos · [div MAMMOTH] · qué es (tarjetas + concepto nativo) · diagrama
integración · diagrama zoom MoE · figura oficial fused (dims overlay) · variante keep_slots
(fused) · **tabla** 8 tareas drop-in (estructura unificada: n por clase + Δ AUC) · invasión
(**chart** + **confusión** nativos) · **tabla** keep_slots 4 tareas (estructura unificada;
cierre 12 tareas) · [div PathPT] · idea (fig paper) + 3 componentes · diagrama arquitectura
(matemático) · necrosis (**tabla** + **confusión**) · mitótica (2 **confusiones**) · microcalc
(**tabla**) · [div Cierre] · cierre 3 ejes (**tabla**) · **tabla** CLAM + loss rebalanceada
(4º intento = la pérdida, no la arquitectura; misma estructura unificada que las 2 de mammoth)
· próximos pasos.

> **Comparativa unificada (3 tablas, columnas idénticas):** drop-in (mammoth keep_slots=False),
> keep_slots=True y CLAM+loss comparten estructura `Tarea · Dataset(n: sí/no) · bal_acc CLAM→X ·
> Δ bal_acc · AUC CLAM→X · Δ AUC` y el MISMO baseline CLAM (mismos splits k=5) → carcinoma/CDIS/
> tejido anclan con idéntico CLAM 0.639/0.732, 0.595/0.652, 0.577/0.646 en las 3. La de loss se
> rotula **"CLAM + loss"** (NO "mammoth + loss"): la pérdida se aplicó a CLAM_MB intacto.
