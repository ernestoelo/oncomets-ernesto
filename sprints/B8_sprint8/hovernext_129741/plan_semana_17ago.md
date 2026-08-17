# Plan de trabajo — semana del 17-ago: HoVer-NeXt sobre la 129741 + interpretabilidad CLAM/Mammoth

> Escrito el 17-ago-2026 en modo plan. La sesión que ejecute arranca limpia y sigue este documento.
> Sprint B8, rama `main`. Todo lo de acá está verificado hoy contra el servidor, no supuesto.

---

## Context

La reunión del viernes 14-ago ocurrió y Sebastián se pronunció sobre HoVer-NeXt: **le interesa
aunque no suba la métrica**. Su argumento no es de rendimiento sino de producto — un modelo de
detección e interpretabilidad que le **proponga zonas al patólogo** acelera el etiquetado, que es
hoy el cuello real del proyecto; y a 17× más rápido que HoVer-Net la herramienta es viable de
correr sobre la cohorte. Consecuencia metodológica que Sebastián explicitó y hay que respetar:
**se evalúa con las métricas del paper de HoVer-NeXt** (calidad y regularidad de lo segmentado
contra el etiquetado del patólogo), **no con AUC** — que además el paper nunca menciona.

De ahí salieron cuatro encargos, en el orden en que Sebastián los pidió:

1. Comparar el mapa de calor de **HoVer-NeXt solo** contra **CLAM → HoVer-NeXt** contra
   **CLAM + Mammoth → HoVer-NeXt**, sobre la lámina 129741 (la del patólogo, la misma de los
   mapas de calor de CLAM).
2. Generar sobre esa misma lámina los **mapas de atención, de expertos y de slots de CLAM+Mammoth**.
3. Idea de Ernesto, adoptada: hacer interpretable a HoVer-NeXt exhibiendo sus **mapas HV, el
   BCB-map, el raw class y el class-map** — o sea abrir la cadena interna, no solo su salida.
4. Al final de todo lo anterior: **más pruebas de CLAM+Mammoth con otras relaciones E×S**, para
   cubrir un rango de variabilidad mayor que el grid ya cerrado.

Resultado esperado de la semana: un `resultados.md` con la curva de las tres variantes, la tanda de
mapas de Mammoth sobre la 129741, la cadena interna de HoVer-NeXt abierta y explicada, y el grid
ampliado lanzado. Eso es material presentable para la próxima reunión sobre una pregunta —
«¿sirve esto para que el patólogo etiquete más rápido?» — que ninguna de las cuatro ramas cerradas
del proyecto (Hallazgos 11 a 14) llegó a tocar.

---

## Hallazgos de reconocimiento (verificados el 17-ago, no re-verificar)

| Qué | Estado |
|---|---|
| **Repo y pesos de HoVer-NeXt** | **NO están en el servidor.** Nada bajo `clam_testing2/`, nada en `hover_net/` (eso es HoVer-**Net**, de sgaete). **Ernesto autorizó hoy clonar el repo y bajar los pesos.** |
| **Las «30 WSI etiquetadas»** | En el servidor hay **12**, no 30: `/media/administrador/Storage1/sdonoso/anotaciones/*.bif - GDT.geojson` (dueño `sgaete` → **READ-ONLY**). Las 12 tienen features `.h5` y WSI, y **las 12 traen marcas de Mitosis** (94 en total; la 129741 aporta 26, la 126504 tiene 20 y la 128194 17). Faltan 18 → preguntarle a Sebastián. |
| **Checkpoint Mammoth para la 129741** | Existe y la lámina **no fue vista**: en `data/splits_kfold/carcinoma_ductal_insitu_presente_ci_reform_100`, la 129741 cae en **test del fold 4** (y en val del fold 2; en train en 0/1/3). El par CLAM/Mammoth del **job 4589** está en `results/b7_mammoth_interp/carcinoma_ductal_insitu_presente_ci_reform/clam{,_mammoth}_..._f4_20260717_1812_s1/s_4_checkpoint.pt`. Es la **misma tarea del grid E×S**, así que el hilo queda coherente. |
| Mammoth en tasa mitótica | **No existe** y no se va a entrenar: la 129741 está en **train en los 5 folds** de `grado_mitotic_3clases_pth_100`. |
| Interpretabilidad B7 | Corrió sobre **7 láminas TCGA**, **nunca sobre la 129741**. Los mapas de expertos y slots sobre esta lámina son trabajo nuevo. |
| Lámina | `/media/administrador/Storage1/sdonoso/wsi/129741/129741.bif` (symlink, legible). OpenSlide: 39669×80640, **0,465 µm/px**, 20×, 10 niveles. h5: `coords`+`features`, **4799 parches**. |
| Dos regiones de escaneo | Confirmado: el lienzo contiene el tejido **dos veces** (`region[1].y = 49920`; 2303 parches arriba, 2496 abajo). **Las 163 anotaciones caen todas abajo.** Hay que anticiparlo en cada figura y en cada caption. |
| Disco / GPU | 2,5 TB libres. GPU **congestionada**: 42/49 GB usados, jobs `4974` (sdonoso, 12 h corridas), `4981` (sgaete) corriendo y `4975`/`4980` (capstone) en cola. |

