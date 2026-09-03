# Resultados — la atención de CLAM sobre las doce anotadas

> **2-sep-2026, sesión 40.** Ejecuta el pre-registro de [`prereg.md`](prereg.md), escrito el
> mismo día y **antes** del código. Todo CPU post-hoc, sin GPU, sin `sbatch`.
>
> Driver: [`scripts/b9_atencion_12_laminas.py`](../../../scripts/b9_atencion_12_laminas.py).
> Salida: `results/b9_atencion_12/{auc_por_lamina.csv, geometria_por_lamina.csv, meta.json}`.
>
> **Estado al 2-sep (sesión 42): el eje está COMPLETO.** El brazo primario (§1), los dos
> brazos de control (§4) y la escalera de área (§5) están medidos. Falta sólo llevarlo al deck.

---

## 0. El gate de regresión pasó, exacto

Antes de leer un solo número nuevo, el driver reprodujo los cuatro valores del B8 sobre la
129741, cabeza verdadera, familia `results_modelo_combined_5fold`
([`prereg.md`](prereg.md) §5.a):

| ckpt | universo | esperado | obtenido | \|Δ\| |
|---|---|---:|---:|---:|
| `seba_5fold_f0` | lámina | 0,925697 | 0,925697 | 8,1 e-08 |
| `seba_5fold_f0` | región | 0,936444 | 0,936444 | 3,8 e-07 |
| `seba_5fold_f2` | lámina | 0,916527 | 0,916527 | 6,6 e-08 |
| `seba_5fold_f2` | región | 0,927269 | 0,927269 | 4,4 e-08 |

Los cuatro bajo 1e-6 ⇒ **las primitivas importadas hacen lo mismo que en el B8** y una
diferencia aguas abajo es resultado, no bug. Se corre con `--gate`.

**Chequeo de geometría, de yapa**: la moda del paso por fila da **256 px en las doce** y el
total es **49.832 parches = 706,1 mm²**, que es exactamente lo que
[`insumos_json_out.md`](insumos_json_out.md) §4 había derivado por otro camino.

---

## 1. El resultado primario

**La atención de CLAM cae sobre los parches donde el patólogo marcó mitosis.**

| agregado | AUC mitosis | AUC gate |
|---|---:|---:|
| **primario: nueve láminas con `score_1/2/3`, media sin ponderar** | **0,809 ± 0,127** | **0,745 ± 0,183** |
| las doce, media sin ponderar (secundario) | 0,810 | 0,772 |

**Las nueve del primario dan las nueve por encima de 0,5** en la cabeza de mitosis, y las
cuatro de mayor `n` (28, 28, 21 y 7 parches marcados) tienen `p` por traslación rígida bajo
0,05. Es exactamente la lectura que el pre-registro fijó como **primaria** antes de correr:
agregado sobre 0,5, mayoría de láminas sobre 0,5, `p` bajo donde hay `n`.

Las medias de las doce reproducen **al tercer decimal** el go/no-go que la sesión 39 había
calculado en memoria (0,810 y 0,772) ⇒ el driver lee la misma fuente de la misma manera.

### 1.a Por lámina, universo lámina

| lámina | N parches | marcados | tier | label | AUC mitosis | IC 95 % | p | AUC gate | primario |
|---|---:|---:|---|---|---:|---|---:|---:|:-:|
| 129741 | 4799 | 28 | val | score_3 | **0,942** | 0,882–1,000 | 0,002 | 0,830 | sí |
| 126504 | 4410 | 28 | ausente | score_3 | **0,778** | 0,676–0,880 | 0,001 | 0,795 | sí |
| 128194 | 4570 | 21 | test | score_3 | **0,947** | 0,880–1,000 | 0,002 | 0,881 | sí |
| 124729 | 4334 | 7 | ausente | score_2 | **0,924** | 0,787–1,000 | 0,000 | 0,805 | sí |
| 124806 | 2705 | 7 | ausente | score_1 | **0,815** | 0,623–1,000 | 0,100 | 0,701 | sí |
| B25-158899 | 4697 | 6 | ausente | sin label | 0,612 | 0,372–0,853 | 0,448 | 0,676 | no |
| 144317 | 4769 | 4 | test/val | score_2 | **0,877** | 0,656–1,000 | 0,076 | 0,800 | sí |
| 164001 | 3796 | 4 | val | score_1 | **0,669** | 0,377–0,961 | 0,279 | 0,858 | sí |
| 106552 | 4659 | 2 | ausente | no_identificado | 0,979 | 0,838–1,000 | 0,013 | 0,888 | no |
| 103762 | 5203 | 2 | ausente | score_1 | **0,740** | 0,343–1,000 | 0,150 | 0,757 | sí |
| 109609 | 2957 | 2 | ausente | score_2 | **0,586** | 0,171–1,000 | 0,397 | **0,278** | sí |
| 110616 | 2933 | 2 | ausente | no_identificado | 0,852 | 0,518–1,000 | 0,132 | 0,990 | no |

