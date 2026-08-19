# El segundo factor del techo: las 177 detecciones contra las 26 marcas

> Medido el **19-ago-2026**, CPU post-hoc, sin GPU. Script:
> [scripts/cruce_hovernext_marcas.py](../../../scripts/cruce_hovernext_marcas.py).
> Salidas: `results/b8_hovernext_129741/cruce_marcas/`.
>
> `techo_atencion.md` midió el **primer** factor (cuánto deja pasar la máscara de atención) y
> dejó el segundo abierto porque no había con qué medirlo. La corrida del job 5008
> (`corrida_5008.md`) lo habilitó. Con esto la desigualdad del patrón **P2.a** queda cerrada
> sobre esta lámina.

## 1. El resultado

**HoVer-NeXt recupera 13 de las 26 marcas de `Mitosis` del patólogo: 50,0 %.**

El emparejamiento es **uno a uno** (húngaro): una detección no puede acreditar dos marcas.
Contar por «distancia mínima» daba 14 a 30 µm y 18 a 100 µm, siempre con **13 detecciones
distintas** — el exceso era la misma detección reusada.

## 2. El corte no decide nada

| tolerancia | 7,5 µm | 15 | 22,5 | 30 | 50 | 75 | 100 | 150 | 200 | 300 |
|---|---|---|---|---|---|---|---|---|---|---|
| aciertos /26 | 13 | 13 | 13 | **13** | 13 | 13 | 14 | 17 | 18 | 20 |

**Plano entre 7,5 y 75 µm**, que es un rango de **10×**. Se adopta 30 µm (el uso habitual en
detección de mitosis) y la elección es indiferente: no hay corte razonable que cambie el 13.
Por encima de 100 µm el número sube, pero 100 µm son unos seis núcleos de distancia y ahí el
emparejamiento ya no dice que sea el mismo objeto.

La distribución de distancias es **bimodal**, y por eso la meseta:

| percentil | p0 | p25 | p50 | p75 | p100 |
|---|---|---|---|---|---|
| marca → detección más cercana | 0,8 µm | **2,0 µm** | 14,1 µm | **114,6 µm** | 314,3 µm |

O acierta encima (mediana de 2 µm en el cuartil bajo) o no hay nada cerca. **Las 13 que fallan
no son «por poco»**: su detección más cercana está a **115 µm de mediana** (mínimo 23 µm). No
es un problema de tolerancia ni de centrado, es ausencia.

## 2.b Por qué falla la mitad: el detector está fuera de su dominio

§2 cierra en «es ausencia» y ahí se detenía. La explicación no hay que buscarla en el cruce,
está en el paper y la teníamos fichada desde el 14-ago (`papers_14_agosto/hovernext_estudio.md`).
Se escribe acá porque es la primera pregunta que hace cualquiera que vea el 13 de 26.

1. **La clase de mitosis se entrenó y se validó SOLO en colon, y esta lámina es de mama.**
   Textual del estudio §3.a: «los tres conjuntos que la tocan son CRC sin excepción: Lizard es
   colon, el dataset de mitosis son 48 ROI de 11 WSI de colon, y MitEval son 13 ROI de nueve WSI
   de resección de colon. **Cero mitosis medidas en mama.**» Ojo con la versión ingenua del
   argumento, que el mismo §3.a desactiva: para **segmentar y tipificar núcleos** en mama el
   modelo tiene número propio y bueno (mama sale 6ª de 19 tejidos, por encima del promedio). Lo
   que no tiene validación fuera de colon es **la clase mitótica**, que es justo la que usamos.
2. **Ni en su propio terreno es exhaustiva.** Supp. C.3 da para HNTiny, que es exactamente el
   checkpoint que corrimos (`lizard_convnextv2_tiny`), **recall 0,720** en mitosis sobre colon.
   Se le escapan ~28 de cada 100 en casa. Un 50 % fuera de su tejido deja de ser anómalo.
3. **Segundo eje de dominio, el escáner.** La razón de existir del desafío MIDOG es que los
   detectores de mitosis se caen al cambiar de escáner (`tareas_geometricas/midog_notas.md` §3.a).
   Nuestro `.bif` es Ventana. No está medido acá, pero es el segundo sospechoso y no se puede
   separar del primero con una lámina.
4. **La dirección del sesgo empeora la lectura, no la mejora.** El patólogo marca solo donde la
   evidencia es más clara ([[anotaciones-patologo-qupath]] trampa 2) ⇒ las 26 deberían ser **las
   fáciles**. Perder la mitad de las fáciles es peor que perder la mitad de una muestra
   representativa.

**Lo que NO está medido, y es lo barato que sigue:** si los núcleos fallados **fueron segmentados
y clasificados como otra cosa** (epitelio, conectivo) o si **no fueron segmentados**. Son dos
fallas distintas con arreglos distintos de costo muy distinto, y el cruce actual solo miró la
clase `mitosis`. Es contestable **sin GPU y sin volver a correr**: sobreviven
`129741_raw_256_inst.zip` (9,7 GB) y `129741_raw_256_cls.zip` (`corrida_5008.md` §2, gracias a
`--keep_raw`). **Ésta, y no el ensemble, es la continuación natural.**

## 3. Los dos factores juntos

`recall_fase3(K) ≤ min( techo_atencion(K) , detección )`, y además el conteo **real** de la
intersección, que es más informativo que la cota:

