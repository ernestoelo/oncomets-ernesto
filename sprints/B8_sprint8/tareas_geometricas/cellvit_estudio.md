# CellViT: estudio (familia C)

> Hörst F, Rempe M, Heine L, Seibold C, Keyl J, Baldini G, Ugurel S, Siveke J, Grünwald B,
> Egger J, Kleesiek J, *CellViT: Vision Transformers for precise cell segmentation and
> classification*, **Medical Image Analysis 94:103143 (2024)**. arXiv:2306.15350.
> PDF en [`cellvit_horst2024.pdf`](cellvit_horst2024.pdf) (23 pág.).
> Código clonado en `clam_testing2/CellViT_reference/` (HEAD `05097e1`, 23-jul-2025, 130 MB),
> **reference only**: solo lectura, NO al PYTHONPATH, NO import cruzado. **Los pesos no se
> bajaron** (el clon no los trae).
>
> **Bajado el 3-ago-2026.** Ficha: [`papers_mitosis.md`](papers_mitosis.md) §3.
> Contraparte obligatoria: [`../hovernet_estudio.md`](../hovernet_estudio.md), porque CellViT es
> un HoVer-Net con el encoder cambiado y hereda su post-procesamiento.

---

## 1. Qué propone, en una frase

El mismo esquema de HoVer-Net (una red que predice a la vez máscara de núcleo, mapas de distancia
horizontal y vertical, y tipo de núcleo) pero con el encoder CNN reemplazado por un **Vision
Transformer pre-entrenado**, y con parches de inferencia de 1024×1024 en vez de 256.

## 2. Lo que confirma y lo que corrige de la ficha del 2-ago

La ficha se escribió leyendo el texto del preprint por web. Con el PDF completo:

**Confirmado, y ahora con verificación fuerte.**

- **No tiene clase mitótica.** Las clases son las 5 de PanNuke: neoplásica, epitelial,
  inflamatoria, conectiva y muerta. Además, **la palabra "mitosis" (en cualquier flexión) no
  aparece ni una sola vez en las 23 páginas**. No es que la clase esté y rinda mal: el problema
  no está planteado. Para contar mitosis no sirve, y esto ya no hace falta volver a discutirlo.
- **Sigue usando watershed.** El post-procesamiento es el de HoVer-Net: gradiente de los mapas
  de distancia, Sobel, y watershed controlado por marcadores para separar núcleos pegados. Los
  autores lo dicen como "*additional postprocessing steps*" y las tres ramas del decoder
  (NP, HV, NT) son las mismas de HoVer-Net. O sea que **no elimina los 75 minutos de CPU** que el
  [`README.md`](README.md) §3.C identificó como el grueso del costo.

**Se corrige, o al menos se precisa.**

- **El 1.85× es de la variante chica.** Contra HoVer-Net, el speedup es **1.85× para CellViT256**
  (encoder ViT-S) y **1.39× para CellViT-SAM-H**, que es la variante con mejores números. Citar
  "1.85×" a secas mezcla las dos.
- **Y el speedup viene del tamaño del parche de inferencia, no de la arquitectura.** Usar parches
  de 1024 px en vez de 256 acelera **2.49× (CellViT256)** y **2.25× (SAM-H)** al mismo modelo. El
  1.85× contra HoVer-Net es en buena medida ese efecto. Es un dato que reordena la conversación:
  el mismo truco de parche grande podría aplicarse a HoVer-Net.

## 3. Los números en PanNuke

Media de la validación cruzada 3-fold oficial de PanNuke. Detección (agnóstica de clase):

| Modelo | Precisión | Recall | F1 detección |
|---|---|---|---|
| HoVer-Net | 0.82 | 0.79 | 0.80 |
| CellViT256 | 0.83 | 0.82 | 0.82 |
| CellViT-SAM-B | 0.83 | 0.82 | 0.83 |
| **CellViT-SAM-H** | 0.84 | 0.81 | **0.83** |
| CellViT-Random (sin pre-entrenar) | 0.79 | 0.81 | 0.80 |

Panoptic quality media **0.50**, F1 de detección **0.83**, que son los números del abstract.
La mejora sobre HoVer-Net en detección es de **2 a 3 puntos de F1**, y la fila
`CellViT-Random` muestra que buena parte de la ganancia viene del **pre-entrenamiento** del
encoder, no de la arquitectura: sin él, cae al nivel de HoVer-Net.

Por clase, la clase `dead` sigue siendo mala (F1 0.36 a 0.39), igual que la clase *miscelánea* de
HoVer-Net que ya habíamos cerrado.

## 4. El dato nuevo que más nos toca: qué pasa a 0.50 µm/px

