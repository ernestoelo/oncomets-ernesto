"""DSMIL aggregator dual-stream.

Réplica del módulo de `DSMIL_official_reference/dsmil.py` (HEAD 80465ed),
adaptado para integración con `CLAM_MB`. Diferencias deliberadas vs el
oficial:

- NO incluye el `Conv1d` final (`fcc`) que mezcla clases en `BClassifier`.
  El bag classifier viene de `CLAM_MB` (`nn.Linear` por clase,
  `models/model_clam.py:198`).
- Encapsula Stream 1 (instance scorer W_0) y Stream 2 (q/v + atención
  relacional) en un único módulo que devuelve `(A, V, c)`. El caller
  (`DSMIL_CLAM_MB`) integra `A` con `inst_eval` y `V` con el bag
  classifier; `c` se expone para que el training script compute `L_max`
  (decisión R1 = B.1.3, w_max = 0.1, ver
  `sprints/B4_sprint4/objetivo_3_modulo_mil_alternativo/hipotesis.md`).

Referencias:
- Paper: Li, Li & Eliceiri, *Dual-stream MIL...*, CVPR 2021.
  arXiv:2011.08939.
- Código: `DSMIL_official_reference/dsmil.py:6-62`.
"""

import math

import torch
import torch.nn as nn
import torch.nn.functional as F


class DSMIL_Aggregator(nn.Module):
    """Replaces `Attn_Net_Gated` of `CLAM_MB`. Operates on already-projected
    features (post Linear+ReLU+Dropout) and returns attention β, info
    vectors V, and instance scores c.

    Args:
        input_size: feature dim D (post-proyección de CLAM = 512).
        output_class: nº de clases (= n_classes de CLAM).
        nonlinear: q-net no-lineal (True = código oficial,
            Linear→ReLU→Linear→Tanh dim 128; False = Linear, paper Ec. 4).
        passing_v: v-net (True = MLP; False = Identity, default oficial).
    """

    def __init__(self, input_size, output_class,
                 nonlinear=True, passing_v=False):
        super().__init__()
        # Stream 1: instance classifier W_0 (FCLayer del repo oficial).
        self.i_classifier = nn.Linear(input_size, output_class)

        # Stream 2: q-net (query). Dim 128 hardcoded en el código oficial.
        if nonlinear:
            self.q = nn.Sequential(
                nn.Linear(input_size, 128),
                nn.ReLU(),
                nn.Linear(128, 128),
                nn.Tanh(),
            )
        else:
            self.q = nn.Linear(input_size, 128)

        # Stream 2: v-net. Default = Identity (decisión cerrada en §4).
        if passing_v:
            self.v = nn.Sequential(
                nn.Linear(input_size, input_size),
                nn.ReLU(),
            )
        else:
            self.v = nn.Identity()

        self.output_class = output_class

    def forward(self, feats):
        """Args:
            feats: [N, D] features ya proyectadas (Linear+ReLU+Dropout del
                wrapper, equivalente al input que `Attn_Net_Gated` ve
                dentro del `nn.Sequential` original de `CLAM_MB`).

        Returns:
            A: [N, n_classes] atención relacional β POST-softmax sobre N.
                NO aplicar softmax aguas abajo (diferencia con CLAM, que
                aplica softmax después del transpose).
            V: [N, D] information vectors (= feats si passing_v=False).
                Toma el rol de `h` en CLAM (input de `inst_eval` y de
                `M = A·h`).
            c: [N, n_classes] scores raw del instance scorer W_0
                (pre-softmax). Expuesto para que el training compute
                L_max sobre c[m] (R1 = B.1.3).
        """
        # Stream 1: scores por instancia.
        c = self.i_classifier(feats)  # [N, C]

        # Stream 2: q y v.
        V = self.v(feats)  # [N, D]
        Q = self.q(feats)  # [N, 128]

        # Parche crítico por clase: argmax de c sobre N (vía sort).
        # Réplica dsmil.py:52-53.
        _, m_indices = torch.sort(c, dim=0, descending=True)  # [N, C]
        m_feats = torch.index_select(
            feats, dim=0, index=m_indices[0, :]
        )  # [C, D]
        q_max = self.q(m_feats)  # [C, 128]

        # Atención relacional: Q × q_max^T, escalada /√128.
        # Réplica dsmil.py:55-56.
        A = torch.mm(Q, q_max.transpose(0, 1))  # [N, C]
        scale = math.sqrt(Q.shape[1])
        A = F.softmax(A / scale, dim=0)  # softmax sobre N (cada col suma 1)

        return A, V, c
