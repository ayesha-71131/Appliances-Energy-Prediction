# Experiments

**Author:** Zarwa (Model owner)
**Project:** Appliances Energy Prediction (Phases 6 and 7)

This file explains, in simple words, what I built, what experiments I ran, what I found, and
which one won.

---

## 1. The goal

Predict how much energy the house appliances will use **10 minutes from now** (in Wh), using
temperature, humidity, weather, lights and the recent past of the appliance energy itself.

The data is a time series (one row every 10 minutes), so I split it by time, not randomly:

| Part | Share | Used for |
|---|---|---|
| Train | first 70% | teaching the model |
| Validation | next 15% | choosing the best settings |
| Test | last 15% | the final honest check |

---

## 2. What I built (my working)

1. **`src/train.py`** trains a model. Which model, and all its settings, come from
   `configs/params.yaml`, so nothing is hard-coded.
2. **`src/evaluate.py`** scores the model on validation and test and saves the result in
   `metrics.json`. It also saves the git commit, so every result can be traced to its code.
3. **`dvc.yaml`** connects the steps: `validate` -> `prepare` -> `train` -> `evaluate`.
   `dvc repro` runs them in order and only re-runs what changed.
4. **Tests** in `tests/test_train.py` check both models, the seed, and the metrics.
5. **Seed 42** is used everywhere, so the same settings always give the same numbers.
6. **Data safety:** the model only sees the past. No future information leaks into the features,
   and the split is by time.

### How to read the scores

| Score | Meaning | Better is |
|---|---|---|
| **R²** | How much of the ups and downs the model explains (1 = perfect, 0 = as good as guessing the average, below 0 = worse than guessing) | higher |
| **MAE** | Average mistake in Wh | lower |
| **RMSE** | Like MAE but punishes big mistakes more | lower |

I pick the winner by **validation R²**. The test score is only a final check. If I picked by
test score, the test set would stop being an honest check.

---

## 3. The two models

| Model | Simple idea |
|---|---|
| **Random forest** | Many decision trees vote independently and the votes are averaged. Hard to break, but not the sharpest. |
| **Gradient boosting** | Trees are built one after another, and each new tree fixes the mistakes of the previous ones. Usually more accurate. |

Two gradient boosting settings matter most here:
- **Learning rate:** how big each correction step is. Smaller steps are slower but safer.
- **`min_samples_leaf`:** the smallest group of rows a tree may split off. A bigger number makes
  the model ignore small, noisy clusters.

---

## 4. All experiments, compared

Every experiment changes **one thing** from its starting point, so any difference is caused by
that one change. Sorted by validation R² (best first).

| Experiment | What I changed | Val R² | Test R² | Test MAE | Test RMSE |
|---|---|---|---|---|---|
| **gb-leaf50** | learning rate 0.02, 600 rounds, `min_samples_leaf` 50 | **0.613** | 0.522 | 30.8 | 62.9 |
| gb-leaf100 | same, `min_samples_leaf` 100 | 0.606 | 0.546 | 28.6 | 61.3 |
| gb-leaf200 | same, `min_samples_leaf` 200 | 0.604 | 0.545 | 29.0 | 61.3 |
| gb-lr02 | learning rate 0.02, 600 rounds | 0.601 | 0.498 | 32.1 | 64.4 |
| gb-depth4 | lr 0.02/600, tree depth 4 | 0.596 | 0.463 | 41.4 | 66.7 |
| rolling | add 1 h and 6 h rolling averages | 0.595 | 0.467 | 38.1 | 66.4 |
| gb-lr01 | learning rate 0.01, 1200 rounds | 0.595 | 0.470 | 35.2 | 66.2 |
| gb-depth8 | tree depth 8 | 0.579 | 0.352 | 46.6 | 73.2 |
| gb-baseline | gradient boosting, default settings | 0.578 | 0.359 | 46.3 | 72.8 |
| drop-rv | remove the 2 random noise columns | 0.568 | 0.191 | 60.1 | 81.8 |
| lags-more | add 20 min, 6 h and 1 week history | 0.560 | 0.453 | 39.3 | 67.6 |
| rf-baseline | random forest, default settings | 0.525 | 0.245 | 46.8 | 79.1 |
| rf-tuned | random forest, 500 trees, depth 20 | 0.464 | -0.050 | 58.0 | 93.2 |

---

## 5. What each experiment taught me

**My three main experiments**

1. **`gb-lr02` (smaller learning rate).** Test R² went from 0.36 to 0.50. Smaller steps make the
   model learn the real pattern instead of chasing noise. A big first win.
2. **`gb-leaf50` (bigger leaves) is the winner.** On top of the smaller learning rate, requiring
   at least 50 rows per leaf gave the best validation score (0.613). Energy use is spiky, so
   forcing the model to ignore tiny groups of rows makes it generalise better.
