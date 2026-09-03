"""b9_galeria_regiones_epi.py — una región epitelial y una de estroma, con sus núcleos (B9)

Hace visible el número del control positivo del eje 4: HoVer-NeXt llama epitelial al 90 % de
los núcleos dentro de las regiones que el patólogo marcó como epitelio, y a casi ninguno
dentro de las que marcó como estroma (`results/b9_nucleos/regiones_epi_estroma.csv`). El
número dice que separa; esta figura muestra qué separa.

Cuatro recortes lado a lado, dos de cada grupo, con los núcleos de HoVer-NeXt pintados
**epitelial contra conectivo** encima del tejido y `f_epi` impreso en cada uno. Los dos
colores son los del propio HoVer-NeXt (`hover_next_reference/src/constants.py`: verde `epi`,
naranja `con`), no una paleta nuestra.

Tres cosas que gobiernan el código:

  - `regiones_epi_estroma.csv` NO trae coordenadas. Los polígonos se re-derivan con
    `cargar_regiones` de `b9_epitelio_estroma.py`, y el join contra el CSV es **por
    posición**: sus filas están en el orden que devuelve esa función dentro de cada lámina
    (verificado en las doce, clase a clase).
  - Los centroides y las clases salen del **npz** (`results/b9_nucleos/<slide>_nucleos.npz`),
    así que no hace falta `zarr` y todo corre en `clam_latest`.
  - Se dibujan sólo los núcleos cuyo **centroide cae dentro del polígono**. El `f_epi` que se
    imprime es el del CSV, que se calculó sobre el ráster de celdas de 8 px del mismo
    polígono: son dos caminos al mismo número y el `.json` deja anotada la diferencia.

Se eligen las regiones con más núcleos entre las de offset **alineado**, una por lámina, para
que los cuatro paneles no salgan de la misma.

Env `clam_latest`: los `.bif` sólo abren con la `libopenslide` parchada (workaround K).

  CUDA_VISIBLE_DEVICES="" /home/sdonoso/miniconda3/envs/clam_latest/bin/python \
      scripts/b9_galeria_regiones_epi.py
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw

REPO = Path("/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto")
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

from b9_epitelio_estroma import OFF, cargar_regiones                        # noqa: E402
from scripts.galeria_mitosis_12 import fuente                               # noqa: E402

WSI_DIR = Path("/media/administrador/Storage1/sdonoso/wsi")
NUC = REPO / "results/b9_nucleos"
OUT = REPO / "sprints/B9_sprint9/presentacion_b9/assets/regiones_epi.png"

MPP = 0.465
EPITELIAL, CONECTIVO = 2, 6          # `hover_next_reference/src/constants.py:31-39`

TILE = 560                           # lado del panel, px
MARGEN = 0.06                        # margen alrededor del bbox del polígono
N_POR_GRUPO = 2

# Los colores del propio HoVer-NeXt, no una paleta nuestra.
C_EPI, C_CON = (0, 255, 0), (255, 179, 102)
FONDO, TITULO, CUERPO = (255, 255, 255), (0x1A, 0x1A, 0x2E), (0x1B, 0x4F, 0x8C)
BLANCO = (255, 255, 255)


def elegir(csv_path: Path) -> list[dict]:
    """Las regiones con más núcleos de cada grupo, entre las de offset ALINEADO.

    Una por lámina: dos paneles de la misma lámina se leerían como una sola evidencia.
    """
    d = pd.read_csv(csv_path)
    d = d[d["alineada"]].copy()
    d["n"] = d["n_epi"] + d["n_conn"]
    d["fila"] = d.groupby("slide").cumcount()          # posición dentro de la lámina
    sel = []
    for grupo in ("epitelio", "estroma"):
        g = d[d["grupo"] == grupo].sort_values("n", ascending=False)
        vistas = set()
        for _, r in g.iterrows():
            if r["slide"] in vistas:
                continue
            vistas.add(r["slide"])
            sel.append(r.to_dict())
            if len(vistas) == N_POR_GRUPO:
                break
    return sel


def panel(sl, poly: np.ndarray, cx, cy, clase) -> tuple[Image.Image, int, int, float]:
    """El recorte del bbox del polígono, con su contorno y los núcleos de adentro.

    Devuelve (imagen, n_epi dibujados, n_con dibujados, µm por píxel del panel).
    """
    x0, y0 = poly.min(axis=0)
    x1, y1 = poly.max(axis=0)
    mx, my = (x1 - x0) * MARGEN, (y1 - y0) * MARGEN
    x0, y0, x1, y1 = x0 - mx, y0 - my, x1 + mx, y1 + my
    bw, bh = max(x1 - x0, 1.0), max(y1 - y0, 1.0)

    ds = max(bw, bh) / TILE
    lvl = sl.get_best_level_for_downsample(max(ds, 1.0))
    dl = sl.level_downsamples[lvl]
    im = sl.read_region((int(x0), int(y0)), lvl,
                        (max(1, int(bw / dl)), max(1, int(bh / dl)))).convert("RGB")
    esc = min(TILE / bw, TILE / bh)
    pw, ph = max(1, int(round(bw * esc))), max(1, int(round(bh * esc)))
    im = im.resize((pw, ph), Image.LANCZOS)

    def a_panel(x, y):
        return (x - x0) * esc, (y - y0) * esc

    # Máscara del polígono a resolución del panel: es la que decide qué núcleo se dibuja.
    m = Image.new("1", (pw, ph), 0)
    ImageDraw.Draw(m).polygon([a_panel(px, py) for px, py in poly], fill=1)
    dentro_mask = np.asarray(m, dtype=bool)

    u, v = a_panel(cx, cy)
    ok = (u >= 0) & (u < pw) & (v >= 0) & (v < ph)
    ui, vi = u[ok].astype(int), v[ok].astype(int)
    cl = clase[ok]
    dentro = dentro_mask[vi, ui]

    d = ImageDraw.Draw(im)
    r = max(2.0, 6.0 * esc)
    n_epi = n_con = 0
    for uu, vv, cc in zip(ui[dentro], vi[dentro], cl[dentro]):
        if cc == EPITELIAL:
            col, n_epi = C_EPI, n_epi + 1
        elif cc == CONECTIVO:
            col, n_con = C_CON, n_con + 1
        else:
            continue
        d.ellipse([uu - r, vv - r, uu + r, vv + r], outline=col, width=2)

    # El contorno va con reborde oscuro debajo: en blanco a secas se pierde sobre el
    # tejido pálido, que es justo el caso de las regiones de estroma.
    cerrado = [a_panel(px, py) for px, py in poly] + [a_panel(poly[0, 0], poly[0, 1])]
    d.line(cerrado, fill=TITULO, width=6)
    d.line(cerrado, fill=BLANCO, width=3)

    # Barra de escala: 100 µm, con su longitud recomputada para el µm/px de ESTE panel.
    um_px = MPP / esc
    L = int(round(100.0 / um_px))
    if L < pw - 30:
        bx, by = pw - L - 14, ph - 20
        d.rectangle([bx, by, bx + L, by + 5], fill=BLANCO, outline=TITULO)
        d.text((bx, by - 17), "100 µm", fill=TITULO, font=fuente(13, bold=True),
               stroke_width=2, stroke_fill=BLANCO)

    lienzo = Image.new("RGB", (TILE, TILE), FONDO)
    lienzo.paste(im, ((TILE - pw) // 2, (TILE - ph) // 2))
    return lienzo, n_epi, n_con, um_px


def hoja(paneles, path):
    """Los cuatro paneles en un renglón, con el grupo como cabecera y `f_epi` bajo cada uno."""
    pad, h_cab, h_pie = 12, 30, 58
    n = len(paneles)
    W = pad + n * (TILE + pad)
    H = h_cab + TILE + h_pie
    im = Image.new("RGB", (W, H), FONDO)
    d = ImageDraw.Draw(im)
    f_cab, f_lab, f_min = fuente(19, bold=True), fuente(17, bold=True), fuente(15)

    for k, p in enumerate(paneles):
        x = pad + k * (TILE + pad)
        d.text((x, 4), "el patólogo marcó %s" % p["grupo"].upper(),
               fill=TITULO if p["grupo"] == "epitelio" else CUERPO, font=f_cab)
        im.paste(p["img"], (x, h_cab))
        y = h_cab + TILE + 6
        d.text((x, y), "f_epi = %.2f" % p["f_epi"], fill=TITULO, font=f_lab)
        d.text((x + 130, y + 2),
               "%d epiteliales · %d conectivos" % (p["n_epi"], p["n_conn"]),
               fill=CUERPO, font=f_min)
        d.text((x, y + 24), "%s · %s" % (p["slide"], p["clase"]), fill=CUERPO, font=f_min)

    # Leyenda de los dos colores, que son los de HoVer-NeXt.
    lx = pad + (n - 1) * (TILE + pad) + TILE - 250
    ly = h_cab + TILE + 30
    for dx, col, txt in ((0, C_EPI, "epitelial"), (120, C_CON, "conectivo")):
        d.ellipse([lx + dx, ly, lx + dx + 12, ly + 12], outline=col, width=3)
        d.text((lx + dx + 18, ly - 2), txt, fill=CUERPO, font=f_min)
    im.save(path, optimize=True)
    return im.size


def main():
    import openslide
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)

    sel = elegir(NUC / "regiones_epi_estroma.csv")
    paneles, meta = [], []
    for r in sel:
        slide = r["slide"]
        off = json.loads((Path(OFF) / f"offset_{slide}.json").read_text())
        regs = cargar_regiones(slide, off["dx"], off["dy"])
        nombre, grupo, poly = regs[int(r["fila"])]
        if nombre != r["clase"] or grupo != r["grupo"]:
            raise SystemExit(f"{slide}: la fila {r['fila']} del CSV dice {r['clase']}/"
                             f"{r['grupo']} y cargar_regiones da {nombre}/{grupo}")
        z = np.load(NUC / f"{slide}_nucleos.npz")
        sl = openslide.OpenSlide(str(WSI_DIR / slide / f"{slide}.bif"))
        img, n_epi, n_con, um_px = panel(sl, poly, z["cx"].astype(np.float64),
                                         z["cy"].astype(np.float64), z["clase"])
        sl.close()
        paneles.append(dict(img=img, slide=slide, clase=nombre, grupo=grupo,
                            f_epi=float(r["f_epi"]), n_epi=int(r["n_epi"]),
                            n_conn=int(r["n_conn"])))
        meta.append(dict(slide=slide, clase=nombre, grupo=grupo, f_epi=float(r["f_epi"]),
                         n_epi_csv=int(r["n_epi"]), n_conn_csv=int(r["n_conn"]),
                         n_epi_dibujados=n_epi, n_conn_dibujados=n_con,
                         um_por_px_panel=round(um_px, 3),
                         area_um2=float(r["area_um2"])))
        print(f"[ok] {slide:<12} {grupo:<9} {nombre:<15} f_epi={r['f_epi']:.3f}  "
              f"CSV {int(r['n_epi'])}/{int(r['n_conn'])}  dibujados {n_epi}/{n_con}")

    # Los paneles van epitelio primero, que es como se lee la comparación.
    paneles.sort(key=lambda p: (p["grupo"] != "epitelio", -p["f_epi"]))
    size = hoja(paneles, args.out)
    print(f"  escrito: {args.out}  {size[0]}x{size[1]}")

    Path(args.out).with_suffix(".json").write_text(json.dumps(dict(
        que_es="control positivo del eje 4: fracción de núcleos que HoVer-NeXt llama "
               "epiteliales dentro de las regiones que el patólogo marcó como epitelio y "
               "como estroma",
        f_epi="del CSV, calculado sobre el ráster de celdas de 8 px del polígono. Los "
              "`n_*_dibujados` cuentan centroides dentro del mismo polígono: son dos "
              "caminos al mismo número, no dos números distintos",
        colores=dict(epitelial=list(C_EPI), conectivo=list(C_CON),
                     fuente="hover_next_reference/src/constants.py, la paleta del propio "
                            "HoVer-NeXt"),
        seleccion=f"las {N_POR_GRUPO} regiones con más núcleos de cada grupo entre las de "
                  f"offset alineado, una por lámina",
        procedencia=dict(csv="results/b9_nucleos/regiones_epi_estroma.csv",
                         npz="results/b9_nucleos/<slide>_nucleos.npz",
                         poligonos="cargar_regiones de scripts/b9_epitelio_estroma.py, join "
                                   "POSICIONAL contra el CSV",
                         offsets="sprints/B8_sprint8/anotaciones_patologo/offset_<slide>.json"),
        paneles=meta), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
