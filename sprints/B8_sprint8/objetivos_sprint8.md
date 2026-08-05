# Sprint 8 (B8) — mapa

> **Reestructurado el 5-ago-2026** como índice, adoptando la gramática de secciones de la
> skill *wayfinder* (Destino / Decisiones / Todavía sin especificar / Fuera de alcance).
> Antes era una narrativa cronológica de 319 líneas con tres ADDENDUMs encima, que
> **duplicaba** el detalle que ya vive en los subdirectorios del sprint.
>
> **Regla de este documento: es un índice, no un almacén.** Cada decisión vive en
> exactamente un lugar (su archivo), y acá aparece con una línea que alcanza para juzgar si
> hay que abrirlo. Si algo se explica dos veces, la copia de acá es la que sobra.
>
> Origen: reunión del **viernes 24-jul-2026** con Sebastián y Benjamín sobre la
> presentación del Sprint 7. La mejor reunión hasta ahora según Ernesto: quedó demostrado
> el entendimiento del mecanismo al explicar slots, expertos, cabezas y el diagrama del
> paper, que era lo que Benjamín venía exigiendo ([[feedback-benjamin-entender-mammoth]]).

---

## Destino

Cerrar el eje de **capacidad y entendimiento** de Mammoth con números de tarea y no de
muestra (cuántos expertos y slots hacen falta, y si recortarlos cuesta métrica), y dejar
**elegida y justificada** la dirección de la rama por tarea para mitosis, sin código.

El B8 llega a su fin cuando no queda nada por **decidir** antes de que alguien se siente a
construir esa rama.

## Notas

- **Dominio:** interpretabilidad y capacidad de MoE sobre MIL en patología computacional.
  Ortogonal al eje de rendimiento, cerrado en los Hallazgos 11-14 de `CLAUDE.md`.
- **Skills a consultar en cada sesión:** `@slurm-submission` antes de cualquier `sbatch`,
  `@mammoth` para el modelo, `@knowledge-audit` al documentar, `@humanizer-es` para el
  guion del deck.
- **Restricciones permanentes:** regla 9 (argumento y pre-registro antes de código) en todo
  lo que toque entrenamiento; regla 9.b si algo pretende reabrir el eje de rendimiento;
  workaround H (no cambiar de rama con un job vivo); workaround J (proceso CPU largo va
  desatado y reanudable).
- **Comparaciones:** siempre pareadas reusando el `--split_dir` del baseline
  ([[patron-paired-comparison-reuso-splits]]). El pipeline es determinista bit a bit, así
  que una réplica que quiera ser independiente **tiene que cambiar la semilla**
  ([[pipeline-determinista-bit-a-bit]]).

---

## Decisiones tomadas

Una línea por asunto cerrado. El detalle está en el enlace.

- [**Encargo 1 — escalar la medición de slots**](q1_slots_escalado/resultados.md) (27-jul)
  — barridas 1858 láminas-fold (1176 únicas) en 18 min de CPU: **slots efectivos
  159.5 ± 26.3 de 300** y **expertos 29.98 de 30**, con `e50=15` y `e90=27` exactos en las
  1858 sin excepción. El 158.7 de n=7 se sostiene y ahora es el número de la tarea; **E=30
  no está sobredimensionado**. Método en
  [`metodologia.md`](q1_slots_escalado/metodologia.md).
- [**Encargo 1, corrección sobre la dispersión**](q1_slots_escalado/resultados.md) (27-jul)
  — con n grande se **invierte** lo que decía el B7: no manda el tamaño de lámina
  (ρ cae 0.750 → 0.141) sino levemente la tarea (eta²=0.086), y el ~88 % de la varianza es
  entre láminas. La **cohorte casi no mueve la aguja**, lo que descarta que medir solo TCGA
  en el B7 haya sesgado el número.
