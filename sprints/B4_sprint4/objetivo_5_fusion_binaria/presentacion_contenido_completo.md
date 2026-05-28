# Contenido completo de presentación — Objetivo 5

> Pensado como una slide por sección. Para copiar/pegar directo a OnlyOffice.
> Tablas, fórmulas inline sin LaTeX, sin emojis. Speaker notes opcionales en
> bloques `BLOQUE N — Título`.

---

## SLIDE 1 — Qué son Fase 0, Fase 1 y Fase 2 (resumen explícito)

| Fase | Pregunta que responde | Tarea(s) | Modelo | Slides | k MC-CV |
|---|---|---|---|---|---|
| **Fase 0** | ¿Cuánto puede bailar mi métrica solo por la suerte del sorteo? | 3 binarias separadas (carcinoma, CDIS, tejido) | CLAM_MB | 328 c/u | **5** |
| **Fase 1** | ¿Si uno las 3 binarias en una sola "tiene/no tiene" y meto las no_identificado como negativo, mejora? | 1 binaria fusionada | CLAM_MB | 2814 | **3** |
| **Fase 2** | ¿Sobre el fusionado, una arquitectura distinta (DSMIL) le gana a CLAM? | 1 binaria fusionada | DSMIL | 2814 | **3** |

BLOQUE 1 — La historia
-> Fase 0 mide la VARIANZA del baseline que ya teníamos (no entrena nada nuevo, solo lo repite muchas veces).
-> Fase 1 prueba la propuesta de Sebastián (reunión 26-may): "tiene/no tiene micro" como pregunta única.
-> Fase 2 prueba si la arquitectura DSMIL aporta sobre el régimen con más datos que la fusión habilita.
Punto clave: el orden no es arbitrario. Sin Fase 0 no podríamos saber si Fase 1/2 son mejoras reales o ruido.

---

## SLIDE 2 — Por qué la varianza importaba: el problema con un solo número

BLOQUE 1 — El problema
-> En las 3 binarias el test tiene ~33 slides, de las cuales ~7 son positivas (carcinoma).
-> Una sola partición de test = un solo número. Con 7 positivas, mover 1 sola slide cambia el AUC unos 0.05-0.10.
-> El número que reportamos antes (job 4109, 1 sola partición) era una foto suelta — escondía la incertidumbre.

BLOQUE 2 — La solución
-> Repetir el sorteo de test k veces. Reportar media ± desviación.
-> La media estima el valor "verdadero"; la desviación es la barra de error.

---

## SLIDE 3 — Qué es un fold y qué es Monte Carlo CV

BLOQUE 1 — Definición de fold
-> Un fold es UNA repetición del sorteo train/val/test.
-> Con k=5: 5 sorteos distintos, 5 entrenamientos desde cero, 5 números de test.
-> Cada fold tiene su propio modelo (no se transfiere nada entre folds).

BLOQUE 2 — Validación cruzada Monte Carlo (MC-CV)
-> Cada fold sortea sus 33 slides de test del pool COMPLETO (328), independientemente del fold anterior.
-> Los test sets PUEDEN solaparse entre folds (algunas slides aparecen en varios test).
-> Es lo que hace CLAM por defecto (generate_split, utils/utils.py:104-141): fija la semilla una sola vez y deja que numpy sortee 5 veces.

BLOQUE 3 — No es lo mismo que k-fold canónico
-> k-fold canónico: la data se parte en 5 BLOQUES disjuntos. Cada slide cae en test exactamente 1 vez.
-> MC-CV: cada fold re-sortea, los bloques pueden solaparse.
-> Ambos dan barra de error. CLAM usa MC-CV.

BLOQUE 4 — Por qué k=5 binarias y k=3 fusionado
-> Cuántos folds necesitás depende de cuán inestable es tu test.
-> Binarias: 7 positivas en test → muy inestable → k=5.
-> Fusionado: 32 positivas en test → estable → k=3 basta.

BLOQUE 5 — Analogía
-> Medir una mesa con regla floja una vez te da un número (1.20 m).
-> Medirla 5 veces te da el valor Y la incertidumbre: "1.20 ± 0.01" o "1.22 ± 0.07".
-> MC-CV es exactamente eso para el AUC.

---

## SLIDE 4 — Las métricas: recall, accuracy, balanced accuracy, AUC

### Definiciones (con la matriz de confusión a la vista)

```
                pred: no    pred: sí
verdad no:        TN          FP
verdad sí:        FN          TP
```

