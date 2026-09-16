# Sprint 10 (B10) — mapa

> Abierto el **8-sep-2026**. Origen: la reunión con Sebastián que siguió a la presentación del B9
> ante Benjamín (7-sep). Transcripción literal en
> [`../B9_sprint9/reunion_sebastian.txt`](../B9_sprint9/reunion_sebastian.txt).
>
> **Regla de este documento: es un índice, no un almacén.** Cada decisión vive en exactamente un
> lugar, su archivo, y acá aparece con una línea que alcanza para juzgar si hay que abrirlo. Si
> algo se explica dos veces, la copia de acá es la que sobra. Formato fijado en `CLAUDE.md`
> §"Formato de `objetivos_sprintN.md`".
>
> El sprint anterior cerró el **8-sep-2026**: [`../B9_sprint9/objetivos_sprint9.md`](../B9_sprint9/objetivos_sprint9.md).

---

## Destino

Dejar medido **si HoVer-NeXt solo, sin la marca del patólogo, reencuentra los núcleos que el
patólogo eligió**, y con qué carga de superficie.

El B10 llega a su fin cuando ese número existe con su nulo y su escalera de carga, cuando la
pregunta del score está contestada contra el protocolo CAP, y cuando la localización del CDIS tiene
una medición en vez de una impresión.

### El reparto de tareas, que es lo primero que fijó la reunión

**Sebastián toma la región de la tasa mitótica. Ernesto toma el grado nuclear.** Textual: «para no
repetir la tarea, para dividirnos bien las tareas; el tema de la región para la tasa mitótica es algo
que igual iba a estar viendo». Resuelve, **para este eje**, el solape que `CLAUDE.md` arrastra desde
el 3-sep ([[sgaete-yolo-mitosis-solapamiento]]). No lo resuelve para los otros tres.

### Los tres encargos, textuales

1. **Replicar el experimento del B9 sin la marca del patólogo**: «podríai replicar el experimento
   solamente con HoVer-Net y ver si te da lo mismo, las mismas anotaciones del patólogo al final».
2. **Investigar cómo se determina el score** cuando en una lámina conviven núcleos de grados
   distintos: «uno intuitivamente piensa en, ya, la mayoría gana, pero pueden haber sutilezas o
   reglas al momento de hacer el scoring».
3. **El CDIS como prerrequisito de la gradación**: «una vez identificado el CDIS, el grado nuclear
   sí o sí va a depender de la tarea de localización del CDIS», evaluando por ahora solo sobre
   láminas anotadas.

**Cadencia**: objetivos cortos y reunión semanal. La próxima es **el martes**.

## Notas

- **Dominio**: morfometría nuclear sobre la segmentación de HoVer-NeXt y su cruce contra anotación
  de patólogo. Ortogonal al eje de rendimiento de MIL, cerrado en los Hallazgos 11-14 de
  `CLAUDE.md`.
- **Skills a consultar**: `@grilling` antes de pre-registrar, `@slurm-submission` antes de cualquier
  `sbatch`, `@csv-audit` si entra un CSV nuevo, `@knowledge-audit` al documentar, `@humanizer-es`
  para el guion.
- **Restricciones permanentes**: `anotaciones/`, `hover_net/`, `clam_testing/`, `clam_environ/`,
  `clam_ensemble/`, `MitosisDetection/` y `hover_next_reference/` son **READ-ONLY**; regla 9 antes
  de tocar código de experimento; workaround **L** antes de leer un `PD (Priority)` como espera
  normal; workaround **J** para cualquier proceso CPU largo; workaround **B** siempre (binario
  absoluto del env).
- **Positivos parciales**: el geojson del patólogo marca donde la evidencia es clara, no todo lo que
  existe. **No se calcula precisión, F1 ni PQ contra él**, en ningún eje. Se hereda del B9 y no se
  renegocia.
- **Unidades**: conviven marcas, núcleos, parches y mm². Toda tabla declara la suya.

---

## Decisiones tomadas

