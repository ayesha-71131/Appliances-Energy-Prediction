# Report: Appliances Energy Prediction

MLOps project that predicts appliance energy use (Wh) 10 minutes ahead and runs it like a real team
project: branches, reviewed pull requests, DVC-versioned data and models, CI and a tagged release.

> Items marked **TODO** do not exist yet and must be completed by the named owner before submission.

## 1. Project overview

**Team members and roles**

| Member | GitHub | Role |
|---|---|---|
| Ayesha Waheed | `ayesha-71131` | Data owner (DVC, data checks, dataset updates) |
| Zarwa | `zarwak` | Model owner (training pipeline, configs, experiments) |
| Mahnoor Aslam | `mahnraslam` | Platform owner (CI, pre-commit, environment, releases) |

**Dataset:** [Appliances Energy Prediction (UCI)](https://archive.ics.uci.edu/dataset/374/appliances+energy+prediction),
19,735 rows at 10-minute intervals from a low-energy house in Belgium (Candanedo, Feldheim &
Deramaix, 2017). The CSV (about 11.4 MB) is tracked with DVC, not Git.

**Starter code:** none was imported. The pipeline (`src/prepare.py`, `src/train.py`,
`src/evaluate.py`, `src/data_checks.py`, `src/eda.py`) was written by the team for this project.

**Task:** time-series regression. The split is chronological (70% train, 15% validation, 15% test),
never shuffled, and every feature at time T uses only information at or before T.

## 2. Reproducibility table (released model `model-v1.0`)

| Attribute | Value |
|---|---|
| Release commit SHA | `926223c73c63e326f4e71483cb46973ecb878b97` (tag `model-v1.0` on `main`) |
| Raw data `.dvc` hash | `data/raw/energydata_complete.csv.dvc`: md5 `69ef922b5fcafcd49097cfc09e07167e`, 11,979,363 bytes |
| Lock files | `dvc.lock` (pipeline hashes) and `uv.lock` (pinned Python environment) |
| Processed data (lock) | `data/processed`: md5 `4a5a2fca54472d52222fe272c997eb19.dir` |
| Model (lock) | `models/model.joblib`: md5 `c0bb121eea89f974c559f94145d4ed23` |
| Seed | `42` |
| Model | `hist_gradient_boosting` |
| `params.yaml` (train) | `loss: absolute_error`, `learning_rate: 0.1`, `max_iter: 300`, `max_depth: null`, `min_samples_leaf: 100`, `max_leaf_nodes: 31`, `l2_regularization: 0`, `early_stopping: false`, `max_features: 0.8` |
| `params.yaml` (prepare) | lags `[1,2,3,6,12,18,36,72,144]`, rolling windows `[3,6,12,36,72,144,288]`, environment lags `[1,3,6,12,144]` on `T_out`, `RH_out`, `Windspeed`, `Tdewpoint`, horizon 1, split 0.70 / 0.15 / 0.15 |
| Final metrics (validation) | R² 0.6017, MAE 22.53 Wh, RMSE 57.32 Wh |
| Final metrics (test) | R² 0.5815, MAE 22.67 Wh, RMSE 58.81 Wh |

Reproduce:
```bash
git clone https://github.com/ayesha-71131/Appliances-Energy-Prediction.git
cd Appliances-Energy-Prediction
git checkout model-v1.0
uv sync
uv run dvc pull
uv run dvc repro -f      # metrics must match the table above
```
Always run DVC through `uv run`, never a bare `dvc` (a global Python gives different library versions).

Reproduction evidence: a dry run by Zarwa on a fresh clone (all four stages forced to re-run,
metrics identical) is posted on [PR #17](https://github.com/ayesha-71131/Appliances-Energy-Prediction/pull/17#issuecomment-5979727093).
**TODO (Mahnoor or Ayesha):** post an independent reproduction (`metrics.json` and commands) on
[PR #18](https://github.com/ayesha-71131/Appliances-Energy-Prediction/pull/18).
`metrics.json` also contains the commit SHA of the run, so that one field differs on every re-run by design.

## 3. Experiments and model selection

`dvc exp show` comparison of all experiments. Validation R² / MAE are the selection numbers, test
numbers are only the final check. Experiments 1 to 13 start from the same gradient boosting
baseline (learning rate 0.05, 300 rounds, depth 6) unless stated; 14 to 16 start from the
`gb-leaf50` setup; 17 is the final feature-engineered model.

| # | Experiment | Owner | Change | Val R² | Test R² | Test MAE (Wh) |
|---|---|---|---|---|---|---|
| 1 | gb-leaf50 | Zarwa | lr 0.02, 600 rounds, `min_samples_leaf` 50 | 0.613 | 0.522 | 30.8 |
| 2 | gb-leaf100 | Zarwa | same, `min_samples_leaf` 100 | 0.606 | 0.546 | 28.6 |
| 3 | gb-leaf200 | Zarwa | same, `min_samples_leaf` 200 | 0.604 | 0.545 | 29.0 |
| 4 | gb-lr02 | Zarwa | learning rate 0.02, 600 rounds | 0.601 | 0.498 | 32.1 |
| 5 | gb-depth4 | Zarwa | lr 0.02/600, `max_depth` 4 | 0.596 | 0.463 | 41.4 |
| 6 | rolling | Zarwa | rolling windows `[6,36]` | 0.595 | 0.467 | 38.1 |
| 7 | gb-lr01 | Zarwa | learning rate 0.01, 1200 rounds | 0.595 | 0.470 | 35.2 |
| 8 | gb-depth8 | Zarwa | `max_depth` 8 | 0.579 | 0.352 | 46.6 |
| 9 | gb-baseline | Zarwa | gradient boosting, defaults | 0.578 | 0.359 | 46.3 |
| 10 | drop-rv | Zarwa | drop `rv1`, `rv2` | 0.568 | 0.191 | 60.1 |
| 11 | lags-more | Zarwa | lags `[1,2,6,36,144,1008]` | 0.560 | 0.453 | 39.3 |
| 12 | rf-baseline | Zarwa | random forest, defaults | 0.525 | 0.245 | 46.8 |
| 13 | rf-tuned | Zarwa | random forest 500 trees, depth 20 (abandoned) | 0.464 | -0.050 | 58.0 |
| 14 | drop rv1, rv2 | Ayesha | from `gb-leaf50` | 0.6105 | 0.4963 | n/a |
| 15 | rolling `[6,36]` | Ayesha | from `gb-leaf50` | 0.6072 | 0.5342 | n/a |
| 16 | lags `[1,2,3,6,144]` | Ayesha | from `gb-leaf50` | 0.6087 | 0.5391 | n/a |
| 17 | **Advanced features (final)** | Mahnoor | cyclic time encoding, rolling std and deltas, environment lags, `absolute_error` loss | 0.602 | **0.581** | **22.7** |

Experiments 14 to 16 are documented in `docs/experiments.md` (section 10); the full write-up of 1 to
13 is in the same file. **TODO (Mahnoor):** add two more documented experiments for the final feature
set so that every member has at least three.

### Why the winner was chosen
- The team goal was the lowest error in watt-hours, so the model was selected on **MAE** (the loss
  `absolute_error` optimises directly), with R² as a second check.
- The final model has the best MAE on both splits: validation 22.5 Wh and test 22.7 Wh, against
  25.2 Wh and 30.8 Wh for the best hyperparameter-only run (`gb-leaf50`).
- `gb-leaf50` has a slightly higher validation R² (0.613 against 0.602), but a much worse MAE,
  and its test R² (0.522) is lower than the final model's 0.581.
- Hyperparameter tuning gave the first big gain (test R² 0.36 to 0.50 with a smaller learning rate
  and larger leaves). Feature engineering and an MAE loss gave the second.
- Experiment 13 (a bigger random forest) was abandoned: it overfits this spiky data
  (test R² -0.05).

## 4. Collaboration evidence

| Requirement | Link |
|---|---|
| Data-update PR | **TODO (Ayesha):** open a `data/<change>` PR that modifies the dataset and show `git checkout` plus `dvc checkout` moving between versions. [PR #5](https://github.com/ayesha-71131/Appliances-Energy-Prediction/pull/5) only added the initial dataset. |
| Conflict-resolution PR | **TODO:** two members change the same line of `params.yaml` on separate branches; the second rebases and documents the resolution. |
| "Changes requested" review | [Review on PR #11](https://github.com/ayesha-71131/Appliances-Energy-Prediction/pull/11#pullrequestreview-5404486202): Ayesha flagged credentials committed to `.dvc/config` and blocked the merge. |
| Release PRs | [PR #17](https://github.com/ayesha-71131/Appliances-Energy-Prediction/pull/17) (`dev` to `staging`) and [PR #18](https://github.com/ayesha-71131/Appliances-Energy-Prediction/pull/18) (`staging` to `main`); tag `model-v1.0` |
| Abandoned `exp/` branch | [`exp/zarwa-rf-tuned`](https://github.com/ayesha-71131/Appliances-Energy-Prediction/tree/exp/zarwa-rf-tuned): never merged, because deeper random forests overfit and did worse than the untuned forest |

## 5. Quality assurance (screenshots)

**TODO (screenshots are not in the repo yet).** Save them as `docs/screenshots/<name>.png` and link
them here:
<img width="1314" height="772" alt="image" src="https://github.com/user-attachments/assets/5c89543f-816a-4008-b78e-f4ec7f550eac" />

<img width="1300" height="300" alt="image" src="https://github.com/user-attachments/assets/db6d6718-3f2d-4a9f-9614-fc2f0bb10dd5" />

<img width="1327" height="806" alt="image" src="https://github.com/user-attachments/assets/e169f5ca-73b3-4f72-b377-6288ba16cefc" />

<img width="1302" height="549" alt="image" src="https://github.com/user-attachments/assets/eb384a4b-de3f-4a5c-8ef5-51f56e220992" />


CI (`.github/workflows/ci.yml`) runs lint (ruff), unit tests (pytest), data checks and a smoke
train on every PR into `dev`, `staging` and `main`.

## 6. Retrospective

**What broke**
- A DagsHub access token was committed to `.dvc/config` (commit `0b55db8`) and removed in
  `42a93b9`. It stays in Git history, so it was rotated.
- The `.gitignore` rule `data/raw/*` made DVC skip the `data/raw/` folder, so `dvc exp run` deleted
  the raw CSV.
- Windows and Unix line endings produced different `dvc.lock` hashes on different machines.
- Early experiments ran with the global Python instead of the `uv` environment, DVC reused cached
  results, and experiments chained onto each other, so the first numbers were wrong.
- `dvc.lock` went stale and the processed data and model were never pushed, so `dvc pull` failed
  on `dev` until PR #16.
- Several PRs merged without a review, and the test file `test_prepare.py` was lost in a CI merge
  (restored in PR #14).

**What we added to `CONTRIBUTING.md` because of it:** a "Lessons learned" section (see that file):
never commit credentials, run DVC through `uv run`, reset between experiments, `dvc push` before
`git push`, keep `.gitattributes` for line endings, and every PR needs a reviewer who runs it.

## 7. Individual contributions

**Ayesha Waheed (Data owner).** Added the pre-commit configuration (ruff, nbstripout,
large-file check, secret scanner) in PR #3, built the EDA notebook with its paired script and a
tested helper in `src/eda.py` (PR #6), restored the lost prepare tests (PR #14), and ran three
data and feature experiments documented in `docs/experiments.md` (PR #13). She reviewed PR #1
(approved), PR #12, and requested changes on PR #11 after spotting the committed credentials.

**Zarwa (Model owner).** Built the training and evaluation stages (`src/train.py`, `src/evaluate.py`,
the `train` and `evaluate` stages in `dvc.yaml`, `configs/params.yaml`) and the unit tests, with
every setting and the seed in `params.yaml` and the commit SHA logged in `metrics.json` (PR #7). Ran
13 experiments with `dvc exp run`, promoted the `gb-leaf50` winner (PR #8 and #9), and kept the
abandoned `exp/zarwa-rf-tuned` branch. Found and fixed the `.gitignore` rule that hid the raw data
from DVC, added `.gitattributes` for stable line endings, and refreshed `dvc.lock` and pushed the
missing data and model to the remote (PR #16). Opened the release PRs #17 and #18 and posted a
fresh-clone reproducibility dry run. Wrote `docs/phase-6-7-model-tuning.md` and
`docs/experiments.md` and this report's corrections.

**Mahnoor Aslam (Platform owner).** Set up the repository baseline and layout (PR #1), versioned the
raw dataset with DVC and the DagsHub remote (PR #5), built the GitHub Actions CI with lint, tests,
data checks and a smoke train (PR #11 and #15), and developed the advanced time-series feature set and
the optimised gradient boosting model that became the released model (cyclic time, rolling
statistics, environment lags, `absolute_error` loss; PR #12, which landed on `dev` through the CI
PRs). She merged the release PR #18 and created the `model-v1.0` tag.
