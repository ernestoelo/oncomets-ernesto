# Investigación: *retrieval* para OncoMets — análisis profundo + lectura pedagógica

> **Sprint B5 — fase de ARGUMENTO (regla 9).** Este documento NO toca
> `model_*.py`/`core_utils.py`/training, NO usa GPU, NO entrena. Es el
> *argumento antes de código*: qué es retrieval, qué dicen los papers reales,
> y cuál variante (A/B/C/D) conviene **dado nuestro cuello diagnosticado
> (datos/desbalance), nuestra materia prima (CONCH) y el calendario**.
>
> Anclado a 2 papers que Ernesto subió y que se leyeron completos (regla 5):
> - **[Alfasly 2024]** Alfasly, Alabtah, Hemati, Kalari, Tizhoosh. *Zero-Shot
>   Whole Slide Image Retrieval in Histopathology Using Embeddings of
>   Foundation Models.* Kimia Lab, Mayo Clinic. arXiv:2409.04631.
>   → `papers/Zero-Shot Whole Slide Image Retrieval.pdf`
> - **[He 2025/26]** He, Zhou, Guan, … Xie. *Boosting Pathology Foundation
>   Models via Few-shot Prompt-tuning for Rare Cancer Subtyping (PathPT).*
>   Shanghai Jiao Tong Univ. arXiv:2508.15904 → *Nature Communications*.
>   → `papers/Boosting Pathology Foundation Models via Few-shot.pdf`
>
> Papers ancla adicionales **citados pero no subidos** (del mismo lab que
> CLAM/CONCH; pedir PDF si se quiere profundizar): **SISH** (Chen et al.,
> *Nat Biomed Eng* 2022) y **PANTHER** (Song et al., CVPR 2024).

---

## 0. TL;DR — la recomendación en 6 líneas

1. **El cuello NO es la arquitectura, son los datos.** Lo probamos nosotros (8
   tareas pareadas, 0 palancas) **y lo confirma PathPT**: con pocos datos los
   métodos convergen a un **techo impuesto por los datos** (pediátrico:
   0.54–0.55 a 10-shot, *"ceiling imposed by limited data"* [He 2025/26]).
2. **Variante A (agregador-retrieval)** = repetir el error de mammoth. Descartar
   como apuesta; es swap de agregador sobre las mismas features.
3. **Variante D (CBIR, "buscador de slides parecidas")** = **la apuesta para
   AHORA**: bajo riesgo, alto brillo, usa exactamente lo que tenemos (CONCH +
   ~3000 slides), **NO entrena nada** (regla 9 trivial), y **sidestepea la
   trampa de "subir la métrica"** porque es un *entregable clínico*, no un
   número que ya sabemos que no se mueve por arquitectura.
4. **Variante B (prototipos / few-shot para clases raras, estilo PathPT)** = la
   **única que ataca el cuello (pocos positivos) con evidencia nueva**, pero con
   un *caveat honesto fuerte*: la ganancia de PathPT **depende del modelo base**
   (KEEP ≫ CONCH para grounding zero-shot), y choca con el techo de datos. Es
   apuesta de *trimestre siguiente*, no quick-win.
5. **Variante C (parches útiles)** = ya es el **Eje B del plan B5**; PathPT da
   una receta principista (pseudo-labels tile-level). Plegar a ese eje.
6. **Recomendación**: **D primario (presentación), B secundario (research si
   Ernesto sigue)**, C dentro del Eje B, A descartado con nota al pie.

---

## 1. Pedagogía: ¿qué es *retrieval* y por qué a NOSOTROS nos calza?

> Ernesto: esta sección es la base conceptual. Si ya la tenés clara, saltá a §3.

### 1.1 La idea base, sin jerga

Un modelo de clasificación clásico (como nuestro CLAM) **comprime** todo el
conocimiento en sus pesos: ve miles de slides, ajusta parámetros, y para una
slide nueva produce una etiqueta. El conocimiento queda *enterrado* en los
números del modelo.

**Retrieval** es el paradigma opuesto: en vez de comprimir todo en pesos,
mantenés una **"biblioteca" de casos** (sus *embeddings*) y, para un caso nuevo,
**buscás los más parecidos** y decidís en base a ellos. Es la diferencia entre
"estudié tanto que me sé la respuesta de memoria" (modelo paramétrico) vs
"busco en mi archivo los 5 casos más parecidos a este y miro cómo se
diagnosticaron" (retrieval, *no-paramétrico*).

