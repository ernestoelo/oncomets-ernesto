# progress/history.md

> Bitácora append-only de sprints cerrados. Al cerrar un sprint, el
> contenido de `current.md` se mueve acá y `current.md` se reinicia.

---

## Sprint 4 (B4) — CERRADO (1-jun-2026)

> Bitácora cronológica del sprint. Resumen final consolidado abajo
> ("Cierre B4"). El sprint B5 arranca con el deck B4 como base y mammoth
> como objetivo headline.

### 21 may 2026 — re-encolado del baseline tras el bug `topk`

- **Bug `topk`** en `inst_eval` (run 4096): slides de train con `<B` parches
  crashean `torch.topk`. Mitigado con split filtrado `minpatch16` +
  `scripts/preflight_minpatch.py` (preflight obligatorio en los `.slurm`).
- **Baseline B=8** re-encolado como job `4098` (RUNNING); **ablation B=16**
  como `4099` (PD, `dependency=afterok:4098`).
- **Limpieza de ramas**: c1-c4 (infraestructura compartida) movidos a `main`
  vía cherry-pick; c5 (pregunta de Obj 3) rehecho en `feature`; rename del
  dir de Obj 3 alineado en `main`.
- **Consolidación operativa**: preflight como patrón obligatorio, bug `topk`
  y reglas de git workflow documentados (`CLAUDE.md`, `docs/workarounds.md`).

### 21 may 2026 — resultados del baseline B=8 (job 4098)

- **Baseline B=8 COMPLETADO** (job `4098`, ~4h 11m). Métricas: test_auc 0.81,
  val_auc 0.69, test_acc 0.72, **balanced accuracy 0.31**. Detalle en
  `sprints/B4_sprint4/objetivo_1_baseline/resultados.md`.
- **Hallazgo central**: el régimen de evaluación de `microcalcificaciones_pth`
  NO es confiable — 4 de 8 clases tienen 1 muestra en val/test → macro-AUC
  dominado por ruido (inversión val < test). Métrica recomendada: balanced
  accuracy + matriz de confusión.
- **Hallazgo**: las 8 clases son un problema multi-label (3 tejidos) aplastado;
  propuesta para la reunión = reformular como 3 binarios.
- **B=16** (job `4099`) lanzado; mismo patrón de sobreajuste temprano.
- Eduardo aportó 3 papers a `papers/` para atacar el desbalance.

### Cierre B4 (1-jun-2026) — consolidación

- **Obj 1 baseline + Obj 2 ablación B**: el régimen de eval de las 8 clases es
  ruido (4 clases n=1); **B no es la palanca** (Δ ambiguo, balanced_acc bajó).
  El cuello es la **formulación**, no el hiperparámetro.
- **Reformulación 3 binarios** (carcinoma/cdis/tejido, `no_identificado`
  excluido): infra de Sebastián reproducida y validada; eval pasó de no-medible
  a confiable. Igualamos/mejoramos sus métricas oficiales.
- **Obj 3 + Obj 5 + ANEXO (DSMIL)**: cuadro CLAM×DSMIL cerrado **simétricamente**
  con MC-CV k=5. Veredicto: **la arquitectura del agregador NO es la palanca** a
  ninguna escala (fusionado = banda ambigua; binarias = NULL en 2/3 + regresión
  leve consistente en CDIS). El cuello sigue siendo **datos / contexto espacial /
  desbalance**. Hallazgo metodológico fuerte: el single-split engaña fuerte a
  n≈33 → MC-CV obligatorio + comparación PAIRED por reuso de splits.
- **Deck B4** presentado (1-jun). Base legacy: `papers/presentations/CLAM_Sprint_B4.pdf`.
- **Cambio de equipo**: **Eduardo renunció** (1-jun) → queda Ernesto + Sebastián.
  Heredó su trabajo de **mammoth** (sin commitear en `clam_testing`).
- **Obj 6 — mammoth (puente a B5)**: investigado + portado a `models_mammoth/`
  (subclase de CLAM_MB, 1ª capa → MoE) + driver `train_dsmil.py --model_type
  clam_mammoth` + slurm k=5 paired + test CPU + hipótesis (regla 9) + reviewer GO.
  **Snapshot** del trabajo de Eduardo preservado. Listo para correr en B5.

