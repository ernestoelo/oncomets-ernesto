# Pre-registro — la atención de CLAM sobre las doce anotadas, y la escalera de área

> Escrito el **2-sep-2026**, **antes del código**. Es el eje que abrió la reunión del 1-sep con la
> pregunta «¿mejora el conteo de mitosis si a HoVer-NeXt se le pasa la atención de CLAM?».
>
> Sus insumos ya están verificados contra el archivo y **no se re-verifican acá**:
> [`hechos_verificados.md`](hechos_verificados.md) (sesión 38: el gate exacto, los tres tiers de
> fold limpio, la población de nueve) y [`insumos_json_out.md`](insumos_json_out.md) (sesión 39:
> dónde está la atención, qué es, la geometría de HoVer-NeXt, por qué filtrar no sube el conteo).
>
> **No toca modelo ni entrenamiento.** Es medición post-hoc en CPU sobre artefactos en disco. Va
> pre-registrado igual porque el grado de libertad que puede fabricar el resultado está en las
> **elecciones de lectura** (qué rama de atención, qué folds, qué población, qué agregado), y todas
> ésas se fijan acá y no después de ver el número.

---

## 1. El encuadre, escrito explícito

La pregunta es de **localización**, no de rendimiento: dado un modelo ya entrenado, ¿su atención
se concentra sobre los parches donde el patólogo marcó mitosis? Es la misma pregunta que el B8
contestó sobre **una** lámina (AUC 0,890 lámina / 0,903 región, cuatro checkpoints) y que acá se
extiende a **doce**, que es exactamente la corrección que el cruce de las 94 obligó a hacer: la
129741 era el mejor caso y no el típico ([[hovernext-especialista-segunda-etapa]]).

**No reabre ningún eje de rendimiento.** No se entrena nada, no se compara arquitectura, no se
mueve ninguna métrica de clasificación. El Hallazgo 12 y el 14 quedan donde están.

**La segunda pregunta, la de la reunión, no es la misma y se contesta aparte** (§6): filtrar las
detecciones de HoVer-NeXt con la atención de CLAM **no puede subir** el número de mitosis
encontradas, porque HoVer-NeXt ya corrió sobre la lámina entera y todo filtro es un subconjunto de
las 26 acreditadas. Lo que la restricción compra es **área**, y por eso lo que se mide es una
escalera de presupuesto en mm² y no un top-K ([[techo-filtro-antes-de-correr]] P2.a.ter,
[[carga-fija-no-k-fijo]]).

---

## 2. Las dos fuentes de atención, y por qué son dos

| brazo | qué es | rol |
|---|---|---|
| **`json_out`** | `clam_ensemble/attn_batch/json_out/<slide>__<tarea>.json`, de `sgaete` | **primario** |
| **`ckpt_limpio`** | `environ/results_modelo_combined_5fold/grado_histologico_mitotic_rate_combined_s1/s_{f}_checkpoint.pt`, promediando sólo los folds limpios de cada lámina | **control de honestidad** |

`json_out` es primario por decisión de Ernesto (D3 del handoff): **es la fuente que Sebastián va a
usar para tejido neoplásico**, así que los números cruzan sin re-trabajo. Y para el gate invasivo
es la **única** fuente con cobertura: del gate sólo existe el fold 0 y es nuestro, con ocho de las
doce en `train` (`insumos_json_out.md` §3.a).

**Tres propiedades del `json_out` que se declaran en toda tabla y todo pie de figura**, porque
ninguna es la que uno asume:

1. Es un **ensemble de los cinco folds**, ponderado por confianza ⇒ **contaminado por
   construcción**: cada lámina estuvo en `train` en dos a cinco de esos folds, y sólo la
   B25-158899 está limpia de los cinco.
2. Lee la rama de la clase **predicha** por cada fold, no la verdadera. La rama decide el
   resultado ([[rama-de-atencion-decide-el-resultado]]).
3. Es la familia **`_pth_balance`**, no la `_combined_5fold` de los números de referencia del B8.
   **Los dos brazos no son intercambiables y no se promedian entre sí.**

