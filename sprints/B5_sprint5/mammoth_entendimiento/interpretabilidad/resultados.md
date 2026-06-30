# OBJ-A — Interpretabilidad de expertos/slots de MAMMOTH en mama (resultados)

> Generado 30-jun-2026. **Etapa 0: CPU, post-hoc, sin GPU, sin sbatch, sin reviewer**
> (inferencia sobre un checkpoint congelado — no toca modelo/training, regla 9 no aplica).
> Eje **entendimiento/interpretabilidad**, **ortogonal** al "0 palancas" (Hallazgo 12):
> NO es un intento de mejorar métrica. Responde con imágenes las preguntas 3/6/9 de
> Benjamín (reunión 29-jun) sobre "en qué se fija cada experto/slot".

## 1. Qué se corrió

| Campo | Valor |
|---|---|
| Script | `scripts/mammoth_interpretability.py` (adaptación propia del tutorial de la lib) |
| Checkpoint | `results/obj6_mammoth_binarias_cdis/clam_mammoth_cdis_f0_20260602_0006_s1/s_0_checkpoint.pt` |
| Tarea | `microcalcificaciones_en_cdis` (binaria `si`/`no`), brazo **mammoth drop-in** (`keep_slots=False`) |
| Slides | **4 slides TCGA-BRCA del test set de cdis fold 0** (en distribución): primaria **TCGA-E2-A14Q** + estabilidad cross-slide (§3.4) |
| — primaria | TCGA-E2-A14Q-01Z-00-DX1 — `y_true=1, y_pred=1, prob=0.98`, 24 942 parches |
| — positivo 2 | TCGA-D8-A1XF-01Z-00-DX1 — `y_true=1, y_pred=1, prob=0.98`, 12 961 parches |
| — negativo 1 | TCGA-BH-A0EE-01Z-00-DX1 — `y_true=0, y_pred=0, prob=0.23`, 20 747 parches |
| — negativo 2 | TCGA-UU-A93S-01Z-00-DX1 — `y_true=0, y_pred=0, prob=0.22`, 33 601 parches |
| Config Mammoth | `input_dim=512, dim=512, E=30, S=10, H=16, slot_dim=256, auto_rank→rank 8` |
| `slot_embeds` | `(30, 16, 10, 16)` = E×H×S×P (verificado contra el checkpoint real) |
| Dispatch | `(1, 24942, 30, 16, 10)` = (b, N, E, H, S) |
| Magnificación / parche | level-0 = 40x; parche = 512 px nivel-0 (256 px @ 20x) |
| Hardware | **CPU** (`CUDA_VISIBLE_DEVICES="" <env-python>`), ~minutos |

Comando (reproducible):
```bash
CUDA_VISIBLE_DEVICES="" /home/sdonoso/miniconda3/envs/clam_latest/bin/python \
  scripts/mammoth_interpretability.py \
  --ckpt results/obj6_mammoth_binarias_cdis/clam_mammoth_cdis_f0_20260602_0006_s1/s_0_checkpoint.pt \
  --h5  <clam_environ>/environ/features/h5_files/TCGA-E2-A14Q-01Z-00-DX1.*.h5 \
  --wsi <TCGA_dataset_curated>/TCGA-E2-A14Q-01Z-00-DX1/TCGA-E2-A14Q-01Z-00-DX1.*.svs \
  --out-dir sprints/B5_sprint5/mammoth_entendimiento/interpretabilidad/TCGA-E2-A14Q-01Z-00-DX1_cdis_f0 \
  --topk 8 --label "y_true=1,y_pred=1,prob=0.98"
```

## 2. Hallazgo metodológico (corrige el handoff §6)

El handoff asumía features en `.pt` y coords en un `.h5` **separado**. **Falso**: cada
h5 de `clam_environ/.../features/h5_files/` trae **`coords` (N,2) Y `features` (N,512)
juntas** → se leen ambas del mismo archivo (como el tutorial). No hace falta tocar los
`.pt`. El script lee `features`+`coords` del h5.

