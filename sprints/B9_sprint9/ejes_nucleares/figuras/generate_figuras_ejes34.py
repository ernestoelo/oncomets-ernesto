#!/usr/bin/env python
"""generate_figuras_ejes34.py — las figuras de los dos ejes nucleares, NATIVAS.

Qué es esto
-----------
Una **hoja de figuras**, no un deck: cuatro láminas con la gramática de la plantilla oficial,
listas para entrar al deck del período cuando Ernesto lo decida. No toca
`presentacion_b9/generate_b9_deck.py` ni su `.pptx`.

Por qué existe
--------------
[[hallazgo-necesita-forma-presentable]]: los ejes 3 y 4 estaban medidos y documentados, y no
tenían una sola figura. Un número sin dibujo no se defiende en voz alta. Y su ADDENDUM del
19-ago fija el **cómo**: la figura **importa el código que produjo el número**, no lo
reimplementa, así que «la figura muestra otra cosa que la tabla» no sea representable.

De dónde sale cada número
-------------------------
  - `scripts/b9_epitelio_estroma.py`      -> `rank_auc` (eje 4)
  - `scripts/b9_pleomorfismo.py`          -> `spearman`, `permutacion_exacta`, `ORDEN` (eje 3)
  - `results/b9_nucleos/regiones_epi_estroma.csv` + `regiones_nulo.npy`
  - `results/b9_nucleos/marcas_grado.csv`
  - `presentacion_b9/generate_b9_deck.py` -> paleta, geometría, medición de texto y QA

Nada se transcribe a mano. Los números que quedan dibujados se escriben además a
`numeros_figuras.csv`, que sí se versiona (el `.pptx` es derivado y está gitignored).

Todo NATIVO
-----------
Las cuatro figuras son objetos dibujables (barras, puntos, histogramas, ejes), así que van
como shapes y no como PNG: el criterio del ADDENDUM B5 de `CLAUDE.md` no es de dónde salió la
imagen sino si el objeto se puede dibujar.

Lo que las figuras NO pueden decir (handoff §9, prereg §4)
----------------------------------------------------------
  - Ninguna cita un AUC **por lámina** de la población restringida: valen 1,000 con n = 1.
  - Ninguna presenta el área cruda (H3.b) como el resultado: el primario es el percentil.
  - Ninguna compara áreas en µm² entre clases de HoVer-NeXt ([[descriptor-absoluto-trae-el-umbral]]).
  - Ninguna lee el ordenamiento como validación de Nottingham.
  - Cada figura declara su **unidad** (región, lámina, marca), que es donde se confunden.

Uso:
    PYTHONPATH=/media/administrador/Storage1/sdonoso/clam_testing2/.pylibs \
      /home/sdonoso/miniconda3/envs/pruebas/bin/python generate_figuras_ejes34.py

(`envs/pruebas` es el único con zarr y pandas juntos, y `b9_pleomorfismo` importa zarr al
tope; `.pylibs` aporta python-pptx. Workaround B: binario absoluto.)
"""
import csv
import os
import sys

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(AQUI, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "scripts"))
sys.path.insert(0, os.path.join(REPO, "sprints", "B9_sprint9", "presentacion_b9"))

import b9_epitelio_estroma as E                                          # noqa: E402
import b9_pleomorfismo as P                                              # noqa: E402
from generate_b9_deck import (ACENTO, BLANCO, CUERPO, G_CUERPO, LINEA,   # noqa: E402
                              PT_PIE, SEP, T_PIE_S03, TITULO, _alto_bloque,
                              _rect, add_textbox, auditar, barrer_rayas,
                              borrar_slide, clonar_s03, forzar_barlow, notes, num,
                              pie_lineas, set_cejilla, set_cuerpo, set_titulo, text_w)
from pptx import Presentation                                            # noqa: E402
from pptx.enum.shapes import MSO_SHAPE                                   # noqa: E402
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN                          # noqa: E402
from pptx.util import Inches, Pt                                         # noqa: E402

TPL = os.path.join(REPO, "papers", "presentations",
                   "[AAAAMMDD] [Nombre Apellido] [Image-to-text].pptx")
