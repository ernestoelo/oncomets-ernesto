# ZoomMIL: estudio (familia B)

> Thandiackal K, Chen B, Pati P, Jaume G, Williamson DFK, Gabrani M, Goksel O, *Differentiable
> Zooming for Multiple Instance Learning on Whole-Slide Images*, **ECCV 2022**. arXiv:2204.12454.
> PDF en [`zoommil_thandiackal2022.pdf`](zoommil_thandiackal2022.pdf) (19 pág.).
> Código clonado en `clam_testing2/ZoomMIL_reference/` (HEAD `da7bb7f`, 3-nov-2022, 1.6 MB),
> **reference only**: solo lectura, NO al PYTHONPATH, NO import cruzado.
>
> **Bajados el 3-ago-2026.** Ficha: [`papers_mitosis.md`](papers_mitosis.md) §4.
>
> **Corrección de entrada, y es la principal razón por la que valía bajarlo:** los números
> **68.3 / 69.3** con la cadena **1.25× → 2.5× → 10×** que la ficha del 2-ago atribuía a
> CAMELYON16 son de **BRIGHT** (Tabla 2), no de CAMELYON16. En CAMELYON16 (Tabla 3) ZoomMIL usa
> **10× → 20×** y da **83.3 / 84.2**. La fuente secundaria estaba cruzada. Detalle en §4.

---

## 1. Qué propone, en una frase

Mirar primero toda la lámina en aumento bajo, **aprender** cuáles de esos parches merecen que se
los mire de cerca, y volver a mirar solo esos en el aumento siguiente; todo derivable de punta a
punta, así que la decisión de dónde hacer zoom se entrena con la sola etiqueta de la lámina.

## 2. Cómo funciona

**El bloque base es atención con compuerta** (Ilse et al. 2018), la misma familia que CLAM: pesos
`a_i` por parche vía `softmax(wᵀ(tanh(V·h_i) ⊙ σ(U·h_i)))` y una representación de lámina
`g = Σ a_i h_i` (ec. 2).

**Lo nuevo son tres cosas.**

**a) Dos atenciones por magnificación, no una (Dual Gated Attention).** En cada nivel hay
`GA_m`, que produce la representación de lámina de ese nivel, y `GA'_m`, **auxiliar**, cuya única
función es decidir qué parches se amplían. Separarlas evita que el mismo puntaje tenga que servir
para dos objetivos que no coinciden: clasificar bien acá y elegir bien para el nivel siguiente.

**b) Un top-K derivable.** Elegir los K parches de mayor atención es una operación discreta y no
tiene gradiente. Usan el método del máximo perturbado (Berthet et al. 2020, vía Cordonnier et al.
2021): se le suma ruido gaussiano a los pesos de atención, se resuelve el argmax para 100
muestras y se promedia (ec. 4), lo que da una matriz indicadora "blanda" con jacobiano definido
(ec. 5). En **inferencia** se usa el top-K duro. Es decir que entrenamiento e inferencia no son
el mismo grafo, y eso está declarado como los dos modos (I) y (II) de la Figura 2.

**c) La expansión al nivel siguiente.** Si el parche `i` de aumento bajo se selecciona, hay que
traer **sus hijos** en el aumento alto. Se hace con un producto de Kronecker entre la matriz de
selección y una identidad del tamaño del factor de subdivisión (ec. 6):

```
H̃_m' = (T_m ⊗ 1_m')ᵀ · H_m'
```

**El supuesto que esconde esa línea es el que más nos importa** (§5): que la grilla de parches
del nivel alto sea una **subdivisión anidada exacta** de la del bajo, con los hijos contiguos en
el orden del tensor.

**Preprocesamiento.** Parches de **256×256 en todas las magnificaciones** (tamaño de parche
constante, no proporcional), codificados con **ResNet-50 de ImageNet** con average pooling
adaptativo tras el tercer bloque residual. Mantener el parche constante en píxeles significa que
el **campo de visión en µm se achica** al subir de aumento, que es justamente lo que da contexto
distinto en cada nivel.

## 3. Qué mide y contra quién

