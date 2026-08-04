# Resultados del grid E×S de Mammoth sobre CDIS `_ci_reform` (job 4774)

> Escrito el 4-ago-2026, con el job cerrado y los 40 runs completos.
> Lectura según [`prereg.md`](prereg.md) §6, escrito antes de correr y **no modificado**.
> Encargo 3 del B8 ([`../objetivos_sprint8.md`](../objetivos_sprint8.md) §3), formalización del
> pedido de Sebastián del 23-jul.

## Respuesta corta

**Gana H_nula.** A igual capacidad total, recortar slots y recortar expertos se toleran
igual: el contraste primario da signo mezclado en los tres peldaños y, peor para
H_primaria, **el signo de la media se invierte entre peldaños** (+0.022, −0.014, −0.002 de
AUC). En los tres la desviación supera a la media. La frase que el grid ponía a prueba, «el
margen de recorte está en S y no en E», **no se sostiene**: la ocupación medida en el encargo
1 describe cómo se reparte el peso, pero no dice qué capacidad hace falta.

Dos resultados secundarios, ambos del lado de que la capacidad sobra:

- **El piso aguanta.** 30×3 tiene 90 slots totales, un 70 % menos de capacidad que el
  control, y pierde 0.039 de AUC con desviación 0.062, que cruza cero.
- **Dentro de la rama S no hay dosis-respuesta.** De 270 a 90 el AUC va 0.792, 0.797, 0.802,
  0.786: un rango de 0.016, más chico que la desviación típica de un solo brazo. El 30×5, que
  cae justo sobre el número efectivo medido (150 contra 159.5), no marca ningún quiebre.

Y una verificación metodológica que salió mejor de lo pedido: **el control reprodujo al job
4589 bit a bit**, checkpoint incluido (§2).

## 1. Qué corrió, y provenance

40 runs, 8 brazos × 5 folds, **0 `Traceback` y 0 `FAILED`**, 40 `[DONE]`.

Las dos líneas que el prereg §9 pide citar del `.out`, que son la prueba de que lo ejecutado
es lo pre-registrado:

```
TASK=carcinoma_ductal_insitu_presente_ci_reform  K=5  brazos=30:10 27:10 30:9 21:10 30:7 15:10 30:5 30:3
commit=b69531c54c93b60ef4446e33c2075926c4f17e55  rama=main
```

Los 8 brazos son los pre-registrados, en el orden pre-registrado. `ARMS` no fue
sobre-escrito por entorno.

- Job **4774**, lanzado el domingo 2-ago 20:10:29, cerrado el martes 4-ago 07:04:08.
- **34 h 54 min de pared** contra las 24.3 h presupuestadas (§7 del prereg).
- Log: `logs/eg_b8_grid_es_4774.out`.

**El exceso de tiempo es contención de GPU y no toca la métrica.** El costo por run arranca en
36-37 min, exactamente el 36.4 estimado, y se dispara a 87 min en la ventana en que entraron
tres jobs ajenos de `capstone` (4778, 4780, 4782), para bajar a ~62 al final:

| brazo | 30×10 | 27×10 | 30×9 | 21×10 | 30×7 | 15×10 | 30×5 | 30×3 |
|---|---|---|---|---|---|---|---|---|
| min/run | 37 | 36-48 | 36 | 35 | 35-73 | 69-84 | 64-87 | 60-67 |

Es el caso que `CLAUDE.md` documenta en «jobs ajenos que alargan el nuestro»: afecta el tiempo
de pared, no el resultado. Con `sacct` deshabilitado (workaround C) el dato se capturó en vivo.

## 2. El control reproduce al 4589, bit a bit

El prereg §5 gastó 5 de los 40 runs en re-correr el Mammoth 30×10 para verificar que la tanda
nueva reproduce la vieja, y fijó como criterio que cayera «dentro de lo que se mueve una
corrida». Cayó bastante mejor que eso:

