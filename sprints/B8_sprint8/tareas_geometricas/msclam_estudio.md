# MS-CLAM: estudio (el cuarto, fuera de las tres familias)

> Tourniaire P, Ilie M, Hofman P, Ayache N, Delingette H, *MS-CLAM: Mixed supervision for the
> classification and localization of tumors in Whole Slide Images*, **Medical Image Analysis
> 85:102763 (2023)**. DOI `10.1016/j.media.2023.102763`.
> PDF en [`msclam_tourniaire2023.pdf`](msclam_tourniaire2023.pdf) (17 pág., versión de autor de
> HAL `hal-03972289`, porque la de revista es de suscripción).
> Código clonado en `clam_testing2/MSCLAM_reference/` (HEAD `18e8827`, 29-ago-2024, 5.1 MB),
> **reference only**: solo lectura, NO al PYTHONPATH, NO import cruzado.
>
> **Bajado el 3-ago-2026.** Ficha: [`papers_mitosis.md`](papers_mitosis.md) §5.
>
> Se lo incluyó porque el encargo dice "aprovechando la información del patólogo sobre las
> etiquetas" y este es el que responde a esa frase de la forma más literal. Queda quinto en
> prioridad, y ahora se puede decir **por qué** con precisión.

---

## 1. Qué propone, en una frase

CLAM, el mismo, entrenado con **supervisión mixta**: la mayoría de las láminas aporta solo su
etiqueta de lámina, y unas pocas aportan además la etiqueta de **cada parche**, que se usa para
supervisar directamente los puntajes de atención.

Es el paper más cercano a nuestra infraestructura de los cuatro: el repo es un fork del CLAM de
Mahmood Lab, con `main.py`, `models/`, `splits/`, `dataset_csv/` y `.h5` de parches. Si alguna vez
se implementara, no habría que aprender un codebase nuevo.

## 2. Las tres piezas

**a) La loss de atención.** Para láminas **normales**, la atención debería ser plana (todos los
parches pesan igual), y eso se impone con un término de entropía, equivalente a una divergencia
KL contra la uniforme. Para láminas **tumorales** con etiquetas de parche, el término tiene tres
partes (ec. 3), con tres objetivos declarados:

1. la atención de los parches **no tumorales** debe ser cercana a cero;
2. por lo tanto la suma de la atención de los tumorales debe acercarse a 1;
3. la entropía **dentro** de los tumorales debe ser máxima, o sea que todos los parches con tumor
   pesen parecido.

```
L_att = Σ_{no tumorales} a_i  +  (1/log m)·Σ_{tumorales} a_j log a_j  -  Σ_{tumorales} a_j
```

**b) El lote pareado (paired batch).** Procesan a la vez una lámina tumoral y una normal, y arman
el lote de parches con `B` tumorales y `B/2` normales de la tumoral, más `B/2` normales de la
normal, para un lote de `2B`. Sirve para que el clasificador de parches vea las dos clases en cada
paso.

**c) El muestreo exponencial decreciente.** Las láminas **con** etiquetas de parche arrancan con
peso `W` y las que no, con peso 1; `W` decae por `γ` en cada época hasta que todas se muestrean
uniformemente. Reemplaza el entrenamiento en dos fases de su paper previo: al principio el
clasificador de parches ve sobre todo etiquetas verdaderas, y de a poco se le van sumando las
pseudo-etiquetas.

## 3. El hueco #5 del handoff: qué hace con las láminas sin anotación de parche

La pregunta era si "una sola lámina anotada" lo mata del todo o solo lo debilita. El paper la
responde de forma explícita y hay dos capas.

**Capa 1, la que sí está resuelta.** Las láminas sin etiquetas de parche caen en el camino
débilmente supervisado de CLAM de siempre: las **pseudo-etiquetas** salen de los puntajes de
atención (su Figura 2, mitad de arriba). Y hay una sección entera, la **§2.5 "MS-CLAM without
tile-level labels"**, que trata la ausencia total como caso particular: se conserva solo la ec. 2
(la de láminas normales), porque la ec. 3 necesita etiquetas de parche; el lote pareado se sigue
usando; y el muestreo exponencial se apaga fijando `W = 1, γ = 1`. O sea que el método **degrada
con gracia** hasta volver a ser CLAM. La escasez, por sí sola, no lo rompe.

