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

---

# Tercera pasada — cierre de la sesión del grid E×S (2-ago-2026, noche)

Auditoría acotada, del tamaño de la sesión: el grid quedó lanzado y sus hallazgos ya se
escribieron en el pre-registro, en `progress/current.md` y en la memoria del eje, así que lo
que falta registrar son dos cosas que aparecieron al cerrar, más una incoherencia que se cruzó
en el camino.

**Contexto operativo:** rama `main`, job **4774** (nuestro, grid E×S) **corriendo**. La
auditoría es documental y toca solo archivos que el job no lee (`progress/`, `sprints/`,
memorias, `.claude/skills/`). **Cero checkouts** (workaround H).

| id | Hallazgo | Tipo | Severidad | Acción |
|---|---|---|---|---|
| C1 | El repo tiene «Reunión confirmada: viernes 07/08/2026» en 3 lugares; Ernesto avisó el 2-ago que la reunión con Sebastián es **mañana lunes 3-ago** | stale parcial | **alta** | Registrar la del 3-ago **sin borrar** el registro del 07/08 |
| C2 | Encargo nuevo de Ernesto: **3 papers** para subir métricas en tareas específicas como mitosis, en una **rama aparte de CLAM**, especializándose con la información del patólogo sobre las etiquetas | registro | **alta** | Anclarlo donde ya vive su contexto: objetivo 5 y familias B/C/D |
| C3 | La skill `@knowledge-audit` dice crear branch nueva «si hay un job GPU corriendo (workaround H)», que es **al revés** de lo que manda el workaround H | contradicción | media | Corrección concisa de esa línea |

## C1 — La fecha de la reunión

- Lo que dice el repo: `sprints/B8_sprint8/reunion_31jul_redireccion.md:5`,
  `progress/current.md:1088` y `:1123`, y la memoria `reunion-24jul-encargos-b8` (ADDENDUM
  31-jul) fijan **viernes 07/08/2026**, y el deck de SI-MIL se construyó para esa fecha.
- Lo que dice Ernesto el 2-ago: hay reunión con Sebastián **mañana, lunes 3-ago**.
- **Lo que NO se sabe y no se inventa**: si la del 3-ago **reemplaza** a la del 07/08, si es
  una reunión adicional, o si el 07/08 quedó obsoleto desde la del 31-jul. El handoff anterior
  ya arrastraba esta duda y la dejaba explícitamente en manos de Ernesto.
- **Acción**: registrar la reunión del **lunes 3-ago** como un hecho nuevo y fechado, dejando
  el registro del 07/08 intacto y marcado como «sin resolver si sigue en pie». No se toca la
  lámina de título de ningún deck: eso depende de la respuesta que solo Ernesto tiene.

> **RESUELTO el lunes 3-ago-2026, 15:30, por Ernesto. C1 se cierra.**
> **La reunión del lunes 3-ago no ocurrió** (se movió o se canceló) y **queda en pie la del
> viernes 07/08/2026**, que es la que el repo ya tenía anotada en los tres lugares. O sea que
> los tres registros del 07/08 **no estaban stale**: eran correctos, y la del 3-ago era la
> excepción. La decisión de no borrarlos fue la correcta.
>
> **Consecuencias**: el deck de SI-MIL construido para el 07/08 **sigue apuntando a la fecha
> correcta** y no hay lámina de título que corregir; y el material de los papers, que el
> handoff daba por urgente para hoy, pasa a tener hasta el viernes. Se entregó igual, en el
> formato que pidió Ernesto: [`../tareas_geometricas/hojas_reunion.md`](../tareas_geometricas/hojas_reunion.md).

## C2 — El encargo de los 3 papers

- **Dónde ancla**: no es un encargo huérfano. `tareas_geometricas/README.md` §3 ya tiene las
  **cuatro familias de respuesta** (A operador de agregación, B campo de visión, C unidad de
  representación del parche al núcleo, D detector dedicado con anotaciones de objeto), y el
  ADDENDUM 31-jul de [[reunion-24jul-encargos-b8]] ya abrió el **objetivo 5**, «ramas aparte
  de CLAM dedicadas a mitosis y grado nuclear». El encargo nuevo es **la búsqueda
  bibliográfica que le faltaba a ese objetivo**.
- **Lo que el resultado del 1-ago ya decidió sobre el encuadre**: la atención **sí** cae sobre
  las mitosis (AUC 0.890 ± 0.039) y el modelo igual responde mal, así que la familia **A**
  perdió su motivación principal y los papers tienen que apuntar a **B, C y D**, no a
  reemplazar el operador de agregación.
- **La parte de «con la información del patólogo sobre las etiquetas»** conecta con la familia
  **D** y con [[anotaciones-patologo-qupath]]: el geojson de 129741 son **positivos
  parciales** (lo no marcado no es negativo) y está en coordenadas que no son las de openslide.
  Un paper que pida supervisión densa por objeto choca con eso; uno que trabaje con
  supervisión parcial o por puntos, no.
- **Acción**: registrar el encargo en el objetivo 5 y en la memoria del eje, con esas tres
  restricciones (apuntar a B/C/D, no a A; positivos parciales; workaround E) para que la
  sesión que lo ejecute no las re-derive.

## C3 — La skill contradice el workaround H

- `.claude/skills/knowledge-audit/SKILL.md`, sección Setup: «create a NEW branch
  `chore/audit-coherencia-<sprint>` only if the audit will carry changes into model/training
  code (regla 9) **or a GPU job is running (workaround H)**».
- El workaround H de `CLAUDE.md` manda exactamente lo contrario: **con un job en curso NO se
  cambia de rama**. La cita del workaround está usada como si lo respaldara.
- **Acción**: corregir esa línea, concisa ([[edicion-concisa-agentes-skills]]). Las dos
  pasadas anteriores de esta misma auditoría ya habían hecho lo correcto en la práctica (cero
  checkouts con un job vivo), así que el texto es lo único desalineado.

---

# Cuarta pasada — cierre de la sesión de lectura de los papers (2-ago-2026, noche, 3ª)

> Contexto: se bajaron y leyeron los 5 papers del encargo de mitosis, con dos correcciones a
> `tareas_geometricas/papers_mitosis.md`. La auditoría revisa qué quedó stale **por esas
> correcciones** y qué hallazgo operativo nuevo merece subir a las instrucciones.
> Job 4774 vivo durante toda la pasada: cero branch-switch, cero edición de inputs del job
> (workaround H). Todo lo tocado son docs, memorias y `CLAUDE.md`, que el job no lee.

## Resumen

| id | Hallazgo | Tipo | Sev | Acción |
|---|---|---|---|---|
| D1 | La memoria `papers-rama-mitosis-bcd` dice en su **cuerpo** «código no localizado» (D), «µm/px de MIDOG NO verificado» y «el dato de ZoomMIL no está verificado»; los tres se resolvieron en el ADDENDUM del final | stale | **alta** | Marcar los tres inline apuntando al ADDENDUM, sin borrar el texto original |
| D2 | El workaround E de `CLAUDE.md` se puede leer como que el server **no tiene salida a internet** | error de lectura inducido | media | Sub-cláusula aditiva: la restricción es de **política**, no técnica |
| D3 | «Paths críticos» de `CLAUDE.md` lista 2 repos reference-only; ahora son **6** | stale | media | Agregar los 4 nuevos con la misma regla |
| D4 | Los estudios nuevos fechados **3-ago** cuando la sesión fue la noche del **2-ago** | error | media | **Ya corregido** antes de esta pasada |
| D5 | `papers_mitosis.md` terminaba con dos etiquetas sueltas (`</content>`, `</invoke>`) commiteadas el 2-ago | error | baja | **Ya corregido** en el commit `c9dd72a` |

## D1 — La memoria contradice su propio ADDENDUM

La memoria se escribió el 2-ago con tres cosas marcadas como no verificadas, y esta sesión las
verificó. El ADDENDUM está al final y las corrige, pero **el cuerpo sigue afirmando lo viejo**, y
alguien que escanee la tabla de la línea 20 (`Código: no localizado`) o la línea 44 (`µm/px de
MIDOG: NO verificado`) se lleva el dato equivocado sin llegar al final.

- **Qué dice cada fuente.** Cuerpo de la memoria: no localizado / no verificado. ADDENDUM de la
  misma memoria + `pulearning_estudio.md` + `midog_notas.md` + `zoommil_estudio.md`: resueltos,
  con cita al PDF y al código.
- **Cuál es canónica:** el ADDENDUM y los estudios.
- **Acción:** marcar los tres puntos **inline** con un puntero al ADDENDUM. No se borra el texto
  original, porque registra qué se sabía el 2-ago y por qué la búsqueda falló (se buscó en la
  página de abstract y el link estaba en el cuerpo del paper), que es una lección reusable.

## D2 — El workaround E induce a creer que el server está aislado

`CLAUDE.md:123-130` dice: «No descargar nada de afuera: si falta algo, reportarlo y que Ernesto lo
suba». Es una regla de política, y está bien que exista. Pero el título del workaround es
«`/mnt/project/` no existe en este server» y el texto no aclara si el server **puede** salir.

Esta sesión lo verificó: `curl` a arXiv y `git clone` de GitHub **funcionan** desde la máquina.
Los `WebFetch` de sesiones anteriores salían por el harness, que es otra cosa y no probaba nada
sobre el server.

- **Por qué importa:** una sesión futura podría descartar una opción legítima (bajar algo que
  Ernesto ya autorizó) creyendo que técnicamente no se puede, o al revés, gastar tiempo pidiéndole
  a Ernesto que suba a mano algo que él ya autorizó bajar.
- **Acción:** sub-cláusula aditiva al workaround E. **No se relaja la regla**: el default sigue
  siendo no descargar sin autorización explícita. Solo se separa «no está permitido» de «no se
  puede».

## D3 — El mapa de paths quedó corto

`CLAUDE.md:56-71` lista `CLAM_official_reference/` e `ILSC_reference/` bajo `clam_testing2/`, con
la regla dura de reference-only. Esta sesión agregó cuatro directorios con exactamente el mismo
estatuto: `PUcell_reference/`, `CellViT_reference/`, `ZoomMIL_reference/`, `MSCLAM_reference/`.

- **Acción:** agregarlos al árbol y una línea con la regla compartida, sin repetir el párrafo
  completo para cada uno (canonical + puntero, [[edicion-concisa-agentes-skills]]).

## D4 y D5 — Ya corregidos antes de esta pasada

- **D4:** los cinco documentos nuevos se fecharon **3-ago** cuando el reloj local del server
  marcaba **domingo 2-ago 21:58**. Se corrigieron todas las ocurrencias propias, preservando las
  referencias legítimas a «la reunión del **lunes** 3-ago». La fecha es provenance y otros docs la
  citan, así que no es cosmético.
- **D5:** `papers_mitosis.md` terminaba con `</content>` y `</invoke>`, residuo de la escritura
  del 2-ago que se commiteó. Corregido en `c9dd72a`.

## Verificado sin cambios

- **Skills y agentes:** las 12 skills tienen su `SKILL.md`; `trainer.md` y `reviewer.md` intactos.
  Ninguna de las dos correcciones de esta sesión toca sus reglas.
- **Hallazgos 11 a 14 de `CLAUDE.md`:** ninguno se toca. La lectura de los papers no reabre el eje
  de arquitectura ni contradice nada de lo cerrado; lo que hace es fichar métodos externos.
- **La familia A sigue descartada para los papers.** Ningún paper leído propone cambiar el
  operador de agregación, así que la restricción del encargo se respetó.

---

# Quinta pasada — cierre de la sesión del material de la reunión (3-ago-2026, tarde)

Sesión corta y **documental**: el job 4774 sigue vivo (19 h 44, 27 de 40 runs), así que cero
checkouts y cero ediciones de lo que el job lee (workaround H). Lo auditado es lo que esta sesión
produjo o cambió de estado.

| id | Hallazgo | Tipo | Severidad | Acción |
|---|---|---|---|---|
| E1 | **C1 queda RESUELTO por Ernesto**: la reunión del lunes 3-ago no ocurrió y sigue en pie la del **viernes 07/08/2026** | resolución | **alta** | Cerrar C1 con la resolución fechada; corregir la cabecera de `papers_mitosis.md` |
| E2 | La memoria `papers-rama-mitosis-bcd` dice «para la reunión con Sebastián del **lunes 3-ago**» y apunta a `papers_mitosis.md` como entregable de reunión | stale | media | ADDENDUM fechado, aditivo |
| E3 | La memoria `reunion-24jul-encargos-b8` dice «Reunión confirmada: viernes 07/08/2026» | **correcto, no stale** | baja | Marcar que quedó reconfirmado, para que no se vuelva a dudar |
| E4 | La ETA del grid se explicó como «la estimación del prereg quedó corta»; hay **3 jobs ajenos** compartiendo la GPU | precisión | media | Sub-línea en la regla de cortesía de `CLAUDE.md` |

## E1 — C1 resuelto, y los registros que parecían stale eran los correctos

Ernesto confirmó a las 15:30 del 3-ago que **la reunión del lunes no ocurrió** (se movió o se
canceló) y que **sigue en pie la del viernes 07/08/2026**.

- **Lo que esto invierte:** C1 (cuarta pasada) tenía los tres registros del 07/08 como «stale
  parcial». **No lo estaban**: eran correctos, y la reunión del 3-ago era la excepción. La acción
  que C1 eligió, registrar la nueva **sin borrar** los del 07/08, resultó ser la correcta, y es un
  buen argumento para la regla de edición aditiva.
- **Consecuencia práctica:** el deck de SI-MIL, construido para el 07/08, **apunta a la fecha
  correcta**; no hay lámina de título que corregir en ningún deck.
- **Aplicado:** resolución fechada bajo C1 (arriba en este mismo doc); cabecera de
  `tareas_geometricas/papers_mitosis.md` corregida con tachado y no con borrado, para que quede
  registrado que el documento se escribió apuntando al lunes.

## E2 — La memoria de los papers quedó stale en dos puntos

- `papers-rama-mitosis-bcd`, cuerpo: «ejecutado esa misma noche para la reunión con Sebastián del
  **lunes 3-ago**». La fecha ya no vale.
- La misma memoria da `papers_mitosis.md` como «Entregable». Sigue siendo cierto que es el
  documento del encargo, pero **el que se lleva a la reunión ahora es
  `tareas_geometricas/hojas_reunion.md`** (3-ago), una hoja por paper, condensado de los cinco
  estudios; `papers_mitosis.md` pasa a ser la **fuente larga** (fichas, abstracts verbatim,
  historial de correcciones).
- **Acción**: ADDENDUM 3-ago al final de la memoria. **No se reescribe** el cuerpo ni el ADDENDUM
  del 2-ago: el registro de que el trabajo se hizo contra la fecha del lunes es parte de la
  historia, y ninguna de las conclusiones técnicas cambia.

## E3 — La memoria de la reunión estaba bien, y conviene dejarlo dicho

`reunion-24jul-encargos-b8` (ADDENDUM 31-jul) cierra con «**Reunión confirmada: viernes
07/08/2026**». Con la resolución de E1 eso es **correcto y vigente**. Se agrega una marca de
reconfirmación para que una sesión futura no vuelva a abrir la duda que costó el hallazgo C1.

## E4 — La ETA del grid: contención de GPU, no solo mala estimación

El commit `3f292d1` (y el handoff de las 15:25) atribuyen la desviación de la ETA a que «el prereg
suponía que los brazos chicos serían más rápidos». Es cierto, pero **incompleto**.

- **Medido a las 15:54**: `squeue` muestra **tres jobs ajenos** de `capstone` en el mismo nodo
  (4778 desde hace 6 h 37, 4780 hace 4 h 53, 4782 hace 7 min), más el nuestro. La GPU está
  repartida entre **cuatro** trabajos.
- La ventana en que los runs pasaron de ~37 a ~70 min **coincide** con la aparición de los ajenos.
  No se afirma causalidad exacta (no hay traza por-job de utilización de GPU, y `sacct` está
  deshabilitado, workaround C), pero es una explicación al menos tan fuerte como la de la
  estimación, y **hay que decirla al escribir `resultados.md`** en vez de dejar registrado que
  pre-registramos mal.
- **Lo que NO cambia**: el job no tiene errores y los resultados no se invalidan. La contención
  afecta el **tiempo de pared**, no la métrica.
- **Acción**: sub-línea en la regla de cortesía de `CLAUDE.md`, que hoy solo dice cómo no
  monopolizar la GPU y no dice nada del caso inverso, que es el que nos tocó.

## Verificado sin cambios

- **CLAUDE.md, Hallazgos 11 a 14**: ninguno se toca. Esta sesión no produjo resultados
  experimentales.
- **El pre-registro del grid está intacto.** No se leyó ninguna métrica parcial ni se escribió
  nada que condicione la lectura del prereg §6.
- **`results/b8_grid_es/` sigue deliberadamente sin versionar**, con 27 de 40 runs. Se commitea
  cuando cierren los 8 brazos.
- **Skills y agentes**: sin cambios; la sesión fue documental y no tocó modelo ni training.

---

# Sexta pasada — cierre de la sesión de exposición (3-ago-2026, tarde, 2ª)

Sesión **documental**: el job 4774 sigue vivo (21 h 07, 28 de 40 runs, cero errores), así que
cero checkouts y cero ediciones de lo que el job lee (workaround H). La sesión expuso el material
de la reunión, respondió una pregunta de Ernesto sobre la medición del 1-ago y produjo un
documento nuevo.

| id | Hallazgo | Tipo | Severidad | Acción |
|---|---|---|---|---|
| F1 | **El resultado del 1-ago no existe en ningún entregable presentable.** Ernesto, que lo encargó, no retuvo cómo se verificó: preguntó si «habíamos hecho algo de los mapas de calor» | gap | **alta** | Encargo del deck + memoria de feedback |
| F2 | La decisión del 31-jul («el deck del B8 se rehace con esta línea **en vez de** presentar el de SI-MIL») queda **precisada**: SI-MIL sobrevive, compactado a la mitad | precisión | media | ADDENDUM fechado, aditivo; no se borra la decisión original |
| F3 | Tercer documento sobre los mismos cuatro papers (`papers_explicados.md`) | redundancia potencial, **descartada** | baja | Verificado complementario; queda la tabla de «cuál es cuál» en su §0 |
| F4 | Las dos figuras de atención muestran el tejido **dos veces** (dos regiones de escaneo del `.bif`) | trampa de lectura | media | Instrucción explícita: van al deck **con leyenda**, si no se leen como defecto |

## F1 — El hallazgo más importante del B8 no tiene forma presentable

**Lo que pasó.** Ernesto preguntó qué pruebas habíamos revisado de mitosis antes de buscar
papers, y dijo textualmente que en su memoria no recordaba cómo verificamos que CLAM estuviera
prestando atención correctamente, que *«creo que hicimos algo de los mapas de calor»*.

**Lo que el repo tiene, y está bien.** `sprints/B8_sprint8/atencion_vs_patologo/resultados.md` es
completo, correcto y verificado: AUC de ranking 0.890 ± 0.039, el nulo por traslación rígida, el
descarte del efecto de región, el control de memorización, y la disociación *mira bien y responde
mal*. Nada de eso hay que rehacerlo ni re-verificarlo.

**El problema no es de conocimiento, es de forma.** El resultado vive solo en documentos técnicos
(`prereg.md`, `resultados.md`, dos memorias, dos PNG sueltos). No hay ninguna lámina, ninguna
tabla presentable, ningún guion. Y es, por lejos, el hallazgo con más contenido del sprint: es el
que **reordenó las cuatro familias** y el que decidió que la búsqueda bibliográfica apuntara a B,
C y D y no a la A.

**Corolario incómodo y útil:** si el que lo encargó no lo retuvo, Sebastián y Benjamín no lo van a
retener leyendo un `resultados.md`. La medición cambia lo que el sprint hace a continuación, así
que tiene que poder explicarse en voz alta.

