# Estudio campaña papilar (CLAM-MB + Mammoth) y diseño del sweep V2

Tarea: `cdis_patron_papilar_pth_balance` — clasificación binaria de patrón papilar en CDIS.
Modelo: CLAM-MB + Mammoth. Fecha: 2026-05-29.

Fuente: `reports/papilar_clam_mammoth_sweep/` (8 configs, 1 fold, 1 seed).

---

## 1. El hallazgo que reordena todo: el test es estadísticamente ciego

Composición del split (fold-0, único existente):

| split | n | positivos | negativos |
|-------|---|-----------|-----------|
| train | 231 | — | — |
| val   | 29  | 3 | 26 |
| test  | 28  | **3** | 25 |

Con **3 positivos × 25 negativos = 75 pares**, el `test_auc` solo puede tomar
valores múltiplos de **1/75 ≈ 0.0133**. Verificado sobre el reporte:

| test_auc | × 75 |
|----------|------|
| 0.7467 | 56/75 |
| 0.7200 | 54/75 |
| 0.7067 | 53/75 |
| 0.6533 | 49/75 |
| 0.5467 | 41/75 |
| 0.4800 | 36/75 |

**Implicación:** reordenar **un solo slide** mueve el AUC entre 0.013 y 0.04.
La diferencia entre la config #1 (0.747) y la #3 (0.707) es de ~3 pares. Con 1
fold y 1 seed, el ranking del v1 **no es estadísticamente distinguible de ruido**.
Cualquier conclusión "config A > config B" basada en este test es frágil.

---

## 2. Qué pasa de verdad con los 3 positivos del test

Probabilidades predichas (prob_class_1) en los 3 positivos del test, para las 3 mejores configs:

| Config | sens | spec | bacc | probs en los 3 positivos |
|--------|------|------|------|--------------------------|
| #1 `do0.6 e8s16h16d256` (AUC 0.747) | 0.33 | 1.00 | 0.667 | 0.03 / 0.82 / **0.03** |
| #2 `do0.5 e4s8h8d128` (AUC 0.720, gap mín) | 0.33 | 0.96 | 0.647 | 0.01 / 0.99 / **0.06** |
| #3 `do0.5 e2s4h8d128` (AUC 0.707) | **0.67** | 0.92 | **0.793** | 0.02 / 0.97 / **0.78** |

- **Un positivo es "imposible"**: todas las configs lo predicen ~0.01–0.03.
  Candidato a error de etiqueta o caso atípico. → revisar el slide manualmente.
- El "ganador" por AUC (#1) **solo detecta 1 de 3 positivos**.
- El que mejor rescata clínicamente (2/3) es el **mammoth compacto `e2s4h8d128`**,
  3º por AUC pero **1º por balanced accuracy (0.793)**.

---

## 3. Lectura del sweep V1

- **Learning rate:** 5e-4 domina. `3e-4` → test 0.48 (peor de todos);
  `7e-4` → bacc 0.50. **Descartados ambos.**
- **Scheduler:** `cosine` (0.653) < `plateau`. **Descartado cosine.**
- **Dropout / reg:** `do0.6 + reg5e-5` (régimen de alta capacidad) da el mejor
  AUC; `do0.5 + reg3e-5` con mammoth pequeño da la mejor estabilidad (gap 0.126).
- **Tamaño Mammoth:** los compactos (`e2s4h8d128`, `e4s8h8d128`) generalizan
  mejor (menor gap val-test, mejor bacc) que el grande (`e8s16h16d256`), salvo
  cuando el grande se acompaña de dropout fuerte (0.6).
- **val ≫ test en todas:** consistente con la escasez de positivos, no
  necesariamente sobreajuste real.

### Los "2 mejores" = dos regímenes, no dos puntos
- **Régimen A — alta capacidad + reg fuerte:** `lr5e-4 do0.6 reg5e-5 e8s16h16d256 plateau`.
  Mejor val/test AUC; conservador (sens 0.33).
- **Régimen B — mammoth compacto:** `lr5e-4 do0.5 reg3e-5 e2s4h8d128 plateau`
  (y su primo `e4s8h8d128`, gap mínimo). Mejor balanced accuracy / sensibilidad,
  menos parámetros, más estable.

---

## 4. Diseño del sweep V2

Archivo: `run_papilar_clam_mammoth_sweep_v2.slurm`
Reporte: `generate_papilar_report_v2.py` (promedia sobre seeds; el v1 no lo hace).

**Decisiones (acordadas con el usuario):**
1. **Multi-seed (1, 2, 3) sobre el mismo fold-0** → ejecutable HOY sin generar
   splits nuevos. Da variabilidad de inicialización y métricas con media±std.
2. **Bloqueado:** `lr=5e-4`, `scheduler=plateau`, `wpos=3.0` (perdedores eliminados).
3. **Grid fino** alrededor de los regímenes A y B.
4. **Nueva palanca:** `confidence_penalty ∈ {0.1, 0.2, 0.3}` (v1 fija en 0.2).
5. **Selección por test_auc PROMEDIO entre seeds.**

**Grid (8 configs × 3 seeds = 24 corridas):**

| # | dropout | reg | mammoth | cp | régimen |
|---|---------|-----|---------|-----|---------|
| A1 | 0.6 | 5e-5 | e8s16h16d256 | 0.2 | A (champion v1) |
| A2 | 0.6 | 5e-5 | e8s16h16d256 | 0.1 | A |
| A3 | 0.6 | 5e-5 | e8s16h16d256 | 0.3 | A |
| A4 | 0.5 | 5e-5 | e8s16h16d256 | 0.2 | A (dropout cruzado) |
| B1 | 0.5 | 3e-5 | e2s4h8d128 | 0.2 | B (best bacc v1) |
| B2 | 0.5 | 3e-5 | e2s4h8d128 | 0.1 | B |
| B3 | 0.5 | 3e-5 | e2s4h8d128 | 0.3 | B |
| B4 | 0.5 | 3e-5 | e4s8h8d128 | 0.2 | B (gap mín v1) |

---

## 5. Limitación que el V2 NO resuelve (y el camino a V3)

El multi-seed **no cambia el split**: siguen siendo los mismos 3 positivos en
test. El arreglo definitivo es **K=5 cross-validation estratificada**, donde cada
caso rota por test (≈15 positivos agregados) y las métricas dejan de ser ruido.

**Bloqueador actual:** solo existe `splits_0.csv`. Para K=5 hay que generar
`splits_0..4` estratificados por label; `create_splits_seq.py` no soporta las
tasks `environ` todavía. El `run_papilar_clam_mammoth_sweep_v2.slurm` ya queda
preparado (variable `K`) y `generate_papilar_report_v2.py` ya promedia sobre
folds Y seeds, así que el salto a V3 (K=5) es solo generar los splits y poner `K=5`.

**Recomendación de priorización:**
1. (Aparte del sweep) Revisar el positivo "imposible" del test → posible error de etiqueta.
2. Correr V2 multi-seed para cuantificar variabilidad y cerrar `confidence_penalty`.
3. Generar splits 5-fold y correr V3 (K=5) — única vía para conclusiones sólidas.
