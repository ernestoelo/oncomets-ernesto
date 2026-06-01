# Guión de montaje — Slides Obj 5 + Anexo (OnlyOffice)

> Entregable copy-paste para armar el deck en OnlyOffice (branding Environ lo
> pone Ernesto). Para cada slide: **(a)** qué PNG insertar, **(b)** bullets del
> cuerpo, **(c)** speaker notes (formato B2, pegar en el panel de notas).
>
> **Base de assets** (todo bajo este folder):
> `sprints/B4_sprint4/objetivo_5_fusion_binaria/figuras/`
> - Tablas / matrices de fold: `figuras/slide_assets/T##_*.png` y `M##_*.png`
> - Figuras de barras / matrices agregadas: `figuras/*.png`
>
> Convención de assets: **PRIMARIO** = el que va sí o sí en la slide; **opcional**
> = backup o para un apéndice si querés más detalle. No metas 6 PNG en una slide.
>
> Tono (pre-acordado, NO sobre-vender): *"el aporte real del Obj 5 fue medir la
> incertidumbre que el single-split escondía"*, NO *"ganamos 2 métricas vs
> Sebastián"*. Ver Slide 13.
>
> **Nota de assets (1-jun):** las tablas `slide_assets/T*.png` se regeneraron
> hoy — se arregló un bug de render (texto de headers/celdas que se solapaba en
> T04/T05/T10/T12/T13). Usá la versión actual del folder.

---

## SLIDE 1 — Qué son Fase 0, Fase 1, Fase 2 y Anexo

**PNG a insertar**
- PRIMARIO: `figuras/slide_assets/T04_resumen_fases.png` (la tabla Fase/Pregunta/Tarea/Modelo/Slides/k/Job).
- Opcional (2ª slide o apéndice): `figuras/slide_assets/T03_splits_por_fase.png` (train/val/test por fase).

**Bullets del cuerpo** (si querés texto además de la tabla)
- 4 experimentos, una pregunta cada uno; el orden NO es arbitrario.
- Fase 0 mide la varianza del baseline; Fase 1/2 prueban fusión y arquitectura; el Anexo cierra el cuadro.

**Speaker notes**
```
BLOQUE 1 — La historia
-> Fase 0 mide la VARIANZA del baseline que ya teníamos (no entrena nada nuevo, solo lo repite muchas veces).
-> Fase 1 prueba la propuesta de Sebastián (reunión 26-may): "tiene/no tiene micro" como pregunta única.
-> Fase 2 prueba si la arquitectura DSMIL aporta sobre el régimen con más datos que la fusión habilita.
-> Anexo cierra simétricamente el cuadro: aplica MC-CV a DSMIL x binarias (mismos splits que Fase 0) para juzgar el 4137 con barras de error.
Punto clave: sin Fase 0 no sabríamos si Fase 1/2 son mejoras reales o ruido. El anexo aplica esa misma vara a DSMIL.
```

---

## SLIDE 2 — Por qué la varianza importaba: el problema con un solo número

**PNG a insertar**
- PRIMARIO: `figuras/fig1a_fase0_auc.png` (barras MC-CV con la X del single-split 4109 por encima → "el single-split engañaba; con barra de error son indistinguibles"). Ilustra de un vistazo el mensaje de la slide.
- Opcional: dejar la slide solo-texto si preferís reservar fig1a para la Slide 8.

**Bullets del cuerpo**
- En las 3 binarias el test tiene ~33 slides, ~7 positivas (carcinoma).
- Una sola partición = un solo número; mover 1 slide cambia el AUC 0.05–0.10.
- El número del 4109 (1 sola partición) escondía la incertidumbre. Solución: repetir el sorteo k veces, reportar media ± desviación.

**Speaker notes**
```
BLOQUE 1 — El problema
-> En las 3 binarias el test tiene ~33 slides, de las cuales ~7 son positivas (carcinoma).
-> Una sola partición de test = un solo número. Con 7 positivas, mover 1 sola slide cambia el AUC unos 0.05-0.10.
-> El número que reportamos antes (job 4109, 1 sola partición) era una foto suelta: escondía la incertidumbre.

BLOQUE 2 — La solución
-> Repetir el sorteo de test k veces. Reportar media ± desviación.
-> La media estima el valor "verdadero"; la desviación es la barra de error.
```

