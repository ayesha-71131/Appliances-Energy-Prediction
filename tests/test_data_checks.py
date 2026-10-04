import numpy as np
import pandas as pd
import pytest

from src.data_checks import EXPECTED_COLUMNS, validate


@pytest.fixture
def good_df() -> pd.DataFrame:
    n = 50
    data = {c: np.full(n, 20.0) for c in EXPECTED_COLUMNS if c != "date"}
    for c in list(data):
        if c.startswith("RH_"):
            data[c] = np.full(n, 40.0)
    data["Press_mm_hg"] = np.full(n, 750.0)
    df = pd.DataFrame(data)
    df.insert(0, "date", pd.date_range("2016-01-11 17:00", periods=n, freq="10min"))
    return df[EXPECTED_COLUMNS]


def test_valid_data_passes(good_df):
    assert validate(good_df).ok


def test_missing_column_fails(good_df):
    assert not validate(good_df.drop(columns=["T1"])).ok


def test_null_fails(good_df):
    good_df.loc[3, "T1"] = np.nan
    assert not validate(good_df).ok


def test_duplicate_timestamp_fails(good_df):
    good_df.loc[5, "date"] = good_df.loc[4, "date"]
    assert not validate(good_df).ok


def test_unsorted_timestamps_fail(good_df):
    assert not validate(good_df.iloc[::-1].reset_index(drop=True)).ok


def test_negative_energy_fails(good_df):
    good_df.loc[0, "Appliances"] = -5
    assert not validate(good_df).ok


def test_humidity_out_of_range_fails(good_df):
    good_df.loc[0, "RH_1"] = 120
    assert not validate(good_df).ok


def test_gap_is_warning_not_error(good_df):
    df = good_df.drop(index=10).reset_index(drop=True)
    report = validate(df)
    assert report.ok
    assert report.warnings
