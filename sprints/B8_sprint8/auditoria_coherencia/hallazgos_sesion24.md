# Auditoría de coherencia — cierre de la sesión 24 (23-ago-2026)

Alcance acotado: **lo que esta misma sesión escribió** (README del deck B8, `progress/current.md`
§Sesión 24, y las memorias `humanizer-es-skill`, `deck-qa-puntos-ciegos-chequeo` y
`deck-b8-dos-ejes-simil-mitosis` + su línea en `MEMORY.md`). No audita el resto del espacio.

## Resumen

| id | hallazgo | severidad | acción |
|---|---|---|---|
| H1 | «L5 −2» quedó stale: el fix del QA le sumó 10 palabras y hoy es **+10** | media | corregir el número en los 2 lugares |
| H2 | **La explicación del recorte es incorrecta**: no es cierto que las láminas sin contenido obligatorio llegaran a su presupuesto, ni que las que se pasan sean «exactamente» las de la lista | **alta** | reescribir el argumento en los 3 lugares con el reparto real |
| H3 | Consecuencia de H2: queda recorte disponible que los docs daban por cerrado | media | pasarlo a pendiente en el handoff |

## H1 — «L1 +3, L2 +2, L5 −2» tiene un número stale

`README.md:1466` y `progress/current.md:4416` citan **L5 −2**. Ese delta se calculó **antes** de
la pasada de QA visual, que le agregó a L5 la glosa de `score_N` (regla 13). Hoy L5 está en
**+10**. Los otros dos (L1 +3, L2 +2) siguen exactos.

Es el patrón de [[seccion-prospectiva-contradice-restricciones]]: el párrafo que resume se
escribió antes de los últimos fixes y no se volvió a derivar del dato.

## H2 — el argumento del recorte no se sostiene con los números (lo importante)

Los tres documentos afirman, con estas palabras o equivalentes: *«las láminas sin contenido
obligatorio llegaron a su presupuesto; las que se pasan son exactamente las que cargan la
lista»*. **Las dos mitades de la frase son falsas**, y el error se propagó a los mensajes de
commit `d21dac7` y `bdded21`.

**Reparto real del exceso**, tomando como «obligatorias» las diez láminas con pedido literal en
`correcciones.txt` + handoff §6 (L3, L4, L5, L6, L7, L8, L9, L11, L15, L17):

| lámina | ¿pedido literal? | palabras | objetivo | exceso |
|---|---|---|---|---|
| L1 | no | 153 | 150 | +3 |
| L2 | no | 182 | 180 | +2 |
| L3 | sí | 348 | 330 | +18 |
| L4 | sí | 348 | 330 | +18 |
| L5 | sí | 290 | 280 | +10 |
| L6 | sí | 348 | 300 | +48 |
| L7 | sí | 281 | 240 | +41 |
| L8 | sí | 260 | 200 | +60 |
| L9 | sí | 341 | 260 | +81 |
| L10 | no | 321 | 250 | +71 |
| L11 | sí | 394 | 280 | +114 |
| L12 | no | 557 | 380 | +177 |
| L13 | no | 329 | 280 | +49 |
| L14 | no | 381 | 280 | +101 |
| L15 | sí | 340 | 240 | +100 |
| L16 | no | 323 | 230 | +93 |
| L17 | sí | 428 | 250 | +178 |

- Exceso sobre láminas **con** pedido literal: **668 palabras** (57 % del total).
- Exceso sobre láminas **sin** pedido literal: **496 palabras** (43 %).

Dos errores concretos:

1. **L5 se citaba como ejemplo de lámina sin contenido obligatorio, y sí lo tiene.** Es la de los
   siete conteos del patólogo (61 polígonos con su reparto, 4799 parches, 163 marcados, 28 con
   mitosis), que es un pedido explícito. Usarla de evidencia invierte el argumento.
2. **Cinco láminas sin ningún pedido literal se pasan holgadamente**: L12 +177, L14 +101, L16
   +93, L10 +71 y L13 +49. Suman **491 palabras** de exceso que **no** están defendidas por
   ninguna corrección de Ernesto.

**Enunciado correcto:** la lista de intocables explica algo más de la mitad del exceso (56 %)
y **fija un piso real**, pero **no explica el resto**. Sí llegaron a su presupuesto las dos
láminas más cortas y sin figura (L1, L2); las demás no, con o sin pedido.

## H3 — queda recorte disponible, y los docs lo daban por cerrado

De H2 se sigue algo accionable que la redacción anterior tapaba: hay **~491 palabras**
recortables en cinco láminas **sin tocar un solo pedido de Ernesto**, lo que llevaría el guion de
5624 a ~5094 palabras (~39 min contra los ~43 de hoy). No es «el recorte no se puede
bajar más»: es «no se bajó más». Pasa a pendiente del handoff.

## Lo que la auditoría verificó y está BIEN

- **5624 palabras y 21,5 %** son correctos y consistentes en los tres documentos.
- Las notas del `.pptx` coinciden palabra por palabra con `guion_recortado_24ago.md` en las 17.
- Los tres defectos del QA (solape L17, nombre propio L15, guion largo L14) están descritos con
  su causa y su fix, y verificados en el deck regenerado.
- La línea de `MEMORY.md` y la `description` de `deck-b8-dos-ejes-simil-mitosis` quedaron
  consistentes con el estado nuevo (guion aplicado, sin placeholders).
- Los ADDENDUM son aditivos y fechados; no se reescribió ninguna hipótesis pre-registrada.

## Nota sobre los mensajes de commit

`d21dac7` y `bdded21` contienen la afirmación corregida por H2. **No se reescriben**: `main` es
compartido y ya tiene los commits ([[git-main-shared-pushes]], nunca `--force`). La corrección
vive acá y en los tres documentos canónicos, que es donde se consulta.
