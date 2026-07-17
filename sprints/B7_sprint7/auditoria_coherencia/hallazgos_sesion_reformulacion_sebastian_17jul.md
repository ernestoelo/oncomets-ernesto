# Hallazgos — reformulación de CDIS/LVI (respuesta de Sebastián, 17-jul-2026)

> Continúa `hallazgos_sesion_ci_inspeccion_16jul.md` (C1-C7). Cierra la observación C2
> (el plegado de `no_identificado` en las binarias): Ernesto se la planteó a Sebastián por
> WhatsApp y **Sebastián respondió con un cambio de formulación**. Este doc registra su
> decisión, los números exactos verificados en disco (regla 5), y el estado de la coordinación.
> Branch: main (documental). GPU: libre (`squeue` vacío). `origin/main`: 1 commit por delante
> (e7acd72, se pushea al cierre). Todo read-only sobre `clam_environ/`; sin GPU, sin `sbatch`.

## La conversación (WhatsApp 17-jul)

Ernesto le planteó las observaciones (C2 principal: el plegado de no_id en CDIS/invasión).
Sebastián respondió (11:25-11:48):

1. **tipo_histologico CONFIRMADO:** "el gate de binario de invasión/no invasión nos hace sacar
   el no_identificado de tipo histologico y dejar solo esas 3 clases". → el `_ci` de tipo queda válido.
2. **Primero justificó el plegado** (11:28): "Cómo CDIS e invasión linfovascular son preguntas
   independientes, considero que es apropiado mapear el no_identificado a ausente dado que una wsi
   puede no tener un carcinoma invasivo pero sí in situ".
3. **Luego se retractó y REFORMULÓ** (11:48): "igual tomemos esos dos casos mejor. De las WSI
   invasivas, entrenar LVI y CDIS **solo con los casos explícitamente ausentes**. No vaya a ser que
   el modelo termine clasificando nuevamente invasión/no invasión para la tarea de LVI o CDIS. O sea
   que termine aprendiendo otra cosa 'más grande' o 'más global' que la tarea".

**Interpretación (decisión operativa):** para CDIS y LVI → **descartar `no_identificado`** (no plegar)
**+ restringir a las WSI invasivas** (las positivas del clasificador de invasión). Motivo: si no_id se
mapea a ausente, la clase negativa se llena de WSIs donde no se evaluó el hallazgo → el modelo puede
aprender a separar invasivo/no-invasivo (la tarea del clasificador de entrada) en vez de LVI/CDIS.
Es un argumento de **fuga de tarea**, metodológicamente sólido, y de paso corrige el desbalance que
motivó C2.

## Tabla resumen

| id | hallazgo | tipo | sev | acción |
|----|----------|------|-----|--------|
| R1 | **Reformulación de CDIS/LVI (decisión de Sebastián).** Descartar no_id + restringir a WSI invasivas, solo casos explícitos. tipo_histologico sin cambios (3 clases). Supersede el plegado del `_ci` (C2) | decisión de proyecto (durable) | alta | ADDENDUM memorias + progress + objetivos; `_ci` CDIS/LVI superseded |
| R2 | **Números exactos de la formulación nueva** (verificados con el CSV del clasificador de invasión + labels de 3 categorías). CDIS **da vuelta el desbalance** a 85% positivo (solo 132 neg); LVI queda balanceado | verificación | alta | avisado a Sebastián por si quiere ajustar CDIS |
| R3 | **Tenemos los insumos para regenerar** (3 CSVs en disco). Pregunta abierta: ¿regenera Sebastián o Ernesto? | coordinación | media | preguntado en el mensaje de respuesta |
| R4 | **El slide sin features (C3) se auto-resuelve.** `histai_1132_slide_H&E_0` es no-invasivo → excluido por la formulación nueva; los 2 conjuntos nuevos verificados 100% con features | cierre de C3 | media | cerrar C3 |

## Detalle y verificación (números en disco, regla 5)

### Insumos encontrados
- **Clasificador de invasión (el "gate", el modelo AUC 0.9524):** su CSV de labels es
  `environ/csv_balance/dataset_invasion_carcinoma_gate_label.csv` → **{invasivo: 2013, no_invasivo: 802}**, n=2815.
  Split asociado: `environ/splits/invasion_carcinoma_gate_pth_balance_100`.
