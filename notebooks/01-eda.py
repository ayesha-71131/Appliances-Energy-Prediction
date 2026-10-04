# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.5
#   kernelspec:
#     display_name: appliances-energy-prediction (3.12.10)
#     language: python
#     name: python3
# ---

# %% [markdown]
# ## EDA

# %%
import sys
from pathlib import Path

PROJECT_ROOT = Path.cwd().parent
sys.path.insert(0, str(PROJECT_ROOT))

import matplotlib.pyplot as plt

# %%
import pandas as pd

from src.eda import summarize_numeric

DATA_PATH = Path("../data/raw/energydata_complete.csv")

df = pd.read_csv(DATA_PATH)

print(f"Shape: {df.shape}")
df.head()

# %%
df.info()

# %%
PROCESSED_PATH = Path("../data/processed")

train = pd.read_csv(PROCESSED_PATH / "train.csv")
val = pd.read_csv(PROCESSED_PATH / "val.csv")
test = pd.read_csv(PROCESSED_PATH / "test.csv")

print("Train:", train.shape)
print("Val:  ", val.shape)
print("Test: ", test.shape)

train.head()

# %%
for name, data in [("Train", train), ("Validation", val), ("Test", test)]:
    print(f"\n{name}")
    print(f"  Missing values: {data.isna().sum().sum()}")
    print(f"  Duplicate rows: {data.duplicated().sum()}")
    print(f"  Date range: {data['date'].min()} → {data['date'].max()}")

print("Train date dtype:", train["date"].dtype)
print("Validation date dtype:", val["date"].dtype)
print("Test date dtype:", test["date"].dtype)

# %%
# converting date column to datetime type
for data in [train, val, test]:
    data["date"] = pd.to_datetime(data["date"])

# %%
# 1. What are we predicting?
# Question: What does future appliance energy consumption (target) look like?

train["target"].describe()

# %%
PROJECT_ROOT = Path.cwd().parent
sys.path.insert(0, str(PROJECT_ROOT))


target_summary = summarize_numeric(train, "target")

print("Target summary:")
for statistic, value in target_summary.items():
    print(f"{statistic:>8}: {value:.2f}")

# %%
# Are these high values isolated/extreme observations, or are there recurring periods of high appliance consumption?

# Visual: target distribution
plt.figure(figsize=(8, 5))
plt.hist(train["target"], bins=50)

plt.xlabel("Future appliance energy consumption (Wh)")
plt.ylabel("Frequency")
plt.title("Distribution of Target")

plt.show()


# Text version: target ranges and their frequencies
bins = [0, 50, 100, 200, 300, 500, 700, 900, float("inf")]
labels = [
    "0–49",
    "50–99",
    "100–199",
    "200–299",
    "300–499",
    "500–699",
    "700–899",
    "900+",
]

target_ranges = pd.cut(train["target"], bins=bins, labels=labels, right=False)

print("Target frequency by range:")
print(target_ranges.value_counts().sort_index())

# %%
# Q2 — Does appliance consumption have a systematic time-of-day pattern?

# Average target by hour
hourly_target = (
    train.groupby("hour")["target"].agg(["mean", "median", "count"]).round(2)
)

# Visual
plt.figure(figsize=(9, 5))
plt.plot(hourly_target.index, hourly_target["mean"], marker="o")

plt.xlabel("Hour of day")
plt.ylabel("Average target (Wh)")
plt.title("Average Future Appliance Consumption by Hour")
plt.xticks(range(24))
plt.grid(True, alpha=0.3)

plt.show()


# Text version
print("Average target by hour:")
print(hourly_target)

# %%
# Q3 — Is this time-of-day pattern consistent across weekdays, or does consumption differ between weekdays and weekends?

# Average target by weekday
weekday_target = (
    train.groupby("weekday")["target"].agg(["mean", "median", "count"]).round(2)
)

# Visual
plt.figure(figsize=(8, 5))
plt.bar(weekday_target.index, weekday_target["mean"])

