# progress/current.md

> Estado vivo del sprint actual. Es un **snapshot** — se reemplaza al avanzar
> el sprint. Al cerrar el sprint, el resumen pasa a `history.md`.
>
> **Roll-over 6-jul-2026 (sesión Fable):** B5 cerrado y movido a `history.md`
> (deck entregado, trimestre cerrado, Ernesto continúa). Este archivo arranca B6.

---

## Sprint actual: B6 / Sprint 6 — Magnificación multi-escala (CONCH) sobre CLAM

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
   cohorte, fusión promedio, hipótesis H1/H0/H2, eval bal_acc+AUC. **Self-review inline regla-9 OK**
   (`review_regla9.md`); **pase formal del reviewer PENDIENTE** (se cortó por límite de API).
4. ✅ **Wrapper + `.slurm` listos** (NO lanzados): `scripts/extract_multiscale_features.py`
   (bug openslide+workers corregido), `extract_multiscale.slurm` (preflight + stage1 patching +
   stage2 extracción B0/B), `microcalc_slidelist_tcga_privado.csv` (283 slides).
5. **PENDIENTE antes de lanzar:** (a) pase formal del reviewer, (b) co-firma de Sebastián sobre las
   escalas (lunes), (c) dry-run CPU de stage-1 create_patches (esquema del process_list), (d) OK de
   Ernesto para `sbatch`. Luego stage-3 CLAM paired reusando splits.

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