Y una regla de implementación: **su campo `patch_size` no se usa** (da 127 y 64 donde la geometría
del h5 da 256). El tamaño de parche sale de la moda del paso **por fila** del h5
([[patch-size-desde-geometria-h5]]). Las `coords` sí son exactas, así que el join contra
`parches_anotados_<slide>.csv` es **por coordenada** y no por vecino más cercano.

### 2.a Los tres tiers de fold limpio se declaran, no se promedian a ciegas

«Limpio» son tres cosas distintas y el orden de limpieza es **ausente > test > val**
(`hechos_verificados.md` §3). El brazo `ckpt_limpio` reporta el **tier por lámina** en su fila; el
agregado los mezcla, y eso queda dicho en el pie.

---

## 3. La población: nueve láminas en el primario

Decisión de Ernesto del 1-sep (`hechos_verificados.md` §4). El primario son las **nueve** con
`score_1/2/3`, que reúnen **103 de los 113** parches con `Mitosis`. Las otras tres se miden igual
y se **reportan aparte**:

- `106552` y `110616` son `no_identificado`, que significa «el reporte CAP no menciona tasa
  mitótica» y no un grado de severidad: leer esa cabeza como «dónde busca mitosis el modelo» es un
  salto que el material no sostiene.
- `B25-158899` **no tiene fila** en el CSV de la tarea ⇒ su cabeza de la clase verdadera no
  existe.

**Cuatro de las doce tienen 2 parches marcados y no se leen solas** (`103762`, `109609`, `110616`,
`106552`). Entran al agregado y a la tabla por lámina; no se comentan como resultado individual.

---

## 4. Qué se mide, con qué estadístico

**Unidad = parche.** El objeto medido es «la atención del parche», y positivo es «el parche
contiene al menos una marca de `Mitosis`».

| qué | cómo | de dónde |
|---|---|---|
| ordenamiento | `rank_auc` sobre rangos medios (`ranks_of`) — Mann-Whitney U normalizado | `scripts/atencion_vs_anotaciones.py:127,133` |
| incertidumbre | `ic_hanley_mcneil` (varía lo que el patólogo marcó, con el modelo fijo) | `scripts/auc_atencion_fold4.py:58` |
| nulo | `p_traslacion`: traslación **rígida** de la máscara sobre la grilla | `scripts/atencion_vs_anotaciones.py:159` |
| región | `REGION_ANOTADA`, **intervalo por lámina** | `scripts/cruce_94_marcas.py:71` |

**Se importan, no se copian.** El `CKPTS` de `atencion_vs_anotaciones.py` está atado al
pre-registro del B8 y **no se toca**; por eso el driver es un script aparte que importa, mismo
patrón y mismo motivo que llevó a `auc_atencion_fold4.py` a existir.

**El nulo es por traslación rígida, nunca por permutación de etiquetas**
([[nulo-espacial-traslacion-rigida]]): los parches marcados son contiguos, y permutar rompe esa
contigüidad y da un `p` optimista.

**El confinamiento a la región va como intervalo por lámina.** El escalar `Y_CORTE_REGION = 49920`
de `scripts/techo_atencion_topk.py:45` es de la 129741 y **da vuelta la B25-158899**, donde el
patólogo anotó la región de arriba.

### 4.a El agregado

Primario = **media sin ponderar sobre láminas**, cada lámina un voto (la lámina es la réplica).
Secundario = **pooled sobre parches**. Decisión de Ernesto del 1-sep (`hechos_verificados.md` §5):
el `n` por lámina va de 2 a 28, un factor 14, y ponderar por parches le daría a la 129741 y la
126504 la mitad del peso, que es exactamente el sesgo que el cruce de las 94 documentó.

### 4.b Los dos universos

Cada AUC se reporta en dos universos y **no se mezclan**: `lámina` (los N parches) y `región` (los
parches dentro del intervalo anotado, sólo para las dos láminas multi-región). Es la misma
separación que publica `sprints/B8_sprint8/atencion_vs_patologo/resultados.md` §1.

---

## 5. Dirección esperada, y cómo se leería cada resultado

