# Q1 escalada: cuántos slots usa Mammoth, con n grande

Encargo 1 de la reunión del 24-jul-2026. Método y validación del tooling:
[`metodologia.md`](metodologia.md). Verdad de campo: `results/b8_q1_slots_escalado/`.

Medido el 27-jul-2026 sobre **1858 láminas-fold** (1176 láminas únicas), o sea todas las
de test de los 5 folds de las 3 tareas del job 4589, contra las **7** del Sprint 7.

## Respuesta corta

| | n=7 (B7) | **n=1858 (B8)** |
|---|---|---|
| **Slots efectivos** (de 300) | 158.7 ± 34.6 | **159.5 ± 26.3** |
| **Expertos efectivos** (de 30) | 30.0 | **29.98** |
| Rango de slots | 89.7 a 196.4 | 65 a 228 |
| Slots sobre la cota 1/300 | 63 a 96 | 43 a 113 (media 81.6) |
| Masa que concentran | 73 % | 71 % |

**El número aguanta el escalado.** La media pasa de 158.7 a **159.5**, dentro de un
cuarto de desviación estándar. La objeción de Benjamín era correcta como método (con n=7
el número describía y no establecía), y el resultado sobrevivió a la prueba: ahora sí es
el número de la tarea y no una descripción de 7 láminas.

## 1. Slots: 159.5 de 300

Mediana 161.8, IQR 141.8 a 178.2, desviación estándar 26.3. El rango se ensancha respecto
del B7 (65 a 228 contra 89.7 a 196.4), que es lo esperable al pasar de 7 a 1858
mediciones: aparecen las colas.

Las tres medidas independientes vuelven a converger en «~160 de 300», igual que en el B7:

| Medida | B7 (n=7) | B8 (n=1858) |
|---|---|---|
| Número efectivo `exp(H)` | 158.7 | **159.5** |
| Slots para el 90 % del peso | 164.4 | **168.9** |
| Slots para el 50 % del peso | 38.7 | **38.1** |

La distribución sigue siendo **sesgada**: 38 slots llevan la mitad del peso y hacen falta
169 para el 90 %. `N_eff = 159.5` no significa «159 slots trabajando por partes iguales».

Por tarea:

| Tarea | n | Slots efectivos | Sobre la cota | Parches (media) |
|---|---|---|---|---|
| `tipo_histologico_3clases_ci` | 1013 | **165.5 ± 24.9** | 84.3 | 8724 |
| `carcinoma_ductal_insitu_presente_ci_reform` | 429 | **158.3 ± 28.0** | 80.8 | 9790 |
| `invasion_linfatica_vascular_ci_reform` | 416 | **146.2 ± 22.7** | 75.9 | 10214 |

## 2. Expertos: confirmado, y pegados al techo

**29.98 de 30** de media, con mínimo 29.925 y máximo 29.999 sobre las 1858. Más
contundente todavía: `e50 = 15` y `e90 = 27`, los valores exactos del reparto uniforme
sobre 30, salen **idénticos en las 1858 láminas**, sin una sola excepción.

Un cuarto ángulo, independiente de los tres anteriores: los expertos que superan el peso
uniforme 1/30 son **14.96 de media** (rango 8 a 20), o sea la mitad justa de los 30, que es
lo que da una distribución simétrica y plana. Si algún experto dominara, esa cuenta se
desplomaría.

Como `N_eff = n` se alcanza **sólo** en el reparto uniforme (máximo de la entropía), esto
es reparto uniforme, no «muchos expertos usados». **E=30 no está sobredimensionado**, y el
margen de recorte de capacidad está en **S**, tal como decía el B7. Eso se sostiene ahora
con tres órdenes de magnitud más de datos y de forma transversal a las 3 tareas y a las 3
cohortes.

## 3. La dispersión: hay que corregir lo que decía el B7

El B7 concluyó que **la dispersión de slots sigue al TAMAÑO de la lámina y no a la tarea**
(Spearman ρ=0.750, p=0.052, n=7), con la salvedad explícita de que con n=7 describía y no
establecía, porque la correlación se apoyaba en una sola lámina chica. **Con n grande esa
conclusión no se sostiene.**

| Variable | Varianza explicada | Detalle |
|---|---|---|
| **Tarea** | **0.086** (eta²) | Kruskal-Wallis H=177.2, p=3.4e-39 |
| **Tamaño de lámina** | **0.020** (ρ²) | ρ=+0.141, p=9.9e-10 |
| Cohorte | 0.018 (eta²) | H=30.5, p=2.4e-07 |

Dos lecturas, y las dos importan:

1. **El orden se invierte.** La tarea explica unas **4 veces más** varianza que el tamaño,
   cuando el B7 decía lo contrario. La correlación con el tamaño sigue siendo positiva y
   ahora es estadísticamente significativa (el n la vuelve detectable), pero **cae de
   ρ=0.750 a ρ=0.141**: era un artefacto del n chico. Dentro de cada tarea va de ρ=0.093
   (CDIS) a ρ=0.248 (tipo), y dentro de la cohorte privada es ρ=0.011 (p=0.88), o sea nula.
2. **Pero ninguna de las tres explica gran cosa.** Sumadas no llegan al 12 % de la
   varianza. La dispersión de slots efectivos es sobre todo **variabilidad entre láminas**
   que no captura ni la tarea, ni el tamaño, ni la cohorte. La desviación estándar sigue
   siendo de 26.3 slots sobre una media de 159.5.

La formulación honesta para presentar es: *el número de slots efectivos está alrededor de
160 en las tres tareas, con diferencias entre tareas chicas pero reales (146 a 166), y una
dispersión entre láminas que no se explica por el tamaño de la lámina como creíamos con
n=7.*

## 4. Cohortes

El B7 midió sólo TCGA, porque necesitaba el `.svs` para los overlays. El barrido cubre las
tres:

| Cohorte | n | Slots efectivos |
|---|---|---|
| TCGA | 981 | 162.2 ± 24.7 |
| privado | 189 | 162.7 ± 27.6 |
| HistAI | 688 | 154.9 ± 27.6 |

**La cohorte casi no mueve la aguja** (eta² 0.018), y en particular las láminas privadas de
Environ dan **162.7**, indistinguible de TCGA. Eso responde de paso, para esta medición, la
lectura más plausible del encargo 2 («verlos sobre nuestras láminas privadas»): el número
no cambia por mirar la cohorte propia. No cierra el encargo 2, que sigue esperando que
Sebastián aclare qué pidió, pero saca del medio la hipótesis de que TCGA estuviera dando
un número no representativo.

## 5. Qué se puede afirmar ahora, y qué no

**Sí:**

- El número de slots efectivos de la tarea es **~160 de 300**, medido sobre 1858
  láminas-fold de las 3 tareas y las 3 cohortes.
- **E=30 no está sobredimensionado**: reparto uniforme exacto, sin excepciones.
- **El margen de recorte de capacidad está en S**, no en E. Es el insumo directo del
  encargo 3 (grid de E y S).

**No:**

- Que la dispersión siga al tamaño de la lámina. Eso **queda desmentido** como explicación
  principal (ρ² = 0.020).
- Que la diferencia entre tareas sea grande. Es real y muy significativa, pero explica el
  8.6 % de la varianza: no alcanza para pedir un S distinto por tarea sobre esta evidencia
  sola.
- Que recortar S a ~160 no cueste rendimiento. Esta medición dice cuánta capacidad se usa,
  **no** qué pasa si se saca. Eso lo tiene que medir el grid del encargo 3.
