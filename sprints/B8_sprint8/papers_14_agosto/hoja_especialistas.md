# Hoja 8. Los especialistas que sí mapean el objeto, no solo lo puntúan

> Escrita el **14-ago-2026**, una hora antes de la reunión, a pedido de Ernesto. Continúa la
> numeración de [`hoja_jaroensri.md`](hoja_jaroensri.md) (Hoja 7).
>
> ⚠ **Estado de verificación, actualizado el 14-ago (tarde).** El **§1, HoVer-NeXt, YA ESTÁ
> VERIFICADO contra el PDF**: se leyó entero y el estudio está en
> [`hovernext_estudio.md`](hovernext_estudio.md). Sus seis afirmaciones se sostienen como hechos,
> pero **dos decían algo distinto de lo que esta hoja hacía creer** y quedaron corregidas abajo
> (el F1 0,84 y la balanced accuracy 0,758). **Los §2, §3 y §4 siguen siendo búsqueda web**:
> CellViT++, MIDOG 2025 y los descartados no se abrieron como artículo completo. Para esos vale
> la advertencia de [`busqueda.md`](busqueda.md) §8: citamos lo que dice su ficha, **no
> presentarlos como verificados**.
>
> **Qué NO es.** No es un pre-registro y no propone implementar nada. Regla 9.

---

## 0. El encuadre: la Hoja 7 llenó media casilla

Jaroensri es **la forma del pipeline, publicada**, y por eso sigue siendo la propuesta principal.
Pero sus tres modelos de etapa 1 son **puntuadores de parche**: entra un parche, sale un número.
Lo que Ernesto está pidiendo hoy es lo otro, un especialista **con trasfondo arquitectónico para
rastrear y mapear** el objeto, es decir que devuelva **dónde está cada mitosis y cada núcleo**
dentro del parche, no un puntaje del parche entero.

Son dos familias distintas y conviene decirlo en voz alta antes de mezclar papers:

| | Qué devuelve | Quién | Qué habilita |
|---|---|---|---|
| **Puntuador** de parche | un número por parche | Jaroensri (Hoja 7), Mercan (Hoja 6) | agregar a puntaje de lámina, barato |
| **Mapeador** por objeto | polígono + clase de cada núcleo | los de esta hoja | contar, medir tamaño, comparar contra el vecindario, y **mostrárselo al patólogo** |

El mapeador es el que responde a las dos frases del patólogo: «núcleos particulares y dispersos»
(hay que **localizarlos**) y «núcleos más grandes de lo normal comparados con su vecindario» (hay
que **medirlos y comparar**). Un puntuador no puede hacer ninguna de las dos, solo aprenderlas
implícitamente.

## 1. El candidato principal: HoVer-NeXt (MIDL 2024)

> Baumann E, Dislich B, Rumberger JL, Nagtegaal ID, Rodriguez Martinez M, Zlobec I. *HoVer-NeXt:
> A Fast Nuclei Segmentation and Classification Pipeline for Next Generation Histopathology*.
> **MIDL 2024, PMLR vol. 250.** Acceso abierto. Código y pesos:
> `github.com/digitalpathologybern/hover_next_inference` (GPL-3.0), datos y pesos en Zenodo
> (`10.5281/zenodo.10636591`, `11657620`). Universidad de Berna.

**Tres cosas lo ponen adelante de todo lo que veníamos mirando, y las tres son cosas que ya
habíamos anotado como bloqueos nuestros:**

1. **Tiene clase de mitosis.** Extendieron el dataset Lizard con una clase mitótica y publicaron
   datos de validación aparte para ella. Esto es **exactamente el agujero** que le documentamos a
   CellViT y a HoVer-Net el 2-ago: cero apariciones de «mitos\*» en las 23 páginas de CellViT, y
   las 5 clases de PanNuke no incluyen mitosis ([[papers-rama-mitosis-bcd]]).
2. **Corre nativo a 0,5 µm/px**, que es nuestro privado (0,465). Declara **1,8 s/mm² a 0,5 mpp** y
   3,2 s/mm² a 0,25. Todo el resto de la rama de mitosis pide 0,25 y nos obliga a ampliar 1,86×.
   Es el único candidato aparecido hasta hoy donde la escala física del privado **no es un
   problema a resolver antes de empezar**.
