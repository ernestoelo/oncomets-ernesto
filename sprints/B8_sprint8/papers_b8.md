# Papers a estudiar para la reunión con Sebastián (B8)

Los tres que salieron de la reunión del 24-jul-2026. Descargados el **27-jul-2026** con
autorización de Ernesto (workaround E: no se baja nada de afuera sin pedido explícito).

> **Nota de convención:** el repo guarda los papers en [`papers/`](../../papers/) con una
> entrada en su tabla de inventario. Estos quedan acá porque Ernesto los pidió en la
> carpeta del sprint. Si conviene, se mueven después y se indexan allá; lo que **no** hay
> que hacer es duplicar el PDF en los dos lugares.

---

## 1. Hover-Net ✅ descargado

**Archivo:** `hovernet_graham2019.pdf` (5.7 MB, arXiv:1812.06499v5, 13-nov-2019)

Graham, Vu, Raza, Azam, Tsang, Kwak, Rajpoot. *HoVer-Net: Simultaneous Segmentation and
Classification of Nuclei in Multi-Tissue Histology Images*. Medical Image Analysis, 2019.

```bibtex
@article{graham2019hovernet,
  title   = {HoVer-Net: Simultaneous Segmentation and Classification of Nuclei in
             Multi-Tissue Histology Images},
  author  = {Graham, Simon and Vu, Quoc Dang and Raza, Shan E Ahmed and Azam, Ayesha and
             Tsang, Yee Wah and Kwak, Jin Tae and Rajpoot, Nasir},
  journal = {Medical Image Analysis},
  volume  = {58},
  pages   = {101563},
  year    = {2019},
  doi     = {10.1016/j.media.2019.101563}
}
```

**Por qué nos toca:** trabaja a nivel de **núcleo**, no de parche. Es la vía más creíble
para ponerle nombre real al tejido que hoy nombramos por **lectura visual nuestra**, que
es la salvedad que arrastramos desde OBJ-A y que sigue sin sign-off de patólogo
([[mammoth-interpretabilidad-objA]], [[slot-unidad-de-morfologia]]).

## 2. SI-MIL ✅ descargado

**Archivo:** `simil_kapse2024.pdf` (28 MB, arXiv:2312.15010v2, 18-may-2024)

Kapse, Pati, Das, Zhang, Chen, Vakalopoulou, Saltz, Samaras, Gupta, Prasanna. *SI-MIL:
Taming Deep MIL for Self-Interpretability in Gigapixel Histopathology*. CVPR 2024.

```bibtex
@inproceedings{kapse2024simil,
  title     = {SI-MIL: Taming Deep MIL for Self-Interpretability in Gigapixel
               Histopathology},
  author    = {Kapse, Saarthak and Pati, Pushpak and Das, Srijan and Zhang, Jingwei and
               Chen, Chao and Vakalopoulou, Maria and Saltz, Joel and Samaras, Dimitris
               and Gupta, Rajarsi R. and Prasanna, Prateek},
  booktitle = {Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern
               Recognition (CVPR)},
  year      = {2024}
}
```

**Por qué nos toca:** es interpretabilidad ***self-*** dentro del MIL, o sea el mismo eje
del Sprint 7 pero con otra estrategia. Nuestro análisis de expertos y slots es **post-hoc**
sobre un modelo ya entrenado; este propone que la interpretabilidad salga del propio
diseño. Buen contraste para la discusión.

**✅ LEÍDO el 30-jul-2026** (principal + suplementario §8 a §17). El estudio completo, con
el contraste contra lo nuestro, los bloqueos para aplicarlo acá y las preguntas para la
reunión, está en [`simil_estudio.md`](simil_estudio.md). Tres cosas que salieron de la
lectura y conviene tener a mano:

- **HoVer-Net es el front-end de SI-MIL**, así que los papers 1 y 2 de este encargo no son
  dos ángulos separados sino la misma cadena.
- En la única celda que nos corresponde (**CLAM** como MIL de base, Tabla 2) SI-MIL rinde
  un poco **menos** que CLAM a secas (0.937 → 0.925 acc, 0.972 → 0.957 AUC). El titular de
  «sin compromiso entre rendimiento e interpretabilidad» está sostenido sobre ABMIL.
- **HoVer-Net exige 40×** y ellos filtraron sus datasets a eso, lo que choca con nuestras
  cohortes a magnificación física distinta ([[cohortes-magnificacion-fisica]]).

## 3. Invasión linfovascular ⚠ NO descargable

Chen J, Yang Y, Luo B, Wen Y, Chen Q, Ma R, Huang Z, Zhu H, Li Y, Chen Y, Qian D.
*Further predictive value of lymphovascular invasion explored via supervised deep learning
for lymph node metastases in breast cancer*. **Human Pathology 131:26-37 (2023)**.
DOI `10.1016/j.humpath.2022.11.007` · PMID `36481204`.

