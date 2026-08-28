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
- **Restricciones permanentes**: `anotaciones/`, `hover_net/`, `clam_testing/`, `clam_environ/` y
  `hover_next_reference/` son **READ-ONLY**; regla 9 en todo lo que toque entrenamiento; workaround
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
- [**Los dos ejes nucleares, pre-registrados**](ejes_nucleares/prereg.md) (27-ago, CPU) — antes
  de medir aparecieron **tres correcciones de premisa**: las 107 anotaciones de grado son
  **núcleos sueltos y no regiones** (218,8 µm² y bbox 36×36, el perfil de una marca de
  `Mitosis`), así que la unidad del eje 3 es **punto contra punto**; el **área del polígono es en
  parte el pincel de QuPath** y por eso ningún descriptor sale de la marca; y el grado está
  **confundido con la lámina** sin un solo cruce, así que el `n` del ordenamiento es **12
  láminas**. Gate pasado: **107 de 107** marcas caen sobre un núcleo segmentado. El §4 del
  inventario queda corregido por ADDENDUM. **Nada medido todavía.**
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
- **¿Los descriptores nucleares de `pinst_pp.zip` ordenan los tres grados del patólogo?** Eje 3 del
  inventario, **CPU y ya en disco**: 107 **núcleos** con grado declarado (77 alto, 14 moderado, 16
  bajo), no regiones (ver la decisión de arriba). **Ya pre-registrado** en
  [`ejes_nucleares/prereg.md`](ejes_nucleares/prereg.md) §3 y **sin correr**. El criterio de éxito
  es que **ordenen**, no que separen perfecto, y el primario es el percentil intra-lámina porque
  el grado está confundido con la lámina.
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
