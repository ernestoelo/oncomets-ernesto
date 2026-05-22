# Plan de entrenamiento — 3 tareas binarias de microcalcificaciones

> **Scaffolding — NO se ejecuta** hasta cumplir las precondiciones (ver
> `README.md` y §5). Esta es la **próxima implementación de entrenamiento**
> del Sprint B4, lista para lanzar cuando la reunión la confirme.
>
> Cumple la regla 9 de `CLAUDE.md` — "argumento antes de código":
> hipótesis enunciada de antemano + métrica de éxito predefinida.

---

## 1. Argumento — por qué este experimento

El baseline 8-clases (job 4098) tiene dos problemas, ambos del **régimen
de evaluación**, no del entrenamiento (`../objetivo_1_baseline/resultados.md`):

- 4 de 8 clases con **1 muestra** en val/test → macro-AUC = ruido.
- `balanced accuracy 0.31`, el modelo colapsa a la clase mayoritaria.

Causa raíz: las 8 clases son un **multi-etiqueta de 3 tejidos aplastado**
en clases-combinación. Aplastar fabrica clases ultra-raras (la triple:
6 slides). La reformulación en 3 tareas binarias **des-aplasta**: re-cuenta
los slides multi-combinación y produce, por tarea, un régimen de
evaluación medible (≥7 positivos en val/test, ver `README.md`).

Argumento detallado y conexión con la literatura (PCGrad, HMIL):
[`../objetivo_3_modulo_mil_alternativo/investigacion/05_papers_eduardo_desbalance.md`](../objetivo_3_modulo_mil_alternativo/investigacion/05_papers_eduardo_desbalance.md)
y [`06_busqueda_web_multiclase_desbalance.md`](../objetivo_3_modulo_mil_alternativo/investigacion/06_busqueda_web_multiclase_desbalance.md).

---

## 2. Hipótesis (enunciada ANTES de correr)

> **H1.** Entrenar las 3 tareas binarias (CLAM_MB, una corrida
> independiente por tejido, sobre los CSVs/splits existentes) produce,
> por tarea, un **balanced accuracy en test claramente superior al del
> modelo 8-clases (0,31)** — porque el modelo deja de gastar capacidad
> separando combinaciones que comparten tejido, y cada tarea tiene una
> frontera de decisión binaria bien poblada.

> **H2.** El régimen de evaluación deja de ser ruido: `val_auc` y
> `test_auc` por tarea quedan **consistentes** (sin la inversión
> `val < test` del baseline 8-clases, que era la firma de la
> inestabilidad), porque cada split tiene ≥7 positivos en val y test.

> **H3 (mecanismo, falsable).** La señal *"hay microcalcificación en
> este parche"* es común a las 3 tareas; lo que cambia es el tejido. Por
> eso, si más adelante se entrena un **backbone compartido** (ruta
> multi-task / PCGrad), se espera **eficiencia de datos** sobre las 3
> corridas independientes. H3 NO se testea en este plan — es la
> motivación del paso siguiente.

---

## 3. Métrica de éxito (predefinida)

Para **cada** una de las 3 tareas binarias, sobre el **split de test**:

| Métrica | Cómo | Umbral de éxito |
|---|---|---|
| **Balanced accuracy** | media del recall por clase, desde `split_0_results.pkl` | **tejido y cdis: > 0,65** · **carcinoma: > 0,60** (menor `n` de positivos → umbral más laxo, reportado con honestidad) |
| **Matriz de confusión 2×2** | desde `split_0_results.pkl`, **siempre con el `n` por clase** | informativa — no umbral, pero debe mostrarse |
| **AUC** | `summary.csv` (`test_auc`, `val_auc`) | secundaria; éxito si **`|val_auc − test_auc|` < 0,10** (H2 — sin inversión) |

**Métrica primaria = balanced accuracy.** El macro-AUC solo, **nunca**
(lección del baseline; `CLAUDE.md` Hallazgo 6).

**Comparaciones obligatorias** (contexto para interpretar el número):

1. **Baseline trivial por tarea**: predecir siempre la clase mayoritaria
   → balanced accuracy = 0,50. El modelo debe superarlo con holgura.
2. **Modelo 8-clases proyectado a cada eje binario**: tomar el
   `split_0_results.pkl` del job 4098, colapsar las 8 clases predichas a
   `si/no` por tejido, y calcular el balanced accuracy binario. Es la
   comparación *directa* "reformular vs no reformular".

