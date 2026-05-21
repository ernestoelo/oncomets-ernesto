# Frente 4 — Riesgos, supuestos y preguntas para la reunión

> **Fuentes**: paper DSMIL + código oficial (ver `01_`, `02_`), código
> CLAM (`03_`), e inspección **real** de las features CONCH del servidor
> (read-only, sin GPU, esta sesión).
>
> Cada riesgo trae: descripción → evidencia → severidad → mitigación.
> Severidad: 🔴 alta / 🟡 media / 🟢 baja-o-descartada.

---

## A. Supuestos del paper que NO se cumplen en nuestro setup

### A.1 — El paper usa features SimCLR; nosotros usamos CONCH 🟡

- **Paper**: extractor `f` = ResNet18 entrenado con SimCLR
  (self-supervised) sobre los parches del propio dataset (`01_` §5).
- **OncoMets**: features **CONCH** — foundation model vision-language de
  patología (Lu et al., *Nature Medicine* 2024), preentrenado en ~1,17 M
  pares imagen-texto de patología. 512-dim, ya extraídas, read-only.
- **Implicación**: el componente #2 de DSMIL (contrastive learning, que
  el paper acredita con ≥14–16 % de accuracy, Tabla 3) **no se ejecuta**.
  CONCH es un extractor **más fuerte** que un ResNet18-SimCLR por dataset.
  La hipótesis razonable es que CONCH **cubre y supera** ese rol — pero
  **el paper nunca evaluó DSMIL sobre features de un foundation model**.
  Es un supuesto, no un hecho.
- **Evidencia medida (esta sesión)**: inspección de 6 `.pt` de CONCH —
  la norma L2 por parche es **≈22,65 con std 0,01** (rango 22,60–22,70),
  uniforme entre parches y entre slides. CONCH entrega features
  **efectivamente normalizadas**. Eso es **favorable** para el instance
  classifier lineal de DSMIL (`c = W_0·h`): un clasificador lineal sobre
  features semánticas y normalizadas es justo el caso fácil.
- **Severidad 🟡**: no es un bloqueante, pero es el supuesto más grande
  que cambia. Es positivo en expectativa, negativo solo si CONCH tuviera
  alguna patología de espacio de features que no anticipamos.
- **Mitigación**: smoke test temprano — entrenar 5 epochs en la task más
  chica y verificar que el instance scorer separa algo (no queda en
  azar). Barato y definitivo.

### A.2 — DSMIL nunca se evaluó en multi-clase desbalanceado 🔴

- **Paper**: Camelyon16 = **binario** (n=400). TCGA-lung = 2 subtipos
  **sin clase negativa**, bags balanceados (n=1054). Datasets MIL
  clásicos (MUSK/FOX/TIGER/ELEPHANT) = todos **binarios**. → **DSMIL no
  tiene ni una evaluación en multi-clase mutuamente excluyente, ni en el
  régimen de desbalance severo de OncoMets.**
- **OncoMets**: las 4 tareas prioritarias incluyen casos multi-clase y
  con desbalance severo (CLAUDE.md, Hallazgo 5: `gh_dif_tubular` score_1=4
  en train; `cdi_necrosis` presente_focal=1). MicroCalcificaciones
  ~3.000 slides.
- **Implicación**: estamos llevando DSMIL a un régimen **fuera de su
  envolvente de validación**. El paper sí *describe* el caso multi-clase
  (§3.2, bag embedding `[L×C]`), pero describir ≠ validar.
- **Severidad 🔴**: es el supuesto roto más serio. No invalida la
  propuesta, pero **debe decirse explícito en la reunión**: el resultado
  de DSMIL en OncoMets es territorio no medido por el paper.
- **Mitigación**: (1) la integración conserva el bag classifier softmax +
  CrossEntropy de CLAM → la salida multi-clase es correcta por
  construcción (`03_` §6). (2) Conservar `--weighted_sample` de CLAM
  (el loop de DSMIL no tiene weighted sampling). (3) Evaluar sobre el
  subset binario efectivo, igual que Objetivos 1 y 2.

### A.3 — Magnificación de extracción: desconocida 🟡

- **Paper**: parches 224×224, magnificación **20×** (single-scale);
  20×+5× para multiescala (`01_` §6).