**Acción.** Encargo del deck (F2) y memoria de feedback nueva, `hallazgo-necesita-forma-presentable`.

## F2 — La decisión del 31-jul se precisa, no se contradice

**Lo que dice el registro vigente.** La memoria `tareas-geometricas-mitosis-grado-nuclear`:
*«Decidido con Ernesto el 31-jul: el deck del B8 se rehace con esta línea en vez de presentar el
de SI-MIL»*. Leída sola, esa frase autoriza a borrar SI-MIL del deck.

**Lo que Ernesto pidió hoy.** Compactar las láminas de SI-MIL **a la mitad**, no eliminarlas,
*«que fue una de las tareas de investigación»*, y agregar la sección de mitosis.

**No es contradicción, es refinamiento**, y hay que registrarlo para que la próxima sesión no
borre SI-MIL creyendo que cumple la decisión del 31-jul. El deck pasa de ser monográfico de SI-MIL
a tener dos ejes, con el peso invertido respecto de hoy: SI-MIL como tarea de investigación
cerrada y resumida, mitosis como la línea viva.

**Estado real del deck, verificado.** `sprints/B8_sprint8/presentacion_b8/CLAM_Sprint8_SIMIL.pptx`,
**14 láminas** (2 heredadas del template + 12 de contenido), generado por `generate_b8_deck.py`
(81 KB), ya recortado una vez el 31-jul de 19 a 14. Su README se titula «Presentación B8 —
SI-MIL», que a partir de este encargo queda **stale** y hay que reescribir junto con el deck.

**Acción.** ADDENDUM fechado en la memoria; el detalle operativo va al handoff.

## F3 — El tercer documento es complementario, verificado

Los tres cubren los mismos cuatro papers y respondían a la sospecha de redundancia. Verificado
que no la hay, porque responden preguntas distintas:

| Archivo | Pregunta | Uso |
|---|---|---|
| `papers_mitosis.md` (36 KB) | ¿qué encontramos y con qué evidencia? | referencia, no se lee de corrido |
| `hojas_reunion.md` (25 KB) | ¿qué digo el viernes? | exposición en la reunión |
| `papers_explicados.md` (nuevo) | ¿cómo funciona por dentro? | entender el mecanismo |

El nuevo **no agrega ninguna afirmación**: todos sus números salen de los cinco estudios ya
verificados contra los PDF el 2-ago, y sus ejemplos numéricos están rotulados como ilustrativos.
La tabla de arriba vive en su §0, así que la pregunta «cuál es cuál» queda contestada dentro del
propio documento. **Canonical sigue siendo `papers_mitosis.md`** si alguna vez divergen, y eso
está dicho ahí.

**Sin cambios** en `hojas_reunion.md`: está terminado y verificado, y el handoff anterior pedía
explícitamente no reescribirlo de oficio.

## F4 — Las figuras de atención tienen una trampa de lectura

`figura_atencion_vs_anotaciones.png` y `figura_mitosis_sobre_atencion.png` muestran **el tejido dos
veces**, porque el lienzo de openslide contiene las **dos regiones de escaneo** del Ventana `.bif`
(`region[1].y = 49920`) y el pipeline extrajo parches de las dos: 2303 arriba, 2496 abajo. Las 163
anotaciones caen **todas** en la de abajo.

Ya está anotado como nota de lectura al pie de `atencion_vs_patologo/resultados.md`, pero en una
lámina proyectada, sin esa nota, se lee como un error de la figura. **Si van al deck, van con
leyenda**, y conviene que la leyenda diga además que se midió y se descartó que la región
explicara el efecto (AUC región anotada contra la otra = 0.462-0.478, o sea que recibe *algo
menos* de atención).

## Verificado sin cambios

- **CLAUDE.md, Hallazgos 11 a 14**: ninguno se toca. La sesión no produjo resultados
  experimentales.
- **El pre-registro del grid sigue intacto.** No se leyó ninguna métrica parcial del 4774 en esta
  sesión: solo se contaron archivos (`test_metrics.json`) y se miró `squeue`.
- **`results/b8_grid_es/` sigue deliberadamente sin versionar**, ahora con 28 de 40 runs.
- **`atencion_vs_patologo/`**: nada que re-medir. Los AUC, los p del nulo espacial y la corrida
  confinada están cerrados desde el 2-ago.
- **Skills y agentes**: sin cambios; la sesión fue documental y no tocó modelo ni training.

---

# Séptima pasada — cierre de la sesión del deck a dos ejes (3-ago-2026, tarde, 3ª)

> Job 4774 vivo durante toda la pasada (22 h 14 min, 29 de 40 runs): cero branch-switch,
> cero edición de inputs del job. Todo lo tocado es documental.

| id | Hallazgo | Tipo | Severidad | Acción |
|---|---|---|---|---|
| G1 | **F1 y F4 de la sexta pasada quedan RESUELTOS.** El resultado del 1-ago ya tiene forma presentable (8 láminas + guion) y las figuras llevan su leyenda obligatoria | cierre | alta | Marcar resueltos acá y en las memorias |
| G2 | CLAUDE.md dice que la **única** excepción a «todo nativo» son las figuras externas de un paper, y el deck lleva 3 imágenes que son **producción nuestra** | reconciliación | media | Sub-cláusula aditiva; no se reescribe la regla |
| G3 | La memoria de puntos ciegos del QA **no cubre las dos clases de defecto** que aparecieron en esta pasada, ambas con la auditoría en cero | gap | media | ADDENDUM fechado |
| G4 | Dos procesos con el mismo id de sesión escribiendo el mismo archivo | gotcha nuevo | media | Memoria nueva + línea en el índice |
| G5 | Dos líneas de `MEMORY.md` quedaron stale: el encargo del deck ya se ejecutó, y el hallazgo del 1-ago ya tiene forma | stale | baja | Reescribir las dos líneas |

## G1 — El hallazgo del 1-ago ya tiene forma presentable

**Qué decía la sexta pasada.** F1: *«el resultado más importante del B8 no existe en ningún
entregable presentable»*, con severidad **alta**, y F4: *«las dos figuras muestran el tejido
dos veces … si van al deck, van con leyenda»*.

**Qué hay ahora.** `presentacion_b8/CLAM_Sprint8.pptx`, 17 láminas, de las cuales **ocho** son
la medición: la pregunta con sus dos hipótesis pre-registradas, qué se mide exactamente, los
dos mapas, la escalera de los siete grupos, los 28 parches sobre el mapa, la disociación, los
cuatro controles, y qué mueve en las cuatro familias. Con guion hablado en las ocho.

**F4 cumplido al pie.** La lámina de los mapas lleva el panel que explica las dos regiones de
escaneo (2303 arriba, 2496 abajo, las 163 marcas todas abajo) **y** el dato de que se midió y
se descartó el efecto de región (0,462 a 0,478). Sin eso la figura se lee como un defecto.

**F2 no requiere acción**: era una precisión de registro y ya estaba aplicada como ADDENDUM.

## G2 — «Todo nativo salvo figuras de paper» necesita una segunda excepción

**Lo que dice CLAUDE.md** (línea 1119): *«Única excepción: **figuras externas de un paper**
(van como imagen)»*.

**Lo que hace el deck.** Lleva tres imágenes que **no** son de un paper:
`atencion_dos_regiones.png`, `mitosis_region_anotada.png` y `mitosis_zoom.png`. Son mapas de
atención sobre una lámina real, producidos por nosotros.

**No es una violación de la regla, es un caso que la regla no contempló.** El espíritu de
«todo nativo» es que Ernesto pueda agrandar y editar tablas, gráficos y diagramas, y que nada
que se pueda dibujar con shapes viaje como raster. Un mapa de atención sobre tejido **no se
puede dibujar con shapes**: es una fotografía de un resultado. Lo que sí se mantuvo nativo es
todo lo que lo acompaña, incluida la escalera de los siete AUC, que es un gráfico de barras
dibujado con la gramática del template y no un PNG de matplotlib.

**Fix**: sub-cláusula aditiva en la misma línea, sin reescribir la regla.

## G3 — Dos clases de defecto que el chequeo programático tampoco ve

La auditoría dio **cero avisos** en las dos pasadas de generación, y aun así mirando las
láminas rasterizadas aparecieron cuatro defectos. Dos son de una clase que la memoria
[[deck-qa-puntos-ciegos-chequeo]] todavía no registraba:

- **Imagen centrada en una caja con otra relación de aspecto.** `add_image_fit` centra la
  figura dentro de su caja; si la caja no tiene el aspecto de la figura, sobra aire a los
  costados y **los rótulos de columna quedan corridos respecto de lo que rotulan**. El
  chequeo no lo ve porque nada se sale de su caja: la caja está bien, la imagen está bien, y
  la relación entre las dos es la que falla. Se corrige fijando `h = w / ar`.
- **Tira de paneles auto-dimensionados, dentada.** `panel(..., h=None)` calcula su alto
  midiendo el texto, que es justamente el fix del ADDENDUM del 30-jul; el efecto lateral es
  que una tira de cuatro sale con cuatro alturas distintas. Se igualan **después** de
  dibujarlos con `sp.height = Inches(alto_max)`, que es seguro porque el texto está anclado
  arriba.

Las otras dos fueron un pie de figura lejos de su figura y jerga interna en un remate
(«commiteadas»), que son de la clase que ya estaba registrada: solo salen mirando.

## G4 — Dos procesos con el mismo id de sesión

Al interrumpir la sesión y retomarla, el proceso anterior **no murió** y siguió editando el
generador por su cuenta: 151 líneas a las 17:49, con el mismo plan ya aprobado. Se detectó
por un `Edit` que falló con «modified since read».

El síntoma es idéntico al de una sesión ajena pisando el árbol compartido, y la reacción
correcta es la misma (parar y mirar el diff antes de escribir), pero el diagnóstico cambia
qué se hace con lo encontrado: trabajo ajeno se preserva, trabajo propio huérfano se
aprovecha o se descarta. Se distinguen por el `--resume` de cada proceso. Ernesto autorizó
cerrar el viejo y la construcción siguió sobre lo que había dejado.

**Fix**: memoria nueva [[proceso-viejo-vivo-tras-interrumpir]] + línea en el índice.

## G5 — Dos líneas del índice de memoria quedaron stale

- La de `deck-b8-dos-ejes-simil-mitosis` empieza con «encargo 3-ago», y el encargo ya está
  ejecutado.
- La de `hallazgo-necesita-forma-presentable` termina con «el del 1-ago no lo tenía», que
  después de esta sesión es falso.

## Verificado sin cambios

- **CLAUDE.md, Hallazgos 11 a 14**: ninguno se toca. La sesión no produjo resultados
  experimentales.
- **El pre-registro del grid sigue intacto.** No se leyó ninguna métrica parcial del 4774:
  solo se contaron archivos (`test_metrics.json`, 29 de 40) y se miró `squeue`.
- **`results/b8_grid_es/` sigue deliberadamente sin versionar.**
- **`atencion_vs_patologo/`**: nada que re-medir. Los siete AUC de la escalera del deck se
  verificaron contra `auc_por_checkpoint.csv` y reproducen el `resultados.md` dígito a dígito.
- **Skills y agentes**: sin cambios; la sesión no tocó modelo ni training.

---

# Octava pasada — cierre de la sesión del grid E×S (4-ago-2026, martes)

> Job 4774 **cerrado** al abrir la pasada (4-ago 07:04, 40/40 runs, cero `Traceback`). Sin jobs
> propios en cola; los dos de `capstone` son ajenos y no leen este árbol. Todo lo tocado es
> documental más el `git add` de la verdad de campo, que el handoff bloqueaba hasta el cierre
> de los 8 brazos.

| id | Hallazgo | Tipo | Severidad | Acción |
|---|---|---|---|---|
| H1 | **«El margen de recorte está en S y no en E» está propagado en 5 lugares y el grid NO lo sostuvo.** La medición que lo originó sigue siendo correcta; lo que cae es la inferencia de capacidad que se le colgó encima | contradicción | **alta** | Precisar en los 5, aditivo, sin borrar la medición |
| H2 | CLAUDE.md declara el eje E×S como **«Eje de trabajo abierto»** al cierre del Hallazgo 12; el eje cerró en H_nula | stale | alta | ADDENDUM fechado en el Hallazgo 12 |
| H3 | **El pipeline es determinista bit a bit**, hecho nuevo y transversal que refuerza el patrón P1 y a la vez acota qué cuenta como réplica independiente | hallazgo nuevo | alta | Sub-cláusula aditiva en P1 + memoria nueva |
| H4 | `progress/current.md` no tiene la sesión del 4-ago | stale | media | Sección nueva |
| H5 | La línea de `MEMORY.md` del grid decía «PRE-REGISTRADO Y LANZADO» | stale | baja | Ya reescrita en esta sesión |

## H1 — La frase propagada que el grid puso a prueba, y que no aguantó

**Dónde vive**, verificado con `grep -n`:

| Fuente | Línea | Qué dice |
|---|---|---|
| `CLAUDE.md` | 857 | «el margen de recorte de capacidad está en **S**, no en E» (ADDENDUM 24-jul, n=7) |
| `CLAUDE.md` | 881 | «**el margen de capacidad está en S**, confirmado con n grande» (ADDENDUM 27-jul, n=1858) |
| memoria `mammoth-slot-routing-weight` | description, 57, 69, 178 | idem, cuatro veces |
| `MEMORY.md` | 68 | «⇒ margen en S» |

**Qué pasó.** El grid E×S (job 4774) existía justamente para poner a prueba esa frase, y el
contraste primario `(recorta S) − (recorta E)` a igual E·S dio **+0.022 / −0.014 / −0.002** de
AUC en los peldaños 270 / 210 / 150: **el signo de la media se invierte entre peldaños**, la
desviación supera a la media en los tres, y el único peldaño a favor tiene 3 de 5 folds.

**Qué se corrige y qué NO.** Hay que separar dos afirmaciones que venían pegadas:

- **La medición se mantiene intacta**: slots efectivos 159.5 ± 26.3 de 300 y expertos 29.98 de
  30 con `e50=15` / `e90=27` exactos sobre 1858 láminas-fold. Nadie la contradijo, y **no se
  toca**.
- **La inferencia de capacidad NO se sostiene**: de «poco más de la mitad de los slots concentra
  el peso» no se sigue «entonces conviene recortar S y no E». El 30×5 tiene 150 slots totales,
  prácticamente el N_eff medido, y no marca ningún quiebre.

Lectura durable, que es lo que va a los cinco lugares: **la ocupación describe cómo se reparte
el peso, no dimensiona la capacidad necesaria.** Es exactamente la lectura que el pre-registro
le había asignado por anticipado a H_nula (`grid_expertos_slots/prereg.md` §3), así que la
interpretación no se eligió después de ver el número.

**Criterio aplicado**: edición aditiva, la medición se preserva palabra por palabra y se le
agrega el límite. Nada se borra: el ADDENDUM del 27-jul es registro histórico de qué se sabía
y cuándo.

## H2 — El eje E×S ya no está abierto

`CLAUDE.md:916-918`, al cerrar el Hallazgo 12, dice **«Eje de trabajo abierto (NO reabre
rendimiento): afinar E y S para mama reduciendo uno con el otro fijo a igual total (27×10 vs
30×9), regla 9 + reviewer + paired sobre los splits del 4589»**. Ese eje se ejecutó y cerró.

Va como ADDENDUM fechado del Hallazgo 12, **sin tocar** el texto del eje abierto: el Hallazgo 12
es «Mammoth no es palanca» y el grid **no lo movió**, porque midió capacidad y no rendimiento
y no calculó ningún Δ contra CLAM por brazo. El ADDENDUM cierra el eje y deja el Hallazgo donde
estaba.

## H3 — Determinismo bit a bit: refuerza P1 y acota qué es una réplica

El control 30×10 del grid re-corrió el mismo Mammoth del job 4589 y salió **`md5` idéntico en
los 5 folds**, incluido el `s_<f>_checkpoint.pt` de 2.5 MB. Verificado que los runs fueron
reales (mtime del 2-ago, 260 épocas loggeadas, 40 `[DONE]`), no un reuso encubierto.

Toca el patrón **P1** (`CLAUDE.md:465`) en dos direcciones opuestas, y por eso conviene que
esté escrito ahí y no solo en la memoria:

- **A favor**: el reuso pareado de un baseline con la misma semilla, splits y features es válido
  **por construcción**, no «referencia informativa». El prereg del grid solo se animaba a pedir
  que el control cayera «dentro de lo que se mueve una corrida», asumiendo no-determinismo de
  GPU; no hay tal cosa acá.
- **En contra de un mal uso**: re-correr la misma config con la misma semilla **no aporta
  evidencia nueva**. Aplica directo al pendiente de replicar el Δ +0.074 del 4589, que el
  control **no** replicó y no podía replicar.

Memoria nueva `pipeline-determinista-bit-a-bit` + línea en el índice. Alcance acotado a esta
GPU y este stack: el determinismo cross-hardware no se midió y no se afirma.

## H4 — `progress/current.md`

Sección nueva `## Sesión del 4-ago-2026 (martes)`, con el cierre del job, el veredicto, el
hallazgo del determinismo y el estado de los pendientes.

## Verificado sin cambios

- **El pre-registro no se tocó**, en ninguna de sus secciones. El resultado se escribió contra
  las hipótesis tal como estaban (regla 9).
- **El Hallazgo 12 no se movió**: el grid midió capacidad. Cero Δ contra CLAM por brazo, que
  era el riesgo que el prereg §6 identificó y evitó por diseño.
- **La política de eval B5** se cumple en el `resultados.md`: balanced accuracy y AUC juntos,
  matrices de confusión y n por clase en los 8 brazos.
- **Los cuatro frentes**: agentes y skills sin cambios, no los tocó esta sesión.

# Novena pasada — cierre de la sesión del grid al deck (4-ago-2026, martes, 2ª)

> Sin jobs propios en toda la pasada. Ajenos: los dos de `capstone` y uno nuevo, `4791
> oncomets` de `dbustama`, que arrancó durante la sesión. Ninguno lee este árbol. Todo lo
> tocado es el generador del deck, su README y documentación.

| id | Hallazgo | Tipo | Severidad | Acción |
|---|---|---|---|---|
| I1 | La memoria del deck y su línea de índice dicen **«17 láminas»** y describen el deck como de dos ejes; ahora tiene **20** con una sección de cierre | stale | alta | ADDENDUM fechado, sin tocar el registro del 3-ago |
| I2 | La memoria de puntos ciegos del QA **no cubre la clase de defecto** de esta pasada: dos objetos válidos superpuestos | gap | alta | ADDENDUM fechado con la clase y su regla |
| I3 | La memoria del grid lista los pendientes del cierre pero no registra que el resultado **ya tiene forma presentable** | stale | baja | Una línea |
| I4 | `progress/current.md` no tiene la sesión del 4-ago por la tarde | stale | media | Sección nueva |
| I5 | La memoria de «un hallazgo necesita forma presentable» está escrita sobre un resultado **positivo**; el del grid es **nulo** y también la necesitó | ampliación | baja | Una línea |

## I1 — El deck dejó de tener 17 láminas, y la decisión de encuadre es lo que hay que preservar

**Dónde vive**, verificado con `grep -n`:

| Fuente | Qué dice |
|---|---|
| memoria `deck-b8-dos-ejes-simil-mitosis`, ADDENDUM 3-ago | «`CLAM_Sprint8.pptx`, **17 láminas**: 2 heredadas + 1 de mapa + 6 de SI-MIL + 8 de atención» |
| `MEMORY.md` L86 | «EJECUTADO 3-ago: CLAM_Sprint8.pptx, 17 láminas» |
| `presentacion_b8/README.md` | ya actualizado en esta sesión, con la estructura de 20 |

