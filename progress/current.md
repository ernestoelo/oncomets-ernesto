# progress/current.md

> Estado vivo del sprint actual. Es un **snapshot** — se reemplaza al avanzar
> el sprint. Al cerrar el sprint, el resumen pasa a `history.md`.
>
> **Roll-over 6-jul-2026 (sesión Fable):** B5 cerrado y movido a `history.md`.
> **Roll-over 13-jul-2026:** abre **B7** (reunión con Sebastián, deck B6 presentado y
> salió bien). El eje **magnificación** de B6 **NO se cierra**: sigue vivo (pipeline
> armado, se lanza el próximo fin de semana con OK) y se arrastra a B7 más abajo. El
> detalle histórico de B6 puede pasar a `history.md` **si Ernesto lo pide** (pendiente).

---

## B7 / Sprint 7 — Interpretabilidad CLAM vs Mammoth + ¿cuántos expertos/slots?

> **PRESENTADO el 24-jul-2026** ante Sebastián y Benjamín, y salió bien. El foco pasó al
> **B8**, cuyos cuatro encargos están al final de este archivo y desarrollados en
> `sprints/B8_sprint8/objetivos_sprint8.md`. El B7 **no se movió a `history.md`**: quedan
> pendientes vivos del deck y ese traspaso lo decide Ernesto (mismo caso que el B6, ver
> cabecera del archivo). Lo de abajo es el registro del sprint tal como se ejecutó.

**Abierto 13-jul-2026.** Nace de la reunión con Sebastián (deck B6 presentado, salió
bien). Eje de **entendimiento / interpretabilidad** (ortogonal al de rendimiento, cerrado
en Hallazgos 11-14). Equipo = Ernesto + Sebastián. Reunión de seguimiento: **miércoles**.

### Headline

Comparar **mapas de calor / atención de CLAM vs Mammoth** en 3 tareas y responder:
**¿cuántos expertos (E) y cuántos slots (S) hacen falta para todas las tareas?**

- **3 tareas:** `tipo_histologico` · `carcinoma_ductal_insitu_presente` (CDIS presente) ·
  `invasion_linfatica_vascular` (invasión linfovascular).
- **Requisito por tarea (Sebastián, obligatorio):** qué slides · qué magnificación (µm/px) ·
  qué dataset · qué etiqueta del patólogo.
- **Análisis:** expertos por zona · consecuencia cross-slide/cross-task · **peso de los
  300 slots en el ruteo** (NUEVO, ≠ top-k de parches existente; usa `combine_weights`).
- Docs: `sprints/B7_sprint7/{objetivos_sprint7.md, preguntas_resueltas.md}`.

### Factibilidad (verificado 13-jul — LOAD-BEARING)

- **`invasion_linfatica_vascular`**: hay checkpoints CLAM + Mammoth (obj2/obj3) →
  comparación CPU-post-hoc **ejecutable ya**.
- **`tipo_histologico`** y **`carcinoma_ductal_insitu_presente`**: **NO** hay checkpoint
  Mammoth nuestro → generar sus mapas de expertos exige **entrenar mammoth = GPU (gate
  d/b + regla 9 + reviewer)**. Opciones (A/B/C) en `objetivos_sprint7.md` — a decidir con
  Ernesto. **Nada a GPU esta sesión.**

### Respuestas de Sebastián (14-15 jul, VERIFICADAS — `auditoria_coherencia/hallazgos_sesion_sebastian_15jul.md`)

- **Magnificación VERIFICADA:** su parche = **448 px @ ×40 en TCGA** (`run_create_patches_tcga_sc.slurm`)
  → `--target_patch_size 224` a CONCH (`run_extract_features_tcga_sc.slurm`) = mismo campo físico (104 µm)
  que 224@×20. Privado+HistAI a ×20 sin cambio. Confirma la matemática (A VERIFICAR→VERIFICADO). Su fix =
  **escala única común = brazo B0** del pre-registro; nuestra pirámide agrega contexto 512 µm encima.
- **⚠ El drift de features del 26-27 jun ES este parche.** Reemplazó las TCGA en `features/pt_files`;
  backup viejas 224@×40 en `features_tcga_224x40` (864). **Checkpoint invasión = 04-jun → features viejas.**
  → **re-entrenar las 3 tareas** sobre features actuales para consistencia. [[features-tcga-drift-reextraccion]].
- **Cambio de formulación (audio):** pipeline en **cascada** — gate binario carcinoma-invasivo → downstream
  **sin `no_identificado`**. `carcinoma_ductal_insitu_presente` = **binaria** {no:636, si:810}. `tipo_histologico`
  = **3-clase CONFIRMADA** {no_especifico, lobulillar, otros} sin no_id (Sebastián 15-jul: "Eso mismo"). [[formulacion-cascada-gate-invasivo]].
- **✅ Formulación + splits CONFIRMADOS (Sebastián, WhatsApp 15-jul 18:41-18:42):** `tipo_histologico` = las 3
  clases; **splits = REGENERAR en carpeta nueva** (no reusar). **Dato nuevo:** ya dejó artefactos con terminación
  **`_ci`** en `clam_environ/environ/` (ci = carcinoma invasivo) → **inspeccionar read-only `environ/*_ci*` ANTES
  de generar** para no duplicar; confirmar qué contienen. Pidió observaciones.
- **Gate entrenado (mensaje 15-jul):** Sebastián entrenó el clasificador binario de invasivo → **AUC
  0.9524 ± 0.017 / val 0.9596** ("generalizó super bien"). Muy probablemente "el modelo que te comentó" (a
  confirmar). Buena señal para la cascada. El código del gate sigue siendo suyo (sin ubicar).
- **✅ Paths del parche de magnif RECIBIDOS** (Sebastián, WhatsApp 15-jul 9:23-9:24): `run_create_patches_tcga_sc.slurm`,
  `run_extract_features_tcga_sc.slurm`, backup `features_tcga_224x40` — coinciden con lo ya verificado. **No re-pedir**
  ([[verificar-antes-de-pedir-dato]]).
- **✅ `_ci` inspeccionados + REUSO decidido (16-jul):** Sebastián dejó la suite completa de la cascada (8 tareas)
  en `environ/{csv_balance_ci, splits_5fold_balance_ci}` (5-fold estratificado, cross-check regla 10 limpio). Son
  los "nuevos splits en carpeta nueva" → **decisión Ernesto: reusarlos para todas las pruebas** (el `.slurm` apunta
  a `splits_5fold_balance_ci/<task>_ci_100`, paired; **resuelve el prereq B** "generar splits"). Distribuciones
  reales: tipo 3-clase n=2027 {1610/240/177}; CDIS binaria {no:2005, si:810}; invasión binaria {ausente:2447,
  presente:368}. **✅ SB6 resuelto:** `patch_size_level0:512` @ ×40 = tercera geometría → refuerza re-entrenar invasión.
- **✅ Observaciones planteadas a Sebastián y RESPONDIDAS (17-jul) → REFORMULACIÓN de CDIS/LVI:** Ernesto le
  planteó el plegado de no_id (obs. 1); Sebastián confirmó tipo_histologico (3 clases, `_ci` válido) y **reformuló
  CDIS y LVI**: descartar no_id + **restringir a WSI invasivas, solo casos explícitos** (motivo: evitar que el
  modelo aprenda invasión/no-invasión en vez de la tarea). El **plegado del `_ci` de CDIS/LVI queda SUPERSEDED**.
  Números nuevos (verificados con el CSV del clasificador de invasión `csv_balance/dataset_invasion_carcinoma_gate_label.csv`
  = {invasivo:2013}): **CDIS {no:132, si:730} n=862 → 85% positivo** (desbalance dado vuelta; los "no CDIS" estaban
  casi todos en WSIs no invasivas); **LVI {ausente:470, presente:366} n=836 balanceado**. La obs. 2 (slide
  `histai_1132` sin features) **se auto-resuelve**: es no-invasivo → excluido; los 2 conjuntos nuevos verificados
  100% con features. Detalle: `auditoria_coherencia/hallazgos_sesion_reformulacion_sebastian_17jul.md` (R1-R4).
- **✅ Sebastián RESPONDIÓ (WhatsApp 17-jul 16:04-16:05):** **acepta la formulación nueva y los números tal cual**
  ("Perfecto" + "Ahí tendríamos los dos casos") — **el CDIS 85% positivo (no 132/si 730) queda ACEPTADO sin ajuste**;
  y a "¿los splits los regeneras tú o los armo yo?" respondió **"Si puedes, dale no más" → la generación de splits de
  CDIS/LVI queda de NUESTRO lado**. Cierra las 2 preguntas abiertas.
- **✅ EJECUTADO (17-jul tarde/noche, esta sesión):** (1) **splits CDIS/LVI `_ci_reform` GENERADOS + verificados**
  (`data/splits_kfold/{carcinoma_ductal_insitu_presente,invasion_linfatica_vascular}_ci_reform_100/`; script
  `build_cdis_lvi_ci_reform_splits.py`; reviewer PASA; 10/10 folds OK: 0 sin `.pt`, 0 dup, 0 fuga de paciente,
  cross-check regla 10; naming `_ci_reform` confirmado por Ernesto). (2) **snapshot tipo 3-clase** creado
  (`dataset_tipo_histologico_3clases_ci_label.csv`, 2027 slides, cubre exacto el `_ci` de Sebastián). (3)
  **entrenamiento de las 3 tareas LANZADO** — `run_b7_mammoth_interp_kfold.slurm` cableado (tipo reusa el `_ci`
  de Sebastián 3-clase; CDIS/LVI `_ci_reform` binarias; `max_epochs 200` + early stopping, corrige el `30` del
  draft) + prereg (regla 9) + reviewer #2 PASA → **job 4589 RUNNING** (30 runs: 3 tareas × {CLAM, Mammoth} × 5
  folds). Commits locales `1fe7436` (splits) + `acbae5f` (slurm/prereg/snapshot). Detalle:
  `auditoria_coherencia/hallazgos_sesion_generacion_splits_entrenamiento_17jul.md` (E1-E5).
- **✅ 18-jul — job 4589 CERRADO limpio** (14:20:55): 30/30 runs, 3 tareas `done`, 0 errores (solo
  `FutureWarning` benigno). **Paridad verificada:** md5 de los `slide_id` de test idéntico fold a fold entre
  brazos; 52 épocas por fold en ambos. Commits `684723b` (verdad de campo, 150 archivos) + `43480dc` (tooling
  + resultados). **Gotcha durable:** `tipo_histologico_4clases_ci_100` contiene **3 clases** (no 4; label_dict
  con strings completos); `max_epochs > stop_epoch` o el early stopping no dispara.
