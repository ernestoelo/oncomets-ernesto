# papers/

Papers descargados localmente para referencia rápida durante sprints.
Versionados en el repo para garantizar que la cita siempre apunta al PDF
exacto que se leyó (evitar drift de URL).

## Convenciones

- Nombre del archivo: `<primer_autor><año>.pdf` en kebab-case del apellido.
- Una entrada por paper en la tabla de abajo con cita BibTeX.
- No incluir papers cuyo PDF no sea distribuible (paywall sin
  acceso, preprints retirados, etc.). En esos casos dejar solo la cita.

## Inventario

| Archivo | Paper | Año | Sprint que lo introdujo |
|---|---|---|---|
| `dsmil_li2021.pdf` | Li, Li & Eliceiri — Dual-stream MIL for WSI | 2021 | B4 / Sprint 4 |
| `2001.06782v4.pdf` | Yu et al. — Gradient Surgery for Multi-Task Learning (PCGrad) | 2020 | B4 (recomendado por Eduardo, 21 may) |
| `2512.18734.pdf` | Chen & Xu — Breast Cancer Recurrence Risk Prediction Based on MIL | 2025 | B4 (recomendado por Eduardo, 21 may) |
| `electronics-13-04445.pdf` | Liu et al. — Dual-Attention MIL Framework for Pathology WSI | 2024 | B4 (recomendado por Eduardo, 21 may) |

> **Papers de Eduardo (21 may 2026)**: aportados para atacar el desbalance de
> clases de `microcalcificaciones_pth`. Nombres de archivo conservados como
> los subió Eduardo (no se renombraron a la convención `<autor><año>`). El
> análisis profundo de si alguna idea aplica al problema está pendiente de
> una sesión dedicada (ver `progress/current.md`).

## Citas

### DSMIL (Li et al., 2021)

```bibtex
@inproceedings{li2021dsmil,
  title     = {Dual-stream Multiple Instance Learning Network for Whole Slide
               Image Classification with Self-supervised Contrastive Learning},
  author    = {Li, Bin and Li, Yin and Eliceiri, Kevin W.},
  booktitle = {Proceedings of the IEEE/CVF Conference on Computer Vision and
               Pattern Recognition (CVPR)},
  year      = {2021},
  pages     = {14318--14328},
  archivePrefix = {arXiv},
  eprint    = {2011.08939},
  url       = {https://arxiv.org/abs/2011.08939}
}
```

Versión del PDF en este repo: arXiv v3 (2 abril 2021).
Repo oficial: <https://github.com/binli123/dsmil-wsi>.

## Papers de referencia que NO viven acá

Estos están bajo `~/EnvironBio/Papers/` (workspace del usuario, fuera del
repo) o en project files de claude.ai:

- **CLAM** (Lu et al., Nature BME 2021) — paper base del proyecto OncoMets.
- **CONCH** — extractor de features 512-dim (TCGA) / 1024-dim (Environ).
- **SlideChat**, **LongNet**, **CrossModal Projection**.

Si en algún sprint se necesita validar contra uno de estos, copiar el
PDF acá y agregarlo a la tabla.
