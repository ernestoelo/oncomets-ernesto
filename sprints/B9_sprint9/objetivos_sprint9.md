# Sprint 9 (B9) — mapa

> Abierto el **25-ago-2026**. Origen: la reunión con Sebastián que cerró el B8, donde Ernesto
> trajo tres objetivos y un encuadre que reordena el criterio de éxito.
>
> **Regla de este documento: es un índice, no un almacén.** Cada decisión vive en exactamente un
> lugar, su archivo, y acá aparece con una línea que alcanza para juzgar si hay que abrirlo. Si
> algo se explica dos veces, la copia de acá es la que sobra. Formato fijado en `CLAUDE.md`
> §"Formato de `objetivos_sprintN.md`".
>
> El sprint anterior cerró el **25-ago-2026**: [`../B8_sprint8/objetivos_sprint8.md`](../B8_sprint8/objetivos_sprint8.md).

---

## Destino

Dejar **medido en qué tareas HoVer-NeXt aporta y en cuáles es ciego**, y entregar la primera
versión de una **zona propuesta al patólogo** con su número al lado.

El B9 llega a su fin cuando esa zona existe como entregable (una lámina, una tabla y un guion) y
cada eje del inventario tiene un veredicto medido o un NO-GO argumentado.

### Los tres objetivos de la reunión, textuales

Los pidió **Ernesto**, trayendo lo acordado con Sebastián, en la reunión que cerró el B8
(**25-ago-2026**):

1. **Escalar la tarea de mitosis con HoVer-NeXt a más WSI etiquetadas por el patólogo.**
2. **Evaluar HoVer-NeXt para la tarea de necrosis.**
3. **Evaluar la implementación de nuevas métricas para la tarea de mitosis.**

**Encuadre**: ahondar en HoVer-NeXt y hacer más pruebas que ayuden a **demarcar una zona
importante para el patólogo**. Es el argumento del 14-ago convertido en objetivo del sprint: se
evalúa con las métricas del paper y con utilidad para el patólogo, **no con AUC**.

## Notas

- **Dominio**: detección nuclear sobre WSI y su cruce contra anotación de patólogo. Ortogonal al
  eje de rendimiento de MIL, cerrado en los Hallazgos 11-14 de `CLAUDE.md`.
- **Skills a consultar**: `@slurm-submission` antes de cualquier `sbatch`, `@csv-audit` si entra
  un CSV nuevo, `@grilling` antes de pre-registrar, `@knowledge-audit` al documentar,
  `@humanizer-es` para el guion.
- **Restricciones permanentes**: `anotaciones/`, `hover_net/`, `clam_testing/`, `clam_environ/`,
  `clam_ensemble/` y `hover_next_reference/` son **READ-ONLY**; regla 9 en todo lo que toque entrenamiento; workaround
  **L** antes de leer un `PD (Priority)` como espera normal; workaround **J** para cualquier
  proceso CPU largo.
- **Unidades**: en este sprint conviven cuatro y mezclarlas es el error más fácil. **Marcas** (94),
  **parches** (28 en la 129741), **detecciones** (732) y **polígonos** (472 anotaciones). Toda
  tabla declara la suya.
- **Positivos parciales**: el geojson del patólogo marca donde la evidencia es clara, no todo lo
  que existe. **No se calcula precisión ni F1 contra él**, en ningún eje.
- **La plantilla oficial cambió** el 25-ago: `[AAAAMMDD] [Nombre Apellido] [Proyecto].pptx`, en
  inglés y con 4 láminas ejecutivas. Spec en [`../../docs/plantilla_oficial.md`](../../docs/plantilla_oficial.md).
  **No construir un deck con Deep-LLM-V ni con `Presentation()`.**

---

## Decisiones tomadas

Una línea por asunto cerrado. El detalle está en el enlace.