Una línea por asunto cerrado. El detalle está en el enlace.

- **El set de anotaciones CRECIÓ y el B9 nunca lo vio** (8-sep, verificado contra el archivo) —
  `anotaciones/` tiene **23 geojson / 22 láminas**, no 13/12: hay **10 archivos nuevos con fecha
  27-ago-2026**. Contra ese set los números que citó Sebastián cuadran exacto:
  `Nucleos alto grado` **99** en 10 láminas, `Nucleos mod grado` **84** en 10, y CDIS
  (`CDIS_solido` 10 + `DCIS` 6 + `CDIS_papilar` 6 + `CDIS_cribiforme` 5 + `CDIS_micropapilar` 3)
  = **30 en 10 láminas**. Tres correcciones para llevarle: `NucleosBajoGrado` son **16 y no 25**
  (los 25 cuentan la segunda exportación de la 103762, el duplicado que el B9 ya había cazado), el
  grado vive en **22 láminas y no en 12** (21 medibles más la Br0244), y de las 30 láminas que
  mencionó ahora **faltan 8**, no 18. *Corregido el 11-sep: decía «20 láminas», que sumaba alto
  (10) y moderado (10) y dejaba fuera las 2 de bajo ([[conteo-de-grupo-es-union]]).* Detalle en [[anotaciones-patologo-qupath]].
- **Las marcas de grado siguen la etiqueta de PLEOMORFISMO de la lámina, no el grado nuclear del
  CDIS** (8-sep, verificado contra `environ/csv/`) — las **10** láminas con marcas `moderado` son
  **10 de 10 `score_2`**; la única con marcas `bajo` que tiene etiqueta es **`score_1`**; 6 de 8 con
  marcas `alto` son `score_3`. Y **8 de las 21 láminas con marcas de grado tienen
  `CDIS_presente = no`**, así que ahí las marcas no pueden ser grado nuclear de CDIS. Consecuencia:
  la cadena CDIS → grado nuclear vale para el grado nuclear del CDIS, pero **el material anotado
  mide pleomorfismo invasivo**, cuya máscara (`Tumor`, 162 regiones en 21 láminas) ya existe.
  **Es pregunta para Sebastián el martes**, porque decide qué máscara corresponde.
  [[marcas-grado-son-pleomorfismo-de-lamina]].
- **La pregunta del score se contesta con un PDF que ya está en `papers/`** (8-sep) —
  `Breast.Invasive.Bx_1.2.0.0.REL_CAPCP.pdf`. Pleomorfismo invasivo: score 1 = «little increase in
  size in comparison with normal breast epithelial cells», score 3 = «marked variation in size and
  shape», o sea **tamaño relativo al epitelio normal más dispersión**, y **no** una mayoría ni un
  conteo. Grado nuclear de CDIS: **6 rasgos** con cortes cuantitativos de tamaño, **1,5 a 2×** el
  núcleo epitelial ductal normal en grado I y **>2,5×** en grado III. El único que sí es un conteo
  por área es el **mitótico**, que es la parte de Sebastián. Consecuencia de método: el descriptor
  fiel al CAP es la **razón contra epitelio normal**, no el percentil intra-lámina que usó el B9.
  [[cap-scoring-pleomorfismo-y-grado-cdis]].
- **Los costos de incorporar las láminas nuevas, medidos y no estimados** (8-sep) — las 9 láminas
  nuevas numéricas tienen `.bif` en `/media/.../wsi/<id>/` y `.h5`/`.pt` en `features/`. Falta
  HoVer-NeXt (**~103 min** de GPU para 11 láminas en el B8) y los offsets (**~22 min** de CPU para
  11, `logs/a3_offsets_desatado.log`). El `.slurm` acepta `SLIDES_OVERRIDE` y el alineador recibe
  `--geojson` por argumento, así que **solo el driver de shell necesita un fix**: 5 de los 9 geojson
  nuevos se llaman `<id>.bif GDT.geojson`, sin el ` - ` que `run_a3_offsets.sh` tiene cableado.