El paper publica modelos entrenados sobre **PanNuke reescalado a 0.50 µm/px** (su "×20"), que es
prácticamente la escala de nuestra cohorte privada (**0.465 µm/px** medido en la 129741). Los
números caen fuerte:

| Modelo | Precisión | Recall | F1 detección |
|---|---|---|---|
| CellViT256 @ **0.25 µm/px** | 0.83 | 0.82 | 0.82 |
| CellViT256 @ **0.50 µm/px** | 0.86 | **0.60** | **0.71** |
| CellViT-SAM-H @ **0.25 µm/px** | 0.84 | 0.81 | 0.83 |
| CellViT-SAM-H @ **0.50 µm/px** | 0.88 | **0.63** | **0.73** |

El **recall se desploma unos 19 a 22 puntos** al bajar de aumento, mientras la precisión hasta
sube: el modelo encuentra menos núcleos pero se equivoca menos en los que encuentra. Y la clase
`dead` se derrumba a F1 0.07 a 0.08.

**Consecuencia práctica, y no estaba en la ficha:** a la escala de nuestra cohorte privada,
CellViT queda **por debajo de HoVer-Net a 0.25 µm/px** (F1 0.71 a 0.73 contra 0.80). Cualquier
plan de la familia C sobre el privado tiene que contar con eso, o resolver primero el reescalado.
Sobre TCGA (0.2325 µm/px) el problema no existe.

Es, además, otra confirmación empírica y ajena de nuestra regla de proyecto: la escala física
manda, y el mismo modelo cambia de comportamiento según µm/px ([[cohortes-magnificacion-fisica]]).

## 5. La cuenta que ya estaba, y sigue en pie

Sebastián pausó la familia C por costo (3.3 h por lámina con HoVer-Net) y él mismo propuso
correrla solo sobre los **20 mejores parches que CLAM selecciona**. Puestas al lado:

| Idea | Factor |
|---|---|
| Cambiar HoVer-Net por CellViT256 | 1.85× |
| Cambiar HoVer-Net por CellViT-SAM-H | 1.39× |
| Acotar de 4799 parches a 20 | ~240× |

La elección de modelo es de segundo orden frente a la idea que él ya tenía. Si C se reabre, se
reabre por el subconjunto de parches.

**Un dato de hardware que vale la pena:** el paper dice explícitamente que una **RTX A6000 de
48 GB alcanza** para entrenar las variantes ViT256 y SAM-B. Es exactamente nuestra GPU. No es que
haga falta entrenar (los pesos están publicados), pero cierra la pregunta de si el modelo entra
acá.

## 6. Qué nos sirve, y qué no

**Sirve.**

- Para **grado nuclear** sigue siendo la familia que mejor calza con lo que describió el patólogo:
  una vez segmentado el núcleo, "más grande que su vecindario" es una razón entre áreas, directa
  de calcular e **invariante a la escala**, que es el confundido de §2.c del README.
- Pesos públicos, sin entrenamiento propio.
- Es reemplazo directo de lo que `sgaete` ya tiene corriendo: mismo dataset (PanNuke), misma
  familia de salida, misma forma de post-procesamiento.

**No sirve, o hay que aclararlo.**

- **Para mitosis, no.** Cero menciones en el paper.
- **En el privado rinde mucho peor** por la escala (§4).
- No elimina el post-procesamiento, que es donde está el costo de CPU.
- El riesgo de diseño no está en segmentar, está en **cómo se convierten las instancias de núcleo
  en features por parche y cómo entran al agregador**. Ahí SI-MIL ya nos mostró que se puede
  perder métrica ([[simil-hovernet-decision-31jul]]).

## 7. Lo que este estudio no afirma

- Que CellViT mejore nuestra métrica en ninguna tarea. No se probó en nuestros datos.
- Que sus 5 clases sean suficientes para grado nuclear. La feature que nos interesa es
  geométrica (razón de áreas), no la clase del núcleo, así que en principio alcanza; pero eso no
  está medido por nadie.
- Que reescalar el privado a 0.25 µm/px recupere el rendimiento. Interpolar hacia arriba no
  inventa detalle; el paper no evalúa ese caso.

## 8. Preguntas para llevar

1. Si C se reabre, ¿se reabre por el subconjunto de 20 parches (que es lo que da el 240×) y se
   deja el modelo como decisión posterior?
2. Sobre el privado, ¿cómo se resuelve la caída a 0.50 µm/px? Es la pregunta que decide si C es
   viable fuera de TCGA.
3. ¿Vale la pena mirar **LSP-DETR** (arXiv:2601.03163, ene-2026,
   [`lspdetr_pekar2026.pdf`](lspdetr_pekar2026.pdf), también bajado)? Es el que sí elimina el
   post-procesamiento con polígonos estrella-convexos, pero es preprint y no verificamos si tiene
   pesos públicos.