**Tooling que ya existe y se reusa (no reescribir):**

- [scripts/clam_vs_mammoth_attention.py](scripts/clam_vs_mammoth_attention.py) — atención CLAM vs Mammoth lado a lado + Spearman/Jaccard/entropía. Se maneja con un JSON de selección (`--selection`).
- [scripts/mammoth_interpretability.py](scripts/mammoth_interpretability.py) — 30 heatmaps por experto, montage, top-k a alta resolución, `expert_usage.csv`.
- [scripts/slot_heatmaps_contraste.py](scripts/slot_heatmaps_contraste.py) — heatmap por **slot** (2ª softmax `combine`). **Hardcodeado a las láminas del B7** en las líneas 48 y 53-55 y 123: hay que parametrizarlo.
- [scripts/atencion_vs_anotaciones.py](scripts/atencion_vs_anotaciones.py) — AUC de ranking atención vs marcas, con el nulo por traslación rígida.
- [scripts/alinear_anotaciones_qupath.py](scripts/alinear_anotaciones_qupath.py) — offset del geojson (`--geojson --slide_id --wsi`), imprescindible para la fase 5.
- [scripts/select_interp_slides.py](scripts/select_interp_slides.py) — genera el JSON de selección; sirve de molde para el de la 129741.

---

## La decisión de diseño que gobierna todo

**HoVer-NeXt se corre UNA sola vez sobre la lámina completa, y los brazos 2 y 3 se construyen
enmascarando esa salida post-hoc con el mapa de atención.** No se corre HoVer-NeXt sobre parches
recortados.

Cuatro razones, las cuatro verificadas en
[hovernext_mecanismo.md](sprints/B8_sprint8/papers_14_agosto/hovernext_mecanismo.md) §7 y §12:

1. **El pipeline espera una WSI.** Su foreground sale del thumbnail de OpenSlide y el stitcher
   existe para pegar ROI. Con parches sueltos hay que tocar código, no configurar.
2. **Los parches sueltos pagan un borde perimetral.** El propio paper evalúa Lizard sobre recortes
   centrales de 248 de 256 para no tener que detectar núcleos con el centro afuera del tile.
3. **No hay motivo de costo.** ~2 min por lámina entera. Restringir para ahorrar cómputo dejó de
   tener sentido; el único motivo que sobrevive es controlar falsos positivos (patrón **P2**).
4. **Deja los tres brazos pareados por construcción.** Lo único que cambia entre ellos es la
   máscara, que es exactamente la variable de estudio.

**Salvedad a declarar en el `resultados.md`**: enmascarar da la **cota superior** del pipeline
restringido, porque no paga la penalización de borde que sí pagaría correrlo sobre recortes.

---

## Fase 0 — Instalar HoVer-NeXt y auditar la plomería

**Autorizado hoy por Ernesto.** Bajo containment y bajo las mismas reglas que los 4 repos del 2-ago:
**REFERENCE ONLY, fuera del `PYTHONPATH`, sin import cruzado.**

1. `git clone https://github.com/digitalpathologybern/hover_next_inference` →
   `clam_testing2/hover_next_reference/`. Registrar el HEAD y la fecha.
