# Workarounds conocidos

## 1. Importar `CLAM_MB` desde mi workspace

**Estado**: ⚠️ **a re-validar al primer uso (5 mayo 2026)**.

**Síntoma histórico** (sprints anteriores): hacer
`from models.model_clam import CLAM_MB` desde mi workspace fallaba porque
el `__init__.py` del fork de Sebastián importaba `timm`, y `timm` no estaba
siempre instalado en el env de trabajo.

**Estado actual del archivo**:
- `models/__init__.py` existe pero su contenido no fue verificado al
  re-armar este repo.
- `models/timm_wrapper.py` existe — sospechoso, sigue habiendo dependencia
  de timm en el package.

### Procedimiento de import — intentar en orden

**Paso 1 — Import directo simple** (intentar primero):

```python
import sys
sys.path.insert(0, "/mnt/disco_duro/onco/sebastianDonoso/testMIL/CLAM")

from models.model_clam import CLAM_MB
print("import OK")
```

Si esto funciona, no hay workaround necesario.

**Paso 2 — Workaround con `importlib.util`** (fallback si Paso 1 falla):

```python
import importlib.util
import sys
from pathlib import Path

CLAM_PATH = Path("/mnt/disco_duro/onco/sebastianDonoso/testMIL/CLAM")

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
`/mnt/disco_duro/onco/sebastianDonoso/testMIL/CLAM/openslide/`.

**Lectura obligatoria si aparecen errores de openslide**:
`/mnt/disco_duro/onco/sebastianDonoso/testMIL/CLAM/openslide_solution.md`.

## 3. (espacio para más workarounds según vayan apareciendo)
