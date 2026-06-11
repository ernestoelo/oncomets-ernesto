"""models_pathpt — PathPT-CONCH portado a OncoMets (Etapa 1, B5).

Port FIEL del repo de referencia `MAGIC-AI4Med/PathPT` (vendorizado en
clam_testing2/PathPT_reference, pin 0ab7f1b), adaptado a:
  - nuestro CONCH (`conch.open_clip_custom`, en clam_environ/CONCH, READ-ONLY),
  - features .pt cacheadas `forward_no_head` → el driver aplica `proj_contrast`,
  - tarea BINARIA presencia/ausencia (no subtyping) → el driver maneja el
    pseudo-etiquetado de slides `ausente` (todos los parches normales).

NO toca clam_environ. Entrena solo θ_v (módulo espacial) + θ_t (32 prompts CoOp);
CONCH congelado. Pre-registración: sprints/B5_sprint5/pathpt/etapa1_prereg_necrosis.md.
Depende de `nystrom_attention` (clam_testing2/.pylibs).
"""
from .losses import PatchSSLoss, balanced_ce_loss
from .pathpt import PathPTCONCH
from .prompt import CONCHTextEncoder, PromptLearnerCONCH
from .spatial import MultiKernelConv1DTrans, TransLayer

__all__ = [
    "PathPTCONCH",
    "MultiKernelConv1DTrans",
    "TransLayer",
    "PromptLearnerCONCH",
    "CONCHTextEncoder",
    "PatchSSLoss",
    "balanced_ce_loss",
]