- [**La atención de CLAM cae sobre las mitosis, en las doce**](atencion_12_laminas/resultados.md)
  (2-sep, CPU) — pre-registrado en [`prereg.md`](atencion_12_laminas/prereg.md) **antes** del
  código. Primario, las **nueve** con `score_1/2/3` y media sin ponderar sobre láminas: **AUC
  0,809 ± 0,127** (cabeza de mitosis) y **0,745 ± 0,183** (gate invasivo), **9 de 9 por encima
  de 0,5** y `p` por traslación rígida bajo 0,05 en las cuatro de mayor `n`. El **gate de
  regresión del B8 reproduce a 1e-6**. **La fuente está contaminada por construcción** (el
  `json_out` promedia los cinco folds) ⇒ el número es optimista y el brazo `ckpt_limpio`
  **queda pendiente**. La **escalera de área**, que es la pregunta de la reunión, **no se
  corrió**.
- **La geometría de HoVer-NeXt, contestada** (1-sep verificada, 2-sep escrita a `sgaete`) —
  tesela **256 px a 20×**, paso **248**, escribe el centro **248**; en nuestras láminas
  **119 µm = 0,0142 mm²**, el mismo tamaño físico que un parche de CLAM ⇒ **3 mm² ≈ 212
  parches** y las doce juntas **706,1 mm²** (verificado por el driver, no sólo derivado).
  Detalle en [`insumos_json_out.md`](atencion_12_laminas/insumos_json_out.md) §4.
- [**El cruce de las 94 marcas**](mitosis_12_laminas/cruce_94.md) (25-ago, CPU) — HoVer-NeXt
  reencuentra **26 de las 94 marcas** de mitosis a 30 µm sobre las doce láminas anotadas
  (**27,7 %**), plano de 7,5 a 50 µm. La **129741 aporta 13 de esos 26 y es el mejor caso, no el
  típico**: sin ella el agregado baja a **19,1 %**. Cierra el objetivo 1 en su parte medible.
  Regresión de la 129741 idéntica a la del B8 en las diez tolerancias.
- **La región anotada no está del mismo lado en las dos láminas multi-región** (25-ago) — en la
  129741 el patólogo anotó la de **abajo** y en la B25-158899 la de **arriba**, así que la
  constante escalar `Y_CORTE_REGION` de `scripts/techo_atencion_topk.py:45` **no generalizaba**, y
  no por faltarle un valor por lámina. Queda el **intervalo** por lámina, verificado contra las
  marcas. Detalle en [`cruce_94.md`](mitosis_12_laminas/cruce_94.md) §3.c.
- [**El inventario de tareas contra las que HoVer-NeXt se puede medir**](hovernext_tareas/inventario_tareas.md)
  (25-ago) — **ocho ejes**: mitosis (medido), necrosis (GO, GPU), pleomorfismo y tumor/estroma
  (**GO y ya en disco**, CPU), infiltrado inmune (`n=7`, no sostiene número), y **tres NO-GO
  argumentados** por falta de clase o de unidad: permeaciones vasculares, microcalcificaciones y
  arquitectura. Es lo que Ernesto pidió primero.
- **Los `n` del vocabulario del patólogo se cuentan sobre DOCE geojson, no trece** (25-ago) — el
  glob de `anotaciones/` devuelve **13** archivos y el extra es una segunda exportación de la
  103762. Contarlo inflaba cuatro clases: `Tumor` 108→**98**, `AreaSolida` 54→**45**, `AreaTubular`
  30→**25**, `NucleosBajoGrado` 25→**16**. Ya estaba cazado para `Mitosis` (94, no 95).
- **Las siete clases de Lizard y los `pinst_pp.zip` están en disco para las doce** (25-ago,
  verificado) — gitignored por peso, **no ausentes**. Eso mueve los ejes de pleomorfismo y de
  tumor/estroma a **CPU post-hoc**. Lo que **no** está es el raw: las once corrieron sin
  `--keep_raw`.
