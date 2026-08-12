# Cuatro papers para la rama de mitosis: una hoja cada uno

> **ADDENDUM 11-ago-2026 (noche) — el cuarteto de la reunión del 12-ago NO es el de este
> documento.** Ernesto lo corrigió en sesión: los cuatro papers que se abordan el miércoles
> 12-ago son **PU learning** (hoja 1) y **ZoomMIL** (hoja 3) de acá, más los **dos que trajo
> Sebastián el 6-ago** y que viven en [`../papers_11_agosto/`](../papers_11_agosto/): NPKC-MIL
> (Wang y Yuan, iScience 2024) y el de pleomorfismo nuclear (Mercan et al., npj Breast Cancer
> 2022). **CellViT (hoja 2) y MS-CLAM (hoja 4) quedan fuera de esa reunión**; sus hojas siguen
> siendo fichas válidas y no se tocan. Las dos hojas nuevas, con el encuadre del cuarteto real
> y por qué queda simétrico (dos papers por tarea, mitosis y grado nuclear), están en
> [`../papers_11_agosto/hojas_papers_nuevos.md`](../papers_11_agosto/hojas_papers_nuevos.md).
>
> Material para la reunión con Sebastián del **jueves 6-ago-2026** (el viernes 7 es la de
> Benjamín). La reunión prevista para el lunes 3-ago no ocurrió, y la del viernes 7 que este
> encabezado anotaba hasta el 6-ago se adelantó un día.
>
> **Qué es esto.** El resumen ejecutable de los cuatro papers, una hoja por paper, para leer en la
> reunión sin abrir nada más. **Todo lo de acá está verificado contra los PDF**, que están bajados
> en esta carpeta desde el 2-ago con autorización explícita de Ernesto.
>
> **Qué NO es.** No es un pre-registro y no propone implementar nada. Regla 9: si alguna de estas
> ramas avanza, va con hipótesis pre-registrada, métrica y dirección esperada, y `reviewer` antes
> de tocar código.
>
> **De dónde sale.** El documento largo es [`papers_mitosis.md`](papers_mitosis.md) (36 KB) y el
> detalle por paper vive en [`pulearning_estudio.md`](pulearning_estudio.md),
> [`cellvit_estudio.md`](cellvit_estudio.md), [`zoommil_estudio.md`](zoommil_estudio.md),
> [`msclam_estudio.md`](msclam_estudio.md) y [`midog_notas.md`](midog_notas.md). El mapa de las
> cuatro familias de respuesta está en [`README.md`](README.md) §3.

---

## Hoja 0. La recomendación, y las tres cosas que hay que decir sí o sí

**Recomendación: la familia D primero, y en dos pasos.**

Los cuatro se ordenan por un solo criterio, que es el que descarta candidatos rápido: **qué
supervisión exige cada uno**, contra la que efectivamente tenemos. Lo que tenemos son **positivos
parciales**: una lámina anotada (129741), 26 marcas de mitosis, un anotador, y lo no marcado **no
es negativo**.

| | **D. PU learning** | **C. CellViT** | **B. ZoomMIL** | **MS-CLAM** |
|---|---|---|---|---|
| **Supervisión que exige** | Positivos parciales, **los nuestros** | Ninguna nuestra (pesos públicos) | Solo etiqueta de lámina | Etiqueta de parche **exhaustiva** |
| **¿Compatible con nuestras marcas?** | **Sí, por construcción** | Sí, no las usa | Sí, no las usa | **No**, asume que no son parciales |
| **Qué habilita** | Contar mitosis, y de ahí el conteo en el punto caliente | Razón núcleo/vecindario, que es grado nuclear | Contexto multi-escala y armonización de µm/px | Localización, si hubiera anotación densa |
| **Costo de montarlo** | **Alto** (detector nuevo) | **Bajo si se acota** (sin entrenar) | **Medio** (pirámide + GPU) | Bajo de codebase, imposible de datos |
| **Lo que lo frena** | 26 marcas no entrenan nada | **Sin clase mitótica** | En el privado no hay 40× al que hacer zoom | Su loss castiga lo no marcado |
| **Prioridad** | **1** | 2 (para grado nuclear) | 3 | 5 |

