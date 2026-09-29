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


def add_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["hour"] = out["date"].dt.hour
    out["weekday"] = out["date"].dt.weekday
    out["month"] = out["date"].dt.month
    return out


def add_lag_features(df: pd.DataFrame, column: str, lags: list[int]) -> pd.DataFrame:
    """lag_k at row T is the value of `column` at T - k (k >= 1)."""
    out = df.copy()
    for k in lags:
        if k < 1:
            raise ValueError(f"Lag must be >= 1, got {k}")
        out[f"{column}_lag_{k}"] = out[column].shift(k)
    return out


def add_rolling_features(df: pd.DataFrame, column: str, windows: list[int]) -> pd.DataFrame:
    """Trailing mean over rows T-w+1 .. T (window ends at T, never looks ahead)."""
    out = df.copy()
    for w in windows:
        if w < 2:
            raise ValueError(f"Rolling window must be >= 2, got {w}")
        out[f"{column}_roll_mean_{w}"] = out[column].rolling(window=w).mean()
    return out


def add_target(df: pd.DataFrame, column: str, horizon: int) -> pd.DataFrame:
    """Target at row T is `column` at T + horizon (the only forward-looking column)."""
    if horizon < 1:
        raise ValueError(f"Horizon must be >= 1, got {horizon}")
    out = df.copy()
    out[TARGET_COL] = out[column].shift(-horizon)
    return out


def chronological_split(
    df: pd.DataFrame, train_frac: float, val_frac: float
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Earliest rows -> train, next -> val, latest -> test. No shuffling."""
    if train_frac <= 0 or val_frac <= 0 or train_frac + val_frac >= 1:
        raise ValueError("Need train_frac > 0, val_frac > 0 and train_frac + val_frac < 1")
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
    out = add_lag_features(out, target, params.get("lags", []))
    out = add_rolling_features(out, target, params.get("rolling_windows", []))
    out = add_target(out, target, params.get("horizon", 1))
    return out.dropna().reset_index(drop=True)


def prepare(params: dict) -> dict[str, Path]:
    df = load_raw(params["raw_path"])
    data = build_dataset(df, params)
    train, val, test = chronological_split(data, params["train_frac"], params["val_frac"])

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