- **OncoMets**: la magnificación con que Sebastián extrajo las features
  CONCH **no está documentada** en CLAUDE.md ni es derivable de lo que
  tengo. `clam_environ/environ/` tiene `features/pt_files/` (CONCH) y
  `features_256/pt_files/` (CONCH "@ patch 256") — sugiere que hay más de
  una configuración de parche.
- **Implicación**: si la magnificación difiere mucho de 20×, el campo de
  visión por parche cambia y la noción de "parche crítico focal" se
  desplaza. No rompe DSMIL, pero afecta la comparabilidad con los números
  del paper.
- **Severidad 🟡** — **NO inventar el valor**. Es la pregunta C.5.

---

## B. Riesgos técnicos de la integración

### B.1 — El instance scorer de DSMIL solo entrena si se supervisa 🔴

- **Hallazgo (cadena de gradiente)**: el instance scorer `c = W_0·h`
  (Stream 1) cumple dos roles: (a) elegir el parche crítico vía
  `argmax(c)`, (b) ser, vía max-pooling, una de las dos predicciones.
  El `argmax` (`dsmil.py:52`, `torch.sort`) es **no diferenciable**: no
  propaga gradiente al `W_0`. Por lo tanto **`W_0` recibe gradiente
  ÚNICAMENTE de una loss aplicada directamente a `c`** (el `max_loss` de
  `train_tcga.py:70`).
- **Consecuencia**: si la integración "mantiene solo la loss de CLAM" y
  **descarta el `max_loss` de DSMIL**, el instance scorer `W_0` **nunca
  se entrena** → se queda en su inicialización → el "parche crítico" lo
  elige una proyección lineal aleatoria fija. El Stream 2 quedaría
  midiendo "distancia a un parche de referencia arbitrario", vaciando de
  sentido la idea de instancia crítica.
- **Severidad 🔴**: invalida silenciosamente el mecanismo central de
  DSMIL si no se atiende. Es el riesgo técnico más importante de esta
  investigación.
- **Mitigación**: la integración **no puede** quedarse solo con la loss
  de CLAM tal cual. Hay que **conservar un término de supervisión del
  Stream 1**. Opciones:
  1. Loss = `bag_weight·L_bag(CLAM, CE) + (1−bag_weight)·L_max(DSMIL,
     CE-sobre-el-parche-máximo)` — reemplaza la rama instance de CLAM por
     la de DSMIL, manteniendo CE para coherencia multi-clase.
  2. Loss = `w1·L_bag + w2·L_inst(CLAM, SmoothTopSVM) + w3·L_max(DSMIL)`
     — conserva ambas ramas instance; tres términos.
  3. Mantener la rama instance de CLAM operando sobre la atención `β` de
     DSMIL, y supervisar `c` con un L_max adicional de bajo peso.
  → esto **es** la pregunta C.2; ya no es una preferencia, es una
  necesidad arquitectónica. Debe cerrarse en la reunión.

### B.2 — Inestabilidad del argmax por norma de features 🟢 (descartado con datos)

- **Riesgo planteado**: si las features CONCH tuvieran normas L2 muy
  dispares entre parches, el score lineal `W_0·h` estaría dominado por la
  norma y no por el contenido → `argmax` inestable / sesgado.
- **Evidencia medida (esta sesión)**: norma L2 por parche **≈22,65, std
  0,01**, rango 22,60–22,70, **uniforme entre parches y entre slides**
  (6 `.pt` inspeccionados). Las features CONCH están efectivamente
  normalizadas.
- **Severidad 🟢**: **riesgo descartado** con datos. No hace falta
  normalización extra antes del aggregator. (Aun así, una `LayerNorm` o
  L2-norm explícita es barata y a prueba de futuro si cambia la
  extracción; opcional.)

### B.3 — Max-pooling poco diferenciable + bags grandes 🟡

- **Riesgo**: el `max` sobre N (`train_tcga.py:68`) propaga gradiente
  **solo al parche ganador**. Con N grande, el término `max_loss` da
  gradiente a 1 de N parches por bag por época → señal rala y ruidosa.
- **Atenuante**: el Stream 2 (`bag_loss`) da gradiente **denso** a todos
  los parches vía los pesos de atención `β`. El diseño dual de DSMIL
  precisamente compensa la ralitud del Stream 1 con la densidad del
  Stream 2. No es tan grave como el max-pooling puro.