OUT = os.path.join(AQUI, "figuras_ejes_3_4.pptx")
CSV_NUM = os.path.join(AQUI, "numeros_figuras.csv")
TEMA = "Detección Nuclear"

CSV_REG = os.path.join(REPO, "results", "b9_nucleos", "regiones_epi_estroma.csv")
NPY_NUL = os.path.join(REPO, "results", "b9_nucleos", "regiones_nulo.npy")
CSV_MAR = os.path.join(REPO, "results", "b9_nucleos", "marcas_grado.csv")

# Las dos láminas cuyo offset quedó con `alineada: false`. Se dibujan con el punto HUECO: una
# de ellas es el peldaño del medio entero, y eso tiene que verse en la figura y no en el pie.
NO_ALIN = P.NO_ALINEADAS


# ===========================================================================
# Primitivas de dibujo que la plantilla no traía
# ===========================================================================
def eje_x(slide, l, t, w, vmin, vmax, ticks, dec=2, fs=8.5, col=SEP):
    """Eje horizontal: línea de base y etiquetas debajo. Devuelve el borde inferior."""
    _rect(slide, l, t, w, 0.012, col)
    for v in ticks:
        x = l + w * (v - vmin) / float(vmax - vmin)
        _rect(slide, x - 0.006, t, 0.012, 0.07, col)
        txt = num(v, dec)
        add_textbox(slide, x - 0.45, t + 0.08, 0.90, 0.17,
                    [(txt, fs, False, CUERPO, PP_ALIGN.CENTER)], anchor=MSO_ANCHOR.TOP)
    return t + 0.08 + 0.17


def eje_y(slide, l, t, h, vmin, vmax, ticks, dec=0, fs=8.5, col=SEP):
    """Eje vertical con el 0 abajo. `l` es la x de la línea; las etiquetas van a su izquierda."""
    _rect(slide, l, t, 0.012, h, col)
    for v in ticks:
        y = t + h * (1.0 - (v - vmin) / float(vmax - vmin))
        _rect(slide, l - 0.06, y - 0.006, 0.07, 0.012, col)
        add_textbox(slide, l - 0.62, y - 0.09, 0.50, 0.18,
                    [(num(v, dec), fs, False, CUERPO, PP_ALIGN.RIGHT)],
                    anchor=MSO_ANCHOR.MIDDLE)


def punto(slide, cx, cy, d, color, hueco=False):
    """Marcador circular. Hueco = anillo, para las láminas con `alineada: false`."""
    ov = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(cx - d / 2.0), Inches(cy - d / 2.0),
                                Inches(d), Inches(d))
    if hueco:
        ov.fill.background()
        ov.line.color.rgb = color
        ov.line.width = Pt(1.75)
    else:
        ov.fill.solid()
        ov.fill.fore_color.rgb = color
        ov.line.fill.background()
    ov.shadow.inherit = False
    return ov


def histograma(slide, l, t, w, h, vals, vmin, vmax, nbins, color):
    """Histograma nativo: una barra por bin, apoyadas en la base. Devuelve el conteo máximo."""
    bordes = np.linspace(vmin, vmax, nbins + 1)
    cuenta, _ = np.histogram(np.asarray(vals, float), bins=bordes)
    top = max(int(cuenta.max()), 1)
    wb = w / float(nbins)
    for i, c in enumerate(cuenta):
        if not c:
            continue
        hb = h * c / float(top)
        _rect(slide, l + i * wb + 0.006, t + h - hb, max(wb - 0.012, 0.012), hb, color)
    return top


def marcador_vertical(slide, x, t, h, texto, color, fs=9.5, lado="der"):
    """Línea vertical rotulada: el valor observado sobre un histograma."""
    _rect(slide, x - 0.012, t, 0.024, h, color)
    aw = text_w(texto, fs, True) + 0.12
    xl = x + 0.09 if lado == "der" else x - 0.09 - aw
    al = PP_ALIGN.LEFT if lado == "der" else PP_ALIGN.RIGHT
    add_textbox(slide, xl, t - 0.02, aw, 0.20, [(texto, fs, True, color, al)],
                anchor=MSO_ANCHOR.MIDDLE)


