# Workarounds conocidos

## 1. Importar `CLAM_MB` desde mi workspace

**Estado**: ✅ **NO necesario** (validado en Werner/`memoriaSebaDonoso` el
5 mayo 2026; re-validar en `clam_latest` al primer uso). El import directo
`from models.model_clam import CLAM_MB` funciona sin parches.

**Síntoma histórico** (sprints anteriores): hacer ese import desde mi
workspace fallaba porque el `__init__.py` del fork de Sebastián importaba
`timm`, y `timm` no estaba siempre instalado en el env de trabajo.

**Estado actual del archivo**:
- `models/__init__.py` existe; en `memoriaSebaDonoso` su carga no rompe.
- `models/timm_wrapper.py` existe pero `timm` está instalado en el env, así
  que la dependencia se resuelve.

### Procedimiento de import — intentar en orden

**Paso 1 — Import directo simple** (esto es lo que se usa hoy):

```python
import sys
sys.path.insert(0, "/media/administrador/Storage1/sdonoso/clam_environ")

from models.model_clam import CLAM_MB
print("import OK")
```

Si esto funciona, no hay workaround necesario. **(En `memoriaSebaDonoso`
funciona — validado 5 mayo 2026.)**

**Paso 2 — Workaround con `importlib.util`** (fallback histórico, sólo si
en un env distinto el Paso 1 vuelve a fallar):

```python
import importlib.util
import sys
from pathlib import Path

CLAM_PATH = Path("/media/administrador/Storage1/sdonoso/clam_environ")

spec = importlib.util.spec_from_file_location(
    "model_clam",
    CLAM_PATH / "models" / "model_clam.py",
)
model_clam = importlib.util.module_from_spec(spec)
sys.modules["model_clam"] = model_clam
spec.loader.exec_module(model_clam)

CLAM_MB = model_clam.CLAM_MB
```

**Importante**: el path real es `models/model_clam.py`, no
`model_clam.py` en raíz como decían algunas memorias viejas.

**Paso 3 — Documentar el resultado**: actualizar este archivo con cuál
de los dos pasos funcionó, y eliminar la incertidumbre.

### Smoke test

`./scripts/verify_clam_access.sh` ejecuta el procedimiento completo y
reporta cuál camino funcionó.

### Cuándo NO usar ningún workaround

Cuando el código que voy a correr es `main.py` directo de Sebastián vía
`python main.py ...`. Ese entrypoint resuelve sus propios imports relativos
correctamente. El workaround es solo para cuando yo importo `CLAM_MB` desde
un script propio en mi workspace.

## 2. Openslide build local

**Estado**: solo aplica si encuentro problemas leyendo WSI. Sebastián tuvo
problemas con openslide en este server y armó un build local en
`/media/administrador/Storage1/sdonoso/clam_environ/openslide/`.

**Lectura obligatoria si aparecen errores de openslide**:
`/media/administrador/Storage1/sdonoso/clam_environ/openslide_solution.md`.

## 3. Bug `topk` en `inst_eval` con slides `< k_sample` patches

**Estado**: 🔧 mitigado vía split filtrado + preflight (Sprint 4). El bug
está en el codebase de Sebastián (read-only) — no se corrige ahí.

**Síntoma**: el entrenamiento crashea con
`RuntimeError: selected index k out of range`, traza terminando en
`models/model_clam.py:112` (la línea del `torch.topk`). El crash puede
aparecer **tarde** (tras horas / muchas épocas).

**Causa**: `inst_eval` hace `torch.topk(A, self.k_sample)` con
`k_sample = --B`. Si una slide tiene un tensor de features `.pt` con
`shape[0] < k_sample` (menos parches que `B`), `topk` no puede seleccionar
`B` elementos de un tensor más chico → revienta. Con `--weighted_sample`
(muestreo con reemplazo) la slide problemática puede no sortearse hasta una
época avanzada → por eso el crash es tardío.

**Cómo detectar**: `scripts/preflight_minpatch.py` escanea el split de train
y reporta las slides con `< min_patches` parches **antes** de entrenar. Es
el preflight obligatorio de los `.slurm` (ver entrada G de "Workarounds
operativos" en `CLAUDE.md`).

**Cómo mitigar**:
1. Filtrar el split con `scripts/filter_split_by_minpatch.py` — remueve del
   **train** las slides problemáticas (val/test intactos: el path de eval
   `summary()` no llama `inst_eval`). Ejemplo aplicado:
   `splits_local/microcalcificaciones_pth_100_minpatch16/README.md`.
2. **NO** modificar `clam_environ/` (codebase read-only de Sebastián).
3. **NO** bajar `k_sample` / `--B` — es variable de ablation en el Sprint 4.

**Run de referencia**: `results/failed_runs/4096_baseline_B8_topk_bug/`
(logs + checkpoint parcial del job 4096 que cayó por este bug).

**Slides identificadas a la fecha** (ambas en el train de
`microcalcificaciones_pth`):
- `histai_1536_slide_H&E_0` — 6 parches (rompe B=8 y B=16).
- `histai_1196_slide_H&E_0` — 8 parches (rompe B=16).

Para la reunión queda abierta la pregunta de si son biopsias chicas
esperables o un fallo de detección de tejido upstream (ver sección C de
`sprints/B4_sprint4/objetivo_3_modulo_mil_alternativo/investigacion/04_riesgos_y_preguntas_reunion.md`).

## 4. (espacio para más workarounds según vayan apareciendo)
