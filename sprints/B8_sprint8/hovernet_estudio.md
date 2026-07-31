# HoVer-Net: estudio para la reunión (encargo 4)

> Graham et al., *HoVer-Net: Simultaneous Segmentation and Classification of Nuclei in
> Multi-Tissue Histology Images*, Medical Image Analysis 58:101563 (2019). PDF en
> [`hovernet_graham2019.pdf`](hovernet_graham2019.pdf) (arXiv:1812.06499v5). Leído completo
> el **31-jul-2026**: paper principal (15 pág.) y el apéndice A de ablaciones.
>
> Ficha bibliográfica y cita BibTeX: [`papers_b8.md`](papers_b8.md) §1.
> Contraparte: [`simil_estudio.md`](simil_estudio.md), porque **HoVer-Net es el front-end
> de SI-MIL** y los dos papers del encargo son la misma cadena.
>
> **Lo primero que hay que saber antes de leer el resto:** HoVer-Net **ya está instalado y
> corriendo en este servidor**, no es una hipótesis. Lo montó `sgaete` el 29-jul y el 30-jul
> completó una lámina de TCGA de punta a punta. El §10 tiene el inventario verificado.

---

## 1. Qué propone, en una frase

Separar núcleos que se tocan sin dibujar su contorno: en vez de predecir el borde, se
predice **dentro** de cada núcleo un campo con signo que va de −1 a +1, y el borde aparece
solo, como el salto entre el +1 de uno y el −1 del vecino.

## 2. El problema, que es de instancias y no de píxeles

Conviene tener clara la distinción antes de la fórmula, porque de ahí sale todo el diseño.

- **Segmentación semántica**: por cada píxel, decir si es núcleo o fondo. Sale una máscara
  binaria.
- **Segmentación de instancias**: además, decir **de cuál** núcleo es cada píxel. Salen
  objetos numerados.

Para contar núcleos, medir su forma o clasificarlos uno por uno hace falta lo segundo. Y ahí
está el problema real del paper: los núcleos tumorales aparecen **en racimo**, pegados. La
máscara binaria de un racimo de cinco núcleos es una sola mancha. Si uno se queda en la
máscara, cuenta uno donde hay cinco, y toda la morfometría que venga después queda
envenenada.

Las salidas previas atacaban esto prediciendo el **contorno** como clase aparte (DCAN,
CIA-Net) y restándolo de la máscara. El contorno es una línea de uno o dos píxeles de
ancho: es la clase más chica, la más desbalanceada y la más frágil justo donde dos núcleos
se aprietan y el borde se vuelve indistinto. El paper busca una señal que sea **gruesa y
redundante** en vez de fina y crítica.

## 3. El truco: los mapas horizontal y vertical

Para cada píxel de núcleo se calcula la distancia **con signo** a su propio centro de masa,
por separado en x y en y, **normalizada por núcleo** al rango [−1, +1]. El fondo vale 0, y
la línea que cruza el centro de masa también vale 0.

Salen dos mapas por imagen: el **horizontal** y el **vertical**. Eso es todo lo que
significa el nombre, HoVer = **Ho**rizontal + **Ver**tical.

**Mini ejemplo en una dimensión.** Una fila de 10 píxeles con dos núcleos pegados: el A
ocupa las columnas 1 a 4, el B las columnas 5 a 8.

| columna | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|---|---|
| máscara binaria (NP) | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 0 |
| mapa horizontal | 0 | −1 | −0.33 | +0.33 | +1 | −1 | −0.33 | +0.33 | +1 | 0 |

La máscara binaria es una sola mancha de ocho píxeles: no hay nada que separar. El mapa
horizontal, en cambio, sube monótono dentro de A, **se desploma de +1 a −1 entre la columna
4 y la 5**, y vuelve a subir dentro de B. La derivada entre columnas contiguas vale 0.67
adentro de cada núcleo y **−2 en la costura**. Un factor 3 de contraste, sobre una señal
que ocupa el núcleo entero y no una línea de un píxel.

Tres detalles del diseño que no son decorativos:

- **La normalización por núcleo** es lo que hace que el salto valga siempre ≈2 sin importar
  si el núcleo mide 10 píxeles o 60. Sin ella, el umbral del salto dependería del tamaño.
- **Hacen falta los dos mapas.** Si los dos núcleos se tocan de lado, el salto está en el
  mapa horizontal y el vertical cruza la costura sin enterarse. Si están uno encima del
  otro, al revés. Por eso el post-procesamiento toma el **máximo** de los dos gradientes.
