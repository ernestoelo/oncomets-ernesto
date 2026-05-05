#!/usr/bin/env python3
"""
scaffold_harness.py — Genera el harness multi-agente en el proyecto actual.

Uso:
    python3 scaffold_harness.py [--runtime RUNTIME] [--features F1,F2,...] [--retrofit]

Argumentos:
    --runtime    {python, node, rust, go, none}. Si se omite, se autodetecta.
    --features   Nombres separados por coma para sembrar feature_list.json.
                 Si se omite, queda 1 feature placeholder.
    --retrofit   No sobreescribir nada. Lista qué crearía y pide confirmación
                 archivo a archivo.

Lee templates de ../assets/templates/ y los renderiza en el cwd.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
TEMPLATES_DIR = SKILL_DIR / "assets" / "templates"

sys.path.insert(0, str(SCRIPT_DIR))
from render_init_template import render  # noqa: E402


def detect_runtime(cwd: Path) -> str:
    if (cwd / "pyproject.toml").exists() or (cwd / "requirements.txt").exists():
        return "python"
    if (cwd / "package.json").exists():
        return "node"
    if (cwd / "Cargo.toml").exists():
        return "rust"
    if (cwd / "go.mod").exists():
        return "go"
    return "none"


def substitute(text: str, vars: dict) -> str:
    out = text
    for k, v in vars.items():
        out = out.replace("{{" + k + "}}", str(v))
    return out


def render_feature_list(template: str, project_name: str, features: list[str], vars: dict) -> str:
    rendered = substitute(template, {**vars, "PROJECT_NAME": project_name, "FEATURE_1_NAME": features[0]})
    data = json.loads(rendered)
    base_acceptance = data["features"][0]["acceptance"]
    data["features"] = [
        {
            "id": i + 1,
            "name": name,
            "status": "pending",
            "acceptance": [a for a in base_acceptance],
            "depends_on": [],
        }
        for i, name in enumerate(features)
    ]
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def confirm(path: Path, retrofit: bool) -> bool:
    if not path.exists():
        return True
    if not retrofit:
        print(f"[skip] existe: {path.relative_to(Path.cwd())} (usa --retrofit para confirmar)")
        return False
    ans = input(f"[retrofit] sobreescribir {path.relative_to(Path.cwd())}? [y/N] ").strip().lower()
    return ans == "y"


def write_template(rel_template: str, rel_target: str, vars: dict, retrofit: bool, raw: str | None = None):
    src = TEMPLATES_DIR / rel_template
    dst = Path.cwd() / rel_target
    dst.parent.mkdir(parents=True, exist_ok=True)
    if not confirm(dst, retrofit):
        return False
    content = raw if raw is not None else substitute(src.read_text(), vars)
    dst.write_text(content)
    print(f"[create] {rel_target}")
    return True


def main():
    p = argparse.ArgumentParser(description="Scaffold harness multi-agente.")
    p.add_argument("--runtime", choices=["python", "node", "rust", "go", "none"])
    p.add_argument("--features", default="feature_one")
    p.add_argument("--retrofit", action="store_true")
    p.add_argument("--project-name", default=None)
    args = p.parse_args()

    cwd = Path.cwd()
    runtime = args.runtime or detect_runtime(cwd)
    print(f"[info] runtime: {runtime}")

    vars = render(runtime)
    project_name = args.project_name or cwd.name
    features = [f.strip() for f in args.features.split(",") if f.strip()]

    write_template("AGENTS.md.tmpl", "AGENTS.md", vars, args.retrofit)
    write_template("CHECKPOINTS.md.tmpl", "CHECKPOINTS.md", vars, args.retrofit)
    write_template("CLAUDE.md.tmpl", "CLAUDE.md", vars, args.retrofit)
    write_template("docs/architecture.md.tmpl", "docs/architecture.md", vars, args.retrofit)
    write_template("docs/conventions.md.tmpl", "docs/conventions.md", vars, args.retrofit)
    write_template("docs/verification.md.tmpl", "docs/verification.md", vars, args.retrofit)
    write_template("progress/current.md.tmpl", "progress/current.md", vars, args.retrofit)
    write_template("progress/history.md.tmpl", "progress/history.md", vars, args.retrofit)
    write_template(".claude/agents/leader.md.tmpl", ".claude/agents/leader.md", vars, args.retrofit)
    write_template(".claude/agents/implementer.md.tmpl", ".claude/agents/implementer.md", vars, args.retrofit)
    write_template(".claude/agents/reviewer.md.tmpl", ".claude/agents/reviewer.md", vars, args.retrofit)
    write_template(".claude/settings.json.tmpl", ".claude/settings.json", vars, args.retrofit)

    init_template = (TEMPLATES_DIR / "init.sh.tmpl").read_text()
    init_rendered = substitute(init_template, vars)
    init_path = cwd / "init.sh"
    if confirm(init_path, args.retrofit):
        init_path.write_text(init_rendered)
        os.chmod(init_path, 0o755)
        print("[create] init.sh (chmod +x)")

    fl_template = (TEMPLATES_DIR / "feature_list.json.tmpl").read_text()
    fl_rendered = render_feature_list(fl_template, project_name, features, vars)
    write_template("feature_list.json.tmpl", "feature_list.json", vars, args.retrofit, raw=fl_rendered)

    print("\n[done] harness scaffolded. Próximos pasos:")
    print("  1. Revisa docs/architecture.md y conventions.md (personaliza al proyecto).")
    print("  2. Edita feature_list.json con acceptance criteria reales.")
    print("  3. ./init.sh (debe terminar con exit 0).")
    print("  4. bash ~/.claude/skills/harness/scripts/validate_harness.sh .")


if __name__ == "__main__":
    main()
