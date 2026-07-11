# Pre-registro — magnificación multi-escala (CONCH) sobre CLAM, piloto microcalc

> **Regla 9 (argumento ANTES de código).** Toca el **data-pipeline** (re-extracción de
> features) → requiere **reviewer** antes de commitear el wrapper. Comparación **PAIRED**
> por reuso de splits (P1). Eval B5: **balanced_acc Y AUC** + confusión + n/clase.
> Fundamento clínico completo: `investigacion_magnificacion.md` (§2–§6). NO es una decisión
> revisitada (regla 9.b): la magnificación es un **eje nuevo** (dato/contexto), no reabre el
> eje arquitectura cerrado en Hallazgos 11-14. Fecha: 10-jul-2026.

## 1. Pregunta y mecanismo (por qué, no solo qué)

La etiqueta CAP de las 3 binarias de microcalc es **contextual** ("¿la microcalcificación vive en
CDIS / carcinoma invasivo / tejido no neoplásico?"), no de detalle celular. Localizar exige ver el
**tejido anfitrión** (conducto de DCIS, nido invasor, lobulillo) que a parche fino (campo ~59–119 µm)
**no cabe**. La palanca = **agregar una escala GRUESA de contexto** (no más zoom). Es la **única
señal nueva** disponible tras cerrar arquitectura/loss (0 palancas). Réplica del baseline MIL
multi-escala de CPathAgent (Ap. C.1.2): pirámide de campos → CONCH → **promedio** → CLAM_MB intacto.

## 2. Tarea (decisión + matiz honesto)

- **Piloto = las 3 binarias de microcalc** (`microcalcificaciones_en_{cdis, carcinoma_invasivo,
  tejido_no_neoplasico}_pth`). Elegida por **costo** (pocas WSI, cabe en un fin de semana — pedido de
  Sebastián), para **validar la tubería multi-escala end-to-end**, NO por ser la de mejor argumento.
- **Matiz para Sebastián** (§5.6 investigación): la mayor apuesta de retorno científico es
  `gh_dif_tubular` o un patrón de DCIS (context-hungry puro, sin techo de oxalato) → **follow-up si el
  piloto valida la tubería**. No contradice su scoping; lo refina.

## 3. Diseño experimental — 3 brazos paired

Escalas (definidas en **µm/px físico**, no en `level`; crop en px calculado **por slide** desde su
`mpp-x` real — TCGA ~0.2325, privado ~0.465):

| Escala | Campo | Rol |
|---|---|---|
| **Fina** | ~112 µm (224 px @ 0.5 µm/px = CONCH-nativo 20×) | detecta la calcificación + morfología |
| **Contexto** | ~512 µm (224 px @ ~2.3 µm/px ≈ 5×) | conducto/lobulillo anfitrión (la localización CAP) |

**Fusión = promedio** de los 2 vectores CONCH → un token `[N,512]` → **CLAM_MB intacto** (único delta
= el contenido del token, no el agregador). Alternativas (concat/multi-token) = 2ª iteración solo si el
promedio da lift.

| Brazo | Features | Aísla |
|---|---|---|
| **A** (baseline) | single-scale actual (256 px @ level0), **re-entrenado sobre features actuales** | referencia |
| **B0** (fine-only) | solo tile fino @ grid común 112 µm | efecto del **re-grid a µm/px común** (corrige el confound §4.2) |
| **B** (multiscale) | fino 112 µm + contexto 512 µm, **promediados** | efecto de **agregar contexto** |

Comparaciones paired (mismos splits, mismo subset): **B vs A** (efecto total), **B vs B0** (contexto
aislado), **B0 vs A** (re-grid aislado). Reuso de splits k=5 existentes (`data/splits_kfold/
microcalcificaciones_en_*_pth_100`), Δ **pareado por fold** ([[patron-paired-comparison-reuso-splits]]).

**HistAI (49/333):** sin MPP fiable (`histai_magnificacion.md`) → **se excluye de la re-extracción**;
conserva su single-scale actual en los 3 brazos (impureza acotada al 15% minoritario, documentada). El
subset con µm/px resuelto (TCGA 207 + privado 76 = 283, = el slidelist y el preflight) es donde vive el contraste. **Por qué re-entrenar
A:** las features TCGA driftearon (re-extracción 26-27 jun, ver `tier0_calibracion/resultados.md`); para
que el Δ B−A sea limpio, A se re-entrena sobre las **mismas features actuales** que B0/B.

## 4. Hipótesis pre-registrada (regla 9 / 9.a — dirección, no umbral mágico)

- **Primaria (H1):** el contexto 5× sube la señal arquitectural → **Δ pareado ≥ 0 consistente en signo**
  en `en_cdis` y `en_carcinoma_invasivo` (las context-hungry), en **balanced_acc Y AUC**, para **B vs B0**
  (contexto aislado) y **B vs A**.
- **Nula (H0):** Δ dentro del ruido (std ≳ |media|, signo inconsistente) = el contexto no mueve la aguja
  en microcalc → converge con "el cuello es el dato/desbalance, no la representación".
- **Regresión (H2):** Δ < 0 consistente = el **promedio diluye** la señal fina de la calcificación →
  descartar promedio, evaluar multi-token/concat.
- **Predicción por tarea** (§5.4): `en_cdis` = mayor candidato a lift (patrón ductal = puro contexto);
  `en_carcinoma_invasivo` = candidato; `en_tejido_no_neoplasico` = **menor** (techo de oxalato Tipo I,
  CONCH ciego — §2.1) → si algún brazo NO sube ahí, es **esperado**, no falla del método.
- **Magnitud esperada: CHICA.** CPathAgent gana solo **+2.9% sobre ABMIL multi-escala** y **no rompe el
  techo de datos**. El experimento se justifica por inyectar la única señal nueva, no por promesa de salto.

## 5. Métrica y evaluación

**balanced_acc Y AUC juntos** (macro-OVR binario) + matriz de confusión + **n por clase**, **Δ pareado por
fold** sobre los mismos splits k=5. Reporte por las 3 binarias por separado (no promediar tareas). Sin
GO/NO-GO numérico rígido (regla 9.a): se decide por **consistencia de signo del Δ pareado + magnitud vs
varianza inter-fold**, interpretado por tarea.

## 6. Pipeline (3 etapas) y gobernanza

1. **Patching por-cohorte** (grid común 112 µm): `create_patches_fp.py` (clam_environ, **sin modificar**,
   solo args) con `--patch_size = round(112/mpp)` y `--patch_level 0` por cohorte → `.h5` de coords bajo
   `clam_testing2/`. TCGA patch_size≈482, privado≈241.
2. **Extracción multi-escala** (wrapper propio `scripts/extract_multiscale_features.py`, regla 2 — no toca
   clam_environ; reusa `get_encoder('conch_v1')`): `--mode fine_only` (B0) y `--mode multiscale` (B) →
   `.pt [N,512]` bajo `clam_testing2/oncomets-ernesto/results/` o `data/`.
3. **CLAM paired** (`scripts/train_dsmil.py --model_type clam`, harness existente): 3 brazos × 3 binarias
   × 5 folds sobre los mismos splits, `--data_root_dir` apuntando al feature dir de cada brazo.

**Gobernanza (no negociable):** GPU **solo vía sbatch** (workaround B, binario absoluto del env);
**preflight** obligatorio (workaround G — validar nº min de parches/slide); **containment** (todo bajo
`clam_testing2/`); **cortesía single-GPU** (job de fin de semana, `squeue` antes); **reviewer** antes de
commitear el wrapper y el `.slurm`. **NO** `sbatch` sin OK explícito de Ernesto.

## 7. Riesgos / caveats declarados

- **Techo de oxalato** en `en_tejido_no_neoplasico` (Tipo I invisible en H&E) → lift esperado nulo ahí.
- **HistAI single-scale** en los 3 brazos = impureza acotada (15%, minoritario), documentada.
- **Bordes**: crops de contexto cerca del borde del WSI se **clampean** (no black-fill) en el wrapper.
- **Coste CONCH**: 2 escalas × 284 slides × N parches — job de fin de semana; el contexto se lee del
  mejor nivel de la pirámide (barato), no a level0 crudo.
- **Drift de features** (Tier 0): A se re-entrena sobre features actuales para pairing limpio.