Tres datasets, todos 40× nativo: **CRC** (1133 láminas colorrectales, Leica GT450), **BRIGHT**
(703 láminas de **mama**, no-canceroso / pre-canceroso / canceroso, Aperio AT2) y **CAMELYON16**
(399 láminas de ganglio). Media de 3 corridas con inicializaciones distintas. Los baselines son
MaxMIL, MeanMIL, SparseConvMIL, ABMIL, CLAM-SB y TransMIL.

## 4. Los números, ya verificados contra el PDF

**BRIGHT (Tabla 2), que es el dataset de mama y donde ZoomMIL gana:**

| Método | Weighted-F1 | Accuracy | TFLOPs | Tiempo (s) |
|---|---|---|---|---|
| ABMIL (10×) | 63.5 ± 2.7 | 65.5 ± 1.9 | 16.45 | 5.86 |
| CLAM-SB (10×) | 63.1 ± 1.7 | 64.3 ± 1.7 | 16.45 | 5.86 |
| TransMIL (10×) | 65.5 ± 2.8 | 66.0 ± 2.7 | 16.46 | 5.86 |
| ZoomMIL-Eff (1.25× → 2.5×) | 66.0 ± 1.9 | 66.5 ± 1.5 | 0.40 | 0.14 |
| **ZoomMIL (1.25× → 2.5× → 10×)** | **68.3 ± 1.1** | **69.3 ± 1.0** | 1.29 | 0.46 |

**CAMELYON16 (Tabla 3), donde queda a la par:**

| Método | Weighted-F1 | Accuracy | TFLOPs | Tiempo (s) |
|---|---|---|---|---|
| ABMIL (20×) | 83.2 ± 1.7 | 84.0 ± 1.3 | 39.12 | 13.92 |
| CLAM-SB (20×) | 83.3 ± 1.5 | 84.0 ± 1.3 | 39.12 | 13.92 |
| TransMIL (20×) | **83.6 ± 2.6** | **85.3 ± 1.9** | 39.12 | 13.92 |
| ZoomMIL (10× → 20×) | 83.3 ± 0.3 | 84.2 ± 0.4 | 14.94 | 5.32 |

En BRIGHT le saca **5.2 puntos de weighted-F1 a CLAM-SB** con **12.8× menos FLOPs**. En
CAMELYON16 no gana: queda 1.1 puntos de accuracy por debajo de TransMIL, con ~2.6× menos FLOPs.

## 5. El párrafo del paper que más nos importa, y no es una tabla

En CAMELYON16 los autores explican por qué bajaron el rendimiento relativo (pág. 9):

> *"As the metastatic regions can be extremely small, we set the lowest magnification to 10× in
> ours. Nevertheless, this still has an adverse impact on the performance."*

O sea: **cuando el objeto a encontrar es muy chico, el mecanismo de zoom se degrada**, y los
propios autores tuvieron que renunciar a empezar en aumento bajo. Eso no es una opinión nuestra
sobre el método, es el resultado del paper.

Nuestro caso es más extremo todavía. Una micro-metástasis en CAMELYON16 mide cientos de micras;
una figura mitótica marcada por el patólogo mide **16.7 µm** ([`README.md`](README.md) §2.a). Si
a 10× ya sufre con metástasis, el argumento de que un modelo de zoom encuentre mitosis partiendo
de aumento bajo se debilita mucho. Esto **refuerza** que B quede tercera para mitosis, y ahora es
un número del paper y no una inferencia nuestra.

## 6. El hueco #4 del handoff: ¿tolera una pirámide en µm/px?

La pregunta era si el mecanismo de agregación entre magnificaciones aguanta una pirámide
parametrizada en **µm/px físicos** en lugar de por `level`, que es lo que nuestro caso de cohortes
a escalas distintas necesita ([[cohortes-magnificacion-fisica]]).

**Respuesta, verificada en el código:**

**a) El factor de expansión NO está hardcodeado.** En `zoommil/models/zoommil.py:114-117` la
identidad del producto de Kronecker se dimensiona con
`int(num_features[1] // num_features[0])`, o sea con la **razón medida entre la cantidad de
parches de dos niveles**. Tolera razones arbitrarias mientras sean enteras. Lo que sí exige es
que la grilla sea una subdivisión exacta y que los hijos queden **contiguos** en el orden del
tensor; el preprocesamiento lo garantiza rellenando la imagen hasta un múltiplo de
`factor × patch_size` (`pad_image_with_factor`, `preprocessing.py:383`).

