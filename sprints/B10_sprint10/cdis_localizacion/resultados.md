# Resultados O3 — la atención de CLAM SÍ cae sobre el CDIS que dibujó el patólogo

> Pre-registro: [`prereg.md`](prereg.md). Lo de acá se lee contra él, no al revés.
>
> Medido el **9-sep-2026**, CPU, sin GPU. Driver `scripts/b10_cdis_atencion.py`,
> log `logs/b10_cdis_atencion.log`, 3 min de pared.

---

## 1. El resultado

**H_O3 se cumple en la dirección pre-registrada**, con la salvedad del §3.

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
| 164001 | val | `si` | 3 | 3796 | 6 | 0,999 | **0,926** | 0,741 |
| B25-158899 | fuera | (sin fila) | 3 | 4697 | 7 | **0,236** | (sin etiqueta) | 0,198 |

## 2. Lo que el resultado NO alcanza a sostener, y estaba declarado antes

**Una sola lámina cae en `test`, y es la peor medida de las diez.** La 126504 tiene **1 polígono
y 2 parches positivos**: su AUC 0,704 viene con IC de Hanley-McNeil **[0,297 · 1,110]**, que
contiene 0,5 y se sale del rango de un AUC. Con `n` = 2 el punto no significa nada y el `p` por
traslación da 0,31. **La evidencia limpia de este eje es una lámina, y esa lámina no mide.**

El resto del reparto es el del pre-registro §1.c: 5 en `train`, 3 en `val`, 1 fuera del split.
El agregado de arriba **no es evidencia limpia** y no se presenta como tal.

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
- **La B25-158899 no está medida** (§3), no está midiendo mal.

## 7. Artefactos

| Qué | Path |
|---|---|
| AUC por lámina, fuente y tier (29 filas) | `results/b10_cdis/auc_cdis.csv` |
| Control negativo (8 filas) | `results/b10_cdis/control_negativo.csv` |
| Lo que se saltó, con motivo | `results/b10_cdis/saltadas.csv` |
| Log | `logs/b10_cdis_atencion.log` |
| Driver | `scripts/b10_cdis_atencion.py` |