**Estado: de suscripción (Elsevier), sin versión en PMC ni preprint abierto** (verificado
contra la API de Europe PMC: `isOpenAccess: N`, `PMCID: None`, único enlace de texto
completo = "Subscription required"). **No lo bajé**: hacerlo exigiría saltar el paywall.
Se consigue con acceso institucional UTFSM o la suscripción de Environ.

```bibtex
@article{chen2023lbvi,
  title   = {Further predictive value of lymphovascular invasion explored via supervised
             deep learning for lymph node metastases in breast cancer},
  author  = {Chen, Jiaxian and Yang, Yanmei and Luo, Bo and Wen, Yanhui and Chen, Qingtang
             and Ma, Ru and Huang, Zhicheng and Zhu, Hangjia and Li, Yan and Chen, Yun and
             Qian, Dahong},
  journal = {Human Pathology},
  volume  = {131},
  pages   = {26--37},
  year    = {2023},
  doi     = {10.1016/j.humpath.2022.11.007}
}
```

**Abstract** (de PubMed, distribución libre):

> Lymphovascular invasion, specifically lymph-blood vessel invasion (LBVI), is a risk
> factor for metastases in breast invasive ductal carcinoma (IDC) and is routinely
> screened using hematoxylin-eosin histopathological images. However, routine reports only
> describe whether LBVI is present and does not provide other potential prognostic
> information of LBVI. This study aims to evaluate the clinical significance of LBVI in 685
> IDC cases and explore the added predictive value of LBVI on lymph node metastases (LNM)
> via supervised deep learning (DL), an expert-experience embedded knowledge transfer
> learning (EEKT) model in 40 LBVI-positive cases signed by the routine report.
> Multivariate logistic regression and propensity score matching analysis demonstrated that
> LBVI (OR 4.203, 95% CI 2.809-6.290, P < 0.001) was a significant risk factor for LNM.
> Then, the EEKT model trained on 5780 image patches automatically segmented LBVI with a
> patch-wise Dice similarity coefficient of 0.930 in the test set and output counts,
> location, and morphometric features of the LBVIs. Some morphometric features were
> beneficial for further stratification within the 40 LBVI-positive cases. The results
> showed that LBVI in cases with LNM had a higher short-to-long side ratio of the minimum
> rectangle (MR) (0.686 vs. 0.480, P = 0.001), LBVI-to-MR area ratio (0.774 vs. 0.702,
> P = 0.002), and solidity (0.983 vs. 0.934, P = 0.029) compared to LBVI in cases without
> LNM. The results highlight the potential of DL to assist pathologists in quantifying LBVI
> and, more importantly, in exploring added prognostic information from LBVI.

**Por qué nos toca, y qué se puede leer ya del abstract:**

- Es **nuestra tarea `invasion_linfatica_vascular`**, una de las 3 del Sprint 7, y apunta
  al objetivo clínico del proyecto (metástasis ganglionar).
- **Es supervisado a nivel de píxel**, no MIL débilmente supervisado: segmenta el LBVI con
  Dice 0.930 sobre 5780 parches anotados. Nuestra tarea es de etiqueta por lámina, sin
  anotación por parche. Es una diferencia de régimen que conviene tener clara antes de
  discutirlo, porque cambia qué de acá es aplicable a nuestro pipeline.
- **El aporte interesante para nosotros es el otro:** que el reporte de rutina solo dice
  presente o ausente, y que las **features morfométricas** del LBVI (relación de lados del
  rectángulo mínimo, razón de áreas, solidez) estratifican dentro de los positivos. Eso es
  el mismo salto que discutimos con los slots: pasar de "está" a "cómo es".
- Ojo con el n: **40 casos LBVI-positivos** para la parte de deep learning, sobre 685 IDC.

---

## 4. ILSC / Co-assistant networks ⚠ NO descargable, pero el código es público

**Pedido de Sebastián por correo el 29-jul-2026, 12:15**, con prioridad explícita de
relleno: *«Solo si te queda tiempo revisemos este también. Si no lo dejamos para la próxima
semana.»*

Liu Z, Shen JY, Cui L, Xu M, Zhu X, Shi X. *Co-assistant networks by pathology foundation
model and convolutional neural network for gigapixel whole slide image analysis*.
**Medical Image Analysis, 2026.** DOI `10.1016/j.media.2026.104202` · PMID `42398343`.

```bibtex
@article{liu2026ilsc,
  title   = {Co-assistant networks by pathology foundation model and convolutional neural
             network for gigapixel whole slide image analysis},
  author  = {Liu, Zhuoran and Shen, Jun-yi and Cui, Lei and Xu, Meilian and Zhu, Xiaofeng
             and Shi, Xiaoshuang},
  journal = {Medical Image Analysis},
  year    = {2026},
  doi     = {10.1016/j.media.2026.104202}
}
```