**Dirección**: balanced accuracy ↑ frente a ambas comparaciones. Si una
tarea no supera el baseline trivial, la reformulación **no** ayudó en esa
tarea — resultado válido y reportable (no se maquilla).

> **Falsabilidad.** Si las 3 tareas dan balanced accuracy ≈ 0,50 o
> mantienen la inversión `val/test`, H1 y H2 se refutan: el problema no
> era la formulación sino algo más profundo (features, etiquetas). Es un
> resultado publicable para la reunión, no un fracaso del plan.

---

## 4. Configuración de las corridas

3 corridas **independientes**, una por tarea. Args **bendecidos**
(`CLAUDE.md`) + los específicos:

| Arg | Valor | Nota |
|---|---|---|
| `--task` | `microcalcificaciones_en_{carcinoma_invasivo,cdis,tejido_no_neoplasico}_pth` | task configs ya registradas |
| `--split_dir` | `environ/splits/microcalcificaciones_en_<tejido>_pth_100` | o el filtrado `minpatch` si el preflight lo exige (§5) |
| `--model_type` | `clam_mb` | igual que el baseline |
| `--embed_dim` | `512` | CONCH |
| `--auto-label-dict` | (flag) | **obligatorio** — `label_dict={}` (`no`=0, `si`=1) |
| `--bag_loss` | `ce` · `--inst_loss svm` · `--drop_out 0.25` · `--lr 2e-4` | bendecidos |
| `--B` | `8` | mismo que el baseline, para comparar |
| `--weighted_sample` | (flag) | **clave** — carcinoma es 20 % positivos; corrige el desbalance intra-tarea |
| `--early_stopping` · `--k 1` · `--log_data` | | bendecidos |
| `--results_dir` | `results/reformulacion_multilabel/<tejido>` | absoluto, bajo el repo personal (containment) |

Tratamiento opcional del desbalance intra-tarea (carcinoma, 20 %): focal
loss / label smoothing del paper de Chen & Xu (`05_…desbalance.md` §2) —
**no en esta primera corrida**: primero medir CLAM_MB + `--weighted_sample`
puro, luego decidir. Mantener una variable a la vez.

Plantilla `.slurm`: [`train_microcalc_3binarios.slurm`](train_microcalc_3binarios.slurm).

---

## 5. Precondiciones de ejecución — checklist

**Ninguna se asume cumplida. Cero `sbatch` hasta marcar las 4.**

- [ ] **Reunión confirma la reformulación** como dirección para
      `microcalcificaciones` (precondición A).
- [ ] **`no_identificado` ratificado.** El equipo eligió `excluir`
      (333 slides). La reunión debe confirmar la interpretación clínica.
      Si se decide "negativo limpio", regenerar CSVs con
      `--no-identificado negativo` + splits nuevos (precondición B).
- [ ] **Preflight `topk`** (`CLAUDE.md` workaround G): correr
      `scripts/preflight_minpatch.py` sobre los 3 splits de train. Si
      alguna slide de train tiene `< B` parches, filtrar con
      `scripts/filter_split_by_minpatch.py` hacia `splits_local/` y usar
      esa copia. El bloque preflight va **dentro** del `.slurm`.
- [ ] **Cortesía de GPU** (`CLAUDE.md`): `squeue` antes de lanzar — GPU
      única, partición única. No monopolizar si hay jobs ajenos
      pendientes por `Resources`.

---

## 6. Evaluación post-corrida

Por cada tarea, al terminar:

1. `summary.csv` → `test_auc`, `val_auc` (chequear H2: sin inversión).
2. `split_0_results.pkl` → **balanced accuracy** + **matriz de confusión
   2×2 con `n` por clase**. (`scripts/extract_metrics.py` o equivalente.)
3. Proyectar el `split_0_results.pkl` del baseline 8-clases (job 4098) a
   cada eje binario → comparación "reformular vs no reformular".
4. Entregable: una tabla de las 3 tareas (balanced accuracy, matriz, AUC,
   `n`) — formato visual (`CLAUDE.md`: diagramas > texto), insumo para la
   reunión / el siguiente sprint.

**No reportar el macro-AUC solo. Siempre el `n` por clase visible.**

---

## 7. Qué sigue (fuera de este plan)

Si H1/H2 se confirman, el paso siguiente — **no este plan** — es la ruta
multi-task con backbone compartido + PCGrad
(`05_…desbalance.md` §1), que requiere generar un **split compartido**
estratificado sobre las 8 clases. Y, ortogonalmente, la decisión del
módulo MIL (CLAM vs DSMIL, Objetivo 3). Ambos se deciden en la reunión.
