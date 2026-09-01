# Aviso a `sgaete` — lo manda Ernesto

> Redactado el **1-sep-2026**. Es el aviso que el handoff arrastra sin dar **desde el 17-ago**, y
> ahora hay **dos** solapes y no uno ([[sgaete-yolo-mitosis-solapamiento]]).
>
> **Por qué va antes de escalar y no después:** él tiene un pipeline propio de atención contra
> anotaciones (`anotaciones/atencion/`, 8 tareas, `overlays/`, jobs 4838/4839) que **mide
> exactamente** el eje que estamos por abrir. Si ya lo midió, el trabajo se duplica entero.
>
> Ernesto decidió **medir igual** en paralelo: el riesgo del solape es trabajo duplicado, no un
> resultado equivocado, y la medición es CPU y reversible.

---

## El mensaje

> Hola Sebastián,
>
> Dos cosas cortas sobre las láminas anotadas por el patólogo, para no pisarnos.
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
