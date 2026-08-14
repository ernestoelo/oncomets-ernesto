# Hoja 7. Jaroensri et al. El pipeline de dos etapas, publicado y medido

> Escrita el **13-ago-2026 (noche)** para la reunión del **viernes 14-ago**. Mismo formato que
> [`../papers_11_agosto/hojas_papers_nuevos.md`](../papers_11_agosto/hojas_papers_nuevos.md)
> (Hojas 5 y 6) y que [`../tareas_geometricas/hojas_reunion.md`](../tareas_geometricas/hojas_reunion.md)
> (Hojas 1 a 4): se lee en la reunión sin abrir nada más. La numeración sigue de esas seis.
>
> **Todo lo de acá está verificado contra el PDF y su Supplementary**, los dos en esta carpeta.
> Cómo se eligió y contra quiénes compitió: [`busqueda.md`](busqueda.md). El estudio a fondo:
> [`jaroensri_estudio.md`](jaroensri_estudio.md).
>
> **Qué NO es.** No es un pre-registro y no propone implementar nada. Regla 9: si esta rama
> avanza, va con hipótesis pre-registrada, métrica y dirección esperada, y `reviewer` antes de
> tocar código.

---

> Jaroensri R, Wulczyn E, Hegde N, … Liu Y, Steiner DF, Chen P-HC. *Deep learning models for
> histologic grading of breast cancer and association with disease prognosis*. **npj Breast
> Cancer 8:113 (2022).** DOI `10.1038/s41523-022-00478-y` · PMC9530224. **Acceso abierto.**
> Google Health. **Ojo:** Mercan, el de pleomorfismo de la Hoja 6, es `00488-w`; **este es
> `00478-y`**.

## Por qué este y no otro: es la forma del pipeline de Sebastián, publicada

Sebastián propuso que CLAM y su mapa de atención elijan dónde mirar, y que sobre los parches de
mayor atención corra un **segundo modelo especialista**. Este paper hace exactamente esa forma,
con otro selector:

```
WSI  ->  modelo de carcinoma invasivo (10×, parche 1024)  ->  MÁSCARA de invasivo
                                                                │
                                              (acá pondríamos la atención de CLAM)
                                                                v
                              ETAPA 1: tres modelos de PARCHE, uno por componente
                                mitosis (40×, 128 px)   pleomorfismo (40×, 1024 px)
                                              formación tubular (10×, 1024 px)
                                                                v
                              ETAPA 2: clasificador liviano de scikit-learn
                                              -> puntaje de LÁMINA 1 a 3
```

**Y ataca los tres componentes de Nottingham a la vez, que son nuestras tres etiquetas CAP:**

| Componente del paper | Task nuestra | Nuestro baseline, AUC a 5 folds |
|---|---|---|
| Recuento mitótico | `grado_histologico_mitotic_rate` | **sin entrenar todavía** |
| Pleomorfismo nuclear | `grado_histologico_pleomorfismo_nuclear` | 0,77 ± 0,046 |
| Formación tubular | `grado_histologico_diferenciacion_tubular` | 0,82 ± 0,062 |
| (los tres sumados) | `grado_histologico_grado_general` | 0,74 ± 0,046 |

Ningún otro candidato de la búsqueda cubre esa tabla. Y la etapa 2 es **regresión logística y
ridge**, no otro MIL: toda la parte cara vive en la etapa 1.

## Los números, y cuál es el baseline que gana

**El baseline contra el que gana es el patólogo humano**, que es la forma más fuerte de responder
al pedido de Ernesto («que aumente métricas») sin depender de comparar arquitecturas. Kappa
cuadrático, a nivel de lámina:

| | Mitosis | Pleomorfismo | Tubular |
|---|---|---|---|
| Acuerdo **entre patólogos** | 0,56 | 0,36 | 0,55 |
| Acuerdo **modelo con patólogo** | **0,64** | **0,39** | **0,69** |

**El modelo concuerda con los patólogos mejor de lo que ellos concuerdan entre sí, en los tres.**
Y su puntaje pronostica: sumado a las variables clínicas de base, el c-index sube de 0,74 a 0,76
(p = 0,036), y su recuento mitótico correlaciona con Ki-67 mejor que el del patólogo (0,47 contra
0,37, p = 0,002).

**Lo que hay que leer al lado, y conviene decirlo nosotros.** El artículo titula con kappa, pero
el Supplementary trae **balanced accuracy**, que es lo que nuestra política de eval exige
reportar: **pleomorfismo a nivel de parche está en 0,50**, con el trivial de tres clases en 0,333.
Su accuracy de 0,67 vive del desbalance. Es el mismo patrón que documentamos en
microcalcificaciones (Hallazgo 6). Y en detección de mitosis, el F1 de 0,60 es **precisión 0,76
con recall 0,50**: encuentra la mitad.

## Las tres preguntas nuestras

**1. ¿Cómo entra después del top-k de CLAM?** Nuestro parche es 256 px a 0,465 µm/px, o sea
**119 µm** de lado. Con los 20 parches de mayor atención:

| Rama | Campo del especialista | Inferencias por lámina | Cuánto ahorra el top-k |
|---|---|---|---|
| **Mitosis** | 32 µm, entra 14 veces en nuestro parche | **280** de un ResNet50 sobre 128 px | **muchísimo** |
| **Pleomorfismo** | 256 µm, más grande que nuestro parche | **20**, una ventana centrada por parche | algo |
| **Formación tubular** | 1 mm, ocho veces nuestro parche | una ventana ya cubre ~**70** parches nuestros | **casi nada** |