| fold | AUC grid | AUC 4589 | Δ | bal grid | bal 4589 | Δ |
|---|---:|---:|---:|---:|---:|---:|
| f0 | 0.811 | 0.811 | +0.000 | 0.710 | 0.710 | +0.000 |
| f1 | 0.850 | 0.850 | +0.000 | 0.773 | 0.773 | +0.000 |
| f2 | 0.840 | 0.840 | +0.000 | 0.676 | 0.676 | +0.000 |
| f3 | 0.932 | 0.932 | +0.000 | 0.899 | 0.899 | +0.000 |
| f4 | 0.693 | 0.693 | +0.000 | 0.652 | 0.652 | +0.000 |

No es redondeo. Verificado por `md5sum`: `test_metrics.json`, `test_predictions.csv`,
`metrics.jsonl` y el `s_<f>_checkpoint.pt` de 2.5 MB son **idénticos** a los del 4589 en los
cinco folds. Los runs son nuevos de verdad (mtime del 2-ago, 260 épocas del brazo 30×10
loggeadas en el `.out`, 40 `[DONE]`); el pipeline sencillamente es determinista en esta GPU
con la misma semilla.

**Consecuencia**: el reuso pareado del CLAM del 4589 queda validado por completo, no como
«referencia informativa». Y el `--seed 1` compartido explica por qué: es la misma razón por la
que el control **no** es una réplica independiente del Δ +0.074 del 4589 (prereg §8).

## 3. Tabla completa: AUC y balanced accuracy por brazo y fold

Celda = `AUC / balanced_acc`. Los parámetros salen de `scripts/grid_es_config_check.py`.

| brazo | E | S | E·S | params | f0 | f1 | f2 | f3 | f4 | **AUC medio** | **bal medio** |
|---|---:|---:|---:|---:|---|---|---|---|---|---:|---:|
| **C** control | 30 | 10 | 300 | 630,424 | 0.811/0.710 | 0.850/0.773 | 0.840/0.676 | 0.932/0.899 | 0.693/0.652 | **0.825** | **0.742** |
| **A1** recorta E | 27 | 10 | 270 | 621,480 | 0.796/0.605 | 0.848/0.759 | 0.674/0.536 | 0.920/0.815 | 0.610/0.480 | 0.770 | 0.639 |
| **B1** recorta S | 30 | 9 | 270 | 622,744 | 0.807/0.630 | 0.839/0.700 | 0.771/0.620 | 0.859/0.717 | 0.682/0.627 | 0.792 | 0.659 |
| **A2** recorta E | 21 | 10 | 210 | 605,400 | 0.835/0.766 | 0.851/0.728 | 0.811/0.708 | 0.928/0.895 | 0.633/0.562 | 0.812 | 0.732 |
| **B2** recorta S | 30 | 7 | 210 | 607,384 | 0.795/0.637 | 0.824/0.700 | 0.846/0.750 | 0.882/0.770 | 0.640/0.599 | 0.797 | 0.691 |
| **A3** recorta E | 15 | 10 | 150 | 586,792 | 0.824/0.721 | 0.880/0.707 | 0.728/0.651 | 0.916/0.808 | 0.671/0.582 | 0.804 | 0.694 |
| **B3** recorta S | 30 | 5 | 150 | 592,024 | 0.785/0.696 | 0.834/0.780 | 0.802/0.644 | 0.925/0.748 | 0.664/0.595 | 0.802 | 0.693 |
| **B4** piso | 30 | 3 | 90 | 576,664 | 0.738/0.637 | 0.918/0.784 | 0.803/0.676 | 0.847/0.717 | 0.625/0.581 | 0.786 | 0.679 |

**La varianza inter-fold domina a cualquier efecto del grid.** El f3 va de 0.847 a 0.932 de
AUC y el f4 de 0.610 a 0.693, en los ocho brazos: la distancia entre folds (~0.25) es un orden
de magnitud mayor que la distancia entre brazos (~0.05). Es exactamente la situación para la
que el prereg exigió Δ pareado por fold y no medias sueltas.

## 4. Contraste primario: H_primaria contra H_nula

