#!/usr/bin/env python
"""Diagnóstico de O1 del B10: ¿cuánto mueve confinar a su región anotada las dos láminas con dos
regiones de escaneo (129741 y B25-158899)?

El pre-registro de O1 no declaró el universo para estas dos, y el driver usó la lámina entera.
Esto NO es un brazo nuevo ni reemplaza a `b10_grado_sin_marca.py`: mide cuánto se movería el
resultado publicado, para declararlo en `grado_sin_marca/resultados.md` §7.a.

Reusa `escalera()`, `cargar_offset()` y `marcas_de_grado()` del driver sin tocarlos, y el
intervalo de `cruce_94_marcas.REGION_ANOTADA`, que fijó el B9. Lo único que se repite son las
líneas que arman `epi` y `pct` (driver :238-283), para poder cambiar `sel`. **La fila `lamina`
tiene que reproducir `escalera.csv`** (129741: 2 · 4 · 8 en N = 200 · 500 · 2000), o el
diagnóstico no vale: se verifica abajo y falla ruidosamente.

  /home/sdonoso/miniconda3/envs/pruebas/bin/python scripts/b10_grado_region_diag.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path("/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto")
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))
import b10_grado_sin_marca as g                                   # noqa: E402
from scripts.cruce_94_marcas import REGION_ANOTADA                # noqa: E402

ESC = pd.read_csv(REPO / "results/b10_grado_sin_marca/escalera.csv")
ESC = ESC[(ESC.brazo == "A_lamina_entera") & (ESC.desc == "percentil")]


def main():
    tol_px = g.TOL_VECINDAD_UM / g.MPP
    print("O1, diagnóstico de universo: lámina entera (publicado) contra región anotada")
    print("unidad: marcas de grado recuperadas entre los N núcleos epiteliales más grandes; "
          "carga en mm2 (unión de parches de 256 px)\n")
    for slide in REGION_ANOTADA:
        z = np.load(REPO / "results/b9_nucleos" / f"{slide}_nucleos.npz")
        cls, area_px = z["clase"], z["area_px"].astype(float)
        cx, cy = z["cx"].astype(float), z["cy"].astype(float)
        mpp = float(z["mpp"])
        area_um2 = area_px * mpp * mpp
        epi = (cls == g.EPITELIAL) & (area_px > 0)
        pct = np.full(len(cls), np.nan)
        ae = area_um2[epi]
        orden = np.argsort(ae, kind="stable")
        r = np.empty(len(ae)); r[orden] = np.arange(len(ae))
        pct[np.nonzero(epi)[0]] = 100.0 * r / max(len(ae) - 1, 1)

        dx, dy, alineada = g.cargar_offset(slide)
        marcas = g.marcas_de_grado(slide, dx, dy)
        mxy = np.asarray([p for _, _, p in marcas], float)
        lo, hi = REGION_ANOTADA[slide]
        en_reg = (cy >= lo) & (cy < hi)
        m_in = int(((mxy[:, 1] >= lo) & (mxy[:, 1] < hi)).sum())
        if m_in != len(mxy):
            raise SystemExit(f"{slide}: {len(mxy) - m_in} marcas fuera de REGION_ANOTADA")
        print(f"{slide}  alineada={alineada}  región y ∈ [{lo}, {hi})  marcas {len(mxy)} "
              f"(todas en la región)  epiteliales {int(epi.sum())}, en la región "
              f"{int((epi & en_reg).sum())}")
        for nombre, sel in (("lamina", epi), ("region", epi & en_reg)):
            filas, n_res, n_cand = g.escalera(cx, cy, pct, sel, mxy, tol_px, g.ESCALERA)
            if nombre == "lamina":
                pub = ESC[ESC.slide == slide].set_index("N")["recall"]
                for f in filas:
                    if f["N"] in pub.index and pub[f["N"]] != f["recall"]:
                        raise SystemExit(f"{slide}: N={f['N']} da {f['recall']} y "
                                         f"escalera.csv dice {pub[f['N']]}: no reproduce")
            print(f"  {nombre:<7} candidatos {n_cand:>6}  alcanzables {n_res:>3}   " +
                  "  ".join(f"N{f['N']}: {int(f['recall'])} ({f['carga_mm2']:.1f} mm2)"
                            for f in filas if f["N"] in (200, 500, 2000)))
    print("\nla fila `lamina` reproduce escalera.csv en los dos casos")


if __name__ == "__main__":
    main()
