# Las anotaciones del patólogo: qué son, y por qué no se pueden usar tal cual salen

> Sesión del 31-jul-2026. Todo CPU, lectura sobre lo ajeno, escritura solo bajo este repo.
> Script reproducible: [`scripts/alinear_anotaciones_qupath.py`](../../../scripts/alinear_anotaciones_qupath.py).
> Salidas: `parches_anotados_129741.csv`, `offset_129741.json`, `run.log`.

## 0. De dónde salió

Ernesto contó que está trabajando con un patólogo, que le mostró una herramienta donde se
ve la lámina con puntos marcados de distinto color según el tipo de lesión y con las zonas
de tumor encerradas, y que compartió esas etiquetas con él. Eso identifica el archivo que
la sesión paralela había encontrado el mismo día en el directorio de HoVer-Net de `sgaete`
y que quedó anotado como autoría desconocida ([[hovernet-ya-corriendo-sgaete]], pendiente
10 del handoff de las 14:45):

```
/media/administrador/Storage1/sdonoso/hover_net/129741.bif - GDT.geojson
```

La herramienta es **QuPath** (el geojson tiene el `objectType: annotation` y el bloque
`classification` con `name` y `color` que QuPath escribe al exportar). Los colores por
clase que describió Ernesto están literalmente en el archivo.

**Pendiente 10 queda resuelto en lo esencial**: es la anotación del patólogo. Lo que sigue
sin confirmar es el nombre detrás de «GDT» y si hay más láminas anotadas, y eso se pregunta,
no se deduce.

## 1. Qué contiene

61 polígonos, todos sobre la lámina **129741** de la cohorte privada. El inventario, y el
tamaño de cada tipo de marca medido contra el parche de 256 px con el que trabajamos:

| Clase | n | Área mediana | Como fracción de un parche de 256 px |
|---|---:|---:|---:|
| **Mitosis** | 26 | 1012 px² (219 µm²) | **1.54 %** |
| **Nucleos alto grado** | 14 | 1042 px² | **1.59 %** |
| necrosis | 6 | 10 027 px² | 15.3 % |
| Immune cells | 5 | 33 764 px² | 51.5 % |
| Tumor | 5 | 41 850 px² | 63.9 % |
| Tejido Adiposo | 2 | 1 068 091 px² | 1630 % |
| Negative | 2 | 6 591 379 px² | 10 058 % |
| Stroma | 1 | 217 746 px² | 332 % |

Las marcas de mitosis y de núcleo de alto grado son de **36 × 36 px**, o sea **16.7 µm** de
lado a 0.465 µm/px. Es el tamaño de una célula. Las otras clases son regiones de tejido.
Dicho de otro modo: el patólogo usó dos registros distintos en el mismo archivo, objetos
para lo celular y regiones para lo arquitectural.

**Las etiquetas de la lámina son coherentes con las marcas.** En los CSV del pipeline,
129741 tiene `tasa_mitotica = score_3` (el más alto), `cdis_grado_nuclear = grado_3_alto`,
`grado_general = grado_3`. Una lámina con 26 mitosis marcadas y 14 núcleos de alto grado es
exactamente eso. La anotación y el informe CAP no se contradicen.

## 2. El problema: las coordenadas no son las nuestras

Superponer el geojson sobre nuestros parches sin más da **3 de 61** aciertos, y contra la
máscara de tejido de la propia WSI da **1 de 61** (y ese uno es un `Negative`, o sea fondo).
De las 26 marcas de mitosis, **cero** caían sobre un parche extraído. No es que el patólogo
haya marcado fuera del tejido: es que el geojson está en otro origen.

El `.bif` es un Ventana con **dos regiones de escaneo** (`region[0]` 35840 × 30720 en (0,0)
y `region[1]` 34560 × 30720 en (0, 49920)), que openslide arma sobre un lienzo de
**39669 × 80640**. El lienzo es más ancho que la región, y esa diferencia es el
desplazamiento.

Se estimó por tres criterios, los dos primeros independientes entre sí:

| Criterio | Sin trasladar | Mejor | Dónde |
|---|---:|---:|---|
| (a) el centro de la marca cae sobre un parche extraído | 3/61 | **58/61** | dx [3096, 4440], dy [-808, 1816] |
| (b) el centro cae sobre tejido (máscara de saturación) | 1/61 | **58/61** | dx [3352, 4376], dy [-616, 1560] |
| (c) refinamiento por **área** del polígono | -0.75 | 56.80 | **dx 3832, dy 13** |

Las tres se cruzan. Y el número que predice el propio contenedor,

```
dx = level0.width - region[0].width = 39669 - 35840 = 3829 ,  dy = 0
```

