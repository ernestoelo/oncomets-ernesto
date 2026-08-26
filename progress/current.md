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

**Del guion, nada**: las 14 láminas con notas tienen ahora las tres capas.

Durante el cierre se verificó un falso pendiente: el cuerpo de la lámina 12 escribe «folds» y
el de la 14 «particiones», pero **la R5 de la decimocuarta pasada lo decidió así a propósito**
(en esa tabla «fold» es el identificador del checkpoint). La regla es no mezclarlos *dentro*
de una lámina, no unificarlos entre láminas.

## Sesión 6-ago-2026 — estudio del deck, y el grep que el H1 no había hecho

Sesión de **estudio**, no de construcción: el handoff del 5-ago la orientaba a dominar el
material antes de la reunión con Sebastián. **El deck no se tocó** — cero ediciones al
generador, cero regeneraciones, cero figuras — y ningún número del sprint cambió.

Guion extraído con `scripts/extraer_guion_deck.py` y leído entero: **16 láminas, 6511
palabras ≈ 50 min hablados**. Ese número es el que hay que contrastar con lo que dure la
reunión; si hay que comprimir, las candidatas por tamaño son la lámina 5 (846 palabras) y la
14 (697, que es el paréntesis del grid y no el mensaje del día).

Los ocho números que el handoff marcaba como de mayor riesgo de repregunta se verificaron
contra verdad de campo uno por uno y **los ocho reproducen**.

### Los dos hallazgos

**El grep del H1 buscó donde ya sabía que estaba.** La octava pasada (4-ago) corrigió «el
margen de recorte está en S» en cinco lugares, pero no barrió el repo entero: quedaron sin
acotar `q1_slots_escalado/resultados.md` (2 veces, una bajo el encabezado «Qué se puede
afirmar ahora») y la memoria `slot-unidad-de-morfologia`, que la usa como razonamiento de
apoyo. El primero es **el documento que originó la frase** y el que el handoff nombra como
verdad de campo del 159.5. Los dos corregidos de forma aditiva, con la redacción canónica de
`CLAUDE.md`; ningún número tocado. La lección de método quedó en la skill `@knowledge-audit`:
**el documento más peligroso no es el que repite la frase, es el que la originó**, porque ahí
está enunciada sin las salvedades que los demás le fueron agregando.

**132 negativos y 65 negativos son los dos correctos.** El deck dice 132 (del dataset) y el
B7 dice 65 (los evaluados). Contado sobre los splits reales: 862 láminas con 132 negativos,
cinco test **disjuntos** que cubren 429 con **65** negativos, 13 por fold exacto en las cinco.
Los otros 67 nunca se evalúan. Reconciliación anotada en `grid_expertos_slots/resultados.md`
§7, que es donde alguien la va a buscar.

### Queda abierto

Sin cambios respecto del handoff anterior: las **dos preguntas de la reunión** (cuál de las
tres lecturas es el encargo 2, y cuántas láminas anotadas hay y quién las anotó), la réplica
del dato abierto del 4589 con semillas nuevas (regla 9.b), el sign-off del patólogo, y
`@grilling` sin estrenar.

## Sesión 6-ago-2026 (tarde) — ensayo de la lámina 15, y la nota que no se entendía

Sesión de **ensayo hablado** antes de la reunión con Sebastián, que era ese mismo jueves. **El
deck no se tocó**: cero ediciones al generador, cero regeneraciones, cero figuras, y ningún
número del sprint cambió. El guion se regeneró solo para leerlo (es derivado y gitignored).

La lámina 15 se ensayó entera: 362 palabras de nota, de las cuales **46 son las cuatro líneas de
resumen del encabezado y no se hablan**, así que el arco dicho son ~316 palabras, **2 min 25 s** a
las 130 palabras por minuto que da el deck completo. Se desarmó en sus tres movimientos (las
cuatro familias escritas antes de la medición, qué reordenó la medición, por qué el primer paper),
más las repreguntas probables con su respuesta y su segundo golpe. **No se le encontró ningún
defecto de contenido.**

### Los tres hallazgos

**El más importante: una nota puede pasar las tres capas de QA y no entenderse.** Ernesto leyó
dos veces los dos párrafos finales de la nota de la lámina 9 (el confundido de las dos regiones de
escaneo) y no los entendió. Cada frase por separado es correcta; lo que falta es el eslabón entre
la complicación y el método. El AUC pareado está definido en la lámina **8**, y la 9 nunca vuelve
a decir que el «parche sin marca al azar» **incluye los 2303 parches de la otra región**, que es
exactamente lo que vuelve rival a la región. **La premisa no falta del deck: está a 4½ minutos y
la nota no la re-invoca.** Eso hace una **cuarta capa** de QA, y es la única que el autor no puede
correr, porque siempre tiene el método entero en la cabeza. Queda en
[[deck-qa-puntos-ciegos-chequeo]]. La reescritura está redactada y **NO aplicada**: editar el deck
el día de la reunión es decisión de Ernesto.

**El documento que se lee en la reunión tenía la fecha vieja.** `hojas_reunion.md` encabezaba con
«viernes 7-ago-2026» y la reunión con Sebastián fue el **jueves 6** (el viernes 7 es la de
Benjamín). Corregido, más ADDENDUM aditivo en las dos memorias que arrastraban la fecha. Los
registros históricos que dicen 07/08 no se tocan: eran correctos cuando se escribieron.

**26 y 28 no son la misma unidad, y ahora está la regla.** La décima pasada ya había registrado
que los dos son correctos, pero ninguno decía por qué difieren. Verificado sobre el CSV de parches
anotados: **26 cuenta polígonos del patólogo, 28 cuenta parches que tocan al menos un polígono de
mitosis** (26 puros + 1 compartido con núcleos de alto grado + 1 con tumor). Los siete grupos de
la tabla reproducen exacto con esa regla. Anotado en `atencion_vs_patologo/resultados.md` §1.

### Queda abierto

La reescritura de la nota de la lámina 9, con la redacción lista. Y sin cambios respecto del
handoff anterior: las dos preguntas de la reunión, la réplica del dato abierto del 4589 con
semillas nuevas, el sign-off del patólogo y `@grilling` sin estrenar.

---

## Sesión 6-ago-2026 (noche) — la reunión ya fue, y el deck se reordena entero

La reunión con Sebastián **ocurrió** (jueves 6). La de Benjamín del viernes 7 **se cayó**: Ernesto
tiene clases. El deck se presenta a Benjamín la **semana del 11-ago**, sin día confirmado, así que
la portada pasó de `06/08/2026` a `Agosto 2026` hasta que haya fecha.

**Lo que dijo Sebastián.** Que la prueba de la atención contra las marcas del patólogo «estuvo muy
buena», y que lo importante es **dónde se está perdiendo la información** que hace que el modelo
prediga mal. Y un orden nuevo para la presentación: **abrir con el grid de expertos y slots**,
**transicionar a los mapas de calor contra las marcas**, y **dejar SI-MIL al final**. Pidió además
copia del deck **sin notas del presentador** para mirar los mapas y los parches.

### Los dos hallazgos de contenido

**El +2 de 26 → 28 son dos efectos grandes que casi se cancelan.** La sesión anterior dejó la regla
de conteo correcta (26 polígonos, 28 parches) pero el mecanismo sin calcular, y el neto de +2
invita a leerlo como «dos marcas cruzaron un borde». Calculado desde el geojson y las coords del
h5: **26 + 10 − 8 = 28**. Diez marcas caen sobre el borde entre dos parches y suman uno cada una;
siete parches tienen más de una mitosis adentro y restan ocho (6×1 + 1×2). La causa de fondo es de
escala: una marca de mitosis mide **36 px de lado** contra los **256 px del parche**, o sea entre
el 2 % y el 4 % de su área. **El neto no es portable a otra lámina** — depende de la dispersión de
las marcas. Tabla completa en `atencion_vs_patologo/resultados.md` §1.a.

**Los siete grupos comparten estadístico pero no precisión, y la escalera no lo mostraba.** Con n
de 12 a 48 parches, el IC 95 % del AUC (Hanley-McNeil) va de **0,10 de ancho en tejido adiposo a
0,33 en estroma**. Son **dos incertidumbres distintas** y el deck solo contaba una: la `sd` mide
cambiar de **modelo** (±0,039 en mitosis) y el IC mide que el patólogo hubiera marcado **otras**
mitosis (±0,080). El caso que obliga a corregir el guion es **estroma**: se venía diciendo que
«queda justo en el azar, que es donde uno esperaría», y con su IC de 0,37 a 0,70 la lámina no puede
distinguir estroma evitado de estroma atendido — es una ausencia de dato contada como dato.
**Mitosis aguanta** (su IC no toca 0,5). Tabla en `resultados.md` §1.b.

### Un defecto de deck encontrado de paso

La lámina «La pregunta medible» dice que se mira dónde caen «los **163** marcados» y muestra
**0,89**, que es el número de los **28 de mitosis**. Los 163 son los siete grupos juntos y no
tienen AUC calculado en ningún artefacto. Mismo patrón que el Q1 de la pasada anterior: cada frase
pasa la auditoría por separado y el defecto está en el eslabón. **Sin corregir.**

### Qué se alcanzó a tocar del generador

Cuatro ediciones, todas coherentes entre sí y verificadas (`generate_b8_deck.py` corre limpio, 16
láminas, auditoría en cero): la fecha de portada, `ESCALERA` a 5-tuplas con el semiancho del IC,
`barras_ranking` dibujando el bigote, y dos helpers nuevos (`cadena_cuenta` para la cuenta 26→28,
todavía sin usar). **El reordenamiento de `build()` NO se hizo.**

### Queda abierto

**El pedido entero de Ernesto sobre el deck**, que es lo grande y va al handoff con su detalle:
reordenar las tres secciones, eliminar la lámina de objetivos del sprint y la de los tres papers,
retitular «Del embudo al reporte», poner la de cierre en el molde exacto de la de objetivos,
reforzar cuatro láminas con la estadística, reescribir el guion para el orden nuevo y para
Benjamín, regenerar y sacar la copia sin notas para Sebastián. Más: los dos papers de
`papers_11_agosto/` sin leer, el envío a Sebastián de los dos recomendados, R1 y el Q1 de la pasada
anterior sin aplicar, y los pendientes de sprint de siempre.

---

## Sesión 7-ago-2026 — el deck reordenado, y los dos entregables

Sesión de construcción pura, sin GPU. Se ejecutaron **los seis pedidos** que Ernesto dejó el
6-ago por la noche más **los dos entregables**. El deck queda en **14 láminas**, la auditoría
del generador en cero, **ningún número cambió** y ni el `prereg.md` ni el `resultados.md` de los
dos experimentos se tocaron.

**El orden nuevo lo pidió Sebastián y no se re-decidió**: abre el grid de expertos y slots,
sigue la medición de atención contra las marcas del patólogo, y SI-MIL queda al final. La
audiencia es Benjamín, la semana del 11-ago.

### Lo estructural

`build()` **dejó de ser un bloque de mil líneas**: cada lámina es una función `lam_*(prs)` y
`build()` es la lista de llamadas. El cuerpo de cada bloque quedó donde estaba, a cuatro
espacios, así que la conversión no movió una sola línea de indentación. Los comentarios
`# ---- N. Título ----` **perdieron el número**, que quedaba stale en cada reorden y obligaba a
mantener a mano un mapeo entre «la lámina N» de los pedidos y el código.

**Se fueron dos láminas** con sus constantes: «Objetivos del sprint» (`OBJETIVOS`) y «Tres
papers para la rama de mitosis» (`PAPERS`). Nada de su contenido se perdió: el molde de la
primera lo hereda «Objetivos propuestos», y el razonamiento de la segunda bajó al guion de esa
misma lámina, que es donde justifica el objetivo propuesto 2.

### Las cuatro láminas de la medición, con la estadística adentro

Es el pedido de fondo: Ernesto dijo que le falta entender la parte estadística para defender qué
mide cada tipo de tejido. «La pregunta medible» ahora **nombra** el estadístico (U de
Mann-Whitney normalizada) y **hace la cuenta en pantalla** (`28 × 4771 = 133 588` pares, y en el
89 % gana el marcado), con tres tarjetas que dicen contra qué se mide cada grupo, por qué son
comparables y qué significa quedar bajo 0,5. La escalera **explica el bigote** y cambia sus dos
tarjetas por **las dos incertidumbres**. Y la lámina de los 28 parches abre con la **cadena
26 → +10 → −8 → 28** y la escala del 2 al 4 % del área del parche, que es el puente a la
siguiente.

También se aplicaron los dos pendientes heredados: **R1** (la lámina decía «los 163 marcados» y
mostraba el 0,89 de mitosis) y **Q1** (la nota de los mapas no decía contra qué compite un
parche marcado).

### Lo que salió del QA visual, con la auditoría en cero

**Dos líneas cruzando un texto**, la clase que ningún chequeo de cajas ve. Los dos rótulos
rotados de las cintas se pisaban entre sí, y era **preexistente**: un shape rotado 270° ocupa a
lo alto lo que mide de ancho, y el bbox que reporta es el de antes de rotar, así que el chequeo
los veía separados cuando se solapaban en una pulgada. Y la línea punteada del azar **cruzaba el
rótulo de Linfocitos**, porque el valor iba pegado a la punta del bigote y para los grupos bajo
el azar esa punta cae antes de la línea del 0,5. Ahora los siete valores van en columna fija.

### El guion

Reescrito para el orden nuevo, pasado por `@humanizer-es` y por la lectura en voz alta. Lo que
solo se oye: dos «paso a» seguidos en un cambio de lámina, una frase del grid que
**contradecía la portada** al pasar de cierre a apertura, el 26 contra 28 sonando a
contradicción durante dos láminas, y **tres preguntas «para hoy» apiladas al final** porque
SI-MIL pasó al cierre. Lo transversal: fusionar láminas vuelve vecinos a dos vocabularios, pero
**reordenarlas rompe las referencias cruzadas**, que es otra cosa; dos frases prometían algo
«en la segunda parte» apuntando a una medición que ahora ya ocurrió.

### La copia sin notas

`sin_notas.py`, versionado al lado del generador: cirugía de zip, no python-pptx. Deja **82
partes del paquete byte-idénticas** (fuentes embebidas, imágenes y theme intactos) y 0 láminas
con notas. Se versionó el script y no el `.pptx`, porque Sebastián va a querer la copia de nuevo
cada vez que el deck cambie.

### Queda abierto

Los **dos papers de `papers_11_agosto/`** sin leer ni fichar, y el **envío a Sebastián** de
ZoomMIL y positivos parciales (falta ver si los PDF están en el repo). Tres decisiones de
Ernesto sobre el deck: la lámina de cierre queda muy vacía con el molde exacto, las dos figuras
de mitosis cedieron un 20 % de alto, y la leyenda mezclada de la figura de marcas. Las dos
preguntas de la reunión del 6-ago siguen sin respuesta conocida. Y los pendientes de sprint de
siempre: la réplica del 4589 con semillas nuevas, el sign-off del patólogo y `@grilling` sin
estrenar.

---

## Sesión 11-ago-2026 — reunión de papers mañana, y un deck planificado sin construir

Sesión **de planificación, cero código**. Ernesto avisó que **mañana miércoles 12-ago hay reunión
con Sebastián para abordar los cuatro papers de la rama de mitosis** y que no leyó ninguno. Pidió
un archivo visual, de esta ocasión sola, con las **figuras originales de los autores** y **notas
del presentador** que sirvan para las dos cosas: leerlas en vivo y estudiar de ahí mirando la
figura. Tope de diez láminas. El plan quedó **aprobado y sin ejecutar**: lo construye la sesión
siguiente.

**La reunión es un frente nuevo, no la continuación del 6-ago.** Verificado antes de planificar:
la del 6-ago con Sebastián ocurrió pero trató la medición de atención y el reordenamiento del
deck, y de ese reordenamiento salió justamente la lámina de los papers. O sea que los cuatro
papers **nunca se expusieron**, y el material que los cubre sigue siendo el mismo de siempre:
`hojas_reunion.md` (una hoja por paper), `papers_explicados.md` (el mecanismo desde cero) y los
cuatro `*_estudio.md`. Nada de eso se re-verifica ni se re-lee contra los PDF: el deck es la
**forma presentable** de material ya verificado el 2-ago.

### Lo que se decidió, con las tres preguntas que Ernesto contestó

Diez láminas: portada, una de encuadre («lo que tenemos son positivos parciales»), **una por
paper** con la figura del autor a la izquierda y tres bloques de síntesis a la derecha, el cuadro
comparativo de los cuatro, la recomendación en dos pasos, las tres cosas que hay que decir sí o
sí, y la pregunta que decide. El reparto **una lámina por paper** ganó contra dos por paper
porque deja lugar al cuadro y a la recomendación, que es lo que la reunión tiene que resolver.
Las notas van en el formato que el deck del B8 ya usa: punteo de tres a cinco renglones y después
la prosa hablada. Y se construye con el template OncoMets, no con un archivo suelto.

### El dato que salió al elegir las figuras

**El paper de PU learning no tiene figura de método.** Sus cuatro figuras son todas resultados
cualitativos de detección, porque lo que propone es una loss y no una arquitectura. Las otras tres
sí tienen su figura de arquitectura en las primeras páginas. Consecuencia para el deck: la lámina
de PU learning se apoya en la Fig. 1 de la pág. 14, que son detecciones sobre **MITOS-ATYPIA-14**,
un dataset de mitosis en mama, con flechas que marcan lo que el método encuentra y los
competidores pierden. Es representativa del resultado, no del mecanismo, y el mecanismo hay que
contarlo en la nota.

Las cuatro elegidas: PU learning Fig. 1 pág. 14, CellViT Fig. 1 pág. 2, ZoomMIL Fig. 1 pág. 2
(la comparación de métodos, que es la más explicativa de las suyas) y MS-CLAM Fig. 1 pág. 5.

### Queda abierto

**Construir el deck**, que es el pendiente principal y tiene fecha de mañana. El plan completo
está en `/home/sdonoso/.claude/plans/necesito-planificar-la-reunion-rustling-firefly.md` y el
handoff lo arrastra entero. Sin cambios en el resto: los dos papers de `papers_11_agosto/` sin
fichar, las dos preguntas del 6-ago sin respuesta, la réplica del 4589 con semillas nuevas, el
sign-off del patólogo y `@grilling` sin estrenar.

---

## Sesión 11-ago-2026 (noche) — el cuarteto no era el que decía el plan

Sesión de construcción del deck de papers, **interrumpida a propósito y cerrada a mitad de
camino**. Arrancó ejecutando el plan aprobado unas horas antes y se dio vuelta en el segundo
paso: **Ernesto corrigió cuáles son los cuatro papers de la reunión de mañana.**

### La corrección, y lo que arrastra

El plan y el handoff daban por hecho que el cuarteto era el que fichamos el 2-ago: PU learning,
CellViT, ZoomMIL y MS-CLAM. Los cuatro reales son:

| | Paper | Origen |
|---|---|---|
| 1 | PU learning, Zhao et al., MELBA 2022 | nuestra búsqueda del 2-ago |
| 2 | ZoomMIL, Thandiackal et al., ECCV 2022 | nuestra búsqueda del 2-ago |
| 3 | **NPKC-MIL**, Wang y Yuan, iScience 2024 | Sebastián, 6-ago |
| 4 | **Pleomorfismo nuclear**, Mercan et al., npj Breast Cancer 2022 | Sebastián, 6-ago |

O sea que **los dos papers de `papers_11_agosto/` no eran un pendiente lateral: son la mitad de
la reunión**. Llevaban desde el 6-ago sin leer, y tres pasadas de auditoría los venían listando
como pendiente menor. **CellViT y MS-CLAM salen del deck**; sus hojas quedan como fichas válidas
y se marcó el desvío con un ADDENDUM al encabezado de `hojas_reunion.md`.

La regla de la sesión anterior, «cero números nuevos, todo sale de `hojas_reunion.md`», **dejó de
aplicar para la mitad del deck**: los dos papers nuevos no tenían ni una línea escrita, así que
hubo que leerlos completos contra el PDF.

### El encuadre que aparece al ordenar el cuarteto real

El encargo del 31-jul tenía **dos** tareas, mitosis y grado nuclear, y nuestra búsqueda del 2-ago
quedó volcada a mitosis: tres de los cuatro eran de esa rama, y grado nuclear se apoyaba en
CellViT, que ni siquiera tiene clase mitótica ni puntaje de pleomorfismo. Los dos que trajo
Sebastián llenan justo ese hueco y el cuarteto queda **simétrico, dos papers por tarea**. Ese es
el encuadre del deck.

Y de ahí sale el mensaje que conviene decir temprano en la reunión: **la escala física juega al
revés en cada rama**. La mitosis se cuenta a 40× y el privado está a 20×, así que esa rama
arrastra un reescalado con riesgo; el paper de pleomorfismo entrena y evalúa a **0,5 µm/px**, que
es prácticamente nuestro privado (0,465). Es el único de los cuatro donde la escala no estorba.

### Los dos papers, fichados (`papers_11_agosto/hojas_papers_nuevos.md`)

**NPKC-MIL** (iScience 27:109826, abierto, código en `github.com/WxpHB/NPKC-MIL`). No cambia el
agregador: le suma a la loss dos penalizaciones, una de parche y una de núcleo, esta última una
red de grafos sobre los núcleos segmentados con HoVer-Net, con 16 features hechas a mano por
nodo. **El detalle que lo vuelve nuestro: esa rama entrena sobre los `c = 8` parches de atención
más alta**, o sea que es la idea que propuso el propio Sebastián (correr núcleos solo sobre los
mejores parches de CLAM) publicada y con números. Reportan 96,25 % de accuracy contra 86,25 % de
CLAM-SB en binario normal/canceroso sobre 476 láminas. **Y sus propias ablaciones no cierran**:
las dos restricciones por separado suman +2,5 y +1,25, y juntas dan +12,5, sin explicación y con
80 láminas de test. Eso hay que llevarlo dicho por nosotros.

