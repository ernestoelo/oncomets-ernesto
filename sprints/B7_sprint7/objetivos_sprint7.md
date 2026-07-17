# Sprint 7 (B7) — Objetivos acordados con Sebastián (reunión 13-jul-2026)

> Abierto 13-jul-2026 tras presentar el deck B6 a Sebastián (salió bien). Los objetivos
> los fijó Sebastián en esa reunión; Ernesto los trajo como contexto. Este doc los
> registra con el molde del proyecto (tarea · baseline · variable · métrica · gobernanza)
> y marca lo que hay que verificar antes de ejecutar. Equipo = Ernesto + Sebastián.
> Reunión de seguimiento: **miércoles** (cuántos expertos/slots hacen falta).

---

## Headline

Comparar los **mapas de calor / atención de CLAM vs Mammoth** en varias tareas y
responder la pregunta central: **¿cuántos expertos y cuántos slots necesitamos para
todas las tareas?** Es un eje de **interpretabilidad / entendimiento** (ortogonal al de
rendimiento, que está cerrado: mammoth 0 palancas, Hallazgo 12). No reabre el veredicto
de arquitectura.

## Tareas a evaluar (3)

| # | Nombre reunión | Task real (`main.py` TASK_CONFIGS) | n_clases |
|---|---|---|---|
| 1 | Tipo histológico | `tipo_histologico` (/ `_combined` / `_pth`) | multiclase |
| 2 | CDIS presente | `carcinoma_ductal_insitu_presente` (/ `_combined` / `_pth` / `_pth_balance`) | binaria |
| 3 | Invasión linfovascular | `invasion_linfatica_vascular` (/ `_combined` / `_pth` / `_pth_balance`) | 3 clases {ausente, no_identificado, presente} |

> Nota: la "cdis" de los checkpoints obj6 es **microcalcificaciones_en_cdis** (microcalc
> en tejido CDIS), que **NO es** `carcinoma_ductal_insitu_presente`. Son tareas distintas.

## Requisito de documentación por tarea (Sebastián — es obligatorio, no opcional)

Por **cada** tarea, dejar registrado con claridad:

- **Qué slides** se usaron (IDs concretos).
- A qué **magnificación** se trabajó (µm/px físicos, no solo `level`; ver
  `contexto_magnificacion.md` y [[cohortes-magnificacion-fisica]]).
- Qué **dataset** (privado / TCGA / HistAI / combinado; cohorte y n).
- Qué decía la **etiqueta del patólogo** de esa slide (de `meta.json` / CSV de labels).

Este bloque se llenará al generar los heatmaps (una tabla por tarea con esas 4 columnas
+ el slide_id).

## Análisis pedido

1. **Expertos por zona:** por tarea, qué expertos se activan en qué zonas de la WSI
   (heatmaps de ruteo por experto — ya lo hace `mammoth_interpretability.py`).
2. **Consecuencia de los expertos:** si un mismo experto es **consecuente** con el
   contenido que ve **a través de distintas tareas y slides** (mismo experto → mismo
   patrón morfológico, label-independiente). Es la evidencia del Hallazgo 12.
3. **Peso de los slots en el ruteo (NUEVO):** rankear los **300 slots (E·S)** por su peso
   de ruteo para identificar los más activados / importantes ("los más parecidos").
   ⚠️ **Esto NO es el top-k de parches por experto que ya existe** — es un análisis nuevo
   sobre la dimensión de slots (usa `combine_weights`, softmax sobre los 300 slots). Ver
   `preguntas_resueltas.md` §Q1 para el mecanismo exacto y la decisión dispatch-vs-combine.
4. **Pregunta central para el miércoles:** ¿cuántos expertos (E) y cuántos slots (S)
   hacen falta para todas las tareas? El propio paper marca el E/S/H fijo como
   **limitación** y propone elegirlos dinámicamente como trabajo futuro
   (`respuestas_preguntas_benjamin.md` §Q5). La vía honesta = ablación de E/S/H paired +
   interpretabilidad (¿más expertos/slots se especializan más o se vuelven redundantes?).

## Molde por objetivo

| Aspecto | Definición |
|---|---|
| Tarea(s) | las 3 de arriba |
| Baseline | CLAM (mapa de atención) por tarea |
| Variable de estudio | Mammoth (mapas de ruteo por experto + peso de slots) vs CLAM |
| Métrica / entregable | figuras comparadas CLAM-atención vs Mammoth-expertos + tabla slides/magnif/dataset/label por tarea + `slot_usage.csv` (ranking de slots) + lectura de consecuencia cross-slide/cross-task |
| Gobernanza | análisis **post-hoc CPU** (`CUDA_VISIBLE_DEVICES=""`, workaround B) sobre checkpoints congelados → regla 9 NO se dispara para la extracción. **Entrenar** un checkpoint mammoth que falte = GPU = gate d/b + regla 9 + reviewer |