---

## Sprint 5 (B5) — CERRADO (~fin jun / 2-jul-2026)

> Sprint de cierre de trimestre (la presentación decidía la continuidad de
> Ernesto → continúa). Consigna de Benjamín: avanzar rápido y lucirse. Detalle
> por objetivo en `sprints/B5_sprint5/` (README + resultados por objetivo).

### Cierre B5 — consolidación

- **Eje ARQUITECTURA/OBJETIVO cerrado — 4 ángulos, 0 palancas** (CLAUDE.md
  Hallazgos 11-14): agregador/DSMIL (11), patch-embed/mammoth (12), lenguaje+tile/
  PathPT (13), loss focal/class_balanced (14). Todos convergen: el cuello es
  **datos / desbalance / contexto espacial**, NO la arquitectura ni la loss.
- **Hilo mammoth COMPLETO**: 8 tareas drop-in (`keep_slots=False`) + 4
  `keep_slots=True` = 0 palancas vs CLAM (jobs 4229/4243/4246/4387/4400, k=5
  paired). `slot_dropout` descartado. El (débil) efecto lo gobierna el balance de
  clases, no el patch-embed. [[mammoth-investigacion-integracion]].
- **Eje ORTOGONAL de interpretabilidad (OBJ-A, 30-jun)**: no reabre rendimiento;
  responde a Benjamín (29-jun). Los 30 expertos rutean por **morfología, no por
  clase** (detectores de tejido) → el cuello no está en la 1ª capa. Pendiente
  sign-off de patólogo. [[mammoth-interpretabilidad-objA]],
  [[feedback-benjamin-entender-mammoth]].
- **PathPT y loss-desbalance** probados y cerrados (necrosis H_alt, mitotic
  colapso de formulación, microcalc NO-GO; focal null, cb = H_reg). Confirman el
  cuello = CONCH/datos/calibración. [[pathpt-testing-necrosis-mitotic]],
  [[loss-desbalance-eje-c1]].
- **CPathAgent leído (30-jun) → magnificación aterrizada**: la palanca portable
  NO es el agente LMM (8×H800 + 278K Gemini + reportes pareados) sino la **fusión
  de features multi-escala** del baseline MIL (Ap. C.1.2), dentro de CONCH v1 512.
  [[magnificacion-cpathagent-proxima-direccion]].
- **Deck B5 entregado** (`papers/presentations/CLAM_Sprint_B5.pptx`, nativo
  python-pptx). Convenciones: [[deck-completo-pptx-buildable]],
  [[notas-presentador-guion-didactico]].
- **Palanca viva sin ejecutar al cierre**: Tier 0 calibración post-hoc del
  operating-point — la más barata (CPU, 230 `.pkl` en disco) y nunca corrida.
  [[calibracion-tier0-pendiente-ejecutar]].
- **Reunión con Sebastián (2-jul)**: aprobó la magnificación multi-escala,
  **acotada a microcalcificaciones** (pocas WSI) y a un **fin de semana**;
  Ernesto decide las magnificaciones y la estrategia de fusión. → arranca B6.

---

## Sprint 8 (B8) — CERRADO (25-ago-2026)

> Del **24-jul** al **25-ago-2026**. Abrió como sprint de **capacidad y entendimiento de
> Mammoth** (los cuatro encargos de la reunión del 24-jul) y **giró el 14-ago** a
> HoVer-NeXt, con Sebastián cambiando el criterio de éxito: quiere detección que le
> **proponga zonas al patólogo**, aunque no suba ninguna métrica. Mapa del sprint en
> `sprints/B8_sprint8/objetivos_sprint8.md`; detalle por objetivo en sus subdirectorios.

### Cierre B8 — consolidación