- **Hay checkpoint de CDIS con la cabeza verdadera, y no hay familia 5fold** (8-sep, verificado) —
  `environ/results_modelo_pth_balance/carcinoma_ductal_insitu_presente_pth_balance_s1/s_0_checkpoint.pt`,
  **un solo fold**, con su `splits_0.csv` al lado, que permite declarar el tier de cada lámina
  anotada. `results_modelo_combined_5fold/` solo tiene `mitotic_rate`, así que **no existe brazo de
  folds limpios para CDIS sin entrenar**. El brazo con cabeza verdadera **no es opcional**: el
  `json_out` lee la rama de la clase *predicha* y eso ya produjo un 0,500 exacto en otro eje
  ([[rama-de-atencion-decide-el-resultado]]).
- **O1, O2 y O3 EJECUTADOS** (9-sep) — los tres cerrados a tiempo para la reunión del martes.
  **O2**: el CAP contesta el score y corrige el descriptor
  ([`score_grado/estudio_score.md`](score_grado/estudio_score.md)); no hay regla de cantidad, el eje
  es la **dispersión**, y el protocolo **no dice** qué hacer cuando el grado varía dentro del mismo
  carcinoma. **O1**: el tamaño reencuentra el **alto** grado y no el **bajo** (en ~4 mm²/lámina, 41
  de 76 alcanzables en `alto`, 12 de 53 en `moderado`, **0 de 16** en `bajo`), muy por encima del
  nulo, con denominador alcanzable **145 de 187** y los dos descriptores dando idéntico por ser
  monótonos entre sí ([`grado_sin_marca/resultados.md`](grado_sin_marca/resultados.md)). **O3**: la
  atención **sí** cae sobre el CDIS (AUC mediana **0,755** con la rama verdadera, 9 de 9 por encima
  de 0,5), pero la única lámina en `test` tiene 2 parches positivos y su IC contiene 0,5
  ([`cdis_localizacion/resultados.md`](cdis_localizacion/resultados.md)).
- **La B25-158899 re-medida: el universo no era la causa** (10-sep) — confinada a su región
  anotada da **0,201** (rama `si`) contra 0,198 en la lámina entera, así que la hipótesis cae por la
  regla pre-declarada. Es la única de las diez al revés y **la única que el fold nunca vio**, y su
  offset tiene `alineada: false` desde el B8, igual que la 164001, que da 0,926. Consecuencia: **la
  localización de O3 descansa en `train` y `val`**; en láminas nuevas no está mostrada
  ([`cdis_localizacion/resultados.md`](cdis_localizacion/resultados.md) §2 y §3.b).
- **O1 no declaró dos cosas, y ninguna mueve el titular** (10-sep) — el universo de las dos
  láminas con dos regiones de escaneo (129741 y B25-158899 se ordenaron sobre la lámina entera) y
  las dos con `alineada: false` (164001 y B25-158899). Confinar lleva `alto` de 27 · 41 · 57 a
  29 · 41 · 60 en N = 200 · 500 · 2000; sacar las no alineadas deja N=500 en 52 de 140. Declarado,
  sin re-correr ([`grado_sin_marca/resultados.md`](grado_sin_marca/resultados.md) §6.a).
- **O1 y O3 tienen forma presentable, y el doc de la reunión está escrito** (11-sep): dos figuras
  con sus CSV, dibujadas por `scripts/b10_figuras_o1_o3.py`, que verifica cada número contra los
  `resultados.md` antes de dibujar, y [`reunion_martes.md`](reunion_martes.md) con las cinco
  preguntas para Sebastián. Al armarlo se corrigieron dos números: el grado vive en **22** láminas
  y no en 20, y el IC de la 126504 cierra en **1,111** y no en 1,110
  ([`figuras/`](figuras/README.md)).