def leyenda_puntos(slide, l, t, items, fs=9, d=0.13):
    """Leyenda de marcadores: (color, hueco, texto)."""
    x = l
    for color, hueco, txt in items:
        punto(slide, x + d / 2.0, t + 0.09, d, color, hueco)
        add_textbox(slide, x + d + 0.08, t, text_w(txt, fs) + 0.10, 0.18,
                    [(txt, fs, False, CUERPO)], anchor=MSO_ANCHOR.MIDDLE)
        x += d + 0.08 + text_w(txt, fs) + 0.30
    return t + 0.18


def caja_figura(fin_cuerpo, pie, w):
    """Reparte lo que queda entre el cuerpo y la zona de pie. Devuelve (top, alto, y_pie)."""
    h_pie = _alto_bloque(pie, w - 0.06, PT_PIE, space_after=1.5)
    top = fin_cuerpo + 0.16
    alto = T_PIE_S03 - 0.12 - h_pie - 0.12 - top
    return top, alto, top + alto + 0.12


# ===========================================================================
# Los datos: se LEEN y se recalculan con las primitivas que produjeron el número
# ===========================================================================
def datos_eje4():
    import pandas as pd
    df = pd.read_csv(CSV_REG)
    nul = np.load(NPY_NUL)
    pos = (df["grupo"] == "epitelio").to_numpy()
    obs = E.rank_auc(df["f_epi"].to_numpy(), pos)
    aucs = np.array([E.rank_auc(nul[:, i], pos) for i in range(nul.shape[1])])
    aucs = aucs[~np.isnan(aucs)]
    p = (1 + int((aucs >= obs).sum())) / (1.0 + len(aucs))
    sub = df[df["alineada"]]
    clases = []
    for cl, g in df.groupby("clase"):
        v = g["f_epi"].dropna()
        if not len(v):
            continue
        clases.append(dict(clase=cl, grupo=g["grupo"].iloc[0], n=len(g), n_val=len(v),
                           med=float(v.median()), p25=float(v.quantile(.25)),
                           p75=float(v.quantile(.75))))
    # epitelio primero, cada grupo por mediana descendente: el orden de la tabla de §1.a
    clases.sort(key=lambda d: (d["grupo"] != "epitelio", -d["med"]))
    return dict(df=df, clases=clases, obs=obs, nulo=aucs, p=p,
                n_reg=len(df), n_epi=int(pos.sum()), n_est=int((~pos).sum()),
                sin_nucleos=int(df["f_epi"].isna().sum()),
                auc_alin=E.rank_auc(sub["f_epi"].to_numpy(),
                                    (sub["grupo"] == "epitelio").to_numpy()),
                n_alin=len(sub))


def datos_eje3():
    import pandas as pd
    m = pd.read_csv(CSV_MAR)
    COL = "pct_area_um2"                      # el PRIMARIO: percentil intra-lámina, no el área

    def bloque(df, etiqueta):
        pl = (df.groupby(["slide", "grado", "grado_ord"], as_index=False)
                .agg(n=(COL, "size"), med=(COL, "median")))
        pl["alineada"] = ~pl["slide"].isin(NO_ALIN)
        rho, _ = P.spearman(pl["grado_ord"], pl["med"])
        perm = P.permutacion_exacta(pl["grado_ord"], pl["med"], con_rhos=True)
        grados = []
        for g in P.ORDEN:
            s = df[df["grado"] == g][COL].dropna()
            grados.append(dict(grado=g, n_marcas=len(s),
                               n_lam=int(pl[pl["grado"] == g].shape[0]),
                               med=float(s.median()), p25=float(s.quantile(.25)),
                               p75=float(s.quantile(.75))))
        pares = []
        for g1, g2 in (("bajo", "moderado"), ("moderado", "alto")):
            sub = df[df["grado"].isin([g1, g2])]
            auc, npos, nneg = P.rank_auc(sub[COL], (sub["grado"] == g2).to_numpy())
            pares.append(dict(par="%s > %s" % (g2, g1), auc=auc, n_neg=nneg, n_pos=npos))
        return dict(etiqueta=etiqueta, pl=pl, rho=rho, obs=perm[0], p_bi=perm[1],
                    p_uni=perm[2], k=perm[3], rhos=perm[4], grados=grados, pares=pares,
                    n_marcas=len(df), n_lam=len(pl))

    r = m[m["clase_hovernext"] == "epithelial-cell"]
    return dict(restringida=bloque(r, "restringida a epitelio"),
                completa=bloque(m, "completa"))