plt.xlabel("Weekday (0 = Monday, 6 = Sunday)")
plt.ylabel("Average target (Wh)")
plt.title("Average Future Appliance Consumption by Weekday")
plt.xticks(range(7), ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
plt.grid(axis="y", alpha=0.3)

plt.show()


# Text version
print("Average target by weekday:")
print(weekday_target)

# %%
# Q4 — Does the weekday pattern remain after accounting for the hour of day?

# Average target by weekday and hour
weekday_hour = train.groupby(["weekday", "hour"])["target"].mean().unstack().round(2)

# Visual
plt.figure(figsize=(14, 5))
plt.imshow(weekday_hour, aspect="auto")

plt.colorbar(label="Average target (Wh)")
plt.xlabel("Hour of day")
plt.ylabel("Weekday")
plt.title("Average Future Appliance Consumption by Weekday and Hour")

plt.xticks(range(24), range(24))
plt.yticks(range(7), ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])

plt.show()


# Text version
print("Average target by weekday and hour:")
print(weekday_hour)

# %%
# Hour appears to capture a strong recurring daily pattern, while weekday adds some variation but doesn't appear to explain the main pattern by itself.
# Q5 — Is there a broader time/seasonal pattern across the months?

# Average target by month
monthly_target = (
    train.groupby("month")["target"].agg(["mean", "median", "count"]).round(2)
)

# Visual
plt.figure(figsize=(7, 5))
plt.bar(monthly_target.index.astype(str), monthly_target["mean"])

plt.xlabel("Month")
plt.ylabel("Average target (Wh)")
plt.title("Average Future Appliance Consumption by Month")
plt.grid(axis="y", alpha=0.3)

plt.show()


# Text version
print("Average target by month:")
print(monthly_target)

# %%
# Does knowing recent appliance consumption help predict consumption 10 minutes into the future?
lag_cols = ["Appliances_lag_1", "Appliances_lag_6", "Appliances_lag_144", "target"]

lag_corr = train[lag_cols].corr()["target"].drop("target").sort_values(ascending=False)

print("Correlation with future appliance consumption (target):")
print(lag_corr.round(3))

# %%
plt.figure(figsize=(8, 5))

plt.scatter(train["Appliances_lag_1"], train["target"], alpha=0.2)

plt.xlabel("Appliance consumption 10 minutes ago (Wh)")
plt.ylabel("Future appliance consumption (Wh)")
plt.title("Previous 10-Minute Consumption vs Future Consumption")
plt.grid(True, alpha=0.3)

plt.show()

print("Numeric summary:")
print(train[["Appliances_lag_1", "target"]].describe().round(2))

# %%
lag_corr = (
    train[
        [
            "Appliances_lag_1",
            "Appliances_lag_6",
            "Appliances_lag_144",
            "target",
        ]
    ]
    .corr()["target"]
    .drop("target")
    .sort_values(ascending=False)
)

plt.figure(figsize=(7, 4))
plt.bar(["10 min ago", "1 hour ago", "24 hours ago"], lag_corr.values)

plt.xlabel("Previous consumption")
plt.ylabel("Correlation with target")
plt.title("Relationship Between Previous and Future Appliance Consumption")
plt.ylim(0, 0.65)
plt.grid(axis="y", alpha=0.3)

plt.show()

print("Lag correlation with target:")
for lag, corr in lag_corr.items():
    print(f"{lag}: {corr:.3f}")

# %%
# Which variables show the strongest linear relationship with future appliance consumption?

# Q6: Which sensor/environment variables are most related to future consumption?

# Exclude identifiers/time columns and the target itself
exclude_cols = ["date", "hour", "weekday", "month", "target"]

feature_cols = [col for col in train.columns if col not in exclude_cols]

correlations = (
    train[feature_cols + ["target"]].corr()["target"].drop("target").sort_values()
)

# Visual
plt.figure(figsize=(9, 8))
plt.barh(correlations.index, correlations.values)

plt.xlabel("Correlation with target")
plt.ylabel("Feature")
plt.title("Feature Correlation with Future Appliance Consumption")
plt.grid(axis="x", alpha=0.3)

plt.show()

# Text version of the visual
print("Features ranked by correlation with target:")
print(correlations.round(3))

print("\nStrongest positive relationships:")
print(correlations.tail(10).sort_values(ascending=False).round(3))

