"""models_pathpt/losses.py — las 3 pérdidas de PathPT (curriculum de confianza).

Port FIEL de `PathPT_reference/loss.py` (pin 0ab7f1b): `PatchSSLoss` + `balanced_ce_loss`.

Convención de labels por parche (la genera el pseudo-etiquetado zero-shot, §3.3):
  - label >= 0  : parche con pseudo-label CONFIABLE (clase conocida) → CE balanceada.
  - label  < 0  : parche CANDIDATO, codificado como -k → "es clase 0 (normal) o clase k
                  (el subtipo de la slide)". Pérdida de etiqueta parcial -log(p0+pk) (ec.7).

Las 3 componentes (pesos [1.0, 0.5, 0.1] = labeled, pseudo, candidate):
  - labeled_loss   : CE (balanceada) sobre parches con pseudo-label confiable. peso 1.0
  - pseudo_loss    : self-training — desde época>=10, re-etiqueta candidatos cuyo argmax
                     cae en {0, k} y aplica CE. peso 0.5
  - candidate_loss : etiqueta parcial -log(p0+pk) sobre todos los candidatos. peso 0.1
"""
import copy

import torch
import torch.nn as nn
import torch.nn.functional as F


def balanced_ce_loss(logits, labels):
    """CE promediada POR CLASE (no por muestra) → robusta al desbalance de parches."""
    num_classes = logits.shape[-1]
    if labels.dim() > 1:
        logits = logits.view(-1, logits.size(-1))
        labels = labels.view(-1)
    individual = F.cross_entropy(logits, labels, reduction="none")
    per_class = torch.zeros(num_classes, device=logits.device)
    count = torch.zeros(num_classes, device=logits.device)
    for cls in range(num_classes):
        mask = labels == cls
        if mask.any():
            per_class[cls] = individual[mask].mean()
            count[cls] = 1
    return per_class[count > 0].mean()


def PatchSSLoss(logits, labels, epoch, total_epoch=20, weights=(1.0, 0.5, 0.1),
                balance=True, vision_only=False, pseudo_loss=True):
    """Pérdida semi-supervisada por parche. Port verbatim de la referencia.

    logits: [N, C] (patch_logits, ya softmax en el modelo o logits crudos — acá se
            re-softmaxea para los candidatos; ver nota).
    labels: [N] con la convención >=0 conocido / <0 candidato (-k).
    Devuelve dict con 'loss' + componentes + 'valid_pseudo_ratio' (+ 'return_labels').
    """
    losses = {
        "labeled_loss": torch.tensor(0.0, device=logits.device),
        "pseudo_loss": torch.tensor(0.0, device=logits.device),
        "candidate_loss": torch.tensor(0.0, device=logits.device),
        "valid_pseudo_ratio": 0.0,
    }
    logits = logits.view(-1, logits.size(-1))
    labels = labels.view(-1)

    # 1) parches con pseudo-label confiable (label >= 0)
    known = labels >= 0
    if known.any():
        if balance:
            losses["labeled_loss"] = balanced_ce_loss(logits[known], labels[known].long())
        else:
            losses["labeled_loss"] = F.cross_entropy(logits[known], labels[known].long())

    # 2) parches candidatos (label < 0, codifican -k)
    if not vision_only:
        cand = ~known
        if cand.any():
            k = (-labels[cand]).long()
            probs = F.softmax(logits[cand], dim=1)
            p0 = probs[:, 0]
            pk = probs[torch.arange(len(k)), k]
            # etiqueta parcial (ec.7): siempre activa
            losses["candidate_loss"] = -torch.log(p0 + pk + 1e-8).mean()

            # self-training (epoch>=10): re-etiqueta candidatos con argmax en {0,k}
            if epoch >= 10 and pseudo_loss:
                max_idx = torch.argmax(probs, dim=1)
                conf = (max_idx == 0) | (max_idx == k)
                valid = int(conf.sum().item())
                losses["valid_pseudo_ratio"] = valid / len(conf)
                if valid > 0:
                    pseudo_labels = max_idx[conf].detach()
                    if balance:
                        losses["pseudo_loss"] = balanced_ce_loss(
                            logits[cand][conf], pseudo_labels.long())
                    else:
                        losses["pseudo_loss"] = F.cross_entropy(
                            logits[cand][conf], pseudo_labels.long())
                    return_labels = copy.deepcopy(labels)
                    cand_idx = torch.nonzero(cand).flatten()
                    return_labels[cand_idx[conf]] = pseudo_labels
                    losses["return_labels"] = return_labels

    losses["loss"] = (
        weights[0] * losses["labeled_loss"]
        + weights[1] * losses["pseudo_loss"]
        + weights[2] * losses["candidate_loss"]
    )
    return losses
