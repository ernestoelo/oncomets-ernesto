# O2 — Cómo se determina el score cuando conviven núcleos de grados distintos

> Encargo 2 de Sebastián en la reunión que abre el B10: «uno intuitivamente piensa en, ya, la
> mayoría gana, pero pueden haber sutilezas o reglas al momento de hacer el scoring».
>
> Escrito el **8-sep-2026**. Fuente primaria: `papers/Breast.Invasive.Bx_1.2.0.0.REL_CAPCP.pdf`,
> que **ya estaba en el repo** desde el 3-jun. **No se bajó nada** (regla E, default sin
> autorización). Todas las citas son textuales y van con su sección del protocolo.
>
> Esto no es un doc suelto: es lo que justifica el descriptor del pre-registro de O1
> ([`../grado_sin_marca/prereg.md`](../grado_sin_marca/prereg.md)).

---

## 0. La respuesta corta

**No hay regla de cantidad, y no gana la mayoría.** El protocolo no cuenta núcleos de ningún
grado. Lo que separa un score de otro es **cuánta variación** hay respecto de un tamaño de
referencia externo, que es el **epitelio mamario normal**.

Y hay una asimetría que conviene decirle a Sebastián en la misma frase, porque le toca a él:
**el único componente del grado que sí es un conteo por área es el mitótico**, y es también
**el único que trae regla de selección de campo** («la parte más mitóticamente activa»). Para
pleomorfismo el protocolo **no dice** dónde mirar.

---

## 1. Dónde vive cada cosa en el protocolo

| Qué | Sección del CAP | Página |
|---|---|---|
| Los tres componentes de Nottingham y su suma | checklist «Histologic Grade (Nottingham Histologic Score)» | 4-5 |
| Definición de los 3 scores de pleomorfismo | ídem, sub-bloque «Nuclear Pleomorphism» | 4 |
| Cómo se puntúa el mitótico y la regla del campo | Nota B, «Histologic Grade» | 8 |
| Tabla de mitosis por diámetro de campo | Nota B, **Tabla 1** | 9 |
| Grado nuclear de CDIS, los 6 rasgos | Nota C, **Tabla 2** | 10 |
| Carcinomas múltiples con grados distintos | Nota E, «Additional Findings» | 11 |

## 2. Pleomorfismo nuclear invasivo: la definición es comparativa, no cuantitativa

Los tres scores, textuales del checklist (pág. 4):

- **Score 1**: «Nuclei small with **little increase in size in comparison with normal breast
  epithelial cells**, regular outlines, uniform nuclear chromatin, **little variation in size**».
- **Score 2**: «Cells **larger than normal** with open vesicular nuclei, visible nucleoli, and
  **moderate variability in both size and shape**».
- **Score 3**: «Vesicular nuclei, often with prominent nucleoli, exhibiting **marked variation in
  size and shape**, occasionally with very large and bizarre forms».

Tres cosas que hay que leer explícitas, porque contestan el encargo:

1. **El eje que separa los tres scores es la variación**, no el tamaño solo: «little variation»,
   «moderate variability», «marked variation». El estadístico fiel es de **dispersión** (CV, rango
   intercuartil, cola alta), no de tendencia central.
2. **El tamaño se define contra una referencia externa**, el epitelio mamario normal, y no contra
   la propia lámina. El percentil intra-lámina que usó el B9 es una elección nuestra, sin respaldo
   en el protocolo.
3. **No aparece ningún umbral de cantidad** para pleomorfismo invasivo. Ni «cuántos núcleos
   grandes», ni «qué fracción del área». La sospecha de Sebastián de que existe una regla así
   **no se verifica en este documento**, y su intuición de «gana la mayoría» tampoco.

Nottingham suma los tres componentes (tubular, pleomorfismo, mitótico), cada uno 1 a 3, y el total
da el grado: **3-5 = grado 1, 6-7 = grado 2, 8-9 = grado 3** (checklist, pág. 4-5).

## 3. El único que cuenta y el único que dice dónde mirar es el mitótico

Nota B, pág. 8, textual: «The mitotic score is determined by the number of mitotic figures found in
**10 consecutive high-power fields (HPF) in the most mitotically active part of the tumor**. Only
clearly identifiable mitotic figures should be counted; hyperchromatic, karyorrhectic, or apoptotic
nuclei are excluded.»

