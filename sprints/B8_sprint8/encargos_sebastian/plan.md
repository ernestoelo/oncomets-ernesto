# Plan — los cuatro encargos de Sebastián después de la reunión

## Objetivo rector

**El resultado que importa es que HoVer-NeXt encierre las mismas mitosis que marcó el patólogo.**
Hoy son **13 de 26** en la 129741. Todo lo que sigue se ordena por cuánto aporta a subir ese
número o a explicar por qué no sube; lo demás es contexto.

Consecuencias sobre las prioridades de abajo, y hay que sostenerlas:

- **El recall contra las marcas es la métrica primaria.** La carga de revisión (área, objetos a
  mirar) es el desempate cuando dos brazos empatan en recall, **no** el eje principal.
- **El cuello está medido y no es la máscara.** Desde K=189 (7,6 % de la región) el factor que
  manda es la **detección**: por generoso que sea el recorte, el techo se queda en 13 de 26. O sea
  que **agrandar la máscara ya no compra marcas** — lo que hay que mover es el detector.
- **Por eso el pendiente 1 está en el camino crítico**, no es un extra: saber si los 13 núcleos
  fallados **fueron segmentados y mal clasificados** o **no fueron segmentados** decide cuál es el
  arreglo. Son dos fallas con costo muy distinto y se contesta **sin GPU**, con los `raw` que ya
  están en disco.
- **Las 12 láminas (B1) importan porque cambian el denominador de 26 a 94**, no por cubrir más
  superficie. Es lo que convierte un número de una lámina en un número medible.

## Contexto

La reunión del 19-ago se presentó con dos láminas y dejó el número que sostiene la
conversación: **HoVer-NeXt recupera 13 de las 26 marcas de `Mitosis` del patólogo en la
129741**, con la escalera 68,0 mm² → 13/26 · 35,4 mm² → 13/26 · 4,3 mm² → 11/26 (el recorte
compra área, no marcas). Sebastián pidió cuatro cosas encima de eso:

1. Repetir la cadena mapa de calor → parches más atendidos → HoVer-NeXt con el checkpoint de
   **carcinoma invasivo**, para comparar contra el resultado ya obtenido.
2. Mirar las imágenes de las **164 detecciones sin marca** (177 − 13) y ver si se parecen
   entre sí.
3. Revisar si la **necrosis** que señala HoVer-NeXt coincide con las marcas del patólogo.
4. Correr HoVer-NeXt sobre **las 12 láminas anotadas**.

Lo que la exploración cambió del enunciado, y hay que decirlo antes de ejecutar:

- **El checkpoint que Sebastián no recordaba** es `carcinoma_ductal_insitu_presente_ci_reform`,
  **fold 4** del job 4589 (par CLAM/Mammoth propio). No era el de invasivo.
- Para carcinoma invasivo la tarea es **`invasion_carcinoma_gate_pth_balance`** (2013 invasivo /
  802 no). La 129741 está etiquetada `invasivo` y cae en **test del fold 0**. Hay checkpoint
  entrenado en `clam_testing/`, pero al abrirlo tiene claves `attention_net.0.mammoth.*`:
  **es Mammoth, no CLAM plano**, aunque su `experiment.txt` declare `model_type: clam_mb`.
  CLAM plano del gate no existe en disco.
- **El checkpoint de HoVer-NeXt que corrimos no tiene clase de necrosis.** Lizard-Mitosis
  clasifica neutrophil, epithelial-cell, lymphocyte, plasma-cell, eosinophil,
  connective-tissue-cell y mitosis (`hover_next_reference/src/constants.py:33-39`). La clase
  `dead` vive **solo en PanNuke** (`constants.py:44-48`), que nunca se lanzó. El encargo 3
  necesita esa corrida. **No reabre la decisión de no lanzar el ensemble**: esa decisión decía
  que el ensemble no puede mover el 13/26 de mitosis, y sigue siendo cierta. Es otra pregunta.
- **Las 12 láminas tienen mitosis**, pero repartidas 26/20/17/8/6/6/3/3/2/1/1/1 sobre 94 marcas.
  Seis láminas tienen ≤3 → un recall por lámina desde n=1 no distingue nada; el denominador
  honesto es el agregado.
- **Necrosis hay en 5 láminas, 18 polígonos**, con vocabulario inconsistente: `necrosis` (6, en
  la 129741), `Necrosis` (4 en 128194, 2 en B25-158899), `Comedonecrosis` (3 en 124729, 3 en
  124806).