**Criterio aplicado.** El ADDENDUM del 3-ago **no se reescribe**: es el registro de qué se
ejecutó ese día y su cuenta de láminas era correcta entonces. Va un ADDENDUM nuevo fechado.

**Lo que hay que preservar, que no es la cuenta sino la decisión.** El handoff planteaba tres
encuadres posibles y Ernesto eligió **(b), sección de cierre**. Lo que importa registrar es el
**motivo**, porque es lo que evita que una sesión futura lo re-decida: el hallazgo que cambia
el plan es el de atención y no el grid, el deck ya venía largo, y meterlo como tercer eje
obligaba a rehacer la lámina del mapa del recorrido (cuya tira de dos tarjetas está
**calculada**, `bw = (9.28 - 0.34) / 2`) y a reescribir su guion, que es la parte cara.

## I2 — La clase de defecto que faltaba: dos objetos válidos superpuestos

Con `auditar(prs)` en **cero**, el QA visual encontró **tres** defectos en las tres láminas
nuevas. Dos de ellos son de una clase que los ADDENDUM anteriores de esa memoria no cubren.

Los puntos ciegos ya registrados son: colores de fuente, texto dentro de un PNG, texto que
desborda su caja (resuelto midiendo con los TTF), imagen centrada en una caja con otro aspecto,
y tira de paneles dentada. Los de hoy no son ninguno de esos: **cada objeto está bien por
separado y dentro del lienzo**, y lo que falla es que dos se pisan.

| Defecto | Los dos objetos | Por qué ninguna consulta lo ve |
|---|---|---|
| La línea de tendencia cruzaba los rótulos de valor | un conector y un textbox | el rótulo entra perfecto en su caja; el conector está en su sitio; no hay desborde de nada |
| Los paneles chocaban con la regla de `takeaway_bar` | un panel `h=None` y un rectángulo de posición fija | el panel se auto-dimensiona y queda dentro del lienzo, y la regla está donde se la puso |

**La regla que generaliza**, y es la que va a la memoria: el auto-dimensionado (`h=None`)
resolvió el desborde pero **creó** una clase nueva, porque un alto que se calcula al vuelo
puede invadir cualquier cosa posicionada con una constante. Cuando un bloque auto-dimensionado
va seguido de un elemento fijo, el fijo tiene que posicionarse **desde el alto medido**, igual
que ya se hace con las tiras de paneles.

## I3 — El grid ya tiene forma presentable

La memoria del grid cierra con la lista de pendientes post-cierre. Se agrega que las tres
láminas existen, dónde, y que el pendiente que sigue vivo es la réplica con semillas nuevas.

## I4 — `progress/current.md`

Sección nueva `## Sesión del 4-ago-2026 (martes, tarde)`, con la decisión de encuadre, las tres
láminas, los tres defectos del QA visual y el estado de los pendientes.

## I5 — Un resultado NULO también necesita forma presentable

`hallazgo-necesita-forma-presentable` nació de un resultado **positivo** que cambiaba el plan y
no existía en ninguna lámina. El del grid es el caso simétrico: un **H_nula** que además
responde un encargo explícito, y que sin lámina llega a la reunión como «no dio nada». Se
agrega la línea, porque el reflejo natural con un resultado nulo es justamente no presentarlo.

## Verificado sin cambios

- **`CLAUDE.md`**: el ADDENDUM del 4-ago del Hallazgo 12 y el patrón **P1.a** siguen correctos
  y completos. Armar láminas no cambia ninguna regla; nada que agregar.
- **El pre-registro y el `resultados.md` del grid**: intactos, como pedía el handoff. Las tres
  láminas se hicieron **a partir** de ellos.
- **Cero Δ contra CLAM por brazo** en el deck, que era la regla de diseño del prereg §6. CLAM
  no aparece en ninguna de las tres láminas, ni siquiera como fila de escala.
- **Agentes y skills**: sin cambios, esta sesión no los tocó.

---

# Décima pasada — cierre de la sesión de revisión del deck completo (4-ago-2026, martes, 3ª)

> Sin jobs propios en toda la pasada. Ajenos: `4778` y `4780` de `capstone`; el `4791` de
> `dbustama` ya no está en cola. Ninguno lee este árbol. Lo único tocado es el generador del
> deck y documentación.

Primera sesión que mira **las 20 láminas de una sentada** y lee el guion **de corrido**, que es
lo que el handoff pedía. Seis defectos, y el dato que los ordena a todos está en el hallazgo J2.

| id | Hallazgo | Tipo | Severidad | Acción |
|---|---|---|---|---|
| J1 | Una convención nueva (`_num`, coma decimal) se aplicó solo a las figuras nuevas; la función vieja `barras_ranking` siguió con `"%.3f"` y dejó la lámina 13 con punto decimal al lado de su propio `0,890` | error | alta | Fix en el generador + ADDENDUM a la memoria de puntos ciegos |
| J2 | **Los seis defectos estaban en láminas previas al grid. Las tres nuevas salieron limpias.** El riesgo de ampliar un deck no está en lo que se agrega | ampliación | alta | ADDENDUM con la lección + línea en el README |
| J3 | El arco se rompió en el **empalme** entre tandas, y solo se ve leyendo de corrido: la 17 prometía continuidad hacia algo que la tanda nueva desplazó | gap | media | Fix en el generador + registro de la clase |
| J4 | El markup de subíndice `_x` aplicado a un subíndice de **dos** caracteres es silencioso: `L_CE` produce «L꜀E» y no falla | error | media | Fix + una línea en el README §6 |
| J5 | El README de la presentación no tiene la tabla de esta pasada ni registra que el deck se revisó entero | stale | media | Sección nueva |
| J6 | `progress/current.md` no tiene la sesión del 4-ago por la noche | stale | media | Sección nueva |

## J1 — La convención nueva no alcanzó a la función vieja

`_num()` nació el 4-ago con la sección del grid y formatea con coma decimal y menos
tipográfico. Se aplicó a `barras_divergentes()` y `escalera_capacidad()`, las dos figuras
nuevas. Pero `barras_ranking()`, escrita el 3-ago para la lámina 13, siguió con
`"%.3f" % auc`, así que los siete valores de la escalera salían **`0.890`, `0.828`…** en una
lámina que en el mismo alto dice `azar = 0,5` y `Mitosis: 0,890 ± 0,039`.

**Por qué ningún chequeo lo ve.** No es layout: el texto entra en su caja, nada se sale del
lienzo, nada se pisa. Es una **inconsistencia entre una parte vieja y una convención nueva**,
y la única consulta que la caza es una que nadie había escrito: buscar `\d+\.\d+` en todo el
texto del deck. Se corrió y dio exactamente los siete de la lámina 13 y ninguno más.

**La regla que generaliza:** cuando una sesión introduce una convención de formato, el barrido
tiene que ser sobre el deck entero, no sobre lo que esa sesión escribió. El chequeo es de una
línea y ahora existe.

## J2 — Los seis defectos estaban en lo viejo, no en lo nuevo

Es el hallazgo de la pasada y conviene que quede escrito con el reparto a la vista:

| Láminas | Cuándo se escribieron | Defectos encontrados |
|---|---|---|
| 4 a 9 (SI-MIL) | 30-jul, recortadas el 3-ago | 2 (láminas 8 y 9) |
| 10 a 17 (atención) | 3-ago | 4 (láminas 12, 13, 15, 17) |
| **18 a 20 (grid)** | **4-ago, ya miradas** | **0** |

Las tres del grid se habían mirado en su propia sesión y sus tres defectos se corrigieron
entonces. Lo que nadie había hecho es volver sobre las diecisiete anteriores **después** de que
el deck creciera, ni leer el guion entero de una sentada.

**La lección, que es la que va a la memoria:** al ampliar un deck, el QA de las láminas nuevas
es el barato y el que se hace solo. El que paga es releer lo que ya estaba, porque lo viejo
acumula la deriva de las convenciones que llegaron después (J1), las promesas de continuidad
que la ampliación invalidó (J3) y los choques de números entre láminas que antes no eran
vecinas. Ninguno de los tres es visible mirando la lámina sola.

## J3 — El arco se rompe en el empalme, y solo se ve de corrido

La lámina 17 cerraba el eje de atención con dos frases que prometían continuidad hacia los
papers: en el panel, «Es la parte que sigue en la agenda de hoy»; en el guion, «Esa es la parte
que sigue». Lo que sigue, desde el 4-ago, es la sección del grid. Y encima las dos láminas del
empalme abrían con la misma construcción: «Cierro con lo que esto cambia» en la 17 y «Cierro
con un encargo» en la 18.

Ninguna de las dos cosas es visible mirando una lámina. La primera exige saber qué viene
después; la segunda, haber leído las dos seguidas.

**Fix aplicado**, mínimo y sin tocar la decisión de encuadre: la 17 ahora remata con «Los
traigo aparte, en las hojas que preparé para hoy» (panel y guion) y abre con «Termino esta
parte con lo que cambia». Con eso el «Cierro con un encargo» de la 18 aterriza limpio y es el
único cierre del deck. **La lámina 3 no se tocó** y el deck sigue siendo de dos ejes con una
sección de cierre.

**La regla:** cuando una tanda nueva se agrega al final, hay que releer el remate de la lámina
que antes era la última. Una promesa de continuidad envejece en el momento en que algo se pone
detrás.

## J4 — El subíndice multi-carácter sin paréntesis es silencioso

`_add_runs()` documenta las dos formas, `_x` para un carácter y `_(xx)` para varios. La
ecuación 10 estaba escrita `L_CE(...) + λ L_KD(...)`, así que el parser bajó **solo la C y la
K** y dejó la E y la D a tamaño completo: en pantalla se leía «L꜀E» y «LₖD».

No falla, no avisa y la auditoría no lo ve, porque el resultado es texto válido dentro de su
caja. El README §6 tenía anotado el gotcha del `_` **literal** (el `model\_clam.py`), que es el
caso inverso; faltaba éste. Corregido a `L_(CE)` / `L_(KD)`, verificado sobre los runs del XML.

## J5 y J6 — README de la presentación y `progress/current.md`

El README gana una sección con la tabla de los seis defectos de esta pasada y el reparto de J2.
`progress/current.md` gana la sesión del 4-ago por la noche.

## Verificado sin cambios

- **`CLAUDE.md`**: nada que tocar. Revisar láminas no cambia ninguna regla, y las convenciones
  de deck que la pasada usó (todo nativo, Barlow, cero rayas, notas como guion hablado) se
  cumplieron sin excepción.
- **Los dos `prereg.md` y los dos `resultados.md`** (grid y atención): intactos, como pedía el
  handoff. Los seis fixes son de generador y de guion; **ningún número cambió**. Los valores de
  la lámina 13 se re-verificaron contra `auc_por_checkpoint.csv` al cambiarles el formato.
- **Cero Δ contra CLAM por brazo**: sigue sin aparecer en las tres láminas del grid.
- **El veredicto H_nula del grid**: la sección se releyó entera y lo sigue contando como tal.
- **Agentes y skills**: sin cambios.

## Lo que queda abierto y va al handoff

Dos decisiones de Ernesto, ninguna bloqueante:

- **La lámina 12**: el cuadrante inferior derecho queda vacío, cerca del 30 % de la lámina, y
  las filas de la grilla 2×2 no tienen rótulo (las columnas sí). Es la lámina de la leyenda
  obligatoria, así que es la que más conviene que se lea sola.
- **La lámina 20**: sigue abriendo en voz alta el pendiente de la réplica. Viene así desde el
  4-ago por la tarde, a propósito, y todavía sin respuesta.

---

# Undécima pasada — QA visual de las nueve láminas del rediseño (4-ago-2026, martes, 4ª)

> Sin jobs propios: esta sesión no lanzó ninguno. El `4809` (`test_vis`) corre bajo la cuenta
> compartida `sdonoso` desde `Test_D/D_abs/`, fuera de este árbol y de `clam_environ`, así que
> el workaround H no restringe el cierre. Ajenos: `4780` de `capstone`, `4800` de `gvenegas`.
> Lo único tocado es el generador del deck y documentación.

La tanda que el handoff de las 20:00 dejó pendiente: mirar rasterizadas las nueve láminas que el
rediseño tocó y nadie miró (9, 10, 11, 13, 14, 15, 17, 18, 19). **Un defecto real de nueve**, y
dos sospechas que se cayeron al verificarlas, que es de donde salen K2 y K3.

| id | Hallazgo | Tipo | Severidad | Acción |
|---|---|---|---|---|
| K1 | La lámina 17 se pisa a sí misma: `barras_divergentes` dibuja sus rótulos de lado en `t − 0,34` y caían sobre el renglón de dataset del bloque de arriba | error | alta | Fix en el generador + ADDENDUM a la memoria de puntos ciegos |
| K2 | Una sospecha de defecto geométrico nacida de un rasterizado a 100 dpi resultó **falsa** al mirarla a 200 y contra el código | falso positivo | media | ADDENDUM: verificar antes de «arreglar» |
| K3 | Medir **tinta por renglón** sobre el PNG separa una colisión real de un solape nominal de cajas, y verifica el fix sin gastar presupuesto de imágenes | método | alta | ADDENDUM con la receta |
| K4 | El «26 vs 28» que la sesión volvió a levantar **ya estaba resuelto** en la décima pasada | stale | baja | Se cierra acá, no viaja al handoff |
| K5 | `progress/current.md` y el README del deck no registran esta pasada | stale | media | Secciones nuevas |

## K1 — Una figura que dibuja por encima de su propio `t`

`barras_divergentes()` pone los dos textos que nombran los lados («gana recortar expertos» /
«gana recortar slots») en `t − 0,34` (`generate_b8_deck.py:744`). Quien la llama razona con el
`t` y el alto que le pasa, así que **cree que la figura empieza en `t`** y apila lo suyo hasta
ahí. En la 17 el bloque de arriba había ganado en el rediseño un renglón de dataset de 9 pt, y
con la figura en `TOP + 0,84` los rótulos aterrizaron encima: se leía «5 particiones» tachado
por «gana recortar expertos».

**Por qué no lo caza ni el chequeo de solapes.** Solape hay, pero el chequeo de esta lámina
reporta **tres** y solo uno es real: las cajas de texto son más altas que su texto (una
`caption` mide 0,4" y su renglón de 9 pt ocupa 0,17"), así que dos cajas se solapan sin que las
tintas se toquen. Un solape de cajas no es evidencia de que haya colisión **ni de que no la
haya**; por eso hizo falta K3.

**El fix y por qué es ese.** La figura baja a `TOP + 1,06` y **cede 0,10" de alto** para
pagarlo, así que la barra de remate y todo lo que va debajo quedan donde estaban (verificado:
las bandas de tinta por debajo de y=618 son idénticas antes y después). Empujar hacia abajo sin
ceder alto habría llevado el remate contra el borde inferior.

**La regla que generaliza:** una figura que dibuja por encima de su propio `t` tiene un alto
efectivo mayor que el declarado, y quien la llama no lo sabe. Es la imagen espejo del bloque
auto-dimensionado que invade un elemento fijo (ADDENDUM del 4-ago): allá el alto crece hacia
abajo y se calcula al vuelo, acá crece hacia arriba y está escondido en una constante del
helper. Mientras el helper no devuelva su extensión real, **el margen superior es responsabilidad
del que llama** y hay que dejarlo a mano.

## K2 — El rasterizado a 100 dpi puede fabricar un defecto

A 100 dpi la polilínea de la lámina 18 parecía arrancar en la **esquina superior derecha** de la
primera barra en vez de su centro, en las dos ramas. A 200 dpi arranca en el centro, y el código
lo confirma sin ambigüedad (`topes.append((cx, base - alto))`, con `cx` el centro de la barra).
Lo que engañaba es que la línea baja apenas sale del vértice, así que sobre la mitad izquierda de
esa barra no hay línea y el vértice se lee corrido.

**La regla:** 100 dpi alcanza para leer una lámina, no para juzgar una geometría de pocos
píxeles. Antes de tocar el generador por un defecto geométrico, subir el dpi **y** leer la
función que lo dibuja. Creerle sale más caro que el defecto, porque se «arregla» algo que estaba
bien.

Es simétrico del falso positivo ya anotado (un solape de cajas que no es colisión) pero por el
otro lado: aquel es un falso positivo del chequeo programático, este es uno de **la mirada**.

## K3 — Medir tinta por renglón

```python
ink = (np.array(Image.open(png).convert("L")) < 200).sum(axis=1)
```

y listar las corridas de filas con tinta. Cada banda es un renglón de texto o un objeto, y los
huecos entre bandas son el aire real. En la 17: **antes** una sola banda de 25 px (y=232..256),
que es el renglón de dataset y los rótulos **fundidos**; **después** dos bandas, de 15 y 16 px,
con 24 px limpios entre medio.

Sirve para tres cosas que mirar no da:

- **Distingue** la colisión real del solape nominal de cajas, que es lo que K1 necesitaba.
- **Verifica un fix cuantitativamente**, y el número queda en el commit.
- **No gasta presupuesto de imágenes** ([[image-api-qa-limit]]), que en una sesión larga es el
  recurso que se acaba primero. Se puede correr sobre las 20 láminas de una.

**No reemplaza mirar**, y no hay que venderlo como que sí: no ve colores, no ve qué dice el
texto, no ve si una flecha apunta al lado equivocado, no ve nada dentro de un PNG. Es el
complemento del orden de siempre, no su sustituto.

## K4 — El «26 vs 28» ya estaba cerrado

La sesión lo volvió a levantar al ver «26 marcas» en la 15 y «28 parches» en la 13 y la 14.
**Ya estaba resuelto**: es el punto ciego nuevo 3 de la décima pasada, y su fix (nombrar la
unidad, «26 marcas de mitosis») está aplicado en la lámina. Los dos números son correctos y
salen del mismo `resultados.md`. Se cierra acá para que no vuelva a viajar en un handoff.

## K5 — README de la presentación y `progress/current.md`

El README gana el resultado de la tanda de QA en su sección «Lo que quedó sin hacer», que la
daba por pendiente. `progress/current.md` gana la sesión.

## Verificado sin cambios

- **Las otras ocho láminas** (9, 10, 11, 13, 14, 15, 18, 19): limpias. Las dos que el handoff
  marcaba como de mayor riesgo por cambio de geometría, la **9** (tabla a `row_h=0,50`, `fs=13`)
  y la **15** (dos paneles menos y remate más abajo), no tienen desborde ni solape.
- **La 14**: el pie «la región anotada» es correcto. El asset es `mitosis_region_anotada.png`,
  ya recortado a esa región, no el lienzo con las dos.
- **Barrido de reglas duras sobre las 20 láminas, cuerpo Y notas**: cero `\d+\.\d+`, cero `—`,
  cero letras A/B/C/D. El de puntos decimales es el que nació en J1 y ahora se corre completo.
- **Los dos `prereg.md` y los dos `resultados.md`**: intactos. **Ningún número cambió**; el
  único fix es de geometría.
- **Cero Δ contra CLAM por brazo** y **veredicto H_nula**: siguen como estaban en las láminas
  del grid.
- **`CLAUDE.md`, agentes y skills**: sin cambios. Mirar láminas no mueve ninguna regla.

## Lo que queda abierto y va al handoff

- **El guion sin pasar por `@humanizer-es`**, que era el segundo pendiente de la tanda.
- **La leyenda mezclada español/inglés** de la figura de la 12 («Immune cells», «Stroma»,
  «Nucleos» sin tilde). Es de `atencion_vs_patologo/`, no del generador: arreglarlo es regenerar
  esa figura. Decisión de Ernesto si vale la pena antes del viernes.
- **Una duda de estilo menor, no bloqueante**: la lámina 11 dice el mismo número con dos
  precisiones, «0,89» junto a la cinta y «0,890» en la banda de abajo. Hay argumento para
  dejarlo, porque las cintas son ilustración (7 bloques marcados de 33, no los 163 de 4799
  reales) y la banda es el valor medido. No se tocó.

---

