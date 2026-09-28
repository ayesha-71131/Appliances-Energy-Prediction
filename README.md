# Appliances Energy Prediction

MLOps project for reproducible prediction of appliance energy consumption.

## Project Status

Repository foundation and development environment are being established.
ML pipeline, dataset versioning, CI, and experiments are developed through
separate feature branches.

## Repository Structure

- `.claude/specs/` — specifications, plans, and task definitions
- `data/` — dataset artifacts managed through the project workflow
- `src/` — reusable source code
- `tests/` — automated tests
- `notebooks/` — exploratory analysis
- `models/` — generated model artifacts
- `configs/` — configuration and experiment parameters
- `.github/workflows/` — CI workflows

## Setup

Install uv.

Then:

```bash
uv sync

## Run tests

```sh
uv run pytest
```

## Development workflow

Create a feature branch from `dev`, make focused changes, and open a pull
request targeting `dev`. Request teammate review and run the local checks before
opening the PR. See [CONTRIBUTING.md](CONTRIBUTING.md) for details.
