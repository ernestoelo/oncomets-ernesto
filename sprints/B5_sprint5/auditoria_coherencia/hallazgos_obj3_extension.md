# Auditoría de coherencia — Obj 3 B5: hallazgos de la sesión de entrenamiento (19-jun, 2ª tanda)

> **Gatillo:** registrar los hallazgos críticos de la sesión que (a) lanzó el job 4387 (keep_slots
> tejido+invasión) y vio su progreso, (b) verificó un gotcha de eval, y (c) extendió keep_slots a las
> 2 binarias faltantes (job 4400, addendum §8 del prereg). Auditoría DOCUMENTAL, read-only sobre código.
>
> **Branch (workaround H):** hay **job 4387 corriendo + 4400 encolado**, ambos releen el working-tree
> compartido → **NO se cambia de branch** (mismo criterio que `hallazgos_obj3_keepslots.md`). Se edita
> solo docs/memorias/skills sobre `feat/mammoth-keepslots`; nada que los jobs lean (`scripts/train_dsmil.py`,
> `models_mammoth/`, `data/`, gates).

## Resumen

| id | hallazgo | tipo | sev | acción |
|---|---|---|---|---|
| G1 | `val_auc=nan` en training 3-clase es NORMAL — verificado vs baseline 4246 (310 épocas), checkpoint por val_loss, test_auc final OK; NO lo introdujo keep_slots | error (anti-falso-positivo) | **alta** | hecho validado en CLAUDE.md (eval) |
| G2 | doc stale: "Job 4387 ENCOLADO sin números" en CLAUDE.md L753 + progress L102/106 — 4387 ya **corre** (tejido 10/10), invasión en curso; + 4400 encolado (extensión §8) | stale | media | actualizar estado (aditivo, no reescribir veredictos) |
| G3 | extensión §8 a 3 binarias (job 4400) no está en memoria mammoth ni en progress | stale/project | media | addendum en `[[mammoth-investigacion-integracion]]` + progress + índice |
| G4 | principio nuevo: "completar la matriz de ablation por completitud/defensibilidad" = expansión de alcance de variante YA aprobada, NO 9.b "probarlo igual" | (nuevo) | media | 2º addendum a `[[meta-regla-decisiones-revisitadas]]` |
| G5 | feedback revelado: Ernesto prefiere correr la matriz comparativa COMPLETA antes que omitir pruebas por asunción ("no lo probé porque asumí que no mejoraría") | feedback | media | nueva memoria feedback + índice |
| G6 | operacional: `--nice=N` envía un job al FINAL de la cola (cortesía single-GPU); prioridad del cluster ≈ FIFO por orden de envío | (nuevo) | baja | una línea en skill `@slurm-submission` |

---

## G1 — `val_auc=nan` durante training 3-clase = NORMAL (anti-falso-positivo)

**Qué se observó:** el job 4387, en la tarea invasión (3 clases), loguea `val_auc=nan` en todas las
épocas. **Verificación (read-only):** el baseline mammoth-F invasión (job 4246) **también** lo logueaba
— 310 líneas `val_auc=nan` en `logs/eg_mammoth_patinv_4246.out`. El checkpoint se guarda por **val_loss**
(no val_auc), y el **test_auc final se computa bien** (el baseline 4246 cerró con macro-OVR AUC 0.80–0.86).

**Por qué importa:** es un **falso positivo de alarma** clásico — una sesión futura que vea `val_auc=nan`
en un run multiclase podría declarar el run roto o culpar a la variante en prueba (keep_slots). **NO** lo
introdujo keep_slots; es comportamiento del AUC de validación 3-clase en este codebase. Mantiene la
comparación apples-to-apples (baseline y brazo nuevo comparten el mismo nan en val).

**Canónico:** CLAUDE.md (hechos validados, junto al gotcha de `A_raw`/grad-sanity). Recurrirá (invasión,
mitotic y cualquier task multiclase) → CLAUDE.md (siempre cargado) en vez de memoria, para evitar redundancia.

## G2 — Stale: estado del job 4387

`CLAUDE.md` L753 (`ADDENDUM 19-jun` de Hallazgo 12): *"job 4387 encolado, sin números"*.
`progress/current.md` L102/106: *"Job 4387 ENCOLADO"*. **Realidad:** 4387 **corriendo** (~6h), **tejido
completo (10/10 runs, ambos brazos)**, invasión en curso (0/5). **Resultado sigue PENDIENTE** (regla 7:
sin veredicto hasta los 4 brazos × tareas). **Acción:** actualizar el estado de forma aditiva (4387
corre + tejido done + 4400 extensión encolado); **NO** tocar el "PENDIENTE" del veredicto.

