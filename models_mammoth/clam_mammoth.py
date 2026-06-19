"""clam_mammoth.py — CLAM_MB con la primera capa lineal reemplazada por Mammoth.

Mammoth (*Mixture of Mini Experts in Pathology*, Shao et al., ICLR 2026, Mahmood
Lab) reemplaza el `nn.Linear` que proyecta los features del encoder (CONCH 512)
al espacio interno de la MIL, por un **mixture-of-experts de bajo rango (LoRA)
con ruteo por slots**. Es drop-in: misma forma de entrada/salida que la lineal.
Motivación: *instance-gradient interference* — parches de fenotipos distintos en
una misma slide tiran gradientes en conflicto sobre la capa lineal única; el
ruteo a expertos los separa (README MAMMOTH + paper §"Main Findings").

**Delta mínimo vs el CLAM_MB de Sebastián (regla 2 — no se toca `clam_environ/`):**
`CLAM_MB_Mammoth` es **subclase de `CLAM_MB`** y solo re-implementa `__init__`
para construir el `attention_net` con `MammothPatchEmbed` en lugar de
`nn.Linear(size[0], size[1])`. `forward`, `inst_eval`, `inst_eval_out` se heredan
**verbatim** → la comparación CLAM vs CLAM+mammoth difiere SOLO en la 1ª capa
(paired por construcción a nivel de arquitectura, [[patron-paired-comparison-reuso-splits]]).

**`keep_slots=False` por defecto** (decisión Obj 6 #1): Mammoth devuelve los N
parches transformados [N, output_dim] — misma semántica de attention pooling e
instance-loss top-k que el baseline. `keep_slots=True` (salida E·S agregadas)
queda como variante posterior, no en la 1ª pasada.

NUNCA correr con `python` a secas (workaround B). Usar el binario absoluto del env
`clam_latest` o lanzar vía `sbatch`.
"""
from __future__ import annotations

import sys

import torch.nn as nn

# El CLAM_MB y los Attn_Net viven en el codebase READ-ONLY de Sebastián. Mismo
# patrón de import que scripts/train_dsmil.py (clam_environ en sys.path).
_CLAM_ENVIRON = "/media/administrador/Storage1/sdonoso/clam_environ"
if _CLAM_ENVIRON not in sys.path:
    sys.path.insert(0, _CLAM_ENVIRON)

from models.model_clam import CLAM_MB, Attn_Net, Attn_Net_Gated  # noqa: E402

try:
    from mammoth import Mammoth
except ImportError:  # pragma: no cover
    Mammoth = None


# Hiperparámetros recomendados por el paper (README MAMMOTH "recommended
# hyperparameters"). Con auto_rank=True el rank se calcula para mantener el
# conteo de parámetros comparable a la capa lineal original.
MAMMOTH_DEFAULTS = dict(
    num_experts=30,
    num_slots=10,
    num_heads=16,
    slot_dim=256,
    dropout=0.1,
    slot_dropout=0.0,   # Obj 3 B5: regularizador del ruteo. Default 0.0 = retro-
                        # compatible con los baselines (keep_slots=False, jobs 4229/4246)
                        # y mantiene el Brazo 1 (keep_slots=True) PURO. Brazo 2 pasa 0.1.
    keep_slots=False,
    share_lora_weights=True,
    auto_rank=True,
)


