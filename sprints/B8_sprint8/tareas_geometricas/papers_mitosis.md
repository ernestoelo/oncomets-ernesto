# Tres papers para la rama de mitosis

> Encargo de Ernesto del 2-ago-2026, para la reunión con Sebastián del **lunes 3-ago**.
> Registro del encargo: [`../objetivos_sprint8.md`](../objetivos_sprint8.md) §4, ADDENDUM
> 2-ago (noche). Mapa contra el que se ubican:
> [`README.md`](README.md) §3, las cuatro familias de respuesta.
>
> **Restricciones que la búsqueda no re-deriva** (ya decididas):
> 1. Apuntar a las familias **B** (campo de visión), **C** (unidad de representación) y **D**
>    (detector dedicado). La **A** (cambiar el operador de agregación) está descartada por la
>    medición del 1-ago: la atención **sí** cae sobre las mitosis (AUC de ranking 0.890 ± 0.039
>    en los checkpoints que nunca vieron la lámina) y el modelo igual responde mal
>    ([`../atencion_vs_patologo/resultados.md`](../atencion_vs_patologo/resultados.md)).
> 2. La supervisión disponible son **positivos parciales**: una lámina, un anotador, y lo no
>    marcado **no es negativo** ([[anotaciones-patologo-qupath]]).
> 3. ~~**No se descarga nada** (workaround E).~~ **Superado el 2-ago-2026 (noche):** Ernesto autorizó
>    explícitamente bajar estos papers y sus repos. Ver el ADDENDUM de abajo.
>
> **Nota de acceso, y es buena noticia: los cinco papers de este documento se leen sin
> paywall**, tres por su versión de autor (arXiv o HAL) y uno por ser de una revista
> enteramente abierta. No hace falta acceso institucional para ninguno, a diferencia de los
> dos pendientes del encargo anterior (LVI e ILSC).
>
> ---
>
> ## ADDENDUM 2-ago-2026 (noche): bajados, leídos, y qué cambió
>
> Los ocho PDF están en esta carpeta y los cuatro repos en `clam_testing2/<Nombre>_reference/`
> (**reference only**: solo lectura, NO al PYTHONPATH, NO import cruzado). Inventario en §7.
> Un estudio por paper, del tipo `hovernet_estudio.md`:
> [`pulearning_estudio.md`](pulearning_estudio.md) (D),
> [`cellvit_estudio.md`](cellvit_estudio.md) (C),
> [`zoommil_estudio.md`](zoommil_estudio.md) (B),
> [`msclam_estudio.md`](msclam_estudio.md) (el cuarto),
> [`midog_notas.md`](midog_notas.md) (el dataset).
>
> **La recomendación se sostiene: D sigue primero.** Pero la lectura movió cuatro cosas, y dos
> son correcciones a este documento, no matices:
>
> 1. **El paper de PU learning SÍ tiene código** (`github.com/zipeizhao/PU-learning-for-cell-detection`,
>    citado en la pág. 3 del cuerpo, no en la página de abstract, que es por donde se buscó el
>    2-ago). Pero pide **PyTorch 0.4.0 y CUDA 8.0** y no corre en una RTX A6000; lo reusable es
>    la loss, que son **cinco líneas** con el prior hardcodeado en 0.04.
> 2. **Los números 68.3 / 69.3 de ZoomMIL con la cadena 1.25×→2.5×→10× son de BRIGHT, no de
>    CAMELYON16.** La fuente secundaria estaba cruzada. En CAMELYON16 usa 10×→20× y da 83.3 /
>    84.2, o sea **a la par** de CLAM-SB, no mejor. Corregido en §4.
> 3. **El paso 1 (go/no-go) no depende del paper de PU learning.** Necesita pesos públicos de un
>    detector de mitosis, y quien los tiene es el ecosistema de MIDOG. Eso **desacopla** la
>    prueba barata de la decisión cara, que es justo lo que uno quiere.
> 4. **CellViT pierde mucho a la escala de nuestra cohorte privada**: a 0.50 µm/px su recall de
>    detección cae de 0.82 a 0.60. Ver §3.

---

## 1. El entregable: los tres lado a lado, y la recomendación

Ejes: **qué supervisión exige** (que es el filtro que descarta candidatos rápido) y **cuánto
cuesta montarlo acá**.

