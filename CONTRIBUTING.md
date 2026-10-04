# Contributing

## Branching Model

We follow a strict one-way flow: `feat/` & `data/` $\rightarrow$ `dev` $\rightarrow$ `staging` $\rightarrow$ `main`.

| Branch | Purpose | Created from | Merges into | Protection |
| :--- | :--- | :--- | :--- | :--- |
| `main` | Production: released, tagged models | — | — | PR only, 1 approval, CI pass |
| `staging` | Release candidate; validated | `main` | `main` | PR only, 1 approval, CI pass |
| `dev` | Integration of finished work | `main` | `staging` | PR only, 1 approval, CI pass |
| `feat/<name>` | Production code: features, pipeline | `dev` | `dev` | Deleted after merge |
| `data/<name>` | Dataset updates tracked with DVC | `dev` | `dev` | Deleted after merge |
| `exp/<member>-<idea>` | Exploration; may never merge | `dev` | Nothing | Cherry-pick winner to `feat/` |
| `fix/<name>` | Urgent fix to production | `main` | `main` $\rightarrow$ `dev` | Deleted after merge |

## Workflow

1. **Update Specification**: Ensure the task is defined.
2. **Branch**: Create a branch from `dev` (or `main` for hotfixes).
3. **Implement**: Develop the feature, pipeline change, or data update.
4. **DVC Push**: If data/models changed, run `dvc push` **before** `git push`.
5. **Local Checks**: Run `uv sync` and `uv run pytest`.
6. **Pull Request**: Open a PR into `dev`.
7. **Review**: Request a teammate's review. Address comments.
8. **Merge**: Merge only after approval and CI checks pass.

## Role Responsibilities

To streamline contributions and reviews, please coordinate with the respective owners:

- **Data Owner (Ayesha Waheed)**: Consult for DVC changes, data validation, or dataset updates.
- **Model Owner (Zarwa)**: Consult for changes to the training pipeline, hyperparameters, or experiment configs.
- **Platform Owner (Mahnoor Aslam)**: Consult for CI/CD updates, pre-commit hooks, or environment configurations.

## Commits

Use **Conventional Commits** for messages:
- `feat: add scaling step`
- `fix: resolve null handling in src/train.py`
- `data: remove duplicate rows`
- `exp: try max_depth=8`
- `docs: update README`
- `chore: update dependencies`

## Pull Requests and Review

All changes arrive via PRs. 
**Merge Strategy**: We use **squash-merges** into `dev` to keep the integration history clean.

### Review Checklist
Every PR must be reviewed against:
- [ ] No data leakage (no target or future information in features)
- [ ] Splits are fixed; preprocessing fit on training data only
- [ ] No hardcoded paths; runs on a teammate's machine
- [ ] Seeds set for shuffling, initialisation and sampling
- [ ] Metric computed the way the team reports it
- [ ] `dvc push` done before `git push` (if data or models changed)
- [ ] Notebook restarted and run top to bottom (if notebooks changed)
- [ ] Style and naming (linter passes)

## Local checks

For Python project changes, synchronize the environment and run the test suite:

```sh
uv sync
uv run pytest
```

Keep datasets, model outputs, credentials, and local environment files out of Git.
