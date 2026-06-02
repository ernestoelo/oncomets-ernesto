# Objetivo 6 — mammoth en CLAM sobre las 3 binarias de microcalcificaciones (K=5 paired)

> Arrancado 2026-06-01 tras la reunión con Benjamín (prioriza mammoth, trabajo
> heredado de Eduardo). Estado: **port implementado y verificado en CPU + reviewer
> GO** (1-jun). Pendiente: commit (rama a confirmar con Ernesto) y `sbatch`
> (solo con OK explícito). NO se ha lanzado GPU.

## Contexto

mammoth (*Mixture of Mini Experts*, ICLR 2026, Mahmood Lab) reemplaza la **primera
capa lineal** (patch embed) de CLAM por un mixture-of-experts de bajo rango con
ruteo por slots. Drop-in. Motivación: *instance-gradient interference* — en una
capa lineal única, parches de fenotipos distintos (carcinoma / estroma / normal en
la misma slide) generan gradientes en conflicto; el ruteo a expertos los separa.
Evidencia: paper CLAM 71.7→78.5 (bal_acc, subtyping morfológico); interno, mammoth
ganaba en 3 tasks de la tabla Environ. Detalle e historia del trabajo heredado:
`eduardo_snapshot/` y memoria `mammoth-investigacion-integracion`.

## Argumento (regla 9)

- **Clínico/arquitectónico:** las 3 binarias tienen desbalance + alta
  heterogeneidad de fenotipos por slide. Mammoth ataca exactamente ese mecanismo.
  Es el candidato con evidencia interna **y** prioridad explícita de Benjamín.
- **Por qué ahora y no DSMIL / por qué NO es reapertura (regla 9.b no aplica):**
  DSMIL se cerró (la arquitectura del *agregador* no es la palanca para
  microcalc; anexo 4179: NULL en 2/3 + regresión CDIS). mammoth NO toca el
  agregador — modifica el **patch embed**, capa que DSMIL deja intacta. Es un eje
  **ortogonal** al descartado, no una reapertura del mismo experimento.

## Diseño experimental

- **Tareas:** `microcalcificaciones_en_{carcinoma_invasivo,cdis,tejido_no_neoplasico}_pth`
  (identificadas; `no_identificado` excluido).
- **Comparación PAIRED** ([[patron-paired-comparison-reuso-splits]]) reusando
  `data/splits_kfold/<task>_pth_100/splits_0..4.csv` — los **mismos** splits MC-CV
  k=5 de Fase 0 (CLAM) y del anexo DSMIL. **NO regenerar.**
- **Brazos:** CLAM baseline (`use_mammoth=False`) vs CLAM+mammoth
  (`use_mammoth=True`) — mismo código portado, único delta = el flag. (El baseline
  Fase 0 ya está computado sobre estos splits; correr ambos brazos por la copia
  portada re-confirma el baseline y elimina confound de training-loop.)
- **Hiperparámetros mammoth (1ª pasada):** recomendados del paper — e30 s10 h16
  d256, share_lora_weights, auto_rank. `keep_slots`: ver decisión técnica 1.
- **Régimen:** 1 seed × k=5; B=8 y demás args bendecidos idénticos al baseline.

## Hipótesis pre-registrada

- **H1 (primaria):** mammoth mejora balanced_acc, **Δ pareado ≥ +0.03 (media)** en
  **≥2/3 binarias** con **bandas no solapadas** (mismo umbral §2.2 del Obj 5).
- **H0 (alternativa):** Δ en banda ambigua (|Δ|<0.03 ó bandas solapadas) → mammoth
  no es palanca a esta escala → refuerza "el cuello es datos, no arquitectura".
- **Regresión:** **Δ ≤ −0.05** en alguna binaria con signo consistente (≥4/5
  folds) → mammoth perjudica (como DSMIL en CDIS, −0.053 ± 0.026).
- **Métrica decisiva:** balanced_acc media ± std (k=5), Δ **pareado por fold**.
  AUC = secundaria (reportar, no decidir — test ciego: 7–20 positivos/test).
- **Mecanismo a verificar:** convergencia del bag-loss + `train_clustering_loss`;
  si `keep_slots=True`, validar que el instance-loss top-k sobre E·S pseudo-
  instancias siga teniendo sentido.

### Umbrales anclados al baseline real (CLAM Fase 0, k=5)

| Tarea | CLAM baseline bal_acc | DSMIL Δ bal (ref) | éxito mammoth | regresión |
|---|---|---|---|---|
| carcinoma invasivo | 0.639 ± 0.077 | −0.023 ± 0.071 | Δ ≥ +0.03 + bandas | Δ ≤ −0.05 |
| CDIS | 0.595 ± 0.077 | **−0.053 ± 0.026** | idem | idem |
| tejido no neoplásico | 0.577 ± 0.030 | +0.021 ± 0.051 | idem | idem |