| | **D. Detector con anotación incompleta** | **C. Del parche al núcleo** | **B. Campo de visión** |
|---|---|---|---|
| **Paper** | Zhao et al., *Positive-unlabeled learning… with incomplete annotations*, MELBA 2022 | Hörst et al., *CellViT*, Medical Image Analysis 2024 | Thandiackal et al., *Differentiable Zooming (ZoomMIL)*, ECCV 2022 |
| **Qué propone** | Reformular el entrenamiento del detector como aprendizaje **positivo-no-etiquetado**: lo no anotado tiene etiqueta **desconocida**, no negativa | Segmentar y clasificar **núcleos** con un ViT, más rápido que HoVer-Net y con pesos públicos | Aprender **a qué zonas hacer zoom**, agregando contexto de varias magnificaciones de punta a punta |
| **Supervisión que exige** | **Positivos parciales**, exactamente los nuestros | **Ninguna nuestra**: viene pre-entrenado en PanNuke | **Solo etiqueta de lámina**, la que ya tenemos |
| **¿Compatible con nuestras marcas?** | **Sí, por construcción.** Es el único que las convierte en señal de entrenamiento | Sí, trivialmente: no las usa | Sí, no las usa |
| **Qué habilita** | Contar mitosis por parche, y de ahí el **conteo en el punto caliente**, que es la regla clínica (§2.b del README) | Razón de tamaño núcleo/vecindario, que es **grado nuclear** e **invariante a la magnificación** | Contexto multi-escala barato y armonización de µm/px entre cohortes |
| **Costo de montarlo** | **Alto**: detector nuevo, dataset público, y evaluación contra las 26 marcas | **Bajo si se acota**: pesos públicos, sin entrenamiento | **Medio**: pirámide multi-escala (el pipeline del B6 ya existe) más re-entrenamiento en GPU |
| **Lo que lo frena hoy** | Con **1 lámina y 26 mitosis** no se entrena nada: hay que arrancar de datos públicos | **No tiene clase mitótica** (las 5 de PanNuke), igual que HoVer-Net. Y **sigue usando watershed** | El privado está escaneado a **20×** y la mitosis se cuenta a **40×**: no hay a dónde hacer zoom |
| **Acceso** | Abierto (MELBA + arXiv) | Abierto (arXiv:2306.15350); la versión de revista es de suscripción | Abierto (ECVA + arXiv) |

### Recomendación: **D primero, y en dos pasos**

**Por qué D y no las otras dos.** Es el único de los tres cuyo régimen de supervisión coincide
con el que tenemos. Las 26 marcas del patólogo hoy solo sirven de validación; el paper de Zhao
es lo que las vuelve entrenables sin mentir sobre los negativos. Y ataca el argumento que
**sobrevivió** a la medición del 1-ago: el recuento de Nottingham es un **conteo en el punto
caliente** (~141 parches contiguos, el 2.9 % de la lámina), no un promedio ponderado. Producir
un conteo es producir exactamente la cantidad que define el puntaje.

**Los dos pasos, y el primero es barato.**

1. **Go/no-go antes de gastar GPU.** Correr un detector de mitosis entrenado en datos públicos
   sobre unas pocas láminas nuestras y medir contra las 26 marcas de la 129741. Datos públicos
   candidatos: **MIDOG 2021** (200 casos de **cáncer de mama humano**, 4 escáneres, CC-BY, ver
   §2.d) y los que usa el propio paper (MITOS-ATYPIA-14, TUPAC). Si el detector no encuentra
   las mitosis que el patólogo marcó, la familia D se cierra ahí y no se gastó un fin de semana
   de GPU. Es el mismo patrón «Etapa 0 antes de Etapa 1» que ya ahorró 18 a 24 h en PathPT
   (Hallazgo 13).

   > **Precisión del 2-ago (noche), y mejora el argumento: este paso NO depende del paper de Zhao.**
   > Lo que necesita son pesos públicos de un detector de mitosis, y el paper de PU learning no
   > publica ninguno (su repo trae la loss, no un modelo entrenado). Quien sí tiene tooling
   > público es el ecosistema de MIDOG: `DeepPathology/MIDOG_reference_docker` (algoritmo de
   > referencia) y `MIDOG_evaluation_docker` (el evaluador oficial), ninguno bajado todavía.
   > Que el paso 1 sea independiente del paso 2 es una ventaja: se puede medir si la detección
   > de mitosis transfiere a nuestras láminas **antes** de comprometerse con la familia D
   > entera. Y el criterio de acierto del challenge (centroide a menos de **7.5 µm**) cae
   > holgadamente dentro de nuestras marcas de 16.7 µm, así que la evaluación contra el geojson
   > es viable sin inventar tolerancias. Detalle: [`midog_notas.md`](midog_notas.md).
2. **Solo si el paso 1 pasa**: fine-tuning con PU learning sobre nuestra cohorte a medida que
   lleguen más láminas anotadas, y de ahí el conteo en el punto caliente como entrada de un
   clasificador chico de `score_1/2/3`.

**El paso 1 tiene un orden de cohortes que importa.** TCGA está a ~40× nativo (0.2325 µm/px) y
el privado a ~20× (0.465 µm/px) ([[cohortes-magnificacion-fisica]]). Los datasets de mitosis se
anotan a la magnificación a la que se cuenta clínicamente, que es 40×. Entonces el go/no-go
corre **primero sobre TCGA**, donde la escala calza sola, y recién después sobre el privado con
reescalado, que es un brazo aparte y con su propio riesgo. La lámina anotada (129741) es
privada, así que la validación contra las marcas cae en el brazo difícil: hay que decirlo antes
de diseñar, no después de ver el número.

**Y le da forma al pedido al patólogo.** Deja de ser «necesitamos más anotaciones» y pasa a ser:
marcas por punto sobre figuras mitóticas, en **N láminas**, y **está bien que sean parciales**,
porque el método está construido para eso. Eso es lo que hoy más destraba la familia D, y se
conecta con que sigue sin saberse quién es «GDT» ni si hay más láminas anotadas.

