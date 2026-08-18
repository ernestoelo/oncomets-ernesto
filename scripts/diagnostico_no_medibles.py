#!/usr/bin/env python3
"""Por qué la mitad de las láminas del barrido no es medible.

El barrido del 17-ago dejó 54 de 108 láminas en las que la etapa A NO localiza
(`resultados.md` §8.a), y su §8.d declara explícitamente que no las explica:
puede ser los PARÁMETROS de selección de ventanas o puede ser que el tejido sea
de verdad distinto. Este script separa los dos modos usando el detalle POR
VENTANA que el CSV agregado había perdido.

LA IDEA. Una ventana "no localiza" cuando su pico de NCC no supera al segundo
por 10 %. Eso pasa por dos razones que son físicamente opuestas:

  - MODO AMBIGUO: hay un pico alto, pero hay más de uno. El tejido de esa
    ventana se parece a sí mismo en varios sitios (grasa, estroma laxo, un
    borde largo). El registro EXISTE, la ventana no lo distingue. Es un
    problema de QUÉ ventana elegimos -> lo arreglan los parámetros.
  - MODO SIN SEÑAL: no hay pico. El mapa de NCC es plano contra su propio
    fondo. No hay nada que localizar en ese sitio -> los parámetros no lo
    arreglan.

El estadístico que los separa ya está calculado en cada JSON: `sd_sobre_fondo`,
que es la altura del pico medida en sd del fondo del mapa de NCC. Alto con
margen chico = ambiguo; bajo = sin señal. Es independiente del valor absoluto
del NCC, que depende del contraste del tejido y no es comparable entre láminas.

Salida: sprints/.../regiones_escaneo/diagnostico_no_medibles.{csv,json}
"""
import argparse, json, sys
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parents[1]
BASE = REPO / "sprints/B8_sprint8/anotaciones_patologo/regiones_escaneo"

MARGEN_UNICO = 0.10      # el corte del criterio pre-fijado (cosechar_barrido_registro.py:48)


