# Resultado — el modelo SÍ mira donde marcó el patólogo, y aun así responde mal

> 1-ago-2026. Pre-registro: [`prereg.md`](prereg.md), escrito y commiteado (`d52676f`) antes
> de correr. Script: [`scripts/atencion_vs_anotaciones.py`](../../../scripts/atencion_vs_anotaciones.py).
> Todo CPU, post-hoc, sin GPU. Lámina **129741**, 4799 parches, 163 anotados (3.4 %).
>
> **Veredicto: gana H_alternativa.** Los parches marcados rankean muy por encima del azar.
> La intuición del patólogo de que «esos parches quizá no reciben atención suficiente»
> **no se sostiene** en esta lámina.

## 1. El número

AUC de ranking = probabilidad de que un parche anotado reciba más atención que uno no
anotado. Nulo = 0.5. Cabeza de la clase verdadera (`score_3`), media ± sd sobre los 4
checkpoints **primarios** (los que nunca vieron la lámina):

| Grupo anotado | n parches | AUC (lámina) | AUC (solo región anotada) |
|---|---:|---:|---:|
| **Mitosis** | 28 | **0.890 ± 0.039** | **0.903 ± 0.032** |
| **Núcleos alto grado** | 13 | 0.828 ± 0.055 | 0.842 ± 0.045 |
| Tumor | 48 | 0.826 ± 0.039 | 0.843 ± 0.033 |
| necrosis | 18 | 0.748 ± 0.105 | — |
| Stroma | 12 | 0.537 ± 0.105 | — |
| Immune cells | 23 | 0.322 ± 0.026 | — |
| Tejido adiposo | 27 | 0.154 ± 0.106 | 0.162 ± 0.100 |

> **La columna `n parches` cuenta PARCHES, no marcas del patólogo, y los dos números conviven.**
> El patólogo dibujó **26 polígonos** de mitosis y **14** de núcleos de alto grado
> ([[anotaciones-patologo-qupath]]); la tabla dice **28** y **13** porque cuenta parches que tocan
> al menos un polígono de ese grupo. Verificado sobre `../anotaciones_patologo/parches_anotados_129741.csv`
> (163 filas, columna `clases` multi-etiqueta con `|`): mitosis = 26 + 1 `Mitosis|Nucleos alto grado`
> + 1 `Mitosis|Tumor` = 28; núcleos alto grado = 12 + ese mismo compartido = 13. Los siete grupos
> reproducen exacto con esa regla.

### 1.a La descomposición del +2, ya calculada (6-ago)

