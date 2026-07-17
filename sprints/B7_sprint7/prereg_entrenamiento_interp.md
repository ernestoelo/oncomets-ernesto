# Pre-registro — entrenamiento CLAM vs Mammoth para interpretabilidad (B7)

> Regla 9 (argumento antes de código) + 9.a ("métrica predefinida" ≠ umbral mágico).
> Slurm: `run_b7_mammoth_interp_kfold.slurm`. Harness: `scripts/train_dsmil.py`
> (`--model_type {clam, clam_mammoth}`, único delta entre brazos). Fecha: 17-jul-2026.

## 1. Propósito (qué es y qué NO es)

Es un **instrumento de interpretabilidad**, NO un experimento de rendimiento. El sprint 7
compara los **mapas de atención de CLAM** vs los **mapas de ruteo por experto/slot de
Mammoth** en 3 tareas (pedido de Sebastián, reunión 13-jul). Para eso hace falta un
checkpoint CLAM y uno Mammoth por tarea, entrenados **paired** (mismo split por fold), y
luego correr `scripts/mammoth_interpretability.py` sobre el checkpoint clam_mammoth.

**NO se reclama que Mammoth mejore la métrica.** Eso está CERRADO (Hallazgo 12: 8 drop-in
+ 4 keep_slots = 0 palancas; el efecto lo gobierna el balance de clases, no la
arquitectura). Este pre-registro **no reabre** ese veredicto (no es decisión revisitada:
no probamos rendimiento, producimos checkpoints para interpretabilidad).

## 2. Por qué re-entrenar (no reusar checkpoints viejos)

- **Drift de features** ([[features-tcga-drift-reextraccion]]): TCGA re-extraído 26-27 jun
  (parche de magnificación de Sebastián, 448@×40→224). Los checkpoints pre-27jun (invasión
  04-jun) usan features viejas → re-inferir hoy diverge. Hay que re-entrenar sobre features
  ACTUALES.
- **Reformulación** (17-jul, Sebastián): cascada gate invasivo. CDIS/LVI = invasivas ∩
  explícitos (binarias); tipo_histologico = 3 clases (no_identificado excluido). El
  checkpoint de invasión viejo es 3-clase {ausente, no_id, presente} → doblemente stale.

## 3. Tareas, formulación y datos (fijados, verificados en disco — regla 5)

| tarea | n_clases | label_dict | split_dir | n | dist |
|---|---|---|---|---|---|
| tipo_histologico | 3 | carcinoma_invasivo_tipo_no_especifico:0, carcinoma_lobulillar_invasivo:1, otros:2 | `environ/splits_5fold_balance_ci/tipo_histologico_4clases_ci_100` (Sebastián, RO) | 2027 | 1610 / 240 / 177 |
| CDIS presente | 2 | no:0, si:1 | `data/splits_kfold/carcinoma_ductal_insitu_presente_ci_reform_100` | 862 | si 730 · no 132 |
| LVI (linfovascular) | 2 | ausente:0, presente:1 | `data/splits_kfold/invasion_linfatica_vascular_ci_reform_100` | 836 | ausente 470 · presente 366 |

Cohorte: las 3 sobre features actuales (priv+TCGA+HistAI según cobertura del CSV). Todos
los slides con `.pt` (preflight embebido, 0 faltantes). Splits paired (reviewer PASÓ los
de CDIS/LVI; tipo reusa el `_ci` de Sebastián). Régimen bendecido: max_epochs 200,
early_stopping patience 20 stop_epoch 50, B 8, bag_weight 0.7, lr 2e-4, reg 1e-5,
drop_out 0.25, embed_dim 512, seed 1 (idéntico a los baselines → apples-to-apples).

## 4. Hipótesis y métrica (regla 9.a — dirección esperada, sin gate rígido)

Como es instrumento, el "éxito" es **producir checkpoints válidos + los mapas**, no ganar
métrica. Expectativas pre-registradas:

- **Convergencia sana:** ambos brazos entrenan sin degenerar (val_loss baja; el checkpoint
  se guarda por val_loss). Recordatorio: `val_auc=nan` época a época en multiclase 3-clase
  es NORMAL, no bug (CLAUDE.md core_utils) → no declarar roto el run de tipo por eso.
- **Métrica reportada (política B5, obligatoria):** balanced_acc **Y** AUC juntos + matriz
  de confusión + **n por clase**, por fold, test (y val si aporta). Nunca AUC aislado.
- **Dirección CLAM vs Mammoth:** se espera Δ (Mammoth − CLAM) **dentro del ruido**
  (std ≳ |media|), consistente con Hallazgo 12. Un Δ **grande y consistente a favor de
  Mammoth sería sorpresa** (a investigar, no a celebrar); un Δ **grande y consistente en
  contra** sería señal de checkpoint Mammoth malo → NO confiar en sus heatmaps hasta
  entender por qué. No hay umbral GO/NO-GO: el entregable es la comparación de mapas.
- **CDIS 85% positivo (ojo al colapso):** riesgo de colapso a la mayoritaria (predecir todo
  `si`). Se reporta **recall por clase**; si colapsa, el valor interpretativo (mapas de
  atención/ruteo) **igual se computa** — se documenta el colapso, no invalida el instrumento.

## 5. Gobernanza

- Paired por reuso del mismo `split_dir` por fold ([[patron-paired-comparison-reuso-splits]]).
- GPU SOLO vía `sbatch`; binario absoluto del env (workaround B); preflight por fold (G).
- Reviewer (regla 9) sobre slurm + este doc + OK de Ernesto + GPU libre ANTES del sbatch.
- Read-only sobre `clam_environ/`; todo output bajo `results/b7_mammoth_interp/`.
- Workaround H: con el job en curso, no cambiar de rama ni editar versionados del árbol.

## 6. Entregable

Checkpoints CLAM + Mammoth por tarea/fold → `scripts/mammoth_interpretability.py` sobre el
clam_mammoth → tabla por tarea (slides, magnificación µm/px, dataset, etiqueta del patólogo;
requisito de Sebastián) + heatmaps CLAM vs ruteo por experto/slot Mammoth.
