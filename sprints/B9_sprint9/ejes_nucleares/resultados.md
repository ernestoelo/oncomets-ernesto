# Resultados — los dos ejes nucleares de CPU

> Pre-registro: [`prereg.md`](prereg.md). Lo de acá se lee contra él, no al revés.
>
> Estado al **28-ago-2026**: los **dos ejes están medidos**. El eje 4 (control positivo)
> pasa; el eje 3 ordena, con el `n` honesto y las salvedades del §2.b.

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

## 2. Eje 3, pleomorfismo: los descriptores ORDENAN, y el `n` honesto son 10 láminas

**Pregunta**: ¿el tamaño del núcleo que HoVer-NeXt segmentó debajo de cada marca de grado ordena
alto > moderado > bajo?

**Unidad**: punto contra punto. Cada una de las 107 marcas se resuelve a una instancia de
`pinst_pp` y se leen **sus** descriptores. El área del polígono del patólogo no se usa en ninguna
tabla ni figura ([`prereg.md`](prereg.md) §0.b).

**Resultado primario, H3.a** (percentil del área dentro de la población epitelial de la propia
lámina, población restringida a las marcas que HoVer-NeXt llamó `epithelial-cell`):

| Grado | marcas | láminas | percentil mediano | p25 | p75 |
|---|---|---|---|---|---|
| bajo | 15 | 2 | **75,1** | 61,3 | 80,3 |
| moderado | 4 | **1** | **92,1** | 83,8 | 97,0 |
| alto | 66 | 7 | **98,9** | 95,9 | 99,9 |

| Estadístico | valor | criterio pre-registrado |
|---|---|---|
| ρ de Spearman **por lámina** (n = 10) | **+0,809** | ρ > 0 |
| nulo exacto, permutando el grado entre las 10 láminas (360 asignaciones) | `p` = **0,0056** bilateral · 0,0028 unilateral | |
| ρ de Spearman por marca (n = 85, marcas **no** independientes) | +0,626 | |
| AUC moderado > bajo, por marca | 0,833 | > 0,5 |
| AUC alto > moderado, por marca | 0,739 | > 0,5 |

**Los dos AUC de pares contiguos están por encima de 0,5 y ρ es positivo en las cuatro
variantes** (dos poblaciones × dos niveles). En la dirección pre-registrada, y no es H3 nula ni
H3 regresión.

### 2.a La población completa ordena igual pero no despega del nulo

Las dos poblaciones se declararon antes y se reportan juntas ([`prereg.md`](prereg.md) §3):

| Población | nivel | ρ | `p` del nulo exacto | AUC mod>bajo | AUC alto>mod |
|---|---|---|---|---|---|
| (i) restringida, n = 85 marcas | lámina (10) | **+0,809** | **0,0056** | 0,833 | 0,739 |
| (i) restringida | marca (85) | +0,626 | — | | |
| (ii) completa, n = 107 marcas | lámina (12) | +0,552 | **0,0673** | 0,808 | 0,799 |
| (ii) completa | marca (107) | +0,581 | — | | |

**La completa no cruza 0,05 a nivel lámina**, y el pre-registro dice que cuando los dos niveles
discrepan manda el de lámina. O sea: el ordenamiento es consistente en signo en las cuatro
variantes, y **el `p` sólo despega en la población restringida**. La lectura honesta es
«ordena, con `p` = 0,0056 sobre 10 láminas en la población limpia y 0,0673 sobre 12 en la
completa», no «da significativo».

La diferencia entre las dos tiene mecanismo, no es ruido: la completa mete marcas resueltas a
clases distintas, y **el área absoluta no es comparable entre clases de HoVer-NeXt** (§2.d).

