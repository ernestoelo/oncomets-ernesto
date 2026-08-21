# A0 — las 13 que se escapan estaban segmentadas: falla la clase, no la segmentación

> Medido el **21-ago-2026**, CPU post-hoc, sin GPU y sin tocar nada ajeno.
> Script: [scripts/a0_segmentadas_o_no.py](../../../scripts/a0_segmentadas_o_no.py).
> Salidas: `results/b8_hovernext_129741/a0_falladas/`.
>
> Extiende [cruce_marcas.md](../hovernext_129741/cruce_marcas.md), que cerró el **13 de 26** y
> se detuvo en «es ausencia» sin preguntar de qué. No es uno de los cuatro encargos: es lo que
> más mueve el objetivo rector, porque el cuello ya está medido y **no es la máscara** (desde
> K=189 manda la detección), así que lo único que puede subir el 13 es el detector.

## 1. El resultado

**Las 13 marcas que HoVer-NeXt no acredita tienen un núcleo segmentado encima. Las 13.
Ninguna se escapó por falta de segmentación: se escaparon por la clase.**

| de las 13 falladas | n |
|---|---|
| con una instancia del mapa sobre la marca | **13** |
| sin ninguna instancia | **0** |
| la instancia recibió `epithelial-cell` | 12 |
| la instancia recibió `neutrophil` | 1 |
| tenían alguna instancia de clase `mitosis` a ≤ 15 µm | **0** |

La instancia no está «cerca»: está **encima**. Mediana de 2,1 µm entre el centroide de la marca
y el centroide del núcleo, máximo 6,7 µm, sobre marcas cuyo lado mediano es 16,7 µm.

Eso cambia el costo del arreglo. El objeto ya está detectado, delineado y con centroide; lo que
falló es la **cabeza de clase**. Es la rama barata de las dos que planteaba el plan.

## 2. El control positivo, que es lo que hace legible al grupo de estudio

Las 13 acreditadas pasaron por el mismo procedimiento (patrón **P3**: si el criterio no las
recupera a ellas, el criterio está mal y no el grupo de estudio). Las dos mitades salen
**indistinguibles en todo menos en la etiqueta**:

| | acreditadas (13) | falladas (13) |
|---|---|---|
| instancia más cercana, distancia mediana | 1,9 µm | 2,1 µm |
| ídem, máximo | 4,9 µm | 6,7 µm |
| clase de esa instancia | `mitosis` ×13 | `epithelial-cell` ×12, `neutrophil` ×1 |
| instancias dentro de 15 µm, mediana | 9 | 9 |
| lado mediano de la marca | 16,7 µm | 16,7 µm |

Mismo tejido, misma densidad de núcleos, misma puntería de la segmentación. **La única
variable que separa los dos grupos es la clase que salió de la cabeza de clasificación.**

## 3. Qué precisa esto de lo que ya estaba escrito

`cruce_marcas.md` §2 decía que las 13 falladas «no son por poco»: su detección de mitosis más
cercana está a 115 µm de mediana, o sea que **no es un problema de tolerancia ni de centrado,
es ausencia**. Sigue siendo cierto **y ahora se sabe ausencia de qué**: falta la *detección de
mitosis*, no el *núcleo*. A 2 µm hay un núcleo segmentado; lo que no hay en 15 µm a la redonda
es una instancia con la etiqueta `mitosis`.

Las dos frases conviven: el barrido de tolerancia de §2 mide distancia a detecciones **de clase
mitosis**, y éste mide distancia a **instancias de cualquier clase**.

## 4. A qué clase van a parar, y por qué importa que sea ésa

12 de 13 caen en `epithelial-cell`. En un carcinoma de mama una figura mitótica **es** una
célula epitelial, así que el modelo no la está confundiendo con estroma ni con un linfocito: la
está poniendo en su clase padre y perdiendo la distinción fina. El único caso fuera de esa
lectura es la marca 4, que salió `neutrophil`.

Esto encaja con la explicación de dominio de `cruce_marcas.md` §2.b — la clase de mitosis de
HoVer-NeXt se entrenó y validó **solo en colon**, mientras que segmentar y tipificar núcleos en
mama sí tiene número propio y bueno (mama 6ª de 19 tejidos). Acá se ve exactamente esa forma:
lo que sabe hacer fuera de su tejido lo hace bien, y lo que no fue validado fuera de colon es lo
que falla.

## 5. Qué habilita, en orden de costo

1. **Una segunda etapa de clasificación sobre las instancias que ya existen.** El caro (barrer
   la lámina, segmentar 238.329 núcleos) ya está pago y su salida está en disco. Un
   reclasificador solo necesita el recorte alrededor de cada centroide.
2. **Recalibrar la cabeza de clase.** Antes de reentrenar nada hay que ver si `mitosis` quedó
   segunda por poco o si no aparece — ver §7.
3. **Lo que este resultado descarta**: no hace falta tocar la segmentación, ni cambiar de
   modelo de instancias, ni volver a correr HoVer-NeXt para el eje de mitosis.

Ojo con el orden: el 13 de 26 es sobre **una** lámina y 26 marcas. B1 lleva el denominador a
94 sobre 12 láminas, y ese número es el que debería decidir cuánto se invierte, no éste.

## 6. Cómo se verificó la geometría antes de usarla

`class_inst.json` y `pinst_pp.zip` están en el sistema de coordenadas interno de HoVer-NeXt, y
que coincida con openslide level 0 **no se asumió**:

- `ds_factor = LUT_MAGNIFICATION_X[argmax] / level`. La lámina tiene mpp 0,465, que casa con el
  0,485 de la tabla a `rtol=0,2`, y Lizard tesela a 20× ⇒ **`ds_factor = 1`**
  (`hover_next_reference/src/post_process_utils.py:656`).
- Comprobación empírica, que es la que vale: los **177** centroides de clase 7 de
  `class_inst.json` reproducen las **177** filas de `pred_mitosis.tsv` con `x = columna`,
  `y = fila` — 177 de 177, sin una sola excepción. Y `pinst_pp[fila, columna]` devuelve el id de
  la instancia cuyo centroide es ése.
- Al geojson se le aplica el mismo offset ya derivado (`dx=3829, dy=0`) que usa el cruce.

## 7. Qué no se afirma

- **Nada de esto es precisión.** Las marcas son positivos parciales: lo no marcado no es
  negativo, y ninguna detección se llama acá falso positivo.
- **No se afirma qué ES cada núcleo.** La verdad de campo dice `Mitosis` y nada más; que la
  instancia recibiera `epithelial-cell` describe **a dónde fue a parar**, no una segunda opinión.
- **No se midió si `mitosis` quedó segunda.** El reparto de arriba es el argmax, y separar
  «quedó segunda por poco» (se arregla con umbral) de «no aparece» (hay que reentrenar) exige
  las probabilidades por instancia. Están en `129741_raw_256_cls.zip`, pero por **tesela**
  (51.192 × 8 × 256 × 256): hay que reconstruir la grilla de teselas para consultarlas, y eso es
  trabajo aparte. **Queda abierto, y es lo que decide entre los puntos 1 y 2 de §5.**
- **Es una lámina.** 13 marcas falladas no sostienen un reparto de clases: sostienen el hallazgo
  binario (segmentadas sí / no), que salió 13-0.
- Unidad: **marcas** (26 en la 129741). No parches (28) ni detecciones (177).