**Pleomorfismo nuclear** (npj Breast Cancer 8:120, abierto, grupo de Radboud). Ataca **nuestra
tarea con nuestro nombre**. Dos ideas: acotar al tumor invasivo con un detector epitelial
congelado, y puntuar el pleomorfismo como **regresión continua entre 1 y 3** en vez de clasificar
en tres clases, con la referencia = **promedio de 10 patólogos** por región, porque forzar una
mayoría tira el desacuerdo, que es justamente la señal de que la cosa es un continuo. Kappa 0,61
contra la mayoría, mejor que 8 de los 10 patólogos, y el kappa medio pareado más alto del panel.
Trabaja a 0,5 µm/px, **no exige anotar ni un núcleo**, y agrega promediando, que es lo contrario
del máximo local de mitosis: las dos tareas del encargo piden operadores opuestos. Lo que lo
frena: **el código no está público** y la primera etapa es in-house; lo que sí está público son
las 118 láminas de test y el evaluador oficial.

### Lo que quedó construido

`prep_assets_papers.py` versionado, que es la primera vez que la receta de recortar una figura de
paper queda en el repo (la de SI-MIL fue ad-hoc). Las cuatro páginas se verificaron buscando el
texto del epígrafe, no de memoria, y las cajas se midieron una vez y quedaron congeladas como
constantes. Los cuatro PNG están en `assets/`. La de PU learning se **recompone**: de la grilla
de cuatro métodos por tres parches quedan tres columnas y dos filas, que son las que sostienen el
argumento, y lo que sale tiene que ir dicho en el pie de la lámina.

### Queda abierto

**El deck entero**: no existe `generate_papers_deck.py` ni `.pptx`. El contenido de las diez
láminas está escrito y verificado, y el diseño lámina por lámina está en el README del
directorio nuevo. Falta también mirar dos de los cuatro PNG (`fig_zoommil.png` y
`fig_pleomorfismo.png`), que se generaron pero nadie miró. El resto del sprint sin cambios: las
dos preguntas del 6-ago sin respuesta, la réplica del 4589 con semillas nuevas, el sign-off del
patólogo y `@grilling` sin estrenar.

---

## 12-ago-2026 (mañana) — el QA de las figuras cerrado, y el mapa para escribir el generador

Sesión corta, con la reunión encima. La misión era construir el deck de las diez láminas y
**no se llegó a escribirlo**: el contexto se consumió en la lectura previa (el handoff, el
README del directorio, las dos hojas de contenido, el relevamiento del generador del B8 y las
imágenes). Lo que sí quedó cerrado es lo que **tenía** que hacerse temprano y lo que ahorra esa
misma lectura la próxima vez.

### QA visual de las cuatro figuras: cerrado

`fig_zoommil.png` y `fig_pleomorfismo.png` eran las dos que nadie había mirado, y se miraron
**de entrada**, que es cuando se puede ([[image-api-qa-limit]]). **Pasan las dos** y ninguna
necesita re-recorte: paneles completos y epígrafes enteros, con las etiquetas `10x` / `2.5x` de
ZoomMIL sin cortar y la barra de color del pleomorfismo incluida. Con eso, las cuatro figuras
del deck están verificadas.

De paso quedó escrito en el README **qué muestra cada una de las cuatro**, panel por panel y con
sus rótulos. No es adorno: leer las cuatro imágenes cuesta contexto, y los pies de lámina y el
guion se escriben describiendo la figura. La sesión que siga **no tiene que abrir ninguna**.

### El mapa para copiar los helpers

El README §4 pedía copiar del generador del B8 «solo los helpers que este deck usa». Ese archivo
tiene 2594 líneas y encontrarlos leyendo se lleva medio contexto. Quedaron relevados **por rango
de líneas**: son **seis bloques contiguos** que cubren la lista entera, extraíbles con `sed`.

Y salieron dos cosas que hay que tocar al copiarlos. `retitular_portada` trae el título del
sprint hardcodeado. Y sobre todo: **`auditar` no ve dos defectos que este deck sí puede tener**,
distintos de los que ya lista [[deck-qa-puntos-ciegos-chequeo]]. Una tabla nativa cuyo texto no
entra se le escapa, porque el `row_h` de `simple_table` es un mínimo y PowerPoint crece la fila
solo. Y una pila de paneles de alto automático que se pasa hacia abajo y se mete debajo de la
barra de remate tampoco dispara aviso, porque no está «fuera del lienzo». Como el molde de las
cuatro láminas de paper es exactamente eso, tres paneles apilados de alto automático, el
generador tiene que imprimir el borde inferior del último panel de cada lámina y compararlo
contra la barra.

### Queda abierto

**El deck entero, igual que ayer**: no existe `generate_papers_deck.py` ni `.pptx`. Lo que
cambió es que ahora está todo lo previo hecho, así que la sesión que siga puede escribir el
generador de entrada, sin abrir imágenes y sin releer el generador del B8. El resto del sprint
sin cambios: las dos preguntas del 6-ago sin respuesta, la réplica del 4589 con semillas nuevas,
el sign-off del patólogo y `@grilling` sin estrenar.

---

## 12-ago-2026 (mediodía) — el deck de los cuatro papers, construido y sin estrenar

Se escribió `sprints/B8_sprint8/presentacion_papers_mitosis/generate_papers_deck.py` y quedó
producido `Papers_Mitosis.pptx`: **once láminas físicas**, que son las diez del plan contando la
apertura heredada del template como dos (portada de marca más lámina de título). Construido
SOBRE el `.pptx` de Deep-LLM-V, con `forzar_barlow` y `auditar` en cero avisos. El `.pptx` está
gitignored por `sprints/**/*.pptx`: **se regenera corriendo el script**, no está en el repo.

**Y quedó sin estrenar.** La reunión del miércoles 12-ago con Sebastián **ocurrió, pero sin el
deck**. O sea que el entregable está terminado y verificado y todavía no tiene audiencia. Qué
hacer con él es una decisión abierta, no un pendiente técnico: no le falta trabajo.

### El molde de las cuatro láminas de paper: la retícula quedó CONSTANTE

El README anticipaba que el ancho de la columna izquierda no se puede fijar, porque las cuatro
figuras van de 1,27 a 3,09 de relación de aspecto. La solución que quedó es la inversa de lo que
sugería esa frase: **lo constante son las dos regiones**, 4,96" para la figura con su pie y
4,10" para los bloques, iguales en las cuatro láminas; la figura se dibuja centrada dentro de su
región y ocupa lo que su forma permite. Fijar el ancho de la *figura* habría dejado a PU
learning con una columna de texto de 5,24" y a ZoomMIL con una de 4,10", que es exactamente la
diferencia de lectura que el molde existe para evitar.

Alturas resultantes: PU 3,48 × 2,74" · ZoomMIL 4,96 × 1,86" · NPKC-MIL 3,65 × 2,60" ·
pleomorfismo 4,96 × 1,61". Las dos anchas son las que la relación de aspecto achata, tal como
estaba previsto.

### La trampa que ningún chequeo listaba: el PIE

El README §4 y [[deck-qa-puntos-ciegos-chequeo]] avisaban de la pila de paneles metiéndose
debajo de la barra de remate, y el generador la chequea. **Ese chequeo mira una sola columna.**
En una lámina a dos columnas la otra también crece sola, y ahí se coló el defecto de verdad: el
**pie de la figura** se metió debajo de la barra en PU learning, con `auditar` en cero y el
chequeo de paneles en verde. Lo cazó mirar la lámina rasterizada.

Van **dos chequeos, uno por columna**, y el fix no es solo el aviso: con la región izquierda de
ancho constante, el alto del pie **no depende de la figura**, así que se mide primero y el alto
de la figura sale de lo que sobra. Con el ancho de la figura variable el cálculo era circular.

De paso apareció un bug de medición heredado: `panel` calculaba el wrap contra el ancho de la
**caja**, pero PowerPoint mete 0,1" de margen por lado, así que el texto envuelve 0,2" antes y
subestimaba una línea. Corregido acá; **`generate_b8_deck.py` conserva la versión vieja** y no
se tocó, porque su deck ya está cerrado y verificado a ojo.

### La tabla, y el guion

El cuadro comparativo de la lámina 8 se dimensionó con `alto_tabla` para **llenar** la zona: a
9 pt medía 1,64" y dejaba pulgada y media de blanco hasta el remate. Quedó a 11,5 pt, ocupando
2,97". Cuando la prosa compite con una tabla, gana la tabla.

El guion pasó por `@humanizer-es`. El riesgo que el handoff había anticipado era real: **tres de
las cuatro láminas de paper abrían con «Este paper»**, y la quinta con «Este cuadro». Ahora cada
una entra por lo que el paper hace. También se sacaron cuatro anuncios que no decían nada
(«Empiezo por explicar», «Planteo la situación») y la misma transición hacia «lo que lo frena»
repetida tres veces.

Verificado sobre el archivo: cero Arial y cero Calibri fuera de los fallbacks de script del
theme, solo Barlow embebida en el PDF rasterizado, cero puntos decimales, cero guiones largos,
cero «palanca» y cero «al revés», y el punteo de cada nota entre tres y cinco renglones.

### Queda abierto

Qué se hace con el deck, que es decisión de Ernesto y no trabajo pendiente. **Y qué salió de la
reunión del 12-ago**: esta sesión no lo registra. El resto del sprint sin cambios: las dos
preguntas del 6-ago sin respuesta, la réplica del 4589 con semillas nuevas, el sign-off del
patólogo y `@grilling` sin estrenar.

---

## 13-ago-2026 (tarde) — Lo que salió de la reunión del 12-ago, y el plan para ejecutarlo

Sesión de **planificación, sin ejecución**: Ernesto pidió separar el planificar del ejecutar
para que una sesión limpia corra lo planificado. El plan completo está en
[`.handoffs/handoff_B8_20260813_1330.md`](../.handoffs/handoff_B8_20260813_1330.md).

**Queda contestado el pendiente que abría el handoff anterior.** De la reunión del 12-ago
salieron dos encargos:

1. **Un paper para el viernes 14-ago.** La tarea es pleomorfismo nuclear, mitosis o grado
   nuclear, y el encuadre es el pipeline que diseñó Sebastián inspirado en NPKC-MIL: donde los
   autores usan HoVer-Net para encontrar lo relevante, **nosotros usamos CLAM y su mapa de
   calor**, y sobre los parches de mayor atención corre un **segundo modelo especialista**. El
   paper que se busca es el de esa segunda etapa, y el criterio de Ernesto es que sea
   integrable y que suba métricas.
2. **El «CSV duplicado» de la lámina 129741.** Sebastián explicó que las dos láminas que
   aparecen al evaluar no son dos láminas sino un error de un `.csv` donde se repetía dos veces
   lo mismo, dijo que hay más WSI con el mismo defecto y que por ahora basta registrarlo.
   **Ernesto pidió verificarlo antes de registrarlo**, porque no entendió la explicación.

### Lo que sí se verificó en esta sesión, contra disco

**La lectura literal de la frase de Sebastián no se sostiene.** No hay ningún `.csv` nuestro
con la lámina dos veces: cero `slide_id` duplicados en los 13 `dataset_*_label.csv` de
`csv_privado/`, y lo mismo en `csv/`, `csv_tcga/`, `csv_histai/`, `csv_balance/` y
`csv_balance_ci/`. Tampoco en los cuatro `dataset_validation.csv`, que son los que
`run_create_patches.slurm` pasa como `--process_list` y por lo tanto los que gobiernan qué se
parchea (561, 3350, 864 y 1925 filas, cero duplicados en las cuatro).

Lo que él describe, si existe, está aguas arriba de nuestros CSV. La lectura que mejor calza es
que **el `.bif` contenga dos escaneos de la misma lámina**, con la duplicación en el worklist de
digitalización del laboratorio, que no tenemos.

**Y ahí el B8 tiene un punto débil que conviene apretar antes de descartar nada.** El test que
concluyó que las dos regiones son tejido distinto comparó parches «gemelos» geométricos y dio
coseno 0.708 contra 0.503 de azar, pero **las dos regiones difieren en 1280 px de ancho**, cinco
parches de 256, así que un emparejamiento ingenuo pudo estar desalineado. El test bueno barre un
desplazamiento 2D y mira la distribución, no la media; y hay uno más barato y más concluyente
todavía, que es comparar las dos miniaturas con openslide.

**El resultado principal sobrevive pase lo que pase**, y conviene decirlo para no sobredimensionar
el asunto: la corrida definitiva `con_region/` está confinada a la región anotada (N = 2496,
AUC 0.903) y **no toca la otra región**. Lo que quedaría contaminado es el universo `lamina`, el
del 0.890. El guion de la lámina 5 del deck tampoco queda falso: dice que hay dos regiones y que
las marcas caen todas en una, y las dos cosas siguen siendo ciertas.

### Queda abierto

Los dos encargos, para la sesión de ejecución. Y una pregunta para Sebastián que la verificación
no puede contestar sola: **cuál es el `.csv` del que hablaba**.

---

## 13-ago-2026 (tarde/noche) — Ejecución del handoff: el paper leído y el barrido de regiones corrido

> Sesión de **ejecución** del plan de la entrada anterior. Cerrada a pedido de Ernesto para que
> una sesión limpia siga. **Ninguno de los dos encargos está terminado**, y los dos quedaron
> mucho más cerca: lo que falta de A es redacción, y lo que falta de B es un bug.

### Encargo A (vence el viernes 14-ago): investigación cerrada, documentos sin escribir

Se aplicó el rubric de cinco criterios del handoff sobre cuatro candidatos y **gana Jaroensri
et al., npj Breast Cancer 8:113 (2022)**, DOI `10.1038/s41523-022-00478-y`. PDF y Supplementary
**bajados** a `sprints/B8_sprint8/papers_14_agosto/` y **leídos enteros**.

**Por qué gana:** es la forma del pipeline de Sebastián, publicada. Una máscara elige dónde
mirar, tres modelos de **parche** puntúan los tres componentes de Nottingham (que son nuestras
tres etiquetas CAP), y una etapa 2 liviana de scikit-learn agrega a puntaje de lámina. Nuestro
cambio sería reemplazar su máscara de carcinoma invasivo por la atención de CLAM. Y cumple el
criterio de Ernesto de «aumentar métricas» en la forma más fuerte que hay: **supera el acuerdo
entre patólogos en los tres componentes** (kappa modelo-patólogo 0,64 / 0,39 / 0,69 contra
inter-patólogo 0,56 / 0,36 / 0,55), con TCGA como test set, que es cohorte nuestra.

**Los dos hallazgos que valen más allá del paper, y ninguno estaba dicho en el sprint:**

1. **Excluye explícitamente las láminas a 20×**, para garantizar 40× en mitosis y pleomorfismo.
   Nuestra cohorte privada está **entera** a 0,465 µm/px (verificado esta sesión sobre las 490,
   sin una excepción). Sus campos son 32 µm a 0,25 para mitosis, 256 µm a 0,25 para
   pleomorfismo y **1 mm a 1,0 µm/px para formación tubular**, así que **tubular es el único de
   los tres que nuestro privado alimenta sin ampliar**. Eso **corrige el encuadre** que traíamos
   desde el 11-ago, donde pleomorfismo era la rama «a favor» por Mercan a 0,5 µm/px.
2. **Probaron features de núcleo hechas a mano para pleomorfismo y no mejoraron.** Es evidencia
   en contra de la rama de NPKC-MIL, de un grupo con más datos.

Y un dato de MIDOG 2025 (arXiv `2606.07368`) que vale solo y no depende de quién gane el rubric:
fuera de los puntos calientes curados la tasa de falsos positivos de los detectores de mitosis
**se triplica** (aumento del 208 %), sobre 365 casos y 12 tipos tumorales. O sea que restringir
el detector a los parches de mayor atención **es la forma correcta del problema**, medido por un
challenge, y es el mejor argumento externo que tenemos para el diseño de dos etapas.

**Lo que falta son los tres documentos.** Para que no haya que releer el PDF, todos los números
verificados quedaron en `papers_14_agosto/notas_extraccion_jaroensri.md`, incluida la cuenta de
cuántos parches por lámina cuesta cada rama y la tabla del rubric puntuada.

### Encargo B: el alcance medido, el veredicto NO

**Lo que pidió Sebastián cuantificar está cuantificado.** Barrido de las 589 carpetas de `wsi/`
leyendo `openslide.region[N].*`: de las **490** con `.bif` sin sufijo de tinción, **139 declaran
más de una región de escaneo** (130 con dos, 8 con tres, 1 con cuatro), o sea el **28,4 %**.
Lista con nombres en `regiones_escaneo/laminas_multiregion.csv`. Tenía razón en que hay más, y
son bastantes más de lo que uno esperaría.

**El veredicto sobre la 129741 no se registra, porque no está establecido**, que es la condición
que puso Ernesto. Tres tests, resultado partido:

- **Features con el desfase corregido:** el óptimo del barrido 2D no está en el nominal sino en
  dx=−256, dy=50432, y sube el coseno de 0,708 a **0,811** contra 0,502 al azar. Pero **el test
  no decide**, y su propio control lo demuestra: el mejor coseno contra la otra banda da 0,9013
  y contra la **propia** banda da 0,9009. Las features CONCH son tan suaves sobre el tejido que
  el parche de al lado ya se parece 0,90.
- **Píxeles a escala gruesa: NCC 0,9569 registrada contra −0,159 del control espejado**, y a ojo
  los seis fragmentos tienen el mismo contorno y la misma disposición. Evidencia fuerte de que
  es la misma lámina escaneada dos veces.
- **Píxeles a level 0: no corrió bien.** NCC ≈ 0 y el control también ≈ 0, o sea que los dos
  recortes no miran el mismo sitio. Es un bug de mapeo de coordenadas, no un resultado.

### Queda abierto

Los tres documentos de A (vencen mañana), el bug del test de level 0 de B, y la pregunta a
Sebastián sobre cuál es el `.csv` del que hablaba. Detalle en el handoff.

---

## 13-ago-2026 (noche, sesión corta) — Encargo A ENTREGADO: los tres documentos del paper

> Sesión de **redacción pura**: la investigación ya estaba cerrada por la sesión anterior y todos
> los números verificados vivían en `papers_14_agosto/notas_extraccion_jaroensri.md`. No hizo
> falta releer el PDF, que es exactamente para lo que ese archivo se había escrito.

### Lo entregado

Los tres documentos que vencían el **viernes 14-ago**, en `sprints/B8_sprint8/papers_14_agosto/`:

| Archivo | Qué es |
|---|---|
| `busqueda.md` | El rubric de cinco criterios **puntuado sobre los cuatro candidatos**, las fichas de cada uno con DOI, y por qué pierden los otros tres. Es lo que hace auditable la elección |
| `jaroensri_estudio.md` | El estudio a fondo, con los números del texto del PDF y del Supplementary |
| `hoja_jaroensri.md` | **Hoja 7**, la que se lee en la reunión sin abrir nada más, con su sección «No se afirma» |

Ganador: **Jaroensri et al., npj Breast Cancer 8:113 (2022)**, DOI `10.1038/s41523-022-00478-y`.

### Lo que salió al escribir, y no estaba en las notas de extracción

Tres cosas, las tres de leer el PDF con la pregunta de integración puesta encima:

1. **El ahorro del top-k depende de la razón entre el campo del especialista y el parche del
   selector**, y eso reordena las ramas. Nuestro parche mide 119 µm. Mitosis pide 32 µm y entra 14
   veces, o sea **280 inferencias por lámina** con los 20 parches de atención. Pleomorfismo pide
   256 µm, más grande que nuestro parche: **20 inferencias**. Tubular pide 1 mm, y **una sola
   ventana ya cubre unos 70 parches nuestros**, o sea que el top-k **casi no ahorra nada**.
   Cruzado con la escala sale incómodo: **la rama donde nuestro privado alcanza (tubular) es justo
   donde el recorte por atención no sirve**, y donde sí sirve (mitosis) hay que ampliar 1,86×.
2. **Su máscara y nuestra atención no son el mismo objeto.** La suya es **semántica**: un
   clasificador de parche de 3 clases (no tumor / in situ / invasivo), AUC 0,95 contra anotación
   de patólogo, y la máscara sale por argmax sobre parches de 1024. La nuestra es un **ranking de
   saliencia** entrenado solo con etiqueta de lámina. La sustitución **no es neutra y está sin
   medir**; lo único a favor medido es que el ranking cae sobre las mitosis marcadas en una
   lámina (AUC 0,890).
3. **Observación, no resultado:** en la Supplementary Tabla 5, los puntajes de mitosis tomados del
   **informe de patología original** dan c-index **0,65**, por encima del modelo continuo (0,59) y
   del voto de mayoría de tres patólogos (0,58). Nos toca porque **nuestras etiquetas salen del
   informe CAP**. La salvedad que impide usarlo fuerte: esas filas parecen computadas sobre el
   subconjunto con informe disponible (n = 550) y no sobre las 829, y el paper no las plantea como
   comparación cabeza a cabeza. Queda registrado como observación.

También quedó documentada la mecánica reusable de su etapa 2: para mitosis usa **cinco percentiles
de la densidad mitótica** (5, 25, 50, 75, 95), **no el máximo**, y la cadena de detección es umbral
0,915 → erosión con elemento de 16 µm → componentes conexas → centroide, con la densidad medida en
**baldosas de 1,8 × 1,8 mm al 50 % de solape**, que es el punto caliente de Nottingham con otro
nombre.

### Queda abierto

**El encargo B**, entero desde donde lo dejó la sesión anterior: el bug de mapeo de coordenadas
del test de píxeles a level 0, que es lo único que separa del veredicto sobre si las dos regiones
de la 129741 son la misma lámina. Y la pregunta a Sebastián sobre **cuál es el `.csv`** del que
hablaba. Detalle en el handoff.

---

## Sesión 14-ago-2026: el test de píxeles a level 0, arreglado

El encargo B estaba bloqueado por un test que daba cero. **Ya no da cero**, y de paso el
diagnóstico que se había dejado escrito resultó equivocado en las dos pistas que ofrecía.

### El bug no era el que estaba anotado

Se había apuntado a un término faltante en el mapeo de coordenadas y a una contradicción entre
`dy = +512` (features) y `dy = −640` (píxeles). Verificado contra el archivo, ninguna de las dos:

- La 129741 tiene `region[0].x = region[1].x = 0`, así que el término que faltaba **vale cero
  acá**. Era un bug latente de generalidad, no la causa. Arreglado igual.
- No había contradicción: derivando el signo de la búsqueda gruesa sale `DY = −512` contra los
  −640 medidos, y esos **128 px son la cuantización** de la grilla del h5 (±128) más la de la
  miniatura (±64). Los dos números eran compatibles.

La causa real es de **resolución**: la posición en la región 1 se derivaba de un único offset
global medido a **level 6**, donde 1 px de miniatura son **64 px de level 0, unas cinco células**.
El test daba cero **por construcción**, midiera lo que midiera. Lección reusable: un registro a
level N no sirve para decidir a level 0 si su cuantización queda por encima de la escala del
objeto que se quiere comparar.