- **El signo importa.** Un mapa de distancia sin signo (el de DIST, ref. [31] del paper)
  tiene un mínimo en el borde, pero el descenso es suave; acá hay una discontinuidad.

## 4. La red

Un encoder compartido y tres decoders. Fig. 2, pág. 4.

**Encoder**: Preact-ResNet50 con una modificación que importa: bajan el factor de
sub-muestreo total de **32 a 8**, poniendo stride 1 en la primera convolución y sacando el
max-pooling que le sigue. La razón es que en segmentación no se puede tirar resolución de
entrada y esperar recuperarla después. Bloques residuales de 3, 4, 6 y 3 unidades en los
niveles 1, 2, 4 y 8, con m = 256, 512, 1024 y 2048 mapas.

**Tres ramas de subida**, todas con el mismo diseño (upsample por vecino más cercano +
unidades densas):

| Rama | Qué predice | Salida |
|---|---|---|
| **NP** (nuclear pixel) | núcleo o fondo, por píxel | 2 canales |
| **HoVer** | las distancias horizontal y vertical | 2 canales de regresión |
| **NC** (nuclear classification) | el tipo de núcleo, por píxel | K canales |

NP y HoVer juntas hacen la segmentación de instancias: NP separa núcleo de fondo, HoVer
separa núcleos entre sí. NC es opcional: si no hay etiquetas de tipo, la red corre con dos
ramas.

Tres decisiones de implementación que conviene tener a mano:

- **Skip connections por suma, no por concatenación.** Ahorra memoria y mantiene fijo el
  ancho del decoder.
- **Convolución válida** en las ramas de subida, sin padding: por eso la entrada es 270×270
  y la salida 80×80. Se procesa por ventana deslizante y se descarta el borde, que es donde
  la predicción es peor. El costo es que hay que hacer más de un forward por parche nuestro
  de 256 px.
- **Unidades densas**: el texto dice 4 después del primer upsample y 8 después del segundo;
  la Fig. 2 dibuja 8 y después 4. Se contradicen. Si alguna vez importa, manda el código.

## 5. La loss

Seis términos, cuatro grupos de pesos (`w0` encoder, `w1` HoVer, `w2` NP, `w3` NC),
optimizados juntos. Ecuación (1):

```
L = λa·La + λb·Lb  +  λc·Lc + λd·Ld  +  λe·Le + λf·Lf
    \___ HoVer ___/    \___ NP ___/     \___ NC ___/
```

con `λb = 2` y el resto en 1, por selección empírica.

- **`La`** (ec. 2): error cuadrático medio entre los mapas H/V predichos y los reales, sobre
  todos los píxeles.
- **`Lb`** (ec. 3): la contribución nueva del paper. Error cuadrático medio entre el
  **gradiente** del mapa predicho y el gradiente del real (∇x sobre el horizontal, ∇y sobre
  el vertical), **promediado solo sobre los píxeles de núcleo**. Es el único término que
  mira directamente lo que después se va a usar para cortar. Que su λ sea el doble que el
  resto dice cuánto pesa en el diseño.
- **`Lc` + `Ld`**: entropía cruzada (ec. 4, K=2) más Dice (ec. 5, ε=1e-3) en NP. El Dice
  entra por el desbalance núcleo/fondo.
- **`Le` + `Lf`**: lo mismo en NC, con K = número de tipos + 1 por el fondo (5 en CoNSeP: 4
  tipos + fondo). Solo se calculan si hay etiquetas de tipo.

## 6. El post-procesamiento, paso a paso

Es la mitad del método y es clásico, no aprendido. Fig. 1, pág. 3.

1. **Gradiente de los mapas H/V** con Sobel, y se toma el máximo de los dos (ec. 6):
   `Sm = max(Hx(px), Hy(py))`. Alto en las costuras entre núcleos.
2. **Marcadores**: `M = σ(τ(q,h) − τ(Sm,k))`, donde `q` es la probabilidad de la rama NP,
   `τ(a,b)` umbraliza a 1 lo que supera `b`, y `σ` recorta los negativos a 0. En palabras:
   *lo que NP dice que es núcleo, menos lo que el gradiente dice que es costura*. Queda un
   germen por núcleo, bien adentro.
