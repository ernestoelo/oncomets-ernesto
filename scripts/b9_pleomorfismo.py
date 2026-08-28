"""b9_pleomorfismo.py — eje 3 del inventario del B9: ¿ordenan los descriptores los tres grados?

Pre-registro: `sprints/B9_sprint9/ejes_nucleares/prereg.md` §3. Esto lo ejecuta, no lo rediseña.

La pregunta
-----------
El patologo marco 107 nucleos con su grado (alto 77, moderado 14, bajo 16). Cada marca se
resuelve al **nucleo segmentado que tiene debajo** en `pinst_pp.zip` y se leen SUS descriptores
(los calcula `b9_descriptores_nucleos.py`; el area del poligono del patologo no se usa, es en
parte el pincel de QuPath — [[anotacion-tamano-objeto-vs-region]]). Si el tamano nuclear mide
pleomorfismo, tiene que ordenar alto > moderado > bajo.

Unidad: PUNTO CONTRA PUNTO, la del eje 1. No se rasteriza ninguna region: las tres clases de
grado son nucleos sueltos, no areas (prereg §0.a).

Las dos cosas que gobiernan la lectura
--------------------------------------
1. **El grado esta confundido con la lamina**: alto vive en 8 laminas, moderado en 2 y bajo en
   2, sin un solo cruce. Comparar grados **es** comparar laminas, asi que el `n` honesto del
   ordenamiento es **12 laminas**, no 107 marcas. Por eso el primario es el **percentil dentro
   de la poblacion epitelial de la propia lamina**, que cancela el efecto de lamina por
   construccion, y por eso el nulo se permuta **a nivel lamina** y no a nivel marca.
2. **El area absoluta no es comparable entre clases de HoVer-NeXt**: el umbral de foreground
   del post-proceso esta afinado por clase (`epithelial-cell` 0,6, el mas alto; `plasma-cell` y
   `connective` 0,3, los mas bajos). El reparto de clases cambia con el grado — `moderado` trae
   **7 plasmaticas de 14** —, asi que la poblacion completa mezcla umbrales y la restringida a
   epitelio no. Las dos se reportan, ninguna se elige despues de ver el resultado.

Nulo
----
Permutacion **exhaustiva** de la etiqueta de grado entre las 12 laminas: 12!/(8!·2!·2!) = 2.970
asignaciones distintas, o sea que se enumeran todas y el `p` es **exacto**, no muestreado. Es
valido a nivel lamina, donde las unidades son intercambiables bajo la nula; **a nivel marca no
lo seria**, porque las marcas de una misma lamina no son independientes. Nada que ver con el
nulo por traslacion del eje 4: alli el problema era la contiguidad espacial de una mascara
([[nulo-espacial-traslacion-rigida]]), aca el confundido es la lamina.

Lo que NO se afirma
-------------------
- **No es una validacion del grado de Nottingham.** Nottingham puntua la variacion de una
  poblacion en el campo de peor grado; aca son nucleos que el patologo eligio como ejemplares.
- **No hay precision, F1 ni PQ**: el geojson son positivos parciales.
- **12 laminas no alcanzan** para separar grado de efecto de lamina mas alla de lo que cancela
  la normalizacion intra-lamina.

Uso (workaround B; `envs/pruebas` es el unico con zarr Y pandas):
  /home/sdonoso/miniconda3/envs/pruebas/bin/python scripts/b9_pleomorfismo.py
"""
from __future__ import annotations

import argparse
import json
import sys
from itertools import combinations
from pathlib import Path

import numpy as np
import zarr

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
from b9_descriptores_nucleos import CLASES, EPITELIAL, MPP, SLIDES, paths_de   # noqa: E402

ANOTACIONES = Path("/media/administrador/Storage1/sdonoso/anotaciones")
OFFSETS = REPO / "sprints/B8_sprint8/anotaciones_patologo"

# Las tres clases de grado del geojson, con su orden ordinal. Los nombres son EXACTOS: el
# patologo no uso un vocabulario uniforme (`NucleosBajoGrado` va pegado, los otros dos no).
GRADOS = {"NucleosBajoGrado": ("bajo", 1),
          "Nucleos mod grado": ("moderado", 2),
          "Nucleos alto grado": ("alto", 3)}
ORDEN = ["bajo", "moderado", "alto"]

