# Auditoría de código de HoVer-NeXt — las 6 preguntas de mecanismo

> **Fase 0 del plan de la semana** (`plan_semana_17ago.md`). Escrito el **17-ago-2026**.
> Todo lo de acá sale de **leer el código clonado**, no del paper y no de suposiciones.
> Cada afirmación cita `archivo:línea`.
>
> Repo: `clam_testing2/hover_next_reference/`, clonado el 17-ago de
> `github.com/digitalpathologybern/hover_next_inference`.
> **HEAD `29134a303fb6ade6c8654c160a84f8331021a035`** (26-oct-2025), 508 KB, 9 módulos en `src/`.
> **REFERENCE ONLY**: fuera del `PYTHONPATH`, sin import cruzado. Se ejecuta por su
> entrypoint (`main.py`), que es su uso previsto; nada de él se importa desde nuestros scripts.

---

## Resumen para el que tiene apuro

| # | Pregunta | Respuesta | Qué obliga a cambiar |
|---|---|---|---|
| 1 | ¿Los mapas HV entran al post-proceso? | **No. Ni siquiera se guardan.** | La fase 2.b pierde un panel: se muestran 3, no 4 |
| 2 | ¿De qué lado va el λ = 0,02? | **Valor confirmado** en `params.toml`; **el lado sigue abierto** | Nada: ninguna fase lo necesita |
| 3 | ¿Las vistas de TTA se sortean o se enumeran? | **Se sortean**, y no hay `--seed` | La corrida **no es reproducible**; hay que declararlo o fijar semilla |
| 4 | ¿La entrada por tiles sueltos está expuesta? | **Sí**, `.npy` y `.png/.jpg` | **Corrige una de las 4 razones** de la decisión de diseño (la decisión igual se sostiene) |
| 5 | ¿BCB-map y raw class accesibles? | **Sí, pero solo con `--keep_raw`** | La fase 2 **tiene** que pasar `--keep_raw` o los borra |
| 6 | ¿Cómo trata una `.bif` de dos regiones? | **No filtra fondo en esta lámina** → tesela el lienzo entero | El presupuesto de la fase 2 pasa de **~2 min a decenas de minutos** |

Las dos que mueven el plan son la **5** (un flag que, olvidado, borra el insumo de la 2.b) y la
**6** (el presupuesto de GPU estaba mal por un orden de magnitud).

Y hay un séptimo hallazgo que **no era una de las preguntas** y casi cuesta una corrida entera:
el env nuevo **no puede abrir la lámina** sin el openslide parchado del proyecto (§9). Lo cazó
el preflight en segundos.

---

## 1. Los mapas HV se descartan en inferencia

**Se predicen y se tiran antes de escribir nada.** La cabeza de instancia produce **5** canales
(`multi_head_unet.py:88-92`, `get_model(..., out_channels_inst=5)`), y el modelo devuelve
`torch.cat(masks, 1)` (`multi_head_unet.py:343`) → canales 0-4 instancia, 5+ clases.

En inferencia se rebana así (`inference.py:249-250`, y de nuevo en el camino con TTA,
`inference.py:263-264`):

```python
ct   = out_fast[:, 5:].softmax(1)     # clases
inst = out_fast[:, 2:5].softmax(1)    # BCB: 3 canales
```

**Los canales 0 y 1 — los dos mapas HV — no se leen nunca.** El zarr de instancia se crea con
**3** canales (`inference.py:126`), así que tampoco llegan al disco. Y el post-proceso consume
solo esos 3: `work()` (`post_process_utils.py:125-163`) pasa `out_img` (3 canales) y `out_cls` a
`faster_instance_seg`, que usa `out_img[0]` (fondo) y `out_img[1]` (interior) y nada más
(`post_process_utils.py:371-416`).

**Cierra la duda que el paper dejaba abierta** (§2.1 los llama «auxiliar», §2.3 usa solo el BCB,
pero la Fig. 1B los dibuja apuntando al *Instance map*): **manda §2.3**. Los HV son una tarea
auxiliar de entrenamiento y en inferencia son peso muerto.