3. **Paisaje de energía**: `E = [1 − τ(Sm,k)] · τ(q,h)`. Bajo en las costuras.
4. **Watershed controlado por marcadores**: cada germen crece hasta chocar con el vecino,
   frenado por las costuras.
5. **Tipo por instancia**: la rama NC predice tipo **por píxel**; el tipo del núcleo es la
   **clase más votada** entre sus píxeles. Simple y robusto: un puñado de píxeles mal
   clasificados no cambia el voto.

Los umbrales `h` y `k` se eligieron para dar el mejor resultado. Son dos hiperparámetros
libres del post-procesamiento, no de la red.

## 7. Las métricas que proponen

El paper dedica una sección entera a esto y es una contribución aparte, útil más allá de
núcleos.

**El problema.** Las dos métricas usuales (DICE2 y AJI) castigan de más. La Fig. 4 muestra
dos predicciones que difieren en unos pocos píxeles y sacan DICE2 0.648 contra 0.901. La
razón: si una instancia predicha pisa un poquito la instancia vecina del ground truth, esos
píxeles se penalizan dos veces. Una sola falla de detección arrastra el puntaje.

**Panoptic Quality** (ec. 7), tomada de Kirillov et al.:

```
PQ  =  ────────|TP|────────  ×  ── Σ IoU(x,y) ──
       |TP| + ½|FP| + ½|FN|         |TP|
        \___ Detection Quality ___/  \_ Segmentation Quality _/
```

El emparejamiento con IoU > 0.5 está probado único, así que no hay ambigüedad de matching.
Lo valioso es que **PQ = DQ × SQ** factoriza el puntaje en dos preguntas separables:
*¿encontró los núcleos?* (DQ, que es un F1 de detección) y *¿los dibujó bien?* (SQ, que es
el IoU medio de los que sí encontró). Un modelo puede tener SQ excelente y DQ pésimo.

**Para clasificación** (ecs. 8 y 9) definen un F por tipo que **incluye los errores de
detección**, con α0 = α1 = 2 sobre los errores de clase y α2 = α3 = 1 sobre los de
detección. La ec. 9 lo factoriza igual de lindo: `F = Fd × (exactitud de clase dentro de lo
correctamente detectado)`. Para métodos que solo detectan y no segmentan, el criterio de
acierto es un radio: **6 px a 20× o 12 px a 40×**.

## 8. Qué reportan

**Segmentación** (Tabla III, pág. 11), contra una docena de métodos. HoVer-Net gana PQ en
los tres datasets:

| | Kumar | CoNSeP | CPM-17 |
|---|---|---|---|
| HoVer-Net (PQ) | **0.597** | **0.547** | **0.697** |
| segundo mejor (PQ) | 0.577 (CIA-Net) | 0.460 (Mask-RCNN) | 0.674 (Mask-RCNN) |

**Generalización** (Tabla IV): entrenan en Kumar y aplican a CPM, TNBC y CoNSeP sin
reentrenar. HoVer-Net gana PQ en los tres (0.606 / 0.578 / 0.408), pero conviene mirar el
detalle: en TNBC y CoNSeP, **SegNet+watershed saca mejor DICE** (0.758 vs 0.749 y 0.681 vs
0.664). O sea, SegNet encuentra los píxeles de núcleo igual de bien o mejor; la ventaja de
HoVer-Net está entera en **separar instancias**, que es lo que dice el título.

El número que a nosotros nos importa de esa tabla: sobre CoNSeP, entrenar en el mismo
dataset da PQ 0.547 y entrenar en otro da **0.408**. El cambio de dominio cuesta ~0.14 de
PQ. No es catastrófico, no es despreciable.

**Clasificación** (Tabla V, pág. 15), entrenando en CoNSeP:

| | Fd | epitelial | inflamatorio | fusiforme | miscelánea |
|---|---|---|---|---|---|
| CoNSeP (40×) | 0.748 | 0.635 | 0.631 | 0.566 | **0.426** |
| CRCHisto (20×) | 0.688 | 0.486 | 0.573 | 0.302 | **0.178** |

**Ablaciones** (apéndice A): la loss propuesta mejora todo (§9), el post-procesamiento con
Sobel es mejor que umbralar un pseudo mapa de distancia (PQ 0.597 vs 0.541 en Kumar), y la
rama NC dedicada mejora la clasificación frente a meter las clases en la rama NP (F de
miscelánea 0.333 → 0.426 en CoNSeP).

## 9. Dos cosas que solo salen haciendo la aritmética

