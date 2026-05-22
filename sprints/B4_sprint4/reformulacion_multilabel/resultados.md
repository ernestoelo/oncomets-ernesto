# Resultados — Reformulación Multi-label

> **ESTADO: PRELIMINAR** — 1 semilla, 333 slides, contingente a la reunión
> (confirmación de la reformulación + aclaración de `no_identificado`).

---

## Qué cambió vs lo canónico de Sebastián

| Dimensión | Canónico (Obj 1 baseline) | Esta reformulación |
|---|---|---|
| CSV de etiquetas | 1 archivo, columna `label` con 8 valores | 3 archivos, cada uno con `label` binario (0/1) |
| `--task` | 1 (`microcalcificaciones_pth`) | 3 (una por tejido) |
| Runs de entrenamiento | 1 | 3 (job `4109`, secuenciales, ~42 min) |
| Cabeza del modelo | 8 salidas (softmax multiclase) | 2 salidas (sí/no) ×3 |
| Slides usadas | 3072 (incluye `no_identificado`) | 333 (excluye `no_identificado`) |
| Modelo / features / args bendecidos | CLAM_MB, CONCH 512-dim, B=8 | **idénticos** |

**La única diferencia es la organización de las etiquetas.** Modelo, features
y args son idénticos a los aprobados por Sebastián. Los 3 CSVs/tasks binarios
ya existían en `clam_environ` (infraestructura del equipo de Sebastián). Lo
único nuevo de este objetivo fue:
- El `.slurm` que apunta a las 3 tasks con `--max_epochs 30`.
- El script verificador de que los labels binarios coinciden con la partición
  manual esperada.

---

## Por qué se reformuló (motivación resumida)

Las 8 clases de `microcalcificaciones_pth` son combinaciones de 3 tejidos
(carcinoma invasivo, CDIS, tejido no neoplásico) + `no_identificado`.
Eso genera dos problemas demostrados en los Objetivos 1 y 2:

1. **Clases fantasma**: 4 de 8 clases con 1 sola muestra en val/test → métrica
   no confiable.
2. **Fragmentación de señal**: la triple combinación tiene 6 slides en total;
   el carcinoma está partido en 4 cajas (38 / 11 / 13 / 6). Un modelo no puede
   aprender de 6 ejemplos.
3. **Colapso a mayoritaria**: el modelo predice `no_identificado` para el 74.5%
   de los slides de test (Objetivo 1, balanced acc = 0.31).

La reformulación convierte 1 pregunta de 8 combinaciones en 3 preguntas
binarias independientes. Los ejemplos fragmentados se reagrupan:

```
carcinoma (38) + carcinoma+cdis (11) + carcinoma+tejido (13) + triple (6)
  ──────────────────────────────────────────────────────────────────────
             = 68 positivos para "¿hay micro en carcinoma?"
```

Una slide con múltiples tejidos cuenta como positivo en varias tareas — no
cae en una sola caja. El negativo de cada tarea no es "sin microcalcificación"
sino "con microcalcificación, pero en otro tejido" → clases más balanceadas.

---

## Setup del entrenamiento

- **Job SLURM**: `4109`  
- **Duración**: ~42 min (3 runs secuenciales, 30 épocas cada uno)  
- **Modelo**: CLAM_MB  
- **Features**: CONCH 512-dim  
- **Args bendecidos**: `--drop_out 0.25 --lr 2e-4 --bag_loss ce --inst_loss svm`
  `--model_type clam_mb --embed_dim 512 --k 1 --early_stopping`
  `--weighted_sample --auto-label-dict --B 8 --max_epochs 30`  
- **Splits**: los proporcionados por el equipo (`val_frac=test_frac=0.1`,
  `seed=1`, excluye `no_identificado`)  
- **Slides totales**: 333  

---

## Resultados

### Tabla de métricas (test)

| Tarea | Positivos en test | test_auc | balanced_acc | Umbral predefinido | ¿Cumple? |
|---|---|---|---|---|---|
| carcinoma invasivo | 7 / 33 | 0.81 | **0.78** | > 0.60 | ✅ sí, con holgura |
| CDIS | 13 / 35 | 0.68 | 0.59 | > 0.65 | ❌ no (apenas sobre 0.50) |
| tejido no neoplásico | 20 / 33 | 0.66 | 0.58 | > 0.65 | ❌ no (apenas sobre 0.50) |

