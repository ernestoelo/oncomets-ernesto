# Tareas que dependen de geometría: mitosis y grado nuclear

> Abierto el 31-jul-2026 por encargo de Sebastián, después de la reunión donde se descartó
> implementar SI-MIL. Registro de la reunión:
> [`../reunion_31jul_redireccion.md`](../reunion_31jul_redireccion.md).
> **Esto no es un pre-registro.** Es el argumento y el mapa de opciones que la regla 9 exige
> *antes* de proponer código. El pre-registro de cada rama va aparte, con `reviewer`.

## 1. El encargo

Investigar modelos o variantes que salgan de CLAM como **rama aparte**, dedicados por
completo a una tarea concreta, para tareas que dependen de una geometría particular:
**mitosis** y **grado nuclear**. La motivación no es teórica: viene de mirar una lámina con
el patólogo. Sus dos observaciones, en sus términos:

- en mitosis, los núcleos son muy particulares y aparecen dispersos en zonas distintas de la
  lámina, y son detalles tan finos que a CLAM y a Mammoth se les escapan, porque son parches
  que quizá no reciben atención suficiente y otros embeddings se los comen;
- en grado nuclear, lo que se ve es que hay **núcleos más grandes de lo normal comparados con
  su vecindario**.

Las dos observaciones son afirmaciones sobre **geometría y escala**, no sobre capacidad del
modelo. Eso es lo que las hace atacables.

## 2. Por qué el pipeline actual está mal calibrado para estas dos tareas

Cuatro medidas, todas verificadas en esta sesión sobre la lámina 129741 y los CSV del
pipeline. No son estimaciones de orden de magnitud.

### 2.a La marca del patólogo ocupa el 1.5 % de un parche

Una mitosis marcada mide **36 × 36 px = 16.7 µm**; un núcleo de alto grado, lo mismo. Un
parche nuestro es de 256 px. En área, la marca es el **1.54 %** del parche
([`../anotaciones_patologo/hallazgos.md`](../anotaciones_patologo/hallazgos.md) §1). Ese
parche entero se comprime a **un vector de 512 dimensiones** de CONCH, y ese vector es todo
lo que el agregador llega a ver. La frase del patólogo sobre que otros embeddings se los
comen tiene una versión medible: el objeto diagnóstico es **1/65 del contenido** del vector
que lo representa, y compite dentro de él con estroma, linfocitos y tejido normal.

Es la misma forma del problema que ya cerramos por otro lado: el cuello no es el agregador
(Hallazgos 11 a 14, cuatro ángulos y ninguna mejora), sino **qué entra al agregador**.

### 2.b La regla clínica no es un promedio, es un máximo local

El recuento mitótico de Nottingham se hace en el **punto caliente**: se cuentan las mitosis
en 10 campos de gran aumento, unos 2 mm², eligiendo la zona más activa de la lámina. Con
0.465 µm/px, un parche de 256 px cubre 119 × 119 µm = **0.0142 mm²**. Entonces:

| Cantidad | Valor |
|---|---|
| Parche de 256 px en la cohorte privada | 0.0142 mm² |
| Los 2 mm² del recuento clínico | **≈ 141 parches contiguos** |
| Tejido total de la lámina 129741 (4799 parches) | ≈ 68 mm² |
| Fracción de la lámina donde se decide el puntaje | **≈ 2.9 %** |

CLAM promedia con pesos de atención sobre las 4799. La regla clínica toma el **mejor bloque
contiguo de 141**. Son operadores distintos, y la diferencia no se arregla ajustando
hiperparámetros: se arregla cambiando el operador. Ahí hay una rama con argumento clínico
explícito, que es lo que la regla 9 pide.

### 2.c El grado nuclear es una comparación relativa, y la escala física no es la misma entre cohortes

Lo que describió el patólogo, núcleos más grandes que su vecindario, es exactamente cómo se
puntúa el pleomorfismo: no por el tamaño absoluto en abstracto sino **contra el núcleo
epitelial normal de al lado**. Dos consecuencias opuestas:

- A favor: una razón entre tamaños es **invariante a la escala**, así que una feature
  construida así sobrevive a que las cohortes estén a magnificaciones distintas.
