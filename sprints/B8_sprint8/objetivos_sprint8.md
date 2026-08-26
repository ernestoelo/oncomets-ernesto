# Sprint 8 (B8) — mapa

> ## CERRADO el 25-ago-2026
>
> Resumen de cierre en [`../../progress/history.md`](../../progress/history.md)
> §"Sprint 8 (B8)". El sprint siguiente arranca en
> [`../B9_sprint9/objetivos_sprint9.md`](../B9_sprint9/objetivos_sprint9.md), y hereda los
> pendientes vivos (B2 sin lanzar, el análisis B3 del gate, la réplica del 4589, el
> vocabulario de necrosis y los pendientes con personas).
>
> **El cuerpo de abajo no se toca**: queda como estaba al cierre.

> **Reestructurado el 5-ago-2026** como índice, adoptando la gramática de secciones de la
> skill *wayfinder* (Destino / Decisiones / Todavía sin especificar / Fuera de alcance).
> Antes era una narrativa cronológica de 319 líneas con tres ADDENDUMs encima, que
> **duplicaba** el detalle que ya vive en los subdirectorios del sprint.
>
> **Regla de este documento: es un índice, no un almacén.** Cada decisión vive en
> exactamente un lugar (su archivo), y acá aparece con una línea que alcanza para juzgar si
> hay que abrirlo. Si algo se explica dos veces, la copia de acá es la que sobra.
>
> Origen: reunión del **viernes 24-jul-2026** con Sebastián y Benjamín sobre la
> presentación del Sprint 7. La mejor reunión hasta ahora según Ernesto: quedó demostrado
> el entendimiento del mecanismo al explicar slots, expertos, cabezas y el diagrama del
> paper, que era lo que Benjamín venía exigiendo ([[feedback-benjamin-entender-mammoth]]).

---

## Destino

Cerrar el eje de **capacidad y entendimiento** de Mammoth con números de tarea y no de
muestra (cuántos expertos y slots hacen falta, y si recortarlos cuesta métrica), y dejar
**elegida y justificada** la dirección de la rama por tarea para mitosis, sin código.

El B8 llega a su fin cuando no queda nada por **decidir** antes de que alguien se siente a
construir esa rama.

## Notas

- **Dominio:** interpretabilidad y capacidad de MoE sobre MIL en patología computacional.
  Ortogonal al eje de rendimiento, cerrado en los Hallazgos 11-14 de `CLAUDE.md`.
- **Skills a consultar en cada sesión:** `@slurm-submission` antes de cualquier `sbatch`,
  `@mammoth` para el modelo, `@knowledge-audit` al documentar, `@humanizer-es` para el
  guion del deck.
- **Restricciones permanentes:** regla 9 (argumento y pre-registro antes de código) en todo
  lo que toque entrenamiento; regla 9.b si algo pretende reabrir el eje de rendimiento;
  workaround H (no cambiar de rama con un job vivo); workaround J (proceso CPU largo va
  desatado y reanudable).
- **Comparaciones:** siempre pareadas reusando el `--split_dir` del baseline
  ([[patron-paired-comparison-reuso-splits]]). El pipeline es determinista bit a bit, así
  que una réplica que quiera ser independiente **tiene que cambiar la semilla**
  ([[pipeline-determinista-bit-a-bit]]).

---

## Decisiones tomadas

Una línea por asunto cerrado. El detalle está en el enlace.

- [**Encargo 1 — escalar la medición de slots**](q1_slots_escalado/resultados.md) (27-jul)
  — barridas 1858 láminas-fold (1176 únicas) en 18 min de CPU: **slots efectivos
  159.5 ± 26.3 de 300** y **expertos 29.98 de 30**, con `e50=15` y `e90=27` exactos en las
  1858 sin excepción. El 158.7 de n=7 se sostiene y ahora es el número de la tarea; **E=30
  no está sobredimensionado**. Método en
  [`metodologia.md`](q1_slots_escalado/metodologia.md).
