# Interpretabilidad comparada de dos agregadores MIL sobre imagen histopatológica

Documento de referencia para la revisión de avance. Reúne el entrenamiento pareado,
la comparación de mapas de atención, el conteo efectivo de expertos y slots, y dos
observaciones de datos que aparecieron durante el trabajo.

---

## 1. Qué se comparó y cómo

Dos agregadores sobre las mismas características de parche (CONCH, 512 dimensiones):

- **Base**: atención con ramas por clase (CLAM_MB).
- **Variante**: la misma arquitectura, con la primera capa lineal del *patch embedding*
  reemplazada por una mezcla de expertos de bajo rango (30 expertos, 10 slots cada uno,
  16 cabezas en paralelo).

Tres tareas clínicas, cinco particiones cada una, los dos brazos sobre **exactamente las
mismas particiones**. La comparación es pareada por construcción: el conjunto de prueba de
cada partición se verificó idéntico entre brazos mediante la firma md5 de los
identificadores de lámina, partición por partición. No se asumió, se comprobó.

Treinta ejecuciones completas, sin errores. Ambos brazos corrieron 52 épocas por partición
bajo el mismo criterio de parada temprana.

| Tarea | Láminas | Distribución de clases |
|---|---|---|
| Tipo histológico (3 clases) | 2027 | 1610 / 240 / 177 |
| Carcinoma ductal in situ presente | 862 | 730 sí / 132 no |
| Invasión linfovascular | 836 | 470 ausente / 366 presente |

---

## 2. Rendimiento: se reportan exactitud balanceada y AUC juntos

| Tarea | Exactitud balanceada base | Exactitud balanceada variante | Diferencia pareada | AUC base | AUC variante | Diferencia pareada |
|---|---|---|---|---|---|---|
| Tipo histológico | 0.665 ± 0.056 | 0.655 ± 0.047 | −0.010 ± 0.017 (1 de 5 a favor) | 0.833 ± 0.043 | 0.821 ± 0.056 | −0.012 ± 0.025 (3 de 5) |
| Invasión linfovascular | 0.657 ± 0.040 | 0.634 ± 0.050 | −0.023 ± 0.086 (2 de 5) | 0.720 ± 0.032 | 0.684 ± 0.056 | −0.036 ± 0.073 (2 de 5) |
| Carcinoma ductal in situ | 0.668 ± 0.098 | **0.742 ± 0.099** | **+0.074 ± 0.033 (5 de 5)** | 0.765 ± 0.111 | **0.825 ± 0.086** | **+0.060 ± 0.042 (5 de 5)** |

### Recall por clase, sumando las cinco particiones

| Tarea | Clase | n | Recall base | Recall variante |
|---|---|---|---|---|
| Tipo histológico | Carcinoma invasivo de tipo no especial | 802 | 0.817 | 0.839 |
| Tipo histológico | Carcinoma lobulillar invasivo | 121 | 0.744 | 0.769 |
| Tipo histológico | Otros | 90 | 0.433 | 0.356 |
| Ductal in situ | No | 65 | 0.477 | 0.569 |
| Ductal in situ | Sí | 364 | 0.860 | 0.915 |
| Invasión linfovascular | Ausente | 235 | 0.723 | 0.694 |
| Invasión linfovascular | Presente | 181 | 0.591 | 0.575 |

En tipo histológico y en invasión linfovascular la diferencia queda dentro del ruido: la
desviación estándar iguala o supera la magnitud de la media. Es lo que se había anticipado
por escrito antes de correr el experimento.

### El caso del ductal in situ

Es la única de las tres donde la variante mide mejor de forma consistente. Lo que sostiene
la observación:

- Las cinco particiones son positivas en exactitud balanceada y también en AUC.
- **Suben los dos recalls a la vez** (0.477 a 0.569 y 0.860 a 0.915). Eso descarta la firma
  típica de haber corrido el umbral de decisión, que sube una clase y hunde la otra.
- El AUC sube en las cinco particiones, es decir mejoró el ordenamiento, no el punto de
  operación.
- La pérdida de validación de la variante es menor en cuatro de las cinco particiones, y
  ese es el criterio de selección del modelo guardado. No es un efecto del conjunto de prueba.

Lo que obliga a frenar antes de llamarlo mejora:

- **La muestra es chica**: 65 negativos en total, cerca de 13 por partición. Cada negativo
  vale unos 7.7 puntos de recall de esa clase. En números absolutos son 6 negativos y 20
  positivos más acertados sobre 429.
- Esta formulación de la tarea es nueva y no formó parte de las doce configuraciones
  anteriores con las que se evaluó esta variante. No contradice aquellos resultados, abre
  terreno distinto.