**(a) La Tabla A1 tiene las columnas mal rotuladas, y el texto se equivoca leyéndola.** El
paper afirma, sobre la ablación de la loss, que *«there is a significant boost in the SQ»*.
Con los encabezados impresos (DICE, AJI, DQ, SQ, PQ), la fila de la loss propuesta en Kumar
sería AJI 0.770, SQ 0.597, PQ 0.618, que **contradice la Tabla III** del mismo paper (AJI
0.618, SQ 0.773, PQ 0.597). Se resuelve con la identidad `PQ = DQ × SQ`:

- Con los encabezados impresos: 0.773 × 0.597 = 0.461 ≠ 0.618. No cierra.
- Reordenando a (DICE, DQ, SQ, PQ, AJI): 0.770 × 0.773 = 0.595 ≈ 0.597. Cierra, en las
  cuatro filas y en los dos datasets.

La Tabla A2 sí es consistente con la Tabla III, así que la mal rotulada es la A1. Con el
orden corregido, las mejoras reales de la loss propuesta son:

| | DICE | DQ | SQ | PQ | AJI |
|---|---|---|---|---|---|
| Kumar | +0.003 | **+0.020** | +0.002 | +0.016 | +0.010 |
| CoNSeP | +0.007 | **+0.017** | +0.004 | +0.015 | +0.014 |

La ganancia está en **DQ**, la detección, no en SQ. Lo cual es coherente con el mecanismo:
`Lb` mira el gradiente, el gradiente sirve para **cortar**, y cortar bien es encontrar más
instancias. El SQ casi no se mueve porque el contorno de un núcleo ya bien detectado no
depende de esto. El paper tiene razón en el mecanismo y se equivoca al citar su propia
tabla.

**(b) El eslabón débil es justo el que nos toca.** La clase *miscelánea* de CoNSeP agrupa
**necrótico, mitótico y lo no categorizable**, y es la peor de todas: F 0.426 en CoNSeP y
0.178 en CRCHisto, contra 0.6 de las otras. El propio paper lo atribuye a que hay pocas
muestras y mucha variabilidad intra-clase, y lo pone como trabajo futuro. Nosotros tenemos
una tarea de **tasa mitótica** y una de **necrosis**: si alguien propone usar HoVer-Net para
contar mitosis, este número es la respuesta, y es un no.

## 10. Lo que ya existe en el servidor (verificado el 31-jul)

Esto no estaba en el encuadre del encargo y cambia la conversación. En
`/media/administrador/Storage1/sdonoso/hover_net/` (owner **`sgaete`**, fuera de nuestro
workspace, **solo lectura para nosotros**) hay una instalación funcionando:

| Qué | Estado verificado |
|---|---|
| Repo | Clonado el 29-jul. Env conda propio `hovernet`. |
| Pesos | `hovernet_fast_pannuke_type_tf2pytorch.tar`, **PanNuke**, `model_mode=fast`. Es el mismo checkpoint que usa SI-MIL. |
| Clases (`type_info.json`) | 6: `nolabe`, `neopla`, `inflam`, `connec`, `necros`, `no-neo`. |
| Corridas | Jobs 4708 y 4709 fallaron; **4714 completó una lámina**: `TCGA-3C-AALI-01Z-00-DX1`, 101184×74432 px, `--proc_mag=40`, batch 32. De 05:12 a 08:48 del 30-jul = **3 h 36 min**. |
| Desglose del costo | Post-procesamiento 4504 s (75 min, CPU, 16 workers) y guardado 599 s (10 min). La inferencia en GPU es ~2 h; el watershed del §6 se lleva un tercio del total. |
| Cola preparada | `dataset/tcga_flat` con **881 láminas** de TCGA listas para barrer. |
| Post-proceso propio | Export a QuPath de una región 4096×4096 con 7798 núcleos (jobs 4739/4740), overlay de 1024 px (4738), y un `viz_hv_maps.py` del 30-jul a las 12:50. |
| Modo tile | `run_infer_tile.slurm` ya escrito, con `--save_raw_map`, y un comentario que dice que es la única forma de quedarse con los mapas H/V crudos. |

**El motivo del crash de 4708/4709 queda registrado**: `CUDA error: no kernel image is
available for execution on the device`, o sea un PyTorch compilado sin kernels para la
arquitectura de la A6000. Está resuelto en el env `hovernet`; si alguna vez montamos algo
parecido en nuestro workspace, es el primer sospechoso.

