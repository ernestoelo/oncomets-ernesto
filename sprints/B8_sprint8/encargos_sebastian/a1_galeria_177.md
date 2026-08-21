# Encargo 2 — las imágenes de las 177 detecciones, y si se parecen entre sí

> Medido el **21-ago-2026**, CPU post-hoc. Script:
> [scripts/galeria_mitosis_129741.py](../../../scripts/galeria_mitosis_129741.py).
> Salidas: `results/b8_hovernext_129741/galeria_mitosis/`.

## 1. Los tres bloques

| lámina de contacto | n | qué muestra |
|---|---|---|
| `bloque_sin_marca.png` | **164** | las detecciones que no acreditaron ninguna marca |
| `bloque_acertadas.png` | **13** | la detección con la marca del patólogo encima |
| `bloque_falladas.png` | **13** | la marca que se escapó, centrada, sin detección cerca |

164 + 13 = **177** = las filas de `pred_mitosis.tsv`. Es la verificación del plan y cierra.
Recortes a resolución nativa, ventana de **128 px = 59,5 µm** de lado (una figura mitótica
mide 10–20 µm, así que entra con contexto alrededor).

## 2. La respuesta: sí se parecen, y mucho más de lo que se esperaría

Cortando el dendrograma en cuatro familias, **145 de las 164 caen en una sola**:

| familia | n | brillo mediano | saturación | fracción de fondo |
|---|---|---|---|---|
| #1 | 15 | 208,8 | 0,112 | **0,647** |
| #2 | 1 | 170,3 | 0,236 | 0,397 |
| **#3** | **145** | **142,0** | **0,341** | **0,023** |
| #4 | 3 | 151,6 | 0,308 | 0,329 |

- **#3 (145 de 164, el 88 %)** es epitelio tumoral denso: recortes oscuros, saturados y sin
  fondo (2 % de píxeles claros). Visualmente el objeto circulado es un núcleo hipercromático
  y condensado, que es exactamente la forma que la herramienta busca.
- **#1 (15)** es la familia que se separa sola y es la que hay que mirar: recortes **claros**
  y con **65 % de fondo** — tejido laxo, adiposo o borde de la lámina, con un núcleo oscuro
  aislado. Ocupan la primera fila de la lámina de contacto.
- **#2 y #4 (4 en total)** son intermedios sueltos, no una familia.

O sea que la respuesta al encargo es **sí**: el grueso de las 164 es homogéneo y del mismo
tipo que las 13 acertadas, y lo que se despega es un grupo chico y bien delimitado.

## 3. Lo que NO se afirma, y acá importa más que en otros lados

- **Las 164 NO son falsos positivos.** El patólogo marca solo donde la evidencia es clara, así
  que una detección fuera de las 26 puede ser una mitosis real sin marcar
  ([[anotaciones-patologo-qupath]]). **No se calcula precisión** y ningún panel las pinta
  como error.
- **El parecido es de PÍXELES, no semántico.** El vector es 16×16 RGB + histograma de color;
  el orden es PCA + linkage `average` + *optimal leaf ordering*. Que dos vecinos se parezcan
  significa que comparten color y textura, **no** que sean la misma entidad biológica.
- **Los descriptores de la tabla no son las features del clustering.** Brillo, saturación y
  fracción de fondo se calculan aparte, para poder decir *en qué* se parecen sin apelar a
  «se ven distintas».
- **No se ordena por confianza**: `pred_mitosis.tsv` no trae score. Sus columnas son
  `x  y  name  color` y nada más.
- **`k = 4` es una elección, no un resultado.** Con otro corte los 145 se subdividen; lo que
  no cambia con el corte es que la familia clara de 15 se separa primero.

## 4. El bloque que más informa es el de las 13 falladas

Es el único que muestra en qué se equivoca el detector, y se lee junto con
[A0](a0_segmentadas_o_no.md): en los 13 recortes hay un núcleo segmentado bajo la marca, con
figuras mitóticas visualmente clásicas en varias, y lo que falló fue la **clase** (12
`epithelial-cell`, 1 `neutrophil`), no la segmentación.

## 5. Unidad

**Detecciones (177)** en los bloques 1 y 2; **marcas (26)** en el bloque 3. No parches (28).
