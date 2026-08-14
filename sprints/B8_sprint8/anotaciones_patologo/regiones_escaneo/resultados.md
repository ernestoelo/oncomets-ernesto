# Regiones de escaneo en la cohorte privada: qué se midió y qué no cierra todavía

> **Encargo B de la reunión del 12-ago-2026.** Sebastián explicó que las «dos láminas» que
> aparecieron al evaluar la 129741 no son dos láminas sino **un error en un `.csv` donde se
> repetía dos veces lo mismo**, dijo que hay más WSI con el mismo defecto, y pidió registrarlo.
> Ernesto puso la condición que manda: *«quiero que verifiques lo que dijo Sebastián porque yo
> no lo entendí, así que luego de ello, se registra el hallazgo»*. Primero verificar, después
> registrar.
>
> **Escrito el 13-ago-2026.** Todo lo de acá se midió en esta sesión salvo donde se cita otro
> documento. Script: [`../../../../scripts/auditar_regiones_escaneo.py`](../../../../scripts/auditar_regiones_escaneo.py).
> Provenance en `meta.json`, log del barrido en `run_barrido.log`.
>
> ## ⚠ Estado: el ALCANCE está medido, el VEREDICTO no
>
> La pregunta «¿cuántas WSI más?» **está contestada con nombres** (§3). La pregunta «¿son las
> dos regiones la misma lámina escaneada dos veces?» **NO está cerrada**. **No se registra
> ningún veredicto hasta que el test decisivo cierre.** Lo que sigue abierto está en §5.
>
> **Actualización 14-ago-2026.** El test de level 0 estaba roto y **quedó arreglado**: no era el
> bug de signo que se había diagnosticado sino un problema de resolución, y ahora mide
> correspondencia celular real (NCC 0.3820 contra 0.0493 del control, 8/8 ventanas, §2.d). Con
> eso **la lectura 2 gana terreno**, pero el número cae **entre** las dos hipótesis que quedan
> vivas y el barrido de rotación sigue saturado, así que el veredicto sigue sin registrarse.
> Además se **corrigió un argumento equivocado de §2.c**: la disposición de los seis fragmentos
> NO distingue un re-escaneo de dos secciones seriadas.

---

## 1. Las tres lecturas de lo que dijo Sebastián

Ernesto no entendió la explicación, así que en vez de adivinar cuál era se enumeran y se testean.

| | Lectura | Estado |
|---|---|---|
| **1** | Un `.csv` **nuestro** tiene la lámina dos veces | **REFUTADA** (§1.a) |
| **2** | El `.bif` contiene **dos escaneos de la misma lámina**, y la duplicación está aguas arriba, en el worklist de digitalización del laboratorio | **NO RESUELTA**, y es la que mejor calza (§2) |
| **3** | Dos `slide_id` distintos apuntan al mismo tejido (tipo `X` y `X-2`) | **REFUTADA** como explicación de este caso (§1.b) |

### 1.a Lectura 1: no hay ningún CSV nuestro con la lámina repetida

Verificado en la sesión del 13-ago (mañana), contra disco, en lectura. Se buscaron `slide_id`
repetidos en las cuatro familias de CSV del pipeline:

| Directorio | Archivos | `slide_id` duplicados |
|---|---|---|
| `environ/csv_privado/` | los 13 `dataset_*_label.csv` | **0** |
| `environ/csv/` | idem, combinado | **0** |
| `environ/csv_tcga/`, `environ/csv_histai/` | idem | **0** |
| `environ/csv_balance/`, `environ/csv_balance_ci/` | idem | **0** |

Y en los `dataset_validation.csv`, que son los que `run_create_patches.slurm` pasa como
`--process_list` y por lo tanto los que gobiernan qué se parchea:

| Archivo | Filas | Duplicados |
|---|---:|---:|
| `csv_privado/dataset_validation.csv` | 561 | **0** |
| `csv/dataset_validation.csv` | 3350 | **0** |
| `csv_tcga/dataset_validation.csv` | 864 | **0** |
| `csv_histai/dataset_validation.csv` | 1925 | **0** |

**La lectura literal de la frase de Sebastián no se sostiene.** Si el `.csv` del que hablaba
existe, no es ninguno de los nuestros. Memoria: [[csv-duplicado-sebastian-no-esta-en-nuestros-csv]].

### 1.b Lectura 3: los sufijos `-1` / `-2` son bloques, no duplicados

La cohorte privada tiene varias láminas por caso con sufijos `-1`, `-2` (`102737-1`,
`102737-2`, y también `102737-1-2`). Son **bloques distintos del mismo caso** y el `case_id`
los agrupa. No es un error y no explica lo de la 129741, que es **una sola carpeta con un solo
`.bif`** conteniendo dos regiones. Queda descartada por escrito para que no vuelva.