El 1-ago se dejó anotado que la descomposición «no se calculó y no hace falta». Se calculó el
**6-ago** porque Ernesto volvió a tropezar con los dos números, y resulta que **no es un +2
simple: son dos efectos grandes que casi se cancelan**. Sobre la geometría real (geojson +
`coords` del h5, offset `dx = 3829` ya adoptado) y con la regla de mapeo de
[`scripts/alinear_anotaciones_qupath.py:252`](../../../scripts/alinear_anotaciones_qupath.py#L252)
— un parche cuenta si su cuadrado de 256 px se solapa con la **caja envolvente** del polígono:

| | |
|---|---:|
| polígonos de mitosis | 26 |
| pares (polígono, parche) | 36 |
| **parches distintos** | **28** |
| polígonos que caen enteros en un parche | 16 |
| polígonos repartidos entre dos parches | 10 |
| parches con una sola mitosis | 21 |
| parches con dos | 6 |
| parches con tres | 1 |

O sea **26 + 10 − 8 = 28**: diez marcas cruzan el borde entre dos parches y suman uno cada una;
siete parches contienen más de una marca y restan ocho en total (6×1 + 1×2). Que el neto dé +2 es
una coincidencia aritmética de esta lámina, **no** una regla general — con marcas más dispersas el
neto sería mucho mayor.

La razón de fondo es de escala, y conviene tenerla a mano porque conecta con el §3: **una marca de
mitosis mide 36 px de lado** (las hay de 54; a 0,465 µm/px son 17 y 25 µm) contra los **256 px del
parche**. Una mitosis ocupa entre el **2 % y el 4 % del área del parche**, y con ese tamaño la
probabilidad de caer sobre un borde no es despreciable: 10 de 26 lo hacen.

Script de la cuenta: `scratchpad/desc_26_28.py` de la sesión del 6-ago (efímero; el cálculo se
reproduce con el geojson, el h5 y las tres líneas de la regla de arriba).

### 1.b Cuánta precisión tiene cada barra: el n manda

Los siete grupos comparten estadístico y nulo, pero **no comparten precisión**: `n` va de 12 a 48
parches. El intervalo de confianza al 95 % del AUC por la fórmula de **Hanley y McNeil** (1982),
con n₋ = 4799 − n₊, calculado el 6-ago sobre `con_region/auc_por_checkpoint.csv` (universo
`lamina`, rol `primario`, cabeza de la clase verdadera):

| Grupo | n | AUC | ± sd entre ckpt | IC 95 % (Hanley-McNeil) | ancho del IC |
|---|---:|---:|---:|---:|---:|
| Mitosis | 28 | 0.890 | 0.039 | 0.811 – 0.970 | 0.16 |
| Núcleos alto grado | 13 | 0.828 | 0.055 | 0.690 – 0.966 | 0.28 |
| Tumor | 48 | 0.826 | 0.039 | 0.754 – 0.899 | 0.14 |
| necrosis | 18 | 0.748 | 0.105 | 0.617 – 0.880 | 0.26 |
| Stroma | 12 | 0.537 | 0.106 | 0.370 – 0.704 | 0.33 |
| Immune cells | 23 | 0.322 | 0.026 | 0.228 – 0.417 | 0.19 |
| Tejido adiposo | 27 | 0.154 | 0.106 | 0.104 – 0.205 | 0.10 |

**Son dos incertidumbres distintas y no hay que mezclarlas.** La `sd` mide qué pasa si cambio de
**modelo** (dispersión entre los 4 checkpoints primarios sobre las mismas marcas). El IC mide qué
pasa si el patólogo hubiera marcado **otras** mitosis (muestreo de parches, con el modelo fijo). La
segunda es la grande: en mitosis, ±0.039 contra ±0.080.

Consecuencias que sí cambian cómo se lee la tabla del §1:

- **Mitosis aguanta**: su IC no toca 0.5 ni de lejos, y además sobrevive al nulo espacial (§2.a).
- **Estroma «en el azar» no es un dato, es una ausencia de dato**: con n = 12 el IC va de 0.37 a
  0.70, así que la lámina no puede distinguir estroma evitado de estroma atendido. Decir «el
  estroma queda justo en el azar, que es donde uno esperaría» **sobre-lee** el número.
- **Núcleos de alto grado tiene el segundo IC más ancho** (0.28), lo que es una segunda razón,
  independiente del p por traslación del §5, para no presentarlo como resultado.
- **Tejido adiposo es el número más preciso de los siete** (IC 0.10) pese a no ser el de mayor n:
  el IC se angosta cerca de los extremos, no solo con n grande.

El percentil mediano de los 28 parches de mitosis es **91** sobre 100. Y el orden completo
no es ruido: la atención sube monótonamente desde grasa (0.15) y linfocitos (0.32), pasa por
estroma en el azar (0.54), y llega a tumor (0.83) y mitosis (0.89). **Mitosis es el grupo
mejor rankeado de los siete**, por encima de Tumor.

## 2. Lo que lo vuelve un resultado y no una coincidencia

**a) Sobrevive al nulo espacial.** Permutar al azar qué parches son «anotados» da p = 0.0005
(el piso de 2000 permutaciones) en absolutamente todo, incluido lo que no debería —
exactamente el falso positivo que el pre-registro anticipó y por el que se construyó otro
nulo. Contra el nulo honesto, que **traslada rígidamente** la máscara anotada sobre la
lámina conservando su forma y dispersión, mitosis da p = **0.0021–0.0023 en los 4
checkpoints primarios**. Ese valor es el piso 1/(1+N): **ninguna** de las ~440 traslaciones
válidas alcanzó el AUC observado, aunque las traslaciones ya parten de un AUC nulo alto
(0.67–0.75, porque mover la mancha dentro del tumor sigue cayendo en zona de atención alta).