3. **Es 17× más rápido que HoVer-Net y 5× más rápido que CellViT** (verificado: 17,2× y 5,6×,
   medidos con el modelo chico sobre PanNuke a 0,25 mpp en una A40, no en la configuración de
   mitosis). Eso ataca de frente el motivo por el que Sebastián puso la rama de núcleos en pausa,
   que fue **el costo** y no el método ([[simil-hovernet-decision-31jul]]: 3 h 36 por lámina, 881
   en cola). **Con nuestros números la premisa no queda atacada, queda demolida:** la 129741 tiene
   68 mm² de tejido, que a 1,78 s/mm² son **dos minutos por lámina**. Las 881 de la cola darían
   **~30 h** contra los ~132 días de HoVer-Net. A ese precio **el recorte a los parches de mayor
   atención deja de ser necesario para ahorrar tiempo**, y sigue haciendo falta solo para controlar
   falsos positivos. (El «~240×» que citaba esta hoja salía de 4799/20 y **se cae** con el §6.)

**Números que publica, ya verificados y con la atribución corregida** (detalle en
[`hovernext_estudio.md`](hovernext_estudio.md) §2):

- **F1 0,84 = detección BINARIA**, o sea «¿acá hay un núcleo?», sin decir de qué tipo. Cuando hay
  que decir el tipo, el F1 medio por clase es **0,606**.
- **Balanced accuracy 0,758 = promedio sobre seis clases entre las que NO está la mitosis**
  (neutrófilo, epitelio, linfocito, plasmática, eosinófilo, conectivo).
- **La mitosis sola, que es el número que decide, está en el apéndice: F1 0,55 a 0,62 según cómo
  se agregue, con recall 0,72 y precisión 0,55.** O sea que sobre-cuenta casi al doble. El mejor
  en mitosis es el modelo **más chico** (HNTiny), que es además el más rápido.
- **47,7 mPQ en PanNuke**: cierto, y el +3 % es relativo (0,477 contra 0,463). Pero **CellViT
  queda arriba con 0,498**, y en la clase **neoplásica** HoVer-NeXt queda **por debajo de
  HoVer-Net**. Además los propios autores dicen que el mPQ es la métrica que hay que evitar.

**El punto débil, ahora con el PDF delante y peor de lo que decía esta hoja:** las ventajas
**no viven en el mismo juego de pesos**. Lizard-Mitosis tiene la clase mitótica y corre a 0,5 mpp,
pero es **todo colon**; PanNuke cubre mama pero **no tiene mitosis y corre a 0,25 mpp**. Elegir el
brazo de mama cuesta la clase mitótica **y también** la escala nativa. La combinación que queremos
no viene de fábrica, y ese sigue siendo el primer riesgo a medir.

**Lo que sí mejoró al verificar:** el paper **sí valida fuera de colon**, y en mama le va bien.
Su tabla por tejido (Supp. C.5) pone a **mama 6ª de 19 con mPQ 0,495, por encima del promedio
0,477 y muy por encima de colon, que sale 17º con 0,428**. El riesgo «es un paper de colon, en
mama va a andar mal» queda desactivado para segmentar y tipificar núcleos. **Lo que nunca se midió
fuera de colon es la clase mitótica**, y eso queda entero.

## 2. El candidato que resuelve la supervisión: CellViT++ (2025)

> Hörst F et al. *CellViT++: Energy-Efficient and Adaptive Cell Segmentation and Classification
> Using Foundation Models*. **arXiv `2501.05269`**, publicado (PMID 41576779). Código:
> `github.com/TIO-IKIM/CellViT-plus-plus`, además paquete de PyPI. Mismo grupo que CellViT, del
> que ya tenemos el repo clonado como referencia.

**Su aporte no es segmentar mejor, es cuánta anotación pide para una clase nueva.** Usa un modelo
fundacional congelado como encoder, calcula tokens por célula, y entrena encima **cabezas
clasificadoras livianas** para tipos celulares que nunca vio, con muy pocos datos. Reportan
segmentación zero-shot y clasificación de tipo celular «data-efficient» sobre siete datasets.

**Por qué nos toca en el punto exacto donde estamos trabados:** nuestro material de patólogo son
**61 polígonos de una lámina, y parciales** ([[anotaciones-patologo-qupath]]). Cualquier método
que pida anotación densa por objeto queda fuera por el criterio 2 del rubric. Este está construido
para el régimen contrario, que es agregar una clase con poquísimos ejemplos. Es la vía por la que
las 26 marcas de mitosis dejarían de servir solo para validar.

**Evidencia externa que lo respalda, y es de esta semana en términos del proyecto:** *Benchmarking
Foundation Models for Mitotic Figure Classification* (Ammeling, Ganz, … Aubreville; **MELBA
2026**, arXiv `2508.04441`) mide justamente esto y concluye que adaptar un modelo fundacional con
**LoRA alcanza el rendimiento del 100 % de los datos usando el 10 %**, y que reduce el hueco
fuera de dominio en tipos tumorales no vistos. Es el argumento cuantitativo de por qué una cabeza
liviana sobre un encoder congelado es el camino cuando la anotación escasea.