# Regresion del gate (prereg §1): 107 de 107 marcas caen sobre un nucleo segmentado, y este es
# el reparto de la clase que HoVer-NeXt le asigno al nucleo. Si cambia, hay un bug de offset o
# de path y ningun numero de abajo se puede leer.
GATE = {
    "alto":     {"epithelial-cell": 67, "connective-tissue-cell": 8, "lymphocyte": 2},
    "moderado": {"epithelial-cell": 4, "connective-tissue-cell": 3, "plasma-cell": 7},
    "bajo":     {"epithelial-cell": 15, "lymphocyte": 1},
}

TOL_VECINDAD_UM = 15.0        # radio de la ventana de rescate, el mismo de a0_segmentadas_o_no

# Las dos laminas cuyo offset quedo con `alineada: false`. No se excluyen — el gate resolvio
# 107 de 107 tambien en ellas —, pero se marcan: «la marca cae sobre ALGUN nucleo» es evidencia
# debil de alineamiento cuando el tejido es denso, y una de las dos (164001) es una de las dos
# unicas laminas de grado `moderado`.
NO_ALINEADAS = {"164001", "B25-158899"}


def marcas_de_grado(slide, dx, dy):
    """[(grado, ord, centroide xy en coords openslide level 0)] de las 3 clases de grado.

    Primer anillo del primer sub-poligono, igual que alinear_anotaciones_qupath.py:59-61.
    """
    js = json.loads((ANOTACIONES / f"{slide}.bif - GDT.geojson").read_text())
    out = []
    for ft in js.get("features", []):
        cl = ft.get("properties", {}).get("classification", {})
        nombre = cl.get("name") if isinstance(cl, dict) else str(cl)
        if nombre not in GRADOS:
            continue
        g = ft["geometry"]
        anillos = g["coordinates"] if g["type"] == "Polygon" else g["coordinates"][0]
        p = np.asarray(anillos[0], dtype=float) + np.array([dx, dy], dtype=float)
        grado, orden = GRADOS[nombre]
        out.append((grado, orden, p.mean(axis=0)))
    return out


def resolver(z, cen_de, mx, my, rad):
    """Instancia bajo la marca, bajo LAS DOS reglas de desempate. Devuelve dict.

    Primero el pixel bajo el centroide del poligono. Si cae en fondo (el borde de un nucleo, o
    el hueco entre dos), hay que elegir entre las instancias de la ventana de +-rad, y ahi hay
    dos desempates razonables que no siempre coinciden:

      - `centroide`: la instancia cuyo CENTROIDE global esta mas cerca de la marca. Es el patron
        de a0_segmentadas_o_no.py:118-135, que es el que cita el pre-registro §1.
      - `pixel`: la instancia del PIXEL no-cero mas cercano dentro de la ventana.

    Sobre las 107 marcas discrepan en **una** (106552 #4, con 9 instancias en la ventana), y esa
    es exactamente la diferencia contra el reparto del gate. Se calculan las dos: la primaria
    manda y la otra queda como analisis de sensibilidad, para que ningun numero dependa de un
    desempate. Si la ventana esta vacia, la marca no resuelve y no se inventa nada.
    """
    cx, cy = int(round(mx)), int(round(my))
    bajo = int(z[cy, cx])
    if bajo:
        d = float(np.hypot(cen_de[bajo, 1] - mx, cen_de[bajo, 0] - my))
        return dict(inst=bajo, inst_px=bajo, dist_px=d, via="centroide")
    y0, x0 = max(cy - rad, 0), max(cx - rad, 0)
    v = np.asarray(z[y0:cy + rad + 1, x0:cx + rad + 1])
    pres = np.unique(v)
    pres = pres[pres > 0]
    if not len(pres):
        return dict(inst=0, inst_px=0, dist_px=float("nan"), via="ninguna")
    d = np.hypot(cen_de[pres, 1] - mx, cen_de[pres, 0] - my)
    j = int(np.argmin(d))
    iy, ix = np.nonzero(v)
    dp = np.hypot((x0 + ix) - mx, (y0 + iy) - my)
    k = int(np.argmin(dp))
    return dict(inst=int(pres[j]), inst_px=int(v[iy[k], ix[k]]),
                dist_px=float(d[j]), via="vecina")