- **`sgaete` ya midió atención contra anotaciones en 8 tareas × las 12 láminas**, necrosis
  incluida (`anotaciones/atencion/resumen_atencion.csv`, 108 filas). El gate de invasivo **no**
  está en su lista, así que el encargo 1 es trabajo nuevo. Decisión de Ernesto: **seguimos y le
  avisamos después.**

Resultado esperado: los cuatro encargos contestados, con la mitad barata resuelta en CPU el
mismo día y tres corridas de GPU autorizadas para lo que no se puede contestar sin ellas.

---

## Fase A — CPU, sin GPU, sin depender de la cola

### A0. Camino crítico — por qué se escapan las 13 (segmentadas o no segmentadas)

**No es uno de los cuatro encargos, pero es lo que más mueve el objetivo rector**, y se contesta
sin GPU con datos que ya están en disco. El cruce solo miró la clase `mitosis`: nunca preguntó qué
pasó con los 13 núcleos que se escaparon.

Dos fallas posibles, con arreglos de costo muy distinto:

| Si el núcleo… | Significa | Qué lo arreglaría |
|---|---|---|
| **fue segmentado y clasificado como otra cosa** (epitelial, conectivo) | la instancia está, falla la **cabeza de clase** | recalibrar o re-entrenar solo la clase, o una segunda etapa barata encima |
| **no fue segmentado** | falla la **segmentación** | mucho más caro: no hay objeto que reclasificar |

Insumo: `129741_raw_256_inst.zip` (9,7 GB, el BCB-map de instancias) y `129741_raw_256_cls.zip`,
que sobrevivieron gracias a `--keep_raw` (`corrida_5008.md` §2). Se busca, en la posición de cada
una de las 13 marcas falladas, si hay una **instancia** y qué **clase** le tocó.

Salida esperada: «de las 13, N estaban segmentadas y clasificadas como X, y M no tenían instancia».
Ese reparto decide en qué se invierte el resto del esfuerzo, así que va **antes** de cualquier
propuesta de cómo subir el 13 de 26.

### A1. Encargo 2 — la galería de las 177

**Script nuevo**: `scripts/galeria_mitosis_129741.py`.

Tres bloques de láminas de contacto, recortes a resolución nativa (level 0, ventana de 128 px
≈ 59,5 µm de lado, que da contexto alrededor de una figura mitótica de 10-20 µm):

| Bloque | n | Qué muestra |
|---|---|---|
| Detecciones sin marca | 164 | El inventario que pidió Sebastián |
| Detecciones acertadas | 13 | Con la marca del patólogo dibujada encima |
| Marcas que se escaparon | 13 | Recorte centrado en la marca, sin detección cerca |

Dentro de cada bloque los recortes se **ordenan por parecido**: vector por recorte (píxeles
reducidos + histograma de color), PCA, y clustering jerárquico con *optimal leaf ordering*
(`scipy.cluster.hierarchy`). Es parecido **de píxeles, no semántico**, y la caption tiene que
decirlo — no es una afirmación de que sean mitosis.

