# Notas del presentador — `CLAM_Sprint_B4.pdf` (22 slides)

> **Orden final del deck (Ernesto, OnlyOffice, 1-jun-2026):** … → Fase 1 (CLAM
> fusionado) → Fase 2 (CLAM vs DSMIL fusionado) → DSMIL Notación → DSMIL
> Arquitectura → Anexo (CLAM vs DSMIL binarias k=5) → Objetivos propuestos. OJO:
> en el deck real de Ernesto los números absolutos difieren (mencionó "CLAM vs
> DSMIL fusionado = slide 22", "single-split vs MC-CV = slide 23"); este archivo
> usa su propia numeración secuencial de contenido — mapear con el deck real la
> próxima sesión.
>
> Guía de narración para el deck del Sprint B4 que Ernesto tiene en
> `papers/presentations/CLAM_Sprint_B4.pdf` (LOCAL, gitignored).
> Formato B2 (CLAUDE.md → "Speaker notes"): bloques `BLOQUE N — Título`,
> sub-items con `-> `, fórmulas inline sin LaTeX, sin emojis, destacados en
> línea propia (`Punto clave:` / `Detalle crítico:`). Ultra-minimalista para
> pegar en el panel de notas de OnlyOffice.
>
> **Todos los números provienen de la verdad de campo** (`objetivo_*/resultados.md`,
> `objetivo_5_fusion_binaria/resultados.md`, jobs 4098/4099/4109/4170/4171/4172/4179).
> NO inventar; si una métrica falta, está en esos .md.
>
> **Ver al final "Observaciones de revisión"** — 3 cosas del deck que conviene
> arreglar antes de presentar (objetivos de la slide 2, título de la slide 18,
> título de la slide 14).

---

## SLIDE 1 — Portada (logo Environ)

```
BLOQUE 1 — Apertura
-> Presentación del avance del Sprint B4 sobre OncoMets: clasificación de microcalcificaciones en WSI con CLAM.
-> Recorrido: qué nos propusimos, los datos, la configuración, los resultados de las 8 clases, la reformulación a 3 binarias, y el cierre con varianza honesta (MC-CV) + comparación de arquitecturas CLAM vs DSMIL.
Punto clave: el hilo conductor es que el cuello de botella resultó ser DATOS / formulación, no los hiperparámetros ni la arquitectura.
```

---

## SLIDE 2 — Recapitulación de objetivos

> NOTA: ver "Observaciones de revisión" #1. Estos objetivos (TCGA-BRCA /
> CAMELYON16, LongNet) son los del PLAN inicial del sprint; el cuerpo del deck
> trabaja sobre microcalcificaciones y DSMIL. Las notas abajo asumen que dejás
> la slide tal cual y narrás la transición. Si preferís alinear la slide al
> trabajo real, decímelo y reescribo.

```
BLOQUE 1 — Lo que nos propusimos al arrancar
-> Objetivo 1: reproducir CLAM end-to-end y validar el pipeline de atención con heatmaps contra anotaciones de tumor.
-> Objetivo 2: medir empíricamente cuánto pesa el hiperparámetro B (los top-B / bottom-B parches del instance classifier) sobre la instance_loss y las métricas finales.
-> Objetivo 3: evaluar si un módulo post-CONCH (LongNet u otro) aporta sobre el pipeline.

BLOQUE 2 — Cómo evolucionó en la práctica
-> El objetivo 2 (impacto de B) se cumplió tal cual: lo verán en la slide de ablación.
-> El objetivo 1 y la idea de "módulo alternativo" se aterrizaron sobre el caso clínico real que nos tocó: microcalcificaciones. El alternativo que probamos a fondo fue DSMIL (LongNet lo evaluó el equipo y empeoró en general; mammoth sí ganó en otras tasks).
Punto clave: el dato real (microcalcificaciones, fuerte desbalance) reorientó el sprint. El resto del deck es ese recorrido.
```

---

## SLIDE 3 — Sección: Matriz de datos / Splits

```
BLOQUE 1 — Transición
-> Antes de los resultados, de qué datos hablamos y cómo los partimos.
```

---

## SLIDE 4 — Matriz de datos: 8 clases