- **El deck del período, especificado y ESCRITO** (26-ago) — cuatro decisiones de Ernesto:
  láminas en **inglés** pero guion hablado en **español**, proyecto **Nuclear Detection** en el
  tercer corchete y en la cejilla, período **25/08/2026 a 08/09/2026**, y **dos** láminas de
  contenido (el cruce de las 94 y el inventario de los ocho ejes). El hallazgo de método es que
  esta plantilla **se rellena en sitio** y no se reconstruye, al revés que los seis decks
  anteriores: [`../../docs/plantilla_oficial.md`](../../docs/plantilla_oficial.md) §7.
  **ESCRITO el 26-ago** en [`presentacion_b9/`](presentacion_b9/): cinco láminas, generador,
  guion y README, con la auditoría y el barrido de estilo limpios. Salieron **cinco** y no seis
  (la aritmética del handoff no cerraba) y el QA corrigió tres datos, entre ellos que las 107
  regiones con grado están en **las 12** láminas y no en 8 ([[conteo-de-grupo-es-union]]). Las
  restricciones que sólo aparecieron al rellenar la plantilla de verdad quedaron en
  `plantilla_oficial.md` §7.c.

  > **ADDENDUM 27-ago-2026 — Ernesto cambió tres de las cuatro decisiones y el deck quedó en
  > siete láminas.** Va **entero en español**, el nombre del proyecto incluido: **Detección
  > Nuclear**, que también nombra el archivo. Las láminas de contenido pasaron de dos a
  > **cuatro**, porque pidió ver **las mitosis detectadas contra las que marcó el patólogo** y
  > eligió partirlas en aciertos y falladas; y la lámina de los ocho ejes quedó con **un solo
  > punto** de resumen para que la tabla se quede con el contenido. Lo único que no cambió es
  > el período. La portada sigue en inglés, ahora por decisión y no por herencia: es copy de la
  > empresa. Las dos láminas nuevas salen de `scripts/galeria_mitosis_12.py`, que **no re-mide
  > nada**: lee los pares del cruce y recorta. Detalle y QA en
  > [`presentacion_b9/README.md`](presentacion_b9/README.md); lo que quedó stale por el cambio,
  > en [`auditoria_coherencia/hallazgos.md`](auditoria_coherencia/hallazgos.md).
  >
  > **ADDENDUM 28-ago-2026 — los dos ejes nucleares entraron al deck, que quedó en ONCE
  > láminas.** (Superado el 1-sep: la revisión de Ernesto lo lleva a trece; ver la última línea
  > de esta sección.) Las cuatro figuras van **en el cuerpo**, entre los recortes de mitosis y la lámina
  > de los ocho ejes. Con eso, tres tablas quedaban contradiciendo al deck y se actualizaron:
  > OBJETIVOS marca el objetivo como **Cerrado** nombrando los dos ejes medidos, la tabla de los
  > ocho ejes pasa «Grado nuclear» y «Tumor y estroma» a **medidos**, y **Tareas quedó con dos
  > filas** (necrosis y punto caliente mitótico), sin reemplazar la que se libera. Se borró
  > además el `.pptx` huérfano en inglés. Al incorporarlas **la dependencia entre los dos
  > generadores se invirtió**: las cuatro láminas y sus primitivas viven en
  > `presentacion_b9/generate_b9_deck.py` y la hoja de
  > [`ejes_nucleares/figuras/`](ejes_nucleares/figuras/) quedó como envoltorio delgado. El
  > intérprete del deck pasó a `envs/pruebas`, porque ahora depende de `zarr`. Lo decidió el
  > 28-ago (§Cuarta pasada de
  > [`auditoria_coherencia/hallazgos.md`](auditoria_coherencia/hallazgos.md)) y **se ejecutó** el
  > mismo día; el QA visual encontró tres defectos de geometría que `auditar` no ve, detallados
  > en [`presentacion_b9/README.md`](presentacion_b9/README.md).
