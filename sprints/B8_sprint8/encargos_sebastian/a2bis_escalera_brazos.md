# A2.bis — la escalera de brazos: ¿el detector agrega algo sobre la atención sola?

> Medido el **21-ago-2026**, CPU post-hoc, sin GPU. Script:
> [`scripts/escalera_brazos.py`](../../../scripts/escalera_brazos.py).
> Salidas: `results/b8_hovernext_129741/{escalera_brazos,escalera_brazos_gate}/`
> (`escalera_brazos.csv`, `escalera_brazos.png`, `meta.json`).
> Pedido de Ernesto (21-ago), planificado en [`plan.md`](plan.md) §A2.bis.

Hasta acá HoVer-NeXt se leyó **contra sí mismo**. Falta la pregunta anterior: **¿el detector
agrega algo sobre la atención sola?** Para contestarla el brazo de atención pura deja de ser
«el techo» y pasa a ser **la línea base contra la que se lee todo**.

**Una precisión de forma, porque se presta a confusión**: Mammoth **no se suma a CLAM, lo
reemplaza** (es CLAM con la 1ª capa lineal cambiada por el MoE), así que son brazos
**alternativos**. Lo que sí es un brazo nuevo es **combinar las dos máscaras**.

## 1. Por qué hizo falta un eje y no alcanzaba una columna

Comparados por recall a secas, los brazos dicen que HoVer-NeXt **empeora**: 19/26 → 11/26 en
K=300. Eso es un artefacto de mirar una sola columna. El detector baja el recall **y** cambia
la unidad de lo que hay que revisar, y las dos cosas pasan a la vez. Por eso se grafica
**recall contra carga de revisión**, con la carga en **dos unidades, las dos declaradas**:

- **objetos a mirar** — parches en los brazos de atención, **núcleos puntuales** en los que
  llevan HoVer-NeXt;
- **área (mm²)** — la superficie que se le pone delante al patólogo.

**Chequeo de sanidad, y pasa en las dos tareas**: en K = 2496 (la región anotada entera) los
brazos de atención convergen a **26/26**, los que llevan HoVer-NeXt a **13/26**, y el azar
converge al mismo punto que los de atención. Si la escalera no cerrara ahí, el eje estaría mal
construido y nada de abajo se leería.

## 2. La comparación justa: objetos para llegar a cada recall

A **K fijo** la comparación es tramposa (una máscara más grande gana por ser más grande). Lo
que se compara es **cuánta carga pide cada brazo para llegar al mismo recall**. CDIS fold 4,
denominador **26 marcas**:

| llegar a | CLAM | Mammoth | CLAM∩Mammoth | CLAM∪Mammoth | HoVer-NeXt solo |
|---|---|---|---|---|---|
| 8/26 | 71 parches | 70 | **33** | 80 | — |
| 10/26 | 86 | 80 | **48** | 98 | — |
| **13/26** | 130 | 95 | **84** | 126 | **82 núcleos** |
| 16/26 | 217 | 144 | **134** | 155 | imposible |
| 19/26 | 300 | **217** | 241 | 251 | imposible |
| 22/26 | 450 | **300** | 382 | 372 | imposible |
| 26/26 | 2496 | 2496 | 2496 | 2496 | imposible |

Tres cosas que **solo aparecen con este eje**:

1. **La unión nunca es el mejor brazo.** A K fijo `CLAM∪Mammoth` parecía el mejor de todos
   (24/26 en K=300 contra 22 y 19); a **carga fija** queda igual que CLAM y por debajo de
   Mammoth. Su ventaja era **el tamaño de la máscara**, no la calidad del ranking. Es
   exactamente el artefacto que este documento existe para evitar.
2. **La intersección es el brazo más eficiente donde la carga es chica** (hasta ~16/26): pide
   la mitad de parches que cualquiera de los dos solos para el mismo recall. Donde CLAM y
   Mammoth **coinciden**, aciertan.
3. **Mammoth le gana a CLAM en todos los niveles de recall** en esta tarea. No es una
   afirmación de rendimiento del modelo: es sobre **dónde pone la atención**, no sobre cómo
   clasifica.

## 3. La respuesta a la pregunta, con su condición

**Sí, pero solo por debajo de 13/26, y con una advertencia de unidad.**

- **Por debajo de 13/26** los dos caminos piden una carga **comparable en número de objetos**:
  HoVer-NeXt solo pide **82 núcleos**, la intersección **84 parches**, Mammoth **95 parches**.
  Lo que cambia no es cuántos objetos, sino **de qué tamaño**: un parche mide 256 px
  (**119 µm de lado**) y un núcleo es un **punto ya localizado**.
