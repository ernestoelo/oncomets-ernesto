#!/bin/bash
# Quick validation for AI/ML project structure
# Usage: ./validate_project.sh [project_root]

ROOT=${1:-.}

check() {
  if [ ! -d "$ROOT/src" ]; then echo "Missing src/ directory"; fi
  if [ ! -f "$ROOT/pyproject.toml" ]; then echo "Missing pyproject.toml"; fi
  if [ ! -f "$ROOT/uv.lock" ]; then echo "Missing uv.lock"; fi
  if [ ! -f "$ROOT/README.md" ]; then echo "Missing README.md"; fi
  if [ ! -d "$ROOT/models" ]; then echo "Missing models/ directory"; fi
  if [ ! -d "$ROOT/data" ]; then echo "Missing data/ directory"; fi
}

check