- **Encargo 1 (escalar la medición de slots) CERRADO** (27-jul, CPU, 18 min): barridas
  **1858 láminas-fold** (1176 únicas). **Slots efectivos 159,5 ± 26,3 de 300** y
  **expertos 29,98 de 30**, con `e50=15` y `e90=27` exactos en las 1858 sin una excepción.
  El 158,7 de `n=7` del B7 se sostiene y ahora **es el número de la tarea**: E=30 no está
  sobredimensionado. Corrige además al B7 en la dispersión: con `n` grande **no manda el
  tamaño de lámina** (ρ cae 0,750 → 0,141) y el ~88 % de la varianza es entre láminas.
  [[mammoth-slot-routing-weight]].
- **Encargo 3 (grid E×S) CERRADO en H_nula** (4-ago, job 4774, 40/40 runs): el contraste
  primario (recortar S) menos (recortar E) da **+0,022 / −0,014 / −0,002** de AUC en los
  peldaños 270/210/150, o sea que **el signo se invierte entre peldaños** y la dirección
  del recorte es **indistinguible**. Los secundarios apuntan a que la capacidad sobra: el
  piso 30×3 (−70 %) pierde 0,039 ± 0,062, que cruza cero. **Acota el encargo 1**: la
  ocupación medida describe el reparto del peso, **no dimensiona la capacidad**.
  [[mammoth-grid-expertos-slots]].
- **El pipeline resultó DETERMINISTA bit a bit** (4-ago), hallazgo transversal que salió
  del control del grid: misma semilla, mismos splits y mismas features reproducen el
  checkpoint **byte a byte**. Valida el reuso pareado por construcción (patrón P1) y a la
  vez **prohíbe llamar réplica** a re-correr con la misma semilla.
  [[pipeline-determinista-bit-a-bit]].
- **Encargo 2 sin cerrar**: qué pidieron exactamente con «entrenar los slots» tiene tres
  lecturas y la respuesta la tiene Sebastián. La más plausible quedó **parcialmente
  respondida** por el encargo 1.
- **Encargo 4 (papers) cerrado con una decisión, no con una lectura** (31-jul): **SI-MIL no
  se implementa** (gana interpretabilidad y pierde métrica, en la celda que nos toca) y
  **HoVer-Net queda en pausa por costo**. [[simil-hovernet-decision-31jul]].
- **La atención SÍ cae sobre las mitosis, y el modelo igual responde mal** (1-ago): AUC de
  ranking **0,890 ± 0,039** en checkpoints que nunca vieron la lámina. Le sacó la
  motivación principal a la familia A de la rama de mitosis, y es la firma que se repitió
  después en dos tareas más.
- **Patrón P2 nacido acá, y caro**: un AUC alto **no** implica que el top-k capture los
  positivos. Con AUC 0,890, el **top-20 contiene 3 de los 28** parches con mitosis, porque
  el percentil mediano de esos parches es ~96 y el top-20 es el 99,58. El go/no-go
  propuesto no tenía denominador. [[topk-percentil-no-auc]].
- **El sprint GIRÓ el 14-ago**: Sebastián pidió un especialista que **mapee el objeto**
  (polígono y clase por núcleo) y no un puntuador de parche. Gana **HoVer-NeXt** (MIDL
  2024): clase de mitosis, pesos públicos, 0,5 µm/px nativo y 17× más rápido que
  HoVer-Net, o sea que ataca a la vez el agujero de la clase mitótica, el del 20× y el del
  costo que había dejado la rama en pausa. Riesgo entero al cierre: **su clase mitótica se
  validó sólo en colon**. [[hovernext-especialista-segunda-etapa]].
- **Reconocimiento del 17-ago, tres hallazgos sin GPU**: hay **12 láminas anotadas** por el
  patólogo y no una (**94 marcas** de mitosis contra 26; Sebastián habló de 30, **faltan
  18**); la 129741 cae en **test del fold 4** de CDIS `_ci_reform`, así que el par
  CLAM/Mammoth sobre esa lámina no vista **ya existía**; y **`sgaete` tiene un pipeline
  propio** de atención contra anotaciones sobre 8 tareas. [[anotaciones-patologo-qupath]].
- **HoVer-NeXt corrió, y recupera la mitad de las marcas de la 129741** (19-ago, job 5008,
  18 min): **13 de 26** con emparejamiento uno a uno a 30 µm, plano de 7,5 a 75 µm. El
  ensemble PanNuke **no puede** contestar esa pregunta: no tiene clase de mitosis.
  [[hovernext-clases-necrosis-solo-pannuke]].
