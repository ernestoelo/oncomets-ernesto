# Auditoría de coherencia — contraste paper original de Mammoth ↔ nuestro material

> Fecha: 2026-06-25 · Rama: `chore/audit-paper-mammoth-b5`
> Disparador: sesión de **estudio** del paper original (handoff
> `handoff_B5_estudio_paper_mammoth_20260625_1136.md`). Se descargó
> `papers/mammoth_shao_iclr2026.pdf` (OpenReview `S5Io33pc78`, autorizado por
> Ernesto) y se contrastó **línea por línea** contra el código fuente
> (`clam_testing/MAMMOTH/src/mammoth/mammoth.py`), nuestra integración
> (`models_mammoth/clam_mammoth.py`), `@mammoth`, `CLAUDE.md` y los diagramas.
> **Es estudio, no investigación nueva** → cero GPU, cero cambios a modelo/training.
> Las correcciones son al **material pedagógico/doc**, no al modelo.

## Resumen (id · hallazgo · severidad · acción)

| id | hallazgo | tipo | severidad | acción |
|----|----------|------|-----------|--------|
| H1 | `keep_slots=False` (nuestro default/drop-in) = la **ablación Soft-MoE-output** del paper (§A4.6, Tabla 4a −4.7%); `keep_slots=True` = el **diseño canónico** del paper (§3.4) | reconciliation | media | cláusula concisa en `@mammoth` + nota 1 línea en docstring de `clam_mammoth.py` |
| H2 | "MoE/mammoth overfittea MÁS con pocos datos" tiene tensión con la **data-efficiency claim** del paper (§5.3 + Fig. 4): el paper presenta MAMMOTH como data-*eficiente* (le gana a la lineal aun al 20% de datos) | reconciliation | media | ADDENDUM datado a `insuficiencia-datos-ejes-investigacion` (no reescribir) + índice |
| H3 | título mal citado: *"Mixture of Mini Experts **in Pathology**"* → título real *"...: Overcoming the Linear Layer Bottleneck in Multiple Instance Learning"* | error | baja | fix en `@mammoth:8` y `clam_mammoth.py:3` + agregar el acrónimo MAMMOTH |

**Nota de alcance:** mi reporte previo decía "título mal en 3 lugares (incl. CLAUDE.md)".
Verificado con `grep`: **CLAUDE.md NO cita el título completo** (solo lo describe como
"MoE en el patch-embed"). Son **2 lugares**, no 3. La memoria
`mammoth-investigacion-integracion` ya lo tiene **correcto** → no se toca.

**Veredicto global:** nada en el paper contradice el **Hallazgo 12** (12 tareas,
0 palancas). La integración es fiel y la comparación pareada es válida. NO se reabre
mammoth. Todas las acciones son documentales/aditivas.

---

## H1 — `keep_slots` vs el paper (reconciliation)

**Qué dice cada fuente:**
- **Paper §3.4:** la salida canónica de MAMMOTH son los **S·E slot-tokens**
  (`{z_j^(k)}`, condensación >25× respecto de N). Eso = `keep_slots=True` en el código
  (`mammoth.py:359` el branch `if not self.keep_slots` es el que NO se toma).
- **Paper §A4.6 + Tabla 4a ("Output: Slots → Patches"):** recombinar los slots de
  vuelta a N parches (la "Soft-MoE patch output formulation") es una **ablación** que
  **pierde −4.7%**. Eso = `keep_slots=False`.
- **Nuestro material:** `clam_mammoth.py:18,58` usa `keep_slots=False` por defecto, y
  `@mammoth:48-52` lo describe como "1ª pasada / comparación limpia". El diagrama
  `Diagrama_mammoth_fused.pptx` (slide 2) rotula `False`="mammoth normal (base)" y
  `True`="variante NUEVA".

**Por qué NO es bug y NO cambia el veredicto:**
- Elegimos `keep_slots=False` **a propósito**: preserva los N parches → el
  attention-pooling y el instance-loss top-k de CLAM quedan **idénticos al baseline**
  → comparación pareada que aísla SOLO el patch-embed (regla de oro del hilo).