# Duodécima pasada — la lectura en voz alta del guion (4-ago-2026, martes, 6ª)

> Sin jobs propios. El `4809` (`test_vista`) sigue bajo la cuenta compartida `sdonoso` con
> `WorkDir=/media/administrador/Storage1/sdonoso/Test_D/D_abs`, fuera de este árbol y de
> `clam_environ`: el workaround H no restringe nada. Ajenos: `4780` de `capstone`, `4800` de
> `gvenegas`. Lo único tocado es el generador del deck y documentación.
>
> La 5ª sesión del martes (el guion por `@humanizer-es`, 22:30) se documentó en el README del
> deck y en `progress/`, sin dejar pasada acá; de ahí que esta sea la duodécima y no la
> decimotercera.

La mitad que quedaba de la tanda anterior: **leer las 19 láminas con notas en voz alta, de
corrido**. Salieron **20 hallazgos**, se aplicaron **13** (los que son defecto o no entran en un
respiro) y **7 quedaron para Ernesto** por ser decisiones de vocabulario. El guion pasó de 6089 a
6114 palabras de prosa, +25 netas.

| id | Hallazgo | Tipo | Severidad | Acción |
|---|---|---|---|---|
| L1 | La lámina 12 dice «las ciento sesenta y tres marcas» tres frases después de decir que las marcas son «sesenta y un polígonos» | error | alta | Fix: son 163 **parches** marcados (`resultados.md:45`) |
| L2 | «se pesa cada parche igual» se oye como «todos pesan lo mismo», que es lo contrario de la ecuación que la lámina explica | error | alta | Fix: «por su atención igual que antes» |
| L3 | La lectura en voz alta es una **tercera capa** de QA, distinta del barrido automático y de `@humanizer-es`, y caza una clase propia | método | alta | ADDENDUM a [[deck-qa-puntos-ciegos-chequeo]] |
| L4 | La lámina 9 recita cuatro decimales dígito a dígito, los cuatro empezando con «cero coma nueve», con la tabla a la vista | estilo hablado | media | Fix: leer la fila por su dirección; los valores quedan en la tabla |
| L5 | El README del deck y `progress/current.md` no registran esta pasada | stale | media | Secciones nuevas |

## L1 — La unidad viaja en la palabra, y al hablarla se pierde

La lámina 12 decía, con veinte segundos de diferencia: «las marcas son **sesenta y un
polígonos** que el patólogo dibujó» y después «**las ciento sesenta y tres marcas** caen todas en
la segunda». Leído en la pantalla, uno completa solo; **dicho en voz alta, es una
contradicción**. La verdad de campo es `atencion_vs_patologo/resultados.md:45`: «Los **163
parches anotados** caen todos en la de abajo». 61 son los polígonos, 163 los parches que quedan
debajo de alguno.

El mismo defecto, en su otra forma, estaba en la lámina 3: «lo escalamos a **mil ochocientas
cincuenta y ocho láminas por partición**». La unidad real es la lámina-partición, pero al oírla
se entiende «1858 en cada una». Se resolvió diciendo **los dos** números, porque 1858 es el
titular del sprint y no correspondía hacerlo desaparecer: «mil ciento setenta y seis láminas
distintas, mil ochocientas cincuenta y ocho contando cada partición por separado»
(`q1_slots_escalado/resultados.md:6`).

**La clase**, que es lo que generaliza: cuando un número lleva su unidad pegada en una palabra
(«láminas-fold», «marcas»), el texto escrito deja que el lector la reconstruya del contexto y
**la voz no**. Es hermano del «26 vs 28» de la décima pasada, con la diferencia de que aquel se
arreglaba nombrando la unidad en la lámina y este, diciéndola completa en el guion.

## L2 — Una palabra que al oírse significa lo contrario

La lámina 6 explica que los dos órdenes de la ecuación dan el mismo número, y los dos pesan cada
parche por su atención. El guion decía «el camino de abajo es el de la ecuación: **se pesa cada
parche igual**, pero el clasificador se aplica a cada uno por separado». El «igual» quería decir
«igual que arriba»; dicho, se oye «**todos los parches pesan lo mismo**», que contradice
exactamente lo que la lámina está enseñando. Quedó explícito: «se pesa cada parche por su
atención igual que antes».

Es el hallazgo que mejor justifica la pasada. No es un error de dato ni de ritmo: es una frase
correcta escrita que **se vuelve falsa al pronunciarla**, y no hay cuenta ni skill que la
detecte.

## L3 — La tercera capa de QA

Las tres capas que corrimos sobre este deck cazan cosas disjuntas, y conviene tenerlo escrito:

| Capa | Qué caza | Qué NO ve |
|---|---|---|
| Barrido automático (reglas duras, tinta por renglón) | rayas, decimales, letras A/B/C/D, colisiones geométricas | cualquier cosa de sentido |
| `@humanizer-es` | tells de vocabulario y **racimos de ritmo** a lo largo de las 19 | concordancias, unidades, ambigüedad al oír |
| **Lectura en voz alta** | concordancias rotas, unidades que se pierden, frases que no entran en un respiro, palabras que al oírse invierten el sentido | lo que ya cubren las otras dos |

Lo que las separa es que la de humanización **cuenta** (por eso encontró los racimos y el arco
roto de la 17) y la lectura **entiende de a una frase**. Las siete que quedaron abiertas son de
una cuarta clase, la de vocabulario sostenido, que solo se ve leyendo todo seguido pero es
decisión de estilo, no defecto.

Las otras cinco correcciones de esta pasada, por si hay que rastrearlas: «pero **puesta** así»
con el sujeto cambiado de género (lámina 8), la comparación colgada «**como una de las copias**,
si uno mueve la mancha» (16), «Ese número **es** bien por debajo» (13), «cuyos nombres **se los**
pusimos» con el clítico duplicado (9), y «también **la mixta**» nombrando una tercera hipótesis
que el guion nunca había presentado (10), que ahora se dice en media línea tomándola del
`prereg.md` sin tocarlo.

## L4 — Cuatro decimales seguidos con la tabla a la vista

La lámina 9 recitaba «de cero coma nueve tres siete a cero coma nueve dos cinco, y el área bajo
la curva de cero coma nueve siete dos a cero coma nueve cinco siete». Los cuatro empiezan igual y
nadie los sigue de oído. **La tabla está proyectada**, así que el guion pasa a leer la fila por su
dirección («la exactitud algo más de un punto y el área bajo la curva un punto y medio, y los
valores exactos están en la fila»), que es además lo que pide la convención de notas para láminas
de resultados (`convenciones_deck_b5.md` §3.b, regla 11: leer la tabla por su columna, no
recitarla).

Los otros cuatro de respiro se resolvieron partiendo la frase, sin sacar contenido: la de la
lámina 17 (55 palabras) y la de la 6 (48) ganaron un punto seguido; la 18 cambió «entre
doscientas setenta y noventa unidades», que se oye como tres números, por «desde noventa unidades
totales hasta doscientas setenta»; y la 5 perdió el trabalenguas de oclusivas «un **p**untaje
crudo **p**or **p**arche en **p**orcentajes».

## L5 — README de la presentación y `progress/current.md`

El README gana la sección de la lectura en voz alta, y `progress/current.md` la sesión.

## Verificado sin cambios

- **Los dos `prereg.md` y los dos `resultados.md`**: intactos. El `prereg.md` de atención se
  **leyó** para nombrar la hipótesis mixta, no se tocó.
- **Ningún número cambió de valor.** El único que cambió de forma es el de la lámina 3, que pasa
  a decir los dos (1176 y 1858) en vez de uno mal enunciado.
- **Las láminas no se tocaron**: títulos, remates, rótulos y punteos guía siguen como los dejó el
  rediseño del 4-ago. El «fold por fold» del cuerpo de la 17 (`generate_b8_deck.py:2136`) queda
  como está por eso mismo, aunque el de las notas se haya listado como abierto.
- **Barrido de reglas duras sobre las 20 láminas, cuerpo y notas**: cero rayas, cero «palanca»,
  cero letras A/B/C/D. El único decimal está en el **punteo guía** de la 11, que no es prosa
  hablada y es el comportamiento esperado.
- **Deck**: 20 láminas, auditoría del generador en cero avisos, 1172 referencias forzadas a
  Barlow.
- **`CLAUDE.md`, agentes y skills**: sin cambios. Leer un guion no mueve ninguna regla.
- **El «0,89 vs 0,890»**: no se reabrió. Lo que esta pasada anota es otra cosa, la **pronunciación**
  de los decimales, y va al handoff como decisión de Ernesto.

## Lo que queda abierto y va al handoff

**Las siete de vocabulario que la lectura levantó y no se tocaron**, todas decisión de Ernesto:

1. **«fold» contra «partición»** conviven en la misma frase (láminas 17 y 18). En el cuerpo de la
   17 también, y ahí no se toca por regla.
2. **Tres sistemas para decir decimales**: dígito a dígito, decenas y centenas. **No es** el
   «0,89 vs 0,890» de las láminas, que está cerrado.
3. **«logit», «softmax», «sigmoide con temperatura»** sin definir, cuando el resto del guion
   evita el término técnico (convención §3.b, regla 5).
4. La lámina 9 **recorre la tabla 1 → 3 → 2** mientras el ojo va 1 → 2 → 3, y llama a la misma
   fila «la destacada» y después «la del medio».
5. **«rankearían»** (10), **«agarrar»** (20), **«pipeline»** (12).
6. **4799 dicho entero en tres láminas seguidas** (10, 11 y 12).
7. La lámina 13 dice «está entre el nueve por ciento más atendido»; el número es correcto
   (`resultados.md:27`, percentil mediano 91) pero «dentro del» se oiría mejor.

**Y lo de siempre**: la leyenda mezclada español/inglés de la figura de la 12, que es de
`atencion_vs_patologo/` y no del generador.

---

# Decimotercera pasada — las siete de vocabulario, resueltas (4-ago-2026, martes, 7ª)

> Sin jobs propios: el `4813` (`test_vista`, sucesor del `4809`) volvió a aparecer bajo la
> cuenta compartida `sdonoso` con el mismo `WorkDir=/media/administrador/Storage1/sdonoso/
> Test_D/D_abs`, fuera de este árbol y de `clam_environ`, y terminó durante la sesión. Ajenos:
> `4780` de `capstone`, `4800` de `gvenegas`. Workaround H sin efecto. Lo único tocado es el
> generador del deck y documentación.

La misión que dejó la duodécima: **decidir las siete de vocabulario**. Ernesto aprobó las siete
recomendaciones, que son **once ediciones** en `generate_b8_deck.py`, **todas en notas**. Ningún
número cambió de valor, ninguna lámina se tocó, y ni `prereg.md` ni `resultados.md` se abrieron
para escribir.

| id | Hallazgo | Tipo | Severidad | Acción |
|---|---|---|---|---|
| V1 | Tres de las siete **cambian de dirección** al verificar que el término está escrito en el CUERPO de la lámina | método | alta | ADDENDUM a [[deck-qa-puntos-ciegos-chequeo]] |
| V2 | La mezcla «fold»/«partición» es **del deck**, no del guion: el cuerpo de la 17 ya las usa juntas y «fold» está en el cuerpo de tres láminas | error de encuadre | media | Se arregla **solo la frase** donde conviven |
| V3 | No había convención de **pronunciación de decimales**; con tres sistemas en uso hacía falta una | convención | media | Regla nueva en `convenciones_deck_b5.md` §3.b |
| V4 | «pipeline» y «rankearían» tenían una **segunda ocurrencia** que el handoff no listaba | stale | baja | «pipeline» se cambia en las dos; «rankearían» no se toca |
| V5 | El README del deck y `progress/current.md` no registran esta pasada | stale | media | Secciones nuevas |

## V1 — Una decisión de vocabulario del guion no se resuelve solo en el guion

Es el hallazgo de la pasada, y contradice el reflejo natural. Las siete llegaron descritas como
decisiones sobre **cómo se dice** algo, así que parecían resolverse leyendo el guion. Tres de
ellas se dieron vuelta al abrir el generador:

- **Los tres términos técnicos** (`logit`, `softmax`, `sigmoide con temperatura`) están
  **escritos en las láminas 6, 7 y 8** (`generate_b8_deck.py:1378`, `:1398`, `:1477`, `:1529`).
  Quitarlos del guion, que era la lectura obvia del hallazgo, habría dejado al presentador
  diciendo una palabra distinta de la proyectada. Lo que pide la convención (§3.b, regla 5) es
  **definir antes de usar**, no evitar: así que se **glosaron** los dos que no tenían glosa y el
  tercero se dejó, porque ya la traía.
- **«fold»** está en el cuerpo de la tabla de la 15, en el rótulo de la figura de la 17 y en el
  rótulo más el remate de la 18. Ver V2.
- **«rankearían»** está en los **dos paneles de hipótesis** de la lámina 10 (`:1700`, `:1706`).
  Cambiarlo solo en el guion desajusta voz y pantalla, y el cuerpo está congelado por el pedido
  del rediseño del 4-ago. **No se tocó.**

**La clase**, que es lo que generaliza: cuando el cuerpo está congelado, el guion **hereda su
vocabulario**, y el desajuste entre lo que se oye y lo que se lee cuesta más que el tell que uno
venía a sacar. Antes de reescribir una palabra del guion hay que **grepear el generador** para
ver si está proyectada. Es hermano del criterio de las tres capas (L3 de la duodécima), pero
apunta a otra cosa: no a qué capa caza el defecto, sino a **dónde se verifica el arreglo**.

## V2 — La mezcla «fold»/«partición» ya estaba en el deck

El handoff la planteaba como un problema del guion con una excepción en el cuerpo de la 17. La
verificación muestra algo distinto: el cuerpo de la 17 **usa las dos palabras en el mismo
bloque** (`:2141` «la diferencia pareada fold por fold» junto a `:2144` «5 particiones»), y
«fold» aparece además en `:1972-1973` (tabla de la 15), `:779` (rótulo de la figura del grid) y
`:2214`/`:2216` (rótulo y remate de la 18).

Con el cuerpo congelado, unificar el guion entero a «partición» habría contradicho cuatro
rótulos proyectados. Se hizo lo contrario de lo global: **hay una sola frase donde las dos
palabras conviven** (`:2173`), y es la que se arregló. El resto de los «folds» del guion queda,
porque cada uno está respaldado por algo que se lee en pantalla.

> **Antes**: «…comparamos recortar por un lado contra recortar por el otro, con las mismas
> particiones y midiendo la diferencia **fold por fold**.»
> **Después**: «…comparamos recortar por un lado contra recortar por el otro **sobre las mismas
> particiones, midiendo la diferencia en cada una**.»

## V3 — La regla de decimales que faltaba

El guion tenía tres maneras de pronunciar un decimal y ninguna razón para elegir entre ellas. La
regla que se fija, y que sirve para cualquier guion futuro: **un decimal se dice tal cual, dos se
agrupan en decenas, tres en centenas.** Con eso el guion entero queda consistente y solo cambian
dos frases: `0,46 / 0,48` en la 12 y `0,056` en la 16.

La regla **no toca** el «0,89 vs 0,890», que es qué se escribe en la lámina y está cerrado: al
contrario, lo respeta, porque cada uno se pronuncia según sus decimales y el guion sigue diciendo
lo que la lámina muestra.

## V4 — Las segundas ocurrencias

«pipeline» aparecía también en la nota de la lámina 5 (`:1341`, «en nuestro pipeline son
quinientos doce números»), no solo en la 12. Se cambiaron las dos, porque dejar una sola habría
sido peor que no cambiar ninguna. «rankearían» tiene su segunda en la 10 (`rankeen`), y las dos
se quedan por lo de V1.

## Las once ediciones

| Lámina | Antes | Después |
|---|---|---|
| 5 | «en nuestro **pipeline** son quinientos doce números» | «en nuestro **caso**…» |
| 6 | «el **logit final** es el mismo número por los dos caminos» | «el logit final, **ese número que sale del clasificador**, es el mismo…» |
| 6 | «sale de una **softmax**, así que todos sus valores son positivos» | «sale de una softmax, **el reparto del cien por ciento que vimos recién**, así que…» |
| 9 | recorrido 1 → 3 → 2, y «la fila destacada» + «esa fila del medio» | recorrido **1 → 2 → 3**, y **«la fila destacada»** las dos veces |
| 11 | «Se toman **los cuatro mil setecientos noventa y nueve** parches» | «Se toman **todos los** parches» (el número está proyectado) |
| 12 | «el **pipeline** extrajo parches de las dos» | «el **procesamiento** extrajo…» |
| 12 | «entre cero coma **cuatro seis** y cero coma **cuatro ocho**» | «entre cero coma **cuarenta y seis** y cero coma **cuarenta y ocho**» |
| 13 | «está **entre** el nueve por ciento más atendido» | «está **dentro del** nueve por ciento…» |
| 16 | «cero coma **cero cinco seis**» | «cero coma **cero cincuenta y seis**» |
| 17 | «con las mismas particiones y midiendo la diferencia **fold por fold**» | «**sobre** las mismas particiones, midiendo la diferencia **en cada una**» |
| 20 | «**agarrar** un detector de mitosis público» | «**tomar** un detector…» |

La de la lámina 9 arregla las dos cosas de una: el orden pasa a ser el que sigue el ojo, y la
fila queda con **un solo apodo**. Cumple además la regla 11 de la convención (recorrer la tabla
en el orden en que se lee). La tabla es ABMIL / **CLAM destacada** / TransMIL (`:1601-1603`).

## Verificado sin cambios

- **Los dos `prereg.md` y los dos `resultados.md`**: intactos, ni leídos para escribir.
- **Las láminas**: cero cambios. Títulos, remates, rótulos y punteos guía como los dejó el
  rediseño del 4-ago. El «fold por fold» del cuerpo de la 17 sigue ahí, ahora **por decisión
  verificada** y no por omisión.
- **Ningún número cambió de valor.** Los dos decimales que se tocaron cambiaron de
  **pronunciación**, no de cifra.
- **Barrido de reglas duras sobre las 20 láminas, cuerpo y notas**: cero rayas, cero «palanca»,
  cero letras de rotulación, cero decimales en cifras dentro de la prosa hablada.
- **Deck**: 20 láminas, auditoría del generador en cero avisos, 1172 referencias forzadas a
  Barlow. Prosa de 6104 a **6117 palabras**, +13.
- **`CLAUDE.md`, agentes y skills**: sin cambios. Ninguna regla dura se movió.
- **No se volvió a pasar `@humanizer-es`** ni a leer el guion entero en voz alta: las once son
  ediciones de frase, no reescrituras de lámina, y el handoff anterior lo dejaba explícito.

## Lo que queda abierto y va al handoff

- **La leyenda mezclada español/inglés** de la figura de la 12 («Immune cells», «Stroma»,
  «Nucleos» sin tilde). Sigue siendo de `atencion_vs_patologo/`, no del generador: arreglarlo es
  regenerar esa figura, y es decisión de Ernesto si vale la pena antes del viernes. **Es el único
  pendiente que le queda al deck.**

---

# Decimocuarta pasada — el recorte de 20 a 16 láminas (5-ago-2026, miércoles, 8ª)

> Sesión de rediseño, no de auditoría: Ernesto pidió **nueve cambios** sobre el deck del 4-ago
> y la pasada registra lo que salió al ejecutarlos. Dos hallazgos son de **dato** (uno corrige
> una cifra publicada en el README) y tres son de **método de QA**.
>
> Deck resultante: **16 láminas**, auditoría del generador en cero, 1172 referencias forzadas
> a Barlow. Ningún `prereg.md` ni `resultados.md` se tocó, y **ningún número de los dos
> experimentos cambió de valor**.

