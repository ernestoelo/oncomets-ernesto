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
- **CUDA runtime visto por PyTorch**: 12.8 (validado 5 mayo 2026)

## Software (validado 5 mayo 2026)

| Componente | Valor real | Cómo verificar |
|---|---|---|
| Python | 3.11 | `python --version` |
| PyTorch | **2.10.0+cu128** | `python -c "import torch; print(torch.__version__)"` |
| CUDA visible al runtime | **12.8** | `python -c "import torch; print(torch.version.cuda)"` |
| nvidia-smi | OK con 4 dispositivos | `nvidia-smi -L` |

> Nota: la memoria del proyecto decía `2.11+cu130`. La realidad en Werner
> al 5 mayo 2026 es `2.10.0+cu128`. La memoria estaba desactualizada y se
> corrigió en esta misma fecha (ver bitácora).

## Conda

- **Profile path real**: `/home/onco/miniconda3/etc/profile.d/conda.sh`.
- **Env activo por default al login**: `(base)`. **`base` NO tiene torch**
  — no usar para CLAM.
- **Env de trabajo confirmado**: **`memoriaSebaDonoso`**. Contiene
  `torch==2.10.0+cu128` y todas las deps necesarias para correr `main.py`
  de Sebastián. Usar este env para todo lo del Sprint 3 B3.
- Activar manualmente:
  ```bash
  source /home/onco/miniconda3/etc/profile.d/conda.sh
  conda activate memoriaSebaDonoso
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

> Nota sobre `/mnt/disco_duro/onco/oncologiaEnviron/`: es un **repo git**
> del equipo, pero su `.gitignore` excluye toda la carpeta `ernestogamero/`.
> Mi trabajo bajo `ernestogamero/oncomets-ernesto/` no afecta al repo padre.

## Dependencias clave del env (capturar al primer setup)

```
# pendiente: pegar acá output de `pip list` o `conda list -n memoriaSebaDonoso`
# en próxima sesión
```

## Bitácora de divergencias

| Fecha | Componente | Esperado | Encontrado | Acción |
|---|---|---|---|---|
| 2026-05-05 | conda env activo | `base` con torch 2.11+cu130 | `base` sin torch; el env real con torch es `memoriaSebaDonoso` (torch 2.10.0+cu128) | Documentado en este archivo; default de `bootstrap_werner.sh` cambiado a `memoriaSebaDonoso` |
| 2026-05-05 | import CLAM_MB | requería workaround `importlib.util` | import directo `from models.model_clam import CLAM_MB` funciona en `memoriaSebaDonoso` | Workaround marcado como fallback en `docs/workarounds.md` |
