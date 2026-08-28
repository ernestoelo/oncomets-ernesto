# Resultados — los dos ejes nucleares de CPU

> Pre-registro: [`prereg.md`](prereg.md). Lo de acá se lee contra él, no al revés.
>
> Estado al **27-ago-2026**: el **eje 4 está medido y pasa**. El **eje 3 no se corrió**.

---

## 1. Eje 4, el control positivo: PASA

**Pregunta**: ¿la fracción de núcleos epiteliales que da HoVer-NeXt dentro de las regiones que el
patólogo marcó como epitelio es mayor que dentro de las que marcó como estroma?

**Unidad**: región contra punto. **Denominador**: 209 regiones de las 12 láminas (188 del grupo
epitelio, 21 del grupo estroma); **11 quedaron sin ningún núcleo adentro** y salen del cálculo.

| | valor | criterio pre-registrado |
|---|---|---|
| AUC de rango (epitelio > estroma) | **0,906** | ≥ 0,80 |
| Nulo por traslación, media | 0,439 | debajo del observado |
| Nulo, percentil 97,5 | 0,528 | |
| `p` | **0,0050** | < 0,05 |
| Sólo las 10 láminas con `alineada: true` | **0,937** (n = 170) | reportado aparte |

**El `p` es el piso**: con 200 traslaciones el mínimo alcanzable es 1/201 = 0,00498, así que el
resultado es «por debajo de 1 en 201», no un valor exacto. Ninguna de las 200 iteraciones del
nulo llegó al observado.

### 1.a Por clase, que es donde se ve que el número no es un artefacto del estadístico

| Clase | grupo | `n` | `f_epi` mediana | p25 | p75 |
|---|---|---|---|---|---|
| `CDIS_solido` | epitelio | 8 | **0,914** | 0,783 | 0,965 |
| `AreaSolida` | epitelio | 45 | 0,857 | 0,549 | 0,946 |
| `DCIS` | epitelio | 6 | 0,835 | 0,333 | 0,904 |
| `Tumor` | epitelio | 98 | 0,792 | 0,215 | 0,926 |
| `AreaTubular` | epitelio | 25 | 0,754 | 0,333 | 0,856 |
| `CDIS_papilar` | epitelio | 6 | **0,242** | 0,112 | 0,495 |
| `Stroma` | estroma | 12 | **0,000** | 0,000 | 0,000 |
| `Tejido Adiposo` | estroma | 9 | **0,000** | 0,000 | 0,038 |

Las dos clases de estroma dan **cero exacto** en la mediana y las cuatro clases sólidas de
epitelio dan entre 0,75 y 0,91. Ése es el chequeo de sanidad que se había declarado antes de
medir, y no depende del estadístico ni del nulo.

### 1.b Lo que llama la atención y no se explica acá

- **`CDIS_papilar` da 0,242**, o sea que se comporta como estroma estando en el grupo epitelio.
  Son **6 marcas de una sola lámina**, así que no sostiene número propio. Candidato natural:
  el patrón papilar tiene ejes fibrovasculares adentro, que son tejido conectivo de verdad. **No
  se afirma**: se deja anotado.
- **El nulo se centra en 0,439 y no en 0,50.** Las regiones de epitelio son más grandes que las
  de estroma, así que al trasladarlas no muestrean el mismo fondo. No invalida el contraste (el
  observado está a más de 20 puntos del percentil 97,5 del nulo), pero el nulo no es simétrico y
  conviene decirlo.
- **El `p25` de `Tumor` es 0,215**, muy por debajo de su mediana 0,792. `Tumor` es la clase con
  más marcas (98) y la más heterogénea: hay regiones marcadas como tumor con mayoría de núcleos
  conectivos. Es coherente con que el patólogo circunscribe un área tumoral, no un epitelio puro.

### 1.c Consecuencia

El método (offsets, membresía en la región, clases de HoVer-NeXt) **funciona**, así que la
condición de lectura del eje 3 que fijaba el pre-registro **queda satisfecha**. Un resultado nulo
en el eje 3 ya no se podrá atribuir al instrumento.

### 1.d Un bug del nulo que vale para la próxima vez

La primera corrida dio **cero traslaciones válidas** y el nulo salió vacío. La causa: «tejido» se
había definido como **celda de 8 px con al menos un núcleo**, y como un núcleo aporta **un
centroide**, eso marcaba el **0,2 a 0,9 %** de la grilla; ninguna traslación pasaba el umbral de
90 % de cobertura. Con el tejido definido por **bloque de 256 px** (el lado del parche) el mismo
material da **12 a 21 %** y el nulo corre. La resolución a la que «hay tejido acá» es verdad
**no** es la resolución a la que se cuenta.

---

## 2. Eje 3, pleomorfismo: NO CORRIDO

Está pre-registrado ([`prereg.md`](prereg.md) §3) y su gate pasó (**107 de 107** marcas caen
sobre un núcleo segmentado), pero **no se midió nada**. Faltan los dos scripts que describe el
handoff. No hay ningún número de este eje en ningún lado, y si aparece uno, no salió de acá.

---

## 3. Qué no se afirma

- **No se calculó precisión, F1 ni PQ**, y no se puede: el geojson son positivos parciales.
- **No se llamó falso positivo** a ninguna detección sin marca.
- **El 0,906 no es una métrica de HoVer-NeXt.** Es la separación entre dos grupos de regiones
  dibujadas por el patólogo, medida con las clases de HoVer-NeXt. Dice que el instrumento
  distingue epitelio de estroma sobre este material, no cuán bueno es en absoluto.
- **No se afirma que las 12 láminas alcancen** para el eje 3. El grupo estroma son 21 regiones y
  `Stroma` vive en 7 láminas.
- **`CDIS_papilar` no se interpreta** (§1.b).

## 4. Artefactos

| Qué | Path |
|---|---|
| Fracción epitelial por región (209 filas) | `results/b9_nucleos/regiones_epi_estroma.csv` |
| Las 200 traslaciones del nulo por región | `results/b9_nucleos/regiones_nulo.npy` |
| Log de la corrida | `logs/b9_epi_estroma.log` |
| Script | `scripts/b9_epitelio_estroma.py` |
