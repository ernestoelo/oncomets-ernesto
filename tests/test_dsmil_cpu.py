"""Smoke tests CPU para DSMIL_CLAM_MB.

Cubre §6 pasos 1 y 2 de
`sprints/B4_sprint4/objetivo_3_modulo_mil_alternativo/hipotesis.md`:

- §6.1 — Forward CPU con bag random [200, 512]: shapes, no-NaN,
  Y_prob normalizado, A normalizada sobre N, gradiente fluye.
- §6.2 — Forward CPU con .pt real de
  `clam_environ/environ/features/pt_files/`: shapes y rangos.
- Verificación adicional R1/B.1: el instance scorer W_0 NO recibe
  gradiente del logits.sum() solo (argmax no diferenciable), pero SÍ
  lo recibe cuando se agrega L_max sobre c. Justifica B.1.3.

Ejecutable directo:
    /home/sdonoso/miniconda3/envs/clam_latest/bin/python tests/test_dsmil_cpu.py
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import torch  # noqa: E402

from models_dsmil import DSMIL_CLAM_MB  # noqa: E402


def test_forward_random_bag():
    """§6.1 — forward CPU bag random [200, 512]."""
    torch.manual_seed(0)
    model = DSMIL_CLAM_MB(
        n_classes=2, embed_dim=512, dropout=0.25, k_sample=8,
        subtyping=False,
    )
    model.eval()

    bag = torch.randn(200, 512)
    label = torch.tensor([1])

    # Sin instance_eval
    logits, Y_prob, Y_hat, A, results = model(
        bag, label=label, instance_eval=False
    )
    assert logits.shape == (1, 2), f"logits shape {logits.shape}"
    assert not torch.isnan(logits).any(), "logits contiene NaN"
    assert not torch.isinf(logits).any(), "logits contiene Inf"
    assert Y_prob.shape == (1, 2), f"Y_prob shape {Y_prob.shape}"
    assert torch.allclose(
        Y_prob.sum(dim=1), torch.tensor([1.0]), atol=1e-5
    ), f"Y_prob no suma 1: {Y_prob}"
    assert Y_hat.shape == (1, 1), f"Y_hat shape {Y_hat.shape}"
    assert A.shape == (2, 200), f"A shape {A.shape}"
    # A ya viene con softmax sobre N → cada fila (clase) suma 1.
    assert torch.allclose(
        A.sum(dim=1), torch.ones(2), atol=1e-5
    ), f"A no normalizada sobre N: row sums {A.sum(dim=1)}"
    assert 'instance_scores_c' in results
    assert results['instance_scores_c'].shape == (200, 2), (
        f"c shape {results['instance_scores_c'].shape}"
    )

    # Con instance_eval
    model.train()
    logits, Y_prob, Y_hat, A, results = model(
        bag, label=label, instance_eval=True
    )
    assert 'instance_loss' in results
    assert 'inst_labels' in results
    assert 'inst_preds' in results
    assert 'instance_scores_c' in results
    assert not torch.isnan(results['instance_loss']), "instance_loss NaN"

    # Gradiente fluye desde el logits hacia bag classifier + fc projection.
    loss = logits.sum()
    loss.backward()
    assert model.classifiers[0].weight.grad is not None, (
        "bag classifier no recibió gradiente"
    )
    fc_grads = [p.grad for p in model.fc_projection.parameters()]
    assert all(g is not None for g in fc_grads), (
        "fc_projection no recibió gradiente"
    )

    print("[OK] §6.1 forward CPU random bag")


def test_W0_gradient_requires_Lmax():
    """Verificación R1/B.1: W_0 NO entrena con loss del bag solo;
    requiere L_max directa sobre c. Justifica empíricamente la decisión
    B.1.3 documentada en hipotesis.md §5.
    """
    torch.manual_seed(0)
    model = DSMIL_CLAM_MB(
        n_classes=2, embed_dim=512, dropout=0.0, k_sample=8,
    )
    model.train()
    bag = torch.randn(200, 512)
    label = torch.tensor([1])

    # (a) Loss SOLO sobre logits: W_0 NO debe recibir gradiente.
    model.zero_grad()
    logits, _, _, _, _ = model(bag, label=label, instance_eval=False)
    logits.sum().backward()
    W0_grad = model.dsmil_aggregator.i_classifier.weight.grad
    grad_norm_a = (
        W0_grad.abs().sum().item() if W0_grad is not None else 0.0
    )
    assert grad_norm_a < 1e-9, (
        f"W_0 recibió gradiente del logits solo (|grad|={grad_norm_a}). "
        f"Contradice R1/B.1 — el argmax debería bloquear el gradiente."
    )

    # (b) Loss que incluye c (simula L_max): W_0 SÍ debe recibir gradiente.
    model.zero_grad()
    logits, _, _, _, results = model(
        bag, label=label, instance_eval=False
    )
    c = results['instance_scores_c']  # [N, C]
    # L_max minimalista: CE sobre el parche de score máximo (réplica
    # dsmil.py:68-70). Solo para verificar el flujo de gradiente.
    max_pred, _ = torch.max(c, dim=0)  # [C]
    L_max = torch.nn.functional.cross_entropy(
        max_pred.view(1, -1), label.long()
    )
    (logits.sum() + 0.1 * L_max).backward()
    W0_grad = model.dsmil_aggregator.i_classifier.weight.grad
    grad_norm_b = (
        W0_grad.abs().sum().item() if W0_grad is not None else 0.0
    )
    assert grad_norm_b > 1e-9, (
        f"W_0 NO recibió gradiente con L_max sobre c (|grad|={grad_norm_b}). "
        f"Algo está roto en la conexión c → L_max → grad."
    )

    print(
        "[OK] W_0 sin grad bajo bag-only (|grad|={:.2e}); con grad bajo "
        "L_max (|grad|={:.2e}) — confirma R1/B.1 → B.1.3".format(
            grad_norm_a, grad_norm_b
        )
    )


def test_forward_real_pt():
    """§6.2 — forward CPU con un .pt real de clam_environ."""
    pt_path = Path(
        "/media/administrador/Storage1/sdonoso/clam_environ/"
        "environ/features/pt_files/101907.pt"
    )
    assert pt_path.is_file(), f"falta el .pt real: {pt_path}"

    # weights_only=True requerido por PyTorch ≥2.4 para tensores planos.
    try:
        bag = torch.load(pt_path, map_location="cpu", weights_only=True)
    except TypeError:
        # PyTorch <2.4 no acepta weights_only — fallback.
        bag = torch.load(pt_path, map_location="cpu")

    assert bag.dim() == 2, f"esperaba 2D, vino {tuple(bag.shape)}"
    assert bag.shape[1] == 512, (
        f"esperaba D=512 (CONCH), vino {bag.shape[1]}"
    )

    model = DSMIL_CLAM_MB(
        n_classes=2, embed_dim=512, dropout=0.25, k_sample=8,
    )
    model.eval()
    label = torch.tensor([1])

    with torch.no_grad():
        logits, Y_prob, Y_hat, A, results = model(
            bag, label=label, instance_eval=False
        )

    feat_norm = bag.norm(dim=1)  # L2 por parche
    print(f"[INFO] .pt real: {pt_path.name}")
    print(f"  shape bag             : {tuple(bag.shape)}  (N={bag.shape[0]})")
    print(f"  shape logits          : {tuple(logits.shape)}")
    print(f"  shape Y_prob          : {tuple(Y_prob.shape)}")
    print(f"  shape A               : {tuple(A.shape)}")
    print(f"  shape c               : {tuple(results['instance_scores_c'].shape)}")
    print(
        f"  range bag features    : "
        f"[{bag.min().item():.3f}, {bag.max().item():.3f}]"
    )
    print(
        f"  L2 norm parches       : mean={feat_norm.mean().item():.3f}  "
        f"std={feat_norm.std().item():.3f}  "
        f"min={feat_norm.min().item():.3f}  "
        f"max={feat_norm.max().item():.3f}"
    )
    print(
        f"  range logits          : "
        f"[{logits.min().item():.3f}, {logits.max().item():.3f}]"
    )
    print(f"  Y_prob                : {Y_prob.flatten().tolist()}")
    print(
        f"  A.sum(dim=1)          : {A.sum(dim=1).tolist()}  "
        f"(debería ser ~[1,1])"
    )
    print(
        f"  A entropy (clase 0)   : "
        f"{-(A[0] * (A[0] + 1e-12).log()).sum().item():.3f}  "
        f"(uniforme ≈ {torch.log(torch.tensor(float(bag.shape[0]))).item():.3f})"
    )
    print(
        f"  c range               : "
        f"[{results['instance_scores_c'].min().item():.3f}, "
        f"{results['instance_scores_c'].max().item():.3f}]"
    )

    assert not torch.isnan(logits).any()
    assert not torch.isinf(logits).any()
    assert torch.allclose(A.sum(dim=1), torch.ones(2), atol=1e-4)
    print("[OK] §6.2 forward CPU con .pt real")


class _FakeSlideDataset:
    """Mini dataset compatible con `compute_test_metrics`. Expone solo
    `slide_data['slide_id']` y se itera devolviendo `(bag, label)` por
    cada slide — suficiente para validar shapes/cálculo en CPU.

    Loader real (Generic_MIL_Dataset + get_split_loader) se ejercita en
    el smoke en GPU; acá validamos solo la lógica de métricas.
    """
    def __init__(self, slides):
        # slides: list[(slide_id, bag_tensor, label_int)]
        self._slides = slides
        import pandas as pd
        self.slide_data = pd.DataFrame({
            'slide_id': [s[0] for s in slides]
        })

    def __len__(self):
        return len(self._slides)


class _FakeLoader:
    """Mimetiza el iterador de un DataLoader CLAM: yields (data, label)
    con un dataset que tiene slide_data['slide_id']."""
    def __init__(self, dataset):
        self.dataset = dataset

    def __iter__(self):
        for _sid, bag, lbl in self.dataset._slides:
            yield bag, torch.tensor([lbl])


def test_compute_test_metrics():
    """Verifica que compute_test_metrics produce balanced_accuracy +
    confusion_matrix coherentes con sklearn sobre datos sintéticos.

    Construye 6 slides (3 positivos, 3 negativos) con bags pequeños.
    El modelo está en init aleatoria → sus predicciones serán
    arbitrarias, pero la INTEGRIDAD del cálculo (shapes, no-NaN,
    consistencia entre confusion y balanced_acc) es lo que validamos.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "train_dsmil",
        str(REPO_ROOT / "scripts" / "train_dsmil.py"),
    )
    train_dsmil = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(train_dsmil)

    torch.manual_seed(42)
    model = DSMIL_CLAM_MB(n_classes=2, embed_dim=512, dropout=0.25, k_sample=8)
    model.eval()
    device = torch.device("cpu")

    slides = []
    for i in range(6):
        N = 150 + i * 20  # bag sizes diferentes
        bag = torch.randn(N, 512)
        label = i % 2  # alterna 0/1
        slides.append((f"slide_{i:03d}", bag, label))

    loader = _FakeLoader(_FakeSlideDataset(slides))
    patient_results, test_metrics, preds_df = train_dsmil.compute_test_metrics(
        model, loader, device,
    )

    # patient_results: 1 entrada por slide.
    assert len(patient_results) == 6, f"patient_results len {len(patient_results)}"
    for sid in [f"slide_{i:03d}" for i in range(6)]:
        assert sid in patient_results
        assert 'prob' in patient_results[sid]
        assert patient_results[sid]['prob'].shape == (1, 2)

    # preds_df: 6 filas, columnas correctas.
    assert list(preds_df.columns) == ['slide_id', 'y_true', 'y_prob_si', 'y_pred']
    assert len(preds_df) == 6
    assert preds_df['y_prob_si'].between(0.0, 1.0).all(), \
        f"y_prob_si fuera de [0,1]: {preds_df['y_prob_si'].tolist()}"

    # Métricas: shapes y rangos.
    assert 'test_auc' in test_metrics
    assert 'test_acc' in test_metrics
    assert 'balanced_acc' in test_metrics
    assert 'confusion' in test_metrics
    cm = test_metrics['confusion']
    assert len(cm) == 2 and len(cm[0]) == 2, f"confusion shape {cm}"
    # La suma de la matriz de confusión debe ser n_test.
    cm_sum = sum(sum(row) for row in cm)
    assert cm_sum == test_metrics['n_test'] == 6, \
        f"sum(confusion)={cm_sum}, n_test={test_metrics['n_test']}"
    assert 0.0 <= test_metrics['test_acc'] <= 1.0
    assert 0.0 <= test_metrics['balanced_acc'] <= 1.0
    assert 0.0 <= test_metrics['test_auc'] <= 1.0

    # Consistencia interna: balanced_acc = mean(recall_clase_0, recall_clase_1).
    from sklearn.metrics import balanced_accuracy_score
    bal_check = balanced_accuracy_score(
        preds_df['y_true'].to_numpy(), preds_df['y_pred'].to_numpy()
    )
    assert abs(test_metrics['balanced_acc'] - bal_check) < 1e-9, \
        f"balanced_acc inconsistente: {test_metrics['balanced_acc']} vs {bal_check}"

    print(f"[OK] compute_test_metrics: 6 slides, "
          f"auc={test_metrics['test_auc']:.3f}, "
          f"acc={test_metrics['test_acc']:.3f}, "
          f"bal_acc={test_metrics['balanced_acc']:.3f}, "
          f"confusion={cm}")


