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
  abrió la 129741. *(Sigue vigente como advertencia. El «solo se abrió la 129741» quedó
  superado el 17-ago: el barrido de §7 abrió tres más, y la primera que corrió entera **no**
  reproduce su firma.)*
- **Nada sobre el `.csv` de Sebastián**, porque no sabemos cuál es.

---

## 7. ADDENDUM 17-ago-2026 (tarde): el barrido arrancó, y la 129741 no es representativa

Se lanzó el barrido del test de registro sobre las **129 láminas restantes de 2 regiones**
(`scripts/barrido_registro_multiregion.sh`, CPU, desatado con `setsid`, reanudable por el JSON
final). Salida en `barrido_138/`. Con **tres** láminas medidas ya aparecen dos cosas que el
documento de arriba no podía saber, porque **solo se había abierto la 129741**.

### 7.a El test rechaza muchas láminas, y no por la geometría de las regiones

De las tres primeras, **dos se pararon solas** antes de llegar al test decisivo:

| Lámina | Silueta (NCC registrada) | Resultado |
|---|---:|---|
| 118925 | 0.4792 | `[stop] solo 2 ventanas utilizables` |
| 119414 | **0.9993** | `[stop] solo 0 ventanas utilizables` |
| 120063 | 0.9847 | corrió completo (§7.b) |

El caso de la **119414 es el que enseña**: su silueta registra a **0.9993** contra un control
espejado de −0.32, o sea que a escala de arquitectura las dos regiones son casi idénticas — y
aun así la etapa A no consiguió **ni una** ventana utilizable. **No es un problema de tamaño de
las regiones**: se midió la geometría de las 130 y la razón de áreas mediana es **0.952**, con
solo **2** láminas de ventana de solape degenerada.

La causa está en los parámetros de selección de ventanas, que se fijaron sobre una lámina rica
en tejido:

- `--min-tejido 0.5` exige que la mitad de la ventana sea tejido;
- la exclusión de bordes de `auditar_regiones_escaneo.py:690` pide que el destino previsto entre
  entero con `--margen-a 2048` de holgura, que en una región chica descarta casi todo el marco;
- y el piso de **≥3 ventanas** (`:700`) está en el código, no en la CLI.

**Consecuencia operativa**: el rendimiento del barrido hay que leerlo como «cuántas láminas el
test **pudo** medir», no como «cuántas son duplicados». Las palancas para recuperar láminas
rechazadas son todas de CLI (`--min-tejido`, `--margen-a`, `--plantilla-a`) salvo el piso de 3.
**Nadie las tocó todavía**: el barrido corre con los valores por defecto y `--rot-max 8.0`.

### 7.b La 120063 corrió entera y NO reproduce la firma de la 129741

| Medida | 129741 | 120063 |
|---|---:|---:|
| NCC señal, medio | **0.3820** | **0.1432** |
| NCC control, medio | 0.0493 | 0.0494 |
| Separación señal-control | **29.5 sd** | **3.3 sd** |
| Ventanas sobre el máximo del control | **8 / 8** | **4 / 8** |
| Ajuste rígido: escala | 1.0117 | **1.0723** |
| Ajuste rígido: residuo RMS | 103 µm | **732 µm** |
| θ de la etapa B | −2.0 a −4.0 (agrupado) | **−8.0 a +8.0 (disperso)** |

Los dos perfiles son **cualitativamente distintos**. En la 129741 el campo de desplazamiento lo
explica un cuerpo casi rígido y las ocho ventanas coinciden; en la 120063 el ajuste pide un **7 %
de escala**, deja **732 µm** de residuo y los ángulos se reparten por todo el rango barrido,
incluidos los dos extremos. Eso es lo que el criterio pre-fijado
(`auditar_regiones_escaneo.py:591-601`) describe como el caso de **secciones seriadas**, no de
re-escaneo.

**Con una salvedad que impide llamarlo veredicto**: en la 120063 el segundo pico está pegado al
primero (ventana 4: NCC 0.3494 contra segundo pico 0.3345), o sea que la localización de la
etapa A es **ambigua**. Un etapa-A que no localiza produce una etapa B sin sentido, y eso es
indistinguible, con lo que hay hoy en la salida, de «el tejido de verdad es distinto».

### 7.c Sobre la saturación de la rotación

