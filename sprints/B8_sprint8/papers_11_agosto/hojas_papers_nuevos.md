# Los dos papers que trajo Sebastián: una hoja cada uno

> Escrito el **11-ago-2026 (noche)** para la reunión del **miércoles 12-ago**. Mismo formato
> que [`../tareas_geometricas/hojas_reunion.md`](../tareas_geometricas/hojas_reunion.md): una
> hoja por paper, para leer en la reunión sin abrir nada más.
>
> **Todo lo de acá está verificado contra los dos PDF de esta carpeta**, que Sebastián dejó el
> 6-ago. Los números salen del texto del paper, no de resúmenes.
>
> **Qué NO es.** No es un pre-registro y no propone implementar nada. Regla 9: si alguna de
> estas dos ramas avanza, va con hipótesis pre-registrada, métrica y dirección esperada, y
> `reviewer` antes de tocar código.

---

## Hoja 0. El cuarteto real, y por qué cambia el encuadre

La reunión es sobre **cuatro** papers, y no son los cuatro que fichamos el 2-ago. Son:

| | Paper | De dónde salió | Qué tarea ataca |
|---|---|---|---|
| 1 | **PU learning**, Zhao et al., MELBA 2022 | nuestra búsqueda del 2-ago | mitosis |
| 2 | **ZoomMIL**, Thandiackal et al., ECCV 2022 | nuestra búsqueda del 2-ago | mitosis (y el confundido de escala) |
| 3 | **NPKC-MIL**, Wang y Yuan, iScience 2024 | Sebastián, 6-ago | grado nuclear |
| 4 | **Pleomorfismo nuclear**, Mercan et al., npj Breast Cancer 2022 | Sebastián, 6-ago | grado nuclear |

**CellViT y MS-CLAM quedan fuera de la reunión.** Sus hojas (2 y 4 de
`hojas_reunion.md`) siguen siendo fichas válidas y no se tocan, pero no son el material de
esta reunión.

**Lo que el cambio hace visible.** El encargo del 31-jul tenía dos tareas, mitosis y grado
nuclear, y nuestra búsqueda del 2-ago quedó volcada a mitosis: de los cuatro que fichamos,
tres eran de esa rama y grado nuclear se apoyaba en CellViT, que **no tiene clase mitótica ni
puntaje de pleomorfismo** y entraba de refilón. Los dos que trajo Sebastián llenan justo ese
hueco. El cuarteto queda **simétrico: dos por tarea**, y esa es la forma de la reunión.

**La consecuencia que más pesa, y conviene decirla temprano: la escala juega al revés en cada
rama.** La mitosis se cuenta a 40× y nuestro privado está a 20×, así que toda la rama de
mitosis arrastra un reescalado con riesgo. El paper de pleomorfismo entrena y evalúa a
**0,5 µm/px**, que es prácticamente nuestro privado (0,465): la rama de grado nuclear no tiene
ese problema. No es un detalle de implementación, es el orden en que conviene gastar el
esfuerzo.

---

## Hoja 5. NPKC-MIL (Wang y Yuan). Núcleos como restricción de la loss

> Wang X, Yuan W. *Nuclei-level prior knowledge constrained multiple instance learning for
> breast histopathology whole slide image classification*. **iScience 27:109826, 21-jun-2024.**
> DOI `10.1016/j.isci.2024.109826`. **Acceso abierto (CC BY).**
> Código: `github.com/WxpHB/NPKC-MIL`, declarado público en el paper.

**Qué propone.** Que a un MIL con atención, que es nuestro CLAM, le falta una dimensión de
análisis: mira la lámina y mira el parche, pero nunca mira el **núcleo**. La propuesta no
cambia el agregador. Agrega **dos penalizaciones a la loss**: una de parche (una CNN sobre los
parches) y una de núcleo (una red convolucional de grafos sobre los núcleos), y entrena con la
suma de las tres. La interpretabilidad es el argumento declarado: las features de núcleo
tienen nombre.

**Cómo construye la parte de núcleos.** Segmenta con **HoVer-Net**, convierte cada núcleo en
un nodo, arma la topología con K-NN, y le cuelga a cada nodo **16 features hechas a mano**:
nueve geométricas (eje mayor, eje menor, área, dirección, excentricidad, elipticidad, diámetro
equivalente, perímetro, área del casco convexo) y siete de textura (contraste, disimilitud,
homogeneidad, entropía, momento angular de segundo orden, rugosidad, dispersión).

**El detalle que lo vuelve interesante para nosotros, y está verificado en el texto.** La rama
de núcleos no corre sobre la lámina entera: entrena sobre los **c = 8 parches de atención más
alta**. O sea que **es la idea que propuso Sebastián**, la de correr el análisis de núcleos
solo sobre los mejores parches que CLAM selecciona, publicada y con números. La diferencia es
de grado: él dijo veinte, el paper usa ocho.

