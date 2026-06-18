# Auditoría de coherencia — formato minimalista de READMEs de resultados (18-jun-2026)

Gatillo: Ernesto pidió replicar el formato minimalista con el que Sebastián reporta sus
resultados (cola de `results/README_experimentos_mammoth_environ.md`) en nuestros READMEs de
resultados, "más ordenado y claro", cortando información extra. Aplicado hoy a los dos canónicos.

## Resumen

| id | hallazgo | tipo | severidad | acción |
|---|---|---|---|---|
| F1 | No existe convención documentada del formato de los README de resultados | gap | media | registrar memoria + puntero en CLAUDE.md |
| F2 | El minimalismo podría leerse como "reportar AUC solo" (choca con política eval B5) | reconciliation | alta | el formato CONSERVA balanced+AUC; dejarlo explícito |
| F3 | "Formato de entregables" (CLAUDE.md L794) es sobre decks, no sobre docs de resultados | coherencia | baja | edición aditiva: cláusula complementaria, no reescritura |
| F4 | La copia derivada `clam_testing/README.md` debe seguir el mismo molde | propagación | media | sincronizar (fuera del commit; repo ajeno, regla 3.a) |

## Detalle

### F1 — Convención nueva a registrar
- Qué dicen las fuentes: ninguna. `grep` en CLAUDE.md y memorias no devuelve formato de README
  de resultados. La cola de `README_experimentos_mammoth_environ.md` (sección de Sebastián) es
  el estilo de referencia: **Tareas / Dataset / Resultados** (mejor + 5-fold), sin prosa.
- Canónico: nueva memoria `readme-resultados-formato-minimalista` + puntero conciso en CLAUDE.md.
- Formato adoptado (nuestro, "más ordenado"): **Tareas / Dataset / Splits / Comando / Resultados**
  (tabla AUC + balanced) + 1 línea de resumen. SIN política de eval, hallazgo crítico, lectura
  del hilo, mecanismos ni provenance → eso vive en `sprints/.../resultados.md`, referenciado en
  1 línea. Números exactos (no redondear en el canónico).

### F2 — Reconciliación con la política de eval B5
- `eval-reporte-auc-y-umbrales-obj6` + Hallazgo 6/9.a: "reportar SIEMPRE balanced_acc Y AUC
  juntos; lo prohibido es decidir con AUC a secas".
- No hay conflicto: el formato minimalista **mantiene la tabla con balanced + AUC**. El recorte
  es de **prosa**, no de métricas. Queda explícito en la memoria y en la nota de CLAUDE.md.

### F3 — "Formato de entregables" es sobre decks
- CLAUDE.md L794–845 trata decks, diagramas, speaker notes, PNG, pptx. El README de resultados
  es otro artefacto (doc de texto citable). No se contradicen.
- Fix aditivo: una cláusula corta al final de la sección, apuntando a la memoria. No se reescribe
  nada existente (regla "editar hard rules aditivamente").

### F4 — Copia en clam_testing
- `clam_testing/README.md` es la copia de conveniencia (derivada) que ve Sebastián. Debe seguir
  el mismo molde minimalista por consistencia. Se sincroniza fuera del commit del repo (es repo
  ajeno; regla 3.a, no se commitea ahí). [[clam-testing-workspace-compartido]],
  [[merge-criterio-contenido-vs-derivables]].

## Fixes aplicados
1. `results/README_experimentos_mammoth_environ.md` → minimalista (324→153 líneas; cola de
   Sebastián intacta; números verificados por grep).
2. `results/README_pathpt_environ.md` → minimalista (mismo molde).
3. Memoria nueva `readme-resultados-formato-minimalista` (+ índice en MEMORY.md).
4. CLAUDE.md: cláusula complementaria en "Formato de entregables".
5. (Derivado) `clam_testing/README.md` sincronizado al mismo molde.