El estadístico que decide, según prereg §6: `(B recorta S) − (A recorta E)`, pareado por fold,
dentro de cada peldaño de igual E·S. La métrica que manda es el **AUC**, con la balanced
accuracy al lado.

| peldaño | ΔAUC media ± sd | signos | Δbal media ± sd | signos |
|---|---:|:---:|---:|:---:|
| E·S=270: 30×9 − 27×10 | **+0.022 ± 0.063** | `+ - + - +` | +0.020 ± 0.101 | `+ - + - +` |
| E·S=210: 30×7 − 21×10 | **−0.014 ± 0.034** | `- - + - +` | −0.041 ± 0.084 | `- - + - +` |
| E·S=150: 30×5 − 15×10 | **−0.002 ± 0.048** | `- - + + -` | −0.001 ± 0.049 | `- + - - +` |

**Veredicto: H_nula.** H_primaria pedía que el brazo que recorta S quedara por encima del que
recorta E **en los tres pares**, con consistencia de signo. Lo que hay:

1. Se cumple en **1 de 3** peldaños (270). En 210 el orden se invierte y en 150 es un empate
   numérico (−0.002, dos milésimas de AUC).
2. En el único peldaño que sale a favor, la consistencia por fold es **3 de 5**, y el prereg
   dejó escrito que «un Δ grande en un solo par con signo mezclado en el resto no cuenta como
   confirmación».
3. En los tres peldaños **sd > |media|**, que es la definición literal de H_nula del §3.

**No es H_alternativa tampoco**: recortar E no gana con signo consistente, gana en un peldaño y
pierde en otro. Lo que hay es ruido alrededor de cero.

**Las dos métricas no se contradicen**, así que no se activa la cláusula de «par ambiguo» por
discrepancia del §6: AUC y balanced accuracy apuntan en la misma dirección en los tres
peldaños. La ambigüedad es por magnitud frente al ruido, no por desacuerdo entre métricas.

El primer peldaño, 27×10 contra 30×9, es el par que Sebastián pidió textualmente el 23-jul.
Su respuesta: **+0.022 ± 0.063 de AUC a favor de recortar slots, con 3 de 5 folds. No alcanza
para afirmar una dirección.**

## 5. Δ pareado contra el control 30×10

Descriptivo del costo de recortar, no del contraste primario.

| brazo | E·S | ΔAUC media ± sd | signos | Δbal media ± sd | signos |
|---|---:|---:|:---:|---:|:---:|
| 27×10 | 270 | −0.055 ± 0.069 | `- - - - -` | −0.103 ± 0.060 | `- - - - -` |
| 30×9 | 270 | −0.034 ± 0.034 | `- - - - -` | −0.083 ± 0.059 | `- - - - -` |
| 21×10 | 210 | −0.013 ± 0.032 | `+ + - - -` | −0.010 ± 0.059 | `+ - + - -` |
| 30×7 | 210 | −0.028 ± 0.025 | `- - + - -` | −0.051 ± 0.076 | `- - + - -` |
| 15×10 | 150 | −0.022 ± 0.055 | `+ + - - -` | −0.048 ± 0.041 | `+ - - - -` |
| 30×5 | 150 | −0.023 ± 0.012 | `- - - - -` | −0.049 ± 0.061 | `- + - - -` |
| 30×3 | 90 | −0.039 ± 0.062 | `- + - - -` | −0.063 ± 0.077 | `- + 0 - -` |

**Los siete quedan por debajo del control en media, en las dos métricas.** Recortar cuesta
algo. Pero la magnitud es chica (0.013 a 0.055 de AUC) y solo tres brazos tienen 5 de 5 folds
del mismo signo: 27×10, 30×9 y 30×5. El caso más nítido es **30×5, con −0.023 ± 0.012 y 5 de
5**: desviación pequeñísima, o sea una degradación consistente aunque diminuta.

Esto **no** estaba pre-registrado como hipótesis con dirección, así que se reporta como lo que
es, una lectura descriptiva del peldaño, y no como confirmación de nada.