**Lo que lo frena:** de CellViT ya medimos que **a 0,50 µm/px el recall de detección cae de 0,82 a
0,60** y queda por debajo de HoVer-Net a 0,25. No sabemos si CellViT++ arregla eso, y es lo
primero que habría que ir a buscar en su PDF antes de recomendarlo por encima de HoVer-NeXt.

## 3. El especialista puro de mitosis, con pesos públicos: MIDOG 2025

Si lo que se quiere es el detector de mitosis y nada más, el ecosistema MIDOG ya tiene los
modelos, entrenados y abiertos, sin que nosotros anotemos nada:

| Rol | Método | Números | Código |
|---|---|---|---|
| Detectar la mitosis (Track 1) | **RF-DETR** con minería de negativos duros, arXiv `2509.02599`, entrenado sobre MIDOG++ | F1 **0,789**, recall 0,839, precisión 0,746 en test preliminar | sí |
| Decidir si es atípica (Track 2, **ganador**) | **DINOv3-H+ con LoRA** y focal loss ponderada por dominio, arXiv `2508.21041` | 1º puesto en el test oculto final, entrenando solo ~**1,3 M** parámetros | `github.com/Sanofi-Public/EFTD-midog-amf` |

Que el ganador de 2025 sea un modelo fundacional con LoRA y 1,3 M de parámetros entrenables es el
mismo mensaje del párrafo anterior, ahora en forma de resultado de competencia: **la arquitectura
específica pesa menos que adaptar bien un encoder grande con poca anotación.**

**El argumento externo que ya teníamos y que sigue siendo el mejor de la carpeta:** fuera de los
puntos calientes curados, la tasa de falsos positivos de los detectores de mitosis **se triplica**
(+208 %, 365 casos, 12 tipos tumorales; overview MIDOG 2025). Correr el detector sobre la lámina
entera es justo lo que no hay que hacer, y restringirlo a los parches de mayor atención de CLAM es
la forma correcta del problema. **Ese número defiende el diseño de Sebastián, gane el paper que
gane.**

## 4. La tabla, contra el mismo rubric de `busqueda.md`

| Candidato | 1 · parche | 2 · supervisión | 3 · ganancia | 4 · µm/px | 5 · abierto | Mapea el objeto |
|---|---|---|---|---|---|---|
| **HoVer-NeXt** *(verificado)* | sí, y devuelve objetos | **pesos públicos**, cero anotación nuestra | **F1 mitosis 0,55-0,62** (el 0,84 es detección binaria) · 17× más rápido, **2 min/lámina** | **0,5 nativo** en el brazo mitosis; **0,25** en el brazo mama | código GPL-3.0 + pesos | **sí** |
| **CellViT++** | sí, y devuelve objetos | **cabeza nueva con pocos ejemplos** | zero-shot + clasificación con pocos datos, 7 datasets | hereda el problema de CellViT a 0,5 | código + PyPI | **sí** |
| **MIDOG 2025** (RF-DETR / DINOv3-LoRA) | sí | **pesos públicos** | F1 0,789 detección · 1º puesto atípicas | 0,23 a 0,26 | sí | **sí**, solo mitosis |
| Jaroensri (Hoja 7) | sí | pesos **no** | supera al patólogo en 3 de 3 componentes | 0,25, y **excluye el 20×** | artículo sí, pesos no | no, puntúa |

## 5. Cuántas tareas cubre cada uno, que es la otra pregunta de Ernesto

Un mapeador de núcleos cubre **dos de las tres tareas con un solo modelo**, porque las dos se
calculan del mismo objeto:

- **Mitosis**: contar los núcleos de clase mitótica en la ventana más activa. Es un **máximo
  local**, la regla de Nottingham.
- **Pleomorfismo y grado nuclear**: medir área, forma y textura de los núcleos, y comparar cada uno
  **contra la mediana de su vecindario**, que es como puntúa el patólogo y que además es
  **invariante a la escala**, así que esquiva el problema del 20× contra 40×.

**La tercera no la cubre, y hay que decirlo: formación tubular es arquitectura del tejido, no
núcleos.** Ahí el especialista tiene que ser otro, y el de Jaroensri (1 mm a 1,0 µm/px) es el que
tenemos fichado.