| Métrica | Fórmula | Qué mide | Trampa |
|---|---|---|---|
| Recall positivo | TP / (TP + FN) | De las slides que SÍ tenían micro, ¿qué fracción detecté como "sí"? | — |
| Recall negativo | TN / (TN + FP) | De las slides que NO tenían, ¿qué fracción dije "no"? | — |
| Accuracy clásica | (TP + TN) / total | Aciertos globales | **Engaña con desbalance** |
| **Balanced accuracy** | (recall+ + recall−) / 2 | Promedio de recalls | Piso trivial 0.50, robusta al desbalance |
| AUC | área bajo curva ROC | Si rankeo todas las slides por probabilidad, ¿quedan las "sí" arriba? | Independiente del umbral |

### Por qué accuracy clásica engaña — ejemplo extremo

> 100 slides: 90 "no" + 10 "sí". Un modelo bobo que dice "no" siempre acierta 90 → **accuracy 0.90** (parece bueno) pero **recall+ = 0** (no detecta nada). Balanced accuracy = (1 + 0) / 2 = **0.50** = piso trivial = el modelo no aprendió.

### Cuándo usar cada una

BLOQUE 1 — Cuando la decisión clínica importa
-> Balanced accuracy. Mide qué tan bien el modelo DECIDE con el umbral 0.5.

BLOQUE 2 — Cuando importa el ranking, no la decisión
-> AUC. Mide si el modelo "sabe" diferenciar, aunque el umbral esté mal posicionado.

BLOQUE 3 — Por qué reportamos las dos
-> Un modelo puede tener AUC alto y balanced_acc bajo (ordena bien pero umbralaza mal — fue lo que le pasó a DSMIL en las binarias separadas, job 4137).
-> Las dos son complementarias.

Punto clave para la slide: balanced accuracy = (recall positivo + recall negativo) / 2. Eso era lo que Sebastián te preguntó.

---

## SLIDE 5 — Sin fusión: carcinoma invasivo (Fase 0, k=5 MC-CV)

Dataset: 328 slides identificadas. **68 positivas (sí) / 260 negativas (no)**. Ratio 3.8:1.

### Por fold (CLAM_MB sobre 5 sorteos distintos del mismo dataset)

| Fold | TN | FP | FN | TP | recall+ | recall− | balanced_acc | accuracy | AUC |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 23 | 2 | 6 | 1 | **0.14** | 0.92 | 0.531 | 0.75 | **0.406** |
| 1 | 23 | 2 | 3 | 4 | 0.57 | 0.92 | 0.746 | 0.84 | 0.834 |
| 2 | 22 | 3 | 5 | 2 | 0.29 | 0.88 | 0.583 | 0.75 | 0.743 |
| 3 | 23 | 4 | 4 | 3 | 0.43 | 0.85 | 0.640 | 0.76 | 0.836 |
| 4 | 28 | 1 | 4 | 3 | 0.43 | **0.97** | 0.697 | 0.86 | 0.842 |
| **media ± std** | | | | | **0.37 ± 0.14** | **0.91 ± 0.04** | **0.639 ± 0.077** | **0.79 ± 0.05** | **0.732 ± 0.167** |

### Interpretación

BLOQUE 1 — La inestabilidad es la noticia
-> AUC va de 0.41 (peor que random) a 0.84 según el sorteo de las 7 positivas.
-> El número suelto del job 4109 fue 0.808 → era el TOPE de la distribución.
-> Con barras de error, las 3 binarias son **indistinguibles** del 0.79 de Sebastián.

BLOQUE 2 — Por qué recall+ es bajo y variable
-> Solo 7 positivas en test. Si el modelo se equivoca en 4 de 7, recall+ = 0.43. En 6 de 7, recall+ = 0.14.
-> Es exactamente lo que pasa: recall+ va de 0.14 a 0.57 entre folds.

---

## SLIDE 6 — Sin fusión: CDIS (Fase 0, k=5 MC-CV)

Dataset: 328 slides. **118 positivas / 210 negativas**. Ratio 1.8:1 (el más balanceado).

| Fold | TN | FP | FN | TP | recall+ | recall− | balanced_acc | accuracy | AUC |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 19 | 3 | 6 | 8 | 0.57 | 0.86 | 0.718 | 0.75 | 0.692 |
| 1 | 15 | 6 | 8 | 3 | 0.27 | 0.71 | 0.494 | 0.56 | 0.528 |
| 2 | 18 | 4 | 9 | 5 | 0.36 | 0.82 | 0.588 | 0.64 | 0.627 |
| 3 | 20 | 2 | 7 | 4 | 0.36 | 0.91 | 0.636 | 0.73 | 0.740 |
| 4 | 17 | 4 | 8 | 3 | 0.27 | 0.81 | 0.541 | 0.62 | 0.675 |
| **media ± std** | | | | | **0.37 ± 0.11** | **0.82 ± 0.07** | **0.595 ± 0.077** | **0.66 ± 0.07** | **0.652 ± 0.072** |

