# Auditoría de coherencia — entregable de interpretabilidad para Sebastián (15-jul-2026)

> Continúa `hallazgos_sesion_sebastian_15jul.md` (SB1-SB6). Esta sesión NO agregó
> conocimiento técnico nuevo: produjo un **entregable** (revisión de heatmaps para
> Sebastián) y **re-verificó** los hechos de SB1/SB2 contra disco+código (siguen firmes).
> Doc ANTES de los fixes. Branch: **main** (documental). GPU: job ajeno `4584 mammoth_ sgaete`
> CORRIENDO (~2 h) → auditoría solo-documental, sin tocar `clam_environ` (de donde lee su job),
> sin cambio de rama (workaround H). `origin/main` en sync (0/0).

## Resumen (id · hallazgo · tipo · acción)

| id | hallazgo | tipo | acción |
|---|---|---|---|
| E1 | **Entregable producido:** zip liviano (17 MB) de la carpeta de interpretabilidad de CDIS (`sprints/B5_sprint5/mammoth_entendimiento/interpretabilidad/`) + `README.md` unificado y sanitizado + correo de revisión para Sebastián. Cumple el ítem "Documentación de cierre" de B7. | progreso | registrar en `progress/current.md` |
| E2 | **Preferencia de trabajo nueva (entregables externos):** para material que sale a Sebastián/revisores → **un solo doc unificado**, **sin nombres propios** (Benjamín/Sebastián), **sin jerga interna** («palanca», «hallazgo», «reunión», IDs de job, nº de sprint), **comandos precisos**. | feedback | memoria nueva `entregable-externo-sanitizado` |
| E3 | **Re-verificación SB1/SB2 (siguen firmes):** líneas exactas + disco confirmados (ver Detalle). Enriquece SB1 con los nº de línea que no estaban explícitos. | validación | nº de línea citados acá; memorias ya correctas |
| E4 | **Higiene:** el `.zip` del entregable es un derivado binario (como los `.pptx`/`.pdf`) → NO versionar. Añadir regla a `.gitignore`. | higiene | `.gitignore` `sprints/**/*.zip` |
| E5 | **Abiertos sin cambio (se arrastran al handoff):** clases de `tipo_histologico`, splits reuso vs regenerar, `patch_size_level0:512` del meta de interp. de invasión (SB6), ubicar código del gate binario, Sebastián manda *dónde* documentó el parche. | pendiente | handoff |

## Detalle

### E1 — Entregable de revisión de heatmaps (para que Sebastián revise por su cuenta)
- **Fuente (canónica, versionada):** `sprints/B5_sprint5/mammoth_entendimiento/interpretabilidad/`
  — 4 slides TCGA-BRCA del checkpoint `obj6_mammoth_binarias_cdis` (cdis_f0), heatmaps de
  ruteo por experto + top-k por experto + cross-slide. 1.6 GB completa.
- **Entregable (derivado, NO versionado):** `interpretabilidad_liviano.zip` (**17 MB**, 22 archivos).
  Curado para caber como adjunto físico de Gmail (<25 MB):
  - Incluye por slide: `heatmap_montage.png`, `topk_contact_sheet.jpg` (convertida de PNG a
    JPG q92 para pesar ~1 MB en vez de ~5), `expert_usage.csv`, `meta.json`; `topk_subset_6experts.png`
    (solo E2-A14Q); a nivel raíz `cross_slide/` (4) y `README.md` unificado.
  - Excluye por peso: `heatmaps/` (30 PNG/slide full-res) y `topk_patches/` (240 recortes/slide).
- **`README.md` unificado (dentro del zip):** funde el `README.md` (guía de reproducción) +
  `resultados.md` (lectura de figuras) de la carpeta fuente en **un solo archivo sanitizado**
  (sin nombres, sin jerga interna). Secciones: qué contiene · cómo se generaron (comandos
  exactos) · config del modelo · cómo leer las figuras · limitaciones. Los `.md` fuente de la
  carpeta **NO se tocaron** (siguen con su contexto interno completo).
- **Correo de revisión** redactado (papers de microcalc + presentación + zip); estructura de
  carpetas descrita 1:1 con el contenido del zip. Lo envía Ernesto.

### E2 — Preferencia de entregables externos (feedback durable)
Ernesto pidió, iterando sobre este entregable: (1) fundir README+resultados en uno; (2) NO
mencionar a Benjamín ni a Sebastián; (3) comandos precisos y concisos; (4) evitar «palanca»,
«hallazgo», «reunión» y términos internos. Extiende [[deck-estilo-sin-rayas-ni-palanca]]
(cero «—» / sin «palanca») al material que sale del equipo, y complementa
[[readme-resultados-formato-minimalista]]. → memoria `entregable-externo-sanitizado`.

### E3 — Re-verificación de SB1/SB2 (read-only, regla 5) — con líneas exactas
- `run_create_patches_tcga_sc.slurm:17-18` → `--patch_size 448` / `--step_size 448` (TCGA).
- `run_extract_features_tcga_sc.slurm:32,34` → `--model_name conch_v1` / `--target_patch_size 224`.
  → 448@×40 baja a 224 antes de CONCH = mismo campo físico (104 µm) que 224@×20.
- Disco: `environ/features_tcga_224x40/pt_files` = **864** (backup viejas 224@×40);
  `environ/features_tcga_sc/pt_files` = **0** (vacía, las movió a `features/`); un `.pt` de
  TCGA en `environ/features/pt_files` con **mtime 2026-06-27, owner `sgaete`**.
  → confirma [[features-tcga-drift-reextraccion]] y [[magnificacion-cpathagent-proxima-direccion]] ADDENDUM 15-jul.

### E5 — Abiertos (para el handoff, sin cambio esta sesión)
1. Clases exactas de `tipo_histologico` (hipótesis 3-clase {no_especifico, lobulillar, otros} sin no_id — confirmar con Sebastián).
2. Splits: reusar los existentes vs regenerar con el label set reducido (data-pipeline → regla 9 + reviewer).
3. `patch_size_level0:512` del meta de la interpretabilidad de invasión (SB6) — chequear geometría del `.h5` antes de usar esos heatmaps.
4. Ubicar el código del gate binario carcinoma-invasivo que Sebastián dejó en el server.
5. Sebastián iba a mandar *dónde/cómo* documentó el parche de magnificación.

## Fixes aplicados
- `progress/current.md` — ítem "Documentación de cierre" marca el entregable producido + correo redactado.
- Memoria nueva `entregable-externo-sanitizado` (feedback) + línea en `MEMORY.md`.
- `.gitignore` — `sprints/**/*.zip` (derivados binarios, como los `.pptx`/`.pdf`).
- El `.zip` NO se commitea (derivado); la fuente versionada es la carpeta `interpretabilidad/`.