- **Fase A completa** (21 y 22-ago, toda en CPU, seis piezas): **A0** las 13 falladas
  estaban **segmentadas** (13 de 13, mediana 2,1 µm) y recibieron otra clase ⇒ **el arreglo
  es la cabeza de clase, no la segmentación**; **A1** la galería de las 177, donde 145 de
  164 caen en una sola familia; **A2** la atención del gate de invasivo, con AUC que se
  solapan y top-K radicalmente distintos (P2 de manual); **A2.bis** la escalera de brazos
  **a carga fija**, que dio vuelta el resultado (la unión ganaba **por el tamaño de la
  máscara**, no por el ranking, [[carga-fija-no-k-fijo]]); **A3** los 12 offsets, con las
  **94 de 94** marcas sobre parche; **A4** la necrosis, donde el modelo **se equivoca de
  clase y su cabeza igual localiza** en el percentil 96,8 (rama verdadera **0,899**, rama
  predicha **0,500 exacto**, [[rama-de-atencion-decide-el-resultado]]).
- **Fase B corrida a medias** (madrugada del 25-ago, sin que nadie los tocara): **B1**
  barrió las **11 láminas** restantes (113 min, 555 detecciones, las 12 completas) y **B3**
  entrenó el **CLAM plano del gate** (test AUC 0,9539), que destraba la pregunta de la
  lámina 15. **B2 (necrosis con el ensemble PanNuke) nunca se lanzó**: la GPU estuvo tomada
  por `UNLIMITED` ajenos todo el tramo final.
- **El re-barrido de regiones de escaneo, cerrado con giro** (18 y 19-ago): **31 de 77**
  medibles, y refutó que 33 fuera un piso. Dejó dos patrones nuevos: **P3**, el control
  positivo **calibra el criterio** y no sólo valida el instrumento; y **P4**, una categoría
  residual definida por **dos fallos** puede estar **fabricada por el instrumento**, que se
  confirmó con dato el 19-ago. [[control-positivo-calibra-el-criterio]],
  [[categoria-residual-fabricada-por-el-instrumento]].
- **Deck del B8 presentado** el 25-ago, 17 láminas a dos ejes, guion recortado y aplicado
  (7160 → 5585 palabras). [[deck-b8-dos-ejes-simil-mitosis]]. El **formato oficial de
  presentación cambió** ese mismo día: `[AAAAMMDD] [Nombre Apellido] [Proyecto].pptx`, en
  inglés y con 4 láminas ejecutivas, **supersede a Deep-LLM-V**. Spec en
  `docs/plantilla_oficial.md`. [[plantilla-oficial-image-to-text]].
- **El eje de rendimiento de Mammoth NO se movió** (Hallazgos 11-14 de `CLAUDE.md` intactos).
  Sigue vivo el **DATO ABIERTO** del job 4589 en CDIS `_ci_reform` (Δbal_acc +0,074 ± 0,033,
  5/5 folds), cuya réplica **exige semillas nuevas** y entra por regla 9.b.
- **Qué queda vivo al cierre, heredado por el B9**: B2 sin lanzar · el análisis B3 del gate
  (CPU, ya tiene el CLAM plano en disco) · la réplica del 4589 · el vocabulario de necrosis
  sin unificar · si `mitosis` quedó **segunda por poco** en las 13 falladas (sólo la 129741
  tiene el raw) · **avisarle a `sgaete`**, que ahora son **dos** solapes porque corre
  detección de mitosis con YOLOv11-m · las dos preguntas del 6-ago (las 30 láminas, y quién
  es «GDT») · el sign-off del patólogo.
- **Reunión del 25-ago**: Sebastián deja **tres objetivos** para el período que viene
  (escalar mitosis a más WSI anotadas, evaluar necrosis, evaluar métricas nuevas de
  mitosis) con el encuadre de **demarcar una zona importante para el patólogo**. → arranca
  B9, `sprints/B9_sprint9/objetivos_sprint9.md`.
