# Sprint 8 (B8) — objetivos, de la reunión del 24-jul-2026

Reunión del **viernes 24-jul-2026** con Sebastián y Benjamín, sobre la presentación
del Sprint 7 (interpretabilidad CLAM vs Mammoth). **Es la mejor reunión hasta ahora**
según Ernesto: quedó demostrado el entendimiento del mecanismo al explicar slots,
expertos, cabezas y el diagrama original del paper, que era exactamente lo que
Benjamín venía exigiendo ([[feedback-benjamin-entender-mammoth]]). Los mapas de calor
fueron el material central, tanto el de los 30 expertos como los de slots.

Este documento registra los cuatro encargos que salieron de esa reunión. **No es un
pre-registro**: los objetivos 2 y 3 tocan entrenamiento y exigen su propio prereg
(regla 9) + `reviewer` antes de tocar código o mandar un `sbatch`.

---

## 1. Escalar la medición de slots ocupados (encargo de Benjamín)

**Lo que dijo:** el promedio de **158.7 slots útiles de 300** se midió sobre **7
láminas**, y con ese n no generaliza al conjunto de la tarea. Hay que encontrar ese
número **con más datos**.

**Es una objeción correcta y ya estaba anticipada de nuestro lado.** La respuesta a Q1
(`sprints/B7_sprint7/respuesta_q1_expertos_slots.md`, §5 de
`resultados_interpretabilidad.md`) dice literalmente que con n=7 el número **describe,
no establece**, y que la dispersión (89.7 a 196.4) sigue al **tamaño de la lámina**
(Spearman ρ=0.750, p=0.052) y no a la tarea. Escalar el n es justamente lo que
convierte esa descripción en un resultado.

**Qué se escala y qué no:**

| Medida | n=7 | ¿Escala? |
|---|---|---|
| Expertos efectivos (`exp(H)` sobre los 30) | **30.0 / 30** en las 7, con `e50=15` y `e90=27` = los valores exactos del reparto uniforme | Sí, pero se espera que se confirme: es el resultado sólido y transversal a las 3 tareas |
| Slots efectivos (`exp(H)` sobre los 300) | **158.7 ± 34.6** | **Este es el que Benjamín pide** |
| Slots sobre la cota uniforme (1/300 = 0.333 %) | **63 a 96 por lámina**, concentran el 73 % del peso | Escala igual, es la misma pasada ([[cota-softmax-slots-uniforme]]) |
| Correlación con el tamaño de lámina | ρ=0.750, p=0.052 (n=7, no significativa) | Con n grande pasa a ser testeable de verdad |

**El camino técnico está despejado** (verificado hoy, 27-jul, sobre el código):

- `scripts/mammoth_interpretability.py` lee **features y coords del MISMO h5**
  (`load_feats_and_coords`, L128). La WSI `.svs` se abre **solo** para la miniatura,
  los overlays y los recortes de alta resolución (`openslide`, L230 en adelante).
- Por lo tanto **la medición de Q1 no necesita la WSI**: con el h5 alcanza. Eso saca
  de encima la restricción que limitó el Sprint 7 a 7 láminas TCGA (se eligieron por
  tener `.svs` disponible y estar bien clasificadas por ambos brazos).
- Lo caro de los ~10 min por lámina es el rasterizado de los 30 paneles del montage,
  no el forward. Un script que solo calcule `combine_weights` → entropía → `N_eff`
  debería correr en segundos por lámina.

**Plan propuesto:** script nuevo y reducido (`scripts/q1_slots_escalado.py` o similar)
que reuse `build_mammoth` + `load_feats_and_coords` de
`mammoth_interpretability.py`, sin openslide ni matplotlib, y barra **todas las
láminas de test de los 5 folds** de las 3 tareas (tipo n=2027, CDIS n=862, LVI n=836).
Salida: un CSV por lámina con `N_parches`, `N_eff_expertos`, `N_eff_slots`,
`slots_sobre_cota`, tarea, fold, cohorte, y el agregado por tarea. Con eso se responde
además, ahora sí con potencia, si la dispersión es por tamaño de lámina o por tarea.

**Restricciones a respetar:** CPU post-hoc, sin GPU. Si la corrida pasa de una hora,
va **desatada** con `setsid nohup` y reanudable marcando con el artefacto final
(workaround J, [[proceso-cpu-largo-desatado-setsid]]). Regla 9 **no aplica**: es
inferencia sobre checkpoints congelados, no toca modelo ni entrenamiento.

