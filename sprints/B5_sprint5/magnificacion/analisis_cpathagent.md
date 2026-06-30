# Análisis de CPathAgent aterrizado a OncoMets — eje magnificación / contexto espacial

> **Insumo para la reunión del jueves 2-jul-2026 con Sebastián.**
> Lectura/análisis del paper (NeurIPS 2025), **sin código, sin GPU** (regla 9: fase argumento).
> Paper: `papers/NeurIPS-2025-cpathagent-...-Paper-Conference.pdf` (Sun et al., Zhejiang/Westlake/OSU).
> Toda afirmación del paper citada con sección/figura/tabla; lo que es razonamiento propio va marcado **[inferencia]**.
> Encuadre obligado (handoff + Hallazgos 11-14): CPathAgent se lee como **ataque al cuello = DATOS / contexto
> espacial**, NO como "otra arquitectura para que CLAM/mammoth gane" (ese eje está cerrado: 4 ejes, 0 palancas).

---

## 0. TL;DR (veredicto en 6 líneas)

1. CPathAgent **NO es portable tal cual**: es un LMM-agente (Qwen3-14B + CPath-CLIP) entrenado en 8× H800-80G,
   sobre **278K muestras instruction-tuning generadas con Gemini-2.5-Pro** y **reportes WSI pareados** (HistGen/TCGA).
   Nada de eso lo tenemos (1× A6000, cohorte privada **sin reportes pareados**, sin presupuesto Gemini).
2. **Pero el paper esconde una palanca de magnificación barata y directamente portable**, y NO está en el agente:
   está en el **preprocesamiento MIL** (Apéndice C.1.2) — **fusión de features multi-escala** (parche 2048 + 4×1024 +
   16×512, promediados por región vía el encoder) que alimenta un ABMIL/DSMIL estándar. Eso SÍ entra en nuestro presupuesto.
3. Hoy OncoMets es **escala única** (`patch_level=0`, parche 256, CONCH 512-dim). La fusión multi-escala es exactamente
   el **Obj 2 (magnificación)** del plan B5, todavía pendiente.
4. El paper **refuerza nuestro Hallazgo "cuello = datos"**: su propia clasificación WSI gana **solo +2.9% sobre ABMIL**
   multi-escala (Tabla 3) y su limitación nº3 admite que 5.254 WSIs es chico; su ventaja real es **eficiencia de datos**, no techo.
5. Lo accionable para nosotros = **agregar contexto multi-escala a las features CONCH** (paired vs CLAM single-scale,
   regla 9 + reviewer si se implementa). Lo NO realista = el agente LMM completo.
6. **Conexión con TITAN** (memoria [[insuficiencia-datos-ejes-investigacion]]): la fusión multi-escala de CPathAgent es
   más barata que TITAN porque **se queda dentro de CONCH v1 512-dim** (TITAN exige re-extraer con CONCHv1.5 768-dim).

---

## 1. Qué propone CPathAgent (resumen fiel)

**Idea central (Abstract, §1):** los modelos actuales (MIL y LMM) emiten el diagnóstico de un saque, sin imitar
*cómo* trabaja un patólogo: **mirar a baja magnificación para tener panorama → ir haciendo zoom progresivo en
regiones sospechosas (10×, 20×, 40×)**, integrando observaciones a través de escalas. CPathAgent es un **agente** que
hace eso explícitamente y verbaliza el razonamiento (interpretabilidad).

**Workflow en 3 etapas (§3.1, Fig. 2):**

```
                         CPathAgent — workflow tipo patólogo (§3.1)
  ┌──────────────────────┐   ┌───────────────────────┐   ┌──────────────────────────────┐
  │ 1) GLOBAL SCREENING   │   │ 2) NAVIGATION PLANNING │   │ 3) MULTI-SCALE REASONING      │
  │ thumbnail (32× down)  │──▶│ por cada región: plan  │──▶│ recibe TODA la secuencia de   │
  │ → grid N regiones      │   │ de pasos (x,y,m,o):     │   │ vistas recortadas de una vez   │
  │   16000×16000 @ 40×    │   │  x,y = coords [0,1]     │   │ → razonamiento holístico       │
  │ → agrupa en K clusters │   │  m = magnif. relativa   │   │   en 1ª persona (cross-ref.    │
  │ → severidad s_k∈{0..5} │   │      (1.0× = vista full)│   │   de evidencia entre escalas)  │
  │ → skip d_k∈{0,1}       │   │  o = foco diagnóstico   │   │ → reporte final                │
  └──────────────────────┘   └───────────────────────┘   └──────────────────────────────┘
```