- **Métricas (política B5)** — detalle en `sprints/B7_sprint7/resultados_interpretabilidad.md`:
  tipo Δbal −0.010 ± 0.017 (1/5) y LVI Δbal −0.023 ± 0.086 (2/5) = **dentro del ruido**, confirman el
  Hallazgo 12. **CDIS `_ci_reform` = la "sorpresa" pre-registrada** (prereg §4, "a investigar, no a
  celebrar"): Δbal **+0.074 ± 0.033 (5/5)**, ΔAUC **+0.060 ± 0.042 (5/5)**; suben AMBOS recalls y el
  `val_loss` de Mammoth es menor en 4/5 folds. Frenan: n chico (65 negativos totales), formulación NUEVA no
  incluida en las 12 configs del Hallazgo 12, e invierte su patrón (gana la MÁS desbalanceada). **NO se
  reabre el eje de rendimiento** — exige regla 9.b.
- **✅ Entregable de atención producido** (7 slides TCGA, test de fold 0, bien clasificadas por ambos):
  Spearman 0.805 · Jaccard top-5% 0.172 · top-1% 0.073 · entropía CLAM 0.781 vs Mammoth 0.894 (6/7 con
  Mammoth más difuso) → **"mismo barrio, distintas casas"**. Tooling: `scripts/clam_vs_mammoth_attention.py`
  (+ `select_interp_slides.py`, `build_interp_task_table.py`, `answer_q1_expertos_slots.py`,
  `run_b7_expert_interp.sh`). Tabla por tarea lista (`tabla_por_tarea.md`, n coinciden con el prereg).
- **Hallazgos laterales:** (a) bug en el tooling OBJ-A — `patch_size_at_level0()` devolvía **512px** donde la
  geometría real del h5 es **448px**, y trata como 40× cualquier slide ≤20×; corregido derivándolo de la moda
  del paso entre coords ([[patch-size-desde-geometria-h5]]). (b) **TCGA no es homogénea en magnificación**:
  de 200/864 slides, 94.5% ~40× pero **3.5% nativas 20× → 224 µm por parche (el doble)**; extiende
  [[cohortes-magnificacion-fisica]] al interior de la cohorte.
- **✅ Q1 CERRADA (act. 19-jul, n=7/7).** El ruteo desatado (`setsid`, ppid=1) terminó limpio el
  18-jul 22:24 — el workaround J quedó validado en el caso real (antes murió 2 veces por colgar del
  shell, [[proceso-cpu-largo-desatado-setsid]]). Respuesta en
  `sprints/B7_sprint7/respuesta_q1_expertos_slots.md` y §5 de `resultados_interpretabilidad.md`:
  - **Expertos: 30.0 de 30 en las 7 láminas**, con `e50=15` / `e90=27` idénticos en todas (los valores
    exactos del reparto uniforme) → **E=30 NO está sobredimensionado**. Transversal a las 3 tareas; es
    el resultado sólido.
  - **Slots: 158.7 de 300** (sd 34.6, rango 89.7–196.4) → ahí está el margen de recorte.
  - **La dispersión NO es por tarea sino por TAMAÑO de lámina** (Spearman ρ=0.750, p=0.052; sin la
    lámina chica queda 170.2 ± 18.1). Las 2 láminas de CDIS son los **dos extremos**, lo que descarta
    el efecto de tarea. Con n=7 **describe, no establece**.
  - **Fix `f0d043e`**: el agregador globeaba `slot_usage.csv` (artefacto **intermedio**) y podía
    promediar una lámina en vuelo sin avisar; ahora filtra por `meta.json` y reporta las excluidas.
- **✅ Material de la reunión producido**: `sprints/B7_sprint7/material_reunion.md`, sanitizado y
  verificado (cero «—», sin nombres propios, sin jerga interna, comandos precisos —
  [[entregable-externo-sanitizado]]). Cubre entrenamiento pareado, atención, Q1, las 2 observaciones de
  datos y lo que queda abierto. Lleva la advertencia de que los nombres de tejido son lectura visual
  nuestra, no anotación.
- **QA visual hecho temprano** ([[image-api-qa-limit]]): `heatmap_montage.png` correcto (30 paneles,
  tejido alineado). **Observación para la presentación:** a esa escala los 30 expertos se ven muy
  parecidos entre sí y moteados; el mensaje "cada experto capta una morfología distinta" **no salta**
  visualmente como en OBJ-A. Consistente con "expertos uniformes", pero conviene saberlo antes de
  proyectarlo.

### Deck (correcciones para la próxima presentación, la verá también Benjamín)

- **RESUELTO (13-jul, commit `8926e5f`)**: la migración al template de Sebastián y las
  correcciones §2 de `correcciones_deck.md` **ya están aplicadas** en
  `presentacion_b7/generate_b7_deck.py` (re-base por construir a 10×5.625 y escalar
  ×1.3333, [[deck-rebase-plantilla-1610]]). Los checkboxes del checklist quedaron sin
  marcar pero el código los cumple: verificado 18-jul (cero «—» en texto de slide, sin
  nombres de guías, recap con layout de `Plantilla`).
- **Sección nueva agregada 18-jul (17 → 21 slides)**, commit `1c90b7f`: divisoria +
  métricas pareadas (balanced Y AUC juntas) + comparación de atención (lámina CDIS, el
  contraste de entropía más fuerte) + Q1 expertos/slots. Recap de objetivos ampliada a 6
  (tipografía 24 → 19pt para que entren). **La slide de Q1 lee sus números del JSON**
  (`respuesta_q1_expertos_slots.json`) en vez de hardcodearlos: si el análisis no está,
  marca el hueco en vez de inventar un número → regenerar el deck lo completa solo.
  Nomenclatura alineada a **CLAM / MAMMOTH** (el resto del deck y la propia figura los
  nombran; sanitizar aplica a personas, no a modelos).
- QA visual en LibreOffice hecho: corregido un solape donde el wrap de celdas hacía crecer
  la tabla de métricas sobre los paneles inferiores.
- **✅ Regenerado el 19-jul con Q1 dentro** (21 slides · 13.333x7.5). La lámina 16 lee sus
  números del JSON; se le agregó el **rango de slots al pie** para no sobrevender la media.
  QA visual de la 16 en LibreOffice: OK.
- **✅ Migrado el 19-jul a las DOS cabeceras reales de Plantilla** (commit `42280de`).
  Ernesto abrió el deck y no lo reconoció como el template. El volcado de las 30 láminas de
  `Plantilla.pptx` mostró por qué: usa **dos** cabeceras según el tipo de lámina, y las
  **técnicas (s04-s18) llevan la de OncoMets** (logo + línea teal), no la Environ. El deck
  usaba la Environ en todo y **7 de 21 láminas no llevaban cabecera alguna** — entre ellas
  la 5 (pipeline) y la 7 (arquitectura del paper), las dos del bloque que se iba a estudiar.
  Ahora: 17 técnicas con cabecera OncoMets, la recapitulación con la Environ, 4 portadillas
  en fondo teal con logo blanco, portada de Plantilla. De paso se resolvió el título de la
  lámina 16 (los títulos se toparon a 25pt, el tamaño de Plantilla; con los heredados los
  largos caían a 2 líneas y la 2ª quedaba cortada por la línea). Dos títulos se acortaron
  para entrar en una línea: la 14 y la 18. Detalle: [[plantilla-dos-cabeceras]].
- **✅ Re-basado el 19-jul (tarde) sobre el template VÁLIDO** (commit `170f7bd`). Ernesto
  volvió a abrirlo y **seguía viendo la plantilla anterior**, y fijó cuál es el archivo a
  respetar: **`Modelo OncoMets Spatial V1 Deep-LLM-V.pptx`**. La causa raíz resultó ser
  otra que la de la mañana: los templates **embeben sus fuentes** (`ppt/fonts/*.fntdata` +
  `embeddedFontLst`) y el generador construía con `Presentation()`, que no embebe ninguna.
  Sin Barlow, PowerPoint **sustituye la tipografía en las 22 láminas** y el deck se ve
  fuera de template aunque el branding esté perfecto. Ahora el deck se construye **sobre el
  .pptx del template** (se le borran las láminas y se hereda el paquete): verificado, 5
  `.fntdata` + Barlow y Cambria Math viajan en la salida. De paso:
  - **21 → 22 láminas**: la portada JPG cedió a las **dos láminas de apertura nativas**
    (portada de marca + título, retitulada con la fecha de la reunión).
  - Cabecera con **geometría literal** del template (verificada shape a shape contra su
    s04), no la compactada; `reflow_onco()` baja el contenido y lo escala ~8% si no entra.
  - La **recapitulación pasó a cabecera OncoMets** — Deep-LLM-V no tiene la Environ en
    ninguna lámina, y era la última con logo Environ en la banda.
  - Tres bugs cazados en el QA visual: la tabla de la lámina 7 se comía su leyenda (escalar
    solo geometría no encoge una tabla), el título quedaba `"OncoMets · MAMMOTH - Spatial"`
    (el texto del template viene partido en varios runs) y la pill "Escalas a definir"
    chocaba con los crops de tejido. Detalle: [[deck-template-fuentes-embebidas]] +
    `auditoria_coherencia/hallazgos_sesion_template_valido_19jul.md`.
- **✅ CERRADO el pendiente "¿Barlow está instalada?"**: ya no depende de la máquina de
  Ernesto, las fuentes viajan dentro del `.pptx`.
- **✅ Validado el re-base en PowerPoint** (Ernesto, 19-jul noche): el branding está.
- **✅ Migrado el CUERPO a la gramática Deep-LLM-V** (commit `3fb62fa`). El re-base de la
  tarde había migrado la **cabecera** y no el cuerpo: **18 de 22 láminas** seguían con la
  paleta de B4 (10 colores que el template no tiene, incluida una familia naranja entera) y
  las tiras de bloques estaban dibujadas **claro-con-texto-teal**, el negativo del molde.
  - Paleta remapeada por **valor** conservando los **nombres** de las constantes (no se
    tocan las ~700 líneas de `build()`). Helpers nuevos `_proc`/`_dato`/`_grupo`/`_conn`
    con los 5 arquetipos medidos sobre el template.
  - **Lámina 6 recreada NATIVA** (`pipeline_mammoth()`): venía copiada de B4 en Carlito con
    **129 runs bajo 10 pt** y no se salvaba con restyling. Horizontal, como la lámina de
    flujo general del propio template. Se dejaron fuera sus paneles de fórmulas (la 7 ya
    lleva esa matemática en tabla nativa) y se agregó la forma del tensor antes y después:
    las dos dicen `[N, 512]` = evidencia visual de drop-in.
  - Verificado: cero fills fuera de paleta, **Carlito 96 → 0**, **runs <10 pt 129 → 0**,
    fuentes embebidas intactas, sin colisiones nuevas.
  - Detalle: [[deck-gramatica-diagrama-deep-llm-v]] +
    `auditoria_coherencia/hallazgos_sesion_template_valido_19jul.md` §T6-T9.
- **El render de LibreOffice ya sirve para QA de este deck**: al salir las fórmulas del
  diagrama copiado, `Cambria Math` cae a 0 y desaparece el artefacto de
  [[pptx-qa-omml-libreoffice]]. Lo único que LibreOffice sigue sin poder juzgar es la
  **tipografía** (no tiene Barlow) → eso solo se valida en PowerPoint.
- **Inventario lámina por lámina** + agenda de reunión + qué no afirmar:
  `sprints/B7_sprint7/guia_estudio_b7.md` (punto de reentrada al sprint,
  [[guia-reentrada-al-cerrar-sprint]]). Su §5 ya está **renumerado a las 22 reales**
  (19-jul noche): el bloque pedagógico de Mammoth son las **láminas 4 a 10**.
- **Pasada de contenido visual (19-jul cierre, commit `bae7f8b` + tanda de cierre).**
  Feedback de Ernesto sobre **seis láminas a la vez**: bullets largos no, partirlos en
  cortos, agrandar la tabla y volver la lámina visual. Regla que salió de ahí: un bullet no
  se acorta, **se convierte en dibujo** si su contenido tiene forma
  ([[deck-contenido-visual-no-bullets]]).
  - **s01** (portada): se quitan **dos defectos que vienen DEL template** Deep-LLM-V, no del
    deck — el claim con marcador sin reemplazar («Care in <code>») y el párrafo descriptivo
    que se salía por el borde inferior. Se reproducen abriendo el template solo.
  - **s06** rediseñada sobre el molde de arquitectura del template (s11-s16): dos tonos de
    bloque, dimensión como etiqueta suelta, **expansión punteada** que abre MAMMOTH en sus
    4 pasos internos. **s08** sin título ni tira de dimensiones → la figura del paper pasa
    de 8.50 a 9.70 de ancho (**+30% de área**). **s09** esquema anidado + tabla a 12 pt.
    **s10** diagrama de bifurcación. **s17** barras de proporción (30/30 contra 159/300).
    **s19** eje de escala física en log. **s20** la cuenta µm/px como cadenas de bloques.
    **s21** tarjetas con barra de visibilidad + referencias en 3 grupos al pie.
  - Helpers nuevos (todos derivados de arquetipos medidos en el template): `ratio_bar`,
    `scale_axis`, `_proc_claro`, `_dim`, `_oper`, `_conn_dash`, `_rot_label`.
  - Verificado: **cero fills fuera de paleta, cero runs <10 pt, cero rayas largas**, fuentes
    embebidas intactas, 22 láminas. Ampliación de la gramática y gotchas nuevos (bbox de
    shape rotado, compresión de `reflow_onco` delatada por un run <10 pt):
    [[deck-gramatica-diagrama-deep-llm-v]] §ADDENDUM.
  - **Ernesto todavía NO validó esta pasada en PowerPoint.**
- **Revisión completa de las 22 láminas (20-jul, sesión limpia).** Barrido visual lámina por
  lámina + chequeos programáticos. El chequeo de conformidad daba **todo limpio** y aun así
  había **cinco defectos reales**, tres de ellos invisibles para el script por construcción
  ([[deck-qa-puntos-ciegos-chequeo]]). Corregidos:
  - **s13: colisión de texto real.** El pie en negrita se dibujaba encima del párrafo. La
    causa era redundancia de contenido, no geometría: pie y párrafo decían **los dos** lo del
    sign-off de patólogo. Deduplicado (el conteo de láminas pasó al párrafo, donde argumenta)
    → pie de una línea, colisión resuelta sin tocar el diseño.
  - **s11, s14, s18: el título de la portadilla pisaba su subtítulo.** Causa mecánica: la
    caja del título medía **1.1″** y una línea a 44 pt ocupa ~0.61″, así que **entraba UNA
    sola línea**; 3 de los 4 títulos envuelven a dos. La s04 se salvaba de casualidad porque
    «MAMMOTH» es una palabra sola. Caja a 1.45″, subtítulo a 3.42.
  - **`LAV_TITLE = #CDD6F4` fuera de paleta** en las 4 portadillas: lavanda de B4 que
    sobrevivió a la migración a Deep-LLM-V (única constante sin remapear, **con un comentario
    `(sin uso vivo)` que era falso** — la usa `divider()`). Pasada a blanco. El chequeo del
    handoff no la veía porque **solo audita fills, no colores de fuente**.
  - **s18: «Magnificación multi-» / «escala»** partido por el guion → guion no separable (U+2011).
  - **s08: notación que no se podía seguir.** El pie bautizaba los subíndices como `e`/`s`,
    letras que **no aparecen en la figura**: el paper usa **z_j^(k)** con *j* = slot (S=10) y
    *k* = experto (E=30). Verificado ampliando la figura a 200 DPI antes de corregir.
    Alineado a las variables del paper ([[deck-molde-fiel-referencia]]).
  - Chequeo final: 22 láminas · fills fuera de paleta **ninguno** · **colores de fuente fuera
    de paleta ninguno** (auditoría nueva) · runs <10 pt **0** · rayas largas **0** · Barlow +
    Cambria Math embebidas, 5 `.fntdata`.
  - **Queda vivo, sin resolver:** el tamaño de parche **baila entre tres láminas seguidas** —
    s19 tabula «Parche 256 px» (59/119 µm), s20 hace la aritmética con **224 px** (52/104 µm)
    y s22 fija la escala fina en **112 µm**. Cada número es correcto por separado (256 =
    extraído, 224 = entrada de CONCH, 112 = objetivo de la pirámide) pero **no hay puente**
    entre ellos: quien las vea en fila lee 119 → 104 → 112 para lo que parece la misma cosa.
    Es material de pregunta para Benjamín. Decisión de Ernesto, no tocada.
  - **Menor, registrado sin tocar:** la s16 tiene una raya larga **dentro del PNG** del
    heatmap (`clase si — rama 1`); el chequeo es estructuralmente ciego al raster. Y Consolas
    (bloques de código, s07/s10/s22) no viaja embebida — riesgo bajo, es fuente de Office.
- **✅ Pasada de `@humanizer-es` sobre el guion hablado (20-jul, commit `03cba8f`).** Pedido
  explícito de Ernesto, pendiente desde el handoff anterior. Las 21 láminas con notas, sobre la
  fuente versionada (el generador), no sobre el `.pptx` derivado. **El guion ya estaba limpio de
  vocabulario de IA** (cero «profundizar/robusto/abordar/panorama/sinergia») y con cero rayas
  desde `f9f1c0c` → lo que quedaba eran **tells de ritmo y de fórmula**, en racimo:
  - «conviene» como apertura formulaica **8 → 1** (sobrevive la s19, que es el uso genuino y
    calibra con la voz de los guiones B5, que lo usan una vez).
  - **Anunciar la honestidad en vez de ser honesto 5 → 0** («Con la honestidad por delante»,
    «una precisión honesta», «la quiero presentar con cuidado», «Lo digo como lo que es»). Se
    preservan **todos** los límites que esas frases introducían (cala chica, n=65 negativos,
    sign-off de patólogo pendiente): sale la ceremonia, no el contenido.
  - Aperturas «Esta es la / Este es el» **5 → 1** (la s08 queda: ahí es **deíctica**, señala la
    figura en pantalla). Tropos de autoridad **4 → 0** («el corazón del mecanismo», «la parte
    que quiero dejar clarísima», «lo notable es que», «un punto clave»). Aforismo de remate de
    la s13, reescrito como reclamo concreto.
  - **No tocado a propósito:** los seis quiasmos «X, no Y» («tejido, no clase», «contexto, no
    detalle») son **contrastes técnicos reales**, no el paralelismo retórico del patrón §9;
    aplanarlos costaba precisión. Idem los giros humanos («Fíjense en», «Mismo barrio,
    distintas casas») y los números hablados.
  - Guion **4026 → 3982 palabras (−1,1 %)** = la medida de que salió ceremonia y no contenido.
    Chequeo de conformidad en verde (fills · colores de fuente · <10 pt · rayas incl. notas) y
    fuentes embebidas intactas (5 `.fntdata`, Barlow + Cambria Math). Solo cambió el generador.
  - **Gotcha del método, nuevo:** la propia reescritura **introdujo** una repetición (s09 y s10
    abriendo las dos con «Hay una…»). Se cazó **listando las 21 aperturas en fila**, no
    releyendo lámina por lámina. Registrado en [[humanizer-es]] §ADDENDUM.
  - **Ernesto todavía NO validó esta pasada** (se suma a las tres anteriores sin ver).

### Preguntas abiertas resueltas (13-jul, citadas a código)

1. "top-k de slots por peso de ruteo" ≠ top-k de parches existente (usa `combine_weights`,
   softmax sobre 300 slots) → `preguntas_resueltas.md` §Q1.
2. Matemática magnif área↔µm/px↔parche (224@×20 ≡ 448@×40) → `contexto_magnificacion.md`
   (interpretación de Ernesto **A VERIFICAR** con Sebastián/código).
3. 16 cabezas × 30 expertos × 10 slots (NO 1 experto por cabeza) → `preguntas_resueltas.md` §Q3.

### Documentación de cierre (pedido de Sebastián)

- Guía/README para que Sebastián replique la extracción de heatmaps de expertos (§7 del
  prompt) — cronometrar 1 corrida CPU real. ✅ el `README.md` de la carpeta de
  interpretabilidad ya trae la guía + tiempo real medido (563 s CPU).
- ✅ **Entregable de revisión producido (15-jul):** `interpretabilidad_liviano.zip` (17 MB,
  gitignored) — copia curada de `sprints/B5_sprint5/mammoth_entendimiento/interpretabilidad/`
  para que Sebastián revise los heatmaps por su cuenta. Incluye `README.md` unificado y
  **sanitizado** (funde README+resultados, sin nombres ni jerga interna — nueva pauta
  [[entregable-externo-sanitizado]]); hojas de contacto en JPG q92 para pesar <25 MB.
  **Correo de revisión redactado** (papers microcalc + presentación + zip); lo envía Ernesto.
  Detalle: `auditoria_coherencia/hallazgos_sesion_entregable_interp_15jul.md`.
- ✅ `/knowledge-audit` (entregable + feedback) ejecutada 15-jul AM.
- ✅ `/knowledge-audit` 15-jul PM: corregida nota "Pendiente" stale que indujo re-pedir paths
  de magnif ya enviados; registrado el resultado del gate; nueva memoria de prevención
  [[verificar-antes-de-pedir-dato]]. Detalle: `auditoria_coherencia/hallazgos_sesion_magnif_paths_15jul.md`.
- ✅ `/knowledge-audit` 16-jul (esta sesión): inspección read-only de los `_ci` (C1-C7) → decisión de reuso,
  gotcha del plegado de no_id en binarias, blocker del slide sin features, SB6 resuelto. Memorias actualizadas
  ([[formulacion-cascada-gate-invasivo]], [[sprint7-interpretabilidad-clam-vs-mammoth]], [[data-gotchas-csv-wsi-interp]]).
  Detalle: `auditoria_coherencia/hallazgos_sesion_ci_inspeccion_16jul.md`.
- ✅ `/knowledge-audit` 17-jul (mañana): registrada la reformulación de CDIS/LVI (descartar no_id + restringir a
  WSI invasivas), números nuevos verificados en disco, C3 cerrado. (R1-R4).
- ✅ `/knowledge-audit` 17-jul (tarde, esta sesión): **cerradas las 2 preguntas abiertas** — Sebastián RESPONDIÓ
  (16:04-16:05): acepta el CDIS 85% **sin ajuste** + **nos deja regenerar los splits** ("dale no más"). R5:
  verificación independiente en disco (0 sin `.pt`, 0 dup, 0 fuga de paciente) + viabilidad `patient_strat` + plan
  de generación (script `build_cdis_lvi_ci_reform_splits.py`, naming `_ci_reform`). Reemplazado "esperando respuesta"
  en los 4 frentes. Detalle: `auditoria_coherencia/hallazgos_sesion_reformulacion_sebastian_17jul.md` (R1-R5).
- ✅ `/knowledge-audit` 17-jul (noche, esta sesión): registrada la **EJECUCIÓN** — splits `_ci_reform` generados +
  verificados (2 reviewers PASA), snapshot tipo 3-clase, entrenamiento de las 3 tareas lanzado (**job 4589**).
  Gotchas durables: tipo `_4clases`=3 clases; `max_epochs > stop_epoch`. Detalle:
  `auditoria_coherencia/hallazgos_sesion_generacion_splits_entrenamiento_17jul.md` (E1-E5).
- ✅ **Verdad de campo COMUNICADA a Sebastián por chat (20-jul, 12:01-12:20).** Ernesto le mandó, en 5 mensajes,
  el paquete verificable de lo que corrimos: splits generados (script productor + los 3 dirs + n por clase),
  snapshots de labels, el `.slurm` con el único delta entre brazos (`--model_type clam / clam_mammoth`),
  los resultados **por modelo** (balanced_acc y AUC de CLAM y de Mammoth en las 3 tareas) y dónde caen
  `summary.csv` / `split_N_results.pkl` / checkpoint, más la paridad por md5 de los `slide_id` de test.
  Todas las rutas se verificaron contra disco antes de enviarlas. **Salvedad NO incluida en el envío**: el
  matiz de CDIS (65 negativos, candidato a réplica y no mejora confirmada) quedó fuera; está en
  `resultados_interpretabilidad.md` §2 por si Sebastián repregunta. Pauta de redacción de chat:
  [[entregable-externo-sanitizado]] §ADDENDUM 20-jul.
- ✅ **Verificado 20-jul: la comparación de heatmaps CLAM vs Mammoth (el encargo de Sebastián) ESTÁ HECHA y
  ESTÁ EN EL DECK.** Se chequeó ante la duda de Ernesto ("no sé si está realizada e incluida"): las figuras
  existen para las 7 láminas de las 3 tareas (`attention_clam.png`, `attention_mammoth.png`,
  `attention_side_by_side.png` bajo `results/b7_mammoth_interp/interpretabilidad/<tarea>/<slide>/`) y el
  generador inserta el side-by-side en la **lámina 16 «Mismo barrio, distintas casas»**
  (`generate_b7_deck.py:191` y :1546-1589). **No re-abrirla como pendiente.**
- ➡️ **Nuevo pedido de Sebastián (20-jul, tarde) — heatmaps con vs sin `no_identificado`, lo ejecuta ÉL.**
  Sebastián propuso comparar heatmaps de la MISMA tarea en sus dos formulaciones (con y sin `no_identificado`)
  para tipo/CDIS/LVI y ver si el modelo mira lo mismo. **Es un eje distinto al CLAM vs Mammoth que ya
  entregamos.** Verificado contra disco en esta sesión (para poder responderle preciso): (1) los splits
  «con `no_identificado`» de las 3 **YA EXISTEN**, no hay que generar nada — **tipo** →
  `splits_5fold_balanced/tipo_histologico_4clases_pth_balance_100` (2815 = las 3 clases del `_ci` +
  `no_identificado` como 4ª; **sgaete ya tiene checkpoint fold-0** en
  `results_modelo_pth_balance/tipo_histologico_4clases_pth_balance_s1`, test_auc 0.844); **CDIS/LVI** → sus
  `_ci` tal cual (2815, `no_id` plegado al negativo). El CSV viejo `dataset_tipo_histologico_4clases_label.csv`
  (1396) es un corte anterior, **descartado**. (2) La «con» y la «sin» son **particiones distintas** (no
  anidadas salvo fold-0 de tipo, ~92% igual) → una lámina de heatmap debe caer en **test de las dos** para que
  ningún modelo la haya visto en train (intersección fold-0: tipo ~186, CDIS 7, LVI 3). (3) Matiz para
  interpretar el resultado, no bloqueante: en CDIS/LVI el «sin» (reform) además **restringe a invasivas**, así
  que una diferencia puede venir del `no_id` o de esa restricción. **Sebastián se encarga de este eje**
  (respuesta precisa enviada por chat); **nuestro foco sigue siendo CLAM vs Mammoth** (ya entregado) y el
  repaso pedagógico para la reunión. [[b7-splits-con-sin-no-identificado-ya-existen]].
- ⚠️ **LA REUNIÓN ES EL VIERNES 24, no el miércoles 22** (Ernesto, 22-jul: «el viernes hay reunión
  bisemanal con benja»). Las entradas anteriores de este archivo que dicen «miércoles 22» quedan
  **superseded**. **Pendiente que esto abre**: `generate_b7_deck.py:66` tiene
  `FECHA_REUNION = "22/07/2026"  # miércoles` **hardcodeada y se imprime en la lámina 2** → hay que
  corregirla y regenerar el deck. No se hizo en esta sesión (el deck no se toca sin pedido explícito).
- ✅ **Envío del heatmap CLAM vs Mammoth a Sebastián PREPARADO y ENVIADO (22-jul).** Ernesto pidió
  mandar **una sola imagen** con un mensaje corto. Elegida `tipo_TCGA-AC-A8OS_lobulillar.png`
  (carcinoma lobulillar invasivo): es la única que sostiene **las dos mitades** del mensaje a la vez
  (Spearman 0.885, de las más altas, con Jaccard top-5% 0.243), es una cuña de tejido limpia sin
  fragmentos sueltos que inviten preguntas de artefacto, y es de **tipo histológico**, así que no
  arrastra el punto delicado de CDIS. Descartadas: la CDIS positiva (masa grande y pareja, la
  diferencia no salta), la de `otros` (fragmento aislado al rojo vivo en ambos modelos) y la de LVI
  presente (Jaccard 0.008 pero correlación baja → rompe la mitad de «mismo barrio»).
  Paquete derivado (7 PNG renombrados + zip, **gitignorados**) y **mensaje canónico** en
  `sprints/B7_sprint7/envio_heatmaps/mensaje_sebastian.md`. Commits `72d2400`, `1356f21`, `3cd7fee`.
  **Enviado por chat 14:36-14:42**, pero Ernesto mandó sólo los 3 primeros párrafos: **quedaron
  fuera** el cierre interpretativo, la calibración del 0.243 contra el azar (0.026) y la salvedad de
  que el mapa no es ruteo de expertos. Si Sebastián repregunta, están en el `.md`.
- ✅ **Aclarado el mecanismo del heatmap (duda de Ernesto, verificada contra código).** El mapa **no
  es de un experto ni el promedio de los 30**: es la **atención de CLAM sobre los parches**, mismo
  mecanismo en los dos brazos (`CLAM_MB_Mammoth` hereda el `forward` de `CLAM_MB`). Con
  `keep_slots=False` los **300 slots ya vienen fundidos por parche** vía `combine_weights`
  (`mammoth.py:366`) **antes** de la atención. El artefacto per-experto es otro:
  `expertos/heatmap_montage.png`. Nueva memoria [[heatmap-atencion-no-es-per-experto]].
- ➡️ **Precisión sobre un pendiente menor ya registrado**: la raya larga «—» del título **está en las
  7 figuras**, no sólo en la de la lámina 16. Sale de `scripts/clam_vs_mammoth_attention.py:236`
  (el `suptitle`). Arreglarla exige re-correr el forward de las 7 láminas (CPU, ~70 min, desatado por
  workaround J) porque **las atenciones no quedan cacheadas en disco**: `attention_stats.json` sólo
  guarda escalares. Cosmético; se envió así.

#### Sesión de ESTUDIO del deck (23-jul) — láminas 3 y 5

- ✅ **Formato nuevo de las notas del presentador: punteadas por viñeta.** Ernesto pidió un punto
  numerado por cada viñeta de la lámina, separados por línea en blanco («para que al leerlas me sea
  más fácil visualmente»). Sigue siendo guion hablado; **no** son etiquetas de fase. Aplicado a las
  láminas 3 y 5 y validado («me encantó el punteo así»). ADDENDUM en
  [[notas-presentador-guion-didactico]].
- ✅ **Lámina 3:** el objetivo 1 pierde «y explicarlo con una analogía simple» (queda «Dominar el
  mecanismo de MAMMOTH»), y con eso el deck deja de prometer una analogía que había que entregar.
- ⚠️ **ERROR FACTUAL corregido en la lámina 5.** El pie de la Fig. 3 decía «cada color es el ruteo de
  un experto sobre la slide». Leyendo la figura real: los paneles están rotulados por **par
  experto+slot** (`Expert 16 Slot 4`) y la barra es `Patch-slot similarity`. **La morfología la
  captura el slot, no el experto** (e16·s1 alvéolos vs e16·s4 estroma) → nueva memoria
  [[slot-unidad-de-morfologia]] + precisión en CLAUDE.md Hallazgo 12. Decirlo «por experto» además
  contradecía la lámina 17.
- ✅ **Vocabulario:** fuera «blando»/«duro» (soft/hard routing, opacos para Ernesto) y «reclama» →
  **«concentra»** en las 9 apariciones del generador. ADDENDUM en
  [[deck-estilo-sin-rayas-ni-palanca]].
- ⚠️ **CORRECCIÓN de un enunciado que estaba en 3 docs:** «las dos láminas de CDIS son los dos
  extremos» es falso — 89.7 es el mínimo, pero el máximo 196.4 es de **LVI** (180.3 es la 2ª más
  alta). Reescrito como «cubren casi todo el rango solas». Corregido en `resultados_interpretabilidad.md`,
  `material_reunion.md`, `guia_estudio_b7.md` y CLAUDE.md. Registrado además que la tendencia con el
  tamaño **no es monótona** (la lámina más grande rompe el orden; por eso ρ=0.750).
- ✅ **Dato nuevo, triangulación de Q1:** 38.7 slots juntan el 50 % del peso y 164.4 el 90 %, contra
  `N_eff`=158.7 → dos medidas independientes convergen en ~160 de 300. Y los expertos están en el
  **techo teórico** (29.969-29.987 de 30 = 99.9 %), que solo se alcanza con reparto uniforme.
  En `resultados_interpretabilidad.md` §5 con la fórmula de `exp(entropía)` escrita para explicarla.
- ⏳ **Sebastián respondió y PREGUNTÓ (23-jul):** «lo que representarían los slots y cuántos
  deberíamos ocupar». Respuesta redactada en la voz de Ernesto, **sin enviar todavía**. La parte de
  «cuántos» incluye una **propuesta de experimento** (E=30, S=5 → 150 slots, paired sobre los mismos
  splits) que, si Sebastián acepta, **toca el modelo** ⇒ regla 9 + reviewer.
  [[sprint7-interpretabilidad-clam-vs-mammoth]].
- ⚠️ **La fecha del deck SIGUE mal.** Se ofreció corregirla dos veces en la sesión y Ernesto no se
  pronunció; no se tocó. **RESUELTO en la sesión siguiente** (ver abajo).

#### Sesión de ESTUDIO del deck (23-jul, tarde) — lámina 6

- ✅ **Fecha del deck CORREGIDA.** `generate_b7_deck.py:66` pasó de `"22/07/2026"  # miércoles` a
  `"24/07/2026"  # viernes`. Verificado por round-trip en la lámina 2. Cierra el pendiente que
  venía arrastrándose de la sesión anterior.
- ✅ **Lámina 6 («Dónde entra MAMMOTH en el pipeline») reescrita, 3 iteraciones.** El guion viejo
  era un bloque corrido que narraba **sólo la fila de arriba**: la expansión punteada, los 4 pasos
  internos y la frase del promedio ponderado quedaban dibujados y sin decir. Quedó punteado en
  **9 puntos, 717 palabras**, con el interior llevándose el 73 % del guion.
- ⚠️ **HALLAZGO de mecanismo, disparado por una pregunta de Ernesto.** Preguntó: *«si el tercer
  tramo del parche sólo se compara con el tercer tramo de los prototipos, ¿no deberían existir 16
  prototipos, uno por cabeza?»*. La respuesta, verificada contra `mammoth.py`: **no**. `slot_embeds`
  es `(e,h,s,d)=(30,16,10,16)` ⇒ **300 prototipos, cada uno cortado en los mismos 16 tramos** que el
  parche, y el `einsum` de `get_logits` deja `h` compartido ⇒ **16 tablas de N×300, no una** ⇒
  **4800 parecidos por parche**. Nueva memoria [[mammoth-cabezas-son-tramos]] + ADDENDUM en
  [[mammoth-slot-routing-weight]] (`combine` normaliza **por parche Y por tramo**, no globalmente).
- ⚠️ **Dos defectos del guion que esa pregunta destapó**, ambos corregidos: (1) decir «una tabla de
  parecidos contra los 300» **después** de explicar el corte en tramos **se contradice solo**;
  (2) el guion llenaba los slots y saltaba al concat **sin contar nunca cómo el parche recupera su
  vector** (se había perdido el abanico). La reconstrucción quedó explícita: mezcla convexa de los
  300 slots ya transformados, pesada por el parecido, y **sin conexión residual** (el parche
  sobrevive sólo a través de esos parecidos). Cierre aritmético: 256 = 16×16 a la entrada,
  512 = 16×32 a la salida.
- ✅ **Las cabezas, que fueron la confusión de la reunión pasada, ocupan ahora 3 puntos enteros.**
  La estrategia que funcionó es **desmontar primero la lectura equivocada** («no es que una mire el
  color y otra la textura») y recién después dar la correcta, más el ejemplo numérico del corte
  (1 al 16, 17 al 32). Reacción: *«ahora sí quedó mucho más claro»*.
- ⏳ **Menor, ofrecido y no respondido:** la lámina 5 dice «una tabla de parches contra prototipos»
  y difiere explícitamente («ahí vamos a volver con las dimensiones puestas»), promesa que la 6
  ahora cobra. Funciona por el diferimiento, pero se puede dejar sin filo con una frase en la 5
  («una tabla de parecidos, que después vamos a ver que son dieciséis»).
- ⏳ **«drop-in» salió del guion de la 6**, reemplazado por lo que hace («el resto del modelo no se
  entera del reemplazo»), por la regla de vocabulario del 23-jul. Sigue en la tabla de la lámina 7
  (`combine → salida drop-in`). Se ofreció reponerlo y Ernesto no se pronunció.

#### Sesión de ESTUDIO del deck (23-jul, noche) — lámina 6 cerrada, lámina 7 ABIERTA

- ✅ **Lámina 6 CERRADA.** Recortada a **6 puntos / 458 palabras** (venía de 9 / 717). Salieron: la
  narración de la tabla de parecidos leída «por filas y por columnas» (Ernesto: *no hay respaldo
  visual en esa lámina y no quiere agregarlo*, la 7 fija la idea con el código) y la imagen del
  **embudo y el abanico**, que rechazó. Las dos lecturas se nombran ahora por lo que hacen, llenar
  los slots y rearmar el parche. Reacción: *«quedaron excelentes»*.
  - Se cayeron dos cosas, **ofrecidas y sin respuesta**: la frase «el tejido no vive en la cabeza,
    vive en el slot» (adelanto a la interpretabilidad) y las 4800 comparaciones por parche.
- ⚠️ **HALLAZGO — el guion de la lámina 7 leía `slot_embeds` como una jerarquía FALSA.** Decía
  «treinta expertos, cada experto con dieciséis cabezas, cada cabeza con diez slots», que implicaría
  **30×16×10 = 4800 slots** y **contradecía el pie impreso en la propia lámina** («30 expertos × 10
  slots = 300»). Verificado: `slot_embeds = nn.Parameter(torch.randn(num_experts, num_heads,
  num_slots, head_dim_input))` = `(30,16,10,16)`, `mammoth.py:281`. Los prototipos son **300**
  (`e × s`); los otros dos ejes describen a cada uno **por dentro**, cortado en los mismos 16 tramos
  de 16 que el parche. ADDENDUM en [[mammoth-cabezas-son-tramos]].
- ⚠️ **HALLAZGO — el guion cruzaba `dispatch` con `combine`.** Decía que el dispatch «reparte cada
  parche entre los slots»; eso es el combine. Verificado `mammoth.py:410`:
  `dispatch_weights = F.softmax(logits, dim=1)` sobre `(b,n,e,h,s)`, o sea el eje **n**. Corregido.
- ❌ **Lámina 7 NO CERRADA — es el pendiente central.** Tres pasadas (punteo → corrección del
  anidamiento → `@humanizer-es`) y **los puntos 2, 3, 4 y 5 siguen sin entenderse**. Ernesto la
  declaró *«super importante»*. Lo que aprendimos de los intentos fallidos está en el ADDENDUM 2 del
  23-jul de [[notas-presentador-guion-didactico]]: el guion **narraba la tabla fila por fila** (5 de
  5 aperturas eran «La X fila…»), y humanizar arregla ritmo pero **no arregla comprensión**.

#### Sesión de ESTUDIO del deck (23-jul, madrugada 24) — lámina 7 CERRADA

- ✅ **Lámina 7 CERRADA en dos rondas más.** Reescritura completa de los puntos 2 a 6 del guion con
  la estrategia de la lámina 6 (desmontar la lectura equivocada → dar la correcta → mini-ejemplo
  numérico) + amarrar **cada punto a su línea del código por nombre** (`dispatch`, `expert_heads`,
  `combine`). El guion pasó de 5 a **6 puntos** (cada uno una sola operación) y de ~623 a **~510
  palabras**. Cómo se destrabó: ADDENDUM 3 de [[notas-presentador-guion-didactico]].
- ✅ **Cambios en la lámina misma (no solo el guion), resolviendo 3 decisiones que estaban abiertas:**
  (1) la fila `S · prototipos (slot_embeds)` → **`S · 300 prototipos de 256`** (el 300 impreso mata
  el anidamiento falso en el origen; la forma `[30,16,10,16]` queda como dato al lado); (2) el pie
  dejó de repetir «30×10=300» y ahora dice lo que sí necesitaba respaldo visual — **los tramos no se
  cruzan y salen 4800 parecidos por parche** (se había caído al recortar la 6); (3) `drop-in` salió
  de la tabla (`combine → salida por parche`) y del comentario del código (`keep_slots=False (camino
  base)`), por la regla de vocabulario.
- ⚠️ **Feedback de vocabulario (2ª ronda):** Ernesto pidió *«más preciso y profesional»* y rechazó
  dos coloquialismos — **«flaca»** (matriz de bajo rango) → «de bajo rango / dos matrices de rango
  pequeño (LoRA)»; **«al revés»** (la reconstrucción) → «la segunda softmax, el combine, simétrica a
  la del dispatch». Registrado en [[deck-estilo-sin-rayas-ni-palanca]] ADDENDUM 2.
- ⏳ **Próximo: la lámina 8**, la figura del paper — y detrás la **9** («la relación 16×30×10»,
  esquema anidado + tabla grande), que es **la más densa del deck**. El punto 6 de la 7 ya entrega a
  la 8 («en la lámina siguiente lo vemos dibujado por los autores»).
- ℹ️ **Untracked de sesión paralela (NO commiteados por esta sesión):**
  `scripts/build_slot_softmax_tables.py` + `sprints/B7_sprint7/slot_softmax/*.csv` (13:35-13:36 hoy).
  Material para la respuesta a Sebastián (2ª softmax por slot, `combine_weights` sobre los 300);
  no son de esta sesión, se dejan intactos para quien los creó.

---

## Eje que continúa de B6 — Magnificación multi-escala (CONCH) sobre CLAM (pipeline armado, NO lanzado)

**Abierto 6-jul-2026.** Nace de la reunión con Sebastián del **2-jul**: aprobada la
dirección **magnificación / contexto espacial** (Eje A, la única que inyecta *señal
nueva* tras cerrar los 4 ejes de arquitectura, 0 palancas). Equipo = Ernesto +
Sebastián. Foco declarado por Ernesto: **mammoth + CPathAgent con CLAM como base** —
donde lo accionable de CPathAgent es su **baseline MIL multi-escala** (Ap. C.1.2), NO
el agente LMM. Insumo: `sprints/B5_sprint5/magnificacion/analisis_cpathagent.md`.

> *(Nombre B6 = continuación natural de B3→B4→B5; renombrable si Ernesto prefiere otra
> convención para el trimestre nuevo.)*

### Decisiones de la reunión (2-jul) — lo que Sebastián fijó

1. **GO** a probar CLAM con features CONCH extraídas a **varias magnificaciones**
   (pirámide por región, estilo CPathAgent: parche grande → sub-parches más finos).
2. **Restricción de costo**: la extracción CONCH es lenta → **acotar a una tarea con
   POCAS WSI = microcalcificaciones**, y correrla en un **fin de semana**.
3. **Decisión delegada a Ernesto**: **qué magnificaciones/resoluciones** usar y, según
   eso, **cómo fusionarlas** (promedio u otra).

### Objetivo headline — magnificación multi-escala, paired vs CLAM single-scale

| Aspecto | Definición |
|---|---|
| Tarea | **microcalcificaciones** (las 3 binarias, `_pth` 333 identificadas; pocas WSI = cabe en un fin de semana) |
| Baseline | CLAM single-scale actual (parche 256 @ level0, CONCH 512) — reusar los **mismos splits k=5** ([[patron-paired-comparison-reuso-splits]]) |
| Variable de estudio | features CONCH **multi-escala fusionadas** por región |
| Métrica | balanced_acc **Y** AUC juntos + matriz de confusión + n/clase (regla eval B5), Δ **pareado** por fold |
| Gobernanza | toca el data-pipeline (extracción) → **regla 9 + reviewer + sbatch** + preflight; cortesía single-GPU |

### Decisión de diseño pendiente (tuya) — escalas + fusión · con recomendación

**Estado hoy (verificado, regla 5):** escala única — `create_patches_fp.py`
`patch_size=256`, `step_size=256`, `patch_level=0`; `extract_features_fp.py`
`target_patch_size=224` → CONCH 512. `CLAM_MB` recibe `[N,512]`.

- **(a) ¿Qué magnificaciones?** El paper usa región 2048 @40× + 4×1024 + 16×512
  (promediados). Para microcalc (features chicas, lo que falta es **contexto**
  arquitectural alrededor) propongo empezar con una pirámide de **2–3 escalas**: la
  fina actual (256) + una/dos **más gruesas de mayor campo** (p.ej. 512 y 1024,
  downsampleadas a 224 para CONCH) que cubran más tejido por parche.
  - ✅ **Bloqueador RESUELTO 2/3 (10-jul, openslide)**: **TCGA ≈40× (0.2325 µm/px)**,
    **privado ≈20× (0.465 µm/px)** → difieren 2×; **HistAI sin MPP confiable (pendiente)**.
    Confirma que la pirámide se define en **µm/px físicos, no en `level`**, y que el single-scale
    actual ya mete un confound (TCGA a CONCH a ~40×). Ver [[cohortes-magnificacion-fisica]] +
    `magnificacion_microcalc/investigacion_magnificacion.md` §4–§5.5.
- **(b) ¿Cómo fusionar?** Recomiendo **promedio por región** (como el paper): fusiona
  las escalas en **un token `[N,512]`** → **CLAM_MB queda intacto** y la comparación es
  la más limpia (mismo bag, solo cambia el contenido del token). Alternativas
  (multi-token / concatenación) cambian la forma del bag y meten un confound extra →
  dejarlas para una 2ª iteración solo si el promedio muestra lift.
- **Expectativa honesta a pre-registrar** (regla 9): lift probablemente **chico** y
  ortogonal al agregador — el propio paper gana solo **+2.9% vs ABMIL multi-escala** y
  **no rompe el techo de datos**. Se justifica porque inyecta señal nueva (contexto),
  no por promesa de salto. Dirección esperada: Δ pareado ≥0 consistente en signo;
  Δ<0 consistente = la fusión no ayuda en microcalc.

### Próximos pasos (orden recomendado)

**Sesión 10-jul (tarde) ejecutó los pasos 1-4 hasta dejar el `.slurm` listo. NADA lanzado a GPU,
nada commiteado/pusheado (pendiente OK + pase formal del reviewer).**

1. ✅ **Tier 0 calibración post-hoc EJECUTADA** (`sprints/B6_sprint6/tier0_calibracion/`,
   `scripts/tier0_calibration.py`, CPU, umbral en val→congelado a test, paired k=5).
   Resultado: **mitotic Δbal +0.046 ± 0.029 (5/5 folds+)** — win consistente donde el modelo
   colapsa al argmax (Hallazgo 13); **invasión null** (+0.009, y el drift de features lo deja bajo
   el histórico); **necrosis null** (−0.005). Palanca real pero task-dependiente. Caveat colateral:
   **features TCGA re-extraídas 26-27 jun** (dir live) → surfacear con Sebastián.
2. ✅ **HistAI resuelto operativamente** (`histai_magnificacion.md`): `generic-tiff`, MPP no
   recuperable (placeholder), dims ~40× no concluyente → **excluido del piloto** (49/45 slides,
   minoría); el wrapper lo salta solo. TCGA+privado (283) = donde vive el contraste.
3. ✅ **Pre-registrado** (`prereg_magnificacion.md`, regla 9): 3 brazos paired (A single-scale
   re-entrenado / B0 fine-only@grid común / B multiscale-fused), escalas 112µm+512µm en µm/px por
   cohorte, fusión promedio, hipótesis H1/H0/H2, eval bal_acc+AUC.
4. ✅ **Wrapper + `.slurm` listos** (NO lanzados): `scripts/extract_multiscale_features.py`
   (bug openslide+workers corregido), `extract_multiscale.slurm` (preflight + stage1 patching +
   stage2 extracción B0/B), `microcalc_slidelist_tcga_privado.csv` (283 slides).
5. **Los 4 gates (sesión 10-jul tarde-noche):**
   - ✅ **(a) pase FORMAL del reviewer** — **APRUEBA CON OBSERVACIONES**. Regla 9/9.a íntegras, 9.b N/A,
     containment + workflow SLURM OK, comparación paired, código correcto en todas las rutas load-bearing.
     5 observaciones, ninguna bloquea: O1 conteo (283, corregido), O2 dry-run (=gate c), O3 preflight
     minpatch en stage-3, O4/O5 cosméticas. Detalle: `review_regla9.md`.
   - ✅ **(c) dry-run CPU de stage-1** — **cazó un bug bloqueante**: `create_patches_fp` re-lee el
     `--process_list` con `pd.read_csv` sin dtype → slide_id privados numéricos (105040) → `int64` →
     `get_clean_slide_name` crashea → **se caería toda la cohorte privada (76)**. **FIX** (no toca
     clam_environ): stage-1 pasa a **symlink-farm plano** sin `--process_list`/`--nested_folders`.
     Verificado end-to-end TCGA+privado (`.h5` con stem=slide_id, attr patch_size 482/241). §Gate (c) en `review_regla9.md`.
   - ⏳ **(b) co-firma de Sebastián sobre las escalas** (112µm/512µm, fusión promedio) — reunión **13-jul
     OCURRIÓ y salió bien** (deck presentado); gate NO bloqueante ([[gobernanza-gate-cofirma-sebastian]]).
     **NO asumir el resultado de la co-firma:** los objetivos del sprint 7 + las correcciones de slides
     los aporta Ernesto la próxima sesión → no lanzar el multi-escala sin su OK explícito ([[surface-premise-discrepancies]]).
   - ⏳ **(d) OK explícito de Ernesto para `sbatch`** + cortesía single-GPU (`squeue` antes). Job de fin de semana.
     **12-jul: Ernesto DECIDIÓ ESPERAR la co-firma (b) del lunes antes de lanzar** — se le presentó el
     análisis de viabilidad (era viable lanzar el fin de semana con su OK, co-firma no bloqueante) y
     optó por presentar el pre-registro a Sebastián primero y lanzar después con su visto bueno de las
     escalas. NADA lanzado a GPU. El pipeline sigue armado (stage-2 + stage-3 encadenable). Detalle:
     `auditoria_coherencia/hallazgos_sesion_deck_magnif_12jul.md`.
   - ✅ **stage-3 `.slurm` PREPARADO** (`train_multiscale_stage3.slurm`, NO lanzado): CLAM_MB paired
     3 brazos (A/B0/B) × 3 binarias × 5 folds = **45 runs** reusando `splits_kfold`; **preflight minpatch**
     por fold (O3); **backfill del pairing** (symlink de las 45 HistAI single-scale en B0/B → los 3 brazos
     cubren las mismas 328 slides). Validado `bash -n` + python embebido compila. Depende de stage-2 (chequeado en preflight).

### Ejes vivos en paralelo (menor prioridad)

- **Interpretabilidad mammoth (OBJ-A)**: pendiente **sign-off de patólogo/Sebastián**
  sobre los top-k (cierra la métrica de la hipótesis). Eje ortogonal, no rendimiento.
  [[mammoth-interpretabilidad-objA]].
- **Deck reunión viernes 10-jul (eje Benjamín = entender/interpretar mammoth)**:
  CONSTRUIDO 9-jul + **2ª ronda de ediciones 10-jul** — 11 slides, formato B4,
  `sprints/B6_sprint6/presentacion_viernes/generate_b6_deck.py` (el `.pptx` y los
  assets `papers/presentations/` son derivados **gitignored**, locales a este server).
  Ronda 2: recap con **marcadores de estado** (check verde / pill "En progreso") y
  **objetivos reescritos** (infinitivo, sin resultados); **s7** rehecha (figura del
  paper GRANDE y limpia, sin logo/título ni callouts encima, + `dim_pipeline` de
  dimensiones en la notación de la figura); **s11** con imágenes cross-slide
  agrandadas; **notas del presentador humanizadas** en las 11 slides. Convenciones +
  mapa vigente en `convenciones_deck_b6.md` **§7**; hallazgos ronda 2 en
  `auditoria_coherencia/hallazgos_deck_10jul.md`. **Pendiente**: QA fino en
  **PowerPoint** (OMML del diagrama s5) + ensayo del guion. [[deck-molde-fiel-referencia]].
  **EXTENDIDO 12-jul (pedido de Ernesto)**: se anexó la **sección MAGNIFICACIÓN multi-escala**
  para la reunión con Sebastián (lunes) — estudio + referencias microcalc + imágenes didácticas
  (esquema nativo + crop real 2 escalas vía `render_multiscale_crop.py`) + **la decisión de
  escalas** (para que Sebastián guíe las dimensiones). Aditivo (no toca mammoth).
  **AJUSTADO 13-jul (pedido de Ernesto)**: la sección se comprimió a **4 slides** (deck **11→15**):
  se **eliminó** la slide de diseño pareado/expectativa y se **fusionaron** contexto + hallazgo
  físico en una sola de dos columnas; limpieza de estilo (fuera «—» y «palanca» en la sección).
  Re-QA LibreOffice 4/4 (slides 12-15). Detalle: `convenciones_deck_b6.md` §8.
- **Palancas de datos de reserva** si la magnificación no basta: **HistAug**
  (augmentación en espacio de features, verificar CONCH v1 512) y **TITAN** (caro,
  re-extrae CONCHv1.5 768). [[insuficiencia-datos-ejes-investigacion]].

### Sesión 23-jul (tarde) — softmax por slot + reunión con Sebastián

- **Generado**: tablas de la 2ª softmax por slot (`sprints/B7_sprint7/slot_softmax/`:
  300 slots por tarea + `slot_softmax_resumen.csv` + mini **por lámina**) y **mapas de
  calor por SLOT** (`slot_heatmaps_<tarea>.png`), vía `scripts/build_slot_softmax_tables.py`
  y `scripts/slot_heatmaps_contraste.py`. Todo CPU post-hoc. Detalle:
  `resultados_interpretabilidad.md` §5.2.
- **Medido**: los slots top **no son redundantes** (corr. espacial media −0.00 entre los
  top-8; #1 vs #2 = **−0.62**, regiones opuestas) → evidencia propia de
  [[slot-unidad-de-morfologia]], que antes se apoyaba solo en la Fig. 3 del paper.
- **Medido**: la **anatomía del desacuerdo** CLAM/Mammoth (§3.1) — los parches en disputa
  del top-5 % están en el **percentil 10-17 %** del otro modelo, **0 %** en la mitad
  inferior; la cola alta está aplastada (#210 pesa 1.20× el #420 en Mammoth). Explica
  ρ=0.885 con Jaccard=0.243 sin contradicción.
- **Reunión con Sebastián (14:30): salió bien, le gustó el trabajo.** Pidió incorporar
  tablas + mapas al deck del 24-jul. Acuerdos y encargos completos en
  `sprints/B7_sprint7/reunion_23jul_acuerdos.md`.
- ~~PENDIENTE (delegado a sesión limpia)~~ → **HECHO la misma noche del 23-jul** (ver
  bloque siguiente).
- **Eje siguiente (post-presentación)**: «perillar» E y S de Mammoth para mama —
  reducir uno con el otro fijo a igual total (27×10 vs 30×9 = 270) sobre las 3 tareas.
  Regla 9 + reviewer + paired sobre los splits del 4589. [[mammoth-grid-expertos-slots]].

### Lo que NO se reabre (cerrado con argumento)

- Otro agregador / otro patch-embed / "mammoth #3" → null garantizado (Hallazgos 11/12).
- El agente LMM de CPathAgent → fuera de presupuesto (8×H800 + Gemini + reportes pareados).

### Reglas que gobiernan el sprint (de CLAUDE.md)

- Argumento antes de código (regla 9 + 9.a/9.b) + reviewer antes de commitear
  modelo/training/data-pipeline.
- Comparación PAIRED por reuso de splits ([[patron-paired-comparison-reuso-splits]]).
- Reportar SIEMPRE balanced_acc Y AUC juntos + confusión + n/clase (política eval B5).
- GPU solo vía `sbatch`; cortesía single-GPU; preflight obligatorio; workspace containment.
- Entregables: notas concisas, guion hablado, sin nº de job, baselines "Environ vX".

### Sesión 23-jul (noche) — encargos de la reunión ejecutados, deck a 24 láminas

Ejecutados los puntos **§1 a §5** de `sprints/B7_sprint7/reunion_23jul_acuerdos.md`.
Todo CPU post-hoc, read-only sobre artefactos ya existentes (regla 9 no aplica).

- **Mapas regenerados con el top-4 PURO del ranking.** `pick_diverse_slots` queda en
  `scripts/slot_heatmaps_contraste.py` pero **sin llamarse**. Los slots dibujados ahora
  calzan 1:1 con las 4 primeras filas de la tabla mini.
- **Respondida la pregunta de Sebastián** («¿los slots de un mismo experto ven lo mismo?»):
  198 pares de correlación espacial, 6 del mismo experto. **`e28·s4` (#1) vs `e28·s5` (#4)
  en CDIS da −0.56** (regiones opuestas). Pero no es regla: `e13·s6` vs `e13·s5` da +0.71.
  Los hermanos cubren −0.56 a +0.71, casi el rango entero de los no-hermanos (−0.78 a
  +0.89). Media +0.26 vs +0.04, **con n=6 describe, no establece**.
- **Cota sobre la softmax definida: el reparto uniforme, 1/300 = 0.333 %** (único corte sin
  parámetro libre). Da **63 a 96 slots por lámina** que concentran el **73 %** del peso;
  estable entre las 3 tareas. Nuevo `scripts/slot_cota_softmax.py` +
  `slot_softmax/slot_cota_por_lamina.csv`. [[cota-softmax-slots-uniforme]].
- **Deck: 22 → 24 láminas.** Nuevas **18** («Dónde se concentra cada slot»: las 3 tiras +
  tabla nativa al lado, con el % y el 15 % explicados) y **19** («Una cota para decidir qué
  slot aporta»: corte a ojo vs cota, tabla por tarea, idea general de entropía y el efecto
  del tamaño de lámina). Ambas con guion hablado y QA rasterizado mirado.
- **Dos defectos cazados por el QA visual** (el chequeo programático no los ve): el
  `suptitle` de las figuras se montaba sobre los títulos de panel (faltaba el `rect` en
  `tight_layout`), y los rótulos a 11 pt aterrizaban en ~3.5 pt proyectados. De ahí la
  variante `_deck` de cada PNG (sin suptitle, rótulos ~3× más grandes) y el ancho
  **adaptativo** al alto real de las tiras en la lámina 18.
- Detalle técnico completo: `resultados_interpretabilidad.md` **§5.3**.

### Sesión 23-jul (noche, 2ª) — guion de la 8 a la 24 y tipografía Barlow

Sesión de deck, sin GPU ni CPU pesado. Commits `f88e891` y `1421868`.

- **Guion hablado reescrito de la lámina 8 a la 24** (5.962 palabras en total) con la
  lógica de las láminas 5 a 7: párrafos numerados que recorren la lámina en su orden
  visual, cada una abriendo con el cierre de la anterior. Antes venían en un bloque único
  (la 8, con 617 palabras) o demasiado cortas para lo que muestra la lámina.
- **Cinco correcciones de fondo, no de estilo:**
  - **Lámina 9**: ata el `16 × 30 = 480` impreso en la lámina a los **4800** parecidos por
    parche de la lámina 7. Son cuentas distintas (pares cabeza-experto vs comparaciones),
    y sin el puente las dos láminas se contradecían. Era el riesgo registrado en el
    handoff de las 13:47.
  - **Lámina 13**: decía «con esta prueba cierra la presentación» con once láminas por
    delante. Ahora cierra la parte de interpretabilidad y entrega a la 14.
  - **Lámina 12**: suma la salvedad de que los nombres de tejido son lectura visual
    nuestra, que ya estaba escrita en la lámina y faltaba en el guion.
  - **Lámina 21**: sale «al revés», del vocabulario vetado.
  - **Lámina 15**: se lee por la columna de la diferencia pareada (convención de láminas
    de resultados, `convenciones_deck_b5.md` §3.b regla 11).
- **Tipografía: TODO el deck en Barlow** (pedido de Sebastián). `F_MONO` deja Consolas y
  se agrega `forzar_barlow(prs)` al generador, porque poner Barlow en los runs **no
  alcanza**: el `fontScheme` del theme es el de Office (Arial) y las láminas heredadas del
  template traen Calibri en `endParaRPr`/`buFont`. Verificado sobre el `.pptx`: 1.172
  referencias forzadas, cero Calibri, cero Consolas. Detalle y método de verificación en
  [[deck-template-fuentes-embebidas]] (ADDENDUM 23-jul noche).
- **Queda fuera de Barlow lo que no es texto del `.pptx`**: los rótulos dentro de los PNG
  de matplotlib (mapas por slot de la lámina 18, figuras de atención de la 16). Pendiente
  para la próxima sesión, junto con instalar la fuente en el servidor.

### Sesión 23-jul (noche, 3ª) — Barlow instalada y QA tipográfico fiel

Sesión de deck, sin GPU ni CPU pesado. Sin cambios al `.pptx` ni al generador.

- **Barlow instalada bajo containment** (Ernesto autorizó la descarga): 18 TTF en
  `clam_testing2/fonts/barlow/` desde el repo `google/fonts`, más
  `clam_testing2/fonts/fonts.conf`, que **hereda** `/etc/fonts/fonts.conf` y le suma el
  directorio. Se activa por `FONTCONFIG_FILE`. Huella cero fuera del workspace: sin la
  variable, `fc-list | grep -ci barlow` sigue en **0**, y las 574 del sistema quedan
  intactas. Procedimiento completo en `presentacion_b7/fuentes_barlow.md`.
  - Gotcha: `fonts.google.com/download?family=Barlow` devuelve **HTML**, no un zip. Los
    TTF salen de `raw.githubusercontent.com/google/fonts/main/ofl/barlow/`.
- **El rasterizado local ya sirve para juzgar tipografía.** El PDF de LibreOffice embebe
  `Barlow-Regular` y `Barlow-Bold` reales (antes sustituía). **Matplotlib** también la ve
  vía `font_manager.addfont()`, así que regenerar los PNG está de-riskeado.
- **Barlow no trae 4 glifos** del deck y caen a DejaVu: `→` (7 láminas), `⟨⟩` (7), `≡`
  (22) y el guion duro U+2011 (20). Mirado rasterizado en la 7 y la 22: indistinguible, y
  PowerPoint sustituirá igual. **No es defecto**; es el límite real de "todo en Barlow".
- **QA visual** de las láminas 1, 7, 18 y 22. Nada desborda. La **18** muestra el único
  choque tipográfico visible del deck: rótulos de PNG en DejaVu (ancha) contra la tabla
  nativa en Barlow (condensada), lado a lado. **Ernesto decidió NO regenerar los PNG**
  antes de la reunión; queda como pendiente.
- **Verificado que el `112 µm` de la lámina 24 no es un error**: es la escala fina
  propuesta de la pirámide, con su cuenta propia coherente (`112/0.2325 = 482 px` en
  TCGA, `112/0.465 = 241 px` en privado, ambos impresos). La 22 habla del campo de HOY
  (`224 × 0.465 = 104 µm`). El pendiente 7 del handoff sigue siendo de **puente
  narrativo**, no de aritmética, y el puente natural es que 112 ≈ 104.
- **Observación sin accionar** (no se barrió, Ernesto no lo pidió): el pie de la lámina 18
  dice «Dos slots del mismo experto encienden regiones distintas», que se lee como
  afirmación general; `e13·s6` vs `e13·s5` da **+0.71**. Ver §8 del handoff.

---

## Reunión del 24-jul-2026 (viernes) — B7 presentado, se abre B8

Presentación del Sprint 7 ante **Sebastián y Benjamín**. Según Ernesto, **la mejor
reunión hasta ahora**: quedó demostrado el entendimiento del mecanismo al explicar
slots, expertos, cabezas y el diagrama original del paper, que es lo que Benjamín
venía exigiendo ([[feedback-benjamin-entender-mammoth]]). Los mapas de calor fueron
el material central, tanto el de los 30 expertos como los de slots; ahí estuvo el
hilado fino.

**Encargos para el sprint siguiente** (registro completo, con verificaciones,
presupuesto de GPU y restricciones: `sprints/B8_sprint8/objetivos_sprint8.md`):

1. **Escalar la medición de slots ocupados.** Benjamín observó que el promedio de
   **158.7 slots útiles de 300** sale de **7 láminas** y no generaliza a la tarea
   entera. Objeción correcta y coherente con lo que ya decíamos («con n=7 describe, no
   establece»). **Camino despejado:** la medición **no necesita la WSI**, features y
   coords salen del mismo h5 (`mammoth_interpretability.py:128`); openslide entra solo
   para miniatura y recortes. Un script reducido, sin rasterizado, barre los test de
   los 5 folds de las 3 tareas. CPU post-hoc, regla 9 no aplica.
2. **Entrenar los slots de MAMMOTH con nuestro dataset.** ⚠ **Discrepancia a aclarar
   con Sebastián:** `slot_embeds` es `nn.Parameter` con init aleatorio
   (`MAMMOTH/src/mammoth/mammoth.py:281-285`) y el job 4589 entrenó Mammoth **desde
   cero sobre nuestros splits** → los slots analizados **ya** están entrenados con
   nuestro dataset. Lectura más plausible del pedido: verlos sobre **láminas privadas**
   (las 7 del B7 son todas TCGA). Otra: una etapa de pre-entrenamiento del ruteo, que
   sería objetivo nuevo con prereg propio.
3. **Grid de E y S**, comparando contra **CLAM baseline** y **Mammoth baseline** con
   los mismos hiperparámetros; varias ramas, un fin de semana de GPU. Amplía el eje del
   23-jul ([[mammoth-grid-expertos-slots]]). **`train_dsmil.py` ya expone
   `--mammoth_num_experts` y `--mammoth_num_slots` (L223-224)** → es configuración, no
   código nuevo. **Presupuesto:** el 4589 hizo 30 runs en ~20 h (~40 min/run) → un fin
   de semana son **~70 runs**, y cada configuración sobre 3 tareas × 5 folds cuesta 15.
   O pocas configuraciones sobre las 3 tareas, o un grid ancho sobre una sola. Falta
   prereg (regla 9) + `reviewer`, y cuidado con 9.b si se plantea como reapertura del
   eje de rendimiento.
4. **Tres papers para discutir con Sebastián esta semana**: Hover-Net (núcleos),
   SI-MIL (interpretabilidad dentro del MIL) y el de invasión linfovascular para
   metástasis ganglionar. **2 de 3 descargados** el 27-jul con autorización de Ernesto
   (workaround E), en `sprints/B8_sprint8/` y no en `papers/`: `hovernet_graham2019.pdf`
   (arXiv:1812.06499v5) y `simil_kapse2024.pdf` (arXiv:2312.15010v2). El tercero (Chen
   et al., Human Pathology 131:26-37, 2023) es **de suscripción**, sin PMC ni preprint
   → lo consigue Ernesto por acceso institucional. Fichas y abstract:
   `sprints/B8_sprint8/papers_b8.md`.

---

## Sesión del 27-jul-2026 (tarde) — encargo 1 del B8 ejecutado

**Escalado de la Q1: cuántos slots usa Mammoth, ahora con n grande.** Es el encargo de
Benjamín (158.7 de 300 salía de 7 láminas y no generalizaba). CPU post-hoc sobre
checkpoints congelados del job 4589, sin GPU, regla 9 no aplica.

**Tooling nuevo**, los dos validados antes de usarse:

- `scripts/q1_slots_escalado.py` — barre las láminas de test de los 5 folds de las 3
  tareas midiendo `combine_weights` (slots) y `dispatch_weights` (expertos), sin openslide
  ni matplotlib. Reanudable por fold marcando con `meta.json` (workaround J).
- `scripts/q1_slots_analisis.py` — separa las dos explicaciones candidatas de la
  dispersión (tamaño de lámina contra tarea).

**Validación:** `--self-test` compara el camino con streaming contra la implementación del
B7 (tolerancia relativa, porque son las mismas sumas float32 en distinto orden), y
`--validate-b7` remide las 7 láminas del Sprint 7 y **reproduce exactamente** sus números
(158.7 y 30.0/30, peor delta relativo 4e-08). Recién entonces se barrió el resto.

**Barrido:** 1858 láminas-fold (1176 únicas, las 3 cohortes) en **18 min**.

| | n=7 (B7) | n=1858 (B8) |
|---|---|---|
| Slots efectivos (de 300) | 158.7 ± 34.6 | **159.5 ± 26.3** |
| Expertos efectivos (de 30) | 30.0 | **29.98** (`e50=15`, `e90=27` exactos en las 1858) |

- **El número aguanta el escalado** y ahora es el número de la tarea, no de 7 láminas.
- **E=30 no está sobredimensionado y el margen de recorte está en S**, confirmado con n
  grande y transversal a tareas y cohortes. Es el insumo directo del grid del encargo 3.
- **Se corrige lo que decía el B7 sobre la dispersión.** Con n=7 se concluyó que seguía al
  tamaño de la lámina y no a la tarea (ρ=0.750); con n grande se invierte el orden y las
  dos explican poco: tarea eta²=0.086, tamaño ρ²=0.020 (ρ cae a 0.141), cohorte 0.018. El
  ~88 % de la varianza es variabilidad entre láminas. La salvedad «describe, no establece»
  que el propio resultado llevaba es exactamente lo que se cumplió.
- **La cohorte casi no mueve la aguja**: privado 162.7, TCGA 162.2, HistAI 154.9. Medir
  solo TCGA en el B7 no sesgó el número, y roza (sin cerrar) la lectura 1 del encargo 2.

Detalle: `sprints/B8_sprint8/q1_slots_escalado/{resultados.md,metodologia.md}`. Verdad de
campo: `results/b8_q1_slots_escalado/`. Memorias: [[mammoth-slot-routing-weight]] y
[[mammoth-dispatch-softmax-sobre-parches]] (las dos softmax de Mammoth normalizan sobre
ejes distintos, que es lo que obliga al streaming en dos pasadas).

---

## Sesión del 28-jul-2026 — verificación del escalado y entregable de presentaciones

**La re-corrida del barrido cerró bien.** El proceso desatado (PID 2989473) terminó por
finalización normal: 1858 láminas en 17.4 min, con los mismos números (slots 159.5 ± 26.3,
expertos 29.98). La corrección que la motivaba quedó efectivamente en disco: la columna
`expertos_sobre_uniforme` ahora da 14.96 de media (rango 8 a 20, cero filas en 0) contra el
0 constante de antes, y cae justo sobre el `e50 = 15` del reparto uniforme, que es lo
esperado. Los CSV se escribieron 17:51:13 y el commit `b3cb700` es de 17:51:43, así que la
verdad de campo versionada es la corregida. **El pendiente 1 del handoff queda cerrado.**

**Inventario de las comparaciones de atención CLAM contra Mammoth** (consulta de la
sesión, sin trabajo nuevo): viven en `results/b7_mammoth_interp/interpretabilidad/<tarea>/
<lámina>/`, con `attention_side_by_side.png`, los dos mapas por separado y
`attention_stats.json`. Son 7 láminas, **todas del test del fold 0**, y en las 7 aciertan
los dos modelos. La copia curada para enviar ya existe en `sprints/B7_sprint7/
envio_heatmaps/`. Lo que dicen los stats (Spearman alto 0.67 a 0.92 pero Jaccard del top
5 % bajo, 0.01 a 0.31) **ya estaba documentado** en
`sprints/B7_sprint7/resultados_interpretabilidad.md` §3 y §3.1: no es hallazgo nuevo.

**Presentaciones del semestre sin notas del presentador (pedido de Sebastián).** Se
quitaron las notas de los 6 decks (B2 a B7, 102 guiones, ~158k caracteres) por cirugía de
zip, dejando todo lo demás byte-idéntico y verificado por CRC parte por parte. Cero
diferencias inesperadas en los 6.

> **Incidente, y es lo que hay que leer de esta entrada.** Después de terminar y verificar,
> `papers/presentaciones-semestre/` **y su carpeta de respaldo hermana desaparecieron las
> dos**. No queda ningún `.pptx` con mtime posterior al 24-jul en todo el árbol. Los decks
> B3, B4, B6 y B7 sobreviven en sus carpetas de sprint (el del B6 como
> `CLAM_Reunion_Mammoth.pptx`) y el del B5 existe en otra versión en
> `papers/presentations/`, pero **el del B2 no tiene copia en ningún lado del servidor y su
> guion se perdió**. La lección durable, en [[pptx-quitar-notas-y-respaldo]]: los `.pptx`
> no están versionados por diseño (`.gitignore`, «Precedente: 0 pptx trackeados»), así que
> no hay red de git, y **un respaldo hermano comparte el radio de acción de un borrado de
> carpeta**. El respaldo va a otro árbol.

> **ADDENDUM 30-jul-2026 — no hubo incidente: los borró Ernesto, a propósito.** Lo aclaró
> él al abrir la sesión del 30: **ya le mandó las presentaciones sin notas a Sebastián**,
> las eliminó del servidor después de enviarlas y **tiene todo respaldado en su máquina
> local**. Con eso, el entregable **está cumplido**, no hay que rehacerlo, y no hubo
> pérdida de datos. Queda **una sola pregunta abierta**: si el respaldo local incluye
> también los **originales con notas** (en particular el del B2, cuyo guion no tiene copia
> en el servidor) o solamente las copias sin notas que se enviaron. La parte del
> procedimiento sigue valiendo entera (la cirugía de zip funcionó y quedó verificada por
> CRC); lo que se cae es el diagnóstico de causa. El consejo de respaldar fuera del árbol
> sigue siendo bueno, pero como precaución, no como conclusión de este episodio.
> **Confirmado el mismo día: el respaldo local sí incluye los originales con notas**, así
> que el guion del B2 tampoco se perdió y el pendiente muere entero.

---

## Sesión del 30-jul-2026 — SI-MIL leído

**Corrección del cierre anterior**, arriba en el ADDENDUM del 28: no hubo incidente con las
presentaciones. Los pendientes 3 y 4 del handoff quedan cerrados.

**SI-MIL leído completo** (paper principal y suplementario §8 a §17). El estudio, con el
contraste contra lo nuestro y las preguntas para la reunión, en
[`sprints/B8_sprint8/simil_estudio.md`](../sprints/B8_sprint8/simil_estudio.md). Lo que
importa de la lectura:

- **Los dos papers del encargo 4 son la misma cadena, no dos ángulos.** HoVer-Net es el
  front-end de SI-MIL: segmenta y clasifica los núcleos en 5 clases, y de ahí salen las 246
  features «PathExpert» sobre las que predice la rama interpretable. Eso sube a Hover-Net
  de prioridad.
- **En la celda que nos corresponde, SI-MIL rinde un poco menos.** Su Tabla 2 adapta el
  método a otros MIL sobre TCGA-BRCA: con ABMIL la accuracy sube (0.937 → 0.944), pero con
  **CLAM baja** (0.937 → 0.925 acc, 0.972 → 0.957 AUC) y con TransMIL también. El titular
  de «sin compromiso entre rendimiento e interpretabilidad» está sostenido sobre ABMIL.
  **No reabre el Hallazgo 12**: es un trabajo de diseño de interpretabilidad, y traerlo
  como propuesta de mejora activaría la regla 9.b sin con qué citarla.
- **Su crítica al post-hoc nos apunta y conviene aceptarla:** dicen que explicar un modelo
  con features distintas de aquellas con las que fue entrenado deja una desconexión. El
  OBJ-A cae ahí, porque nombramos morfología mirando parches y el modelo nunca vio esa
  noción.
- **Dispersión impuesta contra dispersión medida.** Ellos fuerzan con un percentil que
  pocas features expliquen la predicción, porque un reporte de 246 renglones no lo lee
  nadie. Nuestro encargo 1 midió sin forzar nada que el modelo usa 29.98 de 30 expertos y
  159.5 de 300 slots. No se contradicen: la capacidad que un modelo usa y la que necesita
  para explicarse no tienen por qué ser el mismo número.
- **Ya medimos lo que ellos miden en su §16.** Comparan top-K entre SI-MIL y MIL
  convencional y les da 6 de 20 parches compartidos en IDC y 0 de 20 en ILC. Nuestro
  Jaccard del top-5 % entre CLAM y Mammoth fue 0.172 con Spearman 0.805. Las cifras no son
  comparables (ellos usan K=20 fijo, nosotros el 5 % de N), pero el fenómeno sí: dos MIL
  que aciertan igual coinciden en el mapa grueso y discrepan en los picos.
- **Bloqueo concreto para aplicarlo acá:** HoVer-Net está entrenado solo a 40× y ellos
  filtraron sus datasets a eso. Nuestras cohortes están a magnificación física distinta
  ([[cohortes-magnificacion-fisica]]), así que sin restringir a TCGA las features de
  núcleos saldrían bajo escalas distintas según el origen de la lámina. Y el
  preprocesamiento cuesta ~2 h por WSI, ~4400 h para 2.2K láminas con 3 GPU. **Lo primero
  a verificar es si el dataset que publican cubre nuestras láminas de TCGA-BRCA**, porque
  eso saltea el costo entero.

**Pedido nuevo de Sebastián** (correo del 29-jul, 12:15), marcado por él como opcional:
*Co-assistant networks by pathology foundation model and convolutional neural network for
gigapixel whole slide image analysis*. **Localizado con búsqueda autorizada por Ernesto:**
Liu et al., **Medical Image Analysis 2026**, DOI `10.1016/j.media.2026.104202`, PMID
42398343. **De suscripción y sin vía abierta** (Europe PMC `isOpenAccess: N`, `hasPDF: N`,
sin PMCID; arXiv devuelve 0 entradas; Semantic Scholar lo da `Closed`), así que **no se
descargó**: es el mismo caso que el paper de Human Pathology y se resuelve igual, con
acceso institucional. Lo que sí es público es el **código**, en `github.com/lZhuoRan/ILSC`,
no clonado.

El método se llama **ILSC** (*Interpretable Large-Small Co-assistant*) y por el abstract es
la misma familia de idea que SI-MIL: dos ramas, una potente y otra acotada y legible. Acá
la segunda es una CNN chica con atención a nivel de célula, y la crítica que abre el paper
apunta al **foundation model**, que es nuestro caso con CONCH: dicen que la self-attention
del PFM codifica relaciones triviales o ruidosas y le cuesta el patrón local. Detalle
importante para cualquier prueba futura: según su README el preprocesamiento es **CLAM**,
o sea lo que ya corremos, así que la barrera de entrada es mucho menor que la de SI-MIL
(HoVer-Net a 40× y ~2 h por lámina). Su PFM es PLIP, no CONCH. Ficha completa con abstract
en `papers_b8.md` §4.

Sin GPU y sin procesos CPU en esta sesión.

## Sesión del 30-jul-2026 (tarde) — SI-MIL explicado, insumo del deck listo

Sesión de explicación, sin código ni experimentos. Ernesto había leído el paper y pidió que
se le explicara la matemática, empezando por las **ecuaciones 1 y 2**, que eran las que no
le cerraban. Lo producido está en
[`sprints/B8_sprint8/simil_explicacion_matematica.md`](../sprints/B8_sprint8/simil_explicacion_matematica.md),
que es material pedagógico, **no** un segundo estudio del paper (ese sigue siendo
`simil_estudio.md`).

Cubierto y cerrado: el mapa de símbolos con la trampa `D` contra `d`, la **ecuación 1**
(bolsa, proyector, atención y sobre qué eje normaliza), la **ecuación 2** completa, y la
**Figura 2** panel por panel como recorrido de un tensor. Quedaron **sin explicar** las
ecuaciones 3 a 10 y las secciones posteriores a las fórmulas; el plan de cómo desarmarlas
está escrito en §6.2 y §7 de ese documento, con las fórmulas ya transcritas literales para
no re-extraerlas.

Lo durable que salió, verificado contra `models/model_clam.py` y no inferido:

- **Mapeo exacto de las ecuaciones 1 y 2 a `CLAM_MB`**: `H` es la línea 191 (la misma capa
  que Mammoth reemplaza), `A^p` son la 193 y la 213, `C` es la 198, y el orden
  agregar-y-después-clasificar son la 239 y la 243.
- **La distinción de orden es el nudo del paper.** El orden A (agregar y clasificar, que es
  CLAM) y el orden B aditivo (clasificar por parche y sumar, que es la ecuación 2) dan **el
  mismo número** cuando `C` es lineal. Lo que cambia es que el orden B deja las
  contribuciones por parche **con signo**, y el A las pierde en una fusión irreversible.
- **Acota lo que pueden afirmar nuestros heatmaps del B7.** `α` es post-softmax y por lo
  tanto siempre positiva: dice cuánto miró el modelo, nunca hacia qué clase empujó lo que
  miró. No invalida el B7, porque ahí la pregunta era dónde mira cada modelo. Pero al
  presentar corresponde decir «acá el modelo puso su atención», no «acá encontró el tumor».
  Memoria [[mil-orden-aditivo-vs-agregado]], más un ADDENDUM en
  [[heatmap-atencion-no-es-per-experto]].
- **En SI-MIL `β` es por feature y no suma 1**, porque termina en sigmoide (ecuación 5):
  son 246 compuertas independientes, no una torta. `α`, en cambio, es por parche y suma 1
  sobre `N`. Es justo la clase de confusión de eje que ya costó una memoria en Mammoth.
- **Dos notas de lectura del paper**: el `+ b` de la ecuación 9 es una simplificación de
  notación (sustituyendo la 7 en la 8 sale `K·b`, no `b`), y el **stop-gradient de la
  destilación está en el suplementario**, no en el paper principal. Si se cita, citar el
  suplementario.

**Lo que sigue es la presentación.** El B8 todavía no tiene directorio de deck; el tooling
vive en `sprints/B7_sprint7/presentacion_b7/generate_b7_deck.py` y las convenciones en
`sprints/B5_sprint5/presentacion_b5/convenciones_deck_b5.md`. La figura original del paper
va como **imagen** (única excepción a «todo nativo»); el resto de los diagramas van nativos.
Los candidatos a lámina visual están listados en §8 del documento nuevo.

Sin GPU y sin procesos CPU en esta sesión.

## Sesión del 30-jul-2026 (noche) — el deck de SI-MIL, construido

**Estado: HECHO.** `sprints/B8_sprint8/presentacion_b8/` con el generador, el `.pptx` de
**19 láminas** y la Fig. 2 del paper recortada. Documentación de las decisiones en el
`README.md` del directorio; no se repite acá.

**Alcance, decidido por Ernesto al abrir la sesión: solo el deck.** Las ecuaciones 3 a 10
quedan **en panorama** (una línea de glosa cada una, con la 9 destacada) y desarmarlas una
por una sigue pendiente. La lámina de objetivos lo declara con su marcador de estado en
lugar de disimularlo.

**Lo que el deck presenta:**

- Las **ecuaciones 1 y 2 desarmadas**. *(Recortado el 31-jul: la 2 entra ahora entera en
  UNA lámina, la analogía de la licuadora contra la libreta pasó al guion y el mini ejemplo
  numérico se retiró; queda el diagrama de los dos órdenes más la tabla de qué queda en
  memoria tras el forward, que era el malentendido de fondo.)*
- La **Fig. 2 completa** (pág. 4, extraída a 400 DPI) más los paneles (b) y (c) por
  separado, en las láminas de la ecuación 1 y de la rama interpretable. Es la **única
  imagen** del deck; todo lo demás es nativo.
- El **embudo del PAG Top-K** con la cuenta hecha sobre una lámina nuestra de 10 000
  parches: 5 120 000 números que se descartan, contra 4920 que tienen nombre.
- El **límite de nuestros mapas de atención**. Al presentar: «acá el modelo puso su
  atención», no «acá el modelo encontró el tumor». *(Recortado el 31-jul: se fusionó con el
  mapeo a `model_clam.py` y salió la segunda tabla numérica, α contra contribución.)*
- La **Tabla 2 con la fila de CLAM destacada** (0.937 → 0.925 en accuracy, 0.972 → 0.957 en
  AUC): el método NO se presenta como mejora de rendimiento.
- Que **HoVer-Net y SI-MIL son la misma cadena**, en la lámina de las dos entradas.

**Dos cosas reusables que salieron de acá** (detalle en el README y en las memorias):

- **Un deck de ecuaciones obliga a decidir qué pasa con las griegas.** Barlow no las trae, y
  el template también embebe Cambria Math. Se rasterizaron las variantes y **gana Barlow con
  el fallback**: las griegas de Cambria Math son serif finas y contrastan con el Barlow que
  las rodea. ADDENDUM en [[deck-template-fuentes-embebidas]].
- **El punto ciego «texto que desborda su caja» sí se puede automatizar: hay que medir el
  texto.** Con Barlow instalada se mide con sus propios TTF, y los paneles calculan su
  propio alto. En la primera pasada había **seis láminas** con la última línea afuera y una
  tabla montada sobre un panel. ADDENDUM en [[deck-qa-puntos-ciegos-chequeo]]. La auditoría
  no reemplaza mirar: los defectos de diseño (una flecha que sugería el flujo equivocado, un
  rótulo compitiendo con la barra de remate) solo salieron mirando las láminas.

**Guion del presentador** pasado por `@humanizer-es`. El vocabulario salió limpio y los
tells eran **de ritmo**: diez láminas abrían su último párrafo con «Y » (quedaron cero) y
catorce párrafos abrían señalando una posición del layout (quedaron seis, que es lo que la
convención pide para seguir la figura).

~~**Ojo al retomar:** la fecha de la lámina de título…~~ **Resuelto el 31-jul**: Ernesto
confirmó que la reunión es el **viernes 07/08/2026**; `FECHA_REUNION` ya la tiene.

Sin GPU y sin procesos CPU en esta sesión.

---

## Sesión del 31-jul-2026 — el deck de SI-MIL recortado a 14 láminas

**Pedido de Ernesto:** menos láminas, y sobre todo **fuera el ejemplo numérico del orden de
las operaciones**, que tenía que quedar claro en una sola lámina. Quedó en **14** (de 19).
Commit `665ad5e` + el de la fecha. Auditoría sin avisos y QA visual sobre el rasterizado con
Barlow real.

**Supersede una decisión que el handoff daba por cerrada:** la secuencia «analogía → ejemplo
numérico → tabla de qué queda» del 30-jul. La ecuación 2 entra ahora entera en una lámina
con el diagrama de los dos órdenes arriba y la tabla de qué queda en memoria abajo,
recortada a las tres filas que de verdad separan a los órdenes.

**Las cinco fusiones** (tabla completa en `sprints/B8_sprint8/presentacion_b8/README.md`
§«El recorte del 31-jul»):

| Antes | Ahora |
|---|---|
| divisoria de sección + «qué propone» | una: la ficha del paper entra como línea de referencia |
| ecuación 2 + el ejemplo numérico | **una** |
| «por qué la atención no rescata» + «dónde queda nuestro modelo» | una: mapeo a `model_clam.py` arriba, dos paneles abajo |
| «qué reportan» + «el contraste» | una: dos tablas, sin los cuatro paneles |
| «qué costaría» + «preguntas» | una: bloqueos en tira, preguntas en rejilla 2 × 2 |

**Nada de contenido se perdió: se movió al guion hablado.** La crítica del paper a la
interpretación post-hoc, los dos puntos donde coincidimos con ellos y las dos diferencias
entre su formulación y la nuestra se cuentan hablando. Los guiones de las fusionadas se
**reescribieron**, no se pegaron: el deck bajó de **3705 a 3199 palabras**, y se verificó
que no reaparecieran los tells de ritmo que la primera pasada había corregido.

**Fecha de la reunión confirmada: viernes 07/08/2026.**

**Hallazgo operativo del cierre:** el preflight encontró en el árbol un archivo nuevo
(`hovernet_estudio.md`) y un `papers_b8.md` modificado que **esta sesión no tocó**, y `ps`
mostró **dos** procesos `claude` vivos bajo `sdonoso`. Es una **sesión paralela** trabajando
el otro paper del sprint. Su trabajo **NO se commiteó** acá. ADDENDUM en
[[git-main-shared-pushes]].

Sin GPU y sin procesos CPU en esta sesión.

---

## Sesión del 31-jul-2026 (tarde) — HoVer-Net estudiado, y ya estaba corriendo

**Pedido de Ernesto:** estudiar HoVer-Net mientras él corregía las láminas del deck de
SI-MIL en una sesión paralela. Todo lo de esta sesión es lectura y documentación: **sin GPU,
sin procesos CPU, sin tocar nada ajeno**.

Paper leído completo (principal más el apéndice A de ablaciones) y volcado en
[`sprints/B8_sprint8/hovernet_estudio.md`](../sprints/B8_sprint8/hovernet_estudio.md): el
mecanismo de los mapas horizontal y vertical con un ejemplo en una dimensión, las tres ramas
sobre el encoder compartido, la loss de seis términos, el watershed por marcadores y las
métricas PQ y Fc que el paper propone de paso.

**El mecanismo, en una línea:** en vez de dibujar el contorno, se predice dentro de cada
núcleo la distancia con signo a su propio centro de masa, normalizada a [−1, +1]. Dos núcleos
pegados producen un salto de +1 a −1 en la costura, y la derivada ahí vale el triple que
adentro del núcleo. La señal ocupa el núcleo entero, no una línea de un píxel.

**Dos cosas que salieron de verificar en vez de leer:**

1. **La Tabla A1 del paper tiene las columnas mal rotuladas, y el texto se equivoca al
   citarla.** Dice que la ganancia de su loss está en SQ. Con la identidad `PQ = DQ × SQ` la
   fila no cierra con los encabezados impresos (0.773 × 0.597 ≠ 0.618) y sí cierra
   reordenando (0.770 × 0.773 ≈ 0.597), en las cuatro filas y los dos datasets. La ganancia
   real está en **DQ**, la detección, que además es lo coherente con el mecanismo: el
   gradiente sirve para cortar, y cortar bien es encontrar más instancias.
2. **La clase *miscelánea* agrupa necrótico y mitótico** y es la peor del paper (F 0.426 en
   CoNSeP, 0.178 en CRCHisto, contra ~0.6 de las demás). Si alguien propone contar mitosis
   con esto, ese número es la respuesta.

**El hallazgo que corre el encuadre del encargo 4:** HoVer-Net **ya está instalado y
corriendo en el servidor**, no es una hipótesis. Lo montó `sgaete` el 29-jul en
`/media/administrador/Storage1/sdonoso/hover_net/` (ajeno, leído y nada más) con los pesos de
**PanNuke**, el mismo checkpoint que usa SI-MIL. El job 4714 completó una lámina de TCGA el
30-jul en **3 h 36 min**, y hay **881 en cola**. Detalle verificado en el §10 del estudio y
en la memoria [[hovernet-ya-corriendo-sgaete]].

Y en ese mismo directorio hay **`129741.bif - GDT.geojson`**: 61 regiones dibujadas a mano en
QuPath, en español y con vocabulario clínico. La lámina **está en nuestras features y en los
splits de las 3 tareas del B7**, incluidos los `_ci_reform` del job 4589. **No cierra el
sign-off de patólogo que arrastramos desde OBJ-A** (región no es parche, es una sola lámina,
y no sabemos quién la firmó), pero es el primer material concreto con el que se podría
contrastar. Está razonado en la segunda pasada de
[`auditoria_coherencia/hallazgos.md`](../sprints/B8_sprint8/auditoria_coherencia/hallazgos.md)
§B3.

**La asimetría que vuelve todo esto viable:** SI-MIL corre HoVer-Net sobre todos los parches
porque necesita entrenar su rama; nosotros solo queremos leer los que el modelo ya destacó.
Veinte parches de 256 px son 1.3 Mpx contra los 7530 de la lámina completa. Segundos de GPU
por lámina en vez de horas, y el `run_infer_tile.slurm` con `--save_raw_map` que hace
exactamente eso ya está escrito en el repo de sgaete.

Sigue en pie el bloqueo de magnificación: la corrida usa `--proc_mag=40` y la cohorte privada
está a ≈20× ([[cohortes-magnificacion-fisica]]).

**Nota de convivencia:** la sesión paralela tenía cambios sin commitear en
`presentacion_b8/`. Todos los commits de esta sesión se hicieron con **path explícito**, y el
índice de memorias se compactó de 19.8 a 13.2 KB verificando que las 76 entradas y sus
enlaces siguieran resolviendo.

---

## Sesión del 31-jul-2026 (noche) — reunión con Sebastián: se descarta SI-MIL y el sprint gira

**Ernesto volvió de la reunión con Sebastián con una redirección.** Registro completo en
[`sprints/B8_sprint8/reunion_31jul_redireccion.md`](../sprints/B8_sprint8/reunion_31jul_redireccion.md).
⚠ La fecha exacta de la reunión quedó **sin confirmar**: el repo tenía anotada una para el
viernes 07/08 con el deck de SI-MIL construido para ella.

**Lo decidido.** SI-MIL **no se implementa**: gana interpretabilidad a costa de empeorar
levemente la métrica, y lo que se busca es métrica. Coincide con lo que su Tabla 2 ya
mostraba en nuestra celda (0.937 → 0.925 acc, 0.972 → 0.957 AUC con CLAM de base), así que
el estudio no queda desmentido, queda usado. **HoVer-Net en pausa por costo**: Sebastián lo
corrió él mismo y midió 3.3 h por lámina, el mismo número que habíamos leído de sus logs
(3 h 36 min, job 4714), o sea que llega por dos vías independientes. **Se conserva** su idea
de correrlo solo sobre los **20 mejores parches de CLAM**, para cuando haya más GPU.

**Lo encargado.** Seguir con las configuraciones de hiperparámetros de Mammoth con CLAM (es
el encargo 3, que pasa a prioridad y sigue **sin pre-registro**), e investigar **ramas aparte
de CLAM dedicadas a una tarea**: mitosis y grado nuclear, que dependen de una geometría
particular. Argumento en
[`sprints/B8_sprint8/tareas_geometricas/README.md`](../sprints/B8_sprint8/tareas_geometricas/README.md).
**Cero código escrito**, por regla 9.

**El material del patólogo, y la trampa que traía.** El patólogo le mostró la lámina en
**QuPath** y compartió sus etiquetas. Ese archivo **es** el geojson que la sesión de la tarde
había encontrado en el directorio de `sgaete` con autoría desconocida: el pendiente queda
resuelto en lo esencial. Y al medirlo apareció algo que había que cazar antes de que alguien
construyera encima: **el geojson no está en coordenadas de openslide**. Superpuesto tal cual,
**0 de las 26 marcas de mitosis** caen sobre un parche extraído, y contra la máscara de
tejido de la propia WSI acierta 1 de 61. Con el desplazamiento correcto caen **58 de 61**, y
las 3 que fallan son las de fondo y grasa. El desplazamiento es **`dx = level0.width −
region[0].width` = 39669 − 35840 = 3829, `dy = 0`**, o sea derivable de las propiedades del
`.bif`: el óptimo empírico por área cae a **3 px en x y 13 px en y** de esa predicción.
Script reproducible en
[`scripts/alinear_anotaciones_qupath.py`](../scripts/alinear_anotaciones_qupath.py), hallazgo
en [`sprints/B8_sprint8/anotaciones_patologo/hallazgos.md`](../sprints/B8_sprint8/anotaciones_patologo/hallazgos.md).
Resultado: **163 parches de 4799** quedan bajo alguna anotación, de ellos **28 de mitosis** y
**13 de núcleos de alto grado**.

**La restricción que hay que respetar al usarlas:** textual del patólogo, el cáncer cubre toda
la zona pero él solo marca donde se evidencia con mayor exactitud. Son **positivos parciales,
no una segmentación**: un parche sin marca **no** es un negativo. Sirven para evaluar y como
semilla, no como verdad de campo exhaustiva.

**Medidas nuevas que sostienen el objetivo 5**, todas verificadas en esta sesión: la marca de
mitosis del patólogo es de 36 × 36 px = 16.7 µm, el **1.54 %** del área de un parche de 256 px
que se comprime a un vector de 512; los 2 mm² del recuento clínico de Nottingham son **~141
parches contiguos**, el **2.9 %** de la lámina, contra el promedio ponderado sobre las 4799
que hace CLAM; la lámina mide **0.465 µm/px con `objective-power = 20`**, que confirma en el
caso concreto lo que [[cohortes-magnificacion-fisica]] decía de la cohorte y deja abierto que
le estemos pidiendo a 20× lo que el patólogo hace a 40×; y en `grado_mitotic_3clases` la
calibración Tier 0 ya capturó casi todo su margen (bal_acc **0.531** de un techo de **0.571**,
AUC 0.721), así que lo que quede tiene que venir de la representación.

**Siguiente barato, sin GPU:** medir si nuestros modelos ya entrenados miran donde mira el
patólogo, con el percentil de atención de los 28 parches de mitosis entre los 4799. **Con un
gotcha que apareció al preparar la corrida:** 129741 cae en `val` en los splits de Sebastián
(`grado_histologico_mitotic_rate{,_combined}_100`, 4 clases) pero en **`train` en los 5 folds**
del k-fold nuestro (`grado_mitotic_3clases_pth_100`, 3 clases), que es **justamente el de los
checkpoints con el baseline que citamos**. Hay que elegir familia antes de correr, no después
de ver el número. Las dos opciones, en `tareas_geometricas/README.md` §4.

**Decisiones de Ernesto al cierre:** el deck del B8 **se rehace con la línea nueva** (mitosis
y grado nuclear, el argumento geométrico, las anotaciones del patólogo y el plan de ramas por
tarea) en vez de presentarse como estaba; y el orden de trabajo es **primero la medición en
CPU, después el pre-registro del grid de E y S**.

Sin GPU y sin procesos CPU largos en esta sesión.

---

## Sesión del 1-ago-2026 — la medición de atención vs las marcas del patólogo

Se ejecutó el primer experimento del objetivo 5, el que el cierre anterior dejó como
«siguiente barato, sin GPU». **Todo CPU, post-hoc, sin GPU y sin `sbatch`.** Pre-registro
escrito y commiteado **antes** de correr (`d52676f`), porque la elección de checkpoint era
el grado de libertad que podía fabricar el resultado:
`sprints/B8_sprint8/atencion_vs_patologo/prereg.md`. Resultado completo, con lo que no se
afirma: `sprints/B8_sprint8/atencion_vs_patologo/resultados.md`.

**El gotcha del checkpoint se resolvió sin tener que elegir entre las dos familias.** La
corrida 5-fold de Sebastián (`environ/results_modelo_combined_5fold/`) tiene 129741 en `val`
en los folds 0 y 2 y en `train` en 1, 3 y 4, o sea que el contraste visto/no-visto quedó
**dentro de una misma corrida**, con el mismo modelo y los mismos hiperparámetros. Se
corrieron los 12 checkpoints con roles asimétricos fijados de antemano: 4 primarios (lámina
nunca vista), 3 de control interno (misma corrida, vista) y los 5 de Tier 0 como
corroboración, rotulados como lámina de train.

**Ganó la hipótesis alternativa: el modelo sí mira donde marcó el patólogo.** Los 28 parches
de mitosis dan un AUC de ranking de **0.890 ± 0.039** en los checkpoints que nunca vieron la
lámina, con percentil mediano **91** sobre 100. Mitosis es el grupo mejor rankeado de los
siete, **por encima de Tumor** (0.826), y la atención cae ordenadamente hasta linfocitos
(0.322) y grasa (0.154). Sobrevive al nulo espacial por traslación rígida (p = 0.0021–0.0023:
ninguna de las ~440 traslaciones válidas alcanzó el valor observado) y no es memorización
(los checkpoints que la vieron en train dan 0.946, apenas +0.056).

**El hallazgo que reordena el sprint: mira bien y responde mal.** 3 de los 4 checkpoints
primarios **clasifican mal** la lámina — predicen `score_2` siendo `score_3` — mientras su
atención está puesta sobre las mitosis. El caso extremo es `seba_5fold_f0`, que tiene el mejor
AUC de atención del grupo (0.926) y la predicción más equivocada (0.712 a `score_2`). El
cuello no está en **elegir** los parches.

**Consecuencia para las cuatro familias de `tareas_geometricas/README.md` §3.** La familia A
pierde su motivación principal: la frase del patólogo sobre que esos parches no reciben
atención suficiente queda refutada en esta lámina. **Conserva** el otro argumento, el del
máximo local de Nottingham contra el promedio ponderado, que este experimento no evalúa; si A
se pre-registra, tiene que apoyarse en ese y no en la frase. Las familias B y C se
fortalecen, que es hacia donde apunta la disociación. Para **grado nuclear** el efecto es más
débil y no hay que estirarlo: 0.828, pero contra el nulo por traslación solo 1 de 4
checkpoints baja de p = 0.05, y con 13 parches no se distingue de cualquier mancha compacta.

**Dos cosas metodológicas que quedan para reusar.** El nulo por permutación de etiquetas es
**inválido** cuando los parches marcados son contiguos: dio p = 0.0005, el piso, en
absolutamente todo, incluido lo que contra el nulo bueno no es significativo
([[nulo-espacial-traslacion-rigida]]). Y la lámina 129741 tiene **dos regiones de escaneo**
con parches extraídos de las dos (2303 arriba, 2496 abajo), así que el tejido aparece dos
veces en cualquier heatmap; las 163 marcas están todas abajo. Se verificó que no es un
artefacto de región: la región anotada recibe *menos* atención que la otra (AUC 0.462–0.478)
y al confinar la medición ahí el efecto **sube** a 0.903.

**Subproducto:** las cabezas por clase de CLAM_MB no son específicas por clase en esta lámina
(Spearman entre pares de cabezas 0.72–0.94; la cabeza `no_identificado` rankea las mitosis
casi igual que la de `score_3`). El modelo tiene una sola noción de «tejido interesante».

**Proceso CPU desatado al cierre** (workaround J): la corrida definitiva con los dos universos
y 2000 traslaciones cada uno, hacia
`sprints/B8_sprint8/atencion_vs_patologo/con_region/`, log en
`logs/atencion_region_desatado.log`. Los AUC ya están confirmados por una corrida previa; lo
que agrega son los p-valores del universo confinado. **Sin GPU y sin jobs SLURM propios.**

**Quedaron sin empezar** los otros dos puntos del handoff anterior: el pre-registro del grid
de E y S, y rehacer el deck del B8.

---

## Sesión del 2-ago-2026 — cerrado el universo confinado, y el grid queda decidido

Sesión corta de cierre. Se retomó el handoff del 1-ago y se cerró su pendiente inmediato;
lo demás fue dejar el grid de E y S listo para que una sesión limpia lo escriba y lo lance.

**El pendiente del §4 quedó cerrado.** El proceso desatado (PID 1741266) había terminado
bien antes de que muriera la sesión anterior: escribió los tres archivos de
`atencion_vs_patologo/con_region/`. Se hizo el cotejo que pedía el handoff y **pasa**: los
AUC del universo `lamina` son idénticos dígito a dígito a los ya commiteados (delta
0.000e+00 en las 301 filas, y lo mismo en los percentiles); entre las dos corridas solo
difieren los p, por remuestreo.

**Lo que agrega el universo confinado.** Dentro de la región anotada (N = 2496) caben
**~1300 traslaciones válidas** en vez de las ~440 de la lámina entera, así que el nulo
espacial se vuelve más exigente. Mitosis vuelve a dar el piso 1/(1+N), **p =
0.00075–0.00078** en las 7 combinaciones checkpoint × cabeza de los 4 primarios. Grado
nuclear queda **igual de mixto** que en la lámina completa (p = 0.012–0.093, bajo 0.05 en 4
de 7): confinar no lo rescata, que es coherente con no estirar ese resultado. La conclusión
no se movió. Documentado en el §2.b de `atencion_vs_patologo/resultados.md`.

**Decisión de Ernesto sobre el grid: va ANCHO sobre UNA sola tarea.** Cierra la disyuntiva
que el §3 de `objetivos_sprint8.md` había dejado abierta (o pocas configuraciones sobre las
3 tareas, o un grid ancho sobre una). Motivo operativo: es domingo y la GPU está vacía, hay
que aprovechar la ventana.

**El presupuesto del §3 estaba inflado por un promedio engañoso.** Medido el tiempo real por
run del 4589 desde los mtime de los `test_metrics.json`, las tres tareas no cuestan lo
mismo: `tipo_histologico_3clases_ci` **83 min/run** (1621 slides de train, 3 clases), contra
**36.2 min/run** de `carcinoma_ductal_insitu_presente_ci_reform` y 37.0 de LVI reform. El
«~40 min por run» del §3 era el promedio de las tres y sobreestima la tarea candidata en más
de un 10 %.

**Y los baselines de esa tarea ya existen, verificado.** Los 10 runs del 4589 (5 CLAM + 5
Mammoth 30×10) están en `results/b7_mammoth_interp/carcinoma_ductal_insitu_presente_ci_reform/`
sobre los **mismos splits**, y **ninguna feature cambió desde entonces** (cero `.pt` con
mtime posterior al 17-jul; el dir quedó en 28-jun, que es el parche de magnificación). O sea
que el reuso pareado es válido por construcción y **libera 10 runs** para configuraciones
nuevas.

**Sin GPU, sin jobs SLURM propios y sin procesos CPU al cierre.** La cola estaba vacía.

**Quedaron sin empezar** el pre-registro del grid (que la próxima sesión escribe y lanza) y
rehacer el deck del B8.

---

## Sesión del 2-ago-2026 (noche) — el grid de E y S, pre-registrado y LANZADO (job 4774)

Se cumplió la misión del handoff en el orden que pedía: pre-registro → `reviewer` → commit →
`sbatch`. **Job 4774** corriendo desde las 20:47 del domingo, 8 brazos × 5 folds = 40 runs
sobre `carcinoma_ductal_insitu_presente_ci_reform`, ~24.3 h estimadas.

**El encuadre quedó escrito, que era el punto delicado.** El pre-registro
(`sprints/B8_sprint8/grid_expertos_slots/prereg.md`) elige **capacidad**, no rendimiento, y lo
sostiene con el diseño y no con una etiqueta: el contraste primario es **Mammoth contra
Mammoth** (cada brazo contra el control 30×10), CLAM entra solo como fila de referencia y
**sin Δ por brazo**, porque calcular 8 Δ contra CLAM justo en la tarea del dato abierto serían
8 disparos al eje cerrado del Hallazgo 12. El `reviewer` verificó los cuatro puntos del diseño
y dictaminó que **no aplica regla 9.b**, así que no hizo falta citar hallazgo habilitante.

**El grid.** Escalera de capacidad total con los dos recortes apareados en cada peldaño:
control 30×10, después 27×10 contra 30×9 (E·S=270, que es el par textual que pidió Sebastián
el 23-jul), 21×10 contra 30×7 (210), 15×10 contra 30×5 (150) y el piso 30×3 (90), este último
solo en la rama S. Orden de ejecución elegido para que un corte por cortesía o por tiempo se
lleve el peldaño más agresivo y no el control. La hipótesis pre-registrada sale del encargo 1
de este mismo sprint (expertos 29.98/30 uniforme, slots 159.5/300 sobre 1858 láminas-fold):
**a igual E·S, recortar S debería tolerarse mejor que recortar E**.

**Hallazgo mecanístico que salió al preparar el grid: los pares a igual E·S son casi
iso-parámetro, y no era obvio.** `auto_rank` deriva el `lora_rank` de
`(input_dim, slot_dim, output_dim, num_experts)`, o sea que **depende de E y no de S**
(`MAMMOTH/src/mammoth/mammoth.py:297-322`): recortar E sube el rank (8→9→12→17) y compensa el
presupuesto, mientras que recortar S solo achica `slot_embeds`. Medido, la diferencia dentro
de cada par es de **+0.20 %, +0.33 % y +0.89 %**. El contraste A contra B aísla entonces
**dónde** está la capacidad, no cuántos parámetros hay.

**Preflight nuevo, reusable:** `scripts/grid_es_config_check.py` construye las 8
configuraciones en CPU, les corre un forward y verifica que `A_raw` conserve la forma
`(n_classes, N)`. Tarda segundos y evita descubrir una config rota a mitad de 24 h de GPU. Es
el segundo de los tres preflights del `.slurm` (test CPU del modelo → configs →
`preflight_minpatch` por fold); los tres pasaron en el 4774.

**Dos correcciones que trajo el `reviewer`.** La tabla de min/run del ADDENDUM 2-ago rotulaba
«mediana» a lo que eran los **mínimos**: las medianas del brazo Mammoth son 83.6 / 37.4 /
**36.4**, no 83.0 / 37.0 / 36.2 (commit `322dd40`). Y faltaba decir **cuál métrica manda si
balanced_acc y AUC se contradicen**: con 13 negativos por test la balanced accuracy se mueve a
saltos de 0.038, así que la consistencia de signo de un par puede depender de una sola lámina.
Queda pre-registrado que la decisiva es el **AUC**, con balanced_acc al lado como lectura del
punto de operación, y que un desacuerdo se declara **ambiguo** (sería calibración, no
capacidad). Las dos métricas se siguen reportando juntas, así que la política B5 se cumple.

**Ventana de GPU:** la cola estaba vacía y el nodo `idle` al momento del `sbatch`, pero 24 h
lanzadas un domingo a la noche **ocupan el lunes laboral entero**. Si aparecen jobs ajenos,
aplica la cortesía de `CLAUDE.md` y se evalúa `scancel` de los brazos que falten (el orden de
ejecución está pensado para eso).

**Con el job vivo: no cambiar de rama ni editar archivos versionados que el job lea**
(workaround H). El `.slurm` ahora loguea `commit=` y `rama=` para dejar la provenance.

**Dos cosas que Ernesto avisó al cerrar la sesión.** Hay **reunión con Sebastián el lunes
3-ago**. El repo tenía anotada una para el **viernes 07/08** (`reunion_31jul_redireccion.md:5`,
este archivo en las líneas 1088 y 1123) y el deck de SI-MIL se construyó para esa fecha; **no
se sabe** si la del 3-ago la reemplaza, la adelanta o es adicional, y eso lo resuelve Ernesto,
no el repo. Y queda un **encargo nuevo**: buscar **3 papers** para subir métrica en tareas
específicas como mitosis, con una **rama aparte de CLAM** especializada en ellas y usando la
información del patólogo sobre las etiquetas, **para presentar en esa reunión**. Es la
búsqueda bibliográfica que le faltaba al objetivo 5; restricciones ya decididas (apuntar a las
familias B/C/D y no a la A, supervisión de positivos parciales, no descargar papers) en el
ADDENDUM 2-ago del §4 de `objetivos_sprint8.md`.

**Sigue sin empezar** rehacer el deck del B8.

---

## Sesión del 2-ago-2026 (noche, 2ª) — los 3 papers de la rama de mitosis, para la reunión del lunes

Entregable: [`sprints/B8_sprint8/tareas_geometricas/papers_mitosis.md`](../sprints/B8_sprint8/tareas_geometricas/papers_mitosis.md).
Tabla con los tres lado a lado (**supervisión y costo** como ejes), una recomendación, y las
fichas detrás. El job 4774 siguió corriendo toda la sesión, sin tocarlo.

**Los tres, uno por familia.** **D**, Zhao et al., *Positive-unlabeled learning… with incomplete
annotations* (MELBA 2022, abierto): reformula el entrenamiento del detector como PU learning, o
sea que lo no anotado tiene etiqueta **desconocida** y no negativa. **C**, CellViT (MedIA 2024):
núcleos con ViT, 1.85× sobre HoVer-Net, pesos públicos. **B**, ZoomMIL (ECCV 2022): aprende a
qué zonas hacer zoom, solo con etiqueta de lámina y hasta 40× menos cómputo.

**La recomendación es D, y en dos pasos.** Es el único cuyo régimen de supervisión coincide con
el nuestro: hoy las 26 marcas del patólogo solo sirven de validación, y este método las vuelve
**entrenables** sin mentir sobre los negativos. Además ataca el argumento que **sobrevivió** al
1-ago (el §2.b: el recuento de Nottingham es un conteo en el punto caliente, no un promedio
ponderado). Paso 1 = **go/no-go barato**: detector público sobre unas pocas láminas, medido
contra las 26 marcas, **primero en TCGA** porque está a ~40× nativo y el privado a 20×. Paso 2,
solo si el 1 pasa: fine-tuning PU sobre nuestra cohorte. Es el patrón «Etapa 0 antes de Etapa 1»
que ya ahorró 18 a 24 h en PathPT.

**Dos cosas que salieron de la búsqueda y que valen aparte del ranking.**

- **Se cierra con números una frase que el README §3.C había dejado abierta.** «Mucho más
  barato» que HoVer-Net = CellViT, 1.85×, pero **sigue usando watershed controlado por
  marcadores** (verificado en el texto), así que **no** elimina los 75 min de CPU. El que sí los
  elimina es **LSP-DETR** (arXiv:2601.03163, ene-2026), polígonos estrella-convexos sin
  post-procesamiento, >5× sobre el siguiente más rápido, todavía preprint. Y la cuenta que
  reordena la familia C: cambiar de modelo rinde 1.85×, acotar a los **20 mejores parches de
  CLAM** (idea del propio Sebastián) rinde **~240×**. El paper es de segundo orden frente al
  subconjunto de parches.
- **CellViT no tiene clase mitótica** (las 5 de PanNuke), igual que HoVer-Net. Para grado
  nuclear sirve; **para contar mitosis no**.

**Lo que frena a cada uno, dicho en la ficha.** D: con 1 lámina y 26 mitosis no se entrena nada,
hay que arrancar de datos públicos (MIDOG 2021 son 200 casos de mama humana, 4 escáneres, CC-BY)
y el escáner nuestro (Ventana) no está entre los suyos, que es justamente el resultado central
del challenge. B: el privado está a **20×** y la mitosis se cuenta a **40×**, así que un método
que aprende a hacer zoom no tiene a dónde hacerlo; su aporte real es el confundido de µm/px
entre cohortes (§2.c).

**Un cuarto, fuera de las tres familias, incluido a propósito:** **MS-CLAM** (MedIA 2023,
abierto por HAL), que es CLAM con **supervisión mixta** y responde de la forma más literal a
«aprovechar la información del patólogo sobre las etiquetas». Queda quinto en prioridad con un
motivo concreto y no por desinterés: su 12 a 62 % es una fracción de un conjunto **completo** de
anotaciones de parche, y nosotros tenemos **una** lámina, con positivos parciales. Sirve como
respuesta preparada si en la reunión sale «¿y por qué no le agregamos supervisión de parche a
CLAM y listo?».

**Acceso: los cinco se leen sin paywall**, tres por versión de autor (arXiv, HAL) y uno por
revista abierta. **Ninguno se descargó** (workaround E). Un `WebFetch` al PDF de ZoomMIL dejó una
copia de 5.5 MB en el cache del harness (`~/.claude/.../tool-results/`); se borró en el momento.
Para leer detalles finos de un paper conviene quedarse en páginas de abstract y APIs (Europe
PMC, HAL), que es lo que se usó para todo lo demás.

**Estado del job 4774 al cierre de esta sesión:** vivo, brazo control 30×10, fold 0, sin
`Traceback` ni `FAILED`, ningún `test_metrics.json` escrito todavía. El
`EarlyStopping counter: N out of 20` con N>20 en el log **es normal**: `stop_epoch=50` está
hardcodeado, así que el contador corre pero no dispara antes de la época 50.

**Sigue sin empezar** rehacer el deck del B8.

**Al cerrar la sesión, Ernesto autorizó descargar los papers con su código.** Levanta el
workaround E **para los cinco de `papers_mitosis.md` y sus repos**, y solo para ellos (los dos
de suscripción del encargo anterior, LVI e ILSC, **no** quedan cubiertos). Destinos: los PDF a
`sprints/B8_sprint8/tareas_geometricas/` y se commitean, que es la convención verificada del
encargo anterior; los repos a `clam_testing2/<Nombre>_reference/` con las mismas reglas que
`CLAM_official_reference/` (solo lectura, NO al PYTHONPATH, NO import cruzado). Código
localizado: CellViT `TIO-IKIM/CellViT`, ZoomMIL `histocartography/zoommil`, MS-CLAM
`paul-tourniaire/MS-CLAM`. **Del paper de PU learning no se encontró repo**, y eso cambia el
costo de la familia D: si no hay implementación, el detector y la loss se escriben desde cero.
La próxima sesión estudia cada uno y **confirma o corrige** la recomendación, con el job 4774
todavía corriendo.

---

## Sesión del 2-ago-2026 (noche, 3ª) — los papers bajados y leídos, con dos correcciones a la ficha

Se ejecutó el handoff del 2-ago 20:57: bajar los papers **con su código**, estudiarlos, y dejar
la reunión del lunes preparada. El job 4774 corrió toda la sesión sin que se lo tocara.

**Bajado, bajo la autorización explícita de Ernesto y solo para esta lista.** Ocho PDF en
`sprints/B8_sprint8/tareas_geometricas/` y cuatro repos en `clam_testing2/<Nombre>_reference/`
(reference only, sin checkpoints). Inventario con tamaños y HEAD en
[`papers_mitosis.md`](../sprints/B8_sprint8/tareas_geometricas/papers_mitosis.md) §7. El servidor
sí tiene salida a internet, cosa que no estaba verificada: los `WebFetch` anteriores salían por
el harness.

**Cuatro estudios nuevos**, del formato de `hovernet_estudio.md`: `pulearning_estudio.md`,
`cellvit_estudio.md`, `zoommil_estudio.md`, `msclam_estudio.md`, más `midog_notas.md` para el
dataset.

**Los cinco huecos del handoff quedaron cerrados, y dos eran errores, no huecos.**

1. **El paper de PU learning SÍ tiene código.** Está citado en la pág. 3 del cuerpo, no en la
   página de abstract, que es por donde se buscó el 2-ago:
   `github.com/zipeizhao/PU-learning-for-cell-detection`. Pero encontrarlo cambia menos de lo que
   parece: pide **PyTorch 0.4.0 y CUDA 8.0** (*"now it does not support 0.4.1 or higher"*) y no
   corre en una RTX A6000. Lo reusable es la loss, que es **una línea**
   (`faster_rcnn.py:121`), con el prior **hardcodeado en 0.04** y solo el caso binario. El costo
   de la familia D baja respecto de "escribir todo de cero", pero no baja a "clonar y correr".
2. **Los 68.3 / 69.3 de ZoomMIL estaban mal atribuidos.** Son de **BRIGHT** (Tabla 2, un dataset
   de mama), no de CAMELYON16. En CAMELYON16 (Tabla 3) usa 10× → 20× y da 83.3 / 84.2, **a la par
   de CLAM-SB**. La fuente secundaria estaba cruzada.
3. **El µm/px de MIDOG: 0.23 a 0.26** en sus seis escáneres, y MITOS-ATYPIA-14 a 0.2455. **TCGA
   (0.2325) cae dentro del rango** y corre sin reescalar; el privado (0.465) está a 2× de todos.
4. **ZoomMIL tolera una pirámide en µm/px, pero su preprocesamiento no.** El factor de expansión
   entre magnificaciones se deriva de la razón medida de parches (`zoommil.py:114`), así que
   admite razones arbitrarias. Pero `preprocessing.py:452` lee el aumento **solo de
   `aperio.AppMag`** y, si no está, **asume 40× con un warning**: nuestro privado es Ventana
   `.bif` y caería ahí, tratado como 40× estando a 20×. Error silencioso de factor 2.
5. **MS-CLAM sin anotación de parche degrada con gracia hasta ser CLAM** (tiene una §2.5 para
   eso). Así que no lo mata la escasez: lo mata la **parcialidad**. El primer término de su loss
   de atención empuja a cero la atención de todo lo no marcado, que con positivos parciales es el
   gradiente exactamente equivocado. Es la hipótesis **opuesta** a la del paper de PU learning.

**La recomendación se sostiene: D primero.** Pero se reestructura en un punto que la mejora: **el
paso 1 (go/no-go) no depende del paper de Zhao**, porque necesita pesos públicos de un detector y
ese paper no publica ninguno. Quien tiene tooling público es el ecosistema de MIDOG
(`DeepPathology/MIDOG_reference_docker` y `MIDOG_evaluation_docker`, no bajados). Desacoplar la
prueba barata de la decisión cara es exactamente lo que uno quiere.

**Dos matices que hay que llevar a la reunión y no estaban.**

- **El régimen de "incompleto" que testea el paper de PU learning es suave**: borran hasta dejar
  una marca por parche de 500×500, o sea **~73 % de retención**. Nosotros tenemos 26 marcas en
  4799 parches. **No evalúan ese régimen.** Esa es la salvedad honesta, más que el tamaño del
  efecto. (Que además estaba subvalorado: el +0.011 es contra BDE; contra el baseline es
  **+0.037**, el 70 % del hueco recuperable, y el recall llega casi al techo.)
- **CellViT a 0.50 µm/px, la escala del privado, pierde mucho**: recall de detección 0.82 → 0.60,
  quedando por debajo de HoVer-Net a 0.25. Y el 1.85× es de la variante chica; SAM-H rinde 1.39×.
  Que no tiene clase mitótica quedó verificado del modo más fuerte: **cero apariciones** de la
  palabra en 23 páginas.

**Un dato lindo de MIDOG:** su unidad de dato **no son WSI**, son **ROI de 2.0 mm²** elegidas por
un patólogo, que es exactamente el campo del recuento de Nottingham y por lo tanto los ~141
parches contiguos del §2.b del README. MIDOG resuelve "cuántas mitosis hay acá dentro" y nos deja
"dónde está el acá dentro". Y sus ROI tienen 20 o menos mitosis cada una, comparable a nuestras
26: la diferencia no es la densidad de anotación, son los **200 casos** contra nuestra **una
lámina**.

**Defecto encontrado y corregido:** `papers_mitosis.md` terminaba con dos etiquetas sueltas
(`</content>`, `</invoke>`) de una escritura anterior, commiteadas el 2-ago.

**Estado del job 4774 al cierre:** vivo, ~1 h 45 de corrida, brazo control 30×10, sin `Traceback`
ni `FAILED`. ETA ~lunes 20:30.

> **Actualización lunes 3-ago 15:25** (la sesión quedó abierta hasta el día siguiente): el job
> lleva **19 h 12 min** y **cerró 5 de 8 brazos** (`30×10`, `27×10`, `30×9`, `21×10`, `30×7`),
> va por `15×10`, **26 de 40 runs**, sigue sin `Traceback` ni `FAILED`. **La ETA del prereg
> quedó corta:** suponía que los brazos chicos serían más rápidos (~37 min/run) y los `mtime`
> reales dan **~70 min/run** en los últimos, así que el cierre cae en la **madrugada o mañana
> del martes 4-ago**, no el lunes 20:30. No es un fallo del job; conviene anotarlo al escribir
> `resultados.md`.

**Sigue sin empezar** rehacer el deck del B8, que ahora tiene material nuevo para una lámina de
«hacia dónde sigue».

---

## Sesión del 3-ago-2026 (lunes, tarde)

**La fecha de la reunión quedó resuelta, y era la que el repo ya tenía.** Ernesto confirmó a las
15:30 que **la reunión del lunes 3-ago no ocurrió** (se movió o se canceló) y que **sigue en pie
la del viernes 07/08/2026**. Con eso se cierra el hallazgo **C1** de la auditoría, abierto desde
el 2-ago: los tres registros del 07/08 (`reunion_31jul_redireccion.md:5`, `current.md:1088` y
`:1123`, más la memoria `reunion-24jul-encargos-b8`) **no estaban stale**, eran correctos. La
decisión de la auditoría de registrar la del 3-ago sin borrarlos fue la correcta. **El deck de
SI-MIL, construido para el 07/08, apunta a la fecha correcta y no hay título que corregir.**

**Entregado: el material de los papers, en el formato que pidió Ernesto.**
[`sprints/B8_sprint8/tareas_geometricas/hojas_reunion.md`](../sprints/B8_sprint8/tareas_geometricas/hojas_reunion.md),
una hoja por paper, condensado de los cinco estudios del 2-ago sin volver a abrir un PDF. Cuatro
hojas (PU learning, CellViT, ZoomMIL, MS-CLAM) más media hoja de anexo de MIDOG, que no es
candidato sino la fuente de datos que vuelve ejecutable el paso 1. Adelante va la recomendación
(**D primero, en dos pasos**) con la tabla comparativa de los cuatro por supervisión exigida, y
las **tres cosas que hay que decir sí o sí**: que el paso 1 está desacoplado del paper de Zhao,
que el régimen de anotación que ese paper evalúa (~73 % de retención) no es el nuestro (26 marcas
en 4799 parches), y que la pregunta que decide si la familia D existe es si hay más láminas
anotadas y quién es «GDT». Todos los números salen de los estudios ya verificados contra los PDF;
no se agregó ninguna afirmación nueva.

**Job 4774, a las 15:27:** sin cambios respecto del handoff de las 15:25. 19 h 17 min, 5 brazos
cerrados, `15×10` en curso, **26 de 40 runs**, cero `Traceback` y cero `FAILED`.

**Novedad de la cola, que explica la ETA:** aparecieron **dos jobs ajenos** de `capstone` (4778 y
4780, lanzados hace 6 h y 4 h) en el mismo nodo. La GPU está compartida entre tres trabajos, lo
que es coherente con que los runs pasaran de ~37 a ~70 min. Refuerza que el cierre del grid caiga
en la madrugada o mañana del **martes 4-ago**. No hay que lanzar nada, así que la regla de
cortesía no obliga a ninguna acción; queda anotado para el `resultados.md`.

---

## Sesión del 3-ago-2026 (lunes, 17:20) — el hallazgo de mitosis necesita forma presentable

**Sesión de exposición**, sin GPU y sin tocar nada que el job 4774 lea (workaround H).

**Ernesto no recordaba cómo verificamos que CLAM atiende las mitosis.** Preguntó qué pruebas
habíamos revisado antes de buscar papers y dijo que creía que «habíamos hecho algo de los mapas de
calor». Se le expuso la medición del 1-ago completa: el estadístico es el **AUC de ranking** de la
atención sobre los parches anotados (nulo 0.5), no el mapa de calor, que fue el subproducto.
Mitosis dio **0.890 ± 0.039** sobre los 4 checkpoints que nunca vieron la lámina (percentil mediano
91), el grupo mejor rankeado de los siete, por encima de Tumor (0.826), con grasa en 0.154. Con los
cuatro controles: nulo por traslación rígida (p en el piso, ninguna de las ~440 traslaciones
válidas lo alcanza), descarte del efecto de región (confinado sube a 0.903), control de
memorización (haberla visto suma solo ~0.056) y el sesgo de la anotación parcial jugando en contra.
Y el hallazgo que reordenó el sprint: **3 de esos 4 checkpoints clasifican mal la lámina**
(predicen `score_2` siendo `score_3`) mientras su atención está sobre las mitosis.

**Lo que eso destapó, y es el hallazgo de la sesión.** El resultado más importante del B8 no existe
en ningún entregable presentable: vive en `prereg.md`, `resultados.md`, dos memorias y dos PNG
sueltos. Si el que lo encargó no lo retuvo, Sebastián y Benjamín tampoco lo van a retener leyendo
un documento técnico. Queda como hallazgo **F1** de la sexta pasada de la auditoría.

**Entregado: [`papers_explicados.md`](../sprints/B8_sprint8/tareas_geometricas/papers_explicados.md).**
Tercer documento sobre los mismos cuatro papers, y complementario, no redundante: `papers_mitosis.md`
responde «qué encontramos y con qué evidencia», `hojas_reunion.md` responde «qué digo el viernes», y
este responde **«cómo funciona por dentro»**. Vocabulario común primero (clasificación contra
detección contra segmentación, MIL, los cuatro grados de supervisión, por qué la precisión deja de
ser medible con positivos parciales, µm/px), y después un capítulo por paper con una analogía por
término antes de la fórmula y un mini-ejemplo numérico por mecanismo: la loss PU con la cuenta
hecha, la caída de recall de CellViT explicada por los píxeles que pierde un núcleo de 8 µm, el
top-K derivable y el producto de Kronecker de ZoomMIL desarmados, y la ec. 3 de MS-CLAM aplicada a
cinco parches, que es donde se ve por qué la parcialidad lo mata. **No agrega ninguna afirmación**:
todo sale de los cinco estudios ya verificados contra los PDF el 2-ago.

**Encargo nuevo para la próxima sesión: rehacer el deck del B8.** Compactar **a la mitad** las
láminas de SI-MIL (no borrarlas: fue una de las tareas de investigación) y agregar la sección de la
medición de atención con sus dos PNG, tablas y conclusiones, en registro **muy pedagógico**, porque
va para Sebastián y Benjamín y porque el propio Ernesto dice que todavía no le queda claro. Esto
**precisa** la decisión del 31-jul («el deck se rehace con esta línea en vez de presentar el de
SI-MIL»), que leída sola autorizaba a borrar SI-MIL entero. Hallazgo **F2**.

**Job 4774 a las 21:07:** vivo, 21 h 07 min, **28 de 40 runs**, cero `Traceback` y cero `FAILED`,
en el brazo `15×10`. Siguen los **tres** jobs ajenos de `capstone` (4778, 4780, 4782) compartiendo
la GPU. No se leyó ninguna métrica parcial: solo se contaron archivos y se miró `squeue`, así que
el pre-registro sigue intacto.

## Sesión del 3-ago-2026 (lunes, 18:20) — el deck del B8 pasa a dos ejes

**Sesión de construcción**, sin GPU y sin tocar nada que el job 4774 lea (workaround H).

**Entregado: el deck rehecho, `sprints/B8_sprint8/presentacion_b8/CLAM_Sprint8.pptx`, 17 láminas.**
Cumple el encargo del 3-ago en sus tres partes. **SI-MIL compactado a la mitad y no borrado**: de
12 láminas de contenido a 6, fusionando pares con el método del 31-jul, o sea que lo que sale de
la lámina se cuenta hablando y el guion de la fusionada se reescribe. **Entra la sección de
atención**, ocho láminas, con las dos figuras y la leyenda obligatoria de las dos regiones de
escaneo. **Registro pedagógico**: el estadístico tiene lámina y figura propias, que es lo que
faltaba, y la escalera de los siete grupos es un gráfico de barras nativo y no una lista.

El archivo pasó a llamarse `CLAM_Sprint8.pptx`; el generador retira el `CLAM_Sprint8_SIMIL.pptx`
previo, que ya no describe el contenido. Ningún `.pptx` está versionado.

**Colisión de sesiones, resuelta.** Al interrumpir y retomar, el proceso anterior de esta misma
sesión quedó vivo y siguió trabajando solo: escribió 151 líneas del generador a las 17:49, con el
mismo plan. Se verificó que no fuera trabajo ajeno, Ernesto autorizó cerrarlo, y la construcción
siguió **sobre** lo que había dejado, que estaba bien hecho. Es el riesgo que el handoff anticipaba
en su §11 y la primera vez que se materializa: dos procesos con el mismo id de sesión escribiendo
el mismo archivo.

**Los números de la sección se verificaron contra `auc_por_checkpoint.csv` antes de escribirlos**
(4 checkpoints primarios, cabeza de la clase verdadera): la escalera completa reproduce el
`resultados.md` dígito a dígito. **Nada se re-midió.**

**QA visual hecho y con hallazgos**, que es la razón por la que se hace: la auditoría programática
dio cero avisos en las dos pasadas, y aun así mirando las láminas rasterizadas aparecieron cuatro
defectos de layout, todos corregidos. Dos figuras centradas en cajas con otra relación de aspecto,
que dejaban los rótulos de columna corridos respecto de lo que rotulaban; una tira de cuatro
paneles dentada porque cada uno se auto-dimensiona; y jerga interna en un remate («commiteadas»).

**Job 4774 a las 18:20:** vivo, 22 h 10 min, **29 de 40 runs**, cero `Traceback` y cero `FAILED`.
Siguen los tres jobs ajenos de `capstone`. No se leyó ninguna métrica parcial: el pre-registro
sigue intacto.

## Sesión del 4-ago-2026 (martes) — el grid E×S cierra en H_nula, y el pipeline resultó determinista

**Sesión de cierre de objetivo**, sin GPU. El job 4774 ya había terminado al abrirla, así que el
workaround H dejó de aplicar: no hubo jobs propios en cola en toda la sesión.

**El job.** 4774 cerrado el **4-ago 07:04**, lanzado el domingo 2-ago 20:10. **40 de 40 runs, cero
`Traceback`, cero `FAILED`, 40 `[DONE]`.** La provenance del `.out` confirma que corrieron los 8
brazos pre-registrados en el orden pre-registrado (`brazos=30:10 27:10 30:9 21:10 30:7 15:10 30:5
30:3`) desde el commit `b69531c` en `main`. **34 h 54 min de pared contra 24.3 h presupuestadas**:
el costo por run arranca en 36-37 min, exactamente lo estimado, y se dispara a 87 en la ventana de
los tres jobs ajenos de `capstone`, para bajar a ~62 al final. Tiempo de pared, no métrica, y así
quedó escrito.

**El veredicto: H_nula.** El contraste primario `(recorta S) − (recorta E)` a igual E·S da
**+0.022 / −0.014 / −0.002** de AUC en los peldaños 270 / 210 / 150. El signo de la media **se
invierte entre peldaños**, la desviación supera a la media en los tres, y el único peldaño a favor
tiene 3 de 5 folds. La frase que el grid ponía a prueba, «el margen de recorte está en S y no en
E», **no se sostiene**. Tampoco es H_alternativa: recortar expertos no gana con consistencia, gana
en un peldaño y pierde en otro.

Lo durable: **la ocupación describe cómo se reparte el peso, no dimensiona la capacidad
necesaria.** El brazo 30×5 tiene 150 slots totales, prácticamente el N_eff de 159.5 medido en el
encargo 1, y no marca ningún quiebre. Es la lectura que el pre-registro le había asignado por
anticipado a H_nula, así que no se eligió después de ver el número. Dos secundarios, los dos hacia
que la capacidad sobra: el piso 30×3 pierde **0.039 ± 0.062** con un 70 % menos de capacidad
(cruza cero), y dentro de la rama S no hay dosis-respuesta, hay un escalón y después meseta
(0.792, 0.797, 0.802, 0.786). La rama E ni siquiera es monótona: el **peor** brazo del grid es
27×10, que es el recorte más chico.

**El hallazgo que no se buscaba: el pipeline es determinista bit a bit.** El control 30×10, que el
prereg había presupuestado como verificación de reproducibilidad, salió **`md5` idéntico al job
4589 en los cinco folds**, incluido el `s_<f>_checkpoint.pt` de 2.5 MB. Se verificó que los runs
fueron reales (mtime del 2-ago, 260 épocas loggeadas, 40 `[DONE]`) y no un reuso encubierto de
artefactos. Vale para todo el proyecto y corta en dos direcciones: el reuso pareado de baselines
con misma semilla, splits y features es válido **por construcción**, y **cualquier réplica que
pretenda ser independiente tiene que cambiar la semilla**. El control **no** replicó el Δ +0.074
del 4589 y no podía hacerlo.

**Entregado**: `sprints/B8_sprint8/grid_expertos_slots/resultados.md` (10 secciones según el
prereg §6, con AUC y balanced accuracy por brazo y fold, matrices de confusión con el n por clase,
CLAM como fila de escala sin Δ por brazo, y la sección de lo que el resultado no dice) y
`results/b8_grid_es/` versionado, 200 archivos, ahora que los 8 brazos cerraron. **El pre-registro
no se tocó.**

**El Hallazgo 12 no se movió**: el grid midió capacidad, no rendimiento, y por diseño no calculó
ningún Δ contra CLAM por brazo. Lo que se cerró es el «eje de trabajo abierto» que colgaba de él.

**Auditoría, octava pasada** (`sprints/B8_sprint8/auditoria_coherencia/hallazgos.md`): cinco
hallazgos. El importante es H1, la frase «el margen está en S» propagada en cinco lugares que el
grid no sostuvo; se acotó en los cinco de forma aditiva, **preservando la medición**, que sigue
siendo correcta. La memoria de slots ya llevaba la salvedad bien puesta («no afirmar que recortar
S salga gratis, eso es el grid»); lo que se había propagado a `CLAUDE.md` era la versión sin ella.

## Sesión del 4-ago-2026 (martes, tarde) — el grid entra al deck, sin volverlo de tres ejes

**Sesión de entregable**, sin GPU y sin jobs propios. Ajenos en el nodo: los dos de `capstone`
y uno nuevo, `4791 oncomets` de `dbustama`, que arrancó durante la sesión. Ninguno lee este
árbol.

**La decisión, que era de Ernesto y no de la sesión.** El handoff dejaba tres encuadres
posibles para meter el grid E×S en `CLAM_Sprint8.pptx` y bloqueaba explícitamente decidirlo
solo. Ernesto eligió **(b): sección de cierre**, después de los dos ejes. Con eso **la lámina
del mapa del recorrido queda intacta**, el deck sigue siendo de dos ejes, y el grid se cuenta
como «lo que además cerró este sprint» con su propio rótulo. El motivo pesa más que la
elección: el hallazgo que cambia el plan es el de atención y no el grid, así que el grid no le
roba espacio; y pasar la lámina 3 a tres tarjetas costaba **reescribir su guion hablado**, no
mover geometría (su tira está calculada, `bw = (9.28 - 0.34) / 2`).

**Las tres láminas**, todas a partir de `grid_expertos_slots/resultados.md` y **sin re-medir
nada**:

- **18, el veredicto.** Los tres peldaños como barras divergentes alrededor del cero, con la
  desviación como bigote y un cuadro por fold. El mensaje visual es **el signo que se cambia de
  lado** y el bigote que cruza el cero en los tres, no la magnitud del Δ. El peldaño que pidió
  Sebastián va resaltado con su respuesta honesta: dos centésimas, 3 folds de 5, no alcanza.
- **19, la escalera de capacidad.** Las dos ramas con la línea que une los topes: escalón y
  meseta del lado de S, curva que ni siquiera es monótona del lado de E. Eje recortado desde
  0,75 y **rotulado en la lámina**. El remate pone la escala real, 0,25 entre folds contra 0,05
  entre brazos.
- **20, el determinismo**, como lámina de MÉTODO, con su límite escrito (esta GPU, este
  entorno) y las dos consecuencias opuestas en paneles.

**Las dos reglas del pre-registro se respetaron**: el H_nula se cuenta como tal, sin buscarle
el ángulo positivo, y **cero Δ contra CLAM por brazo**, ni siquiera como fila de escala. El
`prereg.md` y el `resultados.md` no se tocaron.

**El QA visual volvió a pagar, con la auditoría programática en cero.** Tres defectos, y dos de
ellos de una clase que las pasadas anteriores no habían registrado: **dos objetos válidos
superpuestos**. Un conector cruzando un rótulo que entra perfecto en su caja, y dos paneles
auto-dimensionados metiéndose bajo la regla de `takeaway_bar`. La lección que generaliza es que
el `h=None` que resolvió el desborde **creó** esta clase, porque un alto calculado al vuelo
puede invadir cualquier cosa posicionada con una constante. El tercer defecto era de contenido:
una leyenda que no decía qué significaba el relleno de sus cuadros.

**Entregado**: `generate_b8_deck.py` con la sección nueva y dos figuras nativas
(`barras_divergentes`, `escalera_capacidad`), `presentacion_b8/README.md` con la estructura de
**20 láminas** y la tabla de los tres defectos, y el guion hablado de las tres pasado por
`@humanizer-es`. Commit `e938bec`.

**Auditoría, novena pasada**: cinco hallazgos (I1 a I5), todos documentales y aditivos.

## Sesión del 4-ago-2026 (martes, noche) — el deck se revisó entero, y los defectos estaban en lo viejo

**Sesión de revisión**, sin GPU y sin jobs propios. Ajenos en el nodo: `4778` y `4780` de
`capstone`; el `4791` de `dbustama` ya salió de la cola. Ninguno lee este árbol, así que el
workaround H no aplicó en ningún momento.

**La misión del handoff se cumplió entera**: mirar las **20 láminas de una sentada** y leer el
guion **de corrido**, que es lo que el deck nunca había tenido. Se armó en tres tandas (30-jul,
3-ago, 4-ago) y cada una revisó lo suyo.

**Seis defectos, y el reparto es el hallazgo.** Dos en SI-MIL (láminas 8 y 9), cuatro en la
sección de atención (12, 13, 15 y 17) y **cero en las tres del grid**, que eran las nuevas y las
que ya se habían mirado. La lección que queda: al ampliar un deck, el QA de lo que uno acaba de
escribir es el barato y se hace solo; **el que paga es releer lo que ya estaba**, porque lo
viejo acumula la deriva de las convenciones que llegaron después, las promesas de continuidad
que la ampliación invalidó, y los choques de números entre láminas que antes no eran vecinas.

Los seis, y por qué ninguno es de layout:

- **La lámina 13 tenía punto decimal** en los siete valores de la escalera, al lado de su propio
  `0,890 ± 0,039` y de `azar = 0,5`. `_num()` nació con las figuras del grid el 4-ago y se
  aplicó solo a ellas; `barras_ranking()`, del 3-ago, siguió con `"%.3f"`. Queda como chequeo un
  barrido `\d+\.\d+` sobre el deck entero.
- **La ecuación 10 bajaba medio subíndice**: `L_CE` deja la E a tamaño completo porque `_x` es
  de un carácter. Silencioso y válido. Va `L_(CE)`.
- **El empalme de la 17 a la 18**, que el handoff había marcado como sospechoso y lo era. La 17
  cerraba prometiendo los papers («Es la parte que sigue») y detrás quedó el grid; y las dos
  láminas abrían con «Cierro con». **La lámina 3 no se tocó**: el deck sigue siendo de dos ejes
  con una sección de cierre.
- **26 contra 28 mitosis** en láminas contiguas. Los dos números son correctos, son marcas y
  parches. Se nombró la unidad en la 15, no se cambió el número.
- **Dos del guion**, que solo aparecen leyéndolo en voz alta: «nueve coma tres siete» donde el
  número es 0,937, y una frase que decía el mismo tipo de número de dos maneras distintas.

**Ningún número cambió** y no se tocaron el `prereg.md` ni el `resultados.md` de ninguno de los
dos experimentos, como pedía el handoff. Los valores de la lámina 13 se re-verificaron contra
`auc_por_checkpoint.csv` al cambiarles el formato. Verificado tras regenerar: auditoría en cero,
20 láminas, cero rayas, cero puntos decimales, un solo «Cierro con».

**Quedan dos decisiones de Ernesto**, ninguna bloqueante: el aire del cuadrante inferior derecho
de la **lámina 12** (cerca del 30 %) junto con los rótulos de fila que le faltan a su grilla
2×2, y si la **lámina 20** sigue abriendo en voz alta el pendiente de la réplica.

**Auditoría, décima pasada** (`sprints/B8_sprint8/auditoria_coherencia/hallazgos.md`): seis
hallazgos, J1 a J6.

---

## 4-ago-2026 (tarde, 17:30 a 17:55) — Ernesto revisó el deck y pidió un rediseño de doce puntos

Sesión corta y de análisis, **sin ejecutar el rediseño**. Se abrió para ejecutar las dos
decisiones de diseño que el handoff de las 17:30 dejaba abiertas y terminó siendo otra cosa:
Ernesto había estado mirando la presentación y trajo doce cambios propios, que **superan** a
esas dos y a la decisión de encuadre de la lámina 3.

**Las dos decisiones abiertas quedan resueltas por arriba.** La 12 no se retoca con rótulos de
fila y aire redistribuido: se rehace entera, con las figuras al doble y sin panel de texto. Y la
20, la del determinismo, **se borra**, con lo que la pregunta de si el pendiente de la réplica
se dice en voz alta deja de existir en el deck.

**Lo que Ernesto pidió**, en una línea cada uno: la 3 pasa a objetivos del sprint en el molde de
recapitulación; la 9 más sintética alrededor de su tabla; los rótulos de hipótesis de la 10 más
profesionales; el renglón que define el estadístico en la 11 convertido en figura; la 12 con las
figuras grandes, sin el panel, sin la fila que se lee repetida y con la procedencia escrita; el
guion de la 13 y el de la 14 más pedagógicos y el «lo que se ve» de la 14 a una línea; la 15 con
la tabla intacta y una sola lectura sintética; las cuatro familias reemplazadas por una lámina
de los tres papers, al final y sin las letras A/B/C/D; el grid sin «el encargo de julio» y con
el dataset nombrado; la 20 borrada; y una lámina nueva de objetivos propuestos al cierre. Más
dos pedidos transversales: **todos los títulos** minimalistas y precisos, y **todas las notas**
con un punteo guía antes de la prosa.

**Dos decisiones nuevas, elegidas por él en la sesión.** Los cuatro controles **se quedan**,
rehechos para que el nulo por traslación sea la figura de la lámina: dijo que la idea de mover
la mancha por la lámina le gustó pero que **no la entendió del todo**, así que esa lámina se
mide por si se entiende sola. Y los objetivos propuestos son **dos**: llevar la medición a más
láminas anotadas, y el paper de positivos parciales empezando por su go/no-go barato.

**La procedencia que preguntó Sebastián quedó verificada de punta a punta** y escrita en el
README de la presentación: la lámina, dónde vive, el geojson del patólogo con sus 61 polígonos,
las etiquetas de la lámina en nuestros CSV tarea por tarea, y los cuatro checkpoints con su
dataset de entrenamiento. De ahí salió **una corrección para el rediseño**: el deck dice
«checkpoints que NUNCA vieron esta lámina» y lo que se puede defender es «no la vieron **en
entrenamiento**», porque en los cuatro está en **validación**, que gobierna el early stopping.
El `prereg.md` y el `resultados.md` ya lo decían bien y **no se tocaron**. Se corrobora con la
fila `129741` de los `splits_*_bool.csv`, que es una línea y la puede correr cualquiera.

**Ejecutado, y es lo único**: `prep_assets_atencion.py` emite
`assets/atencion_region_anotada.png`, solo la región anotada. La fila que Ernesto vio repetida
es la de la región **sin** marcas, cuyo panel de anotaciones es tejido pelado. Dos pasadas
anteriores la habían tratado como un problema de explicación y le dedicaron un panel entero de
la lámina; no alcanzó. Esa fila no aporta: las 163 marcas caen todas en la otra región. El
generador conserva `FIG_MAPAS` en la grilla vieja y deja el asset nuevo en `FIG_MAPAS_ANOTADA`,
así que el deck **sigue regenerando idéntico**: 20 láminas, auditoría en cero.

---

## Sesión del 4-ago-2026 (martes, 19:00) — el rediseño quedó planificado, no ejecutado

Sesión corta, **sin editar el generador y sin GPU**. Rama `main` sincronizada, árbol limpio,
ningún job propio; ajenos `4778` y `4780` de `capstone` y `4800` de `gvenegas`, ninguno lee
este árbol. Se leyó el contexto completo que el handoff pedía (CLAUDE.md, el README de la
presentación, esta bitácora, las siete memorias del deck y los 2101 renglones de
`generate_b8_deck.py`) y se armó el plan de ejecución de los doce puntos. **Se cerró antes de
tocar código, por presupuesto de contexto**: el rediseño toca casi las veinte láminas y no
entra en lo que quedaba.

**Lo que sí quedó versionado**, en `presentacion_b8/README.md` §«Preparado para ejecutarlo»,
que es lo que la próxima sesión tendría que volver a derivar:

- **El mapeo de numeración**: la «lámina N» de los pedidos es el comentario `# ---- N-1 ----`
  del `build()`, porque las dos de apertura salen del template y no llevan comentario.
- **Cuál hipótesis es la primaria**, verificado contra `atencion_vs_patologo/prereg.md` §2: la
  primaria es **la del patólogo** (los marcados **no** rankean mejor que el azar), así que
  «Si tuviera razón» es la primaria y «Si no la tuviera» la alternativa, que es la que el
  resultado apoyó. Es la trampa del punto 3 del pedido: cambiarlas de lado tergiversaría el
  pre-registro.
- **La caja de la lámina 12 con la cuenta hecha**: ar 2,407 y `h = w / ar`, así que con las
  tres líneas de procedencia al pie el ancho tiene tope en ≈ 8,10 y cada panel queda en
  ≈ 4,05", contra 2,17" de la grilla actual.
- **Los dieciocho títulos propuestos** para el pedido transversal, a confirmar al ejecutar.

**El deck no cambió**: sigue en 20 láminas y regenera idéntico. El plan completo, lámina por
lámina y con la geometría de las cuatro figuras nuevas, viaja en el handoff de las 19:15.

---

## Sesión del 4-ago-2026 (martes, 19:10-20:00) — el rediseño de doce puntos, EJECUTADO

Sesión de escritura, **sin GPU**. Rama `main` sincronizada, árbol limpio al abrir; ningún job
propio, y de los ajenos solo `4780` de `capstone` y `4800` de `gvenegas`, que no leen este
árbol. Se ejecutaron **los doce puntos** del rediseño que Ernesto pidió a las 17:30, más los dos
transversales de títulos y notas. El deck sigue en **20 láminas**, regenera limpio, la auditoría
da **cero avisos**, y el barrido de `\d+\.\d+` sobre el archivo entero no encuentra ningún punto
decimal. **Ningún número cambió**, y ni el `prereg.md` ni el `resultados.md` de los dos
experimentos se tocaron.

**Lo estructural.** Las dos puntas del deck cambiaron de contenido. La lámina 3 pasó del mapa
del recorrido a **objetivos del sprint**, en el molde de recapitulación del B7: los seis en
infinitivo con su marcador de estado, y el objetivo 1, el escalado de slots, es **el único sin
lámina propia**, así que se cuenta en el guion con sus números (1858 láminas-fold, 159,5 de 300
slots, 29,98 de 30 expertos) y de paso deja dicho uno de los tres mensajes que hay que llevar a
la reunión. El final son ahora los **tres papers** (heredan el lugar de la lámina de las cuatro
familias, cuyo reordenamiento pasó entero al guion, y sin las letras A/B/C/D) y una lámina nueva
de **objetivos propuestos**, los dos que eligió Ernesto. La lámina del **determinismo se
retiró**: lo único que quedaba en pie de ella es una línea de comparabilidad en el guion del
grid, por si preguntan.

**Cuatro helpers nuevos**, todos después de `escalera_capacidad()`: `pie_lineas` (varias líneas
en un solo textbox, porque `caption` gasta 0,4" por renglón y las tres de procedencia no
entraban), `escala_auc`, `_mancha` con su `_RACIMO`, y `nube_traslaciones` con un generador
propio `_lcg` de semilla fija, para que el jitter salga igual en cada regenerada.

**La lámina 16 se rehizo entera**, que era la más importante porque Ernesto dijo que no la
entendía. El nulo por traslación es ahora el objeto visual: la lámina como panel, la zona de
atención alta adentro, la mancha real sólida dentro de esa zona, y tres traslaciones huecas, una
de ellas **también** dentro de la zona caliente, que es lo que explica que el nulo parta de 0,67
y no de 0,5. Debajo, la distribución contra el valor observado, que es la brecha que sostiene el
resultado.

**Tres defectos salieron de mirarla rasterizada**, y ninguno lo habría visto la auditoría: la
banda no decía en qué valores caía, el pie se partía en dos renglones, y **un racimo dibujado
con `fill.background()` se lee casi igual que uno sólido** sobre el celeste, con lo que la
distinción que sostiene la figura desaparecía. El fix del tercero es relleno blanco explícito.
Registrado en [[deck-qa-puntos-ciegos-chequeo]].

**La lámina 12** adoptó `FIG_MAPAS_ANOTADA` con la caja recalculada (`w = 8,10`, `h = 3,37`) y
las tres líneas de `PROVENANCIA` al pie. El panel de las dos regiones **se fue entero al
guion**: con la fila repetida fuera del asset, ya no explicaba nada de lo que se ve.

**Se miraron rasterizadas solo cuatro láminas**, las rehechas de cero: la 3, la 12, la 16 y la
20. Las otras nueve que se tocaron (9, 10, 11, 13, 14, 15, 17, 18, 19) **quedan sin QA visual**,
igual que el guion sin pasar por `@humanizer-es`. Y quedó anotado un defecto que **no es del
deck**: la leyenda de la figura de marcas mezcla español e inglés, y sale de la figura de
`atencion_vs_patologo/`, así que arreglarlo es regenerar esa figura.

---

## Sesión del 4-ago-2026 (martes, 22:00) — QA visual de las nueve láminas: un defecto, y era la 17

**Misión del handoff de las 20:00**, cumplida en su primera mitad: mirar rasterizadas las nueve
láminas que el rediseño de doce puntos tocó y nadie miró (9, 10, 11, 13, 14, 15, 17, 18, 19).

**Sin jobs propios.** El `4809` (`test_vis`) corre bajo la cuenta compartida `sdonoso` desde
`Test_D/D_abs/`, fuera de este árbol y de `clam_environ`: no lee nada nuestro, así que el
workaround H no restringió el cierre. Ajenos: `4780` de `capstone`, `4800` de `gvenegas`.

### El defecto: la lámina 17 se pisaba a sí misma

`barras_divergentes()` dibuja sus dos rótulos de lado («gana recortar expertos» / «gana recortar
slots») en `t − 0,34`, o sea **por encima del `t` que recibe**. El que la llama razona con ese
`t` y apila lo suyo hasta ahí. En el rediseño el bloque de arriba había ganado un renglón de
dataset de 9 pt, y con la figura en `TOP + 0,84` los rótulos le cayeron encima: se leía
«5 particiones» tachado por «gana recortar expertos».

**Fix**: la figura baja a `TOP + 1,06` y **cede 0,10" de alto** para pagarlo, así que la barra de
remate y todo lo que va debajo quedan exactamente donde estaban. Commit `e15e6e1`.

**Verificado midiendo tinta por renglón** sobre el rasterizado, no solo mirando: antes una sola
banda de 25 px (y=232..256) con el renglón y los rótulos fundidos, después dos de 15 y 16 px con
24 px limpios entre medio, y todas las bandas por debajo de y=618 idénticas antes y después.

### Dos sospechas que se cayeron al verificarlas

- **La polilínea de la 18**: a 100 dpi parecía arrancar en la esquina superior derecha de la
  primera barra. A 200 dpi arranca en el centro, y el código lo confirma
  (`topes.append((cx, base - alto))`). Se estuvo a un paso de «arreglar» algo que estaba bien.
- **El pie «la región anotada» de la 14**: es correcto, el asset es `mitosis_region_anotada.png`,
  ya recortado a esa región y no el lienzo con las dos.

### Lo demás

Las otras ocho láminas salieron limpias, incluidas las dos que el handoff marcaba como de mayor
riesgo por cambio de geometría (la 9 con la tabla agrandada y la 15 con dos paneles menos).
El barrido de reglas duras sobre las **20** láminas, **cuerpo y notas**, da cero puntos
decimales, cero rayas y cero letras A/B/C/D.

El «26 vs 28» que la sesión volvió a levantar **ya estaba resuelto** en la pasada anterior: la 15
dice «26 marcas de mitosis» justamente por eso, y los dos números son correctos.

### Queda abierto

Pasar el guion por `@humanizer-es` y leerlo en voz alta; la leyenda mezclada español/inglés de la
figura de la 12, que es de `atencion_vs_patologo/` y no del generador; y una duda de estilo menor
que no se tocó, que la lámina 11 dice «0,89» junto a la cinta y «0,890» en la banda.

Registro: `sprints/B8_sprint8/auditoria_coherencia/hallazgos.md` undécima pasada (K1 a K5),
`presentacion_b8/README.md` §«El QA de las nueve», y las memorias
[[deck-qa-puntos-ciegos-chequeo]] y [[deck-b8-dos-ejes-simil-mitosis]].

---

## Sesión del 4-ago-2026 (martes, 22:30) — el guion por `@humanizer-es`

**Misión del handoff de las 22:24**, cumplida salvo la lectura en voz alta. Sesión de
escritura, **sin GPU**. Rama `main` sincronizada con `origin` al abrir y árbol limpio.
Ningún job propio: el `4809` figura bajo la cuenta compartida `sdonoso`, pero
`scontrol show job 4809` confirma `WorkDir=/media/administrador/Storage1/sdonoso/Test_D/D_abs`,
fuera de este árbol y de `clam_environ`, así que el workaround H no restringió nada. Ajenos:
`4780` de `capstone`, `4800` de `gvenegas`.

### Lo que se hizo

El guion de las **19 láminas con notas** se extrajo a un archivo aparte para leerlo de
corrido, y recién sobre eso se corrió el loop de 4 pasos de `@humanizer-es`. **16 ediciones
quirúrgicas** en `generate_b8_deck.py`, todas dentro de los strings de `notes()`: de **7112 a
7028 palabras**, un **−1,2 %** casi calcado del −1,1 % del guion del B7, que es la medida de
que no se sobre-editó. El deck sigue en **20 láminas** y regenera con la auditoría en cero.

**Alcance respetado**: solo la prosa hablada. Los punteos guía de 3 a 5 renglones, los
títulos, los rótulos de figura y los remates de lámina no se tocaron, y ningún punteo
reintrodujo etiquetas de fase. Tampoco se tocó ningún `prereg.md` ni `resultados.md`, ni se
regeneró la figura de `atencion_vs_patologo/`.

**El diagnóstico confirmó lo que la memoria de la skill anticipaba**: en un guion maduro no
quedan tells de vocabulario (el barrido §7 dio cero, igual que rayas, «palanca» y decimales
en la prosa). Lo que había era **ritmo**, y solo se ve contando a lo largo de las 19 láminas:
aperturas «Acá está» 3 → 0, «conviene» 4 → 1, «es la que» 7 → 3, «es lo que» 7 → 4,
«exactamente» 8 → 5, aperturas «Est\* es el/la» 5 → 1. El rewrite **no metió tells nuevos**:
ninguna palabra que no estuviera antes aparece más de una vez.

### El defecto que salió de leerlo de corrido

La lámina 17 abría con **«Cierro con un encargo»**, y después venían **tres láminas más**
(18, 19 y 20). No cerraba nada. Ahora dice «Hago un paréntesis», y la 19, que antes abría
con «Y termino con los papers», abre con «Vuelvo a la mitosis», que cierra el paréntesis y
de paso saca el tercer «cierro/termino» de tres láminas casi seguidas. **Ninguna cuenta
automática lo caza**: aparece al leer las 19 seguidas, que es para lo que sirve sacar el
guion a un archivo aparte antes de editarlo.

### Lo que NO se cambió, a propósito

- Los **diez quiasmos «X, no Y»** son contrastes reales, no retórica (§9 de la skill), así
  que no se aplanaron.
- La salvedad **«una lámina y un anotador describen, no establecen»** se repite en las
  láminas 10, 16 y 20. Es una consigna sostenida a propósito, y la 20 lo dice en voz alta
  («lo dije al principio y lo sostengo»): repetición deliberada, no fórmula de IA.
- El **`0,89` de la lámina 11 junto al `0,890` de la 13** se re-verificó y sigue siendo la
  decisión de estilo que la sesión anterior tomó a propósito. **No es un defecto y no
  debería volver a viajar en un handoff.**

### Queda abierto

**Leer el guion en voz alta.** Se verificaron uno por uno los números escritos en letras
(los cuatro de la lámina 9, y los de la 11, 12, 13, 15 y 16), que es donde estaba el
precedente del «nueve coma tres siete», pero falta leer las 19 láminas corridas, que es lo
que caza lo que leer no caza.

Registro: `presentacion_b8/README.md` §«La pasada de `@humanizer-es`» y la memoria
[[deck-b8-dos-ejes-simil-mitosis]].

---

## Sesión del 4-ago-2026 (martes, 23:00) — el guion leído en voz alta

**Misión del handoff de las 22:41**, cumplida entera. Sesión de escritura, **sin GPU**. Rama
`main` sincronizada con `origin` al abrir y árbol limpio. Ningún job propio: el `4809` sigue
siendo de la cuenta compartida pero con `WorkDir=.../Test_D/D_abs`, fuera de este árbol y de
`clam_environ`, así que el workaround H no restringió nada. Ajenos: `4780` de `capstone`,
`4800` de `gvenegas`.

### Lo que se hizo

Deck regenerado (20 láminas, auditoría en cero), guion de las **19 láminas con notas**
extraído a un archivo aparte, y leído **de corrido**. **20 hallazgos**: **13 aplicados**
—los que son defecto real o frase que no entra en un respiro— y **7 dejados para Ernesto**
por ser decisiones de vocabulario. De 6089 a **6114 palabras** de prosa, +25 netas. Las
láminas no se tocaron, ni `prereg.md` ni `resultados.md`.

### Los dos que justifican la pasada

- **La lámina 12 decía «las ciento sesenta y tres marcas»** veinte segundos después de decir
  que las marcas son «sesenta y un polígonos». Son **163 parches**, no marcas
  (`atencion_vs_patologo/resultados.md:45`). Leído en pantalla uno completa solo; **dicho en
  voz alta es una contradicción**.
- **La lámina 6 decía «se pesa cada parche igual»**, con el sentido de «igual que arriba».
  Pronunciado se entiende «todos los parches pesan lo mismo», que es **lo contrario** de la
  ecuación que la lámina explica. Una frase correcta escrita que se vuelve falsa al decirla,
  y no hay cuenta ni skill que la detecte.

Los otros once: la unidad de la 3 (ahora dice «mil ciento setenta y seis láminas distintas,
mil ochocientas cincuenta y ocho contando cada partición por separado»), cuatro concordancias
y una comparación colgada, los cuatro decimales seguidos de la 9 —que la tabla ya muestra—,
dos frases de 55 y 48 palabras partidas, el rango de la 18 dicho de menor a mayor, y el
trabalenguas de la 5.

### Lo durable

**Las tres capas de QA cazan cosas disjuntas**: el barrido automático ve reglas duras y
geometría, `@humanizer-es` **cuenta** (racimos, arcos rotos), y la lectura en voz alta
**entiende de a una frase**. Ninguna sustituye a las otras.

### Queda abierto

Las **siete de vocabulario** (fold contra partición, los tres sistemas para decir decimales,
los términos técnicos sin definir, el orden 1 → 3 → 2 de la tabla de la 9, tres anglicismos,
el 4799 repetido y el «entre el nueve por ciento»), todas decisión de Ernesto. Y la leyenda
mezclada español/inglés de la figura de la 12, que es de `atencion_vs_patologo/`.

Registro: `auditoria_coherencia/hallazgos.md` duodécima pasada (L1 a L5),
`presentacion_b8/README.md` §«La lectura en voz alta», y las memorias
[[deck-qa-puntos-ciegos-chequeo]] y [[deck-b8-dos-ejes-simil-mitosis]].

---

## Sesión del 4-ago-2026 (martes, 23:20) — las siete de vocabulario, resueltas

**Misión del handoff de las 23:06**, cumplida entera. Sesión de escritura, **sin GPU**. Rama
`main` sincronizada con `origin` al abrir y árbol limpio. Ningún job propio: el `4813`
(`test_vista`, sucesor del `4809`) volvió a aparecer bajo la cuenta compartida con
`WorkDir=.../Test_D/D_abs` y terminó durante la sesión. Ajenos: `4780` de `capstone`, `4800`
de `gvenegas`.

### Lo que se hizo

Deck regenerado, guion extraído de nuevo a un archivo aparte, y las siete de vocabulario
puestas a decidir con recomendación y frase antes/después por cada una. Ernesto aprobó las
siete: **once ediciones** en `generate_b8_deck.py`, **todas en notas**. Prosa de 6104 a
**6117 palabras**, +13. Barrido de reglas duras sobre cuerpo y notas en **cero avisos**, deck
en 20 láminas con auditoría en cero. Ninguna lámina se tocó, ningún número cambió de valor,
ni `prereg.md` ni `resultados.md` se abrieron para escribir.

### Lo durable

**Una decisión de vocabulario del guion no se resuelve solo en el guion.** Tres de las siete
**cambiaron de dirección** al verificar el generador, porque el término está escrito en el
**cuerpo** de la lámina: `logit`, `softmax` y `sigmoide con temperatura` se leen en las
láminas 6, 7 y 8, y «rankearían» está en los dos paneles de hipótesis de la 10. Con el cuerpo
congelado, el guion **hereda su vocabulario**: quitar la palabra habría dejado al presentador
diciendo una cosa distinta de la proyectada, y ese desajuste cuesta más que el tell. Lo que
pide la convención es **definir antes de usar**, no evitar, así que se glosaron en vez de
sacarlas.

El mismo criterio dio vuelta lo de «fold» contra «partición»: la mezcla resultó **del deck**
—el cuerpo de la 17 usa las dos en el mismo bloque y «fold» está en tres cuerpos— así que se
arregló la **única frase del guion** donde conviven, en lugar de unificar todo.

Y queda fijada una convención nueva de pronunciación: **un decimal se dice tal cual, dos se
agrupan en decenas, tres en centenas** (`convenciones_deck_b5.md` §3.b, regla 12). No toca el
«0,89 vs 0,890», que es qué se escribe en la lámina y está cerrado.

### Queda abierto

**La leyenda mezclada español/inglés** de la figura de la lámina 12, que es de
`atencion_vs_patologo/` y no del generador: arreglarla es regenerar esa figura, y es decisión
de Ernesto. Es **el único pendiente que le queda al deck** de cara al viernes 07/08.

Registro: `auditoria_coherencia/hallazgos.md` decimotercera pasada (V1 a V5),
`presentacion_b8/README.md` §«Las siete de vocabulario, resueltas», y las memorias
[[deck-qa-puntos-ciegos-chequeo]], [[notas-presentador-guion-didactico]] y
[[deck-b8-dos-ejes-simil-mitosis]].

---

## Sesión 5-ago-2026 — evaluación de `wayfinder` y cosecha de dos primitivas

Ernesto trajo la skill `wayfinder` de mattpocock para evaluar si integrarla. **No se
integró**, y la evaluación está en [[wayfinder-evaluacion-y-cosecha]]: exige un tracker con
blocking nativo (`gh` **no está instalado**, y el remoto es un repo personal que Sebastián y
Benjamín no miran), traerla son 6 archivos porque su tipo de ticket por defecto depende de
otras cuatro skills, y su regla central de **un ticket por sesión** choca de frente con
[[procede-con-todo-el-plan-momentum]].

Lo que sí se hizo, que es trabajo de método y no de sprint:

- **`objetivos_sprint8.md` reestructurado como índice**, 319 → 168 líneas, adoptando la
  gramática de secciones del mapa: Destino / Notas / Decisiones tomadas / Todavía sin
  especificar (+ Pendiente sharp) / Fuera de alcance, conservando el «Qué no se afirma»
  propio. **Ningún dato se perdió**: cada número distintivo de la narrativa vieja se
  verificó presente en otro archivo antes de sacarlo. El formato quedó fijado en `CLAUDE.md`.
- **El encargo 2 salió a archivo propio**, `slots_entrenados_encargo2.md`, porque era lo
  único del doc sin otro hogar y sigue abierto.
- **`@grilling` portada y validada** (110 líneas, PASS), adaptada: los hechos los busca ella
  sin subagentes, y aterriza en el prereg de regla 9 o en las secciones del mapa.
  **Sin usar en producción todavía** ([[grilling-skill-portada]]).

`sprints/B7_sprint7/objetivos_sprint7.md` **queda en formato viejo a propósito**: el sprint
está cerrado y presentado, el formato es hacia adelante.

### Queda abierto (sin cambios respecto de lo de arriba)

La leyenda de la figura de la lámina 12 sigue siendo el único pendiente del deck de cara al
viernes 07/08. Esta sesión no lo tocó.

---

## Sesión 5-ago-2026 (tarde) — el deck baja de 20 a 16 láminas

Ernesto pidió **nueve cambios** sobre el deck del B8 y avisó que **la reunión con Sebastián
se adelantó al jueves 6-ago**; el viernes 7 es la de Benjamín, a la que probablemente no
llegue por clases. `FECHA_REUNION` del generador actualizada.

Los nueve están ejecutados, con la auditoría del generador en cero y **sin que cambie ningún
número** de los dos experimentos (ni `prereg.md` ni `resultados.md` se tocaron):

| Pedido | Resultado |
|---|---|
| 4 con menos bullets | la figura del paper pasa de **8,05 a 9,60** de ancho: la limitaba el alto de la caja, no la lámina |
| **5 + 6 + 7 en un diagrama** | una lámina con las dos ramas, el puente Top-K y el orden de las operaciones; salen las dos tablas |
| 8 pedagógica | las ecuaciones 3 a 10 dejan de ser tabla: la compuerta, la grilla de contribuciones que **es** la ecuación 9, y el entrenamiento conjunto |
| **10 + 11 en una** | las hipótesis bajan a una línea y mandan las dos cintas de parches reordenados |
| 12, 13 y 14 | intactas, por pedido explícito |
| 15: la tabla | ver abajo |
| 16: el dibujo | `mapa_traslaciones()`, con la zona de atención con forma y los rótulos pegados a lo que nombran |
| **17 + 18 en una** | los tres gráficos juntos, sin los renglones de prosa |
| 20 | molde de objetivos de la lámina 3 |

**El hallazgo de dato:** al armar la tabla de la 15 apareció que el «153 / 978 / 934 láminas
de entrenamiento» del README del deck son **los totales del split**, no la parte de train.
Los de entrenamiento son **120 / 783 / 746 / 749**, contados sobre los `splits_*_bool.csv`.
Y la pregunta que Ernesto hacía —por qué de la corrida de cinco aparecen dos folds— tenía
respuesta en `atencion_vs_patologo/resultados.md` §2.d y no en la lámina: **129741 cae en
`val` en los folds 0 y 2, y en `train` en 1, 3 y 4**. Ahora lo dice el pie.

**Los hallazgos de método**, en `auditoria_coherencia/hallazgos.md` §decimocuarta pasada y en
[[deck-qa-puntos-ciegos-chequeo]]: un **conector cruzando un texto** (los dos objetos válidos,
y la línea no tiene caja que medir), **offsets de rótulo fijos** en un helper reusado con otra
altura, y que **fusionar láminas vuelve vecinos a dos vocabularios** («fold» y «partición»
volvieron a chocar apenas se juntaron las dos del grid).

### Queda abierto

El **guion de las láminas nuevas y fusionadas** (4, 5, 6, 8, 12, 13, 14 y 16 de la numeración
nueva) no pasó por `@humanizer-es` ni por la lectura en voz alta; las no tocadas conservan las
dos pasadas del 4-ago. Es el pendiente principal de cara al jueves.

La leyenda mezclada español/inglés de la figura de marcas **deja de ser pendiente**: Ernesto
dijo que esa lámina queda como está.

## Sesión 5-ago-2026 (22:40) — el guion de las ocho, con las tres capas

El pendiente que dejaba el handoff. Las ocho láminas nuevas o fusionadas del recorte (4, 5,
6, 8, 12, 13, 14 y 16) pasaron por `@humanizer-es` y por la lectura en voz alta. **14
ediciones, las 14 dentro de `notes(...)`**, verificado a máquina: de las 33 líneas
modificadas, cero caen fuera de una llamada `notes()`, así que el cuerpo no se tocó y no hubo
que volver a mirar las láminas. Auditoría en cero, 6532 → 6512 palabras.

Detalle completo en `sprints/B8_sprint8/presentacion_b8/README.md` §«El guion de las ocho».
Lo que vale como método:

**Extraer a un archivo aparte hizo su trabajo.** El hallazgo mayor no es un tell de prosa
sino un **arco roto por la fusión**: la lámina 4 describe la figura del paper y la 5 volvía a
describir el mismo montaje desde cero, unas 110 palabras repetidas a veinte segundos de
distancia. Dentro del generador eso es invisible; en el archivo corrido salta. La 5 ahora se
apoya en la 4 y baja de 887 a 846 palabras. Otras tres repeticiones del mismo tipo (una de
ellas textual entre la 8 y la 13).

**La lectura en voz alta volvió a cazar un choque de vocabularios**, que es el defecto que
[[deck-qa-puntos-ciegos-chequeo]] predice cuando se fusionan láminas: la 14 decía «unidades»
y «niveles» mientras su **título** escribe «slots» y su cuerpo «peldaños». Se glosa una vez y
se adopta lo que está escrito, que es la regla del ADDENDUM 23:20.

**Un dato impreciso, que es lo que más importa.** La 14 decía que «poco más de la mitad» de
los 300 slots «concentra casi todo». Eso mezcla dos mediciones que
`q1_slots_escalado/resultados.md:38` separa a propósito: el número efectivo es 159.5 de 300,
y aparte 38 slots llevan la mitad del peso y hacen falta 169 para el 90 %. El archivo avisa
textualmente que *«`N_eff = 159.5` no significa 159 slots trabajando por partes iguales»*.
Ahora la 14 dice lo que ya decía la lámina 3, que venía revisada. **Ningún número del sprint
cambió.**

Y un dato vago que tenía valor: el tercer término de la pérdida de SI-MIL no pesa «bastante
alto», pesa **λ = 20** contra 1 de los otros dos (`simil_estudio.md:68`).

### Queda abierto

El **cuerpo** de la lámina 12 escribe «folds» y el de la 14 «particiones»: mismo choque, pero
del lado escrito, y el alcance de esta pasada era la prosa hablada. Es un `caption` de una
línea (`generate_b8_deck.py:2029`) y la decisión es de Ernesto.
