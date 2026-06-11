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


def test_patchssloss_multiclass_candidate_active():
    """En 3-clase candidate_loss NO degenera (p0+pk<1) → la maquinaria multiclase se activa
    (a diferencia del binario, addendum §7 necrosis; prereg mitotic §1)."""
    torch.manual_seed(0)
    N = 60
    raw = torch.rand(N, 3, requires_grad=True)
    logits = torch.softmax(raw, -1)
    labels = torch.tensor(([0, 1, -2] * (N // 3))[:N])    # candidatos -2 (tumor_class=2)
    out = PatchSSLoss(logits, labels, epoch=0, total_epoch=20, weights=(1.0, 0.5, 0.1), balance=True)
    assert out["candidate_loss"].item() > 1e-4, \
        f"candidate_loss debería ser >0 en 3-clase, fue {out['candidate_loss'].item()}"
    out["loss"].backward()
    assert raw.grad is not None and raw.grad.abs().sum() > 0, "no fluye gradiente"
    print(f"[OK] PatchSSLoss 3-clase: candidate_loss={out['candidate_loss'].item():.4f} (ACTIVA), "
          f"loss={out['loss'].item():.4f}")


def test_generate_patch_label_multiclass():
    """generate_patch_label tumor_class=2 (3-clase): confiables {0,2}; la CLASE INTERMEDIA (1)
    cae a candidato (-2) incluso con thd=0 → así se activa la candidate_loss multiclase (≠ binario,
    donde no hay clase intermedia). thd alto → ≥ candidatos. (prereg mitotic §1/§3.1.)"""
    drv = _load_driver()
    torch.manual_seed(0)
    probs = torch.softmax(torch.randn(50, 3), -1)
    lab0 = drv.generate_patch_label(probs, logits_thd=0.0, tumor_class=2)
    assert set(lab0.tolist()) <= {0, 2, -2}, f"labels fuera de {{0,2,-2}}: {set(lab0.tolist())}"
    assert (lab0 == -2).any(), \
        "en 3-clase la clase intermedia debería caer a candidato -2 (activa la candidate_loss)"
    n0 = int((lab0 == -2).sum())
    lab_hi = drv.generate_patch_label(probs, logits_thd=0.9, tumor_class=2)
    assert int((lab_hi == -2).sum()) >= n0, "thd alto debería dar ≥ candidatos"
    print(f"[OK] generate_patch_label 3-clase (tumor=2): candidatos thd0={n0} → "
          f"thd0.9={int((lab_hi == -2).sum())} (la clase intermedia activa la candidate_loss)")


def test_model_forward_3class():
    """PathPTCONCH 3-clase (CONCH real): forward [N,512]->[N,3] preserva N, softmax por fila."""
    from conch.open_clip_custom import create_model_from_pretrained
    torch.manual_seed(0)
    conch = create_model_from_pretrained("conch_ViT-B-16", checkpoint_path=CKPT,
                                         device="cpu", return_transform=False)
    conch.eval()
    classnames = [["a low mitotic count", "rare mitoses"],
                  ["an intermediate mitotic count"],
                  ["a high mitotic count", "frequent mitotic figures"]]
    model = PathPTCONCH(classnames, conch, device="cpu", n_ctx=32, vfeat_dim=512)
    assert model.n_classes == 3, f"n_classes {model.n_classes}"
    N = 40
    _, patch_logits = model(torch.randn(N, 512))
    assert patch_logits.shape == (N, 3), f"patch_logits {tuple(patch_logits.shape)}"
    assert torch.allclose(patch_logits.sum(-1), torch.ones(N), atol=1e-4), "no softmax por fila"
    print(f"[OK] PathPTCONCH 3-clase forward [N=40,512]→{tuple(patch_logits.shape)} preserva N, softmax")


def test_eval_multiclass_auc():
    """Lógica de eval multiclase (argmax + macro-OVR AUC + confusión 3x3) corre y da valores válidos."""
    import numpy as np
    from sklearn.metrics import roc_auc_score, balanced_accuracy_score, confusion_matrix
    rng = np.random.RandomState(0)
    yt = np.array([0] * 12 + [1] * 8 + [2] * 6)
    st = rng.dirichlet(np.ones(3), size=len(yt))
    for i, y in enumerate(yt):                            # empuja la diagonal → AUC > 0.5
        st[i, y] += 0.5
    st = st / st.sum(1, keepdims=True)
    yhat = st.argmax(1)
    auc = roc_auc_score(yt, st, multi_class="ovr", average="macro", labels=[0, 1, 2])
    bal = balanced_accuracy_score(yt, yhat)
    cm = confusion_matrix(yt, yhat, labels=[0, 1, 2])
    assert 0.0 <= auc <= 1.0 and cm.shape == (3, 3), "eval multiclase inválido"
    print(f"[OK] eval multiclase: macro-OVR AUC={auc:.3f} bal_acc={bal:.3f} conf3x3 N={cm.sum()}")


if __name__ == "__main__":
    test_spatial_preserves_N()
    test_patchssloss_binary_candidate_degenerate()
    test_generate_patch_label_threshold()
    test_best_threshold()
    test_model_forward_and_grad()
    # --- multiclase (Etapa 1 mitotic 3-clase ordinal) ---
    test_patchssloss_multiclass_candidate_active()
    test_generate_patch_label_multiclass()
    test_model_forward_3class()
    test_eval_multiclass_auc()
    print("\nTodos los smoke tests CPU de PathPT pasaron.")