- **Global screening (§3.1):** thumbnail por *downsampling* 32×, particiona en grid de N regiones con 5% de overlap;
  cada región `g_i` = **16000×16000 px @ 40×**. Agrupa regiones similares en K clusters con etiqueta semántica
  ("Core Tumor Regions", "Background Adipose..."), asigna severidad `s_k ∈ {0..5}` y decide saltar (`d_k=0`) o
  revisar a alta magnificación (`d_k=1`). Filtra lo no informativo → reduce cómputo.
- **Navigation planning (§3.1):** por región preservada genera un plan `P_i = {(x,y,m,o)}` autorregresivo —
  coordenada normalizada, **magnificación relativa** `m` (1.0× = la región completa; valores mayores = zoom), y `o` =
  qué hay que observar ahí.
- **Multi-scale reasoning (§3.1):** recibe la **secuencia completa de vistas recortadas a distintas escalas de una sola
  vez** y razona de forma holística, integrando evidencia entre escalas.

**Arquitectura y entrenamiento (§3.4):**
- Base **LLaVA-OneVision**; LLM = **Qwen3-14B**; encoder de visión = **CPath-CLIP** (de CPath-Omni); conector = MLP de 2 capas.
- Entrenamiento progresivo en **3 etapas**. Etapas 1-2 = protocolo CPath-Omni (alineación multimodal + patch-level).
  **Etapa 3 = la fase "agente"**: entrena sobre **CPathAgent-Instruct** (+ 20% de CPath-Instruct), todos los parámetros
  descongelados → capacidades de navegación/razonamiento tipo patólogo.
- **CPathAgent-Instruct (§3.2):** **278K** muestras de instruction-tuning, sintetizadas con **Gemini-2.5-Pro** guiado por
  **reportes WSI** (de HistGen) + imágenes. Incluye *multi-scale patch captioning*: 1× (overview) + 2× (4 vistas) +
  4× (16 vistas) = **21 parches** por región.

**Datos fuente (§3.2, Ap. A.1):** reportes WSI de **HistGen** + WSIs de **TCGA**. Split 80/20 por paciente →
**5.254 WSIs** de entrenamiento. (El subset de *region selection* se expandió con las 24.429 overviews de TCGA.)

**Benchmark nuevo (§3.3):** **PathMMU-HR²** — primer benchmark de "huge region" (16000×16000 px), 1.668 pares VQA
**validados por 3 patólogos certificados**. Argumento: el patólogo examina **regiones grandes**, una escala intermedia
entre parche y slide completo, hoy ignorada por los benchmarks.

---

## 2. La clave: el paper cuenta DOS historias de magnificación, no una

Esto es lo que más importa para nosotros. El paper mezcla dos mecanismos multi-escala con costos opuestos:

| | **(A) Agente LMM multi-escala** | **(B) Fusión multi-escala en el MIL** |
|---|---|---|
| Dónde está | El producto estrella (§3.1, §3.4) | El **baseline** de clasificación WSI (Ap. **C.1.2**) |
| Qué hace | Navega/zoomea como patólogo, razona en lenguaje | Promedia features de varias magnificaciones por región |
| Componentes | Qwen3-14B + CPath-CLIP + 278K samples Gemini | CLAM-seg + CPath-CLIP + ABMIL/DSMIL estándar |
| Costo | 8× H800-80G, ~73 h, reportes + Gemini | Re-extracción de features multi-escala + MIL normal |
| Portable a OncoMets | **No** (fuera de presupuesto y sin reportes/Gemini) | **Sí** (es nuestro Obj 2 de magnificación) |

