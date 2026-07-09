---
name: humanizer-es
description: Reescribe prosa en español para que suene humana, sin tells de IA. Foco = guion del presentador y prosa de entregables OncoMets. Triggers — humanizar, sonar natural, quitar tells de IA, revisar el guion, pulir prosa, suena a IA.
---

# humanizer-es — Quitar señales de IA en prosa española

Editor de estilo que detecta y reescribe patrones típicos de texto generado
por IA para que la prosa suene a una persona. Adaptación al **español técnico
de OncoMets** de la skill `blader/humanizer` (MIT; ver Atribución al final).

## Cuándo aplica

- **Consumidor primario — el guion HABLADO del presentador.** La convención
  vigente ([[notas-presentador-guion-didactico]] + CLAUDE.md §"Notas del
  presentador") pide *prosa corrida, solo lo que se dice, sin frases
  artificiales ni coloquialismos, leíble de corrido*. Esta skill es el
  **procedimiento** para cumplir esa regla, no una lista de prohibiciones.
- **Consumidor secundario — prosa de entregables** (párrafos narrativos de
  `resultados.md`, texto de slides, correos, un README no-canónico).
- **Voz por defecto**: si no se da muestra, calibrar contra tus guiones B5 en
  `sprints/B5_sprint5/presentacion_b5/` para sonar a vos, no a Claude.

## Cuándo NO aplica (exclusiones — heredadas del original)

Para texto **enciclopédico, técnico, legal o de referencia, lo neutro y
llano ES la voz humana correcta**: no inyectar opinión ni primera persona ahí.
En concreto, NO tocar:

- **Docs técnicos estructurados**: `resultados.md` en sus tablas/métricas,
  READMEs canónicos minimalistas ([[readme-resultados-formato-minimalista]]),
  CLAUDE.md, memorias. El proyecto usa a propósito listas con inline-header,
  boldface y estructura — ahí NO son "tells", son la casa.
- **Código, configs, `.slurm`, changelogs, guías de migración** (donde el
  estilo diff/versionado es correcto).
- **Material citado, títulos, nombres propios o el término que se está
  discutiendo** (no el que se usa).
- **Números, IDs de job, ecuaciones, citas de papers**: se preservan literales.

Regla de oro del original: buscar **racimos** de tells, no uno aislado. Una
sola raya no es nada; raya + regla-de-tres + "vibrante panorama" + una
"Conclusión" genérica es una confesión.

## Nota de idioma y tipografía

De los 33 patrones del original, **~22 son portables** al español (contenido,
gramática, ritmo, retórica). Se **descartan** los específicos del inglés
(clusters de vocabulario inglés, pares con guion tipo *data-driven*,
Title-Case de encabezados — el español ya usa mayúscula de oración).

Los patrones de **tipografía** (rayas, negrita, emojis, comillas) aplican solo
a **entregables escritos**; en el **guion hablado son N/A** (se lee en voz
alta). Y **la raya (—) NO es constraint cero** como en el original: el estilo
de la casa (decks, CLAUDE.md) la usa como separador legítimo → acá se marca
solo el **abuso** como tell de ritmo, no se prohíbe.

---

## Proceso (loop de 4 pasos)

1. **Leer e identificar** cada instancia de los patrones de abajo.
2. **Borrador**: reescribir (no borrar) cubriendo todo lo que cubría el
   original. Que se lea natural en voz alta, con **largo de oración variado**,
   detalles concretos y construcciones simples (es/son/tiene), en el registro
   apropiado.
3. **Auto-auditoría** — preguntar: *"¿Qué hace que esto todavía suene a IA?"*
   Responder en 2-4 bullets con los tells que queden.
4. **Versión final** que los resuelva.

**Entregable**: borrador + bullets "todavía-suena-a-IA" + versión final +
(opcional) resumen corto de cambios.

## Calibración de voz (opcional)

Si se da una muestra de escritura propia, analizarla ANTES de reescribir:
largo de oraciones (cortas/largas/mixtas), registro (casual/académico), cómo
abre los párrafos, hábitos de puntuación, muletillas, estilo de transiciones.
**Igualar esa voz** en el rewrite en vez de imponer una nueva. Cómo pasarla:
inline ("humanizá esto; muestra: [texto]") o por archivo ("usá mi estilo de
[path]"). Sin muestra → registro técnico-neutro pero con ritmo hablado natural
(el guion lo dice Ernesto: primera persona "yo/nosotros" es correcta acá).

---

## PATRONES DE CONTENIDO

### 1. Énfasis indebido en significancia / legado / tendencias amplias
**Vigilar:** constituye un hito, marca un antes y un después, juega un rol
crucial/clave/fundamental, refleja una tendencia más amplia, sienta las bases
de, deja una huella, representa un cambio de paradigma, momento decisivo.
**Problema:** infla la importancia conectando algo puntual con un "tema mayor".
> Antes: El método marca un hito pivotal en la evolución de la patología computacional.
> Después: El método reduce el error de clasificación de 0.31 a 0.42 balanced-acc en la tarea de invasión.

### 2. Énfasis en notabilidad y cobertura
**Vigilar:** ampliamente reconocido, citado por múltiples fuentes, referente
del área (sin fuente concreta). Reemplazar por el hecho específico y sourceado.

### 3. Lenguaje promocional
**Vigilar:** destaca por, vibrante, rico en, en el corazón de, imponente,
revolucionario (figurado), de vanguardia, imprescindible, asombroso.
> Antes: CLAM se erige como un enfoque de vanguardia con un rendimiento asombroso.
> Después: CLAM clasifica a nivel de slide agregando parches con atención.

### 4. Atribuciones vagas / weasel words
**Vigilar:** los expertos señalan, diversos estudios, se ha demostrado que,
según diversas fuentes, es sabido que. **Muy relevante en charlas técnicas:**
citar el job/paper concreto, no una autoridad difusa.
> Antes: Diversos estudios sugieren que el agregador importa.
> Después: El anexo del Obj 5 (job 4179) mostró Δ −0.053 ± 0.026 en CDIS.

### 5. Secciones formulaicas "Desafíos y perspectivas futuras"
**Vigilar:** A pesar de estos desafíos, de cara al futuro, no exento de retos.
Reemplazar por el hecho concreto (qué falta, qué se midió), sin el arco
"obstáculo→triunfo".

## GRAMÁTICA Y RITMO

### 6. Gerundios de análisis superficial
**Vigilar:** ...reflejando, destacando, subrayando, contribuyendo a, lo que
pone de manifiesto, evidenciando. Cola de gerundio pegada para fingir hondura.
> Antes: Usa atención, destacando su capacidad de foco y reflejando el diseño MIL.
> Después: Usa atención para ponderar parches. El diseño es MIL débilmente supervisado.

### 7. Vocabulario "de IA" sobreusado (cluster español)
**Vigilar:** profundizar (en), aprovechar/apalancar, robusto, integral,
panorama, sinergia, crucial, fomentar, en aras de, cabe destacar, resulta
fundamental, en el ámbito de, tejido (figurado), abordar, potenciar.
Coocurren: si aparecen tres juntos, es señal.

### 8. Evitación de "es/son" (perífrasis de cópula)
**Vigilar:** se erige como, constituye, se posiciona como, ofrece, presenta
[en vez de "tiene"]. Devolver el verbo simple.
> Antes: El split constituye la verdad de campo y ofrece cinco folds.
> Después: El split es la verdad de campo y tiene cinco folds.

### 9. Paralelismos negativos y negaciones de cola
**Vigilar:** No solo... sino que también..., No se trata de X, sino de Y, no
es meramente... es... Reescribir como cláusula real.
> Antes: No se trata solo de la arquitectura, es el dato.
> Después: El cuello es el dato, no la arquitectura.

### 10. Regla de tres forzada
Agrupar todo en tríos para parecer completo.
> Antes: Ofrece rapidez, precisión y escalabilidad; innovación, impacto y valor.
> Después: Corre en una GPU y da métricas comparables al baseline.

### 11. Variación elegante (ciclo de sinónimos)
Sustituir el mismo referente por sinónimos rebuscados ("el modelo... la red...
el clasificador... el agregador...") cuando conviene repetir el término.

### 12. Rangos falsos
**Vigilar:** "desde X hasta Y" con X e Y que no están en una escala real.
> Antes: Cubre desde la génesis del dato hasta la danza enigmática de la atención.
> Después: Cubre extracción CONCH, agregación con atención y clasificación.

### 13. Voz pasiva / sujeto omitido
Pasiva-refleja que esconde al actor: "se preserva automáticamente", "no se
requiere configuración". Pasar a activa cuando aclara.
> Antes: Los resultados se preservan automáticamente.
> Después: El sistema guarda los resultados en `results/`.

## TIPOGRAFÍA (solo entregables ESCRITOS; N/A en guion hablado)

### 14. Abuso de raya (—) / guion
NO es constraint cero (la casa la usa). Marcar solo el **abuso rítmico**: varias
rayas por párrafo dando cadencia sales-y. Reemplazo según convenga: punto, coma,
dos puntos o paréntesis. Cazar también ` -- ` doble.

### 15. Abuso de negrita
Resaltar frases en **negrita** mecánicamente. En prosa narrativa, quitar; en
docs técnicos estructurados NO se toca (es la casa).

### 16. Listas con inline-header
`- **Título:** repetición del título`. En prosa, fundir en oraciones. En docs
técnicos del proyecto **está permitido** (exclusión de arriba).

### 17. Emojis
Decorar encabezados/bullets con emoji. Quitar (el proyecto ya los prohíbe en
notas). 

### 18. Comillas curvas
“ ” → " " en entregables donde importe el texto plano. Solo cuenta apilado con
otros tells (los editores auto-curvan).

## COMUNICACIÓN

### 19. Artefactos de chatbot pegados como contenido
**Vigilar:** Espero que esto ayude, ¡Por supuesto!, Tienes toda la razón,
¿Querés que...?, ¿Continúo?, avísame, aquí tienes un... Borrar: es
correspondencia de chat, no contenido.

### 20. Disclaimers de corte de conocimiento / relleno especulativo
**Vigilar:** a la fecha de..., hasta mi última actualización, si bien la
información es limitada..., probablemente [creció/estudió], se cree que. Decir
lo que NO se sabe, o cortar la oración; no disfrazar una conjetura de hecho.

### 21. Tono servil / sicofante
**Vigilar:** ¡Excelente pregunta!, tienes toda la razón, un punto excelente.
Ir directo al contenido.

## RELLENO Y HEDGING

### 22. Frases de relleno
- "con el fin de lograr" → "para"
- "debido al hecho de que llovía" → "porque llovía"
- "en este momento / en este punto del tiempo" → "ahora"
- "tiene la capacidad de procesar" → "puede procesar"
- "es importante notar que los datos muestran" → "los datos muestran"

### 23. Hedging excesivo
> Antes: Podría posiblemente llegar a argumentarse que quizás afecte algo.
> Después: La política puede afectar el resultado.

### 24. Conclusiones positivas genéricas
> Antes: El futuro se ve prometedor; se vienen tiempos emocionantes.
> Después: El próximo paso es correr Tier 0 sobre los .pkl ya en disco.

### 25. Tropos de autoridad persuasiva
**Vigilar:** la verdadera pregunta es, en el fondo, lo que realmente importa,
fundamentalmente, el meollo del asunto. Suelen introducir un punto ordinario
con ceremonia. Decir el punto directo.

### 26. Señalización / anuncios (muy relevante en el guion)
**Vigilar:** vamos a explorar, profundicemos en, sin más preámbulo, lo que
necesitan saber es, ahora veamos. Anunciar lo que se va a hacer en vez de
hacerlo. Decir la cosa directamente.
> Antes: Profundicemos en cómo funciona la atención. Esto es lo que hay que saber.
> Después: La atención pondera cada parche por su relevancia y suma los vectores.

### 27. Encabezados fragmentados (escrito)
Encabezado seguido de una línea que solo lo reformula antes del contenido real.
Borrar la línea de calentamiento.

### 28. Escritura anclada al diff
Doc/comentario narrado como un cambio ("esta función reemplaza el enfoque
anterior") en vez de describir la cosa como es. Excepción: changelogs / notas
de versión.

### 29. Remates fabricados / drama staccato
Cadena de fragmentos cortos para fabricar dramatismo. Una oración corta de
énfasis está bien; una ristra suena a ingeniería.
> Antes: Entonces llegó mammoth. Sin sesgo. Sin preferencia. Sin memoria. Todo cambió.
> Después: mammoth reemplaza la 1ª capa por un MoE, pero no movió la aguja.

### 30. Fórmulas de aforismo
**Vigilar:** X es el Y de Z, X se vuelve una trampa, X no es una herramienta
sino un espejo, el lenguaje de, la arquitectura de. Reemplazar por el reclamo
concreto.

### 31. Aperturas retóricas conversacionales
**Vigilar:** ¿Honestamente?, Miren, La cosa es así, La verdad es que, Seamos
sinceros — como gancho suelto antes de un punto ordinario. Una persona honesta
dice la cosa directamente.
> Antes: ¿Vale la pena? ¿Honestamente? Depende de cuánto lo uses.
> Después: Que valga la pena depende de cuánto lo uses.

---

## Qué NO marcar (falsos positivos)

Un humano limpio puede tocar varios patrones sin IA de por medio. NO son señal
por sí solos:

- **Gramática y estilo pulidos.** Pulcritud ≠ IA (hay editores y profesionales).
- **Mezcla de registros** casual/formal — suele indicar persona técnica.
- **Prosa "seca" o "robótica"** sin tells específicos: es escritura seca, no IA.
- **Vocabulario formal** que no esté en el cluster de §7. No aplanar "ostensible".
- **Una transición suelta** (además, sin embargo): solo cuenta apilada.
- **Comillas curvas solas** (auto-formato de editores).
- **Una raya sola** (muchos periodistas las usan).
- **Una sola oración corta enfática.** El tell es la ristra, no una.
- **Falta de citas** en sí misma.
- **Formato correcto y complejo** (plantillas producen output limpio).
- **Texto citado**: no reescribir el patrón dentro de comillas/títulos/ejemplos.

## Señales de escritura humana (preservar)

Cuando aparezcan, inclinarse a **dejar la prosa como está** — sobre-editar
destruye lo que la hace sonar a persona:

- **Detalle específico difícil de fabricar** (un número raro, un nombre, una
  anécdota). La IA redondea; los humanos acumulan especificidad.
- **Sentimientos encontrados / tensión no resuelta** ("creo que está bien, pero
  me incomoda y no sé bien por qué").
- **Referencias de época** (jerga, memes datables).
- **Decisiones editoriales en 1ª persona que el autor puede defender.**
- **Variedad de largo de oración.**
- **Digresiones, paréntesis, autocorrecciones genuinas.**

---

## Atribución

Adaptación al español de **[blader/humanizer](https://github.com/blader/humanizer)**
(MIT License), basada a su vez en
[Wikipedia:Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)
(WikiProject AI Cleanup). Copia de referencia read-only en
`clam_testing2/humanizer_reference/`. Esta versión recorta los patrones
específicos del inglés, adapta los ~22 portables al español técnico de OncoMets
y acota el alcance al guion del presentador y la prosa de entregables,
preservando las exclusiones de texto técnico/referencia del original.