## Decisiones técnicas del port (a validar con reviewer)

1. **`keep_slots`:** Eduardo lo dejó `True` (salida E·S agregadas, cambia la
   semántica de attention/instance-loss). **Recomendación:** 1ª pasada con
   `keep_slots=False` (mantiene los N parches → semántica idéntica al baseline,
   comparación más limpia); `keep_slots=True` como variante posterior.
2. **Base del port:** copia limpia del `model_clam.py` + driver del codebase de
   Sebastián, **no** el fork divergido de Eduardo (evita arrastrar su
   `core_utils.py` +749 de maquinaria de sweeps).
3. **PCGrad (`utils/pcgrad.py`):** fuera de esta 1ª pasada. Gradient surgery es un
   **eje separado** (ataca el mismo problema por optimización); mezclarlo
   confundiría dos variables. Se evalúa después.

## Dependencia y containment (observación del reviewer, 1-jun)

`mammoth-moe` está **instalado editable en `clam_latest` desde
`clam_testing/MAMMOTH/`** (workspace de otra persona, fuera de nuestro
containment). El paquete = clon público `github.com/mahmoodlab/MAMMOTH` **pineado
en `fe36d4e`** (snapshot en `eduardo_snapshot/`). Riesgo: si ese dir se mueve/edita,
los jobs de Obj 6 dejan de reproducir sin aviso. **Fix recomendado antes de que
esto sea un resultado citable** (mutará el env compartido `clam_latest`, hacer con
OK de Ernesto): clonar MAMMOTH bajo `clam_testing2/` y `pip install -e` desde ahí.
Por ahora la 1ª pasada es exploratoria y el pin queda documentado.

## Estado

- [x] Investigación de mammoth + snapshot del trabajo de Eduardo (`eduardo_snapshot/`).
- [x] Hipótesis pre-registrada (este doc).
- [x] Port a `models_mammoth/` + driver (`train_dsmil.py --model_type clam_mammoth`)
      + slurm con preflight (`run_obj6_mammoth_binarias_kfold.slurm`) + test CPU (pasa).
- [x] Reviewer valida argumento + decisiones de port → **GO con observaciones** (1-jun).
- [x] Commit + vendorizar mammoth (HECHO 2-jun: `clam_testing2/MAMMOTH`, pin `fe36d4e`).
- [x] sbatch (HECHO 2-jun con OK de Ernesto: **job 4229**, ambos brazos, RUNNING).

---

## ADDENDUM (2-jun-2026) — política de evaluación: se retiran los umbrales rígidos

> Este addendum **no reescribe** la hipótesis pre-registrada de arriba (los
> umbrales `Δ≥+0.03 / Δ≤−0.05 / ≥4/5 folds` quedan como registro histórico de lo
> que se comprometió **antes** de correr el 4229 — la integridad del pre-registro
> se preserva). Lo que cambia es **cómo se juzga el resultado**.

Decisión de Ernesto durante la corrida del 4229 (fuente de verdad: memoria
`eval-reporte-auc-y-umbrales-obj6`):

1. **Se retira el GO/NO-GO numérico automático.** Ya no se dispara "éxito" porque
   `Δ≥+0.03` ni "regresión" porque `Δ≤−0.05` en ≥4/5 folds. Esos números eran
   arbitrarios y, con n≈33 y std±0.14 (régimen ruidoso de las binarias), forzaban
   un veredicto binario sobre señales dominadas por varianza (la vista preliminar
   de carcinoma —Δ −0.054 ± 0.140, f1 colapsado a 0.5— lo expone).
2. **Reportar SIEMPRE balanced_acc Y AUC** (test, y val si aporta), Δ pareado por
   fold, media±std, matriz de confusión + n por clase. Nunca una sola métrica.
3. **Interpretación cualitativa razonada**, no pass/fail: consistencia de signo a
   través de folds, magnitud de la varianza, si supera el trivial 0.5.

**Cómo convive con regla 9** (no la viola): la métrica predefinida **sigue
existiendo** = Δ pareado en balanced_acc+AUC con **dirección esperada**
(mammoth mejora ⇒ Δ>0 consistente; un Δ<0 consistente sería regresión; varianza
que cruza 0 = ambiguo). Lo que se retira es el umbral mágico, no la
pre-registración de qué se espera y en qué dirección. Ver reconciliación en
`CLAUDE.md` (regla 9 + Hallazgo 6) y `auditoria_coherencia/hallazgos.md` §E.
