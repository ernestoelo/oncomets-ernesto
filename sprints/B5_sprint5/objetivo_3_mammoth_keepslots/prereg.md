# Objetivo 3 (B5) — Mammoth `keep_slots=True` (+ `slot_dropout`): pre-registración (regla 9 + 9.b)

> **Qué es:** reabre el patch-embed de mammoth con una variante arquitectónica **no testeada**
> en el hilo cerrado (Hallazgo 12): el cuello de botella de slots (`keep_slots=True`) y el
> regularizador de ruteo (`slot_dropout`). Se compara **paired vs el baseline ya corrido**
> (CLAM y mammoth-`keep_slots=False`) sobre **los mismos splits k=5**.
> **Argumento ANTES de código (regla 9).** Este doc se escribe **antes** de tocar
> `models_mammoth/` o el `.slurm`; el `reviewer` lo evalúa, y recién con su GO + test CPU +
> OK de Ernesto se lanza el `sbatch`.
>
> Base conceptual (NO re-derivar): traza de dimensiones y semántica en el análisis de sesión
> (resumida en §1). Código verificado: [models_mammoth/clam_mammoth.py](../../../models_mammoth/clam_mammoth.py),
> [scripts/train_dsmil.py](../../../scripts/train_dsmil.py), paquete vendorizado
> `clam_testing2/MAMMOTH/src/mammoth/mammoth.py` (pin `fe36d4e`).

---

## 0. Estatus regla 9.b — lo digo sin maquillar

El hilo mammoth está **cerrado** (Hallazgo 12 / [[mammoth-investigacion-integracion]]): 8 tareas
pareadas k=5, **0 palancas**. El descarte **generaliza**: "la arquitectura del patch-embed NO es
la palanca; el cuello = datos / desbalance / contexto espacial".

