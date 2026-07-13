# Sprint 7 (B7) — Correcciones del deck (Sebastián + Ernesto, reunión 13-jul-2026)

> Checklist accionable de las correcciones de la presentación, para el sprint 7 (la
> verán **Sebastián y Benjamín**). Se aplican SOBRE el deck B6 (15 slides: 11 mammoth +
> 4 magnif), generador `sprints/B6_sprint6/presentacion_viernes/generate_b6_deck.py`,
> convenciones en `convenciones_deck_b6.md`. Reglas de estilo duras: deck nativo
> python-pptx, guion HABLADO en prosa, **cero «—»**, **3ª persona sin nombres de guías**,
> caveat de honestidad en interpretabilidad. Fuente: prompt de entrada §2 + §3.

---

## 2.1 Migración de template (PRIORITARIO — pedido de Sebastián)

- [ ] Migrar la presentación a los **templates que Sebastián envió** y Ernesto subió a
      `sprints/B7_sprint7/` (todos de Sebastián, NO tocar/commitear los binarios):
      - `Modelo OncoMets Spatial V1.pptx/.pdf`
      - `Modelo OncoMets Spatial V1 Deep-LLM-V.pptx/.pdf`
      - `Plantilla.pptx/.pdf` (subido aparte).
- [ ] **Añadir la slide de RECAPITULACIÓN DE OBJETIVOS** con el layout de `Plantilla.pptx`
      (formato idéntico a los otros templates, pero esta trae ese layout de recap que
      falta en la nuestra). Adoptar ese layout.
- [ ] Copiar los **diagramas y figuras reutilizables** de los templates (son buenos,
      ilustran el formato de trabajo) para B7 y futuras presentaciones.
- [ ] Usar algunos diagramas como **inspiración para reconstruir las slides de la
      arquitectura del modelo**.

> **Decisión de enfoque pendiente (consultar a Ernesto antes de tocar el generador):**
> ¿re-basar `generate_b6_deck.py` sobre `Plantilla.pptx` (inyectar slides preservando
> branding/diagramas de Sebastián), o replicar el branding del template dentro del
> generador nativo? Se recomienda tras inspeccionar `Plantilla.pptx`.

## 2.2 Slide 7 (diagrama central de la arquitectura)

- [ ] Mejorar las notas del presentador para **seguir la pista de la variable X** en la
      imagen (dónde aparece, cómo se transforma paso a paso).
- [ ] Explicar **cuándo aparece X con subíndices `s,e`** (la salida `{z_j^{(k)}}^{S,E}`):
      indicar **qué representa cada subíndice** (y en general qué es cada subíndice de
      cada variable). Referencia de dimensiones: `preguntas_resueltas.md` §Q3 +
      `respuestas_preguntas_benjamin.md` §0 (E=experto, S=slot, H=cabeza, P=dim por cabeza).
- [ ] La respuesta **MoE vs PoE** debe quedar **dentro del hilo lógico** mientras se
      explica el pipeline (no como bloque aparte); leíble de corrido. Fuente:
      `respuestas_preguntas_benjamin.md` §Q4 (con el caveat: el paper NO menciona PoE).

## 2.3 Slides de mapas de calor por experto (slides 10-11)

- [ ] **Quitar/reformular** el supuesto "el experto 8 se fijó en epitelio" (y análogos):
      **eso NO lo sabemos** y puede confundir. Reformular a: *"cada experto se
      especializa en un patrón de tejido, nombrado por inspección visual; falta sign-off
      de patólogo"*. Caveat de honestidad ya documentado (§S3 hallazgos 13-jul,
      [[mammoth-interpretabilidad-objA]]).
- [ ] **Especificar claramente qué slides se usaron** para las pruebas (IDs concretos,
      de `meta.json`). Enlaza con el requisito por-tarea de `objetivos_sprint7.md`.

## 2.4 Nueva slide: cabezas / expertos / dimensiones / slots (explicación visual)

- [ ] Añadir una slide que **explique gráfica y visualmente**: qué son las **cabezas**,
      los **expertos**, las **dimensiones**, los **slots**, **qué se guarda en cada slot**
      y el rol de las **dos softmax** (dispatch sobre parches N / combine sobre los 300
      slots). Fuente lista: `preguntas_resueltas.md` §Q3.
- [ ] Debe **responder la duda de Sebastián**: preguntó si las 16 cabezas toman 16
      features distintos del parche y cada cabeza manda a su propio experto (→ 16
      expertos), pero **hay 30**. Aclarar: **16 cabezas × 30 expertos × 10 slots**; las
      cabezas corren en paralelo y **cada una tiene su propia mezcla de los 30 expertos**;
      NO es 1 experto por cabeza.

## 2.5 Reglas de estilo del deck (duras)

- [ ] **Cero guiones largos «—»**: quedan slides (las 1-11 de mammoth no se barrieron en
      B6) con doble guion que se nota IA. Eliminarlos todos. [[deck-estilo-sin-rayas-ni-palanca]].
- [ ] **Nunca diálogos** tipo *"queda pendiente decisión de tu guía"* (aparece en la
      última slide). Sacar.
- [ ] **Nunca nombres ni referencias a guías** (Benjamín, Sebastián): se omiten siempre.
      **Todo en 3ª persona.**
- [ ] (implícito) Evitar la palabra «palanca» ([[deck-estilo-sin-rayas-ni-palanca]]).

## Slides nuevas de magnificación (de §3 del prompt)

- [ ] Añadir una slide con la **matemática de área ↔ magnificación ↔ tamaño de parche**
      (µm/px, área física, píxeles) — Benjamín va a preguntar. Contenido en
      `contexto_magnificacion.md` §Q2.

---

## Orden sugerido de aplicación

1. Inspeccionar `Plantilla.pptx` → decidir enfoque de migración (con Ernesto).
2. Migrar branding/layout + añadir slide de recap de objetivos (§2.1).
3. Slide 7 (§2.2) + slide nueva cabezas/expertos/slots (§2.4) + slide matemática magnif (§3).
4. Slides 10-11 heatmaps (§2.3): caveat honestidad + IDs de slides.
5. Barrido de estilo (§2.5): «—», diálogos, nombres → cero, en TODO el deck.
6. Re-QA visual (rasterizar 1 vez, temprano — [[image-api-qa-limit]]).
