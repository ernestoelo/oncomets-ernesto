# Auditoría de coherencia — apertura del B8 (27-jul-2026)

Sesión de registro de la reunión del 24-jul y apertura del Sprint 8. La auditoría cubre
lo escrito hoy (`sprints/B8_sprint8/`, `progress/current.md`, memorias nuevas y sus
addendums) contra `CLAUDE.md`, el índice de memorias y los docs del B7.

**Contexto operativo:** rama `main`, árbol limpio antes de empezar. Job **4684**
(`entrenamiento_multimodal`) corriendo bajo la cuenta compartida `sdonoso`, pero desde
`/media/administrador/Storage1/sdonoso/Test_D/D_abs` y con su propio `train.slurm`: **no
lee nuestro árbol**, así que no hay riesgo de workaround H. Aun así la auditoría es
documental y **no se hizo ningún cambio de rama** (cero checkouts).

## Resumen

| id | Hallazgo | Tipo | Severidad | Acción |
|---|---|---|---|---|
| A1 | `progress/current.md:14` sigue diciendo «Sprint actual: B7» con el B7 ya presentado y el B8 abierto | stale | media | Editar el encabezado de forma aditiva |
| A2 | `CLAUDE.md` Hallazgo 12 declara «Q1 del B7 **CERRADA**»; Benjamín objetó que el número de slots no generaliza con n=7 | stale parcial | **alta** | ADDENDUM fechado, sin reescribir lo anterior |
| A3 | ¿`N_eff`=158.7 contradice la cota de 63-96 slots ahora que se escala? | reconciliación | media | Verificado: **no se contradicen**. Sin cambios |
| A4 | La discrepancia de «entrenar los slots» y sus citas `file:line` | verificación | alta | Verificado en 3 fuentes. Sin cambios |
| A5 | `sprint7-interpretabilidad-clam-vs-mammoth` no registra el desenlace (presentado, salió bien) ni que el número de slots pasa a B8 | stale | baja | ADDENDUM breve |
| A6 | Pendientes del handoff del 23-jul que la reunión volvió obsoletos | stale | media | Se resuelven en el handoff nuevo, no en el repo |

---

## A1 — «Sprint actual: B7» quedó desactualizado

- `progress/current.md:14`: `## Sprint actual: B7 / Sprint 7 ...`, abierto el 13-jul.
- El B7 **ya se presentó el 24-jul** y hoy se abrió el B8
  (`sprints/B8_sprint8/objetivos_sprint8.md`), que además ya tiene su carpeta y sus papers.
- La sección nueva del 24-jul está al final del archivo, a 780 líneas del encabezado: quien
  entre a leer arriba se lleva la idea equivocada.

**Por qué no se cierra el B7 del todo:** la convención del repo dice que al cerrar un
sprint su resumen pasa a `history.md`, y eso es decisión de Ernesto (el B6 sigue con el
mismo pendiente anotado en la cabecera del archivo). Además quedan pendientes vivos del
deck. **Fix aplicado:** edición aditiva del encabezado dejando constancia de que el B7 se
presentó y de que el foco pasó al B8, sin mover nada a `history.md`.

## A2 — «Q1 CERRADA» ya no es exacto (el hallazgo importante de la sesión)

- `CLAUDE.md:808`: «**Q1 del B7 CERRADA** (19-jul, n=7 láminas, CPU post-hoc)», con los
  dos números, expertos 30.0/30 y slots 158.7/300.
- La reunión del 24-jul la reabre **a medias**: Benjamín observó que 158.7 sale de 7
  láminas y **no generaliza** al dataset de la tarea.

**Qué sobrevive y qué no**, que es lo que hay que dejar escrito para que otra sesión no lo
confunda:

| Resultado | Estado tras el 24-jul |
|---|---|
| Expertos **30.0 de 30**, con `e50=15` / `e90=27` = los valores del reparto uniforme, idénticos en las 3 tareas | **En pie.** Es el resultado sólido y transversal; nadie lo objetó |
| **E=30 no está sobredimensionado** y el margen de recorte está en **S** | **En pie**, se apoya en lo anterior |
| Slots **158.7 de 300** como número de la tarea | **Pendiente de escalar.** Es el encargo 1 del B8 |
| La dispersión sigue al **tamaño de la lámina** (ρ=0.750, p=0.052) | Descriptivo con n=7; con n grande pasa a testeable |

El propio resultado ya llevaba la salvedad («con n=7 describe, no establece»), así que
esto **no es una corrección**: es que el sprint siguiente ejecuta lo que la salvedad pedía.
**Fix aplicado:** ADDENDUM fechado en el Hallazgo 12, sin tocar el texto original (regla de
integridad de pre-registración: lo anterior queda como registro histórico).

