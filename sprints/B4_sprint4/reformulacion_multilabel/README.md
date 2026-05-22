# Reformulación multi-label de `microcalcificaciones` — scaffolding

> **Sprint B4 — preparación de la próxima implementación de entrenamiento.**
> Rama `feature/sprint4-reformulacion-multilabel`.
>
> Resuelve el **hallazgo de fondo** del baseline (job 4098): las 8 clases
> de `microcalcificaciones_pth` son un **multi-etiqueta aplastado** —
> 3 preguntas binarias de tejido {carcinoma invasivo, CDIS, tejido no
> neoplásico} comprimidas en 8 clases-combinación mutuamente excluyentes.
> Detalle del hallazgo: [`../objetivo_1_baseline/resultados.md`](../objetivo_1_baseline/resultados.md).
> Argumento de por qué la reformulación es la dirección correcta:
> [`../objetivo_3_modulo_mil_alternativo/investigacion/05_papers_eduardo_desbalance.md`](../objetivo_3_modulo_mil_alternativo/investigacion/05_papers_eduardo_desbalance.md).
>
> **Estado (21 may 2026): run PRELIMINAR lanzado.** El scaffolding pasó a
> ejecución como **corrida preliminar** — para llevar números reales a la
> reunión. La *interpretación y adopción* de la reformulación siguen
> gateadas por las precondiciones (ver abajo); el run preliminar no las
> pre-decide, solo produce evidencia.
>
> No se modifica `clam_environ/` (read-only): se usan sus CSVs/splits/task
> configs tal cual.

---

## Hallazgo: la reformulación YA está implementada por el equipo

Al preparar este scaffolding se descubrió que el equipo de Sebastián
**ya construyó** la infraestructura de las 3 tareas binarias. No hay que
crearla — hay que **verificarla, documentarla y planificar el
entrenamiento**. Por eso este scaffolding gira sobre lo existente.

### Infraestructura existente (auditada el 21 may 2026)

| Artefacto | Ubicación (`clam_environ/`, **read-only**) | Estado |
|---|---|---|
| Task configs | `main.py` → `microcalcificaciones_en_{carcinoma_invasivo,cdis,tejido_no_neoplasico}_pth` | ✅ registradas (`label_dict={}` → requieren `--auto-label-dict`) |
| Task configs `_balance` | `main.py` → idem `..._pth_balance` | ✅ registradas |
| 3 CSVs binarios | `environ/csv/dataset_microcalcificaciones_en_<tejido>_label.csv` | ✅ existen (12 may) |
| 3 CSVs `_balance` | `environ/csv_balance/dataset_microcalcificaciones_en_<tejido>_label.csv` | ✅ existen (20 may) — **byte-idénticos a los de `csv/`** |
| 3 splits | `environ/splits/microcalcificaciones_en_<tejido>_pth_100/` | ✅ existen, estratificados |
| 3 splits `_balance` | `environ/splits/microcalcificaciones_en_<tejido>_pth_balance_100/` | ✅ existen |

> **Nota sobre `_balance`.** Para estas 3 tareas, los CSVs de `csv_balance/`
> son **byte-idénticos** a los de `csv/` (`diff` da identical). Si la
> variante `_balance` aporta algo, está en los **splits**
> (`_pth_balance_100`), no en el CSV. Confirmar con Sebastián qué hace
> exactamente el sufijo `_balance` — pregunta para la reunión.

### Verificación — los CSVs están bien derivados

`scripts/verify_binary_microcalc_csvs.py` re-deriva las etiquetas binarias
de forma **determinística** desde el CSV de 8 clases y las cross-chequea
contra los CSVs existentes. Resultado (21 may 2026):

```
política no_identificado: excluir
  carcinoma_invasivo    filas 333 | si  68  no 265 | MATCH (etiquetas idénticas)
  cdis                  filas 333 | si 121  no 212 | MATCH (etiquetas idénticas)
  tejido_no_neoplasico  filas 333 | si 195  no 138 | MATCH (etiquetas idénticas)
RESULTADO: los CSVs existentes coinciden con la derivación determinística.
```

Los 3 CSVs existentes son **correctos**: coinciden 1:1 con el parseo
determinístico del nombre de la clase de 8-clases.

---

## La decisión sobre `no_identificado` — ya tomada (`excluir`)

