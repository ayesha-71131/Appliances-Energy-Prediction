# Pre-Commit Hooks Specification

## 1. Purpose

Establish automated local quality checks that run before commits in the
Appliances Energy Prediction MLOps project.

The checks shall help prevent formatting issues, notebook metadata
noise, oversized files, and accidentally committed secrets.

## 2. Scope

This specification covers:

- Ruff linting
- Ruff formatting
- notebook output cleanup with nbstripout
- large-file detection
- secret detection
- Git pre-commit hook installation

## 3. Non-Goals

This task does not implement:

- CI/CD workflows
- machine-learning models
- dataset ingestion
- DVC pipelines
- experiment tracking
- production deployment

## 4. Required Checks

The pre-commit configuration shall include:

- Ruff linting
- Ruff formatting
- nbstripout for Jupyter notebooks
- check-added-large-files with a 1 MB limit
- detect-secrets for secret scanning

## 5. Configuration

The repository shall contain:

    .pre-commit-config.yaml

The project shall use the existing uv environment for running pre-commit.

Developers shall install the Git hook using:

    uv run pre-commit install

## 6. Verification

All configured hooks shall be executable with:

    uv run pre-commit run --all-files

The checks shall pass on the existing repository files.

The large-file check shall reject files larger than 1 MB.

The secret scanner shall detect accidentally added credentials or API
keys.

## 7. Git Rules

The pre-commit configuration shall be committed to Git.

The local Python environment and generated files shall not be committed.

Pre-commit changes shall be developed on a feature branch and merged
into `dev` through a pull request.

## 8. Acceptance Criteria

The implementation is complete when:

1. `.pre-commit-config.yaml` exists.
2. Ruff linting is configured.
3. Ruff formatting is configured.
4. nbstripout is configured.
5. Added files larger than 1 MB are blocked.
6. Secret scanning is configured.
7. `uv run pre-commit install` succeeds.
8. `uv run pre-commit run --all-files` passes.
9. The changes are reviewed through a pull request.
10. No local environment or secret is committed.