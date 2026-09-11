# Resultados O3 — la atención de CLAM SÍ cae sobre el CDIS que dibujó el patólogo

> Pre-registro: [`prereg.md`](prereg.md). Lo de acá se lee contra él, no al revés.
>
> Medido el **9-sep-2026**, CPU, sin GPU. Driver `scripts/b10_cdis_atencion.py`,
> log `logs/b10_cdis_atencion.log`, 3 min de pared.

---

## 1. El resultado

**H_O3 se cumple en la rama verdadera** (9 de 9 por encima de 0,5), con dos salvedades: la
evidencia fuera de `train` es chica (§2), y la única lámina que el fold nunca vio va al revés,
también confinada a su región (§3.b).

| fuente | `n` | AUC mediana | rango | AUC > 0,5 | `p` < 0,05 |
|---|---|---|---|---|---|
| `json_out` (ensemble 5 folds, rama **predicha**) | 10 | **0,862** | 0,236 - 0,999 | 9/10 | 6/10 |
| checkpoint 1 fold, rama **verdadera** | 9 | **0,755** | 0,704 - 0,929 | **9/9** | 5/9 |
| checkpoint 1 fold, rama **predicha** | 10 | 0,743 | 0,198 - 0,929 | 9/10 | 4/10 |

La fila que manda es la del medio: es la rama verdadera, la que el pre-registro declaró como
no opcional. **Las 9 láminas medibles dan AUC por encima de 0,5, sin una sola excepción**, y su
mínimo es 0,704.

### 1.a Por lámina, con el tier declarado

| lámina | tier | etiqueta | pol | parches | CDIS | `json_out` | ckpt verdadera | ckpt predicha |
|---|---|---|---|---|---|---|---|---|
| 110616 | train | `no_identificado` | 6 | 2933 | 44 | 0,936 | **0,775** | 0,775 |
| 124729 | train | `si` | 5 | 4334 | 32 | 0,948 | **0,929** | 0,929 |
| 124806 | val | `si` | 2 | 2705 | 9 | 0,922 | **0,925** | 0,925 |
| **126504** | **test** | `si` | 1 | 4410 | **2** | 0,703 | **0,704** | 0,704 |
| 128250 | train | `si` | 4 | 4489 | 33 | 0,788 | **0,745** | 0,745 |
| 131461-1 | train | `si` | 4 | 7839 | 28 | 0,852 | **0,715** | 0,715 |
| 132844 | val | `si` | 1 | 2292 | 3 | 0,872 | **0,755** | 0,919 |
| 142541-1 | train | `si` | 1 | 5875 | 4 | 0,840 | **0,722** | 0,722 |
| 164001 † | val | `si` | 3 | 3796 | 6 | 0,999 | **0,926** | 0,741 |
| B25-158899 † | fuera | (sin fila) | 3 | 4697 | 7 | **0,236** | (sin etiqueta) | 0,198 |

† `alineada: false` en su offset desde el B8. Son las dos únicas de las diez (§3.b), y el
pre-registro no lo declaró. Sin la 164001, la rama verdadera da **8 de 8** por encima de 0,5.

## 2. Lo que el resultado NO alcanza a sostener, y estaba declarado antes

**Una sola lámina cae en `test`, y es la peor medida de las diez.** La 126504 tiene **1 polígono
y 2 parches positivos**: su AUC 0,704 viene con IC de Hanley-McNeil **[0,297 · 1,111]**, que
contiene 0,5 y se sale del rango de un AUC. Con `n` = 2 el punto no significa nada y el `p` por
traslación da 0,31. **La evidencia limpia de este eje es una lámina, y esa lámina no mide.**

El resto del reparto es el del pre-registro §1.c: 5 en `train`, 3 en `val`, 1 fuera del split.
El agregado de arriba **no es evidencia limpia** y no se presenta como tal.

**Con la B25-158899 medida (§3.b), la lectura por tier queda así**, con el orden de limpieza
ausente > test > val que fijó el B9 ([[atencion-doce-laminas-folds-limpios]]):