El barrido corre con **`--rot-max 8.0`** (el default del script es 1.5 y la corrida del 14-ago
usó 4.0 y saturó). La 120063 **igual satura**, pero en **los dos extremos a la vez** (+8.0 y
−8.0 en distintas ventanas). Eso ya no se lee como «el rango es corto»: se lee como que **no hay
una rotación consistente que encontrar** en esa lámina. Para la 129741, en cambio, el pendiente
de §2.d.1 sigue **abierto tal cual** — no se re-midió y su 0.3820 sigue siendo cota inferior.

### 7.c-bis Trampa al leer la tabla: la «separación en sd» no es comparable entre láminas

La **120361** cerró con **36.5 sd**, más que las 29.5 de la 129741 — y **no significa que esté
mejor registrada**. Su NCC medio es **0.1379**, un tercio del de la 129741. El número es alto
porque el denominador es la **sd del control**, que ahí vale 0.0181 y está estimada sobre
**3 ventanas** (el piso del test). Con n = 3 esa sd es ruido, y dividir por ella infla la
separación sin límite.

**Regla para leer el barrido**: comparar el **NCC medio de la señal** y las **ventanas sobre el
máximo del control**, y usar la separación en sd solo junto al **número de ventanas**. Una
lámina con 3 ventanas y una con 8 no son el mismo experimento.

### 7.d Qué NO afirma este addendum

- **Que la 120063 sean secciones seriadas.** Su perfil es el que el criterio asocia a ese caso,
  pero la ambigüedad de la etapa A (§7.b) admite la lectura alternativa de que el test falló en
  localizar. No es separable con lo que la salida guarda hoy.
- **Que las láminas rechazadas no tengan señal.** No se midieron: el test se paró antes.
- **Que 3 láminas digan algo de las 129.** Es el arranque del barrido, no su resultado.
- **Nada nuevo sobre la 129741.** No se volvió a medir.

---

## 8. ADDENDUM 17-ago-2026 (noche): el barrido terminó, y el veredicto se puede empezar a dar

El barrido cerró a las **20:10**, tras **198 min** de pared. Salida en `barrido_138/`, agregada por
[scripts/cosechar_barrido_registro.py](scripts/cosechar_barrido_registro.py) a
`barrido_resumen.csv`.

| | |
|---|---:|
| Láminas con JSON | **108** |
| Rechazadas por el test (`stop`) | **19** |
| Fallidas | **0** |

La tasa de rechazo final es **15 %**, no el 35 % que se veía a media corrida. El aviso de no
anticiparla estaba bien puesto.

### 8.a La mitad de las láminas medidas NO son interpretables, y eso es el primer resultado

Aplicando el **eje 1 del criterio pre-fijado** (`auditar_regiones_escaneo.py:591-601`), que pide
que la etapa A localice cada ventana con un pico **alto y único**, se cuenta por lámina en cuántas
ventanas el pico supera al segundo por al menos un 10 %:

| | láminas | |
|---|---:|---|
| La etapa A localiza (mayoría de ventanas con pico único) | **54** | 50 % |
| La etapa A **no** localiza | **54** | 50 % |

Las 54 de abajo **no son «secciones seriadas»**: son **no medibles**. Una etapa A que no localiza
produce una etapa B que mide ruido, y eso es indistinguible de que el tejido sea de verdad
distinto. Es la lección de la 120063 de §7.b, ahora cuantificada sobre 108 láminas.

### 8.b Entre las medibles, el perfil dominante es el de re-escaneo

Con los tres ejes juntos (pico único, cuerpo rígido, NCC muy sobre el control):

| Perfil | láminas | |
|---|---:|---|
| etapa A no localiza | 54 | 50 % |
| **perfil de re-escaneo** | **33** | 31 % |
| ambiguo | 20 | 19 % |
| **perfil de secciones seriadas** | **1** | 1 % |

Las 33 del perfil de re-escaneo tienen razón señal/control mediana **5,20**, escala mediana
**0,9996** y residuo rígido mediano **62 µm**: un cuerpo rígido explica el campo de
desplazamiento, que es exactamente lo que el criterio pre-fijado describe como la misma lámina
escaneada dos veces.

**Los cortes numéricos son posteriores a ver los datos** (el criterio pre-fijado es cualitativo:
«escala ~1», «residuo de pocos píxeles»). Por eso se reporta la sensibilidad:

| corte | re-escaneo | seriadas | ambiguo |
|---|---:|---:|---:|
| laxo (razón ≥2,5, banda 0,03, ≥60 %) | 37 | **1** | 16 |
| base (razón ≥3, banda 0,02, ≥75 %) | 33 | **1** | 20 |
| estricto (razón ≥4, banda 0,015, ≥87,5 %) | 21 | **1** | 32 |

Lo que se mueve con el corte es el reparto entre re-escaneo y ambiguo. **Las secciones seriadas
se quedan en 1 con los tres cortes**, y esa única lámina (`150986-3`) pide un **13 % de escala**
(0,8718), que se parece más a un ajuste malo que a un hallazgo.

### 8.c Se corrigen dos lecturas del ADDENDUM anterior

1. **La 120063 no es evidencia de secciones seriadas.** Falla la puerta del eje 1 con **1 de 8**
   ventanas de pico único. La salvedad que §7.b dejó anotada («su etapa A no localiza bien, así
   que no es veredicto») queda confirmada y cerrada: la lámina es **no medible**, y no hay que
   seguir citándola como el contraejemplo de la 129741.
2. **La 129741 sí es representativa, entre las medibles.** Contra las 54 que pasan la puerta cae
   en el **percentil 91** de NCC de señal, **89** de razón señal/control y **57** de residuo
   rígido. O sea es un buen ejemplar del perfil mayoritario, no una rareza. (Su NCC de 0,3820
   sigue siendo **cota inferior**: su barrido de rotación satura y **no se re-midió**.)
   Esto **relaja**, sin borrarlo, el «la 129741 no es representativa» que venía del handoff: era
   cierto con 3 láminas medidas, y con 108 ya no se sostiene en esta dimensión.

### 8.d Qué no se afirma

- **No se afirma que 139 de 490 láminas privadas sean re-escaneos.** Se midieron 108, la mitad no
  es interpretable, y de la otra mitad 33 muestran el perfil. El denominador honesto es
  **33 de 54 medibles**, no 33 de 490.
- **El 50 % no medible no está explicado.** Puede ser parámetros de selección de ventanas (§7.a,
  decisión todavía pendiente) o puede ser tejido de verdad distinto. **Este barrido no los
  separa.** *(Actualizado en §9: los parámetros quedaron DESCARTADOS por evidencia — el fallo es
  «sin señal» en 381 de 388 ventanas. Queda viva una tercera causa que este ADDENDUM no había
  considerado: que la etapa A no busque rotación.)*
- **No se re-midió la 129741**, así que su número sigue siendo cota inferior.
- **No se midió el efecto sobre los datasets de entrenamiento.** Sigue abierto.

---

## 9. ADDENDUM 17-ago-2026 (noche, 2ª parte): por qué la mitad no es medible

§8.d dejó declarado que **el 50 % no medible no está explicado**, con dos candidatos: los
parámetros de selección de ventanas o que el tejido sea de verdad distinto. Se atacó con dos
piezas. **La primera está cerrada; la segunda quedó corriendo.**

### 9.a El fallo es SIN SEÑAL, no ambigüedad ⇒ NO son los parámetros

`scripts/diagnostico_no_medibles.py` recupera el detalle **por ventana** que el CSV agregado
había perdido, y separa dos modos que son físicamente opuestos:

- **ambiguo**: hay pico, pero hay más de uno (el tejido se parece a sí mismo en varios sitios).
  El registro existe y la ventana no lo distingue ⇒ **lo arreglarían los parámetros**.
- **sin señal**: no hay pico. El mapa de NCC es plano contra su propio fondo ⇒ **los parámetros
  no lo arreglan**.

El estadístico que los separa ya estaba en cada JSON: `sd_sobre_fondo`, la altura del pico medida
en desviaciones del fondo del mapa. Es independiente del NCC absoluto, que depende del contraste
del tejido y no es comparable entre láminas.

| | |
|---|---:|
| Láminas agregadas | 108 |
| Ventanas totales | 732 |
| Ventanas que no localizan | 388 |
| **modo ambiguo** | **7** |
| **modo sin señal** | **381 (98 %)** |
| Láminas no medibles | 54 |
| Láminas clasificadas «sin señal» | **54 de 54** |

**Las 54 sin excepción caen en el modo sin señal.** Y no correlaciona con la densidad de tejido
ni con el número de ventanas utilizables.

**Consecuencia, que cierra un pendiente abierto desde §7.a**: relajar `--min-tejido` o
`--margen-a` **no** iba a recuperar esas láminas. La decisión que §7.a y el handoff dejaban
pendiente («¿re-corremos el subconjunto rechazado con parámetros relajados?») **queda contestada
que no**, y por evidencia, no por criterio.