**Por qué D y no las otras.** Es el único cuyo régimen de supervisión coincide con el nuestro. Hoy
las 26 marcas solo sirven de validación; este paper es lo que las vuelve entrenables sin mentir
sobre los negativos. Y ataca el argumento que **sobrevivió** a la medición del 1-ago: el recuento
de Nottingham es un **conteo en el punto caliente** (unos 141 parches contiguos, el 2.9 % de la
lámina), no un promedio ponderado. Producir un conteo es producir la cantidad que define el
puntaje.

**Los dos pasos, y el primero es barato.**

1. **Go/no-go antes de gastar GPU.** Correr un detector de mitosis entrenado en datos públicos
   sobre unas pocas láminas nuestras y medir contra las 26 marcas. Si no encuentra lo que el
   patólogo marcó, la familia D se cierra ahí. Es el mismo patrón «Etapa 0 antes de Etapa 1» que
   ya ahorró de 18 a 24 h en PathPT (Hallazgo 13).
2. **Solo si el paso 1 pasa**: fine-tuning con PU learning a medida que lleguen más láminas
   anotadas, y de ahí el conteo en el punto caliente como entrada de un clasificador chico de
   `score_1/2/3`.

**Las tres cosas que hay que decir sí o sí.**

1. **El paso 1 no depende del paper de Zhao.** Necesita pesos públicos de un detector de mitosis,
   y quien los tiene es el ecosistema de MIDOG (anexo). Que la prueba barata esté **desacoplada**
   de la decisión cara es la mejor propiedad del plan.
2. **El régimen de anotación que el paper evalúa no es el nuestro, y es la salvedad más
   importante.** Ellos borran marcas hasta dejar una por parche de 500×500, o sea **retienen el
   ~73 %**. Nosotros tenemos **26 marcas en 4799 parches**. El paper no evalúa ese régimen y no hay
   forma de extrapolar la curva.
3. **La pregunta que decide si la familia D existe: ¿hay más láminas anotadas, y quién es «GDT»?**
   Con 26 marcas en 1 lámina no se entrena; con varias decenas de láminas, sí, y el método admite
   que sean parciales. Eso convierte «necesitamos más anotaciones» en un pedido con forma: marcas
   por punto sobre figuras mitóticas, en N láminas, **y está bien que sean parciales**.

**El paso 1 tiene un orden de cohortes que importa, y hay que decirlo antes de diseñar.** Los
datasets de mitosis se anotan a 40×, que es donde se cuenta clínicamente. TCGA está a 0.2325 µm/px
y calza sin reescalar; el privado está a 0.465, o sea al doble de grueso. Entonces el go/no-go
corre **primero sobre TCGA**, y el privado es un brazo aparte con su propio riesgo. La lámina
anotada es privada, así que la validación contra las marcas cae justo en el brazo difícil.

---

## Hoja 1. PU learning para detección celular (familia D). **Prioridad 1**

> Zhao Z, Pang F, Liu Y, Liu Z, Ye C. *Positive-unlabeled learning for binary and multi-class cell
> detection in histopathology images with incomplete annotations*. **MELBA vol. 1, dic-2022.**
> DOI `10.59275/j.melba.2022-8g31` · arXiv:2302.08050. Previo: MICCAI 2021.
> **Acceso abierto.** Código: `github.com/zipeizhao/PU-learning-for-cell-detection`.

**Qué propone.** Que cuando el patólogo anota **algunas** células y no todas, el término de la loss
que castiga falsos positivos está **mal especificado**, porque le enseña al detector que las
células no marcadas son negativas. Y que ese término se puede reescribir usando solo positivos y
no-etiquetados, sin inventar negativos. No es un modelo nuevo: es un cambio en una de las dos
mitades de la loss de clasificación, y los autores lo declaran agnóstico a la arquitectura.

**Por qué nos toca.** El primer párrafo del abstract describe nuestra situación palabra por
palabra. El paper lo dice sin rodeos (pág. 4): *«the regions with no instances labeled as positive
are not necessarily all truly negative»*.

**Los números** (MITOS-ATYPIA-14, mitosis en mama, 5-fold, anotación incompleta simulada):