cae a **3 px en x y 13 px en y** del óptimo empírico, con un score indistinguible (56.762
contra 56.799). Cuando el dato no separa dos candidatos y uno tiene explicación
independiente, gana el que la tiene: **se adopta dx = 3829, dy = 0**.

Los 3 de 61 que no alinean bajo ningún desplazamiento son los dos `Negative` y un
`Tejido Adiposo`, que es lo esperado: son fondo y grasa, y la máscara de saturación no los
cuenta como tejido.

Con el desplazamiento aplicado, **163 parches de los 4799** de la lámina (3.40 %) quedan bajo
alguna anotación: 48 de Tumor, **28 de Mitosis**, 27 de adiposo, 23 de inmune, 18 de necrosis,
**13 de núcleos de alto grado**, 12 de estroma.

### Por qué esto importa más allá de esta lámina

Cualquiera que superponga este geojson sobre coordenadas de openslide sin corregir obtiene
ruido con apariencia de señal, y no hay nada en el archivo que avise. Vale para nosotros y
vale para el pipeline de HoVer-Net, que trabaja en coordenadas de openslide. La regla
`dx = level0.width - region[0].width` es **derivable de las propiedades del archivo**, así
que se puede aplicar y verificar lámina por lámina, pero **está validada en una sola**: no
darla por buena en otra sin volver a correr el script, que reporta los tres criterios.

## 3. La restricción que el patólogo dejó dicha, y que cambia cómo se usan

Textual de lo que Ernesto transmitió: el cáncer cubre toda la zona, pero el patólogo
**solo marca donde se evidencia con mayor exactitud**, y después el modelo del software
identifica dónde se propaga en menor medida.

O sea que estas anotaciones son **positivos parciales, no una segmentación**. Un parche sin
marca no es un negativo: puede ser tejido tumoral que el patólogo no marcó porque ya había
marcado el ejemplo claro. Las consecuencias son concretas:

- **No se puede entrenar un clasificador de parche tratando lo no marcado como clase 0.** El
  ruido de etiqueta quedaría en la clase mayoritaria y el modelo aprendería a llamar negativo
  a tejido tumoral. Si se entrena a nivel de parche, el encuadre correcto es aprendizaje con
  positivos y no etiquetados, o usar las marcas solo como semilla.
- **Sí se puede usar para evaluar**, que es lo más valioso hoy y lo más barato: preguntar si
  los parches que el patólogo marcó reciben atención alta en nuestros modelos ya entrenados.
  Un positivo ignorado por el modelo es un error del modelo; un parche no marcado con
  atención alta **no** es un error, y esa asimetría es justamente la que la anotación parcial
  permite explotar sin sesgo.
- **La cota de lo que se puede afirmar es una lámina.** 61 polígonos, un caso, un anotador.
  Sirve para medir una hipótesis, no para establecer un resultado.

## 4. Lo que NO cierra

- **No cierra el sign-off de patólogo pendiente desde OBJ-A.** Ese pendiente es sobre los
  nombres de tejido que le pusimos a los expertos de Mammoth por lectura visual
  ([[mammoth-interpretabilidad-objA]], [[slot-unidad-de-morfologia]]). Esto es una lámina con
  regiones marcadas, no una revisión de nuestros mapas. El razonamiento completo está en
  `auditoria_coherencia/hallazgos.md` §B3 y sigue vigente.
- **No dice quién es «GDT»** ni si hay más láminas anotadas. Se pregunta.
- **No habilita nada de HoVer-Net.** El bloqueo de magnificación sigue igual: la corrida de
  `sgaete` es a `proc_mag=40` y esta lámina está medida a **0.465 µm/px con
  `objective-power = 20`**, que confirma en la lámina concreta lo que
  [[cohortes-magnificacion-fisica]] decía de la cohorte.

## 5. Lo que sí habilita, en orden de costo

1. **Medir si nuestros modelos miran donde mira el patólogo** (CPU, horas). La pregunta es el
   ranking de atención de los 28 parches de mitosis entre los 4799 de la lámina. **Ojo con el
   checkpoint**: 129741 cae en `val` en los splits de Sebastián pero en **`train` en los 5
   folds** del k-fold nuestro que usó Tier 0. Las dos opciones y qué cuesta cada una, en
   [`../tareas_geometricas/README.md`](../tareas_geometricas/README.md) §4.
2. **Pedir más láminas anotadas**, ahora con un pedido preciso: qué clases, cuántas láminas,
   y dejando dicho que sabemos que las marcas son parciales.
3. **Contrastar contra los mapas de expertos y slots** del B7, que es el uso que empuja el
   sign-off pendiente sin pretender que ya está resuelto.