## Factibilidad de checkpoints (verificado 13-jul — LOAD-BEARING, a resolver con Ernesto)

La comparación CLAM-vs-Mammoth necesita, por tarea, un checkpoint **CLAM** y uno
**Mammoth** (`CLAM_MB_Mammoth`, prefijo `attention_net.0.mammoth.`). Estado hoy:

| Tarea | Checkpoint Mammoth (nuestro) | Checkpoint CLAM | ¿Ejecutable CPU ya? |
|---|---|---|---|
| `invasion_linfatica_vascular_pth` | **SÍ** — `results/obj2_mammoth/…` (f0-f4, `clam_mammoth_*`) + `results/obj3_mammoth_keepslots/…` (`kst_*`) | SÍ (`results/obj2_mammoth/…/clam_*`) | **SÍ** |
| `tipo_histologico` | **NO** (no hay mammoth en `results/`) | eval de Sebastián existe (`clam_environ/environ/results_eval/EVAL_tipo_histologico*`, read-only) + `heatmap_production/tipo_histologico` | **NO** sin entrenar mammoth |
| `carcinoma_ductal_insitu_presente` | **NO** | baseline de Sebastián (`clam_environ/environ/results_modelo_pth/carcinoma_ductal_insitu_presente_pth_s1`, read-only) | **NO** sin entrenar mammoth |

**Implicación:** solo **invasión linfovascular** se puede correr en CPU **ahora**. Para
tipo histológico y CDIS presente, generar los mapas de expertos de Mammoth exige
**entrenar mammoth** en esas 2 tasks → **GPU = gate d/b + regla 9 + reviewer** (no en
esta sesión sin OK). Opciones a decidir con Ernesto:

- (A) arrancar el sprint con **invasión linfovascular** (CPU, ya) + preparar el `.slurm`
  paired para entrenar mammoth en las otras 2 (sin lanzar) para el próximo fin de semana;
- (B) confirmar con Sebastián si él tiene checkpoints mammoth de esas 2 tasks reusables;
- (C) reformular el alcance (p.ej. usar tasks con checkpoint mammoth ya disponible).

**Decisión (13-jul): opción A.** Ejecutado: (1) corrida CPU de invasión hecha
(`interpretabilidad_invasion/TCGA-AR-A24L_invasion_f0/`, 563 s / 10 401 parches); (2)
`.slurm` DRAFT preparado (`run_b7_mammoth_interp_kfold.slurm`, **NO lanzado**). ⚠️ El slurm
tiene **3 prerequisitos que hoy bloquean** el sbatch (documentados en su header):
- **A. Formulación** de cada tarea (n_classes, label_dict, cohorte) — decisión de
  Ernesto/Sebastián + regla 9. `carcinoma_ductal_insitu_presente` {no:636, no_id:1369,
  si:810} → ¿binaria excluyendo no_identificado o 3-clase? `tipo_histologico` → usar la
  versión limpia `_4clases` {no_especifico:766, lobulillar:183, no_id:366, otros:81}.
- **B. Splits + CSV** para estas 2 tareas **NO existen** en `data/splits_kfold/` ni
  `data/csv_new_tasks/` → hay que generarlos (paso CPU, pero data-pipeline → pre-registrar).
- **C. Reviewer (regla 9) + OK de Ernesto** antes del sbatch (gate d/b).

> **ADDENDUM 16-jul — prereqs A y B RESUELTOS (formulación confirmada + splits `_ci` de Sebastián a reusar).**
> - **A (formulación):** confirmada por Sebastián (cascada, sin `no_identificado` en la multiclase). Distribuciones
>   REALES de los artefactos `_ci` (superseden los números tentativos de arriba, que venían del CSV viejo `_4clases`):
>   `tipo_histologico` = **3 clases** {no_especifico:1610, lobulillar:240, otros:177}, n=2027 (drop no_id + subtipos
>   raros→`otros`); `carcinoma_ductal_insitu_presente` = **binaria** {no:2005, si:810}, n=2815; `invasion_linfatica_vascular`
>   = **binaria** {ausente:2447, presente:368}, n=2815 (**ya NO** las "3 clases {ausente, no_identificado, presente}"
>   de la tabla de arriba). ⚠ En las **binarias** `no_identificado` quedó **plegado en el negativo** (no descartado):
>   CDIS no=2005=636+1369; invasión ausente=2447=479+1968 → observación abierta a Sebastián (re-infla la mayoritaria).
> - **B (splits+CSV):** **ya NO hay que generarlos.** Sebastián dejó la suite en `environ/csv_balance_ci/` +
>   `environ/splits_5fold_balance_ci/<task>_ci_100/` (5-fold estratificado, cross-check regla 10 limpio). **Decisión
>   (Ernesto, 16-jul): REUSAR los `_ci`** → el `.slurm` apunta a `environ/splits_5fold_balance_ci/<task>_ci_100` (paired).
> - **Blocker previo al sbatch:** `histai_1132_slide_H&E_0` está en los splits de CDIS/invasión **sin features CONCH**
>   → preflight de presencia de `.pt` (workaround G) o sacarlo del CSV/split. **C (reviewer + OK)** sigue en pie.
> - Detalle: `auditoria_coherencia/hallazgos_sesion_ci_inspeccion_16jul.md` (C1-C7), [[formulacion-cascada-gate-invasivo]].