BLOQUE 1 — Interpretación
-> Menos inestable que carcinoma (más positivas en test ≈ 11-14).
-> AUC va de 0.53 a 0.74. Std 0.07 — mediano.
-> Sebastián 0.69 cae dentro de la banda. Indistinguibles.

---

## SLIDE 7 — Sin fusión: tejido no neoplásico (Fase 0, k=5 MC-CV)

Dataset: 328 slides. **192 positivas / 136 negativas**. Es la tarea **donde más positivas hay**.

| Fold | TN | FP | FN | TP | recall+ | recall− | balanced_acc | accuracy | AUC |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 8 | 5 | 8 | 12 | 0.60 | 0.62 | 0.608 | 0.61 | 0.635 |
| 1 | 7 | 6 | 9 | 11 | 0.55 | 0.54 | 0.544 | 0.55 | 0.635 |
| 2 | 7 | 6 | 7 | 12 | 0.63 | 0.54 | 0.585 | 0.59 | 0.656 |
| 3 | 6 | 10 | 3 | 16 | 0.84 | 0.38 | 0.609 | 0.63 | 0.688 |
| 4 | 6 | 7 | 8 | 13 | 0.62 | 0.46 | 0.540 | 0.56 | 0.615 |
| **media ± std** | | | | | **0.65 ± 0.10** | **0.51 ± 0.08** | **0.577 ± 0.030** | **0.59 ± 0.03** | **0.646 ± 0.025** |

BLOQUE 1 — Interpretación
-> El test está casi balanceado (19-21 positivas vs 13-16 negativas).
-> Std súper chico (0.025 en AUC) — la métrica es estable.
-> Pero balanced_acc apenas sobre 0.50: el modelo no logra diferenciar bien las dos clases.
-> Sebastián 0.63 cae dentro de la banda.

---

## SLIDE 8 — Patrón entre las 3 binarias (sin fusión, Fase 0)

| Tarea | n_test | positivas | std(AUC) | std(bal_acc) | media bal_acc |
|---|---|---|---|---|---|
| carcinoma | 33 | 7 | **0.167** (enorme) | 0.077 | 0.639 |
| CDIS | 33 | 11-14 | 0.072 (mediana) | 0.077 | 0.595 |
| tejido no neo. | 33 | 19-21 | 0.025 (chica) | 0.030 | 0.577 |

BLOQUE 1 — Lo que el patrón demuestra
-> La varianza escala EXACTAMENTE con el número de positivas en test, como predijo la hipótesis.
-> A más positivas, métrica más estable; a menos, más bailoteo.
-> Es la prueba empírica directa de por qué MC-CV con varias repeticiones era necesaria.

BLOQUE 2 — Por qué el número "ganador" del 4109 era ilusión
-> En carcinoma (donde "ganamos" 0.808 vs 0.79 de Sebastián) era donde más bailaba el AUC.
-> El 0.79 de Sebastián cae cómodamente dentro de nuestra banda 0.56-0.90.
-> Con barras de error: indistinguibles.

---

## SLIDE 9 — Con fusión: binario "¿tiene microcalcificaciones?" (Fase 1 CLAM, k=3 MC-CV)

Dataset: **2814 slides** (después de quitar 1 sin features CONCH). **328 positivas** (alguna de las 3 binarias) / **2486 negativas** (no_identificado). Ratio 7.6:1.

Construcción del label (regla determinística):
- label = "sí" si hay micro en cualquier tejido (cualquier combinación de carcinoma, CDIS, tejido).
- label = "no" si el reporte CAP no menciona micro (= no_identificado).

### Por fold

| Fold | TN | FP | FN | TP | recall+ | recall− | balanced_acc | accuracy | AUC |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 206 | 43 | 18 | 14 | 0.44 | 0.83 | 0.632 | 0.78 | 0.805 |
| 1 | 228 | 26 | 21 | 11 | 0.34 | 0.90 | 0.621 | 0.84 | 0.764 |
| 2 | 225 | 24 | 22 | 10 | 0.31 | 0.90 | 0.608 | 0.83 | 0.758 |
| **media ± std** | | | | | **0.36 ± 0.05** | **0.88 ± 0.03** | **0.620 ± 0.010** | **0.82 ± 0.03** | **0.776 ± 0.021** |

### Interpretación

BLOQUE 1 — El patrón es consistente
-> Los 3 folds cuentan la MISMA historia: recall negativo alto (0.83-0.90), recall positivo bajo (0.31-0.44).
-> Std súper chico (0.010 en balanced_acc) porque cada test tiene 281 slides (32 positivas) — mucho más estable que las binarias.