- [**Encargo 1, corrección sobre la dispersión**](q1_slots_escalado/resultados.md) (27-jul)
  — con n grande se **invierte** lo que decía el B7: no manda el tamaño de lámina
  (ρ cae 0.750 → 0.141) sino levemente la tarea (eta²=0.086), y el ~88 % de la varianza es
  entre láminas. La **cohorte casi no mueve la aguja**, lo que descarta que medir solo TCGA
  en el B7 haya sesgado el número.
- [**Encargo 3 — grid E×S**](grid_expertos_slots/resultados.md) (4-ago, job 4774, 40/40
  runs) — **cerrado en H_nula**: el contraste primario (recortar S) menos (recortar E) da
  +0.022 / −0.014 / −0.002 de AUC en los peldaños 270/210/150, o sea **el signo se invierte
  entre peldaños** y la dirección del recorte es indistinguible. Pre-registro en
  [`prereg.md`](grid_expertos_slots/prereg.md).
- [**Encargo 3, secundarios**](grid_expertos_slots/resultados.md) (4-ago) — los dos apuntan
  a que **la capacidad sobra**: el piso 30×3 (−70 % de capacidad) pierde solo
  0.039 ± 0.062 de AUC, que cruza cero, y dentro de la rama S **no hay dosis-respuesta**.
  El peor brazo del grid es 27×10, el recorte más chico.
- **Acotación al «el margen está en S»** (4-ago) — la ocupación medida en el encargo 1
  **describe el reparto del peso, no dimensiona la capacidad**. Los números 159.5/300 y
  29.98/30 siguen vigentes; lo que no se sostiene es inferir de ellos **dónde** conviene
  recortar. Anotado en `CLAUDE.md` Hallazgo 12 y en [[mammoth-slot-routing-weight]].
- [**El pipeline es determinista bit a bit**](grid_expertos_slots/resultados.md) (4-ago) —
  hallazgo transversal que salió del control del grid: misma semilla, mismos splits y
  mismas features reproducen el checkpoint **byte a byte** en esta GPU. Valida el reuso
  pareado por construcción y a la vez prohíbe llamar «réplica» a re-correr con la misma
  semilla ([[pipeline-determinista-bit-a-bit]]).
- [**Encargo 4 — papers**](reunion_31jul_redireccion.md) (31-jul) — cerrado **con una
  decisión, no con una lectura**. Ver *Fuera de alcance* para qué quedó afuera y por qué.
- [**La atención sí cae sobre las mitosis**](atencion_vs_patologo/resultados.md) (1-ago) —
  AUC de ranking **0.890 ± 0.039** en checkpoints que nunca vieron la lámina, y el modelo
  igual responde mal. Es el resultado que le sacó la motivación principal a la familia A.
  Pre-registro en [`prereg.md`](atencion_vs_patologo/prereg.md).
- [**Encargo nuevo de 3 papers para mitosis**](tareas_geometricas/papers_mitosis.md)
  (2-ago) — los tres son **D** PU learning (Zhao, MELBA 2022), **C** CellViT (MedIA 2024) y
  **B** ZoomMIL (ECCV 2022). **Se recomienda D primero y en dos pasos**, por ser el único
  cuyo régimen de supervisión coincide con nuestros positivos parciales, con un **go/no-go
  barato** antes de gastar GPU. Hojas de reunión en
  [`hojas_reunion.md`](tareas_geometricas/hojas_reunion.md), mecanismo interno en
  [`papers_explicados.md`](tareas_geometricas/papers_explicados.md).
- [**Deck del B8**](presentacion_b8/README.md) (3 al 5-ago) — **16 láminas** a dos ejes, con
  el grid E×S como sección de cierre. Dos rediseños ejecutados (12 puntos el 4-ago, nueve
  más el 5-ago que lo bajan de 20 a 16), auditoría en cero. Queda **una** pendiente propia:
  el guion de las láminas nuevas y fusionadas, sin pasar por `@humanizer-es`.
