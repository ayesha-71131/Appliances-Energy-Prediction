import pytest
import pandas as pd
import numpy as np
from src.prepare import add_temporal_features, add_lag_features, add_rolling_features

def test_add_temporal_features():
    # Create a dummy dataframe with a date column
    df = pd.DataFrame({
        "date": pd.to_datetime(["2023-01-01 10:00:00", "2023-01-01 10:10:00"]),
        "Appliances": [100.0, 110.0]
    })
    result = add_temporal_features(df)

    # Check if new columns exist
    assert "hour" in result.columns
    assert "minute" in result.columns
    assert "sin_day" in result.columns
    assert "cos_day" in result.columns

    # Verify values: 10:00 should be hour 10, minute 0
    assert result.iloc[0]["hour"] == 10
    assert result.iloc[0]["minute"] == 0

def test_add_lag_features():
    df = pd.DataFrame({
        "Appliances": [10.0, 20.0, 30.0, 40.0]
    })
    # Lag of 1
    result = add_lag_features(df, "Appliances", [1])

    assert "Appliances_lag_1" in result.columns
    # The first value should be NaN, second should be the first value
    assert np.isnan(result.iloc[0]["Appliances_lag_1"])
    assert result.iloc[1]["Appliances_lag_1"] == 10.0

def test_add_rolling_features():
    df = pd.DataFrame({
        "Appliances": [10.0, 20.0, 30.0, 40.0]
    })
    # Window of 2
    result = add_rolling_features(df, "Appliances", [2])

    assert "Appliances_roll_mean_2" in result.columns
    assert "Appliances_roll_std_2" in result.columns
    # Second row mean: (10+20)/2 = 15
    assert result.iloc[1]["Appliances_roll_mean_2"] == 15.0