---

## SLIDE 3 — Qué es un fold y qué es Monte Carlo CV

**PNG a insertar**
- NINGUNO (slide conceptual). No existe PNG de diagrama fold/MC-CV y no hace falta — el texto + analogía bastan. Si querés un gráfico, es opcional dibujarlo en OnlyOffice.

**Bullets del cuerpo**
- Fold = una repetición del sorteo train/val/test (k=5 → 5 modelos desde cero, 5 números).
- MC-CV: cada fold re-sortea del pool completo (328); los test PUEDEN solaparse. Es lo que hace CLAM por defecto.
- No es k-fold canónico (bloques disjuntos). Ambos dan barra de error; CLAM usa MC-CV.
- k=5 en binarias (7 positivas → inestable), k=3 en fusionado (32 positivas → estable).

**Speaker notes**
```
BLOQUE 1 — Definición de fold
-> Un fold es UNA repetición del sorteo train/val/test.
-> Con k=5: 5 sorteos distintos, 5 entrenamientos desde cero, 5 números de test.
-> Cada fold tiene su propio modelo (no se transfiere nada entre folds).

BLOQUE 2 — Validación cruzada Monte Carlo (MC-CV)
-> Cada fold sortea sus 33 slides de test del pool COMPLETO (328), independiente del fold anterior.
-> Los test sets PUEDEN solaparse entre folds.
-> Es lo que hace CLAM por defecto (generate_split, utils/utils.py:104-141): fija la semilla una vez y deja que numpy sortee 5 veces.

BLOQUE 3 — No es k-fold canónico
-> k-fold canónico: la data se parte en 5 BLOQUES disjuntos; cada slide cae en test exactamente 1 vez.
-> MC-CV: cada fold re-sortea, los bloques pueden solaparse.
-> Ambos dan barra de error. CLAM usa MC-CV.

BLOQUE 4 — Por qué k=5 binarias y k=3 fusionado
-> Cuántos folds necesitás depende de cuán inestable es tu test.
-> Binarias: 7 positivas en test, muy inestable, k=5.
-> Fusionado: 32 positivas en test, estable, k=3 basta.

BLOQUE 5 — Analogía
-> Medir una mesa con regla floja una vez te da un número (1.20 m).
-> Medirla 5 veces te da el valor Y la incertidumbre: "1.20 ± 0.01" o "1.22 ± 0.07".
-> MC-CV es exactamente eso para el AUC.
```

---

## SLIDE 4 — Las métricas: recall, accuracy, balanced accuracy, AUC

**PNG a insertar**
- NINGUNO (slide conceptual). Reproducí la matriz de confusión esquemática y la tabla de métricas como TEXTO en la slide (abajo). No hay un PNG genérico y no conviene fabricarlo.

**Bullets del cuerpo** (la matriz va como bloque de texto monoespaciado)
```
                pred: no    pred: sí
verdad no:        TN          FP
verdad sí:        FN          TP
```
- recall+ = TP/(TP+FN); recall− = TN/(TN+FP).
- balanced_acc = (recall+ + recall−)/2 — piso trivial 0.50, robusta al desbalance.
- AUC = ranking, independiente del umbral. Accuracy clásica ENGAÑA con desbalance.

**Speaker notes**
```
BLOQUE 1 — Cuando la decisión clínica importa
-> Balanced accuracy. Mide qué tan bien el modelo DECIDE con el umbral 0.5.

BLOQUE 2 — Cuando importa el ranking, no la decisión
-> AUC. Mide si el modelo "sabe" diferenciar, aunque el umbral esté mal posicionado.

BLOQUE 3 — Por qué reportamos las dos
-> Un modelo puede tener AUC alto y balanced_acc bajo (ordena bien pero umbraliza mal: le pasó a DSMIL en binarias separadas, job 4137).
-> Son complementarias.
Punto clave: balanced accuracy = (recall positivo + recall negativo) / 2. Eso era lo que te preguntó Sebastián.
Detalle crítico: ejemplo del modelo bobo. 90 "no" + 10 "sí"; decir "no" siempre da accuracy 0.90 pero recall+ = 0, balanced_acc = 0.50 = piso trivial = no aprendió.
```

