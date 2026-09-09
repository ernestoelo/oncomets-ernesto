# Pre-registro O3 — ¿La atención de CLAM localiza el CDIS?

> Escrito el **9-sep-2026**, antes de medir. Regla 9. **CPU, cero GPU.**
>
> Encargo 3 de Sebastián, textual: «una vez identificado el CDIS, el grado nuclear sí o sí va a
> depender de la tarea de localización del CDIS», evaluando por ahora sólo sobre láminas anotadas.
>
> Convierte «a CLAM le costaba identificar el CDIS» en un número. **D4 de Ernesto**: se limita a
> medir la atención **que ya está en disco**. Sin BRACS y sin entrenar.

---

## 0. El censo, verificado el 9-sep contra el archivo

**30 polígonos de CDIS en 10 láminas**, que es exactamente lo que citó Sebastián:

| clase | n | láminas |
|---|---|---|
| `CDIS_solido` | 10 | 124729 (5), 124806 (2), 126504 (1), 132844 (1), 142541-1 (1) |
| `CDIS_papilar` | 6 | 110616 (6) |
| `DCIS` | 6 | 164001 (3), B25-158899 (3) |
| `CDIS_cribiforme` | 5 | 128250 (4), 131461-1 (1) |
| `CDIS_micropapilar` | 3 | 131461-1 (3) |

Dos de esas clases (`CDIS_cribiforme`, `CDIS_micropapilar`) **no existían** en el vocabulario de
las doce del B9. Se tratan como CDIS, que es lo que son en el checklist del CAP (Nota C, «Cribriform»
y «Micropapillary» son patrones arquitectónicos de DCIS).

### 0.a El cruce contra la etiqueta clínica, que reordena los grupos

Contra `dataset_carcinoma_ductal_in_situ_presente_label.csv`:

| grupo | n | láminas |
|---|---|---|
| polígonos **y** etiqueta `si` | **8** | 124729, 124806, 126504, 128250, 131461-1, 132844, 142541-1, 164001 |
| polígonos y etiqueta `no_identificado` | 1 | **110616** (6 `CDIS_papilar`) |
| polígonos y **sin fila en el CSV** | 1 | **B25-158899** |
| etiqueta `si` y **cero polígonos** | **3** | **129741, 133677, 154144** |
| etiqueta `no` y cero polígonos | **8** | 103762, 106552, 109609, 110962, 128194, 132208, 141426-1, 144317 |

Tres consecuencias de diseño, y las tres van declaradas antes:

1. **Las 3 láminas `si` sin polígono NO son negativos.** Son positivos **no anotados**: el patólogo
   marca donde la evidencia es clara, no todo lo que existe. Meterlas al grupo negativo fabricaría
   un contraste a favor. **Salen de los dos grupos** y se reportan aparte.
2. **La 110616 es `no_identificado` con 6 polígonos.** `no_identificado` significa que el reporte CAP
   **no menciona** el hallazgo, no que esté ausente ([[microcalc-dataset-decision]]). Entra al grupo
   con polígonos, y su etiqueta se declara en la tabla.
3. **La B25-158899 no tiene fila en el CSV** (es un caso de 2025). Entra por polígono, sin etiqueta.

## 1. Las dos fuentes de atención, y por qué hacen falta las dos

### 1.a `json_out` (el ensemble de `sgaete`, READ-ONLY)

`clam_ensemble/attn_batch/json_out/<slide>__carcinoma_ductal_insitu_presente_pth_balance.json`,
verificado presente para las 10 láminas con polígonos. **Tres contaminaciones que se declaran cada
vez que se usa** ([[clam-ensemble-json-out-atencion]]):

- es un **ensemble de los cinco folds**, así que está contaminado por construcción (incluye los
  folds donde la lámina estuvo en `train`);
- lee la rama de la clase **predicha**, no la verdadera;
- es la familia **`_pth_balance`**, no la `_combined_5fold` de los números de referencia del B8.

### 1.b Checkpoint con la cabeza VERDADERA (no es opcional)

`environ/results_modelo_pth_balance/carcinoma_ductal_insitu_presente_pth_balance_s1/s_0_checkpoint.pt`,
**un solo fold**, con su `splits_0.csv` al lado.

**Este brazo no es opcional**: `json_out` lee la rama predicha, y eso ya produjo un **0,500 exacto**
en otro eje ([[rama-de-atencion-decide-el-resultado]]). Un AUC de 0,5 que viene de leer la rama
equivocada es indistinguible de un AUC de 0,5 que viene de que el modelo no localiza, y esa
confusión es exactamente lo que este eje tiene que evitar.

### 1.c El tier de cada lámina, leído del `splits_0.csv` y declarado en la tabla