2. Bajar los **dos** juegos de pesos siguiendo el README del repo (Ernesto autorizó los dos) →
   `clam_testing2/hover_next_reference/weights/`. Anotar tamaño y checksum.
   - **Lizard-Mitosis**: colon, **0,5 µm/px**, **trae clase de mitosis**. Nuestra lámina está a
     0,465 → remuestreo de **1,075×**, despreciable.
   - **PanNuke**: mama validada (6º de 19, mPQ 0,495), **sin clase de mitosis**, **0,25 µm/px** →
     habría que **ampliar 1,86×** una resolución que la lámina no tiene. **Declarar esa limitación
     en los resultados**: el brazo PanNuke corre sobre píxeles interpolados, no sobre detalle real.
3. **Entorno propio, sin contaminar `clam_latest`**:
   `conda create -p /media/administrador/Storage1/sdonoso/clam_testing2/envs/hovernext ...`
   (prefix bajo containment). Se invoca siempre por **binario absoluto** (workaround B).
4. **Auditoría de código** — cerrar de una vez las cuatro preguntas de mecanismo del §14 más dos
   nuevas, y escribirlas en `sprints/B8_sprint8/hovernext_129741/auditoria_codigo.md`:
   1. ¿Los mapas HV entran al post-proceso o se descartan?
   2. ¿De qué lado va el λ = 0,02?
   3. ¿Las vistas de TTA se sortean o se enumeran?
   4. ¿La entrada por tiles sueltos está expuesta?
   5. **¿Están accesibles el BCB-map, el raw class y los mapas HV del caché intermedio?**
      (el paper dice que el caché guarda el mapa de clases y el BCB **crudos, cuantizados a
      0-255, antes de post-procesar** → deberían estar; confirmarlo es lo que habilita la fase 2.b).
   6. **¿Cómo trata una `.bif` con dos regiones de escaneo?** El foreground sale del thumbnail →
      va a encontrar las dos. Decidir si se acota por bounding box a la de abajo o se corre entera
      y se filtra después (preferible lo segundo: es más barato y no toca su código).

**Sin GPU.** Clonado, descarga y lectura de código son CPU.

---

## Fase 1 — CLAM + Mammoth sobre la 129741 (encargo 2)

CPU pura, post-hoc, sin `sbatch`. **No depende de la fase 0 → corre en paralelo.** Es el entregable
más barato y el que no puede fallar por plomería ajena.

1. Escribir `sprints/B8_sprint8/hovernext_129741/interp_slides_129741.json` con el mismo schema que
   [sprints/B7_sprint7/interp_slides.json](sprints/B7_sprint7/interp_slides.json): una entrada,
   tarea `carcinoma_ductal_insitu_presente_ci_reform`, **fold 4**, `ckpt_clam` y `ckpt_mammoth` del
   job 4589 (paths en la tabla de hallazgos), `h5` = `.../features/h5_files/129741.h5`,
   `wsi` = `.../wsi/129741/129741.bif`, `y_true` leído del CSV de labels.
2. `clam_vs_mammoth_attention.py --selection <ese json> --out-root results/b8_hovernext_129741/interp`
   → `attention_clam.png`, `attention_mammoth.png`, `attention_side_by_side.png`, `attention_stats.json`.
3. `mammoth_interpretability.py --ckpt <mammoth f4> --h5 ... --wsi ... --out-dir .../expertos`
   → 30 heatmaps por experto, montage, contact sheet top-k, `expert_usage.csv`.
4. **Parametrizar `slot_heatmaps_contraste.py`** (añadir `--selection`, `--out`, `--slide`;
   quitar el diccionario hardcodeado de las líneas 53-55) y correrlo → heatmaps por **slot**.
   Mismo tratamiento para `build_slot_softmax_tables.py`, que asume nombres TCGA
   (`split("-01Z")` en la línea 56) y **se rompe con `129741`**.
   Son scripts nuestros, CPU, post-hoc: **no tocan modelo ni training, regla 9 no aplica.**
5. **Overlay de las anotaciones del patólogo** sobre los mapas de atención de los dos brazos,
   reusando `parches_anotados_129741.csv` (163 parches ya alineados, offset `dx = 3829`).
6. Opcional y barato: `atencion_vs_anotaciones.py` con el par CLAM/Mammoth del fold 4 → da el AUC
   de ranking de este checkpoint, que **no es el mismo** que el 0,890 ya medido (ese es de los
   checkpoints de tasa mitótica de Sebastián). Sirve como referencia para dimensionar la fase 3.

