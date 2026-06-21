---
name: mammoth
description: Entrena/integra Mammoth (MoE de bajo rango que reemplaza la 1ª capa lineal de CLAM) en OncoMets. Triggers — mammoth, mixture of experts, MoE, reemplazar capa lineal de CLAM, clam_mammoth, instance-gradient interference, expertos.
---

# mammoth — Mixture of Mini Experts en la 1ª capa de CLAM

**Mammoth** (*Mixture of Mini Experts in Pathology*, Shao et al., ICLR 2026,
Mahmood Lab) reemplaza la **primera capa lineal** del pipeline MIL — el `nn.Linear`
que proyecta los features del encoder (CONCH 512) al espacio interno — por un
**mixture-of-experts de bajo rango (LoRA) con ruteo por slots**. NO es un modelo
MIL aparte (a diferencia de DSMIL): es drop-in para esa única capa. Motivación:
*instance-gradient interference* — parches de fenotipos distintos en una misma
slide tiran gradientes en conflicto sobre la capa lineal; el ruteo a expertos los
separa. Paper: CLAM 71.7→78.5 (bal_acc subtyping). **Licencia CC-BY-NC-ND 4.0**
(solo investigación académica).

Contexto, historia heredada de Eduardo y plan: memorias
[[mammoth-investigacion-integracion]], [[equipo-arquitecturas-mammoth-longnet]] y
`sprints/B4_sprint4/objetivo_6_mammoth/`.

## Cómo está integrado en NUESTRO workspace

- **Modelo:** `models_mammoth/clam_mammoth.py` → `CLAM_MB_Mammoth`, **subclase de
  `CLAM_MB`** (de Sebastián, READ-ONLY). Único delta vs el baseline: la 1ª entrada
  de `attention_net` es `MammothPatchEmbed` en vez de `nn.Linear`. `forward`,
  `inst_eval`, `inst_eval_out` se heredan verbatim → comparación clam vs
  clam_mammoth **paired a nivel de arquitectura**.
- **Driver:** `scripts/train_dsmil.py` (harness genérico ya existente) con
  `--model_type clam_mammoth`. MISMA loss (bag CE + inst SmoothTop1SVM) y MISMO
  train/val/test que `--model_type clam`; único delta = el patch embed.
- **Dependencia:** `mammoth-moe` está instalado editable en `clam_latest` desde
  `clam_testing/MAMMOTH/src`. `import mammoth` funciona.

## Activación (args)

```
--model_type clam_mammoth
--mammoth_num_experts 30   # recomendado del paper
--mammoth_num_slots   10
--mammoth_num_heads   16
--mammoth_slot_dim    256
# --mammoth_keep_slots   ← NO pasar en la 1ª pasada (ver abajo)
```
Con `auto_rank=True` (hardcodeado) el rank LoRA se calcula para mantener el
conteo de parámetros comparable a la capa lineal. Con e30/s256/d512 → rank 8.

### `keep_slots` (decisión Obj 6 #1)
- **`False` (default): la salida son los N parches transformados** → semántica de
  attention pooling e instance-loss top-k IDÉNTICA al baseline CLAM. **Usar False
  en la 1ª pasada** (comparación limpia).
- `True`: la salida son E·S features agregadas (pseudo-instancias). Cambia el
  pooling y el top-k. Variante posterior, no en la primera comparación.
  - **Obj 3 B5 (19-jun) ES esa variante posterior** (REABRE el hilo "cerrado" como
    variante NO testeada, no 9.b estricta): prueba `keep_slots=True` + el arg nuevo
    `--mammoth_slot_dropout` (default 0.0, retro-compatible; Brazo 2 = 0.1), paired vs el
    baseline `keep_slots=False` (job 4387). El test CPU ya cubre la config real
    `[300,512]` + el wiring de slot_dropout. Pre-reg + reviewer GO:
    `sprints/B5_sprint5/objetivo_3_mammoth_keepslots/prereg.md`.
  - **CERRADO (21-jun, jobs 4387+4400, matriz 4 brazos × 4 tareas):** `keep_slots=True`
    **NO es palanca vs CLAM** (0/4); mitiga su propio colapso a la mayoritaria pero no
    gana al baseline; `slot_dropout` descartado. **Hilo mammoth completo: 8 drop-in + 4
    keep_slots = 0 palancas.** Veredicto: `objetivo_3_mammoth_keepslots/resultados.md`
    (§0 + §6.3) + [[mammoth-investigacion-integracion]].

## Correr (SOLO vía sbatch — workaround B/cortesía single-GPU)

Plantilla lista: `scripts/run_obj6_mammoth_binarias_kfold.slurm` (3 binarias de
microcalcificaciones × k=5, ambos brazos clam + clam_mammoth, splits reusados de
Fase 0 → paired). Antes de lanzar: `squeue ; sinfo`. Lanzar:
```
sbatch scripts/run_obj6_mammoth_binarias_kfold.slurm
```
Brazo único (economía GPU): `MODEL_TYPES="clam_mammoth" sbatch ...`.

## Verificación antes de GPU

```
CUDA_VISIBLE_DEVICES="" /home/sdonoso/miniconda3/envs/clam_latest/bin/python tests/test_mammoth_cpu.py
```
Valida: swap efectivo, `keep_slots=False` preserva N, gradiente fluye por Mammoth,
forward sobre `.pt` real, harness compartido. El slurm ya lo corre como preflight.

## Reglas que aplican

- **Argumento antes de código (regla 9):** cualquier cambio al modelo/harness va
  con hipótesis pre-registrada + reviewer. La del Obj 6 está en
  `sprints/B4_sprint4/objetivo_6_mammoth/README.md`.
- **Comparación paired** ([[patron-paired-comparison-reuso-splits]]): reusar
  `data/splits_kfold/<task>_pth_100`, NO regenerar.
- **PCGrad** (`utils/pcgrad.py` de Eduardo, gradient surgery) es un **eje
  separado** — NO mezclar con mammoth en la misma corrida.
- **Métrica decisiva:** balanced_acc media±std (k=5), Δ pareado por fold. AUC
  secundaria (test ciego, 7–20 positivos). Umbral éxito Δ≥+0.03 + bandas; regresión
  Δ≤−0.05 (vara del Obj 5).
- **Entregables:** sin números de job en figuras/tablas; baseline como "Environ
  vX" ([[presentacion-convenciones-benjamin]]).
