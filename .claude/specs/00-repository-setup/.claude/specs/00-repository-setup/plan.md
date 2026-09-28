# Repository Setup Plan

## Phase 1 — Repository structure

Create the project directories:

- `.claude/specs`
- `data/raw`
- `data/processed`
- `notebooks`
- `src`
- `tests`
- `models`
- `configs`
- `.github/workflows`

## Phase 2 — Python project configuration

Create `pyproject.toml`.

Define:

- project metadata
- supported Python version
- runtime dependencies required by the current project
- development dependencies
- pytest configuration

Do not invent ML dependencies before starter-code requirements are known.

## Phase 3 — Environment lock

Use uv to resolve dependencies:

    uv lock

Then create the environment:

    uv sync

Commit `uv.lock`.

## Phase 4 — Git hygiene

Create `.gitignore`.

Ignore:

- `.venv`
- Python caches
- notebook checkpoints
- local environment files
- generated datasets
- model artifacts
- DVC cache
- editor-specific files

Do not ignore:

- source code
- tests
- configuration
- DVC pointer files
- `dvc.yaml`
- `dvc.lock`
- `params.yaml`
- metrics files

## Phase 5 — Testing foundation

Configure pytest so that:

    uv run pytest

can be executed from the repository root.

Create a minimal smoke test to validate the test infrastructure.

## Phase 6 — Documentation

Create:

- `README.md`
- `CONTRIBUTING.md`

Document local setup and the team's branch/PR workflow.

## Phase 7 — Verification

Run:

    uv sync
    uv run pytest
    git status

Verify that only intended files are tracked.

## Phase 8 — Pull Request

Push:

    feat/repo-setup

Create a PR into `dev`.

At least one teammate reviews the PR before merge.