**Trampas obligatorias:** la atención de `attention_only` viene **pre-softmax** (aplicar
`softmax(dim=1)`); CLAM_MB tiene una cabeza por clase; y **el tejido sale dos veces** en todo mapa
sobre esta lámina.

---

## Fase 2 — HoVer-NeXt sobre la 129741 completa (encargos 1 y 3)

Depende de la fase 0. `sbatch` por si usa GPU, con `squeue` previo — y **la GPU está congestionada**,
así que se encola detrás y no se monopoliza. Presupuesto: **~2 min de cómputo por juego de pesos**,
más el tiempo de espera en cola.

**2.a — La corrida.** Los dos juegos de pesos sobre la lámina entera. Salidas Zarr/LZ4 a
`results/b8_hovernext_129741/hovernext/{lizard_mitosis,pannuke}/`. Registrar el **tiempo de pared
real** (es el dato que contrasta con las 3 h 36 medidas de HoVer-Net y con el ~2 min estimado).

**2.b — La cadena interna abierta (la idea de Ernesto).** Para dos o tres recortes representativos
— uno centrado en una mitosis marcada por el patólogo, uno de tumor sin marca, uno de estroma o
grasa — una figura de cuatro paneles en cadena:

`mapas HV` → `BCB-map` (3 canales: fondo / interior / borde) → `raw class` → `class-map` final

y encima el resultado del **watershed** y del **voto de mayoría** que asigna una clase por instancia.
Es el punto de diseño más limpio del pipeline: un decodificador dice **dónde** y el otro dice **qué**.
Si la auditoría de la fase 0 concluye que los mapas HV no se exponen en inferencia, se dice eso y se
muestran los tres restantes — **no se fabrica el panel que falta**.

**2.c — Descriptores de regularidad por instancia**: área en µm², **solidez** (área / área del
convex hull), circularidad `4πA/P²`, excentricidad. Distribuciones por clase, dentro y fuera de las
regiones marcadas. Esto **no es decoración**: HoVer-NeXt sacó el convex hull para ganar velocidad y
lo pagó en distancia de Hausdorff, así que la solidez es exactamente el eje donde se ve ese trueque.

---

## Fase 3 — Los tres brazos (encargo 1)

Todo post-hoc sobre la salida de la fase 2. **Confinado a la región anotada** (la de abajo, 2496
parches ≈ 35,4 mm²), igual que hizo la corrida `con_region/` del 1-ago: si una región recibiera más
atención que la otra se estaría midiendo la región y no las marcas.

**Los brazos:**

| Brazo | Máscara |
|---|---|
| 1. HoVer-NeXt solo | ninguna (toda la región anotada) |
| 2. CLAM → HoVer-NeXt | top-K parches por atención de **CLAM** (fold 4) |
| 3. CLAM + Mammoth → HoVer-NeXt | top-K parches por atención de **Mammoth** (fold 4) |

**El presupuesto K se barre, no se fija** — es el patrón **P2** aplicado de frente: un top-k se
dimensiona por percentil y hay que declarar el denominador alcanzable. Con AUC de atención 0,890 el
top-20 de esta lámina contiene **3 de 28** parches con mitosis; para la mitad hacen falta ~189 y
para todas ~1392. Por eso el entregable es una **curva**, no un número:

K ∈ {20, 50, 100, 189, 300, 500, 750, 1000, 1392, 2000, 2496}

**Las métricas, y qué significa cada una:**

1. **Recall de mitosis @ K** — de las 26 marcas (28 parches), cuántas caen en un parche de la
   máscara que además contiene ≥1 detección de mitosis de HoVer-NeXt.
   **El denominador es anidado y hay que declararlo explícitamente**: el brazo 1 fija el techo. Si
   HoVer-NeXt encuentra 18 de 26, ningún brazo restringido puede pasar de 18, y la curva de los
   brazos 2 y 3 mide **cuánto de ese techo sobrevive al filtro de atención**, no cuánto detecta.
2. **Área propuesta al patólogo @ K** — en mm² y en parches. El par (recall, área) **es** el
   entregable: es la forma medible del argumento de Sebastián sobre acelerar el etiquetado.
3. **Enriquecimiento** — mitosis detectadas por mm² dentro de la máscara contra fuera. Es el motivo
   de control de falsos positivos, el único que sobrevive cuando el cómputo deja de ser caro.