**Por qué C queda segunda y no primera.** Es la más barata de probar, pero para **mitosis** no
sirve tal cual: ni CellViT ni HoVer-Net tienen clase mitótica. Su valor está en **grado
nuclear**, donde la razón de áreas núcleo/vecindario es directa una vez segmentado y sobrevive
al confundido de magnificación del §2.c. Vale la pena llevarla a la reunión igual, por un motivo
concreto: **pone números a una frase que el README dejó abierta** (§3.C, «hay familias más
nuevas que evitan el watershed o lo hacen mucho más barato, no las afirmo con números»). Los
números están en §3 de acá.

**Por qué B queda tercera.** Su premisa clínica es fuerte (§2.d: le pedimos a 20× lo que el
patólogo hace a 40×) pero eso mismo la bloquea: en el privado **no existe** el 40× al que hacer
zoom. ZoomMIL entrega contexto multi-escala barato y una vía para armonizar µm/px entre
cohortes, que es real y útil, pero no entrega la magnificación que le falta a la tarea.

**Una cuenta que reordena la familia C, y conviene tenerla a mano en la reunión.** Sebastián
pausó C porque HoVer-Net cuesta 3.3 h por lámina, y su propia idea fue correrlo solo sobre los
**20 mejores parches que CLAM selecciona**. Puestos uno al lado del otro: cambiar de modelo
(CellViT) rinde **1.85×**; acotar de los 4799 parches de la lámina a 20 rinde **~240×**. La
elección de modelo es de segundo orden frente a la idea que él ya tenía. Si C se reabre, se
reabre por el subconjunto de parches, no por el paper.

---

## 2. Familia D. Aprendizaje positivo-no-etiquetado para detección celular con anotaciones incompletas

**Estado: BAJADO el 2-ago-2026 (noche)** ([`pulearning_zhao2022_melba.pdf`](pulearning_zhao2022_melba.pdf),
[`pulearning_zhao2022_arxiv.pdf`](pulearning_zhao2022_arxiv.pdf) y el previo de MICCAI
[`pulearning_zhao2021_miccai.pdf`](pulearning_zhao2021_miccai.pdf)) **y leído**:
[`pulearning_estudio.md`](pulearning_estudio.md). **Código encontrado y clonado** en
`clam_testing2/PUcell_reference/`.

Zhao Z, Pang F, Liu Y, Liu Z, Ye C. *Positive-unlabeled learning for binary and multi-class
cell detection in histopathology images with incomplete annotations*. **Machine Learning for
Biomedical Imaging (MELBA), vol. 1, diciembre 2022.** DOI `10.59275/j.melba.2022-8g31` ·
arXiv:2302.08050.

Versión previa, más corta: Zhao et al., *Positive-unlabeled Learning for Cell Detection in
Histopathology Images with Incomplete Annotations*, **MICCAI 2021**, DOI
`10.1007/978-3-030-87237-3_49` · arXiv:2106.15918.

```bibtex
@article{zhao2022pucell,
  title   = {Positive-unlabeled learning for binary and multi-class cell detection in
             histopathology images with incomplete annotations},
  author  = {Zhao, Zipei and Pang, Fengqian and Liu, Yaou and Liu, Zhiwen and Ye, Chuyang},
  journal = {Machine Learning for Biomedical Imaging},
  volume  = {1},
  year    = {2022},
  doi     = {10.59275/j.melba.2022-8g31}
}
```

**Abstract** (verbatim, de arXiv:2302.08050):

> Cell detection in histopathology images is of great interest to clinical practice and
> research, and convolutional neural networks (CNNs) have achieved remarkable cell detection
> results. Typically, to train CNN-based cell detection models, every positive instance in the
> training images needs to be annotated, and instances that are not labeled as positive are
> considered negative samples. However, manual cell annotation is complicated due to the large
> number and diversity of cells, and it can be difficult to ensure the annotation of every
> positive instance. In many cases, only incomplete annotations are available, where some of
> the positive instances are annotated and the others are not, and the classification loss term
> for negative samples in typical network training becomes incorrect. In this work, to address
> this problem of incomplete annotations, we propose to reformulate the training of the
> detection network as a positive-unlabeled learning problem. Since the instances in
> unannotated regions can be either positive or negative, they have unknown labels. Using the
> samples with unknown labels and the positively labeled samples, we first derive an
> approximation of the classification loss term corresponding to negative samples for binary
> cell detection, and based on this approximation we further extend the proposed framework to
> multi-class cell detection. For evaluation, experiments were performed on four publicly
> available datasets. The experimental results show that our method improves the performance of
> cell detection in histopathology images given incomplete annotations for network training.

**Por qué nos toca.** El primer párrafo del abstract describe nuestra situación palabra por
palabra. La anotación de la 129741 marca 26 mitosis y **no es exhaustiva**: las mitosis no
marcadas quedan en el conjunto «sin marca» y un entrenamiento normal las trataría como
negativos, o sea le enseñaría al detector que una mitosis es un no-ejemplo. Este paper cambia
justamente ese término de la loss. Es la respuesta directa a la restricción 2 del encargo, y el
único de los tres que la usa en vez de esquivarla.