```
  PARAMÉTRICO (CLAM)                      RETRIEVAL (kNN / CBIR)
  ┌──────────────┐                        ┌──────────────────────────┐
  slide → │  pesos  │ → label             slide → embedding → buscar k │
          │ (caja   │                              vecinos en la       │
          │ negra)  │                              biblioteca → votar  │
  └──────────────┘                        └──────────────────────────┘
  conocimiento en los pesos               conocimiento en la biblioteca
```

### 1.2 Glosario mínimo (anclado a nuestros datos)

| Término | Qué es | En NUESTRO caso |
|---|---|---|
| **Embedding** | Vector que resume una imagen en un espacio donde "cerca = parecido" | Las **features CONCH 512-dim**. Ya las tenemos para ~3000 slides |
| **kNN** (*k-nearest neighbors*) | Buscar los *k* vectores más cercanos (coseno / L2) y votar su clase | "dame las 5 slides más parecidas a esta y mirá sus labels" |
| **Memory-bank** | La "biblioteca" de embeddings guardados | Un índice sobre las ~3000 features CONCH |
| **Prototipo** | Un vector que *representa* una clase entera (ej. el promedio de sus embeddings) | Un vector "invasión presente", uno "ausente", uno "no identificado" |
| **CBIR** | *Content-Based Image Retrieval*: buscador "mostrame casos parecidos a esta imagen" | Un buscador para el patólogo: subo una slide, me muestra las N más parecidas del archivo |
| **Zero-shot** | Usar los embeddings **sin entrenar** ningún clasificador encima | Exactamente lo que permite CONCH ya calculado |

### 1.3 Por qué retrieval es atractivo **para nosotros en particular**

La parte cara de cualquier sistema de retrieval son **embeddings buenos** (que
"parecido visual ⇒ cercano en el espacio"). **Esa parte ya la tenemos resuelta**:
CONCH es un *foundation model* visión-lenguaje, y sus 512-dim son justo para
medir similitud. La materia prima del retrieval (los embeddings de ~3000 slides)
**ya existe y es read-only en `clam_environ`**. No hay que entrenar un encoder.

> **El matiz técnico que NO hay que pasar por alto** (punto de diseño, §3.D):
> las features CONCH son **por parche** (`[N_parches, 512]`), no **por slide**.
> Para retrieval *a nivel slide* hay que producir **un vector por slide**
> (ej. promediar los parches, o un esquema tipo mosaico). Esto es barato (CPU,
> sin entrenar) pero es una **decisión de diseño real**, no un detalle.

---

## 2. Nuestra materia prima y nuestro cuello (contra qué se evalúa cada variante)

### 2.1 Lo que TENEMOS

| Activo | Detalle | Estado |
|---|---|---|
| Features CONCH | **3013** `.pt`, `[N_parches, 512]` por slide (live count; CLAUDE.md documenta 2935 → creció) | READ-ONLY en `environ/features/pt_files/` |
| Coords / h5 | parches + coordenadas espaciales | READ-ONLY `environ/features/h5_files/` |
| Labels por task | CSVs `dataset_<task>_label.csv` (microcalc ×4, CDIS patrón ×5, invasión, …) | READ-ONLY `environ/csv/` |
| Splits k-fold | MC-CV pareados ya usados por el hilo mammoth | `data/splits_kfold/<task>_pth_100` |
| Harness pareado | `train_dsmil.py` (`--model_type dsmil\|clam\|clam_mammoth`) | nuestro, reusable |

### 2.2 El cuello diagnosticado (Hallazgos 11/12)

- **Arquitectura NO es palanca**: 8 tareas pareadas k=5 (DSMIL + mammoth +
  LongNet), **0 palancas**. Swapear/aumentar el agregador da el mismo *null*.
- **El cuello son los DATOS**: desbalance fuerte (invasión: mayoritaria
  `no_identificado` ~70%), **pocos positivos** (binarias microcalc: carcinoma
  68, cdis 121, tejido 195 de 333; CDIS micropapilar/papilar ~32 positivos),
  contexto espacial.