def rank_auc(valores, es_pos):
    """P(un valor del grupo positivo rankea por encima de uno del negativo). Nulo 0,5.

    Misma definicion que b9_epitelio_estroma.py:143-155 y atencion_vs_anotaciones.py:133-144.
    """
    from scipy.stats import rankdata
    v = np.asarray(valores, dtype=float)
    ok = ~np.isnan(v)
    v, p = v[ok], np.asarray(es_pos, dtype=bool)[ok]
    npos, nneg = int(p.sum()), int((~p).sum())
    if npos == 0 or nneg == 0:
        return float("nan"), npos, nneg
    r = rankdata(v)
    return float((r[p].sum() - npos * (npos + 1) / 2.0) / (npos * nneg)), npos, nneg


def spearman(x, y):
    from scipy.stats import spearmanr
    r = spearmanr(np.asarray(x, float), np.asarray(y, float))
    return float(r.statistic), float(r.pvalue)


def permutacion_exacta(orden_por_lamina, valor_por_lamina, tope=500_000):
    """`p` EXACTO de rho, enumerando todas las asignaciones del grado a las laminas.

    Con el reparto real 8/2/2 sobre 12 laminas son 12!/(8!·2!·2!) = 2.970 asignaciones, o sea
    que se agota el espacio: no hay muestreo y no hay piso de iteraciones. Se generaliza a
    cualquier reparto de tres grupos y se rinde si la enumeracion pasa `tope`.

    Bajo la nula «el grado no tiene relacion con el descriptor» las laminas son intercambiables.
    A nivel MARCA esto no seria valido: las marcas de una misma lamina no son independientes.
    """
    from math import comb

    from scipy.stats import spearmanr
    v = np.asarray(valor_por_lamina, float)
    etiquetas = np.asarray(orden_por_lamina, float)
    n = len(v)
    niveles = sorted(np.unique(etiquetas))
    if len(niveles) != 3:
        return None
    o1, o2, o3 = niveles
    n1, n2 = int((etiquetas == o1).sum()), int((etiquetas == o2).sum())
    total = comb(n, n1) * comb(n - n1, n2)
    if total > tope:
        return None
    obs = float(spearmanr(etiquetas, v).statistic)
    idx = list(range(n))
    rhos = []
    for a in combinations(idx, n1):
        resto = [i for i in idx if i not in a]
        for b in combinations(resto, n2):
            lab = np.full(n, float(o3))
            lab[list(a)] = o1
            lab[list(b)] = o2
            rhos.append(float(spearmanr(lab, v).statistic))
    rhos = np.asarray(rhos)
    return (obs,
            float((np.abs(rhos) >= abs(obs) - 1e-12).mean()),   # bilateral
            float((rhos >= obs - 1e-12).mean()),                # unilateral, direccion de H3.a
            len(rhos))


