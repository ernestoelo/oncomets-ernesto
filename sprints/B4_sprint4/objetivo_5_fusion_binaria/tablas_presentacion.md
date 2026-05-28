# Tablas para la presentación — slides por entrenamiento + validación Monte Carlo + comparativa

> Para copiar/pegar a la presentación. Conteos = verdad de campo (CSVs/splits
> reales, 27-may). **Fase 0 ya recolectada** (job 4170); Fase 1/2 pendientes.

> **Nota de rótulo (importante).** Lo que en archivos/scripts llamamos "k-fold"
> es técnicamente **validación cruzada Monte Carlo (MC-CV)**: k particiones
> aleatorias con test que **pueden solaparse** — el **MISMO método que usa CLAM**
> (`generate_split` fija la semilla una vez y sortea val/test del pool completo
> en cada repetición). NO es k-fold canónico (bloques disjuntos). El nombre
> "k-fold" quedó en los nombres de archivo como identificador histórico; el
> método y los resultados son válidos. En la presentación usar **"Monte Carlo CV"**.

---

## A. ¿Para qué hicimos validación cruzada Monte Carlo (MC-CV)? (explicación)

**El problema.** Un entrenamiento normal parte los datos en train / validación /
test UNA vez. El test queda con pocas slides (ej. en las binarias de
microcalcificaciones: ~33 slides, de las cuales **solo 7 son positivas**). El
AUC que sale de ahí es **un solo número, y depende de la suerte del sorteo**: si
una sola slide positiva cae en test en vez de train, el AUC se mueve ~0.05. Con
7 positivas, eso es enorme.

**Consecuencia — y lo CONFIRMAMOS con datos (Fase 0).** El 0.808 que reportamos
en carcinoma (job 4109, 1 sorteo) era un **sorteo afortunado**: al repetir 5
veces, los AUC fueron [0.41, 0.83, 0.74, 0.84, 0.84] → **media 0.732 ± 0.167**.
Un fold dio 0.41 (peor que el azar). La "ventaja sobre el 0.79 de Sebastián"
**no existía** — era ruido del sorteo. Sin barras de error, comparar números
sueltos engaña.

**Qué hacemos (MC-CV).** En vez de un solo sorteo, hacemos **k particiones
aleatorias distintas** de test (k=5 en las binarias). Entrenamos k veces, cada
una con un test diferente, y obtenemos **k números**. Reportamos:

```
        AUC = media ± desviación estándar   (sobre los k folds)
```

La **media** es una estimación mucho más estable; la **desviación estándar (±)**
nos dice *cuánto podemos confiar* en ese número. Es la "barra de error".

**Analogía.** Medir una mesa con una regla floja una sola vez te da un número
dudoso. Medirla 5 veces y reportar "1.20 m ± 0.01" te dice el valor Y cuánta
incertidumbre tiene. MC-CV es exactamente eso para el AUC.

**Por qué no alcanzaba con cambiar la semilla.** La semilla (`seed`) cambia cómo
se inicializan los pesos del modelo, pero **NO cambia qué slides caen en test**
(eso lo fija el archivo de split). Entonces variar la semilla daría barras de
error **falsamente chicas** — mediría el ruido del modelo, no el ruido del
sorteo de test, que es el grande. Por eso la palanca correcta es **re-sortear
el test** (MC-CV), no multi-semilla.

**Por qué k=5 en las binarias y k=3 en el fusionado.** La cantidad de folds que
hace falta depende de cuán ruidoso es el test:
- Binarias: ~7 positivas en test → muy ruidoso → **k=5** (más sorteos).
- Fusionado: ~33 positivas en test → ya estable → **k=3** basta (y ahorra
  cómputo en una GPU compartida).

Punto clave para la slide: *la validación repetida (MC-CV) no mejora el modelo;
mejora nuestra **confianza en el número**. Sin barras de error, "0.808 vs 0.79"
no significa nada — y de hecho ese 0.808 resultó ser 0.732 ± 0.167 al repetir.*

