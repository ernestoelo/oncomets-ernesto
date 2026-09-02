# Los insumos del cruce CLAM × HoVer-NeXt, verificados

> **1-sep-2026, sesión 39.** Todo lo de acá se verificó **contra el archivo**, no contra un doc.
> Es el insumo del plan del 07/09 y el complemento de
> [`hechos_verificados.md`](hechos_verificados.md), que sigue vigente entero.
>
> Existe porque la reunión abrió una pregunta nueva ("¿mejora HoVer-NeXt si se le pasa la atención
> de CLAM?") y la respuesta depende de cuatro cosas que **ya estaban en disco** y que ninguna
> sesión anterior había mirado. **Cero código nuevo se escribió**; el único número calculado se
> hizo en memoria, sin escribir archivo.

---

## 1. Los mapas de atención YA EXISTEN, y son de `sgaete`

`/media/administrador/Storage1/sdonoso/clam_ensemble/attn_batch/json_out`

| | |
|---|---|
| dueño | `sgaete` (uid 1009), modo `0775` ⇒ **lectura sí, escritura no** |
| tamaño | **57.249** archivos, **18 GB** (más `json_out.tar.zst`, 5,7 GB) |
| cobertura | 3013 láminas × **19 tareas**, nombre `<slide>__<tarea>.json` |
| fecha | 21-jul-2026, job `attn_full` 4606, cerrado sin errores |
| generador | `clam_ensemble/attn_batch/batch_extract_attention.py` (único escritor) |

**Las doce anotadas están completas**, con las 19 tareas cada una, incluidas las dos que pidió
Ernesto: `grado_histologico_mitotic_rate_pth_balance` e `invasion_carcinoma_gate_pth_balance`.

Esquema, arreglos paralelos de largo `N` parches:

```
task · coords (x,y de level 0) · weights (suman 1) · patch_size · predicted_label · confidence
```

**No hay que generar nada y no hace falta GPU.** Es el mismo caso que `anotaciones/` en su
momento: material del proyecto que el repo nunca había referenciado.

### 1.a Qué atención es, exactamente

No es un `A[Y_hat]` de un fold. Es un **ensemble de los cinco folds** (`clam_ensemble/inference.py`,
`predict_task`, "Option-B"): por fold se hace softmax sobre parches de los logits crudos de la
atención con puerta, se toma la rama de la clase que **ese fold predijo**, y se promedian los cinco
**ponderados por la confianza de cada fold en la clase que predijo el ensemble**.

De ahí salen las tres propiedades que hay que **declarar en toda tabla** que use esta fuente:

1. **Rama predicha, no verdadera.** La rama que se lee decide el resultado
   ([[rama-de-atencion-decide-el-resultado]]).
2. **Contaminada por construcción.** El ensemble incluye los folds donde la lámina estuvo en
   `train`, y eso es la mayoría (tabla §3).
3. **Otra familia de checkpoints** (`_pth_balance`) que la del 0,890 de referencia
   (`_combined_5fold`). Los números no son intercambiables.

### 1.b Su campo `patch_size` NO es fiable

Da **127** en la 129741 y **64** en la B25-158899, donde nuestra geometría da **256** en las doce
(`parches_anotados_*.csv`). El `coords` del h5 **no trae `attrs`**, así que el script lo deriva, y
lo deriva mal. **Usar el nuestro**, moda del paso **por fila** ([[patch-size-desde-geometria-h5]]).
Las **coords sí coinciden exactamente** (mismo h5), así que el join es por coordenada y es exacto.

### 1.c Lo que `sgaete` mide en `anotaciones/` NO sale de acá

`anotaciones/atencion_vs_anotaciones.py` y su `resumen_atencion.csv` **recalculan** la atención
desde `results_modelo/<tarea>_s1/s_<fold>_checkpoint.pt` (fold 0, transformada a percentiles como
`create_heatmaps.py`). Son **dos fuentes distintas** para las mismas doce láminas: no cruzarlas sin
decirlo. El aviso de coordinación sigue pendiente ([`aviso_sgaete.md`](aviso_sgaete.md)).

---

## 2. Esa atención SÍ ordena los parches con mitosis

AUC de rango de la atención del `json_out` contra los parches con marca de `Mitosis`, calculado en
esta sesión en memoria (sin escribir nada), unidad **parche**:

| lámina | N parches | parches `Mitosis` | AUC cabeza mitosis | AUC cabeza gate |
|---|---:|---:|---:|---:|
| 129741 | 4799 | 28 | 0,942 | 0,830 |
| 126504 | 4410 | 28 | 0,778 | 0,795 |
| 128194 | 4570 | 21 | 0,947 | 0,881 |
| 124729 | 4334 | 7 | 0,924 | 0,805 |
| 124806 | 2705 | 7 | 0,815 | 0,701 |
| B25-158899 | 4697 | 6 | 0,612 | 0,676 |
| 144317 | 4769 | 4 | 0,877 | 0,800 |
| 164001 | 3796 | 4 | 0,669 | 0,858 |
| 106552 | 4659 | 2 | 0,979 | 0,888 |
| 103762 | 5203 | 2 | 0,740 | 0,757 |
| 109609 | 2957 | 2 | 0,586 | 0,278 |
| 110616 | 2933 | 2 | 0,852 | 0,990 |
| **media, doce** | | **113** | **0,810** | **0,772** |
| **media, nueve del primario** | | **103** | **0,809** | **0,745** |

**Es un go/no-go, no un resultado.** Sin IC, sin nulo, sin folds limpios y **contaminado**
(§1.a.2). Lo que habilita es que el eje no es un callejón sin salida. Las cuatro láminas con 2
parches marcados **no se leen solas**.

---

## 3. Cuánta contaminación arrastra el ensemble

Folds en que cada lámina **NO** estuvo en `train`, contra
`environ/splits_5fold_balanced/<tarea>_100/splits_{0..4}.csv`:

| lámina | `mitotic_rate_pth_balance` | `invasion_carcinoma_gate_pth_balance` |
|---|:-:|:-:|
| 103762 | 0 de 5 | 0 de 5 |
| 106552 | 1 | 2 |
| 109609 | 1 | 0 |
| 110616 | 1 | 3 |
| 124729 | 2 | 1 |
| 124806 | 1 | 2 |
| 126504 | 1 | 1 |
| 128194 | 1 | 0 |
| 129741 | 2 | 2 |
| 144317 | 3 | 0 |
| 164001 | 1 | 0 |
| B25-158899 | **5** (ausente) | **5** (ausente) |

Sólo la B25-158899 está limpia del todo, y es la única sin etiqueta. **Cuatro láminas están
contaminadas en los cinco folds** del gate. Por eso el plan corre en paralelo el brazo
`ckpt_limpio` sobre `_combined_5fold`, que sí tiene folds limpios por lámina
([`hechos_verificados.md`](hechos_verificados.md) §3).

### 3.a Del gate invasivo sólo tenemos el fold 0, y es nuestro

`results/b8_gate_invasivo/invasion_carcinoma_gate_pth_balance_clam_fold0_s1/s_0_checkpoint.pt`.
No hay 5-fold propio ni de Sebastián (`clam_environ/environ/results_modelo*` no tiene la tarea).
Y en ese fold **ocho de las doce están en `train`**: limpias sólo 110616 y 129741 (`test`), 124729
(`val`) y B25-158899 (ausente). ⇒ **para el gate, la única fuente con cobertura es el `json_out`.**

---

## 4. La geometría de HoVer-NeXt — la pregunta de Sebastián

Verificado en `hover_next_reference/`, con línea:

| qué | valor | dónde |
|---|---|---|
| tesela de entrada | **256 × 256 px** | `main.py:186` ("models are trained on 256x256") |
| paso entre teselas | `--overlap 0.96875` es un **stride**, no un solapamiento ⇒ **248 px** | `main.py:191`, `src/data_utils.py:205-207,596-622` |
| solapamiento físico | **8 px** (4 por lado), 3,1 %, sólo contexto | derivado de las dos anteriores |
| lo que escribe | el **centro 248 × 248** de cada tesela | `src/post_process_utils.py:649,663,283` |
| magnificación | **20×** con los pesos Lizard (40× con PanNuke) | `src/inference.py:111` |
| 20× nominal | **0,485 µm/px** | `src/constants.py:52-53` |
| canales de salida | **13** = 5 `inst` + 8 `cls` (7 clases + fondo) | `src/multi_head_unet.py:339-343`, `lizard_convnextv2_tiny/params.toml:6-7` |

**En nuestras láminas** (privado, **0,465 µm/px**, `np.isclose(0.465, 0.485, rtol=0.2)` ⇒ 20× ⇒
`ds_factor = 1`): **no hay remuestreo**, se lee level 0, y la tesela mide

> **119 µm de lado = 0,0142 mm²**, que es **exactamente el tamaño físico de un parche de CLAM**
> (también 256 px sobre la misma lámina).

Consecuencias que el plan usa:

- Enmascarar por parches de CLAM es enmascarar **a la granularidad de la tesela de HoVer-NeXt**.
- **3 mm² ≈ 212 parches.** La lámina entera va de 2705 a 5203 parches (**38 a 74 mm²**); las doce
  juntas, **49.832 parches = 706 mm²**.

---

## 5. El paper, y de dónde se baja

`README.md:9` del repo apunta a OpenReview, que **devuelve 403** (también su API). El mismo
artículo está en las actas de MIDL 2024, **PMLR v250**, y ahí sí responde:

```
https://proceedings.mlr.press/v250/baumann24a.html
https://raw.githubusercontent.com/mlresearch/v250/main/assets/baumann24a/baumann24a.pdf   (23 MB, 200)
```

Baumann, Dislich, Rumberger, Nagtegaal, Rodriguez Martinez, Zlobec — *HoVer-NeXt: A Fast Nuclei
Segmentation and Classification Pipeline for Next Generation Histopathology*, MIDL 2024. Título
verificado contra la página. **Ernesto autorizó bajarlo** el 1-sep para recortar su diagrama; la
autorización es **para este archivo**, no para el tema (política E.a).

---

## 6. Por qué filtrar no puede subir el conteo

HoVer-NeXt ya corrió sobre la **lámina entera** en las doce, así que "HoVer-NeXt + CLAM" es un
**subconjunto** de las 732 detecciones y de las 26 marcas acreditadas: **el conteo sólo puede
bajar**. Lo que la restricción compra es **área**, y por eso el plan mide una escalera de
presupuesto en mm² y no un top-K ([[techo-filtro-antes-de-correr]] P2.a.ter,
[[carga-fija-no-k-fijo]]). Corolario operativo: **no hay que re-correr nada**, el filtro es
post-hoc y **el brazo sin filtro sale gratis**.

---

## 7. Qué NO se verificó

- **Si el `json_out` reproduce el 0,890 del B8.** No puede: otra familia de checkpoints, otra
  definición de atención, otro reparto de folds. El gate exacto del plan es para el brazo
  `ckpt_limpio`.
- **Por qué `patch_size` del `json_out` da 127 y 64.** Se constató que no coincide y se decidió
  ignorarlo; la causa quedó sin investigar porque no cambia nada aguas abajo.
- **Si `sgaete` ya midió el cruce contra HoVer-NeXt.** El aviso sigue sin darse.
- **La escalera de área.** No se corrió: es lo que ejecuta la sesión siguiente.
