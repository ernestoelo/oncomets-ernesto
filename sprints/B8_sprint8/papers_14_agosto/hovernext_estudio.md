# HoVer-NeXt 2024: estudio

> Baumann E, Dislich B, Rumberger JL, Nagtegaal ID, Rodríguez Martínez M, Zlobec I. *HoVer-NeXt:
> A Fast Nuclei Segmentation and Classification Pipeline for Next Generation Histopathology*.
> **Proceedings of Machine Learning Research 250:61-86, MIDL 2024, full paper track.**
> CC-BY 4.0. Institute of Tissue Medicine and Pathology, Universidad de Berna.
> Código: `github.com/digitalpathologybern/hover_next_train` y `/hover_next_inference`.
>
> PDF en [`../hover_next.pdf`](../hover_next.pdf) (26 pág., md5 `ce8dfa11e6f12542a6570fb7bd4a7d47`),
> volcado de texto en [`../hover_next.txt`](../hover_next.txt) (`pdftotext -layout`, 1191 líneas).
> **Leído entero el 14-ago-2026**, cuerpo y los dos apéndices. **No se bajaron pesos ni se clonó
> el repo.**
>
> La versión de una página que este estudio verifica: [`hoja_especialistas.md`](hoja_especialistas.md)
> (Hoja 8), escrita el mismo día **con búsqueda web y sin el PDF**. Este documento es el que
> cierra esa brecha.
>
> **Cómo funciona el modelo por dentro** (el BCB-map, los dos decodificadores, el watershed, las TTA,
> el stitcher) está en [`hovernext_mecanismo.md`](hovernext_mecanismo.md), escrito el 14-ago a la
> noche. Este documento verifica los **números**; ese otro explica el **mecanismo** y contesta con
> cuentas dos cosas que acá se dan por sentadas: **de dónde sale realmente el 17×** (el BCB compra
> ~1,5×, no 17×) y **si el pipeline acepta parches sueltos** (espera una WSI).
>
> **Las tablas del paper vienen destrozadas en el volcado** (columnas intercaladas, Figura 2 sobre
> todo). Los números de acá se leyeron cruzando el volcado con el texto corrido que los comenta;
> donde el volcado no permite decidir, se dice.

---

## 1. Qué propone, en una frase

Segmentar y clasificar **cada núcleo** de una lámina H&E lo bastante rápido como para correrlo
sobre cohortes enteras, con una U-Net de dos decodificadores y encoder ConvNeXt-v2, más un
*stitcher* aparte que arma la lámina completa; y, de paso, **agregarle a Lizard una clase de
mitosis** que no tenía.

El paper es dos cosas a la vez y conviene separarlas, porque solo una nos interesa: es un paper
de **ingeniería de inferencia** (de ahí el 17×) y es un paper de **dataset** (de ahí la clase
mitótica). El modelo en sí es una actualización incremental de su propia entrada al CoNiC 2022.

## 2. Las seis afirmaciones de la Hoja 8, contra el texto

| # | Afirmación de la Hoja 8 | Veredicto | Lo que dice el paper |
|---|---|---|---|
| 1 | Tiene clase de mitosis | **Confirmada** | Contribuciones 1 y 2 (§1, L100-105). Extienden Lizard con mitosis y publican dataset propio + validación |
| 2 | Corre nativo a 0,5 µm/px, 1,8 s/mm² a 0,5 y 3,2 a 0,25 | **Confirmada** | Abstract L37. Lizard está «available at 0.5mpp» (A.5, L825). 1,78 s/mm² HNLarge 4TTA y 3,22 s/mm² HNTiny (§3.3) |
| 3 | 17× sobre HoVer-Net y 5× sobre CellViT | **Confirmada, con letra chica** | 17,2× y 5,6× (§3.3, L435). Medido con **HNTiny sobre PanNuke a 0,25 mpp**, 4 TTA, A40 48 GB, 16 cores, 5 WSI de TCGA COAD/READ |
| 4 | F1 **0,84** | **Confirmada pero mal atribuida** | Es **bF1, detección binaria**: hay núcleo o no hay, sin clase. 0,841 en GlaS. El F1 **medio por clase** es **mF1 0,606**, y la mitosis **ni siquiera está en esa tabla** |
| 5 | balanced accuracy media **0,758** | **Confirmada, y es sobre 6 clases que NO incluyen mitosis** | mAcc 0,759 de HNLarge en GlaS, promediando neutrófilo, epitelio, linfocito, plasmática, eosinófilo y conectivo (Fig. 2A) |
| 6 | 47,7 mPQ en PanNuke, +3 % sobre HoVer-Net | **Confirmada, y el +3 es relativo** | mPQ<sub>Tiss</sub> 0,477 (HNTiny, 16 TTA) contra 0,463 de HoVer-Net: **+0,014 absoluto**, que es +3,0 % relativo (Fig. 3) |