**Eso es un hallazgo de diseño, no un detalle:** el ahorro del pipeline de dos etapas depende de
la razón entre el campo del especialista y el parche del selector. Cuando el especialista mira más
grande que el selector, recortar por atención deja de servir.

**2. ¿Con qué supervisión lo entrenaríamos?** La etapa 1 pide **tres regiones de 1 mm² por
lámina, cada una anotada por 3 patólogos**. Suena caro, pero el matiz cambia el pedido: para
pleomorfismo y tubular la etiqueta de parche es **el puntaje de la región propagado a todos los
parches**, no anotación por objeto. O sea que lo que hay que pedirle al patólogo es «poné 1, 2 o 3
en esta región», no «marcá cada núcleo». La etapa 2 se entrena con la etiqueta de lámina que ya
tenemos del CAP. Y sus cajas de mitosis son de **16 µm** contra nuestras 16,7: nuestras marcas
evalúan un detector sin inventar tolerancias.

**3. ¿Qué métrica se movería, sobre qué tarea y en qué dirección?** Como dirección esperada, sin
umbral de pass/fail (regla 9.a): el candidato que Sebastián nombró es `pleomorfismo_nuclear`, hoy
en **0,77 ± 0,046** de AUC, y se esperaría un Δ pareado positivo y consistente en signo sobre los
mismos splits. **Pero la rama con mejor pinta técnica es formación tubular**, y no es la que él
nombró: es la única que nuestra cohorte privada alimenta sin ampliar (abajo).

## Los dos hallazgos que cambian nuestro plan

**1. El paper excluye las láminas a 20×, textual**, «in order to ensure availability of 40x» para
mitosis y pleomorfismo. **Nuestra cohorte privada está entera a 0,465 µm/px**, las 490 sin una
excepción. Puesto en cuentas:

| Rama | En nuestro privado | En TCGA (0,2325 µm/px) |
|---|---|---|
| Mitosis (32 µm a 0,25) | 69 px, **ampliar 1,86×** e inventar detalle | sin problema |
| Pleomorfismo (256 µm a 0,25) | 551 px, **ampliar 1,86×** | sin problema |
| **Tubular (1 mm a 1,0 µm/px)** | 2202 px, **se reduce**: sin problema | sin problema |

**Un grupo con los recursos de Google prefirió tirar datos antes que correr esas dos tareas a
20×.** Y eso **corrige el encuadre que traíamos del 11-ago**, donde pleomorfismo era la rama «a
favor» porque Mercan (Hoja 6) trabaja a 0,5 µm/px. Los dos papers son de mama, del mismo año y de
la misma revista, y eligen escalas distintas para la misma tarea: con Mercan la escala del privado
alcanza, con Jaroensri no.

**2. Probaron features de núcleo hechas a mano para pleomorfismo y no mejoraron.** Textual del
Methods, y lo atribuyen a la variabilidad de tinción y de aspecto celular en los casos de grado
alto. **Es evidencia en contra de la rama de NPKC-MIL (Hoja 5)**, que propone justamente 16
features de núcleo hechas a mano, y viene de un grupo con más datos. No la cierra, pero conviene
tenerla antes de gastar el costo de HoVer-Net.

## Y un tercero, que no es de este paper pero vale solo

De MIDOG 2025 (arXiv `2606.07368`, 365 casos y 12 tipos tumorales): **fuera de los puntos
calientes curados, la tasa de falsos positivos de los detectores de mitosis se triplica** (aumento
del 208 %). O sea que correr el detector sobre la lámina entera es justamente lo que no hay que
hacer. **Es el mejor argumento externo que tenemos para el diseño de dos etapas de Sebastián, y no
depende de qué paper se elija.**

## Lo que lo frena, sin maquillar

- **No publica pesos**: «have not yet undergone regulatory review». Lo público es el código de la
  etapa 2 y la ResNet50x1 de BiT. **La etapa 1, que es la que nos interesa, hay que entrenarla.**
- **Su supervisión no es la nuestra.** Tres regiones de 1 mm² por lámina, tres patólogos cada una,
  y para mitosis marcado exhaustivo dentro de la región, lo que les permite tratar **lo no marcado
  como negativo**. Nosotros tenemos 61 polígonos de una lámina y son **positivos parciales**: eso
  no lo podemos hacer.
- **Pleomorfismo es su componente flojo** (kappa 0,45 parche y 0,48 lámina, balanced accuracy
  0,50), y es justo la tarea que Sebastián quiere atacar. El propio panel de patólogos concuerda
  0,36, así que el techo es bajo para todos.
- **La sustitución de su máscara por nuestra atención no es neutra.** Su máscara es semántica
  («esto es tejido invasivo», AUC 0,95 contra anotación de patólogo); nuestra atención es un
  ranking de saliencia entrenado solo con etiqueta de lámina. A favor: sale gratis, y medimos que
  el ranking cae sobre las mitosis marcadas (AUC 0,890 ± 0,039 en los checkpoints que nunca vieron
  esa lámina). En contra: un top-k no es una máscara de tejido.

## No se afirma

Que Jaroensri suba ninguna de nuestras métricas: no está probado en nuestros datos, y el historial
del proyecto son cuatro ejes cerrados sin mejora. Que la atención de CLAM sea un reemplazo válido
de su máscara de invasivo: son objetos distintos y la sustitución está sin medir, con una sola
lámina y un anotador de respaldo. Que ampliar 1,86× el privado recupere el rendimiento: interpolar
hacia arriba no inventa detalle, y el paper directamente excluye el 20× en vez de evaluarlo. Que
el resultado negativo sobre features de núcleo cierre la rama de NPKC-MIL: es una frase del
Methods, no una ablación publicada.

**Nada de esto está implementado ni pre-registrado.** Regla 9.
