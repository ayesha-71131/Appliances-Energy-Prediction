"""Reusable helpers for exploratory data analysis."""

from __future__ import annotations

import pandas as pd


def summarize_numeric(df: pd.DataFrame, column: str) -> dict[str, float]:
    """Return a compact statistical summary for a numeric column."""
    series = df[column]

    return {
        "count": float(series.count()),
        "mean": float(series.mean()),
        "median": float(series.median()),
        "std": float(series.std()),
        "min": float(series.min()),
        "max": float(series.max()),
        "skewness": float(series.skew()),
    }
