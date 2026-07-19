# Guía de estudio B7: dónde estamos, qué dice el deck, qué se discute con Sebastián

> Escrita el 19-jul-2026 al cerrar la sesión, como punto de reentrada.
> Objetivo: poder retomar el sprint sin releer todo el historial, y entrar a la
> reunión sabiendo qué hay en cada lámina y qué se decide.
>
> Documento de **orientación**. La verdad de campo con los números exactos vive en
> `resultados_interpretabilidad.md`; lo que sale hacia afuera, en `material_reunion.md`.

---

## 1. Qué es el Sprint 7, en una frase

Comparar **dónde mira CLAM y dónde mira Mammoth** sobre tres tareas clínicas, y
responder cuánta de su capacidad usa Mammoth de verdad. Es un sprint de
**interpretabilidad**, no de rendimiento.

Esa distinción es la que ordena todo el resto. El eje de rendimiento de Mammoth está
cerrado desde el Hallazgo 12 (doce configuraciones, cero mejoras). Este sprint nació
del pedido de Benjamín del 29-jun: entender el mecanismo, no volver a medir si gana.

### De dónde viene cada pieza

| Pieza | Origen |
|---|---|
| Las 3 tareas y su formulación | Cascada de Sebastián (gate invasivo), reformulada el 17-jul |
| El entrenamiento pareado | Job 4589, cerrado el 18-jul, 30/30 runs |
| La comparación de atención | Pedido central del sprint |
| Q1 (expertos/slots) | Pregunta de Benjamín de la reunión anterior |
| La sección de magnificación | Eje B6, que venía de antes y se presenta acá |

---

## 2. Estado: qué está cerrado y qué no

**Cerrado y verificado**
- Entrenamiento job 4589: 30/30 runs, paridad de particiones verificada por md5.
- Comparación de atención: 7 láminas, una por clase y tarea.
- Q1: cerrado el 19-jul con las 7 láminas.
- Deck: 21 láminas, generado y con los números de Q1 dentro.
- Material sanitizado para la reunión: completo.

**Abierto**
- QA fino del deck en PowerPoint (LibreOffice rompe las fórmulas, es artefacto suyo).
  Incluye **validar la migración de cabeceras del 19-jul** (ver §5) y confirmar que
  **Barlow** esté instalada: si no lo está, PowerPoint sustituye la tipografía y el deck se
  ve fuera de template aunque el archivo esté bien.
- Decisión sobre cómo proyectar el montage de expertos (ver §5).
- Sign-off de patólogo para los nombres de tejido (bloqueo externo, viene de OBJ-A).
- Qué hacer con el resultado de CDIS (ver §4, es decisión tuya).

---

## 3. Los tres resultados del sprint

### 3.1 Rendimiento: dos tareas confirman lo esperado, una sorprende

| Tarea | Δ balanced_acc (Mammoth menos CLAM) | Lectura |
|---|---|---|
| tipo histológico | −0.010 ± 0.017 (1/5 folds) | Ruido, como se pre-registró |
| invasión linfovascular | −0.023 ± 0.086 (2/5 folds) | Ruido, como se pre-registró |
| **CDIS** | **+0.074 ± 0.033 (5/5 folds)** | **Sorpresa** |

Las dos primeras confirman el Hallazgo 12. La tercera no, y es el punto delicado del
sprint (§4).

### 3.2 Atención: mismo barrio, distintas casas

Sobre las 7 láminas: correlación de rangos **0.805**, pero solapamiento del top 5% de
parches de solo **0.172**, y del top 1% de **0.073**.

Traducido: los dos modelos **ordenan el tejido parecido** (coinciden en qué región
importa), pero **los parches concretos que ponen arriba son distintos**. Además Mammoth
reparte la atención más que CLAM en 6 de 7 láminas (entropía 0.894 contra 0.781).

Esa frase, "mismo barrio, distintas casas", es la lámina 15 y es el mensaje central del
entregable.

### 3.3 Q1: los expertos se usan todos, los slots no

| Nivel | Efectivos | De | Lectura |
|---|---|---|---|
| Expertos | **30.0** | 30 | No están sobredimensionados |
| Slots | **158.7** | 300 | Cerca de la mitad aporta poco |

Los expertos dan 30.0 de 30 en **las 7 láminas**, y los cuantiles (15 expertos para el
50% del peso, 27 para el 90%) son exactamente los del reparto uniforme. Sólido.

Los slots varían entre 89.7 y 196.4, y esa dispersión **no depende de la tarea**: las dos
láminas de CDIS son justamente los dos extremos. Sigue al **tamaño de la lámina**
(ρ = 0.750, p = 0.052). Con siete láminas eso describe, no establece.

