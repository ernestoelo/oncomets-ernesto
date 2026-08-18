#!/usr/bin/env python3
"""¿Las 54 láminas no medibles fallan por ROTACIÓN o porque el tejido es distinto?

CONTEXTO. El barrido del 17-ago dejó 54 de 108 láminas en las que la etapa A no
localiza, y `resultados.md` §8.d declara que no las explica. El diagnóstico por
ventana (`diagnostico_no_medibles.py`) ya cerró una mitad de la pregunta: el
fallo es **SIN SEÑAL** (381 de 388 ventanas, 98 %), no ambigüedad, y no depende
de la densidad de tejido ni del número de ventanas utilizables. O sea NO es
`--min-tejido` ni `--margen-a`.

QUEDA UNA HIPÓTESIS DE MÉTODO SIN DESCARTAR, y es la que prueba este script.
`_buscar_local` (auditar_regiones_escaneo.py:462) busca **solo traslación**: la
rotación entra recién en la etapa B. Si las dos regiones de escaneo están
giradas entre sí, un template de 1024 px pierde correlación aunque las células
sean las mismas, y el mapa de NCC queda plano -> exactamente el "sin señal" que
se observa. Sería una limitación NUESTRA, no un hecho del tejido.

PRE-REGISTRO (escrito antes de correr):
  - Si el fallo es ROTACIÓN: al barrer θ, la fracción de ventanas que localizan
    en el grupo A sube de forma marcada, y el θ ganador es consistente entre
    ventanas de la misma lámina (es un cuerpo rígido).
  - Si el fallo es TEJIDO DISTINTO: barrer θ no recupera nada. El pico sigue
    plano en todos los ángulos.
  - CONTROL POSITIVO (grupo C, láminas medibles): el probe tiene que reproducir
    su localización a θ=0. Si no, el probe está roto y no se lee nada más.
  - θ ganador disperso entre ventanas = ruido, NO rotación: la rotación de un
    vidrio es común a toda la lámina.

Grupos (muestra_rotacion.txt): A = no medible con silueta >= 0.95 (el subgrupo
con arquitectura bien registrada), B = no medible con silueta < 0.95,
C = medible, control positivo.
"""
import argparse, importlib.util, json, sys, time
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parents[1]
BASE = REPO / "sprints/B8_sprint8/anotaciones_patologo/regiones_escaneo"

spec = importlib.util.spec_from_file_location("aud", REPO / "scripts/auditar_regiones_escaneo.py")
aud = importlib.util.module_from_spec(spec)
sys.modules["aud"] = aud
spec.loader.exec_module(aud)


def stage_a_rot(sl, tpl_xy, dest_xy, L0, M0, lvl, ds, thetas):
    """Etapa A con barrido de rotación: mismo mapa de NCC, una vez por θ."""
    lt, lb = int(round(L0 / ds)), int(round((L0 + 2 * M0) / ds))
    tpl = np.asarray(sl.read_region(tuple(tpl_xy), lvl, (lt, lt)).convert("L"), dtype=np.float64)
    org = (int(dest_xy[0] - M0), int(dest_xy[1] - M0))
    img = np.asarray(sl.read_region(org, lvl, (lb, lb)).convert("L"), dtype=np.float64)
    if tpl.std() < 1.0 or img.std() < 1.0:
        return None
    out = []
    for th in thetas:
        I = img if th == 0.0 else aud._alinear_array(img, img.shape[0], th, 1.0)
        m = aud._mapa_ncc(I, tpl)
        if m is None:
            continue
        r = aud._pico(m)
        r["theta"] = float(th)
        r["margen"] = 1.0 - r["segundo_pico"] / max(r["ncc"], 1e-9)
        out.append(r)
    if not out:
        return None
    mejor = max(out, key=lambda r: r["ncc"])
    cero = next((r for r in out if r["theta"] == 0.0), None)
    return dict(mejor=mejor, cero=cero,
                ncc_por_theta={round(r["theta"], 2): round(r["ncc"], 4) for r in out})