# ===========================================================================
# Las cuatro láminas
# ===========================================================================
def lamina_f1(s, d4):
    """Eje 4: la fracción epitelial por clase. Es el chequeo que no depende del estadístico."""
    set_cejilla(s, TEMA)
    set_titulo(s, "El control positivo separa epitelio de estroma", nombre="Text 1")
    fin = set_cuerpo(s, [
        ("%d regiones del patólogo en las doce láminas: " % d4["n_reg"],
         "la fracción epitelial cuenta núcleos de HoVer-NeXt dentro del polígono, y las dos "
         "clases de estroma dan cero exacto en la mediana."),
    ])
    l, _, w = G_CUERPO
    pie = ["Unidad: una REGIÓN por fila. La barra es el rango intercuartil y la marca oscura "
           "la mediana; %d regiones quedaron sin ningún núcleo adentro y salen del cálculo. "
           "«CDIS_papilar» se comporta como estroma estando en el grupo epitelio, y son 6 "
           "marcas de una sola lámina: se deja anotado, no se interpreta."
           % d4["sin_nucleos"]]
    top, alto, y_pie = caja_figura(fin, pie, w)

    w_lab, w_num, gap = 2.05, 1.15, 0.16
    x0 = l + w_lab + gap
    w_bar = w - w_lab - w_num - 2 * gap
    filas = d4["clases"]
    h_eje = 0.25
    paso = (alto - h_eje - 0.30) / len(filas)
    h_b = min(0.20, paso - 0.10)

    y_leg = top
    cx = x0
    for col, txt in ((CUERPO, "grupo epitelio"), (SEP, "grupo estroma")):
        _rect(s, cx, y_leg + 0.045, 0.16, 0.11, col)
        add_textbox(s, cx + 0.21, y_leg, 1.7, 0.19, [(txt, 8.5, False, CUERPO)],
                    anchor=MSO_ANCHOR.MIDDLE)
        cx += 0.21 + text_w(txt, 8.5) + 0.32
    add_textbox(s, l + w - w_num, y_leg, w_num, 0.19,
                [("regiones", 8.5, True, CUERPO, PP_ALIGN.RIGHT)], anchor=MSO_ANCHOR.MIDDLE)

    y0 = top + 0.30
    for i, f in enumerate(filas):
        y = y0 + i * paso
        yc = y + (paso - h_b) / 2.0
        col = CUERPO if f["grupo"] == "epitelio" else SEP
        _rect(s, x0, yc, w_bar, h_b, LINEA)
        xa = x0 + w_bar * f["p25"]
        xb = x0 + w_bar * f["p75"]
        _rect(s, xa, yc, max(xb - xa, 0.02), h_b, col)
        _rect(s, x0 + w_bar * f["med"] - 0.022, yc - 0.035, 0.044, h_b + 0.07, TITULO)
        add_textbox(s, l, y, w_lab, paso, [(f["clase"], 9.5, True, CUERPO, PP_ALIGN.RIGHT)],
                    anchor=MSO_ANCHOR.MIDDLE)
        add_textbox(s, l + w - w_num, y, w_num, paso,
                    [("%d" % f["n"], 9.5, False, CUERPO, PP_ALIGN.RIGHT)],
                    anchor=MSO_ANCHOR.MIDDLE)
    eje_x(s, x0, y0 + len(filas) * paso + 0.06, w_bar, 0.0, 1.0,
          [0.0, 0.25, 0.5, 0.75, 1.0], dec=2)
    pie_lineas(s, l, y_pie, w, pie)
    notes(s, "Procedencia: results/b9_nucleos/regiones_epi_estroma.csv, "
             "vía scripts/b9_epitelio_estroma.py. Unidad: región.")