---

## B. Slides por entrenamiento (tablas para copiar)

### B.1 — Diagnóstico: 8 clases (jobs 4098 / 4099)

| Experimento | Modelo | Slides (train / val / test) | Total | Clases | test_auc | balanced_acc |
|---|---|---|---|---|---|---|
| Baseline B=8 (4098) | CLAM_MB | 2436 / 319 / 315 | 3072 | 8 | 0.81 (ruidoso) | 0.31 |
| Ablación B=16 (4099) | CLAM_MB | 2436 / 319 / 315 | 3072 | 8 | 0.82 | 0.24 |

> Las 8 clases = combinaciones de 3 tejidos + `no_identificado`. 4 clases con
> 1 sola muestra en val/test → régimen de evaluación roto (de ahí el diagnóstico
> que motivó reformular).

### B.2 — Reformulación en 3 binarias (composición del dataset, hoy 328 slides)

| Tarea binaria | Positivos (sí) | Negativos (no) | Total | Ratio neg:pos |
|---|---|---|---|---|
| micro en carcinoma invasivo | 68 | 260 | 328 | 3.8 : 1 |
| micro en CDIS | 118 | 210 | 328 | 1.8 : 1 |
| micro en tejido no neoplásico | 192 | 136 | 328 | 0.7 : 1 |

> `no_identificado` excluido. (Jobs 4109/4137 corrieron sobre 333 — drift menor
> del CSV de Sebastián; misma tarea.)

### B.3 — Binario fusionado "¿tiene microcalcificaciones?" (Fase 1/2)

| Clase | Slides | Qué incluye |
|---|---|---|
| sí (positivo) | 328 | micro en CUALQUIER tejido (une las 3 binarias) |
| no (negativo) | 2486 | `no_identificado` (CAP no menciona micro) |
| **Total** | **2814** | ratio 7.6 : 1 |

> Excluida 1 slide sin features CONCH (histai_1132).

---

## C. Tabla comparativa maestra — todos los entrenamientos

> Resultados conocidos rellenados; **celdas vacías = pendientes** del chain en
> curso. Métrica decisiva = **balanced accuracy** (honesta con el desbalance);
> test_auc se reporta pero a n chico es ruidoso.

| # | Job | Experimento | Modelo | Formulación | Slides | k | Estado | test_auc | balanced_acc |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 4098 | Baseline | CLAM_MB | 8 clases | 3072 | 1 split | ✅ | 0.81 | 0.31 |
| 2 | 4099 | Ablación B=16 | CLAM_MB | 8 clases | 3072 | 1 split | ✅ | 0.82 | 0.24 |
| 3 | 4109 | Reformulación — carcinoma inv. | CLAM_MB | binaria | 333 | 1 split | ✅ | 0.808 | 0.78 |
| 4 | 4109 | Reformulación — CDIS | CLAM_MB | binaria | 333 | 1 split | ✅ | 0.678 | 0.59 |
| 5 | 4109 | Reformulación — tejido no neo. | CLAM_MB | binaria | 333 | 1 split | ✅ | 0.658 | 0.58 |
| 6 | 4137 | DSMIL — carcinoma inv. | DSMIL | binaria | 333 | 1 split | ✅ | 0.824 | (fracaso) |
| 7 | 4137 | DSMIL — CDIS | DSMIL | binaria | 333 | 1 split | ✅ | 0.570 | (fracaso) |
| 8 | 4137 | DSMIL — tejido no neo. | DSMIL | binaria | 333 | 1 split | ✅ | 0.577 | (fracaso) |
| 9 | 4170 | Fase 0 varianza — carcinoma | CLAM_MB | binaria | 328 | **5** | ✅ | **0.732 ± 0.167** | **0.639 ± 0.077** |
| 10 | 4170 | Fase 0 varianza — CDIS | CLAM_MB | binaria | 328 | **5** | ✅ | **0.652 ± 0.072** | **0.595 ± 0.077** |
| 11 | 4170 | Fase 0 varianza — tejido | CLAM_MB | binaria | 328 | **5** | ✅ | **0.646 ± 0.025** | **0.577 ± 0.030** |
| 12 | 4171 | Fase 1 — fusionado | CLAM_MB | fusionada | 2814 | **3** | ✅ | **0.776 ± 0.021** | **0.620 ± 0.010** (plateau) |
| 13 | 4172 | Fase 2 — fusionado | DSMIL | fusionada | 2814 | **3** | ✅ | **0.756 ± 0.024** | **0.661 ± 0.046** (ambigua) |
| 14 | 4179 | **Anexo** — DSMIL × binarias — carcinoma | DSMIL | binaria | 328 | **5** | ✅ | **0.722 ± 0.098** | **0.617 ± 0.117** (NULL) |
| 15 | 4179 | **Anexo** — DSMIL × binarias — CDIS | DSMIL | binaria | 328 | **5** | ✅ | **0.619 ± 0.099** | **0.543 ± 0.077** (regr. leve) |
| 16 | 4179 | **Anexo** — DSMIL × binarias — tejido | DSMIL | binaria | 328 | **5** | ✅ | **0.682 ± 0.042** | **0.599 ± 0.029** (null/ambigua) |