---

## 2. Lectura 2: ¿son las dos regiones de la 129741 el mismo tejido?

### 2.a El punto de partida, y por qué el test previo no alcanzaba

El B8 ya había testeado esto y concluido que no eran un duplicado: coseno medio entre parches
«gemelos» geométricos **0.708** contra **0.503** entre parches al azar
([`../hallazgos.md`](../hallazgos.md) §2, [`../../atencion_vs_patologo/resultados.md`](../../atencion_vs_patologo/resultados.md) §2.b).

Ese test es débil, y por una razón concreta: las dos regiones tienen la **misma altura**
(30720) y anchos que difieren en **1280 px**, o sea cinco parches de 256. Si el emparejamiento
«gemelo» no corrigió ese desfase, un duplicado real se habría medido desalineado por hasta
cinco parches, y 0.708 es perfectamente compatible con eso.

### 2.b Test de features, con el desfase corregido

Barrido 2D de traslación `(dx, dy)` en múltiplos del paso de grilla, sobre las features CONCH
del `129741.h5`, sin abrir la WSI. La grilla arranca en (0,0) con paso fijo, así que una
traslación por un múltiplo del paso manda lattice sobre lattice y los gemelos son coincidencias
**exactas** de coordenada. Eso es lo que el test viejo no hizo.

Geometría medida: paso de grilla **256 px**, banda 0 `y 1856..28096` con **2303** parches,
banda 1 `y 51904..78528` con **2496** parches. Coincide con los 2303 / 2496 ya registrados.

| Medida | Valor |
|---|---|
| Coseno de pares al azar dentro de la banda 0 | 0.502 ± 0.194 |
| Coseno de pares al azar dentro de la banda 1 | 0.496 ± 0.198 |
| Coseno de pares al azar entre las dos bandas | 0.498 ± 0.196 |
| **Óptimo del barrido** | **dx = −256, dy = 50432** |
| Coseno medio en el óptimo | **0.811** (mediana 0.834) |
| Coseno medio sobre los 441 offsets | 0.636 ± 0.038 |
| A cuántas desviaciones está el óptimo | **4.59** |
| Cobertura del emparejamiento | 753 / 2303 = **0.327** |

**La corrección del desfase era real**: el óptimo no está en el `dy` nominal (50176) sino
256 px más abajo y 256 a la izquierda, y sube el coseno de 0.708 a **0.811**.

**Lo que este test dice, contra el criterio fijado antes de mirar.** El criterio era: lo que
separa un re-escaneo de una sección vecina es que el emparejamiento óptimo sea **casi biyectivo**
y con un desplazamiento **único y consistente**. Salió partido:

- **Único y consistente: SÍ.** Un solo óptimo, a 4.59 desviaciones del offset típico. No es
  difuso.
- **Casi biyectivo: NO.** Cobertura 0.327.
- Y el dato que más pesa: **ningún gemelo llega a coseno 0.99, y solo el 0.66 % pasa 0.95**
  (p99 = 0.944). Un re-escaneo del mismo vidrio debería dar features casi idénticas.

**Control del vecino más cercano, y es el que desarma el test entero.** Para cada parche de la
banda 0, el mejor coseno contra **cualquier** parche de la banda 1 da **0.9013**. Parece alto,
hasta que se mira el control: el mejor coseno contra cualquier **otro parche de su propia
banda** da **0.9009**. Idénticos a tres decimales. O sea que las features CONCH son **tan
suaves sobre el tejido** que el parche de al lado ya se parece 0.90, y el estadístico no puede
separar «duplicado» de «tejido parecido». **El test de features no decide, en ninguna
dirección.** Por eso hubo que ir al píxel.

Salida completa: `contenido_129741.json`.

### 2.c Test de píxeles a escala gruesa: las dos regiones son la MISMA LÁMINA

Se volcaron las dos regiones a PNG con openslide (`129741_region0.png`, `129741_region1.png`,
level 6, downsample 64) y se registraron por búsqueda exhaustiva de traslación entera.

| Medida | Valor |
|---|---|
| Mejor traslación | dx = 0, dy = −10 px de miniatura (**dy = −640 px de level 0**) |
| NCC sin registrar | 0.9508 |
| **NCC registrada** | **0.9569** |
| **Control: NCC contra la región 1 espejada** | **−0.1590** |