**b) Pero el preprocesamiento razona en magnificación, no en µm/px, y de la peor manera para
nosotros.** En `preprocessing.py:442-469`:

```python
if image.properties.get('aperio.AppMag') is not None:
    max_mag = int(image.properties['aperio.AppMag'])
    assert max_mag in [20, 40]
else:
    print('WARNING: Assuming max. magnification is 40x!')
    max_mag = 40
```

Lee el aumento nativo **solo de la propiedad de Aperio**, y si no está **asume 40× con un
warning**. Nuestra cohorte privada es **Ventana `.bif`**, que no expone `aperio.AppMag`: caería
en el `else` y se la trataría como 40× cuando está a **20×** (0.465 µm/px, medido). Es
exactamente el error silencioso de factor 2 contra el que advierte nuestra regla de proyecto.
HistAI, sin MPP confiable, cae en la misma trampa.

**Conclusión:** el **modelo** tolera la pirámide en µm/px sin cambios; el **preprocesamiento no**,
y habría que reescribirlo para elegir los niveles por µm/px objetivo en vez de por aumento
nominal. Es un cambio acotado y localizado, pero es obligatorio, no opcional. Como nosotros ya
producimos features en `.h5` por parche, en la práctica el preprocesamiento de ellos no se usaría:
se usaría el nuestro, con la condición de anidamiento del punto (a), que **nuestros `.h5`
actuales no cumplen** (son un solo nivel, sin jerarquía padre-hijo).

## 7. Qué nos sirve, y qué no

**Sirve.**

- **Es la única de las cuatro familias que gana en un dataset de mama** contra CLAM-SB, y por un
  margen no trivial (+5.2 weighted-F1 en BRIGHT). Eso es un argumento real, aunque para
  clasificación de subtipo y no para mitosis.
- La eficiencia es genuina y grande: 12.8× menos FLOPs que CLAM-SB en BRIGHT.
- Entrena **solo con etiqueta de lámina**, que es la que ya tenemos. No pide nada del patólogo.
- La forma del dato de entrada (features de parche en `.h5`) es la nuestra.
- La infraestructura multi-escala del B6 (`scripts/extract_multiscale_features.py`) existe y
  está sin usar, así que el costo de la pirámide ya está parcialmente pagado.

**No sirve, o hay que decirlo.**

- **Para mitosis el argumento se cae por donde el propio paper avisa** (§5): objetos chicos
  degradan el zoom.
- **En el privado no hay 40× al que hacer zoom.** Un método que aprende dónde ampliar no puede
  ampliar a una magnificación que el archivo no contiene. Esto vale para mitosis; para tareas
  donde el contexto importa más que el detalle, no aplica.
- Nuestros `.h5` no tienen la jerarquía padre-hijo que la expansión de Kronecker necesita.
- El preprocesamiento propio del repo asume Aperio y adivina 40× (§6.b).

## 8. Lo que este estudio no afirma

- Que ZoomMIL suba nuestra métrica en ninguna tarea. No se probó en nuestros datos.
- Que el +5.2 de BRIGHT se traslade a nuestras tareas de mama: BRIGHT es subtipo en 3 clases con
  703 láminas de un solo centro y un solo escáner, y nuestras tareas son puntajes de grado sobre
  cohortes mezcladas.
- Que la pirámide en µm/px resuelva el confundido entre cohortes. Es la vía natural para
  atacarlo, no una demostración de que funcione.

## 9. Preguntas para llevar

1. Si el interés real es el **confundido de magnificación entre cohortes** (§2.c del README) y no
   mitosis, ZoomMIL es el paper que justifica gastar el pipeline del B6. ¿Se separa ese objetivo
   del de mitosis, que es donde el método flaquea?
2. BRIGHT es mama y ZoomMIL le gana a CLAM-SB por 5.2 puntos. ¿Vale como argumento para probarlo
   en nuestras tareas de mama que **no** dependen de objetos chicos (invasión, CDIS)?
3. Si se prueba, ¿con qué escalas? Definirlas en µm/px y no en `level`, porque el código de ellos
   se equivoca justo en nuestro caso.