Los 3 CSVs tienen **333 filas**, no 3072. Es decir: las **2739 slides
`no_identificado` fueron EXCLUIDAS**. El dataset binario es solo el
subconjunto de **333 slides con al menos una localización de tejido**.

Implicación — el **negativo** de cada tarea binaria NO es `no_identificado`;
es *"slide con microcalcificación, pero en otro tejido"*. La tarea binaria
real es: **dado un slide que tiene microcalcificación, ¿está en el tejido
X?**

Esto tiene dos consecuencias buenas:

1. **Esquiva la ambigüedad de `no_identificado`.** No importa si
   `no_identificado` significa "sin microcalcificación" o "con
   microcalcificación sin ubicar": al excluirlo, no contamina las
   etiquetas binarias.
2. **Tareas mucho más balanceadas.** Sobre 333 (no sobre 3072):

   | Tarea | positivos (`si`) | % positivos |
   |---|---|---|
   | carcinoma_invasivo | 68 / 333 | 20,4 % |
   | cdis | 121 / 333 | 36,3 % |
   | tejido_no_neoplasico | 195 / 333 | 58,6 % |

   Comparar con el régimen del 8-clases, donde 4 clases tenían **1 sola
   muestra** en val/test. Acá la tarea más desbalanceada (carcinoma,
   20 %) es perfectamente entrenable.

**Pero la interpretación clínica sigue abierta.** El equipo *codificó*
`excluir`; falta *ratificarlo* en la reunión. Si la reunión decide que
`no_identificado` debe ser un negativo limpio (interpretación
alternativa), el script regenera la variante:

```bash
python scripts/verify_binary_microcalc_csvs.py \
    --eight-class-csv /.../environ/csv/dataset_microcalcificaciones_label.csv \
    --no-identificado negativo \
    --out-dir sprints/B4_sprint4/reformulacion_multilabel/csv_negativo
```

(Esa variante tiene 3072 filas y positivos 2,2 % / 3,9 % / 6,3 % — mucho
más desbalanceada. No se versiona: es regenerable y determinística.)

---

## Pedagogía de CSV — los 3 binarios (formato `CLAUDE.md`)

```
CSV: dataset_microcalcificaciones_en_<tejido>_label.csv   (×3: carcinoma_invasivo, cdis, tejido_no_neoplasico)
Path en server: clam_environ/environ/csv/  (read-only)  ·  copia en csv_balance/ byte-idéntica
Schema (columnas y tipos):
  - case_id : str   — id de paciente (ej. patient_0). Agrupa slides del mismo caso.
  - slide_id: str   — id de slide; matchea environ/features/pt_files/<slide_id>.pt
  - label   : str   — 'si' | 'no'  (¿microcalcificación en este tejido?)
Filas: 333  (subconjunto con localización; no_identificado excluido)
Producido por: pipeline del equipo (script no publicado). Re-derivable y
  verificable con scripts/verify_binary_microcalc_csvs.py.
Consumido por: main.py vía Generic_MIL_Dataset, task microcalcificaciones_en_<tejido>_pth.
Ejemplo (head -3 de carcinoma_invasivo):
  case_id,slide_id,label
  patient_0,B25-158771_2,no
  patient_0,B25-158771,no
Trampas conocidas:
  - label_dict={} en main.py -> OBLIGATORIO --auto-label-dict (ordena alfabético: no=0, si=1).
  - 1 de las 333 slides no tiene .pt (150012-2-3 en carcinoma) -> el dataloader la salta.
  - csv_balance/ es byte-idéntico a csv/ -> el sufijo _balance NO está en el CSV.
```

---

## Estrategia de splits

Los 3 splits `microcalcificaciones_en_<tejido>_pth_100/` ya existen y son
**uno por tarea, estratificado sobre su propia etiqueta binaria**.
Descriptores (verificados — suman a los totales de los CSV):

| Tarea | train no/si | val no/si | test no/si |
|---|---|---|---|
| carcinoma_invasivo | 210 / 54 | 28 / **7** | 27 / **7** |
| cdis | 169 / 96 | 21 / **12** | 22 / **13** |
| tejido_no_neoplasico | 112 / 155 | 13 / **20** | 13 / **20** |

