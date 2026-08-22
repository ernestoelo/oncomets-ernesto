# Pre-registro — B3: CLAM plano del gate de carcinoma invasivo, fold 0

> Escrito el **21-ago-2026**, **antes de lanzar nada** y antes de escribir el `.slurm`.
> Es la fase B3 de [`../encargos_sebastian/plan.md`](../encargos_sebastian/plan.md) (con su
> ADDENDUM del 21-ago), que cierra la mitad que falta del **encargo 1** de Sebastián.
> Toca entrenamiento ⇒ **regla 9**: este documento va antes del código y `reviewer` antes del
> commit.

## 1. Para qué existe esta corrida, dicho antes que nada

Sebastián pidió repetir la cadena mapa de calor → parches más atendidos → HoVer-NeXt con el
checkpoint de **carcinoma invasivo**, y compararla contra la que ya corrimos. La corrida ya
hecha ([`../encargos_sebastian/a2_atencion_gate_invasivo.md`](../encargos_sebastian/a2_atencion_gate_invasivo.md))
contestó **medio encargo**: el único checkpoint del gate que hay en disco es **Mammoth**, no
CLAM plano, aunque su `experiment.txt` declare `model_type: clam_mb`
([[checkpoint-familia-se-lee-del-statedict]]). El CLAM plano del gate **no existe**.

Entonces la comparación que quedó sobre la mesa mezcla dos cosas a la vez:

| | tarea de atención | brazo |
|---|---|---|
| medida ya hecha (CDIS) | `carcinoma_ductal_insitu_presente_ci_reform`, fold 4 | CLAM **y** Mammoth |
| medida ya hecha (gate) | `invasion_carcinoma_gate_pth_balance`, fold 0 | **solo Mammoth** |

El resultado de A2 es que el gate **recorta peor**: 11/26 marcas dentro del top-300 contra 22/26
de CDIS-Mammoth y 19/26 de CDIS-CLAM. Con un solo brazo en el gate **no se puede separar** si eso
es propiedad de la **tarea** (invasivo vs CDIS) o del **brazo** (Mammoth vs CLAM).

**B3 produce el brazo que falta.** Su producto primario es un **instrumento**, no una afirmación
de rendimiento: el checkpoint `s_0_checkpoint.pt` de CLAM plano sobre el mismo split, para que la
comparación del encargo quede **CLAM contra CLAM**, que es lo que se pidió.

## 2. Esto NO reabre el Hallazgo 12, y así se mantiene cerrado

El Hallazgo 12 de `CLAUDE.md` («Mammoth no mejora la métrica», 12 configuraciones, 0 mejoras)
está cerrado y este documento **no lo toca**. La corrida va a producir, de rebote, un Δ de
métrica entre CLAM y Mammoth en el fold 0 del gate, así que hay que decir de antemano cómo se
lee, o se decide después de ver el número:

- Es **un solo fold**, n=1. El Hallazgo 12 se cerró con comparaciones de 5 folds pareadas. Un Δ
  de un fold **no tiene poder** para confirmarlo ni para contradecirlo, en ninguna dirección.
- La tarea `invasion_carcinoma_gate_pth_balance` **no estaba** entre las 12 configuraciones que
  cerraron el Hallazgo 12, así que tampoco es terreno repetido: es terreno **nuevo y con n=1**,
  que es la peor combinación posible para sacar conclusiones de rendimiento.
- **Si CLAM sale por encima de Mammoth**, eso es consistente con el Hallazgo 12 y no agrega nada.
- **Si Mammoth sale por encima de CLAM**, se registra como dato y **no se reclama nada**: sería el
  segundo caso de la familia del DATO ABIERTO del job 4589, y reclamar rendimiento exigiría un
  pre-registro nuevo bajo **regla 9.b**, con su hallazgo habilitante, su branch y sus 5 folds con
  semillas nuevas. Queda escrito acá para que la decisión no se tome mirando el resultado.

## 3. Por qué queda pareado por construcción (patrón P1)