```
BLOQUE 1 — La estructura de las 8 clases
-> Las 8 clases NO son independientes: son combinaciones de 3 tejidos {carcinoma invasivo, CDIS, tejido no neoplásico} más "no identificado".
-> "no identificado" = la WSI cuyo reporte CAP no menciona microcalcificaciones (no es ausencia confirmada, es no-reportado).

BLOQUE 2 — El problema salta a la vista en la tabla
-> La mayoritaria "no identificado" tiene 2168 / 287 / 282 (train/val/test). Domina todo.
-> Las combinaciones raras tienen 1 sola slide en val y test (carc.inv+CDIS, +tejido, CDIS+tejido).
Detalle crítico: con 1 sola muestra por clase en val/test, las métricas por clase son ruido puro. Esto rompe el régimen de evaluación, como se ve en los resultados.
Punto clave: aplastar un problema multi-etiqueta en clases-combinación fabrica clases ultra-raras. Ese es el germen de todo lo que sigue.
```

---

## SLIDE 5 — Sección: Configuración entrenamiento / Parámetros

```
BLOQUE 1 — Transición
-> Antes de los números, con qué configuración entrenamos. Casi todo son los args bendecidos por Sebastián.
```

---

## SLIDE 6 — Configuración de entrenamiento

```
BLOQUE 1 — Lo que NO es default y por qué
-> model_type clam_mb: CLAM multi-branch, una rama de atención por clase (8). El default es clam_sb (single-branch).
-> embed_dim 512: dimensión de los features CONCH. Es obligatorio; el default 1024 (ResNet legacy) crashearía.
-> inst_loss svm: activa el instance clustering con SmoothTop1SVM sobre los 2·B parches seleccionados. El default es None (sin instance loss).
-> lr 2e-4: el doble del default (1e-4). Elección de Sebastián.
-> early_stopping y weighted_sample activados: el primero corta si val_loss no mejora (patience 20, stop_epoch 50); el segundo sube la probabilidad de muestrear clases minoritarias para pelear el desbalance.

BLOQUE 2 — Lo que se dejó en default (mencionar al pasar)
-> B=8 (es justo el que se ablaciona después), bag_loss ce, drop_out 0.25, weight decay 1e-5, adam, max_epochs 200, seed 1.
Punto clave: el único hiperparámetro que tocamos a propósito para estudiarlo fue B. Todo lo demás queda fijo para que la comparación sea limpia.
```

---

## SLIDE 7 — Sección: Resultados / Métricas de evaluación

```
BLOQUE 1 — Transición
-> Con esa configuración, qué pasó. Arrancamos por las 8 clases.
```

---

## SLIDE 8 — Resultados 8-clases: Baseline + Hiperparámetro B

```
BLOQUE 1 — Qué es balanced accuracy y por qué la usamos acá
-> balanced accuracy = el promedio del recall de CADA clase por separado (acá, las 8). No premia acertar la clase fácil: pesa las 8 por igual.
-> Por qué importa con ESTE dataset: ~89% de las slides son "no identificado". Un modelo que dijera "no identificado" siempre sacaría accuracy cruda ~0.89 sin aprender NADA de las clases clínicas.
-> La accuracy cruda premia ese atajo; la balanced accuracy lo castiga: recall ~0 en las 7 clases minoritarias -> el promedio se desploma.
Punto clave: con desbalance extremo, la accuracy cruda miente; la balanced accuracy es la métrica honesta.

BLOQUE 2 — Qué dice el 0.31 (y por qué bajar a 0.24 mata la hipótesis)
-> Con 8 clases, predecir siempre la mayoritaria da balanced accuracy 1/8 = 0.125 (el piso). El 0.31 está apenas encima: el modelo casi no aprende las clases raras.
-> La ablación de B: comparamos baseline B=8 (job 4098) vs B=16 (job 4099). Si más parches en el instance classifier ayudaran, balanced accuracy debería SUBIR. Bajó: 0.31 -> 0.24.

BLOQUE 3 — Las 3 señales apuntan al mismo lado
-> test_auc subió solo +0.009 (0.812 -> 0.821), bajo el umbral predefinido +0.03 -> irrelevante.
-> balanced accuracy BAJÓ -0.07 (debería subir si B ayudara).
-> train_clustering_loss SUBIÓ 0.0089 -> 0.0126 (debería bajar si el instance classifier mejorara).
-> Hipótesis NO confirmada. B es un hiperparámetro: ajustarlo no mueve la aguja.
Punto clave: el cuello de botella no son los hiperparámetros, es la FORMULACIÓN de la tarea. Esta ablación negativa es la evidencia que justifica reformular.
Detalle crítico: ojo con el test_auc 0.81 — suena bien, pero la balanced accuracy 0.31 revela que el modelo NO decide bien por clase. Por eso nunca reportamos el AUC solo en este régimen (la matriz de la slide siguiente lo muestra).
```