| tier | qué tan limpia | láminas | AUC > 0,5 | `p` < 0,05 |
|---|---|---|---|---|
| `train` | nada: el fold se entrenó con ellas | 5 | 5 de 5 | 3 |
| `val` | débil: eligió el checkpoint | 3 | 3 de 3 | 2 (una es la 164001 †) |
| `test` | fuerte | 1 | 1 de 1 (0,704, IC contiene 0,5) | 0 |
| ausente | la más fuerte | 1 (rama `si`) | **0 de 1** (0,201 confinada) † | 0 |

**Las dos láminas que el fold no usó ni para entrenar ni para elegir el checkpoint no muestran
localización**: una no mide y la otra va al revés. Fuera de `train`, lo que se separa del nulo es
`val`, el tier más débil, y la mitad de eso viene de la 164001, que no está alineada. **No se afirma
que esta atención localice el CDIS en láminas nuevas**: el material no lo sostiene ni en un sentido
ni en el otro.

**La segunda incertidumbre es la que manda** ([[auc-atencion-dos-incertidumbres]]): la dispersión
entre fuentes es chica (0,74 a 0,86 de mediana), y el IC de Hanley-McNeil es enorme donde el
polígono es uno solo.

## 3. La B25-158899 va al revés, y hay una causa candidata declarada antes de mirarla

Es la única lámina con AUC **por debajo** de 0,5 (0,236 y 0,198, con `p` de 0,92 y 0,995, o sea
que el nulo la supera casi siempre). Dos cosas la separan de las demás:

1. **Tiene dos regiones de escaneo**, y el patólogo anotó la de **arriba** (`region[0]`), que es
   el caso que el ADDENDUM 17 de [[anotaciones-patologo-qupath]] documentó: sus 38 de 38
   anotaciones caen entre y=7537 y y=17495. **Este driver midió sobre el universo «lámina
   entera», que incluye la región no anotada**, y eso deprime el AUC por construcción. El B9 tenía
   `universos_de()` exactamente para esto y acá **no se aplicó**.
2. **No tiene fila en el CSV de labels**, así que su brazo de rama verdadera no existe.

**No se interpreta como que la atención evite el CDIS ahí.** Queda como pendiente re-medirla
confinada al intervalo de su región anotada, que es una corrida de segundos, y hasta entonces la
fila se lee como no medida. Sin ella, la rama predicha da **9 de 9 por encima de 0,5**.

### 3.a Lo que se declara ANTES de re-medirla (10-sep)

Escrito y commiteado antes de correr. El número de lámina entera ya se vio (0,236), así que lo
único que protege la re-medición de ser una búsqueda a posteriori es que **nada de lo que sigue
se elige ahora**:

- **Universo**: `y ∈ [0, 25600)`, el intervalo que el B9 fijó para esta lámina en
  `scripts/cruce_94_marcas.py:71` (`REGION_ANOTADA`). Se aplica con `universos_de()` y `medir()`
  de `scripts/b9_atencion_12_laminas.py`, importados **sin tocarlos**. No se prueba ningún otro
  intervalo.
- **Nulo**: el mismo, traslación rígida con 200 iteraciones, restringida a la región.
- **Rama**: la verdadera no existe, porque la lámina no tiene fila en el CSV. Los polígonos de
  `DCIS` implican la clase `si`, que es además la que el fold predice, así que la fila «predicha»
  **es** la rama `si`. Se reporta con ese nombre y **no** se la llama «verdadera».
- **Lectura, fijada antes**:
  - AUC confinado **> 0,5**: el 0,236 era del universo, no de la atención. La B25-158899 se suma a
    las que localizan, **fuera del split** y por lo tanto sin valor de evidencia limpia.
  - AUC confinado **≤ 0,5**: la hipótesis del universo queda refutada y la B25-158899 pasa a ser
    la única lámina donde la atención no cae sobre el CDIS. Se reporta así, **sin buscar una
    tercera causa**.
  - El signo y el `p` se leen por separado: un AUC > 0,5 con `p` alto va en la dirección y no se
    separa del nulo, con 7 parches positivos.
  - **Ninguna de las dos lecturas mueve el resultado principal** (rama verdadera, 9 de 9), porque
    la B25-158899 no está en esa fila.