### El arreglo y lo que mide

`registro` quedó reescrito en dos etapas: la posición **no se deriva, se busca**. Ocho ventanas
repartidas en grilla 4×4 sobre la región se localizan primero dentro de ±2048 px a level 2, y
después se refinan a level 0 con barrido de rotación. El control de sitio equivocado corre con
**los mismos grados de libertad** que la señal.

| | Señal | Control de sitio equivocado |
|---|---|---|
| NCC a level 0, medio | **0.3820** | 0.0493 |
| rango | 0.2488 .. 0.4521 | máximo 0.0671 |
| ventanas sobre el máximo del control | **8 / 8** | |

Hay correspondencia celular real, a 29.5 sd del control. Maquinaria verificada aparte en
`tests/test_registro_geometria.py`, incluido el signo de la rotación (invertido da 0.31 en vez
de 0.98, así que sin ese test la conclusión podía salir al revés).

### Por qué igual NO hay veredicto

El barrido de rotación **sigue pegando en el borde** (0.38 es cota inferior), el θ óptimo varía
entre ventanas cuando un cuerpo rígido daría uno solo, el ajuste rígido deja residuo **RMS
103 µm**, y sobre todo **0.38 cae entre las dos hipótesis**: un re-escaneo bien registrado daría
0.8 a 0.9, pero dos secciones seriadas cortadas a 3 a 5 µm **comparten núcleos** y también dan
correspondencia parcial.

También se **corrigió un argumento equivocado**: que la disposición de los seis fragmentos
probara algo. No prueba nada, porque los fragmentos van embebidos juntos en el bloque y el corte
sale como una cinta única que conserva la disposición. Dos secciones seriadas la conservan **por
construcción**.

### Queda abierto

Cerrar el veredicto iterando el ajuste (usar la rotación ajustada como centro del barrido, no
cero) y **conseguir un control positivo empírico** corriendo el test sobre una muestra de las
otras 138 láminas multi-región: si alguna da 0.9, esa es la referencia contra la cual leer el
0.38, y de paso se sabe cuáles están afectadas de verdad. Sigue pendiente la pregunta a Sebastián
sobre **cuál es el `.csv`**. Detalle en el handoff.

---

## 14-ago-2026 (tarde) — la segunda tanda de candidatos, y uno que ataca los tres bloqueos

Encargo de Ernesto una hora antes de la reunión con Sebastián: candidatos de **segunda etapa**
para el pipeline que él diseñó, donde CLAM elige los parches de mayor atención y un modelo
especialista los procesa para mitosis, pleomorfismo o grado nuclear. La condición nueva respecto
del encargo A del 13-ago es que el modelo tenga **trasfondo arquitectónico para rastrear y
mapear** la tarea, no solo puntuar el parche.

Entregable: `sprints/B8_sprint8/papers_14_agosto/hoja_especialistas.md` (Hoja 8).

### Lo que ordena la búsqueda

Jaroensri, el ganador del encargo A, es un **puntuador**: entra un parche, sale un número. Lo
pedido hoy es un **mapeador**: polígono y clase de cada núcleo dentro del parche. Solo el segundo
puede localizar núcleos dispersos y compararlos contra su vecindario, que son literalmente las
dos frases del patólogo que originaron el objetivo 5.

### El candidato

**HoVer-NeXt** (Baumann et al., MIDL 2024, PMLR 250:61-86) toca tres cosas que teníamos anotadas
como bloqueos separados:

| Bloqueo nuestro | Lo que trae |
|---|---|
| CellViT y HoVer-Net no cuentan mitosis | **clase de mitosis propia** (extendieron Lizard) |
| el privado está a 20× y la rama pide 40× | **1,8 s/mm² a 0,5 mpp**, nativo, sin ampliar |
| la rama de núcleos quedó en pausa por costo | **17× más rápido** que HoVer-Net, pesos públicos |

Detrás quedan **CellViT++** (cabezas nuevas con poquísimos ejemplos, que es la vía por la que las
26 marcas dejarían de servir solo para validar) y **MIDOG 2025** (RF-DETR y el ganador DINOv3-H+
con LoRA, los dos con pesos).

### Lo que NO se afirma

Nada de la Hoja 8 está verificado **contra el PDF**: es una hora de búsqueda web. El riesgo
principal está identificado y es concreto: la clase mitótica de HoVer-NeXt está entrenada sobre
**colon**, y el modelo que sí cubre mama (PanNuke) no tiene esa clase. Ernesto subió el artículo
a `sprints/B8_sprint8/hover_next.pdf` para que una sesión limpia lo estudie.

---

## 14-ago-2026 (tarde/noche) — HoVer-NeXt leído: el candidato aguanta, y su prueba no

Misión del handoff `handoff_B8_20260814_1400.md`: estudiar el PDF de HoVer-NeXt (MIDL 2024, 26
pág.) y verificar las seis afirmaciones que la Hoja 8 había escrito **con búsqueda web**. Leído
entero, cuerpo y los dos apéndices, vía el volcado `hover_next.txt`. Sin GPU, sin descargas.

Entregable: `sprints/B8_sprint8/papers_14_agosto/hovernext_estudio.md`. Hoja 8 corregida en el
mismo turno.

### El veredicto: las seis se sostienen, dos decían otra cosa

**Ninguna afirmación resultó falsa.** Pero las dos que se leen como «qué tan bueno es esto»
estaban mal atribuidas:

- **El F1 0,84 es de detección BINARIA** («¿acá hay un núcleo?», sin decir de qué tipo). El F1
  medio **por clase** es **0,606**, y **la mitosis sola, que es la que decide, da 0,55 a 0,62**
  (Supp. C.3, que el resumen no muestra), con **precisión 0,545** y recall 0,720. Sobre-cuenta
  casi al doble.
- **La balanced accuracy 0,758 promedia seis clases entre las que NO está la mitosis.**

Dos apuntes que la búsqueda web no daba: **no es el estado del arte en PanNuke** (CellViT 0,498
contra 0,477) y en la clase **neoplásica** queda **por debajo de HoVer-Net**; y **los propios
autores dicen que el mPQ es la métrica que hay que evitar** (§2.5), así que citar el 47,7 como
titular es apoyarse en lo que el paper desaconseja.

### Las tres preguntas abiertas, contestadas

- **¿Validan fuera de colon?** Sí, y **mejor de lo temido**: la tabla por tejido pone a **mama 6ª
  de 19** (mPQ 0,495), por encima del promedio y muy por encima de **colon, que sale 17ª**. Pero
  **la clase mitótica nunca se midió fuera de CRC**, y ese riesgo queda entero.
- **¿Qué predice cada juego de pesos?** Son dos vocabularios distintos, y **las ventajas no se
  suman**: Lizard-Mitosis tiene mitosis y 0,5 µm/px pero es todo colon; PanNuke cubre mama pero sin
  mitosis y a 0,25. **Elegir el brazo de mama cuesta la clase mitótica Y la escala.**
- **¿Y a 0,465?** No hay estudio de sensibilidad, pero **su propia MitEval viene de láminas a 0,12
  y 0,25 re-muestreadas a 0,5**: al lado de eso, nuestro 1,075× no merece discusión.

### El costo: no queda atacado, queda demolido

La 129741 tiene 68,0 mm² de tejido (4799 parches de 256 px a 0,465). A 1,78 s/mm² son **~2 minutos
por lámina**, contra las **3 h 36** que midió Sebastián con HoVer-Net. Las 881 de la cola: **~30 h**
contra ~132 días. **A ese precio el recorte por atención deja de hacer falta para ahorrar tiempo**,
y sobrevive solo como control de falsos positivos.

### El hallazgo de la sesión: al go/no-go del top-20 no le da el denominador

La Hoja 8 proponía correr los pesos sobre «los ~20 parches de mayor atención» y contar cuántas de
las 26 mitosis recupera. **Esa prueba no podía dar un resultado interpretable, y se ve sin correr
nada.** Cruzando `atencion_vs_patologo/percentiles_por_parche.csv` contra los 28 parches con
marcas, sobre los 12 checkpoints:

| Parches de mayor atención | Mediana | Rango |
|---|---:|---|
| lo que captura el **top-20** | **3 de 28** | 0 a 5 |
| para la mitad (14 de 28) | **189** | 120 a 585 |
| para el 80 % (23 de 28) | **508** | 426 a 1147 |
| para las 28 | **1392** | 822 a 2609 |

**No contradice el AUC 0,890.** El percentil mediano de un parche con mitosis es ~96, o sea el
puesto ~190 de 4799; el top-20 es el percentil **99,58**, un punto de operación mucho más exigente
que el que el AUC resume. **El AUC resume todos los umbrales; un top-k es UN umbral, de los
extremos.** También se cae el «ahorro ~240×» (era 4799/20): con top-189 es 25×.

Versión corregida, que es **más barata** que la original: correr la lámina entera (2 min), medir
**recall sobre las 26**, **sin** calcular precisión contra el geojson (los positivos son
**parciales**, así que una detección fuera de las marcas no es un error), y usar la atención como
**variable, no como filtro**. Con HNTiny y TTA, que es el mejor en mitosis en las dos agregaciones.

### Dos cosas laterales que valen

- **La receta de etiquetas de mitosis sin patólogo** (§2.4, A.6, A.7): re-tinte pHH3, registro y
  umbral sobre el canal DAB deconvuelto sobre 48 ROI de 11 WSI, más auto-entrenamiento ST++ para
  el resto de las clases. Es una vía publicada para el cuello exacto que tenemos.
- **Su procedimiento de registro sirve para el hilo trabado de las regiones de escaneo**: ancla
  manual **primero** sobre un núcleo visible en las dos imágenes, después SimpleElastix rígido y no
  rígido sobre **gris submuestreado a 0,5 mpp**, y recién ahí aplicar a resolución completa.

### Lo que NO se hizo

No se bajaron pesos ni se clonó el repo (no autorizado). **No se declara reabierta la rama de
núcleos**: sigue pausada desde el 31-jul y reabrirla es regla 9.b. El go/no-go corregido **es una
propuesta, no una tarea ejecutada**. Y **no sabemos qué salió de la reunión del 14-ago**: todo esto
asume que el encargo sigue vigente.

> **SUPERSEDED el 17-ago** en cuanto a la reunión: ocurrió y HoVer-NeXt se presentó. Ver la entrada
> del 17-ago al final de este archivo.

## 14-ago-2026 (noche) — HoVer-NeXt por dentro: el 17× no está donde parecía

Misión del handoff `handoff_B8_20260814_2030.md`: entender el **mecanismo** de HoVer-NeXt y
explicarlo pedagógicamente. Nada de re-verificar números. Sin GPU, sin descargas.

Entregable: `sprints/B8_sprint8/papers_14_agosto/hovernext_mecanismo.md` (452 líneas), escrito como
**delta contra `hovernet_estudio.md`**, que ya estaba en el repo. Reusa su mini ejemplo de 10
píxeles con una fila más, para que los dos documentos hablen el mismo idioma. Figuras 1 y 5 leídas
del PDF **al principio de la sesión** ([[image-api-qa-limit]]) y descritas en el mismo pase.

### El BCB-map, y lo que la Fig. 5 regala

El BCB (**B**oundary, **C**enter, **B**ackground) le da al watershed sus dos ingredientes ya
hechos: las semillas son los píxeles `centro`, las barreras son los `borde`. HoVer-Net tenía que
fabricárselos con la cadena Sobel → máximo → marcadores → paisaje de energía, cada paso una pasada
a resolución completa con dos umbrales libres. La **Fig. 5 lo muestra literal**: su panel *Model
BCB Output* es rojo de fondo, verde en los núcleos y una franja azul de borde (el código de color
es lectura visual, el epígrafe no lo escribe).

### Los tres hallazgos de mecanismo

1. **El BCB NO es donde vive el 17×.** Cruzando nuestra medición del job 4714 con el paper: el
   post-proceso de HoVer-Net era **1 h 15 de 3 h 36 = ~35 %**, así que borrarlo entero compra
   **~1,5×**. El resto sale de ingeniería (HNTiny, media precisión, salida cuantizada a un byte,
   Zarr/LZ4, escritura en otro proceso, pre-stitching) y de **quitar el convex hull, que se pagó**:
   la distancia de Hausdorff **empeora** contra su propia entrada al CoNiC (neutrófilos 1,966 →
   2,250 en HNLarge), y el paper lo admite en la Discusión.
2. **El BCB tampoco separa mejor.** En PanNuke el **bPQ**<sub>Tiss</sub> da **0,656 (HNTiny) contra
   0,659 (HoVer-Net)**. Separa **igual y más barato**, que es la tesis real de un paper de
   ingeniería de inferencia. El paper ni lo presenta como mejora de calidad: justifica el BCB
   citando resultados en **otras modalidades** (Caicedo 2018). Y hay una tensión que vale nombrar:
   HoVer-Net existía **para no** predecir el contorno como clase, y HoVer-NeXt vuelve a hacerlo.
3. **El pipeline espera una WSI** (la 2ª pregunta del handoff). Su foreground sale del **thumbnail
   de OpenSlide** y el stitcher existe para pegar ROI: con parches sueltos, los dos primeros pasos
   de la Fig. 1A quedan sin uso. Es **fricción de plomería, no de costo**, y además paga un costo
   de **borde** (el paper evalúa Lizard sobre recortes centrales de 248 de 256 «to avoid having to
   detect nuclei with their center outside of the tile»); un parche aislado tiene ese problema en
   todo el perímetro. Refuerza por mecanismo lo que §7 del estudio decía por costo: **correr la
   lámina entera es el modo para el que la herramienta está construida**.

### Una observación nueva, chica

**La ablación C.2 dice menos de lo que §2.2 le hace decir.** El texto justifica quedarse solo con
muestreo («data sampling is already sufficient»), pero en la tabla **la fila ganadora en mAcc y bF1
es la de ponderación sola** (0,766 / 0,846), que es la que descartaron. Las tres configuraciones
que conservan alguna de las dos están dentro de 0,007. Lo único claro es que **sacar las dos duele**
(mF1 0,571 contra ~0,606). Los propios autores lo dicen así en la Discusión («no clear best
configuration»). No cambia ningún veredicto: es nota de mecanismo, no de números.

### Lo que queda abierto

Cuatro preguntas que **solo cierra el código**, que no está autorizado a clonar: si los mapas HV
entran al post-proceso o no (§2.1 dice «auxiliar», §2.3 usa solo el BCB, pero la Fig. 1B los dibuja
juntos apuntando a *Instance map*); de qué lado va el **λ = 0,02** que pesa las dos ramas (un factor
50 en cuál domina el gradiente); si las vistas de TTA se **sortean o se enumeran** (la tabla C.1
lista probabilidades también en test); y si la entrada por tiles sueltos está expuesta.

**Sigue sin respuesta qué salió de la reunión con Sebastián del 14-ago.** Se preguntó al cerrar las
dos sesiones anteriores. Todo el encuadre asume que el encargo sigue vigente.

> **SUPERSEDED el 17-ago**: la reunión ocurrió y HoVer-NeXt se presentó. Ver la entrada de abajo.

## 17-ago-2026 — la reunión del viernes ocurrió, y HoVer-NeXt se presentó

Cierre de la sesión del mecanismo. Lo dijo Ernesto al pedir el cierre, y **cancela el pendiente
efímero que venía arrastrándose tres sesiones** («no sabemos qué salió de la reunión del 14-ago»):

- **La reunión del viernes 14-ago se hizo, y Ernesto presentó HoVer-NeXt.** O sea que el estudio
  factual y la corrección de la Hoja 8 tuvieron audiencia; el trabajo de las dos sesiones del 14-ago
  llegó a destino.
- **Sebastián encargó tareas para esta semana**, después de la reunión.
- **Las conclusiones de la reunión y el contenido de esas tareas NO están en este archivo ni en
  ningún doc del repo.** Ernesto se las pasa directamente a la sesión siguiente. **Nada de lo
  escrito antes del 17-ago debe leerse como si las conociera.**

**Qué implica para el encuadre previo.** Todo el material de HoVer-NeXt (la Hoja 8, el estudio
factual, el doc de mecanismo, el go/no-go corregido) se produjo **asumiendo** que el encargo de
segunda etapa seguía vigente. La reunión ya se pronunció, así que **esa suposición dejó de ser
necesaria y también dejó de ser válida como respaldo**: la dirección la fijan las tareas de
Sebastián, no nuestros documentos. Si las tareas apuntan a otro lado, gana la reunión y el material
de HoVer-NeXt queda como referencia, no como plan.

**Lo que NO se sabe y no se debe suponer**: si las tareas tienen algo que ver con HoVer-NeXt; qué
artefacto exacto se usó para presentarlo (el deck `Papers_Mitosis.pptx` sigue registrado como
terminado y sin audiencia, y **no hay evidencia de que fuera ese**); ni si se autorizó bajar pesos o
clonar el repo. Todo eso lo define lo que Ernesto informe.

**Próxima sesión**: arranca en **modo plan**, y su trabajo es estudiar la forma correcta de elaborar
las tareas de la semana, con las tareas en mano.

## 17-ago-2026 (tarde) — los cuatro encargos de la reunión, traducidos a plan

Sesión de **planificación pura**: cero GPU, cero experimentos, ningún número movido. Ernesto trajo
las tareas que Sebastián dejó el viernes y esta sesión hizo el reconocimiento y escribió el plan.
**Ejecuta una sesión limpia** — plan en
[`sprints/B8_sprint8/hovernext_129741/plan_semana_17ago.md`](../sprints/B8_sprint8/hovernext_129741/plan_semana_17ago.md).

**El encuadre que fijó Sebastián**, y que cambia el criterio de éxito: **quiere HoVer-NeXt aunque
no suba ninguna métrica.** Lo que busca es detección e interpretabilidad que le **proponga zonas al
patólogo** y le acelere el etiquetado — que es el cuello real del proyecto — y que a 17× de su
predecesor sea viable sobre la cohorte. **Se evalúa con las métricas del paper, no con AUC.** Los
cuatro encargos: los tres brazos de mapa de calor sobre la 129741 (HoVer-NeXt solo · CLAM → HN ·
CLAM+Mammoth → HN), los mapas de atención/expertos/slots de CLAM+Mammoth sobre esa misma lámina,
abrir la cadena interna de HoVer-NeXt (HV → BCB → raw class → class-map, idea de Ernesto) y, al
final de todo, más relaciones E×S.

**Tres hallazgos del reconocimiento, ninguno costó GPU:**

- **Hay 12 láminas anotadas por el patólogo, no una.** Viven en
  `/media/administrador/Storage1/sdonoso/anotaciones/` (de `sgaete`, **READ-ONLY**), un directorio
  que **ningún documento del repo mencionaba**. Las 12 tienen features y WSI, y **las 12 traen
  marcas de mitosis**: 94 contra las 26 de la 129741. **Sebastián habló de 30: faltan 18**, y por
  qué es pregunta para él. «Quién es GDT» sigue sin respuesta.
- **El encargo de los mapas de Mammoth sale sin GPU.** La 129741 cae en **test del fold 4** de
  `carcinoma_ductal_insitu_presente_ci_reform`, así que el par CLAM/Mammoth del job 4589 **ya
  existe** sobre esta lámina no vista. En tasa mitótica ese par no existe (la lámina está en train
  en los 5 folds) y construirlo costaría splits nuevos y días de GPU.
- **`sgaete` tiene un pipeline propio** de atención-vs-anotaciones sobre 8 tareas y las 12 láminas,
  que mide lo mismo que nuestro `atencion_vs_patologo/`. **Riesgo de trabajo duplicado**: se
  coordina antes de barrer las 12, no después.

**Dos decisiones de diseño que la sesión ejecutora no debe reinventar**: HoVer-NeXt se corre **una
vez sobre la lámina entera** y los brazos restringidos se hacen **enmascarando post-hoc** (el
pipeline espera una WSI, un parche suelto paga borde perimetral, a ~2 min no hay motivo de costo, y
así los tres brazos quedan pareados por construcción); y **PQ / bPQ / mPQ no son computables** contra
este geojson, porque no es una segmentación exhaustiva y las marcas de mitosis no son contornos
nucleares. Sobreviven el recall de detección y los descriptores de regularidad.

**Autorizaciones y encuadre de reglas.** Ernesto autorizó **clonar `hover_next_inference` y bajar
los dos juegos de pesos** (segundo precedente del workaround E.a). Y la vuelta de la rama de núcleos
al alcance **no es regla 9.b encubierta**: la reunión **redibujó el destino**, que es la única
condición bajo la cual el mapa del sprint deja volver algo de «Fuera de alcance», y vuelve **como
esfuerzo nuevo**. La pausa del 31-jul se apoyaba en el costo (demolido: ~2 min contra 3 h 36) y en
el top-20 (que no tiene denominador, patrón P2).

**Nada se ejecutó.** Los cuatro encargos siguen enteros por delante.

## 17-ago-2026 (tarde/noche) — se EJECUTÓ: fases 0 y 1 cerradas, la GPU quedó sin tocar

Primera sesión ejecutora del plan de la semana
([`plan_semana_17ago.md`](../sprints/B8_sprint8/hovernext_129741/plan_semana_17ago.md)). Se
cerraron las **dos fases que no necesitan GPU**, y se paró en el punto donde el plan manda parar:
antes del primer `sbatch`.

### Fase 1 — interpretabilidad sobre la 129741 (encargo 2). CERRADA

Par **CLAM/Mammoth del job 4589, fold 4 de `carcinoma_ductal_insitu_presente_ci_reform`**, la
única configuración del proyecto con esta lámina **no vista en entrenamiento**. Es la **primera
vez que la interpretabilidad corre sobre una lámina privada** — el B7 fueron 7 TCGA. Todo CPU
post-hoc, cero GPU. Salidas en `results/b8_hovernext_129741/interp/`.

**El resultado, que son dos cosas y hay que leerlas juntas:**

- **La atención cae donde marcó el patólogo, en los dos brazos.** Percentil medio dentro de la
  región anotada: **Mitosis es el grupo más alto de los siete** (CLAM **0,872**, Mammoth
  **0,914**, contra ~0,50 del resto). Reproduce el orden del 1-ago **con checkpoints de otra
  tarea**, así que no era propiedad de los de tasa mitótica.
- **Y los dos igual se equivocan en la lámina**: predicen `no` (CLAM p=0,625, Mammoth p=0,798)
  contra `y_true = si`. Misma firma que el 1-ago, ahora en CDIS.