def lamina_f2(s, d4):
    """Eje 4: el estadístico contra su propio nulo. El número necesita su figura."""
    set_cejilla(s, TEMA)
    set_titulo(s, "Ninguna traslación del nulo llega al observado", nombre="Text 1")
    fin = set_cuerpo(s, [
        ("AUC de rango %s, contra un nulo por traslación rígida: " % num(d4["obs"], 3),
         "las %d traslaciones se centran en %s y su percentil 97,5 queda en %s, más de veinte "
         "puntos por debajo." % (len(d4["nulo"]), num(d4["nulo"].mean(), 3),
                                 num(float(np.percentile(d4["nulo"], 97.5)), 3))),
    ])
    l, _, w = G_CUERPO
    pie = ["Unidad: una REGIÓN por observación. El nulo traslada la máscara de cada región "
           "sobre el tejido de su lámina y nunca permuta etiquetas: los polígonos son "
           "contiguos.",
           "El p es el PISO alcanzable: con %d traslaciones el mínimo es 1 entre %d, así que "
           "el resultado se lee «por debajo de 1 en %d» y no como un valor exacto. Y el nulo "
           "se centra en %s y no en 0,5 porque las regiones de epitelio son más grandes que "
           "las de estroma, así que al trasladarlas no muestrean el mismo fondo."
           % (len(d4["nulo"]), len(d4["nulo"]) + 1, len(d4["nulo"]) + 1,
              num(d4["nulo"].mean(), 3))]
    top, alto, y_pie = caja_figura(fin, pie, w)

    l_h, w_h = l + 0.70, w - 1.10
    h_h = alto - 0.55
    histograma(s, l_h, top + 0.22, w_h, h_h - 0.22, d4["nulo"], 0.0, 1.0, 50, LINEA)
    for v, col, txt, lado in (
            (float(d4["nulo"].mean()), SEP, "nulo %s" % num(d4["nulo"].mean(), 3), "izq"),
            (float(np.percentile(d4["nulo"], 97.5)), SEP, "p97,5 %s"
             % num(float(np.percentile(d4["nulo"], 97.5)), 3), "der"),
            (float(d4["obs"]), ACENTO, "observado %s" % num(d4["obs"], 3), "izq")):
        marcador_vertical(s, l_h + w_h * v, top + 0.22, h_h - 0.22, txt, col, lado=lado)
    eje_x(s, l_h, top + h_h + 0.06, w_h, 0.0, 1.0, [0.0, 0.25, 0.5, 0.75, 1.0], dec=2)
    add_textbox(s, l_h, top + h_h + 0.32, w_h, 0.20,
                [("AUC de rango (epitelio > estroma)", 8.5, False, CUERPO, PP_ALIGN.CENTER)],
                anchor=MSO_ANCHOR.TOP)
    pie_lineas(s, l, y_pie, w, pie)
    notes(s, "Procedencia: results/b9_nucleos/regiones_nulo.npy (200 traslaciones por región), "
             "vía scripts/b9_epitelio_estroma.py. Unidad: región.")


