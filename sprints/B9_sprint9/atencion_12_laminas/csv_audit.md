# Auditoría de los CSV nuevos del eje (`@csv-audit`)

> **2-sep-2026, sesión 42.** Cierra el pendiente P3 de [`resultados.md`](resultados.md) §6.
> Formato fijo de CLAUDE.md § «Pedagogía de CSVs». Cuatro CSV nuevos: dos del eje de atención
> y dos de la escalera de área, más su agregado.
>
> Los cuatro viven en `results/`, que **se versiona** (verdad de campo chica), y **ninguno pisa
> a otro**: el sufijo lleva la variante y no sólo la fuente
> ([[agregador-nombre-fijo-pisa-referencia]]).

---

## 1. `auc_por_lamina_ckpt_{limpios,todos}.csv`

```
CSV: auc_por_lamina_ckpt_limpios.csv  ·  auc_por_lamina_ckpt_todos.csv
Path: results/b9_atencion_12/
Schema (21 columnas):
  - slide: str, "129741" / "B25-158899", la lámina anotada
  - universo: str, {lamina, region}. `region` sólo en las dos multi-región
  - n_parches: int, parches del universo (4799 en la 129741, 2496 en su región)
  - n_marcados: int, parches con al menos una marca de `Mitosis`, POR SOLAPE (113 en las doce)
  - auc: float, Mann-Whitney U normalizado sobre rangos medios (`rank_auc`)
  - ee, ic95_lo, ic95_hi: float, Hanley-McNeil. `ic95_hi` puede pasar de 1: es aproximación
    normal y se recorta al DIBUJAR, no al calcular
  - p_nulo, n_iter_nulo, auc_nulo_obs: float/int/float, traslación RÍGIDA de la máscara.
    `auc_nulo_obs` tiene que ser igual a `auc` (el driver aborta si difieren en más de 1e-9)
  - fuente: str, siempre "ckpt_limpio" en estos dos
  - label: str, la clase del CSV de la tarea. `folds_variante` la distingue de la predicha
  - primario: bool, False en 106552, 110616 (no_identificado) y B25-158899 (sin fila)
  - tier_fold: str, {ausente, test, val} de la LÁMINA, no del brazo
  - folds_usados: str, "0+2" / "0+1+2+3+4", los folds que se promediaron DE VERDAD
  - tarea: str, "grado_histologico_mitotic_rate_combined_5fold"
  - cabeza: str, "verdadera"
  - predicha, confianza: vacías (son del `json_out`)
  - folds_variante: str, {limpios, todos}. Es LA columna que separa los dos archivos
Filas: 12 cada uno (11 láminas × 1 universo + la 129741 con `region`).
  La B25-158899 se salta: no tiene fila en el CSV de la tarea ⇒ su cabeza verdadera no existe
Producido por: scripts/b9_atencion_12_laminas.py --fuente ckpt_limpio --folds {limpios,todos}
Consumido por: resultados.md §4, y las dos láminas de atención del deck del 07/09
```

**Trampas conocidas** (cuatro acá y una quinta abajo, que salió del cross-check).

1. **`tier_fold` describe la LÁMINA, no el brazo.** Con `--folds todos` la lámina entra igual
   por sus folds de `train`, así que un `tier_fold = ausente` en el archivo `_todos` no
   significa que ese brazo esté limpio. Lo que dice qué se promedió es **`folds_usados`**.
   El `meta_*.json` lo lleva escrito en `nota_tier_fold`.
2. **Siete de las once tienen `folds_usados = 0+1+2+3+4` en los DOS archivos**, o sea que sus
   filas son idénticas por construcción y su Δ es cero estructural, no un efecto medido
   (§4.a). Restar los dos archivos fila a fila y promediar las once **diluye** el contraste.
3. **`n_marcados` cuenta por SOLAPE (113 en las doce).** La escalera cuenta por CENTROIDE (94).
   Son dos mapeos de la misma marca ([[escalera-punto-a-parche-geometria]]).
4. **No se promedian contra `auc_por_lamina.csv`** (el primario `json_out`): otra familia, otra
   cabeza, otra definición de atención.

**Cross-check hecho.** `n_parches` y `n_marcados` de los dos archivos coinciden lámina a
lámina con `geometria_por_lamina.csv` del primario, y el gate de regresión reproduce los cuatro
valores del B8 a **1e-6** con el mismo driver que escribió estos archivos.

> **Quinta trampa, y la destapó este cross-check: estos dos archivos suman 107 parches
> marcados, no 113.** Los 113 son de las **doce** láminas; acá son **once**, porque la
> B25-158899 (6 parches marcados) se salta por no tener cabeza verdadera. El 113 sigue siendo
> el número del primario `json_out` y el 103 el de sus nueve. **Tres denominadores conviven en
> el mismo eje** (113 · 107 · 103) y cada tabla tiene que decir cuál usa
> ([[dos-numeros-iguales-denominador-distinto]]).

