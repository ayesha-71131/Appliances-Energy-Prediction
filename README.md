# Appliances Energy Prediction

MLOps project for reproducible prediction of appliance energy consumption. This project follows the "Git-Based Collaboration for an ML Project" framework to ensure full reproducibility and professional collaboration.

## Project Status

Repository foundation and development environment are being established.
ML pipeline, dataset versioning, CI, and experiments are developed through
separate feature branches.

## Project Governance

To ensure clear ownership and accountability, the project is divided into the following roles:

- **Data Owner (Ayesha Waheed)**: Responsible for DVC, data checks, and dataset updates.
- **Model Owner (Zarwa)**: Responsible for the training pipeline, configs, and experiments.
- **Platform Owner (Mahnoor Aslam)**: Responsible for CI, pre-commit, environment, and releases.

## Repository Structure

- `.claude/specs/` — specifications, plans, and task definitions
- `configs/` — configuration and experiment parameters (e.g., `params.yaml`)
- `data/` — dataset artifacts managed through DVC (ignored by Git)
- `models/` — generated model artifacts managed through DVC (ignored by Git)
- `src/` — reusable, tested source code
- `tests/` — automated tests
- `notebooks/` — exploratory analysis (using Jupytext for clean diffs)
- `.github/workflows/` — CI workflows

## Setup

Install `uv`.

Then:

```bash
uv sync
```

## Run tests

```sh
uv run pytest
```

## Development workflow

Create a feature branch from `dev`, make focused changes, and open a pull
request targeting `dev`. Request teammate review and run the local checks before
opening the PR. See [CONTRIBUTING.md](CONTRIBUTING.md) for details.
