# Investigación: ¿qué integrar para mejorar resultados? — síntesis post-cierre de arquitectura

> **Sprint B5 — fase de ARGUMENTO (regla 9).** Este documento NO toca
> `model_*.py` / `core_utils.py` / training, NO usa GPU, NO entrena. Es el
> *argumento antes de código*: con los **tres ejes de arquitectura ya cerrados**
> (0 palancas) y **PathPT cerrado hoy**, ¿qué conviene integrar de aquí al lunes
> para de verdad mover la aguja, atacando el cuello REAL (datos / desbalance /
> calibración) y no repitiendo un swap de modelo?
>
> Punto de partida (NO re-derivado acá): `investigacion_retrieval/analisis.md`
> (variantes A/B/C/D + 2 papers leídos). Cierre PathPT:
> `pathpt/{resultados_necrosis.md, resultados_mitotic.md}` + auditoría
> `auditoria_coherencia/hallazgos_pathpt.md`. Hallazgos durables: `CLAUDE.md`
> §"Hallazgos vigentes" 11 (agregador), 12 (mammoth), 13 (PathPT).

---

## 0. TL;DR — la recomendación en 7 líneas

1. **La arquitectura no es la palanca — cerrado en 3 ejes independientes, 0
   palancas** (agregador/DSMIL, patch-embed/mammoth, lenguaje+tile/PathPT). Y un
   grupo SOTA externo (PathPT) **choca el mismo techo de datos**. Esto es un
   resultado, presentable, no un fracaso.
2. **Hay UNA palanca nueva, genuina y NO explorada que salió HOY:** el **punto de
   operación / calibración** bajo desbalance. El colapso de mitotic lo destapó —
   el AUC sobrevive (el ranking tiene señal) pero el **argmax** colapsa a la
   mayoritaria. Esto NO es arquitectura: es *cómo leemos la salida del modelo*.
3. **Candidato 1 (la apuesta de fondo): calibración del operating-point.** Barato,
   directo sobre CLAM, **demostrable post-hoc sobre artefactos que YA existen**
   (las probabilidades por clase están guardadas). Atacar el colapso/desbalance
   sin re-entrenar.
4. **Candidato 2 (la apuesta de presentación): CBIR / variante D.** Bajo riesgo,
   alto brillo, CPU, no entrena, reusa CONCH as-is. Con PathPT cerrado, **vuelve a
   ser** el entregable clínico de menor riesgo para el lunes. El diagrama ya está
   hecho (`investigacion_retrieval/figuras/D10_*`).
5. **Descartados / no reabrir:** A (swap de agregador-retrieval = "mammoth #3"),
   B/PathPT (lo probamos hoy, no aporta con CONCH).
6. **Encuadre honesto del lunes:** "el baseline FUNCIONA (invasión bal_acc 0.62 /
   AUC 0.83 ≫ trivial 0.33); la arquitectura no es la palanca (resultado real, 3
   ejes); el próximo lever no es otro modelo — es **leer mejor la salida**
   (calibración) y **entregar valor por otra vía** (CBIR)".
7. **Priorización:** calibración = la **propuesta técnica** (alto valor, bajo
   riesgo, regla-9-limpia en su variante post-hoc); CBIR = el **entregable
   lúcible**. No compiten — atacan ejes distintos.

---

## 1. El cuello, re-confirmado en 3 ejes (y por un grupo externo)

Lo que ya sabíamos y quedó **cerrado simétricamente**:

```
  EJE                         MÉTODO PROBADO         VEREDICTO (paired k=5)
  ────────────────────────────────────────────────────────────────────────
  Agregador (cómo se          DSMIL                  NULL  (Hallazgo 11)
    combinan los parches)
  Patch-embed (1ª capa →      mammoth / MoE          NULL  · 8 tareas (Hallazgo 12)
    mixture of experts)
  Lenguaje + supervisión      PathPT-CONCH           necrosis H_alt · mitotic
    tile-level                                       COLAPSO · microcalc NO-GO
                                                     (Hallazgo 13, cerrado HOY)
  ────────────────────────────────────────────────────────────────────────
  → Los tres convergen: el cuello = CONCH / DATOS / DESBALANCE / CALIBRACIÓN,
    NO el método. Cambiar/aumentar el modelo da el mismo null.
```

