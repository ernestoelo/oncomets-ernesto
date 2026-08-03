# Pre-registro — grid de expertos (E) y slots (S) de Mammoth sobre CDIS `_ci_reform`

> Escrito el 2-ago-2026 (noche), **antes de lanzar nada**. Es el objetivo 3 del B8
> ([`../objetivos_sprint8.md`](../objetivos_sprint8.md) §3 + ADDENDUM 2-ago), que formaliza el
> encargo de Sebastián del 23-jul y de la reunión del 24-jul.
>
> El cambio es **configuración pura**: `scripts/train_dsmil.py` ya expone
> `--mammoth_num_experts` (L223) y `--mammoth_num_slots` (L224). No se toca
> `models_mammoth/clam_mammoth.py` ni el harness. Aun así va pre-registrado y pasa por
> `reviewer`, porque cambia la configuración del modelo (regla 9) y porque el encuadre es el
> grado de libertad que puede fabricar la lectura del resultado.

## 1. El encuadre, elegido y escrito explícito

Este grid es una pregunta de **capacidad**: cuántos expertos y cuántos slots por experto hace
falta que tenga Mammoth para **nuestro** contexto (mama, features CONCH de 512, nuestras
tareas), dado que E=30 / S=10 son los valores que los autores afinaron para tipo histológico y
otros cánceres. Es el eje tal como lo planteó Sebastián el 23-jul.

**No es una reapertura del eje de rendimiento.** El Hallazgo 12 de `CLAUDE.md` («Mammoth no
mejora la métrica», 12 configuraciones, 0 mejoras) queda cerrado y este documento no lo toca.
La forma concreta en que se mantiene cerrado es que **el contraste primario del grid es
Mammoth contra Mammoth**: cada configuración se compara contra el control 30×10, no contra
CLAM. CLAM entra solo como contexto de escala en el reporte.

**La tensión que hay que nombrar, porque existe.** El grid ancho cae sobre
`carcinoma_ductal_insitu_presente_ci_reform`, que es exactamente la tarea donde vive el dato
abierto del job 4589 (Mammoth 30×10 sobre CLAM: Δbal_acc +0.074 ± 0.033, 5/5 folds; ΔAUC
+0.060 ± 0.042, 5/5). Es fácil que se lea como búsqueda de mejora. La tarea se eligió por dos
razones operativas, ambas verificables y ninguna relacionada con ese Δ:

1. **Costo**: es la más barata de las tres del 4589, **36.4 min/run** contra 83.6 de
   `tipo_histologico` (mediana de los intervalos entre `test_metrics.json` consecutivos del
   brazo Mammoth; ver §7). Es la única que deja entrar un grid ancho en una ventana de fin
   de semana.
2. **Baselines ya corridos sobre los mismos splits y las mismas features**, lo que libera 10
   runs para configuraciones nuevas (§5).

Si el grid arrojara que una configuración reducida supera al control, **eso no reabre el
Hallazgo 12**: sería un resultado de capacidad (alcanza con menos), y reclamar rendimiento
exigiría un pre-registro nuevo bajo regla 9.b, con su hallazgo habilitante y su branch. Queda
escrito acá para que no se decida después de ver el número.

## 2. De dónde sale la dirección esperada

No es corazonada, es medición propia del encargo 1 de este mismo sprint
(`../q1_slots_escalado/resultados.md`, 1858 láminas-fold, 1176 láminas únicas, las 3 tareas y
las 3 cohortes):

| Qué se midió | Resultado | Lectura |
|---|---|---|
| Expertos efectivos, exp(entropía) sobre `combine_weights` | **29.98 de 30** | los 30 se usan, reparto prácticamente uniforme |
| Cuantiles del reparto por experto | `e50=15`, `e90=27` exactos, sin una sola excepción en 1858 | es el uniforme teórico, no hay expertos muertos |
| Slots efectivos | **159.5 ± 26.3 de 300** | poco más de la mitad de los slots concentra el peso |

De ahí sale la frase que este grid pone a prueba: **el margen de recorte está en S, no en E**.

## 3. Hipótesis, fijadas antes de correr