**Las seis se sostienen como hechos. Dos de ellas dicen algo distinto de lo que la Hoja 8 hace
creer,** y son justamente las dos que se leen como «qué tan bueno es esto»:

- **El 0,84 no es la calidad de clasificación, es la de detección binaria.** Responde «¿acá hay un
  núcleo?», no «¿de qué tipo es?». Cuando hay que decir el tipo, el promedio cae a **0,606**, y
  las clases raras se hunden: neutrófilo 0,313, plasmática 0,471, eosinófilo 0,553. La regularidad
  es transparente: **cuanto más rara la clase, peor el F1**, y la mitosis es la más rara de todas.
- **El 0,758 promedia seis clases entre las que no está la mitosis.** El test de esa tabla es GlaS,
  que es el subconjunto externo de Lizard, y Lizard-Mitosis no se evalúa ahí. Citar ese número al
  lado de «tiene clase de mitosis» sugiere una cobertura que el número no da.

Dos apuntes más, que no son correcciones pero cambian el tono:

- **HoVer-NeXt no es el estado del arte en PanNuke.** CellViT-SAM-H marca 0,498 mPQ<sub>Tiss</sub>
  contra sus 0,477. El paper lo dice sin esconderlo y responde con dos argumentos: que CellViT sin
  pre-entrenamiento solo empata a HoVer-Net, y que **cualitativamente su ventaja no se traslada a
  la lámina completa** (Supp. Fig. 7). Y en la clase **neoplásica**, que es la que a nosotros nos
  importa, HoVer-NeXt (0,536 PQ) queda **por debajo de HoVer-Net** (0,551) y bastante por debajo de
  CellViT (0,581).
- **El mPQ es la métrica que los propios autores dicen que hay que evitar.** §2.5 abre citando a
  Foucart 2023: la panoptic quality no debería usarse para núcleos, porque el IoU es demasiado
  sensible en objetos chicos y porque el producto premia **no detectar** un objeto por sobre
  clasificarlo mal. Lo reportan «for comparison». Usar el 47,7 como titular es apoyarse en la
  métrica que el paper desaconseja en la página anterior.

## 3. Las tres preguntas que la búsqueda web dejó abiertas

### 3.a ¿Validan fuera de colon?

**Sí, pero solo con el modelo que no tiene mitosis, y el resultado en mama es mejor de lo que
esperábamos.** La tabla de Supp. C.5 desglosa PanNuke por tejido, y ahí sí hay mama:

| Tejido | bPQ | mPQ (16 TTA) | Puesto de 19 |
|---|---:|---:|---:|
| Vejiga | 0,696 | **0,578** | 1 |
| Esófago | 0,647 | 0,527 | 2 |
| Riñón | 0,683 | 0,517 | 3 |
| Hígado | 0,717 | 0,504 | 4 |
| Testículo | 0,680 | 0,497 | 5 |
| **Mama** | **0,643** | **0,495** | **6** |
| *(promedio de los 19)* | | *0,477* | |
| **Colon** | **0,570** | **0,428** | **17** |
| Piel | 0,623 | 0,414 | 19 |

**Mama sale 6ª de 19 y por encima del promedio; colon sale 17ª.** El grupo es de patología
colorrectal, su dataset propio es colon, y sin embargo el tejido donde su modelo pan-cáncer rinde
peor es colon y mama le va claramente mejor. Eso desactiva la versión ingenua del riesgo («es un
paper de colon, en mama va a andar mal»): **para segmentar y tipificar núcleos en mama, el modelo
de PanNuke tiene número propio y es bueno.**

Lo que **no** hay es validación de la **clase mitótica** fuera de colon. Los tres conjuntos que la
tocan son CRC sin excepción: Lizard es colon, el dataset de mitosis son 48 ROI de 11 WSI de colon,
y MitEval son 13 ROI de nueve WSI de resección de colon. **Cero mitosis medidas en mama.**

