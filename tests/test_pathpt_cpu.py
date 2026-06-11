"""Smoke tests CPU para el port de PathPT-CONCH (Etapa 1 B5).

Verifica el paquete models_pathpt/ + las funciones clave del driver
scripts/train_pathpt.py, sin GPU y sin entrenar de verdad:

- θ_v (MultiKernelConv1DTrans): preserva los N parches, sin NaN.
- PatchSSLoss: en BINARIO el candidate_loss (ec.7) es degenerado (0) — addendum §7
  de la pre-registración; gradiente fluye.
- generate_patch_label: con logits_thd=0 no hay candidatos en binario (todo 0/1);
  con umbral alto sí aparecen candidatos (-k).
- best_threshold: elige el umbral que maximiza balanced_acc (rama eval H-2).
- PathPTCONCH (con CONCH real, CPU): forward [N,512]→[N,2] preserva N, softmax,
  entrena SOLO θ_v+θ_t (CONCH congelado), gradiente fluye a ambos.

El smoke END-TO-END del driver (carga .pt+h5, proj_contrast, ranking de teacher,
curriculum, eval, volcados schema-CLAM) se corre aparte sobre datos reales
(results/pathpt_smoke). Acá validamos las piezas de forma rápida y determinista.

Ejecutable directo (NUNCA `python` a secas — workaround B); requiere .pylibs en path:
    PYTHONPATH=/media/administrador/Storage1/sdonoso/clam_testing2/.pylibs \
    /home/sdonoso/miniconda3/envs/clam_latest/bin/python tests/test_pathpt_cpu.py
"""
import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
_PYLIBS = "/media/administrador/Storage1/sdonoso/clam_testing2/.pylibs"
_CLAM = "/media/administrador/Storage1/sdonoso/clam_environ"
for _p in (_PYLIBS, str(REPO_ROOT), _CLAM):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import torch  # noqa: E402

from models_pathpt import MultiKernelConv1DTrans, PatchSSLoss, PathPTCONCH  # noqa: E402

CKPT = ("/home/sdonoso/.cache/huggingface/hub/models--MahmoodLab--conch/"
        "snapshots/f9ca9f877171a28ade80228fb195ac5d79003357/pytorch_model.bin")