**H_primaria (la que se pre-registra como esperada).** A **igual capacidad total E·S**,
recortar S se tolera mejor que recortar E. Operacionalmente: para cada uno de los tres totales
apareados (270, 210, 150), el brazo que recorta S queda **por encima** del que recorta E; los
empates cuentan para H_nula, no para ésta. Lo que la haría creíble es la **consistencia de
signo**: el mismo orden en los tres pares y en la mayoría de los 5 folds de cada par, no un
par suelto grande.

**H_nula.** No hay diferencia sistemática entre las dos direcciones de recorte: el Δ pareado
entre A y B queda dentro del ruido inter-fold (std ≳ |media|) y el signo se mezcla entre pares.
Lectura: la ocupación medida describe cómo se reparte el peso pero no predice qué capacidad
hace falta.

**H_alternativa (el resultado que contradiría la medición).** Recortar E se tolera **mejor**
que recortar S, con signo consistente. Lectura: el número efectivo de slots sobreestima lo que
el modelo necesita en S, y la ocupación uniforme de los expertos no implica que los 30 hagan
falta. Sería el resultado más interesante de los tres y hay que reportarlo como tal, no
enterrarlo.

**Predicción secundaria (dosis-respuesta sobre la escalera de S).** Bajando por la rama que
recorta S, el rendimiento debería sostenerse hasta ~150 (que es donde cae el número efectivo
medido, 159.5) y recién degradarse en el piso de 90, claramente por debajo. Si 30×3 (=90) **no**
degrada, entonces la capacidad sobra todavía más de lo que dice la ocupación, y ese es un
resultado publicable del encargo. Si degrada ya en 270, la ocupación no sirve para dimensionar.

Las tres lecturas están escritas antes de correr. Ninguna se elige mirando el número.

## 4. El grid

Ocho brazos, 5 folds cada uno, 40 runs. La estructura es una escalera de capacidad total con
los dos recortes apareados en cada peldaño:

| Brazo | E | S | E·S | Qué recorta | Parámetros del modelo |
|---|---:|---:|---:|---|---:|
| **C** control | 30 | 10 | 300 | (referencia, = 4589) | 630,424 |
| **A1** | **27** | 10 | 270 | E | 621,480 |
| **B1** | 30 | **9** | 270 | S | 622,744 |
| **A2** | **21** | 10 | 210 | E | 605,400 |
| **B2** | 30 | **7** | 210 | S | 607,384 |
| **A3** | **15** | 10 | 150 | E | 586,792 |
| **B3** | 30 | **5** | 150 | S | 592,024 |
| **B4** piso | 30 | **3** | 90 | S (solo) | 576,664 |

El primer peldaño (270) es el par 27×10 contra 30×9 que Sebastián pidió textualmente el
23-jul. Los otros dos lo extienden a −30 % y −50 % de capacidad. El piso B4 va solo en la rama
S porque es la dirección que H_primaria declara tolerable: si ahí degrada, tenemos el piso de
capacidad acotado; si no, la conclusión de sobredimensionamiento se vuelve mucho más fuerte.

**Los pares a igual E·S son casi iso-parámetro, y eso hay que decirlo porque no era obvio.**
`auto_rank` deriva el `lora_rank` de `(input_dim, slot_dim, output_dim, num_experts)`, o sea
que **depende de E y no de S** (`MAMMOTH/src/mammoth/mammoth.py:297-322`): recortar E sube el
rank y compensa el presupuesto de parámetros, mientras que recortar S solo achica
`slot_embeds`. Medido con `scripts/grid_es_config_check.py`, la diferencia dentro de cada par
es de **+0.20 %, +0.33 % y +0.89 %** (270, 210, 150). Es chica, pero no es cero, y va reportada
junto al resultado: el contraste A contra B aísla **dónde** está la capacidad, no cuántos
parámetros hay.

Todo lo demás queda **fijo e idéntico al 4589**: `--mammoth_num_heads 16`, `--mammoth_slot_dim
256`, `slot_dropout` 0.0, `keep_slots` **False** (preserva los N parches, semántica de atención
y de instance-loss idéntica al baseline), régimen de training bendecido (max_epochs 200,
early_stopping patience 20 stop_epoch 50, B 8, bag_weight 0.7, lr 2e-4, reg 1e-5, drop_out
0.25, embed_dim 512, seed 1) y el mismo harness `scripts/train_dsmil.py`. **El único delta
entre brazos son E y S.**