## A3 — `N_eff` 158.7 contra la cota de 63-96: verificado, no hay contradicción

Chequeado porque el B8 los pone en la misma tabla y podían leerse como cifras rivales.

- `CLAUDE.md:840` ya lo reconcilia explícitamente: «Los 85 (concentran) y el `N_eff` 159
  (cuenta cada slot en proporción a su peso) **no se contradicen**, miden cosas distintas».
- `N_eff = exp(H)` pesa cada slot por su peso y no tiene parámetro libre.
- La cota **1/300 = 0.333 %** cuenta cuántos slots superan el reparto uniforme: 63 a 96 por
  lámina, que concentran el 73 % del peso.
- La tabla de `objetivos_sprint8.md` §1 las lista como **filas separadas**, cada una con su
  definición, y aclara que ambas salen de la misma pasada. **Sin cambios.**

## A4 — La discrepancia de «entrenar los slots»: registrada y con las citas verificadas

Registrada en tres lugares y sin contradicción entre ellos:
`sprints/B8_sprint8/objetivos_sprint8.md` §2, la sección del 24-jul de
`progress/current.md`, y la memoria `reunion-24jul-encargos-b8`. Las tres dicen lo mismo:
el pedido choca con el estado del repo, hay tres lecturas posibles y **se pregunta antes de
codear** ([[surface-premise-discrepancies]]).

Citas verificadas hoy contra el código, una por una:

| Cita | Verificado |
|---|---|
| `MAMMOTH/src/mammoth/mammoth.py:281-285` — `slot_embeds` es `nn.Parameter`, init `orthogonal_` y después `xavier_uniform_` | ✅ |
| `scripts/train_dsmil.py:223-224` — `--mammoth_num_experts` / `--mammoth_num_slots` | ✅ |
| `scripts/mammoth_interpretability.py:128` — `load_feats_and_coords` lee features **y** coords del mismo h5 | ✅ |
| Job 4589 entrenó Mammoth desde cero sobre nuestros splits | ✅ contra `progress/current.md` y los `results/b7_mammoth_interp/` |

**Sin cambios.**

## A5 — La memoria del Sprint 7 no registra el desenlace

`sprint7-interpretabilidad-clam-vs-mammoth` describe el sprint como ejecutado (job 4589,
heatmaps, Q1) pero no dice cómo terminó ni que el número de slots pasa al B8. **Fix
aplicado:** ADDENDUM breve con el desenlace y el puntero a
[[reunion-24jul-encargos-b8]].

## A6 — Pendientes del handoff del 23-jul que la reunión dejó obsoletos

`.handoffs/handoff_B7_20260723_2209.md` §7 lista 13 pendientes, de los que **8 eran
decisiones sobre el deck ofrecidas antes de la reunión** (§7.4 a §7.9, §7.11, §7.12). El
deck se presentó el 24-jul y salió bien, así que dejaron de ser decisiones pendientes:
sobreviven solo si el deck se reusa o se comparte. Dos más quedaron cumplidos de hecho
(validarlo en PowerPoint, §7.2; y el repaso pedagógico de Mammoth, §7.3, que la propia
reunión demostró cumplido). **No es un defecto del repo**, es el handoff arrastrando
pendientes efímeros ya vencidos: se resuelve al escribir el handoff nuevo, marcando cuáles
sobreviven ([[verificar-antes-de-pedir-dato]]).

Sobreviven de verdad: el **sign-off de patólogo** (§7.13, y ahora conecta con Hover-Net),
el pie engañoso de la lámina 18 (§7.12, es exactitud factual y aguanta mientras el deck
exista) y regenerar los PNG en Barlow (§7.1, solo si el deck se reusa).

---
---

# Segunda pasada — cierre de la sesión de HoVer-Net (31-jul-2026, tarde)

Alcance **acotado al cierre de esta sesión**, no una auditoría de la base entera. Cubre lo
escrito hoy sobre HoVer-Net (`hovernet_estudio.md`, `papers_b8.md` §1, la memoria nueva y el
índice compactado) contra `CLAUDE.md`, las memorias de interpretabilidad y el registro de la
reunión del 24-jul.

**Contexto operativo:** rama `main`, sincronizada con `origin/main`, árbol limpio.
**Sin jobs propios** en `squeue` (sí ajenos: `capstone` 4736/4749 corriendo, 4750/4751
encolados), así que no aplica workaround H y no se hizo ningún checkout. **Sesión paralela
activa** bajo la misma cuenta trabajando el deck de SI-MIL: sus archivos se dejaron
intactos y los commits de hoy fueron todos con path explícito.

## Resumen