**Detalle de (B), Ap. C.1.2 — esto es lo accionable:**
> Pipeline MIL (heredado de CPath-Omni): CLAM segmenta tejido → parches **no solapados de 2048×2048 @ 40×** →
> **subdivisión jerárquica**: se conserva el parche 2048×2048 **y** se extraen **cuatro 1024×1024** + **dieciséis 512×512**
> de la misma región → features de **todos** los parches multi-escala vía CPath-CLIP → **promediadas** en una
> representación unificada por región 2048. Esa representación alimenta ABMIL/DSMIL (20 épocas, LR 1e-5, Adam, batch 1, 5 seeds).

Es decir: **un token MIL por región codifica 1 vista gruesa + 4 medias + 16 finas, fusionadas por promedio**. No hay agente,
no hay LLM, no hay Gemini. Es ingeniería de features multi-magnificación sobre un agregador MIL clásico. **[inferencia]**
Esto es exactamente la palanca "jugar con la magnificación" que Sebastián propuso, y es ortogonal al agregador (que ya
cerramos como no-palanca, Hallazgos 11/12).

---

## 3. Relación con nuestro cuello = datos / contexto espacial

**Hoy OncoMets es escala única** (verificado contra el código, regla 5):
- `create_patches_fp.py`: `patch_size=256`, `step_size=256` (no solapado), `patch_level=0` (nivel de máxima resolución).
- `extract_features_fp.py`: `target_patch_size=224`, encoder CONCH → **512-dim**.
- → **una sola magnificación, un solo tamaño de parche**. CLAM_MB recibe `[N_parches, 512]`.

```
   OncoMets HOY (escala única)              CPathAgent baseline MIL (B) (multi-escala)
   WSI → parches 256 @ level0          WSI → región 2048 @ 40×
        → CONCH 512  → [N,512]               ├─ 1×  parche 2048      ┐
        → CLAM_MB                            ├─ 4×  parches 1024     ├─ encoder → promedio → [N_reg, D]
                                             └─ 16× parches 512      ┘   → ABMIL/DSMIL
```

**Por qué ataca nuestro cuello (y no la arquitectura):**
- Nuestros 4 ejes de arquitectura/objetivo cerrados (agregador, patch-embed/mammoth, lenguaje+tile/PathPT, loss) dieron
  **0 palancas** porque ninguno **agrega señal nueva** — reordenan la misma información de un solo nivel.
- La fusión multi-escala **sí inyecta señal nueva**: contexto arquitectural (estroma, interfaz tumor-estroma, patrón
  glandular) que a parche 256 de un solo nivel **no entra en el campo de visión**. El propio paper lo dice en la ablación
  (Tabla A5): quitar navegación+razonamiento multi-escala es lo que **más** cae (−7.8%), porque procesar regiones grandes
  de un saque obliga a *downsampling* agresivo que **"hace indiscernibles los detalles diagnósticos críticos"**.
- Esto **converge** con [[insuficiencia-datos-ejes-investigacion]]: atacar el DATO/contexto, no el modelo.

**Caveat honesto (regla 5):** el paper NO demuestra que la magnificación rompa el techo de datos. Su clasificación WSI
gana **+2.9% sobre ABMIL multi-escala** (Tabla 3: 82.8 vs 79.9) y su *upper bound* es 91.7 (9% de gap). El gran salto del
agente está en **VQA de regiones grandes** (Tabla 2, 88.6%) y en **eficiencia de datos** (Fig. 4: 88.1% con 5.254 WSIs vs
TITAN 91.9% con 335.645 — **64× menos slides**), no en clasificación pura. **[inferencia]** Para nosotros: la magnificación
es candidata legítima, pero hay que **pre-registrar la expectativa honesta** (probable lift chico, ortogonal al agregador).

---

## 4. ¿Aplicable a OncoMets? Escalera de 3 niveles con costo

Ordenado de **barato/realista** a **caro/aspiracional**:

### Nivel 1 — Fusión de features multi-escala (la idea (B), portable) ✅ realista
- **Qué:** re-extraer CONCH a ≥2 magnificaciones (p.ej. parche 256 @ level0 + parche que cubra más contexto, downsampleado),
  y fusionar por región (promedio, o concatenación, o un token por escala) antes de CLAM_MB. Réplica directa de Ap. C.1.2
  pero con **CONCH v1 512-dim** (no CPath-CLIP).
