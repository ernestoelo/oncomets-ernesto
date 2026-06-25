# Auditoría de conocimiento — eje loss-desbalance (B5)

> **ADDENDUM 2026-06-24 (cierre, post-4472): H4 RESUELTO.** El job 4472 terminó (15/15,
> 23:16) → `cb` = **NO palanca = H_reg** (sube recall minoritaria, hunde mayoritaria,
> bal_acc neta sin cambio; std ≳ |media|). El eje cierra: ni focal ni cb mueven la aguja.
> Veredicto + tablas: `resultados.md`. Cierre en CLAUDE.md = **Hallazgo 14**. Memoria
> [[loss-desbalance-eje-c1]] actualizada. Lo de abajo es el snapshot de la sesión AM
> (cuando 4472 estaba PD) y se conserva por trazabilidad — NO reescrito.
>
> Fecha: 2026-06-24. Disparador: hallazgos del job 4463 (focal/cb binarias) al
> verificar resultados. Job 4472 (re-run cb con el fix) **PD/en curso** al momento
> de la auditoría → veredicto cb NO se afirma. Auditoría documental (no toca el job,
> no cambia de rama; workaround H).

## Resumen (id · hallazgo · tipo · severidad · acción)

| id | hallazgo | tipo | sev | acción |
|---|---|---|---|---|
| H1 | El brazo `cb` (class_balanced) del 4463 fue un **no-op**: `nn.CrossEntropyLoss(weight=w)` con `reduction='mean'` cancela el peso a **batch=1** (MIL). Salió byte-idéntico al baseline CE. | error (resuelto) | alta | gotcha durable → memoria nueva + línea en CLAUDE.md; fix `ClassBalancedCE` (commit `2cab10f`); ADDENDUM al prereg |
| H2 | `focal` (γ=2, sin α) **NO es palanca**: null-a-negativo y **baja** el recall de la minoritaria (contra H1 del prereg). | resultado | media | registrar en memoria del eje (válido, no afectado por el bug) |
| H3 | Memoria [[loss-desbalance-eje-c1]] quedó **stale**: dice "job 4463 EN CURSO" y "test CPU 5/5". | stale | media | actualizar: 4463 cerrado, focal null, cb re-corriéndose (4472), test 6/6, commits `2cab10f`/`7d245fd` |
| H4 | El veredicto del **eje** (cb como palanca) está **pendiente** (4472 sin terminar). | — | — | NO escribir Hallazgo de cierre en CLAUDE.md hasta tener números (handoff §6) |

## Detalle

### H1 — bug class_balanced no-op a batch=1 (gotcha durable)
- **Qué dice cada fuente:** el prereg §1-§3 argumenta `class_balanced` con pesos por
  número efectivo (correcto). El código (`build_bag_loss`) los **computaba bien** (el
  print del log lo confirma: `[0.413, 1.587]` etc.) pero los **aplicaba con
  `nn.CrossEntropyLoss(weight=w)` reduction='mean'**, que con MIL `batch_size=1`
  (`clam_environ/utils/utils.py` get_split_loader, todas las ramas) normaliza por
  `w_y` → el peso se cancela → `L = CE`. Demostrado numéricamente (`CE_w(mean) ==
  CE_plana` exacto a batch=1; predicciones del run cb byte-idénticas al baseline).
- **Canónico:** el fix + la causa viven en (a) el código (`ClassBalancedCE`,
  `scripts/train_dsmil.py`), (b) el ADDENDUM del prereg (provenance pre-registración),
  (c) memoria nueva [[mil-weighted-ce-noop-batch1]] (gotcha reusable), (d) una línea
  en CLAUDE.md (fact validado contra el código, alto costo de re-tropiezo). `focal`
  NO sufre (su modulación `(1-pt)^γ` es por-sample, sobrevive el `.mean()` de 1 elem).
- **Por qué es gotcha y no hallazgo de eje:** es cierto independientemente del
  veredicto cb; cualquier loss ponderada futura en este harness MIL lo re-pisa.

### H2 — focal no es palanca (resultado válido)
- Δ paired (focal − CE), k=5 pooled: carcinoma Δ bAcc −0.042 ± 0.081 (2+/3−), Δ AUC
  −0.036; cdis −0.064 ± 0.093 (2+/2−), Δ AUC −0.062; tejido (control balanceado)
  +0.013 ± 0.052 ≈ null. Recall minoritaria `si` **baja** carcinoma 0.371→0.286,
  cdis 0.377→0.262 → lectura H_alt/H_reg: el γ-focusing sin α no rescata la
  minoritaria, el colapso persiste. Coherente con el techo de datos (Hallazgos 11/12/13).

### H3/H4 — propagación + límite
- Actualizar la memoria del eje al estado real (sin afirmar cb).
- El cierre del eje (Hallazgo nuevo en CLAUDE.md) **espera** los números de 4472.

## Fixes aplicados por esta auditoría
1. Memoria nueva [[mil-weighted-ce-noop-batch1]] (gotcha) + línea índice en MEMORY.md.
2. Memoria [[loss-desbalance-eje-c1]] actualizada (estado real, link al gotcha) + índice.
3. CLAUDE.md: una línea en "Modelos alternativos en NUESTRO repo" (gotcha bag-loss
   batch=1, puntero a la memoria) — aditiva, no reescribe nada.
4. (Ya hechos fuera de esta auditoría: fix `ClassBalancedCE` + test regresión 6/6 +
   ADDENDUM prereg, commits `2cab10f`/`7d245fd`; runs cb buggy segregados a
   `results/loss_desbalance/_buggy_noop_cb_4463/`.)