---

## 2. Entrenar los slots de MAMMOTH con nuestro dataset

**Lo que pidieron:** entrenar los slots de MAMMOTH con nuestro dataset.

**⚠ Discrepancia con el estado real del repo, a aclarar con Sebastián antes de
ejecutar** ([[surface-premise-discrepancies]]). Verificado hoy contra el código:

- `slot_embeds` es un `nn.Parameter` del paquete `mammoth` instalado
  (`clam_testing2/MAMMOTH/src/mammoth/mammoth.py:281`), inicializado al azar
  (`orthogonal_` y después `xavier_uniform_`, L284-285) y **entrenado de punta a punta
  con el resto del modelo**. No hay pesos pre-entrenados del paper en juego.
- El job **4589** (17-18 jul) entrenó `CLAM_MB_Mammoth` **desde cero sobre nuestros
  splits** (`tipo_histologico_4clases_ci_100` de Sebastián y los `_ci_reform` nuestros).
  O sea: **los slots que analizamos ya están entrenados con nuestro dataset.**

**Lecturas posibles del pedido, en orden de plausibilidad:**

1. **Analizar sobre nuestras láminas privadas, no sobre TCGA.** Las 7 del Sprint 7 son
   **todas TCGA** (`interp_slides.json`), porque necesitábamos el `.svs` para el
   overlay. Si lo que quieren es ver los slots sobre la cohorte de Environ, el pedido
   se solapa con el objetivo 1 y se resuelve barriendo las privadas. Hay que verificar
   la disponibilidad de WSI privadas si además quieren los mapas, no solo el número.
2. **Una etapa de pre-entrenamiento de los slots** (por ejemplo auto-supervisada, o
   congelar el resto y entrenar solo el ruteo). Eso sí sería un objetivo nuevo, con
   prereg propio.
3. Que en la reunión haya quedado la impresión de que los slots venían del paper. Si
   es esto, se cierra mostrando el `nn.Parameter` y el job 4589.

**Acción antes de codear:** preguntarle a Sebastián cuál de las tres es. No es
bloqueante para el objetivo 1 ni para el 3.

---

## 3. Grid de hiperparámetros: E y S, contra CLAM y contra Mammoth baseline

**Lo que pidieron:** pruebas de MAMMOTH + CLAM variando **cantidad de expertos y de
slots**, comparando contra **CLAM baseline** y contra **Mammoth baseline** con los
mismos hiperparámetros. Varias ramas, dejarlo corriendo un fin de semana.

Formaliza y amplía el eje que Sebastián ya había planteado el 23-jul: reducir uno con
el otro fijo a igual total, 27×10 contra 30×9 ([[mammoth-grid-expertos-slots]]). Ahora
es un grid con dos baselines.

**Lo que ya está listo (verificado hoy):**

- `scripts/train_dsmil.py` **ya expone las dos perillas**: `--mammoth_num_experts`
  (L223) y `--mammoth_num_slots` (L224), más `--mammoth_num_heads`,
  `--mammoth_slot_dim`, `--mammoth_slot_dropout` y `--mammoth_keep_slots`. **No hace
  falta tocar `models_mammoth/clam_mammoth.py` ni el harness** para correr el grid, lo
  que deja el cambio en configuración pura.
- Los splits del 4589 están y son los que hay que reusar para que la comparación quede
  pareada por construcción ([[patron-paired-comparison-reuso-splits]]).
- El `.slurm` del 4589 (`sprints/B7_sprint7/run_b7_mammoth_interp_kfold.slurm`) es el
  molde: 30 runs, 3 tareas × 2 brazos × 5 folds.

**Presupuesto, que es la restricción real.** El 4589 corrió 30 runs en ~20 h (lanzado
el 17-jul 18:12, cerrado el 18-jul 14:20), o sea **~40 min por run**. Un fin de semana
de GPU son ~48 h, es decir **~70 runs**. Con 5 folds y 3 tareas, cada configuración
del grid cuesta 15 runs:

| Alcance | Configs | Runs | Horas estimadas |
|---|---|---|---|
| 3 tareas × 5 folds × (CLAM + Mammoth 30×10 + 2 configs nuevas) | 4 brazos | 60 | ~40 h |
| 3 tareas × 5 folds × (CLAM + Mammoth 30×10 + 4 configs nuevas) | 6 brazos | 90 | ~60 h |
| 1 tarea × 5 folds × 8 configs de grid | 8 | 40 | ~27 h |