---

## SLIDE 9 — Matriz de confusión (8 clases)

```
BLOQUE 1 — Cómo leer la matriz
-> Filas = clase real, columnas = clase predicha (cl0..cl7, en orden: carc invasivo, c.inv+cdis, c.inv+cdis+tejido, c.inv+tejido, cdis, cdis+tejido, tejido no neopl., no identificado).
-> La diagonal son los aciertos. Lo de fuera de la diagonal, los errores.

BLOQUE 2 — Qué se ve
-> El modelo colapsa hacia la mayoritaria: predice "no identificado" (cl7) casi siempre. De 269 no-identificado reales, acierta 211, pero arrastra ahí gran parte de las demás clases.
-> Las clases raras prácticamente no se aciertan (las filas con total 1 caen fuera de su diagonal).
-> balanced accuracy 0.31: el modelo no decide bien por clase; está dominado por el desbalance.

BLOQUE 3 — Por qué el AUC 0.81 mentía
-> Con 4 de 8 clases teniendo 1 sola muestra en test, el macro-AUC (promedio one-vs-rest) está dominado por ruido.
-> La prueba: val_auc (0.69) salió MENOR que test_auc (0.81). Esa inversión es la firma de un régimen inestable.
Punto clave: el AUC solo, en este régimen, no es una métrica honesta. Por eso reportamos balanced accuracy + matriz de confusión, siempre con el n por clase.
```

---

## SLIDE 10 — Reformulación: de 8 clases a 3 preguntas binarias

```
BLOQUE 1 — La idea
-> En vez de 8 clases-combinación, 3 preguntas binarias independientes: ¿hay micro EN carcinoma invasivo? ¿EN CDIS? ¿EN tejido no neoplásico?
-> Una WSI con micro en varios tejidos dice "sí" en cada binario correspondiente. "no identificado" queda EXCLUIDO de los 3 CSVs.

BLOQUE 2 — De dónde sale cada positivo (columna composición)
-> Cada binario suma las clases-combinación que contienen ese tejido. Carcinoma invasivo: 38 + 11 + 13 + 6 = 68 positivos. CDIS: 89 + 15 + 11 + 6 = 121. Tejido: 161 + 15 + 13 + 6 = 195.
-> El "+6" que aparece en los tres es la triple combinación (carc.inv + CDIS + tejido): esas 6 slides son positivas en los 3 binarios a la vez.

BLOQUE 3 — Honestidad sobre la autoría
-> Esta reformulación NO es hallazgo nuestro: Sebastián ya había des-aplastado las 8 clases en 3 binarios hace tiempo. Nosotros dimos con su CSV y reprodujimos/validamos sus resultados de forma independiente.
Punto clave: nuestro aporte propio fue el DIAGNÓSTICO (el régimen de eval roto + la ablación B negativa) que muestra POR QUÉ la reformulación era necesaria.
```

---

## SLIDE 11 — Resultados 3 binarias

```
BLOQUE 1 — Qué cambió respecto a las 8 clases
-> El régimen de evaluación pasó de "no medible" (clases con n=1) a confiable: ahora hay 7 / 13 / 20 positivos en test.
-> Métricas honestas (balanced accuracy, piso trivial 0.50).

BLOQUE 2 — Lectura por tarea
-> Carcinoma invasivo: balanced acc 0.78, test_auc 0.81. Supera el umbral pre-registrado (>0.60) con holgura. Es la prueba de concepto: la reformulación funciona donde el tejido es más localizable.
-> CDIS: 0.59, y tejido no neoplásico: 0.58. Apenas sobre el piso 0.50. No alcanzan su umbral (>0.65).

BLOQUE 3 — Veredicto y matiz
-> La reformulación es la dirección correcta: arregla la evaluación y vuelve aprendible el caso difícil.
-> Pero CDIS y tejido siguen flojos. El siguiente cuello de botella es DATOS (solo 333 slides identificadas -> sobreajuste), no la formulación.
Detalle crítico: esto es PRELIMINAR — 1 sola semilla, 1 sola partición. Justo esa fragilidad es lo que el resto del deck (Fase 0, MC-CV) viene a medir con honestidad.
```

---

## SLIDE 12 — Propuesta de fases y splits

