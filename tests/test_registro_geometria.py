#!/usr/bin/env python
"""Tests de la geometría de `scripts/auditar_regiones_escaneo.py registro`.

Corren en CPU, en segundos, sin abrir ninguna WSI: la lámina se reemplaza por
un `FakeSlide` que sirve recortes de un array sintético. Verifican las tres
piezas donde el test decisivo se puede romper en silencio y devolver un cero
que parece un resultado:

  1. `_mapa_ncc` encuentra una plantilla en su posición EXACTA, y aguanta
     cambios de brillo, de contraste y ruido.
  2. `_ajuste_rigido` recupera una rotación, una escala y una traslación
     conocidas a partir del campo de desplazamiento.
  3. `_alinear_array` deshace esa rotación, con el SIGNO correcto. Es la que
     más fácil se equivoca: con el signo invertido el NCC empeora en vez de
     mejorar, y sin este test la conclusión saldría al revés.

Uso: /home/sdonoso/miniconda3/envs/clam_latest/bin/python tests/test_registro_geometria.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.ndimage import affine_transform, gaussian_filter

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from auditar_regiones_escaneo import (  # noqa: E402
    _ajuste_rigido, _alinear_array, _mapa_ncc, _pico, _recorte_alineado,
)

FALLOS = []


def check(cond, msg):
    print(f"  {'ok  ' if cond else 'FALLA'}  {msg}")
    if not cond:
        FALLOS.append(msg)


def textura(n, seed):
    """Textura con contraste realista. Sin el reescalado por la sd, un clip a
    0..255 satura la imagen y `_mapa_ncc` devuelve None por varianza nula."""
    g = gaussian_filter(np.random.default_rng(seed).normal(0, 1, (n, n)), 1.5)
    return np.clip(128 + 60 * g / g.std(), 0, 255)


def test_mapa_ncc():
    print("\n[1] _mapa_ncc localiza la plantilla")
    img = textura(400, 0)
    ty, tx = 137, 211
    tpl = img[ty:ty + 64, tx:tx + 64].copy()
    m = _mapa_ncc(img, tpl)
    check(m.shape == (400 - 64 + 1,) * 2, f"la forma del mapa es 'valid': {m.shape}")
    r = _pico(m)
    check((r["iy"], r["ix"]) == (ty, tx), f"pico en ({r['iy']},{r['ix']}), esperado ({ty},{tx})")
    check(r["ncc"] > 0.999, f"NCC en el sitio exacto = {r['ncc']:.6f}")

    rng = np.random.default_rng(3)
    tpl2 = tpl * 0.7 + 40 + rng.normal(0, 5, tpl.shape)
    r2 = _pico(_mapa_ncc(img, tpl2))
    check((r2["iy"], r2["ix"]) == (ty, tx), "aguanta brillo, contraste y ruido")
    check(r2["ncc"] > 0.9, f"NCC con ruido = {r2['ncc']:.4f}")

    r3 = _pico(_mapa_ncc(img, textura(64, 99)))
    check(r3["ncc"] < 0.25, f"una plantilla ajena da linea base {r3['ncc']:.4f}")


def test_ajuste_y_alineacion():
    print("\n[2] _ajuste_rigido recupera la transformación, [3] _alinear_array la deshace")
    I0 = textura(900, 7)
    TH, T = 1.5, np.array([30.0, -20.0])
    th = np.radians(TH)
    c, s = np.cos(th), np.sin(th)
    R = np.array([[c, -s], [s, c]])              # en (x, y)
    # "region 1" = I1[v] = I0[R^-1 (v - t)], generada en orden (fila, columna)
    Rinv_rc = np.array([[c, -s], [s, c]])
    I1 = affine_transform(I0, Rinv_rc, offset=-Rinv_rc @ np.array([T[1], T[0]]), order=1)

    class FakeSlide:
        def read_region(self, org, lvl, size):
            x, y = org
            w, h = size
            out = np.zeros((h, w))
            sub = I1[max(0, y):y + h, max(0, x):x + w]
            out[:sub.shape[0], :sub.shape[1]] = sub
            return Image.fromarray(out.astype(np.uint8))

    L, M = 200, 60
    us, vs = [], []
    for cx in (250, 450, 650):
        for cy in (250, 450, 650):
            u = np.array([cx, cy], float)
            vp = R @ u + T
            tpl = I0[int(u[1] - L / 2):int(u[1] + L / 2), int(u[0] - L / 2):int(u[0] + L / 2)]
            o = (int(vp[0] - L / 2 - M), int(vp[1] - L / 2 - M))
            r = _pico(_mapa_ncc(I1[o[1]:o[1] + L + 2 * M, o[0]:o[0] + L + 2 * M], tpl))
            us.append(u)
            vs.append(vp + np.array([r["ix"] - M, r["iy"] - M]))
    fit = _ajuste_rigido(np.array(us), np.array(vs))
    check(abs(fit["theta_grados"] - TH) < 0.1,
          f"rotación recuperada {fit['theta_grados']:+.3f}°, verdad {TH:+.3f}°")
    check(abs(fit["escala"] - 1.0) < 0.01, f"escala recuperada {fit['escala']:.5f}")
    check(abs(fit["traslacion"][0] - T[0]) < 3 and abs(fit["traslacion"][1] - T[1]) < 3,
          f"traslación recuperada ({fit['traslacion'][0]:.1f},{fit['traslacion'][1]:.1f})")
    check(fit["rms_px"] < 2.0, f"residuo del ajuste RMS {fit['rms_px']:.2f} px")

    u_c = np.array([450.0, 450.0])
    v_c = R @ u_c + T
    tpl = I0[int(u_c[1] - L / 2):int(u_c[1] + L / 2), int(u_c[0] - L / 2):int(u_c[0] + L / 2)]
    m = slice(12, -12)

    def ncc(a, b):
        a = a.ravel() - a.mean()
        b = b.ravel() - b.mean()
        return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))

    sl = FakeSlide()
    comp = ncc(tpl[m, m], _recorte_alineado(sl, v_c, L, fit["theta_grados"], fit["escala"])[m, m])
    sin_c = ncc(tpl[m, m], _recorte_alineado(sl, v_c, L, 0.0, 1.0)[m, m])
    reves = ncc(tpl[m, m], _recorte_alineado(sl, v_c, L, -fit["theta_grados"], fit["escala"])[m, m])
    check(comp > 0.95, f"con la rotación compensada NCC = {comp:.4f}")
    check(comp > sin_c + 0.2, f"compensar mejora: {comp:.4f} contra {sin_c:.4f} sin compensar")
    check(comp > reves + 0.2,
          f"el SIGNO es el correcto: {comp:.4f} contra {reves:.4f} con el signo invertido")

    a = _alinear_array(np.asarray(sl.read_region((0, 0), 0, (300, 300)).convert("L"), float),
                       100, 0.0, 1.0)
    check(a.shape == (100, 100), "_alinear_array respeta el lado pedido")


if __name__ == "__main__":
    test_mapa_ncc()
    test_ajuste_y_alineacion()
    print(f"\n{'TODOS OK' if not FALLOS else str(len(FALLOS)) + ' FALLAS'}")
    sys.exit(1 if FALLOS else 0)