- **Costo:** GPU de **extracción de features** (no de entrenamiento del LLM) sobre ~3.072 slides `_pth`. La extracción CONCH
  ya se corre en la A6000 (jobs `conch_fe` de Sebastián). El entrenamiento CLAM **no cambia**. **[inferencia]** Es el de
  menor fricción: se queda dentro de CONCH, reusa CLAM, es paired vs el baseline single-scale ([[patron-paired-comparison-reuso-splits]]).
- **Riesgo/fricción:** toca el data pipeline → **regla 9 + reviewer + sbatch**. Duplica/triplica el almacenamiento de `.pt`.
  Decisión de diseño abierta: promedio (como el paper) vs concatenación vs multi-token (¿rompe el supuesto `[N,512]` de CLAM_MB?).
- **Veredicto:** **es el Obj 2 (magnificación) del plan B5.** Candidato #1 para proponerle a Sebastián.

### Nivel 2 — Re-extraer con encoder de mayor contexto (TITAN / CONCHv1.5) ⚠️ caro
- **Qué:** cambiar de encoder a uno con prior slide-level o más resolución (TITAN, mismo lab que mammoth; ver
  [[insuficiencia-datos-ejes-investigacion]] eje 2).
- **Costo:** **re-extraer features de ~3.000 slides con CONCHv1.5 768-dim** (TITAN). Mayor techo, pero caro y es **eje nuevo**,
  no "magnificación barata". CPathAgent NO usa TITAN, así que esto es tangencial al paper.
- **Veredicto:** fuera del alcance de "jugar con la magnificación" de esta reunión; anotarlo como dirección separada.

### Nivel 3 — El agente CPathAgent completo ❌ no realista para nosotros
- **Qué:** reproducir el agente LMM (Qwen3-14B + CPath-CLIP + navegación + razonamiento).
- **Por qué NO:** (a) **8× H800-80G** vs nuestra **1× A6000 49GB**; (b) **278K muestras instruction-tuning generadas con
  Gemini-2.5-Pro** — sin presupuesto ni pipeline; (c) **necesita reportes WSI pareados** (HistGen/TCGA) — nuestra cohorte
  privada (~533) **no tiene reportes pareados** en este formato; (d) el paper mismo muestra (Ap. B.5, Tabla A6) que aplicar
  la estrategia-agente a un modelo cerrado (Gemini-2.5-Pro) para clasificación WSI **empeora 6.7%** → el valor del agente
  viene del entrenamiento dedicado, no del prompting. **[inferencia]** Sería un proyecto en sí mismo, no un experimento de sprint.
- **Veredicto:** **inspiración / norte conceptual**, no implementación.

---

## 5. Lo que NO hay que hacer (consistente con el handoff)

- **NO** enmarcar CPathAgent como "nueva arquitectura para ganar métrica" — el eje rendimiento por arquitectura está
  cerrado (Hallazgos 11-14). Se evalúa como **ataque al dato/contexto espacial**.
- **NO** proponer meterle el agente/LLM a mammoth ni "más capacidad" — contraproducente con pocos datos
  ([[insuficiencia-datos-ejes-investigacion]] ADDENDUM 25-jun).
- **NO** prometer techo: la magnificación es señal nueva, pero el paper mismo no rompe el límite de datos (limitación nº3:
  5.254 WSIs « PRISM 587K / TITAN 335K).

---

## 6. Preguntas concretas para Sebastián (reunión jueves)

1. **¿Confirmamos que "jugar con la magnificación" = fusión de features multi-escala (Nivel 1), no el agente LMM?**
   Si es eso, es el Obj 2 del plan B5 y es realista con la A6000.
2. **¿A qué magnificaciones extraemos hoy realmente?** El código dice `patch_level=0` (máxima resolución del WSI) — para
   TCGA suele ser 40×, para algunas Environ 20×. **¿Las slides privadas y TCGA/HistAI están todas al mismo nivel base?**
   (Si no, la fusión multi-escala necesita normalizar por magnificación física, no por `level`.)
