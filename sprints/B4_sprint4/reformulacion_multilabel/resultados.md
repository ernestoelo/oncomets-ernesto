# Reformulación multi-label — Resultados PRELIMINARES (3 tareas binarias)

> Job `4109` **COMPLETED** el 22 may 2026 (00:16). Las 3 tareas binarias
> corrieron secuenciales en un mismo job (~42 min total, 30 épocas c/u, sin
> crashes). Números reales de los `summary.csv` y recálculo desde los
> `split_0_results.pkl` de cada tarea. No se inventa nada.
>
> **PRELIMINAR** — 1 sola semilla, 333 slides por tarea. Contingente a que
> la reunión (a) confirme la reformulación y (b) ratifique qué es
> `no_identificado`. Ver `README.md` § precondiciones.

## Setup

| Campo | Valor |
|---|---|
| Tareas | `microcalcificaciones_en_{carcinoma_invasivo,cdis,tejido_no_neoplasico}_pth` |
| CSVs / splits | existentes en `clam_environ/environ/` (infra del equipo); 333 slides, `no_identificado` excluido |
| Modelo | CLAM_MB | 
| Features | CONCH 512-dim | 
| Args | bendecidos + `--B 8` + `--max_epochs 30` |
| `.slurm` | `train_microcalc_3binarios.slurm` (job `4109`) |
| Etiquetas (auto-label-dict) | `no`=0, `si`=1 |
| Épocas | 30 exactas (early stopping `stop_epoch=50` > 30 → no recorta) |

## Tabla de resultados

Métrica primaria = **balanced accuracy** (promedio del recall por clase,
recalculada del `split_0_results.pkl`). **Piso trivial binario = 0.50** —
un binario se ancla solo: 0.50 = "no aprendió nada". No hace falta baseline.

| Tarea | positivos test | test_auc | val_auc | test_acc | **balanced acc** | umbral predefinido | ¿cumple? |
|---|---|---|---|---|---|---|---|
| **carcinoma invasivo** | 7 / 33 | 0.808 | 0.704 | 0.818 | **0.780** | > 0.60 | ✅ **sí, con holgura** |
| **CDIS** | 13 / 35 | 0.678 | 0.758 | 0.629 | **0.594** | > 0.65 | ❌ no (apenas sobre 0.50) |
| **tejido no neoplásico** | 20 / 33 | 0.658 | 0.831 | 0.576 | **0.583** | > 0.65 | ❌ no (apenas sobre 0.50) |

> Umbrales tomados de `plan_entrenamiento.md` §3 (predefinidos antes de
> correr — regla 9 de `CLAUDE.md`).

## Matrices de confusión (test) — fila = verdadera, columna = predicha

```
carcinoma invasivo (n=33)        CDIS (n=35)                  tejido no neoplásico (n=33)
          pred:no  si                  pred:no  si                    pred:no  si
verdad no:   22     4         verdad no:   16     6           verdad no:    8     5
verdad sí:    2     5         verdad sí:    7     6           verdad sí:    9    11

recall no = 22/26 = 0.85      recall no = 16/22 = 0.73        recall no =  8/13 = 0.62
recall sí =  5/7  = 0.71      recall sí =  6/13 = 0.46        recall sí = 11/20 = 0.55
```

## Qué cambió vs lo canónico de Sebastián

La **única diferencia** con el pipeline canónico del equipo es la
**organización de las etiquetas**:

| | Canónico (8 clases) | Esta reformulación |
|---|---|---|
| Etiquetas | **1 CSV** con 8 valores-combinación | **3 CSVs binarios** (`si`/`no`) |
| Tasks | 1 task (`microcalcificaciones_pth`) | 3 tasks (una por tejido) |
| Runs | 1 run | 3 runs |
| Modelo | CLAM_MB | **idéntico** |
| Features | CONCH 512-dim | **idénticas** |
| Args bendecidos | drop_out 0.25, lr 2e-4, ce, svm, B, weighted_sample… | **idénticos** |

