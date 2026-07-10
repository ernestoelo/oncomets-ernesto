# Investigación — ¿qué magnificación(es) para microcalcificaciones y por qué?

> **Fundamento (regla 9: argumento ANTES de código) del experimento de magnificación
> multi-escala del B6.** Responde a la pregunta de Sebastián (reunión 2-jul): *¿cuál es
> el criterio de las dimensiones/escala que escojo para microcalcificaciones?* — antes de
> extraer features a ciegas.
> Análisis SIN GPU, SIN entrenamiento. Toda afirmación clínica va con su fuente; el
> razonamiento propio va marcado **[inferencia]**. Insumo previo: `../../B5_sprint5/magnificacion/analisis_cpathagent.md`.

---

## 0. TL;DR — recomendación en 8 líneas

1. La etiqueta de las 3 tareas (CAP Nota D: microcalc **en** CDIS / **en** carcinoma invasivo / **en**
   tejido no neoplásico) NO pregunta *"¿hay una calcificación?"* sino *"¿en qué estructura vive?"* →
   es una pregunta **arquitectural/contextual**, no de detalle celular.
2. Esa localización exige ver el **tejido anfitrión** (el conducto con patrón de DCIS, el nido invasor,
   el lobulillo benigno) — que a **parche fino** (128 µm) **no cabe en el campo de visión**.
3. Por eso la palanca de magnificación aquí = **agregar una escala GRUESA de contexto**, no más zoom.
4. Recomendación: **pirámide de 2 escalas — fina ≈20× (0.5 µm/px, detecta la calcificación + su
   morfología) + contexto ≈5× (2 µm/px, el conducto/lobulillo)**. Precedente directo: DSMIL (20×+5×,
   ya en `models_dsmil/`) y Deep Multi-Magnification Networks (mama/DCIS).
5. **Fusión = promedio por región → un token `[N,512]`** → **CLAM_MB intacto**, comparación paired
   más limpia (réplica del baseline MIL de CPathAgent, Ap. C.1.2). Multi-token/concat = 2ª iteración.
6. **Hallazgo empírico (resuelve el bloqueador):** las cohortes **no** están a la misma magnificación
   física a `level0` — **TCGA 0.2325 µm/px (~40×), privado 0.465 µm/px (~20×)** → la pirámide se
   define en **µm/px**, no en `level`. HistAI: sin MPP confiable en metadata (pendiente).
7. **Techo honesto (regla 9):** las calcificaciones de **oxalato de calcio (Tipo I)** son casi
   invisibles en H&E de campo claro (solo con luz polarizada) → CONCH está ciego a ellas a
   **cualquier** magnificación; el lift esperado es **chico** (el propio CPathAgent gana solo +2.9%
   sobre ABMIL multi-escala y no rompe el techo de datos).
8. Encuadre (Hallazgos 11-14): esto **no** reabre "otra arquitectura para ganar" — es la **única señal
   nueva** (contexto espacial) que el parche fino físicamente no contiene.

---

## 1. La pregunta y por qué no es trivial

Sebastián no preguntó "¿multi-escala sí o no?" (eso ya lo aprobó). Preguntó **con qué criterio se eligen
las escalas para ESTA tarea**. La respuesta no puede ser "las del paper" (CPathAgent usa 2048+4×1024+16×512
sobre CPath-CLIP, no CONCH), sino **qué escala aporta señal diagnóstica para microcalcificaciones en mama**,
argumentado desde patología. Eso es lo que sigue.

La trampa: uno intuye "microcalcificación = objeto chico = necesito MÁS zoom". Es al revés. Ver §2.3.

---

## 2. Fundamento clínico (patología de la microcalcificación mamaria)

### 2.1 Dos tipos de calcio — y uno es invisible en H&E

| Tipo | Composición | En H&E de campo claro | Malignidad | Relevancia para CONCH |
|---|---|---|---|---|
| **Tipo I** | Oxalato de calcio (weddellita) | **Casi invisible** — incolora/refráctil, solo visible con **luz polarizada** | Casi siempre **benigna**, rara | **CONCH está ciego** (trabaja H&E brightfield, sin polarización) → **techo**, a cualquier magnificación |
| **Tipo II** | Fosfato de calcio (hidroxiapatita) | **Basófila** (púrpura/azul), anillos concéntricos laminados, en luz ductal o estroma | **Benigna Y maligna** | **Visible** → aquí SÍ juega la magnificación |