**Estado: de suscripción (Elsevier), sin PDF abierto.** Búsqueda autorizada por Ernesto el
30-jul-2026 y hecha: Europe PMC devuelve `isOpenAccess: N`, `inPMC: N`, `hasPDF: N`, sin
PMCID y con un único enlace de texto completo marcado *«Subscription required»*; la API de
arXiv devuelve **0 entradas** para el título, y Semantic Scholar lo da como `Closed` sin
`openAccessPdf`. **No se descargó**: bajarlo exigiría saltar el paywall. Es el mismo caso
que el paper de Human Pathology (§3), y se resuelve igual: acceso institucional UTFSM o
suscripción de Environ.

**Lo que sí es público: el código, y ya está clonado.** Los autores publican la
implementación en `github.com/lZhuoRan/ILSC`. Clonado el **30-jul-2026** con autorización
de Ernesto a `clam_testing2/ILSC_reference/` (HEAD `f193187`, 117 MB), bajo las mismas
reglas que `CLAM_official_reference/`: **solo lectura, NO al PYTHONPATH, NO import
cruzado**. Como el paper es de suscripción, **el código es la única vía abierta al
método**. Estructura: `main.py`, `model/{model.py,PFM_model.py}`, `preprocess/`
(incluido `process_for_clam.py` y `generate_npy.py`), `datasets/`, `utils/`, `ILSC.yml`.

**Abstract** (de PubMed, distribución libre):

> Multiple instance learning (MIL) with pre-trained models to extract patch-level features
> has been widely used in whole slide image (WSI) analysis to avoid expensive pixel-level
> annotations. Although pre-trained pathology foundation model (PFM) have achieved
> promising performance on WSI analysis, their performance is still restricted by two key
> challenges: (i) self-attention mechanisms might encode trivial or noisy relations during
> fine-grained feature aggregation, and (ii) self-attention mechanisms struggle to capture
> local patterns. To overcome these limitations, we propose an Interpretable Large-Small
> Co-assistant (ILSC) framework, which synergistically integrates a PFM with a small
> convolutional neural network (CNN) to leverage their complementary advantages. The
> framework comprises three core components: (i) a general-feature extraction model that
> leverages a pre-trained PFM with adapter and attention modules to capture global and
> universal pathological features, (ii) a specific-feature extraction model that employs a
> CNN with cell-level attention to mine discriminative task-specific local features, and
> (iii) a feature fusion module that integrates both pathways using patch-attention for
> slide-level classification. Extensive experiments demonstrate that the proposed framework
> achieves superior classification performance compared to recent state-of-the-art methods,
> while also offering enhanced interpretability and generalizability. Furthermore,
> experiments illustrate that the small CNN model can boost the interpretability of PFM,
> while the pre-trained PFM can strengthen the generalizability of CNN for WSI analysis.

**Por qué nos toca, y qué se puede leer ya sin el PDF:**

- **Es la misma familia de idea que SI-MIL** (§2): dos ramas donde una red potente se
  aparea con otra más acotada y legible. En SI-MIL la segunda rama es un lineal sobre
  features de patología con nombre; acá es una CNN chica con atención a nivel de célula.
  El hilo del encargo 4 se sostiene solo.
- **Su premisa es una crítica al foundation model, que es nuestro caso.** Dicen que el
  problema del PFM son las relaciones triviales o ruidosas que mete la self-attention y su
  dificultad para captar patrones locales. CONCH es nuestro PFM, así que la crítica aplica
  a nuestro pipeline sin traducción.
- **La barrera de entrada es mucho más baja que la de SI-MIL.** Según el README, su
  preprocesamiento es **CLAM** (usa los `.h5` de coordenadas), que es exactamente lo que
  corremos nosotros; y su demo es CAMELYON16, binario. SI-MIL, en cambio, exige HoVer-Net a
  40× y unas 2 h por lámina. Si en algún momento se prueba algo de esta línea, esta cuesta
  menos.
- **Ojo con dos cosas antes de entusiasmarse.** El PFM de su implementación es **PLIP**, no
  CONCH: **verificado contra el código clonado** (89 menciones de `plip` entre `.py`, `.md`
  y `.yml`, y cero de `conch`), no solo contra el README. Y «superior classification
  performance» viene del abstract: no hay tabla a la vista, así que **no se cita como
  resultado** hasta leer el paper.

**Prioridad: tercero.** El propio Sebastián lo puso como opcional, y Hover-Net subió de
importancia con la lectura de SI-MIL (es su front-end, ver §2).
