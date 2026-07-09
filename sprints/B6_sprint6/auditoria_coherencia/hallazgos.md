# Auditoría de coherencia — Fable, 9-jul-2026 (sprint B6)

> Gatillada por el cierre del test de la skill `humanizer-es` en sesión fresca
> (handoff `handoff_B6_20260709_152223.md`) + pedido de registrar progreso y actualizar
> el repo. Alcance: integrar el conocimiento nuevo (skill probada) en los cuatro frentes
> y tapar los huecos de coherencia que salieron. Documental — sin GPU, sin tocar
> modelo/training → se queda en `main` ([[git-trabajar-en-main-por-defecto]]).

## Tabla resumen

| id | hallazgo | tipo | severidad | acción |
|----|----------|------|-----------|--------|
| F1 | CLAUDE.md §"Skills cargadas" no lista `humanizer-es` (existe en disco + loader desde `5d70218`) | stale | media | agregar 1 línea al inventario |
| F2 | Sin memoria ni entrada en MEMORY.md para `humanizer-es` (conocimiento nuevo no persistido) | gap | media | crear memoria `humanizer-es-skill` + línea en index |
| F3 | `.pptx` de sprints NO gitignoreado, pero precedente = 0 pptx trackeados (deck = derivado) | policy-gap | media | regla `.gitignore` `sprints/**/*.pptx` |
| F4 | Resultado del test fresco de `humanizer-es` solo vive en scratchpad (efímero) | gap | baja | doc durable `humanizer_es_validacion.md` |
| F5 | Agentes `trainer`/`reviewer` y skills — estado | OK | — | sin acción (verificado) |

---

## F1 — CLAUDE.md no lista `humanizer-es` (stale)

- **Qué dice cada fuente:** la skill existe en `.claude/skills/humanizer-es/SKILL.md`
  (commit `5d70218`, valida PASS) y el loader la surface con sus triggers. Pero
  CLAUDE.md §"Skills cargadas en este repo" (L877+) enumera 8 skills y **no** la incluye.
- **Canónico:** CLAUDE.md es el inventario durable → debe listarla.
- **Fix:** agregar una línea concisa después de `@knowledge-audit`, con puntero a la
  convención de estilo que la skill cumple ([[notas-presentador-guion-didactico]]).

## F2 — Conocimiento nuevo sin persistir (gap)

- **Qué falta:** ninguna memoria ni línea en MEMORY.md describe qué es `humanizer-es`,
  su alcance (guion hablado + prosa de entregables; NO docs técnicos estructurados) ni
  el resultado del test fresco.
- **Canónico:** las memorias son la persistencia cross-sesión → crear una `reference`
  que apunte al SKILL.md y a la convención de notas.
- **Fix:** memoria `humanizer-es-skill` + línea en index. Enlaza
  [[notas-presentador-guion-didactico]] (la skill es el *procedimiento* de esa regla) y
  [[readme-resultados-formato-minimalista]] (una de las exclusiones).

## F3 — `.pptx` de sprints no ignorado (policy-gap)

- **Evidencia:** `git ls-files '*.pptx'` = 0; el B5 se manejó como "deck gitignored"
  (CLAUDE.md ADDENDUM B5). El de B6 (`sprints/B6_sprint6/presentacion_viernes/CLAM_Reunion_Mammoth.pptx`,
  4.6 MB) cae fuera de los patrones actuales (`CLAM_Sprint_*.pdf`, `papers/presentations/`).
- **Regla de la casa:** el deck es un derivado local; la fuente vive en el `generate_*.py`
  + `convenciones_deck_*.md` + guion. El binario no va a git.
- **Fix:** regla `.gitignore` `sprints/**/*.pptx` (con comentario). Si algún sprint quiere
  snapshot histórico, `git add -f` explícito (mismo patrón que el PDF transitorio).

## F4 — Resultado del test solo en scratchpad (gap)

- **Fix:** mover el resultado del loop de 4 pasos + los tests de exclusión a
  `sprints/B6_sprint6/humanizer_es_validacion.md` (durable, citable).

## F5 — Agentes y skills (verificado, sin acción)

- **Agentes:** `trainer.md` (act. 6-jul) y `reviewer.md` (2-jun) presentes, con
  frontmatter válido (name/description/tools) y rol claro; ambos aparecen en los tipos
  de agente disponibles. **Ya implementados.** Sin cambios.
- **Skills:** las 11 skills tienen `SKILL.md`; `humanizer-es` valida PASS
  (`quick_validate.py`). Sin deriva estructural.

---

## Resultado del test de `humanizer-es` (insumo de F1/F2/F4)

Probada en sesión fresca sobre un borrador crudo (guion de magnificación B6 cargado de
tells) + calibrada contra la voz de las notas B5. Veredicto por propiedad:

1. **Auto-activación:** triggers/description bien formados; un prompt natural
   ("esto suena a IA, humanizalo" / "revisá el guion") matchea casi literal. No se pudo
   probar el disparo en frío porque la sesión llegó dirigida por el handoff (ya cebada);
   recomendación = confirmación de 1 min en sesión fría con prompt natural.
2. **Loop de 4 pasos:** corrió completo (identificar ~20 tells con nº de patrón →
   borrador → auto-auditoría que cazó residuos → final). Delta grande y bueno.
3. **Exclusiones:** dejó intacto un snippet técnico estructurado (tabla balanced_acc/AUC +
   path) y una prosa ya limpia (slide 5 B5) → respeta precision.

**Señal fuerte:** la versión final convergió casi palabra por palabra con la slide-final
ya canónica del guion B5 → la skill empuja prosa cruda-IA hacia la voz real del autor.
Detalle en `humanizer_es_validacion.md`.

**Veredicto:** skill LISTA para uso, sin ajustes al `SKILL.md`.