**El `main.py` es el de `clam_testing`, no el de `clam_environ`.** Los dos árboles divergieron
(`main.py` 885 líneas contra 750; `utils/core_utils.py` ~1000 líneas de diff;
`models/model_clam.py` ~312). El brazo Mammoth de `sgaete` salió de `clam_testing/main.py
--use_mammoth` (`clam_testing/run_mammoth_5fold_balanced.slurm`). Correr el CLAM plano desde
`clam_environ/main.py` cambiaría **el modelo y el bucle de entrenamiento a la vez**, que es
exactamente lo que P1 existe para evitar.

**La corrida pareada es ese MISMO archivo sin el flag.** Verificado en este repo, hoy:

- `--use_mammoth` tiene `default=False` (`clam_testing/main.py:646-651`).
- El flag **solo** viaja al diccionario de construcción del modelo (`utils/core_utils.py:315-333`
  y `:380-384`). **No hay ninguna rama de `use_mammoth` en el bucle de entrenamiento.**
- Sin el flag, `CLAM_MB` construye `nn.Linear(size[0], size[1])`, la primera capa de siempre
  (`clam_testing/models/model_clam.py:303`, rama `else` 301-306); con el flag la reemplaza por `MammothPatchEmbed`
  (`:284-300`).

O sea: **mismo bucle, mismos splits, misma semilla, mismas features; único delta la primera
capa lineal.** Es la definición del patrón P1.

**Salvedad que hay que escribir, porque «mismo archivo» no es demostrable** (la levantó el
`reviewer`, verificada acá): `clam_testing/main.py` tiene **mtime 15-jul-2026 18:07**, y el brazo
Mammoth corrió ese mismo día de **09:12 a 13:25**. La edición es **posterior a la corrida del
comparador**, así que el `main.py` de hoy **no es demostrablemente** el que lo produjo, y el repo
git de `clam_testing` no tiene commits locales (HEAD es el upstream de Mahmood Lab), o sea que la
versión de esa mañana **no es recuperable**. Los otros dos archivos sí están limpios:
`utils/core_utils.py` es del **28-may** y `models/model_clam.py` del **4-jun**, los dos muy
anteriores a las dos corridas.

Tres datos acotan el riesgo, y ninguno lo elimina:

1. `environ/csv_balance_ci/` y `environ/splits_5fold_balance_ci/` se crearon el **15-jul a las
   18:01**, seis minutos antes de la edición, y `main.py` documenta que las tasks `_ci` leen de
   esos dos directorios ⇒ la edición fue casi con seguridad **aditiva sobre `TASK_CONFIGS`**.
2. El conjunto de claves del `settings` que `main.py` serializa hoy (`:741-764`) es **idéntico**
   al que quedó escrito en el `experiment_*.txt` del comparador. Si el bloque de args hubiera
   cambiado, se vería ahí.
3. La entrada de `TASK_CONFIGS` de esta tarea apunta hoy al mismo `csv_path`
   (`environ/csv_balance/dataset_invasion_carcinoma_gate_label.csv`, `main.py:366-370`).

**Cómo se lee**: el pareado del **bucle de entrenamiento** está limpio (los dos archivos que lo
implementan son anteriores a las dos corridas). Lo que no se puede demostrar es que el
**entrypoint** sea idéntico, y la evidencia disponible dice que el cambio no lo tocó. Se declara
como riesgo 4 en §8 en vez de darse por resuelto.

**Reuso de splits** (P1): `--split_dir` apunta **exactamente** al mismo directorio que usó el
brazo Mammoth, `environ/splits_5fold_balanced/invasion_carcinoma_gate_pth_balance_100`. No se
regeneran splits.

## 4. El comparador, medido hoy y no citado de memoria

Fold 0 del brazo Mammoth de `sgaete`, recomputado desde su `split_0_results.pkl`:

| métrica | Mammoth fold 0 | baseline trivial |
|---|---|---|
| **balanced accuracy** | **0,9194** | 0,5000 |
| **AUC** | **0,9681** | 0,5000 |
| accuracy | 0,9283 | 0,7168 (mayoritaria) |
| recall `invasivo` | 0,9400 (n=200) | — |
| recall `no_invasivo` | 0,8987 (n=79) | — |

