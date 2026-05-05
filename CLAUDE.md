# CLAUDE.md — Control center OncoMets / Ernesto

> Este archivo es lo primero que Claude Code lee al lanzarse en este repo.
> Contiene contexto persistente del proyecto y reglas operativas.
> Estado en evolución (sprint actual, hallazgos): ver `progress/current.md`.

---

## Quién soy y dónde estoy

Soy Ernesto Gamero, estudiante de último año de Ingeniería Civil Electrónica
(esp. Computadores) en la UTFSM. Práctica en EnvironBio en el proyecto
**OncoMets** (IA para diagnóstico oncológico), 20 hrs/sem. Supervisor:
Sebastián Gaete. Senior: Benjamín. Colaborador: Eduardo.

Este repo (`oncomets-ernesto`) es mi **control center** sobre Werner. NO
contiene el código de CLAM — ese es de Sebastián Donoso y es read-only.

## Stack y paths críticos

**Servidor**: Werner — 4× NVIDIA TITAN RTX, Python 3.11, PyTorch 2.11+cu130.
- Hostname real del equipo: `jenny2-System-Product-Name`.
- Alias SSH desde mi laptop: `environbio` (configurado en `~/.ssh/config`).
- Usuario en Werner: `onco` (compartido entre el equipo, no personal).
- Mi `$HOME` allá: `/home/onco/` (compartido), pero **mi workspace de trabajo
  vive bajo `/mnt/disco_duro/onco/oncologiaEnviron/ernestogamero/`**, separado
  del de los demás miembros del equipo.
- Conda activo por default: `(base)`. El env con PyTorch 2.11+cu130 puede ser
  `base` u otro — confirmar con `conda env list` la primera vez y documentarlo
  en `docs/werner_environment.md`.

**Codebase de Sebastián Donoso (READ-ONLY, no tocar)**:
```
/mnt/disco_duro/onco/sebastianDonoso/testMIL/CLAM/
├── model_clam.py          # L107–123: inst_eval. L125–136: inst_eval_out. L237: attention pooling.
├── core_utils.py          # L243–251: cómputo de instance loss en train loop
├── main.py                # entrypoint
└── builder.py             # construcción del modelo
```

**Mi workspace en Werner**:
```
/mnt/disco_duro/onco/oncologiaEnviron/ernestogamero/
└── oncomets-ernesto/      # ← este repo, clonado acá
```

> El home `/home/onco/` es **compartido** con el equipo. No instalar deps
> personales con `pip install --user` ni dejar archivos personales ahí.
> Todo lo mío vive bajo `oncologiaEnviron/ernestogamero/`.

**Embeddings**: CONCH (512-dim TCGA, 1024-dim Environ).

## Pipeline OncoMets (referencia rápida)

```
WSI → patches → CONCH features (512/1024-dim) → CLAM_MB → 10 clases clínicas
```

## Sprint actual: B3 / Sprint 3

**Deadline: miércoles 6 de mayo de 2026.**

Detalle exhaustivo en `Objetivo_Especifico_B3_Sprint3__EG.xlsx` (hoja
"Ernesto Gamero"). Resumen de los 4 entregables:

| # | Foco | Entregable |
|---|---|---|
| 1 | Estudio profundo de `L_instance` y su acoplamiento con pseudo-etiquetas | Diagrama `attention → top-B/bottom-B → pseudo-labels → SmoothTop1SVM → L_instance` + tabla de hiperparámetros |
| 2 | Entrenamiento end-to-end de CLAM en Werner con dataset público | Reporte con config, dataset, curvas loss/acc, observaciones |
| 3 | Pipeline de entrenamiento + formato de los `.csv` | Diagrama del pipeline + esquemas de CSVs input/output |
| 4 | ≥2 propuestas de mejora algorítmica (estudio teórico, sin implementar) | Una de ellas es aumentar top-B/bottom-B; la otra abierta |

**Estado vivo**: ver `progress/current.md`.

## Reglas operativas no negociables

1. **NO modificar** ningún archivo bajo `/mnt/disco_duro/onco/sebastianDonoso/`.
   Si necesito cambiar comportamiento, lo hago via wrapper o copia local en
   mi workspace.
2. **Workaround conocido**: `CLAM_MB` debe importarse vía `importlib.util`
   por el `timm` en el `__init__.py` de Sebastián. Ver `docs/workarounds.md`.
3. **Validación factual**: toda afirmación técnica se valida contra
   (a) paper original (`CLAM_Data_Efficient_and_Weakly_Supervised__Paper.pdf`)
   y/o (b) código en `model_clam.py` / `core_utils.py`. Si no está en
   ninguno: decir "no encontrado", no inventar.
4. **Referenciar líneas exactas** del código: formato `model_clam.py:107–123`.
5. **No inventar resultados experimentales**. Si una métrica no está en los
   logs, decirlo.

## Hechos validados (no re-derivar)

- Attention pooling (`model_clam.py:237`, `torch.mm(A, h)`) opera sobre
  **todos los N parches**. La selección top-B/bottom-B NO interviene acá.
- top-B/bottom-B sólo aplica al **instance classifier path**
  (`inst_eval` L107–123, `inst_eval_out` L125–136).
- Bajo `subtyping=True`: las ramas out-of-class dominan la instance loss
  ~9:1 vs la rama in-class. Es sesgo estructural, no de tuning.
- La división por `n_classes` en `L_instance` interactúa con `bag_weight`
  en `core_utils.py` — entender juntos, no aislados.

## Formato de entregables (regla de oro)

**Diagramas > texto plano. Siempre.** Sebastián rechaza informes de texto
plano. Estilo visual: ver `Modelo_OncoMets_Spatial_V1.pdf` en project files.
Estructura de presentación: ver `Plantilla.pdf`.

**Speaker notes (formato fijado en B2)**:
- Bloques `BLOQUE N — Título`
- Sub-items con `-> `
- Fórmulas inline sin LaTeX render (ej. `h_k = ReLU(W₁·z_k)`)
- Sin emojis ni corchetes de gesto
- Destacados en línea propia: `Punto clave:` / `Detalle crítico:`
- Ultra-minimalista, listo para copy-paste a OnlyOffice

## Subagentes disponibles

| Agente | Foco | Cuándo invocarlo |
|---|---|---|
| `trainer` | Entregable 2: ejecutar entrenamiento end-to-end | Cualquier tarea que toque `main.py`, splits CSV, lanzamiento en GPU |

(Sólo `trainer` por ahora. Setup minimal pre-deadline. Post-cierre se
escalará a leader/implementer/reviewer con `@harness`.)

## Skills cargadas en este repo

- `@dev-workflow` — estructura del repo, Gitflow, validación.
- `@harness` — referencia para escalado post-sprint.

(`@architect` y `@sys-env` no aplican a este repo — la primera es para
crear skills, la segunda es de mi laptop personal Arch+Hyprland.)

## Contexto del usuario para sesiones rápidas

Idioma: **español**. Tono: técnico + explicativo. No simplificar conceptos
generales de ML/DL/CV. SÍ explicar pedagógicamente al introducir notación
específica del subcampo (MIL, weakly-supervised, computational pathology).