`dispatch_weights` se obtienen con `mammoth(x, return_weights=True)` y son
**independientes de `keep_slots`** (se calculan antes del combine) → la interpretabilidad
funciona igual para drop-in (obj6/obj2) y para keep_slots=True (obj3).

## 3. Resultados

### 3.1 Ruteo espacial: los expertos se reparten regiones distintas
**Figura `heatmap_montage.png`** (30 heatmaps de ruteo, ordenados por uso medio). Cada
experto enciende **zonas espacialmente distintas** de la misma slide — p. ej. e15/e12/e19
cargan la masa densa inferior-izquierda; e13 el borde superior-izquierdo; el patrón del
estroma laxo difiere del de los nidos epiteliales. Es la evidencia visual directa de que
**la capa única se reemplazó por especialistas que miran cosas distintas** (paper §2 + Fig 1).
*Caveat*: el color es **percentil por experto** (cada experto recibe todo el rango 0–1 por
construcción) → se ve "moteado"; muestra estructura relativa, no magnitud absoluta de uso.

### 3.2 Morfología por experto: especialización parcial pero reconocible
**Figuras `topk_subset_6experts.png`** (legible) y `topk_contact_sheet.png` (los 30).
Top-k parches recortados a **alta resolución del `.svs`** (`read_region`, no del thumbnail).
Lectura cualitativa **provisional** (pendiente sign-off patólogo — ver §5):

| Experto | Morfología dominante en sus top parches (provisional) |
|---|---|
| **e8** | Nidos epiteliales densos, núcleos basófilos apiñados → **epitelio tumoral** |
| **e26** | Estroma fibroso fuertemente eosinófilo (colágeno) → **estroma** |
| **e3** | Estructuras ductales con revestimiento epitelial → **epitelio ductal / pared de ducto** |
| **e15, e13, e20** | Mixtos (epitelio + zonas laxas/quísticas) → solapamiento esperado bajo ruteo suave |

Coincide con la tesis del paper (Fig 3 / §5.2): **la semántica morfológica vive en los
slots/expertos** (validada por patólogos: tumor, alvéolos, estroma, linfocitos, glóbulos
rojos) — **NO** en las cabezas (subespacios multi-head), y **emerge sin supervisión de
tejido**. Esto convierte el "no sé" de la reunión (pregunta 3: ¿qué es una cabeza?) en
evidencia: cabezas = subespacios; **slots/expertos = morfología** (respuestas §Q1, §Q6).

### 3.3 Carga de expertos ~uniforme (no hay expertos muertos ni dominantes)
**`expert_usage.csv`**: el uso medio por experto es **casi uniforme** (~2.0–2.2 × 10⁻⁴;
el máximo por construcción ≈ 1/(E·H·S·... ) repartido entre 30). No hay experto colapsado
ni acaparador. Es **consistente con el objetivo del ruteo suave del paper** (§2: evitar
*imbalanced expert utilization* de la asignación dura). La señal interpretable es **espacial**
(qué región/morfología, §3.1–3.2), **no** desbalance de carga.

### 3.4 Estabilidad cross-slide: las especializaciones se repiten entre slides
Como `slot_embeds` son **parámetros compartidos del modelo**, el experto `e8` es el
*mismo* en las 4 slides → si la especialización es real, debe elegir la misma morfología
en todas. **Figuras `cross_slide/expert_XX_crossslide.png`** (filas = las 4 slides, 2 pos
+ 2 neg). Inspeccionados e8 y e26:

| Experto | Tema morfológico repetido en las 4 slides (provisional) |
|---|---|
| **e8** | Regiones de **alta densidad nuclear / epitelio celular** (nidos apiñados) — estable |
| **e26** | **Estroma / interfaz epitelio-estroma / zonas fibrosas eosinófilas** — estable |

**Conclusión fina (importante para no malinterpretar):** los expertos rutean por
**MORFOLOGÍA, no por la etiqueta de la slide**. e8 enciende epitelio celular **también en
los negativos** (que igual son slides de mama con tumor; "negativo" es *cdis sin
microcalcificación*, no *sin tumor*). Es decir, **un experto es un detector de tejido, no
un detector de clase** — la decisión slide-level viene **después** (attention pooling +
clasificador de bag). Esto encaja con el diseño (el ruteo opera a nivel de parche/fenotipo)
y explica por qué mammoth no movió la métrica (Hallazgo 12): la especialización morfológica
existe, pero el cuello de botella del problema no está en la 1ª capa.