**No tengo un habilitante 9.b limpio**, y no lo voy a inventar: el mecanismo del job 4246
(invasión, regresión leve consistente vía colapso a la mayoritaria, `presente` recall
0.577→0.434) fue **parte del conjunto que cerró** el hilo, no un hallazgo *posterior* que lo
contradiga. Reabrir esto **no** cumple 9.b en su lectura estricta ("un hallazgo posterior del
mismo sprint contradice el argumento del descarte").

El ángulo legítimo, dicho con precisión:

1. **Las 8 tareas testearon UN solo punto del espacio de config de mammoth** — `keep_slots=False`,
   `slot_dropout=0`, sin aux-loss, hiperparámetros del paper fijos. El descarte se infirió de
   ese punto y se generalizó a "mammoth".
2. **`keep_slots=True` es una arquitectura materialmente distinta**, no un re-tuneo: deja de ser
   un drop-in de la lineal (cardinalidad N→N) y pasa a ser un **cuello de botella de slots**
   (N→300 tokens dependientes del contenido) tipo Perceiver/Set-Transformer. Es discutible que
   sea "la misma decisión" descartada. **El reviewer (§7) resolvió este punto: NO es 9.b
   estricta (no reabre el mecanismo descartado con un valor nuevo) sino un punto no testeado
   del espacio de config con semántica arquitectónica distinta** — por eso no se exige el
   habilitante job-posterior, pero sí la carga de regla 9 completa (cumplida, §2).
3. El mecanismo de 4246 **no habilita la reapertura, pero sí define el blanco**: la intervención
   se diseña apuntada al **colapso a la mayoritaria** (recuperar recall de la minoritaria), no a
   un tuneo genérico de capacidad. Eso es lo que separa esto de "vamos a probarlo igual" (que
   regla 9.b prohíbe).

**Decisión de gobernanza:** que esto avance lo deciden **`reviewer` + Sebastián**. Mi lectura:
`keep_slots=True` pasa como *variante arquitectónica no testeada*; `slot_dropout` va **acoplado**
a ese experimento (no como cambio aislado); la **aux-loss queda fuera de esta pasada** (§4).
Si el reviewer juzga que NO cae bajo "variante nueva" sino bajo "decisión revisitada sin
habilitante", **el experimento no se lanza** — y esta pre-registración deja el razonamiento
trazado para esa conversación.

---

## 1. Mecanismo: por qué `keep_slots=True` *podría* mover la aguja (y por qué podría no)

**Hoy (`keep_slots=False`):** mammoth es drop-in de la 1ª lineal de CLAM. Rutea los N parches a
30 expertos × 10 slots y **recombina de vuelta a N** (`combine_weights`, softmax sobre los 300
slots) → salida `[N, 512]`. Misma cardinalidad → la atención gated de CLAM y la instance-loss
top-k operan sobre los N parches, igual que el baseline.

**Propuesto (`keep_slots=True`):** se **salta** la recombinación y devuelve los **300 slot-tokens**
`[300, 512]`. Los `slot_embeds` (parte aprendida, fija) rutean los N parches de *esta* slide a
300 slots **dependientes del contenido** (vía `dispatch_weights` = softmax sobre los N parches).
Es un **cuello de botella aprendido ANTES** de la atención de CLAM → atención de dos etapas
(mammoth-slots → CLAM-gated). Traza verificada (CONCH 512, `auto_rank→8`):
`[N,512] → wq → [N,256] → dispatch(softmax_N) → slots [30,16,10,16] → expert_heads → [300,512]`.
La dim final **512 = num_heads·(dim/num_heads) = 16·32** (reconstrucción de `input_dim` vía heads,
`mammoth.py:351-357`), **NO** el `slot_dim=256` ni la fórmula confusa de la docstring del vendor
(`mammoth.py:334`). Aquí 512(out)=512(in) porque CONCH y la dim interna coinciden; si se cambiara
`dim`, esa igualdad se rompe → el test CPU (§3.6) verifica la forma por el rearrange real, no por
la coincidencia numérica.

**El `forward` de CLAM_MB es genérico en el nº de tokens M** ([clam_environ model_clam.py:207](../../../../clam_environ/models/model_clam.py)):
`A,h = attention_net(h)` con `h:[M,512]`, `inst_eval` top-k sobre M, `M_pool = A@h`. Flipear
`keep_slots=True` solo cambia `M: N → 300` — **transparente, sin código de modelo**.

Por qué **podría ayudar** (H1): un slot puede **especializarse** en el fenotipo raro — el dispatch
es softmax sobre parches, así que un slot puede concentrar su masa en pocos parches raros
(foco de invasión, microcalc). El bottleneck denoisea y da **capacidad dedicada** a la
minoritaria → recupera el recall que hoy colapsa.

Por qué **podría empeorar** (H_reg, riesgo serio): comprimir N→300 con softmax-sobre-parches puede
**promediar** la señal local rara (que vive en poquísimos parches). Como el modo de falla actual
**ya es** colapso a la mayoritaria, el bottleneck puede **acentuarlo**. Doble filo genuino → por
eso se pre-registra con H_reg explícita, no como mejora asumida.

**`slot_dropout`** (regularizador, hoy en 0.0): enmascara logits de ruteo en training antes del
softmax → "dropout sobre la asignación de slots". Estándar en MoE; con n chico **podría** frenar
el sobreajuste a la mayoritaria. EV modesto; va como 2º brazo barato, no como apuesta central.

**Riesgo honesto (H0 no es de paja):** el mismo sprint cerró que ni el agregador (DSMIL,
Hallazgo 11), ni el patch-embed en su config probada (mammoth, Hallazgo 12), ni el lenguaje+tile
(PathPT, Hallazgo 13) son palanca — el cuello fue el **dato**. `keep_slots=True` es otra
config del **mismo** componente; lo más probable a priori es **banda ambigua**. La pregunta no es
"¿gana?", es "¿el Δ pareado es positivo y consistente en signo, y se angosta el gap de recall?".

---

## 2. Hipótesis pre-registrada (regla 9)

Comparación **PAIRED por fold** sobre los **mismos** splits k=5 que el baseline
([[patron-paired-comparison-reuso-splits]]): el Δ pareado cancela la varianza inter-fold y revela
señales chicas. **Dos contrastes** (ambos paired, mismos splits):

- **C1 (primario — within-mammoth):** `keep_slots=True` **vs** `keep_slots=False`. Responde la
  pregunta real "¿el cuello de botella mejora a mammoth?". Δ_i = KST_i − KSF_i por fold.
- **C2 (vs CLAM):** `keep_slots=True` **vs** CLAM baseline. Responde "¿la mejor variante de mammoth
  le gana al baseline real?". Δ_i = KST_i − CLAM_i por fold.

### Hipótesis (aplican a C1 y C2)

- **H1 (primaria):** `keep_slots=True` mejora la clasificación slide-level →
  **Δ balanced_acc pareado > 0, consistente en signo** (mayoría de los 5 folds positivos,
  idealmente |media| ≳ std) **Y** el **gap de recall mayoritaria↔minoritaria se angosta**
  (diagnóstico mecanístico, abajo). Interpretación: el bottleneck da capacidad dedicada a la
  clase rara.
- **H_alt (nula/ambigua):** Δ pareado **cruza 0** (std ≳ |media|, signo inconsistente) → la
  variante **no aporta**. Lectura: mismo techo de datos que Hallazgos 11/12/13 — confirma que el
  patch-embed no es la palanca **ni siquiera** con el cuello de botella. **Resultado presentable**,
  no fracaso (cierra el espacio de config de mammoth de forma más completa).
- **H_reg (regresión):** Δ pareado **< 0 consistente** → el bottleneck **acentúa** el colapso
  (promedia la señal rara). Hallazgo informativo y coherente con el mecanismo de 4246.

### Diagnóstico mecanístico decisivo (NO es el promedio)

El veredicto **no** se lee del balanced_acc medio: se lee del **gap de recall por clase**, que es
lo que el mecanismo de 4246 puso en evidencia. Pre-registrado:

- **Invasión 3-clase:** ¿`presente` recall **sube desde 0.434** (mammoth-F) hacia/encima de CLAM
  (0.577)? ¿`no_identificado` recall **baja desde 0.815** (menos colapso)? H1 ⇒ ambas; H_reg ⇒
  lo contrario.
- **Tejido (binaria balanceada):** ¿se mantiene o mejora el recall de la clase minoritaria sin
  sacrificar la otra (gap más simétrico)?

### Métrica + subset + dirección (predefinidos, política B5)

| | |
|---|---|
| **Subset A** | **invasión linfática vascular**, 3 clases (`no_identificado` 1967 / `ausente` 479 / `presente` 368), n=2814. **El de más poder y eval más sano del hilo** (cada clase n≥36/test → lectura **fold-a-fold**). Es donde mammoth-F mostró la regresión más nítida (5/5−) → testbed natural de la intervención. |
| **Subset B** | **microcalc en tejido no neoplásico**, binaria (si 195 / no 138), n=333. La tarea **más balanceada** del hilo y donde mammoth-F tuvo el único lean+ leve (Δbal +0.049) → **régimen balanceado / mejor caso a priori** (NO "control positivo": el +0.049 venía con std≳\|media\|, banda H0 — no es un efecto establecido que `keep_slots=True` deba *reproducir*; Obs 2.a reviewer). |
| **Primaria** | **balanced_acc** en el **test** de cada fold; estadístico = **Δ pareado por fold** (media ± std + signo por fold), para C1 y C2. |
| **Secundaria** | invasión: **macro-OVR AUC**; tejido: **ROC-AUC**. **Reportar SIEMPRE junto a balanced_acc** + matriz de confusión + **recall por clase con n** ([[eval-reporte-auc-y-umbrales-obj6]]). |
| **Dirección si H1** | Δ>0 consistente en signo en bal_acc; gap de recall se angosta (diagnóstico arriba). |
| **Regla de decisión (regla 9.a — NO gate mágico)** | Δ>0 consistente y |media|≳std **y** gap se angosta → **aporta**. Δ cruza 0 / std≳|media| → **ambiguo** (techo de datos). Δ<0 consistente / gap se ensancha → **regresión**. Con n chico mandan **signo + magnitud relativa a la varianza + el gap de recall**, no un umbral automático. **Desempate (Obs 4.a reviewer):** ante conflicto balanced_acc↔gap-de-recall, **manda el gap de recall** (es el mecanismo); bal_acc subiendo SIN angostar el gap se lee **H_alt, no H1**. |

**Entregable obligatorio:** matriz de confusión **por clase con n** — fold-a-fold en invasión
(eval sano) y **pooled** en tejido (test chico). Es la única lectura estable del mecanismo.

---

## 3. Decisiones de ingeniería (ANTES de código — para el reviewer)

### 3.1 Splits y baselines — **ya existen, se reusan tal cual (paired por construcción)**
- Splits: `data/splits_kfold/invasion_linfatica_vascular_pth_100/` y
  `data/splits_kfold/microcalcificaciones_en_tejido_no_neoplasico_pth_100/` (MC-CV k=5,
  val=test=10%, seed 1, patient_strat). **NO se regeneran** (regla P1).
- Baselines CLAM y mammoth-`keep_slots=False` **ya corridos** sobre esos mismos splits:
  invasión en `results/obj2_mammoth/invasion_linfatica_vascular_pth/`, tejido en
  `results/obj6_mammoth_binarias_tejido_no_neoplasico/`. El Δ pareado se construye contra esas
  predicciones por fold guardadas → **los baselines NO se re-corren**; solo los brazos nuevos van a GPU.

### 3.2 Brazo 1 — `keep_slots=True` — **CERO código de modelo**
El flag **ya existe y está cableado**: `--mammoth_keep_slots`
([train_dsmil.py:144](../../../scripts/train_dsmil.py) → `build_model` → `CLAM_MB_Mammoth` →
`MammothPatchEmbed` → `Mammoth`). El brazo es el **mismo comando del baseline** + `--mammoth_keep_slots`
(todos los demás args idénticos al job 4246/4229 → paired). **No toca `model_*.py`.**
> Aun siendo config-only, **NO se lanza sin reviewer**: la reapertura cae bajo regla 9.b (§0).

### 3.3 Brazo 2 — `+ slot_dropout` — **toca código (aditivo, ~4 puntos)**
`slot_dropout` existe en `Mammoth.__init__` pero **el wrapper no lo expone**. Cambio aditivo:
1. `MAMMOTH_DEFAULTS` += `slot_dropout=0.1` (default sugerido del paper para training).
2. `MammothPatchEmbed.__init__` → param + pasarlo a `Mammoth(...)`.
3. `CLAM_MB_Mammoth.__init__` → param `mammoth_slot_dropout` + pasarlo a `MammothPatchEmbed`.
4. `train_dsmil.py` → `--mammoth_slot_dropout` (default 0.0, retro-compatible) + cableado en
   `build_model`.
**Sin tocar `forward` ni `clam_environ/`.** Dispara `reviewer` + **test CPU** obligatorio.

### 3.4 aux-loss de ruteo — **FUERA de esta pasada** (registrada para no perderla)
Se difiere a una 2ª iteración **condicionada** a que el Brazo 1 muestre señal (H1 o H_reg neto,
no banda plana). Diseño anticipado (para el reviewer, no se implementa ahora):
- Punto de inyección limpio: replicar el patrón `model_type=="dsmil"` de
  [train_dsmil.py:255-273](../../../scripts/train_dsmil.py) (término gated + métrica gated).
- Señal: `MammothPatchEmbed.forward` llama `self.mammoth(x, return_weights=True)` (devuelve
  `dispatch_weights`), computa la aux, la **stashea** en `self.last_aux`; el loop la lee vía
  `model.attention_net[0].last_aux` y suma `w_aux·L_aux` antes de `backward`. **No** se overridea
  el `forward` heredado (regla 2 / delta mínimo).
- Restricción: `return_weights` solo da `dispatch` (no `combine`) → la aux práctica es **sobre
  dispatch**, que es justo lo que gobierna `keep_slots=True` (acople natural). Formulación
  recomendada: **anti-starvation / cobertura** (penalizar parches con masa de dispatch agregada
  ≈ 0 → "ningún parche raro queda sin rutear"), la más alineada al mecanismo del colapso.
- **No** editar el paquete vendorizado (rompería el pin `fe36d4e`).

### 3.5 Preflight / containment
- `keep_slots=True` produce siempre 300 tokens ≥ `k_sample=8` → el bug topk (Workaround G) se
  vuelve imposible. **Igual se mantiene el preflight** y se **loguea el N de entrada** por slide
  (el bottleneck enmascara slides patológicamente chicas, no las arregla).
- `--results_dir` absoluto bajo `clam_testing2/`; GPU solo vía `sbatch`; cortesía single-GPU
  (hoy hay jobs ajenos de `nschiaff` en cola → esperar/coordinar).

### 3.6 Test CPU (estilo `tests/test_mammoth_cpu.py`)
Wiring de ambos brazos; **shapes** (`keep_slots=True` ⇒ salida del patch-embed `[300,512]`, A
`[3,300]`/`[2,300]`, M_pool `[n_clases,512]`); **el bag forward corre** y produce logits del nº
de clases correcto; smoke 1 época sin NaN. Para Brazo 2: verificar que `slot_dropout` solo actúa
en `train()` y es no-op en `eval()`.

---

## 4. Alcance — DECIDIDO

| | Qué corre | Código | En esta pasada |
|---|---|---|---|
| **Brazo 1** | `keep_slots=True` | 0 (flag existe) | **SÍ** |
| **Brazo 2** | `keep_slots=True + slot_dropout` | aditivo (~4 puntos) | **SÍ** (acoplado) |
| aux-loss cobertura | dispatch anti-starvation | patrón existente | **NO** (2ª iteración, condicionada) |

Sobre **2 tareas** (invasión = testbed de la regresión; tejido = régimen balanceado / mejor caso a priori).
Razón del acople 1+2: `slot_dropout` es barato y ataca el mismo mecanismo (sobreajuste a la
mayoritaria); correrlo junto evita una 2ª tanda de GPU. La aux-loss se difiere porque es la de
más código e incertidumbre, y su mejor formulación (cobertura sobre dispatch) **solo cobra
sentido con `keep_slots=True`** — primero confirmamos que el bottleneck mueve algo.

---

## 5. Orden de ejecución (estricto)

1. ✅ **Pre-registración** (este doc) — branch `feat/mammoth-keepslots`.
2. ⏳ **`reviewer`** sobre §0–4, **antes** de tocar `models_mammoth/` o el `.slurm`. Decide,
   junto a Sebastián, si la reapertura (§0) está habilitada. **Si NO → se detiene acá.**
3. ⏳ **Implementar** Brazo 2 (`slot_dropout` aditivo, §3.3) + `.slurm`
   (`scripts/run_obj3_mammoth_keepslots_kfold.slurm`, espejo del de obj2) + **test CPU** (§3.6).
4. ⏳ **`sbatch`** (GPU, branch `feat/mammoth-keepslots`, preflight, cortesía single-GPU) —
   solo los brazos nuevos sobre los splits reusados. **PARAR antes y confirmar con Ernesto.**
5. ⏳ Análisis paired (C1, C2) + diagnóstico de recall + `resultados.md` + memoria/Hallazgo.
   El `resultados.md` reporta los **3 puntos** (KSF baseline / Brazo 1 / Brazo 2) para que el
   efecto de `slot_dropout` sea **atribuible** (Brazo 2 vs Brazo 1 aísla el regularizador; Obs 4.b reviewer).

**Se PARA antes de:** el `sbatch`/GPU, el merge a `main`, y cualquier escritura en `clam_environ/`.

---

## 6. Qué NO afirma / límites

- `keep_slots=True` es config **CONCH-específica**; un null no condena la idea del cuello de
  botella con otro encoder/dataset.
- Un Δ>0 en **tejido** (balanceada) **no** generaliza a regímenes desbalanceados salvo que
  **invasión** también se mueva — por eso ambos subsets, no uno.
- Esto testea el **patch-embed**; no reabre el agregador (DSMIL, Hallazgo 11) ni el eje
  lenguaje+tile (PathPT, Hallazgo 13). Si todo da H_alt, refuerza "el cuello es el dato" cerrando
  el espacio de config de mammoth de forma más completa, no abre un eje nuevo.
- **No** es habilitante de la aux-loss: esa requiere su propio gate condicionado al resultado de
  esta pasada (§3.4, §4).

---

*Pre-registración escrita ANTES de cualquier código de training/modelo. El Brazo 1 es config-only
pero la reapertura (§0) exige reviewer + OK antes del `sbatch`. El Brazo 2 (slot_dropout) y el
`.slurm` se implementan recién tras el GO del reviewer.*

---

## 7. ADDENDUM — reviewer (2026-06-19)

**Veredicto: GO con observaciones.** El reviewer resolvió el punto de gobernanza 9.b: esto **NO
es una decisión revisitada 9.b estricta** (no reabre el mecanismo descartado con un valor nuevo —
eso lo habría bloqueado por falta de habilitante job-posterior), sino una **variante arquitectónica
materialmente distinta y no testeada** del patch-embed (`keep_slots=True` cambia el mecanismo:
cardinalidad N→300, salta la recombinación, introduce cuello de botella aprendido), **apuntada a un
modo de falla concreto y pre-registrado** (colapso a la mayoritaria, job 4246) — lo que la separa de
"vamos a probarlo igual". Carga de regla 9 estricta cumplida; paired verificado contra el código
real (flag cableado, `forward` genérico en M, baselines con predicciones por fold en disco).

**Observaciones incorporadas en este doc:** 2.a (rótulo tejido → "régimen balanceado", §2), 3.a
(traza de dims anclada al rearrange real, §1 + test CPU §3.6), 4.a (desempate bal_acc↔gap-recall →
manda el gap, §2), 4.b (reportar 3 puntos KSF/B1/B2, §5.5).

**Condiciones que QUEDAN PENDIENTES antes del `sbatch`** (no bloquean implementar Brazo 2 + test CPU):
1. **Co-firma de Sebastián** del encuadre "variante no testeada, no reapertura 9.b" — el GO del
   reviewer es necesario, **no suficiente** (gobernanza compartida, §0). **← decisión de Ernesto/Sebastián.**
2. **GPU libre** — hay jobs de `nschiaff` (4383 R, 4384 PD por Resources); aplica cortesía single-GPU.
