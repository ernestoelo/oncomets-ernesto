# Resultados — Sprint 7: interpretabilidad CLAM vs Mammoth

> Job 4589 (entrenamiento pareado) cerrado el 18-jul-2026 14:20:55.
> Pre-registro: `prereg_entrenamiento_interp.md`. Política de eval B5.
> Commit de la verdad de campo: `684723b`.

## 1. Integridad del entrenamiento

30/30 runs completos (3 tareas × 2 brazos × 5 folds): 30 checkpoints, 30 `summary.csv`,
30 `split_*_results.pkl`, las 3 tareas con marca `done` y cero errores en el `.err`
(solo `FutureWarning` de `kaiming_uniform`, benigno).

**Paridad verificada, no asumida**: el md5 de los `slide_id` de test coincide fold a
fold entre brazos en las 3 tareas → el Δ pareado es válido por construcción
([[patron-paired-comparison-reuso-splits]]). Ambos brazos corrieron 52 épocas por fold
(`stop_epoch=50` hardcodeado + paciencia 20).

## 2. Métricas (política B5: balanced_acc Y AUC juntos)

| Tarea | n_test/fold | CLAM bal | MAM bal | Δ bal (folds+) | CLAM AUC | MAM AUC | Δ AUC (folds+) |
|---|---|---|---|---|---|---|---|
| tipo_histologico (3 clases) | ~202 | 0.665 ± 0.056 | 0.655 ± 0.047 | −0.010 ± 0.017 (1/5) | 0.833 ± 0.043 | 0.821 ± 0.056 | −0.012 ± 0.025 (3/5) |
| LVI `_ci_reform` | ~83 | 0.657 ± 0.040 | 0.634 ± 0.050 | −0.023 ± 0.086 (2/5) | 0.720 ± 0.032 | 0.684 ± 0.056 | −0.036 ± 0.073 (2/5) |
| CDIS `_ci_reform` | ~85 | 0.668 ± 0.098 | **0.742 ± 0.099** | **+0.074 ± 0.033 (5/5)** | 0.765 ± 0.111 | **0.825 ± 0.086** | **+0.060 ± 0.042 (5/5)** |

### Recall por clase (confusión sumada sobre los 5 folds)

| Tarea | Clase | n | Recall CLAM | Recall Mammoth |
|---|---|---|---|---|
| tipo_histologico | carcinoma_invasivo_tipo_no_especifico | 802 | 0.817 | 0.839 |
| tipo_histologico | carcinoma_lobulillar_invasivo | 121 | 0.744 | 0.769 |
| tipo_histologico | otros | 90 | 0.433 | 0.356 |
| CDIS | no | 65 | 0.477 | 0.569 |
| CDIS | si | 364 | 0.860 | 0.915 |
| LVI | ausente | 235 | 0.723 | 0.694 |
| LVI | presente | 181 | 0.591 | 0.575 |

**tipo_histologico y LVI confirman lo pre-registrado**: Δ dentro del ruido
(std ≥ |media|), consistente con el Hallazgo 12. La clase `otros` de tipo es la que
más sufre bajo Mammoth (0.433 → 0.356).

### El caso CDIS: la "sorpresa" que el pre-registro anticipó

El prereg §4 fijó: *"Un Δ grande y consistente a favor de Mammoth sería sorpresa
(a investigar, no a celebrar)"*. Es lo que ocurrió, y se reporta en ese registro.

Lo que sostiene la señal:
- 5/5 folds positivos en balanced_acc **y** en AUC, con std < |media| en balanced_acc.
- **No hubo colapso** pese al 85% positivo, y **suben los dos recalls** (`no`
  0.477→0.569, `si` 0.860→0.915). Eso descarta la firma de mover el umbral, que sube
  uno y hunde el otro (Hallazgo 14, [[calibracion-operating-point-palanca-b5]]).
- El AUC sube 5/5 → mejoró el **ranking**, no el punto de operación.
- **Corroborado en validación**: el mejor `val_loss` de Mammoth es menor que el de CLAM
  en 4/5 folds, y `val_loss` es el criterio de selección de checkpoint → no es un
  artefacto del test set.

