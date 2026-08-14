# Jaroensri 2022: todo lo verificado contra el PDF, listo para escribir las tres hojas

> **Escrito el 13-ago-2026** en la sesión que bajó y leyó el paper pero **no alcanzó a escribir
> los tres entregables** (`busqueda.md`, `jaroensri_estudio.md`, `hoja_jaroensri.md`).
>
> **Para qué existe este archivo:** que la sesión que continúe escriba los tres documentos
> **sin volver a leer el PDF**. Todos los números de acá salen del texto del artículo o de su
> Supplementary, con la referencia al lado. Los PDF están en esta carpeta:
> `jaroensri_2022_npjbc.pdf` (12 pág., el artículo) y `supp.pdf` (el Supplementary), más los
> volcados `jaroensri.txt` y `supp.txt` de `pdftotext -layout`.
>
> Lo que falta es **redacción**, no investigación.

---

## 0. Ficha

> Jaroensri R, Wulczyn E, Hegde N, Brown T, Flament-Auvigne I, Tan F, Cai Y, Nagpal K, Rakha EA,
> Dabbs DJ, Olson N, Wren JH, Thompson EE, Seetao E, Robinson C, Miao M, Beckers F, Corrado GS,
> Peng LH, Mermel CH, Liu Y, Steiner DF, Chen P-HC. *Deep learning models for histologic grading
> of breast cancer and association with disease prognosis*. **npj Breast Cancer 8:113 (2022).**
> DOI `10.1038/s41523-022-00478-y` · PMC9530224 · PMID 36192400. **Acceso abierto.**
> Recibido 7-feb-2022, aceptado 1-sep-2022, publicado 4-oct-2022. Google Health.

**Ojo con el DOI**, porque se parece al de Mercan (Hoja 6 de `papers_11_agosto/`): Mercan es
`s41523-022-00488-w`, **este es `s41523-022-00478-y`**. Los dos son npj Breast Cancer 2022.

---

## 1. Por qué es EL candidato: es literalmente el pipeline de Sebastián, publicado

El pipeline que propuso Sebastián es: CLAM y su mapa de calor eligen dónde mirar, y sobre los
parches de mayor atención corre un **segundo modelo especialista** de mitosis, pleomorfismo o
grado nuclear.

Jaroensri hace **exactamente esa forma**, con otro selector:

```
WSI -> modelo de carcinoma invasivo (10x, parche 1024)  ->  MÁSCARA de invasivo
                                                              │
                                            (acá nosotros ponemos la atención de CLAM)
                                                              │
                                                              v
                            ETAPA 1: tres modelos de PARCHE, uno por componente
                              MC (40x, parche 128)  NP (40x, parche 1024)  TF (10x, parche 1024)
                                                              │
                                                              v
                            ETAPA 2: clasificador liviano -> puntaje de LÁMINA 1-3
                              MC: regresión logística sobre percentiles de densidad mitótica
                              NP y TF: regresión ridge sobre el softmax medio por parche
```

**Es el único candidato que ataca los TRES componentes de Nottingham a la vez**, que son
exactamente nuestras tres etiquetas CAP. Y su etapa 2 es un clasificador de scikit-learn, no
otro MIL: la parte cara ya la hace la etapa 1.

---

## 2. Los números, todos verificados

### 2.a Rendimiento por componente (Tabla 2 del artículo)

| Nivel | Componente | Métrica | Resultado [IC 95 %] |
|---|---|---|---|
| **Parche** | Recuento mitótico | F1 de detección | **0,60** [0,58 · 0,62] |
| **Parche** | Pleomorfismo nuclear | kappa cuadrático | **0,45** [0,41 · 0,50] |
| **Parche** | Formación tubular | kappa cuadrático | **0,70** [0,63 · 0,75] |
| **Lámina** | Recuento mitótico | kappa cuadrático | **0,81** [0,78 · 0,84] |
| **Lámina** | Pleomorfismo nuclear | kappa cuadrático | **0,48** [0,43 · 0,53] |
| **Lámina** | Formación tubular | kappa cuadrático | **0,75** [0,67 · 0,81] |

### 2.b El dato que hay que llevar por nuestra política de eval (Suppl. Tabla 1)

El artículo titula con kappa; el Supplementary trae **balanced accuracy**, que es la métrica que
nosotros exigimos reportar siempre ([[eval-reporte-auc-y-umbrales-obj6]]). Cambia la lectura:

| Componente (parche) | Accuracy | **Balanced accuracy** | kappa sin ponderar |
|---|---|---|---|
| Pleomorfismo nuclear | 0,67 | **0,50** | 0,40 |
| Formación tubular | 0,93 | **0,67** | 0,54 |

Con tres clases el trivial es 0,333. **Pleomorfismo a nivel de parche está en 0,50 de balanced
accuracy**, o sea despega del trivial pero poco, y su accuracy de 0,67 vive del desbalance. Es
el mismo patrón que nosotros documentamos en microcalcificaciones (Hallazgo 6). Conviene decirlo
nosotros antes de que lo pregunten.

Recuento mitótico a nivel de parche: **precisión 0,76 · recall 0,50**. El F1 de 0,60 es un
recall a la mitad.

### 2.c Contra el desacuerdo entre patólogos (Fig. 4 y Suppl. Tabla 2A)

| | MC | NP | TF |
|---|---|---|---|
| Acuerdo **entre patólogos** (kappa cuadrático) | 0,56 | 0,36 | 0,55 |
| Acuerdo **modelo–patólogo** | **0,64** | **0,39** | **0,69** |
| Modelo contra el voto de mayoría | 0,81 | 0,48 | 0,75 |

**El modelo concuerda con los patólogos mejor de lo que los patólogos concuerdan entre sí, en
los tres componentes.** Ese es el argumento de «aumenta métricas» en su forma más fuerte, y no
necesita un baseline de arquitectura: el baseline es el humano.

### 2.d Valor pronóstico (Tablas 3, 4 y 5)

- c-index para intervalo libre de progresión, sobre 829 casos de TCGA: **0,58** el modelo
  (suma continua) contra **0,58** los patólogos (suma discreta). Delta 0,004, cota inferior del
  IC unilateral 95 % −0,036, con margen de no inferioridad prefijado en 0,075 → **no inferior**.
- Con el grado combinado: **0,60** el modelo contra 0,58 los patólogos.
- Sumando a las variables clínicas de base (edad, TNM, estado de RE): base sola 0,74, base más
  modelo **0,76** (p = 0,036 en test de razón de verosimilitud).
- De los tres componentes, **solo el recuento mitótico** tiene valor pronóstico independiente
  (HR 1,30, p = 0,015 univariable).
- El recuento mitótico del modelo **correlaciona con Ki-67 mejor que el del patólogo**: 0,47
  contra 0,37, p = 0,002 en test de permutación.

### 2.e Datos

- Tres fuentes: un hospital terciario (TTH, 657 casos / 1502 láminas), un laboratorio médico
  (MLAB, 98/98) y **TCGA (829 casos / 878 láminas)**.
- **TTH y MLAB para desarrollo, TCGA solo para evaluar.** Para evaluar el grado se usan 662
  casos / 685 láminas (se excluyen las láminas sin mayoría entre patólogos).
- **TCGA es nuestra cohorte también.** El test set de este paper es un conjunto que tenemos.

---

## 3. La cuenta que necesita la hoja: escala física y cuántos parches

### 3.a Configuración de cada modelo (Suppl. Tabla 8, verbatim)

| Modelo | Magnificación | Parche (px) | **Campo físico** |
|---|---|---|---|
| Carcinoma invasivo | 10× | 1024 | 1024 µm ≈ 1 mm |
| **Recuento mitótico** | **40×** | **128** | **32 µm** |
| **Pleomorfismo nuclear** | **40×** | **1024** | **256 µm** |
| **Formación tubular** | **10×** | **1024** | ≈ 1 mm |

Arquitectura: BiT-L (ResNet50x1) preentrenada en JFT, softmax cross-entropy, normalización de
tinción, 1 M de pasos con early stopping. Batch 32 salvo pleomorfismo, que va en 8.

### 3.b **El hallazgo que más nos toca, y es una frase del Methods**

> «All WSIs used in this study were scanned at 0.25 μm/pixel (40×). The small number of TCGA
> images in the BRCA study scanned at **0.50 μm/pixel (20×) were excluded** in order to ensure
> availability of 40x for DLS-based MC and NP grading.»

**Un grupo con los recursos de Google prefirió tirar láminas antes que correr mitosis y
pleomorfismo a 20×.** Nuestra cohorte privada está **entera** a 0,4650 µm/px con
`objective-power = 20` (verificado el 13-ago sobre las 490 láminas con `.bif`, sin una sola
excepción, en `../anotaciones_patologo/regiones_escaneo/resultados.md` §3).

Consecuencia, y conviene decirla como cuenta y no como opinión:

| Rama | Campo que pide | En nuestro privado (0,465 µm/px) | En TCGA (0,2325 µm/px) |
|---|---|---|---|
| Mitosis | 32 µm a 0,25 µm/px = 128 px | 69 px, hay que **ampliar 1,86×** (inventar detalle) | 138 px, baja a 128 sin problema |
| Pleomorfismo | 256 µm a 0,25 µm/px = 1024 px | 551 px, **ampliar 1,86×** | 1101 px, baja a 1024 |
| **Formación tubular** | 1 mm a 1,0 µm/px = 1024 px | 2202 px, **se reduce**: sin problema | 4404 px, se reduce |

**Formación tubular es el único de los tres que nuestro privado puede alimentar sin inventar
resolución.** Es un resultado nuevo y no estaba dicho en ningún documento del sprint: hasta
ahora la escala se discutía para mitosis (en contra) y pleomorfismo (a favor, por Mercan a
0,5 µm/px). Este paper dice que a 40× **pleomorfismo también** queda del lado difícil, porque
él lo corre a 0,25 y no a 0,5.

### 3.c Cuántos parches por lámina, con nuestros números

Nuestro parche es 256 px a 0,465 µm/px = **119 µm**. Con los 20 parches de mayor atención que
propuso Sebastián:

- **Mitosis**: cada parche nuestro contiene 3,7 × 3,7 ≈ **14 ventanas** de 32 µm, o sea unas
  **280 inferencias** de un ResNet50 sobre 128 px por lámina. Es nada.
- **Pleomorfismo**: el campo del modelo (256 µm) es **más grande que nuestro parche** (119 µm),
  así que hay que centrar una ventana de 551 px en cada parche de atención y ampliarla a 1024:
  **20 inferencias** por lámina, con solapamiento entre parches vecinos.
- **Formación tubular**: el campo (1 mm) es **ocho veces** nuestro parche. Acá el top-k de CLAM
  casi no ahorra nada, porque una sola ventana del modelo ya cubre 70 parches nuestros.

**Esa última línea es un hallazgo de diseño, no un detalle**: el recorte por atención rinde
muchísimo para mitosis, algo para pleomorfismo, y **casi nada para formación tubular**. La
ganancia del pipeline de dos etapas depende de la razón entre el campo del especialista y el
parche del selector.

---

## 4. Lo que lo frena, y hay que decirlo en la hoja

1. **No hay pesos.** Textual del Code Availability: *«The final, trained models have not yet
   undergone regulatory review and cannot be made available at this time.»* Lo público es el
   framework (TensorFlow 1.14), la ResNet50x1 de BiT, y el código de la **etapa 2**
   (`github.com/Google-Health/google-health/tree/master/breast_survival_prediction`). La etapa
   1, que es la que nos interesa, **hay que entrenarla**.
2. **La supervisión de la etapa 1 no es la nuestra.** Necesita **3 regiones de 1 × 1 mm por
   lámina**, cada una anotada por **3 patólogos** de un pool de 10: mitosis exhaustivas dentro
   de la región (y solo cuentan las que 2 de 3 marcan) y puntaje 1-3 por región para
   pleomorfismo y tubular. Nosotros tenemos **61 polígonos en una lámina**, y son positivos
   parciales ([[anotaciones-patologo-qupath]]).
   - **El matiz que salva media pregunta:** para pleomorfismo y tubular la etiqueta de parche
     es el **puntaje de la región propagado a todos los parches** que caen dentro. No es
     anotación por objeto. Es una anotación mucho más barata que marcar núcleos, y es
     exactamente lo que se le podría pedir al patólogo.
   - Y sus cajas de mitosis son de **16 µm**, contra las nuestras de 16,7 µm. Prácticamente la
     misma convención: nuestras marcas servirían para evaluar sin inventar tolerancias.
3. **Un resultado negativo suyo que toca a NPKC-MIL.** Textual: para pleomorfismo probaron
   además *«a hand-engineered nuclear segmentation-based approach»* y **no mejoró**, y lo
   atribuyen a la variabilidad de tinción y de aspecto celular en los casos de grado alto.
   NPKC-MIL (Hoja 5 de `papers_11_agosto/`) propone justamente features de núcleo hechas a
   mano. **Es evidencia en contra de esa rama, de un grupo con más datos**, y conviene tenerla
   a mano en la reunión.
4. **Pleomorfismo es su componente flojo**, en todas las métricas y en los dos niveles (kappa
   0,45 parche / 0,48 lámina, balanced accuracy 0,50). Y es la tarea que Sebastián quiere
   atacar. El propio panel de patólogos concuerda 0,36, así que el techo es bajo, pero no
   conviene prometer.