- **Mammoth ordena mejor el tejido y clasifica peor**: hunde el **tejido adiposo a 0,066**
  mientras CLAM lo deja en **0,572**, y sube Tumor (0,834 vs 0,712). No reabre el Hallazgo 12:
  es interpretabilidad, no métrica.
- Spearman entre las dos atenciones **0,456** y Jaccard top-5 % **0,228** ⇒ **no son el mismo
  mapa**, con lo cual el contraste de brazos de la fase 3 tiene sentido de correrse.
- 30 heatmaps por experto + montage + contact sheet; heatmaps y tablas por **slot** con
  **N_eff = 192,0 de 300**.
- **Sanidad**: las **163/163** marcas casan exactamente con parches del h5 y **todas** caen en la
  región de escaneo de abajo (2303 arriba / 2496 abajo = 4799), que son los números ya
  documentados.

**Tooling**: se parametrizaron `slot_heatmaps_contraste.py` y `build_slot_softmax_tables.py`
(tenían clavadas las 3 láminas TCGA del B7 y su layout). **Los 4 CSV del B7 se reproducen byte a
byte**, así que la parametrización no fue regresiva. Nuevo: `overlay_anotaciones_atencion.py`.

### Fase 0 — HoVer-NeXt instalado y auditado. CERRADA

Repo clonado (HEAD `29134a3`), **4 × 128 MB de pesos** con sha256 (`lizard_convnextv2_tiny` +
los 3 folds de PanNuke, que es como el paper arma su ensemble), env propio bajo containment con
los **17 imports reales** del camino de inferencia. `auditoria_codigo.md` contesta las 6
preguntas. **Tres hallazgos cambian el plan:**

1. **`--keep_raw` es obligatorio**: `main.py:121-126` borra el BCB-map y el raw class al
   terminar, que son el insumo de la fase 2.b.
2. **El «~2 min por lámina» no aplica a esta lámina**: no expone `thumbnail`, así que el filtro
   de fondo **nunca corre** y se teselaría el lienzo entero — **51.192 tiles** (Lizard) y
   **206.382** (PanNuke) ⇒ **el `.slurm` pide horas, no minutos**. La decisión de correr entera
   y enmascarar post-hoc **no cambia**; cambia el presupuesto.
3. **Los mapas HV se descartan en inferencia** ⇒ la figura de la 2.b tiene **tres** paneles, no
   cuatro. No se fabrica el que falta.

Además: el **TTA se sortea y no hay `--seed`** (la corrida **no es reproducible**, al revés que
nuestro pipeline); con los pesos de Lizard **`--metric f1` es la única opción usable**; y **los
tiles sueltos sí están expuestos**, lo que **corrige una de las cuatro razones** de la decisión
de diseño (la decisión se sostiene con las otras tres).

### Lo que cazó el preflight, y es la mejor defensa del workaround G que dio el sprint

**El env nuevo no podía abrir la lámina**: `Bad direction attribute "LEFT"`. Los `.bif` privados
traen `direction=LEFT` y el OpenSlide oficial solo entiende `RIGHT` y `UP`. **No es versión** —
bajar a 4.0.0 stock tampoco anda: hace falta la build **parchada** que ya estaba resuelta en
`clam_environ/openslide_solution.md` y que `clam_latest` usa desde enero **sin que ninguna sesión
se hubiera enterado**. Nuevo **workaround K** + [[openslide-parchado-bif-env-nuevo]].

### Lo que NO se hizo

**Cero GPU.** El `.slurm` (`scripts/run_hovernext_129741.slurm`) y su preflight están **listos y
en verde para los dos juegos de pesos**, y **no se lanzaron**: el plan manda parar antes de
cualquier `sbatch`, y se le preguntó a Ernesto sin respuesta antes del cierre. Quedan enteras las
**fases 2, 3, 4, 5 y 6**. La cola estaba con 4 jobs pendientes de 4 usuarios distintos.

---

## 17-ago-2026 (tarde/noche, 2ª sesión) — se apretó el botón de la fase 2, y arrancó el barrido de registro

Sesión corta y de ejecución: las dos decisiones que el handoff dejaba abiertas se tomaron y se
lanzaron las dos cosas que estaban esperando.

### Fase 2 lanzada — job 4998, y es la PRIMERA GPU de este eje

Ernesto respondió la pregunta de §10 del handoff: **Lizard, TTA = 4**.

```
sbatch --export=ALL,CP=lizard_convnextv2_tiny,TAG=lizard_mitosis,TTA=4 \
       scripts/run_hovernext_129741.slurm
```

**Job 4998, encolado** (`PD (Priority)`) detrás de dos de `nschiaff`; con `sgaete`, `capstone` y
`gvenegas` corriendo y la GPU en 43,7/49 GB. Entró **al final de la cola**, sin monopolizar.
`METRIC=f1` (obligatorio con Lizard), `BATCH=32`, `--keep_raw`, salida a
`results/b8_hovernext_129741/hovernext/lizard_mitosis/`. **Disco antes: 2,5 TB libres de 15 T**
(el plan pide el delta que dejan los zarr crudos). **Al cierre seguía encolado: no hay ningún
número de HoVer-NeXt todavía.**

### Barrido de registro multi-región — corriendo desatado

El pendiente más viejo del hilo de regiones de escaneo. Driver nuevo
`scripts/barrido_registro_multiregion.sh`: invoca `auditar_regiones_escaneo.py registro` lámina
por lámina, **reanudable por el JSON final** y **desatado con `setsid` (ppid = 1 verificado)**,
así que sobrevive al cierre de la sesión (workaround J). **No toca el script auditado** — lo
llama por CLI y muda su salida a `barrido_138/`, con lo que el resultado de la 129741 sigue
siendo reproducible byte a byte.

**129 láminas en lista** (las 130 de 2 regiones menos la 129741). Las **9 de 3 y 4 regiones
quedan fuera por construcción del test**, que compara un par.

**Lo medido con 3 láminas, y las dos lecciones están en el ADDENDUM §7 de
`regiones_escaneo/resultados.md`:**

1. **El test rechaza láminas por sus parámetros, no por la geometría.** 2 de 3 se pararon por
   falta de ventanas utilizables — incluida la **119414, con silueta 0.9993 y CERO ventanas**.
   La razón de áreas mediana de las 130 es 0,952, así que no es tamaño de región: son
   `--min-tejido 0.5` y la exclusión de bordes con `--margen-a 2048`, calibradas sobre una
   lámina rica en tejido. **El rendimiento del barrido se lee como «cuántas pudo medir».**
2. **La 129741 no es representativa.** La 120063 corrió entera y da **3,3 sd** de separación
   (4/8 ventanas) contra las **29,5 sd** (8/8) de la 129741, con **7 % de escala** y **732 µm**
   de residuo en el ajuste rígido. Es el perfil que el criterio pre-fijado asocia a **secciones
   seriadas** — **pero no es veredicto**: su segundo pico está pegado al primero, o sea que la
   etapa A no localiza, y eso es indistinguible de «el tejido es distinto».

Se subió el barrido de rotación a **±8°** (default 1,5; la corrida del 14-ago usó 4,0 y saturó).
La 120063 **igual satura, pero en los dos extremos a la vez**, que ya no se lee como rango corto.

### Lo que NO se hizo

- **Cero resultado de HoVer-NeXt**: el job quedó encolado. Fases 2.b, 2.c, 3, 4, 5 y 6 enteras.
- **El barrido no terminó**: 3 de 129 al cierre. Sigue corriendo desatado.
- **No se tocaron los parámetros de selección de ventanas** pese al hallazgo 1. El barrido corre
  con los defaults, a propósito: primero saber cuántas rechaza, después decidir si se relaja.

---

## 17-ago-2026 (tarde, 3ª sesión) — la GPU está bloqueada por la cola, y la fase 3 se acotó sin ella

Sesión de diagnóstico y de trabajo lateral: **no había nada que cosechar** (los dos procesos del
handoff seguían en vuelo), pero mirar por qué destapó un bloqueo que ninguna sesión había visto.

### El 4998 no espera su turno: está bloqueado por cómo está declarada la cola

`squeue` decía `PD (Priority)` y eso parecía una espera normal. `scontrol` dice otra cosa:

- El nodo tiene **un solo token de GPU** (`Gres=gpu:1`) y lo tiene **4996** (`gvenegas`, un
  `VLLM::EngineCore` con 38 GB de VRAM) declarado a **365 días**.
- Delante nuestro hay **4993 y 4997** (`nschiaffino`), los dos pidiendo GPU y los dos
  **`TimeLimit = UNLIMITED`**.
- Memoria: **208 de 230 GB asignados**, 17 GB libres; nosotros pedimos 96 GB.

**Consecuencia que importa: achicar nuestro job NO nos adelanta.** El backfill necesita saber
cuándo terminan los de más prioridad para colar uno chico, y con `UNLIMITED` delante esa ventana
no se puede calcular. Por eso la estimación de SLURM es `StartTime = 2027-08-17`, que es lo que
devuelve cuando **no puede planificar** — no es una predicción de un año de espera.

Ernesto decidió **coordinar y dejarlo encolado**. Queda
`sprints/B8_sprint8/hovernext_129741/coordinacion_gpu.md` con el snapshot, quién tiene qué, y el
pedido concreto: no que nadie cancele, sino **que 4993/4997 declaren un `--time` real** (con eso
el backfill vuelve a funcionar para todos) y saber si el vLLM de 4996 es una validación de horas
o un servicio permanente. Con la contraoferta de bajar nuestro propio `--mem` de 96 G si la fila
no avanza.

### El techo del filtro de atención — la mitad de la fase 3 no necesitaba la GPU

El hallazgo de la sesión. **Un parche que no entra en la máscara top-K no lo recupera nadie**, por
bueno que sea el detector ⇒ la atención sola ya **acota por arriba** el recall de los brazos 2 y 3:

```
recall_fase3(K)  ≤  min( techo_atencion(K) , detección_de_HoVer-NeXt )
```

Es el **patrón P2** aplicado *antes* de gastar GPU en vez de después. Medido sobre la región
anotada (2496 parches, 35,37 mm²), con el par CLAM/Mammoth del fold 4 del 4589:

- **El techo NO condena la fase 3.** A **4,25 mm² (12 % de la región)** ya son **19/28** en CLAM y
  **22/28** en Mammoth, con enriquecimiento **5,7× y 6,5×** sobre el azar. La pregunta de Sebastián
  (proponer un área chica que igual contenga las mitosis) **tiene margen**; falta medir cuánto se
  come la detección.
- **Mammoth ordena mejor**: llega a **28/28 en K = 750** y CLAM no llega hasta barrer todo. Es
  ≥ CLAM en **9 de los 11 K**, con **K = 50 la única inversión clara** (6 vs 4). **No reabre el
  Hallazgo 12** — es orden de parches, no métrica de lámina, y los dos siguen fallando la lámina.
- **El top-20 vuelve a dar 2-3 de 28**, ahora con checkpoints **de otra tarea** ⇒ corrobora
  [[topk-percentil-no-auc]] de forma independiente.
- **Chequeo de sanidad de la fase 3 ya aprobado a nivel de techo**: en K = 2496 los dos brazos dan
  **idéntico** (28/28), que es justo lo que el plan exige verificar.

Entregables: `scripts/techo_atencion_topk.py`, `sprints/B8_sprint8/hovernext_129741/techo_atencion.md`,
`results/b8_hovernext_129741/techo_atencion/`.

### Dos pendientes del handoff cerrados

1. **El brazo PanNuke ya se puede lanzar.** El choque era que `--export` de SLURM separa por comas
   y `--cp` de HoVer-NeXt *espera* comas para promediar el ensemble de 3 folds. Ahora se pasa con
   `+` y el `.slurm` traduce. Es **idempotente**, así que el 4998 encolado no se ve afectado.
   Preflight sobre los 3 folds: **OK**.
2. **La atención por parche ya queda persistida.** La fase 1 solo había guardado los PNG, y la
   fase 3 la necesita. Se agregó `--dump-attention` a `clam_vs_mammoth_attention.py` como cambio
   **aditivo**: los 4 artefactos previos se regeneran con **md5 idéntico**.

### Lo que NO se hizo

- **Sigue sin haber un solo número de HoVer-NeXt.** El 4998 nunca arrancó. Fases 2.a, 2.b, 2.c
  enteras, y de la 3 solo está el techo (falta el brazo 1, que es el que exige GPU).
- **El barrido no terminó**: al cierre **11 ok / 3 stop / 115 pendientes**, ETA ~3,7 h. Sigue vivo
  y desatado (`ppid = 1`). Tasa de rechazo hasta acá **21 %**, más benigna de lo que se temía.
- **`barrido_138/` sigue sin commitear**, a propósito, por lo mismo del handoff anterior.
- No se re-midió el veredicto de la 129741 ni se tocaron los parámetros del test de registro.

## 17-ago-2026 (noche, 4ª sesión) — se cosecharon los dos procesos: uno falló rápido, el otro cerró

**Estado de entrada**: el 4998 llevaba 41 min en `PD (Priority)` y el barrido de registro iba por
la lámina 14 de 129. Los dos se resolvieron durante la sesión.

**1. El 4998 corrió, y falló en 29 s por plomería.** Arrancó a las 18:00 (o sea la cola se destrabó
sola, sin que hiciera falta el pedido de coordinación) y murió con
`NotImplementedError: Only *.svs, *.tif, *.czi, and *.mrxs files supported`. HoVer-NeXt valida la
**extensión del nombre** (`data_utils.py:234-242`) antes de abrir nada, y todo lo que viene después
pasa por OpenSlide, que detecta el formato **leyendo el archivo**. El gate es cosmético para un
`.bif`, que es TIFF por dentro.

- **Fix sin tocar el repo de referencia**: symlink `.tif` en `clam_testing2/wsi_shim/`. Verificado
  que OpenSlide sigue eligiendo el driver `ventana` con dims, mpp, niveles y `associated` idénticos:
  **no** cae a `generic-tiff`, que era el modo de falla que perdería el mpp.
- **El preflight ahora chequea la extensión** (probado en las dos direcciones). Queda como
  **workaround M** de `CLAUDE.md`.
- **La fase 2 está lista para relanzarse**, pero **no se lanzó**: el handoff manda parar antes de
  cualquier `sbatch` nuevo, y además `5000` (gvenegas) está `PD (Resources)`.
- Dato del plan, ya registrado: la lámina **no expone `thumbnail`** ⇒ no se filtra fondo y se tesela
  el lienzo entero. Decenas de minutos, no los ~2 min del paper.

**2. El barrido terminó**: 198 min, **108 con JSON, 21 rechazadas, 0 fallos** (rechazo final 16 %,
no el 35 % que se veía a media corrida). Agregado con `scripts/cosechar_barrido_registro.py`.

- **La mitad no es interpretable**: en **54 de 108** la etapa A no localiza (pico no único). Esas
  **no son «seriadas», son no medibles**.
- Entre las 54 medibles: **33 perfil de re-escaneo** (razón señal/control 5,20, escala 0,9996,
  residuo rígido 62 µm), 20 ambiguo, **1 seriada**, y el 1 aguanta los tres cortes de sensibilidad.
- **Se corrigen dos lecturas**: la **120063 no es evidencia de seriadas** (falla la puerta con 1 de
  8 ventanas), y la **129741 sí es representativa** entre las medibles (percentil 91 / 89 / 57).
- Denominador honesto: **33 de 54 medibles**, nunca de 490.

**3. Fase 1 paso 6 cerrada** (estaba marcada opcional): AUC de ranking del par CLAM/Mammoth del
fold 4, `scripts/auc_atencion_fold4.py`. Mitosis **0,876 (CLAM) y 0,918 (Mammoth)**, con el 0,890 de
Sebastián entre los dos y llegando desde **otra tarea**, lo que lo corrobora de forma independiente.
Sobrevive el nulo por traslación (p 0,012 y 0,0008); **Tumor no lo sobrevive** pese a su AUC alto.
Los dos brazos **clasifican mal la lámina** y aun así ordenan las mitosis en el percentil 93-95.

**Commits**: `17168d1`, `f9d065b`, `71990a2` en `main`.

## 17-ago-2026 (noche, 5ª sesión) — se explicó la mitad no medible, y quedó un probe a medio correr

Sesión corta. El pendiente que §8.d dejaba abierto («el 50 % no medible no está explicado») se
atacó con dos piezas: **una cerró, la otra quedó corriendo**.

### 1. El fallo NO son los parámetros, y eso cierra una decisión pendiente

`scripts/diagnostico_no_medibles.py` recupera el detalle **por ventana** que el CSV agregado había
perdido y separa dos modos opuestos: **ambiguo** (hay pico pero hay varios ⇒ lo arreglarían los
parámetros) y **sin señal** (no hay pico ⇒ no lo arreglan). El estadístico ya estaba en cada JSON:
`sd_sobre_fondo`, independiente del NCC absoluto.

**De 388 ventanas que no localizan, 381 (98 %) no tienen pico** y solo 7 son ambiguas. **Las 54
láminas no medibles caen las 54 en modo sin señal**, sin correlación con densidad de tejido ni con
el número de ventanas.

⇒ **Relajar `--min-tejido` o `--margen-a` no las recupera.** La decisión que §7.a y los dos
handoffs anteriores arrastraban como pendiente («¿re-corremos las rechazadas con parámetros
relajados?») **queda contestada que no, por evidencia**.

### 2. Queda una causa de MÉTODO nuestro, y el probe se cortó antes de poder leerlo

`_buscar_local` (`auditar_regiones_escaneo.py:462`) busca **solo traslación**; la rotación entra
recién en la etapa B. Dos regiones giradas entre sí dan mapa plano aunque las células sean las
mismas: sería limitación nuestra, no un hecho del tejido.

`scripts/probe_rotacion_etapaA.py` barre θ dentro de la etapa A sobre 16 láminas en 3 grupos
(A = no medible con silueta ≥0.95, B = no medible con silueta <0.95, **C = control positivo**),
con pre-registro escrito antes de correr.

**Al cierre iba por 3 de 16, todas del grupo A y ninguna del C.** Las dos leídas recuperan casi
todas sus ventanas al barrer θ y **duplican** el NCC (128696: 0.25 → 1.00, θ\* +7.0° con sd 0.9;
135924: 0.12 → 0.88, θ\* −10.5° con sd **3.7**).

**La señal es fuerte y aun así no se lee**, por dos razones que están en su propio pre-registro:
**sin el grupo C el probe no está validado**, y un θ disperso entre ventanas (la 135924) cuenta
como **ruido**, no como rotación. **Si la rotación resulta ser la causa, el «33 de 54 medibles»
de §8.b hay que recontarlo.** Detalle en `regiones_escaneo/resultados.md` §9.

### Gotcha operativo de esta sesión

**El probe de la sesión anterior seguía vivo al retomar** ([[proceso-viejo-vivo-tras-interrumpir]])
y el `grep` de preflight no lo cubría (buscaba `barrido_registro|auditar_regiones`, no
`probe_rotacion`). Se relanzó uno nuevo y hubo **dos procesos escribiendo el mismo JSON** durante
~6 s. Se mató el nuevo, que no había alcanzado a escribir; el viejo siguió sano. **Lección: el
preflight tiene que grepear por el directorio del repo, no por nombres de script sueltos.**

### Lo que NO se hizo

- **La fase 2 no se relanzó desde esta sesión**: el job **5008** ya estaba encolado al entrar.
- **El probe no terminó**: 3 de 16, sin control positivo. Sigue corriendo desatado.
- **No se re-midió la 129741** ni se tocó el conteo de §8.b.

## 17-ago-2026 (noche, 6ª sesión) — la fase 2 se relanzó, y el probe quedó a un paso de poder leerse

Sesión corta y de dos frentes. **Ninguno de los dos cerró**, y los dos quedaron en un estado
limpio para retomar.

### El job 5008: la fase 2 está encolada, y el bloqueo es el mismo de siempre

Ernesto **autorizó el `sbatch`** sabiendo que quedaba detrás de la cola. Se mandó **solo
Lizard-Mitosis** (el juego de pesos que trae la clase de mitosis, o sea el que alimenta 2.b, 2.c
y la fase 3); PanNuke se manda después, para no ocupar dos lugares con gente esperando.

El diagnóstico de la cola, hecho antes de mandar y que conviene repetir la próxima vez:

- **`5001`** (`sgaete`, `yolo_train`) tiene la GPU y declara **`TimeLimit` real de 2 días** ⇒
  SLURM sí puede planificar detrás suyo. Termina el **19-ago 19:33**.
- **`5000`** (`gvenegas`) está `PD (Resources)` con **`TimeLimit = UNLIMITED`**, y va **delante**
  nuestro. Es otra vez el **workaround L**: en cuanto arranque, no hay ventana de backfill que
  calcular para nosotros.
- `scontrol` nos da `StartTime = 19-ago 19:33`, **igual que a 5000**. Eso es la primera
  disponibilidad del recurso, **no** una predicción que descuente lo que 5000 vaya a durar.

Apareció además **`5011`** (`extra`, de `Test_D/D_abs_cambiado/`) bajo la **cuenta compartida
`sdonoso`**: trabajo ajeno, encolado después del nuestro, **no nos bloquea**. Recordatorio de que
`squeue -u $USER` mezcla operadores distintos en este server.

### El probe de rotación: sigue vivo y NO se leyó

Al cierre iba por **11 de 16**: el grupo A entero (8), tres del B, y **cero del control C**. Su
propio pre-registro prohíbe leerlo sin el control, así que **no se leyó**, y esta entrada tampoco
adelanta veredicto. Queda `scripts/cosechar_probe_rotacion.py`, que **se niega a imprimir el
grupo A si el C no valida**.

Lo que sí se pudo cerrar sin tocar el probe son **dos corroboraciones independientes**, que están
en el nuevo **§9.d** de `regiones_escaneo/resultados.md`:

1. **El argmax de la etapa A en las no medibles es indistinguible de ruido**: la dispersión del
   desplazamiento entre ventanas de la misma lámina es **1462 px** contra los **1672 px** que
   daría un argmax uniforme sobre el cuadrado de ±2048. En las medibles es **564 px**. Confirma
   §9.a por otra vía: no es señal débil, es que no hay señal.
2. **La etapa B queda clavada en el borde de su barrido de ±8° tres veces más seguido** en las no
   medibles (22 % de ventanas contra 7 %), con sd de θ intra-lámina 5,08° contra 2,42°.
   **Sugerente y no decisivo**: en una lámina no medible la etapa B busca donde la etapa A eligió
   mal, así que su θ también es ruido.