**Unidad: PARCHE.** No marca, no detección, no lámina. Los `marcados` suman **113** en las
doce y **103** en las nueve del primario.

**Los IC recortados a 1,000** son los de Hanley-McNeil, que es una aproximación normal y con
`n` chico se pasa del 1: se recortan al dibujarlos, no al calcularlos. El CSV trae el valor
crudo. **Cuatro láminas tienen 2 parches marcados y no se leen solas**
(103762, 106552, 109609, 110616): su IC va de 0,17 a 1,00.

### 1.b La región, en las dos láminas que la tienen

| lámina | N parches en la región | marcados | AUC mitosis | p | AUC gate |
|---|---:|---:|---:|---:|---:|
| 129741 | 2496 | 28 | **0,948** | 0,001 | 0,834 |
| B25-158899 | 2404 | 6 | 0,631 | 0,411 | 0,687 |

Confinar a la región anotada **sube** el número en las dos, o sea que el efecto no es «una
región de escaneo recibe más atención que la otra». El confinamiento se hizo con el
**intervalo por lámina** (`REGION_ANOTADA`): la 129741 en `[49920, 80640)` y la B25-158899 en
`[0, 25600)`, y el driver **verifica** que las marcas caigan dentro. Con el corte escalar
`y >= 49920` la B25-158899 quedaría al revés.

---

## 2. Lo que NO se puede concluir de esto

**La fuente está contaminada por construcción y el número es optimista.** El `json_out` es un
ensemble de los cinco folds, así que incluye los folds donde cada lámina estuvo en `train`
(dos a cinco de los cinco; sólo la B25-158899 está limpia de todos). **Cuánto infla, no se sabe**: se sabe la dirección y cuántos folds la producen. Medir la
contaminación *dentro de una misma familia* es el brazo `ckpt_limpio`, y está en **§4**.

Las otras dos propiedades de la fuente, que van en toda tabla: lee la rama de la clase
**predicha** y no la verdadera, y es la familia **`_pth_balance`**, que no es la
`_combined_5fold` de los números del B8. **Los dos brazos no se promedian entre sí.**

Y lo que un AUC alto **no** implica: que un top-k capture las mitosis. El AUC resume todos los
umbrales y un top-k es uno solo, de los extremos ([[topk-percentil-no-auc]]). Eso es lo que mide la escalera de
área, en **§5**.

### 2.a El gate invasivo tiene una lámina por debajo del azar

La **109609** da **0,278** en la cabeza del gate, contra 0,586 en la de mitosis. Es la única
de las doce por debajo de 0,5 en cualquiera de las dos cabezas, y ya venía señalada: aporta
**cero marcas epiteliales** al eje del grado y es la de **menor fracción epitelial** de las
doce (5,4 %). Tiene **2 parches marcados**, así que su IC cruza el azar de sobra
(−0,01 a 0,57) y **no se lee sola**. Queda anotado, no interpretado.

---

## 3. La geometría punto→parche, medida el 2-sep

Antes de escribir la escalera de área se midió la contención exacta de cada punto en la
teselación de CLAM sobre las doce. El resultado corrige un número del pre-registro y por eso
va con ADDENDUM ([`prereg.md`](prereg.md) §6.a):

| unidad | dentro de la teselación | total | fuera |
|---|---:|---:|---:|
| marcas de `Mitosis` | **94** | 94 | **0** |
| marcas **acreditadas** | **26** | 26 | **0** |
| detecciones de HoVer-NeXt | **707** | 732 | **25** |

Las 25 de afuera están sobre tejido que el **segmentador de CLAM descartó**: ningún brazo
enmascarado por parches puede alcanzarlas. Entonces la escalera lleva **dos controles** y no
uno: `sin_filtro` (la lámina completa, **732 · 26**) y `teselado` (todos los parches,
**707 · 26**), y el chequeo del peldaño «lámina entera» se lee contra el segundo.

**Dos trampas que la misma medición dejó a la vista:**

- La grilla del h5 **no es un retículo regular** (de 7 a 29 valores distintos de `x mod 256`
  por lámina), así que la contención va **por intervalo y exacta**. Un hash con `//256` da 166
  detecciones donde la exacta da 168 en la 129741.
