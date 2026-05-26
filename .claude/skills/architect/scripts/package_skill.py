#!/usr/bin/env python3
"""
Skill Packager - Creates a distributable .skill file (zip) from a skill folder.

Usage:
    python package_skill.py <path/to/skill-folder> [output-directory]

Example:
    python package_skill.py ../../my-skill
    python package_skill.py ../../my-skill ./dist
"""

import sys
import zipfile
from pathlib import Path
from quick_validate import validate_skill


def package_skill(skill_path, output_dir=None):
    skill_path = Path(skill_path).resolve()
    if not skill_path.is_dir():
        print(f"Error: '{skill_path}' is not a directory")
        return False

    is_valid, message = validate_skill(skill_path)
    if not is_valid:
        print(f"Validation failed: {message}")
        return False

    skill_name = skill_path.name
    output_dir = Path(output_dir).resolve() if output_dir else skill_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{skill_name}.skill"

    with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in skill_path.rglob("*"):
            if file.is_file() and ".git" not in file.parts:
                arcname = file.relative_to(skill_path.parent)
                zf.write(file, arcname)

    print(f"Packaged '{skill_name}' -> {output_file}")
    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python package_skill.py <path/to/skill-folder> [output-directory]")
        sys.exit(1)
    skill = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else None
    success = package_skill(skill, out)
    sys.exit(0 if success else 1)