Matriz de confusión (filas = verdad):

|  | pred `invasivo` | pred `no_invasivo` |
|---|---|---|
| **`invasivo`** (n=200) | 188 | 12 |
| **`no_invasivo`** (n=79) | 8 | 71 |

El `test` del fold 0 tiene **279 láminas: 200 `invasivo` / 79 `no_invasivo`**. Verificado como
verdad de campo por el join `splits_0.csv ⨯ dataset_invasion_carcinoma_gate_label.csv` (regla 10);
el `splits_0_descriptor.csv` **está en sync** con ese join. La **129741 cae en `test`** del fold 0
y está etiquetada `invasivo`, que es la razón por la que este es el fold que sirve: la lámina no
fue vista en entrenamiento.

`label_dict` por `--auto-label-dict` (alfabético, `label_dict: {}` en `main.py:369`):
`invasivo`=0, `no_invasivo`=1.

## 5. Hipótesis, fijadas antes de correr

### 5.a — Sobre la competencia a nivel lámina (la corrida en sí)

**H_primaria.** CLAM plano alcanza en el fold 0 una competencia **comparable** a la de Mammoth:
AUC y balanced accuracy en el mismo rango (|ΔAUC| y |Δbal_acc| chicos frente a la varianza
inter-fold del brazo Mammoth, que va de 0,926 a 0,968 de AUC entre sus 5 folds, o sea un rango de
**0,042**). Dirección esperada: **Δ ≈ 0**, y es lo que predice el Hallazgo 12. Lo que la haría
creíble es que el Δ quede **dentro de ese rango inter-fold**, no que dé exactamente cero.

**La banda se eligió ancha a propósito.** El rango inter-fold mide la varianza de **sorteo**, que
en un Δ pareado se cancela (P1), así que sobreestima la incertidumbre del Δ de un fold. Se usa
igual porque juega a favor de la lectura nula, que es la conservadora acá: con una banda más
angosta sería más fácil declarar una diferencia que no está.

**Por qué importa que se cumpla, y no es un trámite:** si CLAM saliera mucho peor clasificador,
cualquier diferencia posterior en el top-K quedaría confundida con «este brazo simplemente
clasifica peor», y el encargo no se podría contestar. **La H_primaria es la condición que hace
interpretable el paso siguiente.**

**H_alternativa.** El Δ se sale de ese rango en cualquiera de las dos direcciones. Se **registra
con su signo** y se lee según §2: no se reclama rendimiento en ninguna dirección con n=1, y el
top-K posterior se reporta **con la advertencia** de que los dos brazos no son igual de
competentes a nivel lámina.

**H_regresión.** AUC del fold 0 **muy** por debajo del rango del 0,95 que reportó Sebastián para
el gate (criterio de verificación ya escrito en `plan.md`), o entrenamiento que colapsa a la
mayoritaria (recall de `no_invasivo` cercano a 0 con accuracy cerca de 0,717). Lectura: **la
config no quedó pareada** o el run está roto. En ese caso el resultado **no se usa** y se depura
la config antes de reintentar; no se reporta como hallazgo sobre CLAM.

**Sin gate numérico rígido de éxito/fracaso** (regla 9.a): lo que se pre-registra es la métrica,
el subset, la dirección esperada y cómo se interpreta cada desenlace.

### 5.b — Sobre la pregunta que el encargo realmente hace (el top-K, post-hoc en CPU)

Esta es la que contesta a Sebastián, y también va con dirección esperada.

**H_primaria.** La diferencia de A2 la explica **la tarea, no el brazo**: `gate·CLAM` va a caer
**cerca de `gate·Mammoth`** (11/26 en K=300) y **lejos** de los brazos de CDIS (19-22/26).
Fundamento: en CDIS, donde sí están los dos brazos, CLAM y Mammoth dan top-K **parecidos** (19/26
vs 22/26 en K=300), o sea que el brazo mueve poco; y el gate es una tarea cuya evidencia
(invasión) está repartida por el tumor entero, no concentrada donde están las mitosis.