- **Invierte el patrón observado hasta ahora**, según el cual el efecto lo gobernaba el
  balance de clases. Acá gana la tarea más desbalanceada (85/15) y retrocede la balanceada.

Conclusión propuesta: candidato a réplica con más semillas o más particiones antes de
presentarlo como mejora. No se cambia la lectura general del eje de rendimiento.

---

## 3. Entregable central: dónde mira cada modelo

Siete láminas, una por clase y tarea, todas del conjunto de prueba de la primera partición
(no vistas en entrenamiento) y **bien clasificadas por los dos brazos**, para comparar el
foco sin el ruido de un error.

La comparación es directa porque la variante hereda el mismo método de atención de la base,
así que los dos mapas salen del mismo código.

| Lámina | Tarea | Clase | Parches | Correlación de rangos | Solapamiento del 5% superior | Entropía base | Entropía variante |
|---|---|---|---|---|---|---|---|
| TCGA-AO-A12D | Tipo | Invasivo no especial | 7097 | 0.848 | 0.079 | 0.873 | 0.929 |
| TCGA-AC-A8OS | Tipo | Lobulillar invasivo | 4201 | 0.885 | 0.243 | 0.760 | 0.830 |
| TCGA-E9-A1NE | Tipo | Otros | 5592 | 0.669 | 0.315 | 0.341 | 0.675 |
| TCGA-A7-A4SB | Ductal in situ | No | 2793 | 0.921 | 0.261 | 0.887 | 0.938 |
| TCGA-D8-A1XB | Ductal in situ | Sí | 16442 | 0.847 | 0.202 | 0.642 | 0.927 |
| TCGA-D8-A1XW | Linfovascular | Ausente | 22206 | 0.796 | 0.101 | 0.985 | 0.975 |
| TCGA-D8-A1X5 | Linfovascular | Presente | 28170 | 0.668 | 0.008 | 0.978 | 0.986 |

**Agregado sobre las siete**: correlación de rangos 0.805 (entre 0.668 y 0.921), solapamiento
del 5% superior 0.172, solapamiento del 1% superior 0.073, entropía 0.781 en la base contra
0.894 en la variante, con la variante más difusa en seis de las siete.

### Lectura

1. **Coinciden en el mapa grueso.** La correlación de rangos alta dice que ambos ordenan el
   tejido de forma parecida. La región que importa es la misma.
2. **Difieren en los picos.** El solapamiento del 5% superior es bajo y el del 1% es casi
   nulo. Mismo barrio, distintas casas: los parches concretos que cada uno pone arriba son
   en su mayoría distintos.
3. **La variante reparte la atención, la base la concentra.** El contraste más fuerte
   aparece en la lámina positiva de ductal in situ y en la clase "otros" de tipo
   histológico, justo donde la base más se concentra.

Que la mayor difusión aparezca en la tarea donde la variante también mide mejor es
sugerente, pero con siete láminas no se puede atribuir la diferencia de métrica a la forma
de la atención. Queda como hipótesis, no como explicación.

---

## 4. Cuántos expertos y cuántos slots se usan de verdad

La pregunta se responde sobre el **peso de combinación**, la segunda distribución softmax
sobre los 300 slots (30 expertos por 10 slots cada uno). No es el conteo de parches más
atendidos por experto, que es otra medida.

La medida usada es el **número efectivo**, la exponencial de la entropía de la distribución
de pesos. Vale 300 si el ruteo fuera perfectamente uniforme y 1 si colapsara en un solo
slot. Se elige porque la softmax da peso positivo a todos los slots, así que contar "los que
reciben algo" siempre daría el total.

Resultados sobre las siete láminas (detalle por lámina en `respuesta_q1_expertos_slots.md`):

| Parches | Slots efectivos | Expertos efectivos |
|---|---|---|
| 2 793 | 89.7 | 30.0 |
| 4 201 | 156.0 | 30.0 |
| 5 592 | 147.5 | 30.0 |
| 7 097 | 178.3 | 30.0 |
| 16 442 | 180.3 | 30.0 |
| 22 206 | 196.4 | 30.0 |
| 28 170 | 162.4 | 30.0 |

**Los expertos se usan por igual.** El número efectivo da 30.0 de 30 en las siete láminas,
y hacen falta 15 expertos para juntar la mitad del peso y 27 para juntar el 90%, que es
exactamente lo que daría un reparto uniforme. El resultado es idéntico en las tres tareas,
así que el número de expertos no está sobredimensionado: el modelo los ocupa todos.

