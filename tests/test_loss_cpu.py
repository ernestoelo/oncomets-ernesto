"""Smoke tests CPU para las bag losses de desbalance (Eje C1).

Valida el delta del experimento `loss_desbalance` (prereg
sprints/B5_sprint5/loss_desbalance/prereg.md) SIN tocar GPU:

- `--bag_loss ce` == baseline (nn.CrossEntropyLoss, idéntico a F.cross_entropy).
- `focal` con γ=0 == CE (invariante: (1-pt)^0 = 1 → focal se reduce a -logpt).
- `focal` con γ>0 baja el peso de los ejemplos fáciles (loss < CE en un ejemplo
  bien clasificado) y es diferenciable.
- `class_balanced` reproduce los pesos por número efectivo (1-β)/(1-β^n),
  normalizados a media 1, y pondera MÁS la clase minoritaria.
- `class_balanced` APLICA el peso con batch_size=1 (MIL): CB = w_y·CE != CE plana
  (regresión del bug del job 4463, donde reduction='mean' lo cancelaba a batch=1).
- build_bag_loss corre con un split fake (slide_cls_ids) → produce loss finita.

Ejecutable directo (NUNCA `python` a secas — workaround B):
    /home/sdonoso/miniconda3/envs/clam_latest/bin/python tests/test_loss_cpu.py
"""
import importlib.util
import math
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import torch  # noqa: E402
import torch.nn as nn  # noqa: E402
import torch.nn.functional as F  # noqa: E402


