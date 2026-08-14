# Hoja 8. Los especialistas que sí mapean el objeto, no solo lo puntúan

> Escrita el **14-ago-2026**, una hora antes de la reunión, a pedido de Ernesto. Continúa la
> numeración de [`hoja_jaroensri.md`](hoja_jaroensri.md) (Hoja 7).
>
> ⚠ **Estado de verificación: búsqueda web, NO PDF.** Ninguno de los cuatro candidatos de acá se
> abrió como artículo completo. Los números salen de resúmenes, páginas de proyecto y repos.
> Vale la misma advertencia que [`busqueda.md`](busqueda.md) §8 aplicó a sus candidatos 5.2 a
> 5.4: del elegido citamos texto, de estos citamos lo que dice su ficha. **No presentarlos como
> verificados.**
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
3. **Es 17× más rápido que HoVer-Net y 5× más rápido que CellViT.** Eso ataca de frente el motivo
   por el que Sebastián puso la rama de núcleos en pausa, que fue **el costo** y no el método
   ([[simil-hovernet-decision-31jul]]: 3 h 36 por lámina, 881 en cola). Combinado con el recorte a
   los 20 parches de mayor atención, que ya calculamos en ~240×, el costo deja de ser el
   argumento que decide.

**Números que publica:** F1 binario de detección **0,84**, balanced accuracy media **0,758** sobre
sus clases, y **47,7 mPQ** en PanNuke, +3 % sobre HoVer-Net. Pesos disponibles en dos sabores,
Lizard-Mitosis (el que trae la clase mitótica) y PanNuke.

**Lo que hay que decir sin que lo pregunten, porque es el punto débil:** el modelo con clase
mitótica está entrenado sobre **Lizard, que es colon**, y nosotros somos mama. El que sí es
pan-cáncer y cubre mama es el de PanNuke, y **ese no tiene clase mitótica**. O sea que la
combinación que queremos, mitosis y mama, **no viene resuelta de fábrica**, y ese es el primer
riesgo a medir. Tampoco verificamos contra el PDF si validan fuera de colon.

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
| **HoVer-NeXt** | sí, y devuelve objetos | **pesos públicos**, cero anotación nuestra | F1 0,84 · +3 % mPQ sobre HoVer-Net · 17× más rápido | **0,5 declarado y nativo** | código GPL-3.0 + pesos | **sí** |
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
3. **La prueba barata es la de siempre, y no necesita GPU ni anotación nueva:** correr el modelo
   con pesos públicos sobre los ~20 parches de mayor atención de la lámina 129741 y ver cuántas
   de las **26 mitosis marcadas** recupera. Es el patrón «Etapa 0 antes de Etapa 1» que ya ahorró
   entre 18 y 24 horas en PathPT. Si no las recupera, la rama se cierra en un día y no en un
   sprint.
4. **La pregunta abierta para Sebastián** sigue siendo la misma del 12-ago: si hay **más láminas
   anotadas** y quién es GDT. Con una lámina se valida un go/no-go; para entrenar cualquier cosa,
   no alcanza.

## 7. Lo que esta hoja no afirma

- **Que ninguno de estos suba una métrica nuestra.** No hay nada medido en nuestros datos, y el
  historial son cuatro ejes cerrados sin mejora (Hallazgos 11 a 14).
- **Ningún número de acá está verificado contra el PDF.** Ver el aviso de arriba.
- **Que HoVer-NeXt funcione en mama.** Su clase mitótica es de colon. Es el primer riesgo, no un
  detalle.
- **Que la búsqueda sea exhaustiva.** Es una hora de trabajo. Quedaron sin mirar NuLite
  (arXiv `2408.01797`) y LSP-DETR (arXiv `2601.03163`), los dos de la familia rápida de núcleos.

Relacionadas: [[papers-rama-mitosis-bcd]], [[jaroensri-2022-nottingham-tres-componentes]],
[[papers-nucleos-pleomorfismo-sebastian]], [[tareas-geometricas-mitosis-grado-nuclear]],
[[simil-hovernet-decision-31jul]], [[anotaciones-patologo-qupath]],
[[cohortes-magnificacion-fisica]].
