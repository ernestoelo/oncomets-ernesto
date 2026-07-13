# Interpretabilidad de expertos de Mammoth — guía para replicar la extracción

> Guía para reproducir los **mapas de calor de ruteo por experto** y los **top-k parches
> por experto** de Mammoth (`CLAM_MB_Mammoth`) sobre una WSI de mama. Son las figuras que
> aparecen en el deck de la reunión (slides 10-11). Corre en **CPU, post-hoc**, sobre un
> checkpoint ya entrenado: no reentrena ni toca el modelo. Escrita para que Sebastián (u
> otra persona del equipo) la replique sin reconstruir el contexto.

## Qué produce

Para una WSI, a partir de su checkpoint mammoth + su `.h5` (features+coords) + su `.svs`:

1. **Heatmap de ruteo por experto** (30 PNG + un `heatmap_montage.png`): pinta la lámina
   según cuánto el router manda cada parche a cada experto → **dónde** se activa cada uno.
2. **Top-k parches por experto** (`topk_patches/` + `topk_contact_sheet.png`): recorta a
   alta resolución los parches que más activa cada experto → **qué morfología** mira.
3. **`expert_usage.csv`**: ranking de los 30 expertos por uso medio.
4. **`slot_usage.csv` + `slot_usage_top.png`** (añadido en B7): ranking de los **300 slots
   (E·S)** por su **peso de ruteo** (softmax `combine_weights` sobre los slots). Responde
   "cuáles slots son los más activados" — distinto del top-k de parches por experto.
5. **`meta.json`**: provenance (checkpoint, h5, wsi, etiqueta de slide, config, nº parches).

## Dónde está la presentación

- Deck: `sprints/B6_sprint6/presentacion_viernes/` — generador `generate_b6_deck.py`,
  convenciones `convenciones_deck_b6.md`. El `.pptx` es un derivado gitignored (se
  regenera con el script). (En B7 el deck se re-basa sobre el template de Sebastián; ver
  `sprints/B7_sprint7/correcciones_deck.md`.)

## Dónde están las figuras de los expertos (trackeadas y pusheadas)

- **Slide 10** (ruteo espacial + top-k): `interpretabilidad/TCGA-E2-A14Q-01Z-00-DX1_cdis_f0/`
  → `heatmap_montage.png`, `topk_subset_6experts.png`.
- **Slide 11** (mismo experto cross-slide): `interpretabilidad/cross_slide/`
  → `expert_08_crossslide.png`, `expert_26_crossslide.png`.
- Hay `heatmap_montage.png` de 4 slides TCGA-BRCA en carpetas hermanas
  (`TCGA-BH-A0EE…`, `TCGA-D8-A1XF…`, `TCGA-UU-A93S…`, `TCGA-E2-A14Q…`).

## Cómo generarlas

Script: `scripts/mammoth_interpretability.py` (trackeado). **Nunca `python` a secas**
(workaround B del entorno): usar el binario absoluto del env y `CUDA_VISIBLE_DEVICES=""`
para forzar CPU.

```bash
cd /media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto
CUDA_VISIBLE_DEVICES="" /home/sdonoso/miniconda3/envs/clam_latest/bin/python \
  scripts/mammoth_interpretability.py \
    --ckpt <checkpoint CLAM_MB_Mammoth .pt> \
    --h5   <features+coords .h5> \
    --wsi  <WSI .svs> \
    --out-dir <carpeta de salida bajo clam_testing2/> \
    --label "task=...,y_true=...,fold=..." \
    [--keep-slots]   # solo para checkpoints obj3 (keep_slots=True). Default: drop-in.
```

### Tiempo real medido (para no venderlo sin dato)

Corrida cronometrada el 13-jul-2026 (CPU, este server): **563 s ≈ 9.4 min** para una WSI
TCGA de **10 401 parches** (invasión linfovascular, checkpoint `obj2_mammoth` fold 0). El
grueso del tiempo es el paso 5 (recortar los top-k a alta resolución leyendo el `.svs`);
el forward de Mammoth y los heatmaps son segundos. Escala ≈ con el nº de parches.

## Insumos y config

- **Checkpoints mammoth** disponibles: `results/obj6_mammoth_binarias_*` (microcalc
  carcinoma/cdis/tejido), `results/obj2_mammoth/…` (invasión, cdis-patrones),
  `results/obj3_mammoth_keepslots/…` (usar `--keep-slots`).
- **h5** (features CONCH 512 + coords, mismo archivo): `clam_environ/environ/features/h5_files/`
  (READ-ONLY).
- **WSI .svs**: TCGA en `/media/administrador/Storage1/sdonoso/TCGA_dataset_curated/<slide_id_corto>/`
  (READ-ONLY; el slide_id del CSV trae el UUID, el dir usa la forma corta).
- **Config Mammoth** (hardcodeada en el script, = la nuestra CONCH 512): `input_dim=512`,
  `num_experts=30`, `num_slots=10`, `num_heads=16`, `slot_dim=256`, `auto_rank → 8`.
  Prefijo del sub-state-dict: `attention_net.0.mammoth.`.

## Caveat de honestidad (importante)

Los **nombres de tejido** de los expertos (por ejemplo "experto 8 = epitelio tumoral")
son **interpretación visual nuestra**, mirando los parches top-k. **No** son anotación de
patólogo: el modelo entrega la etiqueta **clínica de slide**, no anotación de tejido por
parche. El hallazgo de fondo (cada experto rutea consistentemente por una morfología, y lo
hace igual en slides de etiqueta distinta → detecta tejido, no clase) es
**label-independiente** y se sostiene aunque el nombre sea impreciso. Falta el **sign-off
de un patólogo** sobre los nombres. Ver `resultados.md` + memoria `mammoth-interpretabilidad-objA`.

## Referencia

- Detalle de adaptaciones, hallazgos y las 4 slides TCGA-BRCA: `resultados.md` (esta carpeta).
- Contexto del mecanismo (cabezas/expertos/slots, dos softmax): `../respuestas_preguntas_benjamin.md`
  §0 + `sprints/B7_sprint7/preguntas_resueltas.md`.