- **La reunión con Sebastián es el jueves 6-ago**, no el viernes 7 (esa es la de Benjamín).
- [**Paper de segunda etapa para la reunión del 14-ago**](papers_14_agosto/hoja_jaroensri.md)
  (13-ago) — gana **Jaroensri et al., npj Breast Cancer 8:113 (2022)** (`10.1038/s41523-022-00478-y`):
  es la forma del pipeline de Sebastián publicada, con modelos de **parche** para los tres
  componentes de Nottingham y una etapa 2 de scikit-learn. Rubric puntuado sobre cuatro candidatos
  en [`busqueda.md`](papers_14_agosto/busqueda.md), estudio en
  [`jaroensri_estudio.md`](papers_14_agosto/jaroensri_estudio.md). Dos cosas que cambian el plan:
  **excluye el 20×**, que es toda nuestra cohorte privada, así que **tubular es la única rama que
  el privado alimenta sin ampliar**; y el **ahorro del top-k se cae** justo en esa rama, porque su
  campo de 1 mm cubre ~70 parches nuestros.
- [**Segunda tanda de candidatos, los que mapean el objeto**](papers_14_agosto/hoja_especialistas.md)
  (14-ago, Hoja 8) — pedida por Ernesto una hora antes de la reunión. Separa **puntuador** de
  parche (devuelve un número: Jaroensri, Mercan) de **mapeador** por objeto (devuelve polígono y
  clase de cada núcleo), que es el único que puede localizar núcleos dispersos y compararlos
  contra su vecindario. Gana **HoVer-NeXt** (MIDL 2024): **clase de mitosis**, **pesos
  públicos**, **0,5 µm/px nativo** y **17× más rápido que HoVer-Net**, o sea que ataca a la vez
  el agujero de la clase mitótica, el del 20× y el del costo que dejó la rama en pausa. Detrás
  quedan **CellViT++** y el ecosistema **MIDOG 2025**. Riesgo principal: su clase mitótica es
  de **colon**.
- [**HoVer-NeXt, verificado contra el PDF**](papers_14_agosto/hovernext_estudio.md) (14-ago,
  tarde) — leído entero. **Las seis afirmaciones de la Hoja 8 se sostienen como hechos**, con tres
  correcciones que cambian la lectura: **(1)** el **F1 0,84 es detección binaria** («¿hay un
  núcleo?»), el F1 medio por clase es 0,606 y **la mitosis sola da 0,55-0,62** con precisión 0,545,
  o sea que **sobre-cuenta casi al doble**; la balanced accuracy 0,758 promedia seis clases **sin**
  mitosis. **(2)** Las ventajas **no viven en el mismo juego de pesos**: Lizard-Mitosis trae la
  mitosis y el 0,5 µm/px pero es **todo colon**, PanNuke cubre mama pero **sin mitosis y a 0,25**.
  A favor: **sí validan fuera de colon** y mama sale **6ª de 19** (mPQ 0,495), por encima de colon
  (17ª); y la escala es gratis, porque su propia MitEval viene re-muestreada a 0,5 desde 0,12 y
  0,25. **(3)** El costo no queda atacado sino **demolido**: la 129741 son **~2 min**, las 881 de
  la cola **~30 h** contra ~132 días de HoVer-Net. **Lo que nunca se midió es la clase mitótica
  fuera de colon**, y ese es el único riesgo que queda entero.
- **El go/no-go del top-20 no tenía denominador, y se corrigió** (14-ago, tarde) — el top-20 de los
  4799 parches de la 129741 **contiene 3 de los 28 parches con mitosis** (mediana de 12
  checkpoints; rango 0 a 5): el máximo recuperable de la prueba propuesta era 3, no 26. Para la
  mitad de las marcas hacen falta **189** parches y para las 28, **1392**. **No contradice el AUC
  0,890**: el percentil mediano de un parche con mitosis es ~96 y el top-20 es el 99,58. La versión
  que decide es **correr la lámina entera** (dos minutos) y medir **recall sobre las 26**, sin
  calcular precisión contra un geojson de positivos **parciales**. También se cae el «ahorro
  ~240×». Lección transportable en [[topk-percentil-no-auc]].
