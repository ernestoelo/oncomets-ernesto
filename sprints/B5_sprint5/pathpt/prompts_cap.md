# Prompts anclados en los protocolos CAP — extracción + provenance

> **Para qué:** los prompts de PathPT comparan parches contra **frases clínicas**. Esta
> extracción ancla esas frases en la **fuente oficial** — los protocolos del College of
> American Pathologists (CAP) — en vez de redactarlas a ojo. Es la validación clínica que
> la Etapa 0 dejó pendiente (go/no-go §9: "iterar los prompts con validación clínica
> Sebastián/CAP"). El **sign-off clínico final es de Sebastián**; acá se transcribe el texto
> oficial (no se inventa morfología). [[cap-fuente-clases-tareas]]
>
> **Fuentes** (en `papers/`):
> - `Breast.Invasive.Bx_1.2.0.0.REL_CAPCP.pdf` — *Biopsy Specimens from Patients with
>   Invasive Carcinoma of the Breast* (v1.2.0.0, mar-2023). **← la relevante para PathPT**
>   (morfología H&E: necrosis, grado/mitosis, patrones, microcalc, invasión).
> - `Breast.Bmk_1.6.0.0.REL.CAPCP.pdf` — *Biomarker Reporting* (v1.6.0.0, mar-2025).
>   **NO aplica a PathPT**: es **inmunohistoquímica/molecular** (ER, PgR, HER2 IHC/ISH,
>   Ki-67) — tinciones, no morfología H&E. CONCH/PathPT trabajan sobre H&E. Queda como
>   referencia para tareas futuras de biomarcadores (Ki-67 ≈ proliferación, análogo
>   conceptual a la tasa mitótica pero por IHC, no H&E).

---

## 1. NECROSIS (tarea primaria de la Etapa 1) — Invasive.Bx, Nota C (pág. 11)

**Template oficial** (pág. 5, bajo DCIS) — mapea 1:1 a nuestras clases:

| Template CAP | Nuestra clase (CSV) |
|---|---|
| Not identified | `ausente` |
| Present, focal (small foci or single cell necrosis) | `presente_focal` |
| Present, central (expansive "comedo" necrosis) | `presente_central` |
| Cannot be determined | `no_identificado` (excluido del binario) |

**Definición morfológica oficial (Nota C — texto literal CAP):**
- **Central ("comedo")**: *"The central portion of an involved ductal space is replaced by
  an area of expansive necrosis that is easily detected at low magnification. **Ghost cells
  and karyorrhectic debris are generally present.** Although central necrosis is generally
  associated with high-grade nuclei (i.e., comedo DCIS), it can also occur with DCIS of low
  or intermediate nuclear grade."*
- **Focal**: *"Small foci, indistinct at low magnification, or single cell necrosis."*
- **Distinción negativa (clave)**: *"Necrosis should be distinguished from **secretory
  material**, which can also be associated with calcifications, but **does not include
  nuclear debris**."*

**Términos oficiales para los prompts** (positivo): comedonecrosis · central necrosis in a
ductal space · expansive necrosis · ghost cells · karyorrhectic / nuclear debris · single
cell necrosis · small foci of necrosis. **(negativo / distractor):** secretory material
*sin* nuclear debris · viable tumor cells · DCIS without necrosis.

### Estado de los prompts (empírico, go/no-go CPU)
- **v1** (actual del driver) — AUC **0.677** (top-5). Positivos: `tumor necrosis`,
  `comedonecrosis`, `necrotic cellular debris`, `central necrosis in ductal carcinoma in
  situ`. **Ya es lenguaje CAP** (comedo / central necrosis in DCIS = Nota C).
- **v2** (más morfología: `karyorrhectic debris`, `eosinophilic necrotic debris in duct
  lumen`) — AUC **0.649**. **Peor que v1**: más detalle no ayudó.
- **v3 (CAP)** — AUC **0.688** (top-10), bal_acc@bestthr 0.665. **El mejor piso** (v3 > v1 >
  v2). Refina el **lado NEGATIVO** con la distinción de la Nota C (`secretory material without
  nuclear debris`) + positivos con la firma low-mag (`ghost cells and karyorrhectic debris`,
  `expansive necrosis`, `comedonecrosis`, `central necrosis in a ductal space`). La palanca CAP
  del lado negativo **ayudó modestamente** (+0.011 vs v1); sigue bajo la banda GO fuerte (≥0.70)
  pero es el set **más anclado en CAP y empíricamente mejor** → **default del driver** desde ahora
  (`train_pathpt.py` TASK_PROMPTS necrosis). Reproducir: `zeroshot_necrosis_gonogo.py --version v3`
  → `results/pathpt_gonogo/necrosis_v3_zeroshot_metrics.json`. **Sign-off clínico final: Sebastián.**

---

## 2. TASA MITÓTICA (tarea secundaria) — Invasive.Bx, Nota B + Table 1 (págs. 8–9)

- Parte del **Nottingham combined histologic grade** (Elston-Ellis). Score = nº de **figuras
  mitóticas** en 10 HPF consecutivos en la zona más activa. Template: Score 1 / 2 / 3 →
  nuestras `score_1/2/3`.
- **Literal CAP**: *"Only clearly identifiable mitotic figures should be counted;
  hyperchromatic, **karyorrhectic, or apoptotic nuclei are excluded**."* (Ojo: el debris
  karyorrhéctico que **señala necrosis** se **excluye** del conteo mitótico → prompts
  distintos.)
