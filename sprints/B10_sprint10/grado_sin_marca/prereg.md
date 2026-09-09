# Pre-registro O1 — ¿HoVer-NeXt solo reencuentra los núcleos que marcó el patólogo?

> Escrito el **9-sep-2026**, **antes de medir nada** de lo que este documento propone. Regla 9:
> hipótesis, métrica y dirección esperada declaradas antes del código. CPU, sin GPU.
>
> Encargo 1 de Sebastián, textual: «podríai replicar el experimento solamente con HoVer-Net y ver
> si te da lo mismo, las mismas anotaciones del patólogo al final».
>
> El experimento que se replica es el eje 3 del B9
> ([`../../B9_sprint9/ejes_nucleares/prereg.md`](../../B9_sprint9/ejes_nucleares/prereg.md) y su
> [`resultados.md`](../../B9_sprint9/ejes_nucleares/resultados.md)). **Lo que se quita es la marca**:
> allá cada marca decía qué núcleo mirar, acá el núcleo lo tiene que elegir el descriptor.
>
> El descriptor sale de [`../score_grado/estudio_score.md`](../score_grado/estudio_score.md) (O2),
> que se escribió primero a propósito.

---

## 0. Lo que cambió respecto del B9, y por qué el experimento vale la pena ahora

El B9 midió sobre **12 láminas y 107 marcas**. Desde el 27-ago hay **10 geojson nuevos** y el
8-sep se verificó que las cifras de Sebastián son de ese set. El barrido de HoVer-NeXt de las 9
nuevas numéricas corrió el **9-sep (job 5402, OK=9, 116 min)** y sus offsets el 8-sep
(**9 de 9, las 9 con `alineada: true`**), así que el material está instrumentado **antes** de
pre-registrar.

Censo de marcas de grado sobre las 22 láminas deduplicadas (contado el 9-sep):

| Grado | marcas | láminas | en el B9 | láminas medibles acá |
|---|---|---|---|---|
| bajo | 16 | 2 | 16 en 2 | 2 |
| moderado | **84** | **10** | 14 en 2 | 10 |
| alto | 99 | 10 | 77 en 8 | **9** (sale `Br0244`) |
| **total** | **199** | **22** | 107 en 12 | **187 en 21** |

**El cambio que justifica el experimento es el peldaño del medio.** En el B9 `moderado` eran
4 marcas epiteliales de **una** lámina no alineada, y el resultado primario descansaba ahí
([`resultados.md`](../../B9_sprint9/ejes_nucleares/resultados.md) §2.b). Ahora son **84 marcas en
10 láminas**. `bajo` **no** mejoró: sigue en 16 marcas de 2 láminas, y eso se declara como el
límite que queda.

**`Br0244 AP473 OT1760 1199 1 1-6 MxBr_02 HE` queda fuera** de todo brazo: es `.svs`, no tiene
`.bif` en `wsi/`, no corrió en HoVer-NeXt ni tiene offset. Se lleva 12 marcas de `alto`.

## 1. Los dos brazos, y por qué el sin restringir sale gratis

**D2 de Ernesto**: el experimento sin la marca se restringe a la máscara **`Tumor`** del patólogo.
El fundamento no es de conveniencia: el cruce del 8-sep muestra que las marcas de grado siguen la
etiqueta de **pleomorfismo invasivo de la lámina** y no el grado nuclear del CDIS
([[marcas-grado-son-pleomorfismo-de-lamina]]), y la máscara del pleomorfismo invasivo es `Tumor`,
que **ya existe**: 162 regiones en 21 láminas.

| Brazo | máscara | láminas | qué contesta |
|---|---|---|---|
| **A. sin restringir** | la lámina entera | 21 | el comparador. Es el que dice cuánto compra la máscara |
| **B. con máscara** | unión de polígonos `Tumor` | **20** | la pregunta de Sebastián en su forma útil |

**La 110962 tiene 10 marcas de `alto` y CERO región `Tumor`**, así que sale del brazo B y se
declara en la tabla, no se deja caer en silencio. El brazo B corre sobre 20 láminas y 177 marcas.

El brazo A **no cuesta nada**: la lámina entera ya está segmentada, así que la máscara se aplica
**post-hoc sobre la salida** y no se paga dos veces (P2.a.ter, [[techo-filtro-antes-de-correr]]).
Filtrar antes ahorraría cómputo una vez y destruiría la comparación para siempre.