print("\nStrongest negative relationships:")
print(correlations.head(10).round(3))

# %%
# Q7: What is the relationship between rv1, rv2, and the target?

rv_summary = train[["rv1", "rv2", "target"]].describe().round(4)

rv_corr = train[["rv1", "rv2", "target"]].corr().round(3)

# Check how often rv1 and rv2 are exactly equal
equal_fraction = (train["rv1"] == train["rv2"]).mean()

print("Summary statistics:")
print(rv_summary)

print("\nCorrelation matrix:")
print(rv_corr)

print(f"\nFraction of rows where rv1 == rv2: {equal_fraction:.3f}")
print(f"Number of rows where rv1 != rv2: {(train['rv1'] != train['rv2']).sum()}")

# %% [markdown]
# Findings: rv1 and rv2 contain duplicate information, and neither shows a meaningful linear relationship with the target.

# %%
# Q8: How does current appliance consumption relate to future consumption?
# When current appliance consumption is low/high, does future consumption tend to be low/high as well, and how consistently?

plt.figure(figsize=(8, 5))

plt.scatter(train["Appliances"], train["target"], alpha=0.2)

plt.xlabel("Current appliance consumption (Wh)")
plt.ylabel("Future appliance consumption (Wh)")
plt.title("Current vs Future Appliance Consumption")
plt.grid(True, alpha=0.3)

plt.show()


# Text version: average future consumption at different
# levels of current consumption
bins = [0, 50, 100, 200, 300, 500, 700, 900, float("inf")]
labels = [
    "0–49",
    "50–99",
    "100–199",
    "200–299",
    "300–499",
    "500–699",
    "700–899",
    "900+",
]

current_bins = pd.cut(train["Appliances"], bins=bins, labels=labels, right=False)

current_vs_target = (
    train.assign(current_range=current_bins)
    .groupby("current_range", observed=False)["target"]
    .agg(["mean", "median", "count"])
    .round(2)
)

print("Future target by current appliance-consumption range:")
print(current_vs_target)

# %% [markdown]
# findings: Current appliance consumption is strongly informative about the 10-minute-ahead target (correlation = 0.760), with higher current-consumption ranges generally corresponding to higher future consumption.

# %%
# Q9: Are target distributions reasonably consistent across
# train, validation, and test?

split_summary = pd.DataFrame(
    {
        "Train": train["target"].describe(),
        "Validation": val["target"].describe(),
        "Test": test["target"].describe(),
    }
).round(2)

print("Target distribution across chronological splits:")
print(split_summary)

print("\nTarget mean by split:")
print(
    pd.DataFrame(
        {
            "Train": [train["target"].mean()],
            "Validation": [val["target"].mean()],
            "Test": [test["target"].mean()],
        }
    ).round(2)
)

# %% [markdown]
# finding
#
# The chronological splits are reasonably similar:
#
# Train mean: 98.96 Wh
# Validation mean: 92.15 Wh
# Test mean: 97.03 Wh
# All three have median 60 Wh
# The 25th percentile is 50 Wh in all three.
# Train has some larger peaks (1080 Wh) than validation (870) and test (850), but the overall distributions aren't radically different.
#
# So there isn't an obvious major distribution shift that would immediately make the temporal split problematic.

# %%
# Q10: Are the lag relationships stable across train, validation, and test?

lag_cols = ["Appliances_lag_1", "Appliances_lag_6", "Appliances_lag_144"]

splits = {"Train": train, "Validation": val, "Test": test}

for name, data in splits.items():
    correlations = data[lag_cols + ["target"]].corr()["target"].drop("target")

    print(f"\n{name}")
    print(correlations.round(3))