- **Por encima de 13/26 el detector no es una opción a ninguna carga.** Está **topado**: no
  pasa de 13/26 ni con la lámina entera. La atención sola llega a 26/26. Ése es el argumento
  más fuerte a favor de la atención, y no depende de ninguna convención.
- **Combinar los dos nunca sube el recall** por encima de 13/26 (el techo lo pone la
  detección), pero **sí baja los objetos**: `CLAM+HoVer-NeXt` en K=300 pide **48 núcleos** para
  11/26, contra los 82 de HoVer-NeXt solo para 13/26. Cambia **2 marcas por la mitad de los
  objetos**.

## 4. La advertencia que hay que leer antes que el eje de área

**El área de un núcleo es una CONVENCIÓN, no una medida.** Un núcleo es un punto; para darle
área hay que elegirle una ventana de inspección. Se adoptó **128 px** (≈59,5 µm de lado), la
misma de la galería del encargo 2, porque da contexto alrededor de una figura mitótica de
10-20 µm. **La conclusión sobre área depende de esa elección, y bastante:**

| ventana | lado | área de las 82 detecciones | contra CLAM (1,84 mm²) |
|---|---|---|---|
| 64 px | 29,8 µm | 0,073 mm² | 25,3× menos |
| 96 px | 44,6 µm | 0,163 mm² | 11,2× menos |
| **128 px** (adoptada) | 59,5 µm | **0,290 mm²** | **6,3× menos** |
| 192 px | 89,3 µm | 0,654 mm² | 2,8× menos |
| 256 px | 119,0 µm | 1,162 mm² | 1,6× menos |
| 384 px | 178,6 µm | 2,614 mm² | **0,7× — más área, no menos** |

O sea: **el «6,3× menos área» no es un resultado, es una consecuencia de la ventana elegida**,
y el signo se da vuelta antes de los 384 px. **El eje de objetos no tiene ese problema** y es
el que sostiene las conclusiones de §2 y §3. El de área queda como ilustración, con su
convención escrita en la figura.

Es el mismo patrón que P2/P3/P4 vienen marcando en este sprint: frente a un resultado que
sorprende, el primer sospechoso es **la herramienta**, no el mundo. Acá la herramienta era la
unidad del eje.

## 5. El gate de invasivo, con el mismo eje

Corriendo lo mismo sobre `invasion_carcinoma_gate_pth_balance` fold 0 (brazo Mammoth; el CLAM
plano lo entrena **B3**):

| llegar a | gate · Mammoth | CDIS · Mammoth |
|---|---|---|
| 8/26 | 189 parches | 70 |
| 13/26 | 367 | 95 |
| 19/26 | 556 | 217 |
| 22/26 | 639 | 300 |

**El gate pide entre 2,5 y 4 veces más carga para el mismo recall.** Confirma lo de
[`a2_atencion_gate_invasivo.md`](a2_atencion_gate_invasivo.md) §3 en la unidad correcta, y
agrega un dato que no estaba: **en K=100 el gate queda al nivel del azar** (1,0/26 de la
atención contra 1,0/26 esperado por sorteo). En el recorte más chico, la atención del gate **no
aporta información sobre dónde están las mitosis**. En CDIS, al mismo K, CLAM da 12/26 y
Mammoth 14/26 contra el mismo 1,0/26 del azar.

**Lo que esto todavía NO separa** es si eso es propiedad de **la tarea** o del **brazo**: en el
gate solo hay Mammoth. Lo separa **B3**.

## 6. Qué no se afirma

- **No se afirma que HoVer-NeXt «sea mejor» ni «peor» que la atención.** Contestan cosas
  distintas: la atención llega a 26/26 con carga alta, el detector se queda en 13/26 con carga
  baja y objetos ya localizados.
- **No se afirma nada sobre área sin la convención al lado** (§4).
- **No se calcula precisión** contra el geojson y **nada se llama falso positivo**: las marcas
  del patólogo son **positivos parciales** y lo no marcado no es negativo.
- El denominador son **las marcadas** (26), no las mitosis que hay en la lámina.
- **No es una comparación CLAM-vs-Mammoth de rendimiento** (Hallazgo 12 sigue cerrado): es
  sobre **dónde ponen la atención** en una lámina, no sobre cómo clasifican.
- **Una lámina, 26 marcas, un checkpoint por brazo.** Sin sd entre checkpoints. Las dos
  incertidumbres del caso están en [[auc-atencion-dos-incertidumbres]]. **B1** es lo que lleva
  el denominador a 94.
- Las cifras de «objetos para llegar a R» son **interpoladas** entre los K del barrido
  (20, 50, 100, 189, 300, 500, 750, 1000, 1392, 2000, 2496), no medidas en cada valor.