> Ojo con la nomenclatura: "peso por slot" es `combine_weights`, la segunda softmax sobre
> los 300 slots. **No** es el top-k de parches por experto. Si en la reunión alguien lo
> llama top-k, corregirlo.

---

## 4. El punto delicado: CDIS

Mammoth gana en CDIS con **5/5 folds positivos** en balanced_acc y en AUC.

**Lo que sostiene la señal**: suben **los dos** recalls (no 0.477→0.569, si 0.860→0.915),
lo que descarta que sea solo mover el umbral. El AUC sube 5/5, o sea mejoró el ranking. Y
el `val_loss` de Mammoth es menor en 4/5 folds, así que no es un artefacto del test.

**Lo que obliga a frenar**: hay **65 negativos en total**, unos 13 por fold. Cada negativo
vale 7.7 puntos de recall. En bruto son 6 negativos y 20 positivos más acertados sobre 429.
Además `_ci_reform` es formulación nueva, nunca incluida en las 12 configuraciones que
cerraron el Hallazgo 12, así que no lo contradice: abre terreno nuevo.

**Postura registrada**: no se reabre el eje de rendimiento (eso exige regla 9.b: pre-registro
nuevo, branch, reviewer). Queda como candidato a réplica con más semillas o folds. El deck
y el material ya lo presentan así.

**Esto sigue siendo decisión tuya.** Pediste explícitamente no tocar el punto.

---

## 5. Inventario del deck: qué hay en cada lámina

`sprints/B7_sprint7/presentacion_b7/CLAM_Sprint7.pptx`, **22 láminas**, 13.333 × 7.5.
Se regenera con `generate_b7_deck.py` (el .pptx es derivado y está gitignorado).

> **Actualizado el 19-jul (mañana):** el deck se migró a las **dos cabeceras reales de
> Plantilla** (commit `42280de`). Antes iban todas con la Environ y **siete no llevaban
> cabecera alguna**, entre ellas la 5 y la 7, que se leían como láminas rotas.
>
> **Actualizado el 19-jul (tarde) — re-base sobre el template VÁLIDO** (commit `170f7bd`).
> Ernesto fijó que el template a respetar es **`Modelo OncoMets Spatial V1 Deep-LLM-V.pptx`**,
> y el deck ahora se construye **sobre ese archivo** en vez de con `Presentation()`. El
> motivo es la causa raíz real del síntoma: los templates **embeben sus fuentes** y el
> default de python-pptx no, así que sin Barlow PowerPoint sustituía la tipografía y el
> deck se veía fuera de template **aunque el branding estuviera bien**
> ([[deck-template-fuentes-embebidas]]). Qué cambió:
>
> - **Numeración: 21 → 22 láminas.** La portada JPG se reemplazó por las **dos láminas de
>   apertura nativas** del template (portada de marca + lámina de título, retitulada
>   "OncoMets · MAMMOTH" con la fecha de la reunión). **Todo lo que sigue corre +1**
>   respecto de la tabla de abajo.
> - **Cabecera con la geometría LITERAL** del template (banda hasta 1.421), no la
>   compactada a 0.785. El contenido baja bajo la banda y, si no entra, se escala ~8%.
> - **La recapitulación pasó a cabecera OncoMets**: Deep-LLM-V no tiene cabecera Environ en
>   ninguna lámina. Era la última con logo Environ en la banda, justo lo que Ernesto vio.
> - Las **4 portadillas** siguen en fondo teal con el logo Environ blanco (decisión suya;
>   revisable, ver pendientes).

### Bloque A: apertura (1 a 2)
| # | Contenido |
|---|---|
| 1 | Portada |
| 2 | Recapitulación de objetivos |

### Bloque B: qué es Mammoth por dentro (3 a 9)
Es el bloque pedagógico, el que responde a Benjamín "domino el mecanismo".

| # | Contenido |
|---|---|
| 3 | Portadilla MAMMOTH |
| 4 | Qué significa la sigla y la idea general |
| 5 | Dónde entra MAMMOTH en el pipeline (feature extractor CONCH / ResNet50) |
| 6 | Dimensiones y código, con tabla |
| 7 | La arquitectura de MAMMOTH paso a paso: dimensiones por bloque, con las variables de la figura |
| 8 | **La relación 16 × 30 × 10**: cabezas, expertos y slots |
| 9 | La variante `keep_slots` y dónde cambia la salida |

### Bloque C: interpretabilidad, el corazón del sprint (10 a 16)
| # | Contenido |
|---|---|
| 10 | Portadilla: ¿qué mira cada experto? |
| 11 | Dónde y qué morfología recoge cada experto |
| 12 | **El experto detecta tejido, no clase** (resultado de OBJ-A) |
| 13 | Portadilla: ¿dónde mira cada modelo? |
| 14 | Comparación pareada: mismas particiones y datos |
| 15 | **Mismo barrio, distintas casas** (el mensaje central) |
| 16 | **¿Cuántos expertos y slots se usan de verdad?** (Q1) |

### Bloque D: magnificación multi-escala (17 a 21)
Eje B6, que no es de interpretabilidad. Va acá porque hay que decidir escalas.

| # | Contenido |
|---|---|
| 17 | Portadilla magnificación |
| 18 | No es más zoom, es contexto: escalas por cohorte |
| 19 | La matemática: µm/px, área física, tamaño de parche |
| 20 | Patología de la microcalcificación |
| 21 | **La decisión de escalas** (lámina de decisión) |

### El montage, que quedó sin decidir
La figura de los 30 expertos es correcta, pero a escala de proyección **los expertos se
ven todos parecidos** y el mensaje "cada uno capta una morfología distinta" no salta como
en OBJ-A.

Hay una tensión de honestidad, no solo estética: el hallazgo de Q1 es que **los expertos
son uniformes**, y se ven parecidos justamente porque lo son. Recortar a los expertos más
contrastantes haría saltar el mensaje, pero sería **seleccionar los casos favorables y
mostrarlos como típicos**. Opciones: proyectarlo tal cual, recortar declarando que es una
selección, o apoyarse en el contact sheet de top-k parches, que ya existe.

---

## 6. Agenda sugerida para la reunión

### Lo que se presenta como resultado
1. **El entregable de atención** (láminas 13 a 15). Mismo barrio, distintas casas. Es lo
   más sólido del sprint y lo que se pidió.
2. **Q1 cerrado** (lámina 16). Los expertos no sobran, los slots sí tienen margen. Si
   alguna vez hay que recortar capacidad, el parámetro son los slots.
3. **El experto detecta tejido, no clase** (lámina 12), con la advertencia de §7.

### Lo que se lleva como decisión a tomar
4. **La decisión de escalas** (lámina 21). Es el punto accionable para el próximo sprint.
5. **Qué hacer con CDIS**: réplica con más semillas o folds, o se deja registrado y
   quieto. Conviene llevar una recomendación, no una pregunta abierta.

### Lo que conviene preguntar
6. **Sign-off de patólogo** para los nombres de tejido: quién y cuándo. Es el bloqueo que
   más limita cómo se puede contar la interpretabilidad.
7. Si el número de slots interesa como palanca de eficiencia, o es curiosidad.

---

## 7. Qué NO afirmar en la reunión

- **Los nombres de tejido no son anotación.** Son lectura visual nuestra. No hay etiqueta
  de tejido por parche, solo la etiqueta clínica de la lámina. Lo que sí se sostiene es que
  el ruteo es **independiente de la etiqueta**: el mismo experto responde al mismo patrón
  en láminas de clases distintas.
- **CDIS no es una mejora establecida.** 65 negativos totales.
- **Q1 con n=7 describe, no establece**, sobre todo la correlación con el tamaño, que se
  apoya en una sola lámina chica.
- **Que Mammoth "difunda" la atención no explica que mida mejor en CDIS.** Es sugerente,
  con 7 láminas no se puede atribuir.
- **No llamar top-k al peso por slot.**

---

## 8. Dónde está cada cosa

| Qué | Dónde |
|---|---|
| Resultados completos con números | `sprints/B7_sprint7/resultados_interpretabilidad.md` |
| Material sanitizado para afuera | `sprints/B7_sprint7/material_reunion.md` |
| Respuesta de Q1 por lámina | `sprints/B7_sprint7/respuesta_q1_expertos_slots.md` |
| Tabla por tarea (pedido de Sebastián) | `sprints/B7_sprint7/tabla_por_tarea.md` |
| Generador del deck | `sprints/B7_sprint7/presentacion_b7/generate_b7_deck.py` |
| Figuras de atención y de expertos | `results/b7_mammoth_interp/interpretabilidad/<tarea>/<lámina>/` |
| Pre-registro del entrenamiento | `sprints/B7_sprint7/prereg_entrenamiento_interp.md` |

### Reproducir Q1 desde cero
```bash
PY=/home/sdonoso/miniconda3/envs/clam_latest/bin/python
# el ruteo (CPU, ~10 min por lámina, 7 láminas), SIEMPRE desatado (workaround J)
setsid nohup bash scripts/run_b7_expert_interp.sh > logs/b7_expert_interp_desatado.log 2>&1 < /dev/null &
# agregación (solo toma láminas con meta.json)
$PY scripts/answer_q1_expertos_slots.py
```