# %% [markdown]
# # EDA Findings — Appliances Energy Prediction
#
# ## 1. Objective
#
# The exploratory data analysis (EDA) was performed on the prepared Appliances Energy Prediction dataset to understand:
#
# 1. The distribution and behavior of future appliance energy consumption.
# 2. Temporal patterns in appliance energy usage.
# 3. The relationship between historical appliance consumption and future consumption.
# 4. Relationships between environmental/sensor variables and future consumption.
# 5. Whether `rv1` and `rv2` provide useful information.
# 6. Whether the observed patterns remain reasonably consistent across train, validation, and test splits.
#
# The EDA is descriptive and does not modify the prepared datasets or select a final model/feature set.
#
# ---
#
# ## 2. Dataset and Prediction Setup
#
# The original dataset contains appliance energy measurements at **10-minute intervals**.
#
# The preparation pipeline creates a one-step-ahead prediction target:
#
# * Current time: `T`
# * Prediction target: appliance energy at `T + 1`
# * Forecast horizon: **10 minutes**
# * Target column: `target`
# * Original current consumption column: `Appliances`
#
# The prepared dataset contains:
#
# * **13,713 rows** in training
# * **2,938 rows** in validation
# * **2,939 rows** in test
# * **36 columns** after feature preparation
#
# The chronological split is:
#
# | Split      | Start            | End              |
# | ---------- | ---------------- | ---------------- |
# | Train      | 2016-01-12 17:00 | 2016-04-16 22:20 |
# | Validation | 2016-04-16 22:30 | 2016-05-07 08:00 |
# | Test       | 2016-05-07 08:10 | 2016-05-27 17:50 |
#
# No missing values or duplicate rows were found in the prepared splits.
#
# ---
#
# # 3. Scenario 1 — Target Behavior
#
# ### Question
#
# **What does future appliance energy consumption look like?**
#
# The training target has the following summary:
#
# | Statistic          |     Value |
# | ------------------ | --------: |
# | Count              |    13,713 |
# | Mean               |  98.96 Wh |
# | Median             |  60.00 Wh |
# | Standard deviation | 107.11 Wh |
# | Minimum            |     10 Wh |
# | Maximum            |  1,080 Wh |
# | Skewness           |      3.26 |
#
# ### Findings
#
# * The mean (**98.96 Wh**) is substantially higher than the median (**60 Wh**).
# * The target has strong **right skew**, with a skewness of **3.26**.
# * Most observations have relatively low appliance consumption.
# * A smaller number of observations have substantially higher consumption.
#
# Target distribution by range:
#
# | Target range | Count |
# | ------------ | ----: |
# | 0–49 Wh      | 2,644 |
# | 50–99 Wh     | 7,412 |
# | 100–199 Wh   | 2,188 |
# | 200–299 Wh   |   548 |
# | 300–499 Wh   |   692 |
# | 500–699 Wh   |   171 |
# | 700–899 Wh   |    54 |
# | 900+ Wh      |     4 |
#
# Approximately **73.4%** of training targets are below 100 Wh, while approximately **1.7%** are 500 Wh or higher.
#
# ### Interpretation
#
# Future appliance consumption is highly concentrated at lower values but occasionally reaches much larger values. The high values should not automatically be treated as errors or removed as outliers without additional evidence.
#
# ---
#
# # 4. Scenario 2 — Temporal Behavior
#
# ## 4.1 Hourly Pattern
#
# ### Question
#
# **Does appliance energy consumption vary systematically by time of day?**
#
# Mean target consumption by hour:
#
# | Hour | Mean Wh |
# | ---: | ------: |
# |   00 |   50.56 |
# |   01 |   48.89 |
# |   02 |   47.04 |
# |   03 |   47.16 |
# |   04 |   47.95 |
# |   05 |   48.00 |
# |   06 |   56.70 |
# |   07 |   74.51 |
# |   08 |  111.75 |
# |   09 |  111.39 |
# |   10 |  132.91 |
# |   11 |  133.44 |
# |   12 |  130.44 |
# |   13 |  129.79 |
# |   14 |  109.96 |
# |   15 |  112.49 |
# |   16 |  121.49 |
# |   17 |  149.20 |
# |   18 |  213.51 |
# |   19 |  141.89 |
# |   20 |  132.01 |
# |   21 |  100.12 |
# |   22 |   65.60 |
# |   23 |   55.84 |
#
# ### Findings
#
# * Consumption is lowest during the early morning hours.
# * Consumption begins increasing around **07:00–08:00**.
# * Consumption remains relatively high throughout much of the daytime.
# * The strongest peak occurs around **18:00**, with mean consumption of approximately **213.5 Wh**.
# * Consumption decreases again during the late evening.
#
# ### Interpretation
#
# There is a pronounced **daily/diurnal pattern** in appliance energy consumption. The hour of day appears to contain useful predictive information.
#
# ---
#
# ## 4.2 Weekday Pattern
#
# ### Question
#
# **Does appliance consumption vary substantially by day of the week?**
#
# | Weekday   | Mean Wh | Median Wh |
# | --------- | ------: | --------: |
# | Monday    |  123.93 |        60 |
# | Tuesday   |   92.71 |        60 |
# | Wednesday |   94.52 |        70 |
# | Thursday  |   90.20 |        60 |
# | Friday    |   96.25 |        50 |
# | Saturday  |  101.24 |        60 |
# | Sunday    |   95.06 |        60 |
#
# ### Findings
#
# * Monday has the highest mean consumption at approximately **123.9 Wh**.
# * The other weekdays have means mostly between approximately **90–101 Wh**.
# * Median consumption is relatively similar across weekdays.
#
# ### Interpretation
#
# There is some weekday variation, but it appears weaker than the hourly pattern. Weekday effects may also interact with time of day rather than acting independently.
#
# ---
#
# ## 4.3 Weekday × Hour
#
# ### Question
#
# **Does the daily pattern remain visible across different weekdays?**
#
# The weekday-hour analysis shows that the **18:00 peak appears consistently across weekdays**.
#
# Examples of higher evening values occur across the week, with Monday showing particularly high afternoon/evening consumption.
#
# ### Interpretation
#
# The daily cycle is not limited to one particular weekday. This supports the usefulness of temporal features such as `hour`, while also suggesting that interactions between weekday and hour could be explored during later modeling.
#
# ---
#
# ## 4.4 Month
#
# ### Question
#
# **Is there a strong month-level pattern in this dataset?**
#
# |    Month | Mean Wh | Median Wh |
# | -------: | ------: | --------: |
# |  January |   96.65 |        50 |
# | February |  100.95 |        60 |
# |    March |   96.95 |        60 |
# |    April |  102.03 |        60 |
#
# ### Findings
#
# Monthly mean consumption remains relatively close, approximately **97–102 Wh**.
#
# ### Interpretation
#
# There is no strong month-level difference visible in this dataset. However, the dataset only covers approximately January through May, so it does not provide enough coverage to evaluate full annual seasonality.
#
# ---
#
# # 5. Scenario 3 — Historical/Lag Behavior
#
# ## 5.1 Lag Correlations
#
# ### Question
#
# **How strongly is future consumption related to previous appliance consumption?**
#
# Correlation between lagged appliance consumption and the future target:
#
# | Feature              | Correlation with Target |
# | -------------------- | ----------------------: |
# | `Appliances_lag_1`   |                   0.548 |
# | `Appliances_lag_6`   |                   0.295 |
# | `Appliances_lag_144` |                   0.201 |
#
# The lags represent:
#
# * `lag_1` → previous 10-minute observation
# * `lag_6` → previous 1 hour
# * `lag_144` → previous 24 hours
#
# ### Findings
#
# * The previous 10-minute value has the strongest relationship with future consumption.
# * The previous-hour value also has a noticeable positive relationship.
# * The previous-day value has a weaker but still positive relationship.
#
# ### Interpretation
#
# Recent historical consumption contains useful information about future appliance consumption. The strength of `lag_1` suggests that appliance usage has substantial short-term persistence.
#
# The 24-hour lag is weaker but still non-zero, which is consistent with the temporal patterns observed earlier.
#
# ---
#
# ## 5.2 Current Consumption vs Future Consumption
#
# ### Question
#
# **Does higher current appliance consumption generally correspond to higher future consumption?**
#
# | Current `Appliances` range | Future target mean |
# | -------------------------- | -----------------: |
# | 0–49                       |           43.49 Wh |
# | 50–99                      |           67.09 Wh |
# | 100–199                    |          137.54 Wh |
# | 200–299                    |          240.18 Wh |
# | 300–499                    |          295.98 Wh |
# | 500–699                    |          431.87 Wh |
# | 700–899                    |          566.11 Wh |
# | 900+                       |          752.50 Wh |
#
# ### Finding
#
# Higher current consumption generally corresponds to higher future consumption.
#
# ### Interpretation
#
# This relationship is not perfectly proportional, but it provides further evidence that recent appliance consumption is informative for predicting the next 10-minute value.
#
# ---
#
# # 6. Scenario 4 — Environmental and Sensor Variables
#
# ### Question
#
# **Which environmental or sensor variables have the strongest individual linear relationships with future appliance consumption?**
#
# The strongest observed correlations were:
#
# | Feature       | Correlation with Target |
# | ------------- | ----------------------: |
# | `RH_out`      |                  -0.147 |
# | `RH_8`        |                  -0.114 |
# | `RH_6`        |                  -0.085 |
# | `RH_7`        |                  -0.072 |
# | `RH_9`        |                  -0.060 |
# | `RH_2`        |                  -0.053 |
# | `Press_mm_hg` |                  -0.037 |
# | `Tdewpoint`   |                   0.012 |
# | `T5`          |                   0.029 |
# | `T7`          |                   0.054 |
# | `Windspeed`   |                   0.068 |
# | `T4`          |                   0.071 |
# | `T8`          |                   0.072 |
# | `T1`          |                   0.075 |
# | `RH_1`        |                   0.080 |
# | `T_out`       |                   0.094 |
# | `T6`          |                   0.110 |
# | `T3`          |                   0.116 |
# | `T2`          |                   0.142 |
# | `lights`      |                   0.213 |
#
# ### Findings
#
# * Most individual sensor variables have relatively weak linear correlations with the future target.
# * `lights` has the strongest positive correlation among the non-lag features at approximately **0.213**.
# * `T2`, `T3`, and `T6` show smaller positive relationships.
# * Several humidity variables show negative relationships, particularly `RH_out` at approximately **-0.147**.
# * The environmental variables individually do not show correlations as strong as the lagged appliance-consumption features.
#
# ### Interpretation
#
# The sensor and environmental variables may still provide useful information when combined with temporal and lag features. However, individual Pearson correlation alone does not determine whether a feature is useful for a predictive model because relationships may be nonlinear or conditional on other variables.
#
# ---
#
# # 7. Scenario 5 — `rv1` and `rv2`
#
# ### Question
#
# **Are `rv1` and `rv2` informative or redundant?**
#
# Summary:
#
# | Statistic |   `rv1` |   `rv2` |
# | --------- | ------: | ------: |
# | Count     |  13,713 |  13,713 |
# | Mean      |   24.98 |   24.98 |
# | Std       |   14.55 |   14.55 |
# | Min       |  0.0053 |  0.0053 |
# | Median    |   24.84 |   24.84 |
# | Max       | 49.9965 | 49.9965 |
#
# Correlation:
#
# | Relationship    | Correlation |
# | --------------- | ----------: |
# | `rv1` vs `rv2`  |       1.000 |
# | `rv1` vs target |      -0.013 |
# | `rv2` vs target |      -0.013 |
#
# Additionally:
#
# * `rv1 == rv2` for **100% of the training rows**.
# * The number of differing rows between the two columns is **0**.
# * Both variables have almost zero linear correlation with the target.
#
# ### Interpretation
#
# `rv1` and `rv2` are descriptively redundant in the prepared training data and provide almost no individual linear relationship with the target.
#
# However, this EDA does not automatically remove them from the dataset. Their removal can instead be evaluated later as a controlled modeling/ablation experiment.
#
# ---
#
# # 8. Scenario 6 — Train/Validation/Test Consistency
#
# ### Question
#
# **Are the target distributions reasonably consistent across the chronological splits?**
#
# | Statistic       |  Train | Validation |  Test |
# | --------------- | -----: | ---------: | ----: |
# | Count           | 13,713 |      2,938 | 2,939 |
# | Mean            |  98.96 |      92.15 | 97.03 |
# | Std             | 107.11 |      90.22 | 90.99 |
# | Min             |     10 |         20 |    20 |
# | Median          |     60 |         60 |    60 |
# | 75th percentile |    100 |         90 |   100 |
# | Max             |  1,080 |        870 |   850 |
#
# ### Findings
#
# * The three splits have similar median target values.
# * Train has somewhat higher variability and larger maximum values.
# * Validation and test have lower maximum values than train.
# * The overall target behavior remains broadly similar across the chronological periods.
#
# ### Interpretation
#
# There is no obvious dramatic distribution shift in the target across the chronological splits, although the training period contains some larger peaks.
#
# The test set remains reserved for final model evaluation and should not be used for model selection or tuning.
#
# ---
#
# # 9. Lag Stability Across Splits
#
# ### Question
#
# **Do the relationships between historical consumption and future consumption remain reasonably stable over time?**
#
# | Split      | Lag 1 | Lag 6 | Lag 144 |
# | ---------- | ----: | ----: | ------: |
# | Train      | 0.548 | 0.295 |   0.201 |
# | Validation | 0.482 | 0.240 |   0.251 |
# | Test       | 0.515 | 0.327 |   0.225 |
#
# ### Findings
#
# * `Appliances_lag_1` is the strongest of the three lags in all splits.
# * `Appliances_lag_6` remains moderately positively correlated with the target.
# * `Appliances_lag_144` remains positively correlated, although weaker than the shorter lags.
# * The general ordering and direction of the relationships remain reasonably stable across the chronological periods.
#
# ### Interpretation
#
# The usefulness of historical appliance consumption is not restricted to the training period. The lag relationships remain present in validation and test periods.
#
# This supports investigating lag features in later modeling experiments, but correlation alone does not establish the amount of predictive improvement a model will achieve.
#
# ---
#
# # 10. Overall EDA Findings
#
# The EDA provides the following main observations:
#
# 1. **Future appliance consumption is strongly right-skewed.**
#    Most target values are relatively low, while a smaller number of observations have substantially higher consumption.
#
# 2. **There is a pronounced daily pattern.**
#    Appliance consumption varies considerably by hour, with a notable peak around 18:00.
#
# 3. **Weekday effects exist but appear weaker than hourly effects.**
#    The hourly pattern is visible across weekdays.
#
# 4. **Recent appliance consumption is strongly related to future consumption.**
#    The previous 10-minute value (`Appliances_lag_1`) has the strongest lag correlation.
#
# 5. **Longer historical context also contains information.**
#    Both one-hour and 24-hour lags have positive relationships with future consumption.
#
# 6. **Sensor/environmental variables generally have weaker individual linear relationships with the target.**
#    `lights` has the strongest positive relationship among the non-lag features, while several humidity variables show negative relationships.
#
# 7. **`rv1` and `rv2` appear redundant in the prepared training data.**
#    They are identical across all observed training rows and have almost zero linear correlation with the target.
#
# 8. **The target behavior is broadly consistent across chronological splits.**
#    Train, validation, and test distributions are similar overall, although train contains larger peaks.
#
# 9. **Lag relationships remain reasonably stable across splits.**
#    This provides descriptive evidence that historical appliance consumption is a potentially useful source of predictive information.
#
# ---
#
# # 11. Implications for Later Modeling
#
# The EDA suggests several **candidate modeling investigations**, without declaring any feature set as the final or best choice:
#
# * Compare models using recent lag features against models without them.
# * Investigate whether adding temporal features such as `hour` and `weekday` improves prediction.
# * Evaluate whether environmental/sensor variables provide additional information beyond historical consumption.
# * Test the effect of removing redundant `rv1`/`rv2` variables as a controlled ablation.
# * Consider whether nonlinear models can capture relationships that are not apparent from simple correlations.
# * Evaluate all modeling decisions using the chronological validation split rather than the test set.
#
# These are hypotheses for subsequent modeling experiments, not conclusions about model performance.
#
# ---
#
# ## 12. Important EDA Boundary
#
# This EDA intentionally **does not modify the prepared dataset**.
#
# The analysis was performed on the existing prepared train/validation/test data. Feature-removal experiments, alternative feature sets, rolling-window configurations, and model comparisons should be handled later as controlled modeling experiments rather than being mixed into the exploratory analysis.
