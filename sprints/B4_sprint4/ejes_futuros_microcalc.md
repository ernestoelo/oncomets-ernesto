# Ejes futuros para microcalcificaciones (aprobados reunión 26-may, NO en este sprint)

> Dos líneas que Sebastián aprobó y le entusiasmaron, pero quedan para
> **objetivos futuros** (post chain 4170→4171→4172). Se registran acá para no
> perderlas y poder arrancarlas con argumento. Ambas tocan datos/cómputo caro
> → planificar antes de ejecutar.

---

## Eje A — Mayor magnificación (re-extracción CONCH con más zoom)

**Qué.** Re-extraer las features CONCH de los parches a una **magnificación
mayor** (más zoom) que la actual, **solo para las slides de microcalcificaciones**
(CONCH es caro → no re-extraer todo el universo).

**Por qué (argumento clínico).** Una microcalcificación es un punto muy
pequeño. A la magnificación actual la señal puede estar sub-resuelta; más zoom
→ más detalle espacial en el parche que contiene la lesión. Es el factor
"escala / nº de parches" que Sebastián ya había señalado el 22-may.

**Dependencias / costo.**
- Requiere correr el pipeline de tessellation + extracción CONCH
  (`create_patches_fp.py` + `extract_features_fp.py` de Sebastián, READ-ONLY —
  vía `.slurm` propio, output bajo `clam_testing2/`).
- CONCH es lento → acotar a las slides de microcalc (identificadas + las del
  binario fusionado según el experimento que se quiera alimentar).
- Las nuevas features viven bajo `clam_testing2/` (containment), NO mezclar con
  `environ/features/pt_files/`.

**Primer paso cuando se retome.** Hipótesis pre-registrada (regla 9): qué
magnificación, sobre qué subset, métrica de éxito = Δ balanced_acc vs el mejor
modelo a la magnificación actual, MISMO dataset. Reviewer OK antes de extraer.

**Pendiente de Sebastián.** Confirmar la magnificación objetivo y de dónde
salen las WSIs originales para re-tesselar (las features actuales no bastan —
hay que volver a la WSI).

---

## Eje B — Selección de parches con información (no ruido)

**Qué.** Usar el **mejor modelo** disponible para identificar los parches
**informativos** (señal) vs ruido de una slide, y luego **re-entrenar**
ponderando más esos parches (o seleccionándolos al inicio del entrenamiento).

**Por qué.** Idea de Sebastián, conecta con el Eje A: si subimos magnificación,
arrastramos también más parches-basura; conviene descartar el ruido para no
"procesar basura". Analogía: el experimento de heatmap de CLAM sobre Camelyon,
donde el modelo resalta gran parte del tumor. (Matiz que Sebastián mismo marcó:
no siempre el cáncer se ve como "tumor" — es una idea genérica a desarrollar.)

**Estado.** La más abierta de las dos ("aún eso está por verse", Sebastián).
Falta definir: qué modelo genera la selección, criterio de "informativo"
(¿attention scores? ¿instance scores top-B?), cómo se inyecta al re-entrenar
(pesos de muestreo vs filtrado duro de parches).

**Conexión con lo que ya tenemos.** El Objetivo 4 (heatmaps comparativos,
PENDIENTE, viabilidad ya verificada en `objetivo_4_heatmaps/`) es el vehículo
natural para visualizar qué parches atiende el modelo → insumo directo de este
eje. La rama de instancia de CLAM (top-B/bottom-B sobre la atención) ya hace una
forma de selección de parches; este eje la llevaría a re-entrenamiento.

**Primer paso cuando se retome.** Conectar con Objetivo 4 (heatmaps del mejor
modelo del chain actual) para ver si la atención ya separa señal/ruido de forma
útil; recién entonces diseñar el re-entrenamiento ponderado, con hipótesis +
métrica pre-registradas.

---

## Eje C — CDIS: atención dual vs gated en lesiones distribuidas en ductos

**Qué.** Investigar si la atención **gated absoluta** de CLAM (`models/
model_clam.py:172`/`:239` — `M = torch.mm(A, h)` sobre todos los N parches)
captura algo específico de CDIS que la **atención dual relacional** de DSMIL
no replica. Posible vía: ablation por mecanismo de atención (gated vs dual)
manteniendo el resto del pipeline fijo, sobre el dataset binario CDIS.

**Por qué (pregunta abierta — argumento morfológico).** El anexo del
Objetivo 5 (job 4179, 28-may-2026) dio en CDIS un Δ pareado bal_acc =
**−0.053 ± 0.026** con signo negativo en los **5/5 folds** — no es ruido
del sorteo (la magnitud es chica pero la consistencia inter-fold descarta
azar). NULL en carcinoma y tejido, regresión leve solo en CDIS. La
morfología de CDIS (microcalcificaciones distribuidas en **ductos**, con
patrón espacial difuso a lo largo de estructuras tubulares) podría
beneficiar más a un mecanismo que pondere parches **absoluta**mente sobre
todo el bag (CLAM gated) que a uno que pondere **relativamente** entre
parches (DSMIL dual): si la señal está distribuida en muchos parches con
intensidad moderada, la atención dual de DSMIL — que tiende a destacar
parches "raros" relativo al resto — puede dispersarse, mientras la gated
absoluta los suma sin requerir contraste relacional.

