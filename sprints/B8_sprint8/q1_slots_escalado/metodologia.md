# Escalado de la Q1: método y validación

Encargo 1 de la reunión del 24-jul-2026. Benjamín objetó que los **158.7 slots efectivos
de 300** salían de **7 láminas** y no generalizan al conjunto de la tarea. Acá está cómo
se escaló la medición y por qué el número nuevo es comparable con el viejo.

Los resultados están en [`resultados.md`](resultados.md). Este documento es el método.

## 1. Qué se mide (idéntico al B7)

- **Peso por slot** = `combine_weights`, la segunda softmax sobre los E·S=300 slots
  (`mammoth.py:411`). No es el top-k de parches por experto
  ([[mammoth-slot-routing-weight]]).
- **Uso por experto** = `dispatch_weights` normalizado por parche y promediado sobre
  cabezas y slots, igual que `mammoth_interpretability.compute_expert_scores`.
- **Número efectivo** = exp(entropía de la distribución de pesos). Da 300 si el ruteo
  reparte parejo entre los 300 slots y 1 si colapsa en uno solo. Se usa porque la softmax
  da peso positivo a todos los slots: contar «los que reciben algo» daría siempre 300.
- **Cota del uniforme** = 1/300 = 0.333 %, el único corte sin parámetro libre
  ([[cota-softmax-slots-uniforme]]): cuántos slots la superan y qué masa concentran.

## 2. Qué se barre

Todas las láminas de **test de los 5 folds de las 3 tareas** del job 4589:

| Tarea | Láminas-fold |
|---|---|
| `tipo_histologico_3clases_ci` | 1013 |
| `carcinoma_ductal_insitu_presente_ci_reform` | 429 |
| `invasion_linfatica_vascular_ci_reform` | 416 |
| **Total** | **1858** (sobre 1176 láminas únicas) |

Una lámina puede aparecer en el test de más de un fold: los splits son Monte Carlo CV, con
test solapados (el rótulo «k-fold» de los archivos es un identificador histórico). Cada par
(fold, lámina) se mide con **el checkpoint de ese fold**, así que son mediciones distintas,
no repeticiones de la misma.

**El conjunto medido sale de `test_predictions.csv`** del brazo `clam_mammoth` de cada
fold, o sea de la verdad de campo del propio job, en lugar de re-derivar el split cruzando
la columna `test` del `splits_<f>.csv` con el CSV de labels y el `label_dict`. Así el
conjunto es exactamente el que evaluó el job, sin reimplementar ese filtro.

## 3. Lo que destrabó el escalado

**La medición no necesita la WSI.** Features y coords viven en el mismo h5
(`load_feats_and_coords`, `scripts/mammoth_interpretability.py:128`); el `.svs` se abría
sólo para la miniatura, los overlays y los recortes de alta resolución. Esa dependencia es
la que había limitado el Sprint 7 a 7 láminas TCGA con `.svs` disponible. Sacándola, el
barrido cubre las tres cohortes: **981 láminas-fold TCGA, 688 HistAI y 189 privadas**.

Lo caro de los ~10 min por lámina del B7 era rasterizar los 30 paneles del montage, no el
forward. Sin matplotlib ni openslide, el costo real es de **décimas de segundo por lámina**.

## 4. Streaming exacto sobre los parches

`scripts/q1_slots_escalado.py` no materializa los logits de los N parches de una vez:
serían N·30·16·10 floats, unos 380 MB para una lámina de 20 mil parches, y hay láminas
bastante más grandes.

El detalle que obliga a tener cuidado es que **`dispatch_weights = softmax(logits, dim=n)`
normaliza sobre los parches**, no sobre los expertos: no es separable por chunk. Se
resuelve con dos pasadas sobre la proyección `q` (que sí es chica y se materializa entera):

1. **Pasada 1**: acumula `combine` (softmax local por parche y cabeza, separable) y el
   logsumexp sobre parches que necesita `dispatch`, con máximo incremental.
2. **Pasada 2**: aplica el denominador global, normaliza por parche y acumula el uso por
   experto.

