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
> dos regiones la misma lámina escaneada dos veces?» **NO está cerrada**: dos de los tres tests
> apuntan a que sí y el tercero no pudo correrse bien (§2.d). **No se registra ningún veredicto
> hasta que ese test funcione.** Lo que sigue abierto está en §5.

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

### 2.d Test de píxeles a level 0: NO CORRIÓ BIEN, y por eso no hay veredicto

El test que **decide** es el de arriba llevado al nivel de célula: si es el mismo vidrio, el
mismo punto físico muestra **las mismas células**; si son dos secciones seriadas del mismo
bloque, muestra tejido parecido con células distintas. Es lo único que separa las dos hipótesis
que sobreviven a §2.c.

**No funciona todavía.** Sobre un recorte de 1024×1024 en level 0 centrado en la ventana con
más tejido, la NCC da **−0.0045**, y el control corrido 64 px da **0.0090**. Los dos son cero:
eso no es «tejido distinto», es que **los dos recortes no están mirando el mismo sitio**. El
residuo de registro dentro del recorte salió dx = −233, dy = 357, que es más de lo que la
traslación gruesa (dy = −640 en level 0) debería dejar sin corregir.

Diagnóstico de por dónde va el error, para que la sesión que lo retome no empiece de cero:

1. El mapeo de coordenadas región 0 → región 1 mezcla el origen de la región (`y1 = 49920`) con
   el desplazamiento medido (`DY`), y el signo de `DY` no está verificado contra un caso
   conocido.
2. La traslación gruesa se mide sobre miniaturas **recortadas al mínimo común** (`w = min(w0,w1)`,
   `h = min(h0,h1)`), así que está en coordenadas de ese recorte, no del lienzo.
3. El paso `contenido` había encontrado el óptimo en dx = −256, dy = 50432, o sea **dy = +512
   respecto del origen nominal**; el paso `registro` mide **dy = −640**. Los dos no pueden ser
   ciertos a la vez y esa contradicción es la pista más corta.

**Hasta que esto cierre, la afirmación del B8 («las dos regiones son tejido distinto, no un
duplicado») NO se toca**, y tampoco se afirma lo contrario. Ver §5.

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

1. **Arreglar el test de level 0** (§2.d) y con eso cerrar el veredicto. Es el bloqueo real. La
   contradicción entre `dy = +512` (features) y `dy = −640` (píxeles) es por donde entrar.
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

- **Que las dos regiones de la 129741 sean la misma lámina escaneada dos veces.** Es lo que
  sugieren §2.c y la inspección visual, pero el test que lo decidiría no corrió (§2.d).
- **Que no lo sean.** El test de features (§2.b) no distingue, y quedó demostrado por qué: su
  control interno da el mismo número que la señal.
- **Que las 139 láminas con varias regiones tengan todas el mismo problema.** Lo medido es que
  su `.bif` declara más de una región de escaneo. Qué hay en cada una, no se miró: solo se
  abrió la 129741.
- **Nada sobre el `.csv` de Sebastián**, porque no sabemos cuál es.