- [**HoVer-NeXt por dentro, el mecanismo**](papers_14_agosto/hovernext_mecanismo.md) (14-ago,
  noche) — cómo funciona cada pieza, escrito como delta contra
  [`hovernet_estudio.md`](hovernet_estudio.md). Lo que corrige de la lectura natural del candidato:
  **(1)** el **BCB-map no es donde vive el 17×**. Cruzando nuestra medición de HoVer-Net (job 4714)
  con el paper, el post-proceso era **~35 % del costo** (1 h 15 de 3 h 36), así que borrarlo entero
  compra **~1,5×**; el resto sale de ingeniería de inferencia (encoder Tiny, media precisión, salida
  cuantizada a un byte, Zarr/LZ4, escritura en otro proceso, pre-stitching) y de **sacar el convex
  hull, que se pagó en distancia de Hausdorff**. **(2)** El BCB **no separa mejor que los mapas HV**:
  en PanNuke el bPQ da 0,656 contra 0,659 de HoVer-Net. Separa **igual y más barato**, que es la
  tesis real del paper. **(3)** El pipeline **espera una WSI**: su foreground sale del thumbnail de
  OpenSlide y el stitcher existe para pegar ROI, así que darle parches sueltos es tocar código, no
  configurarlo, y además paga un **borde perimetral** que el solape de la lámina evita. **(4)** La
  ablación de C.2 dice **«hace falta una de las dos y cuál importa poco»**, no «muestrear es mejor»:
  la fila ganadora en mAcc es justamente la **ponderación sola**, que descartaron. Quedan **cuatro
  preguntas que solo cierra el código** (§14 del doc).
- [**La reunión del 14-ago redibujó el destino**](hovernext_129741/plan_semana_17ago.md) (17-ago)
  — Sebastián dejó **cuatro encargos** y un argumento que reordena el criterio de éxito del
  sprint: **quiere HoVer-NeXt aunque no suba ninguna métrica**, porque busca detección e
  interpretabilidad que **le proponga zonas al patólogo** y le acelere el etiquetado, y porque a
  17× de su predecesor es viable sobre la cohorte. **Se evalúa con las métricas del paper, no con
  AUC.** Los encargos: los tres brazos de mapa de calor sobre la 129741, los mapas de atención /
  expertos / slots de CLAM+Mammoth sobre esa lámina, abrir la cadena interna de HoVer-NeXt
  (HV → BCB → raw class → class-map) y, al final, más relaciones E×S.
  Memoria [[hovernext-encargo-17ago-diseno]].
- **Reconocimiento del 17-ago** — tres hallazgos que cambian el mapa y no costaron GPU:
  **(1)** hay **12 láminas anotadas por el patólogo**, no una, en `sdonoso/anotaciones/` (de
  `sgaete`, READ-ONLY), las 12 con features y WSI y **las 12 con mitosis** — 94 marcas contra 26;
  Sebastián habló de 30, **faltan 18**. **(2)** La 129741 cae en **test del fold 4** de
  `carcinoma_ductal_insitu_presente_ci_reform`, o sea que **ya existe** el par CLAM/Mammoth del
  job 4589 sobre esta lámina **no vista** — el encargo 2 sale **sin GPU**. **(3)** `sgaete` tiene
  un pipeline **propio** de atención-vs-anotaciones sobre 8 tareas ⇒ **coordinar antes de barrer
  las 12**. Detalle en [`auditoria_coherencia/hallazgos.md`](auditoria_coherencia/hallazgos.md)
  (vigésima pasada).
- **Diseño de los tres brazos** (17-ago) — HoVer-NeXt se corre **una vez sobre la lámina entera**
  y los brazos restringidos se construyen **enmascarando post-hoc**, no recortando parches: el
  pipeline espera una WSI, un parche suelto paga borde perimetral, a ~2 min no hay motivo de
  costo, y así los tres brazos quedan **pareados por construcción**. Y **PQ / bPQ / mPQ no son
  computables** contra este geojson (no es segmentación exhaustiva ni son contornos nucleares);
  sobreviven el **recall de detección** y los **descriptores de regularidad**.
  > **Acotado el 17-ago (tarde) por la auditoría de código**: la razón «hay que tocar código para
  > parches sueltos» **es falsa** (`.npy` y `.png` están expuestos por `--input`) y la de costo
  > **se debilitó** (esta lámina no filtra fondo ⇒ 51k tiles, ~21 min, no ~2). **La decisión no
  > cambia**: se sostiene en el borde perimetral y en el pareo por construcción.