### 3.b ¿Qué clases predice cada juego de pesos, y cuánto rinde la mitosis sola?

Son **dos modelos con vocabularios distintos**, y se publican en tres tamaños de encoder cada uno
(Tiny, Base, Large):

| Pesos | Clases | Resolución nativa | Mitosis |
|---|---|---|---|
| **Lizard-Mitosis** | neutrófilo, epitelio, linfocito, plasmática, eosinófilo, conectivo **+ mitosis** | 0,5 mpp | **sí** |
| **PanNuke** | neoplásica, epitelial no neoplásica, inflamatoria, conectiva, muerta | 0,25 mpp | **no** |

**La mitosis sola, que es el número que decide el candidato, está en Supp. C.3** y no en ninguna
de las tablas grandes:

| Modelo | Precisión | Recall | F1 |
|---|---:|---:|---:|
| HNLarge | 0,564 | 0,680 | 0,617 |
| HNBase | 0,527 | 0,671 | 0,590 |
| **HNTiny** | 0,545 | **0,720** | **0,620** |

El texto de §3.1 da otros valores para lo mismo (**HNTiny 0,553**, HNLarge 0,521, HNBase 0,517).
No es una contradicción: §2.4 avisa que para MitEval y EosEval reportan «WSI-level performance», y
C.3 promedia distinto que la Figura 2D. El mismo desfase aparece en eosinófilos (0,668 en el texto
contra 0,688 en C.4, con 11 ROI de 8 pacientes promediadas sobre 7). **Cualquiera de las dos
agregaciones deja la mitosis entre 0,55 y 0,62 de F1, no en 0,84.**

Tres lecturas operativas:

1. **Precisión ~0,55: casi la mitad de lo que llama mitosis, no lo es.** Con recall 0,72. Para un
   conteo de Nottingham, que es un máximo local sobre una ventana, un detector que sobre-cuenta al
   doble no sirve crudo: pide umbral propio o una segunda pasada.
2. **HNTiny es el mejor en mitosis en las dos agregaciones**, y es también el más rápido y el más
   chico. Es una coincidencia cómoda: si algún día corremos esto, el modelo a elegir para mitosis
   es el chico, no el grande. El paper no lo destaca, pero es lo que muestran sus dos tablas.
3. **Las TTA le rinden a las clases raras mucho más que al resto.** Con 4 TTA la mitosis gana
   **+4,87 % de F1**, neutrófilos +4,16 y eosinófilos +2,16, mientras las clases comunes ganan menos
   del 1 % y las plasmáticas **pierden** 0,35 %. Si se corre para mitosis, se corre con TTA.

### 3.c ¿A qué µm/px están los pesos, y qué pasa a 0,465?

**Lizard-Mitosis a 0,5 mpp; PanNuke a 0,25 mpp** (A.5: «PanNuke is only available as 256×256px
crops and only at ∼0.25mpp»). Nuestro privado está en **0,465**, o sea a **7,5 % del nativo** del
modelo que tiene mitosis.

**Qué pasa exactamente a 0,465: no encontrado.** El paper no hace ningún estudio de sensibilidad a
la resolución. Lo que sí hay es una evidencia indirecta fuerte, y está escondida en A.8: **los ROI
de MitEval vienen de láminas a 0,12 y 0,25 mpp, y los publican re-muestreados a ~0,5 mpp.** O sea
que su propia validación de mitosis está hecha sobre material llevado a 0,5 desde 4,2× y 2× más
fino. **Nuestro 1,075× es despreciable al lado de eso.**

## 4. El hallazgo que reordena la lectura: las dos ventajas no viven en el mismo modelo

La Hoja 8 presenta tres ventajas en una lista, como si se sumaran. Con el PDF delante, **se
reparten entre los dos juegos de pesos y compiten**:

| Lo que queremos | Lizard-Mitosis | PanNuke |
|---|---|---|
| Clase de mitosis | **sí** | no |
| Validado en mama | no (todo CRC) | **sí, mPQ 0,495, 6º de 19** |
| Nativo a nuestra escala (0,465) | **sí, 0,5 mpp** | no, 0,25 → habría que ampliar 1,86× |

**Los dos ejes se cruzan al revés de lo que uno querría.** El modelo que sabe de mitosis es de
colon y está a nuestra escala; el que cubre mama no sabe de mitosis y está a la escala que no
tenemos. La Hoja 8 ya decía que la combinación «mitosis y mama» no viene de fábrica, y eso queda
confirmado; lo nuevo es que **elegir el brazo de mama cuesta también el 0,5 mpp**, no solo la clase
mitótica. Es un costo doble que la hoja no registraba.

