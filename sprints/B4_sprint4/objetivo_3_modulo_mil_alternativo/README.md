# Objetivo 3 — Módulo MIL alternativo

> Sprint B4. Hilo 3 de 4. **Implementación con argumento arquitectónico
> explícito** (regla 9 del proyecto, "Argumento antes de código").
> Wrapper-only sobre el codebase de Sebastián (`clam_environ/`) — no se
> duplica ni se modifica su código.

## Estado

**PROPUESTA — sujeto a confirmación en reunión con Sebastián y Eduardo.**

El módulo MIL alternativo todavía **no está decidido**. El candidato
actual es **DSMIL**, pero la elección final se cierra en la reunión
pendiente (decisión #6 de [`../README.md`](../README.md)). El nombre de
este directorio (`objetivo_3_modulo_mil_alternativo`, no `objetivo_3_dsmil`)
es intencionalmente genérico: comunica que es un objetivo abierto, no una
decisión tomada.

El argumento clínico/arquitectónico de DSMIL está en
[`propuesta_dsmil.md`](propuesta_dsmil.md). Las alternativas evaluadas
(TransMIL, HIPT, ablation de `B`) están en
[`alternativas_consideradas.md`](alternativas_consideradas.md).

## Candidato actual: DSMIL

DSMIL — *Dual-stream Multiple Instance Learning* (Li, Li & Eliceiri,
CVPR 2021). Por qué se propuso primero (detalle en `propuesta_dsmil.md`):

- **Ataca el cuello arquitectónico, no el sampling.** El attention
  pooling lineal de CLAM (`M = torch.mm(A, h)`) pondera cada parche de
  forma **independiente**; no modela relaciones inter-parche. DSMIL
  agrega una segunda rama que computa atención **relativa al parche
  crítico** — estructuralmente más adecuada para tareas focales como
  MicroCalcificaciones (señal positiva < 1% de la WSI).
- **Cambio mínimo y contenido.** Solo se reemplaza la rama de pooling.
  Se conservan features CONCH, bag classifier, instance branch y CSVs
  → la única variable experimental es el aggregator.
- **Costo de integración bajo.** El aggregator de DSMIL es PyTorch puro
  (sin dependencias nuevas sobre `clam_latest`; ver
  [`requirements_obj3.txt`](requirements_obj3.txt)).

## Qué se necesita confirmar en la reunión

Checklist — bloquea la implementación efectiva:

- [ ] **¿DSMIL, u otro aggregator?** TransMIL y HIPT quedaron como
      alternativas (ver `alternativas_consideradas.md`). Decisión #6 del
      sprint.
- [ ] **Dataset compartido y splits canónicos** definitivos (decisiones
      #1 y #2 del sprint) — necesarios para que el resultado de DSMIL sea
      comparable con el baseline de Objetivo 1 y la ablation de Objetivo 2.
- [ ] **`embed_dim` = 512 (CONCH)** confirmado y split de evaluación
      (`_pth_100` vs `_100`) — decisión #7.
- [ ] **4 tareas prioritarias** confirmadas (decisión #5).
- [ ] **Loss**: ¿se mantiene `--bag_loss ce --inst_loss svm` de CLAM (para
      que la única variable sea el aggregator) o se replica la loss nativa
      de DSMIL (BCE bag + BCE max-pooling)? Propuesta por defecto:
      mantener la de CLAM. Ver `propuesta_dsmil.md` §Riesgos.
- [ ] **División de trabajo Ernesto / Eduardo** (decisión #3) — quién
      toma este hilo.

## Qué está hecho (scaffolding de esta sesión)

Esta sesión produjo **scaffolding preparatorio**, no implementación
funcional. El scaffolding es independiente del módulo MIL específico:
sirve igual si la reunión confirma DSMIL o propone otro aggregator (solo
cambia el bloque de arquitectura).

- `README.md` — este archivo (estado, candidato, checklist de reunión).
- `propuesta_dsmil.md` — argumento clínico/arquitectónico de DSMIL,
  diagrama de integración, métrica de éxito predefinida.
- `alternativas_consideradas.md` — TransMIL, HIPT, ablation de `B`.
- `plan_integracion.md` — cómo se enchufa al pipeline existente.
- `requirements_obj3.txt` — dependencias adicionales (ninguna; ver archivo).
- `notas_readme_anterior.md` — contenido del README previo
  (`objetivo_3_dsmil/`) que no folió limpio a la nueva estructura.
- `scaffolding/` — skeletons no funcionales:
  - `dsmil_wrapper.py` — esqueleto de `DSMIL_CLAM_MB` y del aggregator
    dual-stream, con TODOs marcados. Compila/importa, `forward` levanta
    `NotImplementedError`.
  - `train_obj3.py` — esqueleto del training script (patrón de `main.py`
    de Sebastián, no copia).
  - `README_scaffolding.md` — mapa de qué hace cada archivo.

## Qué falta para implementación efectiva (post-reunión)

1. **Confirmar el módulo** en la reunión (checklist de arriba). Si la
   reunión elige otro aggregator, se reescribe `propuesta_dsmil.md` y el
   bloque de arquitectura del scaffolding; el resto sobrevive.
2. **Validar la arquitectura** contra el repo oficial
   (`binli123/dsmil-wsi`, clonado read-only como hermano en
   `clam_testing2/DSMIL_official_reference/`) y el paper
   ([`../../papers/dsmil_li2021.pdf`](../../papers/dsmil_li2021.pdf)).
   No inventar la arquitectura: replicarla.
3. **Implementar** el aggregator dual-stream y el wrapper sobre `CLAM_MB`
   — rellenar los TODOs de `scaffolding/dsmil_wrapper.py`.
   **Antes de commitear esa implementación, pasar por el agente
   `reviewer`** (regla 9: toca arquitectura de modelo → necesita
   hipótesis + métrica de éxito; ya están en `propuesta_dsmil.md`).
4. **Smoke test**: forward de un batch sintético, verificar shapes y que
   el gradiente fluye. Después, train de 5 epochs sobre la task más chica.
5. **Train completo** sobre las 4 tareas prioritarias y comparación
   lado a lado con Objetivo 1 (baseline) y Objetivo 2 (B=16).
6. **Objetivo 1 completado** es prerrequisito: sin baseline reproducible
   no hay con qué comparar DSMIL.

## Placeholder de resultados

_Pendiente — completar tras confirmación + implementación + ejecución._

| Tarea | test_auc baseline | test_auc DSMIL | Δ | Veredicto |
|---|---|---|---|---|
| MicroCalcificaciones | — | — | — | — |
| C.D.I. Grado Nuclear | — | — | — | — |
| C.D.I. Necrosis | — | — | — | — |
| G.H. Dif. Tubular | — | — | — | (no degradación) |