- **Comparación con CLAM**: la rama instance de CLAM usa `SmoothTop1SVM`
  sobre `2B` parches — una versión **suave** del top-1, diseñada justo
  para evitar la no-diferenciabilidad del max duro. Punto a favor de la
  opción de mitigación B.1.3 (conservar la rama instance suave de CLAM).
- **Severidad 🟡**: manejable. Mitigación: asegurar que el término del
  Stream 2 esté presente y con peso suficiente; preferir, si hay ruido en
  los logs, una variante suave para el Stream 1.

### B.4 — OOM en la A6000 con bags grandes 🟢 (descartado con datos)

- **Riesgo planteado**: si N fuera 50k+ parches, ¿OOM en la A6000 única
  (49 GB)?
- **Evidencia medida (esta sesión)**: muestra de 6 slides → N entre
  **1.365 y 7.701 parches, media ~4.159**. Orden de magnitud: **miles**,
  no decenas de miles. (Es una muestra de 6 de 3.013 `.pt`; el máximo
  global podría ser mayor, pero el orden de magnitud es claro.)
- **Cálculo**: con N=50.000 y D=512 float32, el tensor de features pesa
  ~100 MB; `Q` [N,128] ~25 MB; activaciones+gradientes ~3–4× → < 1 GB por
  bag. DSMIL es O(N) (`03_` §7). En 49 GB hay margen de sobra.
- **Severidad 🟢**: **riesgo descartado**. DSMIL no agrega riesgo de OOM
  sobre CLAM. (El verdadero riesgo de memoria sería TransMIL con
  self-attention O(N²) — ver [`../alternativas_consideradas.md`](../alternativas_consideradas.md).)

### B.5 — `v` = Identidad por defecto (sin `W_v`) 🟡

- **Hallazgo** (`02_` §6, discrepancia 2): el código oficial usa
  `v = nn.Identity()` por defecto → el bag embedding es media ponderada
  de **features CRUDAS**, sin la matriz `W_v` que el paper define (Ec. 4).
- **Implicación**: con CONCH (512-dim, ya semántico y normalizado) puede
  bastar. Pero perdemos un grado de libertad que el paper sí formaliza.
- **Severidad 🟡**: bajo–medio. Mitigación: probar `passing_v=True`
  (activa el MLP de `v`) como variante en el smoke test; barato.

### B.6 — Reproducibilidad de los números del paper 🟢

- El README oficial reporta, con los *updates 2024*, métricas **mejores**
  que la tabla del paper (Camelyon16 AUC 0,961 vs 0,8944). El código
  actual no reproduce literal el paper. No es un riesgo para nosotros
  (no buscamos reproducir el paper, sino comparar DSMIL vs CLAM a
  igualdad de features), pero **conviene no citar “0,89 AUC” como si
  fuera lo que veríamos** — los números dependen de features, dataset y
  régimen, todos distintos a los nuestros.
- **Severidad 🟢**: solo una nota de honestidad para la reunión.

---

## C. Preguntas concretas para la reunión

> Lista para imprimir y llevar. Cada una con qué desbloquea.

**1. ¿Preferencia de módulo: DSMIL, TransMIL, HIPT u otro?**
   Razones técnicas o de equipo. — *Desbloquea*: decisión #6 del sprint;
   define si seguimos con DSMIL o se reescribe `propuesta_dsmil.md`.
   Contexto: ver [`../alternativas_consideradas.md`](../alternativas_consideradas.md).

**2. Si DSMIL: ¿loss compuesta tipo CLAM (`bag_weight`) o loss nativa de
   DSMIL (BCE en ambos streams)?**
   — *Desbloquea*: la implementación del training. **No es solo
   preferencia**: el Frente 4 §B.1 muestra que el instance scorer de
   DSMIL **no entrena** si no se conserva algún término de supervisión
   del Stream 1. Hay que elegir entre las 3 opciones de mitigación de
   B.1. Trade-off: la loss de CLAM hace que la única variable sea el
   aggregator (comparación limpia); la nativa de DSMIL replica el paper
   pero mete 2 variables.

**3. ¿Eduardo implementa otro módulo en paralelo, o ambos convergemos a
   uno?**
   — *Desbloquea*: decisión #3 (división de trabajo); evita esfuerzo
   duplicado.

