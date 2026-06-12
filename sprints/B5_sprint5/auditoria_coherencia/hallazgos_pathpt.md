# Auditoría de coherencia — cierre del hilo PathPT (11-jun-2026)

> Disparada por: registrar/documentar los hallazgos del hilo PathPT (necrosis, mitotic,
> microcalc) cerrado el 11-jun. Skill `@knowledge-audit`. Branch
> `chore/audit-coherencia-pathpt-b5`. Read-only → este doc → fixes → commit.
> (Complementa, no reemplaza, `hallazgos.md` — la auditoría B5 previa.)

## Contexto: qué cerró hoy

PathPT-CONCH probado en 3 tareas, paired vs CLAM:
- **Necrosis** (binaria, job 4309): **H_alt** — no aporta (Δbal −0.020±0.078, Δauc −0.066±0.094).
- **Mitotic** (3-clase ordinal, job 4326): **colapso de formulación** — argmax a la mayoritaria
  (bal_acc 0.333 exacto, 0 preds de s2/s3); causa = "clase 0 = score_1 basal".
- **Microcalc** (3 binarias, go/no-go CPU): **NO-GO** — CONCH no groundea (AUC 0.44–0.63);
  iterar prompts (v2/v3) no superó v1 (0.629).

Mensaje unificado: **el cuello es CONCH / los datos, no el método** → converge con Hallazgos 11
(DSMIL/agregador) y 12 (mammoth/patch-embed). Commits (pusheados): e6462cd, f76576d, ac823f1,
c180e60, d92e170, efd8f90.

## Tabla de hallazgos

| id | hallazgo | tipo | severidad | acción |
|---|---|---|---|---|
| F1 | CLAUDE.md no registra el hilo PathPT (los Hallazgos llegan al 12 = mammoth) | falta de registro | **alta** | agregar **Hallazgo 13** (cierre PathPT) tras el 12 (CLAUDE.md:746) |
| F2 | `retrieval-investigacion-b5` ADDENDUM 10-jun predijo "CONCH en régimen favorable" para PathPT; el resultado lo contradijo | stale | media | **ADDENDUM 2 (11-jun)** cerrando el resultado (sin reescribir el addendum 1) |
| F3 | `MEMORY.md` línea de retrieval refleja sólo la predicción optimista 10-jun | stale | media | actualizar la línea del índice (PathPT probado → no aporta) |
| F4 | `pathpt-testing-necrosis-mitotic` (canónica del detalle) — ya actualizada hoy con los 3 resultados | verificación | baja | confirmar canónica + coherente (OK, sin cambios) |
| F5 | D/CBIR (retrieval) vuelve a ser candidato "alto brillo / bajo riesgo" para la presentación, ahora que PathPT cerró | nota (no contradicción) | info | mencionar en el ADDENDUM 2; la re-priorización es decisión de Ernesto |

## Detalle por hallazgo

### F1 — Hallazgo 13 en CLAUDE.md (el registro principal)
- **Qué dice cada fuente:** CLAUDE.md "Hallazgos vigentes" llega al 12 (mammoth, líneas 724-746);
  **cero menciones de PathPT** en todo el archivo (`grep -ni pathpt CLAUDE.md` vacío). El detalle
  vive en la memoria `pathpt-testing-necrosis-mitotic` y en `sprints/B5_sprint5/pathpt/`.
- **Canónico:** CLAUDE.md debe llevar el **resumen durable** (1 Hallazgo), con punteros al detalle
  (memoria + docs de sprint). El detalle NO se duplica.
- **Fix:** agregar Hallazgo 13 tras CLAUDE.md:746 — necrosis H_alt + mitotic colapso + microcalc
  NO-GO; cierre = cuello CONCH/datos, converge 11/12; punteros a `pathpt-testing-necrosis-mitotic`
  y `sprints/B5_sprint5/pathpt/{resultados_necrosis,resultados_mitotic}.md`.

### F2 — ADDENDUM 2 en retrieval-investigacion-b5
- **Qué dice:** el ADDENDUM 10-jun (líneas 48-56) elevó PathPT (variante B) a prueba activa y predijo
  *"en nuestras 2–4 clases CONCH está en su régimen favorable… el riesgo real = grounding zero-shot de
  nuestra morfología (testeable barato)"*.
- **Por qué es stale:** ese riesgo **se materializó** — el grounding zero-shot resultó débil
  (necrosis 0.677, mitotic 0.648, microcalc 0.44–0.63) y PathPT no aportó. La predicción optimista
  quedó superada por evidencia.
- **Criterio (preservar pre-registración):** NO reescribir el addendum 1 (es registro histórico de la
  predicción). Agregar **ADDENDUM 2 dated (11-jun)** con el resultado y puntero a la canónica.

### F3 — índice MEMORY.md (línea retrieval)
- La línea actual cierra con *"caveat CONCH refinado (gana 9/11)"* — refleja sólo la lectura optimista.
  **Fix:** añadir que PathPT se probó y NO aportó (grounding débil), apuntando a Hallazgo 13.

### F4 — pathpt-testing-necrosis-mitotic (verificación)
- Ya actualizada hoy con necrosis (H_alt), mitotic (colapso) y microcalc (NO-GO). Es la **canónica**
  del detalle del hilo. **Sin cambios** — solo se confirma que Hallazgo 13 (CLAUDE.md) apunta a ella.

### F5 — D/CBIR (nota, no contradicción)
- El análisis de retrieval (5-jun) tenía D/CBIR como primario de presentación y B/PathPT secundario;
  el addendum 10-jun invirtió la prioridad. Con PathPT cerrado (no aporta), D/CBIR **vuelve a ser** el
  candidato de bajo riesgo / alto brillo para el lunes. **No es contradicción** (D nunca se descartó);
  se anota como contexto. La decisión de re-priorizar es de Ernesto/Sebastián.

## Guardrails respetados
- Containment: escribo solo bajo `clam_testing2/oncomets-ernesto/` + memorias en `~/.claude`.
- GPU intacta (gvenegas corriendo desde su path — no se toca; audit sin GPU).
- Pre-registración: addendum dated, sin reescribir hipótesis previas.
- Reglas duras: Hallazgo 13 es aditivo (no altera reglas).
