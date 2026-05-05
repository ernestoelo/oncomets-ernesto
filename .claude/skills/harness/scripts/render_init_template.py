#!/usr/bin/env python3
"""
render_init_template.py — Render runtime-specific values for harness templates.

Returns a dict of substitutions used by scaffold_harness.py:
  RUNTIME, SRC_DIR, TESTS_DIR, EXT, RUN_CMD, TEST_CMD, FORMATTER, LINTER,
  NAMING_RULE, QUOTE_STYLE, TEMP_FIXTURE, TMP_PATTERNS, RUNTIME_CHECKS,
  POST_EDIT_CMD, PERMISSIONS_ALLOW, LAYER_1, LAYER_2, LAYER_3.

Usage:
    python3 render_init_template.py <runtime>
    runtime ∈ {python, node, rust, go, none}
"""
from __future__ import annotations

import json
import sys

RUNTIMES = {
    "python": {
        "RUNTIME": "python",
        "SRC_DIR": "src/",
        "TESTS_DIR": "tests/",
        "EXT": "py",
        "RUN_CMD": "python3 -m src",
        "TEST_CMD": "python3 -m unittest discover -s tests -v",
        "FORMATTER": "black",
        "LINTER": "ruff",
        "NAMING_RULE": "snake_case",
        "QUOTE_STYLE": "dobles",
        "TEMP_FIXTURE": "tempfile.TemporaryDirectory()",
        "TMP_PATTERNS": "*.tmp, __pycache__, .pytest_cache",
        "RUNTIME_CHECKS": (
            'command -v python3 >/dev/null || fail "python3 no encontrado"\n'
            'ok "python3 $(python3 --version | cut -d\' \' -f2)"\n\n'
            "# 4. Tests\n"
            'python3 -m unittest discover -s tests -q || fail "tests fallaron"\n'
            'ok "tests verdes"'
        ),
        "POST_EDIT_CMD": "python3 -m unittest discover -s tests -q 2>&1 | tail -3",
        "PERMISSIONS_ALLOW": json.dumps(
            ["Bash(./init.sh)", "Bash(python3 -m unittest*)", "Bash(python3 -m src*)"]
        ),
        "LAYER_1": "Storage",
        "LAYER_2": "Domain",
        "LAYER_3": "CLI",
    },
    "node": {
        "RUNTIME": "node",
        "SRC_DIR": "src/",
        "TESTS_DIR": "tests/",
        "EXT": "ts",
        "RUN_CMD": "npm start",
        "TEST_CMD": "npm test",
        "FORMATTER": "prettier",
        "LINTER": "eslint",
        "NAMING_RULE": "camelCase",
        "QUOTE_STYLE": "simples",
        "TEMP_FIXTURE": "fs.mkdtempSync(...)",
        "TMP_PATTERNS": "*.tmp, node_modules, .next, dist",
        "RUNTIME_CHECKS": (
            'command -v node >/dev/null || fail "node no encontrado"\n'
            'ok "node $(node --version)"\n\n'
            "# 4. Tests\n"
            'npm test --silent || fail "tests fallaron"\n'
            'ok "tests verdes"'
        ),
        "POST_EDIT_CMD": "npm test --silent 2>&1 | tail -5",
        "PERMISSIONS_ALLOW": json.dumps(
            ["Bash(./init.sh)", "Bash(npm test*)", "Bash(npm start*)", "Bash(npm run*)"]
        ),
        "LAYER_1": "Storage",
        "LAYER_2": "Domain",
        "LAYER_3": "API",
    },
    "rust": {
        "RUNTIME": "rust",
        "SRC_DIR": "src/",
        "TESTS_DIR": "tests/",
        "EXT": "rs",
        "RUN_CMD": "cargo run --",
        "TEST_CMD": "cargo test",
        "FORMATTER": "rustfmt",
        "LINTER": "clippy",
        "NAMING_RULE": "snake_case",
        "QUOTE_STYLE": "dobles",
        "TEMP_FIXTURE": "tempfile::TempDir::new()",
        "TMP_PATTERNS": "target/, *.tmp",
        "RUNTIME_CHECKS": (
            'command -v cargo >/dev/null || fail "cargo no encontrado"\n'
            'ok "$(cargo --version)"\n\n'
            "# 4. Tests\n"
            'cargo test --quiet || fail "tests fallaron"\n'
            'ok "tests verdes"'
        ),
        "POST_EDIT_CMD": "cargo test --quiet 2>&1 | tail -5",
        "PERMISSIONS_ALLOW": json.dumps(
            ["Bash(./init.sh)", "Bash(cargo test*)", "Bash(cargo run*)", "Bash(cargo build*)"]
        ),
        "LAYER_1": "Storage",
        "LAYER_2": "Domain",
        "LAYER_3": "CLI",
    },
    "go": {
        "RUNTIME": "go",
        "SRC_DIR": "internal/",
        "TESTS_DIR": "internal/",
        "EXT": "go",
        "RUN_CMD": "go run ./cmd/...",
        "TEST_CMD": "go test ./...",
        "FORMATTER": "gofmt",
        "LINTER": "golangci-lint",
        "NAMING_RULE": "PascalCase (exportado) / camelCase (privado)",
        "QUOTE_STYLE": "dobles",
        "TEMP_FIXTURE": "t.TempDir()",
        "TMP_PATTERNS": "*.tmp, vendor/",
        "RUNTIME_CHECKS": (
            'command -v go >/dev/null || fail "go no encontrado"\n'
            'ok "$(go version)"\n\n'
            "# 4. Tests\n"
            'go test ./... || fail "tests fallaron"\n'
            'ok "tests verdes"'
        ),
        "POST_EDIT_CMD": "go test ./... 2>&1 | tail -5",
        "PERMISSIONS_ALLOW": json.dumps(
            ["Bash(./init.sh)", "Bash(go test*)", "Bash(go run*)", "Bash(go build*)"]
        ),
        "LAYER_1": "Storage",
        "LAYER_2": "Domain",
        "LAYER_3": "CLI",
    },
    "none": {
        "RUNTIME": "none",
        "SRC_DIR": "src/",
        "TESTS_DIR": "tests/",
        "EXT": "",
        "RUN_CMD": "(definir según proyecto)",
        "TEST_CMD": "(definir según proyecto)",
        "FORMATTER": "(según proyecto)",
        "LINTER": "(según proyecto)",
        "NAMING_RULE": "(según proyecto)",
        "QUOTE_STYLE": "(según proyecto)",
        "TEMP_FIXTURE": "(según proyecto)",
        "TMP_PATTERNS": "*.tmp",
        "RUNTIME_CHECKS": '# Sin runtime — solo se valida estructura.\nok "estructura OK (sin runner)"',
        "POST_EDIT_CMD": "echo '[harness] runtime=none, sin tests automáticos'",
        "PERMISSIONS_ALLOW": json.dumps(["Bash(./init.sh)"]),
        "LAYER_1": "Storage",
        "LAYER_2": "Domain",
        "LAYER_3": "Interface",
    },
}


def render(runtime: str) -> dict:
    if runtime not in RUNTIMES:
        raise ValueError(f"runtime '{runtime}' no soportado. Opciones: {list(RUNTIMES)}")
    return RUNTIMES[runtime].copy()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    print(json.dumps(render(sys.argv[1]), indent=2, ensure_ascii=False))