> ✅ hecho · ⏳ en cola/corriendo · `±` = media ± desviación sobre las k
> repeticiones de MC-CV. Filas 3-5 (4109) = **un solo sorteo** → optimistas
> (ver filas 9-11, la estimación honesta con barras de error).
> Filas 6-8 (4137) = **un solo sorteo** DSMIL binarias (parecía "fracaso" en
> bal_acc) → reemplazadas en honestidad por filas 14-16 con MC-CV (anexo,
> ver §C.2 abajo).

### C.1 — Comparativa contra Sebastián (test_auc) — single-split vs MC-CV honesto

| Tarea | 4109 (1 sorteo) | **Fase 0 MC-CV (honesto)** | Sebastián (1 sorteo) | ¿distinguibles? |
|---|---|---|---|---|
| micro carcinoma invasivo | 0.808 | **0.732 ± 0.167** | 0.79 | NO — Sebastián cae dentro de nuestra banda |
| micro CDIS | 0.678 | **0.652 ± 0.072** | 0.69 | NO — se solapan |
| micro tejido no neoplásico | 0.658 | **0.646 ± 0.025** | 0.63 | NO — se solapan |

> **Mensaje honesto para la slide:** el "empatamos/ganamos a Sebastián" del
> single-split NO se sostiene con barras de error — pero tampoco perdemos: con
> MC-CV las tres tareas son **estadísticamente indistinguibles** de Sebastián
> (su número es también 1 sorteo, con la misma varianza). La contribución real
> es **medir la incertidumbre**, que el single-split escondía. Carcinoma es el
> caso de manual: 0.808 (suerte) → 0.732 ± 0.167 (realidad).

### C.2 — Anexo: comparativa pareada CLAM vs DSMIL × 3 binarias × MC-CV k=5 (job 4179)

Cierra simétricamente el cuadro arquitectónico. Mismos splits que Fase 0
(paired por construcción).

| Tarea | CLAM bal (Fase 0) | DSMIL bal (Anexo) | **Δ bal pareado** | CLAM auc | DSMIL auc | **Δ auc pareado** | Veredicto pre-registrado |
|---|---|---|---|---|---|---|---|
| carcinoma invasivo | 0.639 ± 0.077 | 0.617 ± 0.117 | **−0.023 ± 0.071** | 0.732 ± 0.167 | 0.722 ± 0.098 | −0.011 ± 0.080 | **NULL ✅** |
| CDIS | 0.595 ± 0.077 | 0.543 ± 0.077 | **−0.053 ± 0.026** | 0.652 ± 0.072 | 0.619 ± 0.099 | −0.034 ± 0.081 | **Regresión leve ⚠️** |
| tejido no neoplásico | 0.577 ± 0.030 | 0.599 ± 0.029 | **+0.021 ± 0.051** | 0.646 ± 0.025 | 0.682 ± 0.042 | +0.036 ± 0.048 | NULL / ambigua |

