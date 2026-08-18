"""cosechar_barrido_registro.py — agrega los JSON del barrido de registro multi-region.

Aplica los TRES ejes del criterio pre-fijado en `auditar_regiones_escaneo.py:591-601`
(escrito ANTES de correr, no se reordena despues de ver numeros):

  1. etapa A localiza con pico alto y UNICO           -> margen contra el segundo pico
  2. desplazamientos consistentes (cuerpo rigido)     -> residuo RMS del ajuste, en um
  3. NCC a level 0 muy por encima del control         -> ncc_medio vs control_medio

El eje 1 es una PUERTA, no una medida: si la etapa A no localiza, la etapa B mide ruido y
el resultado es indistinguible de «el tejido es de verdad distinto» (leccion de la 120063,
resultados.md §7.b). Por eso las laminas que no pasan la puerta se cuentan aparte y NO se
clasifican.

Trampa que este script evita a proposito (resultados.md §7.c-bis): **no se compara la
separacion en sd entre laminas**, porque depende del n de ventanas del control. Se comparan
NCC medio y la fraccion de ventanas sobre el maximo del control.
"""
from __future__ import annotations
import json, glob, sys
from pathlib import Path
import numpy as np, pandas as pd

D = Path(sys.argv[1] if len(sys.argv) > 1 else
         "sprints/B8_sprint8/anotaciones_patologo/regiones_escaneo/barrido_138")

filas = []
for f in sorted(glob.glob(str(D / "registro_*.json"))):
    d = json.load(open(f))
    vs, eb, si = d["ventanas"], d["etapa_b"], d["silueta"]
    # `ajuste_rigido` es None cuando no hubo ventanas suficientes para ajustar un cuerpo
    # rigido (2 laminas de 108). El eje 2 queda sin medir; los otros dos siguen valiendo.
    ar = d["ajuste_rigido"] or {}
    mpp = d["mpp"]
    rot_max = max(abs(r) for r in eb["rotaciones"])

    # eje 1: unicidad del pico de la etapa A, ventana por ventana
    margen = np.array([1.0 - v["etapa_a"]["segundo_pico"] / max(v["etapa_a"]["ncc"], 1e-9)
                       for v in vs])
    th = np.array([v["etapa_b"]["theta"] for v in vs])

    filas.append(dict(
        slide_id=str(d["slide_id"]),
        n_ventanas=len(vs),
        silueta_ncc=round(si["ncc_registrada"], 4),
        # eje 1
        margen_pico_medio=round(float(margen.mean()), 4),
        vent_pico_unico=int((margen >= 0.10).sum()),      # >=10 % sobre el 2o pico
        # eje 2
        escala=round(ar["escala"], 4) if ar else float("nan"),
        rms_um=round(ar["rms_px"] * mpp, 1) if ar else float("nan"),
        # eje 3
        ncc_medio=round(eb["ncc_medio"], 4),
        control_medio=round(eb["control_medio"], 4),
        razon_senal_control=round(eb["ncc_medio"] / max(eb["control_medio"], 1e-9), 2),
        vent_sobre_control=eb["ventanas_sobre_control"],
        frac_sobre_control=round(eb["ventanas_sobre_control"] / len(vs), 3),
        # rotacion: satura en los DOS extremos = no hay rotacion consistente que hallar
        theta_sd=round(float(th.std()), 2),
        satura_ambos=bool((th <= -rot_max).any() and (th >= rot_max).any()),
    ))

df = pd.DataFrame(filas)
# La puerta del eje 1: la mayoria de las ventanas tiene que haber localizado limpio.
df["etapaA_ok"] = df.vent_pico_unico >= np.ceil(df.n_ventanas / 2)
df = df.sort_values(["etapaA_ok", "ncc_medio"], ascending=[False, False])
df.to_csv(D.parent / "barrido_resumen.csv", index=False)