**Y hay evidencia en contra que no podemos esconder:** Jaroensri **probó features de núcleo hechas
a mano para pleomorfismo y no mejoraron**, y lo atribuye a la variabilidad de tinción y de aspecto
en grado alto ([[jaroensri-2022-nottingham-tres-componentes]]). Eso golpea a la rama de núcleos
para pleomorfismo, viniendo de un grupo con más datos que nosotros. **Donde la rama de núcleos
queda limpia es en mitosis**, que es un objeto discreto que se cuenta, no una textura que se
puntúa.

## 6. Lo que yo propondría decir en la reunión

1. **Jaroensri sigue siendo la propuesta principal** para la forma del pipeline y para las tres
   etiquetas a la vez. No se cae.
2. **HoVer-NeXt es la propuesta nueva**, y entra por la puerta que Sebastián mismo cerró: es la
   rama de núcleos **sin el costo** que la puso en pausa, con clase de mitosis, con pesos
   públicos, y a la escala de nuestro privado sin ampliar nada.
3. **La prueba barata, CORREGIDA el 14-ago tarde.** La versión original de esta hoja decía «correr
   el modelo sobre los ~20 parches de mayor atención de la 129741 y ver cuántas de las 26 mitosis
   recupera». **Esa prueba no puede dar un resultado interpretable, y se ve sin correr nada:** el
   top-20 de los 4799 parches **contiene 3 de los 28 parches con mitosis** (mediana sobre los 12
   checkpoints; el peor da 0 y el mejor 5). Para capturar la mitad de las marcas hacen falta **189
   parches**, y para las 28, **1392**. El máximo recuperable de la prueba original era 3, no 26.
   *(No contradice el AUC 0,890: el percentil mediano de un parche con mitosis es ~96, o sea el
   puesto ~190 de 4799, y el top-20 es el percentil 99,58, un punto de operación mucho más
   exigente que el que el AUC resume.)*

   **La versión que sí decide es más simple y encima más barata**, porque el §1.3 la volvió
   gratis: **correr sobre la lámina entera**, que son dos minutos, y medir **recall sobre las 26
   marcas**. La pregunta que decide el candidato es si un detector entrenado en **colon** ve las
   mitosis que el patólogo marcó en **mama**. **Sin calcular precisión contra el geojson**: las
   anotaciones son positivos **parciales**, así que una detección fuera de las marcas es de
   estatus desconocido y no un error. La atención entra como **variable**, no como filtro: ver si
   las detecciones se concentran donde el modelo mira, que es el argumento de MIDOG (+208 % de
   falsos positivos fuera de los puntos calientes) medido en nuestra lámina. Sigue siendo el
   patrón «Etapa 0 antes de Etapa 1» que ahorró entre 18 y 24 horas en PathPT: si no recupera, la
   rama se cierra en un día y no en un sprint.
4. **La pregunta abierta para Sebastián** sigue siendo la misma del 12-ago: si hay **más láminas
   anotadas** y quién es GDT. Con una lámina se valida un go/no-go; para entrenar cualquier cosa,
   no alcanza.

## 7. Lo que esta hoja no afirma

- **Que ninguno de estos suba una métrica nuestra.** No hay nada medido en nuestros datos, y el
  historial son cuatro ejes cerrados sin mejora (Hallazgos 11 a 14).
- **Los números de HoVer-NeXt (§1) SÍ están verificados** contra el PDF desde el 14-ago tarde.
  **Los de CellViT++ y MIDOG (§2 y §3) NO.** Ver el aviso de arriba.
- **Que HoVer-NeXt detecte mitosis en mama.** Su clase mitótica se entrenó y se validó **solo en
  colon**: verificado, no hay un solo número de mitosis fuera de CRC. Es el primer riesgo, no un
  detalle. *(Distinto es segmentar y tipificar núcleos en mama, donde su modelo de PanNuke sí
  tiene número propio y bueno.)*
- **Que la rama de núcleos esté reabierta.** Sigue pausada desde el 31-jul. El costo verificado
  ataca la premisa que la pausó, pero reabrir es **regla 9.b** y exige pre-registro.
- **Que la búsqueda sea exhaustiva.** Es una hora de trabajo. Quedaron sin mirar NuLite
  (arXiv `2408.01797`) y LSP-DETR (arXiv `2601.03163`), los dos de la familia rápida de núcleos.

Relacionadas: [[papers-rama-mitosis-bcd]], [[jaroensri-2022-nottingham-tres-componentes]],
[[papers-nucleos-pleomorfismo-sebastian]], [[tareas-geometricas-mitosis-grado-nuclear]],
[[simil-hovernet-decision-31jul]], [[anotaciones-patologo-qupath]],
[[cohortes-magnificacion-fisica]].