**b) No es un efecto de región.** La lámina es un Ventana `.bif` con **dos regiones de
escaneo** (`region[1].y = 49920`) y el pipeline extrajo parches de las dos: 2303 arriba,
2496 abajo. Los 163 parches anotados caen **todos** en la de abajo. Si esa región recibiera
de por sí más atención, el AUC mediría la región y no las marcas. Medido: AUC(región anotada
vs la otra) = **0.462–0.478**, o sea que la región anotada recibe *algo menos* de atención.
Al repetir todo confinado a esa región, el efecto **sube** (0.890 → 0.903). Descartado.
(Las dos regiones son tejido distinto, no un duplicado: coseno medio entre parches
geométricamente «gemelos» 0.708 contra 0.503 entre parches al azar.)

La corrida confinada (`con_region/`, universo `region_anotada`, N = 2496) también rehace el
nulo espacial dentro de esa región, donde caben **~1300 traslaciones válidas** en vez de
~440: mitosis vuelve a dar el piso 1/(1+N), p = **0.00075–0.00078** en las 7 combinaciones
checkpoint × cabeza de los 4 primarios. Grado nuclear queda igual de mixto que en la lámina
completa (p = 0.012–0.093, por debajo de 0.05 en 4 de 7), así que confinar no lo rescata.
Los AUC del universo `lamina` de esa corrida son idénticos dígito a dígito a los de este
documento; lo único que cambia entre las dos corridas son los p, por remuestreo.

**c) El sesgo de la anotación parcial juega en contra, no a favor.** Las marcas son positivos
parciales: mitosis no marcadas quedan en el conjunto «no anotado» y **acercan el AUC a 0.5**.
Un 0.89 es creíble justamente porque el sesgo lo empuja hacia abajo.

**d) No es memorización.** El contraste vive dentro de una misma corrida de Sebastián, que
tiene la lámina en `val` en los folds 0 y 2 y en `train` en 1, 3 y 4:

| Rol | 129741 | AUC mitosis (lámina) |
|---|---|---:|
| Primario (4 ckpt) | no vista | 0.890 ± 0.039 |
| Control interno (3 ckpt, misma corrida) | vista en train | 0.946 ± 0.004 |
| Corroboración (5 folds Tier 0, 3 clases) | vista en train | 0.928 ± 0.029 |

Haber visto la lámina suma ~0.056 de AUC. El efecto **no** viene de ahí: 0.890 ya está lejos
de 0.5 sin haberla visto nunca.

## 3. El hallazgo que reordena el sprint: mira bien y responde mal

**3 de los 4 checkpoints primarios clasifican mal la lámina.** La verdadera es `score_3`
(tasa mitótica alta, coherente con 26 mitosis marcadas) y predicen `score_2`:

| Checkpoint | predicción | p(score_2) | p(score_3) | AUC mitosis |
|---|---|---:|---:|---:|
| `seba_privado_s0` | **score_2** ✗ | 0.645 | 0.351 | 0.840 |
| `seba_combined_s0` | score_3 ✓ | 0.224 | 0.525 | 0.878 |
| `seba_5fold_f0` | **score_2** ✗ | 0.712 | 0.256 | 0.926 |
| `seba_5fold_f2` | **score_2** ✗ | 0.524 | 0.401 | 0.917 |

Los 8 checkpoints que **sí** vieron la lámina la aciertan con confianza (hasta p = 0.93). O
sea: sobre una lámina no vista el modelo **subestima** la tasa mitótica, y lo hace mientras
su atención está puesta exactamente sobre las mitosis. `seba_5fold_f0` es el caso extremo:
el mejor AUC de atención del grupo primario (0.926) y la predicción más equivocada (0.712 a
`score_2`).

