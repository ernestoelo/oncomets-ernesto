# Aviso a `sgaete` — DADO el 1-sep, en la reunión

> **ESTADO (4-sep-2026, sesión 48): ya no es un pendiente.** Ernesto informó que **el contenido
> de este aviso se lo dio a Sebastián verbalmente en la reunión pasada**, así que el mensaje
> escrito no hay que mandarlo. El documento se conserva como **registro de qué se comunicó y de
> las tres preguntas que quedaron planteadas** (qué cubre `hnx_win`, el esquema de salida, y si
> leer la rama predicha es deliberado); lo que sigue abierto son **las respuestas**, no el envío.
>
> Deja de aparecer como pendiente en los handoffs. Lo que sí sigue vivo, y es otra cosa, es la
> **coordinación de fondo**: repartir el terreno antes de escalar, que es lo que la última lámina
> del deck plantea en voz alta.


> Redactado el **1-sep-2026**, ampliado el **2-sep** y el **3-sep**. Es el aviso que el handoff
> arrastra sin dar **desde el 17-ago**, y ahora hay **cuatro** solapes y no uno
> ([[sgaete-yolo-mitosis-solapamiento]]): el tercero es que **vamos a leer su
> `attn_batch/json_out`**, así que la medición ya no sólo se parece a la suya, **consume un
> artefacto suyo** ([[clam-ensemble-json-out-atencion]]); y el cuarto, encontrado el 3-sep, es que
> sus jobs `5213 hnx_time` y `5249 hnx_win` corren **HoVer-NeXt con nuestro mismo checkpoint**
> (`lizard_convnextv2_tiny`) sobre **81 ventanas** de **nuestras mismas láminas**.
>
> **Por qué va antes de escalar y no después:** él tiene un pipeline propio de atención contra
> anotaciones (`anotaciones/atencion/`, 8 tareas, `overlays/`, jobs 4838/4839) que **mide
> exactamente** el eje que estamos por abrir. Si ya lo midió, el trabajo se duplica entero.
>
> Ernesto decidió **medir igual** en paralelo: el riesgo del solape es trabajo duplicado, no un
> resultado equivocado, y la medición es CPU y reversible.
>
> **Lo agregado el 2-sep** son tres cosas: que vamos a consumir su `json_out` y con qué alcance,
> el **esquema de salida** que proponemos para que su medición de tejido neoplásico y la nuestra
> crucen sin re-trabajo, y la **respuesta al tamaño de parche de HoVer-NeXt**, que es la pregunta
> que él hizo en la reunión del 1-sep.
>
> **Lo agregado el 3-sep** es la pregunta por `hnx_win`, y es la que más apura: el deck del 07/09
> propone el **punto caliente por ventana de área fija** como tarea del próximo período, y sus dos
> jobs corren eso mismo. **Preguntar antes de presentar esa fila**, o se lee como que proponemos
> algo que él ya está haciendo.

---

## El mensaje

