# Tabla por tarea — interpretabilidad CLAM vs Mammoth (Sprint 7)

Magnificacion **fisica** leida con openslide de cada WSI (no del `level`
ni del nombre de la cohorte). Entrenamiento pareado, job 4589.

## Tipo histologico (3 clases)

- **Tarea (task)**: `tipo_histologico_3clases_ci`
- **Dataset**: n = 2027 WSI · carcinoma_invasivo_tipo_no_especifico: 1610 · carcinoma_lobulillar_invasivo: 240 · otros: 177
- **Cohortes**: HistAI: 997 · TCGA: 859 · privado (Environ): 171
- **Fold usado para interpretabilidad**: 0 (5-fold pareado)

| Slide (ID) | Cohorte | Etiqueta del patologo | um/px (nivel 0) | Magnif. equiv. | Fuente del MPP | Dimensiones nivel 0 |
|---|---|---|---|---|---|---|
| `TCGA-AO-A12D-01Z-00-DX1` | TCGA | carcinoma_invasivo_tipo_no_especifico | 0.4992 | ~20x | openslide.mpp-x | 55775x42281 |
| `TCGA-AC-A8OS-01Z-00-DX1` | TCGA | carcinoma_lobulillar_invasivo | 0.2520 | ~40x | openslide.mpp-x | 46043x46426 |
| `TCGA-E9-A1NE-01Z-00-DX1` | TCGA | otros | 0.2485 | ~40x | openslide.mpp-x | 49794x65923 |

## Carcinoma ductal in situ presente

- **Tarea (task)**: `carcinoma_ductal_insitu_presente_ci_reform`
- **Dataset**: n = 862 WSI · no: 132 · si: 730
- **Cohortes**: HistAI: 240 · TCGA: 500 · privado (Environ): 122
- **Fold usado para interpretabilidad**: 0 (5-fold pareado)

| Slide (ID) | Cohorte | Etiqueta del patologo | um/px (nivel 0) | Magnif. equiv. | Fuente del MPP | Dimensiones nivel 0 |
|---|---|---|---|---|---|---|
| `TCGA-A7-A4SB-01Z-00-DX1` | TCGA | no | 0.2480 | ~40x | openslide.mpp-x | 90439x80048 |
| `TCGA-D8-A1XB-01Z-00-DX2` | TCGA | si | 0.2527 | ~40x | openslide.mpp-x | 95615x82390 |

## Invasion linfovascular

- **Tarea (task)**: `invasion_linfatica_vascular_ci_reform`
- **Dataset**: n = 836 WSI · ausente: 470 · presente: 366
- **Cohortes**: HistAI: 133 · TCGA: 563 · privado (Environ): 140
- **Fold usado para interpretabilidad**: 0 (5-fold pareado)

| Slide (ID) | Cohorte | Etiqueta del patologo | um/px (nivel 0) | Magnif. equiv. | Fuente del MPP | Dimensiones nivel 0 |
|---|---|---|---|---|---|---|
| `TCGA-D8-A1XW-01Z-00-DX2` | TCGA | ausente | 0.2527 | ~40x | openslide.mpp-x | 111551x77773 |
| `TCGA-D8-A1X5-01Z-00-DX2` | TCGA | presente | 0.2527 | ~40x | openslide.mpp-x | 101591x81748 |
