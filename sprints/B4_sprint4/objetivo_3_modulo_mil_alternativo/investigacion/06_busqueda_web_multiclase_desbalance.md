# 06 — Búsqueda web: paper para el multiclase desbalanceado

> **Objetivo 3, Sprint B4 — investigación complementaria.**
> Continuación de [`05_papers_eduardo_desbalance.md`](05_papers_eduardo_desbalance.md).
> Búsqueda en la web (may 2026) de literatura reciente (2023–2025) que
> ataque nuestro problema: **clasificación multiclase / multi-etiqueta
> con desbalance severo y clases raras de poquísimas muestras en MIL
> sobre WSI de patología**.
>
> Se aplica el mismo análisis que a los papers de Eduardo, siguiendo la
> regla 9 de `CLAUDE.md` ("argumento antes de código": hipótesis +
> métrica de éxito explícitas).
>
> **Insumo para la reunión con Sebastián y Eduardo.** Sesión read-only:
> cero GPU, cero SLURM, cero modificación de `clam_environ/`.
>
> El PDF de HMIL **no se descargó** a `papers/` (workaround E de
> `CLAUDE.md`: no bajar artefactos externos sin pedido). Si el equipo
> quiere versionarlo, que Ernesto lo suba y lo agregue a `papers/README.md`.

---

## TL;DR — veredicto

| Paper | Qué es | ¿Ataca nuestro problema? | Recomendación |
|---|---|---|---|
| **HMIL** (Hierarchical MIL, IEEE-TMI 2024/25) | MIL que encoda la **jerarquía de etiquetas** en vez de tratar el problema como multi-clase plano | **Sí, en el diagnóstico**: nombra exactamente nuestro error ("flat multi-class"). Pero su arquitectura asume un **árbol**, y nuestro espacio es un **lattice multi-etiqueta** | **CONDICIONAL** — adoptar el *principio* y componentes transferibles; NO adoptarlo entero |
| **FR-MIL** (Distribution Re-Calibration MIL, IEEE-TMI 2024) | Re-calibra la distribución del bag; balanced-batch sampling | Parcial: ataca desbalance, pero formulado para **MIL binario** | Candidato secundario — fuente de la idea de *balanced-batch sampling* |

**Conclusión de una línea**: HMIL es la **validación externa más fuerte**
de que el problema está mal *formulado* (multi-clase plano sobre un
espacio de etiquetas estructurado) — el mismo diagnóstico de
`resultados.md`. Pero su arquitectura exacta **no transfiere 1:1**: HMIL
asume una taxonomía en árbol y nuestro problema es un multi-etiqueta de
3 tejidos (un lattice, no un árbol). La reformulación en 3 binarios
(doc 05) sigue siendo la dirección primaria; de HMIL se toman piezas.

---

## 0. Cómo se buscó (reproducibilidad)

Búsquedas (WebSearch, may 2026):

1. `multi-label multiple instance learning whole slide image
   classification class imbalance rare classes 2024 2025`
2. `long-tailed multi-class classification computational pathology MIL
   WSI 2024 2025`
3. Búsquedas dirigidas a los dos candidatos más fuertes (HMIL, FR-MIL).

Candidatos revisados y por qué se descartaron como foco principal:

| Candidato | Por qué no es el foco |
|---|---|
| **EfficientMIL / Long-MIL / LiteMIL** | Atacan **eficiencia computacional** (complejidad lineal, secuencias largas), no el desbalance multiclase. |
| **MICIL** (class-incremental) | *Class-incremental learning* — añadir clases nuevas en el tiempo. No es nuestro problema. |
| **"Beyond accuracy / Reliability" (PLOS One 2025)** | Aporta la idea de métricas de fiabilidad — ya cubierto por nuestro hallazgo de balanced accuracy + matriz de confusión. Útil como respaldo, no como método. |
| **Masked Hard Instance Mining** | Minería de instancias difíciles *dentro* del bag — desbalance a nivel instancia, no de clase. Mismo encuadre erróneo que DAML (doc 05 §3). |
| **FR-MIL** | Sí ataca desbalance, pero formulado para MIL **binario** → candidato secundario (§4). |
| **HMIL** | **Foco principal** — único que ataca explícitamente la *formulación plana* de un espacio de etiquetas estructurado. |