> **ADDENDUM 28-ago-2026 (cierre) — el `p` de la restringida es el PISO, y la completa no está
> limitada por el diseño.** Sale de dibujar el nulo, no de re-medir: los números de arriba no
> cambian. El §1 ya decía «el `p` es el piso» del eje 4; acá vale también, y por una razón más
> fuerte.
>
> | población | láminas | asignaciones | ρ obs | ρ **máximo** posible | `p` obs | **piso** del `p` |
> |---|---|---|---|---|---|---|
> | (i) restringida | 10 | 360 | **+0,809** | **+0,809** | 0,0056 | **0,0056** |
> | (ii) completa | 12 | 2970 | +0,552 | +0,836 | 0,0673 | 0,0007 |
>
> **En la restringida el ρ observado ES el máximo de las 360 asignaciones**: la observada es la
> única que ordena perfecto (`p` unilateral 1/360, bilateral 2/360). Con este reparto
> (2 bajo / 1 moderado / 7 alto) **no existe un resultado mejor**, así que 0,0056 no es «el `p`
> que salió» sino el mínimo que el diseño puede dar, alcanzado. Leerlo como holgura contra el
> 0,05 convencional es un error: no hay holgura, hay techo.
>
> **Y la completa no está frenada por el diseño**, que es la mitad que faltaba: tenía un piso
> cien veces más bajo disponible (0,0007) y quedó en 0,0673. Lo que la frena son **dos láminas de
> `alto` que caen por debajo de las de `bajo`** (la 106552 en 70,3 y la B25-158899 en 73,1,
> contra 66,7 y 75,1 de las dos de `bajo`), las dos con marcas resueltas a clases no epiteliales.
> Es el mecanismo del §2.d, escrito en la unidad del nulo. Sin esto, «la restringida despega y la
> completa no» se lee como «más láminas, peor `p`», que es al revés.
>
> Detalle: [`../auditoria_coherencia/hallazgos.md`](../auditoria_coherencia/hallazgos.md) C1-C2.

### 2.b El `n` real es peor que 10 láminas, y hay que decirlo

El reparto por lámina, que es lo que el §0.c del pre-registro obligaba a mirar:

| Grado | Lámina | `alineada` | marcas | epiteliales | clases que le tocaron |
|---|---|---|---|---|---|
| bajo | 103762 | sí | 9 | 9 | epithelial 9 |
| bajo | 110616 | sí | 7 | 6 | epithelial 6, lymphocyte 1 |
| moderado | 109609 | sí | 10 | **0** | plasma 7, connective 3 |
| moderado | 164001 | **no** | 4 | 4 | epithelial 4 |
| alto | 106552 | sí | 8 | 2 | connective 4, epithelial 2, lymphocyte 2 |
| alto | 124729 | sí | 13 | 13 | epithelial 13 |
| alto | 124806 | sí | 10 | 10 | epithelial 10 |
| alto | 126504 | sí | 8 | 8 | epithelial 8 |
| alto | 128194 | sí | 11 | 11 | epithelial 11 |
| alto | 129741 | sí | 14 | 14 | epithelial 14 |
| alto | 144317 | sí | 11 | 8 | epithelial 8, connective 3 |
| alto | B25-158899 | **no** | 2 | **0** | connective 2 |

Tres cosas que la tabla de arriba no deja esconder:

1. **El grado `moderado` de la población restringida son 4 marcas de UNA lámina**, la 164001,
   que además es una de las dos con `alineada: false`. La 109609 aporta **cero** epiteliales: sus
   10 marcas de moderado cayeron sobre 7 plasmáticas y 3 conectivas. O sea que el peldaño del
   medio del resultado primario descansa sobre una sola lámina no alineada.
2. Por eso la restringida corre sobre **10 láminas y no 12**: se caen la 109609 y la
   B25-158899, las dos por quedarse sin ninguna marca epitelial.
3. **Los AUC por lámina de la restringida valen 1,000 con `n` = 1 en uno de los dos grupos.**
   Un AUC con un solo elemento de un lado no es una medición; están en el log por completitud y
   no se citan.

### 2.c El área cruda (H3.b) ordena MÁS, y eso es lo esperado, no una buena noticia

| Población | nivel | ρ | `p` exacto | mediana bajo / mod / alto (µm²) |
|---|---|---|---|---|
| (i) restringida | lámina (10) | +0,749 | 0,0222 | 31,1 · 65,8 · 102,8 |
| (ii) completa | lámina (12) | +0,652 | 0,0256 | 31,0 · 40,1 · 93,8 |