**H_alternativa.** `gate·CLAM` cae cerca de los 19-22/26 de CDIS. Entonces el brazo **sí** explica
la diferencia y lo de A2 es un efecto de Mammoth sobre esta tarea. Sería una **sorpresa a
investigar, no a celebrar**: obligaría a re-leer §3 de A2 y no habilita por sí sola ninguna
afirmación de rendimiento.

**H_nula / ambiguo.** `gate·CLAM` cae en el medio (digamos 14-18/26 en K=300) sin acercarse a
ninguno de los dos grupos: se reporta como **no concluyente** con un solo fold y una sola lámina,
y se dice explícitamente que hace falta más de una lámina para separarlo. **B1 es lo que da esas
láminas.**

**Chequeo de sanidad, heredado y obligatorio:** en K = 2496 (la región anotada entera) los brazos
tienen que converger a **13/26**, que es el factor de detección solo. Si difieren, hay bug en el
enmascarado y el resultado no se lee.

## 6. Métricas, subset y unidad

- **Subset**: el `test` del fold 0, n=279 (200/79). No se toca val ni train.
- **Métricas, siempre juntas** (política de eval del B5, [[eval-reporte-auc-y-umbrales-obj6]]):
  **balanced accuracy Y AUC**, más **matriz de confusión** y **`n` por clase**. El AUC **nunca**
  aislado.
- **Unidad del top-K**: **marcas** (26 en la 129741), no parches (28) ni detecciones (177).
- **No se calcula precisión** contra el geojson y **nada se llama falso positivo**: las marcas del
  patólogo son **positivos parciales**.

## 7. Configuración exacta

Copiada del `.slurm` del brazo Mammoth, **quitando `--use_mammoth`** y acotando a un fold:

| arg | valor | de dónde |
|---|---|---|
| `--task` | `invasion_carcinoma_gate_pth_balance` | idéntico |
| `--split_dir` | `.../environ/splits_5fold_balanced/invasion_carcinoma_gate_pth_balance_100` | **idéntico (P1)** |
| `--data_root_dir` | `.../clam_environ/environ` | idéntico |
| `--model_type` | `clam_mb` | idéntico |
| `--embed_dim` | 512 | idéntico (CONCH) |
| `--lr` | 2e-4 | idéntico |
| `--reg` | 1e-5 | idéntico |
| `--drop_out` | 0.25 | idéntico |
| `--max_epochs` | 30 | idéntico |
| `--seed` | 1 | **idéntico** |
| `--bag_loss` | ce | idéntico |
| `--inst_loss` | svm | idéntico |
| `--early_stopping`, `--weighted_sample`, `--auto-label-dict` | activos | idénticos |
| `B`, `bag_weight` | 8, 0.7 (defaults, no se pasan) | idénticos |
| `--use_mammoth` | **ausente** | **el único delta** |
| `--k --k_start --k_end` | `5 0 1` | acota a `folds = [0]` |
| `--results_dir` | `<repo>/results/b8_gate_invasivo` | **containment** |

Tres cosas de plomería, ya verificadas en el ADDENDUM de `plan.md` §B3:

- **Containment**: `main.py` y `core_utils.py` escriben **solo** bajo `args.results_dir`, así que
  un `--results_dir` absoluto dentro de nuestro repo alcanza. Usa `os.mkdir`, no `makedirs` ⇒ hay
  que **crear el padre antes**.
- **`--chdir` a `clam_testing`** porque el `csv_path` de `TASK_CONFIGS` se resuelve relativo al
  CWD. Su `environ/` es un **symlink a `clam_environ/environ`**, o sea el CSV canónico. **No se
  escribe nada ahí.**
- **El resumen sale `summary_partial_0_1.csv`**, no `summary.csv`. Y `seed_torch(args.seed)` corre
  **por fold**, así que el fold 0 aislado reproduce el fold 0 de una corrida de 5.

