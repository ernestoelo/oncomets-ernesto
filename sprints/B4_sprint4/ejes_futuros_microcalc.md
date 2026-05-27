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