- En contra: el modelo actual no ve razones, ve píxeles. Y la escala física **no** es la
  misma: privado ≈ **0.465 µm/px** (medido en esta lámina, `objective-power = 20`) contra
  TCGA ≈ 0.2325 ([[cohortes-magnificacion-fisica]]). El mismo núcleo de 8 µm ocupa ~17 px en
  una cohorte y ~34 px en la otra, y nada en la entrada le dice al modelo en cuál está. Para
  una tarea definida por tamaño, eso es un confundido de primer orden, no un detalle.

### 2.d La cohorte privada está escaneada a 20×, y la mitosis se cuenta a 40×

Medido: `openslide.objective-power = 20`, `mpp = 0.465`. El reconocimiento de una figura
mitótica se apoya en la textura de la cromatina condensada, y clínicamente se hace a 40×.
Puede que le estemos pidiendo al modelo a 20× lo que el patólogo hace a 40×. No está
demostrado que sea el cuello, pero es una hipótesis barata de testear y hay que tenerla
sobre la mesa antes de culpar a la arquitectura.

### 2.e Dónde está hoy la métrica, y cuánto queda del camino barato

De la calibración Tier 0 (`sprints/B6_sprint6/tier0_calibracion/resultados.md`), 5 folds:

| | AUC test | bal_acc argmax | bal_acc calibrado | oracle (cota) |
|---|---|---|---|---|
| `grado_mitotic_3clases` | 0.721 ± 0.036 | 0.484 ± 0.053 | **0.531 ± 0.026** | 0.571 |

La lectura importa: re-umbralizar ya capturó casi todo lo que había (0.531 de un techo de
0.571). **El camino del punto de operación está gastado en esta tarea.** Lo que quede por
ganar tiene que venir de una representación mejor, que es justamente lo que Sebastián pidió
investigar. El AUC de 0.721 marca el ranking que hoy sobrevive.

Distribución de clases, para no diseñar en el aire:

| Tarea | privado | privado + TCGA + HistAI |
|---|---|---|
| `tasa_mitotica` | score_1 51, score_2 51, score_3 29, no_ident 22 | 636 / 287 / 254, no_ident 693 |
| `pleomorfismo_nuclear` | score_3 80, score_2 52, score_1 5, no_ident 16 | 768 / 471 / 62, no_ident 569 |
| `cdis_grado_nuclear` | alto 39, intermedio 23, bajo 3, no_ident 25 | 297 / 217 / 42, no_ident 254 |

`pleomorfismo score_1` tiene **5 láminas** en privado y 62 en el conjunto grande, y
`cdis_grado_nuclear bajo` tiene 3 y 42. Cualquier rama nueva se evalúa con balanced_acc y
AUC juntos, con la matriz y el n por clase (regla de eval del B5), y con la minoritaria a la
vista.

## 3. Las cuatro familias de respuesta, ordenadas por costo

Cada una ataca una de las medidas de arriba. No son excluyentes.

> **Búsqueda bibliográfica hecha el 2-ago-2026:**
> [`papers_mitosis.md`](papers_mitosis.md) ficha un paper por cada una de B, C y D (la A quedó
> descartada por el §4 de acá), los compara con **supervisión y costo** como ejes, y recomienda
> **D primero**. Ese documento es el que se lleva a la reunión.

### A. Cambiar el operador de agregación (barata, sin datos nuevos)

Reemplazar el promedio ponderado por atención por algo que se parezca a la regla clínica:
top-k sobre parches, o mejor, **máximo sobre bloques contiguos** del tamaño del campo de
recuento (~141 parches en privado, y el número correcto en cada cohorte según su µm/px, no
según su nivel). Encaja en `scripts/train_dsmil.py` como un `--model_type` nuevo siguiendo
la receta de `@mil-model-integration`, se compara pareado contra CLAM reusando el mismo
`--split_dir` ([[patron-paired-comparison-reuso-splits]]) y no toca `clam_environ`.

Es la única de las cuatro que se puede pre-registrar y lanzar sin depender de nadie.

### B. Cambiar el campo de visión (media, la infraestructura ya está)