**Y hay un archivo que vale más que todo lo anterior:** en la raíz de ese repo está
`129741.bif - GDT.geojson`, con **61 anotaciones de región dibujadas a mano** (formato de
exportación de QuPath), en vocabulario clínico y en español:

| Etiqueta | Regiones |
|---|---|
| Mitosis | 26 |
| Nucleos alto grado | 14 |
| necrosis | 6 |
| Immune cells | 5 |
| Tumor | 5 |
| Tejido Adiposo | 2 |
| Negative | 2 |
| Stroma | 1 |

Verificado contra nuestros datos: **`129741.pt` está en `features/pt_files`**, la lámina
tiene sus `.bif` en `wsi/129741/` (H&E más RE, RP, HER-2, KI67 y el informe), aparece en los
CSV de etiquetas de varias tareas y **está en los splits de las tres tareas del B7**,
incluidos nuestros `_ci_reform` locales del job 4589. Es decir: es una lámina para la que ya
tenemos modelo entrenado, mapas de atención y expertos medidos.

**No sabemos quién la anotó.** El vocabulario y el idioma sugieren un patólogo, pero eso hay
que preguntarlo, no suponerlo.

## 11. Qué nos sirve de esto, y qué no

**Sirve, y es el hilo del encargo.** Desde OBJ-A arrastramos que los nombres de tejido de
los expertos y los slots son **lectura visual nuestra**, sin anotación que los respalde
([[mammoth-interpretabilidad-objA]], [[slot-unidad-de-morfologia]]). HoVer-Net da un
vocabulario **cuantitativo y con nombre** por parche: cuántos núcleos neoplásicos, cuántos
inflamatorios, qué forma tienen, cómo están mezclados en el espacio. Eso es exactamente el
insumo de las 246 features PathExpert de SI-MIL, y es lo que permitiría decir *«el slot
e28·s4 se concentra en parches con densidad alta de núcleos neoplásicos y baja de
conectivos»* en vez de *«se concentra en lo que a nosotros nos parece epitelio»*.

**No sirve para lo que uno esperaría a primera vista, y conviene decirlo antes que lo
pregunten:**

- **Tipo de núcleo no es tipo de tejido.** HoVer-Net etiqueta la célula de la que viene cada
  núcleo. El nombre del tejido de un parche sigue siendo una **derivación** nuestra a partir
  de conteos y proporciones, no una respuesta del modelo. Cambia la naturaleza del reclamo
  (deja de ser impresión visual y pasa a ser una estadística reproducible) pero **no
  reemplaza la firma de un patólogo**.
- **No cuenta mitosis de forma usable** (§9b). Ni necrosis con confianza.
- **No ve microcalcificaciones.** Segmenta núcleos; el calcio no es un núcleo. Para el eje
  de microcalcificaciones esto no aporta nada, y menos aún para el oxalato invisible en H&E
  ([[luz-polarizada-oxalato-birrefringencia]]).
- **La magnificación sigue siendo el bloqueo.** La corrida de sgaete usa `--proc_mag=40`, que
  es la magnificación nativa de TCGA. Nuestra cohorte privada está a **≈20× en level0**
  ([[cohortes-magnificacion-fisica]]): pedirle 40× obliga a interpolar detalle que la lámina
  no tiene. Y la evidencia del propio paper de qué pasa al bajar a 20× es la columna CRCHisto
  de la Tabla V, donde el F fusiforme se cae de 0.566 a 0.302. Está confundida con el cambio
  de centro y de protocolo de anotación, así que es indicio y no medición, pero apunta en la
  dirección incómoda.

## 12. Lo que costaría correrlo acá

Ya no hay que estimarlo desde el paper: hay una medición nuestra, en nuestro hardware.

- **Lámina completa: 3 h 36 min** en la A6000 (job 4714). Barrer las 881 de TCGA son
  **~3170 h de GPU ≈ 132 días corridos**. Con una sola GPU compartida, eso no existe.
- **Coherencia con el paper**: 11.04 s por megapíxel en 2019 con convolución válida, 1.97 s
  con convolución con padding (5.6× más rápido, que es el `model_mode=fast` que sgaete usa).
  Escalado al área de esa lámina da ~4 h contra las 3.6 h medidas. Los números del paper
  traducen bien; no hay sorpresa de hardware que nos salve.
