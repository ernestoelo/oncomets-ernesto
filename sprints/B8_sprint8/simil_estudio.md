# SI-MIL: estudio para la reunión (encargo 4)

> Kapse et al., *SI-MIL: Taming Deep MIL for Self-Interpretability in Gigapixel
> Histopathology*, CVPR 2024. PDF en [`simil_kapse2024.pdf`](simil_kapse2024.pdf)
> (arXiv:2312.15010v2). Leído completo el **30-jul-2026**: paper principal (8 pág.) y
> suplementario (§8 a §17).
>
> Ficha bibliográfica y cita BibTeX: [`papers_b8.md`](papers_b8.md) §2.
> Código y dataset que anuncian: `github.com/bmi-imaginelab/SI-MIL` (no descargado).

---

## 1. Qué propone, en una frase

Que un MIL prediga con un **modelo lineal sobre features de patología con nombre**, y que
la red profunda quede como el maestro que le enseña **dónde mirar** y después se descarta.
La interpretación deja de ser algo que se calcula después: **es** la predicción.

## 2. Cómo funciona

Dos ramas que se entrenan juntas (§3.3, Fig. 2):

**Rama MIL convencional.** Additive ABMIL sobre features profundas `g_i ∈ R^D` (un ViT-S
preentrenado con DINO sobre los propios parches). Produce atención por parche `α` y una
predicción `Ŷ_g`.

**Rama self-interpretable (SI).** No ve las features profundas. Trabaja sobre las
**PathExpert**, `f_i ∈ R^d`, que son features hechas a mano a partir del mapa de núcleos:

- HoVer-Net (entrenado en PanNuke) segmenta y clasifica los núcleos de cada parche en 5
  clases: neoplásico epitelial, conectivo, inflamatorio, necrosis y epitelial no
  neoplásico.
- De ahí salen **246 features por parche** (§17): 205 morfométricas (10 propiedades por
  núcleo × 4 estadísticos de agregación (media, desviación, asimetría, curtosis) × 5
  clases, más 5 conteos) y el resto de análisis de grafo de células (modularidad,
  coeficiente de clustering, centralidad) y de heterogeneidad espacial (mezcla de tipos
  celulares, índice de Simpson local, entropía). En TCGA-Lung son 203 porque HoVer-Net
  solo tiene 4 clases anotadas ahí.
- Cada feature tiene nombre legible: *«células neoplásicas: asimetría de la solidez»*,
  *«mezcla de células conectivas en la región de células neoplásicas»*.

**El puente: PAG Top-K.** El módulo *Patch Attention-Guided Top-K* toma la atención `α` de
la rama profunda y selecciona los **K = 20 parches** más salientes. La rama SI solo mira
esos 20. Como el Top-K normal no es diferenciable, usan el *perturbed Top-K* de
Cordonnier et al., y por ahí baja el gradiente que hace que las dos ramas se co-aprendan.

**Cómo predice la rama SI.** Un módulo de atención por feature (`PF-Mixer`, capas MLP-Mixer
que mezclan información entre parches y entre features, más atención con compuerta) produce
un peso `β_j` por cada una de las d features. Los `β` se escalan por percentil `γ = 0.75` y
sigmoide con temperatura `t = 3`, que es lo que **fuerza dispersión**: pocas features
sobreviven con peso alto. Después, un predictor **lineal** con pesos `w_j`. La predicción
final es literalmente:

```
Ŷ_f = ψ( Σ_i Σ_j  w_j · β_j · M_ij  + b )        (ec. 9)
```

Cada sumando `w_j · β_j · M_ij` es la contribución del parche *i* por su feature *j*. Eso
es el reporte que le muestran al patólogo.

**Pérdida** (ec. 10): `CE(Y, Ŷ_g) + CE(Y, Ŷ_f) + λ·KD(Ŷ_g, Ŷ_f)` con λ = 20 y
stop-gradient en la destilación, para que la rama SI persiga a la profunda y no al revés.

**En inferencia se usa solo `Ŷ_f`. La rama profunda se descarta.** Es la parte más audaz:
el modelo que sale a producción es un lineal sobre 246 features nombradas en 20 parches.
Tiene 625K parámetros contra 345K del ABMIL con DINO ViT-S, así que la mejora no viene de
tamaño.

