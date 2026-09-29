"""Validation checks for the raw Appliances Energy Prediction dataset.

Usage:
    python src/data_checks.py data/raw/energydata_complete.csv

Exits with status 1 if any hard check fails (used by CI and DVC).
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

EXPECTED_COLUMNS = [
    "date", "Appliances", "lights",
    "T1", "RH_1", "T2", "RH_2", "T3", "RH_3", "T4", "RH_4", "T5", "RH_5",
    "T6", "RH_6", "T7", "RH_7", "T8", "RH_8", "T9", "RH_9",
    "T_out", "Press_mm_hg", "RH_out", "Windspeed", "Visibility", "Tdewpoint",
    "rv1", "rv2",
]  # fmt: skip

SAMPLING_INTERVAL = pd.Timedelta(minutes=10)

# (min, max) inclusive; None means unbounded on that side.
RANGES: dict[str, tuple[float | None, float | None]] = {
    "Appliances": (0, None),
    "lights": (0, None),
    "Windspeed": (0, None),
    "Visibility": (0, None),
    "Press_mm_hg": (600, 800),
    "RH_out": (0, 100),
    **{f"RH_{i}": (0, 100) for i in range(1, 10)},
    **{f"T{i}": (-20, 45) for i in range(1, 10)},
    "T_out": (-30, 45),
    "Tdewpoint": (-30, 45),
}


@dataclass
class Report:
    """Collected results: errors fail the run, warnings are informational."""

    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def check_columns(df: pd.DataFrame, report: Report) -> None:
    missing = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    extra = [c for c in df.columns if c not in EXPECTED_COLUMNS]
    if missing:
        report.errors.append(f"Missing columns: {missing}")
    if extra:
        report.warnings.append(f"Unexpected extra columns: {extra}")


def check_nulls(df: pd.DataFrame, report: Report) -> None:
    nulls = df.isna().sum()
    bad = nulls[nulls > 0]
    if not bad.empty:
        report.errors.append(f"Null values found: {bad.to_dict()}")


def check_dtypes(df: pd.DataFrame, report: Report) -> None:
    for col in EXPECTED_COLUMNS:
        if col in df.columns and col != "date":
            if not pd.api.types.is_numeric_dtype(df[col]):
                report.errors.append(f"Column '{col}' is not numeric ({df[col].dtype})")


def check_timestamps(df: pd.DataFrame, report: Report) -> None:
    if "date" not in df.columns:
        return
    parsed = pd.to_datetime(df["date"], errors="coerce")
    n_bad = int(parsed.isna().sum())
    if n_bad:
        report.errors.append(f"{n_bad} unparseable timestamps in 'date'")
        return
    if parsed.duplicated().any():
        report.errors.append(f"{int(parsed.duplicated().sum())} duplicate timestamps")
    if not parsed.is_monotonic_increasing:
        report.errors.append("Timestamps are not sorted in increasing order")
    gaps = parsed.sort_values().diff().dropna()
    irregular = gaps[gaps != SAMPLING_INTERVAL]
    if not irregular.empty:
        report.warnings.append(
            f"{len(irregular)} steps differ from the 10-minute interval "
            f"(largest gap: {irregular.max()})"
        )


def check_ranges(df: pd.DataFrame, report: Report) -> None:
    for col, (lo, hi) in RANGES.items():
        if col not in df.columns:
            continue
        series = df[col]
        if lo is not None and (series < lo).any():
            report.errors.append(f"'{col}' has values below {lo} (min={series.min()})")
        if hi is not None and (series > hi).any():
            report.errors.append(f"'{col}' has values above {hi} (max={series.max()})")


def validate(df: pd.DataFrame) -> Report:
    """Run all checks and return a Report."""
    report = Report()
    check_columns(df, report)
    check_nulls(df, report)
    check_dtypes(df, report)
    check_timestamps(df, report)
    check_ranges(df, report)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate the raw dataset.")
    parser.add_argument("path", type=Path, help="Path to energydata_complete.csv")
    args = parser.parse_args(argv)

    df = pd.read_csv(args.path)
    print(f"Loaded {args.path} with shape {df.shape}")
    report = validate(df)

    for w in report.warnings:
        print(f"WARNING: {w}")
    for e in report.errors:
        print(f"ERROR: {e}")
    print("Data checks PASSED" if report.ok else "Data checks FAILED")
    return 0 if report.ok else 1


if __name__ == "__main__":
    sys.exit(main())
