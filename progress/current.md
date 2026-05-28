# progress/current.md

> Estado vivo del sprint actual. Es un **snapshot** — se reemplaza al avanzar
> el sprint. Al cerrar el sprint, el resumen pasa a `history.md`.

---

## Sprint actual: B4 / Sprint 4

**Snapshot: 28 may 2026 (post chain Obj 5 + ANEXO DSMIL × binarias)**
(Objetivos 1-3 completados; reformulación 3 binarios validada; **Objetivo 5
COMPLETADO + ANEXO** — chain SLURM 4170→4171→4172 ✅, **job anexo 4179 ✅**
(DSMIL × binarias × k=5, cierre simétrico arquitectónico). Veredicto §2.2 =
**banda ambigua** para DSMIL sobre fusionado; veredicto anexo = **NULL en
2/3 binarias (carcinoma, tejido) + regresión leve en CDIS (5/5 folds Δ
negativo)**. Cuadro arquitectónico cerrado simétricamente. Slides 1-13
listas (anexo en 11-12). Objetivo 4 (heatmaps) pendiente.)

### Estado por objetivo

- **Objetivo 1 — Baseline CLAM reproducible**: **COMPLETADO**.
  Job `4098` (B=8, `microcalcificaciones_pth`, split `minpatch16`) terminó
  COMPLETED. Resultados y análisis completos en
  `sprints/B4_sprint4/objetivo_1_baseline/resultados.md`.
  **Hallazgo central**: el régimen de evaluación de la task NO es confiable
  (ver abajo). Métricas: test_auc 0.81 (ruidoso), val_auc 0.69, test_acc 0.72,
  **balanced accuracy 0.31**.
- **Objetivo 2 — Ablation B=8 vs B=16**: **COMPLETADO**.
  Job `4099` (B=16) terminó COMPLETED. **Veredicto: hipótesis NO confirmada.**
  Δtest_auc +0.009 (umbral predefinido era +0.03 → banda ambigua); balanced
  accuracy *bajó* 0.31→0.24; train_clustering_loss *subió* 0.0089→0.0126
  (contradice el mecanismo de la hipótesis). **Conclusión de fondo**: `B` es
  un hiperparámetro — ajustarlo no mueve la aguja porque el cuello de botella
  es la **FORMULACIÓN** de la tarea, no los hiperparámetros. La ablación
  negativa es la evidencia que justifica la reformulación. Detalle:
  `sprints/B4_sprint4/objetivo_2_ablation_B/resultados.md`.
- **Objetivo 3 — Módulo MIL alternativo (propuesta DSMIL)**: **INVESTIGACIÓN
  COMPLETA, unificada a `main`**. Docs `00`–`06` en
  `objetivo_3_modulo_mil_alternativo/investigacion/`: DSMIL + evaluación de
  los 3 papers de Eduardo (`05`) y de HMIL vía búsqueda web (`06`). DSMIL es
  un eje **ortogonal** al desbalance; **sujeto a confirmación** en la reunión.
- **Objetivo 4 — Heatmaps comparativos**: **PENDIENTE** (Obj 2 ya no lo
  bloquea). Viabilidad verificada (`objetivo_4_heatmaps/viabilidad_script.md`).
- **Objetivo 5 — Fusión binaria + varianza MC-CV + CLAM-vs-DSMIL**:
  **COMPLETADO + ANEXO (28 may 2026)**. Chain `4170→4171→4172` ✅ + job
  anexo `4179` ✅ (DSMIL × 3 binarias × k=5, cierre simétrico). Veredicto §2.2
  = **banda AMBIGUA** para DSMIL sobre fusionado (Δ bal_acc +0.040 ± 0.038
  positivo en los 3 folds pero bandas mean±std solapadas; AUC retrocede
  −0.020 ± 0.019). **Veredicto anexo**: NULL en carcinoma (Δ −0.023 ± 0.071,
  el "0.824" del 4137 era ruido del sorteo) + NULL/ambigua en tejido (Δ
  +0.021 ± 0.051) + **regresión leve consistente en CDIS** (Δ −0.053 ± 0.026,
  5/5 folds negativos — el "fracaso" del 4137 se sostiene con barras).
  **Hallazgo central agregado**: la arquitectura sola NO es la palanca a
  ninguna escala (binarias n=328 ni fusionado n=2814), con evidencia
  simétrica. El cuello sigue siendo datos / contexto espacial / desbalance.
  Slides 1-13 listas (anexo en 11-12). Detalle:
  `objetivo_5_fusion_binaria/resultados.md` (§FASE 2 + §ANEXO).