Lo que obliga a frenar antes de llamarlo mejora:
- **n chico**: 65 negativos en total (~13 por fold); cada negativo vale ~7.7 puntos de
  recall de la clase 0. En bruto son 6 negativos y 20 positivos más acertados sobre 429.
- **`_ci_reform` es formulación nueva**, jamás incluida en las 12 configuraciones de
  Mammoth que cerraron el Hallazgo 12 → no contradice esos resultados en el mismo
  terreno; abre terreno nuevo.
- **Invierte el patrón declarado** en el Hallazgo 12 ("el efecto lo gobierna el balance:
  leve a favor en las balanceadas, nulo o en contra en las desbalanceadas"). Acá la
  tarea **más desbalanceada** (85/15) es la que gana y la **balanceada** (LVI 56/44) la
  que regresa.

**No se reabre el eje de rendimiento.** El Hallazgo 12 sigue cerrado; reabrirlo exige
regla 9.b (pre-registro nuevo, hipótesis primaria/alternativa/regresión, branch,
reviewer). Queda como candidato a réplica con más semillas o folds antes de presentarlo
a nadie como mejora.

## 3. Entregable central: comparación de atención CLAM vs Mammoth

7 slides (una por clase y tarea), todas del **test set del fold 0** (no vistas en
entrenamiento) y **bien clasificadas por ambos brazos**, para comparar *dónde mira* cada
uno sin el ruido de un error. Tooling: `scripts/clam_vs_mammoth_attention.py`.

Es apples-to-apples por construcción: `CLAM_MB_Mammoth` es subclase de `CLAM_MB` y
hereda su `forward`, así que la atención de ambos brazos sale del mismo código
(`model(h, attention_only=True)`). Gotcha aplicado: eso devuelve A **pre-softmax**; se
normaliza sobre los N parches antes de visualizar.

| Slide | Tarea | Clase | N parches | Spearman | Jaccard top-5% | Entropía CLAM | Entropía Mammoth |
|---|---|---|---|---|---|---|---|
| TCGA-AO-A12D | tipo | inv. tipo no especifico | 7097 | 0.848 | 0.079 | 0.873 | 0.929 |
| TCGA-AC-A8OS | tipo | lobulillar invasivo | 4201 | 0.885 | 0.243 | 0.760 | 0.830 |
| TCGA-E9-A1NE | tipo | otros | 5592 | 0.669 | 0.315 | 0.341 | 0.675 |
| TCGA-A7-A4SB | CDIS | no | 2793 | 0.921 | 0.261 | 0.887 | 0.938 |
| TCGA-D8-A1XB | CDIS | si | 16442 | 0.847 | 0.202 | 0.642 | 0.927 |
| TCGA-D8-A1XW | LVI | ausente | 22206 | 0.796 | 0.101 | 0.985 | 0.975 |
| TCGA-D8-A1X5 | LVI | presente | 28170 | 0.668 | 0.008 | 0.978 | 0.986 |

**Agregado (n=7):** Spearman 0.805 (rango 0.668–0.921) · Jaccard top-5% 0.172
(0.008–0.315) · Jaccard top-1% 0.073 · entropía CLAM 0.781 vs Mammoth 0.894
(Δ +0.113, **6/7 slides con Mammoth más difuso**).

### Lectura

1. **Coinciden en el mapa grueso.** La correlación de rangos alta (0.805 medio) dice que
   ambos ordenan el tejido de forma parecida: la región que importa es la misma.
2. **Difieren en los picos.** El solapamiento del top-5% de parches es bajo (0.172) y el
   del top-1% casi nulo (0.073). O sea: **mismo barrio, distintas casas**. Los parches
   concretos que cada modelo pone arriba son en su mayoría distintos.
3. **Mammoth reparte la atención; CLAM la concentra.** Mammoth es más difuso en 6/7
   slides. El contraste más fuerte está en la slide CDIS positiva (0.642 → 0.927) y en
   `otros` de tipo (0.341 → 0.675), justo las dos donde CLAM más se concentra.

La observación de que la mayor difusión aparezca en CDIS, la tarea donde Mammoth también
mide mejor, es **sugerente pero no demostrada**: con 7 slides no se puede atribuir la
diferencia de métrica a la forma de la atención. Queda como hipótesis, no como
explicación.

**Nombres de tejido**: cuando se describan las regiones, va la advertencia de
[[mammoth-interpretabilidad-objA]] — son **lectura visual nuestra, no anotación**; no
hay ground truth de tejido por parche y el sign-off de patólogo sigue pendiente.

Figuras por slide en `results/b7_mammoth_interp/interpretabilidad/<tarea>/<slide>/`:
`attention_clam.png`, `attention_mammoth.png`, `attention_side_by_side.png` (CLAM |
Mammoth | delta) y `attention_stats.json`.

### 3.1 Anatomía del desacuerdo: cómo conviven ρ=0.885 y Jaccard=0.243 (23-jul)

La pregunta natural al ver la tabla ("ordenan casi igual" pero "comparten 1 de cada 4 del
top") tiene respuesta medible. Recalculado sobre `TCGA-AC-A8OS` (N=4201, k=5 % = 210
parches; los puntajes por parche no se guardan, se re-derivan con
`clam_vs_mammoth_attention.py`):

**Los parches en disputa no están en el fondo del otro modelo.**

| Conjunto | Puesto mediano en el **otro** modelo | En la mitad inferior |
|---|---|---|
| Los 128 del top de CLAM que Mammoth no marca | **721 de 4201** (percentil 17 %) | **0 %** |
| Los 128 del top de Mammoth que CLAM no marca | **422 de 4201** (percentil 10 %) | **0 %** |

Ni un solo parche en disputa cae en la mitad de abajo del otro modelo; el peor caso está en
el puesto 1577 (tercio superior). Además el top-5 % de CLAM concentra el **21.5 %** de toda
la atención de Mammoth, y el de Mammoth el **31.1 %** de la de CLAM (si fueran
independientes: 5 %).

**Mecanismo: la cola alta está aplastada.** En Mammoth el parche #210 pesa solo **1.20×** el
#420 (en CLAM, 2.19×). Cortar al 5 % con esa diferencia es trazar una raya donde los valores
están casi empatados → la membresía del top es inestable, mientras que la correlación de
rangos casi no se entera de que un parche se mueva del puesto 210 al 420 sobre 4201.

**Las dos métricas contestan preguntas distintas** — la correlación, si coinciden en el
orden general; el solapamiento, si coinciden en la selección exacta de los 210 mejores. Las
dos pueden ser ciertas a la vez.

> **No usar como hallazgo:** la correlación restringida a la unión de los dos tops da −0.426,
> pero es **artefacto de selección** (condicionar sobre "estar arriba en al menos uno"), no
> evidencia de orden invertido.

## 4. Hallazgo lateral: la geometría del parche no se puede inferir de la magnificación

Al montar los heatmaps apareció un **bug en el tooling heredado de OBJ-A**.
`patch_size_at_level0()` (`mammoth_interpretability.py:254`) infiere el tamaño de parche
desde la magnificación y **fuerza el fallback de 40× cuando `mag <= 20`**. Sobre las 7
slides devolvía **512 px**, cuando la geometría real de las coords del h5 es **448 px**
en todas (= el parche de magnificación de Sebastián, 448@×40→224). Cada parche se
dibujaba ~14% sobredimensionado.

Peor: `TCGA-AO-A12D` es **genuinamente 20×** (mpp 0.4992, `objective-power` 20 y
`AppMag` 20, los tres concordantes — acá el tag Aperio *no* miente) y la función la
habría tratado como 40×.

**Fix**: derivar el tamaño de parche de la **moda del paso entre coords contiguas del
h5** — las coords no mienten. Implementado en `clam_vs_mammoth_attention.py`
(`infer_patch_size_level0`) y expuesto como flag `--patch-size-level0` en
`mammoth_interpretability.py` (aditivo, default = comportamiento OBJ-A, no altera su
reproducibilidad).

### Consecuencia de datos: TCGA no es homogénea en magnificación

Muestreo de 200 de las 864 slides TCGA de estas 3 tareas (leído con openslide):

| Magnificación nativa | Slides | Campo físico de un parche de 448 px |
|---|---|---|
| ~40× (mpp 0.233–0.253) | 189 (94.5%) | 104–113 µm |
| **~20× (mpp 0.499)** | **7 (3.5%)** | **224 µm (el doble)** |
| ~61× (mpp 0.164) | 3 (1.5%) | 74 µm |
| sin mpp | 1 (0.5%) | no determinable |

Extrapolado a las 864 slides TCGA de estas tareas: ~30 slides reciben el doble de campo
físico por parche y ~13 reciben dos tercios. Esto **extiende
[[cohortes-magnificacion-fisica]]**: el confound de escala no vive solo *entre* cohortes
(TCGA vs privado vs HistAI), también **dentro de TCGA**, porque la extracción se
parametriza en píxeles a nivel 0 y no en µm/px físicos. Es minoritario y acotado, pero
es exactamente el modo de falla que esa memoria anticipa.

## 5. Q1 — ¿cuántos expertos/slots usa Mammoth?

Ver `respuesta_q1_expertos_slots.md` (generado por
`scripts/answer_q1_expertos_slots.py` sobre los `slot_usage.csv`).

> **Estado 19-jul: CERRADA con las 7/7 láminas.** El ruteo desatado terminó limpio el
> 18-jul 22:24 (`setsid`, ppid=1, log en `logs/b7_expert_interp_desatado.log`), tras morir
> dos veces por colgar del shell de la sesión (workaround J,
> [[proceso-cpu-largo-desatado-setsid]]).

«Peso por slot» = `combine_weights`, la segunda softmax sobre los E·S=300 slots
(`mammoth.py:411`) — **no** el top-k de parches por experto
([[mammoth-slot-routing-weight]]).

### 5.1 Respuesta

| Lámina | Parches | Slots efect. (de 300) | Expertos efect. (de 30) |
|---|---|---|---|
| `TCGA-A7-A4SB` (CDIS) | 2 793 | 89.7 | 30.0 |
| `TCGA-AC-A8OS` (tipo) | 4 201 | 156.0 | 30.0 |
| `TCGA-E9-A1NE` (tipo) | 5 592 | 147.5 | 30.0 |
| `TCGA-AO-A12D` (tipo) | 7 097 | 178.3 | 30.0 |
| `TCGA-D8-A1XB` (CDIS) | 16 442 | 180.3 | 30.0 |
| `TCGA-D8-A1XW` (LVI) | 22 206 | 196.4 | 30.0 |
| `TCGA-D8-A1X5` (LVI) | 28 170 | 162.4 | 30.0 |
| **media** | | **158.7** | **30.0** |

**Expertos: no están sobredimensionados.** 30.0/30 en las 7 láminas, y los cuantiles dan
`e50=15`, `e90=27` **idénticos en todas** — exactamente el reparto uniforme. Transversal a
las 3 tareas.

**Slots: ahí está el margen de recorte.** Media 158.7/300 (sd 34.6): cerca de la mitad del
presupuesto aporta poco al peso final.

**Triangulación por masa acumulada (23-jul, calculado sobre `respuesta_q1_expertos_slots.json`).**
Promediando las 7 láminas, **38.7 slots juntan el 50 % del peso** y **164.4 juntan el 90 %**.
Que ese 164.4 caiga tan cerca del `N_eff`=158.7 es lo que sostiene el "~160 de 300": dos medidas
independientes (entropía vs masa acumulada) apuntan al mismo lugar. Corolario a tener listo para
la repregunta: `N_eff`=158.7 **no** dice que 159 slots trabajen por partes iguales — la
distribución es sesgada y 39 slots llevan la mitad.

**Los expertos están en el techo teórico, no solo "altos".** Los valores exactos del JSON van de
**29.969 a 29.987 sobre un máximo de 30** (99.9 %). Como `N_eff = n` se alcanza **sólo** en el
reparto uniforme (máximo de la entropía), eso *es* reparto uniforme.

> **La cuenta, para explicarla.** Con `p_j = w_j / Σw` sobre los 300 slots (`w_j` =
> `mean_combine_weight` de la lámina): `H = −Σ p_j ln p_j` y `N_eff = exp(H)`. Forma equivalente:
> `N_eff = Π (1/p_j)^{p_j}`, la media geométrica ponderada de `1/p_j`, que es lo que le da unidades
> de "nº de slots". Calibración: uniforme sobre k ítems ⇒ `H = ln k` ⇒ `N_eff = k` exacto; cotas
> `1 ≤ N_eff ≤ n`. Se llama perplejidad (NLP) o número de Hill de orden 1 (ecología).

**La dispersión NO es por tarea, sigue al tamaño de la lámina.** Las dos láminas de CDIS cubren
casi todo el rango por sí solas (89.7, el mínimo de las 7, y 180.3, la segunda más
alta), lo que descarta el efecto de tarea. El orden
sigue al nº de parches: Spearman ρ=0.750 (p=0.052, n=7); excluyendo la lámina chica (2 793
parches, la mitad que la siguiente) queda **170.2 ± 18.1**. Lectura mecánica: menos parches,
menos morfología distinta que rutear. **La tendencia no es monótona**: la lámina más grande de
las 7 (28 170 parches) da 162.4 y rompe el orden, que es por qué ρ=0.750 y no 1.0. Conviene
decirlo antes de que lo vean en la tabla.

> **Fuerza de la evidencia.** Con n=7 esto **describe** el comportamiento, no lo establece:
> la correlación con el tamaño se apoya en **un solo** caso de lámina chica, y p=0.052 está
> al borde. Lo que sí es sólido es el resultado de expertos (idéntico en 7/7).

**Gotcha del agregador (fix `f0d043e`):** `answer_q1_expertos_slots.py` globeaba
`slot_usage.csv`, que es un artefacto **intermedio** — podía promediar una lámina en vuelo
(CSV a medio escribir) o de una corrida cortada, **sin avisar**. Ahora filtra por `meta.json`
(marcador final, misma regla que el driver reanudable) y reporta las excluidas.

### 5.2 La softmax por slot, tabla y mapa (23-jul)

Pedido de Ernesto para que Sebastián viera **literalmente** la segunda softmax, con la
cola de slots que pesan ~0. Generado por `scripts/build_slot_softmax_tables.py` (tablas) y
`scripts/slot_heatmaps_contraste.py` (mapas), ambos CPU post-hoc sobre los `slot_usage.csv`
ya existentes. Salidas en `sprints/B7_sprint7/slot_softmax/`.

**La cola es basura numérica, y el umbral a ojo es arbitrario.** En `TCGA-AC-A8OS`: ningún
slot vale exactamente 0 (el mínimo es `3.98e-05`, unas 84× menos que el uniforme 0.00333),
así que "contar los no nulos" da **300 siempre**. Y el conteo depende del corte elegido:

| Corte | Slots que pasan |
|---|---|
| > 0 | 300 |
| > 0.0001 | 299 |
| > el uniforme (0.333 %) | 91 |
| > 0.5 % | 53 |
| > 1 % | 25 |

De 25 a 300 según dónde se corte → **por eso `N_eff = exp(H)` es la medida honesta: no
tiene parámetro libre.** Triangula con la masa acumulada (38 slots = 51 %, 164 = 91 %,
contra `N_eff` 156) — dos medidas independientes convergen en ~160/300.

**Agregado por tarea** (`slot_softmax_resumen.csv`):

| Tarea | N_eff (promedio de tarea) | N_eff por lámina | Sobre el uniforme | ≈0 | Top-1 |
|---|---|---|---|---|---|
| tipo histológico | 199.3 | 156 / 178 / 148 | 103 | 197 | e12·s2 (3.72 %, 11.1× el uniforme) |
| CDIS | 160.1 | 90 / 180 | 82 | 218 | e13·s6 (3.24 %, 9.7×) |
| LVI | 195.9 | 162 / 196 | 98 | 202 | e6·s7 (3.22 %, 9.7×) |

> **Gotcha del promediado.** El `N_eff` de la columna "promedio de tarea" sale **inflado**
> respecto al por-lámina (199 vs ~161 en tipo): promediar distribuciones de láminas
> distintas **sube la entropía**. Para el argumento de recortar S hay que citar el
> **por-lámina**; la tabla por tarea sirve para *ver qué slots se activan*, no para
> re-medir cuántos. Por eso la tabla mini se emite **por lámina**.

**Mapa de calor por slot (no por experto).** Los heatmaps que ya existían
(`expertos/heatmaps/expert_N.png`) son por **experto** y usan la **primera** softmax
(`dispatch`); la tabla rankea **slots** con la **segunda** (`combine`). Contrastarlas
mezclaría dos niveles y dos softmax — y a nivel experto el ruteo es uniforme (30.0/30), así
que la tabla no discrimina ahí. `slot_heatmaps_contraste.py` toma `combine` **sin colapsar
el eje espacial N**, selecciona la columna del slot `(e,s)` y pinta el **top-15 % de
parches** de ese slot sobre el tejido (recorte visual; con todos los parches pintados el
contraste entre slots se aplasta). Es el análogo de la Fig. 3 del paper.

**Los slots top NO son redundantes entre sí** (medido sobre `TCGA-AC-A8OS`): la correlación
espacial de rangos entre los **top-8** slots tiene media **−0.00**, y el #1 (`e12·s2`) está
**anti-correlacionado con el #2** (`e5·s5`, **−0.62**) — encienden regiones opuestas. Pero
algunos pares sí se parecen mucho (`e5·s5` vs `e24·s9`, **+0.89**). Complementa
[[slot-unidad-de-morfologia]] con evidencia sobre **nuestras** láminas, no solo la figura
del paper.

> **Honestidad:** esto muestra que slots distintos se concentran en **regiones distintas**
> del tejido, que es medible. **Qué tejido es cada región sigue siendo lectura visual, no
> anotación** — sign-off de patólogo pendiente (igual que en OBJ-A).

### 5.3 Corrección de los mapas y la cota sobre la softmax (23-jul, tarde)

Los dos encargos de la reunión con Sebastián (`reunion_23jul_acuerdos.md` §1 y §4).

**(a) Los mapas ahora dibujan el top-4 PURO del ranking.** `pick_diverse_slots` elegía slots
espacialmente diversos dentro del top-20 y salteaba puestos (en tipo mostraba #1, #2, #4,
#13). Eso escondía justo el caso que Sebastián quiere ver: **dos slots del mismo experto**.
La función queda en el archivo, sin llamarse. Los slots dibujados hoy son:

| Tarea | Lámina | #1 | #2 | #3 | #4 |
|---|---|---|---|---|---|
| tipo histológico | `TCGA-AC-A8OS` | `e12·s2` 3.8 % | `e5·s5` 2.5 % | `e24·s9` 2.4 % | `e11·s3` 2.2 % |
| CDIS | `TCGA-D8-A1XB` | `e28·s4` 2.9 % | `e6·s9` 2.8 % | `e13·s6` 2.4 % | `e28·s5` 2.1 % |
| LVI | `TCGA-D8-A1X5` | `e6·s7` 4.9 % | `e15·s5` 2.9 % | `e19·s9` 2.8 % | `e15·s7` 2.7 % |

**(b) ¿Los slots de un mismo experto ven lo mismo?** Correlación espacial de rangos entre los
top-12 de cada lámina (`slot_corr_<tarea>.csv`), 198 pares en total, 6 de ellos del mismo
experto:

| Par mismo experto | Corr | | Par mismo experto | Corr |
|---|---|---|---|---|
| `e28·s4` vs `e28·s5` (CDIS) | **−0.56** | | `e8·s6` vs `e8·s9` (LVI) | +0.59 |
| `e15·s5` vs `e15·s7` (LVI) | +0.07 | | `e19·s9` vs `e19·s5` (CDIS) | +0.62 |
| `e11·s3` vs `e11·s4` (tipo) | +0.11 | | `e13·s6` vs `e13·s5` (CDIS) | +0.71 |

**Compartir experto no predice qué ve el slot.** Los 6 pares del mismo experto cubren de
**−0.56 a +0.71**, casi el mismo rango que los 192 pares de expertos distintos (−0.78 a
+0.89). El caso que pidió ver, `e28·s4` (#1) vs `e28·s5` (#4) en CDIS, va en la dirección
fuerte: **−0.56**, regiones opuestas de la misma lámina, con el mismo experto. Hay una leve
tendencia a parecerse más entre hermanos (media **+0.26** vs **+0.04** entre expertos
distintos), pero con **n=6 pares esto describe, no establece**, y el caso principal la
contradice. Consistente con [[slot-unidad-de-morfologia]]: la unidad es el **slot**.

**(c) La cota sobre la softmax: el reparto uniforme, 1/300 = 0.333 %.** Es el único corte
**sin parámetro libre** (misma virtud que `N_eff = exp(H)`): un slot por debajo recibe menos
de lo que le tocaría si el ruteo fuera ciego, así que no está concentrando nada. Los cortes a
ojo dan de 25 a 300 slots según dónde se pongan (tabla de arriba), que es exactamente por qué
la cota hay que justificarla. Medido **por lámina** (`slot_cota_por_lamina.csv`, generado por
`scripts/slot_cota_softmax.py`):

| Tarea | Slots sobre la cota | Masa que concentran | `N_eff` |
|---|---|---|---|
| tipo histológico | 80 / 91 / 96 | 71–76 % | 148 / 156 / 178 |
| CDIS | 63 / 90 | 69–82 % | 90 / 180 |
| LVI | 82 / 95 | 68–70 % | 162 / 196 |
| **7 láminas** | **63–96, media 85** (28 % de 300) | **73 %** | **158.7** |

El recuento es **notablemente estable entre tareas** (80–96 en seis de las siete); el 63 es la
lámina chica de CDIS, 2 793 parches, coherente con "menos parches, menos morfología que
rutear". En el otro extremo, el slot más chico de cada lámina recibe entre **15× y 161× menos**
que el uniforme: la cola es cero en la práctica.

> **Las tres medidas no se contradicen, miden cosas distintas.** 85 slots es *cuántos
> concentran*; `N_eff`≈159 es *cuántos hay contando a cada uno en proporción a su peso*, y sale
> más alto porque los ~215 de la cola, aunque individualmente pesen menos que el reparto ciego,
> **entre todos suman el 27 % restante**. La masa acumulada al 90 % (~164) triangula con
> `N_eff`. Al citarlas juntas hay que decir qué mide cada una.

**Cuántos slots requiere cada tarea, entonces.** De 80 a 96 hacen el trabajo de concentración
en las tres tareas, con el total efectivo alrededor de 160. Bajar de 300 a 270 (el primer par
del eje E×S, §6 de los acuerdos) queda **holgado por las dos medidas**. Bajar a 150 queda por
encima del recuento de slots que concentran pero **por debajo** del `N_eff`, así que ahí ya es
pregunta empírica, no aritmética. Esto **encuadra** el experimento de recorte; no lo anticipa.

## 6. Tabla por tarea (requisito de Sebastián)

`tabla_por_tarea.md`: slides usadas, magnificación física µm/px leída de cada WSI,
dataset/cohorte/n y etiqueta del patólogo. Los n y las distribuciones coinciden
exactamente con el pre-registro (2027 / 862 / 836).

## 7. Reproducir

```bash
PY=/home/sdonoso/miniconda3/envs/clam_latest/bin/python   # workaround B
# metricas agregadas de los 30 runs
$PY scripts/extract_metrics.py    # o el parser del sprint
# seleccion de slides (prefiere cohortes con MPP confiable)
$PY scripts/select_interp_slides.py --fold 0 --per-class 1
# comparacion de atencion CLAM vs Mammoth (CPU)
CUDA_VISIBLE_DEVICES="" $PY scripts/clam_vs_mammoth_attention.py
# ruteo por experto/slot (CPU, patch size real del h5)
bash scripts/run_b7_expert_interp.sh
# Q1
$PY scripts/answer_q1_expertos_slots.py
# tabla por tarea
$PY scripts/build_interp_task_table.py
```

Todo lo de interpretabilidad es **Etapa 0: CPU, post-hoc, sin GPU y sin sbatch** —
inferencia sobre checkpoints congelados, no toca modelo ni training.