| id | Hallazgo | Tipo | Severidad | Acción |
|---|---|---|---|---|
| R1 | El «153 / 978 / 934 láminas de entrenamiento» del README del deck son **totales de split**, no la parte de train | error | **alta** | Cifras corregidas a 120 / 783 / 746 / 749, contadas sobre los `splits_*_bool.csv` |
| R2 | La tabla de la lámina no decía **por qué** de la corrida de cinco aparecían dos folds | stale | media | Pie nuevo: son los dos únicos donde 129741 cae en validación |
| R3 | Un **conector cruzando un texto**: clase de defecto que ningún chequeo de cajas ve | método | media | Registrado en [[deck-qa-puntos-ciegos-chequeo]] |
| R4 | **Offsets de rótulo fijos** en un helper reusado con otra altura | método | media | `barras_divergentes` los calcula desde el alto de fila; registrado |
| R5 | Fusionar dos láminas vuelve **vecinos** a dos vocabularios («fold» y «partición») | método | media | Unificado en la lámina; registrado como chequeo obligatorio del recorte |
| R6 | `objetivos_sprint8.md` y `progress/current.md` no registran el recorte | stale | media | Secciones actualizadas |

## R1 — La cifra publicada era la del split entero, no la del entrenamiento

Es el hallazgo que más vale de la pasada, porque **corrige un número que ya estaba escrito**.
El §«La procedencia» del README del deck (4-ago) decía que los datasets de entrenamiento de los
cuatro checkpoints primarios eran «153 láminas (privado), 978 (privado + TCGA) y 934 (privado +
TCGA, cinco particiones)».

Contado el 5-ago sobre los splits reales:

| Corrida | split_dir | Total | Train | Val | Test | 129741 |
|---|---|---:|---:|---:|---:|---|
| privado, single-split | `splits/grado_histologico_mitotic_rate_100` | 153 | **120** | 15 | 18 | val |
| privado + TCGA, single-split | `splits/..._combined_100` | 978 | **783** | 98 | 97 | val |
| privado + TCGA, fold 0 | `splits_5fold/..._combined_100` | 934 | **746** | 92 | 96 | val |
| privado + TCGA, fold 2 | idem | 934 | **749** | 93 | 92 | val |

153 = 120 + 15 + 18 y 978 = 783 + 98 + 97: los números publicados son la **suma de las tres
particiones**. No invalida nada de `atencion_vs_patologo/` —su `resultados.md` nunca afirmó
tamaños de entrenamiento, solo que la lámina no estaba en train (§2.d)— pero sí era incorrecto
como descripción de «con qué se entrenó». La lámina ahora usa los de train, que es lo que su
columna dice.

## R2 — La pregunta que la tabla dejaba abierta

Ernesto: *«no entiendo la tabla a qué modelo o checkpoint entrenando con 5 fold, fold 0 y luego
en la siguiente fila 5 fold, fold 2»*. La respuesta estaba en `resultados.md` §2.d y no en la
lámina: **129741 está en `val` en los folds 0 y 2, y en `train` en 1, 3 y 4**. Por eso el grupo
primario tiene esos dos y no los cinco. Es un dato de diseño del experimento que la tabla
mostraba como si fuera una elección arbitraria.

## R3 y R4 — Dos puntos ciegos nuevos del chequeo automático

Auditoría en cero y **ocho defectos a la vista**. Seis son de la familia ya conocida (texto que
compite, número partido en dos renglones, rótulo repetido). Los otros dos son clase nueva:

- **Un conector cruzando un texto** (lámina 5): la línea que baja la atención hasta el Top-K
  pasaba por el medio del segundo renglón del bloque de mediciones. Los dos objetos están dentro
  de su caja y dentro del lienzo; lo que colisiona es **una línea contra un texto**, y `auditar`
  solo mide texto contra su propia caja. Hermano del «dos objetos válidos superpuestos» del
  4-ago, con la diferencia de que acá uno de los dos **no tiene caja**.
- **Offsets fijos en un helper reusado con otra altura** (lámina 14): `barras_divergentes` ponía
  el rótulo y su subtítulo a **0,26 fijos** del centro de la fila. Con la figura a 1,70 de alto
  eso sobra; al bajarla a 1,16 para la lámina fusionada, la fila queda en 0,39 y el subtítulo de
  una pisa el rótulo de la siguiente. **La regla que queda:** un helper que posicione texto con
  constantes absolutas es correcto solo a la altura para la que se escribió; al reusarlo con
  otra, las constantes se derivan del alto disponible.

## R5 — Fusionar láminas vuelve vecinos a dos vocabularios

La decimotercera pasada ya había cazado «fold» y «partición» conviviendo **dentro** de la
lámina 17. Al fusionar 17 y 18 el problema reaparece en la lámina nueva, ahora entre el cuerpo
(«5 particiones») y el pie del helper («cada cuadro es un fold»). No es reincidencia: es que
**cada fusión crea vecindades que antes no existían**, y el vocabulario es lo primero que choca.
Queda como chequeo obligatorio de cualquier recorte futuro, al lado del de números que chocan
entre láminas vecinas (décima pasada).

Resuelto unificando a «partición» en la lámina del grid, y a «fold» en la de los cuatro modelos
—donde es el identificador del checkpoint— sin mezclar dentro de ninguna de las dos.

## Verificado sin cambios

- **Los dos `prereg.md` y los dos `resultados.md`**: intactos.
- **Las láminas 9, 10 y 11** (las viejas 12, 13 y 14): cero cambios, por pedido explícito.
- **`CLAUDE.md`, agentes y skills**: sin cambios. Ninguna regla dura se movió.
- **Barrido de reglas duras sobre las 16 láminas, cuerpo y notas**: cero decimales con punto,
  cero rayas, cero «palanca», cero letras de rotulación.
- **Las 14 láminas con notas** las tienen; ninguna quedó sin guion.

## Lo que queda abierto y va al handoff

- **El guion de las láminas nuevas y fusionadas** (4, 5, 6, 8, 12, 13, 14 y 16 de la numeración
  nueva) **no pasó por `@humanizer-es`** ni por la lectura en voz alta. Las no tocadas conservan
  las dos pasadas del 4-ago. Es el pendiente principal de cara a la reunión.
- **La leyenda mezclada español/inglés** de la figura de marcas (hoy lámina 9). Ernesto dijo que
  esa lámina queda como está, así que deja de ser pendiente del deck y pasa a ser una decisión
  tomada.

---

# Decimoquinta pasada — el guion de las ocho, con las tres capas (5-ago-2026, miércoles, 9ª)

> Cierra el pendiente principal que dejó la decimocuarta pasada: las ocho láminas nuevas o
> fusionadas del recorte (4, 5, 6, 8, 12, 13, 14 y 16) no tenían las dos capas de QA de prosa
> que sí tenían las demás. Ahora las tienen, más la lectura en voz alta.
>
> **14 ediciones, las 14 dentro de `notes(...)`**, verificado a máquina: de las 33 líneas
> modificadas, **cero** caen fuera de una llamada `notes()`, así que el cuerpo de las láminas
> no se tocó y no correspondía volver a mirarlas. Auditoría del generador en cero, guion de
> 6532 a 6512 palabras. Ningún `prereg.md` ni `resultados.md` se tocó y **ningún número de los
> dos experimentos cambió de valor**.

| id | Hallazgo | Tipo | Severidad | Acción |
|---|---|---|---|---|
| S1 | La 14 glosaba el reparto de peso entre los 300 slots como «poco más de la mitad **concentra casi todo**», que mezcla `N_eff` con la concentración | error | **alta** | Pasa a decir lo mismo que la lámina 3: «el reparto ocupa alrededor de ciento sesenta». Registrado en [[mammoth-slot-routing-weight]] |
| S2 | El hallazgo mayor de la pasada de humanizer **no fue un tell de prosa sino un arco roto**: la 4 y la 5 contaban el mismo montaje dos veces | método | **alta** | La 5 se apoya en la 4; baja de 887 a 846 palabras. Registrado en [[humanizer-es-skill]] |
| S3 | El choque de vocabularios de R5 reaparece en una **tercera superficie**: entre el guion y el cuerpo, con «slots» en el propio **título** | método | media | Se glosa una vez y se adopta lo escrito. Registrado en [[deck-qa-puntos-ciegos-chequeo]] |
| S4 | El tercer término de la pérdida de SI-MIL se contaba como «un peso bastante alto», sin número, teniéndolo | stale | media | Es **λ = 20** contra 1 de los otros dos (`simil_estudio.md:68`) |
| S5 | Tres repeticiones textuales más entre láminas, invisibles dentro del generador | método | baja | Resueltas; ver abajo |

## S1 — Glosar `N_eff` como concentración mezcla dos mediciones

Es el hallazgo que más vale, porque **toca cómo se cuenta un número del sprint** delante de
Sebastián. La lámina 14 decía que, del reparto del peso entre los 300 slots, «poco más de la
mitad concentra casi todo».

Eso junta dos mediciones que `../q1_slots_escalado/resultados.md:38` separa **a propósito**:

- el número efectivo es **159.5 de 300** (`exp` de la entropía), y
- por otro lado **38 slots llevan la mitad del peso** y hacen falta **169 para el 90 %**.

El propio archivo advierte, textual: *«`N_eff = 159.5` no significa 159 slots trabajando por
partes iguales»*. La frase de la lámina tomaba el conteo de la primera medición («poco más de
la mitad» de 300) y le pegaba el predicado de la segunda («concentra casi todo»). Dicha en voz
alta suena a una afirmación de sesgo del reparto, que es justo lo que el número efectivo **no**
dice.

Resuelto adoptando la formulación de la **lámina 3**, que ya había pasado las dos capas el
4-ago y dice «se ocupan alrededor de ciento sesenta unidades de las trescientas». Las dos
láminas ahora coinciden. **Ningún número cambió**: cambió la glosa.

## S2 — El hallazgo mayor de una pasada de humanizer sobre láminas fusionadas fue un ARCO

La pasada se pedía para quitar tells de prosa. Lo que apareció primero, y con diferencia, fue
otra cosa: la **lámina 4 describe la figura del paper** (los dos caminos, la caja amarilla que
hace de puente) y la **lámina 5 volvía a describir el mismo montaje desde cero**, unas 110
palabras a veinte segundos de distancia, incluida la bisagra contada dos veces con dos nombres
(«la bisagra del diseño» / «el movimiento central del diseño»).

No es un defecto de estilo: es el arco que rompió la fusión. La 5 nació de juntar tres láminas
de ecuaciones, y su guion se escribió como si abriera el tema, cuando ahora entra después de la
figura del paper. **Dentro del generador es invisible** —las dos llamadas `notes()` están a 130
líneas de distancia— y en el archivo extraído salta a la primera lectura.

La 5 ahora se apoya en la 4 («es el mismo recorrido, redibujado con los anchos y la notación»)
y va directo a lo que agrega. Baja de 887 a 846 palabras, y sigue siendo la más larga del deck.

**La regla que queda:** al humanizar láminas fusionadas, la primera pasada es de **arcos**, no
de prosa. Una lámina fusionada hereda un guion escrito para otro lugar del recorrido.

## S3 — El choque de vocabularios tiene una tercera superficie

La R5 de la decimocuarta pasada registró que fusionar láminas vuelve vecinos a dos
vocabularios, y lo vio dos veces: **dentro del cuerpo** de una lámina (13ª pasada) y entre el
**cuerpo y el pie de un helper** (14ª). Acá aparece la tercera: entre el **guion y el cuerpo**.

La lámina 14 decía, hablada, «unidades» y «niveles», mientras su cuerpo escribe «peldaños» y su
**título** escribe «slots». El asistente lee una palabra en la pantalla y oye otra, sin que
nadie las conecte nunca.

Resuelto con la regla del ADDENDUM 23:20 del 4-ago: si la palabra está escrita en el cuerpo,
**se glosa, no se saca**. Una sola vez, al abrir la lámina («en el título aparecen como slots,
que es lo mismo»), y «peldaño» se adopta en el guion porque es lo que está escrito. El resto de
la lámina puede seguir diciendo «unidades», que es lo que dicen la lámina 3 y el punteo guía.

**Lo que agrega a R5:** el chequeo de vocabulario de un recorte no se cierra mirando el cuerpo.
Son tres superficies —cuerpo, pie de helper y guion— y el título cuenta como cuerpo.

## S4 y S5 — Un dato vago, y tres repeticiones

- **S4:** la lámina 6 contaba el tercer término de la pérdida de SI-MIL como «con un peso
  bastante alto». El valor estaba en el repo hace días: **λ = 20**, contra 1 de cada uno de los
  otros dos términos (`../simil_estudio.md:68`, `../simil_explicacion_matematica.md:438`, los
  dos verificados contra el paper). Un hedge vago donde había número.
- **S5:** tres repeticiones textuales más, todas entre láminas y por eso invisibles dentro del
  generador. «dos modelos corriendo en paralelo» aparecía en el guion de la 5, en el **cuerpo**
  de la 6 y en el guion de la 6 (manda el cuerpo: se saca de la 5). Y la 6 hacía tres veces el
  mismo movimiento de «esto es lo que hay que llevarse».

**Y una que NO se tocó, por una decisión previa.** «una lámina y un anotador describen, no
establecen» aparece **textual** en la 8 y en la 13, y citada en la 16. Parecía la cuarta
repetición, pero [[humanizer-es-skill]] §5 la registró el 4-ago como **salvedad repetida a
propósito**: no es fórmula de IA si el guion la reconoce como consigna sostenida, y se
preserva junto con los quiasmos «X, no Y». Se respetó: la salvedad queda **entera y textual**
en las tres. Lo único que cambia es que la 13 ahora la introduce reconociéndola —«sigue en pie
lo que dije al empezar»— que es justo el criterio que la memoria pide, y que la 13 era la única
de las tres que no cumplía.

De la lectura en voz alta salieron además cuatro correcciones de las que solo se oyen: «un
vector de quinientos doce» perdía la unidad, «contra uno de cada uno de los otros dos» tenía
tres «uno» en una frase, «trescientas» aparecía dos veces en una oración de la 14, y «responde
con más convicción la respuesta equivocada» (la 12) pasa a «se equivoca con más convicción».

## Verificado sin cambios

- **Los dos `prereg.md` y los dos `resultados.md`**: intactos. Ningún número se movió.
- **El cuerpo de las 16 láminas**: verificado **a máquina**, no a ojo. Las 33 líneas del diff
  caen todas dentro de una llamada `notes()`. Por eso no se re-inspeccionaron las láminas, que
  es lo que pedía el plan del handoff.
- **Barrido de reglas duras sobre el guion**: cero rayas «—», cero «palanca». Las 17 rayas que
  aparecían en el archivo extraído eran de las cabeceras del propio script de extracción.
- **`CLAUDE.md`, agentes y skills**: sin cambios. Ninguna regla dura se movió.
- **«fold» en la lámina 12 y «partición» en la 14 NO es un defecto**: la R5 de la decimocuarta
  pasada lo decidió así a propósito —«fold» es el identificador del checkpoint en esa tabla— y
  la regla es no mezclarlos **dentro** de una lámina, no unificarlos entre láminas. Se verificó
  antes de tocar nada.

## Lo que queda abierto y va al handoff

- **Nada del guion.** Las 14 láminas con notas tienen ahora las tres capas.
- Los pendientes del sprint que no son del deck siguen abiertos y van al handoff sin cambios:
  las dos preguntas de la reunión (encargo 2 y cuántas láminas anotadas hay), la réplica del
  dato abierto del 4589 con semillas nuevas, y el sign-off del patólogo.

---

# Decimosexta pasada — la sesión de estudio, y el alcance del grep del H1 (6-ago-2026, jueves)

> Sesión de **estudio** del deck, no de construcción: el handoff del 5-ago la orientaba a
> dominar el material antes de la reunión con Sebastián. El deck **no se tocó** y ningún
> número del sprint cambió. Los dos hallazgos salieron de verificar contra verdad de campo
> los números que el guion dice de memoria.

| id | Hallazgo | Tipo | Severidad | Acción |
|---|---|---|---|---|
| P1 | **El grep del H1 (octava pasada) no cubrió el documento que ORIGINÓ la frase.** «El margen de recorte está en S» quedó sin acotar en `q1_slots_escalado/resultados.md` (2 veces, una bajo el encabezado «Qué se puede afirmar ahora») y en la memoria `slot-unidad-de-morfologia` | contradicción | **alta** | Acotación aditiva en los dos, misma redacción canónica que `CLAUDE.md` |
| P2 | **El dataset CDIS `_ci_reform` admite dos cuentas de negativos, las dos correctas**: 132 en el dataset y 65 evaluados. Chocan si alguien las cruza en una repregunta | reconciliación | media | Nota de una línea en el `resultados.md` del grid |

## P1 — Un grep que buscó donde sabía que estaba

**Qué había pasado.** El H1 de la octava pasada (4-ago) corrigió la frase en cinco lugares:
`CLAUDE.md` dos veces, la memoria `mammoth-slot-routing-weight` cuatro, y `MEMORY.md` una.
La corrección en sí fue correcta y su criterio (aditivo, la medición se preserva textual) es
el que se reusa acá. Lo que falló es **el alcance del `grep`**: buscó en los frentes donde ya
sabía que la frase vivía y no barrió el repo entero.

**Los dos que quedaron afuera**, verificados con `grep -rn "margen" --include="*.md"` sobre
todo el árbol más el directorio de memorias:

| Fuente | Línea | Por qué importa |
|---|---|---|
| `q1_slots_escalado/resultados.md` | 62 y 121 | Es **el documento que originó la frase**, y la 121 está bajo «Qué se puede afirmar ahora». El handoff lo nombra como verdad de campo del 159.5 |
| memoria `slot-unidad-de-morfologia` | 32 | La usa como **razonamiento de apoyo** («Si la morfología vive en el slot, el experto es un agrupador»), no como dato suelto |

**La lección, que es de método y sobrevive a este caso.** Cuando una afirmación propagada se
refuta, el documento **más peligroso no es el que la repite, es el que la originó**: ahí está
enunciada con más fuerza, sin las salvedades que los demás le fueron agregando al citarla, y
es el que alguien va a abrir cuando quiera respaldar el número. **El barrido tiene que ser
sobre el repo entero y el directorio de memorias, no sobre los frentes donde uno recuerda
haberla escrito.** Anotado en la skill `@knowledge-audit`.

**Qué NO se tocó**, y por qué:

- `progress/current.md` (L128, L862) y `sprints/B7_sprint7/resultados_interpretabilidad.md`
  (L222): son **registro cronológico**, valen como «qué se sabía y cuándo». El propio H1 fijó
  ese criterio.
- El generador del deck del B7 (L1273, L2105, L2137): presentación ya dada, histórica.
- El ADDENDUM 24-jul de `CLAUDE.md` (L910, L921): queda sin acotar en el sitio, pero el
  ADDENDUM 27-jul que le sigue lleva el `⚠ ACOTADO` inline. Cadena cronológica, criterio del H1.

## P2 — 132 negativos y 65 negativos son los dos correctos

**Dónde chocan.** La lámina 14 del deck dice «862 láminas, 730 con presencia y 132 no», que
sale de `grid_expertos_slots/prereg.md:135`. El B7 y `CLAUDE.md` dicen «**65 negativos en
total**, ~13 por fold» (`B7/resultados_interpretabilidad.md:58`, `guia_estudio_b7.md:115`,
DATO ABIERTO del Hallazgo 12).

**Por qué los dos son correctos**, contado sobre los splits reales
(`data/splits_kfold/carcinoma_ductal_insitu_presente_ci_reform_100`) y el CSV de labels:

| Denominador | n | Negativos |
|---|---:|---:|
| Dataset completo | 862 | **132** |
| Unión de los 5 test (disjuntos) | 429 | **65** |
| Cada test individual | 85-88 | **13** en las cinco, exacto |

Los cinco test son **disjuntos** y cubren 429 de las 862, o sea la mitad del dataset. Los
otros 67 negativos viven siempre en train o val y **nunca se evalúan**. De ahí que 13 × 5 = 65
cierre exacto.

