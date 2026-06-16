# Auditoría de coherencia — diagrama de arquitectura PathPT (slide 11) + estilo

> Sesión 16-jun-2026. Disparador: Ernesto pidió `/knowledge-audit` tras aprobar el
> rediseño del diagrama de arquitectura de PathPT (slide 11 del deck B5). Foco: registrar
> los **hallazgos de estilo** (convención de diagrama nueva) y los **hechos code-accurate**
> que ahora viven en el diagrama, y propagarlos a las fuentes canónicas. Audit documental
> (sin GPU; jobs ajenos PD en cola, no tocados).

## Resumen

| id | hallazgo | tipo | acción |
|----|----------|------|--------|
| D1 | El diagrama de arquitectura del deck evolucionó a un **estilo "cascada de 3 ramas"** (paneles etiquetados + bloques modulares + callouts laterales + nodo backbone compartido). No estaba registrado. | style | Agregar a `convenciones_deck_b5.md §5` + memoria [[diagramas-arquitectura-pptx-editable]]. |
| D2 | El diagrama se construyó **code-accurate** (params exactos de `models_pathpt/{spatial,prompt,pathpt}.py` pin `0ab7f1b`), no solo del paper. La convención §5 previa decía "matemático" pero implícitamente paper. | reconciliation | Aclarar en §5: "matemático **y code-accurate**" (paper para ecuaciones, código para params reales). |
| D3 | Preferencias de Ernesto reveladas iterando (≥6 rondas) sobre cómo quiere el diagrama de arquitectura. Valor de feedback durable. | feedback | Memoria [[diagramas-arquitectura-pptx-editable]] (cláusula fechada). |
| D4 | Helper nuevo `edge()` en `generate_pathpt_pptx.py` (conector recto con punta de flecha, para aristas de cascada/árbol). | reference | Mencionado en §5 como helper disponible; no requiere doc aparte. |
| D5 | Regla "sin proceso de entrenamiento" ([[presentacion-convenciones-benjamin]]) se confirmó en la práctica: Ernesto pidió **quitar la "lectura"/agregación** del diagrama (eso es de slides previas) → el diagrama de arquitectura es **forward puro**. | reconciliation | Reforzar en §5: el diagrama de arquitectura = forward; lectura/agregación/eval van en otras slides. |

## Detalle

### D1 — Estilo "cascada de 3 ramas" (convención nueva)

**Qué se descubrió iterando:** el diagrama de arquitectura de un modelo multi-stream
(visión + lenguaje, como PathPT) converge a este molde, que Ernesto aprobó (rev 14):

- **3 ramas subdivididas en paneles etiquetados** con fondo de color tenue:
  rama VISIÓN (`θᵥ`, azul claro `#ECF2F8`), rama TEXTO (`θₜ`, naranjo claro `#FBF3EA`),
  rama MATCHING (gris claro `#EEF1F3`). Cada panel lleva un título (mayúsculas, 14pt).
- **Cascada hacia abajo**: VISIÓN (izq) y TEXTO (der) descienden y **convergen** en
  MATCHING (centro-abajo), que es **su propia mini-cascada** (no un solo bloque).
- **Bloques modulares** (1 operación por bloque, nombre corto) + **callouts laterales**
  con la **fórmula del traspaso** de información (estilo expansión de `Diagrama_CLAM.pptx`:
  izq para visión, der para texto). Conector fino bloque↔callout.
- **Nodo backbone compartido al centro** para llenar el hueco medio sin romper el
  minimalismo: `CONCH` (Φᵥ + Φₜ congelados), conectado con líneas finas a la rama visión
  (Φᵥ) y a la rama texto (Φₜ). Arquitectónicamente correcto: son los 2 encoders del mismo
  modelo congelado.
- **Aristas con flecha** (`edge()`); dims del traspaso sobre las aristas convergentes
  (`V̄ : N×512`, `T : C×512`).
- **Leyenda en esquina** (color = congelado/entrenable + glosario de dims), fuera de las ramas.
- **Color**: gris = CONGELADO, naranjo = ENTRENABLE, azul = pipeline.

**Canónico:** `convenciones_deck_b5.md §5` (registro versionado del deck) + memoria
[[diagramas-arquitectura-pptx-editable]].

### D2 — Code-accurate (no solo paper)

El diagrama detalla la arquitectura con los **elementos reales del código** además del
paper. Fuente de verdad = `models_pathpt/` (port pin `0ab7f1b`):

- `spatial.py` (`θᵥ`): `Conv1d` k=3,5,7 (pad 1/2/3) + LN + ReLU → suma `o₁+o₂+o₃+V`
  (residual) → `TransLayer` = LN + **NyströmAttention** (8 heads · 64/head · 256 landmarks
  · 6 pinv · dropout 0.1 · residual) → LayerNorm. Preserva `[N,512]`.
- `prompt.py` (`θₜ`): `ctx ∈ ℝ^(C×32×768)` aprendible (**768 = dim token-embedding**, NO
  512), init `"a histopathology image of"`; ensambla `[SOS | ctx×32 | CLASS+EOS] →
  ℝ^(C×127×768)`; `CONCHTextEncoder` (congelado) → `pooled ∈ ℝ⁷⁶⁸` → `· W_text → ℝ⁵¹²`.
- `pathpt.py`: features `.pt` son `forward_no_head` (pre-proyección) → el **driver** aplica
  `vᵢ = hᵢ · W_proj ∈ ℝ⁵¹²`; matching = L2-norm ambos → `logits = V̄·Tᵀ` →
  `P = softmax(logits · 10)` (`LOGIT_SCALE=10`, τ=0.1).

**Distinción clave a no perder:** `512` = dim contrastivo (espacio de matching) vs `768` =
dim token-embedding (donde viven los `ctx` aprendibles). El diagrama lo aclara en su leyenda.

### D3 — Preferencias de Ernesto (feedback durable)

Iterando ≥6 rondas, Ernesto convergió a (en orden de descubrimiento):
1. quiere **vectores con dimensiones entre las flechas** (estilo CLAM), no solo dentro de
   los bloques;
2. **rechaza bloques grandes con mucho texto** ("muy grandes") y **rechaza el layout
   horizontal de filas** (rev 12, "no me gustó para nada");
3. prefiere **cascada hacia abajo** + **bloques modulares chicos + callouts laterales**;
4. quiere **3 ramas subdivididas** (paneles etiquetados);
5. el medio vacío de un árbol se llena bien con el **backbone compartido** (no con prosa);
6. **bloques y fuentes grandes**; **sin bullets/prosa**; **leyenda en una esquina**;
7. el diagrama de arquitectura NO incluye la "lectura"/agregación (D5).

→ memoria [[diagramas-arquitectura-pptx-editable]].

### D5 — Forward puro (sin lectura/training)

Ernesto pidió explícitamente **quitar la agregación tumor-ratio / `ŷ` / mapa de localización
/ grounding** del diagrama de arquitectura ("eso es de slides previas"). Converge con
[[presentacion-convenciones-benjamin]] ("sin proceso de entrenamiento"). El diagrama termina
en `P ∈ ℝ^(N×C)` (clasificación por parche). La lectura/eval/losses viven en otras slides.

## Acciones aplicadas
- `convenciones_deck_b5.md §5` reescrita con el molde "cascada de 3 ramas" + code-accurate + forward-puro.
- Memoria [[diagramas-arquitectura-pptx-editable]] ampliada (cláusula 16-jun) + índice `MEMORY.md`.
- Sin contradicciones nuevas en CLAUDE.md / agentes / otras skills (el cambio es aditivo a §Formato de entregables).