Y a ojo no hay duda: los **seis fragmentos de tejido** aparecen en las dos regiones con el
mismo contorno, el mismo tamaño y la **misma disposición relativa**. Dos secciones seriadas se
montan a mano sobre el vidrio; reproducir la posición y la rotación de seis fragmentos sueltos
a esa precisión no es algo que pase montando dos veces.

**Esto es evidencia fuerte de que la lectura 2 es correcta**: un mismo vidrio digitalizado dos
veces dentro del mismo `.bif`.

> **CORRECCIÓN 14-ago-2026: el párrafo de arriba tiene un argumento equivocado y hay que
> descontarlo.** Decía que reproducir la posición de seis fragmentos sueltos «no es algo que pase
> montando dos veces». Es falso: los fragmentos **no se montan uno por uno**. Van embebidos
> juntos en el mismo bloque de parafina, el corte sale del bloque como una cinta única con todos
> los fragmentos **en su posición relativa**, y esa cinta se monta entera. Dos secciones seriadas
> del mismo bloque **conservan la disposición de los fragmentos por construcción**, así que la
> inspección visual de §2.c **no distingue** las dos hipótesis. Lo que sigue en pie de §2.c es la
> medida (NCC 0.9569 registrada contra −0.1590 espejada), pero **como evidencia de que las dos
> regiones son el mismo bloque, no de que sean el mismo vidrio**. El peso de la decisión queda
> entero sobre §2.d.

### 2.d Test de píxeles a level 0: ARREGLADO el 14-ago, y ahora SÍ mide

El test que **decide** es el de §2.c llevado al nivel de célula: si es el mismo vidrio, el mismo
punto físico muestra **las mismas células**; si son dos secciones seriadas del mismo bloque,
muestra tejido parecido con células distintas. Es lo único que separa las dos hipótesis que
sobreviven a §2.c.

#### Por qué la primera versión daba cero, que no era el bug que se creía

El 13-ago se dejó anotado que el error estaba en el mapeo de coordenadas (que mezclaba el origen
de la región con el desplazamiento medido) y que la contradicción entre `dy = +512` del paso
`contenido` y `dy = −640` del paso `registro` era la pista más corta. **Las dos cosas resultaron
falsas**, verificadas contra el archivo:

- La 129741 tiene `region[0].x = 0` y `region[1].x = 0`, así que el término del origen que
  faltaba en el mapeo **vale cero en esta lámina**. Era un bug latente de generalidad (habría
  mordido en una lámina con orígenes distintos), no la causa. Queda arreglado igual.
- No había contradicción: derivando el signo de la búsqueda gruesa se obtiene
  `dy_contenido = (y1 − y0) − DY`, o sea `DY = 49920 − 50432 = −512` contra los −640 medidos.
  **Difieren 128 px**, que es lo que suman la cuantización de la grilla del h5 (±128) y la de la
  miniatura (±64). Los dos números eran compatibles.

**La causa real es de resolución, no de signo.** La posición en la región 1 se derivaba de un
**único offset global medido a level 6**, donde 1 px de miniatura son **64 px de level 0, o sea
unas cinco células**. Aun con el mapeo perfecto, la cuantización deja hasta ±32 px de error, y
cualquier rotación entre los dos escaneos agrega mucho más. Un NCC a level 0 necesita precisión
de pocos píxeles: **el test daba cero por construcción, midiera lo que midiera**.

#### El arreglo: la posición no se deriva, se busca

`registro` quedó reescrito en dos etapas, con la maquinaria verificada aparte
(`tests/test_registro_geometria.py`):

| Etapa | Qué hace |
|---|---|
| Silueta | NCC de las dos regiones a level 6. Es la medida de §2.c y **la domina el contorno**, no las células |
| A | Ocho ventanas de 1024 px **repartidas en una grilla 4×4** sobre la región (repartirlas importa: por densidad a secas, los empates al 100 % las amontonan todas en un fragmento). Cada una se **localiza** dentro de ±2048 px a level 2 |
| B | A level 0, plantilla de 512 px alrededor de lo que encontró A, con búsqueda residual ±48 px y barrido de rotación |

El **control de sitio equivocado** es la misma plantilla buscada en el destino localizado de
**otra** ventana, y corre con **los mismos grados de libertad** que la señal (misma búsqueda de
traslación y mismo barrido de rotación). Sin esa simetría la comparación quedaría amañada a
favor de la señal.

#### Lo que mide

| Medida | Señal | Control de sitio equivocado |
|---|---|---|
| NCC a level 0, medio | **0.3820** | 0.0493 |
| mediana | 0.4083 | 0.0465 |
| rango | 0.2488 .. 0.4521 | máximo 0.0671 |
| Ventanas por encima del máximo del control | **8 / 8** | |
| Separación | **29.5 sd** del control | |

