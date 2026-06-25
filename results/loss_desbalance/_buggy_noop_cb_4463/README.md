# Brazo `cb` (class_balanced) del job 4463 — INVÁLIDO (no-op), segregado

Estos 15 runs (3 binarias × 5 folds, timestamp 20260623_1559) salieron
**byte-idénticos al baseline CLAM+CE** porque la implementación previa de
`class_balanced` usaba `nn.CrossEntropyLoss(weight=w)` con `reduction='mean'`,
que con `batch_size=1` (MIL) CANCELA el peso → la loss colapsa a CE plana.

Se preservan acá como evidencia del bug (no se borran — workaround C), fuera
del path que lee `scripts/analyze_loss_desbalance.py`, para no contaminar la
verdad de campo. El brazo `cb` se re-corre con el fix (`ClassBalancedCE`,
`reduction='none'.mean()`). Detalle: `sprints/B5_sprint5/loss_desbalance/prereg.md`
(ADDENDUM 2026-06-24).

El brazo `focal_*` del mismo job 4463 NO está afectado (es válido y se reporta).
