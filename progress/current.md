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
- **Pendiente real (actualizado):** (1) **inspeccionar read-only `environ/*_ci*`** (splits/CSVs que dejó
  Sebastián) antes de generar nada + darle observaciones; (2) verificar `patch_size_level0:512` del meta de
  interp. invasión (SB6); (3) ubicar el código del gate. *(Las clases de `tipo_histologico` y la decisión de
  splits ya NO son pendiente — confirmadas 15-jul.)*

### Deck (correcciones para la próxima presentación, la verá también Benjamín)

- Migrar al **template de Sebastián** (`sprints/B7_sprint7/*.pptx`) + añadir slide de
  **recap de objetivos** (layout de `Plantilla.pptx`). Enfoque de migración = decisión
  pendiente con Ernesto (re-basar vs replicar branding).
- Correcciones §2: slide 7 (rastro de X, subíndices s,e, MoE-vs-PoE en el hilo), slides
  10-11 (caveat honestidad + IDs de slides), slide nueva cabezas/expertos/slots (§2.4),
  slide matemática de magnificación (§3), estilo duro (cero «—», 3ª persona sin nombres,
  sin diálogos, sin «palanca»). Checklist: `sprints/B7_sprint7/correcciones_deck.md`.

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
- ✅ `/knowledge-audit` 15-jul PM (esta sesión): corregida nota "Pendiente" stale que indujo re-pedir paths
  de magnif ya enviados; registrado el resultado del gate; nueva memoria de prevención
  [[verificar-antes-de-pedir-dato]]. Detalle: `auditoria_coherencia/hallazgos_sesion_magnif_paths_15jul.md`.

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