**Hay correspondencia a escala celular, y no es marginal.** Las ocho ventanas, repartidas sobre
11.8 mm de vidrio, superan el máximo del control. El control de maquinaria (una plantilla
buscada contra sí misma) da NCC 1.0000 en (0,0), así que el camino de código está bien.

#### Lo que todavía NO cierra, y por eso sigue sin haber veredicto

1. **El barrido de rotación sigue pegando en el borde.** Con ±1.5° las ocho ventanas eligieron
   −1.50°; con ±4.0° eligen entre −2.0° y −4.0°, y una toma el extremo. El 0.3820 es una **cota
   inferior**, no el valor.
2. **El θ óptimo varía entre ventanas** (−2.0 a −4.0). Un cuerpo rígido daría el mismo ángulo en
   todas. O hay deformación local, o los picos de la etapa A (NCC 0.11 a 0.30) son demasiado
   ruidosos para fijar el ángulo.
3. **El ajuste rígido del campo da residuo RMS 103 µm** (máximo 154 µm) con rotación −2.354° y
   escala 1.0117. Eso es mucho para dos imágenes del mismo vidrio, que deberían llevarse una a
   otra con residuo de pocos píxeles.
4. **0.38 cae entre las dos hipótesis.** Un re-escaneo bien registrado debería dar 0.8 a 0.9.
   Dos secciones seriadas cortadas a 3 a 5 µm **comparten núcleos** (un núcleo de 8 µm aparece en
   dos cortes consecutivos), así que también producen correspondencia celular parcial. **El valor
   medido no separa todavía las dos.**

**Hasta que esto cierre, la afirmación del B8 («las dos regiones son tejido distinto, no un
duplicado») NO se toca**, y tampoco se afirma lo contrario. El paso siguiente está en §5.1.

---

## 3. Alcance: cuántas WSI privadas más tienen varias regiones de escaneo

Esto sí está cerrado, y es lo que Sebastián pidió cuantificar. Barrido de las **589 carpetas**
de `/media/administrador/Storage1/sdonoso/wsi/`, leyendo las propiedades
`openslide.region[N].*` del `.bif` sin sufijo de tinción (el que usa el pipeline), más la
geometría de la grilla de cada `.h5`. 1 min 40 s de CPU.

| | Láminas |
|---|---:|
| Carpetas barridas | 589 |
| Con `.bif` sin sufijo de tinción | **490** |
| Sin `.bif` sin sufijo (solo IHQ, o nombre distinto) | 99 |
| **Con 1 sola región** | 351 |
| **Con 2 regiones** | **130** |
| **Con 3 regiones** | **8** |
| **Con 4 regiones** | **1** |
| **Total con más de una región** | **139** (28,4 % de las 490) |

**La lista con nombres está en `laminas_multiregion.csv`**, que es lo que permite depurarlo
después. Las primeras: `118925`, `119414`, `120063`, `120361`, `128291`, `128605`, `128696`,
`128771`, `128774-2`, `129440`, `129500`, `129741`, `129743`, `129749`, `130301`…

**Sebastián tenía razón en que hay más, y son muchas más de las que uno esperaría: casi tres de
cada diez.** Eso vale independientemente de cómo cierre §2.d, porque es geometría declarada por
el propio archivo.

Dos datos de control que salieron del mismo barrido:

- **Toda la cohorte privada está a 0,4650 µm/px y `objective-power = 20`**, las 490 sin una
  excepción. Confirma [[cohortes-magnificacion-fisica]] con n grande, que hasta ahora se
  apoyaba en la 129741.
- **La geometría del h5 NO es un sustituto de openslide**: concuerda en 320 láminas y discrepa
  en 169. El heurístico de bandas parte la grilla en cualquier hueco vertical de tejido, y una
  lámina de una sola región con fragmentos separados también lo dispara. Sirve de tamiz barato,
  **no de medición**. Quien use `n_bandas_h5` como si fuera el número de regiones se va a
  equivocar en una de cada tres.

---

## 4. Qué NO cambia, pase lo que pase con §2.d

Conviene decirlo para no exagerar el impacto:

- **El resultado principal del B8 sobrevive por construcción.** La corrida definitiva
  `con_region/` está **confinada a la región anotada** (N = 2496, AUC 0.903), así que no toca
  la otra región en absoluto. Si las dos regiones resultan ser el mismo tejido, lo que queda
  contaminado es el universo `lamina` (el AUC 0.890), y el sentido de la contaminación es que
  **infla el denominador con parches duplicados**, no que invente la señal.