- **Labels originales con las 3 categorías** (para recuperar los "explícitos"):
  - CDIS: `environ/csv_balance/dataset_carcinoma_ductal_insitu_presente_label.csv` → {no_id:1369, si:810, no:636}.
  - LVI: `environ/csv/dataset_invasion_linfovascular_label.csv` → {no_id:1968, ausente:479, presente:368}.

### R2 — Números de la formulación nueva (invasivas ∩ explícitos)

| tarea | plegado (`_ci` actual, superseded) | explícito, sin restringir | **explícito ∩ invasivas (FORMULACIÓN NUEVA)** |
|---|---|---|---|
| CDIS presente | no 2005 · si 810 (n=2815) | no 636 · si 810 (n=1446) | **no 132 · si 730 (n=862)** — 85% positivo |
| LVI (invasión) | ausente 2447 · presente 368 (n=2815) | ausente 479 · presente 368 (n=847) | **ausente 470 · presente 366 (n=836)** — balanceado |

- **Consecuencia nueva en CDIS:** al restringir a invasivas los negativos caen de 636 a **132** (la mayoría
  de los "no CDIS" estaban en WSIs no invasivas). El desbalance no desaparece, **se da vuelta hacia el "sí"**
  (85% positivo). Clínicamente coherente (el invasivo suele traer CDIS asociado). Avisado a Sebastián por si
  quiere ajustar antes de fijarlo (él pensaba en el 636/810).
- **LVI** queda 470/366 (~56/44) = bien balanceado.
- Equivalencia de nombres de clase (misma semántica, distinto string por tarea): `ausente`(LVI) ≡ `no`(CDIS) =
  negativo; `presente`(LVI) ≡ `si`(CDIS) = positivo. Se preservan los strings reales (así están en los CSV).

### R4 — El slide sin features se cae solo
- `histai_1132_slide_H&E_0`: gate = **no_invasivo**, CDIS = `no`, LVI = `no_identificado` → excluido por
  la formulación nueva (no-invasivo). Los 2 conjuntos nuevos verificados: CDIS **862/862** con `.pt`, LVI
  **836/836** con `.pt` → cero features faltantes bajo la formulación nueva. **C3 cerrado** para estas 2 tareas.

## Estado de coordinación
- **Mensaje de respuesta a Sebastián: redactado y humanizado** (sin jerga interna, sin "gate"; número
  132/730 de CDIS + slide + pregunta de quién regenera). **Lo envía Ernesto.** ESPERANDO su respuesta a:
  (1) ¿el 85% positivo de CDIS le sirve o ajusta?; (2) ¿regenera él los splits de CDIS/LVI o los arma Ernesto?
- Generar los CSV+splits nuevos toca el **data-pipeline** → si los hace Ernesto: **regla 9 + reviewer + OK**
  antes de correr, con los gotchas de [[data-gotchas-csv-wsi-interp]] (CRLF Windows, naming linfovascular,
  preflight de presencia de features). Insumos listos (3 CSVs de arriba).

## Implicaciones para el sprint
- `_ci` de **CDIS y LVI = SUPERSEDED** por la formulación nueva; `_ci` de **tipo_histologico = válido**.
- La comparación de heatmaps CLAM vs Mammoth de las 3 tareas se entrena sobre features actuales
  ([[features-tcga-drift-reextraccion]]) con esta formulación → el checkpoint de invasión (04-jun) queda
  doblemente stale (features viejas + formulación 3-clase vieja) → re-entrenar las 3.

## Fixes aplicados (esta sesión)
1. Este doc (R1-R4) — deliverable primero.
2. Memoria [[formulacion-cascada-gate-invasivo]]: ADDENDUM 17-jul (reformulación + números + gate CSV).
3. Memoria [[sprint7-interpretabilidad-clam-vs-mammoth]]: ADDENDUM 17-jul (`_ci` CDIS/LVI superseded).
4. `progress/current.md` §B7: reformulación + mensaje enviado + esperando respuesta.
5. `sprints/B7_sprint7/objetivos_sprint7.md`: ADDENDUM formulación nueva de CDIS/LVI.
6. `MEMORY.md`: líneas de índice.

## Guardarraíles respetados
- Read-only absoluto sobre `clam_environ/`. Sin `sbatch`, sin GPU. Ediciones a memorias/docs = aditivas.
- Números `_ci` plegados dejados como **superseded** (no borrados); histórico citable.
- Binarios `.pptx`/`.pdf` de B7 NO tocados (gitignored).