**Esa disociación es el resultado.** El problema no está en *elegir* los parches. Está en lo
que queda del parche una vez comprimido, y en cómo se convierte un conjunto de parches
correctamente seleccionados en un puntaje.

## 4. Un subproducto: las cabezas por clase de CLAM_MB no son específicas por clase

CLAM_MB tiene una cabeza de atención por clase. Acá rankean casi igual entre sí: Spearman
medio entre pares de cabezas **0.717 a 0.941** según el checkpoint, y la cabeza de
`no_identificado` rankea las mitosis tan alto (AUC 0.756–0.916) como la de `score_3`. El
modelo tiene una noción única de «tejido interesante», no un mapa de evidencia por clase.

## 5. Qué mueve esto en el mapa de las cuatro familias

Contra [`../tareas_geometricas/README.md`](../tareas_geometricas/README.md) §3:

- **La familia A pierde su motivación principal, no toda.** Su primer argumento era el del
  patólogo, que los parches de mitosis no reciben atención suficiente: **refutado acá**. Su
  segundo argumento sigue **intacto y sin tocar por esta medición**: el recuento de Nottingham
  es un **máximo local** sobre ~141 parches contiguos (§2.b), no un promedio ponderado, y eso
  es una diferencia de operador que este experimento no evalúa. Si A se pre-registra, tiene
  que apoyarse en §2.b, no en la frase del patólogo.
- **Las familias B y C se fortalecen**, que es hacia donde apunta la disociación del §3: si
  el modelo mira el parche correcto y aun así subestima, lo que falla es la representación —
  campo de visión (B, §2.c y §2.d: la cohorte está a 20× y la mitosis se cuenta a 40×) o
  unidad de representación (C, del parche al núcleo).
- **Para grado nuclear el resultado es más débil y no hay que estirarlo.** Núcleos de alto
  grado da 0.828, pero contra el nulo por traslación solo **1 de 4** checkpoints primarios
  baja de p = 0.05 (p = 0.035, 0.060, 0.103, 0.139). Con 13 parches, lo honesto es decir que
  no se distingue de cualquier mancha compacta de ese tamaño puesta en el tejido.

## 6. Lo que este resultado NO dice

- **Una lámina, un anotador, un caso.** Describe, no establece. Se pre-registró así.
- **No dice que la atención de CLAM esté bien en general**, solo que en esta lámina cae sobre
  las marcas. Y menos aún que esté bien en las láminas que el modelo acierta: el hecho de que
  el grupo primario mayormente **falle** la clasificación es lo que hace informativo el
  resultado, pero también significa que no medimos el caso «modelo correcto».
- **No convierte lo no marcado en negativo.** Un parche sin marca con atención alta no es un
  error del modelo; puede ser tejido tumoral que el patólogo no marcó.
- **No valida los nombres de tejido de OBJ-A** ni cierra el sign-off de patólogo pendiente.
- Las clases de contraste (Tumor, Stroma, …) **no son control negativo**: son regiones
  grandes marcadas con otro criterio. Que la grasa dé 0.15 muestra que la atención tiene
  estructura, no que el método esté validado.

## 7. Artefactos

| Archivo | Qué es |
|---|---|
| `auc_por_checkpoint.csv` | AUC, percentiles y p-valores por checkpoint × cabeza × grupo |
| `percentiles_por_parche.csv` | atención y percentil de cada parche anotado |
| `figura_atencion_vs_anotaciones.png` | mapa de atención y mapa de anotaciones, lado a lado |
| `figura_mitosis_sobre_atencion.png` | los 28 parches de mitosis sobre el mapa de atención |
| `meta.json`, `run.log` | provenance de la corrida |
| `con_region/` | corrida definitiva con los dos universos y 2000 traslaciones cada uno |

> Nota de lectura de las figuras: se ve el tejido **dos veces** porque el lienzo de openslide
> contiene las dos regiones de escaneo del `.bif` (§2.b). Las anotaciones están todas en la
> de abajo. No es un error de la figura.
