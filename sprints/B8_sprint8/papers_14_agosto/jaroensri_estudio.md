# Jaroensri 2022: estudio

> Jaroensri R, Wulczyn E, Hegde N, Brown T, Flament-Auvigne I, Tan F, Cai Y, Nagpal K, Rakha EA,
> Dabbs DJ, Olson N, Wren JH, Thompson EE, Seetao E, Robinson C, Miao M, Beckers F, Corrado GS,
> Peng LH, Mermel CH, Liu Y, Steiner DF, Chen P-HC. *Deep learning models for histologic grading
> of breast cancer and association with disease prognosis*. **npj Breast Cancer 8:113 (2022).**
> DOI `10.1038/s41523-022-00478-y` · PMC9530224 · PMID 36192400. **Acceso abierto.** Google Health.
> PDF en [`jaroensri_2022_npjbc.pdf`](jaroensri_2022_npjbc.pdf) (12 pág.) y el Supplementary en
> [`supp.pdf`](supp.pdf). **No se bajaron pesos** (no los publican, §10).
>
> **Bajado y leído el 13-ago-2026.** Por qué se lo eligió, y contra qué compitió:
> [`busqueda.md`](busqueda.md). La versión de una página para la reunión:
> [`hoja_jaroensri.md`](hoja_jaroensri.md). Los números crudos con su referencia al PDF:
> [`notas_extraccion_jaroensri.md`](notas_extraccion_jaroensri.md).
>
> Contraparte obligatoria: [`../papers_11_agosto/hojas_papers_nuevos.md`](../papers_11_agosto/hojas_papers_nuevos.md),
> porque este paper **corrige el encuadre de escala** que traíamos del 11-ago (§7) y trae
> **evidencia en contra de la rama de NPKC-MIL** (§8).
>
> **Ojo con el DOI:** Mercan, el de pleomorfismo, es `s41523-022-00488-w`; **este es `00478-y`**.

---

## 1. Qué propone, en una frase

Puntuar el **grado histológico de Nottingham** de forma automática separándolo en sus tres
componentes, con un modelo de **parche** por componente, sobre la región de carcinoma invasivo
que otro modelo segmenta antes, y agregando a puntaje de lámina con un clasificador liviano de
scikit-learn.

Con eso responden dos preguntas distintas: si el sistema concuerda con los patólogos, y si su
puntaje **sirve para pronosticar**, que es la parte que hace al paper más que un benchmark.

## 2. La arquitectura, y dónde entraríamos nosotros

```
WSI
 │
 ├─ ETAPA 0: modelo de CARCINOMA INVASIVO (10×, parche 1024 px)
 │            3 clases: no tumor / carcinoma in situ / carcinoma invasivo
 │            argmax por parche  ->  MÁSCARA de invasivo
 │                        │
 │        ┌───────────────┘   (acá entraría la atención de CLAM, en lugar de esta máscara)
 │        │
 ├─ ETAPA 1: tres modelos de PARCHE, uno por componente, solo dentro de la máscara
 │            MC (40×, 128 px)     NP (40×, 1024 px)     TF (10×, 1024 px)
 │                        │
 └─ ETAPA 2: clasificador liviano  ->  puntaje de LÁMINA 1 a 3, por componente
              MC: regresión logística sobre percentiles de densidad mitótica
              NP y TF: regresión ridge sobre el softmax medio por parche
```

**Son cuatro modelos profundos, no uno**, y ninguno es un MIL. Ese es el punto: la casilla que
este paper llena es la del **especialista de parche**, no la del agregador.

### 2.a La etapa 0, que es la que nosotros reemplazaríamos

El modelo de carcinoma invasivo se entrena con anotaciones de patólogo de tres clases (no tumor,
carcinoma in situ, carcinoma invasivo), pedidas como **anotaciones gruesas de regiones con al
menos 70 % de pureza tumoral**. En el conjunto de ajuste da **AUC 0,95** de invasivo contra las
otras dos clases. La máscara se arma aplicando **argmax por parche de 1024 × 1024** sobre el mapa
de probabilidad y quedándose con los parches cuya clase más probable es invasivo.