## 2. Unidad primaria: el núcleo (D3)

Dentro de la máscara del brazo, se ordenan **descendente por el descriptor** los núcleos que
HoVer-NeXt llamó `epithelial-cell`, y se mide **cuántas de las marcas de grado de esa lámina caen
entre los N primeros**.

**No es un top-K fijo.** A K fijo gana siempre la máscara más grande ([[carga-fija-no-k-fijo]]), y
acá se comparan dos máscaras de tamaño muy distinto. El resultado se reporta como **escalera de
carga**: para cada N, el **recall** de las marcas y la **carga en mm²** que ese N le pone delante
al patólogo.

**Carga en mm², definida antes de medir**: superficie de la **unión de los parches de 256 px**
(0,465 µm/px ⇒ 119 µm de lado ⇒ **0,0142 mm²** cada uno,
[[hovernext-salida-geometria-y-clases]]) que contienen al menos uno de los N núcleos candidatos.
Es la unidad del B9 y la que hace comparables las dos escaleras. Se usa la **unión** y no
`N × 0,0142` porque dos candidatos pueden caer en el mismo parche; la suma sería una cota, no la
carga.

**Escalera declarada**: N ∈ {10, 20, 50, 100, 200, 500, 1000, 2000, 5000} y además el N que agota
la máscara, que es el chequeo de sanidad del barrido: ahí los dos brazos tienen que coincidir con
el gate (P2.a).

## 3. Los dos descriptores, los dos declarados antes

**H_O1.a (primario, continuidad con el B9)**: **percentil del área** del núcleo dentro de la
población epitelial de su propia lámina. Es el descriptor del B9 y el que permite la regresión
obligatoria del §6.

**H_O1.b (fidelidad al protocolo)**: **razón del área contra el proxy de epitelio normal**, que es
lo que exige el CAP ([`../score_grado/estudio_score.md`](../score_grado/estudio_score.md) §2 y §4).
Dos cosas que van declaradas y no se eligen después:

- **El proxy**: mediana del área de los `epithelial-cell` que caen **fuera de toda región anotada**
  de la lámina (`Tumor`, `AreaSolida`, `AreaTubular`, y las cinco clases de CDIS). **Es un proxy y
  se reporta con ese nombre**: confunde «epitelio normal» con «epitelio no marcado», y el geojson
  son positivos parciales, así que «no marcado» no significa «normal».
- **La lectura del corte**: el CAP dice «size» sin decir si es diámetro o área (O2 §4.a). Se adopta
  **diámetro**, o sea que en área los cortes son **2,25× a 4,00×** (grado I) y **>6,25×**
  (grado III). Los cortes se usan como **referencia externa dibujada sobre la distribución**, nunca
  como clasificador: el área de `epithelial-cell` está erosionada por su umbral de foreground
  ([`../../B9_sprint9/ejes_nucleares/resultados.md`](../../B9_sprint9/ejes_nucleares/resultados.md) §2.d).

Los dos descriptores se corren **en los dos brazos** y se reportan juntos, en una matriz completa
([[completitud-matriz-por-defensibilidad]]). **Ninguno se elige después de ver el resultado.**

## 4. Hipótesis y dirección esperada

Regla 9.a: métrica, subset y dirección, sin gate numérico rígido.

**H_O1 (primaria)**: a carga fija, el recall de las marcas que da el orden por tamaño está **por
encima del nulo por traslación**, y el signo es **consistente entre láminas**.

**H_O1 nula**: el recall no despega del nulo. Lectura: **el tamaño solo no basta** para elegir los
núcleos que el patólogo eligió, y la marca aporta información que el descriptor no reconstruye. Es
un resultado publicable y es la respuesta honesta al encargo de Sebastián.

**H_O1 regresión**: recall **por debajo** del nulo de forma consistente. Sería señal de que la
resolución marca → núcleo o el offset están mal, no de biología, y dispara el §6 antes que
cualquier lectura.

**Secundario, el ordenamiento**: con los núcleos elegidos por descriptor y **sin mirar las marcas**,
¿el percentil mediano de los N primeros ordena alto > moderado > bajo entre láminas? Es la versión
sin marca del ρ = +0,809 del B9. Se reporta con su nulo de permutación de grado entre láminas, y
con el **piso del `p`** que ese diseño permite, que en el B9 resultó ser el valor observado
([`resultados.md`](../../B9_sprint9/ejes_nucleares/resultados.md) §2.a ADDENDUM).