- **Fases 0 y 1 EJECUTADAS y cerradas** (17-ago) — HoVer-NeXt instalado y auditado
  ([`hovernext_129741/auditoria_codigo.md`](hovernext_129741/auditoria_codigo.md)), e
  interpretabilidad CLAM/Mammoth sobre la 129741 con el par del fold 4
  (`results/b8_hovernext_129741/interp/`). **La atención cae sobre las marcas del patólogo en los
  dos brazos** (mitosis es el grupo de percentil más alto: CLAM 0,872 / Mammoth 0,914 contra
  ~0,50) **y los dos igual clasifican mal la lámina** — la misma firma del 1-ago, ahora en otra
  tarea. Mammoth hunde la grasa a 0,066 donde CLAM la deja en 0,572.
- **Tres cosas de la auditoría que gobiernan la fase 2** (17-ago) — `--keep_raw` es
  **obligatorio** (si no, se borra el insumo de la 2.b); el **presupuesto pasa de minutos a
  horas** (sin `thumbnail` no hay filtro de fondo: 51k tiles Lizard / 206k PanNuke); y los
  **mapas HV se descartan en inferencia**, así que la figura de la 2.b lleva **tres** paneles y
  se dice por qué falta el cuarto. Además el TTA **se sortea sin semilla** ⇒ la corrida **no es
  reproducible**, y con Lizard **`--metric f1` es la única opción**.

---

## Todavía sin especificar

Niebla: se intuye que viene, pero todavía no se puede formular con precisión. El test para
sacar algo de acá **no es poder responderlo, es poder enunciarlo**.

- **Qué pidieron exactamente en el encargo 2.** Hay tres lecturas y la respuesta la tiene
  Sebastián. Análisis completo en
  [`slots_entrenados_encargo2.md`](slots_entrenados_encargo2.md). La lectura más plausible
  quedó **parcialmente respondida** por el encargo 1; si es la correcta, falta solo la
  parte de mapas sobre láminas privadas, que exige verificar disponibilidad de WSI.
- **Qué forma tiene una «rama aparte de CLAM» especializada por tarea.** La dirección está
  elegida (D, en dos pasos), pero la arquitectura concreta, dónde se engancha con el
  pipeline actual y qué comparte con el CLAM de producción no están definidos. Es lo que
  hay que aclarar antes de que esto pueda pre-registrarse.
- **El sign-off del patólogo sobre los nombres de tejido.** Los nombres que usamos para
  expertos y slots son **lectura visual nuestra, no anotación**
  ([[mammoth-interpretabilidad-objA]]). Se arrastra desde OBJ-A y sigue sin resolver.
- **Si el material de anotación alcanza para entrenar.** Hay **doce láminas**, un anotador y
  **94 marcas de mitosis** (corregido el 17-ago: eran «una lámina y 26 marcas» hasta que el
  reconocimiento encontró `sdonoso/anotaciones/`), con positivos parciales y varias con más de
  una región de escaneo ([[anotaciones-patologo-qupath]]). Cuánto de eso es suficiente para el
  paso 1 de D sigue siendo parte del go/no-go, pero **cambió de orden de magnitud**.

### Pendiente sharp (ya se puede enunciar, falta pre-registro)

- **¿El Δ del 4589 en CDIS `_ci_reform` sobrevive a semillas nuevas?** Mammoth dio
  Δbal_acc **+0.074 ± 0.033 (5/5 folds)** en la formulación nueva, con ambos recalls al
  alza. El control del grid **no** lo replicó ni podía (misma semilla). La réplica **exige
  semillas nuevas** y, si se plantea como búsqueda de mejora, entra por **regla 9.b** con
  pre-registro, branch y `reviewer`. Detalle en
  `sprints/B7_sprint7/resultados_interpretabilidad.md` §2.