def bloque_analisis(df, etiqueta, col, nombre_col):
    """Reporta H3 sobre una columna: por marca, por lamina, pares contiguos y nulo exacto."""
    print(f"\n  --- {etiqueta} · descriptor: {nombre_col} ---")
    if df.empty or df[col].notna().sum() == 0:
        print("      sin datos")
        return
    print(f"      {'grado':<10}{'marcas':>7}{'laminas':>8}{'mediana':>10}{'p25':>9}{'p75':>9}")
    for g in ORDEN:
        s = df[df["grado"] == g][col].dropna()
        if s.empty:
            print(f"      {g:<10}{0:>7}{0:>8}{'-':>10}{'-':>9}{'-':>9}")
            continue
        nl = df[df["grado"] == g]["slide"].nunique()
        print(f"      {g:<10}{len(s):>7}{nl:>8}{s.median():>10.2f}{s.quantile(.25):>9.2f}"
              f"{s.quantile(.75):>9.2f}")

    rho_m, p_m = spearman(df["grado_ord"], df[col])
    print(f"      por MARCA   : rho = {rho_m:+.3f}  (p asintotico {p_m:.4f}, n = {len(df)} "
          f"marcas NO independientes)")

    porlam = df.groupby(["slide", "grado_ord"], as_index=False)[col].median()
    if porlam["grado_ord"].nunique() >= 2 and len(porlam) >= 3:
        rho_l, p_l = spearman(porlam["grado_ord"], porlam[col])
        reparto = "/".join(str(porlam["grado_ord"].value_counts().get(o, 0))
                           for o in (3, 2, 1))
        print(f"      por LAMINA  : rho = {rho_l:+.3f}  (p asintotico {p_l:.4f}, "
              f"n = {len(porlam)} laminas, reparto alto/mod/bajo = {reparto})")
        perm = permutacion_exacta(porlam["grado_ord"], porlam[col])
        if perm:
            _, p_bi, p_uni, k = perm
            print(f"      nulo EXACTO : permutando el grado entre las {len(porlam)} laminas, "
                  f"{k} asignaciones -> p bilateral {p_bi:.4f}, unilateral {p_uni:.4f}")
        else:
            print("      nulo EXACTO : no aplicable (hacen falta los tres grados en la poblacion)")
    else:
        print("      por LAMINA  : no calculable (falta algun grado en esta poblacion)")

    for g1, g2 in (("bajo", "moderado"), ("moderado", "alto")):
        sub = df[df["grado"].isin([g1, g2])]
        auc, npos, nneg = rank_auc(sub[col], (sub["grado"] == g2).to_numpy())
        sl = sub.groupby(["slide", "grado"], as_index=False)[col].median()
        auc_l, nl_p, nl_n = rank_auc(sl[col], (sl["grado"] == g2).to_numpy())
        print(f"      AUC {g2} > {g1:<9}: por marca {auc:.3f} (n {nneg}/{npos})"
              f"   por lamina {auc_l:.3f} (n {nl_n}/{nl_p})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slides", nargs="*", default=SLIDES)
    ap.add_argument("--mpp", type=float, default=MPP)
    ap.add_argument("--npz-dir", default=str(REPO / "results/b9_nucleos"))
    ap.add_argument("--out", default=str(REPO / "results/b9_nucleos"))
    a = ap.parse_args()
    import pandas as pd                                                     # noqa: E402

    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    rad = int(round(TOL_VECINDAD_UM / a.mpp))

    print("=" * 100)
    print("EJE 3 — PLEOMORFISMO: ¿ordenan los descriptores nucleares los tres grados?")
    print("=" * 100)
    print("unidad = MARCAS resueltas a la instancia de HoVer-NeXt que tienen debajo (107).")
    print("el area del poligono del patologo NO se usa: es en parte el pincel de QuPath.")
    print(f"ventana de rescate {TOL_VECINDAD_UM:g} um = {rad} px\n")
    print(f"  {'lamina':<12}{'grado':<10}{'marcas':>7}{'bajo centr.':>12}{'vecina':>8}"
          f"{'sin inst.':>10}{'pobl. epi':>10}")

    filas = []
    for slide in a.slides:
        off = json.loads((OFFSETS / f"offset_{slide}.json").read_text())
        marcas = marcas_de_grado(slide, off["dx"], off["dy"])
        if not marcas:
            continue
        d = paths_de(slide)
        ci = json.loads((d / "class_inst.json").read_text())
        nmax = max(int(k) for k in ci)
        cls_de = np.zeros(nmax + 1, np.int8)
        cen_de = np.zeros((nmax + 1, 2), np.float64)
        for k, v in ci.items():
            cls_de[int(k)] = v[0]
            cen_de[int(k)] = v[1]
        z = zarr.open(zarr.storage.ZipStore(str(d / "pinst_pp.zip"), mode="r"), mode="r")

        npz = np.load(Path(a.npz_dir) / f"{slide}_nucleos.npz")
        des = {k: npz[k] for k in ("id", "clase", "area_px", "eje_mayor_px", "eje_menor_px",
                                   "diam_eq_px", "excentricidad", "razon_aspecto")}
        pos = np.full(int(des["id"].max()) + 1, -1, np.int64)
        pos[des["id"]] = np.arange(len(des["id"]))
        col = {
            "area_um2": des["area_px"] * a.mpp ** 2,
            "eje_mayor_um": des["eje_mayor_px"] * a.mpp,
            "eje_menor_um": des["eje_menor_px"] * a.mpp,
            "diam_eq_um": des["diam_eq_px"] * a.mpp,
            "excentricidad": des["excentricidad"].astype(np.float64),
            "razon_aspecto": des["razon_aspecto"].astype(np.float64),
        }
        # La poblacion de referencia del percentil es SIEMPRE la epitelial de la propia lamina,
        # tambien para las marcas que HoVer-NeXt no llamo epiteliales (prereg §3).
        epi = des["clase"] == EPITELIAL
        ref = {k: np.sort(v[epi][~np.isnan(v[epi])]) for k, v in col.items()}

        cuenta = {"centroide": 0, "vecina": 0, "ninguna": 0}
        for i, (grado, orden, (mx, my)) in enumerate(marcas):
            r = resolver(z, cen_de, mx, my, rad)
            inst, inst_px, via = r["inst"], r["inst_px"], r["via"]
            cuenta[via] += 1
            f = dict(slide=slide, marca=i, grado=grado, grado_ord=orden,
                     alineada=slide not in NO_ALINEADAS,
                     x=round(float(mx), 1), y=round(float(my), 1), inst=inst, via=via,
                     dist_px=round(r["dist_px"], 2) if inst else np.nan,
                     clase_hovernext=CLASES[int(cls_de[inst])] if inst else "(sin instancia)",
                     n_pobl_epi=len(ref["area_um2"]))
            j = pos[inst] if inst and inst < len(pos) else -1
            for k, v in col.items():
                val = float(v[j]) if j >= 0 else np.nan
                f[k] = val
                f[f"pct_{k}"] = (100.0 * np.searchsorted(ref[k], val, side="right") / len(ref[k])
                                 if (j >= 0 and not np.isnan(val) and len(ref[k])) else np.nan)
            # la regla de desempate alternativa, solo para el analisis de sensibilidad del
            # primario: no se mezcla con las columnas de arriba en ninguna tabla
            f["inst_px"] = inst_px
            f["clase_px"] = CLASES[int(cls_de[inst_px])] if inst_px else "(sin instancia)"
            jp = pos[inst_px] if inst_px and inst_px < len(pos) else -1
            vp = float(col["area_um2"][jp]) if jp >= 0 else np.nan
            f["area_um2_px"] = vp
            f["pct_area_um2_px"] = (100.0 * np.searchsorted(ref["area_um2"], vp, side="right")
                                    / len(ref["area_um2"])
                                    if (jp >= 0 and not np.isnan(vp)) else np.nan)
            filas.append(f)

        g = {gr for gr, _, _ in marcas}
        print(f"  {slide:<12}{'/'.join(sorted(g)):<10}{len(marcas):>7}{cuenta['centroide']:>12}"
              f"{cuenta['vecina']:>8}{cuenta['ninguna']:>10}{len(ref['area_um2']):>10}", flush=True)

    df = pd.DataFrame(filas)
    csv = out / "marcas_grado.csv"
    df.to_csv(csv, index=False)

    # ------------------------------------------------------------------ regresion del gate
    print("\n" + "-" * 100)
    print("REGRESION DEL GATE (prereg §1): 107 de 107 y el reparto de clases")
    print("-" * 100)
    fallos = []
    if len(df) != 107:
        fallos.append(f"marcas totales: esperado 107, obtenido {len(df)}")
    sin = int((df["inst"] == 0).sum())
    if sin:
        fallos.append(f"{sin} marcas sin instancia (el gate declaro 107 de 107)")

    # El reparto se compara contra LAS DOS reglas de desempate. El gate del 27-ago se corrio con
    # un script que no quedo en el repo, asi que no se puede diffear: lo que sirve como regresion
    # es que alguna de las dos lo reproduzca EXACTO y que las dos coincidan en casi todas las
    # marcas. Un bug de offset o de path movería muchas marcas y las dos reglas a la vez.
    reparto = {r: {g: df[df["grado"] == g][c].value_counts().to_dict() for g in GATE}
               for r, c in (("centroide", "clase_hovernext"), ("pixel", "clase_px"))}
    reproduce = [r for r, d in reparto.items() if d == GATE]
    for grado, esperado in GATE.items():
        print(f"  {grado:<10} gate      {esperado}")
        for r in ("centroide", "pixel"):
            marca = "  <-- reproduce el gate" if reparto[r][grado] == esperado else ""
            print(f"  {'':<10} {r:<9} {reparto[r][grado]}{marca}")
    difieren = df[df["clase_hovernext"] != df["clase_px"]]
    if not reproduce:
        fallos.append("ninguna de las dos reglas de desempate reproduce el reparto del gate")
    if len(difieren) > 3:
        fallos.append(f"las dos reglas difieren en {len(difieren)} marcas (se esperaba 1)")
    if fallos:
        print("\n  REGRESION FALLADA:")
        for f in fallos:
            print(f"    - {f}")
        print("  Hay un bug de offset o de path. Ningun numero de abajo se puede leer.")
        sys.exit(1)

    print(f"\n  REGRESION OK: {len(df)} de 107 marcas resueltas, cero sin instancia, y el "
          f"reparto del gate lo reproduce EXACTO la regla `{'`, `'.join(reproduce)}`.")
    print(f"  Las dos reglas de desempate difieren en {len(difieren)} marca(s) de 107:")
    for _, r in difieren.iterrows():
        print(f"    {r['slide']} #{int(r['marca'])} ({r['grado']}): "
              f"centroide -> {r['clase_hovernext']} · pixel -> {r['clase_px']}")
    print("  El primario corre con `centroide`, que es el patron que cita el pre-registro §1")
    print("  (a0_segmentadas_o_no.py:118-135). La otra va abajo como sensibilidad.")

    print("\n" + "-" * 100)
    print("DE DONDE SALE CADA GRADO (el grado esta confundido con la lamina, prereg §0.c)")
    print("-" * 100)
    print(f"  {'grado':<10}{'lamina':<13}{'alineada':>9}{'marcas':>8}{'epiteliales':>12}"
          f"{'clases de HoVer-NeXt'}")
    for grado in ORDEN:
        for sl, g in df[df["grado"] == grado].groupby("slide"):
            cl = g["clase_hovernext"].value_counts().to_dict()
            print(f"  {grado:<10}{sl:<13}{str(bool(g['alineada'].iloc[0])):>9}{len(g):>8}"
                  f"{int((g['clase_hovernext'] == 'epithelial-cell').sum()):>12}  "
                  + ", ".join(f"{k} {v}" for k, v in cl.items()))

    # ------------------------------------------------------------------ H3
    epi_only = df[df["clase_hovernext"] == "epithelial-cell"]
    poblaciones = [
        ("(i) RESTRINGIDA a las marcas que HoVer-NeXt llamo epithelial-cell", epi_only),
        ("(ii) COMPLETA, las 107 marcas", df),
    ]
    print("\n" + "=" * 100)
    print("H3.a PRIMARIA — percentil del area dentro de la poblacion epitelial de la propia lamina")
    print("=" * 100)
    for etq, sub in poblaciones:
        bloque_analisis(sub, etq, "pct_area_um2", "percentil del area (0-100)")

    print("\n" + "=" * 100)
    print("H3.b SECUNDARIA — area cruda en um2 (contaminada por el efecto de lamina, prereg §0.c)")
    print("=" * 100)
    for etq, sub in poblaciones:
        bloque_analisis(sub, etq, "area_um2", "area (um2)")

    print("\n" + "=" * 100)
    print("DESCRIPTORES SECUNDARIOS, sobre la poblacion restringida (i)")
    print("=" * 100)
    # La razon de aspecto NO se reporta aparte: `exc = sqrt(1 - (menor/mayor)^2)` y
    # `razon = mayor/menor` son monotonas una de otra (verificado: spearman = 1,000000 exacto
    # sobre las 43.585 instancias de la 109609), asi que TODO estadistico de rango — percentil,
    # rho de Spearman, AUC — da identico. Presentarlas como dos descriptores seria contar dos
    # veces el mismo. Las dos columnas siguen en el CSV porque sus valores absolutos difieren.
    for c, n in (("pct_eje_mayor_um", "percentil del eje mayor"),
                 ("pct_excentricidad", "percentil de la excentricidad (= el de la razon de "
                                       "aspecto, son monotonas)")):
        bloque_analisis(epi_only, "(i) restringida", c, n)

    print("\n" + "=" * 100)
    print("SENSIBILIDAD AL DESEMPATE — el primario con la regla `pixel` en vez de `centroide`")
    print("=" * 100)
    print("Es la regla que reproduce el reparto del gate. Si el primario se mueve con esto,")
    print("el resultado depende de como se resuelve UNA marca y hay que decirlo.")
    bloque_analisis(df[df["clase_px"] == "epithelial-cell"], "(i) restringida, regla `pixel`",
                    "pct_area_um2_px", "percentil del area (0-100)")
    bloque_analisis(df, "(ii) completa, regla `pixel`",
                    "pct_area_um2_px", "percentil del area (0-100)")

    print(f"\n  -> {csv}")


if __name__ == "__main__":
    main()
