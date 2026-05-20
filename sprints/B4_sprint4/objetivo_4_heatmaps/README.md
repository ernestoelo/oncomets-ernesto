# Objetivo 4 — Heatmaps cualitativos lado-a-lado

> Sprint B4. **Dependencia de Objetivos 1, 2 y 3**. Cualitativo por
> defecto; upgrade a **cuantitativo (IoU / Dice)** si Sebastián confirma
> disponibilidad de anotaciones de patólogo.

## Hipótesis

Para un conjunto pequeño (N=5–10) de slides representativas de cada
tarea prioritaria, los heatmaps de **attention map** de las tres
configuraciones (baseline B=8, B=16, DSMIL) deberían diferir
**visiblemente** en:

1. **Localización**: ¿el modelo "mira" la región diagnóstica anotada por
   el patólogo, o regiones espurias?
2. **Dispersión**: heatmaps difusos (atención repartida sobre toda la
   slide) vs heatmaps concentrados (foco claro en una región pequeña).
3. **Coincidencia con patrones focales conocidos**: en
   MicroCalcificaciones, las regiones positivas son pequeñas y discretas;
   el heatmap correcto debería **concentrarse** en ellas, no difuminarse.

Predicción cualitativa:

- **Baseline B=8** → heatmap difuso en tareas focales.
- **B=16** → ligeramente más concentrado (más samples top/bottom guían
  la atención).
- **DSMIL** → **substancialmente más concentrado** en tareas focales,
  porque la atención relacional al parche crítico colapsa la masa de
  atención.

## Métrica de éxito

### Modo cualitativo (default)

- **Visual side-by-side de heatmaps** para N slides × 3 configuraciones
  × {2–4 tareas prioritarias}.
- **Evaluación por inspección** (lo que vea Ernesto al mirar las
  imágenes). Reportar acuerdo / desacuerdo con la hipótesis de
  concentración.

### Modo cuantitativo (si hay anotaciones de patólogo)

- **IoU** y **Dice** del heatmap binarizado contra la máscara de
  anotación, agregado sobre las N slides.
- Criterio de éxito: **Δ IoU (DSMIL − baseline) > 0.05** en tareas
  focales.
- Threshold de binarización: definirlo de antemano (top-X% de attention,
  con X fijo). No optimizar sobre el threshold post-hoc — eso invalida
  la comparación.

## Generación de heatmaps

Sebastián tiene `create_heatmaps.py` en su codebase
(`/media/administrador/Storage1/sdonoso/clam_environ/create_heatmaps.py`).
**Reusar ese script** vía wrapper, no reimplementar.

Atención: el script usa el **attention map del slide-level classifier**,
no del instance classifier path. Es la salida natural de CLAM. Para
DSMIL, el "attention map" relevante es `β_i` (atención relacional al
parche crítico). Hay que adaptar el wrapper de heatmaps para emitir `β_i`
en el modo DSMIL.

## Dependencias

- [ ] **Objetivo 1, 2 y 3 ejecutados** con checkpoints disponibles para
      cada configuración.
- [ ] **Selección de N slides representativas** por tarea — criterio:
      slides con diversidad de presentación clínica, idealmente con
      anotación de patólogo si existe.
- [ ] **Anotaciones de patólogo** (PENDIENTE confirmar con Sebastián):
  - ¿Existen? ¿Para cuáles tareas? ¿Formato (máscara binaria, polígono,
    bbox)? ¿% de slides cubiertas?
- [ ] `create_heatmaps.py` legible y entendido para construir el wrapper
      DSMIL.

## Output esperado

```
objetivo_4_heatmaps/
├── README.md                       # este archivo
├── heatmaps_qualitative/
│   └── <task>/
│       └── <slide_id>/
│           ├── baseline_B8.png
│           ├── B16.png
│           └── dsmil.png
├── heatmaps_quantitative/          # solo si hay anotaciones
│   ├── annotations_snapshot.md     # qué anotaciones se usaron, fuente, % cobertura
│   └── iou_dice_table.md           # tabla por (task, config)
└── interpretacion.md               # narrativa de las observaciones para presentación
```

## Placeholder de tabla cuantitativa (si aplica)

| Tarea | IoU baseline | IoU B=16 | IoU DSMIL | Dice baseline | Dice B=16 | Dice DSMIL |
|---|---|---|---|---|---|---|
| MicroCalcificaciones | — | — | — | — | — | — |
| C.D.I. Necrosis | — | — | — | — | — | — |

## Riesgos identificados

- **Anotaciones inexistentes o muy escasas** → upgrade cuantitativo
  cae, queda solo lo cualitativo. Aceptable, pero menos defendible para
  Benjamín.
- **Heatmap de DSMIL no comparable directamente con CLAM**: la
  semántica del `β_i` (atención relacional) es diferente a `α_i`
  (atención absoluta). Cuidado en la interpretación visual — documentar
  la diferencia en `interpretacion.md`.
- **Cherry-picking**: si las N slides se eligen post-hoc para favorecer
  DSMIL, la comparación se invalida. Fijar las slides **antes** de
  generar los heatmaps de DSMIL.
