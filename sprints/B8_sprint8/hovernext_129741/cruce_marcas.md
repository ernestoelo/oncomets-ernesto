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

- El **brazo de ensemble** ahora tiene contra qué compararse: el mismo cruce sobre su salida da
  el Δ, y ése era el punto de correrlo.
- La **fase 3 restringida** queda dimensionada: en el 12 % de la región el máximo alcanzable son
  **11 de 26**, y el cuello es el detector. Si el objetivo es subir ese número, lo que hay que
  mover es la detección, no el tamaño de la máscara.
- Es el primer número del proyecto que mide **una herramienta de núcleos contra material de
  patólogo**, y el molde se reusa tal cual en las otras once láminas anotadas — coordinando
  antes con `sgaete` ([[anotaciones-patologo-qupath]] §10).