def _load_train_dsmil():
    spec = importlib.util.spec_from_file_location(
        "train_dsmil", str(REPO_ROOT / "scripts" / "train_dsmil.py"),
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class _FakeSplit:
    """Imita el atributo slide_cls_ids de Generic_Split (lista de índices por
    clase) — lo único que build_bag_loss lee para class_balanced."""

    def __init__(self, counts):
        # slide_cls_ids[c] = lista de índices de la clase c (su len = conteo).
        self.slide_cls_ids = [list(range(n)) for n in counts]


def test_ce_equals_baseline():
    td = _load_train_dsmil()
    torch.manual_seed(0)
    logits = torch.randn(4, 3)
    target = torch.tensor([0, 1, 2, 1])
    loss_fn = td.build_bag_loss("ce", None, 3, 2.0, 0.9999, torch.device("cpu"))
    assert isinstance(loss_fn, nn.CrossEntropyLoss)
    got = loss_fn(logits, target)
    ref = F.cross_entropy(logits, target)
    assert torch.allclose(got, ref, atol=1e-6), f"ce != F.cross_entropy: {got} vs {ref}"
    print(f"[OK] ce == baseline (F.cross_entropy): {got.item():.4f}")


def test_focal_gamma0_equals_ce():
    """γ=0 → focal se reduce EXACTAMENTE a CE (sin α)."""
    td = _load_train_dsmil()
    torch.manual_seed(1)
    logits = torch.randn(5, 2)
    target = torch.tensor([0, 1, 1, 0, 1])
    focal0 = td.FocalLoss(gamma=0.0)
    ce = F.cross_entropy(logits, target)
    got = focal0(logits, target)
    assert torch.allclose(got, ce, atol=1e-6), f"focal(γ=0) != CE: {got} vs {ce}"
    print(f"[OK] focal(γ=0) == CE: {got.item():.4f}")


def test_focal_downweights_easy_example():
    """En un ejemplo bien clasificado (pt alto), focal(γ=2) < CE (down-weight)."""
    td = _load_train_dsmil()
    # logits muy confiados hacia la clase correcta → pt ~ 1 → (1-pt)^2 ~ 0.
    logits = torch.tensor([[5.0, -5.0]])
    target = torch.tensor([0])
    ce = F.cross_entropy(logits, target).item()
    focal = td.FocalLoss(gamma=2.0)(logits, target).item()
    assert focal < ce, f"focal({focal}) debería ser < CE({ce}) en ejemplo fácil"
    # diferenciable
    logits.requires_grad_(True)
    td.FocalLoss(gamma=2.0)(logits, target).backward()
    assert logits.grad is not None and torch.isfinite(logits.grad).all()
    print(f"[OK] focal down-weight: focal={focal:.5f} < ce={ce:.5f}, grad finito")


def test_class_balanced_weights_and_direction():
    """CB: pesos = (1-β)/(1-β^n) normalizados a media 1; minoritaria pesa más."""
    td = _load_train_dsmil()
    counts = [260, 68]            # carcinoma: no=260, si=68 (la minoritaria)
    beta = 0.9999
    split = _FakeSplit(counts)
    loss_fn = td.build_bag_loss("class_balanced", split, 2, 2.0, beta, torch.device("cpu"))
    assert isinstance(loss_fn, td.ClassBalancedCE) and loss_fn.weight is not None
    w = loss_fn.weight
    # 1) Reproduce la fórmula del número efectivo, normalizada a media 1.
    eff = [(1.0 - beta) / (1.0 - beta ** n) for n in counts]
    ref = torch.tensor(eff); ref = ref / ref.mean()
    assert torch.allclose(w, ref, atol=1e-5), f"pesos CB {w} != fórmula {ref}"
    # 2) Media 1 (escala comparable a CE).
    assert abs(w.mean().item() - 1.0) < 1e-5, f"pesos no normalizados a media 1: {w.mean()}"
    # 3) La minoritaria (índice 1, n=68) pesa MÁS que la mayoritaria.
    assert w[1] > w[0], f"la minoritaria debería pesar más: {w.tolist()}"
    # 4) En régimen n pequeño, CB ≈ inversa de frecuencia (ratio ≈ counts ratio).
    ratio_w = (w[1] / w[0]).item()
    ratio_n = counts[0] / counts[1]
    assert abs(ratio_w - ratio_n) / ratio_n < 0.05, \
        f"ratio CB {ratio_w:.2f} debería ≈ ratio conteos {ratio_n:.2f}"
    print(f"[OK] class_balanced: weights={[round(x,3) for x in w.tolist()]} "
          f"(minoritaria pesa {ratio_w:.2f}×, ≈ 1/freq {ratio_n:.2f}×)")


def test_class_balanced_applies_weight_batch1():
    """REGRESIÓN del bug del job 4463: con batch_size=1 (MIL = un slide por forward),
    la CB loss DEBE aplicar el peso (L = w_y·CE) y por tanto DIFERIR de CE plana.
    `nn.CrossEntropyLoss(weight=w)` (reduction='mean') fallaba este invariante: el
    peso se cancelaba (denominador = w_y) → CB ≡ CE → el brazo cb salía byte-idéntico
    al baseline. Este test reproduce el caso batch=1 que el test de pesos no cubría."""
    td = _load_train_dsmil()
    counts = [260, 68]            # carcinoma: no=260, si=68 (minoritaria, w>1)
    split = _FakeSplit(counts)
    loss_fn = td.build_bag_loss("class_balanced", split, 2, 2.0, 0.9999, torch.device("cpu"))
    w = loss_fn.weight
    logits = torch.tensor([[0.8, -0.3]])
    for c in (0, 1):
        target = torch.tensor([c])                       # un solo slide = batch=1
        cb = loss_fn(logits, target).item()
        ce = F.cross_entropy(logits, target).item()
        # 1) el peso se aplica de verdad: CB == w_c · CE.
        assert abs(cb - w[c].item() * ce) < 1e-6, \
            f"CB no aplica el peso a batch=1: {cb} vs w·CE {w[c].item()*ce}"
        # 2) y por tanto DIFIERE de CE plana (w_c != 1 en ambas clases acá).
        assert abs(cb - ce) > 1e-6, \
            f"CB ≡ CE con batch=1 → bug no-op (el peso se canceló): {cb} vs {ce}"
    print("[OK] class_balanced aplica el peso con batch=1 (CB = w_y·CE != CE plana)")


def test_class_balanced_3class_finite():
    """CB con 3 clases (invasión) produce loss finita y pesos coherentes."""
    td = _load_train_dsmil()
    counts = [479, 1967, 368]    # ausente, no_identificado, presente (aprox train)
    split = _FakeSplit(counts)
    loss_fn = td.build_bag_loss("class_balanced", split, 3, 2.0, 0.9999, torch.device("cpu"))
    torch.manual_seed(3)
    logits = torch.randn(6, 3)
    target = torch.tensor([0, 1, 2, 1, 1, 2])
    loss = loss_fn(logits, target)
    assert torch.isfinite(loss), f"loss CB no finita: {loss}"
    w = loss_fn.weight
    # no_identificado (mayoritaria, idx 1) debe pesar MENOS que presente (idx 2).
    assert w[1] < w[2] and w[1] < w[0], f"mayoritaria no pesa menos: {w.tolist()}"
    print(f"[OK] class_balanced 3-clase: loss={loss.item():.4f}, "
          f"weights={[round(x,3) for x in w.tolist()]}")


if __name__ == "__main__":
    test_ce_equals_baseline()
    test_focal_gamma0_equals_ce()
    test_focal_downweights_easy_example()
    test_class_balanced_weights_and_direction()
    test_class_balanced_applies_weight_batch1()
    test_class_balanced_3class_finite()
    print("\nTodos los smoke tests CPU de bag loss pasaron.")
