#!/usr/bin/env python
"""Eje 4 del inventario del B9: el CONTROL POSITIVO del metodo.

Pregunta: la fraccion de nucleos epiteliales que da HoVer-NeXt dentro de las regiones que el
patologo marco como epitelio, es mayor que dentro de las que marco como estroma?

Es el control positivo porque epitelio contra estroma es lo minimo que cualquier segmentador
nuclear deberia acertar. Si esto no separa, el eje 3 (pleomorfismo) no se lee.

Unidad: REGION CONTRA PUNTO. El patologo dibujo areas y HoVer-NeXt devuelve nucleos con clase,
asi que no hay emparejamiento uno a uno: la metrica es una fraccion dentro de cada region.

Metodo: histograma 2D de detecciones por clase a resolucion de celda, y la region rasterizada a
esa MISMA resolucion. El valor observado y el nulo se calculan igual, y trasladar la mascara es
un slice de array.

Nulo: TRASLACION RIGIDA de cada region sobre la lamina, nunca permutacion de etiquetas: los
poligonos son contiguos (memoria nulo-espacial-traslacion-rigida).

Pre-registro: sprints/B9_sprint9/ejes_nucleares/prereg.md §2

Uso (workaround B, binario absoluto del env):
  PYTHONPATH=/media/administrador/Storage1/sdonoso/clam_testing2/.pylibs \
  /home/sdonoso/miniconda3/envs/clam_latest/bin/python scripts/b9_epitelio_estroma.py
"""
import argparse, json, os, sys
import numpy as np
from PIL import Image, ImageDraw

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AN = "/media/administrador/Storage1/sdonoso/anotaciones"
OFF = os.path.join(REPO, "sprints/B8_sprint8/anotaciones_patologo")
MPP = 0.465

# Lista EXPLICITA: el glob de anotaciones/ da 13 archivos y 12 laminas (el extra es una segunda
# exportacion de la 103762). Ver cruce_94_marcas.py:53-58.
SLIDES = ["129741", "103762", "106552", "109609", "110616", "124729",
          "124806", "126504", "128194", "144317", "164001", "B25-158899"]

# Solo las clases que son REGIONES de verdad. Las de grado son nucleos sueltos (prereg §0.a).
EPITELIO = {"Tumor", "AreaSolida", "AreaTubular", "CDIS_solido", "CDIS_papilar", "DCIS"}
ESTROMA = {"Stroma", "Tejido Adiposo"}

# Offsets con alineada=false: se reportan aparte, no se excluyen.
NO_ALINEADAS = {"164001", "B25-158899"}


def paths_de(slide):
    """El barrido de las once anido el slide_id dos veces; la 129741 corrio sola y quedo plana."""
    a = os.path.join(REPO, f"results/b8_hovernext_12laminas/hovernext/lizard_mitosis/{slide}/{slide}")
    b = os.path.join(REPO, f"results/b8_hovernext_129741/hovernext/lizard_mitosis/{slide}")
    d = a if os.path.isdir(a) else b
    if not os.path.isdir(d):
        sys.exit(f"no encuentro la salida de HoVer-NeXt de {slide}")
    return d


def cargar_regiones(slide, dx, dy):
    """Devuelve [(clase, grupo, poly Nx2 en coords openslide level 0)].

    Toma el primer anillo del primer sub-poligono, igual que alinear_anotaciones_qupath.py:59-61.
    Los 131 extras de MultiPolygon son astillas de digitalizacion (mediana 0,4 um2, 105 de 131
    bajo 10 um2) y se descartan a proposito.
    """
    js = json.load(open(os.path.join(AN, f"{slide}.bif - GDT.geojson")))
    out = []
    for ft in js.get("features", []):
        cl = ft.get("properties", {}).get("classification", {})
        nombre = cl.get("name") if isinstance(cl, dict) else str(cl)
        if not nombre:
            nombre = "(sin clase)"
        grupo = "epitelio" if nombre in EPITELIO else ("estroma" if nombre in ESTROMA else None)
        if grupo is None:
            continue
        g = ft["geometry"]
        anillos = g["coordinates"] if g["type"] == "Polygon" else g["coordinates"][0]
        p = np.asarray(anillos[0], dtype=float) + np.array([dx, dy], dtype=float)
        out.append((nombre, grupo, p))
    return out


def leer_tsv(path):
    """x, y de un pred_<clase>.tsv. Columnas: x  y  name  color, sin score."""
    xs, ys = [], []
    with open(path) as fh:
        next(fh)
        for ln in fh:
            a = ln.split("\t", 2)
            xs.append(float(a[0])); ys.append(float(a[1]))
    return np.asarray(xs), np.asarray(ys)