**La sustitución que proponemos no es neutra, y conviene decirlo antes de que lo pregunten.** Su
máscara es **semántica**: dice «esto es tejido invasivo», entrenada contra anotación de patólogo.
Nuestra atención de CLAM es un **ranking de saliencia** entrenado solo con etiqueta de lámina. No
son el mismo objeto. A favor nuestro juegan dos cosas: la supervisión es mucho más barata (no
anotamos nada) y **tenemos una medición propia de que el ranking cae donde debe**, al menos en
una lámina (AUC de atención 0,890 ± 0,039 sobre los parches con mitosis marcada, en los cuatro
checkpoints que nunca la vieron;
[`../atencion_vs_patologo/resultados.md`](../atencion_vs_patologo/resultados.md)). En contra
juega que un ranking top-k **no es una máscara de tejido**: no hay garantía de que los 20 mejores
parches sean todos invasivo, ni de que cubran el invasivo que importa.

### 2.b La etapa 1, con las configuraciones exactas

Del Supplementary, Tabla 8:

| Modelo | Magnificación | Parche (px) | **Campo físico** |
|---|---|---|---|
| Carcinoma invasivo | 10× | 1024 | 1024 µm ≈ 1 mm |
| **Recuento mitótico (MC)** | **40×** | **128** | **32 µm** |
| **Pleomorfismo nuclear (NP)** | **40×** | **1024** | **256 µm** |
| **Formación tubular (TF)** | **10×** | **1024** | ≈ 1 mm |

Arquitectura: **BiT-L (ResNet50x1)** preentrenada en JFT, softmax cross-entropy, normalización de
tinción, 1 M de pasos con early stopping, batch 32 salvo pleomorfismo que va en 8. Los
hiperparámetros, **incluidos el tamaño de parche y la magnificación**, se eligieron por
componente con Vizier más búsqueda en grilla.

**Ese último detalle vale por sí solo**: los tres campos físicos de arriba no son una convención
heredada, son el resultado de una búsqueda. Que a mitosis le convenga 32 µm y a pleomorfismo
256 µm es un hallazgo suyo, no un supuesto.

### 2.c La etapa 2, que es sorprendentemente barata

- **MC**: se calculan **densidades mitóticas** sobre la máscara de invasivo y se le pasan al
  clasificador los percentiles **5, 25, 50, 75 y 95** de esa distribución por lámina.
  Clasificador: **regresión logística**.
- **NP y TF**: la entrada es el **softmax medio por parche** para cada puntaje posible (1, 2, 3)
  sobre la región invasiva. Clasificador: **regresión ridge**, elegida por simplicidad y porque
  permite generar puntajes continuos. Probaron también logística y random forest, con rendimiento
  comparable.
- Todos regularizados, con la fuerza de regularización elegida por validación cruzada de 5 folds
  sobre el conjunto de entrenamiento.

**Lo que la etapa 2 le dice a nuestra discusión de operadores.** Veníamos con que mitosis es un
**máximo local** en el punto caliente y pleomorfismo es un **promedio**, y que las dos tareas
piden operadores opuestos ([`../papers_11_agosto/hojas_papers_nuevos.md`](../papers_11_agosto/hojas_papers_nuevos.md)
Hoja 6). Este paper hace exactamente eso, con un matiz que mejora la idea: para MC **no toma el
máximo, toma la distribución entera resumida en cinco percentiles**, y deja que la regresión
decida cuánto pesa la cola. El percentil 95 es lo más parecido al punto caliente, pero no va solo.

### 2.d Cómo convierten un mapa de probabilidad en un conteo de mitosis

Es el detalle de ingeniería más reusable del paper, y se entiende sin tener el modelo:

1. Umbral **0,915** (elegido en el conjunto de ajuste) sobre el mapa de probabilidad, para
   obtener un mapa de detecciones.
2. **Erosión morfológica con un elemento estructurante cuadrado de 16 µm × 16 µm.** Como las
   anotaciones son cajas de 16 µm (el tamaño de una célula), dos mitosis pegadas quedan como dos
   puntos desconectados en vez de una sola mancha.
3. Análisis de **componentes conexas**, y el centroide de cada una es una mitosis.
4. La **densidad mitótica** se calcula con ventana deslizante sobre toda la máscara de invasivo,
   en **baldosas de 1,8 × 1,8 mm con 50 % de solape**.
5. En la evaluación, una detección cuenta como acierto si hay una mitosis de referencia **a menos
   de 16 µm**.

**Las baldosas de 1,8 × 1,8 mm son el punto caliente de Nottingham con otro nombre**: 3,24 mm²,
del orden de los 10 campos de gran aumento que manda la regla clínica. Y nuestras cajas de
mitosis miden **16,7 µm** contra sus 16 µm, o sea prácticamente la misma convención: **nuestras
marcas servirían para evaluar un detector sin inventar tolerancias**.

