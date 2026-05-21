# Investigación DSMIL — Resumen ejecutivo

> **Objetivo 3, Sprint B4 — módulo MIL alternativo (propuesta: DSMIL).**
> Investigación documentada, **no implementación**. Insumo para la reunión
> con Sebastián y Eduardo y base técnica para implementar rápido si la
> reunión confirma DSMIL.
>
> Sesión read-only: cero modificación a `clam_environ/` y a
> `DSMIL_official_reference/`, cero GPU, cero SLURM.

## Documentos

| # | Documento | Contenido |
|---|---|---|
| 01 | [`01_paper_resumen.md`](01_paper_resumen.md) | Paper DSMIL (CVPR 2021) leído completo: arquitectura dual-stream, loss, SimCLR, datasets, hiperparámetros, ablations, limitaciones. |
| 02 | [`02_codigo_oficial_mapeo.md`](02_codigo_oficial_mapeo.md) | Código oficial `binli123/dsmil-wsi` (HEAD `80465ed`): `dsmil.py` línea por línea, mapeo paper→código, loop de training, discrepancias paper↔código. |
| 03 | [`03_comparacion_clam_dsmil.md`](03_comparacion_clam_dsmil.md) | Comparación arquitectónica CLAM vs DSMIL: pooling, supervisión de instancia, loss, multi-clase, memoria, punto de inserción. |
| 04 | [`04_riesgos_y_preguntas_reunion.md`](04_riesgos_y_preguntas_reunion.md) | Supuestos rotos, riesgos técnicos con severidad, y las 9 preguntas para la reunión. |

Fuentes: paper en [`../../../papers/dsmil_li2021.pdf`](../../../papers/dsmil_li2021.pdf)
(8 pp.); código DSMIL en `clam_testing2/DSMIL_official_reference/`
(read-only); código CLAM en `clam_environ/` (read-only); inspección real
de las features CONCH del servidor.

---

## Los 3 hallazgos más importantes

