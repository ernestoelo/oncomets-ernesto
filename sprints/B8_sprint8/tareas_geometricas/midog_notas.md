# MIDOG 2021: notas del dataset (insumo del paso 1 de la familia D)

> Aubreville M et al., *Mitosis domain generalization in histopathology images: The MIDOG
> challenge*, **Medical Image Analysis 84:102699 (2023)**. arXiv:2204.03742.
> PDF en [`midog_aubreville2023.pdf`](midog_aubreville2023.pdf) (19 pág.). Bajado el 2-ago-2026 (noche).
>
> No es uno de los papers del encargo: es la **fuente de datos** que el go/no-go del paso 1
> necesita. Esta nota existe para tapar el hueco #1 del handoff (el µm/px, que estaba sin
> verificar) y para dejar registrado lo que el dataset habilita y lo que advierte.

---

## 1. El hueco #1, resuelto: la resolución de MIDOG

Los seis escáneres, con la resolución óptica declarada en el paper (§2.2):

| Escáner | Modelo | Resolución | En qué conjunto |
|---|---|---|---|
| A | Hamamatsu NanoZoomer XR | **0.23 µm/px** @ 40× | train + test (referencia clínica) |
| B | Hamamatsu NanoZoomer S360 | **0.23 µm/px** @ 40× | train |
| C | Aperio Scanscope CS2 | **0.25 µm/px** @ 40× | train |
| D | Leica Aperio GT 450 | **0.26 µm/px** @ 40× | train (sin labels) + test |
| E | 3DHISTECH Panoramic 1000 | **0.24 µm/px** @ 20× | solo test |
| F | Hamamatsu NanoZoomer 2.0RS | **0.23 µm/px** @ 40× | solo test |

**El rango entero es 0.23 a 0.26 µm/px.**

**Qué significa para nosotros.**

- **TCGA está a 0.2325 µm/px**: cae dentro del rango de MIDOG, entre los escáneres A/B y C. Un
  detector entrenado en MIDOG corre sobre TCGA **sin reescalar**. El paso 1 sobre TCGA es barato,
  y esto ahora está verificado y no supuesto.
- **El privado está a 0.465 µm/px**, o sea **2× más grueso** que todo MIDOG. Ahí hay que
  reescalar, y el reescalado hacia arriba no inventa detalle. Es el brazo con riesgo, y es
  justamente donde vive la única lámina anotada (129741).
- Un detalle que refuerza nuestra regla de proyecto: el escáner E declara **"0.24 µm/px @ 20×"**.
  El rótulo de aumento y la escala física **no se corresponden** entre fabricantes. Parametrizar
  en µm/px y no en `objective-power` no es una manía nuestra, es lo que hace falta para leer esta
  misma tabla ([[cohortes-magnificacion-fisica]]).

## 2. La unidad de dato de MIDOG es exactamente el campo de recuento clínico

El dataset **no son WSI**: son **regiones de interés de 2.0 mm²** seleccionadas por un patólogo
sobre el escaneo de referencia, que es la definición de los 10 campos de gran aumento del
recuento de Nottingham (el paper lo dice así, §2.1).

Eso coincide **exactamente** con el §2.b de [`README.md`](README.md): los 2 mm² del recuento
clínico son ≈141 parches contiguos en nuestra cohorte privada. O sea que la unidad de anotación de
MIDOG **es** el punto caliente que nosotros tendríamos que aprender a elegir. MIDOG resuelve el
"cuántas mitosis hay acá dentro" y nos deja el "dónde está el acá dentro".

**Y la escala de anotación es comparable a la nuestra por región:** el paper dice que la mayoría
de las ROI contienen **20 o menos figuras mitóticas**. Nuestra 129741 tiene **26 marcas**. La
diferencia con MIDOG no es la densidad de anotación por región, es que ellos tienen **200 casos de
entrenamiento** y nosotros **una lámina**.

## 3. Lo que el challenge advierte, y es incómodo para el paso 1

**a) La razón de existir del challenge es que los detectores de mitosis se caen al cambiar de
escáner.** El test incluye a propósito escáneres no vistos (E y F). Nuestra cohorte privada es
**Ventana `.bif`**, que no está entre los seis. El riesgo de transferencia no es una preocupación
teórica nuestra, es el resultado central del challenge.

**b) Ellos también tienen anotación incompleta, y lo dicen.** El paper reconoce que las figuras
mitóticas son eventos raros y a veces tenues, y que **los expertos tienden a pasar por alto los
objetos menos reconocibles** al revisar la imagen, razón por la cual estos datasets se anotan por
consenso de varios expertos. Es un argumento adicional a favor de la familia D: el supuesto de
"lo no marcado es negativo" es frágil incluso en datasets construidos con cuidado.

**c) Hay imitadores.** Núcleos apoptóticos, células con cromatina condensada y áreas de necrosis
producen falsos positivos duros. El dataset incluye a propósito un número comparable de
"imposters" anotados.

## 4. Los números de referencia

| Enfoque | F1 (IC 95 %) |
|---|---|
| Ensamble de los 5 mejores | 0.773 [0.722, 0.813] |
| Ganador (*AI medical*) | **0.748 [0.704, 0.781]** |
| IAMLAB | 0.706 [0.650, 0.748] |

El ganador supera a seis expertos humanos en la misma tarea.

**Un número útil para calibrar expectativas del paso 1:** el criterio de acierto es que el
centroide predicho esté a menos de **7.5 µm** del centroide anotado. Con nuestras marcas de
36×36 px a 0.465 µm/px (16.7 µm de lado), un acierto según ese criterio cae holgadamente dentro de
la marca, así que la evaluación contra el geojson del patólogo es viable sin inventar tolerancias.

## 5. Herramientas públicas, que es lo que abarata el paso 1

El challenge publicó en GitHub, bajo la organización `DeepPathology`:

- `MIDOG_reference_docker`: algoritmo de referencia empaquetado.
- `MIDOG_evaluation_docker`: el evaluador oficial.

**No se bajaron** (están fuera de la lista autorizada del handoff §5). Si el paso 1 se aprueba,
son el primer lugar donde mirar, porque evitan implementar un detector y un evaluador de cero.
Licencia del dataset: **CC-BY**.

## 6. Lo que esta nota no afirma

- Que un detector de MIDOG transfiera a TCGA o al privado. Es exactamente lo que el paso 1 tiene
  que medir, y el propio challenge sugiere que la respuesta puede ser que no.
- Que tengamos permiso o intención de bajar el dataset. Acá solo se fichó lo que el paper dice.
- Que MIDOG 2022 (MedIA 2024, F1 del ganador 0.764, extiende a varios tumores y a perro) no sea
  mejor punto de partida. No se estudió.
