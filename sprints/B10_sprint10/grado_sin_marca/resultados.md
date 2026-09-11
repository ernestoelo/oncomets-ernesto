# Resultados O1 — el tamaño solo reencuentra los núcleos de ALTO grado, y no los de bajo

> Pre-registro: [`prereg.md`](prereg.md), escrito y commiteado antes del código. Lo de acá se lee
> contra él, no al revés.
>
> Medido el **9-sep-2026**. CPU, sin GPU. Driver `scripts/b10_grado_sin_marca.py`, log
> `logs/b10_grado_sin_marca.log`, ~4 min sobre 21 láminas.

---

## 0. Antes de leer nada: el brazo con máscara NO se ejecutó, y por qué

El pre-registro declaraba dos brazos. **El brazo B (máscara `Tumor`, D2) es degenerado por
construcción** y su recall es **0 en los 400 registros que produjo**, en las 20 láminas y en todos
los peldaños. La causa no es el descriptor:

**Ninguna de las 187 marcas de grado cae dentro de ningún polígono `Tumor`**, y al ampliar la
prueba a **todas** las clases del geojson, tampoco cae ninguna en ninguna. `Tumor` no delimita el
tumor invasor: son parches ejemplares de 2,5 a 26 mil µm² que suman **0,013 a 0,59 mm² por lámina**,
menos del 0,1 % de la superficie, y la distancia de una marca al borde del `Tumor` más cercano
tiene **mediana 2925 µm** y máximo **13.117 µm**. El resultado **no depende del offset**: marcas y
polígonos reciben la misma traslación, así que la contención es invariante.

Ernesto decidió el 9-sep correr **solo el brazo A** y llevarle a Sebastián la pregunta de qué
región corresponde. **No se eligió una máscara nueva después de ver que la pre-registrada daba
cero.** Detalle: [[marcas-grado-fuera-de-toda-region-anotada]].

## 1. El gate: 187 de 187, y reproduce el B9

Cada marca resuelve a un núcleo segmentado, con la regla `centroide` del pre-registro:

| Grado | marcas | epithelial | connective | plasma | lymphocyte | sin instancia |
|---|---|---|---|---|---|---|
| alto | 87 | 74 | 11 | 0 | 2 | **0** |
| moderado | 84 | 49 | 18 | 12 | 5 | **0** |
| bajo | 16 | 15 | 0 | 0 | 1 | **0** |

**`bajo` reproduce el B9 exacto** (15 epiteliales + 1 linfocito). El chequeo duro de escala
(`DIMS_LEVEL0`) y el de transposición pasan en las 21; 3 de las 9 nuevas caen bajo el rango de área
epitelial del pre-registro, por la misma causa conocida (umbral de foreground por clase), que en el
B9 afectaba a 4 de 12.

**El peldaño del medio dejó de ser una lámina**: `moderado` pasa de **4 marcas epiteliales de una
lámina no alineada** a **49 de 10 láminas**. Es el cambio que justificaba correr esto.

## 2. El denominador alcanzable: 145 de 187, no 187

Los candidatos son los núcleos que HoVer-NeXt llamó `epithelial-cell`. **Una marca cuyo núcleo no
es epitelial no la recupera nadie**, por bueno que sea el descriptor: 49 de las 187 resuelven a
`connective`, `plasma` o `lymphocyte`. Medido con la misma regla que usa la escalera (núcleo
epitelial más cercano dentro de 15 µm), **145 de 187 son alcanzables**.

Es la forma operativa de declarar el denominador que exige P2, y **cambia la lectura**: 53 sobre
187 es 28,3 %, pero sobre lo alcanzable es **36,6 %**. Las dos cifras van juntas en toda tabla.

## 3. La escalera de carga (brazo A, descriptor percentil)

**Unidad**: núcleo candidato para `N`, **mm² para la carga**, y la carga es la unión de parches de
256 px que contienen a los `N` primeros, no `N × 0,0142`.

