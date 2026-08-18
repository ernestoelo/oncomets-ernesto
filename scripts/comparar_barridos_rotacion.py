"""comparar_barridos_rotacion.py — compara PAREADO el barrido sin rotacion contra el barrido
con rotacion en la etapa A, y rehace el recuento de resultados.md §8.b.

Por que pareado: las dos corridas cubren EXACTAMENTE el mismo set de laminas con el mismo
codigo salvo el flag `--rot-a-max`, asi que cada lamina es su propio control. El delta por
lamina cancela la variabilidad entre laminas, que en §8.b domina todo (patron P1 de CLAUDE.md,
aplicado aca a un test geometrico y no a un entrenamiento).

Lo que este script contesta, en el orden en que el handoff lo pidio:

  1. cuantas laminas son medibles ahora           -> matriz de transicion de la PUERTA (eje 1)
  2. como clasifican las RECUPERADAS              -> cross-tab de perfiles, fila «recuperadas»
  3. el DELTA contra el 33 de 54, no solo el numero nuevo
  4. si la etapa B es el proximo cuello           -> por que no clasifica cada recuperada

Trampa que evita a proposito: NO proyecta la proporcion vieja sobre el pool nuevo. §10.c ya
advirtio que las recuperadas son justo las que mas girada tienen la segunda region, asi que
no hay razon para que se repartan como las que ya eran medibles. Se las cuenta aparte.

Uso:
  python scripts/comparar_barridos_rotacion.py [csv_sin_rot] [csv_con_rot]
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np, pandas as pd

RE = Path("sprints/B8_sprint8/anotaciones_patologo/regiones_escaneo")
A_CSV = Path(sys.argv[1]) if len(sys.argv) > 1 else RE / "barrido_resumen.csv"
B_CSV = Path(sys.argv[2]) if len(sys.argv) > 2 else RE / "barrido_resumen_barrido_rot.csv"

for f in (A_CSV, B_CSV):
    if not f.exists():
        sys.exit(f"[abort] falta {f}. Cosechar primero con cosechar_barrido_registro.py")

A = pd.read_csv(A_CSV, dtype={"slide_id": str})   # sin rotacion  (verdad de campo §8)
B = pd.read_csv(B_CSV, dtype={"slide_id": str})   # con rotacion en la etapa A

# --- COPIA de la clasificacion de cosechar_barrido_registro.py -----------------------------
# Se duplica para poder rehacer la sensibilidad; la ASERCION de abajo falla si las dos se
# desincronizan, asi que la copia no puede quedar stale en silencio.
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

for nombre, df in (("sin rot", A), ("con rot", B)):
    rehecho = [clasificar(r) for r in df.itertuples()]
    assert list(df.perfil) == rehecho, f"clasificar() se desincronizo del cosechador ({nombre})"

# ---------------------------------------------------------------------------------------
# 1. Cobertura y pareo
# ---------------------------------------------------------------------------------------
sa, sb = set(A.slide_id), set(B.slide_id)
pareadas = sorted(sa & sb)
print("=" * 78)
print("COMPARACION PAREADA — barrido sin rotacion  vs  barrido con rotacion en la etapa A")
print("=" * 78)
print(f"  laminas con JSON, sin rot : {len(A):3d}   ({A_CSV.name})")
print(f"  laminas con JSON, con rot : {len(B):3d}   ({B_CSV.name})")
print(f"  pareadas (mismo slide_id) : {len(pareadas):3d}")
solo_a, solo_b = sorted(sa - sb), sorted(sb - sa)
def corta(xs, k=15):
    return ", ".join(xs[:k]) + (f", ... (+{len(xs)-k})" if len(xs) > k else "")
if solo_a:
    print(f"  solo sin rot ({len(solo_a)})     : {corta(solo_a)}")
    print("     ^ ojo: una lamina que ANTES daba JSON y ahora no, es un STOP nuevo o un fallo.")
if solo_b:
    print(f"  solo con rot ({len(solo_b)})     : {corta(solo_b)}")
    print("     ^ esperado para la 129741, que esta corrida si incluye.")

M = A.merge(B, on="slide_id", suffixes=("_a", "_b"))
n = len(M)

# ---------------------------------------------------------------------------------------
# 2. La puerta del eje 1: quien pasa a ser medible
# ---------------------------------------------------------------------------------------
print("\n" + "=" * 78)
print("EJE 1 — LA PUERTA DE MEDIBILIDAD (transicion pareada)")
print("=" * 78)
ct = pd.crosstab(M.etapaA_ok_a, M.etapaA_ok_b, rownames=["sin rot"], colnames=["con rot"])
print(ct.to_string())
recup   = M[(~M.etapaA_ok_a) & (M.etapaA_ok_b)]
perdida = M[(M.etapaA_ok_a) & (~M.etapaA_ok_b)]
estable_ok = M[(M.etapaA_ok_a) & (M.etapaA_ok_b)]
estable_no = M[(~M.etapaA_ok_a) & (~M.etapaA_ok_b)]
med_a, med_b = int(M.etapaA_ok_a.sum()), int(M.etapaA_ok_b.sum())
print(f"\n  medibles ANTES : {med_a:3d} de {n}   ({100*med_a/n:.0f} %)")
print(f"  medibles AHORA : {med_b:3d} de {n}   ({100*med_b/n:.0f} %)")
print(f"  DELTA          : {med_b-med_a:+3d} laminas")
print(f"    recuperadas (no medible -> medible) : {len(recup):3d}")
print(f"    perdidas    (medible -> no medible) : {len(perdida):3d}"
      + ("   <- revisar, no deberia ser masivo" if len(perdida) > len(recup) else ""))
print(f"    estables medibles / no medibles     : {len(estable_ok):3d} / {len(estable_no):3d}")
if len(estable_no):
    print(f"\n  Las {len(estable_no)} que NO se recuperan resisten un barrido de rotacion: la lectura de")
    print("  §9.a (no hay senal que encontrar) se les sostiene entera.")

# contraste con la extrapolacion de §10.c, que salio de 12 laminas
if len(M[~M.etapaA_ok_a]):
    tasa = len(recup) / len(M[~M.etapaA_ok_a])
    print(f"\n  tasa de recuperacion medida : {len(recup)}/{len(M[~M.etapaA_ok_a])} = {100*tasa:.0f} %")
    print("  §10.c la habia extrapolado de 6/12 = 50 %, IC Clopper-Pearson [21 %, 79 %].")
    print("  -> " + ("CAE DENTRO del IC." if 0.21 <= tasa <= 0.79 else "CAE FUERA del IC (dato nuevo)."))

# ---------------------------------------------------------------------------------------
# 3. El recuento de §8.b, rehecho
# ---------------------------------------------------------------------------------------
print("\n" + "=" * 78)
print("§8.b REHECHO — reparto por perfil sobre el pool nuevo de medibles")
print("=" * 78)
orden = ["etapa A no localiza", "perfil de re-escaneo", "ambiguo", "perfil de secciones seriadas"]
va = M.perfil_a.value_counts()
vb = M.perfil_b.value_counts()
print(f"  {'perfil':32s} {'sin rot':>9s} {'con rot':>9s} {'delta':>8s}")
for k in orden:
    a_, b_ = int(va.get(k, 0)), int(vb.get(k, 0))
    print(f"  {k:32s} {a_:9d} {b_:9d} {b_-a_:+8d}")
print(f"\n  El denominador de §8.b pasa de {med_a} medibles a {med_b}.")
re_a = int(va.get("perfil de re-escaneo", 0)); re_b = int(vb.get("perfil de re-escaneo", 0))
print(f"  El perfil de re-escaneo pasa de {re_a}/{med_a} ({100*re_a/max(med_a,1):.0f} %) "
      f"a {re_b}/{med_b} ({100*re_b/max(med_b,1):.0f} %).")

# ---------------------------------------------------------------------------------------
# 4. Como clasifican las RECUPERADAS — la pregunta que §10.c dejo sin contestar
# ---------------------------------------------------------------------------------------
print("\n" + "=" * 78)
print("COMO CLASIFICAN LAS RECUPERADAS  (§10.c: «no sabemos como clasifican»)")
print("=" * 78)
if len(recup) == 0:
    print("  Ninguna lamina cruzo la puerta. El recuento de §8.b no se mueve.")
else:
    vr = recup.perfil_b.value_counts()
    for k in orden[1:]:
        c = int(vr.get(k, 0))
        print(f"  {k:32s} {c:3d}   ({100*c/len(recup):.0f} % de las {len(recup)} recuperadas)")
    print("\n  Contra las que YA eran medibles (¿se reparten igual?):")
    ve = estable_ok.perfil_b.value_counts()
    for k in orden[1:]:
        cr, ce = int(vr.get(k, 0)), int(ve.get(k, 0))
        print(f"  {k:32s} recuperadas {100*cr/len(recup):5.0f} %   "
              f"ya medibles {100*ce/max(len(estable_ok),1):5.0f} %")
    print("\n  Detalle de las recuperadas:")
    cols = ["slide_id", "ncc_medio_a", "ncc_medio_b", "razon_senal_control_b",
            "frac_sobre_control_b", "escala_b", "rms_um_b", "theta_sd_b", "perfil_b"]
    print(recup.sort_values("ncc_medio_b", ascending=False)[cols].to_string(index=False))

# ---------------------------------------------------------------------------------------
# 5. ¿Es la etapa B el proximo cuello? (contexto efimero del handoff, §10)
# ---------------------------------------------------------------------------------------
print("\n" + "=" * 78)
print("¿LA ETAPA B ES EL PROXIMO CUELLO?  (no busca escala; barre solo ±8°)")
print("=" * 78)
print("  Para cada lamina que pasa la puerta pero NO cae en «re-escaneo», que criterio fallo:")
def diagnostico(sub, etiqueta):
    if not len(sub):
        print(f"  {etiqueta}: ninguna."); return
    solo_esc = solo_fue = ambos = 0
    for r in sub.itertuples():
        esc = getattr(r, "escala_b"); raz = getattr(r, "razon_senal_control_b")
        frac = getattr(r, "frac_sobre_control_b")
        rigido = (not np.isnan(esc)) and abs(esc - 1.0) <= 0.02
        fuerte = (raz >= 3.0) and (frac >= 0.75)
        if not rigido and fuerte:   solo_esc += 1
        elif rigido and not fuerte: solo_fue += 1
        elif not rigido:            ambos += 1
    tot = len(sub)
    print(f"  {etiqueta} (n={tot}):")
    print(f"     falla SOLO la escala/rigidez (|escala-1|>0.02) : {solo_esc:3d}  "
          f"<- esto es cuello de la etapa B")
    print(f"     falla SOLO la fuerza de senal (razon/frac)     : {solo_fue:3d}")
    print(f"     fallan las dos                                 : {ambos:3d}")
no_reesc_r = recup[recup.perfil_b != "perfil de re-escaneo"]
no_reesc_e = estable_ok[estable_ok.perfil_b != "perfil de re-escaneo"]
diagnostico(no_reesc_r, "recuperadas que no clasifican como re-escaneo")
diagnostico(no_reesc_e, "ya medibles que no clasifican como re-escaneo")
if len(recup):
    esc = recup.escala_b.dropna()
    if len(esc):
        fuera = int((abs(esc - 1.0) > 0.02).sum())
        print(f"\n  Escala pedida por las recuperadas: mediana {esc.median():.4f}, "
              f"rango {esc.min():.4f}-{esc.max():.4f}")
        print(f"  Fuera de la banda ±2 %: {fuera} de {len(esc)}.")
        print("  Si esto es la mayoria, la etapa B es el proximo cuello y NO un bug: el ajuste")
        print("  rigido pide escala que la etapa B no busca (handoff 18-ago §10).")

# ---------------------------------------------------------------------------------------
# 6. Delta pareado de las metricas continuas
# ---------------------------------------------------------------------------------------
print("\n" + "=" * 78)
print("DELTA PAREADO DE LAS METRICAS CONTINUAS")
print("=" * 78)
# `razon = ncc / max(control, 1e-9)` explota cuando el control medio es NEGATIVO (el max lo
# clava en 1e-9 y la razon se va a 1e8). Un control negativo significa que las ventanas de
# control ANTI-correlacionan, que no es senal fuerte: es un denominador degenerado. Se excluyen
# de cualquier estadistico de razon en vez de dejar que dominen la media.
ctrl_ok = (M.control_medio_a > 0) & (M.control_medio_b > 0)
for col, etiq in (("ncc_medio", "NCC de senal"), ("razon_senal_control", "razon senal/control"),
                  ("margen_pico_medio", "margen del pico (eje 1)")):
    sub = M[ctrl_ok] if col == "razon_senal_control" else M
    d = sub[f"{col}_b"] - sub[f"{col}_a"]
    extra = f"   [excluidas {n-int(ctrl_ok.sum())} con control<=0]" if col == "razon_senal_control" and int(ctrl_ok.sum()) < n else ""
    print(f"  {etiq:26s} delta medio {d.mean():+.4f}  mediana {d.median():+.4f}  "
          f"sube en {int((d>0).sum()):3d}/{len(sub)}{extra}")
print("\n  §10.a ya habia visto que barrer θ sube el NCC TAMBIEN en las medibles: la etapa A")
print("  venia tolerando la rotacion, no evitandola. Aca se verifica sobre el set entero.")
if len(estable_ok):
    d = estable_ok.ncc_medio_b - estable_ok.ncc_medio_a
    print(f"  Solo entre las que ya eran medibles: delta NCC medio {d.mean():+.4f}, "
          f"sube en {int((d>0).sum())}/{len(estable_ok)}")

# ---------------------------------------------------------------------------------------
# 7. Sensibilidad del reparto nuevo a los cortes
# ---------------------------------------------------------------------------------------
print("\n" + "=" * 78)
print("SENSIBILIDAD DEL REPARTO NUEVO A LOS CORTES  (los cortes son posteriores al dato)")
print("=" * 78)
for kr, bd, kf in [(2.5, 0.03, 0.60), (3.0, 0.02, 0.75), (4.0, 0.015, 0.875)]:
    c = pd.Series([clasificar(r, kr, bd, kf) for r in B.itertuples()]).value_counts()
    print(f"  razon>={kr:<4} banda={bd:<6} frac>={kf:<6} -> "
          f"re-escaneo {c.get('perfil de re-escaneo',0):3d} | "
          f"seriadas {c.get('perfil de secciones seriadas',0):3d} | "
          f"ambiguo {c.get('ambiguo',0):3d}")

# ---------------------------------------------------------------------------------------
# 8. La 129741 y las que empeoran
# ---------------------------------------------------------------------------------------
print("\n" + "=" * 78)
print("LA 129741  (entro al barrido por primera vez)")
print("=" * 78)
if "129741" in set(B.slide_id):
    f = B[B.slide_id == "129741"].iloc[0]
    otras = B[(B.etapaA_ok) & (B.slide_id != "129741")]
    print(f"  pasa la puerta: {bool(f.etapaA_ok)}   perfil: {f.perfil}")
    print(f"  NCC {f.ncc_medio:.4f}  razon {f.razon_senal_control:.2f}  escala {f.escala}  "
          f"residuo {f.rms_um} um  theta_sd {f.theta_sd}  satura_ambos {bool(f.satura_ambos)}")
    if len(otras):
        print(f"  percentil de NCC contra las otras {len(otras)} medibles: "
              f"{100*(otras.ncc_medio < f.ncc_medio).mean():.0f}")
    print("  Su 0.3820 previo era COTA INFERIOR (su barrido de rotacion saturaba).")
    if f.satura_ambos:
        print("  ATENCION: sigue saturando los dos extremos -> sigue siendo cota inferior.")
else:
    print("  No esta en el CSV con rotacion. ¿Termino la corrida? ¿Quedo en .stop?")

deg = B[(B.control_medio <= 0)]
deg_puerta = deg[deg.etapaA_ok]
if len(deg):
    print("\n" + "=" * 78)
    print("AVISO — DENOMINADOR DEGENERADO (control_medio <= 0)")
    print("=" * 78)
    print(deg[["slide_id","ncc_medio","control_medio","razon_senal_control",
               "etapaA_ok","perfil"]].to_string(index=False))
    if len(deg_puerta):
        print(f"\n  {len(deg_puerta)} de estas PASA(N) la puerta con rotacion. Su razon es un")
        print("  artefacto del signo del control, NO senal fuerte, y el clasificador la manda")
        print("  a «perfil de re-escaneo» por encima de cualquier corte. NO contarlas ahi sin")
        print("  mirar la lamina: revisar a mano antes de escribir el recuento de §8.b.")
    else:
        print("\n  Ninguna pasa la puerta -> no entran al reparto por perfil. Inocuo, como en §8.")

if len(perdida):
    print("\n" + "=" * 78)
    print(f"CHEQUEO DE SANIDAD — {len(perdida)} lamina(s) que EMPEORAN")
    print("=" * 78)
    print(perdida[["slide_id", "margen_pico_medio_a", "margen_pico_medio_b",
                   "ncc_medio_a", "ncc_medio_b"]].to_string(index=False))
    print("  No es necesariamente un bug: θ se elige por el maximo de NCC, y un angulo que sube")
    print("  el pico puede subir tambien el segundo, bajando el margen (§10.b, caso 142430).")
