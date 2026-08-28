# Pre-registro — los dos ejes nucleares de CPU (ejes 4 y 3 del inventario)

> Escrito el **27-ago-2026**, antes de medir nada. Regla 9: hipótesis, métrica y dirección
> esperada declaradas antes del código. CPU, sin GPU, sin `sbatch`.
>
> Cubre los dos ejes que el [inventario](../hovernext_tareas/inventario_tareas.md) §4 declaró
> **GO y ya en disco**: el **eje 4** (tumor/estroma, que es el control positivo) y el **eje 3**
> (pleomorfismo y grado nuclear). Se corren en ese orden: si el control positivo falla, el otro
> no se lee.

---

## 0. Tres correcciones de premisa, verificadas antes de escribir código

Las tres cambian el diseño, así que van antes que las hipótesis.

### 0.a Las 107 anotaciones de grado son núcleos sueltos, no regiones

El inventario §4 clasificó el eje 3 como **«región contra población»**: descriptores de los
núcleos *dentro* de cada región contra los de fuera. **Medido, no es así.** Las tres clases de
grado tienen el perfil de tamaño de una marca puntual, idéntico al de `Mitosis`:

| Clase | `n` | área mediana | diámetro equivalente | bbox mediano | % bajo 400 µm² |
|---|---|---|---|---|---|
| `Mitosis` (referencia) | 94 | 218,8 µm² | 16,7 µm | 36×36 px | 82 % |
| `Nucleos alto grado` | 77 | 218,8 µm² | 16,7 µm | 36×36 px | 78 % |
| `Nucleos mod grado` | 14 | 35,5 µm² | 6,7 µm | 16×14 px | 100 % |
| `NucleosBajoGrado` | 16 | 25,6 µm² | 5,7 µm | 12×12 px | 100 % |

Un núcleo epitelial mamario mide 7 a 9 µm de diámetro. Las marcas de grado **son del tamaño de
un núcleo**, no de una población de núcleos. Compárese con las clases que sí son regiones:
`Tumor` 4.025 µm² (216×219 px), `AreaTubular` 7.055 µm², `Tejido Adiposo` 191.364 µm².

**Consecuencia**: la unidad del eje 3 es **punto contra punto**, la misma del eje 1, y no
«región contra población». No hay que rasterizar nada ni comparar dentro contra fuera: cada
marca se resuelve al **núcleo segmentado que está debajo** y se leen **sus** descriptores.
El §4 del inventario queda corregido por este documento.

### 0.b El área de la marca es en parte el PINCEL, no el núcleo

`Mitosis` y `Nucleos alto grado` comparten la mediana **exacta** de 218,82 µm². No es
coincidencia: ese valor aparece **14 veces** en `Mitosis` y **4** en `alto`, siempre con los
mismos 53 vértices; 155,25 µm² aparece **8** y **4** veces, con 65 vértices. Es un pincel de
radio fijo de QuPath. `NucleosBajoGrado`, en cambio, tiene 16 áreas distintas en 16 marcas
(trazado a mano).

**Consecuencia dura**: el área del polígono del patólogo **no se usa como medida del núcleo**,
en ninguna tabla ni figura. Todos los descriptores salen de la segmentación de HoVer-NeXt
(`pinst_pp.zip`). Si se usara el polígono, los tres grados ordenarían por tamaño de pincel y el
resultado sería un artefacto con forma de hallazgo.

### 0.c El grado está confundido con la lámina, sin un solo cruce

Las tres clases son **disjuntas por lámina**, y eso ya estaba declarado (8 + 2 + 2), pero la
consecuencia estadística no:

| Grado | Láminas | `n` marcas |
|---|---|---|
| alto | 129741, 106552, 124729, 124806, 126504, 128194, 144317, B25-158899 | 77 |
| moderado | 109609, 164001 | 14 |
| bajo | 103762, 110616 | 16 |