**Qué evalúa, y en qué se parece a lo nuestro.** Cuatro datasets públicos, dos de ellos de
**mitosis en mama**: MITOS-ATYPIA-14 y TUPAC. Los otros dos son CRCHistoPhenotypes (núcleos en
adenocarcinoma colorrectal) y NuCLS (núcleos multi-clase en mama). En MITOS-ATYPIA-14 con
anotaciones incompletas por borrado aleatorio reportan **F1 0.507** (recall 0.608, precisión
0.439) contra **0.496** de la línea base BDE.

**Ojo con esa diferencia, porque es chica.** +0.011 de F1 sobre un baseline. El paper es
convincente en el **planteo** (la loss estaba mal especificada y ellos la corrigen) más que en la
magnitud del efecto, y así hay que presentarlo. Con el historial del proyecto (cuatro ejes
cerrados sin mejora) conviene no prometer que el método por sí solo mueva la métrica: lo que
aporta es **permitir entrenar con lo que tenemos**, que hoy directamente no se puede.

> **ADDENDUM 2-ago (noche), con el PDF leído: el encuadre de arriba subvalora el resultado, aunque la
> conclusión no cambia.** El +0.011 es contra **BDE**, que es el competidor especializado.
> Contra el **baseline**, que es lo que haríamos nosotros si entrenáramos de la forma normal, la
> diferencia es **+0.037** (0.470 → 0.507). Y el paper publica el *upper bound* con anotación
> completa, **0.523**: el hueco que abre la anotación incompleta es 0.053, y el método recupera
> **el 70 % de él**. En recall recupera casi todo (0.608 contra un techo de 0.613). Es
> consistente en los 5 folds y significativo con t-test pareado y corrección Benjamini-Hochberg.
>
> **Y aparece una limitación que este documento no tenía, más importante que la magnitud:** el
> régimen de «incompleto» que testean es suave. Borran anotaciones hasta dejar **una por parche
> de 500×500**, lo que deja **~73 % de las marcas**. Nosotros tenemos 26 marcas en 4799 parches.
> **El paper no evalúa ese régimen** y no hay forma de extrapolar la curva. Esa es la salvedad
> que hay que decir en la reunión, más que el tamaño del efecto.

**Qué exigiría implementarlo acá.**

- Un detector base con anotación por punto o por caja. No hay nada de eso en `clam_environ`; es
  código nuevo entero, en `clam_testing2/`, fuera del pipeline MIL.
- Datos públicos para arrancar, porque 26 mitosis no entrenan nada. MIDOG 2021 es el candidato
  natural (§2.d) y es CC-BY.
- Resolver la magnificación **antes** de escribir código: nuestras marcas están a 0.465 µm/px y
  los datasets de mitosis se anotan a 40×. ~~**No verifiqué el µm/px exacto de MIDOG**~~
  **VERIFICADO el 2-ago (noche): MIDOG va de 0.23 a 0.26 µm/px** en sus seis escáneres, y
  **MITOS-ATYPIA-14 está a 0.2455 µm/px**. **TCGA (0.2325) cae dentro del rango** y corre sin
  reescalar; el privado (0.465) está a **2×** de todos ellos. Tabla completa en
  [`midog_notas.md`](midog_notas.md) §1.
- Y después el paso que convierte detección en métrica: agregar el conteo sobre el **mejor
  bloque contiguo de ~141 parches** y clasificar el puntaje. Eso no está en el paper, lo
  ponemos nosotros, y sale del §2.b del README.

**Regla 9.** Nada de esto se implementa sin pre-registro y `reviewer`. Acá solo se identifica.

### 2.d El dataset público que lo acompaña: MIDOG

No es uno de los tres papers, es la fuente de datos que el paso 1 necesita. Dos ediciones, las
dos publicadas en Medical Image Analysis por Aubreville et al.:

- **MIDOG 2021** (MedIA 2023, vol. 84, 102699, DOI `10.1016/j.media.2022.102699`, PMID
  36463832, arXiv:2204.03742). **200 casos de cáncer de mama humano** de entrenamiento y 100 de
  test, repartidos en 4 escáneres (Hamamatsu XR, Hamamatsu S360, Aperio CS2, Leica GT450), dos
  de ellos no vistos en el test. Anotaciones en formato MS COCO. Licencia CC-BY. El algoritmo
  ganador dio **F1 0.748** y superó a seis expertos en la misma tarea.
- **MIDOG 2022** (MedIA 2024, vol. 94, 103155, DOI `10.1016/j.media.2024.103155`, PMID 38537415,
  arXiv:2309.15589). Extiende a varios tipos tumorales y a perro. Ganador **F1 0.764**.

**Lo que MIDOG le dice a nuestro caso, y es incómodo:** su razón de existir es que los
detectores de mitosis **se degradan al cambiar de escáner**. Nuestra cohorte privada es Ventana
(`.bif`), que no está entre sus cuatro. O sea que el riesgo de transferencia no es una
preocupación teórica nuestra, es el resultado central del challenge. Refuerza que el paso 1 sea
un go/no-go y no un supuesto.

