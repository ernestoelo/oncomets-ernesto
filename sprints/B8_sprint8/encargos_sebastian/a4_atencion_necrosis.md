# Encargo 3, mitad CLAM — la atención de necrosis contra las marcas del patólogo

> Medido el **21-ago-2026**, CPU post-hoc, sin GPU. Selección:
> [`interp_slides_necrosis.json`](../hovernext_129741/interp_slides_necrosis.json).
> Salidas: `results/b8_hovernext_129741/{interp/carcinoma_ductal_insitu_necrosis,auc_necrosis_f0}/`.
> Planificado en [`plan.md`](plan.md) §A4.

Sebastián pidió revisar si la necrosis que señala HoVer-NeXt coincide con las marcas del
patólogo. **Este documento cubre la mitad que se podía contestar sin GPU**: la de CLAM. La otra
mitad **no es opcional ni es pereza**: el checkpoint de HoVer-NeXt que corrimos es
Lizard-Mitosis y **no tiene clase de necrosis** — `dead` vive solo en PanNuke
(`hover_next_reference/src/constants.py:44-48`), que nunca se lanzó. Esa mitad es **B2**.

## 0. El aviso que va antes de cualquier número

**El modelo de necrosis es débil, y hay que decirlo cada vez que se cite el 0,899.** Entrenado
con **train=45 / val=7 / test=9**; su `summary.csv` da **test_auc 0,557** y **test_acc 0,222**;
y **colapsa**: predice la clase 1 en 8 de las 9 láminas de test. Sobre la 129741 **se equivoca**:
la clase verdadera es `presente_central` y predice `ausente` con probabilidades
[0,599 · 0,106 · 0,294 · 0,000].

Eso no invalida lo que sigue, pero cambia cómo se lee: lo que se mide acá **no es la calidad del
clasificador**, es **dónde mira una de sus cabezas de atención**. Y resulta que son cosas
distintas, que es el hallazgo del §2.

## 1. Qué se midió, y sobre qué

- **Checkpoint**: `environ/results_modelo/carcinoma_ductal_insitu_necrosis_s1/s_0_checkpoint.pt`.
  **CLAM_MB plano**, verificado por `state_dict` (25 claves, cero `mammoth`) y no por su
  `experiment.txt`, que es lo que enseñó [[checkpoint-familia-se-lee-del-statedict]]. Ajeno
  (`clam_environ`), se lee y no se toca.
- **La 129741 cae en TEST** del fold 0 de `environ/splits/carcinoma_ductal_insitu_necrosis_100`:
  no fue vista en entrenamiento.
- **El `label_dict` hardcodeado está STALE y no se usó.** `clam_environ/main.py:157-161` declara
  `{'no identificado':0, 'focal':1, 'central':2}`, y **esos strings no existen en el CSV**. El
  CSV real (`csv_privado/dataset_carcinoma_ductal_in_situ_necrosis_label.csv`, 90 filas) trae
  `{ausente:32, presente_central:30, no_identificado:27, presente_focal:1}`. La corrida usó
  `--auto-label-dict` (alfabético): **`ausente`=0, `no_identificado`=1, `presente_central`=2,
  `presente_focal`=3**. Confirmado por dos vías independientes: el checkpoint tiene
  `attention_c` con **4** salidas (no 3), y en `split_0_results.pkl` la 129741 sale `label=2`,
  que es `presente_central`, su etiqueta en el CSV.
- **Unidad**: **parches** (18), no polígonos. Los **6** polígonos de `necrosis` del geojson tocan
  **18 parches** del h5. No mezclar con las unidades del eje de mitosis: marcas (26/94), parches
  (28), detecciones (177).
- **Universo**: la región anotada (2496 parches de los 4799; la lámina tiene dos regiones de
  escaneo y las anotaciones caen todas abajo, `y ≥ 49920`).

## 2. El resultado, y por qué la rama que se lee decide todo

AUC de la atención como detector de los 18 parches con `necrosis`, **las cuatro ramas**:

| rama | AUC | IC 95 % | percentil mediano | nulo |
|---|---|---|---|---|
| **`presente_central`** (la **verdadera**) | **0,899** | 0,804–0,995 | **96,8 %** | **p = 0,0005** |
| `no_identificado` | 0,740 | 0,607–0,872 | 77,5 % | — |
| **`ausente`** (la que el modelo **predijo**) | **0,500** | 0,366–0,633 | 45,4 % | — |
| `presente_focal` | 0,458 | 0,328–0,587 | 44,6 % | — |