**Confirmación independiente (no somos solo nosotros).** El paper PathPT
[He 2025/26] reporta que en el régimen pediátrico, a 10-shot, **PathPT, TransMIL y
DGRMIL convergen a 0.54–0.55** y lo llama textual *"a ceiling imposed by limited
data"*. Es la misma tesis que nuestros Hallazgos 11/12/13, dicha por un grupo SOTA
con un método mucho más sofisticado: **cuando faltan datos, el método deja de ser
la palanca.** (Detalle y caveats en `investigacion_retrieval/analisis.md` §4.)

**Implicación dura para esta sesión:** proponer un **4º swap de arquitectura sobre
features CONCH sería "mammoth #3"** — predicción honesta = null. Lo prohíbe el
handoff y lo prohíbe la evidencia. La pregunta correcta NO es "¿qué modelo nuevo?"
sino **"¿qué eje, que NO sea la arquitectura, todavía no tocamos?"**.

---

## 2. La lección nueva de hoy: el *operating point* es una palanca real y no explorada

El colapso de mitotic (job 4326) no es solo un null más: **destapó un grado de
libertad que veníamos dejando en su valor por defecto.**

### 2.1 El diagnóstico: el ranking sobrevive, la decisión colapsa

PathPT en mitotic dio `balanced_acc = 0.333` **exacto** en los 5 folds — el trivial
de 3 clases. La confusión pooled lo dice todo:

```
  VERDAD \ PRED      score_1   score_2   score_3      recall
  score_1 (n=320)      320        0         0          1.00   ← todo a la mayoritaria
  score_2 (n=142)      142        0         0          0.00
  score_3 (n=126)      126        0         0          0.00
  ───────────────────────────────────────────────────────────
  macro-OVR AUC = 0.662  ← el RANKING no colapsa: hay señal latente
  argmax           = degenerado  ← el OPERATING POINT sí colapsa
```

**El punto clave:** un AUC de 0.66 con un balanced_acc de 0.33 **es una contradicción
aparente que tiene una sola explicación** — el modelo *ordena* las clases por encima
del azar (el score continuo de score_3 > score_2 > score_1 en promedio), pero el
**umbral de decisión** (el argmax crudo) manda todo a la clase basal porque su masa
de probabilidad domina bajo el desbalance. **No falta señal: falta umbral.**

Esto **no es arquitectura.** Es ortogonal a los 3 ejes cerrados: el modelo ya
produce los scores; lo que está mal calibrado es **cómo los convertimos en una
etiqueta.** Es un eje que literalmente no tocamos en todo el trimestre.

### 2.2 No es solo mitotic — el mismo síntoma en invasión y necrosis

El patrón "sesgo a la mayoritaria por operating-point por defecto" aparece en TODO
lo desbalanceado, no solo en el colapso extremo:

| Tarea (brazo CLAM) | AUC | bal_acc | recall mayoritaria | recall minoritaria(s) | lectura |
|---|---|---|---|---|---|
| **invasión** 3-clase | 0.828 | 0.622 | `no_identificado` 0.79 | `presente` 0.58 / `ausente` ~0.50 | ranking BUENO, sub-detecta minoritarias |
| **necrosis** binaria | 0.727 | 0.633 | `presente` 0.87 | `ausente` 0.40 | sub-detecta la clase chica |
| **mitotic** 3-clase | 0.724 | 0.494 | `score_1` 0.72 | `score_2` 0.19 | flojo en la del medio |

(invasión/necrosis = brazo CLAM, jobs 4246/4309; provenance en CLAUDE.md Hallazgo
12/13 y `resultados_necrosis.md`.)

**En invasión el AUC es 0.83 — hay headroom real.** El modelo *sabe* ordenar
(`presente` tiene score alto cuando lo es), pero al umbral por defecto sub-detecta
`presente` (recall 0.58) y `ausente` (~0.50) y sobre-detecta `no_identificado`
(0.79). **Mover el operating point hacia las minoritarias puede subir balanced_acc
sin tocar el modelo** — es exactamente el grado de libertad que no exploramos.

