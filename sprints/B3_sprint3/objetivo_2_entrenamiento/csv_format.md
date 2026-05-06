# Formato de los CSV del pipeline CLAM

Documenta los archivos `.csv` que entran y salen del pipeline tal como
los usa Sebastián (validado contra el código real, 5 mayo 2026).

## Vista general del flujo

```
WSI (.svs)
  └─ create_patches_fp.py ──► patches/<slide_id>.h5  (coord+meta de parches)
                              process_list_autogen.csv  (índice de WSI procesadas)

[informe PDF de cada WSI]
  └─ extractor_caracteristicas/modeloCaracteristicas.py ──► <slide_id>.json (ground truth crudo)

JSONs + WSIs
  └─ environ_utils.py ──► dataset_<task>_label.csv     (case_id, slide_id, label)

patches + WSI
  └─ extract_features_fp.py ──► features/pt_files/<slide_id>.pt   (Tensor [N_patches, D])
                                features/h5_files/<slide_id>.h5   (idem en h5)

dataset_<task>_label.csv
  └─ create_splits_seq.py --task <t> ──► environ/splits/<task>_100/splits_0.csv
                                          environ/splits/<task>_100/splits_0_bool.csv
                                          environ/splits/<task>_100/splits_0_descriptor.csv

splits + features + main.py
  └─ python main.py ──► results_modelo/<exp_code>_s1/
                          ├─ s_0_checkpoint.pt
                          ├─ s_0_results.pkl
                          ├─ split_0_results.pkl
                          ├─ summary.csv
                          └─ task_X.txt (config dump)
```

## CSVs de input

### 1. `environ/csv/dataset_<task>_label.csv` (ground truth)

Tres columnas: `case_id, slide_id, label`. Una fila por WSI etiquetada.

```csv
case_id,slide_id,label
patient_0,AP_494_OT_1808_14-2715_MxBr_89_HE,carcinoma invasivo de tipo no específico (ductal)
patient_1,AP_494_OT_1814_46875_MxBr_55_HE,carcinoma invasivo de tipo no específico (ductal)
```

- **`case_id`**: identificador de paciente (un mismo paciente puede aportar
  varias slides — el split garantiza que todas las slides de un paciente
  caen en la misma partición).
- **`slide_id`**: nombre de la WSI sin extensión. Debe coincidir con el
  nombre del `.pt` en `features/pt_files/<slide_id>.pt`.
- **`label`**: string libre. Si en `main.py:TASK_CONFIGS[task]['label_dict']`
  hay un mapeo `{label_string: int}`, se usa eso. Con `--auto-label-dict`
  se ignora el `label_dict` y se generan IDs en orden alfabético sobre los
  labels únicos presentes en este CSV.

### 2. `environ/splits/<task>_100/splits_0.csv` (split principal)

Generado por `create_splits_seq.py`. Tres columnas paralelas, una por
partición. **NO es row-aligned**: cada columna es una lista independiente
de `slide_id`.

```csv
,train,val,test
0,AP_494_OT_1808_14-2715_MxBr_89_HE,AP_494_OT_1808_15-0559_MxBr_107_HE,AP656_OT2122_Br0247_HE
1,AP_494_OT_1814_46875_MxBr_55_HE,AP473_OT1760_14143_MxBr_31_HE,AP_494_OT_1808_14-2524_MxBr_87_HE
2,OT1808_AP_494_46875_MxBr_55,AP_494_OT_1808_15-0742_MxBr_112_HE,AP_494_OT_1808_14-2443_MxBr_84_HE_Br0326
3,OT_1788_AP_487__12073_1R1_MxBr_06_HE,,AP_494_OT_1808_14-2443_MxBr_84_HE
```

- Primera columna sin nombre = índice posicional dentro de la partición.
- Si una partición es más corta que las otras, las celdas faltantes
  quedan vacías (ver fila 3 col `val` en el ejemplo).
- El sufijo `_100` en el directorio = `label_frac=1.0` (el 100% de los
  labels disponibles entran al split, vs `_75`, `_50`).

### 3. `environ/splits/<task>_100/splits_0_bool.csv` (representación booleana)

Misma información que `splits_0.csv` pero en formato wide: una fila por
slide y tres columnas booleanas indicando partición.

```csv
,train,val,test
AP_494_OT_1808_14-2715_MxBr_89_HE,True,False,False
AP_494_OT_1814_46875_MxBr_55_HE,True,False,False
```

Útil para verificar que cada slide aparece en exactamente una partición.

### 4. `environ/splits/<task>_100/splits_0_descriptor.csv` (resumen por clase)

Resumen de cuántas slides de cada clase entran a cada partición.

```csv
,train,val,test
carcinoma invasivo de tipo no específico (ductal),30,3,4
carcinoma lobulillar invasivo,4,0,0
```

> **Nota crítica para `tipo_histologico`**: aunque `TASK_CONFIGS` declara
> 18 clases en `label_dict`, en este split solo aparecen 2 (las únicas
> presentes en el CSV de labels). Con `--auto-label-dict`, el modelo se
> entrena efectivamente como **binario**, no como 18-clase. La clase
> minoritaria queda 4/0/0, lo que limita lo informativo de la métrica
> de validación.

### 5. `environ/features/pt_files/<slide_id>.pt`

Tensor de PyTorch shape **`[N_patches, D]`** float32.

- Para `environ/features/pt_files/`: `D=1024` (extractor proyectado a 1024).
- Para `environ/features_CONCH/pt_files/`: `D=512` (CONCH-v1 nativo).
- `N_patches` varía por slide (ej. 10205 en
  `AP473_OT1760_1199_1_1-6_MxBr_02_HE.pt`).

`main.py` arma el path como
`<data_root_dir>/<TASK_CONFIGS[task].data_dir>/pt_files/<slide_id>.pt`,
es decir con `--data_root_dir environ/` y `data_dir: 'features'`,
levanta de `environ/features/pt_files/<slide_id>.pt`.

## CSVs de output (post-training)

Bajo `<results_dir>/<exp_code>_s<seed>/`:

- **`summary.csv`** — una fila por fold con columnas `fold, val_loss,
  val_error, val_auc, test_loss, test_error, test_auc`.
- **`split_0_results.pkl`** — pickle con predicciones detalladas
  (probas y labels) del fold 0.
- **`s_0_checkpoint.pt`** — pesos del best-model del fold 0 (criterio
  early stopping).
- **`task_X.txt`** — dump textual de los args usados.

## Variantes y dependencias importantes

- **`--auto-label-dict`** se usa en TODOS los runs de Sebastián. Sobrescribe
  `label_dict` de `TASK_CONFIGS`. Solo entran clases con ≥1 muestra en el
  CSV.
- **`--k 1`** = un solo fold (no k-fold real). Para cross-validation real,
  poner `--k 10`. Sebastián usa `--k 1` por costo computacional.
- **`--weighted_sample`** se activa siempre — corrige el desbalance
  muestreando minoritarias con mayor probabilidad.
- **`--early_stopping`** corta cuando `val_loss` no mejora (paciencia y
  delta están hardcodeados en `core_utils.py`, no expuestos por CLI).