- **El baseline FUNCIONA** (esto es importante para el ánimo y es un dato, no
  consuelo): invasión 3-clase CLAM **bal_acc 0.622 ± 0.028 / macro-OVR AUC
  0.828 ± 0.021** ≫ trivial 0.333. Lo que NO mejoró fue *cambiar de
  arquitectura* — no el sistema entero.

> **Criterio de "sirve":** una variante de retrieval *sirve* en la medida en que
> **(a)** ataca el cuello real (datos/desbalance/pocos positivos), **o (b)**
> cambia el *frame* (entrega valor sin pelear la métrica donde ya sabemos que
> nos estrellamos). NO en que sea un método nuevo y vistoso.

---

## 3. Las 4 variantes A/B/C/D — análisis por variante

Para cada una: **(i)** qué es; **(ii)** paper(s) ancla; **(iii)** mapeo a
nuestro contexto; **(iv)** riesgo / costo / brillo dado el calendario.

### A. Agregador con *retrieval* — ⚠️ "mammoth #2"

- **(i) Qué es.** Reemplazar el *attention-pooling* de CLAM (cómo combina los N
  parches en un vector de slide) por un mecanismo basado en **vecinos**: en vez
  de pesar parches con atención aprendida, pesarlos/combinarlos según su
  cercanía a otros ejemplos recuperados.
- **(ii) Ancla.** **RAM-MIL** (Cui et al., NeurIPS 2023): usa *Optimal
  Transport* como distancia para recuperar vecinos y **aumenta** el MIL. Su
  ganancia reportada es **robustez out-of-domain** (test de otro hospital).
- **(iii) Mapeo.** Sigue siendo **un swap de agregador sobre las mismas
  features/datos**. Por nuestra propia evidencia (8 tareas, 0 palancas), la
  predicción honesta es **null**. El *único* ángulo no-redundante es el
  out-of-domain (nosotros SÍ mezclamos privado+TCGA+HistAI), pero **ese no es
  el cuello que diagnosticamos** (nuestro problema es desbalance/pocos
  positivos *dentro* de dominio, no shift entre hospitales).
- **(iv) Veredicto.** **Descartar como apuesta.** Nota al pie: si alguna vez el
  problema se reformula como *generalización cross-fuente*, RAM-MIL vuelve a la
  mesa. Hoy no.

### B. Prototipos / *memory-bank* para clases raras — ✅ ataca el cuello (pocos positivos)

- **(i) Qué es.** Guardar **prototipos por clase** (o un banco de embeddings) y
  clasificar por cercanía. Intuición: cuando hay **pocos positivos**, un
  clasificador paramétrico no tiene con qué ajustar bien la frontera; pero un
  *prototipo* (centroide de los pocos positivos que hay) + métrica de distancia
  puede ser más estable y *data-efficient*.
- **(ii) Anclas.**
  - **PathPT** [He 2025/26] — **el paper más relevante** (lo leímos). Few-shot
    para *rare cancer subtyping* con *foundation models* visión-lenguaje
    (incluye **CONCH**). No es prototipos puros: combina **(1)** agregación
    espacial liviana, **(2)** *prompt-tuning* (tokens de texto aprendibles) y
    **(3)** pseudo-labels tile-level desde el *grounding* zero-shot del modelo
    VL. Pertenece a la familia "atacar few-shot/desbalance con el prior del
    foundation model", que es el frame B.
  - **PANTHER** (CVPR 2024, mismo lab que CLAM/CONCH) — resume los parches en un
    set chico de **prototipos morfológicos** vía GMM → representación de slide
    *task-agnostic*. (No subido; pedir PDF si se profundiza.)
- **(iii) Mapeo.** Es la **única familia con evidencia nueva que apunta al
  cuello real** (pocos positivos). PathPT usa CONCH explícito y reporta ganancias
  en few-shot. **PERO** (caveat honesto de §4): sus ganancias **dependen del
  modelo base** — con CONCH son *moderadas* (KEEP fue mejor), y **chocan con el
  techo de datos**. Implementarlo bien NO es trivial (prompt-tuning + grounding
  + pseudo-labels) → es desarrollo grande con riesgo real de re-aterrizar en
  *null* si el grounding de CONCH no alcanza.