El resultado es **exacto, no aproximado**. Las dos implementaciones suman los mismos
términos float32 en distinto orden, así que coinciden hasta el redondeo de float32, no bit
a bit: por eso el `--self-test` usa tolerancia **relativa** de 1e-5 y no una absoluta.

## 5. Validación contra el n=7

Dos chequeos, los dos PASS, corridos el 27-jul-2026:

**`--self-test`**: el camino streaming contra la implementación original del B7
(`compute_expert_scores` + `compute_slot_weights`) sobre una lámina de 2793 parches.

```
max |Δ| relativo: expertos 1.63e-07  slots 5.27e-08
n_eff:            expertos 3.79e-10  slots 7.37e-09      PASS (tolerancia 1e-5)
```

**`--validate-b7`**: las 7 láminas del Sprint 7, comparadas contra
`sprints/B7_sprint7/respuesta_q1_expertos_slots.json` lámina por lámina.

| Lámina | Slots (B8) | Slots (B7) |
|---|---|---|
| `TCGA-A7-A4SB` (CDIS) | 89.7 | 89.7 |
| `TCGA-D8-A1XB` (CDIS) | 180.3 | 180.3 |
| `TCGA-D8-A1X5` (LVI) | 162.4 | 162.4 |
| `TCGA-D8-A1XW` (LVI) | 196.4 | 196.4 |
| `TCGA-AC-A8OS` (tipo) | 156.0 | 156.0 |
| `TCGA-AO-A12D` (tipo) | 178.3 | 178.3 |
| `TCGA-E9-A1NE` (tipo) | 147.5 | 147.5 |

Media **158.7 de 300** y expertos **30.0 de 30**, que son exactamente los números del B7.
Peor delta relativo por lámina: 4.18e-08. **El número nuevo y el viejo miden lo mismo**, así
que la diferencia entre ambos es tamaño de muestra y nada más.

## 6. Cómo correrlo

CPU post-hoc, sin GPU, sin `sbatch`. Inferencia sobre checkpoints congelados: no toca
modelo ni entrenamiento, así que la **regla 9 no aplica** (igual que todo el trabajo
post-hoc del B7). Binario absoluto del env (workaround B).

```bash
PY=/home/sdonoso/miniconda3/envs/clam_latest/bin/python
cd /media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto

CUDA_VISIBLE_DEVICES="" $PY scripts/q1_slots_escalado.py --self-test --validate-b7
CUDA_VISIBLE_DEVICES="" $PY scripts/q1_slots_escalado.py            # barrido completo
CUDA_VISIBLE_DEVICES="" $PY scripts/q1_slots_escalado.py --solo-agregar
```

El barrido completo tarda unos **20 minutos** con `--threads 8` (default, por cortesía: el
nodo es compartido y los jobs SLURM ajenos también usan CPU). Aun así se lanzó **desatado**
por el workaround J:

```bash
setsid nohup env CUDA_VISIBLE_DEVICES="" $PY scripts/q1_slots_escalado.py \
    > logs/q1_slots_escalado_desatado.log 2>&1 < /dev/null &
```

**Reanudable**: cada fold escribe `laminas.csv` fila a fila y se marca terminado con
`meta.json`, que es el artefacto **final**. Un fold sin `meta.json` se retoma desde la
última fila íntegra del CSV, y la agregación excluye los folds sin marcar, así que una
corrida cortada nunca entra a medias en el promedio.

## 7. Salida

```
results/b8_q1_slots_escalado/
├── <tarea>/fold<f>/laminas.csv     una fila por lámina + meta.json al terminar el fold
├── q1_escalado_laminas.csv         las 1858 filas juntas
├── q1_escalado_por_grupo.csv       resumen por tarea y por cohorte
└── validacion/validacion_b7.json   las 7 láminas del B7 remedidas
```

Columnas por lámina: `task`, `fold`, `slide_id`, `cohorte`, `n_parches`, `n_eff_expertos`,
`expertos_50/90`, `expertos_sobre_uniforme`, `n_eff_slots`, `slots_50/90`,
`slots_sobre_cota`, `masa_sobre_cota`, `y_true`, `y_pred`, `top5_slots`, `segundos`.