---

## 1. HMIL — *Hierarchical Multi-Instance Learning for Fine-Grained WSI Classification*

> Jin et al., *IEEE Transactions on Medical Imaging*, 2024/2025.
> arXiv:2411.07660 · código: `github.com/ChengJin-git/HMIL`.

### 1.1 Idea central

HMIL parte de una observación que es **palabra por palabra nuestro
hallazgo**: *"existing MIL methods often overlook hierarchical label
correlations, **treating fine-grained classification as a flat
multi-class classification task**."*

La idea: cuando las clases finas tienen una **estructura** (una clase fina
"anida" dentro de una clase gruesa), tratarlas como categorías
independientes y mutuamente excluyentes **tira esa estructura**, que es
justamente señal de regularización gratis. HMIL la usa.

Arquitectura (resumen técnico):

- **Dos ramas**: una **gruesa** (Kc clases) y una **fina** (Kf clases).
- **Atención por clase** (gated attention) a nivel de instancia: calcula
  una matriz de atención por cada clase, no una sola.
- **Alineación jerárquica a nivel de instancia (HAM)**: una matriz de
  mapeo `ℳ ∈ ℝ^{Kf×Kc}` proyecta la atención fina a la gruesa; una
  pérdida de similitud coseno fuerza que coincidan.
- **Alineación jerárquica a nivel de bag (HBA)**: los logits finos `p_f`
  se proyectan a logits gruesos vía `ℳ` (`Ỹ_c = ℳ·p_f`) y se exige
  consistencia con la etiqueta gruesa real. Es decir: **la predicción
  fina tiene que "sumar bien" a la predicción gruesa**.
- **Supervised contrastive learning (SCL)** sobre las features finas del
  bag: junta lo de la misma clase fina, separa lo de clases distintas
  (`τ = 0.1`).
- **Ponderación dinámica curricular**: `β = 1 − e/E` (e = época actual).
  El entrenamiento **empieza guiado por lo grueso** (β alto: la tarea
  fácil) y **transita hacia el refinamiento fino contrastivo** (β bajo).
  La pérdida total:
  `L = β·(L_ce^c + L_ia + L_ba) + (1−β)·L_reg + L_ce^f`.

Datasets y resultados relevantes (10-fold CV / bootstrap):

| Dataset | Dominio | Kc / Kf | Acc fina | AUC fina | **Sensibilidad fina** | F1 fina |
|---|---|---|---|---|---|---|
| **BRACS** | **mama, histología** | 3 / 7 | 55,6 % | 83,0 | **38,6 %** | 39,0 % |
| PANDA | próstata | 3 / 5 | 63,4 % | 89,4 | 58,4 % | 58,2 % |
| CCC | cérvix, citología | 2 / 6 | 80,3 % | 91,2 | **41,0 %** | 44,4 % |

HMIL le gana a ABMIL, DSMIL, HIPT — y, clave, logra **AUC por clase
balanceado** (Figura 4): los competidores se sesgan a las clases
grandes, HMIL no. Backbone: ResNet-50 ImageNet (no foundation model).
Solo etiqueta de slide, sin anotaciones de instancia.

### 1.2 Aplicabilidad a microcalcificaciones — el matiz que decide todo

HMIL **acierta el diagnóstico** pero **su arquitectura no calza directo**.
Hay que ser quirúrgico con esto:

**Lo que HMIL valida (a favor):**

- Es la confirmación externa, revisada por pares y en IEEE-TMI, de que
  *"multi-clase plano sobre etiquetas estructuradas"* es un error de
  formulación, no un detalle. Exactamente el hallazgo de `resultados.md`.
