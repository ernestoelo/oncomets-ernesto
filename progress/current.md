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

## Sprint actual: B7 / Sprint 7 — Interpretabilidad CLAM vs Mammoth + ¿cuántos expertos/slots?

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
- **Pendiente del deck**: **QA fino en PowerPoint** (el OMML de los diagramas se ve roto en
  LibreOffice pero OK en PowerPoint, [[pptx-qa-omml-libreoffice]]). Mirar de paso el título
  de la lámina 16: parte en dos líneas y roza la banda del encabezado.
- **Inventario lámina por lámina de las 21** + agenda de reunión + qué no afirmar:
  `sprints/B7_sprint7/guia_estudio_b7.md` (punto de reentrada al sprint,
  [[guia-reentrada-al-cerrar-sprint]]).

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
