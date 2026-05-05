# Werner — entorno

Datos confirmados del servidor. Si algo diverge al primer arranque, anotar
en la tabla "Bitácora" al final.

## Identificación

| Campo | Valor |
|---|---|
| Nombre interno (equipo) | **Werner** |
| Hostname real | `jenny2-System-Product-Name` |
| IP (ejemplo) | `200.1.17.169` |
| Alias SSH (mi laptop) | `environbio` |
| Usuario | `onco` (compartido entre el equipo, no personal) |
| OS | Ubuntu 20.04.6 LTS |
| Kernel | `5.15.0-176-generic` |

## Hardware

- **GPUs**: 4× NVIDIA TITAN RTX (24 GB VRAM c/u)
- **CUDA**: 13.0 (driver compatible con PyTorch 2.11)

## Software

| Componente | Esperado | Cómo verificar |
|---|---|---|
| Python | 3.11 | `python --version` |
| PyTorch | 2.11+cu130 | `python -c "import torch; print(torch.__version__)"` |
| CUDA visible al runtime | 13.0 | `python -c "import torch; print(torch.version.cuda)"` |
| nvidia-smi | OK con 4 dispositivos | `nvidia-smi -L` |

## Conda

- **Activo por default al login**: `(base)`. Pero `base` puede no ser el env
  con PyTorch 2.11+cu130 — confirmar al primer uso.
- **Profile path**: por confirmar (probablemente `/home/onco/miniconda3/`).
- **Para descubrir el env real con CLAM/PyTorch**:
  ```bash
  conda env list
  for env in $(conda env list | awk '/^[a-zA-Z]/ {print $1}'); do
      echo "--- ${env} ---"
      conda run -n "${env}" python -c "import torch; print(torch.__version__)" 2>&1
  done
  ```
- **Override desde laptop**: `ONCOMETS_CONDA_ENV=<name> ssh environbio`.

## Paths críticos

| Path | Tipo | Quién |
|---|---|---|
| `/mnt/disco_duro/onco/sebastianDonoso/testMIL/CLAM/` | read-only | Sebastián Donoso |
| `/mnt/disco_duro/onco/oncologiaEnviron/ernestogamero/` | mi workspace personal | yo |
| `/mnt/disco_duro/onco/oncologiaEnviron/<otros>/` | workspaces de colegas | Eduardo, Sebastián G. |
| `/home/onco/` | home compartido — NO usar para personal | equipo |
| `/mnt/disco_duro/datasets/` (probable) | datasets WSI públicos | compartido |

## Dependencias clave del env (capturar al primer setup)

```
# pendiente: pegar acá output de `pip list` o `conda list`
# del env real con CLAM funcionando, una vez identificado
```

## Bitácora de divergencias

| Fecha | Componente | Esperado | Encontrado | Acción |
|---|---|---|---|---|
| _(vacío)_ | | | | |