> **Consecuencia para la fase 2.b:** el panel de mapas HV **no se puede producir** con el
> pipeline tal como viene. Se muestran los tres que sí existen (BCB → raw class → class-map) y
> **se dice por qué falta el cuarto**, que es exactamente lo que el plan mandaba hacer en este
> caso. No se fabrica.

---

## 2. El λ = 0,02: el valor está CONFIRMADO, el lado sigue abierto

`hover_next_inference` **no contiene ninguna loss**: es un repo de inferencia. El único `0.02`
del *código* es la sigma del ruido gaussiano de aumentación (`augmentations.py:187`), que no
tiene relación.

**Pero los pesos traen su configuración de entrenamiento**, y ahí está
(`lizard_convnextv2_tiny/params.toml`):

```toml
inst_channels    = 5        # ← confirma la pregunta 1: 2 HV + 3 BCB
out_channels_cls = 8        # 7 clases de Lizard + fondo
fl_gamma         = 2        # focal loss
loss_lambda      = 0.02     # ← el λ del paper, confirmado como valor
tta              = 16
seed             = 42
```

Así que **el λ = 0,02 del paper es real y viaja con el checkpoint** — eso ya no hay que
suponerlo. **De qué lado va sigue sin contestarse**: `params.toml` da el número, no la fórmula
que lo consume. Eso exige el repo de **entrenamiento** (`hover_next_train`), que **no está
autorizado ni clonado**; la autorización del 17-ago es para *esa lista* (repo de inferencia + los
dos juegos de pesos), no para el tema. **No se especula de qué lado va.**

**Ninguna fase del plan lo necesita**: es un dato de cómo se entrenó, no de cómo se corre.

> Dato aparte del mismo archivo: los pesos se entrenaron con **`tta = 16`**, y el default de
> `main.py` es **4**. El paper reporta sus mejores números de mitosis con TTA alto. Si la fase 2
> corre con 4, se declara; subir a 16 multiplica por 4 el cómputo (ver pregunta 6, que ya lo
> tiene caro).

---

## 3. Las vistas de TTA se SORTEAN, y la corrida no es reproducible

`inference.py:252` hace `for _ in range(nviews)` y en cada vuelta llama
`aug.forward_transform(raw)`. Ahí (`spatial_augmenter.py:39-42`) cada transformación se decide
con una moneda:

```python
self.random_state[key] = {"prob": bool(np.random.binomial(1, self.params[key]["prob"]))}
```

Con `TTA_AUG_PARAMS` (`constants.py:59-67`) sólo `mirror` y `rotate` tienen probabilidad no nula,
las dos **0,75**. O sea:

- Las 4 vistas de `--tta 4` **no son** las 4 canónicas del grupo diédrico: son 4 sorteos.
- Una vista puede salir **identidad** (0,25 × 0,25 = **6,25 %** de las veces).
- **Dos vistas pueden salir idénticas**, y nada lo impide.

**`main.py` no expone `--seed`** y nadie fija `np.random.seed` en el árbol. ⇒ **dos corridas de
la misma lámina con los mismos pesos y `--tta > 0` dan resultados distintos.**

> Contrasta de frente con nuestro pipeline, que es **determinista bit a bit** con la misma
> semilla ([[pipeline-determinista-bit-a-bit]]). Acá la garantía no existe.
> **Qué hacer en la fase 2**: correr con `--tta 4` como el paper y **declarar** que la corrida no
> es reproducible exactamente, o fijar la semilla desde el wrapper. Lo que **no** se puede es
> presentar un número de esta corrida como si fuera repetible sin decirlo.

---

## 4. Los tiles sueltos SÍ están expuestos — y esto corrige una de las cuatro razones

`main.py:48-54` (`get_input_type`) despacha por extensión: `.npy` → `NpyDataset`, y
`.jpg/.png/.jpeg/.bmp` → `ImageDataset` (`inference.py:94-109`). Son caminos de primera clase,
no un hack.