- **La asimetría que lo vuelve viable**: para nombrar tejido no necesitamos la lámina
  entera, solo los parches que el modelo destacó. SI-MIL corre HoVer-Net sobre todo porque
  necesita entrenar su rama sobre todos los parches; **nosotros solo queremos leer los
  top-K**. Veinte parches de 256 px son 1.3 Mpx, contra los 7530 Mpx de la lámina: es un
  factor ~5700. Del orden de segundos de GPU por lámina en vez de horas, y las 1176 láminas
  únicas del barrido del encargo 1 caerían en una franja de horas, no de meses. La
  herramienta para eso (`run_infer_tile.slurm` con `--save_raw_map`) **ya está escrita en el
  repo de sgaete**.
- Cualquier corrida nuestra va por `sbatch` (regla 1), en nuestro workspace, y con
  `squeue` antes: sgaete estuvo usando la GPU para esto el 29 y el 30 de julio.

## 13. Qué no se afirma

- **No se afirma que HoVer-Net mejore ninguna métrica de OncoMets.** No es un clasificador
  de láminas ni compite con CLAM. Es instrumentación descriptiva.
- **No se afirma que el geojson de la lámina 129741 sea de un patólogo**, ni que sea
  exhaustivo. Son 61 regiones dibujadas, no una anotación densa de la lámina.
- **No se afirma que las clases de PanNuke apliquen limpio a mama.** PanNuke incluye mama,
  pero los números del paper son de colon (CoNSeP) y multi-órgano (Kumar); el checkpoint que
  está en el servidor no lo evaluamos nosotros contra nada.
- **No se toca nada de `sgaete/hover_net/`.** Todo lo del §10 es lectura.
- El 3 h 36 min es **una lámina, una vez**. Sirve para el orden de magnitud, no como
  promedio.

## 14. Preguntas para llevar

1. **¿Sabíamos que Sebastián ya lo tiene corriendo?** Si el encargo era leer el paper para
   discutirlo, la discusión cambia: no es *si* se prueba, es *qué* se hace con las 881 de
   TCGA en cola y quién las corre. Y hay que evitar duplicar trabajo.
2. **¿Quién anotó `129741.bif - GDT.geojson` y hay más?** Es la pregunta más cara del
   documento. Una sola lámina anotada por región ya permite contrastar contra ella nuestros
   mapas de atención y de slots del job 4589, que es literalmente el sign-off que venimos
   arrastrando desde OBJ-A. Un puñado de láminas más lo convertiría en una validación.
3. **¿La lámina entera o solo los parches destacados?** Es la diferencia entre 132 días y
   unas horas (§12), y depende de para qué se quiere: entrenar algo tipo SI-MIL necesita
   todo; nombrar lo que ya destacamos necesita solo el top-K.
4. **¿Se acepta acotarlo a TCGA?** Misma pregunta que quedó abierta en SI-MIL §8, y por el
   mismo motivo: la cohorte privada está a 20× y la corrida está parametrizada a 40×.
5. **La clase miscelánea (§9b) hunde mitosis y necrosis.** Si la expectativa de alguien es
   contar mitosis con esto, mejor bajarla ahora.

---

## Anexo: números del paper, por si hace falta el detalle

**CoNSeP**, el dataset que introducen: 41 tiles de 1000×1000 a **40×**, sacados de 16 WSI de
adenocarcinoma colorrectal (un paciente cada una), escáner Omnyx VL120, UHCW. **24 319
núcleos** anotados uno por uno por dos patólogos, con revisión cruzada y consenso. Siete
categorías originales, agrupadas a cuatro para los experimentos (epitelial normal +
maligno/displásico → *epitelial*; fibroblasto + músculo + endotelio → *fusiforme*;
inflamatorio; miscelánea = necrótico + mitótico + no categorizable).

**Entrenamiento**: TensorFlow 1.8, dos GTX 1080 Ti. Inicialización con pesos de ImageNet,
50 épocas entrenando solo los decoders (~120 min) y 50 afinando todo (~260 min), total ~380
min. Adam, lr 1e-4 bajando a 1e-5 en la época 25, repetido en el fine-tuning. Batch 8 y
luego 4 por GPU. Entrada RGB normalizada a [0,1]. Aumentación: flip, rotación, blur
gaussiano y de mediana.

**Inferencia**: 11.04 s por tile de 1000×1000, contra 106.98 s de Mask-RCNN (9.7× más
rápido). Con convolución con padding baja a 1.97 s (5.6×). Todo con batch 1 en una GPU de
12 GB, y los propios autores avisan que el número depende del hardware.