```
BLOQUE 1 — Por qué un diseño en fases
-> Cada fase responde UNA pregunta, y el orden no es arbitrario.
-> Fase 0: ¿cuánto baila la métrica por suerte del sorteo? (3 binarias separadas, CLAM_MB, 328 slides c/u, k=5 MC-CV). No entrena nada nuevo: repite el baseline muchas veces para medir su varianza.
-> Fase 1: ¿fusionar las 3 binarias en "tiene / no tiene micro" + incluir no_identificado como negativo mejora? (fusionado presencia, CLAM_MB, 2814 slides, k=3).
-> Fase 2: ¿DSMIL le gana a CLAM sobre el fusionado? (mismo fusionado, DSMIL, k=3).
-> Anexo: cierra el cuadro aplicando MC-CV a DSMIL sobre las 3 binarias separadas (mismos splits que Fase 0 -> comparación pareada).

BLOQUE 2 — Sobre los splits (tabla inferior)
-> Fase 0 / Anexo: k=5 por tarea binaria. Los test son chicos (7-20 positivas) -> por eso k=5.
-> Fase 1 / Fase 2: k=3 sobre el fusionado. El test tiene ~32 positivas -> mucho más estable, k=3 basta.
Punto clave: sin Fase 0 no sabríamos si las mejoras de Fase 1/2 son reales o ruido del sorteo. La Fase 0 es la vara con la que medimos todo lo demás.
```

---

## SLIDE 13 — Sección: Fase 0 / Matriz de confusión

```
BLOQUE 1 — Transición
-> Arrancamos por la Fase 0: cuánto baila la métrica del baseline cuando repetimos el sorteo.
```

---

## SLIDE 14 — Varianza (barras MC-CV, Fase 0)

> NOTA: ver Observaciones #3 — el título dice "y matrices de confusión" pero las
> matrices están en la slide 15. Estas notas son para el gráfico de barras.

```
BLOQUE 1 — Qué muestra el gráfico
-> Barra = AUC media de CLAM sobre cada binaria con Monte Carlo CV (k=5). El bigote es la desviación estándar (la incertidumbre).
-> La X roja = el single-split del job 4109 (1 sola partición). El rombo negro = el número de Sebastián (1 sorteo). La línea punteada = piso trivial 0.50.

BLOQUE 2 — La noticia: la incertidumbre, no el promedio
-> Carcinoma invasivo: 0.73 ± 0.17. El bigote es enorme: un fold dio 0.41 (peor que random), otro 0.84.
-> CDIS: 0.65 ± 0.07. Tejido no neoplásico: 0.65 ± 0.02 (el más estable).
-> Patrón: la varianza ESCALA con el nº de positivas en test. Carcinoma tiene solo 7 positivas -> más bailoteo; tejido tiene 20 -> más estable.

BLOQUE 3 — Qué le pasa al "0.808" que reportábamos antes
-> El 0.808 del single-split (4109) en carcinoma era el TOPE de la distribución, no el valor típico. La media honesta es 0.732.
-> La X roja cae arriba del bigote -> el single-split engañaba.
Punto clave: a más positivas en test, métrica más estable. Es la prueba empírica directa de por qué hacía falta repetir el sorteo (MC-CV) en vez de confiar en un solo número.
```

---

## SLIDE 15 — Matrices de confusión por fold (Fig 2a/2b/2c)

```
BLOQUE 1 — Qué leer en cada matriz (bal y r+)
-> Una fila de 5 matrices por tarea (un fold cada una): Fig 2a carcinoma, 2b CDIS, 2c tejido. Sobre cada matriz, dos números: bal = balanced accuracy del fold, r+ = recall positivo del fold.
-> balanced accuracy = (recall+ + recall-)/2: el promedio entre "qué tan bien detecto los SÍ" y "qué tan bien detecto los NO". Piso trivial 0.50.

BLOQUE 2 — Por qué balanced accuracy y no accuracy cruda
-> En estas binarias los negativos mandan (carcinoma: ~7 positivas vs ~25 negativas en test).
-> Un modelo que dijera "no" siempre sacaría accuracy ~0.78 sin atrapar NI UNA micro. Su balanced accuracy sería 0.50 -> queda al desnudo.
Punto clave: bajo desbalance, balanced accuracy es la que distingue "aprendió" de "se rindió a la mayoritaria".

BLOQUE 3 — Por qué importa el recall positivo (es el que pesa clínicamente)
-> recall+ = TP/(TP+FN) = de todas las slides que DE VERDAD tienen micro en ese tejido, cuántas atrapó el modelo. Es la sensibilidad.
-> El error caro en screening es el FALSO NEGATIVO: una microcalcificación que se pasa por alto. recall+ mide exactamente eso.
-> Por eso no basta con descartar bien las sanas (recall- alto): el modelo TIENE que atrapar los positivos (recall+ alto). Un recall+ bajo = deja pasar hallazgos reales.

BLOQUE 4 — Por qué r+ baila entre folds y arrastra a bal
-> Carcinoma (2a) tiene solo ~7 positivas en test: cada positiva que se escapa mueve el recall+ ~0.14. Por eso r+ va de 0.14 a 0.57 y la bal lo sigue (0.53 a 0.75).
-> CDIS (2b): bal 0.49-0.72. Tejido (2c): bal 0.54-0.61, el más plano (más positivas -> más estable).
-> El recall- es alto y estable (sobran negativas): la inestabilidad vive toda en el recall+.
Punto clave: la varianza fold-a-fold que ven en bal viene casi toda del recall+, y el recall+ es inestable porque hay poquísimos positivos. Es la misma razón por la que hizo falta MC-CV.
```

