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
