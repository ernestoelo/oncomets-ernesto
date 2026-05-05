# Entregable 2 — Entrenamiento end-to-end de CLAM en Werner

**Deadline**: 6 mayo 2026. **Lo lleva el agente `trainer`.**

## Tareas

1. Auditar datasets WSI ya disponibles en Werner. Camelyon mencionado por
   Sebastián como candidato.
2. Configurar splits train/val/test y generar el `.csv` de input siguiendo
   la convención exigida por el repo CLAM (validar contra `main.py`).
3. Ejecutar al menos un entrenamiento completo. Registrar config, curvas,
   métricas. Trazabilidad para iteraciones futuras.

## Output esperado

- `splits/<dataset>_{train,val,test}.csv`
- `csv_format.md` — esquema validado contra `main.py`.
- `logs/<run_id>/config_snapshot.txt` (auto-generado por `train_clam.sh`).
- `logs/<run_id>/train.log`
- `logs/<run_id>/metrics.csv` (vía `extract_metrics.py`).
- `reporte.md` — narrativa: dataset elegido, config, métricas, observaciones.

## Cómo lanzar

```bash
./scripts/train_clam.sh \
    --csv sprints/B3_sprint3/objetivo_2_entrenamiento/splits/<dataset>_train.csv \
    --data-root <path-features-CONCH> \
    --extra "--task <task> --model_type clam_mb --B 8"
```