3. **`rf-tuned` (bigger random forest) is abandoned.** Test R² fell to -0.05, which is worse
   than guessing the average. More and deeper trees memorised the noise. This is the
   experiment I did **not** merge (branch `exp/zarwa-rf-tuned`).

**Other experiments**

| Experiment | What I learned |
|---|---|
| gb-leaf100 / gb-leaf200 | Bigger leaves stop helping around 50. The gaps are small and within noise. |
| gb-lr01 | Going even slower than 0.02 did not help. The benefit has run out. |
| gb-depth4 / gb-depth8 | Depth 6 is about right. Too shallow misses patterns; too deep overfits. |
| rolling | Smoothed recent averages help: test R² 0.36 -> 0.47. Worth combining with `gb-leaf50` later. |
| lags-more | More history gave mixed results: worse on validation, better on test. |
| drop-rv | Removing the noise columns hurt on test, a surprise. Likely noise in the scores. |
| rf-baseline | Random forest with default settings is clearly weaker than gradient boosting. |

---

## 6. Before and after

| | Val R² | Test R² | Test MAE | Test RMSE |
|---|---|---|---|---|
| Before (random forest baseline) | 0.525 | 0.245 | 46.8 | 79.1 |
| **After (`gb-leaf50`)** | **0.613** | **0.522** | **30.8** | **62.9** |

Test R² roughly doubled, and the typical mistake dropped from about 47 Wh to about 31 Wh.

---

## 7. Problems I hit and fixed

| Problem | Cause | Fix |
|---|---|---|
| `dvc exp run` deleted the raw data file | `.gitignore` rule `data/raw/*` made DVC skip the whole folder | Changed it to `data/raw/*.csv` |
| Same code gave different `dvc.lock` hashes | Windows vs Unix line endings | Added `.gitattributes` (`* text=auto eol=lf`) |
| Experiments gave strange, repeated numbers | Experiments carried each other's changes, and DVC reused old cached results | Reset the workspace between runs and cleared `.dvc/cache/runs` |
| Scores differed between runs | I ran `dvc` with the global Python, which had different library versions | Always run `uv run dvc ...` |

---

## 8. How to reproduce my result

```bash
git checkout feat/tune-gradient-boosting
uv sync
uv run dvc pull
uv run dvc repro        # metrics.json should match the table
```

## 9. What is left to try

- Combine the best ideas: `gb-leaf50` plus rolling averages.
- Teammates run their own experiments (see `docs/phase-6-7-model-tuning.md`).
- Check how noisy the scores are by trying other seeds (7 and 123).

---

## 10. Data and feature experiments (Ayesha)

**Branch:** `exp/ayesha-data-features`
**Starting point:** `gb-leaf50` (the winner above). Each experiment changes one thing from this baseline. Decision rule: validation decides, test confirms.

| Experiment | What I changed | Val R2 | Test R2 | Test MAE | Test RMSE | Commit | Verdict |
|---|---|---|---|---|---|---|---|
| baseline (`gb-leaf50`) | nothing | 0.6126 | 0.5219 | 30.8 | 62.9 | n/a | n/a |
| ayesha-drop-rv | drop `rv1`, `rv2` | 0.6105 | 0.4963 | 34.8 | 64.6 | 8bdcf7f | **Failed** |
| ayesha-rolling | rolling windows `[6, 36]` | 0.6072 | 0.5342 | 30.2 | 62.1 | 4d429c4 | **Inconclusive** |
| ayesha-lags | lags `[1, 2, 3, 6, 144]` | 0.6087 | 0.5391 | 29.0 | 61.8 | 1a8ec16 | **Marginal pass** |

### What each experiment taught me

1. **ayesha-drop-rv (failed).** Worse on every metric (test R2 -0.026, test MAE +3.96). Dropping the random columns gave no benefit, so they stay. This agrees with Zarwa's `drop-rv` result, though her drop was larger because she started from a weaker model.
2. **ayesha-rolling (inconclusive).** Validation got slightly worse (R2 -0.005) while test got slightly better (R2 +0.012). Because the two disagree, I can't claim a real gain.
3. **ayesha-lags (marginal pass).** Test improved on all three metrics (R2 +0.017, MAE -1.80, RMSE -1.15). Validation MAE improved slightly (-0.05), while validation RMSE and R2 were slightly worse (+0.28 and -0.004), which is within noise. This is the best candidate from my branch.

### Conclusion

Proposed config: denser lags `[1, 2, 3, 6, 144]`, no rolling windows, no dropped columns. No experiment beat the baseline on validation, so this is a modest test-side improvement, not a decisive win.

**Limitations:** single seed (42), small splits (about 2,900 rows each), and all differences are small. Next step is to repeat with seeds 7 and 123, and to try lags together with rolling windows.

### How to reproduce

```bash
git checkout exp/ayesha-data-features
uv sync
uv run dvc pull
uv run dvc repro
```