- **(iv) Veredicto.** **Apuesta de research seria, NO quick-win.** Mejor pista
  para "seguir peleando la métrica con un lever que por fin no es la
  arquitectura". Riesgo medio-alto; brillo alto si funciona; **no entra cómodo
  en la pista corta** hasta fin de mes.

### C. *Retrieval* para seleccionar parches útiles — ✅ ya es el Eje B del plan

- **(i) Qué es.** Recuperar, dentro de cada slide, los **parches más
  informativos** (los que aportan a la decisión) y descartar el resto. Ataca el
  hecho de que una WSI tiene miles de parches y la mayoría es tejido irrelevante.
- **(ii) Ancla.** PathPT hace exactamente una versión principista de esto: usa
  el *grounding* zero-shot del modelo VL para quedarse con los **tiles cuya
  predicción es "normal" o concuerda con el label de slide** → pseudo-labels
  tile-level. Es "selección de parches útiles" guiada por texto.
- **(iii) Mapeo.** Es **literalmente el Eje B "parches/slides útiles" que ya
  está en `progress/current.md`** (Objetivo 4 de B5). No es una vía nueva: es la
  que ya teníamos, ahora con una receta de la literatura.
- **(iv) Veredicto.** **Plegar al Eje B existente.** No abrir como "variante de
  retrieval" separada; sí anotar que PathPT da el patrón.

### D. CBIR — buscador "mostrame slides parecidas" — ✅ frame distinto, bajo riesgo, alto brillo

- **(i) Qué es.** *Content-Based Image Retrieval*: el patólogo sube una slide y
  el sistema le muestra las **N más parecidas del archivo** (con sus diagnósticos
  conocidos). No es subir una métrica de clasificación: es un **entregable
  clínico** ("ayuda al diagnóstico por casos similares").
- **(ii) Anclas.**
  - **[Alfasly 2024]** — lo leímos. Retrieval **zero-shot** (no altera
    embeddings, no entrena clasificador) con *foundation models* (UNI, Virchow,
    GigaPath; **no CONCH**). Pipeline Yottixel: mosaico de parches + *barcoding*
    + distancia Hamming *median-of-minimum*. Métrica = **macro-F1** de top-1 /
    mayoría top-3 / mayoría top-5.
  - **SISH** (Chen et al., *Nat Biomed Eng* 2022, mismo lab que CLAM/CONCH) — el
    paper fundacional de búsqueda de WSI O(1), pensado **explícitamente para
    rare cancers** con pocas WSIs. (No subido; pedir PDF si se profundiza.)
- **(iii) Mapeo.** **El mejor encaje con lo que tenemos AHORA**: usa CONCH como
  está (vía un vector por slide, §1.3), **NO entrena nada** (regla 9 se cumple
  trivial: es indexar + buscar, no model training), corre en **CPU** (sin GPU),
  y vive 100% dentro de containment. **Cambia el frame**: no compite contra el
  baseline en una métrica que ya sabemos rígida; produce una herramienta.
- **(iv) Veredicto.** **La apuesta para la presentación.** Bajo riesgo, alto
  brillo, *lucible*, tratable en pista corta. **Caveat** (§4): como *clasificador*
  el retrieval zero-shot es modesto en problemas fine-grained de 100+ clases;
  hay que **venderlo como herramienta** y **validarlo con números honestos en
  NUESTRAS tareas de 2–3 clases** (donde debería ir mucho mejor que el 117-vías
  del paper).

---

## 4. Lo que dicen los 2 papers leídos (evidencia anclada, con sus caveats)

> Esta sección es la que sostiene la recomendación con **números reales**, no
> con hype. Los dos papers, leídos a fondo, **refuerzan nuestra tesis** más de
> lo que la contradicen.

### 4.1 [Alfasly 2024] — Zero-Shot WSI Retrieval (frame D)

**Qué hicieron.** Retrieval **zero-shot** de WSI completas sobre TCGA (11,444
WSIs, 9,339 pacientes, **23 órganos, 117 subtipos**). No entrenan nada: toman
embeddings de *foundation models* y buscan por similitud con el motor Yottixel
(mosaico de parches 224×224 al 2% + *barcoding* + Hamming *median-of-minimum*).

**Números (macro-F1, mayoría top-5):**