- **Reformulación multi-label**: **COMPLETADO (PRELIMINAR)** — **NO es hallazgo
  nuestro.** En la reunión Sebastián confirmó que él ya había hecho la
  separación en 3 binarios hace tiempo; nosotros dimos con su CSV y
  **reprodujimos/validamos** sus resultados de forma independiente (quedó
  satisfecho de que lo encontráramos). Comparación: **igualamos en carcinoma
  invasivo y mejoramos algo en CDIS y tejido** respecto a sus métricas. Nuestro
  aporte propio = el diagnóstico (eval roto + ablación B). Job `4109`. Detalle:
  `sprints/B4_sprint4/reformulacion_multilabel/resultados.md`.

### Hallazgos críticos (21–22 may 2026)

1. **Régimen de evaluación roto.** `microcalcificaciones_pth` tiene 8 clases;
   4 de ellas tienen **1 sola slide** en val y en test. El macro-AUC es un
   promedio dominado por ruido → la inversión val(0.69) < test(0.81) lo
   confirma. **Usar balanced accuracy + matriz de confusión, no el AUC solo.**
2. **El modelo colapsa a la clase mayoritaria.** Predice `no_identificado`
   para el 74.5 % de las slides de test; `test_acc` 0.72 está por *debajo*
   del baseline trivial (0.89).
3. **Estructura multi-label.** Las 8 clases son combinaciones de 3 tejidos +
   `no_identificado` → es un problema multi-etiqueta aplastado. Reformulado
   como 3 tareas binarias en `reformulacion_multilabel/`.
4. **El dataset grande no ayuda al desbalance.** 3072 vs 548 de V4: la
   expansión fue casi toda `no_identificado` (2739/3072); las clases raras
   siguen con 6–161 slides. Más datos de la mayoritaria no enseña las
   minoritarias. **Verificado 22 may (read-only):** el ~548 de V4 ≈ cohorte
   PRIVADA `microcalcificaciones_100` = **533 slides** hoy. Mapa: privado 533 ·
   combined 1397 · `_pth` 3072 · binarios identificados 333. Regla de la
   reunión: entrenar con ~548, reservar 3072 para pruebas finales.
5. **B no es la palanca (ablación Obj 2).** Doblar B (8→16) deja todo igual o
   peor — confirma empíricamente que el problema está en la formulación.
6. **La reformulación funciona donde más importa (carcinoma invasivo):**
   balanced acc 0.78, sobre el umbral de 0.60. CDIS y tejido siguen flojos
   (0.59 / 0.58) — el cuello de botella es datos (333 slides), no formulación.

### Jobs SLURM (snapshot)

| Job | Qué | Estado |
|---|---|---|
| `4098` | baseline B=8 `minpatch16` | COMPLETED |
| `4099` | ablation B=16 `minpatch16` | COMPLETED |
| `4109` | reformulación: 3 tareas binarias (PRELIMINAR) | COMPLETED |
| `4137` | DSMIL 3 binarias (obj3, fracaso en balanced_acc) | COMPLETED |
| `4170` | **Obj5 Fase 0** — varianza CLAM 3 binarias k=5 | COMPLETED (27-may) |
| `4171` | **Obj5 Fase 1** — CLAM fusionado k=3 | COMPLETED (27-may) |
| `4172` | **Obj5 Fase 2** — DSMIL fusionado k=3 + gate | COMPLETED (28-may, gate PASÓ) |
| `4179` | **Obj5 ANEXO** — DSMIL × 3 binarias k=5 (paired vs 4170) | COMPLETED (28-may, ~3h29m) |

### Reformulación multi-label — COMPLETADO (PRELIMINAR)

Job `4109` (22 may 2026): las **3 tareas binarias** de microcalcificaciones
corrieron secuenciales (CLAM_MB, B=8, `--max_epochs 30`, 333 slides,
`no_identificado` excluido, ~42 min). Análisis completo con matrices de
confusión en `reformulacion_multilabel/resultados.md`.

**Balanced accuracy (test), piso trivial 0.50:**

| Tarea | balanced acc | umbral | ¿cumple? |
|---|---|---|---|
| carcinoma invasivo | **0.78** | >0.60 | ✅ |
| CDIS | 0.59 | >0.65 | ❌ (apenas sobre 0.50) |
| tejido no neoplásico | 0.58 | >0.65 | ❌ (apenas sobre 0.50) |