*Fuentes:* revisión *Breast microcalcifications: Past, present and future* (PMC8892454); *Calcification in
breast histopathology* (Diagnostic Histopathology 2024); *Polyhedral microcalcifications… calcium oxalate*
(Radiology 1993).

**Consecuencia de diseño:** el techo de las 3 tareas **no** es el mismo. Las de carcinoma/CDIS dependen de
Tipo II (visible) → magnificación puede ayudar. La de *tejido no neoplásico* arrastra más Tipo I (oxalato,
benigno) → CONCH parcialmente ciego ahí, independiente de la escala. **[inferencia]**

### 2.2 Tamaño — la calcificación cabe en un parche fino; el conducto NO

- Microcalcificación asociada a malignidad: **50–500 µm** (0.05–0.5 mm). Histología las subclasifica en
  **<100 µm** y **≥100 µm**. Benignas suelen ser más gruesas (>1 mm). (*Microcalcifications… size matters!*,
  PubMed 17566305; *Independent predictors…*, Br J Cancer 2011.)
- A CONCH nativo (20×, 0.5 µm/px, parche 256 px = **128 µm** de campo): una calcificación chica (50–100 µm)
  **entra** en un parche; una laminada grande (300–500 µm) **no** entra completa. → El detalle fino ya
  resuelve la calcificación; lo que **no** cubre es su **estructura anfitriona**.
- Estructura anfitriona a clasificar: conducto de DCIS **0.2–2 mm**, nido invasor/interfaz **0.5–2 mm**,
  TDLU/lobulillo benigno **0.5–1 mm**. → El contexto diagnóstico vive a **~0.5–2 mm de campo**, es decir
  **~2.5×–10× de magnificación efectiva**, no a 20–40×.

### 2.3 Las DOS tareas visuales tienen demandas OPUESTAS de magnificación

```
   Microcalcificación (Tipo II, basófila, alto contraste)
   ├─ TAREA A: detectar + caracterizar morfología          ──►  ALTA magnif (20–40×)
   │   (anillos laminados/psammoma ⇒ DCIS; amorfa; cristalina;      campo ~100–130 µm
   │    atipia epitelial adyacente)                                 = donde vive CONCH
   │   · nota: por su alto contraste basófilo el patólogo las
   │     DETECTA ya a bajo aumento (scanning power); el zoom
   │     es para CARACTERIZARLAS, no para verlas.
   │
   └─ TAREA B: localizarla en el compartimento tisular      ──►  BAJA–MEDIA magnif (5–10×)
       = LA ETIQUETA CAP (¿en DCIS? ¿en invasor? ¿en benigno?)     campo ~0.5–2 mm
       requiere ver el CONDUCTO/LOBULILLO anfitrión completo       = lo que HOY falta
       y su patrón (cribiforme/comedo/sólido, nido infiltrante).
```

**El cuello para nuestras tareas es la TAREA B, y es exactamente lo que el parche fino no puede contener.**
El pipeline actual (escala única fina) detecta la calcificación pero **no tiene campo de visión para
atribuirla** a su anfitrión — que es literalmente lo que la etiqueta codifica. Agregar una escala **gruesa**
inyecta ese contexto = **señal nueva**. **[inferencia, anclada en 2.1–2.2 + §3]**

---

## 3. Qué dice cada referencia (citable — regla 5)

