# Auditoría de coherencia — registro de resultados Obj2 (patrón, job 4243)

> Addendum a `hallazgos.md` (H1–H9). Auditoría puntual **post-análisis del job 4243**,
> antes de pushear el commit `94284b6`. Foco: que los últimos hallazgos/resultados estén
> registrados de forma consistente en los 5 documentos tocados. Read-only → 1 fix.
> Fecha: 4-jun-2026. GPU libre (sin jobs activos al auditar).

## Alcance

Cross-read de los 5 frentes donde aterrizó el resultado del job 4243:
`sprints/.../objetivo_2_mammoth_patron_invasion/resultados.md`,
`results/README_experimentos_mammoth_environ.md` §4.b, `CLAUDE.md` Hallazgo 12,
`progress/current.md`, memoria `mammoth-investigacion-integracion` (+ `MEMORY.md`).

## Resumen

| id | hallazgo | severidad | acción |
|---|---|---|---|
| A1 | README del Obj2 §Estado marcaba `[~]` "En curso (~13h)" tras el cierre del job | stale | **corregido** → `[x]` 40 runs completos + resultado |
| A2 | Δ pareado y métricas pooled consistentes entre resultados.md, README §4.b y CLAUDE.md | OK | sin acción |
| A3 | Job/fecha/runs (4243 · 4-jun 01:33 · 40 runs) consistentes en los 5 docs | OK | sin acción |
| A4 | Balance % (tejido ~58, cribiforme ~49, micro 7, papilar 6) y conteo 7 binarias coherentes | OK | sin acción |
| A5 | Wikilinks de Hallazgo 12 (CLAUDE.md) y de la memoria editada → todos resuelven | OK | sin acción |
| A6 | Verdad de campo `results/obj2_mammoth/` versionada sin pesados (`.pt` gitignored) | OK | sin acción |

## Detalle

### A1 — stale (corregido)
`objetivo_2_mammoth_patron_invasion/README.md` §Estado L133-137 todavía decía
`[~] sbatch ... En curso (~13h); analizar al terminar` y un item `[ ] Resultados`
pendiente. El job cerró 4-jun 01:33 y los resultados ya están escritos+analizados.
**Fix:** los dos items pasan a `[x]` (40 runs completos; resultados analizados, veredicto
mammoth NO es palanca). Se preserva la traza del crash 4241 y el puntero a
[[working-tree-compartido-job-en-curso]].

### A2–A6 — verificado consistente (sin acción)
- **Números:** cribiforme Δbal **+0.044 ± 0.048** (4+/1−), ΔAUC +0.022 ± 0.042; solido
  **−0.014 ± 0.064** (3+/2−); pooled micropapilar (CLAM bAcc 0.617 / mam 0.561; AUC
  0.707/0.710) y papilar (0.531/0.506; AUC 0.583/0.599); TP global 4/15·2/15 (CLAM),
  3/15·1/15 (mammoth). Idénticos donde se repiten.
- **Pre-registración intacta:** el README §Hipótesis (regla 9) NO se tocó; el veredicto
  vive en `resultados.md`. Sin reescritura retroactiva.
- **Canonical vs referencia:** detalle en `resultados.md`; tabla equipo en README §4.b;
  fact durable en CLAUDE.md Hallazgo 12; átomo en la memoria. Sin duplicar contenido único.

## Conclusión
Registro **coherente**. Un único stale (A1) corregido. Listo para push.
