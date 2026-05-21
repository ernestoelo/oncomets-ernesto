# Presentación Sprint 4 — contenido de slides

> Contenido paste-ready para `CLAM_Sprint_B4.pptx` (OnlyOffice). Cada slide
> trae TÍTULO, CUERPO y NOTAS DEL PRESENTADOR (para leer en modo espectador).
> Generado el 21 may 2026 a partir de los datos reales del baseline B=8.
> Las cifras salen de `objetivo_1_baseline/resultados.md` — no editar a mano
> sin re-verificar contra los logs.

Orden sugerido: datos → cómo entrenamos → diferencias vs Sebastián →
resultados → matriz de confusión → por qué el dataset grande no ayuda.

---

## Slide 1 — La matriz de datos y los splits

**CUERPO** — dataset `microcalcificaciones_pth`: 3072 slides · 3013 con
features `.pt` · 8 clases · 39–136 452 parches/slide (CONCH 512-dim).
Split filtrado `minpatch16`: train 2436 / val 319 / test 315.

| Clase | train | val | test |
|---|---|---|---|
| en_carcinoma_invasivo | 30 | 4 | 4 |
| en_carcinoma_invasivo-en_cdis | 9 | 1 | 1 |
| en_carcinoma_invasivo-en_cdis-en_tejido_no_neoplasico | 4 | 1 | 1 |
| en_carcinoma_invasivo-en_tejido_no_neoplasico | 11 | 1 | 1 |
| en_cdis | 73 | 8 | 8 |
| en_cdis-en_tejido_no_neoplasico | 13 | 1 | 1 |
| en_tejido_no_neoplasico | 128 | 16 | 17 |
| no_identificado | 2168 | 287 | 282 |

**NOTAS DEL PRESENTADOR:**

> Antes de hablar de modelos, veamos con qué datos trabajamos, porque acá está
> la clave de todo lo que viene. La tarea es microcalcificaciones: 3.072
> slides, 3.013 con features extraídas con CONCH. Son 8 clases — y ojo, no son
> "benigno/maligno", son la ubicación del tejido donde aparece la
> microcalcificación. Miren la tabla: cuatro de las ocho clases tienen una
> sola slide en validación y una sola en test. Y "no identificado" es casi el
> 90% del dataset. Esto no es un error: es la realidad clínica. Pero tiene una
> consecuencia fuerte: el AUC sobre una clase con una sola muestra no
> significa nada estadísticamente. Esto explica el "AUC = nan" del Sprint 3.

---

## Slide 2 — La configuración de entrenamiento ("parámetros bendecidos")

**CUERPO** — "bendecidos" = la configuración que Sebastián sancionó como
canónica, para que los tres (Ernesto, Eduardo, Sebastián) entrenen igual y
los resultados sean comparables.

| Argumento | Valor | Default CLAM | Rol |
|---|---|---|---|
| `--model_type` | clam_mb | clam_sb | multi-branch: una rama de atención por clase |
| `--embed_dim` | 512 | 1024 | dimensión features CONCH — obligatorio |
| `--inst_loss` | svm | None | instance clustering (SmoothTop1SVM) |
| `--lr` | 2e-4 | 1e-4 | learning rate (elección de Sebastián) |
| `--early_stopping` | on | off | corta si val_loss no mejora |
| `--weighted_sample` | on | off | muestreo ponderado — mitiga desbalance |
| `--B` | 8 | 8 | top-B/bottom-B del instance classifier |
| resto (bag_loss, drop_out, reg, opt, seed, max_epochs) | = default | | |

**NOTAS DEL PRESENTADOR:**

> Esta es la configuración exacta con la que entrenamos. Le decimos
> "parámetros bendecidos" — es jerga: una configuración aprobada oficialmente,
> la que Sebastián sancionó como canónica. La idea es que los tres usemos
> exactamente la misma config, para que los resultados sean comparables y no
> andemos "probando por probar", como pidió Benjamín. Quiero destacar una
> cosa: esta config NO es el CLAM de fábrica. Tiene seis desviaciones
> deliberadas del default. Las más importantes: CLAM multi-branch,
> embed_dim 512 porque los features de CONCH son de 512 dimensiones,
> el instance loss con SVM, y weighted_sample para el desbalance. El resto
> quedó en default. Y nosotros las usamos sin modificar nada.