## 3. Los datos, y la supervisión que exige

**Tres fuentes:** un hospital terciario (TTH, 657 casos / 1502 láminas), un laboratorio médico
(MLAB, 98 / 98) y **TCGA (829 casos / 878 láminas)**. **TTH y MLAB para desarrollo, TCGA solo
para evaluar.** Para evaluar el grado se usan 662 casos / 685 láminas, porque se excluyen las
láminas sin mayoría entre patólogos.

**TCGA es cohorte nuestra.** El test set de este paper es un conjunto que tenemos en el servidor.

**La supervisión de la etapa 1, en detalle**, porque es lo que decide si esto es pedible acá:

- **Tres regiones de 1 × 1 mm por lámina**, cada una anotada por **3 patólogos certificados**
  asignados al azar de un pool de **10**.
- **MC**: las mitosis se marcan con cajas de 16 µm, y la referencia de parche son las regiones
  del tamaño de una célula identificadas como figura mitótica por **al menos 2 de los 3**.
- **NP y TF**: el patólogo da un puntaje 1 a 3 **por región**, como si esa región representara al
  tumor entero, y la etiqueta final de la región es el **voto de mayoría**. Después **ese puntaje
  se propaga a todos los parches** que caen dentro de la región.
- A nivel de lámina, tres patólogos puntúan cada componente y se toma la mayoría. Además
  registran, aparte, los puntajes de los **informes de patología originales**.

**El matiz que salva media pregunta, y es el que hay que llevar a la reunión.** Para NP y TF **no
hay anotación por objeto**: la etiqueta de parche es el puntaje de una región de 1 mm² propagado.
Eso es mucho más barato que marcar núcleos, y es exactamente el tipo de pedido que se le puede
hacer a un patólogo. Para MC sí hay marcado exhaustivo dentro de la región.

**Y la diferencia de régimen que nos separa de ellos, dicha sin rodeos.** El paper declara que,
para la evaluación de MC, **todas las regiones del tamaño de una célula que no cumplen el
criterio se consideran negativas**. Pueden hacerlo porque dentro de sus regiones de 1 mm² la
anotación es exhaustiva. **Nosotros no podemos**: nuestras 61 marcas son positivos parciales y lo
no marcado no es negativo ([[anotaciones-patologo-qupath]]). Es la misma frontera que ya
identificamos al fichar PU learning, y este paper la vuelve a marcar desde el otro lado.

## 4. Los números por componente

**Tabla 2 del artículo.** Los intervalos son los del paper, al 95 %.

| Nivel | Componente | Métrica | Resultado [IC 95 %] |
|---|---|---|---|
| **Parche** | Recuento mitótico | F1 de detección | **0,60** [0,58 · 0,62] |
| **Parche** | Pleomorfismo nuclear | kappa cuadrático | **0,45** [0,41 · 0,50] |
| **Parche** | Formación tubular | kappa cuadrático | **0,70** [0,63 · 0,75] |
| **Lámina** | Recuento mitótico | kappa cuadrático | **0,81** [0,78 · 0,84] |
| **Lámina** | Pleomorfismo nuclear | kappa cuadrático | **0,48** [0,43 · 0,53] |
| **Lámina** | Formación tubular | kappa cuadrático | **0,75** [0,67 · 0,81] |

En detección de mitosis a nivel de parche, el F1 de 0,60 se descompone en **precisión 0,76 y
recall 0,50**: encuentra la mitad de las mitosis, y de lo que marca acierta tres de cada cuatro.

**Y el dato que exige nuestra política de eval** ([[eval-reporte-auc-y-umbrales-obj6]]): el
artículo titula con kappa, pero el Supplementary (Tabla 1) trae **balanced accuracy**, y cambia
la lectura.

| Componente (parche) | Accuracy | **Balanced accuracy** | kappa sin ponderar |
|---|---|---|---|
| Pleomorfismo nuclear | 0,67 | **0,50** | 0,40 |
| Formación tubular | 0,93 | **0,67** | 0,54 |

Con tres clases el trivial es 0,333. **Pleomorfismo a nivel de parche está en 0,50 de balanced
accuracy**: despega del trivial, pero poco, y su accuracy de 0,67 vive del desbalance. Es el
mismo patrón que nosotros documentamos en microcalcificaciones (Hallazgo 6), y conviene decirlo
nosotros antes de que lo pregunten.