| Backbone | Top-1 | Mayoría @3 | Mayoría @5 |
|---|---|---|---|
| DenseNet (ImageNet) | 28% | 28% | 27% |
| UNI | **44%** | **44%** | **42%** |
| Virchow | 41% | 41% | 40% |
| GigaPath | 43% | 43% | 41% |

**Mama específicamente** (Tablas 2–4, *organ = Breast*): top-1 UNI ≈ **0.27**,
mayoría@3 ≈ 0.30, mayoría@5 ≈ 0.31 — de las más bajas (los subtipos de mama
están muy desbalanceados: *infiltrating duct* 805 WSIs vs *medullary* 7).

**Cómo leerlo HONESTO (no es malo para D, hay que entender qué mide):**
- Es un problema **brutal**: discriminar **117 subtipos finos** por similitud,
  sin entrenar. Nuestras tareas son de **2–3 clases**. El 0.42 macro-F1 **NO es
  comparable** a lo que esperaríamos en invasión (3 clases) o las binarias.
- **No testearon CONCH** — testearon modelos visión-only (UNI/Virchow/GigaPath).
  CONCH es visión-**lenguaje**; sus embeddings de imagen sirven para CBIR, pero
  *no está medido aquí*. (Y §4.2 sugiere que CONCH no es el mejor para tareas
  zero-shot — caveat real.)
- Su conclusión textual: *"not yet adequate for clinical application"* **como
  clasificador**, pero enmarcan el retrieval como *"aiding diagnosis through
  similarity matching"* — es decir, **la herramienta CBIR (mostrar casos
  parecidos) tiene valor aunque el voto top-k no sea clínico-grado**. Eso es
  exactamente el frame D.
- *"The challenge of representing an entire WSI with a single vector remains
  unresolved"* → confirma el **punto de diseño de §1.3** (cómo pasar de parches
  a un vector de slide es LA decisión).

**Qué nos da:** una **plantilla de método** (mosaico/embedding-kNN) + **expectativas
honestas** (modesto como clasificador en fine-grained; útil como buscador). Para
nosotros, el experimento barato es: **voto mayoritario top-k sobre NUESTRAS
tareas de 2–3 clases**, que debería superar con holgura los números 117-vías.

### 4.2 [He 2025/26] — PathPT (frame B) — **el paper que más nos sirve, y confirma nuestra tesis**

**Qué hicieron.** Few-shot (1/5/10 shots, ×10 repeticiones) para *rare cancer
subtyping*. 8 datasets raros (4 adulto + 4 pediátrico, 56 subtipos, ~2,910 WSIs)
+ 3 comunes. **Modelos base VL**: PLIP, **CONCH**, MUSK, KEEP. **Baselines MIL**:
ABMIL, **CLAM**, TransMIL, DGRMIL (todos sobre features tile-level de los VL).
PathPT = (1) agregación espacial + (2) prompt-tuning (tokens de texto
aprendibles) + (3) pseudo-labels tile-level desde *grounding* zero-shot.

**Por qué este paper es oro para NOSOTROS (3 lecturas):**

1. **CLAM + CONCH es un baseline ahí.** O sea, nuestro setup exacto está en el
   benchmark. Da legitimidad y comparabilidad.

2. **Confirma "cuello = datos", no nosotros solos.** En pediátrico, a 10-shot
   **PathPT, TransMIL y DGRMIL convergen a 0.54–0.55** y el paper lo llama
   *"a ceiling imposed by limited data"*. Es **la misma conclusión que nuestros
   Hallazgos 11/12**, dicha por un grupo independiente con un método mucho más
   sofisticado: cuando faltan datos, **el método deja de ser la palanca**. Esto
   es algo *presentable* y *reencuadrante* para Ernesto: "no es que falle
   nuestro modelo; es un límite estructural de datos que la literatura SOTA
   también choca".

