# Auditoría de coherencia — cierre FINAL Obj 3 (mammoth keep_slots) + consolidación a main

> Fecha: 2026-06-21. Disparador: cierre del Obj 3 (matriz completa 4387+4400) y pedido de
> consolidar todo en main, eliminar `feat/mammoth-keepslots` y push.
> Estado GPU al auditar: **cola vacía** (sin jobs propios ni ajenos) → branch-switch/merge seguros
> (workaround H no se gatilla). Read-only → findings → fixes → commit → merge → push → cleanup.

## Contexto: lo ya propagado ESTA sesión (verificado coherente, sin acción nueva)

El cierre del Obj 3 (veredicto FINAL: `keep_slots=True` 0/4 supera a CLAM; matiz mecanístico
recupera el colapso a la mayoritaria; slot_dropout descartado; hilo mammoth completo 8+4=12 tareas,
0 palancas) ya se propagó a:
- `sprints/B5_sprint5/objetivo_3_mammoth_keepslots/resultados.md` (§0 FINAL + §6 + §6.3; §0-bis conserva el interim).
- `CLAUDE.md` Hallazgo 12 — ADDENDUM 19-jun pasó a **Resultado FINAL 21-jun (CERRADO)**.
- Memoria `mammoth-investigacion-integracion` (bloque RESULTADO FINAL) + línea de `MEMORY.md`.
- `progress/current.md` (sección Obj 3 → "CERRADO 21-jun").
- `results/README_experimentos_mammoth_environ.md` — sección keep_slots=True (minimalista).
Verificación: `grep` de marcadores interim/abierto en canónicos → **0 stale** (los 2 hits de
"Abierto" son "sprint abierto", falsos positivos).

## Resumen de hallazgos NUEVOS

| id | hallazgo | frente | sev | tipo | acción |
|---|---|---|---|---|---|
| F1 | `equipo-arquitecturas-mammoth-longnet`: mammoth presentado como "el candidato con respaldo"/"gana en 3 tasks" (tabla single-split de Eduardo 26-may) | memoria | media | stale | nota de cierre + puntero a [[mammoth-investigacion-integracion]] |
| F2 | línea de `MEMORY.md` de esa memoria repite "gana en 3 tasks" | memoria/índice | media | stale | actualizar la línea |
| F3 | `@mammoth` SKILL.md L54-59: Obj 3 en presente ("prueba", solo job 4387), sin veredicto | skill | baja-media | stale | una línea de cierre concisa |
| F4 | `progress/current.md` tabla plan fila 1b: "Cierra el hilo mammoth (8 tareas)" — ahora 12 (8 drop-in + 4 keep_slots) | progress | baja | stale | nota de la extensión keep_slots |
| F5 | `sprint-cierre-trimestre-junio`: "priorizar mammoth primero" / "tenía buenos resultados" — mammoth ya cerrado | memoria | baja | stale | puntero de cierre breve |
| F6 | `results/README_*_mammoth_environ.md` §Dataset: cuentas si/no de carcinoma y cdis **INTERCAMBIADAS** + n stale (333 vs 328) | results-doc | media | error (pre-existente) | corregir a cuentas verificadas live (n=328) |
| F7 | `.claude/agents/trainer.md` L26-28: "Obj 2, job 4243 **corriendo**" — 4243 cerró 4-jun; sin cierre del hilo | agente | baja-media | stale | actualizar a completado + puntero al cierre |

| id | reconciliación / nota (SIN acción) | frente |
|---|---|---|
| R1 | `CLAUDE.md` Hallazgo 12 cuerpo "Cierra el hilo mammoth: 8 tareas" vs ADDENDUM "8+4=12" → el ADDENDUM reconcilia aditivamente (integridad de pre-registración: no se reescribe el cuerpo histórico) | instrucciones |
| N1 | `CLAUDE.md` Hallazgo 9 "333 ident., pos 68/121/195" = registro histórico reunión 22-may; CSV live hoy 328 (carcinoma 68 / cdis 118 / tejido 192). Drift menor por filtrado de slides; se deja como registro de reunión | instrucciones |

## Detalle por hallazgo

### F6 (error, el más concreto) — README cuentas swapped
- **Qué dice** (`results/README_experimentos_mammoth_environ.md` §Dataset):
  `carcinoma: si 121 / no 212 (333)` · `cdis: si 68 / no 265 (333)`.
- **Verdad de campo** (CSV live `clam_environ/environ/csv/dataset_microcalcificaciones_en_*_label.csv`,
  verificado con `awk` esta sesión): carcinoma **68 si / 260 no**, cdis **118 si / 210 no**,
  tejido **192 si / 136 no** (n=328 cada uno). Canónico CLAUDE.md Hallazgo 9 confirma el ORDEN
  (pos 68/121/195 = carcinoma/cdis/tejido) → la línea de carcinoma y cdis está **intercambiada**.
- **Fix**: reescribir las 3 líneas con las cuentas live (n=328) → además alinea con `resultados.md` §6.
- Es **pre-existente** (README del 18-jun), no introducido por el cierre del Obj 3.

### F1/F2/F5 — mammoth ya no es "candidato prometedor"
La evaluación pareada MC-CV propia (12 tareas, 0 palancas) **supersede** la tabla single-split de
Eduardo (26-may) donde "ganaba en 3 tasks". Las memorias que lo presentan como candidato con
respaldo se actualizan con una **nota de cierre + puntero** a [[mammoth-investigacion-integracion]]
(canónica del veredicto). No se borra el contexto histórico (Eduardo, Benjamín lo priorizó): se
marca cerrado.

### F3/F4/F7 — referencias operativas en presente/stale
Skill `@mammoth`, `progress` y `trainer` describen el Obj 3/hilo mammoth como en curso. Edición
**aditiva y concisa** ([[edicion-concisa-agentes-skills]]): una cláusula de cierre + puntero, sin
reescribir la mecánica (que sigue siendo correcta y útil para correr la variante).

## Criterios aplicados
- Canónica del veredicto mammoth = memoria `mammoth-investigacion-integracion` + CLAUDE.md Hallazgo 12;
  el resto **apunta**, no duplica.
- Pre-registración intacta (resultados.md §0-bis y prereg.md no se tocan; CLAUDE.md cuerpo histórico no
  se reescribe — el ADDENDUM actualiza).
- Edición aditiva/concisa en skills y agentes.
- Contenido único nunca se borra (Eduardo/Benjamín/LongNet se preservan).