**La rama predicha da 0,500: exactamente el azar.** La rama verdadera da 0,899, con el nulo por
**traslación rígida** (no por permutación de etiquetas, porque los polígonos son contiguos,
[[nulo-espacial-traslacion-rigida]]) en **p = 0,0005**. Es la evidencia directa de por qué leer
la rama predicha contesta otra pregunta: `sgaete` midió sobre la rama predicha y obtuvo **AUC
0,382**, bajo el azar. **Queda pendiente preguntarle si esa elección es deliberada**, y este
número es lo que hay que mostrarle.

### El hallazgo que no esperábamos

**El modelo se equivoca de clase en esta lámina y su cabeza de `presente_central` igual sabe
dónde está la necrosis.** A nivel lámina predice `ausente`; a nivel parche, la cabeza de la
clase correcta pone los parches con necrosis en el **percentil 96,8**. Localización y decisión
**se disocian**: son dos preguntas distintas y este modelo acierta la primera fallando la
segunda.

Es un argumento a favor de leer siempre la rama de la clase verdadera cuando se la conoce, y de
**no** usar la predicción del modelo como criterio para elegir qué mirar.

## 3. La señal es específica, no un mapa de "tejido interesante"

La misma rama `presente_central` sobre todos los grupos anotados:

| grupo | n parches | AUC | IC 95 % | nulo |
|---|---|---|---|---|
| **necrosis** | 18 | **0,899** | 0,804–0,995 | **0,0005** |
| Mitosis | 28 | 0,736 | 0,630–0,843 | 0,0526 |
| Tumor | 48 | 0,704 | 0,620–0,787 | 0,0160 |
| Núcleos alto grado | 13 | 0,600 | 0,437–0,764 | 0,4348 |
| Stroma | 12 | 0,458 | 0,300–0,617 | — |
| Immune cells | 23 | 0,416 | 0,306–0,526 | — |
| Tejido Adiposo | 27 | 0,088 | 0,057–0,119 | — |

La necrosis queda **primera y separada**, y el adiposo casi en cero (o sea que la atención lo
**evita** activamente). No es un mapa genérico de "acá hay tejido": discrimina.

Dicho eso, **necrosis y tumor no son independientes en el tejido** (la necrosis comedo vive
dentro del ducto tumoral), así que parte del 0,704 de Tumor y del 0,899 de necrosis miran zonas
que se solapan. No se afirma que la cabeza distinga necrosis **de** tumor.

## 4. Qué se responde y qué no

- **Se responde, para el brazo CLAM**: la atención del modelo de necrosis **sí** cae sobre la
  necrosis que marcó el patólogo, con AUC 0,899 y nulo espacial p = 0,0005, y **es específica**.
- **No se responde el encargo completo.** La pregunta de Sebastián era si **la necrosis que
  señala HoVer-NeXt** coincide con las marcas. Eso exige la clase `dead`, que solo tiene PanNuke.
  **Es B2**, y su cruce **no es el de mitosis**: la necrosis del patólogo son **regiones** (6
  polígonos) y `dead` son **núcleos** (puntos). No hay emparejamiento uno a uno posible; se mide
  densidad dentro contra fuera, cuántos de los 6 polígonos contienen al menos un `dead`, y el
  nulo por traslación rígida.
- **No se afirma que el modelo de necrosis sirva.** Es débil (§0) y en esta lámina falla. Lo que
  se afirma es más chico y más raro: **una de sus cabezas localiza bien aunque la decisión de
  lámina esté mal**.
- **Una lámina, 18 parches, un checkpoint.** Sin sd entre checkpoints; las dos incertidumbres del
  caso están en [[auc-atencion-dos-incertidumbres]], y con n=18 la grande es el IC de
  Hanley-McNeil, que acá va de 0,804 a 0,995.
- **No se calcula precisión** contra el geojson y **nada se llama falso positivo**: las
  anotaciones del patólogo son **positivos parciales**.
- El vocabulario de necrosis del patólogo es **inconsistente entre láminas** (`necrosis` en la
  129741, `Necrosis` en 128194 y B25-158899, `Comedonecrosis` en 124729 y 124806). Acá solo se
  usó `necrosis`, que es lo que trae esta lámina. Barrer las 5 láminas con necrosis exige
  unificar ese vocabulario antes, y **no está hecho**.