---

## 3. Familia C. CellViT: núcleos con Vision Transformers

**Estado: abierto por la versión de autor, no descargado.** La versión de revista es de
suscripción (Elsevier, Europe PMC `isOpenAccess: N`, sin PMCID); el preprint arXiv:2306.15350
es abierto, y el código con los pesos también.

Hörst F, Rempe M, Heine L, Seibold C, Keyl J, Baldini G, Ugurel S, Siveke J, Grünwald B, Egger
J, Kleesiek J. *CellViT: Vision Transformers for precise cell segmentation and classification*.
**Medical Image Analysis 2024, vol. 94, 103143.** DOI `10.1016/j.media.2024.103143` · PMID
38507894 · arXiv:2306.15350 · código `github.com/TIO-IKIM/CellViT`.

```bibtex
@article{horst2024cellvit,
  title   = {CellViT: Vision Transformers for precise cell segmentation and classification},
  author  = {H{\"o}rst, Fabian and Rempe, Moritz and Heine, Lukas and Seibold, Constantin and
             Keyl, Julius and Baldini, Giulia and Ugurel, Selma and Siveke, Jens and
             Gr{\"u}nwald, Barbara and Egger, Jan and Kleesiek, Jens},
  journal = {Medical Image Analysis},
  volume  = {94},
  pages   = {103143},
  year    = {2024},
  doi     = {10.1016/j.media.2024.103143}
}
```

**Los números, verificados contra el texto del preprint:**

| Cantidad | Valor |
|---|---|
| Panoptic quality en PanNuke | 0.50 |
| F1 de detección en PanNuke | 0.83 |
| Velocidad contra HoVer-Net | **1.85× más rápido** (parches de 1024×1024 px, solape 64 px, 10 WSI de esófago) |
| Magnificación esperada | **40× (0.25 µm/px)**; hay experimentos suplementarios a 20× (0.50 µm/px) |
| Clases | 5 de PanNuke: neoplásica, epitelial, inflamatoria, conectiva, muerta |

> **Precisiones del 2-ago (noche), con el PDF completo** ([`cellvit_estudio.md`](cellvit_estudio.md)):
>
> - **El 1.85× es de la variante chica.** Contra HoVer-Net son **1.85× para CellViT256** y
>   **1.39× para CellViT-SAM-H**, que es la de mejores números. Y el speedup viene sobre todo del
>   **parche de inferencia de 1024 px**: el mismo modelo acelera 2.49× al pasar de 256 a 1024. El
>   truco es del tamaño de parche, no de la arquitectura.
> - **A 0.50 µm/px, que es la escala de nuestra cohorte privada, se cae fuerte.** El recall de
>   detección pasa de **0.82 a 0.60** (CellViT256) y de **0.81 a 0.63** (SAM-H), y el F1 baja a
>   0.71 a 0.73, o sea **por debajo de HoVer-Net a 0.25 µm/px (0.80)**. En TCGA el problema no
>   existe; en el privado sí.
> - **La clase mitótica no existe, verificado de la forma más fuerte posible:** la palabra
>   «mitosis» **no aparece ni una vez** en las 23 páginas.
> - Dato de hardware: el paper dice que una **RTX A6000 de 48 GB alcanza** para entrenar las
>   variantes ViT256 y SAM-B. Es nuestra GPU.

**Por qué nos toca.** Es el reemplazo directo del HoVer-Net que `sgaete` ya tiene corriendo:
mismo dataset de entrenamiento (PanNuke), misma familia de salida (instancias de núcleo con
clase), pesos públicos. Y para **grado nuclear** es la familia que mejor calza con lo que
describió el patólogo, porque «núcleos más grandes que su vecindario» es una razón entre áreas
una vez que hay núcleos segmentados, y una razón es invariante a la escala, que es el confundido
del §2.c.

**Dos cosas que hay que decir en la misma frase, porque acotan el entusiasmo.**

- **No tiene clase mitótica.** Las cinco de PanNuke no incluyen mitosis. Es exactamente la
  limitación que ya cerramos para HoVer-Net (su clase *miscelánea* mezcla mitótico y necrótico,
  F 0.426), y CellViT no la resuelve: la esquiva por no tener la clase. **Para contar mitosis no
  sirve.**
- **Sigue usando watershed.** Verificado en el texto: gradiente de los mapas de distancia
  horizontal y vertical, filtro Sobel, y **watershed controlado por marcadores** para separar
  núcleos superpuestos. O sea que **no** es el que elimina los 75 min de CPU que el README §3.C
  señaló como el grueso del costo. El 1.85× es de la tubería completa, no de haber sacado ese
  paso.