**Por qué creen que se puede.** Su hipótesis (§1) es que un modelo muy preciso **no es
único**: con sobreparametrización hay muchas soluciones casi óptimas, así que se puede
empujar el entrenamiento hacia una que además sea legible.

## 3. Qué reportan

Tabla 1, media de 5-fold CV sobre test, con Additive ABMIL de base:

| | Lung Acc/AUC | BRCA Acc/AUC | CRC Acc/AUC |
|---|---|---|---|
| DINO ViT-S (profundo, no interpretable) | 0.896 / 0.957 | 0.937 / 0.974 | 0.904 / 0.897 |
| CTransPath (profundo) | 0.904 / 0.967 | 0.920 / 0.974 | 0.906 / 0.897 |
| PathFeat (MIL sobre PathExpert, con proyector) | 0.830 / 0.888 | 0.885 / 0.950 | 0.886 / 0.818 |
| PathFeat sin proyector (interpretable de verdad) | 0.767 / 0.837 | 0.889 / 0.914 | 0.853 / 0.720 |
| Entrenamiento en 2 etapas (análogo a post-hoc) | 0.865 / 0.932 | 0.908 / 0.924 | 0.876 / 0.862 |
| **SI-MIL** | **0.884 / 0.941** | **0.944 / 0.968** | 0.884 / **0.910** |

La lectura que hacen es que un MIL sobre features interpretables solo (`PathFeat`) pierde
bastante, y que el co-aprendizaje recupera casi todo. En BRCA incluso queda arriba del
mejor profundo en accuracy.

Ablaciones (misma tabla): sacar el PAG Top-K o la destilación cuesta entre 2 y 4 puntos
según dataset, así que las dos piezas hacen trabajo. En el suplementario (§12): si además
reemplazan las features profundas de la rama MIL por PathExpert, o sea si sacan la red
profunda del todo, la cosa cae. La red profunda hace falta **como guía**, no como
predictor.

**Un detalle que a nosotros nos toca de cerca.** La Tabla 2 adapta SI-MIL a otros MIL sobre
TCGA-BRCA:

| MIL de base | DINO ViT-S Acc/AUC | SI-MIL Acc/AUC |
|---|---|---|
| ABMIL | 0.937 / 0.974 | **0.944 / 0.968** |
| **CLAM** | **0.937 / 0.972** | 0.925 / 0.957 |
| TransMIL | 0.934 / 0.936 | 0.929 / 0.933 |

Con ABMIL la accuracy sube. **Con CLAM, que es nuestro modelo, baja** (0.937 → 0.925 en
accuracy, 0.972 → 0.957 en AUC), y con TransMIL también, un poco. O sea que el titular «no
hay compromiso entre rendimiento e interpretabilidad» está sostenido sobre ABMIL; en las
dos arquitecturas restantes hay un costo chico. Es un dato que conviene llevar dicho, no
para desacreditar el paper sino porque es exactamente la celda que nos correspondería.

**Evaluación con patólogo** (§5.1, Tabla 3). Le dieron los reportes de las 10 features más
contribuyentes en 10 láminas IDC y 10 ILC. El patólogo marcó **44.5 %** de las features
como muy relevantes, 28.3 % moderadamente y **27.2 % no relevantes**. En IDC 5.40 ± 1.43
features muy relevantes de 10; en ILC 3.25 ± 0.97. Es honesto de su parte publicarlo: algo
más de un cuarto de lo que el modelo dice que le importa, al patólogo no le dice nada, y
ellos mismos apuntan que parte puede venir de errores de HoVer-Net.

## 4. El contraste con lo nuestro, que es la conversación

| | SI-MIL | B7 y B8 nuestros |
|---|---|---|
| Cuándo aparece la interpretación | Durante el entrenamiento, por diseño | Después, sobre checkpoints congelados |
| Qué se interpreta | Features con nombre de patología | Expertos y slots aprendidos, sin nombre |
| Quién puso los nombres | La literatura de patología, antes de entrenar | Nuestra lectura visual, sin sign-off |
| Qué afecta al modelo | Lo cambia: la rama SI reorienta la atención | Nada: el modelo ya está entrenado |
| Costo de equivocarse | Un modelo peor | Una descripción equivocada |