### 2.3 El argumento clínico (regla 9): el operating point NO debería ser argmax

En oncología de screening el costo de un falso negativo (no detectar invasión /
necrosis presente) **no es simétrico** con el de un falso positivo. El argmax
(equivalente a umbral 0.5 / "la clase más probable") optimiza *accuracy*, que es la
métrica equivocada bajo desbalance y costo asimétrico. **Elegir el operating point
por costo clínico (o por balanced_acc en val) es una decisión metodológica
correcta y no explorada**, no un truco para inflar números.

---

## 3. Candidato 1 — Calibración / operating-point (la palanca nueva)

> **Esto NO reabre un eje descartado (regla 9.b no aplica): la calibración es un
> eje NUEVO, ortogonal a la arquitectura.** Los 3 ejes cerrados son sobre *el
> modelo*; este es sobre *cómo se lee su salida*. No hay decisión previa que
> revisitar.

### 3.1 Qué es y por qué ataca el cuello

En vez de cambiar el modelo, cambiar **cómo convertimos sus scores en etiqueta**:

- **Umbral por clase calibrado en val** (en vez del argmax crudo): para cada clase,
  elegir el umbral que maximiza balanced_acc (o la sensibilidad objetivo) en el set
  de validación, y **congelarlo** para test. Bajo desbalance esto rescata las
  minoritarias que el argmax aplasta.
- **Re-ponderación / pérdida balanceada en entrenamiento** (focal loss,
  class-balanced CE): el `--weighted_sample` ya corrige el muestreo, pero la
  *pérdida* sigue siendo CE plana; una focal/class-balanced empuja el gradiente a
  las minoritarias. (Esto SÍ toca training → regla 9 + reviewer.)
- **Tratar el ordinal como ranking** (mitotic): usar el AUC/score continuo como
  salida primaria y derivar el operating point por umbral, en vez del argmax 3-vías.

### 3.2 La escalera de riesgo (de barato/limpio a caro)

```
  TIER 0  ── post-hoc, NO toca training, NO dispara reviewer ──  ⭐ empezar acá
  │  Re-umbralizar los scores YA guardados de CLAM.
  │  Insumo: y_prob_* en test_predictions.csv + checkpoints s_N_checkpoint.pt
  │          (verificado: las probabilidades por clase están guardadas).
  │  Honesto: umbral elegido en VAL (inferencia CPU con el checkpoint), aplicado
  │           a TEST. Sin DoF post-hoc.
  │  Costo: minutos de CPU. Riesgo: nulo. Regla 9: trivial (es análisis).
  │
  TIER 1  ── toca training → regla 9 (hipótesis pre-registrada) + reviewer + sbatch
  │  Focal / class-balanced loss en el bag classifier, o pérdida ordinal en mitotic.
  │  Paired vs CLAM, reusando splits (patrón [[patron-paired-comparison-reuso-splits]]).
  │  Costo: una ola GPU k=5. Riesgo: medio (puede ser null, pero informa).
```

**El Tier 0 es la joya para el lunes:** es *demostrable sobre datos que ya tenemos*,
sin GPU, sin reviewer, sin reabrir nada. Convierte un clasificador colapsado en uno
usable y muestra el trade-off sensibilidad/especificidad de forma explícita.

### 3.3 Factibilidad verificada (no es promesa)

```
  results/.../split_N_results.pkl   →  {slide_id: {prob:[p0,p1,p2], label}}   ✓
  results/.../test_predictions.csv  →  y_true, y_prob_0/1/2, y_pred           ✓
  results/.../s_N_checkpoint.pt     →  pesos CLAM (para inferir scores en val) ✓
```

Las probabilidades por clase de CLAM (invasión, mitotic, necrosis) **ya están en
disco**. La calibración post-hoc se puede demostrar **esta semana, en CPU, sin
re-correr nada en GPU**. Lo único a generar es la inferencia de scores sobre el set
de **val** de cada fold (CPU, checkpoints guardados) para elegir el umbral honesto.

### 3.4 Qué promete y qué NO (honestidad — acotado por el AUC)

