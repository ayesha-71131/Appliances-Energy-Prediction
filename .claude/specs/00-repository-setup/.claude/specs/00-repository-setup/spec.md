# Repository Setup Specification

## 1. Purpose

Establish a reproducible and structured repository baseline for the
Appliances Energy Prediction MLOps project.

This specification defines the repository structure, development
environment expectations, source-code organization, testing location,
configuration conventions, and documentation requirements.

The implementation must provide a clean baseline on which later MLOps
features can be developed through feature branches and pull requests.

## 2. Scope

This specification covers:

- repository directory structure
- Python project configuration
- uv-based dependency management
- test configuration
- Git ignore rules
- project documentation
- development workflow documentation
- Spec-Driven Development structure

## 3. Non-Goals

This task does not implement:

- machine-learning models
- dataset ingestion
- DVC pipeline
- EDA
- pre-commit hooks
- GitHub Actions CI
- production release

Those are separate specifications and tasks.

## 4. Repository Structure

The repository shall use the following structure:

    .claude/
    └── specs/

    data/
    ├── raw/
    └── processed/

    notebooks/

    src/
    tests/

    models/

    configs/

    .github/
    └── workflows/

The following root-level project files shall be supported:

    README.md
    CONTRIBUTING.md
    pyproject.toml
    .gitignore

## 5. Python Environment

Python dependencies shall be declared in pyproject.toml.

uv shall be used for dependency resolution and environment creation.

A uv.lock file shall be committed so that the environment can be
reproduced.

A developer should be able to execute:

    uv sync

and obtain the project environment.

## 6. Testing

Tests shall live under:

    tests/

Pytest shall be the test framework.

The repository shall support:

    uv run pytest

## 7. Git Rules

Generated environments and machine-specific files shall not be committed.

Large datasets shall not be stored directly in Git.

Future dataset artifacts shall be managed through DVC.

Secrets, credentials, local environment files, caches, and Python
generated files shall not be committed.

## 8. Documentation

README.md shall explain:

- project purpose
- project structure
- local setup
- how to run tests
- development workflow

CONTRIBUTING.md shall explain:

- branch naming
- commit conventions
- pull-request workflow
- review expectations
- required local checks

## 9. Acceptance Criteria

The repository setup is complete when:

1. The required directory structure exists.
2. pyproject.toml defines the Python project.
3. uv.lock is committed.
4. `uv sync` completes successfully.
5. `uv run pytest` executes successfully.
6. Git ignores local/generated artifacts.
7. README.md documents local setup.
8. CONTRIBUTING.md documents the Git workflow.
9. The implementation is reviewed through a pull request.
10. No dataset or secret is committed.

## 10. Verification

The setup shall be validated from a clean working tree with:

    uv sync
    uv run pytest
    git status