Ninguna lámina tiene dos grados. **Comparar grados es comparar láminas**, así que tinción,
escáner y grosor de corte entran como confusores, y el `n` efectivo del ordenamiento es
**12 láminas (8/2/2)**, no 107 marcas: las marcas dentro de una lámina no son independientes.

**Mitigación pre-registrada**: además del descriptor crudo se mide el descriptor
**normalizado contra la población de núcleos epiteliales de su propia lámina** (percentil del
núcleo marcado dentro de su lámina). Eso cancela el efecto de lámina por construcción, y además
es lo que hace la graduación de Nottingham en clínica, que compara contra el epitelio normal
del mismo corte. **El resultado primario es el normalizado.**

---

## 1. Gate ya ejecutado: 107 de 107 marcas caen sobre un núcleo segmentado

Condición de lectura, verificada antes de pre-registrar: si HoVer-NeXt no segmentó los núcleos
marcados, el eje 3 no existe.

| Grado | Marcas | Segmentadas | % |
|---|---|---|---|
| alto | 77 | 77 | **100 %** |
| moderado | 14 | 14 | **100 %** |
| bajo | 16 | 16 | **100 %** |

Método: centroide de la marca más el offset de la lámina, lectura de `pinst_pp` en ese píxel y,
si cae en fondo, la instancia más cercana en una ventana de ±32 px (el patrón de
`scripts/a0_segmentadas_o_no.py:118-135`). **El eje 3 es medible.**

Sale además el dato que gobierna la hipótesis H3.b: la clase que HoVer-NeXt le asigna al núcleo
marcado **no** es epitelial en todos los casos.

| Grado | epithelial-cell | connective | plasma-cell | lymphocyte |
|---|---|---|---|---|
| alto | 67 | 8 | 0 | 2 |
| moderado | **4** | 3 | 7 | 0 |
| bajo | 15 | 0 | 0 | 1 |

Los 7 `plasma-cell` de `moderado` son todos de la 109609. Restringir a epitelio deja
**moderado en n = 4**, así que las dos variantes se corren y se reportan juntas (matriz
completa, [[completitud-matriz-por-defensibilidad]]).

---

## 2. Eje 4, el control positivo: ¿separa epitelio de estroma?

**Unidad**: región contra punto. El patólogo dibujó áreas y HoVer-NeXt devuelve núcleos con
clase, así que no hay emparejamiento y la métrica es una **fracción dentro contra fuera**.

**Grupos** (sólo las clases que son regiones de verdad, §0.a):

- **Epitelio**: `Tumor` (98), `AreaSolida` (45), `AreaTubular` (25), `CDIS_solido` (8),
  `CDIS_papilar` (6), `DCIS` (6).
- **Estroma**: `Stroma` (12), `Tejido Adiposo` (9).

**Métrica**: fracción epitelial por región,
`f_epi = n(epithelial-cell) / (n(epithelial-cell) + n(connective-tissue-cell))`, contando las
detecciones cuyo punto cae dentro del polígono.

**H4 (primaria)**: `f_epi` es mayor en las regiones del grupo epitelio que en las del grupo
estroma. Estadístico: **AUC de rango** (Mann-Whitney U normalizado, nulo 0,5) sobre las regiones.
**Dirección esperada: AUC > 0,5**, y para que el control se dé por pasado hace falta
**AUC ≥ 0,80** con el nulo por traslación por debajo.

**H4 nula**: AUC ≈ 0,5. Si eso pasa, **el eje 3 no se lee** y el problema es el método o el
alineamiento, no el grado nuclear.

**Nulo**: **traslación rígida** de cada máscara de región sobre la lámina, nunca permutación de
etiquetas: los polígonos son contiguos ([[nulo-espacial-traslacion-rigida]]). Se aceptan las
traslaciones donde la región desplazada sigue cayendo sobre tejido.