## G3 — Extensión §8 (job 4400) no propagada

La decisión de extender keep_slots a carcinoma+cdis (prereg §8, commit `ae1e3c0`, job 4400 encolado con
`--nice` al final de la cola) está en el prereg pero no en la memoria mammoth ni en progress. **Acción:**
addendum fechado en `[[mammoth-investigacion-integracion]]` (4387 corre + 4400 extensión) + bloque en
progress + línea de índice. **NO** reescribir el cierre "8 tareas, 0 palancas" (sigue válido para la config
drop-in; la extensión es PENDIENTE).

## G4 — Principio nuevo: completitud ≠ "probarlo igual"

Esta sesión separó dos cosas que se parecen pero no son lo mismo:
- **"Variante no testeada"** (ya en el addendum 19-jun de `[[meta-regla-decisiones-revisitadas]]`):
  reabrir con una config que cambia el MECANISMO.
- **"Completar la matriz de ablation"** (NUEVO): extender una variante **ya aprobada** (keep_slots=True,
  reviewer GO) a **más tareas del mismo tipo** (las 2 binarias faltantes). No abre experimento nuevo, es
  **expansión de alcance**. El driver es **completitud/defensibilidad** (cerrar el espacio de config, tabla
  comparativa completa), **NO optimismo de efecto**. La línea que lo separa de 9.b "probarlo igual" =
  **pre-registrar la expectativa honesta** (acá: probablemente null/regresión, porque son desbalanceadas,
  Hallazgo 12) → un null **cierra**, un H1 sería positivo pre-registrado. **Acción:** 2º addendum conciso a
  `[[meta-regla-decisiones-revisitadas]]`. Canónico del caso: prereg §8.

## G5 — Feedback: completitud por sobre asunción

Ernesto (19-jun): *"me gustaría probarlo igual para tener una tabla comparativa completa con todos los
resultados y no tener que decir: 'no hice estas pruebas porque asumí que no mejorarían'."* → preferencia
de trabajo: ante una prueba de bajo-EV pero barata y pareada, **prefiere correr la matriz completa** (por
defensibilidad ante la audiencia/presentación) **antes que omitirla por asunción**, siempre que se
pre-registre la expectativa honesta (no como apuesta de mejora). **Acción:** nueva memoria `feedback`
`completitud-matriz-por-defensibilidad` + índice. Complementa [[procede-con-todo-el-plan-momentum]]
(momentum de ejecución) y se ata a G4.

## G6 — Operacional: `--nice` para enviar al final de la cola

Esta sesión envió el job 4400 con `sbatch --nice=100` para que quede al **final de la cola** y no le salte
el turno a jobs ajenos (nschiaff/sgaete). Verificado: prioridad resultante `...645`, la más baja de la cola.
La prioridad de este cluster es ≈ **FIFO por orden de envío** (4387=755 … 4392=750, decreciente), así que un
job nuevo cae último de todos modos; `--nice` lo **garantiza** explícitamente. (Evitado `--dependency=afterany`
por el riesgo de `DependencyNeverSatisfied` si el job-padre termina entre el commit y el sbatch.) **Acción:**
una línea en `@slurm-submission` (sección cortesía single-GPU). [[edicion-concisa-agentes-skills]].

---

## Fixes aplicados (19-jun, 2ª tanda)

- [x] G1 — CLAUDE.md core_utils: hecho validado `val_auc=nan` 3-clase normal
- [x] G2 — CLAUDE.md (ADDENDUM Hallazgo 12) + progress: estado 4387 corre / tejido done (aditivo, veredicto intacto)
- [x] G3 — addendum en `mammoth-investigacion-integracion` (4387 corre + 4400 extensión) + progress + índice
- [x] G4 — 2º addendum a `meta-regla-decisiones-revisitadas` (completitud ≠ probarlo igual) + índice
- [x] G5 — nueva memoria feedback `completitud-matriz-por-defensibilidad` + índice
- [x] G6 — una línea en skill `@slurm-submission` (--nice cortesía)

Criterios respetados: cierres/veredictos preservados como histórico (aditivo, no reescritura) → integridad
de pre-registración; ediciones aditivas a reglas/skills; cero edición a inputs de los jobs 4387/4400;
memorias bajo `~/.claude/` (excepción de containment conocida); branch sin cambiar (workaround H).