| id | Hallazgo | Tipo | Severidad | Acción |
|---|---|---|---|---|
| B1 | `CLAUDE.md` «Paths críticos» no lista `sdonoso/hover_net/`, un hermano nuevo de `sgaete` que una sesión futura va a encontrar con un `find` | stale | media | Línea aditiva en el árbol de paths |
| B2 | `reunion-24jul-encargos-b8` §4 da Hover-Net como «paper a leer»; está leído y además ya corre en el servidor | stale | media | ADDENDUM fechado, sin reescribir el encargo |
| B3 | ¿El geojson anotado invalida el «sign-off de patólogo pendiente» de OBJ-A? | reconciliación | **alta** | Verificado: **no lo invalida**. Puntero, sin tocar la afirmación |
| B4 | `progress/current.md` no tiene la sesión de HoVer-Net (la paralela escribió la suya) | stale | media | Sección nueva al final, sin tocar la ajena |

---

## B1 — `hover_net/` no está en el mapa de paths

- `CLAUDE.md` § «Paths críticos» dibuja el árbol de `/media/administrador/Storage1/sdonoso/`
  con `clam_environ/`, `clam_testing/` y `clam_testing2/`. No menciona `hover_net/`.
- Verificado hoy: `/media/administrador/Storage1/sdonoso/hover_net/` existe, es de **`sgaete`**
  y tiene trabajo vivo (jobs del 29 y 30-jul). Es exactamente el caso que
  [[paths-absolutos-fuera-del-repo]] anticipa: un hermano, no un subdirectorio.
- La regla 3 protege `clam_testing/` por nombre; este directorio cae bajo la misma lógica
  (workspace ajeno y activo) pero no está nombrado en ningún lado.
- **Acción**: línea aditiva en el árbol de paths, con el puntero a la memoria. No se toca la
  regla 3 ni su redacción (edición aditiva de reglas duras).

## B2 — El encargo 4 daba Hover-Net como pendiente de lectura

- `reunion-24jul-encargos-b8` §4: *«Tres papers para discutir con Sebastián… 2 de 3
  descargados»*, con Hover-Net descrito por su motivación, no por su contenido.
- Hoy quedó leído completo y, más importante, el terreno está más adelante que el encargo:
  ya está instalado y corriendo.
- **Acción**: ADDENDUM fechado en esa memoria más el enlace a la nueva. **No se reescribe**
  el texto del encargo: es el registro de lo que se pidió en la reunión y vale como
  histórico (misma criterio que se usó con la pre-registración).

## B3 — El geojson anotado NO cierra el sign-off pendiente

Es el punto delicado de esta pasada, porque la tentación es cantar victoria.

- `mammoth-interpretabilidad-objA:55-63` afirma dos cosas: **(1)** *«NO tenemos anotación de
  tejido por parche»* y **(2)** *«Pendiente sign-off de patólogo»*, con la instrucción
  explícita de no presentar «e8 = epitelio tumoral» como hecho anotado.
- `slot-unidad-de-morfologia:60,98` repite lo mismo para los slots.
- Lo encontrado hoy es `129741.bif - GDT.geojson`: **61 polígonos de región** sobre **una**
  lámina.

**Las dos afirmaciones siguen siendo correctas, y por tres razones distintas:**

1. **Región ≠ parche.** Son 61 polígonos dibujados a mano, no una etiqueta por cada uno de
   los miles de parches de la lámina. Habría que intersectar geometrías para derivar algo
   por parche, y lo que quede afuera de los 61 polígonos sigue sin etiqueta.
2. **Una lámina no es la cohorte.** OBJ-A midió sobre TCGA-BRCA; esta es una privada.
3. **No sabemos quién firmó.** Verificado además que el archivo **no lo produce el pipeline
   de `sgaete`** (sus exportaciones van a `output/<run>/qupath_regions/` y ninguno de sus
   scripts menciona ni «GDT» ni esta lámina), así que es una anotación **traída de afuera**.
   Eso lo hace más probable que sea de un patólogo, pero probable no es verificado.

- **Acción**: **no se toca ninguna de las dos afirmaciones.** Se agrega en
  `mammoth-interpretabilidad-objA` un puntero de una línea a la memoria nueva, diciendo que
  apareció un **candidato** a material de sign-off y qué habría que preguntar. El estado
  sigue siendo «pendiente».

## B4 — La sesión de HoVer-Net no está en `progress/current.md`

- La sesión paralela escribió su propia entrada (`## Sesión del 31-jul-2026 — el deck de
  SI-MIL recortado a 14 láminas`, línea 1094) y registró en su cierre que había detectado
  archivos de una sesión ajena sin commitear.
- **Acción**: sección nueva al final del archivo, **sin tocar** la de la sesión paralela.
  Las dos entradas del 31-jul conviven, distinguidas por el sufijo «(tarde)», que es la
  convención que el archivo ya usa.
