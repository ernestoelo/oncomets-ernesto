# PU learning para detección celular: estudio (familia D)

> Zhao Z, Pang F, Liu Y, Liu Z, Ye C, *Positive-unlabeled learning for binary and multi-class
> cell detection in histopathology images with incomplete annotations*, **Machine Learning for
> Biomedical Imaging (MELBA) vol. 1, dic-2022**. DOI `10.59275/j.melba.2022-8g31`.
> PDF en [`pulearning_zhao2022_melba.pdf`](pulearning_zhao2022_melba.pdf) (30 pág., versión de
> revista) y [`pulearning_zhao2022_arxiv.pdf`](pulearning_zhao2022_arxiv.pdf) (arXiv:2302.08050,
> mismo contenido). Versión previa MICCAI 2021, más corta:
> [`pulearning_zhao2021_miccai.pdf`](pulearning_zhao2021_miccai.pdf) (arXiv:2106.15918).
>
> **Bajados el 3-ago-2026** con autorización explícita de Ernesto. Ficha bibliográfica y BibTeX:
> [`papers_mitosis.md`](papers_mitosis.md) §2.
>
> **Código: SÍ existe**, y el 2-ago se dio por no localizado. Está citado en el cuerpo del paper
> (pág. 3), no en la página de abstract, que es por donde se buscó:
> `github.com/zipeizhao/PU-learning-for-cell-detection`. Clonado en
> `clam_testing2/PUcell_reference/` (HEAD `1bce728`, 6-nov-2022, 120 MB), **reference only**.
> El §7 explica por qué encontrarlo cambia menos de lo que parece.

---

## 1. Qué propone, en una frase

Que cuando el patólogo anota **algunas** de las células y no todas, el término de la loss que
castiga a los falsos positivos está **mal especificado**, porque le enseña al detector que las
células no marcadas son ejemplos negativos; y que ese término se puede **reescribir** usando
solo positivos y no-etiquetados, sin inventar negativos.

No es un modelo nuevo. Es un cambio en **una** de las dos mitades de la loss de clasificación de
un detector estándar, y los autores lo dicen así: el método es agnóstico a la arquitectura.

## 2. El problema, en los términos del paper

Un detector tipo Faster R-CNN entrena con una loss que suma localización y clasificación. La de
clasificación (ec. 1) es:

```
L_cls = 1/(Nn+Np) · [ Σ_j H(c_n^j, 0)  +  Σ_i H(c_p^i, 1) ]
```

donde los `Np` positivos son las cajas que solapan mucho con una marca, y los `Nn` negativos son
**todo lo demás**. Ese "todo lo demás" es el supuesto que se rompe: con anotación incompleta, una
mitosis no marcada cae en el segundo grupo y el gradiente empuja activamente al detector a
llamarla negativa.

El paper lo dice sin rodeos (pág. 4): *"the regions with no instances labeled as positive are not
necessarily all truly negative"*. Esa frase es literalmente nuestra situación
([[anotaciones-patologo-qupath]]: las 26 marcas de la 129741 son positivos parciales, y lo no
marcado no es negativo).

## 3. La derivación, que son cuatro pasos y vale seguirla

**Paso 1.** La loss es una estimación empírica de la esperanza `E[H(c,z)]`, que se parte por clase
usando el **prior positivo** `π = Pr(z=1)` (ec. 2):

```
E[H(c,z)] = (1-π)·E_{x|z=0}[H(c,0)]  +  π·E_{x|z=1}[H(c,1)]
```

El segundo término se puede estimar: son los positivos, y esos sí los tenemos. El primero no,
porque exige saber cuáles son los negativos.

**Paso 2.** Se despeja la densidad de los negativos de la mezcla,
`Pr(z=0)p(x|z=0) = p(x) - Pr(z=1)p(x|z=1)`, y el término inaccesible queda (ec. 4):

```
(1-π)·E_{x|z=0}[H(c,0)]  =  E_x[H(c,0)]  -  π·E_{x|z=1}[H(c,0)]
```

Ahí está el truco: la esperanza sobre los **negativos** se cambia por una esperanza sobre **todo**
menos una corrección sobre los positivos. Ninguna de las dos necesita saber qué es negativo.