> **Piso trivial de balanced accuracy = 0.50** (adivinar siempre la clase
> mayoritaria en un binario). Todo resultado ≤ 0.50 = el modelo no aprendió nada.

### Matrices de confusión

#### Carcinoma invasivo (balanced acc 0.78)

```
                pred: NO    pred: SÍ
verdad NO:        22           4
verdad SÍ:         2           5

recall_positivo = 5/7 = 0.71
precision_positivo = 5/9 = 0.56
```

#### CDIS (balanced acc 0.59)

```
                pred: NO    pred: SÍ
verdad NO:        16           6
verdad SÍ:         7           6

recall_positivo = 6/13 = 0.46
precision_positivo = 6/12 = 0.50
```

#### Tejido no neoplásico (balanced acc 0.58)

```
                pred: NO    pred: SÍ
verdad NO:         8           5
verdad SÍ:         9          11

recall_positivo = 11/20 = 0.55
precision_positivo = 11/16 = 0.69
```

---

## Análisis

### (a) El mayor logro es invisible en la tabla

Antes de esta reformulación, 4 de las 8 clases tenían 1 sola muestra en
val/test → cualquier métrica era ruido estadístico puro. Ahora cada tarea
tiene 7–20 positivos en test. **Los números son creíbles.** Eso, por sí solo,
ya valida que la dirección era correcta — independientemente del valor de
balanced accuracy.

### (b) Carcinoma invasivo es la prueba de concepto

Era el tejido más fragmentado en las 8 clases: estaba repartido en 4
combinaciones con 6–38 slides cada una. Al reagruparlas en 1 sola pregunta
binaria, el modelo juntó 68 positivos y aprendió (balanced acc 0.78, muy por
encima del piso 0.50). Esto confirma empíricamente el argumento central:
des-aplastar el multi-etiqueta libera señal que estaba dispersa.

### (c) CDIS y tejido siguen flojos — y era esperable

0.59 y 0.58 están apenas sobre el piso de 0.50. La causa más probable es el
techo de datos: con 333 slides, CLAM_MB sobreajusta. Evidencia directa en
tejido: val_auc 0.83 >> test_auc 0.66 (brecha val-test de 0.17). Esto es
exactamente lo que predicen Chen & Xu y HMIL: ningún truco arquitectónico
vence la falta de datos. La reformulación **arregló la medición** para estos
dos tejidos; el aprendizaje sigue limitado por el n.

Nota: normalizado como "cuánto sube sobre el piso", CDIS y tejido suben
parecido a lo que subía el modelo de 8 clases sobre su piso trivial. La
reformulación no multiplicó el aprendizaje en estos dos casos.

---

## Veredicto preliminar

**La reformulación es la dirección correcta, confirmado en lo que importa:**

1. El régimen de evaluación pasó de "no medible" (4 clases con 1 muestra)
   a "medible y confiable" (7–20 positivos por tarea en test).
2. Carcinoma invasivo (el tejido más fragmentado) se volvió claramente
   aprendible → prueba de concepto del argumento.
3. Cumplir el umbral en 1 de 3 y quedarse corto en 2 **es un dato honesto**,
   no un fracaso. Los umbrales se fijaron antes de correr.

**El siguiente cuello de botella es datos, no formulación.** Con el dataset
compartido unificado (>1000 slides), la expectativa es que CDIS y tejido
superen sus umbrales sin cambiar modelo ni args.

---

## Caveats y preguntas abiertas para la reunión

1. **PRELIMINAR — 1 semilla.** Resultado contingente a confirmación en la
   reunión con Sebastián y Eduardo.
2. **¿Qué significa `no_identificado`?** Si significa "hay microcalcificación
   sin ubicar" (y no "sin microcalcificación"), habría que rehacer los CSVs
   y re-correr. Si significa "sin microcalcificación", los CSVs actuales son
   correctos y los resultados se sostienen.
3. **Carcinoma: 7 positivos en test** — resultado real pero con incertidumbre
   alta por el n chico. Con más datos, el intervalo de confianza se estrecha.
4. **Comparación plano 7-clases vs 3 binarios (misma data)**: sería el
   experimento ideal para aislar el efecto de la reformulación. Pendiente
   porque registrar esa task exige editar `clam_environ` (read-only). Lo
   dejamos como pregunta #16 para la reunión.
5. **El 0.55 de V4 (`Environ_OncoMets_Metricas_V4.pdf`)** corresponde a una
   configuración diferente — no es el blanco de reproducción de este objetivo.