| Método | Recall | Precisión | F1 |
|---|---|---|---|
| Baseline (trata lo no marcado como negativo) | 0.570 ± 0.075 | 0.403 ± 0.040 | 0.470 ± 0.045 |
| BDE (el competidor especializado) | 0.598 ± 0.077 | 0.427 ± 0.039 | 0.496 ± 0.044 |
| **Propuesto** | **0.608 ± 0.079** | **0.439 ± 0.038** | **0.507 ± 0.044** |
| *Upper bound* (anotación completa) | 0.613 ± 0.074 | 0.461 ± 0.049 | 0.523 ± 0.048 |

**Cómo leer esa tabla, porque el titular engaña.** El +0.011 es contra BDE. Contra el **baseline**,
que es lo que haríamos nosotros entrenando de la forma normal, la diferencia es **+0.037**. Con el
*upper bound* a la vista: el hueco que abre la anotación incompleta es 0.053, y el método recupera
**el 70 % de él**. En recall recupera casi todo (0.608 contra un techo de 0.613). Consistente en
los 5 folds, con t-test pareado y corrección Benjamini-Hochberg.

**A favor.**

- Único de los cuatro cuyo **régimen de supervisión es el nuestro**. No lo esquiva, lo usa.
- Bajo anotación parcial **seleccionan el hiperparámetro por recall y no por precisión**, porque un
  «falso positivo» puede ser una célula real sin marcar. Es el mismo razonamiento que ya
  escribimos por nuestra cuenta el 1-ago, y el paper le da forma de procedimiento. **Es adoptable
  aunque nunca implementemos el detector.**
- Probaron una simulación más realista (quedarse con la célula de mayor acuerdo entre patólogos,
  que imita a un anotador que marca lo fácil) y la ventaja se mantiene: F1 0.512 contra 0.473.
  Es el escenario que más se parece al nuestro.

**Lo que lo frena.**

- **El régimen que testean retiene el ~73 % de las marcas. El nuestro es 26 en 4799.** No se puede
  tapar con que «el planteo es correcto».
- **El código existe pero no corre acá.** La loss son cinco líneas reconocibles término a término
  (`faster_rcnn.py:121`), pero `π` está **hardcodeado en 0.04**, es **solo el caso binario**, y el
  entorno pide **PyTorch 0.4.0 y CUDA 8.0**: no hay kernels para una RTX A6000 (sm_86, CUDA 12.8).
  Es referencia de la loss, no software que se clone y se corra.
- **No entrega el conteo en el punto caliente.** Eso lo ponemos nosotros y no está en ninguno de
  los cuatro papers.

**Qué costaría acá.** Andamiaje de detección nuevo en `clam_testing2/`, fuera del pipeline MIL:
Faster R-CNN de torchvision, anclas a 0.7 / 0.3, dataset a partir del geojson del patólogo (que
además hay que corregir por el `dx=3829`). Lo reusable es chico y está claro; lo que hay que
escribir de cero es el andamiaje, no el método.

**Si preguntan por el prior.** En mitosis vive entre **0.02 y 0.05** (2 % a 5 % de las cajas
candidatas). Para multi-clase no hacen grid: fijan el de la clase mayoritaria y derivan los otros
en tiempo de entrenamiento, que es también el punto más frágil del método.

**No se afirma.** Que transfiera a nuestro régimen, que suba `grado_mitotic_3clases` (el paper mide
F1 de **detección**, no puntaje de lámina), ni que 0.04 sea nuestro prior.

---

## Hoja 2. CellViT (familia C). **Prioridad 2, y para grado nuclear, no para mitosis**

> Hörst F et al. *CellViT: Vision Transformers for precise cell segmentation and classification*.
> **Medical Image Analysis 94:103143 (2024).** DOI `10.1016/j.media.2024.103143` ·
> arXiv:2306.15350. **Preprint abierto** (la versión de revista es de suscripción).
> Código: `github.com/TIO-IKIM/CellViT`, con pesos públicos.