---

## SLIDE 5 — Sin fusión: carcinoma invasivo (Fase 0, k=5 MC-CV)

**PNG a insertar**
- PRIMARIO: `figuras/slide_assets/M01_fase0_carcinoma_invasivo.png` (grid 5 matrices de confusión, una por fold — acompaña la tabla por fold).
- Opcional (más limpio para slide): `figuras/fig4a_fase0_carcinoma_invasivo_confusion.png` (matriz agregada única).

**Bullets del cuerpo**
- Dataset 328 slides, 68 positivas / 260 negativas (ratio 3.8:1).
- AUC media 0.732 ± 0.167; un fold dio 0.41 (peor que random), otro 0.84.
- El 0.808 del 4109 era el TOPE de la distribución. Con barras de error, indistinguible del 0.79 de Sebastián.

**Speaker notes**
```
BLOQUE 1 — La inestabilidad es la noticia
-> AUC va de 0.41 (peor que random) a 0.84 según el sorteo de las 7 positivas.
-> El número suelto del 4109 fue 0.808: era el TOPE de la distribución.
-> Con barras de error, las 3 binarias son indistinguibles del 0.79 de Sebastián.

BLOQUE 2 — Por qué recall+ es bajo y variable
-> Solo 7 positivas en test. Si el modelo se equivoca en 4 de 7, recall+ = 0.43; en 6 de 7, recall+ = 0.14.
-> Es exactamente lo que pasa: recall+ va de 0.14 a 0.57 entre folds.
```

---

## SLIDE 6 — Sin fusión: CDIS (Fase 0, k=5 MC-CV)

**PNG a insertar**
- PRIMARIO: `figuras/slide_assets/M01_fase0_cdis.png` (grid 5 folds).
- Opcional: `figuras/fig4a_fase0_cdis_confusion.png` (matriz agregada).

**Bullets del cuerpo**
- 328 slides, 118 positivas / 210 negativas (ratio 1.8:1, el más balanceado).
- AUC media 0.652 ± 0.072 (va de 0.53 a 0.74); std mediano.
- Sebastián 0.69 cae dentro de la banda → indistinguibles.

**Speaker notes**
```
BLOQUE 1 — Interpretación
-> Menos inestable que carcinoma (más positivas en test, ~11-14).
-> AUC va de 0.53 a 0.74. Std 0.07, mediano.
-> Sebastián 0.69 cae dentro de la banda. Indistinguibles.
```

---

## SLIDE 7 — Sin fusión: tejido no neoplásico (Fase 0, k=5 MC-CV)

**PNG a insertar**
- PRIMARIO: `figuras/slide_assets/M01_fase0_tejido_no_neoplasico.png` (grid 5 folds).
- Opcional: `figuras/fig4a_fase0_tejido_no_neoplasico_confusion.png`.

**Bullets del cuerpo**
- 328 slides, 192 positivas / 136 negativas (la tarea con más positivas).
- AUC media 0.646 ± 0.025 (std súper chico → estable).
- Pero balanced_acc apenas sobre 0.50: el modelo no diferencia bien. Sebastián 0.63 dentro de la banda.

**Speaker notes**
```
BLOQUE 1 — Interpretación
-> El test está casi balanceado (19-21 positivas vs 13-16 negativas).
-> Std súper chico (0.025 en AUC): la métrica es estable.
-> Pero balanced_acc apenas sobre 0.50: el modelo no logra diferenciar bien las dos clases.
-> Sebastián 0.63 cae dentro de la banda.
```

---

## SLIDE 8 — Patrón entre las 3 binarias + por qué el 4109 era ilusión

**PNG a insertar**
- PRIMARIO: `figuras/fig1a_fase0_auc.png` + `figuras/fig1b_fase0_balacc.png` (las barras de error se achican carcinoma → CDIS → tejido: la varianza escala con el nº de positivas).
- PRIMARIO (comparativa): `figuras/slide_assets/T12_comparativa_sebastian.png` (single-split vs MC-CV honesto vs Sebastián).
- Opcional (números completos): `figuras/slide_assets/T05_fase0_resultados.png`.

