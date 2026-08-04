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
