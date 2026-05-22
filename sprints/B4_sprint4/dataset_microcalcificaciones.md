# Dataset microcalcificaciones — cuentas verificadas y decisión de entrenamiento

> Verificado **read-only** el 22 may 2026 sobre `clam_environ/environ/`
> (CRLF en los CSV de cohorte: limpiar con `tr -d '\r'` al parsear `$NF`).
> Fuente de verdad para qué dataset usar en cada prueba de microcalcificaciones.

## Dónde vive todo (paths absolutos, READ-ONLY)

```
clam_environ/environ/
├── csv/          dataset_microcalcificaciones_label.csv            (8 clases, COMBINADO = priv+TCGA+HistAI, 3072)
│                 dataset_microcalcificaciones_en_{carcinoma_invasivo,cdis,tejido_no_neoplasico}_label.csv  (binarios, 333 c/u)
├── csv_privado/  dataset_microcalcificaciones_label.csv            (solo Environ, 533)
├── csv_tcga/     dataset_microcalcificaciones_label.csv            (solo TCGA, 864)
├── csv_histai/   dataset_microcalcificaciones_label.csv            (solo HistAI, 1675)
├── csv_balance/  dataset_microcalcificaciones_en_{...}_label.csv   (HOY byte-idéntico a csv/ → 333; placeholder)
├── splits/
│   ├── microcalcificaciones_100/                  (privado, 533)
│   ├── microcalcificaciones_combined_100/         (priv+TCGA, 1397)
│   ├── microcalcificaciones_pth_100/              (priv+TCGA+HistAI, 3072)
│   ├── microcalcificaciones_en_{tejido}_pth_100/          (binarios, 333)
│   └── microcalcificaciones_en_{tejido}_pth_balance_100/  (HOY = 333; placeholder)
└── features/pt_files/   ← features CONCH 512-dim por slide ([N_parches, 512] float32)
```

## Cuentas por cohorte (8 clases)

| Cohorte | total | `no_identificado` | **identificadas** |
|---|---|---|---|
| privado (`_100`) | 533 | 456 | **77** |
| combined (priv+TCGA) | 1397 | 1113 | **284** |
| `_pth` (priv+TCGA+HistAI) | 3072 | 2739 | **333** |

> El "~548" del doc V4 ≈ **cohorte privada** (533 hoy; deriva de snapshot de 15).
> La expansión privado→`_pth` fue **89% `no_identificado`** — no aporta a las
> clases raras.

## Distribución de clases (combinado `csv/`, 8 clases)

```
2739 no_identificado          161 en_tejido_no_neoplasico     89 en_cdis
  38 en_carcinoma_invasivo     15 cdis+tejido                  13 carc+tejido
  11 carc+cdis                  6 carc+cdis+tejido (la triple, ultra-rara)
```

## Tareas binarias (`no_identificado` excluido → 333 slides)

| Tarea | total | positivos (`si`) | negativos (`no`) |
|---|---|---|---|
| `..._en_carcinoma_invasivo` | 333 | 68 | 265 |
| `..._en_cdis` | 333 | 121 | 212 |
| `..._en_tejido_no_neoplasico` | 333 | 195 | 138 |

Identificadas por cohorte (de dónde sale la señal de los binarios):
**privado 77 · TCGA 207 · HistAI 49**. El grueso útil es **TCGA**.

## Decisión de entrenamiento (post-reunión 22 may 2026)

| Escenario | Dataset a usar | Por qué |
|---|---|---|
| Binarios — baseline actual / comparar DSMIL | **333 identificadas** (`_pth` sin `no_identificado`) | todo lo identificado; apples-to-apples; dio carcinoma 0.78 |
| Binarios — siguiente paso | **`balanced_pth_100`** (cuando exista) | negativos acotados ≤10×; ayuda a CDIS/tejido **si** `no_identificado` ≈ "ausente" |
| 8-clases / reproducir V4 | **~548 privado (533)** | lo que usó Sebastián |
| Validación final de un modelo | **`_pth` 3072** | regla de Sebastián: completo solo para pruebas finales |

**Por qué NO entrenar los binarios solo con el privado:** privado tiene solo
**77 identificadas** → inentrenable repartido en 3 tareas. Los binarios
necesitan al menos `combined` (284) o `_pth`-identificado (333).

**Regla DSMIL:** entrenar DSMIL y el baseline CLAM sobre **el mismo dataset**
(las 333 binarias) para que la comparación sea limpia (exigencia de Sebastián).

**Pendiente de confirmar:** qué es `no_identificado` (¿ausente, o no anotado?)
— define si los negativos del `balanced` son señal o ruido de etiqueta.