**Bullets del cuerpo**
- La varianza escala con el nº de positivas en test: carcinoma std(AUC) 0.167, CDIS 0.072, tejido 0.025.
- A más positivas, métrica más estable → prueba empírica de por qué hacía falta MC-CV.
- El "ganamos 0.808 vs 0.79" del 4109 era ilusión: el 0.79 de Sebastián cae cómodo dentro de la banda 0.56–0.90.

**Speaker notes**
```
BLOQUE 1 — Lo que el patrón demuestra
-> La varianza escala EXACTAMENTE con el número de positivas en test, como predijo la hipótesis.
-> A más positivas, métrica más estable; a menos, más bailoteo.
-> Es la prueba empírica directa de por qué MC-CV con varias repeticiones era necesaria.

BLOQUE 2 — Por qué el número "ganador" del 4109 era ilusión
-> En carcinoma (donde "ganamos" 0.808 vs 0.79 de Sebastián) era donde más bailaba el AUC.
-> El 0.79 de Sebastián cae cómodamente dentro de nuestra banda 0.56-0.90.
-> Con barras de error: indistinguibles.
```

---

## SLIDE 9 — Con fusión: binario "¿tiene microcalcificaciones?" (Fase 1 CLAM, k=3)

**PNG a insertar**
- PRIMARIO: `figuras/slide_assets/T06_fase1_resultados.png` (tabla por fold: AUC, bal_acc, recall+/−, confusión).
- Opcional: `figuras/slide_assets/M02_fase1_clam_fusionado.png` (grid 3 folds) y/o `figuras/slide_assets/T02_fusionado_composicion.png` (composición 2814 = 328 sí / 2486 no) para presentar el dataset.

**Bullets del cuerpo**
- Fusión: label "sí" si hay micro en cualquier tejido; "no" = no_identificado. 2814 slides, 328 sí / 2486 no (7.6:1).
- balanced_acc 0.620 ± 0.010 → PLATEAU (no llega al umbral clínico 0.65, pero no colapsa).
- recall+ ≈ 0.36 (detecta 1 de cada 3 micros) vs recall− ≈ 0.88. Accuracy 0.82 ENGAÑA (desbalance).

**Speaker notes**
```
BLOQUE 1 — El patrón es consistente
-> Los 3 folds cuentan la MISMA historia: recall negativo alto (0.83-0.90), recall positivo bajo (0.31-0.44).
-> Std súper chico (0.010 en balanced_acc): cada test tiene 281 slides (32 positivas), mucho más estable que las binarias.

BLOQUE 2 — Qué significa
-> El modelo es bueno descartando slides sanas (recall- alto) y mediocre detectando micros (recall+ ~0.36).
-> Solo encuentra ~36% de los positivos reales.
-> El desbalance 7.6:1 lo empuja a decir "no" pese al --weighted_sample.

BLOQUE 3 — Veredicto vs umbral pre-registrado
-> Umbral clínico (§1.3): >= 0.65 usable, 0.55-0.65 plateau, < 0.55 colapso.
-> balanced_acc 0.620 cae en PLATEAU. Aprende algo pero no llega al umbral.
-> Coherente con la predicción honesta: detector modesto, no salto.

BLOQUE 4 — Por qué la accuracy es alta y engaña
-> Accuracy 0.82 parece muy bueno, pero el modelo solo detecta 36% de los positivos.
-> Con desbalance 7.6:1, decir "no" casi siempre da accuracy alta.
-> Por eso reportamos balanced_acc, no accuracy.
```

---

## SLIDE 10 — Con fusión: ¿gana DSMIL a CLAM? (Fase 2, k=3, comparación pareada)

**PNG a insertar**
- PRIMARIO: `figuras/fig2_fusionado_clam_vs_dsmil.png` (barras CLAM vs DSMIL, bal_acc y AUC con error) + `figuras/slide_assets/T08_fase12_paired.png` (Δ pareado fold por fold).
- Opcional: `figuras/slide_assets/T07_fase2_resultados.png` (DSMIL por fold), `figuras/slide_assets/M03_fase2_dsmil_fusionado.png` (grid 3 folds).
- Opcional (arquitectura): diagrama DSMIL — está en `diagrama_dsmil.md` como **mermaid** (no hay PNG). Renderizalo en OnlyOffice o exportá el mermaid a PNG aparte si lo querés en la slide.

