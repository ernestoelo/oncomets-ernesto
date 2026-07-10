# Registro — Luz polarizada, oxalato de calcio (Tipo I) y el techo de CONCH en microcalcificaciones

> **Para exponer a Sebastián.** Hallazgo colateral de la investigación de magnificación (B6):
> una parte de las microcalcificaciones mamarias es **físicamente invisible** en el H&E de campo
> claro sobre el que trabaja CONCH — hay evidencia y literatura. Es un dato clínico nuevo sobre
> microcalcificaciones + un límite honesto de nuestro pipeline + una dirección de investigación
> (no accionable hoy, sí como norte conceptual).
> Toda afirmación va con su fuente (regla 5); el razonamiento propio va marcado **[inferencia]**.

---

## 1. Las microcalcificaciones son de DOS materiales distintos

| Tipo | Composición | Cristalografía | En H&E de **campo claro** | Malignidad |
|---|---|---|---|---|
| **Tipo I** | **Oxalato de calcio** (weddellita) | Birrefringente | **Casi invisible** — incolora/refráctil; solo se ve con **luz polarizada** | Casi siempre **benigna**, poco frecuente |
| **Tipo II** | **Fosfato de calcio** (hidroxiapatita) | No/poco birrefringente | **Basófila** (púrpura/azul), anillos concéntricos laminados, en luz ductal o estroma | **Benigna Y maligna** — hasta **93% de los DCIS** las presentan |

*Fuentes:* *Breast microcalcifications: Past, present and future* (PMC8892454); *Calcification in
breast histopathology* (Diagnostic Histopathology 2024, S1756-2317(24)00207-X); *Polyhedral
microcalcifications at mammography: histologic correlation with calcium oxalate* (Radiology 1993).

---

## 2. Qué es la birrefringencia / luz polarizada (por qué el Tipo I es invisible)

- La luz normal vibra en **todas** las direcciones. Un **polarizador** es una "reja" que solo deja pasar
  la vibración en **una** dirección.
- Con **dos polarizadores cruzados a 90°**, la luz que pasó el primero **no** pasa el segundo → el campo se
  ve **negro**.
- Un material **birrefringente** (como el cristal de oxalato de calcio, o el colágeno) **rota** el plano de
  vibración al atravesarlo → desvía la luz lo justo para que **atraviese el segundo polarizador** → **brilla
  intensamente sobre el fondo negro**.
- Por eso el patólogo usa **luz polarizada** justamente para **cazar las calcificaciones de oxalato (Tipo I)**,
  que en el H&E normal se le pasarían por ser incoloras.

```
   H&E campo claro (lo que ve CONCH)        Polarizadores cruzados (microscopio del patólogo)
   ┌───────────────────────────┐            ┌───────────────────────────┐
   │  ·  fosfato (Tipo II)      │            │        ·                  │
   │     PÚRPURA, se ve         │            │   oxalato (Tipo I)        │
   │                            │            │   BRILLA (birrefringente) │
   │  ( oxalato Tipo I: casi    │            │   fondo negro             │
   │    invisible, incoloro )   │            │                           │
   └───────────────────────────┘            └───────────────────────────┘
```

---

## 3. Cómo trabaja CONCH — y por qué esto es un techo para nosotros

- **CONCH** (Lu et al., *Nat Med* 2024) es el extractor de features de OncoMets: un modelo
  visión-lenguaje entrenado sobre **H&E de campo claro (brightfield)**, magnificación nativa **20× (0.5 µm/px)**,
  tiles de 256 px → vector de **512 dimensiones** por parche. CLAM/mammoth consumen esos vectores `[N, 512]`.
- **CONCH NO tiene canal de luz polarizada.** La birrefringencia es una propiedad **física** de la interacción
  luz↔cristal que **no está codificada en el píxel** de un escaneo H&E normal → **no se puede reconstruir a
  partir del H&E**. → **CONCH está ciego al oxalato (Tipo I) a CUALQUIER magnificación.** **[inferencia,
  anclada en §1–§2]**

