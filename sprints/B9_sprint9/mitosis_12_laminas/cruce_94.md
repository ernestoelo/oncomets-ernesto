# El cruce de las 94 marcas: HoVer-NeXt contra el patólogo sobre las 12 láminas

> Ejecutado el **25-ago-2026**, CPU y post-hoc, sin GPU y sin escribir fuera del repo.
> Script: [`scripts/cruce_94_marcas.py`](../../../scripts/cruce_94_marcas.py).
> Salidas: [`results/b9_cruce_94/`](../../../results/b9_cruce_94/).
>
> Generaliza a las doce láminas anotadas el cruce que el B8 hizo sobre la 129741 sola
> (13 de 26). Es el análisis que el barrido de las once (job 5070) habilitó y que nadie
> había corrido.

---

## 0. Cómo se lee esto, antes del número

Cinco condiciones. No son advertencias de cortesía: si alguna se ignora, el número
significa otra cosa.

1. **La unidad es marcas de `Mitosis`: 94.** No parches (28, que es el techo de alineación
   de la 129741), no detecciones (732 = 177 + 555), no polígonos (472 anotaciones en
   total). Mezclar unidades es el error más fácil de cometer acá, porque las cuatro
   cuentas conviven en el mismo directorio.
2. **No se calcula precisión y no se llama falso positivo a nada.** Las marcas son
   **positivos parciales**: el patólogo señaló donde la evidencia es clara, no todo lo que
   existe ([[anotaciones-patologo-qupath]]). Una detección sin marca encima puede ser una
   mitosis real que nadie marcó.
3. **Un recall agregado no es el recall de HoVer-NeXt.** El denominador son **las
   marcadas**, no las mitosis de la lámina. Es «de lo que el patólogo señaló, cuánto
   reencuentra», y nada más.
4. **Seis láminas tienen 3 marcas o menos, y tres concentran 63 de las 94.** El número que
   se lee es el agregado; la fila por lámina va con su `n` al lado y no es una medición
   independiente. Un recall desde `n=1` no distingue nada.
5. **El techo de A3 no promete recall.** Que las 94 de 94 caigan sobre un parche extraído
   dice que **la alineación no acota** el resultado, no que la detección vaya a encontrarlas
   (patrón P2.a: es una cota, no una predicción).

---

## 1. El resultado

**26 de las 94 marcas** a la tolerancia adoptada de 30 µm, o sea **27,7 %**.

> **Los 30 µm son una DISTANCIA, no un tamaño.** Es la separación máxima entre la marca del
> patólogo y el centroide de la detección para contarlas como el mismo objeto. Las doce
> láminas están a la **misma** resolución (0,465 µm/px), así que la tolerancia no compensa
> ninguna diferencia de escala entre ellas. Escribirla sin su sustantivo la vuelve ilegible
> ([[parametro-necesita-su-semantica]]).

| Tolerancia (µm) | 7,5 | 15 | 22,5 | **30** | 50 | 75 | 100 | 150 | 200 | 300 |
|---|---|---|---|---|---|---|---|---|---|---|
| TP sobre 94 | 26 | 26 | 26 | **26** | 26 | 27 | 28 | 33 | 36 | 41 |
| Recall | 27,7 % | 27,7 % | 27,7 % | **27,7 %** | 27,7 % | 28,7 % | 29,8 % | 35,1 % | 38,3 % | 43,6 % |

**El corte no decide nada en el rango creíble**: el resultado es plano de 7,5 a 50 µm, que
son las tolerancias con las que la literatura de detección de mitosis trabaja. Lo que crece
después es el emparejamiento a 150 µm o más, donde una detección y una marca ya no son el
mismo objeto: se barre hasta 300 µm para **mostrar** dónde el emparejamiento deja de ser
creíble, no para elegir de ahí.

El emparejamiento es **uno a uno** (húngaro con corte). Contar por distancia mínima
inflaría el recall reusando la misma detección para varias marcas.