**Control de sanidad declarado antes**: la 164001 y la B25-158899 tienen `alineada: false` en su
offset. Se reportan **por separado** además de en el agregado.

---

## 3. Eje 3: ¿ordenan los descriptores los tres grados?

**Unidad**: punto contra punto (§0.a). Cada una de las 107 marcas resuelve a una instancia de
`pinst_pp`; se leen los descriptores de esa instancia.

**Descriptores** (momentos de la máscara de la instancia, sin `skimage`): área en µm², diámetro
equivalente, eje mayor y menor, excentricidad, y razón de aspecto. El área es el descriptor
primario porque el tamaño nuclear es el componente dominante del pleomorfismo de Nottingham.

**H3.a (primaria, normalizada)**: el **percentil del área del núcleo marcado dentro de la
población de núcleos epiteliales de su propia lámina** ordena alto > moderado > bajo.
Estadístico: correlación de rangos de Spearman entre grado ordinal (bajo 1, moderado 2, alto 3)
y percentil, más el AUC de rango de cada par de grados contiguos.
**Dirección esperada: ρ > 0**, y los dos AUC de pares contiguos por encima de 0,5.

**H3.b (secundaria, cruda)**: la misma pregunta sobre el área en µm² sin normalizar.
Se espera que ordene **también**, pero es la variante contaminada por el efecto de lámina (§0.c):
si cruda ordena y normalizada no, la conclusión es efecto de lámina, no de grado.

**H3 nula**: ρ que cruza cero, o AUC de pares contiguos con el signo invertido entre pares.

**H3 regresión**: ρ < 0 consistente, es decir que los núcleos de alto grado midan **menos**.
Sería señal de que la resolución de la marca al núcleo está mal, no de biología.

**Las dos variantes de población** que exige el §1: (i) restringida a las marcas cuyo núcleo
HoVer-NeXt llamó `epithelial-cell` (n = 86, con moderado en 4) y (ii) todas las 107. La
restringida es la que tiene sentido clínico; la completa es la que tiene `n`. Se reportan juntas
y **ninguna de las dos se elige después de ver el resultado**.

**Nivel de agregación**: se reporta el resultado por marca **y** el resumen por lámina
(mediana de la lámina), porque el `n` honesto del ordenamiento es 12 láminas (§0.c). Si los dos
niveles discrepan, manda el de lámina.

---

## 4. Qué no se va a afirmar

- **Ni precisión, ni F1, ni PQ**, en ninguno de los dos ejes. El geojson son positivos parciales
  ([inventario](../hovernext_tareas/inventario_tareas.md) §4.b).
- **No se va a llamar falso positivo** a ninguna detección sin marca.
- **No se va a usar el área del polígono del patólogo** como medida del núcleo (§0.b).
- **No se va a presentar el ordenamiento como validación del grado de Nottingham.** Nottingham
  se puntúa sobre la variación de una población en el campo de peor grado, y acá se miden
  núcleos que el patólogo eligió como ejemplares.
- **No se va a afirmar que 12 láminas alcancen.** Con 8/2/2 y el grado confundido con la lámina,
  un ordenamiento es consistente con el grado y también con el efecto de lámina; lo único que
  separa las dos lecturas es la normalización intra-lámina, y aun así con `n` = 12.
- **No se va a extrapolar el control positivo al eje 3.** Que epitelio y estroma separen dice que
  la clasificación de núcleos funciona, no que los descriptores de tamaño midan grado.

## 5. Artefactos que produce

| Qué | Path |
|---|---|
| Descriptores de **todas** las instancias, por lámina | `results/b9_nucleos/<slide>_nucleos.npz` (gitignored) |
| Las 107 marcas resueltas, con grado y descriptores | `results/b9_nucleos/marcas_grado.csv` |
| Fracción epitelial por región | `results/b9_nucleos/regiones_epi_estroma.csv` |
| Resultados y lectura | [`resultados.md`](resultados.md) |