def lamina_f3(s, d3):
    """Eje 3: el ordenamiento, con el `n` por lámina VISIBLE. Es lo que exige el handoff §6.3."""
    R = d3["restringida"]
    set_cejilla(s, TEMA)
    set_titulo(s, "Los tres grados ordenan sobre diez láminas", nombre="Text 1")
    fin = set_cuerpo(s, [
        ("Percentil del área dentro de la población epitelial de la propia lámina: ",
         "%s · %s · %s de mediana, con ρ = %s entre las %d láminas."
         % (num(R["grados"][0]["med"]), num(R["grados"][1]["med"]),
            num(R["grados"][2]["med"]), num(R["rho"], 3), R["n_lam"])),
    ])
    l, _, w = G_CUERPO
    pie = ["Unidad: una LÁMINA por punto, en la mediana de sus marcas. El grado está "
           "confundido con la lámina sin un solo cruce, así que comparar grados es comparar "
           "láminas y el n honesto son láminas, no las %d marcas." % R["n_marcas"],
           "Los AUC por lámina de esta población no se citan: valen 1,000 con n = 1 de un "
           "lado. Y los percentiles son altos en los tres grados, «bajo» incluido: el "
           "patólogo marca núcleos grandes para su lámina en cualquier grado, y lo que "
           "separa es cuánto."]
    top, alto, y_pie = caja_figura(fin, pie, w)

    # -- izquierda: el strip vertical, un punto por lámina
    w_izq = 5.30
    x_eje = l + 0.72
    h_pl = alto - 0.62
    t_pl = top + 0.24
    eje_y(s, x_eje, t_pl, h_pl, 0, 100, [0, 25, 50, 75, 100])
    add_textbox(s, l - 0.10, t_pl - 0.26, 3.2, 0.20,
                [("percentil intra-lámina", 8.5, False, CUERPO)], anchor=MSO_ANCHOR.TOP)
    w_pl = w_izq - (x_eje - l) - 0.20
    d = 0.155
    for gi, g in enumerate(P.ORDEN):
        sub = R["pl"][R["pl"]["grado"] == g].sort_values("med")
        cx = x_eje + w_pl * (gi + 0.5) / 3.0
        # mediana del grado: tick horizontal, y el conector que muestra el ordenamiento
        mg = R["grados"][gi]["med"]
        ym = t_pl + h_pl * (1.0 - mg / 100.0)
        _rect(s, cx - 0.34, ym - 0.011, 0.68, 0.022, ACENTO)
        n = len(sub)
        for j, (_, row) in enumerate(sub.iterrows()):
            jitter = 0.0 if n == 1 else (j / float(n - 1) - 0.5) * min(0.62, 0.14 * n)
            y = t_pl + h_pl * (1.0 - row["med"] / 100.0)
            punto(s, cx + jitter, y, d, CUERPO, hueco=not row["alineada"])
        add_textbox(s, cx - 0.75, t_pl + h_pl + 0.10, 1.50, 0.19,
                    [(g, 9.5, True, CUERPO, PP_ALIGN.CENTER)], anchor=MSO_ANCHOR.TOP)
        add_textbox(s, cx - 0.75, t_pl + h_pl + 0.29, 1.50, 0.19,
                    [("%d lámina%s · %d marcas" % (n, "" if n == 1 else "s",
                                                   R["grados"][gi]["n_marcas"]),
                      8.0, False, CUERPO, PP_ALIGN.CENTER)], anchor=MSO_ANCHOR.TOP)
    # La leyenda va ARRIBA del panel: abajo pisaba el pie, y la auditoría automática no ve
    # el solape entre dos formas ([[deck-qa-puntos-ciegos-chequeo]]).
    leyenda_puntos(s, x_eje + 1.55, t_pl - 0.32,
                   [(CUERPO, False, "offset alineado"),
                    (CUERPO, True, "alineada: false")], fs=8.5)

    # -- derecha: las diez láminas, que es de dónde sale cada punto
    x_t = l + w_izq + 0.30
    w_t = w - w_izq - 0.30
    filas = []
    for g in P.ORDEN:
        sub = R["pl"][R["pl"]["grado"] == g].sort_values("med")
        for _, row in sub.iterrows():
            filas.append([g, row["slide"], "%d" % row["n"], num(row["med"]),
                          "sí" if row["alineada"] else "NO"])
    tabla(s, x_t, top, w_t,
          ["grado", "lámina", "marcas", "percentil", "alineada"], filas,
          [0.21, 0.26, 0.17, 0.21, 0.15], fs=9.0, row_h=0.265)
    pie_lineas(s, l, y_pie, w, pie)
    notes(s, "Procedencia: results/b9_nucleos/marcas_grado.csv, columna pct_area_um2 "
             "(el primario H3.a), vía scripts/b9_pleomorfismo.py. Unidad: lámina.")


