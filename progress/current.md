# progress/current.md

> Sesión activa. Append-only. Cada sesión nueva = entrada nueva al final.
> Al cerrar el sprint, mover este contenido a `history.md` y reiniciar acá.

---

## Sprint actual: B3 / Sprint 3

**Deadline**: miércoles 6 de mayo de 2026.

**Estado por entregable** (actualizar tras cada sesión):

- [ ] **Entregable 1** — Estudio L_instance + diagrama + tabla de hiperparámetros.
  - Próximo paso: re-leer Sec 2.2 del paper CLAM con foco en SmoothTop1SVM.
- [ ] **Entregable 2** — Entrenamiento end-to-end de CLAM en Werner.
  - Próximo paso: auditar datasets WSI locales en Werner.
  - Bloqueante de los entregables 3 y parcialmente del 4.
- [ ] **Entregable 3** — Pipeline + formato `.csv`.
  - Próximo paso: trazar control flow `main.py → core_utils.py`.
  - Depende parcialmente de E2 (formato real lo confirma corriendo).
- [ ] **Entregable 4** — ≥2 propuestas de mejora.
  - Idea 1: aumentar top-B/bottom-B (ya planteada en reunión).
  - Idea 2: candidatas en memoria — adaptive pseudo-label selection,
    fragility de mutual exclusivity, asimetría 9:1 bajo subtyping.

---

## Sesión 1 — _(fecha de inicio)_

_(arrancar acá la primera sesión real en Werner)_

### Setup

- [ ] `bootstrap_werner.sh` corrió sin errores.
- [ ] `verify_clam_access.sh` confirma `CLAM_MB` importable.
- [ ] `nvidia-smi` muestra 4 GPUs disponibles.

### Decisiones tomadas

_(vacío)_

### Bloqueos

_(vacío)_

### Próxima sesión arranca con

_(vacío)_

---
