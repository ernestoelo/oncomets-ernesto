# Resultados — Objetivo 5

> Se llena por fase. **Fase 0 COMPLETA** (job 4170, 27-may). Fase 1 (4171)
> corriendo, Fase 2 (4172) en cola. Métricas = verdad de campo desde
> `results/obj5_varianza_*/.../summary.csv` y `split_*_results.pkl`.

---

## FASE 0 — Caracterización de varianza (CLAM, 3 binarias, MC-CV k=5)

**Setup**: CLAM_MB, args bendecidos, 328 slides/tarea, 5 repeticiones de
validación cruzada Monte Carlo (test_frac=0.1, semilla 1). Job 4170.

> "k-fold" en nombres de archivo = **Monte Carlo CV** (test solapados), el mismo
> `generate_split` de CLAM (`utils/utils.py:104-141`). No es k-fold canónico.

### Resultados (media ± std sobre 5 repeticiones)

| Tarea | test_auc por fold | **test_auc** | **balanced_acc** | 4109 (1 sorteo) |
|---|---|---|---|---|
| carcinoma invasivo | 0.41 / 0.83 / 0.74 / 0.84 / 0.84 | **0.732 ± 0.167** | **0.639 ± 0.077** | auc 0.808 · bal 0.78 |
| CDIS | 0.69 / 0.53 / 0.63 / 0.74 / 0.68 | **0.652 ± 0.072** | **0.595 ± 0.077** | auc 0.678 · bal 0.59 |
| tejido no neoplásico | 0.64 / 0.64 / 0.66 / 0.69 / 0.62 | **0.646 ± 0.025** | **0.577 ± 0.030** | auc 0.658 · bal 0.58 |

### Veredicto (regla §0.2)

**std(test_auc) > 0.05 en carcinoma (0.167) y CDIS (0.072)** → **varianza
confirmada grande**. Decisión pre-registrada aplicada: toda comparación
downstream (Fase 1/2, Sebastián) se evalúa **solo con MC-CV mean±std**; ningún
Δ de una sola partición cuenta como evidencia.

### Hallazgos

1. **El single-split del 4109 era optimista por suerte de sorteo.** Carcinoma:
   el 0.808 (bal_acc 0.78) que celebramos estaba en el TOPE de la distribución;
   un fold dio test_auc **0.406** (peor que el azar). Estimación honesta:
   **0.732 ± 0.167** / bal_acc **0.639 ± 0.077**. La "ventaja sobre Sebastián"
   en carcinoma **no se sostiene**.
2. **El std escala con los positivos en test, como predijo la hipótesis §0.1.**
   carcinoma (7 pos/test) → ±0.167; CDIS (11-14 pos) → ±0.072; tejido (20 pos)
   → ±0.025. Prueba empírica directa de por qué el método hacía falta.
3. **Frente a Sebastián: indistinguibles, no superiores.** Su número (1 sorteo,
   misma varianza) cae dentro de nuestras bandas en las 3 tareas. La
   contribución del objetivo NO es "ganarle" sino **medir la incertidumbre que
   el single-split escondía**.
4. **balanced_acc honesta**: las 3 tareas quedan en 0.58-0.64 — modestas,
   apenas sobre el piso 0.50. Coherente con el diagnóstico de que el cuello es
   **datos** (328 slides), no formulación ni arquitectura.

### Para la presentación

- Tabla y gráfico de barras con error: `tablas_presentacion.md` §C / §C.1.
- Mensaje: *medir la incertidumbre cambió la lectura* — el single-split decía
  "ganamos en carcinoma"; MC-CV dice "estadísticamente iguales, con barra de
  error grande donde hay pocas positivas".

---

## FASE 1 — CLAM sobre el fusionado (PENDIENTE, job 4171 corriendo)

(se llena al terminar — `results/obj5_fase1_clam_fusionado/clam_presencia_f*_s1/test_metrics.json`)

## FASE 2 — DSMIL sobre el fusionado (PENDIENTE, job 4172 en cola)

(corre solo si el gate de colapso pasa; comparación pareada CLAM vs DSMIL,
ver hipotesis.md §2.2 + adenda estadística)