Ahí están las dos cosas que faltan en pleomorfismo: **un conteo** y **una regla de peor campo**. La
Tabla 1 (pág. 9) convierte ese conteo en score según el **diámetro del campo**, de 0,40 a 0,69 mm,
o sea de 0,125 a 0,374 mm² por campo. Diez campos de 0,60 mm de diámetro son **2,83 mm²**, que es
de dónde sale la cifra de 3 mm² del paper de Ibrahim que ya está citada en el deck del B9
([[paper-3mm2-ibrahim-modern-pathology]]).

**Esta parte es de Sebastián** por el reparto de la reunión. Se documenta acá sólo porque es la
mitad que contesta su pregunta: la regla que él buscaba existe, pero no en el componente que nos
tocó.

## 4. Grado nuclear de CDIS: seis rasgos, y el único corte numérico es de tamaño

Nota C, **Tabla 2** (pág. 10). Seis rasgos: pleomorfismo, tamaño, cromatina, nucléolos, mitosis y
orientación, cada uno con su descripción para grado I, II y III. **El grado II se define en los
seis rasgos como «Intermediate»**, o sea por descarte de los otros dos.

El único con corte numérico es **tamaño**, y su texto completo importa:

| Grado | Texto textual de la fila «Size» |
|---|---|
| I (bajo) | «**1.5 to 2 x** the size of a normal red blood cell **or** a normal duct epithelial cell nucleus» |
| II (intermedio) | «Intermediate» |
| III (alto) | «**>2.5 x** the size of a normal red blood cell **or** a normal duct epithelial cell nucleus» |

Tampoco acá hay regla de cantidad ni de mayoría.

### 4.a La ambigüedad que hay que resolver antes de usar los cortes

**El protocolo dice «size» y no dice si es diámetro o área.** No es un detalle de redacción: el
factor entre las dos lecturas es el cuadrado.

| Corte del CAP | Si «size» = **diámetro** ⇒ en área | Si «size» = **área** ⇒ en área |
|---|---|---|
| 1,5× | **2,25×** | 1,50× |
| 2,0× | **4,00×** | 2,00× |
| >2,5× | **6,25×** | 2,50× |

Nuestro descriptor primario es el **área** de la instancia de HoVer-NeXt, así que la lectura elegida
cambia el umbral por un factor 2,5. **Se adopta la lectura de diámetro** y se declara: en patología
las razones de tamaño nuclear se expresan contra el **diámetro** del glóbulo rojo, que es la
referencia clásica de calibración al microscopio, y la alternativa (una razón de áreas) obligaría a
que el patólogo estimara superficies a ojo. **Es una interpretación nuestra, no una cita**, y va a
la lista de preguntas para el patólogo.

### 4.b Y la referencia son dos cosas distintas, no una

«a normal red blood cell **or** a normal duct epithelial cell nucleus»: el protocolo ofrece **dos
anclas** y las trata como intercambiables. Un glóbulo rojo mide ~7,5 µm de diámetro. Medido sobre
nuestro propio material, el núcleo epitelial mediano por lámina que segmenta HoVer-NeXt da:

| lámina | n epiteliales | área mediana (µm²) | diámetro equivalente (µm) |
|---|---|---|---|
| 109609 | 2.348 | 22,7 | 5,38 |
| 103762 | 28.948 | 23,8 | 5,50 |
| 106552 | 8.731 | 26,2 | 5,77 |
| B25-158899 | 30.688 | 28,1 | 5,98 |
| 110616 | 4.828 | 30,9 | 6,27 |
| 124729 | 63.400 | 33,1 | 6,49 |
| 124806 | 100.223 | 34,2 | 6,60 |
| 126504 | 91.192 | 35,2 | 6,70 |
| 144317 | 18.296 | 34,8 | 6,66 |
| 128194 | 43.034 | 36,1 | 6,78 |
| 164001 | 17.842 | 37,0 | 6,86 |
| 129741 | 87.553 | 46,5 | 7,69 |

Rango **5,38 a 7,69 µm**, mediana 6,54. Es del orden del glóbulo rojo, así que las dos anclas del
CAP son consistentes entre sí sobre este material. **Pero esto no valida el ancla**: son *todos* los
epiteliales de la lámina, tumorales incluidos, y además el área de `epithelial-cell` está erosionada
por su umbral de foreground, que es el más alto de las siete clases
([`../../B9_sprint9/ejes_nucleares/resultados.md`](../../B9_sprint9/ejes_nucleares/resultados.md) §2.d).
El número de arriba sirve para decir que el orden de magnitud cierra, no para fijar el denominador.