**Qué propone.** El mismo esquema de HoVer-Net (máscara de núcleo, mapas de distancia horizontal y
vertical, tipo de núcleo) con el encoder CNN reemplazado por un **Vision Transformer
pre-entrenado**, y parches de inferencia de 1024×1024 en vez de 256.

**Los números en PanNuke** (detección agnóstica de clase, 3-fold oficial):

| Modelo | Precisión | Recall | F1 detección |
|---|---|---|---|
| HoVer-Net | 0.82 | 0.79 | 0.80 |
| CellViT256 | 0.83 | 0.82 | 0.82 |
| **CellViT-SAM-H** | 0.84 | 0.81 | **0.83** |
| CellViT-Random (sin pre-entrenar) | 0.79 | 0.81 | 0.80 |

La fila `CellViT-Random` es la que ordena la lectura: buena parte de la ganancia viene del
**pre-entrenamiento** del encoder, no de la arquitectura.

**El dato que más nos toca: qué pasa a la escala de nuestra cohorte privada.** El paper publica
modelos sobre PanNuke reescalado a 0.50 µm/px, que es prácticamente nuestro privado (0.465):

| Modelo | Recall @ 0.25 µm/px | Recall @ 0.50 µm/px | F1 @ 0.50 |
|---|---|---|---|
| CellViT256 | 0.82 | **0.60** | 0.71 |
| CellViT-SAM-H | 0.81 | **0.63** | 0.73 |

El recall se desploma de 19 a 22 puntos. **A la escala del privado, CellViT queda por debajo de
HoVer-Net a 0.25 µm/px (0.80).** En TCGA el problema no existe. Es, además, una confirmación ajena
de nuestra regla de proyecto: la escala física manda.

**Lo que lo frena, y va en la misma frase que el entusiasmo.**

- **No tiene clase mitótica**, verificado de la forma más fuerte posible: la palabra «mitosis» **no
  aparece ni una vez en las 23 páginas**. No es que la clase esté y rinda mal; el problema no está
  planteado. **Para contar mitosis no sirve.**
- **Sigue usando watershed** (gradiente de los mapas de distancia, Sobel, watershed por
  marcadores). O sea que **no elimina los 75 min de CPU** que identificamos como el grueso del
  costo de HoVer-Net.
- **El 1.85× es de la variante chica.** SAM-H, la de mejores números, rinde **1.39×**. Y el speedup
  viene sobre todo del **parche de 1024 px**, no de la arquitectura: el mismo modelo acelera 2.49×
  al pasar de 256 a 1024. El mismo truco podría aplicarse a HoVer-Net.

**La cuenta que reordena la familia, y conviene tenerla a mano.** Sebastián pausó C por costo
(3.3 h por lámina) y su propia idea fue correrla solo sobre los **20 mejores parches que CLAM
selecciona**. Puestas al lado: cambiar de modelo rinde **1.85×**; acotar de 4799 parches a 20 rinde
**~240×**. La elección de modelo es de segundo orden. **Si C se reabre, se reabre por el
subconjunto de parches, no por el paper.**

**Dónde sí sirve.** En **grado nuclear**, que es donde mejor calza con lo que describió el
patólogo: una vez segmentado el núcleo, «más grande que su vecindario» es una razón entre áreas,
directa de calcular e **invariante a la escala**, que es justo nuestro confundido de magnificación.

**Dato de hardware.** El paper dice que una **RTX A6000 de 48 GB alcanza** para entrenar ViT256 y
SAM-B. Es nuestra GPU. No hace falta entrenar (los pesos están), pero cierra la pregunta.

**Nota al margen, para completar una frase que dejamos abierta.** El que sí elimina el
post-procesamiento es **LSP-DETR** (Pekár et al., arXiv:2601.03163, ene-2026): polígonos
estrella-convexos, la separación de núcleos emerge sola, **más de 5× sobre el siguiente más
rápido**. Es preprint, no verificamos si tiene pesos públicos, y **no lo propongo como candidato**.

**No se afirma.** Que mejore nuestra métrica en ninguna tarea, que 5 clases alcancen para grado
nuclear (nadie lo midió), ni que reescalar el privado a 0.25 recupere el rendimiento (interpolar
hacia arriba no inventa detalle, y el paper no evalúa ese caso).