H3.b es la variante **contaminada por el efecto de lámina** y el pre-registro ya decía qué
significa: si cruda ordena y normalizada no, la conclusión sería efecto de lámina. Acá **ordenan
las dos**, así que el efecto de lámina no explica el resultado por sí solo. Dato que lo apoya: el
área epitelial mediana **de la lámina entera** va de 22,7 a 46,5 µm² entre las doce, un factor 2
que es exactamente lo que la normalización intra-lámina cancela.

### 2.d Hallazgo que sale de acá: el área no es comparable entre clases de HoVer-NeXt

`pinst_pp` no es el contorno del núcleo: es la región que sobrevive al umbral de foreground del
post-proceso, y **ese umbral está afinado por clase**
(`hover_next_reference/src/post_process_utils.py:370-409`, umbrales en
`lizard_convnextv2_tiny/liz_test_param_dict.json`, entrada `best_fg_f1` porque el job corrió
`--metric f1`):

| clase | neutrophil | **epithelial** | lymphocyte | **plasma** | eosinophil | **connective** | mitosis |
|---|---|---|---|---|---|---|---|
| umbral fg | 0,5 | **0,6** | 0,5 | **0,3** | 0,5 | **0,3** | 0,5 |

`epithelial-cell` tiene **el umbral más alto de las siete**, así que es la clase más erosionada.
Medido en la 109609, una plasmática sale **más grande** (25,7 µm²) que una epitelial (22,7 µm²),
que biológicamente está al revés. **Consecuencia**: cualquier tabla que mezcle marcas resueltas a
clases distintas mezcla umbrales, y el reparto de clases **cambia con el grado** (moderado trae 7
plasmáticas de 14). Es el mecanismo del §2.a, y es la razón por la que la población limpia es la
restringida.

Esto también explica el chequeo de sanidad que el pre-registro había declarado y **no se cumple
en 4 de 12 láminas**: el área epitelial mediana va de 22,7 a 46,5 µm² y quedan por debajo de los
30 µm² la 103762 (23,8), la 106552 (26,2), la 109609 (22,7) y la B25-158899 (28,1). **No es un
error de escala**, y eso se verificó antes de explicarlo (§2.f).

### 2.e Los descriptores secundarios: el eje mayor sigue al área, la forma casi no aporta

Sobre la población restringida, percentil intra-lámina:

| Descriptor | ρ por lámina (n = 10) | `p` exacto | mediana bajo / mod / alto |
|---|---|---|---|
| área (primario) | +0,809 | 0,0056 | 75,1 · 92,1 · 98,9 |
| eje mayor | +0,749 | 0,0222 | 47,5 · 90,8 · 95,2 |
| excentricidad | +0,629 | 0,0556 | 16,3 · 27,1 · 30,7 |

La **excentricidad no despega del nulo**, y su AUC alto > moderado es **0,447**, o sea por debajo
de 0,5: la forma no ordena los dos grados altos. Lo que ordena es el **tamaño**, que es lo que el
pre-registro había puesto como descriptor primario y la razón por la que lo era.

**La razón de aspecto no se reporta como descriptor aparte.** `exc = sqrt(1 − (menor/mayor)²)` y
`razón = mayor/menor` son monótonas una de otra (verificado: Spearman = **1,000000 exacto** sobre
las 43.585 instancias de la 109609), así que todo estadístico de rango da idéntico. Presentarlas
como dos sería contar dos veces el mismo descriptor. Las dos columnas siguen en el CSV porque sus
valores absolutos difieren.

### 2.f Las tres verificaciones que sostienen los números

1. **Escala, contra la fuente**: el shape de `pinst_pp` reproduce las dimensiones de level 0 del
   `.bif` en **las 12 láminas**, con un recorte de 128 a 243 px (menos de una tesela). Un error de
   nivel daría un factor 2 o 4. Está cableado como chequeo duro en
   `scripts/b9_descriptores_nucleos.py` (`DIMS_LEVEL0`), leído con openslide desde `clam_latest`,
   que es el env con la libopenslide parchada (workaround K).
2. **Sin transposición fila/columna**: el centroide que sale de los momentos coincide con el de
   `class_inst.json` con **mediana 0,00 px en las 12 láminas**. Es la trampa que documenta
   [[hovernext-salida-geometria-y-clases]] y sale gratis.
