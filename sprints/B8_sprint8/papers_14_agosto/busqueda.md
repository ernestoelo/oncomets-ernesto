# Cómo se eligió el paper del 14 de agosto, y contra qué se lo comparó

> Encargo de Ernesto del **13-ago-2026**, para la reunión del **viernes 14-ago**. Buscar un
> paper que ocupe la casilla del **segundo modelo** del pipeline que propuso Sebastián: el
> especialista que corre sobre los parches de mayor atención de CLAM. Las dos condiciones que
> puso Ernesto son **que sea integrable** y **que aumente métricas**.
>
> **➜ El entregable de la reunión es [`hoja_jaroensri.md`](hoja_jaroensri.md)**, una página que
> se lee sin abrir nada más. El estudio a fondo del ganador está en
> [`jaroensri_estudio.md`](jaroensri_estudio.md). **Este documento es la fuente auditable de la
> elección**: qué se buscó, contra qué rubric se puntuó, quiénes compitieron y por qué perdieron.
> No se lee en la reunión.
>
> **Ganador: Jaroensri et al., npj Breast Cancer 8:113 (2022)**, DOI
> `10.1038/s41523-022-00478-y`. Bajado, leído entero, y con sus números volcados en
> [`notas_extraccion_jaroensri.md`](notas_extraccion_jaroensri.md).
>
> **Qué NO es.** No es un pre-registro y no propone implementar nada. Regla 9: si alguna rama
> avanza, va con hipótesis pre-registrada, métrica y dirección esperada, y `reviewer` antes de
> tocar código.

---

## 1. Qué se buscaba, exactamente

El pipeline en el que el paper tiene que encajar es el que propuso Sebastián el 12-ago
([[tareas-geometricas-mitosis-grado-nuclear]]):

```
WSI
 └─> parches 256 px  ->  CONCH 512-dim  ->  CLAM_MB  ->  atención por parche
                                                            │
                                                            ├─> etiqueta de lámina (lo de hoy)
                                                            │
                                                            └─> top-k parches de atención más alta
                                                                     │
                                                                     └─> SEGUNDO MODELO
                                                                         (mitosis / pleomorfismo /
                                                                          grado nuclear)
```

**La casilla que se busca llenar es la de abajo, no otra vez la de arriba.** Un MIL nuevo no
sirve: ya hay cuatro ejes de arquitectura cerrados sin mejora (Hallazgos 11 a 14). Lo que falta
es el especialista que mira el parche.

Y hay una medición propia que le da piso a la primera etapa, del 1-ago:
sobre la lámina 129741, los parches con mitosis marcada rankean con **AUC de atención
0,890 ± 0,039** en los cuatro checkpoints que nunca vieron esa lámina, con percentil mediano 91.
**CLAM ya elige bien los parches.** Lo que falla es lo que viene después: **3 de esos 4
checkpoints clasifican mal la lámina mientras su atención está puesta exactamente sobre las
mitosis** ([`../atencion_vs_patologo/resultados.md`](../atencion_vs_patologo/resultados.md) §3).

Esa disociación es el argumento clínico de la búsqueda, y no hay que inventarlo: el problema no
está en elegir dónde mirar, está en qué se hace con el parche una vez elegido.

## 2. El rubric, y por qué cada criterio

Cinco criterios, en orden de peso. Los fijó el encargo antes de mirar candidatos, que es lo que
evita elegir por corazonada y justificar después.

| # | Criterio | Por qué está, y qué lo hace fallar |
|---|---|---|
| **1** | **Opera sobre parches, no sobre la lámina** | **Eliminatorio.** Si el método necesita la WSI entera, no puede ser segunda etapa de nada |
| **2** | **Supervisión compatible con la que tenemos** | Vale si trae **pesos preentrenados** o si se entrena con **etiqueta de lámina** (la del informe CAP), que es lo único que tenemos a escala. Si exige anotación de objeto por parche se ficha pero no se recomienda: nuestras únicas marcas son **61 polígonos de una lámina** y son **positivos parciales** ([[anotaciones-patologo-qupath]]) |
| **3** | **Reporta ganancia contra un baseline comparable** | Es el pedido explícito de Ernesto. Se anota contra qué baseline, con cuántas láminas de test, y si la ganancia sobrevive al tamaño de esa muestra |
| **4** | **Declara la escala física en µm/px** | Nuestro privado está **entero** a 0,4650 µm/px con `objective-power = 20`, verificado sobre las 490 láminas sin una excepción ([`../anotaciones_patologo/regiones_escaneo/resultados.md`](../anotaciones_patologo/regiones_escaneo/resultados.md) §3). Un método entrenado a 0,25 exige ampliar, y eso es un riesgo que se anota, no un detalle |
| **5** | **Acceso abierto, con código o pesos públicos** | Preferido, **no eliminatorio** |