## 4. Cómo responde a Benjamín
- **Pregunta 3 (¿qué significa cada cabeza? ¿textura/forma/color?)** → con imágenes: la
  semántica reconocible está en los **expertos/slots** (e8 tumor, e26 estroma, e3 ducto),
  no en las cabezas. Confirma §Q1.
- **Pregunta 6 (los cuadros que se dividen en cada experto)** → el ruteo reparte parches a
  prototipos de slot; los top-k muestran qué fenotipo resume cada experto.
- **Pregunta 9 (en qué se fijan para una zona importante)** → heatmaps + top-k = "este
  experto se fija en epitelio tumoral; este otro en estroma".

## 5. Limitaciones / honestidad
- **4 slides** (2 pos + 2 neg, una sola tarea = cdis, un solo fold = f0). La coherencia
  morfológica es **cualitativa** y por ahora **mía, no de un patólogo**: la hipótesis OBJ-A
  pide **sign-off de Sebastián/patólogo** antes de afirmar etiquetas de tejido con certeza.
  Las etiquetas de §3.2 y §3.4 son **provisionales**. Solo inspeccioné a fondo e8/e26/e3/e15;
  los 30 expertos están en `topk_contact_sheet.png` para revisión.
- Heatmaps con color **percentil por experto** → buenos para ver estructura relativa, no
  magnitud. Iteración posible: colorear por score crudo con escala compartida o umbralizar al
  top-percentil.
- Solapamiento entre expertos (e15/e13/e20 mixtos) es **esperado** con ruteo suave + solo top-k.

## 6. Próximos pasos sugeridos (no ejecutados)
1. ✅ **Más slides + negativos** — hecho (§3.4: 4 slides, estabilidad confirmada). Pendiente:
   un caso de **otra tarea** (tejido/invasión) para ver si los temas se mantienen entre tareas.
2. **Sign-off de patólogo/Sebastián** sobre los top-k (cierra la métrica de la hipótesis).
3. Variante **`keep_slots=True`** (obj3): los 300 slots como cuello de botella explícito →
   ¿prototipos más nítidos por slot? (mismo script, `--keep-slots`).
4. Enlaza con **OBJ-B** (ablación de nº de cabezas H): ¿más cabezas = especializaciones más
   distintas o redundantes? (eso SÍ toca config → GPU + reviewer).

## 7. Archivos (provenance)
```
interpretabilidad/
├── resultados.md                       ← este documento
├── cross_slide/
│   └── expert_{08,26,03,15}_crossslide.png  ← top-5 de un experto fijo en las 4 slides (Fig 3.4)
├── TCGA-E2-A14Q-01Z-00-DX1_cdis_f0/    ← primaria (pos 0.98); las otras 3 misma estructura
│   ├── meta.json                       ← provenance completa (ckpt, config, dims)
│   ├── expert_usage.csv                ← uso medio por experto (ranking)
│   ├── heatmap_montage.png             ← 30 heatmaps de ruteo (Fig 3.1)
│   ├── heatmaps/expert_XX.png          ← 30 heatmaps individuales
│   ├── topk_subset_6experts.png        ← top-6 parches de 6 expertos (Fig 3.2, legible)
│   ├── topk_contact_sheet.png          ← contact sheet de los 30 expertos × top-8
│   └── topk_patches/expert_XX_rank_YY.png  ← 240 parches alta-res (30×8)
├── TCGA-D8-A1XF-01Z-00-DX1_cdis_f0/    ← positivo 2 (0.98)
├── TCGA-BH-A0EE-01Z-00-DX1_cdis_f0/    ← negativo 1 (0.23)
└── TCGA-UU-A93S-01Z-00-DX1_cdis_f0/    ← negativo 2 (0.22)
```
Referencia técnica: `../respuestas_preguntas_benjamin.md` (§0 dims, §Q1 cabezas, §Q6 herramienta).
```