n = len(df); ok = df[df.etapaA_ok]; no = df[~df.etapaA_ok]
print("=" * 74)
print(f"BARRIDO DE REGISTRO — {n} laminas con JSON")
print("=" * 74)
print(f"etapa A localiza (puerta)  : {len(ok):3d}   ({100*len(ok)/n:.0f} %)")
print(f"etapa A NO localiza        : {len(no):3d}   -> no clasificables, no son 'seriadas'")
print()
if len(ok):
    print("Entre las que pasan la puerta:")
    print(f"  NCC senal medio   : mediana {ok.ncc_medio.median():.4f}  "
          f"rango {ok.ncc_medio.min():.4f}-{ok.ncc_medio.max():.4f}")
    print(f"  NCC control medio : mediana {ok.control_medio.median():.4f}")
    print(f"  razon senal/control: mediana {ok.razon_senal_control.median():.2f}")
    print(f"  residuo rigido    : mediana {ok.rms_um.median():.0f} um  "
          f"rango {ok.rms_um.min():.0f}-{ok.rms_um.max():.0f}")
    print(f"  escala            : mediana {ok.escala.median():.4f}  "
          f"rango {ok.escala.min():.4f}-{ok.escala.max():.4f}")
    print(f"  satura ambos extremos de rotacion: {int(ok.satura_ambos.sum())} de {len(ok)}")
    print(f"  8/8 ventanas sobre el control    : {int((ok.frac_sobre_control==1.0).sum())}")
    print()
    print("  Top 12 por NCC de senal:")
    print(ok.head(12)[["slide_id","silueta_ncc","ncc_medio","control_medio",
                       "razon_senal_control","frac_sobre_control","escala","rms_um",
                       "satura_ambos"]].to_string(index=False))
print(f"\n[out] {D.parent / 'barrido_resumen.csv'}")

# ---------------------------------------------------------------------------
# Operacionalizacion de los tres ejes. ATENCION: los cortes numericos se eligen
# DESPUES de ver los datos (el criterio pre-fijado es cualitativo: «escala ~1»,
# «residuo de pocos pixeles», «muy por encima del control»). Por eso abajo se
# reporta la sensibilidad a los cortes: si el reparto se mueve mucho, el corte
# manda mas que el dato y no habria que clasificar.
# ---------------------------------------------------------------------------
def clasificar(r, k_ratio=3.0, banda=0.02, k_frac=0.75):
    if not r.etapaA_ok:
        return "etapa A no localiza"
    rigido = (not np.isnan(r.escala)) and abs(r.escala - 1.0) <= banda
    fuerte = (r.razon_senal_control >= k_ratio) and (r.frac_sobre_control >= k_frac)
    if rigido and fuerte:
        return "perfil de re-escaneo"
    if (r.razon_senal_control < 2.0) and not rigido:
        return "perfil de secciones seriadas"
    return "ambiguo"

df["perfil"] = [clasificar(r) for r in df.itertuples()]
print("\n" + "=" * 74)
print("REPARTO POR PERFIL  (corte base: razon>=3, |escala-1|<=0.02, >=75 % ventanas)")
print("=" * 74)
for k, v in df.perfil.value_counts().items():
    print(f"  {k:30s} {v:3d}   ({100*v/len(df):.0f} %)")

print("\nSensibilidad del reparto a los cortes:")
for kr, bd, kf in [(2.5,0.03,0.60), (3.0,0.02,0.75), (4.0,0.015,0.875)]:
    c = pd.Series([clasificar(r,kr,bd,kf) for r in df.itertuples()]).value_counts()
    print(f"  razon>={kr:<4} banda={bd:<6} frac>={kf:<6} -> "
          f"re-escaneo {c.get('perfil de re-escaneo',0):3d} | "
          f"seriadas {c.get('perfil de secciones seriadas',0):3d} | "
          f"ambiguo {c.get('ambiguo',0):3d}")

# La 129741, para situarla contra el resto (su JSON vive fuera del barrido).
ref = D.parent / "registro_129741.json"
if ref.exists():
    d = json.load(open(ref)); eb = d["etapa_b"]; ar = d["ajuste_rigido"]
    r = eb["ncc_medio"] / max(eb["control_medio"], 1e-9)
    print("\n" + "=" * 74)
    print("DONDE CAE LA 129741 (su barrido de rotacion SATURA => 0.3820 es cota INFERIOR)")
    print("=" * 74)
    print(f"  NCC senal {eb['ncc_medio']:.4f} -> percentil {100*(ok.ncc_medio < eb['ncc_medio']).mean():.0f} "
          f"de las {len(ok)} que pasan la puerta")
    print(f"  razon senal/control {r:.2f} -> percentil {100*(ok.razon_senal_control < r).mean():.0f}")
    print(f"  escala {ar['escala']:.4f}, residuo {ar['rms_px']*d['mpp']:.0f} um "
          f"-> percentil de residuo {100*(ok.rms_um > ar['rms_px']*d['mpp']).mean():.0f} (mas bajo es mejor)")

df.to_csv(D.parent / "barrido_resumen.csv", index=False)
