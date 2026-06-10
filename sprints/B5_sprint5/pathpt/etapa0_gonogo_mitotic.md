# Etapa 0 — Go/No-Go de PathPT-CONCH en TASA MITÓTICA (pre-registración regla 9)

> Misma metodología que [etapa0_gonogo_necrosis.md](etapa0_gonogo_necrosis.md) (mecanismo,
> reconstrucción del espacio contrastivo, política de eval). Acá solo lo específico de mitotic.
> Script: `scripts/zeroshot_gonogo.py --task mitotic`.

## 1. Datos (verdad de campo, read-only)
`dataset_grado_histologico_tasa_mitotica_label.csv` — 1870 slides:
`no_identificado` 693 · `score_1` 636 · `score_2` 287 · `score_3` 254.
- **Excluir `no_identificado`** (mal definido a nivel tile). Subset = **score_1/2/3 (1177)**.
- **3 clases ordinales** (Nottingham mitotic score). Trivial balanced_acc = 1/3 ≈ 0.333.

## 2. Hipótesis (regla 9)
- **H1:** los prompts de "high mitotic count" puntúan más alto en `score_3` que en `score_1`
  (gradiente ordinal) → CONCH groundea densidad mitótica zero-shot.
- **H0:** sin separación (macro-OVR AUC ≈ 0.5, bal_acc ≈ 0.33).
- **Riesgo a priori MAYOR que necrosis:** contar mitosis es **sutil** (figuras pequeñas,
  dependientes de aumento) → es plausible que el grounding zero-shot de CONCH sea débil acá.
  Eso **en sí es un hallazgo informativo** (acota dónde PathPT-CONCH puede y no puede).

## 3. Métrica (política B5) y dirección
- **macro-OVR AUC** (primaria, threshold-free) + balanced_acc(argmax) + matriz de confusión + n.
- **Dirección esperada si H1:** AUC > 0.5 con orden score_1<score_2<score_3 en el score.
- **Regla de decisión (interpretada, regla 9.a):** macro-OVR AUC ≳0.60–0.65 → señal usable
  (lean-GO); ≈0.5 → NO-GO barato (CONCH no cuenta mitosis zero-shot); intermedio → iterar prompts.
  (Mismo espíritu que necrosis: es un FLOOR; PathPT añade prompt-tuning + contexto espacial.)

## 4. Resultado (10-jun-2026) — 1177 slides (score_1 636 / score_2 287 / score_3 254)

`scripts/zeroshot_gonogo.py --task mitotic` (CPU, 136s). Salida en
`results/pathpt_gonogo/mitotic_v1_zeroshot_metrics.json`.

| top-j | macro-OVR AUC | bal_acc @ argmax |
|---|---|---|
| 5 | 0.647 | 0.460 |
| 10 | **0.648** | 0.455 |
| 50 | 0.647 | 0.440 |

**Lectura:** macro-OVR AUC ~0.648 (trivial 0.5), bal_acc@argmax ~0.46 (trivial 0.333) →
**señal real, lean-GO**, comparable a necrosis (~0.67) pese a ser 3 clases ordinales y una
tarea más sutil (contar mitosis). H0 (no grounding) se descarta. Mismo patrón: es un **FLOOR**
zero-shot; PathPT añadiría prompt-tuning + contexto espacial. Prompts a iterar con criterio
clínico antes de la decisión GO→Etapa 1 (GPU + reviewer).

*Pre-registración (§1–3) escrita ANTES de correr. Resultado (§4) = corrida real, CPU, sin entrenar (regla 5/9).*