> Hola Sebastián,
>
> Unas cosas cortas sobre las láminas anotadas por el patólogo, para no pisarnos. Las tres
> primeras son estado; las del final son preguntas, y la última es la que más me importa.
>
> **Una.** Corrimos HoVer-NeXt (pesos Lizard-Mitosis) sobre las **12** láminas con geojson, y
> cruzamos sus detecciones de mitosis contra las marcas del patólogo. De las **94** marcas
> reencuentra **26**, emparejando una a una con una tolerancia de 30 µm entre la marca y el
> centroide de la detección. La 129741, que era el caso que veníamos mirando, aporta **13 de esos
> 26**: o sea que era el mejor de los doce y no el típico. Sin ella el agregado baja a 19 %. No
> calculamos precisión ni F1 porque las marcas son positivos parciales.
>
> **Dos, y es lo que quería consultarte.** Vamos a medir si la **atención de CLAM** cae sobre los
> parches donde el patólogo marcó mitosis, en las doce láminas. Vi que en `anotaciones/` tenés un
> pipeline de atención contra anotaciones corriendo sobre 8 tareas, con overlays. **¿Estás
> midiendo esto mismo?** Si ya lo tenés, prefiero leer lo tuyo antes que rehacerlo. Y si vamos por
> caminos distintos, mejor saberlo ahora y comparar después.
>
> **Tres.** Para esa medición vamos a leer tu `clam_ensemble/attn_batch/json_out`, **sólo
> lectura**, sin escribir nada en esa carpeta: los `<slide>__<tarea>.json` de las 12 láminas, para
> `grado_histologico_mitotic_rate_pth_balance` e `invasion_carcinoma_gate_pth_balance`. Elegimos
> tu salida y no un mapa propio justamente para que los números crucen con lo que vayas a medir de
> tejido neoplásico. Dos cosas que anotamos al leerla, por si te sirven: el campo `patch_size` de
> esos JSON no coincide con la geometría del h5 (da 127 y 64 donde el paso entre coordenadas da
> 256), así que nosotros derivamos el parche del h5 y las `coords` sí cruzan exactas; y como el
> ensemble promedia los cinco folds, cada lámina estuvo en `train` en dos a cinco de ellos, así
> que lo declaramos como medición contaminada y corremos en paralelo un brazo con folds limpios.
>
> El esquema con el que vamos a publicar, para que lo tuyo y lo nuestro se junten sin re-trabajo:
> una fila por lámina y por brazo, con `slide, fuente, tarea, cabeza, universo, n_parches,
> n_marcados, auc, ic95_lo, ic95_hi, p_nulo, tier_fold, label`. Si preferís otras columnas u otros
> nombres, decime y uso los tuyos.
>
> **Y te contesto lo del tamaño de parche**, que quedó pendiente de la reunión. HoVer-NeXt tesela
> en **256 × 256 px a 20×**. El `--overlap 0.96875` del repo es un *stride*, no un solapamiento:
> el paso real es de **248 px**, se solapan 8 px que sirven de contexto y se descartan, y de cada
> tesela escribe el centro **248 × 248**. Nuestras láminas están a 0,465 µm/px y el modelo trabaja
> a 20× nominal (0,485 µm/px), así que **no hay remuestreo**: la tesela mide **119 µm de lado,
> 0,0142 mm²**, que es exactamente el tamaño físico de un parche de CLAM sobre la misma lámina.
> Enmascarar por parches de CLAM es, entonces, enmascarar a la granularidad de la tesela de
> HoVer-NeXt.
>
> **Y una pregunta suelta** de cuando miramos tu pipeline: al leer la atención, ¿tomás la rama de
> la clase **predicha** a propósito? Lo pregunto porque en nuestro material la elección cambia
> todo: sobre la misma lámina la rama de la clase **verdadera** dio 0,899 de AUC y la **predicha**
> dio 0,500 exacto. Si es deliberado me sirve entender el criterio.
>
> **Y una última, que es la que más me importa.** Vi que tenés corriendo `hnx_time` y `hnx_win`
> con `lizard_convnextv2_tiny` sobre ventanas de estas mismas láminas, que es el mismo checkpoint
> que usamos nosotros. **¿Qué cubre `hnx_win`?** Lo pregunto porque para el próximo período
> teníamos anotado el punto caliente mitótico, la ventana de área fija que maximiza el conteo por
> mm², y si eso ya está corriendo prefiero sumarme antes que abrirlo en paralelo.
>
> Gracias,
> Ernesto

---

## Las otras preguntas abiertas con él (NO van en este mensaje)

Se dejan aparte a propósito: mezclarlas diluye el pedido de coordinación, que es el urgente.

- **Sebastián habló de 30 láminas y hay 12.** Dónde están las otras 18.
- **Quién es «GDT»**, el sufijo de los doce geojson.
- **El paper de las 3 mm²: la referencia ya NO falta.** Es `MitosisDetection/AreaMitosis.md`, en
  su propio workspace: Ibrahim et al., *Defining the area of mitoses counting in invasive breast
  cancer using whole slide image*, **Modern Pathology (2022) 35:739-748**. La fila de la lámina 13
  **lleva la cita**. Lo que queda por preguntarle es sólo la **confirmación de que ése es el que
  citó**, porque atribuírselo es una inferencia razonable nuestra y no una confirmación suya
  ([[paper-3mm2-ibrahim-modern-pathology]]).
