# Sprint B5 — Cierre de trimestre (recta final)

> Abierto 1-jun-2026 tras la reunión con Benjamín. **Sprint de alto riesgo**:
> Benjamín vuelve ~21-jun, a fin de mes cierra el trimestre y la presentación
> **decide si Ernesto continúa** en EnvironBio. Consigna: avanzar más rápido y
> lucirse. Equipo = Ernesto + Sebastián (Eduardo renunció).
>
> Base del deck: B4 cerrado (`papers/presentations/CLAM_Sprint_B4.pdf`, legacy
> local, gitignored). Convenciones de entregables:
> [[presentacion-convenciones-benjamin]] (notas concisas, sin nº de job,
> baselines como "Environ vX").

## Lecciones de B4 que gobiernan B5

- **La arquitectura del agregador NO es la palanca** para microcalc (CLAM×DSMIL
  cerrado simétricamente). El cuello = **datos / contexto espacial / desbalance**.
- **Single-split engaña** fuerte a n≈33 → **MC-CV k=5 obligatorio** + comparación
  **PAIRED** por reuso de splits ([[patron-paired-comparison-reuso-splits]]).
- **Métrica honesta** = balanced_acc media±std + matriz de confusión con n por
  clase. Macro-AUC solo, nunca (test ciego con pocos positivos).

## Objetivos (priorizados por Benjamín)

### Obj 1 — mammoth k=5 paired (HEADLINE, port listo)
Correr y analizar mammoth (CLAM con la 1ª capa → MoE) sobre las 3 binarias de
microcalcificaciones, paired vs CLAM, k=5. **Mammoth ataca el patch embed —
componente que DSMIL NO toca → eje ortogonal al cerrado en B4** (no es reapertura).
Port, hipótesis y reviewer GO ya hechos en B4: `objetivo_6_mammoth/`. Falta:
`sbatch scripts/run_obj6_mammoth_binarias_kfold.slurm` (con OK de Ernesto) +
análisis (Δ pareado por fold, balanced_acc). Skill: `@mammoth`.

### Obj 2 — Magnificación (research-first)
Benjamín pidió **investigar más antes de implementar**. Buscar papers donde
mayor magnificación / nº de parches mueve tareas donde estamos débiles, con
buenos resultados; idealmente llegar con algo corrido para comparar contra el
baseline. NO codear extracción de features nueva sin argumento (regla 9). Es el
"Eje A" de `sprints/B4_sprint4/ejes_futuros_microcalc.md`.

### Obj 3 — k=5 folds en más tasks
Extender MC-CV k=5 a otras tasks débiles (no solo microcalc) — da media±std en
vez del single-split ruidoso. Reusar el harness `train_dsmil.py` (genérico:
clam/dsmil/clam_mammoth) y el patrón de splits k=5.

### Obj 4 — Parches/slides útiles (Eje B)
Identificar los parches/slides que aportan valor al train; sin ellos el modelo
fracasa si aparecen en val. Insumo: heatmaps de atención (Obj 4 de B4, pendiente).
Conecta con la magnificación (qué contexto espacial importa).

### Obj 5 — Pregunta del CAP (research clínico)
Benjamín pidió investigar en el **College of American Pathologists** si tener
**una** de las 3 binarias positiva (cdis / tejido no neoplásico / carcinoma
invasivo) ya cuenta como "cáncer con microcalcificación". Define la semántica de
la etiqueta y si la jerarquía presencia/ausencia tiene sentido clínico.

### Obj 6 — PCGrad (gradient surgery, eje separado)
Eduardo dejó `utils/pcgrad.py` + `grad_cosine` en su `core_utils`. PCGrad
proyecta gradientes en conflicto → ataca el **mismo** *instance-gradient
interference* que mammoth, pero por **optimización** (no arquitectura). Eje
separado: NO mezclar con mammoth en la misma corrida. Evaluar con su propia
hipótesis tras Obj 1.

## Reglas duras (de CLAUDE.md, no se renegocian)

Containment (`clam_testing2/`), `clam_environ/` READ-ONLY, GPU solo vía `sbatch`,
preflight obligatorio, argumento antes de código + reviewer, push lo autoriza
Ernesto. Decisión revisitada → branch nueva (mammoth NO lo es: eje ortogonal).