- Evaluado en **BRACS — mama, histología** (7 lesiones mamarias:
  N, PB, UDH, FEA, ADH, DCIS, IC). Es el dataset **más cercano a
  OncoMets** de todos los papers analizados (Eduardo + este). Que HMIL
  funcione en BRACS sube su credibilidad para nuestro dominio.
- Trabaja con **solo etiquetas de slide** — compatible con nuestro setup.
- Su SCL y su ponderación curricular son piezas **transferibles** a
  cualquier formulación.

**Lo que NO calza (el problema estructural):**

HMIL asume una **taxonomía en árbol**: *"each fine-grained class maps to
**exactly one** coarse category"* — la matriz `ℳ` codifica un padre único
por clase fina. BRACS lo cumple (cada lesión anida en un grupo). PANDA lo
cumple (ISUP→riesgo).

**Nuestro problema NO es un árbol.** Las 8 clases son el **conjunto
potencia** de 3 tejidos {carcinoma invasivo, CDIS, tejido no neoplásico}.
La clase `en_carcinoma_invasivo-en_cdis` pertenece **a la vez** a
"carcinoma invasivo" y a "CDIS" → tiene **dos padres**. Es un **lattice
(DAG) multi-etiqueta**, no una jerarquía en árbol. La matriz `ℳ` de HMIL,
tal cual, **no puede representar nuestro espacio de etiquetas**.

```
   HMIL asume (árbol)            Microcalcificaciones (lattice multi-label)

        riesgo                       carc      cdis      tejido
       /  |  \                        |  \    /   \     /   |
    sub1 sub2 sub3              {carc} {carc,cdis} {cdis,tejido} ...
   (1 padre por hoja)          (una combinación tiene 2-3 padres)
```

**Consecuencia.** Hay dos formas de "salvar" HMIL para nuestro caso, y
ninguna lo hace la respuesta directa:

- **(A) Proyección en árbol válida.** Sí existe **un** árbol legítimo:
  coarse = binario `{no_identificado / hay_localización}` (¿hay alguna
  microcalcificación localizada?), fine = las 8 clases. Cada clase fina
  mapea a exactamente un coarse → `ℳ` válida. Esto **sí** es un HMIL
  legítimo y aportaría: la tarea gruesa "¿hay localización?" es binaria
  con 333 positivos / 2739 negativos — desbalanceada pero muy
  aprendible, y da regularización a la rama fina. **Pero** la rama fina
  sigue con las 8 clases planas: la clase triple sigue teniendo **6
  slides**. HMIL la *mitiga* (señal gruesa + SCL + currículum); **no
  disuelve la escasez fabricada**.

- **(B) Reformulación multi-etiqueta (doc 05).** La reformulación en 3
  binarios **sí** maneja el lattice correctamente — porque no intenta
  forzar un árbol: cada slide aporta su etiqueta a las tareas que
  correspondan. Y **re-cuenta**: la clase triple de 6 slides se disuelve
  en 68/121/195 positivos. La reformulación ataca la raíz (P2, escasez
  fabricada); HMIL-(A) solo la amortigua.

**Caveat honesto — el techo de datos.** HMIL es el método jerárquico
SOTA, y aun así su **sensibilidad fina es ~38–41 %** en BRACS y CCC.
Es decir: incluso encodando la jerarquía perfectamente, las clases finas
raras siguen costando. Es la **misma lección** del paper de Chen & Xu
(doc 05 §2): la estructura ayuda, pero el `n` de la clase rara es un
techo duro. HMIL no es una excepción — lo confirma.

### 1.3 Recomendación — **CONDICIONAL**

**Adoptar el principio y las piezas transferibles; NO adoptar HMIL
entero esperando que esquive el problema de formulación o el techo de
datos.**

Concretamente:

1. **Usar HMIL como argumento en la reunión** — es respaldo IEEE-TMI,
   en mama (BRACS), de que la formulación plana es el error. Refuerza la
   propuesta de reformular.