- **Table 1**: el corte 1/2/3 depende del diámetro de campo (ordinal de densidad). Ej. campo
  0.50 mm: Score 1 ≤7, Score 2 8–14, Score 3 ≥15 mitosis/10 campos.
- Términos para prompts: `mitotic figure(s)` · `high/low mitotic count` · `frequent/rare
  mitoses` (gradiente ordinal score_1<score_2<score_3).

---

## 3. Otras tareas OncoMets ancladas en el MISMO protocolo (contexto)

El Invasive.Bx ancla varias tareas del proyecto (confirma [[cap-fuente-clases-tareas]]):

| Tarea OncoMets | Sección CAP (Invasive.Bx) | Tipo |
|---|---|---|
| `cdis_patron_{cribiforme,micropapilar,papilar,solido}` | DCIS → **Architectural Patterns** (pág. 5): Comedo, Paget, Cribriform, Micropapillary, Papillary, Solid — *"select all that apply"* | binarias (multi-label) |
| `microcalcificaciones_en_{cdis,carcinoma_invasivo,tejido_no_neoplasico}` | **Microcalcifications** (pág. 5, Nota D): Not identified / Present in DCIS / in invasive carcinoma / in non-neoplastic tissue — *"select all that apply"* | binarias (multi-label) |
| `invasion_linfatica_vascular` | **Lymphatic and/or Vascular Invasion** (pág. 5): Not identified / Present / Cannot be determined | 3 clases |
| `gh_dif_tubular` | Histologic Grade → **Glandular/Tubular Differentiation** Score 1/2/3 (pág. 4) | 3 clases (ordinal) |
| Nuclear grade DCIS | **Table 2** (pág. 10): Grade I/II/III por 6 features | 3 clases |

(El "select all that apply" del CAP es exactamente por qué estas tareas se reformulan como
**binarias independientes** — coincide con la decisión de Sebastián.)

---

## 4. Provenance para la presentación / Sebastián

Los prompts de necrosis **se basan en el texto literal del protocolo CAP Invasive.Bx, Nota C**
(comedo/central/focal necrosis), no en redacción ad-hoc. La iteración v3 prueba la única
palanca CAP aún no medida (distinción negativa vs material secretorio). Validación clínica
final = Sebastián. Resultado empírico de v3: ver §1 / `results/pathpt_gonogo/`.