Las 8 configuraciones ya se verificaron en CPU antes de escribir el `.slurm`: construyen,
hacen forward sobre un bag de 200 parches y devuelven `A_raw` con forma `(n_classes, N)`
(`scripts/grid_es_config_check.py`, corre en segundos). Es el preflight a nivel de
configuración: una config rota se paga en horas de GPU si aparece a mitad del grid.

## 5. Comparación pareada y reuso de los baselines del 4589

**Splits reusados, sin regenerar**:
`data/splits_kfold/carcinoma_ductal_insitu_presente_ci_reform_100`, los mismos 5 folds del job
4589 ([[patron-paired-comparison-reuso-splits]]). El Δ se construye **por fold**, así la
varianza inter-fold se cancela en la diferencia.

**Dataset**: 862 láminas, 730 `si` / 132 `no` (85 % positivo), invasivas ∩ explícitos.
Por fold: ~691 de train, ~85 de val, 85-88 de test, con **~13 negativos por test**. Ese n
chico en la clase minoritaria es la limitación principal de todo lo que salga de acá y está
escrito antes, no después.

**Qué se reusa y qué se re-corre.** Los 10 runs del 4589 (5 CLAM + 5 Mammoth 30×10) viven en
`results/b7_mammoth_interp/carcinoma_ductal_insitu_presente_ci_reform/`, sobre los mismos
splits, y se verificó el 2-ago que **ninguna feature cambió desde entonces** (cero `.pt` con
mtime posterior al 17-jul; el directorio quedó en 28-jun, el parche de magnificación de
Sebastián, [[features-tcga-drift-reextraccion]]). Con features y splits idénticos el reuso
pareado es válido por construcción.

Aun así el grid **re-corre el Mammoth 30×10 como control**, y ese es el uso de 5 de los 40
runs. Su función es verificar que la tanda nueva reproduce la vieja: si el control no
reproduce al 4589, el reuso del CLAM se cae y conviene enterarse **antes** de interpretar el
grid, no después. Criterio de lectura, fijado ahora: se espera que el control caiga sobre los
números del 4589 dentro de lo que se mueve una corrida (los runs son deterministas salvo
no-determinismo de GPU); si algún fold se aparta más que los efectos que el grid pretende
leer, el reporte lo dice y el CLAM reusado pasa a ser referencia informativa, no comparador.

## 6. Métrica y cómo se lee

**Balanced accuracy Y AUC, juntos**, más matriz de confusión y n por clase, por fold y
agregados (política de eval B5, [[eval-reporte-auc-y-umbrales-obj6]]). Nunca AUC aislado. Con
85 % de positivos, la accuracy cruda no dice nada y no se reporta como resultado.

**Estadístico primario**: Δ pareado por fold contra el control 30×10, reportado como media ±
desviación sobre los 5 folds **más los 5 signos**. El contraste que decide H_primaria es
`(B_i − A_i)` dentro de cada peldaño de igual E·S.

**Cuál manda si las dos métricas se contradicen, decidido ahora.** Para la dirección de
H_primaria la métrica decisiva es el **AUC**, y la balanced accuracy se reporta al lado como
lectura del punto de operación. La razón es de granularidad, no de preferencia: con 13
negativos por test, la balanced accuracy se mueve a saltos de 1/(2·13) = 0.038 por cada
negativo que cambia de lado, así que la consistencia de signo de un par puede depender de
**una sola lámina**, mientras el AUC no tiene ese problema. Si AUC y balanced accuracy apuntan
en direcciones distintas, el par se declara **ambiguo** y se reporta la discrepancia como tal:
significaría que la diferencia entre recortar E y recortar S está en el umbral y no en el
ordenamiento, que es terreno de calibración ([[calibracion-operating-point-palanca-b5]]) y no
de capacidad. Esto no viola la política B5, que prohíbe decidir con AUC **aislado**: las dos
métricas se reportan siempre juntas, con matriz de confusión y n por clase.

**CLAM entra como fila de referencia, no como comparador.** En el `resultados.md` los 5 runs
CLAM del 4589 aparecen como una fila de escala (bal_acc y AUC por fold), **sin Δ por brazo**.
Calcular un Δ contra CLAM para cada una de las 8 configuraciones serían 8 disparos al eje
cerrado del Hallazgo 12, justo sobre la tarea del dato abierto. Si alguna vez se calcula, va
rotulado como descriptivo y nunca como inferencial.