**Corrección, escrita después de medir (10-sep).** El primer punto de la lectura dice «fuera del
split y por lo tanto sin valor de evidencia limpia». **Es al revés**: una lámina que no está en el
split es **ausente**, el tier más limpio del orden ausente > test > val del B9. El error no cambia
qué lectura se aplica, que dependía sólo del signo, pero sí el peso de la B25-158899 en la
conclusión (§2).

### 3.b El resultado: confinar no cambia nada

Unidad: parche. Rama `si` en las dos fuentes (§3.a). Lámina entera, de `auc_cdis.csv`; región, de
`auc_cdis_region.csv`.

| fuente | universo | parches | CDIS | AUC | IC 95 % (Hanley-McNeil) | `p` traslación |
|---|---|---|---|---|---|---|
| `json_out` | lámina entera | 4697 | 7 | 0,236 | 0,099 · 0,374 | 0,920 |
| `json_out` | **región anotada** | **2404** | 7 | **0,239** | 0,100 · 0,379 | 0,915 |
| checkpoint 1 fold | lámina entera | 4697 | 7 | 0,198 | 0,078 · 0,318 | 0,995 |
| checkpoint 1 fold | **región anotada** | **2404** | 7 | **0,201** | 0,079 · 0,323 | 0,995 |

La región anotada tiene la mitad de los parches y los mismos 7 positivos, y el AUC se mueve en la
tercera cifra. **Por la regla del §3.a, la hipótesis del universo queda refutada**: la B25-158899 es
la única de las diez donde la atención no cae sobre el CDIS dibujado. Pone esos parches por debajo
del 76 al 80 % de los de su propia región, y el nulo la supera en más del 90 % de las traslaciones.
El fold acierta la clase con esa misma rama (predice `si`): localización y decisión se disocian, en
el sentido opuesto al de la necrosis del B8 ([[rama-de-atencion-decide-el-resultado]]).

**Lo que la pre-declaración no tenía y había que decir.** El offset de esta lámina tiene
**`alineada: false`** desde el B8. Se vio **después de medir**, al verificar el tier, y **no se usa
para rescatar el número**. Qué significa el flag, según el A3 del B8
(`sprints/B8_sprint8/encargos_sebastian/a3_offsets_11_laminas.md` §3): menos del 80 % de **todas**
las anotaciones cae sobre tejido (acá 27 de 38, 71 %). Lo que se cae son polígonos grandes cuyo
centroide queda sobre fondo, y las 6 marcas de `Mitosis` caen las 6. O sea que el flag **no prueba**
que el offset esté mal, y **tampoco** lo verifica para los polígonos de CDIS. La otra lámina con el
flag es la **164001**, que da 0,926, así que el flag solo no ordena el resultado. El B9 lo había
declarado como control de sanidad para estas mismas dos
(`../../B9_sprint9/ejes_nucleares/prereg.md` §2). El pre-registro de O3 no lo hizo, y ése es un
hueco del pre-registro, no del dato.

**Estado de la fila**: medida y al revés. Lo que no se afirma es el mecanismo: con el offset sin
verificar, «la atención no cae sobre el polígono» y «el polígono no está donde se lo dibujó» no se
distinguen.

## 4. La rama que se lee decide el resultado, otra vez

Las dos ramas coinciden en 7 de las 10 láminas, porque el fold predice la clase verdadera. En las
**tres** en que no coinciden, el número cambia y en una cambia el signo de la conclusión:

| lámina | etiqueta | predicha | AUC verdadera | AUC predicha |
|---|---|---|---|---|
| 132844 | `si` | `no` | 0,755 (`p` 0,289) | **0,919** (`p` 0,055) |
| 164001 | `si` | `no_identificado` | **0,926** (`p` 0,0050) | 0,741 (`p` 0,249) |
| B25-158899 | (sin fila) | `si` | (no medible) | 0,198 |