---

## Slide 3 — Qué compartimos y qué difiere respecto a los runs de Sebastián

**CUERPO:**

| Aspecto | Runs de Sebastián (V4) | Nuestro baseline (job 4098) | Estado |
|---|---|---|---|
| Codebase | `clam_environ` | `clam_environ` — read-only, sin modificar | Idéntico |
| Features | CONCH 512-dim | Las mismas `.pt`, sin re-extraer | Idéntico |
| Hiperparámetros | Config bendecida | Config bendecida — verbatim | Idéntico |
| Semilla | seed=1 | seed=1 | Idéntico |
| Split | canónico `microcalcificaciones_pth_100` | canónico menos 2 slides de train (bug topk) | Difiere — acotado |
| Dataset | n=548 (reporte V4) | 3072 slides (`_pth`, post-expansión) | Por confirmar |

**NOTAS DEL PRESENTADOR:**

> La pregunta natural es: ¿es comparable lo nuestro con tus runs de V4? La
> respuesta honesta es: en casi todo sí, y las diferencias están acotadas y
> documentadas. Compartimos codebase, features de CONCH, hiperparámetros
> bendecidos y semilla — no tocamos la configuración. Las diferencias son
> dos. Una: el split — el canónico menos dos slides de train que removimos
> porque hacían crashear el topk; está documentado. Y dos, la importante: el
> tamaño del dataset. V4 reporta 548 slides; nuestra task tiene 3.072, porque
> es el dataset después de procesar las slides públicas adicionales. Por eso
> no asumimos reproducir el 0.55 de V4 — primero hay que confirmar qué
> conjunto exacto usó V4. Esa es la decisión número uno de la reunión.

---

## Slide 4 — Resultados del baseline B=8 (job 4098, completado)

**CUERPO:**

| Métrica | Valor | Lectura |
|---|---|---|
| test_auc | 0.81 | infla — promedio ruidoso sobre 8 clases |
| val_auc | 0.69 | gap val−test = −0.125 (invertido) |
| test_acc | 0.72 | por debajo del trivial (0.89) |
| balanced accuracy | 0.31 | la métrica honesta |

**NOTAS DEL PRESENTADOR:**

> Estos son los resultados finales del baseline B=8 — el job corrió cuatro
> horas. Hay un resultado que parece muy bueno pero les pido leerlo con
> cuidado. El test AUC dio 0.81; parece que superamos el 0.55 de V4. No lo
> presento como victoria, por tres razones. Primera: el AUC de validación es
> 0.69 y el de test 0.81 — el test salió mejor que validación, al revés de lo
> normal. Esa inversión es la señal de que la métrica no es confiable: se
> promedia sobre ocho clases y cuatro tienen una sola muestra en test.
> Segunda: la accuracy de test es 0.72, pero predecir siempre la clase
> mayoritaria acertaría 0.89 — somos peores que la respuesta trivial. Tercera:
> el modelo sigue fallando casi todas las clases minoritarias. La lectura
> honesta: el baseline corre y es reproducible, pero el régimen de evaluación
> de esta task no es confiable. Y eso, más que un fracaso, es el hallazgo
> central que justifica el sprint.

---

## Slide 5 — Matriz de confusión: qué hace realmente el modelo

**CUERPO** — test, 302 slides (fila = verdadera, columna = predicha):

```
verdadera \ predicha   cl0 cl1 cl2 cl3 cl4 cl5 cl6 cl7  total
carc_inv                 1   .   .   .   .   .   1   2     4
carc_inv+cdis            .   .   .   .   .   .   .   1     1
carc_inv+cdis+tejido     .   .   1   .   .   .   .   .     1
carc_inv+tejido          .   .   .   .   .   .   .   1     1
cdis                     .   .   .   1   2   .   1   4     8
cdis+tejido              .   .   .   .   .   .   1   .     1
tejido_no_neo            3   1   .   .   3   1   3   6    17
no_identificado          5   4   1   1  21   .  26 211   269
```

