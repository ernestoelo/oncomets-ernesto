---
name: handoff
description: Comprime la conversación actual en un documento de handoff para que otra sesión de Claude Code la continúe sin pérdida de contexto. Triggers en español: "handoff", "pasar contexto a otra sesión", "preparar prompt para nueva sesión", "comprimir conversación", "cerrar sesión y abrir otra". Útil al cerrar un objetivo del sprint, antes de un experimento largo, o cuando el contexto está saturado y conviene reiniciar limpio.
argument-hint: "¿En qué se va a focalizar la próxima sesión? (1 línea)"
---

# handoff — Comprimir conversación en documento para sesión nueva

Convierte el estado de la conversación actual en un brief autocontenido que
otra sesión de Claude Code puede leer como primer mensaje y retomar el
trabajo sin re-derivar contexto. Reemplaza la práctica manual de escribir
prompts largos cada vez que se cierra una fase del sprint.

## Cuándo invocar esta skill

- Al cerrar un objetivo del sprint (e.g., "Objetivo 3 DSMIL cerrado, pasamos al 4").
- Antes de un experimento largo que va a saturar contexto (smoke tests + análisis + redacción).
- Cuando la sesión actual ya cumplió su misión y la próxima tiene un foco distinto.
- Cuando notás que estás repitiendo contexto en cada respuesta (señal de saturación).

## Cuándo NO invocarla

- Para una continuación trivial de la misma tarea (el contexto ya está cargado).
- Para tomar notas internas no destinadas a otra sesión (usá `progress/current.md`).
- Para documentar resultados (van a `sprints/<sprint>/<objetivo>/resultados.md`).

## Estructura obligatoria del handoff

Cada sección es REQUERIDA. Si una no aplica, marcar `n/a` con razón breve.

```markdown
# Handoff — <título corto descriptivo>

> Generado: <YYYY-MM-DD HH:MM>
> Sprint actual: <e.g., B4/Sprint 4>
> Branch al momento del handoff: <branch>
> Próxima sesión va a: <descripción del argumento o, si no hubo argumento, "ver §6">

## 1. Misión de la próxima sesión
<1-2 líneas, concreto>

## 2. Antes de hacer NADA, leer

Lecturas en orden:

1. `CLAUDE.md` (control center — reglas duras, workarounds A-G, hallazgos)
2. `progress/current.md` (estado vivo del sprint)
3. `~/.claude/projects/-media-administrador-Storage1-sdonoso-clam-testing2-oncomets-ernesto/memory/MEMORY.md`
   (memorias persistentes — al menos chequear el index)
4. <docs específicos del objetivo de la próxima sesión, paths absolutos o relativos al repo>

## 3. Reglas duras del proyecto (recordatorio)

Estas vienen de CLAUDE.md. NO se renegocian.

- **Workspace containment**: todo bajo `/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/`.
- **`clam_environ/` y `clam_environ/environ/` son READ-ONLY** (codebase + datos de Sebastián).
- **GPU SOLO vía `sbatch`** — nunca `python` directo en GPU (workaround B: `which python` base roto).
- **Preflight obligatorio** en `.slurm` de entrenamiento (workaround G).
- **Git**: NUNCA `--force` push; `git fetch` antes de pushear; `git branch --show-current` antes de cada commit.
- **Argumento antes de código** (regla 9 de CLAUDE.md): cualquier cambio en modelo/training va con hipótesis pre-registrada + métrica de éxito + reviewer OK.
- **Identidad git LOCAL**, nunca global (`user.email = ernesto.gamero@sansano.usm.cl`).

## 4. Estado al momento del handoff

- Rama: <branch>
- Último commit: <sha corto> <mensaje breve>
- Jobs SLURM activos: <ninguno / job ID + estado PD/R + cuándo se lanzó>
- Working tree: <limpio / N archivos sin trackear: [lista]>
- Cambios sin commitear: <ninguno / lista breve>
- Remoto sincronizado: <sí / N commits pendientes de push>

## 5. Decisiones cerradas (no reabrir sin razón nueva)

Lista de cosas con veredicto pre-registrado, resultados ya commiteados, o
acuerdos con el equipo (reuniones con Sebastián, Eduardo, Benjamín):

- <decisión> — referencia: <doc o commit>
- ...

## 6. Plan de trabajo sugerido

Orden estricto, no improvisar:

1. <paso 1>
2. <paso 2>
3. ...

PARÁS antes de: <acciones que requieren confirmación humana — sbatch, push, merge a main, etc.>

## 7. Skills sugeridas a invocar según la tarea

- `@slurm-submission` — si la tarea involucra GPU.
- `@environ-server` — si necesitás inventario del codebase/datos de Sebastián.
- `@csv-audit` — si introducís o auditás un CSV en el pipeline.
- `@dev-workflow` — si tocás estructura del repo o gitflow.
- `@harness` — si escalás a multi-agente.
- `@reviewer` (subagente) — OBLIGATORIO antes de commitear cambios a modelo/training.
- `@trainer` (subagente) — para entrenamientos end-to-end vía SLURM.

## 8. Lo que NO hacer

- <lista de antipatrones específicos para esta sesión>
- NO escribir/mover/borrar fuera de `clam_testing2/oncomets-ernesto/`.
- NO modificar nada bajo `clam_environ/`.
- NO mergear a `main` sin OK explícito.
- ...

## 9. Artefactos referenciados (NO copiados acá)

Si el handoff necesita hacer referencia a contenido extenso, listá los paths
en vez de pegar el contenido:

- Hipótesis pre-registrada: `<path>`
- Resultados previos: `<path>`
- Logs SLURM: `logs/<archivo>.out`
- Memorias relevantes: `<path>`

## 10. Contexto efímero relevante (no commiteado al repo)

Información de esta sesión que NO está en ningún doc del repo y que la
próxima sesión necesita. Ejemplos:

- "Sebastián confirmó por WhatsApp el 25-may que no_identificado se trata como negativo."
- "El otro Claude detectó que csv_balance es placeholder (mismas 328 slides)."
- "Reunión con Sebastián mañana 26-may donde define balanced_pth_100 final."

(Si esta sección crece, considerá si esa info debería migrar a una memoria
project o a `progress/current.md` antes del handoff.)
```