**H1 — CONCH ya cubre (y supera) el componente self-supervised de DSMIL.**
El paper atribuye al contrastive learning con SimCLR **≥14–16 % de
accuracy** (Tabla 3) — es una pieza grande del resultado, no un detalle.
Nosotros **no hacemos SimCLR**: usamos CONCH, un foundation model
vision-language de patología, mucho más fuerte que un ResNet18-SimCLR por
dataset. Medición de esta sesión: las features CONCH tienen norma L2
**uniforme** (≈22,65, std 0,01 entre parches y entre slides) → están
efectivamente normalizadas. Eso es el caso ideal para el instance
classifier lineal de DSMIL. **Cambia el entendimiento previo**: no
"perdemos" el componente #2 de DSMIL — lo tenemos cubierto de fábrica, y
del paper solo necesitamos transplantar el aggregator (componente #1).

**H2 — El instance scorer de DSMIL no entrena si no se lo supervisa
aparte.** El `argmax` que elige el parche crítico (`dsmil.py:52`) es no
diferenciable: no propaga gradiente al instance scorer `W_0`. `W_0` solo
aprende si hay una loss aplicada directamente a él (el `max_loss` de
DSMIL). **Consecuencia**: la idea de "mantener solo la loss de CLAM y
cambiar nada más" **no funciona tal cual** — dejaría el selector de
parche crítico congelado en su inicialización aleatoria. **Cambia el
entendimiento previo**: la decisión de loss pasa de "preferencia de
comparabilidad" a "requisito arquitectónico" (detalle en `04_` §B.1).

**H3 — DSMIL nunca fue evaluado en multi-clase desbalanceado.** Todos los
datasets del paper son **binarios** (Camelyon16, TCGA-lung como 2
subtipos, y los 5 datasets MIL clásicos). El paper *describe* el caso
multi-clase pero no lo *valida*. OncoMets sí es multi-clase y con
desbalance severo. **Cambia el entendimiento previo**: el "DSMIL es SOTA"
del paper **no se traslada automáticamente** a nuestro régimen — hay que
decirlo explícito y medirlo nosotros.

Hallazgos secundarios (en `02_`/`03_`/`04_`): DSMIL es **O(N)** en
memoria igual que CLAM (sin riesgo de OOM); los bags reales son de
**~1,4k–7,7k parches** (no decenas de miles); hay varias discrepancias
paper↔código (la `v`-net es Identidad por defecto, el softmax lleva
escala `/√128`, el lr real usa cosine annealing y no es constante).

---

## Los 3 riesgos más serios

**R1 🔴 — Régimen no validado (multi-clase desbalanceado).** DSMIL en
OncoMets opera fuera de la envolvente experimental del paper. Mitigado
**por diseño**: la integración conserva el bag classifier softmax + CE de
CLAM (salida multi-clase correcta) y `--weighted_sample`. Pero el
resultado es territorio no medido — enunciarlo en la reunión. (`04_` §A.2)

**R2 🔴 — Loss condicionada por H2.** No se puede "solo usar la loss de
CLAM": hay que conservar un término de supervisión del Stream 1 de DSMIL,
o el parche crítico nunca se aprende. Hay 3 opciones concretas de loss
(`04_` §B.1) — es la pregunta C.2 de la reunión y **debe cerrarse antes
de implementar**.

**R3 🟡 — SimCLR→CONCH es el supuesto más grande.** Expectativa positiva
(ver H1), pero el paper nunca evaluó DSMIL sobre features de un foundation
model. Se cierra barato con un smoke test temprano (5 epochs en la task
más chica, verificar que el instance scorer separa señal). (`04_` §A.1)

Riesgos **descartados con datos** esta sesión: inestabilidad del argmax
por norma de features (norma uniforme → 🟢) y OOM por bags grandes
(bags de miles, no de decenas de miles → 🟢).

---

## Las 9 preguntas para la reunión

Detalle y "qué desbloquea cada una" en
[`04_riesgos_y_preguntas_reunion.md`](04_riesgos_y_preguntas_reunion.md) §C.

1. ¿Preferencia de módulo: DSMIL, TransMIL, HIPT u otro?
2. Si DSMIL: ¿loss compuesta tipo CLAM o loss nativa de DSMIL? (ligada a
   R2 — no es solo preferencia).
3. ¿Eduardo implementa otro módulo en paralelo o convergemos a uno?
4. ¿Esperamos el dataset HISTAI completo o arrancamos con lo que hay?
   (hoy: 3.013 `.pt`).
5. ¿A qué magnificación se extrajeron las features CONCH?
6. ¿Hay anotaciones ROI para MicroCalcificaciones?
7. Si DSMIL se descarta, ¿siguiente alternativa preferida?
8. ¿Convención del equipo para nombrar runs, checkpoints y reportes?
9. ¿Cómo se reparte el tiempo de GPU entre Eduardo y Ernesto?

---

## Veredicto técnico

**DSMIL sigue siendo la mejor propuesta como módulo MIL alternativo.**
Nada en la investigación sugiere cambiar de candidato; varias cosas la
refuerzan:

- El swap es **arquitectónicamente limpio y barato**: cambia un solo
  bloque (el pooling), el resto del pipeline CLAM sobrevive intacto. Cero
  dependencias nuevas sobre `clam_latest`.
- DSMIL es **O(N)** confirmado — sin el riesgo de memoria O(N²) que
  cargaría TransMIL. Con bags reales de ~miles de parches, no hay ningún
  problema de GPU. Esto **amplía la ventaja de DSMIL sobre TransMIL**
  respecto a lo que sabíamos antes de la investigación.
- El argumento focal (atención relacional al parche crítico vs atención
  absoluta de CLAM) se mantiene intacto y bien fundado para
  MicroCalcificaciones y C.D.I. Necrosis.
- CONCH cubre el componente self-supervised del paper (H1): integramos
  DSMIL en su "caso fácil" de features.

**Pero la investigación afila dos condiciones que antes no estaban
explícitas:**

1. La integración **no es** "cambiar el pooling y nada más". Hay que
   resolver la supervisión del Stream 1 (R2/H2). Es un detalle de loss,
   no un bloqueante, pero hay que decidirlo en la reunión.
2. El resultado de DSMIL en OncoMets es **no validado por el paper**
   (R1/H3). La propuesta sigue en pie como hipótesis con argumento
   arquitectónico — exactamente lo que pide la regla 9 — pero se presenta
   como hipótesis a medir, no como mejora garantizada.

**¿Cambió algo que sugiera otra alternativa?** No. TransMIL sigue con su
incógnita de memoria; HIPT sigue exigiendo rehacer la extracción de
features. La comparación de
[`../alternativas_consideradas.md`](../alternativas_consideradas.md) no se
mueve. Si la reunión descarta DSMIL, la investigación no aporta un motivo
técnico para ello — solo lo aportaría una decisión de equipo (p. ej. que
Eduardo ya tome TransMIL, o que se priorice modelar correlaciones de
orden superior sobre el costo de integración).

**Recomendación**: llevar DSMIL a la reunión como propuesta firme, con
los dos 🔴 enunciados de frente (no esconderlos) y la pregunta C.2 de loss
preparada con las 3 opciones. Si se confirma, el scaffolding ya existe y
la implementación es rellenar TODOs guiados por `02_` y `03_`.