El modelo manda **74,5 % de las predicciones (225/302) a `no_identificado`**.
Balanced accuracy 0.31 vs 0.125 de un clasificador trivial → aprendió una
señal débil, pero está lejos de ser útil.

**NOTAS DEL PRESENTADOR:**

> Esta es la slide que de verdad explica el modelo. La matriz de confusión:
> cada fila es la clase verdadera, cada columna la que predijo el modelo. La
> diagonal serían los aciertos. Miren la última columna: el modelo manda casi
> tres de cada cuatro slides a "no identificado", la clase mayoritaria. Las
> clases minoritarias quedan casi vacías en la diagonal. Por eso digo que el
> AUC de 0.81 engaña: el modelo no aprendió a distinguir las clases raras,
> aprendió a apostar a la mayoritaria. La métrica honesta acá es la balanced
> accuracy, que trata las ocho clases por igual: dio 0.31. Un clasificador al
> azar daría 0.125, así que el modelo aprendió algo — pero 0.31 está muy lejos
> de ser clínicamente útil. La matriz de confusión deja esto a la vista; un
> solo número de AUC lo esconde.

---

## Slide 6 — Por qué el dataset grande no ayuda + propuesta

**CUERPO:**
- El dataset tiene 3072 slides, pero el 89 % es una sola clase
  (`no_identificado`). Las clases raras tienen 6–15 slides — y ese número es
  **fijo**: agregar slides de la clase mayoritaria no enseña las minoritarias.
- `weighted_sample` no crea información: re-muestrea las ~250 slides raras de
  train muchas veces → el modelo las memoriza → sobreajuste (mejor época: 6).
- Las 8 clases = combinaciones de 3 tejidos {carcinoma invasivo, CDIS, tejido
  no neoplásico} + `no_identificado`. Es un problema **multi-label aplastado**
  en clases-combinación → fabrica clases ultra-raras (la triple: 6 slides).
- **Propuesta para la reunión**: reformular como **3 tareas binarias**
  (¿microcalcificación en carcinoma invasivo? ¿en CDIS? ¿en tejido no
  neoplásico?). Cada binario tendría clases evaluables y un AUC con sentido.

**NOTAS DEL PRESENTADOR:**

> Una pregunta natural: si tenemos 3.072 slides, ¿por qué el modelo anda mal?
> Porque un modelo aprende una clase de ejemplos de esa clase. Las clases
> raras tienen entre 6 y 15 slides, y ese número es fijo: agregar miles de
> slides más de "no identificado" no le da al modelo ni una pista nueva sobre
> cómo se ve un CDIS. El muestreo ponderado tampoco crea información: repite
> las mismas pocas slides raras hasta que el modelo las memoriza. Y acá viene
> el hallazgo de fondo: si miran los nombres de las ocho clases, son las
> combinaciones posibles de tres tejidos. O sea, en realidad esto no es un
> problema de ocho clases: son tres preguntas binarias independientes —
> ¿hay microcalcificación en carcinoma invasivo, sí o no? ¿en CDIS? ¿en tejido
> no neoplásico? — que alguien aplastó en ocho categorías combinadas. Y
> aplastarlas es justo lo que fabrica las clases con seis slides. Nuestra
> propuesta para la reunión es reformularlo como tres tareas binarias: cada
> una tendría suficientes ejemplos por clase y un AUC que de verdad signifique
> algo.

---

## Slide 7 — Ablación B=8 vs B=16  [PENDIENTE — job 4099]

> Completar cuando el job `4099` (B=16) termine. Comparar contra B=8:
> Δ test_auc, Δ balanced accuracy, `train_clustering_loss` final, matriz de
> confusión. Comportamiento preliminar observado: idéntico a B=8 (sobreajuste
> en época 6, val AUC plateau ~0.66) → pista temprana de que doblar B no
> cambia la dinámica. Métrica de éxito predefinida (Objetivo 2):
> Δ test_auc ≥ +0.03.
