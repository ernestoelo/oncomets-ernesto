# Resultados — la atención de CLAM sobre las doce anotadas

> **2-sep-2026, sesión 40.** Ejecuta el pre-registro de [`prereg.md`](prereg.md), escrito el
> mismo día y **antes** del código. Todo CPU post-hoc, sin GPU, sin `sbatch`.
>
> Driver: [`scripts/b9_atencion_12_laminas.py`](../../../scripts/b9_atencion_12_laminas.py).
> Salida: `results/b9_atencion_12/{auc_por_lamina.csv, geometria_por_lamina.csv, meta.json}`.
>
> **Estado: el brazo primario está medido; el brazo de control `ckpt_limpio` y la escalera de
> área NO se corrieron todavía.** Lo que sigue vale para el primario y sólo para él.

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
(dos a cinco de los cinco; sólo la B25-158899 está limpia de todos). **Cuánto infla, no se
sabe**: se sabe la dirección y cuántos folds la producen. Medirlo es el brazo `ckpt_limpio`,
que **queda pendiente**.

Las otras dos propiedades de la fuente, que van en toda tabla: lee la rama de la clase
**predicha** y no la verdadera, y es la familia **`_pth_balance`**, que no es la
`_combined_5fold` de los números del B8. **Los dos brazos no se promedian entre sí.**

Y lo que un AUC alto **no** implica: que un top-k capture las mitosis. El AUC resume todos los
umbrales y un top-k es uno solo, de los extremos ([[topk-percentil-no-auc]]). Eso es lo que
mide la escalera de área, y es lo que falta.

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

## 4. Qué falta de este eje

| # | qué | por qué importa |
|---|---|---|
| P1 | **El brazo `ckpt_limpio`** (`--fuente ckpt_limpio`) | Es el control de honestidad: sin él, el 0,809 no tiene con qué contrastarse. El pre-registro fija que el contaminado tiene que dar **más alto** que el limpio, y si no ordena así es bug de la tabla de membresía |
| P1.bis | **El brazo contaminado de la MISMA familia** (`--folds todos`, que el driver todavía no tiene) | El ordenamiento pre-registrado es «contaminado > limpio». Contra `json_out` esa comparación está confundida por familia (`_pth_balance` vs `_combined_5fold`), cabeza (predicha vs verdadera) y definición de atención. Con los mismos checkpoints y la misma cabeza, el único delta pasa a ser qué folds entran |
| P2 | **La escalera de área** (`scripts/b9_escalera_area.py`, §6 del prereg) | Es la pregunta de la reunión. Todavía no existe el script |
| P3 | **`@csv-audit`** sobre `auc_por_lamina.csv` y `escalera.csv` | Son CSV nuevos del pipeline |

El driver ya soporta `--fuente ckpt_limpio` y `--cabeza {verdadera, predicha}`; falta correrlo
y cruzarlo. **No hay ningún resultado del brazo limpio en este documento.** Tampoco de la escalera:
lo único medido de ella es la geometría de §2.b.