- **O1 se queda en la lámina entera, y `sgaete` es Sebastián** (14-sep) — las dos preguntas que
  quedaban con Ernesto, contestadas. **No** se re-corre O1 confinado a la región anotada: el titular
  no se mueve y la lámina entera es lo que tendría una lámina nueva sin anotar
  ([`reunion_martes.md`](reunion_martes.md) §6). Y son **dos Sebastianes**: `sgaete` es Sebastián
  Gaete, el supervisor que escucha el deck, mientras que `sdonoso` es la cuenta compartida y
  Sebastián Donoso; los cuatro directorios ajenos read-only son **del supervisor**
  ([[sgaete-es-sebastian-gaete-supervisor]]).
- **El deck de la reunión del martes, construido** (11-sep, plan aprobado y deck construido el
  14-sep) — decisiones de Ernesto: **español** salvo la portada, **7 láminas** (portada ·
  OBJETIVOS · O1 · O2 · O3 · cinco preguntas · Tareas), gráficos con **shapes nativas** y una sola
  fila de tareas, **dispersión contra epitelio normal**. Los números salen de `datos_o1()` y
  `datos_o3()` del script de figuras, que ya verifican contra los `resultados.md`. Vive en
  [`presentacion_b10/`](presentacion_b10/README.md), con el QA automático en cero. **Las láminas se
  miraron en la sesión 59** (M1-M6 de `auditoria_coherencia/hallazgos.md`): seis defectos
  corregidos, uno de ellos del visor (LibreOffice dibuja una sombra del theme que PowerPoint no), y
  el `.pptx` regenerado reemplaza al que se le mandó a Ernesto.
- **El deck del 15-sep se rehace más visual, planificado y sin ejecutar** (16-sep) — a Ernesto le
  faltaban imágenes de los núcleos de HoVer-NeXt y resultados a la vista. Decisiones: mismo período
  y mismo archivo, **11 láminas** (las 7 intactas más cuatro de imagen: qué detecta HoVer-NeXt, O1
  sobre una lámina, O1 núcleo a núcleo y los mapas de atención de O3), todo en CPU y con gates
  contra los números ya medidos. Plan en
  [`presentacion_b10/plan_deck_visual.md`](presentacion_b10/plan_deck_visual.md). Sesión 61: la
  selección de recortes corrió con sus gates en verde; el render y las cuatro láminas siguen sin hacer.
- **D2 no se pudo ejecutar y no se reemplazó** (9-sep) — **0 de 187** marcas de grado caen dentro de
  ninguna anotación, de ninguna clase. El brazo con máscara queda declarado **degenerado por
  construcción** y qué región corresponde es **pregunta para Sebastián**.
  [[marcas-grado-fuera-de-toda-region-anotada]].
- **Las 9 láminas nuevas quedaron instrumentadas** (9-sep) — HoVer-NeXt job 5402 (OK=9, 116 min) y
  offsets **9 de 9 con `alineada: true`**. Hay 21 láminas medibles y 187 de las 199 marcas.
- **El plan del sprint, escrito y sin ejecutar** (8-sep) — cuatro decisiones de Ernesto: **D1**
  encolar HoVer-NeXt de las nuevas ya y medir sobre las 12 mientras corre; **D2** el experimento sin
  la marca se restringe a la **máscara `Tumor`**; **D3** el primario es **el núcleo** (recall de las
  marcas en los N más grandes, como escalera de carga) y la zona es secundaria; **D4** el eje CDIS
  se limita a **medir la atención que ya está en disco**, sin BRACS y sin entrenar. **Nada de esto
  se ejecutó**: lo toma una sesión limpia.

---

## Todavía sin especificar

Niebla: se intuye que viene, pero todavía no se puede formular con precisión. El test para sacar
algo de acá **no es poder responderlo, es poder enunciarlo**.

- **Qué es «epitelio normal» en nuestras láminas.** El CAP define el tamaño **contra** él y no
  tenemos anotación de epitelio normal. El proxy candidato son los `epithelial-cell` fuera de toda
  región anotada, pero no está validado y confunde epitelio normal con epitelio no marcado.