**Esto corrige la razón 1 de la decisión de diseño**, que decía (tomada de
`hovernext_mecanismo.md` §7) que con parches sueltos «hay que tocar código, no configurar».
**Es falso: está expuesto por `--input`.** Lo que sí es cierto es que el camino **WSI** usa el
thumbnail y el stitcher, y ese es otro camino.

**La decisión de correr la lámina entera NO se cae**, porque se apoyaba en cuatro patas y las
otras tres siguen firmes:

- **Borde perimetral** (razón 2): un parche aislado paga borde en todo su contorno, y el propio
  paper evalúa Lizard sobre recortes centrales de 248 de 256 por eso mismo.
- **Pareo por construcción** (razón 4): enmascarar post-hoc deja los tres brazos idénticos salvo
  en la máscara, que es la variable de estudio.
- **Sin motivo de costo** (razón 3): **ojo, esta pata se debilita con el hallazgo 6** — ver abajo.

Se registra la corrección para que el `resultados.md` no repita un argumento que el código
desmiente.

---

## 5. El BCB-map y el raw class están, pero `--keep_raw` es obligatorio

Durante la inferencia se escriben dos zarr (`inference.py:123-148`):

| Archivo | Forma | dtype | Qué es |
|---|---|---|---|
| `<slide>_raw_256_inst.zip` | `(n_tiles, 3, 256, 256)` | `f4` | **BCB-map**: fondo / interior / borde, ya post-softmax (`inference.py:250`, `266`) |
| `<slide>_raw_256_cls.zip` | `(n_tiles, n_clases, 256, 256)` | `u1` | **raw class**: softmax **× 255**, cuantizado a un byte (`inference.py:167`) |

Coincide con lo que decía el paper: el caché guarda el mapa de clases y el BCB **crudos y
cuantizados** antes de post-procesar. El `u1` del class-map es literalmente esa cuantización.

**La trampa:** `main.py:121-126` los **borra** apenas termina el post-proceso, salvo que se pase
**`--keep_raw`**:

```python
if not params["keep_raw"]:
    os.remove(params["model_out_p"] + "_inst.zip")
    os.remove(params["model_out_p"] + "_cls.zip")
```

> **La fase 2 corre con `--keep_raw` sí o sí.** Sin ese flag la corrida termina «bien», el
> `pinst_pp.zip` queda, y el insumo de la 2.b se fue a la basura — habría que volver a pagar la
> GPU. (Alternativa: `--only_inference`, `main.py:104-112`, que corta después de inferir y
> conserva los crudos, pero entonces no hay `class-map` final que mostrar.)

**El resto de la cadena, para armar la figura:**

- **watershed**: `post_process_utils.py:405-408`. Las semillas son los píxeles de *interior* sobre
  umbral (`fg_pred > seed_thresh`) y la superficie es `1 − interior`; la máscara viene del canal
  de fondo. Los dos ingredientes salen ya hechos del BCB, que es la tesis del paper.
- **la clase por instancia**: `make_ct` (`post_process_utils.py:503-520`). **Precisión que importa
  para el caption**: no es un voto de mayoría de etiquetas, es
  `np.sum(probabilidades, axis=0).argmax()` — la **suma de probabilidades** sobre los píxeles de
  la instancia, y después argmax. Equivale a votar por probabilidad media, no por moda.
- **Salidas finales** (`post_process.py:89-107`): `pinst_pp.zip` (mapa de instancias),
  `class_inst.json` (instancia → clase), TSVs por clase, y geojson para QuPath **solo con
  `--save_polygon`**. Ese geojson es interesante de por sí: es el formato en el que el patólogo
  ya trabaja.

---

## 6. La 129741 no tiene `thumbnail`, así que el filtro de fondo nunca corre

El filtro de fondo está guardado por una condición (`data_utils.py:297`):

```python
if remove_background and "thumbnail" in self.s.associated_images:
```

Y la lámina **no tiene** esa imagen asociada. Verificado con openslide sobre el `.bif` real:

