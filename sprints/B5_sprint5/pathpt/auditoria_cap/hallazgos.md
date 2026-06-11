# Knowledge-audit — integración del hallazgo CAP (prompts PathPT)

> Audit FOCALIZADO (un tema, no re-audit completo) bajo el método de
> `@knowledge-audit`: dejar la evidencia del hallazgo CAP en su home canónico, sin
> duplicar ni romper la pre-registración. Findings-first; fixes en §2.
>
> **Por qué en `feat/pathpt-etapa1` y no en branch de audit aparte:** la integración
> es parte del mismo entregable PathPT/CAP que se mergea a main en este turno — un
> branch de audit separado fragmentaría el merge pedido. Juicio documentado.

## 0. El hallazgo (qué dejar para futuras sesiones)
Revisión de los 2 protocolos CAP que Ernesto señaló (`papers/Breast.Invasive.Bx_1.2.0.0.REL_CAPCP.pdf`,
`papers/Breast.Bmk_1.6.0.0.REL.CAPCP.pdf`) para anclar los prompts de PathPT:
- **`Breast.Invasive.Bx` (v1.2.0.0) = la fuente H&E relevante.** Necrosis (Nota C: comedo/
  central/focal + distinción vs material secretorio "without nuclear debris"), mitosis
  (Nottingham, Table 1), patrones, microcalc, invasión, diferenciación tubular.
- **`Breast.Bmk` (v1.6.0.0) = inmunohistoquímica/molecular (ER/PgR/HER2/Ki-67) → NO aplica
  a PathPT/CONCH** (que trabajan sobre H&E). Referencia para tareas futuras de biomarcadores.
- **Necrosis prompts → v3 (CAP Nota C)**: AUC go/no-go **0.688** > v1 0.677 > v2 0.649. La
  palanca CAP no probada (distinción NEGATIVA vs material secretorio) ayudó +0.011. Es el
  default del driver desde el commit `8bb08ca`. Sign-off clínico final = Sebastián.
- Detalle canónico: [prompts_cap.md](../prompts_cap.md).

## 1. Findings (id · qué · canónico · acción)

| id | finding | tipo | canónico | acción |
|---|---|---|---|---|
| C1 | El conocimiento CAP↔tareas vive en la memoria `cap-fuente-clases-tareas`, pero le falta la distinción **Invasive.Bx (H&E) vs Bmk (IHC, no aplica)** y el estado de los prompts | redundancy/gap | memoria `cap-fuente-clases-tareas` + doc `prompts_cap.md` | añadir distinción + necrosis v3 + puntero al doc |
| C2 | Memoria `pathpt-testing-necrosis-mitotic` referencia prompts **v1**; ahora el driver usa **v3 CAP** | stale | misma memoria | actualizar a v3 (0.688) |
| C3 | Prereg `etapa1_prereg_necrosis.md` §3.5 dice "reusar pool v1"; era cierto al pre-registrar | pre-reg integrity | §3.5 queda histórico | **NO reescribir §3.5**; ADDENDUM en §7 con el update CAP v3 |
| C4 | `progress/current.md` no refleja que la Etapa 1 está **implementada + validada CPU + CAP-grounded, lista para lanzar** | stale | `progress/current.md` (snapshot vivo) | actualizar sección PathPT |
| C5 | CLAUDE.md: sin contenido de prompts/CAP-grounding | — | (homes = memoria + doc) | **no tocar** (evitar bloat; criterio canónico-vs-referencia) |

## 2. Fixes aplicados (este turno)
- C1 → memoria `cap-fuente-clases-tareas` (+ Invasive.Bx/Bmk + necrosis v3 + puntero `prompts_cap.md`).
- C2 → memoria `pathpt-testing-necrosis-mitotic` (prompts v3 CAP).
- C3 → addendum en prereg §7 (sin tocar §3.5).
- C4 → `progress/current.md` (Etapa 1 implementada, lista para `sbatch`).
- C5 → sin cambios (decisión).
- `MEMORY.md` index actualizado para las memorias tocadas.

Containment OK (solo bajo `clam_testing2/oncomets-ernesto/` + memorias en `~/.claude`).
GPU libre, sin job que perturbar (workaround H). Merge a main autorizado por Ernesto este turno.