---

## SLIDE 16 — Single-Split vs MC-CV

```
BLOQUE 1 — La comparación clave
-> Tres columnas de número: el single-split nuestro (4109, 1 sorteo), nuestro MC-CV honesto (media ± std), y el número de Sebastián (1 sorteo).
-> Carcinoma: 4109 daba 0.808; honesto 0.732 ± 0.167; Sebastián 0.79.
-> CDIS: 0.678 vs 0.652 ± 0.072 vs 0.69. Tejido: 0.658 vs 0.646 ± 0.025 vs 0.63.

BLOQUE 2 — La conclusión honesta frente a Sebastián
-> En las 3 tareas, el número de Sebastián cae DENTRO de nuestra banda de error.
-> Es decir: NO somos distinguibles de Sebastián. Ni mejores ni peores: paridad estadística.
Punto clave: el "ganamos 0.808 vs 0.79" del single-split era ilusión. Con barras de error, indistinguibles. El aporte real de esta fase fue medir la incertidumbre que un solo número escondía, no ganar una métrica.
```

---

## SLIDE 17 — Fase 1: CLAM x Fusionado (k=3)

```
BLOQUE 1 — Qué es el fusionado
-> Una sola pregunta binaria: ¿la WSI tiene microcalcificaciones en cualquier tejido, sí o no? Con "no identificado" incluido como negativo.
-> 2814 slides, 328 sí / 2486 no (desbalance 7.6:1). Test ~281 slides, ~32 positivas por fold -> régimen estable, k=3.

BLOQUE 2 — Resultados por fold
-> test_auc 0.776 ± 0.021. balanced_acc 0.620 ± 0.010 (std súper chico: los 3 folds cuentan la misma historia).
-> recall+ 0.365 ± 0.053 (detecta ~1 de cada 3 micros). recall- 0.876 ± 0.035 (descarta muy bien las sanas).

BLOQUE 3 — Veredicto
-> balanced_acc 0.620 = PLATEAU: aprende algo pero no llega al umbral clínico 0.65, y tampoco colapsa.
-> El desbalance 7.6:1 lo empuja a decir "no" pese al weighted_sample.
Detalle crítico: la accuracy cruda sería ~0.82 y suena buenísima, PERO solo detecta 36% de los positivos reales. Con este desbalance, decir "no" casi siempre da accuracy alta. Por eso reportamos balanced_acc, no accuracy.
Punto clave: fusionar + incluir no_identificado NO fue bala de plata. El 0.620 es básicamente el promedio de las binarias separadas.
```

---

## SLIDE 18 — Fase 2: CLAM vs DSMIL sobre el fusionado (comparación pareada)

> NOTA: ver Observaciones #2 — el título de esta slide dice "Objetivos
> propuestos" (copiado de la slide 19). DEBERÍA decir algo como "Fase 2: CLAM
> vs DSMIL (fusionado)". Estas notas son para el gráfico de barras comparativo.