| N | láminas | marcas | alcanzables | recall | % de alcanzables | carga total mm² | mm²/lámina | nulo medio | nulo p97,5 |
|---|---|---|---|---|---|---|---|---|---|
| 10 | 21 | 187 | 145 | **8** | 5,5 % | 2,8 | 0,13 | 0,01 | 0,0 |
| 20 | 21 | 187 | 145 | 10 | 6,9 % | 5,4 | 0,26 | 0,03 | 1,0 |
| 50 | 21 | 187 | 145 | 17 | 11,7 % | 12,7 | 0,60 | 0,07 | 1,0 |
| 100 | 21 | 187 | 145 | 24 | 16,6 % | 24,1 | 1,15 | 0,12 | 1,0 |
| 200 | 21 | 187 | 145 | 31 | 21,4 % | 42,5 | 2,02 | 0,27 | 2,0 |
| 500 | 21 | 187 | 145 | **53** | 36,6 % | 85,4 | 4,07 | 0,64 | 3,0 |
| 1000 | 21 | 187 | 145 | 68 | 46,9 % | 135,5 | 6,45 | 1,33 | 4,0 |
| 2000 | 21 | 187 | 145 | **86** | 59,3 % | 200,6 | 9,55 | 2,51 | 7,0 |
| 5000 | **19** | **170** | **137** | 102 | 74,5 % | 299,1 | 15,74 | 5,22 | 11,0 |

**El peldaño de 5000 corre sobre 19 láminas, no 21**: la 109609 (2348 candidatos) y la 110616
(4828) no llegan a tener 5000 núcleos epiteliales, así que salen y el denominador baja a 170. Los
peldaños de 10 a 2000 son los que tienen las 21.

**H_O1 se cumple, y con margen.** En todos los peldaños el recall observado está **muy por encima
del percentil 97,5 del nulo por traslación**: 53 contra 3 en N=500, 86 contra 7 en N=2000. Ninguna
de las 200 traslaciones se acercó, así que el `p` es **el piso, «por debajo de 1 en 201»**, y no un
valor exacto.

## 4. Lo que la escalera esconde si no se abre por grado

Éste es el resultado, y no está en la fila agregada:

| N | alto (de 76 alcanzables) | moderado (de 53) | bajo (de 16) |
|---|---|---|---|
| 200 | **27** (35,5 %) | 4 (7,5 %) | **0** |
| 500 | **41** (53,9 %) | 12 (22,6 %) | **0** |
| 2000 | **57** (75,0 %) | 23 (43,4 %) | 6 (37,5 %) |

**El tamaño reencuentra los núcleos de alto grado y no los de bajo.** En el 0,3 % de los núcleos de
la lámina (N=500, ~4 mm²) el orden por tamaño recupera **más de la mitad de las marcas de alto** y
**ninguna de las de bajo**.

**No es un fracaso del método: es lo que «bajo grado» significa.** El B9 ya había medido que el
percentil mediano del área bajo cada marca es **75,1 · 92,1 · 98,9** para bajo, moderado y alto: un
núcleo de bajo grado está en el percentil 75 de su lámina, así que un top-N por tamaño, que es el
percentil 99,5, no lo va a contener nunca. La escalera es la consecuencia aritmética de aquella
tabla, vista desde el otro lado.

**Consecuencia para la pregunta de Sebastián**: HoVer-NeXt solo **sí** reencuentra lo que el
patólogo marcó, pero **solo donde la marca coincide con «el núcleo más grande»**. Para bajo y
moderado hace falta otra cosa que el tamaño, y el CAP dice cuál: **dispersión**, no tendencia
central ([`../score_grado/estudio_score.md`](../score_grado/estudio_score.md) §2).

## 5. Los dos descriptores dan el MISMO resultado, y eso tiene mecanismo

| N | percentil intra-lámina | razón contra proxy de epitelio normal |
|---|---|---|
| 200 | 31 | **31** |
| 500 | 53 | **53** |
| 2000 | 86 | **86** |

Idénticos, no parecidos. **El proxy es una constante por lámina**, así que `área / proxy` es una
transformación **monótona** del área dentro de la lámina, y el percentil intra-lámina también lo
es. Dos funciones monótonas del mismo descriptor producen **el mismo orden**, y por lo tanto el
mismo top-N y el mismo recall. Es el patrón [[descriptores-monotonos-cuentan-doble]] otra vez, y
presentarlos como dos mediciones sería contar una sola dos veces.

**Esto no anula el descriptor del CAP**: dice **dónde** aporta, que no es acá. La razón contra
epitelio normal aporta cuando se comparan **láminas entre sí** o se usan los **cortes absolutos**
del protocolo (1,5-2× y >2,5× en diámetro), que es un umbral **sin parámetro libre**. Dentro de una
lámina, para ordenar núcleos, no agrega nada sobre el percentil.

## 6. Por lámina, en N=500

De las 21, **13 tienen recall por encima de su nulo medio** y 8 dan cero. Las 8 son 6 de `moderado`
(131461-1, 132844, 133677, 142541-1, 154144, y la 109609 con 1 sola alcanzable), las 2 de `bajo`
(103762, 110616) y la B25-158899, que aporta 1 marca alcanzable de 2. Las que mejor rinden son de
`alto`: la 124806 recupera **10 de 10** y la 128194 **8 de 11**.