## 5. Qué pasa cuando conviven grados distintos: lo que el CAP dice y lo que no

Se buscó explícitamente en el documento entero (`worst`, `predominant`, `majority`, `highest`,
`average`, `overall`, `heterogen`, `multiple`). El resultado:

- **La única regla de selección espacial de todo el protocolo** es la del mitótico, «the most
  mitotically active part of the tumor» (pág. 8). No hay equivalente para pleomorfismo ni para el
  grado nuclear de CDIS.
- **La única regla sobre grados que conviven** está en la Nota E (pág. 11): «If **multiple invasive
  carcinomas** are present and **differ in histologic type, grade**, or the expression of ER, PgR,
  or HER2, this information should be included as text in this section». O sea: cuando la
  heterogeneidad es **entre carcinomas distintos**, el protocolo pide **reportarlos por separado**,
  no promediarlos ni quedarse con el peor.
- **Para la heterogeneidad dentro de un mismo carcinoma, este documento no dice nada.** Ni mayoría,
  ni peor campo, ni promedio. Eso es un hallazgo, no una laguna de nuestra búsqueda: la respuesta a
  la pregunta de Sebastián, tal como la hizo, **no está en el protocolo del CAP**.

El CAP cita como fuentes Ellis & Elston (*Breast Pathology*, 2006) para el grado histológico y la
NHSBSP nº 58 (2005) para la Tabla 1, y Schwartz et al. (*Cancer* 1997) para la Tabla 2. **Ir a
esas fuentes exigiría autorización de descarga** (regla E.a) y no se hizo.

## 6. Consecuencia operativa para O1

1. **El descriptor fiel al protocolo es una razón contra epitelio normal**, no el percentil
   intra-lámina del B9. La razón trae **sus propios cortes** (1,5-2× y >2,5× en diámetro, §4.a) y
   por lo tanto **no tiene parámetro libre**, que es su ventaja real sobre el percentil.
2. **El percentil no se tira.** Es el resultado del B9 y el que hace la regresión obligatoria del
   pre-registro. Los dos se reportan juntos: el percentil como continuidad y la razón como fidelidad
   al protocolo.
3. **Hay que declarar el proxy de «epitelio normal».** No lo tenemos anotado. El candidato es
   `epithelial-cell` **fuera** de toda región anotada, y **es un proxy**: confunde «normal» con «no
   marcado». Se reporta con ese nombre en toda tabla.
4. **Además del tamaño hay que medir dispersión**, porque el eje que separa los tres scores es la
   variación (§2). El B9 midió tendencia central sobre núcleos elegidos por el patólogo; el CAP
   describe la población.
5. **Ninguna cifra en µm² se compara contra la literatura ni entre clases de HoVer-NeXt**, por el
   umbral de foreground por clase.

## 7. Preguntas que este documento NO contesta

Van al patólogo, o a Sebastián el martes. **No se rellenan.**

- **¿«Size» es diámetro o área?** §4.a. Adoptamos diámetro con argumento, no con cita.
- **¿Qué se hace cuando el pleomorfismo varía dentro del mismo carcinoma?** El CAP no lo dice
  (§5). Es exactamente lo que preguntó Sebastián.
- **¿Cuál es el epitelio normal de referencia en una lámina que es casi toda tumor?** El protocolo
  supone que hay epitelio normal a la vista; nuestras láminas anotadas no lo tienen marcado.
- **¿El ancla es el glóbulo rojo o el núcleo epitelial ductal normal?** El CAP los da como
  equivalentes; sobre nuestro material el orden de magnitud cierra (§4.b), pero no se verificó cuál
  usa el patólogo.

## 8. Qué no se afirma

- **No se afirma que el CAP sea la única fuente.** Es la que está en disco y la que usa el proyecto
  para las clases de las tareas ([[cap-fuente-clases-tareas]]). WHO 5th ed. y Elston-Ellis podrían
  traer la regla que falta en §5, y **no se consultaron**.
- **No se afirma que las marcas del patólogo sigan este protocolo.** El cruce del 8-sep dice que
  siguen la etiqueta de **pleomorfismo de la lámina** ([[marcas-grado-son-pleomorfismo-de-lamina]]),
  que es una tercera cosa: ejemplares elegidos para sostener un score ya decidido.
- **No se afirma que el proxy de epitelio normal sea epitelio normal** (§6.3).
- **La tabla del §4.b no es una medición de núcleos normales.** Son todos los epiteliales de cada
  lámina, tumorales incluidos, bajo el umbral de foreground de su clase.