- [**Encargo 3 — grid E×S**](grid_expertos_slots/resultados.md) (4-ago, job 4774, 40/40
  runs) — **cerrado en H_nula**: el contraste primario (recortar S) menos (recortar E) da
  +0.022 / −0.014 / −0.002 de AUC en los peldaños 270/210/150, o sea **el signo se invierte
  entre peldaños** y la dirección del recorte es indistinguible. Pre-registro en
  [`prereg.md`](grid_expertos_slots/prereg.md).
- [**Encargo 3, secundarios**](grid_expertos_slots/resultados.md) (4-ago) — los dos apuntan
  a que **la capacidad sobra**: el piso 30×3 (−70 % de capacidad) pierde solo
  0.039 ± 0.062 de AUC, que cruza cero, y dentro de la rama S **no hay dosis-respuesta**.
  El peor brazo del grid es 27×10, el recorte más chico.
- **Acotación al «el margen está en S»** (4-ago) — la ocupación medida en el encargo 1
  **describe el reparto del peso, no dimensiona la capacidad**. Los números 159.5/300 y
  29.98/30 siguen vigentes; lo que no se sostiene es inferir de ellos **dónde** conviene
  recortar. Anotado en `CLAUDE.md` Hallazgo 12 y en [[mammoth-slot-routing-weight]].
- [**El pipeline es determinista bit a bit**](grid_expertos_slots/resultados.md) (4-ago) —
  hallazgo transversal que salió del control del grid: misma semilla, mismos splits y
  mismas features reproducen el checkpoint **byte a byte** en esta GPU. Valida el reuso
  pareado por construcción y a la vez prohíbe llamar «réplica» a re-correr con la misma
  semilla ([[pipeline-determinista-bit-a-bit]]).
- [**Encargo 4 — papers**](reunion_31jul_redireccion.md) (31-jul) — cerrado **con una
  decisión, no con una lectura**. Ver *Fuera de alcance* para qué quedó afuera y por qué.
- [**La atención sí cae sobre las mitosis**](atencion_vs_patologo/resultados.md) (1-ago) —
  AUC de ranking **0.890 ± 0.039** en checkpoints que nunca vieron la lámina, y el modelo
  igual responde mal. Es el resultado que le sacó la motivación principal a la familia A.
  Pre-registro en [`prereg.md`](atencion_vs_patologo/prereg.md).
- [**Encargo nuevo de 3 papers para mitosis**](tareas_geometricas/papers_mitosis.md)
  (2-ago) — los tres son **D** PU learning (Zhao, MELBA 2022), **C** CellViT (MedIA 2024) y
  **B** ZoomMIL (ECCV 2022). **Se recomienda D primero y en dos pasos**, por ser el único
  cuyo régimen de supervisión coincide con nuestros positivos parciales, con un **go/no-go
  barato** antes de gastar GPU. Hojas de reunión en
  [`hojas_reunion.md`](tareas_geometricas/hojas_reunion.md), mecanismo interno en
  [`papers_explicados.md`](tareas_geometricas/papers_explicados.md).
- [**Deck del B8**](presentacion_b8/README.md) (3 al 4-ago) — 20 láminas a dos ejes, con el
  grid E×S como sección de cierre. Rediseño de 12 puntos ejecutado, auditoría en cero,
  guion humanizado y leído en voz alta. Queda **una** pendiente propia: la leyenda de la
  figura de la lámina 12.

---

## Todavía sin especificar

Niebla: se intuye que viene, pero todavía no se puede formular con precisión. El test para
sacar algo de acá **no es poder responderlo, es poder enunciarlo**.

- **Qué pidieron exactamente en el encargo 2.** Hay tres lecturas y la respuesta la tiene
  Sebastián. Análisis completo en
  [`slots_entrenados_encargo2.md`](slots_entrenados_encargo2.md). La lectura más plausible
  quedó **parcialmente respondida** por el encargo 1; si es la correcta, falta solo la
  parte de mapas sobre láminas privadas, que exige verificar disponibilidad de WSI.
- **Qué forma tiene una «rama aparte de CLAM» especializada por tarea.** La dirección está
  elegida (D, en dos pasos), pero la arquitectura concreta, dónde se engancha con el
  pipeline actual y qué comparte con el CLAM de producción no están definidos. Es lo que
  hay que aclarar antes de que esto pueda pre-registrarse.
