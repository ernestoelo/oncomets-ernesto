# Auditoría de coherencia — Objetivo 3 B5 (mammoth keep_slots=True + slot_dropout)

> **Gatillo:** registrar el proceso/pruebas del Obj 3 (job 4387 encolado 19-jun) y verificar
> que las 4 frentes (CLAUDE.md, memorias, agentes, skills) estén coherentes con la **reapertura**
> del hilo mammoth. Auditoría DOCUMENTAL — read-only sobre código; **no toca** archivos que el job
> 4387 lee (`scripts/`, `models_mammoth/`, `data/`).
>
> **Decisión de branch (workaround H):** el skill pide branch nueva `chore/audit-*`, pero su propio
> guardrail prohíbe branch-switch con un job encolado/corriendo. Job 4387 está **encolado** y
> releerá el working-tree → **NO se cambia de branch**; la auditoría se hace sobre
> `feat/mammoth-keepslots`, editando solo docs/memorias (no inputs del job). Coherente: esta branch
> implementa Obj 3 y lo registra en la base de conocimiento.

## Resumen

| id | hallazgo | tipo | sev | acción |
|---|---|---|---|---|
| F1 | "Hilo mammoth CERRADO / 0 palancas" vive en 4 lugares y Obj 3 lo **reabre** (variante no testeada) | reconciliation | **alta** | addendum aditivo en los 4 (no reescribir el cierre) |
| F2 | `progress/current.md` stale: para en 5-jun (cierre mammoth) / 10-jun (PathPT activa); no refleja PathPT cerrado (11-jun) ni Obj 3 (19-jun) | stale | media | registrar Obj 3 como trabajo activo + nota PathPT cerrado |
| F3 | skill `@mammoth` dice `keep_slots` "variante posterior, no en la 1ª comparación" y no menciona `--mammoth_slot_dropout` | stale | media | nota concisa: Obj 3 ES esa variante (job 4387) + arg nuevo + puntero |
| F4 | memoria `[[mammoth-investigacion-integracion]]` cierra el hilo (L97-99); falta el addendum de reapertura | stale | media | addendum + actualizar línea de `MEMORY.md` |
| F5 | el reviewer estableció un principio reusable: "variante de config NO testeada ≠ decisión revisitada 9.b" | (nuevo) | media | addendum a `[[meta-regla-decisiones-revisitadas]]` |
| F6 | preferencia de trabajo revelada hoy: Ernesto asume el gate de gobernanza (no molestar a Sebastián para pruebas que maximizan mammoth) | feedback | media | nueva memoria feedback |
| F7 | CLAUDE.md L617 ("keep_slots=False preserva N") y skill L70 | no-action | baja | siguen correctos (default real); cubierto por addendum F1 |

---

## F1 — Reconciliation: el cierre del hilo mammoth se REABRE (variante no testeada)

**Qué dice cada fuente (todas afirman "cerrado / 0 palancas"):**
- `CLAUDE.md` Hallazgo 12, L742-743: *"Cierra el hilo mammoth: 8 tareas (3 microcalc + 4 patrón + 1 invasión), 0 palancas."*
- memoria `mammoth-investigacion-integracion.md`, L97-99: *"Cierra el hilo mammoth: 8 tareas pareadas k=5 ... 0 palancas; cuello = datos ... NO el patch-embed."*
- `MEMORY.md` índice, L13: *"HILO MAMMOTH CERRADO: 8 tareas pareadas k=5, 0 palancas."*
- `progress/current.md`, L25 + L34 + §Estado inmediato: *"Cierra el hilo mammoth (8 tareas, 0 palancas)."*

**Qué es correcto / reconciliación:** las 8 tareas testearon **un solo punto** del espacio de config
de mammoth — el drop-in `keep_slots=False`, `slot_dropout=0`. El veredicto "0 palancas" **sigue
siendo válido para esa config** y NO se reescribe (integridad de pre-registración + edición aditiva).
Obj 3 prueba una **variante arquitectónica materialmente distinta y NO testeada**: `keep_slots=True`
cambia el mecanismo (cardinalidad N→300 slot-tokens, salta la recombinación, cuello de botella
aprendido) + `slot_dropout` (regularizador del ruteo). Apuntada al **modo de falla pre-registrado**
(colapso a la mayoritaria, job 4246). **Reviewer GO-con-observaciones** (no 9.b estricta; ver F5).
**Resultado PENDIENTE** — job 4387 encolado, sin números (regla 7: no inventar resultados).

**Acción (aditiva, no reescribir):** en los 4 lugares, dejar el cierre como está y agregar un
addendum fechado: *"el cierre vale para la config drop-in testeada; Obj 3 (19-jun, job 4387) prueba
la variante no testeada keep_slots=True + slot_dropout — PENDIENTE."* Canónico del detalle:
`sprints/B5_sprint5/objetivo_3_mammoth_keepslots/prereg.md`.

---

## F2 — Stale: `progress/current.md`