| K | % región | en máscara (CLAM) | detectadas | **ambas** | cota `min()` |
|---|---|---|---|---|---|
| 100 | 4,0 % | 12/26 | 13/26 | 8/26 | 12 |
| 189 | 7,6 % | 15/26 | 13/26 | 10/26 | 13 |
| **300** | **12,0 %** | 19/26 | 13/26 | **11/26** | 13 |
| 500 | 20,0 % | 23/26 | 13/26 | 12/26 | 13 |
| 1392 | 55,8 % | 26/26 | 13/26 | 13/26 | 13 |
| 2496 | 100 % | 26/26 | 13/26 | 13/26 | 13 |

> **La unidad cambió, y las dos tablas NO se cruzan.** `techo_atencion.md` cuenta **parches
> con marca (28)**; ésta cuenta **marcas (26)**, porque una detección se empareja con una marca
> y no con un parche. Son 28 parches para 26 marcas porque una marca puede caer sobre dos. Que
> algunas celdas coincidan (19 en K=300 en las dos) es **casualidad**: no leer una tabla como
> continuación de la otra.

Mammoth ordena mejor y llena la máscara antes (26/26 en K=750 contra 1392 de CLAM, coherente
con `techo_atencion.md` §2), pero **en la intersección los dos convergen**: 11/26 en el 12 % de
la región, 13/26 desde K=750.

**Tres lecturas:**

1. **El factor que manda cambió.** Desde **K=189 (7,6 % de la región)** la cota la fija la
   **detección**, no la máscara. `techo_atencion.md` concluyó que el filtro «no condena» la
   prueba, y era cierto; lo que ahora se ve es que **relajar el filtro ya no compra nada**: por
   generoso que sea el recorte, el techo se queda en 13 de 26.
2. **La cota `min()` es floja, y hay que decirlo.** En el 12 % de la región `min()` promete 13 y
   la intersección real es **11**. La cota sirve para condenar una prueba, no para
   presupuestarla.
3. **Chequeo de sanidad, aprobado.** Con la región entera (K=2496) los dos brazos dan
   exactamente **13/26**, que es el factor de detección solo. Si ahí no coincidieran, habría un
   error en el cruce.

## 4. ¿Son las mismas marcas las que se atienden y las que se detectan?

Sin evidencia de asociación. Percentil de atención de las detectadas contra las no detectadas:

| brazo | detectadas | no detectadas | U normalizada | p |
|---|---|---|---|---|
| CLAM | 96,6 | 91,1 | 0,651 | 0,200 |
| Mammoth | 96,3 | 94,2 | 0,604 | 0,383 |

Las dos van en la misma dirección (lo detectado se atiende algo más) y **ninguna llega a
significación** con 13 contra 13. Los dos factores se comportan como **aproximadamente
independientes**, que es lo que hace que la intersección observada (11 en K=300) quede cerca de
lo que predice la independencia (19/26 × 13/26 ≈ 9,5) y no cerca de la cota.

## 5. Qué NO se afirma

- **No hay precisión, y no se va a calcular.** En la región anotada hay **82** detecciones y
  **26** marcas; 13 coinciden. Las **69 restantes NO son falsos positivos**: las marcas son
  **positivos parciales** ([[anotaciones-patologo-qupath]] trampa 2) y el patólogo declaró que
  marca solo donde la evidencia es más clara. Cualquier precisión calculada acá está sesgada
  hacia abajo por construcción y no mide al detector.
- **El 50 % no es «el recall de HoVer-NeXt en mitosis».** El denominador son **las marcadas**,
  no las mitosis que hay en la lámina.
- **No se afirma nada sobre la otra región de escaneo.** Las 95 detecciones de arriba no tienen
  anotación contra la cual medirse.
- **Una lámina, un anotador.** Describe; no establece. El sign-off del patólogo sigue pendiente,
  y también quién es «GDT».
- **No compara brazos de HoVer-NeXt**: el de ensemble no se lanzó.

## 6. Qué habilita

- ~~El **brazo de ensemble** ahora tiene contra qué compararse: el mismo cruce sobre su salida da
  el Δ, y ése era el punto de correrlo.~~ **CORREGIDO el 19-ago (tarde): es falso, y hay que
  decirlo antes de que alguien gaste GPU en eso.** El brazo de ensemble son los tres folds de
  **PanNuke**, y PanNuke **no tiene clase de mitosis** (`out_channels_cls` 6 = 5 clases + fondo,
  contra 8 = 7 + fondo de Lizard-Mitosis; `auditoria_codigo.md` §«Diferencias entre los dos
  juegos»). Sobre su salida **este cruce no es computable**: no produce el objeto que se
  empareja con las marcas. El ensemble sirve para el inventario de tipos de núcleo y para
  calidad de segmentación, **no** para mover el 13 de 26, y PQ/bPQ/mPQ siguen sin ser
  computables contra el geojson ([[hovernext-encargo-17ago-diseno]]). **Correr el ensemble no
  contesta la pregunta de mitosis.**
- La **fase 3 restringida** queda dimensionada: en el 12 % de la región el máximo alcanzable son
  **11 de 26**, y el cuello es el detector. Si el objetivo es subir ese número, lo que hay que
  mover es la detección, no el tamaño de la máscara.
- Es el primer número del proyecto que mide **una herramienta de núcleos contra material de
  patólogo**, y el molde se reusa tal cual en las otras once láminas anotadas — coordinando
  antes con `sgaete` ([[anotaciones-patologo-qupath]] §10).