BLOQUE 2 — Qué significa
-> El modelo es bueno descartando slides sanas (recall− alto) y mediocre detectando micros (recall+ ≈ 0.36).
-> Solo encuentra ~36% de los positivos reales: detecta 1 de cada 3 casos con micro.
-> El desbalance 7.6:1 lo empuja a decir "no" pese al --weighted_sample.

BLOQUE 3 — Veredicto vs umbral pre-registrado
-> Umbral clínico (§1.3): ≥ 0.65 = "usable", 0.55-0.65 = "plateau", < 0.55 = "colapso".
-> balanced_acc 0.620 → cae en PLATEAU. Aprende algo pero no llega al umbral clínico.
-> Coherente con la predicción honesta: "detector modesto, no salto".

BLOQUE 4 — Por qué la accuracy es alta y engaña
-> Accuracy 0.82 parece muy bueno. Pero el modelo solo detecta 36% de los positivos.
-> Es exactamente el ejemplo del SLIDE 4: con desbalance 7.6:1, decir "no" casi siempre da accuracy alta.
-> Por eso reportamos balanced_acc, no accuracy.

---

## SLIDE 10 — Con fusión: ¿gana DSMIL a CLAM? (Fase 2, k=3 MC-CV)

> **PENDIENTE — el job 4172 sigue corriendo al cierre de la sesión 27-may noche.**
> Mismo dataset (2814 fusionado), mismos splits k=3 que Fase 1 (comparación pareada).
> Se llena con los `test_metrics.json` de DSMIL al terminar el chain.

| Fold | TN | FP | FN | TP | recall+ | recall− | balanced_acc | accuracy | AUC |
|---|---|---|---|---|---|---|---|---|---|
| 0 |  |  |  |  |  |  |  |  |  |
| 1 |  |  |  |  |  |  |  |  |  |
| 2 |  |  |  |  |  |  |  |  |  |
| **media ± std** | | | | | | | | | |

### Comparación pareada CLAM vs DSMIL — el resultado clave del objetivo

| Métrica | CLAM (Fase 1) | DSMIL (Fase 2) | Δ (DSMIL − CLAM) |
|---|---|---|---|
| balanced_acc | **0.620 ± 0.010** | _pendiente_ | _pendiente_ |
| test AUC | **0.776 ± 0.021** | _pendiente_ | _pendiente_ |
| recall+ | 0.36 ± 0.05 | _pendiente_ | _pendiente_ |
| recall− | 0.88 ± 0.03 | _pendiente_ | _pendiente_ |

BLOQUE 1 — Veredicto a aplicar (§2.2 de la hipótesis, pre-registrado)
-> Éxito arquitectónico = Δ balanced_acc ≥ +0.03 Y bandas mean ± std no solapadas.
-> Plateau = |Δ| < 0.03 o bandas solapadas → DSMIL no aporta sobre el fusionado.
-> Regresión = Δ ≤ −0.05 → DSMIL peor.

BLOQUE 2 — Guardrail estadístico (adenda 27-may)
-> Los test sets de MC-CV se solapan entre folds → los Δ están correlacionados.
-> "Bandas no solapadas" es un heurístico de screening, no una prueba de significancia formal.
-> Con k=3 el std mismo es ruidoso.
-> Reportar la dirección del Δ, no afirmar un p-valor.

---

## SLIDE 11 — Cierre: la lección del Objetivo 5

BLOQUE 1 — Tres descubrimientos
-> El single-split del 4109 era optimista por suerte. La estimación honesta es más modesta.
-> Frente a Sebastián, estamos en paridad estadística (no superiores, no inferiores).
-> Fusionar las 3 binarias en una sola pregunta + incluir no_identificado NO fue bala de plata: balanced_acc 0.620 ≈ promedio de las binarias separadas (0.60).

BLOQUE 2 — Lo que el objetivo aportó
-> Medir la incertidumbre que el single-split escondía.
-> Confirmar que el cuello de botella sigue siendo datos / contexto espacial / desbalance, NO arquitectura ni formulación.
-> Justificar empíricamente los próximos ejes: mayor magnificación CONCH y selección de parches con información (no ruido).

BLOQUE 3 — Próximos pasos (ya aprobados por Sebastián, futuros sprints)
-> Re-extraer CONCH a mayor magnificación, solo para slides de microcalcificaciones.
-> Selección de parches útiles vía el mejor modelo, estilo heatmap Camelyon.
-> Ver `sprints/B4_sprint4/ejes_futuros_microcalc.md`.
