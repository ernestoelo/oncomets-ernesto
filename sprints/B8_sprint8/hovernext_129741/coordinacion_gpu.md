# Pedido de coordinación por la GPU — fase 2 de HoVer-NeXt (job 4998)

> Escrito el **17-ago-2026 17:05**. Todo lo de acá es un snapshot de `squeue` / `scontrol` /
> `nvidia-smi` de esa hora, no una interpretación.
>
> **Para qué sirve este documento**: el job 4998 no está esperando su turno, está bloqueado por una
> configuración de la cola que no se resuelve técnicamente de nuestro lado. Esto es lo que hay que
> mostrarle a Sebastián para pedir la coordinación.

---

## El problema en una línea

**El nodo tiene un solo token de GPU, lo tiene un job declarado a 365 días, y delante nuestro hay
dos jobs más declarados sin límite de tiempo.** Con eso, SLURM no puede estimar cuándo corremos:
su propia estimación es `StartTime = 2027-08-17`.

---

## El snapshot (17-ago 17:05)

```
  JOBID   NAME           USER          ST   TIME     TIME_LIMIT    RAZÓN
   4993   CTXTEST        nschiaffino   PD   0:00     UNLIMITED     Resources
   4997   CTXTESTS       nschiaffino   PD   0:00     UNLIMITED     Priority
   4998   eg_hn129741    sdonoso       PD   0:00     12:00:00      Priority   ← el nuestro
   4991   yolo_dataset   sgaete        R    27:30    8:00:00
   4995   cs_genesel     capstone      R    27:28    365-00:00:00
   4996   llm_validate   gvenegas      R    55:28    365-00:00:00  ← tiene la GPU
```

Nodo: `CPUAlloc = 44/64`, `AllocMem = 212992 / 230000 MB` ⇒ **17 GB de memoria asignable libre**.
GPU: **43.833 / 49.140 MiB usados**, utilización 74-100 %.

## Quién tiene qué

| Job | Usuario | Recursos | `TimeLimit` | ¿Tiene la GPU? |
|---|---|---|---|---|
| 4996 `llm_validate` | `gvenegas` | 8 CPU, 24 GB, **`gres:gpu:1`** | **365 días** | **sí** — un `VLLM::EngineCore` con **38 GB** de VRAM |
| 4995 `cs_genesel` | `capstone` | 20 CPU, **120 GB** | **365 días** | no (pero se lleva la mitad de la RAM del nodo) |
| 4991 `yolo_dataset` | `sgaete` | 16 CPU, 64 GB | 8 h | no |
| 4993 `CTXTEST` | `nschiaffino` | 12 CPU, 64 GB, **`gres:gpu:1`** | **UNLIMITED** | pendiente, **delante nuestro** |
| 4997 `CTXTESTS` | `nschiaffino` | 4 CPU, 32 GB, **`gres:gpu:1`** | **UNLIMITED** | pendiente, **delante nuestro** |

Fuera de SLURM hay además dos procesos en la GPU: un `uvicorn` de `root` (5,1 GB, 7 días
corridos) y un script de `bprieto` (0,6 GB).

## Por qué no se arregla de nuestro lado

1. **El token de GPU es uno solo** (`Gres=gpu:1`). No se comparte por SLURM: quien lo toma lo tiene
   hasta que termina. Lo tiene 4996.
2. **Somos terceros en la fila por ese token**, detrás de 4993 y 4997.
3. **El backfill no nos puede colar antes.** Para adelantar un job chico, SLURM necesita saber
   cuándo terminan los de más prioridad. Con `TimeLimit = UNLIMITED` en 4993 y 4997 esa ventana no
   se puede calcular, así que no hay backfill posible. **Achicar nuestro job no nos adelanta.**
4. Lo único que sí controlamos es nuestro pedido de **96 GB** (ver abajo), y eso solo importa
   *después* de que se libere la GPU.

## Qué pedimos

No pedimos que nadie cancele nada. Lo que destraba esto es información:

1. **¿Cuánto va a durar realmente 4996 (`gvenegas`)?** Es un servidor de inferencia vLLM declarado
   a 365 días. Si es una validación de unas horas, alcanza con saberlo. Si es un servicio que va a
   quedar levantado, entonces **el nodo no tiene GPU disponible para nadie más** y eso hay que
   decidirlo a nivel de equipo, no de job.
2. **¿4993 y 4997 (`nschiaffino`) tienen que ser `UNLIMITED`?** Si declararan un `--time` real,
   el backfill vuelve a funcionar para todos, no solo para nosotros. Es el cambio de mayor impacto
   y el más barato.
3. **Nuestro job son ~2-3 h de GPU y ya está encolado sin monopolizar** (`--time=12:00:00`, entró
   último a propósito). No necesita prioridad, necesita que la fila avance.

## Nuestro propio pedido de memoria, para no pedir sin dar

`4998` pide **96 GB**. Es defendible pero no es intocable: el pico lo fija el post-proceso, con
`pp_workers = 14` sobre `pp_tiling = 8` (64 baldosas de ~50 Mpx; cada worker materializa BCB +
clases en `float32`, del orden de 3-5 GB). Subiendo `pp_tiling` y bajando `pp_workers` el pico baja
casi proporcional, a costo de reloj.

**Si la coordinación no destraba la cola, la contraoferta es re-encolar con `pp_tiling 16`,
`pp_workers 8` y `--mem 32G`.** No nos adelanta (ver punto 3 de arriba), pero deja de exigir que
terminen dos de los tres jobs corriendo para que quepamos.

## Qué NO se afirma

- **No se afirma que nadie esté haciendo mal uso del nodo.** Un `TimeLimit` largo es una
  declaración de tope, no una predicción: los tres jobs pueden terminar en horas. Lo que se afirma
  es que, **declarado así, SLURM no puede planificar** y nosotros no podemos estimar nada.
- **No se midió** cuánta memoria consume de verdad nuestro job: los 3-5 GB por worker son una
  cuenta sobre la forma de los arrays, no una medición. La corrida real es la que lo diría.
- El `StartTime = 2027` **no es una predicción de SLURM**, es lo que devuelve cuando no puede
  calcular. No significa que vayamos a esperar un año.
