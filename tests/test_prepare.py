import numpy as np
import pandas as pd
import pytest

from src.prepare import (
    TARGET_COL,
    add_lag_features,
    add_rolling_features,
    add_target,
    build_dataset,
    chronological_split,
    load_raw,
)

PARAMS = {
    "target": "Appliances",
    "drop_columns": [],
    "temporal_features": True,
    "lags": [1, 6],
    "rolling_windows": [3],
    "horizon": 1,
}


@pytest.fixture
def df() -> pd.DataFrame:
    n = 100
    rng = np.random.default_rng(0)
    return pd.DataFrame(
        {
            "date": pd.date_range("2016-01-11 17:00", periods=n, freq="10min"),
            "Appliances": rng.integers(10, 500, n).astype(float),
            "T1": rng.normal(20, 2, n),
        }
    )


def test_load_raw_sorts_and_parses(tmp_path, df):
    path = tmp_path / "raw.csv"
    df.iloc[::-1].to_csv(path, index=False)
    loaded = load_raw(path)
    assert pd.api.types.is_datetime64_any_dtype(loaded["date"])
    assert loaded["date"].is_monotonic_increasing


def test_lag_values(df):
    out = add_lag_features(df, "Appliances", [6])
    assert out.loc[10, "Appliances_lag_6"] == df.loc[4, "Appliances"]


def test_lag_must_be_positive(df):
    with pytest.raises(ValueError):
        add_lag_features(df, "Appliances", [0])


def test_rolling_window_ends_at_current_row(df):
    out = add_rolling_features(df, "Appliances", [3])
    expected = df.loc[8:10, "Appliances"].mean()
    assert out.loc[10, "Appliances_roll_mean_3"] == pytest.approx(expected)


def test_target_is_future_value(df):
    out = add_target(df, "Appliances", 1)
    assert out.loc[5, TARGET_COL] == df.loc[6, "Appliances"]


def test_split_is_chronological_and_disjoint(df):
    train, val, test = chronological_split(df, 0.7, 0.15)
    assert len(train) + len(val) + len(test) == len(df)
    assert train["date"].max() < val["date"].min()
    assert val["date"].max() < test["date"].min()


def test_split_rejects_bad_fractions(df):
    with pytest.raises(ValueError):
        chronological_split(df, 0.9, 0.2)


def test_no_future_leakage_in_features(df):
    """Changing rows after T must not change any feature (non-target) at rows <= T."""
    cut = 60
    base = build_dataset(df, PARAMS)

    changed = df.copy()
    changed.loc[cut + 1 :, ["Appliances", "T1"]] = 9999.0
    altered = build_dataset(changed, PARAMS)

    feature_cols = [c for c in base.columns if c != TARGET_COL]
    # rows whose timestamp is <= cut, but exclude the row whose target is row cut+1
    ts_cut = df.loc[cut, "date"]
    a = base[base["date"] < ts_cut][feature_cols].reset_index(drop=True)
    b = altered[altered["date"] < ts_cut][feature_cols].reset_index(drop=True)
    pd.testing.assert_frame_equal(a, b)


def test_build_dataset_has_no_nans(df):
    out = build_dataset(df, PARAMS)
    assert not out.isna().any().any()
    assert TARGET_COL in out.columns
