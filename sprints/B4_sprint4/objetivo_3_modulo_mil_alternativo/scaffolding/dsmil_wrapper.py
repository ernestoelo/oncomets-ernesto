"""dsmil_wrapper.py — SKELETON del módulo MIL alternativo (DSMIL).

================================================================================
ESTADO: SCAFFOLDING NO FUNCIONAL. Sujeto a confirmación en reunión.
================================================================================

Este archivo es un ESQUELETO. Importa y compila sin error, pero la lógica
central de cada `forward` levanta `NotImplementedError`. No entrena nada.

Qué hay aquí:
  - `DSMILAggregator` : la rama de pooling dual-stream de DSMIL (Li et al.,
                        CVPR 2021). Es lo único arquitectónicamente nuevo.
  - `DSMIL_CLAM_MB`   : el wrapper que enchufa ese aggregator en el lugar del
                        `Attn_Net_Gated` de `CLAM_MB`, conservando el resto
                        del pipeline (fc de entrada, bag classifier, rama
                        instance). Respeta la firma de `CLAM_MB.forward`.

Por qué el skeleton subclasea `nn.Module` y NO `CLAM_MB`:
  importar `CLAM_MB` exige meter `clam_environ/` en `sys.path` y puede fallar
  por `timm` en `models/__init__.py` (ver CLAUDE.md). Para que
  `import scaffolding.dsmil_wrapper` NUNCA explote, el skeleton no importa
  nada de `clam_environ/` a nivel de módulo. La implementación efectiva
  decidirá entre subclasear `CLAM_MB` o componerlo; ese import irá dentro de
  `__init__`, no en el top-level.

Referencias para la implementación efectiva (NO inventar la arquitectura):
  - Paper            : ../../papers/dsmil_li2021.pdf  (arXiv 2011.08939)
  - Código oficial   : clam_testing2/DSMIL_official_reference/dsmil.py  (HEAD 80465ed)
  - Argumento/diagrama: ../propuesta_dsmil.md
  - Integración      : ../plan_integracion.md

Antes de commitear la versión funcional de este archivo: pasar por el agente
`reviewer` (regla 9 del proyecto — toca arquitectura de modelo).
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


class DSMILAggregator(nn.Module):
    """Rama de pooling dual-stream de DSMIL. SKELETON.

    Reemplaza el `Attn_Net_Gated` de CLAM. Calcula la representación del bag
    como atención RELACIONAL al parche crítico, en vez de atención absoluta.

    Streams (ver propuesta_dsmil.md §Argumento arquitectónico):
      Stream 1 — scoring por instancia: c_i = w_c . h_i  ->  parche crítico
                 h_m = argmax_i c_i.
      Stream 2 — atención relacional: q_i = W_q h_i,  k_m = W_q h_m,
                 beta_i = softmax(<q_i, k_m> / sqrt(dim_q)),
                 bag rep  M_c = sum_i beta_{i,c} (W_v h_i).

    Correspondencia con dsmil.py oficial:
      Stream 1  <->  IClassifier / FCLayer.fc
      Stream 2  <->  BClassifier (self.q, self.v, el producto interno y softmax)
      NOTA: el `nn.Conv1d` final de BClassifier (clasificador de bag de DSMIL)
            NO se usa aquí — el bag classifier lo aporta CLAM_MB.
    """

    def __init__(self, in_dim: int = 512, n_classes: int = 2,
                 q_dim: int = 128, dropout_v: float = 0.0,
                 passing_v: bool = False, nonlinear: bool = True):
        """
        Args:
            in_dim     : dimensión de los embeddings de parche que entran al
                         aggregator. Tras el `fc` de CLAM es 512 (size[1]).
            n_classes  : nº de clases clínicas (C). DSMIL_MB produce un bag
                         rep por clase.
            q_dim      : dimensión del espacio de queries (128 en el oficial).
            dropout_v  : dropout de la v-net (solo si passing_v=True).
            passing_v  : si True, la v-net es un MLP; si False, Identidad
                         (default del repo oficial).
            nonlinear  : si True, la q-net es un MLP con ReLU+Tanh; si False,
                         un Linear simple.
        """
        super().__init__()
        self.in_dim = in_dim
        self.n_classes = n_classes
        self.q_dim = q_dim

        # TODO(impl): Stream 1 — scorer por instancia.
        #   Oficial: nn.Linear(in_dim, n_classes)  (IClassifier.fc / FCLayer)
        #   self.instance_scorer = nn.Linear(in_dim, n_classes)
        self.instance_scorer = None  # TODO

        # TODO(impl): Stream 2 — q-net (proyección a queries).
        #   Oficial (nonlinear=True):
        #     nn.Sequential(nn.Linear(in_dim, q_dim), nn.ReLU(),
        #                   nn.Linear(q_dim, q_dim), nn.Tanh())
        #   nonlinear=False: nn.Linear(in_dim, q_dim)
        self.q_net = None  # TODO

        # TODO(impl): Stream 2 — v-net (proyección de valores).
        #   Oficial: nn.Identity() por defecto; si passing_v:
        #     nn.Sequential(nn.Dropout(dropout_v),
        #                   nn.Linear(in_dim, in_dim), nn.ReLU())
        #   La salida de v-net define la dim del bag rep -> mantener = in_dim
        #   para que el bag classifier de CLAM (Linear 512->1) calce.
        self.v_net = None  # TODO

        # NOTA: NO hay bag_classifier aquí. El clasificador de bag lo pone
        # DSMIL_CLAM_MB reutilizando `CLAM_MB.classifiers` (Linear in_dim->1
        # por clase). Shapes a respetar: M -> [n_classes, in_dim].

    def forward(self, h: torch.Tensor):
        """Pooling dual-stream.

        Args:
            h: embeddings de parche [N, in_dim] (tras el `fc` de CLAM).

        Returns:
            A: atención relacional [n_classes, N] (post-softmax sobre N).
            M: representación de bag por clase [n_classes, in_dim].
            c: scores de instancia [N, n_classes] (Stream 1, para la rama
               max-pooling / instance loss).

        Esquema de la implementación efectiva (ver dsmil.py:46-62):
            c      = instance_scorer(h)                     # [N, C]
            _, idx = torch.sort(c, dim=0, descending=True)  # critical sort
            h_m    = h[idx[0, :]]                           # [C, in_dim]
            Q      = q_net(h)                               # [N, q_dim]
            q_max  = q_net(h_m)                             # [C, q_dim]
            A      = softmax(Q @ q_max.T / sqrt(q_dim), 0)  # [N, C]
            V      = v_net(h)                               # [N, in_dim]
            M      = (A.T @ V)                              # [C, in_dim]
        """
        # TODO(impl): implementar el dual-stream descrito arriba.
        raise NotImplementedError(
            "DSMILAggregator.forward es un skeleton. Implementar tras "
            "confirmar el módulo en la reunión (ver ../README.md)."
        )


class DSMIL_CLAM_MB(nn.Module):
    """Wrapper: CLAM_MB con la rama de pooling reemplazada por DSMIL. SKELETON.

    Conserva del pipeline de CLAM (ver plan_integracion.md §3):
      - `fc` de entrada: Linear(embed_dim -> 512) . ReLU . Dropout.
      - bag classifier: un nn.Linear(512, 1) por clase.
      - rama instance: instance_classifiers + inst_eval/inst_eval_out
                       (SmoothTop1SVM), `--B` sin tocar.
    Reemplaza:
      - SOLO el `Attn_Net_Gated` -> `DSMILAggregator`.

    `forward` respeta la firma de `CLAM_MB.forward` para que
    `utils/core_utils.py` (train_loop_clam) lo consuma sin cambios:
        return logits, Y_prob, Y_hat, A_raw, results_dict
    """

    def __init__(self, gate: bool = True, size_arg: str = "small",
                 dropout: float = 0.25, k_sample: int = 8, n_classes: int = 2,
                 instance_loss_fn=None, subtyping: bool = False,
                 embed_dim: int = 512):
        """Firma alineada con `CLAM_MB.__init__` (model_clam.py:186-205).

        Args:
            embed_dim : dim de las features CONCH de entrada. 512 (CONCH).
            k_sample  : top-B/bottom-B del instance path (`--B`, default 8).
            n_classes : nº de clases clínicas.
            (resto)   : ver CLAM_MB; se mantienen por compatibilidad.
        """
        super().__init__()
        # size_dict["small"] = [embed_dim, 512, 256]  (model_clam.py:189)
        self.size_dict = {"small": [embed_dim, 512, 256],
                          "big": [embed_dim, 512, 384]}
        size = self.size_dict[size_arg]
        self.n_classes = n_classes
        self.k_sample = k_sample
        self.subtyping = subtyping
        self.instance_loss_fn = instance_loss_fn

        # --- bloque CONSERVADO de CLAM: fc de entrada -------------------------
        # TODO(impl): self.fc = nn.Sequential(
        #     nn.Linear(size[0], size[1]), nn.ReLU(), nn.Dropout(dropout))
        self.fc = None  # TODO

        # --- bloque REEMPLAZADO: pooling dual-stream DSMIL -------------------
        # TODO(impl): self.aggregator = DSMILAggregator(
        #     in_dim=size[1], n_classes=n_classes)
        self.aggregator = None  # TODO

        # --- bloque CONSERVADO de CLAM: bag classifier por clase ------------
        # TODO(impl): self.classifiers = nn.ModuleList(
        #     [nn.Linear(size[1], 1) for _ in range(n_classes)])
        #   (espejo de model_clam.py:198-199)
        self.classifiers = None  # TODO

        # --- bloque CONSERVADO de CLAM: instance classifiers ----------------
        # TODO(impl): self.instance_classifiers = nn.ModuleList(
        #     [nn.Linear(size[1], 2) for _ in range(n_classes)])
        #   (espejo de model_clam.py:200-201)
        self.instance_classifiers = None  # TODO

        # NOTA(impl): inst_eval / inst_eval_out (model_clam.py:107 / :128) se
        # reutilizan tal cual. Opciones: (a) subclasear CLAM_MB e importar
        # esos métodos, (b) componer una instancia de CLAM_MB. El import de
        # `CLAM_MB` va DENTRO de __init__ (no en el top-level del módulo),
        # con sys.path.insert(0, ".../clam_environ"). Decidir en la impl.

    def forward(self, h, label=None, instance_eval=False,
                return_features=False, attention_only=False):
        """Firma idéntica a `CLAM_MB.forward` (model_clam.py:207).

        Esquema de la implementación efectiva:
            h          = self.fc(h)                  # [N, 512]  (CONSERVADO)
            A, M, c    = self.aggregator(h)           # DSMIL  (REEMPLAZO)
            if attention_only: return A
            if instance_eval:                        # rama instance CONSERVADA
                ... inst_eval/inst_eval_out sobre A y c, SmoothTop1SVM ...
            logits[0,k] = self.classifiers[k](M[k])  # bag classifier CONSERVADO
            Y_hat      = topk(logits, 1)[1]
            Y_prob     = softmax(logits, dim=1)
            return logits, Y_prob, Y_hat, A_raw, results_dict
        """
        # TODO(impl): ensamblar fc -> aggregator -> classifiers + rama instance.
        raise NotImplementedError(
            "DSMIL_CLAM_MB.forward es un skeleton. Implementar tras confirmar "
            "el módulo en la reunión y validar contra DSMIL_official_reference."
        )


if __name__ == "__main__":
    # Humo mínimo: construir los skeletons no debe fallar; forward sí debe
    # levantar NotImplementedError. No usa GPU.
    agg = DSMILAggregator(in_dim=512, n_classes=2)
    model = DSMIL_CLAM_MB(embed_dim=512, n_classes=2)
    print("[ok] skeletons construidos:", type(agg).__name__,
          "+", type(model).__name__)
    try:
        model.forward(torch.zeros(10, 512))
    except NotImplementedError as e:
        print("[ok] forward levanta NotImplementedError (esperado):", e)