**La frase para decirlo**, si sale en la reunión: *el dataset tiene 132 negativos; los que
llegan a evaluarse alguna vez son 65, trece por partición, porque las particiones de prueba no
se solapan y entre las cinco cubren la mitad del conjunto.*

## Verificaciones que salieron limpias

Los ocho números que el handoff marcaba como de mayor riesgo de repregunta se verificaron
contra verdad de campo, uno por uno, y **los ocho reproducen**: 0.890 ± 0.039 y el percentil 91
de mitosis, la banda 0.67-0.75 de las ~440 traslaciones, el 0.462-0.478 del efecto de región,
los tres contrastes del grid, el 159.5 de 300, los tamaños de entrenamiento 120 / 783 / 746 /
749, y el 862 = 730 + 132 contado sobre el CSV.

- **El deck no se tocó.** Cero ediciones al generador, cero regeneraciones, cero figuras.
- **Nada de GPU.** Sin `sbatch`; los dos jobs del nodo son ajenos y no leen este árbol.
- **`prereg.md` y `resultados.md` de los dos experimentos**: intactos salvo la acotación
  aditiva del P1, que no toca ningún número.

---

# Decimoséptima pasada — la sesión de ensayo, y una nota que su propio presentador no entendió (6-ago-2026, jueves, tarde)

> Sesión de **ensayo hablado** de la lámina 15 antes de la reunión, no de construcción. El
> deck **no se tocó**: cero ediciones al generador, cero regeneraciones. Los tres hallazgos
> salieron de dos lugares: leer la lámina 15 como quien la va a decir en voz alta, y que
> Ernesto reportara que **no entendía** la nota de la lámina 9 después de leerla dos veces.

| id | Hallazgo | Tipo | Severidad | Acción |
|---|---|---|---|---|
| Q1 | **La nota de la lámina 9 pasó las tres capas de QA y su propio presentador no la entiende.** El argumento del confundido de región depende de una premisa que está en la lámina 8, a 4½ minutos de distancia, y la nota nunca la vuelve a invocar | error de exposición | **alta** | ADDENDUM a [[deck-qa-puntos-ciegos-chequeo]]: es una **cuarta capa** de QA. Redacción propuesta lista, **sin aplicar** (decisión de Ernesto) |
| Q2 | **`hojas_reunion.md` encabeza con «viernes 7-ago-2026»**, y la reunión con Sebastián es **hoy jueves 6**. Es el documento que se lee EN la reunión | stale | **alta** | Corregir la cabecera; ADDENDUM aditivo en las dos memorias que arrastran la fecha vieja |
| Q3 | **26 y 28 no son la misma unidad, y ahora está la regla de conteo.** La décima pasada ya registró que los dos son correctos, pero ninguno de los dos documentos decía **por qué** difieren | verificación | media | Nota de una línea en `atencion_vs_patologo/resultados.md`, con la descomposición sacada del CSV |

## Q1 — Una nota correcta, auditada, y que no se entiende

**Qué pasó.** Ernesto leyó los dos párrafos finales de la nota de la lámina 9 (el confundido de
las dos regiones de escaneo) y dijo dos veces que no los entendía. Esa nota es de las 14 que la
decimosexta pasada declaró con **las tres capas de QA** encima: barrido automático, `@humanizer-es`
y lectura en voz alta.

**Por qué las tres capas no podían verlo.** La tabla de las tres capas
([[deck-qa-puntos-ciegos-chequeo]], ADDENDUM del 4-ago 23:00) dice que la lectura en voz alta
«entiende **de a una frase**». Acá **cada frase por separado es correcta y comprensible**. Lo que
falla es una propiedad del **argumento completo**, no de ninguna frase: le falta el eslabón que
conecta el confundido con el método.

**El eslabón, con precisión.** El número es un AUC pareado, y la lámina 8 **sí** lo define
textualmente: *«es la probabilidad de que, si tomo un parche marcado y uno sin marca al azar, el
marcado tenga más atención»*. Lo que la lámina 9 nunca dice es que ese *«uno sin marca al azar»*
**incluye los 2303 parches de la otra región**, que es exactamente lo que convierte a la región en
un rival y vuelve el confundido un problema. La nota anuncia *«si la región de abajo recibiera de
por sí más atención, el número mediría la región»* como si esa consecuencia fuera evidente, y solo
lo es para quien tiene la mecánica del pareo fresca.

**No es que la premisa falte del deck. Es que está a 4½ minutos y la nota no la vuelve a
invocar.** La distinción importa porque cambia el arreglo: no hay que re-enseñar el AUC, alcanza
con una oración que lo re-enganche donde se necesita.

**La regla que queda, y es una capa nueva de QA:**

> Cuando una nota introduce una **complicación** sobre un método ya explicado (un confundido, una
> excepción, un caso especial), tiene que **volver a invocar la pieza del método que hace que la
> complicación importe**. No alcanza con que esa pieza esté definida antes.

**Y el motivo por el que ninguna capa anterior la caza:** el autor **siempre** tiene el método
entero en la cabeza, así que para el autor el eslabón está ahí aunque no esté escrito. Las tres
capas las corre el autor. La cuarta es la única que necesita un lector que **no** tenga el
resultado en la cabeza, y acá la corrió Ernesto sin proponérselo. Proxy practicable en solitario:
por cada nota argumentativa, listar de qué premisas depende la conclusión y verificar que cada una
esté **en esa nota**.

**Estado: diagnosticado y NO aplicado.** La redacción propuesta existe (re-engancha el pareo en
una oración, mismo largo), pero editar el deck el día de la reunión es decisión de Ernesto y el
handoff vigente pedía no tocarlo. Va al handoff como pendiente con la redacción lista.

## Q2 — El documento que se lee en la reunión tiene la fecha vieja

**La verdad de campo**: la reunión con Sebastián es el **jueves 6-ago**; el **viernes 7 es la de
Benjamín**. Está en `objetivos_sprint8.md:96`, en `presentacion_b8/README.md:15`, en
[[deck-b8-dos-ejes-simil-mitosis]] (dos veces) y en la línea de índice de
[[papers-rama-mitosis-bcd]]. El deck escribe 06/08/2026.

**Lo stale**: `tareas_geometricas/hojas_reunion.md:3` («viernes 7-ago-2026»), que es **el
documento que Ernesto tiene abierto durante la reunión**, y el cuerpo de la memoria
[[papers-rama-mitosis-bcd]] (ADDENDUM del 3-ago, líneas 161-165), que quedó **contradicho por su
propia línea de índice**.

**Lo que NO se toca**: los registros históricos que dicen 07/08 porque eran correctos cuando se
escribieron (`reunion_31jul_redireccion.md`, las pasadas C1 y E1 de esta misma auditoría,
[[simil-hovernet-decision-31jul]]). La cuarta y la quinta pasada ya pelearon esta fecha dos veces;
la lección de entonces (registrar sin borrar) sigue vigente y por eso acá se corrige **aditivo**.

**Ojo con una trampa de esta corrección**: [[reunion-24jul-encargos-b8]] tiene la línea del 07/08
marcada con *«Esta línea es la correcta; no volver a marcarla como stale»*. Era cierto el 3-ago y
dejó de serlo. Se le agrega el puntero en vez de borrar la marca, porque la marca documenta que
esa fecha se dudó dos veces sin motivo.

## Q3 — 26 son polígonos, 28 son parches: la regla de conteo

La décima pasada (punto ciego nuevo 3) ya registró que **«26 marcas» y «28 parches» son los dos
correctos** y que se arregla nombrando la unidad, cosa que el deck ya hace (la lámina 9 dice
«sesenta y un polígonos» y la 11 titula «Los 28 parches»). **No es un hallazgo nuevo**; se verificó
antes de reportarlo ([[verificar-antes-de-pedir-dato]]).

Lo que ningún documento decía es **por qué difieren**. Sacado de
`anotaciones_patologo/parches_anotados_129741.csv` (163 filas, columna `clases` multi-etiqueta con
`|`):

```
   parches con Mitosis           = 26 (solo Mitosis) + 1 (Mitosis|Nucleos alto grado) + 1 (Mitosis|Tumor) = 28
   parches con Nucleos alto grado = 12 + 1 (el compartido con Mitosis)                                    = 13
```

Los **siete** grupos de la tabla del §1 de `atencion_vs_patologo/resultados.md` se reproducen
exactos con esa regla (Tumor 45+2+1 = 48, Immune cells 21+2 = 23, necrosis 16+2 = 18, Stroma 10+2 =
12, Tejido Adiposo 27). O sea: **26 cuenta polígonos que dibujó el patólogo, 28 cuenta parches que
tocan al menos un polígono de mitosis**. Son unidades distintas y no tienen por qué coincidir.

**Lo que NO se afirma**: la descomposición exacta del +2 (cuántos vienen de una marca de 36 px que
cruza el borde entre dos parches de 256 y cuántos de dos marcas que caen en el mismo parche) **no
se calculó**. La regla de conteo alcanza para responder la repregunta y no requiere esa
descomposición.

## Verificado sin cambios

- **El deck**: cero ediciones al generador, cero regeneraciones, cero figuras. El guion se
  regeneró para leerlo y es derivado gitignored.
- **Ningún número del sprint se movió.** Los dos `prereg.md` y los dos `resultados.md`, intactos
  salvo la nota de conteo de Q3, que no toca ninguna métrica.
- **`CLAUDE.md`, agentes y skills**: sin cambios. Ninguna regla dura se movió.
- **Nada de GPU.** Sin `sbatch`; los dos jobs del nodo (4800 `gvenegas`, 4820 `dbustama`) son
  ajenos y no leen este árbol.
- **La lámina 15 se ensayó y no se le encontró ningún defecto de contenido.** Sí dos notas de
  **habla**, que van al handoff y no son ediciones: la bisagra «de encaje y no de calidad» está en
  una subordinada y se pierde al hablar rápido, y hay **dos series de ordinales en 90 segundos**
  («la primera/segunda/tercera/cuarta» familia contra «el primero/segundo/tercero» paper) que no
  se corresponden entre sí. Lo segundo es consecuencia de haber sacado las letras A/B/C/D, que fue
  una decisión correcta; se resuelve nombrando los papers por contenido al decirlos.

## Lo que queda abierto y va al handoff

- **Q1 sin aplicar**: la reescritura de la nota de la lámina 9, con la redacción ya propuesta.
- Los pendientes del sprint siguen abiertos sin cambios: las dos preguntas de la reunión, la
  réplica del dato abierto del 4589 con semillas nuevas, el sign-off del patólogo y `@grilling`
  sin estrenar.

---

# Decimoctava pasada — la reunión ocurrió y el deck se reordena entero (6-ago-2026, jueves, noche)

> Sesión **post-reunión**. Sebastián dio feedback sobre la medición de atención, pidió un orden
> nuevo para la presentación, y la de Benjamín del viernes 7 **se cayó** (Ernesto tiene clases):
> el deck se presenta a Benjamín la **semana del 11-ago**, sin día confirmado. La sesión alcanzó a
> hacer la parte de **contenido** (los dos hallazgos de abajo) y a arrancar la reestructuración del
> generador; el reordenamiento de `build()` quedó **a medio camino** y va entero al handoff.

| id | Hallazgo | Tipo | Severidad | Acción |
|---|---|---|---|---|
| R1 | **La lámina «La pregunta medible» dice que se mira dónde caen «los 163 marcados» y acto seguido muestra 0,89, que es el número de los 28 de mitosis.** Los 163 son los siete grupos juntos y no tienen AUC en ninguna tabla | error de contenido | **alta** | Corregir la línea: el estadístico se calcula **por grupo**, y la cinta ilustra el de mitosis. **Sin aplicar** |
| R2 | **El +2 de 26 → 28 no es un +2 simple: son +10 y −8 que casi se cancelan.** La décima y la decimoséptima pasada dieron la regla de conteo correcta, pero el mecanismo quedó sin calcular y el neto invita a leerlo como un solo efecto | verificación | media | Calculado y registrado en `atencion_vs_patologo/resultados.md` §1.a |
| R3 | **Los siete grupos comparten estadístico pero no precisión**, y la escalera los dibuja con barras del mismo grosor. Con n de 12 a 48, el IC 95 % va de 0,10 a 0,33 de ancho | omisión | media | §1.b nuevo en `resultados.md` con los IC de Hanley-McNeil; bigote agregado a `barras_ranking` |

## R1 — «los 163 marcados» y el 0,89 no son el mismo conjunto

La lámina encadena tres frases: se ordenan los 4799 parches, se mira dónde caen **los 163
marcados**, y el resultado es **0,89**. Las tres son ciertas por separado y juntas dicen algo
falso: los 163 son la unión de los siete grupos (tumor, grasa, linfocitos incluidos), y ese
conjunto **no tiene AUC calculado en ningún artefacto** — mezclaría grupos que van de 0,15 a 0,89.
El 0,89 es de los **28 de mitosis**.

Es el mismo tipo de defecto que la decimoséptima pasada catalogó en Q1: cada frase pasa la
auditoría por separado y el problema está en el eslabón. Acá encima lo agrava que el número 163
aparece también en la lámina siguiente, en el pie de procedencia, donde **sí** corresponde.

**Corrección**: la línea pasa a decir que se mira dónde cayeron los parches **del grupo**, y que la
cinta de abajo es la de mitosis. Queda **sin aplicar** en esta sesión.

## R2 — el mecanismo del 26 → 28

Ver `atencion_vs_patologo/resultados.md` §1.a, que trae la tabla entera. Lo que importa acá como
hallazgo de auditoría es que **el documento invitaba a la lectura equivocada**: decía que la
descomposición «no se calculó y no hace falta», y el neto de +2 se lee naturalmente como «dos
marcas cruzaron un borde». Son **diez** las que cruzan; lo que las tapa son **siete parches con más
de una mitosis adentro**, que restan ocho. Que el neto sea +2 es una coincidencia de esta lámina.

Consecuencia de método, y por eso es hallazgo y no una nota al pie: **el neto no es portable**. Si
la medición se lleva a otras láminas (que es el objetivo propuesto 1), el neto va a ser distinto y
mucho mayor, porque depende de la dispersión de las marcas. Lo portable es la regla de mapeo.

## R3 — siete barras del mismo grosor sugieren siete números de la misma calidad

La escalera de los siete grupos dibuja siete barras idénticas en forma. Con n de 12 a 48, la
precisión no es comparable: el IC 95 % de estroma mide 0,33 de ancho y el de tejido adiposo 0,10.
El caso que más importa es **estroma**: se venía contando como «queda justo en el azar, que es
donde uno esperaría algo que no es informativo ni estorba», y con su IC de 0,37 a 0,70 la lámina
**no puede distinguir** estroma evitado de estroma atendido. Eso es una ausencia de dato contada
como si fuera un dato.

`barras_ranking` ya dibuja el bigote (`ESCALERA` pasó a 5-tuplas con el semiancho); falta la
lámina que lo explique y el guion que lo diga.

## Verificado sin cambios

- **La regla de conteo de la decimoséptima pasada (Q3) es correcta** y se reprodujo desde otra
  fuente: la décima y la decimoséptima la sacaron del CSV de parches anotados; esta la recalculó
  desde el **geojson y las coords del h5**, que es el insumo de más arriba, y da lo mismo.
- **El generador corre limpio en el estado intermedio**: 16 láminas, auditoría en cero avisos.
  Las ediciones aplicadas (constantes, `barras_ranking`, `cadena_cuenta`, fecha) son coherentes
  entre sí; lo que falta es el reordenamiento, que no rompe nada por no estar.

## Lo que queda abierto y va al handoff

- **Todo el pedido de Ernesto sobre el deck**, que es lo grande: reordenar, eliminar dos láminas,
  retitular una, arreglar el molde de la de cierre, reforzar cuatro con la estadística, reescribir
  el guion, regenerar y sacar la copia sin notas.
- **R1 sin aplicar.**
- **Q1 de la pasada anterior sigue sin aplicar** (la nota de la lámina 9). Con el reordenamiento
  esa lámina cambia de número, así que conviene aplicarla en la misma pasada.
- Los pendientes de sprint sin cambios: la réplica del dato abierto del 4589 con semillas nuevas,
  el sign-off del patólogo y `@grilling` sin estrenar.

---

# Decimonovena pasada — el reordenamiento ejecutado, y dos líneas cruzando un texto (7-ago-2026, viernes)

> Sesión de **construcción**: los seis pedidos de deck del 6-ago más los dos entregables.
> Todo el material de contenido ya estaba escrito y verificado por la pasada anterior. **Ningún
> número cambió**, y ni el `prereg.md` ni el `resultados.md` de los dos experimentos se tocaron.
> El deck queda en **14 láminas**, auditoría del generador en cero.