**Qué dice:** la tabla del plan (L24-25) y §Estado inmediato (L34) cierran en 5-jun; la "Dirección
VIGENTE (10-jun)" pone a PathPT como prueba activa. **No refleja:** (a) PathPT CERRADO en
diagnóstico (11-jun, ya en CLAUDE.md Hallazgo 13 y memoria pathpt); (b) Obj 3 keep_slots (19-jun).

**Acción:** agregar bloque "act. 19-jun" registrando Obj 3 como trabajo activo (job 4387 encolado,
pre-reg + reviewer GO, brazos kst/kst_sd sobre tejido+invasión) y nota de una línea de que PathPT
cerró. Es el deliverable central de "registrar el proceso". No reescribir el histórico previo.

---

## F3 — Stale (concisa): skill `@mammoth`

**Qué dice:** L43 *"# --mammoth_keep_slots ← NO pasar en la 1ª pasada"*; §`keep_slots` (L48-53)
*"True ... Variante posterior, no en la primera comparación."*; no menciona `--mammoth_slot_dropout`
(arg nuevo); L70 el test valida solo "keep_slots=False preserva N".

**Acción (concisa, [[edicion-concisa-agentes-skills]]):** una línea en §keep_slots: *"Obj 3 (B5) ES
esa variante posterior — prueba keep_slots=True + el arg nuevo `--mammoth_slot_dropout` (default 0.0),
paired vs el baseline keep_slots=False (job 4387); pre-reg + reviewer GO en
`objetivo_3_mammoth_keepslots/prereg.md`."* + mención del arg + que el test CPU ya cubre la config real.

---

## F4 — Stale: memoria `[[mammoth-investigacion-integracion]]`

**Qué dice:** L97-99 cierra el hilo; L32 documenta que la integración vieja de Eduardo (en
clam_testing, READ-ONLY) tenía `keep_slots=True` **HARDCODEADO** pero nunca validado limpio; L50
nuestro port usa `keep_slots=False`. **Conexión:** Obj 3 valida limpiamente (paired, pre-reg) lo que
Eduardo había hardcodeado sin validar.

**Acción:** addendum fechado (reapertura Obj 3, job 4387, reviewer GO, conecta con el keep_slots=True
de Eduardo) + actualizar la línea de `MEMORY.md`. NO reescribir los veredictos previos.

---

## F5 — Nuevo principio reusable (del reviewer): variante no testeada ≠ revisitada 9.b

El reviewer estableció una distinción reusable: reabrir un eje cerrado con una **config NO testeada
que cambia el mecanismo** del mismo componente **NO** es "decisión revisitada" en el sentido de
regla 9.b (no exige citar un hallazgo-posterior-que-contradice), **pero** sigue exigiendo la carga de
regla 9 completa (H primaria/alternativa/regresión + métrica/subset/dirección) + reviewer + apuntar a
un modo de falla concreto. La línea que la separa de "vamos a probarlo igual" (prohibido por 9.b) es
justamente ese apuntado mecanístico. **Acción:** addendum a `[[meta-regla-decisiones-revisitadas]]`
+ línea `MEMORY.md`.

---

## F6 — Feedback: gate de gobernanza asumido por Ernesto

Hoy (19-jun) Ernesto decidió: *"No quiero molestar a Sebastián pero estoy seguro de que él y Benjamín
estarían interesados en que realice todo tipo de pruebas para sacar el máximo provecho a mammoth, así
que continuemos con todo."* → para experimentos exploratorios que **maximizan una prioridad heredada**
(mammoth = prioridad de Benjamín), Ernesto **asume** el gate "¿pedir co-firma a Sebastián?" y procede,
tratándolo como alineado con el interés del equipo. La co-firma queda como recomendable *a posteriori*
(para la presentación), no como bloqueante. **Acción:** nueva memoria `feedback`.

---

## Fixes aplicados (19-jun)

- [x] F1 — addendum aditivo en CLAUDE.md Hallazgo 12 (L746+) + línea índice MEMORY.md
- [x] F2 — progress/current.md: bloque "Dirección VIGENTE (19-jun)" (Obj 3 activo + PathPT cerrado)
- [x] F3 — skill @mammoth §keep_slots: nota concisa (Obj 3 = variante posterior + arg slot_dropout)
- [x] F4 — memoria `mammoth-investigacion-integracion` addendum 19-jun + línea índice MEMORY.md
- [x] F5 — addendum a memoria `meta-regla-decisiones-revisitadas` (variante-no-testeada ≠ 9.b) + índice
- [x] F6 — nueva memoria feedback `gobernanza-gate-cofirma-sebastian` + línea índice
- [—] F7 — sin acción (CLAUDE.md L617 / skill L70 siguen correctos; cubierto por F1)

Criterios respetados: cierres preservados como histórico (addendum, no reescritura) → integridad de
pre-registración; ediciones aditivas a reglas/skills; cero edición a inputs del job 4387; memorias
bajo `~/.claude/` (excepción de containment conocida).