**El que sí elimina el post-procesamiento, para completar la frase abierta del README.**
Pekár M, Musil V, Nenutil R, Holub P, Brázdil T. *LSP-DETR: Efficient and Scalable Nuclei
Segmentation in Whole Slide Images*, arXiv:2601.03163 (6-ene-2026). Representa los núcleos como
**polígonos estrella-convexos** y una loss de distancia radial hace que la separación de núcleos
superpuestos emerja sola, **sin post-procesamiento hecho a mano**; reportan ser **más de 5×
más rápido que el siguiente método más rápido**, evaluado en PanNuke y MoNuSeg. **Es un
preprint de enero de 2026**, no verifiqué que haya pesos públicos, y no lo propongo como
candidato a implementar: lo dejo anotado porque es la respuesta con número a lo que el README
dejó como afirmación sin respaldo.

**Qué exigiría implementarlo acá.** Poco, si se acota: los pesos están publicados y no hay que
entrenar. El trabajo real es (i) decidir sobre qué parches correrlo, y ahí manda la idea de
Sebastián de los 20 mejores de CLAM, (ii) convertir las instancias de núcleo en features por
parche, y (iii) meter esas features al agregador. El punto (iii) es donde vive el riesgo de
diseño, y es donde SI-MIL ya nos mostró que se puede perder métrica.

---

## 4. Familia B. ZoomMIL: aprender a hacer zoom

**Estado: abierto, no descargado.** Actas de ECCV en ECVA, más arXiv y código.

Thandiackal K, Chen B, Pati P, Jaume G, Williamson DFK, Gabrani M, Goksel O. *Differentiable
Zooming for Multiple Instance Learning on Whole-Slide Images*. **ECCV 2022.** arXiv:2204.12454 ·
código `github.com/histocartography/zoommil`.

```bibtex
@inproceedings{thandiackal2022zoommil,
  title     = {Differentiable Zooming for Multiple Instance Learning on Whole-Slide Images},
  author    = {Thandiackal, Kevin and Chen, Boqi and Pati, Pushpak and Jaume, Guillaume and
               Williamson, Drew F. K. and Gabrani, Maria and Goksel, Orcun},
  booktitle = {European Conference on Computer Vision (ECCV)},
  year      = {2022}
}
```

**Abstract** (verbatim, de arXiv:2204.12454):

> Multiple Instance Learning (MIL) methods have become increasingly popular for classifying
> giga-pixel sized Whole-Slide Images (WSIs) in digital pathology. Most MIL methods operate at a
> single WSI magnification, by processing all the tissue patches. Such a formulation induces
> high computational requirements, and constrains the contextualization of the WSI-level
> representation to a single scale. A few MIL methods extend to multiple scales, but are
> computationally more demanding. In this paper, inspired by the pathological diagnostic
> process, we propose ZoomMIL, a method that learns to perform multi-level zooming in an
> end-to-end manner. ZoomMIL builds WSI representations by aggregating tissue-context
> information from multiple magnifications. The proposed method outperforms the state-of-the-art
> MIL methods in WSI classification on two large datasets, while significantly reducing the
> computational demands with regard to Floating-Point Operations (FLOPs) and processing time by
> up to 40x.

**Por qué nos toca.** Es la formalización de lo que el patólogo hace y nuestro pipeline no:
mirar en bajo aumento, elegir dónde, y recién ahí acercar. Un módulo de atención con compuerta
entre dos magnificaciones consecutivas decide qué instancias se amplían y a la vez mejora la
representación de la magnificación baja. Entrena **solo con etiqueta de lámina**, que es la que
ya tenemos, y no pide una anotación nueva. Y su preprocesamiento son features de parche en
`.h5`, o sea la misma forma de dato que ya producimos.

**El bloqueo, y es de la cohorte, no del método.** Nuestro privado está escaneado a **20×**
(`objective-power = 20`, 0.465 µm/px, medido en la 129741) y la mitosis se cuenta a **40×**. Un
método que aprende a hacer zoom **no puede hacer zoom a una magnificación que el archivo no
contiene**. En TCGA (~40× nativo) sí. Entonces para mitosis, B resuelve el contexto y la
eficiencia, no el detalle que falta.

**Dónde sí aporta.** En el confundido del §2.c: si la pirámide se parametriza en **µm/px
físicos** y no en `level`, un modelo multi-escala es la vía natural para que TCGA a 0.2325 y el
privado a 0.465 dejen de ser dos escalas distintas sin avisar. Esa infraestructura ya está
escrita y sin lanzar del eje de magnificación del B6
([[magnificacion-cpathagent-proxima-direccion]], `scripts/extract_multiscale_features.py`), y
este paper es el argumento para gastarla acá en vez de como mejora genérica.

~~**Un dato que NO verifiqué contra el paper.** Circula que en CAMELYON16 usan la cadena
1.25× → 2.5× → 10× y que dan F1 ponderado 68.3 ± 1.1 y accuracy 69.3 ± 1.0.~~