## 3. Cómo se buscó

Dos rondas, en dos sesiones del mismo día.

**Ronda 1, sesión del mediodía del 13-ago: la lista corta.** Cuatro búsquedas web, organizadas
por los dos ejes del encargo del 31-jul, mitosis y grado nuclear, cruzados con la forma del
pipeline:

1. Grado histológico de mama con aprendizaje profundo **a nivel de parche**, apuntando a los
   tres componentes de Nottingham.
2. Puntaje **cuantitativo** de pleomorfismo nuclear, buscando específicamente si alguien mide de
   forma **relativa al vecindario**, que es lo que describió el patólogo y lo que ninguna de las
   16 features de NPKC-MIL hace.
3. Detección de mitosis, estado del arte 2025, con foco en el ecosistema **MIDOG**.
4. Métodos de **dos etapas** para mitosis, del tipo propuestas y después clasificación.

**Ronda 2, sesión de la tarde: verificación.** El ganador se verificó **abriendo el PDF y el
Supplementary enteros**. Los otros tres se verificaron **por búsqueda web, no por PDF**, y así
quedan marcados en la tabla del §4 y en las fichas del §5. Es una diferencia que importa: del
elegido citamos números del texto del artículo, de los demás citamos lo que dice su resumen o su
página.

> **Lo que este documento no puede ofrecer, y conviene decirlo: las cadenas de búsqueda
> literales no quedaron registradas.** Lo que sí queda auditable es lo que decide la elección:
> cada candidato con su identificador permanente (DOI o arXiv), el estado de verificación de
> cada uno, y el puntaje contra los cinco criterios. Si alguien quiere rehacer la búsqueda, los
> cuatro ejes de arriba son el punto de partida, y **la sesión que la repita debería anotar las
> consultas literales**, que es una mejora barata de proceso.

## 4. La tabla del rubric, puntuada sobre los cuatro candidatos

| Candidato | 1 · parche | 2 · supervisión | 3 · ganancia | 4 · µm/px | 5 · abierto | Verificado |
|---|---|---|---|---|---|---|
| **Jaroensri 2022** (elegido) | **sí**, los tres modelos son de parche | parcial: **pesos no**, pero la etiqueta de la etapa 1 es **puntaje por región**, no por objeto | **sí**: supera el acuerdo entre patólogos en **3 de 3** componentes, con TCGA como test | **sí**, 0,25 declarado, y **excluye explícitamente el 20×** | artículo sí, código de la etapa 2 sí, **pesos no** | **PDF completo + Supplementary** |
| **MIDOG 2025 overview**, arXiv `2606.07368` | sí | pesos de los equipos participantes | F1 **0,740** de detección y balanced accuracy **0,908** en atípicas, sobre **365 casos y 12 tipos tumorales** | 0,23 a 0,26 en MIDOG | sí | búsqueda web |
| **YOLO11x + ConvNeXt**, dos etapas, arXiv `2509.02627` | sí | **anotación de objeto** | F1 **0,882** contra 0,847 de una etapa (+0,035); precisión 0,762 → 0,839; **0,7587** en el test preliminar de MIDOG 2025 | idem MIDOG | sí, código en `github.com/xxiao0304/MIDOG-2025-Track-1-of-SZTU` | búsqueda web |
| **Diagnostics 14(18):2045 (2024)**, PMC11431806 | **núcleo**, y exige segmentar primero con CellProfiler | segmentación previa obligatoria | acc **0,97** sobre **600 núcleos elegidos a mano**, 200 por clase | **no la declara** | artículo sí, **datos y código no** | búsqueda web |

