# progress/current.md

> Estado vivo del sprint actual. Es un **snapshot** — se reemplaza al avanzar
> el sprint. Al cerrar el sprint, el resumen pasa a `history.md`.

---

## Sprint actual: B4 / Sprint 4

**Snapshot: 22 may 2026 (post-reunión Sebastián + Eduardo)** (Objetivos 1 y 2
completados; investigación del Objetivo 3 unificada a `main`; reformulación en
3 binarios corrida y comparada con Sebastián — ver Reunión abajo).

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

Acuerdos y dirección del sprint (ver `CLAUDE.md` Hallazgo 10):

1. **Reformulación en 3 binarios = trabajo previo de Sebastián.** No es hallazgo
   nuestro; lo reprodujimos/validamos. Igualamos carcinoma invasivo, mejoramos
   algo CDIS y tejido. Sebastián quedó satisfecho.
2. **Dataset de trabajo = ~548 slides (cohorte privada ≈ 533), NO el `_pth`
   3072.** El universo completo se reserva para PRUEBAS FINALES de una
   incorporación. Mapeo de tamaños verificado read-only el 22 may (ver
   Hallazgo crítico 4).
3. **`balanced_pth_100`** (Sebastián lo está finalizando): mayoritaria
   `no_identificado` ≤ 10× minoritaria. Aún no existe como split (el
   `csv_balance`/`_pth_balance` actual = 333, placeholder). Invitados a entrenar
   sobre él cuando esté.
4. **Early stopping efectivo:** cortar cuando deja de mejorar por época.
5. **Modelo alternativo (DSMIL u otro):** adoptar SOLO con justificación
   clínica/arquitectónica + comparación contra baseline en el MISMO dataset.
6. **Investigar:** escala / nº de parches y features de citoplasma según tarea;
   buscar papers que evalúen tareas débiles con buenos resultados.

### Próxima misión (Ernesto — este finde + semana que viene)

- **Investigar requisitos para mejorar microcalcificaciones** y los factores
  clave para adoptar un modelo nuevo (escala de parches, citoplasma, etc.).
- **Llegar con una implementación corrida** (DSMIL u otro) para comparar contra
  el baseline en el mismo dataset (~548), ojalá con mejora medible.
- Mejorar la presentación del Sprint 4
  (`sprints/B4_sprint4/presentacion_contenido.md`) — reencuadrar la
  reformulación como validación, no como descubrimiento.

### Pendiente de confirmar con Sebastián

- Qué define exactamente el subconjunto de 548 (privado 533 incluye
  `no_identificado`) vs los 333 identificados de los binarios.
- Qué es `no_identificado` (¿sin microcalcificación, o sin ubicar?).

### Ramas

- `main`: todo el Sprint 4 — Objetivos 1, 2, 3 (investigación) unificados,
  scripts, preflight, splits, presentación, docs, reformulación multi-label.
- `feature/sprint4-obj3-mil-alternativo`: **ya unificada a `main`** (merge
  `43d2ae4`).
- `feature/sprint4-reformulacion-multilabel`: **ya unificada a `main`**
  (merge `c4982ed`).
