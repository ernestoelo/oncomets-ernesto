"""DSMIL_CLAM_MB — wrapper sobre CLAM_MB que sustituye el aggregator.

Hereda de `CLAM_MB` y reemplaza el `Attn_Net_Gated` por el aggregator
dual-stream de DSMIL. Conserva del CLAM_MB original:

- Proyección fc (Linear→ReLU→Dropout) sobre features CONCH 512-dim.
- `bag_classifier` (nn.Linear por clase, `models/model_clam.py:198`).
- `inst_eval` / `inst_eval_out` (operan sobre β de DSMIL en lugar de α
  gated). Métodos heredados sin modificar.
- Firma de `forward()` compatible con `core_utils.train_loop_clam`
  (devuelve `logits, Y_prob, Y_hat, A_raw, results_dict`).

Expone adicionalmente `instance_scores_c` en `results_dict` para que el
training script compute `L_max` sobre el instance scorer W_0
(decisión R1 = B.1.3, w_max = 0.1; `hipotesis.md` §5).

Decisiones cerradas (hipotesis.md §4, §5):
- `passing_v=False` (Identity, default oficial `dsmil.py:41`).
- `nonlinear=True` (q-net MLP, default oficial `dsmil.py:30-33`).
- escala `/√128` (Q.shape[1]) como `dsmil.py:56`, NO `/√D`.
- `Conv1d` final de DSMIL descartado — bag classifier de CLAM lo
  reemplaza (preserva multi-clase softmax + CE).
"""

import sys

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

# Import de CLAM_MB desde el codebase READ-ONLY de Sebastián.
# NO copiamos ni modificamos nada de clam_environ/; se inserta el path en
# tiempo de import (CLAUDE.md, "Reglas operativas no negociables" §2).
_CLAM_ENVIRON_PATH = "/media/administrador/Storage1/sdonoso/clam_environ"
if _CLAM_ENVIRON_PATH not in sys.path:
    sys.path.insert(0, _CLAM_ENVIRON_PATH)

from models.model_clam import CLAM_MB  # noqa: E402

from .aggregator import DSMIL_Aggregator  # noqa: E402


class DSMIL_CLAM_MB(CLAM_MB):
    """CLAM_MB con aggregator DSMIL dual-stream.

    Args (sobre los heredados de CLAM_MB):
        dsmil_nonlinear: q-net no-lineal (True = oficial).
        dsmil_passing_v: v-net activa (False = Identity = oficial).
    """

    def __init__(self, gate=True, size_arg="small", dropout=0.,
                 k_sample=8, n_classes=2,
                 instance_loss_fn=nn.CrossEntropyLoss(),
                 subtyping=False, embed_dim=512,
                 dsmil_nonlinear=True, dsmil_passing_v=False):
        super().__init__(
            gate=gate, size_arg=size_arg, dropout=dropout,
            k_sample=k_sample, n_classes=n_classes,
            instance_loss_fn=instance_loss_fn,
            subtyping=subtyping, embed_dim=embed_dim,
        )
        size = self.size_dict[size_arg]
        fc = [nn.Linear(size[0], size[1]), nn.ReLU(), nn.Dropout(dropout)]
        self.fc_projection = nn.Sequential(*fc)
        self.dsmil_aggregator = DSMIL_Aggregator(
            input_size=size[1],
            output_class=n_classes,
            nonlinear=dsmil_nonlinear,
            passing_v=dsmil_passing_v,
        )
        # El attention_net heredado (Linear+ReLU+Dropout+Attn_Net_Gated)
        # no se usa en este forward. Desregistrarlo evita que sus pesos
        # entren a model.parameters() y al optimizer.
        del self.attention_net

    def forward(self, h, label=None, instance_eval=False,
                return_features=False, attention_only=False):
        h_proj = self.fc_projection(h)  # [N, D=512]

        # DSMIL aggregator: A ya viene con softmax sobre N → NO aplicar
        # otro softmax (diferencia con CLAM_MB línea 213).
        A_dsmil, V, c = self.dsmil_aggregator(h_proj)
        # A_dsmil: [N, C]; V: [N, D]; c: [N, C]

        A = A_dsmil.transpose(0, 1).contiguous()  # [C, N]  (convención CLAM)
        if attention_only:
            return A
        A_raw = A  # nombre histórico de CLAM_MB; acá ya es post-softmax

        if instance_eval:
            total_inst_loss = 0.0
            all_preds = []
            all_targets = []
            inst_labels = F.one_hot(label, num_classes=self.n_classes).squeeze()
            for i in range(len(self.instance_classifiers)):
                inst_label = inst_labels[i].item()
                classifier = self.instance_classifiers[i]
                if inst_label == 1:
                    instance_loss, preds, targets = self.inst_eval(
                        A[i], V, classifier
                    )
                    all_preds.extend(preds.cpu().numpy())
                    all_targets.extend(targets.cpu().numpy())
                else:
                    if self.subtyping:
                        instance_loss, preds, targets = self.inst_eval_out(
                            A[i], V, classifier
                        )
                        all_preds.extend(preds.cpu().numpy())
                        all_targets.extend(targets.cpu().numpy())
                    else:
                        continue
                total_inst_loss += instance_loss
            if self.subtyping:
                total_inst_loss /= len(self.instance_classifiers)

        M = torch.mm(A, V)  # [C, D]
        logits = torch.empty(1, self.n_classes).float().to(M.device)
        for cc in range(self.n_classes):
            logits[0, cc] = self.classifiers[cc](M[cc])
        Y_hat = torch.topk(logits, 1, dim=1)[1]
        Y_prob = F.softmax(logits, dim=1)

        if instance_eval:
            results_dict = {
                'instance_loss': total_inst_loss,
                'inst_labels': np.array(all_targets),
                'inst_preds': np.array(all_preds),
                'instance_scores_c': c,
            }
        else:
            results_dict = {'instance_scores_c': c}
        if return_features:
            results_dict.update({'features': M})
        return logits, Y_prob, Y_hat, A_raw, results_dict