Contra eso juega, y no es poco, que **el eje tejido resultó más benigno de lo temido** (§3.a: mama
por encima del promedio y de colon) mientras que **el eje escala resultó casi gratis** (§3.c). Lo
que queda como riesgo real, sin evidencia a favor ni en contra, es **la clase mitótica en tejido
mamario**, que es exactamente lo que un go/no-go de un día mide.

## 5. Cómo consiguieron las etiquetas de mitosis sin patólogo

Es la parte del paper que más nos toca, porque **la anotación es nuestro cuello**, no el modelo.

**El dataset de entrenamiento (§2.4, A.6):** 48 ROI de 8192×8192 px sobre 11 WSI de colon H&E. A
cada lámina le hicieron un **re-tinte de inmunohistoquímica pHH3**, que marca específicamente
mitosis; **registraron** el par H&E-pHH3 y sacaron la verdad de campo por **umbral sobre el canal
DAB deconvuelto**. Cero anotación manual de objetos. Los umbrales son **por ROI**, para absorber
diferencias intra e inter lámina, y eligieron los ROI a propósito con mucha mitosis potencial,
evitando zonas necróticas y artefactos de tinción.

**Cómo completaron el resto de las clases (A.7):** una rutina de auto-entrenamiento adaptada de
ST++. Entrenan cinco modelos sobre Lizard con validación cruzada, infieren en ensemble sobre los
recortes de mitosis, reentrenan sobre el combinado guardando checkpoints, y **parten las muestras
en fáciles y difíciles según cuánto les cambió la panoptic quality** entre el primer checkpoint y
el mejor. Reentrenan desde cero solo con las fáciles y con eso predicen las difíciles. Al final,
un modelo entrenado solo con mitosis anota mitosis sobre Lizard, y **solo agrega la marca donde no
había ninguna otra etiqueta en ningún píxel**.

**Y el test que sí es de patólogos (A.8):** MitEval, 13 ROI sobre nueve WSI de resección de colon,
anotadas por **tres patólogos certificados** con elipses chicas. Emparejan a 6 µm de distancia
máxima y **conservan la anotación si al menos un segundo observador coincide**, sin ronda de
revisión. El acuerdo entre los tres da **ICC3 = 0,860, IC [0,69 · 0,95]**. Nueve ROI son de cohorte
interna a 0,12 mpp y cuatro de TCGA a 0,25.

**Por qué importa acá:** es una receta completa y publicada para fabricar etiquetas de mitosis a
escala sin pedirle horas a un patólogo, que es literalmente el problema por el que nuestras
anotaciones son 61 polígonos parciales de una lámina. **No es gratis** (pide re-teñir el bloque y
un registro de lámina entera), pero es una vía que hasta hoy no teníamos fichada. Y el propio
paper la señala como conclusión en la Discusión: el re-tinte automático «is a straightforward way
of generating large labeled datasets» y **una sola institución alcanza** para aprender mitosis.

### 5.a Un regalo lateral para el hilo de las regiones de escaneo

A.6 describe **su procedimiento de registro**, y ese hilo nuestro está abierto y trabado
([[regiones-escaneo-bif-cohorte-privada]]). Hacen, en orden: convertir a TIFF; **fijar a mano un
punto de anclaje** sobre un núcleo claramente visible en las dos imágenes, para matar el
desplazamiento grueso; estimar transformaciones **rígida y no rígida con SimpleElastix** sobre las
versiones **en escala de grises submuestreadas a 0,5 mpp**; y recién entonces aplicar el resultado
a resolución completa. Máquina de 64 cores y 512 GB.

Nosotros venimos midiendo con NCC a level 0 y con el barrido de rotación saturado, y ya sabemos
que el diagnóstico anterior falló **por resolución**. Su receta dice dos cosas útiles: que el
ancla gruesa va **primero y a mano** (nosotros tenemos el desplazamiento medido, dx=3829), y que
la estimación se hace **a 0,5 mpp en gris**, no a resolución completa. No es prueba de nada sobre
nuestras láminas, pero es una referencia publicada para el paso que tenemos trabado.

## 6. Lo que el paper dice de sí mismo, y conviene decirlo nosotros primero

§5, «Limitations», es breve y honesto:

- **Lizard tiene mitosis mal anotadas.**
- **No todo objeto pHH3-positivo es una mitosis visible en H&E.** El pHH3 también marca células en
  G2 y otros objetos levantan el anticuerpo (esto último lo dicen en A.8, y es la razón por la que
  armaron MitEval aparte).
- **El dataset es ruidoso por construcción**, y los resultados «will never entirely reflect the
  true model performance».
- **Había un método mejor disponible** para anotar mitosis en H&E y no lo usaron: citan a
  Aubreville 2023, que es MIDOG.
- **No usaron la partición en 3 folds de Lizard**, para maximizar datos de entrenamiento y poder
  compararse con su propia entrada al CoNiC. O sea que los números de Lizard salen de **una sola
  partición**.

A eso se suma una observación cualitativa suya sobre la lámina completa (Supp. Fig. 7) que es un
aviso para cualquiera que quiera correr esto en producción: HoVer-NeXt «falsely classifies a lot»
de mucosa normal como neoplásica, aunque es el único de los tres que clasifica bien los agregados
linfoides. **Los tres modelos comparados se equivocan feo fuera de dominio**, cada uno a su manera.

## 7. La cuenta de costo, con nuestros números

Es el argumento por el que este candidato apareció, así que conviene hacerlo con nuestra lámina y
no con las suyas. La **129741** tiene **4799 parches de 256 px a 0,465 µm/px**, o sea
0,0142 mm² por parche y **68,0 mm² de tejido**.

| Escenario | Cuenta | Tiempo |
|---|---|---|
| **HoVer-NeXt sobre la 129741 entera** | 68,0 mm² × 1,78 s/mm² | **~2 min** |
| HoVer-Net, medido por Sebastián | | **3 h 36** |
| Las 881 de la cola, si todas fueran como la 129741 | 881 × 2 min | **~30 h** |
| Las mismas con HoVer-Net | 881 × 3 h 36 | **~132 días** |

**Salvedades, las tres importan:** el 1,78 s/mm² es HNLarge con 4 TTA a 0,5 mpp sobre una A40 de
48 GB, que es comparable a nuestra A6000 pero no es nuestra medición; **HNTiny sería más rápido
todavía** y es el mejor en mitosis, así que el número es una cota superior; y **no verificamos que
la 129741 sea de tamaño típico** en la cohorte privada, así que las 30 h son una estimación de
orden de magnitud, no un presupuesto.

Con eso, **la premisa de costo que puso la rama en pausa el 31-jul no queda atacada, queda
demolida**: no es que se abarate lo suficiente como para justificar el recorte a los parches de
más atención, es que **a dos minutos por lámina el recorte deja de ser necesario para ahorrar
tiempo**. Sigue siendo necesario, pero por otro motivo, que es el del párrafo siguiente.

## 8. El go/no-go, corregido: al top-20 no le da el denominador

La Hoja 8 propone correr los pesos públicos sobre **«los ~20 parches de mayor atención»** de la
129741 y contar cuántas de las **26 mitosis marcadas** recupera. **Esa prueba, tal como está
escrita, no puede dar un resultado interpretable**, y se ve sin correr nada.

Cruzando `atencion_vs_patologo/percentiles_por_parche.csv` (los 163 parches anotados, con su
percentil de atención dentro de los 4799 de la lámina) contra los **28 parches que contienen las
26 marcas**, sobre los **12 checkpoints** medidos:

| Cuántos parches de mayor atención hay que tomar | Mediana de los 12 ckpt | Rango |
|---|---:|---|
| para capturar **3 de 28** | **20** | 0 a 5 marcas en el top-20 |
| para capturar la **mitad** (14 de 28) | **189** | 120 a 585 |
| para capturar el **80 %** (23 de 28) | **508** | 426 a 1147 |
| para capturar **las 28** | **1392** | 822 a 2609 |

**El top-20 contiene 3 de los 28 parches con mitosis** (mediana; un checkpoint da 0 y el mejor da
5). O sea que el máximo recuperable de la prueba propuesta es 3, no 26, y con ese denominador
**cualquier resultado, 0 o 3, es compatible con casi todo.**

**Esto no contradice el AUC 0,890.** Un AUC alto dice que los parches con mitosis rankean alto *en
promedio*: su percentil mediano es ~96, o sea el puesto ~190 de 4799. El top-20 es el percentil
**99,58**, un punto de operación muchísimo más exigente que el que el AUC resume. Las dos cosas son
ciertas a la vez, y la que manda para diseñar la prueba es el percentil, no el AUC.