---

## Hoja 3. ZoomMIL (familia B). **Prioridad 3 para mitosis, y candidato real para otra cosa**

> Thandiackal K et al. *Differentiable Zooming for Multiple Instance Learning on Whole-Slide
> Images*. **ECCV 2022.** arXiv:2204.12454. **Acceso abierto.**
> Código: `github.com/histocartography/zoommil`.

**Qué propone.** Mirar toda la lámina en aumento bajo, **aprender** cuáles parches merecen que se
los mire de cerca, y volver a mirar solo esos en el aumento siguiente. Todo derivable de punta a
punta, así que la decisión de dónde hacer zoom se entrena **solo con la etiqueta de lámina**, que
es la que ya tenemos. El bloque base es atención con compuerta, la misma familia que CLAM.

**Los números** (media de 3 corridas):

| Dataset | Método | Weighted-F1 | Accuracy | TFLOPs |
|---|---|---|---|---|
| **BRIGHT** (mama) | CLAM-SB (10×) | 63.1 ± 1.7 | 64.3 ± 1.7 | 16.45 |
| **BRIGHT** (mama) | **ZoomMIL** (1.25×→2.5×→10×) | **68.3 ± 1.1** | **69.3 ± 1.0** | **1.29** |
| CAMELYON16 | CLAM-SB (20×) | 83.3 ± 1.5 | 84.0 ± 1.3 | 39.12 |
| CAMELYON16 | ZoomMIL (10×→20×) | 83.3 ± 0.3 | 84.2 ± 0.4 | 14.94 |

**Corrección respecto de lo que circulaba, y es la razón por la que valía bajar el PDF.** Los
68.3 / 69.3 con la cadena 1.25×→2.5×→10× son de **BRIGHT, no de CAMELYON16**. En CAMELYON16 usa
10×→20× y queda **a la par**, no mejor. En BRIGHT, que es mama, le saca **5.2 puntos de
weighted-F1 a CLAM-SB con 12.8× menos FLOPs**.

**El párrafo del paper que más nos importa, y no es una tabla.** En CAMELYON16 los autores
explican (pág. 9): *«As the metastatic regions can be extremely small, we set the lowest
magnification to 10× in ours. Nevertheless, this still has an adverse impact on the performance.»*
O sea: **cuando el objeto a encontrar es chico, el mecanismo de zoom se degrada**, y tuvieron que
renunciar a empezar en aumento bajo. Una micro-metástasis mide cientos de micras; **una figura
mitótica marcada mide 16.7 µm**. Esto refuerza que B quede tercera para mitosis, y ahora es un
número del paper y no una inferencia nuestra.

**El bloqueo, y es de la cohorte, no del método.** Nuestro privado está escaneado a **20×**
(`objective-power = 20`, 0.465 µm/px, medido en la 129741) y la mitosis se cuenta a **40×**. Un
método que aprende a hacer zoom **no puede hacer zoom a una magnificación que el archivo no
contiene**.

**Un gotcha del código, verificado, que nos mordería exactamente a nosotros.** El preprocesamiento
lee el aumento nativo **solo de la propiedad de Aperio** y, si no está, **asume 40× con un
warning** (`preprocessing.py:442-469`). Nuestra cohorte privada es **Ventana `.bif`**, que no
expone `aperio.AppMag`: caería en el `else` y se la trataría como 40× estando a 20×. Es el error
silencioso de factor 2 contra el que advierte nuestra regla de proyecto. El **modelo** sí tolera
una pirámide parametrizada en µm/px (el factor de expansión se dimensiona con la razón medida entre
niveles, no está hardcodeado); el **preprocesamiento no**, y habría que reescribirlo.

**Dónde sí aporta, y vale separarlo de mitosis.** En el **confundido de magnificación entre
cohortes**: si la pirámide se parametriza en µm/px físicos y no en `level`, un modelo multi-escala
es la vía natural para que TCGA a 0.2325 y el privado a 0.465 dejen de ser dos escalas distintas
sin avisar. Esa infraestructura ya está escrita y sin lanzar del eje del B6
(`scripts/extract_multiscale_features.py`), y este paper es el argumento para gastarla acá en vez
de como mejora genérica. Y el +5.2 en BRIGHT es un argumento honesto para probarlo en tareas de
mama que **no** dependen de objetos chicos (invasión, CDIS).