3. **Regresión del gate**: **107 de 107** marcas resuelven, cero sin instancia, y el reparto de
   clases del gate del 27-ago se reproduce **exacto**.

### 2.g Una marca de 107 depende del desempate, y no cambia nada

El gate se corrió con un script que no quedó en el repo, así que no se puede diffear. Al
reimplementarlo aparecieron **dos desempates razonables** para las marcas cuyo centroide cae en
fondo (10 de 107): `centroide`, la instancia cuyo centroide global está más cerca (es el patrón
de `a0_segmentadas_o_no.py:118-135`, el que **cita** el pre-registro §1), y `pixel`, la instancia
del píxel no-cero más cercano.

Difieren en **una marca de 107**: la 106552 #4, con 9 instancias en su ventana, va a `connective`
por centroide y a `epithelial` por píxel. Ésa es exactamente la diferencia contra el gate
(66 + 9 contra 67 + 8 en `alto`), o sea que **la regla `pixel` reproduce el gate exacto** y
`centroide` difiere en esa sola marca. Un bug de offset o de path movería muchas marcas y las dos
reglas a la vez, así que esto no es eso.

Se corrieron **las dos**. El primario cambia en el tercer decimal:

| regla | ρ por lámina | `p` exacto | ρ por marca |
|---|---|---|---|
| `centroide` (primario, la que cita el prereg) | +0,809 | 0,0056 | +0,626 |
| `pixel` (la que reproduce el gate) | +0,809 | 0,0056 | +0,624 |

**Ninguna conclusión depende del desempate.**

### 2.h Qué NO dice este resultado

- **No es una validación del grado de Nottingham.** Nottingham puntúa la variación de una
  población entera en el campo de peor grado; acá son núcleos que el patólogo eligió **como
  ejemplares**. Que los tres grados ordenen dice que eligió núcleos progresivamente más grandes,
  y eso es consistente con el grado y también con cómo se marca.
- **Los percentiles son altos en los tres grados** (bajo ya está en el 75). El patólogo marca
  núcleos grandes para su lámina en cualquier grado; lo que separa es **cuánto**.
- **No separa grado de efecto de lámina más allá de lo que cancela la normalización.** El grado
  sigue confundido con la lámina, sin un solo cruce, y el peldaño del medio es una lámina.
- **No se calculó precisión, F1 ni PQ**, y no se puede: positivos parciales.
- **El área absoluta no mide el núcleo**: mide el núcleo *bajo el umbral de foreground de su
  clase* (§2.d). Sirve para comparar dentro de una clase, no entre clases ni contra la literatura.

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
- **El eje 3 no valida Nottingham ni separa grado de lámina** (§2.h).
- **El área de una instancia de HoVer-NeXt no es comparable entre clases** (§2.d), así que
  ninguna cifra en µm² de acá se compara contra la literatura ni contra otra clase.

## 4. Artefactos

| Qué | Path |
|---|---|
| Fracción epitelial por región (209 filas) | `results/b9_nucleos/regiones_epi_estroma.csv` |
| Las 200 traslaciones del nulo por región | `results/b9_nucleos/regiones_nulo.npy` |
| Log de la corrida | `logs/b9_epi_estroma.log` |
| Script | `scripts/b9_epitelio_estroma.py` |
| Descriptores de todas las instancias, por lámina | `results/b9_nucleos/<slide>_nucleos.npz` (gitignored) |
| Las 107 marcas resueltas, con grado y descriptores | `results/b9_nucleos/marcas_grado.csv` |
| Logs del eje 3 | `logs/b9_descriptores_nucleos.log`, `logs/b9_pleomorfismo.log` |
| Scripts del eje 3 | `scripts/b9_descriptores_nucleos.py`, `scripts/b9_pleomorfismo.py` |
| **Las figuras de los dos ejes** (4 láminas nativas) | `figuras/generate_figuras_ejes34.py` → `figuras_ejes_3_4.pptx` (gitignored, regenerable) |
| Los 48 números que quedan dibujados | `figuras/numeros_figuras.csv` |