def una_lamina(sid, thetas, args):  # noqa: C901
    import openslide
    j = BASE / "barrido_138" / f"registro_{sid}.json"
    if not j.exists():
        return dict(slide_id=sid, error="sin JSON del barrido")
    d = json.load(open(j))
    regs = d["regiones"]
    (x0, y0, w0, h0), (x1, y1, w1, h1) = regs[0], regs[1]
    sl = openslide.OpenSlide(str(aud.bif_limpio(aud.WSI_DIR / sid)))
    lva = d["etapa_a"]["nivel"]
    LA, MA = d["etapa_a"]["plantilla"], d["etapa_a"]["margen"]
    dsa = sl.level_downsamples[lva]
    vent = []
    for v in d.get("ventanas", []):
        ax, ay = v["region0"]
        bx, by = v["prediccion"]
        r = stage_a_rot(sl, (ax, ay), (bx, by), LA, MA, lva, dsa, thetas)
        if r is None:
            continue
        vent.append(dict(n=v["n"], tejido=v.get("tejido"),
                         ncc0=r["cero"]["ncc"] if r["cero"] else None,
                         margen0=r["cero"]["margen"] if r["cero"] else None,
                         ncc_best=r["mejor"]["ncc"], margen_best=r["mejor"]["margen"],
                         theta_best=r["mejor"]["theta"],
                         sd_best=r["mejor"]["sd_sobre_fondo"],
                         ncc_por_theta=r["ncc_por_theta"]))
    sl.close()
    if not vent:
        return dict(slide_id=sid, error="cero ventanas utilizables")
    m0 = np.array([v["margen0"] for v in vent], dtype=float)
    mb = np.array([v["margen_best"] for v in vent], dtype=float)
    tb = np.array([v["theta_best"] for v in vent], dtype=float)
    return dict(slide_id=sid, n_ventanas=len(vent),
                frac_localiza_theta0=round(float((m0 >= 0.10).mean()), 3),
                frac_localiza_rot=round(float((mb >= 0.10).mean()), 3),
                ncc_medio_theta0=round(float(np.nanmean([v["ncc0"] for v in vent])), 4),
                ncc_medio_rot=round(float(np.mean([v["ncc_best"] for v in vent])), 4),
                theta_best_mediano=round(float(np.median(tb)), 2),
                theta_best_sd=round(float(np.std(tb)), 2),
                # θ* clavado en el borde del barrido = el rango se quedó corto y la
                # MAGNITUD no se puede leer (la dirección sí). Se reporta siempre.
                frac_theta_en_borde=round(float(np.mean(np.abs(np.abs(tb) - max(abs(thetas[0]), abs(thetas[-1]))) < 1e-6)), 3),
                ventanas=vent)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--muestra", default=str(BASE / "muestra_rotacion.txt"))
    ap.add_argument("--rot-max", type=float, default=20.0)
    ap.add_argument("--rot-paso", type=float, default=1.0)
    ap.add_argument("--out", default=str(BASE / "probe_rotacion.json"))
    args = ap.parse_args()

    thetas = np.round(np.arange(-args.rot_max, args.rot_max + 1e-9, args.rot_paso), 2)
    print(f"barrido de θ: {len(thetas)} ángulos de {thetas[0]:+.1f}° a {thetas[-1]:+.1f}°")
    muestra = [l.split("\t") for l in Path(args.muestra).read_text().split("\n") if l.strip()]
    res = []
    for grupo, sid in muestra:
        t0 = time.time()
        r = una_lamina(sid, thetas, args)
        r["grupo"] = grupo
        r["seg"] = round(time.time() - t0, 1)
        res.append(r)
        if "error" in r:
            print(f"[{grupo}] {sid:<12} ERROR: {r['error']}")
        else:
            print(f"[{grupo}] {sid:<12} localiza θ=0 {r['frac_localiza_theta0']:.2f} -> "
                  f"con rotación {r['frac_localiza_rot']:.2f}   "
                  f"NCC {r['ncc_medio_theta0']:.3f} -> {r['ncc_medio_rot']:.3f}   "
                  f"θ* mediano {r['theta_best_mediano']:+.1f}° (sd {r['theta_best_sd']:.1f}"
                  f"{', CLAVADO' if r['frac_theta_en_borde'] > 0.5 else ''})  "
                  f"[{r['seg']:.0f}s]")
        json.dump(res, open(args.out, "w"), indent=1, ensure_ascii=False)

    print(f"\n=== resumen por grupo ===")
    for g in ("C", "A", "B"):
        sub = [r for r in res if r.get("grupo") == g and "error" not in r]
        if not sub:
            continue
        f0 = np.mean([r["frac_localiza_theta0"] for r in sub])
        fr = np.mean([r["frac_localiza_rot"] for r in sub])
        sd = np.mean([r["theta_best_sd"] for r in sub])
        cl = np.mean([r["frac_theta_en_borde"] for r in sub])
        print(f"  {g} (n={len(sub)}): localiza {f0:.2f} -> {fr:.2f}   "
              f"sd de θ* intra-lámina {sd:.2f}°   θ* clavado en el borde {100*cl:.0f} %")
    print(f"\n-> {args.out}")


if __name__ == "__main__":
    main()