- **El guion de la lámina 5 del deck del B8 no queda falso.** Lo que dice (que hay dos regiones,
  que las marcas del patólogo caen todas en una, y que esa región recibe algo menos de atención)
  es cierto en las dos hipótesis. No hay que regenerar el deck.
- **Las 61 anotaciones del patólogo caen todas en la región de abajo**, y eso tampoco se mueve.

---

## 5. Lo que queda abierto

1. **Cerrar el veredicto con el test de level 0, que ya funciona** (§2.d). Ya no es «arreglarlo»:
   mide, y mide señal fuerte. Lo que falta es **empujar el registro hasta que el NCC deje de
   subir** y ver dónde se estabiliza, porque ahí está la respuesta:
   - **Iterar el ajuste**: usar la rotación del ajuste rígido como **centro** del barrido de la
     etapa B en vez de centrarlo en cero, re-medir el campo con la predicción mejorada, y
     repetir. Hoy el barrido arranca en cero y se le acaba el rango.
   - **Ampliar `--rot-max`** hasta que ninguna ventana elija el extremo (con ±4.0° una todavía
     lo toma).
   - El criterio de lectura ya está fijado: **si el NCC trepa a 0.8 o 0.9, es el mismo vidrio**
     (la lectura 2 de Sebastián); **si se estanca cerca de 0.4 con residuo elástico de ~100 µm,
     son dos secciones seriadas** del mismo bloque montadas en el mismo vidrio, y entonces la
     afirmación original del B8 queda confirmada y la de Sebastián no calza.
   - **Falta un control positivo de verdad**: nada en este dataset se sabe que sea un re-escaneo
     genuino, así que el «0.8 a 0.9 esperable» es teoría, no una medida. La forma de conseguirlo
     es **correr el test sobre una muestra de las otras 138 láminas multi-región** (§5.6): si
     alguna da 0.9, esa es la referencia empírica y además ya se sabe cuáles están afectadas de
     verdad. Ese barrido es CPU pura, ~1 a 2 min por lámina, y conviene lanzarlo desatado.
2. **Si la lectura 2 se confirma**: ADDENDUM fechado en
   [`../../atencion_vs_patologo/resultados.md`](../../atencion_vs_patologo/resultados.md) §2.b y
   en [`../hallazgos.md`](../hallazgos.md) §2, **sin reescribir el original**, diciendo qué se
   midió después, con qué método, y **qué no cambia** (§4). Más el número de láminas afectadas.
3. **Si se refuta**: registrar el test bueno como confirmación fuerte de lo ya escrito y
   decirle a Sebastián, con los números, que su explicación no calza con lo medido.
4. **La pregunta para Sebastián que la verificación no puede contestar sola: cuál es el `.csv`
   del que hablaba.** No es ninguno de los nuestros (§1.a). Si es del laboratorio, no lo tenemos
   y no lo podemos auditar. Preguntarlo con esa forma
   ([[verificar-antes-de-pedir-dato]]: primero verificamos lo que se puede, después preguntamos
   lo que falta).
5. **Las 99 carpetas sin `.bif` sin sufijo de tinción** no se investigaron. Puede ser normal
   (casos solo-IHQ) o puede esconder otro defecto de nomenclatura. Sin mirar.
6. **El efecto sobre las otras 138 láminas** no se midió. Si el veredicto es «duplicado», la
   pregunta siguiente es cuántos parches del dataset son copias, y eso sí toca los universos de
   entrenamiento.

---

## 6. Lo que este documento no afirma

- **Que las dos regiones de la 129741 sean la misma lámina escaneada dos veces.** El test
  decisivo ya corre y da señal celular fuerte (§2.d), pero su valor (0.38) cae **entre** lo que
  daría un re-escaneo y lo que daría un par de secciones seriadas, y el registro todavía no
  convergió.
- **Que no lo sean.** El test de features (§2.b) no distingue, y quedó demostrado por qué: su
  control interno da el mismo número que la señal.
- **Que 0.8 a 0.9 sea el número que daría un re-escaneo real.** Es lo esperable en teoría, pero
  **no hay ningún re-escaneo conocido en este dataset contra el cual anclarlo** (§5.1).
- **Que la disposición de los seis fragmentos pruebe nada** sobre re-escaneo contra secciones
  seriadas. Ese argumento de §2.c está corregido y retirado.
- **Que las 139 láminas con varias regiones tengan todas el mismo problema.** Lo medido es que
  su `.bif` declara más de una región de escaneo. Qué hay en cada una, no se miró: solo se
  abrió la 129741.
- **Nada sobre el `.csv` de Sebastián**, porque no sabemos cuál es.
