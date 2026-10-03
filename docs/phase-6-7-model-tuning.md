# Phase 6 & 7: Model Training and Experiments

Owner of this part: **Zarwa (Model owner)**. Branch for the pipeline: `feat/dvc-pipeline`
(PR into `dev`). Experiments live on personal `exp/<member>-<idea>` branches.

## 1. Files

| File | What it does |
|---|---|
| `src/train.py` | Trains `random_forest` or `hist_gradient_boosting`, chosen by `train.model` |
| `src/evaluate.py` | Scores the val and test splits, writes `metrics.json` (MAE, RMSE, R², commit SHA) |
| `configs/params.yaml` | Every setting: seed, model, hyperparameters, features, split |
| `dvc.yaml` | Stages: `validate` -> `prepare` -> `train` -> `evaluate` |
| `dvc.lock` | Exact hashes of the last run (what makes a run reproducible) |
| `tests/test_train.py` | Unit tests: both models, seeded reproducibility, metrics |
| `metrics.json` | Metrics of the committed baseline |
| `.gitignore`, `.gitattributes` | Fixes needed for DVC (see section 6) |

## 2. Plan

1. Build `train` and `evaluate` stages; seed and every hyperparameter in `params.yaml`. (done)
2. Fit preprocessing on the training split only. Both models are tree ensembles and need no
   scaler; a scale-sensitive model would need a scaler fitted on `train.csv` only. (done)
3. Log the git commit SHA in `metrics.json`. (done)
4. Run `dvc repro`, `dvc push`, then `git push`; open the PR. (done, PR 7)
5. Run at least 3 experiments per member with `dvc exp run`, compare with `dvc exp show`.
6. Promote the winner (by **validation** R²) to a `feat/` branch and open a PR into `dev`.
7. Keep one experiment branch unmerged and explain why in `REPORT.md`.

## 3. What is done

- Pipeline works end to end and gives identical metrics on a re-run.
- Baseline (random forest, default params): val R² 0.525, test R² 0.244.
- Gradient boosting baseline: val R² 0.577, test R² 0.358.

Experiments already run (each changes exactly one setting from the gradient boosting baseline):

| Name | Change | Val R² | Test R² | Test MAE |
|---|---|---|---|---|
| gb-baseline | none | 0.577 | 0.358 | 46.3 |
| **gb-lr02** | `learning_rate=0.02`, `max_iter=600` | **0.601** | **0.498** | 32.1 |
| rolling | `rolling_windows=[6,36]` | 0.595 | 0.467 | 38.1 |
| lags-more | `lags=[1,2,6,36,144,1008]` | 0.560 | 0.453 | 39.3 |
| gb-depth8 | `max_depth=8` | 0.579 | 0.351 | 46.6 |
| drop-rv | `drop_columns=[rv1,rv2]` | 0.567 | 0.190 | 60.1 |
| rf-baseline | `model=random_forest` | 0.525 | 0.244 | 46.8 |

Current best by validation: **gb-lr02**.

## 4. Experiments still to do (12, four per member)

Rules for every experiment:
- Branch from `dev`: `git switch -c exp/<name>-<idea> dev`. Commit before running.
- Change **one** setting from the baseline, except where a combo is stated.
- Use `uv run dvc ...`, never a bare `dvc` (a bare one picks up the wrong Python).
- Reset between runs (see section 5). Choose the winner by validation R², not test R².
- `-S` means `--set-param`. Our params file is not in the repo root, so always write
  `configs/params.yaml:<key>=<value>`.
- Add `-S configs/params.yaml:train.model=hist_gradient_boosting` to every command, because the
  committed default is `random_forest`.

### Member A: Zarwa (Model owner): model hyperparameters

| # | Name | Change |
|---|---|---|
| A1 | `gb-leaf50` | `train.hist_gradient_boosting.min_samples_leaf=50` on top of lr 0.02 / 600 |
| A2 | `gb-lr01` | `learning_rate=0.01`, `max_iter=1200` |
| A3 | `gb-depth4` | `max_depth=4` on top of lr 0.02 / 600 |
| A4 | `rf-tuned` | `model=random_forest`, `n_estimators=500`, `max_depth=20`, `min_samples_leaf=3` |

### Member B: Data owner: features

| # | Name | Change |
|---|---|---|
| B1 | `lags-short` | `prepare.lags=[1,2,3,6]` |
| B2 | `lags-day-week` | `prepare.lags=[1,6,144,1008]` |
| B3 | `rolling-long` | `prepare.rolling_windows=[36,144]` |
| B4 | `no-temporal` | `prepare.temporal_features=false` |

### Member C: Platform owner: combinations and reliability

| # | Name | Change |
|---|---|---|
| C1 | `combo-lr-roll` | lr 0.02 / 600 **and** `rolling_windows=[6,36]` |
| C2 | `combo-lr-roll-lags` | C1 **and** `lags=[1,2,6,36,144,1008]` |
| C3 | `seed-7` | `seed=7` on the baseline, to measure how noisy the scores are |
| C4 | `seed-123` | `seed=123` on the baseline, same reason |

Example command (A2):
```bash
uv run dvc exp run -n gb-lr01 \
  -S configs/params.yaml:train.model=hist_gradient_boosting \
  -S configs/params.yaml:train.hist_gradient_boosting.learning_rate=0.01 \
  -S configs/params.yaml:train.hist_gradient_boosting.max_iter=1200
```

Phase 7 also needs a deliberate merge conflict: A and B each edit the `train.model` line of
`configs/params.yaml` on their own branch. The second PR rebases on `dev` and documents the
resolution.

## 5. How to run experiments safely

```bash
git checkout -- configs/params.yaml dvc.lock metrics.json   # reset the workspace
uv run dvc checkout                                         # restore data and model
uv run dvc exp run -n <name> -S ...                         # run one experiment
uv run dvc exp show                                         # compare all experiments
uv run dvc exp apply <name>                                 # put the winner in the workspace
```

## 6. Lessons learned (add to CONTRIBUTING.md)

1. **Experiments chain.** `dvc exp run` applies its result to the workspace, so the next run
   starts from it. Reset between runs.
2. **DVC reuses old results.** Its run cache ignores the Python environment. After a wrong run,
   delete `.dvc/cache/runs`.
3. **Use `uv run dvc`.** A bare `dvc` runs stages with the global Python (different
   scikit-learn/pandas versions, different scores).
4. **`.gitignore` can hide the raw data from DVC.** The rule `data/raw/*` made DVC skip the
   `data/raw/` folder, so `dvc exp run` deleted the raw CSV. The rule is now `data/raw/*.csv`.
5. **Line endings change `dvc.lock`.** `.gitattributes` (`* text=auto eol=lf`) keeps hashes
   the same on every machine.
6. **Always `dvc push` before `git push`.**