| Fuente | Qué aporta al criterio de escala | Cita |
|---|---|---|
| **CAP** *Invasive Breast, Nota D* | La etiqueta es *"Microcalcifications: Not identified / **in DCIS** / **in invasive carcinoma** / **in non-neoplastic tissue**"* — *"select all that apply"* → la pregunta es **dónde vive**, contextual. | `prompts_cap.md`; [[cap-fuente-clases-tareas]] |
| **CPathAgent** (NeurIPS 2025) — lógica de asignación de magnif. (E.3) | *"excludes the benign/background breast tissue areas from **high-magnification** requirements, as these regions… appear benign and uninvolved **at low magnification**"* → **baja magnif. triagea el tipo de tejido**; la alta se reserva para el detalle en regiones significativas. Es el principio de nuestras 2 tareas visuales. | PDF §E.3 (L2896) |
| **CPathAgent** — ejemplo de mama | Region-reasoning real: *"invasive ductal carcinoma… associated DCIS… **Microcalcifications are present in conjunction with the invasive carcinoma**"* → mismo encuadre contextual que nuestra tarea; mama = su clase tisular más grande (3.110 WSIs). | PDF (L435-441, L2256) |
| **CPathAgent** — baseline MIL (Ap. C.1.2) | Fusión multi-escala por **promedio** por región (2048 + 4×1024 + 16×512) → ABMIL/DSMIL. **Portable** a CONCH; es la receta de fusión que adoptamos. | PDF Ap. C.1.2 |
| **DSMIL** (CVPR 2021) — **ya en `models_dsmil/`** | Pirámide **20× + 5×**: el vector 5× se concatena a cada parche 20× de su región. Establece **5× como la magnif. de "contexto"** estándar en MIL de WSI. | Li et al., CVPR 2021 |
| **Deep Multi-Magnification Networks** (Ho et al., Mount Sinai) | Segmentación multiclase de **mama incl. DCIS**: multi-magnificación **supera** a single-magnificación en IoU → grounding *breast-specific* de que el contexto cross-escala mejora la discriminación de **compartimentos tisulares** (nuestra Tarea B). | Med Image Anal 2021 / arXiv:1910.13042 |
| **CONCH** — punto de operación nativo | **20× / 0.5 µm/px**, tiles 256 px. → la escala **fina** debe anclarse cerca de 20× (su "casa"); 5× es un OOD moderado y precedentado, por eso va como token secundario con 20× de ancla. | Lu et al., Nat Med 2024 |

---

## 4. Hallazgo empírico — magnificación física de las cohortes (resuelve el bloqueador (a) de `current.md`)

Verificado read-only con `openslide` sobre 1 WSI real de cada cohorte (sin GPU):

| Cohorte | `objective-power` (tag) | **`mpp-x` real** | Magnif. física a `level0` | Parche 256 px cubre | Fuente |
|---|---|---|---|---|---|
| **TCGA** (.svs Aperio) | 20 (tag) | **0.2325 µm/px** | **~40×** (el tag miente; el MPP manda; coincide con el dir `features_tcga_224x40`) | **59.5 µm** | `TCGA-A8-A08A-01Z-…svs` |
| **Privado** (.bif Ventana) | 20 | **0.465 µm/px** | **~20×** | **119 µm** | `wsi/B25-158771/…bif` |
| **HistAI** (.tiff) | None | **1000 (bogus)** | **sin metadata confiable** → PENDIENTE | ? | `wsi_histai/case_1647/…tiff` |

