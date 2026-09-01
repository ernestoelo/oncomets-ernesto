# Hechos verificados antes de pre-registrar el eje de atención

> **1-sep-2026, sesión 38.** Todo lo de acá se verificó **contra el archivo**, no contra un doc.
> Es el insumo del `prereg.md`, que todavía **no existe**: lo escribe la sesión que ejecute.
>
> Existe porque tres afirmaciones del plan del 1-sep
> ([`../../../.handoffs/plan_B9_20260901_revision_deck_y_atencion.md`](../../../.handoffs/plan_B9_20260901_revision_deck_y_atencion.md))
> **no resistieron la verificación**, y una de ellas habría hecho fallar el gate de regresión
> contra un número que el driver no puede producir.

---

## 1. El número de referencia del B8 no es lo que el plan dice

El plan fija como gate: «sobre la 129741, cabeza verdadera, **confinado a la región anotada**, el
AUC tiene que reproducir el **0,890 ± 0,034** dentro de su rango 0,840-0,926». Las tres partes de
esa frase fallan. Verificado sobre
[`../../B8_sprint8/atencion_vs_patologo/auc_por_checkpoint.csv`](../../B8_sprint8/atencion_vs_patologo/auc_por_checkpoint.csv)
y su gemelo `con_region/`, grupo `Mitosis`, `es_cabeza_verdadera == True`:

| | lámina | región |
|---|---:|---:|
| media de los **4 primarios** | **0,8901 ± 0,0391** | **0,9025 ± 0,0322** |
| media de los **3 contaminados** | 0,9456 ± 0,0044 | 0,9500 ± 0,0065 |
| media de la familia **5fold limpia** (f0, f2) | **0,9211** | **0,9265** |

Tres correcciones:

1. **La sd es 0,039, no 0,034.**
2. **El 0,890 es el universo `lámina`**, no el región. El región es **0,903**, que es el que la
   tabla de [`resultados.md`](../../B8_sprint8/atencion_vs_patologo/resultados.md) §1 publica.
3. **Los 4 primarios salen de tres directorios distintos**, no de la familia 5fold:

   | ckpt | directorio | AUC lámina |
   |---|---|---:|
   | `seba_privado_s0` | `results_modelo/…_s1/s_0` | 0,840315 |
   | `seba_combined_s0` | `results_modelo_combined/…_s1/s_0` | 0,877983 |
   | `seba_5fold_f0` | `results_modelo_combined_5fold/…_s1/s_0` | **0,925697** |
   | `seba_5fold_f2` | `results_modelo_combined_5fold/…_s1/s_2` | **0,916527** |

**La consecuencia operativa.** El driver que el plan especifica usa **sólo la familia
`results_modelo_combined_5fold`**, o sea f0 y f2 para la 129741. Su valor esperado es **0,9265**
en región, que cae **fuera de la banda 0,840-0,926 del propio plan**. El gate como estaba escrito
disparaba una falsa alarma en el caso región, o pasaba por suerte en el caso lámina (0,9211 entra
por 0,005). En los dos casos estaba midiendo otra cosa que la que dice medir.

### 1.a El gate que sí sirve, y es más barato

Como el CSV del B8 está en el repo y trae el valor **por checkpoint**, el gate no necesita bandas:
se compara **exacto**, a 1e-6.

| ckpt | lámina | región |
|---|---:|---:|
| `seba_5fold_f0` | **0,925697** | **0,936444** |
| `seba_5fold_f2` | **0,916527** | **0,927269** |

Reproducir esos cuatro valores es una regresión bastante más fuerte que un «± 1 sd», y distingue
de verdad **bug del driver** de **resultado**. Es el mismo principio que el `md5` del checkpoint
en [[pipeline-determinista-bit-a-bit]]: si hay una referencia exacta disponible, una banda es una
pérdida de poder.

---

## 2. El driver NO corre en `envs/pruebas`

El handoff manda el eje de atención a `envs/pruebas`. No puede:

| | `pruebas` | `clam_latest` |
|---|---|---|
| `torch` | 2.7.1+cu118 | 2.8.0+cu128 |
| `topk` (smooth-topk) | **FALTA** | OK |
| `zarr` | 2.18.3 | **FALTA** |
| `libopenslide` parchada (1,2 MB) | **no está** | sí, `1200248` bytes |

