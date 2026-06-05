# Servidor Environ — entorno

Datos confirmados del servidor (migración desde Werner el 19 may 2026).
Reconocimiento completo: `sprints/B4_sprint4/reconocimiento_entorno.md`.
Si algo diverge al primer arranque, anotar en la "Bitácora" al final.

## Identificación

| Campo | Valor |
|---|---|
| Hostname | `administrador-PowerEdge-R740xd` (Dell PowerEdge R740xd) |
| Acceso | VPN oficial Environ + SSH |
| Usuario | `sdonoso` (uid 1008) — **compartido**, no personal |
| OS | Ubuntu 22.04 |
| Kernel | `6.8.0-101-generic` x86_64 |

## Hardware

- **GPU**: 1× NVIDIA RTX A6000 (49 GB VRAM)
- **Driver**: 570.211.01 — **CUDA 12.8**

## SLURM

| Campo | Valor |
|---|---|
| Versión | slurm-wlm 21.08.5 |
| Particiones | **`debug`** (única, default, `infinite`) |
| Nodos | 1 (`administrador-PowerEdge-R740xd`, este mismo host) |

- Toda carga GPU va por **`sbatch`** (skill `@slurm-submission`).
- **Cortesía**: GPU única → revisar `squeue`/`sinfo` antes de enviar. Hay un
  job `conch_fe` (feature extraction CONCH de Sebastián) que puede estar en
  cola — no monopolizar.

## Conda

- **Profile**: `/home/sdonoso/miniconda3/etc/profile.d/conda.sh`.
- **Env activo al login**: `base`. ⚠ **`which python` en `base` está ROTO**
  (apunta a un ADFRsuite python2.7 sin `libpython2.7.so.1.0`).
- **Env de CLAM**: **`clam_latest`** (lo activan todos los `.slurm` de
  `clam_environ/`). Para inspección CPU de `.pt`:
  `/home/sdonoso/miniconda3/envs/clam_latest/bin/python`.
- Otros envs presentes: `conch`, `trident`, `extractor_caracteristicas`,
  `memoriaSebaDonoso` (legacy Werner), `dataset-env`, `report-env`, etc.
- Activar:
  ```bash
  source /home/sdonoso/miniconda3/etc/profile.d/conda.sh
  conda activate clam_latest
  ```

## Paths críticos

| Path | Tipo | Quién |
|---|---|---|
| `/media/administrador/Storage1/sdonoso/clam_environ/` | **read-only** | codebase CLAM de Sebastián |
| `/media/administrador/Storage1/sdonoso/clam_environ/environ/` | **read-only** | datos del proyecto (features `.pt`, CSVs, splits) |
| `/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/` | mi workspace | yo (Ernesto) |
| `/media/administrador/Storage1/sdonoso/clam_testing/` | **NO entrar a escribir** | otra persona |
| `/media/administrador/Storage1/` | montaje (`/dev/sdb`, 15T, 88% usado) | compartido |

## Datos y features (resumen — detalle en `@environ-server`)

- Features CONCH v1: `environ/features/pt_files/` — **~3013 slides, 512-dim** (live 5-jun-2026; crece).
- ResNet legacy: `environ/features_resnet/pt_files/` — 1024-dim.
- **No hay `.pth`**; el sufijo `_pth` = "privado+TCGA+HistAI".
- CSVs: `csv_privado/` (Environ), `csv_tcga/`, `csv_histai/`, `csv/` (combinado).
- Splits: `<task>_100` (privado), `_combined_100`, `_pth_100` (grande).

## Identidad git (CRÍTICO)

El `git config --global` del usuario compartido `sdonoso` apunta a
**Seba Donoso** (`ssebastiandonoso@gmail.com`). En el repo clonado, identidad
**LOCAL** (ya configurada):

```bash
git config --local user.name  "Ernesto Gamero"
git config --local user.email "ernesto.gamero@sansano.usm.cl"
```

## Bitácora de divergencias

| Fecha | Componente | Esperado (doc Werner) | Encontrado (server Environ) | Acción |
|---|---|---|---|---|
| 2026-05-19 | servidor | Werner / jenny2, 4× TITAN RTX | `administrador-PowerEdge-R740xd`, 1× RTX A6000 | doc migrada |
| 2026-05-19 | conda env CLAM | `memoriaSebaDonoso` | `clam_latest` | actualizado en todo el repo |
| 2026-05-19 | `which python` | conda base con torch | ROTO (ADFRsuite py2.7) | siempre activar `clam_latest` |
| 2026-05-19 | features CONCH | 512(TCGA)/1024(Environ) | 512 para todo; 1024 = ResNet legacy | `--embed_dim 512` |
| 2026-05-19 | git global | onco → Sebastián | sdonoso → Seba Donoso | identidad LOCAL = Ernesto |
| 2026-05-19 | git local user.name | "Ernesto Gamero" | era `ernestoelo` | corregido a "Ernesto Gamero" |