Extraer, solo para estas tareas, parches parametrizados en **µm/px físicos** en vez de por
`level`. El eje de magnificación del B6 ya dejó el pipeline armado y sin lanzar
([[magnificacion-cpathagent-proxima-direccion]], `scripts/extract_multiscale_features.py`).
Lo que cambia hoy es que hay un argumento clínico específico para gastarlo acá (§2.c y §2.d)
en vez de como mejora genérica.

### C. Cambiar la unidad de representación: del parche al núcleo (cara hoy)

Es lo que hacen HoVer-Net y las 246 features de SI-MIL, y es lo que Sebastián descartó **por
ahora** por costo: 3.3 h por lámina medidas por él mismo. Queda registrado que la idea que él
mismo propuso, correrlo solo sobre los **20 mejores parches que CLAM selecciona**, es la que
vuelve el costo manejable, y que espera a que haya más GPU.

Dos cosas para cuando se retome, que conviene dejar escritas ahora:

- Para **grado nuclear** esta familia es la que mejor calza con la observación del patólogo,
  porque una vez segmentado el núcleo, «más grande que su vecindario» es una razón entre
  áreas, directa de calcular y **invariante a la magnificación**, que es el confundido de
  §2.c.
- Para **mitosis** no sirve el checkpoint que hay corriendo: PanNuke y CoNSeP meten mitótico
  y necrótico en la clase *miscelánea*, la peor del paper (F 0.426 y 0.178). Ya está cerrado
  en `../hovernet_estudio.md` y no hay que reabrirlo por entusiasmo.
- El costo de 3.3 h no es intrínseco a segmentar núcleos: **75 de esos 216 minutos son
  post-procesamiento en CPU** (el watershed por marcadores), no la red. Hay familias más
  nuevas de segmentación de núcleos que evitan ese paso o lo hacen mucho más barato. **No
  las afirmo con números**: no tenemos los papers acá y no se descarga nada (workaround E).
  Si esta familia se reabre, el primer paso es que Ernesto suba los PDF y se los fiche como
  se hizo con HoVer-Net y SI-MIL.
  > **ADDENDUM 2-ago-2026: los números ya están, en
  > [`papers_mitosis.md`](papers_mitosis.md) §3.** «Mucho más barato» = **CellViT**, 1.85×
  > sobre HoVer-Net, publicado y con pesos, pero **sigue usando watershed** y **no tiene clase
  > mitótica**. «Evitan ese paso» = **LSP-DETR** (arXiv:2601.03163, ene-2026), polígonos
  > estrella-convexos sin post-procesamiento, >5× sobre el siguiente más rápido, todavía
  > preprint. Y la cuenta que reordena la familia: cambiar de modelo rinde 1.85×, mientras que
  > acotar a los **20 mejores parches de CLAM** (la idea del propio Sebastián) rinde ~240×. El
  > paper es de segundo orden frente al subconjunto de parches.

### D. Un detector dedicado, entrenado con anotaciones de objeto (la que necesita al patólogo)

Es la respuesta canónica para mitosis en la literatura, y la que el material del patólogo
empieza a habilitar: sus marcas de 36 px **son** anotaciones de objeto. Con 26 en una lámina
no se entrena nada; con varias decenas de láminas, sí. Esto convierte «pedirle más
anotaciones al patólogo» de un favor difuso en un pedido con forma: qué clases, cuántas
láminas, y sabiendo que las marcas son parciales
([`../anotaciones_patologo/hallazgos.md`](../anotaciones_patologo/hallazgos.md) §3).

## 4. El primer experimento, que es barato y no depende de nadie