**Los números** (476 láminas, binario normal contra canceroso, partición 7:1:2, o sea unas 80
láminas de test):

| Método | AC (%) | SP (%) | SE (%) | PC (%) |
|---|---|---|---|---|
| **NPKC-MIL** | **96,25** | **97,50** | **95,00** | **97,44** |
| TransMIL | 88,75 | 87,50 | 90,00 | 87,80 |
| CLAM-SB | 86,25 | 82,50 | 90,00 | 83,72 |
| ReMix | 86,25 | 92,50 | 80,00 | 91,43 |
| DTFD-MIL | 83,75 | 87,50 | 80,00 | 86,49 |
| FRMIL | 76,25 | 67,50 | 85,00 | 72,34 |

**Y la tabla que hay que leer al lado, porque es la que no cierra.** Sus propias ablaciones:
solo lámina **83,75**; lámina más parche **86,25**; lámina más núcleos **85,00**. Las dos
restricciones por separado suman **+2,5** y **+1,25**, y juntas dan **+12,5**. El paper no
explica ese salto, y con 80 láminas de test cada punto son 0,8 láminas. **Es la primera
pregunta que haría un revisor, y conviene llevarla dicha por nosotros.**

**El dataset, que también hay que mirar.** 476 láminas juntando tres fuentes: BRACS (423
efectivas de 547), BACH2018 (20 cancerosas) y 33 propias de los autores, **agregadas para
balancear**. Y las tres están a escalas distintas: 0,25 · 0,42 · 0,50 µm/px. Es exactamente
nuestro confundido de magnificación, sin tratamiento y sin mención.

**A favor.**

- **No cambia el agregador ni pide anotación nueva.** Las features de núcleo se calculan, no
  se anotan. La supervisión que exige es la etiqueta de lámina, que ya tenemos.
- **Es la versión publicada de la idea de Sebastián** (núcleos solo sobre los parches de
  atención alta), y eso vuelve la idea citable en vez de casera.
- Código público y hardware modesto: entrenaron en una **GTX 2080 de 8 GB**. Nuestra A6000 no
  es el límite.
- Encaja en la receta de `@mil-model-integration` sin tocar `clam_environ`: es un
  `--model_type` nuevo con dos términos más en la loss.

**Lo que lo frena.**

- **La tarea es binaria, normal contra canceroso.** Es más fácil que las nuestras, y de ahí no
  se deduce nada sobre `pleomorfismo_nuclear` en tres clases. Nuestro `tipo_histologico`, que
  es lo más parecido, ya está en 0,88 de AUC a 5 folds.
- **Hereda entero el costo que Sebastián pausó**: sin segmentación de núcleos no hay rama de
  núcleos, y eso es HoVer-Net. Los ocho parches lo vuelven manejable, y esa es justamente la
  cuenta que conviene rehacer en la reunión.
- **El salto de las ablaciones no está explicado** (arriba), y las tablas de cuatro láminas
  sueltas (WSI-1 a WSI-4) son anecdóticas, no evidencia.
- Sus 16 features son las mismas familias que las 246 de SI-MIL, que ya miramos y descartamos
  implementar por costo. Acá el paquete es mucho más chico, que es a la vez su ventaja y su
  techo.

**No se afirma.** Que suba ninguna de nuestras métricas, que el +12,5 sea real fuera de su
partición, ni que las 16 features capturen «más grande que su vecindario», que es lo que pidió
el patólogo y que **ninguna de las 16 mide de forma relativa al vecindario**.

---

## Hoja 6. Pleomorfismo nuclear (Mercan et al.). El que ataca nuestra tarea de frente

> Mercan C, Balkenhol M, Salgado R, … van der Laak J, Ciompi F. *Deep learning for
> fully-automated nuclear pleomorphism scoring in breast cancer*. **npj Breast Cancer 8:120
> (2022).** DOI `10.1038/s41523-022-00488-w`. **Acceso abierto.** Grupo de Radboud.
> Datos: las 118 láminas de evaluación están públicas (Zenodo `10.5281/zenodo.7285896`) con
> plataforma de evaluación en `breastpleomorphism.grand-challenge.org`. **El código no.**

**Qué propone.** Dos ideas, y la segunda es la que importa.

1. Acotar el análisis al tumor invasivo con un **detector de células epiteliales** (RetinaNet
   entrenado con anotaciones de punto, parches de 256 px a 40×), que queda **congelado**.
2. Puntuar el pleomorfismo como una **regresión continua entre 1 y 3** en vez de clasificar en
   tres clases, con una DenseNet sobre parches de **512 × 512 a 0,5 µm/px** y loss smoothL1.