Las dos posturas responden preguntas distintas y ninguna reemplaza a la otra. La nuestra
pregunta *qué hace este modelo*; la de ellos, *cómo construyo uno que se explique solo*.
Lo que sí es cierto es que la crítica que abre su §1 nos apunta directamente: dicen que el
análisis post-hoc sufre de **desconexión** entre las features con las que el modelo fue
entrenado y las features con las que uno después lo explica, y que un parche muy atendido
puede no ser informativo en el espacio de features interpretables. Nuestro OBJ-A cae justo
ahí: nombramos morfología mirando parches, y el modelo nunca vio esa noción de morfología.

Hay tres puntos donde el paper y lo nuestro se tocan de manera concreta:

**(a) Sus features nombradas son la respuesta a nuestro pendiente 9.** Lo que nos falta
desde el B7 es un vocabulario de tejido que no sea lectura nuestra. Las 246 PathExpert son
exactamente eso: definidas de antemano, con significado geométrico y físico, y con un
patólogo evaluándolas. Y salen de HoVer-Net, que es el otro paper del encargo.
**Los dos papers de Sebastián no son dos ángulos separados: son la misma cadena.**
HoVer-Net es el front-end de SI-MIL. Esto vale la pena decirlo en la reunión.

**(b) Dispersión impuesta contra dispersión medida.** Su percentil `γ` y su temperatura `t`
existen para forzar que **pocas** features expliquen la predicción, porque un reporte con
246 renglones no lo lee nadie. Nuestro encargo 1 midió lo contrario, sin forzar nada: el
modelo usa **29.98 de 30 expertos** y **159.5 de 300 slots** sobre 1858 láminas-fold. Puesto
uno al lado del otro: nuestro modelo reparte su capacidad, y SI-MIL muestra que se puede
predecir casi igual de bien desde un subespacio chico y legible. No son incompatibles; la
capacidad que un modelo *usa* y la que *necesita para explicarse* no tienen por qué ser el
mismo número. Es el mismo tipo de distinción que ya escribimos entre los 85 slots que
concentran el 73 % del peso y el `N_eff` de 159.

**(c) Ya medimos lo que ellos miden en su §16.** Comparan los top-K parches de SI-MIL
contra los del MIL convencional y encuentran **6 de 20 compartidos** en IDC y **0 de 20** en
ILC: co-aprender le cambia el foco al modelo. Nosotros medimos lo mismo entre CLAM y
Mammoth y dio Jaccard del top-5 % de **0.172** y del top-1 % de **0.073**, con Spearman alto
(0.805). Cuidado con equiparar los números: ellos comparan conjuntos fijos de 20 parches y
nosotros el 5 % de N, que en nuestras láminas son cientos o miles. Lo comparable es el
fenómeno, no la cifra: **dos MIL que aciertan igual pueden coincidir en el mapa grueso y
discrepar casi por completo en los picos**. Que ellos lo reporten refuerza que nuestro
hallazgo del B7 no era una rareza de Mammoth.

## 5. Qué haría falta para correrlo acá, y qué lo frena

No es una propuesta, es el inventario honesto de costos para poder responder en la reunión.

1. **La magnificación es un bloqueo duro, no un detalle.** HoVer-Net está entrenado solo a
   40×, y por eso ellos **filtraron sus datasets a láminas de 40×** (§8). Nuestras cohortes
   están a magnificación física distinta en `level0`: TCGA ≈ 40× (0.2325 µm/px), privado
   ≈ 20× (0.465 µm/px) y HistAI sin MPP confiable ([[cohortes-magnificacion-fisica]]).
   Aplicar PathExpert sobre nuestra cohorte entera daría features de núcleos calculadas
   bajo escalas físicas distintas según el origen de la lámina, que es un confound nuevo
   encima del que ya tenemos. Lo aplicable sin pelear con esto es **TCGA solamente**.
2. **El costo de preprocesamiento es de otro orden.** Reportan **~2 horas por WSI** entre
   el mapa de núcleos en GPU y las features en CPU, y ~4400 horas en total para 2.2K
   láminas con 3 RTX 8000 y una CPU de 40 núcleos con 500 GB de RAM (§13). Nosotros
   tenemos **una** A6000 compartida, hoy con cuatro jobs ajenos. Esto no entra en un fin de
   semana como el grid del encargo 3.