**4. ¿Esperamos al dataset compartido HISTAI completo (faltan ~128 `.pt`)
   o arrancamos con lo que hay?**
   — *Desbloquea*: decisión #1; define cuándo empieza el entrenamiento.
   Dato: hoy hay **3.013 `.pt`** en `features/pt_files/` (CLAUDE.md
   registraba 2.935 → Sebastián sigue procesando).

**5. ¿A qué magnificación se extrajeron las features CONCH?**
   — *Desbloquea*: comparabilidad con DSMIL original (20×). Ver §A.3.
   Hay `features/` y `features_256/` — aclarar qué es cada una.

**6. ¿Hay anotaciones ROI para MicroCalcificaciones específicamente?**
   — *Desbloquea*: el upgrade del Objetivo 4 (heatmaps) a validación
   cuantitativa (IoU/Dice); también permitiría sanity-check de la
   atención de DSMIL.

**7. Si DSMIL se descarta, ¿cuál es la siguiente alternativa preferida?**
   — *Desbloquea*: plan B inmediato sin otra reunión. Candidatas
   ordenadas en `../alternativas_consideradas.md` (TransMIL antes que
   HIPT).

**8. ¿Convención del equipo para nombrar runs, guardar checkpoints y
   reportar a Benjamín?**
   — *Desbloquea*: que los resultados de Objetivos 1–4 sean comparables
   entre Ernesto, Eduardo y Sebastián, y consistentes con lo que espera
   Benjamín.

**9. ¿Cómo se reparte el tiempo de GPU si Eduardo y yo entrenamos en
   paralelo?**
   — *Desbloquea*: planificación realista. Contexto: GPU **única**
   (RTX A6000), partición SLURM única `debug`. Hoy mismo hay jobs en
   cola (4096/4097). Sin acuerdo, los hilos se bloquean entre sí.

**10. ¿Slides con < B parches tras CONCH: biopsias chicas esperables o
   fallo de detección de tejido upstream?**
   Las slides `histai_1536_slide_H&E_0` (6 parches CONCH) y
   `histai_1196_slide_H&E_0` (8 parches CONCH) tienen **menos de B
   parches** tras la extracción de features. ¿Es esperable para esos WSIs
   específicos (biopsias muy pequeñas) o sugiere un fallo de detección de
   tejido en el pipeline upstream? Para el Sprint 4 las filtré del train
   para desbloquear la ablation B=8 vs B=16 (split filtrado documentado en
   `splits_local/microcalcificaciones_pth_100_minpatch16/`).
   — *Desbloquea*: si es un bug upstream, conviene una regla general de
   `min_patches` en la generación de splits; si no, basta el filtro local.
   Distinto de la pregunta 4 (esas slides **sí** tienen `.pt`, solo que
   con muy pocos parches — no es el caso de los ~128 `.pt` ausentes).

---

## D. Síntesis de severidad

| Riesgo | Severidad | Estado |
|---|---|---|
| A.1 SimCLR→CONCH | 🟡 | Supuesto grande, expectativa positiva; smoke test lo cierra |
| A.2 multi-clase desbalanceado no validado | 🔴 | Decir explícito en reunión; mitigado por diseño (bag classifier CLAM) |
| A.3 magnificación desconocida | 🟡 | Pregunta C.5, no inventar |
| B.1 instance scorer sin gradiente | 🔴 | **Decide la loss**; pregunta C.2 |
| B.2 argmax inestable por norma | 🟢 | Descartado con datos (norma uniforme) |
| B.3 max-pooling poco diferenciable | 🟡 | Manejable; el Stream 2 compensa |
| B.4 OOM bags grandes | 🟢 | Descartado con datos (N ~miles) y cálculo |
| B.5 `v`=Identidad | 🟡 | Probar `passing_v=True` en smoke test |
| B.6 reproducibilidad del paper | 🟢 | Nota de honestidad |

**Dos riesgos 🔴**: A.2 (régimen no validado) y B.1 (el instance scorer
no entrena sin supervisión propia). Ninguno bloquea la propuesta, pero
**ambos deben enunciarse en la reunión** — B.1 además condiciona la
decisión de loss (pregunta C.2).