### 9.b Queda una hipótesis de MÉTODO, y es la que estaba corriendo al cierre

`_buscar_local` (`auditar_regiones_escaneo.py:462`) busca **solo traslación**: la rotación entra
recién en la etapa B. Si las dos regiones están giradas entre sí, un template de 1024 px pierde
correlación aunque las células sean las mismas, y el mapa queda plano — que es **exactamente** el
«sin señal» observado. Sería una limitación **nuestra**, no un hecho del tejido.

`scripts/probe_rotacion_etapaA.py` la prueba barriendo θ dentro de la etapa A, sobre una muestra
de 16 láminas en tres grupos: **A** = no medible con silueta ≥ 0.95, **B** = no medible con
silueta < 0.95, **C** = medible (**control positivo**). Pre-registro escrito antes de correr:

- **rotación** ⇒ la fracción que localiza sube marcadamente **y** el θ ganador es **consistente
  entre ventanas** de la misma lámina (un vidrio gira entero);
- **tejido distinto** ⇒ barrer θ no recupera nada;
- **θ disperso entre ventanas = ruido, NO rotación**;
- **si el grupo C no reproduce su localización a θ = 0, el probe está roto y no se lee nada más.**

**Al cierre iba por 3 de 16, todas del grupo A, y NINGUNA del grupo C.** Las dos con números
leídos:

| Lámina | localiza θ=0 | localiza con rotación | NCC | θ* mediano (sd) |
|---|---:|---:|---|---:|
| 128696 | 0.25 | **1.00** | 0.130 → 0.275 | **+7.0° (0.9)** |
| 135924 | 0.12 | **0.88** | 0.156 → 0.278 | −10.5° (**3.7**) |

**La señal es fuerte y el resultado NO se puede leer todavía**, y las dos cosas son ciertas a la
vez. Fuerte: en las dos, barrer θ recupera casi todas las ventanas y **duplica** el NCC. No
legible: la 128696 tiene θ consistente (sd 0.9, la firma de rotación) pero la 135924 lo tiene
**disperso** (sd 3.7), que su propio pre-registro llama **ruido**; y sobre todo **el control
positivo no ha corrido**, y el pre-registro dice que sin él no se lee nada.

### 9.c Qué NO se afirma

- **Que las 54 no medibles se expliquen por rotación.** El probe iba por 3 de 16 y sin control.
- **Que no se expliquen.** Los dos casos leídos recuperan casi todas las ventanas al barrer θ.
- **Que el «33 de 54 medibles» de §8.b cambie.** Si la rotación resulta ser la causa, el
  denominador de medibles crece y **hay que recontar**; si no, §8.b queda como está. **Hoy no se
  sabe cuál de las dos.**
- **Nada nuevo sobre la 129741.** No se re-midió.

### 9.d Dos corroboraciones que NO dependen del probe (y por eso sí se pueden leer)

El probe todavía no se puede leer (le falta el control positivo, §9.b). Pero la hipótesis de
§9.b — que el «sin señal» de §9.a sea culpa de que la etapa A no busque rotación — tiene dos
consecuencias medibles **sobre datos que ya estaban en disco**, sin correr nada nuevo. Las dos
apuntan en la misma dirección, y ninguna de las dos es decisiva por sí sola.

**1. El argmax de la etapa A en las no medibles es indistinguible de ruido.** Si en una lámina
hubiera señal débil pero real, las ventanas se pondrían de acuerdo en un desplazamiento común
(el vidrio se mueve entero). Si no hay señal, cada ventana pone su máximo donde le toca y la
dispersión tiende a la de un argmax uniforme sobre el cuadrado de búsqueda de ±2048 px, que es
**1672 px**:

| | sd del desplazamiento entre ventanas de la misma lámina |
|---|---:|
| láminas medibles (n=54) | **564 px** (p25 271, p75 1000) |
| láminas NO medibles (n=54) | **1462 px** (p25 1239, p75 1761) |
| argmax de puro ruido (referencia teórica) | 1672 px |

Las no medibles están a un 13 % del valor de ruido puro. Es una confirmación **independiente**
de §9.a: no es que la señal sea débil, es que no hay. Lo mismo dice el residuo del ajuste rígido
(mediana 597 µm contra 235 µm en las medibles).

