# Audit de coherencia — recortes del deck B5 + notas slides 7–cierre (26-jun-2026)

> Sesión documental (notas del presentador, sin GPU, sin tocar modelo/training). Audit acotado
> a lo que esta sesión tocó o dejó stale. Sin push (default: commits los hace Ernesto).

## Resumen

| id | hallazgo | tipo | sev | acción |
|----|----------|------|-----|--------|
| F1 | Header de `notas_presentador_guion.md` dice "slides 1–7 FINALIZADAS / 8–21 pendientes" | stale | media | FIX: actualizar a 1–15 + cierre; deck recortado |
| F2 | `convenciones_deck_b5.md` §7 lista la estructura de 21 slides (incl. las eliminadas) | stale | media | FIX aditivo: ADDENDUM con los recortes + puntero |
| F3 | `generate_b5_deck.py` aún construye las slides eliminadas | divergencia | baja | sin fix (LEGACY; deck se edita en OnlyOffice; ya flageado) |
| F4 | Preferencias de estilo nuevas reveladas (slides de resultados; no jerga no presentada) | feedback | media | FIX: regla concisa en §3.b + memoria |
| F5 | Memoria `magnificacion-cpathagent-proxima-direccion` añadida | ok | — | indexada, wikilinks válidos; sin acción |

## Detalle

### F1 — Header stale en la fuente de notas (stale)
`notas_presentador_guion.md` líneas 9–10: "slides 1–7 FINALIZADAS … Slides 8–21 pendientes".
Realidad tras esta sesión: **slides 1–15 + slide final de próximos pasos finalizadas**, y el deck
se **recortó de 21 a ~16 slides** (ver F2). Canónico = el cuerpo del propio archivo (slides escritas).
**Fix:** reescribir la línea de estado.

### F2 — Estructura de 21 slides stale en la convención (stale)
`convenciones_deck_b5.md` §7 describe las 21 slides, incluyendo **tasa mitótica, microcalc go/no-go,
div Cierre, cierre 3 ejes y CLAM + loss**, todas eliminadas el 26-jun. El recorte está documentado
en `notas_presentador_guion.md` (sección "Slide final — Próximos pasos") como intencional y con
"propagar al generador/§7 solo si se pide". Para no engañar a un lector futuro de §7, **fix aditivo**:
un ADDENDUM al inicio de §7 con los recortes y puntero a la nota estructural. NO se reescribe §7
(decisión de Ernesto: propagar al generador solo si lo pide).

### F3 — Generador aún arma las slides eliminadas (divergencia, baja)
`generate_b5_deck.py` sigue construyendo mitótica/microcalc/div-cierre/3-ejes/CLAM+loss. Es el
generador LEGACY (el deck no se regenera; Ernesto edita el `.pptx` en OnlyOffice). Ya está flageado
en la nota estructural. Sin fix; se propaga solo si Ernesto lo pide.

### F4 — Preferencias de estilo nuevas (feedback)
Reveladas esta sesión, refinan el guion hablado (convención §3.b / [[notas-presentador-guion-didactico]]):
- **Slides de resultados (tabla):** leer **por la columna del Δ pareado** de arriba a abajo;
  mencionar **solo bal_acc y AUC** (no varianza/colores en prosa); **atar al dataset** de la tarea;
  cerrar con una **conclusión breve del porqué**.
- **No introducir nomenclatura no presentada** (cazado: `slot_dropout`, "token") — definir o quitar.
- **Slide técnica que el presentador no domina:** primero explicársela a Ernesto, luego la nota;
  **referenciar los paneles de la figura** para que el guion siga la imagen.
**Fix:** sub-regla concisa en §3.b + nota en la memoria.

### F5 — Memoria nueva (ok)
`magnificacion-cpathagent-proxima-direccion` (próxima dirección = magnificación; lectura CPathAgent
semana del 29-jun). Indexada en `MEMORY.md`; enlaza [[insuficiencia-datos-ejes-investigacion]] y
[[sprint-cierre-trimestre-junio]]. Sin acción.

## Fixes aplicados
F1, F2, F4. (F3/F5 sin cambios.) Sin commit (rama destino no especificada → Ernesto commitea/pushea).
