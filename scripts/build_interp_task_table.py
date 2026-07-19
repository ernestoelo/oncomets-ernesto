"""build_interp_task_table.py — tabla por tarea para el Sprint 7 (requisito de Sebastian).

Por tarea: slides usadas (IDs) · magnificacion FISICA um/px · dataset/cohorte/n ·
etiqueta del patologo. La magnificacion se LEE de cada WSI con openslide (regla 5:
validar contra el dato real), NO se asume del `level` ni del nombre de cohorte
([[cohortes-magnificacion-fisica]]: el tag Aperio miente; TCGA ~0.2325 um/px = 40x,
privado ~0.465 = 20x, HistAI generic-tiff sin MPP confiable).

Etapa 0: CPU, solo lectura.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

REPO = Path("/media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto")
# Los CSVs de las 3 tareas son NUESTROS (generados para la reformulacion _ci_reform),
# viven en el repo — no en clam_environ. Coincide con $CSV_NT del slurm del job 4589.
CSV_NT = REPO / "data/csv_new_tasks"

TASK_CSV = {
    "tipo_histologico_3clases_ci": "dataset_tipo_histologico_3clases_ci_label.csv",
    "carcinoma_ductal_insitu_presente_ci_reform":
        "dataset_carcinoma_ductal_insitu_presente_ci_reform_label.csv",
    "invasion_linfatica_vascular_ci_reform":
        "dataset_invasion_linfatica_vascular_ci_reform_label.csv",
}
TASK_PRETTY = {
    "tipo_histologico_3clases_ci": "Tipo histologico (3 clases)",
    "carcinoma_ductal_insitu_presente_ci_reform": "Carcinoma ductal in situ presente",
    "invasion_linfatica_vascular_ci_reform": "Invasion linfovascular",
}


def cohort_of(sid):
    if sid.startswith("TCGA"):
        return "TCGA"
    if sid.startswith("histai"):
        return "HistAI"
    return "privado (Environ)"


def read_label_csv(path):
    """slide_id -> label. Gotcha [[data-gotchas-csv-wsi-interp]]: CRLF de Windows."""
    if not path.exists():
        return {}
    out = {}
    with open(path, newline="", encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            sid = (row.get("slide_id") or "").strip().strip("\r")
            lab = (row.get("label") or "").strip().strip("\r")
            if sid:
                out[sid] = lab
    return out


def read_mpp(wsi_path):
    """um/px a nivel 0 leidos del archivo. Devuelve (mpp_x, mag_declarada, fuente)."""
    try:
        import openslide
    except ImportError:
        return None, None, "openslide no disponible"
    try:
        sl = openslide.OpenSlide(str(wsi_path))
    except Exception as exc:  # pragma: no cover
        return None, None, f"error abriendo: {exc}"
    props = sl.properties
    mpp = None
    fuente = "ausente"
    for key in ("openslide.mpp-x", "aperio.MPP", "tiff.XResolution"):
        val = props.get(key)
        if not val:
            continue
        try:
            f = float(val)
        except (TypeError, ValueError):
            continue
        if key == "tiff.XResolution":
            unit = (props.get("tiff.ResolutionUnit") or "").lower()
            if f > 0 and unit in ("centimeter", "cm"):
                mpp = 10000.0 / f
                fuente = "tiff.XResolution (derivado)"
                break
            continue
        if f > 0:
            mpp = f
            fuente = key
            break
    mag = props.get("openslide.objective-power") or props.get("aperio.AppMag")
    dims = sl.dimensions
    sl.close()
    return mpp, (float(mag) if mag else None), fuente, dims


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selection", default=str(REPO / "sprints/B7_sprint7/interp_slides.json"))
    ap.add_argument("--out", default=str(REPO / "sprints/B7_sprint7/tabla_por_tarea.md"))
    args = ap.parse_args()

    sel = json.loads(Path(args.selection).read_text())
    lines = ["# Tabla por tarea — interpretabilidad CLAM vs Mammoth (Sprint 7)", "",
             "Magnificacion **fisica** leida con openslide de cada WSI (no del `level`",
             "ni del nombre de la cohorte). Entrenamiento pareado, job 4589.", ""]
    payload = {}

    for task, cfg in sel.items():
        labels = read_label_csv(CSV_NT / TASK_CSV[task])
        dist = Counter(labels.values())
        coh = Counter(cohort_of(s) for s in labels)
        pretty = TASK_PRETTY[task]
        print(f"\n### {pretty}")
        print(f"  dataset: n={len(labels)}  dist={dict(dist)}  cohortes={dict(coh)}")

        lines += [f"## {pretty}", "",
                  f"- **Tarea (task)**: `{task}`",
                  f"- **Dataset**: n = {len(labels)} WSI · "
                  + " · ".join(f"{k}: {v}" for k, v in sorted(dist.items())),
                  f"- **Cohortes**: " + " · ".join(f"{k}: {v}" for k, v in sorted(coh.items())),
                  f"- **Fold usado para interpretabilidad**: {cfg['fold']} (5-fold pareado)",
                  "",
                  "| Slide (ID) | Cohorte | Etiqueta del patologo | um/px (nivel 0) | Magnif. equiv. | Fuente del MPP | Dimensiones nivel 0 |",
                  "|---|---|---|---|---|---|---|"]

        rows = []
        for sl in cfg["slides"]:
            sid = sl["slide_id"]
            mpp, mag, fuente, dims = read_mpp(sl["wsi"])
            equiv = f"~{10.0 / mpp:.0f}x" if mpp else "no determinable"
            mpp_s = f"{mpp:.4f}" if mpp else "**no disponible**"
            lab = labels.get(sid, sl["label"])
            short = sid.split(".")[0]
            lines.append(
                f"| `{short}` | {sl['cohort']} | {lab} | {mpp_s} | {equiv} | "
                f"{fuente} | {dims[0]}x{dims[1]} |")
            print(f"    {short:<42} {sl['cohort']:<8} {lab:<38} "
                  f"mpp={mpp_s} ({equiv})  [{fuente}]")
            rows.append(dict(slide_id=sid, cohort=sl["cohort"], etiqueta=lab,
                             mpp_x=mpp, magnif_equiv=equiv, fuente_mpp=fuente,
                             dims_level0=list(dims)))
        lines.append("")
        payload[task] = dict(pretty=pretty, n=len(labels), dist=dict(dist),
                             cohortes=dict(coh), fold=cfg["fold"], slides=rows)

    Path(args.out).write_text("\n".join(lines))
    Path(args.out).with_suffix(".json").write_text(json.dumps(payload, indent=2))
    print(f"\nTabla escrita en: {args.out}")


if __name__ == "__main__":
    main()
