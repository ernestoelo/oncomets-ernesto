# Encargo 1 (brazo disponible hoy) — la atención del gate de carcinoma invasivo

> Medido el **21-ago-2026**, CPU post-hoc, sin GPU. Salidas:
> `results/b8_hovernext_129741/{interp/invasion_carcinoma_gate_pth_balance,auc_gate_f0,techo_atencion_gate,cruce_marcas_gate}/`.
> Selección: [interp_slides_gate.json](../hovernext_129741/interp_slides_gate.json).

Sebastián pidió repetir la cadena con el checkpoint de **carcinoma invasivo** y comparar
contra la que ya corrimos (que era **CDIS `_ci_reform`, fold 4**, no invasivo). No hizo falta
volver a correr HoVer-NeXt: la 129741 se corrió entera y el filtro se aplica **post-hoc**
sobre la salida (patrón P2.a.ter). Lo único nuevo es la atención.

**Este documento cubre medio encargo.** El checkpoint del gate que hay en disco es
**Mammoth**, no CLAM plano — su `experiment.txt` dice `clam_mb` y es falso, el `state_dict`
trae `attention_net.0.mammoth.*` ([[checkpoint-familia-se-lee-del-statedict]]). El CLAM plano
lo entrena **B3** sobre el mismo `--split_dir`, y ahí la comparación queda CLAM contra CLAM,
que es lo que se pidió.

## 1. Qué se midió, y sobre qué fold

| | CDIS (ya medido) | gate de invasivo (nuevo) |
|---|---|---|
| tarea | `carcinoma_ductal_insitu_presente_ci_reform` | `invasion_carcinoma_gate_pth_balance` |
| fold | **4** | **0** |
| brazos | CLAM + Mammoth | **solo Mammoth** (el CLAM plano no existe) |
| clase verdadera de la 129741 | `si` | `invasivo` |
| predicción del modelo | — | `invasivo`, p = **1,000** |

Los folds difieren **a propósito**: en cada tarea el fold 0 / 4 es donde la 129741 cae en
**test** y no fue vista en entrenamiento. Verificado en
`splits_5fold_balanced/invasion_carcinoma_gate_pth_balance_100/splits_0.csv`.

El `label_dict` sale de `--auto-label-dict` (alfabético, `label_dict: {}` en `main.py:371`):
`invasivo`=0, `no_invasivo`=1. Confirmado contra el `probability_log` del fold 0 de `sgaete`:
la 129741 sale `true_label=0` con `prob_class_0=0,99999`.

**Se lee la rama de la clase verdadera y se registra la predicha.** Acá coinciden (el modelo
acierta con p=1,000), así que la elección no cambia nada — a diferencia del caso de necrosis,
donde `sgaete` leyó la rama predicha, que estaba equivocada, y obtuvo AUC 0,382.

## 2. Por AUC, el gate parece equivalente

AUC de la atención como detector de parches anotados, universo = región anotada (2496
parches), cabeza de la clase verdadera:

| grupo | n | **gate · Mammoth** | CDIS · Mammoth | CDIS · CLAM |
|---|---|---|---|---|
| Mitosis | 28 | **0,865** (0,778–0,951) | 0,919 (0,848–0,989) | 0,876 (0,793–0,960) |
| Núcleos alto grado | 13 | 0,869 | 0,839 | 0,843 |
| Tumor | 48 | 0,831 | 0,840 | 0,717 |
| necrosis | 18 | 0,528 | 0,828 | 0,750 |
| Stroma | 12 | 0,531 | 0,603 | 0,406 |
| Immune cells | 23 | 0,339 | 0,440 | 0,592 |
| Tejido Adiposo | 27 | 0,042 | 0,061 | 0,573 |

En Mitosis los tres intervalos se solapan de sobra: por AUC **no se distinguen**. El nulo por
traslación rígida da p = 0,0008 para el gate, o sea que la señal es real.

## 3. Por top-K, el gate es claramente peor — y ésa es la comparación que importa

Marcas que caen dentro del top-K por atención, confinado a la región anotada (denominador 26
marcas):

| K | % región | área mm² | **gate · Mammoth** | CDIS · Mammoth | CDIS · CLAM |
|---|---|---|---|---|---|
| 20 | 0,8 % | 0,28 | **0/26** | 2/26 | 1/26 |
| 50 | 2,0 % | 0,71 | **0/26** | 4/26 | 2/26 |
| 100 | 4,0 % | 1,42 | **1/26** | 14/26 | 12/26 |
| 189 | 7,6 % | 2,68 | **8/26** | 18/26 | 15/26 |
| 300 | 12,0 % | 4,25 | **11/26** | 22/26 | 19/26 |
| 500 | 20,0 % | 7,08 | **17/26** | 23/26 | 23/26 |
| 750 | 30,0 % | 10,63 | 26/26 | 26/26 | 24/26 |

**Es el patrón P2 otra vez, y de manual**: AUC casi igual (0,865 vs 0,919) y top-K muy
distinto. La explicación está en el percentil, no en el AUC — el gate deja los parches con
mitosis en el **percentil 86**, y CDIS-Mammoth en el **95**. El AUC resume todos los
umbrales; el top-K es uno solo, y de los extremos.

**Chequeo de sanidad, y pasa**: en K = 2496 (región entera) los dos brazos convergen a
**13/26**, que es el factor de detección solo. Si difirieran habría bug en el enmascarado.

## 4. Qué se responde y qué no

- **Se responde**: con el checkpoint de invasivo la cadena **recorta peor**. Para poner las
  mismas marcas delante del patólogo hay que darle bastante más superficie.
- **No se responde todavía**: si eso es propiedad de **la tarea** (invasivo vs CDIS) o del
  **brazo** (Mammoth vs CLAM). Con un solo brazo en el gate no se pueden separar. **B3
  entrena el CLAM plano sobre el mismo split y lo separa.**
- **No cambia el 13 de 26.** La detección es el factor que manda desde K=189, y no depende de
  qué checkpoint recorta. Cambiar de tarea de atención mueve el área, no las marcas
  (P2.a.ter).
- Una lámina, 26 marcas, un checkpoint por brazo: sin sd entre checkpoints. Las dos
  incertidumbres del caso están en [[auc-atencion-dos-incertidumbres]].