**Bullets del cuerpo**
- Mismos splits que Fase 1 → comparación pareada (única variable: el aggregator).
- Δ balanced_acc +0.040 ± 0.038, positivo en los 3 folds, PERO bandas se solapan y AUC retrocede −0.020.
- DSMIL recupera más positivos (recall+ 0.49 vs 0.36) pero acepta más FP → menos conservador, no mejor discriminador.
- Veredicto: banda AMBIGUA — no sobre-vender como "supera a CLAM".

**Speaker notes**
```
BLOQUE 1 — La dirección es consistente, la magnitud no es concluyente
-> Δ balanced_acc positivo en los 3 folds (signo consistente, mecanismo plausible).
-> Pero magnitud chica y std grande con k=3: +0.040 ± 0.038.
-> Las bandas mean ± std SE SOLAPAN: CLAM [0.610, 0.630] vs DSMIL [0.615, 0.707].
-> AUC retrocede -0.020: no acompaña al balanced_acc.

BLOQUE 2 — Qué cambia DSMIL en la práctica
-> DSMIL recupera más positivos: recall+ 0.49 vs 0.36.
-> Pero acepta más falsos positivos: recall- 0.83 vs 0.88.
-> Lectura: DSMIL es menos conservador, no necesariamente mejor discriminador.
-> El AUC bajando confirma: no rankea mejor, solo desplaza el umbral implícito.

BLOQUE 3 — Veredicto aplicado (§2.2, pre-registrado)
-> Éxito arquitectónico = Δ balanced_acc >= +0.03 mean Y bandas mean ± std no solapadas.
-> DSMIL cumple el Δ (+0.040) pero NO la condición de bandas (se solapan).
-> No es éxito en sentido fuerte. No es regresión. No es plateau estricto.
-> Lectura honesta: banda AMBIGUA. No sobre-vender como "supera a CLAM".

BLOQUE 4 — Guardrail estadístico
-> Los test de MC-CV se solapan entre folds: los Δ están correlacionados.
-> "Bandas no solapadas" es un heurístico de screening, no una prueba de significancia formal.
-> Con k=3 el std mismo es ruidoso (Δ std 0.038 abarca cero).
-> Reportar la dirección del Δ, no afirmar un p-valor.
Punto clave: DSMIL aporta direccionalmente en balanced_acc pero no en AUC, y las bandas se solapan a k=3. No es éxito ni fracaso: es "no concluyente". El cuello sigue siendo datos / contexto espacial / desbalance, no la arquitectura.
```

---

## SLIDE 11 — Anexo: ¿el "fracaso DSMIL en binarias" del 4137 también era ruido?

**PNG a insertar**
- PRIMARIO: `figuras/fig3a_anexo_dsmil_vs_clam_binarias_auc.png` + `figuras/fig3b_anexo_dsmil_vs_clam_binarias_balacc.png` (paired DSMIL vs CLAM por tarea) + `figuras/slide_assets/T09_anexo_resultados.png` (mean±std + Δ pareado + veredicto por tarea).
- Opcional (signo por fold): `figuras/slide_assets/T10_anexo_paired_per_fold.png` (CDIS 5/5 negativo).
- Opcional (detalle): grids `figuras/slide_assets/M04_anexo_{carcinoma_invasivo,cdis,tejido_no_neoplasico}.png` y/o matrices agregadas `figuras/fig4d_anexo_*_confusion.png`. (Para una sola slide, no metas las 3; reservalas para apéndice.)

**Bullets del cuerpo**
- Mismo régimen que Fase 0 (3 binarias × k=5, MISMOS splits) pero con DSMIL. Hipótesis pre-registrada: NULL arquitectónico.
- carcinoma: Δ −0.023 ± 0.071 → NULL (el "0.824" del 4137 era ruido). tejido: Δ +0.021 ± 0.051 → NULL/ambigua.
- CDIS: Δ −0.053 ± 0.026, NEGATIVO en los 5 folds → regresión leve consistente (no es ruido).