**Veredicto: gana Jaroensri, y gana por el criterio 3 leído en su forma más fuerte.** Es el único
que reporta ganancia contra un baseline que a nosotros nos sirve de referencia directa, que es el
**patólogo humano**, y lo hace en los tres componentes a la vez. Los otros tres, ordenados por lo
que los frena:

- **MIDOG 2025** no pierde el rubric, pierde la pregunta: es un **overview de challenge**, no un
  método. Sirve de marco y para elegir detector, y trae un dato que vale solo (§7), pero si
  Sebastián espera un paper de método, no es este.
- **YOLO11x + ConvNeXt** cae por el criterio 2. Su forma de dos etapas calza con la nuestra, pero
  se entrena con anotación de objeto, que es exactamente lo que no tenemos.
- **Diagnostics 14(18):2045** cae por el criterio 1 y por el 3 a la vez, y conviene dejar dicho
  por qué, porque llegaba con una esperanza concreta (§5.4).

## 5. Los cuatro candidatos, uno por uno

### 5.1 Jaroensri et al. 2022, el elegido

> Jaroensri R, Wulczyn E, Hegde N, Brown T, Flament-Auvigne I, Tan F, Cai Y, Nagpal K, Rakha EA,
> Dabbs DJ, Olson N, Wren JH, Thompson EE, Seetao E, Robinson C, Miao M, Beckers F, Corrado GS,
> Peng LH, Mermel CH, Liu Y, Steiner DF, Chen P-HC. *Deep learning models for histologic grading
> of breast cancer and association with disease prognosis*. **npj Breast Cancer 8:113 (2022).**
> DOI `10.1038/s41523-022-00478-y` · PMC9530224 · PMID 36192400. **Acceso abierto.** Google Health.

```bibtex
@article{jaroensri2022grading,
  title   = {Deep learning models for histologic grading of breast cancer and association with
             disease prognosis},
  author  = {Jaroensri, Ronnachai and Wulczyn, Ellery and Hegde, Narayan and Brown, Trissia and
             Flament-Auvigne, Isabelle and Tan, Fraser and Cai, Yuannan and Nagpal, Kunal and
             Rakha, Emad A. and Dabbs, David J. and Olson, Niels and Wren, James H. and
             Thompson, Elaine E. and Seetao, Erik and Robinson, Carrie and Miao, Melissa and
             Beckers, Fabien and Corrado, Greg S. and Peng, Lily H. and Mermel, Craig H. and
             Liu, Yun and Steiner, David F. and Chen, Po-Hsuan Cameron},
  journal = {npj Breast Cancer},
  volume  = {8},
  pages   = {113},
  year    = {2022},
  doi     = {10.1038/s41523-022-00478-y}
}
```

**Ojo con el DOI**, porque se parece al de Mercan, el de pleomorfismo que ya está fichado en
[`../papers_11_agosto/hojas_papers_nuevos.md`](../papers_11_agosto/hojas_papers_nuevos.md) Hoja 6:
Mercan es `s41523-022-00488-w`, **este es `s41523-022-00478-y`**. Los dos son npj Breast Cancer
2022 y los dos son de mama. No son el mismo paper ni el mismo grupo.

**Por qué gana, en una frase: es la forma del pipeline de Sebastián, publicada.** Una máscara
elige dónde mirar, tres modelos de **parche** puntúan los tres componentes de Nottingham, y una
etapa 2 liviana de scikit-learn agrega a puntaje de lámina. Nuestro cambio sería reemplazar su
máscara de carcinoma invasivo por la atención de CLAM.

**Y sus tres componentes son nuestras tres etiquetas CAP, con nombre y todo:**

| Componente del paper | Task nuestra en `TASK_CONFIGS` | Baseline nuestro, AUC a 5 folds |
|---|---|---|
| Recuento mitótico | `grado_histologico_mitotic_rate` | **sin entrenar todavía** (figura en la lista de pendientes) |
| Pleomorfismo nuclear | `grado_histologico_pleomorfismo_nuclear` | 0,77 ± 0,046 |
| Formación tubular | `grado_histologico_diferenciacion_tubular` | 0,82 ± 0,062 |
| (el grado combinado) | `grado_histologico_grado_general` | 0,74 ± 0,046 |