**2. La etapa B, que sí barre rotación, queda clavada en el borde de su barrido más seguido en
las no medibles.** El barrido corrió con ±8°:

| | ventanas con θ clavado en ±8° | \|θ\| mediano | sd de θ intra-lámina |
|---|---:|---:|---:|
| medibles | 7 % | 1,88° | 2,42° |
| NO medibles | **22 %** | 2,62° | **5,08°** |

**Esto es sugerente, NO decisivo, y la razón importa**: en una lámina no medible la etapa B
busca en el sitio que la etapa A eligió mal, así que su θ también es ruido. El dato es compatible
con «hay rotación grande sin resolver» y también con «no hay nada que alinear». **No usarlo como
evidencia de rotación por sí solo.**

**Salvedad de diseño del probe, para quien lo coseche.** El probe elige θ por **máximo NCC** (la
alineación físicamente correcta), no por máximo margen. Por eso una lámina puede **bajar** su
fracción que localiza al rotar: en su mejor alineación el pico resulta menos único. Elegir θ por
margen sería elegir el ángulo que más le conviene al criterio, y no se hizo a propósito.

**Y una advertencia sobre el corte de «θ consistente».** El pre-registro dice «sd chica», sin
número. Cualquier corte concreto (`scripts/cosechar_probe_rotacion.py` usa **sd ≤ 4°**) es
**posterior a ver los datos**, igual que los cortes de §8.b. Se reporta como tal y la cosecha
debe acompañarlo con su sensibilidad, no presentarlo como pre-registrado.

## 10. ADDENDUM 17-ago-2026 (noche, 3ª parte): el probe cerró, y la respuesta es mitad y mitad

El probe de §9.b terminó las 16 láminas. Cosechado con
[scripts/cosechar_probe_rotacion.py](scripts/cosechar_probe_rotacion.py) **en el orden que manda
su propio pre-registro**: el control positivo primero, y recién después las no medibles.

### 10.a El control positivo pasa ⇒ el probe se puede leer

| Lámina | localiza θ=0 | con rotación | NCC θ=0 → rot | θ* mediano | sd de θ* |
|---|---:|---:|---|---:|---:|
| 148781 | 1.00 | 1.00 | 0.396 → 0.590 | +4.0° | 0.5° |
| B25-151026 | 0.86 | 0.86 | 0.254 → 0.417 | −3.0° | 2.2° |
| B25-150006 | 0.62 | 0.75 | 0.324 → 0.365 | −3.5° | 1.1° |
| 136248 | 0.57 | 0.71 | 0.134 → 0.228 | +4.0° | 0.8° |

**Las 4 siguen siendo medibles a θ = 0** (fracción media 0.76): el probe reproduce el barrido y
la condición de lectura del pre-registro está cumplida.

**El control además obligó a corregir el criterio de consistencia, y esa es su segunda función.**
El pre-registro decía «θ disperso = ruido» sin fijar un corte. Medida sobre **todas** las ventanas,
la sd de θ* del grupo C es 5.16°: un corte fijo de 4° **rechaza a 3 de las 4 láminas del control**,
que localizan perfectamente. La causa es que θ* se elige por máximo de NCC y, en una ventana que no
localiza, la superficie en θ es plana y su argmax vaga, inflando la sd de la lámina entera. La
consistencia se mide **solo sobre las ventanas que localizan** — con eso las 4 del control pasan —
y el corte se calibra contra el peor de ellas: **sd ≤ 2.2°**. Un control positivo no solo valida el
probe: **calibra el criterio**.

**Dato que no esperábamos y que importa:** barrer θ sube el NCC **también en el control**
(0.277 → 0.400, con |θ*| mediano **3.8°**). O sea **hay rotación entre las dos regiones también en
las láminas medibles**: la etapa A la venía **tolerando**, no evitando.

### 10.b Seis de doce no medibles se recuperan barriendo θ

| grupo | | localiza θ=0 → rot | pasan a medible |
|---|---|---:|---:|
| **A** (silueta ≥ 0.95) | n=8 | 0.12 → **0.48** | **4 de 8** |
| **B** (silueta < 0.95) | n=4 | 0.29 → **0.45** | **2 de 4** |
| C (control) | n=4 | 0.76 → 0.83 | 4 de 4 (ya lo eran) |