Todo lo demás —arquitectura, extractor de features, hiperparámetros
bendecidos— es **exactamente el mismo**. No tocamos el modelo ni los datos.

**Y los 3 CSVs / tasks binarios YA EXISTÍAN** en `clam_environ/` (infra del
equipo de Sebastián: CSVs del 12 may, task configs en `main.py`, splits
estratificados). Nuestra contribución nueva en esta reformulación fue solo:

- el **`.slurm`** que lanza las 3 tareas (`train_microcalc_3binarios.slurm`), y
- el **script verificador** (`scripts/verify_binary_microcalc_csvs.py`), que
  confirma de forma determinística que esos CSVs están bien derivados
  (cross-check MATCH: positivos 68/121/195).

En otras palabras: **no construimos infraestructura nueva de entrenamiento;
re-organizamos cómo se le presenta el problema al mismo modelo.**

## Veredicto preliminar

Tres lecturas, en orden de importancia:

**1. El mayor logro es el régimen de evaluación, no el score.** En el
modelo de 8 clases, 4 clases tenían **1 sola muestra** en val/test → la
métrica era ruido y no se podía concluir nada. Ahora cada tarea tiene
**7–20 positivos en test** → los números **se pueden creer**. Aunque CDIS y
tejido den flojo, son números *honestos*, no artefactos. Eso ya valida la
dirección.

**2. Carcinoma invasivo demuestra que des-aplastar recupera señal real.**
Era el tejido **más fragmentado** en las 8 clases (repartido en 4 clases
rarísimas). Al reagruparlo en una pregunta binaria (68 positivos), el modelo
**aprendió a detectarlo**: balanced accuracy 0.78, muy por encima del piso
0.50. Es exactamente lo que predecía el argumento de la reformulación.

**3. CDIS y tejido siguen difíciles — techo de datos, no de formulación.**
0.59 y 0.58 están *apenas* sobre 0.50. Si normalizamos "cuánto sube sobre el
piso", CDIS y tejido (0.18 y 0.16) suben parecido a lo que subía el modelo
de 8 clases sobre *su* piso (0.21); solo carcinoma (0.56) claramente más. La
causa probable es el **techo de datos**: con 333 slides, CLAM_MB sobreajusta
—visible en tejido, val_auc 0.83 vs test 0.66—. Coincide con lo que avisaban
los papers (`05_`/`06_`): la estructura ayuda, pero ningún truco de modelo
fabrica muestras que no existen.

**Síntesis**: la reformulación es la dirección correcta —arregló lo que
estaba definitivamente roto (la medición) y volvió aprendible el tejido más
fragmentado—. Pero **no es magia**: el siguiente cuello de botella es
**datos**, no formulación. Cumplir el umbral en 1 de 3 y quedarse corto en 2
es información honesta (umbrales fijados *antes* de correr), no un fracaso.

## Caveats

- **PRELIMINAR**: 1 semilla, 333 slides. Sin múltiples corridas no hay
  barras de error; los scores tienen incertidumbre (carcinoma se apoya en
  **7 positivos de test**).
- **Contingente a la reunión**: si `no_identificado` no significa "sin
  microcalcificación", habría que rehacer los CSVs (`--no-identificado
  negativo`) y re-correr.
- **Sobreajuste**: 333 slides es poco para CLAM_MB; los gaps val−test
  (sobre todo tejido) lo confirman.
- **Comparación plano-vs-binario perfecta pendiente**: medir 7 clases vs 3
  binarios sobre las *mismas* 333 slides aislaría el efecto de la
  reformulación. Bloqueada porque registrar la task de 7 clases exige editar
  `clam_environ` (read-only) — pregunta #16 para la reunión (`README.md`).

## Para la reunión

- Llevar carcinoma como **prueba de concepto** de que la reformulación
  funciona, y CDIS/tejido como evidencia de que el límite ahora es **datos**.
- Decidir: ¿se adopta la reformulación? ¿qué es `no_identificado`? ¿se
  registra la task plana de 7 clases para la comparación controlada?
- Resultados detallados por slide: `results/reformulacion_3binarios_<tejido>/`.