4. **Solapamiento de región** — Dice/IoU entre el mapa de densidad neoplásica de HoVer-NeXt
   (umbralizado) y los polígonos de Tumor/CDIS del patólogo. Reportar en las dos direcciones y
   recordar que **la ausencia de marca no es un negativo**.
5. **Contraste entre brazos 2 y 3** — Spearman entre los dos rankings de atención y Jaccard del
   top-K. Si los dos mapas coinciden, las curvas coincidirán y **eso es el resultado**, no un fallo.

**Lo que NO se calcula, y hay que escribirlo:** **PQ, bPQ, mPQ y SQ contra este geojson.** Las
marcas del patólogo **no son una segmentación exhaustiva de núcleos** — son positivos parciales y,
en el caso de mitosis, cuadrados de ~36 px que no son contornos nucleares. Cualquier PQ reportado
contra ellas sería inventado. De la familia del paper sobrevive legítimamente el **recall de
detección** (que es DQ sin su mitad de precisión) y los **descriptores de regularidad** de la 2.c.
Por el mismo motivo **no se reporta precisión de mitosis**: lo no marcado puede contener mitosis
reales, así que toda precisión contra este geojson está sesgada a la baja por construcción.

**Nota de alcance:** un head-to-head PQ contra HoVer-Net sobre esta lámina **no es posible con lo
que hay** — la corrida de sgaete (job 4714) fue sobre `TCGA-3C-AALI`, no sobre la 129741. Correrlo
costaría 3 h 36 de GPU y queda **fuera de este plan**.

---

## Fase 4 — Entregable

`sprints/B8_sprint8/hovernext_129741/resultados.md`, con:

- La curva recall-vs-área de los tres brazos, y su lectura.
- La cadena interna de HoVer-NeXt abierta panel por panel.
- Los mapas de atención, expertos y slots de CLAM+Mammoth.
- Una sección **«Qué no se afirma»** — es la higiene del sprint y acá hace falta más que nunca:
  una lámina, un anotador, positivos parciales, PanNuke corriendo sobre píxeles interpolados,
  enmascarado como cota superior del pipeline restringido, y **cero evidencia de que nada de esto
  mueva una métrica de lámina**.
- `meta.json` + `run.log` de provenance, como en todas las corridas anteriores.

Assets para presentar: tablas y gráficos **nativos** si van a deck; las figuras de mapas sobre
tejido van como imagen (es la excepción ya establecida: una fotografía de un resultado no es un
diagrama). Commits granulares, `git branch --show-current` antes de cada uno, **nunca `git add -A`**.

---

## Fase 5 — Extensión a las 11 láminas restantes (si sobra semana)

Mismo código, sin nada nuevo. Multiplica las marcas de mitosis por ~3,6 (26 → 94).

El paso que **no** es gratis: el offset del geojson está validado en **una** lámina. Para cada una
de las 11 hay que correr `alinear_anotaciones_qupath.py --geojson --slide_id --wsi` y **mirar los
tres criterios que reporta** antes de usar el resultado. Varias son `.bif` con más de una región de
escaneo (139 de 490 en la cohorte privada), así que el caso de las dos regiones es la regla y no la
excepción.

Preguntarle a Sebastián por las **18 láminas que faltan** para llegar a las 30 que mencionó.

---

## Fase 6 — Grid E×S ampliado (encargo 4, al final de todo)

**Requiere pre-registro y GPU.** Se hace **después** de lo anterior, como pidió Ernesto.

**Encuadre honesto, que el `prereg.md` tiene que dejar por escrito.** El grid E×S
**cerró en H_nula el 4-ago** (job 4774, 8 brazos × 5 folds sobre CDIS `_ci_reform`, brazos
`30:10 27:10 30:9 21:10 30:7 15:10 30:5 30:3`): la dirección del recorte resultó indistinguible y
el piso 30×3 perdió solo 0,039 de AUC. Ampliarlo es **reabrir una medición cerrada**, y el motivo
habilitante **no es un hallazgo técnico nuevo sino un encargo del supervisor**. Se declara así, sin
disfrazarlo de descubrimiento, y se apoya en el gate de gobernanza «co-firma de Sebastián» — que
acá viene pedido directamente por él, así que está cubierto de origen.