## 5. Contra el desacuerdo entre patólogos, que es donde el paper gana

**Fig. 4 y Supplementary Tabla 2A**, kappa cuadrático:

| | MC | NP | TF |
|---|---|---|---|
| Acuerdo **entre patólogos** | 0,56 | 0,36 | 0,55 |
| Acuerdo **modelo con patólogo** | **0,64** | **0,39** | **0,69** |
| Modelo contra el voto de mayoría | 0,81 | 0,48 | 0,75 |

**El modelo concuerda con los patólogos mejor de lo que los patólogos concuerdan entre sí, en los
tres componentes.** Es el criterio 3 del rubric en su forma más fuerte: no necesita un baseline
de arquitectura porque **el baseline es el humano**.

Y trae su propia cota: en pleomorfismo el panel concuerda **0,36** consigo mismo. El techo de esa
tarea es bajo para todos y el modelo ya está pegado a él. Sobre eso no conviene prometer.

## 6. El valor pronóstico

Sobre los 829 casos de TCGA, con el intervalo libre de progresión como desenlace:

- **c-index 0,58 el modelo (suma continua) contra 0,58 los patólogos (suma discreta).** Delta
  0,004, cota inferior del IC unilateral 95 % en −0,036, contra un margen de no inferioridad
  prefijado de 0,075: **no inferior**.
- Con el **grado combinado**: 0,60 el modelo contra 0,58 los patólogos.
- Sumado a las variables clínicas de base (edad, TNM, estado de RE): base sola **0,74**, base más
  modelo **0,76** (p = 0,036, test de razón de verosimilitud).
- De los tres componentes, **solo el recuento mitótico** tiene valor pronóstico independiente
  (HR 1,30 con p = 0,015 univariable; pleomorfismo 0,97 con p = 0,879).
- El recuento mitótico del modelo **correlaciona con Ki-67 mejor que el del patólogo**: 0,47
  contra 0,37, con p = 0,002 en un test de permutación de 1000 muestras.

**Lo que esto le dice a nuestro proyecto, con cuidado.** Que de los tres componentes el que carga
el pronóstico sea **mitosis** es un argumento para no abandonar esa rama por difícil, y a la vez
explica por qué pleomorfismo, que es la que Sebastián quiere atacar, sale floja en todos lados:
si los patólogos concuerdan 0,36 entre sí y su HR es 0,97, puede ser que la señal clínica sea
genuinamente más débil, y no que el modelo no la encuentre.

### 6.a Un dato del Supplementary que nos toca directo, con su salvedad

La Supplementary Tabla 5 desglosa el c-index por componente y por origen del puntaje, y en la
fila de mitosis los puntajes **tomados del informe de patología original** dan **0,65**
[0,57 · 0,71], por encima del modelo continuo (0,59), del patólogo único (0,54) y del voto de
mayoría (0,58).

**Nos toca porque nuestras etiquetas salen exactamente de ahí**: del informe CAP, no de una
relectura hecha para el estudio. Si el dato se sostiene, la supervisión que tenemos no es una
versión pobre de la del paper, es otra cosa, y en pronóstico no está peor.

**La salvedad, y por eso no se usa como afirmación fuerte:** la nota de la tabla anterior dice que
los datos de informe original se computan **solo sobre el subconjunto con informe disponible
(n = 550)**, mientras que el encabezado de la Tabla 5 dice n = 829, y el paper **no plantea esa
fila como una comparación cabeza a cabeza**. O sea que las filas pueden no ser sobre los mismos
casos. Se lleva como observación, no como resultado.

## 7. El hallazgo de escala, que corrige nuestro encuadre del 11 de agosto

Del Methods, textual:

> «All WSIs used in this study were scanned at 0.25 μm/pixel (40×). The small number of TCGA
> images in the BRCA study scanned at **0.50 μm/pixel (20×) were excluded** in order to ensure
> availability of 40x for DLS-based MC and NP grading.»

**Un grupo con los recursos de Google prefirió tirar láminas antes que correr mitosis y
pleomorfismo a 20×.** Nuestra cohorte privada está **entera** a 0,4650 µm/px con
`objective-power = 20`, verificado sobre las 490 láminas con `.bif` limpio, sin una sola
excepción ([`../anotaciones_patologo/regiones_escaneo/resultados.md`](../anotaciones_patologo/regiones_escaneo/resultados.md) §3).

La consecuencia, como cuenta y no como opinión:

| Rama | Campo que pide | En nuestro privado (0,465 µm/px) | En TCGA (0,2325 µm/px) |
|---|---|---|---|
| Mitosis | 32 µm a 0,25 µm/px = 128 px | 69 px, hay que **ampliar 1,86×** (inventar detalle) | 138 px, se reduce a 128 sin problema |
| Pleomorfismo | 256 µm a 0,25 µm/px = 1024 px | 551 px, **ampliar 1,86×** | 1101 px, se reduce a 1024 |
| **Formación tubular** | 1 mm a 1,0 µm/px = 1024 px | 2202 px, **se reduce**: sin problema | 4404 px, se reduce |

**Formación tubular es el único de los tres que nuestro privado alimenta sin inventar
resolución.** Eso **corrige el encuadre que traíamos del 11-ago**, donde la rama «a favor» era
pleomorfismo porque Mercan trabaja a 0,5 µm/px, que es prácticamente nuestro privado. Los dos
papers son de mama, del mismo año y de la misma revista, y **eligen escalas distintas para la
misma tarea**: Mercan remuestrea a 0,5 y Jaroensri exige 0,25. No se contradicen sobre un hecho,
difieren en una decisión de diseño, pero para nosotros la diferencia es concreta: **con Mercan la
escala del privado alcanza y con Jaroensri no**.

Y hay una asimetría que conviene tener presente: TCGA nos alimenta las tres ramas sin ampliar
nada, porque está a 0,2325. La rama difícil es la cohorte propia, no la pública.

## 8. Un resultado negativo suyo que toca la rama de NPKC-MIL

Textual, sobre pleomorfismo:

> «For NP, additional experiments with a hand-engineered nuclear segmentation-based approach were
> also conducted. **This approach did not improve performance in our experiments**, potentially
> due to the wide variability in staining and cellular appearance in high-grade cases.»

**NPKC-MIL propone justamente eso**: 16 features de núcleo hechas a mano, nueve geométricas y
siete de textura, calculadas sobre núcleos segmentados con HoVer-Net
([`../papers_11_agosto/hojas_papers_nuevos.md`](../papers_11_agosto/hojas_papers_nuevos.md)
Hoja 5). Acá hay un grupo con más datos que probó esa familia para la misma tarea y reporta que
no mejoró, con una explicación mecanística: la variabilidad de tinción y de aspecto celular en
los casos de grado alto.

**No cierra esa rama**, porque no es el mismo método ni el mismo pipeline, y porque un resultado
negativo mencionado en una frase del Methods no es una ablación publicada. Pero es evidencia en
contra, es ajena, y es exactamente el tipo de dato que conviene tener antes de gastar el costo de
HoVer-Net que Sebastián ya había pausado.

## 9. La cuenta de integración, con nuestros números

Nuestro parche es 256 px a 0,465 µm/px, o sea **119 µm** de lado. Con los 20 parches de mayor
atención que propuso Sebastián:

| Rama | Campo del especialista | Cuántas inferencias por lámina | Cuánto ahorra el top-k |
|---|---|---|---|
| **Mitosis** | 32 µm, entra **3,7 × 3,7 ≈ 14 veces** en nuestro parche | 20 × 14 = **280** de un ResNet50 sobre 128 px | **muchísimo** |
| **Pleomorfismo** | 256 µm, **más grande** que nuestro parche (119 µm) | **20**, centrando una ventana de 551 px en cada parche y ampliándola a 1024 | algo, con solapamiento entre parches vecinos |
| **Formación tubular** | 1 mm, **ocho veces** nuestro parche | una sola ventana ya cubre unos **70** parches nuestros | **casi nada** |

**Esa última fila es un hallazgo de diseño, no un detalle de implementación.** La ganancia del
pipeline de dos etapas depende de la **razón entre el campo del especialista y el parche del
selector**: cuando el especialista mira más grande que el selector, el recorte por atención deja
de ahorrar. Y se cruza con el §7 de forma incómoda: **la rama donde la escala nos favorece
(tubular) es justo aquella donde el top-k no aporta**, y la rama donde el top-k rinde muchísimo
(mitosis) es la que exige ampliar 1,86×.

## 10. Qué nos sirve, y qué no

**Sirve.**

- **Es la forma del pipeline de Sebastián, publicada y medida.** Deja de ser una idea de reunión y
  pasa a ser un diseño citable, con la etapa 2 barata y explícita (§2.c).
