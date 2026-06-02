import torch
import random


class PCGrad:
    def __init__(self, optimizer):
        self.optimizer = optimizer

    def zero_grad(self):
        self.optimizer.zero_grad()

    def step(self):
        self.optimizer.step()

    def pc_backward(self, losses, model):
        params = [p for p in model.parameters() if p.requires_grad]
        shapes = [p.shape for p in params]

        grads = []

        for loss in losses:
            grad = torch.autograd.grad(
                loss,
                params,
                retain_graph=True,
                allow_unused=True
            )

            flat_grad = []
            for g, p in zip(grad, params):
                if g is None:
                    flat_grad.append(torch.zeros_like(p).reshape(-1))
                else:
                    flat_grad.append(g.contiguous().reshape(-1))

            grads.append(torch.cat(flat_grad))
        # después de llenar la lista grads
        if len(grads) == 2:
            g_bag = grads[0]
            g_inst = grads[1]

            cos_sim = torch.dot(g_bag, g_inst) / (
                torch.norm(g_bag) * torch.norm(g_inst) + 1e-12
            )

            print(f"[PCGrad] cos(g_bag, g_inst): {cos_sim.item():.4f}")

        pc_grads = []

        for i, g_i in enumerate(grads):
            g_proj = g_i.clone()
            order = list(range(len(grads)))
            random.shuffle(order)

            for j in order:
                if i == j:
                    continue

                g_j = grads[j]
                dot = torch.dot(g_proj, g_j)

                if dot < 0:
                    g_proj = g_proj - dot / (torch.dot(g_j, g_j) + 1e-12) * g_j

            pc_grads.append(g_proj)

        final_grad = torch.stack(pc_grads, dim=0).mean(dim=0)

        pointer = 0
        for p, shape in zip(params, shapes):
            numel = p.numel()
            p.grad = final_grad[pointer:pointer + numel].view(shape).clone()
            pointer += numel