**Veredicto preliminar**: la reformulación es la dirección correcta —
arregló el régimen de evaluación (de "no medible" a confiable) y volvió
aprendible el tejido más fragmentado (carcinoma = prueba de concepto). Pero
CDIS y tejido siguen flojos: el siguiente cuello de botella es **datos**
(333 slides → sobreajuste), no formulación. PRELIMINAR (1 semilla),
contingente a la reunión.

### Reunión Sebastián + Eduardo — REALIZADA (22 may 2026)

**Foco de entrenamiento confirmado: las 3 tareas binarias de
microcalcificaciones, NO las 8 clases.** El 8-clases queda solo como
diagnóstico cerrado (jobs 4098/4099). Toda mejora futura se evalúa sobre los
binarios y se compara contra el baseline binario (job 4109) sobre el mismo
dataset.

Acuerdos y dirección del sprint (ver `CLAUDE.md` Hallazgo 10):

1. **Reformulación en 3 binarios = trabajo previo de Sebastián.** No es hallazgo
   nuestro; lo reprodujimos/validamos. Igualamos carcinoma invasivo, mejoramos
   algo CDIS y tejido. Sebastián quedó satisfecho.
2. **Dataset de trabajo = ~548 slides (cohorte privada ≈ 533), NO el `_pth`
   3072.** El universo completo se reserva para PRUEBAS FINALES de una
   incorporación. Mapeo de tamaños verificado read-only el 22 may (ver
   Hallazgo crítico 4).
3. **`balanced_pth_100` para binarios = diseño, NO placeholder** (corregido
   tras WhatsApp Sebastián 26-may-2026 — antes leído como work-in-progress).
   El "balance" se define con un cap de imbalance ratio ≤10×; como los 3
   binarios ya cumplen (carcinoma 3.8×, cdis 1.8×, tejido 1.4×),
   `csv_balance/` y `splits/microcalcificaciones_en_*_pth_balance_100/`
   quedan iguales a las 333 identificadas (solo cambia el seed del split).
   Para los binarios de microcalcificaciones, entrenar sobre `_balance` no
   aporta nada vs entrenar sobre 333. El cap SÍ aplica a multiclase
   (`tipo_histologico_4clases`, etc.).
4. **Early stopping efectivo:** cortar cuando deja de mejorar por época.
5. **Modelo alternativo (DSMIL u otro):** adoptar SOLO con justificación
   clínica/arquitectónica + comparación contra baseline en el MISMO dataset.
6. **Investigar:** escala / nº de parches y features de citoplasma según tarea;
   buscar papers que evalúen tareas débiles con buenos resultados.

### Próxima misión (Ernesto — semana 28-may en adelante)

- **Armar slides en OnlyOffice** copiando desde
  `sprints/B4_sprint4/objetivo_5_fusion_binaria/presentacion_contenido_completo.md`
  (Slides 1-11, formato copy-paste) + insertar `figuras/{fig1a_fase0_auc.png,
  fig1b_fase0_balacc.png, fig2_fusionado_clam_vs_dsmil.png}`. Una vez listo
  → habilita merge a main del Obj 5.
- **Objetivo 4 (heatmaps comparativos)**: arrancar; viabilidad ya verificada
  (`objetivo_4_heatmaps/viabilidad_script.md`). Insumo natural del Eje B
  (selección de parches con información).
- **Ejes futuros (post-sprint, aprobados Sebastián 26-may)**: re-extracción
  CONCH a mayor magnificación (Eje A, priorizado) + selección de parches
  útiles (Eje B). Ver `sprints/B4_sprint4/ejes_futuros_microcalc.md`.
- **Anexo EJECUTADO (28-may)**: DSMIL × 3 binarias × k=5 (job 4179) corrió
  como cierre simétrico tras decisión revisitada con Ernesto. Hipótesis
  pre-registrada `hipotesis_dsmil_binarias.md` con reviewer OK (regla 9
  cumplida). Resultado: NULL en carcinoma + NULL/ambigua en tejido + regresión
  leve consistente en CDIS (5/5 folds Δ negativo). El veredicto refuerza
  Hallazgo 4 Fase 0 con evidencia simétrica. Detalle en
  `ejes_futuros_microcalc.md` §Apéndice y `objetivo_5_fusion_binaria/resultados.md` §ANEXO.