- **Ataca las tres etiquetas CAP que ya tenemos**, y ningún otro candidato lo hace:
  `grado_histologico_mitotic_rate`, `grado_histologico_pleomorfismo_nuclear`,
  `grado_histologico_diferenciacion_tubular`, más el `grado_histologico_grado_general` que sale de
  sumarlas.
- **El baseline contra el que gana es el patólogo**, no una arquitectura (§5).
- **TCGA es su test set y es cohorte nuestra**, así que sus números están medidos sobre datos que
  podemos mirar.
- La cadena de mitosis del §2.d (umbral, erosión de 16 µm, componentes conexas, densidad en
  baldosas de 1,8 mm) es reusable tal cual, y **nuestras marcas de 16,7 µm evalúan sin inventar
  tolerancias**.
- Para NP y TF, **la supervisión de etapa 1 es puntaje por región, no anotación por objeto**: es
  un pedido realista al patólogo (§3).

**No sirve, o hay que aclararlo.**

- **No publica pesos.** Textual del Code Availability: *«The final, trained models have not yet
  undergone regulatory review and cannot be made available at this time.»* Lo público es el
  framework (TensorFlow 1.14), la ResNet50x1 de BiT, y el código de la **etapa 2**
  (`github.com/Google-Health/google-health/tree/master/breast_survival_prediction`). **La etapa 1,
  que es la que nos interesa, hay que entrenarla.**
- **La escala del privado no alcanza para dos de las tres ramas** (§7).
- **Pleomorfismo es su componente flojo** en todas las métricas y en los dos niveles (kappa 0,45
  parche, 0,48 lámina, balanced accuracy 0,50), y es la tarea que Sebastián quiere atacar.
- **Su régimen de supervisión de MC trata lo no marcado como negativo** (§3), que es justamente lo
  que nosotros no podemos hacer.
- Seguimiento corto en TCGA (mediana cercana a 2 años), sin control por tratamiento, y la mayoría
  de los casos aporta una sola lámina. Lo listan ellos como limitación.

## 11. Lo que este estudio no afirma

- **Que Jaroensri suba ninguna de nuestras métricas.** No se probó en nuestros datos, y el
  historial del proyecto son cuatro ejes cerrados sin mejora (Hallazgos 11 a 14).
- **Que la atención de CLAM sea un reemplazo válido de su máscara de invasivo.** Son objetos
  distintos (§2.a) y la sustitución está sin medir. Lo único medido es que la atención rankea bien
  los parches con mitosis **en una lámina**, con un anotador.
- **Que ampliar 1,86× el privado recupere el rendimiento.** Interpolar hacia arriba no inventa
  detalle, y el paper no evalúa ese caso: directamente **excluye** las láminas a 20×.
- **Que el resultado negativo del §8 cierre la rama de NPKC-MIL.** Es evidencia en contra de una
  familia de features, mencionada en una frase, no una ablación publicada.
- **Que la fila «informe original» del §6.a sea una comparación cabeza a cabeza.** Puede estar
  computada sobre otro n, y el paper no la plantea así.
- **Nada de esto está implementado ni pre-registrado.** Regla 9: si alguna rama avanza, va con
  hipótesis pre-registrada, métrica y dirección esperada, y `reviewer` antes de tocar código.

## 12. Preguntas para llevar

1. **¿Con cuál de las tres ramas se arranca?** La cuenta del §9 y la escala del §7 no coinciden:
   tubular es la única que nuestro privado alimenta sin ampliar, pero es también donde el top-k de
   CLAM no ahorra nada. Mitosis es al revés. Es una decisión, y conviene tomarla con los dos
   números a la vista.
2. **¿La primera etapa es la atención de CLAM o una máscara de invasivo propia?** Ya tenemos
   tareas de invasión entrenadas, así que la opción de imitarlos existe. La atención sale gratis y
   está medida en una lámina; la máscara es más fiel al paper y cuesta más.
3. **¿Se le puede pedir al patólogo un puntaje 1 a 3 sobre regiones de 1 mm², y sobre cuántas
   láminas?** Es la supervisión que la etapa 1 de NP y TF necesita, y es mucho más barata que
   marcar objetos. La respuesta a esto decide si la rama existe.
4. **¿Y si en vez de entrenar la etapa 1 se evalúa primero sobre TCGA?** Ahí la escala calza sola,
   es su propio test set, y es el mismo patrón «Etapa 0 antes de Etapa 1» que ya ahorró entre 18 y
   24 horas de GPU en PathPT (Hallazgo 13).
