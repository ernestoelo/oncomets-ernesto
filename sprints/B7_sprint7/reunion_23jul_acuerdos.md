# Reunión con Sebastián — 23-jul-2026 (14:30). Acuerdos y encargos

Reunión pedida por él tras el envío de los heatmaps CLAM vs Mammoth y la respuesta a
Q1 (cuántos expertos/slots). Salió bien: **le gustó el trabajo** y pidió incorporar
los resultados nuevos (tablas resumidas de la softmax por slot + mapas de calor por
slot) a la presentación del **24-jul**.

---

## 1. Corrección pedida a los mapas de calor (bloqueante para el deck)

Sebastián detectó que los tres PNG generados el 23-jul **no muestran los cuatro
primeros puestos del ranking**. La causa es nuestra: `pick_diverse_slots`
(`scripts/slot_heatmaps_contraste.py`) elegía slots **espacialmente diversos** dentro
del top-20 para que el contraste visual se viera, y eso **saltea puestos** (en tipo
mostró #1, #2, #4, #13).

**Lo que él quiere ver es justamente lo que esa selección escondía:** en CDIS el
ranking tiene **e28·s4 en el puesto #1 y e28·s5 en el #4** — el **mismo experto 28**
con **dos slots distintos**. La pregunta que quiere responder es:

> ¿los slots de un mismo experto están viendo cosas distintas, o se parecen entre sí?

**Encargo:** regenerar los 3 mapas de calor con **el top-4 puro del ranking**, aunque
se repita el experto. Sin selección por diversidad.

> **Por qué importa (y por qué el pedido es el correcto):** es exactamente lo que
> muestra la Fig. 3 del paper Mammoth, que rotula por **par experto+slot** porque el
> mismo experto tiene slots de morfología distinta (`e16·s1` alvéolos vs `e16·s4`
> estroma). Nuestra selección diversa impedía observar ese caso en nuestras láminas.
> Ver [[slot-unidad-de-morfologia]].

## 2. Entregable para el deck del 24-jul

Una lámina que contenga **las 3 imágenes de mapas de calor (una por tarea) con su
respectiva tabla resumen al lado**. Las tablas son las mini por lámina
(`sprints/B7_sprint7/slot_softmax/heatmaps/slot_mini_<tarea>.csv`), que calzan 1:1 con
los slots dibujados.

## 3. Cómo presentar la entropía (pedido explícito)

Ernesto le dijo que no termina de entender la entropía. Acuerdo:

- **Explicar la idea general**, no la derivación: *a mayor reparto equitativo, mayor
  entropía*.
- **Argumentarlo de forma consistente con el número** que se reporta (que la idea
  general y el 158.7 no queden desconectados).
- **Entregar el número efectivo de slots por tarea POR SEPARADO** — cada tarea es
  distinta y promediar las tres esconde eso.
- **Mencionar el efecto del tamaño de la lámina** (WSI grandes vs chicas): el número
  efectivo sigue al nº de parches, no a la tarea.

## 4. Análisis nuevo pedido: la cota de la softmax

Interpretar **cuál sería una cota conveniente sobre la softmax** para decidir qué
slots ya **no aportan prácticamente nada**, y con eso dar una idea general de
**cuántos slots requiere aproximadamente cada tarea**. Ese resultado va también al
deck.

Insumos que ya existen para responderlo (`slot_softmax_resumen.csv`): `slots_sobre_uniforme`
(103/82/98 de 300), `slots_para_50pct` y `slots_para_90pct`, y `peso_min_pct`
(0.011–0.022 %, contra 0.333 % del reparto uniforme). La sesión del 23-jul ya midió que
**el corte es arbitrario** si se elige a mano (25 a 300 slots según el umbral), que es
justo el argumento para elegir la cota con criterio y no a ojo.

## 5. Qué explicar en el deck sobre los mapas de calor

- **Qué representa el porcentaje de la softmax** que se pinta en el mapa de calor
  (`combine`: de cada parche, qué fracción se reparte a ese slot).
- **Qué es el 15 %**: el recorte visual (se pintan solo los parches del top-15 % de ese
  slot, el resto queda transparente para que se vea el tejido). No es un parámetro del
  modelo.

---

## 6. Eje de trabajo siguiente: «perillar» el fine-tuning de Mammoth

**Contexto que aportó Sebastián:** los autores del paper usaron el modelo principalmente
sobre **tipo histológico** (y otras tareas que Ernesto no recuerda), y sobre **otros
cánceres, como pulmón**. O sea la configuración por defecto (E=30, S=10) **no está
afinada para nuestro contexto** (cáncer de mama, nuestras tres tareas). Hay que
afinarla.

**Diseño pedido:** reducir la capacidad **manteniendo uno de los dos parámetros fijo**,
comparando configuraciones de **igual número total de slots**, sobre las **mismas tres
tareas** (CDIS, LVI, tipo histológico). El primer par:

| Brazo | Expertos (E) | Slots por experto (S) | Total E·S |
|---|---|---|---|
| baseline | 30 | 10 | 300 |
| A | **27** | 10 | 270 |
| B | 30 | **9** | 270 |

…y así ir reduciendo en paralelo. La comparación A vs B a igual total aísla **dónde**
conviene recortar (en E o en S).

**Evidencia propia que motiva el eje** (no es una corazonada): Q1 midió expertos
**30.0/30** (reparto uniforme, techo teórico) y slots **158.7/300** → el margen de
recorte está en **S**, no en E. La expectativa honesta es que el brazo B (recortar S)
tolere mejor la reducción que el A (recortar E). Ver [[mammoth-slot-routing-weight]].

> **Gobernanza:** esto toca la configuración del modelo → **regla 9** (hipótesis +
> métrica + dirección pre-registradas) y **reviewer** antes de commitear. Comparación
> **paired** reusando los splits del job 4589 ([[patron-paired-comparison-reuso-splits]]).
> Reportar balanced_acc **y** AUC juntos (política eval B5).

---

## 7. Estado al cierre de la sesión

Hecho el 23-jul (tarde): tablas de la softmax por slot (`slot_softmax/`), mapas de calor
por slot, y la anatomía del desacuerdo CLAM/Mammoth (§3.1 de `resultados_interpretabilidad.md`).

Pendiente y **delegado a una sesión limpia**: los puntos **1, 2, 3, 4 y 5** de este
documento (regenerar los mapas + armar la lámina + los textos del deck). El eje del
punto **6** es trabajo de entrenamiento posterior a la presentación.