class MammothPatchEmbed(nn.Module):
    """Wrapper drop-in del `nn.Linear` de patch embed de CLAM.

    CLAM pasa los features como `[N_patches, input_dim]` (sin dimensión de batch);
    Mammoth espera `[B, N, input_dim]`. Este wrapper agrega/quita el eje de batch.

    Con `keep_slots=False` la salida es `[N, output_dim]` (los N parches
    transformados) → idéntica forma a la lineal que reemplaza.
    """

    def __init__(
        self,
        input_dim,
        output_dim,
        num_experts=MAMMOTH_DEFAULTS["num_experts"],
        num_slots=MAMMOTH_DEFAULTS["num_slots"],
        num_heads=MAMMOTH_DEFAULTS["num_heads"],
        slot_dim=MAMMOTH_DEFAULTS["slot_dim"],
        dropout=MAMMOTH_DEFAULTS["dropout"],
        slot_dropout=MAMMOTH_DEFAULTS["slot_dropout"],
        keep_slots=MAMMOTH_DEFAULTS["keep_slots"],
        share_lora_weights=MAMMOTH_DEFAULTS["share_lora_weights"],
        auto_rank=MAMMOTH_DEFAULTS["auto_rank"],
    ):
        super().__init__()
        if Mammoth is None:
            raise ImportError(
                "No se pudo importar Mammoth. El paquete `mammoth-moe` debe estar "
                "instalado en el env clam_latest (lo está, editable desde "
                "clam_testing/MAMMOTH). Reinstalar: pip install mammoth-moe"
            )
        self.keep_slots = keep_slots
        self.mammoth = Mammoth(
            input_dim=input_dim,
            dim=output_dim,
            num_experts=num_experts,
            num_slots=num_slots,
            num_heads=num_heads,
            slot_dim=slot_dim,
            dropout=dropout,
            slot_dropout=slot_dropout,   # solo actúa en training (Mammoth.get_weights)
            keep_slots=keep_slots,
            share_lora_weights=share_lora_weights,
            auto_rank=auto_rank,
        )

    def forward(self, x):
        was_unbatched = False
        if x.dim() == 2:                # [N, d] -> [1, N, d]
            x = x.unsqueeze(0)
            was_unbatched = True
        x = self.mammoth(x)
        if was_unbatched:               # [1, M, d] -> [M, d]
            x = x.squeeze(0)
        return x


class CLAM_MB_Mammoth(CLAM_MB):
    """CLAM_MB con la 1ª capa lineal reemplazada por MammothPatchEmbed.

    Réplica EXACTA de `CLAM_MB.__init__` (clam_environ/models/model_clam.py:186)
    salvo la primera entrada de `fc`: `nn.Linear(size[0], size[1])` →
    `MammothPatchEmbed(size[0], size[1], ...)`. Todo lo demás (clasificadores de
    bag, instance classifiers, k_sample, forward heredado) es idéntico.
    """

    def __init__(
        self,
        gate=True,
        size_arg="small",
        dropout=0.0,
        k_sample=8,
        n_classes=2,
        instance_loss_fn=nn.CrossEntropyLoss(),
        subtyping=False,
        embed_dim=512,
        mammoth_num_experts=MAMMOTH_DEFAULTS["num_experts"],
        mammoth_num_slots=MAMMOTH_DEFAULTS["num_slots"],
        mammoth_num_heads=MAMMOTH_DEFAULTS["num_heads"],
        mammoth_slot_dim=MAMMOTH_DEFAULTS["slot_dim"],
        mammoth_slot_dropout=MAMMOTH_DEFAULTS["slot_dropout"],
        mammoth_keep_slots=MAMMOTH_DEFAULTS["keep_slots"],
    ):
        nn.Module.__init__(self)
        self.size_dict = {"small": [embed_dim, 512, 256], "big": [embed_dim, 512, 384]}
        size = self.size_dict[size_arg]

        # >>> ÚNICO delta vs CLAM_MB: la 1ª capa lineal -> MammothPatchEmbed.
        fc = [
            MammothPatchEmbed(
                input_dim=size[0],
                output_dim=size[1],
                num_experts=mammoth_num_experts,
                num_slots=mammoth_num_slots,
                num_heads=mammoth_num_heads,
                slot_dim=mammoth_slot_dim,
                dropout=dropout,
                slot_dropout=mammoth_slot_dropout,
                keep_slots=mammoth_keep_slots,
                share_lora_weights=True,
                auto_rank=True,
            ),
            nn.ReLU(),
            nn.Dropout(dropout),
        ]
        # <<< fin del delta. Lo de abajo es idéntico a CLAM_MB.__init__.

        if gate:
            attention_net = Attn_Net_Gated(L=size[1], D=size[2], dropout=dropout, n_classes=n_classes)
        else:
            attention_net = Attn_Net(L=size[1], D=size[2], dropout=dropout, n_classes=n_classes)
        fc.append(attention_net)
        self.attention_net = nn.Sequential(*fc)
        bag_classifiers = [nn.Linear(size[1], 1) for _ in range(n_classes)]
        self.classifiers = nn.ModuleList(bag_classifiers)
        instance_classifiers = [nn.Linear(size[1], 2) for _ in range(n_classes)]
        self.instance_classifiers = nn.ModuleList(instance_classifiers)
        self.k_sample = k_sample
        self.instance_loss_fn = instance_loss_fn
        self.n_classes = n_classes
        self.subtyping = subtyping