**De dónde sale la etiqueta, que es el corazón del paper.** No de un consenso ni de una
mayoría: del **promedio de los puntajes de 10 patólogos de 6 países** sobre cada región. El
argumento es que forzar una mayoría tira a la basura la información que está en el desacuerdo,
y que ese desacuerdo **es** la señal de que el pleomorfismo es un continuo. Por eso pueden
entrenar una regresión: la referencia ya viene con decimales.

**Cómo pasa de parches a lámina.** Recorre la lámina en tiles solapados (512 px con 448 de
solape), promedia los puntajes por bloque y después promedia los bloques. **Promediar es lo
correcto acá**, y conviene decirlo en voz alta porque es lo contrario de mitosis: el recuento
mitótico es un máximo local en el punto caliente, el pleomorfismo es el aspecto predominante.
Las dos tareas del encargo piden operadores opuestos.

**Los números.**

| Nivel | Medida | Valor |
|---|---|---|
| Parche | MAE / MSE / varianza explicada | 0,262 ± 0,004 · 0,111 ± 0,002 · 0,756 ± 0,009 |
| Región (45 ROI) | kappa cuadrático contra la mayoría | **0,61**, mejor que 8 de los 10 patólogos |
| Región | kappa medio pareado | **0,53**, el más alto de todo el panel |
| Lámina (118) | coincidencia exacta con cada patólogo | 74 · 66 · 71 · 75 láminas (63 · 56 · 60 · 64 %) |
| Lámina | kappa pareado | 0,56 · 0,43 · 0,44 · 0,47, media 0,475 (segundo del panel) |

Los dos únicos patólogos que le ganan en región tienen kappa 0,67 y 0,66 contra la mayoría.
Fuera de esos dos, **el algoritmo concuerda con el panel mejor que sus miembros**. Y el techo
lo pone el propio panel: entre patólogos el kappa medio es de ese mismo orden, así que la
tarea tiene un límite de acuerdo humano y el modelo ya está pegado a él.

**Datos, para dimensionar.** Región: 125 ROI de tumor y 79 de epitelio normal, de 39 láminas;
entrenaron con **52 ROI de 16 láminas**. Lámina: 118, usadas solo para evaluar. Todo escaneado
a 0,25 µm/px y remuestreado a 0,5 para entrenar.

**Por qué nos toca de frente.**

- **Es nuestra tarea, con nuestro nombre.** `pleomorfismo_nuclear` existe en nuestros CSV y
  hoy está en 0,77 ± 0,046 de AUC a 5 folds, con score_1 en 5 láminas en privado y 62 en el
  conjunto grande.
- **Trabaja a 0,5 µm/px, que es nuestro privado.** Es el único de los cuatro donde la escala
  física juega a favor sin reescalar nada.
- **No exige anotación de núcleos.** El paper lo dice como su ventaja principal: entrenar la
  regresión no necesita marcar un solo núcleo. Lo que sí necesita es un **puntaje por región**,
  que es una anotación mucho más barata que un punto por objeto.
- El modo de falla que reportan es informativo para nosotros: cuando el detector epitelial
  confunde benigno o in situ con invasivo, el promedio se hunde y la lámina baja un punto. Y
  el Grad-CAM muestra que acierta cuando mira núcleos y falla cuando mira estroma.

**Lo que lo frena.**

- **El código no está publicado**, y la primera etapa, el detector epitelial, es **in-house**
  y de otro paper del mismo grupo. Reproducir la cadena entera no es clonar un repo. Lo que sí
  está público es el **test**: 118 láminas y el evaluador oficial.
- **La referencia son 10 patólogos por región.** Lo nuestro es un puntaje por lámina sacado
  del informe CAP: mucho más barato y mucho más grueso. La brecha entre las dos supervisiones
  es exactamente lo que habría que discutir antes de prometer nada.
- Una lámina por paciente, y ellos mismos lo marcan como limitación.

**No se afirma.** Que la regresión continua suba nuestra métrica, que un puntaje de informe
CAP alcance donde ellos usan el promedio de diez lecturas de región, ni que su primera etapa
sea reemplazable por lo que tenemos. Las tres son preguntas abiertas y la reunión es el lugar
para plantearlas.

---

## Lo que estas dos hojas no afirman

- **Que ninguno de los dos suba la métrica.** No están probados en nuestros datos, y el
  historial del proyecto son cuatro ejes cerrados sin mejora (Hallazgos 11 a 14).
- **Que la rama de grado nuclear sea más prometedora que la de mitosis.** Lo que se afirma es
  más chico y más sólido: en grado nuclear la escala física juega a favor y la anotación que
  haría falta es más barata, mientras que en mitosis las dos cosas juegan en contra.
- **Nada de esto está implementado ni pre-registrado.** Regla 9.