> **CORREGIDO el 2-ago (noche) contra el PDF: ese dato estaba mal atribuido.** Los 68.3 ± 1.1 / 69.3 ± 1.0
> con la cadena 1.25× → 2.5× → 10× son de **BRIGHT** (Tabla 2), que es un dataset de **mama**.
> En **CAMELYON16** (Tabla 3) ZoomMIL usa **10× → 20×** y da **83.3 ± 0.3 / 84.2 ± 0.4**, contra
> CLAM-SB 83.3 ± 1.5 / 84.0 ± 1.3 y TransMIL 83.6 ± 2.6 / 85.3 ± 1.9: **queda a la par, no
> mejor**, con ~2.6× menos FLOPs.
>
> **Y la corrección viene con el dato que más pesa para mitosis, que es del propio paper.** Los
> autores explican que en CAMELYON16 tuvieron que **subir la magnificación más baja a 10×**
> porque *«las regiones metastásicas pueden ser extremadamente chicas»*, y agregan que **aun así
> eso perjudica el rendimiento**. O sea que el mecanismo de zoom **se degrada cuando el objeto es
> chico**, dicho por ellos. Una micro-metástasis mide cientos de micras; una figura mitótica
> marcada mide **16.7 µm**. Esto **refuerza** que B quede tercera para mitosis, y ahora es un
> número del paper y no una inferencia nuestra.
>
> **Donde B sí gana es en mama:** en BRIGHT le saca **5.2 puntos de weighted-F1 a CLAM-SB** con
> 12.8× menos FLOPs. Ese es el argumento honesto para probarlo, y es sobre tareas que **no**
> dependen de objetos chicos. Detalle: [`zoommil_estudio.md`](zoommil_estudio.md) §4 y §5.

**Qué exigiría implementarlo acá.** Re-extraer features en varias escalas para la tarea de
mitosis (GPU, y el pipeline existe), un `--model_type` nuevo en `scripts/train_dsmil.py` según
la receta de `@mil-model-integration`, y comparación pareada reusando el mismo `--split_dir`
([[patron-paired-comparison-reuso-splits]]). Es la más «nuestra» de las tres en términos de
infraestructura, y la que menos promete para mitosis.

---

## 5. Un cuarto, fuera de las tres familias, que igual conviene llevar

Lo agrego porque el encargo dice **«aprovechando la información del patólogo sobre las
etiquetas»** y este es el paper que responde a esa frase de la forma más literal: es CLAM con
supervisión mixta. No entra en B, C ni D, y **tampoco es familia A**: no toca el operador de
agregación, cambia la supervisión. Va como quinto lugar en prioridad, y con un motivo concreto,
no por desinterés.

Tourniaire P, Ilie M, Hofman P, Ayache N, Delingette H. *MS-CLAM: Mixed supervision for the
classification and localization of tumors in Whole Slide Images*. **Medical Image Analysis
2023, vol. 85, 102763.** DOI `10.1016/j.media.2023.102763` · PMID 36764037.

**Acceso: abierto por HAL.** La versión de revista es de suscripción (Europe PMC
`isOpenAccess: N`, sin PMCID), pero la versión de autor está libre en el repositorio de Inria:
`https://inria.hal.science/hal-03972289`. No se descargó.

**Qué propone.** Partiendo de MIL con atención, usar **supervisión mixta**, o sea etiquetas de
lámina **y** etiquetas de parche, para mejorar a la vez clasificación y localización, usando
solo una cantidad limitada de láminas con anotación de parche. Agregan un término de loss sobre
la atención y un método de lotes pareados. Reportan acercarse al rendimiento totalmente
supervisado usando entre el **12 y el 62 %** de las anotaciones de parche disponibles, en
DigestPath2019 y Camelyon16.

**Por qué queda quinto y no primero, que es la parte útil para la reunión.** Ese 12 a 62 % es
una fracción de un conjunto **completo** de anotaciones de parche. Nosotros tenemos **una**
lámina anotada sobre miles, y encima con positivos parciales, mientras que el método asume que
en la lámina anotada la etiqueta de parche es correcta. O sea que no es que sea caro: es que hoy
no hay con qué. Sirve como respuesta preparada si en la reunión sale «¿y por qué no le agregamos
supervisión de parche a CLAM y listo?»: se puede, está publicado, y necesita un orden de
magnitud más de anotación del que tenemos.

> **ADDENDUM 2-ago (noche): leído, y el diagnóstico se afina** ([`msclam_estudio.md`](msclam_estudio.md)).
> El paper tiene una sección entera, **§2.5 «MS-CLAM without tile-level labels»**, para el caso
> sin anotación: las láminas sin etiquetas de parche usan las **pseudo-etiquetas de atención** de
> CLAM de siempre, y el método **degrada con gracia** hasta volver a ser CLAM. Su ajuste más chico
> usa 11 láminas tumorales anotadas.
>
> **Así que la escasez no es lo que lo mata; lo que lo mata es la parcialidad.** El primer término
> de su loss de atención minimiza la suma de atención de los parches marcados como **no**
> tumorales, o sea **empuja a cero la atención de todo lo no marcado**. Con positivos parciales
> ese es el gradiente exactamente equivocado: castigaría al modelo por mirar una mitosis que el
> patólogo no marcó. Es la **hipótesis opuesta** a la del paper de PU learning, y por eso los dos
> no se pueden mezclar sin reescribir la ec. 3.
>
> Nota que conviene tener a mano: el problema que MS-CLAM resuelve es que **la atención de CLAM
> se derrama** (Dice 0.520 en Camelyon16, cubriendo casi todo el tejido). En nuestra medición del
> 1-ago la atención **no** se derramó: cayó sobre las marcas. Llegamos a este paper con el
> síntoma que arregla ya bastante ausente.