**6 de las 12 no medibles cruzan el umbral de medibilidad** (`frac_localiza ≥ 0.5`, el mismo
criterio del barrido) cuando la etapa A busca rotación. Las tres más limpias traen la **firma de
cuerpo rígido** que el pre-registro pedía — θ consistente entre ventanas:

| Lámina | localiza θ=0 → rot | θ* mediano | sd de θ* | lectura |
|---|---:|---:|---:|---|
| 128696 | 0.25 → **1.00** | **+7.0°** | 0.9° | rotación rígida |
| 135924 | 0.12 → **0.88** | **−10.5°** | 2.1° | rotación rígida |
| 145819 | 0.33 → **0.83** | **+8.5°** | 1.6° | rotación rígida |
| B25-150012 | 0.38 → **0.88** | −6.0° | 5.0° | recuperada, θ no consistente |
| B25-158771 | 0.12 → 0.50 | +9.0° | 11.5° | recuperada, θ no consistente |
| 152303 | 0.25 → 0.50 | −4.5° | 9.1° | recuperada, θ no consistente |

**El |θ*| mediano de las recuperadas es 7.8°.** El barrido de rotación de la etapa B llega a ±8°
y su default es **±1.5°**: las rotaciones que hacían falta estaban **fuera de rango por diseño**.

De las otras 6, **5 no se recuperan** — con θ barrido de −20° a +20° siguen sin localizar y su θ*
queda disperso (sd 11-16°) — y **1 queda indeterminada**: la 145917 tiene la mayoría de sus
ventanas con θ* **clavado en el borde** del barrido, así que su rotación real podría estar fuera de
±20° y no se puede afirmar que la rotación no la explique. Para las 5, la lectura de §9.a se
sostiene entera: **no hay señal que encontrar**.

| veredicto | láminas |
|---|---:|
| recuperada por rotación (θ consistente, sd ≤ 2.2°) | **3** |
| recuperada, θ no consistente | **3** |
| no recuperada | 5 |
| indeterminada (θ clavado en el borde) | 1 |

**Una lámina empeora** (142430, 0.38 → 0.12). No es un bug: θ* se elige por el máximo de NCC, y un
ángulo que sube el pico puede subir también el segundo, así que el margen baja. Ninguna del
control cruza hacia abajo.

### 10.c Consecuencia: el «33 de 54 medibles» de §8.b queda PROVISIONAL

Esto es lo que el pre-registro anticipó como «trabajo, no un ajuste de redacción».

Extrapolando 6/12 a las 54 no medibles — **con el intervalo, que es ancho**: Clopper-Pearson 95 %
sobre 6 de 12 da **[0.21, 0.79]**, o sea **~27 láminas recuperables, rango [11, 43]**. El pool de
medibles pasaría de 54 a **~81, rango [65, 97]**.

**Y no sabemos cómo clasifican las recuperadas.** El perfil (re-escaneo / seriada / ambiguo) sale
de la etapa B, que **no se corrió** sobre ellas. Entonces:

- El **denominador** de §8.b está subestimado, probablemente por cerca del doble.
- El **numerador** (33 con perfil de re-escaneo) es un piso, no un total.
- **La proporción 33/54 = 61 % no se puede proyectar**: las recuperadas podrían repartirse de otra
  forma, y justamente son las que más girada tienen la segunda región.

Para cerrarlo hace falta **re-correr el test con rotación en la etapa A**, no reinterpretarlo.

### 10.d Qué NO se afirma

- **No se afirma que las 54 se expliquen por rotación.** La mitad de la muestra sí; la otra mitad
  resiste un barrido de ±20° y sigue sin señal.
- **No se afirma la cifra 27.** Sale de 12 láminas y su IC va de 11 a 43.
- **No se afirma que las 6 recuperadas sean re-escaneos.** Cruzan la puerta de medibilidad; el
  perfil lo da la etapa B, que sobre ellas no corrió.
- **Las 3 «no consistentes» son evidencia más débil que las 3 rígidas.** Cruzan el umbral sin un θ
  común, que es lo que el pre-registro pedía como firma.
- **No cambia nada de §9.a.** Que el fallo sea «sin señal» y no ambigüedad sigue en pie: la
  rotación es justamente un mecanismo que **produce** falta de señal, y no rehabilita relajar
  `--min-tejido` ni `--margen-a`.
- **Nada nuevo sobre la 129741.** Sigue sin re-medirse; su 0.3820 sigue siendo cota inferior — y
  ahora con un motivo más para pensar que está subestimado.