## 2. La tabla por lámina, con su `n`

| Lámina | Marcas | Detecciones | Det. en la región anotada | TP a 30 µm | Recall | Mediana de la distancia a la detección más cercana |
|---|---|---|---|---|---|---|
| 129741 | 26 | 177 | 82 | **13** | 50,0 % | 14 µm |
| 126504 | 20 | 109 | 109 | **5** | 25,0 % | 323 µm |
| 128194 | 17 | 45 | 45 | **4** | 23,5 % | 193 µm |
| 124729 | 8 | 10 | 10 | **1** | 12,5 % | 744 µm |
| 124806 | 6 | 74 | 74 | **3** | 50,0 % | 39 µm |
| B25-158899 | 6 | 7 | **2** | 0 | 0,0 % | 1402 µm |
| 144317 | 3 | 10 | 10 | 0 | 0,0 % | 4152 µm |
| 164001 | 3 | 20 | 20 | 0 | 0,0 % | 1538 µm |
| 106552 | 2 | 10 | 10 | 0 | 0,0 % | 3378 µm |
| 103762 | 1 | 252 | 252 | 0 | 0,0 % | 933 µm |
| 109609 | 1 | 13 | 13 | 0 | 0,0 % | 2021 µm |
| 110616 | 1 | 5 | 5 | 0 | 0,0 % | 2581 µm |
| **Total** | **94** | **732** | | **26** | **27,7 %** | |

Cinco láminas acreditan al menos una marca, y esas cinco concentran **77 de las 94**. Las
siete restantes suman 17 marcas y ninguna acreditada.

## 3. Tres cosas que la tabla dice y el agregado esconde

### 3.a La 129741 aporta la mitad de los aciertos y es el mejor caso, no el típico

Sacándola, las once restantes dan **13 de 68 = 19,1 %**, con la misma forma de escalera
(plana en 13 de 7,5 a 50 µm, 14 a 75 y 100, 16 a 150, 18 a 200, 21 a 300). El 50 % de la
129741 no se replica en ninguna otra salvo la 124806, que tiene 6 marcas.

Importa porque **todo el B8 se construyó sobre esa lámina**. El 13 de 26 no era pesimista:
era el caso favorable.

### 3.b El rango de detecciones es enorme y no acompaña a las marcas

De **5** detecciones en la 110616 a **252** en la 103762, con mediana 16. Las dos láminas de
los extremos tienen **una** marca cada una. No hay relación visible entre cuánto detecta
HoVer-NeXt en una lámina y cuánto marcó el patólogo en ella, lo que era de esperar con
positivos parciales: el patólogo marcó una muestra, no un censo.

La consecuencia operativa es que **no se puede asumir homogeneidad entre láminas** para
nada aguas abajo (ni para un conteo por mm², ni para un hotspot, ni para una concordancia
ordinal).

### 3.c La región anotada de la B25-158899 es la de ARRIBA, no la de abajo

Las dos láminas con más de una región de escaneo son la 129741 y la B25-158899
([[regiones-escaneo-bif-cohorte-privada]]), y **el patólogo no anotó la misma**:

| Lámina | Regiones | Región anotada | Anotaciones dentro |
|---|---|---|---|
| 129741 | `[0, 30720)` y `[49920, 80640)` | la de abajo, `region[1]` | 61 de 61 |
| B25-158899 | `[0, 25600)` y `[30720, 58880)` | **la de arriba, `region[0]`** | 38 de 38 |