**Estado.** Hipótesis abierta, sin formalizar. Requiere literatura sobre
mecanismos de atención en MIL para histopatología, y argumento clínico
formal sobre por qué CDIS sería el caso límite (lesión distribuida en
ductos vs lesión focal en carcinoma vs lesión dispersa en tejido).

**Primer paso cuando se retome.** Pre-registrar hipótesis (regla 9):
mecanismo concreto que se va a aislar (gated vs dual vs híbrido), métrica
de éxito = Δ bal_acc CDIS específicamente, sobre **los mismos splits** que
4170/4179 (paired por construcción — ver
[[patron-paired-comparison-reuso-splits]]). Reviewer OK obligatorio.

**Conexión con los otros ejes.** Es ortogonal a A y B: A toca features
(magnificación), B toca selección de parches, C toca el mecanismo de
agregación. Si los 3 se ejecutan, se pueden combinar (ej. mayor
magnificación + atención gated → ¿saca CDIS de la regresión leve?).

---

## Orden sugerido (cuando se retomen)

1. Cerrar el chain actual (4170→4171→4172) y decidir según resultados si el
   fusionado / DSMIL aportan.
2. Eje A (magnificación) primero — es el factor con argumento clínico más
   directo y Sebastián lo priorizó ("muy vital", "quedó entusiasmado").
3. Eje B (selección de parches) después, apoyado en los heatmaps del Objetivo 4
   y, si se hizo, sobre las features de mayor magnificación del Eje A.
4. Eje C (atención CDIS) en paralelo con B o al final — abre pregunta
   morfológica específica, no compite con A/B por cómputo (es ablation de
   mecanismo, no de datos). Útil solo si A no resuelve CDIS por sí solo.

Ver [[equipo-arquitecturas-mammoth-longnet]] y [[microcalc-fusion-objetivo5]]
(memorias) para el contexto de modelo y el estado del objetivo en curso.

---

## Apéndice — Experimentos ejecutados como anexo del Objetivo 5

### DSMIL × 3 binarias × k=5 MC-CV — EJECUTADO (job 4179, 28-may-2026)

**Decisión revisitada el 28-may** (post-merge del Obj 5 a main): tras
discutir con Ernesto, se decidió ejecutar el experimento aplicando la
regla 9 estricta (hipótesis primaria NULL pre-registrada + alternativa +
regresión + métrica decisiva + umbrales numéricos antes del sbatch +
reviewer OK obligatorio). El argumento clave que destrabó la decisión: el
"fracaso DSMIL" del job 4137 era **single-split** — el mismo régimen que
en Fase 0 invalidamos para CLAM (Hallazgo 1: carcinoma "0.808" era
0.732 ± 0.167). No se podía sostener "DSMIL falla en binarias" sin la
misma vara MC-CV.

**Hipótesis pre-registrada:** `sprints/B4_sprint4/objetivo_5_fusion_binaria/hipotesis_dsmil_binarias.md`
(reviewer-aprobado 28-may; cumple regla 9 íntegramente).

**Setup:** train_dsmil.py `--model_type dsmil`, 3 binarias × k=5 MC-CV,
**MISMOS splits que Fase 0** (paired por construcción), args idénticos a
Fase 2 (w_max 0.1 fijo). Wall: ~3h29m (early stopping cortó antes de las
30 epochs en la mayoría de folds).

**Resultado (veredicto por tarea según umbrales pre-registrados):**

| Tarea | Δ bal pareado | Veredicto |
|---|---|---|
| carcinoma invasivo | −0.023 ± 0.071 | **NULL** ✅ — el "0.824" del 4137 era ruido del sorteo |
| CDIS | **−0.053 ± 0.026** | **Regresión leve** ⚠️ — signo negativo en los 5 folds (consistente, no ruido) |
| tejido no neoplásico | +0.021 ± 0.051 | NULL / ambigua |

**Hallazgo agregado al Hallazgo 4 Fase 0:** la arquitectura sola no es la
palanca para microcalcificaciones, ahora con evidencia simétrica en ambos
regímenes (binarias y fusionado, ambos con MC-CV). CDIS abre una pregunta
morfológica (atención dual de DSMIL vs gated absoluta de CLAM) — tema para
futuro, no de este sprint.

**Detalle completo:**
- Resultados y comparación pareada por fold: `objetivo_5_fusion_binaria/resultados.md` §"ANEXO — DSMIL × 3 binarias × MC-CV k=5"
- Tabla comparativa maestra: `objetivo_5_fusion_binaria/tablas_presentacion.md` §C (filas 14-16) y §C.2
- Slides 11-12: `objetivo_5_fusion_binaria/presentacion_contenido_completo.md`
- Figuras: `objetivo_5_fusion_binaria/figuras/fig3{a,b}_anexo_dsmil_vs_clam_binarias_*.png` + `fig4{a..d}_*_confusion.png`