## 6. Dosis-respuesta: la predicción secundaria no se cumple, en ninguno de los dos sentidos

El prereg §3 esperaba que la rama S se sostuviera hasta ~150, donde cae el número efectivo
medido (159.5), y se degradara recién en el piso de 90.

| rama S (E=30) | S=10 | S=9 | S=7 | S=5 | S=3 |
|---|---:|---:|---:|---:|---:|
| E·S | 300 | 270 | 210 | 150 | 90 |
| AUC | 0.825 | 0.792 | 0.797 | 0.802 | 0.786 |
| bal | 0.742 | 0.659 | 0.691 | 0.693 | 0.679 |

| rama E (S=10) | E=30 | E=27 | E=21 | E=15 |
|---|---:|---:|---:|---:|
| E·S | 300 | 270 | 210 | 150 |
| AUC | 0.825 | 0.770 | 0.812 | 0.804 |
| bal | 0.742 | 0.639 | 0.732 | 0.694 |

**Lo observado es un escalón y después una meseta, no una rampa.** La rama S cae de 0.825 a
0.792 en el primer recorte y ahí se queda: entre 270 y 90 el AUC se mueve dentro de 0.016, por
debajo de la desviación de un brazo cualquiera. El piso de 90 no degrada más que el primer
peldaño.

La rama E ni siquiera es monótona: el **peor** brazo de todo el grid es 27×10 (0.770), que es
el recorte **más chico**, y 21×10 (0.812) es el mejor de los siete recortados. Un recorte de
capacidad que mejora al recortar más es la firma de ruido, no de una curva de capacidad.

**Sobre el valor predictivo de la ocupación medida:** 30×5 tiene 150 slots totales, prácticamente
el número efectivo medido en el encargo 1 sobre 1858 láminas-fold, y no marca ningún quiebre.
La métrica de ocupación describe el reparto del peso y no dimensiona la capacidad necesaria.
Es la lectura que el prereg §3 le había asignado por anticipado a H_nula.

## 7. Matrices de confusión y n por clase

Política de eval B5: nunca AUC aislado. `n` de test 85-88 por fold, con **13 negativos
exactos en los cinco folds**, tal como el prereg §5 anticipó. Filas = verdad `[no, si]`,
columnas = predicción `[no, si]`; `no` es la minoritaria.

| brazo | f0 | f1 | f2 | f3 | f4 |
|---|---|---|---|---|---|
| 30×10 | [[6,7],[3,69]] | [[8,5],[5,67]] | [[6,7],[8,65]] | [[12,1],[9,63]] | [[5,8],[6,69]] |
| 27×10 | [[4,9],[7,65]] | [[8,5],[7,65]] | [[2,11],[6,67]] | [[10,3],[10,62]] | [[0,13],[3,72]] |
| 30×9 | [[5,8],[9,63]] | [[7,6],[10,62]] | [[4,9],[5,68]] | [[6,7],[2,70]] | [[4,9],[4,71]] |
| 21×10 | [[8,5],[6,66]] | [[7,6],[6,66]] | [[7,6],[9,64]] | [[11,2],[4,68]] | [[3,10],[8,67]] |
| 30×7 | [[5,8],[8,64]] | [[7,6],[10,62]] | [[9,4],[14,59]] | [[9,4],[11,61]] | [[5,8],[14,61]] |
| 15×10 | [[7,6],[7,65]] | [[7,6],[9,63]] | [[5,8],[6,67]] | [[10,3],[11,61]] | [[3,10],[5,70]] |
| 30×5 | [[6,7],[5,67]] | [[8,5],[4,68]] | [[5,8],[7,66]] | [[7,6],[3,69]] | [[3,10],[3,72]] |
| 30×3 | [[5,8],[8,64]] | [[9,4],[9,63]] | [[6,7],[8,65]] | [[8,5],[13,59]] | [[4,9],[11,64]] |