- [**Los dos ejes nucleares, pre-registrados**](ejes_nucleares/prereg.md) (27-ago, CPU) — antes
  de medir aparecieron **tres correcciones de premisa**: las 107 anotaciones de grado son
  **núcleos sueltos y no regiones** (218,8 µm² y bbox 36×36, el perfil de una marca de
  `Mitosis`), así que la unidad del eje 3 es **punto contra punto**; el **área del polígono es en
  parte el pincel de QuPath** y por eso ningún descriptor sale de la marca; y el grado está
  **confundido con la lámina** sin un solo cruce, así que el `n` del ordenamiento es **12
  láminas**. Gate pasado: **107 de 107** marcas caen sobre un núcleo segmentado. El §4 del
  inventario queda corregido por ADDENDUM.
- [**El control positivo del eje 4, medido y pasando**](ejes_nucleares/resultados.md) (27-ago,
  CPU) — la fracción epitelial dentro de las regiones del patólogo separa epitelio de estroma con
  **AUC de rango 0,906** sobre 209 regiones (0,937 en las 10 láminas bien alineadas), contra un
  nulo **por traslación** centrado en 0,439 con p97,5 = 0,528; `p` = 0,0050, que es el piso de 200
  iteraciones. `Stroma` y `Tejido Adiposo` dan **cero exacto** en la mediana. ⇒ **el instrumento
  funciona** y la condición de lectura del eje 3 queda satisfecha, que es lo que habilitó medirlo
  al día siguiente (línea de abajo).
- [**El eje 3, pleomorfismo: los descriptores ORDENAN**](ejes_nucleares/resultados.md) (28-ago,
  CPU) — el percentil del área dentro de la población epitelial de la propia lámina da **75,1 ·
  92,1 · 98,9** de mediana para bajo, moderado y alto, con **ρ = +0,809** entre las **10 láminas**
  de la población restringida y `p` = **0,0056** en el nulo exacto de 360 asignaciones. La
  población completa ordena igual (+0,552) y **no despega** (0,0673), y el pre-registro dice que
  manda el nivel lámina. El `n` honesto son **láminas y no marcas**, porque el grado está
  confundido con la lámina; y el ordenamiento **no valida Nottingham**: son núcleos que el
  patólogo eligió como ejemplares, con percentiles altos en los tres grados.
- [**Los dos ejes tienen figura, y el `p` del eje 3 es un techo**](ejes_nucleares/figuras/) (28-ago)
  — cuatro láminas nativas sobre la plantilla oficial, con el generador importando el código que
  produjo cada número en vez de reimplementarlo. Dibujar el nulo produjo el hallazgo: en la
  restringida el ρ observado **es el máximo** de las 360 asignaciones, así que 0,0056 es el piso
  del diseño y **no una holgura** contra el 0,05; y la completa **no está frenada por el diseño**
  (tenía 0,0007 disponible), la frenan dos láminas de `alto` que caen por debajo de las de `bajo`.
  Va como ADDENDUM en `resultados.md` §2.a: ninguna tabla publicada cambia.