**No se afirma.** Que suba nuestra métrica, que el +5.2 de BRIGHT se traslade (BRIGHT es subtipo en
3 clases, un centro, un escáner), ni que la pirámide en µm/px resuelva el confundido: es la vía
natural para atacarlo, no una demostración.

---

## Hoja 4. MS-CLAM (fuera de las tres familias). **Prioridad 5, y se lleva igual**

> Tourniaire P, Ilie M, Hofman P, Ayache N, Delingette H. *MS-CLAM: Mixed supervision for the
> classification and localization of tumors in Whole Slide Images*. **Medical Image Analysis
> 85:102763 (2023).** DOI `10.1016/j.media.2023.102763`.
> **Abierto por HAL** (`inria.hal.science/hal-03972289`). Código: fork del CLAM de Mahmood Lab.

**Por qué está en la lista.** El encargo dice «aprovechando la información del patólogo sobre las
etiquetas», y este es el que responde a esa frase de la forma más literal: es CLAM con
**supervisión mixta**, la mayoría de las láminas con solo su etiqueta y unas pocas con la etiqueta
de **cada parche**, que supervisa directamente los puntajes de atención. Es también el más cercano
a nuestra infraestructura: si se implementara, no habría codebase nuevo que aprender.

**Qué reportan.** Con entre el **12 y el 62 %** de las láminas con anotación de parche llegan a
rendimiento cercano al totalmente supervisado, en clasificación y en localización. Con el 12 %, que
en Camelyon16 son **11 láminas tumorales completamente anotadas**, ya ven la mejora sobre CLAM.

**La escasez no es lo que lo mata.** Tienen una sección entera (§2.5, *MS-CLAM without tile-level
labels*) para el caso sin anotación: las láminas sin etiquetas de parche usan las pseudo-etiquetas
de atención de CLAM de siempre, y el método **degrada con gracia** hasta volver a ser CLAM.

**Lo que sí lo mata para nosotros es la parcialidad.** El primer término de su loss de atención
(ec. 3) minimiza la suma de atención de los parches marcados como no tumorales, o sea **empuja
activamente hacia cero la atención de todo lo que no fue marcado**. Con positivos parciales ese es
exactamente el gradiente equivocado: castigaría al modelo por mirar una mitosis que el patólogo no
marcó. Es la **hipótesis opuesta** a la del paper de PU learning, y por eso los dos no se pueden
mezclar sin reescribir esa ecuación.

**Una ironía útil.** Su propio dataset tiene el problema: aclaran que en Camelyon16 todas las
láminas metastásicas están anotadas exhaustivamente *«except for 20 slides which were only
partially annotated»*. La anotación parcial aparece en sus datos como una excepción molesta, no
como un régimen que el método modele.

**Y llegamos con el síntoma que arregla ya bastante ausente.** El aporte más visible de MS-CLAM es
en localización, porque **la atención de CLAM se derrama** (Dice 0.520 en Camelyon16, cubriendo a
veces casi todo el tejido). En nuestra medición del 1-ago la atención **no** se derramó: cayó sobre
las marcas (AUC de ranking 0.890 para mitosis, y grasa en 0.154).

**Para qué llevarlo igual.** Es la **respuesta preparada** si en la reunión sale «¿y por qué no le
agregamos supervisión de parche a CLAM y listo?». Se puede, está publicado, funciona, y necesita un
orden de magnitud más de anotación del que tenemos, con una suposición que nuestras marcas no
cumplen. **Y vuelve a la mesa** si el patólogo alguna vez anota **regiones** en vez de puntos: vale
la pena preguntarlo junto con el pedido de marcas de mitosis.

**No se afirma.** Que no sirva nunca, ni que su ec. 3 no se pueda modificar para tolerar positivos
parciales. Se podría, y sería traer la idea de PU learning acá. Eso es una propuesta, no un
hallazgo, y va con regla 9.

---

## Anexo (media hoja). MIDOG: no es candidato, es el insumo que hace ejecutable el paso 1