Se documentaron además dos cosas que la cosecha necesita saber: el probe elige θ por **máximo
NCC** y no por máximo margen (por eso una lámina puede **bajar** su fracción al rotar, y no es un
bug), y el corte de «θ consistente» (sd ≤ 4°) es **posterior a ver los datos**, así que se reporta
como tal y con sensibilidad, no como pre-registrado.

### Lo que NO se hizo

- **El probe no terminó** y **no se leyó**. Falta 1 de B y **los 4 del control C**.
- **Cero números de HoVer-NeXt**: el 5008 nunca arrancó. Fases 2.a a 6 enteras.
- **No se recontó §8.b**: depende del veredicto del probe.
- No se re-midió la 129741 ni se tocó nada del hilo de las multi-región.

## 17-ago-2026 (noche, 6ª sesión) — el probe cerró: la mitad de las no medibles era ROTACIÓN nuestra

Sesión de cosecha. Entró con el probe corriendo (8 de 16) y el 5008 encolado; sale con el probe
leído, el veredicto escrito y §8.b marcado como provisional.

### El control positivo pasó, así que el probe se pudo leer

Se respetó el orden del pre-registro: **primero el grupo C**. Las 4 láminas medibles siguen
localizando a θ = 0 (fracción media 0,76) ⇒ el probe reproduce el barrido y la condición de
lectura está cumplida.

**El control resultó hacer un segundo trabajo que no estaba previsto: calibrar el criterio.** El
cosechador venía con `sd ≤ 4°` medido sobre **todas** las ventanas, y con ese corte **3 de las 4
láminas del control quedan rechazadas** — láminas que localizan perfectamente. La causa: θ* se
elige por máximo de NCC y, en una ventana que no localiza, la superficie en θ es plana y su argmax
vaga, inflando la sd de la lámina entera. Medida **solo sobre las ventanas que localizan**, las 4
del control pasan y el peor da 2,2°, que es el corte adoptado.

### Seis de doce se recuperan, y la mitad de esas con firma de cuerpo rígido

| veredicto | láminas |
|---|---:|
| recuperada por rotación (θ consistente, sd ≤ 2,2°) | **3** |
| recuperada, θ no consistente | **3** |
| no recuperada | 5 |
| indeterminada (θ clavado en el borde del ±20°) | 1 |

El **|θ*| mediano de las que cruzan es 7,8°**: las rotaciones que hacían falta estaban **fuera de
rango por diseño** (la etapa B barre ±8° y su default es ±1,5°). Las tres limpias son 128696
(0,25 → 1,00 con θ* +7,0°, sd 0,9), 135924 (0,12 → 0,88, −10,5°, sd 2,1) y 145819 (0,33 → 0,83,
+8,5°, sd 1,6).

**Sensibilidad, que §9.d exigía**: el **6 de 12 no depende del corte** (cruzar el umbral es
cuestión de `frac_localiza`, no de θ), y el reparto 3/3 es estable en todo el rango donde el
control pasa entero (2,2° a 4,0°), con un hueco natural de 2,5× en los datos.

**Dato inesperado**: barrer θ sube el NCC **también en el control** (0,277 → 0,400, |θ*| mediano
3,8°) ⇒ hay rotación entre las dos regiones **también en las medibles**; la etapa A la venía
**tolerando**, no evitando.

### Consecuencia real: §8.b queda provisional, y eso es trabajo

Extrapolar 6/12 a las 54 da **~27 láminas recuperables, IC95 [11, 43]** (Clopper-Pearson): el pool
de medibles pasaría de 54 a **~81 [65, 97]**. Y **no se sabe cómo clasifican las recuperadas**,
porque el perfil sale de la etapa B y sobre ellas no corrió. Entonces el denominador de §8.b está
subestimado, el numerador (33) es un piso, y **la proporción 61 % no se puede proyectar**.
Cerrarlo exige **re-correr el test con rotación en la etapa A**, no reinterpretarlo.

Entregables: `scripts/cosechar_probe_rotacion.py` (fusiona el cosechador de `e05bb1a` con la
calibración contra el control), `regiones_escaneo/probe_rotacion_veredicto.csv`, y §10 completo de
`regiones_escaneo/resultados.md`.

### Lo que NO se hizo

- **Cero números de HoVer-NeXt.** El **5008 sigue `PD (Priority)`** con `StartTime = 19-ago 19:33`,
  que es cuando termina el `yolo_train` de sgaete — pero delante va el **5000 de gvenegas con
  `TimeLimit = UNLIMITED`**, así que ese StartTime es **cota inferior** (workaround L.b). Fases
  2.a a 6 enteras.
- **No se re-corrió el barrido con rotación**: es la consecuencia de §10.c y es una decisión de
  alcance, no un ajuste.
- No se re-midió la 129741 ni se tocó el hilo de las multi-región sobre training.
- Nota del árbol compartido: los jobs **5011/5013/5015 NO son nuestros** pese a figurar como
  `sdonoso` (`WorkDir = Test_D/D_abs_cambiado`). Solo el 5008 lo es.

**Cierre de la 6ª sesión — la rotación quedó implementada y el re-barrido corriendo.**
Ernesto autorizó re-correr **las 108** (no solo las 54) con rotación en la etapa A: el control
mostró que las medibles también tienen rotación sin corregir, así que medirlas con dos métodos
distintos dejaría dos cohortes incomparables.

- `--rot-a-max` es **opt-in, default 0.0 = apagado**. **Regresión verificada**: con el flag
  apagado la 148781 re-corrida reproduce su JSON de `barrido_138` **idéntico** (silueta, etapa_a,
  ajuste rígido y etapa_b), salvo las dos claves nuevas neutras ⇒ `barrido_138` sigue siendo
  reproducible byte a byte.
- Barrido **grueso-a-fino** (2° sobre ±20°, después 0,5° alrededor del ganador) para no pagar 41
  evaluaciones por ventana.
- **Corriendo desatado**: `OUT_DIR=barrido_rot ROT_A_MAX=20.0 SALTAR_129741=0`, **130 láminas**
  (esta vez **incluye la 129741**, cuyo barrido de rotación saturaba), `ppid = 1`, reanudable por
  el JSON final. Log en `logs/barrido_rotacion_desatado.log`. **No pisa `barrido_138`.**
- Lección de plomería registrada como **patrón P3** de `CLAUDE.md` +
  [[control-positivo-calibra-el-criterio]].

---

## 18-ago-2026 (7ª sesión) — el instrumento del recuento, listo y probado

**La misión (cosechar el re-barrido) estaba bloqueada:** al abrir la sesión el barrido llevaba
**20 min de 6,5 h** (8 láminas de 130, 296 s/lámina). Y el **5008 sigue `PD`**: delante van el
`yolo_train` de sgaete (termina 19-ago 19:33) **y** el 5000 de gvenegas con `TimeLimit =
UNLIMITED`, así que su `StartTime` sigue siendo **cota inferior** (workaround L.b) — sin cambios.

En vez de esperar, se dejó **listo y ejercitado** todo el camino de la cosecha, que es donde la
sesión anterior perdió una corrida entera por un `UnboundLocalError` en código no probado.

### Lo que se hizo

- **`cosechar_barrido_registro.py` blindado.** Escribía **siempre** en `barrido_resumen.csv`, así
  que cosechar `barrido_rot` habría **pisado la verdad de campo** del barrido sin rotación — que es
  justo la referencia de la comparación pareada. Ahora el destino se deriva del directorio y ese
  archivo está protegido **incluso contra un destino explícito** (`--force` para pisarlo). *(El
  guard se agregó porque en la prueba lo pisé yo: se restauró desde git y se verificó idéntico.)*
  **Regresión: sobre `barrido_138` reproduce `barrido_resumen.csv` celda a celda.**
- **El bloque de la 129741** usaba su JSON externo, que en un barrido que **sí** la incluye queda
  stale; ahora prefiere la medición de adentro, excluye a la lámina de su propio percentil y
  reporta el delta contra la medición previa.
- **`scripts/comparar_barridos_rotacion.py` nuevo** — es el recuento de §8.b: matriz de transición
  de la puerta, **cómo clasifican las recuperadas** (lo que §10.c dejó abierto), delta contra el
  33/54, sensibilidad a los cortes, y el diagnóstico de **si la etapa B es el próximo cuello**.
  Probado end-to-end sobre el parcial, y sobre un caso sintético con la 129741 adentro.
- **Dos trampas del recuento, documentadas en `regiones_escaneo/resultados.md` §11**: el control
  negativo que manda la razón a 1e8 (§11.a) y la etapa B que puede **fabricar «seriadas»** con las
  recuperadas (§11.b). Las dos con guard en el script.
- **§8 corregido**: decía **19** `stop` copiando el contador del driver; en disco hay **21** (2
  heredadas de una corrida previa, contadas como `saltadas`). Cobertura real **108 + 21 = 129**,
  completa — el «2 pendientes» del log no eran pendientes. **Las 108 medidas no se mueven.**

### Lo que NO se hizo

- **El recuento de §8.b sigue sin rehacerse**: el re-barrido no terminó. Los números del parcial
  **no se leen** (8 láminas, las primeras alfabéticamente).
- **Cero números de HoVer-NeXt**, sin cambios respecto de ayer.

---

## 18-ago-2026 (8ª sesión) — el deck del 6-ago se extendió con doce láminas

Sesión de **construcción de entregable**, no de análisis: la reunión con Sebastián es mañana
19-ago y el re-barrido no cierra a tiempo. **Ningún número se movió** y **ningún resultado se
leyó del parcial**.

### La decisión que abría la sesión, tomada por Ernesto

El handoff dejaba una sola pregunta de verdad abierta: **extender el deck del 6-ago o hacer uno
nuevo**. Ernesto eligió **extender**, con el material nuevo **al final y en orden cronológico**,
y con **tres hilos de cuatro**: regiones de escaneo, HoVer-NeXt y metodología. **Los papers de
mitosis quedan afuera** (el `Papers_Mitosis.pptx` sigue sin estrenar). El bloque del 6-ago **no se
tocó**: ni una lámina, ni un número, ni una nota.

### Las doce láminas nuevas, 15 a 26

| # | Lámina | Hilo |
|---|---|---|
| 15 | Lo que se hizo desde el 6 de agosto | mapa del bloque |
| 16 | Dos regiones de escaneo dentro del mismo archivo | regiones |
| 17 | Cómo se mide si son la misma lámina | |
| 18 | El primer resultado: la mitad no es medible | |
| 19 | Entre las medibles, 33 de 54 | |
| 20 | Faltaba buscar giro, y estaba fuera de rango por diseño | |
| 21 | El recuento se está rehaciendo, y trae dos trampas | |
| 22 | HoVer-NeXt: instalado, auditado y sin números todavía | HoVer-NeXt |
| 23 | El techo de la prueba, medido sin gastar GPU | |
| 24 | La GPU: un pedido de coordinación | |
| 25 | Tres patrones nuevos en dos semanas | método |
| 26 | Qué sigue | cierre |

**Todo el contenido sale de documentos ya escritos** (`regiones_escaneo/resultados.md` §3, §8,
§10, §11; `techo_atencion.md`; `coordinacion_gpu.md`; `plan_semana_17ago.md`) y las constantes
están al lado de las láminas con la sección de la que vienen. **Se respetaron las tres
prohibiciones del handoff**: el 33 va siempre sobre 54 medibles y nunca sobre 490, no aparece un
solo número de HoVer-NeXt, y ninguna lámina afirma que las recuperadas sean re-escaneos.

### Tres helpers nativos nuevos

`barra_reparto` (un total repartido en tramos proporcionales), `eje_angulos` (el giro sobre su
recorrido, con lo que el método barría y lo que hacía falta) y `curva_techo` (recall alcanzable
contra el tamaño de la máscara, tres curvas superpuestas). Los tres con la gramática del
template, **ningún gráfico como PNG**.

### Assets: dos imágenes que son fotografía de resultado, no diagrama

`prep_assets_regiones.py` recorta las dos regiones de la 129741 (banda negra de 59 px, **la misma
en las dos**, así que la correspondencia se conserva) y saca de **git** la figura de registro a
resolución completa, porque el re-barrido en curso movió la del árbol a su subdirectorio. **Las
dos regiones se dibujan al mismo ALTO y no al mismo ancho**: están al mismo downsample, así que a
igual alto quedan a igual escala y la comparación que la lámina propone es legítima.

### Lo que la 129741 dio al re-medirse, y por qué NO se leyó

El driver ya la procesó (15:17) y su JSON está en `barrido_rot/`. **No se miró como resultado**:
§11.c dice que los números del parcial no se leen, y la 129741 está en ese parcial. De paso queda
explicado un ruido de `git status` que parecía anomalía: los dos archivos que figuran como
borrados **los movió el propio driver** a `barrido_rot/` (`barrido_registro_multiregion.sh:104`).
No hay pérdida y no hay que restaurarlos.

### Lo que NO se hizo

- **Las doce láminas nuevas no tienen guion.** Cero `notes()`. Es el pendiente más grande.
- **Cuatro colisiones de la barra de remate** y dos defectos de figura, todos cazados por el
  rasterizado y **ninguno por la auditoría automática**, que dio «sin avisos» en las 26.
- **El re-barrido sigue corriendo** y **§8.b sigue sin recontar**.
- Cero GPU, cero `sbatch`, cero cambios a los dos scripts que el driver relee.

---

## 18-ago-2026 (9ª sesión) — los siete defectos del deck, y el chequeo que faltaba

Sesión corta y de una sola cosa: **arreglar los defectos visuales del bloque nuevo del deck**.
El guion de las doce láminas **sigue sin escribirse**, que es el pendiente grande.

### Los seis defectos, arreglados, y un séptimo que apareció

Los seis que la sesión anterior había dejado listados en el README están arreglados
(`presentacion_b8/README.md` §«Los siete defectos»): las cuatro colisiones de la barra de remate
(17, 18, 23, 26), los rótulos pisados del eje de ángulos (20), las dos curvas del mismo color
(23), el «dos de ellos» que fue uno (15), el denominador ausente (19) y las etapas sin rotular
(17). El deck sigue en **26 láminas** y construye con la auditoría en cero.

**El séptimo lo encontró el chequeo nuevo, no el ojo**: en la lámina 24 el tercer panel de la
columna derecha también cruza la barra. Había pasado el QA visual completo de la sesión anterior.
Cruza porque `panel()` **crece** para que entre su texto, así que el número no está escrito en
ninguna constante del generador.

### El chequeo de la barra de remate, que el ADDENDUM de la mañana pedía

`auditar` ahora marca cualquier shape que cruce la barra. Construirlo tuvo tres trampas, y las
tres dan un chequeo que parece andar: la `t` con la que se dibuja **no es** donde la barra queda
(`reflow_onco` reancla después, y el `4,85` termina en `4,82` o `4,49`), la barra **se marca a sí
misma** si se la excluye por posición en vez de por identidad, y **una caja de texto no se ve, se
ve el texto** (medir la caja marcaba captions de una línea en láminas del 6-ago que estaban
perfectas). Detalle en [[deck-qa-puntos-ciegos-chequeo]], ADDENDUM del 18-ago noche.

De paso, un defecto que **ningún chequeo de cajas puede ver**: en `eje_angulos` las dos bandas
nacen en cero y se pintaban en el orden declarado, así que la ancha cubría entera a la chica, que
es la que carga el hallazgo. Se pintan de la más grande a la más chica.

### Lo que NO se hizo

- **El guion de las doce láminas nuevas: sigue en cero.** Sin `@humanizer-es` y sin lectura en
  voz alta.
- **Las ocho láminas tocadas no se volvieron a mirar.** La auditoría da cero, que es exactamente
  lo que daba con los seis defectos adentro. El rasterizado quedó sin correr.
- **La copia sin notas**, sin regenerar.
- **El re-barrido sigue corriendo** (80 ok / 19 stop / 31 pendientes a las 19:15, ETA ~21:00) y
  **§8.b sigue sin recontar**.
- Cero GPU, cero `sbatch`, cero cambios a los dos scripts que el driver relee.

---

## 18-ago-2026 (10ª sesión) — sesión de PLAN: el guion de las doce, especificado y sin escribir

Sesión **en modo plan, sin ejecutar nada del deck**. Ernesto pidió explícitamente que el plan lo
levante una **sesión limpia**, porque el paso que abre necesita el presupuesto de lecturas de
imagen entero ([[image-api-qa-limit]]). El plan quedó en
`~/.claude/plans/handoffs-handoff-b8-20260818-1920-md-hazy-dijkstra.md`.

### Las dos decisiones que tomó Ernesto sobre el plan

- **QA visual: medir primero, mirar después.** Rasterizar con `FONTCONFIG_FILE` puesto, correr la
  medición de tinta por renglón sobre las ocho láminas tocadas **sin gastar lecturas de imagen**,
  y recién entonces mirarlas. El rasterizado, que él había rechazado en la sesión anterior, queda
  autorizado en ese orden.
- **La portada NO se toca.** La regla «ni una nota del bloque del 6-ago» queda entera; la costura
  la resuelve **la nota de la lámina 15**, que hace el pivote.

### Dos precisiones de contenido que salieron al leer las fuentes

Las dos son de la lámina 22, que es nueva y por lo tanto se puede tocar:

1. **`0,872` y `0,914` no son AUC, son el percentil medio de atención.** Lo dice explícito
   `hovernext_129741/auc_ranking_fold4.md:88` («no es el AUC, aunque los valores queden cerca»);
   los AUC de mitosis de ese par son **0,876** y **0,918**. La lámina proyecta los dos números
   **sin nombrarlos**, al lado de una sección que habla de ranking de atención: se les agrega
   «percentil medio», y el guion no los llama AUC.
2. **«los cuatro juegos de pesos» es correcto pero se lee raro.** En disco hay
   `lizard_convnextv2_tiny` más `pannuke_convnextv2_tiny_{1,2,3}`: **un modelo con clase de
   mitosis y tres del otro, que se promedian**. El guion lo dice así.

### La fila de la GPU rotó entera desde el snapshot del 17-ago

Verificado a las 19:44 y anotado como ADDENDUM en `hovernext_129741/coordinacion_gpu.md`. Importa
porque la lámina 24 pide una coordinación concreta y **los destinatarios cambiaron**: el servidor
de inferencia declarado a 365 días ya no tiene la GPU, la tiene ahora un entrenamiento con
**tope declarado**, y aparecieron **tres trabajos más pidiendo GPU desde la cuenta compartida**
que no son nuestros. Nuestro 5008 sigue `PD (Priority)` y **no va a correr antes de la reunión**.

### Lo que NO se hizo

- **El guion de las doce láminas nuevas: sigue en cero.** Es el pendiente grande y está
  especificado lámina por lámina en el plan.
- **Las ocho láminas tocadas, sin rasterizar y sin mirar.**
- **La copia sin notas**, sin regenerar.
- **El re-barrido sigue corriendo** (86 ok / 18 stop / 26 pendientes a las 19:31, ETA ~20:55) y
  **§8.b sigue sin recontar**. Queda abierta la decisión de si se actualizan las láminas 19, 21 y
  26 en caso de que el recuento cierre antes de la reunión.
- Cero GPU, cero `sbatch`, cero cambios a los dos scripts que el driver relee, cero ediciones al
  generador del deck.

---

## Sesión 11 (19-ago-2026) — el plan quedó escrito, y dos cosas cambiaron de estado solas

Sesión corta y de reconocimiento: se escribió el plan de ejecución
(`~/.claude/plans/enumerated-finding-cocke.md`) para que una sesión limpia haga el guion, y en el
camino se descubrió que **dos procesos que el handoff daba por pendientes ya cerraron**.

### 1. El job de HoVer-NeXt CORRIÓ (lo más importante para la reunión)

`sprints/B8_sprint8/hovernext_129741/corrida_5008.md`. La cola de la GPU **se drenó sola** de
madrugada; el job 5008 arrancó 00:33 y cerró 00:52 con exit 0. **18 min de pared** contra las
3 h 36 de HoVer-Net. Produjo **177 detecciones de mitosis** en la lámina entera (más seis clases
más), con los dos zips crudos que la auditoría había pedido conservar.

**Corrió solo el brazo de mitosis** (`lizard_convnextv2_tiny`). El de ensemble
(`pannuke_..._{1,2,3}`) **nunca se lanzó** y su directorio está vacío. La cola está vacía ahora,
así que lanzarlo es un `sbatch` — decisión de Ernesto.

**No se cruzó nada todavía** contra las 26 marcas del patólogo: las 177 son salida cruda.

**Esto deja stale cinco láminas del deck** (15, 22, 23, 24, 26), que fue construido dando por
hecho que la corrida no había pasado. El detalle por lámina está en §4 de `corrida_5008.md`.

### 2. El re-barrido con giro también cerró

18-ago 20:53, 366 min de pared, 109 JSON, 20 rechazadas por el test, **0 fallidas**. Ernesto
decidió **cosecharlo y actualizar el cuerpo del deck** con los números nuevos, en vez de
presentar el recuento como provisional. Sin cosechar todavía.

### 3. QA visual de las ocho láminas tocadas: hecho

Rasterizadas y miradas. La medición de tinta por renglón dio **cero en las ocho**, igual que
daba con los seis defectos anteriores adentro; los dos hallazgos salieron del ojo:

- **Lámina 23**: el rótulo `marcas / de 28` colisiona con la etiqueta `14` del eje Y del gráfico
  del techo. Se lee «de 2814».
- **Lámina 24**: `pie_lineas` arranca 0,04″ antes de que termine la tabla; la nota queda pegada
  a la última fila.

Las otras seis (15, 17, 18, 19, 20, 26) están limpias. El eje de ángulos de la 20 dibuja bien
sus bandas anidadas: es diseño, no defecto.

### Lo que NO se hizo

- **El guion de las doce láminas nuevas: sigue en cero.** Es el pendiente grande.
- **La cosecha del re-barrido**, decidida pero sin correr.
- **Los dos defectos visuales**, sin arreglar.
- **El brazo de ensemble de HoVer-NeXt**, sin lanzar.
- **El cruce de las 177 contra las marcas**, sin hacer.
- Cero GPU, cero `sbatch`, cero ediciones al generador del deck.

---

## Sesión 12 (19-ago-2026) — el deck quedó presentable, y el dato refutó una predicción nuestra