**Implicaciones (importantes):**
1. **TCGA y privado difieren 2× en escala física a `level0`.** Un "parche 256 @ level0" mide **59 µm en
   TCGA vs 119 µm en privado** → **la pirámide se define en µm/px físicos, NO en `level`.** (Confirma la
   advertencia del análisis CPathAgent, pregunta #2.)
2. **Confound latente en el pipeline actual (single-scale):** hoy TCGA se le entrega a CONCH a **~40×**
   (2× por encima de su nativo 20×) y privado a **~20×** (nativo). CONCH ve el **mismo** tejido a **2×
   distinta magnificación** según cohorte. La re-extracción a un **target de µm/px común** (p.ej. 20×) no
   solo habilita la pirámide: **de paso normaliza este confound.** **[inferencia]**
3. La señal útil de microcalc es **TCGA-heavy** (identificadas: TCGA 207 / privado 77 / HistAI 49 de 333;
   `dataset_microcalcificaciones.md`) → anclar la escala fina a TCGA(40×)+privado(20×), que están resueltos.
   HistAI (minoritario) se resuelve aparte (§7).

---

## 5. Recomendación fundamentada — escalas + fusión

### 5.1 Escalas (definidas en µm/px; cada cohorte mapea a su `level`+downsample para alcanzarlas)

| Escala | Target físico | Campo por tile CONCH (256 px) | Rol clínico | Qué resuelve |
|---|---|---|---|---|
| **Fina** | **≈20× · 0.5 µm/px** | ~128 µm | **Tarea A** — detecta la calcificación (Tipo II basófila) + morfología (laminada/psammoma ⇒ DCIS) + atipia epitelial adyacente | el objeto + su detalle; ancla CONCH-nativo; **normaliza el confound §4.2** |
| **Contexto** | **≈5× · 2.0 µm/px** | ~512 µm | **Tarea B** — el **conducto/lobulillo anfitrión** y su patrón (cribiforme/comedo/sólido; nido invasor; TDLU benigno) | la **localización** que la etiqueta CAP exige |
| *(opcional)* Intermedia | ≈10× · 1.0 µm/px | ~256 µm | puente si 2 escalas dejan un salto brusco | 2ª iteración **solo si** el par 20×+5× muestra lift |

### 5.2 Por qué estas y no otras (el argumento, no la intuición)

- **Por qué agregar una escala GRUESA y no más zoom:** la etiqueta es contextual (§2.3, §3-CAP). El
  detalle celular fino ya lo tenemos; lo que falta es el campo de visión del anfitrión (0.5–2 mm). Más zoom
  no aporta señal nueva a la Tarea B.
- **Por qué 5× y no más grueso (2.5×/1.25×):** (a) CONCH se entrenó a 20×; 5× ya es 4× de downsample (OOD
  moderado, pero **precedentado** — DSMIL/DMMN lo usan). A 1.25× (16× downsample) el tile deja de parecerse
  a lo que CONCH vio → features degradadas. (b) El contexto para "¿en qué compartimento?" es el
  conducto/lobulillo (0.5–1 mm), **cubierto a 5×**; ir más grueso agrega contexto de lóbulo entero que la
  etiqueta no necesita. **[inferencia]**
- **Por qué mantener la escala fina (no solo 5×):** los anillos laminados/psammoma que asocian a DCIS, la
  atipia, y el **contraste** de la calcificación Tipo II se resuelven solo cerca de 20×. 5× solo perdería el
  objeto. → la fina es el **ancla**; el contexto es **aditivo**.
- **Por qué empezar con 2 escalas (no las 3):** restricción de costo de Sebastián (microcalc = pocas WSI,
  un fin de semana; menos escalas = menos extracción CONCH). La 3ª (10×) es un follow-up barato.

### 5.3 Fusión

**Promedio de los vectores CONCH por región → un token `[N,512]`.**
- Mantiene la forma del bag → **CLAM_MB intacto** → la comparación paired es la más limpia (único delta =
  el **contenido** del token, no la arquitectura del agregador — que ya cerramos, Hallazgos 11/12).
- Es la receta del baseline MIL de CPathAgent (Ap. C.1.2).
- **Alternativas (2ª iteración, solo si el promedio da lift):** concatenación estilo DSMIL (→ `[N,1024]`,
  cambia `embed_dim`) o multi-token (1 embedding por escala, cambia el bag). Ambas meten un confound extra
  → no en la 1ª pasada.

### 5.4 Qué tarea se beneficia más (predicción por tarea)

| Tarea binaria | Anfitrión | Predicción del efecto del contexto 5× |
|---|---|---|
| `..._en_cdis` (121 pos) | conducto de DCIS (patrón arquitectural fuerte) | **mayor** candidato a lift — el patrón ductal es puro contexto |
| `..._en_carcinoma_invasivo` (68 pos) | nido/interfaz invasora | **candidato** — la infiltración estromal es contextual |
| `..._en_tejido_no_neoplasico` (195 pos) | TDLU/adenosis benigna | **menor** — arrastra más Tipo I (oxalato) que CONCH no ve (§2.1) → techo |

### 5.5 Cómo extraer dado que las cohortes están a 40× (TCGA) y 20× (privado) — magnificación ≠ tamaño de parche

Dos ejes que NO hay que confundir:
- **Magnificación / resolución = µm/px** = cuánto **detalle**. La fija el escáner (no se elige): TCGA 0.2325
  µm/px (~40×), privado 0.465 µm/px (~20×).
- **Tamaño de parche (px) = cuánto CAMPO** cubro. **Esto sí lo elegimos** al extraer.
- **Campo físico (µm) = tamaño_parche_px × µm_por_px.**

Los "2048 / 1024 / 512" de CPathAgent (Ap. C.1.2) son **tamaños de parche en px a una magnificación FIJA (40×)**
→ 512 µm / 256 µm / 128 µm de campo. Todos se **redimensionan al input del encoder** (224/256 px): un parche
grande achicado = el encoder ve **más tejido con el mismo nº de píxeles** = "menos magnificación / más contexto".

**NO podemos copiar sus px literales**, porque nuestras cohortes NO están todas a 40×: 2048 px = 512 µm en TCGA
pero **1024 µm en el privado** → mismo px, campo físico distinto = confound. **La pirámide se parametriza en
campo físico (µm), y el tamaño de parche en px se calcula POR COHORTE** para dar en el blanco:

| Escala | Campo objetivo | TCGA (0.2325 µm/px) recorta | Privado (0.465 µm/px) recorta | Luego |
|---|---|---|---|---|
| **Fina ≈20×** | ~112 µm | ~482 px | ~241 px | resize → 224 (CONCH) |
| **Contexto ≈5×** | ~512 µm | ~2202 px | ~1101 px | resize → 224 (CONCH) |

Así CONCH ve **el mismo campo físico a la misma escala en ambas cohortes** (y de paso se **corrige el confound**
§4.2). Implementación: leer una región mayor del WSI (`patch_level`/`custom_downsample` de openslide) y
reescalar a 224. Misma idea que CPathAgent (pirámide de campos → input fijo → promedio), **parametrizada por
µm/px** en vez de px crudos.

### 5.6 ¿Es microcalc la mejor tarea para esto? — ranking por "context-hunger"

Honesto (regla 9 + [[surface-premise-discrepancies]]): microcalc se eligió por **costo** (pocas WSI, un fin de
semana), NO por ser la de mejor argumento. Ranking por cuánto depende el diagnóstico del **contexto arquitectural**
(lo que la escala gruesa aporta):

| Tarea | ¿Diagnóstico arquitectural (bajo-medio aumento)? | Candidata a multi-escala |
|---|---|---|
| `gh_dif_tubular` (diferenciación glandular/tubular) | **Sí, puro** | **Máxima** |
| `cdis_patron_*` (cribiforme/comedo/sólido/micropapilar) | **Sí, puro** | **Máxima** |
| `invasion_linfatica_vascular` | Sí (relación epitelio↔estroma/vaso) | Alta |
| **`microcalcificaciones_en_*`** | **Parcial** (localización sí; detección fina; techo oxalato) | **Media** |
| `mitotic`, grado nuclear | No (features celulares de alto aumento) | Baja |

**Recomendación:** correr microcalc como **piloto barato para validar el pipeline** multi-escala end-to-end
(honra el presupuesto de Sebastián), pre-registrando lift **chico**, y dejar **`gh_dif_tubular` o un patrón de
DCIS como la apuesta de mayor retorno** si el piloto valida la tubería. Es un matiz para Sebastián, no una
contradicción con su scoping.

---

## 6. Expectativa honesta pre-registrable (regla 9 / 9.a)

- **Hipótesis primaria:** fusionar 20×+5× (promedio) sube el contexto arquitectural → **Δ pareado ≥0
  consistente en signo** en `en_cdis` y `en_carcinoma_invasivo` (las context-hungry), sobre balanced_acc y AUC.
- **Alternativa/nula:** Δ dentro del ruido (std ≳ |media|) = en microcalc el contexto no mueve la aguja
  (convergería con los 4 ejes de 0 palancas → el cuello sería puramente el dato/desbalance).
- **Regresión:** Δ<0 consistente = la fusión **empeora** (p.ej. el promedio diluye la señal fina de la
  calcificación) → descartar promedio, evaluar multi-token.
- **Magnitud esperada: chica.** CPathAgent gana solo **+2.9% sobre ABMIL multi-escala** y **no rompe el
  techo de datos**; el oxalato Tipo I es un techo duro para `no_neoplasico`. El experimento se justifica
  porque inyecta la **única señal nueva** disponible, no por promesa de salto.
- **Evaluación:** balanced_acc **Y** AUC juntos + matriz de confusión + n/clase, **Δ pareado** por fold,
  reusando los **mismos splits k=5** del baseline single-scale ([[patron-paired-comparison-reuso-splits]]).

---

## 7. Pendientes y próximos pasos

1. **HistAI — magnificación física sin resolver** (metadata TIFF sin MPP válido). Opciones: (a) preguntar
   a Sebastián / doc del proveedor HistAI; (b) calibrar por tamaño de estructura conocida; (c) si no se
   resuelve, tratar HistAI aparte o excluirlo de la pirámide (es minoritario, 49/333). **No bloquea** el
   diseño con TCGA+privado.
2. **Confirmar con Sebastián** el criterio de esta investigación (que "escala" = target en µm/px, pirámide
   20×+5×, fusión promedio) — es la co-firma del gate exploratorio ([[gobernanza-gate-cofirma-sebastian]]).
3. **Pre-registrar** (regla 9 + **reviewer**, porque toca el data-pipeline de extracción) con §5–§6.
4. **Slurm de re-extracción multi-escala** (fin de semana, cortesía single-GPU, **preflight**): por cada
   región, extraer el tile fino (20×) + el tile de contexto (5×) mapeando cada cohorte a su `level`/downsample
   para alcanzar el target µm/px → CONCH 512 c/u → **promedio** → `.pt [N,512]`. Reusar `create_patches_fp.py`
   (soporta `patch_level`/`custom_downsample`) sin tocar `clam_environ` (wrapper en mi workspace, regla 2).
5. **Entrenar CLAM paired** vs single-scale sobre los mismos splits k=5, las 3 binarias.
6. **Tier 0 (calibración post-hoc) va ANTES de la GPU** ([[calibracion-tier0-pendiente-ejecutar]]) — palanca
   más barata, independiente de la magnificación.

---

## 8. Apéndice — verificación y fuentes

### 8.1 Comando de verificación de magnificación física (reproducible)

```python
# /home/sdonoso/miniconda3/envs/clam_latest/bin/python  (workaround B: binario absoluto)
import openslide
s = openslide.OpenSlide(path)
s.properties[openslide.PROPERTY_NAME_OBJECTIVE_POWER]  # tag (puede mentir: TCGA dice 20, es 40×)
s.properties[openslide.PROPERTY_NAME_MPP_X]            # µm/px REAL (manda esto)
# TCGA .svs  → mpp 0.2325 (~40×) · privado .bif → 0.465 (~20×) · histai .tiff → 1000 (bogus)
```

### 8.2 Estado del pipeline actual (regla 5, verificado en `clam_environ/`)

`create_patches_fp.py`: `patch_size=256`, `step_size=256` (no solapado), `patch_level=0`. →
`extract_features_fp.py`: `target_patch_size=224` → CONCH **512-dim**. → `CLAM_MB` recibe `[N,512]`.
Escala única. Soporta `patch_level` y `custom_downsample` → multi-escala factible sin modificar el codebase.

### 8.3 Fuentes (regla 5)

- *Breast microcalcifications: Past, present and future (Review)* — PMC8892454 / PubMed 35251632.
- *Breast microcalcifications: the lesions in anatomical pathology* — ScienceDirect S2211568413003884.
- *Calcification in breast histopathology* — Diagnostic Histopathology 2024, S1756-2317(24)00207-X.
- *Polyhedral microcalcifications at mammography: histologic correlation with calcium oxalate* — Radiology 1993.
- *Microcalcifications of the breast: size matters!* — PubMed 17566305.
- *Independent predictors of breast malignancy in screen-detected microcalcifications* — Br J Cancer 2011 (PMC3242612).
- Li et al., *Dual-stream MIL Network for WSI Classification* (DSMIL) — CVPR 2021 (PMC8765709).
- Ho et al., *Deep Multi-Magnification Networks for Multi-Class Breast Cancer Image Segmentation* — arXiv:1910.13042 / Med Image Anal 2021.
- Lu et al., *A visual-language foundation model for computational pathology* (CONCH) — Nat Med 2024.
- Sun et al., *CPathAgent* — NeurIPS 2025 (`papers/NeurIPS-2025-cpathagent-…-Conference.pdf`), §E.3, Ap. C.1.2.