**Lo que el grid viejo no cubrió, y es donde vale la pena gastar la GPU:** todos sus brazos
**recortaban desde 30×10 en una sola dimensión**. Nunca cruzó al régimen de **forma extrema a igual
total** (`10:30`, `6:50`, `60:5`, `100:3`) ni **por encima** del control (`30:15`, `45:10`, `30:20`).
Ahí sí hay rango de variabilidad nuevo, que es literalmente lo que Sebastián pidió.

**Restricciones duras que el pre-registro debe respetar:**

- **Paired**: reusar `data/splits_kfold/carcinoma_ductal_insitu_presente_ci_reform_100`, los mismos
  splits del 4774 y del 4589 (patrón P1).
- **Semilla**: el pipeline es **determinista bit a bit**. Repetir una config con `--seed 1` no
  aporta un solo bit. Toda configuración nueva es nueva por su E×S; si además se quisiera replicar
  algo ya corrido, **exige semilla distinta**.
- **Presupuesto**: el 4774 fueron 40 runs en ~35 h de pared, y se pasó de las 24 h presupuestadas
  por contención ajena. Con 6 brazos × 5 folds ≈ 30 runs, presupuestar **~26-35 h** y avisar que la
  contención mueve el reloj, no la métrica.
- **Preflight obligatorio** en el `.slurm` (workaround G) y **no cambiar de rama con el job vivo**
  (workaround H).
- Métrica + dirección esperada pre-registradas (regla 9); **sin gate numérico rígido** (regla 9.a).
- Pasar por el subagente **`reviewer`** antes del `sbatch`.
- Considerar **`@grilling`** antes de escribir el `prereg.md`: es su caso de uso exacto y sigue sin
  estrenarse en producción.

---

## Verificación

Cada fase se da por cerrada cuando:

- **F0** — `hover_next_reference/` clonado con HEAD registrado, los dos juegos de pesos en disco
  con checksum, el env `hovernext` importa el paquete, y `auditoria_codigo.md` contesta las 6
  preguntas (o dice explícitamente cuál quedó abierta y por qué).
- **F1** — existen los tres PNG de atención, los 30 heatmaps de expertos con su montage, los
  heatmaps por slot, y `attention_stats.json`. Chequeo de sanidad: el mapa muestra el tejido dos
  veces y las anotaciones caen todas en la mitad de abajo. Si no, el offset se aplicó mal.
- **F2** — la salida Zarr existe para los dos juegos de pesos, el tiempo de pared quedó registrado,
  y la figura de cuatro paneles se lee sin explicación oral.
- **F3** — la tabla recall/área para los 11 valores de K por brazo, con el **techo del brazo 1
  escrito arriba de todo**. Chequeo de sanidad: en K = 2496 los tres brazos tienen que dar
  **idéntico**; si no, el enmascarado tiene un bug.
- **F4** — `resultados.md` con su sección «Qué no se afirma», commiteado.
- **F6** — `prereg.md` con GO del `reviewer`, `squeue` verificado, job encolado con su ID anotado.

---

## Reglas y trampas para la sesión ejecutora

- **Containment**: todo bajo `clam_testing2/`, incluido el env conda (por `-p`, no por `-n`).
- **READ-ONLY absoluto**: `clam_environ/`, `clam_testing/`, `hover_net/`, `wsi/` y
  **`anotaciones/`** (es de `sgaete`; los 12 geojson se leen, jamás se escriben ahí).
- **GPU solo por `sbatch`**, con `squeue` previo. Hoy hay 4 jobs ajenos y 42/49 GB ocupados.
- **Python siempre por binario absoluto** (workaround B). Para HoVer-NeXt, el de su propio env.
- **Cualquier proceso CPU largo va desatado** con `setsid nohup` y reanudable por su artefacto
  final (workaround J) — vale para el barrido de la fase 5.
- **No re-medir lo ya cerrado**: los percentiles de atención y el AUC 0,890 están en
  [sprints/B8_sprint8/atencion_vs_patologo/resultados.md](sprints/B8_sprint8/atencion_vs_patologo/resultados.md);
  el mecanismo y los números del paper, en `papers_14_agosto/`.
- **El sesgo de los positivos parciales tiene dirección y es conservador**: empuja toda AUC hacia
  0,5. Un número alto es creíble; uno en 0,5 es ambiguo, no negativo.
- Actualizar `sprints/B8_sprint8/objetivos_sprint8.md` (sigue sin las entradas del 11 y el 12-ago)
  y `progress/current.md` al cerrar.