---

## Fuera de alcance

Ruled out de **este** esfuerzo. No gradúa: vuelve solo si se redibuja el destino, y
entonces como esfuerzo nuevo.

- **SI-MIL no se implementa** (31-jul). Gana interpretabilidad a costa de empeorar
  levemente la métrica, y lo que se busca es métrica. Su propia Tabla 2 lo muestra en la
  celda que nos toca (0.937 → 0.925 accuracy, 0.972 → 0.957 AUC con CLAM de base). Estudio
  conservado en [`simil_estudio.md`](simil_estudio.md) y
  [`simil_explicacion_matematica.md`](simil_explicacion_matematica.md).
- ~~**HoVer-Net queda en pausa por costo** (31-jul)~~ → **VUELVE al alcance el 14-ago, como
  esfuerzo nuevo y con otro modelo.** Se deja tachado y no borrado porque la cadena importa.
  La pausa se apoyaba en dos premisas y **las dos cayeron**: el **costo** (3,3 h por lámina
  medidas por Sebastián, contra **~2 min** de HoVer-NeXt) y el **top-20** como diseño (no le
  da el denominador — patrón **P2**, [[topk-percentil-no-auc]]). Y sobre todo **la reunión del
  14-ago redibujó el destino**, que es la única condición bajo la cual esta sección deja
  volver algo. **No es regla 9.b encubierta: es el supervisor cambiando el objetivo.** Estudio
  viejo en [`hovernet_estudio.md`](hovernet_estudio.md), memoria
  [[simil-hovernet-decision-31jul]]; encargo y diseño nuevos en
  [`hovernext_129741/plan_semana_17ago.md`](hovernext_129741/plan_semana_17ago.md) +
  [[hovernext-encargo-17ago-diseno]].
- **La familia A de la rama de mitosis** (cambiar el operador de agregación) perdió su
  motivación principal el 1-ago: la atención **sí** cae sobre las mitosis y el modelo igual
  responde mal. Quedan B, C y D. Ver [`tareas_geometricas/README.md`](tareas_geometricas/README.md).
- **Los dos papers de suscripción**: LVI → metástasis ganglionar (Human Pathology 131:26-37,
  2023) e ILSC (Liu et al., MedIA 2026). Sin arXiv ni PMC, verificado. Requieren acceso
  institucional y los consigue Ernesto. Fichas y BibTeX en [`papers_b8.md`](papers_b8.md).
- **Recortar E o S en producción.** El grid cerró en H_nula, así que no hay base para
  cambiar la configuración 30×10 por ninguna de las probadas.

---

## Qué no se afirma

- Que la **dirección** del recorte de capacidad sea indiferente en general. Se midió en una
  tarea (CDIS `_ci_reform`), un dataset y una GPU. Lo que se afirma es que **en ese
  terreno** resultó indistinguible.
- Que el determinismo bit a bit valga cross-hardware. Está acotado a esta RTX A6000 y este
  stack.
- Que el encargo 2 esté cerrado porque los slots ya se entrenan con nuestro dataset.
  Primero se aclara qué pidieron.
- Que el Δ del CDIS `_ci_reform` sea real. Son 65 negativos totales, ~13 por fold, y la
  réplica con semillas nuevas está pendiente.
- Que los nombres de tejido de expertos y slots sean anotación. Son lectura visual nuestra.
- Que HoVer-NeXt mejore nada nuestro. **Al 17-ago no se corrió una sola vez sobre nuestros
  datos**; el encargo es medirlo, no un resultado.
- Que las 18 láminas que faltan para las 30 de Sebastián no existan. Lo que se afirma es que
  **en el servidor hay 12**; dónde están las otras es pregunta para él.
- Que el brazo PanNuke vea detalle a 0,25 µm/px. La lámina tiene **0,465**: corre sobre píxeles
  interpolados.
