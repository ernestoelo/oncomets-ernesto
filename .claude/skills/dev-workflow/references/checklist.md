# AI Project Development – Repository Self-Validation Checklist

This checklist defines the **mandatory self-validation requirements**
for any AI/ML project repository.

Each project team is responsible for ensuring that **all applicable items
are satisfied before the repository is considered ready for use,
deployment, or handover**.

This checklist is intended for **self-validation**, not formal review.

---

## 1. Overview

- [ ] A README.md exists at the repository root
- [ ] The project description is clear and concise
- [ ] The main purpose of the AI/ML system is explicitly stated
- [ ] The problem being solved is clearly defined
- [ ] Model architecture or approach is documented
- [ ] Expected inputs and outputs are described

---

## 2. Project Structure

- [ ] Project was initialized using `uv init --lib`
- [ ] Source code is organized in `src/` directory
- [ ] A `.python-version` file exists
- [ ] A `pyproject.toml` file exists with project metadata
- [ ] A `uv.lock` file exists and is committed
- [ ] A `data/` directory exists with `.gitkeep`
- [ ] A `models/` directory exists with `.gitkeep`
- [ ] A `notebooks/` directory exists for exploratory work
- [ ] A `.gitignore` file properly excludes `.venv/`, `data/*`, `models/*`, and `conf.env`

---

## 3. Environment Management

- [ ] Python version is pinned using `uv python pin`
- [ ] All dependencies are managed via `uv add`
- [ ] Development dependencies are separated from core dependencies
- [ ] `conf.env` is used for environment variables (not committed)

---

## 4. Code Quality

- [ ] All functions in `src/` have type hints
- [ ] All functions follow Google Python docstring style
- [ ] A `.pre-commit-config.yaml` file exists
- [ ] A `pyproject.toml` section exists for Mypy configuration
- [ ] Code passes `make lint` without errors

---

## 5. Automation Scripts

- [ ] A `run.sh` script exists with `install` and `lint` functions
- [ ] The `run.sh` script is executable
- [ ] A `Makefile` exists with at least `install` and `lint` targets
- [ ] `make install` successfully sets up the environment
- [ ] `make lint` runs all pre-commit checks

---

## 6. Execution

- [ ] A `main.py` entry point exists
- [ ] If using Metaflow, a `flows/` directory exists
- [ ] Pipeline orchestration is documented

---

## 7. Data Management

- [ ] Local `data/` folder is used only for temporary processing
- [ ] Production data location (buckets/storage) is specified
- [ ] Data loading and preprocessing steps are in `src/`
- [ ] No data files are committed to Git (except `.gitkeep`)

---

## 8. Model Management

- [ ] Model artifacts are stored in `models/` locally
- [ ] Production model storage location is documented
- [ ] Model loading and inference code is in `src/`
- [ ] No model files are committed to Git (except `.gitkeep`)

---

## 9. Notebooks

- [ ] Notebooks are used only for exploration and prototyping
- [ ] Working functions are moved from notebooks to `src/`
- [ ] Notebook checkpoints are ignored by Git

---

## 10. Containerization

- [ ] A `Dockerfile` exists if the project is containerized
- [ ] The Dockerfile uses the pinned Python version
- [ ] Container build instructions are documented
- [ ] Container execution instructions are documented
- [ ] Development dependencies are excluded from production containers
- [ ] Environment variables are managed via `conf.env` in containers
- [ ] A command to run the container is provided in Makefile

---

## 11. Documentation Standards

- [ ] README reflects the current state of the project
- [ ] All documented commands exist and work as described
- [ ] Dependencies are up to date in documentation
- [ ] Common errors and troubleshooting are documented
- [ ] Examples of usage are provided

---

## 12. Security

- [ ] No secrets or API keys are committed
- [ ] `conf.env` is in `.gitignore`
- [ ] No hardcoded credentials in code or notebooks

---

## Self-Validation Statement

By completing this checklist, the team confirms that:

- The repository meets the minimum organizational standards for AI projects
- The environment can be reproduced by a new team member
- The code follows quality and security best practices
- The documentation reflects the actual system behavior

Date:
Validated by:
Notes:
