# La corrida de HoVer-NeXt cerró (job 5008, 19-ago-2026 00:52)

> **Estado que esto cambia**: el deck `CLAM_Sprint8.pptx` fue construido el 18-ago dando por
> hecho que esta corrida **no había corrido**. Cerró de madrugada. Las láminas 15, 22, 23, 24 y
> 26 quedan stale — detalle en §4.

## 1. Qué corrió, y qué no

| Brazo | `CP` | Estado |
|---|---|---|
| **Mitosis** | `lizard_convnextv2_tiny` | **Corrió** — job 5008, exit 0 |
| **Ensemble** | `pannuke_convnextv2_tiny_{1,2,3}` | **NO se lanzó.** Su directorio de salida está vacío |

La cola de la GPU, que el 18-ago a las 19:44 estaba trabada con dos trabajos sin límite delante
(`coordinacion_gpu.md`), **se drenó sola durante la noche**. El 5008 arrancó a las 00:33 y cerró
a las 00:52. Al momento de escribir esto **la cola está completamente vacía**.

## 2. Los números de la corrida

- **Tiempo de pared: 18 min** (1128 s) — 7 min 30 s de inferencia y 10 min 54 s de
  post-proceso. Contrasta con las **3 h 36** medidas de HoVer-Net (job 4714) sobre la misma
  clase de material.
- El preflight avisó, y acertó, que la WSI **no expone miniatura**, así que se teseló el lienzo
  entero (1600 tiles) en vez de filtrar fondo. Aun así el costo real quedó muy por debajo de lo
  que ese aviso hacía temer.
- **`--keep_raw` funcionó**: sobreviven `129741_raw_256_inst.zip` (9,7 GB) y
  `129741_raw_256_cls.zip` (815 MB), que es lo que la auditoría pidió pedir explícitamente
  porque el pipeline los borra al terminar.
- Salida total: **11 GB**.

Detecciones por clase, en la lámina entera:

| Clase | Detecciones |
|---|---|
| epithelial-cell | 87 553 |
| connective-tissue-cell | 68 364 |
| lymphocyte | 67 952 |
| plasma-cell | 12 322 |
| neutrophil | 1 419 |
| eosinophil | 542 |
| **mitosis** | **177** |

## 3. Qué NO se afirma

- **No hay comparación todavía contra las marcas del patólogo.** Las 177 son la salida cruda del
  detector sobre la lámina entera; las marcas del patólogo son **26** y son **positivos
  parciales** ([[anotaciones-patologo-qupath]]). Cruzarlas es trabajo que no se hizo.
- **No se afirma que el detector acierte.** No se calculó precisión, recall ni nada contra el
  geojson. Y PQ/bPQ/mPQ **siguen sin ser computables** contra ese geojson
  ([[hovernext-encargo-17ago-diseno]]).
- **No se midió el segundo factor del techo.** `techo_atencion.md` acotó lo que la máscara de
  atención deja pasar; **cuánto se come la detección** sigue sin medirse, que es exactamente lo
  que esta corrida ahora permite calcular y todavía no se calculó.
- **No se compararon los tres brazos**, porque solo corrió uno.

## 4. Qué queda stale en el deck del 18-ago

> **CONSUMIDA el 19-ago-2026.** Las cinco filas se corrigieron: las cuatro primeras en la sesión
> de la mañana y la última en la de la tarde, que además metió la lámina del cruce (el deck pasó
> de 26 a 27 láminas). La tabla se conserva **sin tocar** como registro del estado del 18-ago;
> **no es una lista de pendientes**. Lo único que sigue abierto de su última fila es el **brazo
> de ensemble**. Detalle: `presentacion_b8/README.md`, las dos secciones del 19-ago.

| Lámina | Lo que afirma hoy | Por qué quedó stale |
|---|---|---|
| **15** | «Cero números de segmentación»; sello «Falta la GPU»; remate «uno detenido por la cola de la GPU» | Corrió |
| **22** | Título «sin números todavía»; «No corrió: no hubo GPU disponible en toda la semana»; sello «En cola»; remate «Todo lo que no necesitaba GPU está cerrado» | Corrió |
| **23** | Remate «falta medir cuánto se come la detección» | Sigue siendo cierto, pero ahora **es calculable** y conviene decirlo así |
| **24** | La lámina entera pide coordinar una fila trabada | La fila se drenó sola y está vacía |
| **26** | Paso 2 «cuando se libere el turno de GPU» | El turno se liberó; lo que falta es el brazo de ensemble y el cruce |

**El bloque del 6-ago (láminas 1 a 14) no se ve afectado.**

## 5. Lo inmediato que esto habilita

1. **Lanzar el brazo de ensemble**, que es un `sbatch` con `CP=pannuke_..._1+..._2+..._3` y la
   cola vacía. Decisión de Ernesto (regla 1: nada de GPU sin pedido explícito).
2. **Cruzar las 177 contra las 26 marcas** — el segundo factor del techo.
