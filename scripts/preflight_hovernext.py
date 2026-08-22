"""preflight_hovernext.py — invariantes que tienen que valer ANTES de gastar GPU.

Workaround G del CLAUDE.md aplicado a la fase 2 del plan del 17-ago: el patron es
obligatorio en cualquier `.slurm`, no solo en los de entrenamiento. Acá el crash caro no es
un `topk` tardío sino: correr 40 min de inferencia y descubrir que `--keep_raw` no estaba y
el BCB-map se borró, o que `--metric mpq` no tiene clave en el JSON de umbrales de Lizard.

Todo lo que valida sale de `sprints/B8_sprint8/hovernext_129741/auditoria_codigo.md`.
Falla RUIDOSO y con exit != 0 para que el `.slurm` muera en segundos.

Uso:
  <env hovernext>/bin/python scripts/preflight_hovernext.py --cp lizard_convnextv2_tiny \
      --input <wsi> --output-root <dir> --metric f1 --keep-raw 1
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

HN = Path("/media/administrador/Storage1/sdonoso/clam_testing2/hover_next_reference")

fallos: list[str] = []
avisos: list[str] = []


def chk(cond, msg):
    (avisos if cond is None else fallos).append(msg) if not cond else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cp", required=True, help="lista separada por comas, igual que main.py")
    ap.add_argument("--input", required=True)
    ap.add_argument("--output-root", required=True)
    ap.add_argument("--metric", default="f1")
    ap.add_argument("--keep-raw", type=int, default=1)
    ap.add_argument("--sin-raw-a-proposito", action="store_true",
                    help="declara que --keep_raw=0 es una DECISION, no un olvido. Sin este "
                         "flag, keep_raw=0 sigue siendo FALLA (que es lo que protege contra "
                         "correr 40 min y descubrir que el raw no se guardo). Con el, baja a "
                         "AVISO. Lo usa B1, que barre 11 laminas y no necesita el raw: son "
                         "~142 MB por lamina en vez de ~10,5 GB.")
    a = ap.parse_args()

    print("=" * 70)
    print("PREFLIGHT HoVer-NeXt")
    print("=" * 70)

    # --- 1. la lamina existe, TIENE UNA EXTENSION QUE HoVer-NeXt ACEPTA, y openslide la abre ---
    if not os.path.exists(a.input):
        fallos.append(f"la WSI no existe: {a.input}")
    else:
        # data_utils.py:234-242 es una whitelist de extension, y es lo PRIMERO que corre
        # en WholeSlideDataset. El job 4998 la choco a los 29 s con un .bif. Que openslide
        # abra la lamina NO alcanza: hay que pasar tambien esta puerta.
        ext = os.path.splitext(a.input)[1].lower()
        aceptadas = (".svs", ".tif", ".czi", ".mrxs")
        chk(ext in aceptadas,
            f"HoVer-NeXt rechaza la extension '{ext}' (data_utils.py:234-242, acepta "
            f"{', '.join(aceptadas)}). Usar el symlink .tif del shim; openslide detecta "
            f"el formato leyendo el archivo, no por el nombre.")
        try:
            import openslide
            sl = openslide.OpenSlide(a.input)
            w, h = sl.dimensions
            mpp = sl.properties.get("openslide.mpp-x")
            assoc = list(sl.associated_images.keys())
            print(f"[ok] WSI {w}x{h}  mpp-x={mpp}  associated={assoc}")
            if "thumbnail" not in assoc:
                avisos.append(
                    "la WSI NO expone 'thumbnail' -> data_utils.py:297 NO filtra fondo: "
                    "se tesela el LIENZO ENTERO. Esperar decenas de minutos, no ~2 min.")
        except Exception as e:
            fallos.append(f"openslide no pudo abrir la WSI: {e!r}")

    # --- 2. los pesos estan donde main.py los busca, y son coherentes ---
    cps = [c.strip() for c in a.cp.split(",") if c.strip()]
    if not cps:
        fallos.append("--cp vacio")
    pannuke_flags = set()
    for c in cps:
        d = HN / c
        if not (d / "params.toml").exists():
            fallos.append(f"faltan pesos o params.toml: {d}")
            continue
        if not (d / "train" / "best_model").exists():
            fallos.append(f"falta el checkpoint {d}/train/best_model")
            continue
        import toml
        p = toml.load(d / "params.toml")
        pannuke_flags.add(p["dataset"] == "pannuke")
        print(f"[ok] {c}: dataset={p['dataset']} cls={p['out_channels_cls']} "
              f"inst={p['inst_channels']} lambda={p.get('loss_lambda')}")

        # --- 3. la clave de umbrales que get_pp_params va a pedir EXISTE ---
        js = ("pannuke_test_param_dict.json" if p["dataset"] == "pannuke"
              else "liz_test_param_dict.json")
        dt = json.loads((d / js).read_text())
        if f"best_fg_{a.metric}" not in dt:
            fallos.append(
                f"{c}: --metric '{a.metric}' no tiene clave 'best_fg_{a.metric}' en {js} "
                f"(disponibles: {sorted(k for k in dt if k.startswith('best_fg_'))}) "
                f"-> get_pp_params reventaria con KeyError DESPUES de inferir")
        if p["dataset"] != "pannuke" and not (d / "mit_test_param_dict.json").exists():
            fallos.append(f"{c}: falta mit_test_param_dict.json y post_process llama "
                          f"get_pp_params(mit_eval=True) -> FileNotFoundError")

    if len(pannuke_flags) > 1:
        fallos.append("se estan mezclando pesos de pannuke y de lizard en un mismo --cp: "
                      "distinto nº de clases y distinta magnificacion de crop")

    # --- 4. el flag que decide si sobrevive el insumo de la fase 2.b ---
    if not a.keep_raw and not a.sin_raw_a_proposito:
        fallos.append("--keep_raw esta APAGADO: main.py:121-126 borra los zarr _inst/_cls "
                      "al terminar y la fase 2.b (BCB-map / raw class) se queda sin insumo. "
                      "Si es a proposito, pasar --sin-raw-a-proposito")
    elif not a.keep_raw:
        avisos.append("--keep_raw APAGADO A PROPOSITO: NO van a quedar los zarr _inst/_cls, "
                      "asi que esta salida no sirve para preguntar si un nucleo fue "
                      "segmentado-pero-mal-clasificado (eso es A0 y ya se contesto sobre la "
                      "129741). Ahorra ~10,4 GB por lamina.")
    else:
        print("[ok] --keep_raw activo: sobreviven _inst.zip (BCB) y _cls.zip (raw class)")

    # --- 5. salida escribible y bajo containment ---
    out = Path(a.output_root)
    if "clam_testing2" not in str(out.resolve()):
        fallos.append(f"la salida cae FUERA del containment clam_testing2/: {out}")
    try:
        out.mkdir(parents=True, exist_ok=True)
        (out / ".w").write_text("x"); (out / ".w").unlink()
        print(f"[ok] salida escribible: {out}")
    except Exception as e:
        fallos.append(f"no se puede escribir la salida {out}: {e!r}")

    # --- 6. GPU: inference.py:87-90 aborta sin cuda ---
    try:
        import torch
        if not torch.cuda.is_available():
            fallos.append("torch no ve GPU, e inference.py:87-90 aborta explicitamente sin cuda")
        else:
            free, total = torch.cuda.mem_get_info()
            print(f"[ok] GPU visible: {torch.cuda.get_device_name(0)} "
                  f"{free/2**30:.1f} GB libres de {total/2**30:.1f}")
            if free / 2**30 < 4:
                avisos.append(f"quedan {free/2**30:.1f} GB de GPU libres: bajar --batch_size "
                              f"o esperar a que se descongestione")
    except Exception as e:
        fallos.append(f"no se pudo consultar torch/cuda: {e!r}")

    print("-" * 70)
    for w in avisos:
        print(f"[AVISO] {w}")
    for f in fallos:
        print(f"[FALLA] {f}")
    if fallos:
        print(f"\nPREFLIGHT FALLIDO ({len(fallos)} fallas). No se gasta GPU.")
        sys.exit(1)
    print("\nPREFLIGHT OK")


if __name__ == "__main__":
    main()