def histograma(xs, ys, nx, ny, cell):
    """Conteo de puntos por celda de `cell` px, como matriz (ny, nx)."""
    ix = np.clip((xs / cell).astype(np.int64), 0, nx - 1)
    iy = np.clip((ys / cell).astype(np.int64), 0, ny - 1)
    h = np.bincount(iy * nx + ix, minlength=nx * ny).astype(np.int32)
    return h.reshape(ny, nx)


def mascara_tejido(h_tot, blk):
    """Tejido = BLOQUE de `blk` celdas con al menos un nucleo, re-expandido a celdas.

    A resolucion de celda (8 px) un nucleo aporta UN centroide, asi que «celda con nucleo» marca
    menos del 1 % de la grilla y ninguna traslacion pasa un umbral de cobertura. El bloque de
    32 celdas (256 px, el lado del parche) es la escala a la que «hay tejido aca» es verdad.
    """
    ny, nx = h_tot.shape
    py, px = (-ny) % blk, (-nx) % blk
    pad = np.pad(h_tot, ((0, py), (0, px)))
    b = pad.reshape(pad.shape[0] // blk, blk, pad.shape[1] // blk, blk).sum(axis=(1, 3)) > 0
    return np.repeat(np.repeat(b, blk, axis=0), blk, axis=1)[:ny, :nx]


def mascara_region(poly, cell):
    """Rasteriza el poligono a resolucion de celda. Devuelve (mask bool, cx0, cy0).

    Mismo patron que alinear_anotaciones_qupath.py:126-133 (PIL.ImageDraw.polygon), que es la
    unica forma exacta de region que ya estaba probada en el repo: no hay shapely en ningun env.
    """
    q = poly / cell
    x0, y0 = np.floor(q[:, 0].min()), np.floor(q[:, 1].min())
    x1, y1 = np.ceil(q[:, 0].max()), np.ceil(q[:, 1].max())
    w, h = int(max(x1 - x0, 1)), int(max(y1 - y0, 1))
    im = Image.new("1", (w, h), 0)
    ImageDraw.Draw(im).polygon([(float(a - x0), float(b - y0)) for a, b in q], fill=1)
    m = np.array(im, dtype=bool)
    if not m.any():          # poligono mas chico que una celda: al menos su celda de origen
        m[0, 0] = True
    return m, int(x0), int(y0)


def frac_epi(mask, cx0, cy0, h_epi, h_con):
    """f_epi de la mascara colocada en (cx0, cy0). NaN si no hay ningun nucleo dentro."""
    ny, nx = h_epi.shape
    mh, mw = mask.shape
    if cx0 < 0 or cy0 < 0 or cx0 + mw > nx or cy0 + mh > ny:
        return np.nan, 0, 0
    e = int(h_epi[cy0:cy0 + mh, cx0:cx0 + mw][mask].sum())
    c = int(h_con[cy0:cy0 + mh, cx0:cx0 + mw][mask].sum())
    if e + c == 0:
        return np.nan, e, c
    return e / (e + c), e, c


def rank_auc(valores, es_pos):
    """P(una region de epitelio rankea por encima de una de estroma). Mann-Whitney U normalizado.

    Reusa la definicion de scripts/atencion_vs_anotaciones.py:133-144.
    """
    from scipy.stats import rankdata
    v = np.asarray(valores, dtype=float)
    ok = ~np.isnan(v)
    v, p = v[ok], np.asarray(es_pos, dtype=bool)[ok]
    n_pos, n_neg = int(p.sum()), int((~p).sum())
    if n_pos == 0 or n_neg == 0:
        return float("nan")
    r = rankdata(v)
    return float((r[p].sum() - n_pos * (n_pos + 1) / 2.0) / (n_pos * n_neg))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cell", type=int, default=8, help="lado de celda en px de level 0")
    ap.add_argument("--n-null", type=int, default=200)
    ap.add_argument("--blk", type=int, default=32,
                    help="lado del bloque de tejido, en celdas (32 celdas de 8px = 256px)")
    ap.add_argument("--min-frac", type=float, default=0.9,
                    help="fraccion de la mascara trasladada que debe caer sobre tejido")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default=os.path.join(REPO, "results/b9_nucleos"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    rng = np.random.default_rng(a.seed)

    filas, nulos = [], []
    for slide in SLIDES:
        off = json.load(open(os.path.join(OFF, f"offset_{slide}.json")))
        dx, dy = off["dx"], off["dy"]
        regs = cargar_regiones(slide, dx, dy)
        d = paths_de(slide)
        xe, ye = leer_tsv(os.path.join(d, "pred_epithelial-cell.tsv"))
        xc, yc = leer_tsv(os.path.join(d, "pred_connective-tissue-cell.tsv"))

        maxx = max(xe.max(), xc.max(), max(p[:, 0].max() for _, _, p in regs))
        maxy = max(ye.max(), yc.max(), max(p[:, 1].max() for _, _, p in regs))
        nx = int(maxx // a.cell) + 2
        ny = int(maxy // a.cell) + 2
        h_epi = histograma(xe, ye, nx, ny, a.cell)
        h_con = histograma(xc, yc, nx, ny, a.cell)
        tejido = mascara_tejido(h_epi + h_con, a.blk)

        print(f"{slide:12} regiones={len(regs):3}  grilla={nx}x{ny} celdas de {a.cell}px  "
              f"epi={len(xe):7} conn={len(xc):7}  tejido={100*tejido.mean():4.1f}%", flush=True)

        for nombre, grupo, poly in regs:
            m, cx0, cy0 = mascara_region(poly, a.cell)
            f, ne, nc = frac_epi(m, cx0, cy0, h_epi, h_con)
            area_um2 = m.sum() * (a.cell * MPP) ** 2
            filas.append(dict(slide=slide, clase=nombre, grupo=grupo, f_epi=f,
                              n_epi=ne, n_conn=nc, area_um2=area_um2,
                              celdas=int(m.sum()), alineada=slide not in NO_ALINEADAS))
            # nulo: n_null traslaciones rigidas validas de ESTA region
            mh, mw = m.shape
            need = a.min_frac * m.sum()
            vals, acc, tries = [], 0, 0
            while acc < a.n_null and tries < 20000:
                tries += 1
                tx = int(rng.integers(0, max(nx - mw, 1)))
                ty = int(rng.integers(0, max(ny - mh, 1)))
                if tx == cx0 and ty == cy0:
                    continue
                if tejido[ty:ty + mh, tx:tx + mw][m].sum() < need:
                    continue
                fv, _, _ = frac_epi(m, tx, ty, h_epi, h_con)
                if np.isnan(fv):
                    continue
                vals.append(fv); acc += 1
            nulos.append(vals + [np.nan] * (a.n_null - len(vals)))

    import pandas as pd
    df = pd.DataFrame(filas)
    nul = np.asarray(nulos, dtype=float)
    csv = os.path.join(a.out, "regiones_epi_estroma.csv")
    df.to_csv(csv, index=False)
    np.save(os.path.join(a.out, "regiones_nulo.npy"), nul)

    es_pos = (df["grupo"] == "epitelio").to_numpy()
    obs = rank_auc(df["f_epi"].to_numpy(), es_pos)
    aucs_null = np.array([rank_auc(nul[:, i], es_pos) for i in range(nul.shape[1])])
    aucs_null = aucs_null[~np.isnan(aucs_null)]
    p = ((1 + int((aucs_null >= obs).sum())) / (1 + len(aucs_null))
         if len(aucs_null) else float("nan"))
    validas = int((~np.isnan(nul)).sum(axis=1).min()) if len(nul) else 0

    print("\n== EJE 4, control positivo: fraccion epitelial dentro de la region ==")
    print(f"  regiones: {len(df)}  (epitelio {int(es_pos.sum())}, estroma {int((~es_pos).sum())})"
          f"   sin nucleos dentro: {int(df['f_epi'].isna().sum())}")
    print(f"\n  {'clase':16} {'n':>3} {'f_epi mediana':>14} {'p25':>7} {'p75':>7}")
    for cl, g in df.groupby("clase"):
        v = g["f_epi"].dropna()
        if len(v) == 0:
            continue
        print(f"  {cl:16} {len(g):3} {v.median():14.3f} {v.quantile(.25):7.3f} {v.quantile(.75):7.3f}")
    print(f"\n  grupo epitelio: f_epi mediana {df[es_pos]['f_epi'].median():.3f}")
    print(f"  grupo estroma : f_epi mediana {df[~es_pos]['f_epi'].median():.3f}")
    print(f"\n  AUC de rango (epitelio > estroma) = {obs:.3f}")
    if len(aucs_null):
        print(f"  nulo por traslacion: media {aucs_null.mean():.3f}, "
              f"p2.5 {np.percentile(aucs_null,2.5):.3f}, p97.5 {np.percentile(aucs_null,97.5):.3f}"
              f"  ({len(aucs_null)} iteraciones; la region peor servida junto {validas} traslaciones)")
        print(f"  p = {p:.4f}")
    else:
        print("  nulo por traslacion: SIN iteraciones validas -> el criterio no se puede leer.")
        print("  (si pasa esto, el umbral --min-frac o el bloque --blk estan mal calibrados)")
    crit = "PASA" if (obs >= 0.80 and p < 0.05) else "NO PASA"
    print(f"\n  criterio pre-registrado (AUC >= 0,80 y nulo por debajo): {crit}")

    sub = df[df["alineada"]]
    print(f"\n  solo las 10 con alineada=true: AUC "
          f"{rank_auc(sub['f_epi'].to_numpy(), (sub['grupo']=='epitelio').to_numpy()):.3f} "
          f"(n={len(sub)})")
    print(f"\n  -> {csv}")


if __name__ == "__main__":
    main()