- Corrimos **ambos** modos (False en Obj1/2, True en Obj3) → **0 palancas** en los dos.
- El rótulo "base vs nueva" es correcto respecto de **nuestra cronología** (drop-in
  primero), pero **respecto del paper está invertido**: `True` es el diseño del paper,
  `False` es su modo ablado. Vale anotarlo para no confundir a quien lea el diagrama.

**Fix (conciso, sin reescribir):** una cláusula en `@mammoth` (sección `keep_slots`) y
una nota de 1 línea en el docstring de `clam_mammoth.py` aclarando la correspondencia
paper↔código. NO se tocan los diagramas en esta pasada (son `papers/presentations/`,
gitignored; el fix de notación de la slide queda como tarea pedagógica aparte si Ernesto
lo pide).

---

## H2 — Tensión de la afirmación "mammoth overfittea con pocos datos" (reconciliation)

**Qué dice cada fuente:**
- **Memoria `insuficiencia-datos-ejes-investigacion` (L16-24):** "MoE es data-hungry...
  los modelos sparse/MoE overfittean MÁS que los densos con pocos datos... → modificar
  mammoth es CONTRAPRODUCENTE". Cita HuggingFace MoE blog + MoEC (arXiv 2207.09094).
- **Paper §5.3 + Fig. 4 (Data efficiency):** *"A core design principle of MAMMOTH is to
  facilitate stable training in the data-scarce regimes common in CPath... MAMMOTH
  attains the highest overall performance across all fractions... **other MoE methods
  consistently underperform compared to the linear layer at lower data fractions**,
  highlighting the limitations of traditional MoE approaches for CPath."*

**La reconciliación (no es contradicción del Hallazgo 12):**
- La parte "**MoE genérico** es data-hungry" → el paper **coincide** (dice exactamente
  eso de "traditional MoE approaches").
- La parte "**mammoth** overfittea más con pocos datos" → el paper **disputa**: su tesis
  central es que MAMMOTH (bajo rango + Φ compartida + condensación a slots) está
  diseñado para NO hacerlo, y le gana a la lineal **incluso al 20% de datos**.
- **El "pocos datos" del paper** = fracciones de datasets n=547–10.616 razonablemente
  balanceados. **Nuestro régimen** = desbalance extremo con 3–6 positivos absolutos por
  test, que el paper nunca probó.

**Por qué la conclusión "no modificar mammoth" SOBREVIVE — pero sobre un argumento más
afilado:** no es "mammoth overfittea con pocos datos" (el paper lo niega), sino que
**(a)** en nuestro régimen extremo mammoth empíricamente no movió la aguja (Hallazgo 12,
medido); **(b)** hacer mammoth "más grande / más expresivo" (más expertos, ruteo más rico)
**erosiona justamente las restricciones (bajo rango / weight-sharing) de las que viene su
data-efficiency** → ahí sí caería en el régimen data-hungry del MoE genérico. El cuello es
cantidad/desbalance de datos, no el patch-embed.

**Fix:** ADDENDUM datado a la memoria (no reescribir el cuerpo ni borrar la cita externa;
es un registro de investigación `reference`). Actualizar la línea del índice.

---

## H3 — Título mal citado (error)

**Verdad de campo (del PDF descargado + README + bibtex del repo fuente):**
- Título real: **"Mixture of Mini Experts: Overcoming the Linear Layer Bottleneck in
  Multiple Instance Learning"** (ICLR 2026, Shao et al., Mahmood Lab).
- Acrónimo (definido en §3, 1ª línea): **MA**trix-factorized **M**ixture **M**odule
  **o**f **T**ransformation **H**eads — ni `@mammoth` ni el código lo mencionaban.

**Dónde está mal:**
- `.claude/skills/mammoth/SKILL.md:8` → *"Mixture of Mini Experts in Pathology"*.
- `models_mammoth/clam_mammoth.py:3` → *"Mixture of Mini Experts in Pathology"*.

**Dónde está bien (no tocar):** `mammoth-investigacion-integracion` (memoria) y
`sprints/B4_sprint4/objetivo_6_mammoth/README.md:10` (cita corta "*Mixture of Mini
Experts*", sin subtítulo errado).

**Fix:** corregir el subtítulo en los 2 lugares + agregar el acrónimo en `@mammoth`
(home canónico del "qué es mammoth").