Es decir: **o pocas configuraciones sobre las 3 tareas, o un grid ancho sobre una sola
tarea.** Las dos no entran en un fin de semana. Hay que elegir, y la elección es de
diseño experimental, no de infraestructura. Candidata natural para la tarea única:
**CDIS `_ci_reform`**, que es donde apareció el dato abierto del 4589 (Δbal_acc +0.074,
5/5 folds) y donde una réplica con más configuraciones aporta doble.

**Pendiente antes del `sbatch`:** pre-registro con hipótesis, métrica, subset y
dirección esperada (regla 9 y 9.a) + `reviewer`. Ojo con **regla 9.b**: si el grid se
plantea como reapertura del eje de rendimiento cerrado en el Hallazgo 12, necesita
citar el hallazgo habilitante. El dato abierto del CDIS `_ci_reform` es candidato a
serlo, pero eso hay que escribirlo explícito en el prereg, no darlo por sentado. Como
eje de **capacidad y entendimiento** (cuántos E y S hacen falta) no reabre nada, que
es como venía planteado el 23-jul.

**Nota operativa sobre "varias ramas":** el árbol de trabajo es compartido y un job
relee su código y sus inputs del working tree en cada invocación. **No se cambia de
rama con un job corriendo** (workaround H,
[[working-tree-compartido-job-en-curso]]). Si el fin de semana corren varios brazos,
todo lo que el job lee tiene que estar commiteado en la rama que queda checked out,
idealmente `main`.

---

## 4. Papers a estudiar esta semana

Para discutirlos con Sebastián en la reunión de esta semana:

1. **Hover-Net** — *Simultaneous segmentation and classification of nuclei in
   multi-tissue histology images* (Graham et al., Medical Image Analysis 2019).
2. **SI-MIL** — *Taming Deep MIL for Self-Interpretability in Gigapixel
   Histopathology* (Kapse et al., CVPR 2024).
3. *Further predictive value of lymphovascular invasion explored via supervised deep
   learning for lymph node metastases in breast cancer*.

**Estado (27-jul, con autorización de Ernesto): 2 de 3 descargados en esta carpeta.**
Ficha completa, citas BibTeX y abstract del tercero: [`papers_b8.md`](papers_b8.md).

| Paper | Archivo | Estado |
|---|---|---|
| Hover-Net | `hovernet_graham2019.pdf` | ✅ arXiv:1812.06499v5 |
| SI-MIL | `simil_kapse2024.pdf` | ✅ arXiv:2312.15010v2 |
| LVI → metástasis ganglionar | (sin PDF) | ⚠ Human Pathology 131:26-37 (2023), DOI `10.1016/j.humpath.2022.11.007`. **De suscripción**, sin PMC ni preprint (verificado en Europe PMC). Requiere acceso institucional UTFSM o de Environ |

**Por qué encajan con lo que estamos haciendo, a confirmar leyéndolos:**

- **SI-MIL** es el más directo: es interpretabilidad *self-* dentro de un MIL, o sea el
  mismo eje del Sprint 7 pero con otra estrategia. Sirve de contraste con lo que hicimos
  post-hoc sobre expertos y slots.
- **Hover-Net** trabaja a nivel de **núcleos**, no de parche. Es la vía más creíble
  para poner nombre real al tejido que hoy solo nombramos por lectura visual, que es
  la salvedad que arrastramos desde OBJ-A y que sigue sin sign-off de patólogo
  ([[mammoth-interpretabilidad-objA]], [[slot-unidad-de-morfologia]]).
- El tercero toca **invasión linfovascular**, que es una de las 3 tareas del Sprint 7
  (`invasion_linfatica_vascular`), y además apunta a metástasis ganglionar, que es el
  objetivo clínico del proyecto.

---

## 5. Qué no se afirma

- Que 158.7 sea el número de slots útiles de la tarea. **Es de 7 láminas.** Ese es
  justamente el encargo 1.
- Que los slots ya entrenados con nuestro dataset cierren el encargo 2 sin
  preguntar. Primero se aclara qué pidieron.
- Que el grid de E y S reabra el eje de rendimiento. Mientras se plantee como pregunta
  de capacidad, no lo reabre; si se plantea como búsqueda de mejora, entra regla 9.b.