**Sin gate numérico rígido** (regla 9.a). Lo que se pre-registra es la métrica, el subset, la
dirección esperada y cómo se interpreta: consistencia de signo entre los tres pares y entre
folds, magnitud comparada con la desviación, y si el intervalo cruza cero se llama ambiguo y
se dice ambiguo. Un Δ grande en un solo par con signo mezclado en el resto **no** cuenta como
confirmación.

## 7. Presupuesto y riesgo operativo

40 runs × 36.4 min/run ≈ **24.3 h**. El número sale de los intervalos entre
`test_metrics.json` consecutivos de los 5 runs **Mammoth** del 4589 en esta tarea (36.4 /
36.2 / 36.4 / 36.5, mediana 36.4). Se usa el costo del brazo Mammoth y no una mediana mezclada
porque los 40 runs del grid son todos Mammoth: los CLAM de la misma tarea costaron 19.3
min/run y promediarlos subestimaría el presupuesto en casi un tercio. El `--time` del `.slurm`
queda en 48:00:00, que da margen sobrado. Lanzado un domingo por la noche, **termina el lunes por la noche y ocupa el lunes
laboral**: es una única GPU compartida, así que si aparecen jobs ajenos aplica la cortesía de
`CLAUDE.md` y se evalúa `scancel` de los brazos que falten.

El orden de ejecución está elegido para que un corte temprano deje algo interpretable:
**control → los tres pares de arriba hacia abajo (270, 210, 150) → el piso 90**. Si hay que
cortar, lo que se pierde es el peldaño más agresivo, no el control ni el par que pidió
Sebastián.

**Working tree compartido** (workaround H, [[working-tree-compartido-job-en-curso]]): el job
relee su código en cada una de las 40 invocaciones. Todo lo que lee queda commiteado en `main`
**antes** del `sbatch`, y con el job vivo no se cambia de rama ni se editan archivos
versionados que el job use.

## 8. Lo que NO se va a afirmar

- **No** se va a afirmar que Mammoth mejora el rendimiento, en ninguna configuración. Ese eje
  está cerrado (Hallazgo 12) y este grid no lo mide.
- **No** se va a extender la conclusión a las otras dos tareas ni a otras cohortes. Es **una**
  tarea, la más barata, con 85 % de positivos y ~13 negativos por test. La lección del encargo
  1 fue justamente esa: un número medido sobre 7 láminas no era el número de la tarea. Acá
  vale igual, un peldaño más arriba.
- **No** se va a leer un brazo suelto como ganador sin consistencia de signo entre pares y
  entre folds.
- **No** se va a reciclar el Δ +0.074 del 4589 como si el grid lo hubiera replicado: el control
  re-corre el mismo 30×10 con el mismo seed, así que **no** es una réplica independiente de ese
  dato. La réplica sigue pendiente y necesita semillas o folds nuevos.
- Si sale H_alternativa, se reporta como contradicción de nuestra propia medición, no se
  esconde ni se re-interpreta a favor.

## 9. Salidas

- Checkpoints y métricas:
  `results/b8_grid_es/carcinoma_ductal_insitu_presente_ci_reform/mammoth_e<E>s<S>_f<0..4>_<ts>_s1/`
  con `test_metrics.json`, `test_predictions.csv`, `summary.csv`, `split_<f>_results.pkl`.
- Lanzador: `sprints/B8_sprint8/grid_expertos_slots/run_b8_grid_es.slurm`.
- Preflight de configuración: `scripts/grid_es_config_check.py`.
- Resultados y lectura: `sprints/B8_sprint8/grid_expertos_slots/resultados.md` (después del
  job), con la tabla completa de balanced_acc y AUC por brazo y fold.

**Provenance que el `resultados.md` tiene que citar del `.out`**, porque el `.slurm` las
imprime justamente para eso: la línea `brazos=` (los brazos que corrieron de verdad, ya que
`ARMS` es sobre-escribible por entorno) y la línea `commit=` con el `HEAD` desde el que corrió
el job. Con un árbol compartido y 24 h de corrida, ese par de líneas es la prueba de que lo
ejecutado es lo pre-registrado.