```
associated_images: ['macro']          ← no hay 'thumbnail'
dims level0: (39669, 80640)   mpp 0.465   objective-power 20   vendor ventana
region[0]: x=0 y=0     w=35840 h=30720
region[1]: x=0 y=49920 w=34560 h=30720
openslide.bounds-x / bounds-y : ausentes
```

⇒ **`remove_background=True` es un no-op en esta lámina** y la grilla cubre el **lienzo entero**,
fondo incluido. La pregunta original («¿acota por bounding box o corre entera y filtra después?»)
queda contestada por abajo: **el pipeline ni siquiera distingue las dos regiones**, porque no
llega a mirar el tejido.

**Lo que eso cuesta**, calculado con su propia fórmula de grilla
(`data_utils.py:_build_reference_grid`, `tile_size=256`, `overlap=0.96875`):

| Juego de pesos | Magnificación de crop | Grilla | Tiles |
|---|---|---|---|
| Lizard-Mitosis | 20× (nativo de la lámina) | 158 × 324 | **51.192** |
| PanNuke | 40× (⇒ 0,25 µm/px interpolados) | 318 × 649 | **206.382** |

| Área | mm² | % del lienzo |
|---|---|---|
| Lienzo entero | 691,7 | 100 % |
| Las dos regiones declaradas | 467,6 | 68 % |
| **Región anotada** (2496 parches) | **35,4** | **5 %** |

> **El «~2 min por lámina» del plan no aplica a esta lámina.** Ese número salía de láminas
> chicas con filtro de fondo activo. Acá, a los 1,78 s/mm² del paper (HNLarge, 4 TTA, 0,5 mpp),
> el lienzo entero da **~21 min** de cómputo para Lizard — y PanNuke tiene **4× los tiles**.
> HNTiny es más rápido que HNLarge, así que tómese como orden de magnitud, no como reloj.
> **Consecuencia operativa: el `.slurm` de la fase 2 pide horas, no minutos.**

**Lo que NO cambia:** la decisión de correr la lámina entera y enmascarar post-hoc. Acotarla
exigiría tocar el código de un repo que es read-only, o pasar por el camino de tiles sueltos que
paga borde. Lo que cambia es el **presupuesto**, y que hay que decirlo en el pre-vuelo.

**Dos cosas más que salieron de mirar esto:**

- **`bounds-x/bounds-y` no existen en este `.bif`, y no es un problema**: `get_openslide_info`
  (`post_process_utils.py:685-692`) los toma con `try/except KeyError` y los deja en 0.
- **Disco**: con `--keep_raw`, el `_inst.zip` de Lizard es del orden de 51.192 × 3 × 256² × 4 B
  ≈ 40 GB **sin comprimir**, y el `_cls.zip` ≈ 26 GB. Van con Blosc/LZ4 y los tiles de fondo
  comprimen muchísimo, así que el número real será una fracción — pero conviene mirar el disco
  antes y después (hay 2,5 TB libres, así que no bloquea).

---

## 7. Extra no pedido: los umbrales de post-proceso, y `--metric` no es libre

Salió al mirar los pesos y afecta directo a la fase 3, así que se registra.

`post_process_main` llama `get_pp_params(params, **True**)` (`post_process.py:47`), o sea
**`mit_eval=True` está cableado**. Para los pesos de Lizard eso hace (`post_process_utils.py:574-584`):

1. lee los umbrales de las 7 clases de `liz_test_param_dict.json`;
2. y **pisa los de la ÚLTIMA clase** — índice `-1`, que es **mitosis** — con los de
   `mit_test_param_dict.json`.

O sea que **la clase que nos importa tiene umbrales propios, optimizados para mitosis**. Es una
decisión de diseño del repo a favor nuestro y conviene decirla en el `resultados.md`.

**El gotcha:** la clave que busca es `best_fg_{metric}` con `metric` = `--metric`, que
`main.py:168` restringe a `{mpq, f1, pannuke}`. Pero los JSON de Lizard solo traen
**`best_fg_lizard`** y **`best_fg_f1`**. ⇒ con los pesos de Lizard, **`--metric mpq` revienta con
`KeyError`** y `--metric f1` (el default) es **la única opción usable**. `lizard` no se puede
pedir porque no está en la lista blanca.

