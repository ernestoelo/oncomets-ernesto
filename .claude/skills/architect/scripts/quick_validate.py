#!/usr/bin/env python3
"""
Quick validation script for skills - checks structure and frontmatter compliance
"""

import sys
import os
import re
import yaml
from pathlib import Path

PROHIBITED_FILES = {"README.md", "CHANGELOG.md", "INSTALLATION_GUIDE.md", "QUICK_REFERENCE.md"}
VALID_DIRS = {"scripts", "references", "assets"}
MAX_LINES = 500


def validate_skill(skill_path):
    """Basic validation of a skill"""
    skill_path = Path(skill_path)
    issues = []

    # Check SKILL.md exists
    skill_md = skill_path / 'SKILL.md'
    if not skill_md.exists():
        return False, "SKILL.md not found"

    # Read and validate frontmatter
    content = skill_md.read_text()
    if not content.startswith('---'):
        return False, "No YAML frontmatter found"

    # Extract frontmatter
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return False, "Invalid frontmatter format"

    frontmatter_text = match.group(1)

    # Parse YAML frontmatter
    try:
        frontmatter = yaml.safe_load(frontmatter_text)
        if not isinstance(frontmatter, dict):
            return False, "Frontmatter must be a YAML dictionary"
    except yaml.YAMLError as e:
        return False, f"Invalid YAML in frontmatter: {e}"

    # Check required fields
    if 'name' not in frontmatter:
        issues.append("Missing 'name' field in frontmatter")
    if 'description' not in frontmatter:
        issues.append("Missing 'description' field in frontmatter")

    # Warn about non-standard fields
    official_fields = {
        'name', 'description', 'disable-model-invocation', 'user-invocable',
        'allowed-tools', 'context', 'agent', 'model', 'effort', 'hooks',
        'paths', 'argument-hint', 'shell'
    }
    for key in frontmatter:
        if key not in official_fields:
            issues.append(f"Non-standard frontmatter field: '{key}'")

    # Check description length
    desc = frontmatter.get('description', '')
    if len(desc) > 250:
        issues.append(f"Description is {len(desc)} chars (truncated at 250 in skill listing)")

    # Check line count
    line_count = len(content.splitlines())
    if line_count > MAX_LINES:
        issues.append(f"SKILL.md is {line_count} lines (max {MAX_LINES})")

    # Check for prohibited files
    for item in skill_path.iterdir():
        if item.name in PROHIBITED_FILES:
            issues.append(f"Prohibited file found: {item.name}")

    # Check for duplicate frontmatter (common corruption)
    # Strip code blocks first to avoid false positives from examples
    body = content[match.end():]
    body_no_codeblocks = re.sub(r'```[\s\S]*?```', '', body)
    second_fm = re.search(r'\n---\s*\nname:\s', body_no_codeblocks)
    if second_fm:
        issues.append("Multiple frontmatter blocks detected — possible content duplication")

    if issues:
        return False, "; ".join(issues)

    return True, "Skill is valid"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python quick_validate.py <path/to/skill>")
        sys.exit(1)

    path = sys.argv[1]
    valid, message = validate_skill(path)
    print(f"{'PASS' if valid else 'FAIL'}: {message}")
    sys.exit(0 if valid else 1)