- **El sign-off del patólogo sobre los nombres de tejido.** Los nombres que usamos para
  expertos y slots son **lectura visual nuestra, no anotación**
  ([[mammoth-interpretabilidad-objA]]). Se arrastra desde OBJ-A y sigue sin resolver.
- **Si el material de anotación alcanza para entrenar.** Hay una lámina, un anotador y 26
  marcas de mitosis, con positivos parciales y dos regiones de escaneo
  ([[anotaciones-patologo-qupath]]). Cuánto de eso es suficiente para el paso 1 de D es
  parte del go/no-go, no algo que se pueda decidir antes.

### Pendiente sharp (ya se puede enunciar, falta pre-registro)

- **¿El Δ del 4589 en CDIS `_ci_reform` sobrevive a semillas nuevas?** Mammoth dio
  Δbal_acc **+0.074 ± 0.033 (5/5 folds)** en la formulación nueva, con ambos recalls al
  alza. El control del grid **no** lo replicó ni podía (misma semilla). La réplica **exige
  semillas nuevas** y, si se plantea como búsqueda de mejora, entra por **regla 9.b** con
  pre-registro, branch y `reviewer`. Detalle en
  `sprints/B7_sprint7/resultados_interpretabilidad.md` §2.

---

## Fuera de alcance

Ruled out de **este** esfuerzo. No gradúa: vuelve solo si se redibuja el destino, y
entonces como esfuerzo nuevo.

- **SI-MIL no se implementa** (31-jul). Gana interpretabilidad a costa de empeorar
  levemente la métrica, y lo que se busca es métrica. Su propia Tabla 2 lo muestra en la
  celda que nos toca (0.937 → 0.925 accuracy, 0.972 → 0.957 AUC con CLAM de base). Estudio
  conservado en [`simil_estudio.md`](simil_estudio.md) y
  [`simil_explicacion_matematica.md`](simil_explicacion_matematica.md).
- **HoVer-Net queda en pausa por costo** (31-jul). Sebastián lo corrió él mismo: **3.3 h
  por lámina**. **Se conserva su idea** de correrlo solo sobre los 20 mejores parches que
  CLAM selecciona, para cuando haya más GPU. Estudio en
  [`hovernet_estudio.md`](hovernet_estudio.md), memoria [[simil-hovernet-decision-31jul]].
- **La familia A de la rama de mitosis** (cambiar el operador de agregación) perdió su
  motivación principal el 1-ago: la atención **sí** cae sobre las mitosis y el modelo igual
  responde mal. Quedan B, C y D. Ver [`tareas_geometricas/README.md`](tareas_geometricas/README.md).
- **Los dos papers de suscripción**: LVI → metástasis ganglionar (Human Pathology 131:26-37,
  2023) e ILSC (Liu et al., MedIA 2026). Sin arXiv ni PMC, verificado. Requieren acceso
  institucional y los consigue Ernesto. Fichas y BibTeX en [`papers_b8.md`](papers_b8.md).
- **Recortar E o S en producción.** El grid cerró en H_nula, así que no hay base para
  cambiar la configuración 30×10 por ninguna de las probadas.

---

## Qué no se afirma

- Que la **dirección** del recorte de capacidad sea indiferente en general. Se midió en una
  tarea (CDIS `_ci_reform`), un dataset y una GPU. Lo que se afirma es que **en ese
  terreno** resultó indistinguible.
- Que el determinismo bit a bit valga cross-hardware. Está acotado a esta RTX A6000 y este
  stack.
- Que el encargo 2 esté cerrado porque los slots ya se entrenan con nuestro dataset.
  Primero se aclara qué pidieron.
- Que el Δ del CDIS `_ci_reform` sea real. Son 65 negativos totales, ~13 por fold, y la
  réplica con semillas nuevas está pendiente.
- Que los nombres de tejido de expertos y slots sean anotación. Son lectura visual nuestra.