Regla 9.a: métrica + subset + dirección, **sin gate numérico de pass/fail**. Con n de 2 a 28
parches por lámina, un corte binario forzaría un veredicto sobre ruido.

| resultado | lectura |
|---|---|
| **primaria** | AUC agregado de las nueve **por encima de 0,5**, con la mayoría de las láminas individuales por encima y `p_traslacion` bajo en las de `n` grande ⇒ la atención localiza mitosis. Es lo que el go/no-go de `insumos_json_out.md` §2 anticipa (0,810 contaminado) |
| **alternativa** | AUC agregado cerca de 0,5, o signo inconsistente entre láminas ⇒ la atención no localiza, y el eje de segunda etapa por atención se cierra |
| **regresión** | AUC agregado **por debajo** de 0,5 consistente ⇒ la atención evita sistemáticamente los parches con mitosis. Sería un hallazgo, no un bug, y exigiría revisar la rama leída antes de publicarlo |

**Lo que ya se sabe y por eso no cuenta como confirmación:** el 0,810 del go/no-go es de esta misma
fuente, contaminado, sin IC y sin nulo. El pre-registro no puede fingir que no existe; lo que sí
puede es fijar de antemano **qué agrega** la corrida completa (IC, nulo, brazo limpio, tier,
población declarada) y qué no.

**Ordenamiento esperado entre brazos:** el brazo **contaminado tiene que dar más alto que el
limpio**. Si no ordena así, la tabla de membresía está mal leída y es bug, no resultado.

### 5.a El gate de regresión: valor exacto a 1e-6

Sobre la **129741**, cabeza **verdadera**, brazo **`ckpt_limpio`**, familia
`results_modelo_combined_5fold` (`hechos_verificados.md` §1.a):

| ckpt | lámina | región |
|---|---:|---:|
| `seba_5fold_f0` | **0,925697** | **0,936444** |
| `seba_5fold_f2` | **0,916527** | **0,927269** |

Reproducir esos cuatro valores a **1e-6** distingue bug del driver de resultado. **No se usa el
0,890 como banda**: promedia cuatro checkpoints de tres directorios distintos y es del universo
lámina ([[gate-regresion-valor-exacto-no-banda]]). Y el `json_out` **no puede** reproducirlo: otra
familia, otra definición de atención, otro reparto de folds.

### 5.b Conteos duros que tienen que salir

**113** parches con `Mitosis` sumando las doce · **103** en las nueve del primario · **94** marcas
· **26** acreditadas · **732** detecciones · **12** láminas · **9** del primario. Las marcas de la
B25-158899 caen en `[0, 25600)` y las de la 129741 en `[49920, 80640)`.

---

## 6. La escalera de área — qué mide y qué NO mide

**Lo que NO mide.** No mide si filtrar «mejora» el conteo de mitosis. **No puede**: HoVer-NeXt ya
corrió sobre la lámina entera en las doce, así que «HoVer-NeXt + CLAM» es un **subconjunto** de las
732 detecciones y de las 26 marcas acreditadas, y el conteo **sólo puede bajar**
(`insumos_json_out.md` §6). Decirlo al revés en cualquier lámina o pie sería falso.

**Lo que mide.** Cuánta **área** compra cada marca retenida. Es la pregunta del patólogo («cuánta
superficie tengo que mirar») y la del sprint que viene (la zona de ~3 mm²).

Corolario operativo: **no se re-corre nada**. El filtro se aplica *post-hoc* sobre las detecciones
ya escritas, y **el brazo sin filtro sale gratis** — que es contra el que se lee cualquier
resultado restringido (P2.a.ter).

**La grilla.** Por lámina y por presupuesto ∈ {lámina entera, 30, 10, **3**, 1 mm²}, con
`k = ⌈presupuesto / 0,0142⌉` parches de mayor atención. El 0,0142 mm² es la tesela de HoVer-NeXt,
que mide **exactamente lo mismo** que un parche de CLAM sobre estas láminas
(`insumos_json_out.md` §4) ⇒ enmascarar por parches es enmascarar a la granularidad del detector.