3. **¿Fusión por promedio (como el paper, Ap. C.1.2) o multi-token?** El promedio mantiene `[N,512]` y CLAM_MB intacto;
   multi-token (un embedding por escala) cambia la forma del bag — ¿vale la pena el cambio en CLAM?
4. **¿Sobre qué tareas lo probamos primero?** Propuesta: las que más sufren de contexto espacial (invasión 3-clase, patrón
   arquitectónico) — donde "qué hay alrededor del parche" es diagnóstico, no solo la célula. Paired k=5 vs CLAM single-scale.
5. **¿Hay reportes WSI pareados de la cohorte privada?** Si existieran, abre la puerta (a futuro) a algo estilo CPathAgent;
   si no, confirmamos que el agente queda descartado y nos quedamos en Nivel 1.
6. **Costo de re-extracción:** ¿cuánto tarda hoy `conch_fe` por slide? Para estimar el costo GPU de re-extraer ~3.072 slides
   a 2-3 escalas (cortesía single-GPU, encolar detrás de jobs ajenos).

---

## 7. Apéndice — números clave del paper (citables, regla 5)

| Dato | Valor | Fuente |
|---|---|---|
| Región "huge" | 16000×16000 px @ 40× | §3.1 |
| Thumbnail screening | downsampling 32× | §3.1 |
| Multi-scale patch captioning | 1× + 2×(4) + 4×(16) = 21 parches | §3.2, Fig.3 |
| LLM backbone | Qwen3-14B | §3.4 |
| Vision encoder | CPath-CLIP (de CPath-Omni) | §3.4 |
| Base multimodal | LLaVA-OneVision | §3.4 |
| Instruction-tuning samples | 278K (Gemini-2.5-Pro) | §3.2 |
| WSIs de entrenamiento | 5.254 (80% HistGen/TCGA, split por paciente) | §3.2, Ap.A.1 |
| Benchmark nuevo | PathMMU-HR², 1.668 VQA, 3 patólogos | §3.3 |
| **Hardware entrenamiento** | **8× NVIDIA H800-80G** | **Ap. C.3** |
| **Tiempo entrenamiento** | Etapa1 9h + Etapa2 25h + Etapa3 39h | **Ap. C.3** |
| **MIL multi-escala (baseline)** | 2048 + 4×1024 + 16×512 → promedio/región | **Ap. C.1.2** |
| WSI classif. — CPathAgent | 82.8% avg (6 tareas TCGA) | §4.3, Tabla 3 |
| WSI classif. — ABMIL / DSMIL | 79.9% / 76.8% avg | §4.3, Tabla 3 |
| Margen agente vs ABMIL | **+2.9%** (upper bound 91.7%) | §4.3, Tabla 3 |
| VQA región grande — CPathAgent | 88.6% (vs Gemini-2.5-Pro 76.4%, CPath-Omni 71.7%) | §4.2, Tabla 2 |
| OOD CPTAC-Lung | 88.1% (5.254 WSIs) vs TITAN 91.9% (335.645) → 64× menos | §4.4, Fig.4 |
| Ablación: −global screening | 82.8 → 80.3 (−2.5%) | Tabla A5 |
| Ablación: −navegación+razonamiento | 82.8 → 75.0 (**−7.8%**, el más crítico) | Tabla A5 |
| Gemini-2.5-Pro como agente (WSI) | **−6.7%** (72.1→65.4) | Ap. B.5, Tabla A6 |
| Limitaciones admitidas | paths sintéticos; solo clasif. (no pronóstico/biomarker); 5.254 WSIs es chico | Ap. D |

---

## 8. Una línea para la slide de "próximos pasos" del deck B5

> *Magnificación = fusión de features CONCH multi-escala (inspirada en el baseline MIL de CPathAgent, Ap. C.1.2):
> inyecta contexto espacial — la única señal nueva — sin tocar el agregador ya cerrado; paired vs CLAM single-scale.
> El agente LMM de CPathAgent queda como norte conceptual, fuera de presupuesto (8× H800 + 278K samples Gemini + reportes pareados).*
