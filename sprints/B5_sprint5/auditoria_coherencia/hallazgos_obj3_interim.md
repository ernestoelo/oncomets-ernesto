# Auditoría de coherencia — integración INTERIM Obj 3 (job 4387)

> 20-jun-2026. Verifica la consistencia de los cambios documentales hechos al integrar el
> resultado **parcial** del job 4387 (invasión + tejido, 2 de 4 tareas) — con `/knowledge-audit`.
> Alcance: 5 archivos tocados. **Documental** (sin GPU, sin branch nueva: workaround H — job 4400
> encolado releerá el working-tree al arrancar). Rama `feat/mammoth-keepslots`.

## Resumen

| id | hallazgo | severidad | acción |
|---|---|---|---|
| O3i-1 | `mammoth-investigacion-integracion.md:112` (ADDENDUM 19-jun) decía "job 4387 CORRIENDO … invasión en curso" — contradice el bloque INTERIM 20-jun (4387 CERRADO) | stale | **CORREGIDO**: reencuadrado como "Lanzamiento 19-jun ~17h" (snapshot); el status vivo lo lleva el bloque 20-jun |
| O3i-2 | estado de 4400 (carcinoma+cdis) en los 5 archivos | OK | consistente: PD/no arrancó/PENDIENTE/placeholder en todos |
| O3i-3 | cierre prematuro del hilo / ADDENDUM | OK | ningún archivo cierra; todos dicen "ADDENDUM ABIERTO, falta 4400" |
| O3i-4 | consistencia numérica entre archivos | OK | C2 invasión −0.031±0.047 (4/5−), `presente` 0.434→0.516, slot_dropout 0.385, tejido null — idénticos en resultados.md / CLAUDE.md / progress / memoria |
| O3i-5 | integridad de pre-registración (prereg.md, regla 9) | OK | `prereg.md` intacto; los resultados se reportan en `resultados.md`, no se reescribió la hipótesis |

## Detalle

**O3i-1 (stale, corregido).** El bloque "REAPERTURA Obj 3" (19-jun) es un addendum dated; al
añadir el bloque "RESULTADO INTERIM 20-jun" debajo, la frase de status del bloque 19-jun quedó
contradiciendo al nuevo. Fix aditivo: la línea 19-jun pasa a describir el **lanzamiento** (hecho
histórico), el status vivo (4387 CERRADO / 4400 PD) vive en el bloque 20-jun. No se borró
contenido único.

**O3i-3 (clave del encargo).** Verificado que NINGÚN archivo declara el Obj 3 ni el hilo mammoth
cerrado por la variante keep_slots: CLAUDE.md §Hallazgo 12 ADDENDUM = "Resultado INTERIM … NO se
cierra el hilo todavía"; `resultados.md` = "ESTADO PARCIAL/INTERIM (2 de 4 tareas) … NO es el
veredicto final"; progress = "Resultado INTERIM … NO cierra el ADDENDUM"; memoria = "Hilo NO
cerrado … cierre cuando 4400 dé 5/5". El "HILO MAMMOTH CERRADO: 8 tareas" de MEMORY.md se refiere
al hilo **drop-in** (Hallazgo 12) y queda calificado en la misma línea por REABIERTO/INTERIM/
ADDENDUM ABIERTO → no es contradicción.

**Conclusión:** la base de conocimiento queda coherente en estado interim. El cierre del ADDENDUM
del Hallazgo 12 y la sección §6 de `resultados.md` (carcinoma+cdis) quedan explícitamente
pendientes del job 4400.