def _load_driver():
    spec = importlib.util.spec_from_file_location(
        "train_pathpt", str(REPO_ROOT / "scripts" / "train_pathpt.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_spatial_preserves_N():
    """θ_v: [N,512] -> [1,N,512], preserva N, sin NaN, con gradiente."""
    torch.manual_seed(0)
    N = 137
    theta_v = MultiKernelConv1DTrans(in_channels=512, out_channels=512)
    x = torch.randn(N, 512, requires_grad=True)
    y = theta_v(x)
    assert y.shape == (1, N, 512), f"θ_v shape {tuple(y.shape)}, esperaba (1,{N},512)"
    assert not torch.isnan(y).any() and not torch.isinf(y).any(), "θ_v NaN/Inf"
    y.sum().backward()
    assert any(p.grad is not None and p.grad.abs().sum() > 0 for p in theta_v.parameters()), \
        "θ_v no recibió gradiente"
    print(f"[OK] θ_v preserva N={N}, gradiente fluye")


def test_patchssloss_binary_candidate_degenerate():
    """En binario (2 clases) candidate_loss = -log(p0+p1) = 0 (addendum §7). Gradiente OK."""
    torch.manual_seed(0)
    N = 60
    raw = torch.rand(N, 2, requires_grad=True)          # tensor HOJA (acumula .grad)
    logits = torch.softmax(raw, -1)                      # patch_logits ya softmax (como el modelo)
    # labels: mezcla conocidos (0/1) y candidatos (-1)
    labels = torch.tensor(([0, 1, -1] * (N // 3))[:N])
    out = PatchSSLoss(logits, labels, epoch=0, total_epoch=20, weights=(1.0, 0.5, 0.1), balance=True)
    assert abs(out["candidate_loss"].item()) < 1e-6, \
        f"candidate_loss debería ser ~0 en binario, fue {out['candidate_loss'].item()}"
    assert out["loss"].item() > 0, "loss total degenerada a 0"
    out["loss"].backward()
    assert raw.grad is not None and raw.grad.abs().sum() > 0, "no fluye gradiente"
    print(f"[OK] PatchSSLoss binario: candidate_loss={out['candidate_loss'].item():.2e} (degenerado), "
          f"loss={out['loss'].item():.4f}")


def test_generate_patch_label_threshold():
    """generate_patch_label: thd=0 → sin candidatos en binario; thd alto → candidatos (-1)."""
    drv = _load_driver()
    torch.manual_seed(0)
    probs = torch.softmax(torch.randn(50, 2), -1)
    lab0 = drv.generate_patch_label(probs, logits_thd=0.0, tumor_class=1)
    assert set(lab0.tolist()) <= {0, 1}, f"thd=0 no debería dar candidatos: {set(lab0.tolist())}"
    lab_hi = drv.generate_patch_label(probs, logits_thd=0.95, tumor_class=1)
    assert (lab_hi == -1).any(), "thd alto debería producir candidatos -1"
    print(f"[OK] generate_patch_label: thd=0 sin candidatos; thd=0.95 candidatos={(lab_hi==-1).sum().item()}")


def test_best_threshold():
    """best_threshold elige el corte que separa bien (rama eval H-2: umbral en val)."""
    import numpy as np
    drv = _load_driver()
    ys = np.array([0, 0, 0, 1, 1, 1])
    scores = np.array([0.1, 0.2, 0.3, 0.7, 0.8, 0.9])
    t = drv.best_threshold(ys, scores)
    assert 0.3 <= t < 0.7, f"umbral {t} no separa las clases"
    print(f"[OK] best_threshold separable → t={t:.3f}")


def test_model_forward_and_grad():
    """PathPTCONCH con CONCH real: forward [N,512]->[N,2] preserva N; entrena solo θ_v+θ_t."""
    from conch.open_clip_custom import create_model_from_pretrained
    torch.manual_seed(0)
    conch = create_model_from_pretrained("conch_ViT-B-16", checkpoint_path=CKPT,
                                         device="cpu", return_transform=False)
    conch.eval()
    classnames = [["benign breast tissue"], ["tumor necrosis", "comedonecrosis"]]
    model = PathPTCONCH(classnames, conch, device="cpu", n_ctx=32, vfeat_dim=512)

    train_names = [n for n, p in model.named_parameters() if p.requires_grad]
    assert "prompt_learner.ctx" in train_names, "θ_t (ctx) no entrenable"
    assert any(n.startswith("spatial.") for n in train_names), "θ_v (spatial) no entrenable"
    assert all(n.startswith("spatial.") or n == "prompt_learner.ctx" for n in train_names), \
        f"se filtró algo de CONCH a entrenable: {train_names}"

    N = 40
    feats = torch.randn(N, 512)
    _, patch_logits = model(feats)
    assert patch_logits.shape == (N, 2), f"patch_logits {tuple(patch_logits.shape)}"
    assert torch.allclose(patch_logits.sum(-1), torch.ones(N), atol=1e-4), "no softmax por fila"

    labels = torch.tensor(([0, 1] * (N // 2))[:N])
    out = PatchSSLoss(patch_logits, labels, epoch=0, total_epoch=20, weights=(1.0, 0.5, 0.1))
    out["loss"].backward()
    g_ctx = model.prompt_learner.ctx.grad
    g_sp = next(p.grad for n, p in model.named_parameters()
                if n.startswith("spatial.conv1") and p.grad is not None)
    assert g_ctx is not None and g_ctx.abs().sum() > 0, "θ_t sin gradiente"
    assert g_sp.abs().sum() > 0, "θ_v sin gradiente"
    print(f"[OK] PathPTCONCH forward [N=40,512]→{tuple(patch_logits.shape)} preserva N; "
          f"gradiente fluye a θ_v y θ_t (trainable={len(train_names)} tensores)")


if __name__ == "__main__":
    test_spatial_preserves_N()
    test_patchssloss_binary_candidate_degenerate()
    test_generate_patch_label_threshold()
    test_best_threshold()
    test_model_forward_and_grad()
    print("\nTodos los smoke tests CPU de PathPT pasaron.")