Para dimensionar: su ajuste más chico usa el **12 % de las láminas anotadas**, que en Camelyon16
son **11 láminas tumorales completamente anotadas**. Nosotros tenemos **una**, parcial.

**Capa 2, y es la que lo descarta para nuestro caso.** Dentro de una lámina anotada, el método
asume que la etiqueta de parche es **correcta y exhaustiva**. El primer término de la ec. 3
minimiza la suma de atención de los parches marcados como no tumorales, es decir **empuja
activamente hacia cero la atención de todo lo que no fue marcado**.

Con positivos parciales eso es exactamente el gradiente equivocado: una mitosis real sin marcar
recibiría presión para que el modelo deje de mirarla. Es la **hipótesis opuesta** a la del paper
de PU learning, que dice que lo no marcado tiene etiqueta desconocida y por eso reescribe el
término.

**Y hay una ironía útil para la reunión:** su propio dataset tiene el problema. El paper aclara
que en Camelyon16 todas las láminas metastásicas están anotadas exhaustivamente **"except for 20
slides which were only partially annotated"**, y más adelante observan que algunas láminas
tumorales de DigestPath2019 tienen tumor sin anotar. O sea que la anotación parcial aparece en sus
datos como una excepción molesta, no como un régimen que el método modele.

**Respuesta corta al hueco:** una sola lámina anotada lo **debilita** (el método sigue corriendo,
degradado a CLAM); lo que lo **mata** para nosotros es que esa única lámina tiene positivos
parciales, y la loss de atención asume que no los tiene.

## 4. Qué reportan

Camelyon16 y DigestPath2019. Con entre el **12 y el 62 %** de las láminas con anotación de parche
llegan a rendimiento cercano al totalmente supervisado, en clasificación y en localización (Dice
sobre láminas tumorales, especificidad sobre normales). Con el 12 %, o sea 11 láminas, ya ven la
mejora sobre CLAM.

El aporte más visible es en **localización**: los mapas de atención de CLAM sobreestiman mucho la
región tumoral (Dice 0.520 en Camelyon16, cubriendo a veces casi todo el tejido) y la supervisión
de atención los ajusta.

Ese punto merece una nota para nosotros: el problema que MS-CLAM resuelve es que **la atención de
CLAM se derrama**. En nuestra medición del 1-ago la atención **no** se derramó, cayó sobre las
marcas (AUC 0.890 para mitosis, y grasa en 0.154). O sea que llegamos a este paper con el síntoma
que él arregla ya bastante ausente.

## 5. Qué nos sirve, y qué no

**Sirve.**

- Es la **respuesta preparada** si en la reunión sale "¿y por qué no le agregamos supervisión de
  parche a CLAM y listo?". Se puede, está publicado, funciona, y necesita un orden de magnitud
  más de anotación del que tenemos, con una suposición que nuestras marcas no cumplen.
- Es el más barato de adoptar en términos de codebase: es CLAM.
- La idea del **muestreo con peso decreciente** para láminas anotadas es reusable por separado, si
  alguna vez tenemos anotaciones de parche.

**No sirve hoy.**

- Su loss de atención asume anotación exhaustiva dentro de la lámina anotada (§3, capa 2).
- Es binario tumor / no tumor, y nuestras tareas de mitosis y grado nuclear son puntajes de 3
  clases.
- El síntoma que arregla (atención derramada) no es el que medimos.

## 6. Lo que este estudio no afirma

- Que MS-CLAM no sirva **nunca** para nosotros. Si alguna vez hay láminas con anotación densa de
  región tumoral, vuelve a la mesa.
- Que su ec. 3 no se pueda modificar para tolerar positivos parciales. Se podría, y sería
  precisamente traer la idea del paper de PU learning acá. Eso es una propuesta, no un hallazgo, y
  va con regla 9 si alguien la quiere seguir.
- Que sus números se trasladen a nuestras tareas. Son Camelyon16 y DigestPath2019, binarias.

## 7. Preguntas para llevar

1. ¿Alguien va a pedir supervisión de parche para CLAM? Si sí, esta es la referencia y este es el
   motivo por el que hoy no se puede.
2. Si el patólogo anotara **regiones** (no puntos) en unas pocas láminas, MS-CLAM pasaría de
   quinto a candidato. ¿Vale la pena preguntarlo junto con el pedido de marcas de mitosis?