Baselines de [`../../../results/README_experimentos_mammoth_environ.md`](../../../results/README_experimentos_mammoth_environ.md),
dataset `pth_balance`. **Ningún candidato de la lista cubre las cuatro filas de esa tabla; este
las cubre.**

El estudio completo, con los números del texto del PDF, está en
[`jaroensri_estudio.md`](jaroensri_estudio.md). Lo que lo frena está ahí y en la hoja, sin
maquillar: **no publica pesos**, su supervisión de etapa 1 no es la nuestra, y **pleomorfismo es
su componente flojo**, que es justo la tarea que Sebastián quiere atacar.

### 5.2 MIDOG 2025, el overview del challenge

> *Mitosis Detection in the Wild*, overview de MIDOG 2025, **arXiv `2606.07368`** (5-jun-2026).
> Verificado por búsqueda web, no por PDF.

**Qué aporta.** El estado del arte de la detección de mitosis con números frescos: F1 **0,740** de
detección y balanced accuracy **0,908** en la clasificación de mitosis atípicas, sobre **365
casos y 12 tipos tumorales**. Y trae el dato del §7, que es el mejor argumento externo que
tenemos para el diseño de dos etapas.

**Por qué no es el paper de la reunión.** Es un overview de challenge. Da marco, da baseline y da
de dónde sacar un detector con pesos, pero no propone un método que uno pueda poner en la casilla
del segundo modelo y decir «esto es lo que implementaríamos». Si la rama de mitosis avanza, este
documento es el primer lugar donde mirar para elegir detector; para la reunión del viernes es
soporte, no protagonista.

### 5.3 YOLO11x + ConvNeXt, dos etapas explícitas

> *Two-Stage Strategy for Mitosis Detection Using Improved YOLO11x Proposals and ConvNeXt
> Classification*, **arXiv `2509.02627`**. Código en
> `github.com/xxiao0304/MIDOG-2025-Track-1-of-SZTU`. Verificado por búsqueda web, no por PDF.

**Qué aporta.** Es dos etapas de forma literal: YOLO11x propone y ConvNeXt clasifica. Y publica el
delta de la segunda etapa, que es el número que a nosotros nos interesa: **F1 0,882 contra 0,847**
de una sola etapa, con la precisión subiendo de 0,762 a 0,839. O sea que **la segunda etapa
compra precisión**, que es exactamente el problema del §7.

**Por qué pierde.** Criterio 2. Se entrena con anotación de objeto sobre cajas de mitosis, y
nuestras marcas son 61 polígonos de una lámina, parciales. Se puede correr con pesos si los
publican, pero como método a entrenar acá no tiene con qué. Queda fichado por si la rama de
mitosis avanza por la vía de pesos preentrenados, que es donde el criterio 2 se resuelve sin
supervisión nuestra.

### 5.4 Diagnostics 14(18):2045, el descarte limpio

> *A Quantitative Measurement Method for Nuclear-Pleomorphism Scoring in Breast Cancer*,
> **Diagnostics 14(18):2045 (2024)**, PMC11431806. Verificado por búsqueda web, no por PDF.

**Llegaba con una esperanza concreta y conviene decir que no se cumplió**, porque si no queda
como un candidato descartado sin motivo. Se lo fichó para ver **si mide de forma relativa al
vecindario**, que es lo que el patólogo describió («núcleos más grandes que su vecindario») y lo
que **ninguna de las 16 features de NPKC-MIL** hace ([`../papers_11_agosto/hojas_papers_nuevos.md`](../papers_11_agosto/hojas_papers_nuevos.md)
Hoja 5).

**La respuesta es que no: evalúa cada núcleo aislado.** Con eso pierde la única razón por la que
estaba en la lista. Y encima falla otros tres criterios: opera sobre **núcleos** y exige
segmentar antes con CellProfiler (criterio 1), su 0,97 de accuracy es sobre **600 núcleos
seleccionados a mano**, 200 por clase, y no sobre láminas, así que no es comparable con nada
nuestro (criterio 3), y **no declara µm/px** (criterio 4).

## 6. Lo que quedó fuera, y por qué

**Fichados en la lista corta y no puntuados**, por tiempo y porque el ganador ya estaba claro:

- **arXiv `2509.02600`** (Team Westwood, ensemble de CNN) y **arXiv `2508.18831`** (ConvNeXt V2,
  track 2 del challenge, normales contra atípicas). Son soluciones concretas del mismo challenge
  que 5.3, con la misma limitación de supervisión.
- **TDA-MIL**, MICCAI 2025 (`papers.miccai.org/miccai-2025/0933-Paper2460.html`). Atención
  top-down: selecciona las instancias relevantes y **las re-inyecta** en una segunda pasada. No
  es la segunda etapa, **es la primera**: sería una alternativa a «top-k y listo». Queda anotado
  porque la primera etapa también es una decisión de diseño, no porque compita en este rubric.

**Fuera de la búsqueda por construcción**, y conviene tenerlo presente para que la reunión no
mezcle listas: los cuatro papers del 2-ago (PU learning, CellViT, ZoomMIL, MS-CLAM,
en [`../tareas_geometricas/`](../tareas_geometricas/)) y los dos que trajo Sebastián el 6-ago
(NPKC-MIL y Mercan, en [`../papers_11_agosto/`](../papers_11_agosto/)). **Esta búsqueda no los
reemplaza ni los revisa.** Y hay una relación que sí cambia: Jaroensri trae **evidencia en contra
de la rama de NPKC-MIL** (§8 de [`jaroensri_estudio.md`](jaroensri_estudio.md)).

## 7. El dato de MIDOG 2025 que vale solo, gane quien gane el rubric

Fuera de los puntos calientes curados, **la tasa de falsos positivos de los detectores de mitosis
se triplica** (aumento del **208 %**), medido sobre 365 casos y 12 tipos tumorales.

O sea que **correr el detector sobre la lámina entera es justamente lo que no hay que hacer**, y
restringirlo a los parches de mayor atención es la forma correcta del problema. **Es el mejor
argumento externo que tenemos para el diseño de dos etapas de Sebastián**, viene de un challenge
con 365 casos, y **no depende de que Jaroensri gane el rubric**. Si en la reunión hay que
defender la forma del pipeline antes que el paper, este es el número.

## 8. Lo que este documento no afirma

- **Que Jaroensri suba ninguna de nuestras métricas.** No está probado en nuestros datos, y el
  historial del proyecto son cuatro ejes cerrados sin mejora (Hallazgos 11 a 14). Lo que se
  afirma es que es el único candidato cuya forma calza con el pipeline propuesto, que ataca las
  tres etiquetas que ya tenemos, y que su ganancia está medida contra un baseline que entendemos.
- **Que los otros tres candidatos sean malos papers.** Se los puntúa contra **nuestro** rubric,
  que está hecho para una casilla muy específica. MIDOG 2025 y el de dos etapas siguen siendo las
  referencias vivas de la rama de mitosis.
- **Ningún número de los candidatos 5.2 a 5.4.** Salen de búsqueda web, no de haber abierto los
  PDF. Solo los de Jaroensri están verificados contra el texto.
- **Que la búsqueda sea exhaustiva.** Es una búsqueda de dos sesiones con una fecha encima, y las
  cadenas literales no quedaron registradas (§3). Quedaron sin fichar, entre otros, las ediciones
  2023 y 2024 de MIDOG, la línea de mitosis atípicas en mama (AMi-Br), y cualquier trabajo
  posterior a Jaroensri que ataque los tres componentes juntos.
- **Nada de esto está implementado ni pre-registrado.** Regla 9.

## 9. Inventario de lo descargado

Descarga autorizada por Ernesto el 13-ago, **acotada a PDF de acceso abierto**. No incluye
checkpoints ni pesos, y no se bajó ninguno.

| Archivo | Qué es | Fuente |
|---|---|---|
| [`jaroensri_2022_npjbc.pdf`](jaroensri_2022_npjbc.pdf) | El artículo, 12 pág. | PMC9530224 |
| [`supp.pdf`](supp.pdf) | El Supplementary, de donde salen la balanced accuracy y la Tabla 8 de configuraciones | idem |
| `jaroensri.txt`, `supp.txt` | Volcados de `pdftotext -layout`, para no re-extraer | generados acá |

De los otros tres candidatos **no se bajó nada**: quedaron descartados antes de necesitar el PDF.