### WhatsApp Sebastián 26-may-2026 (mañana) — pendientes aclarados

- **`_balance` para binarios = diseño** (cap imbalance ratio ≤10× ya cumplido).
  Ver punto 3 de la reunión actualizado arriba.
- **`no_identificado` semántica**: WSI sin mención en reporte CAP (no
  necesariamente ausencia). **NO se incluye** en entrenamiento de binarios
  hoy (ni nuestros ni de Sebastián). Es decisión por defecto.
- **Mapeo multi-label → binarios**: WSI con mención de tejido(s) → `si` en
  ese binario, `no` en los demás. Combinaciones → si en ambos.
- Detalle completo + citas textuales en memorias
  `microcalc-dataset-decision.md` (actualizada) y `CLAUDE.md` Hallazgo 10.

### Reunión Sebastián + Eduardo — REALIZADA (26-may-2026 16:30)

8 puntos conversados (reporte de Ernesto):

1. **Tabla de mejores resultados de Sebastián** (17 tasks, 12 con test_auc≥0.75
   = 71%). Métrica reportada = **test AUC**. Escoge dataset **por task** (no
   uniforme): micro carc inv 0.79 (`combined`), micro cdis 0.69 (`pth_balance`
   **con** no_id, rango 118-2010), micro tej no neo 0.63 (`pth_balance` 328).
   Snapshot en `objetivo_5_fusion_binaria/` (vía hipotesis.md Tarea 0).
2. **Eduardo + mammoth** en grado nuclear: reemplazó la 1ª FC común de CLAM por
   mammoth → subió. **mammoth ya gana en 3 tasks** de Sebastián (g.h. tubular
   0.81, c.d.i. grado nuclear 0.78, pleomorfismo 0.78).
3. **Sebastián + LongNet** post-CONCH (al embedding) → empeoró en general.
4. **Necrosis fusionada a 1 binario**: al unir varias binarias en UNA pregunta
   ("tiene/no tiene"), **SÍ incluye `ausente/no_identificado` como negativo**;
   con varias binarias separadas NO (absorberían la señal). **Regla nueva.**
5. **Aprobado: fusionar las 3 binarias de microcalc en 1 binario** "tiene/no
   tiene" + no_id como negativo. Condición: **no tocar sus CSVs/splits, crear
   los nuestros** bajo `clam_testing2/`. → **Objetivo 5 Fase 1.**
6. **Aprobado: CLAM vs DSMIL también en el fusionado** (Fase 2). Reabre DSMIL
   solo en este régimen (más datos → ya no data-starved como en job 4137).
7. **Diagrama DSMIL para la presentación** + diferencias/ventajas vs CLAM.
8. **Ejes futuros aprobados**: (a) re-extraer CONCH a **mayor magnificación**
   solo para slides de microcalc (CONCH es caro); (b) **selección de parches
   con info (no ruido)** vía el mejor modelo, estilo heatmap Camelyon. Ambos
   pendientes, no en este sprint.

Alcance preciso de lo aprobado: **binario fusionado plano (nivel 1)**, NO el
nivel 2 condicionado de la propuesta jerárquica original. Ver memoria
[[microcalc-hierarchical-proposal]] (cerrada como adopción parcial) y
[[microcalc-fusion-objetivo5]] (decisiones operativas del objetivo).

### Objetivo 5 — Fusión binaria + varianza + arquitecturas (COMPLETADO 28-may)

Argumento + métrica pre-registrados (reviewer OK):
`sprints/B4_sprint4/objetivo_5_fusion_binaria/hipotesis.md`. 3 fases en chain
SLURM (rama `feature/sprint4-fusion-microcalc`, pusheada a origin con todos
los commits del cierre):

- **Fase 0 (job 4170) — COMPLETA 27-may.** Varianza vía **Monte Carlo CV**
  (k=5; lo llamamos "k-fold" en archivos pero es MC-CV = test solapados, el
  mismo `generate_split` de CLAM, `utils/utils.py:104-141`). **Resultado clave**:
  el single-split del 4109 era **optimista por suerte de sorteo**. test_auc
  honesto (media±std): carcinoma **0.732 ± 0.167** (un fold dio 0.41!), cdis
  **0.652 ± 0.072**, tejido **0.646 ± 0.025**; balanced_acc **0.639 / 0.595 /
  0.577**. La "paridad/ventaja sobre Sebastián" del single-split NO se sostiene
  — pero tampoco perdemos: con barras de error las 3 son **indistinguibles** de
  Sebastián (su 0.79/0.69/0.63 cae dentro de las bandas). Regla §0.2 disparada
  (std>0.05) → downstream solo con MC-CV.
