# Alternativas consideradas — módulo MIL

> El Objetivo 3 propone DSMIL, pero **DSMIL no es la única opción** y la
> decisión queda abierta a la reunión (decisión #6 del sprint). Este
> documento deja por escrito qué otros aggregators se evaluaron, para que
> la reunión decida con el campo completo a la vista y no sobre una sola
> propuesta.

## TransMIL (Shao et al., NeurIPS 2021)

*TransMIL: Transformer based Correlated Multiple Instance Learning for
Whole Slide Image Classification* (<https://arxiv.org/abs/2106.00908>).
Es alternativa porque ataca exactamente la misma carencia que motiva el
Objetivo 3: el pooling lineal de CLAM no modela correlaciones entre
parches. TransMIL las modela con **self-attention completa** sobre todos
los parches del bag, lo que captura relaciones de orden superior que el
dual-stream de DSMIL (centrado solo en el parche crítico) no alcanza.
**Riesgo**: la self-attention es cuadrática en N. TransMIL la aproxima
con **Nyström-attention**, pero aun así, con WSIs grandes
(N > 50.000 parches, frecuentes en este dataset) el consumo de memoria
en la única RTX A6000 (49 GB) es una incógnita que habría que medir
antes de comprometerse. DSMIL es lineal en N y no tiene ese riesgo.

## HIPT (Chen et al., CVPR 2022)

*Scaling Vision Transformers to Gigapixel Images via Hierarchical
Self-Supervised Learning* (<https://arxiv.org/abs/2206.02647>). HIPT es
**jerárquico**: agrega parches en varios niveles de resolución
(parche → región → slide) con Transformers anidados, en vez de tratar la
WSI como un bag plano. Conceptualmente es el cambio más potente —
respeta la estructura espacial multi-escala de la patología— pero también
el **más invasivo**: HIPT asume su propio pipeline de features
auto-supervisadas (DINO sobre [256×256] y [4096×4096]); enchufarlo sobre
las features CONCH ya extraídas no es un swap de un bloque, es rehacer la
extracción. Queda como **dirección futura**, fuera del alcance de un
sprint con dataset y splits aún por confirmar.

## Aumentar `B` (top-B / bottom-B) — no es módulo nuevo

Subir el hiperparámetro `--B` del instance classifier path se consideró,
pero **no es un módulo MIL alternativo**: es una ablation de un
hiperparámetro del CLAM existente. Ya está cubierta como
**Objetivo 2** del sprint ([`../objetivo_2_ablation_B/`](../objetivo_2_ablation_B/),
ablation `B=8` vs `B=16`). Se menciona aquí solo para dejar claro que
Objetivo 2 y Objetivo 3 atacan cosas distintas: Objetivo 2 ajusta el
**sampling** del modelo actual; Objetivo 3 cambia la **arquitectura** de
agregación. No se solapan.

## Por qué se propuso DSMIL primero

Entre las alternativas, DSMIL se propuso primero por una combinación de
tres razones, en este orden:

1. **Mínimo cambio de pipeline.** DSMIL reemplaza solo la rama de
   pooling. Conserva features CONCH, bag classifier, instance branch y
   CSVs → la única variable experimental es el aggregator, y el resultado
   es directamente comparable con el baseline (Objetivo 1) y la ablation
   de `B` (Objetivo 2). TransMIL también es un swap de bloque, pero HIPT
   exige rehacer la extracción de features.
2. **Sin riesgo de memoria.** DSMIL es lineal en N. TransMIL, aun con
   Nyström, deja una incógnita de memoria sobre la GPU única del servidor.
3. **Argumento focal directo.** El dual-stream de DSMIL (atención
   relativa al parche crítico) mapea de forma limpia y explicable a la
   hipótesis clínica del sprint: las tareas peor evaluadas
   (MicroCalcificaciones, C.D.I. Necrosis) son **focales**. Es el
   argumento más fácil de defender ante Sebastián y Eduardo bajo la
   regla 9 ("argumento antes de código").

Esto **no cierra** la decisión: si la reunión prioriza modelar
correlaciones de orden superior por sobre el costo de integración,
TransMIL es la opción razonable. HIPT queda para un sprint futuro con
presupuesto para tocar la extracción de features.