## 5. El nulo

**Traslación rígida de la máscara de marcas**, nunca permutación de etiquetas de núcleo: las marcas
son contiguas y una permutación las trataría como independientes
([[nulo-espacial-traslacion-rigida]]). Se aceptan las traslaciones donde las marcas desplazadas
siguen cayendo sobre tejido, con el tejido definido por **bloque de 256 px** y no por celda de 8 px,
que es el bug que dejó el nulo vacío en el B9
([`resultados.md`](../../B9_sprint9/ejes_nucleares/resultados.md) §1.d).

200 iteraciones ⇒ el `p` tiene **piso 1/201 = 0,00498**, y se reporta como «por debajo de 1 en 201»
y no como valor exacto.

## 6. Gate de lectura y regresión obligatoria

**Gate**: cada marca tiene que resolver a un núcleo segmentado. En las 12 el B9 dio **107 de 107**.
Se corre igual sobre las 21, con la regla `centroide` como primaria y `pixel` como control, que en
el B9 diferían en **una marca de 107** y no movían ninguna conclusión
([`resultados.md`](../../B9_sprint9/ejes_nucleares/resultados.md) §2.g). **La lámina que falle el
gate se declara y sale**: así se caza un offset malo.

**Regresión contra el B9, obligatoria antes de leer nada**: con el brazo A (máscara = lámina
entera), descriptor percentil y las **12** láminas del B9, hay que reproducir **75,1 · 92,1 · 98,9**
y **ρ = +0,809**. Si no sale, el bug es nuestro y no se lee el resultado nuevo.

**Chequeo de escala**, ya ejecutado sobre las 9 nuevas: el shape de `pinst_pp` contra las
dimensiones de level 0 del `.bif` (`DIMS_LEVEL0`, medidas con openslide desde `clam_latest`,
workaround K). Un error de nivel daría factor 2 o 4, no 200 px.

## 7. Secundario: la zona de 3 mm²

Ventana de área fija de **3 mm²** que maximiza la densidad de núcleos grandes, y si contiene o no
las marcas. Es el entregable con forma para el patólogo y **es explícitamente un `n` de una zona
por lámina**. La cifra sale de la Tabla 1 del CAP: diez campos de 0,60 mm de diámetro son
**2,83 mm²** (O2 §3), que es de donde viene el 3 mm² de Ibrahim
([[paper-3mm2-ibrahim-modern-pathology]]).

**La zona es secundaria por D3** y no se presenta como resultado principal.

## 8. Qué NO se va a afirmar

- **Ni precisión, ni F1, ni PQ**, en ningún brazo. Positivos parciales, heredado del B9 y no
  renegociable.
- **No se va a llamar falso positivo** a ningún núcleo grande sin marca. Es justamente lo que el
  patólogo no marcó, no lo que no existe.
- **No se va a afirmar que las marcas sean todos los núcleos de ese grado de la lámina.** Son
  ejemplares elegidos, y el B9 midió que sus percentiles son altos en los tres grados.
- **No se va a presentar esto como validación de Nottingham.** Nottingham puntúa la variación de una
  población en el campo de peor grado (O2 §2).
- **No se va a afirmar que el proxy de epitelio normal sea epitelio normal** (§3).
- **No se va a comparar área en µm² entre clases de HoVer-NeXt** ni contra la literatura.
- **No se va a afirmar que 21 láminas alcancen.** El grado sigue confundido con la lámina: `bajo`
  son 2 láminas y ninguna lámina tiene dos grados.
- **No se va a afirmar que las marcas midan grado nuclear de CDIS.** Miden pleomorfismo de lámina
  hasta que Sebastián diga lo contrario, y esa pregunta está abierta.

## 9. Artefactos que produce

| Qué | Path |
|---|---|
| Driver | `scripts/b10_grado_sin_marca.py` |
| Escalera de carga por brazo, lámina y descriptor | `results/b10_grado_sin_marca/escalera.csv` |
| Las 187 marcas resueltas, con brazo y rango del núcleo | `results/b10_grado_sin_marca/marcas_rango.csv` |
| Las 200 traslaciones del nulo | `results/b10_grado_sin_marca/nulo.npy` |
| Log | `logs/b10_grado_sin_marca.log` |
| Resultados y lectura | `resultados.md` |