**El margen de recorte está en los slots.** El promedio es 158.7 de 300, es decir que cerca
de la mitad del presupuesto de slots aporta poco. La dispersión entre láminas (de 89.7 a
196.4) no responde a la tarea sino al **tamaño de la lámina**: las dos láminas de ductal in
situ cubren casi todo ese rango por sí solas (89.7, el mínimo, y 180.3, la segunda más
alta), y el orden sigue al número de parches (correlación de
rangos 0.75, al borde de la significancia con siete láminas). Descontando la lámina más
chica, que tiene la mitad de parches que la siguiente, el rango se cierra en 170.2 ± 18.1.
La lectura razonable es que una lámina con pocos parches ofrece menos morfología distinta
que rutear, no que el ruteo cambie con la pregunta clínica.

> Con siete láminas esto describe el comportamiento observado, no lo establece. La
> correlación con el tamaño se apoya en un solo caso de lámina chica.

---

## 5. Sobre los nombres de los tejidos

Cuando se describe qué morfología recoge cada experto, esos nombres son **lectura visual
propia, no anotación**. No existe etiqueta de tejido por parche, solo la etiqueta clínica de
la lámina completa. La validación por parte de un patólogo sigue pendiente.

El argumento que sí se sostiene sin esa validación es que el ruteo es **independiente de la
etiqueta**: el mismo experto responde al mismo patrón en láminas de clases distintas. Eso es
verificable con los datos que hay.

---

## 6. Dos observaciones de datos

### 6.1 El tamaño del parche no se puede deducir de la magnificación

La herramienta previa infería el tamaño del parche desde la magnificación declarada y
forzaba un valor por defecto. Sobre estas siete láminas devolvía 512 píxeles cuando la
geometría real de las coordenadas guardadas es 448 en todas. Cada parche se dibujaba con un
14% de exceso.

Además, una de las láminas es genuinamente de 20 aumentos (0.4992 µm/px, con los tres
campos de metadatos concordantes) y la función la habría tratado como de 40.

La corrección es derivar el tamaño del paso más frecuente entre coordenadas contiguas. Las
coordenadas no mienten. Ya está implementada y expuesta como parámetro, de forma aditiva,
sin alterar la reproducibilidad del trabajo anterior.

### 6.2 La cohorte pública no es homogénea en magnificación

Muestreo de 200 de las 864 láminas públicas de estas tres tareas, leído directamente del
archivo:

| Magnificación nativa | Láminas | Campo físico de un parche de 448 px |
|---|---|---|
| Cerca de 40 aumentos (0.233 a 0.253 µm/px) | 189 (94.5%) | 104 a 113 µm |
| **Cerca de 20 aumentos (0.499 µm/px)** | **7 (3.5%)** | **224 µm, el doble** |
| Cerca de 61 aumentos (0.164 µm/px) | 3 (1.5%) | 74 µm |
| Sin metadato de escala | 1 (0.5%) | no determinable |

Extrapolado, cerca de 30 láminas reciben el doble de campo físico por parche y cerca de 13
reciben dos tercios. La consecuencia práctica es que la diferencia de escala no vive solo
entre cohortes distintas, también **dentro de la misma cohorte**, porque la extracción se
parametriza en píxeles y no en micrómetros por píxel. Es minoritario y acotado, pero es
exactamente el modo de falla que conviene cerrar antes de cualquier trabajo multiescala.

---

## 7. Qué queda abierto

1. **Réplica del resultado de ductal in situ** con más semillas o particiones, antes de
   contarlo como mejora.
2. **Validación de un patólogo** sobre los nombres de morfología asignados a los expertos.
3. **Parametrizar la extracción en micrómetros por píxel** en lugar de píxeles a nivel cero,
   para eliminar la diferencia de escala dentro y entre cohortes.
4. **Recorte del presupuesto de slots**, si el conteo efectivo se confirma sobre las siete
   láminas.

---

## 8. Cómo reproducir

```bash
PY=/home/sdonoso/miniconda3/envs/clam_latest/bin/python

# selección de láminas (prefiere cohortes con escala confiable)
$PY scripts/select_interp_slides.py --fold 0 --per-class 1

# comparación de atención entre los dos brazos (CPU)
CUDA_VISIBLE_DEVICES="" $PY scripts/clam_vs_mammoth_attention.py

# ruteo por experto y slot (CPU, tamaño de parche real de las coordenadas)
bash scripts/run_b7_expert_interp.sh

# conteo efectivo de expertos y slots
$PY scripts/answer_q1_expertos_slots.py

# tabla por tarea
$PY scripts/build_interp_task_table.py
```

Todo el análisis de interpretabilidad corre en CPU, después del entrenamiento, sobre
modelos ya congelados. No toca el modelo ni el entrenamiento.
