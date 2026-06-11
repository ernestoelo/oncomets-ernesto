"""models_pathpt/pathpt.py — modelo PathPT-CONCH (PPTCONCH de la referencia, port).

Junta θ_v (módulo espacial) + θ_t (prompt-tuning sobre el text encoder de CONCH) y
clasifica CADA parche por coseno imagen-texto. Port de `PPTCONCH` (config
vision_grad=True, learnable='token') de `PathPT_reference/models/PathPT_model_CONCH.py`.

ENTRADA: features de parche en el **espacio contrastivo** [N, 512]. ⚠️ Las .pt
cacheadas de Sebastián son `forward_no_head` (pre-proyección): el DRIVER aplica
`feat @ proj_contrast` ANTES de pasar al modelo (no se hace acá, para que el modelo
sea testeable con features sintéticas y para no acoplar el modelo a CONCH.visual).

SALIDA: (None, patch_logits) con patch_logits = softmax(sims*10, -1)  [N, n_cls].
NOTA FIEL: la referencia pasa ESTE patch_logits (ya softmax) a PatchSSLoss, que vuelve
a aplicar cross_entropy/softmax (doble-softmax). Se replica tal cual (alcance A = port
fiel); no es un bug a "arreglar" — cambiarlo testearía otra cosa.

CONGELADO: el CONCH base (Φ_v vía proj en el driver, Φ_t = text transformer). ENTRENA:
θ_v (`spatial`) + θ_t (`prompt_learner.ctx`). Usar `trainable_parameters()`.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F

from .prompt import CONCHTextEncoder, PromptLearnerCONCH
from .spatial import MultiKernelConv1DTrans

LOGIT_SCALE = 10.0  # τ=0.1 (ref: softmax(logits*10))


class PathPTCONCH(nn.Module):
    def __init__(self, classnames_lst, conch_model, device, n_ctx=32,
                 ctx_init="a histopathology image of ", vfeat_dim=512,
                 vision_grad=True):
        super().__init__()
        self.device = device
        self.vision_grad = vision_grad
        self.n_classes = len(classnames_lst)
        self.prompt_learner = PromptLearnerCONCH(
            classnames_lst, conch_model, device, n_ctx=n_ctx, ctx_init=ctx_init)
        self.text_encoder = CONCHTextEncoder(conch_model, embed_cls=True)
        if vision_grad:
            self.spatial = MultiKernelConv1DTrans(in_channels=vfeat_dim, out_channels=vfeat_dim)
        else:
            self.spatial = None
        self._freeze_base()

    def _freeze_base(self):
        """Congela todo menos θ_v (spatial) + θ_t (prompt_learner.ctx)."""
        for name, p in self.named_parameters():
            p.requires_grad = name.startswith("spatial.") or name == "prompt_learner.ctx"

    def trainable_parameters(self):
        return [p for p in self.parameters() if p.requires_grad]

    def encode_text(self):
        """θ_t → text features [n_cls, 512] (normalizadas)."""
        prompt_emb = self.prompt_learner()                       # [n_cls,127,768]
        tf = self.text_encoder(prompt_emb, self.prompt_learner.tokenized_prompts)
        return tf / tf.norm(dim=-1, keepdim=True)

    def forward(self, image_features):
        # image_features: [N,512] contrastivo (o [1,N,512])
        if self.vision_grad:
            image_features = self.spatial(image_features)        # θ_v → [1,N,512]
        image_features = image_features / image_features.norm(dim=-1, keepdim=True)
        text_features = self.encode_text()                       # [n_cls,512]

        logits = image_features @ text_features.t()              # [1,N,n_cls] o [N,n_cls]
        if logits.dim() == 1:
            logits = logits.unsqueeze(0)
        elif logits.dim() == 3:
            logits = logits.squeeze(0)                           # [N,n_cls]
        patch_logits = F.softmax(logits * LOGIT_SCALE, dim=-1)
        return None, patch_logits
