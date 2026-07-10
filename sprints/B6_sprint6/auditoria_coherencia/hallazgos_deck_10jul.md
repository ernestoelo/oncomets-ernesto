# Auditoría de coherencia — deck B6 ronda 2 (10-jul-2026)

> Gatillada tras la 2ª ronda de ediciones de Ernesto al deck del viernes
> (recap con estados, s7 figura grande + pipeline de dimensiones, s11 imágenes
> agrandadas, notas humanizadas). Alcance **scoped a lo tocado hoy** — no barre
> todo el repo. Documental, sin GPU, sin tocar modelo/training → se queda en
> `main` ([[git-trabajar-en-main-por-defecto]]). Complementa (no reemplaza) el
> `hallazgos.md` del 9-jul (Fable, skill humanizer).

## Tabla resumen

| id | hallazgo | tipo | severidad | acción |
|----|----------|------|-----------|--------|
| F1 | `progress/current.md` entrada del deck describe solo la ronda 9-jul (stale tras ronda 2) | stale | media | actualizar la entrada del deck |
| F2 | `deck-molde-fiel-referencia` no cubre los patrones de la ronda 2 (estados del B3, objetivos en infinitivo sin resultados, figura del paper grande+limpia con SUS variables, `dim_pipeline`) | gap | media | ADDENDUM a la memoria + línea en index |
| F3 | Assets nuevos (`check_verde.png`, `mammoth_fig2_arch.png`) gitignoreados | info | baja | ninguna (por diseño: `papers/presentations/` entero está gitignoreado, línea 60) |
| F4 | `convenciones_deck_b6.md` §7 | OK | — | ya documenta la ronda 2 (hecho esta sesión) |
| F5 | agentes `trainer`/`reviewer` y otras skills | OK | — | no tocados; sin acción |

---

## F1 — progress/current.md (stale)

**Dice** (§"Ejes vivos en paralelo"): el deck está "CONSTRUIDO y editado 9-jul…
Pendiente: verificación fina en PowerPoint + ensayo del guion".

**Realidad (10-jul)**: 2ª ronda aplicada — recap con marcadores de estado
(check verde / pill "En progreso") y **objetivos reescritos** (infinitivo, sin
resultados); s7 rehecha (figura del paper grande y limpia + pipeline de
dimensiones en bloques, notación de la figura); s11 con imágenes agrandadas;
notas del presentador humanizadas en las 11 slides. Sigue pendiente el QA en
PowerPoint + ensayo.

**Fix**: actualizar la entrada del deck en `progress/current.md`.

## F2 — memoria deck-molde-fiel-referencia (gap)

La ronda 2 aporta patrones durables NO cubiertos por la memoria:

1. **Marcadores de estado del B3** — al pedir "el ticket verde de bueno y en
   progreso como en `CLAM_Sprint_B3.pptx`", se **extrajo el check real** del
   `.pptx` de B3 (PICTURE blob 96×96 → `assets_branding/check_verde.png`) y se
   replicó el concepto "En progreso". Es **el mismo principio** que ya tiene la
   memoria (extraer el molde/asset real del deck de referencia, no reinventar).
2. **Recap de objetivos = enunciados en infinitivo, concisos, SIN resultados ni
   conclusiones** — Ernesto rechazó la 1ª persona ("Cerramos…", "Hoy traigo…") y
   los resultados ("ninguno movió la métrica", "el cuello de botella es el dato,
   no la arquitectura"). Los objetivos de una slide de objetivos van como
   objetivos (infinitivo), no como hallazgos; los hallazgos viven en las slides
   de contenido/cierre, no en el recap.
3. **Figura de un paper = grande, completa y limpia + referenciarnos en SUS
   variables** — quitó logo/título y **descartó nuestros callouts** que tapaban
   las etiquetas de la figura; pidió que el trazo y las notas usen la notación
   de la propia figura (W, x̄, s, Φ, W_low, cross-head concat, slide embed). Se
   armó un `dim_pipeline` (bloques variable+dimensión) al pie con esa notación.

**Fix**: ADDENDUM 10-jul a `deck-molde-fiel-referencia` (cabe: misma familia de
feedback de formato de deck) + refrescar la línea de `MEMORY.md`.

## F3 — assets nuevos gitignoreados (info, sin fix)

`git check-ignore` confirma que `check_verde.png` y `mammoth_fig2_arch.png` están
ignorados: `papers/presentations/` está **entero gitignoreado** (`.gitignore:60`),
igual que TODOS los assets del deck (logo, portada, fig1/fig3 — 0 archivos
trackeados en `assets_branding/`). El deck se construye desde assets **locales**
de este server; la fuente versionada es el **script** (`generate_b6_deck.py`) +
`convenciones_deck_b6.md`. No es regresión de esta sesión: es el diseño vigente.
**Implicación para el handoff**: una sesión fresca en ESTE server tiene los
assets; no viajan por git.

## F4/F5 — sin acción

`convenciones_deck_b6.md` §7 ya documenta la ronda 2 (esta sesión). Agentes y
demás skills no se tocaron.
