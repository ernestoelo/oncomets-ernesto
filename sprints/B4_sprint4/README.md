# B4 — Sprint 4

> **Estado**: scaffolding inicial (12 mayo 2026). Dataset compartido,
> splits canónicos y división de trabajo Ernesto/Eduardo **pendientes**
> de reunión con Sebastián + Eduardo (fecha sin confirmar, esta semana).

## Contexto que abrió el sprint

- **12 mayo 2026**: presentación al equipo. Benjamín felicitó el sprint
  anterior y dejó dirección clara:
  > **De propuestas teóricas a implementación con argumento clínico /
  > arquitectónico explícito. No probar por probar.**
- **Métricas distribuidas por Sebastián** (`Environ_OncoMets_Metricas_V4.pdf`,
  1397 slides = TCGA + HISTAI + Environ). Tareas peor evaluadas
  (AUC test < 0.65) que abren el foco del sprint:

  | Tarea | AUC test | AUC val | Gap | n |
  |---|---|---|---|---|
  | MicroCalcificaciones | 0.55 | 0.82 | 0.27 | 548 |
  | C.D.I. Grado Nuclear | 0.60 | — | — | 508 |
  | C.D.I. Necrosis | 0.61 | — | — | 508 |
  | G.H. Diferenciación Tubular | 0.65 | 0.81 | 0.16 | 934 |

- **Procesamiento adicional**: Sebastián está procesando ~1400 slides
  públicas adicionales. Dataset compartido final = pendiente.

## Hilos del sprint (4)

Los 4 hilos corren **sobre el dataset compartido** una vez definido. Antes
de la reunión, lo que se puede hacer es preparar wrappers y skeletons.

### Objetivo 1 — Baseline CLAM reproducible

[`objetivo_1_baseline/`](objetivo_1_baseline/)

Reproducir CLAM con los args bendecidos por Sebastián, sobre el dataset
compartido, en las 4 tareas prioritarias. **Punto de partida** para los
otros 3 hilos.

### Objetivo 2 — Ablation cuantitativa `B=8` vs `B=16`

[`objetivo_2_ablation_B/`](objetivo_2_ablation_B/)

Comparación directa del hiperparámetro `--B` (top-B / bottom-B count del
instance classifier path) sobre las tareas prioritarias. **Hipótesis
enunciada de antemano + métrica de éxito predefinida** (regla operativa
"Argumento antes de código").

### Objetivo 3 — Implementar DSMIL como módulo MIL alternativo

[`objetivo_3_dsmil/`](objetivo_3_dsmil/)

Wrapper que reemplaza el `attention_net` de CLAM por el aggregator
dual-stream de DSMIL (Li et al., CVPR 2021, paper en
[`../../papers/dsmil_li2021.pdf`](../../papers/dsmil_li2021.pdf)).
**Argumento arquitectónico**: el attention pooling lineal de CLAM no
modela relaciones inter-parche y es estructuralmente el peor caso para
tareas focales como MicroCalcificaciones; DSMIL agrega una segunda rama
que captura el "parche crítico" preservando el resto del pipeline
(CONCH features, bag classifier, CSVs).

### Objetivo 4 — Heatmaps cualitativos lado-a-lado

[`objetivo_4_heatmaps/`](objetivo_4_heatmaps/)

N slides representativas, heatmaps de attention para baseline + B=16
+ DSMIL. **Upgrade a cuantitativo (IoU / Dice)** si Sebastián confirma
disponibilidad de anotaciones de patólogo a nivel de región (existen
para un subset; pendiente confirmar alcance).

## Decisiones pendientes — reunión Sebastián + Eduardo

| # | Decisión | Bloquea |
|---|---|---|
| 1 | Composición exacta del **dataset compartido** (Environ + TCGA + HISTAI; fracciones; criterios de inclusión) | Objetivos 1, 2, 3, 4 |
| 2 | **Splits canónicos** que los tres usaremos (Ernesto, Eduardo, Sebastián) — necesario para comparar resultados | Objetivos 1, 2, 3 |
| 3 | **División de trabajo** Ernesto / Eduardo (¿quién toma qué tarea, qué hilo?) | Plan de ejecución del sprint |
| 4 | **Anotaciones de patólogo**: existencia, formato, % de slides cubiertas | Upgrade Objetivo 4 a cuantitativo |
| 5 | **Confirmación de las 4 tareas prioritarias** (¿se mantienen, se añade, se quita alguna?) | Objetivos 1, 2 |

Una vez confirmadas, actualizar este README y los READMEs de cada
objetivo con: dataset path, split path, tarea(s) asignada(s).

## Regla operativa nueva (interpretación del feedback de Benjamín)

Toda propuesta de implementación o módulo nuevo viene con justificación
clínica / arquitectónica explícita **antes** de tocar código. Una
ablation cuantitativa cuenta como argumento solo si:

1. La **hipótesis** está enunciada de antemano (qué se espera observar y
   por qué, en términos del mecanismo del modelo o de la tarea clínica).
2. La **métrica de éxito** está predefinida (qué número, sobre qué
   subset, con qué dirección de cambio).

Cada `objetivo_*/README.md` de este sprint declara hipótesis + métrica
de éxito explícitamente. Si un commit toca modelo o training y los
campos no están, el agente `reviewer` bloquea.

## Excel de seguimiento

`Excel_Objetivo_Especifico_B4_Sprint4__EG.xlsx` — a generar después de
la reunión, con tasks asignadas y deadlines.

## Estado vivo

Ver `progress/current.md` en el root del repo.