> Aubreville M et al. *Mitosis domain generalization in histopathology images: The MIDOG
> challenge*. **Medical Image Analysis 84:102699 (2023).** arXiv:2204.03742. Licencia del dataset:
> **CC-BY**.

**Qué es.** 200 casos de **cáncer de mama humano** de entrenamiento y 100 de test, en 4 escáneres,
dos de ellos no vistos en el test. Anotaciones en formato MS COCO. Es la fuente de datos del paso 1.

**Tres cosas lo vuelven el candidato natural.**

1. **La escala calza con TCGA.** Sus seis escáneres van de **0.23 a 0.26 µm/px**. TCGA (0.2325) cae
   dentro del rango y corre **sin reescalar**; el privado (0.465) está al doble y necesita
   reescalado, que es el brazo con riesgo.
2. **Su unidad de dato es exactamente el campo de recuento clínico.** No son WSI: son **regiones de
   2.0 mm²** elegidas por un patólogo, que es la definición de los 10 campos de gran aumento de
   Nottingham. O sea, MIDOG resuelve el «cuántas mitosis hay acá dentro» y nos deja el «dónde está
   el acá dentro». Y la densidad de anotación es comparable: la mayoría de sus ROI tienen **20 o
   menos** figuras mitóticas; nuestra 129741 tiene **26**. La diferencia no es la densidad, son los
   200 casos contra nuestra lámina.
3. **La evaluación contra el geojson es viable sin inventar tolerancias.** Su criterio de acierto
   es centroide a menos de **7.5 µm**, que cae holgadamente dentro de nuestras marcas de 16.7 µm.

**Los números de referencia.** Ganador F1 **0.748**, ensamble de los 5 mejores 0.773. El ganador
**supera a seis expertos humanos** en la misma tarea.

**Lo que advierte, y es incómodo para el paso 1.** La razón de existir del challenge es que **los
detectores de mitosis se degradan al cambiar de escáner**, y el test incluye a propósito escáneres
no vistos. Nuestra cohorte privada es **Ventana `.bif`**, que no está entre los seis. El riesgo de
transferencia no es una preocupación teórica nuestra: es el resultado central del challenge. Por
eso el paso 1 es un go/no-go y no un supuesto.

**Dos detalles que refuerzan cosas nuestras.** Su escáner E declara «0.24 µm/px @ 20×»: el rótulo
de aumento y la escala física **no se corresponden** entre fabricantes, que es exactamente por qué
parametrizamos en µm/px. Y reconocen que **los expertos pasan por alto los objetos menos
reconocibles**, razón por la cual anotan por consenso: el supuesto de «lo no marcado es negativo»
es frágil incluso en datasets construidos con cuidado, que es un argumento extra a favor de D.

**Estado.** El tooling público del challenge (`MIDOG_reference_docker` con el algoritmo de
referencia y `MIDOG_evaluation_docker` con el evaluador oficial) **no se bajó**: está fuera de la
lista que Ernesto autorizó el 2-ago. Si el paso 1 se aprueba, es el primer lugar donde mirar,
porque evita implementar un detector y un evaluador de cero. **Bajarlo requiere autorización
nueva.**

---

## Lo que este documento no afirma

- **Que alguno de los cuatro suba la métrica.** Ninguno está probado en nuestros datos, y el
  historial del proyecto son cuatro ejes cerrados sin mejora (Hallazgos 11 a 14). Lo que se afirma
  es cuál es compatible con la supervisión que tenemos y cuánto costaría probarlo.
- **Que la familia D vaya a transferir a nuestra cohorte.** MIDOG existe justamente porque los
  detectores de mitosis se caen al cambiar de escáner.
- **Que estos sean los únicos candidatos.** Quedaron sin fichar las ediciones 2023 a 2025 de MIDOG,
  la línea de figuras mitóticas atípicas en mama (AMi-Br), y los multi-escala alternativos a
  ZoomMIL (HIPT, ensambles multi-magnificación). De los ocho PDF bajados, **LSP-DETR es el único
  sin estudiar**.
- **Nada de esto está implementado ni pre-registrado.** Regla 9.