3. **Caveat fuerte que nos AHORRA una mala apuesta.** PathPT con base
   **PLIP/MUSK/CONCH "underperformed MIL baselines"** en EBRAINS, *"likely due
   to the relatively poor performance of the original VL model"* en grounding
   zero-shot → **malos pseudo-labels**. **KEEP** (el que mejor *grounding*
   zero-shot tiene) fue el único que ganó claro (PathPT-KEEP EBRAINS **0.679**
   bal-acc a 10-shot, +0.271 sobre zero-shot). **Implicación directa**: si
   replicáramos PathPT **con CONCH** (que es lo que tenemos), estaríamos en el
   brazo *moderado*, no en el ganador. Meterse en ese desarrollo grande con
   CONCH tiene riesgo real de **null #2**. (Para ganar habría que conseguir
   KEEP — otra dependencia, otro encoder, fuera de lo que tenemos hoy.)

**Números útiles de contexto:** común — UBC-OCEAN **0.820**, TCGA **0.769**
(PathPT-KEEP, 10-shot). Mama (TCGA-BRCA) = 2 subtipos (ductal vs lobular
invasivo). El set "común" son 548 WSIs / 10 subtipos.

**Qué nos da:** **(a)** munición de reencuadre (el techo de datos es real y
SOTA); **(b)** el *lever* genuino para el cuello (texto + grounding + few-shot),
pero **(c)** con la advertencia de que rinde según el modelo base, y CONCH no es
el campeón → **apuesta de research, no de pista corta**.

---

## 5. Análisis comparativo y recomendación razonada

### 5.1 Tabla comparativa