- **La revisión del deck y el eje de atención, DECIDIDOS y sin ejecutar** (1-sep) — Ernesto miró
  el deck armado por primera vez y devolvió cuatro cosas. Tres son de comprensión: los **30 µm**
  de la lámina del resultado no dicen que son una **distancia de emparejamiento** y se leen como
  un tamaño ([[parametro-necesita-su-semantica]]); las láminas 7, 8 y 9 «están bonitas pero no se
  entienden»; y la 6 tampoco, con un **eje horizontal que no tiene rótulo** y pasó las cuatro
  capas de QA. La cuarta abre trabajo: preguntó si a HoVer-NeXt se le pasaron los parches de más
  atención de CLAM. **No** ([`cruce_94.md`](mitosis_12_laminas/cruce_94.md) §6: la WSI entera, en
  las doce), y sobre esa respuesta decidió **medir la atención de CLAM sobre las doce** y ver si
  coincide con las mitosis del patólogo. Diseño cerrado: **folds limpios por lámina**, cabeza
  primaria la de la clase verdadera, nulo por traslación, unidad parche con el agregado por
  lámina, y **dos láminas nuevas** en el deck, que queda en **trece**
  ([[atencion-doce-laminas-folds-limpios]]). **Nada de esto se ejecutó**: el plan lo toma una
  sesión limpia.
  De paso quedó contestado, sin medir nada nuevo, que **las marcas falladas no son más chicas**
  (lado mediano 36 px en los dos grupos, [`cruce_94.md`](mitosis_12_laminas/cruce_94.md) §3.d).

  > **ADDENDUM 1-sep-2026 (sesión 38) — el plan se verificó contra el archivo y tres de sus
  > afirmaciones no resistieron.** Sigue **sin ejecutar**: lo que cambió es que ahora la sesión que
  > lo tome arranca con la verdad de campo hecha, en
  > [`atencion_12_laminas/hechos_verificados.md`](atencion_12_laminas/hechos_verificados.md).
  > **(1)** El **0,890 de referencia no lo produjo la familia 5fold**: promedia 4 checkpoints de
  > tres directorios, y es del universo *lámina* (el de región es 0,903). Un driver que use sólo
  > esa familia da **0,9265**, fuera de la banda que el propio plan fijaba ⇒ el gate se cambia por
  > el **valor exacto por checkpoint** ([[gate-regresion-valor-exacto-no-banda]]). **(2)** El
  > driver **no corre en `envs/pruebas`**: `build_clam` importa `topk`, que ahí no está, y tampoco
  > está la `libopenslide` parchada; los dos scripts van en **`clam_latest`** y el deck se queda en
  > `pruebas` por `zarr`. **(3)** «Fold limpio» son **tres** tiers (ausente · test · val) y no dos:
  > `val` gobernó el early stopping, así que se declara. Más dos decisiones de Ernesto: el
  > **primario son nueve láminas** con `score_1/2/3` (103 de los 113 parches; salen la que no tiene
  > etiqueta y las dos `no_identificado`, que se reportan aparte) y el agregado es **media sin
  > ponderar sobre láminas**, con el pooled como secundario. El **aviso a `sgaete` quedó redactado**
  > en [`atencion_12_laminas/aviso_sgaete.md`](atencion_12_laminas/aviso_sgaete.md), listo para que
  > lo mande.
- **La reunión del 1-sep reordenó el período, y los insumos del cruce YA estaban en disco** (1-sep)
  — Ernesto presentó el deck de once y volvió con seis cosas: **borrar las láminas 7, 9 y 10** (los
  dos histogramas de nulo y la tabla de los ocho ejes), cruzar la **atención de CLAM con
  HoVer-NeXt** para ver si mejora el conteo de mitosis, dejar la **zona de ~3 mm²** como objetivo
  propuesto del sprint que viene, contestarle a Sebastián **qué tamaño de parche toma HoVer-NeXt**,
  y **tres láminas visuales nuevas** (cómo funciona HoVer-NeXt con el diagrama del paper, los
  núcleos del grado nuclear, las regiones del núcleo epitelial). La próxima reunión es el **lunes
  07/09**. Verificado antes de planificar, en
  [`atencion_12_laminas/insumos_json_out.md`](atencion_12_laminas/insumos_json_out.md): los mapas
  de atención de las doce **ya existen** en `clam_ensemble/attn_batch/json_out`
  ([[clam-ensemble-json-out-atencion]]) y **ordenan** los parches con mitosis (AUC de rango 0,810
  mitosis · 0,772 gate), contaminados; la tesela de HoVer-NeXt es **256 px a 20× = 0,0142 mm²**, el
  mismo tamaño físico que un parche de CLAM, de donde **3 mm² ≈ 212 parches**; y **filtrar no puede
  subir el conteo**, sólo bajar el área, así que la medición es una **escalera de área** y no un
  top-K ([[carga-fija-no-k-fijo]]). **Nada de esto se ejecutó**: el plan lo toma una sesión limpia.
