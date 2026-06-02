"""Smoke tests CPU para CLAM_MB_Mammoth (Objetivo 6).

Verifica que el port de Mammoth como reemplazo de la 1ª capa lineal de CLAM_MB
es correcto y drop-in:

- Forward CPU con bag random [200, 512]: shapes, no-NaN, Y_prob normalizado,
  A normalizada sobre N, instance_eval, gradiente fluye por la capa Mammoth.
- **keep_slots=False preserva los N parches** (A.shape == (2, N)) → semántica de
  attention/instance-loss idéntica al baseline CLAM (decisión Obj 6 #1).
- keep_slots=True cambia la cardinalidad (E·S pseudo-instancias) — documentado.
- El swap tomó efecto: attention_net[0] es MammothPatchEmbed, NO nn.Linear.
- Forward CPU con un .pt real de clam_environ.
- compute_test_metrics (harness compartido de train_dsmil) corre con el modelo.

Ejecutable directo (NUNCA `python` a secas — workaround B):
    /home/sdonoso/miniconda3/envs/clam_latest/bin/python tests/test_mammoth_cpu.py
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import torch  # noqa: E402
import torch.nn as nn  # noqa: E402

from models_mammoth import CLAM_MB_Mammoth, MammothPatchEmbed  # noqa: E402


def test_swap_took_effect():
    """La 1ª capa de attention_net es MammothPatchEmbed, no nn.Linear."""
    model = CLAM_MB_Mammoth(n_classes=2, embed_dim=512, dropout=0.25, k_sample=8)
    first = model.attention_net[0]
    assert isinstance(first, MammothPatchEmbed), (
        f"attention_net[0] = {type(first).__name__}, esperaba MammothPatchEmbed"
    )
    assert not isinstance(first, nn.Linear), "la 1ª capa sigue siendo lineal"
    print("[OK] swap: attention_net[0] es MammothPatchEmbed")


def test_forward_random_bag():
    """Forward CPU bag random [200, 512]; keep_slots=False preserva N."""
    torch.manual_seed(0)
    N = 200
    model = CLAM_MB_Mammoth(
        n_classes=2, embed_dim=512, dropout=0.25, k_sample=8, subtyping=False,
        mammoth_keep_slots=False,
    )
    model.eval()

    bag = torch.randn(N, 512)
    label = torch.tensor([1])

    logits, Y_prob, Y_hat, A, results = model(bag, label=label, instance_eval=False)
    assert logits.shape == (1, 2), f"logits shape {logits.shape}"
    assert not torch.isnan(logits).any(), "logits NaN"
    assert not torch.isinf(logits).any(), "logits Inf"
    assert Y_prob.shape == (1, 2), f"Y_prob shape {Y_prob.shape}"
    assert torch.allclose(Y_prob.sum(dim=1), torch.tensor([1.0]), atol=1e-5), \
        f"Y_prob no suma 1: {Y_prob}"
    assert Y_hat.shape == (1, 1), f"Y_hat shape {Y_hat.shape}"
    # keep_slots=False → N parches preservados → A es [n_classes, N].
    # OJO: CLAM_MB.forward devuelve A_raw (atención PRE-softmax), no normalizada
    # (a diferencia de DSMIL_CLAM_MB). Lo que verificamos es la cardinalidad (N
    # preservado) y que su softmax sobre N normaliza.
    assert A.shape == (2, N), \
        f"A shape {A.shape}, esperaba (2, {N}) — keep_slots=False debe preservar N"
    assert not torch.isnan(A).any() and not torch.isinf(A).any(), "A_raw NaN/Inf"
    assert torch.allclose(torch.softmax(A, dim=1).sum(dim=1), torch.ones(2), atol=1e-5), \
        "softmax(A_raw) sobre N no normaliza"

    # Con instance_eval + gradiente: debe fluir por la capa Mammoth.
    model.train()
    logits, _, _, _, results = model(bag, label=label, instance_eval=True)
    assert 'instance_loss' in results
    assert not torch.isnan(results['instance_loss']), "instance_loss NaN"
    loss = logits.sum() + results['instance_loss']
    loss.backward()
    mammoth_grads = [p.grad for p in model.attention_net[0].parameters()]
    assert len(mammoth_grads) > 0, "MammothPatchEmbed no tiene parámetros"
    assert any(g is not None and g.abs().sum() > 0 for g in mammoth_grads), \
        "la capa Mammoth NO recibió gradiente"
    assert model.classifiers[0].weight.grad is not None, \
        "bag classifier no recibió gradiente"
    print(f"[OK] forward random bag: A={tuple(A.shape)}, gradiente fluye por Mammoth")


def test_keep_slots_true_changes_cardinality():
    """keep_slots=True → la salida son E·S pseudo-instancias, NO los N parches.

    Documenta por qué la 1ª pasada usa keep_slots=False (Obj 6 #1): con True, el
    attention pooling y el instance-loss top-k operan sobre E·S, no sobre parches.
    """
    torch.manual_seed(0)
    N, E, S = 200, 6, 4   # E·S = 24 != N
    model = CLAM_MB_Mammoth(
        n_classes=2, embed_dim=512, dropout=0.0, k_sample=8,
        mammoth_num_experts=E, mammoth_num_slots=S, mammoth_num_heads=8,
        mammoth_slot_dim=128, mammoth_keep_slots=True,
    )
    model.eval()
    bag = torch.randn(N, 512)
    _, _, _, A, _ = model(bag, label=torch.tensor([1]), instance_eval=False)
    assert A.shape[1] != N, (
        f"con keep_slots=True la cardinalidad NO debería ser N={N}; A={tuple(A.shape)}"
    )
    print(f"[OK] keep_slots=True: A={tuple(A.shape)} (E·S, no N={N}) — documentado")


def test_forward_real_pt():
    """Forward CPU con un .pt real de clam_environ (CONCH 512)."""
    pt_path = Path(
        "/media/administrador/Storage1/sdonoso/clam_environ/"
        "environ/features/pt_files/101907.pt"
    )
    assert pt_path.is_file(), f"falta el .pt real: {pt_path}"
    try:
        bag = torch.load(pt_path, map_location="cpu", weights_only=True)
    except TypeError:
        bag = torch.load(pt_path, map_location="cpu")
    assert bag.dim() == 2 and bag.shape[1] == 512, \
        f"esperaba [N,512] CONCH, vino {tuple(bag.shape)}"

    model = CLAM_MB_Mammoth(n_classes=2, embed_dim=512, dropout=0.25, k_sample=8)
    model.eval()
    with torch.no_grad():
        logits, Y_prob, Y_hat, A, _ = model(bag, label=torch.tensor([1]), instance_eval=False)
    assert not torch.isnan(logits).any() and not torch.isinf(logits).any()
    assert A.shape == (2, bag.shape[0]), \
        f"A shape {A.shape}, esperaba (2, {bag.shape[0]})"  # A_raw, pre-softmax
    assert not torch.isnan(A).any() and not torch.isinf(A).any()
    print(f"[OK] forward .pt real {pt_path.name}: N={bag.shape[0]}, "
          f"Y_prob={Y_prob.flatten().tolist()}")


def test_compute_test_metrics_with_mammoth():
    """El harness compartido (train_dsmil.compute_test_metrics) corre con
    CLAM_MB_Mammoth y produce balanced_acc + confusion coherentes."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "train_dsmil", str(REPO_ROOT / "scripts" / "train_dsmil.py"),
    )
    train_dsmil = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(train_dsmil)

    torch.manual_seed(42)
    model = CLAM_MB_Mammoth(n_classes=2, embed_dim=512, dropout=0.25, k_sample=8)
    model.eval()

    class _FakeSlideDataset:
        def __init__(self, slides):
            import pandas as pd
            self._slides = slides
            self.slide_data = pd.DataFrame({'slide_id': [s[0] for s in slides]})

        def __len__(self):
            return len(self._slides)

    class _FakeLoader:
        def __init__(self, dataset):
            self.dataset = dataset

        def __iter__(self):
            for _sid, bag, lbl in self.dataset._slides:
                yield bag, torch.tensor([lbl])

    slides = [(f"slide_{i:03d}", torch.randn(150 + i * 20, 512), i % 2) for i in range(6)]
    loader = _FakeLoader(_FakeSlideDataset(slides))
    patient_results, test_metrics, preds_df = train_dsmil.compute_test_metrics(
        model, loader, torch.device("cpu"),
    )
    assert len(patient_results) == 6
    assert list(preds_df.columns) == ['slide_id', 'y_true', 'y_prob_si', 'y_pred']
    cm = test_metrics['confusion']
    assert sum(sum(r) for r in cm) == test_metrics['n_test'] == 6
    assert 0.0 <= test_metrics['balanced_acc'] <= 1.0
    print(f"[OK] compute_test_metrics con Mammoth: "
          f"bal_acc={test_metrics['balanced_acc']:.3f}, confusion={cm}")


if __name__ == "__main__":
    test_swap_took_effect()
    test_forward_random_bag()
    test_keep_slots_true_changes_cardinality()
    test_forward_real_pt()
    test_compute_test_metrics_with_mammoth()
    print("\nTodos los smoke tests CPU de Mammoth pasaron.")
