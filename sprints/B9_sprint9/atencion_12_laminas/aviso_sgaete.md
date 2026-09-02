# Aviso a `sgaete` — lo manda Ernesto

> Redactado el **1-sep-2026**, ampliado el **2-sep**. Es el aviso que el handoff arrastra sin dar
> **desde el 17-ago**, y ahora hay **tres** solapes y no uno
> ([[sgaete-yolo-mitosis-solapamiento]]): el tercero es que **vamos a leer su
> `attn_batch/json_out`**, así que la medición ya no sólo se parece a la suya, **consume un
> artefacto suyo** ([[clam-ensemble-json-out-atencion]]).
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

---

## El mensaje

> Hola Sebastián,
>
> Tres cosas cortas sobre las láminas anotadas por el patólogo, para no pisarnos.
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
> Gracias,
> Ernesto

---

## Las otras dos preguntas abiertas con él (NO van en este mensaje)

Se dejan aparte a propósito: mezclarlas diluye el pedido de coordinación, que es el urgente.

- **Sebastián habló de 30 láminas y hay 12.** Dónde están las otras 18.
- **Quién es «GDT»**, el sufijo de los doce geojson.
- **El paper de las 3 mm²** que citó en la reunión: falta la referencia. El número entra al deck
  como objetivo a demostrar, atribuido a él, sin cita.