- **La forma de las tres láminas que quedaban abiertas** (2-sep, sesión 43) — con los insumos ya
  medidos, lo único sin decidir era **cómo se dibujan**. Ernesto eligió: la **7** lleva el mosaico
  casi a todo el ancho más los **tres brazos como barras** (0,809 · 0,792 · 0,770) y no una tabla;
  la **8** lleva **barras de área** con el conteo impreso y no la tabla de cinco filas; la **12**
  recompone la galería de núcleos a **dos columnas de seis**, conservando las doce láminas. Detalle
  y consecuencias en
  [`presentacion_b9/README.md`](presentacion_b9/README.md) § Estado al 2-sep (sesión 43), y el plan
  entero en `.handoffs/plan_B9_20260902_cinco_laminas_y_guion.md`. **Nada de esto se ejecutó**: lo
  toma una sesión limpia, y quedan cinco días para la reunión del 07/09.
- **Las dos decisiones de forma que faltaban, y el paper de las 3 mm²** (3-sep, sesión 45) —
  **D4**: en la lámina 7 las tres barras van **al lado** del mosaico y no debajo, porque apilado el
  mosaico caía a 7,3" y así llega a **8,3"** ([[figura-alto-lo-decide-el-pie]]). **D5**: la lámina 12
  se entrega a dos columnas y, si el QA visual muestra que a ~0,53" no se lee, se pasa a `--n-col 3`
  **sin volver a preguntar**. Además apareció la **cita de las 3 mm²** en el workspace de `sgaete`
  (Ibrahim et al., *Modern Pathology* 2022, [[paper-3mm2-ibrahim-modern-pathology]]), lo que cierra
  ese pendiente con personas, y con ella el **cuarto solape**: sus jobs `hnx_time` y `hnx_win`
  corren HoVer-NeXt con **nuestro checkpoint** sobre 81 ventanas de nuestras láminas, o sea la
  tarea del punto caliente que la lámina 13 propone. Detalle en
  [`presentacion_b9/README.md`](presentacion_b9/README.md) § Estado al 3-sep (sesión 45).
  **Las cinco láminas siguen sin escribirse.**
- **La simetría de los dos juegos de pesos** (heredada del B8, se re-declara porque gobierna el
  objetivo 2) — Lizard-Mitosis tiene **mitosis y no necrosis**; PanNuke tiene **`dead` y no
  mitosis**. Las dos son verdaderas a la vez y **ninguna reabre nada**
  ([[hovernext-clases-necrosis-solo-pannuke]]).

---

## Todavía sin especificar

Niebla: se intuye que viene, pero todavía no se puede formular con precisión. El test para sacar
algo de acá **no es poder responderlo, es poder enunciarlo**.

- **Por qué HoVer-NeXt falla en más de la mitad de las marcas.** La hipótesis vigente es que su
  clase de mitosis se validó **sólo en colon** y esto es mama, pero el cruce es consistente con
  ella sin probarla. Distinguir «el umbral está mal calibrado» de «la cabeza necesita reentrenarse»
  exige las probabilidades por tesela, y ésas existen **para una lámina de doce**.
- **Qué forma tiene la zona que se le propone al patólogo.** El hotspot es la definición
  operativa candidata (ventana de área fija que maximiza el conteo), pero cuánta área, con qué
  criterio de aceptación y contra qué se compara no están decididos. Es lo que hay que aclarar
  antes de que esto pueda pre-registrarse.
- **Si las doce láminas alcanzan para algo más que describir.** Sólo `Tumor` y `Mitosis` están en
  las doce; siete clases viven en 3 láminas o menos. Sebastián habló de **30** láminas y hay
  **12**: dónde están las otras 18 es pregunta para él.
