#!/usr/bin/env python3
"""
Skill Scaffold - Generates the standard directory structure for a new skill.

Usage:
    python skill_scaffold.py <skill-name> [description]

Example:
    python skill_scaffold.py my-skill "Handles PDF form filling and validation"
"""

import os
import sys

TEMPLATE_SKILL_MD = '''---
name: {name}
description: This skill should be used when the user asks to [TODO: add trigger phrases]. Provides [TODO: what it does].
---

# {title}

[TODO: One-line summary of what this skill does.]

## When This Skill Applies

- [TODO: List activation conditions]

## Usage

[TODO: Core workflow and instructions]

## References

- Add references/ files for detailed documentation
- Add scripts/ for deterministic operations
- Add assets/ for output templates and resources
'''


def scaffold_skill(skill_name, description="[TODO: add description]"):
    title = skill_name.replace("-", " ").title()
    base = os.path.abspath(skill_name)

    os.makedirs(os.path.join(base, "scripts"), exist_ok=True)
    os.makedirs(os.path.join(base, "references"), exist_ok=True)
    os.makedirs(os.path.join(base, "assets"), exist_ok=True)

    skill_md_path = os.path.join(base, "SKILL.md")
    if not os.path.exists(skill_md_path):
        content = TEMPLATE_SKILL_MD.format(name=skill_name, title=title)
        if description != "[TODO: add description]":
            content = content.replace(
                "This skill should be used when the user asks to [TODO: add trigger phrases]. Provides [TODO: what it does].",
                description,
            )
        with open(skill_md_path, "w") as f:
            f.write(content)

    print(f"Skill '{skill_name}' scaffolded at {base}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python skill_scaffold.py <skill-name> [description]")
        sys.exit(1)
    name = sys.argv[1]
    desc = sys.argv[2] if len(sys.argv) > 2 else "[TODO: add description]"
    scaffold_skill(name, desc)
