# REPORT

> Work in progress. This section was written by the Model owner (Zarwa); the other
> sections (team, reproducibility table, screenshots, retrospective) are added by the team.

## Experiments (Model owner)

Task: predict appliance energy use (Wh) 10 minutes ahead. Chronological split
(70% train / 15% validation / 15% test), seed 42. All numbers come from
`uv run dvc exp run` on committed code, and are sorted by validation R².

| Experiment | Change | Val R² | Test R² | Test MAE (Wh) | Test RMSE (Wh) |
|---|---|---|---|---|---|
| **gb-leaf50** | lr 0.02/600 + min_samples_leaf=50 | 0.613 | 0.522 | 30.8 | 62.9 |
| gb-leaf100 | lr 0.02/600 + min_samples_leaf=100 | 0.606 | 0.546 | 28.6 | 61.3 |
| gb-leaf200 | lr 0.02/600 + min_samples_leaf=200 | 0.604 | 0.545 | 29.0 | 61.3 |
| gb-lr02 | learning_rate=0.02, max_iter=600 | 0.601 | 0.498 | 32.1 | 64.4 |
| gb-depth4 | lr 0.02/600 + max_depth=4 | 0.596 | 0.463 | 41.4 | 66.7 |
| rolling | baseline + rolling_windows=[6,36] | 0.595 | 0.467 | 38.1 | 66.4 |
| gb-lr01 | learning_rate=0.01, max_iter=1200 | 0.595 | 0.470 | 35.2 | 66.2 |
| gb-depth8 | baseline + max_depth=8 | 0.579 | 0.352 | 46.6 | 73.2 |
| gb-baseline | gradient boosting, defaults (lr 0.05, 300 rounds, depth 6, leaf 20) | 0.578 | 0.359 | 46.3 | 72.8 |
| drop-rv | baseline + drop rv1, rv2 | 0.568 | 0.191 | 60.1 | 81.8 |
| lags-more | baseline + lags=[1,2,6,36,144,1008] | 0.560 | 0.453 | 39.3 | 67.6 |
| rf-baseline | random forest, defaults (200 trees, depth 12, leaf 5) | 0.525 | 0.245 | 46.8 | 79.1 |
| rf-tuned | random forest, 500 trees, depth 20, leaf 3 | 0.464 | -0.050 | 58.0 | 93.2 |

### Why `gb-leaf50` won
- The winner is chosen by **validation** R², never by test R², so the test set stays an honest check.
- `gb-leaf50` has the best validation R² (0.613) and a clearly better test score than the baseline
  (0.522 vs 0.359).
- `min_samples_leaf` 100 and 200 score slightly higher on test but lower on validation. The gaps
  between 50, 100 and 200 are within noise, so we kept the one that won on validation.
- Lessons: slower learning (lr 0.02) and bigger leaves (min 50) help because the target is spiky and
  smoother trees generalise better. Removing the noise columns `rv1`/`rv2` surprisingly hurt on test.

### Metrics before and after

| | Val R² | Test R² | Test MAE (Wh) | Test RMSE (Wh) |
|---|---|---|---|---|
| Before (committed baseline, random forest) | 0.525 | 0.245 | 46.8 | 79.1 |
| After (`gb-leaf50`, gradient boosting) | 0.613 | 0.522 | 30.8 | 62.9 |

### Abandoned experiment branch
[`exp/zarwa-rf-tuned`](https://github.com/ayesha-71131/Appliances-Energy-Prediction/tree/exp/zarwa-rf-tuned)
(never merged). A bigger, deeper random forest (500 trees, depth 20, leaf 3) did **worse** than the
untuned one: validation R² 0.464, test R² -0.050 (worse than predicting the mean). Larger forests
overfit this spiky data, and gradient boosting was already clearly better, so the branch was
abandoned.

### How to reproduce
```bash
git checkout feat/tune-gradient-boosting
uv sync
uv run dvc pull
uv run dvc repro        # metrics.json must match the table above
```
Settings live in `configs/params.yaml`; stages in `dvc.yaml`. Always run DVC through `uv run`.
