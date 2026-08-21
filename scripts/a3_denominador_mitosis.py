#!/usr/bin/env python
"""a3_denominador_mitosis.py — el denominador ALCANZABLE del cruce de la fase B1.

Patron P2.a del CLAUDE.md: el techo de una prueba restringida se mide ANTES de correr la
etapa cara. Aca la etapa cara es HoVer-NeXt sobre las 11 laminas; el filtro barato que va
delante es la alineacion QuPath -> openslide de A3. Una marca de `Mitosis` cuyo centroide
NO cae sobre un parche extraido no la puede recuperar nadie, por bueno que sea el detector.

Entonces esto contesta, sin GPU y sin re-correr nada: **con el offset adoptado por lamina,
cuantas de las 94 marcas de Mitosis caen sobre un parche del h5**. Ese numero es el
denominador honesto de B1.

Unidad: **marcas** (94 en las 12 laminas). NO parches (113 quedan tocados por alguna marca,
porque una marca puede tocar dos parches y dos marcas pueden compartir uno) ni detecciones.

Uso:
  <clam_latest>/bin/python scripts/a3_denominador_mitosis.py
"""
import json
import os
import sys

import h5py
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "scripts"))
from alinear_anotaciones_qupath import cargar_anotaciones   # noqa: E402

OFFSETS = os.path.join(REPO, "sprints/B8_sprint8/anotaciones_patologo")
ANOT = "/media/administrador/Storage1/sdonoso/anotaciones"                       # ajeno, RO
H5 = "/media/administrador/Storage1/sdonoso/clam_environ/environ/features/h5_files"  # ajeno, RO

# ordenadas por numero de marcas, como en la tabla de hallazgos_exploracion.md §4
SLIDES = ["129741", "126504", "128194", "124729", "124806", "B25-158899",
          "144317", "164001", "106552", "103762", "109609", "110616"]


def main():
    tot_m = tot_ok = 0
    filas = []
    for s in SLIDES:
        j = json.load(open(os.path.join(OFFSETS, f"offset_{s}.json")))
        dx, dy, ps = j["dx"], j["dy"], j["patch_size"]
        anot = cargar_anotaciones(os.path.join(ANOT, f"{s}.bif - GDT.geojson"))
        with h5py.File(os.path.join(H5, f"{s}.h5"), "r") as f:
            coords = f["coords"][:].astype(int)
        celdas = set(map(tuple, (coords // ps).tolist()))
        marcas = [p for c, p in anot if c == "Mitosis"]
        ok = sum(1 for p in marcas
                 if tuple(((p.mean(0) + np.array([dx, dy])) // ps).astype(int).tolist()) in celdas)
        tot_m += len(marcas)
        tot_ok += ok
        filas.append(dict(slide_id=s, marcas=len(marcas), sobre_parche=ok, dx=dx, dy=dy,
                          verif_a=j.get("verif_a_en_offset_adoptado"),
                          n_anotaciones=j["n_anotaciones"]))

    print(f"{'lamina':12s} {'marcas':>7s} {'sobre parche':>13s} {'%':>6s}   (a) todas las anot.")
    for r in filas:
        pct = 100 * r["sobre_parche"] / r["marcas"] if r["marcas"] else float("nan")
        print(f"{r['slide_id']:12s} {r['marcas']:>7d} {r['sobre_parche']:>13d} {pct:>5.0f}%"
              f"   {r['verif_a']}/{r['n_anotaciones']}")
    print(f"{'TOTAL':12s} {tot_m:>7d} {tot_ok:>13d} {100 * tot_ok / tot_m:>5.0f}%")
    print("\nRECORDATORIO: las marcas son positivos PARCIALES. 94 es 'las marcadas',")
    print("no 'las que hay', y nada de esto es precision.")

    dest = os.path.join(OFFSETS, "denominador_mitosis_12.json")
    json.dump({"unidad": "marcas de Mitosis (no parches, no detecciones)",
               "total_marcas": tot_m, "sobre_parche": tot_ok, "por_lamina": filas,
               "aviso": "positivos parciales: 94 son las marcadas, no las que hay"},
              open(dest, "w"), indent=2, ensure_ascii=False)
    print(f"\nescrito: {dest}")


if __name__ == "__main__":
    main()