Con `--metric f1`, los umbrales efectivos de Lizard-Mitosis quedan:

| | neu | epi | lym | pla | eos | con | **mitosis** |
|---|---|---|---|---|---|---|---|
| `fg` | 0,5 | 0,6 | 0,5 | 0,3 | 0,5 | 0,3 | **0,5** |
| `seed` | 0,2 | 0,5 | 0,6 | 0,1 | 0,7 | 0,3 | **0,1** |

(En este checkpoint el override de mitosis coincide con el valor de Lizard para `f1`, así que es
un no-op **acá**; con `--metric lizard` sí diferiría. Se anota para que nadie lo lea como que el
override no existe.)

**Tamaño mínimo de objeto**: `MIN_THRESHS_LIZARD` (`constants.py:4`) pone **15 px** para mitosis,
el más permisivo de las 7 clases, y `MAX_THRESHS` 5000. Las marcas del patólogo son cuadrados de
~36 px de lado (~1300 px²), así que el filtro de tamaño no las excluye por construcción.

---

## 8. Inventario de lo instalado (fase 0, puntos 1-3)

**Repo**: `clam_testing2/hover_next_reference/`, HEAD `29134a3` (26-oct-2025), 508 KB.

**Pesos** — bajados de Zenodo `10635618` el 17-ago, a
`clam_testing2/hover_next_reference/<id>/` (es donde el código los busca: `main.py:74-77` arma
`data_dirs` como `dirname(main.py)/<cp>`). Los `.zip` quedan en `_zips/`.

| Juego | id | sha256 del zip | Tamaño |
|---|---|---|---|
| **Lizard-Mitosis** | `lizard_convnextv2_tiny` | `cc7c5e23873cbe296f6d41184fc4fc7bdf3fbbb9eae6647962e5a434917b40cd` | 128 MB |
| PanNuke fold 1 | `pannuke_convnextv2_tiny_1` | `fc92a7807e21ad73f18dc7b41c9c13674a53383cb383561e9b2481f74a2578fa` | 128 MB |
| PanNuke fold 2 | `pannuke_convnextv2_tiny_2` | `e8db31e58d5f36eaa637e786b4d6ca099848ee3f675c05ec4fe2e24eeec5b36a` | 128 MB |
| PanNuke fold 3 | `pannuke_convnextv2_tiny_3` | `1b9804610ad07df0fdb4ba8992b381ea317c7d06070efbcde9c2e8c076e447e3` | 128 MB |

**Por qué `tiny` y no `large`/`base`** (Lizard viene en los tres): lo decidió nuestro propio
estudio antes de esta sesión — `hovernext_estudio.md` §3.b rec. 5, «con HNTiny y con TTA: es el
mejor en mitosis y el que más gana con TTA», y §3.1 lo confirma en las dos agregaciones. No es
una elección nueva.

**Por qué los tres folds de PanNuke**: `--cp` es una **lista separada por comas** que el código
promedia como ensemble (`main.py:76`, `inference.py:245-248`), y así es como el paper reporta
PanNuke. Son el mismo «juego de pesos» del plan, no un juego extra.

**Diferencias entre los dos juegos** (de sus `params.toml`):

| | Lizard-Mitosis | PanNuke |
|---|---|---|
| `out_channels_cls` | 8 (7 clases + fondo) | 6 (5 clases + fondo) |
| `inst_channels` | 5 | 5 |
| `loss_lambda` | **0,02** | **0,1** |
| clase de mitosis | **sí** (la 7ª) | **no** |
| `--metric` usable | **solo `f1`** (no hay `best_fg_mpq`) | `f1`, `pannuke` |
| magnificación de crop | 20× (`inference.py:111`) | 40× ⇒ **0,25 µm/px interpolados** |

> El λ **no es el mismo en los dos**: 0,02 en Lizard y 0,1 en PanNuke. La pregunta 2 hablaba del
> 0,02 del paper, y ese es el de Lizard.