---

## 2. `escalera.csv`

```
CSV: escalera.csv
Path: results/b9_escalera_area/
Schema (12 columnas):
  - slide: str, la lámina
  - brazo: str, {sin_filtro, teselado, clam_mitosis, clam_gate, clam_combinado, azar}
  - presupuesto_mm2: str|float, {"lamina_entera", 30.0, 10.0, 3.0, 1.0}. COLUMNA MIXTA:
    comparar con == "lamina_entera" antes de castear a float
  - k_parches: int, ceil(presupuesto / area_parche), clampado a N. VACÍO en `sin_filtro`
  - area_real_mm2: float, k × area_parche. VACÍO en `sin_filtro`, que no tiene área comparable
  - marcas_dentro: float, marcas de `Mitosis` por CENTROIDE dentro de la máscara (de 94)
  - acreditadas_dentro: float, de ésas, las que HoVer-NeXt reencontró a 30 µm (de 26)
  - detecciones_dentro: float, detecciones de HoVer-NeXt dentro (de 732 · 707 teseladas)
  - det_por_mm2: float, detecciones_dentro / area_real_mm2
  - *_p975: float, sólo en `azar`: el p97,5 de las 200 repeticiones. Vacío en los demás
Filas: 264 = 12 láminas × (2 controles + 4 presupuestos × 4 brazos con filtro y azar)
Producido por: scripts/b9_escalera_area.py
Consumido por: resultados.md §5 y la lámina de la escalera del deck
```

**Trampas conocidas.**

1. **`presupuesto_mm2` es una columna MIXTA** (el string `"lamina_entera"` y cuatro floats).
   Un `astype(float)` la rompe.
2. **`sin_filtro` no tiene área**, a propósito: es la lámina como corrió el detector, e incluye
   tejido que el segmentador de CLAM descartó. Un `sum()` de pandas convierte su vacío en
   **0**, y un 0 ahí se lee como «cero área», que es lo contrario de lo que significa. El
   agregado lo vuelve a poner en vacío.
3. **Las columnas de conteo son FLOAT** porque el brazo `azar` reporta la media de 200
   repeticiones. En los otros cinco brazos son enteros exactos.
4. **`marcas_dentro` cuenta por CENTROIDE (94)**, no por solape (113). Ver trampa 3 del §1.
5. **En `presupuesto_mm2 == "lamina_entera"` los brazos con filtro son idénticos a
   `teselado` por construcción** (k = N). No es un resultado: es el chequeo de sanidad del
   emparejamiento punto→parche.

**Cross-check hecho.** Los trece chequeos del script pasan y quedan en `meta.json`
(`chequeos_fallidos: []`): peldaño «lámina entera» 732 · 26 en `sin_filtro` y 707 · 26 en
`teselado`, los tres brazos con filtro iguales a `teselado`, monotonía de
`acreditadas_dentro` en las 36 series, y los conteos duros (94 · 26 · 732 · 707 · 12 · 49.832
parches = 706,1 mm²).

---

## 3. `por_lamina.csv` y `agregado.csv`

```
CSV: por_lamina.csv          Path: results/b9_escalera_area/          Filas: 12
  slide, n_parches, paso_px, area_parche_mm2, mm2, marcas, acreditadas, detecciones,
  marcas_en_tesela, marcas_fuera, detecciones_en_tesela, detecciones_fuera, region_anotada

CSV: agregado.csv            Path: results/b9_escalera_area/          Filas: 22
  brazo, presupuesto_mm2, k_parches, area_real_mm2, marcas_dentro, acreditadas_dentro,
  detecciones_dentro, n_laminas, det_por_mm2
```

`por_lamina.csv` es la **geometría** y es donde se lee el hallazgo F1 del ADDENDUM:
`marcas_fuera` da **0 en las doce** y `detecciones_fuera` suma **25**. `paso_px` da **256 en
las doce** y sale de la moda por fila, nunca de la magnificación
([[patch-size-desde-geometria-h5]]).

`agregado.csv` es la suma sobre las doce y es **lo que va al deck**. `n_laminas` está para que
un subconjunto se note: si no dice 12, el agregado no es el publicado.

**Trampa**: `area_real_mm2` del agregado es la suma de las doce (36,0 mm² en el peldaño de
**3 mm² por lámina**, no 3). El presupuesto es **por lámina** y el área es **total**: la lámina
del deck tiene que decir las dos cosas o se leen como el mismo número
([[dos-numeros-iguales-denominador-distinto]]).

---

## 4. Snapshots

Los cuatro CSV **son** artefactos versionados bajo `results/`, así que no llevan copia en
`csv_snapshots/`: el snapshot existe para los CSV que viven en el servidor y pueden mutar
(`clam_environ/environ/...`), y ninguno de éstos lo hace.