**Implicación para nuestras 3 tareas de microcalcificaciones (impacto acotado, no catastrófico):**
- `en_carcinoma_invasivo` y `en_cdis` → dependen de **Tipo II** (fosfato, basófilo, **visible**) → **CONCH sí
  las ve**; el techo del oxalato casi no las afecta.
- `en_tejido_no_neoplasico` → arrastra más calcificaciones **benignas**, donde el **oxalato (Tipo I)** es más
  frecuente → **techo parcial** para esta tarea, independiente de la escala o el modelo.

---

## 4. Sí existe literatura de luz polarizada + ML (evidencia, en mama)

Es un campo real y activo — sobre todo **polarimetría de matriz de Mueller** (*Mueller matrix polarimetry*):

| Paper | Qué hace | Cita |
|---|---|---|
| **Machine learning-based prediction of luminal breast cancer subtypes using polarised light microscopy** | Predice **subtipos luminales de cáncer de mama** con microscopía de luz polarizada + ML | *British Journal of Cancer*, 2025 — s41416-025-03150-x |
| Characterization and classification of ductal carcinoma tissue using Stokes-Mueller polarimetry and ML | Clasifica **carcinoma ductal** con polarimetría Stokes-Mueller | *Lasers Med Sci*, 2024 — s10103-024-04056-5 |
| Mueller polarimetric imaging… collagen microstructures of breast cancer tissues | El colágeno cambia de orientación (paralelo→vertical) al cancerizarse | ScienceDirect S0030401818308186 |
| Deep Learning-Based Holographic Polarization Microscopy | DL recupera birrefringencia (retardancia/orientación) de un holograma | *ACS Photonics*, 2021 |

**El paper canónico para mostrarle a Sebastián:** *Machine learning-based prediction of luminal breast cancer
subtypes using polarised light microscopy* (BJC 2025) — es evidencia directa de que la luz polarizada lleva
señal diagnóstica en mama que el H&E de campo claro no captura.

---

## 5. ¿Es accionable en CLAM + mammoth? — verdict honesto

**No como drop-in.** Todos esos métodos requieren una **adquisición polarimétrica** (cámara de matriz de
Mueller / polarizadores cruzados físicos / setup holográfico). Nuestras cohortes son **escaneos H&E de campo
claro estándar** y las features CONCH salen de ahí → **no tenemos ni una captura polarizada** y no se puede
retro-generar.

- Meterlo a CLAM+mammoth sería un **proyecto de adquisición de datos nuevo**: re-escanear los portaobjetos
  **físicos** con un escáner polarizador → nuevo extractor de features (no CONCH) → nuevo modelo. Mucho más
  allá de "jugar con la magnificación".
- Su payoff es **angosto**: detectar oxalato (Tipo I, **benigno**) sirve más para **descartar** malignidad /
  ayudar a la tarea `tejido_no_neoplasico`, no a las de carcinoma/CDIS (que ya usan el Tipo II visible).
- **Veredicto:** **norte conceptual**, no experimento de sprint — mismo estatus que el agente LMM de CPathAgent.
  Lo directamente accionable con lo que tenemos sigue siendo la **magnificación multi-escala sobre H&E**.

---

## 6. Una línea para Sebastián

> *Dato nuevo de microcalcificaciones: una fracción (las de **oxalato de calcio, Tipo I**) es **birrefringente**
> y solo se ve con **luz polarizada** — invisible en el H&E de campo claro sobre el que trabaja CONCH, a
> cualquier magnificación. Es un **techo físico** que afecta sobre todo la tarea de tejido no neoplásico (el
> oxalato es benigno); las de carcinoma/CDIS usan las de **fosfato (Tipo II)**, que sí son visibles. Hay
> literatura de **luz polarizada + ML en mama** (BJC 2025) como evidencia, pero requiere re-escanear con
> polarizador → norte conceptual, no experimento de este sprint.*
