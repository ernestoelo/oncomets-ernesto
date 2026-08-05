---
name: grilling
description: Interroga por rondas hasta llegar a un entendimiento compartido, antes de pre-registrar una hipótesis o tocar código. Triggers — grilling, interrogame, cuestioná el plan, estresá esta idea, antes de pre-registrar, qué me falta pensar.
---

# Grilling — interrogar hasta el entendimiento compartido

Entrevistar a Ernesto sin piedad hasta que no quede nada asumido en silencio. Es el paso
que va **antes** del pre-registro de la regla 9, no un reemplazo suyo: acá se descubre qué
hay que decidir, allá se escribe la hipótesis con su métrica y su dirección.

Adaptado de la skill `grilling` de mattpocock (`github.com/mattpocock/skills`, commit
`8b36d4f`), portada el 5-ago-2026. Lo que cambia respecto del original: los hechos se
buscan con las herramientas locales y **no** con subagentes, y la sesión aterriza en el
vocabulario de este repo (regla 9, Hallazgos, niebla).

## Cuándo aplica

- Antes de escribir un `prereg.md`, cuando todavía no está claro qué se pregunta.
- Cuando llega un encargo de reunión en una línea y hay que convertirlo en decisiones.
- Cuando una idea suena bien y hay que ver si sobrevive a que la aprieten.
- Cuando Ernesto pide explícitamente que le cuestionen algo.

**Cuándo NO**: si la decisión ya está tomada y documentada, o si lo que falta es ejecutar.
Interrogar sobre algo ya cerrado quema tiempo y contradice
[[verificar-antes-de-pedir-dato]].

## El mecanismo: árbol, frontera, rondas

Modelá el problema como un **árbol de decisiones**: cada decisión abre las que cuelgan de
ella. La **frontera** son las preguntas cuyos prerrequisitos ya están resueltos, o sea las
que se pueden hacer **ahora** sin adivinar respuestas que todavía no escuchaste.

1. Calculá la frontera.
2. Preguntá **toda la frontera en una sola ronda**, numerada, cada pregunta con tu
   respuesta recomendada.
3. Esperá las respuestas. No avances por tu cuenta.
4. Las respuestas empujan la frontera hacia afuera y desbloquean lo que dependía de ellas.
   Recalculá y hacé la ronda siguiente.

Una pregunta cuya respuesta depende de otra que sigue abierta **en esta misma ronda**
pertenece a una ronda posterior, no a esta. Es el error más común y el que hace que la
entrevista se sienta circular.

La sesión termina cuando la frontera queda vacía. No acciones nada hasta que Ernesto
confirme que llegaron a un entendimiento compartido.

### Formato de cada pregunta

```
❓ **Q1 — <título de la pregunta>**
<cuerpo: el contexto mínimo, y las opciones si las hay>

➡️ <tu recomendación, con el motivo en una línea>
```

Siempre va una recomendación. «No sé, decidí vos» no es una pregunta bien hecha: si de
verdad no tenés preferencia, decí cuál es el criterio que la resolvería.

## Los hechos los buscás vos

**Encontrar hechos es tu trabajo, nunca el de Ernesto.** Si una pregunta de la frontera
necesita un dato del entorno (qué hay en un CSV, cuántas slides tiene un split, qué línea
del código hace tal cosa, qué dice un `resultados.md`), lo buscás con `Read`, `Grep`,
`Glob` o `Bash` antes de preguntar. Nada de subagentes salvo que Ernesto los pida.

Lo mismo con las memorias y `CLAUDE.md`: antes de preguntar algo, verificá que no esté ya
contestado ahí.

**Las decisiones sí son de Ernesto.** Cada una se le pone adelante y se espera.

Buscar un hecho no bloquea la ronda: solo esperan las preguntas que cuelgan de ese hecho,
el resto de la frontera se pregunta igual.

## Dos cosas que hay que levantar apenas aparecen

- **La premisa no calza con el repo.** Si lo que dice el encargo contradice lo que está en
  el código o en los datos, se para y se muestra con evidencia, en vez de seguir
  entrevistando sobre una base falsa ([[surface-premise-discrepancies]]). Precedente: el
  encargo 2 del B8, donde «entrenar los slots» ya estaba hecho.
- **Es una decisión revisitada.** Si lo que se propone fue descartado antes (en un
  `ejes_futuros_*.md`, un apéndice «descartado», un veredicto NO-GO o una memoria), entra
  **regla 9.b**: la reapertura tiene que citar un hallazgo posterior que contradiga la
  premisa del descarte, con job ID y número concreto. Preguntalo en la primera ronda, no al
  final.

## Dónde aterriza la sesión

Cada cosa que salió del árbol va a uno de estos tres lugares, y el test para separarlas es
**si podés enunciar la pregunta con precisión ahora, no si podés responderla ahora**:

| Salida | Va a |
|---|---|
| Pregunta afilada y decidible | Un `prereg.md` con hipótesis primaria, alternativa y de regresión, métrica, subset y dirección esperada (regla 9 y 9.a) |
| Pregunta afilada pero todavía no accionable | La sección **Pendiente sharp** del `objetivos_sprintN.md` |
| Se intuye que viene, no se puede formular | La sección **Todavía sin especificar** del `objetivos_sprintN.md` |
| Queda afuera del sprint por decisión, no por falta de nitidez | La sección **Fuera de alcance**, que no gradúa |

No pre-cortes la niebla en pedazos del tamaño de una pregunta: es más gruesa que eso, y un
mismo pedazo puede graduar en varias preguntas o en ninguna.

## Errores que arruinan la sesión

- Contestarte tus propias preguntas y seguir de largo. La entrevista existe porque las
  respuestas son de Ernesto.
- Preguntar de a una y esperar. La ronda es toda la frontera junta.
- Mezclar en la misma ronda una pregunta y otra que depende de ella.
- Preguntar un dato que estaba en el repo.
- Terminar sin escribir nada. La sesión produce un artefacto: el pre-registro, o las
  secciones del mapa del sprint.
