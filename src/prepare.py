"""Prepare the Appliances Energy Prediction dataset.

Prediction scenario: at time T, predict the appliance energy use at T + horizon
using only information available at or before T.

Rules enforced here:
* every feature in row T is computed from rows <= T (no forward-looking windows)
* the only column that looks into the future is the target
* the split is chronological (train < val < test), never shuffled

Usage:
    python src/prepare.py --params configs/params.yaml
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import yaml

TARGET_COL = "target"


def load_params(path: str | Path, section: str = "prepare") -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)[section]


def load_raw(path: str | Path) -> pd.DataFrame:
    """Read the CSV, parse dates and sort chronologically."""
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"])
    return df.sort_values("date").reset_index(drop=True)


import numpy as np


def add_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    out["hour"] = out["date"].dt.hour
    out["minute"] = out["date"].dt.minute
    out["weekday"] = out["date"].dt.weekday
    out["month"] = out["date"].dt.month

    # 10-minute slot within the day: 0..143
    out["minute_of_day"] = out["hour"] * 60 + out["minute"]

    # Cyclic encoding for daily pattern
    out["sin_day"] = np.sin(2 * np.pi * out["minute_of_day"] / 1440)
    out["cos_day"] = np.cos(2 * np.pi * out["minute_of_day"] / 1440)

    # Weekly cycle
    out["sin_week"] = np.sin(2 * np.pi * out["weekday"] / 7)
    out["cos_week"] = np.cos(2 * np.pi * out["weekday"] / 7)

    return out


def add_lag_features(df: pd.DataFrame, column: str, lags: list[int]) -> pd.DataFrame:
    """lag_k at row T is the value of `column` at T - k (k >= 1)."""
    out = df.copy()
    for k in lags:
        if k < 1:
            raise ValueError(f"Lag must be >= 1, got {k}")
        out[f"{column}_lag_{k}"] = out[column].shift(k)
    return out


def add_rolling_features(
    df: pd.DataFrame, column: str, windows: list[int]
) -> pd.DataFrame:
    """Trailing mean and std over rows T-w+1 .. T."""
    out = df.copy()
    for w in windows:
        if w < 2:
            raise ValueError(f"Rolling window must be >= 2, got {w}")
        rolling = out[column].rolling(window=w)
        out[f"{column}_roll_mean_{w}"] = rolling.mean()
        out[f"{column}_roll_std_{w}"] = rolling.std()
    return out


def add_target(df: pd.DataFrame, column: str, horizon: int) -> pd.DataFrame:
    """Target at row T is `column` at T + horizon (the only forward-looking column)."""
    if horizon < 1:
        raise ValueError(f"Horizon must be >= 1, got {horizon}")
    out = df.copy()
    out[TARGET_COL] = out[column].shift(-horizon)
    return out


def add_change_features(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Short-term differences to capture trend."""
    out = df.copy()
    out[f"{column}_diff_1"] = out[column] - out[column].shift(1)
    out[f"{column}_diff_3"] = out[column] - out[column].shift(3)
    out[f"{column}_diff_6"] = out[column] - out[column].shift(6)
    return out


def add_interaction_features(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """Create interaction terms between key environmental variables."""
    out = df.copy()
    # T_out and RH_out interaction (proxy for dew point/comfort)
    if "T_out" in out.columns and "RH_out" in out.columns:
        out["temp_rh_interaction"] = out["T_out"] * out["RH_out"]

    # Target interaction with current temperature
    target = "Appliances"  # This is the default target
    if target in out.columns and "T_out" in out.columns:
        out["app_temp_interaction"] = out[target] * out["T_out"]

    return out


def chronological_split(
    df: pd.DataFrame, train_frac: float, val_frac: float
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Earliest rows -> train, next -> val, latest -> test. No shuffling."""
    if train_frac <= 0 or val_frac <= 0 or train_frac + val_frac >= 1:
        raise ValueError(
            "Need train_frac > 0, val_frac > 0 and train_frac + val_frac < 1"
        )
    n = len(df)
    n_train = int(n * train_frac)
    n_val = int(n * val_frac)
    train = df.iloc[:n_train]
    val = df.iloc[n_train : n_train + n_val]
    test = df.iloc[n_train + n_val :]
    return train, val, test


def build_dataset(df: pd.DataFrame, params: dict) -> pd.DataFrame:
    """Apply column drops, features and target; drop rows made incomplete by shifting."""
    target = params.get("target", "Appliances")
    out = df.drop(columns=params.get("drop_columns", []))
    if params.get("temporal_features", True):
        out = add_temporal_features(out)

    # 1. Lags for target
    out = add_lag_features(out, target, params.get("lags", []))

    # 2. Rolling stats for target
    out = add_rolling_features(out, target, params.get("rolling_windows", []))

    # 3. Trend/Change features for target
    out = add_change_features(out, target)

    # 4. Lags for environmental variables (if specified in params)
    env_lags = params.get("env_lags", {})
    for col, lags in env_lags.items():
        if col in out.columns:
            out = add_lag_features(out, col, lags)

    # 5. Environmental Change features (Deltas)
    # We apply change features to the most important env variables
    for col in ["T_out", "RH_out"]:
        if col in out.columns:
            out = add_change_features(out, col)

    # 6. Interaction features
    out = add_interaction_features(out, ["T_out", "RH_out"])

    out = add_target(out, target, params.get("horizon", 1))
    return out.dropna().reset_index(drop=True)


def prepare(params: dict) -> dict[str, Path]:
    df = load_raw(params["raw_path"])
    data = build_dataset(df, params)
    train, val, test = chronological_split(
        data, params["train_frac"], params["val_frac"]
    )

    out_dir = Path(params["output_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = {}
    for name, part in (("train", train), ("val", val), ("test", test)):
        paths[name] = out_dir / f"{name}.csv"
        part.to_csv(paths[name], index=False)
        print(f"{name}: {len(part)} rows  {part['date'].min()} -> {part['date'].max()}")
    return paths


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Prepare train/val/test splits.")
    parser.add_argument("--params", default="configs/params.yaml")
    args = parser.parse_args(argv)
    prepare(load_params(args.params))


if __name__ == "__main__":
    main()
