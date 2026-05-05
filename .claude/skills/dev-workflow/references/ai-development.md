# AI Project Development Guide

> **Spanish version available:** [02-ai-development.es.md](02-ai-development.es.md).
>
> The English version of this document is the canonical reference.
>
> Last updated: 2026-02-02.

Welcome to the team! This guide outlines our standard project structure and workflow. We use **`uv`** for dependency management to ensure our AI pipelines are fast, reproducible, and production-ready.

---

## Getting Started

### Initialize with the Library Template

To initialize a new project, use the following command (replace `my-awesome-package` with your actual project name):

```bash
uv init --lib my-awesome-package
cd my-awesome-package
```
This creates a src/ directory layout, which is the industry standard for Python packages to ensure your tests run against the installed code, not the local folder.

```sh
src
`-- my_awesome_package
    |-- __init__.py
    |-- __pycache__
    |   `-- __init__.cpython-312.pyc
    `-- py.typed
```
### Setup Environment
1. **Pin Python Version**: Create the .python-version file (replaces PYTHON_VERSION with our standard, e.g., 3.12):

```sh
uv python pin 3.12
```
2. **Add Dependencies**: It is not necessary to create a venv manually. `uv` handles the environment for you. We distinguish between libraries needed to run the code (Production) and tools needed for development (Linting, Testing).:
- Production Dependencies: These are essential for the code to run.
```sh
uv add requests
```
- Development Dependencies: These are only for local work (e.g., pytest, ipykernel). They won't be installed in the final production container if configured correctly.
```sh
uv add --dev pytest ipykernel
```

**Note**: `uv add` automatically creates the `.venv`, resolves the versions, and updates both your `pyproject.toml` and `uv.lock`.

3. **Activate Environment**:
```sh
source .venv/bin/activate
```

### Write and Run Code
Your source code lives in `src/my_awesome_package/__init__.py`. You can run scripts or tests instantly:
```sh
uv run python -c "import my_awesome_package; print('It works!')"
```

## Directory Structure
The complete structure of a project should be the following:
```sh
.
├── .venv/              # Local virtual environment (auto-managed by uv)
├── .python-version     # Pinned Python version
├── conf.env            # Environment variables and secrets (DO NOT COMMIT)
├── data/               # Local datasets
│   └── .gitkeep        # Ensures folder exists in Git
├── Dockerfile          # Instructions for containerizing the application
├── flows/              # Pipeline orchestration with Metaflow (if applicable)
├── main.py             # Primary entry point for execution
├── Makefile            # Shortcuts for common tasks (make install, make lint)
├── models/             # Local storage for weights and artifacts
│   └── .gitkeep        # Ensures folder exists in Git
├── notebooks/          # Jupyter notebooks for EDA and prototyping
├── pyproject.toml      # Project metadata and dependency list
├── README.md           # Project documentation
├── run.sh              # Shell script for automated execution
├── src/                # Core source code
│   └── my_awesome_package/
│       ├── __init__.py # Makes the directory a Python package
│       └── py.typed    # Enables type-checking support for the package
└── uv.lock             # Deterministic lockfile for dependencies
```
### The `.gitignore` File
Crucially, we track the folders but not the heavy files inside them.
```sh
# Python
__pycache__/
*.py[cod]
.venv/
.env
conf.env