En la 164001 leer la rama equivocada **borra el resultado** (de `p` en el piso a `p` = 0,25), y en
la 132844 lo **fabrica**. Es la confirmación directa de [[rama-de-atencion-decide-el-resultado]] y
la razón por la que el pre-registro puso este brazo como no opcional. **Corolario para el
`json_out`**: su columna es de rama predicha, así que sus 0,862 de mediana están medidos sobre la
rama que el ensemble eligió, no sobre la verdadera.

## 5. El control negativo: 8 láminas sin polígono, y una que el modelo llama `si`

No tienen polígonos, así que **no hay AUC** y no se promedian con las de arriba (prereg §2). Lo
que se mide es qué predice el fold y cuánta atención concentra (`n_eff` = exp(entropía) del vector
de atención de la rama verdadera):

| lámina | tier | etiqueta | parches | predicha | `n_eff` | % de la lámina |
|---|---|---|---|---|---|---|
| 103762 | train | `no` | 5203 | `no` | 53,8 | 1,0 % |
| 106552 | train | `no` | 4659 | `no` | 298,8 | 6,4 % |
| 109609 | train | `no` | 2957 | `no` | 104,0 | 3,5 % |
| 110962 | train | `no` | 5043 | `no` | 635,8 | 12,6 % |
| 128194 | train | `no` | 4570 | `no` | 748,9 | 16,4 % |
| **132208** | train | `no` | 7851 | **`si`** | 158,8 | 2,0 % |
| 141426-1 | train | `no` | 4627 | `no` | 2140,4 | 46,3 % |
| 144317 | test | `no` | 4769 | `no` | 1011,5 | 21,2 % |

**7 de 8 las predice `no`**, incluida la única en `test`. La excepción es la **132208**, que el
modelo llama `si` estando etiquetada `no`. **No se interpreta**: es una lámina de `train`, el
patólogo no dibujó CDIS ahí, y «el reporte CAP no lo menciona» no es lo mismo que «no está». Se
deja anotado.

La concentración va de **1,0 % a 46,3 %** de la lámina y no se lee como métrica de calidad: es
descriptiva y su rango dice que el modelo no tiene un comportamiento único cuando no hay CDIS.

## 6. Qué no se afirma

- **Ni precisión, ni F1, ni PQ.** Positivos parciales, en los dos grupos.
- **Ningún parche sin polígono se llama negativo.** Las tres láminas con etiqueta `si` y cero
  polígonos (129741, 133677, 154144) lo prueban, y por eso salieron de los dos grupos.
- **El agregado no es evidencia limpia**: 5 de 10 están en `train` del único fold que existe, y la
  única en `test` tiene 2 parches positivos.
- **No se afirma que CLAM «entienda» CDIS.** Mide que la atención se concentra donde el patólogo
  dibujó, sobre láminas que el modelo mayormente ya vio.
- **No se compara contra los números del B8**, que son de la familia `_combined_5fold`.
- **El `no_identificado` de la 110616 no se lee como ausencia**, y su AUC 0,775 entra al agregado
  con esa etiqueta declarada.
- **No se afirma que la atención evite el CDIS en la B25-158899.** Está medida y va al revés
  (§3.b), pero con `alineada: false` eso no se distingue de un polígono corrido.
- **No se afirma que la atención localice el CDIS en láminas nuevas** (§2): las dos que el fold
  no vio no lo muestran.

## 7. Artefactos

| Qué | Path |
|---|---|
| AUC por lámina, fuente y tier (29 filas) | `results/b10_cdis/auc_cdis.csv` |
| Control negativo (8 filas) | `results/b10_cdis/control_negativo.csv` |
| Lo que se saltó, con motivo | `results/b10_cdis/saltadas.csv` |
| Re-medición confinada de la B25-158899 (2 filas, universo `region`, 10-sep) | `results/b10_cdis/auc_cdis_region.csv` |
| Log de la corrida con la re-medición (el de arriba queda intacto) | `logs/b10_cdis_atencion_region.log` |
| Log | `logs/b10_cdis_atencion.log` |
| Driver | `scripts/b10_cdis_atencion.py` |
