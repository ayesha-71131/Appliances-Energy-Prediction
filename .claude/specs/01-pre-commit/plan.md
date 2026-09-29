# Pre-Commit Hooks Plan

## Phase 1 — Pre-commit dependency

Add `pre-commit` as a development dependency using uv.

Verify:

    uv run pre-commit --version

## Phase 2 — Hook configuration

Create `.pre-commit-config.yaml`.

Configure:

- Ruff linting
- Ruff formatting
- nbstripout
- check-added-large-files with a 1 MB limit
- detect-secrets

## Phase 3 — Install hooks

Install the Git hook:

    uv run pre-commit install

## Phase 4 — Verification

Run all configured hooks against the repository:

    uv run pre-commit run --all-files

Verify that all applicable checks pass.

## Phase 5 — Safety verification

Verify that:

- a file larger than 1 MB is rejected
- a test secret/API key is detected
- generated local environments are not committed

## Phase 6 — Pull Request

Commit the Phase 3 changes on:

    feat/pre-commit

Push the branch and create a pull request into:

    dev

A teammate shall review the pull request before merge.