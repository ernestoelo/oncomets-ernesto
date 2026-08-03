"""Preflight CPU del grid E×S (B8 objetivo 3): construye TODAS las configuraciones
del grid antes de gastar GPU y reporta su presupuesto de parámetros.

Por qué existe (workaround G, a nivel de configuración): el grid son 40 runs ≈ 24 h.
Una config que no construye — o que cambia el presupuesto de parámetros sin que lo
hayamos notado — se paga en horas de GPU si se descubre a mitad de camino. Acá se
descubre en segundos.

Lo que verifica por configuración:
  1. `CLAM_MB_Mammoth` construye con ese (E, S).
  2. Forward CPU sobre un bag random [200, 512] → logits finitos y A con forma
     (n_classes, N) (keep_slots=False preserva los N parches).
  3. Conteo de parámetros, desglosado en `slot_embeds` (∝ E·S) y `expert_heads`
     (gobernado por el `lora_rank` que `auto_rank` deriva de E, NO de S).

El punto 3 es el que importa para leer el grid: `auto_rank` calcula el rank desde
`(input_dim, slot_dim, output_dim, num_experts)` — depende de **E y no de S**
(MAMMOTH/src/mammoth/mammoth.py:297-322), así que recortar E sube el rank y
compensa parámetros, mientras que recortar S solo achica `slot_embeds`. Los pares
a igual E·S no son automáticamente iso-parámetro: esta tabla dice cuánto difieren.

Ejecutable directo (NUNCA `python` a secas — workaround B):
    /home/sdonoso/miniconda3/envs/clam_latest/bin/python scripts/grid_es_config_check.py
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import torch  # noqa: E402

from models_mammoth import CLAM_MB_Mammoth  # noqa: E402

# Grid pre-registrado (sprints/B8_sprint8/grid_expertos_slots/prereg.md §4).
# (etiqueta, E, S). El control 30×10 va primero.
GRID = [
    ("C  control", 30, 10),
    ("A1 recorta E", 27, 10),
    ("B1 recorta S", 30, 9),
    ("A2 recorta E", 21, 10),
    ("B2 recorta S", 30, 7),
    ("A3 recorta E", 15, 10),
    ("B3 recorta S", 30, 5),
    ("B4 piso S", 30, 3),
]

N_PATCHES = 200
EMBED_DIM = 512
N_CLASSES = 2


def build_and_probe(num_experts: int, num_slots: int) -> dict:
    """Construye la config, corre un forward CPU y devuelve el desglose de parámetros."""
    torch.manual_seed(1)
    model = CLAM_MB_Mammoth(
        n_classes=N_CLASSES,
        embed_dim=EMBED_DIM,
        dropout=0.25,
        k_sample=8,
        mammoth_num_experts=num_experts,
        mammoth_num_slots=num_slots,
        mammoth_num_heads=16,
        mammoth_slot_dim=256,
    )
    model.eval()

    embed = model.attention_net[0]
    mam = embed.mammoth
    slot_embeds = mam.slot_embeds.numel()
    expert_heads = sum(p.numel() for p in mam.expert_heads.parameters())
    mammoth_total = sum(p.numel() for p in mam.parameters())
    model_total = sum(p.numel() for p in model.parameters())

    x = torch.randn(N_PATCHES, EMBED_DIM)
    with torch.no_grad():
        logits, Y_prob, Y_hat, A_raw, _ = model(x)

    assert torch.isfinite(logits).all(), "logits con NaN/inf"
    assert A_raw.shape == (N_CLASSES, N_PATCHES), (
        f"A_raw {tuple(A_raw.shape)}, esperaba ({N_CLASSES}, {N_PATCHES}) "
        "— keep_slots=False debe preservar los N parches"
    )
    assert torch.isfinite(Y_prob).all() and abs(Y_prob.sum().item() - 1.0) < 1e-4

    return dict(
        lora_rank=mam.lora_rank,
        slot_embeds=slot_embeds,
        expert_heads=expert_heads,
        mammoth_total=mammoth_total,
        model_total=model_total,
    )


def main() -> int:
    print(f"Preflight del grid E×S — {len(GRID)} configuraciones, "
          f"bag random [{N_PATCHES}, {EMBED_DIM}], n_classes={N_CLASSES}\n")

    rows = []
    for label, e, s in GRID:
        r = build_and_probe(e, s)
        rows.append((label, e, s, r))

    hdr = (f"{'brazo':<14}{'E':>4}{'S':>4}{'E·S':>6}{'rank':>6}"
           f"{'slot_embeds':>13}{'expert_heads':>14}{'mammoth':>10}{'modelo':>10}")
    print(hdr)
    print("-" * len(hdr))
    for label, e, s, r in rows:
        print(f"{label:<14}{e:>4}{s:>4}{e * s:>6}{r['lora_rank']:>6}"
              f"{r['slot_embeds']:>13,}{r['expert_heads']:>14,}"
              f"{r['mammoth_total']:>10,}{r['model_total']:>10,}")

    # Pares a igual E·S: cuánto se apartan en parámetros (lo que auto_rank compensa).
    print("\nPares a igual E·S (A recorta E, B recorta S):")
    by_total = {}
    for label, e, s, r in rows:
        by_total.setdefault(e * s, []).append((label, e, s, r))
    for total, group in sorted(by_total.items(), reverse=True):
        if len(group) != 2:
            continue
        (la, ea, sa, ra), (lb, eb, sb, rb) = group
        d = rb["model_total"] - ra["model_total"]
        rel = 100.0 * d / ra["model_total"]
        print(f"  E·S={total:>4}: {ea}×{sa} = {ra['model_total']:,} par. | "
              f"{eb}×{sb} = {rb['model_total']:,} par. | "
              f"delta {d:+,} ({rel:+.2f} %)")

    print("\n[OK] las 8 configuraciones construyen, hacen forward y preservan los N parches.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