**Preflight obligatorio antes del `python main.py`** (workaround G): validar que toda lámina de
train tenga al menos `--B`=8 parches, para que un bug de datos mate el job en segundos y no a las
horas. **Ya corrido en CPU el 21-ago**: 2255 láminas de train, todas con ≥8 parches, 0 sin `.pt`.

Y tres cosas que van a aparecer en el directorio o en el log y **no son anomalías**:

- **Van a quedar tres checkpoints** (`s_0_checkpoint.pt`, `_best_auc`, `_best_error`). El
  instrumento que usa A2 es el **plano**. `core_utils.py:464-467` carga el `_best_auc` si existe
  para computar el `summary`, y eso **no es un problema**: `EarlyStopping` usa `score = val_auc`
  (`:204-208`) y `validate_clam` le pasa `val_auc=auc` (`:905-917`), así que el plano y el
  `_best_auc` se guardan bajo la **misma condición** y llevan los mismos pesos.
- **`--early_stopping` SÍ puede disparar en este árbol**, a diferencia de lo que dice el
  Hallazgo 10 para `clam_environ`: acá es `EarlyStopping(patience=20, stop_epoch=15)`
  (`core_utils.py:426`), no `stop_epoch=50`, y con `max_epochs=30` es alcanzable. Los dos brazos
  pueden **parar en épocas distintas**: es correcto y esperado, no una asimetría.
- **El `exp_code` no lleva timestamp**, así que el `.slurm` **aborta si el directorio de
  resultados ya existe**. Motivo: `main.py:854-859` reusa el directorio sin chistar y
  `save_probability_records` (`core_utils.py:157-168`) **concatena** sobre el CSV viejo en vez de
  sobreescribirlo ⇒ un run abortado y relanzado dejaría los `val_slide_probabilities_fold_0.csv`
  con las filas de las dos corridas mezcladas y nada lo señalaría.

## 8. Riesgos declarados antes de correr

1. **Árbol compartido y vivo (workaround H, al revés).** `clam_testing/` es de `sdonoso` y lo usan
   otros; si alguien edita `main.py`, `core_utils.py` o `model_clam.py` mientras nuestro job
   corre, le cambia el piso. **Mitigación**: registrar `md5sum` + `mtime` de los tres archivos **al
   lanzar y al terminar**, y guardarlos junto al resultado. Si cambiaron, el run queda marcado como
   **sospechoso** en vez de pasar por bueno.
2. **La GPU es un solo token y hay cola de terceros.** El job declara `--time` real para no matar
   el backfill ajeno (workaround L). `squeue` antes del `sbatch`.
3. **Deriva del entrypoint entre el comparador y hoy (§3).** No se puede demostrar que el
   `main.py` sea el mismo; la evidencia dice que el cambio del 15-jul 18:07 fue aditivo sobre
   `TASK_CONFIGS`. **Mitigación**: el `.slurm` deja el `md5sum` de hoy de los tres archivos en
   `procedencia_<job>.txt`, que es **la línea base hacia adelante**; hacia atrás lo único que hay
   es el argumento de §3. Si el resultado saliera raro, éste es el primer sospechoso.
4. **El determinismo NO alcanza para validar nada acá.** El pipeline reproduce byte a byte con la
   misma semilla ([[pipeline-determinista-bit-a-bit]]), así que esta corrida **no es** una réplica
   independiente de nada: es un brazo nuevo. Cualquier réplica exigiría **semillas nuevas**.

## 9. Qué NO se afirma

- **No se afirma** que CLAM sea mejor ni peor que Mammoth en el gate: un fold no alcanza (§2).
- **No se afirma** que esto cambie el 13 de 26. La detección es el factor que manda desde K=189, y
  **no depende de qué checkpoint recorta**: cambiar la tarea o el brazo de atención mueve el
  **área**, no las **marcas** (P2.a.ter). B3 explica un contraste, no sube el número.
- **No se afirma** nada sobre las otras 11 láminas: esto es una lámina, 26 marcas, un fold.
- **No se afirma** que el `experiment.txt` del brazo Mammoth mienta por descuido de nadie: no
  registra `use_mammoth`, y eso es todo lo que se sabe.