**Con 13 negativos, cada lámina que cambia de lado mueve la balanced accuracy 0.038.** Es la
razón por la que el prereg puso al AUC como métrica decisiva, y acá se ve el caso extremo: el
27×10 en f4 acierta **0 de 13** negativos, y solo por eso su balanced accuracy cae a 0.480. Un
brazo entero se ve peor de lo que es por el comportamiento de un fold en la clase chica.

## 8. CLAM del 4589 como referencia de escala

Fila de contexto, **sin Δ por brazo** (prereg §6): calcular ocho Δ contra CLAM serían ocho
disparos al eje cerrado del Hallazgo 12, justo sobre la tarea del dato abierto.

| CLAM (job 4589) | f0 | f1 | f2 | f3 | f4 | media |
|---|---:|---:|---:|---:|---:|---:|
| AUC | 0.794 | 0.829 | 0.737 | 0.877 | 0.590 | 0.765 |
| bal | 0.623 | 0.745 | 0.624 | 0.794 | 0.555 | 0.668 |

Los ocho brazos del grid caen entre 0.770 y 0.825 de AUC medio. Es escala descriptiva y nada
más: **no** se deriva de acá ninguna afirmación de rendimiento.

## 9. Lo que este resultado NO dice

Se sostiene todo el §8 del pre-registro, sin excepciones:

- **No** dice que Mammoth mejore el rendimiento en ninguna configuración. El eje está cerrado
  (Hallazgo 12) y este grid mide capacidad, no rendimiento.
- **No** se extiende a las otras dos tareas ni a otras cohortes. Es **una** tarea, la más
  barata, con 85 % de positivos y 13 negativos por test. La lección del encargo 1 fue que un
  número medido sobre 7 láminas no era el número de la tarea; acá vale igual, un peldaño más
  arriba.
- **No** replica el Δ +0.074 del 4589. El control re-corrió el mismo 30×10 con la misma
  semilla y salió idéntico bit a bit (§2), que es la prueba más fuerte posible de que **no** es
  una réplica independiente. Esa réplica sigue pendiente y necesita semillas o folds nuevos.
- **No** hay un brazo ganador. Ninguno tiene consistencia de signo entre pares y entre folds.
- **No** se afirma que la capacidad se pueda recortar sin costo: los siete recortes quedan por
  debajo del control en media (§5). Lo que se afirma es que **la dirección del recorte no
  importa**, y que el costo es chico frente al ruido.

## 10. Qué se puede afirmar, y qué se lleva a la reunión

1. **La dirección del recorte no está determinada por la ocupación.** «El margen está en S y
   no en E» era una extrapolación razonable del encargo 1, y el grid no la sostiene. La
   ocupación describe el reparto, no dimensiona la capacidad.
2. **E=30 y S=10 no están groseramente sobredimensionados para esta tarea, pero tampoco son
   necesarios.** Recortar hasta un 70 % de la capacidad cuesta 0.039 de AUC con desviación que
   cruza cero.
3. **El pipeline es determinista bit a bit en esta GPU**, resultado operativo que vale para
   todo el proyecto: cualquier futuro reuso de baselines sobre los mismos splits y semilla es
   válido por construcción, y cualquier réplica que pretenda ser independiente **tiene que
   cambiar la semilla**.
4. Lo que quedaría por hacer si el eje sigue: repetir el peldaño de Sebastián (27×10 contra
   30×9) con semillas nuevas, que es lo único que separaría el +0.022 del ruido, y sobre una
   tarea con más negativos por test.

## Artefactos

- Métricas y checkpoints: `results/b8_grid_es/carcinoma_ductal_insitu_presente_ci_reform/mammoth_e<E>s<S>_f<0..4>_20260802_2010_s1/`
- Pre-registro: [`prereg.md`](prereg.md), no modificado desde el 2-ago
- Lanzador: [`run_b8_grid_es.slurm`](run_b8_grid_es.slurm)
- Preflight de configuración: `scripts/grid_es_config_check.py`
- Log: `logs/eg_b8_grid_es_4774.out`
- Baselines reusados: `results/b7_mammoth_interp/carcinoma_ductal_insitu_presente_ci_reform/` (job 4589)