> **ADDENDUM 17-jul — Sebastián REFORMULÓ CDIS y LVI (el plegado del `_ci` queda superseded).** Al plantearle el
> plegado de no_id, Sebastián lo confirmó primero y luego se retractó: para CDIS y LVI ahora es **descartar no_id +
> restringir a las WSI invasivas, solo casos explícitos** (evita que el modelo aprenda invasión/no-invasión en vez
> de la tarea). `tipo_histologico` sin cambios (3 clases, `_ci` válido). Números nuevos (verificados con
> `csv_balance/dataset_invasion_carcinoma_gate_label.csv` = {invasivo:2013}): **CDIS {no:132, si:730} n=862 (85%
> positivo, desbalance dado vuelta)**; **LVI {ausente:470, presente:366} n=836 (balanceado)**. El slide `histai_1132`
> (blocker previo) es no-invasivo → se excluye solo; conjuntos nuevos 100% con features. **`_ci` de CDIS/LVI ya NO
> se reusan** (los de tipo sí); regenerar CSV+splits con la formulación nueva (data-pipeline → regla 9 + reviewer).
> **✅ Sebastián RESPONDIÓ (17-jul 16:04-16:05):** acepta el CDIS 85% positivo **sin ajuste** ("Perfecto") y **nos
> deja regenerar los splits** ("Si puedes, dale no más"). → generar CSV+splits de CDIS/LVI queda de nuestro lado
> (data-pipeline → regla 9 + reviewer + OK). Números re-verificados en disco esta sesión (regla 5): CDIS {no:132,
> si:730}, LVI {ausente:470, presente:366}, **0 slides sin `.pt`, 0 duplicados, 0 fuga de paciente** (`patient_strat`).
> Detalle: `auditoria_coherencia/hallazgos_sesion_reformulacion_sebastian_17jul.md` (R1-R5).

## Gobernanza y reglas que aplican

- **Post-hoc CPU** para extracción (Etapa 0, sin GPU, sin reviewer). Entrenar = GPU gate.
- **Comparación paired** por reuso de splits donde haya baseline ([[patron-paired-comparison-reuso-splits]]).
- **Reportar SIEMPRE balanced_acc Y AUC** si se reporta rendimiento (política eval B5) —
  aunque este sprint es de interpretabilidad, no de métricas.
- **Caveat de honestidad (crítico, de cara a Benjamín):** los nombres de tejido de los
  expertos (e8 epitelio, e26 estroma, e3 ductal) son **lectura visual nuestra, NO
  anotación de patólogo**. Tenemos la etiqueta clínica de slide, no anotación por parche.
  El argumento morfología≠clase es **label-independiente**. Sign-off de patólogo
  pendiente. [[mammoth-interpretabilidad-objA]] ADDENDUM 13-jul, [[feedback-benjamin-entender-mammoth]].

## Guía para Sebastián (replicar la extracción de heatmaps)

Sebastián quiere replicar la extracción de los mapas de expertos para estudiarla. Guía
canónica escrita en `sprints/B5_sprint5/mammoth_entendimiento/interpretabilidad/README.md`
(dónde está el deck + las figuras + cómo generarlas en CPU + timing real 563 s / ~9.4 min
para 10 401 parches + caveat de honestidad + la extensión de peso de slots de B7).

## Preguntas abiertas resueltas esta sesión

- §6.1 (terminología "top-k" de slots) → `preguntas_resueltas.md` §Q1.
- §6.2 (matemática de magnificación) → `contexto_magnificacion.md`.
- §6.3 (16 cabezas ↔ 30 expertos ↔ slots) → `preguntas_resueltas.md` §Q3.