```
BLOQUE 1 — Qué compara el gráfico
-> Mismos splits que Fase 1 -> comparación PAREADA: la única variable que cambia es el aggregator (CLAM vs DSMIL). k=3, media ± std.
-> Dos grupos de barras: balanced accuracy y test AUC.

BLOQUE 2 — Qué dicen los números
-> balanced acc: DSMIL 0.661 ± 0.046 vs CLAM 0.620 ± 0.010. Δ pareado +0.040, positivo en los 3 folds.
-> test AUC: DSMIL 0.756 vs CLAM 0.776. Δ pareado -0.020: el AUC RETROCEDE con DSMIL, no acompaña al balanced_acc.

BLOQUE 3 — Veredicto honesto
-> DSMIL recupera más positivos (recall+ 0.49 vs 0.36) pero acepta más falsos positivos (recall- 0.83 vs 0.88): es menos conservador, no necesariamente mejor discriminador.
-> El criterio pre-registrado pedía Δ ≥ +0.03 Y bandas mean±std no solapadas. DSMIL cumple el Δ pero las bandas SE SOLAPAN (CLAM [0.610, 0.630] vs DSMIL [0.615, 0.707]).
Punto clave: veredicto = banda AMBIGUA. No es éxito ni fracaso. NO sobre-vender como "DSMIL supera a CLAM". Con k=3 el std mismo es ruidoso.
Detalle crítico: el anexo (DSMIL en las 3 binarias separadas, job 4179) cerró el cuadro: NULL en carcinoma y tejido, regresión leve consistente en CDIS. La arquitectura sola NO es la palanca a ninguna escala. El cuello sigue siendo datos / contexto espacial / desbalance.
```

---

## SLIDE 19 — DSMIL: Notación y puntos clave

```
BLOQUE 1 — Qué es MIL (Multiple Instance Learning) y por qué acá
-> En patología computacional NO hay etiqueta por parche, solo por slide completa: es aprendizaje débilmente supervisado. MIL es el marco para eso.
-> Punto 1 (MIL binario): una "bolsa" (la WSI = el conjunto de parches) es positiva si contiene AL MENOS una instancia (parche) positiva. Es el supuesto clásico de MIL.
-> Punto 2 (marco general): todo modelo MIL hace dos cosas — una función f que saca embeddings de cada parche, y una función g que los agrega en una predicción de bolsa. En nuestro caso f = CONCH (congelado) y g = el aggregator de DSMIL.

BLOQUE 2 — La idea dual-stream (los dos caminos)
-> Stream 1 (punto 3, instancia crítica): un max-pooling localiza el parche MÁS sospechoso de toda la slide. Ese parche es el "ancla".
-> Stream 2 (puntos 4-6, atención): proyecta cada parche (q_i para medir similitud, v_i para aportar información), pesa cada parche por su parecido al parche crítico (atención anclada U) y hace una suma ponderada -> embedding de bolsa b.
Punto clave: por eso es "dual-stream", el DS de DSMIL — una rama localiza el foco, la otra agrega el contexto alrededor de ese foco.

BLOQUE 3 — La figura de apoyo (el riesgo del max-pooling solo)
-> La figura de abajo muestra instancias positivas, negativas e inciertas. El rótulo "potential risk: missing positive instances" es la clave.
-> Quedarse SOLO con el máximo (un único parche) puede dejar pasar otras instancias positivas. Por eso DSMIL no se queda solo con el máximo: la atención del Stream 2 recupera información de todos los parches relevantes. Las dos ramas se complementan.

BLOQUE 4 — El cierre (puntos 7-8)
-> Punto 7 (score global): se clasifica la bolsa usando la representación agregada b.
-> Punto 8 (fusión final): la predicción combina la evidencia LOCAL (el parche crítico del Stream 1) y la GLOBAL (la bolsa del Stream 2) -> un promedio de ambas.
Punto clave: esta slide es solo la notación, para que la arquitectura de la slide siguiente se lea sin fricción. La idea de fondo: DSMIL ancla todo en el parche más sospechoso y pesa el resto por cercanía a él.
```

---

## SLIDE 20 — DSMIL: Arquitectura (árbol en cascada)

> PNG del diagrama: `figuras/slide_assets/D09_cascada_completo.png`. Ecuaciones
> sueltas D01–D06 por si rearmás cajas; D07 = atención absoluta de CLAM (para
> una comparativa); D08 = loss compuesta.