- **Promete:** (a) eliminar el **colapso degenerado** (mitotic deja de ser un
  clasificador trivial → usable); (b) en tareas con AUC decente (invasión 0.83)
  **subir balanced_acc** moviendo recall hacia las minoritarias; (c) exponer el
  trade-off como decisión clínica explícita.
- **NO promete:** romper el techo de datos. La calibración **no crea señal que no
  esté en el ranking** — está acotada por el AUC. Mitotic (AUC 0.66) quedará
  *usable pero modesto*; invasión (AUC 0.83) tiene headroom real. **No es un lever
  para "ganarle a CLAM como modelo"; es para leer CLAM mejor.** Venderlo como otra
  cosa repetiría el error de sobre-prometer.

### 3.5 Esbozo regla 9 (boceto, no pre-registración formal)

- **Hipótesis (mecanismo):** si el AUC > balanced_acc·(algo) indica ranking con
  señal pero operating-point sesgado, entonces re-umbralizar por clase (umbral
  elegido en val) debe **subir balanced_acc en test sin re-entrenar**, más en las
  tareas con mayor brecha AUC↔bal_acc (invasión > necrosis > mitotic).
- **Métrica + subset + dirección (política B5):** balanced_acc **+** AUC (que no
  cambia: el ranking es el mismo) **+** confusión + n por clase, **paired por fold**
  (umbral de val → test). Dirección: Δbalanced_acc(calibrado − argmax) > 0,
  consistente en signo, mayor donde la brecha AUC↔bal_acc es mayor. NO gate mágico
  (regla 9.a): dirección + consistencia + magnitud vs varianza.
- **Variable de diseño:** criterio del umbral (max-bal_acc en val vs costo clínico
  asimétrico vs Youden). Es la decisión de mayor impacto.

---

## 4. Candidato 2 — CBIR / variante D (la apuesta de presentación)

> **Ya analizado a fondo en `investigacion_retrieval/analisis.md` §3.D y §5 — NO
> se re-deriva acá.** Resumen del porqué sigue vivo + el cambio de hoy.