2. **No** sustituir la reformulación (doc 05) por HMIL: HMIL fuerza una
   aproximación en árbol de un espacio que es multi-etiqueta. La
   reformulación modela el lattice **sin aproximar**.
3. **Sí tomar prestadas 3 piezas de HMIL, compatibles con la
   reformulación:**
   - **Rama gruesa `{no_identificado / hay_localización}`** como
     regularizador — una cabeza binaria auxiliar muy aprendible que da
     señal temprana. Encaja como una 4.ª tarea del esquema multi-task.
   - **Pérdida de alineación a nivel de bag (HBA)** como **regularizador
     de consistencia**: si las 3 cabezas binarias predicen todas
     "negativo", la cabeza gruesa debe predecir `no_identificado`, y
     viceversa. HBA es justamente el mecanismo para forzar esa
     coherencia entre cabezas.
   - **Supervised contrastive learning** sobre las features de bag y la
     **ponderación curricular** `β = 1−e/E` (fácil→difícil) como
     refinamientos de entrenamiento.

> **Argumento antes de código (regla 9).**
> **Hipótesis (rama gruesa estilo HMIL)**: añadir una cabeza binaria
> auxiliar `¿hay localización de microcalcificación?` (coarse) al modelo
> reformulado, con una pérdida de consistencia que ligue las 3 cabezas
> binarias a esa cabeza gruesa, mejora el balanced accuracy promedio de
> las 3 tareas — porque la tarea gruesa es muy aprendible (333 positivos)
> y propaga señal a las cabezas finas con pocos positivos.
> **Métrica de éxito**: balanced accuracy promedio de las 3 tareas
> binarias, *con* rama gruesa + consistencia vs *sin* ella, mismo
> backbone y épocas. Éxito si Δ ≥ +0,03. Verificación falsable barata:
> es un ablation de una cabeza, no un cambio de arquitectura.
> **Subordinada a**: la reformulación (doc 05) y a la precondición de
> qué es `no_identificado` — si `no_identificado` no es "sin
> microcalcificación", la rama gruesa cambia de significado.

---

## 2. Candidato secundario — FR-MIL

> Chikontwe et al., *FR-MIL: Distribution Re-Calibration-Based MIL with
> Transformer*, IEEE-TMI 2024. Código: `github.com/PhilipChicco/FRMIL`.

**Idea central**: re-calibra la distribución de instancias de un bag
usando las estadísticas de la *max-instance* (el parche crítico),
asumiendo que en MIL **binario** los bags positivos tienen features de
mayor magnitud; modela los bags positivos como *out-of-distribution* con
una *metric feature loss*. Aporte clave para nosotros: usa
**balanced-batch sampling** (positivos y negativos en cada batch) en
vez del modo single-batch típico.

**Aplicabilidad**: parcial. FR-MIL está formulado para **MIL binario** —
su supuesto central (positivo = features de mayor magnitud) no se traslada
a multi-clase. Pero tras la reformulación en 3 binarios (doc 05), **cada
tarea es binaria** → FR-MIL vuelve a ser aplicable por tarea. Su
**balanced-batch sampling** es una alternativa más fina al
`--weighted_sample` de CLAM (que muestrea con reemplazo y causó el bug
`topk`, ver `docs/workarounds.md`).

**Recomendación**: **secundario / opcional**. No es la dirección; es una
fuente de la idea de *balanced-batch sampling* por si el
`--weighted_sample` actual se queda corto en las tareas binarias muy
desbalanceadas (tarea A, 2,2 % positivos). Registrar la idea, no el
módulo entero.

---

## 3. Dónde encaja HMIL — el stack de 4 niveles del doc 05

El doc 05 ordenó las soluciones en 4 niveles. HMIL es interesante
porque **cruza dos niveles**:

```
  NIVEL                        PIEZA                        ¿HMIL?
  ──────────────────────────────────────────────────────────────────────
  1. Formulación del problema  Reformular 8 → 3 binarias     HMIL valida
     (raíz)                                                  el diagnóstico
                                                             del nivel 1
  2. Optimización              PCGrad                        —
  3. Loss / muestreo           Focal loss, label smoothing   HMIL aporta:
                               balanced-batch (FR-MIL)       SCL, currículum
  4. Arquitectura / agregador  DSMIL · DAMIL                 HMIL es una
                                                             arquitectura
                                                             nivel-1-aware
```

La lectura importante: **HMIL hace, a nivel de arquitectura, lo que la
reformulación hace a nivel de formulación** — ambos atacan la misma raíz
(no tratar un espacio de etiquetas estructurado como multi-clase plano).
Por eso HMIL **no es una pieza nueva del stack** sino una **confirmación
del nivel 1** más un par de componentes para el nivel 3. No cambia la
dirección recomendada; la refuerza.

---

## 4. Conclusión

1. **HMIL es la mejor evidencia externa de que la dirección de
   `resultados.md` es correcta.** Un paper IEEE-TMI 2024/25, evaluado en
   mama (BRACS), cuyo punto de partida es palabra por palabra nuestro
   hallazgo: el multi-clase plano sobre etiquetas estructuradas es un
   error de formulación.
2. **HMIL no reemplaza la reformulación.** Su arquitectura asume una
   **taxonomía en árbol**; nuestro espacio de etiquetas es un **lattice
   multi-etiqueta** de 3 tejidos. La reformulación en 3 binarios (doc 05)
   modela ese lattice **sin aproximar**; HMIL lo forzaría a un árbol.
3. **De HMIL se adoptan piezas, no el módulo:** la rama gruesa
   `{no_identificado / hay_localización}` como regularizador, la pérdida
   de consistencia entre cabezas (HBA), el supervised contrastive
   learning y la ponderación curricular `β = 1−e/E`.
4. **El techo de datos sigue ahí.** HMIL, el método jerárquico SOTA,
   logra solo ~38–41 % de sensibilidad fina. La estructura ayuda; no
   fabrica datos. Coherente con Chen & Xu (doc 05) y con
   `resultados.md` Hallazgo 4.
5. **FR-MIL** queda como fuente secundaria de la idea de *balanced-batch
   sampling* para las tareas binarias reformuladas.

**Dirección recomendada (sin cambios respecto al doc 05, ahora
reforzada):** reformulación multi-etiqueta en 3 tareas binarias +
PCGrad, con la rama gruesa estilo HMIL y la consistencia entre cabezas
como mejora de regularización. El módulo MIL (CLAM vs DSMIL vs DAMIL)
sigue siendo un eje ortogonal que se decide aparte.

### Pregunta nueva para la reunión

Extiende las de [`05_papers_eduardo_desbalance.md`](05_papers_eduardo_desbalance.md) §6.

| # | Pregunta | Qué desbloquea |
|---|---|---|
| 15 | ¿Vale la pena versionar el PDF de HMIL en `papers/` y/o explorar su código (`github.com/ChengJin-git/HMIL`) como referencia para la rama gruesa + consistencia? | Decide si HMIL pasa de "argumento" a "referencia de implementación" para las piezas transferibles. |

---

## Anexo — fichas BibTeX-lite

- **HMIL** — Jin, C. et al. *HMIL: Hierarchical Multi-Instance Learning
  for Fine-Grained Whole Slide Image Classification*. IEEE Transactions
  on Medical Imaging, 2024/2025. arXiv:2411.07660.
  Código: `github.com/ChengJin-git/HMIL`.
- **FR-MIL** — Chikontwe, P. et al. *FR-MIL: Distribution
  Re-Calibration-Based Multiple Instance Learning With Transformer for
  Whole Slide Image Classification*. IEEE Transactions on Medical
  Imaging, 2024. Código: `github.com/PhilipChicco/FRMIL`.