```
BLOQUE 1 — Cómo leer el árbol (de arriba hacia abajo)
-> RAÍZ: la formulación MIL general c(B) = g(f(x_0), ..., f(x_N)). El bag se obtiene agregando los embeddings de los parches. De acá nacen las dos ramas.
-> STREAM 1 (izquierda): c_m(B) = max_i W_0 h_i. Puntúa cada parche y se queda con el máximo -> el parche crítico h_m. Este nodo guía toda la rama derecha.
-> PROYECCIONES (derecha): q_i = W_q h_i (para medir similitud), v_i = W_v h_i (la información a agregar).

BLOQUE 2 — El corazón: la atención ANCLADA
-> ATENCIÓN ANCLADA: U(h_i,h_m) = softmax(⟨q_i,q_m⟩ / √d_q). Cada parche se pesa por su similitud con el parche crítico h_m, no por su cuenta.
-> BAG EMBEDDING: b = Σ_i U(h_i,h_m) · v_i. La bolsa es la suma de los v_i ponderada por esa atención.
-> FUSIÓN FINAL: c(B) = ½(W_0 h_m + W_b b). Promedia la evidencia local (parche crítico) y la global (bolsa).
Punto clave: la diferencia con CLAM está en UN solo bloque, el pooling. CLAM puntúa cada parche de forma ABSOLUTA (solo mira h_i); DSMIL lo puntúa de forma RELACIONAL (mira la relación h_i <-> h_m, el parche crítico).

BLOQUE 3 — Por qué DSMIL es candidato para microcalcificaciones
-> Una microcalcificación es una señal FOCAL: ocupa menos del 1% de la WSI, concentrada en una región chica.
-> La atención absoluta de CLAM puede DISPERSARSE entre miles de parches parecidos; no hay un mecanismo que diga "este es EL parche, comparen el resto con él".
-> DSMIL fija el parche crítico y colapsa la atención a su alrededor -> estructuralmente más adecuado a una señal focal.
Detalle crítico: es una HIPÓTESIS arquitectónica, no un resultado. El paper de DSMIL nunca la midió en multi-clase desbalanceado — por eso la pusimos a prueba.

BLOQUE 4 — Por qué el cambio es limpio (y honesto para comparar)
-> CLAM y DSMIL comparten el MISMO esqueleto MIL: features CONCH -> proyección -> pooling con atención -> clasificador de bag + rama de instancia.
-> Solo cambia el bloque de pooling. Reemplazar uno por otro aísla limpio la variable "aggregator": misma data, mismos splits, mismas features -> apples-to-apples.
Punto clave: no es "probar otra arquitectura de moda", es aislar UNA variable (cómo se agregan los parches) con todo lo demás fijo. La slide siguiente (Fase 2) muestra si esa atención relacional realmente mueve la aguja sobre el fusionado.
```

---

## SLIDE 21 — Anexo: CLAM vs DSMIL en las 3 binarias (k=5, pareado)

> Ubicada DESPUÉS de la 20 (Arquitectura). Figuras disponibles:
> `figuras/fig3a_anexo_dsmil_vs_clam_binarias_auc.png` +
> `figuras/fig3b_anexo_dsmil_vs_clam_binarias_balacc.png` (barras pareadas) y/o
> `figuras/slide_assets/T09_anexo_resultados.png` (tabla Δ por tarea) y
> `T10_anexo_paired_per_fold.png` (signo por fold; CDIS 5/5 negativo).

```
BLOQUE 1 — Qué cierra esta slide
-> En la Fase 0 (slides 14-16) medimos la varianza de CLAM en las 3 binarias con k=5. Acá hacemos lo MISMO pero con DSMIL, sobre los MISMOS splits -> comparación PAREADA: la única variable que cambia es el aggregator.
-> Antes teníamos un solo número de DSMIL en binarias (job 4137) que daba "fracaso". Pero era single-split: la misma vara que ya demostramos engañosa para CLAM en la Fase 0.
Punto clave: sin barras de error no se puede afirmar "DSMIL falla en binarias". Esta slide aplica MC-CV a DSMIL para juzgarlo con la misma honestidad que aplicamos a CLAM.

BLOQUE 2 — Cómo leer la comparación pareada
-> Comparamos la balanced accuracy de DSMIL contra la de CLAM fold por fold, en las mismas particiones. El Δ pareado = DSMIL − CLAM por fold.
-> Pareado importa: al ser los mismos splits, la varianza del sorteo se cancela y queda solo el efecto del aggregator. Un Δ chico unpaired se ahogaría en el ruido inter-fold; pareado, una señal consistente se vuelve visible.

BLOQUE 3 — Resultado por tarea (Δ balanced accuracy, DSMIL − CLAM)
-> Carcinoma: Δ -0.023 ± 0.071 -> NULL. La ventaja que sugería el 4137 (AUC 0.824) era ruido del sorteo, no una mejora real.
-> Tejido: Δ +0.021 ± 0.051 -> NULL / ambigua (signo mezclado entre folds).
-> CDIS: Δ -0.053 ± 0.026, NEGATIVO en los 5 folds -> regresión leve CONSISTENTE.

BLOQUE 4 — Por qué CDIS es distinto (y qué significa)
-> En carcinoma y tejido los signos están mezclados entre folds -> ruido alrededor de cero -> empate estadístico con CLAM.
-> En CDIS los 5 folds dan Δ negativo: no es azar, DSMIL rinde algo PEOR de forma sistemática. El "fracaso" del 4137 en CDIS sí se sostiene con barras de error.
Punto clave: DSMIL quedó evaluado en TODOS los regímenes con MC-CV. En binarias: empate en 2 de 3, regresión leve en CDIS. Sumado a la banda ambigua del fusionado (slide 18), el veredicto es uno solo: la arquitectura sola NO es la palanca a ninguna escala. El cuello sigue siendo datos / contexto espacial / desbalance.
Detalle crítico: CDIS abre una pregunta morfológica para otra iteración (la atención ABSOLUTA de CLAM puntúa cada parche solo; la RELACIONAL de DSMIL lo ancla al crítico — en lesiones distribuidas por los ductos como el CDIS, eso podría jugar distinto). No es decisión de este sprint.
```

