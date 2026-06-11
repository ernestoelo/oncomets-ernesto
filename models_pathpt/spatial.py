"""models_pathpt/spatial.py — θ_v: módulo de conciencia espacial de PathPT.

Port FIEL de `PathPT_reference/model_utils.py` (pin 0ab7f1b), clases
`MultiKernelConv1DTrans` + `TransLayer`, fijado a dim=512 (espacio contrastivo
de CONCH; el paper usa 768 para PLIP/MUSK pero CONCH contrastivo es 512).

Idea (funcionamiento_pathpt.md §3.1): refina cada parche con su vecindario y
dependencias de largo alcance, **conservando 1 vector por parche** (NO colapsa a
slide). La "espacialidad" entra por el ORDEN de los parches: el driver los ordena
por coordenadas (x,y) del h5 antes de pasarlos, de modo que el `Conv1d` (kernels
3/5/7 sobre la dimensión de parches) capture vecindarios locales; el `TransLayer`
(NystromAttention) agrega dependencias globales.

Entrada/salida: [N, 512] (o [B, N, 512]) -> [B, N, 512] (preserva N).
Depende de `nystrom_attention` (vendorizado en clam_testing2/.pylibs; el driver
y el test lo ponen en sys.path/PYTHONPATH).
"""
import torch
import torch.nn as nn

from nystrom_attention import NystromAttention


class TransLayer(nn.Module):
    """Bloque global: LayerNorm + NystromAttention residual (port verbatim)."""

    def __init__(self, norm_layer=nn.LayerNorm, dim=512):
        super().__init__()
        self.norm = norm_layer(dim)
        self.attn = NystromAttention(
            dim=dim,
            dim_head=dim // 8,
            heads=8,
            num_landmarks=dim // 2,   # nº de landmarks
            pinv_iterations=6,        # iteraciones Moore-Penrose (6, recomendado por el paper)
            residual=True,            # residual extra con value (converge más rápido)
            dropout=0.1,
        )

    def forward(self, x):
        x = x + self.attn(self.norm(x))
        return x


class MultiKernelConv1DTrans(nn.Module):
    """θ_v: conv1d multi-kernel (3/5/7) residual + TransLayer global.

    Conserva N parches. Entrada [N, C] o [B, N, C]; salida [B, N, C].
    """

    def __init__(self, in_channels=512, out_channels=512):
        super().__init__()
        self.conv1 = nn.Conv1d(in_channels, out_channels, kernel_size=3, padding=1)
        self.conv2 = nn.Conv1d(in_channels, out_channels, kernel_size=5, padding=2)
        self.conv3 = nn.Conv1d(in_channels, out_channels, kernel_size=7, padding=3)
        self.norm = nn.LayerNorm(out_channels)
        self.active = nn.ReLU()
        self.cls_token = nn.Parameter(torch.randn(1, 1, out_channels))  # presente en ref (sin uso en este forward)
        self.translayer = TransLayer(dim=out_channels)

    def forward(self, x):
        # [N, C] -> [1, N, C]
        if x.dim() == 2:
            x = x.unsqueeze(0)
        inp = x.permute(0, 2, 1)  # [B, C, N] para Conv1d

        o1 = self.active(self.norm(self.conv1(inp).permute(0, 2, 1)))
        o2 = self.active(self.norm(self.conv2(inp).permute(0, 2, 1)))
        o3 = self.active(self.norm(self.conv3(inp).permute(0, 2, 1)))
        output = o1 + o2 + o3 + x      # suma multi-kernel + residual con la entrada

        output = self.translayer(output)
        output = self.norm(output)
        return output                  # [B, N, C], preserva N