Un corte escalar del tipo `y >= Y_CORTE` sirve para una y **da vuelta la otra**. Por eso el
script guarda el **intervalo** de la región y verifica que las marcas caigan dentro, en vez
de heredar la constante `Y_CORTE_REGION = 49920` de
[`scripts/techo_atencion_topk.py:45`](../../../scripts/techo_atencion_topk.py#L45), que era
de la 129741 y sólo de ella.

Con el intervalo correcto, la B25-158899 tiene **2 de sus 7 detecciones** en la región
anotada, no 5. Su cero es un problema de detección, no de alineación.

### 3.d Las marcas que se escapan NO son más chicas

Es la primera pregunta que hizo Ernesto al ver el número, y merece contestarse porque la
tolerancia de 30 µm invita a confundirla con un tamaño: si el detector fallara con las mitosis
chicas, el 27,7 % significaría otra cosa.

`pares_<slide>.csv` ya trae la columna **`lado_px`**, el lado mayor de la caja envolvente del
polígono del patólogo en px de nivel 0 (`cruce_hovernext_marcas.py:63`). Sobre las 94:

| grupo | `n` | lado mediano | media | rango |
|---|---|---|---|---|
| acreditadas | 26 | **36 px** (16,7 µm) | 38,2 px | 22 a 66 |
| falladas | 68 | **36 px** (16,7 µm) | 40,0 px | 19 a 66 |

Las medianas coinciden y las falladas son, si algo, **levemente más grandes**. **No hay señal de
que el detector falle por tamaño.**

**La salvedad manda y hay que decirla junto al número**: 36 px es exactamente el bbox mediano
del **pincel de radio fijo de QuPath** ([[anotacion-tamano-objeto-vs-region]] §2), así que este
proxy mide el pincel tanto como el núcleo. Sirve para **descartar** un sesgo grande de tamaño,
no para afirmar que los dos grupos tienen núcleos iguales.

**Por qué no se mide sobre la segmentación, que sería lo natural**: una marca fallada no tiene
instancia de clase `mitosis` por definición, así que habría que leer el núcleo de la clase que
le tocara, y **el área no es comparable entre clases de HoVer-NeXt** porque el umbral de
foreground está afinado por clase ([[descriptor-absoluto-trae-el-umbral]]). La comparación
acertadas contra falladas sería entre clases distintas por construcción.

## 4. Por qué el cero de siete láminas no es un problema de alineación

Es la sospecha natural: si las marcas quedan lejos de toda detección, quizás el offset está
mal. Tres argumentos dicen que no.

1. **Los offsets se validaron con un criterio independiente y anterior.** A3 (21-ago) los
   derivó por geometría del contenedor y verificó por contención en parche: las **94 de 94**
   marcas caen sobre un parche extraído, y las 472 anotaciones dan `verif_a` alto en las
   doce. Este cruce no aporta ni resta a esa validación.
2. **Donde algo empareja, empareja apretado.** En las cinco láminas con TP la escalera es
   plana desde 7,5 µm, o sea que los aciertos están a **menos de 16 px**. Un offset global
   equivocado desplazaría **todas** las marcas de la lámina por igual y no dejaría cinco
   aciertos a 7,5 µm junto a quince fallos a 300 µm. La 126504 es el caso claro: 5 aciertos
   a 7,5 µm y una mediana de 323 µm.
3. **Las láminas con cero son casi todas las de pocas detecciones.** 110616 tiene 5
   detecciones en la lámina entera; 144317, 10; 106552, 10; 109609, 13. Con esa densidad, la
   distancia esperada de una marca cualquiera a la detección más cercana es de miles de
   micras aunque la alineación sea perfecta.

La excepción aparente es la **103762**: 252 detecciones y su única marca a 933 µm. Con una
sola marca no hay nada que concluir, y es exactamente el caso que la condición 4 del §0
manda no leer por separado.

## 5. Qué queda dicho y qué no

**Queda dicho.** Sobre las doce láminas anotadas, HoVer-NeXt con los pesos Lizard-Mitosis
reencuentra **26 de las 94 marcas** de mitosis del patólogo a 30 µm, con emparejamiento uno
a uno, y el resultado es insensible al corte en todo el rango creíble. La 129741 (50 %) es
el mejor caso de las doce, no el típico: sin ella el agregado baja a 19,1 %.

**No queda dicho.**

- **No** es el recall de HoVer-NeXt sobre las mitosis de estas láminas. El denominador son
  las marcadas.
- **No** hay precisión, ni F1, ni falsos positivos. Contra positivos parciales no son
  computables, y decirlo es parte del resultado, no una omisión.
- **No** se explica *por qué* falla. La hipótesis vigente del B8 sigue siendo que su clase
  de mitosis se validó **sólo en colon** y esto es mama
  ([[hovernext-especialista-segunda-etapa]]); este cruce es consistente con ella pero no la
  prueba, y el ensemble PanNuke **no puede** contestarla porque no tiene clase de mitosis.
- **No** se midió si las 13 falladas de la 129741 quedaron **segundas por poco**. Eso exige
  reconstruir la grilla de probabilidades desde `129741_raw_256_cls.zip`, y es el único
  camino barato que separa «recalibrar el umbral» de «reentrenar la cabeza». Sigue
  pendiente, y ahora es más caro de generalizar: **las once corrieron sin `--keep_raw`**, así
  que ese zip existe únicamente para la 129741.
- **No** cambia nada de lo que el B8 dejó cerrado. La 129741 reprodujo su escalera
  **idéntica**, que es la condición bajo la cual estos números se pueden leer.

## 6. Procedencia y chequeos

| Qué | Valor |
|---|---|
| Detecciones | job **5008** (129741) y job **5070** (las once), pesos `lizard_mitosis` |
| **Entrada del detector** | la **WSI entera**, en las doce (`main.py --input <WSI>`, `scripts/run_hovernext_slides.slurm:144`). **Sin CLAM delante**: no hubo selección de parches por atención ni mapa de calor a la entrada |
| Anotaciones | `sdonoso/anotaciones/<slide>.bif - GDT.geojson`, READ-ONLY |
| Offsets | `sprints/B8_sprint8/anotaciones_patologo/offset_<slide>.json` (A3, 21-ago), los doce con `dy=0` |
| Escala | 0,465 µm/px, verificado en las doce (Ventana a 20×) |
| Emparejamiento | húngaro uno a uno con corte, `TOL_ADOPTADA_UM = 30.0` |

Los tres chequeos que decidían si esto se podía leer, los tres en verde:

- Suma de marcas por lámina = **94**. El glob sobre `anotaciones/` devuelve **trece**
  geojson, no doce: el extra es `103762.bif - Series 0-full.geojson` y contarlo daría **95**.
  Por eso la lista de láminas del script es explícita y el sufijo es siempre `- GDT`.
- Suma de detecciones = **732** (177 + 555).
- **Regresión de la 129741**: escalera idéntica a
  `results/b8_hovernext_129741/cruce_marcas/recall_por_tolerancia.csv` en las diez
  tolerancias (13 plano de 7,5 a 75 µm, 14 a 100, 17 a 150, 18 a 200, 20 a 300). El script
  la verifica contra el CSV del B8 y **aborta** si difiere: una discrepancia sería un bug de
  la generalización, no un resultado.

El script preserva el original: `cruce_hovernext_marcas.py` no se tocó, y de él se importan
`marcas_mitosis()`, `emparejar_pares()`, `TOLS_UM` y `TOL_ADOPTADA_UM`. El emparejamiento no
se re-implementó.

## 7. Salidas

| Archivo | Qué tiene |
|---|---|
| `por_lamina.csv` | una fila por lámina: marcas, detecciones, región anotada, TP y recall a 30 µm, mediana de distancia, offset |
| `recall_por_tolerancia_agregado.csv` | la escalera de las 94 |
| `recall_por_tolerancia_por_lamina.csv` | forma larga (lámina × tolerancia): permite recomputar cualquier subconjunto sin re-correr |
| `pares_<slide>.csv` | una fila por marca: coordenadas, distancia a la más cercana, si quedó acreditada y con qué detección |
| `meta.json` | procedencia, unidad, qué no es, y el estado de los chequeos |