**Paso 3, y es la contribución específica para detección.** Falta estimar `E_x[H(c,0)]`. El PU
learning clásico (Kiryo 2017) lo aproxima con los no-etiquetados solos, `E_{x_u}[H(c,0)]`, porque
asume que la distribución de los no-etiquetados es la de `x`. En **detección** eso es falso: los
positivos y los no-etiquetados salen de la **misma imagen**, así que sacar los positivos del
conjunto sesga la estimación. La corrección de los autores (ec. 6) es unir los dos conjuntos:

```
E_x[H(c,0)] ≈ 1/(Nu+Np) · [ Σ_k H(c_u^k, 0)  +  Σ_i H(c_p^i, 0) ]
```

Le llaman *naive approximation* a la versión sin unir, y en §3.2.2 muestran que rinde peor que la
suya en los 5 folds (y en el fold 1 rinde peor incluso que BDE, el competidor). O sea que el
detalle no es cosmético.

**Paso 4.** Una red expresiva puede hacer que el término estimado se vuelva **negativo** por
sobreajuste, lo que rompe la loss. Como en Kiryo, se lo trunca en cero (ec. 7):

```
max{ 0,  1/(Nu+Np)[Σ_k H(c_u^k,0) + Σ_i H(c_p^i,0)]  -  π/Np · Σ_i H(c_p^i,0) }
```

## 4. El prior π, que es el único hiperparámetro nuevo y el punto sensible

`π` se asume conocido en la teoría, y en la práctica **no lo es**. La solución del paper (§2.3) es
tratarlo como hiperparámetro y buscarlo en un rango sobre el conjunto de validación.