def cargar(barrido: Path):
    filas = []
    for j in sorted(barrido.glob("registro_*.json")):
        try:
            d = json.load(open(j))
        except Exception as e:
            print(f"[skip] {j.name}: {e}", file=sys.stderr)
            continue
        sid = d["slide_id"]
        for v in d.get("ventanas", []):
            a = v.get("etapa_a") or {}
            if "ncc" not in a:
                continue
            ncc = float(a["ncc"])
            filas.append(dict(
                slide_id=sid,
                n=int(v.get("n", -1)),
                tejido=float(v.get("tejido", np.nan)),
                ncc=ncc,
                segundo=float(a.get("segundo_pico", np.nan)),
                margen=1.0 - float(a.get("segundo_pico", np.nan)) / max(ncc, 1e-9),
                sd_fondo=float(a.get("sd_sobre_fondo", np.nan)),
                en_borde=bool(a.get("en_borde", False)),
            ))
    return filas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--barrido", default=str(BASE / "barrido_138"))
    ap.add_argument("--resumen", default=str(BASE / "barrido_resumen.csv"))
    ap.add_argument("--corte-sd", type=float, default=None,
                    help="sd_sobre_fondo que separa ambiguo de sin-senal; "
                         "por defecto la mediana de las ventanas que SI localizan")
    ap.add_argument("--out", default=str(BASE / "diagnostico_no_medibles"))
    args = ap.parse_args()

    import pandas as pd
    res = pd.read_csv(args.resumen)
    ok = dict(zip(res.slide_id.astype(str), res.etapaA_ok))

    w = pd.DataFrame(cargar(Path(args.barrido)))
    w["slide_id"] = w.slide_id.astype(str)
    w["slide_medible"] = w.slide_id.map(ok)
    w = w[w.slide_medible.notna()].copy()
    w["slide_medible"] = w.slide_medible.astype(bool)
    w["localiza"] = w.margen >= MARGEN_UNICO

    print(f"ventanas: {len(w)}  |  láminas: {w.slide_id.nunique()}")
    print(f"  en láminas medibles   : {int((w.slide_medible).sum()):>5}")
    print(f"  en láminas NO medibles: {int((~w.slide_medible).sum()):>5}")

    # --- la referencia: qué altura de pico tiene una ventana que SI localiza ---
    ref = w[w.localiza].sd_fondo
    corte = args.corte_sd if args.corte_sd is not None else float(ref.median())
    print(f"\n[referencia] ventanas que localizan (n={len(ref)}): sd_sobre_fondo "
          f"mediana {ref.median():.2f}, p25 {ref.quantile(.25):.2f}, p75 {ref.quantile(.75):.2f}")
    print(f"[corte] sd_sobre_fondo = {corte:.2f}  (mediana de las que localizan)")

    # --- los dos modos, entre las ventanas que NO localizan ---
    mal = w[~w.localiza].copy()
    mal["modo"] = np.where(mal.sd_fondo >= corte, "ambiguo", "sin_senal")
    print(f"\n=== ventanas que NO localizan (n={len(mal)}) ===")
    for m, g in mal.groupby("modo"):
        print(f"  {m:<10} {len(g):>5} ({100*len(g)/len(mal):>4.1f} %)  "
              f"ncc medio {g.ncc.mean():.3f}  sd_fondo mediano {g.sd_fondo.median():.2f}  "
              f"tejido mediano {g.tejido.median():.2f}")

    # --- por lámina: quién domina en las 54 no medibles ---
    nm = w[~w.slide_medible]
    per = []
    for sid, g in nm.groupby("slide_id"):
        b = g[~g.localiza]
        n_amb = int((b.sd_fondo >= corte).sum())
        n_sin = int((b.sd_fondo < corte).sum())
        per.append(dict(slide_id=sid, n_ventanas=len(g), n_localiza=int(g.localiza.sum()),
                        n_ambiguo=n_amb, n_sin_senal=n_sin,
                        frac_localiza=round(float(g.localiza.mean()), 3),
                        sd_fondo_mediano=round(float(g.sd_fondo.median()), 2),
                        tejido_mediano=round(float(g.tejido.median()), 3),
                        modo=("ambiguo" if n_amb > n_sin else
                              "sin_senal" if n_sin > n_amb else "mixto")))
    per = pd.DataFrame(per).sort_values(["modo", "frac_localiza"])
    print(f"\n=== las {len(per)} láminas NO medibles, por modo dominante ===")
    print(per.modo.value_counts().to_string())

    # --- ¿la densidad de tejido predice que la ventana localice? (test de H1) ---
    print("\n=== ¿la densidad de tejido de la ventana predice que localice? ===")
    print("(si SI, elegir mejor las ventanas recupera láminas -> son los parámetros)")
    for etiqueta, sub in [("láminas medibles", w[w.slide_medible]),
                          ("láminas NO medibles", nm)]:
        print(f"  {etiqueta}:")
        q = sub.tejido.quantile([0, .25, .5, .75, 1.0]).values
        bins = np.unique(q)
        if len(bins) < 3:
            print("    (densidad casi constante, no se puede binear)")
            continue
        sub = sub.copy()
        sub["bin"] = pd.cut(sub.tejido, bins, include_lowest=True)
        for b, g in sub.groupby("bin", observed=True):
            print(f"    tejido {str(b):<16} n={len(g):>4}  localiza "
                  f"{100*g.localiza.mean():>5.1f} %   sd_fondo mediano {g.sd_fondo.median():>5.2f}")

    # --- ¿el número de ventanas utilizables predice la lámina no medible? ---
    print("\n=== nº de ventanas utilizables por lámina (el otro filtro de los parámetros) ===")
    for etiqueta, sub in [("medibles", res[res.etapaA_ok]), ("NO medibles", res[~res.etapaA_ok])]:
        print(f"  {etiqueta:<12} n={len(sub):>3}  ventanas mediana {sub.n_ventanas.median():.1f}  "
              f"min {sub.n_ventanas.min()}  max {sub.n_ventanas.max()}  "
              f"con <6 ventanas: {int((sub.n_ventanas < 6).sum())}")

    out = Path(args.out)
    per.to_csv(out.with_suffix(".csv"), index=False)
    resumen = dict(
        corte_sd_sobre_fondo=round(corte, 4),
        n_ventanas=int(len(w)), n_laminas=int(w.slide_id.nunique()),
        ventanas_no_localizan=int(len(mal)),
        modo_ambiguo=int((mal.modo == "ambiguo").sum()),
        modo_sin_senal=int((mal.modo == "sin_senal").sum()),
        laminas_no_medibles=int(len(per)),
        laminas_modo=per.modo.value_counts().to_dict(),
    )
    json.dump(resumen, open(out.with_suffix(".json"), "w"), indent=2, ensure_ascii=False)
    print(f"\n-> {out.with_suffix('.csv')}\n-> {out.with_suffix('.json')}")


if __name__ == "__main__":
    main()