def lamina_f4(s, d3):
    """Eje 3: los dos nulos exactos, que es donde se ve qué población despega y cuál no."""
    R, C = d3["restringida"], d3["completa"]
    set_cejilla(s, TEMA)
    set_titulo(s, "El nulo exacto, y la población que no despega", nombre="Text 1")
    fin = set_cuerpo(s, [
        ("Las dos poblaciones se declararon antes y se reportan juntas: ",
         "la restringida a epitelio da p = %s sobre %d láminas y la completa queda en %s "
         "sobre %d, y el pre-registro dice que manda el nivel lámina."
         % (num(R["p_bi"], 4), R["n_lam"], num(C["p_bi"], 4), C["n_lam"])),
    ])
    l, _, w = G_CUERPO
    n_igual = int((np.abs(R["rhos"]) >= abs(R["obs"]) - 1e-12).sum())
    pie = ["Unidad: una ASIGNACIÓN del grado a las láminas por observación. El nulo permuta a "
           "nivel lámina, donde las unidades son intercambiables bajo la nula; a nivel marca "
           "no lo sería, porque las marcas de una lámina no son independientes.",
           "En la restringida el p también es el PISO: la asignación observada es la única de "
           "las %d que ordena perfecto, así que %s de las %d igualan o superan su ρ en valor "
           "absoluto y %s es el mínimo que este reparto puede dar. La lectura honesta es "
           "«ordena, con p = %s sobre %d láminas en la población limpia y %s sobre %d en la "
           "completa», no «da significativo»."
           % (R["k"], n_igual, R["k"], num(R["p_bi"], 4), num(R["p_bi"], 4), R["n_lam"],
              num(C["p_bi"], 4), C["n_lam"])]
    top, alto, y_pie = caja_figura(fin, pie, w)

    l_h, w_h = l + 0.70, w - 1.30
    h_par = (alto - 0.30) / 2.0
    for i, B in enumerate((R, C)):
        t_h = top + i * h_par
        h_b = h_par - 0.46
        histograma(s, l_h, t_h + 0.22, w_h, h_b, B["rhos"], -1.0, 1.0, 41, LINEA)
        x_obs = l_h + w_h * (B["obs"] + 1.0) / 2.0
        marcador_vertical(s, x_obs, t_h + 0.22, h_b,
                          "ρ = %s   p = %s" % (num(B["obs"], 3), num(B["p_bi"], 4)),
                          ACENTO, lado="izq")
        add_textbox(s, l_h, t_h, w_h, 0.20,
                    [("%s · %d láminas · %d asignaciones"
                      % (B["etiqueta"], B["n_lam"], B["k"]), 9.5, True, CUERPO)],
                    anchor=MSO_ANCHOR.MIDDLE)
        eje_x(s, l_h, t_h + 0.22 + h_b + 0.04, w_h, -1.0, 1.0, [-1.0, -0.5, 0.0, 0.5, 1.0], dec=1)
    # Debajo de los ticks del eje de abajo, no encima: a `- 0.10` pisaba el «0,0».
    add_textbox(s, l_h, top + 2 * h_par + 0.06, w_h, 0.20,
                [("ρ de Spearman entre el grado y el percentil, por lámina",
                  8.5, False, CUERPO, PP_ALIGN.CENTER)], anchor=MSO_ANCHOR.TOP)
    pie_lineas(s, l, y_pie, w, pie)
    notes(s, "Procedencia: permutacion_exacta() de scripts/b9_pleomorfismo.py, la misma "
             "enumeración que produjo el p. Unidad: asignación.")


# ---------------------------------------------------------------------------
def tabla(slide, l, t, w, headers, filas, fracs, fs=9.0, row_h=0.28):
    """`tabla_ejes` del deck, con el ancho de columna en fracciones. Importada por valor para
    no depender de que el generador del deck no le cambie los defaults."""
    from generate_b9_deck import tabla_ejes
    return tabla_ejes(slide, l, t, w, headers, filas, fracs, fs=fs, row_h=row_h)


