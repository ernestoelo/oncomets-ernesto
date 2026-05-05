# Workarounds conocidos

## 1. Importar `CLAM_MB` vía `importlib.util`

**Síntoma**: hacer `from model_clam import CLAM_MB` desde mi workspace
falla porque el `__init__.py` del fork de Sebastián importa `timm`, y
`timm` no está siempre instalado en el env de trabajo.

**Causa raíz**: el `__init__.py` carga toda la maquinaria del fork al
importar el paquete, no solo el submódulo que necesito.

**Mitigación**: cargar `model_clam.py` directamente sin pasar por el
package init.

```python
import importlib.util
import sys
from pathlib import Path

CLAM_PATH = Path("/mnt/disco_duro/onco/sebastianDonoso/testMIL/CLAM")

spec = importlib.util.spec_from_file_location(
    "model_clam",
    CLAM_PATH / "model_clam.py",
)
model_clam = importlib.util.module_from_spec(spec)
sys.modules["model_clam"] = model_clam
spec.loader.exec_module(model_clam)

CLAM_MB = model_clam.CLAM_MB
```

**Smoke test**: `./scripts/verify_clam_access.sh` corre exactamente este
patrón y reporta éxito/falla.

**Cuándo NO usar**: cuando el código que voy a correr es `main.py` directo
de Sebastián vía `python main.py ...` — ese entrypoint resuelve sus propios
imports relativos. El workaround es para cuando yo importo CLAM_MB desde
un script propio.

## (espacio para más workarounds según vayan apareciendo)
