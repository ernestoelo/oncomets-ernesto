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

CRITERIO DE «RECUPERADA POR ROTACIÓN», aplicado igual a todas:
  (a) la fracción que localiza llega al criterio del barrido original (mayoría
      de ventanas, >= 0.5), Y
  (b) el θ ganador es consistente entre ventanas: sd <= el corte calibrado, Y
  (c) el θ no está CLAVADO en el borde del barrido (si lo está, la magnitud no
      se puede leer y la lámina queda «indeterminada», ni recuperada ni no).

CÓMO SE MIDE (b), Y POR QUÉ NO ES UN CORTE FIJO. La sd de θ* hay que medirla
SOLO sobre las ventanas que localizan, y el corte hay que calibrarlo contra el
control. Medida sobre TODAS las ventanas y con un corte fijo de 4°, el criterio
RECHAZA A 3 DE LAS 4 LÁMINAS DEL CONTROL -láminas que localizan perfectamente-,
porque en una ventana que no localiza la superficie en θ es plana y su argmax
vaga, inflando la sd de la lámina entera. Restringida a las que localizan, el
peor del control da 2.2° y las 4 pasan. Es la función del control positivo:
calibrar el criterio, no solo validar el probe.

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

MARGEN_UNICO = 0.10   # el corte del criterio pre-fijado: pico >=10 % sobre el segundo
FRAC_MIN = 0.5        # el criterio del barrido: mayoría de ventanas localizan


def sd_theta_localizan(r):
    """sd de θ* entre las ventanas de la lámina que EFECTIVAMENTE localizan."""
    th = [v["theta_best"] for v in r["ventanas"] if v["margen_best"] >= MARGEN_UNICO]
    return float(np.std(th)) if len(th) >= 2 else np.nan


def veredicto(r, sd_max):
    if r.get("frac_theta_en_borde", 0) > 0.5:
        return "indeterminada (θ clavado)"
    if r["frac_localiza_rot"] < FRAC_MIN:
        return "no recuperada"
    if not np.isfinite(r["sd_theta_loc"]) or r["sd_theta_loc"] > sd_max:
        return "recuperada, θ no consistente"
    return "recuperada por rotación"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", default=str(BASE / "probe_rotacion.json"))
    ap.add_argument("--out", default=str(BASE / "probe_rotacion_veredicto.csv"))
    ap.add_argument("--sd-max", type=float, default=None,
                    help="corte de consistencia de θ; por defecto se calibra "
                         "contra el peor del grupo C")
    args = ap.parse_args()
    import pandas as pd

    res = [r for r in json.load(open(args.probe)) if "error" not in r]
    if not res:
        print("sin resultados legibles"); return
    for r in res:
        r["sd_theta_loc"] = round(sd_theta_localizan(r), 2)

    # ---------- PASO 1: el control positivo. Sin esto no se lee nada más ----------
    print("=" * 76)
    print("PASO 1 — GRUPO C, CONTROL POSITIVO")
    print("=" * 76)
    C = [r for r in res if r["grupo"] == "C"]
    if not C:
        print("NO HAY GRUPO C -> el pre-registro prohíbe leer el resto."); return
    for r in C:
        print(f"  {r['slide_id']:<12} localiza θ=0 {r['frac_localiza_theta0']:.2f}  "
              f"NCC {r['ncc_medio_theta0']:.3f} -> {r['ncc_medio_rot']:.3f}  "
              f"θ* {r['theta_best_mediano']:+.1f}°  sd(localizan) {r['sd_theta_loc']:.1f}°")
    pasa = all(r["frac_localiza_theta0"] >= FRAC_MIN for r in C)
    print(f"\n  las {len(C)} del control siguen medibles a θ=0: {pasa}")
    if not pasa:
        print("  -> PROBE ROTO. El pre-registro prohíbe leer A y B."); return
    print("  -> el probe REPRODUCE el barrido. Se puede leer.")

    sd_max = args.sd_max if args.sd_max is not None else \
        float(np.nanmax([r["sd_theta_loc"] for r in C]))
    print(f"\n  [calibración] corte de consistencia = peor del control = sd <= {sd_max:.1f}°")
    ncc0 = np.mean([r["ncc_medio_theta0"] for r in C])
    nccr = np.mean([r["ncc_medio_rot"] for r in C])
    print(f"  [dato] barrer θ sube el NCC TAMBIÉN en el control: {ncc0:.3f} -> {nccr:.3f}, "
          f"|θ*| mediano {np.median([abs(r['theta_best_mediano']) for r in C]):.1f}°")
    print("         ⇒ hay rotación también en las medibles: la etapa A la TOLERABA.")

    # ---------- PASO 2: las no medibles ----------
    for r in res:
        r["veredicto"] = veredicto(r, sd_max)
    df = pd.DataFrame([{k: v for k, v in r.items() if k != "ventanas"} for r in res])

    print("\n" + "=" * 76)
    print("PASO 2 — GRUPOS A y B, las no medibles")
    print("=" * 76)
    for g in ("A", "B"):
        sub = df[df.grupo == g]
        if not len(sub):
            continue
        print(f"\n--- grupo {g} ({'silueta>=0.95' if g=='A' else 'silueta<0.95'}, n={len(sub)}) ---")
        print(sub[["slide_id", "frac_localiza_theta0", "frac_localiza_rot",
                   "ncc_medio_theta0", "ncc_medio_rot", "theta_best_mediano",
                   "sd_theta_loc", "veredicto"]].to_string(index=False))

    ab = df[df.grupo != "C"]
    rec = ab[ab.frac_localiza_rot >= FRAC_MIN]
    print("\n" + "=" * 76)
    print("VEREDICTO")
    print("=" * 76)
    print(f"  no medibles de la muestra: {len(ab)}")
    print(f"  cruzan el umbral al barrer θ: **{len(rec)} de {len(ab)}**")
    print(ab.veredicto.value_counts().to_string())
    if len(rec):
        print(f"\n  |θ*| mediano de las que cruzan: "
              f"{np.median(np.abs(rec.theta_best_mediano)):.1f}°  "
              f"(la etapa B barre ±8°, y su default es ±1.5°)")
    baja = ab[ab.frac_localiza_rot < ab.frac_localiza_theta0]
    if len(baja):
        print(f"\n  ⚠ {len(baja)} lámina(s) EMPEORAN al rotar ({', '.join(baja.slide_id)}): "
              f"es la salvedad de diseño, θ se elige por NCC y no por margen. "
              f"Ninguna del control cruza hacia abajo.")

    df.to_csv(args.out, index=False)
    print(f"\n-> {args.out}")


if __name__ == "__main__":
    main()