**De paso corrige la cuenta de ahorro de la Hoja 8**, que citaba «~240×» y sale de 4799/20. Con el
top-189, que es el que captura la mitad, el ahorro real es **25×**; con el top-508, **9,4×**.

**Cómo quedaría la prueba para que decida algo** (y es *más barata* que la original, porque §7 la
volvió gratis):

1. **Correr sobre la lámina entera**, que son dos minutos. Elimina el problema del denominador de
   raíz: se evalúa contra las **26 marcas**, todas.
2. **Medir recall sobre las 26**, que es la pregunta que decide el candidato: ¿el detector de
   mitosis entrenado en colon a 0,5 mpp ve las mitosis que el patólogo marcó en **mama** a 0,465?
3. **No calcular precisión contra el geojson.** Las anotaciones son **positivos parciales**
   ([[anotaciones-patologo-qupath]]): hay mitosis en la lámina que el patólogo no marcó, así que
   toda detección fuera de las marcas es de estatus desconocido, no un falso positivo. Reportar
   solo el conteo bruto fuera de las marcas, como magnitud a explicar, y **no como error**.
4. **Ahí sí usar la atención, pero como variable, no como filtro**: ver si las detecciones caen
   preferentemente en parches de atención alta. Ese es el argumento de MIDOG (+208 % de falsos
   positivos fuera de los puntos calientes curados) medido en nuestra lámina, y es lo que
   defendería el diseño de dos etapas de Sebastián independientemente de qué especialista gane.
5. **Con HNTiny y con TTA**, por §3.b: es el mejor en mitosis y el que más gana con TTA.

**Sigue siendo una propuesta, no una tarea.** Ejecutarla exige bajar pesos (no autorizado) y
clonar el repo (no autorizado), y proponerla como mejora del pipeline cae bajo regla 9 y, por venir
de una rama pausada, bajo **regla 9.b**.

## 9. Qué nos sirve y qué no

**Sirve:**

- **La clase de mitosis con pesos públicos existe y está medida**, F1 0,55 a 0,62 con recall 0,72.
  Es el único candidato fichado que la trae hecha.
- **La escala dejó de ser un problema**: nativo a 0,5 mpp y con precedente propio de re-muestreos
  de 4,2×. Nuestro 1,075× no merece discusión.
- **El costo dejó de ser un argumento**: dos minutos por lámina.
- **Mama no es terreno hostil** para el modelo de PanNuke: 6º de 19, por encima de colon.
- **La receta de pHH3 + registro + umbral DAB** es una vía publicada para etiquetas de mitosis a
  escala sin anotación manual.
- **El procedimiento de registro de A.6** es referencia directa para el hilo de las regiones (§5.a).

**No sirve, o hay que mirarlo de frente:**

- **La clase mitótica nunca se midió fuera de colon.** Es el riesgo que queda entero.
- **Precisión ~0,55 en mitosis.** Sobre-cuenta al doble; para un conteo de Nottingham eso importa.
- **Las dos ventajas están en modelos distintos** y elegir mama cuesta la mitosis *y* la escala.
- **En la clase neoplásica queda por debajo de HoVer-Net**, y neoplásica es nuestra clase.
- **El dataset de mitosis es ruidoso por construcción** y ellos lo dicen.
- **Nada de esto es una mejora de métrica nuestra.** Es un mapeador de núcleos; que mapear núcleos
  mejore una predicción de lámina es una hipótesis sin ninguna evidencia a favor todavía, y el
  historial del proyecto son cuatro ejes cerrados sin mejora.
- **Jaroensri probó features de núcleo hechas a mano para pleomorfismo y no mejoraron.** Ese
  resultado sigue en pie y sigue apuntando a que, si la rama de núcleos sirve para algo, es para
  **mitosis** y no para pleomorfismo.

## 10. Lo que este estudio no afirma

- **Que HoVer-NeXt suba ninguna métrica nuestra.** No hay nada medido en nuestros datos.
- **Que funcione en mama para mitosis.** Es lo único que el paper no puede contestar y el go/no-go
  es exactamente para eso.
- **Que la rama de núcleos esté reabierta.** Sigue pausada desde el 31-jul; este estudio ataca la
  premisa de costo con números verificados, pero reabrir es regla 9.b y exige pre-registro.