`build_clam` ([`scripts/atencion_vs_anotaciones.py:97`](../../../scripts/atencion_vs_anotaciones.py#L97))
importa `topk.svm.SmoothTop1SVM` para instanciar `CLAM_MB`, así que **cualquier** reuso de esa
función arrastra `topk`. Y los mapas de calor piden la `libopenslide` parchada para abrir los
`.bif` (workaround **K**), que tampoco está en `pruebas`.

**Reparto correcto de intérpretes**, y no es el del handoff:

- `scripts/b9_atencion_12_laminas.py` y `scripts/b9_mapas_atencion_12.py` → **`clam_latest`**.
- `generate_b9_deck.py` → sigue en **`pruebas`**, que es donde está `zarr` (lo pide `datos_eje3`).
- La costura aguanta porque `datos_atencion()` sólo **lee un CSV**: no importa nada del driver, así
  que no hay dependencia cruzada entre los dos entornos.

---

## 3. «Fold limpio» son TRES cosas distintas, no dos

La tabla de membresía del plan es **correcta** (8 láminas con 5 folds limpios, dos con 2, dos con
1), reproducida acá contra
`environ/splits_5fold/grado_histologico_mitotic_rate_combined_100/splits_{0..4}.csv`. Lo que le
falta es que **el motivo por el que un fold es limpio no es el mismo en las tres filas**:

| tier | láminas | folds limpios | por qué |
|---|---|---|---|
| **ausente** de los cinco splits | 103762 · 106552 · 109609 · 110616 · 124729 · 124806 · 126504 · B25-158899 | los 5 | nunca entró a la tarea |
| limpio por **val** | 129741 (f0, f2) · 164001 (f3) · 144317 (f4) | 2 · 1 · 1 | no estuvo en train, pero **gobernó el early stopping** |
| limpio por **test** | 128194 (f2) · 144317 (f0) | 1 · 1 | no estuvo en train ni en val |

El orden de limpieza es **ausente > test > val**: una lámina en `val` seleccionó el checkpoint por
`val_loss`, así que su «limpieza» es más débil que la de una que el modelo no vio nunca. El
pre-registro del B8 ya trataba `val` como `rol="primario"` y lo describía como «nunca vista en
entrenamiento», así que **el criterio tiene precedente y no se cambia**; lo que se agrega es
**declarar el tier**, porque el agregado sobre las doce los mezcla.

**Nota sobre las ocho ausentes**: no faltan por no tener etiqueta (siete de las ocho la tienen, §4).
Los splits cubren un subconjunto del CSV de la tarea. Por qué, no se investigó, y no hace falta
para este eje: lo que decide es que **no estuvieron en train en ningún fold**.

---

## 4. Las etiquetas, y por qué el primario son NUEVE láminas

Verificado sobre `environ/csv/dataset_grado_histologico_tasa_mitotica_label.csv` (1870 filas):

| label | láminas |
|---|---|
| `score_3` | 129741 · 126504 · 128194 |
| `score_2` | 124729 · 144317 · 109609 |
| `score_1` | 124806 · 164001 · 103762 |
| `no_identificado` | 106552 · 110616 |
| **sin fila en el CSV** | **B25-158899** |

`B25-158899` no aparece en ese CSV ni bajo otro nombre (aparece en `csv/dataset_validation.csv`,
que es otra cosa) ⇒ **su cabeza de la clase verdadera no existe**.

`no_identificado` **sí** es una clase entrenada (el `label_dict` de la tarea es
`CLASSES_4 = [no_identificado, score_1, score_2, score_3]`, 693 de las 1870 filas), así que la
cabeza existe para 106552 y 110616. Pero significa **«el reporte CAP no menciona tasa mitótica»**,
que no es un grado de severidad mitótica: leer esa cabeza como «dónde busca mitosis el modelo» es
un salto que el material no sostiene.

> **Decisión de Ernesto (1-sep):** el **primario son las nueve** con `score_1/2/3`, que reúnen
> **103 de los 113 parches** con `Mitosis`. Las otras tres se miden igual y se **reportan aparte**
> con la cabeza predicha. Así el titular queda semánticamente limpio sin perder material: las tres
> siguen en la tabla por lámina.

---

## 5. El agregado: media sin ponderar sobre láminas

El `n` de parches marcados va de **2 a 28** por lámina, o sea un factor 14. Con ese rango, «media
de los AUC por lámina» y «un AUC agrupando todos los parches» dan números distintos, y el plan no
decía cuál.

> **Decisión de Ernesto (1-sep):** primario = **media sin ponderar sobre láminas**, cada lámina un
> voto, que es tratar la **lámina como la réplica**. El **pooled sobre parches** se reporta como
> secundario.

Es el mismo criterio que ya gobierna el eje 3, donde el `n` honesto son **láminas y no marcas**
porque el grado está confundido con la lámina. Acá el argumento es paralelo: ponderar por parches
le da a la 129741 y la 126504 (28 cada una) la mitad del peso, que es exactamente el sesgo que el
cruce de las 94 documentó cuando mostró que la 129741 era el mejor caso y no el típico.

---

## 6. Los insumos, verificados uno por uno

| qué | estado |
|---|---|
| `environ/features/h5_files/<slide>.h5` | **12 de 12** presentes |
| `environ/features/pt_files/<slide>.pt` | **12 de 12** presentes |
| `../../B8_sprint8/anotaciones_patologo/parches_anotados_<slide>.csv` | **12 de 12**, columnas `slide_id,x,y,patch_size,clases` (multi-etiqueta con `\|`) |
| parches con `Mitosis` | **113**: 28 · 28 · 21 · 7 · 7 · 6 · 4 · 4 · 2 · 2 · 2 · 2 |
| checkpoints `…_combined_5fold/…_s1/s_{0..4}_checkpoint.pt` | los 5, 2,1 MB cada uno |
| `results/b9_cruce_94/pares_<slide>.csv` | los 12 |

Reparto de los 113 por lámina, que es el que hay que dejar visible en toda tabla del eje:

| lámina | parches `Mitosis` | folds limpios | label | primario |
|---|---:|---:|---|:-:|
| 129741 | 28 | 2 (f0, f2 · val) | `score_3` | sí |
| 126504 | 28 | 5 (ausente) | `score_3` | sí |
| 128194 | 21 | 1 (f2 · test) | `score_3` | sí |
| 124729 | 7 | 5 (ausente) | `score_2` | sí |
| 124806 | 7 | 5 (ausente) | `score_1` | sí |
| B25-158899 | 6 | 5 (ausente) | **sin label** | no |
| 144317 | 4 | 2 (f0 · test, f4 · val) | `score_2` | sí |
| 164001 | 4 | 1 (f3 · val) | `score_1` | sí |
| 106552 | 2 | 5 (ausente) | `no_identificado` | no |
| 103762 | 2 | 5 (ausente) | `score_1` | sí |
| 109609 | 2 | 5 (ausente) | `score_2` | sí |
| 110616 | 2 | 5 (ausente) | `no_identificado` | no |
| **total** | **113** | | | **9 láminas · 103 parches** |

### 6.a Las primitivas que se importan, no se copian

| qué | de dónde |
|---|---|
| `rank_auc`, `ranks_of`, `p_traslacion` | `scripts/atencion_vs_anotaciones.py:127,133,159` |
| `ic_hanley_mcneil` | `scripts/auc_atencion_fold4.py:58` |
| `build_clam`, `get_attention` | `scripts/atencion_vs_anotaciones.py:97,117` |
| `REGION_ANOTADA` (intervalo por lámina) | `scripts/cruce_94_marcas.py:71` |
| `percentile_scores`, `get_wsi_thumbnail`, `build_overlay_rgba`, `blend` | `scripts/mammoth_interpretability.py:217,229,260,293` |
| molde de mosaico (`contacto`) | `scripts/galeria_mitosis_12.py:105` |

El `CKPTS` de `atencion_vs_anotaciones.py` está atado al pre-registro del B8 y **no se toca**: por
eso el driver es un script aparte que importa, que es el mismo patrón y el mismo motivo que llevó
a `auc_atencion_fold4.py` a existir.

**El confinamiento a la región va como intervalo por lámina.** El escalar
`Y_CORTE_REGION = 49920` de `scripts/techo_atencion_topk.py:45` es de la 129741 y **da vuelta la
B25-158899**, donde el patólogo anotó la región de arriba (`[0, 25600)`) y no la de abajo. Usar
`REGION_ANOTADA` cierra de paso un pendiente que el handoff arrastra.

---

## 7. Qué NO se verificó

- **Por qué las ocho láminas ausentes no están en los splits** aunque siete tengan etiqueta. No
  hace falta para el eje y no se investigó.
- **Si `sgaete` ya midió esto.** Su pipeline de atención contra anotaciones mide el mismo eje y el
  aviso sigue sin darse ([[sgaete-yolo-mitosis-solapamiento]]). El texto está en
  [`aviso_sgaete.md`](aviso_sgaete.md), para que lo mande Ernesto.
- **Nada del eje se corrió.** No hay un solo número nuevo en este documento: los que aparecen son
  del B8 o son conteos de archivos.
