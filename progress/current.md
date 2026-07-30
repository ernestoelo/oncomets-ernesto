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