**Y acá hay algo que nos calza de una forma que conviene notar:** dicen que con anotación
incompleta **la precisión medida en validación deja de tener sentido** (un "falso positivo" puede
ser una célula real sin marcar), así que seleccionan `π` por el **mejor recall promedio**. Es
exactamente el mismo razonamiento que ya escribimos en
[`../atencion_vs_patologo/resultados.md`](../atencion_vs_patologo/resultados.md) §6 ("un parche
sin marca con atención alta no es un error del modelo"). El paper le da forma de procedimiento.

Los rangos que usaron, por dataset, dan una idea del orden de magnitud:

| Dataset | Rango de π | Valor elegido |
|---|---|---|
| MITOS-ATYPIA-14 (mitosis en mama) | 0.025 a 0.050, paso 0.005 | 0.035 a 0.045 según fold |
| CRCHistoPhenotypes | 0.1 a 0.4, paso 0.05 | (por validación) |
| TUPAC (mitosis en mama) | 0.02 a 0.07, paso 0.01 | 0.05 |
| NuCLS (multi-clase) | 0.2 a 0.4 para π₁ | (por validación) |

En mitosis el prior vive en **0.02 a 0.05**, o sea entre el 2 % y el 5 % de las cajas candidatas.
Hay un análisis de sensibilidad en el Apéndice B que habría que leer antes de fijar el rango si
esto alguna vez se implementa.

**Para multi-clase** no hacen grid sobre todos los priors (no escala). Fijan `π₁` para la clase
con más anotaciones y derivan las otras **en tiempo de entrenamiento**, batch a batch, con
`π_m = π₁ · N_m/N₁`, donde `N_m` es cuántas células de clase `m` detecta el modelo actual. Es
razonable y es también el punto más frágil del método: los priors dependen del propio detector
mientras se entrena.

## 5. La implementación que ellos usaron

- **Faster R-CNN con VGG16**, pre-entrenado en ImageNet. También probaron ResNet50 y ResNet101
  (§3.2.3) y el método aguanta el cambio de backbone.
- Asignación de anclas: IoU máximo **> 0.7 es positivo**, **< 0.3 es no-etiquetado**, y entre 0.3
  y 0.7 **se descarta**.
- Adam, lr 1e-3, batch 8, 2580 iteraciones, se queda con el último modelo.
- En MITOS-ATYPIA-14: imágenes de ~1539×1376 recortadas a parches de **500×500 con 100 px de
  solape**; en test se predice por parche y se fusiona con NMS.

## 6. Qué reportan, y cómo hay que leerlo

MITOS-ATYPIA-14, 5-fold, anotación incompleta simulada por **borrado aleatorio** (§3.2.1):

| Método | Recall | Precisión | F1 |
|---|---|---|---|
| Baseline (trata lo no marcado como negativo) | 0.570 ± 0.075 | 0.403 ± 0.040 | 0.470 ± 0.045 |
| BDE (Li et al. 2020, el competidor) | 0.598 ± 0.077 | 0.427 ± 0.039 | 0.496 ± 0.044 |
| **Propuesto** | **0.608 ± 0.079** | **0.439 ± 0.038** | **0.507 ± 0.044** |
| *Upper bound* (anotación completa) | 0.613 ± 0.074 | 0.461 ± 0.049 | 0.523 ± 0.048 |

**Corrección de encuadre respecto de la ficha del 2-ago.** Ahí se leyó "+0.011 de F1 sobre un
baseline" y se concluyó que el paper convence por el planteo más que por la magnitud. La segunda
mitad sigue siendo cierta, pero el +0.011 es contra **BDE**, que es el competidor especializado.
Contra el baseline, que es **lo que haríamos nosotros si entrenáramos de la forma normal**, la
diferencia es **+0.037**. Y con el *upper bound* a la vista la lectura cambia de forma: el hueco
que abre la anotación incompleta es 0.523 − 0.470 = **0.053**, y el método recupera **0.037 de
esos 0.053, o sea el 70 %**. En recall recupera casi todo: 0.608 contra un techo de 0.613.

Es consistente en los 5 folds y significativo con t-test pareado y corrección
Benjamini-Hochberg (p < 0.01 en F1 contra los dos competidores).

**El detalle que más acota, y no estaba en la ficha:** el régimen de "incompleto" que testean es
suave. Borran anotaciones **hasta dejar una célula marcada por parche de 500×500**, y como los
parches no tienen muchas células, **queda el ~73 % de las anotaciones**. Nuestro caso es mucho más
extremo: 26 marcas en una lámina de 4799 parches. **El paper no evalúa ese régimen**, y no hay
forma de extrapolar la curva desde acá.

También probaron una simulación más realista (quedarse con la célula de **mayor acuerdo entre
patólogos** por parche, §3.2.4), que imita a un anotador que marca lo fácil. Ahí el método
mantiene la ventaja: F1 0.512 contra 0.473 del baseline. Es el escenario que más se parece al
nuestro de los dos, y es buena noticia.

En NuCLS (multi-clase, mama) el patrón se repite y aparece un dato interesante: para la clase
**stromal**, el método propuesto (F1 0.350) queda **por encima del upper bound en recall** (0.436
contra 0.412), lo que sugiere que en clases difusas la anotación "completa" tampoco es completa.

## 7. El código: existe, pero lo que sirve son cinco líneas

`clam_testing2/PUcell_reference/`, clonado y leído.

**Lo que está.** Es un fork del Faster R-CNN de `jwyang` (el de 2018). La loss PU vive en
**una sola línea**, `lib/model/faster_rcnn/faster_rcnn.py:121`:

```python
RCNN_loss_cls = 0.04*F.cross_entropy(cls_score1, rois_label1) + max(0, (
    (w1*F.cross_entropy(cls_score2, rois_label2)) +
    (w2*F.cross_entropy(cls_score1, rois_label01)) -
    (0.04*F.cross_entropy(cls_score1, rois_label01))))
```

Se reconoce la ec. 7 término a término: el `max(0, ...)` es la corrección no-negativa, y el
`0.04` es `π`.

**Lo que no está, y hay que decirlo.**

- **`π` está hardcodeado en 0.04**, con un `#pi=0.04` de comentario al lado. La búsqueda por
  validación del §2.3 no está implementada.
- **Es solo el caso binario** (`cls_score.view(-1,2)`). La extensión multi-clase, que es la
  contribución de la versión MELBA sobre la de MICCAI, no aparece en el repo.
- **El entorno es de 2018 y no corre acá.** El README pide **PyTorch 0.4.0** ("*now it does not
  support 0.4.1 or higher*") y **CUDA 8.0**, con extensiones CUDA que se compilan con `sh
  make.sh`. Nuestra GPU es una **RTX A6000 (sm_86) con CUDA 12.8**: PyTorch 0.4.0 no tiene
  kernels para esa arquitectura. No es un problema de versiones que se arregle con un `pip
  install`, es un backend que hay que reemplazar.

**Conclusión sobre el hueco #3 del handoff.** La pregunta era si hay código porque eso decide el
costo de la familia D. La respuesta honesta es: **hay código, y sirve como referencia exacta de la
loss, pero no como algo que se clone y se corra**. Lo bueno es que el contenido reusable es chico
y está claro: portar `max(0, ...)` al `roi_heads` de la Faster R-CNN de torchvision es un cambio
acotado, y lo que hay que escribir de cero es el andamiaje (dataset, anclas, evaluación), no el
método. El costo baja respecto de "escribir todo desde cero", pero no baja a "clonar y correr".

## 8. Qué nos sirve, y qué no

**Sirve.**

- Es el único de los cuatro papers cuyo **régimen de supervisión es el nuestro**. No lo esquiva,
  lo usa.
- El criterio de **seleccionar por recall y no por precisión** bajo anotación parcial es un
  procedimiento que podemos adoptar aunque nunca implementemos el detector, y coincide con lo
  que ya razonamos por nuestra cuenta el 1-ago.
- **MITOS-ATYPIA-14 está a 0.2455 µm/px**, que es prácticamente TCGA (0.2325). Si el go/no-go del
  paso 1 corre sobre TCGA, la escala calza casi sola.
- Le da forma al pedido al patólogo: marcas por punto, en N láminas, **parciales está bien**.

**No sirve, o hay que aclararlo.**

- **El régimen que testean (73 % de retención) no es el nuestro.** Es la limitación más grande y
  no se puede tapar con el argumento de que "el planteo es correcto".
- La caja de 32×32 px que generan alrededor del punto anotado mide **7.9 µm** a 0.2455 µm/px.
  Nuestras marcas son de 36×36 px a 0.465, o sea **16.7 µm**, más del doble en tamaño físico.
  Las dos son convenciones de anotación, no medidas de la célula, pero si alguna vez se cruzan
  los dos mundos hay que homologarlas y no suponer que "36 px" y "32 px" son lo mismo.
- El backbone es de 2015 y el detector de 2017. El propio paper dice que sería interesante
  integrarlo con detectores modernos y que no lo hicieron.
- **No entrega el conteo en el punto caliente.** Eso lo ponemos nosotros (§2.b del
  [`README.md`](README.md)) y no está en ningún paper de los cuatro.

## 9. Lo que costaría acá, en orden

1. **Paso 1, go/no-go, sin entrenar nada.** Correr un detector de mitosis público sobre unas
   pocas láminas de TCGA y medir contra las 26 marcas de la 129741. Esto **no necesita este
   paper**: necesita pesos públicos de mitosis, que este repo no publica. Ver §11.
2. Si pasa: escribir el andamiaje de detección en `clam_testing2/`, fuera del pipeline MIL.
   Faster R-CNN de torchvision, anclas a 0.7/0.3, dataset a partir del geojson del patólogo (que
   además hay que corregir por el `dx=3829` de [[anotaciones-patologo-qupath]]).
3. Portar la loss (cinco líneas) y la búsqueda de `π` por recall en validación.
4. Recién ahí, el conteo sobre el mejor bloque contiguo de ~141 parches y un clasificador chico
   de `score_1/2/3`.

Nada de esto se implementa sin pre-registro y `reviewer` (regla 9).

## 10. Lo que este estudio no afirma

- Que el método transfiera a nuestro régimen de anotación, que es **mucho** más escaso que el
  que evalúan.
- Que suba nuestra métrica de `grado_mitotic_3clases`. El paper mide F1 de **detección**, no
  puntaje de lámina, y el puente entre las dos cosas lo tenemos que construir nosotros.
- Que el repo sea utilizable. Es referencia de la loss, no software que corra en este servidor.
- Que 0.04 sea el prior correcto para nuestros datos. Es el valor que ellos dejaron fijo en el
  código para un dataset que no es el nuestro.

## 11. Preguntas para llevar a la reunión

1. **¿Hay más láminas anotadas, y quién es «GDT»?** Es lo que decide si la familia D existe. Con
   26 marcas en 1 lámina no se entrena; con varias decenas de láminas, sí, y el paper dice que
   pueden ser parciales.
2. **El paso 1 no depende de este paper.** Necesita pesos públicos de un detector de mitosis
   (MIDOG tiene los datos, CC-BY, y los participantes publicaron modelos). ¿Vale la pena
   gastarlo antes de comprometerse con la familia D entera?
3. **¿Sobre qué cohorte?** MITOS-ATYPIA está a 0.2455 µm/px y MIDOG entre 0.23 y 0.26
   (ver [`midog_notas.md`](midog_notas.md)). TCGA a 0.2325 calza; el privado a 0.465 necesita
   reescalado y es el brazo con riesgo. La lámina anotada es privada, así que la validación
   contra las marcas cae justo en el brazo difícil.
4. Si la respuesta a la 1 es que no hay más anotaciones a la vista, ¿la familia D se archiva o se
   convierte en el pedido formal al patólogo?