**Δ pareado por fold** (fila por tejido = signo del Δ en bal_acc por fold):

| Tarea | f0 | f1 | f2 | f3 | f4 | Patrón |
|---|---|---|---|---|---|---|
| carcinoma | − | − | − | + | + | mixto |
| CDIS | − | − | − | − | − | **5/5 negativo** (no es ruido) |
| tejido | − | + | + | + | + | 4/5 positivo |

> **Mensaje honesto para la slide:** DSMIL evaluado en TODOS los regímenes
> (binarias + fusionado, ambos con MC-CV). En binarias: **2 de 3 tareas
> empate estadístico** (carcinoma, tejido) → confirma que el cuello es datos
> / contexto / desbalance, no arquitectura. **CDIS regresión leve consistente**
> en los 5 folds (no es ruido) → sostiene el "fracaso" del 4137 con barras de
> error; abre pregunta morfológica (atención dual vs gated absoluta) para
> futuro, no decisión de este sprint. Lectura honesta: la arquitectura sola
> no es la palanca.

---

## D. Notas para llenar resultados

- **Fila 9-11 (Fase 0):** ✅ LLENO (job 4170, `results/obj5_varianza_<tejido>/`).
- **Fila 12 (Fase 1, CLAM fusionado):** ✅ LLENO (job 4171,
  `results/obj5_fase1_clam_fusionado/clam_presencia_f*_s1/test_metrics.json`).
- **Fila 13 (Fase 2, DSMIL fusionado):** ✅ LLENO (job 4172,
  `results/obj5_fase2_dsmil_fusionado/dsmil_presencia_f*_s1/test_metrics.json`).
- **Filas 14-16 (Anexo, DSMIL × binarias × k=5):** ✅ LLENO (job 4179,
  `results/obj5_anexo_dsmil_binarias_<tejido>/dsmil_<tejido>_f*_*_s1/test_metrics.json`).

### La comparación clave del objetivo — lectura honesta (§2.2)

**¿DSMIL (fila 13) supera a CLAM (fila 12) sobre el fusionado?**

| Métrica | CLAM (Fase 1) | DSMIL (Fase 2) | Δ pareado (DSMIL − CLAM) |
|---|---|---|---|
| balanced_acc | **0.620 ± 0.010** | **0.661 ± 0.046** | **+0.040 ± 0.038** |
| test_auc | **0.776 ± 0.021** | **0.756 ± 0.024** | **−0.020 ± 0.019** |

- **DSMIL cruza el umbral 0.65** (umbral §2.2 "supera") por +0.011 — dentro
  de la barra de error.
- Δ balanced_acc **positivo en los 3 folds** (+0.094, +0.009, +0.018) — signo
  consistente, mecanismo plausible.
- Pero las **bandas mean ± std SE SOLAPAN** (CLAM [0.610, 0.630] vs DSMIL
  [0.615, 0.707]) → el heurístico de screening §2.2 NO se cumple.
- **AUC retrocede** (−0.020), no acompaña.
- DSMIL recupera más positivos (recall+ ≈ 0.49 vs CLAM 0.36) pero con más FP
  → es **menos conservador**, no necesariamente mejor discriminador.

**Veredicto: banda AMBIGUA**. No "supera" en el sentido fuerte de §2.2; tampoco
"plateau" estricto (signo consistente). No sobre-vender en la slide.

> **Matiz estadístico (no sobre-afirmar).** Los test de MC-CV **se solapan**
> entre repeticiones → los AUC están correlacionados → "bandas no solapadas"
> es un **heurístico de screening**, NO una prueba de significancia formal.
> Con k=3 el `std` mismo es ruidoso. La comparación CLAM-vs-DSMIL es **pareada**
> (mismos splits) → eso ayuda al Δ. Reportar con esa cautela.
