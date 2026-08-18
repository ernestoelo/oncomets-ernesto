#!/usr/bin/env python3
"""Cosecha del probe de rotación, LEÍDA EN EL ORDEN QUE MANDA SU PRE-REGISTRO.

El pre-registro (probe_rotacion_etapaA.py, y §9.b de regiones_escaneo/resultados.md)
fija el orden y los criterios ANTES de ver los números:

  1. PRIMERO el grupo C (control positivo, láminas medibles). Si C no reproduce
     su localización a θ = 0, el probe está roto y NO SE LEE NADA MÁS.
  2. Recién después A vs B, mirando DOS cosas juntas:
       - cuánto sube la fracción de ventanas que localizan, y
       - si el θ ganador es CONSISTENTE entre ventanas de la misma lámina.
     θ disperso = ruido, NO rotación. Un vidrio gira entero.

CRITERIO DE «RECUPERADA POR ROTACIÓN», fijado acá y aplicado igual a todas:
  (a) la fracción que localiza sube y llega al criterio del barrido original
      (mayoría de ventanas, >= 0.5), Y
  (b) el θ ganador es consistente entre ventanas: sd <= SD_MAX grados, Y
  (c) el θ no está CLAVADO en el borde del barrido (si lo está, la magnitud no
      se puede leer y la lámina queda «indeterminada», ni recuperada ni no).

SALVEDAD DE DISEÑO, que se declara y no se esconde: el probe elige θ por MÁXIMO
NCC (la alineación físicamente correcta), no por máximo margen. Por eso una
lámina puede BAJAR su fracción al rotar: en su mejor alineación el pico es menos
único. Elegir θ por margen sería elegir el ángulo que más conviene al criterio.
"""
import argparse, json
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parents[1]
BASE = REPO / "sprints/B8_sprint8/anotaciones_patologo/regiones_escaneo"

SD_MAX = 4.0        # grados; sd de θ* entre ventanas de la misma lámina
FRAC_MIN = 0.5      # el criterio del barrido: mayoría de ventanas localizan


def veredicto(r):
    if r.get("frac_theta_en_borde", 0) > 0.5:
        return "indeterminada (θ clavado)"
    if r["frac_localiza_rot"] >= FRAC_MIN and r["theta_best_sd"] <= SD_MAX:
        return "recuperada por rotación"
    if r["theta_best_sd"] > SD_MAX:
        return "no recuperada (θ disperso = ruido)"
    return "no recuperada"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", default=str(BASE / "probe_rotacion.json"))
    ap.add_argument("--out", default=str(BASE / "probe_rotacion_veredicto.csv"))
    args = ap.parse_args()
    import pandas as pd

    res = [r for r in json.load(open(args.probe)) if "error" not in r]
    if not res:
        print("sin resultados legibles"); return
    for r in res:
        r["veredicto"] = veredicto(r)
    df = pd.DataFrame([{k: v for k, v in r.items() if k != "ventanas"} for r in res])

    # ---------- PASO 1: el control positivo, y nada más hasta validarlo ----------
    C = df[df.grupo == "C"]
    print("=" * 74)
    print("PASO 1 — CONTROL POSITIVO (grupo C, láminas medibles)")
    print("=" * 74)
    if C.empty:
        print("El grupo C NO corrió. El pre-registro prohíbe leer el resto.")
        print("NO SE LEE NADA MÁS.")
        return
    for _, r in C.iterrows():
        print(f"  {r.slide_id:<12} localiza θ=0 {r.frac_localiza_theta0:.2f}  "
              f"con rotación {r.frac_localiza_rot:.2f}   "
              f"θ* {r.theta_best_mediano:+.1f}° (sd {r.theta_best_sd:.1f})")
    c0 = float(C.frac_localiza_theta0.mean())
    print(f"\n  fracción media que localiza a θ=0 en el control: {c0:.2f}")
    if c0 < FRAC_MIN:
        print("  ** EL CONTROL NO REPRODUCE SU LOCALIZACIÓN A θ=0 **")
        print("  El probe está roto. NO SE LEE NADA MÁS (pre-registro §9.b).")
        return
    print("  -> el control valida el probe. Se puede leer el resto.")

    # ---------- PASO 2: A vs B ----------
    print("\n" + "=" * 74)
    print("PASO 2 — LOS GRUPOS NO MEDIBLES")
    print("=" * 74)
    nom = {"A": "no medible, silueta >= 0.95", "B": "no medible, silueta < 0.95",
           "C": "medible (control +)"}
    for g in ("A", "B", "C"):
        sub = df[df.grupo == g]
        if sub.empty:
            continue
        print(f"\n  grupo {g} — {nom[g]}  (n={len(sub)})")
        for _, r in sub.sort_values("veredicto").iterrows():
            cl = " CLAVADO" if r.get("frac_theta_en_borde", 0) > 0.5 else ""
            print(f"    {r.slide_id:<12} {r.frac_localiza_theta0:.2f} -> {r.frac_localiza_rot:.2f}   "
                  f"NCC {r.ncc_medio_theta0:.3f} -> {r.ncc_medio_rot:.3f}   "
                  f"θ* {r.theta_best_mediano:+6.1f}° (sd {r.theta_best_sd:4.1f}{cl})   {r.veredicto}")

    print("\n" + "=" * 74)
    print("RECUENTO (criterio: frac >= %.1f Y sd de θ* <= %.1f° Y θ* no clavado)"
          % (FRAC_MIN, SD_MAX))
    print("=" * 74)
    t = df.groupby(["grupo", "veredicto"]).size().unstack(fill_value=0)
    print(t.to_string())
    ab = df[df.grupo.isin(["A", "B"])]
    rec = int((ab.veredicto == "recuperada por rotación").sum())
    print(f"\n  no medibles de la muestra: {len(ab)}")
    print(f"  recuperadas por rotación : {rec}  ({100*rec/len(ab):.0f} %)")
    print(f"  indeterminadas (clavado) : {int((ab.veredicto.str.startswith('indeterminada')).sum())}")
    print(f"  no recuperadas           : {int((ab.veredicto.str.startswith('no recuperada')).sum())}")
    print(f"\n  NCC medio, θ=0 -> rotación: {ab.ncc_medio_theta0.mean():.3f} -> {ab.ncc_medio_rot.mean():.3f}")
    print(f"  |θ*| de las recuperadas: "
          f"{', '.join(f'{v:+.1f}°' for v in ab[ab.veredicto=='recuperada por rotación'].theta_best_mediano)}")

    df.to_csv(args.out, index=False)
    print(f"\n-> {args.out}")


if __name__ == "__main__":
    main()