**Entorno**: `conda create -p /media/administrador/Storage1/sdonoso/clam_testing2/envs/hovernext`
(prefix, **no** `-n`, para respetar containment), python 3.11.5 + openslide, torch 2.1.1 /
torchvision 0.16.1 cu118 como pide el README. Se instalaron **los imports reales** del camino de
inferencia (17 paquetes derivados de `grep` sobre `main.py` + `src/*.py`), no el `requirements.txt`
entero: ese trae `staintools`, `spams-bin`, `itk`, `jupyterlab`, `mahotas` desde git y
`libpysal`, que este camino **nunca importa**. Se invoca por binario absoluto (workaround B).

---

## 9. El env nuevo NO podía abrir la lámina: hace falta el openslide PARCHADO

Lo cazó el **preflight**, en segundos, antes de pedir GPU. Es el mejor argumento a favor del
workaround G que dio este sprint.

**Síntoma**: con el env recién creado,

```
OpenSlideError('Bad direction attribute "LEFT"')
```

**Causa**: los `.bif` Ventana de la cohorte privada traen `direction="LEFT"` en su XML, y el
OpenSlide **oficial** (hasta 4.0.0 inclusive) solo entiende `RIGHT` y `UP`. **No es un problema
de versión**: bajar de libopenslide 4.0.1 a 4.0.0 **no lo arregla** (se probó). Lo que hace falta
es el **parche al código fuente**.

**Ya estaba resuelto en el proyecto y el repo no lo tenía a mano**:
`clam_environ/openslide_solution.md` documenta el parche (agregar `DIRECTION_LEFT` a
`src/openslide-vendor-ventana.c` y compilar). `clam_latest` corre esa build parchada — por eso
todas nuestras sesiones abren las láminas privadas sin enterarse de que hay un parche debajo:

| env | openslide-python | libopenslide | ¿abre la 129741? |
|---|---|---|---|
| `clam_latest` | 1.4.2 | 4.0.0 **parchada** (1,2 MB) | **sí** |
| `hovernext` recién creado | 1.3.1 | 4.0.1 de conda-forge | no |
| `hovernext` con `openslide=4.0.0` de conda | 1.3.1 | 4.0.0 stock (287 KB) | **no** |
| `hovernext` final | 1.3.1 | 4.0.0 **parchada** | **sí** |

**Fix aplicado**: se copió la biblioteca parchada al env nuevo, guardando la de conda al lado por
si hay que volver:

```bash
ENVP=/media/administrador/Storage1/sdonoso/clam_testing2/envs/hovernext
cp -n $ENVP/lib/libopenslide.so.1.0.0 $ENVP/lib/libopenslide.so.1.0.0.conda_stock
cp /home/sdonoso/miniconda3/envs/clam_latest/lib/libopenslide.so.1.0.0 $ENVP/lib/
```

`ldd` resuelve todas sus dependencias dentro del env nuevo, así que no arrastra nada de
`clam_latest` en tiempo de ejecución.

> **Regla que se lleva para adelante: cualquier env nuevo que tenga que leer un `.bif` privado
> necesita la libopenslide parchada.** El tamaño delata cuál es: **1,2 MB la parchada, 287 KB la
> stock**. Y hay que exportar `LD_LIBRARY_PATH=$ENVP/lib`, porque al invocar por binario absoluto
> (workaround B) `openslide-python` no encuentra la `.so` sola.

---

## Qué no se afirma

- **No se corrió nada todavía.** Todo lo de arriba es lectura de código y una consulta de
  openslide sobre la lámina. Los tiempos son estimaciones derivadas del paper, no mediciones.
- **No se auditó `post_process_utils.py` entero** (706 líneas): se siguió la cadena que va del
  zarr crudo al `class_inst.json`. El stitching entre tiles solapados y el `remove_obj_cls` se
  leyeron por encima.
- **El λ queda abierto** y no se especula de qué lado va.
- **La cuenta de tiles es analítica**, con la fórmula de la grilla; no se instanció el
  `WholeSlideDataset` (habría sido import cruzado). El número puede moverse en ±1 fila/columna
  por los márgenes, no en su orden de magnitud.