La carga por lámina en N=500 va de **2,2 a 5,8 mm²**, o sea que el peldaño es comparable entre
láminas pese a que su tamaño varía por un factor 40 en número de candidatos.

## 6.a Dos cosas que el pre-registro no declaró (medidas el 10-sep)

Ninguna mueve el titular (N=500). Las dos salieron al re-medir la B25-158899 de O3, que tiene
las dos propiedades a la vez ([`../cdis_localizacion/resultados.md`](../cdis_localizacion/resultados.md) §3.b).

**1. El universo de las dos láminas con dos regiones de escaneo.** La 129741 y la B25-158899 tienen
la anotación en una sola de sus dos regiones, y el driver ordenó los núcleos de la lámina entera,
sin el `REGION_ANOTADA` que el B9 aplicó en su escalera (`scripts/b9_escalera_area.py:269`). La
lámina entera es lo que tendría una lámina nueva sin anotar, así que es un default defendible,
pero no estaba declarado. Confinadas a su región con `scripts/b10_grado_region_diag.py`, cuya
fila de lámina entera reproduce `escalera.csv`:

| lámina | universo | candidatos | N=200 | N=500 | N=2000 |
|---|---|---|---|---|---|
| 129741 (14 alcanzables) | lámina entera (publicado) | 87.553 | 2 (2,2 mm²) | 4 (4,4 mm²) | 8 (10,2 mm²) |
| 129741 | región anotada | 43.957 | 4 (1,9 mm²) | 4 (3,6 mm²) | 11 (7,5 mm²) |
| B25-158899 (1 alcanzable) | lámina entera (publicado) | 30.688 | 0 | 0 | 0 |
| B25-158899 | región anotada | 13.666 | 0 | 0 | 0 |

Unidad: marcas recuperadas entre los N núcleos más grandes, con la carga en mm² entre paréntesis.
En `alto`, la fila del §4 pasaría de 27 · 41 · 57 a **29 · 41 · 60**. El titular no se mueve, y
N=200 y N=2000 se mueven en 2 y 3 marcas de 76. **Queda declarado y el driver no se re-corre.**

**2. Las dos láminas con `alineada: false`.** La 164001 (`moderado`, 4 alcanzables, recupera 1 en
N=500) y la B25-158899 (`alto`, 1 alcanzable, 0). El B9 las había declarado como control de sanidad
para reportar aparte (`../../B9_sprint9/ejes_nucleares/prereg.md` §2), y el pre-registro de O1 no.
Sin ellas, N=500 da **52 de 140** alcanzables (37,1 %) contra 53 de 145 (36,6 %): `alto` 41 de 75 y
`moderado` 11 de 49. Nada cambia de lado.

## 7. Qué NO dice este resultado

- **Ni precisión, ni F1, ni PQ.** Positivos parciales. Ningún núcleo grande sin marca es un falso
  positivo: es lo que el patólogo no marcó, no lo que no existe.
- **No es una validación de Nottingham.** El protocolo puntúa la variación de una población en el
  campo de peor grado; acá se persiguen núcleos que el patólogo eligió como ejemplares.
- **El brazo con máscara no se midió**, no midió cero (§0).
- **El proxy de epitelio normal no es epitelio normal**: es epitelio fuera de región anotada, y
  además no movió el resultado (§5).
- **21 láminas no alcanzan.** El grado sigue confundido con la lámina, `bajo` son 2 láminas, y
  ninguna lámina tiene dos grados.
- **No se afirma que las marcas midan grado nuclear de CDIS.** Miden pleomorfismo de lámina hasta
  que Sebastián diga lo contrario ([[marcas-grado-son-pleomorfismo-de-lamina]]).
- **El área en µm² no se compara entre clases de HoVer-NeXt** ni contra la literatura.

## 8. Artefactos

| Qué | Path |
|---|---|
| Escalera por brazo, lámina, descriptor y peldaño (820 filas) | `results/b10_grado_sin_marca/escalera.csv` |
| Resumen por lámina y brazo | `results/b10_grado_sin_marca/resumen_laminas.csv` |
| Gate: clases bajo cada marca | `results/b10_grado_sin_marca/gate_clases.json` |
| Las 200 traslaciones del nulo, por lámina y brazo | `results/b10_grado_sin_marca/nulo.npz` |
| Log | `logs/b10_grado_sin_marca.log` |
| Driver | `scripts/b10_grado_sin_marca.py` |
| Diagnóstico de universo de las dos láminas con dos regiones (§6.a) | `scripts/b10_grado_region_diag.py`, log `logs/b10_grado_region_diag.log` |