def test_validate_one_epoch_no_early_stop():
    """Verifica que validate_one_epoch corre sin error y devuelve un
    dict con las 4 keys esperadas. EarlyStopping no se enchufa acá
    (eso se valida indirectamente en el smoke GPU)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "train_dsmil",
        str(REPO_ROOT / "scripts" / "train_dsmil.py"),
    )
    train_dsmil = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(train_dsmil)

    torch.manual_seed(0)
    model = DSMIL_CLAM_MB(n_classes=2, embed_dim=512, dropout=0.0, k_sample=8)
    device = torch.device("cpu")
    loss_fn = torch.nn.CrossEntropyLoss()

    slides = [(f"s_{i}", torch.randn(100 + 10 * i, 512), i % 2)
              for i in range(4)]
    loader = _FakeLoader(_FakeSlideDataset(slides))

    should_stop, val_metrics = train_dsmil.validate_one_epoch(
        epoch=0, model=model, loader=loader, loss_fn=loss_fn,
        device=device, early_stopping=None, ckpt_path=None,
    )
    assert should_stop is False
    for k in ['val_loss', 'val_error', 'val_auc', 'val_processed']:
        assert k in val_metrics, f"falta {k} en val_metrics"
    assert val_metrics['val_processed'] == 4
    assert not (val_metrics['val_loss'] != val_metrics['val_loss']), \
        "val_loss es NaN"
    assert 0.0 <= val_metrics['val_error'] <= 1.0

    print(f"[OK] validate_one_epoch: val_loss={val_metrics['val_loss']:.3f}, "
          f"val_auc={val_metrics['val_auc']:.3f}, "
          f"val_err={val_metrics['val_error']:.3f}")


if __name__ == "__main__":
    test_forward_random_bag()
    test_W0_gradient_requires_Lmax()
    test_forward_real_pt()
    test_compute_test_metrics()
    test_validate_one_epoch_no_early_stop()
    print("\nTodos los smoke tests CPU pasaron "
          "(§6.1 §6.2 + val_loop + test_loop).")
