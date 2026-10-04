# Report: Appliances Energy Prediction

This report documents the development, experimentation, and results of the Appliances Energy Prediction project.

## 1. Project Overview

- **Team Members & Roles**:
    - **Ayesha Waheed**: Data Owner (DVC, data checks, dataset updates)
    - **Zarwa**: Model Owner (training pipeline, configs, experiments)
    - **Mahnoor Aslam**: Platform Owner (CI, pre-commit, environment, releases)
- **Dataset Source**:  https://archive.ics.uci.edu/dataset/374/appliances+energy+prediction

## 2. Reproducibility Table (Released Model)

The final model was promoted to `main` and tagged as `model-v1.0`.

| Attribute | Value |
| :--- | :--- |
| **Commit SHA** | `32e3c42` |
| **Params** | `lr=0.1, max_iter=300, min_samples_leaf=100, loss='absolute_error'` | 
| **Lock File** | `uv.lock` (pinned versions) |
| **Seed** | `42` |
| **Final Metrics** | Test MAE: **22.67**, Test $R^2$: **0.581** |

## 3. Experiments & Model Selection

### Experiment Comparison
We conducted several rounds of tuning and feature engineering. The primary goal was to reduce the Test MAE while maintaining a high Validation $R^2$.

| Experiment | Key Change | Val $R^2$ | Test $R^2$ | Test MAE (Wh) | Outcome |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `gb-baseline` | Gradient Boosting Defaults | 0.578 | 0.359 | 46.3 | Baseline |
| `gb-leaf50` | lr 0.02, leaf=50 | 0.613 | 0.522 | 30.8 | Strong Improvement |
| `m3-regularized`| lr 0.02, leaf=100 | 0.606 | 0.546 | 28.6 | Best Tuning |
| **Adv. Features**| Cyclic Time, Rolling Std, Deltas | — | **0.581** | **22.67** | **Winner** |

### Why the Winner was Chosen
While hyperparameter tuning (e.g., `gb-leaf50`) provided initial gains, the **Advanced Feature Engineering** approach provided a breakthrough. By implementing cyclic time encoding, volatility metrics (rolling std), and temperature deltas, we reduced the Test MAE by ~21% compared to the best-tuned baseline. This proved that domain-specific features were more impactful than model parameters.

## 4. Collaboration Evidence

- **Data Update PR**:  https://github.com/ayesha-71131/Appliances-Energy-Prediction/pull/5
- **Conflict Resolution PR**:  
- **Changes Requested Review**: [Linkhttps://github.com/ayesha-71131/Appliances-Energy-Prediction/pull/4 to PR Review]
- **Release PRs**: https://github.com/ayesha-71131/Appliances-Energy-Prediction/pull/15
- **Abandoned Experiment Branch**: [`exp/zarwa-rf-tuned`](https://github.com/ayesha-71131/Appliances-Energy-Prediction/tree/exp/zarwa-rf-tuned) - Abandoned because deep Random Forests overfit the spiky energy data, performing worse than the baseline.

## 5. Quality Assurance (Screenshots)

<img width="1314" height="772" alt="image" src="https://github.com/user-attachments/assets/5c89543f-816a-4008-b78e-f4ec7f550eac" />
<img width="1300" height="300" alt="image" src="https://github.com/user-attachments/assets/db6d6718-3f2d-4a9f-9614-fc2f0bb10dd5" />
<img width="1327" height="806" alt="image" src="https://github.com/user-attachments/assets/e169f5ca-73b3-4f72-b377-6288ba16cefc" />
<img width="1302" height="549" alt="image" src="https://github.com/user-attachments/assets/eb384a4b-de3f-4a5c-8ef5-51f56e220992" />





## 6. Retrospective

**What broke?**
- Initial DVC configurations were overwritten by `.gitignore` rules.
- Line ending differences between Windows and Unix caused `dvc.lock` hash mismatches.
- Early experiments were run using global Python instead of the `uv` environment, leading to inconsistent results.

**Improvements to `CONTRIBUTING.md`**:
- Added a strict requirement to run `dvc push` before `git push`.
- Formalized the Review Checklist to include checks for data leakage and hardcoded paths.
- Defined a specific branching flow (`dev` $\rightarrow$ `staging` $\rightarrow$ `main`) to ensure reproduction before release.

## 7. Individual Contributions

- **Ayesha Waheed**: Set up DVC tracking, managed raw data ingestion, implemented the data validation pipeline, and handled dataset cleaning/updates.
- **Zarwa**: Developed the training and evaluation scripts, conducted extensive hyperparameter tuning using `dvc exp`, and implemented the winning advanced feature engineering.
- **Mahnoor Aslam**: Configured the project scaffold, implemented pre-commit hooks for linting and secret scanning, set up the GitHub Actions CI pipeline, and managed the release tagging process.