| id | Hallazgo | Tipo | Severidad | Acción |
|---|---|---|---|---|
| S1 | **Los dos rótulos rotados de las cintas de «La pregunta medible» se pisaban entre sí**, y era preexistente: un shape rotado 270° ocupa a lo alto lo que mide de ancho (1,60") y las dos cintas están a 0,56" | defecto de lámina | media | Rótulos horizontales en la calle izquierda, cintas corridas a `x = 1,24`. **Corregido** |
| S2 | **La línea punteada del azar cruzaba el rótulo «0,322» de Linfocitos** en la escalera de los siete grupos | defecto de lámina | media | El valor pasa a **columna fija** al final del eje en `barras_ranking`. **Corregido** |
| S3 | **R1 aplicado** (decimoctava pasada): la lámina decía «los 163 marcados» y mostraba 0,89 | error de contenido | alta | La línea nombra el grupo y la lámina dice que cada grupo tiene su propio estadístico. **Corregido** |
| S4 | **Q1 aplicado** (decimoséptima pasada): la nota de los mapas no decía contra qué compite un parche marcado | omisión de guion | media | Entró la oración: compite contra todos los demás de la lámina, incluidos los 2303 de la otra región. **Corregido** |
| S5 | **Cinco defectos de arco** que salieron de leer el guion de corrido con el orden nuevo | guion | media | Los cinco corregidos, detalle abajo |

## S1 y S2 — dos líneas cruzando un texto, con la auditoría en cero

Las dos son de la clase que la undécima y la decimoquinta pasada ya habían catalogado
([[deck-qa-puntos-ciegos-chequeo]]): **los dos objetos son válidos, cada uno está dentro de su
caja, y el cruce es invisible para cualquier chequeo de límites**. Las dos salieron del
rasterizado con LibreOffice.

**S1 agrega un mecanismo nuevo y vale registrarlo**: `_rot_label` rota 270°, y **el bbox que
reporta el shape es el de antes de rotar**. Eso ya estaba anotado como «falso positivo en
chequeos de límites» (ADDENDUM del 19-jul de [[deck-contenido-visual-no-bullets]]); lo que
faltaba decir es que también produce **falsos negativos**: dos rótulos que el chequeo ve
separados por 0,56" en realidad se solapan en 1,04". El defecto era **preexistente** y el
reordenamiento vertical de la lámina solo lo hizo más visible.

**S2 es de la familia «offsets que dejan de servir al cambiar los datos»**, prima del hallazgo
de la decimoquinta pasada sobre `barras_divergentes`. `barras_ranking` ponía el valor a
`xb + 0,08`, o sea pegado a la punta del bigote. Para los grupos **bajo el azar** esa punta cae
antes de la línea punteada del 0,5, así que el rótulo aterriza justo encima de ella. No es un
error de la lámina de hoy: es una regla de posicionamiento que solo funciona para valores
altos, y los tres grupos bajos son datos legítimos de la tabla.

## S5 — lo que solo se oye leyendo de corrido

Cinco, y **cuatro de los cinco son consecuencia directa del reorden**, no de la prosa nueva:

- **Dos «paso a» seguidos** en el cambio de la lámina 3 a la 4. Cada nota, leída sola, está bien.
- «Empiezo por acá porque es **lo único que llega cerrado**» **contradecía la portada**, que
  presenta SI-MIL como lectura terminada. La frase era correcta cuando el grid era la sección de
  cierre y falsa cuando pasó a abrir.
- El **26 contra 28** se oía como contradicción desde la lámina 5 y no se resolvía hasta la 7.
  La R1 lo empeoró sin querer: al corregir «163» por «28» en la lámina 4, el 28 aparece **antes**
  que el 26. Se resuelve con media oración de adelanto en la 5.
- **Tres preguntas «para hoy» apiladas al final**, porque SI-MIL pasó al cierre y trae dos.
  Las dos de SI-MIL pasan a «las dejo planteadas» y la de cierre queda como la única que bloquea.
- «Tomar un detector de mitosis **público**» chocaba, dos párrafos después, con «uno trae pesos
  **públicos** pero no distingue mitosis». Esa sí es de la prosa nueva.

**Lo transversal**: fusionar láminas vuelve vecinos a dos vocabularios (quinta y decimoquinta
pasada); **reordenarlas rompe las referencias cruzadas**, que es otra cosa y no la caza ninguna
cuenta. Dos frases de la lámina 11 prometían algo «en la segunda parte» apuntando a una medición
que, con el orden nuevo, ya ocurrió.

## Verificado sin cambios

- **El «0,89 vs 0,890» y el «26 vs 28» no se reabrieron.** El primero sigue siendo decisión de
  estilo (la cinta ilustra, la banda mide) y el segundo ahora tiene su cadena dibujada en la
  lámina 7, que es lo que la decimoctava pasada dejó preparado.
- **Los rótulos de hipótesis siguen sin reasignarse por cuál ganó**: la primaria es la del
  patólogo, o sea la que el resultado refutó. Al bajarlas de su renglón propio al bloque de
  método se conservó el texto del pre-registro §2.
- **Barrido de reglas duras sobre el `.pptx` construido**, cuerpo y notas: cero rayas, cero
  «palanca», cero decimales con punto, cero «al revés». Había un «al revés» **preexistente** en
  la nota del grid, corregido.
- **La copia sin notas** deja 82 partes del paquete **byte-idénticas**, o sea que fuentes
  embebidas, imágenes y theme no se tocaron.

## Lo que queda abierto y va al handoff

- **Los dos papers de `papers_11_agosto/` siguen sin leer ni fichar.**
- **El envío a Sebastián** de ZoomMIL y el de positivos parciales: falta verificar si los PDF
  están en el repo o hay que bajarlos (y bajar exige autorización explícita, workaround E.a).
- **Tres decisiones de Ernesto sobre el deck**: la lámina de cierre queda muy vacía con el molde
  exacto, las dos figuras de mitosis cedieron un 20 % de alto, y la leyenda mezclada
  español/inglés sigue como está por decisión suya.
- Las **dos preguntas de la reunión del 6-ago** siguen sin respuesta conocida, y de la segunda
  dependen los dos objetivos propuestos.
- Los pendientes de sprint sin cambios: la réplica del dato abierto del 4589 con semillas nuevas,
  el sign-off del patólogo y `@grilling` sin estrenar.

---

# Vigésima pasada — el reconocimiento del encargo nuevo, y un directorio que el repo no conocía (17-ago-2026, lunes)

> Sesión de **planificación**: la reunión del 14-ago ya ocurrió, Sebastián dejó cuatro encargos y
> esta sesión los tradujo a un plan. **Ningún experimento corrió y ningún número se movió.** Lo que
> cambió es el mapa: el reconocimiento del servidor encontró material que ninguno de los documentos
> del sprint sabía que existía, y contestó una pregunta que llevaba abierta desde el 31-jul en ocho
> lugares distintos.

| id | Hallazgo | Tipo | Severidad | Acción |
|---|---|---|---|---|
| T1 | **El directorio `/media/administrador/Storage1/sdonoso/anotaciones/` no aparece en ningún documento del repo**, y contiene **12** geojson del patólogo más un pipeline de atención-vs-anotaciones de `sgaete` sobre 8 tareas | omisión | alta | Entra a la tabla de paths de `CLAUDE.md` como **READ-ONLY**; memoria actualizada |
| T2 | **«¿Hay más láminas anotadas?» está contestada** y seguía abierta en 8 documentos | stale | alta | ADDENDUM fechado en la memoria canónica y en `hovernext_estudio.md` §11. Los sprint docs históricos **no** se reescriben |
| T3 | **Sebastián dijo 30 láminas; en el servidor hay 12** | discrepancia | alta | Se registra como discrepancia, **no** como error de Sebastián. Faltan 18 → pregunta para él |
| T4 | La memoria `anotaciones-patologo-qupath` explica cómo elegir checkpoint **solo para tasa mitótica**, y omite el único mapeo que da par CLAM/Mammoth con la lámina no vista | omisión | alta | Punto nuevo en la memoria |
| T5 | Los documentos dicen que **no hay autorización** para bajar HoVer-NeXt; Ernesto la dio hoy | stale | media | ADDENDUM + memoria + tabla de paths |
| T6 | `objetivos_sprint8.md` dice «hay **una** lámina, un anotador y 26 marcas», y dio de baja HoVer-Net **por costo** conservando la idea del top-20 | stale ×2 | alta | Las dos premisas cayeron. Se actualiza el mapa del sprint |
| T7 | **PQ / bPQ / mPQ no son computables** contra el geojson del patólogo, y son justo las métricas que el encargo pide «como las del paper» | riesgo de fabricación | alta | Guardrail explícito en el plan y en memoria nueva |

## T1 — un directorio con doce láminas que nadie había mirado

`grep -rn "sdonoso/anotaciones"` sobre el repo entero devuelve **cero**. El material vivía a un
nivel del árbol que ninguna sesión había recorrido, y lo que hay dentro es sustancial:

- **12 archivos `<slide>.bif - GDT.geojson`**, no uno. Las 12 tienen features `.h5` y WSI
  disponibles, y **las 12 traen marcas de `Mitosis`**: 94 en total contra las 26 de la 129741.
  La 126504 aporta 20 y la 128194 diecisiete, o sea que hay dos láminas del mismo orden que la
  única que veníamos usando.
- Un vocabulario de clases **más ancho** que el de la 129741: aparecen `AreaTubular`, `AreaSolida`,
  `CDIS_solido`, `CDIS_papilar`, `Comedonecrosis`, `Permeaciones vasculares`, `NucleosBajoGrado`,
  `Nucleos mod grado`, `Mucinoso`, `microcalcificaciones`. La 129741 usa un subconjunto.
- **Un pipeline propio de `sgaete`**: `atencion/` con 8 tareas y `resumen_atencion.csv` de 109
  filas, `overlays/` con `resumen_anotaciones.csv` de 363, más `atencion_vs_anotaciones.py` y su
  `.slurm` (jobs 4838/4839, 7-ago). **Mide lo mismo que nuestro `atencion_vs_patologo/`**, con otro
  código y sobre las 12 láminas.

Lo tercero es lo que más importa operativamente y va al handoff: **hay riesgo real de trabajo
duplicado con Sebastián/sgaete**, y la fase 5 del plan (extender a las 11 restantes) es exactamente
el terreno donde chocaría. Se coordina antes de correr, no después. El directorio es de `sgaete` →
**READ-ONLY**, misma lógica que `hover_net/` y `clam_testing/`.

## T2 y T3 — la pregunta contestada, y la que se abre en su lugar

«¿Hay más láminas anotadas, y quién es GDT?» aparece viva en `reunion_31jul_redireccion.md`,
`hovernet_estudio.md` (×2), `papers_b8.md`, `hovernext_estudio.md` §11, `tareas_geometricas/`
(×2), `hojas_reunion.md` y `anotaciones_patologo/hallazgos.md`. **La primera mitad quedó
contestada hoy: sí, hay doce.** La segunda **sigue abierta** — el nombre detrás de «GDT» no se
resolvió y no lo resuelve mirar archivos.

Criterio aplicado: se corrige la **memoria canónica** y el documento que la lleva como pendiente
vivo (`hovernext_estudio.md` §11). Los demás son **registro histórico de lo que se sabía ese día**
y no se reescriben; quien los lea llega a la memoria por el `[[wikilink]]`.

**T3 no se resuelve mirando el disco.** Sebastián dijo 30 y hay 12. Las lecturas posibles son que
las otras 18 no estén subidas, que vivan en otra cuenta, o que 30 sea el total anotado y 12 el
total compartido. **Ninguna se puede elegir desde acá**, así que se registra la discrepancia y se
pregunta. Lo que **no** se hace es asumir que Sebastián se equivocó.

## T4 — el checkpoint que sí sirve estaba a un grep de distancia

La memoria dice, en su punto 6, que para medir atención sobre estas marcas hay que elegir bien el
checkpoint, y desarrolla el caso de **tasa mitótica**: la 129741 cae en `val` en los splits de
Sebastián y en `train` **en los cinco folds** del k-fold nuestro. Correcto y sigue vigente.

Lo que faltaba: en `data/splits_kfold/carcinoma_ductal_insitu_presente_ci_reform_100` la 129741
cae en **test del fold 4** y en **val del fold 2**. Eso importa porque es el **único** caso del
proyecto donde existe un **par CLAM/Mammoth entrenado paired** (job 4589) sobre una lámina que el
modelo **no vio** — y por lo tanto el único camino para el encargo 2 sin gastar GPU. En tasa
mitótica ese par no existe y no puede construirse sin splits nuevos.

## T6 — dos premisas del mapa del sprint que la semana pasada dio vuelta

**La primera es de tamaño.** «Todavía sin especificar» dice: *«Hay una lámina, un anotador y 26
marcas de mitosis»*. Son **doce, 94 marcas**, y el anotador sigue siendo uno. La pregunta que ese
párrafo dejaba en niebla — si el material alcanza para entrenar — no queda contestada, pero **sí
cambia de orden de magnitud**, que es justo lo que la sección pide para graduar algo a sharp.

**La segunda es de encuadre, y es la que hay que tratar con cuidado.** «Fuera de alcance» dice que
HoVer-Net queda en pausa **por costo**, conservando la idea de correrlo sobre los 20 mejores
parches de CLAM. Las dos mitades cayeron por motivos distintos:

- **El costo** dejó de ser argumento: ~2 min por lámina contra 3 h 36 medidas.
- **El top-20** dejó de ser el diseño: no le da el denominador (patrón **P2**,
  [[topk-percentil-no-auc]]). Con AUC de atención 0,890 contiene 3 de 28 parches con mitosis.

Y sobre todo: **la reunión del 14-ago redibujó el destino**, que es literalmente la única condición
bajo la cual el formato del mapa permite que algo vuelva de «Fuera de alcance», y vuelve **como
esfuerzo nuevo**. No es una reapertura por inercia ni un caso de regla 9.b encubierto: es el
supervisor cambiando el objetivo. Se documenta así, con esa cadena, para que ninguna sesión futura
lo lea como que nos saltamos la regla.

## T7 — la métrica que el encargo pide y el dato no soporta

Sebastián pidió evaluar «con las métricas del paper», y el paper reporta PQ, bPQ y mPQ. **Contra
este geojson no se pueden calcular**, y conviene dejarlo escrito antes de que alguien los produzca:

- PQ = DQ × SQ. **SQ es IoU medio sobre pares emparejados**, y exige contornos nucleares. Las
  marcas de mitosis son **cuadrados de ~36 px**, no contornos.
- **DQ es F1**, y su mitad de precisión no es honesta acá: los positivos son **parciales**, así que
  toda mitosis real no marcada cuenta como falso positivo del modelo.

Lo que **sí** sobrevive de esa familia es el **recall de detección** y los **descriptores de
regularidad** por instancia. Y la regularidad no es un premio de consuelo: HoVer-NeXt sacó el
convex hull para ganar velocidad y **lo pagó en distancia de Hausdorff**, así que la solidez es
justo el eje donde se ve el trueque que el paper hizo.

## Verificado sin cambios

- **Los números del `atencion_vs_patologo/` no se tocaron**: el AUC 0,890 de mitosis, los siete
  grupos, los dos nulos y la disociación del §3 siguen como estaban. Esta sesión los **leyó** para
  dimensionar el barrido de K, y no re-midió nada.
- **El mecanismo y el estudio de HoVer-NeXt no se re-auditaron**, como pedía el handoff.
- **El determinismo bit a bit** sigue siendo el argumento por el que la fase 6 exige semillas
  nuevas para cualquier réplica.
- La lámina 129741 verificada de nuevo contra openslide: 39669 × 80640, 0,465 µm/px, 4799 parches,
  **dos regiones de escaneo** y las 163 anotaciones todas en la de abajo.

## Lo que queda abierto y va al handoff

- **Las 18 láminas que faltan** para las 30 que mencionó Sebastián, y **quién es «GDT»**.
- **Coordinar con Sebastián/sgaete** antes de la fase 5, por el pipeline paralelo de `anotaciones/`.
- Los cuatro encargos, sin ejecutar: nada se corrió esta sesión.
- Pendientes de sprint sin cambios: la réplica del 4589 con semillas nuevas, el sign-off del
  patólogo, `@grilling` sin estrenar, los dos papers de `papers_11_agosto/` sin fichar y las dos
  preguntas de la reunión del 6-ago.

---

# Vigésima primera pasada — el job que no esperaba turno, y la prueba que se acotó sin correrla (17-ago-2026, tarde)

Sesión que arrancó para **cosechar** dos procesos y no pudo cosechar ninguno: los dos seguían en
vuelo. Mirar *por qué* el primero no arrancaba destapó un hallazgo operativo que ninguna sesión
había visto, y la espera forzó un segundo hallazgo que resultó más valioso que la cosecha.

| id | hallazgo | severidad | acción |
|---|---|---|---|
| **U1** | Un `PD (Priority)` puede **no** ser una espera normal: con `TimeLimit=UNLIMITED` delante, el backfill no puede planificar y **achicar el job no adelanta nada** | **alta** — cambia qué se hace ante un job encolado | **workaround L** en CLAUDE.md + memoria |
| **U2** | La mitad de una prueba restringida se puede **acotar por arriba sin correr la etapa cara** | **alta** — es método, no dato | **sub-cláusula P2.a** + memoria |
| **U3** | `--export` de SLURM separa por comas y choca con cualquier arg que **espere** comas | media | dentro del workaround L |

## U1 — `squeue` decía «Priority» y `scontrol` decía otra cosa

`squeue` mostraba `4998 PD (Priority)`, que se lee como «hay gente delante, ya te toca».
`scontrol show job` mostró `StartTime = 2027-08-17`, o sea **un año**. La causa no es la carga:

- el nodo tiene **un solo token de GPU** (`Gres=gpu:1`), y lo tenía un job declarado a **365 días**;
- delante nuestro había **dos jobs `TimeLimit = UNLIMITED`**, los dos pidiendo ese mismo token.

**Lo que importa y no era obvio:** para colar un job chico antes que uno grande, el backfill
necesita **saber cuándo terminan** los de más prioridad. Con `UNLIMITED` delante esa ventana no se
puede calcular, así que **no hay backfill posible** y bajar `--mem`/`--cpus` **no nos adelanta**.
Eso invierte la reacción instintiva ante un job encolado, que es achicarlo.

El `StartTime` de un año **no es una predicción**: es lo que SLURM devuelve cuando no puede
planificar. Confundirlo con una espera real sería igual de equivocado que confundirlo con una
espera corta.

Queda `hovernext_129741/coordinacion_gpu.md` con el snapshot y el pedido, y la decisión de Ernesto
fue **coordinar y dejarlo encolado** — porque el resto de las opciones eran técnicas y ninguna
saltaba la cola.

## U2 — la fase 3 se acotó por arriba sin correr HoVer-NeXt

El razonamiento, que es reusable y no tiene nada de específico de esta prueba: **un candidato que
no entra en la máscara no lo recupera nadie**, por bueno que sea el detector. Entonces el filtro
**solo** ya acota por arriba el resultado del pipeline restringido:

```
recall(K)  ≤  min( techo_del_filtro(K) ,  poder_del_detector )
```

y el primer factor **no depende de la etapa cara**. Medido: el techo **no condena** la fase 3
(a 12 % de la región anotada ya son 19/28 en CLAM y 22/28 en Mammoth, 5,7× y 6,5× sobre el azar),
y de paso el **chequeo de sanidad que el plan exige** para la fase 3 quedó aprobado a nivel de
techo (en K = 2496 los dos brazos dan idéntico).

Es la continuación natural de **P2**: si P2 dice «declará el denominador alcanzable antes de correr
la prueba», U2 dice **cómo medirlo cuando el denominador depende de dos etapas y solo una es cara**.
Por eso va como sub-cláusula P2.a y no como patrón nuevo.

Corrobora además [[topk-percentil-no-auc]] de forma **independiente**: el top-20 vuelve a dar 2-3
de 28 con un par de checkpoints de **otra tarea** que los 12 que dieron el número original.

## U3 — dos convenciones de coma que se pisan

`sbatch --export=ALL,VAR=valor` separa variables **por coma**; `--cp` de HoVer-NeXt espera una
**lista separada por comas** para promediar el ensemble de PanNuke. Pasar el ensemble por `--export`
lo parte en variables basura y el brazo queda mudo, sin error claro. Se pasa con `+` y el `.slurm`
traduce; es idempotente para un checkpoint solo.

Es un caso particular de algo más general y por eso vale registrarlo: **`--export` es hostil a
cualquier valor con comas**, no solo a este.

## Verificado sin cambios

- **La fase 1 se reprodujo byte a byte.** Agregar `--dump-attention` a
  `clam_vs_mammoth_attention.py` no movió ninguno de sus 4 artefactos (md5 idéntico en los 3 PNG y
  el JSON) — el cambio es aditivo de verdad, no «aditivo de palabra».
- **El Hallazgo 12 no se movió.** Que Mammoth ordene mejor los parches es interpretabilidad, no
  métrica de lámina, y los dos brazos siguen clasificando mal esta lámina.
- **No se re-midió** el AUC 0,890 ni los percentiles, como viene mandando el plan.

## Lo que queda abierto y va al handoff

- **Todo HoVer-NeXt**: el 4998 nunca arrancó, así que fases 2.a/2.b/2.c enteras y de la 3 solo el
  techo (falta el brazo 1, el único que exige GPU).
- **El barrido sin terminar** y la decisión sobre los parámetros del test de registro.
- Los pendientes de sprint de siempre, sin tocar: réplica del 4589 con semillas nuevas, las 18
  láminas, el sign-off del patólogo, `@grilling` sin estrenar.

---

# Vigésima segunda pasada — el instrumento que destruye su propia referencia (18-ago-2026)

Pasada de cierre de la 7ª sesión del B8. La sesión no produjo resultados (el re-barrido con
rotación seguía corriendo, ~6 % al cerrar): produjo **el instrumento del recuento de §8.b**, y
ejercitarlo sobre el parcial destapó tres cosas que no estaban en ningún frente.

| id | hallazgo | tipo | severidad | acción |
|---|---|---|---|---|
| **V1** | El cosechador escribía a un nombre FIJO y pisaba la verdad de campo del barrido anterior | error de diseño | **alta** | fix en código + memoria nueva |
| **V2** | `control_medio ≤ 0` manda la razón señal/control a 1e8 y falsearía el perfil | gotcha nuevo | **alta** | guard en el script + memoria nueva |
| **V3** | El criterio de «seriadas» puede ser **fabricado** por una etapa B que no da abasto | patrón nuevo | **alta** | patrón P4 en `CLAUDE.md` + memoria |
| **V4** | «19 rechazadas» es incorrecto en 2 frentes; son **21**, cobertura 129 | error | media | corregido en los 3 lugares |
| **V5** | La memoria y su línea de índice citan §8 sin la marca de PROVISIONAL | stale | media | ADDENDUM 4ª parte + índice |

## V1 — un agregador que escribe a un nombre fijo destruye su propia referencia

`scripts/cosechar_barrido_registro.py` tomaba el directorio de entrada por argumento pero escribía
**siempre** en `D.parent / "barrido_resumen.csv"`. Como los dos barridos son hermanos dentro de
`regiones_escaneo/`, cosechar `barrido_rot/` habría sobrescrito el resumen de `barrido_138/`, que
es **la verdad de campo de §8 y la referencia de la comparación pareada**.

El handoff ya lo había marcado como riesgo («verificar antes de correrlo, NO sobrescribir»), es
decir estaba delegado en que el operador se acordara. **No alcanzó: en la prueba de esta sesión lo
sobrescribí igual**, pasándole a mano la ruta que estaba tratando de proteger. Se restauró desde
git (`git checkout --`) y se verificó idéntico contra una copia de regresión, sin pérdida.

**Canónico**: el destino se deriva del nombre del directorio (`barrido_resumen_<dir>.csv`) y
`barrido_resumen.csv` está protegido **incluso contra un destino explícito** (`--force` para
pisarlo). Regresión verificada: sobre `barrido_138` reproduce el CSV congelado celda a celda.
→ memoria nueva `agregador-nombre-fijo-pisa-referencia`.

## V2 — un control negativo manda la razón a 1e8 y falsea el perfil

`razon_senal_control = ncc_medio / max(control_medio, 1e-9)`. Con `control_medio` **negativo** el
`max` clava el denominador en `1e-9` y la razón se va a **1e8**.

- En `barrido_138` le pasa a **1 de 108** (`130981-2`, control −0,0297, razón 1,8e8).
- **Hoy es inocuo** y por eso ningún número de §8 cambia: no pasa la puerta del eje 1, así que
  nunca entró al reparto, y §8.b reporta medianas, robustas a un outlier.
- **La trampa es prospectiva**: si la rotación recupera una lámina así, su razón supera *cualquier*
  corte y el clasificador la manda a «perfil de re-escaneo» por el **signo del denominador**. El
  parcial del re-barrido ya trae otra en esa condición (`120361`, control −0,0227).

**Canónico**: `resultados.md` §11.a + guard en `comparar_barridos_rotacion.py` (las lista aparte,
las excluye de los estadísticos de razón, avisa si alguna pasa la puerta).
→ memoria nueva `razon-denominador-degenerado`.

## V3 — un criterio residual puede fabricar su propia categoría

«Perfil de secciones seriadas» se define por `razón < 2,0` **y** ajuste no rígido
(`|escala − 1| > 0,02`). Las láminas que la rotación recupera son, por construcción, **las que más
girada tienen la segunda región** (§10.b: |θ*| mediano 7,8°), y **la etapa B barre solo ±8° y no
busca escala**. Una lámina cuya etapa A recién ahora localiza pero cuya etapa B no puede ajustar el
residuo tendrá **las dos** propiedades a la vez ⇒ cae en «seriadas» **por incapacidad del
instrumento, no por hallazgo**.

No es conjetura sobre los datos: es lectura del criterio. Las dos condiciones que definen la
categoría son exactamente las dos que produce el instrumento cuando no da abasto. El único caso
disponible la ilustra (la 128696 cruza la puerta y aterriza en «seriadas» con escala 1,0492 y razón
1,77) pero **es n=1 y no se lee como evidencia**; el mecanismo se sostiene solo.

Es hermano de P2 (un top-k se dimensiona por percentil, no por AUC) y P3 (el control positivo
calibra el criterio): los tres son formas de que **el instrumento se cuele en la conclusión**.
**Canónico**: patrón **P4** en `CLAUDE.md` + `resultados.md` §11.b.
→ memoria nueva `categoria-residual-fabricada-por-el-instrumento`.

## V4 — «19 rechazadas» era el contador del driver, no el disco

`resultados.md` §8 y `progress/current.md:3531` declaraban **19** láminas rechazadas. En disco hay
**21** `.stop`, todas del 17-ago entre 16:48 y 19:55. El 19 sale del contador del driver, que cerró
en «108 ok / 19 stop / 0 fallo / **2 pendientes**»: las 2 láminas restantes ya tenían `.stop` de una
corrida previa, el driver las contó como `saltadas: 3` y por eso nunca incrementaron el contador.

**Ninguna quedó sin correr**: 108 + 21 = **129**, exactamente la lista del driver. **Las 108
medidas y todo lo que cuelga de ellas no se mueven**; cambia el denominador de cobertura, la tasa
de rechazo (15 % → **16 %**) y el «2 pendientes», que no eran pendientes.

Corregido en `resultados.md` §8 (con nota fechada), `progress/current.md` y la memoria.

## V5 — la memoria citaba §8 sin la marca de provisional en su cabecera

El ADDENDUM 3ª parte de `regiones-escaneo-bif-cohorte-privada` **sí** dice que el 33/54 quedó
provisional, pero el ADDENDUM 2ª parte (más arriba, el que un lector encuentra primero) lo presenta
como veredicto, y la **línea del índice** en `MEMORY.md` lo repetía sin salvedad. Con la reunión de
mañana esto es material: es la cifra que se citaría de memoria.

Fix aditivo: ADDENDUM 4ª parte con el estado real + línea de índice actualizada. **No se reescribe**
ningún ADDENDUM anterior (integridad de pre-registración).

## Verificado sin cambios

- `CLAUDE.md` workarounds A-M: ninguno contradicho por esta sesión.
- Patrones P1-P3: vigentes; P4 se agrega, no los toca.
- Agentes (`trainer`, `reviewer`) y skills: sin contacto con lo de esta sesión.
- El resto de `resultados.md` (§1-§10): sin cambios salvo la nota de §8.

## Lo que queda abierto y va al handoff

- **El recuento de §8.b sin rehacer**: el re-barrido termina ~21:45 del 18-ago.
- **Si la etapa B es el próximo cuello** (V3): se contesta al cosechar, no antes.
- **El veredicto de la 129741** sigue abierto; la lámina está en el barrido en curso.
- **HoVer-NeXt sin un solo número**: el 5008 sigue `PD` detrás de un `UNLIMITED`.

---

# Vigésima tercera pasada — una frase falsa que sobrevivió a su propia corrección (19-ago-2026, tarde)

Sesión de deck: entró la lámina del cruce y se corrigieron las frases que daban el cruce por
pendiente. La auditoría de la sesión anterior (19-ago, mañana) no dejó pasada propia; sus
hallazgos están en `progress/current.md` §Sesión 13 y en el ADDENDUM 19-ago de
[[deck-qa-puntos-ciegos-chequeo]], así que esta pasada arranca desde ahí.

| id | hallazgo | severidad | acción |
|---|---|---|---|
| W1 | «ahorró una corrida entera» se corrigió en la lámina donde se cazó y siguió vivo en el **mapa del bloque** | alta | ADDENDUM a [[deck-qa-puntos-ciegos-chequeo]] |
| W2 | `techo_atencion.md` sigue pidiendo medir lo que ya se midió, sin puntero de ida | media | nota fechada + puntero |
| W3 | `corrida_5008.md` §4 es una lista de trabajo ya consumida y sin marcar | media | nota de cierre fechada |

## W1 — corregir la lámina donde se cazó la frase NO cierra el defecto

El ADDENDUM 19-ago de [[deck-qa-puntos-ciegos-chequeo]] registró, como hallazgo 1 de la cuarta
capa, que el remate de una lámina afirmaba que un patrón **«ahorró la corrida entera»** y que no
la ahorró: el techo dio alto y la corrida se hizo igual. Se corrigió esa lámina.

**La misma afirmación siguió viva, palabra por palabra, en la lámina 15**, que es el **mapa del
bloque**: «Uno de ellos ahorró una corrida entera». Apareció al barrer el generador entero
buscando otra cosa, no por un chequeo.

**Por qué pasa, y por qué ninguna capa lo ve.** Un deck largo tiene láminas de **mapa** y de
**recapitulación** que repiten en una línea lo que otra lámina desarrolla. Las cuatro capas de QA
miran **una lámina a la vez** (geometría, reglas duras, prosa) o **el arco de corrido**, y la
lectura de corrido llega al mapa **antes** que al desarrollo: cuando uno lee la afirmación
correcta, ya pasó por la versión comprimida y falsa sin material para juzgarla. Y el desarrollo
suele ser el lugar donde el defecto se caza, porque es donde está el detalle.

**Regla que queda: una frase corregida se busca en TODO el generador antes de darla por
corregida** (`grep` del sustantivo y del verbo, no de la frase entera: el mapa la dice más
corta). Vale especialmente para las láminas de mapa, recapitulación y «qué sigue», que son
justamente las que se escriben una vez y no se vuelven a leer.

**Segunda instancia del mismo modo de falla en esta sesión**: el handoff listaba **cuatro** frases
que daban el cruce por pendiente, las cuatro de guion. El barrido encontró **seis**: las dos que
faltaban eran de **cuerpo**, y las dos estaban en la lámina 15. El inventario de una sesión
anterior no sustituye al barrido.

**Canónico**: ADDENDUM en [[deck-qa-puntos-ciegos-chequeo]] +
`presentacion_b8/README.md` §«La sesión del 19-ago (tarde)».

## W2 — `techo_atencion.md` pide medir lo que ya se midió

`techo_atencion.md` §«Tres lecturas» 1 cierra con «lo que **falta medir** es cuánto de ese margen
se come la detección». Se midió el 19-ago: `cruce_marcas.md`, 13 de 26.

El puntero existe **en un solo sentido**: `cruce_marcas.md` cita a `techo_atencion.md` cinco
veces; `techo_atencion.md` no lo menciona nunca. Un lector que entre por el techo (que es el
documento del patrón P2.a, o sea el que más se va a volver a abrir) se lleva la pregunta como
abierta.

**No se reescribe la lectura 1** — era cierta el 17-ago y es el registro de por qué se hizo el
cruce. Fix aditivo: nota fechada en la cabecera con el puntero de ida.

## W3 — una lista de trabajo consumida que no dice que lo está

`corrida_5008.md` §4 («Qué queda stale en el deck del 18-ago») es una tabla de cinco láminas a
corregir. Las cinco se corrigieron entre la sesión 13 y ésta, y su última fila dice «lo que falta
es el brazo de ensemble **y el cruce**», que ya no es cierto.

Es el mismo riesgo que W1 visto desde el otro lado: un documento que enumera pendientes envejece
peor que uno que enumera hechos, porque **se lee como instrucción**. Fix aditivo: nota de cierre
fechada arriba de la tabla, sin tocar la tabla (es el registro del estado del 18-ago).

## Verificado sin cambios

- **Los conteos «26 láminas» del repo NO son stale**: los cuatro (dos en `progress/current.md`,
  dos en el README del deck, dos en la memoria de QA) están dentro de secciones **fechadas** que
  describen el deck de ese día. El conteo vigente (27) vive en la sección nueva del README y en
  la línea de índice del `.pptx`, que sí se actualizó.
- **`CLAUDE.md`**: workarounds A-M y patrones P1-P4 sin contradecir. El **P2.a.bis** que escribió
  la sesión 13 es justamente lo que la lámina nueva dibuja, y la lámina no afirma más que él.
- **Agentes** (`trainer`, `reviewer`): sin contacto — la sesión no tocó modelo ni entrenamiento.
- **Skills**: las 13 con `SKILL.md`. `@humanizer-es` **no se corrió**, y por decisión medida: la
  prosa nueva da sd 10,2 sobre media 19,1 y cero tells, o sea el caso que la propia skill pide no
  sobre-editar.

## Lo que queda abierto y va al handoff

- **El brazo de ensemble de HoVer-NeXt**, sin lanzar. Decisión de Ernesto, sostenida tres veces.
- **La reunión con Sebastián**, sin ocurrir al cierre de esta sesión.
- **Coordinar con `sgaete`** antes de barrer las once láminas anotadas restantes.
- Los dos papers de `papers_11_agosto/` sin fichar, las dos preguntas del 6-ago, la réplica del
  4589 con semillas nuevas, el sign-off del patólogo y `@grilling` sin estrenar.

---

# Vigesimocuarta pasada — 19-ago-2026 (cierre de la sesión 15)

> Disparador: el recorte del deck de 27 a 16 láminas y la lámina de control que Ernesto pidió
> después. Tres hallazgos durables, uno de ellos un patrón operativo nuevo.

| id | hallazgo | severidad | acción |
|---|---|---|---|
| X1 | El brazo de control salió **gratis** porque la etapa cara se corrió **sin filtro** | durable | P2.a.ter en `CLAUDE.md` + ADDENDUM en [[techo-filtro-antes-de-correr]] |
| X2 | Una figura que ilustra un número publicado tiene que **reusar el código** del número | durable | ADDENDUM en [[hallazgo-necesita-forma-presentable]] |
| X3 | Una orden de recorte admitía **dos lecturas** y una borraba lo que la otra pedía conservar | durable | memoria nueva `orden-destructiva-dos-lecturas` |
| X4 | La memoria del deck dice «14 láminas» y va por 16, con dos recortes sin registrar | stale | ADDENDUM compacto + descripción |

## X1 — el brazo de control salió gratis, y no por suerte

**Qué pasó.** Ernesto pidió, después del recorte, «una lámina donde se use puramente HoVer-NeXt
para la misma WSI, sin CLAM». Se pudo **sin correr nada**: la corrida del 19-ago fue sobre la
**lámina entera** y el recorte por atención se aplicó **post-hoc, sobre la salida**.

**Por qué es durable y no anécdota.** P2.a dice cómo medir el techo del filtro sin correr la etapa
cara. Esto es la decisión **anterior**, la que hace posible todo lo demás: cuando la etapa cara se
puede pagar entera, **correrla sin filtro** deja medibles *todos* los tamaños de filtro a la vez y
regala el brazo sin filtro, que es contra el que se lee cualquier resultado restringido. Filtrar
**antes** de correr ahorra cómputo una vez y destruye la comparación para siempre.

En este caso la decisión estaba tomada por otro motivo (el paper corre sobre WSI, no sobre parches
sueltos, [[hovernext-especialista-segunda-etapa]] ADDENDUM del 14-ago noche), así que el regalo fue
lateral. **Eso es justamente lo que hay que convertir en regla**, para que la próxima vez sea
deliberado.

**Lo que la escalera mostró, y no se sabía:**

| Qué se revisa | Parches | Área | Det. | Marcas |
|---|---|---|---|---|
| La lámina entera, sin recorte | 4799 | 68,0 mm² | 177 | 13 de 26 |
| Solo la región anotada | 2496 | 35,4 mm² | 82 | 13 de 26 |
| El 12 % más atendido por CLAM | 300 | 4,3 mm² | 48 | 11 de 26 |

**El recorte no compra marcas, compra área**: factor 16 en superficie por dos marcas. Es la
respuesta a «cuánta superficie ponerle delante al patólogo», que es una pregunta **distinta** de
«cuántas mitosis encontramos» — y cierra el corolario de costo de P2 con un número, no con un
argumento. Las dos primeras filas coinciden **por construcción** (las 26 marcas caen todas en la
región anotada) y se verificó en vez de asumirse: el emparejamiento con las 82 detecciones de esa
región sola da los mismos 13.

**Fix**: sub-cláusula **P2.a.ter** en `CLAUDE.md` (compacta, con puntero) + ADDENDUM en la memoria.

## X2 — la figura que ilustra un número tiene que reusar el código del número

**Qué pasó.** `prep_assets_hovernext.py` no re-implementa el emparejamiento: importa y reusa el
mismo húngaro, la misma tolerancia de 30 µm, el mismo offset del geojson y el mismo corte de región
que `scripts/cruce_hovernext_marcas.py`, que es el que produjo el 13 de 26 publicado.

**Por qué importa.** Una figura de lámina y el número de un `resultados.md` se escriben con semanas
de distancia y por caminos distintos. Si la figura re-implementa la lógica, puede **contradecir al
número sin que nadie lo note**, y en una lámina la figura es lo que la audiencia recuerda. Reusando
el código, la contradicción **no es representable**.

Salió de acá, además, un dato que no existía: en el 12 % recortado caen **48 de las 82**
detecciones de la región. Es una cuenta de **detecciones**, no de marcas, y la lámina lo dice al
lado de la tabla que cuenta marcas — la trampa de unidad que P2.a.bis ya había cazado una vez.

**Fix**: ADDENDUM en [[hallazgo-necesita-forma-presentable]], que es la memoria de «un resultado no
está entregado hasta tener lámina»: esto dice **cómo** hacerla sin que mienta.

## X3 — la orden admitía dos lecturas, y una borraba lo que la otra pedía conservar

**Qué pasó.** `correcciones.txt` ordena eliminar una lista de láminas. Sobre dos de ellas dice otra
cosa: que esperaba los mapas «**junto con los datos de si identifica las mitosis**». Ese dato **es**
una de esas dos láminas. Leer el renglón como «borrar las dos» habría eliminado el único resultado
cuantitativo que la misma frase pide conservar.

**Lo que lo distingue de [[surface-premise-discrepancies]]:** ahí la premisa del prompt choca con lo
que dice el repo. Acá **la instrucción choca consigo misma**, y el repo no tiene nada que aportar.
No se resuelve con evidencia, se resuelve preguntando.

**La regla**: antes de una acción **destructiva** ordenada por el usuario, releer la orden buscando
si alguna parte pide **conservar** algo que otra parte borra. Si aparece, **parar y preguntar antes
de borrar** — después de borrar, la pregunta ya cuesta rehacer trabajo. Y presentar la pregunta con
las opciones concretas y lo que cada una se lleva puesto, no como objeción.

**Fix**: memoria nueva `orden-destructiva-dos-lecturas` (`type: feedback`).

## X4 — la memoria del deck quedó dos recortes atrás

`deck-b8-dos-ejes-simil-mitosis` describe **14 láminas** y su último ADDENDUM es del 7-ago. Faltan
la extensión del 18-ago (a 26-27) y el recorte del 19-ago (a 16). La descripción es lo que decide
la recuperación, así que un conteo stale ahí se paga en cada sesión nueva.

**Fix**: ADDENDUM **compacto** (el detalle vive en `presentacion_b8/README.md`, que es canónico
para el deck) + descripción actualizada.

## Verificado sin cambios

- **Los conteos «27 láminas»** de las pasadas anteriores quedan: viven en secciones **fechadas**
  que describen el deck de ese día. El vigente (16) está en la sección nueva del README, en
  `progress/current.md` y en el docstring del generador.
- **`CLAUDE.md`**: workarounds A-M sin contradecir; la sesión no tocó servidor ni SLURM.
- **Agentes** (`trainer`, `reviewer`): sin contacto — no se tocó modelo ni entrenamiento.
- **Skills**: `@humanizer-es` **no se corrió**, y la prosa nueva se midió antes de decidirlo (cero
  rayas, cero «palanca», cero «al revés» sobre el `.pptx`, no sobre el fuente).
- **Las dos prohibiciones explícitas** de `correcciones.txt` verificadas sobre el `.pptx` extraído:
  cero menciones de la cola de cómputo y cero fechas de lo que se hizo. Las tres coincidencias del
  `grep` eran falsos positivos («la fila» de una tabla) y la fecha de portada, que es otra cosa.

## Lo que queda abierto y va al handoff

- **Estudiar las notas del presentador del deck recortado**, que es la misión de la próxima sesión.
- **La fecha de portada** (`FECHA_REUNION = "19 de agosto de 2026"`) con la reunión sin ocurrir.
- **Los tres PNG de regiones** siguen en `assets/` sin que el deck los use.
- **El brazo de ensemble de HoVer-NeXt**, sin lanzar. Decisión de Ernesto, sostenida cuatro veces.
- Coordinar con `sgaete`, los dos papers de `papers_11_agosto/` sin fichar, las dos preguntas del
  6-ago, la réplica del 4589 con semillas nuevas, el sign-off del patólogo, `@grilling` sin estrenar.
