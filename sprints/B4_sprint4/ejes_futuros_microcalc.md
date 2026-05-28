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

## Orden sugerido (cuando se retomen)

1. Cerrar el chain actual (4170→4171→4172) y decidir según resultados si el
   fusionado / DSMIL aportan.
2. Eje A (magnificación) primero — es el factor con argumento clínico más
   directo y Sebastián lo priorizó ("muy vital", "quedó entusiasmado").
3. Eje B (selección de parches) después, apoyado en los heatmaps del Objetivo 4
   y, si se hizo, sobre las features de mayor magnificación del Eje A.

Ver [[equipo-arquitecturas-mammoth-longnet]] y [[microcalc-fusion-objetivo5]]
(memorias) para el contexto de modelo y el estado del objetivo en curso.

---

## Apéndice — Experimentos opcionales no prioritarios

Registro de experimentos pensados pero **descartados como prioridad** del
sprint actual. Quedan acá para no perderlos; no son direcciones aprobadas por
Sebastián.

### DSMIL × 3 binarias × k=5 MC-CV (simetría del cuadro CLAM vs DSMIL)

**Qué.** Repetir el régimen de Fase 0 (CLAM × 3 binarias × k=5 MC-CV, job
4170) pero con DSMIL en lugar de CLAM. Cierra simétricamente el cuadro
"CLAM vs DSMIL × {3 binarias, 1 fusionado} × MC-CV" — hoy tenemos CLAM en
ambos (Fase 0 + Fase 1) y DSMIL solo en el fusionado (Fase 2). El cuadrante
faltante es DSMIL × binarias × k=5.

**Por qué NO en este sprint (3 razones).**

1. **Sin hipótesis pre-registrada nueva, viola la regla 9 de CLAUDE.md.** El
   job 4137 (DSMIL × binarias × 1 split) ya cerró como "fracaso
   arquitectónico" sobre balanced_acc; la única hipótesis viable nueva sería
   "el fracaso del 4137 era ruido del single-split" — pero eso sería
   alineado con la lógica de varianza de Fase 0, **no con un mecanismo
   arquitectónico**. Hipótesis débil → reviewer bloquea.
2. **El Hallazgo 4 de Fase 0 ya respondió la pregunta de fondo.** Las 3
   binarias dieron balanced_acc 0.577-0.639 con std 0.030-0.077 → modestas,
   apenas sobre 0.50, con barras de error que cubren el rango clínicamente
   relevante. El cuello es **datos** (328 slides), no arquitectura — Δ
   esperado DSMIL-CLAM ≈ 0 dentro de las bandas. Coherente con el resultado
   de Fase 2 sobre el fusionado: incluso con ~2814 slides el Δ pareado es
   ambiguo (+0.040 ± 0.038 en bal_acc, AUC retrocede). La hipótesis null
   ("DSMIL no aporta sobre las binarias tampoco") es la predicción honesta.
3. **Sebastián pidió otra dirección.** Reunión 26-may: mammoth (ya gana en
   3 tasks de él), mayor magnificación (Eje A), selección de parches
   (Eje B). El presupuesto de cómputo y atención va ahí.

**Si se retomara igual, requisitos mínimos (regla 9).**

- Hipótesis pre-registrada explícita: dirección esperada del Δ, magnitud
  umbral, justificación de por qué la pregunta sigue abierta tras Hallazgo 4.
- Reviewer OK antes de tocar `.slurm` o splits.
- Splits **reutilizar los de Fase 0** (`data/splits_kfold/microcalcificaciones_en_<tejido>_kfold/`)
  para mantener comparación pareada con CLAM 4170.
- Harness = `scripts/train_dsmil.py --model_type dsmil` (path byte-idéntico
  a 4135/4137).
- Wall esperado ≈ 3 × 5 × 1.3h ≈ 20h. Una sola GPU → cortesía single-GPU.
- Reporte = mean ± std + Δ pareado vs 4170; sin sobre-vender.