# Project Specific - Keep the folders, ignore the contents
data/*
!data/.gitkeep
models/*
!models/.gitkeep

# Notebooks
notebooks/.ipynb_checkpoints/

# OS
.DS_Store
```
### The `run.sh` Script
This script handles the environment setup and executes the required scripts.
```sh
#!/bin/bash
set -e
# install core and development Python dependencies into the currently activated venv
function install {
    export UV_HTTP_TIMEOUT=600 # For large packages
    uv venv
    source .venv/bin/activate
    uv sync
}
function lint {
    pre-commit run --all-files
}
# print all functions in this file
function help {
    echo "$0 <task> <args>"
    echo "Tasks:"
    compgen -A function | cat -n
}
TIMEFORMAT="Task completed in %3lR"
time ${@:-help}
```
**Note**: Don't forget to use `uv sync --no-dev` in production to avoid installing development dependencies.

### The `Makefile`
This file must have at least the following commands:

```sh
install:
	bash run.sh install

lint:
	bash run.sh lint
```

## Component Details

1. Dependency Management
- pyproject.toml: The source of truth for your project. Add dependencies using uv add <package-name>.
- uv.lock: Always commit this file. It ensures that every team member (and the production server) uses the exact same versions of every library.
- .venv/: This folder contains the actual Python binaries. Never commit this to Git.

2. The src/ Package
- By putting the code in src/my_awesome_package/, we treat our project as a real library.
- py.typed: This empty file is essential. It tells type-checkers (like Mypy) that we have provided type hints, which helps catch bugs in complex tensor operations early.
- Imports: You can import your logic anywhere (like in a notebook) using from my_awesome_package.module import function.

3. Data & Model Storage
- data/: Keep your data organized. Datasets should be ignored by Git.
- models/: Use this for .pt, .onnx, or .pkl files.
- data/ & models/: These directories contain .gitkeep so they exist in the repo, but the actual data is ignored by Git
- Storage Policy: All production data and large model weights must be stored on the company buckets. Local folders are for temporary processing only.


Best Practices
1. Use Type Hints: AI code is prone to "shape errors." Always type-hint your functions to clarify what dimensions or types are expected.
2. Keep Notebooks Clean: Use notebooks for exploration. Once a function works, move it into the src/ directory so it can be tested and reused.
3. Environment Safety: Never hardcode paths. Use relative paths or environment variables from conf.env.

## Documentation Standards

We follow the **Google Python Style Guide** for all docstrings. Every function in `src/` must be documented to explain the "what," the "how," and the "types."

### Docstring Template
Use the following structure for your functions:

```python
def estimate_length(p1: np.ndarray, p2: np.ndarray) -> tuple[float, list[np.ndarray]]:
    """Estimate fish length by projecting endpoints onto the center's depth plane.

    The two endpoints are first adjusted so their depth matches the depth of the
    fish's center. They are then back-projected into world coordinates.

    Args:
        p1 (numpy.ndarray): Pixel coordinates of the first endpoint
            as an array [u, v, z], where (u, v) are in pixels and z is depth
            in millimeters.
        p2 (numpy.ndarray): Pixel coordinates of the second endpoint,
            same format as p1.

    Returns:
        length_cm (float): Estimated total length in centimeters.
        corrected_endpoints (list[numpy.ndarray]): Two world coordinate
            points corresponding to the corrected endpoints.

    Raises:
        ValueError: If the center's depth value is NaN or invalid.

    Examples:
        >>> p1 = np.array([150, 200, 2.5])
        >>> p2 = np.array([300, 200, 2.0])
        >>> length, pts = estimate_length(p1, p2)
    """
    pass
```
### Code Quality & Pre-commit

We use automated tools to maintain high code standards. These tools prevent common bugs, enforce formatting, and ensure security.

1. Pre-commit Configuration
You must create a .pre-commit-config.yaml file in the project root and paste the following content. This configuration handles everything from linting (Ruff) to security (Gitleaks) and spell-checking (Typos).

```yml
default_language_version:
    python: python3.10

#exclude: "tests/artifacts/.*\\.safetensors$"

repos:
  ##### Meta #####
  - repo: meta
    hooks:
      - id: check-useless-excludes
      - id: check-hooks-apply

   ##### General Code Quality & Formatting #####
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v6.0.0
    hooks:
      - id: check-added-large-files
        args: ['--maxkb=1024']
      - id: debug-statements
      - id: check-merge-conflict
      - id: check-case-conflict
      - id: check-yaml
      - id: check-toml
      - id: end-of-file-fixer
      - id: trailing-whitespace

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.14.1
    hooks:
      - id: ruff-format
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]

  - repo: https://github.com/adhtruong/mirrors-typos
    rev: v1.38.1
    hooks:
      - id: typos
        args: [--force-exclude]

  - repo: https://github.com/asottile/pyupgrade
    rev: v3.21.0
    hooks:
    -   id: pyupgrade
        args: [--py310-plus]

  ##### Markdown Quality #####
  - repo: https://github.com/rbubley/mirrors-prettier
    rev: v3.6.2
    hooks:
      - id: prettier
        name: Format Markdown with Prettier
        types_or: [markdown, mdx]
        args: [--prose-wrap=preserve]

  ##### Security #####
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.28.0
    hooks:
      - id: gitleaks

  # - repo: https://github.com/woodruffw/zizmor-pre-commit
  #   rev: v1.15.2
  #   hooks:
  #     - id: zizmor

  - repo: https://github.com/PyCQA/bandit
    rev: 1.8.6
    hooks:
    - id: bandit
      args: ["-c", "pyproject.toml"]
      additional_dependencies: ["bandit[toml]"]

  # TODO: Uncomment when ready to use
  ##### Static Analysis & Typing #####
  - repo: local
    hooks:
    - id: mypy
      name: mypy
      entry: mypy
      language: system
      types: [python]
      require_serial: true
      args: ["--config-file=pyproject.toml"]
```

2. Mypy Configuration
Add the following block to your pyproject.toml. This tells the type-checker how to handle your specific package:

```yml
[tool.mypy]
python_version = "3.10"
ignore_missing_imports = true
follow_imports = "skip"

[[tool.mypy.overrides]]
# Default: lenient on the whole package during migration
module = "my_awesome_package.*"
ignore_errors = false
```
To check all files without committing:
```sh
make lint
```