- **Una marca tiene dos mapeos a parche.** Por centroide, las 94 caen en 94 parches; por solape
  del polígono, `parches_anotados_*.csv` cuenta **113**. Los 113 son los que usa la tabla §1.a
  de este documento (`n_marcados`); los 94, los que va a usar la escalera
  ([[dos-numeros-iguales-denominador-distinto]]).

---

## 4. Los dos brazos de control, y el ordenamiento se sostiene

Corridos el 2-sep con `--fuente ckpt_limpio --folds {limpios, todos}`. El **único delta entre
los dos es qué folds entran**: misma familia `results_modelo_combined_5fold`, misma cabeza
verdadera, misma definición de atención. Contra el `json_out` esa comparación estaba confundida
por familia, cabeza y definición de atención a la vez, y por eso el brazo `todos` existe.

El gate de regresión volvió a dar los cuatro valores del B8 a 1e-6 con el driver ya parcheado,
así que la diferencia entre brazos es resultado y no deriva del código.

| brazo | familia | cabeza | folds | AUC, nueve del primario |
|---|---|---|---|---:|
| `json_out` (primario) | `_pth_balance` | predicha, ensemble | los cinco | **0,809 ± 0,127** |
| `ckpt --folds todos` | `_combined_5fold` | verdadera | los cinco | **0,792 ± 0,122** |
| `ckpt --folds limpios` | `_combined_5fold` | verdadera | los limpios de cada lámina | **0,770 ± 0,128** |

**Ordena como el pre-registro fijó antes de correr**: el contaminado da más alto que el limpio.
Si no ordenara así sería bug de la tabla de membresía y no resultado (§5 del prereg).

**Los dos brazos cubren ONCE láminas, no doce**: la B25-158899 no tiene fila en el CSV de la
tarea, así que su cabeza verdadera no existe y se salta en los dos. Con eso los dos archivos
suman **107** parches marcados, no los 113 de las doce ni los 103 de las nueve del primario.
**Tres denominadores conviven en este eje** y cada tabla dice cuál usa
([[dos-numeros-iguales-denominador-distinto]]).

Y el resultado primario **sobrevive al control**: en el brazo limpio las **nueve del primario
siguen por encima de 0,5**, y las cuatro de mayor `n` (28, 28, 21 y 7 parches marcados) tienen
`p` por traslación rígida de 0,002, 0,001, 0,002 y 0,007. La lectura de §1 no dependía de la
contaminación.

### 4.a El contraste sólo existe en cuatro de las once, y ahí es mayor

**Siete de las once láminas están ausentes de los cinco folds**, así que para ellas `limpios` y
`todos` promedian exactamente los mismos cinco checkpoints y su Δ es **cero por construcción**,
no un efecto medido. El agregado sobre las nueve del primario (Δ = +0,022 ± 0,041) está
**diluido por cinco ceros estructurales**.

Restringido a las láminas donde la comparación existe de verdad:

| lámina | folds limpios | limpios | todos | Δ |
|---|---|---:|---:|---:|
| 129741 | 0+2 | 0,938 | 0,952 | **+0,014** |
| 128194 | 2 | 0,909 | 0,926 | **+0,017** |
| 144317 | 0+4 | 0,691 | 0,737 | **+0,046** |
| 164001 | 3 | 0,660 | 0,784 | **+0,124** |

**Δ = +0,050 ± 0,051, positivo en las cuatro.** Las cuatro son del primario. La dirección es la
pre-registrada y la magnitud es el doble de lo que sugiere el agregado.

**Lo que sigue sin saberse** es cuánto infla el `json_out`, que es otra familia y otra cabeza:
lo medido acá es cuánto infla la contaminación **dentro de una misma familia**, y no se
transfiere ([[dos-numeros-iguales-denominador-distinto]]).

---

## 5. La escalera de área: el recorte compra superficie, no marcas

Corrida el 2-sep con `scripts/b9_escalera_area.py`. Mide **cuánta área compra cada marca
retenida**, nunca si filtrar encuentra más mitosis: HoVer-NeXt ya corrió sobre la lámina entera
en las doce, así que todo filtro es un subconjunto y el conteo **sólo puede bajar** (P2.a.ter).

**Unidad de marca: CENTROIDE (94, de ellas 26 acreditadas).** El eje de atención de §1 cuenta
por solape (113 parches). Son dos mapeos de la misma marca, no dos números
([[escalera-punto-a-parche-geometria]]).

