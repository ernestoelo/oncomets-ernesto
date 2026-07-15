# Hallazgos — auditoría de coherencia · magnif paths + gate invasivo (15-jul-2026, tarde)

## Contexto (por qué esta auditoría)

Al redactar el mensaje de seguimiento a Sebastián, la sesión propuso pedirle "dónde
documentó el cambio de magnificación de TCGA". **Error:** Sebastián YA lo había enviado
(mensajes WhatsApp 15-jul 9:23–9:24 con los paths exactos) y esos mismos paths **ya estaban
documentados** en dos memorias. La causa raíz es una nota "Pendiente" que sobrevivió a su
propia resolución y fue arrastrada por el handoff como contexto efímero. Este doc registra
el error, las correcciones y el mecanismo para que no vuelva a ocurrir.

## Mensajes de Sebastián registrados esta sesión (fuente de los cambios)

1. **Resultado del clasificador binario de carcinoma invasivo** (WhatsApp 15-jul):
   - "ya está entrenando el modelo que te comenté" → "terminó el entrenamiento, se obtuvo un
     mean auc de **0.9524 ± 0.017**" → "el de validacion fue de **0.9596** asi que generalizó
     super bien".
   - Interpretación (a confirmar): es el **gate/filtro binario** de la cascada
     ([[formulacion-cascada-gate-invasivo]]); el AUC alto encaja con una binaria de entrada.
2. **Paths del parche de magnificación** (WhatsApp 15-jul 9:23–9:24):
   - patching: `/media/administrador/Storage1/sdonoso/clam_environ/run_create_patches_tcga_sc.slurm`
   - features: `/media/administrador/Storage1/sdonoso/clam_environ/run_extract_features_tcga_sc.slurm`
   - backup viejas 224@×40: `/media/administrador/Storage1/sdonoso/clam_environ/environ/features_tcga_224x40`
   - **Coinciden exactamente** con lo ya verificado read-only y documentado en las memorias.

## Tabla resumen

| id | hallazgo | tipo | sev | acción |
|----|----------|------|-----|--------|
| M1 | `magnificacion-cpathagent-proxima-direccion.md:156` "Pendiente: Sebastián manda dónde documentó el cambio" es stale: la MISMA línea ya cita los paths, y Sebastián los reenvió 15-jul 9:23 | stale | media | marcar RESUELTO con paths + "no re-pedir" |
| M2 | `progress/current.md:54-55` replica el mismo pendiente stale ("Sebastián manda dónde documentó el parche") | stale | media | actualizar: paths recibidos, cerrar ese ítem |
| M3 | resultado del clasificador binario de invasivo (AUC 0.9524 ± 0.017, val 0.9596) sin registrar | falta-registro | media | añadir a [[formulacion-cascada-gate-invasivo]] |
| M4 | falta disciplina "verificar antes de pedir" → riesgo de re-preguntar datos ya documentados (los handoffs arrastran pendientes efímeros ya resueltos) | prevención | alta | nueva memoria feedback [[verificar-antes-de-pedir-dato]] |

## Detalle y fix por hallazgo

### M1 — nota "Pendiente" stale en la memoria de magnificación
- **Qué dice hoy:** `...Verificar patch_size_level0:512... Pendiente: Sebastián manda *dónde*
  documentó el cambio. Detalle: ...` — pero los tres paths ya están citados arriba en la misma
  ADDENDUM 15-jul y fueron verificados contra el código.
- **Correcto:** ese "dónde documentó" = exactamente los slurm + el backup, que Sebastián confirmó
  por mensaje el 15-jul 9:23–9:24. Está resuelto.
- **Fix:** reemplazar la frase por `RESUELTO 15-jul: Sebastián confirmó los paths por mensaje
  (run_create_patches_tcga_sc.slurm, run_extract_features_tcga_sc.slurm, backup features_tcga_224x40)
  → ya documentados y verificados aquí; NO volver a pedirlos.` La verificación de `patch_size_level0:512`
  (SB6) queda como el único pendiente real de esa línea.

### M2 — el mismo pendiente stale en progress/current.md
- **Fix:** en la lista "Pendiente (mensaje de seguimiento)" quitar "Sebastián manda dónde documentó
  el parche" (recibido); dejar los pendientes reales: clases exactas de `tipo_histologico`, decisión
  de splits, verificar `patch_size_level0:512`. Registrar que los paths llegaron y el resultado del gate.

### M3 — registrar el resultado del gate
- **Fix:** ADDENDUM en [[formulacion-cascada-gate-invasivo]]: Sebastián entrenó el clasificador binario
  de carcinoma invasivo (AUC 0.9524 ± 0.017 / val 0.9596, 15-jul); generaliza bien. "El modelo que te
  comenté" = muy probablemente este gate (a confirmar). Buena señal para toda la cascada: filtro de
  entrada limpio → downstream recibe población más limpia.

### M4 — mecanismo de prevención (lo que pidió Ernesto)
- **Causa raíz del error:** un handoff arrastra "pendientes" como contexto efímero; si el pendiente ya
  fue resuelto en una memoria canónica, la sesión que confía en el handoff sin cross-check re-pregunta.
- **Fix durable — nueva memoria feedback [[verificar-antes-de-pedir-dato]]:** antes de pedirle a Sebastián
  (o a cualquiera) un dato, o de accionar un "pendiente" de handoff, **grep primero las memorias/repo**
  (regla 5). Un pendiente de handoff NO es autoridad; la memoria canónica manda. Cerrar el pendiente en la
  memoria en cuanto se resuelve, para que no se arrastre.

## Estado tras los fixes
- M1/M2 stale corregidos (memoria + progress). M3 registrado. M4 = memoria feedback nueva + índice.
- Resto de la base sin tensiones nuevas detectadas en este barrido enfocado.