Sesión de ejecución con reunión el mismo día. Se cosechó el re-barrido, se corrigió el cuerpo de
nueve láminas y se escribió el guion de las doce. **Cero GPU.**

### 1. El paso 0 valió la pena: el plan estaba parcialmente obsoleto

El plan del 18-ago se escribió antes de que el job de HoVer-NeXt corriera. Al reevaluarlo contra
el estado nuevo, el alcance resultó **mayor** que el presupuestado: **nueve** de las doce láminas
nuevas necesitaban edición de cuerpo, no las cinco que el plan contaba. Se llevó la decisión de
alcance a Ernesto antes de ejecutar, con tres preguntas.

**Lo que Ernesto decidió**: reencuadrar la lámina 24 como lección en vez de borrarla; **cuerpo
primero, guion después** (garantiza que nada falso llegue a la pantalla); y **no lanzar** el brazo
de ensemble, para no distraer del deck.

### 2. La cosecha, y la predicción que falló

`sprints/B8_sprint8/anotaciones_patologo/regiones_escaneo/resultados.md` **§12** (nueva).

| | Antes | Ahora |
|---|---|---|
| Cadena | 490 → 139 → 129 → 108 | 490 → 139 → **130 → 109** |
| Medibles | 54 de 108 (50 %) | **77 de 109 (70 %)** |
| Re-escaneo | 33 de 54 (61 %) | **31 de 77 (40 %)** |
| Seriadas | 1 | **12** |

- **La tasa de recuperación (24/54 = 44 %) cae dentro del IC [21 %, 79 %] que §10.c predijo.** El
  probe acertó.
- **Pero §10.c también escribió que «el 33 es un piso», y el dato lo REFUTA**: el pool creció y el
  recuento bajó a 31. Se reporta el fallo en el cuerpo del deck y en el guion, sin taparlo.
- **El patrón P4 quedó MEDIDO**: las recuperadas caen en «seriadas» al 29 % contra el 10 % de las
  ya medibles, y **10 de las 18** que no dan re-escaneo fallan **los dos** criterios a la vez.
- **Próximo cuello identificado**: la etapa B pide escala (mediana 1,0117, **11 de 24** fuera de
  ±2 %) y no la busca.
- Las **30** que no se recuperan **resisten el giro** ⇒ la lectura de §9.a se les sostiene entera.

### 3. El deck: nueve láminas de cuerpo y el guion de las doce

- **18 a 21** por los números; **15, 22, 23, 26** por la corrida; **24** reencuadrada como lección
  (la fila de GPU se drenó sola); **23 y 24** además por sus dos defectos visuales.
- **Guion: 5.036 palabras**, 25 de 26 láminas con nota. Formato verificado a máquina: cero dígitos
  en la prosa, cero guiones largos, cero «palanca», cero nombres, cero números de trabajo.
- **QA visual hecho**: las ocho láminas tocadas rasterizadas y miradas una por una.
- La lámina 22 ahora etiqueta `0,872 / 0,914` como **percentil medio** y no como AUC (los AUC son
  `0,874 / 0,919`, casi iguales: ésa era la trampa).

### 4. Verificación de paso: los conteos de la corrida cuadran

Las siete clases de `pred_*.tsv` en disco reproducen **exactamente** la tabla de
`corrida_5008.md` §2 (mitosis 177, epitelial 87.553, conectivo 68.364, linfocito 67.952, plasma
12.322, neutrófilo 1.419, eosinófilo 542).

### Lo que NO se hizo

- **Las dos primeras capas de QA del guion**: `@humanizer-es` y la lectura en voz alta de las doce
  notas extraídas a un solo archivo. La tercera (barrido de reglas duras) **sí** corrió.
- **El brazo de ensemble de HoVer-NeXt**, sin lanzar (decisión de Ernesto). Cola vacía, un envío.
- **El cruce de las 177 contra las 26 marcas**, sin hacer. Es el segundo factor del techo, y es
  análisis, no GPU.
- Sin cambios en: los dos papers de `papers_11_agosto/` sin fichar, las dos preguntas del 6-ago
  sin respuesta, la réplica del 4589 con semillas nuevas, el sign-off del patólogo y `@grilling`
  sin estrenar.

## Sesión 13 (19-ago-2026) — el guion cerró su QA, y el cruce dio 13 de 26

Sesión de análisis y cierre, con la reunión todavía por delante. **Cero GPU.**

### 1. El QA del guion: la capa de estilo pasó, la de lectura de corrido rindió

- **`@humanizer-es`: PASA sin una sola edición.** Medido con `grep` antes de reescribir: cero
  vocabulario del cluster de IA, cero colas de gerundio, cero paralelismos formulaicos, cero
  relleno, cero rayas, cero «palanca». Largo de oración con **sd 9,0 sobre media 18,9** (rango 3
  a 55), que es variedad humana. La skill pide explícitamente no sobre-editar prosa limpia.
- **La lectura de corrido: cuatro hallazgos**, ninguno visible para las otras capas. El más grave
  es de cuerpo, no de guion: el remate de la lámina 25 decía que un patrón **«ahorró la corrida
  entera»**, y no la ahorró (el techo dio alto y la corrida se hizo igual). La nota de la 23 lo
  decía bien y en condicional ⇒ el defecto era un **desacuerdo entre cuerpo y guion sobre el mismo
  hecho**. Los otros tres: una referencia por conteo de láminas que apuntaba cuatro atrás, un dato
  que aparecía como dado porque su presentación vive en el bloque congelado, y una colisión de
  «doce láminas» entre la 20 y la 26.
- **Cinco ediciones**, verificadas a máquina: 11 de las 13 líneas modificadas caen en `notes()` y
  las 2 restantes son el remate del cuerpo, que es el cambio intencional. Notas 15-26: **5.081
  palabras (+0,85 %)**. Deck reconstruido, copia sin notas regenerada, lámina 25 rasterizada y
  mirada.

### 2. El cruce: HoVer-NeXt recupera 13 de las 26 marcas

`sprints/B8_sprint8/hovernext_129741/cruce_marcas.md` · `scripts/cruce_hovernext_marcas.py`.

- **13/26 = 50,0 %**, con emparejamiento **uno a uno** (húngaro). Contar por distancia mínima daba
  14 y hasta 18, siempre con **13 detecciones distintas**: el exceso era la misma detección reusada.
- **El corte no decide nada: plano entre 7,5 y 75 µm**, un rango de 10×.
- Distancias **bimodales** (p25 = 2,0 µm, p75 = 114,6 µm): o acierta encima o no hay nada cerca.
  Las 13 que falla tienen su detección más cercana a **115 µm de mediana**.
- **P2.a cerrada.** Desde **K=189 (7,6 % de la región)** el factor que manda es la **detección**,
  no la máscara. En el 12 % la intersección real es **11 de 26** contra los 13 que promete `min()`.
  Chequeo de sanidad aprobado: con la región entera los dos brazos dan 13/26 exacto.
- Sin evidencia de que lo detectado sea lo más atendido (p = 0,200 y 0,383, n = 13 contra 13).
- **No se calcula precisión**: las 69 detecciones restantes de la región anotada **no son falsos
  positivos** (marcas parciales). El 50 % tampoco es «el recall de HoVer-NeXt».

### Lo que NO se hizo

- **La lámina nueva del deck con el cruce, y la corrección de las láminas 22, 23 y 26**, que hoy
  anuncian el cruce como pendiente. **Ernesto lo aprobó y quedó sin ejecutar** por cierre de
  sesión. Es lo primero de la próxima.
- **El brazo de ensemble**, sin lanzar (decisión de Ernesto sostenida dos veces en esta sesión).
- Sin cambios en: los dos papers de `papers_11_agosto/` sin fichar, las dos preguntas del 6-ago,
  la réplica del 4589 con semillas nuevas, el sign-off del patólogo y `@grilling` sin estrenar.

---

## Sesión 14 (19-ago-2026, tarde) — el cruce entró al deck, y cayeron seis frases

Sesión de deck. **Cero GPU.** La reunión con Sebastián seguía sin ocurrir al arrancar, así que se
ejecutó el plan aprobado en la sesión 13 sin replanificar.

### 1. La lámina nueva: el segundo factor del techo

Deck de **26 a 27 láminas**. La nueva va **después de la 23** (el techo), así que 24→25, 25→26,
26→27. Las dos referencias por posición del deck (láminas 5 y 19) apuntan **antes** del punto de
inserción y se verificaron intactas.

Todo sale de `sprints/B8_sprint8/hovernext_129741/cruce_marcas.md`, transcrito a dos constantes
del generador. Tres objetos: el titular **13 de 26 = 50,0 %** con el emparejamiento uno a uno al
lado (sin eso la primera pregunta de la sala es por qué no son 18), **la meseta** como tira de
celdas con helper nuevo `meseta_tolerancia` (una meseta dibujada como curva es una recta que no
llama la atención de nadie; como tira, el mensaje es el mismo número repetido seis veces), y **la
tabla conjunta con la columna «ambas»**, recortada a cuatro filas por espacio.

Las tres salvedades de `cruce_marcas.md` §5 que más fácil se pierden van en el **cuerpo** y no
solo en el guion: la **unidad** (26 marcas contra los 28 parches de la lámina anterior, que no se
encadenan), que la **cota `mín( )` es floja**, y que el número de la región entera es el chequeo
de sanidad. **Cero precisión en todo el deck**, y es deliberado.

El remate no es el número sino el hallazgo: **el cuello se movió**. Desde el 7,6 % de la región
el que manda es la detección, no el recorte.

### 2. Seis frases stale, no cuatro

El handoff listaba cuatro (guion de la 22 ×2, guion de la 23, guion de la 27). Barriendo el
generador aparecieron **dos más, de cuerpo**, las dos en la lámina 15, que es el mapa del bloque:
«177 mitosis, **sin cruzar**» y «Uno de ellos **ahorró** una corrida entera». La segunda es la
misma afirmación que la sesión 13 corrigió en la lámina 26 y que allí había quedado en pasado.
La lámina 27 se rehízo entera (tres tarjetas, remate y guion): listaba como pendiente lo que la
24 acaba de mostrar.

**No se tocó** el cuerpo de la 22 («nada cruzado todavía», «cruzarlas es lo que sigue»): en ese
punto del recorrido son verdad, y ahora además **arman** la lámina nueva.

### 3. Verificación

`AUDITORÍA: sin avisos` en las 27; copia sin notas regenerada. **AST contra el diff**: de 178
líneas nuevas, 87 caen dentro de un `notes()` y las 91 restantes son cuerpo o código, todas
justificadas. Estilo medido sobre el `.pptx`: cero rayas, cero «palanca». Guion nuevo de **762
palabras**, sd 10,2 sobre media 19,1, cero dígitos en la prosa; medido con `grep` **antes** de
invocar `@humanizer-es`, que por eso no se corrió (habría sobre-editado prosa limpia).
Rasterizadas y miradas la 15, la 24 y la 27.

### 4. La 23ª pasada de auditoría

`sprints/B8_sprint8/auditoria_coherencia/hallazgos.md`. Tres hallazgos, uno durable:

- **W1 (durable)** — una frase falsa **sobrevive a su propia corrección** porque el mapa del
  bloque la repite más corta, y de corrido el mapa llega **antes** que el desarrollo donde se
  caza. Regla: barrer el generador entero por **sustantivo y verbo**, no por la frase. Y el
  inventario de un handoff no sustituye al barrido (listaba cuatro, había seis). ADDENDUM en
  [[deck-qa-puntos-ciegos-chequeo]] + línea de índice.
- **W2** — `techo_atencion.md` seguía pidiendo medir lo ya medido, y el puntero existía en un
  solo sentido. Nota fechada en la cabecera; la lectura 1 **no se reescribe**.
- **W3** — `corrida_5008.md` §4 era una lista de trabajo consumida sin marcar, que se lee como
  instrucción. Nota de cierre fechada; la tabla queda intacta.

### Lo que NO se hizo

- **El brazo de ensemble**, sin lanzar. Sigue siendo decisión de Ernesto.
- Sin cambios en: los dos papers de `papers_11_agosto/` sin fichar, las dos preguntas del 6-ago,
  la réplica del 4589 con semillas nuevas, el sign-off del patólogo, `@grilling` sin estrenar, y
  **coordinar con `sgaete`** antes de barrer las doce láminas anotadas.

---

## Sesión 15 (19-ago-2026, tarde) — el deck se recorta a la mitad y los mapas entran

**Misión**: ejecutar el recorte que Ernesto dejó escrito en
`sprints/B8_sprint8/presentacion_b8/correcciones.txt`. De **27 láminas a 15**, más una de control
que pidió después: **16**.

### 1. Las dos lecturas contradictorias, resueltas ANTES de borrar

El texto ordena eliminar 9, 15, 16-21, 22, 25, 26 y 27, y sobre **23 y 24** dice otra cosa: que
esperaba los mapas de calor con imágenes de dónde se fija, «**junto con los datos de si
identifica las mitosis**». Ese dato **es** la 24, o sea el 13 de 26. Leerlo como «borrar las dos»
se llevaba el único resultado cuantitativo que el mismo renglón pide conservar. Y «eliminá la 26,
deberíamos tener una que mencione RESULTADOS» describe esa misma lámina.

Ernesto resolvió las dos juntas: **una sola lámina de resultados**, con los mapas y el número. Se
va la 23 (el techo, que es método); la 24 cambia de forma y conserva el 13 de 26 y la tabla de los
dos factores. Se va la meseta de tolerancia.

### 2. Los mapas, sin GPU y sin re-medir nada

Todo el material estaba en disco. `presentacion_b8/prep_assets_hovernext.py` **reusa el
emparejamiento de `scripts/cruce_hovernext_marcas.py`** (húngaro, 30 µm, mismo offset del geojson,
mismo corte de región), así que la figura no puede contar algo distinto del número que ya está
publicado. Produce la **cadena de tres paneles** (la misma región en tres estados: atención · el
12 % más atendido · las detecciones) y **cuatro detalles a resolución nativa**, elegidos por
separación máxima entre sí. `prep_assets_paper_hovernext.py` saca la Figura 1 del paper para la
lámina 14.

Dato nuevo que salió de dibujarlo: en el 12 % recortado caen **48 de las 82** detecciones de la
región. Eso cuenta **detecciones**, no marcas, y la lámina lo dice explícito al lado de la tabla
que cuenta marcas.

### 3. El barrido de referencias cruzadas (el hallazgo W1, aplicado)

Borrar seis láminas seguidas deja punteros colgando que **no se encuentran grepeando la frase**.
Aparecieron cuatro sitios: la portada prometía «tres cosas» y ahora son cuatro; el guion de la 7
apuntaba a «las pruebas que vienen ahora» (la lámina de controles); el de la 13 se apoyaba en el
nulo por traslación por su nombre; y «en dos láminas más» en la 6 **sigue resolviendo bien**, lo
que se verificó en vez de asumirlo. En el generador quedaron sin uso **13 constantes y 4
funciones**, retiradas; las que ya estaban huérfanas antes del recorte se dejaron como estaban.

### 4. La lámina de control, pedida después del recorte

Ernesto pidió «una última lámina donde se use puramente HoVer-NeXt para la misma WSI, sin CLAM».
**Se pudo sin correr nada**: la corrida fue sobre la lámina entera y el recorte se aplicó después,
sobre la salida, justamente para conservar esa comparación. Queda de cierre (lámina 16) y es la
que hace legible a la de resultados: sin un brazo sin recorte, «13 de 26 con el recorte» no se
compara con nada.

La escalera, toda medida: **lámina entera** 4799 parches / 68,0 mm² / 177 detecciones / **13 de
26**; **solo la región anotada** 2496 / 35,4 mm² / 82 / **13 de 26**; **el 12 % más atendido** 300
/ 4,3 mm² / 48 / **11 de 26**. O sea que **el recorte no compra marcas, compra área**: factor 16
en superficie por dos marcas. Las dos primeras filas coinciden por construcción (las 26 marcas
caen todas en la región anotada), y se verificó en vez de asumirlo.

Sigue sin afirmarse nada sobre las **95 detecciones de la región sin anotar**, y van del mismo
color que las otras para no sugerir que sean errores.

### 5. Verificación

`AUDITORÍA: sin avisos` en las 16, copia sin notas regenerada. **Rasterizado y mirado**: las 15 en
contacto y las dos nuevas a tamaño. Tres defectos que la auditoría no ve, arreglados: un rótulo que
se partía y quedaba tapado por la figura, una cabecera de tabla que partía «Detectada / s», y la
tabla diciendo «máscara» mientras el resto de la lámina decía «recorte». Los dos títulos nuevos
salían en dos renglones (los únicos del deck) y se acortaron. El generador bajó de 3783 a 2657
líneas; el `.pptx`, de 20,9 a **17,1 MB** tras acotar los assets a la resolución que la lámina usa.

### Lo que NO se hizo

- **`correcciones.txt` no se versiona** — decisión de Ernesto.
- **No se borraron** los assets de regiones de `assets/`: el deck ya no los usa, pero son producto
  de trabajo real y su script sigue ahí.
- **Cero GPU**, cero `sbatch`. El brazo de ensemble sigue sin lanzarse.
- Sin cambios en: los dos papers de `papers_11_agosto/` sin fichar, las dos preguntas del 6-ago,
  la réplica del 4589 con semillas nuevas, el sign-off del patólogo, y **coordinar con `sgaete`**
  antes de barrer las doce láminas anotadas.

## Sesión 16 (19-ago-2026, noche) — la reunión se reduce a dos láminas, y esas dos se reescriben

**El alcance cambió a mitad de sesión, por decisión de Ernesto.** La sesión entró con el encargo
del handoff (leer el guion de las 16 de corrido, buscar arcos, decidir el recorte de tiempo) y ese
trabajo se hizo entero; pero al preguntarle por las decisiones, Ernesto redefinió la reunión: **solo
se presentan la 15 y la 16**, el reloj deja de importar, y el pedido pasa a ser pedagógico. Que cada
una quede muy bien explicada, y que las notas digan **qué hicimos**, **qué genera HoVer-NeXt**, **qué
representan las marcas que genera** y **por qué no rescató las 26 mitosis del patólogo**.

**La reunión con Sebastián YA OCURRIÓ** al cierre de esta sesión. Lo que dijo no está en el repo:
lo trae Ernesto a la sesión que planifique lo que sigue.

### 1. La consecuencia de diseño que gobernó la reescritura

Presentadas solas, la 15 y la 16 **pierden todo el andamiaje** de las anteriores: la 1 a la 8
establecían qué es la atención de CLAM, de dónde salen las 26 marcas y que son positivos parciales;
la 14 presentaba la herramienta. Nada de eso iba a estar en la sala. Las notas nuevas **cargan ese
contexto ellas mismas**, y ése es el motivo del crecimiento: **715 → 1419 palabras** en la 15 y
**441 → 693** en la 16, unos 16 minutos hablados para las dos.

### 2. El «por qué falla la mitad», que faltaba y estaba fichado hace cinco días

`cruce_marcas.md` §2 cerraba en «es ausencia» y ahí se detenía. La explicación estaba en
`papers_14_agosto/hovernext_estudio.md` desde el 14-ago, **nunca escrita junto al resultado**. Se
escribió como **§2.b nueva** y es lo que sostiene las notas:

1. **No es artefacto de medición**: meseta de 10× en la tolerancia (7,5 a 75 µm) y 115 µm de
   mediana a la detección más cercana en las falladas.
2. **La clase de mitosis se entrenó y validó SOLO en colon** (Lizard colon + 48 ROI de 11 WSI de
   colon + MitEval 13 ROI de colon; **cero mitosis medidas en mama**) y la lámina es de mama.
3. **Ni en colon es exhaustiva**: recall **0,720** de HNTiny, que es exactamente el checkpoint que
   corrimos ⇒ un 50 % fuera de su tejido **no es anómalo**.
4. **La dirección del sesgo empeora la lectura**: el patólogo marca solo lo más claro, así que las
   26 deberían ser **las fáciles**.

⚠ Con la salvedad que el propio estudio ya traía: **la versión ingenua («es un paper de colon») está
desactivada** para *tipificar núcleos* en mama (6ª de 19 tejidos). Lo que no tiene validación fuera
de colon es **la clase mitótica**, que es justo la que usamos.

**Lo que NO está medido y es lo barato que sigue**: si los núcleos fallados **fueron segmentados y
mal clasificados** o **no fueron segmentados**. Dos fallas con arreglos de costo muy distinto, y el
cruce solo miró la clase `mitosis`. Se contesta **sin GPU y sin re-correr**, con los `raw` que
sobrevivieron por `--keep_raw`.

### 3. Un error nuestro que iba a costar GPU

`cruce_marcas.md` §6 afirmaba que **el brazo de ensemble «ahora tiene contra qué compararse»**.
**Es falso**: el ensemble son los tres folds de **PanNuke**, que **no tiene clase de mitosis**
(`out_channels_cls` 6 = 5 + fondo, contra 8 = 7 + fondo de Lizard-Mitosis). Sobre su salida el cruce
**no es computable**. Lo mismo estaba en la memoria, **contradiciendo a su propio punto 1 de «How to
apply»**, que decía correctamente que PanNuke no tiene clase mitótica. Corregido en los dos, tachando
el enunciado viejo en vez de borrarlo. **Correr el ensemble no contesta la pregunta de mitosis.**

### 4. El análisis de arcos y de reloj, hecho y sin ejecutar

Se leyó el guion completo de las 16 de corrido. Queda en el README del deck para cuando se retome:

- **Desfase entre prioridades declaradas y presupuesto real**: la portada llama «corto» al encargo
  de expertos (**6,0 min**, 3ª lámina más larga), «comprimida» a SI-MIL (**17,4 min, 27,6 %**) y «lo
  que más quiero discutir» a HoVer-NeXt (**11,8 min**). Lo declarado comprimido ocupa más que lo
  declarado prioritario, y la lámina 10 sola son 866 palabras.
- **La 13 propone como futuro lo que la 14 a la 16 muestran hecho**. Es tiempo verbal.
- **La 13 descarta un paper «porque no distingue mitosis»** (CellViT, y es cierto) y dos láminas
  después entra un segmentador de pesos públicos que sí la tiene. No es contradicción, pero sin una
  cláusula que lo diga suena a una.

### 5. Verificación

`AUDITORÍA: sin avisos` en las 16, copia sin notas regenerada (16 láminas, 0 con notas), guion
re-extraído. Las notas nuevas: cero rayas «—», cero «palanca», números hablados en palabras.