**No hay familia 5fold para esta tarea** (`results_modelo_combined_5fold/` sólo tiene
`mitotic_rate`), así que **no existe brazo de folds limpios sin entrenar**, y entrenarlos está
fuera de alcance por D4. Lo que hay es un fold, y su reparto sobre las anotadas es este:

| tier | láminas con polígonos | láminas del control negativo |
|---|---|---|
| `train` | **5** (110616, 124729, 128250, 131461-1, 142541-1) | 7 (103762, 106552, 109609, 110962, 128194, 132208, 141426-1) |
| `val` | 3 (124806, 132844, 164001) | 0 |
| `test` | **1** (126504) | 1 (144317) |
| fuera del split | 1 (B25-158899) | 0 |

**Una sola lámina con polígonos cae en `test`.** Esto es un límite duro del material, no una
elección: se reporta el agregado **y** la fila de la 126504 sola, y **una lámina en `train` no se
presenta como evidencia limpia**. Si el agregado y la única lámina limpia discrepan, manda la
limpia y se dice que `n` = 1.

## 2. Unidad, métrica y nulo

**Unidad**: el **parche** (256 px de lado, 0,0142 mm²), que es la unidad en la que CLAM produce
atención. Cada parche del `.h5` de la lámina se etiqueta `1` si su centro cae dentro de algún
polígono de CDIS (con el offset de la lámina aplicado) y `0` si no.

**Métrica**: **AUC de rango** (Mann-Whitney U normalizado) de la atención sobre los parches de la
lámina, positivos = parches bajo polígono de CDIS. Nulo 0,5. Es el estadístico del B9
(`scripts/b9_atencion_12_laminas.py`) y se reusa sin cambiarlo.

**Dos incertidumbres, las dos se reportan** ([[auc-atencion-dos-incertidumbres]]): la dispersión
entre fuentes y el **IC de Hanley-McNeil**, que depende del `n` de positivos y es la grande cuando
una lámina tiene 1 solo polígono.

**Nulo**: **traslación rígida** de la máscara de CDIS, nunca permutación de etiquetas de parche
([[nulo-espacial-traslacion-rigida]]). 200 iteraciones ⇒ piso del `p` en 1/201.

**El control negativo mide otra cosa, y se dice.** Las 8 láminas `no` **no tienen polígonos**, así
que ahí no hay AUC que calcular. Lo que aportan es el brazo del patrón P3: sobre ellas se mide la
**concentración espacial de la atención** (con el mismo estadístico sobre una máscara trasladada al
azar) y la **predicción de la lámina**, para saber qué hace el modelo cuando no hay CDIS. **No se
promedian con las positivas**: son dos tablas.

## 3. Hipótesis y dirección esperada

**H_O3 (primaria)**: en las láminas con polígonos, el AUC de la atención sobre los parches de CDIS
es **> 0,5**, consistente en signo entre láminas, y por encima del nulo por traslación.

**H_O3 nula**: AUC ≈ 0,5. Lectura: la atención de CLAM **no localiza** el CDIS, y entonces la cadena
que propuso Sebastián (localizar CDIS antes de graduar) **no se puede montar sobre esta atención**,
que es información accionable y es probablemente el resultado más útil de los dos.

**H_O3 regresión**: AUC < 0,5 consistente, o sea que la atención **evita** el CDIS. Antes de
interpretarlo hay que descartar que se esté leyendo la rama equivocada, que es exactamente para lo
que está el brazo del §1.b.

**Comparación declarada**: `json_out` (rama predicha, ensemble contaminado) contra checkpoint (rama
verdadera, un fold). **Si los dos discrepan, manda el de la rama verdadera** y la discrepancia es el
hallazgo, no un problema a promediar.

## 4. Qué NO se va a afirmar

- **Ni precisión, ni F1, ni PQ.** Positivos parciales, en los dos grupos.
- **No se va a llamar negativo** a un parche sin polígono. Las 3 láminas `si` sin marca lo prueban.
- **No se va a presentar el agregado como evidencia limpia**: 5 de las 10 con polígonos están en
  `train` del único fold disponible (§1.c).
- **No se va a afirmar que un AUC alto signifique que CLAM «entiende» CDIS.** Mide que la atención
  se concentra donde el patólogo dibujó, sobre láminas donde el modelo ya vio la etiqueta.
- **No se va a comparar contra los números del B8**, que son de la familia `_combined_5fold` y no de
  `_pth_balance`.
- **No se va a interpretar el `no_identificado` de la 110616 como ausencia.**

## 5. Artefactos que produce

| Qué | Path |
|---|---|
| Driver | `scripts/b10_cdis_atencion.py` |
| AUC por lámina, fuente y tier | `results/b10_cdis/auc_cdis.csv` |
| Nulos por traslación | `results/b10_cdis/nulo.npy` |
| Log | `logs/b10_cdis_atencion.log` |
| Resultados y lectura | `resultados.md` |
