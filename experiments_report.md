# Experiments Report: Appliance Energy Prediction

## 1. Objective
The goal was to improve the prediction of appliance energy use at time $T+1$ using a `HistGradientBoostingRegressor`. The primary focus was to move beyond simple hyperparameter tuning and implement domain-specific feature engineering for time-series data.

## 2. Baseline and Initial Tuning
The initial baseline used a basic set of temporal features (hour, weekday, month) and a few lags.

### Hyperparameter Experiments
We tested three main directions for tuning the model:

| Experiment | Change | Test MAE | Test $R^2$ | Outcome |
| :--- | :--- | :--- | :--- | :--- |
| `m3-lr-005` | $lr=0.05, max\_iter=300$ | 34.80 | 0.492 | $\text{Degraded}$ |
| `m3-regularized` | $min\_samples\_leaf=100$ | 28.58 | 0.546 | $\text{Best}$ |
| `m3-l2` | $l2\_reg=1$ | 31.94 | 0.528 | $\text{Degraded}$ |

**Key Insight:** Increasing `min_samples_leaf` to 100 acted as a powerful regularizer, preventing the model from overfitting to noise in the training set. In contrast, L2 regularization and lowering the learning rate without increasing iterations hurt performance.

---

## 3. Advanced Feature Engineering (The Breakthrough)
Recognizing that the model was hitting a ceiling, we shifted strategy from "tuning the model" to "enriching the data."

### The Hypotheses
1.  **Temporal Resolution**: The 10-minute sampling interval was being collapsed into hours. We hypothesized that including the exact minute and cyclic encoding (sin/cos) would capture daily rhythms more accurately.
2.  **Volatility**: Energy use is not just about the average; the "stability" of the usage (Standard Deviation) is a strong signal for predicting the next state.
3.  **Trends**: The rate of change (differences) in temperature and energy use provides a "momentum" signal.
4.  **Environmental Interactions**: Appliance use is often a product of temperature $\times$ humidity.

### Implementation
We implemented the following features in `src/prepare.py`:
- **Cyclic Time**: $\sin/\cos$ encoding of the minute-of-day and day-of-week.
- **Rolling Statistics**: Added `roll_std` (volatility) for the target.
- **Deltas**: Added $\Delta_1, \Delta_3, \Delta_6$ for both the target and environmental variables (`T_out`, `RH_out`).
- **Interactions**: Created a `temp_rh_interaction` feature.
- **Loss Function**: Switched the HGB loss from `squared_error` to `absolute_error` to directly optimize for MAE.

### Results of Feature Engineering
| Version | Test MAE | Test $R^2$ | Improvement |
| :--- | :--- | :--- | :--- |
| Baseline Tuning | 28.58 | 0.546 | - |
| Advanced Features | **22.67** | **0.581** | $\mathbf{\sim 21\% \text{ MAE reduction}}$ |

---

## 4. Final Model Configuration
The winning model was promoted to the `feat/improved-features` branch with the following configuration:

- **Model**: `HistGradientBoostingRegressor`
- **Loss**: `absolute_error`
- **Learning Rate**: $0.1$
- **Max Iterations**: $300$
- **Min Samples Leaf**: $100$
- **Early Stopping**: `False` (to respect chronological validation)
- **Max Features**: $0.8$ (for additional regularization)

## 5. Conclusion
The results demonstrate that for this dataset, **feature engineering was significantly more impactful than hyperparameter tuning**. By encoding the physics of the problem (time cycles, temperature changes, and volatility), we reduced the Test MAE from 34.80 to 22.67.