3. **Ellos publican el dataset ya procesado, y ahí hay solapamiento con nosotros.**
   Anuncian mapas de núcleos y PathExpert para más de 2200 WSI, **TCGA-BRCA incluido**
   (910 láminas: 825 de entrenamiento y 85 de test), con licencia CC BY-NC 4.0 y alojamiento
   previsto en TCIA Analysis Results. Si esas láminas se cruzan con las nuestras de TCGA,
   se saltea el punto 2 entero. **Es lo primero que hay que verificar**, y es una consulta
   de una tarde, no un sprint.
4. **Sus tareas son binarias y con clases parejas** (IDC vs ILC, LUAD vs LUSC, mutación
   alta vs baja). Las nuestras están fuertemente desbalanceadas, y esa es la restricción
   que ya nos comió cuatro ejes. Nada en el paper dice cómo se comporta la rama lineal con
   una minoritaria de 65 casos.
5. **Solo probaron features DINO ViT-S** y lo dicen explícito (§4.1: *«evaluated with only
   DINO ViT-S features»*). Nosotros usamos CONCH. No hay razón para que no funcione, pero
   tampoco evidencia de que sí.

## 6. Qué se puede tomar prestado sin adoptar el método

- **El reporte de contribución por feature** como formato de entregable clínico. Aunque no
  usemos SI-MIL, la forma de la Fig. 3 (lámina con heatmap, parche con mapa de núcleos,
  barras de contribución con intervalo, y un ejemplo visual de la feature en valor bajo,
  medio y alto) es un molde de presentación muy superior al nuestro y es replicable.
- **Evaluar con patólogo y publicar el porcentaje de features no relevantes.** Ese 27.2 %
  es el tipo de número que nos falta para cerrar el pendiente del sign-off.
- **Su criterio de comparación justa**: para comparar interpretabilidad entre dos modelos
  eligen solo láminas del test donde **ambos aciertan**. Es exactamente lo que hicimos en
  el B7 con las 7 láminas, así que nuestro diseño coincide con el de un CVPR.

## 7. Qué no se afirma

- **Esto no reabre el eje de rendimiento de Mammoth** (Hallazgo 12). SI-MIL es un trabajo
  de diseño de interpretabilidad, y en la única celda que nos corresponde (CLAM de base)
  su rendimiento **baja** un poco. Traerlo como propuesta de mejora activaría la regla 9.b
  sin tener con qué citarla.
- **No se afirma que las PathExpert vayan a funcionar sobre nuestras tareas.** Están
  validadas sobre subtipos histológicos y carga mutacional, no sobre microcalcificaciones,
  CDIS ni invasión linfovascular.
- **No se afirma que su dataset cubra nuestras láminas.** Hay que verificar el cruce; hoy
  es una expectativa razonable, no un hecho.
- **No se descargó nada** del repositorio ni del dataset (workaround E).

## 8. Preguntas para llevar

1. ¿El interés es **entender** la línea self-interpretable, o **evaluarla** como candidata
   para OncoMets? Cambia por completo el tamaño del trabajo: lo primero está hecho con este
   documento, lo segundo empieza por HoVer-Net sobre TCGA y no cabe junto al grid del
   encargo 3.
2. Si es lo segundo, ¿se acepta acotarlo a **TCGA solo**, por lo de la magnificación? Es la
   única forma de que las features de núcleos sean comparables entre láminas.
3. ¿Vale la pena que gastemos una tarde en **verificar si su dataset publicado cubre
   nuestras láminas de TCGA-BRCA**? Es la diferencia entre 4400 horas de cómputo y una
   descarga.
4. El 27.2 % de features que el patólogo declaró no relevantes, ¿es un resultado aceptable
   para el estándar clínico de Environ, o es justamente el argumento de que la
   interpretabilidad automática todavía no llega?

---

## Anexo: hiperparámetros, por si hace falta el detalle

`K = 20` (subir K empeora, §11), capas PF-Mixer = 4 (6 sobreajusta), `λ = 20`, `γ = 0.75`,
`t = 3`, `d = 246` (203 en Lung), sigmoide como activación final porque todas sus tareas
son binarias, batch de 1 lámina, 5-fold CV sobre el split de entrenamiento con test
apartado, learning rate buscado en {1e-3, 2e-3, 1e-4, 2e-4}, weight decay en {1e-2, 5e-3},
una RTX 8000. Parches de 224×224 a 5× y sus 1792×1792 correspondientes a 40× para las
PathExpert.