- **Qué es:** *Content-Based Image Retrieval* — el patólogo sube una slide, el
  sistema muestra las N más parecidas del archivo con sus diagnósticos. No es subir
  una métrica de clasificación: es un **entregable clínico** ("apoyo por casos
  similares").
- **Por qué encaja AHORA:** usa CONCH as-is (mean-pool → 1 vector/slide → índice
  coseno → kNN), **NO entrena nada** (regla 9 trivial), corre en **CPU**, 100%
  dentro de containment. Cambia el *frame*: no pelea la métrica donde sabemos que
  nos estrellamos.
- **El cambio de hoy:** el análisis de retrieval (5-jun) lo tenía como primario de
  presentación; el addendum del 10-jun lo bajó cuando PathPT subió a prueba activa.
  **Con PathPT cerrado (no aporta), CBIR vuelve a ser el candidato de bajo
  riesgo / alto brillo para el lunes** (auditoría `hallazgos_pathpt.md` F5).
- **Asset ya hecho:** `scripts/generate_cbir_clam_diagram.py` →
  `investigacion_retrieval/figuras/D10_clam_cbir_integrado.png` — diagrama de CLAM
  con la rama CBIR como **rama hermana** que comparte el backbone CONCH (NO se
  inserta en el forward = NO es la variante A). Listo para la slide.
- **Caveat (de [Alfasly 2024]):** venderlo como **herramienta de apoyo**, no como
  clasificador clínico-grado; validar con números honestos en NUESTRAS tareas de
  2–3 clases (no extrapolar el 117-vías del paper). MVP demostrable en CPU.
- **Esbozo regla 9:** ya en `investigacion_retrieval/analisis.md` §6 (macro-F1 de
  voto top-k + balanced_acc + confusión, paired vs CLAM, sin GPU).

---

## 5. Descartados / no reabrir (regla 9.b)

| Vía | Estado | Por qué |
|---|---|---|
| **A — agregador-retrieval** (RAM-MIL) | descartado | Swap de agregador sobre las mismas features = "mammoth #3". Predicción honesta: null. Solo volvería si el problema se reformula como *generalización cross-fuente* (no es nuestro cuello). |
| **B — PathPT / few-shot prompt-tuning** | **cerrado HOY** | Probado paired vs CLAM: necrosis H_alt, mitotic colapso, microcalc NO-GO. El grounding zero-shot de CONCH para nuestra morfología resultó débil (el riesgo anticipado se materializó). **NO re-correr sin sign-off de Sebastián sobre la formulación + razón nueva** (Hallazgo 13, regla 9.b). |
| **Cualquier 4º swap de arquitectura sobre CONCH** | prohibido | Handoff §8 + Hallazgos 11/12/13. |

> Nota: **C (parches útiles)** sigue plegado al **Eje B del plan B5 (Objetivo 4)** —
> no es una vía nueva. PathPT dio la receta (pseudo-labels tile-level) pero el
> método cerró; la *idea* de seleccionar parches útiles sigue en el plan como eje
> de datos.

---

## 6. Comparación y recomendación

### 6.1 Tabla

| | Calibración (Cand. 1) | CBIR / D (Cand. 2) |
|---|---|---|
| **Ataca el cuello** | ✅ desbalance / operating-point (directo) | ⟂ cambia el frame (no pelea la métrica) |
| **Usa CONCH/CLAM as-is** | ✅ (re-umbral sobre scores guardados) | ✅ (mean-pool de CONCH) |
| **Entrena / GPU** | Tier 0: **no** · Tier 1: sí | **no** (indexar + buscar) |
| **Regla 9 / reviewer** | Tier 0: trivial · Tier 1: sí | trivial |
| **Riesgo "null #2"** | bajo (Tier 0 es análisis, no apuesta) | bajo |
| **Factible al lunes** | ✅ Tier 0 demostrable sobre artefactos existentes | ✅ MVP CPU + diagrama ya hecho |
| **Brillo presentación** | medio-alto (diagnóstico + fix elegante) | **alto** (herramienta lúcible) |
| **Rol** | la **propuesta técnica** de fondo | el **entregable** de presentación |

(⟂ = ortogonal: entrega valor por otro eje, no pelea la métrica rígida.)

### 6.2 Recomendación razonada

**No son excluyentes — atacan ejes distintos y juntos cuentan UNA historia honesta
y completa para el lunes:**

1. **Reencuadre (la columna vertebral del mensaje):** el baseline funciona; la
   arquitectura no es la palanca — **resultado real, 3 ejes, confirmado por SOTA
   externo (techo de datos)**. Esto convierte "no mejoramos la métrica" en "probamos
   rigurosamente dónde NO está la palanca", que es ciencia, no fracaso.
2. **La propuesta técnica de fondo = calibración del operating-point.** Es la
   **única palanca nueva, genuina y no explorada** del trimestre, salió de nuestro
   propio diagnóstico (el colapso de mitotic), es barata, ortogonal a lo cerrado, y
   **demostrable post-hoc sobre datos que ya tenemos** (Tier 0). Alto valor / bajo
   riesgo / regla-9-limpia.
3. **El entregable lúcible = CBIR.** Bajo riesgo, alto brillo, CPU, diagrama hecho.
   Da el "wow" clínico sin pelear el techo de datos.

**Prioridad de ejecución si Ernesto da el OK (todo fase-argumento → luego código):**
- **(a)** Cerrar este análisis con Ernesto/Sebastián.
- **(b)** Si se elige avanzar a demostración: **calibración Tier 0** primero (CPU,
  sobre artefactos existentes, sin reviewer) — es el quick-win más sólido y honesto.
- **(c)** CBIR MVP en paralelo (CPU) para la slide de "herramienta".
- **(d)** Calibración Tier 1 (focal/ordinal) = research del trimestre siguiente
  (regla 9 + reviewer + sbatch), si Ernesto continúa.

### 6.3 Por qué es coherente con todo lo que probamos

La lección de las 8+ tareas es: **no inviertas en otro modelo — da null.** Los dos
candidatos **escapan de esa trampa por construcción**: la calibración no cambia el
modelo (cambia cómo se lee su salida); CBIR no es un clasificador (es una
herramienta). Ninguno es "mammoth #3". Y la pieza de evidencia más fuerte —que
PathPT *también* choca el techo de datos— dice que seguir peleando la métrica con
modelos más grandes tiene rendimientos decrecientes. **Estos dos no pelean esa
pelea.**

---

## 7. Diagrama — el árbol de decisión del sprint (para la slide)

```
                    ¿Cómo mejoramos los resultados de OncoMets?
                                     │
            ┌────────────────────────┼────────────────────────┐
            │                        │                         │
     ¿Mejor ARQUITECTURA?      ¿Leer mejor la           ¿Entregar valor
     (el modelo)               SALIDA? (operating        por otra VÍA?
            │                   point)                        │
     ┌──────┼──────┐                 │                   ┌────┴────┐
   DSMIL  mammoth PathPT       CALIBRACIÓN              CBIR    (parches
     │      │      │           ───────────             ──────    útiles =
   NULL   NULL  necrosis H_alt  palanca NUEVA          herramienta  Eje B)
   (H11)  (H12) mitotic COLAPSO  ortogonal              clínica
                microcalc NO-GO  · Tier 0 post-hoc      · CPU, no
                (H13)            · CPU, sin reviewer       entrena
                                 · acotada por el AUC    · diagrama
            ✗ CERRADO            ✓ CANDIDATO 1            ✓ CANDIDATO 2
         (0 palancas, 3 ejes)   (propuesta técnica)      (entregable)
                                     ▲
                  el colapso de mitotic destapó esta rama:
                  AUC sobrevive (ranking) ≠ argmax colapsa (operating point)
```

---

## 8. Caveats y qué NO hacer

- **NO vender la calibración como "le ganamos a CLAM".** Está acotada por el AUC; su
  valor es eliminar el colapso y rebalancear sensibilidad, no romper el techo de
  datos. Honestidad > hype (lección del sprint).
- **NO vender CBIR como clasificador clínico-grado** — herramienta de apoyo, números
  honestos en nuestras 2–3 clases.
- **NO proponer un 4º swap de arquitectura** sobre CONCH (Hallazgos 11/12/13).
- **NO re-correr PathPT** (necrosis/mitotic/microcalc) sin razón nueva + sign-off de
  Sebastián (regla 9.b).
- **El umbral de calibración se elige en VAL y se congela a TEST** — si se elige en
  test, es DoF post-hoc y el resultado es inválido (mismo rigor que H-2 del reviewer
  en PathPT).
- **Tier 1 (focal/ordinal) toca training** → regla 9 (hipótesis pre-registrada) +
  reviewer + sbatch + OK explícito de Ernesto antes de cualquier GPU.
- **NO commitear el working tree ajeno** (README mammoth de Sebastián, untracked sin
  decidir). Este doc + sus figuras son lo único de esta sesión.

---

## 9. Próximos pasos

1. **Cerrar este análisis con Ernesto/Sebastián** (decisión de priorización).
2. Si avanza a demostración: **calibración Tier 0** — script CPU que (i) infiere
   scores de val con los checkpoints guardados, (ii) elige umbral por clase
   maximizando balanced_acc en val, (iii) aplica a test y reporta Δ paired vs argmax.
   Sobre invasión (mayor headroom, AUC 0.83), mitotic (rescatar el colapso) y
   necrosis. Sin GPU, sin reviewer (es análisis post-hoc).
3. **CBIR MVP** (CPU): mean-pool CONCH → índice coseno → kNN top-k en nuestras
   tareas; el diagrama D10 ya está para la slide.
4. Si Tier 1 se materializa: branch nueva + pre-registración regla 9 + reviewer +
   sbatch (research del trimestre siguiente).

---

*Fase de argumento (regla 9). No se tocó modelo, no se usó GPU, no se entrenó. Todo
claim anclado a los resultados/artefactos reales del repo (jobs 4246/4309/4326,
artefactos `results/`) o a los 2 PDFs leídos (regla 5). Provenance de cada número en
CLAUDE.md Hallazgos 11/12/13 y los `resultados_*.md` citados.*