5. Seguimiento corto en TCGA (mediana ~2 años), sin control por tratamiento, y la mayoría de
   los casos aporta una sola lámina. Ellos lo listan como limitación.

---

## 5. Los otros candidatos, para el rubric de `busqueda.md`

Verificados por búsqueda web, **no** por PDF (marcarlo así en el documento).

| Candidato | 1 · parche | 2 · supervisión | 3 · ganancia | 4 · µm/px | 5 · abierto |
|---|---|---|---|---|---|
| **Jaroensri 2022** (el elegido) | **sí**, los tres modelos son de parche | parcial: pesos no, etiqueta de región sí | **sí**: supera el acuerdo entre patólogos en 3/3 | **sí**, 0,25 declarado | artículo sí, **pesos no** |
| **MIDOG 2025 overview**, arXiv `2606.07368` (5-jun-2026) | sí | pesos de los equipos | F1 **0,740** detección, balanced acc **0,908** en atípicas, sobre 365 casos y 12 tipos tumorales | 0,23–0,26 en MIDOG | sí |
| **YOLO11x + ConvNeXt dos etapas**, arXiv `2509.02627` | sí | anotación de objeto | F1 **0,882** contra 0,847 de una etapa (+0,035); precisión 0,762 → 0,839; **0,7587** en el test preliminar de MIDOG 2025 | idem MIDOG | sí, código en `github.com/xxiao0304/MIDOG-2025-Track-1-of-SZTU` |
| **Diagnostics 14(18):2045 (2024)**, PMC11431806 | núcleo | exige segmentar con CellProfiler | acc 0,97 sobre **600 núcleos elegidos a mano** (200 por clase) | **no lo declara** | artículo sí, **datos y código no** |

**El Diagnostics queda descartado de forma limpia**, y conviene dejar dicho por qué, porque el
handoff lo traía con una esperanza concreta: se lo fichó para ver «si mide de forma relativa al
vecindario», que es lo que pidió el patólogo y lo que ninguna de las 16 features de NPKC-MIL
hace. **La respuesta es que no**: evalúa cada núcleo aislado. Además son 600 núcleos
seleccionados, no láminas, así que su 0,97 no es comparable con nada nuestro.

**El dato de MIDOG 2025 que vale por sí solo**, y que valida la primera etapa del pipeline de
Sebastián desde afuera: fuera de los puntos calientes curados, la tasa de falsos positivos de
los detectores de mitosis **se triplica** (aumento del **208 %**). O sea que correr el detector
sobre la lámina entera es justamente lo que no hay que hacer, y **restringirlo a los parches de
mayor atención es la forma correcta del problema**, medida por un challenge con 365 casos. Es
el mejor argumento externo que tenemos para el diseño de dos etapas, y no depende de que
Jaroensri gane el rubric.

---

## 6. Lo que las tres hojas tienen que contestar (§2.d del handoff)

1. **¿Cómo entra después del top-k de CLAM?** Está en §3.c: 280 inferencias por lámina para
   mitosis, 20 para pleomorfismo, y para tubular el top-k casi no ahorra.
2. **¿Con qué supervisión lo entrenaríamos?** Está en §4.2: la etapa 1 pide puntaje por región
   de 1 mm², no anotación por objeto, y eso es un pedido realista al patólogo. La etapa 2 se
   entrena con la etiqueta de lámina que ya tenemos del CAP.
3. **¿Qué métrica nuestra se movería, sobre qué tarea, en qué dirección?** Enunciar como
   dirección esperada, **sin umbral de pass/fail** (regla 9.a). El candidato natural es
   `pleomorfismo_nuclear`, hoy en 0,77 ± 0,046 de AUC a 5 folds. Y conviene decir que **la rama
   con mejor pinta técnica es formación tubular** (§3.b: es la única que nuestro privado
   alimenta sin ampliar), aunque no sea la que Sebastián nombró.

**Nada de esto es un pre-registro.** Regla 9: si alguna rama avanza, va con hipótesis
pre-registrada, métrica y dirección, y `reviewer` antes de tocar código.

Estilo de las hojas: **sin guiones largos**, sin «palanca», coma decimal (`96,25`), y si el
texto va a boca de Ernesto, pasada de `@humanizer-es`. **Ernesto no leyó ninguno de los papers
anteriores**: la hoja carga el peso explicativo, es su material de estudio.