- **Que el top-20 esté «mal» como diseño de pipeline.** Lo que se muestra es que **como prueba de
  validación no tiene denominador**. Cuántos parches conviene pasarle al especialista en
  producción es otra pregunta, y no se contestó acá.
- **Que las 30 h para 881 láminas sean un presupuesto.** Es una extrapolación desde una lámina y
  desde el hardware de ellos.
- **Que HNTiny sea mejor que HNLarge en general.** Lo es en mitosis, en las dos agregaciones. En el
  resto de las clases pierde.
- **Que se haya verificado el código o los pesos.** No se bajó nada. Todo sale del PDF.

## 11. Preguntas para llevar

1. **¿Se autoriza bajar los pesos y clonar `hover_next_inference`?** Sin eso, el go/no-go no se
   puede correr. Precedente: los cuatro repos del 2-ago, bajo las mismas reglas de solo lectura y
   fuera del PYTHONPATH.
2. **¿Hay más láminas anotadas, y quién es GDT?** Sigue sin respuesta desde el 12-ago. Con una
   lámina se valida un go/no-go; para entrenar cualquier cosa, no alcanza.
3. **¿Existe material para re-teñir con pHH3?** Es la pregunta que abre §5. Si hay acceso a los
   bloques, la receta de Berna es la vía más barata que hemos visto para etiquetas de mitosis a
   escala, y **no depende de que HoVer-NeXt nos sirva**.
4. **¿Se prefiere el brazo mama (PanNuke, sin mitosis, a 0,25) o el brazo mitosis (Lizard-Mitosis,
   colon, a 0,5)?** Son excluyentes y la decisión es de dominio, no técnica.

### ADDENDUM 17-ago-2026 — tres de las cuatro quedaron contestadas

La reunión del 14-ago ocurrió y Ernesto resolvió lo que dependía de él. **Las respuestas, en el
mismo orden:**

1. **Sí, autorizado.** Clonar `hover_next_inference` y bajar **los dos** juegos de pesos, destino
   `clam_testing2/hover_next_reference/`, REFERENCE ONLY y fuera del `PYTHONPATH` como los cuatro
   repos del 2-ago. Queda registrado como segundo precedente en el workaround E.a de `CLAUDE.md`.
2. **Sí, hay más: son doce**, no una. Viven en `/media/administrador/Storage1/sdonoso/anotaciones/`
   (de `sgaete`, READ-ONLY), las doce con features y WSI y **las doce con marcas de mitosis** — 94
   en total contra las 26 de la 129741. **Quién es «GDT» sigue sin respuesta.** Y aparece una
   discrepancia nueva: **Sebastián habló de 30**, así que faltan 18 y hay que preguntarle por ellas.
   Detalle en [[anotaciones-patologo-qupath]].
3. **Sin novedad**: la pregunta por el material para re-teñir con pHH3 sigue abierta, y sigue sin
   depender de que HoVer-NeXt nos sirva.
4. **No son excluyentes en la práctica: se corren los dos.** A ~2 min por lámina el costo dejó de
   ser el criterio que forzaba elegir. Responden preguntas distintas — Lizard-Mitosis se contrasta
   contra las 26 marcas de mitosis, PanNuke contra las regiones de Tumor. **Lo que sí hay que
   declarar** es que el brazo PanNuke corre sobre **píxeles interpolados**: pide 0,25 µm/px y la
   lámina tiene 0,465, o sea una ampliación de 1,86× de resolución que no existe en el archivo.

**Lo que este ADDENDUM no cambia**: ningún número del estudio, ni el §4 (las dos ventajas siguen
viviendo en modelos distintos), ni el §8 (el top-20 sigue sin denominador). Diseño de la semana en
`hovernext_129741/plan_semana_17ago.md` + [[hovernext-encargo-17ago-diseno]].

---

Relacionadas: [[hovernext-especialista-segunda-etapa]], [[jaroensri-2022-nottingham-tres-componentes]],
[[papers-rama-mitosis-bcd]], [[papers-nucleos-pleomorfismo-sebastian]],
[[simil-hovernet-decision-31jul]], [[hovernet-ya-corriendo-sgaete]], [[anotaciones-patologo-qupath]],
[[cohortes-magnificacion-fisica]], [[tareas-geometricas-mitosis-grado-nuclear]],
[[regiones-escaneo-bif-cohorte-privada]].