- **Fase 1 (job 4171) — COMPLETA 27-may.** CLAM sobre el fusionado (**k=3**,
  régimen test grande ~33 pos/fold). CSV propio 2814 slides (328 si / 2486 no,
  7.58:1). balanced_acc **0.620 ± 0.010** (PLATEAU §1.3, no llega al umbral
  clínico 0.65 pero no colapsa); test_auc **0.776 ± 0.021**. Gate de colapso
  para Fase 2 PASA (>0.55).
- **Fase 2 (job 4172) — COMPLETA 28-may.** DSMIL sobre el fusionado (mismos
  splits k=3 que Fase 1 → comparación pareada). balanced_acc **0.661 ± 0.046**;
  test_auc **0.756 ± 0.024**. Δ pareado bal_acc **+0.040 ± 0.038** positivo en
  los 3 folds (+0.094/+0.009/+0.018), pero **bandas mean±std SE SOLAPAN** (CLAM
  [0.610, 0.630] vs DSMIL [0.615, 0.707]) → heurístico §2.2 NO se cumple. Δ
  pareado AUC **−0.020 ± 0.019** (no acompaña). DSMIL recupera más positivos
  (recall+ 0.49 vs CLAM 0.36) pero con más FP (recall− 0.83 vs 0.88) → menos
  conservador, no necesariamente mejor discriminador. **Veredicto §2.2 = banda
  AMBIGUA**: NO sobre-vender como "supera a CLAM".

Harness Fase 1/2 = `scripts/train_dsmil.py --model_type {clam,dsmil}` (switch
aditivo; path DSMIL byte-idéntico a 4135/4137, reviewer-verificado) → CLAM y
DSMIL por el MISMO train/val/test = apples-to-apples.

**Hallazgo de la tabla de Sebastián**: su `pth_balance` de cdis YA incluye
no_id (118 pos / 2010 neg) y aun así da 0.69 → temperaba expectativa del
fusionado (incluir no_id no fue bala de plata para él). Resultado nuestro
confirma: balanced_acc honesta 0.620 ≈ promedio de las binarias separadas.

**Lección central del objetivo**: el cuello sigue siendo datos / contexto
espacial / desbalance, NO la arquitectura sola (DSMIL en régimen con datos
tampoco rompe la barrera) NI la formulación (fusionado plano ≈ promedio
binarias separadas). Justifica empíricamente los ejes futuros aprobados
(mayor magnificación CONCH + selección de parches).

**Entregables**: Slides 1-11 en `objetivo_5_fusion_binaria/presentacion_contenido_completo.md`
(formato copy-paste OnlyOffice) + figuras (fig1a, fig1b, fig2) en
`objetivo_5_fusion_binaria/figuras/`. Detalle: `objetivo_5_fusion_binaria/resultados.md`.

### Pendiente de confirmar con Sebastián

- Pendiente menor: qué define exactamente el subconjunto de 548 (privado 533
  incluye `no_identificado`) vs los 333 identificados de los binarios. La
  diferencia es la cohorte (privado vs `_pth`), no una regla de filtro
  adicional; aclarado parcialmente con la WhatsApp 26-may.

### Ramas

- `main`: todo el Sprint 4 — Objetivos 1, 2, 3 (investigación) unificados,
  scripts, preflight, splits, presentación, docs, reformulación multi-label.
- `feature/sprint4-obj3-mil-alternativo`: **ya unificada a `main`** (merge
  `43d2ae4`).
- `feature/sprint4-reformulacion-multilabel`: **ya unificada a `main`**
  (merge `c4982ed`).
- `feature/sprint4-fusion-microcalc`: **ACTIVA, Obj 5 CERRADO en local + push
  a origin (28-may)**. Contiene hipótesis + Fase 0/1/2 completas (splits, CSV
  fusionado, gate, 2 .slurm, switch `--model_type` de train_dsmil, resultados,
  tablas, slides 1-11, figuras). **NO mergeada a `main`** — espera OK
  explícito de Ernesto, condicionado a que la presentación esté lista en
  OnlyOffice.