| brazo | máscara |
|---|---|
| `sin_filtro` | la lámina entera (control, gratis) |
| `clam_mitosis` | top-k por atención de `grado_histologico_mitotic_rate_pth_balance` |
| `clam_gate` | top-k por atención de `invasion_carcinoma_gate_pth_balance` |
| `clam_combinado` | top-k por el producto de los rangos de las dos. **Exploratorio**, se declara como tal |
| `azar` | k parches al azar, **200 repeticiones**, se reporta media y p97,5 |

**Chequeos que el barrido regala, y que son parte del pre-registro:**

- En el peldaño «lámina entera» los brazos con filtro tienen que **coincidir** con `sin_filtro`:
  26 acreditadas, 732 detecciones. Si no coinciden, el emparejamiento punto→parche está mal.
- **Monotonía**: `acreditadas_dentro` **nunca sube** al bajar el presupuesto.
- Se reporta **cuántas marcas caen fuera de todo parche**: la teselación de CLAM no cubre lo que el
  segmentador de tejido descartó.

**Lo que se afirma con la escalera** es de la forma «bajar de X a Y mm² retiene Z de las 26
acreditadas», con `sin_filtro` y `azar` al lado. Nunca «el filtro encuentra más mitosis».

---

## 7. Salidas

| archivo | una fila por |
|---|---|
| `results/b9_atencion_12/auc_por_lamina.csv` | lámina × fuente × tarea × cabeza × universo |
| `results/b9_atencion_12/meta.json` | procedencia, versiones, semilla, conteos duros |
| `results/b9_escalera_area/escalera.csv` | lámina × brazo × presupuesto |
| `results/b9_escalera_area/por_lamina.csv` | lámina (geometría: N parches, mm², parche en px) |
| `results/b9_escalera_area/meta.json` | ídem |

Columnas de `auc_por_lamina.csv`: `slide, fuente, tarea, cabeza, universo, n_parches, n_marcados,
auc, ee, ic95_lo, ic95_hi, p_nulo, n_iter_nulo, tier_fold, folds_usados, label, primario`.

Columnas de `escalera.csv`: `slide, brazo, presupuesto_mm2, k_parches, area_real_mm2,
marcas_dentro, acreditadas_dentro, detecciones_dentro, det_por_mm2`.

**El esquema se le comunicó a `sgaete`** en el mismo mensaje que le avisa que consumimos su
`json_out` ([`aviso_sgaete.md`](aviso_sgaete.md)), para que su medición de tejido neoplásico y la
nuestra crucen sin re-trabajo. Si él propone otros nombres, se adoptan los suyos.

Los dos CSV nuevos pasan por `@csv-audit`.

---

## 8. Qué NO se hace en este eje

- **No se calcula precisión, F1, recall ni PQ** contra las marcas. Son positivos parciales: el
  patólogo marcó lo que le interesaba, no todo lo que hay.
- **No se compara el área en µm² entre clases** de HoVer-NeXt (su umbral está afinado por clase,
  [[descriptor-absoluto-trae-el-umbral]]), ni se usa el área del polígono del patólogo como medida
  del núcleo (sería medir el pincel de QuPath).
- **No se toca la GPU.** Todo CPU post-hoc.
- **No se escribe nada** en `clam_ensemble/`, `clam_environ/`, `clam_testing/`, `hover_net/`,
  `anotaciones/` ni `hover_next_reference/`.
- **No se promedian los dos brazos** de atención entre sí (§2.3).
- **No se lee sola** una lámina con 2 parches marcados.

## 9. Qué no se afirma

- Que el `json_out` reproduzca el 0,890 del B8. No puede, y no es su rol.
- Que un AUC alto implique que un top-k capture las mitosis. No lo implica: el AUC resume todos
  los umbrales y un top-k es uno solo, de los extremos ([[topk-percentil-no-auc]]). Por eso la
  escalera se mide y no se deduce.
- Que la contaminación del `json_out` tenga un tamaño conocido. Se sabe **en qué dirección**
  empuja (hacia arriba) y **cuántos folds** la producen; cuánto infla el número, no.
- Que las doce láminas sean representativas de la cohorte. Son las que el patólogo anotó, y
  Sebastián habló de 30.