**Speaker notes**
```
BLOQUE 1 — La pregunta abierta
-> En Fase 0 vimos que el single-split de CLAM (4109, carcinoma 0.808) era engaño: con MC-CV bajó a 0.732 ± 0.167.
-> El job 4137 (DSMIL x binarias x 1 sorteo) dio "fracaso" en bal_acc en CDIS y tejido.
-> ¿Y si ese fracaso también era ruido del sorteo, como pasó con CLAM?
-> Sin MC-CV no podíamos sostener "DSMIL falla en binarias". Hicimos el experimento.

BLOQUE 2 — Setup (job 4179, 28-may, ~3h29m)
-> Mismo régimen que Fase 0: 3 binarias x k=5 MC-CV, MISMOS splits, mismas features, misma seed.
-> Único cambio: modelo DSMIL en vez de CLAM (w_max 0.1 fijo, idéntico a Fase 2, no se retunea).
-> Hipótesis primaria pre-registrada: NULL arquitectónico (el cuello es datos, Hallazgo 4 Fase 0).
-> Reviewer OK (regla 9 cumplida) antes del sbatch.

BLOQUE 3 — Resultado (mean ± std vs CLAM Fase 0, pareado)
-> carcinoma: Δ pareado -0.023 ± 0.071 -> NULL.
-> CDIS: Δ pareado -0.053 ± 0.026 -> regresión leve.
-> tejido: Δ pareado +0.021 ± 0.051 -> NULL / ambigua.

BLOQUE 4 — Por qué CDIS es distinto
-> En CDIS los 5 folds dan Δ NEGATIVO. No es ruido aleatorio: es consistente.
-> El "fracaso DSMIL en CDIS" del 4137 (single-split) se sostiene con barras de error.
-> En carcinoma y tejido los signos están mezclados -> ruido alrededor de cero -> empate.
Punto clave: DSMIL evaluado en TODOS los regímenes con MC-CV. En binarias, 2 de 3 dan empate estadístico con CLAM. CDIS es la única con regresión consistente: abre una pregunta morfológica para futuro, no decisión de este sprint.
```

---

## SLIDE 12 — Lo que el anexo cierra: el cuadro CLAM-vs-DSMIL completo

**PNG a insertar**
- PRIMARIO: `figuras/slide_assets/T13_cuadro_arquitecturas.png` (cuadro 2×2 modelos × regímenes).
- Opcional: `figuras/slide_assets/T11_comparativa_maestra.png` (las 16 filas, todos los entrenamientos — buena de apoyo / apéndice).

**Bullets del cuerpo**
- Cuadro cerrado simétricamente: CLAM y DSMIL × {binarias n=328, fusionado n=2814}, todo con MC-CV.
- Binarias: empate estadístico en 2/3; DSMIL retrocede leve en CDIS. Fusionado: DSMIL mejora marginal en bal_acc, no en AUC, bandas solapadas.
- Patrón consistente: la arquitectura sola no es la palanca a ninguna escala de datos disponible.

**Speaker notes**
```
BLOQUE 1 — Cuadro arquitectónico cerrado simétricamente
-> CLAM: Fase 0 (binarias, bal 0.58-0.64) + Fase 1 (fusionado, bal 0.620 ± 0.010, plateau).
-> DSMIL: Anexo (binarias, bal 0.54-0.62, Δ ~0 salvo CDIS) + Fase 2 (fusionado, bal 0.661 ± 0.046, ambigua).

BLOQUE 2 — La lectura unificada
-> Régimen pequeño (binarias, n=328): CLAM y DSMIL empatan en 2 de 3; DSMIL retrocede leve en CDIS.
-> Régimen grande (fusionado, n=2814): DSMIL mejora marginal en bal_acc pero NO en AUC, bandas solapadas -> ambigua.
-> Patrón consistente: la arquitectura sola no es la palanca a ninguna escala de datos disponible.

BLOQUE 3 — Lo que significa para el proyecto
-> El cuello sigue siendo datos / contexto espacial / desbalance, y ahora la evidencia es simétrica (no es culpa del modelo).
-> Los próximos ejes (mayor magnificación CONCH, selección de parches útiles) atacan el cuello real.
-> CDIS abre una pregunta morfológica (atención gated absoluta de CLAM vs dual relacional de DSMIL): otra iteración, no este sprint.
```