---

## SLIDE 22 — Objetivos propuestos (próximos pasos)

```
BLOQUE 1 — Hacia dónde vamos (aprobado con Sebastián)
-> 1. Probar diferentes niveles de magnificación CONCH según la tarea: algunas necesitan más contexto espacial. Es el Eje A, priorizado (re-extraer features solo para slides de microcalcificaciones).
-> 2. Probar DSMIL en otras tareas donde las métricas están bajas: acá DSMIL salió ambiguo, pero como eje arquitectónico sigue vivo en tareas distintas.
-> 3. Establecer MC-CV con k=5 en otras tareas, para tener siempre métricas comparativas con barra de error (no más single-split).

BLOQUE 2 — El cierre
-> La lección del sprint: medir bien (MC-CV) cambió las conclusiones. Frente a Sebastián estamos en paridad estadística, no por encima.
-> El cuello de botella real no es el hiperparámetro (B) ni la arquitectura (DSMIL): es DATOS, contexto espacial y desbalance. Los próximos ejes atacan justo eso.
Punto clave: el aporte del sprint fue convertir números optimistas sueltos en estimaciones honestas con incertidumbre, y dejar el diagnóstico que apunta a los próximos ejes.
```

---

## Observaciones de revisión (cosas del deck a decidir antes de presentar)

> Las superficializo con evidencia; vos decidís. No toqué el PDF (es tuyo y va
> en OnlyOffice).

1. **Slide 2 — los objetivos no calzan con el cuerpo del deck.** La slide lista
   "TCGA-BRCA y CAMELYON16 + heatmaps vs anotaciones de tumor" (obj 1) y
   "LongNet" (obj 3), pero el deck trabaja sobre **microcalcificaciones** y
   **DSMIL**, y nunca muestra heatmaps vs tumor (el Obj 4 de heatmaps está
   PENDIENTE en `progress/current.md`), ni TCGA/CAMELYON, ni LongNet. Solo el
   objetivo 2 (impacto de B) aparece tal cual (slide 8). Opciones: **(a)**
   dejar la slide como "plan inicial" y narrar la transición (las notas de la
   slide 2 ya lo hacen así), o **(b)** reescribir los 3 objetivos para que
   reflejen el trabajo real del sprint (baseline 8-clases → reformulación →
   varianza/arquitecturas). Recomiendo (b) para que el deck sea autoconsistente.

2. **Slide 18 — título equivocado.** Dice **"Objetivos propuestos"** (igual que
   la 19), pero el contenido es el **gráfico de barras CLAM vs DSMIL (Fase 2)**.
   Es un copy-paste del título de la slide siguiente. Sugerido: **"Fase 2: CLAM
   vs DSMIL (fusionado, k=3)"**.

3. **Slide 14 — título spanning.** Dice **"Varianza y matrices de confusión"**
   pero la slide solo tiene el **gráfico de barras de varianza**; las matrices
   de confusión están en la slide 15. Menor: o le sacás "y matrices de
   confusión" al título de la 14, o le ponés a la 15 un título propio (hoy no
   tiene; hereda el de la 14).

**Números: todos verificados.** Las tablas y gráficos del deck (ablación B,
matriz 8 clases, 3 binarias, Fase 0 MC-CV, Fase 1, Fase 2) coinciden con la
verdad de campo en los `resultados.md` y los jobs. Sin correcciones numéricas.
