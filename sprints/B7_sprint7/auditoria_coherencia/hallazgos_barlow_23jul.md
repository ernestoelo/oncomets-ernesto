# Auditoría de coherencia — instalación de Barlow (23-jul-2026, noche)

> Alcance **acotado**: lo que tocó la sesión del 23-jul (noche, 3ª), es decir el eje
> tipográfico. No es una auditoría completa de los cuatro frentes.
> Antecedente directo: `hallazgos_sesion_template_valido_19jul.md` (T2).

## Resumen

| id | hallazgo | tipo | severidad | acción |
|---|---|---|---|---|
| A1 | La memoria decía «Barlow no está en el servidor (`fc-list` → 0)» | stale | media | matizado en el cuerpo + ADDENDUM |
| A2 | La misma memoria cerraba con «LibreOffice tampoco tiene Barlow, lo que rasterice es aproximado» | stale | **alta** | reescrita la línea de relacionadas |
| A3 | El acta del 19-jul repite el dato del `fc-list` en 0 | stale | baja | ADDENDUM fechado, sin reescribir |
| A4 | `DejaVu` en `pdffonts` se puede leer como defecto y no lo es | reconciliation | media | canónico + punteros |
| A5 | `pptx-qa-omml-libreoffice` sigue vigente | ok | — | sin cambios |
| A6 | Agentes y skills no afirman nada sobre fuentes | ok | — | sin cambios |
| A7 | El pie de la lámina 18 se lee como afirmación general | contradiction | media | **no accionado**, decide Ernesto |

## A1 — «Barlow no está en el servidor»

`deck-template-fuentes-embebidas.md` afirmaba en plano presente que la fuente no estaba,
citando `fc-list | grep -ci barlow → 0`. Desde esta sesión está instalada.

**Canónico**: el procedimiento vive en `presentacion_b7/fuentes_barlow.md`; la memoria
conserva el *porqué* tipográfico y apunta ahí.

**Fix**: el cuerpo pasa a «no **viene** instalada en el servidor (lo estuvo desde el
23-jul, ver ADDENDUM)». Se conserva íntegra la parte que **sigue siendo verdad y es la
que importa**: no está necesariamente en la máquina donde se presenta, que es lo que
obliga a construir sobre el `.pptx` del template.

## A2 — «lo que rasterice LibreOffice es aproximado»

El más peligroso de los tres, porque **desalienta un QA que ahora sí es válido**: una
sesión futura leería que no vale la pena mirar tipografía en el render local.

**Fix**: reescrita a «desde el 23-jul el rasterizado local **sí** sirve para juzgar
tipografía, con `FONTCONFIG_FILE` apuntando al workspace». Se preserva lo que no cambió:
el QA fino de OMML sigue yendo a PowerPoint.

## A3 — El acta del 19-jul

`hallazgos_sesion_template_valido_19jul.md:63` repite el dato. Es un **registro fechado
de una auditoría pasada**: reescribirlo falsificaría el acta, igual que no se reescribe
una hipótesis pre-registrada. Se le encadenó un **ADDENDUM fechado** que marca qué quedó
superado y qué sigue en pie. Mismo criterio con el que esa acta trató a
`plantilla-dos-cabeceras`.

## A4 — `DejaVu` en `pdffonts` no es un defecto

Barlow no trae cuatro glifos que el deck usa (`→` U+2192, `⟨⟩` U+27E8/9, `≡` U+2261 y el
guion duro U+2011), así que caen al fallback. Comprobado con
`fc-list ":family=Barlow:charset=<cp>"` y mirado rasterizado en las láminas 7 y 22:
indistinguible, y PowerPoint sustituirá igual.

Sin registrar, esto se convierte en un falso positivo garantizado la próxima vez que
alguien corra `pdffonts` sobre el deck. Queda en el canónico (`fuentes_barlow.md`, con la
tabla de glifos) y como puntero de una línea en `CLAUDE.md` y en la memoria.

**El contraste que sí es defecto**: `DejaVu` en los rótulos de un PNG de matplotlib, que
delata una figura generada sin registrar la fuente.

## A5 y A6 — sin cambios

`pptx-qa-omml-libreoffice` es sobre ecuaciones OMML en Cambria Math, ortogonal a la
sustitución de fuentes del cuerpo: sigue vigente tal cual. Ningún agente ni skill afirma
nada sobre fuentes (`grep` sobre `.claude/agents/` y `.claude/skills/` vacío), así que los
frentes 3 y 4 no requerían acción.

## A7 — Abierto, no accionado

El pie de la lámina 18 dice «Dos slots del mismo experto encienden regiones distintas»,
que se lee como afirmación general. La medición propia la contradice como regla:
`e13·s6` vs `e13·s5` da **+0.71**, y el §8 del handoff prohíbe explícitamente esa lectura
([[slot-unidad-de-morfologia]]). Lo medido es que **pueden** hacerlo, con `e28·s4` vs
`e28·s5` en **−0.56**.

No se tocó: Ernesto pidió no barrer láminas que no encargó, y el deck se presenta mañana.
Queda como decisión suya.