---

## SLIDE 13 — Cierre: la lección del Objetivo 5

**PNG a insertar**
- NINGUNO obligatorio (slide de cierre, texto). Opcional: `figuras/slide_assets/T11_comparativa_maestra.png` o `T13_cuadro_arquitecturas.png` como recordatorio visual.

**Bullets del cuerpo**
- El single-split del 4109 era optimista por suerte; la estimación honesta es más modesta. Frente a Sebastián: paridad estadística.
- Fusionar las 3 binarias + incluir no_identificado NO fue bala de plata (bal_acc 0.620 ≈ promedio de las binarias).
- DSMIL fusionado: banda ambigua. Anexo binarias: NULL en 2/3, regresión leve en CDIS.
- Aporte real = medir la incertidumbre que el single-split escondía, NO ganar métricas vs Sebastián.

**Speaker notes**
```
BLOQUE 1 — Cinco descubrimientos (con el anexo cerrado)
-> El single-split del 4109 era optimista por suerte. La estimación honesta es más modesta.
-> Frente a Sebastián, estamos en paridad estadística (no superiores, no inferiores).
-> Fusionar las 3 binarias + incluir no_identificado NO fue bala de plata: balanced_acc 0.620 ~ promedio de las binarias separadas (0.60).
-> DSMIL sobre el fusionado dio Δ +0.040 en balanced_acc (3 folds positivos) pero bandas solapadas y AUC retrocediendo: banda AMBIGUA.
-> El "fracaso DSMIL en binarias" del 4137 era ruido en carcinoma y tejido (empate con MC-CV); en CDIS se sostiene (regresión leve consistente 5/5 folds): pregunta morfológica abierta.

BLOQUE 2 — Lo que el objetivo aportó
-> Medir la incertidumbre que el single-split escondía (binarias y fusionado).
-> Cerrar el cuadro arquitectónico CLAM vs DSMIL en TODOS los regímenes (binarias k=5 + fusionado k=3).
-> Confirmar que el cuello sigue siendo datos / contexto espacial / desbalance, NO la arquitectura sola NI la formulación.
-> Justificar empíricamente los próximos ejes: mayor magnificación CONCH y selección de parches con información.

BLOQUE 3 — Próximos pasos (aprobados por Sebastián, futuros sprints)
-> Re-extraer CONCH a mayor magnificación, solo para slides de microcalcificaciones.
-> Selección de parches útiles vía el mejor modelo, estilo heatmap Camelyon.
-> Pregunta abierta secundaria (CDIS): atención gated absoluta de CLAM vs dual relacional de DSMIL. Tema morfológico.
-> Ver sprints/B4_sprint4/ejes_futuros_microcalc.md.
```

---

## Apéndice — Inventario de assets por si querés reorganizar

| Slide | Primario | Opcional / apéndice |
|---|---|---|
| 1 | T04 | T03 |
| 2 | fig1a | (solo-texto) |
| 3 | — (texto) | — |
| 4 | — (texto) | — |
| 5 | M01_carcinoma | fig4a_carcinoma |
| 6 | M01_cdis | fig4a_cdis |
| 7 | M01_tejido | fig4a_tejido |
| 8 | fig1a + fig1b + T12 | T05 |
| 9 | T06 | M02, T02 |
| 10 | fig2 + T08 | T07, M03, diagrama DSMIL (mermaid) |
| 11 | fig3a + fig3b + T09 | T10, M04×3, fig4d×3 |
| 12 | T13 | T11 |
| 13 | — (texto) | T11 / T13 |

**Assets que NO se usan como primario** (disponibles para apéndice): `T01_binarias_composicion.png` (composición de las 3 binarias — sirve si añadís una slide de setup antes de la 5).

**Recordatorio**: todos los números provienen de la verdad de campo en
`resultados.md` (§FASE 0/1/2/ANEXO) y `tablas_presentacion.md`. No inventar
métricas: si falta una, está en esos .md.