> **EJECUTADO el 1-ago-2026. Resultado: gana H_alternativa.**
> Los parches marcados **sí** rankean alto (AUC de ranking **0.890 ± 0.039** para mitosis en
> los 4 checkpoints que nunca vieron la lámina; percentil mediano 91), y sobreviven al nulo
> por traslación rígida (p = 0.0021–0.0023, ninguna de ~440 traslaciones lo alcanza). Y el
> dato que reordena el mapa: **3 de esos 4 checkpoints clasifican mal la lámina** (dicen
> `score_2`, es `score_3`) *mientras* su atención está sobre las mitosis. El modelo mira bien
> y responde mal. Consecuencia para el §3: **la familia A pierde su motivación principal**
> (la frase del patólogo queda refutada acá) pero **conserva la del §2.b**, que este
> experimento no evalúa; **B y C se fortalecen**. Para grado nuclear el efecto es más débil
> y no aguanta el nulo espacial (1 de 4 checkpoints bajo p = 0.05).
> Detalle, matices y lo que NO se afirma: [`../atencion_vs_patologo/resultados.md`](../atencion_vs_patologo/resultados.md).
> Pre-registro previo a correr: [`../atencion_vs_patologo/prereg.md`](../atencion_vs_patologo/prereg.md).
>
> El gotcha del checkpoint se resolvió sin la disyuntiva que planteaba el cuadro de abajo: la
> corrida 5-fold de Sebastián tiene 129741 en `val` en los folds 0 y 2 y en `train` en 1, 3 y
> 4, así que el contraste visto/no-visto quedó **dentro de una misma corrida** (haber visto la
> lámina suma ~0.056 de AUC, y el efecto no depende de eso).

**Pregunta:** ¿nuestros modelos ya entrenados miran donde mira el patólogo?

Se puede responder hoy, en CPU, sin GPU y sin reentrenar:

- **Insumos que ya existen:** los 28 parches de mitosis y 13 de núcleo de alto grado de la
  lámina 129741 (`../anotaciones_patologo/parches_anotados_129741.csv`), sus features en
  `features/h5_files/129741.h5`, y checkpoints entrenados de mitosis.
- **⚠ Elegir bien el checkpoint, porque las dos familias no coinciden** (verificado 31-jul):

  | Familia | Split | Dónde cae 129741 |
  |---|---|---|
  | Nuestro k-fold, el que usó Tier 0 (`results/pathpt_etapa1/mitotic/`, tarea `grado_mitotic_3clases`, 3 clases) | `data/splits_kfold/grado_mitotic_3clases_pth_100` | **`train` en los 5 folds** |
  | De Sebastián (`environ/results_modelo*/grado_histologico_mitotic_rate*`, 4 clases con `no_identificado`) | `environ/splits/grado_histologico_mitotic_rate{,_combined}_100` | **`val`** (single-split) |

  O sea que el checkpoint con el baseline que citamos en §2.e es justamente el que **vio esta
  lámina en entrenamiento**. Las salidas: usar los checkpoints de Sebastián, donde está en
  `val` (a costa de que la tarea tiene 4 clases y otro baseline), o reportar con los de Tier 0
  dejando explícito que es una lámina de train, que **debilita** la conclusión pero no la
  anula si la pregunta es de ranking relativo de atención dentro de la lámina. Decidirlo
  antes de correr, no después de ver el número.
- **Medida:** el percentil de atención de los parches anotados entre los 4799 de la lámina.
  Con CLAM la atención se toma como `softmax(A_raw, dim=1)`, porque `forward` devuelve la
  atención **pre-softmax** (CLAUDE.md, hechos validados), y CLAM_MB tiene una cabeza por
  clase, así que se reporta por clase.
- **Hipótesis primaria** (la del patólogo): los parches marcados **no** rankean mejor que el
  azar, es decir la atención no se concentra donde está la evidencia.
- **Alternativa:** rankean alto, y entonces el problema no es que el modelo no los mire sino
  que el vector del parche no conserva el detalle, lo que empuja hacia las familias B y C en
  vez de la A.
- **Qué NO se va a afirmar:** una lámina y 28 parches describen, no establecen. Y un parche
  no marcado con atención alta no cuenta como error, porque la anotación es parcial.

Es el experimento que convierte la intuición del patólogo en un número, y sale antes de
gastar un fin de semana de GPU en cualquiera de las cuatro familias.

## 5. Lo que no se afirma acá

- Que alguna de las cuatro familias vaya a subir la métrica. Ninguna está probada en nuestros
  datos, y el historial del proyecto es de cuatro ejes cerrados sin mejora.
- Que la magnificación sea **el** cuello. Está medida como confundido; que sea la causa
  dominante es hipótesis.
- Que los modelos externos que se mencionan en la familia C sirvan. No están verificados
  contra el paper, que es lo que exige la regla 5.