### Lo que NO se hizo

- **No se recortó el guion de las otras catorce**, ni se tocó su contenido: el alcance cambió.
- **No se corrigió el dato stale de la 4 y la 13** («la única que tenemos anotada» / «cuántas
  láminas anotadas hay»), que son notas del 6-ago contra las **12 láminas** aparecidas el 17-ago.
  Está **solo en las notas habladas**; ningún cuerpo de lámina lo afirma. No se presentaban hoy, y
  cómo reencuadrar el objetivo 1 quedó sin decidir.
- **La fecha de portada queda en el 19 de agosto**, por decisión de Ernesto.
- **Cero GPU**, cero `sbatch`. El brazo de ensemble sigue sin lanzarse, y ahora hay una razón
  documentada para no lanzarlo con la mitosis como objetivo.
- Sin cambios en: los dos papers de `papers_11_agosto/` sin fichar, las dos preguntas del 6-ago, la
  réplica del 4589 con semillas nuevas, el sign-off del patólogo, y **coordinar con `sgaete`**.

## Sesión 17 (21-ago-2026) — sesión de PLAN: los cuatro encargos de Sebastián, cruzados contra el disco

**Sesión de planificación, sin ejecutar nada.** Ernesto trajo la retroalimentación de la reunión
(cuatro encargos) y esta sesión los verificó contra lo que hay en disco antes de proponer nada.
Cero GPU, cero escrituras fuera del repo. El plan ejecutable quedó en
`sprints/B8_sprint8/encargos_sebastian/plan.md` y la evidencia en `hallazgos_exploracion.md`.

### 1. Los cuatro encargos

1. Mapa de calor con el checkpoint de CLAM de **carcinoma invasivo**, top-k a HoVer-NeXt, y
   comparar contra el resultado ya obtenido.
2. Ver las imágenes de las **164** detecciones sin marca (177 − 13) y ver si se parecen entre sí.
3. Cruzar la **necrosis** de HoVer-NeXt contra las marcas del patólogo.
4. Correr HoVer-NeXt sobre las **12 láminas anotadas**.

### 2. Lo que la verificación cambió del enunciado

- **El checkpoint que Sebastián no recordaba era CDIS**, no invasivo:
  `carcinoma_ductal_insitu_presente_ci_reform` fold 4 (job 4589), escrito en los dos `meta.json`.
  El de invasivo es la tarea **`invasion_carcinoma_gate_pth_balance`** (2013 invasivo / 802 no);
  la 129741 está etiquetada `invasivo` y cae en **test del fold 0**.
- **El checkpoint del gate que hay en disco es Mammoth, y su `experiment.txt` dice `clam_mb`.**
  El `state_dict` tiene `attention_net.0.mammoth.*`. CLAM plano del gate **no existe** ⇒ hay que
  entrenarlo. Memoria nueva [[checkpoint-familia-se-lee-del-statedict]].
- **Lizard-Mitosis no tiene clase de necrosis**: sus 7 clases son neutrophil, epithelial-cell,
  lymphocyte, plasma-cell, eosinophil, connective-tissue-cell y mitosis. `dead` está **solo en
  PanNuke**, que nunca se lanzó ⇒ el encargo 3 exige el ensemble, **sin que eso reabra** la
  decisión de no correrlo para mitosis (esa sigue en pie, y por la misma razón). Memoria nueva
  [[hovernext-clases-necrosis-solo-pannuke]].
- **Las 12 tienen mitosis**, pero tres concentran 63 de 94 y **seis tienen ≤3** ⇒ el denominador
  que se reporta es el agregado. Necrosis hay en **5 láminas, 18 polígonos**, con el vocabulario
  partido en `necrosis` / `Necrosis` / `Comedonecrosis`.
- **`sgaete` ya midió atención contra anotaciones en 8 tareas × las 12 láminas**, necrosis
  incluida, pero leyendo la **rama predicha** — para la 129741 predice `no identificado` cuando la
  etiqueta es `presente_central`, y por eso le da AUC 0,382. El gate de invasivo **no** está entre
  sus 8 ⇒ el encargo 1 es trabajo nuevo.

### 3. Las decisiones que tomó Ernesto

- **Encargo 1: los dos brazos.** El Mammoth del gate hoy en CPU, y el CLAM plano entrenando el
  fold 0 sobre el mismo `--split_dir` y la misma config, pareado por construcción (P1).
- **GPU autorizada para los tres**: las 11 láminas restantes, el ensemble PanNuke sobre la 129741,
  y el CLAM plano del gate. Orden de envío: el corto primero.
- **Encargo 2: láminas de contacto agrupadas por parecido**, en tres bloques (164 sin marca, 13
  acertadas, 13 marcas que se escaparon).
- **`sgaete`: seguimos y le avisamos después.**
- **Pedido nuevo, sobre el cierre**: incorporar **CLAM puro como línea base** antes de HoVer-NeXt,
  contra Mammoth y contra los dos con el detector encima, para saber si el detector **agrega**.
  Quedó como A2.bis del plan. Casi todo ya está computado en `techo_conjunto.csv`; lo nuevo es el
  **eje**: se grafica recall contra **carga de revisión** (mm² y objetos a mirar), porque
  compararlos por recall a secas dice que HoVer-NeXt empeora, y eso es artefacto de mirar una sola
  columna. Precisión de forma que hay que sostener: **Mammoth no se suma a CLAM, lo reemplaza**.

### 4. Estado al cierre

Rama `main`, sincronizada con `origin`, **sin jobs propios**. El nodo lo ocupan `sgaete` 5052
(`phase3_s`, corriendo hace 6 h 20) y `capstone` 5063; `nschiaff` 5061 en cola por `Resources`.
Nada del plan se ejecutó: la sesión siguiente arranca por la Fase A.

---

## Sesión 26 — 25-ago-2026 · escrito el contrato de comunicación en chat, y borrada la carpeta

Sesión limpia, documental, sin GPU: ejecuta el plan que la 25 dejó escrito y nada más.

**CLAUDE.md §"Contrato de comunicación en chat"** (commit `8ed4289`, líneas 1508-1542, junto a
§"Contexto del usuario para sesiones rápidas"). **35 líneas**, 1507 → 1542, dentro del presupuesto
de 30-35. Lleva las tres primitivas cosechadas: conclusión al final de la respuesta, códigos de
referencia y alias. Alcance **solo el chat**: los entregables escritos siguen bajo `@humanizer-es`
y las reglas de deck, y la sección los enlaza en vez de copiarlos.

**Lo que se recortó para entrar en presupuesto** (el primer borrador salía en 44 líneas): de las
colisiones de namespace quedaron `A1`/`B1` (brazos del grid 4774 y encargos de Sebastián) y `Q1` (la
pregunta del B7), y se fue `P1`-`P4`, que no era colisión real porque la sección no define códigos
`P`. También se fue la cláusula "en respuestas cortas, no", que ya la implica el umbral de tres o
más. Las dos siguen completas en la memoria.

**La carpeta `fixing-smartass-opus-5-main/` se borró** (14 archivos, 192 KB, nunca trackeada),
después del commit y con confirmación de Ernesto en el momento. El orden importaba: la memoria
[[fixing-opus5-evaluacion-y-cosecha]] y la sección son lo que queda en su lugar, y la memoria
incluye los textuales de lo rechazado para no tener que volver al original.

**Verificado que la sección no choca con nada**: los alias `scr`/`eli`/`foc`/`cod` no colisionan con
ningún token del repo (el único match de `cod` es el glob `*.py[cod]` de un `.gitignore` de
ejemplo), y de los códigos de referencia solo `@grilling` los usaba en una skill. Sin cambios en
agentes ni en skills.

**Nada del sprint se movió.** Los pendientes del B8 siguen abiertos tal como los dejó la sesión 24.

---

## Sesión 25 — 25-ago-2026 · sesión de PLAN: evaluado `fixing-smartass-opus-5`, cosecha sin ejecutar

Sesión sin GPU y sin tocar el sprint. Ernesto subió al root del repo
`fixing-smartass-opus-5-main/` (repo MIT de IndyDevDan: un system prompt que se cuelga de
cada sesión para que el modelo responda corto y no ensanche el trabajo) y pidió evaluar si
integrarlo.

**Veredicto: no se integra, se cosechan tres primitivas.** Molde de
[[wayfinder-evaluacion-y-cosecha]]. Los cuatro bloqueos, la cosecha y los textuales de lo
rechazado quedan en la memoria [[fixing-opus5-evaluacion-y-cosecha]], que es
autosuficiente porque **la carpeta se borra**.

El bloqueo decisivo fue **de vehículo, no de contenido**: `just`, `herdr`, `jq`, `pi`,
`npm` y `brew` están los seis ausentes, `--append-system-prompt-file` no existe en claude
2.1.152, no hay output-styles en esta versión, y la extensión de VSCode no pasa flags de
CLI. **El único vehículo de instrucción por-sesión acá es `CLAUDE.md`.**

Lo que sí compra algo: **nada gobierna hoy cómo responde Claude en el chat**
(`@humanizer-es` declara su alcance en el guion hablado y los entregables). Y los códigos
de referencia que el repo ajeno propone **ya son convención de facto** en los
`hallazgos.md` (F1 aparece 120 veces bajo `sprints/`) sin estar escritos en ninguna parte.

**Decisiones de Ernesto:** alcance solo chat · el trailer `Co-Authored-By` se mantiene ·
se adoptan códigos y alias · la carpeta se borra una vez cosechada.

**Pendiente, para una sesión limpia:** escribir la sección de CLAUDE.md (30-35 líneas) y
recién después borrar la carpeta. Handoff
`.handoffs/handoff_20260825_contrato_chat_claudemd.md`.

---

## Cosecha del 25-ago — B3 y B1 corrieron solos y terminaron bien

Registrado al cerrar la sesión 24 (que fue el 23). **La reunión del lunes 24 ya pasó y esta
sesión no sabe cómo salió.** Los dos jobs que llevaban tres sesiones en `PD` corrieron la
madrugada del 25, sin que nadie los tocara.

**5069 — B3, CLAM plano del gate de invasivo, fold 0.** Fin 02:09. Cerró por early stopping con
**test ROC AUC 0,9539** (error 0,1004; clase 0 185/200, clase 1 66/79) y val AUC 0,9749.
Resultados en `results/b8_gate_invasivo/invasion_carcinoma_gate_pth_balance_clam_fold0_s1/`, con
resumen en **`summary_partial_0_1.csv`** (no `summary.csv`). **Esto destraba la pregunta abierta
de la lámina 15 del deck**: hasta ahora el brazo del gate era Mammoth y no existía el plano en
disco, así que no se podía separar si el efecto era de la tarea o del brazo. Ahora sí, y es CPU
post-hoc.

**5070 — B1, HoVer-NeXt sobre 11 láminas.** Fin 04:03, 113 min de pared, ~7 min por lámina.
`TERMINADO OK=11 SKIP=0 FALLO=0`, 831 MB, las 11 completas. **555 detecciones de mitosis**
(103762 252 · 126504 109 · 124806 74 · 128194 45 · 164001 20 · 109609 13 · 124729 10 · 144317 10 ·
106552 10 · B25-158899 7 · 110616 5), más las 177 de la 129741 = las 12 anotadas. Habilita el
**cruce de las 94 marcas**, que es el pendiente arrastrado.

⚠ **`--keep_raw` fue apagado a propósito**: no quedaron los zarr `_inst`/`_cls`, así que esta
salida **no** sirve para la pregunta de A0 (segmentado-pero-mal-clasificado), que ya está
contestada sobre la 129741.

### El inventario del `.slurm` mentía, y era caro

El log de 5070 cierra con **«SIN SALIDA» en las 11 láminas**, sobre un barrido que había
terminado OK y con 831 MB en disco. El chequeo miraba `$OUTBASE/<slide>/pred_mitosis.tsv` y
HoVer-NeXt escribe con el id **anidado dos veces**, `$OUTBASE/<slide>/<slide>/`. Corregido en
`scripts/run_hovernext_slides.slurm` (ahora tolera las dos disposiciones).

**Por qué se registra y no se arregla en silencio:** leer ese log sin mirar el disco lleva a dar
el barrido por fallido y **re-encolar ~2 h de GPU detrás de un `UNLIMITED` ajeno**. Es la misma
familia que el workaround C (sin `sacct`, el `.out` es la única traza) con un agravante: acá la
traza **existe y miente**. Un verificador de salida se prueba contra una corrida buena, no solo
contra una fallida.

### La cola sigue igual de mala

El nodo pasó a **`nschiaffi` 5085 (`UNLIMITED`, 6 h)** y **`gvenegas` 5087 también pide
`UNLIMITED`**. El problema de backfill del workaround L **no se resolvió**: los dos jobs no
entraron porque la cola mejorara, entraron porque el `UNLIMITED` anterior terminó. **B2 sigue sin
lanzar** y encolarlo hoy lo pone detrás de dos `UNLIMITED`.

---

## Sesión 24 — 23-ago-2026 · el guion RECORTADO y aplicado: el deck queda presentable

Sesión de CPU y python-pptx: ni GPU ni jobs. Cierra el §13 del
`plan_actualizacion_24ago.md` y con él **el último pendiente del deck del lunes**. El `.pptx`
ya se puede presentar.

### 1. El recorte

`sprints/B8_sprint8/presentacion_b8/guion_recortado_24ago.md`, **de 7160 a 5624 palabras
(21,5 %)**, contra el objetivo de ~4500 del plan. Quedó en ~43 min y **la diferencia es
deliberada**: la lista de «lo que el recorte no puede comer» son los pedidos literales de
`correcciones.txt` y suma ella sola ~1000 palabras repartidas en diez láminas.

**La auditoría de cierre corrigió el argumento** (`auditoria_coherencia/hallazgos_sesion24.md`
§H2): esa lista explica **668** palabras del exceso, pero las otras **496** caen en láminas
**sin** ningún pedido literal (L12 +177, L14 +101, L16 +93, L10 +71, L13 +49). Llegaron a su
presupuesto solo L1 (+3) y L2 (+2). El piso que impone lo intocable es real, pero **quedan ~491
palabras recortables sin desobedecer nada**, que dejarían el guion en ~5133 (~39 min). Pendiente,
no cerrado.

### 2. La pasada de `@humanizer-es`

Sobre el archivo corrido. Quinta pasada, y **quinta vez que los racimos son de ritmo y ninguno
de vocabulario**: «lo que quiero / me importa» ×10 en nueve láminas, «Lo que…» abriendo oración
×11, párrafo que abre con «Y» ×8, «es el/la que» ×12 con cuatro en una sola lámina de 348
palabras, y los cierres «Con eso» ×5 y «Una precisión/salvedad» ×5. **El recorte y la
humanización tiraron para el mismo lado**: ese racimo era el meta-comentario que había que podar
igual.

### 3. Aplicado al generador y verificado en round-trip

Los 17 bloques a sus `notes()`, incluidos los **cinco `PLACEHOLDER_…`**. Las notas del `.pptx`
coinciden **palabra por palabra** con el markdown en las 17 láminas. `CLAM_Sprint8_guion.md`
regenerado; `CLAM_Sprint8_sin_notas.pptx` **no**, por la decisión del 22-ago.

### 4. El QA visual de las 17 encontró tres defectos con `auditar()` en CERO

Era el pendiente («siguen revisadas solo 2, 3, 4 y 11») y valió la pena:

1. **L17: panel y pie superpuestos 0,35"**, la clase «dos objetos válidos superpuestos» de
   [[deck-qa-puntos-ciegos-chequeo]]. Ninguna caja desborda la suya, así que no hay consulta
   programática que lo vea. El alto y el hueco ahora salen de lo que queda libre hasta el pie.
2. **L15 nombraba a una persona en el cuerpo** de la lámina, contra la convención del deck.
3. **L14 tenía un guion largo** en una celda, constraint-cero, que además convivía con
   «imposible» sin distinguirse. Ahora «no aplica» contra «imposible», y el guion lo explica.

Más dos desincronizaciones guion-lámina por la regla 13 (`score_N` proyectado y no dicho, en L5
y L8) y un decimal (L13 muestra 4,3 mm² y el guion decía «cuatro»).

### 5. Estado al cierre

- **17 láminas**, `auditar()` sin avisos, Barlow embebida. Cero placeholders, cero guiones
  largos, cero nombres propios y cero números de job en cuerpo, tablas y notas.
- Rama `main`, commits locales. **El push lo autoriza Ernesto.**
- Jobs **5069 (B3) y 5070 (B1) siguen `PD`**; **B2 sin lanzar**. Nada de esto lo toca el deck.
- Queda suelto: los **tres PNG de regiones huérfanos** en `assets/`, decisión de Ernesto.

---

## Sesión 23 — 22-ago-2026 · el guion escrito ENTERO, sin recortar y sin aplicar

Sesión corta, de CPU: ni GPU ni jobs. Ejecuta el §13 del
`plan_actualizacion_24ago.md`, que era lo único que le faltaba al deck del lunes, y lo deja
**a mitad de camino**: el guion de las **17 láminas está escrito** y **el recorte no**.
Cerrada a pedido de Ernesto para que una sesión limpia siga.

### 1. El entregable

`sprints/B8_sprint8/presentacion_b8/guion_borrador_24ago.md`, **sin aplicar al generador**.
Trae las 17 láminas, incluidas las **cinco que tenían `PLACEHOLDER_…`** (objetivos del
sprint y las cuatro de la Fase A), más una cabecera con el presupuesto por lámina, la lista
de lo que el recorte no puede comer y los cuatro arcos ya corregidos.

Cada cifra sale de su fuente y no del guion viejo: `a2bis_escalera_brazos.md` §2-§3,
`a2_atencion_gate_invasivo.md` §2-§3, `a0_segmentadas_o_no.md` §1-§4,
`a1_galeria_177.md` §1-§2, y las dimensiones de HoVer-NeXt de
[[hovernext-salida-geometria-y-clases]] (entrada RGB a 0,5 µm/px, ConvNeXtV2-tiny,
decodificador de instancia de 5 canales, de clase de 8, 13 en total).

### 2. Lo que NO se hizo, y es lo que bloquea presentar

**El recorte.** El borrador son **7160 palabras (~55 min)** contra el objetivo de **~4500
(~35 min)**. La cobertura está completa y la densidad no: las doce viejas quedaron más
cortas que su versión previa, pero las cinco nuevas suman unas 2100 palabras que antes no
existían, así que el total apenas baja de 7220 a 7160. Falta también la pasada de
`@humanizer-es`, que es el procedimiento de la convención, y aplicar los bloques a las
llamadas `notes()` del generador.

### 3. Cuatro arcos que el guion vigente tenía rotos, y el borrador corrige

Salieron de leer las 17 notas en un archivo corrido, que es el método
([[humanizer-es-skill]] §3), y ninguno se ve lámina por lámina dentro del generador:

1. La **portada** anunciaba «al final, después de los objetivos que propongo»: los objetivos
   se mudaron a la posición 2 el 22-ago y lo que cierra ahora es la Fase A.
2. La **lámina 12** decía «falta algo que no medimos, es lo primero que yo haría» sobre si
   los núcleos fallados estaban segmentados. Lo contesta la **lámina 16**, que entró en esa
   misma tanda: la promesa quedaba viva veinte segundos antes de su respuesta.
3. La **lámina 13** cerraba la presentación («con eso cierro») con **cuatro láminas por
   delante**. Es exactamente el defecto que [[humanizer-es-skill]] §3 describe.
4. La **lámina 13** conservaba «el recorte no compra marcas, compra área», que Ernesto
   rechazó por poco profesional en `correcciones.txt`; el cuerpo de la lámina ya se había
   corregido el 22-ago y el guion no.

Los cuatro son consecuencia de la misma causa: la reestructura del 22-ago movió láminas y el
guion se quedó describiendo el recorrido anterior.

### 4. Decisión de Ernesto en esta sesión

**`CLAM_Sprint8_sin_notas.pptx` ya no hace falta.** Sale de la lista de derivables a
regenerar; `sin_notas.py` queda en el repo sin correr.

### 5. Estado al cierre

- Rama `main`, árbol limpio antes de esta sesión. Jobs **5069 (B3) y 5070 (B1) siguen `PD`**,
  detrás del `llm_labeller` de `gvenegas` (12 h 24 al cierre) y de tres ajenos de la cuenta
  compartida. **B2 sigue sin lanzar.**
- El deck **sigue sin poder presentarse**: las notas del `.pptx` son las viejas, con los
  cinco marcadores puestos.

---

## Sesión 22 — 22-ago-2026 · el plan del deck, EJECUTADO salvo el guion

Ejecuta `sprints/B8_sprint8/presentacion_b8/plan_actualizacion_24ago.md`. **Trabajo de CPU y
python-pptx**: ni GPU ni jobs. `CLAM_Sprint8.pptx` pasa de 16 a **17 láminas**, compila con
`auditar()` **sin avisos** y con Barlow embebida.

### 1. Lo que quedó hecho

- **`TPL_KEEP` a `(0,)`**: se retira la lámina de título del template y **los objetivos del
  sprint ocupan la posición 2**, con el molde exacto de la ex-lámina de cierre. Los seis
  objetivos (4 cerrados, 2 en curso) se midieron con `text_w` para que cada uno entre en un
  renglón. El sprint y la fecha, **24 de agosto de 2026**, pasan a la portada.
- **Las 13 correcciones de forma** de `correcciones.txt`, incluida la que más pesaba: el
  diagrama divergente ahora lleva **encabezado de métrica** («diferencia de AUC entre los dos
  recortes, partición por partición») y las dos direcciones flanqueando el cero, y pierde las
  dos leyendas que se leían como jerga. Los cuadros por partición se siguen dibujando, sin
  rótulo, y cómo se leen es material del guion, que es lo que Ernesto pidió.
- **Las cuatro láminas nuevas de la Fase A**, las tres primeras con tabla nativa:
  `lam_escalera_brazos` (A2.bis), `lam_gate_invasivo` (A2), `lam_a0_falla_la_clase` (A0) y
  `lam_galeria_164` (A1, con las dos láminas de contacto). **Cada cifra verificada contra su
  CSV**, no contra el documento que la cita.
- **Las láminas de contacto se copian a `assets/` desde `prep_assets_hovernext.py`**, así que
  el deck se reproduce entero desde el generador.
- **La necrosis queda fuera**, por la decisión del 22-ago: sin la clase `dead` (B2, sin
  lanzar) el encargo 3 no se contesta.

### 2. El cross-check encontró un número mal en un documento propio