| Var. | Ataca el cuello (datos)? | Usa CONCH as-is? | Entrena / GPU? | Riesgo "null #2" | Brillo presentación | Encaje calendario |
|---|---|---|---|---|---|---|
| **A** agregador-retrieval | ❌ (swap arquitectura) | sí | sí (entrena) | **Alto** (es mammoth #2) | bajo | malo |
| **B** prototipos/few-shot (PathPT) | ✅ pocos positivos | parcial (CONCH ≠ KEEP) | sí (entrena) | medio-alto | alto si funciona | **malo** (desarrollo grande) |
| **C** parches útiles | ✅ (es el Eje B) | sí | sí (entrena) | medio | medio | medio (ya en plan) |
| **D** CBIR | ⟂ cambia el frame | **sí, ideal** | **no** (indexar+buscar) | **bajo** | **alto** | **bueno** (CPU, sin entrenar) |

(⟂ = "ortogonal": no pelea la métrica donde nos estrellamos; entrega valor por otro eje.)

### 5.2 Recomendación (razonamiento propio, no copiado del handoff)

**Para la presentación (recta corta a fin de mes): D — CBIR.** Razones:
- **Encaja con el cuello por la vía (b)**: no pelea la métrica de clasificación
  (que sabemos rígida por datos); entrega una **herramienta** que aprovecha
  exactamente lo que SÍ funciona (CONCH + banco grande de slides).
- **Riesgo mínimo y feasibility máxima**: sin entrenar (regla 9 trivial), sin
  GPU, CPU, dentro de containment. Un MVP honesto: **mean-pool de los parches
  CONCH → 1 vector/slide → índice coseno → kNN**; validar con **voto top-k en
  nuestras tareas de 2–3 clases** + mostrar *"casos parecidos"* cualitativos.
- **Brillo y reencuadre**: es *lucible* (un buscador clínico se ve y se
  entiende), y permite contar la historia honesta — "el baseline funciona; la
  arquitectura no es la palanca (resultado real); acá hay un uso del foundation
  model que entrega valor sin chocar el techo de datos".
- **Caveat a respetar (de [Alfasly 2024])**: presentarlo como **herramienta de
  apoyo**, no como clasificador clínico-grado; reportar números honestos en
  *nuestras* tareas (no extrapolar el 117-vías del paper).

**Para el trimestre siguiente / si Ernesto continúa: B — few-shot estilo
PathPT.** Es la **única** dirección con evidencia nueva que ataca el cuello real
(pocos positivos vía prior de texto + grounding), pero **con los ojos abiertos**:
PathPT gana con **KEEP**, no con CONCH; con CONCH el resultado esperable es
*moderado*; y hay un **techo de datos** que incluso PathPT choca. Es apuesta de
research, va a branch nueva + reviewer + hipótesis pre-registrada (regla 9.b si
toca algo descartado).

**C** se pliega al **Eje B "parches útiles"** ya planificado (PathPT = receta).
**A** queda **descartado** (mammoth #2), con nota al pie del ángulo out-of-domain.

### 5.3 Por qué esta recomendación es coherente con lo que ya probamos

La lección de las 8 tareas (Hallazgos 11/12) es: **no inviertas en otro swap de
arquitectura — da null.** A y (en parte) C/B-como-agregador son swaps; **D no es
un swap**, es un uso distinto del mismo activo. Y la pieza de evidencia más
fuerte —que PathPT *también* choca un techo de datos— dice que seguir peleando
la métrica con métodos más grandes tiene rendimientos decrecientes. **D escapa
de esa pelea; B la pelea con el mejor lever disponible pero sin garantías.**

---

## 6. (Opcional, sin implementar) Esbozo de hipótesis regla 9 para D

> Esto es un **boceto** para la sesión siguiente (con reviewer + branch). NO es
> la pre-registración formal ni implica código.

- **Hipótesis (mecanismo).** Si los embeddings CONCH agrupan "parecido visual ⇒
  cercano", entonces un kNN sobre vectores de slide debería **recuperar casos
  del mismo label** por encima del azar, **y mejor en nuestras tareas de 2–3
  clases que el 117-vías de [Alfasly 2024]**.
- **Métrica + subset + dirección (política B5).** Sobre cada task (invasión,
  binarias microcalc, CDIS patrón): **macro-F1 de voto mayoritario top-k**
  (k∈{1,3,5}) **+ balanced_acc + matriz de confusión + n por clase**, evaluado
  **con los mismos splits** que el baseline CLAM (pareado). Dirección esperada:
  **F1/bal_acc del kNN > trivial**, y **idealmente comparable al CLAM** en las
  tareas fáciles (si el kNN ≈ CLAM con *cero entrenamiento*, es un resultado
  fuerte; si queda por debajo, sigue siendo válido como *herramienta CBIR*).
- **Variable de diseño a ablacionar:** representación de slide (mean-pool vs
  mosaico vs prototipo) — §1.3. Es la decisión de mayor impacto.
- **Qué NO promete:** superar a CLAM como clasificador (el valor está en el
  *frame* CBIR + el "sin entrenar"). No es un GO/NO-GO numérico rígido (regla
  9.a): es dirección + consistencia + n.

---

## 7. Caveats, riesgos y qué NO hacer

- **NO vender CBIR como clasificador clínico-grado** — [Alfasly 2024] muestra
  que zero-shot retrieval es modesto en fine-grained. Venderlo como *herramienta
  de apoyo* + validar honesto en nuestras 2–3 clases.
- **NO replicar PathPT con CONCH esperando los números de KEEP** — el paper es
  explícito en que la ganancia depende del grounding del base model.
- **NO recomendar A** sin el caveat "mammoth #2" (nuestra propia evidencia).
- **El punto de diseño slide-vector (§1.3) es real** — mean-pool es el MVP, pero
  pierde la estructura MIL/espacial; documentarlo como limitación.
- **CONCH no está medido para retrieval en [Alfasly 2024]** — cualquier número
  que demos es *nuestro*, hay que generarlo (sesión siguiente), no asumirlo.
- **Discrepancia de inventario menor**: live count = 3013 features vs 2935
  documentado en CLAUDE.md. No afecta el análisis; conviene reconciliarlo en un
  `/knowledge-audit` o al armar el índice.

---

## 8. Próximos pasos

1. **Cerrar este análisis con Ernesto** (explicación interactiva — abajo).
2. Si elige **D**: sesión nueva → pre-registración formal regla 9 + branch +
   reviewer; MVP = mean-pool CONCH → índice coseno → kNN top-k en CPU; validar
   en invasión + binarias (paired vs CLAM). **Sin GPU.**
3. Si elige **B**: tratarlo como research de trimestre siguiente; conseguir/
   evaluar KEEP como base; hipótesis pre-registrada; branch + reviewer.
4. **Pedir PDFs** de **SISH** y **PANTHER** si se quiere profundizar las anclas
   D y B (no subidos al 5-jun).
5. (Higiene) reconciliar el conteo 3013 vs 2935 en un `/knowledge-audit`.

---

*Fase de argumento (regla 9). No se tocó modelo, no se usó GPU, no se entrenó.
Todo claim anclado a los 2 PDFs leídos o al código/datos reales (regla 5).*