| presupuesto | área total | % del área | `clam_mitosis` | `clam_gate` | `clam_combinado` | azar |
|---|---:|---:|---:|---:|---:|---:|
| lámina entera (`teselado`) | 706,1 mm² | 100 % | **26 de 26** | 26 | 26 | 26,0 |
| 30 mm² por lámina | 360,2 mm² | 51 % | **26 de 26** | 26 | 26 | 12,6 |
| 10 mm² por lámina | 120,1 mm² | 17 % | **23 de 26** | 15 | 22 | 4,2 |
| **3 mm² por lámina** | **36,0 mm²** | **5,1 %** | **14 de 26** | 5 | 11 | 1,3 |
| 1 mm² por lámina | 12,1 mm² | 1,7 % | **11 de 26** | 0 | 6 | 0,4 |

**El control `sin_filtro`** (la lámina completa, tal como corrió el detector) da **732
detecciones · 26 acreditadas**; el `teselado` da **707 · 26**. La diferencia de 25 detecciones
es el precio de teselar: caen sobre tejido que el segmentador de CLAM descartó, así que ningún
brazo enmascarado por parches puede alcanzarlas (ADDENDUM §6.a del prereg).

**Lo que la escalera afirma**, y nada más: bajar de 706 a 36 mm² (un factor 20) retiene **14 de
las 26 acreditadas**, contra 1,3 que retendría el azar con la misma carga de parches. Y bajar de
706 a 120 retiene 23, o sea que **el primer factor 6 de recorte cuesta tres marcas**.

**La cabeza decide.** El brazo del gate invasivo se desploma (5 acreditadas a 3 mm², 0 a 1 mm²)
mientras el de tasa mitótica retiene 14 y 11. Localizar mitosis lo hace la cabeza de mitosis, no
una atención genérica sobre tejido tumoral ([[rama-de-atencion-decide-el-resultado]]). El
`clam_combinado` queda en el medio y **es exploratorio**, declarado como tal.

Los **trece chequeos** del prereg §6 y su ADDENDUM pasan: el peldaño «lámina entera» da 732 · 26
en `sin_filtro` y 707 · 26 en `teselado`, los tres brazos con filtro coinciden con `teselado`, la
monotonía se sostiene en las 36 series, y los conteos duros no se mueven (94 marcas · 26
acreditadas · 732 detecciones · 12 láminas · 49.832 parches = 706,1 mm²).

---

## 6. Lo que el eje se debía, y su estado

| # | qué | por qué importa |
|---|---|---|
| P1 | **El brazo `ckpt_limpio`** (`--fuente ckpt_limpio`) | Es el control de honestidad: sin él, el 0,809 no tiene con qué contrastarse. El pre-registro fija que el contaminado tiene que dar **más alto** que el limpio, y si no ordena así es bug de la tabla de membresía |
| P1.bis | **El brazo contaminado de la MISMA familia** (`--folds todos`, que el driver todavía no tiene) | El ordenamiento pre-registrado es «contaminado > limpio». Contra `json_out` esa comparación está confundida por familia (`_pth_balance` vs `_combined_5fold`), cabeza (predicha vs verdadera) y definición de atención. Con los mismos checkpoints y la misma cabeza, el único delta pasa a ser qué folds entran |
| P2 | **La escalera de área** (`scripts/b9_escalera_area.py`, §6 del prereg) | Es la pregunta de la reunión. Todavía no existe el script |
| P3 | **`@csv-audit`** sobre `auc_por_lamina.csv` y `escalera.csv` | Son CSV nuevos del pipeline |

> **Cerrado el 2-sep (sesión 42).** P1, P1.bis y P2 están medidos y viven en §4 y §5. P3 se
> resolvió con [`csv_audit.md`](csv_audit.md). Lo que queda del eje no es medición: es llevarlo
> a las dos láminas del deck del 07/09 (la de atención y la de la escalera).

Lo que el eje **sigue sin poder afirmar**, y va en el pie de las dos láminas:

- Cuánto infla el `json_out` respecto de un modelo limpio de su misma familia. Lo medido en §4.a
  es la contaminación **dentro de `_combined_5fold`**, y el `json_out` es otra familia y otra
  cabeza.
- Que las doce láminas representen la cohorte. Son las que el patólogo anotó, y Sebastián habló
  de 30.
- La **109609 da 0,278** en la cabeza del gate, la única de las doce bajo el azar en cualquier
  cabeza. Tiene 2 parches marcados y su IC cruza el azar de sobra ⇒ **queda anotada, no
  interpretada** (§2.a).