- **El sign-off del patólogo sobre los nombres de tejido.** Se arrastra desde OBJ-A del B7 y sigue
  sin resolver ([[mammoth-interpretabilidad-objA]]).

### Pendiente sharp (ya se puede enunciar, falta pre-registro)

- **¿La necrosis que señala PanNuke coincide con los polígonos del patólogo?** Encargo 3 de
  Sebastián. Unidad **región contra punto**, así que no hay emparejamiento: densidad dentro contra
  fuera, con nulo por **traslación** de la máscara. Prerrequisito bloqueante: **unificar y declarar
  el vocabulario** (`necrosis` / `Necrosis` / `Comedonecrosis`). Costo estimado **7 a 9 h** de GPU
  para las cinco láminas con necrosis, extrapolado por área de canvas. Exige que Ernesto lo pida y
  que la GPU se libere.
- **¿El Δ del job 4589 en CDIS `_ci_reform` sobrevive a semillas nuevas?** Arrastrado del B8.
  Mammoth dio Δbal_acc **+0.074 ± 0.033 (5/5 folds)**. La réplica **exige semillas nuevas** y entra
  por **regla 9.b** con pre-registro, branch y `reviewer`.
- **El análisis B3**: rehacer el recorte de la lámina 15 con el CLAM plano del gate y compararlo
  contra el brazo Mammoth. CPU. Cierra el «no separamos si es de la tarea o del brazo».

---

## Fuera de alcance

Ruled out de **este** esfuerzo. No gradúa: vuelve sólo si se redibuja el destino, y entonces como
esfuerzo nuevo.

- **Precisión, F1 y PQ / bPQ / mPQ contra el geojson del patólogo.** No son computables contra
  positivos parciales, en ningún eje. No es una limitación de presupuesto.
- **Permeaciones vasculares, microcalcificaciones y arquitectura** como ejes de HoVer-NeXt. Los
  tres **NO-GO por falta de clase o de unidad**: el objeto de la tarea no es un núcleo. Argumento
  en [`inventario_tareas.md`](hovernext_tareas/inventario_tareas.md) §4.
- **Cualquier métrica de mitosis con umbral de confianza.** `pred_mitosis.tsv` no trae score y las
  once corrieron sin `--keep_raw`. Vuelve sólo si se decide re-correr con el raw.
- **El top-K de parches como forma de restringir.** A K fijo gana siempre la máscara más grande
  ([[carga-fija-no-k-fijo]]); y si la etapa cara se puede pagar entera, se corre **sin filtro** y se
  enmascara post-hoc ([[techo-filtro-antes-de-correr]]). La unidad correcta es **carga en mm²**.
- **SI-MIL** (31-jul) y **el eje de rendimiento de Mammoth** (Hallazgos 11-14). Heredados del B8 y
  sin premisa nueva que los mueva.

---

## Qué no se afirma

- Que el **27,7 %** sea el recall de HoVer-NeXt. El denominador son **las marcadas**, no las
  mitosis que hay en las láminas.
- Que las siete láminas con cero aciertos sean un problema de alineación. Los offsets se validaron
  con un criterio independiente y anterior, y donde algo empareja, empareja a menos de 16 px.
- Que los ejes declarados **GO** vayan a dar señal. Se afirma que son computables y baratos, no
  que midan algo.
- Que HoVer-NeXt mejore ninguna métrica nuestra. **No es el criterio de éxito de este sprint**: se
  busca detección e interpretabilidad que le proponga zonas al patólogo.
- Que el costo del eje de necrosis esté medido. Es una extrapolación por área de canvas sobre los
  18 min de Lizard.
- Que **`sgaete` no esté haciendo esto mismo**. Corre detección de mitosis con YOLOv11-m y tiene un
  pipeline propio de atención contra anotaciones ([[sgaete-yolo-mitosis-solapamiento]]).
  **Coordinar antes de escalar sigue pendiente, y ahora hay dos solapes.**