def escribir_numeros(d4, d3):
    """Todo número que quede dibujado, en un CSV versionado: la figura tiene que ser auditable
    sin abrir el .pptx, que es derivado y está gitignored."""
    filas = []
    for c in d4["clases"]:
        filas.append(["eje4", "f_epi por clase", c["clase"], "region", c["n"],
                      num(c["med"], 3), num(c["p25"], 3), num(c["p75"], 3)])
    filas.append(["eje4", "AUC de rango", "epitelio > estroma", "region", d4["n_reg"],
                  num(d4["obs"], 3), "", ""])
    filas.append(["eje4", "nulo por traslacion", "media / p97,5", "region", len(d4["nulo"]),
                  num(float(d4["nulo"].mean()), 3),
                  num(float(np.percentile(d4["nulo"], 97.5)), 3), ""])
    filas.append(["eje4", "p", "piso 1/(n+1)", "region", len(d4["nulo"]),
                  num(d4["p"], 4), "", ""])
    filas.append(["eje4", "AUC solo alineadas", "epitelio > estroma", "region", d4["n_alin"],
                  num(d4["auc_alin"], 3), "", ""])
    for k, B in (("restringida", d3["restringida"]), ("completa", d3["completa"])):
        for g in B["grados"]:
            filas.append(["eje3", "percentil intra-lamina (%s)" % k, g["grado"], "marca",
                          g["n_marcas"], num(g["med"]), num(g["p25"]), num(g["p75"])])
        for _, row in B["pl"].iterrows():
            filas.append(["eje3", "mediana por lamina (%s)" % k,
                          "%s / %s" % (row["grado"], row["slide"]), "lamina", int(row["n"]),
                          num(row["med"]), "alineada" if row["alineada"] else "NO alineada",
                          ""])
        filas.append(["eje3", "rho por lamina (%s)" % k, "grado vs percentil", "lamina",
                      B["n_lam"], num(B["rho"], 3), "", ""])
        filas.append(["eje3", "nulo exacto (%s)" % k, "p bilateral / unilateral",
                      "asignacion", B["k"], num(B["p_bi"], 4), num(B["p_uni"], 4), ""])
        for pr in B["pares"]:
            filas.append(["eje3", "AUC por marca (%s)" % k, pr["par"], "marca",
                          pr["n_neg"] + pr["n_pos"], num(pr["auc"], 3), "", ""])
    with open(CSV_NUM, "w", newline="") as fh:
        wr = csv.writer(fh)
        wr.writerow(["eje", "medida", "grupo", "unidad", "n", "valor", "p25_o_aux",
                     "p75_o_aux"])
        wr.writerows(filas)
    return len(filas)


def main():
    d4 = datos_eje4()
    d3 = datos_eje3()
    R = d3["restringida"]
    print("Figuras de los ejes nucleares · hoja NATIVA, no toca el deck")
    print("  eje 4: %d regiones (%d epi / %d estroma), AUC %.3f, p %.4f"
          % (d4["n_reg"], d4["n_epi"], d4["n_est"], d4["obs"], d4["p"]))
    print("  eje 3: %d marcas en %d laminas, rho %.3f, p exacto %.4f sobre %d asignaciones"
          % (R["n_marcas"], R["n_lam"], R["rho"], R["p_bi"], R["k"]))

    prs = Presentation(TPL)
    s01, s02, s03, s04 = list(prs.slides)
    sA, sB, sC, sD = [clonar_s03(prs, s03) for _ in range(4)]
    lamina_f1(sA, d4)
    lamina_f2(sB, d4)
    lamina_f3(sC, d3)
    lamina_f4(sD, d3)
    for viejo in (s01, s02, s03, s04):
        borrar_slide(prs, viejo)                # es una hoja de figuras, no un deck

    forzar_barlow(prs)
    problemas = auditar(prs, saltar_idx=())
    problemas += barrer_rayas(prs, saltar_idx=())
    n = escribir_numeros(d4, d3)
    prs.save(OUT)
    print("  %d numeros -> %s" % (n, os.path.basename(CSV_NUM)))
    print("  escrito: %s" % os.path.basename(OUT))
    return 1 if problemas else 0


if __name__ == "__main__":
    sys.exit(main())