- **Si el grado se puede medir en láminas sin marca pero con etiqueta.** Es el paso que Sebastián
  puso después («extrapolarlo a otras WSI donde no tenemos la marca pero sí la etiqueta»), y depende
  de tener el CDIS bien localizado, que es justo lo que falta.
- **Qué forma tiene la zona que se le propone al patólogo** para grado, y si es la misma forma que
  para mitosis. Se hereda del B9 sin resolver.
- **El sign-off del patólogo sobre los nombres de tejido.** Se arrastra desde OBJ-A del B7
  ([[mammoth-interpretabilidad-objA]]).

### Pendiente sharp (ya se puede enunciar, falta pre-registro)

- **¿La necrosis que señala PanNuke coincide con los polígonos del patólogo?** Encargo 3 de
  Sebastián, heredado del B9. Unidad región contra punto, nulo por traslación, prerrequisito
  bloqueante de unificar el vocabulario (`necrosis` / `Necrosis` / `Comedonecrosis`). **7 a 9 h** de
  GPU estimadas por área de canvas. Exige que Ernesto lo pida y que la GPU se libere.
- **El brazo `ckpt_limpio` de la atención sobre mitosis**, que el B9 dejó pendiente y que es el
  control de honestidad del 0,809.
- **¿El Δ del job 4589 en CDIS `_ci_reform` sobrevive a semillas nuevas?** Arrastrado del B8.
  Δbal_acc **+0.074 ± 0.033 (5/5 folds)**. La réplica **exige semillas nuevas** y entra por **regla
  9.b** con pre-registro, branch y `reviewer`.
- **El análisis B3**: rehacer el recorte de la lámina 15 con el CLAM plano del gate y compararlo
  contra el brazo Mammoth. CPU.

---

## Fuera de alcance

Ruled out de **este** esfuerzo. No gradúa: vuelve sólo si se redibuja el destino, y entonces como
esfuerzo nuevo.

- **Precisión, F1 y PQ / bPQ / mPQ contra el geojson del patólogo.** Heredado del B9. No son
  computables contra positivos parciales, y no es una limitación de presupuesto.
- **BRACS y cualquier otro dataset público de CDIS segmentado.** Sebastián lo propuso; Ernesto lo
  dejó fuera del B10 (D4). Bajarlo exigiría además autorización explícita (regla E.a).
- **Entrenar los 5 folds de `carcinoma_ductal_insitu_presente_combined`.** Los splits existen y los
  checkpoints no. Fuera por D4, no por imposible.
- **El top-K de parches como forma de restringir.** A K fijo gana siempre la máscara más grande
  ([[carga-fija-no-k-fijo]]). La unidad correcta es **carga en mm²**.
- **La región de la tasa mitótica.** Es de Sebastián por el reparto de arriba.
- **SI-MIL** y **el eje de rendimiento de Mammoth** (Hallazgos 11-14). Heredados, sin premisa nueva.

---

## Qué no se afirma

- Que las marcas del patólogo sean **todos** los núcleos de ese grado que hay en la lámina. Son
  ejemplares que eligió, y el B9 midió que sus percentiles son altos en los tres grados.
- Que el proxy de «epitelio normal» sea epitelio normal. Es epitelio **fuera de región anotada**, y
  eso no es lo mismo.
- Que el área de una instancia de HoVer-NeXt sea comparable entre clases. El umbral de foreground
  está afinado por clase y `epithelial-cell` es el más erosionado de las siete
  (`ejes_nucleares/resultados.md` §2.d).
- Que las 12 ni las 21 láminas alcancen. El grado sigue confundido con la lámina.
- Que la atención de CLAM localice el CDIS en láminas que el modelo no vio. Las dos que hay no lo
  muestran: una no mide y la otra va al revés con el offset sin verificar.
- Que `sgaete` no esté haciendo esto mismo. El reparto de la reunión cubre **mitosis**; los otros
  tres solapes siguen abiertos.
