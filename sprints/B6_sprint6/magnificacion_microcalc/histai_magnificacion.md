# HistAI — magnificación física (resolución del pendiente §7.1)

> Cierra el pendiente #1 de `investigacion_magnificacion.md` §7: HistAI sin MPP confiable.
> Verificado read-only con openslide sobre 6 WSI reales de HistAI (10-jul-2026). Sin GPU.

## Hallazgo: el MPP de HistAI NO es recuperable del metadata

| Propiedad | Valor | Lectura |
|---|---|---|
| `openslide.vendor` | `generic-tiff` | TIFF piramidal genérico, **sin tags de escáner** (no Aperio/Ventana) |
| `openslide.mpp-x/y` | `1000` | **bogus** — derivado de `tiff.XResolution=10 px/cm` (placeholder) → 1 cm/10 = 1000 µm/px |
| `tiff.ResolutionUnit` | `centimeter` | resolución = 10 px/cm en ambos ejes = valor por defecto, no real |
| `objective-power` | (ausente) | sin tag de aumento |
| `openslide.comment` | `{"shape": [H, W, 3]}` | solo la forma; ningún campo de calibración |

Los tags de resolución (10 px/cm) son **placeholders** que openslide traduce a `mpp=1000`. No hay
señal física recuperable — es la conversión a un TIFF genérico que descartó la calibración original.

## Estimación por dimensiones — ambigua entre 20× y 40×

level0 de 6 slides: 47333×86323, 20844×74277, …, 64239×39241. Un lado de ~86000 px:
- a **0.25 µm/px (40×)** → 21.6 mm (razonable para una sección de tejido)
- a **0.50 µm/px (20×)** → 43 mm (largo, pero posible)

La pirámide es estándar (downsample 1/2/4/8/16/32, tile 4096). El heurístico de dimensiones favorece
**débilmente ~40×** (21 mm es más típico que 43 mm para una sección) pero **no es concluyente** — el
tamaño de la sección varía por caso.

## Decisión para el piloto de magnificación

HistAI es **minoría (49/333 = 15%)** del dataset de microcalc; la señal es TCGA-heavy (207) +
privado (77) = **284/333 = 85% con µm/px resuelto**. Por eso HistAI **no bloquea** el diseño:

1. **Piloto (default):** correr la pirámide sobre **TCGA + privado** (284 slides, µm/px conocido).
   HistAI se **excluye de la re-extracción multi-escala** del piloto — su single-scale actual queda
   como está. El wrapper (`extract_multiscale_features.py`, `resolve_mpp`) ya **salta** cualquier slide
   sin MPP fiable (fallback `None`) → HistAI cae fuera sin código extra.
2. **Si el piloto valida la tubería:** resolver HistAI por (a) preguntar al proveedor / doc HistAI,
   (b) calibrar por tamaño de estructura conocida (núcleo/eritrocito ~7 µm sobre un tile real), o
   (c) **asumir 40× provisional** (favorecido por dimensiones) con caveat, y re-extraer sus 49 slides.

**Implicación de pairing:** como el baseline single-scale y el brazo multi-escala **comparten los
mismos splits k=5**, excluir HistAI del brazo multi-escala exige excluir esas 49 slides **también del
baseline** en la comparación paired (o marcarlas), para que el Δ pareado se calcule sobre el MISMO
conjunto. Se resuelve en el pre-registro (subset común TCGA+privado). No afecta el argumento clínico
de escala (§2–§5 del doc de investigación).

## Estado

Pendiente §7.1 **resuelto operativamente** (no bloquea). Actualiza [[cohortes-magnificacion-fisica]]:
HistAI = `generic-tiff`, MPP no recuperable, heurístico de dims ~40× no concluyente, excluido del piloto.
