# Validación de la skill `humanizer-es` — sesión fresca (9-jul-2026)

> Test de la skill nueva (`.claude/skills/humanizer-es/`, commit `5d70218`) en una sesión
> SIN el contexto en que se creó, para verificar (1) auto-activación por `description`,
> (2) el loop identificar→borrador→auto-auditoría→final, y (3) que NO destroza prosa técnica
> ya limpia. Insumo: guion de la slide de magnificación B6 cargado de tells a propósito
> (borrador crudo, para ver *recall*). Muestra de voz: notas B5
> (`sprints/B5_sprint5/presentacion_b5/notas_presentador_guion.md`).

## Veredicto: PASS en las 3 propiedades. Sin ajustes al SKILL.md.

## Paso 1 — Identificar (tells, con nº de patrón)

- "vibrante panorama" → §3 + §7 · "se erige como" → §8 + §3 · "juega un rol crucial" → §1 + §7
- "Cabe destacar que" → §7 · "constituye un cambio de paradigma" → §1 + §8
- "no se trata solo… sino…" → §9 · "Diversos estudios sugieren" → §4
- "aprovechar / robusto / integral" → §7 · "ofrece" → §8 · "Profundicemos en" → §26
- "reflejando… holística que potencia" → §6 + §7 + §3 · "subrayando" → §6 · "en el corazón de" → §3
- "no… meramente… representa un antes y un después" → §9 + §1 · "abordar" → §7
- "De cara al futuro, y no exento de retos" → §5 · "sienta las bases para una sinergia" → §1 + §7
- "en última instancia, resultará fundamental… desbloquear el verdadero potencial" → §25 + §7 + §3
- "el futuro se ve prometedor / tiempos emocionantes" → §24 · "Espero que esto ayude" → §19
- "¿Querés que profundice…?" → §19 + §26

Racimo confirmado (promocional + weasel + gerundios + regla-de-tres + cierre genérico +
artefacto de chat en 4 párrafos): es confesión, no tell aislado.

## Paso 2 — Borrador

Para cerrar, hacia dónde sigue esto. Ya vimos que cambiar el modelo no mejoró los
resultados, así que el próximo paso apunta a otra cosa: a qué nivel de aumento mira el
modelo el tejido. Son tres frentes. El primero es trabajar a varias magnificaciones a la
vez: el bajo aumento da el contexto del tejido y el alto aumento da el detalle celular, y
la idea es combinar los dos. El segundo es darle más contexto espacial, con más parches y
una región más grande de la lámina. El tercero, el más ambicioso, es un enfoque tipo
agente sobre imágenes de alta resolución, en la línea de CPathAgent: el modelo navega la
lámina como lo haría un patólogo, decidiendo dónde y a qué aumento mirar. Esa es la
dirección para el próximo período.

## Paso 3 — Auto-auditoría ("¿qué sigue sonando a IA?")

- "apunta a otra cosa:" = micro-señalización (§26); colapsar.
- "el más ambicioso" = superlativo suave (§3); bajarlo o anclarlo al hecho.
- "decidiendo dónde y a qué aumento mirar" = gerundio de cola (§6); pasar a cláusula real.
- "tres frentes" NO es regla-de-tres forzada (§10): son los 3 bullets reales → se preserva.

## Paso 4 — Versión final

Para cerrar, hacia dónde sigue esto. Ya vimos que cambiar el modelo no mueve los
resultados, así que el próximo paso mira otra palanca: a qué nivel de aumento observa el
tejido el modelo. Son tres frentes. El primero es trabajar a varias magnificaciones a la
vez, porque el bajo aumento da el contexto del tejido y el alto aumento da el detalle
celular; la idea es combinar los dos. El segundo es darle más contexto espacial: más
parches y una región más grande de la lámina. El tercero es un enfoque tipo agente sobre
imágenes de alta resolución, en la línea de CPathAgent, donde el modelo navega la lámina
como un patólogo y decide dónde y a qué aumento mirar. Esa es la dirección para el próximo
período.

## Test de exclusión (precision)

- **Doc técnico estructurado** (tabla `balanced_acc`/`AUC` + path de split, estilo README
  canónico): FUERA DE ALCANCE → cero ediciones; número exacto y path literales. ✓
- **Prosa ya limpia** (slide 5 del guion B5): EN alcance pero sin racimo → se deja como
  está (disciplina de falso-positivo, §"Qué NO marcar"). ✓

## Convergencia (validación de voz)

La versión final converge casi palabra por palabra con la slide-final ya canónica del
guion B5 ("Slide final — Próximos pasos"), escrita con la voz de Ernesto. La skill empuja
prosa cruda-IA hacia la voz real del autor, no hacia una voz nueva. Es la evidencia más
fuerte de que la calibración de voz funciona.
