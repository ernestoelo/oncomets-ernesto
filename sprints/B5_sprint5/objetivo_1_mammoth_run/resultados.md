# Obj 1 B5 — Resultados: Mammoth en CLAM sobre las 3 binarias de microcalcificaciones (k=5 paired)

> Job 4229 (RTX A6000, 2-jun-2026, ~9h40m). Ambos brazos por el **mismo harness**
> (`scripts/train_dsmil.py`), único delta `--model_type clam | clam_mammoth`.
> Comparación **pareada** reusando `data/splits_kfold/<task>_pth_100/splits_0..4.csv`
> (los mismos splits MC-CV de Fase 0). Hipótesis pre-registrada + addendum de
> política de eval: `sprints/B4_sprint4/objetivo_6_mammoth/README.md`.
>
> **Política de evaluación B5** (memoria `eval-reporte-auc-y-umbrales-obj6`): se
> reportan **balanced_acc Y AUC juntos** (test) + matriz de confusión + n por
> clase. **Sin gate numérico** — interpretación cualitativa (consistencia de signo
> a través de folds, magnitud de la varianza, si supera el trivial 0.5). Dirección
> pre-registrada: mammoth mejora ⇒ Δ pareado > 0 consistente.

## Configuración fija (idéntica a ambos brazos)

`max_epochs 30 · early_stopping · patience 20 · stop_epoch 50 · B 8 · bag_weight 0.7 ·
lr 2e-4 · reg 1e-5 · drop_out 0.25 · embed_dim 512 · seed 1 · label_dict {"no":0,"si":1}`.
Mammoth (defaults del paper): `experts 30 · slots 10 · heads 16 · slot_dim 256 ·
dropout 0.1 · keep_slots False · share_lora_weights True · auto_rank True`.

## Sanity check del port — el brazo CLAM reproduce Fase 0

| Binaria | CLAM bal_acc (re-run 4229) | CLAM bal_acc (Fase 0, ref) |
|---|---|---|
| carcinoma | 0.639 ± 0.077 | 0.639 ± 0.077 ✅ |
| cdis | 0.595 ± 0.077 | 0.595 ± 0.077 ✅ |
| tejido | 0.577 ± 0.030 | 0.577 ± 0.030 ✅ |

El CLAM re-corrido por el harness portado reproduce el baseline Fase 0 **al tercer
decimal** → el port (flag mammoth apagado) no altera el camino base; la comparación
es limpia y el Δ es atribuible solo a mammoth.

## Resultados (test, k=5)

| Binaria | n_test | CLAM bal_acc | +Mammoth bal_acc | CLAM AUC | +Mammoth AUC |
|---|---|---|---|---|---|
| carcinoma | 32 (7 pos) | 0.639 ± 0.077 | 0.585 ± 0.080 | 0.732 ± 0.167 | 0.722 ± 0.132 |
| cdis | 36 (11–14 pos) | 0.595 ± 0.077 | 0.509 ± 0.117 | 0.652 ± 0.072 | 0.618 ± 0.098 |
| tejido | 33 (19–21 pos) | 0.577 ± 0.030 | 0.626 ± 0.096 | 0.646 ± 0.025 | 0.678 ± 0.083 |

### Δ pareado por fold (mammoth − clam)

| Binaria | Δ bal_acc (media±std) | folds Δbal | signo | Δ AUC (media±std) |
|---|---|---|---|---|
| carcinoma | **−0.054 ± 0.125** | [−0.02, −0.25, +0.10, +0.03, −0.14] | 2+/3− | −0.010 ± 0.065 |
| cdis | **−0.086 ± 0.113** | [−0.05, +0.12, −0.18, −0.14, −0.19] | 1+/4− | −0.035 ± 0.104 |
| tejido | **+0.049 ± 0.077** | [+0.04, −0.05, +0.18, +0.07, +0.00] | 4+/1− | +0.032 ± 0.084 |

### Matrices de confusión (sumadas sobre los 5 folds) + recall por clase

| Binaria | brazo | [[TN, FP], [FN, TP]] | recall `no` | recall `si` |
|---|---|---|---|---|
| carcinoma | CLAM | [[119, 12], [22, 13]] | 0.91 | 0.37 |
| carcinoma | +Mammoth | [[116, 15], [25, 10]] | 0.89 | 0.29 |
| cdis | CLAM | [[89, 19], [38, 23]] | 0.82 | 0.38 |
| cdis | +Mammoth | [[82, 26], [44, 17]] | 0.76 | 0.28 |
| tejido | CLAM | [[34, 34], [35, 64]] | 0.50 | 0.65 |
| tejido | +Mammoth | [[49, 19], [48, 51]] | 0.72 | 0.52 |

## Interpretación (cualitativa, sin gate)

- **carcinoma — NULO.** Δbal −0.054 con std 0.125 (2.3× la media) y signo mixto
  (2+/3−); ΔAUC ≈ 0. Señal dominada por varianza; sin efecto distinguible.
- **cdis — leve regresión.** 4/5 folds negativos en bal_acc, ΔAUC también negativo,
  y el brazo mammoth cae a **0.509 ≈ trivial 0.5** (colapsa hacia la mayoritaria:
  recall `si` 0.38→0.28). La std (0.113) aún supera la media en magnitud (folds
  cruzan 0), así que no es regresión "dura", pero **es el mismo patrón que DSMIL en
  CDIS** (anexo 4179: Δ −0.053 ± 0.026). CDIS vuelve a ser la binaria que peor
  responde a cambiar agregador / patch-embed.
- **tejido — leve mejora.** Único caso con 4/5 folds positivos y **ambas** métricas
  arriba (Δbal +0.049, ΔAUC +0.032). Mammoth re-balancea el error (recall `no`
  0.50→0.72 a costa de recall `si` 0.65→0.52). La std (0.077) supera la media →
  sugestivo, no concluyente.

### Veredicto

**Mammoth no es una palanca consistente para microcalcificaciones a esta escala.**
Los tres signos no coinciden (tejido +, cdis −, carcinoma nulo) y **en los tres casos
la varianza inter-fold supera la magnitud del efecto** (std > |media|). Esto cae en la
**hipótesis alternativa H0** pre-registrada: Δ en banda ambigua ⇒ mammoth no mueve la
aguja a esta escala ⇒ **refuerza que el cuello de botella es datos / contexto espacial
/ desbalance, no la arquitectura** (consistente con el cierre simétrico CLAM×DSMIL del
Obj 5, Hallazgo 11). El patch-embed (lo que ataca mammoth) tampoco es el cuello aquí.

Esto **no descarta** mammoth para otras tareas con más datos o más heterogeneidad de
fenotipos por slide (su mecanismo —instance-gradient interference— podría rendir donde
la señal no esté tan limitada por n). Esa es justamente la motivación de probarlo en
**patrón arquitectónico** e **invasión linfática** (Obj 2/3 B5).

## Trazabilidad

- Verdad de campo: `results/obj6_mammoth_binarias_<tejido>/<brazo>_<tejido>_f<0..4>_*/`
  (`test_metrics.json` con balanced_acc + confusión; `split_<f>_results.pkl`;
  `summary.csv` con test_auc/val_auc).
- Log del job: `logs/eg_mammoth_bin_kfold_4229.out`.
- *(Nota: en assets para slides, los números de job se omiten y el baseline se rotula
  "Métricas oficiales Environ vX" — memoria `presentacion-convenciones-benjamin`.)*