## Dónde guardar el handoff

**Por defecto**: `/tmp/handoff_<sprint>_<YYYYMMDD_HHMMSS>.md` (efímero, se
borra al reiniciar la máquina).

**Alternativa persistente**: `clam_testing2/oncomets-ernesto/.handoffs/`
(gitignored). Conviene si la próxima sesión es en otro momento del día y
querés sobrevivir un reinicio o desconexión. **Crear `.gitignore` del repo
con `.handoffs/`** si vas a usar este path.

**NUNCA** commitear handoffs al repo. Son artefactos efímeros entre
sesiones, no documentación del proyecto.

## Reglas de redacción

- **NO duplicar contenido de CLAUDE.md** ni `progress/current.md` ni de
  memorias persistentes. Referenciar el path; la sesión nueva las leerá.
- **NO copiar diffs o commits enteros**. Referenciar el SHA o el path del
  artefacto.
- **SÍ capturar contexto efímero** (decisiones de la sesión actual,
  conversaciones con el equipo, hallazgos no commiteados aún) — eso es lo
  que se pierde sin handoff.
- **Lenguaje**: español, técnico-pedagógico, mismo registro que usa Ernesto.
- **Longitud**: lo más conciso posible. Si el handoff supera 300 líneas,
  probablemente estás duplicando contenido de docs del repo.

## Redacción de información sensible

Antes de guardar el handoff, escanear y redactar:

- **NUNCA** incluir contenido de `~/.ssh/` (claves privadas, configs SSH).
- **NUNCA** incluir tokens de API, GitHub PAT, passwords.
- **OK** incluir paths absolutos del filesystem (son contexto operativo
  necesario para la sesión nueva).
- **OK** incluir nombres del equipo (Sebastián, Eduardo, Benjamín, Ernesto)
  cuando son contexto de decisión.
- **Email de Ernesto** (`ernesto.gamero@sansano.usm.cl`): OK incluir si es
  contexto de identidad git; redactar si no es necesario.

## Flujo de uso

1. Usuario invoca: `/handoff <descripción de la próxima sesión>`
   o pide en lenguaje natural: "hagamos un handoff para la sesión que sigue".

2. La sesión actual:
   - Recolecta el estado del repo (`git branch`, `git status`, `git log -1`).
   - Recolecta jobs SLURM activos (`squeue -u $USER`).
   - Identifica decisiones cerradas en la conversación reciente.
   - Identifica contexto efímero que no está commiteado.
   - Determina las lecturas obligatorias según el foco de la próxima sesión.

3. Genera el handoff con la estructura de §"Estructura obligatoria".

4. Guarda en `/tmp/handoff_<sprint>_<timestamp>.md` (o `.handoffs/` si el
   usuario lo prefiere).

5. Muestra al usuario:
   - Path del archivo generado.
   - Resumen de las secciones clave.
   - Instrucción concreta: "abrí sesión nueva de Claude Code en el repo,
     pegá el contenido de `<path>` como primer mensaje".

## Anti-patrones a evitar

- **Handoff genérico tipo "continuá donde quedamos"** — siempre especificar
  misión concreta y plan en §1 y §6.
- **Handoff que duplica CLAUDE.md** — si lo tenés que copiar, es porque la
  próxima sesión no va a leer CLAUDE.md, y eso no debería ser cierto.
- **Handoff con info sensible expuesta** — escanear ANTES de guardar.
- **Handoff commiteado al repo** — son efímeros; mantenlos fuera de git.
- **Handoff sin "decisiones cerradas"** — si no listás qué NO reabrir, la
  sesión nueva puede repetir debates ya resueltos (p-hacking conversacional).