`a2bis_escalera_brazos.md` §2 tenía **`2496` en las cuatro columnas de la fila «26/26»** de una
tabla cuya columna promete «cuántos objetos pide cada brazo para llegar a». Ese 2496 es el
**chequeo de sanidad** (la región entera), no la carga mínima: el CSV da **CLAM 1392, Mammoth
750, la intersección 915 y la unión 1022**. Las otras seis filas reprodujeron **exactas**.

La causa es de método y por eso se registró: en la meseta la interpolación que produce el resto
de la tabla es **degenerada**, así que esa fila pide el primer cruce medido, que es otra
convención. **Ninguna conclusión del documento se mueve** — se apoyan en las filas de 8 a 22 y
en el techo del detector. El documento lleva la corrección fechada y el deck presenta **8, 13,
19 y 22**, con el tope de la atención dicho en prosa. Detalle: [[carga-fija-no-k-fijo]].

### 3. Lo que NO se hizo, y bloquea presentar

**El §13 del plan, o sea el guion entero.** Sigue en **9131 palabras (~70 min)** contra el
objetivo de **~4500 (~35 min)**, y **las cinco láminas nuevas tienen `notes()` con un
`PLACEHOLDER_…`**. Falta también pasar el resultado por `@humanizer-es`, regenerar
`CLAM_Sprint8_sin_notas.pptx` y `CLAM_Sprint8_guion.md`, mirar las 17 rasterizadas de punta a
punta y escribir la sección «El recorte del 22-ago» en `presentacion_b8/README.md`.

Dos cosas del plan que no sobrevivieron a los datos, las dos con su motivo en el código: la
fila de 26/26 (arriba) y que **la Figura 1 de HoVer-NeXt no puede ir a 9,28" de ancho** (su
razón 1,621 pediría 5,72" de alto y el cuerpo mide 4,22"); para que ampliarla fuera real se
retiró también su barra de remate, que es lo que hace el template en sus láminas de
arquitectura.

### 4. Estado al cierre

- Rama `main`. Jobs **5069 (B3) y 5070 (B1) siguen `PD`**, detrás del `llm_labeller` de
  `gvenegas` (12 h) y de tres jobs ajenos. **B2 sigue sin lanzar.**
- El deck **no se puede presentar como está**: sin guion.

---

## Sesión 21 — 22-ago-2026 · sesión de PLAN: el deck del lunes, especificado y sin escribir

Sesión **de planificación**, cerrada a pedido de Ernesto para que una sesión limpia ejecute.
**Cero código, cero GPU, cero láminas tocadas.** Lo que produjo es el plan completo de la
actualización del deck para la reunión del **lunes 24-ago**, en
`sprints/B8_sprint8/presentacion_b8/plan_actualizacion_24ago.md`.

### 1. La restricción que ordenó todo el plan

**No entra ningún resultado nuevo.** B3 (5069) y B1 (5070) siguen `PD` detrás del
`llm_labeller` de `gvenegas` (`TimeLimit=UNLIMITED`, 11 h 40 al cierre) y B2 nunca se lanzó.
Verificado que `results/b8_hovernext_12laminas/hovernext/lizard_mitosis/<slide>/` está
**vacío en las 11 láminas**: el job creó los directorios y no escribió nada.

⇒ El deck se arma **solo con lo que ya está medido en disco**, o sea la Fase A entera.

### 2. Las cuatro decisiones de Ernesto sobre el plan

| decisión | qué implica |
|---|---|
| **la necrosis queda FUERA** | el encargo 3 pide comparar la necrosis de HoVer-NeXt contra las marcas, y esa mitad exige `dead` (solo PanNuke = B2, sin lanzar). **A4 no se presenta**: sin la mitad del detector contesta otra pregunta |
| **fecha 24-ago-2026** | `correcciones.txt` decía 22; la reunión es el lunes |
| **los objetivos reemplazan la lámina de título** | `TPL_KEEP` pasa de `(0,1)` a `(0,)` y la posición 2 la ocupa una lámina nuestra con el molde de la ex-13 |
| **solo material ya medido** | nada de esperar a B1/B2/B3 |

### 3. El deck queda en 17 láminas

16 − 3 (se van `lam_simil_ramas`, `lam_simil_reporte`, y `lam_objetivos_propuestos` se muda a
la posición 2) + **4 nuevas**, todas con datos en disco:

| nueva | fuente | forma |
|---|---|---|
| CLAM, Mammoth y el detector a igual carga | A2.bis §2-§3 | tabla nativa |
| El checkpoint de carcinoma invasivo | A2 §2-§4 | dos bloques + tabla nativa |
| Las 13 que se escapan sí estaban segmentadas | A0 | tabla nativa (control positivo P3) |
| Las 164 detecciones sin marca | A1 | láminas de contacto (excepción legítima a «todo nativo») |

Más **13 correcciones de forma** sobre las láminas que quedan, y el guion entero reescrito de
**9131 palabras (~70 min) a ~4500 (~35 min)**, que es el pedido transversal de Ernesto.

### 4. Los dos datos que hubo que verificar contra el código, y no estaban escritos

- **Ernesto atribuyó a HoVer-NeXt las 246 dimensiones, que son de SI-MIL.** HoVer-Net es el
  **front-end de SI-MIL** (`papers_b8.md:87`) y de su mapa de núcleos salen las 246 mediciones
  por parche (`simil_estudio.md:40`). HoVer-NeXt no tiene nada de eso.
- **Las dimensiones reales de HoVer-NeXt**, verificadas contra
  `hover_next_reference/lizard_convnextv2_tiny/params.toml` y `src/inference.py:249-250`:
  codificador **ConvNeXtV2-tiny**, decodificador de instancia **5 canales** (2 de regresión +
  3 clases: fondo / interior / borde) y decodificador de clase **8 canales** (fondo + las 7 de
  Lizard-Mitosis). Eso es lo que hace legible el `(n_tiles, 8, 256, 256)` del `_cls.zip`.
- **Las 4 clases de tasa mitótica**, contadas sobre
  `environ/csv/dataset_grado_histologico_tasa_mitotica_label.csv`: `no_identificado` (693),
  `score_1` (636), `score_2` (287), `score_3` (254).

### 5. Estado al cierre

Rama `main`, sincronizada con `origin`. **5069 y 5070 siguen `PD`**; el nodo lo tiene
`gvenegas` 5064 con `UNLIMITED`, y delante de los nuestros hay tres jobs ajenos de otro
operador (5066/5067/5068). **B2 sigue sin lanzar.** Nada de la Fase B se movió.

---

## Sesión 20 — 22-ago-2026 · Fase A CERRADA (A2.bis, A4) y Fase B encolada (B3, B1)

Cierra la Fase A entera y pone dos de los tres jobs de la Fase B en la cola. **Cero
resultados de GPU todavía**: la GPU está tomada y los dos jobs propios quedaron `PD`.

### 1. A2.bis — la escalera de brazos, en la unidad de la pregunta

`a2bis_escalera_brazos.md` · `scripts/escalera_brazos.py` ·
`results/b8_hovernext_129741/{escalera_brazos,escalera_brazos_gate}/`

Contesta la pregunta de Ernesto (¿el detector agrega algo sobre la atención sola?)
comparando **a carga fija**, no a K fijo. Chequeo de sanidad: **cierra en las dos tareas**
(atención → 26/26, HoVer-NeXt → 13/26, azar converge).

Objetos para llegar al mismo recall, CDIS fold 4, denominador **26 marcas**:

| llegar a | CLAM | Mammoth | CLAM∩Mam | CLAM∪Mam | HoVer-NeXt solo |
|---|---|---|---|---|---|
| 8/26 | 71 parches | 70 | **33** | 80 | — |
| **13/26** | 130 | 95 | **84** | 126 | **82 núcleos** |
| 19/26 | 300 | **217** | 241 | 251 | imposible |
| 26/26 | 2496 | 2496 | 2496 | 2496 | imposible |

Tres cosas que **solo aparecen con este eje**:

- **La unión nunca es el mejor brazo.** A K fijo parecía el mejor de todos (24/26 en
  K=300); a carga fija queda igual que CLAM y por debajo de Mammoth. Su ventaja era **el
  tamaño de la máscara**, no la calidad del ranking.
- **La intersección es el brazo más eficiente** hasta ~16/26: la mitad de parches que
  cualquiera de los dos solos.
- **HoVer-NeXt está TOPADO en 13/26** a cualquier carga; la atención sola llega a 26/26.
  Por debajo de 13/26 piden objetos comparables; por encima, el detector no es opción.

**Y la advertencia que gobierna el eje de área**: el área de un núcleo es una **convención**
(ventana de inspección), no una medida. El «6,3× menos área» se da vuelta a **0,7×** con una
ventana de 384 px. **El eje de objetos no depende de nada** y es el que sostiene las
conclusiones. Sensibilidad completa en el §4 del documento.

El gate pide **2,5 a 4 veces más carga** que CDIS para el mismo recall, y en K=100 queda **al
nivel del azar** (1,0/26 contra 1,0/26 esperado por sorteo). Si eso es la tarea o el brazo lo
separa B3.

### 2. A4 — encargo 3, mitad CLAM: la atención de necrosis

`a4_atencion_necrosis.md` · `interp_slides_necrosis.json` ·
`results/b8_hovernext_129741/{interp/carcinoma_ductal_insitu_necrosis,auc_necrosis_f0}/`

Rama verdadera (`presente_central`): **AUC 0,899** (IC 0,804–0,995), percentil mediano
**96,8 %**, nulo por **traslación rígida** p = **0,0005**. Específica: necrosis primera y
separada, con Tejido Adiposo en 0,088 (la atención lo **evita**).

**La rama que se lee decide todo**: la rama que el modelo **predijo** (`ausente`) da **0,500
exacto**, el azar. `sgaete` midió sobre la predicha y obtuvo 0,382. **Queda pendiente
preguntarle si es deliberado**, y éste es el número a mostrarle.

**Hallazgo que no esperábamos:** el modelo **se equivoca de clase** en esta lámina (predice
`ausente`, la verdad es `presente_central`) y su cabeza de `presente_central` **igual localiza**
la necrosis en el percentil 96,8. **Localización y decisión se disocian.**

**Aviso que va antes de cualquier número:** el modelo es **débil** (train 45 / val 7 / test 9,
test_auc 0,557, test_acc 0,222, colapsa en 8 de 9). No se afirma que sirva.

De paso: el `label_dict` hardcodeado de `clam_environ/main.py:157-161` está **stale** (sus
strings no existen en el CSV); la corrida usó `--auto-label-dict`, y el mapeo real se confirmó
por dos vías independientes.

### 3. B3 — pre-registrado, revisado y ENCOLADO (job 5069)

`prereg_gate_invasivo.md` · `scripts/run_b3_gate_clam_fold0.slurm`

Regla 9 cumplida en orden: pre-registro → `reviewer` → commit → `sbatch`. El `reviewer`
**aprobó con observaciones** y las tres están aplicadas.

**Lo que el `reviewer` encontró y yo había afirmado de más:** `clam_testing/main.py` tiene
**mtime 15-jul 18:07** y el comparador corrió **09:12–13:25 del mismo día**, o sea que el
entrypoint **no es demostrablemente el mismo**. El §3 ahora lo declara con los tres datos que
acotan el riesgo (los dirs `_ci` creados a las 18:01 ⇒ edición aditiva sobre `TASK_CONFIGS`;
las claves de `settings` idénticas a las serializadas; el `csv_path` igual) y queda como
**riesgo 4** en vez de darse por resuelto. `core_utils.py` (28-may) y `model_clam.py` (4-jun)
**sí** son anteriores: **el bucle de entrenamiento está limpio**.

Comparador recomputado desde el `.pkl`: Mammoth fold 0 → **bal_acc 0,9194 · AUC 0,9681**,
confusión [[188,12],[8,71]], test n=279 (200/79). Descriptor **en sync** con el join (regla 10).

Además: guard que **aborta si el directorio de resultados existe** (una re-corrida
**concatena** los `probability_logs` sin avisar, `core_utils.py:157-168`).

### 4. B1 — encolado (job 5070)

`scripts/run_hovernext_slides.slurm`. Las **11** láminas restantes en **un solo job** (un token
de GPU), reanudable por una marca `.done` que se escribe **después** de que `main.py` salga 0.
**Sin `--keep_raw`**: ~142 MB por lámina en vez de ~10,5 GB.

**Presupuesto medido, no a ojo:** 18 min y 3199 Mpx de la 129741 contra 17,3 Gpx de las 11 =
**~103 min**. Las 12 comparten que **no exponen `thumbnail`**, así que las 12 teselan el lienzo
entero y la extrapolación es apples-to-apples. `--time=5:00:00`.

**Preflight corrido en CPU sobre las 11: 11/11 OK**, driver `ventana` con mpp 0,465 en todas
(workaround M verificado, ninguna cae a `generic-tiff`).

Eso obligó a tocar `preflight_hovernext.py` dos veces, y las dos son lecciones:

- Trataba `keep_raw=0` como **falla incondicional**. Ese guard protegía contra **olvidarse** el
  flag, no contra **elegirlo**: ahora hace falta `--sin-raw-a-proposito` para bajarlo a aviso.
- Su chequeo de GPU **fallaba duro cuando la GPU estaba llena**. En un barrido eso es peor que
  inútil: un job que esperó días en cola se saltaría **las 11** y saldría en blanco. Ahora
  distingue «no hay GPU» (falla) de «está llena ahora» (aviso, transitorio).

### 5. Estado al cierre

Rama `main`. **Jobs propios: 5069 (B3) y 5070 (B1), los dos `PD (Priority)`.** El nodo lo tiene
`gvenegas` 5064 con `TimeLimit=UNLIMITED`, y delante van `sdonoso` 5066/5067/5068 (de **otro
operador**, `WorkDir=Test_D/`, verificado con `scontrol` — workaround L.b). Con dos `UNLIMITED`
en juego no hay backfill y `StartTime` sale `Unknown`: **puede ser días**.

**B2 NO se lanzó.** El script quedó listo y verificado (los 3 pesos de PanNuke cargan,
preflight OK con el ensemble), pero sin `sbatch`.

## Sesión 19 — 21-ago-2026 · A3: los 12 offsets, y dos bugs que la 129741 no disparaba

> Sesión corta, cerrada a pedido de Ernesto para que una sesión limpia siga con la Fase B.
> Se ejecutó **A3 entero** (CPU). **Nada de la Fase B se lanzó**: B3 sigue sin pre-registro y
> sin pasar por `reviewer`, y no hubo un solo `sbatch`. Doc:
> `sprints/B8_sprint8/encargos_sebastian/a3_offsets_11_laminas.md`.

### 1. A3 — las 94 marcas de las 12 láminas caen sobre un parche

`scripts/run_a3_offsets.sh` · `scripts/a3_denominador_mitosis.py` ·
`sprints/B8_sprint8/anotaciones_patologo/{offset_*.json,parches_anotados_*.csv,denominador_mitosis_12.json}`

Derivados los offsets de las **11** que faltaban. En **las 12** el offset adoptado es la
**geometría del contenedor** (`dx = level0.width − region[0].width`, `dy = 0`), y donde los
barridos empíricos (a) y (b) no se cruzan (124729, 164001, B25-158899, 109609) el geométrico
**les gana a los dos** — el «revisar a mano» que imprime el script es el barrido quedándose
corto, no un caso abierto.

**Techo del filtro (P2.a): 94 de 94 marcas de `Mitosis` sobre parche extraído.** La alineación
**no acota** B1 ⇒ el denominador honesto sigue siendo el agregado de 94, con la tabla por
lámina y su `n`. Un techo alto no promete nada: no dice cuántas va a recuperar el detector.

**Y_CORTE_REGION**: solo **2 de las 12** tienen dos regiones de escaneo — 129741 (49920, ya en
uso) y **B25-158899 (30720)**; las otras 10 se saltan el confinamiento. La constante de módulo
de `techo_atencion_topk.py:45` **sigue sin generalizar** — el valor por lámina está en el doc,
el cambio de código no se hizo.

### 2. Dos bugs que habrían corrompido B1 en silencio

- **`patch_size_desde_coords` daba 64 o 128 en 9 de 12 láminas** (el paso real es 256 en las
  12). Tomaba la moda sobre el `np.unique` **global** de cada eje, y CLAM arranca la grilla en
  el bbox de cada contorno ⇒ el unique global mezcla los desfases entre islas con el paso.
  La 129741 daba 256 **por casualidad**, y por eso sobrevivió desde el 31-jul. Corregido a la
  moda **por fila/columna**, que es la forma que ya usaban los otros cuatro scripts.
- **QuPath deja anotaciones sin clase** (2 en las 12: 126504 y 106552, tamaño de núcleo). El
  script crasheaba al formatear `None`. Se conservan como `(sin clase)` y **no** entran al
  denominador de Mitosis.

**Regresión**: la 129741 reproduce `parches_anotados_129741.csv` **byte a byte** y su
`dx=3829` no se movió.

### 3. El gate de alineación mide otra cosa que la que B1 necesita

El chequeo del script («≥80 % de **todas** las anotaciones sobre tejido») deja fuera a
**B25-158899 (27/38)** y **164001 (23/30)**. Medido sobre la unidad de la pregunta —
**las marcas de Mitosis** — las dos dan **6/6** y **3/3**. Lo que se cae son polígonos grandes
(`Negative`, `Tejido Adiposo`, `Tumor`) cuyo centroide queda sobre fondo. **110616 lo cierra**:
30/30 por «cae sobre parche» y 24/30 por «cae sobre tejido» — el offset ubica todas y la
máscara de saturación es la que pierde seis. Registrado como ADDENDUM de
[[techo-filtro-antes-de-correr]]: el techo se mide en la **unidad del resultado**, o el gate
rechaza material sano.

### 4. Estado al cierre

Rama `main`, **sin jobs propios**, working tree limpio salvo
`presentacion_b8/correcciones.txt` (sin trackear por decisión de Ernesto). El nodo lo ocupan
`sgaete` 5052 (`phase3_s`, 12 h) y `capstone` 5065, con `nschiaff` 5061 y `gvenegas` 5064 en
cola. Pendientes de la Fase A: **A2.bis** y **A4**. Fase B entera sin arrancar.

---

## Sesión 18 — 21-ago-2026 · se ejecuta la Fase A: A0, A1 y A2

> La sesión 17 dejó el plan escrito y sin correr nada. Ésta ejecutó las tres primeras piezas de
> la Fase A, todas en CPU y sin tocar la cola de la GPU. Docs bajo
> `sprints/B8_sprint8/encargos_sebastian/`.

### 1. A0 (camino crítico) — las 13 que se escapan estaban segmentadas

`a0_segmentadas_o_no.md` · `scripts/a0_segmentadas_o_no.py` ·
`results/b8_hovernext_129741/a0_falladas/`

**13 de 13** de las marcas falladas tienen un núcleo segmentado **encima** (mediana 2,1 µm del
centroide de la marca, máximo 6,7 µm, sobre marcas de 16,7 µm de lado). **Cero** fallos de
segmentación. **12 recibieron `epithelial-cell` y 1 `neutrophil`**, y ninguna tiene una
instancia de clase `mitosis` a 15 µm a la redonda.

Control positivo (patrón P3): las 13 acreditadas salen **indistinguibles** en distancia,
densidad de núcleos y tamaño de marca — la única variable que separa los grupos es la clase.

⇒ **El arreglo es la cabeza de clase, no la segmentación**, y la etapa cara ya está pagada con
su salida en disco. Queda descartado tocar segmentación, cambiar de modelo de instancias o
re-correr HoVer-NeXt para el eje de mitosis.

**Abierto**: si `mitosis` quedó **segunda por poco** (se arregla con umbral) o no aparece (hay
que reentrenar). Exige las probabilidades por instancia, que viven **por tesela** en
`*_raw_256_cls.zip` y obligan a reconstruir la grilla.

### 2. A1 — encargo 2: la galería de las 177

`a1_galeria_177.md` · `scripts/galeria_mitosis_129741.py` ·
`results/b8_hovernext_129741/galeria_mitosis/`

Tres láminas de contacto a resolución nativa (ventana 128 px = 59,5 µm): **164** sin marca,
**13** acertadas, **13** marcas que se escapan. **164 + 13 = 177**, la verificación del plan,
cierra contra `pred_mitosis.tsv`.

**Sí se parecen**: cortando el dendrograma en cuatro, **145 de las 164 (88 %) caen en una sola
familia** — epitelio denso, 2 % de fondo. Se despega una familia de **15** recortes claros con
**65 % de fondo** (tejido laxo o borde), más 4 sueltos.

### 3. A2 — encargo 1, brazo de hoy: la atención del gate de invasivo

`a2_atencion_gate_invasivo.md` · `interp_slides_gate.json` ·
`results/b8_hovernext_129741/{auc_gate_f0,techo_atencion_gate,cruce_marcas_gate}/`

Fold 0 (donde la 129741 cae en test), leyendo la rama de la clase verdadera `invasivo` y
registrando la predicha — **coinciden**, el modelo acierta con p = 1,000, así que acá la
elección de rama no cambia nada.

| | AUC Mitosis | percentil med. | top-50 | top-300 |
|---|---|---|---|---|
| gate · Mammoth | 0,865 (0,778–0,951) | **86** | **0/26** | **11/26** |
| CDIS · Mammoth | 0,919 (0,848–0,989) | 95 | 4/26 | 22/26 |
| CDIS · CLAM | 0,876 (0,793–0,960) | 94 | 2/26 | 19/26 |

**Patrón P2 de manual**: los tres AUC se solapan y los top-K son radicalmente distintos. El
aporte nuevo respecto del caso del 14-ago es el simétrico — **el AUC tampoco sirve para
comparar dos candidatos a filtro**. Chequeo de sanidad: en K=2496 los dos convergen a 13/26.

**Media respuesta**: con un solo brazo en el gate no se puede separar si el recorte peor es de
**la tarea** o del **brazo**. Lo separa B3.

### 4. Estado al cierre

Rama `main`, **sin jobs propios**; el nodo lo ocupan `sgaete` 5052 (`phase3_s`, 11 h 28) y
`capstone` 5065, con `nschiaff` 5061 y `gvenegas` 5064 en cola. **Nada de la Fase B se lanzó**:
B3 sigue sin pre-registro y sin pasar por `reviewer`. Pendientes de la Fase A: **A2.bis** (la
escalera de brazos), **A3** (offsets de las 11) y **A4** (atención de necrosis).