---

## 6. Lo que este documento no afirma

- **Que alguno de los tres suba la métrica.** Ninguno está probado en nuestros datos, y el
  historial del proyecto son cuatro ejes cerrados sin mejora (Hallazgos 11 a 14). Lo que se
  afirma es cuál es compatible con la supervisión que tenemos y cuánto costaría probarlo.
- **Que la familia D vaya a transferir a nuestra cohorte.** MIDOG existe justamente porque los
  detectores de mitosis se caen al cambiar de escáner, y el nuestro (Ventana) no está entre los
  suyos. Por eso el paso 1 es un go/no-go, no un supuesto.
- **Ningún número que no haya verificado en la fuente.** ~~Los de CellViT salen del texto del
  preprint; los de MIDOG y del paper de PU learning, de sus abstracts y de la página de MELBA.
  El de ZoomMIL sobre CAMELYON16 queda marcado como **no verificado** en §4, y el µm/px de MIDOG
  como **no verificado** en §2.~~
  **Al 2-ago (noche) los cinco huecos están cerrados contra los PDF**: el µm/px de MIDOG (§2.d y
  [`midog_notas.md`](midog_notas.md)), los números de ZoomMIL (§4, **estaban mal atribuidos**),
  el código de D (§2, **existe**), el mecanismo de agregación de ZoomMIL
  ([`zoommil_estudio.md`](zoommil_estudio.md) §6) y qué hace MS-CLAM sin anotación de parche
  (§5). Lo que **sigue sin verificar**: si LSP-DETR tiene pesos públicos, y todo lo de MIDOG 2022.
- **Que estos sean los únicos candidatos.** Es una búsqueda de una sesión con una fecha encima.
  Quedaron sin fichar, entre otros, las ediciones 2023 a 2025 de MIDOG, la línea de detección de
  figuras mitóticas atípicas en mama (AMi-Br), y los métodos multi-escala alternativos a ZoomMIL
  (HIPT, ensambles multi-magnificación).
- **Nada de esto está implementado ni pre-registrado.** Regla 9: si alguno avanza, va con
  hipótesis pre-registrada, métrica y dirección esperada, y `reviewer` antes de tocar código.

---

## 7. Inventario de lo descargado (2-ago-2026 (noche))

Descarga autorizada explícitamente por Ernesto al cerrar la sesión del 2-ago, **acotada a estos
papers y estos repos**. No se extiende a nada más: si aparece un sexto paper interesante, se ficha
y se pregunta.

**PDF, en esta carpeta.** Todos verificados como PDF válido y abiertos con `pdftotext`.

| Archivo | Fuente | Tamaño |
|---|---|---|
| `pulearning_zhao2022_melba.pdf` | `melba-journal.org/pdf/2022:027.pdf` | 4.9 M, 30 pág. |
| `pulearning_zhao2022_arxiv.pdf` | arXiv:2302.08050 | 5.0 M, 30 pág. |
| `pulearning_zhao2021_miccai.pdf` | arXiv:2106.15918 | 1.6 M, 11 pág. |
| `cellvit_horst2024.pdf` | arXiv:2306.15350 | 11 M, 23 pág. |
| `zoommil_thandiackal2022.pdf` | arXiv:2204.12454 | 15 M, 19 pág. |
| `msclam_tourniaire2023.pdf` | HAL `inria.hal.science/hal-03972289` | 9.7 M, 17 pág. |
| `midog_aubreville2023.pdf` | arXiv:2204.03742 | 11 M, 19 pág. |
| `lspdetr_pekar2026.pdf` | arXiv:2601.03163 | 5.5 M, 34 pág. (sin leer todavía) |

**Repos, en `clam_testing2/`, fuera del repo personal.** Mismas reglas que
`CLAM_official_reference/` e `ILSC_reference/`: **solo lectura, NO al PYTHONPATH, NO import
cruzado** con el codebase de Sebastián. **No se bajó ningún checkpoint.**

| Directorio | Origen | HEAD | Tamaño |
|---|---|---|---|
| `PUcell_reference/` | `zipeizhao/PU-learning-for-cell-detection` | `1bce728` (6-nov-2022) | 120 M |
| `CellViT_reference/` | `TIO-IKIM/CellViT` | `05097e1` (23-jul-2025) | 130 M |
| `ZoomMIL_reference/` | `histocartography/zoommil` | `da7bb7f` (3-nov-2022) | 1.6 M |
| `MSCLAM_reference/` | `paul-tourniaire/MS-CLAM` | `18e8827` (29-ago-2024) | 5.1 M |

**No se bajó:** el tooling de MIDOG (`DeepPathology/MIDOG_reference_docker` y
`MIDOG_evaluation_docker`) ni el dataset de MIDOG, porque están fuera de la lista autorizada.
Son el primer lugar donde mirar si el paso 1 se aprueba.