**Reusos** (nada de esto se reescribe):
- `marcas_mitosis()` y `emparejar()` de [cruce_hovernext_marcas.py](../../../scripts/cruce_hovernext_marcas.py#L53-L74)
- `read_hires_patch()` de [mammoth_interpretability.py:335](../../../scripts/mammoth_interpretability.py#L335)
- `cargar_anotaciones()` de [alinear_anotaciones_qupath.py:46](../../../scripts/alinear_anotaciones_qupath.py#L46)
- El molde de recorte con marca encima de `detalles()` en
  [prep_assets_hovernext.py:206](../presentacion_b8/prep_assets_hovernext.py#L206)

**Único cambio a código existente**: `emparejar()` hoy devuelve solo el booleano sobre marcas, y
la galería necesita saber **qué detección** acreditó cada marca. Se agrega
`emparejar_pares()` que devuelve `(ok, pares)` y `emparejar()` queda como envoltorio de una
línea → las salidas del cruce siguen siendo byte-idénticas.

**Lo que hay que escribir en el documento, o el panel se lee mal**: las 164 **no son falsos
positivos**. Las marcas son positivos parciales y el patólogo marca solo donde la evidencia es
clara, así que una detección fuera de las 26 puede ser una mitosis real sin marcar. El panel de
las 13 falladas es el que más informa, porque ése sí muestra en qué se equivoca el detector.

Salida: `results/b8_hovernext_129741/galeria_mitosis/` + `sprints/B8_sprint8/hovernext_129741/galeria_mitosis.md`.

### A2. Encargo 1, brazo disponible hoy — atención del gate de invasivo

La 129741 ya corrió entera por HoVer-NeXt, así que **no hace falta volver a correr nada en GPU**:
el filtro se aplica post-hoc sobre la salida (patrón P2.a.ter). Solo falta la atención nueva.

1. `sprints/B8_sprint8/hovernext_129741/interp_slides_gate.json` — misma forma que
   [interp_slides_129741.json](../hovernext_129741/interp_slides_129741.json),
   apuntando a
   `clam_testing/results_mammoth_5fold_balanced_tcga_sc/invasion_carcinoma_gate_pth_balance_mammoth_5fold_s1/s_0_checkpoint.pt`
   (lectura sobre workspace ajeno, sin escribir nada ahí), 2 clases, fold 0.
2. `clam_vs_mammoth_attention.py --selection ... --dump-attention`. **Cambio aditivo**: hoy
   construye los dos brazos siempre; se permite `ckpt_clam: null` para saltar el que falta
   (mientras no exista el CLAM plano de B3).
3. Rama de atención: leer la de **`invasivo`** (la clase verdadera), y además registrar cuál
   predijo el modelo. `sgaete` leyó solo la rama predicha en su tabla de necrosis y por eso
   mide sobre la rama equivocada.
4. `techo_atencion_topk.py --npz <nuevo> --out-dir <nuevo>` y
   `cruce_hovernext_marcas.py --npz <nuevo> --out-dir <nuevo>`. **Ya aceptan esos flags**: es
   re-invocación, no código nuevo. La geometría (offset dx=3829, `Y_CORTE_REGION=49920`, mpp
   0,465) es la misma lámina y no se toca.

Entregable: la escalera de invasivo al lado de la de CDIS, en la misma unidad (marcas), y el
aviso de que los folds difieren (CDIS fold 4, gate fold 0) porque en cada tarea ése es el fold
donde la 129741 **no** fue vista en entrenamiento.

### A2.bis. La escalera de brazos — CLAM solo como línea base, antes de HoVer-NeXt

**Pedido de Ernesto (21-ago).** Hasta ahora HoVer-NeXt se leyó contra sí mismo. Falta la pregunta
anterior: **¿el detector agrega algo sobre la atención sola?** Para contestarla el brazo de
atención pura deja de ser «el techo» y pasa a ser **la línea base contra la que se lee todo**.

Una precisión de forma: **Mammoth no se suma a CLAM, lo reemplaza** — es CLAM con la 1ª capa
lineal cambiada por el MoE, así que son brazos **alternativos**. Lo que sí es un brazo nuevo es
combinar las dos máscaras.

| Brazo | Qué propone | De dónde sale |
|---|---|---|
| azar | top-K sorteado dentro de la región | ya está, `techo_atencion_topk.py` |
| **CLAM solo** | top-K por atención de CLAM | ya está, columna `en_mascara` |
| **Mammoth solo** | top-K por atención de Mammoth | ya está |
| CLAM ∩ Mammoth / CLAM ∪ Mammoth | dónde coinciden o dónde suman | **nuevo, trivial** sobre el mismo `npz` |
| HoVer-NeXt solo | las 177 detecciones, sin filtro | ya está, 13/26 |
| **CLAM + HoVer-NeXt** | intersección | ya está, columna `ambas` |
| **Mammoth + HoVer-NeXt** | idem | ya está |

**Casi todo está computado**: sale de
[techo_conjunto.csv](../../../results/b8_hovernext_129741/cruce_marcas/techo_conjunto.csv) más
`techo_atencion_topk.csv`. Lo nuevo es la **figura y el eje**, no el cómputo.

**El recall contra las marcas manda** (objetivo rector); esto es cómo se desempata.
**El eje es lo que decide si la pregunta se contesta bien.** Comparar los brazos por recall a
secas dice que HoVer-NeXt **empeora** (19/26 → 11/26 en K=300), y eso es un artefacto de mirar
una sola columna: el detector baja el recall **y** cambia la unidad de lo que hay que revisar. Se
grafica **recall contra carga de revisión**, con la carga en las dos unidades y las dos declaradas:

- **área** (mm²) — en la que CLAM solo a K=300 pide **4,25 mm²** para 19 marcas;
- **objetos a mirar** — parches en los brazos de atención, **núcleos puntuales** en los que llevan
  HoVer-NeXt (177 detecciones en la lámina entera, 82 en la región anotada).

Ahí es donde el detector puede ganar aunque su recall sea menor, y es exactamente la pregunta de
Sebastián sobre cuánta superficie ponerle delante al patólogo (patrón P2.a.ter: el recorte compra
área, no marcas).

Se corre sobre **las dos tareas**: CDIS (`fold 4`, ya medida) y el gate de invasivo (A2/B3), y más
adelante sobre las 12 láminas (B1) con el agregado de 94 marcas.

Salida: `results/b8_hovernext_129741/escalera_brazos/` + sección en el `resultados.md` del encargo.

### A3. Offsets de las otras 11 — prerrequisito del encargo 4

Sin esto, el cruce de la fase B1 da cero: el geojson no está en coordenadas de openslide y sin
corregir **0 de 26** marcas caen sobre un parche.
[alinear_anotaciones_qupath.py](../../../scripts/alinear_anotaciones_qupath.py) ya es genérico (toma
`--slide_id`, `--geojson`, `--wsi` y deriva dx/dy por tres criterios más el control geométrico
`level0.width − region[0].width`). Se corre una vez por lámina → `offset_<id>.json` +
`parches_anotados_<id>.csv` en `sprints/B8_sprint8/anotaciones_patologo/`.

**Lo que sí hay que generalizar**: `Y_CORTE_REGION = 49920` es constante de módulo en
[techo_atencion_topk.py:45](../../../scripts/techo_atencion_topk.py#L45) y vale solo para la 129741. Pasa
a derivarse por lámina de las propiedades `openslide.region[*]`, con las láminas de una sola
región saltándose el confinamiento. Es proceso CPU largo → va desatado con `setsid` y reanudable
por el artefacto final (workaround J).

### A4. Encargo 3, mitad CLAM — atención de necrosis

`environ/results_modelo/carcinoma_ductal_insitu_necrosis_s1/s_0_checkpoint.pt` es **CLAM_MB
plano** (verificado: sin claves mammoth), 4 clases, y la **129741 cae en test** de su split. Se
le extrae la atención igual que en A2 y se cruza contra los 6 polígonos de `necrosis`.

Reportar **las dos ramas**: la de `presente_central` (la etiqueta verdadera) y la predicha. Es
la diferencia con lo que ya tiene `sgaete`, que midió sobre la rama `no identificado` y obtuvo
AUC 0,382 — bajo el azar.

---

## Fase B — GPU (las tres autorizadas)

Una sola GPU y un solo token; los tres jobs van a correr de a uno. Todos declaran `--time` real
para no matar el backfill de terceros (workaround L). `squeue` antes de cada `sbatch`.

**Orden de envío**: B3 (corto, destraba la respuesta literal del encargo 1) → B1 (el de más
valor) → B2.

### B1. Encargo 4 — HoVer-NeXt sobre las 11 restantes

Generalizar [run_hovernext_129741.slurm](../../../scripts/run_hovernext_129741.slurm) a
`scripts/run_hovernext_slides.slurm`: bucle sobre las 11 láminas dentro de **un solo job**, para
tomar el token de GPU una vez. Se conserva todo lo que ya está resuelto ahí:

- symlink `.tif` bajo `clam_testing2/wsi_shim/` por lámina (workaround M: la whitelist de
  extensión rechaza el `.bif` aunque openslide lo abra bien)
- `LD_LIBRARY_PATH` al env con la libopenslide parchada de 1,2 MB (workaround K)
- binario absoluto del env (workaround B), `set -uo pipefail` sin `-e` (workaround D)
- `preflight_hovernext.py` por lámina antes de gastar GPU (workaround G)
- `CP` con `+` en vez de coma si algún día se pasa un ensemble (workaround L.a)

**Sin `--keep_raw`**: ~135 MB por lámina en vez de 11 GB (1,5 GB total contra 121 GB). El raw
solo hacía falta para la pregunta pendiente de segmentado-pero-mal-clasificado, y el de la
129741 ya está en disco.

Estimación: la 129741 tardó **18 min** y pesa 0,73 GB; las 11 promedian 0,44 GB → **~2,5 h**.
`--time=8:00:00` por margen.

Después, en CPU: correr el cruce por lámina con su offset (A3) y **reportar el agregado sobre las
94 marcas**, más la tabla por lámina con su `n` al lado. Decir explícitamente que las láminas de
1 a 3 marcas no sostienen un número propio.

### B2. Encargo 3 — el ensemble PanNuke sobre la 129741

Mismo `.slurm`, `CP=pannuke_convnextv2_tiny_1+pannuke_convnextv2_tiny_2+pannuke_convnextv2_tiny_3`,
`TAG=pannuke`. Es la **única** vía a la clase `dead`.

Presupuesto: PanNuke tesela a 0,25 µm/px → **206.382 tiles contra 51.192** de Lizard, y encima
promedia 3 checkpoints. Sobre los 18 min medidos, la inferencia escala ~12× y el post-proceso
~4× → **~2 a 2,5 h**. `--time=10:00:00`, `--mem=128G`, **sin `--keep_raw`** (el raw a 4× serían
~40 GB inútiles).

**El cruce NO es el de mitosis, y confundirlos sería el error del encargo**: la necrosis del
patólogo son **6 polígonos** (regiones) y `dead` son **núcleos** (puntos). No hay emparejamiento
uno a uno posible. Lo que se mide:
- densidad de `dead` dentro de los polígonos contra fuera, con el enriquecimiento
- cuántos de los 6 polígonos contienen al menos un `dead`
- **nulo por traslación rígida** de la máscara, no por permutación de etiquetas, porque los
  polígonos son contiguos ([[nulo-espacial-traslacion-rigida]])

Y la advertencia de dominio, simétrica a la de mitosis: PanNuke **sí** cubre mama (6ª de 19,
mPQ 0,495), así que acá el argumento «es un paper de colon» no aplica; lo que sí hay que decir
es que corre a 0,25 µm/px sobre una lámina de 0,465, o sea interpolando.

### B3. Encargo 1 literal — CLAM plano del gate, fold 0

**Toca entrenamiento ⇒ regla 9: pre-registro antes del código, y `reviewer` antes del commit.**
El pre-registro va en `sprints/B8_sprint8/hovernext_129741/prereg_gate_invasivo.md` con
hipótesis primaria, alternativa, regresión, métrica (balanced_acc **y** AUC juntos, con matriz
de confusión y `n` por clase) y dirección esperada. Sin umbral GO/NO-GO rígido (regla 9.a).

Config **idéntica a la del brazo Mammoth** de `sgaete` para que quede pareado por construcción
(P1) — mismo `--split_dir`
`environ/splits_5fold_balanced/invasion_carcinoma_gate_pth_balance_100`, `--seed 1`,
`max_epochs 30`, `lr 2e-4`, `reg 1e-5`, `drop_out 0.25`, `B 8`, `bag_weight 0.7`,
`inst_loss svm`, `weighted_sample`, `model_type clam_mb`, `embed_dim 512`. Solo el fold 0:
`--k 5 --k_start 0 --k_end 1`. `--results_dir` absoluto dentro de nuestro repo
(`results/b8_gate_invasivo/`), preflight de mínimo de parches antes del `python main.py`
(workaround G).

Cuando termine, se repite A2 con el brazo CLAM y la comparación queda CLAM-vs-CLAM, que es lo
que pidió Sebastián.

> **ADDENDUM 21-ago (sesión 19) — el `main.py` a usar es el de `clam_testing`, no el de
> `clam_environ`, y esto NO es un detalle de plomería.** Verificado leyendo los dos árboles:
> `clam_testing/main.py` (885 líneas) y `clam_environ/main.py` (750) **divergieron**, y con
> ellos `utils/core_utils.py` (~1000 líneas de diff) y `models/model_clam.py` (~312). El brazo
> Mammoth de `sgaete` salió de `clam_testing/main.py --use_mammoth`
> (`clam_testing/run_mammoth_5fold_balanced.slurm`). Correr el CLAM plano desde
> `clam_environ/main.py` **no quedaría pareado**: cambiaría el modelo *y* el bucle de
> entrenamiento a la vez, que es exactamente lo que P1 existe para evitar.
> **La corrida pareada es `clam_testing/main.py` SIN `--use_mammoth`** — mismo archivo, único
> delta el flag. Verificado que sin el flag `CLAM_MB` construye la `nn.Linear` de siempre
> (`clam_testing/models/model_clam.py:303`, rama `else` 301-306) y que `use_mammoth` no toca ninguna otra rama.
>
> Tres cosas más que hay que saber antes del `sbatch`:
> - **Containment**: `main.py` y `core_utils.py` escriben **solo** bajo `args.results_dir`
>   (verificado con grep de `open/to_csv/torch.save/SummaryWriter`), así que un `--results_dir`
>   absoluto dentro de nuestro repo alcanza. `os.mkdir` (no `makedirs`) ⇒ crear el padre antes.
> - **`csv_path` de `TASK_CONFIGS` se resuelve relativo al CWD**, así que hay que `--chdir` a
>   `clam_testing`; su `environ/` es un **symlink a `clam_environ/environ`**, o sea el CSV
>   canónico. No se escribe nada ahí.
> - **`--k 5 --k_start 0 --k_end 1`** da `folds = arange(0,1) = [0]` y el resumen sale como
>   `summary_partial_0_1.csv`, no `summary.csv`. Y `seed_torch(args.seed)` corre **por fold**,
>   así que el fold 0 solo reproduce el fold 0 de una corrida de 5.
>
> **Riesgo declarado (workaround H, al revés):** `clam_testing/` es árbol **compartido y vivo**
> — `sgaete` tiene el job 5052 corriendo. Si edita `main.py`, `core_utils.py` o `model_clam.py`
> mientras nuestro job corre, le cambia el piso. Mitigación barata: registrar `md5sum` + `mtime`
> de los tres archivos **al lanzar y al terminar**, y guardarlos con el resultado. Si cambiaron,
> el run queda marcado como sospechoso en vez de pasar por bueno.

---

## Verificación

- **A1**: el bloque de acertadas tiene que dar exactamente 13 recortes y el de sin marca 164;
  13 + 164 = 177 = líneas de `pred_mitosis.tsv` menos la cabecera. Si no suman, el
  emparejamiento se rompió.
- **A2**: re-correr el cruce con el `--npz` **viejo** tiene que reproducir `recall 0,5`, `tp 13`
  y `n_detecciones 177` de `results/b8_hovernext_129741/cruce_marcas/meta.json`. Es el test de
  regresión del cambio a `emparejar()`.
- **A2 / chequeo de sanidad heredado**: en K = 2496 (región entera) los dos brazos tienen que dar
  el mismo número, que es el factor de detección solo. Si difieren, hay bug en el enmascarado.
- **A2.bis**: en K = 2496 los brazos de atención tienen que converger al 26/26 y los que llevan
  HoVer-NeXt al 13/26; el brazo de azar tiene que converger al mismo punto que los de atención.
  Si la escalera no cierra ahí, el eje está mal construido.
- **A3**: por lámina, el offset adoptado tiene que hacer caer la gran mayoría de las anotaciones
  sobre tejido; una lámina donde caigan casi todas fuera se reporta como no alineada y **no
  entra** al agregado.
- **B1**: `exit 0` y salida por lámina con sus `pred_*.tsv`; el preflight tiene que atajar
  cualquier lámina que no abra antes de pedir GPU.
- **B2**: la salida tiene que traer `pred_dead.tsv`. Si no está, el ensemble corrió con el
  `--metric` equivocado y el resto del encargo 3 no se sostiene.
- **B3**: `summary.csv` con AUC del fold 0 en el rango del 0,95 que reportó Sebastián para el
  gate; un valor muy distinto significa que la config no quedó pareada.

## Reglas que gobiernan esta sesión

- Nada se escribe fuera de `clam_testing2/oncomets-ernesto/`. `clam_environ/`, `clam_testing/`,
  `hover_net/` y `anotaciones/` se **leen** y no se tocan.
- `squeue` antes de cada `sbatch`; el nodo tiene jobs de terceros y uno de `sgaete` en cola.
- Commits locales granulares en `main`, `git branch --show-current` antes de cada uno, nunca
  `git add -A`, push solo si Ernesto lo pide.
- No se calcula precisión contra el geojson, no se llama falso positivo a nada, y no se mezcla
  la unidad: **marcas (26/94)**, **parches (28)**, **detecciones (177)**.