**Esto arregla el régimen de evaluación roto.** El peor caso ahora es
**7 positivos en val y 7 en test** (carcinoma) — vs las clases de **n=1**
del modelo 8-clases. Con 7+ positivos, un AUC one-vs-rest y un balanced
accuracy dejan de ser ruido.

Decisiones de splits:

- **3 corridas binarias independientes** (la validación de primer paso,
  ver `05_…desbalance.md` §1.3): cada tarea usa **su propio split** —
  correcto, porque cada uno está estratificado sobre su etiqueta. No se
  comparte split.
- **Modelo multi-task con backbone compartido** (paso posterior, ruta
  PCGrad): ahí **sí** haría falta **un split compartido** entre las 3
  tareas (mismas slides en train/val/test) para que la comparación
  multi-task sea válida. Ese split compartido **no existe todavía** —
  habría que generarlo estratificando sobre las 8 clases originales (así
  cada proyección binaria queda estratificada). Pendiente, solo si se
  toma la ruta multi-task.
- **Bug `topk` / preflight** (workaround G de `CLAUDE.md`): antes de
  entrenar con `--inst_loss svm` hay que verificar que ninguna slide de
  **train** tenga `< B` parches. Es **obligatorio** el bloque preflight
  en el `.slurm`. Si el preflight marca slides, filtrar el split con
  `scripts/filter_split_by_minpatch.py` hacia `splits_local/` (igual que
  el baseline B=8).

---

## Archivos de este directorio

| Archivo | Contenido |
|---|---|
| `README.md` | Este archivo: hallazgo, auditoría, splits. |
| [`plan_entrenamiento.md`](plan_entrenamiento.md) | Plan de entrenamiento con hipótesis + métrica de éxito predefinidas (regla 9). |
| [`train_microcalc_3binarios.slurm`](train_microcalc_3binarios.slurm) | `.slurm` de las 3 corridas binarias (loop secuencial). **Lanzado como run PRELIMINAR el 21 may 2026.** |

Script asociado (en `scripts/`):
[`verify_binary_microcalc_csvs.py`](../../../scripts/verify_binary_microcalc_csvs.py)
— verifica / regenera los CSVs binarios de forma determinística.

---

## Precondiciones — qué gatea el run preliminar vs la adopción

El **run preliminar** (21 may 2026) se lanzó para tener números reales en
la reunión. Lo que **sigue gateado** es la *adopción* de la reformulación:

1. **La reunión confirma la reformulación** en 3 tareas binarias como la
   dirección para `microcalcificaciones`. (El equipo ya la implementó, así
   que es muy probable — pero la decisión se ratifica en la reunión.)
2. **Se ratifica qué es `no_identificado`.** El equipo eligió `excluir`; la
   reunión debe confirmar esa interpretación clínica. Si se decide lo
   contrario, regenerar los CSVs con `--no-identificado negativo` y los
   splits correspondientes, y **re-correr** — los resultados preliminares
   quedarían obsoletos.

Por eso **todo resultado de este run se reporta como PRELIMINAR**: válido
como evidencia para la reunión, no como conclusión cerrada.

---

## Preguntas para la reunión

Extienden las de
[`../objetivo_3_modulo_mil_alternativo/investigacion/04_riesgos_y_preguntas_reunion.md`](../objetivo_3_modulo_mil_alternativo/investigacion/04_riesgos_y_preguntas_reunion.md)
§C y las de los docs `05_`/`06_`.

| # | Pregunta | Qué desbloquea |
|---|---|---|
| 16 | ¿Registrar una **task plana de 7 clases** sobre las **mismas 333 slides** (las 7 combinaciones de tejido, sin `no_identificado`), para una comparación **plano-vs-binario perfectamente controlada** (mismo subconjunto de datos, misma métrica)? Hoy está **bloqueada**: registrar la task exige editar `clam_environ/main.py`, que es read-only. | Permitiría medir el efecto de la reformulación aislado del cambio de subconjunto de datos. Requiere que el equipo (Sebastián) registre la task, o un `main.py` wrapper local. |
| 17 | ¿Qué hace exactamente el sufijo `_balance` de las tasks? Los CSVs `csv_balance/` son byte-idénticos a `csv/` — la diferencia, si existe, está en los splits `_pth_balance_100`. | Aclara si conviene usar las variantes `_balance` en vez de las `_pth`. |
