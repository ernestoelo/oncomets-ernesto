# Entregable 4 — ≥2 propuestas de mejora algorítmica

**Deadline**: 6 mayo 2026. **Estudio teórico, sin implementación en este sprint.**

## Tareas

1. Documentar y justificar técnicamente la propuesta de **aumentar top-B /
   bottom-B**, analizando trade-off sesgo-varianza en la supervisión de la
   loss. Esta propuesta ya fue planteada en reunión.
2. Investigar al menos una estrategia complementaria fundamentada en
   literatura de MIL / weakly-supervised learning.

## Candidatas para la segunda propuesta (en memoria)

- **Adaptive pseudo-label selection**: en lugar de top-B/bottom-B fijo,
  umbralización adaptativa sobre los attention scores.
- **Fragility de mutual exclusivity**: cuestionar `subtyping=True` para la
  taxonomía de 10 clases — si dos clases pueden coexistir en el mismo WSI,
  la asunción se rompe. Pregunta abierta para Sebastián.
- **Asimetría 9:1 bajo subtyping**: mitigar el dominio de las ramas
  out-of-class en el gradiente de `L_instance` (re-pesado, gradient
  scaling, etc.).
- **Soft pseudo-labels**: pasar de hard top-B/bottom-B a una distribución
  ponderada por attention.
- **Calibración del clasificador instance-level**: temperature scaling,
  label smoothing.

## Output esperado

- `propuesta_topB.md` — fundamento teórico, conexión al código actual,
  trade-offs esperados.
- `propuesta_complementaria.md` — misma estructura, basada en una de las
  candidatas o en una nueva.

Cada propuesta debe incluir:
- Motivación (qué problema soluciona)
- Formulación matemática
- Cambios concretos al código actual (referencia a líneas de
  `model_clam.py` / `core_utils.py`)
- Trade-offs esperados (computacional, estadístico, de gradiente)
- Bibliografía relevante
